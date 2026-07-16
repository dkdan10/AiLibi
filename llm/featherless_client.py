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

Structured output — ``response_format_mode`` (owner-ratified finding 2026-06-27)
================================================================================

Task 14.1's contract named the strict ``json_schema`` ``response_format`` as
the OpenAI-compatible analogue of Ollama's ``format=schema.model_json_schema()``.
LIVE testing against the Featherless slate (Qwen3-32B, Qwen3-30B-A3B, GLM-4-32B)
showed that shape is **rejected with a deterministic HTTP 400** on every slate
model — Featherless does not implement guided ``json_schema`` decoding for them
(the only capability it advertises is ``tool_use``, and forced tool-calling is
not honored either). ``response_format={"type":"json_object"}`` (syntactic-JSON
mode) succeeds on every model, and the 32B-class models clear the
structured-output parse bar on the production prompts under ``json_object`` (and
even with no ``response_format`` at all — exactly how the Anthropic adapter has
always worked: prompt + extract + validate + FailedCall, no constrained
decoding).

The Task 16.1 probe RE-VERIFIED this posture UNCHANGED on the locked production
model ``Qwen/Qwen3.6-27B`` (Task 16.2, audits/audit-phase-16-model-lock.md):
``json_object`` accepted 2/2 on BOTH production schemas (MeetingTurn, VoteBallot,
JSON content), while strict ``json_schema`` was deterministically rejected 0/2 on
both (HTTP 400 — the incumbent's same-day re-verify rejected 0/2 too, at drifting
422/504 statuses; the VERDICT, not the status code, is the pin). So ``json_object``
stays the default and there is still NO silent fallback between modes.

So the wire shape is a constructor knob, :data:`ResponseFormatMode`, defaulting
to ``json_object``: ``json_schema`` is kept selectable for a future
endpoint/model that supports it (and so 14.4 can A/B it), but it is never the
default and there is NO silent fallback between modes — the mode is explicit and
a rejected ``json_schema`` request fails loud. Regardless of mode the response
routes through the SAME shared seam the Anthropic and Ollama adapters use:

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
  Qwen3 convention for OpenAI-compatible servers) — but ONLY for models
  EXPLICITLY classified as honoring that chat-template kwarg
  (:func:`_supports_thinking_kwarg`, an exact per-id lookup).
  The Task 14.4 sweep (``experiments/lab/report-featherless-sweep.md``) found
  the mandatory field is honored by the Qwen3 models but BREAKS the non-Qwen
  slate — ``zai-org/GLM-4-32B-0414`` collapses to an empty ``{}`` response and
  ``TheDrummer/Cydonia-24B-v2`` 400/504s — so the sweep had to route them
  through a sweep-local BARE send (``featherless_sweep.py:_bare_send``) that
  omits the field. This adapter instead makes the field CONDITIONAL: for a
  non-supporting model the whole ``chat_template_kwargs`` object is OMITTED (an
  empty ``{}`` is what broke GLM) and ``request_thinking`` is an explicit
  documented no-op (the model runs non-thinking). The gate is an EXPLICIT
  per-family signal, not a swallowed HTTP 400 (AGENTS.md §"No silent
  fallbacks"); an unrecognized id fails loud. This is the sweep AXIS 14.4
  drives.
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

import asyncio
import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Final, Literal, Protocol

from pydantic import BaseModel, ConfigDict, ValidationError

from llm.client import CallKind, LLMResponse, TokenUsage
from llm.provider import (
    _ERROR_MESSAGE_CHARS,
    _FENCE_OPEN_PATTERN,
    _RAW_RESPONSE_CHARS,
    PROVIDER_FEATHERLESS,
    LLMCallFailure,
    _attach_parse_failure,
    _compute_cost_usd,
    _extract_json_block,
)

# Reasoning-model marker pair some models emit inline around their chain of
# thought (Qwen3 etc.). Used both by the ``fail_loud`` guard (to detect inline
# reasoning) and by the ``strip`` path (to excise the block before extraction).
_THINK_CLOSE_TAG: Final[str] = "</think>"
_THINK_OPEN_TAG: Final[str] = "<think>"


_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

# Featherless exposes an OpenAI-compatible API; ``/chat/completions`` is
# appended to this base. Overridable via ``AILIBI_FEATHERLESS_BASE_URL`` (see
# :func:`llm.provider.build_default_client`) for a proxy or a self-hosted
# OpenAI-compatible endpoint.
DEFAULT_FEATHERLESS_BASE_URL: Final[str] = "https://api.featherless.ai/v1"
# Default model id (HuggingFace repo form, as Featherless expects). This IS the
# canonical PRODUCTION model — locked at Task 16.2
# (audits/audit-phase-16-model-lock.md, 2026-07-12), no longer a non-binding
# slate lead. ``Qwen/Qwen3.6-27B`` is the EXACT served id: the ``-Instruct``
# variant 404s, so the un-suffixed id is the only servable form
# (generation-preflight-confirmed). Still overridable per ``call_kind`` via
# ``AILIBI_LLM_MEETING_MODEL`` / ``AILIBI_LLM_TRIGGER_MODEL``.
DEFAULT_FEATHERLESS_MODEL: Final[str] = "Qwen/Qwen3.6-27B"

ThinkingPolicy = Literal["fail_loud", "strip"]
# Response-side policy applied when a response carries reasoning. ``fail_loud``
# mirrors the Ollama doctrine (a half-thinking run is refused, not recorded);
# ``strip`` is the 14.4-sweep harness choice (reasoning discarded explicitly).
DEFAULT_THINKING_POLICY: Final[ThinkingPolicy] = "fail_loud"

ResponseFormatMode = Literal["json_object", "json_schema", "none"]
# How a structured (schema-bearing) call asks Featherless for JSON:
#
# * ``json_object`` — ``response_format={"type":"json_object"}``: the model is
#   forced to emit syntactically valid JSON. It does NOT constrain the schema
#   shape; conformance is enforced afterward by the shared
#   ``_extract_json_block`` -> ``model_validate_json`` -> FailedCall seam
#   (exactly how the Anthropic adapter — which sends NO ``response_format`` —
#   has always worked).
# * ``json_schema`` — the strict ``{"type":"json_schema",...,"strict":True}``
#   grammar shape. This is true constrained decoding WHERE THE BACKEND
#   IMPLEMENTS IT (OpenAI, a vLLM server with guided decoding, local Ollama's
#   GBNF). On the Featherless slate it is NOT implemented and is REJECTED with
#   an HTTP 400, so it is an explicit opt-in for a future endpoint/model that
#   supports it, never the default.
# * ``none`` — send no ``response_format`` at all (the pure Anthropic shape).
#
# DEFAULT is ``json_object`` (owner-ratified deviation 2026-06-27 — see the
# module docstring): live testing showed every Phase-14 slate model returns a
# deterministic 400 to ``json_schema`` while ``json_object`` succeeds, and the
# 32B-class models clear the structured-output parse bar on the production
# prompts under ``json_object`` (and even with ``none``). The Task 16.1 probe
# re-verified this posture UNCHANGED on the locked ``Qwen/Qwen3.6-27B``
# (``json_object`` accepted 2/2, strict ``json_schema`` rejected 0/2 — Task 16.2,
# audits/audit-phase-16-model-lock.md). There is NO silent fallback between modes
# (AGENTS.md): the mode is chosen explicitly at construction time; a rejected
# ``json_schema`` request fails loud.
DEFAULT_RESPONSE_FORMAT_MODE: Final[ResponseFormatMode] = "json_object"


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
      ``chat_template_kwargs={"enable_thinking": ...}`` for Qwen3-family models
      and an explicit no-op (the field is omitted) for non-supporting models
      (:func:`_supports_thinking_kwarg`). Default ``False``.
    * ``thinking_policy`` — the response-side policy (``fail_loud`` default /
      ``strip``). Distinct from ``request_thinking``.
    * ``response_format_mode`` — how a structured call asks for JSON
      (``json_object`` default / ``json_schema`` / ``none``). See
      :data:`ResponseFormatMode`; ``json_object`` is the Featherless-supported
      default (strict ``json_schema`` is rejected by the slate).
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
        response_format_mode: ResponseFormatMode = DEFAULT_RESPONSE_FORMAT_MODE,
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
        if response_format_mode not in ("json_object", "json_schema", "none"):
            raise ValueError(
                "FeatherlessClient response_format_mode must be 'json_object', "
                f"'json_schema', or 'none', got {response_format_mode!r}"
            )
        self._api_key = api_key
        # Normalize a trailing slash so ``{base_url}/chat/completions`` never
        # produces a double slash.
        self._base_url = base_url.rstrip("/")
        self._meeting_model = meeting_model
        self._trigger_model = trigger_model
        self._request_thinking = request_thinking
        self._thinking_policy: ThinkingPolicy = thinking_policy
        self._response_format_mode: ResponseFormatMode = response_format_mode
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
        # Translate the engine-free ``schema`` into the wire ``response_format``
        # per the configured mode (default ``json_object``; see
        # :data:`DEFAULT_RESPONSE_FORMAT_MODE` and the module docstring). ``None``
        # for a free-text call or the ``none`` mode.
        response_format = self._response_format_for(schema)
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
        content = raw.text
        if reasoning is not None:
            if self._thinking_policy == "fail_loud":
                # Deliberate abort-vs-recoverable trade-off (PR #202 review):
                # this raises a RuntimeError, NOT a recoverable FailedCall like
                # a schema-invalid body. The meeting manager's fail-soft nets
                # only TimeoutError / ValidationError, so this propagates and
                # aborts the run — by design: recording a half-thinking run is
                # exactly the failure mode the guard exists to prevent (Ollama
                # parity), so it must fail loud rather than silently record. The
                # cost: a BENIGN leading preamble on a structured call ("Here is
                # the turn: {...}") that ``_extract_json_block`` would have
                # accepted is also flagged and aborts. Acceptable in production
                # because the default ``json_object`` mode forces JSON-first
                # output (a preamble is rare), and 14.7's smoke gate
                # (parse-success ~100%, abandon-on-crater) catches any model
                # that emits one before the atomic 50-seed re-record.
                raise RuntimeError(
                    "Featherless returned reasoning under thinking_policy="
                    f"'fail_loud' (model={raw.model!r}): {reasoning}. Refusing "
                    "to record a half-thinking run; set request_thinking=False "
                    "to suppress reasoning, or thinking_policy='strip' to "
                    "discard it explicitly for the model sweep."
                )
            # ``strip``: discard reasoning EXPLICITLY (logged, never silent).
            # EXCISE a ``<think>...</think>`` reasoning block before extraction:
            # the shared ``_extract_json_block`` returns the FIRST valid JSON
            # object, so scratch/example JSON inside the reasoning would be
            # picked up instead of the final answer. Removing the block first
            # makes the extractor see the answer (a leading prose preamble
            # without think tags is still safely skipped by the extractor).
            content = _strip_reasoning_segment(content)
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
        # Pull the JSON object out of the (reasoning-stripped) text through the
        # SAME shared extractor the Anthropic / Ollama clients use, so 7.6's
        # normalization (which lands in that shared path) covers Featherless.
        text = _extract_json_block(content, schema) if schema is not None else content
        if schema is not None:
            try:
                schema.model_validate_json(text)
            except ValidationError as exc:
                # Under ``json_object`` (the default) the model is only
                # constrained to syntactic JSON, not the schema shape, so a
                # schema-invalid body is expected and must be recoverable.
                # Attach the cost + partial response to the
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

    def _response_format_for(
        self, schema: type[BaseModel] | None
    ) -> dict[str, Any] | None:
        """Build the wire ``response_format`` for ``schema`` per the active mode.

        Returns ``None`` for a free-text call (``schema is None``) or the
        ``none`` mode — the model is left unconstrained and the shared
        extract→validate→FailedCall seam carries correctness. ``json_object``
        forces syntactic JSON (the Featherless-supported default).
        ``json_schema`` builds the strict grammar shape (``name`` =
        ``schema.__name__``) — an explicit opt-in REJECTED by the current
        slate; there is no silent fallback to another mode.
        """

        if schema is None or self._response_format_mode == "none":
            return None
        if self._response_format_mode == "json_object":
            return {"type": "json_object"}
        return {
            "type": "json_schema",
            "json_schema": {
                "name": schema.__name__,
                "schema": schema.model_json_schema(),
                "strict": True,
            },
        }


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
    if _THINK_OPEN_TAG in lowered or _THINK_CLOSE_TAG in lowered:
        return "reasoning markers (<think>...</think>) in content"
    if schema is not None:
        # Strip a leading code-fence opener FIRST so reasoning buried inside a
        # fence (```json\nI think...\n{JSON}\n```) is still caught — a bare
        # ``startswith("```")`` skip would let it through, and the shared
        # extractor would then drop the prose silently (the exact gap the guard
        # exists to close). Reuse the same fence-opener pattern the extractor
        # strips so the two stay in lock-step.
        body = _FENCE_OPEN_PATTERN.sub("", text.lstrip(), count=1).lstrip()
        if body and not body.startswith("{"):
            first_brace = body.find("{")
            preamble = (body if first_brace == -1 else body[:first_brace]).strip()
            if preamble:
                return f"leading prose preamble before JSON ({len(preamble)} chars)"
    return None


def _strip_reasoning_segment(text: str) -> str:
    """Excise a leading ``<think>...</think>`` reasoning block from ``text``.

    Used by the ``strip`` thinking policy BEFORE :func:`_extract_json_block`:
    that extractor returns the FIRST valid JSON object, so a JSON object inside
    the reasoning (scratch notes, an example) would be selected instead of the
    model's final answer. Returns the content after the LAST ``</think>`` (a
    model may emit several blocks), left-stripped; if no closing tag is present
    the text is returned unchanged — a leading prose preamble without think
    tags is already handled safely by the extractor's first-valid-object scan.

    The closing tag is matched CASE-INSENSITIVELY so it stays in lock-step with
    :func:`_detect_reasoning` (which lowercases before matching): a model that
    emits ``</THINK>`` is detected as reasoning, so it must also be stripped —
    otherwise the block (and any scratch JSON inside it) would survive into the
    extractor, the exact failure this function exists to prevent (PR #202
    review). ``str.lower()`` preserves length/indices, so the offset is valid
    against the original ``text``.
    """

    close_at = text.lower().rfind(_THINK_CLOSE_TAG)
    if close_at == -1:
        return text
    return text[close_at + len(_THINK_CLOSE_TAG) :].lstrip()


# Transient HTTP statuses worth a bounded retry: rate-limiting plus the 5xx
# family. Featherless surfaces a genuinely-busy upstream as a 500 ("This model
# is busy, please try again later.") — distinct from a permanent 400 (an
# unsupported ``json_schema`` request), which must fail loud immediately rather
# than burn retries. The 50-seed re-record (Task 14.7) will hit transient 5xx,
# so a small backoff keeps an atomic run from aborting on a blip.
_RETRYABLE_STATUS: Final[frozenset[int]] = frozenset({429, 500, 502, 503, 504})
# Six call-level attempts (Task 17.9). A meeting-heavy corpus game is ~25
# sequential provider calls, and an intermittently-impaired Featherless can fail
# a given large call ~1-in-3 (a 504 gateway timeout, a mid-stream truncation).
# At 6 attempts a single call succeeds ~99.9% of the time, so ~97% of games
# complete first-try WITHOUT crashing/phantoming the whole game; 8+ adds only a
# fraction of a percent while the UNCAPPED exponential backoff below grows
# painful (2**attempt s: 16s at attempt 5, 64s at 7, 256s at 9) and piles load
# on a struggling backend, and the recorder's per-seed shell retry already
# backstops the rare residual miss. Kept modest so a PERMANENT outage still
# fails loud in bounded time rather than hanging.
_MAX_SEND_ATTEMPTS: Final[int] = 6
_SEND_BACKOFF_BASE_S: Final[float] = 1.0


class _HttpResponse(Protocol):
    """Structural type for the bits of an ``httpx.Response`` the retry needs.

    Declared structurally so :func:`_send_with_retry` is unit-testable with a
    fake response and ``httpx`` stays a lazy, test-optional import. The
    accessors are read-only properties so a real ``httpx.Response`` (whose
    ``text`` is a property) structurally matches.
    """

    @property
    def status_code(self) -> int: ...

    @property
    def text(self) -> str: ...

    def json(self) -> Any: ...


# Per-model thinking-capability registry (AGENTS.md §"No silent fallbacks").
#
# ``chat_template_kwargs.enable_thinking`` is the Qwen3 chat-template convention.
# The Task 14.4 sweep (``experiments/lab/report-featherless-sweep.md``) found it
# is honored ONLY by the Qwen3 models on Featherless and BREAKS the non-Qwen
# slate — ``zai-org/GLM-4-32B-0414`` collapses to an empty ``{}`` response and
# ``TheDrummer/Cydonia-24B-v2`` 400/504s — which is why the 14.4 harness routed
# those models through a sweep-local BARE send (``featherless_sweep.py:_bare_send``)
# that omits the field. This adapter makes the field CONDITIONAL on an EXPLICIT
# per-model capability signal instead, so the PRODUCTION client can call GLM /
# Cydonia without that workaround.
#
# The signal is an EXACT model-id lookup, NOT substring matching: each served id
# is classified DELIBERATELY (sweep-verified), so an unverified finetune or a new
# served revision whose name merely contains ``qwen3`` / ``glm`` / ``cydonia`` is
# NOT auto-classified — an UNRECOGNIZED id is a hard error, never a silent
# default. A new model must be added here on purpose (exactly the swallow-the-400
# fallback this task replaces). Stored as an immutable tuple of ``(id, supported)``
# pairs so the gate cannot be mutated at runtime (AGENTS.md §"No global state").
_THINKING_KWARG_BY_MODEL: Final[tuple[tuple[str, bool], ...]] = (
    # Qwen3 models — native ``enable_thinking`` (sweep-verified, Task 14.4).
    ("Qwen/Qwen3-8B", True),
    ("Qwen/Qwen3-32B", True),
    ("Qwen/Qwen3-30B-A3B", True),
    ("Qwen/Qwen3-30B-A3B-Instruct-2507", True),
    # Locked production model (probe-verified Task 16.1, locked Task 16.2 —
    # audits/audit-phase-16-model-lock.md). The 16.1 probe confirmed this served
    # id HONORS the Qwen3 ``chat_template_kwargs.enable_thinking`` kwarg, so it
    # is classified True. CRITICAL: this generation REASONS BY DEFAULT — with the
    # kwarg ABSENT it leaks inline ``</think>`` reasoning into ``content``;
    # ``enable_thinking=false`` suppresses it (0 channel chars). So production
    # PINS non-thinking on EVERY call: the constructor's ``request_thinking=False``
    # default combined with this True entry SENDS the kwarg (with false). An
    # unpinned call would leak inline ``</think>`` think-text into recorded state.
    ("Qwen/Qwen3.6-27B", True),
    # Non-Qwen slate — the mandatory field BREAKS them, so it is omitted (14.4).
    ("zai-org/GLM-4-32B", False),
    ("zai-org/GLM-4-32B-0414", False),
    ("TheDrummer/Cydonia-24B-v2", False),
)


def _supports_thinking_kwarg(model: str) -> bool:
    """Whether ``model``'s Featherless deployment honors ``enable_thinking``.

    Returns ``True`` for the Qwen3 models (the ``chat_template_kwargs.enable_thinking``
    kwarg is native) and ``False`` for the known non-Qwen slate (GLM, Cydonia),
    whose request the field BREAKS (14.4 sweep finding). Raises
    :class:`ValueError` on an unrecognized id: the capability is an EXPLICIT
    per-model decision (an EXACT id lookup against
    :data:`_THINKING_KWARG_BY_MODEL`, not a name-fragment guess), never a silent
    fallback (AGENTS.md), so an unknown model fails loud HERE — up front, by id —
    rather than 400-ing on the wire and being caught after the fact.
    """

    for known_id, supported in _THINKING_KWARG_BY_MODEL:
        if model == known_id:
            return supported
    raise ValueError(
        f"FeatherlessClient has no enable_thinking capability entry for model "
        f"{model!r}: it is not one of the classified ids "
        f"({[known_id for known_id, _ in _THINKING_KWARG_BY_MODEL]}). Classify "
        "it explicitly (add it to _THINKING_KWARG_BY_MODEL) rather than guessing "
        "whether to send the Qwen-only chat_template_kwargs.enable_thinking "
        "field (AGENTS.md: no silent fallbacks)."
    )


def _build_chat_payload(
    *,
    model: str,
    prompt: str,
    response_format: dict[str, Any] | None,
    max_tokens: int,
    temperature: float,
    request_thinking: bool,
) -> dict[str, Any]:
    """Assemble the OpenAI-compatible chat-completions request body.

    Pure (no I/O) so the wire shape is unit-testable without the transport.
    ``response_format`` is omitted entirely when ``None`` (free-text / ``none``
    mode). ``chat_template_kwargs.enable_thinking`` (the Qwen3 request-time
    thinking toggle) is sent ONLY for models explicitly classified as supporting
    it (:func:`_supports_thinking_kwarg`); the whole ``chat_template_kwargs``
    object is OMITTED otherwise, because an empty ``{}`` is what collapsed GLM in
    the 14.4 sweep. For a non-supporting model ``request_thinking`` is an explicit
    no-op — the field is dropped and the request runs non-thinking — rather than
    an error caught after a wire 400. An unrecognized model id fails loud (see
    :func:`_supports_thinking_kwarg`). ``max_tokens`` is the broadly-compatible
    OpenAI output cap honored by Featherless (a vLLM-class server).
    """

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    # Conditional on an explicit per-model capability signal: the Qwen3 path
    # keeps the field (byte-identical to 14.1); a non-Qwen model omits the whole
    # object (an empty ``{}`` is what broke GLM); an unknown id fails loud.
    if _supports_thinking_kwarg(model):
        payload["chat_template_kwargs"] = {"enable_thinking": request_thinking}
    if response_format is not None:
        payload["response_format"] = response_format
    return payload


def _format_send_error(status_code: int, body_text: str, model: str) -> str:
    """Descriptive message for a non-2xx Featherless response.

    Surfaces the status + a truncated body so an unsupported-``json_schema``
    400 (or an exhausted-retry 5xx) is actionable, instead of a bare
    ``httpx.HTTPStatusError`` crashing the meeting.
    """

    return (
        f"Featherless chat-completions POST failed: HTTP {status_code} "
        f"(model={model!r}): {body_text[:_ERROR_MESSAGE_CHARS]}"
    )


async def _send_with_retry(
    poster: Callable[[], Awaitable[_HttpResponse]],
    *,
    model: str,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    max_attempts: int = _MAX_SEND_ATTEMPTS,
    backoff_base: float = _SEND_BACKOFF_BASE_S,
    retryable_exc: tuple[type[BaseException], ...] = (json.JSONDecodeError,),
) -> Any:
    """Call ``poster`` with bounded exponential backoff on transient failures.

    Returns the parsed JSON body on a 2xx. Retries up to ``max_attempts`` on the
    transient families a hosted, flat-rate endpoint produces under load:

    * a :data:`_RETRYABLE_STATUS` response (rate-limit + 5xx, e.g. Featherless's
      "model is busy" 500 or a 504 gateway timeout);
    * a ``retryable_exc`` raised while sending/parsing — by default a truncated
      2xx body that fails JSON parsing (``json.JSONDecodeError`` out of
      ``response.json()``); :func:`_default_send` also passes
      ``httpx.TransportError`` so a dropped / half-read connection
      (``RemoteProtocolError`` "incomplete chunked read"), a read/connect
      timeout, etc. retry too.

    The exception families are the SAME transient class as a 5xx and are retried
    at the CALL level (Task 17.9): before this, a single mid-stream truncation on
    ANY of a game's ~25 sequential meeting calls propagated out and either
    crashed the whole game (a wasted re-record) or forced a validation-default
    phantom row, which made recording against an intermittently-impaired
    Featherless impractical. A non-retryable status (e.g. a permanent 400 for an
    unsupported ``json_schema`` request) raises immediately — no silent fallback
    (AGENTS.md). On exhaustion the last status/body — or the last transport/parse
    error — is surfaced. ``sleep`` is injectable so the loop is unit-testable
    without real delay; ``retryable_exc`` is injectable so the fake-poster tests
    exercise it without importing the transport library.
    """

    last_status = 0
    last_text = ""
    last_exc: BaseException | None = None
    for attempt in range(max_attempts):
        try:
            response = await poster()
            if 200 <= response.status_code < 300:
                return response.json()
            last_status = response.status_code
            last_text = response.text
            last_exc = None
            retryable = response.status_code in _RETRYABLE_STATUS
        except retryable_exc as exc:
            last_exc = exc
            last_status = 0
            last_text = ""
            retryable = True
        if retryable and attempt < max_attempts - 1:
            await sleep(backoff_base * (2**attempt))
            continue
        break
    if last_exc is not None:
        raise RuntimeError(
            f"Featherless chat-completions POST failed after {max_attempts} "
            f"attempt(s) on a transport/parse error (model={model!r}): "
            f"{type(last_exc).__name__}: {str(last_exc)[:_ERROR_MESSAGE_CHARS]}"
        ) from last_exc
    raise RuntimeError(_format_send_error(last_status, last_text, model))


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

    payload = _build_chat_payload(
        model=model,
        prompt=prompt,
        response_format=response_format,
        max_tokens=max_tokens,
        temperature=temperature,
        request_thinking=request_thinking,
    )
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}

    # A fresh client per call (closed via the async context manager) keeps the
    # module-level send-hook stateless — there is no FeatherlessClient instance
    # on which to hang a pooled client without introducing module-level state
    # (which the design forbids), mirroring the Ollama / Anthropic adapters.
    async with httpx.AsyncClient() as client:

        async def _post() -> httpx.Response:
            return await client.post(
                url, headers=headers, json=payload, timeout=httpx.Timeout(600.0)
            )

        # Bounded retry on transient 5xx / rate-limit AND on transport failures
        # (a dropped/half-read connection, a read/connect timeout — all
        # httpx.TransportError subclasses) plus a truncated 2xx body that fails
        # JSON parse; a permanent 4xx (e.g. an unsupported json_schema request)
        # fails loud with a descriptive error rather than a raw httpx exception.
        # The call-level transport retry (Task 17.9) keeps a single mid-stream
        # truncation from crashing a whole game against a flaky hosted endpoint.
        body = await _send_with_retry(
            _post,
            model=model,
            retryable_exc=(httpx.TransportError, json.JSONDecodeError),
        )

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
    "DEFAULT_RESPONSE_FORMAT_MODE",
    "DEFAULT_THINKING_POLICY",
    "FeatherlessClient",
    "FeatherlessRawResponse",
    "FeatherlessSendHook",
    "ResponseFormatMode",
    "ThinkingPolicy",
]
