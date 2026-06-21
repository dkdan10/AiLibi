"""Meeting-prompt fixture battery (Task 13.6) — does the prompt elicit RICHER testimony?

The 13.4 gate (tasks/phase-13.md "GATE FINDING 2026-06-21") proved the inferential
detector is STARVED: the committed 9p2i transcripts hold ~0 multi-witness placements,
so ``reconstruct_stated_paths`` finds no physical-alibi conflicts and R7 = 0/50. The
detector is built and dormant; the lever is the GAME stating more sightings. 13.6 is
that lever (crew STATE more concrete ``saw_player`` observations); its payoff —
"does the new prompt make qwen3.5:9b state richer sightings" — is INVISIBLE to offline
checks and only a real-Qwen run verifies it (a cloud session cannot reach local Ollama).

This battery isolates the PROMPT as the only variable: it reconstructs the FIXED
pre-meeting context each agent had entering a committed meeting (its rendered memory +
the transcript-so-far, via :class:`api.replay_loader.ReplayLoader`, exactly as the
deception batteries do), renders the CURRENT production template against it, and runs
real Qwen ONE call at a time. Run it on ``main`` (old store + old templates) to capture
a baseline, then after the 13.6 edits to capture the treatment, and diff the two JSONLs
(``--compare``): the contexts are reconstructed deterministically from the same
committed replays, so the ONLY difference is the breadcrumb render + the reworked
prompt. The richness metric mirrors ``inference_testimony_probe.py`` (stated placements
= subjects + co-present), and the same run grades the load-bearing FAILURE MODES the
rework must not regress (husk / over-skip / leak / cover-drift), so the rebuild trades
crowding for clarity, NOT for regressions.

Probes:
- CREW-OPEN: the crew body-reporter / emergency-caller opening (crewmate_report.j2).
  The prime "state who you saw, where, when" surface — placements per opening is the
  headline number 13.6 must raise.
- CREW-TURN: every crew reply / opt-in turn (accusation_round.j2). The second sighting
  surface; the opt-in info-share is where a crew witness puts a placement on the record.
- IMP-COVER: a small impostor opening + accused-reply pair (impostor_report.j2 +
  accusation_round.j2), graded for COVER DRIFT (opening vs reply alibi room/window) and
  free-text leaks — the load-bearing guards the trim must carry forward.

Run as a MODULE from the repo root (the lab scripts are not import-path-clean as
bare files: ``import agents`` needs the root on ``sys.path``)::

    uv run python -m experiments.lab.meeting_prompt_battery \
        --sample-dir replays/samples/9p2i --out experiments/lab/results-mpb-baseline.jsonl \
        [--probes CREW-OPEN,CREW-TURN,IMP-COVER] [--cap 10] [--cap-imp 6]
    # ...make the 13.6 edits...
    uv run python -m experiments.lab.meeting_prompt_battery \
        --sample-dir replays/samples/9p2i --out experiments/lab/results-mpb-treatment.jsonl
    uv run python -m experiments.lab.meeting_prompt_battery \
        --compare experiments/lab/results-mpb-baseline.jsonl experiments/lab/results-mpb-treatment.jsonl
"""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from agents.strategic.prompts.loader import (
    accusation_round_prompt,
    crewmate_report_prompt,
)
from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from experiments.lab.deception_battery import (
    KillContext,
    ReplyContext,  # noqa: F401  (re-exported for callers that import from here)
    _call,
    _emit,
    _envelope,
    _self_alibis,
    build_kill_contexts,
)
from experiments.model_probe.corpus import _roles_for_seed, _roster
from experiments.model_probe.probe import preflight
from meetings.schemas import (
    AccusationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries

MODEL = "qwen3.5:9b"
RESULTS = Path("experiments/lab")

# Free-text "tell" lexicon: a crew or impostor turn that narrates role / deliberation
# is the husk / leak failure mode the anti-narration + firewall guards exist to stop.
_LEAK_WORDS = (
    "i killed",
    "my kill",
    "as the impostor",
    "i am the impostor",
    "my victim",
    "my teammate",
    "fellow impostor",
)


# ---------------------------------------------------------------------------
# Crew context reconstruction (the FIXED pre-meeting context per the 13.6 contract)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CrewContext:
    """One crew turn reconstructed from a committed meeting (the prompt fixture)."""

    seed: int
    meeting_id: str
    speaker: str
    kind: str  # "opening" | "reply" | "opt_in"
    rendered_memory: str
    trigger_description: str
    is_body_report: bool
    transcript_so_far: MeetingTranscript
    prior_turn: MeetingTurn | None
    contradictions: tuple[Any, ...]
    living: tuple[str, ...]
    dead: tuple[str, ...]

    @property
    def item_id(self) -> str:
        return f"{self.seed}:{self.meeting_id}:{self.speaker}:{self.kind}"


def _meeting_is_body_report(turns: tuple[MeetingTurn, ...]) -> bool:
    """A body-report meeting iff ANY turn states a found_body observation.

    The crewmate / impostor opening templates branch on the orchestrator's
    "called an emergency meeting" trigger substring; reconstructing it from a
    found_body observation anywhere in the recorded transcript drives the same branch
    deterministically (an emergency opening carries no body —
    :func:`meetings.transcript.triggering_body_rooms`). Scanning every turn (not just
    turn 0) catches a body report whose opener did not restate the body in its LLM
    turn; the committed 9p2i set is body-report-dominant, so this is the safe default.
    """

    return any(
        isinstance(o, FoundBodyObservation) for turn in turns for o in turn.observations
    )


def build_crew_contexts(
    sample_dir: Path, cap: int, *, kinds: frozenset[str]
) -> list[CrewContext]:
    """Reconstruct crew opening / reply / opt-in contexts from committed meetings."""

    game_map = load_canonical_map()
    roster = _roster(sample_dir)
    loader = ReplayLoader(sample_dir, game_map=game_map)
    items: list[CrewContext] = []
    for path in sorted(
        sample_dir.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    ):
        seed = int(path.stem.rsplit("-", 1)[1])
        game_id = f"headless-seed-{seed}"
        roles = _roles_for_seed(seed, game_map, roster)
        for meeting in (
            e for e in read_all_entries(path) if isinstance(e, MeetingReplayEntry)
        ):
            turns = meeting.transcript.turns
            living = sorted({b.voter for b in meeting.ballots})
            dead = sorted(set(roles) - set(living))
            is_body = _meeting_is_body_report(turns)
            opener = turns[0].speaker if turns else None
            trigger = (
                f"{opener} reported a body at tick {meeting.tick}"
                if is_body
                else f"{opener} called an emergency meeting at tick {meeting.tick}"
            )
            for i, turn in enumerate(turns):
                if roles.get(turn.speaker) != "CREWMATE":
                    continue
                kind = turn.turn_kind
                if kind not in kinds:
                    continue
                try:
                    view = loader.get_meeting_memory(
                        game_id, meeting.meeting_id, turn.speaker
                    )
                except KeyError:
                    continue
                prior = None
                if kind == "reply" and turn.reply_to:
                    prior = next((t for t in turns if t.turn_id == turn.reply_to), None)
                items.append(
                    CrewContext(
                        seed=seed,
                        meeting_id=meeting.meeting_id,
                        speaker=turn.speaker,
                        kind=kind,
                        rendered_memory=view.rendered_memory_text,
                        trigger_description=trigger,
                        is_body_report=is_body,
                        transcript_so_far=MeetingTranscript(turns=tuple(turns[:i])),
                        prior_turn=prior,
                        contradictions=tuple(meeting.contradictions),
                        living=tuple(living),
                        dead=tuple(dead),
                    )
                )
                if len(items) >= cap:
                    return items
    return items


# ---------------------------------------------------------------------------
# Grading (richness + the load-bearing failure modes)
# ---------------------------------------------------------------------------
def _richness(turn: MeetingTurn, speaker: str) -> dict[str, Any]:
    """Stated-testimony richness — the material ``reconstruct_stated_paths`` mines.

    A ``saw_player`` observation places its subject AND every ``co_present`` player
    (``meetings.transcript.StatedPlacement``), so ``placements`` = distinct (subject +
    co-present) ids stated across the turn's sightings — the per-turn analogue of
    ``inference_testimony_probe.py``'s placements/meeting. ``with_co_present`` and
    ``distinct_subjects`` are the two-source-conjunction levers 13.4 needs.
    """

    saws = [o for o in turn.observations if isinstance(o, SawPlayerObservation)]
    placed: set[str] = set()
    for o in saws:
        placed.add(o.subject)
        placed.update(o.co_present)
    placed.discard(speaker)
    return {
        "saw_player": len(saws),
        "with_co_present": sum(1 for o in saws if o.co_present),
        "distinct_subjects": len({o.subject for o in saws}),
        "placements": len(placed),
        "completed_task": sum(
            1 for o in turn.observations if o.type == "completed_task"
        ),
        "found_body": sum(1 for o in turn.observations if o.type == "found_body"),
    }


def _failure_modes(turn: MeetingTurn, speaker: str, kind: str) -> dict[str, Any]:
    text = (turn.free_text or "").lower()
    accusations = [
        c.against
        for c in turn.claims
        if isinstance(c, AccusationClaim) and c.against != speaker
    ]
    has_unsure = "unsure" in text
    # Over-skip (husk on an opening): the §5.2 hard rule rejects an opening with
    # neither an accusation nor "unsure"; the manager retries it once, wasting a call.
    over_skip = kind == "opening" and not accusations and not has_unsure
    return {
        "accuses": accusations,
        "has_unsure": has_unsure,
        "over_skip": over_skip,
        "leak": any(w in text for w in _LEAK_WORDS),
        "free_text_len": len(turn.free_text or ""),
    }


def _grade(
    turn: MeetingTurn | None, speaker: str, kind: str, *, role: str
) -> dict[str, Any]:
    if turn is None:
        return {"parsed_ok": False}
    rec: dict[str, Any] = {"parsed_ok": True, "role": role}
    rec.update(_richness(turn, speaker))
    rec.update(_failure_modes(turn, speaker, kind))
    rec["free_text"] = (turn.free_text or "")[:240]
    return rec


# ---------------------------------------------------------------------------
# Probes
# ---------------------------------------------------------------------------
async def probe_crew(ctxs: list[CrewContext], *, sink: TextIO) -> None:
    for n, ctx in enumerate(ctxs):
        living_ids = tuple(p for p in ctx.living if p != ctx.speaker)
        if ctx.kind == "opening":
            prompt = crewmate_report_prompt(
                agent_id=ctx.speaker,
                current_tick=0,
                meeting_trigger=ctx.trigger_description,
                rendered_memory=ctx.rendered_memory,
                public_transcript="",
                living_ids=living_ids,
                dead_ids=tuple(ctx.dead),
            )
        else:
            prompt = accusation_round_prompt(
                agent_id=ctx.speaker,
                rendered_memory=ctx.rendered_memory,
                transcript=ctx.transcript_so_far,
                contradictions=ctx.contradictions,
                prior_turn=ctx.prior_turn,
                turn_kind=ctx.kind,  # type: ignore[arg-type]
                living_ids=living_ids,
                dead_ids=tuple(ctx.dead),
            )
        turn, _raw, lat = await _call(prompt)
        rec = {
            "probe": f"CREW-{ctx.kind.upper()}",
            "item": ctx.item_id,
            "latency_s": round(lat, 1),
        }
        rec.update(_grade(turn, ctx.speaker, ctx.kind, role="CREWMATE"))
        _emit(sink, rec)
        print(f"  CREW {n + 1}/{len(ctxs)} ({ctx.kind})", flush=True)


async def probe_impostor_cover(ctxs: list[KillContext], *, sink: TextIO) -> None:
    """Impostor opening + accused-reply: cover-drift + leak regression (load-bearing)."""

    for n, ctx in enumerate(ctxs):
        living_ids = tuple(p for p in ctx.living if p != ctx.killer)
        from agents.strategic.prompts.loader import impostor_report_prompt

        open_prompt = impostor_report_prompt(
            agent_id=ctx.killer,
            current_tick=ctx.trigger_tick,
            meeting_trigger=ctx.trigger_description,
            rendered_memory=ctx.rendered_memory,
            public_transcript="",
            fellow_impostor_ids=ctx.fellow_living,
            living_ids=living_ids,
            dead_ids=tuple(ctx.dead),
        )
        o_turn, _raw, o_lat = await _call(open_prompt)
        rec: dict[str, Any] = {
            "probe": "IMP-COVER",
            "item": ctx.item_id,
            "kill_room": ctx.kill_room,
            "kill_tick": ctx.kill_tick,
            "latency_s": round(o_lat, 1),
        }
        rec.update(_grade(o_turn, ctx.killer, "opening", role="IMPOSTOR"))
        if o_turn is not None:
            opening = _envelope(
                o_turn,
                index=0,
                meeting="mpb",
                speaker=ctx.killer,
                kind="opening",
                reply_to=None,
            )
            op_alibis = _self_alibis(opening, ctx.killer)
            # Accused-reply: a synthetic witness places the killer at the scene; the
            # reply's alibi must stay CONSISTENT with the opening (cover-drift guard).
            witness = MeetingTurn(
                turn_index=1,
                turn_id="mpb:turn-1",
                speaker=ctx.witness,
                turn_kind="reply",
                reply_to="mpb:turn-0",
                observations=(
                    SawPlayerObservation(
                        type="saw_player",
                        tick=ctx.kill_tick,
                        subject=ctx.killer,
                        room=ctx.kill_room,
                    ),
                ),
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against=ctx.killer,
                        confidence=0.8,
                        reason=f"saw them in {ctx.kill_room} at tick {ctx.kill_tick}",
                    ),
                ),
                free_text=f"I saw {ctx.killer} in {ctx.kill_room} at tick {ctx.kill_tick}.",
            )
            reply_prompt = accusation_round_prompt(
                agent_id=ctx.killer,
                rendered_memory=ctx.rendered_memory,
                transcript=MeetingTranscript(turns=(opening, witness)),
                contradictions=(),
                prior_turn=witness,
                turn_kind="reply",
                fellow_impostor_ids=ctx.fellow_living,
                living_ids=living_ids,
                dead_ids=tuple(ctx.dead),
                is_impostor=True,
                is_body_report=True,
            )
            r_turn, _r_raw, r_lat = await _call(reply_prompt)
            if r_turn is not None:
                reply = _envelope(
                    r_turn,
                    index=2,
                    meeting="mpb",
                    speaker=ctx.killer,
                    kind="reply",
                    reply_to="mpb:turn-1",
                )
                rp_alibis = _self_alibis(reply, ctx.killer)
                consistent = (
                    bool(op_alibis)
                    and bool(rp_alibis)
                    and any(
                        a.room == b.room
                        and a.from_tick <= b.to_tick
                        and b.from_tick <= a.to_tick
                        for a in op_alibis
                        for b in rp_alibis
                    )
                )
                rec["reply"] = {
                    "parsed_ok": True,
                    "opening_alibi": [
                        (a.room, a.from_tick, a.to_tick) for a in op_alibis
                    ],
                    "reply_alibi": [
                        (a.room, a.from_tick, a.to_tick) for a in rp_alibis
                    ],
                    "story_consistent": consistent,
                    "leak": any(
                        w in (r_turn.free_text or "").lower() for w in _LEAK_WORDS
                    ),
                    "latency_s": round(r_lat, 1),
                }
            else:
                rec["reply"] = {"parsed_ok": False}
        _emit(sink, rec)
        print(f"  IMP-COVER {n + 1}/{len(ctxs)}", flush=True)


# ---------------------------------------------------------------------------
# Summary + compare
# ---------------------------------------------------------------------------
def _summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    crew = [
        r for r in rows if r.get("probe", "").startswith("CREW") and r.get("parsed_ok")
    ]
    imp = [r for r in rows if r.get("probe") == "IMP-COVER" and r.get("parsed_ok")]
    replies = [
        r["reply"]
        for r in imp
        if isinstance(r.get("reply"), dict) and r["reply"].get("parsed_ok")
    ]

    def _mean(vals: list[float]) -> float:
        return round(sum(vals) / len(vals), 2) if vals else 0.0

    return {
        "crew_turns": len(crew),
        "crew_parse_fail": sum(
            1
            for r in rows
            if r.get("probe", "").startswith("CREW") and not r.get("parsed_ok")
        ),
        "saw_player_per_turn": _mean([r["saw_player"] for r in crew]),
        "placements_per_turn": _mean([r["placements"] for r in crew]),
        "with_co_present_per_turn": _mean([r["with_co_present"] for r in crew]),
        "distinct_subjects_per_turn": _mean([r["distinct_subjects"] for r in crew]),
        "crew_turns_with_a_sighting": sum(1 for r in crew if r["saw_player"] > 0),
        "over_skip": sum(1 for r in crew if r.get("over_skip")),
        "leak": sum(1 for r in crew if r.get("leak"))
        + sum(1 for r in imp if r.get("leak")),
        "imp_cover_consistent": sum(1 for r in replies if r.get("story_consistent")),
        "imp_replies": len(replies),
    }


def _print_summary(label: str, rows: list[dict[str, Any]]) -> None:
    s = _summarize(rows)
    print(f"\n=== {label} ===")
    for k, v in s.items():
        print(f"  {k:32s} {v}")


def _compare(baseline: Path, treatment: Path) -> None:
    base = [
        json.loads(line) for line in baseline.read_text().splitlines() if line.strip()
    ]
    treat = [
        json.loads(line) for line in treatment.read_text().splitlines() if line.strip()
    ]
    sb, st = _summarize(base), _summarize(treat)
    print("\n=== RICHNESS A/B (baseline -> treatment) ===")
    for k in sb:
        arrow = ""
        if isinstance(sb[k], (int, float)) and isinstance(st[k], (int, float)):
            d = round(st[k] - sb[k], 2)
            arrow = f"   Δ {'+' if d >= 0 else ''}{d}"
        print(f"  {k:32s} {sb[k]}  ->  {st[k]}{arrow}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--probes", type=str, default="CREW-OPEN,CREW-TURN,IMP-COVER")
    parser.add_argument("--cap", type=int, default=10, help="crew context cap")
    parser.add_argument("--cap-imp", type=int, default=6, help="impostor context cap")
    parser.add_argument(
        "--facts", type=Path, help="extractor facts JSON (IMP-COVER only)"
    )
    parser.add_argument(
        "--compare", type=Path, nargs=2, metavar=("BASELINE", "TREATMENT")
    )
    args = parser.parse_args()

    if args.compare:
        _compare(args.compare[0], args.compare[1])
        return 0

    if args.sample_dir is None or args.out is None:
        parser.error("--sample-dir and --out are required unless --compare is given")

    probes = {p.strip().upper() for p in args.probes.split(",")}
    preflight((MODEL,))

    kinds: set[str] = set()
    if "CREW-OPEN" in probes:
        kinds.add("opening")
    if "CREW-TURN" in probes:
        kinds |= {"reply", "opt_in"}
    crew_ctxs = (
        build_crew_contexts(args.sample_dir, args.cap, kinds=frozenset(kinds))
        if kinds
        else []
    )
    imp_ctxs: list[KillContext] = []
    if "IMP-COVER" in probes:
        if args.facts is None:
            print("  (IMP-COVER skipped: pass --facts to enable)", flush=True)
        else:
            imp_ctxs = build_kill_contexts(args.sample_dir, args.facts, args.cap_imp)
    print(f"contexts: crew/{len(crew_ctxs)}, imp/{len(imp_ctxs)}", flush=True)

    async def _run() -> None:
        with args.out.open("w", encoding="utf-8") as sink:
            if crew_ctxs:
                await probe_crew(crew_ctxs, sink=sink)
            if imp_ctxs:
                await probe_impostor_cover(imp_ctxs, sink=sink)

    asyncio.run(_run())
    # Re-read the JSONL we just wrote for the summary (one source of truth; avoids a
    # bespoke tee that the stdlib TextIO typing does not accept).
    rows = [
        json.loads(line)
        for line in args.out.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    _print_summary(str(args.out.name), rows)
    print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
