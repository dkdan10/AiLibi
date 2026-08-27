"""Tests for the meeting training table (Task 15.11; baseline-5 re-ground 17.10).

Pins on the committed baseline-5 bytes: the reconstructed table reproduces the
sets' tournament-report meeting / ejection / ballot totals EXACTLY (every recorded
ballot joins a feature row — 100% join rate), every feature derives offline, the
table rebuilds byte-identically (determinism), the belief-fold suspicion is the
neutral prior at the first meeting and diverges later (the cross-meeting
accumulator), and a committed ``splits.json`` is honoured. The Task-17.10
additions are pinned end-to-end: the coerced-SKIP column follows the anchored
repr-aware marker convention, and :func:`measure_belief_render_parity` proves the
hand-mirrored belief fold IS the production fold on the frozen corpus (0 raw
mismatches) while measuring the graduated-J1 live-parity divergence.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Final, get_args

import numpy as np
import pytest

from api import replay_loader
from agents.memory.beliefs import (
    MEETING_SUSPICION_DECAY_RATE,
    BeliefState,
    apply_meeting_evidence_rules,
)
from engine.actions import Action, DoTaskAction, MoveAction
from engine.entities import BodyState
from engine.events import KilledEvent, VentEnteredEvent
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval.validity import assemble_tournament_report
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_OBSERVATION_ID_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
)
from meetings.schemas import AlibiClaim as SchemaAlibiClaim
from meetings.schemas import (
    BallotTargetRewriteReason,
    CompletedTaskObservation,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    VoteBallot,
)
from meetings.transcript import WEAK_CONTRADICTION_MARKER_PREFIX
from orchestrator.replay import MeetingReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state
from training.surrogate.ballots import (
    MASKED_IS_REPORTER,
    _target_was_rewritten,
    ballot_features_from_row,
)
from training.surrogate.dataset import (
    BALLOT_AUDIT_MARKERS,
    TARGET_REWRITE_LABELS,
    BeliefRenderParity,
    MeetingTableReconstructionError,
    MeetingTableRow,
    _ballot_is_coerced_skip,
    _contradiction_lifts,
    _WindowStats,
    ballot_rewrite_labels,
    build_meeting_table,
    load_splits,
    measure_belief_render_parity,
)

#: The four committed replay sets, in the order every per-set pin below reads.
_COMMITTED_SETS: Final[tuple[Path, ...]] = (
    Path("replays/samples/9p2i"),
    Path("replays/ml_corpus/9p2i"),
    Path("replays/samples/4p1i"),
    Path("replays/ml_corpus/4p1i"),
)

#: Any bracketed annotation, whatever produced it — the census denominator, so
#: the marker parser cannot define away a kind by failing to recognise it.
_BRACKETED: Final[re.Pattern[str]] = re.compile(r"\[[^\]]*\]")

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def _report_totals(sample_dir: Path) -> tuple[int, int, int, int]:
    """``(meetings, ejections, skips, ballots)`` from the set's tournament report."""

    report = assemble_tournament_report(sample_dir)
    meetings = [m for g in report.games for m in g.meetings]
    ejections = sum(1 for m in meetings if m.outcome == "EJECTED")
    skips = sum(1 for m in meetings if m.outcome == "SKIPPED")
    ballots = sum(len(m.ballots) for m in meetings)
    return len(meetings), ejections, skips, ballots


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_table_counts_reproduce_the_committed_report(sample_dir: Path) -> None:
    """Meeting / ejection / ballot totals match the set's assembled report exactly.

    Derived from the report, not hard-coded — substrate-agnostic, so the pins
    survived the baseline-5 re-records unchanged. The table's aggregates AND its
    actual row set both reproduce the report; a drift in either fails here.
    """

    meetings, ejections, skips, ballots = _report_totals(sample_dir)
    table = build_meeting_table(sample_dir)

    assert table.meetings_total == meetings
    assert table.ejections_total == ejections
    assert table.skips_total == skips
    assert table.ballots_total == ballots
    assert table.games_total == len(table.game_seeds())
    # The reconstructed row set reproduces the same counts, independently.
    assert len({(r.seed, r.meeting_id) for r in table.rows}) == meetings
    ejected_meetings = {
        (r.seed, r.meeting_id) for r in table.rows if r.outcome == "EJECTED"
    }
    skipped_meetings = {
        (r.seed, r.meeting_id) for r in table.rows if r.outcome == "SKIPPED"
    }
    assert len(ejected_meetings) == ejections
    assert len(skipped_meetings) == skips


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_every_recorded_ballot_joins_a_row(sample_dir: Path) -> None:
    """100% join rate: one (meeting, voter) row per recorded ballot (asserted)."""

    _, _, _, ballots = _report_totals(sample_dir)
    table = build_meeting_table(sample_dir)

    assert len(table.rows) == ballots == table.ballots_total
    # Each row carries its voter's actual ballot and the full living candidate set.
    for row in table.rows:
        assert row.voter in {c.candidate for c in row.candidates}
        assert row.ballot_target == "SKIP" or isinstance(row.ballot_target, str)
        assert 0.0 <= row.ballot_confidence <= 1.0


@pytest.mark.parametrize("sample_dir", [_NINE, _FOUR])
def test_table_is_byte_deterministic(sample_dir: Path) -> None:
    """Rebuilding the table twice is byte-identical (the determinism pin)."""

    first = build_meeting_table(sample_dir).model_dump_json()
    second = build_meeting_table(sample_dir).model_dump_json()
    assert first == second


def test_belief_fold_is_neutral_at_first_meeting_and_diverges_later() -> None:
    """The pre-meeting belief row starts neutral except for perception pins.

    At meeting index 0 no prior meeting evidence has folded, so a candidate the
    voter holds NO perception pin about reads the neutral 0.5 prior — while a
    pinned candidate (witnessed kill/vent, Rule-1 body proximity) reads ABOVE it,
    exactly as production's perception-time ingest leaves the graph. By a later
    meeting the cross-meeting accumulator has moved some candidate off 0.5 — the
    signal FO-6's six raw counts never carried.
    """

    table = build_meeting_table(_NINE)
    first_meeting = [r for r in table.rows if r.meeting_index == 0]
    assert first_meeting, "expected at least one first-meeting row on 9p2i"
    for row in first_meeting:
        for cand in row.candidates:
            assert cand.belief_trust == pytest.approx(0.5)
            if cand.witnessed_kill or cand.witnessed_vent or cand.body_proximity:
                assert cand.belief_suspicion > 0.5  # the ingested perception pin
            else:
                assert cand.belief_suspicion == pytest.approx(0.5)

    later = [
        cand
        for row in table.rows
        if row.meeting_index >= 1
        for cand in row.candidates
        if not cand.is_self
    ]
    assert any(abs(c.belief_suspicion - 0.5) > 1e-9 for c in later), (
        "expected the cross-meeting belief accumulator to diverge from the prior"
    )


def test_vent_flags_are_counted_in_their_own_band() -> None:
    """The Task-15.4 ``vent_sighting`` flag is a first-class column.

    Grounded vent flags have been recorded since baseline 3 and persist on the
    committed baseline-5 bytes; at least one candidate carries a ``vent_flags``
    count, and it is never folded into the ``strong_flags`` / ``weak_flags``
    bands.
    """

    table = build_meeting_table(_NINE)
    vent_rows = [c for row in table.rows for c in row.candidates if c.vent_flags > 0]
    assert vent_rows, "the committed 9p2i set should carry a vent_sighting flag"


def test_witnessed_kill_marks_the_killer_not_a_bystander() -> None:
    """The witnessed-kill pin reads ``KilledEvent.witnesses`` + actor, not a proxy.

    Every candidate flagged ``witnessed_kill`` must be an IMPOSTOR — only impostors
    kill, so the event-derived pin marks the killer (``event.actor``), never a
    co-present bystander. The committed 9p2i set carries crew-witnessed kills, so
    the column is non-empty (the +1.0 role-proving pin the belief store folds).
    """

    table = build_meeting_table(_NINE)
    witnessed = [
        cand for row in table.rows for cand in row.candidates if cand.witnessed_kill
    ]
    assert witnessed, "the committed 9p2i set should carry a crew-witnessed kill"
    assert all(cand.is_impostor for cand in witnessed), (
        "witnessed_kill must mark the killer (an impostor), never a bystander"
    )


def test_witnessed_vent_marks_the_venter_from_events() -> None:
    """The witnessed-vent pin is the venter, derived from vent-event witnesses.

    A crew member who saw a vent takes the +0.5 role-proving pin even when no
    grounded ``vent_sighting`` contradiction is spoken; every ``witnessed_vent``
    candidate is an IMPOSTOR (vents are impostor-only), so the event-derived pin
    marks the venter, not a bystander.
    """

    table = build_meeting_table(_NINE)
    vented = [
        cand for row in table.rows for cand in row.candidates if cand.witnessed_vent
    ]
    assert vented, "the committed 9p2i set should carry a crew-witnessed vent"
    assert all(cand.is_impostor for cand in vented), (
        "witnessed_vent must mark the venter (an impostor)"
    )


def test_eyewitness_pins_are_voter_local() -> None:
    """A witnessed-kill/vent pin appears only in the WITNESSING voter's row.

    Production stamps the act only for its witnesses, so the +1.0 / +0.5 pin must
    not leak to a co-meeting voter who did not see it. Proven by finding a candidate
    whose pin is True in one voter's row and False in another's, at the same meeting.
    """

    table = build_meeting_table(_NINE)
    by_meeting: dict[tuple[int, str], list[MeetingTableRow]] = {}
    for row in table.rows:
        by_meeting.setdefault((row.seed, row.meeting_id), []).append(row)

    found_local = False
    for rows in by_meeting.values():
        for name in ("witnessed_kill", "witnessed_vent", "body_proximity"):
            per_candidate: dict[str, set[bool]] = {}
            for row in rows:
                for cand in row.candidates:
                    per_candidate.setdefault(cand.candidate, set()).add(
                        bool(getattr(cand, name))
                    )
            if any(values == {True, False} for values in per_candidate.values()):
                found_local = True
    assert found_local, (
        "expected at least one eyewitness pin that some voters hold and others do "
        "not (voter-local), never a global flag shared by every voter"
    )


def test_self_candidate_reads_the_neutral_prior() -> None:
    """A voter's own candidate row is never a held belief (the own-id exclusion)."""

    table = build_meeting_table(_FOUR)
    self_cands = [c for row in table.rows for c in row.candidates if c.is_self]
    assert self_cands
    for cand in self_cands:
        assert cand.belief_suspicion == pytest.approx(0.5)


def test_splits_json_is_honoured_when_present(tmp_path: Path) -> None:
    """A committed ``splits.json`` is read into the table (the 15.12 seam)."""

    # No committed splits on the baseline sets.
    assert load_splits(_FOUR) is None

    # A staged split file is parsed and attached; the builder reads it via
    # ``splits_path`` without needing it inside the (read-only) replay dir.
    splits_file = tmp_path / "splits.json"
    splits_file.write_text(json.dumps({"train": [0, 1, 2], "val": [3], "test": [4, 5]}))
    table = build_meeting_table(_FOUR, splits_path=splits_file)
    assert table.splits is not None
    assert table.splits.train == (0, 1, 2)
    assert table.splits.val == (3,)
    assert table.splits.test == (4, 5)


def test_malformed_splits_fails_loud(tmp_path: Path) -> None:
    """A malformed ``splits.json`` raises rather than silently being ignored."""

    bad = tmp_path / "splits.json"
    bad.write_text(json.dumps({"train": "not-a-list"}))
    with pytest.raises((ValueError, MeetingTableReconstructionError)):
        load_splits(tmp_path)


def test_load_splits_reads_the_frozen_corpus_files() -> None:
    """The committed 15.12 corpus ``splits.json`` files load UNCHANGED.

    Regression pin for the PR #240 review finding: the recorder emits four
    audit-metadata keys (``set``/``split_rule``/``counts``/``total_games``)
    beside the seed lists, and the loader must accept the frozen files exactly
    as committed — the corpus is the 15.13 surrogate's training data.
    """

    nine = load_splits(Path("replays/ml_corpus/9p2i"))
    assert nine is not None
    assert (len(nine.train), len(nine.val), len(nine.test)) == (90, 30, 30)
    nine_seeds = [*nine.train, *nine.val, *nine.test]
    assert len(set(nine_seeds)) == 150  # disjoint — no game in two splits
    assert set(nine_seeds) == set(range(1000, 1150))  # covers the recorded range
    assert nine.set == "9p2i"
    assert nine.split_rule == "seed mod 5: {0,1,2}=train, {3}=val, {4}=test"
    assert nine.total_games == 150

    four = load_splits(Path("replays/ml_corpus/4p1i"))
    assert four is not None
    assert (len(four.train), len(four.val), len(four.test)) == (30, 10, 10)
    four_seeds = [*four.train, *four.val, *four.test]
    assert len(set(four_seeds)) == 50
    assert set(four_seeds) == set(range(1000, 1050))
    assert four.set == "4p1i"


def test_build_meeting_table_consumes_the_frozen_corpus() -> None:
    """The table builder runs on the committed 15.12 corpus END-TO-END.

    The cross-artifact integration the PR #240 review finding proved was never
    executed: the builder walks the frozen 4p1i corpus (hash-verified, ~0.4s),
    attaches its committed split, and joins every recorded ballot. The 9p2i
    corpus rides the identical path (pinned by the splits test above; its
    ~7s walk stays out of the suite).
    """

    table = build_meeting_table(Path("replays/ml_corpus/4p1i"))
    assert table.games_total == 50
    assert table.meetings_total == 44  # was 40
    assert (
        table.ballots_total == 132
    )  # == validity-gate ballot count: 100% join  # was 120
    assert len(table.rows) == 132  # was 120
    assert table.splits is not None
    assert (len(table.splits.train), len(table.splits.val), len(table.splits.test)) == (
        30,
        10,
        10,
    )
    # The fit-side drop census on this set: no J2-coerced ballot, but TWO rows
    # whose target the meeting layer rewrote (both under-gate redirects), so the
    # exclusion is load-bearing on committed bytes rather than fixture-only.
    assert sum(row.ballot_coerced_skip for row in table.rows) == 0
    assert sum(_target_was_rewritten(row) for row in table.rows) == 2  # was 0


def test_splits_count_metadata_must_agree_with_seed_lists(tmp_path: Path) -> None:
    """Present count metadata that contradicts the seed lists is refused."""

    bad = tmp_path / "splits.json"
    bad.write_text(
        json.dumps(
            {
                "train": [0],
                "val": [],
                "test": [],
                "counts": {"train": 2, "val": 0, "test": 0},
                "total_games": 1,
            }
        )
    )
    with pytest.raises(ValueError, match="counts"):
        load_splits(tmp_path)

    bad.write_text(json.dumps({"train": [0], "val": [], "test": [], "total_games": 3}))
    with pytest.raises(ValueError, match="total_games"):
        load_splits(tmp_path)


def test_unknown_splits_keys_still_fail_loud(tmp_path: Path) -> None:
    """Declaring the 15.12 metadata keys did not open the door to unknown keys."""

    bad = tmp_path / "splits.json"
    bad.write_text(json.dumps({"train": [0], "bogus_key": 1}))
    with pytest.raises(ValueError, match="bogus_key"):
        load_splits(tmp_path)


def test_missing_directory_fails_loud(tmp_path: Path) -> None:
    """An absent replay-set directory raises (no silent empty table)."""

    with pytest.raises(NotADirectoryError):
        build_meeting_table(tmp_path / "does-not-exist")


def _weak_flag(
    flag_id: str, *, subject: str, alibi_claim_id: str, sighting_id: str
) -> ContradictionRef:
    """A weak ``alibi_vs_sighting`` flag riding one underlying alibi claim."""

    return ContradictionRef(
        contradiction_id=flag_id,
        kind="alibi_vs_sighting",
        event_a_id=alibi_claim_id,
        event_b_id=sighting_id,
        subjects=(subject,),
        description=(
            f"{WEAK_CONTRADICTION_MARKER_PREFIX}self-stated alibi] alibi vs sighting"
        ),
    )


def test_duplicate_claim_flags_fold_to_one_rendered_lift() -> None:
    """``contradiction_lift`` carries the production dedup + cap, not raw sums.

    ``apply_contradiction_rule`` takes ONE delta per (subject, alibi-claim) lift
    group: one alibi paired against N sightings is N flags but a single +0.08.
    Two flags on DIFFERENT claims still accumulate, and the per-meeting total is
    capped at one strong flag's worth (0.30) — the exact vote-time semantics the
    honest ceiling must read (a raw count sum would report 0.16 / 0.60 here).
    """

    living = ["p-1", "p-2"]
    same_claim = [
        _weak_flag(
            "c-1", subject="p-1", alibi_claim_id="turn:t1:claim:0", sighting_id="s1"
        ),
        _weak_flag(
            "c-2", subject="p-1", alibi_claim_id="turn:t1:claim:0", sighting_id="s2"
        ),
    ]
    assert _contradiction_lifts(same_claim, living, transcript=None)[
        "p-1"
    ] == pytest.approx(0.08)

    distinct_claims = [
        _weak_flag(
            "c-1", subject="p-1", alibi_claim_id="turn:t1:claim:0", sighting_id="s1"
        ),
        _weak_flag(
            "c-2", subject="p-1", alibi_claim_id="turn:t2:claim:1", sighting_id="s2"
        ),
    ]
    assert _contradiction_lifts(distinct_claims, living, transcript=None)[
        "p-1"
    ] == pytest.approx(0.16)

    # Many distinct-claim flags cap at one strong flag's worth, never 1.0.
    stacked = [
        _weak_flag(
            f"c-{i}",
            subject="p-1",
            alibi_claim_id=f"turn:t{i}:claim:{i}",
            sighting_id=f"s{i}",
        )
        for i in range(6)
    ]
    lifts = _contradiction_lifts(stacked, living, transcript=None)
    assert lifts["p-1"] == pytest.approx(0.30)
    assert lifts["p-2"] == pytest.approx(0.0)  # unflagged candidate reads zero


def test_self_refuted_alibi_flag_renders_the_weak_delta() -> None:
    """The lift threads the transcript, so the 14.10 downgrade applies (Codex).

    Production threads the meeting transcript into ``apply_contradiction_rule``
    (``meetings/manager.py``), where a STRONG flag riding an alibi claim the
    speaker disproved within their OWN turn (``self_refuted_alibi_claim_ids``)
    contributes the WEAK 0.08 delta, not 0.30. The table-build lift must render
    the same value or the ``contradiction_lift`` column, the reconstructed
    suspicion, and the honest ceiling all overstate that scenario.
    """

    # One turn: p-1 states an alibi (CAFETERIA, ticks 5-14) beside their OWN
    # completed_task observation at tick 9 in a contradictory room — the audited
    # self-refuted shape (mirrors tests/agents/test_beliefs.py).
    turn = MeetingTurn(
        turn_id="m-1:turn-0",
        turn_index=0,
        speaker="p-1",
        turn_kind="opening",
        reply_to=None,
        observations=(
            CompletedTaskObservation(
                type="completed_task", tick=9, task_id="t-1", room="STORAGE"
            ),
        ),
        claims=(
            SchemaAlibiClaim(
                type="alibi", subject="p-1", from_tick=5, to_tick=14, room="CAFETERIA"
            ),
        ),
        free_text="I was in the cafeteria the whole time.",
    )
    transcript = MeetingTranscript(turns=(turn,))
    strong_flag_on_self_alibi = ContradictionRef(
        contradiction_id="c-1",
        kind="alibi_vs_sighting",
        event_a_id="turn:m-1:turn-0:claim:0",
        event_b_id="turn:m-1:turn-1:obs:0",
        subjects=("p-1",),
        description="alibi vs sighting",  # no weak marker: detector-STRONG
    )

    living = ["p-1", "p-2"]
    with_transcript = _contradiction_lifts(
        [strong_flag_on_self_alibi], living, transcript=transcript
    )
    assert with_transcript["p-1"] == pytest.approx(0.08)  # the production render
    # Without the transcript no downgrade signal exists — the un-threaded 0.30
    # is exactly the overstatement the fix removes.
    without = _contradiction_lifts([strong_flag_on_self_alibi], living, transcript=None)
    assert without["p-1"] == pytest.approx(0.30)


def test_task_and_move_counts_derive_from_accepted_events() -> None:
    """Cadence counters read ACCEPTED engine events, never submitted intents.

    The committed corpora contain rejected ``do_task`` / ``move`` attempts (dead
    actors, wrong rooms, unowned tasks); a rejected intent emits a rejection
    event and no state change, so it must not count (Codex review). An accepted
    move emits ``Moved`` and an accepted task tick ``TaskProgressed`` /
    ``TaskCompleted`` — those do.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=4, num_impostors=1, tasks_per_crewmate=2
    )
    roles = {pid: player.role for pid, player in state.players.items()}

    # A crewmate placed IN its task room: its do_task is accepted. Another
    # crewmate NOT in some task's room submits that task: rejected.
    crew_task = next(
        task for task in state.tasks.values() if roles[task.owner] == "CREWMATE"
    )
    worker = crew_task.owner
    players = dict(state.players)
    players[worker] = replace(players[worker], room=crew_task.room)
    rejected_actor = next(
        task.owner
        for task in state.tasks.values()
        if task.owner != worker
        and roles[task.owner] == "CREWMATE"
        and players[task.owner].room != task.room
    )
    rejected_task = next(
        task
        for task in state.tasks.values()
        if task.owner == rejected_actor and players[rejected_actor].room != task.room
    )
    # A third player moves: legally (adjacent room) — accepted.
    mover = next(
        pid for pid in sorted(state.players) if pid not in (worker, rejected_actor)
    )
    to_room = game_map.room_neighbors(players[mover].room)[0]
    state = replace(state, players=players)

    actions: list[Action] = [
        DoTaskAction(
            type="do_task",
            actor=worker,
            payload={"task_id": crew_task.map_task_id},  # type: ignore[arg-type]
        ),
        DoTaskAction(
            type="do_task",
            actor=rejected_actor,
            payload={"task_id": rejected_task.map_task_id},  # type: ignore[arg-type]
        ),
        MoveAction(
            type="move",
            actor=mover,
            payload={"to_room": to_room},  # type: ignore[arg-type]
        ),
    ]
    next_state, events = advance_tick(state, actions, game_map=game_map)

    stats = _WindowStats(game_map)
    beliefs = {pid: BeliefState() for pid in state.players}
    stats.absorb_tick(next_state, events, roles, beliefs=beliefs)
    assert stats.task_submissions.get(worker, 0) == 1  # accepted task tick counts
    assert rejected_actor not in stats.task_submissions  # rejected intent does not
    assert stats.moves.get(mover, 0) == 1  # accepted move counts
    assert worker not in stats.moves


def test_body_proximity_is_first_sighting_co_presence_not_room_occupancy() -> None:
    """The Rule-1 pin is voter-local first-sighting evidence (Codex review).

    Production fires the +0.2 bump only in the DISCOVERING agent's own beliefs,
    and only for players that agent itself observed in the body's room within the
    prior window — never for whoever stands in the corpse's room at discovery.
    Scenario: A and C share room R at tick 1; by tick 2 C has left, D has walked
    in, and V's body lies in R. A (first sighting, saw C in R at tick 1) pins C —
    and only in A's view. D (arrived with the body, no prior sightings of R) pins
    nobody despite standing in the corpse's room, and C (elsewhere) never saw the
    body at all.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=4, num_impostors=1, tasks_per_crewmate=2
    )
    roles = {pid: player.role for pid, player in state.players.items()}
    crew = sorted(pid for pid, role in roles.items() if role == "CREWMATE")
    observer_a, leaver_c, latecomer_d = crew
    victim_v = next(pid for pid, role in roles.items() if role == "IMPOSTOR")
    room_r = state.players[observer_a].room
    room_s = game_map.room_neighbors(room_r)[0]

    stats = _WindowStats(game_map)
    beliefs = {pid: BeliefState() for pid in state.players}

    # Tick 1: A and C co-present in R; D and V away in S. No body yet.
    players_t1 = dict(state.players)
    players_t1[leaver_c] = replace(players_t1[leaver_c], room=room_r)
    players_t1[latecomer_d] = replace(players_t1[latecomer_d], room=room_s)
    players_t1[victim_v] = replace(players_t1[victim_v], room=room_s)
    state_t1 = replace(state, tick=1, players=players_t1)
    stats.absorb_tick(state_t1, [], roles, beliefs=beliefs)

    # Tick 2: C left to S, D walked into R, V's body lies undiscovered in R.
    players_t2 = dict(players_t1)
    players_t2[leaver_c] = replace(players_t2[leaver_c], room=room_s)
    players_t2[latecomer_d] = replace(players_t2[latecomer_d], room=room_r)
    players_t2[victim_v] = replace(players_t2[victim_v], alive=False, room=room_r)
    body = BodyState(
        id="body-test",
        player_id=victim_v,
        room=room_r,
        position=(0.0, 0.0),
        killed_by=victim_v,
        discovered_by=None,
    )
    state_t2 = replace(state, tick=2, players=players_t2, bodies={body.id: body})
    stats.absorb_tick(state_t2, [], roles, beliefs=beliefs)

    # C is pinned, but ONLY in A's view (A saw C in R shortly before discovery).
    assert stats.body_proximity.get(leaver_c) == {observer_a}
    # D stands in the corpse's room at discovery yet is NOT pinned (nobody
    # observed D in R within the pre-discovery window), and pins nothing.
    assert latecomer_d not in stats.body_proximity
    # The victim is never a suspect of its own body.
    assert victim_v not in stats.body_proximity
    # The +0.2 ingested into the OBSERVER's own belief row at perception —
    # production's Rule-1 stamp — and nobody else's.
    assert beliefs[observer_a].view(leaver_c).suspicion == pytest.approx(0.7)
    assert beliefs[latecomer_d].view(leaver_c).suspicion == pytest.approx(0.5)
    assert beliefs[leaver_c].view(latecomer_d).suspicion == pytest.approx(0.5)


def test_teammate_vent_witness_takes_the_production_pin() -> None:
    """An impostor witnessing a TEAMMATE's vent takes the +0.5 pin (Codex review).

    Production's vent rule carries NO fellow-impostor guard (unlike the kill
    rule's §4.7 guard): `apply_observation_rules` applies `VENTING_SUSPICION_DELTA`
    for every witness of the vent stamp. Filtering vent witnesses to crew would
    drop those real belief updates from impostor voters' pre-meeting rows.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=9, num_impostors=2, tasks_per_crewmate=2
    )
    roles = {pid: player.role for pid, player in state.players.items()}
    venter, teammate = sorted(pid for pid, role in roles.items() if role == "IMPOSTOR")
    crew_witness = sorted(pid for pid, role in roles.items() if role == "CREWMATE")[0]
    room = state.players[venter].room

    stats = _WindowStats(game_map)
    beliefs = {pid: BeliefState() for pid in state.players}
    vent = VentEnteredEvent(
        type="VentEntered",
        tick=1,
        actor=venter,
        vent_id="v-1",
        room=room,
        source_vent_id="v-1",
        destination_vent_id="v-2",
        source_room=room,
        destination_room=room,
        traversal_ticks=1,
        witnesses=(teammate, crew_witness),
        source_witnesses=(teammate, crew_witness),
        destination_witnesses=(),
    )
    stats.absorb_tick(state, [vent], roles, beliefs=beliefs)

    assert stats.witnessed_vent[venter] == {teammate, crew_witness}
    # Both witnesses' OWN rows take the production +0.5 (0.5 -> 1.0).
    assert beliefs[teammate].view(venter).suspicion == pytest.approx(1.0)
    assert beliefs[crew_witness].view(venter).suspicion == pytest.approx(1.0)
    # Non-witnesses take nothing (voter-local).
    non_witness = sorted(pid for pid, role in roles.items() if role == "CREWMATE")[1]
    assert beliefs[non_witness].view(venter).suspicion == pytest.approx(0.5)


def test_vent_stamp_feeds_the_body_proximity_window() -> None:
    """A witnessed vent's ``saw_player`` stamp feeds Rule-1 co-presence (Codex).

    Production records witness-gated kill/vent action stamps as ``saw_player``
    rows even when the actor is not currently visible — a venting actor is
    hidden in the vent — and ``_recent_co_presence`` reads those rows. So a
    voter who saw a player vent in a room must still pin that player when a
    body is first seen there within the window.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=4, num_impostors=1, tasks_per_crewmate=2
    )
    roles = {pid: player.role for pid, player in state.players.items()}
    venter = next(pid for pid, role in roles.items() if role == "IMPOSTOR")
    crew = sorted(pid for pid, role in roles.items() if role == "CREWMATE")
    witness, victim, other = crew
    room_r = state.players[witness].room
    room_s = game_map.room_neighbors(room_r)[0]

    stats = _WindowStats(game_map)
    beliefs = {pid: BeliefState() for pid in state.players}

    # Tick 1: the venter vents in R, witnessed by `witness` — but the venter is
    # IN THE VENT at absorb time, so it is absent from visible_player_ids and
    # only the event stamp can record the sighting.
    players_t1 = dict(state.players)
    players_t1[venter] = replace(players_t1[venter], room=room_r, in_vent=True)
    players_t1[victim] = replace(players_t1[victim], room=room_s)
    players_t1[other] = replace(players_t1[other], room=room_s)
    state_t1 = replace(state, tick=1, players=players_t1)
    vent = VentEnteredEvent(
        type="VentEntered",
        tick=1,
        actor=venter,
        vent_id="v-1",
        room=room_r,
        source_vent_id="v-1",
        destination_vent_id="v-2",
        source_room=room_r,
        destination_room=room_s,
        traversal_ticks=1,
        witnesses=(witness,),
        source_witnesses=(witness,),
        destination_witnesses=(),
    )
    stats.absorb_tick(state_t1, [vent], roles, beliefs=beliefs)

    # Tick 2: the victim's body lies in R; `witness` first-sights it. The venter
    # must be co-present via the tick-1 vent stamp and take the Rule-1 pin.
    players_t2 = dict(players_t1)
    players_t2[victim] = replace(players_t2[victim], alive=False, room=room_r)
    body = BodyState(
        id="body-vent-test",
        player_id=victim,
        room=room_r,
        position=(0.0, 0.0),
        killed_by=venter,
        discovered_by=None,
    )
    state_t2 = replace(state, tick=2, players=players_t2, bodies={body.id: body})
    stats.absorb_tick(state_t2, [], roles, beliefs=beliefs)

    assert witness in stats.body_proximity.get(venter, set())


def test_perception_pins_decay_through_the_real_fold() -> None:
    """A pin ingested at perception decays at unreinforced meeting folds (Codex).

    Production's Rule 5 drifts an already-known row toward the 0.5 prior by
    ``MEETING_SUSPICION_DECAY_RATE`` per meeting that produced no new evidence
    about the subject. Because the walk ingests the witnessed-kill +1.0 into the
    witness's ``BeliefState`` at event time and runs the REAL fold per meeting,
    a stale pin reads its decayed value in later rows — never the full +1.0
    re-applied.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=4, num_impostors=1, tasks_per_crewmate=2
    )
    roles = {pid: player.role for pid, player in state.players.items()}
    killer = next(pid for pid, role in roles.items() if role == "IMPOSTOR")
    crew = sorted(pid for pid, role in roles.items() if role == "CREWMATE")
    witness, victim = crew[0], crew[1]

    stats = _WindowStats(game_map)
    beliefs = {pid: BeliefState() for pid in state.players}
    kill = KilledEvent(
        type="Killed",
        tick=1,
        actor=killer,
        target=victim,
        room=state.players[killer].room,
        witnesses=(witness,),
    )
    stats.absorb_tick(state, [kill], roles, beliefs=beliefs)
    assert beliefs[witness].view(killer).suspicion == pytest.approx(1.0)
    assert witness in stats.witnessed_kill[killer]

    # One meeting with NO evidence about the killer: the real fold decays the
    # pinned row toward 0.5 — 1.0 -> 0.875 at the 0.25 rate.
    beliefs[witness] = apply_meeting_evidence_rules(
        beliefs[witness],
        own_id=witness,
        accused=(),
        roster=frozenset(state.players),
    )
    expected = 0.5 + (1.0 - 0.5) * (1.0 - MEETING_SUSPICION_DECAY_RATE)
    assert beliefs[witness].view(killer).suspicion == pytest.approx(expected)
    # The FLAG persists (the voter once held first-hand evidence) — the decayed
    # MAGNITUDE lives in the belief row, never re-applied at full strength.
    assert witness in stats.witnessed_kill[killer]


# --------------------------------------------------------------------------- #
# Task 17.10 — the coerced-SKIP column + the walk re-validation               #
# --------------------------------------------------------------------------- #


def _skip_ballot(rationale: str) -> VoteBallot:
    return VoteBallot(
        voter="p-1",
        target="SKIP",
        confidence=0.2,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=rationale,
    )


def test_coerced_skip_detection_follows_the_marker_convention() -> None:
    """``_ballot_is_coerced_skip`` is the anchored repr-aware marker parse.

    Built from the imported production literal via the established
    ``api.replay_loader._marker_pattern`` convention (the ``eval.meeting_quality``
    17.2 precedent): a rendered coercion marker matches; a 16.5 nulled-citation
    marker stacked INSIDE it still matches (the gate is the last guard, so the
    coercion marker is the outermost prefix); a coerced-target payload that
    itself contains the marker's tail parses to the real boundary; the TEAMMATE
    coercion marker (which shares the "coerced to SKIP" suffix) does NOT match;
    and the marker mid-string does not match (anchored ``^``).
    """

    marker = UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-3")
    assert _ballot_is_coerced_skip(_skip_ballot(marker + "I still think p-3."))
    # The bare marker (empty original rationale) matches too.
    assert _ballot_is_coerced_skip(_skip_ballot(marker))

    stacked = (
        marker
        + INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-9:12:3")
        + "cited a ghost observation"
    )
    assert _ballot_is_coerced_skip(_skip_ballot(stacked))

    tricky = UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="x' coerced to SKIP] y")
    assert _ballot_is_coerced_skip(_skip_ballot(tricky + "payload survives"))

    teammate = TEAMMATE_VOTE_TARGET_MARKER.format(target="p-7")
    assert not _ballot_is_coerced_skip(_skip_ballot(teammate + "skipping"))
    assert not _ballot_is_coerced_skip(_skip_ballot("no marker at all"))
    assert not _ballot_is_coerced_skip(_skip_ballot("prefix " + marker))


# --------------------------------------------------------------------------- #
# The whole rewrite class: the table, the sources it reads, and the census    #
# --------------------------------------------------------------------------- #


def test_the_marker_chain_is_walked_front_to_back_not_matched_once() -> None:
    """A stacked ordering cannot hide the inner label behind the outer one.

    Every one of the eight uncited markers on committed bytes is LEADING, so a
    single anchored ``.match()`` recovers them all today and an evasion would go
    unnoticed until a recording produced one. Plant that recording: an under-gate
    redirect wrapping an uncited coercion, an order no committed byte carries.
    Both labels come back, and the same ballot with only the outer marker gives
    back only the outer label — so the assertion is not passing on a parser that
    returns everything.
    """

    stacked = (
        BALLOT_TARGET_REDIRECT_MARKER.format(original="p-2", target="p-5")
        + UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-5")
        + "they vented"
    )
    assert set(ballot_rewrite_labels(_skip_ballot(stacked))) == {
        "under_gate_redirect",
        "uncited_coerced",
    }
    outer_only = (
        BALLOT_TARGET_REDIRECT_MARKER.format(original="p-2", target="p-5")
        + "they vented"
    )
    assert ballot_rewrite_labels(_skip_ballot(outer_only)) == ("under_gate_redirect",)


def test_the_structured_guard_reason_wins_over_a_contradicting_marker() -> None:
    """A recording that carries the meeting layer's own testimony is believed.

    ``guard_rewrite_reason`` is the meeting layer stating what it did; the marker
    prefix is the legacy string a reader has to parse back out. When a recording
    carries both and they disagree, the structured field is the answer — planted
    here because no committed byte carries the field at all (0 of 3,602 recorded
    ballots across the four committed sets), so only a plant can distinguish the
    two sources.
    """

    contradicting = VoteBallot(
        voter="p-1",
        target="SKIP",
        confidence=0.2,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=(
            UNCITED_ZERO_FLAG_EJECT_MARKER.format(target="p-5") + "they vented"
        ),
        guard_redirected_from="p-2",
        guard_rewrite_reason="under_gate_redirect",
    )
    assert ballot_rewrite_labels(contradicting) == ("under_gate_redirect",)


def test_the_training_marker_table_cannot_drift_from_the_display_one() -> None:
    """One vocabulary, two layers: training and display read the same sources.

    The label set is pinned against ``api.replay_loader._BALLOT_PREFIX_MARKERS``
    and the drop set against the public
    ``meetings.schemas.BallotTargetRewriteReason`` union (which the display
    layer's own ``_TARGET_REWRITE_LABELS`` is derived from), so the two tables
    are pinned to ONE source rather than to each other. Perturbed copies of both
    prove the comparison bites.
    """

    assert {label for label, _ in BALLOT_AUDIT_MARKERS} == {
        label for label, _ in replay_loader._BALLOT_PREFIX_MARKERS
    }
    assert dict(BALLOT_AUDIT_MARKERS) == dict(replay_loader._BALLOT_PREFIX_MARKERS)
    assert TARGET_REWRITE_LABELS == frozenset(get_args(BallotTargetRewriteReason))
    assert TARGET_REWRITE_LABELS == replay_loader._TARGET_REWRITE_LABELS

    perturbed_table = BALLOT_AUDIT_MARKERS[:-1]
    assert {label for label, _ in perturbed_table} != {
        label for label, _ in replay_loader._BALLOT_PREFIX_MARKERS
    }
    perturbed_drop = TARGET_REWRITE_LABELS - {"under_gate_redirect"}
    assert perturbed_drop != frozenset(get_args(BallotTargetRewriteReason))


def test_the_citation_only_rewrites_stay_in_the_fit() -> None:
    """Nulling a reference is not rewriting a target, and the rule says so."""

    assert "invalid_reason_id" not in TARGET_REWRITE_LABELS
    assert "invalid_observation_id" not in TARGET_REWRITE_LABELS
    nulled = _skip_ballot(
        INVALID_OBSERVATION_ID_MARKER.format(observation_id="p-9:12:3")
        + "cited a ghost observation"
    )
    labels = ballot_rewrite_labels(nulled)
    assert labels == ("invalid_observation_id",)
    row = build_meeting_table(_COMMITTED_SETS[3]).rows[0]
    assert not _target_was_rewritten(
        row.model_copy(update={"ballot_rewrite_labels": labels})
    )
    assert _target_was_rewritten(
        row.model_copy(update={"ballot_rewrite_labels": ("under_gate_redirect",)})
    )


@pytest.mark.slow
def test_the_ballot_audit_marker_census_over_the_four_committed_sets() -> None:
    """What the fit actually consumes, counted — so a re-record cannot move it.

    Recomputed from the recorded bytes: every ballot in every committed set, its
    bracketed annotations counted and its rewrite labels parsed. Six of the seven
    kinds are the prefix markers this module's table parses; the seventh, the
    vote-guard rationale redaction, is a replacement BODY rather than a prefix,
    so the census counts it and the parser does not claim it.
    """

    ballots: list[VoteBallot] = []
    games = 0
    marked_games = 0
    annotations = 0
    kinds: Counter[str] = Counter()
    per_set_rewritten: list[int] = []
    for set_dir in _COMMITTED_SETS:
        rewritten = 0
        for path in sorted(set_dir.rglob("*.jsonl")):
            games += 1
            game_marked = False
            for entry in read_all_entries(path):
                if not isinstance(entry, MeetingReplayEntry):
                    continue
                for ballot in entry.ballots:
                    ballots.append(ballot)
                    brackets = _BRACKETED.findall(ballot.rationale_text)
                    annotations += len(brackets)
                    game_marked = game_marked or bool(brackets)
                    labels = ballot_rewrite_labels(ballot)
                    kinds.update(labels)
                    kinds["rationale_redaction"] += sum(
                        1 for text in brackets if "redact" in text.lower()
                    )
                    if TARGET_REWRITE_LABELS.intersection(labels):
                        rewritten += 1
            marked_games += int(game_marked)
        per_set_rewritten.append(rewritten)

    assert (games, len(ballots), annotations, marked_games) == (300, 3602, 204, 94)
    assert dict(kinds) == {
        "under_gate_redirect": 120,
        "invalid_observation_id": 27,
        "teammate_coerced": 18,
        "rationale_redaction": 18,
        "invalid_reason_id": 9,
        "uncited_coerced": 8,
        "invalid_target": 4,
    }
    assert sum(kinds.values()) == 204
    # samples-9p2i, ml_corpus-9p2i, samples-4p1i, ml_corpus-4p1i.
    assert per_set_rewritten == [45, 102, 1, 2]
    assert sum(per_set_rewritten) == 150
    # 8 of those 150 were already dropped by the J2-only rule; 142 rode into the
    # fit as the voter's own choice before this rule widened.
    assert kinds["uncited_coerced"] == 8
    # No recorded ballot carries the structured field yet, which is why the
    # marker table above is load-bearing rather than belt-and-braces.
    assert sum(b.guard_rewrite_reason is not None for b in ballots) == 0


@pytest.mark.slow
def test_the_reporter_column_is_an_exclusion_oracle_the_fit_may_not_read() -> None:
    """Why ``is_reporter`` is masked: a head on it separates the roles perfectly.

    The census first — over every candidate cell of the four committed sets, a
    reporter is a CREWMATE without exception. Then the head: restore the feature
    into the fit-side vector, fit the one-feature logistic on it against the
    IMPOSTOR label, and it calls every reporter cell crewmate with no error. That
    is roles ground truth reached through a feature column, not a ballot signal
    learned, which is why the slot is masked at every fit and inference site. The
    mask does not expire when the census moves on the next corpus: the reason it
    exists is that the column CAN carry the label, not that it currently does.
    """

    reporter_roles: Counter[str] = Counter()
    features: list[float] = []
    labels: list[float] = []
    for set_dir in _COMMITTED_SETS:
        for row in build_meeting_table(set_dir).rows:
            for feat in row.candidates:
                if feat.is_reporter:
                    reporter_roles[feat.role] += 1
                features.append(float(feat.is_reporter))
                labels.append(float(feat.is_impostor))
    assert reporter_roles == Counter({"CREWMATE": 3602})
    assert reporter_roles["IMPOSTOR"] == 0

    # The fit-side vector never sees it: every built view writes the constant.
    served = {
        cell["is_reporter"]
        for row in build_meeting_table(_COMMITTED_SETS[3]).rows
        for cell in ballot_features_from_row(row).features.values()
    }
    assert served == {MASKED_IS_REPORTER}

    # The head, on the restored feature: deterministic full-batch GD, zeros init.
    x = np.array(features, dtype=np.float64)
    y = np.array(labels, dtype=np.float64)
    weight = bias = 0.0
    for _ in range(400):
        prob = 1.0 / (1.0 + np.exp(-(weight * x + bias)))
        error = prob - y
        weight -= 0.5 * float((error * x).mean())
        bias -= 0.5 * float(error.mean())
    predicted_impostor = (1.0 / (1.0 + np.exp(-(weight * x + bias)))) >= 0.5
    assert not predicted_impostor[x == 1.0].any()
    assert float((predicted_impostor[x == 1.0] == (y[x == 1.0] == 1.0)).mean()) == 1.0


def test_walk_reproduces_the_production_fold_on_the_4p1i_corpus() -> None:
    """The 17.10 re-validation: the hand-mirrored fold IS the production fold.

    The 16.10 walk precedent (measure fidelity, don't assume it): join every
    non-self (meeting, voter, candidate) cell of the reconstructed table to the
    production fold's meeting-open graphs — real ``TacticalAgent``s fed
    reconstructed packets, read through ``suspicion_graph_for_meeting()`` — over
    the frozen 4p1i corpus. Fold fidelity must be EXACT (0 raw / trust
    mismatches), or the ``belief_suspicion`` column has silently corrupted and
    no fit over the table can be trusted (the 17.10 integration risk).
    """

    parity = measure_belief_render_parity(Path("replays/ml_corpus/4p1i"))
    assert parity.games_total == 50
    assert parity.meetings_total == 44  # was 40
    assert parity.rows_total == 132  # was 120
    assert parity.cells_compared == 264  # was 240
    assert parity.raw_mismatches == 0
    assert parity.trust_mismatches == 0
    assert parity.max_raw_abs_delta == 0.0
    # No entirely-soft conviction-grade rows on this tiny set: the live J1
    # render never diverges from the raw column here.
    assert parity.j1_divergent_cells == 0
    assert parity.j1_divergent_rows == 0
    assert parity.j1_divergent_fit_cells == 0
    assert parity.j1_divergent_test_cells == 0


@pytest.fixture(scope="module")
def corpus_parity() -> BeliefRenderParity:
    """Two full walks over the 150-game corpus (~20s); shared by both J1 tests."""

    return measure_belief_render_parity(Path("replays/ml_corpus/9p2i"))


def test_j1_fold_fidelity_is_exact_on_the_9p2i_corpus(
    corpus_parity: BeliefRenderParity,
) -> None:
    """Fold fidelity is EXACT on every compared cell — the SAFETY half of J1.

    Split out of the census test at the PR #301 review: these three assertions are
    not pins that move with a re-record, they are the invariant that the offline
    reconstruction still reproduces the production belief fold. Leaving them inside
    the xfailed census test meant a genuine parity/reconstruction break on the new
    corpus would surface as an expected failure and be waved through — and 18.14
    would then re-fit on corrupted live-parity features. They must hold on ANY
    corpus, so they stay LIVE across the baseline-6 re-record; only the numeric
    census below is deferred.
    """

    assert corpus_parity.raw_mismatches == 0
    assert corpus_parity.trust_mismatches == 0
    assert corpus_parity.max_raw_abs_delta == 0.0
    # A vacuous pass (an empty walk) would satisfy the three above; require the
    # walk to have actually compared something.
    assert corpus_parity.games_total == 150
    assert corpus_parity.cells_compared > 0


def test_j1_live_parity_divergence_is_measured_on_the_9p2i_corpus(
    corpus_parity: BeliefRenderParity,
) -> None:
    """The J1 live-parity CENSUS the report records (§2.1), pinned end-to-end.

    The graduated J1 render clamp (unconditional since the 16.17 baseline-5
    record) makes the live-served scalar diverge from the raw ``belief_suspicion``
    column the fit reads on exactly the measured cells — the recorded train/serve
    skew the report states beside the verdict. The fidelity INVARIANTS are asserted
    live in the test above, not here.

    RE-PINNED (not xfailed) at Task 18.13's baseline-6 re-record. Every number here
    derives from the corpus bytes ALONE — ``measure_belief_render_parity`` reads no
    fitted artifact — so it is honestly re-derivable now, and deferring it to 18.14
    behind an expected failure would let the train/serve skew drift unrecorded in
    the meantime (PR #301 review). The skew SHRANK on the graduated meeting layer:
    divergent cells 280 -> 141 of 14 326 compared, and the max divergence 0.11 ->
    0.06.
    """

    parity = corpus_parity
    assert parity.meetings_total == 432  # was 463
    assert parity.rows_total == 2479  # was 2726
    assert parity.cells_compared == 12600  # was 14326
    assert parity.j1_divergent_cells == 61  # was 141
    assert parity.j1_divergent_rows == 57  # was 130
    assert parity.j1_divergent_fit_cells == 42  # was 113
    assert parity.j1_divergent_test_cells == 19  # was 28
    assert parity.j1_max_abs_divergence == pytest.approx(0.06, abs=1e-9)
