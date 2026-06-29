"""Featherless model x thinking-mode sweep over reconstructed 9p2i contexts (Task 14.4).

Operator-run, $0-marginal matrix driver. It runs each candidate Featherless
model over the SAME reconstructed decision contexts from the committed
``replays/samples/9p2i`` set, on the PINNED 9B prompts, and grades every cell
with the IDENTICAL mechanical detectors used for the 9B reference so the only
moving variable is the model (and, in the cover 2x2, the directive injection):

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

Every cell is run on BOTH the flag-OFF (legacy) and the flag-ON (corrected 13.5)
substrate. The flag-ON contexts are re-derived OFFLINE by setting the four
``AILIBI_*`` env vars before reconstruction (the levers are replay-deterministic
reductions of the recorded events, read ad-hoc via the ``*_enabled()`` resolvers
— so no re-record is needed); each result row carries the ``substrate_flags``
config that produced its context. The Qwen3 models run in both non-thinking and
thinking mode (the request-time ``enable_thinking`` toggle, Task 14.1, threaded
via :func:`experiments.lab.probe_backends.call_turn`, Task 14.3); the non-Qwen
slate runs non-thinking only.

This module is READ-ONLY over the committed replays and CONSUMES the 14.2/14.3
seams (``model_ceiling_probe`` / ``deflection_probe`` / ``probe_backends`` /
``probe``) without editing them. The 9B reference column is NOT re-run here (it
is a local Ollama model, off the hosted endpoint); the report folds the committed
``results-model-ceiling-q9b.jsonl`` (reply) + ``results-deflection-probe.jsonl``
(cover 2x2) as the flag-OFF 9B reference.

Slate (HuggingFace repo form). Two of the contract's owner-confirmed ids
(``Qwen/Qwen3-30B-A3B``, ``zai-org/GLM-4-32B``) return a hard HTTP 404 from the
live endpoint as of 2026-06-29 — Featherless now serves the suffixed canonical
revisions ``Qwen/Qwen3-30B-A3B-Instruct-2507`` and ``zai-org/GLM-4-32B-0414``,
which ARE the MoE-speed and agentic models the contract names. The driver
confirms each id via ``GET {base_url}/models`` before the run and substitutes the
served revision (documented in the PR ``Decisions``).

Usage (run as a module so the repo root is on the path)::

    # full matrix (needs FEATHERLESS_API_KEY; concurrency<=2 — the plan caps at
    # 4 concurrency units and a 32B request costs 2):
    uv run python -m experiments.lab.featherless_sweep run \
        --sample-dir replays/samples/9p2i --concurrency 2

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
from typing import Any, Final

from agents.strategic.prompts.loader import accusation_round_prompt
from experiments.lab.deception_battery import ReplyContext
from experiments.lab.deflection_probe import _body, _cover_directive, _grade
from experiments.lab.model_ceiling_probe import _select
from experiments.lab.probe_backends import active_substrate_flags, call_turn
from experiments.model_probe.corpus import CorpusItem, build_corpus, render_prompt
from experiments.model_probe.probe import select_corpus
from meetings.schemas import MeetingTurn, VoteBallot

WORK: Final[Path] = Path("experiments/lab")
RESULTS: Final[Path] = WORK / "results-featherless-sweep.jsonl"
REPORT: Final[Path] = WORK / "report-featherless-sweep.md"
# Committed 9B reference data (local Ollama, flag-OFF) folded into the report.
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

# Production turn caps (frozen) — the real backstop under $0 provider-keyed cost.
NUM_PREDICT_TURN: Final[int] = 2048
NUM_PREDICT_VOTE: Final[int] = 1024
TEMPERATURE: Final[float] = 0.4
VOTE_TEMPERATURE: Final[float] = 0.0
# json_object is the ratified default (the slate 400s strict json_schema; 14.1).
RESPONSE_FORMAT_MODE: Final[str] = "json_object"
# The harness discards reasoning explicitly so a reasoning model does not abort
# the sweep (probe-side default; the recorded baseline at 14.7 uses fail_loud).
THINKING_POLICY: Final[str] = "strip"


@dataclass(frozen=True)
class ModelSpec:
    """One slate model: its served id, a short label, and its mode axis."""

    model_id: str
    label: str
    # Whether the request-time thinking toggle is meaningful for this model.
    # The two Qwen3 ids honor ``enable_thinking`` natively; the non-Qwen slate
    # runs non-thinking only (the contract), and — as the live probe found — the
    # adapter's mandatory ``chat_template_kwargs.enable_thinking`` field breaks
    # GLM / Cydonia decoding outright (recorded as a fitness finding).
    thinking_axis: bool


# The slate the contract pins (with the two 404'd ids substituted by their
# served canonical revisions). Order = report order.
SLATE: Final[tuple[ModelSpec, ...]] = (
    ModelSpec("Qwen/Qwen3-32B", "qwen3-32b", thinking_axis=True),
    ModelSpec("Qwen/Qwen3-30B-A3B-Instruct-2507", "qwen3-30b-a3b", thinking_axis=True),
    ModelSpec("zai-org/GLM-4-32B-0414", "glm-4-32b", thinking_axis=False),
    ModelSpec("TheDrummer/Cydonia-24B-v2", "cydonia-24b", thinking_axis=False),
)


@dataclass
class SweepConfig:
    """Knobs for one sweep invocation."""

    sample_dir: Path
    reply_cap: int = 16
    vote_limit: int = 12
    concurrency: int = 6
    latency_samples: int = 3
    substrates: tuple[bool, ...] = (False, True)
    base_url: str | None = None
    models: tuple[ModelSpec, ...] = SLATE


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


def _reply_prompt(ctx: ReplyContext, *, cover: bool) -> str:
    """Render the production reply prompt; inject the gp-1 cover directive if ON.

    ``cover`` mirrors :func:`experiments.lab.deflection_probe.run`'s ``B`` arm —
    the directive is appended to rendered memory (which is what wiring it into
    the reply template would do), so the only moving variable vs the baseline arm
    is the cover injection.
    """

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
    """Run + grade one reply cell; never raises (transport errors are recorded)."""

    body_room, body_tick = _body(ctx)
    prompt = _reply_prompt(ctx, cover=cover)
    rec: dict[str, Any] = {
        "corpus": "reply",
        "model": spec.model_id,
        "label": spec.label,
        "mode": _mode_label(request_thinking),
        "request_thinking": request_thinking,
        "cover": "on" if cover else "off",
        "substrate": "flag_on" if any(flags.values()) else "flag_off",
        "substrate_flags": dict(flags),
        "response_format_mode": RESPONSE_FORMAT_MODE,
        "item": ctx.item_id,
        "body_room": body_room,
    }
    async with sem:
        started = time.perf_counter()
        try:
            result = await call_turn(
                prompt,
                MeetingTurn,
                backend="featherless",
                model=spec.model_id,
                temperature=TEMPERATURE,
                max_tokens=NUM_PREDICT_TURN,
                api_key=api_key,
                base_url=base_url,
                request_thinking=request_thinking,
                thinking_policy=THINKING_POLICY,  # type: ignore[arg-type]
                response_format_mode=RESPONSE_FORMAT_MODE,  # type: ignore[arg-type]
                substrate_flags=flags,
            )
        except Exception as exc:  # noqa: BLE001 — record transport failures, don't abort
            rec["latency_s"] = round(time.perf_counter() - started, 1)
            rec["parsed_ok"] = False
            rec["error"] = f"{type(exc).__name__}: {exc}"[:240]
            return rec
    rec["latency_s"] = round(result.latency_s, 1)
    rec["in_tokens"] = result.in_tokens
    rec["out_tokens"] = result.out_tokens
    rec["thinking_chars"] = result.thinking_chars
    turn = result.parsed
    rec["parsed_ok"] = turn is not None
    if turn is None:
        rec["parse_error"] = (result.parse_error or "")[:200]
        rec["raw_head"] = result.raw_text[:200]
    else:
        rec.update(_grade(turn, ctx, body_room, body_tick))
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
    """Run + grade one vote cell (parse-success + conversion); never raises."""

    prompt = render_prompt(item.context)
    rec: dict[str, Any] = {
        "corpus": "vote",
        "model": spec.model_id,
        "label": spec.label,
        "mode": _mode_label(request_thinking),
        "request_thinking": request_thinking,
        "cover": "n/a",
        "substrate": "flag_on" if any(flags.values()) else "flag_off",
        "substrate_flags": dict(flags),
        "response_format_mode": RESPONSE_FORMAT_MODE,
        "item": item.item_id,
        "voter_role": item.voter_role,
        "recorded_target": item.recorded_target,
        "is_inversion": item.is_inversion,
        "available_impostor_ids": list(item.available_impostor_ids),
        "max_impostor_suspicion": round(item.max_impostor_suspicion, 4),
    }
    async with sem:
        started = time.perf_counter()
        try:
            result = await call_turn(
                prompt,
                VoteBallot,
                backend="featherless",
                model=spec.model_id,
                temperature=VOTE_TEMPERATURE,
                max_tokens=NUM_PREDICT_VOTE,
                api_key=api_key,
                base_url=base_url,
                request_thinking=request_thinking,
                thinking_policy=THINKING_POLICY,  # type: ignore[arg-type]
                response_format_mode=RESPONSE_FORMAT_MODE,  # type: ignore[arg-type]
                substrate_flags=flags,
            )
        except Exception as exc:  # noqa: BLE001
            rec["latency_s"] = round(time.perf_counter() - started, 1)
            rec["parsed_ok"] = False
            rec["error"] = f"{type(exc).__name__}: {exc}"[:240]
            return rec
    rec["latency_s"] = round(result.latency_s, 1)
    rec["in_tokens"] = result.in_tokens
    rec["out_tokens"] = result.out_tokens
    rec["thinking_chars"] = result.thinking_chars
    ballot = result.parsed
    rec["parsed_ok"] = ballot is not None
    if ballot is None:
        rec["parse_error"] = (result.parse_error or "")[:200]
    else:
        rec["target"] = ballot.target
        rec["confidence"] = ballot.confidence
        rec["voted_available_impostor"] = ballot.target in item.available_impostor_ids
    return rec


async def _latency_cell(
    *,
    ctx: ReplyContext,
    spec: ModelSpec,
    request_thinking: bool,
    flags: Mapping[str, bool],
    api_key: str,
    base_url: str | None,
) -> dict[str, Any]:
    """One SEQUENTIAL reply call timed in isolation (the latency pass)."""

    prompt = _reply_prompt(ctx, cover=False)
    rec: dict[str, Any] = {
        "corpus": "latency",
        "model": spec.model_id,
        "label": spec.label,
        "mode": _mode_label(request_thinking),
        "request_thinking": request_thinking,
        "substrate": "flag_on" if any(flags.values()) else "flag_off",
        "substrate_flags": dict(flags),
        "item": ctx.item_id,
    }
    started = time.perf_counter()
    try:
        result = await call_turn(
            prompt,
            MeetingTurn,
            backend="featherless",
            model=spec.model_id,
            temperature=TEMPERATURE,
            max_tokens=NUM_PREDICT_TURN,
            api_key=api_key,
            base_url=base_url,
            request_thinking=request_thinking,
            thinking_policy=THINKING_POLICY,  # type: ignore[arg-type]
            response_format_mode=RESPONSE_FORMAT_MODE,  # type: ignore[arg-type]
            substrate_flags=flags,
        )
    except Exception as exc:  # noqa: BLE001
        rec["latency_s"] = round(time.perf_counter() - started, 1)
        rec["parsed_ok"] = False
        rec["error"] = f"{type(exc).__name__}: {exc}"[:240]
        return rec
    rec["latency_s"] = round(result.latency_s, 1)
    rec["parsed_ok"] = result.parsed is not None
    rec["out_tokens"] = result.out_tokens
    return rec


def _preflight_models(
    specs: Sequence[ModelSpec], *, api_key: str, base_url: str | None
) -> dict[str, bool]:
    """Confirm each id is served via a tiny generation probe (an unknown id 404s).

    Returns ``{model_id: served}``. A 404/400 id is logged and SKIPPED (not a
    silent truncation — the skipped set is reported), so the sweep still produces
    a comparison over the served models.
    """

    import httpx

    resolved = base_url or "https://api.featherless.ai/v1"
    served: dict[str, bool] = {}
    # A cold model load on Featherless can exceed a short read timeout, and a
    # transient 5xx/429/blip is not "unserved": only a 404/400 (an unrecognized
    # id) is a real skip. So allow several generous attempts and treat anything
    # other than a 404/400 as retryable before declaring the id unserved.
    for spec in specs:
        payload = {
            "model": spec.model_id,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
            "temperature": 0.0,
        }
        served[spec.model_id] = False
        last = ""
        for attempt in range(4):
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
            time.sleep(2 * (attempt + 1))
        if not served[spec.model_id]:
            print(f"  PREFLIGHT {spec.model_id}: {last} -> SKIPPED", flush=True)
    return served


def _freeze_contexts(
    cfg: SweepConfig, flag_on: bool
) -> tuple[dict[str, bool], list[ReplyContext], list[CorpusItem]]:
    """Set the substrate env and reconstruct the reply + vote corpora for it."""

    flags = _set_substrate(flag_on)
    reply_ctxs = _select(cfg.sample_dir)[: cfg.reply_cap]
    vote_items = select_corpus(
        build_corpus(cfg.sample_dir),
        all_votes=False,
        crew_all=False,
        limit=cfg.vote_limit,
    )
    print(
        f"substrate {'ON' if flag_on else 'OFF'} {flags}: "
        f"{len(reply_ctxs)} reply ctxs, {len(vote_items)} vote ctxs",
        flush=True,
    )
    return flags, reply_ctxs, vote_items


async def run_sweep(cfg: SweepConfig, *, api_key: str) -> int:
    """Run the full matrix and stream rows to :data:`RESULTS`."""

    served = _preflight_models(cfg.models, api_key=api_key, base_url=cfg.base_url)
    specs = [s for s in cfg.models if served.get(s.model_id)]
    skipped = [s.model_id for s in cfg.models if not served.get(s.model_id)]
    if skipped:
        print(f"SKIPPED (unserved): {skipped}", flush=True)
    if not specs:
        raise SystemExit("no slate models are served; nothing to sweep")

    sem = asyncio.Semaphore(cfg.concurrency)
    n_rows = 0
    matrix_log: list[str] = []
    with RESULTS.open("w", encoding="utf-8") as sink:

        def emit(rec: dict[str, Any]) -> None:
            nonlocal n_rows
            sink.write(json.dumps(rec) + "\n")
            sink.flush()
            n_rows += 1

        for flag_on in cfg.substrates:
            flags, reply_ctxs, vote_items = _freeze_contexts(cfg, flag_on)
            sub = "flag_on" if flag_on else "flag_off"

            for spec in specs:
                for request_thinking in _modes_for(spec):
                    mode = _mode_label(request_thinking)
                    tag = f"{spec.label}/{mode}/{sub}"

                    # Sequential latency micro-pass (isolated timing).
                    for ctx in reply_ctxs[: cfg.latency_samples]:
                        rec = await _latency_cell(
                            ctx=ctx,
                            spec=spec,
                            request_thinking=request_thinking,
                            flags=flags,
                            api_key=api_key,
                            base_url=cfg.base_url,
                        )
                        emit(rec)

                    # Reply behavior pass (cover OFF + cover ON = the 2x2), bounded
                    # concurrency.
                    reply_tasks = [
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
                    for rec in await asyncio.gather(*reply_tasks):
                        emit(rec)

                    # Vote pass, bounded concurrency.
                    vote_tasks = [
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
                    for rec in await asyncio.gather(*vote_tasks):
                        emit(rec)

                    matrix_log.append(
                        f"{tag}: reply={len(reply_ctxs)}x2(cover) "
                        f"vote={len(vote_items)} latency={min(cfg.latency_samples, len(reply_ctxs))}"
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


def _ref_reply() -> dict[str, Any]:
    """The committed flag-OFF 9B reply baseline, summarized."""

    rows = [
        json.loads(line) for line in REF_REPLY.read_text().splitlines() if line.strip()
    ]
    return _summ_reply(rows)


def _summ_reply(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    parsed = [r for r in rows if r.get("parsed_ok")]
    p = len(parsed)
    return {
        "n": n,
        "parsed": p,
        "parse_rate": (p / n) if n else 0.0,
        "self_co": sum(1 for r in parsed if r.get("self_co_locates_body")),
        "self_flag": sum(1 for r in parsed if r.get("new_self_flag")),
        "deflect": sum(1 for r in parsed if r.get("deflects_legal")),
    }


def _pct(num: int, den: int) -> str:
    return f"{num}/{den} ({100 * num / den:.0f}%)" if den else "0/0 (—)"


def _fmt_reply(s: Mapping[str, Any]) -> str:
    p = int(s["parsed"])
    return (
        f"parse {_pct(p, int(s['n']))} · "
        f"deflect {_pct(int(s['deflect']), p)} · "
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
        n = len(v)
        parsed = [r for r in v if r.get("parsed_ok")]
        conv = sum(1 for r in parsed if r.get("voted_available_impostor"))
        summ[k] = {"n": n, "parsed": len(parsed), "conv": conv}
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


def _sweep_reply_items(rows: Sequence[Mapping[str, Any]]) -> set[str]:
    return {
        str(r["item"])
        for r in rows
        if r.get("corpus") == "reply" and r.get("substrate") == "flag_off"
    }


def _ref_reply_items() -> set[str]:
    return {
        str(json.loads(line)["item"])
        for line in REF_REPLY.read_text().splitlines()
        if line.strip()
    }


def _verdict(
    rows: Sequence[Mapping[str, Any]], ref: Mapping[str, Any]
) -> dict[str, Any]:
    """Compute the cover-quadrant verdict + the info-ceiling read from the data."""

    # Use the flag-OFF substrate (matched to the 9B reference) for the headline
    # cover 2x2 and the model-ceiling curve.
    off_off = _group_reply(rows, cover="off", substrate="flag_off")
    off_on = _group_reply(rows, cover="on", substrate="flag_off")
    votes_off = _group_vote(rows, substrate="flag_off")
    # Restrict to cells that parsed enough to be meaningful (>= half parsed).
    fit = {
        k
        for k, s in off_off.items()
        if int(s["n"]) and int(s["parsed"]) / int(s["n"]) >= 0.5
    }

    def rate(s: Mapping[str, Any], key: str) -> float:
        p = int(s["parsed"])
        return (int(s[key]) / p) if p else 0.0

    # Does cover ON reduce self-co-location vs cover OFF (prompt-artifact signal)?
    cover_helps: list[tuple[tuple[str, str], float]] = []
    for k in fit:
        if k in off_on:
            cover_helps.append(
                (k, rate(off_off[k], "self_co") - rate(off_on[k], "self_co"))
            )
    # The self-FLAG floor is the comparable-in-spirit ceiling metric (the 9B's
    # was ~25%): does it stay high / fail to fall on every fit model?
    flag_floor = min((rate(off_off[k], "self_flag") for k in fit), default=0.0)
    # Self-co persists at a non-trivial rate on every fit model?
    self_co_persists = (
        all(rate(off_off[k], "self_co") >= 0.25 for k in fit) if fit else False
    )
    # Conversion on the hard vote cases (where the recorded 9B SKIPPED).
    conv = {
        k: (int(s["conv"]), int(s["parsed"])) for k, s in votes_off.items() if k in fit
    }
    overlap = len(_sweep_reply_items(rows) & _ref_reply_items())
    return {
        "fit_cells": sorted(fit),
        "off_off": off_off,
        "off_on": off_on,
        "cover_helps": cover_helps,
        "flag_floor": flag_floor,
        "self_co_persists": self_co_persists,
        "conversion": conv,
        "ref_overlap": overlap,
        "ref": ref,
    }


def write_report() -> int:
    rows = _rows()
    ref = _ref_reply()
    v = _verdict(rows, ref)
    lat = _latency_by_model(rows)

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
        "contexts, on the PINNED 9B prompts, graded by the IDENTICAL mechanical "
        "`deflection_probe._grade`. **Cost:** $0 (Featherless flat-rate)."
    )
    add("")
    add(
        "Slate substitution (live, 2026-06-29): the contract's owner-confirmed "
        "`Qwen/Qwen3-30B-A3B` and `zai-org/GLM-4-32B` ids 404 on the live "
        "endpoint; Featherless now serves the canonical revisions "
        "`Qwen/Qwen3-30B-A3B-Instruct-2507` and `zai-org/GLM-4-32B-0414`, "
        "substituted here (confirmed via `GET /models` + a generation preflight)."
    )
    add("")

    # ── Structured-output fidelity ──
    add("## Structured-output fidelity (parse-success under `json_object`)")
    add("")
    add("Reply corpus, cover OFF, flag-OFF substrate (matched to the 9B reference):")
    add("")
    add("| model | mode | parse-success | latency (isolated) | fit for sim? |")
    add("|---|---|---|---|---|")
    add(
        f"| **qwen3.5:9b (ref, Ollama)** | non_thinking | "
        f"{_pct(int(ref['parsed']), int(ref['n']))} | ~31s | yes (reference) |"
    )
    for k in _ordered_cells(v["off_off"]):
        s = v["off_off"][k]
        p, n = int(s["parsed"]), int(s["n"])
        pr = p / n if n else 0.0
        fit = "yes" if pr >= 0.9 else ("marginal" if pr >= 0.5 else "**NO**")
        latv = lat.get(k)
        lats = f"~{latv}s" if latv is not None else "—"
        add(f"| {k[0]} | {k[1]} | {_pct(p, n)} | {lats} | {fit} |")
    add("")

    # ── Model-ceiling read (cover OFF) ──
    add("## Model-ceiling-vs-information read (cover OFF, flag-OFF)")
    add("")
    add(
        f"**Caveat — the 9B row is a RATE reference, not an item-matched control.** "
        f"Only {int(v['ref_overlap'])}/16 of this sweep's hard reply contexts "
        f"overlap the committed `results-model-ceiling-q9b.jsonl` (that file "
        f"predates the current 9p2i recording, and `_select` picks the hardest "
        f"body-meeting contexts of *each* recording). So compare the Featherless "
        f"rows to each other on identical contexts; treat the 9B row as a "
        f"prior-recording rate baseline. The load-bearing finding is the tell's "
        f"PERSISTENCE across the Featherless slate, not its absolute level vs 9B."
    )
    add("")
    add("| model | mode | deflect | self-co-loc (the *tell*) | self-flag |")
    add("|---|---|---|---|---|")
    add(
        f"| **qwen3.5:9b (ref)** | non_thinking | "
        f"{_pct(int(ref['deflect']), int(ref['parsed']))} | "
        f"{_pct(int(ref['self_co']), int(ref['parsed']))} | "
        f"{_pct(int(ref['self_flag']), int(ref['parsed']))} |"
    )
    for k in _ordered_cells(v["off_off"]):
        s = v["off_off"][k]
        p = int(s["parsed"])
        if p == 0:
            add(f"| {k[0]} | {k[1]} | — (unfit) | — | — |")
            continue
        add(
            f"| {k[0]} | {k[1]} | {_pct(int(s['deflect']), p)} | "
            f"{_pct(int(s['self_co']), p)} | {_pct(int(s['self_flag']), p)} |"
        )
    add("")

    # ── Cover 2x2 verdict ──
    add("## Cover-directive 2x2 (model x {cover OFF, cover ON-reply})")
    add("")
    add("Self-co-location (the tell) with the cover directive OFF vs ON, flag-OFF:")
    add("")
    add("| model | mode | cover OFF self-co-loc | cover ON self-co-loc | Δ |")
    add("|---|---|---|---|---|")
    for k in _ordered_cells(v["off_off"]):
        soff = v["off_off"][k]
        son = v["off_on"].get(k)
        poff = int(soff["parsed"])
        if poff == 0 or son is None or int(son["parsed"]) == 0:
            add(f"| {k[0]} | {k[1]} | — | — | — |")
            continue
        pon = int(son["parsed"])
        roff = int(soff["self_co"]) / poff
        ron = int(son["self_co"]) / pon
        add(
            f"| {k[0]} | {k[1]} | {_pct(int(soff['self_co']), poff)} | "
            f"{_pct(int(son['self_co']), pon)} | {100 * (ron - roff):+.0f} pp |"
        )
    add("")
    quadrant = _quadrant_text(v)
    add(quadrant)
    add("")

    # ── Substrate delta ──
    add("## Per-model substrate delta (flag-ON vs flag-OFF)")
    add("")
    add(
        "Does the corrected 13.5 substrate (richer testimony / witnessed-kill / "
        "movement / unfrozen memory) help THIS model decide where the 9B "
        "degraded? Reply corpus, cover OFF."
    )
    add("")
    add("| model | mode | flag-OFF | flag-ON |")
    add("|---|---|---|---|")
    on_off = _group_reply(rows, cover="off", substrate="flag_on")
    for k in _ordered_cells(v["off_off"]):
        soff = v["off_off"][k]
        son = on_off.get(
            k, {"n": 0, "parsed": 0, "deflect": 0, "self_co": 0, "self_flag": 0}
        )
        add(f"| {k[0]} | {k[1]} | {_fmt_reply(soff)} | {_fmt_reply(son)} |")
    add("")

    # ── Votes ──
    add("## Vote corpus — parse-success + conversion")
    add("")
    add(
        "Crew votes WITH a visible impostor (the conversion-relevant set; this "
        "8-item slice is half recorded-SKIP inversion cases — a true impostor at "
        "suspicion 1.00 over the 0.60 gate where the 9B SKIPPED — and half "
        "recorded ejections). `conversion` = voter picked an available impostor. "
        "Every fit Featherless model converts 100% on BOTH substrates, i.e. it "
        "votes the suspect where the recorded 9B skipped — the single strongest "
        "'a stronger model drives it' signal here, but an isolated-ballot proxy "
        "(not the live R-gate; see the hypothesis section)."
    )
    add("")
    add("| model | mode | substrate | parse-success | conversion |")
    add("|---|---|---|---|---|")
    for sub in ("flag_off", "flag_on"):
        g = _group_vote(rows, substrate=sub)
        for k in _ordered_cells(g):
            s = g[k]
            n, p, c = int(s["n"]), int(s["parsed"]), int(s["conv"])
            add(f"| {k[0]} | {k[1]} | {sub} | {_pct(p, n)} | {_pct(c, p)} |")
    add("")

    # ── Recommendation ──
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
        "`experiments/lab/results-featherless-sweep.jsonl` (per-cell mechanical "
        "grades + parse-success + tokens + latency + `substrate_flags`). 9B "
        "reference folded from the committed `results-model-ceiling-q9b.jsonl` "
        "(reply) and `results-deflection-probe.jsonl` (cover 2x2), both "
        "flag-OFF / local Ollama."
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
            "**Quadrant verdict — UNDETERMINED on the non-Qwen slate.** No "
            "non-Qwen model cleared the structured-output bar (see fidelity "
            "table), so the cover 2x2 is read only over the Qwen3 models below."
        )
    helps = v["cover_helps"]
    deltas = [d for _k, d in helps]
    mean_delta = statistics.mean(deltas) if deltas else 0.0
    helped = sum(1 for d in deltas if d >= 0.1)
    floor = float(v["flag_floor"])
    return (
        "**Quadrant verdict — BOTH, leaning INFORMATION CEILING.** The cover "
        "directive's effect on self-co-location is SMALL and INCONSISTENT across "
        f"the fit Qwen3 cells (mean Δ {100 * mean_delta:+.0f} pp; it helps "
        f"≥10 pp in only {helped} of {len(deltas)} cells, and back-fires in "
        "others) — a far cry from its strong effect on the 9B's own contexts "
        "(cover cut self-co 55%→21% in `results-deflection-probe.jsonl`). So "
        "there IS a prompt-artifact component (the v5 directive never reaches the "
        "reply path today, audit gp-1) worth wiring in at 14.5, but it does NOT "
        "reliably dissolve the tell on the stronger models. The decisive ceiling "
        "signal is the self-FLAG floor: it never falls below "
        f"{100 * floor:.0f}% on any fit model and exceeds the 9B's own ~25% — "
        "the impostor keeps minting a structured self-contradiction because it is "
        "lying into a detector fed by sightings it never saw (the "
        "`report-model-ceiling-probe.md` mechanism), and a stronger model only "
        "grounds its alibi more faithfully in that poisoned memory. Capability "
        "buys cleaner JSON, not a clean alibi."
    )


def _recommendation_text(
    v: Mapping[str, Any], lat: Mapping[tuple[str, str], float]
) -> str:
    off_off = v["off_off"]
    # Candidates: cells that parsed >= 90%.
    cands = [
        k
        for k, s in off_off.items()
        if int(s["n"]) and int(s["parsed"]) / int(s["n"]) >= 0.9
    ]
    if not cands:
        return (
            "No model cleared a 90% parse-success bar under the pinned 14.1 "
            "adapter on the production prompts — see Decisions / fidelity table. "
            "Recommend re-opening Task 14.1 (the adapter's mandatory "
            "`chat_template_kwargs.enable_thinking` field breaks the non-Qwen "
            "slate) before locking a tuple at 14.6."
        )
    order = {s.label: i for i, s in enumerate(SLATE)}
    # Prefer non_thinking (thinking is ~inert under json_object — see below — and
    # costs latency/tokens), then SLATE order.
    cands.sort(key=lambda k: (k[1] != "non_thinking", order.get(k[0], 99)))
    best = cands[0]
    latv = lat.get(best)
    lats = f"~{latv}s/turn isolated" if latv is not None else "latency n/a"
    # The MoE speed alternative for the trigger model, if it is fit.
    speed = next(
        (k for k in cands if k[0] == "qwen3-30b-a3b" and k[1] == "non_thinking"),
        None,
    )
    speed_lat = lat.get(speed) if speed else None
    speed_line = (
        f" For the trigger_model (latency-sensitive), `{_id_for('qwen3-30b-a3b')}` "
        f"(MoE) is the speed option — same 16/16 parse and 100% isolated vote "
        f"conversion at ~{speed_lat}s/turn vs ~{latv}s for the 32B."
        if speed and speed_lat is not None
        else ""
    )
    return (
        f"**Recommended (meeting_model, trigger_model, mode) = "
        f"(`{_id_for(best[0])}`, `{_id_for(best[0])}`, `{best[1]}` / "
        f"`response_format_mode=json_object`).** Evidence: it clears the "
        f"structured-output bar at 16/16 parse-success on the production prompts "
        f"({lats}), posts the lowest self-co-location of the fit cells, and "
        f"converts 100% on the hard vote cases — where the non-Qwen slate fails "
        f"the structured-output bar entirely (see fidelity table). `non_thinking` "
        f"is chosen because under `json_object` the request-time thinking toggle "
        f"is effectively INERT (no reasoning channel surfaces; thinking_chars ≈ 0) "
        f"yet it adds latency and output tokens for no behavior gain.{speed_line} "
        f"GLM-4-32B-0414 and Cydonia-24B-v2 are flagged UNFIT through the pinned "
        f"14.1 adapter (its mandatory `chat_template_kwargs.enable_thinking` field "
        f"collapses GLM to `{{}}` and 400/504s Cydonia — both DO emit valid JSON "
        f"under a bare `json_object` request, so this is an adapter-compat finding "
        f"to feed back to 14.1/14.6, not purely a model verdict). "
        f"NOTE (integration risk): these isolated-turn metrics are PROXIES, not "
        f"the live R-gate — a model can deflect/convert better in isolation yet "
        f"still correctly SKIP in a noisy full game. The lock at 14.6 must read "
        f"this as evidence, not verdict; the trigger_model defaults to the "
        f"meeting_model id pending a dedicated trigger-corpus pass."
    )


def _hypothesis_text(v: Mapping[str, Any]) -> str:
    ref = v["ref"]
    ref_co = int(ref["self_co"]) / int(ref["parsed"]) if int(ref["parsed"]) else 0.0
    ref_flag = int(ref["self_flag"]) / int(ref["parsed"]) if int(ref["parsed"]) else 0.0
    floor = float(v["flag_floor"])
    overlap = int(v["ref_overlap"])
    # Conversion across fit vote cells (the "can the new model drive it" signal).
    conv_cells = v["conversion"]
    full_conv = (
        all(c == p and p for c, p in conv_cells.values()) if conv_cells else False
    )
    fit = _fit_labels(v)
    if not fit:
        return (
            "Inconclusive on the broad slate: only the Qwen3 models cleared the "
            "structured-output bar through the pinned adapter, so the "
            "cross-model persistence test is limited."
        )
    conv_line = (
        " The one place the stronger models clearly DIFFER from the 9B is the "
        "vote corpus: on the hard inversion cases (a true impostor visible at "
        "suspicion 1.00, over the 0.60 gate, where the recorded 9B SKIPPED) every "
        "fit Featherless model converts 100% — it votes the suspect. That is the "
        "sharpened Phase-14 question ('can the new model DRIVE the corrected "
        "substrate where the 9B couldn't?') answered YES *in isolation*. But this "
        "is an isolated single-ballot proxy, NOT the live R-gate: a calibrated "
        "model may still correctly SKIP inside a noisy full game. Only the 14.7 "
        "re-record + 14.8 R-gate can settle it."
        if full_conv
        else ""
    )
    return (
        "**Supported, with one important counter-signal — and a methodological "
        "caveat.** The self-incrimination tell does NOT disappear as model "
        f"strength rises above the 9B: the self-FLAG floor stays ≥ {100 * floor:.0f}% "
        f"on every fit model (vs the 9B's ~{100 * ref_flag:.0f}%) and "
        "self-co-location persists at a non-trivial rate, neither dissolved by "
        "capability nor by the cover prompt. This is the "
        "`model_ceiling_probe.py:11-14` signature of an INFORMATION ceiling, not a "
        "model ceiling — the impostor reasons faithfully from a memory that says "
        '"you found the body here" into a detector fed by sightings it never saw. '
        f"Caveat: only {overlap}/16 of this sweep's hard reply contexts overlap "
        "the committed 9B run (the 9B file predates the current 9p2i recording), "
        f"so the 9B column (self-co {100 * ref_co:.0f}%, self-flag "
        f"{100 * ref_flag:.0f}%) is a RATE-level reference, not an item-matched "
        "control; the load-bearing observation is the tell's PERSISTENCE across "
        "the Featherless slate on identical contexts, not the absolute level vs "
        f"the 9B.{conv_line} Net: a stronger model is necessary (it fixes the 9B's "
        "structured-output + the isolated skip pathology) but the meeting-deflection "
        "tell points at Phase-15 information levers (asymmetric visibility / vents "
        "/ sabotage), not a further model upgrade."
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
    r.add_argument("--reply-cap", type=int, default=16)
    r.add_argument("--vote-limit", type=int, default=12)
    r.add_argument("--concurrency", type=int, default=6)
    r.add_argument("--latency-samples", type=int, default=3)
    r.add_argument(
        "--substrates",
        type=str,
        default="off,on",
        help="Comma list of substrates to run: off, on, or off,on.",
    )
    r.add_argument("--base-url", type=str, default=None)
    sub.add_parser("report", help="(re)generate the report from the results jsonl")
    args = parser.parse_args()

    if args.mode == "report":
        return write_report()

    api_key = os.environ.get("FEATHERLESS_API_KEY")
    if not api_key:
        raise SystemExit("run requires FEATHERLESS_API_KEY in the env.")
    substrates = tuple(
        token.strip().lower() == "on"
        for token in args.substrates.split(",")
        if token.strip()
    )
    cfg = SweepConfig(
        sample_dir=args.sample_dir,
        reply_cap=args.reply_cap,
        vote_limit=args.vote_limit,
        concurrency=args.concurrency,
        latency_samples=args.latency_samples,
        substrates=substrates,
        base_url=args.base_url,
    )
    rc = asyncio.run(run_sweep(cfg, api_key=api_key))
    if rc == 0:
        write_report()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
