"""Deterministic Extract phase of the gameplay-data audit.

Re-derives ground-truth roles (firewalled OUT of the replays) by re-seeding the
engine, re-runs the recorded action stream through ``engine.tick.advance_tick``
(mirroring ``api.replay_loader.ReplayLoader._walk``) so the engine itself
surfaces resolved events (Killed actor/target/room, ActionRejected, Moved,
MeetingTriggered, GameOver), then emits a structured FACTS JSON plus
code-certain HARD rule-violation findings.

Because ``advance_tick`` ENFORCES every hard rule (impostor-only kill, cooldown,
same-room kill, adjacency move, alive-player gate, eligible reporter) by emitting
an ``ActionRejectedEvent`` and NOT applying the offending action, a rule-breaking
action in the recorded stream becomes a rejection — and the rejection's reason is
the code-certain classifier. We additionally re-derive each Killed event's
victim role from the re-seeded roster to catch impostor-on-impostor kills.

v2 (Phase-8 / 9p2i set): meetings are the turns-based accusation chain
(DESIGN.md §5.2; Task 8.7 ``MeetingTranscript.turns``). For every meeting this
script re-walks the recorded chain against the deterministic 3-condition
termination rule (``meetings.transcript.next_chain_step``), re-derives the
opt-in eligibility gate (``meetings.manager._opt_in_eligible_ids``), and
emits per-meeting chain facts (turn-kind counts, chain length, termination
condition, accusations with re-seeded roles, opt-in substance, ballots with
``primary_reason_id`` linkage) plus chain-protocol mechanical checks
(termination / turn-id-order / reply_to / opt-in containment / 7.12 firewall /
dangling primary_reason_id / dead speakers-voters).

Usage:
    PYTHONPATH=<repo root> uv run python audits/workflows/extract_gameplay_facts.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from engine.actions import Action
from engine.events import (
    ActionRejectedEvent,
    KilledEvent,
    MeetingTriggeredEvent,
)
from engine.tick import advance_tick
from engine.world import load_canonical_map
from meetings.manager import _opt_in_eligible_ids
from meetings.schemas import AccusationClaim, MeetingResult, MeetingTranscript, TurnKind
from meetings.transcript import is_canonically_ordered, next_chain_step
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPO_ROOT / "replays" / "samples" / "9p2i"
SEEDSET = "9p2i"

# Action adapter for deserializing recorded raw actions.
_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _deserialize_actions(raw_actions: list[dict[str, Any]]) -> list[Action]:
    return [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in raw_actions]


def _git_head() -> str:
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def _classify_rejection(reason: str) -> str | None:
    """Map an ActionRejected reason to a HARD-rule category, or None.

    Only reasons that correspond to a *hard rule violation in the recorded
    stream* (the producer queued an action the engine had to refuse) are
    classified. Reasons that are normal contention (e.g. a stale do_task whose
    room changed) are not hard violations and return None.
    """

    r = reason.lower()
    if "player is dead" in r or "unknown player" in r:
        return "dead_or_unknown_player_action"
    if "only impostors can kill" in r:
        return "non_impostor_kill"
    if "kill is on cooldown" in r:
        return "kill_ignored_cooldown"
    if "kill requires same room" in r:
        return "kill_cross_room"
    if "move destination must be current or adjacent" in r:
        return "move_non_adjacent"
    if "unknown destination room" in r:
        return "move_unknown_room"
    if "report requires actor and body in same room" in r:
        return "report_ineligible_room"
    if "unknown body id" in r:
        return "report_unknown_body"
    return None


def _analyze_meeting(
    *,
    seed: int,
    meeting_index: int,
    meeting_entry: MeetingReplayEntry,
    trigger_kind: str | None,
    roles: Mapping[str, str],
    living_ids: frozenset[str],
    findings: list[dict[str, Any]],
    invariant_failures: list[str],
) -> dict[str, Any]:
    """Per-meeting chain facts + chain-protocol mechanical checks (v2).

    Re-walks the recorded ``transcript.turns`` against the deterministic
    DESIGN.md §5.2 PHASE-2 rule (via ``meetings.transcript.next_chain_step``)
    to re-derive the termination condition, re-derives the PHASE-3 opt-in
    eligibility gate, and emits one mechanical finding per code-certain
    protocol violation. ``living_ids`` is the alive-player set of the
    reconstructed state at the meeting tick (== the participant roster the
    manager ran with: ``orchestrator.game._build_participants`` builds one
    participant per living player).
    """

    mid = meeting_entry.meeting_id
    where = f"seed {seed} meeting {meeting_index} ({mid})"
    turns = meeting_entry.transcript.turns
    turn_id_set = {t.turn_id for t in turns}
    turn_by_id = {t.turn_id: t for t in turns}

    # ---- ADDED invariant: non-empty transcript, exactly one opening at 0 ----
    opening_positions = [i for i, t in enumerate(turns) if t.turn_kind == "opening"]
    if not turns:
        invariant_failures.append(f"{where}: transcript.turns is empty")
    elif opening_positions != [0]:
        invariant_failures.append(
            f"{where}: opening turns at positions {opening_positions}, "
            "expected exactly one opening at position 0"
        )

    # ---- TURN-ID / ORDER mechanical checks ----
    canonical = bool(is_canonically_ordered(turns))
    for i, t in enumerate(turns):
        problems: list[str] = []
        if t.turn_index != i:
            problems.append(f"turn_index {t.turn_index} at tuple position {i}")
        expected_id = f"{mid}:turn-{t.turn_index}"
        if t.turn_id != expected_id:
            problems.append(f"turn_id {t.turn_id!r} != expected {expected_id!r}")
        if i == 0 and t.turn_kind != "opening":
            problems.append(f"turn 0 has turn_kind {t.turn_kind!r}, not 'opening'")
        if i > 0 and t.turn_kind == "opening":
            problems.append(f"extra 'opening' turn at position {i}")
        if problems:
            findings.append(
                {
                    "id": f"TURNORD-{seed}-{meeting_index}-{i}",
                    "severity": "high",
                    "title": "Turn-id/order violation in meeting transcript",
                    "claim": (
                        "A recorded turn breaks the contiguous turn_index / "
                        "'{meeting_id}:turn-{index}' turn_id / opening-at-0 "
                        "contract: " + "; ".join(problems) + "."
                    ),
                    "evidence": (
                        f"{where} turn {i}: speaker {t.speaker} "
                        f"({roles.get(t.speaker, 'UNKNOWN')}); " + "; ".join(problems)
                    ),
                    "repair_hint": (
                        "meetings/manager.py assigns turn_index=len(turns) and "
                        "turn_id='{meeting_id}:turn-{N}' at the single "
                        "_collect_turn chokepoint; trace how this record "
                        "bypassed it (or how the replay row was mutated)."
                    ),
                }
            )

    # ---- REPLY_TO integrity mechanical checks ----
    for i, t in enumerate(turns):
        if t.turn_kind == "reply":
            earlier_ids = {u.turn_id for u in turns[:i]}
            if t.reply_to is None or t.reply_to not in earlier_ids:
                findings.append(
                    {
                        "id": f"REPLYTO-{seed}-{meeting_index}-{i}",
                        "severity": "high",
                        "title": "Reply turn's reply_to is not an earlier turn",
                        "claim": (
                            "A reply turn must reference an EARLIER turn_id of "
                            f"this meeting; got reply_to={t.reply_to!r}."
                        ),
                        "evidence": (
                            f"{where} turn {i}: reply by {t.speaker} "
                            f"({roles.get(t.speaker, 'UNKNOWN')}) has "
                            f"reply_to={t.reply_to!r}; earlier turn ids: "
                            f"{sorted(earlier_ids)}"
                        ),
                        "repair_hint": (
                            "The manager sets reply_to=prev.turn_id when "
                            "passing the chain; a dangling/forward reference "
                            "means the transcript was assembled out of band."
                        ),
                    }
                )
        elif t.reply_to is not None:
            findings.append(
                {
                    "id": f"REPLYTO-{seed}-{meeting_index}-{i}",
                    "severity": "high",
                    "title": f"Non-reply turn carries a reply_to ({t.turn_kind})",
                    "claim": (
                        "opening and opt_in turns must have reply_to=None "
                        f"(got {t.reply_to!r})."
                    ),
                    "evidence": (
                        f"{where} turn {i}: turn_kind={t.turn_kind!r} by "
                        f"{t.speaker} ({roles.get(t.speaker, 'UNKNOWN')}) has "
                        f"reply_to={t.reply_to!r}"
                    ),
                    "repair_hint": (
                        "meetings/manager.py passes reply_to=None for opening "
                        "and opt_in turns; check the turn-construction path."
                    ),
                }
            )

    # ---- TERMINATION re-walk (DESIGN.md §5.2 PHASE 2, deterministic) ----
    chain_len = 0
    termination: str | None = None
    walk_idx = len(turns)
    if turns:
        chain = [turns[0]]
        spoken: set[str] = {turns[0].speaker}
        prev = turns[0]
        idx = 1
        while True:
            step = next_chain_step(
                prev_turn=prev,
                spoken=frozenset(spoken),
                living_ids=living_ids,
                turns_recorded=len(chain),
            )
            if step.next_speaker is None:
                termination = step.termination
                break
            if idx >= len(turns) or turns[idx].turn_kind != "reply":
                recorded = (
                    f"turn_kind={turns[idx].turn_kind!r} by {turns[idx].speaker}"
                    if idx < len(turns)
                    else "absent (transcript ends)"
                )
                findings.append(
                    {
                        "id": f"TERM-{seed}-{meeting_index}-{idx}",
                        "severity": "high",
                        "title": (
                            "Chain stopped while no termination condition had fired"
                        ),
                        "claim": (
                            "The §5.2 three-condition rule predicts a reply by "
                            f"{step.next_speaker!r} at turn {idx}, but the "
                            "recorded chain stops there with no condition "
                            "(a)/(b)/(c) fired."
                        ),
                        "evidence": (
                            f"{where} turn {idx}: predicted next speaker "
                            f"{step.next_speaker} "
                            f"({roles.get(step.next_speaker, 'UNKNOWN')}); "
                            f"recorded turn is {recorded}"
                        ),
                        "repair_hint": (
                            "meetings/manager.py PHASE-2 loop and "
                            "meetings/transcript.py::next_chain_step must agree; "
                            "a chain that stops early without a recorded reason "
                            "means the manager broke out of the loop on a "
                            "non-rule condition (e.g. the 7.12 guarded_next "
                            "no-op firing for real)."
                        ),
                    }
                )
                break
            t = turns[idx]
            if t.speaker != step.next_speaker:
                findings.append(
                    {
                        "id": f"TERM-{seed}-{meeting_index}-{idx}-speaker",
                        "severity": "high",
                        "title": (
                            "Reply speaker diverges from the deterministic chain"
                        ),
                        "claim": (
                            "The accusation chain passes the floor to the "
                            f"accused ({step.next_speaker!r}), but the recorded "
                            f"reply is by {t.speaker!r}."
                        ),
                        "evidence": (
                            f"{where} turn {idx}: recorded speaker {t.speaker} "
                            f"({roles.get(t.speaker, 'UNKNOWN')}), predicted "
                            f"{step.next_speaker} "
                            f"({roles.get(step.next_speaker, 'UNKNOWN')})"
                        ),
                        "repair_hint": (
                            "next-speaker is a pure function of the prior "
                            "turn's first AccusationClaim; divergence means a "
                            "non-deterministic / corrupted record."
                        ),
                    }
                )
            if t.reply_to != prev.turn_id:
                findings.append(
                    {
                        "id": f"TERM-{seed}-{meeting_index}-{idx}-link",
                        "severity": "high",
                        "title": (
                            "Chain reply links to a turn other than the prior "
                            "chain turn"
                        ),
                        "claim": (
                            "Each chain reply must answer the immediately "
                            f"prior chain turn ({prev.turn_id!r}); got "
                            f"{t.reply_to!r}."
                        ),
                        "evidence": (
                            f"{where} turn {idx}: reply by {t.speaker} "
                            f"({roles.get(t.speaker, 'UNKNOWN')}) reply_to="
                            f"{t.reply_to!r}, expected {prev.turn_id!r}"
                        ),
                        "repair_hint": (
                            "meetings/transcript.py::walk_chain enforces "
                            "reply_to == prev.turn_id; check the manager's "
                            "reply_to wiring."
                        ),
                    }
                )
            chain.append(t)
            spoken.add(t.speaker)
            prev = t
            idx += 1
        chain_len = len(chain)
        walk_idx = idx

        # Turns after the walked chain: replies are violations (continued past
        # termination, or after a terminal opt_in); opt_ins must be by
        # first-time speakers.
        seen_opt_in = False
        earlier_speakers = {t.speaker for t in chain}
        for j in range(walk_idx, len(turns)):
            t = turns[j]
            if t.turn_kind == "reply":
                if seen_opt_in:
                    findings.append(
                        {
                            "id": f"OPTIN-{seed}-{meeting_index}-{j}",
                            "severity": "high",
                            "title": "Reply turn after a terminal opt_in turn",
                            "claim": (
                                "opt_in turns are terminal and cannot extend "
                                "the chain, but a reply was recorded after an "
                                "opt_in."
                            ),
                            "evidence": (
                                f"{where} turn {j}: reply by {t.speaker} "
                                f"({roles.get(t.speaker, 'UNKNOWN')}) after the "
                                "first opt_in turn"
                            ),
                            "repair_hint": (
                                "PHASE 3 opt-ins never re-enter PHASE 2; check "
                                "the manager's phase ordering."
                            ),
                        }
                    )
                elif termination is not None:
                    findings.append(
                        {
                            "id": f"TERM-{seed}-{meeting_index}-{j}-past",
                            "severity": "high",
                            "title": ("Chain continued past its termination condition"),
                            "claim": (
                                f"Termination condition {termination!r} fired "
                                f"after turn {walk_idx - 1}, but a reply was "
                                f"recorded at turn {j}."
                            ),
                            "evidence": (
                                f"{where} turn {j}: reply by {t.speaker} "
                                f"({roles.get(t.speaker, 'UNKNOWN')}) after "
                                f"termination {termination!r}"
                            ),
                            "repair_hint": (
                                "The §5.2 rule is deterministic; a reply past "
                                "the fired condition means the manager and "
                                "next_chain_step disagree."
                            ),
                        }
                    )
            elif t.turn_kind == "opt_in":
                seen_opt_in = True
                if t.speaker in earlier_speakers:
                    findings.append(
                        {
                            "id": f"OPTIN-{seed}-{meeting_index}-{j}-respoke",
                            "severity": "high",
                            "title": ("opt_in by a player who already took a turn"),
                            "claim": (
                                "Opt-in eligibility requires NOT having spoken "
                                f"this meeting, but {t.speaker!r} already took "
                                "a turn."
                            ),
                            "evidence": (
                                f"{where} turn {j}: opt_in by {t.speaker} "
                                f"({roles.get(t.speaker, 'UNKNOWN')}) who "
                                "already spoke"
                            ),
                            "repair_hint": (
                                "meetings/manager.py::_opt_in_eligible_ids "
                                "filters spoken players; check the spoken-set "
                                "bookkeeping."
                            ),
                        }
                    )
            earlier_speakers.add(t.speaker)

    # ---- Opt-in eligibility re-derivation (deterministic PHASE-3 gate) ----
    structural_chain_end = next(
        (i for i, t in enumerate(turns) if t.turn_kind == "opt_in"), len(turns)
    )
    post_chain = MeetingTranscript(turns=tuple(turns[:structural_chain_end]))
    derived_eligible = _opt_in_eligible_ids(
        transcript=post_chain,
        spoken=frozenset(t.speaker for t in turns[:structural_chain_end]),
        living_ids=living_ids,
    )
    recorded_opt_in_speakers = tuple(
        t.speaker for t in turns[structural_chain_end:] if t.turn_kind == "opt_in"
    )
    if recorded_opt_in_speakers != derived_eligible:
        findings.append(
            {
                "id": f"OPTIN-{seed}-{meeting_index}-eligibility",
                "severity": "high",
                "title": (
                    "Recorded opt_in speakers diverge from the deterministic "
                    "eligibility gate"
                ),
                "claim": (
                    "PHASE-3 eligibility is a pure function of the post-chain "
                    "transcript (co-presence with body room / accused), and "
                    "every eligible player takes exactly one terminal turn; "
                    "the recorded opt_in speakers do not match."
                ),
                "evidence": (
                    f"{where}: recorded opt_in speakers "
                    f"{list(recorded_opt_in_speakers)} vs derived eligible "
                    f"{list(derived_eligible)}"
                ),
                "repair_hint": (
                    "Re-run meetings/manager.py::_opt_in_eligible_ids on the "
                    "post-chain transcript; divergence means the recorded "
                    "transcript was not produced by the committed gate."
                ),
            }
        )

    # ---- Accusations (all turn kinds), 7.12 firewall, dead speakers ----
    accusations: list[dict[str, Any]] = []
    for t in turns:
        speaker_role = roles.get(t.speaker, "UNKNOWN")
        if t.speaker not in living_ids:
            findings.append(
                {
                    "id": f"DEADSPK-{seed}-{meeting_index}-{t.turn_index}",
                    "severity": "blocking",
                    "title": "Turn spoken by a player dead at the meeting tick",
                    "claim": (
                        "Meeting participants are the living players at the "
                        "meeting tick; a dead player took a turn."
                    ),
                    "evidence": (
                        f"{where} turn {t.turn_index}: speaker {t.speaker} "
                        f"({speaker_role}) is not alive at tick "
                        f"{meeting_entry.tick} "
                        f"(turn_kind={t.turn_kind!r})"
                    ),
                    "repair_hint": (
                        "orchestrator.game._build_participants gates on "
                        "p.alive; a dead speaker means participants were built "
                        "from a stale state."
                    ),
                }
            )
        for c in t.claims:
            if not isinstance(c, AccusationClaim):
                continue
            accused_role = roles.get(c.against, "UNKNOWN")
            accusations.append(
                {
                    "turn_index": t.turn_index,
                    "speaker": t.speaker,
                    "speaker_role": speaker_role,
                    "accused": c.against,
                    "accused_role": accused_role,
                }
            )
            if (
                speaker_role == "IMPOSTOR"
                and accused_role == "IMPOSTOR"
                and c.against != t.speaker
            ):
                findings.append(
                    {
                        "id": f"FIREWALL-{seed}-{meeting_index}-{t.turn_index}",
                        "severity": "blocking",
                        "title": (
                            "Impostor accusation names a fellow impostor "
                            "(7.12 firewall breach)"
                        ),
                        "claim": (
                            "The Task-7.12 teammate guard must drop an "
                            "impostor's accusation of a fellow impostor before "
                            "the turn is recorded; one survived."
                        ),
                        "evidence": (
                            f"{where} turn {t.turn_index} "
                            f"({t.turn_kind}): {t.speaker} (IMPOSTOR) accused "
                            f"{c.against} (IMPOSTOR)"
                        ),
                        "repair_hint": (
                            "Check agents/strategic guard "
                            "drop_teammate_statement_target wiring at the "
                            "manager's per-turn claim chokepoint."
                        ),
                    }
                )

    opt_ins = [
        {
            "turn_index": t.turn_index,
            "speaker": t.speaker,
            "speaker_role": roles.get(t.speaker, "UNKNOWN"),
            "substantive": bool(t.observations or t.claims),
        }
        for t in turns
        if t.turn_kind == "opt_in"
    ]

    # ---- Ballots: roles, skip, follows-chain, dangling reason, firewall ----
    ejected_id = meeting_entry.ejected_player_id
    ejected_role = roles.get(ejected_id) if ejected_id is not None else None
    ballots_out: list[dict[str, Any]] = []
    skip_count = 0
    for b in meeting_entry.ballots:
        voter_role = roles.get(b.voter, "UNKNOWN")
        is_skip = b.target == "SKIP"
        target_role = None if is_skip else roles.get(b.target, "UNKNOWN")
        follows_chain: bool | None = None
        if is_skip:
            skip_count += 1
        else:
            follows_chain = False
            if b.primary_reason_id is not None and b.primary_reason_id in turn_by_id:
                cited = turn_by_id[b.primary_reason_id]
                follows_chain = any(
                    isinstance(c, AccusationClaim) and c.against == b.target
                    for c in cited.claims
                )
        if b.primary_reason_id is not None and b.primary_reason_id not in turn_id_set:
            findings.append(
                {
                    "id": f"DANGLEREASON-{seed}-{meeting_index}-{b.voter}",
                    "severity": "high",
                    "title": (
                        "Ballot primary_reason_id references a turn that does not exist"
                    ),
                    "claim": (
                        "primary_reason_id must reference a MeetingTurn "
                        "turn_id from this meeting's transcript; the recorded "
                        "id is dangling."
                    ),
                    "evidence": (
                        f"{where}: ballot by {b.voter} ({voter_role}) cites "
                        f"{b.primary_reason_id!r}; transcript turn ids are "
                        f"{sorted(turn_id_set)}"
                    ),
                    "repair_hint": (
                        "The vote-ballot prompt enumerates turn ids; a "
                        "hallucinated id should be normalised or rejected at "
                        "parse time."
                    ),
                }
            )
        if b.voter not in living_ids:
            invariant_failures.append(
                f"{where}: ballot voter {b.voter} is not alive at the "
                f"meeting tick {meeting_entry.tick}"
            )
            findings.append(
                {
                    "id": f"DEADVOTE-{seed}-{meeting_index}-{b.voter}",
                    "severity": "blocking",
                    "title": "Ballot cast by a player dead at the meeting tick",
                    "claim": (
                        "Only living participants vote; a dead player's ballot "
                        "was recorded."
                    ),
                    "evidence": (
                        f"{where}: voter {b.voter} ({voter_role}) is not alive "
                        f"at tick {meeting_entry.tick}"
                    ),
                    "repair_hint": (
                        "orchestrator.game._build_participants gates on "
                        "p.alive; a dead voter means ballots were collected "
                        "from a stale roster."
                    ),
                }
            )
        if (
            voter_role == "IMPOSTOR"
            and not is_skip
            and roles.get(b.target) == "IMPOSTOR"
            and b.target != b.voter
        ):
            findings.append(
                {
                    "id": f"FIREWALL-BALLOT-{seed}-{meeting_index}-{b.voter}",
                    "severity": "blocking",
                    "title": (
                        "Impostor ballot targets a fellow impostor "
                        "(7.12 firewall breach)"
                    ),
                    "claim": (
                        "The teammate firewall must keep an impostor from "
                        "voting out a fellow impostor; one ballot breached it."
                    ),
                    "evidence": (
                        f"{where}: ballot by {b.voter} (IMPOSTOR) targets "
                        f"{b.target} (IMPOSTOR)"
                    ),
                    "repair_hint": (
                        "Check the vote-path teammate guard "
                        "(drop_teammate_ballot_target / equivalent) on the "
                        "ballot chokepoint."
                    ),
                }
            )
        ballots_out.append(
            {
                "voter": b.voter,
                "voter_role": voter_role,
                "target": b.target,
                "target_role": target_role,
                "primary_reason_id": b.primary_reason_id,
                "follows_chain": follows_chain,
            }
        )

    kind_counts = Counter(t.turn_kind for t in turns)
    turn_kinds: tuple[TurnKind, ...] = ("opening", "reply", "opt_in")
    return {
        "meeting_id": mid,
        "meeting_index": meeting_index,
        "tick": meeting_entry.tick,
        "trigger_kind": trigger_kind,
        "triggered_by": meeting_entry.triggered_by,
        "triggered_by_role": roles.get(meeting_entry.triggered_by, "UNKNOWN"),
        "outcome": meeting_entry.outcome,
        "ejected_player_id": ejected_id,
        "ejected_role": ejected_role,
        "living_player_count": len(living_ids),
        "n_turns": len(turns),
        "turn_kind_counts": {k: kind_counts.get(k, 0) for k in turn_kinds},
        "chain_length": chain_len,
        "termination_condition": termination,
        "is_canonically_ordered": canonical,
        "opening_has_accusation": (
            any(isinstance(c, AccusationClaim) for c in turns[0].claims)
            if turns
            else False
        ),
        "accusations": accusations,
        "opt_ins": opt_ins,
        "opt_in_eligible_derived": list(derived_eligible),
        "ballots": ballots_out,
        "skip_count": skip_count,
        "n_contradictions": len(meeting_entry.contradictions),
    }


def main() -> int:
    game_map = load_canonical_map()
    roster = json.loads((SAMPLE_DIR / "roster.json").read_text(encoding="utf-8"))
    num_players = int(roster["num_players"])
    num_impostors = int(roster["num_impostors"])
    tasks_per_crewmate = int(roster["tasks_per_crewmate"])

    replay_paths = sorted(
        SAMPLE_DIR.glob("replay-seed-*.jsonl"),
        key=lambda p: int(p.stem.rsplit("-", 1)[1]),
    )
    games_analyzed = len(replay_paths)

    games: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    # Self-check accumulators.
    total_meeting_records = 0
    invariant_failures: list[str] = []

    # Aggregates.
    win_split: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    total_kills = 0
    impostor_victim_kills = 0
    total_meetings = 0
    ejections_by_role: dict[str, int] = {}
    total_calls = 0
    total_failed_calls = 0
    agg_input_tokens = 0
    agg_output_tokens = 0
    agg_cost = 0.0
    no_game_over = 0
    # v2 chain/ballot aggregates.
    trigger_kind_counts: dict[str, int] = {}
    total_ballots = 0
    total_skip_ballots = 0
    chain_length_hist: dict[str, int] = {}
    termination_counts: dict[str, int] = {}
    opening_accusation_count = 0
    accusations_total = 0
    accusations_at_impostors = 0
    accusations_at_innocents = 0
    self_accusations = 0
    accusations_at_unknown = 0
    opt_in_turns_total = 0
    opt_in_substantive = 0
    opt_in_eligible_total = 0
    ballots_non_skip = 0
    ballots_follow_chain = 0
    ballots_non_skip_null_reason = 0
    total_contradictions = 0

    for path in replay_paths:
        seed = int(path.stem.rsplit("-", 1)[1])
        game_id = f"headless-seed-{seed}"

        # 1) Ground-truth roles.
        init_state = seed_initial_state(
            seed=seed,
            game_map=game_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        roles = {pid: p.role for pid, p in init_state.players.items()}
        found_impostors = sum(1 for r in roles.values() if r == "IMPOSTOR")
        if found_impostors != num_impostors:
            invariant_failures.append(
                f"seed {seed}: found {found_impostors} impostors, "
                f"roster says {num_impostors}"
            )

        # 2) Reconstruct resolved events by re-running the engine.
        entries = read_all_entries(path)
        replay_entries = [e for e in entries if isinstance(e, ReplayEntry)]
        meeting_entries = [e for e in entries if isinstance(e, MeetingReplayEntry)]
        failed_call_entries = [
            e for e in entries if isinstance(e, FailedCallReplayEntry)
        ]
        game_end = next((e for e in entries if isinstance(e, GameEndReplayEntry)), None)
        meeting_by_tick = {e.tick: e for e in meeting_entries}
        total_meeting_records += len(meeting_entries)

        kills: list[dict[str, Any]] = []
        deaths: set[str] = set()
        meetings_out: list[dict[str, Any]] = []
        # Win-condition-gap tracking: the first tick at which alive impostors hit 0.
        first_zero_impostor_tick: int | None = None

        state = init_state
        last_state_for_final = state
        meeting_index = 0

        for entry in replay_entries:
            actions = _deserialize_actions(list(entry.actions))
            state, events = advance_tick(state, actions, game_map=game_map)

            # State-hash self-check (replay determinism; the whole audit trusts
            # this reconstruction).
            actual = _state_hash(state)
            if actual != entry.state_hash:
                invariant_failures.append(
                    f"seed {seed} tick {entry.tick}: state-hash mismatch "
                    f"(recorded {entry.state_hash[:12]}, "
                    f"reconstructed {actual[:12]})"
                )

            for ev in events:
                if isinstance(ev, KilledEvent):
                    victim_role = roles.get(ev.target, "UNKNOWN")
                    killer_role = roles.get(ev.actor, "UNKNOWN")
                    kills.append(
                        {
                            "tick": ev.tick,
                            "killer": ev.actor,
                            "killer_role": killer_role,
                            "victim": ev.target,
                            "victim_role": victim_role,
                            "room": ev.room,
                        }
                    )
                    deaths.add(ev.target)
                    total_kills += 1
                    if victim_role == "IMPOSTOR":
                        impostor_victim_kills += 1
                        findings.append(
                            {
                                "id": f"KILL-IMP-{seed}-{ev.tick}",
                                "severity": "blocking",
                                "title": "Impostor killed a fellow impostor",
                                "claim": (
                                    "A resolved kill has victim_role==IMPOSTOR — an "
                                    "impostor was killed by another player, which "
                                    "the engine should never produce in a normal game."
                                ),
                                "evidence": (
                                    f"seed {seed} tick {ev.tick}: {ev.actor} "
                                    f"({killer_role}) killed {ev.target} (IMPOSTOR) "
                                    f"in {ev.room}"
                                ),
                                "repair_hint": (
                                    "Inspect engine.rules.resolve_kill / the agent "
                                    "target selection that produced an impostor-on-"
                                    "impostor kill; confirm role-aware target "
                                    "filtering for impostor kill intents."
                                ),
                            }
                        )
                elif isinstance(ev, ActionRejectedEvent):
                    category = _classify_rejection(ev.reason)
                    if category is not None:
                        # Severity: dead/unknown-player rejections are downstream
                        # symptoms of same-tick kill races (the actor died earlier
                        # in this tick's action ordering) — informational, not an
                        # independent hard violation. Cross-room / non-adjacent /
                        # ineligible-report are intent-generation waste -> high.
                        if category == "dead_or_unknown_player_action":
                            sev = "informational"
                        else:
                            sev = "high"
                        findings.append(
                            {
                                "id": f"REJ-{category}-{seed}-{ev.tick}",
                                "severity": sev,
                                "title": (
                                    f"Recorded action rejected by engine ({category})"
                                ),
                                "claim": (
                                    "The recorded action stream queued an action the "
                                    "engine refused: "
                                    f"{ev.reason!r}."
                                ),
                                "evidence": (
                                    f"seed {seed} tick {ev.tick}: actor {ev.actor} "
                                    f"({roles.get(ev.actor, 'UNKNOWN')}) action "
                                    f"{ev.action!r} rejected: {ev.reason!r}"
                                ),
                                "repair_hint": (
                                    "Trace the agent/orchestrator path that emitted "
                                    "this action; a producer that queues "
                                    "engine-illegal actions wastes a turn (the agent "
                                    "no-ops) and signals an intent-generation bug."
                                ),
                            }
                        )

            # Track alive impostors AFTER this tick resolved.
            alive_impostors = sum(
                1
                for pid, p in state.players.items()
                if p.alive and roles.get(pid) == "IMPOSTOR"
            )
            if alive_impostors == 0 and first_zero_impostor_tick is None:
                first_zero_impostor_tick = entry.tick

            last_state_for_final = state

            if state.phase == "GAME_OVER":
                break

            if state.phase != "MEETING":
                continue

            # Meeting resolved this tick.
            meeting_entry = meeting_by_tick.get(entry.tick)
            if meeting_entry is None:
                # Partial replay (meeting opened, never resolved). Stop the walk.
                break

            # Trigger body id (for corpse consumption) + trigger kind.
            body_id: str | None = None
            trigger_kind: str | None = None
            for ev in events:
                if isinstance(ev, MeetingTriggeredEvent):
                    body_id = ev.body_id
                    trigger_kind = ev.trigger

            # Schema-verified against meetings/schemas.py::MeetingResult
            # (Task 8.7 shape): meeting_id, triggered_by,
            # trigger_tick<-entry.tick, outcome, ejected_player_id, ballots,
            # contradictions, transcript (turns-based MeetingTranscript).
            # Mirrors api.replay_loader._meeting_result_from_entry.
            result = MeetingResult(
                meeting_id=meeting_entry.meeting_id,
                triggered_by=meeting_entry.triggered_by,
                trigger_tick=meeting_entry.tick,
                outcome=meeting_entry.outcome,
                ejected_player_id=meeting_entry.ejected_player_id,
                ballots=meeting_entry.ballots,
                contradictions=meeting_entry.contradictions,
                transcript=meeting_entry.transcript,
            )

            # Cheap cross-check: the recorded pre-meeting hash must equal this
            # tick's recorded post-tick hash (the state the meeting ran on).
            if meeting_entry.state_hash_before != entry.state_hash:
                invariant_failures.append(
                    f"seed {seed} meeting {meeting_entry.meeting_id}: "
                    "state_hash_before does not match the trigger tick's "
                    "state_hash"
                )

            # Living players at the meeting tick == the participant roster
            # (one MeetingParticipant per living player).
            living_ids = frozenset(pid for pid, p in state.players.items() if p.alive)

            m_facts = _analyze_meeting(
                seed=seed,
                meeting_index=meeting_index,
                meeting_entry=meeting_entry,
                trigger_kind=trigger_kind,
                roles=roles,
                living_ids=living_ids,
                findings=findings,
                invariant_failures=invariant_failures,
            )
            meetings_out.append(m_facts)
            total_meetings += 1

            # v2 aggregates from the per-meeting facts.
            if trigger_kind is not None:
                trigger_kind_counts[trigger_kind] = (
                    trigger_kind_counts.get(trigger_kind, 0) + 1
                )
            total_ballots += len(m_facts["ballots"])
            total_skip_ballots += m_facts["skip_count"]
            chain_key = str(m_facts["chain_length"])
            chain_length_hist[chain_key] = chain_length_hist.get(chain_key, 0) + 1
            term_key = m_facts["termination_condition"] or "VIOLATION_UNDETERMINED"
            termination_counts[term_key] = termination_counts.get(term_key, 0) + 1
            if m_facts["opening_has_accusation"]:
                opening_accusation_count += 1
            for acc in m_facts["accusations"]:
                accusations_total += 1
                if acc["accused"] == acc["speaker"]:
                    self_accusations += 1
                elif acc["accused_role"] == "IMPOSTOR":
                    accusations_at_impostors += 1
                elif acc["accused_role"] == "CREWMATE":
                    accusations_at_innocents += 1
                else:
                    accusations_at_unknown += 1
            opt_in_turns_total += len(m_facts["opt_ins"])
            opt_in_substantive += sum(1 for o in m_facts["opt_ins"] if o["substantive"])
            opt_in_eligible_total += len(m_facts["opt_in_eligible_derived"])
            for b in m_facts["ballots"]:
                if b["target"] == "SKIP":
                    continue
                ballots_non_skip += 1
                if b["follows_chain"] is True:
                    ballots_follow_chain += 1
                if b["primary_reason_id"] is None:
                    ballots_non_skip_null_reason += 1
            total_contradictions += m_facts["n_contradictions"]

            ejected_id = meeting_entry.ejected_player_id
            ejected_role = roles.get(ejected_id) if ejected_id is not None else None
            if ejected_id is not None and ejected_role is not None:
                ejections_by_role[ejected_role] = (
                    ejections_by_role.get(ejected_role, 0) + 1
                )

            # Per-call token totals from this meeting's llm_calls.
            for call in meeting_entry.llm_calls:
                total_calls += 1
                agg_input_tokens += call.input_tokens
                agg_output_tokens += call.output_tokens
                agg_cost += call.cost_usd

            state, post_events = apply_meeting_result(
                state,
                result,
                game_map=game_map,
                triggering_body_id=body_id,
            )
            after = _state_hash(state)
            if after != meeting_entry.state_hash_after:
                invariant_failures.append(
                    f"seed {seed} meeting {meeting_entry.meeting_id}: "
                    f"post-meeting state-hash mismatch"
                )
            meeting_index += 1

            # Re-track alive impostors after the ejection.
            alive_impostors = sum(
                1
                for pid, p in state.players.items()
                if p.alive and roles.get(pid) == "IMPOSTOR"
            )
            if alive_impostors == 0 and first_zero_impostor_tick is None:
                first_zero_impostor_tick = meeting_entry.tick

            last_state_for_final = state
            if state.phase == "GAME_OVER":
                break

        # Failed-call accounting (these carry burned tokens for the aborted run).
        failed_calls_out: list[dict[str, Any]] = []
        for fc in failed_call_entries:
            total_failed_calls += 1
            total_calls += 1
            agg_input_tokens += fc.input_tokens
            agg_output_tokens += fc.output_tokens
            agg_cost += fc.cost_usd
            failed_calls_out.append(
                {
                    "meeting_id": fc.meeting_id,
                    "tick": fc.tick,
                    "model": fc.model,
                    "error_type": fc.error_type,
                    "error_message": fc.error_message[:200],
                    "input_tokens": fc.input_tokens,
                    "output_tokens": fc.output_tokens,
                    "cost_usd": fc.cost_usd,
                }
            )

        # Recorded winner/reason from the game_end row (authoritative producer record).
        recorded_winner = game_end.winner if game_end is not None else None
        recorded_reason = game_end.reason if game_end is not None else None
        recorded_go_tick = game_end.tick if game_end is not None else None
        if game_end is None:
            no_game_over += 1
        else:
            win_split[recorded_winner or "NONE"] = (
                win_split.get(recorded_winner or "NONE", 0) + 1
            )
            if recorded_reason is not None:
                reason_counts[recorded_reason] = (
                    reason_counts.get(recorded_reason, 0) + 1
                )

        # --- Win-condition-gap check ---
        # If alive impostors hit 0 at tick T but the game's recorded game_over
        # tick is strictly later, the game continued past the crew-win point.
        if (
            first_zero_impostor_tick is not None
            and recorded_go_tick is not None
            and recorded_go_tick > first_zero_impostor_tick
        ):
            findings.append(
                {
                    "id": f"WINGAP-{seed}",
                    "severity": "blocking",
                    "title": "Game continued past the tick alive impostors hit 0",
                    "claim": (
                        "Alive impostors reached 0 before the recorded game_over "
                        "tick — the game ran on past the crew-win point "
                        "(win-condition gap)."
                    ),
                    "evidence": (
                        f"seed {seed}: alive impostors hit 0 at tick "
                        f"{first_zero_impostor_tick}, but game_over recorded at tick "
                        f"{recorded_go_tick} ({recorded_winner}/{recorded_reason})"
                    ),
                    "repair_hint": (
                        "engine.win_conditions now has the alive_impostors==0 crew "
                        "win; verify the replay was recorded with that build."
                    ),
                }
            )

        # --- Recorded winner vs final reconstructed state cross-check ---
        # engine/win_conditions.py orders CREWMATE_EJECT (alive impostors == 0)
        # BEFORE the task check, and state.tasks already excludes dead owners'
        # incomplete instances, so done==total remains the valid task test.
        if game_end is not None:
            alive_players = [
                p for p in last_state_for_final.players.values() if p.alive
            ]
            alive_imp = sum(1 for p in alive_players if p.role == "IMPOSTOR")
            alive_crew = sum(1 for p in alive_players if p.role == "CREWMATE")
            total_tasks = len(last_state_for_final.tasks)
            done_tasks = sum(
                1 for t in last_state_for_final.tasks.values() if t.completed
            )
            mismatch_reason: str | None = None
            if recorded_reason == "CREWMATE_TASKS":
                if not (total_tasks > 0 and done_tasks == total_tasks):
                    mismatch_reason = (
                        f"CREWMATE_TASKS but tasks {done_tasks}/{total_tasks} done"
                    )
            elif recorded_reason == "CREWMATE_EJECT":
                if alive_imp != 0:
                    mismatch_reason = (
                        f"CREWMATE_EJECT but {alive_imp} impostor(s) alive"
                    )
            elif recorded_reason == "IMPOSTOR_PARITY":
                if not (alive_imp >= alive_crew):
                    mismatch_reason = (
                        f"IMPOSTOR_PARITY but alive imp {alive_imp} < crew {alive_crew}"
                    )
            if mismatch_reason is not None:
                findings.append(
                    {
                        "id": f"WINMISMATCH-{seed}",
                        "severity": "blocking",
                        "title": "Recorded winner/reason contradicts final state",
                        "claim": (
                            "The recorded game_over winner/reason does not match the "
                            "final reconstructed alive-roles/tasks state."
                        ),
                        "evidence": (
                            f"seed {seed}: recorded {recorded_winner}/"
                            f"{recorded_reason} but {mismatch_reason}"
                        ),
                        "repair_hint": (
                            "Compare engine.win_conditions.evaluate_win_conditions "
                            "against the recorded outcome for this seed."
                        ),
                    }
                )

        # Per-game token totals.
        game_input = sum(
            c.input_tokens for e in meeting_entries for c in e.llm_calls
        ) + sum(fc.input_tokens for fc in failed_call_entries)
        game_output = sum(
            c.output_tokens for e in meeting_entries for c in e.llm_calls
        ) + sum(fc.output_tokens for fc in failed_call_entries)
        game_cost = sum(c.cost_usd for e in meeting_entries for c in e.llm_calls) + sum(
            fc.cost_usd for fc in failed_call_entries
        )

        # Self-check: every kill-derived death has its victim in deaths.
        for k in kills:
            if k["victim"] not in deaths:
                invariant_failures.append(
                    f"seed {seed}: kill victim {k['victim']} at tick {k['tick']} "
                    f"not in deaths set"
                )

        games.append(
            {
                "seed": seed,
                "game_id": game_id,
                "roles": roles,
                "winner": recorded_winner,
                "reason": recorded_reason,
                "game_over_tick": recorded_go_tick,
                "kills": kills,
                "deaths": sorted(deaths),
                "meetings": meetings_out,
                "first_zero_impostor_tick": first_zero_impostor_tick,
                "tokens": {
                    "input": game_input,
                    "output": game_output,
                    "cost_usd": game_cost,
                },
                "failed_calls": failed_calls_out,
            }
        )

    # --- Self-check invariants (FAIL LOUD) ---
    self_checks: list[str] = []
    ok_meetings = total_meetings == total_meeting_records
    self_checks.append(
        f"total meetings in facts ({total_meetings}) == meeting records "
        f"({total_meeting_records}): {'OK' if ok_meetings else 'FAIL'}"
    )
    if not ok_meetings:
        invariant_failures.append(
            f"meeting count mismatch: facts {total_meetings} vs records "
            f"{total_meeting_records}"
        )

    n_files = len(list(SAMPLE_DIR.glob("replay-seed-*.jsonl")))
    ok_games = games_analyzed == n_files
    self_checks.append(
        f"games_analyzed ({games_analyzed}) == replay files ({n_files}): "
        f"{'OK' if ok_games else 'FAIL'}"
    )
    if not ok_games:
        invariant_failures.append(f"games_analyzed {games_analyzed} != files {n_files}")

    impostor_check_ok = all(
        sum(1 for r in g["roles"].values() if r == "IMPOSTOR") == num_impostors
        for g in games
    )
    self_checks.append(
        f"every seed has exactly {num_impostors} impostors: "
        f"{'OK' if impostor_check_ok else 'FAIL'}"
    )

    # v2 ADDED invariants (recorded inside _analyze_meeting; summarized here).
    transcript_failures = [
        f
        for f in invariant_failures
        if "transcript.turns is empty" in f or "opening turns at positions" in f
    ]
    self_checks.append(
        "every meeting transcript is non-empty with exactly one opening at "
        f"index 0: {'OK' if not transcript_failures else 'FAIL'}"
    )
    dead_voter_failures = [f for f in invariant_failures if "ballot voter" in f]
    self_checks.append(
        "every ballot voter is alive at its meeting tick: "
        f"{'OK' if not dead_voter_failures else 'FAIL'}"
    )
    hash_before_failures = [f for f in invariant_failures if "state_hash_before" in f]
    self_checks.append(
        "every meeting state_hash_before matches its trigger tick's "
        f"state_hash: {'OK' if not hash_before_failures else 'FAIL'}"
    )
    walk_hash_failures = [
        f
        for f in invariant_failures
        if "state-hash mismatch" in f or "post-meeting state-hash" in f
    ]
    self_checks.append(
        "per-tick + post-meeting state hashes match the recorded log: "
        f"{'OK' if not walk_hash_failures else 'FAIL'}"
    )

    for line in self_checks:
        print(line, file=sys.stderr)

    if invariant_failures:
        for f in invariant_failures:
            print(f"INVARIANT FAILURE: {f}", file=sys.stderr)
        raise RuntimeError(
            f"{len(invariant_failures)} extraction invariant(s) failed; "
            "the facts file would be untrustworthy. Aborting."
        )

    aggregates = {
        "win_split": win_split,
        "reason_counts": reason_counts,
        "no_game_over_games": no_game_over,
        "total_kills": total_kills,
        "impostor_victim_kills": impostor_victim_kills,
        "total_meetings": total_meetings,
        "trigger_kind_counts": trigger_kind_counts,
        "ejections_by_role": ejections_by_role,
        "total_ballots": total_ballots,
        "skip_ballots": total_skip_ballots,
        "skip_ballot_share": (
            round(total_skip_ballots / total_ballots, 4) if total_ballots else None
        ),
        "chain_length_histogram": dict(
            sorted(chain_length_hist.items(), key=lambda kv: int(kv[0]))
        ),
        "termination_condition_counts": termination_counts,
        "opening_turns_with_accusation": opening_accusation_count,
        "accusations": {
            "total": accusations_total,
            "at_impostors": accusations_at_impostors,
            "at_innocents": accusations_at_innocents,
            "self_accusations": self_accusations,
            "at_unknown_ids": accusations_at_unknown,
        },
        "opt_ins": {
            "eligible_derived_total": opt_in_eligible_total,
            "turns_total": opt_in_turns_total,
            "substantive": opt_in_substantive,
            "empty_pass": opt_in_turns_total - opt_in_substantive,
        },
        "ballot_follows_chain": {
            "non_skip_ballots": ballots_non_skip,
            "follows_chain": ballots_follow_chain,
            "non_skip_with_null_reason": ballots_non_skip_null_reason,
        },
        "total_contradictions": total_contradictions,
        "total_calls": total_calls,
        "total_failed_calls": total_failed_calls,
        "tokens": {
            "input": agg_input_tokens,
            "output": agg_output_tokens,
            "cost_usd": agg_cost,
        },
    }

    facts = {
        "git_head": _git_head(),
        "sample_dir": str(SAMPLE_DIR),
        "seedset": SEEDSET,
        "roster": roster,
        "games_analyzed": games_analyzed,
        "self_checks": self_checks,
        "aggregates": aggregates,
        "games": games,
    }

    tmpdir = os.environ.get("TMPDIR", "/tmp")
    facts_path = Path(tmpdir) / f"ailibi-gameplay-facts-{SEEDSET}.json"
    facts_path.write_text(
        json.dumps(facts, indent=2, sort_keys=False), encoding="utf-8"
    )

    # Emit machine-readable summary for the caller on stdout.
    print(
        json.dumps(
            {
                "facts_path": str(facts_path),
                "games_analyzed": games_analyzed,
                "aggregates": aggregates,
                "n_findings": len(findings),
                "findings": findings,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
