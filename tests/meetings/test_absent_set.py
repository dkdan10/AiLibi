"""Tests for the Task 16.8 absent-set derivation.

The absent set is the complement of
:func:`~meetings.transcript.reconstruct_stated_paths` over a meeting's LIVING
roster: :func:`~meetings.transcript.absent_players` returns every roster player
whom NOBODY'S public testimony placed anywhere this meeting -- neither a spoken
:class:`~meetings.schemas.SawPlayerObservation` (as ``subject`` or in
``co_present``) nor the player's own Task 16.7
:class:`~meetings.schemas.WhereaboutsClaim` roll-call answer. Answering
roll-call therefore REMOVES a player from the set; staying publicly unseen keeps
them in it -- the set the Task 16.8 absence prior prices.

The whole suite pins the DoD firewall (tasks/phase-16.md Task 16.8 DoD bullet
1): the absent set derives ONLY from PUBLIC testimony (stated paths + whereabouts
claims). No engine state, no perception packet, and -- the named negative --
no private memory of others feeds it. A privately-witnessed sighting that nobody
SPOKE (a typed :class:`~meetings.schemas.SightingRecord` on the 16.7 private
channel) leaves its subject absent by construction, because
:func:`~meetings.transcript.absent_players` never reads that channel.

The gates the reconstruction applies to SIGHTINGS carry through: a spawn-window
or kill-scene sighting reconstructs no position (the §6.3 relevance gate,
:func:`~meetings.transcript.is_relevant_sighting`), so it removes nobody; but a
WHEREABOUTS self-placement needs only a spatial label -- it deliberately
BYPASSES that gate, because whether a self-placement EXISTS on the record is a
different question from whether it EXCULPATES (the Task 16.7 asymmetry documented
on :func:`~meetings.transcript.reconstruct_stated_paths`).

Task 17.5 adds the INERT vent-placement widening behind
``include_vent_sightings`` (default OFF -- nothing in production passes it;
whether it ships is the 17.7 gate's ruling): a spoken
:class:`~meetings.schemas.SawVentObservation` GROUNDED against the SPEAKER'S OWN
:class:`~meetings.schemas.VentWitnessRecord` channel (the 15.4 chokepoint)
removes its subject from the absent set, while a spoken but UNGROUNDED vent
claim never places anybody. Sections 12+ pin those semantics and the
default-OFF byte-identity.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from meetings.manager import derive_belief_evidence
from meetings.schemas import (
    AccusationClaim,
    Claim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    PlayerId,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    VentWitnessRecord,
    WhereaboutsClaim,
)
from meetings.transcript import VENT_GROUNDING_TICK_TOLERANCE, absent_players

# --- Builders (cloned from tests/meetings/test_vouch_grounding.py) ----------


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


def _found_body(
    *, body_of: str = "p-9", room: str = "MEDBAY", tick: int = 10
) -> FoundBodyObservation:
    return FoundBodyObservation(
        type="found_body", tick=tick, body_of=body_of, room=room
    )


def _whereabouts(*, tick: int = 7, room: str = "ADMIN") -> WhereaboutsClaim:
    return WhereaboutsClaim(type="whereabouts", tick=tick, room=room)


# Task 17.5 builders (cloned from tests/meetings/test_transcript_vent_flag.py).


def _saw_vent(
    *, tick: int = 14, subject: str = "p-5", room: str = "STORAGE"
) -> SawVentObservation:
    return SawVentObservation(type="saw_vent", tick=tick, subject=subject, room=room)


def _vent_record(
    *, tick: int = 14, subject: str = "p-5", room: str = "STORAGE"
) -> VentWitnessRecord:
    return VentWitnessRecord(subject=subject, room=room, tick=tick)


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


_ROSTER: frozenset[PlayerId] = frozenset({"p-1", "p-2", "p-3", "p-5", "p-7", "p-8"})


# --- 1. Empty transcript -> everyone absent, sorted --------------------------


class TestEmptyTranscriptAbsentsEveryone:
    """With no public testimony NOBODY is placed, so the absent set is the whole
    living roster -- returned as a SORTED tuple (the replay-deterministic fold
    order every consumer in :mod:`meetings.transcript` promises)."""

    def test_empty_transcript_absents_the_whole_roster(self) -> None:
        assert absent_players(_transcript(), roster=_ROSTER) == tuple(sorted(_ROSTER))

    def test_result_is_sorted(self) -> None:
        result = absent_players(_transcript(), roster=_ROSTER)
        assert list(result) == sorted(result)


# --- 2. A spoken sighting removes subject + every co-present ------------------


class TestSightingRemovesSubjectAndCoPresent:
    """One ``saw_player`` observation is a public placement of its ``subject``
    AND every ``co_present`` player (a co-presence is as much a stated placement
    as the subject's -- Task 13.2), so all of them leave the absent set. Players
    NOBODY placed stay in it: the set prices being publicly unseen, not being
    unspoken-of."""

    def test_subject_and_co_present_leave_unplaced_remain(self) -> None:
        # p-2 states seeing p-5 in ADMIN@14 alongside p-3: p-5 and p-3 are placed
        # and drop out; the speaker p-2 (talking is not placement, pinned below)
        # and the entirely-unnamed p-1/p-7/p-8 remain.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="ADMIN", co_present=("p-3",)),),
            )
        )

        absent = absent_players(transcript, roster=_ROSTER)

        assert "p-5" not in absent
        assert "p-3" not in absent
        assert absent == ("p-1", "p-2", "p-7", "p-8")


# --- 3. A whereabouts answer removes its SPEAKER (bypassing the gate) ---------


class TestWhereaboutsRemovesSpeaker:
    """A Task 16.7 :class:`WhereaboutsClaim` places its SPEAKER on the record and
    removes them from the absent set. It is gated on the SPATIAL label ONLY,
    deliberately BYPASSING the §6.3 relevance gate that drops spawn-window and
    kill-scene SIGHTINGS: whether a self-placement EXISTS is a different question
    from whether it EXCULPATES, and a player who answered roll-call -- even
    trivially at spawn, or in the body room -- has accounted for themselves.

    The CONTRAST pins the asymmetry from the other side: a SIGHTING at a
    spawn-window tick reconstructs no position (the gate applies to sightings),
    so it removes nobody."""

    @pytest.mark.parametrize("tick", [0, 1])
    def test_spawn_window_whereabouts_removes_speaker(self, tick: int) -> None:
        # SPAWN_WINDOW_LAST_TICK == 1: a tick-0/1 roll-call answer still accounts
        # for the speaker (the gate is skipped for self-placement), so p-3 is
        # removed even though the identical tick would gate a sighting.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=tick, room="ADMIN"),),
            )
        )

        assert "p-3" not in absent_players(transcript, roster=_ROSTER)

    def test_body_room_whereabouts_removes_speaker(self) -> None:
        # The kill-scene prong is likewise skipped: p-3 answers roll-call IN the
        # meeting's body room (MEDBAY), and is STILL placed even under
        # trigger_kind="report", where that same room gates a sighting (Task 5).
        transcript = _transcript(
            _turn(turn_index=0, speaker="p-1", observations=(_found_body(),)),
            _turn(
                turn_index=1,
                speaker="p-3",
                observations=(_whereabouts(tick=11, room="MEDBAY"),),
            ),
        )

        assert "p-3" not in absent_players(
            transcript, roster=_ROSTER, trigger_kind="report"
        )

    @pytest.mark.parametrize("tick", [0, 1])
    def test_contrast_spawn_window_sighting_does_not_remove_subject(
        self, tick: int
    ) -> None:
        # The other half of the asymmetry: a SIGHTING at a spawn-window tick is
        # evidentially empty (everyone co-spawns in CAFETERIA), so the relevance
        # gate drops it -- it reconstructs no position and p-5 stays absent.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=tick),),
            )
        )

        assert "p-5" in absent_players(transcript, roster=_ROSTER)


# --- 4. A non-spatial whereabouts label removes nobody ------------------------


class TestNonSpatialWhereaboutsRemovesNobody:
    """``canonical_rooms`` is the single room-normalisation point: a non-spatial
    label ("VARIOUS") canonicalises to the empty set, which locates nobody. Even
    a whereabouts -- which skips the RELEVANCE gate -- still requires a SPATIAL
    label, so a "VARIOUS" roll-call answer places nothing and its speaker stays
    absent."""

    def test_various_whereabouts_leaves_speaker_absent(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-3",
                observations=(_whereabouts(tick=7, room="VARIOUS"),),
            )
        )

        assert "p-3" in absent_players(transcript, roster=_ROSTER)


# --- 5. Kill-scene sighting asymmetry (report excludes, emergency drops) ------


class TestKillSceneSightingAsymmetry:
    """A sighting placing a player at the meeting's triggering-body room is gated
    by the §6.3 kill-scene prong under a REPORT meeting -- presence at the scene
    must never exculpate, so it reconstructs no position and the player stays
    absent. An EMERGENCY meeting has no body by design (Task 10.11), so
    :func:`triggering_body_rooms` returns empty, the prong drops, and the SAME
    sighting now removes the player. The absent set inherits the reconstruction's
    trigger-kind sensitivity verbatim."""

    def _body_room_sighting(self) -> MeetingTranscript:
        # Opening body report in MEDBAY; p-2 then places p-5 in MEDBAY@14 -- the
        # kill scene, inside p-5's own would-be alibi window.
        return _transcript(
            _turn(turn_index=0, speaker="p-1", observations=(_found_body(),)),
            _turn(
                turn_index=1,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
            ),
        )

    def test_report_meeting_keeps_kill_scene_subject_absent(self) -> None:
        # Kill-scene exclusion active: the MEDBAY sighting intersects the body
        # room, so it removes nobody and p-5 remains absent.
        assert "p-5" in absent_players(
            self._body_room_sighting(), roster=_ROSTER, trigger_kind="report"
        )

    def test_emergency_meeting_removes_the_same_subject(self) -> None:
        # No kill scene under EMERGENCY: the body room drops out, the sighting is
        # relevant (tick 14 > spawn window), so it places p-5 -- who is no longer
        # absent. Same transcript, opposite outcome purely from trigger_kind.
        assert "p-5" not in absent_players(
            self._body_room_sighting(), roster=_ROSTER, trigger_kind="emergency"
        )

    def test_none_trigger_kind_reads_the_body_as_a_kill_scene(self) -> None:
        # The PR #264 review hazard, pinned: ``trigger_kind=None`` keeps the
        # pre-10.11 behaviour and reads the opening body off the transcript --
        # so for an EMERGENCY meeting whose opening carries a model-FABRICATED
        # ``found_body``, a None-kind derivation gates away the real sighting
        # and reads p-5 as spuriously absent, exactly like a report meeting.
        # This is why the manager's pre-vote region re-derives the absent set
        # with the ENGINE trigger kind (never None) before the fold consumes
        # it: the Task 10.11 emergency gate must hold on the absence channel.
        assert "p-5" in absent_players(
            self._body_room_sighting(), roster=_ROSTER, trigger_kind=None
        )
        assert absent_players(
            self._body_room_sighting(), roster=_ROSTER, trigger_kind=None
        ) == absent_players(
            self._body_room_sighting(), roster=_ROSTER, trigger_kind="report"
        )


# --- 6. Dead players excluded by construction (living-only roster) -----------


class TestDeadPlayersExcludedByConstruction:
    """``roster`` is REQUIRED and must be the meeting's LIVING participants: the
    complement of a placement mapping is only meaningful against an explicit
    universe. A dead player named in testimony is both filtered out of the
    reconstruction (roster-gated) AND absent from the roster, so it can never
    surface in the absent set -- the result is ALWAYS a subset of the roster."""

    def test_dead_subject_never_appears_and_result_subsets_roster(self) -> None:
        # p-9 is dead (absent from the living roster) yet named as a sighting
        # subject and co-presence; it must not surface, and every element of the
        # result must be a living roster member.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-9", room="ADMIN", co_present=("p-9",)),),
            )
        )

        absent = absent_players(transcript, roster=_ROSTER)

        assert "p-9" not in absent
        assert set(absent) <= _ROSTER


# --- 7. A hallucinated (non-roster) id neither appears nor removes ------------


class TestHallucinatedIdIsInert:
    """A sighting naming a non-roster (hallucinated) id is roster-filtered out of
    the reconstruction, mirroring :func:`detect_contradictions`: the phantom
    subject neither appears in the absent set nor removes any real player. The
    absent set stays the full living roster -- no real placement was made."""

    def test_phantom_subject_leaves_roster_absent(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-99", room="MEDBAY", tick=14),),
            )
        )

        absent = absent_players(transcript, roster=_ROSTER)

        assert "p-99" not in absent
        # No real player was placed by the phantom sighting, so all remain.
        assert absent == tuple(sorted(_ROSTER))


# --- 8. Speaking is not placement --------------------------------------------


class TestSpeakingIsNotPlacement:
    """Only a spatial ``saw_player`` or a spatial ``whereabouts`` places a
    player. A turn whose speaker merely ACCUSES or emits free text makes no
    placement, so the speaker stays absent -- talking is not being seen. (The
    accusation names its target but does not place them either.)"""

    def test_accuser_and_free_text_speaker_stay_absent(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                free_text="I think p-5 is acting suspicious",
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

        absent = absent_players(transcript, roster=_ROSTER)

        # The speaker who only talked is absent; so is the merely-accused target.
        assert "p-2" in absent
        assert "p-5" in absent
        assert absent == tuple(sorted(_ROSTER))


# --- 9. Determinism -----------------------------------------------------------


class TestDeterminism:
    """The fold is replay-deterministic: two calls on the same transcript return
    byte-identical tuples (the DESIGN.md §0 rule 1 replay invariant the absence
    prior inherits)."""

    def test_two_calls_return_identical_tuples(self) -> None:
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="ADMIN", co_present=("p-3",)),),
            ),
            _turn(
                turn_index=1,
                speaker="p-7",
                observations=(_whereabouts(tick=8, room="STORAGE"),),
            ),
        )

        first = absent_players(transcript, roster=_ROSTER)
        second = absent_players(transcript, roster=_ROSTER)

        assert first == second


# --- 10. The FIREWALL NEGATIVE (the DoD's named case) ------------------------


class TestFirewallNegativePrivateMemoryNeverFeedsTheSet:
    """The Task 16.8 DoD firewall: the absent set derives ONLY from PUBLIC
    testimony. A private typed :class:`SightingRecord` -- the 16.7 self-channel
    used by :func:`derive_belief_evidence` for GROUNDED VOUCH corroboration --
    naming a player who was NEVER SPOKEN about must leave that player IN
    ``evidence.absent``. :func:`absent_players` never reads that channel, so
    private memory of OTHERS cannot account for them; only a public sighting or
    the player's own roll-call answer can."""

    def test_private_record_of_unspoken_player_stays_absent(self) -> None:
        # p-2 speaks only free text (placing nobody, not even itself), yet holds a
        # private record of seeing p-5 in MEDBAY@14. That record grounds no spoken
        # vouch (there is no matching SawPlayerObservation), and -- the firewall --
        # it never touches the absent set: p-5 stays absent.
        transcript = _transcript(
            _turn(turn_index=0, speaker="p-2", free_text="nothing to add")
        )
        records: Mapping[PlayerId, tuple[SightingRecord, ...]] = {
            "p-2": (_record(subject="p-5", room="MEDBAY", tick=14),)
        }

        evidence = derive_belief_evidence(
            transcript,
            contradictions=(),
            roster=_ROSTER,
            sighting_records=records,
        )

        assert "p-5" in evidence.absent
        # The private channel had ZERO effect: the evidence's absent set is
        # byte-identical to the pure public derivation.
        assert evidence.absent == absent_players(transcript, roster=_ROSTER)
        assert evidence.absent == tuple(sorted(_ROSTER))


# --- 11. The evidence-derivation pin (same set, both entry points) -----------


class TestEvidenceDerivationMatchesHelper:
    """The absent set rides the SAME derivation inside
    :func:`derive_belief_evidence` (same roster, same trigger_kind) as the
    standalone helper, so the two agree for a mixed fixture -- the guarantee the
    replay path relies on to re-derive ``evidence.absent`` bit-identically from
    the public record."""

    def _mixed(self) -> MeetingTranscript:
        # A report meeting (body in MEDBAY) mixing every placement shape:
        #   * p-2 states seeing p-5 in ADMIN@14 with p-3 co-present -> p-5, p-3 in
        #   * p-7 answers roll-call in STORAGE@8 -> p-7 in
        # leaving p-1 (only reported the body), p-2 (spoke, unplaced), and the
        # never-named p-8 absent.
        return _transcript(
            _turn(turn_index=0, speaker="p-1", observations=(_found_body(),)),
            _turn(
                turn_index=1,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="ADMIN", co_present=("p-3",)),),
            ),
            _turn(
                turn_index=2,
                speaker="p-7",
                observations=(_whereabouts(tick=8, room="STORAGE"),),
            ),
        )

    def test_derive_belief_evidence_absent_matches_absent_players(self) -> None:
        transcript = self._mixed()

        evidence = derive_belief_evidence(
            transcript,
            contradictions=(),
            roster=_ROSTER,
            trigger_kind="report",
        )

        expected = absent_players(transcript, roster=_ROSTER, trigger_kind="report")
        assert evidence.absent == expected
        assert evidence.absent == ("p-1", "p-2", "p-8")


# --- 12. Task 17.5: grounded vent sightings place (flag ON) -------------------


def _vent_transcript(
    observation: SawVentObservation | None = None,
) -> MeetingTranscript:
    # One turn: p-2 speaks a vent sighting naming p-5 (STORAGE@14 by default).
    spoken = observation if observation is not None else _saw_vent()
    return _transcript(_turn(turn_index=0, speaker="p-2", observations=(spoken,)))


class TestGroundedVentSightingPlaces:
    """The Task 17.5 widening, flag ON: a spoken vent sighting GROUNDED against
    the SPEAKER'S OWN :class:`VentWitnessRecord` channel (the 15.4 chokepoint:
    same subject, canonically intersecting rooms, tick within
    :data:`~meetings.transcript.VENT_GROUNDING_TICK_TOLERANCE`) places its
    subject -- a witnessed vent accounts for the subject on the public record,
    so they leave the absent set. Grounding is the ONLY gate (the 16.7
    whereabouts asymmetry applied to vents): the §6.3 relevance prongs never
    apply, and the widening reads the transcript + the typed channel only --
    :func:`~meetings.transcript.reconstruct_stated_paths` never learns vents."""

    def test_grounded_vent_sighting_removes_its_subject(self) -> None:
        records = {"p-2": (_vent_record(),)}

        widened = absent_players(
            _vent_transcript(),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )

        assert "p-5" not in widened
        # Only the vent-sighted subject is re-placed; everyone else -- the
        # speaker included (talking is not being seen) -- stays absent.
        assert widened == ("p-1", "p-2", "p-3", "p-7", "p-8")

    def test_without_the_flag_the_same_subject_stays_absent(self) -> None:
        # The contrast pin: the identical transcript WITHOUT the widening reads
        # p-5 as absent -- the double-count population the 17.7 gate prices.
        assert "p-5" in absent_players(_vent_transcript(), roster=_ROSTER)

    def test_tick_within_tolerance_grounds_and_beyond_does_not(self) -> None:
        # The chokepoint's exact tick window, reused verbatim: a spoken tick
        # VENT_GROUNDING_TICK_TOLERANCE away still grounds; one tick further
        # is an ungrounded claim and places nobody.
        records = {"p-2": (_vent_record(tick=14),)}
        at_edge = _vent_transcript(_saw_vent(tick=14 + VENT_GROUNDING_TICK_TOLERANCE))
        beyond = _vent_transcript(_saw_vent(tick=15 + VENT_GROUNDING_TICK_TOLERANCE))

        assert "p-5" not in absent_players(
            at_edge,
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )
        assert "p-5" in absent_players(
            beyond,
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )

    def test_kill_scene_vent_sighting_still_places_under_report(self) -> None:
        # Grounding is the ONLY gate: a grounded vent at the meeting's body room
        # (MEDBAY -- the kill scene, which relevance-gates a SIGHTING under a
        # report meeting) still places its subject. Whether a grounded vent
        # account EXISTS is a different question from whether it exculpates.
        transcript = _transcript(
            _turn(turn_index=0, speaker="p-1", observations=(_found_body(),)),
            _turn(
                turn_index=1,
                speaker="p-2",
                observations=(_saw_vent(subject="p-5", room="MEDBAY", tick=14),),
            ),
        )
        records = {"p-2": (_vent_record(subject="p-5", room="MEDBAY", tick=14),)}

        assert "p-5" not in absent_players(
            transcript,
            roster=_ROSTER,
            trigger_kind="report",
            include_vent_sightings=True,
            vent_witness_records=records,
        )


# --- 13. Task 17.5: ungrounded vent claims never place ------------------------


class TestUngroundedVentClaimPlacesNobody:
    """Speech alone never re-places a player: a spoken vent claim with NO
    matching record in the SPEAKER'S OWN channel -- no records at all, a
    mismatched subject/room, or another player's records -- grounds nothing,
    so its subject stays absent even with the widening ON. The anti-collusion
    floor the 15.4 chokepoint draws, inherited verbatim."""

    def test_no_records_at_all_places_nobody(self) -> None:
        widened = absent_players(
            _vent_transcript(),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records={},
        )

        assert "p-5" in widened
        assert widened == tuple(sorted(_ROSTER))

    def test_none_records_ground_nothing(self) -> None:
        # ``vent_witness_records=None`` (the legacy-caller shape the 15.4
        # detector documents) grounds nothing even with the flag ON.
        widened = absent_players(
            _vent_transcript(),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=None,
        )

        assert widened == tuple(sorted(_ROSTER))

    def test_mismatched_subject_or_room_places_nobody(self) -> None:
        # A record naming a DIFFERENT subject, and one in a disjoint room,
        # both fail the chokepoint match -- the spoken claim stays testimony.
        records = {
            "p-2": (
                _vent_record(subject="p-3"),
                _vent_record(room="ADMIN"),
            )
        }

        assert "p-5" in absent_players(
            _vent_transcript(),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )

    def test_another_speakers_record_never_grounds(self) -> None:
        # The channel is the SPEAKER'S OWN: p-7 holding a perfectly matching
        # record does not ground p-2's spoken claim (no cross-speaker vouching
        # into hard placement -- the collusion shape the chokepoint refuses).
        records = {"p-7": (_vent_record(),)}

        assert "p-5" in absent_players(
            _vent_transcript(),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )

    def test_non_roster_vent_subject_is_inert(self) -> None:
        # A grounded vent naming a non-roster id (dead / hallucinated) mirrors
        # the flag detector's roster filter: it neither surfaces nor removes.
        records = {"p-2": (_vent_record(subject="p-99"),)}

        widened = absent_players(
            _vent_transcript(_saw_vent(subject="p-99")),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )

        assert "p-99" not in widened
        assert widened == tuple(sorted(_ROSTER))


# --- 14. Task 17.5: already-placed subjects and default-OFF byte-identity -----


class TestVentWideningIdempotenceAndByteIdentity:
    """A grounded vent sighting of an ALREADY-PLACED subject changes nothing
    (the widening only ever shrinks the absent set, and removal is idempotent),
    and the flag OFF -- the default and the ONLY production state -- is
    byte-identical to the pre-17.5 derivation no matter what records ride
    alongside."""

    def test_grounded_vent_on_already_placed_subject_changes_nothing(self) -> None:
        # p-5 is already placed by a spoken sighting (ADMIN@14); a grounded vent
        # naming p-5 too changes no byte of the result.
        transcript = _transcript(
            _turn(
                turn_index=0,
                speaker="p-2",
                observations=(
                    _saw(subject="p-5", room="ADMIN", tick=14),
                    _saw_vent(subject="p-5", room="STORAGE", tick=20),
                ),
            )
        )
        records = {"p-2": (_vent_record(subject="p-5", room="STORAGE", tick=20),)}

        widened = absent_players(
            transcript,
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )

        assert widened == absent_players(transcript, roster=_ROSTER)
        assert widened == ("p-1", "p-2", "p-3", "p-7", "p-8")

    def test_flag_off_is_byte_identical_even_with_records_supplied(self) -> None:
        # Default-OFF byte-identity: the flag unset (and explicitly False) with
        # a groundable record supplied returns the identical tuple the bare
        # derivation returns -- records are never even consulted.
        records = {"p-2": (_vent_record(),)}
        transcript = _vent_transcript()

        bare = absent_players(transcript, roster=_ROSTER)
        defaulted = absent_players(
            transcript, roster=_ROSTER, vent_witness_records=records
        )
        explicit_off = absent_players(
            transcript,
            roster=_ROSTER,
            include_vent_sightings=False,
            vent_witness_records=records,
        )

        assert bare == defaulted == explicit_off
        assert "p-5" in bare

    def test_widened_derivation_is_deterministic(self) -> None:
        # The widening inherits the fold's replay determinism: two widened calls
        # on the same transcript + records return byte-identical tuples.
        records = {"p-2": (_vent_record(),)}

        first = absent_players(
            _vent_transcript(),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )
        second = absent_players(
            _vent_transcript(),
            roster=_ROSTER,
            include_vent_sightings=True,
            vent_witness_records=records,
        )

        assert first == second
