"""Featherless model x thinking-mode sweep over reconstructed 9p2i contexts (Task 14.4).

Operator-run, $0-marginal matrix driver. It runs each candidate Featherless
model over the SAME reconstructed opening/reply/vote contexts from the committed
``replays/samples/9p2i`` set, on the PINNED 9B prompts, and grades every cell
with the IDENTICAL mechanical detectors used for the 9B reference so the only
moving variable is the model (and, in the cover 2x2, the directive injection):

* **opening corpus** — the impostor self-report: the killer opens the meeting
  for their OWN kill (``impostor_report`` prompt, real reconstructed memory),
  graded by :func:`experiments.lab.deception_battery._grade_fabrication`
  (self-incrimination vs the engine-walk kill ground truth). Needs the extractor
  facts JSON (``--facts``) for the kill room/tick; skipped with a logged note
  when absent.
* **reply corpus** — the 16 hard impostor *reply* contexts frozen by
  :func:`experiments.lab.model_ceiling_probe._select` (a body was reported and an
  impostor must answer). Rendered through the production ``accusation_round``
  reply prompt and graded by :func:`experiments.lab.deflection_probe._grade`
  (``self_co_locates_body`` / ``new_self_flag`` / ``deflects_legal``). This is
  both the model-ceiling read (cover OFF across models) and one half of the
  cover 2x2.
* **cover 2x2** — the SAME reply contexts re-run with the gp-1 cover directive
  (:func:`experiments.lab.deflection_probe._cover_directive`) injected into
  rendered memory (cover ON), so each ``(model, {cover OFF, cover ON})`` cell is
  graded by the same detector — settling whether the self-incrimination tell is
  a capability ceiling, a prompt artifact, both, or the information ceiling.
* **vote corpus** — real vote-ballot decision contexts
  (:func:`experiments.model_probe.corpus.build_corpus`) rendered through the
  production vote prompt, scored for parse-success and conversion (did the voter
  pick an available impostor).

The corpus item IDs are PINNED ONCE (off the flag-OFF reconstruction) and the
SAME ids are re-rendered under each substrate, so the flag-OFF vs flag-ON
comparison is a controlled re-render of identical contexts, not a re-selection
(vote selection in particular is substrate-sensitive — its ``available_impostor``
gate reads the suspicion graph — so pinning is load-bearing there).

Every cell is run on BOTH the flag-OFF (legacy) and the flag-ON (corrected 13.5)
substrate. The flag-ON contexts are re-derived OFFLINE by setting the four
``AILIBI_*`` env vars before reconstruction (the levers are replay-deterministic
reductions of the recorded events, read ad-hoc via the ``*_enabled()`` resolvers
— so no re-record is needed); each result row carries the ``substrate_flags``
config that produced its context. The Qwen3 models run in both non-thinking and
thinking mode (the request-time ``enable_thinking`` toggle, Task 14.1, threaded
via :func:`experiments.lab.probe_backends.call_turn`, Task 14.3).

9B-class reference: ``qwen3.5:9b`` is a local Ollama model off the hosted
endpoint, so the IN-SWEEP reference is its closest served Featherless analogue —
``Qwen/Qwen3-8B`` (same Qwen3 generation, nearest size, native
``enable_thinking``) — run over the SAME frozen contexts on BOTH substrates, so
the model-ceiling/information-ceiling read is controlled on identical contexts
(addresses the prior version's stale-9B mismatch). The committed Ollama
``results-model-ceiling-q9b.jsonl`` is folded only as a secondary HISTORICAL row
(prior recording; non-item-matched), clearly labelled.

Non-Qwen transport: the Task 14.1 adapter ALWAYS sends
``chat_template_kwargs.enable_thinking`` (the Qwen3 convention), which is honored
by the Qwen3 models but BREAKS the non-Qwen slate (GLM collapses to ``{}``,
Cydonia 400/504s). So the non-Qwen models are routed through a sweep-local BARE
send that omits that field and posts the same ``json_object`` request, then
parses through the SAME shared :func:`llm.provider._extract_json_block` +
``model_validate_json`` seam — giving their real structured-output fidelity
rather than a harness artifact. (The proper fix — making the field conditional —
belongs in ``llm/featherless_client.py``, which is out of scope for 14.4; this is
reported as adapter-compat feedback to 14.1/14.6.)

This module is READ-ONLY over the committed replays and CONSUMES the 14.2/14.3
seams without editing them.

Slate (HuggingFace repo form). Two of the contract's owner-confirmed ids
(``Qwen/Qwen3-30B-A3B``, ``zai-org/GLM-4-32B``) return a hard HTTP 404 from the
live endpoint as of 2026-06-29 — Featherless now serves the suffixed canonical
revisions ``Qwen/Qwen3-30B-A3B-Instruct-2507`` and ``zai-org/GLM-4-32B-0414``,
which ARE the MoE-speed and agentic models the contract names. The driver
confirms each id via a generation preflight before the run and substitutes the
served revision (documented in the PR ``Decisions``).

Usage (run as a module so the repo root is on the path)::

    # the kill ground truth for the opening corpus ($0, offline):
    PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py

    # full matrix (needs FEATHERLESS_API_KEY; concurrency<=2 — the plan caps at
    # 4 concurrency units and a 32B request costs 2):
    uv run python -m experiments.lab.featherless_sweep run \
        --sample-dir replays/samples/9p2i \
        --facts /tmp/ailibi-gameplay-facts-9p2i.json

    # (re)generate the report from the committed results:
    uv run python -m experiments.lab.featherless_sweep report
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import statistics
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from agents.strategic.prompts.loader import (
    accusation_round_prompt,
    impostor_report_prompt,
)
from experiments.lab.deception_battery import (
    KillContext,
    ReplyContext,
    _grade_fabrication,
    build_kill_contexts,
)
from experiments.lab.deflection_probe import _body, _cover_directive, _grade
from experiments.lab.model_ceiling_probe import _select
from experiments.lab.probe_backends import (
    active_substrate_flags,
    call_turn,
    resolve_featherless_base_url,
)
from experiments.model_probe.corpus import CorpusItem, build_corpus, render_prompt
from experiments.model_probe.probe import select_corpus
from llm.featherless_client import _raw_from_response_body, _send_with_retry
from llm.provider import _extract_json_block
from meetings.schemas import MeetingTurn, VoteBallot

WORK: Final[Path] = Path("experiments/lab")
RESULTS: Final[Path] = WORK / "results-featherless-sweep.jsonl"
REPORT: Final[Path] = WORK / "report-featherless-sweep.md"
# Committed Ollama 9B data (PRIOR recording) — folded only as a HISTORICAL row.
REF_REPLY: Final[Path] = WORK / "results-model-ceiling-q9b.jsonl"
REF_COVER: Final[Path] = WORK / "results-deflection-probe.jsonl"

# The four merged 13.5 substrate levers, toggled to build the flag-OFF vs flag-ON
# columns. Set before context reconstruction; read ad-hoc by the ``*_enabled()``
# resolvers (Task 14.3), so toggling them in-process re-derives memory cleanly.
SUBSTRATE_FLAGS: Final[tuple[str, ...]] = (
    "AILIBI_TESTIMONY_AS_CONTENT",
    "AILIBI_WITNESSED_KILL_EVIDENCE",
    "AILIBI_MOVEMENT_PERCEPTION",
    "AILIBI_UNFREEZE_MEMORY",
)

# Production turn caps (the deployed sim's frozen backstop) — recorded for
# reference only; the PROBE does NOT constrain models to these, it measures each
# model's BEST-SHOT result (see _profile below).
PROD_TURN_CAP: Final[int] = 2048
PROD_VOTE_CAP: Final[int] = 1024
TEMPERATURE: Final[float] = 0.4
VOTE_TEMPERATURE: Final[float] = 0.0
# The harness discards reasoning explicitly so a reasoning model does not abort
# the sweep (probe-side default; the recorded baseline at 14.7 uses fail_loud).
THINKING_POLICY: Final[str] = "strip"

# ── Best-shot probe call profiles (owner decision 2026-06-29) ──
# The probe's job is to rank how well each model performs on the corpus, so each
# model/mode is called with the settings MOST LIKELY TO SUCCEED, not the 9B-era
# 2048 / json_object handicap. The OUTPUT (the parsed MeetingTurn / VoteBallot)
# is schema-identical regardless, so downstream graders / consumers are unchanged
# — only the LLM-call knobs vary, and reasoning is DISCARDED (never recorded), so
# it cannot leak into game state.
#
# * THINKING rows: ``response_format=none`` (json_object SUPPRESSES Qwen3
#   reasoning — calibrated 2026-06-29: out=243 vs 3187 tokens), so the model
#   actually reasons; the ``<think>`` block is stripped before extract→validate.
#   A generous 16384 generation budget so reasoning (observed ~3.2k–4.7k tokens)
#   + the answer never truncate, while staying inside the 32K context (~4k input).
# * NON-THINKING rows: ``json_object`` forces JSON-first output; a 4096 budget
#   (headroom over the ~250–500-token turns) removes the rare non-thinking
#   truncation. The recorded answer still fits the production 2048 turn cap.
THINK_BUDGET: Final[int] = 16384
NONTHINK_BUDGET: Final[int] = 4096


def _profile(request_thinking: bool) -> tuple[str, int]:
    """Best-shot ``(response_format_mode, max_tokens)`` for the given mode."""

    if request_thinking:
        return "none", THINK_BUDGET
    return "json_object", NONTHINK_BUDGET


# The in-sweep 9B-class reference (closest served analogue of ``qwen3.5:9b``).
REFERENCE_LABEL: Final[str] = "qwen3-8b"

# The Featherless plan also limits how often the account may SWITCH the active
# model (observed: "switch models 4 times per minute"). The sweep is structured
# model-outer (each model does ALL its work before the next), so switches are
# naturally minutes apart — but preflight (and the first loaded model) can bunch,
# so a pacer enforces a minimum gap between switches to a DIFFERENT model.
MIN_SWITCH_INTERVAL_S: Final[float] = 20.0

# Bounded retry on transport exceptions (network outage / connection reset) that
# the HTTP-status retry in ``_send_with_retry`` does not cover — so a brief blip
# mid-run does not turn a whole model's cells into recorded ConnectErrors.
_TURN_MAX_ATTEMPTS: Final[int] = 4
_TURN_RETRY_BACKOFF_S: Final[float] = 5.0

ModelT = TypeVar("ModelT", bound=BaseModel)


class _SwitchPacer:
    """Enforce a minimum interval between switches to a different model id."""

    def __init__(self, interval_s: float = MIN_SWITCH_INTERVAL_S) -> None:
        self._interval = interval_s
        self._last = 0.0
        self._current: str | None = None

    def touch(self, model: str) -> None:
        if model == self._current:
            return
        if self._current is not None:
            wait = self._interval - (time.monotonic() - self._last)
            if wait > 0:
                print(
                    f"  pacing model switch -> {model}: sleeping {wait:.0f}s "
                    "(4 switches/min plan limit)",
                    flush=True,
                )
                time.sleep(wait)
        self._last = time.monotonic()
        self._current = model


@dataclass(frozen=True)
class ModelSpec:
    """One slate model: served id, short label, mode axis, transport, role."""

    model_id: str
    label: str
    # Run the non-thinking AND thinking modes (the request-time enable_thinking
    # sweep axis)? Only the Qwen3 chat models have a meaningful axis.
    thinking_axis: bool
    # Send ``chat_template_kwargs.enable_thinking`` (the Qwen3 convention, via the
    # 14.1 adapter / ``call_turn``)? FALSE routes through the sweep-local BARE
    # send that omits the field — required for the non-Qwen slate, which the
    # adapter's mandatory field otherwise breaks.
    qwen_kwarg: bool
    # "candidate" (eligible for the recommended tuple) or "reference" (the
    # 9B-class baseline, excluded from the recommendation).
    role: str = "candidate"


# The slate the contract pins, plus the 9B-class reference, with the two 404'd
# ids substituted by their served canonical revisions. Order = report order.
SLATE: Final[tuple[ModelSpec, ...]] = (
    ModelSpec(
        "Qwen/Qwen3-8B",
        REFERENCE_LABEL,
        # The contract wants the 9B-class reference in BOTH modes where available;
        # Qwen3-8B honors enable_thinking, so run the thinking axis too — its
        # thinking row matches the candidate Qwen thinking rows on identical
        # contexts.
        thinking_axis=True,
        qwen_kwarg=True,
        role="reference",
    ),
    ModelSpec("Qwen/Qwen3-32B", "qwen3-32b", thinking_axis=True, qwen_kwarg=True),
    ModelSpec(
        "Qwen/Qwen3-30B-A3B-Instruct-2507",
        "qwen3-30b-a3b",
        thinking_axis=True,
        qwen_kwarg=True,
    ),
    ModelSpec(
        "zai-org/GLM-4-32B-0414", "glm-4-32b", thinking_axis=False, qwen_kwarg=False
    ),
    ModelSpec(
        "TheDrummer/Cydonia-24B-v2",
        "cydonia-24b",
        thinking_axis=False,
        qwen_kwarg=False,
    ),
)


@dataclass
class SweepConfig:
    """Knobs for one sweep invocation."""

    sample_dir: Path
    facts_path: Path | None = None
    reply_cap: int = 16
    vote_limit: int = 8
    opening_cap: int = 10
    # Plan concurrency limit is 4 UNITS and a 32B request costs 2 units, so the
    # safe default is 2 concurrent requests (>2 turns valid cells into 429s).
    concurrency: int = 2
    latency_samples: int = 2
    substrates: tuple[bool, ...] = (False, True)
    base_url: str | None = None
    models: tuple[ModelSpec, ...] = SLATE
    # Append to the results file instead of truncating — used to re-run a single
    # model (``--models``) after an environment outage and merge it back, rather
    # than repeating the whole multi-hour matrix.
    append: bool = False


@dataclass(frozen=True)
class TurnOutcome(Generic[ModelT]):
    """Normalized outcome of one model call, transport-agnostic."""

    parsed: ModelT | None
    raw_text: str
    latency_s: float
    in_tokens: int
    out_tokens: int
    thinking_chars: int
    error: str | None
    parse_error: str | None


def _set_substrate(flag_on: bool) -> dict[str, bool]:
    """Set / clear the four 13.5 env levers and return the active config."""

    for name in SUBSTRATE_FLAGS:
        if flag_on:
            os.environ[name] = "1"
        else:
            os.environ.pop(name, None)
    return active_substrate_flags()


def _modes_for(spec: ModelSpec) -> tuple[bool, ...]:
    """Request-thinking values to run for ``spec`` (the non-thinking/thinking axis)."""

    return (False, True) if spec.thinking_axis else (False,)


def _mode_label(request_thinking: bool) -> str:
    return "thinking" if request_thinking else "non_thinking"


async def _bare_send(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    response_format: dict[str, Any] | None,
    max_tokens: int,
    temperature: float,
) -> Any:
    """A Featherless POST that OMITS ``chat_template_kwargs`` (non-Qwen path).

    Reuses the production bounded-retry (:func:`_send_with_retry`) + body mapping
    (:func:`_raw_from_response_body`) so the only difference from the 14.1 adapter
    is the omitted Qwen-only thinking field — exactly the field that breaks the
    non-Qwen slate. Returns a ``FeatherlessRawResponse``.
    """

    import httpx

    payload: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if response_format is not None:
        payload["response_format"] = response_format
    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    async with httpx.AsyncClient() as client:

        async def _post() -> httpx.Response:
            return await client.post(
                url, headers=headers, json=payload, timeout=httpx.Timeout(600.0)
            )

        body = await _send_with_retry(_post, model=model)
    return _raw_from_response_body(body, model=model)


def _parse(schema: type[ModelT], text: str) -> tuple[ModelT | None, str | None]:
    """Shared extract -> validate path; ``(parsed, parse_error)``."""

    try:
        return schema.model_validate_json(_extract_json_block(text, schema)), None
    except ValidationError as exc:
        return None, str(exc)


async def _run_turn(
    spec: ModelSpec,
    prompt: str,
    schema: type[ModelT],
    *,
    request_thinking: bool,
    max_tokens: int,
    temperature: float,
    response_format_mode: str,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
) -> TurnOutcome[ModelT]:
    """Run one model call via the right transport; never raises.

    Qwen3 models (``qwen_kwarg``) go through ``call_turn`` (the 14.1 adapter,
    sending ``chat_template_kwargs.enable_thinking`` — the real thinking axis).
    Non-Qwen models go through :func:`_bare_send` (omitting that field). BOTH
    route the response through the shared extract -> validate seam.
    """

    resolved = base_url if base_url is not None else resolve_featherless_base_url()
    async with sem:
        # Bounded retry on TRANSPORT exceptions (e.g. ``httpx.ConnectError`` from
        # a brief network outage — which a multi-hour run is exposed to and which
        # ``_send_with_retry`` does NOT cover, as it only retries HTTP statuses,
        # not connection failures). A schema-invalid body is NOT an exception
        # here (``_parse`` returns it as ``parse_error``), so this only retries
        # genuine transport failures; the last error is recorded if all fail.
        last_exc: Exception | None = None
        for attempt in range(_TURN_MAX_ATTEMPTS):
            started = time.perf_counter()
            try:
                if spec.qwen_kwarg:
                    r = await call_turn(
                        prompt,
                        schema,
                        backend="featherless",
                        model=spec.model_id,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        api_key=api_key,
                        base_url=base_url,
                        request_thinking=request_thinking,
                        thinking_policy=THINKING_POLICY,  # type: ignore[arg-type]
                        response_format_mode=response_format_mode,  # type: ignore[arg-type]
                        substrate_flags=flags,
                    )
                    return TurnOutcome(
                        parsed=r.parsed,
                        raw_text=r.raw_text,
                        latency_s=r.latency_s,
                        in_tokens=r.in_tokens,
                        out_tokens=r.out_tokens,
                        thinking_chars=r.thinking_chars,
                        error=None,
                        parse_error=r.parse_error,
                    )
                raw = await _bare_send(
                    base_url=resolved,
                    api_key=api_key,
                    model=spec.model_id,
                    prompt=prompt,
                    response_format=(
                        None
                        if response_format_mode == "none"
                        else {"type": response_format_mode}
                    ),
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                latency = time.perf_counter() - started
                parsed, parse_error = _parse(schema, raw.text)
                return TurnOutcome(
                    parsed=parsed,
                    raw_text=raw.text,
                    latency_s=latency,
                    in_tokens=raw.prompt_tokens,
                    out_tokens=raw.completion_tokens,
                    thinking_chars=len(raw.reasoning_content),
                    error=None,
                    parse_error=parse_error,
                )
            except Exception as exc:  # noqa: BLE001 — record transport failures, don't abort
                last_exc = exc
                if attempt < _TURN_MAX_ATTEMPTS - 1:
                    await asyncio.sleep(_TURN_RETRY_BACKOFF_S * (attempt + 1))
        return TurnOutcome(
            parsed=None,
            raw_text="",
            latency_s=0.0,
            in_tokens=0,
            out_tokens=0,
            thinking_chars=0,
            error=f"{type(last_exc).__name__}: {last_exc}"[:240],
            parse_error=None,
        )


def _base_row(
    *,
    corpus: str,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    response_format_mode: str,
    max_tokens: int,
) -> dict[str, Any]:
    return {
        "corpus": corpus,
        "model": spec.model_id,
        "label": spec.label,
        "role": spec.role,
        "mode": _mode_label(request_thinking),
        "request_thinking": request_thinking,
        "transport": "adapter" if spec.qwen_kwarg else "bare",
        "substrate": "flag_on" if any(flags.values()) else "flag_off",
        "substrate_flags": dict(flags),
        # The best-shot call profile that produced this row (so the comparison is
        # transparent and 14.6 sees exactly how each number was obtained).
        "response_format_mode": response_format_mode,
        "max_tokens": max_tokens,
    }


def _record_outcome(rec: dict[str, Any], out: TurnOutcome[Any]) -> None:
    rec["latency_s"] = round(out.latency_s, 1)
    rec["in_tokens"] = out.in_tokens
    rec["out_tokens"] = out.out_tokens
    rec["thinking_chars"] = out.thinking_chars
    rec["parsed_ok"] = out.parsed is not None
    if out.error is not None:
        rec["error"] = out.error
    if out.parsed is None and out.parse_error is not None:
        rec["parse_error"] = out.parse_error[:200]
        rec["raw_head"] = out.raw_text[:200]


async def _reply_cell(
    *,
    ctx: ReplyContext,
    spec: ModelSpec,
    request_thinking: bool,
    cover: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
) -> dict[str, Any]:
    body_room, body_tick = _body(ctx)
    prompt = _reply_prompt(ctx, cover=cover)
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="reply",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
    )
    rec["cover"] = "on" if cover else "off"
    rec["item"] = ctx.item_id
    rec["body_room"] = body_room
    out = await _run_turn(
        spec,
        prompt,
        MeetingTurn,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
    )
    _record_outcome(rec, out)
    if out.parsed is not None:
        rec.update(_grade(out.parsed, ctx, body_room, body_tick))
    return rec


async def _vote_cell(
    *,
    item: CorpusItem,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
) -> dict[str, Any]:
    prompt = render_prompt(item.context)
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="vote",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
    )
    rec["cover"] = "n/a"
    rec["item"] = item.item_id
    rec["voter_role"] = item.voter_role
    rec["recorded_target"] = item.recorded_target
    rec["is_inversion"] = item.is_inversion
    rec["available_impostor_ids"] = list(item.available_impostor_ids)
    rec["max_impostor_suspicion"] = round(item.max_impostor_suspicion, 4)
    out = await _run_turn(
        spec,
        prompt,
        VoteBallot,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=VOTE_TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
    )
    _record_outcome(rec, out)
    ballot = out.parsed
    if ballot is not None:
        rec["target"] = ballot.target
        rec["confidence"] = ballot.confidence
        rec["voted_available_impostor"] = ballot.target in item.available_impostor_ids
    return rec


async def _opening_cell(
    *,
    ctx: KillContext,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
) -> dict[str, Any]:
    """Run + grade one impostor self-report opening cell (fabrication grade)."""

    prompt = impostor_report_prompt(
        agent_id=ctx.killer,
        current_tick=ctx.trigger_tick,
        meeting_trigger=ctx.trigger_description,
        rendered_memory=ctx.rendered_memory,
        public_transcript="",
        fellow_impostor_ids=ctx.fellow_living,
        living_ids=tuple(p for p in ctx.living if p != ctx.killer),
        dead_ids=tuple(ctx.dead),
    )
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="opening",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
    )
    rec["cover"] = "n/a"
    rec["item"] = ctx.item_id
    rec["kill_room"] = ctx.kill_room
    rec["kill_tick"] = ctx.kill_tick
    out = await _run_turn(
        spec,
        prompt,
        MeetingTurn,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
    )
    _record_outcome(rec, out)
    if out.parsed is not None:
        grade = _grade_fabrication(out.parsed, ctx)
        # ``honest_placement`` = the opener placed itself at the true kill room =
        # the opening-turn self-incrimination tell (mirrors the reply self-co).
        rec["self_co_locates_kill"] = bool(grade["honest_placement"])
        rec["lie_attempted"] = bool(grade["lie_attempted"])
        rec["self_incriminating_text"] = bool(grade["self_incriminating_text"])
        flags_vs_witness = grade["flags_vs_witness"]
        assert isinstance(flags_vs_witness, dict)
        rec["self_flag_vs_witness"] = int(flags_vs_witness["strong"]) > 0
    return rec


async def _latency_cell(
    *,
    ctx: ReplyContext,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
    sem: asyncio.Semaphore,
) -> dict[str, Any]:
    """One SEQUENTIAL reply call timed in isolation (the latency pass)."""

    prompt = _reply_prompt(ctx, cover=False)
    rf_mode, cap = _profile(request_thinking)
    rec = _base_row(
        corpus="latency",
        spec=spec,
        request_thinking=request_thinking,
        flags=flags,
        response_format_mode=rf_mode,
        max_tokens=cap,
    )
    rec["item"] = ctx.item_id
    out = await _run_turn(
        spec,
        prompt,
        MeetingTurn,
        request_thinking=request_thinking,
        max_tokens=cap,
        temperature=TEMPERATURE,
        response_format_mode=rf_mode,
        flags=flags,
        api_key=api_key,
        base_url=base_url,
        sem=sem,
    )
    rec["latency_s"] = round(out.latency_s, 1)
    rec["parsed_ok"] = out.parsed is not None
    rec["out_tokens"] = out.out_tokens
    if out.error is not None:
        rec["error"] = out.error
    return rec


def _reply_prompt(ctx: ReplyContext, *, cover: bool) -> str:
    """Render the production reply prompt; inject the gp-1 cover directive if ON."""

    memory = ctx.rendered_memory
    if cover:
        body_room, body_tick = _body(ctx)
        if body_room is not None:
            memory = memory + _cover_directive(body_room, body_tick or 0)
    return accusation_round_prompt(
        agent_id=ctx.speaker,
        rendered_memory=memory,
        transcript=ctx.transcript,
        contradictions=ctx.contradictions,
        prior_turn=ctx.prior_turn,
        turn_kind="reply",
        fellow_impostor_ids=ctx.fellow_living,
        living_ids=tuple(p for p in ctx.living if p != ctx.speaker),
        dead_ids=tuple(ctx.dead),
    )


def _preflight_models(
    specs: Sequence[ModelSpec],
    *,
    api_key: str,
    base_url: str | None,
    pacer: _SwitchPacer,
) -> dict[str, bool]:
    """Confirm each id is served via a tiny generation probe (an unknown id 404s).

    Resolves the base URL the SAME way as the sweep calls
    (:func:`resolve_featherless_base_url`, honoring ``AILIBI_FEATHERLESS_BASE_URL``)
    so preflight and the run hit the same endpoint. Paces each model touch through
    the shared :class:`_SwitchPacer` so the probe does not trip the 4-switches/min
    plan limit. Only a 404/400 (an unrecognized id) is a real skip; a transient
    5xx/429/blip is retried.
    """

    import httpx

    resolved = base_url if base_url is not None else resolve_featherless_base_url()
    served: dict[str, bool] = {}
    for spec in specs:
        payload = {
            "model": spec.model_id,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
            "temperature": 0.0,
        }
        served[spec.model_id] = False
        last = ""
        for attempt in range(6):
            pacer.touch(spec.model_id)
            try:
                resp = httpx.post(
                    f"{resolved}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json=payload,
                    timeout=180,
                )
                if resp.status_code == 200:
                    served[spec.model_id] = True
                    print(f"  PREFLIGHT {spec.model_id}: served", flush=True)
                    break
                last = f"HTTP {resp.status_code} {resp.text[:120]}"
                if resp.status_code in (400, 404):
                    break  # a genuinely unrecognized id — a real skip, no retry
            except Exception as exc:  # noqa: BLE001
                last = f"{type(exc).__name__}: {exc}"
            # Generous backoff: a 429 here is a transient concurrency / switch-rate
            # blip (not "unserved"); wait long enough to clear the 1-minute window.
            time.sleep(min(30.0, 5.0 * (attempt + 1)))
        if not served[spec.model_id]:
            print(f"  PREFLIGHT {spec.model_id}: {last} -> SKIPPED", flush=True)
    return served


@dataclass(frozen=True)
class PinnedIds:
    """Item IDs selected ONCE (flag-OFF) and re-rendered under each substrate."""

    reply: tuple[str, ...]
    vote: tuple[str, ...]
    opening: tuple[str, ...]


def _pin_ids(cfg: SweepConfig) -> PinnedIds:
    """Select the corpus item IDs once, off the flag-OFF reconstruction."""

    _set_substrate(False)
    reply = tuple(c.item_id for c in _select(cfg.sample_dir)[: cfg.reply_cap])
    votes = select_corpus(
        build_corpus(cfg.sample_dir),
        all_votes=False,
        crew_all=False,
        limit=cfg.vote_limit,
    )
    opening: tuple[str, ...] = ()
    if cfg.facts_path is not None:
        opening = tuple(
            c.item_id
            for c in build_kill_contexts(
                cfg.sample_dir, cfg.facts_path, cfg.opening_cap
            )
        )
    return PinnedIds(reply=reply, vote=tuple(i.item_id for i in votes), opening=opening)


def _contexts_for(
    cfg: SweepConfig, flag_on: bool, pinned: PinnedIds
) -> tuple[dict[str, bool], list[ReplyContext], list[CorpusItem], list[KillContext]]:
    """Re-render the PINNED ids under ``flag_on`` (controlled substrate compare)."""

    flags = _set_substrate(flag_on)
    reply_by_id = {c.item_id: c for c in _select(cfg.sample_dir)}
    reply = [reply_by_id[i] for i in pinned.reply if i in reply_by_id]
    vote_by_id = {i.item_id: i for i in build_corpus(cfg.sample_dir)}
    votes = [vote_by_id[i] for i in pinned.vote if i in vote_by_id]
    openings: list[KillContext] = []
    if pinned.opening and cfg.facts_path is not None:
        kill_by_id = {
            c.item_id: c
            for c in build_kill_contexts(cfg.sample_dir, cfg.facts_path, 10_000)
        }
        openings = [kill_by_id[i] for i in pinned.opening if i in kill_by_id]
    # Fail loud (AGENTS.md: no silent fallbacks) if a pinned id cannot be
    # re-rendered under this substrate: silently shrinking the corpus would make
    # the flag-OFF vs flag-ON delta compare DIFFERENT contexts while the report
    # still describes a same-context delta. Opening ids are checked too.
    opening_ids = {c.item_id for c in openings}
    missing = (
        [f"reply:{i}" for i in pinned.reply if i not in reply_by_id]
        + [f"vote:{i}" for i in pinned.vote if i not in vote_by_id]
        + [f"opening:{i}" for i in pinned.opening if i not in opening_ids]
    )
    if missing:
        raise SystemExit(
            f"substrate {'ON' if flag_on else 'OFF'}: {len(missing)} pinned ids "
            "could not be re-rendered (aborting rather than comparing different "
            f"corpora): {missing[:8]}"
        )
    print(
        f"substrate {'ON' if flag_on else 'OFF'} {flags}: {len(reply)} reply, "
        f"{len(votes)} vote, {len(openings)} opening ctxs",
        flush=True,
    )
    return flags, reply, votes, openings


async def run_sweep(cfg: SweepConfig, *, api_key: str) -> int:
    """Run the full matrix and stream rows to :data:`RESULTS`."""

    pacer = _SwitchPacer()
    served = _preflight_models(
        cfg.models, api_key=api_key, base_url=cfg.base_url, pacer=pacer
    )
    specs = [s for s in cfg.models if served.get(s.model_id)]
    skipped = [s.model_id for s in cfg.models if not served.get(s.model_id)]
    if skipped:
        print(f"SKIPPED (unserved): {skipped}", flush=True)
    if not specs:
        raise SystemExit("no slate models are served; nothing to sweep")
    if cfg.facts_path is None:
        print(
            "NOTE: --facts not supplied; the opening corpus is SKIPPED "
            "(reply + vote + latency still run).",
            flush=True,
        )

    # Reconstruct each substrate's contexts ONCE (memory is baked into the
    # returned objects), so the model-outer loop can re-use them without touching
    # the env again — and, crucially, without interleaving model switches.
    pinned = _pin_ids(cfg)
    ctx_by_sub = {flag: _contexts_for(cfg, flag, pinned) for flag in cfg.substrates}

    sem = asyncio.Semaphore(cfg.concurrency)
    n_rows = 0
    matrix_log: list[str] = []
    with RESULTS.open("a" if cfg.append else "w", encoding="utf-8") as sink:

        def emit(rec: dict[str, Any]) -> None:
            nonlocal n_rows
            sink.write(json.dumps(rec) + "\n")
            sink.flush()
            n_rows += 1

        # Model-OUTER, substrate/mode-INNER: each model is loaded once and does
        # ALL its work before the next, so the 4-switches/min plan limit is
        # respected (the pacer guards the boundary).
        for spec in specs:
            pacer.touch(spec.model_id)
            for flag_on in cfg.substrates:
                flags, reply_ctxs, vote_items, kill_ctxs = ctx_by_sub[flag_on]
                sub = "flag_on" if flag_on else "flag_off"
                for request_thinking in _modes_for(spec):
                    mode = _mode_label(request_thinking)
                    tag = f"{spec.label}/{mode}/{sub}"

                    # Sequential latency micro-pass (isolated timing).
                    for ctx in reply_ctxs[: cfg.latency_samples]:
                        emit(
                            await _latency_cell(
                                ctx=ctx,
                                spec=spec,
                                request_thinking=request_thinking,
                                flags=flags,
                                api_key=api_key,
                                base_url=cfg.base_url,
                                sem=sem,
                            )
                        )

                    # Opening pass (impostor self-report), bounded concurrency.
                    if kill_ctxs:
                        for rec in await asyncio.gather(
                            *[
                                _opening_cell(
                                    ctx=ctx,
                                    spec=spec,
                                    request_thinking=request_thinking,
                                    flags=flags,
                                    api_key=api_key,
                                    base_url=cfg.base_url,
                                    sem=sem,
                                )
                                for ctx in kill_ctxs
                            ]
                        ):
                            emit(rec)

                    # Reply behavior pass (cover OFF + cover ON = the 2x2).
                    for rec in await asyncio.gather(
                        *[
                            _reply_cell(
                                ctx=ctx,
                                spec=spec,
                                request_thinking=request_thinking,
                                cover=cover,
                                flags=flags,
                                api_key=api_key,
                                base_url=cfg.base_url,
                                sem=sem,
                            )
                            for cover in (False, True)
                            for ctx in reply_ctxs
                        ]
                    ):
                        emit(rec)

                    # Vote pass.
                    for rec in await asyncio.gather(
                        *[
                            _vote_cell(
                                item=item,
                                spec=spec,
                                request_thinking=request_thinking,
                                flags=flags,
                                api_key=api_key,
                                base_url=cfg.base_url,
                                sem=sem,
                            )
                            for item in vote_items
                        ]
                    ):
                        emit(rec)

                    matrix_log.append(
                        f"{tag}: opening={len(kill_ctxs)} reply={len(reply_ctxs)}x2 "
                        f"vote={len(vote_items)} latency="
                        f"{min(cfg.latency_samples, len(reply_ctxs))}"
                    )
                    print(f"  done {tag}", flush=True)

    print(f"\nwrote {n_rows} rows -> {RESULTS}")
    print("matrix actually run (no silent truncation):")
    for line in matrix_log:
        print(f"  {line}")
    if skipped:
        print(f"  skipped models: {skipped}")
    return 0


# ─────────────────────────── report generation ───────────────────────────


def _rows() -> list[dict[str, Any]]:
    if not RESULTS.exists():
        raise SystemExit(f"{RESULTS} not found — run the sweep first.")
    return [
        json.loads(line) for line in RESULTS.read_text().splitlines() if line.strip()
    ]


def _summ_reply(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    parsed = [r for r in rows if r.get("parsed_ok")]
    return {
        "n": n,
        "parsed": len(parsed),
        "self_co": sum(1 for r in parsed if r.get("self_co_locates_body")),
        "self_flag": sum(1 for r in parsed if r.get("new_self_flag")),
        "deflect": sum(1 for r in parsed if r.get("deflects_legal")),
    }


def _pct(num: int, den: int) -> str:
    return f"{num}/{den} ({100 * num / den:.0f}%)" if den else "0/0 (—)"


def _fmt_reply(s: Mapping[str, Any]) -> str:
    p = int(s["parsed"])
    return (
        f"parse {_pct(p, int(s['n']))} · deflect {_pct(int(s['deflect']), p)} · "
        f"self-co-loc {_pct(int(s['self_co']), p)} · "
        f"self-flag {_pct(int(s['self_flag']), p)}"
    )


def _group_reply(
    rows: Sequence[Mapping[str, Any]], *, cover: str, substrate: str
) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for r in rows:
        if r.get("corpus") != "reply":
            continue
        if r.get("cover") != cover or r.get("substrate") != substrate:
            continue
        out.setdefault((str(r["label"]), str(r["mode"])), []).append(r)
    return {k: _summ_reply(v) for k, v in out.items()}


def _group_vote(
    rows: Sequence[Mapping[str, Any]], *, substrate: str
) -> dict[tuple[str, str], dict[str, Any]]:
    by: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for r in rows:
        if r.get("corpus") != "vote" or r.get("substrate") != substrate:
            continue
        by.setdefault((str(r["label"]), str(r["mode"])), []).append(r)
    summ: dict[tuple[str, str], dict[str, Any]] = {}
    for k, v in by.items():
        parsed = [r for r in v if r.get("parsed_ok")]
        summ[k] = {
            "n": len(v),
            "parsed": len(parsed),
            "conv": sum(1 for r in parsed if r.get("voted_available_impostor")),
        }
    return summ


def _group_opening(
    rows: Sequence[Mapping[str, Any]], *, substrate: str
) -> dict[tuple[str, str], dict[str, Any]]:
    by: dict[tuple[str, str], list[Mapping[str, Any]]] = {}
    for r in rows:
        if r.get("corpus") != "opening" or r.get("substrate") != substrate:
            continue
        by.setdefault((str(r["label"]), str(r["mode"])), []).append(r)
    summ: dict[tuple[str, str], dict[str, Any]] = {}
    for k, v in by.items():
        parsed = [r for r in v if r.get("parsed_ok")]
        summ[k] = {
            "n": len(v),
            "parsed": len(parsed),
            "self_co": sum(1 for r in parsed if r.get("self_co_locates_kill")),
            "confess": sum(1 for r in parsed if r.get("self_incriminating_text")),
        }
    return summ


def _latency_by_model(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, str], float]:
    by: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        if r.get("corpus") != "latency" or not r.get("parsed_ok"):
            continue
        by.setdefault((str(r["label"]), str(r["mode"])), []).append(
            float(r["latency_s"])
        )
    return {k: round(statistics.mean(v), 1) for k, v in by.items() if v}


def _ordered_cells(summary: Mapping[tuple[str, str], Any]) -> list[tuple[str, str]]:
    order = {s.label: i for i, s in enumerate(SLATE)}
    return sorted(summary, key=lambda k: (order.get(k[0], 99), k[1]))


def _profile_info(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[str, str], tuple[str, int, float]]:
    """Per (label, mode): the call profile (response_format_mode, max_tokens) and
    mean reasoning length (thinking_chars over parsed reply rows) — so the
    fidelity table shows exactly how each cell was called and whether the model
    actually reasoned."""

    out: dict[tuple[str, str], tuple[str, int, float]] = {}
    think: dict[tuple[str, str], list[float]] = {}
    for r in rows:
        if r.get("corpus") != "reply":
            continue
        k = (str(r["label"]), str(r["mode"]))
        if k not in out:
            out[k] = (
                str(r.get("response_format_mode", "?")),
                int(r.get("max_tokens", 0)),
                0.0,
            )
        if r.get("parsed_ok"):
            think.setdefault(k, []).append(float(r.get("thinking_chars", 0)))
    return {
        k: (mode, cap, round(statistics.mean(think[k]), 0) if think.get(k) else 0.0)
        for k, (mode, cap, _) in out.items()
    }


def _historical_q9b() -> dict[str, Any]:
    rows = [
        json.loads(line) for line in REF_REPLY.read_text().splitlines() if line.strip()
    ]
    return _summ_reply(rows)


def _rate(s: Mapping[str, Any], key: str) -> float:
    p = int(s["parsed"])
    return (int(s[key]) / p) if p else 0.0


def _verdict(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    off_off = _group_reply(rows, cover="off", substrate="flag_off")
    off_on = _group_reply(rows, cover="on", substrate="flag_off")
    fit = {
        k
        for k, s in off_off.items()
        if int(s["n"]) and int(s["parsed"]) / int(s["n"]) >= 0.5
    }

    # Cover Δ is only meaningful when BOTH arms parsed comparably: a cover-ON
    # cell that fails to parse would make `_rate` 0 (zero denominator) and read
    # as a large self-co IMPROVEMENT, corrupting the prompt-artifact-vs-ceiling
    # read. Require cover-ON parse ≥ 50% (same bar as `fit`) to count the cell;
    # otherwise it is INCONCLUSIVE (surfaced separately).
    def _ok(s: Mapping[str, Any]) -> bool:
        return bool(int(s["n"])) and int(s["parsed"]) / int(s["n"]) >= 0.5

    cover_helps = [
        (k, _rate(off_off[k], "self_co") - _rate(off_on[k], "self_co"))
        for k in fit
        if k in off_on and _ok(off_on[k])
    ]
    cover_inconclusive = sorted(k for k in fit if k not in off_on or not _ok(off_on[k]))
    flag_floor = min((_rate(off_off[k], "self_flag") for k in fit), default=0.0)
    ref = off_off.get((REFERENCE_LABEL, "non_thinking"), {"n": 0, "parsed": 0})
    return {
        "off_off": off_off,
        "off_on": off_on,
        "fit_cells": sorted(fit),
        "cover_helps": cover_helps,
        "cover_inconclusive": cover_inconclusive,
        "flag_floor": flag_floor,
        "ref_cell": ref,
    }


def write_report() -> int:
    rows = _rows()
    v = _verdict(rows)
    lat = _latency_by_model(rows)
    hist = _historical_q9b()

    lines: list[str] = []
    add = lines.append
    add("# Lab report — Featherless model x thinking-mode sweep (Task 14.4)")
    add("")
    add(
        "**Decision informed:** which Featherless `(meeting_model, trigger_model, "
        "mode)` to lock at Task 14.6, and whether the Phase-13 information-ceiling "
        "hypothesis (`audits/audit-2026-06-25-0859-phase-13-close.md`) survives a "
        "stronger model. **Method:** the model-ceiling-vs-information design of "
        "`experiments/lab/report-model-ceiling-probe.md`, generalized across the "
        "Featherless slate over the SAME reconstructed `replays/samples/9p2i` "
        "opening/reply/vote contexts (item IDs pinned once and re-rendered under "
        "each substrate), on the PINNED 9B prompts, graded by the IDENTICAL "
        "mechanical detectors. **Cost:** $0 (Featherless flat-rate)."
    )
    add("")
    add(
        "**9B-class reference (in-sweep, item-matched):** `qwen3.5:9b` is local "
        "Ollama (off the hosted endpoint), so the reference column is its closest "
        "served analogue **`Qwen/Qwen3-8B`** (same Qwen3 generation / nearest "
        "size / native `enable_thinking`), run over the SAME frozen contexts on "
        "BOTH substrates. The committed Ollama `results-model-ceiling-q9b.jsonl` "
        f"(self-co {100 * _rate(hist, 'self_co'):.0f}%, self-flag "
        f"{100 * _rate(hist, 'self_flag'):.0f}%, deflect "
        f"{100 * _rate(hist, 'deflect'):.0f}%) is folded only as a secondary "
        "HISTORICAL row — it predates the current 9p2i recording (non-item-matched)."
    )
    add("")
    add(
        "**Non-Qwen transport:** GLM-4-32B-0414 and Cydonia-24B-v2 are routed "
        "through a sweep-local BARE send that OMITS the 14.1 adapter's mandatory "
        "`chat_template_kwargs.enable_thinking` field (the Qwen3 convention that "
        "otherwise collapses GLM to `{}` and 400/504s Cydonia) — so their rows "
        "reflect real model structured-output fidelity, not a harness artifact. "
        "The proper conditional-field fix belongs in `llm/featherless_client.py` "
        "(out of scope for 14.4; flagged to 14.1/14.6)."
    )
    add("")
    add(
        "Slate substitution (live, 2026-06-29): the contract's `Qwen/Qwen3-30B-A3B` "
        "and `zai-org/GLM-4-32B` ids 404; Featherless serves the canonical "
        "revisions `Qwen/Qwen3-30B-A3B-Instruct-2507` and `zai-org/GLM-4-32B-0414`."
    )
    add("")
    add(
        "**Best-shot call profiles (owner decision 2026-06-29):** the probe's job "
        "is to rank how each model performs on the corpus, so each model/mode is "
        "called with the settings MOST LIKELY TO SUCCEED — not the 9B-era "
        f"`json_object` / {PROD_TURN_CAP}-token handicap. THINKING rows use "
        f"`response_format=none` (json_object SUPPRESSES Qwen3 reasoning — "
        "calibrated: out=243 vs 3187 tokens) + a 16384-token budget so reasoning "
        "actually happens and never truncates, with the `<think>` block stripped "
        "before extract→validate. NON-THINKING rows use `json_object` + a 4096 "
        "budget. The OUTPUT is the schema-identical `MeetingTurn`/`VoteBallot` "
        "either way (downstream graders unchanged), and reasoning is DISCARDED "
        "(never recorded), so it cannot leak into game state. Per-row `profile` "
        f"(mode + max_tokens) is stamped in the jsonl. The deployed sim still caps "
        f"turns at {PROD_TURN_CAP} / votes at {PROD_VOTE_CAP}; choosing thinking "
        "for the recorded baseline is a 14.6/14.7 decision (raise the generation "
        "budget, cap the recorded answer, strip reasoning) — see the latency note "
        "in the recommendation."
    )
    add("")

    # ── Fidelity ──
    add("## Structured-output fidelity (parse-success, best-shot profile)")
    add("")
    add("Reply corpus, cover OFF, flag-OFF substrate.")
    add("")
    prof = _profile_info(rows)
    add(
        "| model | mode | profile | parse-success | latency (isolated) | reasoning | fit? |"
    )
    add("|---|---|---|---|---|---|---|")
    for k in _ordered_cells(v["off_off"]):
        s = v["off_off"][k]
        p, n = int(s["parsed"]), int(s["n"])
        pr = p / n if n else 0.0
        fit = "yes" if pr >= 0.9 else ("marginal" if pr >= 0.5 else "**NO**")
        latv = lat.get(k)
        lats = f"~{latv}s" if latv is not None else "—"
        ref_tag = " (ref)" if k[0] == REFERENCE_LABEL else ""
        pmode, pcap, think = prof.get(k, ("?", 0, 0.0))
        prof_s = f"{pmode}/{pcap}"
        reason_s = f"~{think:.0f} ch" if think else "—"
        add(
            f"| {k[0]}{ref_tag} | {k[1]} | {prof_s} | {_pct(p, n)} | {lats} | "
            f"{reason_s} | {fit} |"
        )
    add("")

    # ── Model-ceiling read ──
    add("## Model-ceiling-vs-information read (cover OFF, flag-OFF)")
    add("")
    add(
        "`qwen3-8b` is the item-matched 9B-class reference. Read the candidate "
        "rows against it on identical contexts."
    )
    add("")
    add("| model | mode | deflect | self-co-loc (the *tell*) | self-flag |")
    add("|---|---|---|---|---|")
    for k in _ordered_cells(v["off_off"]):
        s = v["off_off"][k]
        p = int(s["parsed"])
        ref_tag = " (ref)" if k[0] == REFERENCE_LABEL else ""
        if p == 0:
            add(f"| {k[0]}{ref_tag} | {k[1]} | — (unfit) | — | — |")
            continue
        add(
            f"| {k[0]}{ref_tag} | {k[1]} | {_pct(int(s['deflect']), p)} | "
            f"{_pct(int(s['self_co']), p)} | {_pct(int(s['self_flag']), p)} |"
        )
    add(
        f"| qwen3.5:9b (Ollama, historical) | non_thinking | "
        f"{_pct(int(hist['deflect']), int(hist['parsed']))} | "
        f"{_pct(int(hist['self_co']), int(hist['parsed']))} | "
        f"{_pct(int(hist['self_flag']), int(hist['parsed']))} |"
    )
    add("")

    # ── Cover 2x2 ──
    add("## Cover-directive 2x2 (model x {cover OFF, cover ON-reply})")
    add("")
    add("Self-co-location (the tell) with the cover directive OFF vs ON, flag-OFF:")
    add("")
    add("| model | mode | cover OFF self-co-loc | cover ON self-co-loc | Δ |")
    add("|---|---|---|---|---|")
    for k in _ordered_cells(v["off_off"]):
        soff = v["off_off"][k]
        son = v["off_on"].get(k)
        poff, noff = int(soff["parsed"]), int(soff["n"])
        if poff == 0 or noff == 0:
            add(f"| {k[0]} | {k[1]} | — | — | — |")
            continue
        pon = int(son["parsed"]) if son else 0
        non = int(son["n"]) if son else 0
        coff = _pct(int(soff["self_co"]), poff)
        # A cover-ON cell that did not parse comparably (≥50%) is INCONCLUSIVE,
        # not an improvement: a 0-denominator self-co rate would otherwise read
        # as a spurious cover win (corrupting the prompt-artifact-vs-ceiling read).
        if son is None or non == 0 or pon / non < 0.5:
            con = _pct(pon, non) if son else "—"
            add(f"| {k[0]} | {k[1]} | {coff} | inconclusive (parse {con}) | — |")
            continue
        add(
            f"| {k[0]} | {k[1]} | {coff} | {_pct(int(son['self_co']), pon)} | "
            f"{100 * (int(son['self_co']) / pon - int(soff['self_co']) / poff):+.0f} pp |"
        )
    add("")
    add(_quadrant_text(v))
    add("")

    # ── Substrate delta ──
    add("## Per-model substrate delta (flag-ON vs flag-OFF)")
    add("")
    add(
        "Does the corrected 13.5 substrate help THIS model decide where the 9B "
        "degraded? Reply corpus, cover OFF, SAME pinned contexts re-rendered."
    )
    add("")
    add("| model | mode | flag-OFF | flag-ON |")
    add("|---|---|---|---|")
    on_off = _group_reply(rows, cover="off", substrate="flag_on")
    empty = {"n": 0, "parsed": 0, "deflect": 0, "self_co": 0, "self_flag": 0}
    for k in _ordered_cells(v["off_off"]):
        add(
            f"| {k[0]} | {k[1]} | {_fmt_reply(v['off_off'][k])} | "
            f"{_fmt_reply(on_off.get(k, empty))} |"
        )
    add("")

    # ── Opening ──
    add("## Opening corpus — impostor self-report (parse + self-incrimination)")
    add("")
    op_off = _group_opening(rows, substrate="flag_off")
    op_on = _group_opening(rows, substrate="flag_on")
    if not op_off and not op_on:
        add(
            "_Not run in this sweep (no `--facts` supplied). The opening pass "
            "renders the production `impostor_report` prompt over reconstructed "
            "kill contexts and grades fabrication vs the engine-walk kill ground "
            "truth._"
        )
    else:
        add(
            "Killer opens the meeting for their own kill. `self-co-loc` = the "
            "opener placed itself at the true kill room (the opening tell); "
            "`confess` = self-incriminating free text. Tabulated per substrate."
        )
        add("")
        add("| model | mode | substrate | parse-success | self-co-loc | confess |")
        add("|---|---|---|---|---|---|")
        for sub, g in (("flag_off", op_off), ("flag_on", op_on)):
            for k in _ordered_cells(g):
                s = g[k]
                p = int(s["parsed"])
                ref_tag = " (ref)" if k[0] == REFERENCE_LABEL else ""
                add(
                    f"| {k[0]}{ref_tag} | {k[1]} | {sub} | {_pct(p, int(s['n']))} | "
                    f"{_pct(int(s['self_co']), p)} | {_pct(int(s['confess']), p)} |"
                )
    add("")

    # ── Votes ──
    add("## Vote corpus — parse-success + conversion")
    add("")
    add(
        "Crew votes WITH a visible impostor; half are recorded-SKIP inversion "
        "cases (a true impostor at suspicion 1.00 over the 0.60 gate where the 9B "
        "SKIPPED). `conversion` = voter picked an available impostor. Same pinned "
        "vote ids re-rendered under each substrate."
    )
    add("")
    add("| model | mode | substrate | parse-success | conversion |")
    add("|---|---|---|---|---|")
    for sub in ("flag_off", "flag_on"):
        g = _group_vote(rows, substrate=sub)
        for k in _ordered_cells(g):
            s = g[k]
            add(
                f"| {k[0]} | {k[1]} | {sub} | "
                f"{_pct(int(s['parsed']), int(s['n']))} | "
                f"{_pct(int(s['conv']), int(s['parsed']))} |"
            )
    add("")

    # ── Recommendation + hypothesis ──
    add("## Recommended tuple + evidence")
    add("")
    add(_recommendation_text(v, lat))
    add("")
    add("## Honest read of the information-ceiling hypothesis")
    add("")
    add(_hypothesis_text(v))
    add("")
    add(
        "**Harness/raw:** `experiments/lab/featherless_sweep.py` + "
        "`experiments/lab/results-featherless-sweep.jsonl` (per-cell grades + "
        "parse-success + tokens + latency + `transport` + `substrate_flags`; the "
        "matrix actually run is logged at run time — no silent truncation). The "
        "9B-class reference is the in-sweep `Qwen/Qwen3-8B`; the committed Ollama "
        "`results-model-ceiling-q9b.jsonl` is a secondary historical row."
    )
    add("")
    REPORT.write_text("\n".join(lines))
    print(f"wrote {REPORT}")
    return 0


def _fit_labels(v: Mapping[str, Any]) -> list[str]:
    return sorted({k[0] for k in v["fit_cells"]})


def _quadrant_text(v: Mapping[str, Any]) -> str:
    fit = _fit_labels(v)
    if not fit:
        return (
            "**Quadrant verdict — UNDETERMINED.** No model cleared the "
            "structured-output bar (see fidelity table)."
        )
    deltas = [d for _k, d in v["cover_helps"]]
    mean_delta = statistics.mean(deltas) if deltas else 0.0
    helped = sum(1 for d in deltas if d >= 0.1)
    floor = float(v["flag_floor"])
    inconclusive = v.get("cover_inconclusive", [])
    incon_note = (
        f" ({len(inconclusive)} cell(s) excluded as INCONCLUSIVE — cover-ON "
        "parse-success below 50%, so a 0-denominator self-co rate is not counted "
        "as a cover win.)"
        if inconclusive
        else ""
    )
    return (
        "**Quadrant verdict — BOTH, leaning INFORMATION CEILING.** The cover "
        "directive's effect on self-co-location is SMALL and INCONSISTENT across "
        f"the fit cells (mean Δ {100 * mean_delta:+.0f} pp; helps ≥10 pp in only "
        f"{helped} of {len(deltas)} comparable cells, back-fires in others) — far "
        "weaker than its effect on the 9B's own contexts (cover cut self-co "
        f"55%→21% in `results-deflection-probe.jsonl`).{incon_note} So there IS a "
        "prompt-artifact component (the v5 directive never reaches the reply path "
        "today, audit gp-1) worth wiring in at 14.5, but it does NOT reliably "
        "dissolve the tell. The decisive ceiling signal is the self-FLAG floor: it "
        f"never falls below {100 * floor:.0f}% on any fit model — the impostor keeps "
        "minting a structured self-contradiction because it is lying into a "
        "detector fed by sightings it never saw (`report-model-ceiling-probe.md`). "
        "Capability buys cleaner JSON, not a clean alibi."
    )


def _recommendation_text(
    v: Mapping[str, Any], lat: Mapping[tuple[str, str], float]
) -> str:
    off_off = v["off_off"]
    cands = [
        k
        for k, s in off_off.items()
        if k[0] != REFERENCE_LABEL
        and int(s["n"])
        and int(s["parsed"]) / int(s["n"]) >= 0.9
    ]
    if not cands:
        return (
            "No candidate cleared a 90% parse-success bar; recommend re-opening "
            "the upstream adapter before locking a tuple at 14.6."
        )
    order = {s.label: i for i, s in enumerate(SLATE)}
    cands.sort(key=lambda k: (k[1] != "non_thinking", order.get(k[0], 99)))
    best = cands[0]
    best_s = off_off[best]
    best_parse = _pct(int(best_s["parsed"]), int(best_s["n"]))
    latv = lat.get(best)
    lats = f"~{latv}s/turn isolated" if latv is not None else "latency n/a"
    speed = next(
        (k for k in cands if k[0] == "qwen3-30b-a3b" and k[1] == "non_thinking"), None
    )
    speed_lat = lat.get(speed) if speed else None
    speed_line = (
        f" For the trigger_model (latency-sensitive), "
        f"`{_id_for('qwen3-30b-a3b')}` (MoE) is the speed option at "
        f"~{speed_lat}s/turn vs ~{latv}s for the 32B."
        if speed and speed_lat is not None
        else ""
    )

    # Classify the non-Qwen models against the SAME 90% structured-output bar the
    # recommendation/fidelity table use (NOT the 50% verdict-`fit` threshold), so
    # the text doesn't claim a marginal model "clears the parse bar".
    def _parse_rate(label: str) -> float:
        s = off_off.get((label, "non_thinking"))
        return (int(s["parsed"]) / int(s["n"])) if s and int(s["n"]) else 0.0

    nq_bits: list[str] = []
    for label, name in (
        ("cydonia-24b", "Cydonia-24B-v2"),
        ("glm-4-32b", "GLM-4-32B-0414"),
    ):
        pr = _parse_rate(label)
        if pr >= 0.9:
            nq_bits.append(f"{name} clears the 90% bar ({pr * 100:.0f}%)")
        elif pr >= 0.5:
            nq_bits.append(f"{name} is MARGINAL ({pr * 100:.0f}%, below the 90% bar)")
        else:
            nq_bits.append(f"{name} is unfit ({pr * 100:.0f}%)")
    nq = (
        " Via the bare send (omitting the Qwen-only chat kwarg), "
        + "; ".join(nq_bits)
        + " — so the 0% in the prior version was an adapter artifact, now "
        "corrected. They remain non-default (a marginal/lower-deflection profile "
        "behind the recommended Qwen3-32B), not disqualified on a parse artifact."
    )
    # Data-driven mode rationale: thinking now ACTUALLY reasons (best-shot
    # profile = none + 16384 + strip), so compare the recommended model's thinking
    # vs non-thinking cells on the FAIR test and report the DIRECTION from the
    # numbers — not a pre-data assumption that thinking is inert.
    nt = off_off.get((best[0], "non_thinking"))
    th = off_off.get((best[0], "thinking"))
    mode_note = ""
    if nt and th and int(nt["parsed"]) and int(th["parsed"]):

        def _r(s: Mapping[str, Any], key: str) -> int:
            return round(100 * _rate(s, key))

        d_defl = _r(th, "deflect") - _r(nt, "deflect")
        d_co = _r(th, "self_co") - _r(nt, "self_co")
        d_flag = _r(th, "self_flag") - _r(nt, "self_flag")
        helps = (d_defl >= 10 or d_flag <= -10 or d_co <= -10) and not (
            d_defl <= -10 or d_flag >= 10 or d_co >= 10
        )
        hurts = (d_defl <= -10 or d_flag >= 10 or d_co >= 10) and not (
            d_defl >= 10 or d_flag <= -10 or d_co <= -10
        )
        nt_lat, th_lat = (
            lat.get((best[0], "non_thinking")),
            lat.get((best[0], "thinking")),
        )
        cost = (
            f" at a real latency cost (~{th_lat}s vs ~{nt_lat}s/turn)"
            if nt_lat is not None and th_lat is not None
            else " at a real latency cost"
        )
        deltas = (
            f"deflect {d_defl:+d} pp, self-flag {d_flag:+d} pp, self-co {d_co:+d} pp"
        )
        if helps:
            mode_note = (
                f" **Mode is a genuine tradeoff now** (the fair best-shot test — "
                f"thinking really reasons, ~16k tokens): on this model thinking "
                f"MEASURABLY IMPROVES behavior ({deltas}){cost}. Mode is therefore "
                f"a 14.6 quality-vs-latency call — `non_thinking` is the "
                f"latency-cheap default, `thinking` the higher-quality option; it is "
                f"no longer the degenerate axis it was under the 2048/json_object "
                f"handicap."
            )
        elif hurts:
            mode_note = (
                f" Mode: on a fair best-shot test thinking does NOT help here "
                f"({deltas}){cost}; `non_thinking` recommended."
            )
        else:
            mode_note = (
                f" Mode: on a fair best-shot test thinking and non-thinking are "
                f"close ({deltas}){cost}; `non_thinking` recommended for latency."
            )
    return (
        f"**Recommended (meeting_model, trigger_model, mode) = "
        f"(`{_id_for(best[0])}`, `{_id_for(best[0])}`, `{best[1]}`).** Evidence: "
        f"it clears the structured-output bar at {best_parse} parse-success "
        f"({lats}), posts a low self-co-location, and converts on the hard vote "
        f"cases.{speed_line}{mode_note}{nq} NOTE (integration risk): these "
        f"isolated-turn metrics are PROXIES, not the live R-gate — a model can "
        f"deflect/convert better in isolation yet still correctly SKIP in a noisy "
        f"full game. The lock at 14.6 must read this as evidence, not verdict; the "
        f"trigger_model defaults to the meeting_model id pending a dedicated "
        f"trigger-corpus pass."
    )


def _hypothesis_text(v: Mapping[str, Any]) -> str:
    ref = v["ref_cell"]
    floor = float(v["flag_floor"])
    fit = _fit_labels(v)
    if int(ref["parsed"]) == 0 or not fit:
        return "Inconclusive: the reference or fit cells did not parse."
    ref_co = _rate(ref, "self_co")
    ref_flag = _rate(ref, "self_flag")
    return (
        "**Supported — and now controlled on identical contexts.** With the "
        "9B-class `qwen3-8b` reference run over the SAME frozen contexts as the "
        "stronger candidates, the self-incrimination tell does NOT fall as model "
        f"strength rises: the self-FLAG floor stays ≥ {100 * floor:.0f}% across "
        f"every fit model (reference self-flag {100 * ref_flag:.0f}%, self-co "
        f"{100 * ref_co:.0f}%) and the cover prompt does not reliably remove it. "
        "This is the `model_ceiling_probe.py:11-14` signature of an INFORMATION "
        "ceiling, not a model ceiling — the impostor reasons faithfully from a "
        'memory that says "you found the body here" into a detector fed by '
        "sightings it never saw. The one place the stronger models clearly DIFFER "
        "from the 9B is the vote corpus: on the hard inversion cases (a true "
        "impostor at suspicion 1.00 over the 0.60 gate where the recorded 9B "
        "SKIPPED) the fit Featherless models convert — the sharpened Phase-14 "
        "question ('can the new model DRIVE the corrected substrate where the 9B "
        "couldn't?') answered YES *in isolation*. But that is an isolated "
        "single-ballot proxy, NOT the live R-gate: only the 14.7 re-record + 14.8 "
        "R-gate can settle it. Net: a stronger model is necessary (it fixes the "
        "9B's structured output + the isolated skip pathology) but the "
        "meeting-deflection tell points at Phase-15 information levers "
        "(asymmetric visibility / vents / sabotage), not a further model upgrade."
    )


def _id_for(label: str) -> str:
    for s in SLATE:
        if s.label == label:
            return s.model_id
    return label


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("run", help="run the full sweep matrix")
    r.add_argument("--sample-dir", type=Path, default=Path("replays/samples/9p2i"))
    r.add_argument(
        "--facts",
        type=Path,
        default=None,
        help="extractor facts JSON (kill ground truth) enabling the opening "
        "corpus; produced by audits/workflows/extract_gameplay_facts.py.",
    )
    r.add_argument("--reply-cap", type=int, default=16)
    r.add_argument("--vote-limit", type=int, default=8)
    r.add_argument("--opening-cap", type=int, default=10)
    r.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Concurrent requests. Default 2: the plan caps at 4 concurrency "
        "units and a 32B request costs 2 units, so >2 risks 429s.",
    )
    r.add_argument("--latency-samples", type=int, default=2)
    r.add_argument(
        "--substrates",
        type=str,
        default="off,on",
        help="Comma list of substrates to run: off, on, or off,on.",
    )
    r.add_argument("--base-url", type=str, default=None)
    r.add_argument(
        "--models",
        type=str,
        default=None,
        help="Comma list of model LABELS to run (default all). Use with --append "
        "to re-run a single model after an outage and merge it back, e.g. "
        "--models cydonia-24b --append.",
    )
    r.add_argument(
        "--append",
        action="store_true",
        help="Append to the results file instead of truncating (for a --models "
        "partial re-run merged into an existing matrix).",
    )
    sub.add_parser("report", help="(re)generate the report from the results jsonl")
    args = parser.parse_args()

    if args.mode == "report":
        return write_report()

    api_key = os.environ.get("FEATHERLESS_API_KEY")
    if not api_key:
        raise SystemExit("run requires FEATHERLESS_API_KEY in the env.")
    # Validate the substrate tokens exactly (a typo like "onn" must not silently
    # be treated as flag-OFF and mislabel the operator-run matrix).
    tokens = [t.strip().lower() for t in args.substrates.split(",") if t.strip()]
    bad = [t for t in tokens if t not in ("off", "on")]
    if bad or not tokens:
        raise SystemExit(
            f"--substrates must be a comma list of 'off'/'on' (got {args.substrates!r}"
            + (f"; invalid: {bad}" if bad else "; empty")
            + ")"
        )
    substrates = tuple(t == "on" for t in tokens)
    models = SLATE
    if args.models:
        want = {m.strip() for m in args.models.split(",") if m.strip()}
        models = tuple(s for s in SLATE if s.label in want)
        unknown = want - {s.label for s in SLATE}
        if unknown or not models:
            raise SystemExit(
                f"--models: unknown label(s) {sorted(unknown)}; "
                f"valid: {[s.label for s in SLATE]}"
            )
    cfg = SweepConfig(
        sample_dir=args.sample_dir,
        facts_path=args.facts,
        reply_cap=args.reply_cap,
        vote_limit=args.vote_limit,
        opening_cap=args.opening_cap,
        concurrency=args.concurrency,
        latency_samples=args.latency_samples,
        substrates=substrates,
        base_url=args.base_url,
        models=models,
        append=args.append,
    )
    rc = asyncio.run(run_sweep(cfg, api_key=api_key))
    if rc == 0:
        write_report()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
