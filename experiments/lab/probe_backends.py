"""Provider-neutral probe backend (Task 14.3) — one seam, two providers.

The real-data probes (``experiments/model_probe/probe.py``,
``experiments/lab/deception_battery.py``, ``experiments/lab/deflection_probe.py``,
``experiments/lab/model_ceiling_probe.py``) reconstruct hard decision contexts
from the committed ``replays/samples/9p2i`` set and call the model through one
tiny seam that historically hit :func:`llm.ollama_client._default_send` then
:func:`llm.provider._extract_json_block` + ``model_validate_json``. This module
factors that seam into a single provider-neutral :func:`call_turn` so the
IDENTICAL reconstructed contexts can flow to either backend:

* ``ollama`` (default) — preserves CI and the existing committed
  ``results-*.jsonl``: the wire call to :func:`llm.ollama_client._default_send`
  is byte-identical to the historical probe calls (same
  ``format=schema.model_json_schema()``, same ``options``, same ``think``), so a
  re-run reproduces the same deterministic decision data (seed 0, the recorded
  temperature).
* ``featherless`` — routes the same prompt to Task 14.1's
  :func:`llm.featherless_client._default_send` (an OpenAI-compatible hosted
  endpoint), so Task 14.4 can sweep the Featherless model slate over the same
  corpora. Threads BOTH the request-time thinking toggle (``request_thinking`` —
  the non-thinking/thinking sweep axis) and the response-side
  :data:`~llm.featherless_client.ThinkingPolicy` (default ``strip`` here so a
  reasoning model does not abort the sweep), reusing the adapter's own
  reasoning-detection / strip helpers so the policy stays in lock-step with the
  production client.

Both backends route the response through the SAME production
:func:`llm.provider._extract_json_block` + ``schema.model_validate_json`` path,
so parse fidelity matches the live sim. :func:`call_turn` returns a
:class:`CallResult` carrying the contracted ``(parsed_or_None, raw_text,
latency)`` plus the token / thinking-channel provenance the vote probe records
and the active ``substrate_flags`` config (see :func:`active_substrate_flags`).

This module is READ-ONLY over the committed replays — it reconstructs contexts
and calls models, it never mutates the engine, agents, or recorded bytes. The
13.5 substrate-flag logic is consumed (via the four ``*_enabled()`` resolvers)
but never modified: the sweep toggles the four ``AILIBI_*`` env vars to build
flag-OFF vs flag-ON contexts, and :func:`call_turn` records which config was
active on each result row.

No network import at module load: the real ``httpx`` / ``ollama`` transports are
imported lazily inside each provider's ``_default_send``, and unit tests inject
those module-level send hooks (``_ollama_send`` / ``_featherless_send``) so the
dispatch + parse path is exercised with no network call.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, Generic, Literal, TypeVar

from pydantic import BaseModel, ValidationError

from agents.memory.store import testimony_as_content_enabled
from llm.featherless_client import (
    DEFAULT_FEATHERLESS_BASE_URL,
    DEFAULT_RESPONSE_FORMAT_MODE,
    ResponseFormatMode,
    ThinkingPolicy,
    _detect_reasoning,
    _strip_reasoning_segment,
)
from llm.featherless_client import _default_send as _featherless_send
from llm.ollama_client import _default_send as _ollama_send
from llm.provider import _extract_json_block
from meetings.transcript import witnessed_kill_evidence_enabled
from observation.service import movement_perception_enabled
from orchestrator.game import unfreeze_memory_enabled

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

# The two providers the probe seam can dispatch to. ``ollama`` is the default so
# CI and the committed ``results-*.jsonl`` are unaffected; ``featherless`` is the
# Phase-14 hosted backend (Task 14.1).
Backend = Literal["ollama", "featherless"]

# Bound the parsed-schema type so :func:`call_turn` returns the caller's concrete
# model (``VoteBallot`` for the vote probe, ``MeetingTurn`` for the deception /
# ceiling probes) rather than a bare ``BaseModel``.
ModelT = TypeVar("ModelT", bound=BaseModel)

# Ollama wire defaults matching the historical probe calls so the ``ollama``
# branch stays byte-identical (the committed probes used seed 0 and an 8192
# context). ``AILIBI_OLLAMA_HOST`` mirrors
# :func:`experiments.model_probe.probe._ollama_host`.
_ENV_OLLAMA_HOST: Final[str] = "AILIBI_OLLAMA_HOST"
_DEFAULT_OLLAMA_HOST: Final[str] = "localhost:11434"
DEFAULT_OLLAMA_SEED: Final[int] = 0
DEFAULT_OLLAMA_NUM_CTX: Final[int] = 8192

# Probe-harness response-side default: the 14.4 sweep evaluates reasoning models,
# so the default policy here is ``strip`` (discard reasoning explicitly, logged),
# NOT the production client's ``fail_loud`` — a reasoning model must not abort the
# sweep. ``fail_loud`` stays selectable for a non-thinking integrity pass.
DEFAULT_PROBE_THINKING_POLICY: Final[ThinkingPolicy] = "strip"


def _resolve_ollama_host(env: Mapping[str, str] | None = None) -> str:
    """Resolve the Ollama host the same way the vote probe does (env-overridable)."""

    environment = env if env is not None else os.environ
    return environment.get(_ENV_OLLAMA_HOST, _DEFAULT_OLLAMA_HOST)


def active_substrate_flags(env: Mapping[str, str] | None = None) -> dict[str, bool]:
    """Snapshot the four merged 13.5 substrate levers for result-row provenance.

    Reads the four ``*_enabled()`` resolvers (each consulting its ``AILIBI_*``
    env var, default OFF) WITHOUT modifying the flag logic. The sweep toggles
    these env vars to reconstruct flag-OFF vs flag-ON contexts; tagging the
    active config on each result row makes the two-column (flag-OFF / flag-ON)
    sweep rows self-describing. ``env`` is threaded through so a caller can
    snapshot a specific mapping deterministically (tests, an explicit sweep
    config) instead of the live process environment.
    """

    return {
        "testimony_as_content": testimony_as_content_enabled(env),
        "witnessed_kill_evidence": witnessed_kill_evidence_enabled(env),
        "movement_perception": movement_perception_enabled(env),
        "unfreeze_memory": unfreeze_memory_enabled(env),
    }


@dataclass(frozen=True)
class CallResult(Generic[ModelT]):
    """Outcome of one provider-neutral turn call.

    Carries the contracted ``(parsed, raw_text, latency_s)`` triple plus the
    provenance the vote probe records (token counts, thinking-channel size) and
    the active ``substrate_flags`` config. ``parsed`` is ``None`` when the model
    output failed ``schema.model_validate_json`` after extraction, with the
    validation error preserved in ``parse_error`` so the probe can record the
    same diagnostic string the historical inline path did.
    """

    parsed: ModelT | None
    raw_text: str
    latency_s: float
    in_tokens: int
    out_tokens: int
    thinking_chars: int
    substrate_flags: dict[str, bool]
    parse_error: str | None = None


def _featherless_response_format(
    schema: type[BaseModel] | None, mode: ResponseFormatMode
) -> dict[str, Any] | None:
    """Build the Featherless ``response_format`` for ``schema`` per ``mode``.

    Mirrors :meth:`llm.featherless_client.FeatherlessClient._response_format_for`
    (the probe seam bypasses ``complete`` to capture raw text + latency, so the
    tiny wire-shape builder is reproduced here): ``None`` for a free-text call or
    ``none`` mode, ``{"type":"json_object"}`` for the supported default, and the
    strict ``json_schema`` grammar (an explicit opt-in the current slate rejects)
    otherwise. No silent fallback between modes.
    """

    if schema is None or mode == "none":
        return None
    if mode == "json_object":
        return {"type": "json_object"}
    return {
        "type": "json_schema",
        "json_schema": {
            "name": schema.__name__,
            "schema": schema.model_json_schema(),
            "strict": True,
        },
    }


def _parse(schema: type[ModelT], text: str) -> tuple[ModelT | None, str | None]:
    """Run the shared extract → validate path; return ``(parsed, parse_error)``."""

    extracted = _extract_json_block(text, schema)
    try:
        return schema.model_validate_json(extracted), None
    except ValidationError as exc:
        return None, str(exc)


async def call_turn(
    prompt: str,
    schema: type[ModelT],
    *,
    backend: Backend = "ollama",
    model: str,
    temperature: float,
    max_tokens: int,
    # ── Ollama wire knobs (kept byte-identical to the historical probe calls) ──
    ollama_host: str | None = None,
    seed: int = DEFAULT_OLLAMA_SEED,
    num_ctx: int = DEFAULT_OLLAMA_NUM_CTX,
    think: bool = False,
    # ── Featherless wire knobs (Task 14.1 adapter) ──
    api_key: str | None = None,
    base_url: str = DEFAULT_FEATHERLESS_BASE_URL,
    request_thinking: bool = False,
    thinking_policy: ThinkingPolicy = DEFAULT_PROBE_THINKING_POLICY,
    response_format_mode: ResponseFormatMode = DEFAULT_RESPONSE_FORMAT_MODE,
    # ── Provenance ──
    substrate_flags: Mapping[str, bool] | None = None,
) -> CallResult[ModelT]:
    """Route ``prompt`` to ``backend`` and parse via the production seam.

    Dispatches to the ollama or featherless ``_default_send`` and routes the
    response through the shared :func:`llm.provider._extract_json_block` +
    ``schema.model_validate_json`` path. ``latency_s`` measures the send only
    (parsing is deterministic and cheap), matching the historical probe timing.

    The ``ollama`` branch reproduces the historical wire call exactly (same
    ``format_schema``, ``options``, and top-level ``think``) so committed
    ``results-*.jsonl`` reproduce. The ``featherless`` branch threads BOTH the
    request-time ``request_thinking`` toggle (the 14.4 sweep axis) and the
    response-side ``thinking_policy`` (default ``strip``): a populated reasoning
    channel / inline ``<think>`` block is detected by the adapter's own
    :func:`~llm.featherless_client._detect_reasoning` before extraction, then
    either raised on (``fail_loud``) or excised (``strip``, logged) — never
    silently accepted.

    ``substrate_flags`` defaults to a live :func:`active_substrate_flags`
    snapshot when not supplied, so each result row self-describes which 13.5
    substrate config reconstructed its context.
    """

    flags = (
        dict(substrate_flags)
        if substrate_flags is not None
        else active_substrate_flags()
    )

    if backend == "ollama":
        started = time.perf_counter()
        raw = await _ollama_send(
            host=ollama_host if ollama_host is not None else _resolve_ollama_host(),
            model=model,
            prompt=prompt,
            format_schema=schema.model_json_schema(),
            options={
                "temperature": temperature,
                "seed": seed,
                "num_predict": max_tokens,
                "num_ctx": num_ctx,
            },
            think=think,
        )
        latency_s = time.perf_counter() - started
        parsed, parse_error = _parse(schema, raw.text)
        return CallResult(
            parsed=parsed,
            raw_text=raw.text,
            latency_s=latency_s,
            in_tokens=raw.prompt_eval_count,
            out_tokens=raw.eval_count,
            thinking_chars=len(raw.thinking),
            substrate_flags=flags,
            parse_error=parse_error,
        )

    if backend == "featherless":
        if not api_key:
            raise ValueError(
                "call_turn(backend='featherless') requires a non-empty api_key "
                "(set FEATHERLESS_API_KEY for the sweep)."
            )
        response_format = _featherless_response_format(schema, response_format_mode)
        started = time.perf_counter()
        raw_f = await _featherless_send(
            base_url=base_url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            response_format=response_format,
            max_tokens=max_tokens,
            temperature=temperature,
            request_thinking=request_thinking,
        )
        latency_s = time.perf_counter() - started
        # Response-side thinking policy on the RAW content BEFORE extraction:
        # the shared extractor strips a prose preamble and returns the first
        # valid JSON object, so reasoning must be handled here or ``fail_loud``
        # silently degrades to ``strip`` (a no-silent-fallbacks violation). Reuse
        # the adapter's own helpers so the probe stays in lock-step with the
        # production client.
        reasoning = _detect_reasoning(raw_f.text, raw_f.reasoning_content, schema)
        content = raw_f.text
        if reasoning is not None:
            if thinking_policy == "fail_loud":
                raise RuntimeError(
                    "Featherless returned reasoning under thinking_policy="
                    f"'fail_loud' (model={raw_f.model!r}): {reasoning}. Set "
                    "request_thinking=False to suppress reasoning, or "
                    "thinking_policy='strip' to discard it explicitly for the "
                    "model sweep."
                )
            content = _strip_reasoning_segment(content)
            _LOGGER.warning(
                "call_turn discarding reasoning under thinking_policy='strip' "
                "(model=%r): %s",
                raw_f.model,
                reasoning,
            )
        parsed, parse_error = _parse(schema, content)
        # Count thinking pollution from BOTH channels: the dedicated
        # ``reasoning_content`` side-channel AND any inline ``<think>...</think>``
        # block the ``strip`` path excised (``len(text) - len(content)``). Inline
        # tags are exactly how Qwen-style models surface reasoning, so omitting
        # them would under-report ``thinking_chars`` for the reasoning-model sweep
        # cases that use them — making the comparison against Ollama's
        # ``thinking_chars`` and side-channel models misleading.
        stripped_inline = len(raw_f.text) - len(content)
        return CallResult(
            parsed=parsed,
            raw_text=raw_f.text,
            latency_s=latency_s,
            in_tokens=raw_f.prompt_tokens,
            out_tokens=raw_f.completion_tokens,
            thinking_chars=len(raw_f.reasoning_content) + stripped_inline,
            substrate_flags=flags,
            parse_error=parse_error,
        )

    # Unreachable under `mypy --strict` (``Backend`` is a ``Literal``), but
    # AGENTS.md mandates no silent fallbacks even for type-guarded branches.
    raise ValueError(f"unknown backend: {backend!r}")


__all__ = [
    "Backend",
    "CallResult",
    "DEFAULT_OLLAMA_NUM_CTX",
    "DEFAULT_OLLAMA_SEED",
    "DEFAULT_PROBE_THINKING_POLICY",
    "active_substrate_flags",
    "call_turn",
]
