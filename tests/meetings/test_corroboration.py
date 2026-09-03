"""The testimony ledger: what it counts, what it refuses to count, what it renders.

Four groups, each with the perturbation that proves it bites (craft rule 2):

A. the resolver and the registration -- default OFF, one key flipped, the
   committed stamp still reading False through the missing-key rule;
B. the builder -- first-hand versus adopted, the fabrication that earns no
   account, the boomerang, and the map's walkable pair, each against a
   near-identical input that lands the other way;
C. the render and the stamp -- an absent ledger renders the pre-lever bytes, a
   present one renders rows only for this voter's candidates, and the lever-ON
   ballot can never wear the default ``vote_ballot`` version string;
D. the walk -- every meeting of the four committed sets rebuilt through the real
   manager, its structural invariants asserted and its four cells re-derived.
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import pytest

from agents.strategic.prompts.loader import build_prompt_renderers
from meetings.constants import (
    ENV_TESTIMONY_SHAPES,
    MAP_ARBITRATION_MAX_HOPS,
    MAP_ARBITRATION_MAX_TICK_GAP,
)
from meetings.corroboration import (
    ENV_CORROBORATION_DISCIPLINE,
    MAX_WALKABLE_TRANSITS_PER_SUBJECT,
    MeetingTestimonyLedger,
    build_testimony_ledger,
    corroboration_discipline_enabled,
)

# Aliased so pytest does not try to COLLECT the production row DTO as a test
# class on its ``Test`` prefix.
from meetings.corroboration import TestimonySupport as _TestimonySupport
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    SuspicionEntry,
)
from meetings.schemas import (
    AccusationClaim,
    Claim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    MoveWitnessRecord,
    ObservationClaim,
    PlayerId,
    SawKillObservation,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
)
from meetings.transcript import reconstruct_stated_paths, room_hops
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS,
    PROMPT_VERSION_SETS,
    TESTIMONY_SHAPES_PROMPT_VERSION_SETS,
    _arm_is_served,  # noqa: PLC2701
    _CORROBORATION_DISCIPLINE_ARM,  # noqa: PLC2701
    build_default_meeting_runner,
    prompt_versions_for_set,
)
from orchestrator.replay import (
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    substrate_flag_snapshot,
)
from tests.meetings._manager_helpers import (
    _ScriptedLLMClient,
    _crewmate_report_prompt,
    _impostor_report_prompt,
    _make_responder,
    _run,
    _statement_prompt,
    _vote_prompt,
)

_LEVER_KEY: Final[str] = "corroboration_discipline"
_SET: Final[str] = "qwen3_6_27b"

# --------------------------------------------------------------------------- #
# Builders                                                                     #
# --------------------------------------------------------------------------- #


def _saw(*, subject: str, room: str = "MEDBAY", tick: int = 14) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", tick=tick, subject=subject, room=room
    )


def _record(*, subject: str, room: str = "MEDBAY", tick: int = 14) -> SightingRecord:
    return SightingRecord(subject=subject, room=room, tick=tick)


def _saw_move(
    *,
    subject: str,
    from_room: str = "WEST_HALL",
    to_room: str = "MEDBAY",
    tick: int = 9,
) -> SawMoveObservation:
    return SawMoveObservation(
        type="saw_move",
        tick=tick,
        subject=subject,
        from_room=from_room,
        to_room=to_room,
    )


def _move_record(
    *,
    subject: str,
    from_room: str = "WEST_HALL",
    to_room: str = "MEDBAY",
    tick: int = 9,
) -> MoveWitnessRecord:
    return MoveWitnessRecord(
        subject=subject, from_room=from_room, to_room=to_room, tick=tick
    )


def _accuses(target: str, *, confidence: float = 0.7) -> AccusationClaim:
    return AccusationClaim(
        type="accusation", against=target, confidence=confidence, reason="movement"
    )


def _turn(
    *,
    index: int,
    speaker: str,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m-1:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "reply",
        reply_to=None if index == 0 else f"m-1:turn-{index - 1}",
        observations=observations,
        claims=claims,
        free_text=f"turn {index} from {speaker}",
    )


def _transcript(*turns: MeetingTurn) -> MeetingTranscript:
    return MeetingTranscript(turns=turns)


def _vent_flag(
    subject: str,
    *,
    flag_id: str = "c-1",
    turn_index: int = 0,
    obs_index: int = 0,
) -> ContradictionRef:
    """A ``vent_sighting`` flag naming the observation it was minted from.

    The detector stamps BOTH event ids with the spoken observation's own id, so
    a fixture that wants to ground a particular speaker names that speaker's
    turn -- exactly the provenance the ledger reads back.
    """

    event_id = f"turn:m-1:turn-{turn_index}:obs:{obs_index}"
    return ContradictionRef(
        contradiction_id=flag_id,
        kind="vent_sighting",
        event_a_id=event_id,
        event_b_id=event_id,
        subjects=(subject,),
        description="witnessed vent",
    )


def _saw_vent(
    *, subject: str, room: str = "MEDBAY", tick: int = 11
) -> SawVentObservation:
    return SawVentObservation(type="saw_vent", tick=tick, subject=subject, room=room)


def _saw_kill(
    *, subject: str, room: str = "ADMIN", tick: int = 11
) -> SawKillObservation:
    return SawKillObservation(type="saw_kill", tick=tick, subject=subject, room=room)


def _conflict_flag(subject: str) -> ContradictionRef:
    """A flag that groups as "Conflicting accounts" — two events, no weak marker."""

    return ContradictionRef(
        contradiction_id="c-2",
        kind="alibi_vs_sighting",
        event_a_id="turn:m-1:turn-0:claim:0",
        event_b_id="turn:m-1:turn-1:obs:0",
        subjects=(subject,),
        description="alibi disagrees with a sighting",
    )


_ROSTER: Final[frozenset[PlayerId]] = frozenset(
    {"p-1", "p-2", "p-3", "p-5", "p-7", "p-8"}
)


def _ledger(
    transcript: MeetingTranscript,
    *,
    contradictions: tuple[ContradictionRef, ...] = (),
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]] | None = None,
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]]
    | None = None,
    opener: str = "p-1",
) -> MeetingTestimonyLedger:
    return build_testimony_ledger(
        transcript,
        contradictions=contradictions,
        sighting_records=sighting_records or {},
        move_witness_records=move_witness_records or {},
        opener=opener,
        roster=_ROSTER,
        trigger_kind="report",
    )


def _row(ledger: MeetingTestimonyLedger, subject: str) -> _TestimonySupport:
    match = [row for row in ledger.rows if row.subject == subject]
    assert match, f"no row for {subject}: {[row.subject for row in ledger.rows]}"
    return match[0]


# --------------------------------------------------------------------------- #
# A. The resolver and the registration                                         #
# --------------------------------------------------------------------------- #


class TestResolver:
    @pytest.mark.parametrize("value", ["1", "true", "TRUE", "Yes", "on", "ON"])
    def test_a_truthy_value_reads_on(self, value: str) -> None:
        assert corroboration_discipline_enabled({ENV_CORROBORATION_DISCIPLINE: value})

    @pytest.mark.parametrize("value", ["", "  ", "0", "no", "off", "maybe", "2"])
    def test_anything_else_reads_off(self, value: str) -> None:
        assert not corroboration_discipline_enabled(
            {ENV_CORROBORATION_DISCIPLINE: value}
        )

    def test_absent_and_empty_env_agree(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Both spellings of "nothing is set" must resolve OFF and agree: the
        # ad-hoc caller passes nothing, the deterministic caller passes ``{}``.
        monkeypatch.delenv(ENV_CORROBORATION_DISCIPLINE, raising=False)
        assert corroboration_discipline_enabled() is False
        assert corroboration_discipline_enabled({}) is False
        assert corroboration_discipline_enabled() == corroboration_discipline_enabled(
            {}
        )


class TestRegistration:
    def test_the_key_keeps_its_index_and_stamps_false(self) -> None:
        # A registration is a pure APPEND at the live end, so a sibling
        # registering behind this key must not move it: the INDEX is the
        # invariant a recorded stamp depends on, not being newest.
        assert TOGGLEABLE_SUBSTRATE_FLAG_KEYS[2] == _LEVER_KEY
        assert SUBSTRATE_FLAG_KEYS[23] == _LEVER_KEY
        assert substrate_flag_snapshot({})[_LEVER_KEY] is False

    def test_exporting_the_variable_flips_exactly_this_key(self) -> None:
        # The perturbation: one export, one key. Everything else in the stamp
        # must be byte-identical, which is what makes a recorded slate readable.
        bare = substrate_flag_snapshot({})
        flipped = substrate_flag_snapshot({ENV_CORROBORATION_DISCIPLINE: "1"})
        assert flipped[_LEVER_KEY] is True
        assert flipped == {**bare, _LEVER_KEY: True}


# --------------------------------------------------------------------------- #
# B. The builder                                                               #
# --------------------------------------------------------------------------- #


class TestFirstHandSources:
    def test_a_record_matched_sighting_is_a_first_hand_source(self) -> None:
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(transcript, sighting_records={"p-2": (_record(subject="p-5"),)}),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.adopted == ()
        assert row.voices == 1
        assert row.originating_turn_id == "m-1:turn-0"

    def test_a_fabricated_sighting_earns_no_account(self) -> None:
        # The label bites: the SAME transcript with no matching record leaves
        # p-2 a voice, not an account. An impostor cannot invent one.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(_ledger(transcript, sighting_records={}), "p-5")
        assert row.first_hand == ()
        assert row.adopted == ("p-2",)
        assert row.voices == 1

    def test_a_teammate_naming_record_the_firewall_filtered_out_grounds_nothing(
        self,
    ) -> None:
        # §4.7: the manager hands the builder a mapping with an impostor's rows
        # naming a fellow impostor already removed, so the same spoken sighting
        # grounds with the row present and grounds nothing without it.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        unfiltered = _ledger(
            transcript, sighting_records={"p-2": (_record(subject="p-5"),)}
        )
        firewalled = _ledger(transcript, sighting_records={"p-2": ()})
        assert _row(unfiltered, "p-5").first_hand == ("p-2",)
        assert _row(firewalled, "p-5").first_hand == ()

    def test_a_grounded_movement_claim_is_a_first_hand_source(self) -> None:
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw_move(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        assert _row(
            _ledger(
                transcript,
                move_witness_records={"p-2": (_move_record(subject="p-5"),)},
            ),
            "p-5",
        ).first_hand == ("p-2",)
        # The negative leg is "no record in EITHER channel", now that a
        # ``saw_move`` can also be borne out by a sighting of the destination.
        assert _row(_ledger(transcript), "p-5").first_hand == ()

    def test_a_sighting_the_speakers_own_move_record_bears_out_is_an_account(
        self,
    ) -> None:
        # A witness who watched p-5 walk into MEDBAY holds a MoveWitnessRecord
        # and may say "I saw p-5 in MEDBAY". Both artifacts assert ONE placement
        # (transcript.sighting_placement), so the record bears the sighting out.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=9),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                move_witness_records={
                    "p-2": (
                        _move_record(
                            subject="p-5",
                            from_room="WEST_HALL",
                            to_room="MEDBAY",
                            tick=9,
                        ),
                    )
                },
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.first_hand_places == (("p-2", (("saw_player", "MEDBAY", 9),)),)

    def test_the_origin_half_of_a_move_record_places_nobody(self) -> None:
        # The perturbation: the SAME record, and a sighting naming the room it
        # moved p-5 OUT of. A transition places its subject at the destination
        # and nowhere else, so this one is a voice with no account.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="WEST_HALL", tick=9),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                move_witness_records={
                    "p-2": (
                        _move_record(
                            subject="p-5",
                            from_room="WEST_HALL",
                            to_room="MEDBAY",
                            tick=9,
                        ),
                    )
                },
            ),
            "p-5",
        )
        assert row.first_hand == ()
        assert row.adopted_spoke_ungrounded == ("p-2",)

    def test_the_move_channel_keeps_its_exact_tick(self) -> None:
        # The perturbation for the tolerance: one tick off the record. The
        # channel under test sets the tolerance, and the movement channel's is
        # exact -- crossing the channels must not import the sighting
        # channel's +-2 into it.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=10),),
                claims=(_accuses("p-5"),),
            ),
        )
        assert (
            _row(
                _ledger(
                    transcript,
                    move_witness_records={
                        "p-2": (
                            _move_record(
                                subject="p-5",
                                from_room="WEST_HALL",
                                to_room="MEDBAY",
                                tick=9,
                            ),
                        )
                    },
                ),
                "p-5",
            ).first_hand
            == ()
        )

    def test_a_transition_the_speakers_own_sighting_bears_out_is_an_account(
        self,
    ) -> None:
        # The mirror: a witness who saw p-5 standing in MEDBAY holds a
        # SightingRecord and may say "I saw p-5 move into MEDBAY". The spoken
        # transition's DESTINATION placement is what the record is tested
        # against, through the sighting channel's own predicate.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_move(
                        subject="p-5",
                        from_room="WEST_HALL",
                        to_room="MEDBAY",
                        tick=9,
                    ),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                sighting_records={
                    "p-2": (_record(subject="p-5", room="MEDBAY", tick=9),)
                },
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.first_hand_places == (("p-2", (("saw_move", "MEDBAY", 9),)),)

    def test_a_sighting_at_the_transitions_origin_bears_nothing_out(self) -> None:
        # The perturbation: the same spoken transition, and a record placing p-5
        # in the room they were said to LEAVE. The origin half is unplaced in
        # this direction too.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_move(
                        subject="p-5",
                        from_room="WEST_HALL",
                        to_room="MEDBAY",
                        tick=9,
                    ),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        assert (
            _row(
                _ledger(
                    transcript,
                    sighting_records={
                        "p-2": (_record(subject="p-5", room="WEST_HALL", tick=9),)
                    },
                ),
                "p-5",
            ).first_hand
            == ()
        )

    @pytest.mark.parametrize("spoken", ["saw_player", "saw_move"])
    def test_a_channel_that_disagrees_with_itself_grounds_neither_shape(
        self, spoken: str
    ) -> None:
        # Codex round 2. Engine truth forbids two transitions of one subject
        # landing on one tick, so the movement chokepoint refuses a channel that
        # says otherwise BEFORE either of its arms matches. The ledger's movement
        # channel adjudicates the same way, for both spoken shapes: without it
        # the row could claim the speaker's record bears the placement out while
        # the transit clause's own reconstruction, reading the same rows, refused
        # every one of them.
        observation = (
            _saw(subject="p-5", room="MEDBAY", tick=9)
            if spoken == "saw_player"
            else _saw_move(
                subject="p-5", from_room="WEST_HALL", to_room="MEDBAY", tick=9
            )
        )
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(observation,),
                claims=(_accuses("p-5"),),
            ),
        )
        agreeing = (
            _move_record(
                subject="p-5", from_room="WEST_HALL", to_room="MEDBAY", tick=9
            ),
        )
        conflicting = (
            *agreeing,
            _move_record(subject="p-5", from_room="WEST_HALL", to_room="LABS", tick=9),
        )
        assert _row(
            _ledger(transcript, move_witness_records={"p-2": agreeing}), "p-5"
        ).first_hand == ("p-2",)
        assert (
            _row(
                _ledger(transcript, move_witness_records={"p-2": conflicting}), "p-5"
            ).first_hand
            == ()
        )
        # The two readings agree on the same rows: the chokepoint takes no
        # placement from the conflicted channel either, so nothing this ledger
        # refuses to credit is quietly placed by its own transit input.
        placed = reconstruct_stated_paths(
            transcript,
            roster=_ROSTER,
            trigger_kind="report",
            movement_witness_records={"p-2": conflicting},
        )
        assert [sorted(placement.rooms) for placement in placed.get("p-5", ())] == (
            [["MEDBAY"]] if spoken == "saw_player" else []
        )

    def test_a_spoken_vent_grounds_only_through_the_flag_channel(self) -> None:
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw_vent(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        assert _row(
            _ledger(transcript, contradictions=(_vent_flag("p-5"),)), "p-5"
        ).first_hand == ("p-2",)
        assert _row(_ledger(transcript), "p-5").first_hand == ()

    def test_a_second_vent_speaker_cannot_ride_the_first_one_s_flag(self) -> None:
        # Codex round 1: one grounded vent mints ONE flag naming the subject. A
        # second speaker who repeats the vent with nothing behind it must not be
        # credited by that flag -- reducing the flags to a bare subject set would
        # launder exactly that claim into an independent account.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw_vent(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-8",
                observations=(_saw_vent(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(transcript, contradictions=(_vent_flag("p-5", turn_index=0),)),
            "p-5",
        )
        # The flag names p-2's own observation, so p-2 keeps their account and
        # p-8 -- who added nothing of their own -- is a voice, not an account.
        assert row.first_hand == ("p-2",)
        assert row.adopted == ("p-8",)

    def test_two_grounded_vents_credit_both_speakers(self) -> None:
        # The perturbation: when BOTH spoken vents are grounded the detector
        # mints a flag on EACH observation, and both speakers are credited.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw_vent(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-8",
                observations=(_saw_vent(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                contradictions=(
                    _vent_flag("p-5", turn_index=0),
                    _vent_flag("p-5", flag_id="c-2", turn_index=1),
                ),
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2", "p-8")
        assert row.adopted == ()

    def test_a_prolific_witness_beside_a_fabricator_credits_only_the_witness(
        self,
    ) -> None:
        # Codex round 2: the cardinality case a flag COUNT cannot see. p-2 speaks
        # TWO grounded vents (two flags, both on p-2's own observations) and p-8
        # speaks one ungrounded vent. Counting flags against speakers reads 2 == 2
        # and would credit the fabricator; resolving each flag to its own
        # observation credits p-2 alone.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_vent(subject="p-5", tick=11),
                    _saw_vent(subject="p-5", room="LABS", tick=13),
                ),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-8",
                observations=(_saw_vent(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                contradictions=(
                    _vent_flag("p-5", turn_index=0, obs_index=0),
                    _vent_flag("p-5", flag_id="c-2", turn_index=0, obs_index=1),
                ),
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.adopted == ("p-8",)

    def test_one_witness_with_two_grounded_vents_is_not_erased(self) -> None:
        # The mirror of the same cardinality bug: two flags, ONE speaker. A count
        # would read 2 != 1 and erase a genuine account; the id resolution keeps
        # it, and still counts the speaker exactly once.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_vent(subject="p-5", tick=11),
                    _saw_vent(subject="p-5", room="LABS", tick=13),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                contradictions=(
                    _vent_flag("p-5", turn_index=0, obs_index=0),
                    _vent_flag("p-5", flag_id="c-2", turn_index=0, obs_index=1),
                ),
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.voices == 1
        assert row.first_hand_places == (
            ("p-2", (("saw_vent", "MEDBAY", 11), ("saw_vent", "LABS", 13))),
        )

    def test_one_grounded_vent_does_not_vouch_for_the_speaker_s_other_one(
        self,
    ) -> None:
        # Codex round 1: the flag names the OBSERVATION it was minted from, so a
        # witness who spoke two vents of one subject and had one grounded is one
        # account whose row names one statement. Crediting the pair would print a
        # fabricated vent detail as verified testimony beside a real one — the
        # laundering hole the id resolution exists to close, in its
        # same-speaker form.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_vent(subject="p-5", tick=11),
                    _saw_vent(subject="p-5", room="LABS", tick=13),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                contradictions=(_vent_flag("p-5", turn_index=0, obs_index=0),),
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.voices == 1
        assert row.first_hand_places == (("p-2", (("saw_vent", "MEDBAY", 11),)),)

    def test_two_statements_at_one_tick_are_told_apart_by_room(self) -> None:
        # Codex round 2: the tick alone could not separate a grounded MEDBAY
        # vent from a fabricated LABS one spoken at the SAME tick — the row
        # would have printed one coordinate covering both. The coordinate is
        # room AND tick, which is exactly the pair the transcript above prints,
        # so the credited statement is identifiable on the page.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_vent(subject="p-5", room="MEDBAY", tick=11),
                    _saw_vent(subject="p-5", room="LABS", tick=11),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        ledger = _ledger(
            transcript, contradictions=(_vent_flag("p-5", turn_index=0, obs_index=0),)
        )
        assert _row(ledger, "p-5").first_hand_places == (
            ("p-2", (("saw_vent", "MEDBAY", 11),)),
        )
        # Codex round 3: render the SAME grounded ledger. Rebuilding it without
        # the flag left zero accounts and no coordinate at all, so the negative
        # assertion would have passed even if coordinates stopped rendering —
        # the positive half is what stops this going vacuous.
        rendered = _render(ledger=ledger, transcript=transcript)
        assert "venting in MEDBAY at tick 11" in rendered
        assert "LABS at tick 11" not in rendered

    def test_one_shape_grounded_beside_another_at_the_same_coordinate(self) -> None:
        # Codex round 3: room and tick alone still collided when the two
        # statements were different SHAPES — a grounded sighting beside an
        # ungrounded vent in the same room at the same tick. The coordinate
        # carries the kind too, which is the last thing the transcript row
        # above distinguishes them by.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw(subject="p-5", room="MEDBAY", tick=11),
                    _saw_vent(subject="p-5", room="MEDBAY", tick=11),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        ledger = _ledger(
            transcript,
            sighting_records={"p-2": (_record(subject="p-5", room="MEDBAY", tick=11),)},
        )
        assert _row(ledger, "p-5").first_hand_places == (
            ("p-2", (("saw_player", "MEDBAY", 11),)),
        )
        rendered = _render(ledger=ledger, transcript=transcript)
        assert "p-2 described seeing them (MEDBAY at tick 11)" in rendered
        assert "venting in MEDBAY at tick 11" not in rendered

    def test_one_speaker_counts_once_however_much_they_hold(self) -> None:
        # The double-count guard: two matching records AND two matching
        # observations in one turn still make p-2 exactly one account.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw(subject="p-5", tick=14),
                    _saw(subject="p-5", room="LABS", tick=16),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                sighting_records={
                    "p-2": (
                        _record(subject="p-5", tick=14),
                        _record(subject="p-5", room="LABS", tick=16),
                    )
                },
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.voices == 1
        # One voice, both statements named: the ticks are coordinates, not a
        # second count, and they are what tells the credited statement apart
        # from the speaker's other sighting of the same subject.
        assert row.first_hand_places == (
            ("p-2", (("saw_player", "MEDBAY", 14), ("saw_player", "LABS", 16))),
        )

    def test_the_ticks_name_only_the_statements_the_record_bore_out(self) -> None:
        # The perturbation of the pair above: drop the second record and the
        # speaker keeps their single account, while the tick that no longer
        # holds up disappears from the row. A bare name would have gone on
        # covering both.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw(subject="p-5", tick=14),
                    _saw(subject="p-5", room="LABS", tick=16),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                sighting_records={"p-2": (_record(subject="p-5", tick=14),)},
            ),
            "p-5",
        )
        assert row.first_hand == ("p-2",)
        assert row.first_hand_places == (("p-2", (("saw_player", "MEDBAY", 14),)),)

    def test_a_second_grounded_speaker_makes_it_a_two_account_row(self) -> None:
        # The perturbation of the guard above: an otherwise identical transcript
        # where a SECOND speaker holds a matching record reads two accounts.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        records = {
            "p-2": (_record(subject="p-5"),),
            "p-3": (_record(subject="p-5"),),
        }
        row = _row(_ledger(transcript, sighting_records=records), "p-5")
        assert row.first_hand == ("p-2", "p-3")
        assert row.adopted == ()
        assert row.voices == 2

    def test_a_speaker_is_never_a_source_against_themselves(self) -> None:
        transcript = _transcript(
            _turn(index=0, speaker="p-2", claims=(_accuses("p-2"),)),
        )
        assert _ledger(transcript).rows == ()

    def test_a_spoken_kill_grounds_nothing(self) -> None:
        # The shapes arm's kill observation is not a channel here. Every channel
        # tests an account against a typed record or a minted flag, and the kill
        # shape has neither — no meeting-layer record type, nothing threaded into
        # ``build_testimony_ledger``, no flag kind. Counting it would credit an
        # ungrounded claim as first-hand, the one thing the word is defined here
        # to exclude.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    SawKillObservation(
                        type="saw_kill", tick=14, subject="p-5", room="MEDBAY"
                    ),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        # Not even with a record that COVERS the same subject/room/tick: there
        # is no predicate that could match the two, so record presence is not a
        # back door into the count.
        records = {"p-2": (_record(subject="p-5", room="MEDBAY", tick=14),)}
        row = _row(_ledger(transcript, sighting_records=records), "p-5")
        assert row.first_hand == ()
        assert row.adopted == ("p-2",)
        assert row.voices == 1
        # Excluded from the COUNT, named on the ROW: the ruling says the shape
        # earns no account, not that the speaker said nothing.
        assert row.adopted_spoke_kill == ("p-2",)
        assert row.adopted_silent == ()

    def test_the_exclusion_is_not_a_dead_fixture(self) -> None:
        # Non-vacuity for the leg above: the SAME speaker, the same accusation
        # and the same records, with a ``saw_player`` row instead of the kill,
        # IS a first-hand source. So the previous test measures the kind, not a
        # transcript that could never have grounded anything.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
        )
        records = {"p-2": (_record(subject="p-5", room="MEDBAY", tick=14),)}
        row = _row(_ledger(transcript, sighting_records=records), "p-5")
        assert row.first_hand == ("p-2",)
        assert row.adopted == ()


class TestAdoptedSources:
    # The A-19 pile: one originator plus three repeats naming the same target,
    # none of them adding an observation of their own.
    _PILE = _transcript(
        _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
        _turn(index=1, speaker="p-8", claims=(_accuses("p-5"),)),
        _turn(index=2, speaker="p-3", claims=(_accuses("p-5"),)),
        _turn(index=3, speaker="p-7", claims=(_accuses("p-5"),)),
    )

    def test_the_pile_reads_four_voices_and_no_account(self) -> None:
        row = _row(_ledger(self._PILE), "p-5")
        assert row.first_hand == ()
        assert row.adopted == ("p-1", "p-3", "p-7", "p-8")
        assert row.voices == 4
        assert row.originating_turn_id == "m-1:turn-0"

    def test_a_repeat_that_saw_something_moves_into_the_first_hand_set(self) -> None:
        # The perturbation: p-8 speaks a record-matched sighting of the target on
        # an otherwise identical pile, and moves out of the adopted set.
        pile = _transcript(
            _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
            _turn(
                index=1,
                speaker="p-8",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
            _turn(index=2, speaker="p-3", claims=(_accuses("p-5"),)),
            _turn(index=3, speaker="p-7", claims=(_accuses("p-5"),)),
        )
        row = _row(
            _ledger(pile, sighting_records={"p-8": (_record(subject="p-5"),)}), "p-5"
        )
        assert row.first_hand == ("p-8",)
        assert row.adopted == ("p-1", "p-3", "p-7")
        assert row.voices == 4

    def test_the_two_sets_are_disjoint_and_the_origin_precedes_the_repeats(
        self,
    ) -> None:
        row = _row(_ledger(self._PILE), "p-5")
        assert not set(row.first_hand) & set(row.adopted)
        origin = next(
            turn for turn in self._PILE.turns if turn.turn_id == row.originating_turn_id
        )
        for speaker in row.adopted:
            first = min(
                turn.turn_index
                for turn in self._PILE.turns
                if turn.speaker == speaker
                and any(
                    isinstance(claim, AccusationClaim) and claim.against == row.subject
                    for claim in turn.claims
                )
            )
            if speaker == origin.speaker:
                assert first == origin.turn_index
            else:
                assert first > origin.turn_index

    def test_the_three_adopted_classes_partition_the_set(self) -> None:
        # One accuser per class on one pile: p-1 says nothing, p-3 speaks a
        # sighting no record bears out, p-7 says they watched the kill. The
        # split is a partition, so the honest voice count cannot drift with it.
        pile = _transcript(
            _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=2,
                speaker="p-7",
                observations=(_saw_kill(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(_ledger(pile), "p-5")
        assert row.adopted_silent == ("p-1",)
        assert row.adopted_spoke_ungrounded == ("p-3",)
        assert row.adopted_spoke_kill == ("p-7",)
        assert row.adopted == ("p-1", "p-3", "p-7")
        assert row.voices == 3

    def test_a_borne_out_sighting_empties_the_ungrounded_class(self) -> None:
        # The perturbation: give p-3 the record that bears their sighting out
        # and they leave the adopted set entirely, so the ungrounded class
        # reports a failed check and never mere silence.
        pile = _transcript(
            _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(
            _ledger(pile, sighting_records={"p-3": (_record(subject="p-5"),)}), "p-5"
        )
        assert row.first_hand == ("p-3",)
        assert row.adopted_spoke_ungrounded == ()
        assert row.adopted_silent == ("p-1",)

    def test_a_sighting_of_someone_else_leaves_the_voice_silent(self) -> None:
        # The classes are per SUBJECT: p-3 described seeing p-8, not p-5, so on
        # p-5's row they added nothing they saw. Scoping this to the accused is
        # what stops the row crediting an unrelated statement as a failed check.
        pile = _transcript(
            _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-8"),),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(_ledger(pile), "p-5")
        assert row.adopted_silent == ("p-1", "p-3")
        assert row.adopted_spoke_ungrounded == ()

    def test_a_watched_kill_outranks_a_failed_sighting_on_one_speaker(self) -> None:
        # A voice who said both is named for the kill: it is the strongest thing
        # they claimed, and the classes have to be disjoint for the counts to
        # stay honest.
        pile = _transcript(
            _turn(
                index=0,
                speaker="p-3",
                observations=(_saw(subject="p-5"), _saw_kill(subject="p-5")),
                claims=(_accuses("p-5"),),
            ),
        )
        row = _row(_ledger(pile), "p-5")
        assert row.adopted_spoke_kill == ("p-3",)
        assert row.adopted_spoke_ungrounded == ()

    def test_rows_are_ordered_by_the_turn_the_charge_started_in(self) -> None:
        transcript = _transcript(
            _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
            _turn(index=1, speaker="p-5", claims=(_accuses("p-3"),)),
            _turn(index=2, speaker="p-3", claims=(_accuses("p-8"),)),
        )
        ledger = _ledger(transcript)
        assert [row.subject for row in ledger.rows] == ["p-5", "p-3", "p-8"]


class TestOpenerContext:
    # The boomerang: the opener p-1 accuses p-8 at turn 0; p-8 answers at turn 1
    # by accusing p-1, and nobody else names the opener.
    _BOOMERANG = _transcript(
        _turn(index=0, speaker="p-1", claims=(_accuses("p-8"),)),
        _turn(index=1, speaker="p-8", claims=(_accuses("p-1"),)),
    )

    def test_the_answering_charge_is_marked(self) -> None:
        row = _row(_ledger(self._BOOMERANG, opener="p-1"), "p-1")
        assert row.opener_charge_turn_id == "m-1:turn-0"

    def test_an_originator_the_opener_never_accused_leaves_it_unset(self) -> None:
        # The perturbation: same shape, but the opener's charge landed on someone
        # else, so p-8's accusation is not an answer to one.
        transcript = _transcript(
            _turn(index=0, speaker="p-1", claims=(_accuses("p-3"),)),
            _turn(index=1, speaker="p-8", claims=(_accuses("p-1"),)),
        )
        assert _row(_ledger(transcript, opener="p-1"), "p-1").opener_charge_turn_id is (
            None
        )

    def test_a_non_opener_subject_never_carries_the_field(self) -> None:
        for row in _ledger(self._BOOMERANG, opener="p-1").rows:
            if row.subject != "p-1":
                assert row.opener_charge_turn_id is None

    def test_the_reply_keeps_its_turn_order_and_its_counter_accusation(self) -> None:
        # Provenance only: the ledger records that the charge answered one and
        # changes nothing about the turn that carried it.
        ledger = _ledger(self._BOOMERANG, opener="p-1")
        assert [turn.turn_index for turn in self._BOOMERANG.turns] == [0, 1]
        assert _row(ledger, "p-1").originating_turn_id == "m-1:turn-1"
        assert _row(ledger, "p-8").originating_turn_id == "m-1:turn-0"


class TestWalkableTransits:
    # The A-12 anchor: two spoken placements of p-5 one doorway apart, one tick
    # apart, so one tick of walking reconciles both accounts.
    def test_the_anchor_pair_is_reported_walkable(self) -> None:
        assert (
            room_hops(frozenset({"MEDBAY"}), frozenset({"WEST_HALL"}), max_hops=1) == 1
        )
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5", room="WEST_HALL", tick=15),),
            ),
        )
        assert _row(_ledger(transcript), "p-5").walkable_transits == (
            ("MEDBAY", "WEST_HALL"),
        )

    def test_widening_the_tick_gap_reports_nothing(self) -> None:
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(
                    _saw(
                        subject="p-5",
                        room="WEST_HALL",
                        tick=14 + MAP_ARBITRATION_MAX_TICK_GAP + 1,
                    ),
                ),
            ),
        )
        assert _row(_ledger(transcript), "p-5").walkable_transits == ()

    def test_two_hops_apart_reports_nothing(self) -> None:
        assert (
            room_hops(
                frozenset({"MEDBAY"}),
                frozenset({"ADMIN"}),
                max_hops=MAP_ARBITRATION_MAX_HOPS,
            )
            is None
        )
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5", room="ADMIN", tick=15),),
            ),
        )
        assert _row(_ledger(transcript), "p-5").walkable_transits == ()

    def test_adjacent_rooms_at_the_SAME_tick_are_not_a_walk(self) -> None:
        # Codex round 1: an upper-bound-only tick test accepts a zero-tick gap,
        # and the ballot would then clear as "one tick of walking" a pair that is
        # a physical impossibility -- the exact charge the map refutes. The walk
        # must have had time to happen.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5", room="WEST_HALL", tick=14),),
            ),
        )
        assert _row(_ledger(transcript), "p-5").walkable_transits == ()

    def test_two_accounts_naming_one_room_are_not_a_walk(self) -> None:
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=15),),
            ),
        )
        assert _row(_ledger(transcript), "p-5").walkable_transits == ()

    def test_a_grounded_transition_supplies_the_second_endpoint(self) -> None:
        # The clause reads the movement channel: p-5's WEST_HALL placement
        # arrives only inside p-3's ``saw_move``, which p-3's own record
        # confirms, so the pair the map reconciles is on the page instead of
        # missing. The 1111 m0 shape, where six ballots convicted a crewmate of
        # a walk this clause could not see.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(
                    _saw_move(
                        subject="p-5",
                        from_room="MEDBAY",
                        to_room="WEST_HALL",
                        tick=15,
                    ),
                ),
            ),
        )
        assert _row(
            _ledger(
                transcript,
                move_witness_records={
                    "p-3": (
                        _move_record(
                            subject="p-5",
                            from_room="MEDBAY",
                            to_room="WEST_HALL",
                            tick=15,
                        ),
                    )
                },
            ),
            "p-5",
        ).walkable_transits == (("MEDBAY", "WEST_HALL"),)

    def test_a_subject_among_its_own_company_starts_no_walk(self) -> None:
        # p-3 says they saw p-5 in WEST_HALL and lists p-5 among the company;
        # p-3's own record moved p-5 out of WEST_HALL into MEDBAY on that tick.
        # The re-read leaves the COMPANY at WEST_HALL, so a subject who is their
        # own co-presence would stand in both rooms at tick 9 -- and WEST_HALL
        # is one door from CAFETERIA, where p-1 places p-5 a tick later, so the
        # clause would certify a walk out of a room p-3's record says p-5 had
        # left. MEDBAY to CAFETERIA is two doors, which is why the certified
        # pair disappears rather than merely changing endpoints.
        assert (
            room_hops(frozenset({"WEST_HALL"}), frozenset({"CAFETERIA"}), max_hops=1)
            == 1
        )
        assert (
            room_hops(
                frozenset({"MEDBAY"}),
                frozenset({"CAFETERIA"}),
                max_hops=MAP_ARBITRATION_MAX_HOPS,
            )
            is None
        )
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-3",
                observations=(
                    SawPlayerObservation(
                        type="saw_player",
                        tick=9,
                        subject="p-5",
                        room="WEST_HALL",
                        co_present=("p-5", "p-7"),
                    ),
                ),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="CAFETERIA", tick=10),),
            ),
        )
        row = _row(
            _ledger(
                transcript,
                move_witness_records={
                    "p-3": (
                        _move_record(
                            subject="p-5",
                            from_room="WEST_HALL",
                            to_room="MEDBAY",
                            tick=9,
                        ),
                    )
                },
            ),
            "p-5",
        )
        assert row.walkable_transits == ()

    def test_an_ungrounded_transition_supplies_nothing(self) -> None:
        # The perturbation: the SAME transcript with p-3 holding no record. An
        # invented transition places nobody, so the clause reports no walk --
        # the movement chokepoint's rule, not a second copy of it.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(
                    _saw_move(
                        subject="p-5",
                        from_room="MEDBAY",
                        to_room="WEST_HALL",
                        tick=15,
                    ),
                ),
            ),
        )
        assert _row(_ledger(transcript), "p-5").walkable_transits == ()


class TestFlagged:
    _CHARGE = _transcript(_turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)))

    def test_the_field_reads_the_flags_not_a_suspicion_value(self) -> None:
        # The same zero-flag predicate ``guard_ballot_citation`` uses: a
        # contradiction naming the subject in ``subjects``, nothing else.
        assert _row(_ledger(self._CHARGE), "p-5").flagged is False
        assert (
            _row(
                _ledger(self._CHARGE, contradictions=(_vent_flag("p-5"),)), "p-5"
            ).flagged
            is True
        )

    def test_a_flag_naming_someone_else_leaves_it_false(self) -> None:
        assert (
            _row(
                _ledger(self._CHARGE, contradictions=(_vent_flag("p-3"),)), "p-5"
            ).flagged
            is False
        )


class TestPurity:
    def test_repeat_calls_return_an_identical_ledger(self) -> None:
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(_saw(subject="p-5"),),
                claims=(_accuses("p-5"),),
            ),
            _turn(index=1, speaker="p-3", claims=(_accuses("p-5"),)),
        )
        records = {"p-2": (_record(subject="p-5"),)}
        first = _ledger(transcript, sighting_records=records)
        second = _ledger(transcript, sighting_records=records)
        assert first == second

    def test_no_accusation_means_no_rows(self) -> None:
        transcript = _transcript(
            _turn(index=0, speaker="p-2", observations=(_saw(subject="p-5"),)),
        )
        ledger = _ledger(transcript)
        assert ledger.rows == ()
        assert not ledger


# --------------------------------------------------------------------------- #
# C. The render and the stamp                                                  #
# --------------------------------------------------------------------------- #


_RENDER_TRANSCRIPT = _transcript(
    _turn(
        index=0,
        speaker="p-1",
        observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
        claims=(_accuses("p-5"),),
    ),
    _turn(index=1, speaker="p-8", claims=(_accuses("p-5"),)),
    _turn(index=2, speaker="p-3", claims=(_accuses("p-5"),)),
)
_RENDER_RECORDS: Final[Mapping[PlayerId, tuple[SightingRecord, ...]]] = {
    "p-1": (_record(subject="p-5", room="MEDBAY", tick=14),)
}


def _render(
    *,
    ledger: MeetingTestimonyLedger | None,
    candidates: tuple[str, ...] = ("p-5",),
    env: Mapping[str, str] | None = None,
    contradiction_flags: tuple[ContradictionRef, ...] = (),
    transcript: MeetingTranscript = _RENDER_TRANSCRIPT,
) -> str:
    """One ballot render. ``transcript`` is the ledger's own wherever a case
    turns on the two agreeing — the production seam renders both from one
    meeting, so a fixture that split them could not see a block naming a shape
    the transcript above it refuses to show."""

    renderers = build_prompt_renderers(_SET, env=dict(env or {}))
    return renderers.vote(
        voter_id="p-2",
        rendered_memory="## Your role: CREWMATE\nnothing yet",
        transcript=transcript,
        contradiction_flags=contradiction_flags,
        suspicion_graph=(SuspicionEntry(player_id="p-5", suspicion=0.5, trust=0.5),),
        candidate_targets=candidates,
        skip_confidence_threshold=0.6,
        testimony_ledger=ledger,
    )


def _block(rendered: str) -> str:
    """Just the source-count block, so a claim about it cannot pass on the page."""

    return rendered.split("<testimony_sources>")[1].split("</testimony_sources>")[0]


class TestAdoptedClauseWording:
    """The adopted clause says what each voice actually did, speaker by speaker.

    One sentence for every adopted voice was false in both directions: a voice
    who spoke nothing read as a failed check, and a voice whose own memory says
    they watched the kill read as having added nothing they saw. So the clause
    forks on the SPEAKER's own shapes — silent, an ungrounded sighting, or a
    watched kill — rather than on the shapes ARM, which cannot know which of the
    three a given voice is. The counts do not move; only which sentence each
    name sits in. The one thing the arm still governs is whether the KILL may be
    named at all, because the transcript three blocks up renders that shape only
    under the arm and the row must never name evidence the page refuses to show.
    """

    _SILENT: Final[str] = "named them without adding anything they saw"
    _UNGROUNDED: Final[str] = (
        "described seeing them, but their own record does not bear that out"
    )
    _KILL: Final[str] = (
        "described watching the kill — nothing at this table can confirm a kill"
    )
    _ON: Final[Mapping[str, str]] = {ENV_TESTIMONY_SHAPES: "1"}

    _KILL_WITNESSES: Final[tuple[PlayerId, ...]] = ("p-7", "p-8")

    @classmethod
    def _table(
        cls,
        *,
        p3_observation: tuple[ObservationClaim, ...] = (),
        with_kill: bool = True,
        kills: int = 1,
    ) -> tuple[MeetingTranscript, MeetingTestimonyLedger]:
        """One table: p-1 and p-2 silent, p-3 as given, then ``kills`` witnesses.

        The transcript is returned WITH its ledger so a render can pass both —
        the production seam builds them from one meeting, and a case about the
        row agreeing with the transcript above it cannot be made on two.
        """

        turns = [
            _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
            _turn(index=1, speaker="p-2", claims=(_accuses("p-5"),)),
            _turn(
                index=2,
                speaker="p-3",
                observations=p3_observation,
                claims=(_accuses("p-5"),),
            ),
        ]
        if with_kill:
            for offset, witness in enumerate(cls._KILL_WITNESSES[:kills]):
                turns.append(
                    _turn(
                        index=3 + offset,
                        speaker=witness,
                        observations=(_saw_kill(subject="p-5"),),
                        claims=(_accuses("p-5"),),
                    )
                )
        transcript = _transcript(*turns)
        return transcript, _ledger(transcript, opener="p-1")

    def _rendered(
        self,
        *,
        env: Mapping[str, str] | None = None,
        p3_observation: tuple[ObservationClaim, ...] = (),
        with_kill: bool = True,
        kills: int = 1,
    ) -> str:
        transcript, ledger = self._table(
            p3_observation=p3_observation, with_kill=with_kill, kills=kills
        )
        return _render(ledger=ledger, transcript=transcript, env=env)

    @staticmethod
    def _interaction(
        transcript: MeetingTranscript, ledger: MeetingTestimonyLedger
    ) -> int:
        """Joint-slate bytes minus what the two arms add on their own."""

        def size(**kwargs: object) -> int:
            return len(_render(transcript=transcript, **kwargs).encode("utf-8"))  # type: ignore[arg-type]

        off = size(ledger=None)
        shapes = size(ledger=None, env={ENV_TESTIMONY_SHAPES: "1"})
        source = size(ledger=ledger)
        both = size(ledger=ledger, env={ENV_TESTIMONY_SHAPES: "1"})
        return (both - off) - ((shapes - off) + (source - off))

    def test_each_voice_gets_the_sentence_its_own_shapes_earn(self) -> None:
        rendered = self._rendered(
            env=self._ON, p3_observation=(_saw(subject="p-5", tick=14),)
        )
        assert f"p-1, p-2 {self._SILENT}" in rendered
        assert f"p-3 {self._UNGROUNDED}" in rendered
        assert f"p-7 {self._KILL}" in rendered

    def test_a_silent_voice_is_never_told_its_record_failed(self) -> None:
        # The larger half of the population: a voice who spoke nothing must not
        # read as a check that was run and came back empty.
        rendered = self._rendered(with_kill=False)
        assert f"p-1, p-2, p-3 {self._SILENT}" in rendered
        assert self._UNGROUNDED not in rendered

    def test_only_that_clause_moves_when_a_voice_changes_class(self) -> None:
        # Craft rule 2, and the gate that makes the others meaningful: give p-3
        # one ungrounded sighting and the ONLY thing that moves in this block is
        # which sentence p-3's name sits in. Scoped to the block because the
        # transcript above it legitimately gains the sighting row too — the
        # ledger's honesty is that the two agree, not that the page is frozen.
        silent = _block(self._rendered(with_kill=False))
        spoke = _block(
            self._rendered(
                with_kill=False, p3_observation=(_saw(subject="p-5", tick=14),)
            )
        )
        assert silent != spoke
        assert (
            silent.replace(
                f"p-1, p-2, p-3 {self._SILENT}",
                f"p-1, p-2 {self._SILENT}; p-3 {self._UNGROUNDED}",
            )
            == spoke
        )

    def test_the_arm_does_not_word_voices_it_cannot_see(self) -> None:
        # With no kill at the table the arm governs nothing on this block: a
        # silent voice and an ungrounded sighting read the same under both
        # states, because the arm cannot tell them apart and the ledger can.
        for observation in ((), (_saw(subject="p-5", tick=14),)):
            assert self._rendered(
                env=self._ON, with_kill=False, p3_observation=observation
            ) == self._rendered(with_kill=False, p3_observation=observation)

    def test_the_row_never_names_a_shape_the_transcript_refuses_to_show(
        self,
    ) -> None:
        # Codex round 1: the ballot's observation walk renders a spoken
        # ``saw_kill`` only under the shapes arm, so with the arm DOWN a row
        # saying "described watching the kill" would publish content the same
        # page withholds — the corroboration-only leg leaking a sibling lever's
        # surface. With the arm down the kill witness reads as what the ledger
        # can defend about them instead: they described seeing the subject and
        # no record bears it out.
        off = self._rendered()
        assert "KILL" not in off
        assert self._KILL not in off
        assert f"p-7 {self._UNGROUNDED}" in off
        on = self._rendered(env=self._ON)
        assert "witnessed p-5 KILL" in on
        assert f"p-7 {self._KILL}" in on

    def test_a_spoken_kill_is_the_one_cross_lever_interaction_on_this_page(
        self,
    ) -> None:
        # Codex round 2, and the prediction 21.23's smoke has to be able to
        # read: the gate above IS an interaction between the two arms, so a
        # joint-slate ballot at a table where a kill was spoken carries bytes
        # neither arm produces alone. Registered here on a SYNTHETIC kill rather
        # than inferred from a corpus that happens to hold none — the committed
        # bytes carry 0 spoken ``saw_kill``, which is why the published census
        # shows the interaction at zero and not why it is absent.
        transcript, ledger = self._table()
        interaction = self._interaction(transcript, ledger)
        assert interaction > 0
        # The floor of the class: kill witnesses ONLY, so both arms render one
        # clause and only its tail moves.
        assert interaction == len(self._KILL.encode("utf-8")) - len(
            self._UNGROUNDED.encode("utf-8")
        )

    def test_the_interaction_does_not_scale_with_the_witness_count(self) -> None:
        # Codex round 3: "per adopted kill witness" was the wrong unit. The
        # template joins every kill witness into ONE clause, so a second witness
        # moves the names on both arms and leaves the interaction where it was.
        one = self._table(kills=1)
        two = self._table(kills=2)
        assert "p-7, p-8" in self._rendered(env=self._ON, kills=2)
        assert self._interaction(*two) == self._interaction(*one)

    def test_a_mixed_row_pays_a_whole_clause_not_a_tail(self) -> None:
        # Codex round 3, the other half of the composition: when the row also
        # carries an ungrounded voice, the OFF arm merges both names into one
        # clause while the joint arm emits two. The interaction is then the
        # SPLIT — a second "; " lead-in, the kill names again, and the kill
        # sentence in full, less the separator that leaves the merged list — an
        # order of magnitude above the tail-only floor, which is why the
        # prediction has to name the row composition and not a per-witness rate.
        mixed = self._table(p3_observation=(_saw(subject="p-5", tick=14),))
        floor = self._interaction(*self._table())
        assert self._interaction(*mixed) > 10 * floor
        # It is the split, exactly: one extra clause carrying p-7's name, minus
        # the ", p-7" the merged OFF clause no longer needs.
        assert self._interaction(*mixed) == len(f"; p-7 {self._KILL}".encode()) - len(
            b", p-7"
        )

    def test_a_table_with_no_kill_has_no_interaction(self) -> None:
        # The perturbation for all three above: strip the kill witnesses and the
        # joint ballot is exactly the two arms added, whatever else the row
        # carries. That is the shape the published census records over the
        # committed bytes, and the reason it records zero.
        for observation in ((), (_saw(subject="p-5", tick=14),)):
            transcript, ledger = self._table(
                with_kill=False, p3_observation=observation
            )
            assert self._interaction(transcript, ledger) == 0

    def test_the_counts_are_untouched_by_the_wording(self) -> None:
        # The perturbation that would make the class vacuous is a reworded
        # clause that also moved a number. Every variant states the SAME split.
        for observation in ((), (_saw(subject="p-5", tick=14),)):
            for env in (None, self._ON):
                assert "4 voices, 0 accounts" in self._rendered(
                    env=env, p3_observation=observation
                )


class TestRender:
    _LADDER: Final[str] = (
        "1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a "
        "case a second account or a contradiction corroborates; ~0.5 for a hunch "
        "read off movement alone."
    )

    def test_an_absent_ledger_renders_the_pre_lever_bytes(self) -> None:
        renderers = build_prompt_renderers(_SET, env={})
        without_kwarg = renderers.vote(
            voter_id="p-2",
            rendered_memory="## Your role: CREWMATE\nnothing yet",
            transcript=_RENDER_TRANSCRIPT,
            contradiction_flags=(),
            suspicion_graph=(
                SuspicionEntry(player_id="p-5", suspicion=0.5, trust=0.5),
            ),
            candidate_targets=("p-5",),
            skip_confidence_threshold=0.6,
        )
        assert _render(ledger=None) == without_kwarg
        assert "<testimony_sources>" not in without_kwarg

    def test_the_block_states_the_counts_and_names_the_repeats(self) -> None:
        rendered = _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        )
        assert "<testimony_sources>" in rendered
        assert "p-5: 3 voices, 1 account" in rendered
        assert "it started at [m-1:turn-0]" in rendered
        assert "p-1 described seeing them (MEDBAY at tick 14)" in rendered
        assert "p-3, p-8 named them without adding anything they saw" in rendered

    def test_the_account_names_the_statement_it_rests_on(self) -> None:
        # The block's definition of "account" is singular, so a bare name lets a
        # voter read the credit as covering EVERY sighting that speaker gave —
        # including the one a contradiction above may be quoting. The ticks say
        # which statements the record bore out and, by omission, which it did
        # not. Here p-1's t14 sighting matches a record and their t19 one does
        # not, and only the first is named.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    _saw(subject="p-5", room="MEDBAY", tick=14),
                    _saw(subject="p-5", room="ADMIN", tick=19),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        records = {"p-1": (_record(subject="p-5", room="MEDBAY", tick=14),)}
        rendered = _render(ledger=_ledger(transcript, sighting_records=records))
        assert "p-1 described seeing them (MEDBAY at tick 14)" in rendered
        assert "ADMIN at tick 19" not in rendered

    def test_two_borne_out_statements_are_both_named(self) -> None:
        # The plural leg, and the non-vacuity twin of the test above: add the
        # record that bears the second statement out and the parenthetical says
        # so, while the COUNT stays at one account — a speaker is one voice
        # however many of their statements hold up.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(
                    _saw(subject="p-5", room="MEDBAY", tick=14),
                    _saw(subject="p-5", room="ADMIN", tick=19),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        records = {
            "p-1": (
                _record(subject="p-5", room="MEDBAY", tick=14),
                _record(subject="p-5", room="ADMIN", tick=19),
            )
        }
        rendered = _render(ledger=_ledger(transcript, sighting_records=records))
        assert (
            "p-1 described seeing them (MEDBAY at tick 14, ADMIN at tick 19)"
            in rendered
        )
        assert "p-5: 1 voice, 1 account" in rendered

    def test_a_coordinate_earned_under_two_shapes_is_named_once(self) -> None:
        # p-2 spoke the transition AND the arrival behind it, and one move
        # record bears both out, so the ledger credits two statements at one
        # (room, tick). Printed as they stand, the account line says "arriving in
        # MEDBAY at tick 9, MEDBAY at tick 9" — one place, said twice, reading
        # like two sightings. The render names it once, under the shape that
        # says the most about it; the ledger keeps both statements.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_move(
                        subject="p-5", from_room="WEST_HALL", to_room="MEDBAY", tick=9
                    ),
                    _saw(subject="p-5", room="MEDBAY", tick=9),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        ledger = _ledger(
            transcript,
            move_witness_records={
                "p-2": (
                    _move_record(
                        subject="p-5", from_room="WEST_HALL", to_room="MEDBAY", tick=9
                    ),
                )
            },
        )
        row = _row(ledger, "p-5")
        assert row.first_hand_places == (
            ("p-2", (("saw_move", "MEDBAY", 9), ("saw_player", "MEDBAY", 9))),
        )
        assert row.rendered_first_hand_places == (
            ("p-2", (("saw_move", "MEDBAY", 9),)),
        )
        rendered = _render(ledger=ledger, transcript=transcript)
        assert "p-2 described seeing them (arriving in MEDBAY at tick 9)" in rendered
        assert "MEDBAY at tick 9, MEDBAY at tick 9" not in rendered

    def test_two_coordinates_that_differ_are_both_still_named(self) -> None:
        # The non-vacuity twin: move the arrival one room on and the same two
        # shapes are two places, so both are printed. The dedupe reads the
        # coordinate, never the shape.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-2",
                observations=(
                    _saw_move(
                        subject="p-5", from_room="WEST_HALL", to_room="MEDBAY", tick=9
                    ),
                    _saw(subject="p-5", room="LABS", tick=10),
                ),
                claims=(_accuses("p-5"),),
            ),
        )
        ledger = _ledger(
            transcript,
            move_witness_records={
                "p-2": (
                    _move_record(
                        subject="p-5", from_room="WEST_HALL", to_room="MEDBAY", tick=9
                    ),
                )
            },
            sighting_records={"p-2": (_record(subject="p-5", room="LABS", tick=10),)},
        )
        rendered = _render(ledger=ledger, transcript=transcript)
        assert (
            "p-2 described seeing them (arriving in MEDBAY at tick 9, LABS at tick 10)"
            in rendered
        )

    def test_the_header_glosses_a_voice_as_the_accusation_channel(self) -> None:
        # The ledger counts accusers. A header that said "anyone who named them"
        # promised the transcript's whole vocabulary — a corroboration claim, a
        # sighting filed against a different name, a mention in free text — and
        # the same page then falsifies it. The gloss states the channel and says
        # where the rest of what was said still lives.
        block = _block(
            _render(
                ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
            )
        )
        assert "A voice is anyone who accused them tonight" in block
        assert "who only backed another's charge, is not counted here" in block
        assert "a player nobody accused has no row" in block

    def test_the_header_says_what_a_second_account_does_and_does_not_settle(
        self,
    ) -> None:
        # A sighting or a movement is a PLACEMENT, while the closing ladder
        # prices "a second account corroborates" in the everyday sense. Two
        # people placing someone in a corridor corroborate each other and
        # nothing about the death, so the header states the scope the ladder
        # assumes — and names the one channel that is not a placement, because a
        # grounded vent IS an account here and is role proof, not geography
        # (Codex round 1).
        block = _block(
            _render(
                ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
            )
        )
        assert "A sighting or a movement only places them somewhere" in block
        assert "only where what it describes bears on the death" in block
        assert (
            "a watched vent is the exception — it names an impostor outright" in block
        )

    def test_the_flag_clause_states_both_polarities(self) -> None:
        # The zero-flag half of the case, read off the flags exactly as
        # ``guard_ballot_citation`` reads them and stated symmetrically, so the
        # row does not lean either way on its own.
        unflagged = _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        )
        assert "No contradiction above names them." in unflagged
        flagged = _render(
            ledger=_ledger(
                _RENDER_TRANSCRIPT,
                contradictions=(_vent_flag("p-5"),),
                sighting_records=_RENDER_RECORDS,
            )
        )
        # The clause names the CONTRADICTION section, not "the evidence": this
        # block calls testimony evidence two lines up, so the negative polarity
        # would otherwise deny the account it has just credited. "Contradiction"
        # is the section's own rendered noun and covers every flag category —
        # a ``vent_sighting`` is role PROOF up there, and a row calling it "a
        # conflict" would contradict the ballot's own taxonomy and invite the
        # voter to underweight the strongest evidence in the game.
        assert (
            "A contradiction above names them — read it there, in its own class."
            in (flagged)
        )
        block = _block(flagged)
        assert "conflict" not in block

    def test_the_band_sentence_restates_the_ladder_verbatim(self) -> None:
        # The ladder the accusation template already asks for, quoted from the
        # served bytes rather than paraphrased, so the two surfaces agree.
        ladder = self._LADDER
        accusation = (
            Path("agents/strategic/prompts") / _SET / "accusation_round.j2"
        ).read_text(encoding="utf-8")
        assert ladder in accusation
        assert ladder in _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        )

    def test_the_band_sentence_yields_to_a_proof_flag(self) -> None:
        # The ladder prices a vent someone ELSE watched at ~0.7, while the Proof
        # paragraph three lines up says nothing at this table outweighs it. Two
        # instructions, one page, opposite answers on the same evidence — so
        # where Proof renders, the ladder does not, and the paragraph that owns
        # the strongest evidence class is the one the voter reads.
        ledger = _ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        rendered = _render(ledger=ledger, contradiction_flags=(_vent_flag("p-5"),))
        assert "Proof. Only an impostor can vent" in rendered
        assert self._LADDER not in rendered

    def test_a_non_proof_flag_leaves_the_band_sentence_standing(self) -> None:
        # The perturbation: the gate is on the PROOF group, not on flags. A
        # conflicting-accounts flag raises no unanswerable-evidence paragraph,
        # so the ladder is still the page's only pricing instruction.
        ledger = _ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        rendered = _render(ledger=ledger, contradiction_flags=(_conflict_flag("p-5"),))
        assert "Conflicting accounts." in rendered
        assert "Proof. Only an impostor can vent" not in rendered
        assert self._LADDER in rendered

    def test_rows_are_emitted_only_for_this_voter_s_candidates(self) -> None:
        transcript = _transcript(
            _turn(index=0, speaker="p-1", claims=(_accuses("p-5"),)),
            _turn(index=1, speaker="p-5", claims=(_accuses("p-3"),)),
        )
        rendered = _render(ledger=_ledger(transcript), candidates=("p-5",))
        assert "p-5: 1 voice" in rendered
        assert "p-3: 1 voice" not in rendered

    def test_an_empty_candidate_set_renders_no_block(self) -> None:
        rendered = _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS),
            candidates=(),
        )
        assert "<testimony_sources>" not in rendered

    def test_the_block_carries_no_internal_dialect(self) -> None:
        # Craft rule 4: no task id, no audit id, no threshold arithmetic, no
        # jargon the block does not itself define.
        rendered = _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        )
        block = _block(rendered)
        for banned in (
            "Task ",
            "audits/",
            "A-10",
            "A-19",
            "hearsay",
            "corroboration_discipline",
            "AILIBI_",
            "lever",
            "MAP_ARBITRATION",
        ):
            assert banned not in block, banned

    def test_the_transit_lines_are_bounded(self) -> None:
        # Three walkable pairs exist; the row carries at most two, so the ballot
        # cannot degenerate into a map dump.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5", room="WEST_HALL", tick=15),),
            ),
            _turn(
                index=2,
                speaker="p-7",
                observations=(_saw(subject="p-5", room="ADMIN", tick=16),),
            ),
            _turn(
                index=3,
                speaker="p-8",
                observations=(_saw(subject="p-5", room="CAFETERIA", tick=17),),
            ),
        )
        row = _row(_ledger(transcript), "p-5")
        assert len(row.walkable_transits) == MAX_WALKABLE_TRANSITS_PER_SUBJECT
        rendered = _render(ledger=_ledger(transcript))
        assert rendered.count("so walking fits both") == 2

    def test_the_transit_line_calls_the_placements_statements_not_accounts(
        self,
    ) -> None:
        # Codex round 1: these placements come from ``reconstruct_stated_paths``
        # over EVERY speaker's sightings -- not necessarily accusers, not
        # necessarily record-grounded. Calling them "accounts" would contradict
        # the block's own definition of the word and let a row read
        # "1 voice, 0 accounts" while claiming two accounts placed the target.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5", room="WEST_HALL", tick=15),),
            ),
        )
        rendered = _render(ledger=_ledger(transcript))
        block = _block(rendered)
        assert "0 accounts" in block
        assert "Two statements put" in block
        # Scoped to THIS block: the ``<map>`` card below it has said "Two
        # accounts …" since 20.31, in the looser everyday sense. Inside a block
        # that DEFINES the word, the word has to mean what the block says.
        assert "Two accounts" not in block

    def test_the_transit_line_presupposes_no_dispute(self) -> None:
        # The pair is almost never a flag's two endpoints, and the same row
        # usually says no contradiction names the subject at all — so a tail
        # calling a conflict "thin" defuses one the page has just denied. The
        # line states what the map settles and names the charge it forecloses,
        # without asserting that anyone made it.
        transcript = _transcript(
            _turn(
                index=0,
                speaker="p-1",
                observations=(_saw(subject="p-5", room="MEDBAY", tick=14),),
                claims=(_accuses("p-5"),),
            ),
            _turn(
                index=1,
                speaker="p-3",
                observations=(_saw(subject="p-5", room="WEST_HALL", tick=15),),
            ),
        )
        block = _block(_render(ledger=_ledger(transcript)))
        assert "No contradiction above names them." in block
        assert (
            "so walking fits both; that pair is no ground for an impossible-move "
            "charge." in block
        )


class TestProvenance:
    def test_the_on_arm_re_bodies_the_ballot_alone(self) -> None:
        default = PROMPT_VERSION_SETS[_SET]
        arm = CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS[_SET]
        assert (
            arm["vote_ballot"] == "vote_ballot.qwen3_6_27b.v5.corroboration_discipline"
        )
        assert arm["vote_ballot"] != default["vote_ballot"]
        for template in ("crewmate_report", "impostor_report", "accusation_round"):
            assert arm[template] == default[template]

    def test_both_sides_read_one_env_mapping(self) -> None:
        # The render-one-stamp-another pin, both directions in one test: the
        # SAME mapping that gives the ballot its block gives the recording its
        # stamp, and the mapping that gives neither leaves the default served.
        off: Mapping[str, str] = {}
        on = {ENV_CORROBORATION_DISCIPLINE: "1"}

        assert corroboration_discipline_enabled(off) is False
        assert prompt_versions_for_set(_SET, env=off) == PROMPT_VERSION_SETS[_SET]
        assert "<testimony_sources>" not in _render(ledger=None)

        assert corroboration_discipline_enabled(on) is True
        assert (
            prompt_versions_for_set(_SET, env=on)["vote_ballot"]
            == "vote_ballot.qwen3_6_27b.v5.corroboration_discipline"
        )
        assert "<testimony_sources>" in _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        )

    def test_the_default_registry_entry_is_not_re_bumped(self) -> None:
        assert PROMPT_VERSION_SETS[_SET]["vote_ballot"] == "vote_ballot.qwen3_6_27b.v5"

    def test_the_render_decision_is_read_off_the_versions_actually_served(
        self,
    ) -> None:
        # Codex round 1: a caller may pin ``prompt_versions`` itself, and an
        # env-only read would then render the block under the OFF-arm stamp. The
        # arm is credited only when the SERVED stamp carries its lineage, so the
        # bytes and the provenance are one decision however the versions arrived.
        arm = _CORROBORATION_DISCIPLINE_ARM["vote_ballot"]
        assert _arm_is_served(
            CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS[_SET],
            template="vote_ballot",
            arm=arm,
        )
        # A caller-pinned DEFAULT mapping does not credit the arm, even though
        # the environment says ON -- so the block cannot render under it.
        assert not _arm_is_served(
            PROMPT_VERSION_SETS[_SET], template="vote_ballot", arm=arm
        )
        # And a composite the fold builds when a sibling arm re-bodies the same
        # template still credits this lineage.
        assert _arm_is_served(
            {"vote_ballot": f"other.arm.v1+{arm}"}, template="vote_ballot", arm=arm
        )
        assert not _arm_is_served({}, template="vote_ballot", arm=arm)

    def test_the_live_sibling_composite_still_credits_this_arm(self) -> None:
        # ``testimony_shapes`` re-bodies this same template, so the all-ON slate
        # -- the one a record is spent on -- serves a two-lineage ``vote_ballot``
        # stamp. Read through the LIVE registry rather than a synthetic string,
        # so this fails if an arm value ever contains a '+' and breaks the split.
        arm = _CORROBORATION_DISCIPLINE_ARM["vote_ballot"]
        all_on = {
            "AILIBI_IMPOSTOR_ROLL_CALL": "1",
            "AILIBI_REPORTER_REASONING": "1",
            ENV_CORROBORATION_DISCIPLINE: "1",
            ENV_TESTIMONY_SHAPES: "1",
        }
        served = prompt_versions_for_set(_SET, env=all_on)
        assert "+" in served["vote_ballot"]
        assert _arm_is_served(served, template="vote_ballot", arm=arm)
        # ...and the sibling's own lineage is credited off the same stamp.
        assert _arm_is_served(
            served,
            template="vote_ballot",
            arm=TESTIMONY_SHAPES_PROMPT_VERSION_SETS[_SET]["vote_ballot"],
        )

    def test_an_agreeing_default_pin_leaves_the_ledger_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The ordinary pin: versions and environment agree the arm is OFF, so the
        # runner builds no ledger and every surface says the same thing.
        monkeypatch.delenv(ENV_CORROBORATION_DISCIPLINE, raising=False)
        runner = build_default_meeting_runner(
            llm_client=FakeProvider(),
            prompt_versions=PROMPT_VERSION_SETS[_SET],
        )
        assert runner._manager._corroboration_discipline is False  # noqa: SLF001

    def test_a_pin_that_contradicts_the_environment_is_refused(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Codex round 2: a recording describes this arm THREE times -- the
        # rendered bytes, the recorded ``prompt_versions``, and
        # ``substrate_flag_snapshot``'s ``game_over`` stamp, which reads the
        # environment. Deriving the render from the versions aligns the first two;
        # the third can still disagree, and a recording that labels ON-arm bytes
        # OFF would corrupt any evaluation stratified by substrate flags. So the
        # disagreement is refused rather than recorded (AGENTS.md: no silent
        # fallbacks), in BOTH directions. The arm is authored for this set only,
        # so the set is selected explicitly (see the sibling test below).
        monkeypatch.setenv("AILIBI_PROMPT_SET", _SET)
        monkeypatch.setenv(ENV_CORROBORATION_DISCIPLINE, "1")
        with pytest.raises(ValueError, match="disagree with the source-count arm"):
            build_default_meeting_runner(
                llm_client=FakeProvider(),
                prompt_versions=PROMPT_VERSION_SETS[_SET],
            )

        monkeypatch.delenv(ENV_CORROBORATION_DISCIPLINE, raising=False)
        with pytest.raises(ValueError, match="disagree with the source-count arm"):
            build_default_meeting_runner(
                llm_client=FakeProvider(),
                prompt_versions=CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS[_SET],
            )

    def test_an_arm_pin_for_another_family_is_refused(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Codex round 3: only the ``qwen3_6_27b`` ballot renders the block, and
        # ``build_prompt_renderers`` binds the ACTIVE set independently of the
        # pin. Pinning this arm while another family is active would stamp the
        # arm over bytes that cannot carry it, so the arm value is looked up for
        # the active set and a set with no arm entry can never credit it.
        monkeypatch.setenv("AILIBI_PROMPT_SET", "qwen3_32b")
        monkeypatch.setenv(ENV_CORROBORATION_DISCIPLINE, "1")
        with pytest.raises(ValueError, match="disagree with the source-count arm"):
            build_default_meeting_runner(
                llm_client=FakeProvider(),
                prompt_versions=CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS[_SET],
            )

    def test_an_agreeing_arm_pin_is_accepted(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The perturbation that proves the refusal above is about DISAGREEMENT,
        # not about pinning: the same arm mapping with the variable exported AND
        # the arm's own set active constructs, and arms the ledger.
        monkeypatch.setenv("AILIBI_PROMPT_SET", _SET)
        monkeypatch.setenv(ENV_CORROBORATION_DISCIPLINE, "1")
        runner = build_default_meeting_runner(
            llm_client=FakeProvider(),
            prompt_versions=CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS[_SET],
        )
        assert runner._manager._corroboration_discipline is True  # noqa: SLF001


# --------------------------------------------------------------------------- #
# C2. The manager seam: the lever renders, it does not rewrite                 #
# --------------------------------------------------------------------------- #


@dataclass
class _CapturingVotePrompt:
    """A conforming vote renderer that records the ledger it was threaded."""

    seen: list[MeetingTestimonyLedger | None]

    def __call__(
        self,
        *,
        voter_id: PlayerId,
        rendered_memory: str,
        transcript: MeetingTranscript,
        contradiction_flags: tuple[ContradictionRef, ...],
        suspicion_graph: tuple[SuspicionEntry, ...],
        candidate_targets: tuple[PlayerId, ...],
        skip_confidence_threshold: float,
        fellow_impostor_ids: tuple[PlayerId, ...] = (),
        reporter_id: PlayerId | None = None,
        persona: str = "",
        suspicion_provenance: tuple[SuspicionEntry, ...] = (),
        render_inputs: object | None = None,
        testimony_ledger: MeetingTestimonyLedger | None = None,
    ) -> str:
        self.seen.append(testimony_ledger)
        return _vote_prompt(
            voter_id=voter_id,
            rendered_memory=rendered_memory,
            transcript=transcript,
            contradiction_flags=contradiction_flags,
            suspicion_graph=suspicion_graph,
            candidate_targets=candidate_targets,
            skip_confidence_threshold=skip_confidence_threshold,
            fellow_impostor_ids=fellow_impostor_ids,
            reporter_id=reporter_id,
        )


def _run_with_lever(
    *, corroboration_discipline: bool | None
) -> tuple[object, _CapturingVotePrompt]:
    capture = _CapturingVotePrompt(seen=[])
    responder = _make_responder(
        accusations={"p-1": "p-3", "p-3": "p-2", "p-2": "p-3"},
        vote_targets={"p-1": "p-3", "p-2": "p-3", "p-4": "SKIP"},
        vote_reason_ids={"p-1": "m-1:turn-0"},
    )
    manager = MeetingManager(
        llm_client=_ScriptedLLMClient(responder=responder),
        crewmate_report_prompt=_crewmate_report_prompt,
        impostor_report_prompt=_impostor_report_prompt,
        statement_prompt=_statement_prompt,
        vote_prompt=capture,
        config=MeetingConfig(deadlines=MeetingDeadlines()),
        corroboration_discipline=corroboration_discipline,
    )
    participants = tuple(
        MeetingParticipant(
            agent_id=agent_id,
            role="CREWMATE",
            rendered_memory=f"## Your role: CREWMATE\n{agent_id} memory",
            suspicion_graph=(),
        )
        for agent_id in ("p-1", "p-2", "p-3", "p-4")
    )
    result = _run(
        manager.run(
            meeting_id="m-1",
            trigger=MeetingTrigger(
                triggered_by="p-1",
                trigger_tick=410,
                description="p-1 reported a body at tick 410",
            ),
            participants=participants,
            dead_ids=(),
        )
    )
    return result, capture


class TestManagerSeam:
    def test_the_construction_binding_decides_whether_a_ledger_is_built(self) -> None:
        _, off = _run_with_lever(corroboration_discipline=False)
        assert off.seen and all(ledger is None for ledger in off.seen)
        _, on = _run_with_lever(corroboration_discipline=True)
        assert on.seen and all(ledger is not None for ledger in on.seen)

    def test_the_ledger_is_built_once_and_shared_by_every_ballot(self) -> None:
        _, on = _run_with_lever(corroboration_discipline=True)
        assert len({id(ledger) for ledger in on.seen}) == 1

    def test_a_lever_on_ballot_is_recorded_exactly_as_authored(self) -> None:
        # The guard chain renders nothing and rewrites nothing: the recorded
        # target, confidence, citation ids and rationale are what the ballot
        # authored, byte-for-byte, under both arms.
        off_result, _ = _run_with_lever(corroboration_discipline=False)
        on_result, _ = _run_with_lever(corroboration_discipline=True)
        off_ballots = {ballot.voter: ballot for ballot in off_result.ballots}  # type: ignore[attr-defined]
        for ballot in on_result.ballots:  # type: ignore[attr-defined]
            twin = off_ballots[ballot.voter]
            assert ballot.target == twin.target
            assert ballot.confidence == twin.confidence
            assert ballot.primary_reason_id == twin.primary_reason_id
            assert (
                ballot.primary_reason_observation_id
                == twin.primary_reason_observation_id
            )
            assert ballot.rationale_text == twin.rationale_text
        assert on_result.outcome == off_result.outcome  # type: ignore[attr-defined]
        assert (
            on_result.ejected_player_id  # type: ignore[attr-defined]
            == off_result.ejected_player_id  # type: ignore[attr-defined]
        )


# --------------------------------------------------------------------------- #
# D. The committed-set walk                                                    #
# --------------------------------------------------------------------------- #


_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_COMMITTED_SETS: Final[tuple[Path, ...]] = (
    _REPO_ROOT / "replays" / "samples" / "9p2i",
    _REPO_ROOT / "replays" / "samples" / "4p1i",
    _REPO_ROOT / "replays" / "ml_corpus" / "9p2i",
    _REPO_ROOT / "replays" / "ml_corpus" / "4p1i",
)


@dataclass(frozen=True)
class _WalkCells:
    """The four offline cells, re-derived over the committed bytes."""

    meetings: int
    rows: int
    ejections: int
    ejected_rows: int
    accused_without_a_first_hand_source: int
    ejected_without_a_first_hand_source: int
    ejected_on_an_answering_turn: int
    ejected_with_a_walkable_pair: int
    elapsed: float


@pytest.fixture(scope="module")
def walk_cells() -> _WalkCells:
    """Rebuild the ledger for every committed meeting, once."""

    from engine.world import load_canonical_map
    from tests.meetings.test_prompt_byte_golden import (
        _canonical_renderers,  # noqa: PLC2701
        _seed_paths,  # noqa: PLC2701
        walk_replay_meetings,
    )

    game_map = load_canonical_map()
    renderers = _canonical_renderers()
    meetings = rows = ejections = ejected_rows = 0
    accused_none = ejected_none = ejected_answer = ejected_walk = 0
    started = time.monotonic()
    for set_dir in _COMMITTED_SETS:
        assert set_dir.is_dir(), f"missing committed set: {set_dir}"
        for path in _seed_paths(set_dir):
            for meeting in walk_replay_meetings(
                path, game_map=game_map, renderers_for_set=renderers
            ):
                meetings += 1
                result = meeting.result
                # The §4.7 firewall re-applied exactly as the manager applies it
                # before handing the mapping to the detector.
                sighting_records: dict[PlayerId, tuple[SightingRecord, ...]] = {}
                for participant in meeting.participants:
                    fellows = frozenset(participant.fellow_impostor_ids)
                    kept = tuple(
                        record
                        for record in participant.sighting_records
                        if record.subject not in fellows
                    )
                    if kept:
                        sighting_records[participant.agent_id] = kept
                ledger = build_testimony_ledger(
                    result.transcript,
                    contradictions=result.contradictions,
                    sighting_records=sighting_records,
                    move_witness_records={
                        p.agent_id: p.move_witness_records
                        for p in meeting.participants
                        if p.move_witness_records
                    },
                    opener=result.triggered_by,
                    roster=frozenset(p.agent_id for p in meeting.participants),
                    trigger_kind=meeting.trigger_kind,
                )
                assert ledger.opener == result.triggered_by
                by_turn = {turn.turn_id: turn for turn in result.transcript.turns}
                for row in ledger.rows:
                    rows += 1
                    # A first-hand source is never also counted as adopted.
                    assert not set(row.first_hand) & set(row.adopted)
                    # The originating turn precedes every ADOPTING turn (the
                    # originator's own turn IS the origin, so it ties).
                    origin = by_turn[row.originating_turn_id]
                    for speaker in (*row.first_hand, *row.adopted):
                        first = min(
                            turn.turn_index
                            for turn in result.transcript.turns
                            if turn.speaker == speaker
                            and any(
                                isinstance(claim, AccusationClaim)
                                and claim.against == row.subject
                                for claim in turn.claims
                            )
                        )
                        assert first >= origin.turn_index
                    # The opener-context field implies the subject is the opener.
                    if row.opener_charge_turn_id is not None:
                        assert row.subject == ledger.opener
                    assert (
                        len(row.walkable_transits) <= MAX_WALKABLE_TRANSITS_PER_SUBJECT
                    )
                    if not row.first_hand:
                        accused_none += 1
                ejected = result.ejected_player_id
                if ejected is None:
                    continue
                ejections += 1
                match = [row for row in ledger.rows if row.subject == ejected]
                if not match:
                    continue
                ejected_rows += 1
                row = match[0]
                if not row.first_hand:
                    ejected_none += 1
                if row.opener_charge_turn_id is not None:
                    ejected_answer += 1
                if row.walkable_transits:
                    ejected_walk += 1
    return _WalkCells(
        meetings=meetings,
        rows=rows,
        ejections=ejections,
        ejected_rows=ejected_rows,
        accused_without_a_first_hand_source=accused_none,
        ejected_without_a_first_hand_source=ejected_none,
        ejected_on_an_answering_turn=ejected_answer,
        ejected_with_a_walkable_pair=ejected_walk,
        elapsed=time.monotonic() - started,
    )


class TestCommittedWalk:
    def test_the_walk_covers_the_committed_corpus(self, walk_cells: _WalkCells) -> None:
        # A guard on the instrument, not a pin on the cells: a walk that
        # silently stopped early would report smaller counts and look green.
        assert walk_cells.meetings > 0
        assert walk_cells.rows > 0
        assert walk_cells.ejections > 0

    def test_the_four_cells_are_reported(
        self, walk_cells: _WalkCells, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # No baseline figure is asserted: these are re-derived counts over the
        # committed bytes, printed for the PR. They count RENDERABLE EVIDENCE --
        # which target a voter names under the block, and at what confidence, is
        # behavioral and is resolved only at the adopting record.
        with capsys.disabled():
            print(
                "\n21.19 offline cells over the four committed sets "
                f"({walk_cells.meetings} meetings, {walk_cells.rows} accused rows, "
                f"{walk_cells.ejections} ejections, "
                f"{walk_cells.elapsed:.1f}s):\n"
                "  accused subjects with no first-hand source: "
                f"{walk_cells.accused_without_a_first_hand_source} of "
                f"{walk_cells.rows}\n"
                "  ejected subjects with no first-hand source: "
                f"{walk_cells.ejected_without_a_first_hand_source} of "
                f"{walk_cells.ejected_rows} ejections carrying a row\n"
                "  ejections whose charge answered the ejectee's own: "
                f"{walk_cells.ejected_on_an_answering_turn}\n"
                "  ejected subjects with a map-satisfied placement pair: "
                f"{walk_cells.ejected_with_a_walkable_pair}\n"
            )
        assert walk_cells.accused_without_a_first_hand_source <= walk_cells.rows
        assert walk_cells.ejected_without_a_first_hand_source <= walk_cells.ejected_rows
        assert walk_cells.ejected_on_an_answering_turn <= walk_cells.ejected_rows
        assert walk_cells.ejected_with_a_walkable_pair <= walk_cells.ejected_rows


# --------------------------------------------------------------------------- #
# E. The three recorded meetings the two grounding fixes were filed on         #
# --------------------------------------------------------------------------- #


#: ``(set, seed, meeting index)`` for each meeting the hardening pass named as a
#: worked case, so the amendment is pinned to the recorded bytes it was measured
#: on rather than to synthetic fixtures alone
#: (audits/audit-phase-21-hardening.md §3.2).
_ANCHORS: Final[tuple[tuple[str, int, int], ...]] = (
    ("ml_corpus/9p2i", 1111, 0),
    ("samples/9p2i", 48, 2),
    ("ml_corpus/9p2i", 1002, 2),
)


@pytest.fixture(scope="module")
def anchor_rows() -> dict[tuple[str, int, int], dict[PlayerId, _TestimonySupport]]:
    """Each anchor meeting's ledger rows, keyed by subject."""

    from engine.world import load_canonical_map
    from tests.meetings.test_prompt_byte_golden import (
        _canonical_renderers,  # noqa: PLC2701
        walk_replay_meetings,
    )

    game_map = load_canonical_map()
    renderers = _canonical_renderers()
    anchors: dict[tuple[str, int, int], dict[PlayerId, _TestimonySupport]] = {}
    for set_name, seed, index in _ANCHORS:
        path = _REPO_ROOT / "replays" / set_name / f"replay-seed-{seed}.jsonl"
        assert path.is_file(), f"missing committed replay: {path}"
        meetings = list(
            walk_replay_meetings(path, game_map=game_map, renderers_for_set=renderers)
        )
        meeting = meetings[index]
        result = meeting.result
        # The §4.7 firewall, re-applied exactly as the manager applies it.
        sighting_records: dict[PlayerId, tuple[SightingRecord, ...]] = {}
        for participant in meeting.participants:
            fellows = frozenset(participant.fellow_impostor_ids)
            kept = tuple(
                record
                for record in participant.sighting_records
                if record.subject not in fellows
            )
            if kept:
                sighting_records[participant.agent_id] = kept
        ledger = build_testimony_ledger(
            result.transcript,
            contradictions=result.contradictions,
            sighting_records=sighting_records,
            move_witness_records={
                p.agent_id: p.move_witness_records
                for p in meeting.participants
                if p.move_witness_records
            },
            opener=result.triggered_by,
            roster=frozenset(p.agent_id for p in meeting.participants),
            trigger_kind=meeting.trigger_kind,
        )
        anchors[(set_name, seed, index)] = {row.subject: row for row in ledger.rows}
    return anchors


class TestRecordedAnchors:
    def test_the_convicting_walk_is_now_certified_for_the_convicted(
        self,
        anchor_rows: dict[tuple[str, int, int], dict[PlayerId, _TestimonySupport]],
    ) -> None:
        # Six ballots ejected crewmate p-2 for travelling West Hall -> East Hall
        # in the time available. The middle ADMIN placement exists only inside
        # two spoken transitions, so the clause used to certify the identical
        # walk for p-9, whom nobody convicted, and say nothing for p-2.
        rows = anchor_rows[("ml_corpus/9p2i", 1111, 0)]
        assert rows["p-2"].walkable_transits == (
            ("WEST_HALL", "ADMIN"),
            ("ADMIN", "EAST_HALL"),
        )
        assert rows["p-9"].walkable_transits == (
            ("WEST_HALL", "ADMIN"),
            ("ADMIN", "EAST_HALL"),
        )

    def test_a_sighting_the_speakers_move_record_bears_out_is_credited(
        self,
        anchor_rows: dict[tuple[str, int, int], dict[PlayerId, _TestimonySupport]],
    ) -> None:
        # p-9 spoke "p-2 in WEST_HALL at tick 7" and held the transition that
        # put p-2 there; their own ballot told them they had named p-2 with
        # nothing their record bore out.
        assert "p-9" in anchor_rows[("samples/9p2i", 48, 2)]["p-2"].first_hand

    def test_a_transition_the_speakers_sighting_bears_out_is_credited(
        self,
        anchor_rows: dict[tuple[str, int, int], dict[PlayerId, _TestimonySupport]],
    ) -> None:
        # The mirror direction on the record: p-6 spoke p-2's CAFETERIA ->
        # EAST_HALL transition and held the EAST_HALL sighting behind it.
        assert "p-6" in anchor_rows[("ml_corpus/9p2i", 1002, 2)]["p-2"].first_hand
