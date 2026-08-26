"""Unit tests for eval/funnel.py's Task 16.10 pooling-folds extension region.

Two layers, mirroring tests/eval/test_funnel.py:

* scripted-fixture unit tests over hand-built ``_VJMeeting`` carriers,
  exercising each pooling fold in isolation AND proving every fold can MOVE
  on a synthetic fixture (the DoD's "an instrument that cannot move is not an
  instrument");
* the baseline-5 REPRODUCTION PINS — ``compute_pooling_funnel`` over the
  committed 9p2i / 4p1i bytes. 16.15's roll-call elicitation has now LANDED, so
  the whereabouts channel is LIVE (non-zero claims, defined coverage, a defined
  lie rate) alongside the folds whose inputs already existed (vouches,
  groundable sightings, the unplaced share).

The reproduction pins were re-derived from the committed bytes on the Task
16.17 baseline-5 re-record (model Qwen/Qwen3.6-27B, prompt set qwen3_6_27b.v3;
9p2i: 165 meetings / 50 games, 4p1i: 39 meetings / 50 games) via eval.funnel.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.entities import PlayerId, Role
from eval.funnel import (
    FunnelReconstructionError,
    MeetingPoolingRow,
    PoolingFunnelReport,
    _absence_set,
    _grounded_vouch_set,
    _pooling_row,
    _roll_call_placed,
    _VJMeeting,
    _vouch_census,
    _whereabouts_claim_event_ids,
    _whereabouts_lies_detected,
    compute_pooling_funnel,
)
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    SightingRecord,
    TurnKind,
    WhereaboutsClaim,
)
from meetings.transcript import MeetingTriggerKind

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"

# Canonical rooms so the transcript helpers' room parsing and the relevance
# gate see real map locations (spawn-window ticks are avoided via tick 10+).
_ROOM_A = "MEDBAY"
_ROOM_B = "ENGINEERING"

# The default scripted-fixture role map: every player of the default living set
# is CREWMATE, so the Task 17.4 breakdown attributes each fixture's placements
# to crew unless a test overrides the map (the impostor-attribution fixture).
_ALL_CREW: dict[PlayerId, Role] = {f"p-{i}": "CREWMATE" for i in range(1, 5)}


def _turn(
    speaker: PlayerId,
    index: int,
    *,
    observations: tuple[ObservationClaim, ...] = (),
    free_text: str = "...",
    turn_kind: TurnKind | None = None,
    reply_to: str | None = None,
) -> MeetingTurn:
    kind: TurnKind = (
        turn_kind if turn_kind is not None else ("opening" if index == 0 else "opt_in")
    )
    return MeetingTurn(
        turn_id=f"m-0:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind=kind,
        reply_to=reply_to,
        observations=observations,
        claims=(),
        free_text=free_text,
    )


def _meeting(
    *,
    turns: tuple[MeetingTurn, ...] = (),
    living: frozenset[PlayerId] = frozenset({"p-1", "p-2", "p-3", "p-4"}),
    contradictions: tuple[ContradictionRef, ...] = (),
    sighting_records: dict[PlayerId, tuple[SightingRecord, ...]] | None = None,
    trigger_kind: MeetingTriggerKind = "emergency",
) -> _VJMeeting:
    return _VJMeeting(
        seed=0,
        meeting_id="m-0",
        tick=20,
        trigger_kind=trigger_kind,
        triggered_by="p-1",
        outcome="SKIPPED",
        ejected=None,
        living=living,
        transcript=MeetingTranscript(turns=turns),
        ballots=(),
        contradictions=contradictions,
        llm_calls=(),
        suspicion_graph_by_voter={},
        sighting_records_by_speaker=sighting_records or {},
        observation_ids_by_voter={},
        fellow_impostor_ids_by_voter={},
    )


# --------------------------------------------------------------------------- #
# Roll-call coverage (whereabouts channel ONLY)                                #
# --------------------------------------------------------------------------- #


def test_roll_call_counts_only_whereabouts_self_placements() -> None:
    turns = (
        _turn(
            "p-1",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
        # A saw_player placement is NOT a roll-call answer.
        _turn(
            "p-2",
            1,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-3", room=_ROOM_B
                ),
            ),
        ),
    )
    placed = _roll_call_placed(_meeting(turns=turns))
    assert placed == frozenset({"p-1"})


def test_roll_call_moves_on_synthetic_fixture() -> None:
    turns = tuple(
        _turn(
            pid,
            index,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        )
        for index, pid in enumerate(("p-1", "p-2"))
    )
    row = _pooling_row(_meeting(turns=turns), roles=_ALL_CREW)
    assert row.whereabouts_claims == 2
    assert row.roll_call_placed == 2
    assert row.roll_call_coverage == pytest.approx(0.5)


def test_roll_call_reads_zero_without_whereabouts() -> None:
    row = _pooling_row(_meeting(turns=(_turn("p-1", 0),)), roles=_ALL_CREW)
    assert row.whereabouts_claims == 0
    assert row.roll_call_placed == 0
    assert row.roll_call_coverage == 0.0


def test_dead_speaker_whereabouts_never_counts() -> None:
    turns = (
        _turn(
            "p-9",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
    )
    meeting = _meeting(turns=turns)  # p-9 not in the living set
    assert _roll_call_placed(meeting) == frozenset()
    assert _whereabouts_claim_event_ids(meeting) == ()


# --------------------------------------------------------------------------- #
# Vouch rate + GROUNDED-vouch rate                                             #
# --------------------------------------------------------------------------- #


def test_vouch_census_counts_other_living_subjects_only() -> None:
    turns = (
        _turn(
            "p-1",
            0,
            observations=(
                # A vouch: another living player.
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-2", room=_ROOM_A
                ),
                # Self-placement is the whereabouts channel, never a vouch.
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-1", room=_ROOM_A
                ),
                # A dead / non-roster subject places no living player.
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-9", room=_ROOM_A
                ),
            ),
        ),
    )
    observations, subjects = _vouch_census(_meeting(turns=turns))
    assert observations == 1
    assert subjects == frozenset({"p-2"})


def test_grounded_vouch_requires_matching_speaker_record() -> None:
    turns = (
        _turn(
            "p-1",
            0,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-2", room=_ROOM_A
                ),
            ),
        ),
    )
    grounded_fixture = _meeting(
        turns=turns,
        sighting_records={
            "p-1": (SightingRecord(subject="p-2", room=_ROOM_A, tick=10),)
        },
    )
    assert _grounded_vouch_set(grounded_fixture) == frozenset({"p-2"})
    # The same spoken vouch with NO matching record grounds nothing (the
    # anti-collusion floor): a fabricated vouch contributes zero.
    ungrounded_fixture = _meeting(turns=turns, sighting_records={})
    assert _grounded_vouch_set(ungrounded_fixture) == frozenset()
    wrong_room = _meeting(
        turns=turns,
        sighting_records={
            "p-1": (SightingRecord(subject="p-2", room=_ROOM_B, tick=10),)
        },
    )
    assert _grounded_vouch_set(wrong_room) == frozenset()


def test_vouch_rates_move_on_synthetic_fixture() -> None:
    turns = (
        _turn(
            "p-1",
            0,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-2", room=_ROOM_A
                ),
                SawPlayerObservation(
                    type="saw_player", tick=11, subject="p-3", room=_ROOM_A
                ),
            ),
        ),
    )
    row = _pooling_row(
        _meeting(
            turns=turns,
            sighting_records={
                "p-1": (SightingRecord(subject="p-2", room=_ROOM_A, tick=10),)
            },
        ),
        roles=_ALL_CREW,
    )
    assert row.vouch_observations == 2
    assert row.vouched_subjects == 2
    assert row.vouch_rate == pytest.approx(0.5)
    assert row.grounded_vouch_subjects == 1
    assert row.grounded_vouch_rate == pytest.approx(0.25)


# --------------------------------------------------------------------------- #
# Absence set                                                                  #
# --------------------------------------------------------------------------- #


def test_absence_set_is_the_unplaced_living_complement() -> None:
    turns = (
        # p-1 self-places (whereabouts); p-2 is placed by p-3's sighting.
        _turn(
            "p-1",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
        _turn(
            "p-3",
            1,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-2", room=_ROOM_B
                ),
            ),
        ),
    )
    absence = _absence_set(_meeting(turns=turns))
    # The sighting's SPEAKER states, it does not self-place; p-4 said nothing.
    assert absence == ("p-3", "p-4")


def test_absence_set_shrinks_as_placements_land() -> None:
    empty = _pooling_row(_meeting(turns=()), roles=_ALL_CREW)
    assert empty.absence_set_size == 4
    placed = _pooling_row(
        _meeting(
            turns=(
                _turn(
                    "p-1",
                    0,
                    observations=(
                        WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),
                    ),
                ),
            )
        ),
        roles=_ALL_CREW,
    )
    assert placed.absence_set_size == 3


# --------------------------------------------------------------------------- #
# Whereabouts-lie detection                                                    #
# --------------------------------------------------------------------------- #


def _whereabouts_lie_fixture() -> _VJMeeting:
    turns = (
        _turn(
            "p-1",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
        _turn(
            "p-2",
            1,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-1", room=_ROOM_B
                ),
            ),
        ),
    )
    # The recorded flag names the whereabouts claim by its event id — the
    # exact ``turn:{turn_id}:whereabouts:{index}`` shape the production
    # detector mints for the degenerate single-tick self-alibi.
    flag = ContradictionRef(
        contradiction_id="c-0",
        kind="alibi_vs_sighting",
        event_a_id="turn:m-0:turn-0:whereabouts:0",
        event_b_id="turn:m-0:turn-1:obs:0",
        subjects=("p-1",),
        description="whereabouts contradicted by a sighting",
    )
    return _meeting(turns=turns, contradictions=(flag,))


def test_whereabouts_event_ids_match_the_production_detector() -> None:
    """The fold's event-id construction is pinned to the detector's own helper.

    Lie detection matches RECORDED flags by event id, so a drift between this
    fold's ``turn:{turn_id}:whereabouts:{index}`` construction and
    ``meetings.transcript._turn_whereabouts_id`` would silently read 0 on the
    very substrate the instrument exists for — pin the two byte-identical.
    """

    from meetings.transcript import _turn_whereabouts_id

    turn = _turn(
        "p-1",
        0,
        observations=(
            SawPlayerObservation(
                type="saw_player", tick=10, subject="p-2", room=_ROOM_B
            ),
            WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),
        ),
    )
    meeting = _meeting(turns=(turn,))
    # The whereabouts claim sits at observation index 1 — the index is the
    # position in turn.observations, exactly _event_speaker_index's read.
    assert _whereabouts_claim_event_ids(meeting) == (
        _turn_whereabouts_id(turn=turn, index=1),
    )


def test_whereabouts_lie_detected_via_recorded_flag_event_id() -> None:
    meeting = _whereabouts_lie_fixture()
    assert _whereabouts_claim_event_ids(meeting) == ("turn:m-0:turn-0:whereabouts:0",)
    assert _whereabouts_lies_detected(meeting) == 1
    row = _pooling_row(meeting, roles=_ALL_CREW)
    assert row.whereabouts_claims == 1
    assert row.whereabouts_lies_detected == 1


def test_unflagged_whereabouts_claim_is_not_a_detected_lie() -> None:
    turns = (
        _turn(
            "p-1",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
    )
    assert _whereabouts_lies_detected(_meeting(turns=turns)) == 0


def test_lie_rate_aggregates_from_synthetic_rows() -> None:
    row = _pooling_row(_whereabouts_lie_fixture(), roles=_ALL_CREW)
    assert row.whereabouts_lies_detected / row.whereabouts_claims == 1.0


# --------------------------------------------------------------------------- #
# Task 17.4 roll-call uptake breakdown (per-role / per-surface / answered-asked)#
# --------------------------------------------------------------------------- #


def test_impostor_placement_attributes_to_impostor_never_crew() -> None:
    """The DoD role-attribution fixture: an impostor self-placement lands under
    ``roll_call_placed_impostor`` and NEVER under ``roll_call_placed_crew``.

    p-1 is the lone IMPOSTOR and answers roll-call beside a crew answerer
    (p-2); the split identities and the per-role coverage cells decompose the
    aggregate exactly.
    """

    roles: dict[PlayerId, Role] = {
        "p-1": "IMPOSTOR",
        "p-2": "CREWMATE",
        "p-3": "CREWMATE",
        "p-4": "CREWMATE",
    }
    turns = (
        _turn(
            "p-1",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
        _turn(
            "p-2",
            1,
            observations=(WhereaboutsClaim(type="whereabouts", tick=11, room=_ROOM_B),),
        ),
    )
    row = _pooling_row(_meeting(turns=turns), roles=roles)
    # Living split partitions the roster by role and sums back to living.
    assert row.living_crew == 3
    assert row.living_impostor == 1
    assert row.living_crew + row.living_impostor == row.living
    # The impostor placement is attributed to the impostor partition ONLY.
    assert row.roll_call_placed == 2
    assert row.roll_call_placed_crew == 1
    assert row.roll_call_placed_impostor == 1
    assert row.roll_call_placed_crew + row.roll_call_placed_impostor == (
        row.roll_call_placed
    )
    # Per-role coverage is per-role placed / per-role living.
    assert row.roll_call_coverage_crew == pytest.approx(1 / 3)
    assert row.roll_call_coverage_impostor == pytest.approx(1.0)


def test_whereabouts_claims_split_by_carrying_turn_surface() -> None:
    """Claims on opening / reply / opt_in turns land in their surface cells and
    sum to ``whereabouts_claims`` (the same living-speaker filter, per claim)."""

    turns = (
        _turn(
            "p-1",
            0,
            turn_kind="opening",
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
        _turn(
            "p-2",
            1,
            turn_kind="reply",
            reply_to="m-0:turn-0",
            observations=(WhereaboutsClaim(type="whereabouts", tick=11, room=_ROOM_B),),
        ),
        _turn(
            "p-3",
            2,
            turn_kind="opt_in",
            observations=(WhereaboutsClaim(type="whereabouts", tick=12, room=_ROOM_A),),
        ),
    )
    row = _pooling_row(_meeting(turns=turns), roles=_ALL_CREW)
    assert row.whereabouts_claims_opening == 1
    assert row.whereabouts_claims_reply == 1
    assert row.whereabouts_claims_opt_in == 1
    assert (
        row.whereabouts_claims_opening
        + row.whereabouts_claims_reply
        + row.whereabouts_claims_opt_in
        == row.whereabouts_claims
    )


def test_answered_asked_census_separates_silence_from_refusal() -> None:
    """The answered/asked census: a living speaker who does not self-place is
    ASKED but not ANSWERED; a living non-speaker is neither; a dead speaker is
    counted nowhere; and ``roll_call_answered == roll_call_placed``."""

    turns = (
        # p-1 speaks AND self-places → asked and answered.
        _turn(
            "p-1",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
        # p-2 speaks with no whereabouts → asked but not answered (refusal).
        _turn(
            "p-2",
            1,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=10, subject="p-3", room=_ROOM_B
                ),
            ),
        ),
        # p-9 is dead (not in the living set) → counted in neither census.
        _turn(
            "p-9",
            2,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
    )
    # p-3 and p-4 never take the mic → never-took-the-mic, not asked.
    row = _pooling_row(_meeting(turns=turns), roles=_ALL_CREW)
    assert row.roll_call_asked == 2  # p-1, p-2 (living speakers)
    assert row.roll_call_answered == 1  # p-1 self-placed
    assert row.roll_call_answered == row.roll_call_placed
    assert row.roll_call_answered <= row.roll_call_asked <= row.living


def test_per_role_coverage_is_none_when_role_has_no_living_members() -> None:
    """Per-role coverage is ``None`` (undefined, never ``0.0``) when that role
    has zero living members — the report's None-means-undefined convention."""

    living = frozenset({"p-1", "p-2"})
    roles: dict[PlayerId, Role] = {"p-1": "CREWMATE", "p-2": "CREWMATE"}
    turns = (
        _turn(
            "p-1",
            0,
            observations=(WhereaboutsClaim(type="whereabouts", tick=10, room=_ROOM_A),),
        ),
    )
    row = _pooling_row(_meeting(turns=turns, living=living), roles=roles)
    assert row.living_impostor == 0
    assert row.roll_call_coverage_impostor is None
    assert row.living_crew == 2
    assert row.roll_call_coverage_crew == pytest.approx(0.5)


def test_missing_role_for_living_player_raises() -> None:
    """A living player absent from the role map fails loud (no silent
    fallback) — the per-role breakdown cannot attribute their uptake."""

    partial: dict[PlayerId, Role] = {
        "p-1": "CREWMATE",
        "p-2": "CREWMATE",
        "p-3": "CREWMATE",
    }  # p-4 (living) is missing
    with pytest.raises(FunnelReconstructionError):
        _pooling_row(_meeting(turns=(_turn("p-1", 0),)), roles=partial)


# --------------------------------------------------------------------------- #
# Report invariants                                                            #
# --------------------------------------------------------------------------- #


def test_pooling_row_is_frozen_and_round_trips() -> None:
    row = _pooling_row(_whereabouts_lie_fixture(), roles=_ALL_CREW)
    assert isinstance(row, MeetingPoolingRow)
    with pytest.raises(ValidationError):
        row.living = 99
    assert MeetingPoolingRow.model_validate_json(row.model_dump_json()) == row


# --------------------------------------------------------------------------- #
# Walk — fail-loud on a drifted state hash (the 15.3 walk's guard, mirrored)   #
# --------------------------------------------------------------------------- #


def test_vj_walk_raises_on_corrupted_state_hash(tmp_path: Path) -> None:
    """A tampered recorded ``state_hash`` fails the memory-augmented walk loud."""

    import json

    from engine.world import load_canonical_map
    from eval.funnel import FunnelReconstructionError, _walk_game_vj

    src = _FOUR / "replay-seed-0.jsonl"
    dst = tmp_path / "replay-seed-0.jsonl"
    lines = src.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["state_hash"] = "0" * 64
    lines[0] = json.dumps(first)
    dst.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with pytest.raises(FunnelReconstructionError):
        _walk_game_vj(
            dst,
            seed=0,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            roles={f"p-{i}": "CREWMATE" for i in range(1, 5)},
            game_map=load_canonical_map(),
        )


# --------------------------------------------------------------------------- #
# Baseline-4 reproduction pins (committed bytes)                               #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def nine_pooling() -> PoolingFunnelReport:
    return compute_pooling_funnel(_NINE)


@pytest.fixture(scope="module")
def four_pooling() -> PoolingFunnelReport:
    return compute_pooling_funnel(_FOUR)


def test_9p2i_pooling_reads_the_live_roll_call_channel(
    nine_pooling: PoolingFunnelReport,
) -> None:
    # 16.15's roll-call elicitation has landed on baseline 5: the whereabouts
    # channel is now populated (non-zero claims, defined coverage), and the lie
    # rate is DEFINED (not None) — lies detected over claims placed.
    assert nine_pooling.games_total == 50
    assert nine_pooling.meetings_total == 152  # was 165
    assert nine_pooling.whereabouts_claims_total == 763  # was 843
    assert nine_pooling.roll_call_meetings == 152  # was 165
    assert nine_pooling.roll_call_coverage_mean == pytest.approx(
        0.8590225563909776
    )  # was 0.8628354978354977
    assert nine_pooling.whereabouts_lies_detected == 29  # was 50
    assert nine_pooling.whereabouts_lie_detection_rate == pytest.approx(
        0.03800786369593709
    )


def test_9p2i_pooling_reproduces_baseline_5_exactly(
    nine_pooling: PoolingFunnelReport,
) -> None:
    # Vouching and the unplaced share on committed bytes. Re-derived from the
    # committed baseline-5 9p2i bytes (Task 16.17 re-record) via eval.funnel.
    assert nine_pooling.vouch_observations_total == 819  # was 1389
    assert nine_pooling.vouch_rate_mean == pytest.approx(
        0.5555372807017543
    )  # was 0.709040404040404
    assert nine_pooling.grounded_vouch_rate_mean == pytest.approx(
        0.4753054511278195
    )  # was 0.587034632034632
    assert nine_pooling.grounded_vouch_share == pytest.approx(
        0.8622754491017964
    )  # was 0.8333333333333334
    assert nine_pooling.absence_set_size_mean == pytest.approx(
        0.3881578947368421
    )  # was 0.22424242424242424
    assert nine_pooling.absence_set_size_median == pytest.approx(0.0)
    assert dict(nine_pooling.absence_set_size_histogram) == {0: 94, 1: 57, 2: 1}
    assert len(nine_pooling.per_meeting) == 152


def test_4p1i_pooling_reproduces_baseline_5_exactly(
    four_pooling: PoolingFunnelReport,
) -> None:
    # Re-derived from the committed baseline-5 4p1i bytes (Task 16.17
    # re-record) via eval.funnel; 16.15's roll-call elicitation has landed so
    # the whereabouts channel reads live here too (non-zero claims, defined
    # coverage and lie rate).
    assert four_pooling.games_total == 50
    assert four_pooling.meetings_total == 40  # was 39
    assert four_pooling.whereabouts_claims_total == 85  # was 86
    assert four_pooling.roll_call_coverage_mean == pytest.approx(
        0.7083333333333333
    )  # was 0.735042735042735
    assert four_pooling.whereabouts_lie_detection_rate == pytest.approx(0.0)
    assert four_pooling.vouch_observations_total == 55
    assert four_pooling.vouch_rate_mean == pytest.approx(0.3583333333333333)
    assert four_pooling.grounded_vouch_rate_mean == pytest.approx(0.14166666666666666)
    assert four_pooling.grounded_vouch_share == pytest.approx(0.3953488372093023)
    assert four_pooling.absence_set_size_mean == pytest.approx(0.625)
    assert dict(four_pooling.absence_set_size_histogram) == {0: 15, 1: 25}


def test_9p2i_pooling_roll_call_breakdown_reproduces_baseline_5(
    nine_pooling: PoolingFunnelReport,
) -> None:
    # Task 17.4 per-role / per-surface / answered-asked breakdown. Re-derived
    # from the committed baseline-5 9p2i bytes via eval.funnel — the breakdown
    # DECOMPOSES the 0.863 aggregate coverage (audits/audit-phase-16-close.md
    # §6), it moves no existing cell: the role split shows the answer rate is
    # STRUCTURED (crew 0.996 vs impostor 0.455 — impostors refuse by prompt
    # design), not uniform silence.
    assert nine_pooling.roll_call_placed_crew_total == 652  # was 723
    assert nine_pooling.roll_call_placed_impostor_total == 104  # was 120
    # The placed split totals partition the answered total exactly.
    assert (
        nine_pooling.roll_call_placed_crew_total
        + nine_pooling.roll_call_placed_impostor_total
        == nine_pooling.roll_call_answered_total
    )
    assert nine_pooling.roll_call_coverage_crew_mean == pytest.approx(1.0)
    assert nine_pooling.roll_call_coverage_impostor_mean == pytest.approx(0.4375)
    assert nine_pooling.whereabouts_claims_opening_total == 157
    assert nine_pooling.whereabouts_claims_reply_total == 79
    assert nine_pooling.whereabouts_claims_opt_in_total == 527
    # The surface split totals partition the set-wide claims total exactly.
    assert (
        nine_pooling.whereabouts_claims_opening_total
        + nine_pooling.whereabouts_claims_reply_total
        + nine_pooling.whereabouts_claims_opt_in_total
        == nine_pooling.whereabouts_claims_total
    )
    assert nine_pooling.roll_call_asked_total == 871
    assert nine_pooling.roll_call_answered_total == 756
    assert nine_pooling.roll_call_answer_rate == pytest.approx(0.8679678530424799)


def test_4p1i_pooling_roll_call_breakdown_reproduces_baseline_5(
    four_pooling: PoolingFunnelReport,
) -> None:
    # Re-derived from the committed baseline-5 4p1i bytes via eval.funnel; the
    # same structured-refusal signal on the smaller roster (crew 1.0 vs
    # impostor 0.205).
    assert four_pooling.roll_call_placed_crew_total == 80  # was 78
    assert four_pooling.roll_call_placed_impostor_total == 5  # was 8
    assert (
        four_pooling.roll_call_placed_crew_total
        + four_pooling.roll_call_placed_impostor_total
        == four_pooling.roll_call_answered_total
    )
    assert four_pooling.roll_call_coverage_crew_mean == pytest.approx(1.0)
    assert four_pooling.roll_call_coverage_impostor_mean == pytest.approx(0.125)
    assert four_pooling.whereabouts_claims_opening_total == 40
    assert four_pooling.whereabouts_claims_reply_total == 8
    assert four_pooling.whereabouts_claims_opt_in_total == 37
    assert (
        four_pooling.whereabouts_claims_opening_total
        + four_pooling.whereabouts_claims_reply_total
        + four_pooling.whereabouts_claims_opt_in_total
        == four_pooling.whereabouts_claims_total
    )
    assert four_pooling.roll_call_asked_total == 120
    assert four_pooling.roll_call_answered_total == 85
    assert four_pooling.roll_call_answer_rate == pytest.approx(0.7083333333333334)


def test_pooling_per_row_decomposition_identities(
    nine_pooling: PoolingFunnelReport,
    four_pooling: PoolingFunnelReport,
) -> None:
    # The Task 17.4 split identities hold on EVERY committed per-meeting row of
    # both sets, not only the synthetic fixtures: the role split, the surface
    # split, and the answered/asked census all decompose their aggregate.
    for report in (nine_pooling, four_pooling):
        for row in report.per_meeting:
            assert row.living_crew + row.living_impostor == row.living
            assert (
                row.roll_call_placed_crew + row.roll_call_placed_impostor
                == row.roll_call_placed
            )
            assert (
                row.whereabouts_claims_opening
                + row.whereabouts_claims_reply
                + row.whereabouts_claims_opt_in
                == row.whereabouts_claims
            )
            assert row.roll_call_answered == row.roll_call_placed
            assert row.roll_call_answered <= row.roll_call_asked <= row.living


def test_pooling_report_round_trips(four_pooling: PoolingFunnelReport) -> None:
    text = four_pooling.model_dump_json()
    assert PoolingFunnelReport.model_validate_json(text) == four_pooling
