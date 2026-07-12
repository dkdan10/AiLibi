"""Tests for the Task 16.7 grounded-vouch corroboration feed.

The sighting channel is :mod:`meetings.transcript`'s ``vent_sighting``
grounding chokepoint with the polarity INVERTED: where a grounded
:class:`~meetings.schemas.SawVentObservation` mints the STRONG role-proving
``vent_sighting`` FLAG against its subject, a spoken
:class:`~meetings.schemas.SawPlayerObservation` that matches one of the
SPEAKER'S OWN typed :class:`~meetings.schemas.SightingRecord` rows (subject +
canonically intersecting room, tick within
:data:`~meetings.transcript.SIGHTING_GROUNDING_TICK_TOLERANCE`) is a GROUNDED
VOUCH -- :func:`~meetings.transcript.grounded_vouch_subjects` surfaces its
subject into the meeting's relevance-gated ``corroborated`` set (the existing
-0.05 exculpation channel priced by
:data:`agents.memory.beliefs.CORROBORATION_SUSPICION_DELTA`), NEVER a
contradiction flag and NEVER the dead trust field. Grounding a sighting proves
the speaker honestly reported what they saw, not that the subject is innocent,
so the earned move is exactly the small weak exculpation the corroboration
channel already prices. An ungrounded vouch stays ordinary testimony.

Impostor-collusion known property (the task contract demands it is recorded).
The anti-collusion FLOOR is pinned hard: two impostors vouching for each other
with FABRICATED sightings (no matching record) earn ZERO exculpation -- the
fold moves neither impostor's suspicion. But grounding CANNOT catch an impostor
who TRUTHFULLY vouches for its partner ("I really did see them in Medbay"): the
sighting is genuine, so the -0.05 is earned legitimately (:class:`TestTruthfulPartnerVouch`
pins exactly that as CORRECT behavior). This is deliberate, not a bug -- the
delta is small BY DESIGN, and the mutual-vouching PATTERN stays visible in the
transcript as material for Phase 17's collusion detectors. Grounding closes the
FABRICATION door, not the truthful-collusion one.

The mechanism ships INERT (:class:`TestLiveFeedInertness`): committed
transcripts already carry speaker-groundable sightings, so
:meth:`meetings.manager.MeetingManager.run` does not pass the participant record
mapping into :func:`meetings.manager.derive_belief_evidence` yet -- the live
feed graduates under the phase's byte-identity lever doctrine, a later task
connects the one call.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from agents.memory.beliefs import (
    CORROBORATION_SUSPICION_DELTA,
    BeliefState,
    apply_meeting_evidence_rules,
)
from meetings.manager import (
    MeetingParticipant,
    derive_belief_evidence,
    derive_reported_testimony,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    PlayerId,
    SawPlayerObservation,
    SightingRecord,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import (
    SIGHTING_GROUNDING_TICK_TOLERANCE,
    StatedPlacement,
    contradiction_lift_key,
    detect_contradictions,
    detect_corroborations,
    grounded_vouch_subjects,
    independent_voices,
    reconstruct_stated_paths,
)
from tests.meetings.test_manager import (
    _make_responder,
    _participant,
    _run_meeting,
)

# --- Builders --------------------------------------------------------------


def _saw(
    *,
    subject: str = "p-5",
    room: str = "MEDBAY",
    tick: int = 14,
    co_present: tuple[str, ...] = (),
) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player",
        tick=tick,
        subject=subject,
        room=room,
        co_present=co_present,
    )


def _record(
    *,
    subject: str = "p-5",
    room: str = "MEDBAY",
    tick: int = 14,
    co_present: tuple[str, ...] = (),
) -> SightingRecord:
    return SightingRecord(subject=subject, room=room, tick=tick, co_present=co_present)


def _whereabouts(*, tick: int = 7, room: str = "ADMIN") -> WhereaboutsClaim:
    return WhereaboutsClaim(type="whereabouts", tick=tick, room=room)


def _turn(
    *,
    turn_index: int,
    speaker: str,
    turn_kind: str = "opening",
    reply_to: str | None = None,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
    free_text: str | None = None,
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to=reply_to,
        observations=observations,
        claims=claims,
        free_text=(
            free_text if free_text is not None else f"turn {turn_index} from {speaker}"
        ),
    )


def _transcript(*turns: MeetingTurn) -> MeetingTranscript:
    return MeetingTranscript(turns=turns)


def _result(transcript: MeetingTranscript, *, voters: tuple[str, ...]) -> MeetingResult:
    # ``voters`` materialises one default-SKIP ballot per id, the meeting's
    # living roster the replay-side reductions read (Task 10.1 / 13.5.2).
    return MeetingResult(
        meeting_id="m-1",
        triggered_by="p-2",
        trigger_tick=100,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(
            VoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="skip",
            )
            for voter in voters
        ),
        contradictions=(),
        transcript=transcript,
    )


_ROSTER: frozenset[PlayerId] = frozenset({"p-1", "p-2", "p-3", "p-5", "p-7", "p-8"})

# The canonical grounded-vouch shape reused across the corroboration pins: the
# speaker p-2 publicly reports seeing p-5 in MEDBAY at tick 14, and p-2's OWN
# typed record confirms exactly that sighting.
_VOUCH_TRANSCRIPT = _transcript(
    _turn(turn_index=0, speaker="p-2", observations=(_saw(subject="p-5"),))
)
_MATCHING_RECORDS: Mapping[PlayerId, tuple[SightingRecord, ...]] = {
    "p-2": (_record(subject="p-5"),)
}


# --- A. Grounded feeds the corroboration channel ----------------------------


class TestGroundedFeedsCorroboration:
    def test_grounded_vouch_subjects_returns_the_subject(self) -> None:
        assert grounded_vouch_subjects(
            _VOUCH_TRANSCRIPT,
            sighting_records=_MATCHING_RECORDS,
            roster=_ROSTER,
        ) == frozenset({"p-5"})

    def test_derive_belief_evidence_corroborates_the_subject(self) -> None:
        evidence = derive_belief_evidence(
            _VOUCH_TRANSCRIPT,
            contradictions=(),
            roster=_ROSTER,
            sighting_records=_MATCHING_RECORDS,
        )

        assert "p-5" in evidence.corroborated

    def test_fold_lowers_suspicion_by_exactly_the_rule3_delta(self) -> None:
        # THE EXACT-DELTA FIXTURE: the grounded vouch travels the EXISTING
        # corroboration channel -- same set, same -0.05, same caps -- so a
        # seeded prior drops by exactly CORROBORATION_SUSPICION_DELTA and the
        # dead trust field never moves.
        evidence = derive_belief_evidence(
            _VOUCH_TRANSCRIPT,
            contradictions=(),
            roster=_ROSTER,
            sighting_records=_MATCHING_RECORDS,
        )
        beliefs = BeliefState()
        beliefs.seed_player("p-5", suspicion=0.55, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="p-1",
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
        )

        assert updated.view("p-5").suspicion == pytest.approx(
            0.55 - CORROBORATION_SUSPICION_DELTA
        )
        # Trust is UNTOUCHED by the fold -- the corroboration lands on
        # suspicion only, NEVER the dead trust field.
        assert updated.view("p-5").trust == 0.5

    def test_tick_within_tolerance_grounds(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(
                    _saw(subject="p-5", tick=14 + SIGHTING_GROUNDING_TICK_TOLERANCE),
                ),
            )
        )

        assert grounded_vouch_subjects(
            transcript,
            sighting_records={"p-2": (_record(subject="p-5", tick=14),)},
            roster=_ROSTER,
        ) == frozenset({"p-5"})

    def test_tick_beyond_tolerance_does_not_ground(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(
                    _saw(
                        subject="p-5",
                        tick=14 + SIGHTING_GROUNDING_TICK_TOLERANCE + 1,
                    ),
                ),
            )
        )

        assert (
            grounded_vouch_subjects(
                transcript,
                sighting_records={"p-2": (_record(subject="p-5", tick=14),)},
                roster=_ROSTER,
            )
            == frozenset()
        )

    def test_tolerance_window_is_symmetric(self) -> None:
        # The tolerance is an abs() window: a spoken tick BELOW the record's by
        # exactly the tolerance grounds, mirroring the above-tolerance case.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(
                    _saw(subject="p-5", tick=14 - SIGHTING_GROUNDING_TICK_TOLERANCE),
                ),
            )
        )

        assert grounded_vouch_subjects(
            transcript,
            sighting_records={"p-2": (_record(subject="p-5", tick=14),)},
            roster=_ROSTER,
        ) == frozenset({"p-5"})

    def test_first_relevant_tick_grounds(self) -> None:
        # tick 2 is the first tick past the spawn window (SPAWN_WINDOW_LAST_TICK
        # == 1): a vouch there is relevance-eligible and grounds against a
        # matching record, pinning the exclusion boundary from the inside.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=2),),
            )
        )

        assert grounded_vouch_subjects(
            transcript,
            sighting_records={"p-2": (_record(subject="p-5", room="MEDBAY", tick=2),)},
            roster=_ROSTER,
        ) == frozenset({"p-5"})

    def test_spawn_window_record_cannot_be_retimed_into_relevance(self) -> None:
        # Codex P2: the relevance gate reads the MATCHED RECORD, not the spoken
        # tick. A true spawn-window sighting (record tick 1) re-stated one tick
        # later (spoken tick 2, out of the spawn window) matches within tolerance
        # but must NOT ground -- the underlying record is evidentially empty, so
        # re-timing cannot smuggle it through the exculpation channel.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=2),),
            )
        )

        assert (
            grounded_vouch_subjects(
                transcript,
                sighting_records={
                    "p-2": (_record(subject="p-5", room="MEDBAY", tick=1),)
                },
                roster=_ROSTER,
            )
            == frozenset()
        )

    def test_compound_room_label_grounds_against_the_canonical_record(self) -> None:
        # canonical_rooms is the one room-normalisation point: a compound
        # spoken label whose member set contains the record's canonical room
        # still grounds (mirrors the vent flag's compound-room precedent).
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="LABS/MEDBAY"),),
            )
        )

        assert grounded_vouch_subjects(
            transcript,
            sighting_records={"p-2": (_record(subject="p-5", room="MEDBAY"),)},
            roster=_ROSTER,
        ) == frozenset({"p-5"})


# --- B. A grounded vouch is NEVER a contradiction flag ----------------------


class TestGroundedVouchIsNeverAFlag:
    def test_grounded_vouch_mints_no_flag(self) -> None:
        # detect_contradictions carries NO sighting-record channel by
        # construction (only vent_witness_records), so the typed records can
        # never reach the flag detector: the flag set is a pure function of the
        # transcript, IDENTICAL whether or not any record exists. The grounded
        # vouch lives entirely in the corroboration channel.
        flags = detect_contradictions(_VOUCH_TRANSCRIPT, roster=_ROSTER)

        assert flags == ()
        # Yet the very same transcript DID ground a vouch -- proving the vouch
        # feeds corroboration, never a flag, and introduces no new flag kind.
        assert grounded_vouch_subjects(
            _VOUCH_TRANSCRIPT,
            sighting_records=_MATCHING_RECORDS,
            roster=_ROSTER,
        ) == frozenset({"p-5"})


# --- C. An ungrounded vouch stays ordinary testimony ------------------------


class TestUngroundedVouchIsTestimony:
    def test_no_records_grounds_nothing(self) -> None:
        empty: Mapping[PlayerId, tuple[SightingRecord, ...]] = {"p-2": ()}

        assert (
            grounded_vouch_subjects(
                _VOUCH_TRANSCRIPT, sighting_records=empty, roster=_ROSTER
            )
            == frozenset()
        )

    def test_mismatched_record_grounds_nothing(self) -> None:
        mismatched: Mapping[PlayerId, tuple[SightingRecord, ...]] = {
            "p-2": (_record(subject="p-5", room="REACTOR"),)
        }

        assert (
            grounded_vouch_subjects(
                _VOUCH_TRANSCRIPT, sighting_records=mismatched, roster=_ROSTER
            )
            == frozenset()
        )

    def test_mismatched_record_leaves_corroborated_empty(self) -> None:
        mismatched: Mapping[PlayerId, tuple[SightingRecord, ...]] = {
            "p-2": (_record(subject="p-5", room="REACTOR"),)
        }
        evidence = derive_belief_evidence(
            _VOUCH_TRANSCRIPT,
            contradictions=(),
            roster=_ROSTER,
            sighting_records=mismatched,
        )

        assert "p-5" not in evidence.corroborated

    def test_ungrounded_sighting_still_records_as_reported_testimony(self) -> None:
        # The observation is accepted public speech: even with no grounding
        # record it is preserved as ordinary testimony, so
        # derive_reported_testimony still carries the saw_player statement
        # (voters may weigh it) -- only the hard corroboration channel is closed.
        result = _result(_VOUCH_TRANSCRIPT, voters=("p-1", "p-2", "p-3", "p-5"))

        statements = derive_reported_testimony(result)

        saw_player = [
            statement for statement in statements if statement.kind == "saw_player"
        ]
        assert len(saw_player) == 1
        assert saw_player[0].speaker == "p-2"
        assert saw_player[0].subject == "p-5"


# --- D. The anti-collusion floor (the pinned fixture) -----------------------


class TestAntiCollusionFloor:
    def _fabricated_transcript(self) -> MeetingTranscript:
        # Two impostors each publicly vouch for the other with a fabricated
        # sighting; their OWN records hold nothing that matches (wrong room and
        # wrong tick) -- the invented vouch the floor must refuse to price.
        return _transcript(
            _turn(
                turn_index=0,
                speaker="p-7",
                observations=(_saw(subject="p-8", room="MEDBAY", tick=14),),
            ),
            _turn(
                turn_index=1,
                speaker="p-8",
                observations=(_saw(subject="p-7", room="MEDBAY", tick=16),),
            ),
        )

    def _fabricated_records(self) -> Mapping[PlayerId, tuple[SightingRecord, ...]]:
        return {
            "p-7": (_record(subject="p-8", room="REACTOR", tick=2),),
            "p-8": (_record(subject="p-7", room="STORAGE", tick=3),),
        }

    def test_fabricated_mutual_vouch_grounds_nothing(self) -> None:
        assert (
            grounded_vouch_subjects(
                self._fabricated_transcript(),
                sighting_records=self._fabricated_records(),
                roster=_ROSTER,
            )
            == frozenset()
        )

    def test_fabricated_mutual_vouch_leaves_corroborated_empty(self) -> None:
        evidence = derive_belief_evidence(
            self._fabricated_transcript(),
            contradictions=(),
            roster=_ROSTER,
            sighting_records=self._fabricated_records(),
        )

        assert evidence.corroborated == ()

    def test_fabricated_mutual_vouch_moves_neither_impostor(self) -> None:
        # ZERO exculpation: fold the (empty) evidence and both impostors' belief
        # views stay byte-identical -- no fabricated -0.05 reaches either. Seeded
        # at the 0.5 prior so Rule-5 decay is a no-op and the ONLY thing that
        # could move the score is a (correctly absent) corroboration.
        evidence = derive_belief_evidence(
            self._fabricated_transcript(),
            contradictions=(),
            roster=_ROSTER,
            sighting_records=self._fabricated_records(),
        )
        beliefs = BeliefState()
        beliefs.seed_player("p-7", suspicion=0.5, trust=0.5)
        beliefs.seed_player("p-8", suspicion=0.5, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="p-1",
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
        )

        assert updated.view("p-7") == beliefs.view("p-7")
        assert updated.view("p-8") == beliefs.view("p-8")


# --- E. Truthful partner vouch (the documented known property) --------------


class TestTruthfulPartnerVouch:
    def test_truthful_partner_vouch_earns_the_legitimate_delta(self) -> None:
        # KNOWN PROPERTY (per the module docstring): grounding cannot catch an
        # impostor who TRUTHFULLY vouches for its partner. p-7's record GENUINELY
        # matches its spoken sighting of partner p-8, so p-8 IS corroborated and
        # earns exactly the -0.05. This is CORRECT behavior: the sighting is
        # real, the delta is small by design, and the mutual-vouching pattern
        # stays visible transcript material for Phase 17's detectors.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-7",
                observations=(_saw(subject="p-8", room="MEDBAY", tick=14),),
            )
        )
        records: Mapping[PlayerId, tuple[SightingRecord, ...]] = {
            "p-7": (_record(subject="p-8", room="MEDBAY", tick=14),)
        }

        assert grounded_vouch_subjects(
            transcript, sighting_records=records, roster=_ROSTER
        ) == frozenset({"p-8"})

        evidence = derive_belief_evidence(
            transcript,
            contradictions=(),
            roster=_ROSTER,
            sighting_records=records,
        )
        assert "p-8" in evidence.corroborated

        beliefs = BeliefState()
        beliefs.seed_player("p-8", suspicion=0.55, trust=0.5)
        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="p-1",
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
        )

        assert updated.view("p-8").suspicion == pytest.approx(
            0.55 - CORROBORATION_SUSPICION_DELTA
        )


# --- F. Grounding gates -----------------------------------------------------


class TestGroundingGates:
    def test_self_vouch_never_grounds(self) -> None:
        # A sighting whose subject IS the speaker grounds nothing even with a
        # matching record -- self-exculpation is closed at the source.
        transcript = _transcript(
            _turn(turn_index=0, speaker="p-2", observations=(_saw(subject="p-2"),))
        )

        assert (
            grounded_vouch_subjects(
                transcript,
                sighting_records={"p-2": (_record(subject="p-2"),)},
                roster=_ROSTER,
            )
            == frozenset()
        )

    @pytest.mark.parametrize("tick", [0, 1])
    def test_spawn_window_vouch_never_grounds(self, tick: int) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", tick=tick),),
            )
        )

        assert (
            grounded_vouch_subjects(
                transcript,
                sighting_records={"p-2": (_record(subject="p-5", tick=tick),)},
                roster=_ROSTER,
            )
            == frozenset()
        )

    def test_kill_scene_vouch_never_grounds(self) -> None:
        # A vouch whose spoken room is the opening turn's found_body room
        # places the subject AT the kill scene inside their own alibi window --
        # presence at the scene must never exonerate.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-1",
                observations=(
                    FoundBodyObservation(
                        type="found_body", tick=10, body_of="p-9", room="MEDBAY"
                    ),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
            ),
        )

        assert (
            grounded_vouch_subjects(
                transcript,
                sighting_records={"p-2": (_record(subject="p-5", room="MEDBAY"),)},
                roster=_ROSTER,
            )
            == frozenset()
        )

    def test_non_roster_subject_never_grounds(self) -> None:
        transcript = _transcript(
            _turn(turn_index=0, speaker="p-2", observations=(_saw(subject="p-99"),))
        )

        assert (
            grounded_vouch_subjects(
                transcript,
                sighting_records={"p-2": (_record(subject="p-99"),)},
                roster=_ROSTER,
            )
            == frozenset()
        )

    def test_non_spatial_room_never_grounds(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="VARIOUS"),),
            )
        )

        assert (
            grounded_vouch_subjects(
                transcript,
                sighting_records={"p-2": (_record(subject="p-5", room="VARIOUS"),)},
                roster=_ROSTER,
            )
            == frozenset()
        )

    def test_only_the_speakers_own_records_ground(self) -> None:
        # ANOTHER participant's matching record must not ground p-2's vouch:
        # the record channel is a self-channel, never pooled.
        assert (
            grounded_vouch_subjects(
                _VOUCH_TRANSCRIPT,
                sighting_records={"p-3": (_record(subject="p-5"),)},
                roster=_ROSTER,
            )
            == frozenset()
        )


# --- G. The whereabouts self-placement mechanism ----------------------------


class TestWhereaboutsClaimMechanism:
    def test_reconstruct_places_the_speaker(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=7, room="ADMIN"),),
            )
        )

        paths = reconstruct_stated_paths(transcript, roster=_ROSTER)

        assert (
            StatedPlacement(
                tick=7,
                rooms=frozenset({"ADMIN"}),
                speaker="p-3",
                # A whereabouts is an alibi-side account, so it carries the
                # :whereabouts: event-id segment (not :obs:) — Task 16.7 lift-key
                # dedup (Codex P2).
                event_id="turn:m-1:turn-0:whereabouts:0",
            )
            in paths["p-3"]
        )

    @pytest.mark.parametrize("tick", [0, 1])
    def test_spawn_window_whereabouts_still_places(self, tick: int) -> None:
        # Codex P2 (reconstruct places roll-call answers): a self-placement is
        # gated on the SPATIAL label only, NEVER the relevance gate -- a
        # spawn-window roll-call answer still accounts for the speaker, so it
        # must place them on the public record (out of Task 16.8's absent set).
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=tick, room="ADMIN"),),
            )
        )

        paths = reconstruct_stated_paths(transcript, roster=_ROSTER)
        assert "p-3" in paths
        assert paths["p-3"][0].tick == tick

    def test_body_room_whereabouts_still_places(self) -> None:
        # The kill-scene prong is likewise skipped for self-placement: a player
        # who answers roll-call IN the body room has still accounted for
        # themselves (presence-at-scene is an EXCULPATION rule, not an
        # existence-on-record rule), so they are NOT absent.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-1",
                observations=(
                    FoundBodyObservation(
                        type="found_body", tick=10, body_of="p-9", room="MEDBAY"
                    ),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-3",
                observations=(_whereabouts(tick=11, room="MEDBAY"),),
            ),
        )

        assert "p-3" in reconstruct_stated_paths(transcript, roster=_ROSTER)

    def test_non_spatial_whereabouts_places_nothing(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=7, room="VARIOUS"),),
            )
        )

        assert "p-3" not in reconstruct_stated_paths(transcript, roster=_ROSTER)

    def test_whereabouts_contradicted_by_sighting_raises_alibi_vs_sighting(
        self,
    ) -> None:
        # p-3 answers roll-call in ADMIN@7 while p-1 places them in REACTOR@7:
        # the degenerate single-tick self-alibi is prosecuted by the EXISTING
        # alibi_vs_sighting path (no new flag kind, subject = p-3). Assert kind
        # and subjects only -- the endpoint-tick classification may weak-mark it.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=7, room="ADMIN"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-1",
                turn_kind="opt_in",
                observations=(_saw(subject="p-3", room="REACTOR", tick=7),),
            ),
        )

        flags = detect_contradictions(transcript, roster=_ROSTER)

        sighting_flags = [flag for flag in flags if flag.kind == "alibi_vs_sighting"]
        assert len(sighting_flags) == 1
        assert sighting_flags[0].subjects == ("p-3",)

    def test_whereabouts_conflicting_own_alibi_raises_alibi_conflict(self) -> None:
        # A whereabouts (ADMIN@7) contradicting the speaker's OWN AlibiClaim
        # (REACTOR over [5, 9]) over an overlapping window is the degenerate
        # self-alibi indexing at work: the EXISTING alibi_conflict path fires
        # against p-3, no new flag kind.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=7, room="ADMIN"),),
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="p-3",
                        from_tick=5,
                        to_tick=9,
                        room="REACTOR",
                    ),
                ),
            )
        )

        flags = detect_contradictions(transcript, roster=_ROSTER)

        conflict_flags = [flag for flag in flags if flag.kind == "alibi_conflict"]
        assert len(conflict_flags) == 1
        assert conflict_flags[0].subjects == ("p-3",)

    def test_one_whereabouts_folds_to_one_lift_key_across_sightings(self) -> None:
        # Codex P2: one roll-call answer contradicted by SEVERAL sightings must
        # fold to a SINGLE contradiction lift (the per-account dedup a real alibi
        # gets), never stack N deltas up to the meeting cap. The :whereabouts:
        # account segment gives contradiction_lift_key a shared key for every
        # (whereabouts, sighting) pair.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=7, room="ADMIN"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-1",
                turn_kind="opt_in",
                observations=(_saw(subject="p-3", room="REACTOR", tick=7),),
            ),
            _turn(
                turn_index=2,
                speaker="p-5",
                turn_kind="opt_in",
                observations=(_saw(subject="p-3", room="STORAGE", tick=7),),
            ),
        )

        flags = detect_contradictions(transcript, roster=_ROSTER)
        sighting_flags = [
            flag
            for flag in flags
            if flag.kind == "alibi_vs_sighting" and flag.subjects == ("p-3",)
        ]
        # One flag per contradicting sighting...
        assert len(sighting_flags) == 2
        # ...but ALL share one lift key (the whereabouts account), so belief
        # Rule 2's (subject, key) dedup folds them to a single delta.
        keys = {contradiction_lift_key(flag) for flag in sighting_flags}
        assert len(keys) == 1
        assert ":whereabouts:" in keys.pop()


# --- H. The live feed stays inert until graduation --------------------------


class TestLiveFeedInertness:
    def test_run_never_consumes_participant_sighting_records(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The doctrine decision (Task 16.7): committed transcripts already carry
        # speaker-groundable sightings, so passing the live per-speaker mapping
        # into derive_belief_evidence would move committed ballot-prompt bytes,
        # and the phase's lever doctrine requires every behavioral change to be
        # byte-identical at rest -- the graduating task connects run() to the
        # derivation. Pin it: replace the derivation's grounded_vouch_subjects
        # with a raiser and prove a REAL meeting (opener carrying records that
        # WOULD ground a spoken sighting) never calls it.
        def _raiser(
            *args: object, **kwargs: object
        ) -> frozenset[PlayerId]:  # pragma: no cover - must never run
            raise AssertionError("live feed must stay inert until graduation")

        monkeypatch.setattr("meetings.manager.grounded_vouch_subjects", _raiser)

        opener = MeetingParticipant(
            agent_id="p-1",
            role="CREWMATE",
            rendered_memory="## Your role: CREWMATE\np-1 memory",
            sighting_records=(_record(subject="p-2", room="MEDBAY", tick=14),),
        )
        participants = (
            opener,
            _participant("p-2"),
            _participant("p-3"),
            _participant("p-4"),
        )

        result, _ = _run_meeting(
            _make_responder(
                observations={"p-1": (_saw(subject="p-2", room="MEDBAY", tick=14),)},
            ),
            participants=participants,
        )

        # The meeting resolved to completion; the raiser was never reached.
        assert isinstance(result, MeetingResult)
        assert result.outcome in ("EJECTED", "SKIPPED")
        assert len(result.ballots) == 4


# --- I. Whereabouts is prosecutable but never an EXCULPATION surface ---------


class TestWhereaboutsIsNotACorroborationSurface:
    """Codex P1: a roll-call self-placement must not become an ungrounded
    corroboration a colluder can confirm. It feeds the contradiction detectors
    (prosecution) but is kept out of detect_corroborations (exculpation)."""

    def _rollcall_plus_confirming_sighting(self) -> MeetingTranscript:
        # p-3 answers roll-call "MEDBAY @ 7"; p-8 (a would-be colluder) confirms
        # it with a sighting placing p-3 in MEDBAY @ 7. NEITHER holds a grounding
        # SightingRecord -- both are pure speech.
        return _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=7, room="MEDBAY"),),
            ),
            _turn(
                turn_index=1,
                speaker="p-8",
                turn_kind="opt_in",
                observations=(_saw(subject="p-3", room="MEDBAY", tick=7),),
            ),
        )

    def test_whereabouts_is_not_detected_as_a_corroboration(self) -> None:
        corroborations = detect_corroborations(
            self._rollcall_plus_confirming_sighting(), roster=_ROSTER
        )

        assert corroborations == ()

    def test_confirmed_rollcall_answer_stays_out_of_corroborated(self) -> None:
        # The whole point: derive_belief_evidence must NOT put p-3 in the
        # corroborated set off a whereabouts + a confederate's ungrounded
        # sighting -- exculpation requires the grounded-vouch channel, which
        # checks the speaker's OWN typed record.
        evidence = derive_belief_evidence(
            self._rollcall_plus_confirming_sighting(),
            contradictions=(),
            roster=_ROSTER,
        )

        assert "p-3" not in evidence.corroborated

    def test_a_real_alibi_still_corroborates(self) -> None:
        # Guard the fix's blast radius: a genuine AlibiClaim (not a whereabouts)
        # confirmed by an independent sighting is STILL a detector-derived
        # corroboration -- only the whereabouts kind is excluded.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="p-3",
                        from_tick=6,
                        to_tick=8,
                        room="MEDBAY",
                    ),
                ),
            ),
            _turn(
                turn_index=1,
                speaker="p-8",
                turn_kind="opt_in",
                observations=(_saw(subject="p-3", room="MEDBAY", tick=7),),
            ),
        )

        corroborations = detect_corroborations(transcript, roster=_ROSTER)

        assert any(c.subject == "p-3" for c in corroborations)


class TestWhereaboutsDoesNotBackAccusations:
    """Codex P2: a self-placement carries no evidence about the accused, so it
    must not promote a bare accusation into an observation-backed independent
    voice (which would neuter the testimony-spread gate once roll-call is
    universal)."""

    def test_accusation_backed_only_by_whereabouts_carries_no_voice(self) -> None:
        # p-2 accuses p-5 and answers roll-call, but states NO observation about
        # p-5. The whereabouts must not back the accusation, so p-5 gets no
        # independent voice.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_whereabouts(tick=7, room="ADMIN"),),
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-5",
                        confidence=0.8,
                        reason="a hunch",
                    ),
                ),
            )
        )

        assert "p-5" not in independent_voices(transcript, roster=_ROSTER)

    def test_accusation_backed_by_a_real_sighting_still_carries_a_voice(
        self,
    ) -> None:
        # Guard the blast radius: a genuine first-hand sighting of the accused
        # STILL backs the voice -- only the whereabouts self-placement is inert.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="ADMIN", tick=7),),
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-5",
                        confidence=0.8,
                        reason="saw them near the body",
                    ),
                ),
            )
        )

        assert "p-5" in independent_voices(transcript, roster=_ROSTER)
