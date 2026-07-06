"""Tests for the Task 15.4 grounded ``vent_sighting`` hard flag.

The grounding chokepoint is the task's whole defense against
evidence-minting: a spoken :class:`~meetings.schemas.SawVentObservation`
raises the role-proving STRONG flag ONLY when it matches one of the
SPEAKER'S OWN typed :class:`~meetings.schemas.VentWitnessRecord` rows
(subject + canonically intersecting room, tick within
:data:`~meetings.transcript.VENT_GROUNDING_TICK_TOLERANCE`); a fabricated
observation records as ordinary testimony and raises NO flag. The fold-side
contract is pinned too: a grounded flag rides the EXISTING strong-flag path
(``apply_contradiction_rule`` + ``MEETING_CONTRADICTION_LIFT_CAP``), never a
new stacking channel.
"""

from __future__ import annotations

from agents.memory.beliefs import (
    CONTRADICTION_SUSPICION_DELTA,
    MEETING_CONTRADICTION_LIFT_CAP,
    BeliefState,
    apply_contradiction_rule,
)
from meetings.schemas import (
    Claim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawVentObservation,
    VentWitnessRecord,
)
from meetings.transcript import (
    VENT_GROUNDING_TICK_TOLERANCE,
    detect_contradictions,
    independent_voices,
    is_weak_contradiction,
)

# --- Builders --------------------------------------------------------------


def _saw_vent(
    *, tick: int = 14, subject: str = "p-5", room: str = "MEDBAY"
) -> SawVentObservation:
    return SawVentObservation(type="saw_vent", tick=tick, subject=subject, room=room)


def _record(
    *, tick: int = 14, subject: str = "p-5", room: str = "MEDBAY"
) -> VentWitnessRecord:
    return VentWitnessRecord(subject=subject, room=room, tick=tick)


def _turn(
    *,
    turn_index: int,
    speaker: str,
    turn_kind: str = "opening",
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
    free_text: str | None = None,
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to=None,
        observations=observations,
        claims=claims,
        free_text=(
            free_text if free_text is not None else f"turn {turn_index} from {speaker}"
        ),
    )


_ROSTER = frozenset({"p-1", "p-2", "p-3", "p-5"})


def _vent_transcript(
    observation: SawVentObservation | None = None,
) -> MeetingTranscript:
    spoken = observation if observation is not None else _saw_vent()
    return MeetingTranscript(
        turns=(_turn(turn_index=0, speaker="p-2", observations=(spoken,)),)
    )


def _vent_flags(flags: tuple[ContradictionRef, ...]) -> list[ContradictionRef]:
    return [flag for flag in flags if flag.kind == "vent_sighting"]


# --- Grounded: the STRONG flag ----------------------------------------------


class TestGroundedVentFlag:
    def test_matching_record_raises_strong_flag_against_subject(self) -> None:
        flags = detect_contradictions(
            _vent_transcript(),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(),)},
        )

        vent_flags = _vent_flags(flags)
        assert len(vent_flags) == 1
        flag = vent_flags[0]
        assert flag.subjects == ("p-5",)
        assert is_weak_contradiction(flag) is False
        # Both event ids reference the spoken observation — the public,
        # citable surface (its turn id is what primary_reason_id reaches).
        assert flag.event_a_id == "turn:m-1:turn-0:obs:0"
        assert flag.event_b_id == "turn:m-1:turn-0:obs:0"
        # The description quotes the RECORD (deterministic memory).
        assert "p-2 witnessed p-5 vent in MEDBAY at tick 14" in flag.description
        assert "impostor-only" in flag.description

    def test_tick_within_tolerance_grounds(self) -> None:
        observation = _saw_vent(tick=14 + VENT_GROUNDING_TICK_TOLERANCE)

        flags = detect_contradictions(
            _vent_transcript(observation),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(tick=14),)},
        )

        assert len(_vent_flags(flags)) == 1

    def test_compound_room_label_still_grounds(self) -> None:
        # The detector's one room-normalisation point (canonical_rooms)
        # applies: a compound spoken label whose member set contains the
        # record's canonical engine room matches.
        observation = _saw_vent(room="LABS/MEDBAY")

        flags = detect_contradictions(
            _vent_transcript(observation),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(room="MEDBAY"),)},
        )

        assert len(_vent_flags(flags)) == 1

    def test_deterministic_across_reruns(self) -> None:
        records = {"p-2": (_record(),)}

        first = detect_contradictions(
            _vent_transcript(), roster=_ROSTER, vent_witness_records=records
        )
        second = detect_contradictions(
            _vent_transcript(), roster=_ROSTER, vent_witness_records=records
        )

        assert first == second

    def test_proxy_intra_turn_guard_does_not_gut_the_flag(self) -> None:
        # Both of a vent flag's event ids resolve to the ONE speaker and the
        # subject is a third party — the exact shape the 10.10 guard
        # re-targets WEAK at the speaker. The vent flag joins after that
        # guard by design: it must stay STRONG against the SUBJECT.
        flags = detect_contradictions(
            _vent_transcript(),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(),)},
        )

        flag = _vent_flags(flags)[0]
        assert flag.subjects == ("p-5",)
        assert is_weak_contradiction(flag) is False


# --- Fabricated: NO flag (the task's most important test) --------------------


class TestFabricatedVentClaimRaisesNoFlag:
    def test_no_records_at_all_raises_no_flag(self) -> None:
        flags = detect_contradictions(
            _vent_transcript(),
            roster=_ROSTER,
            vent_witness_records={"p-2": ()},
        )

        assert _vent_flags(flags) == []

    def test_absent_channel_raises_no_flag(self) -> None:
        # The legacy-caller default: no typed channel at all (None) grounds
        # nothing — committed transcripts re-derive byte-identically.
        flags = detect_contradictions(_vent_transcript(), roster=_ROSTER)

        assert _vent_flags(flags) == []

    def test_wrong_subject_raises_no_flag(self) -> None:
        flags = detect_contradictions(
            _vent_transcript(_saw_vent(subject="p-3")),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(subject="p-5"),)},
        )

        assert _vent_flags(flags) == []

    def test_wrong_room_raises_no_flag(self) -> None:
        flags = detect_contradictions(
            _vent_transcript(_saw_vent(room="REACTOR")),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(room="MEDBAY"),)},
        )

        assert _vent_flags(flags) == []

    def test_tick_beyond_tolerance_raises_no_flag(self) -> None:
        observation = _saw_vent(tick=14 + VENT_GROUNDING_TICK_TOLERANCE + 1)

        flags = detect_contradictions(
            _vent_transcript(observation),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(tick=14),)},
        )

        assert _vent_flags(flags) == []

    def test_only_the_speakers_own_records_ground(self) -> None:
        # ANOTHER participant's genuine record must not ground p-2's claim:
        # grounding is a self-channel comparison, never a pooled one.
        flags = detect_contradictions(
            _vent_transcript(),
            roster=_ROSTER,
            vent_witness_records={"p-3": (_record(),)},
        )

        assert _vent_flags(flags) == []

    def test_non_roster_subject_raises_no_flag(self) -> None:
        flags = detect_contradictions(
            _vent_transcript(_saw_vent(subject="p-99")),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(subject="p-99"),)},
        )

        assert _vent_flags(flags) == []

    def test_fabrication_still_records_as_testimony(self) -> None:
        # The observation is accepted speech: it stays on the recorded turn
        # (voters may weigh it) — only the hard-evidence channel is closed.
        transcript = _vent_transcript()

        flags = detect_contradictions(
            transcript, roster=_ROSTER, vent_witness_records={"p-2": ()}
        )

        assert _vent_flags(flags) == []
        assert isinstance(transcript.turns[0].observations[0], SawVentObservation)


# --- Fold semantics: the existing strong-flag path, no new channel ----------


class TestVentFlagFoldSemantics:
    def _grounded_flag(self) -> ContradictionRef:
        flags = detect_contradictions(
            _vent_transcript(),
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(),)},
        )
        (flag,) = _vent_flags(flags)
        return flag

    def test_flag_lifts_by_the_full_strong_delta(self) -> None:
        beliefs = BeliefState()
        beliefs.seed_player("p-5", suspicion=0.5, trust=0.5)

        updated = apply_contradiction_rule(beliefs, [self._grounded_flag()])

        assert updated.view("p-5").suspicion == 0.5 + CONTRADICTION_SUSPICION_DELTA

    def test_two_grounded_flags_cap_at_one_strong_flags_worth(self) -> None:
        # Two independent witnesses ground two flags against the same
        # subject; the per-subject lift stays capped at
        # MEETING_CONTRADICTION_LIFT_CAP — the same cap semantics the
        # witnessed-kill strong flag rides, no new stacking channel.
        transcript = MeetingTranscript(
            turns=(
                _turn(turn_index=0, speaker="p-2", observations=(_saw_vent(),)),
                _turn(turn_index=1, speaker="p-3", observations=(_saw_vent(),)),
            )
        )
        flags = detect_contradictions(
            transcript,
            roster=_ROSTER,
            vent_witness_records={"p-2": (_record(),), "p-3": (_record(),)},
        )
        vent_flags = _vent_flags(flags)
        assert len(vent_flags) == 2

        beliefs = BeliefState()
        beliefs.seed_player("p-5", suspicion=0.5, trust=0.5)
        updated = apply_contradiction_rule(beliefs, vent_flags)

        assert updated.view("p-5").suspicion == (0.5 + MEETING_CONTRADICTION_LIFT_CAP)


# --- Chain/opt-in relevance: a spoken vent observation backs a voice --------


class TestVentObservationRelevance:
    def test_vent_backed_accusation_mints_a_voice(self) -> None:
        from meetings.schemas import AccusationClaim

        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-2",
                    observations=(_saw_vent(),),
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-5",
                            confidence=0.9,
                            reason="I watched them vent",
                        ),
                    ),
                ),
            )
        )

        voices = independent_voices(transcript, roster=_ROSTER)

        assert voices.get("p-5") == ("p-2",)

    def test_spawn_window_vent_observation_backs_nothing(self) -> None:
        from meetings.schemas import AccusationClaim

        transcript = MeetingTranscript(
            turns=(
                _turn(
                    turn_index=0,
                    speaker="p-2",
                    observations=(_saw_vent(tick=0),),
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-5",
                            confidence=0.9,
                            reason="I watched them vent",
                        ),
                    ),
                ),
            )
        )

        voices = independent_voices(transcript, roster=_ROSTER)

        assert voices.get("p-5") is None
