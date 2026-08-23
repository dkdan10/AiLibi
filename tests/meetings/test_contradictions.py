"""Tests for :func:`meetings.transcript.detect_contradictions` (Task 8.7).

The contract mirrors DESIGN.md §5.4 + §6.4, now indexing over the single
ordered ``transcript.turns`` list (every alibi claim and ``saw_player``
observation appears on a :class:`MeetingTurn`, regardless of turn-kind):

* The detector flags pairs of events that cannot both be true:
  ``alibi_conflict`` for two alibis that place the same agent in
  different rooms over overlapping ticks, and ``alibi_vs_sighting`` for
  an alibi contradicted by a ``saw_player`` observation elsewhere within
  the alibi range.
* Flags are *information*, not verdicts -- the detector reports only what
  cannot both be true.
* The detector is deterministic: re-running on the same transcript
  produces byte-identical flags with a canonical ``contradiction_id``.
* Event ids reference the contributing turn
  (``turn:{turn_id}:claim:{i}`` / ``turn:{turn_id}:obs:{i}``).
"""

from __future__ import annotations

import functools
from dataclasses import dataclass
from pathlib import Path

import pytest

from meetings.constants import GROUNDED_PROSECUTION_MIN_SOURCES
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    MoveWitnessRecord,
    ObservationClaim,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    VentWitnessRecord,
    WhereaboutsClaim,
)
from meetings.transcript import (
    CANONICAL_ROOMS,
    ENV_GROUNDED_PROSECUTION,
    ENV_MOVEMENT_CLAIM_SHAPE,
    ENV_VENT_PLACEMENT_CONTRADICTIONS,
    ENV_WHEREABOUTS_INTERIOR_FLAGS,
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_ADVERSARIAL,
    WEAK_REASON_BOUNDARY_OVERLAP,
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_KILL_SCENE,
    WEAK_REASON_LONE_GROUNDED_SOURCE,
    WEAK_REASON_NARROW_WINDOW,
    WEAK_REASON_SELF_PAIR,
    WEAK_REASON_UNGROUNDED_SIGHTING,
    _event_speaker_index,
    _turn_observation_id,
    _turn_whereabouts_id,
    absent_players,
    canonical_rooms,
    detect_contradictions,
    grounded_prosecution_enabled,
    is_weak_contradiction,
    movement_claim_shape_enabled,
    reconstruct_stated_paths,
    vent_placement_contradictions_enabled,
    whereabouts_interior_flags_enabled,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries

# --- Builders --------------------------------------------------------------


def _alibi(*, subject: str, from_tick: int, to_tick: int, room: str) -> AlibiClaim:
    return AlibiClaim(
        type="alibi",
        subject=subject,
        from_tick=from_tick,
        to_tick=to_tick,
        room=room,
    )


def _saw(
    *, tick: int, subject: str, room: str, co_present: tuple[str, ...] = ()
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player",
        tick=tick,
        subject=subject,
        room=room,
        co_present=co_present,
    )


def _turn(
    *,
    turn_index: int,
    speaker: str,
    turn_kind: str = "opening",
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text=f"turn {turn_index} from {speaker}",
    )


def _whereabouts(*, tick: int, room: str) -> WhereaboutsClaim:
    # A roll-call self-placement ("I was in ``room`` at ``tick``"). Indexed by
    # :func:`_iter_alibis` as a DEGENERATE SINGLE-TICK SELF-ALIBI (subject is the
    # speaker, ``from_tick == to_tick == tick``) -- the Task 18.9 lever-1 class.
    return WhereaboutsClaim(type="whereabouts", tick=tick, room=room)


def _saw_vent(*, tick: int, subject: str, room: str) -> SawVentObservation:
    return SawVentObservation(type="saw_vent", tick=tick, subject=subject, room=room)


def _vent_record(*, tick: int, subject: str, room: str) -> VentWitnessRecord:
    return VentWitnessRecord(subject=subject, room=room, tick=tick)


def _saw_move(
    *, tick: int, subject: str, from_room: str, to_room: str
) -> SawMoveObservation:
    # A spoken transition: the subject was in ``from_room`` at ``tick - 1`` and
    # in ``to_room`` at ``tick``.
    return SawMoveObservation(
        type="saw_move",
        tick=tick,
        subject=subject,
        from_room=from_room,
        to_room=to_room,
    )


def _move_record(
    *, tick: int, subject: str, from_room: str, to_room: str
) -> MoveWitnessRecord:
    return MoveWitnessRecord(
        subject=subject, from_room=from_room, to_room=to_room, tick=tick
    )


_MOVEMENT_ON = {ENV_MOVEMENT_CLAIM_SHAPE: "1"}


# --- Empty / non-contradictory transcripts ---------------------------------


class TestNoContradictions:
    def test_empty_transcript_returns_empty_tuple(self) -> None:
        assert detect_contradictions(MeetingTranscript()) == ()

    def test_single_alibi_cannot_self_conflict(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            claims=(_alibi(subject="p-1", from_tick=100, to_tick=200, room="STORAGE"),),
        )
        assert detect_contradictions(MeetingTranscript(turns=(turn,))) == ()

    def test_same_room_alibis_do_not_conflict(self) -> None:
        # Two agents corroborating that p-3 was in Storage at the same time
        # is *consistent* evidence, not a contradiction.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=120, to_tick=180, room="STORAGE"),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_non_overlapping_ranges_do_not_conflict(self) -> None:
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            claims=(
                _alibi(subject="p-1", from_tick=100, to_tick=150, room="STORAGE"),
                _alibi(subject="p-1", from_tick=160, to_tick=200, room="ADMIN"),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=(turn,))) == ()

    def test_alibis_about_different_subjects_do_not_conflict(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-4", from_tick=100, to_tick=200, room="ADMIN"),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_sighting_outside_alibi_range_is_not_flagged(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=250, subject="p-3", room="CAFETERIA"),),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_sighting_matching_alibi_is_corroboration_not_conflict(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=150, subject="p-3", room="STORAGE"),),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()

    def test_non_alibi_claims_are_ignored(self) -> None:
        # Accusations and corroborations carry no location data; pairing
        # them with a saw_player observation must not raise or emit a flag.
        turn = _turn(
            turn_index=0,
            speaker="p-1",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-5",
                    confidence=0.7,
                    reason="suspicious behaviour near MedBay",
                ),
                CorroborationClaim(
                    type="corroboration",
                    supports="p-3",
                    on_tick=150,
                    reason="saw them in Storage",
                ),
            ),
            observations=(_saw(tick=150, subject="p-3", room="STORAGE"),),
        )
        assert detect_contradictions(MeetingTranscript(turns=(turn,))) == ()

    def test_non_sighting_observations_are_ignored(self) -> None:
        # Only ``saw_player`` is cross-referenced against alibis;
        # ``completed_task`` / ``found_body`` carry the reporter's location,
        # not the alibi subject's.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
                observations=(_saw(tick=150, subject="p-5", room="STORAGE"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                observations=(
                    CompletedTaskObservation(
                        type="completed_task",
                        tick=150,
                        task_id="wiring",
                        room="ELECTRICAL",
                    ),
                    FoundBodyObservation(
                        type="found_body",
                        tick=200,
                        body_of="p-4",
                        room="MEDBAY",
                    ),
                ),
            ),
        )
        assert detect_contradictions(MeetingTranscript(turns=turns)) == ()


# --- alibi_conflict --------------------------------------------------------


class TestAlibiConflict:
    def test_two_alibis_same_subject_different_rooms_overlapping_ticks(
        self,
    ) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        flag = flags[0]
        assert isinstance(flag, ContradictionRef)
        assert flag.kind == "alibi_conflict"
        assert flag.subjects == ("p-3",)
        # Source ids reference the contributing turns in canonical (sorted)
        # order so replays remain byte-stable.
        assert flag.event_a_id <= flag.event_b_id
        assert flag.event_a_id == "turn:m-1:turn-0:claim:0"
        assert flag.event_b_id == "turn:m-1:turn-1:claim:0"
        assert "STORAGE" in flag.description
        assert "CAFETERIA" in flag.description
        assert "p-3" in flag.description

    def test_self_contradicting_turn_is_flagged(self) -> None:
        # A single speaker listing two overlapping alibis with different
        # rooms is a self-contradiction the detector must catch.
        turn = _turn(
            turn_index=0,
            speaker="p-3",
            claims=(
                _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                _alibi(subject="p-3", from_tick=180, to_tick=220, room="ADMIN"),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=(turn,)))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert flags[0].subjects == ("p-3",)
        assert flags[0].event_a_id == "turn:m-1:turn-0:claim:0"
        assert flags[0].event_b_id == "turn:m-1:turn-0:claim:1"

    def test_boundary_overlap_is_a_conflict(self) -> None:
        # AlibiClaim ranges are inclusive, so alibis sharing a boundary tick
        # are mutually exclusive.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=150, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=200, room="ADMIN"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"

    def test_alibi_in_later_turn_conflicts_with_alibi_in_opening(self) -> None:
        # Alibis can be raised on any turn (opening, reply, opt_in); the
        # detector sees every turn surface.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    turn_kind="opening",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-2",
                    turn_kind="reply",
                    claims=(
                        _alibi(subject="p-3", from_tick=150, to_tick=180, room="ADMIN"),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert {flags[0].event_a_id, flags[0].event_b_id} == {
            "turn:m-1:turn-0:claim:0",
            "turn:m-1:turn-1:claim:0",
        }


# --- alibi_vs_sighting -----------------------------------------------------


class TestAlibiVsSighting:
    def test_sighting_inside_alibi_range_different_room_is_flagged(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=150, subject="p-3", room="CAFETERIA"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        flag = flags[0]
        assert flag.kind == "alibi_vs_sighting"
        assert flag.subjects == ("p-3",)
        assert flag.event_a_id <= flag.event_b_id
        assert {flag.event_a_id, flag.event_b_id} == {
            "turn:m-1:turn-0:claim:0",
            "turn:m-1:turn-1:obs:0",
        }
        assert "STORAGE" in flag.description
        assert "CAFETERIA" in flag.description
        assert "p-3" in flag.description

    def test_sighting_at_alibi_boundary_is_flagged(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=200, subject="p-3", room="CAFETERIA"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))
        assert len(flags) == 1
        assert flags[0].kind == "alibi_vs_sighting"

    def test_multiple_sightings_each_emit_a_flag(self) -> None:
        turns = (
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-5",
                observations=(_saw(tick=120, subject="p-3", room="CAFETERIA"),),
            ),
            _turn(
                turn_index=2,
                speaker="p-7",
                observations=(_saw(tick=180, subject="p-3", room="ADMIN"),),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))
        assert len(flags) == 2
        assert all(flag.kind == "alibi_vs_sighting" for flag in flags)


# --- alibi_vs_physical (Task 13.4, report-phase-b-plan B3/B4) ---------------


def _saw_player_obs_ids(transcript: MeetingTranscript) -> set[str]:
    """Every ``saw_player`` observation id in the transcript (id-format mirror).

    Mirrors ``meetings.transcript._turn_observation_id`` so the firewall
    assertion below checks an ``alibi_vs_physical`` flag's placement event id
    against the public ``saw_player`` observations it must trace to -- with no
    reach into the belief layer (a leak test does not scan beliefs, so this is
    the guard that every placement is transcript-derived).
    """

    return {
        f"turn:{turn.turn_id}:obs:{index}"
        for turn in transcript.turns
        for index, obs in enumerate(turn.observations)
        if isinstance(obs, SawPlayerObservation)
    }


def _alibi_claim_ids(transcript: MeetingTranscript) -> set[str]:
    """Every ``alibi`` claim id in the transcript (id-format mirror)."""

    return {
        f"turn:{turn.turn_id}:claim:{index}"
        for turn in transcript.turns
        for index, claim in enumerate(turn.claims)
        if isinstance(claim, AlibiClaim)
    }


class TestAlibiVsPhysical:
    """The inferential ``alibi_vs_physical`` kind (Task 13.4).

    A subject's OWN stated alibi physically contradicted by independent
    CO-PRESENCE placements (the subject named in another player's ``saw_player``
    co-presence list) reconstructed from public testimony. STRONG only under the
    two-source conjunction: the alibi is uncorroborated AND
    ``PHYSICAL_CONTRADICTION_MIN_VOICES`` (2) distinct non-adversarial voices
    place the subject elsewhere at strictly interior ticks; a LONE contradicting
    voice emits WEAK (informs, cannot eject alone). Direct sightings of the
    subject stay the 9.7 weak ``alibi_vs_sighting`` band.
    """

    def _two_voice_conjunction(self) -> MeetingTranscript:
        # p-3's OWN alibi (STORAGE) physically contradicted by two independent
        # co-presence placements in EAST_HALL: p-5 sights p-1 (co-present p-3)
        # and p-7 sights p-2 (co-present p-3). Nobody places p-3 in STORAGE
        # after spawn -> uncorroborated; both co-presence ticks are interior.
        return MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )

    def test_two_source_co_presence_conjunction_is_strong(self) -> None:
        flags = detect_contradictions(self._two_voice_conjunction())
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        # One flag per contradicting co-presence placement (two voices).
        assert len(physical) == 2
        for flag in physical:
            assert flag.subjects == ("p-3",)
            # STRONG by construction: the physical detector mints no weak marker.
            assert is_weak_contradiction(flag) is False
            assert "p-3" in flag.description
            assert "EAST_HALL" in flag.description
            assert "STORAGE" in flag.description

    def test_every_physical_flag_traces_to_a_saw_player(self) -> None:
        # The firewall assertion (DoD): no alibi_vs_physical flag references a
        # placement that is not a public transcript saw_player, and its alibi
        # side is a real alibi claim -- so the flag is transcript-derived end to
        # end (never a belief-layer artifact).
        transcript = self._two_voice_conjunction()
        flags = detect_contradictions(transcript)
        obs_ids = _saw_player_obs_ids(transcript)
        claim_ids = _alibi_claim_ids(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        assert physical  # the scenario does emit flags to check
        for flag in physical:
            # event_a is the subject's alibi claim; event_b the co-presence
            # sighting (canonicalised order may swap them, so check membership).
            assert flag.event_a_id in claim_ids or flag.event_a_id in obs_ids
            assert flag.event_b_id in claim_ids or flag.event_b_id in obs_ids
            placement_ids = {flag.event_a_id, flag.event_b_id} - claim_ids
            assert placement_ids, "a physical flag must reference a saw_player"
            assert placement_ids <= obs_ids

    def test_lone_co_presence_voice_is_weak_not_strong(self) -> None:
        # A single contradicting voice is below the two-source bar: it emits a
        # WEAK alibi_vs_physical (informs) that cannot cross the gate alone.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        assert len(physical) == 1
        assert is_weak_contradiction(physical[0]) is True
        assert physical[0].subjects == ("p-3",)

    def test_corroborated_alibi_suppresses_physical(self) -> None:
        # An independent voice places p-3 INSIDE the STORAGE alibi (co-placement
        # agreement, the crewmate shape) -> the alibi is corroborated, so even
        # two contradicting voices mint no physical flag (the role-gate).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=3,
                    speaker="p-8",
                    observations=(
                        _saw(
                            tick=140,
                            subject="p-9",
                            room="STORAGE",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert not [f for f in flags if f.kind == "alibi_vs_physical"]

    def test_adversarial_voice_does_not_count_toward_the_conjunction(self) -> None:
        # p-7 places p-3 elsewhere but also ACCUSES p-3 (across the accusation
        # chain) -> the 13.3 adversarial guard drops p-7's voice, leaving one
        # non-adversarial voice: below the two-source bar, so no STRONG flag (the
        # lone p-5 voice stays weak).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    turn_kind="reply",
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-3",
                            confidence=0.8,
                            reason="placed p-3 away from their alibi",
                        ),
                    ),
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        # No STRONG flag: p-7's adversarial voice did not promote the conjunction.
        assert all(is_weak_contradiction(f) is True for f in physical)

    def test_endpoint_tick_co_presence_excluded(self) -> None:
        # A co-presence exactly on the alibi window edge (tick 100) is transit
        # fuzz and excluded, leaving one interior voice -> below the STRONG bar.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=100,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        # Only the interior p-7 voice survives -> weak, never STRONG.
        assert all(is_weak_contradiction(f) is True for f in physical)

    def test_direct_sightings_mint_no_physical_flag(self) -> None:
        # Two DIRECT sightings of the subject contradict the self-alibi, but the
        # physical detector reads co-presence ONLY: those stay the 9.7 weak
        # alibi_vs_sighting band (preserving the audited seed-3 design).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=150, subject="p-3", room="EAST_HALL"),),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(_saw(tick=160, subject="p-3", room="ADMIN"),),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert not [f for f in flags if f.kind == "alibi_vs_physical"]
        assert all(f.kind == "alibi_vs_sighting" for f in flags)

    def test_proxy_alibi_mints_no_physical_flag(self) -> None:
        # The alibi must be the subject's OWN (speaker == subject); a proxy alibi
        # (p-1 vouching for p-3) is the Task 10.6 retargeted-proxy domain, never
        # an alibi_vs_physical.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-4",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert not [f for f in flags if f.kind == "alibi_vs_physical"]

    def test_self_alibi_not_hidden_by_earlier_proxy_echo(self) -> None:
        # A proxy (p-1) states p-3's alibi FIRST, then p-3 restates it. The
        # global echo-dedup keeps the proxy claim and would drop p-3's own; the
        # physical detector de-echoes SELF-statements separately, so it still
        # sees p-3's OWN alibi and the two-voice conjunction fires STRONG against
        # p-3's own claim (not the proxy's).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",  # proxy states it first
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-3",  # subject restates own alibi (an echo)
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=3,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-4",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = detect_contradictions(transcript)
        physical = [f for f in flags if f.kind == "alibi_vs_physical"]
        assert physical
        assert all(is_weak_contradiction(f) is False for f in physical)
        assert all(f.subjects == ("p-3",) for f in physical)
        # The contradicted alibi is p-3's OWN claim (turn 1), never the proxy's.
        referenced = {f.event_a_id for f in physical} | {f.event_b_id for f in physical}
        assert "turn:m-1:turn-1:claim:0" in referenced
        assert "turn:m-1:turn-0:claim:0" not in referenced

    def test_co_presence_anchored_on_hallucinated_subject_is_ignored(self) -> None:
        # Each co-presence of p-3 is anchored on a sighting whose OWN subject is
        # a hallucinated id (p-98 / p-99). Under a roster those sightings are
        # dropped, so their co-presence cannot back a physical flag against p-3.
        roster = frozenset({"p-1", "p-2", "p-3", "p-4", "p-5", "p-6", "p-7"})

        def _scenario(anchor_a: str, anchor_b: str) -> MeetingTranscript:
            return MeetingTranscript(
                turns=(
                    _turn(
                        turn_index=0,
                        speaker="p-3",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=100,
                                to_tick=200,
                                room="STORAGE",
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=1,
                        speaker="p-5",
                        observations=(
                            _saw(
                                tick=150,
                                subject=anchor_a,
                                room="EAST_HALL",
                                co_present=("p-3",),
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=2,
                        speaker="p-7",
                        observations=(
                            _saw(
                                tick=160,
                                subject=anchor_b,
                                room="EAST_HALL",
                                co_present=("p-3",),
                            ),
                        ),
                    ),
                )
            )

        hallucinated = detect_contradictions(_scenario("p-98", "p-99"), roster=roster)
        assert not [f for f in hallucinated if f.kind == "alibi_vs_physical"]
        # Sanity: with roster-valid anchors the SAME shape DOES emit, so it is the
        # roster gate that suppressed above, not the co-presence path itself.
        valid = detect_contradictions(_scenario("p-1", "p-2"), roster=roster)
        assert [f for f in valid if f.kind == "alibi_vs_physical"]

    def test_emergency_trigger_kind_drops_kill_scene_exclusion(self) -> None:
        # An emergency opening carries a (fabricated) found_body in EAST_HALL.
        # With trigger_kind="emergency" the reconstruction does NOT treat that
        # room as a kill scene, so the co-presence placements there count as
        # REGULAR physical placements (no kill-scene marker). Under
        # trigger_kind="report" the same placements are relevance-gated as
        # kill-scene sightings and re-enter only through the 13.5.3 kill-scene
        # recovery (unconditional since Task 14.9), so they carry the
        # kill-scene marker -- the Task 10.11 emergency/report distinction now
        # shows up in the flag CLASS, not in suppression.
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    observations=(
                        FoundBodyObservation(
                            type="found_body",
                            tick=40,
                            body_of="p-9",
                            room="EAST_HALL",
                        ),
                    ),
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-1",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        report = [
            f
            for f in detect_contradictions(transcript, trigger_kind="report")
            if f.kind == "alibi_vs_physical"
        ]
        assert report
        assert all("kill scene" in f.description for f in report)
        emergency = [
            f
            for f in detect_contradictions(transcript, trigger_kind="emergency")
            if f.kind == "alibi_vs_physical"
        ]
        assert emergency
        assert all("kill scene" not in f.description for f in emergency)

    def test_physical_detection_is_deterministic(self) -> None:
        transcript = self._two_voice_conjunction()
        assert detect_contradictions(transcript) == detect_contradictions(transcript)


# --- alibi_vs_physical kill-scene intensification (Task 13.5.3 (b)) ---------


class TestKillSceneStrongFlag:
    """Task 13.5.3 (b) -- the kill-scene intensification of alibi_vs_physical.

    A co-presence placing the accused at the BODY's room within the kill window
    (normally DROPPED by the relevance gate -- presence at the scene must never
    exonerate) is RECOVERED (unconditionally since Task 14.9 -- the adopted
    13.5.3 lever is the default substrate) and made to CONTRADICT an alibi
    placed elsewhere. STRICT (owner-LOCKED): a lone kill-scene placement is
    sub-gate; STRONG needs a second independent source.
    """

    def _body(self, *, room: str = "REACTOR") -> FoundBodyObservation:
        return FoundBodyObservation(
            type="found_body", tick=40, body_of="p-9", room=room
        )

    def _scene(
        self,
        *,
        placements: tuple[tuple[str, str, int, str], ...],
        alibi_room: str = "STORAGE",
    ) -> MeetingTranscript:
        # turn 0 reports the body (the kill scene); turn 1 is p-3's OWN alibi;
        # each placement is (speaker, sighting_subject, tick, room) naming p-3 as
        # co_present.
        turns = [
            _turn(turn_index=0, speaker="p-1", observations=(self._body(),)),
            _turn(
                turn_index=1,
                speaker="p-3",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room=alibi_room),
                ),
            ),
        ]
        for index, (speaker, subject, tick, room) in enumerate(placements, start=2):
            turns.append(
                _turn(
                    turn_index=index,
                    speaker=speaker,
                    observations=(
                        _saw(
                            tick=tick, subject=subject, room=room, co_present=("p-3",)
                        ),
                    ),
                )
            )
        return MeetingTranscript(turns=tuple(turns))

    def test_two_kill_scene_voices_are_strong(self) -> None:
        # Two independent co-presence placements of p-3 at the REACTOR kill scene
        # contradict p-3's STORAGE alibi: both placements recovered -> two-source
        # conjunction STRONG.
        transcript = self._scene(
            placements=(
                ("p-5", "p-8", 150, "REACTOR"),
                ("p-7", "p-2", 160, "REACTOR"),
            )
        )
        on = [
            f
            for f in detect_contradictions(transcript)
            if f.kind == "alibi_vs_physical"
        ]
        assert len(on) == 2
        for flag in on:
            assert flag.subjects == ("p-3",)
            assert is_weak_contradiction(flag) is False  # STRONG
            assert "kill scene" in flag.description
            assert "REACTOR" in flag.description
            assert "STORAGE" in flag.description

    def test_lone_kill_scene_placement_is_sub_gate(self) -> None:
        # A SINGLE kill-scene placement INFORMS but cannot eject alone: WEAK with
        # the kill-scene marker (read by is_weak_contradiction), the STRICT rule.
        transcript = self._scene(placements=(("p-5", "p-8", 150, "REACTOR"),))
        on = [
            f
            for f in detect_contradictions(transcript)
            if f.kind == "alibi_vs_physical"
        ]
        assert len(on) == 1
        flag = on[0]
        assert is_weak_contradiction(flag) is True
        assert WEAK_REASON_KILL_SCENE in flag.description
        assert flag.subjects == ("p-3",)

    def test_body_placement_two_source_conjunction_is_strong(self) -> None:
        # The second independent source can be a REGULAR (non-kill-scene)
        # placement: one REACTOR kill-scene voice + one EAST_HALL voice = two
        # sources -> STRONG (the "body+placement two-source conjunction").
        transcript = self._scene(
            placements=(
                ("p-5", "p-8", 150, "REACTOR"),  # kill scene
                ("p-7", "p-2", 160, "EAST_HALL"),  # regular physical placement
            )
        )
        on = [
            f
            for f in detect_contradictions(transcript)
            if f.kind == "alibi_vs_physical"
        ]
        assert len(on) == 2
        assert all(is_weak_contradiction(f) is False for f in on)
        # Exactly one of the two STRONG flags names the kill scene.
        assert sum("kill scene" in f.description for f in on) == 1

    def test_accused_admitting_the_scene_is_not_contradicted(self) -> None:
        # If the accused's OWN alibi places them at the body's room (REACTOR), a
        # kill-scene placement there AGREES -> corroboration suppresses, no flag.
        # Presence-at-scene never exonerates, but a self-consistent account is no
        # contradiction.
        transcript = self._scene(
            placements=(
                ("p-5", "p-8", 150, "REACTOR"),
                ("p-7", "p-2", 160, "REACTOR"),
            ),
            alibi_room="REACTOR",
        )
        assert not [
            f
            for f in detect_contradictions(transcript)
            if f.kind == "alibi_vs_physical"
        ]

    def test_without_a_body_the_kill_scene_path_is_inert(self) -> None:
        # The meeting has NO kill scene (no opening found_body): the kill-scene
        # path is inert and the detector emits exactly the regular 13.4 set
        # (the two-voice conjunction still fires STRONG).
        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(
                        _saw(
                            tick=150,
                            subject="p-8",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(
                        _saw(
                            tick=160,
                            subject="p-2",
                            room="EAST_HALL",
                            co_present=("p-3",),
                        ),
                    ),
                ),
            )
        )
        flags = [
            f
            for f in detect_contradictions(transcript)
            if f.kind == "alibi_vs_physical"
        ]
        assert len(flags) == 2
        assert all(is_weak_contradiction(f) is False for f in flags)
        assert all("kill scene" not in f.description for f in flags)


# --- Mixed cases / determinism / surface contract --------------------------


class TestMixedAndDeterministic:
    def _mixed_transcript(self) -> MeetingTranscript:
        return MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-1",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-2",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=150, to_tick=180, room="CAFETERIA"
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    observations=(_saw(tick=160, subject="p-3", room="ADMIN"),),
                ),
            )
        )

    def test_alibi_conflict_and_alibi_vs_sighting_coexist(self) -> None:
        flags = detect_contradictions(self._mixed_transcript())

        kinds = sorted(flag.kind for flag in flags)
        # One alibi_conflict between the two alibis; one alibi_vs_sighting
        # per alibi whose room differs from ADMIN (both differ).
        assert kinds == [
            "alibi_conflict",
            "alibi_vs_sighting",
            "alibi_vs_sighting",
        ]

    def test_result_is_sorted_by_contradiction_id(self) -> None:
        flags = detect_contradictions(self._mixed_transcript())
        ids = [flag.contradiction_id for flag in flags]
        assert ids == sorted(ids)

    def test_pure_function_is_idempotent(self) -> None:
        transcript = self._mixed_transcript()
        first = detect_contradictions(transcript)
        second = detect_contradictions(transcript)
        assert first == second

    def test_canonical_event_pair_ordering(self) -> None:
        # The same logical contradiction produces a canonical
        # (sorted) event-id pair regardless of which claim the detector
        # visits first, so the §6.6 memory view never double-counts.
        flags = detect_contradictions(
            MeetingTranscript(
                turns=(
                    _turn(
                        turn_index=0,
                        speaker="p-1",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=100,
                                to_tick=200,
                                room="STORAGE",
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=1,
                        speaker="p-2",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=150,
                                to_tick=180,
                                room="CAFETERIA",
                            ),
                        ),
                    ),
                )
            )
        )
        assert len(flags) == 1
        assert flags[0].event_a_id <= flags[0].event_b_id
        assert flags[0].contradiction_id == (
            f"contra:alibi_conflict:{flags[0].event_a_id}|{flags[0].event_b_id}"
        )

    def test_flags_are_shared_schema_objects(self) -> None:
        flags = detect_contradictions(
            MeetingTranscript(
                turns=(
                    _turn(
                        turn_index=0,
                        speaker="p-1",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=100,
                                to_tick=200,
                                room="STORAGE",
                            ),
                        ),
                    ),
                    _turn(
                        turn_index=1,
                        speaker="p-2",
                        claims=(
                            _alibi(
                                subject="p-3",
                                from_tick=150,
                                to_tick=180,
                                room="CAFETERIA",
                            ),
                        ),
                    ),
                )
            )
        )

        assert isinstance(flags, tuple)
        for flag in flags:
            assert isinstance(flag, ContradictionRef)
            dumped = flag.model_dump(mode="json")
            assert ContradictionRef.model_validate(dumped) == flag


# --- Cross-speaker alibi_conflict strength (Task 13.3, B2) ------------------


class TestCrossSpeakerConflictStrength:
    """A genuinely-independent cross-speaker ``alibi_conflict`` is STRONG.

    Task 13.3 (DESIGN.md §5.4; report-phase-b-plan B2; grounding-audit P1):
    two DISTINCT non-subject speakers placing the same subject in two rooms
    over overlapping ticks, with NONE of the four weak-guard conditions
    (self-pair / adversarial / narrow / boundary), is a real inferential
    contradiction and carries NO weak marker -- so ``is_weak_contradiction``
    returns ``False`` and a re-extraction stamps ``strong=True``. The four
    weak guards stay byte-identical: each still down-weights its own
    false-positive shape. These tests lock both halves in so a future detector
    edit cannot silently re-mark the independent case weak (Goodharting R7) or
    drop a guard (re-opening the wrong-ejection path the weak delta closed).
    """

    def test_independent_cross_speaker_conflict_is_strong(self) -> None:
        # Two distinct non-subject speakers (p-1, p-2) place subject p-3 in
        # disjoint rooms over a real (non-boundary) overlap; wide windows; no
        # accusation relation. None of the four guards fire -> STRONG.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=120, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        flag = flags[0]
        assert flag.kind == "alibi_conflict"
        assert flag.subjects == ("p-3",)
        assert is_weak_contradiction(flag) is False
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flag.description

    def test_self_pair_conflict_stays_weak(self) -> None:
        # Both conflicting alibis are the subject's OWN statements: the subject's
        # coarse self-recollection disagreeing with itself, not cross-speaker
        # evidence. The self-pair guard keeps it weak.
        turn = _turn(
            turn_index=0,
            speaker="p-3",
            claims=(
                _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                _alibi(subject="p-3", from_tick=120, to_tick=180, room="CAFETERIA"),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=(turn,)))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_SELF_PAIR in flags[0].description

    def test_adversarial_conflict_stays_weak(self) -> None:
        # One speaker (p-1) is across the accusation chain from the subject
        # (p-1 accused p-3), so p-1's alibi about p-3 is a weaponised
        # counter-alibi (the seed-13 m2 impostor deflection). The adversarial
        # guard keeps the conflict weak even though the speakers are distinct.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-3",
                        confidence=0.7,
                        reason="near MedBay before the kill",
                    ),
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=120, to_tick=180, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_ADVERSARIAL in flags[0].description

    def test_narrow_window_conflict_stays_weak(self) -> None:
        # Distinct non-subject speakers, but one alibi spans a sub-
        # NARROW_ALIBI_WINDOW_TICKS window (a single transit observation), so
        # the conflict inherits the tick-boundary fuzz: weak.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=200, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=151, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_NARROW_WINDOW in flags[0].description

    def test_boundary_overlap_conflict_stays_weak(self) -> None:
        # Distinct non-subject speakers whose windows overlap ONLY on the
        # junction tick where one ends and the other begins -- a movement pair
        # ("STORAGE t100-150" then "CAFETERIA t150-200"), not two incompatible
        # accounts: weak.
        turns = (
            _turn(
                turn_index=0,
                speaker="p-1",
                claims=(
                    _alibi(subject="p-3", from_tick=100, to_tick=150, room="STORAGE"),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                claims=(
                    _alibi(subject="p-3", from_tick=150, to_tick=200, room="CAFETERIA"),
                ),
            ),
        )
        flags = detect_contradictions(MeetingTranscript(turns=turns))

        assert len(flags) == 1
        assert flags[0].kind == "alibi_conflict"
        assert is_weak_contradiction(flags[0]) is True
        assert WEAK_REASON_BOUNDARY_OVERLAP in flags[0].description


# --- Task 18.9 lever resolvers (default-OFF, the 16.8 absence-prior shape) ---


class TestWhereaboutsInteriorFlagsResolver:
    """The Task 18.9 lever-1 resolver -- UNCONDITIONAL since the Task-18.12
    baseline-6 record.

    Retired to the always-ON substrate (the 16.17 move, on the CREW-ONLY
    graduation slate): the resolver ignores its ``env`` argument and always
    returns ``True``, so :func:`detect_contradictions` always applies the
    endpoint-band exemption. ``ENV_WHEREABOUTS_INTERIOR_FLAGS`` is retained for
    signature/stamp-key provenance but no longer read.
    """

    def test_is_unconditionally_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert whereabouts_interior_flags_enabled() is True
        assert whereabouts_interior_flags_enabled(env={}) is True
        assert (
            whereabouts_interior_flags_enabled(env={"AILIBI_SOMETHING_ELSE": "1"})
            is True
        )
        monkeypatch.delenv(ENV_WHEREABOUTS_INTERIOR_FLAGS, raising=False)
        assert whereabouts_interior_flags_enabled() is True
        assert whereabouts_interior_flags_enabled(env=None) is True

    @pytest.mark.parametrize("value", ["1", "true", "", "0", "false", "off", "maybe"])
    def test_env_value_is_ignored(self, value: str) -> None:
        # Any value -- truthy, falsy, or junk -- reads ON.
        assert (
            whereabouts_interior_flags_enabled(
                env={ENV_WHEREABOUTS_INTERIOR_FLAGS: value}
            )
            is True
        )

    def test_env_argument_is_not_mutated_and_reads_deterministically(self) -> None:
        env = {ENV_WHEREABOUTS_INTERIOR_FLAGS: "on", "AILIBI_OTHER": "x"}
        before = dict(env)
        assert whereabouts_interior_flags_enabled(env=env) is True
        assert whereabouts_interior_flags_enabled(env=env) is True
        assert env == before


class TestVentPlacementContradictionsResolver:
    """The Task 18.9 lever-2 resolver -- UNCONDITIONAL since the Task-18.12
    baseline-6 record (graduated on the same CREW-ONLY slate)."""

    def test_is_unconditionally_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        assert vent_placement_contradictions_enabled() is True
        assert vent_placement_contradictions_enabled(env={}) is True
        assert (
            vent_placement_contradictions_enabled(env={"AILIBI_SOMETHING_ELSE": "1"})
            is True
        )
        monkeypatch.delenv(ENV_VENT_PLACEMENT_CONTRADICTIONS, raising=False)
        assert vent_placement_contradictions_enabled() is True
        assert vent_placement_contradictions_enabled(env=None) is True

    @pytest.mark.parametrize("value", ["1", "true", "", "0", "false", "off", "maybe"])
    def test_env_value_is_ignored(self, value: str) -> None:
        assert (
            vent_placement_contradictions_enabled(
                env={ENV_VENT_PLACEMENT_CONTRADICTIONS: value}
            )
            is True
        )

    def test_env_argument_is_not_mutated_and_reads_deterministically(self) -> None:
        env = {ENV_VENT_PLACEMENT_CONTRADICTIONS: "on", "AILIBI_OTHER": "x"}
        before = dict(env)
        assert vent_placement_contradictions_enabled(env=env) is True
        assert vent_placement_contradictions_enabled(env=env) is True
        assert env == before

    def test_both_levers_are_unconditional_since_baseline_6(self) -> None:
        # Both graduated at the 18.12 record: neither reads its key any more, so
        # every env cell (including the other lever's key) resolves ON.
        env_w = {ENV_WHEREABOUTS_INTERIOR_FLAGS: "1"}
        env_v = {ENV_VENT_PLACEMENT_CONTRADICTIONS: "1"}
        assert whereabouts_interior_flags_enabled(env=env_w) is True
        assert vent_placement_contradictions_enabled(env=env_w) is True
        assert vent_placement_contradictions_enabled(env=env_v) is True
        assert whereabouts_interior_flags_enabled(env=env_v) is True


# --- Task 18.9 lever 1: the endpoint-band whereabouts exemption -------------

_L1_ON = {ENV_WHEREABOUTS_INTERIOR_FLAGS: "1"}


class TestEndpointBandExemption:
    """Lever 1 ON: a degenerate single-tick self-alibi becomes interior-class.

    Audit-phase-18-planning.md §3.3: a roll-call whereabouts answer indexes as
    ``from_tick == to_tick`` with the speaker its own subject, so a contradicting
    first-hand sighting sits on an endpoint tick and is banded WEAK. ON, the
    single tick is adjudicated as the claim's INTERIOR and the contradicting
    sighting mints a STRONG ``alibi_vs_sighting`` flag. Everything else is
    byte-identical: multi-tick alibis keep the endpoint band, a proxy alibi is
    untouched.
    """

    def _whereabouts_lie(self) -> MeetingTranscript:
        # p-3 answers roll-call "STORAGE at 150"; p-5 first-hand saw p-3 in
        # CAFETERIA at exactly tick 150 -- the degenerate single-tick self-alibi
        # contradicted on its (only) tick.
        return MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    observations=(_whereabouts(tick=150, room="STORAGE"),),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=150, subject="p-3", room="CAFETERIA"),),
                ),
            )
        )

    def test_default_path_mints_a_strong_flag_since_the_exemption_is_unconditional(
        self,
    ) -> None:
        # Since baseline 6 the exemption is UNCONDITIONAL, so the DEFAULT (no-env)
        # path already adjudicates the single tick as the claim's interior: the
        # contradicting sighting mints a STRONG alibi_vs_sighting with no weak
        # marker (pre-graduation this same scenario read narrow + endpoint weak).
        flags = detect_contradictions(self._whereabouts_lie())
        assert len(flags) == 1
        assert flags[0].kind == "alibi_vs_sighting"
        assert is_weak_contradiction(flags[0]) is False
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flags[0].description
        assert WEAK_REASON_NARROW_WINDOW not in flags[0].description
        assert WEAK_REASON_ENDPOINT_TICK not in flags[0].description

    def test_lever_on_mints_a_strong_alibi_vs_sighting(self) -> None:
        tx = self._whereabouts_lie()
        off = detect_contradictions(tx)
        on = detect_contradictions(tx, env=_L1_ON)
        assert len(on) == 1
        flag = on[0]
        assert flag.kind == "alibi_vs_sighting"
        assert flag.subjects == ("p-3",)
        # STRONG: no weak predicate, no weak marker at all in the free text.
        assert is_weak_contradiction(flag) is False
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in flag.description
        assert WEAK_REASON_NARROW_WINDOW not in flag.description
        assert WEAK_REASON_ENDPOINT_TICK not in flag.description
        # Only the BAND (the description) changed -- the flag identity is stable.
        assert flag.contradiction_id == off[0].contradiction_id
        assert (flag.event_a_id, flag.event_b_id) == (
            off[0].event_a_id,
            off[0].event_b_id,
        )

    def test_genuine_single_tick_self_stated_alibi_is_exempted_too(self) -> None:
        # A single-tick self-stated ``AlibiClaim`` is the SAME class by
        # construction (speaker == subject, from == to) -- indistinguishable from
        # a whereabouts answer -- so the exemption covers it identically.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=150, to_tick=150, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=150, subject="p-3", room="CAFETERIA"),),
                ),
            )
        )
        off = detect_contradictions(tx)
        on = detect_contradictions(tx, env=_L1_ON)
        # Lever 1 is UNCONDITIONAL at baseline 6, so the default (off) path already
        # adjudicates the single tick as interior and mints STRONG -- env is ignored.
        assert is_weak_contradiction(off[0]) is False
        assert len(on) == 1
        assert on[0].kind == "alibi_vs_sighting"
        assert is_weak_contradiction(on[0]) is False

    def test_multi_tick_alibi_endpoint_sighting_stays_weak_under_lever_on(
        self,
    ) -> None:
        # The scope guard: a genuine MULTI-tick alibi (from != to) is NOT the
        # degenerate class, so an endpoint-tick sighting keeps the endpoint band
        # even with the lever ON -- multi-tick endpoint semantics are untouched.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=200, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=200, subject="p-3", room="CAFETERIA"),),
                ),
            )
        )
        on = detect_contradictions(tx, env=_L1_ON)
        assert on == detect_contradictions(tx)  # byte-identical to OFF
        assert len(on) == 1
        assert is_weak_contradiction(on[0]) is True
        assert WEAK_REASON_ENDPOINT_TICK in on[0].description

    def test_multi_tick_narrow_alibi_keeps_narrow_window_under_lever_on(self) -> None:
        # A MULTI-tick but narrow alibi (to - from == 1 < 2) is still outside the
        # exemption (from != to), so the narrow-window band survives ON.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=100, to_tick=101, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=100, subject="p-3", room="CAFETERIA"),),
                ),
            )
        )
        on = detect_contradictions(tx, env=_L1_ON)
        assert on == detect_contradictions(tx)
        assert len(on) == 1
        assert is_weak_contradiction(on[0]) is True
        assert WEAK_REASON_NARROW_WINDOW in on[0].description

    def test_proxy_single_tick_alibi_is_untouched_under_lever_on(self) -> None:
        # A PROXY alibi (speaker != subject) can never be the self-alibi class,
        # so the lever leaves it byte-identical -- and still weak.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-4",
                    claims=(
                        _alibi(
                            subject="p-3", from_tick=150, to_tick=150, room="STORAGE"
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=150, subject="p-3", room="CAFETERIA"),),
                ),
            )
        )
        off = detect_contradictions(tx)
        on = detect_contradictions(tx, env=_L1_ON)
        assert on == off
        assert len(on) == 1
        assert is_weak_contradiction(on[0]) is True


# --- Task 18.9 lever 2: the grounded vent-placement flag variant ------------

_L2_ON = {ENV_VENT_PLACEMENT_CONTRADICTIONS: "1"}
_VENT_ROSTER = frozenset({"p-3", "p-5"})


class TestVentPlacementVariant:
    """Lever 2 ON: a grounded vent placement contradicting a self-alibi is STRONG.

    The 17.5 scope firewall's flag-minting arm, reusing the 15.4 grounding
    chokepoint VERBATIM. A spoken :class:`SawVentObservation` grounded against
    the speaker's own :class:`VentWitnessRecord`, whose RECORD places the subject
    in a room disjoint from the subject's OWN stated alibi over an inclusive
    window, mints a STRONG ``alibi_vs_physical`` flag BESIDE the ``vent_sighting``
    flag. Grounded-only is the firewall: an ungrounded spoken vent claim mints
    nothing.
    """

    def _self_alibi_turn(
        self, *, room: str, from_tick: int, to_tick: int
    ) -> MeetingTurn:
        return _turn(
            turn_index=0,
            speaker="p-3",
            claims=(
                _alibi(subject="p-3", from_tick=from_tick, to_tick=to_tick, room=room),
            ),
        )

    def _vent_turn(self, *, tick: int, room: str = "MEDBAY") -> MeetingTurn:
        return _turn(
            turn_index=1,
            speaker="p-5",
            observations=(_saw_vent(tick=tick, subject="p-3", room=room),),
        )

    def test_grounded_disjoint_placement_mints_strong_physical_beside_vent(
        self,
    ) -> None:
        # The record (MEDBAY @ 14) is quoted; the spoken tick (15) differs within
        # tolerance, so the description must show the RECORD's tick, never the
        # spoken one -- the grounded fact, not the testimony.
        tx = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=15),
            )
        )
        records = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=14),)}
        flags = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records, env=_L2_ON
        )
        assert sorted(f.kind for f in flags) == ["alibi_vs_physical", "vent_sighting"]
        physical = next(f for f in flags if f.kind == "alibi_vs_physical")
        assert physical.subjects == ("p-3",)
        assert is_weak_contradiction(physical) is False
        assert WEAK_CONTRADICTION_MARKER_PREFIX not in physical.description
        # Description quotes the RECORD (room MEDBAY, tick 14) + the stated alibi.
        assert "MEDBAY" in physical.description
        assert "at tick 14" in physical.description
        assert "tick 15" not in physical.description
        assert "STORAGE" in physical.description
        # event_a_id is the self-alibi claim; event_b_id the spoken vent obs.
        obs_id = _turn_observation_id(turn=tx.turns[1], index=0)
        assert obs_id in (physical.event_a_id, physical.event_b_id)

    def test_lever_off_with_records_is_byte_identical(self) -> None:
        # Lever 2 is UNCONDITIONAL at baseline 6, so env absent == env={}: both
        # enter the variant block and mint the STRONG ``alibi_vs_physical`` beside
        # the 15.4 ``vent_sighting``. (Pre-graduation the OFF default minted only
        # ``vent_sighting``.)
        tx = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=14),
            )
        )
        records = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=14),)}
        off_no_env = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records
        )
        off_empty = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records, env={}
        )
        assert off_no_env == off_empty
        assert [f.kind for f in off_no_env] == ["alibi_vs_physical", "vent_sighting"]

    def test_inclusive_window_endpoint_record_tick_mints(self) -> None:
        # The recorded-judgment inclusive-window decision: a record tick sitting
        # ON either window endpoint DOES contradict (engine truth, not testimony
        # fuzz). Both endpoints are pinned.
        records = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=20),)}
        tx_to = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=20),
            )
        )
        flags_to = detect_contradictions(
            tx_to, roster=_VENT_ROSTER, vent_witness_records=records, env=_L2_ON
        )
        assert any(f.kind == "alibi_vs_physical" for f in flags_to)

        records_from = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=10),)}
        tx_from = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=10),
            )
        )
        flags_from = detect_contradictions(
            tx_from, roster=_VENT_ROSTER, vent_witness_records=records_from, env=_L2_ON
        )
        assert any(f.kind == "alibi_vs_physical" for f in flags_from)

    def test_a_consistent_grounded_vent_mints_no_physical(self) -> None:
        # The record room is INSIDE the alibi rooms -- the vent grounds (venting
        # is still role-proving, so ``vent_sighting`` fires) but it does NOT
        # contradict the stated path, so no ``alibi_vs_physical``.
        tx = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="MEDBAY", from_tick=10, to_tick=20),
                self._vent_turn(tick=14),
            )
        )
        records = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=14),)}
        flags = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records, env=_L2_ON
        )
        assert [f.kind for f in flags] == ["vent_sighting"]

    def test_a_consistent_record_never_masks_a_contradicting_one(self) -> None:
        # The 16.7 lesson: match-AND-contradict is tested PER record, so a
        # matching-but-consistent record (STORAGE, inside the alibi) appearing
        # BEFORE a matching-and-contradicting one (MEDBAY, disjoint) never
        # short-circuits the flag. The spoken compound room grounds both records.
        tx = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=14, room="STORAGE/MEDBAY"),
            )
        )
        records = {
            "p-5": (
                _vent_record(subject="p-3", room="STORAGE", tick=14),  # consistent
                _vent_record(subject="p-3", room="MEDBAY", tick=14),  # contradicts
            )
        }
        flags = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records, env=_L2_ON
        )
        physical = next(f for f in flags if f.kind == "alibi_vs_physical")
        # The flag quotes the CONTRADICTING record (MEDBAY), not the consistent one.
        assert "MEDBAY" in physical.description

    @pytest.mark.parametrize(
        "record",
        [
            _vent_record(subject="p-9", room="MEDBAY", tick=14),  # wrong subject
            _vent_record(subject="p-3", room="ADMIN", tick=14),  # wrong room
            _vent_record(subject="p-3", room="MEDBAY", tick=40),  # tick beyond tol
        ],
        ids=["mismatched_subject", "mismatched_room", "tick_beyond_tolerance"],
    )
    def test_an_ungrounded_vent_claim_can_never_mint_a_physical(
        self, record: VentWitnessRecord
    ) -> None:
        # The fabrication firewall: without a record that GROUNDS the spoken
        # observation (15.4 chokepoint), the variant mints nothing -- an
        # ungrounded spoken vent claim is testimony, not evidence.
        tx = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=14),
            )
        )
        flags = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records={"p-5": (record,)}, env=_L2_ON
        )
        assert all(f.kind != "alibi_vs_physical" for f in flags)

    def test_no_self_alibi_mints_no_physical(self) -> None:
        # A grounded vent with no self-alibi to contradict: ``vent_sighting``
        # fires, but there is no stated path to contradict.
        tx = MeetingTranscript(turns=(self._vent_turn(tick=14),))
        records = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=14),)}
        flags = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records, env=_L2_ON
        )
        assert [f.kind for f in flags] == ["vent_sighting"]

    def test_non_roster_subject_mints_nothing(self) -> None:
        # The vent subject p-3 is off the roster -- the whole chain is filtered,
        # exactly like the 15.4 flag detector.
        tx = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=14),
            )
        )
        records = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=14),)}
        flags = detect_contradictions(
            tx, roster=frozenset({"p-5"}), vent_witness_records=records, env=_L2_ON
        )
        assert all(f.kind != "alibi_vs_physical" for f in flags)

    def test_variant_detection_is_deterministic(self) -> None:
        tx = MeetingTranscript(
            turns=(
                self._self_alibi_turn(room="STORAGE", from_tick=10, to_tick=20),
                self._vent_turn(tick=14),
            )
        )
        records = {"p-5": (_vent_record(subject="p-3", room="MEDBAY", tick=14),)}
        first = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records, env=_L2_ON
        )
        second = detect_contradictions(
            tx, roster=_VENT_ROSTER, vent_witness_records=records, env=_L2_ON
        )
        assert first == second


class TestBothLeversCompose:
    def test_a_whereabouts_lie_contradicted_by_sighting_and_vent_mints_both(
        self,
    ) -> None:
        # A single-tick whereabouts lie contradicted by BOTH a first-hand
        # sighting (lever 1 -> STRONG alibi_vs_sighting) AND a grounded vent
        # record (lever 2 -> STRONG alibi_vs_physical, beside vent_sighting).
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    observations=(_whereabouts(tick=14, room="STORAGE"),),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-5",
                    observations=(_saw(tick=14, subject="p-3", room="CAFETERIA"),),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-7",
                    observations=(_saw_vent(tick=14, subject="p-3", room="MEDBAY"),),
                ),
            )
        )
        records = {"p-7": (_vent_record(subject="p-3", room="MEDBAY", tick=14),)}
        env = {
            ENV_WHEREABOUTS_INTERIOR_FLAGS: "1",
            ENV_VENT_PLACEMENT_CONTRADICTIONS: "1",
        }
        flags = detect_contradictions(
            tx,
            roster=frozenset({"p-3", "p-5", "p-7"}),
            vent_witness_records=records,
            env=env,
        )
        by_kind = {f.kind: f for f in flags}
        assert set(by_kind) == {
            "alibi_vs_sighting",
            "alibi_vs_physical",
            "vent_sighting",
        }
        # Both lever-minted flags are STRONG.
        assert is_weak_contradiction(by_kind["alibi_vs_sighting"]) is False
        assert is_weak_contradiction(by_kind["alibi_vs_physical"]) is False


# --- The movement-claim lever (default-OFF) --------------------------------
#
# A witness who saw "p-3 move from MEDBAY to LABS at tick 3" holds two facts and
# may speak only one room. Speaking the ORIGIN states a placement that was
# already false, and the detector then prosecutes the subject's truthful answer
# for disagreeing with it. The lever re-reads such a placement at the
# DESTINATION, grounded on the speaker's own record, and lets a turn state the
# transition outright.

_ROSTER_3 = frozenset({"p-3", "p-5", "p-9"})


class TestMovementClaimShapeResolver:
    def test_defaults_off_with_no_environment(self) -> None:
        assert movement_claim_shape_enabled({}) is False

    def test_reads_the_documented_true_values(self) -> None:
        for value in ("1", "true", "TRUE", "yes", "on", " On "):
            assert movement_claim_shape_enabled({ENV_MOVEMENT_CLAIM_SHAPE: value})

    def test_any_other_value_is_off(self) -> None:
        for value in ("", "0", "false", "no", "off", "maybe"):
            assert (
                movement_claim_shape_enabled({ENV_MOVEMENT_CLAIM_SHAPE: value}) is False
            )


def _origin_spoken_transcript(
    *,
    witness: str = "p-9",
    subject: str = "p-3",
    origin: str = "MEDBAY",
    destination: str = "LABS",
    tick: int = 3,
    answer_room: str | None = None,
    answer_tick: int | None = None,
) -> MeetingTranscript:
    """The G-9 shape: the witness speaks the origin, the subject answers truthfully.

    Turn 0 is the witness's origin-half sighting; turn 1 is the subject's
    roll-call answer, by default the destination room at the same tick (the
    truthful reading of the transition the witness holds).
    """

    return MeetingTranscript(
        turns=(
            _turn(
                turn_index=0,
                speaker=witness,
                observations=(_saw(tick=tick, subject=subject, room=origin),),
            ),
            _turn(
                turn_index=1,
                speaker=subject,
                turn_kind="opt_in",
                observations=(
                    _whereabouts(
                        tick=tick if answer_tick is None else answer_tick,
                        room=destination if answer_room is None else answer_room,
                    ),
                ),
            ),
        )
    )


class TestMovementResolutionArm:
    """ON, a spoken placement the SPEAKER's own record moved the subject out of
    is read at the destination -- so the manufactured contradiction never mints."""

    def test_seed_12_shape_mints_off_and_dissolves_on(self) -> None:
        # samples/9p2i seed 12 meeting-0, recomputed from the committed bytes:
        # p-9 holds MEDBAY->LABS at tick 3 about p-3, speaks MEDBAY at tick 3,
        # p-3 answers LABS at tick 3 -- and the table ejected p-3 (a crewmate)
        # 6-0-1 on the flag below.
        tx = _origin_spoken_transcript()
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        off = detect_contradictions(tx, roster=_ROSTER_3)
        assert [f.kind for f in off] == ["alibi_vs_sighting"]
        assert is_weak_contradiction(off[0]) is False
        assert off[0].subjects == ("p-3",)
        on = detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        )
        assert on == ()

    def test_seed_39_shape_mints_off_and_dissolves_on(self) -> None:
        # samples/9p2i seed 39 meeting-0: the witness holds EAST_HALL->CAFETERIA
        # at tick 8 about p-1, speaks EAST_HALL, p-1 answers CAFETERIA -- the
        # meeting's ONLY flag, and it ejected p-1 (a crewmate) 7-1.
        tx = _origin_spoken_transcript(
            origin="EAST_HALL", destination="CAFETERIA", tick=8
        )
        records = {
            "p-9": (
                _move_record(
                    tick=8, subject="p-3", from_room="EAST_HALL", to_room="CAFETERIA"
                ),
            )
        }
        assert len(detect_contradictions(tx, roster=_ROSTER_3)) == 1
        assert (
            detect_contradictions(
                tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
            )
            == ()
        )

    def test_a_spoken_destination_is_untouched(self) -> None:
        # The 86 flags the review found speaking the destination are already the
        # placement the witness meant: ON must leave them exactly as spoken.
        tx = _origin_spoken_transcript(origin="LABS", answer_room="MEDBAY")
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        off = detect_contradictions(tx, roster=_ROSTER_3)
        on = detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        )
        assert on == off
        assert "LABS" in on[0].description

    def test_the_origin_at_the_previous_tick_is_untouched(self) -> None:
        # "p-3 was in MEDBAY at tick 2" is TRUE under the agent clock -- the
        # transition resolved at tick 3 -- so the exact-tick conjunction must
        # leave it alone rather than re-time it to the destination.
        tx = _origin_spoken_transcript(tick=2, answer_tick=2, answer_room="ADMIN")
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        off = detect_contradictions(tx, roster=_ROSTER_3)
        on = detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        )
        assert on == off
        assert "MEDBAY" in on[0].description

    def test_an_ungrounded_sighting_is_never_rewritten(self) -> None:
        # The firewall: the record belongs to ANOTHER speaker, so this witness
        # grounds nothing and their testimony reads exactly as spoken.
        tx = _origin_spoken_transcript()
        records = {
            "p-5": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        off = detect_contradictions(tx, roster=_ROSTER_3)
        on = detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        )
        assert on == off
        assert on != ()

    def test_two_destinations_at_one_tick_leave_the_placement_alone(self) -> None:
        # Engine truth forbids it; picking a side would invent testimony.
        tx = _origin_spoken_transcript()
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
                _move_record(
                    tick=3, subject="p-3", from_room="MEDBAY", to_room="ADMIN"
                ),
            )
        }
        assert detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        ) == detect_contradictions(tx, roster=_ROSTER_3)

    def test_a_conflicting_record_blocks_the_rewrite_from_any_room(self) -> None:
        # The ambiguity guard is adjudicated over every record naming the subject
        # at that tick, not only the ones whose origin matches the spoken room:
        # a channel that has the subject landing twice on one tick is wrong about
        # something, so nothing in it may pick a destination.
        tx = _origin_spoken_transcript()
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
                _move_record(
                    tick=3, subject="p-3", from_room="ADMIN", to_room="REACTOR"
                ),
            )
        }
        assert detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        ) == detect_contradictions(tx, roster=_ROSTER_3)
        # Two records that AGREE on the destination are not ambiguous, so the
        # guard does not swallow the ordinary case.
        agreeing = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        assert (
            detect_contradictions(
                tx, roster=_ROSTER_3, move_witness_records=agreeing, env=_MOVEMENT_ON
            )
            == ()
        )
        # A conflict at a DIFFERENT tick is a different transition and is none of
        # this placement's business.
        other_tick = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
                _move_record(
                    tick=4, subject="p-3", from_room="ADMIN", to_room="REACTOR"
                ),
            )
        }
        assert (
            detect_contradictions(
                tx, roster=_ROSTER_3, move_witness_records=other_tick, env=_MOVEMENT_ON
            )
            == ()
        )

    def test_a_genuine_conflict_still_mints_at_the_destination(self) -> None:
        # The perturbation that shows the rule bites: the subject claims a THIRD
        # room, so the resolved destination still contradicts them -- STRONG, and
        # the flag now quotes the room the witness actually saw them enter.
        tx = _origin_spoken_transcript(answer_room="ADMIN")
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        off = detect_contradictions(tx, roster=_ROSTER_3)
        on = detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        )
        assert [f.kind for f in on] == ["alibi_vs_sighting"]
        assert is_weak_contradiction(on[0]) is False
        assert "LABS" in on[0].description and "MEDBAY" not in on[0].description
        # Id invariance: only the ROOM is re-read. Every id-keyed surface
        # downstream -- the citation, the lift key, the spectator view -- sees the
        # same flag it saw before.
        assert on[0].contradiction_id == off[0].contradiction_id
        assert (on[0].event_a_id, on[0].event_b_id) == (
            off[0].event_a_id,
            off[0].event_b_id,
        )
        assert on[0].subjects == off[0].subjects

    def test_the_resolution_touches_no_id_keyed_surface(self) -> None:
        # "Only the room is re-read" is what leaves every id-keyed surface
        # untouched, so it is asserted rather than assumed: the flag's two ids
        # still resolve to their speakers, the public path reconstruction still
        # reads the room the witness SPOKE (the re-read lives inside the pairing
        # step, not in the transcript), and the absent set does not move.
        tx = _origin_spoken_transcript(answer_room="ADMIN")
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        on = detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        )
        speakers = _event_speaker_index(tx)
        assert speakers[on[0].event_a_id] == "p-9"
        assert speakers[on[0].event_b_id] == "p-3"
        placements = reconstruct_stated_paths(tx, roster=_ROSTER_3)
        assert [
            (placement.tick, sorted(placement.rooms), placement.speaker)
            for placement in placements["p-3"]
        ] == [(3, ["ADMIN"], "p-3"), (3, ["MEDBAY"], "p-9")]
        # p-9 spoke, but placed only p-3: answering nothing about yourself
        # leaves you absent, and the re-read does not change that either.
        assert absent_players(tx, roster=_ROSTER_3) == ("p-5", "p-9")

    def test_records_are_inert_while_the_lever_is_off(self) -> None:
        # The whole OFF-path guarantee in one assertion: a live channel changes
        # nothing until the lever is on.
        tx = _origin_spoken_transcript()
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        assert detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records
        ) == detect_contradictions(tx, roster=_ROSTER_3)


class TestMovementShapeArm:
    """ON, a grounded spoken transition participates as ONE destination placement."""

    def _transcript(self, *, answer_room: str, answer_tick: int) -> MeetingTranscript:
        return MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-9",
                    observations=(
                        _saw_move(
                            tick=3,
                            subject="p-3",
                            from_room="MEDBAY",
                            to_room="LABS",
                        ),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-3",
                    turn_kind="opt_in",
                    observations=(_whereabouts(tick=answer_tick, room=answer_room),),
                ),
            )
        )

    def test_a_grounded_transition_places_the_subject_at_the_destination(self) -> None:
        tx = self._transcript(answer_room="ADMIN", answer_tick=3)
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        flags = detect_contradictions(
            tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
        )
        assert [f.kind for f in flags] == ["alibi_vs_sighting"]
        assert flags[0].subjects == ("p-3",)
        assert "LABS" in flags[0].description

    def test_the_origin_half_places_nobody(self) -> None:
        # Deliberate: the shape asserts ONE placement. A claim about the ORIGIN
        # tick raises no flag, because inferring "in MEDBAY at tick 2" from a
        # spoken tick would re-open the off-by-one class this shape closes.
        tx = self._transcript(answer_room="ADMIN", answer_tick=2)
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        assert (
            detect_contradictions(
                tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
            )
            == ()
        )

    def test_an_ungrounded_transition_places_nobody(self) -> None:
        tx = self._transcript(answer_room="ADMIN", answer_tick=3)
        records = {
            "p-9": (
                _move_record(
                    tick=3, subject="p-3", from_room="REACTOR", to_room="STORAGE"
                ),
            )
        }
        assert (
            detect_contradictions(
                tx, roster=_ROSTER_3, move_witness_records=records, env=_MOVEMENT_ON
            )
            == ()
        )

    def test_the_off_detector_ignores_the_shape_entirely(self) -> None:
        tx = self._transcript(answer_room="ADMIN", answer_tick=3)
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        assert (
            detect_contradictions(tx, roster=_ROSTER_3, move_witness_records=records)
            == ()
        )

    def test_the_roster_gate_bites_on_the_placement(self) -> None:
        tx = self._transcript(answer_room="ADMIN", answer_tick=3)
        records = {
            "p-9": (
                _move_record(tick=3, subject="p-3", from_room="MEDBAY", to_room="LABS"),
            )
        }
        assert (
            len(
                detect_contradictions(
                    tx,
                    roster=_ROSTER_3,
                    move_witness_records=records,
                    env=_MOVEMENT_ON,
                )
            )
            == 1
        )
        assert (
            detect_contradictions(
                tx,
                roster=frozenset({"p-5", "p-9"}),
                move_witness_records=records,
                env=_MOVEMENT_ON,
            )
            == ()
        )


# --- Task 20.26: grounded prosecution --------------------------------------
#
# Three rules on ONE kind, behind one predicate (the resolver is ON and the
# caller supplied records): an ungrounded sighting side cannot convict, a lone
# grounded speaker cannot convict without a physical anchor, and the degenerate
# single-tick self-placement loses the 18.9 interior exemption.

_GROUNDED_ON = {ENV_GROUNDED_PROSECUTION: "1"}
_ROSTER_4 = frozenset({"p-3", "p-5", "p-7", "p-9"})


def _sighting_record(
    *, tick: int, subject: str, room: str, co_present: tuple[str, ...] = ()
) -> SightingRecord:
    return SightingRecord(subject=subject, room=room, tick=tick, co_present=co_present)


def _prosecution_transcript(
    *,
    alibi_from: int = 4,
    alibi_to: int = 8,
    sighting_tick: int = 6,
    second_witness: bool = True,
) -> MeetingTranscript:
    """p-3's own alibi, contradicted by one or two first-hand sightings.

    A multi-tick window with the sighting strictly inside it, so no pre-lever
    weak reason applies: OFF, every flag below is STRONG.
    """

    turns = [
        _turn(
            turn_index=0,
            speaker="p-3",
            claims=(
                _alibi(
                    subject="p-3",
                    from_tick=alibi_from,
                    to_tick=alibi_to,
                    room="MEDBAY",
                ),
            ),
        ),
        _turn(
            turn_index=1,
            speaker="p-9",
            turn_kind="reply",
            observations=(_saw(tick=sighting_tick, subject="p-3", room="LABS"),),
        ),
    ]
    if second_witness:
        turns.append(
            _turn(
                turn_index=2,
                speaker="p-5",
                turn_kind="opt_in",
                observations=(_saw(tick=sighting_tick, subject="p-3", room="LABS"),),
            )
        )
    return MeetingTranscript(turns=tuple(turns))


def _grounding_records(
    *speakers: str, tick: int = 6, room: str = "LABS"
) -> dict[str, tuple[SightingRecord, ...]]:
    """One matching record per named speaker, for the transcript above."""

    return {
        speaker: (_sighting_record(tick=tick, subject="p-3", room=room),)
        for speaker in speakers
    }


class TestGroundedProsecutionResolver:
    def test_defaults_off_with_no_environment(self) -> None:
        assert grounded_prosecution_enabled({}) is False

    def test_reads_the_documented_true_values(self) -> None:
        for value in ("1", "true", "TRUE", "yes", "on", " On "):
            assert grounded_prosecution_enabled({ENV_GROUNDED_PROSECUTION: value})

    def test_any_other_value_is_off(self) -> None:
        for value in ("", "0", "false", "no", "off", "maybe"):
            assert (
                grounded_prosecution_enabled({ENV_GROUNDED_PROSECUTION: value}) is False
            )

    def test_the_lever_is_inert_without_a_records_mapping(self) -> None:
        # The second half of the predicate: a caller with no records keeps the
        # pre-lever rules, which is what makes the record-free re-derivers safe.
        tx = _prosecution_transcript()
        baseline = detect_contradictions(tx, roster=_ROSTER_4)
        assert [is_weak_contradiction(f) for f in baseline] == [False, False]
        assert detect_contradictions(tx, roster=_ROSTER_4, env=_GROUNDED_ON) == baseline
        assert (
            detect_contradictions(
                tx, roster=_ROSTER_4, sighting_records={}, env=_GROUNDED_ON
            )
            == baseline
        )

    def test_records_without_the_lever_change_nothing(self) -> None:
        tx = _prosecution_transcript()
        baseline = detect_contradictions(tx, roster=_ROSTER_4)
        assert (
            detect_contradictions(
                tx, roster=_ROSTER_4, sighting_records=_grounding_records("p-9")
            )
            == baseline
        )


class TestGroundedProsecutionRuleGrounding:
    """Rule (a): speech the speaker's own record does not support cannot convict."""

    def test_an_ungrounded_speaker_mints_a_weak_flag_not_a_strong_one(self) -> None:
        tx = _prosecution_transcript()
        # p-9 holds a matching record; p-5 holds one for the wrong room.
        records = {
            **_grounding_records("p-9"),
            "p-5": (_sighting_record(tick=6, subject="p-3", room="STORAGE"),),
        }
        flags = detect_contradictions(
            tx, roster=_ROSTER_4, sighting_records=records, env=_GROUNDED_ON
        )
        by_speaker = {_event_speaker_index(tx)[flag.event_b_id]: flag for flag in flags}
        assert set(by_speaker) == {"p-9", "p-5"}
        assert WEAK_REASON_UNGROUNDED_SIGHTING in by_speaker["p-5"].description
        assert is_weak_contradiction(by_speaker["p-5"]) is True
        # p-9 IS grounded, so its flag carries the lone-source reason instead --
        # never the ungrounded one.
        assert WEAK_REASON_UNGROUNDED_SIGHTING not in by_speaker["p-9"].description
        assert WEAK_REASON_LONE_GROUNDED_SOURCE in by_speaker["p-9"].description

    def test_giving_that_speaker_a_record_restores_strong(self) -> None:
        # The perturbation, on the IDENTICAL transcript: the only thing that
        # changes is whether p-5's own memory holds what p-5 said.
        tx = _prosecution_transcript()
        ungrounded = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9"),
            env=_GROUNDED_ON,
        )
        grounded = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9", "p-5"),
            env=_GROUNDED_ON,
        )
        assert [is_weak_contradiction(f) for f in ungrounded] == [True, True]
        assert [is_weak_contradiction(f) for f in grounded] == [False, False]
        # Only the description moved.
        assert [f.contradiction_id for f in ungrounded] == [
            f.contradiction_id for f in grounded
        ]
        assert [f.subjects for f in ungrounded] == [f.subjects for f in grounded]

    def test_a_record_outside_the_tick_window_does_not_ground(self) -> None:
        tx = _prosecution_transcript(second_witness=False)
        flags = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records={
                "p-9": (_sighting_record(tick=6 + 3, subject="p-3", room="LABS"),)
            },
            env=_GROUNDED_ON,
        )
        assert WEAK_REASON_UNGROUNDED_SIGHTING in flags[0].description

    def test_a_movement_derived_placement_reads_grounded(self) -> None:
        # p-9 speaks a TRANSITION its own MoveWitnessRecord confirms and holds no
        # SightingRecord at all -- the two episodic channels are disjoint. With
        # both levers ON the placement is a grounded source, so p-5's grounded
        # sighting is no longer alone and BOTH flags band STRONG.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(subject="p-3", from_tick=4, to_tick=8, room="MEDBAY"),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-9",
                    turn_kind="reply",
                    observations=(
                        _saw_move(
                            tick=6,
                            subject="p-3",
                            from_room="STORAGE",
                            to_room="LABS",
                        ),
                    ),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    turn_kind="opt_in",
                    observations=(_saw(tick=6, subject="p-3", room="LABS"),),
                ),
            )
        )
        moves = {
            "p-9": (
                _move_record(
                    tick=6, subject="p-3", from_room="STORAGE", to_room="LABS"
                ),
            )
        }
        both_on = {**_MOVEMENT_ON, **_GROUNDED_ON}
        flags = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            move_witness_records=moves,
            sighting_records=_grounding_records("p-5"),
            env=both_on,
        )
        assert len(flags) == 2
        assert [is_weak_contradiction(f) for f in flags] == [False, False]
        # The perturbation: drop p-9's movement record. The transition grounds
        # nothing, places nobody, and p-5 is left the lone source.
        alone = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            move_witness_records={},
            sighting_records=_grounding_records("p-5"),
            env=both_on,
        )
        assert len(alone) == 1
        assert WEAK_REASON_LONE_GROUNDED_SOURCE in alone[0].description


class TestGroundedProsecutionRuleTwoSources:
    """Rule (b): one grounded speaker is not a prosecution."""

    def test_two_distinct_grounded_speakers_band_strong(self) -> None:
        tx = _prosecution_transcript()
        flags = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9", "p-5"),
            env=_GROUNDED_ON,
        )
        assert len(flags) == GROUNDED_PROSECUTION_MIN_SOURCES
        assert [is_weak_contradiction(f) for f in flags] == [False, False]

    def test_one_grounded_speaker_alone_bands_weak(self) -> None:
        tx = _prosecution_transcript(second_witness=False)
        (flag,) = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9"),
            env=_GROUNDED_ON,
        )
        assert is_weak_contradiction(flag) is True
        assert WEAK_REASON_LONE_GROUNDED_SOURCE in flag.description

    def test_one_speaker_grounding_twice_is_still_one_source(self) -> None:
        # The double-count guard, in both of its shapes: two records behind one
        # sighting, and two sightings in ONE turn. Neither is a second witness.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(subject="p-3", from_tick=4, to_tick=8, room="MEDBAY"),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-9",
                    turn_kind="reply",
                    observations=(
                        _saw(tick=6, subject="p-3", room="LABS"),
                        _saw(tick=7, subject="p-3", room="LABS"),
                    ),
                ),
            )
        )
        records = {
            "p-9": (
                _sighting_record(tick=6, subject="p-3", room="LABS"),
                _sighting_record(tick=7, subject="p-3", room="LABS"),
            )
        }
        flags = detect_contradictions(
            tx, roster=_ROSTER_4, sighting_records=records, env=_GROUNDED_ON
        )
        assert len(flags) == 2
        assert [is_weak_contradiction(f) for f in flags] == [True, True]
        for flag in flags:
            assert WEAK_REASON_LONE_GROUNDED_SOURCE in flag.description
        # OFF, both of them convict -- which is the conviction this rule removes.
        off = detect_contradictions(tx, roster=_ROSTER_4)
        assert [is_weak_contradiction(f) for f in off] == [False, False]

    def test_a_weak_banded_speaker_is_still_a_source(self) -> None:
        # An endpoint-tick sighting is transit fuzz as its OWN flag, but it is
        # still a second honest account of the same claim (the 10.1 "an endpoint
        # mismatch can still be a real signal once corroborated" band). Counting
        # sources only over already-STRONG flags would demote the interior
        # witness as if they stood alone.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(subject="p-3", from_tick=4, to_tick=8, room="MEDBAY"),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-9",
                    turn_kind="reply",
                    observations=(_saw(tick=6, subject="p-3", room="LABS"),),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    turn_kind="opt_in",
                    # Tick 4 is the window's EDGE: weak before this lever ever runs.
                    observations=(_saw(tick=4, subject="p-3", room="LABS"),),
                ),
            )
        )
        records = {
            "p-9": (_sighting_record(tick=6, subject="p-3", room="LABS"),),
            "p-5": (_sighting_record(tick=4, subject="p-3", room="LABS"),),
        }
        flags = detect_contradictions(
            tx, roster=_ROSTER_4, sighting_records=records, env=_GROUNDED_ON
        )
        by_tick = {
            "interior" if "tick 6" in flag.description else "endpoint": flag
            for flag in flags
        }
        assert set(by_tick) == {"interior", "endpoint"}
        # The interior witness convicts: two distinct grounded speakers.
        assert is_weak_contradiction(by_tick["interior"]) is False
        # The endpoint witness keeps its OWN band and gains no new reason.
        assert WEAK_REASON_ENDPOINT_TICK in by_tick["endpoint"].description
        assert WEAK_REASON_LONE_GROUNDED_SOURCE not in by_tick["endpoint"].description
        # The perturbation: drop the endpoint speaker's record. They stop being a
        # source, and the interior witness is alone again.
        alone = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9"),
            env=_GROUNDED_ON,
        )
        interior = next(f for f in alone if "tick 6" in f.description)
        assert WEAK_REASON_LONE_GROUNDED_SOURCE in interior.description

    def test_a_vent_anchor_carries_a_lone_grounded_source(self) -> None:
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(subject="p-3", from_tick=4, to_tick=8, room="MEDBAY"),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-9",
                    turn_kind="reply",
                    observations=(
                        _saw(tick=6, subject="p-3", room="LABS"),
                        # The vent sits INSIDE p-3's own claimed room, so the
                        # 18.9 vent-placement variant mints nothing and this
                        # fixture isolates the vent_sighting anchor.
                        _saw_vent(tick=6, subject="p-3", room="MEDBAY"),
                    ),
                ),
            )
        )
        vents = {"p-9": (_vent_record(tick=6, subject="p-3", room="MEDBAY"),)}
        flags = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            vent_witness_records=vents,
            sighting_records=_grounding_records("p-9"),
            env=_GROUNDED_ON,
        )
        kinds = {flag.kind: flag for flag in flags}
        assert set(kinds) == {"alibi_vs_sighting", "vent_sighting"}
        assert is_weak_contradiction(kinds["alibi_vs_sighting"]) is False
        # The perturbation: without the vent channel there is no anchor, and the
        # same lone grounded speaker no longer convicts.
        unanchored = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9"),
            env=_GROUNDED_ON,
        )
        assert [f.kind for f in unanchored] == ["alibi_vs_sighting"]
        assert WEAK_REASON_LONE_GROUNDED_SOURCE in unanchored[0].description

    def test_a_physical_anchor_carries_a_lone_grounded_source(self) -> None:
        # p-5's CO-PRESENCE places p-3 in LABS inside p-3's own window: an
        # alibi_vs_physical flag on p-3, the second grounded-by-construction
        # channel. p-9 stays the only sighting speaker.
        tx = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    claims=(
                        _alibi(subject="p-3", from_tick=4, to_tick=8, room="MEDBAY"),
                    ),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-9",
                    turn_kind="reply",
                    observations=(_saw(tick=6, subject="p-3", room="LABS"),),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    turn_kind="opt_in",
                    observations=(
                        _saw(tick=6, subject="p-7", room="LABS", co_present=("p-3",)),
                    ),
                ),
            )
        )
        flags = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9"),
            env=_GROUNDED_ON,
        )
        kinds = {flag.kind: flag for flag in flags}
        assert set(kinds) == {"alibi_vs_sighting", "alibi_vs_physical"}
        assert is_weak_contradiction(kinds["alibi_vs_sighting"]) is False


class TestGroundedProsecutionRuleSingleTickEndpoint:
    """Rule (c): a one-tick self-placement is an edge again, not its own interior."""

    def _roll_call(self, *, tick: int) -> MeetingTranscript:
        return MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-3",
                    turn_kind="opt_in",
                    observations=(_whereabouts(tick=tick, room="MEDBAY"),),
                ),
                _turn(
                    turn_index=1,
                    speaker="p-9",
                    turn_kind="reply",
                    observations=(_saw(tick=tick, subject="p-3", room="LABS"),),
                ),
                _turn(
                    turn_index=2,
                    speaker="p-5",
                    turn_kind="opt_in",
                    observations=(_saw(tick=tick, subject="p-3", room="LABS"),),
                ),
            )
        )

    def test_the_roll_call_answer_bands_weak_under_the_lever(self) -> None:
        tx = self._roll_call(tick=6)
        # OFF: the 18.9 exemption adjudicates the single tick as the interior.
        off = detect_contradictions(tx, roster=_ROSTER_4)
        assert [is_weak_contradiction(f) for f in off] == [False, False]
        # ON: the pre-18.9 band returns -- with its own literals, unchanged.
        on = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9", "p-5"),
            env=_GROUNDED_ON,
        )
        assert [is_weak_contradiction(f) for f in on] == [True, True]
        for flag in on:
            assert (
                f"{WEAK_CONTRADICTION_MARKER_PREFIX}"
                f"{WEAK_REASON_NARROW_WINDOW}; {WEAK_REASON_ENDPOINT_TICK}]"
            ) in flag.description
            # The band is rule (c)'s, not rule (b)'s: two grounded speakers.
            assert WEAK_REASON_LONE_GROUNDED_SOURCE not in flag.description

    def test_widening_the_claim_restores_strong(self) -> None:
        # The perturbation: the same two grounded witnesses, the same contradicted
        # room, but a multi-tick window with the sighting strictly inside it.
        tx = _prosecution_transcript()
        on = detect_contradictions(
            tx,
            roster=_ROSTER_4,
            sighting_records=_grounding_records("p-9", "p-5"),
            env=_GROUNDED_ON,
        )
        assert [is_weak_contradiction(f) for f in on] == [False, False]


# --- The live detector re-derives the committed bytes -----------------------
#
# The graduated detector (levers 1 and 2 unconditional since the Task-18.12
# baseline-6 record) re-derives every recorded flag byte-identically over ALL
# FOUR committed sets -- 707 meetings. ml_corpus was re-grounded on baseline 6
# by Task 18.13 (both MANIFESTs carry the same lever slate), so the walk is no
# longer samples-only.

_REPO_ROOT = Path(__file__).resolve().parents[2]
_COMMITTED_SETS = (
    _REPO_ROOT / "replays" / "samples" / "9p2i",
    _REPO_ROOT / "replays" / "samples" / "4p1i",
    _REPO_ROOT / "replays" / "ml_corpus" / "9p2i",
    _REPO_ROOT / "replays" / "ml_corpus" / "4p1i",
)
_COMMITTED_MEETINGS = 707


@functools.cache
def _committed_meeting_entries() -> tuple[tuple[str, int, MeetingReplayEntry], ...]:
    """Every committed meeting entry across all four sets (set, seed, entry).

    Cached so the byte-identity pin AND the live-detector census below read the
    707-meeting corpus off ONE walk (the "do not walk twice" rule): the file read
    happens once per session, and each consumer runs its own detector
    re-derivations over the shared, already-parsed entries.
    """

    collected: list[tuple[str, int, MeetingReplayEntry]] = []
    for set_dir in _COMMITTED_SETS:
        set_name = f"{set_dir.parent.name}/{set_dir.name}"
        for path in sorted(set_dir.glob("replay-seed-*.jsonl")):
            seed = int(path.stem.rsplit("-", 1)[1])
            for entry in read_all_entries(path):
                if isinstance(entry, MeetingReplayEntry):
                    collected.append((set_name, seed, entry))
    return tuple(collected)


def _living_roster(entry: MeetingReplayEntry) -> frozenset[str]:
    # Every recorded ballot was cast by a living participant, so the ballot
    # voters ARE the roster the recording-time detector received.
    return frozenset(ballot.voter for ballot in entry.ballots)


def _vent_records_from_recorded_flags(
    entry: MeetingReplayEntry,
) -> dict[str, tuple[VentWitnessRecord, ...]]:
    """Rebuild each speaker's groundable vent channel from the RECORDED flags.

    The replay persists no private :class:`VentWitnessRecord`s, but a recorded
    ``vent_sighting`` flag IS the record-time grounding verdict: its
    ``event_a_id`` names the spoken :class:`SawVentObservation` that matched the
    speaker's own channel. Minting a record from that observation's TYPED fields
    (grounding at record time guarantees the label is spatial and the tick
    in-window, so the rebuilt record re-grounds the same observation by
    construction) lets the OFF-path pin re-derive the vent flags too -- ids and
    typed fields only, never a text parse (clone of
    :meth:`tests.agents.test_absence_prior` `_vent_records_from_recorded_flags`).
    """

    flagged = {
        flag.event_a_id for flag in entry.contradictions if flag.kind == "vent_sighting"
    }
    records: dict[str, list[VentWitnessRecord]] = {}
    for turn in entry.transcript.turns:
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawVentObservation):
                continue
            if _turn_observation_id(turn=turn, index=index) not in flagged:
                continue
            records.setdefault(turn.speaker, []).append(
                VentWitnessRecord(
                    subject=observation.subject,
                    room=observation.room,
                    tick=observation.tick,
                )
            )
    return {speaker: tuple(rows) for speaker, rows in records.items()}


# The vent-record TICK is provably unrecoverable from replay bytes: the flag
# description embeds ``VentWitnessRecord.tick`` (the real observed vent tick),
# which the replay does not persist, while the rebuild above uses the SPOKEN
# observation's tick. Grounding still fires (they agree within
# VENT_GROUNDING_TICK_TOLERANCE), so every STRUCTURAL field re-derives
# byte-identically; only that one description tick can differ -- ml_corpus/9p2i
# seed 1075 is the one known case, and it is inside this walk. The comparison
# therefore pins full equality for every non-vent kind and structural equality
# (all fields but ``description``) for ``vent_sighting``.
_VENT_STRUCT = ("contradiction_id", "kind", "event_a_id", "event_b_id", "subjects")


def _flags_match(
    rederived: tuple[ContradictionRef, ...],
    recorded: tuple[ContradictionRef, ...],
) -> bool:
    if len(rederived) != len(recorded):
        return False
    for got, exp in zip(rederived, recorded, strict=True):
        if exp.kind == "vent_sighting":
            if any(getattr(got, name) != getattr(exp, name) for name in _VENT_STRUCT):
                return False
        elif got != exp:
            return False
    return True


def _planted_move_channel(
    entry: MeetingReplayEntry,
) -> dict[str, tuple[MoveWitnessRecord, ...]]:
    """A movement channel that WOULD re-read every spoken placement, if read.

    Each speaker gets one record per sighting they spoke, moving that subject out
    of the room they named at the tick they named into a room they did not: the
    exact conjunction :func:`_movement_destination` resolves on. It is the
    planted case behind the OFF pin -- with the lever OFF this channel must move
    nothing, and the companion test proves the plant is live by turning the lever
    on and watching the corpus change.
    """

    records: dict[str, list[MoveWitnessRecord]] = {}
    for turn in entry.transcript.turns:
        for observation in turn.observations:
            if not isinstance(observation, SawPlayerObservation):
                continue
            spoken = canonical_rooms(observation.room)
            if not spoken:
                continue
            elsewhere = sorted(CANONICAL_ROOMS - spoken)[0]
            records.setdefault(turn.speaker, []).append(
                MoveWitnessRecord(
                    subject=observation.subject,
                    from_room=observation.room,
                    to_room=elsewhere,
                    tick=observation.tick,
                )
            )
    return {speaker: tuple(rows) for speaker, rows in records.items()}


def _planted_sighting_channel(
    entry: MeetingReplayEntry,
) -> dict[str, tuple[SightingRecord, ...]]:
    """A channel that grounds EVERY spoken sighting, verbatim."""

    records: dict[str, list[SightingRecord]] = {}
    for turn in entry.transcript.turns:
        for observation in turn.observations:
            if not isinstance(observation, SawPlayerObservation):
                continue
            if not canonical_rooms(observation.room):
                continue
            records.setdefault(turn.speaker, []).append(
                SightingRecord(
                    subject=observation.subject,
                    room=observation.room,
                    tick=observation.tick,
                )
            )
    return {speaker: tuple(rows) for speaker, rows in records.items()}


def _ungroundable_sighting_channel(
    entry: MeetingReplayEntry,
) -> dict[str, tuple[SightingRecord, ...]]:
    """A channel present for every sighting speaker that matches nothing they said."""

    speakers = {
        turn.speaker
        for turn in entry.transcript.turns
        for observation in turn.observations
        if isinstance(observation, SawPlayerObservation)
    }
    return {
        speaker: (
            SightingRecord(subject="p-nobody", room=sorted(CANONICAL_ROOMS)[0], tick=0),
        )
        for speaker in speakers
    }


class TestLiveDetectorCommittedBytesByteIdentity:
    """The graduated ``detect_contradictions`` re-derives the recorded flags
    byte-identically over every committed meeting, all four sets (baseline 6).

    Coverage beyond the ``test_transcript.py`` re-derivation pin: this walk
    includes ``vent_sighting`` (via records rebuilt from the recorded verdicts)
    across all four sets exhaustively (707 meetings). Levers 1 and 2 are
    UNCONDITIONAL, so the detector ignores its ``env`` for them -- env absent and
    env={} must agree -- while the movement lever is DEFAULT-OFF, so a live
    movement channel must leave every recorded flag exactly where it is.
    """

    def test_re_derivation_equals_recorded_on_every_committed_meeting(self) -> None:
        entries = _committed_meeting_entries()
        # Guard: a thinned checkout or a glob typo fails here, not vacuously.
        assert len(entries) == _COMMITTED_MEETINGS
        mismatches: list[str] = []
        for set_name, seed, entry in entries:
            roster = _living_roster(entry)
            records = _vent_records_from_recorded_flags(entry)
            # Levers unconditional: env absent (default) AND an explicit empty
            # mapping resolve identically (the key is no longer read).
            rederived = detect_contradictions(
                entry.transcript, roster=roster, vent_witness_records=records
            )
            rederived_empty_env = detect_contradictions(
                entry.transcript,
                roster=roster,
                vent_witness_records=records,
                env={},
            )
            # env is ignored => env absent and env={} are byte-identical.
            if rederived != rederived_empty_env:
                mismatches.append(
                    f"{set_name} seed {seed} {entry.meeting_id}: env drift"
                )
            # Determinism: a second call reproduces the first exactly.
            if rederived != detect_contradictions(
                entry.transcript, roster=roster, vent_witness_records=records
            ):
                mismatches.append(f"{set_name} seed {seed} {entry.meeting_id}: nondet")
            if not _flags_match(rederived, entry.contradictions):
                mismatches.append(
                    f"{set_name} seed {seed} {entry.meeting_id}: "
                    f"{len(rederived)} re-derived vs {len(entry.contradictions)} recorded"
                )
        assert mismatches == []

    def test_a_live_movement_channel_moves_nothing_while_the_lever_is_off(
        self,
    ) -> None:
        mismatches: list[str] = []
        for set_name, seed, entry in _committed_meeting_entries():
            roster = _living_roster(entry)
            vents = _vent_records_from_recorded_flags(entry)
            baseline = detect_contradictions(
                entry.transcript, roster=roster, vent_witness_records=vents
            )
            with_channel = detect_contradictions(
                entry.transcript,
                roster=roster,
                vent_witness_records=vents,
                move_witness_records=_planted_move_channel(entry),
            )
            if baseline != with_channel:
                mismatches.append(f"{set_name} seed {seed} {entry.meeting_id}")
        assert mismatches == []

    def test_a_live_sighting_channel_moves_nothing_while_the_lever_is_off(
        self,
    ) -> None:
        # The grounded-prosecution mapping is threaded by the manager on every
        # meeting; with the lever off it must leave every recorded flag exactly
        # where it is. The planted channel grounds EVERY spoken sighting, so a
        # leak of the lever into the OFF path would re-band the class at once.
        mismatches: list[str] = []
        for set_name, seed, entry in _committed_meeting_entries():
            roster = _living_roster(entry)
            vents = _vent_records_from_recorded_flags(entry)
            with_channel = detect_contradictions(
                entry.transcript,
                roster=roster,
                vent_witness_records=vents,
                sighting_records=_planted_sighting_channel(entry),
            )
            if not _flags_match(with_channel, entry.contradictions):
                mismatches.append(f"{set_name} seed {seed} {entry.meeting_id}")
        assert mismatches == []

    def test_the_planted_channel_is_live_when_the_lever_is_on(self) -> None:
        # The OFF pin above would pass vacuously if the plant grounded nothing.
        moved = 0
        for _set_name, _seed, entry in _committed_meeting_entries():
            roster = _living_roster(entry)
            vents = _vent_records_from_recorded_flags(entry)
            baseline = detect_contradictions(
                entry.transcript, roster=roster, vent_witness_records=vents
            )
            on = detect_contradictions(
                entry.transcript,
                roster=roster,
                vent_witness_records=vents,
                move_witness_records=_planted_move_channel(entry),
                env=_MOVEMENT_ON,
            )
            moved += int(baseline != on)
        assert moved > 0


# --- Task 18.12: the committed-samples lever census (the graduated substrate) ---
#
# What the 18.11 gate read as the OFF->ON counterfactual, the 18.12 record ADOPTS:
# lever 1 (whereabouts-interior exemption) and lever 2 (grounded vent-placement)
# are UNCONDITIONAL, so ``detect_contradictions`` ignores its ``env`` and the
# ``env``-toggle differential the pre-graduation census measured has collapsed to
# zero (env absent == ``_L1_ENV`` == ``_L2_ENV``). This census therefore pins the
# LIVE (graduated) detector's flag substrate over the re-recorded SAMPLE bytes:
# the exemption class is now all-STRONG (the invariant the levers reversed), and
# the ON-vs-OFF vent diff is zero. The ``_L*_ENV`` legs are retained to PROVE the
# collapse (they must equal the env-absent leg). ml_corpus is excluded until Task
# 18.13 re-records it on baseline 6; the frozen pre-graduation counterfactual
# (the 25/20-5 funnel, the 5 grounded vents, the 16-claim exemption) lives in
# ``audits/audit-phase-18-baseline-6.md`` and the 18.11 planning audit.
#
# ``trigger_kind`` is threaded as ``None`` (RECON R1: not load-bearing on
# committed bytes -- the two lever paths never read it, lever 1 inside
# :func:`_detect_alibi_vs_sightings`, lever 2 inside
# :func:`_detect_vent_placement_contradictions`, neither of which calls
# ``reconstruct_stated_paths``).

_L1_ENV = {ENV_WHEREABOUTS_INTERIOR_FLAGS: "1"}
_L2_ENV = {ENV_VENT_PLACEMENT_CONTRADICTIONS: "1"}


@functools.cache
def _roles_by_seed(set_name: str) -> dict[int, dict[str, str]]:
    """``seed -> {player_id: role}`` from a set's tournament-eval-report.json.

    ``role`` is ``"CREWMATE"`` / ``"IMPOSTOR"``; a degenerate self-alibi's LIAR
    role and a vent placement's SUBJECT role are both read here, keyed by the
    game seed (mirrors :meth:`tests.agents.test_absence_prior` `roles_by_seed`).
    """

    import json

    report = json.loads(
        (_REPO_ROOT / "replays" / set_name / "tournament-eval-report.json").read_text(
            encoding="utf-8"
        )
    )
    return {game["seed"]: game["roles"] for game in report["report"]["games"]}


def _degenerate_self_alibi_ids(
    entry: MeetingReplayEntry, roster: frozenset[str]
) -> dict[str, tuple[str, str]]:
    """``event_id -> (subject, class)`` for degenerate single-tick self-alibis.

    The Task 18.9 lever-1 class: ``from_tick == to_tick`` AND the speaker is its
    own subject, exactly how :func:`_iter_alibis` indexes a
    :class:`~meetings.schemas.WhereaboutsClaim` (``class == "whereabouts"``, event
    id :func:`_turn_whereabouts_id`) and how a genuine single-tick self-stated
    :class:`~meetings.schemas.AlibiClaim` reads (``class == "alibi"``, event id
    ``turn:{turn_id}:claim:{index}``). Roster-filtered on the subject, matching
    :func:`detect_contradictions`' own alibi filter.
    """

    out: dict[str, tuple[str, str]] = {}
    for turn in entry.transcript.turns:
        for index, claim in enumerate(turn.claims):
            if (
                isinstance(claim, AlibiClaim)
                and claim.from_tick == claim.to_tick
                and claim.subject == turn.speaker
                and claim.subject in roster
            ):
                out[f"turn:{turn.turn_id}:claim:{index}"] = (claim.subject, "alibi")
        for index, obs in enumerate(turn.observations):
            if isinstance(obs, WhereaboutsClaim) and turn.speaker in roster:
                out[_turn_whereabouts_id(turn=turn, index=index)] = (
                    turn.speaker,
                    "whereabouts",
                )
    return out


@dataclass(frozen=True)
class _SetCensus:
    meetings: int
    # --- Lever 1 exemption census (the LIVE graduated detector) --------------
    # (a) DISTINCT degenerate self-alibi claims carrying >=1 alibi_vs_sighting
    #     flag, split by the liar (subject) role and by class. Since baseline 6
    #     they are all STRONG (the graduation reversed the weak invariant).
    exempt_off_distinct_by_role: dict[str, int]
    exempt_off_distinct_by_class: dict[str, int]
    exempt_off_flag_count: int
    exempt_class_all_strong: bool
    # (b) the ``_L1_ENV`` leg -- identical to the default leg (env is ignored),
    #     so this pins the same DISTINCT/flag counts and PROVES the collapse.
    exempt_on_strong_distinct_by_role: dict[str, int]
    exempt_on_strong_flag_count: int
    # the default leg and the ``_L1_ENV`` leg carry the SAME flag ids (env is
    # ignored -- neither adds/drops nor re-bands relative to the other).
    exempt_off_equals_on_strong_ids: bool
    l1_leaves_flag_id_set_unchanged: bool
    # --- Lever 2 vent-placement census --------------------------------------
    # alibi_vs_physical flags present in the ``_L2_ENV`` leg but ABSENT in the
    # default leg -- zero now that env is ignored (both legs ON). Distinct
    # subjects by SUBJECT role (empty since the diff collapsed).
    vent_flag_count: int
    vent_subjects_by_role: dict[str, int]
    vent_new_ids_all_physical: bool
    # --- the live census IS the recorded substrate (re-derived == recorded) --
    off_matches_recorded: bool


@functools.cache
def _committed_lever_census() -> dict[str, _SetCensus]:
    """One shared re-derivation walk of the SAMPLE corpus computing every cell.

    For every committed sample meeting: reconstruct the roster (ballot voters)
    and the rebuilt vent channel, then re-derive :func:`detect_contradictions`
    THREE ways -- default (env absent), ``_L1_ENV``, ``_L2_ENV``. Since the levers
    graduated (baseline 6) all three legs are byte-identical (env is ignored), so
    the exemption census pins the LIVE flag substrate (all STRONG) and the vent
    diff collapses to zero. Cached, so the whole census is one pass over the
    (already cached, samples-only) entries.
    """

    from collections import Counter

    per_set: dict[str, _SetCensus] = {}
    for set_dir in _COMMITTED_SETS:
        set_name = f"{set_dir.parent.name}/{set_dir.name}"
        roles = _roles_by_seed(set_name)

        exempt_off_role: Counter[str] = Counter()
        exempt_off_class: Counter[str] = Counter()
        exempt_on_role: Counter[str] = Counter()
        exempt_off_flags = 0
        exempt_on_flags = 0
        all_strong = True
        off_equals_on_ids = True
        l1_id_set_unchanged = True
        vent_flags = 0
        vent_subjects: dict[str, set[tuple[int, str]]] = {}
        vent_new_all_physical = True
        off_matches = True
        meetings = 0

        for entry_set, seed, entry in _committed_meeting_entries():
            if entry_set != set_name:
                continue
            meetings += 1
            role_map = roles[seed]
            roster = _living_roster(entry)
            records = _vent_records_from_recorded_flags(entry)
            degenerate = _degenerate_self_alibi_ids(entry, roster)

            off = detect_contradictions(
                entry.transcript, roster=roster, vent_witness_records=records
            )
            on1 = detect_contradictions(
                entry.transcript,
                roster=roster,
                vent_witness_records=records,
                env=_L1_ENV,
            )
            on2 = detect_contradictions(
                entry.transcript,
                roster=roster,
                vent_witness_records=records,
                env=_L2_ENV,
            )

            if not _flags_match(off, entry.contradictions):
                off_matches = False

            # (a) default leg: distinct degenerate ids carrying an
            #     alibi_vs_sighting flag -- all STRONG since the graduation.
            off_carrying: set[str] = set()
            for flag in off:
                if flag.kind != "alibi_vs_sighting":
                    continue
                for eid in (flag.event_a_id, flag.event_b_id):
                    if eid in degenerate:
                        off_carrying.add(eid)
                        exempt_off_flags += 1
                        if is_weak_contradiction(flag):
                            all_strong = False
            for eid in off_carrying:
                subject, cls = degenerate[eid]
                exempt_off_role[role_map[subject]] += 1
                exempt_off_class[cls] += 1

            # (b) ON: distinct degenerate ids carrying a STRONG alibi_vs_sighting.
            on_strong: set[str] = set()
            for flag in on1:
                if flag.kind != "alibi_vs_sighting" or is_weak_contradiction(flag):
                    continue
                for eid in (flag.event_a_id, flag.event_b_id):
                    if eid in degenerate:
                        on_strong.add(eid)
                        exempt_on_flags += 1
            for eid in on_strong:
                subject, _cls = degenerate[eid]
                exempt_on_role[role_map[subject]] += 1
            if off_carrying != on_strong:
                off_equals_on_ids = False
            # env is ignored: the default and _L1_ENV legs carry the same ids.
            if {f.contradiction_id for f in off} != {f.contradiction_id for f in on1}:
                l1_id_set_unchanged = False

            # Lever 2 vent census: flags present in the _L2_ENV leg but absent in
            # the default leg -- empty now that env is ignored (both legs ON).
            off_ids = {f.contradiction_id for f in off}
            for flag in on2:
                if flag.contradiction_id in off_ids:
                    continue
                if flag.kind != "alibi_vs_physical":
                    vent_new_all_physical = False
                    continue
                vent_flags += 1
                for subject in flag.subjects:
                    vent_subjects.setdefault(role_map.get(subject, "?"), set()).add(
                        (seed, subject)
                    )

        per_set[set_name] = _SetCensus(
            meetings=meetings,
            exempt_off_distinct_by_role=dict(exempt_off_role),
            exempt_off_distinct_by_class=dict(exempt_off_class),
            exempt_off_flag_count=exempt_off_flags,
            exempt_class_all_strong=all_strong,
            exempt_on_strong_distinct_by_role=dict(exempt_on_role),
            exempt_on_strong_flag_count=exempt_on_flags,
            exempt_off_equals_on_strong_ids=off_equals_on_ids,
            l1_leaves_flag_id_set_unchanged=l1_id_set_unchanged,
            vent_flag_count=vent_flags,
            vent_subjects_by_role={r: len(s) for r, s in vent_subjects.items()},
            vent_new_ids_all_physical=vent_new_all_physical,
            off_matches_recorded=off_matches,
        )
    return per_set


class TestExemptionCensus:
    """Lever 1 (endpoint-band whereabouts exemption) -- the graduated substrate
    census over the committed SAMPLE bytes.

    Per sample set: the DISTINCT degenerate single-tick self-alibi claims that
    carry an ``alibi_vs_sighting`` flag. Since baseline 6 they are all STRONG (the
    graduation reversed the pre-record weak invariant the 18.11 gate read). The
    default leg and the ``_L1_ENV`` leg are byte-identical (env is ignored), so the
    id sets and counts agree -- proving the collapse the record adopts. ml_corpus
    cells are dropped until Task 18.13 re-records them on baseline 6.
    """

    @pytest.fixture(scope="class")
    def census(self) -> dict[str, _SetCensus]:
        return _committed_lever_census()

    def test_exempt_class_is_all_strong_every_sample_set(
        self, census: dict[str, _SetCensus]
    ) -> None:
        # The graduation ADOPTED: every degenerate single-tick self-alibi that
        # carries an alibi_vs_sighting flag is now STRONG (was all weak-tier
        # pre-record -- the audit §3.3 invariant the levers reversed).
        for cell in census.values():
            assert cell.exempt_class_all_strong is True

    def test_env_is_ignored_the_class_is_stable_every_set(
        self, census: dict[str, _SetCensus]
    ) -> None:
        # env is ignored: the default leg and the _L1_ENV leg carry the SAME flag
        # ids and the SAME exempt census -- no flag is added, dropped, or re-banded
        # between them (the differential the pre-graduation census measured is 0).
        for cell in census.values():
            assert cell.exempt_off_equals_on_strong_ids is True
            assert cell.l1_leaves_flag_id_set_unchanged is True
            assert cell.exempt_off_flag_count == cell.exempt_on_strong_flag_count
            assert (
                cell.exempt_off_distinct_by_role
                == cell.exempt_on_strong_distinct_by_role
            )

    def test_samples_9p2i_cells(self, census: dict[str, _SetCensus]) -> None:
        cell = census["samples/9p2i"]
        assert cell.meetings == 165
        assert cell.exempt_off_distinct_by_role == {"CREWMATE": 37, "IMPOSTOR": 3}
        assert cell.exempt_off_distinct_by_class == {"whereabouts": 38, "alibi": 2}
        assert cell.exempt_off_flag_count == 48
        assert cell.exempt_on_strong_distinct_by_role == {"CREWMATE": 37, "IMPOSTOR": 3}
        assert cell.exempt_on_strong_flag_count == 48

    def test_samples_4p1i_cells(self, census: dict[str, _SetCensus]) -> None:
        cell = census["samples/4p1i"]
        assert cell.meetings == 39
        assert cell.exempt_off_distinct_by_role == {"CREWMATE": 1}
        assert cell.exempt_off_distinct_by_class == {"whereabouts": 1}
        assert cell.exempt_off_flag_count == 1
        assert cell.exempt_on_strong_distinct_by_role == {"CREWMATE": 1}
        assert cell.exempt_on_strong_flag_count == 1

    def test_live_census_equals_recorded_on_the_census_walk(
        self, census: dict[str, _SetCensus]
    ) -> None:
        # The live (graduated) census IS the recorded substrate: re-deriving the
        # detector over each sample set reproduces the recorded flags exactly, so
        # the census baseline and the committed bytes are the same substrate.
        for cell in census.values():
            assert cell.off_matches_recorded is True


class TestVentPlacementCensus:
    """Lever 2 (grounded vent-placement variant) -- the graduated substrate
    census over the committed SAMPLE bytes.

    Since baseline 6 the vent-placement lever is UNCONDITIONAL, so the ``_L2_ENV``
    leg is byte-identical to the default leg (env is ignored) and the "present ON
    but absent OFF" differential this cell measured collapses to zero on every
    sample set. The grounded ``alibi_vs_physical`` flags are now part of the
    recorded substrate itself (pinned by ``test_transcript.py`` and the byte-
    identity walk); ml_corpus cells return when 18.13 re-records them.
    """

    @pytest.fixture(scope="class")
    def census(self) -> dict[str, _SetCensus]:
        return _committed_lever_census()

    def test_no_new_flags_since_env_is_ignored_every_set(
        self, census: dict[str, _SetCensus]
    ) -> None:
        for cell in census.values():
            assert cell.vent_new_ids_all_physical is True
            # The diff collapsed, so no subject is measured -- an empty set passes
            # the impostor-only invariant vacuously.
            assert set(cell.vent_subjects_by_role) <= {"IMPOSTOR"}

    def test_samples_9p2i_vent_cells(self, census: dict[str, _SetCensus]) -> None:
        cell = census["samples/9p2i"]
        # env is ignored, so the _L2_ENV leg equals the default leg: no
        # alibi_vs_physical flag is present in one and absent in the other, so the
        # ON-vs-OFF diff this cell measures collapses to 0.
        assert cell.vent_flag_count == 0
        assert cell.vent_subjects_by_role == {}

    def test_samples_4p1i_vent_cells(self, census: dict[str, _SetCensus]) -> None:
        cell = census["samples/4p1i"]
        assert cell.vent_flag_count == 0
        assert cell.vent_subjects_by_role == {}


# --- Task 20.26: the grounded-prosecution census over the committed bytes ---
#
# The committed replays persist no private ``SightingRecord``s, so the census
# reads the lever through two PLANTED channels that bracket the truth: one that
# grounds every spoken sighting (the lever's most generous reading -- whatever
# it still demotes, rules (b) and (c) did) and one that grounds none of them
# (rule (a) alone). The reconstructed-memory reading, which needs the replay
# walk, lives in ``tests/eval/test_evidence_honesty.py``.


@dataclass(frozen=True)
class _GroundedSetCensus:
    meetings: int
    bands_off: dict[str, int]
    bands_grounded: dict[str, int]
    bands_ungrounded: dict[str, int]
    structural_drift: int


def _band_census(flags: tuple[ContradictionRef, ...]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for flag in flags:
        key = f"{flag.kind}:{'weak' if is_weak_contradiction(flag) else 'strong'}"
        counts[key] = counts.get(key, 0) + 1
    return counts


@functools.cache
def _grounded_prosecution_census() -> dict[str, _GroundedSetCensus]:
    """One shared walk of the 707 committed meetings, three detector legs each."""

    per_set: dict[str, _GroundedSetCensus] = {}
    for set_dir in _COMMITTED_SETS:
        set_name = f"{set_dir.parent.name}/{set_dir.name}"
        meetings = 0
        drift = 0
        bands: dict[str, dict[str, int]] = {
            "off": {},
            "grounded": {},
            "ungrounded": {},
        }
        for entry_set, _seed, entry in _committed_meeting_entries():
            if entry_set != set_name:
                continue
            meetings += 1
            roster = _living_roster(entry)
            vents = _vent_records_from_recorded_flags(entry)
            grounding = _planted_sighting_channel(entry)
            off = detect_contradictions(
                entry.transcript, roster=roster, vent_witness_records=vents
            )
            legs = {
                "off": off,
                "grounded": detect_contradictions(
                    entry.transcript,
                    roster=roster,
                    vent_witness_records=vents,
                    sighting_records=grounding,
                    env=_GROUNDED_ON,
                ),
                "ungrounded": detect_contradictions(
                    entry.transcript,
                    roster=roster,
                    vent_witness_records=vents,
                    sighting_records=_ungroundable_sighting_channel(entry),
                    env=_GROUNDED_ON,
                ),
            }
            off_by_id = {flag.contradiction_id: flag for flag in off}
            for leg, flags in legs.items():
                for key, count in _band_census(flags).items():
                    bands[leg][key] = bands[leg].get(key, 0) + count
                if leg == "off":
                    continue
                if len(flags) != len(off):
                    drift += 1
                    continue
                for flag in flags:
                    original = off_by_id.get(flag.contradiction_id)
                    if original is None or (
                        original.kind,
                        original.event_a_id,
                        original.event_b_id,
                        original.subjects,
                    ) != (
                        flag.kind,
                        flag.event_a_id,
                        flag.event_b_id,
                        flag.subjects,
                    ):
                        drift += 1
        per_set[set_name] = _GroundedSetCensus(
            meetings=meetings,
            bands_off=bands["off"],
            bands_grounded=bands["grounded"],
            bands_ungrounded=bands["ungrounded"],
            structural_drift=drift,
        )
    return per_set


class TestGroundedProsecutionCommittedCensus:
    """The lever's price and its scope firewall, over all 707 committed meetings."""

    @pytest.fixture(scope="class")
    def census(self) -> dict[str, _GroundedSetCensus]:
        return _grounded_prosecution_census()

    def test_the_census_covers_every_committed_meeting(
        self, census: dict[str, _GroundedSetCensus]
    ) -> None:
        assert sum(cell.meetings for cell in census.values()) == _COMMITTED_MEETINGS

    def test_only_the_sighting_kind_moves(
        self, census: dict[str, _GroundedSetCensus]
    ) -> None:
        # The scope firewall: the vent channel, the physical kind and the
        # conflict kind are byte-stable on BOTH legs, per set.
        untouched = (
            "vent_sighting:strong",
            "alibi_vs_physical:strong",
            "alibi_vs_physical:weak",
            "alibi_conflict:weak",
        )
        for cell in census.values():
            for band in untouched:
                assert cell.bands_grounded.get(band, 0) == cell.bands_off.get(band, 0)
                assert cell.bands_ungrounded.get(band, 0) == cell.bands_off.get(band, 0)
            # A demotion rewrites the description only: same count, same ids,
            # same kinds, same subjects.
            assert cell.structural_drift == 0

    def test_the_committed_class_and_the_untouched_kinds(
        self, census: dict[str, _GroundedSetCensus]
    ) -> None:
        totals: dict[str, int] = {}
        for cell in census.values():
            for band, count in cell.bands_off.items():
                totals[band] = totals.get(band, 0) + count
        assert totals == {
            "alibi_vs_sighting:strong": 234,
            "alibi_vs_sighting:weak": 79,
            "alibi_vs_physical:strong": 37,
            "alibi_vs_physical:weak": 5,
            "alibi_conflict:weak": 35,
            "vent_sighting:strong": 440,
        }

    def test_the_ungrounded_leg_convicts_on_nothing(
        self, census: dict[str, _GroundedSetCensus]
    ) -> None:
        # Rule (a) alone, at its limit: no speaker's record supports anything
        # they said, so the whole class of 313 flags is weak and none convicts.
        strong = sum(
            cell.bands_ungrounded.get("alibi_vs_sighting:strong", 0)
            for cell in census.values()
        )
        weak = sum(
            cell.bands_ungrounded.get("alibi_vs_sighting:weak", 0)
            for cell in census.values()
        )
        assert (strong, weak) == (0, 313)

    def test_the_fully_grounded_leg_still_drops_most_of_the_class(
        self, census: dict[str, _GroundedSetCensus]
    ) -> None:
        # Ground EVERY spoken sighting -- the most generous reading the lever can
        # be given -- and 234 STRONG flags still come out as 23: the rest fall to
        # rule (b) (one speaker is the whole prosecution) or rule (c) (the
        # one-tick self-placement is an edge again).
        strong = sum(
            cell.bands_grounded.get("alibi_vs_sighting:strong", 0)
            for cell in census.values()
        )
        weak = sum(
            cell.bands_grounded.get("alibi_vs_sighting:weak", 0)
            for cell in census.values()
        )
        assert (strong, weak) == (23, 290)
        assert census["samples/9p2i"].bands_grounded["alibi_vs_sighting:strong"] == 2
        assert census["ml_corpus/9p2i"].bands_grounded["alibi_vs_sighting:strong"] == 21
        for set_name in ("samples/4p1i", "ml_corpus/4p1i"):
            assert (
                census[set_name].bands_grounded.get("alibi_vs_sighting:strong", 0) == 0
            )


def _committed_meeting(set_name: str, seed: int, meeting_id: str) -> MeetingReplayEntry:
    for entry_set, entry_seed, entry in _committed_meeting_entries():
        if (entry_set, entry_seed, entry.meeting_id) == (set_name, seed, meeting_id):
            return entry
    raise AssertionError(f"{set_name} seed {seed} {meeting_id} is not committed")


class TestGroundedProsecutionInjusticeShapes:
    """The three meetings the review named, read under the lever.

    Each ejected a crewmate on a STRONG ``alibi_vs_sighting`` flag. They are read
    here through the FULLY-GROUNDED plant -- the most generous channel the lever
    can be handed -- so a demotion here holds a fortiori for the sparser channel
    the speakers actually held.
    """

    def _flags_on_victim(
        self, set_name: str, seed: int, meeting_id: str
    ) -> tuple[str, tuple[ContradictionRef, ...], tuple[ContradictionRef, ...]]:
        entry = _committed_meeting(set_name, seed, meeting_id)
        victim = entry.ejected_player_id
        assert victim is not None
        roster = _living_roster(entry)
        vents = _vent_records_from_recorded_flags(entry)
        off = detect_contradictions(
            entry.transcript, roster=roster, vent_witness_records=vents
        )
        on = detect_contradictions(
            entry.transcript,
            roster=roster,
            vent_witness_records=vents,
            sighting_records=_planted_sighting_channel(entry),
            env=_GROUNDED_ON,
        )
        named = tuple(
            flag
            for flag in off
            if flag.kind == "alibi_vs_sighting" and victim in flag.subjects
        )
        under_lever = tuple(
            flag
            for flag in on
            if flag.kind == "alibi_vs_sighting" and victim in flag.subjects
        )
        return victim, named, under_lever

    def test_seed_17_meeting_0_is_the_one_tick_self_placement(self) -> None:
        victim, off, on = self._flags_on_victim(
            "samples/9p2i", 17, "headless-seed-17:meeting-0"
        )
        assert victim == "p-1"
        assert len(off) == 2 and all(not is_weak_contradiction(f) for f in off)
        assert all(is_weak_contradiction(f) for f in on)
        # Rule (c): the roll-call tick is an endpoint again.
        for flag in on:
            assert WEAK_REASON_ENDPOINT_TICK in flag.description

    def test_seed_23_meeting_1_is_the_one_tick_self_placement(self) -> None:
        victim, off, on = self._flags_on_victim(
            "samples/9p2i", 23, "headless-seed-23:meeting-1"
        )
        assert victim == "p-4"
        assert len(off) == 1 and not is_weak_contradiction(off[0])
        assert is_weak_contradiction(on[0]) is True
        assert WEAK_REASON_ENDPOINT_TICK in on[0].description

    def test_seed_8_meeting_4_is_the_lone_grounded_source(self) -> None:
        victim, off, on = self._flags_on_victim(
            "samples/9p2i", 8, "headless-seed-8:meeting-4"
        )
        assert victim == "p-9"
        assert len(off) == 1 and not is_weak_contradiction(off[0])
        # Rule (b): the sighting side grounds, but one speaker is the whole case.
        assert WEAK_REASON_LONE_GROUNDED_SOURCE in on[0].description
        assert is_weak_contradiction(on[0]) is True
