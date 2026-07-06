"""Schema tests for the Task 15.4 vent-observability types.

Pins the two public types this task introduces —
:class:`meetings.schemas.SawVentObservation` (the fourth member of the
``ObservationClaim`` discriminated union) and
:class:`meetings.schemas.VentWitnessRecord` (the typed grounding channel) —
plus the backward-compatibility contract: the union extension is ADDITIVE,
so every committed v4 replay meeting entry still parses byte-for-byte
(tasks/phase-15.md Task 15.4, integration risk (b): "a strict validator
change that rejects unknown types would break committed-replay loading —
the backward-compat pin is the guard").
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from meetings.schemas import (
    MeetingTranscript,
    MeetingTurn,
    SawVentObservation,
    VentWitnessRecord,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries

_COMMITTED_9P2I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)


def _vent_turn() -> MeetingTurn:
    return MeetingTurn(
        turn_id="m-1:turn-0",
        turn_index=0,
        speaker="p-2",
        turn_kind="opening",
        reply_to=None,
        observations=(
            SawVentObservation(type="saw_vent", tick=14, subject="p-5", room="MEDBAY"),
        ),
        claims=(),
        free_text="I watched p-5 come out of the vent in MedBay.",
    )


class TestSawVentObservation:
    def test_round_trips_through_the_turn_schema(self) -> None:
        turn = _vent_turn()

        parsed = MeetingTurn.model_validate_json(turn.model_dump_json())

        assert parsed == turn
        observation = parsed.observations[0]
        assert isinstance(observation, SawVentObservation)
        assert observation.subject == "p-5"
        assert observation.room == "MEDBAY"
        assert observation.tick == 14

    def test_union_discriminates_on_saw_vent(self) -> None:
        parsed = MeetingTurn.model_validate(
            {
                "turn_id": "m-1:turn-0",
                "turn_index": 0,
                "speaker": "p-2",
                "turn_kind": "opening",
                "reply_to": None,
                "observations": [
                    {
                        "type": "saw_vent",
                        "tick": 14,
                        "subject": "p-5",
                        "room": "MEDBAY",
                    }
                ],
                "claims": [],
                "free_text": "unsure",
            }
        )

        assert isinstance(parsed.observations[0], SawVentObservation)

    def test_no_phase_field_exists(self) -> None:
        # Deliberately NO enter/exit phase field: perception collapses both
        # vent engine events into one witnessed "vent" action and memory
        # persists only player/room/action, so a phase field would be
        # unobservable fabrication (the task contract's schema decision).
        with pytest.raises(ValidationError):
            SawVentObservation.model_validate(
                {
                    "type": "saw_vent",
                    "tick": 14,
                    "subject": "p-5",
                    "room": "MEDBAY",
                    "phase": "enter",
                }
            )

    def test_unknown_observation_type_is_still_rejected(self) -> None:
        # The union extension is additive, not a loosening: an unknown
        # discriminator still fails validation (no silent fallbacks).
        with pytest.raises(ValidationError):
            MeetingTurn.model_validate(
                {
                    "turn_id": "m-1:turn-0",
                    "turn_index": 0,
                    "speaker": "p-2",
                    "turn_kind": "opening",
                    "reply_to": None,
                    "observations": [
                        {
                            "type": "saw_ghost",
                            "tick": 14,
                            "subject": "p-5",
                            "room": "MEDBAY",
                        }
                    ],
                    "claims": [],
                    "free_text": "unsure",
                }
            )


class TestVentWitnessRecord:
    def test_shape_and_round_trip(self) -> None:
        record = VentWitnessRecord(subject="p-5", room="MEDBAY", tick=14)

        assert VentWitnessRecord.model_validate_json(record.model_dump_json()) == (
            record
        )

    def test_frozen_and_extra_forbid(self) -> None:
        record = VentWitnessRecord(subject="p-5", room="MEDBAY", tick=14)

        with pytest.raises(ValidationError):
            record.subject = "p-6"
        with pytest.raises(ValidationError):
            VentWitnessRecord.model_validate(
                {"subject": "p-5", "room": "MEDBAY", "tick": 14, "phase": "enter"}
            )


class TestCommittedV4ReplaysStillParse:
    def test_committed_meeting_entry_loads_and_round_trips(self) -> None:
        # The backward-compat pin (task DoD): a committed baseline-2 (v4)
        # replay's meeting entries — recorded BEFORE the saw_vent union
        # member existed — parse through the extended schema and round-trip
        # unchanged. Seed 0 is arbitrary but fixed; the full 50-seed
        # byte-identity walk lives in tests/api/test_replay_loader.py.
        path = _COMMITTED_9P2I_DIR / "replay-seed-0.jsonl"
        meetings = [
            entry
            for entry in read_all_entries(path)
            if isinstance(entry, MeetingReplayEntry)
        ]

        assert meetings, "committed seed-0 replay carries no meeting entry"
        for entry in meetings:
            transcript = entry.transcript
            assert isinstance(transcript, MeetingTranscript)
            # No committed v4 turn carries a vent observation (the type did
            # not exist), and every recorded turn re-validates as-is.
            for turn in transcript.turns:
                assert MeetingTurn.model_validate(turn.model_dump()) == turn
                assert not any(
                    isinstance(observation, SawVentObservation)
                    for observation in turn.observations
                )
