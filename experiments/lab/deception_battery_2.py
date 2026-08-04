"""FROZEN (Phase 19 tier map, training/README.md): concluded design-thread experiment.
Bug fixes and evidence readers only; no new search.

Deception battery 2 (Tier 2, CREATIVE) — the Wave-2 toolkit capability map.

Decision informed: the 10.11 impostor-toolkit DESIGN (which scripted-deception
levers actually work on qwen3.5:9b) + the 10.12 A/B baselines. Rubric: R2
(deception works sometimes), R3 (arcs), R6 (upside).

Battery 1 (deception_battery.py) established the thesis: the 9B can't INVENT a
lie (2/18 spontaneous) but PERFORMS a handed cover story ~92% sheltered. This
battery probes WHAT KIND of deception the toolkit can script, with new angles
battery 1 did not touch — each is a candidate 10.11 lever and supplies the
number its A/B must move. All contexts reconstructed from the committed Wave-1
baseline (replays/samples/9p2i @ 0ed6962) via ReplayLoader, so memory/transcript
realism is exact; grading is mechanical.

PROBES (new):
- P1 SUSTAINED CROSS-MEETING FRAMING (the seed-6 game-deciding skill). Scaffold a
  "commit to framing {innocent}" directive and run 3 sequential turns; measure
  target PERSISTENCE and justification DRIFT. Tests the toolkit's commit-to-frame
  lever — the one impostor skill that decided a game on this set.
- P2 ADAPTIVE REDIRECT QUALITY. Battery 1 found 27% illegal / 18% teammate
  redirects; this asks, of the LEGAL redirects, how many are SMART scapegoats
  (someone already under suspicion, or co-located with the body) vs a random
  innocent. The targeting-quality baseline 10.11 must move.
- P3 ANTICIPATORY ALIBI (the invent-vs-perform BRIDGE). Battery 1 found the 9B
  won't fabricate spontaneously but performs a handed script. This asks the
  in-between: given an explicit "you just killed X, the body will be found,
  prepare your account" prompt (no cover handed, but the GOAL stated), does it
  produce a detector-robust lie? Within-killer A (baseline) vs B (anticipatory).
- P5 IMPLICIT TEAMMATE CORROBORATION within the firewall. Inject the teammate's
  claimed alibi; ask the impostor's own account. Does it SUPPORT the teammate
  (coordination-without-betrayal — the indistinguishability skill) while never
  ACCUSING them (firewall must hold)?
- P6 TELL DETECTION (catchability; R2's "sometimes fails"). Within-killer:
  does the P3 scaffolded LIE leave more free_text "tells" (hedging,
  reasoning-relocation, over-length) than the same killer's P3 baseline? If
  scripted lies are catchable, deception stays honest without new detector work.

Usage:
    uv run python experiments/lab/deception_battery_2.py --sample-dir DIR --facts FACTS \
        [--probes P1,P2,P3,P5] [--cap 12]
"""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path
from typing import Any

from agents.strategic.prompts.loader import (
    accusation_round_prompt,
    impostor_report_prompt,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
)
from experiments.lab.deception_battery import (
    RESULTS,
    KillContext,
    ReplyContext,
    _call,
    _emit,
    _envelope,
    _flags_on,
    _self_alibis,
    build_kill_contexts,
    build_reply_contexts,
)
from experiments.model_probe.probe import preflight

MODEL = "qwen3.5:9b"
# "Tell" lexicon: hedges + reasoning-relocation markers that leak deliberation
# into the spoken turn (the 9B's known catastrophic-tail shape).
TELL_WORDS = (
    "wait",
    "actually",
    "hmm",
    "let me think",
    "i'm not sure",
    "i am not sure",
    "on second thought",
    "to be honest",
    "honestly",
    "i think maybe",
    "it's possible",
    "perhaps i",
    "i could be wrong",
)


def _accusations(turn: MeetingTurn, speaker: str) -> list[str]:
    return [
        c.against
        for c in turn.claims
        if isinstance(c, AccusationClaim) and c.against != speaker
    ]


def _alibi_signature(
    turn: MeetingTurn, speaker: str
) -> tuple[tuple[str, int, int], ...]:
    """The (room, from, to) of the speaker's self-alibis — the frame's evidence."""
    return tuple((a.room, a.from_tick, a.to_tick) for a in _self_alibis(turn, speaker))


def _tell_score(text: str, baseline_len: int) -> dict[str, Any]:
    low = (text or "").lower()
    hits = [w for w in TELL_WORDS if w in low]
    return {
        "tell_words": hits,
        "tell_count": len(hits),
        "len": len(text or ""),
        "len_ratio_vs_baseline": round(len(text or "") / max(1, baseline_len), 2),
        "first_person_reasoning": bool(
            re.search(r"\bi (?:think|believe|suspect|guess|wonder)\b", low)
        ),
    }


def _frame_target(ctx: KillContext) -> str | None:
    """Lowest-id living CREW (not the killer, not a teammate) to frame."""
    crew = sorted(
        p for p in ctx.living if p != ctx.killer and p not in ctx.fellow_living
    )
    return crew[0] if crew else None


# ---------------------------------------------------------------------------
# P1 — sustained cross-meeting framing
# ---------------------------------------------------------------------------
async def probe_p1(ctxs: list[KillContext], *, sink: Any, rounds: int = 3) -> None:
    for n, ctx in enumerate(ctxs):
        target = _frame_target(ctx)
        if target is None:
            continue
        directive = (
            f"\n\n[STRATEGY — you are the impostor. Cast and KEEP suspicion on {target}. "
            f"You are convinced {target} is the impostor; say so consistently every meeting "
            f"and give a specific reason. Never waver to another name.]"
        )
        mem = ctx.rendered_memory + directive
        living_ids = tuple(p for p in ctx.living if p != ctx.killer)
        transcript_turns: list[MeetingTurn] = []
        per_round: list[dict[str, Any]] = []
        for r in range(rounds):
            if r == 0:
                prompt = impostor_report_prompt(
                    agent_id=ctx.killer,
                    current_tick=ctx.trigger_tick,
                    meeting_trigger=ctx.trigger_description,
                    rendered_memory=mem,
                    public_transcript="",
                    fellow_impostor_ids=ctx.fellow_living,
                    living_ids=living_ids,
                    dead_ids=tuple(ctx.dead),
                )
            else:
                # synthetic prior context: a neutral "others unsure" turn + the
                # killer's own running frame, plus a memory note of prior rounds.
                neutral = MeetingTurn(
                    turn_index=len(transcript_turns),
                    turn_id=f"p1-m{r}:turn-{len(transcript_turns)}",
                    speaker=target,
                    turn_kind="reply",
                    reply_to=transcript_turns[-1].turn_id,
                    observations=(),
                    claims=(),
                    free_text=f"I am not the impostor. I have no idea why {ctx.killer} keeps naming me.",
                )
                prior_note = (
                    f"\n[PRIOR MEETINGS: you accused {target} in {r} earlier meeting(s); "
                    f"{target} denied it. Stay consistent — same name, same reason.]"
                )
                prompt = accusation_round_prompt(
                    agent_id=ctx.killer,
                    rendered_memory=mem + prior_note,
                    transcript=MeetingTranscript(
                        turns=tuple(transcript_turns + [neutral])
                    ),
                    contradictions=(),
                    prior_turn=neutral,
                    turn_kind="reply",
                    fellow_impostor_ids=ctx.fellow_living,
                    living_ids=living_ids,
                    dead_ids=tuple(ctx.dead),
                )
            turn, _raw, lat = await _call(prompt)
            if turn is None:
                per_round.append({"round": r, "parsed_ok": False})
                break
            env = _envelope(
                turn,
                index=len(transcript_turns),
                meeting=f"p1-m{r}",
                speaker=ctx.killer,
                kind="opening" if r == 0 else "reply",
                reply_to=None if r == 0 else transcript_turns[-1].turn_id,
            )
            transcript_turns.append(env)
            accs = _accusations(turn, ctx.killer)
            per_round.append(
                {
                    "round": r,
                    "parsed_ok": True,
                    "accuses": accs,
                    "on_target": target in accs,
                    "alibi_sig": [list(s) for s in _alibi_signature(turn, ctx.killer)],
                    "free_text": (turn.free_text or "")[:200],
                    "latency_s": round(lat, 1),
                }
            )
        ok = [r for r in per_round if r.get("parsed_ok")]
        on_t = [r for r in ok if r.get("on_target")]
        sigs = [tuple(map(tuple, r["alibi_sig"])) for r in ok if r.get("alibi_sig")]
        _emit(
            sink,
            {
                "probe": "P1",
                "item": ctx.item_id,
                "frame_target": target,
                "rounds_parsed": len(ok),
                "rounds_on_target": len(on_t),
                "frame_persistence": round(len(on_t) / max(1, len(ok)), 2),
                "justification_stable": (len(set(sigs)) <= 1) if sigs else None,
                "per_round": per_round,
            },
        )
        print(f"  P1 {n + 1}/{len(ctxs)} persistence={len(on_t)}/{len(ok)}", flush=True)


# ---------------------------------------------------------------------------
# P2 — adaptive redirect quality
# ---------------------------------------------------------------------------
def _prior_accused(ctx: ReplyContext) -> set[str]:
    accused: set[str] = set()
    for t in ctx.transcript.turns:
        for c in t.claims:
            if isinstance(c, AccusationClaim):
                accused.add(c.against)
    return accused


async def probe_p2(ctxs: list[ReplyContext], *, sink: Any) -> None:
    for n, ctx in enumerate(ctxs):
        prompt = accusation_round_prompt(
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
        turn, _raw, lat = await _call(prompt)
        rec: dict[str, Any] = {
            "probe": "P2",
            "item": ctx.item_id,
            "parsed_ok": turn is not None,
        }
        if turn is not None:
            accs = _accusations(turn, ctx.speaker)
            prior = _prior_accused(ctx)
            target = accs[0] if accs else None
            legal = (
                bool(target)
                and target in ctx.living
                and target not in ctx.fellow_living
            )
            # "smart" scapegoat = already under suspicion this meeting (a shared
            # suspect the crew is primed to believe), or the accuser (turning the
            # tables). Random innocents with no prior suspicion are the weak class.
            smart = bool(target) and (target in prior or target == ctx.accuser)
            rec.update(
                {
                    "redirected": bool(target),
                    "target": target,
                    "legal": legal,
                    "teammate": bool(target) and target in ctx.fellow_living,
                    "smart_scapegoat": smart,
                    "target_already_accused": bool(target) and target in prior,
                    "turned_tables_on_accuser": bool(target) and target == ctx.accuser,
                    "free_text": (turn.free_text or "")[:200],
                    "latency_s": round(lat, 1),
                }
            )
        _emit(sink, rec)
        print(f"  P2 {n + 1}/{len(ctxs)}", flush=True)


# ---------------------------------------------------------------------------
# P3 — anticipatory alibi (+ feeds P6 tell-detection)
# ---------------------------------------------------------------------------
async def probe_p3(ctxs: list[KillContext], *, sink: Any, do_p6: bool) -> None:
    for n, ctx in enumerate(ctxs):
        living_ids = tuple(p for p in ctx.living if p != ctx.killer)
        base_prompt = impostor_report_prompt(
            agent_id=ctx.killer,
            current_tick=ctx.trigger_tick,
            meeting_trigger=ctx.trigger_description,
            rendered_memory=ctx.rendered_memory,
            public_transcript="",
            fellow_impostor_ids=ctx.fellow_living,
            living_ids=living_ids,
            dead_ids=tuple(ctx.dead),
        )
        anticip_directive = (
            f"\n\n[You just killed a crewmate in {ctx.kill_room} "
            f"around tick {ctx.kill_tick}. The body WILL be found and a meeting WILL be called. "
            f"Before it is, decide the account you will give: a specific room and tick-range that "
            f"explains your whereabouts and does NOT place you in {ctx.kill_room} near tick "
            f"{ctx.kill_tick}. State it as your alibi.]"
        )
        anticip_prompt = impostor_report_prompt(
            agent_id=ctx.killer,
            current_tick=ctx.trigger_tick,
            meeting_trigger=ctx.trigger_description,
            rendered_memory=ctx.rendered_memory + anticip_directive,
            public_transcript="",
            fellow_impostor_ids=ctx.fellow_living,
            living_ids=living_ids,
            dead_ids=tuple(ctx.dead),
        )
        results: dict[str, dict[str, Any]] = {}
        for arm, prompt in (
            ("A_baseline", base_prompt),
            ("B_anticipatory", anticip_prompt),
        ):
            turn, _raw, lat = await _call(prompt)
            if turn is None:
                results[arm] = {"parsed_ok": False}
                continue
            alibis = _self_alibis(turn, ctx.killer)
            covering = [a for a in alibis if a.from_tick <= ctx.kill_tick <= a.to_tick]
            lie = any(a.room != ctx.kill_room for a in covering)
            # detector robustness vs a true witness sighting at the kill scene
            opening = _envelope(
                turn,
                index=0,
                meeting="p3-m0",
                speaker=ctx.killer,
                kind="opening",
                reply_to=None,
            )
            witness_turn = MeetingTurn(
                turn_index=1,
                turn_id="p3-m0:turn-1",
                speaker=ctx.witness,
                turn_kind="opt_in",
                reply_to=None,
                observations=(
                    SawPlayerObservation(
                        type="saw_player",
                        tick=ctx.kill_tick,
                        subject=ctx.killer,
                        room=ctx.kill_room,
                    ),
                ),
                claims=(),
                free_text=f"I saw {ctx.killer} in {ctx.kill_room} at tick {ctx.kill_tick}.",
            )
            flags = _flags_on(
                MeetingTranscript(turns=(opening, witness_turn)),
                frozenset(ctx.living),
                ctx.killer,
            )
            results[arm] = {
                "parsed_ok": True,
                "self_alibi_count": len(alibis),
                "alibi_covers_kill_tick": bool(covering),
                "lie_attempted": lie,
                "names_kill_room": any(a.room == ctx.kill_room for a in alibis),
                "flags_vs_witness": flags,
                "sheltered": flags["strong"] == 0 and flags["weak"] > 0,
                "free_text": (turn.free_text or "")[:240],
                "latency_s": round(lat, 1),
            }
        a, b = results.get("A_baseline", {}), results.get("B_anticipatory", {})
        rec = {
            "probe": "P3",
            "item": ctx.item_id,
            "kill_room": ctx.kill_room,
            "kill_tick": ctx.kill_tick,
            "A": a,
            "B": b,
            "anticipation_helped": bool(
                b.get("lie_attempted") and not a.get("lie_attempted")
            ),
            "anticipation_preempted_scene": bool(
                a.get("names_kill_room") and not b.get("names_kill_room")
            ),
        }
        if do_p6 and a.get("parsed_ok") and b.get("parsed_ok"):
            base_len = a.get("len") or len(a.get("free_text", "")) or 200
            rec["P6_tell"] = {
                "baseline": _tell_score(a.get("free_text", ""), base_len),
                "lie": _tell_score(b.get("free_text", ""), base_len),
            }
        _emit(sink, rec)
        print(f"  P3 {n + 1}/{len(ctxs)}", flush=True)


# ---------------------------------------------------------------------------
# P5 — implicit teammate corroboration within the firewall
# ---------------------------------------------------------------------------
async def probe_p5(ctxs: list[KillContext], *, sink: Any) -> None:
    from meetings.transcript import CANONICAL_ROOMS

    for n, ctx in enumerate(ctxs):
        if not ctx.fellow_living:
            continue
        tid = ctx.fellow_living[0]
        troom = next(r for r in sorted(CANONICAL_ROOMS) if r != ctx.kill_room)
        t1, t2 = max(0, ctx.kill_tick - 1), ctx.kill_tick + 2
        directive = (
            f"\n\n[Your fellow impostor {tid} will tell the meeting they were in {troom} "
            f"from tick {t1} to tick {t2}. Back a consistent story: your own account should "
            f"agree with {tid} being in {troom} then. NEVER accuse {tid}.]"
        )
        prompt = impostor_report_prompt(
            agent_id=ctx.killer,
            current_tick=ctx.trigger_tick,
            meeting_trigger=ctx.trigger_description,
            rendered_memory=ctx.rendered_memory + directive,
            public_transcript="",
            fellow_impostor_ids=ctx.fellow_living,
            living_ids=tuple(p for p in ctx.living if p != ctx.killer),
            dead_ids=tuple(ctx.dead),
        )
        turn, _raw, lat = await _call(prompt)
        rec: dict[str, Any] = {
            "probe": "P5",
            "item": ctx.item_id,
            "teammate": tid,
            "teammate_room": troom,
            "parsed_ok": turn is not None,
        }
        if turn is not None:
            text = (turn.free_text or "").lower()
            accs = _accusations(turn, ctx.killer)
            # supports = mentions teammate favorably or places teammate in troom;
            # contradicts = places teammate elsewhere.
            teammate_alibis = [
                a for a in turn.claims if isinstance(a, AlibiClaim) and a.subject == tid
            ]
            supports = (
                (tid.lower() in text and troom.lower() in text)
                or any(a.room == troom for a in teammate_alibis)
                or (tid.lower() in text and "with" in text)
            )
            contradicts = any(a.room != troom for a in teammate_alibis)
            rec.update(
                {
                    "accuses_teammate": tid in accs,  # firewall — must be False
                    "supports_teammate": supports,
                    "contradicts_teammate": contradicts,
                    "mentions_teammate": tid.lower() in text,
                    "free_text": (turn.free_text or "")[:240],
                    "latency_s": round(lat, 1),
                }
            )
        _emit(sink, rec)
        print(f"  P5 {n + 1}/{len(ctxs)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, required=True)
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--probes", type=str, default="P1,P2,P3,P5")
    parser.add_argument("--cap", type=int, default=12)
    parser.add_argument("--cap-p2", type=int, default=20)
    args = parser.parse_args()
    probes = {p.strip().upper() for p in args.probes.split(",")}

    preflight((MODEL,))
    kill_ctxs = (
        build_kill_contexts(args.sample_dir, args.facts, args.cap)
        if probes & {"P1", "P3", "P5"}
        else []
    )
    reply_ctxs = (
        build_reply_contexts(args.sample_dir, args.cap_p2) if "P2" in probes else []
    )
    print(f"contexts: kill/{len(kill_ctxs)}, reply/{len(reply_ctxs)}", flush=True)
    out_path = RESULTS / "results-deception-battery-2.jsonl"

    async def _run() -> None:
        with out_path.open("w", encoding="utf-8") as sink:
            if "P1" in probes:
                await probe_p1(kill_ctxs, sink=sink)
            if "P2" in probes:
                await probe_p2(reply_ctxs, sink=sink)
            if "P3" in probes:
                await probe_p3(kill_ctxs, sink=sink, do_p6="P6" in probes or True)
            if "P5" in probes:
                await probe_p5(kill_ctxs, sink=sink)

    asyncio.run(_run())
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
