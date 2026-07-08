"""Schema tests for the Task 15.4 vent-observability types.

Pins the two public types this task introduces —
:class:`meetings.schemas.SawVentObservation` (the fourth member of the
``ObservationClaim`` discriminated union) and
:class:`meetings.schemas.VentWitnessRecord` (the typed grounding channel) —
plus the backward-compatibility contract: the union extension is ADDITIVE,
so a meeting entry shaped as a PRE-``saw_vent`` recorder emitted it (no
vent observation, no ``vent_sighting`` contradiction) still parses through
the extended schema and round-trips unchanged (tasks/phase-15.md Task 15.4,
integration risk (b): "a strict validator change that rejects unknown types
would break committed-replay loading — the backward-compat pin is the
guard"). The Task 15.7 baseline-3 re-record (Qwen/Qwen3-32B, prompt set
qwen3_32b.v5 + vote_ballot.v6, all six substrate levers ON) surfaces
witnessed vents, so committed rows now carry ``saw_vent`` observations and
can no longer stand in for a v4-era row; the additive-schema guarantee is
therefore pinned against a synthetic v4-shaped fixture, independent of the
committed corpus. The committed-byte identity walk lives in
tests/api/test_replay_loader.py.
"""

from __future__ import annotations

import json
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


def _v4_shaped_meeting_entry() -> dict[str, object]:
    """A meeting replay row shaped as a PRE-Task-15.4 recorder emitted it.

    Carries only the observation kinds (``found_body`` / ``saw_player`` /
    ``completed_task``) and the contradiction kinds (here ``alibi_conflict``)
    that existed BEFORE the ``saw_vent`` union member and the ``vent_sighting``
    contradiction were added — no vent observation, no vent contradiction, no
    :class:`~meetings.schemas.VentWitnessRecord` channel. Because the union
    extension is additive, this is a faithful stand-in for a v4-era committed
    row: today's model serializes byte-identically for content that predates
    ``saw_vent``. It is built by hand (not read from the committed corpus) so
    the additive-schema guarantee no longer depends on a v4 set that the Task
    15.7 baseline-3 re-record replaced with vent-bearing bytes.
    """

    return {
        "kind": "meeting",
        "game_id": "v4-shaped-game",
        "meeting_id": "v4-shaped-game:meeting-0",
        "tick": 12,
        "triggered_by": "p-1",
        "outcome": "EJECTED",
        "ejected_player_id": "p-6",
        "transcript": {
            "turns": [
                {
                    "turn_id": "v4-shaped-game:meeting-0:turn-0",
                    "turn_index": 0,
                    "speaker": "p-1",
                    "turn_kind": "opening",
                    "reply_to": None,
                    "observations": [
                        {
                            "type": "found_body",
                            "tick": 12,
                            "body_of": "p-2",
                            "room": "MEDBAY",
                        },
                        {
                            "type": "saw_player",
                            "tick": 9,
                            "subject": "p-6",
                            "room": "MEDBAY",
                            "co_present": ["p-3"],
                        },
                    ],
                    "claims": [
                        {
                            "type": "accusation",
                            "against": "p-6",
                            "confidence": 0.7,
                            "reason": "p-6 was alone with the body in MedBay.",
                        }
                    ],
                    "free_text": "I found p-2 dead in MedBay and p-6 was right there.",
                },
                {
                    "turn_id": "v4-shaped-game:meeting-0:turn-1",
                    "turn_index": 1,
                    "speaker": "p-6",
                    "turn_kind": "reply",
                    "reply_to": "v4-shaped-game:meeting-0:turn-0",
                    "observations": [
                        {
                            "type": "saw_player",
                            "tick": 9,
                            "subject": "p-1",
                            "room": "CAFETERIA",
                        },
                        {
                            "type": "completed_task",
                            "tick": 8,
                            "task_id": "wires-1",
                            "room": "ELECTRICAL",
                        },
                    ],
                    "claims": [
                        {
                            "type": "alibi",
                            "subject": "p-6",
                            "from_tick": 7,
                            "to_tick": 11,
                            "room": "ELECTRICAL",
                            "evidence": ["wires-1"],
                        },
                        {
                            "type": "corroboration",
                            "supports": "p-3",
                            "on_tick": 9,
                            "reason": "p-3 was with me in Electrical.",
                        },
                    ],
                    "free_text": "I was in Electrical doing wires, not MedBay.",
                },
            ]
        },
        "ballots": [
            {
                "voter": "p-1",
                "target": "p-6",
                "confidence": 0.8,
                "primary_reason_id": "v4-shaped-game:meeting-0:turn-0",
                "considered_alternatives": ["p-3"],
                "rationale_text": "p-6 was with the body.",
            },
            {
                "voter": "p-6",
                "target": "p-1",
                "confidence": 0.5,
                "primary_reason_id": "v4-shaped-game:meeting-0:turn-1",
                "considered_alternatives": [],
                "rationale_text": "p-1 is deflecting.",
            },
            {
                "voter": "p-3",
                "target": "SKIP",
                "confidence": 0.4,
                "primary_reason_id": None,
                "considered_alternatives": ["p-1", "p-6"],
                "rationale_text": "Not enough to be sure.",
            },
        ],
        "contradictions": [
            {
                "contradiction_id": "contra:alibi_conflict:0",
                "kind": "alibi_conflict",
                "event_a_id": "turn:v4-shaped-game:meeting-0:turn-0:obs:1",
                "event_b_id": "turn:v4-shaped-game:meeting-0:turn-1:claim:0",
                "subjects": ["p-6"],
                "description": (
                    "p-1 placed p-6 in MedBay at tick 9, but p-6's alibi claims "
                    "Electrical over tick 7-11."
                ),
            }
        ],
        "llm_calls": [
            {
                "call_kind": "meeting",
                "model": "Qwen/Qwen3-32B",
                "prompt": "You are p-1, opening the meeting ...",
                "response_text": '{"turn_kind": "opening", "accuse": "p-6"}',
                "input_tokens": 1200,
                "output_tokens": 180,
                "cost_usd": 0.0,
                "agent_id": "p-1",
            }
        ],
        "prompt_versions": {
            "meeting_open": "qwen3_32b.v4",
            "vote_ballot": "vote_ballot.v4",
        },
        "state_hash_before": "0" * 64,
        "state_hash_after": "1" * 64,
    }


class TestV4ShapedMeetingEntryStillParses:
    def test_v4_shaped_meeting_entry_loads_and_round_trips(
        self, tmp_path: Path
    ) -> None:
        # The backward-compat pin (Task 15.4 DoD, integration risk (b)): a
        # meeting entry shaped as a PRE-saw_vent recorder emitted it — no
        # saw_vent observation, no vent_sighting contradiction — loads through
        # the extended schema and round-trips unchanged. The Task 15.7
        # baseline-3 re-record (qwen3_32b.v5 + vote_ballot.v6, all six substrate
        # levers ON) surfaces witnessed vents, so committed rows now carry
        # saw_vent observations and can no longer serve as the v4-era fixture;
        # this synthetic v4-shaped row makes the additive-schema guarantee
        # independent of the committed corpus. The full committed-byte identity
        # walk lives in tests/api/test_replay_loader.py.
        path = tmp_path / "replay-v4-shaped.jsonl"
        path.write_text(json.dumps(_v4_shaped_meeting_entry()) + "\n", encoding="utf-8")

        meetings = [
            entry
            for entry in read_all_entries(path)
            if isinstance(entry, MeetingReplayEntry)
        ]

        assert meetings, "v4-shaped fixture carries no meeting entry"
        for entry in meetings:
            transcript = entry.transcript
            assert isinstance(transcript, MeetingTranscript)
            # The whole entry re-validates through the extended schema (the
            # additive union member does not reject the old shape) and the
            # parse round-trips exactly.
            assert (
                MeetingReplayEntry.model_validate_json(entry.model_dump_json()) == entry
            )
            # No v4-shaped turn carries a vent observation (the type did not
            # exist), and every recorded turn re-validates as-is.
            for turn in transcript.turns:
                assert MeetingTurn.model_validate(turn.model_dump()) == turn
                assert not any(
                    isinstance(observation, SawVentObservation)
                    for observation in turn.observations
                )
