"""Deflection probe (gp-2) — does wiring the v5 cover into the REPLY path lift it?

Decision informed: whether the Phase-10 close audit's gp-1 (wire the impostor
cover directive into accusation_round.j2's reply branch) is worth a re-record.
The crater's toolkit half is a TUNING gap: the v5 "prepare your cover" directive
is gated on body-report OPENINGS, but impostors open 0/96 meetings, so it never
reaches them — they only ever speak on REPLY turns, which carry no cover
guidance. The consequence (audit D-1): 30/71 impostor reply alibis self-co-locate
with the body and 27/71 mint a self-contradiction flag.

This is a $0 within-impostor A/B over the recorded reply contexts (the audit's
gp-2). Arm A = the production accusation_round reply prompt as-is. Arm B = the
SAME prompt with the gp-1 cover directive injected into rendered memory (which is
what wiring it into the reply template would do). It does NOT edit any source —
it measures whether the directive changes 9B behavior, BEFORE paying for a
re-record. Mechanical grading; contexts reconstructed from the committed Wave-2
baseline via ReplayLoader.

Target metric: does arm B REDUCE self-co-location + self-flagging and/or LIFT
deflection (counter-accuse a living non-teammate) vs arm A? If yes, gp-1 is worth
a re-record; if not, the gap is the model ceiling and a prompt won't fix it.

Usage:
    uv run python experiments/lab/deflection_probe.py --sample-dir DIR --cap 24
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from agents.strategic.prompts.loader import accusation_round_prompt
from meetings.schemas import (
    AccusationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
)
from meetings.transcript import detect_contradictions
from experiments.lab.deception_battery import (
    RESULTS,
    ReplyContext,
    _call,
    _emit,
    _envelope,
    _self_alibis,
    build_reply_contexts,
)
from experiments.model_probe.probe import preflight

MODEL = "qwen3.5:9b"


def _body(ctx: ReplyContext) -> tuple[str | None, int | None]:
    """The triggering body's (room, tick) from the meeting's opening turn."""
    turns = ctx.transcript.turns
    if not turns:
        return None, None
    for obs in turns[0].observations:
        if isinstance(obs, FoundBodyObservation):
            return obs.room, obs.tick
    return None, None


def _cover_directive(body_room: str, body_tick: int) -> str:
    # The gp-1 cover block, ported from impostor_report.j2's opening-only branch
    # to the reply context (injected via memory to simulate the reply-template
    # wiring without a source change).
    return (
        f"\n\n[COVER — you are the impostor and a body was reported this meeting. "
        f"Build your alibi as ONE room and tick-window AWAY from the body's room "
        f"({body_room}) and the tick it happened (~{body_tick}); reuse the SAME "
        f"room+window if asked again; do NOT claim you found the body and do NOT "
        f"place yourself in {body_room} around tick {body_tick} — an account that "
        f"self-co-locates with the body is exactly what exposes an impostor.]"
    )


def _grade(
    turn: MeetingTurn, ctx: ReplyContext, body_room: str | None, body_tick: int | None
) -> dict[str, Any]:
    alibis = _self_alibis(turn, ctx.speaker)
    text = (turn.free_text or "").lower()
    # self-co-location: a self-alibi naming the body room, or free_text claiming
    # to have found/seen the body.
    alibi_in_body_room = body_room is not None and any(
        a.room == body_room for a in alibis
    )
    found_body_text = "found" in text and (
        "body" in text or "corpse" in text
    )
    self_co_locates = alibi_in_body_room or found_body_text
    # self-flag: does appending this reply mint a detector contradiction on the
    # speaker (the 27/71 self-incrimination class)?
    n_prior = len(ctx.transcript.turns)
    reply = _envelope(
        turn,
        index=n_prior,
        meeting=ctx.meeting_id,
        speaker=ctx.speaker,
        kind="reply",
        reply_to=ctx.prior_turn.turn_id if ctx.prior_turn else None,
    )
    roster = frozenset(ctx.living)
    base_flags = {
        f.event_a_id
        for f in detect_contradictions(ctx.transcript, roster=roster)
        if ctx.speaker in f.subjects
    }
    full = MeetingTranscript(turns=tuple(ctx.transcript.turns) + (reply,))
    new_self_flag = any(
        ctx.speaker in f.subjects and f.event_a_id not in base_flags
        for f in detect_contradictions(full, roster=roster)
    )
    counters = [
        c.against
        for c in turn.claims
        if isinstance(c, AccusationClaim) and c.against != ctx.speaker
    ]
    deflects_legal = any(
        c in ctx.living and c not in ctx.fellow_living for c in counters
    )
    return {
        "self_co_locates_body": self_co_locates,
        "self_alibi_in_body_room": alibi_in_body_room,
        "new_self_flag": new_self_flag,
        "deflects_legal": deflects_legal,
        "counter_ids": counters,
        "free_text": (turn.free_text or "")[:240],
    }


def _kill_explicit_memory(
    mem: str, own_kills: list[tuple[str, str, int]]
) -> str:
    """Rewrite the impostor's memory so its OWN kills read 'You killed X' instead
    of the misleading 'You discovered X's body'. Simulates the proposed firewalled
    self-channel kill line. own_kills = [(victim, room, tick), ...]."""
    by_victim = {v: (room, tick) for v, room, tick in own_kills}
    seen: set[str] = set()
    out_lines: list[str] = []
    for line in mem.splitlines():
        replaced = False
        for victim, (room, tick) in by_victim.items():
            if f"discovered {victim}'s body" in line:
                out_lines.append(
                    f"- [tick {tick}] You (IMPOSTOR) killed {victim} in {room}."
                )
                seen.add(victim)
                replaced = True
                break
        if not replaced:
            out_lines.append(line)
    # victims the impostor never re-saw as a body still get an explicit kill line
    extra = [
        f"- [tick {tick}] You (IMPOSTOR) killed {victim} in {room}."
        for victim, (room, tick) in by_victim.items()
        if victim not in seen
    ]
    return "\n".join(out_lines + extra)


async def run_memory_fix(
    ctxs: list[ReplyContext],
    kills_by_seed: dict[int, list[tuple[str, str, str, int]]],
    *,
    sink: Any,
) -> None:
    """A/B isolating the kill-memory fix ON TOP of the gp-1 cover directive:
    A = cover on the CURRENT 'discovered body' memory (the backfire condition),
    B = cover on a KILL-EXPLICIT memory. Headline: does new_self_flag DROP in B?"""
    for n, ctx in enumerate(ctxs):
        body_room, body_tick = _body(ctx)
        own_kills = [
            (v, room, tick)
            for (killer, v, room, tick) in kills_by_seed.get(ctx.seed, [])
            if killer == ctx.speaker
        ]
        cover = _cover_directive(body_room, body_tick or 0) if body_room else ""
        mems = {
            "A_cover_current_mem": ctx.rendered_memory + cover,
            "B_cover_kill_explicit": _kill_explicit_memory(ctx.rendered_memory, own_kills)
            + cover,
        }
        results: dict[str, dict[str, Any]] = {}
        for arm, mem in mems.items():
            prompt = accusation_round_prompt(
                agent_id=ctx.speaker,
                rendered_memory=mem,
                transcript=ctx.transcript,
                contradictions=ctx.contradictions,
                prior_turn=ctx.prior_turn,
                turn_kind="reply",
                fellow_impostor_ids=ctx.fellow_living,
                living_ids=tuple(p for p in ctx.living if p != ctx.speaker),
                dead_ids=tuple(ctx.dead),
            )
            turn, _raw, _lat = await _call(prompt)
            results[arm] = (
                {"parsed_ok": False}
                if turn is None
                else {"parsed_ok": True, **_grade(turn, ctx, body_room, body_tick)}
            )
        _emit(
            sink,
            {
                "item": ctx.item_id,
                "body_room": body_room,
                "own_kills": own_kills,
                "A": results["A_cover_current_mem"],
                "B": results["B_cover_kill_explicit"],
            },
        )
        print(f"  {n + 1}/{len(ctxs)}", flush=True)


async def run(ctxs: list[ReplyContext], *, sink: Any) -> None:
    for n, ctx in enumerate(ctxs):
        body_room, body_tick = _body(ctx)
        base_prompt = accusation_round_prompt(
            agent_id=ctx.speaker,
            rendered_memory=ctx.rendered_memory,
            transcript=ctx.transcript,
            contradictions=ctx.contradictions,
            prior_turn=ctx.prior_turn,
            turn_kind="reply",
            fellow_impostor_ids=ctx.fellow_living,
            living_ids=tuple(p for p in ctx.living if p != ctx.speaker),
            dead_ids=tuple(ctx.dead),
        )
        results: dict[str, dict[str, Any]] = {}
        for arm in ("A_baseline", "B_cover_on_reply"):
            mem = ctx.rendered_memory
            if arm == "B_cover_on_reply" and body_room is not None:
                mem = ctx.rendered_memory + _cover_directive(body_room, body_tick or 0)
            prompt = (
                base_prompt
                if arm == "A_baseline"
                else accusation_round_prompt(
                    agent_id=ctx.speaker,
                    rendered_memory=mem,
                    transcript=ctx.transcript,
                    contradictions=ctx.contradictions,
                    prior_turn=ctx.prior_turn,
                    turn_kind="reply",
                    fellow_impostor_ids=ctx.fellow_living,
                    living_ids=tuple(p for p in ctx.living if p != ctx.speaker),
                    dead_ids=tuple(ctx.dead),
                )
            )
            turn, _raw, _lat = await _call(prompt)
            results[arm] = (
                {"parsed_ok": False}
                if turn is None
                else {"parsed_ok": True, **_grade(turn, ctx, body_room, body_tick)}
            )
        _emit(
            sink,
            {
                "item": ctx.item_id,
                "body_room": body_room,
                "body_tick": body_tick,
                "A": results["A_baseline"],
                "B": results["B_cover_on_reply"],
            },
        )
        print(f"  {n + 1}/{len(ctxs)}", flush=True)


def _kills_by_seed(facts_path: Path) -> dict[int, list[tuple[str, str, str, int]]]:
    facts = json.loads(facts_path.read_text())
    out: dict[int, list[tuple[str, str, str, int]]] = {}
    for g in facts["games"]:
        out[g["seed"]] = [
            (k["killer"], k["victim"], k["room"], k["tick"])
            for k in g["kills"]
            if k.get("room") is not None
        ]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, required=True)
    parser.add_argument("--cap", type=int, default=24)
    parser.add_argument(
        "--mode", choices=["cover", "memory-fix"], default="cover",
        help="cover = baseline vs cover-on-reply; memory-fix = cover on current vs kill-explicit memory",
    )
    parser.add_argument("--facts", type=Path, help="extractor facts JSON (memory-fix mode)")
    args = parser.parse_args()
    preflight((MODEL,))
    ctxs = build_reply_contexts(args.sample_dir, args.cap)
    print(f"impostor reply contexts: {len(ctxs)} (within-impostor A/B)", flush=True)
    if args.mode == "memory-fix":
        if args.facts is None:
            raise SystemExit("memory-fix mode requires --facts")
        kills = _kills_by_seed(args.facts)
        out_path = RESULTS / "results-memory-fix-probe.jsonl"
        with out_path.open("w", encoding="utf-8") as sink:
            asyncio.run(run_memory_fix(ctxs, kills, sink=sink))
    else:
        out_path = RESULTS / "results-deflection-probe.jsonl"
        with out_path.open("w", encoding="utf-8") as sink:
            asyncio.run(run(ctxs, sink=sink))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
