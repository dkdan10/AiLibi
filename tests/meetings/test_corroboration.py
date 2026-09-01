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
from meetings.transcript import room_hops
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    CORROBORATION_DISCIPLINE_PROMPT_VERSION_SETS,
    PROMPT_VERSION_SETS,
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
        assert _row(_ledger(transcript), "p-5").first_hand == ()

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
        # The Q4 disposition on #416: the testimony-shapes arm's seventh
        # observation kind does NOT join this walk. Every channel here tests an
        # account against a typed record or a minted flag, and the kill shape
        # has neither — no meeting-layer record type, nothing threaded into
        # ``build_testimony_ledger``, no flag kind. Counting it would credit an
        # ungrounded claim as first-hand, which is the one thing the word is
        # defined here to exclude.
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
    *, ledger: MeetingTestimonyLedger | None, candidates: tuple[str, ...] = ("p-5",)
) -> str:
    renderers = build_prompt_renderers(_SET, env={})
    return renderers.vote(
        voter_id="p-2",
        rendered_memory="## Your role: CREWMATE\nnothing yet",
        transcript=_RENDER_TRANSCRIPT,
        contradiction_flags=(),
        suspicion_graph=(SuspicionEntry(player_id="p-5", suspicion=0.5, trust=0.5),),
        candidate_targets=candidates,
        skip_confidence_threshold=0.6,
        testimony_ledger=ledger,
    )


class TestRender:
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
        assert "p-1 described seeing them" in rendered
        assert "p-3, p-8 named them without adding anything they saw" in rendered

    def test_the_flag_clause_states_both_polarities(self) -> None:
        # The zero-flag half of the case, read off the flags exactly as
        # ``guard_ballot_citation`` reads them and stated symmetrically, so the
        # row does not lean either way on its own.
        unflagged = _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        )
        assert "Nothing in the evidence above names them." in unflagged
        flagged = _render(
            ledger=_ledger(
                _RENDER_TRANSCRIPT,
                contradictions=(_vent_flag("p-5"),),
                sighting_records=_RENDER_RECORDS,
            )
        )
        # Codex round 1: the wording must cover EVERY flag category. A
        # ``vent_sighting`` is role PROOF in the evidence section above, so a row
        # calling it "a conflict" would contradict the ballot's own taxonomy and
        # invite the voter to underweight the strongest evidence in the game.
        assert "The evidence above names them — read it there, in its own class." in (
            flagged
        )
        assert "conflict" not in flagged.split("<testimony_sources>")[1].split(
            "</testimony_sources>"
        )[0].replace("a conflict over that pair is thin", "")

    def test_the_band_sentence_restates_the_ladder_verbatim(self) -> None:
        # The ladder the accusation template already asks for, quoted from the
        # served bytes rather than paraphrased, so the two surfaces agree.
        ladder = (
            "1.0 only for a kill or a vent you watched happen first-hand; ~0.7 for a "
            "case a second account or a contradiction corroborates; ~0.5 for a hunch "
            "read off movement alone."
        )
        accusation = (
            Path("agents/strategic/prompts") / _SET / "accusation_round.j2"
        ).read_text(encoding="utf-8")
        assert ladder in accusation
        assert ladder in _render(
            ledger=_ledger(_RENDER_TRANSCRIPT, sighting_records=_RENDER_RECORDS)
        )

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
        block = rendered.split("<testimony_sources>")[1].split("</testimony_sources>")[
            0
        ]
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
        block = rendered.split("<testimony_sources>")[1].split("</testimony_sources>")[
            0
        ]
        assert "0 accounts" in block
        assert "Two statements put" in block
        # Scoped to THIS block: the ``<map>`` card below it has said "Two
        # accounts …" since 20.31, in the looser everyday sense. Inside a block
        # that DEFINES the word, the word has to mean what the block says.
        assert "Two accounts" not in block


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
