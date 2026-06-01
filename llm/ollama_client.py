"""Local Ollama provider adapter (DESIGN.md §5, §7; Phase 7 Ollama plan).

:class:`OllamaClient` implements the :class:`~llm.client.LLMClient` Protocol
against a **local** Ollama server, the canonical Phase 7 agent-intelligence
provider: a self-hosted open model (``qwen2.5:7b-instruct``) that is free
(``cost_usd == 0.0``) and never leaves the owner's machine. It mirrors the
shape of :class:`llm.provider.AnthropicClient` and
:class:`llm.fake_provider.FakeProvider`; provider-specific knobs (host,
per-game ``seed``) live on the constructor and never leak through the
Protocol.

The adapter deliberately REUSES the shared helpers in
:mod:`llm.provider` rather than re-implementing them:

* :func:`llm.provider._extract_json_block` pulls the JSON object out of the
  raw model text — so 7.6's parse-tolerance normalization, which lands in
  that shared extract→validate path, automatically covers Ollama too.
* :func:`llm.provider._compute_cost_usd` (with ``provider=PROVIDER_OLLAMA``)
  resolves the cost — keyed by provider, it returns ``0.0`` for every
  Ollama model.
* :class:`llm.provider.LLMCallFailure` +
  :func:`llm.provider._attach_parse_failure` turn a malformed local output
  into a recoverable FailedCall (the orchestrator records a failed-call
  audit row) rather than a hard crash.

CI never imports the ``ollama`` SDK: the adapter does the import lazily
inside :func:`_default_send`. Unit tests pass an injected ``send`` hook so
the SDK stays optional and no network call is made.

Determinism: the per-game ``seed`` only affects *fresh* generation. The
recording/replay layer captures the client's outputs, so a recorded Ollama
game replays byte-identically without the server; fresh generation may
still drift across Ollama/runtime versions.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, Final

from pydantic import BaseModel, ConfigDict, ValidationError

from llm.client import CallKind, LLMResponse, TokenUsage
from llm.provider import (
    _ERROR_MESSAGE_CHARS,
    _RAW_RESPONSE_CHARS,
    PROVIDER_OLLAMA,
    LLMCallFailure,
    _attach_parse_failure,
    _compute_cost_usd,
    _extract_json_block,
)

if TYPE_CHECKING:
    # Type-only import: the ``ollama`` SDK is imported lazily at call time
    # inside :func:`_default_send` (see the module docstring), never at
    # module-import time, so CI / fake-provider runs never load it.
    from ollama import GenerateResponse


DEFAULT_OLLAMA_HOST: Final[str] = "localhost:11434"
DEFAULT_OLLAMA_MODEL: Final[str] = "qwen2.5:7b-instruct"
# Base seed used when no per-game seed is supplied (e.g. an operator run
# that does not thread the orchestrator's seed). It is a base, not a
# baked-in constant for ``options.seed``: the per-game seed passed to the
# constructor is what folds into generation, so distinct games stay
# distinct. See :func:`llm.provider.build_default_client`.
DEFAULT_OLLAMA_SEED: Final[int] = 0
# Default context window (``num_ctx``). Ollama's own default is small and bounds
# prompt + output TOGETHER, so the largest 7p/2i meeting prompts (~4040 tokens,
# measured) plus their ~150-token report/vote output overflow it and trigger
# output truncation / context-shift that silently drops the prompt head. 8192
# clears the measured max with headroom; prefill cost scales with the actual
# prompt length (~2.4k median), NOT this cap, so normal calls are unaffected.
# Overridable via ``AILIBI_OLLAMA_NUM_CTX`` (see build_default_client).
DEFAULT_OLLAMA_NUM_CTX: Final[int] = 8192


class OllamaRawResponse(BaseModel):
    """Provider-agnostic shape the injectable ``send`` hook returns.

    Real ``ollama`` SDK ``GenerateResponse`` objects are unpacked into this
    model inside :func:`_default_send`; the rest of the adapter operates on
    this shape so unit tests can inject deterministic fixtures without the
    SDK. ``prompt_eval_count`` / ``eval_count`` are Ollama's input / output
    token counters (coerced from the SDK's ``Optional[int]`` to ``0`` when
    absent).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    model: str
    prompt_eval_count: int
    eval_count: int


OllamaSendHook = Callable[..., Awaitable[OllamaRawResponse]]


class OllamaClient:
    """Local-Ollama adapter behind the :class:`~llm.client.LLMClient` Protocol.

    Public surface is just :meth:`complete`. Ollama-only configuration
    lives on the constructor:

    * ``host`` — the Ollama server address (e.g. ``localhost:11434``).
    * ``seed`` — the per-game seed folded into ``options.seed`` for
      reproducible-ish fresh generation. Fixed for the lifetime of the
      client (one client per game), so a game is reproducible-ish and
      distinct games don't collide; it is NOT a single baked-in constant
      and NOT re-hashed per call.
    * ``meeting_model`` / ``trigger_model`` — model ids per ``call_kind``,
      both defaulting to :data:`DEFAULT_OLLAMA_MODEL`.
    * ``send`` — injectable transport hook used by unit tests in place of
      the real SDK. Defaults to ``None`` (real SDK via :func:`_default_send`).
    """

    # Pre-flight cost-estimation rate hints (USD per single token) consumed
    # by :class:`llm.budgeted_client.BudgetedLLMClient`: a local model is
    # free, so both are 0.0 and the USD pre-flight dimension cannot block a
    # free run. The token caps are untouched — a local model can ramble, so
    # the token ceiling is the real backstop. Clients that do not expose
    # these (Anthropic, the fake) keep the budget layer's frontier defaults.
    preflight_cost_per_input_token_usd: float = 0.0
    preflight_cost_per_output_token_usd: float = 0.0

    def __init__(
        self,
        *,
        host: str,
        seed: int,
        num_ctx: int = DEFAULT_OLLAMA_NUM_CTX,
        meeting_model: str = DEFAULT_OLLAMA_MODEL,
        trigger_model: str = DEFAULT_OLLAMA_MODEL,
        send: OllamaSendHook | None = None,
    ) -> None:
        if not host:
            raise ValueError("OllamaClient requires a non-empty host")
        if num_ctx <= 0:
            raise ValueError(f"OllamaClient requires num_ctx > 0, got {num_ctx}")
        self._host = host
        self._seed = seed
        self._num_ctx = num_ctx
        self._meeting_model = meeting_model
        self._trigger_model = trigger_model
        self._send: OllamaSendHook = send if send is not None else _default_send

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        # ``agent_id`` is call-attribution metadata for the replay layer
        # (DESIGN.md §11.4), not a provider knob — deliberately not
        # forwarded to the upstream Ollama server.
        del agent_id
        chosen_model = model if model is not None else self._model_for(call_kind)
        # Constrained (schema-shaped) decoding: Ollama accepts the JSON
        # Schema directly as ``format`` and biases sampling toward output
        # that validates against it. ``None`` when the caller wants free text.
        format_schema = schema.model_json_schema() if schema is not None else None
        # ``seed`` is the per-game seed (fixed for this client instance);
        # ``num_predict`` maps the Protocol's ``max_tokens`` onto Ollama's
        # output cap so the knob is honored rather than silently dropped.
        options: dict[str, Any] = {
            "temperature": temperature,
            "seed": self._seed,
            "num_predict": max_tokens,
            # Context window: Ollama's default bounds prompt + output together and
            # is small enough that the largest meeting prompts plus their output
            # overflow it (silent output truncation / context-shift dropping the
            # prompt head). Set it explicitly so the recorded generation sees the
            # full prompt and isn't cut off mid-JSON.
            "num_ctx": self._num_ctx,
        }
        raw = await self._send(
            host=self._host,
            model=chosen_model,
            prompt=prompt,
            format_schema=format_schema,
            options=options,
        )
        # Cost is $0 for every Ollama response (rate keyed by provider, not
        # model). Computed up front so the same figure is available both for
        # the successful LLMResponse and for the failure carrier attached to
        # a ValidationError below.
        cost_usd = _compute_cost_usd(
            model=raw.model,
            input_tokens=raw.prompt_eval_count,
            output_tokens=raw.eval_count,
            provider=PROVIDER_OLLAMA,
        )
        # Pull the JSON object out of the raw text through the SAME shared
        # extractor the Anthropic client uses, so 7.6's normalization (which
        # lands in that shared path) automatically covers Ollama too.
        text = _extract_json_block(raw.text, schema) if schema is not None else raw.text
        if schema is not None:
            try:
                schema.model_validate_json(text)
            except ValidationError as exc:
                # A weak local model can emit schema-invalid JSON. Attach the
                # cost + partial response to the propagating ValidationError
                # (the same carrier the Anthropic path uses) so the
                # orchestrator's recording layer persists a recoverable
                # failed-call audit row instead of crashing the meeting.
                _attach_parse_failure(
                    exc,
                    LLMCallFailure(
                        model=raw.model,
                        prompt_length=len(prompt),
                        raw_response=raw.text[:_RAW_RESPONSE_CHARS],
                        input_tokens=raw.prompt_eval_count,
                        output_tokens=raw.eval_count,
                        cost_usd=cost_usd,
                        error_type=type(exc).__name__,
                        error_message=str(exc)[:_ERROR_MESSAGE_CHARS],
                    ),
                )
                raise
        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=raw.prompt_eval_count,
                output_tokens=raw.eval_count,
            ),
            cost_usd=cost_usd,
            model=raw.model,
        )

    def _model_for(self, call_kind: CallKind) -> str:
        if call_kind == "meeting":
            return self._meeting_model
        if call_kind == "trigger":
            return self._trigger_model
        # Unreachable under `mypy --strict` because `CallKind` is a
        # `Literal`, but AGENTS.md mandates no silent fallbacks even for
        # type-system-guarded branches.
        raise ValueError(f"unknown call_kind: {call_kind!r}")


async def _default_send(
    *,
    host: str,
    model: str,
    prompt: str,
    format_schema: dict[str, Any] | None,
    options: dict[str, Any],
) -> OllamaRawResponse:
    # Lazy import per the module docstring: the real SDK is only imported
    # when an OllamaClient is actually invoked, so FakeProvider-only test
    # runs and `bash scripts/check.sh` never need it loaded at import time.
    import ollama

    # Use the client as an async context manager so its underlying httpx
    # connection pool is closed deterministically after each call.
    # `_default_send` is a stateless module-level send-hook, so there is no
    # OllamaClient instance on which to hang a long-lived pooled client
    # without introducing module-level state (which the design forbids).
    async with ollama.AsyncClient(host=host) as client:
        response = await client.generate(
            model=model,
            prompt=prompt,
            format=format_schema,
            options=options,
            stream=False,
        )

    # ``stream=False`` returns a single GenerateResponse, but the SDK's
    # return type is a union with the streaming iterator; narrow it (and
    # fail loud if a streaming object ever slips through).
    if not isinstance(response, ollama.GenerateResponse):
        raise RuntimeError(
            f"Ollama returned a streaming response for a non-streaming "
            f"generate call (model={model!r})"
        )

    return _raw_from_generate_response(response, model=model)


def _raw_from_generate_response(
    response: GenerateResponse,
    *,
    model: str,
) -> OllamaRawResponse:
    """Map an Ollama ``GenerateResponse`` onto :class:`OllamaRawResponse`.

    Fails loud when the OUTPUT counter (``eval_count``) is missing: a
    completed non-streaming generation always reports it, so a ``None`` is
    an anomalous response, and silently recording it as 0 output tokens
    would under-count the per-game token budget — the real backstop for
    Ollama, whose USD dimension is deliberately zeroed (AGENTS.md: no
    silent fallbacks). ``prompt_eval_count`` is treated as 0 when absent:
    Ollama omits it when the prompt is served entirely from the context
    cache (no prompt evaluation ran), so 0 evaluated input tokens is the
    correct charge for that call, not a papered-over error.

    Split out of :func:`_default_send` so the mapping (which the live
    transport otherwise hides) is unit-testable without a server.
    """

    if response.eval_count is None:
        raise RuntimeError(
            "Ollama response omitted eval_count (the output token counter) "
            f"for a completed generation (model={model!r}); refusing to "
            "record it as 0 tokens, which would under-count the per-game "
            "token budget."
        )
    return OllamaRawResponse(
        model=response.model or model,
        text=response.response or "",
        # None/absent prompt_eval_count == fully-cached prompt: 0 input
        # tokens were evaluated, which is the correct charge (see docstring).
        prompt_eval_count=response.prompt_eval_count or 0,
        eval_count=response.eval_count,
    )


__all__ = [
    "DEFAULT_OLLAMA_HOST",
    "DEFAULT_OLLAMA_MODEL",
    "DEFAULT_OLLAMA_NUM_CTX",
    "DEFAULT_OLLAMA_SEED",
    "OllamaClient",
    "OllamaRawResponse",
    "OllamaSendHook",
]
