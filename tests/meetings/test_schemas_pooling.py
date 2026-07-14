"""Schema tests for the Task 16.7 roll-call / evidence-pooling types.

Pins the two public types this task introduces —
:class:`meetings.schemas.WhereaboutsClaim` (the fifth member of the
``ObservationClaim`` discriminated union) and
:class:`meetings.schemas.SightingRecord` (the typed grounding channel that
sits beside :class:`meetings.schemas.VentWitnessRecord`) — plus the two
schema decisions the task makes and the backward-compatibility contract.

The SELF-only decision: :class:`WhereaboutsClaim` carries NO ``subject``
field because the subject IS the speaker (``turn.speaker``). Vouching for
OTHERS is already :class:`SawPlayerObservation`'s job, so a subject field
here would only reintroduce the placeholder-subject failure class the shape
was built to eliminate. This module pins that a stray ``subject`` key is
rejected outright (``extra='forbid'``), mirroring the ``saw_vent`` test's
no-phase-field pin.

The additive-union decision: extending ``ObservationClaim`` with a fifth
member is ADDITIVE, not a loosening. An unknown observation discriminator
(e.g. ``"teleported"``) still fails validation, and a COMMITTED meeting
entry recorded BEFORE the ``whereabouts`` kind existed still re-validates
through the extended schema and round-trips byte-for-byte (tasks/phase-16.md
Task 16.7 DoD; same integration risk the Task 15.4 ``saw_vent`` extension
guarded). No committed turn carries a :class:`WhereaboutsClaim` — no meeting
template elicits the kind yet, so the additive guarantee is pinned against
the real committed corpus rather than a synthetic fixture. The no-new-flag
decision is pinned too: :class:`meetings.schemas.ContradictionRef` still
accepts ONLY its four existing kinds (a whereabouts LIE reuses the existing
``alibi_vs_sighting`` path, so no ``whereabouts_lie`` kind is minted).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    SightingRecord,
    WhereaboutsClaim,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries

# The committed 9p/2i meeting-heavy set (Tasks 7.8, 8.12): seed 0 carries
# several resolved meetings recorded under the current substrate but BEFORE
# the Task-16.7 ``whereabouts`` kind existed, so it is the faithful
# pre-whereabouts committed row for the additive-schema pin below.
_COMMITTED_9P2I_SEED_0 = (
    Path(__file__).resolve().parents[2]
    / "replays"
    / "samples"
    / "9p2i"
    / "replay-seed-0.jsonl"
)


def _whereabouts_turn() -> MeetingTurn:
    return MeetingTurn(
        turn_id="m-1:turn-0",
        turn_index=0,
        speaker="p-2",
        turn_kind="opening",
        reply_to=None,
        observations=(WhereaboutsClaim(type="whereabouts", tick=9, room="ELECTRICAL"),),
        claims=(),
        free_text="Roll call: I was in Electrical at tick 9.",
    )


class TestWhereaboutsClaim:
    def test_round_trips_through_the_turn_schema(self) -> None:
        turn = _whereabouts_turn()

        parsed = MeetingTurn.model_validate_json(turn.model_dump_json())

        assert parsed == turn
        observation = parsed.observations[0]
        assert isinstance(observation, WhereaboutsClaim)
        assert observation.room == "ELECTRICAL"
        assert observation.tick == 9

    def test_union_discriminates_on_whereabouts(self) -> None:
        parsed = MeetingTurn.model_validate(
            {
                "turn_id": "m-1:turn-0",
                "turn_index": 0,
                "speaker": "p-2",
                "turn_kind": "opening",
                "reply_to": None,
                "observations": [
                    {
                        "type": "whereabouts",
                        "tick": 9,
                        "room": "ELECTRICAL",
                    }
                ],
                "claims": [],
                "free_text": "roll call",
            }
        )

        assert isinstance(parsed.observations[0], WhereaboutsClaim)

    def test_no_subject_field_exists(self) -> None:
        # Deliberately NO subject field: a whereabouts claim is SELF-placement
        # only (the subject IS the speaker, turn.speaker), and vouching for
        # OTHERS is already SawPlayerObservation's job. Having no subject field
        # means there is no placeholder-subject failure class — nothing for the
        # self-alibi normalizer to rewrite, nothing for the roster chokepoint to
        # validate (the task contract's schema decision). A stray subject key is
        # rejected outright.
        with pytest.raises(ValidationError):
            WhereaboutsClaim.model_validate(
                {
                    "type": "whereabouts",
                    "tick": 9,
                    "room": "ELECTRICAL",
                    "subject": "p-5",
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
                            "type": "teleported",
                            "tick": 9,
                            "room": "ELECTRICAL",
                        }
                    ],
                    "claims": [],
                    "free_text": "unsure",
                }
            )


class TestSightingRecord:
    def test_shape_and_round_trip(self) -> None:
        record = SightingRecord(
            subject="p-5", room="MEDBAY", tick=14, co_present=("p-3", "p-4")
        )

        assert SightingRecord.model_validate_json(record.model_dump_json()) == record
        assert record.subject == "p-5"
        assert record.room == "MEDBAY"
        assert record.tick == 14
        assert record.co_present == ("p-3", "p-4")

    def test_co_present_defaults_to_empty(self) -> None:
        record = SightingRecord(subject="p-5", room="MEDBAY", tick=14)

        assert record.co_present == ()
        assert SightingRecord.model_validate_json(record.model_dump_json()) == record

    def test_frozen_and_extra_forbid(self) -> None:
        record = SightingRecord(subject="p-5", room="MEDBAY", tick=14)

        with pytest.raises(ValidationError):
            record.subject = "p-6"
        with pytest.raises(ValidationError):
            SightingRecord.model_validate(
                {"subject": "p-5", "room": "MEDBAY", "tick": 14, "phase": "enter"}
            )


class TestContradictionRefRejectsWhereaboutsKind:
    def test_whereabouts_lie_is_not_a_contradiction_kind(self) -> None:
        # The no-new-flag-kind pin: a LIE in a whereabouts claim is a degenerate
        # single-tick self-alibi, so it reuses the EXISTING alibi_vs_sighting
        # path — Task 16.7 mints no whereabouts_lie kind. ContradictionRef still
        # accepts only its four existing kinds; an invented kind fails validation.
        with pytest.raises(ValidationError):
            ContradictionRef(
                contradiction_id="contra:whereabouts_lie:0",
                kind="whereabouts_lie",  # type: ignore[arg-type]
                event_a_id="turn:m-1:turn-0:obs:0",
                event_b_id="turn:m-1:turn-1:obs:0",
                subjects=("p-2",),
                description="p-2's roll-call placement contradicted by a sighting.",
            )


class TestCommittedMeetingEntryStillParses:
    def test_committed_9p2i_seed_0_loads_and_round_trips(self) -> None:
        # The additive-union pin (Task 16.7 DoD): a COMMITTED meeting entry loads
        # through the extended schema and round-trips unchanged. Because the union
        # extension is additive, adding WhereaboutsClaim as a fifth member never
        # rejects the committed shape. The baseline-5 re-record (qwen3_6_27b.v3
        # prompts) now ELICITS whereabouts claims via the roll-call surface, so the
        # committed corpus exercises the new member directly — a stronger guarantee
        # than the pre-whereabouts shape it superseded (a committed shape that USES
        # the new kind round-trips, not merely one that predates it). Read the
        # committed path directly (no tmp_path) so it is pinned against the real
        # corpus.
        meetings = [
            entry
            for entry in read_all_entries(_COMMITTED_9P2I_SEED_0)
            if isinstance(entry, MeetingReplayEntry)
        ]

        assert meetings, "committed 9p2i seed 0 carries no meeting entry"
        for entry in meetings:
            transcript = entry.transcript
            assert isinstance(transcript, MeetingTranscript)
            # The whole entry re-validates through the extended schema (the
            # additive union member does not reject the committed shape) and the
            # parse round-trips exactly.
            assert (
                MeetingReplayEntry.model_validate_json(entry.model_dump_json()) == entry
            )
            # Every recorded turn — whereabouts-bearing or not — re-validates as-is
            # through the additive union.
            for turn in transcript.turns:
                assert MeetingTurn.model_validate(turn.model_dump()) == turn
        # The fifth member is exercised on the committed set (the v3 roll-call
        # elicitation): whereabouts claims are present and round-trip.
        whereabouts = [
            observation
            for entry in meetings
            for turn in entry.transcript.turns
            for observation in turn.observations
            if isinstance(observation, WhereaboutsClaim)
        ]
        assert whereabouts
