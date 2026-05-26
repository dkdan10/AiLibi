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

import os
import re
from collections.abc import Awaitable, Callable
from typing import Final

from pydantic import BaseModel, ConfigDict, ValidationError

from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage


DEFAULT_MEETING_MODEL: Final[str] = "claude-sonnet-4-6"
DEFAULT_TRIGGER_MODEL: Final[str] = "claude-haiku-4-5-20251001"

ENV_PROVIDER: Final[str] = "AILIBI_LLM_PROVIDER"
ENV_MEETING_MODEL: Final[str] = "AILIBI_LLM_MEETING_MODEL"
ENV_TRIGGER_MODEL: Final[str] = "AILIBI_LLM_TRIGGER_MODEL"
ENV_ANTHROPIC_API_KEY: Final[str] = "ANTHROPIC_API_KEY"

PROVIDER_ANTHROPIC: Final[str] = "anthropic"
PROVIDER_FAKE: Final[str] = "fake"

# Anthropic per-million-token list pricing as of 2026-05. Kept private so
# call sites never depend on it; if pricing changes only this file moves.
_ANTHROPIC_PRICING_USD_PER_MTOK: Final[dict[str, tuple[float, float]]] = {
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
}
_FALLBACK_PRICING_USD_PER_MTOK: Final[tuple[float, float]] = (3.00, 15.00)


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
    ) -> LLMResponse:
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
        text = _extract_json_block(raw.text) if schema is not None else raw.text
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
) -> LLMClient:
    """Construct the default :class:`LLMClient` from environment configuration.

    Selection rules:

    * ``AILIBI_LLM_PROVIDER=fake`` (or unset) → :class:`llm.fake_provider.FakeProvider`.
      This is the default because CI must never hit the network.
    * ``AILIBI_LLM_PROVIDER=anthropic`` → :class:`AnthropicClient`, with model
      ids picked from ``AILIBI_LLM_MEETING_MODEL`` /
      ``AILIBI_LLM_TRIGGER_MODEL`` when set, otherwise their canonical
      defaults.

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
    raise ValueError(
        f"unknown {ENV_PROVIDER} value: {provider!r}; "
        f"expected one of {PROVIDER_ANTHROPIC!r} or {PROVIDER_FAKE!r}"
    )


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


def _extract_json_block(text: str) -> str:
    """Extract the first balanced JSON object from an LLM response.

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

    Strategy: find the first ``{``, then walk forward tracking brace
    depth with string-literal awareness (braces inside ``"..."`` do not
    count, and ``\\`` escape sequences are respected) and return the
    substring from that ``{`` to its matching ``}``, stripped of
    surrounding whitespace. When the input has no ``{`` at all, or the
    object never closes (a response truncated mid-output — Task 3.17's
    case), fall back to :func:`_strip_json_code_fences` so its documented
    unclosed-fence / no-JSON semantics are preserved (the incomplete body
    reaches Pydantic as an actionable ``ValidationError`` rather than a
    leading-backtick parse error).
    """

    open_index = text.find("{")
    if open_index == -1:
        return _strip_json_code_fences(text)

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
                return text[open_index : index + 1].strip()
    # The first ``{`` never closed (truncated mid-object): fall back to
    # the fence-strip behavior so truncated responses keep Task 3.17's
    # semantics rather than returning a half-object here.
    return _strip_json_code_fences(text)


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
) -> float:
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
    "ENV_PROVIDER",
    "ENV_TRIGGER_MODEL",
    "LLMCallFailure",
    "PROVIDER_ANTHROPIC",
    "PROVIDER_FAKE",
    "SendHook",
    "build_default_client",
    "extract_parse_failure",
]
