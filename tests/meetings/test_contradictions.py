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
    ObservationClaim,
    SawPlayerObservation,
)
from meetings.transcript import detect_contradictions


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
