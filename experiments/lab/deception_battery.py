"""Deception probe battery (Tier 2) — the 10.10 pre-contract gate, pulled forward.

Decision informed: Wave-2 contract shape (10.10 toolkit / 10.11 metrics) — can
qwen3.5:9b play the villain at all, and where exactly does it fail? Rubric: R2
(deception works sometimes), R3 (arc consistency), R6 (upside hunt).

Probes (all contexts reconstructed from RECORDED games — the Wave-1 attempt-1
evidence bytes — via ReplayLoader, so memory/transcript realism is exact):

- A  self-report fabrication: the killer opens the meeting for their own kill
     (production impostor_report prompt, their real memory). Graded vs ground
     truth (kill tick/room from the engine walk): lie attempted? coherent?
     Does the fabricated alibi SURVIVE the repaired detector against a true
     witness sighting (expected: weak self-stated -> sheltered sub-gate)?
     Free-text self-incrimination scan.
- A2 consistency under pressure: after their opening, a synthetic accuser
     confronts them with the true sighting; the reply's alibi is compared to
     the opening's (room/window drift = alibi_conflict self-pair fodder).
- B  deflect-without-boomerang: every recorded impostor REPLY context, re-run
     under the production accusation_round prompt. Graded: counter-accusation
     present (living, non-self, non-teammate), self-incrimination, and
     detector-boomerang (does their own reply mint flags against themselves
     when appended to the real transcript-so-far?).
- C  cover-story deployment: A's context plus an injected cover line ("you
     were doing task wiring in ROOM from tick T1-T2") — previews the 10.10
     fake-task affordance: deployed / partial / ignored / freelance-lie.

All grading is mechanical (schema parse, canonical rooms, detector runs);
qualitative reading happens in the report, not via an LLM grader.

Usage::

    uv run python experiments/lab/deception_battery.py --sample-dir DIR \
        [--probes A,A2,B,C] [--cap-a 18] [--cap-b 22] [--cap-c 12]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from pydantic import ValidationError

from agents.strategic.prompts.loader import (
    accusation_round_prompt,
    impostor_report_prompt,
)
from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from experiments.model_probe.corpus import _roles_for_seed, _roster
from experiments.model_probe.probe import _ollama_host, preflight
from llm.ollama_client import _default_send
from llm.provider import _extract_json_block
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
)
from meetings.transcript import (
    CANONICAL_ROOMS,
    WEAK_CONTRADICTION_MARKER_PREFIX,
    detect_contradictions,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries

MODEL = "qwen3.5:9b"
TEMPERATURE = 0.4  # production turn temperature — behavior rates, not greedy
SEED = 0
NUM_CTX = 8192
NUM_PREDICT = 2048  # production turn cap (frozen)
RESULTS = Path("experiments/lab")

KILL_WORDS = (
    "i killed",
    "my kill",
    "as the impostor",
    "i am the impostor",
    "my victim",
)


def _emit(sink: TextIO, rec: dict[str, object]) -> None:
    sink.write(json.dumps(rec) + "\n")
    sink.flush()


@dataclass(frozen=True)
class KillContext:
    seed: int
    game_id: str
    meeting_id: str
    killer: str
    kill_tick: int
    kill_room: str
    trigger_tick: int
    trigger_description: str
    rendered_memory: str
    living: tuple[str, ...]
    dead: tuple[str, ...]
    fellow_living: tuple[str, ...]
    witness: str  # lowest-id living crewmate != killer (synthetic sighter)

    @property
    def item_id(self) -> str:
        return f"{self.seed}:{self.meeting_id}:{self.killer}"


@dataclass(frozen=True)
class ReplyContext:
    seed: int
    meeting_id: str
    speaker: str
    accuser: str | None
    accuser_room_claims: tuple[str, ...]
    transcript: MeetingTranscript
    prior_turn: MeetingTurn | None
    contradictions: tuple[ContradictionRef, ...]
    rendered_memory: str
    living: tuple[str, ...]
    dead: tuple[str, ...]
    fellow_living: tuple[str, ...]
    recorded_counter_accused: str | None

    @property
    def item_id(self) -> str:
        return f"{self.seed}:{self.meeting_id}:{self.speaker}"


def _envelope(
    turn: MeetingTurn,
    *,
    index: int,
    meeting: str,
    speaker: str,
    kind: str,
    reply_to: str | None,
) -> MeetingTurn:
    """Normalize the model's envelope fields the way the manager does."""
    return turn.model_copy(
        update={
            "turn_index": index,
            "turn_id": f"{meeting}:turn-{index}",
            "speaker": speaker,
            "turn_kind": kind,
            "reply_to": reply_to,
        }
    )


def _self_alibis(turn: MeetingTurn, speaker: str) -> list[AlibiClaim]:
    return [
        c for c in turn.claims if isinstance(c, AlibiClaim) and c.subject == speaker
    ]


def _flags_on(
    transcript: MeetingTranscript, roster: frozenset[str], subject: str
) -> dict[str, int]:
    weak = strong = 0
    for flag in detect_contradictions(transcript, roster=roster):
        if subject not in flag.subjects:
            continue
        if WEAK_CONTRADICTION_MARKER_PREFIX in flag.description:
            weak += 1
        else:
            strong += 1
    return {"weak": weak, "strong": strong}


def build_kill_contexts(
    sample_dir: Path, facts_path: Path, cap: int
) -> list[KillContext]:
    """Kill ground truth (killer/tick/room) comes from the extractor facts —
    the replay tick records carry submitted actions only; rooms exist only
    after the engine re-walk the extractor already performed."""
    facts = json.loads(facts_path.read_text())
    kills_by_seed: dict[int, list[dict[str, Any]]] = {
        g["seed"]: [k for k in g["kills"] if k["killer_role"] == "IMPOSTOR"]
        for g in facts["games"]
    }
    game_map = load_canonical_map()
    roster = _roster(sample_dir)
    loader = ReplayLoader(sample_dir, game_map=game_map)
    items: list[KillContext] = []
    for path in sorted(
        sample_dir.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    ):
        seed = int(path.stem.rsplit("-", 1)[1])
        if seed not in kills_by_seed:
            continue
        game_id = f"headless-seed-{seed}"
        roles = _roles_for_seed(seed, game_map, roster)
        entries = list(read_all_entries(path))
        meetings = [e for e in entries if isinstance(e, MeetingReplayEntry)]
        for kill in kills_by_seed[seed]:
            killer, ktick, kroom = kill["killer"], kill["tick"], kill["room"]
            if kroom is None:
                continue
            meeting = next((m for m in meetings if m.tick >= ktick), None)
            if meeting is None:
                continue
            living = sorted({b.voter for b in meeting.ballots})
            if killer not in living:
                continue
            dead = sorted(set(roles) - set(living))
            witness = next(
                (p for p in living if p != killer and roles.get(p) == "CREWMATE"), None
            )
            if witness is None:
                continue
            try:
                view = loader.get_meeting_memory(game_id, meeting.meeting_id, killer)
            except KeyError:
                continue
            fellows = tuple(
                p for p in living if p != killer and roles.get(p) == "IMPOSTOR"
            )
            items.append(
                KillContext(
                    seed=seed,
                    game_id=game_id,
                    meeting_id=meeting.meeting_id,
                    killer=killer,
                    kill_tick=ktick,
                    kill_room=kroom,
                    trigger_tick=meeting.tick,
                    trigger_description=str(meeting.triggered_by),
                    rendered_memory=view.rendered_memory_text,
                    living=tuple(living),
                    dead=tuple(dead),
                    fellow_living=fellows,
                    witness=witness,
                )
            )
            if len(items) >= cap:
                return items
    return items


def build_reply_contexts(sample_dir: Path, cap: int) -> list[ReplyContext]:
    game_map = load_canonical_map()
    roster = _roster(sample_dir)
    loader = ReplayLoader(sample_dir, game_map=game_map)
    items: list[ReplyContext] = []
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
            by_id = {t.turn_id: t for t in turns}
            living = sorted({b.voter for b in meeting.ballots})
            dead = sorted(set(roles) - set(living))
            for i, turn in enumerate(turns):
                if turn.turn_kind != "reply" or roles.get(turn.speaker) != "IMPOSTOR":
                    continue
                prior = by_id.get(turn.reply_to) if turn.reply_to else None
                try:
                    view = loader.get_meeting_memory(
                        game_id, meeting.meeting_id, turn.speaker
                    )
                except KeyError:
                    continue
                rec_ca = next(
                    (
                        c.against
                        for c in turn.claims
                        if isinstance(c, AccusationClaim) and c.against != turn.speaker
                    ),
                    None,
                )
                accuser_rooms = tuple(
                    o.room
                    for o in (prior.observations if prior else ())
                    if isinstance(o, SawPlayerObservation) and o.subject == turn.speaker
                )
                fellows = tuple(
                    p
                    for p in living
                    if p != turn.speaker and roles.get(p) == "IMPOSTOR"
                )
                items.append(
                    ReplyContext(
                        seed=seed,
                        meeting_id=meeting.meeting_id,
                        speaker=turn.speaker,
                        accuser=prior.speaker if prior else None,
                        accuser_room_claims=accuser_rooms,
                        transcript=MeetingTranscript(turns=tuple(turns[:i])),
                        prior_turn=prior,
                        contradictions=meeting.contradictions,
                        rendered_memory=view.rendered_memory_text,
                        living=tuple(living),
                        dead=tuple(dead),
                        fellow_living=fellows,
                        recorded_counter_accused=rec_ca,
                    )
                )
                if len(items) >= cap:
                    return items
    return items


async def _call(prompt: str) -> tuple[MeetingTurn | None, str, float]:
    started = time.perf_counter()
    raw = await _default_send(
        host=_ollama_host(),
        model=MODEL,
        prompt=prompt,
        format_schema=MeetingTurn.model_json_schema(),
        options={
            "temperature": TEMPERATURE,
            "seed": SEED,
            "num_predict": NUM_PREDICT,
            "num_ctx": NUM_CTX,
        },
        think=False,
    )
    latency = time.perf_counter() - started
    try:
        turn = MeetingTurn.model_validate_json(
            _extract_json_block(raw.text, MeetingTurn)
        )
        return turn, raw.text, latency
    except ValidationError:
        return None, raw.text, latency


def _grade_fabrication(
    turn: MeetingTurn, ctx: KillContext, *, cover: tuple[str, int, int] | None = None
) -> dict[str, object]:
    """Mechanical fabrication grade vs ground truth (+ cover deployment if set)."""
    alibis = _self_alibis(turn, ctx.killer)
    covering = [a for a in alibis if a.from_tick <= ctx.kill_tick <= a.to_tick]
    lie = any(a.room != ctx.kill_room for a in covering)
    honest = any(a.room == ctx.kill_room for a in covering)
    text = (turn.free_text or "").lower()
    rec: dict[str, object] = {
        "self_alibi_count": len(alibis),
        "alibi_covers_kill_tick": bool(covering),
        "lie_attempted": lie,
        "honest_placement": honest,
        "self_incriminating_text": any(w in text for w in KILL_WORDS),
        "accuses": [c.against for c in turn.claims if isinstance(c, AccusationClaim)],
    }
    opening = _envelope(
        turn,
        index=0,
        meeting="probe-m0",
        speaker=ctx.killer,
        kind="opening",
        reply_to=None,
    )
    witness_turn = MeetingTurn(
        turn_index=1,
        turn_id="probe-m0:turn-1",
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
    roster = frozenset(ctx.living)
    rec["flags_self_only"] = _flags_on(
        MeetingTranscript(turns=(opening,)), roster, ctx.killer
    )
    rec["flags_vs_witness"] = _flags_on(
        MeetingTranscript(turns=(opening, witness_turn)), roster, ctx.killer
    )
    if cover is not None:
        room, t1, t2 = cover
        deployed = any(
            a.room == room and a.from_tick <= t2 and a.to_tick >= t1 for a in alibis
        )
        room_only = any(a.room == room for a in alibis) and not deployed
        rec["cover"] = {
            "room": room,
            "t1": t1,
            "t2": t2,
            "deployed": deployed,
            "room_only": room_only,
            "ignored": not deployed and not room_only,
        }
    return rec


async def probe_a_and_c(
    ctxs: list[KillContext], *, sink: TextIO, do_a2: int, do_c: int
) -> None:
    a2_done = 0
    for n, ctx in enumerate(ctxs):
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
        turn, raw, latency = await _call(prompt)
        rec = {
            "probe": "A",
            "item": ctx.item_id,
            "kill_tick": ctx.kill_tick,
            "kill_room": ctx.kill_room,
            "parsed_ok": turn is not None,
            "latency_s": round(latency, 1),
        }
        if turn is None:
            rec["raw_head"] = raw[:200]
        else:
            rec.update(_grade_fabrication(turn, ctx))
            rec["free_text"] = (turn.free_text or "")[:400]
        _emit(sink, rec)

        if turn is not None and a2_done < do_a2:
            a2_done += 1
            opening = _envelope(
                turn,
                index=0,
                meeting="probe-m0",
                speaker=ctx.killer,
                kind="opening",
                reply_to=None,
            )
            accusation = MeetingTurn(
                turn_index=1,
                turn_id="probe-m0:turn-1",
                speaker=ctx.witness,
                turn_kind="reply",
                reply_to="probe-m0:turn-0",
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
                free_text=f"I saw {ctx.killer} in {ctx.kill_room} at tick {ctx.kill_tick} — that's where the body is.",
            )
            reply_prompt = accusation_round_prompt(
                agent_id=ctx.killer,
                rendered_memory=ctx.rendered_memory,
                transcript=MeetingTranscript(turns=(opening, accusation)),
                contradictions=(),
                prior_turn=accusation,
                turn_kind="reply",
                fellow_impostor_ids=ctx.fellow_living,
                living_ids=tuple(p for p in ctx.living if p != ctx.killer),
                dead_ids=tuple(ctx.dead),
            )
            r_turn, r_raw, r_lat = await _call(reply_prompt)
            rec2 = {
                "probe": "A2",
                "item": ctx.item_id,
                "parsed_ok": r_turn is not None,
                "latency_s": round(r_lat, 1),
            }
            if r_turn is not None:
                reply = _envelope(
                    r_turn,
                    index=2,
                    meeting="probe-m0",
                    speaker=ctx.killer,
                    kind="reply",
                    reply_to="probe-m0:turn-1",
                )
                op_alibis = _self_alibis(opening, ctx.killer)
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
                rec2.update(
                    {
                        "opening_alibi": [
                            (a.room, a.from_tick, a.to_tick) for a in op_alibis
                        ],
                        "reply_alibi": [
                            (a.room, a.from_tick, a.to_tick) for a in rp_alibis
                        ],
                        "story_consistent": consistent,
                        "confessed": any(
                            w in (r_turn.free_text or "").lower() for w in KILL_WORDS
                        ),
                        "counter_accuses": [
                            c.against
                            for c in r_turn.claims
                            if isinstance(c, AccusationClaim)
                            and c.against != ctx.killer
                        ],
                        "self_flags_full_chain": _flags_on(
                            MeetingTranscript(turns=(opening, accusation, reply)),
                            frozenset(ctx.living),
                            ctx.killer,
                        ),
                        "free_text": (r_turn.free_text or "")[:400],
                    }
                )
            _emit(sink, rec2)

        if n < do_c:
            cover_room = next(r for r in sorted(CANONICAL_ROOMS) if r != ctx.kill_room)
            t1, t2 = max(0, ctx.kill_tick - 2), ctx.kill_tick + 2
            cover_memory = (
                ctx.rendered_memory
                + f"\n\n[COVER STORY — your prepared account if asked: you were doing the wiring task in {cover_room} from tick {t1} to tick {t2}. Use it naturally.]"
            )
            c_prompt = impostor_report_prompt(
                agent_id=ctx.killer,
                current_tick=ctx.trigger_tick,
                meeting_trigger=ctx.trigger_description,
                rendered_memory=cover_memory,
                public_transcript="",
                fellow_impostor_ids=ctx.fellow_living,
                living_ids=tuple(p for p in ctx.living if p != ctx.killer),
                dead_ids=tuple(ctx.dead),
            )
            c_turn, c_raw, c_lat = await _call(c_prompt)
            rec3 = {
                "probe": "C",
                "item": ctx.item_id,
                "parsed_ok": c_turn is not None,
                "latency_s": round(c_lat, 1),
            }
            if c_turn is not None:
                rec3.update(_grade_fabrication(c_turn, ctx, cover=(cover_room, t1, t2)))
                rec3["free_text"] = (c_turn.free_text or "")[:400]
            _emit(sink, rec3)
        print(f"  A/A2/C item {n + 1}/{len(ctxs)}", flush=True)


async def probe_b(ctxs: list[ReplyContext], *, sink: TextIO) -> None:
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
        turn, raw, latency = await _call(prompt)
        rec = {
            "probe": "B",
            "item": ctx.item_id,
            "parsed_ok": turn is not None,
            "latency_s": round(latency, 1),
            "recorded_counter": ctx.recorded_counter_accused,
        }
        if turn is not None:
            counters = [c for c in turn.claims if isinstance(c, AccusationClaim)]
            counter_ids = [c.against for c in counters if c.against != ctx.speaker]
            text = (turn.free_text or "").lower()
            n_prior = len(ctx.transcript.turns)
            reply = _envelope(
                turn,
                index=n_prior,
                meeting=ctx.meeting_id,
                speaker=ctx.speaker,
                kind="reply",
                reply_to=ctx.prior_turn.turn_id if ctx.prior_turn else None,
            )
            self_flags = _flags_on(
                MeetingTranscript(turns=tuple(ctx.transcript.turns) + (reply,)),
                frozenset(ctx.living),
                ctx.speaker,
            )
            base_flags = _flags_on(ctx.transcript, frozenset(ctx.living), ctx.speaker)
            agrees = (
                any(
                    a.room in ctx.accuser_room_claims
                    for a in _self_alibis(turn, ctx.speaker)
                )
                if ctx.accuser_room_claims
                else False
            )
            rec.update(
                {
                    "deflects": bool(counter_ids),
                    "counter_ids": counter_ids,
                    "counter_living": all(c in ctx.living for c in counter_ids)
                    if counter_ids
                    else None,
                    "counter_teammate": any(
                        c in ctx.fellow_living for c in counter_ids
                    ),
                    "self_accuses": any(c.against == ctx.speaker for c in counters),
                    "confesses": any(w in text for w in KILL_WORDS),
                    "confirms_accuser_room": agrees,
                    "new_self_flags": {
                        k: self_flags[k] - base_flags[k] for k in self_flags
                    },
                    "free_text": (turn.free_text or "")[:400],
                }
            )
        _emit(sink, rec)
        print(f"  B item {n + 1}/{len(ctxs)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-dir", type=Path, required=True)
    parser.add_argument(
        "--facts",
        type=Path,
        required=True,
        help="extractor facts JSON for this sample dir",
    )
    parser.add_argument("--probes", type=str, default="A,A2,B,C")
    parser.add_argument("--cap-a", type=int, default=18)
    parser.add_argument("--cap-a2", type=int, default=10)
    parser.add_argument("--cap-b", type=int, default=22)
    parser.add_argument("--cap-c", type=int, default=12)
    args = parser.parse_args()
    probes = {p.strip().upper() for p in args.probes.split(",")}

    preflight((MODEL,))
    out_path = RESULTS / "results-deception-battery.jsonl"
    kill_ctxs = (
        build_kill_contexts(args.sample_dir, args.facts, args.cap_a)
        if probes & {"A", "A2", "C"}
        else []
    )
    reply_ctxs = (
        build_reply_contexts(args.sample_dir, args.cap_b) if "B" in probes else []
    )
    print(
        f"contexts: A/{len(kill_ctxs)} (A2 first {args.cap_a2}, C first {args.cap_c}), B/{len(reply_ctxs)}",
        flush=True,
    )

    async def _run() -> None:
        with out_path.open("w", encoding="utf-8") as sink:
            if kill_ctxs:
                await probe_a_and_c(
                    kill_ctxs,
                    sink=sink,
                    do_a2=args.cap_a2 if "A2" in probes else 0,
                    do_c=args.cap_c if "C" in probes else 0,
                )
            if reply_ctxs:
                await probe_b(reply_ctxs, sink=sink)

    asyncio.run(_run())
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
