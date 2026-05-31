"""Anthropic provider adapter (DESIGN.md §7, §10.4).

:class:`AnthropicClient` implements the :class:`~llm.client.LLMClient`
Protocol against the Anthropic SDK. Anthropic-specific knobs (extended
thinking, ``cache_control``, prompt-caching beta headers, message-shape
internals) are private parameters on :meth:`AnthropicClient.__init__` and
never leak through the Protocol.

CI never imports the real SDK: the adapter does the import lazily inside
:meth:`complete`. Unit tests that touch this file pass an injected
``_send`` hook so the SDK stays optional in the test environment.
"""

from __future__ import annotations

import json
import os
import re
from collections.abc import Awaitable, Callable
from typing import Final

from pydantic import BaseModel, ConfigDict, ValidationError

from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.report_normalize import normalize_report_payload


DEFAULT_MEETING_MODEL: Final[str] = "claude-sonnet-4-6"
DEFAULT_TRIGGER_MODEL: Final[str] = "claude-haiku-4-5-20251001"

ENV_PROVIDER: Final[str] = "AILIBI_LLM_PROVIDER"
ENV_MEETING_MODEL: Final[str] = "AILIBI_LLM_MEETING_MODEL"
ENV_TRIGGER_MODEL: Final[str] = "AILIBI_LLM_TRIGGER_MODEL"
ENV_ANTHROPIC_API_KEY: Final[str] = "ANTHROPIC_API_KEY"
ENV_OLLAMA_HOST: Final[str] = "AILIBI_OLLAMA_HOST"
ENV_OLLAMA_SEED: Final[str] = "AILIBI_OLLAMA_SEED"

PROVIDER_ANTHROPIC: Final[str] = "anthropic"
PROVIDER_FAKE: Final[str] = "fake"
PROVIDER_OLLAMA: Final[str] = "ollama"

# Anthropic per-million-token list pricing as of 2026-05. Kept private so
# call sites never depend on it; if pricing changes only this file moves.
_ANTHROPIC_PRICING_USD_PER_MTOK: Final[dict[str, tuple[float, float]]] = {
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
}
_FALLBACK_PRICING_USD_PER_MTOK: Final[tuple[float, float]] = (3.00, 15.00)

# Ollama runs a local open model for $0. The rate is keyed by PROVIDER,
# not by model name: every Ollama model resolves to the (0.0, 0.0)
# fallback, so an A/B swap (``qwen2.5:7b`` -> ``llama3.1:8b``) cannot
# silently fall back to a non-zero frontier rate the way a model-keyed
# lookup against the Anthropic table would. The per-model dict is the
# optional override surface (empty today) for a hypothetical metered
# local endpoint; absent an entry the zero fallback applies.
_OLLAMA_PRICING_USD_PER_MTOK: Final[dict[str, tuple[float, float]]] = {}
_OLLAMA_FALLBACK_PRICING_USD_PER_MTOK: Final[tuple[float, float]] = (0.0, 0.0)


class AnthropicRawResponse(BaseModel):
    """Provider-agnostic shape that the injectable ``_send`` hook returns.

    Real SDK responses are unpacked into this Pydantic model inside the
    adapter; the rest of the adapter (pricing, structured-output
    validation, :class:`LLMResponse` construction) operates on this shape
    so unit tests can inject deterministic fixtures.
    """

    text: str
    model: str
    input_tokens: int
    output_tokens: int


class LLMCallFailure(BaseModel):
    """Cost + partial-response metadata for a schema-validation failure.

    Constructed inside :meth:`AnthropicClient.complete` when a non-empty
    provider response fails ``model_validate_json`` and attached to the
    propagating :class:`~pydantic.ValidationError` (see
    :func:`extract_parse_failure`). The orchestrator's recording layer
    reads it off the exception and persists a failed-call audit row so
    post-mortem analysis can reconstruct how much was paid for the
    response that broke the meeting, even though the meeting still aborts
    (DESIGN.md §11.4; Task 3.19 finding 2).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str
    prompt_length: int
    raw_response: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    error_type: str
    error_message: str


SendHook = Callable[..., Awaitable[AnthropicRawResponse]]


class AnthropicClient:
    """Real LLM adapter behind the :class:`~llm.client.LLMClient` Protocol.

    Public surface is just :meth:`complete`. Anthropic-only configuration
    lives on the constructor:

    * ``meeting_model`` — model id for ``call_kind == "meeting"``. Defaults
      to :data:`DEFAULT_MEETING_MODEL`.
    * ``trigger_model`` — model id for ``call_kind == "trigger"``. Defaults
      to :data:`DEFAULT_TRIGGER_MODEL`.
    * ``api_key`` — Anthropic API key. Read from ``ANTHROPIC_API_KEY`` by
      :func:`build_default_client` when not passed explicitly.
    * ``extended_thinking`` / ``prompt_caching_beta`` — Anthropic-only
      knobs. Private; never on the Protocol.
    * ``send`` — injectable transport hook used by unit tests in place of
      the real SDK. Defaults to ``None`` (real SDK).
    """

    def __init__(
        self,
        *,
        api_key: str,
        meeting_model: str = DEFAULT_MEETING_MODEL,
        trigger_model: str = DEFAULT_TRIGGER_MODEL,
        extended_thinking: bool = False,
        prompt_caching_beta: bool = False,
        send: SendHook | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("AnthropicClient requires a non-empty api_key")
        self._api_key = api_key
        self._meeting_model = meeting_model
        self._trigger_model = trigger_model
        self._extended_thinking = extended_thinking
        self._prompt_caching_beta = prompt_caching_beta
        self._send: SendHook = send if send is not None else _default_send

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
        # (DESIGN.md §11.4), not a provider knob — it is deliberately not
        # forwarded to the upstream Anthropic SDK.
        del agent_id
        chosen_model = model if model is not None else self._model_for(call_kind)
        raw = await self._send(
            api_key=self._api_key,
            model=chosen_model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            extended_thinking=self._extended_thinking,
            prompt_caching_beta=self._prompt_caching_beta,
        )
        # Cost is computed up front so the same figure is available both
        # for the successful LLMResponse and for the failure carrier
        # attached to a ValidationError below: the model already burned
        # these tokens regardless of whether the response parses, so the
        # crashing-meeting cost must be recoverable (Task 3.19 finding 2).
        cost_usd = _compute_cost_usd(
            model=raw.model,
            input_tokens=raw.input_tokens,
            output_tokens=raw.output_tokens,
        )
        # Claude models wrap (and sometimes precede) structured-output
        # JSON with markdown fences and "thinking" prose by default.
        # Extract the balanced JSON object at the Protocol boundary so
        # Pydantic — and the recorded LLMResponse.text — see schema-
        # validatable JSON. Placement inside complete() (not _default_send)
        # means a future fencing adapter inherits this.
        text = _extract_json_block(raw.text, schema) if schema is not None else raw.text
        if schema is not None:
            try:
                schema.model_validate_json(text)
            except ValidationError as exc:
                # Attach the cost + partial response to the propagating
                # ValidationError so the orchestrator's recording layer
                # can persist a failed-call audit trail before the meeting
                # aborts. The exception type and message are left untouched
                # so callers that catch ValidationError (including the
                # truncation-failure-mode tests) are unaffected.
                _attach_parse_failure(
                    exc,
                    LLMCallFailure(
                        model=raw.model,
                        prompt_length=len(prompt),
                        raw_response=raw.text[:_RAW_RESPONSE_CHARS],
                        input_tokens=raw.input_tokens,
                        output_tokens=raw.output_tokens,
                        cost_usd=cost_usd,
                        error_type=type(exc).__name__,
                        error_message=str(exc)[:_ERROR_MESSAGE_CHARS],
                    ),
                )
                raise
        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=raw.input_tokens,
                output_tokens=raw.output_tokens,
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


def build_default_client(
    *,
    env: dict[str, str] | None = None,
    send: SendHook | None = None,
    seed: int | None = None,
) -> LLMClient:
    """Construct the default :class:`LLMClient` from environment configuration.

    Selection rules:

    * ``AILIBI_LLM_PROVIDER=fake`` (or unset) → :class:`llm.fake_provider.FakeProvider`.
      This is the default because CI must never hit the network.
    * ``AILIBI_LLM_PROVIDER=anthropic`` → :class:`AnthropicClient`, with model
      ids picked from ``AILIBI_LLM_MEETING_MODEL`` /
      ``AILIBI_LLM_TRIGGER_MODEL`` when set, otherwise their canonical
      defaults. Retained as a still-supported alternative (re-recording
      the frozen baseline; cross-provider validation) — not dead code.
    * ``AILIBI_LLM_PROVIDER=ollama`` → :class:`llm.ollama_client.OllamaClient`,
      POSTing to ``AILIBI_OLLAMA_HOST`` (default ``localhost:11434``) and
      reusing the same ``AILIBI_LLM_MEETING_MODEL`` /
      ``AILIBI_LLM_TRIGGER_MODEL`` knobs, both defaulting to
      ``qwen2.5:7b-instruct`` (the canonical Phase 7 local model).

    ``seed`` is the per-game seed the Ollama client folds into
    ``options.seed`` for reproducible-ish fresh generation; when ``None``
    it is resolved from ``AILIBI_OLLAMA_SEED`` (falling back to
    :data:`llm.ollama_client.DEFAULT_OLLAMA_SEED`). It is ignored by the
    fake and Anthropic branches. ``send`` is the Anthropic transport hook
    only; the Ollama client's transport is injected directly in its unit
    tests, so it is deliberately not plumbed here.

    The function takes an ``env`` dict so callers can construct clients
    deterministically in tests; production callers pass ``env=None`` and
    the real process environment is consulted.
    """

    environment = env if env is not None else dict(os.environ)
    provider = environment.get(ENV_PROVIDER, PROVIDER_FAKE).strip().lower()
    if provider == PROVIDER_FAKE:
        from llm.fake_provider import FakeProvider

        return FakeProvider()
    if provider == PROVIDER_ANTHROPIC:
        api_key = environment.get(ENV_ANTHROPIC_API_KEY, "")
        if not api_key:
            raise ValueError(
                f"{ENV_ANTHROPIC_API_KEY} must be set when "
                f"{ENV_PROVIDER}={PROVIDER_ANTHROPIC}"
            )
        return AnthropicClient(
            api_key=api_key,
            meeting_model=environment.get(ENV_MEETING_MODEL, DEFAULT_MEETING_MODEL),
            trigger_model=environment.get(ENV_TRIGGER_MODEL, DEFAULT_TRIGGER_MODEL),
            send=send,
        )
    if provider == PROVIDER_OLLAMA:
        # Lazy import keeps the ollama SDK optional at module-import time,
        # mirroring the fake/anthropic branches: a non-Ollama run never
        # imports ollama_client (and thus never the ollama package).
        from llm.ollama_client import (
            DEFAULT_OLLAMA_HOST,
            DEFAULT_OLLAMA_MODEL,
            OllamaClient,
        )

        host = environment.get(ENV_OLLAMA_HOST, "").strip() or DEFAULT_OLLAMA_HOST
        return OllamaClient(
            host=host,
            seed=seed if seed is not None else _ollama_seed_from_env(environment),
            meeting_model=environment.get(ENV_MEETING_MODEL, DEFAULT_OLLAMA_MODEL),
            trigger_model=environment.get(ENV_TRIGGER_MODEL, DEFAULT_OLLAMA_MODEL),
        )
    raise ValueError(
        f"unknown {ENV_PROVIDER} value: {provider!r}; expected one of "
        f"{PROVIDER_ANTHROPIC!r}, {PROVIDER_OLLAMA!r}, or {PROVIDER_FAKE!r}"
    )


def _ollama_seed_from_env(environment: dict[str, str]) -> int:
    """Resolve the Ollama per-game seed from ``AILIBI_OLLAMA_SEED``.

    Parses the value as a base-10 integer (leading zeros tolerated, so a
    shell-exported ``007`` is 7, never octal). Returns
    :data:`llm.ollama_client.DEFAULT_OLLAMA_SEED` when the var is
    unset/empty. A non-integer value is fail-loud (AGENTS.md: no silent
    fallbacks) rather than silently substituting the default.
    """

    from llm.ollama_client import DEFAULT_OLLAMA_SEED

    raw = environment.get(ENV_OLLAMA_SEED, "").strip()
    if not raw:
        return DEFAULT_OLLAMA_SEED
    try:
        return int(raw, 10)
    except ValueError as exc:
        raise ValueError(
            f"{ENV_OLLAMA_SEED} must be a base-10 integer, got {raw!r}"
        ) from exc


# Caps on the metadata captured for a failed structured-output call
# (Task 3.19 finding 2). The raw response is truncated to the first ~1KB
# and the exception message to the first 200 chars so a pathologically
# long response or error message cannot bloat the replay log.
_RAW_RESPONSE_CHARS: Final[int] = 1024
_ERROR_MESSAGE_CHARS: Final[int] = 200

# Private attribute under which a :class:`LLMCallFailure` is stashed on a
# ValidationError so the failure metadata rides the propagating exception
# up to the orchestrator's recording layer. Carrying it on the exception
# (rather than changing the exception type) keeps every caller that
# catches ``ValidationError`` unaffected; carrying it on an instance
# attribute (rather than a module-level structure) keeps the adapter free
# of mutable global state (AGENTS.md). The name is project-namespaced to
# avoid colliding with any pydantic internals.
_PARSE_FAILURE_ATTR: Final[str] = "_ailibi_parse_failure"


def _attach_parse_failure(exc: BaseException, failure: LLMCallFailure) -> None:
    setattr(exc, _PARSE_FAILURE_ATTR, failure)


def extract_parse_failure(exc: BaseException) -> LLMCallFailure | None:
    """Return the :class:`LLMCallFailure` carried by ``exc``, if any.

    :meth:`AnthropicClient.complete` attaches an :class:`LLMCallFailure`
    to the :class:`~pydantic.ValidationError` it re-raises when a
    structured-output response fails to validate. The orchestrator calls
    this on the meeting-failure path to recover the cost + partial-
    response metadata for the replay log. Returns ``None`` for any
    exception that carries no such metadata (a provider/deadline timeout,
    or a fake-provider run that never fails validation), so the caller
    records a failed-call row only for genuine schema-validation crashes.
    """

    failure = getattr(exc, _PARSE_FAILURE_ATTR, None)
    return failure if isinstance(failure, LLMCallFailure) else None


def _find_matching_brace(text: str, open_index: int) -> int:
    """Return the index of the ``}`` that closes the ``{`` at ``open_index``.

    Walks forward from ``open_index`` tracking brace depth with string-
    literal awareness: braces inside ``"..."`` do not count toward depth,
    and a ``\\`` escape protects the next character (so ``\\"`` does not
    end the string and ``\\}`` is not a closing brace). Returns ``-1`` if
    depth never returns to zero — the object was truncated mid-output, or
    ``open_index`` is a stray opener with no matching close.
    """

    depth = 0
    in_string = False
    escape_next = False
    for index in range(open_index, len(text)):
        char = text[index]
        if escape_next:
            escape_next = False
            continue
        if in_string:
            if char == "\\":
                escape_next = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


def _extract_json_block(text: str, schema: type[BaseModel] | None = None) -> str:
    """Extract the JSON object from an LLM response, then normalize it (Task 7.6).

    Raw extraction (markdown fences, prose preamble, mid-output truncation) is
    delegated to :func:`_extract_raw_json_block`. When ``schema`` is supplied,
    the extracted JSON additionally passes through discriminator-aware
    normalization (:func:`_normalize_json_text`) so a near-miss model report —
    e.g. a ``co_present`` key on a ``found_body`` observation — is salvaged into
    a payload that survives ``extra="forbid"`` before ``model_validate_json``
    runs. This is the single shared seam every provider adapter (Anthropic and
    the Ollama client) routes through, so normalization is not duplicated per
    client. With ``schema=None`` (free-text calls, or any non-structured use)
    the extracted text is returned unchanged.
    """

    raw_block = _extract_raw_json_block(text)
    if schema is None:
        return raw_block
    return _normalize_json_text(raw_block, schema)


def _normalize_json_text(text: str, schema: type[BaseModel]) -> str:
    """Strip discriminated-union variant extras from extracted JSON ``text``.

    Parses ``text``, runs the pure
    :func:`llm.report_normalize.normalize_report_payload` over it against
    ``schema``, and re-serializes ONLY when normalization actually changed the
    payload. An already-valid payload is therefore returned byte-identical (a
    true no-op, so recorded outputs replay unchanged); text that does not parse
    as JSON is returned unchanged so the downstream ``model_validate_json``
    raises its actionable error rather than this helper masking it.
    """

    try:
        payload = json.loads(text)
    except ValueError:
        return text
    normalized = normalize_report_payload(payload, schema)
    if normalized == payload:
        return text
    return json.dumps(normalized)


def _extract_raw_json_block(text: str) -> str:
    """Extract the first valid JSON object from an LLM response.

    Claude models emit structured-output JSON in several shapes across
    the Pre-Phase-4 evals; this normalises all of them to the bare JSON
    object ``model_validate_json`` expects:

    * **Clean JSON** (``{...}`` start to finish) → returned unchanged.
    * **Fenced JSON** (```` ```json\\n{...}\\n``` ````) → fences dropped.
    * **Prose preamble + fenced/bare JSON** (``I need to analyze...\\n{...}``)
      → the prose is ignored and the JSON extracted. Task 3.19 finding 1:
      Sonnet 4.6 nondeterministically emits "thinking" prose before its
      fenced output, which the open-anchored fence strip could not handle.
    * **JSON + trailing prose** (``{...}\\n\\nDone!``) → trailing prose
      dropped.

    Strategy: scan each ``{`` left to right; for each, find its matching
    ``}`` (:func:`_find_matching_brace`, string-literal aware) and return
    the first balanced span that itself parses as JSON. Validating each
    candidate means a brace that merely *appears* in the prose preamble —
    a balanced-but-not-JSON span like ``{steps}`` or a stray unmatched
    ``{`` — is skipped in favour of the real object that follows, rather
    than aborting the call on it (Task 3.19 finding 1, hardening).

    Fallbacks, both yielding an actionable ``ValidationError`` rather than
    a ``line 1 column 1`` parse error on a leading prose/backtick char:

    * No ``{`` at all → :func:`_strip_json_code_fences` (passes non-fenced
      prose through, strips a truncated leading fence).
    * A ``{`` exists but no candidate parsed (the real object was
      truncated mid-output — Task 3.17's case — possibly behind a prose
      preamble) → the body from the first ``{`` onward, so the incomplete
      object reaches Pydantic without the preamble/fence in front of it.
    """

    first_open = text.find("{")
    if first_open == -1:
        return _strip_json_code_fences(text)

    search_from = first_open
    while search_from != -1:
        close_index = _find_matching_brace(text, search_from)
        if close_index != -1:
            candidate = text[search_from : close_index + 1].strip()
            try:
                json.loads(candidate)
            except ValueError:
                pass  # balanced but not JSON (e.g. a "{steps}" prose span)
            else:
                return candidate
        search_from = text.find("{", search_from + 1)

    return text[first_open:].strip()


# Surrounding markdown code fences as emitted by Claude models for
# structured-output text. Open fence is anchored at the start (after any
# leading whitespace) with an optional, case-insensitive ``json`` tag;
# close fence is anchored at the end (before any trailing whitespace).
# The anchors mean backticks inside the JSON body are never touched.
_FENCE_OPEN_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^\s*```(?:json)?\s*", re.IGNORECASE
)
_FENCE_CLOSE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\s*```\s*$")


def _strip_json_code_fences(text: str) -> str:
    """Strip surrounding markdown code fences from an LLM JSON response.

    Anthropic models (Claude Sonnet 4.6, etc.) wrap JSON in
    ``` ```json … ``` ``` fences by default; this removes them so
    downstream ``model_validate_json`` sees clean JSON. Provider-neutral
    by placement: OpenAI / DeepSeek adapters that occasionally fence
    inherit the protection automatically.

    Behavior matrix (fences are anchored at the text edges, so backticks
    inside the JSON body are never touched):

    * Both open and close fence present → strip both, return trimmed.
    * Only an open fence present (a response truncated mid-output before
      the closing fence was emitted) → strip the opener, return the
      remainder trimmed. The remainder is incomplete JSON, so
      ``model_validate_json`` fails loud with a missing-fields / EOF
      ``ValidationError`` — an actionable signal — rather than an
      ``Invalid JSON … line 1 column 1`` error on the leading backtick.
    * Only a close fence present (no opener to strip) → return unchanged.
    * No fences present → return unchanged.

    Strict on the trailing edge: only the opening fence is stripped, never
    a trailing partial fence. The risk of trimming legitimate content
    outweighs the benefit; a truly-truncated response should surface as a
    Pydantic ``ValidationError``. Nested fences and fence-inside-prose are
    likewise out of scope — they surface as validation errors too.
    """
    open_match = _FENCE_OPEN_PATTERN.match(text)
    if open_match is None:
        return text
    remainder = text[open_match.end() :]
    close_match = _FENCE_CLOSE_PATTERN.search(remainder)
    if close_match is None:
        # Open fence with no matching close (truncated response): strip the
        # opener so Pydantic fails on the incomplete JSON body rather than
        # on the leading backtick.
        return remainder.strip()
    return remainder[: close_match.start()].strip()


def _compute_cost_usd(
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
    provider: str = PROVIDER_ANTHROPIC,
) -> float:
    """Cost in USD for a completion, keyed by ``provider`` then ``model``.

    ``provider`` defaults to :data:`PROVIDER_ANTHROPIC` so the Anthropic
    call site (and its recorded costs) is byte-identical to before this
    parameter existed. :data:`PROVIDER_OLLAMA` selects the local-model
    rate table, whose zero fallback makes every Ollama model free
    regardless of name (see :data:`_OLLAMA_PRICING_USD_PER_MTOK`).
    """

    if provider == PROVIDER_OLLAMA:
        input_rate, output_rate = _OLLAMA_PRICING_USD_PER_MTOK.get(
            model, _OLLAMA_FALLBACK_PRICING_USD_PER_MTOK
        )
    else:
        input_rate, output_rate = _ANTHROPIC_PRICING_USD_PER_MTOK.get(
            model, _FALLBACK_PRICING_USD_PER_MTOK
        )
    return (input_tokens / 1_000_000.0) * input_rate + (
        output_tokens / 1_000_000.0
    ) * output_rate


async def _default_send(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    extended_thinking: bool,
    prompt_caching_beta: bool,
) -> AnthropicRawResponse:
    # Lazy import per the module docstring (lines 9-11): the real SDK is
    # only imported when an AnthropicClient is actually invoked, so
    # FakeProvider-only test runs and `bash scripts/check.sh` never need
    # it loaded at import time.
    import anthropic

    # extended_thinking and prompt_caching_beta are plumbed through the
    # signature for a future task; wiring them to the SDK is a separate
    # concern (see PR ## Decisions). Bind them so they read as
    # intentionally-unused rather than dropped.
    _ = extended_thinking
    _ = prompt_caching_beta

    # Use the client as an async context manager so its underlying httpx
    # connection pool is closed deterministically after each call.
    # `_default_send` is a stateless module-level send-hook, so there is no
    # AnthropicClient instance on which to hang a long-lived pooled client
    # without introducing module-level state (which the design forbids).
    async with anthropic.AsyncAnthropic(api_key=api_key) as client:
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

    text_blocks = [
        block.text
        for block in response.content
        if isinstance(block, anthropic.types.TextBlock)
    ]
    if not text_blocks:
        raise RuntimeError(
            f"Anthropic returned no text content blocks (model={model!r})"
        )

    return AnthropicRawResponse(
        model=response.model,
        text="".join(text_blocks),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


__all__ = [
    "AnthropicClient",
    "AnthropicRawResponse",
    "DEFAULT_MEETING_MODEL",
    "DEFAULT_TRIGGER_MODEL",
    "ENV_ANTHROPIC_API_KEY",
    "ENV_MEETING_MODEL",
    "ENV_OLLAMA_HOST",
    "ENV_OLLAMA_SEED",
    "ENV_PROVIDER",
    "ENV_TRIGGER_MODEL",
    "LLMCallFailure",
    "PROVIDER_ANTHROPIC",
    "PROVIDER_FAKE",
    "PROVIDER_OLLAMA",
    "SendHook",
    "build_default_client",
    "extract_parse_failure",
]
