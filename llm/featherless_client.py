"""Featherless AI provider adapter (DESIGN.md §7, §10.4; Phase 14 plan).

:class:`FeatherlessClient` implements the :class:`~llm.client.LLMClient`
Protocol against **Featherless AI**, a hosted, flat-rate, OpenAI-compatible
inference endpoint (owner decision 2026-06-25, Featherless AI Premium): the
new canonical agent-intelligence provider succeeding the local Ollama
``qwen3.5:9b``. Cost is recorded as ``$0`` keyed by provider (the Ollama
doctrine — a flat monthly subscription, not metered per token), so the token
caps (turn 2048 / vote 1024) stay the real backstop and an A/B model swap can
never silently fall back to a frontier rate. Provider-specific knobs (base
URL, the request-time thinking toggle, the response-side thinking policy) live
on the constructor and never leak through the Protocol.

This adapter is structurally cloned from :mod:`llm.ollama_client` — the closer
template, which already solved lazy-import, an injectable ``send`` hook,
$0-by-provider cost, fail-loud thinking, and the ``_raw_from_*`` test split.
The OpenAI-compatible analogue of Ollama's ``format=schema.model_json_schema()``
is a ``response_format`` of ``{"type": "json_schema", "json_schema": {"name":
schema.__name__, "schema": schema.model_json_schema(), "strict": True}}`` —
strict structured-output decoding. The response then routes through the SAME
shared seam the Anthropic and Ollama adapters use:

* :func:`llm.provider._extract_json_block` pulls the JSON object out of the
  raw model text — so 7.6's parse-tolerance normalization, which lands in that
  shared extract→validate path, automatically covers Featherless too.
* :func:`llm.provider._compute_cost_usd` (with ``provider=PROVIDER_FEATHERLESS``)
  resolves the cost — keyed by provider, it returns ``0.0`` for every model.
* :class:`llm.provider.LLMCallFailure` +
  :func:`llm.provider._attach_parse_failure` turn a malformed output into a
  recoverable FailedCall (the orchestrator records a failed-call audit row)
  rather than a hard crash.

Thinking models (the Phase-14 slate puts them on the table now that inference
is on the cloud) are handled by TWO distinct knobs:

* **Request-time thinking toggle** (``request_thinking``) — mirrors Ollama's
  top-level ``think=`` field: it tells the model whether to reason AT ALL.
  Sent on the wire as ``chat_template_kwargs={"enable_thinking": ...}`` (the
  Qwen3 convention for OpenAI-compatible servers). This is the sweep AXIS
  14.4 drives.
* **Response-side thinking policy** (``thinking_policy``) — what to do when a
  response nonetheless carries reasoning. ``fail_loud`` (default) RAISES on a
  populated reasoning channel (parity with the Ollama doctrine); ``strip``
  discards it EXPLICITLY (logged via the module logger, never silent) so the
  14.4 sweep can evaluate reasoning models.

The ``fail_loud`` guard runs a RAW-CONTENT reasoning check BEFORE
:func:`~llm.provider._extract_json_block`: that shared extractor deliberately
strips a prose preamble and returns the first valid JSON object, so a
``reasoning\n{JSON}`` response would otherwise be silently accepted —
``fail_loud`` would degrade to ``strip``, a no-silent-fallbacks violation. The
guard therefore inspects both the dedicated ``reasoning_content`` channel and
the raw ``content`` (reasoning markers / leading prose) up front.

CI never imports ``httpx``: the adapter does the import lazily inside
:func:`_default_send`. Unit tests pass an injected ``send`` hook so the
transport stays optional and no network call is made.

Determinism: hosted models do not byte-reproduce FRESH generation, but the
recording/replay layer captures the client's outputs, so a recorded
Featherless game replays byte-identically without the endpoint (the loosened
contract Ollama already carries).
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from llm.client import CallKind, LLMResponse, TokenUsage
from llm.provider import (
    _ERROR_MESSAGE_CHARS,
    _RAW_RESPONSE_CHARS,
    PROVIDER_FEATHERLESS,
    LLMCallFailure,
    _attach_parse_failure,
    _compute_cost_usd,
    _extract_json_block,
)


_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

# Featherless exposes an OpenAI-compatible API; ``/chat/completions`` is
# appended to this base. Overridable via ``AILIBI_FEATHERLESS_BASE_URL`` (see
# :func:`llm.provider.build_default_client`) for a proxy or a self-hosted
# OpenAI-compatible endpoint.
DEFAULT_FEATHERLESS_BASE_URL: Final[str] = "https://api.featherless.ai/v1"
# Default model id (HuggingFace repo form, as Featherless expects). Qwen3-32B
# leads the Phase-14 slate; this is a non-binding default — the canonical
# (meeting_model, trigger_model) tuple is locked at Task 14.6 and supplied via
# ``AILIBI_LLM_MEETING_MODEL`` / ``AILIBI_LLM_TRIGGER_MODEL`` until then.
DEFAULT_FEATHERLESS_MODEL: Final[str] = "Qwen/Qwen3-32B"

ThinkingPolicy = Literal["fail_loud", "strip"]
# Response-side policy applied when a response carries reasoning. ``fail_loud``
# mirrors the Ollama doctrine (a half-thinking run is refused, not recorded);
# ``strip`` is the 14.4-sweep harness choice (reasoning discarded explicitly).
DEFAULT_THINKING_POLICY: Final[ThinkingPolicy] = "fail_loud"


class FeatherlessRawResponse(BaseModel):
    """Provider-agnostic shape the injectable ``send`` hook returns.

    Real OpenAI-compatible JSON response bodies are unpacked into this model
    inside :func:`_default_send` (via :func:`_raw_from_response_body`); the
    rest of the adapter operates on this shape so unit tests can inject
    deterministic fixtures without the transport. ``prompt_tokens`` /
    ``completion_tokens`` are the OpenAI ``usage`` counters.
    ``reasoning_content`` is the separate reasoning side-channel some servers
    surface for thinking models (``choices[0].message.reasoning_content``); it
    must be empty under a non-thinking request and is one of the inputs the
    ``fail_loud`` guard inspects (coerced to ``""`` when absent).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    reasoning_content: str = ""


FeatherlessSendHook = Callable[..., Awaitable[FeatherlessRawResponse]]


class FeatherlessClient:
    """Featherless adapter behind the :class:`~llm.client.LLMClient` Protocol.

    Public surface is just :meth:`complete`. Featherless-only configuration
    lives on the constructor:

    * ``api_key`` — Featherless API key (``Authorization: Bearer``). Read from
      ``FEATHERLESS_API_KEY`` by :func:`build_default_client` when not passed.
    * ``base_url`` — the OpenAI-compatible base (``/chat/completions`` is
      appended). Defaults to :data:`DEFAULT_FEATHERLESS_BASE_URL`.
    * ``meeting_model`` / ``trigger_model`` — model ids per ``call_kind``,
      both defaulting to :data:`DEFAULT_FEATHERLESS_MODEL`.
    * ``request_thinking`` — the request-time thinking toggle (does the model
      reason at all). Mirrors Ollama's top-level ``think=``; sent as
      ``chat_template_kwargs={"enable_thinking": ...}``. Default ``False``.
    * ``thinking_policy`` — the response-side policy (``fail_loud`` default /
      ``strip``). Distinct from ``request_thinking``.
    * ``send`` — injectable transport hook used by unit tests in place of the
      real ``httpx`` POST. Defaults to ``None`` (real transport via
      :func:`_default_send`).
    """

    # Pre-flight cost-estimation rate hints (USD per single token) consumed by
    # :class:`llm.budgeted_client.BudgetedLLMClient`: Featherless is flat-rate,
    # so both are 0.0 and the USD pre-flight dimension cannot block a run. The
    # token caps are untouched — a hosted model can ramble, so the token
    # ceiling is the real backstop (the same doctrine as the Ollama client).
    preflight_cost_per_input_token_usd: float = 0.0
    preflight_cost_per_output_token_usd: float = 0.0

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_FEATHERLESS_BASE_URL,
        meeting_model: str = DEFAULT_FEATHERLESS_MODEL,
        trigger_model: str = DEFAULT_FEATHERLESS_MODEL,
        request_thinking: bool = False,
        thinking_policy: ThinkingPolicy = DEFAULT_THINKING_POLICY,
        send: FeatherlessSendHook | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("FeatherlessClient requires a non-empty api_key")
        if not base_url:
            raise ValueError("FeatherlessClient requires a non-empty base_url")
        if thinking_policy not in ("fail_loud", "strip"):
            raise ValueError(
                "FeatherlessClient thinking_policy must be 'fail_loud' or "
                f"'strip', got {thinking_policy!r}"
            )
        self._api_key = api_key
        # Normalize a trailing slash so ``{base_url}/chat/completions`` never
        # produces a double slash.
        self._base_url = base_url.rstrip("/")
        self._meeting_model = meeting_model
        self._trigger_model = trigger_model
        self._request_thinking = request_thinking
        self._thinking_policy: ThinkingPolicy = thinking_policy
        self._send: FeatherlessSendHook = send if send is not None else _default_send

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
        # (DESIGN.md §11.4), not a provider knob — deliberately not forwarded
        # to the upstream Featherless endpoint.
        del agent_id
        chosen_model = model if model is not None else self._model_for(call_kind)
        # Constrained (schema-shaped) decoding: the OpenAI-compatible analogue
        # of Ollama's ``format=schema.model_json_schema()`` is a strict
        # ``response_format`` json_schema. ``None`` when the caller wants free
        # text. The json_schema ``name`` is ``schema.__name__``.
        response_format = (
            {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                    "strict": True,
                },
            }
            if schema is not None
            else None
        )
        raw = await self._send(
            base_url=self._base_url,
            api_key=self._api_key,
            model=chosen_model,
            prompt=prompt,
            response_format=response_format,
            max_tokens=max_tokens,
            temperature=temperature,
            # ``request_thinking`` mirrors Ollama's top-level ``think=``: it
            # asks the model to reason (or not) at all — distinct from the
            # response-side ``thinking_policy`` below.
            request_thinking=self._request_thinking,
        )
        # Response-side thinking policy, applied to the RAW content BEFORE
        # ``_extract_json_block`` (which strips a prose preamble and returns the
        # first valid JSON object — so a post-extraction check could not catch
        # ``reasoning\n{JSON}`` and ``fail_loud`` would silently degrade to
        # ``strip``, a no-silent-fallbacks violation).
        reasoning = _detect_reasoning(raw.text, raw.reasoning_content, schema)
        if reasoning is not None:
            if self._thinking_policy == "fail_loud":
                raise RuntimeError(
                    "Featherless returned reasoning under thinking_policy="
                    f"'fail_loud' (model={raw.model!r}): {reasoning}. Refusing "
                    "to record a half-thinking run; set request_thinking=False "
                    "to suppress reasoning, or thinking_policy='strip' to "
                    "discard it explicitly for the model sweep."
                )
            # ``strip``: discard reasoning EXPLICITLY (logged, never silent).
            # For structured calls the discard is performed by
            # ``_extract_json_block`` below (it drops the prose/marker preamble
            # and returns the JSON); the dedicated ``reasoning_content`` channel
            # is never read into ``text``. This log makes that drop auditable.
            _LOGGER.warning(
                "FeatherlessClient discarding reasoning under "
                "thinking_policy='strip' (model=%r): %s",
                raw.model,
                reasoning,
            )
        # Cost is $0 for every Featherless response (rate keyed by provider,
        # not model). Computed up front so the same figure is available both
        # for the successful LLMResponse and for the failure carrier attached
        # to a ValidationError below.
        cost_usd = _compute_cost_usd(
            model=raw.model,
            input_tokens=raw.prompt_tokens,
            output_tokens=raw.completion_tokens,
            provider=PROVIDER_FEATHERLESS,
        )
        # Pull the JSON object out of the raw text through the SAME shared
        # extractor the Anthropic / Ollama clients use, so 7.6's normalization
        # (which lands in that shared path) automatically covers Featherless.
        text = _extract_json_block(raw.text, schema) if schema is not None else raw.text
        if schema is not None:
            try:
                schema.model_validate_json(text)
            except ValidationError as exc:
                # A model can emit schema-invalid JSON even under strict
                # ``response_format``. Attach the cost + partial response to the
                # propagating ValidationError (the same carrier the Anthropic /
                # Ollama paths use) so the orchestrator's recording layer
                # persists a recoverable failed-call audit row instead of
                # crashing the meeting.
                _attach_parse_failure(
                    exc,
                    LLMCallFailure(
                        model=raw.model,
                        prompt_length=len(prompt),
                        raw_response=raw.text[:_RAW_RESPONSE_CHARS],
                        input_tokens=raw.prompt_tokens,
                        output_tokens=raw.completion_tokens,
                        cost_usd=cost_usd,
                        error_type=type(exc).__name__,
                        error_message=str(exc)[:_ERROR_MESSAGE_CHARS],
                    ),
                )
                raise
        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=raw.prompt_tokens,
                output_tokens=raw.completion_tokens,
            ),
            cost_usd=cost_usd,
            model=raw.model,
        )

    def _model_for(self, call_kind: CallKind) -> str:
        if call_kind == "meeting":
            return self._meeting_model
        if call_kind == "trigger":
            return self._trigger_model
        # Unreachable under `mypy --strict` because `CallKind` is a `Literal`,
        # but AGENTS.md mandates no silent fallbacks even for type-system-
        # guarded branches.
        raise ValueError(f"unknown call_kind: {call_kind!r}")


def _detect_reasoning(
    text: str,
    reasoning_content: str,
    schema: type[BaseModel] | None,
) -> str | None:
    """Return a description of any reasoning present in a raw response.

    This is the RAW-CONTENT guard the ``fail_loud`` policy runs BEFORE
    :func:`llm.provider._extract_json_block` — the shared extractor strips a
    prose preamble and returns the first valid JSON object, so reasoning that
    precedes the JSON must be detected here or it is silently accepted. Returns
    ``None`` when the response carries no reasoning (the clean non-thinking
    happy path: empty ``reasoning_content``, no reasoning markers, JSON-first
    content), else a short human-readable description used in the fail-loud
    error / the strip-policy log.

    Detection, most-specific first:

    * a populated dedicated ``reasoning_content`` side-channel;
    * ``<think>`` reasoning markers anywhere in the content;
    * (structured calls only — ``schema`` supplied) a non-empty prose preamble
      before the first ``{``, i.e. content that is neither JSON-first nor
      fenced. Free-text calls (``schema is None``) legitimately return prose,
      so only the channel / marker signals apply to them.
    """

    if reasoning_content.strip():
        return f"populated reasoning_content channel ({len(reasoning_content)} chars)"
    lowered = text.lower()
    if "<think>" in lowered or "</think>" in lowered:
        return "reasoning markers (<think>...</think>) in content"
    if schema is not None:
        stripped = text.lstrip()
        if stripped and not stripped.startswith("{") and not stripped.startswith("```"):
            first_brace = stripped.find("{")
            preamble = (
                stripped if first_brace == -1 else stripped[:first_brace]
            ).strip()
            if preamble:
                return f"leading prose preamble before JSON ({len(preamble)} chars)"
    return None


async def _default_send(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    response_format: dict[str, Any] | None,
    max_tokens: int,
    temperature: float,
    request_thinking: bool,
) -> FeatherlessRawResponse:
    # Lazy import per the module docstring: ``httpx`` is only imported when a
    # FeatherlessClient is actually invoked, so FakeProvider-only test runs and
    # `bash scripts/check.sh` never need it loaded at import time.
    import httpx

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        # ``max_tokens`` is the broadly-compatible OpenAI output cap honored by
        # Featherless (a vLLM-class server); it maps the Protocol's max_tokens
        # so the knob is honored rather than silently dropped.
        "max_tokens": max_tokens,
        "temperature": temperature,
        # Request-time thinking toggle: the Qwen3 convention for an
        # OpenAI-compatible server is the chat-template kwarg ``enable_thinking``
        # (the sibling of Ollama's top-level ``think=``). False suppresses
        # reasoning so structured-output decoding stays clean.
        "chat_template_kwargs": {"enable_thinking": request_thinking},
    }
    if response_format is not None:
        payload["response_format"] = response_format

    # A fresh client per call (closed via the async context manager) keeps the
    # module-level send-hook stateless — there is no FeatherlessClient instance
    # on which to hang a pooled client without introducing module-level state
    # (which the design forbids), mirroring the Ollama / Anthropic adapters.
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=httpx.Timeout(600.0),
        )
        response.raise_for_status()
        body = response.json()

    return _raw_from_response_body(body, model=model)


def _raw_from_response_body(
    body: dict[str, Any],
    *,
    model: str,
) -> FeatherlessRawResponse:
    """Map an OpenAI-shaped chat-completions body onto a raw response.

    Fails loud (AGENTS.md: no silent fallbacks) on the anomalous shapes a
    completed response never produces, because $0 cost zeroes the
    ``BudgetedLLMClient`` USD dimension and the token counters are the only
    real per-game backstop left:

    * empty / missing ``choices`` — no completion to record;
    * empty assistant ``content`` — mirrors the Anthropic "no text blocks"
      guard (a populated response always carries content);
    * missing ``usage`` block or missing ``prompt_tokens`` /
      ``completion_tokens`` — recording 0 tokens would under-count the budget.

    Split out of :func:`_default_send` so the mapping (which the live transport
    otherwise hides) is unit-testable without the network, like Ollama's
    :func:`~llm.ollama_client._raw_from_generate_response`.
    """

    choices = body.get("choices")
    if not choices:
        raise RuntimeError(
            f"Featherless response carried no choices (model={model!r}); "
            "refusing to record an empty completion."
        )
    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    if not content.strip():
        raise RuntimeError(
            f"Featherless returned empty assistant content (model={model!r})."
        )
    reasoning_content = message.get("reasoning_content") or ""

    usage = body.get("usage")
    if not usage:
        raise RuntimeError(
            f"Featherless response carried no usage block (model={model!r}); "
            "refusing to record 0 tokens, which would under-count the per-game "
            "token budget (the only backstop under $0 provider-keyed cost)."
        )
    if "prompt_tokens" not in usage or "completion_tokens" not in usage:
        raise RuntimeError(
            "Featherless usage block omitted prompt_tokens / completion_tokens "
            f"(model={model!r}); refusing to record 0 tokens, which would "
            "under-count the per-game token budget."
        )

    return FeatherlessRawResponse(
        text=content,
        model=body.get("model") or model,
        prompt_tokens=usage["prompt_tokens"],
        completion_tokens=usage["completion_tokens"],
        reasoning_content=reasoning_content,
    )


__all__ = [
    "DEFAULT_FEATHERLESS_BASE_URL",
    "DEFAULT_FEATHERLESS_MODEL",
    "DEFAULT_THINKING_POLICY",
    "FeatherlessClient",
    "FeatherlessRawResponse",
    "FeatherlessSendHook",
    "ThinkingPolicy",
]
