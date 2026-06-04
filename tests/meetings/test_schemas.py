"""Tests for the shared meeting / output schemas (Task 8.7).

These tests pin the schema surface that strategic LLM outputs target
(DESIGN.md §5.2, §5.3, §5.5, Appendix A) under the reactive
accusation-chain record shape: one ordered ``transcript.turns`` list of
:class:`MeetingTurn`, where the reporter's observations live on the
``opening`` turn and the old ``(reports, statements)`` pair is gone.

The agent-side re-export module (``agents/strategic/output_schemas.py``)
is reshaped in Task 8.8; its re-export anti-drift test moves there with
it, so it is intentionally not exercised here (importing it would pull in
the pre-8.8 ``ReportDocument`` / ``Statement`` re-exports this task
removed).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    CompletedTaskObservation,
    ContradictionRef,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    VoteBallot,
)


def _opening_turn(**overrides: object) -> MeetingTurn:
    # DESIGN.md §5.3 worked example (turn_kind="opening").
    defaults: dict[str, object] = {
        "turn_id": "m-7:turn-0",
        "turn_index": 0,
        "speaker": "p-3",
        "turn_kind": "opening",
        "reply_to": None,
        "observations": (
            SawPlayerObservation(
                type="saw_player",
                tick=380,
                subject="p-5",
                room="ELECTRICAL",
                co_present=("p-7",),
            ),
            CompletedTaskObservation(
                type="completed_task",
                tick=395,
                task_id="wiring_admin",
                room="ADMIN",
            ),
            FoundBodyObservation(
                type="found_body",
                tick=410,
                body_of="p-2",
                room="MEDBAY",
            ),
        ),
        "claims": (
            AlibiClaim(
                type="alibi",
                subject="p-3",
                from_tick=380,
                to_tick=410,
                room="ADMIN",
                evidence=("wiring_admin", "saw_player:p-5"),
            ),
            AccusationClaim(
                type="accusation",
                against="p-5",
                confidence=0.4,
                reason="near MedBay corridor minutes before kill",
            ),
        ),
        "free_text": (
            "I found p-2 in MedBay. I was wiring in Admin from 380 and saw "
            "p-5 head to Electrical with p-7 -- p-5 was near that corridor."
        ),
    }
    defaults.update(overrides)
    return MeetingTurn.model_validate(defaults)


def _vote_ballot(**overrides: object) -> VoteBallot:
    defaults: dict[str, object] = {
        "voter": "p-3",
        "target": "p-5",
        "confidence": 0.65,
        "primary_reason_id": "m-7:turn-4",
        "considered_alternatives": ("p-7",),
        "rationale_text": (
            "p-5's claim to be in Electrical is contradicted by p-1's alibi..."
        ),
    }
    defaults.update(overrides)
    return VoteBallot.model_validate(defaults)


class TestMeetingTurn:
    def test_design_md_opening_example_round_trips(self) -> None:
        # DESIGN.md §5.3 worked example; the structured-plus-free-text
        # contract round-trips through model_dump / model_validate.
        turn = _opening_turn()

        dumped = turn.model_dump(mode="json")

        assert dumped["turn_id"] == "m-7:turn-0"
        assert dumped["turn_index"] == 0
        assert dumped["turn_kind"] == "opening"
        assert dumped["reply_to"] is None
        assert dumped["observations"][0]["type"] == "saw_player"
        assert dumped["observations"][2]["type"] == "found_body"
        assert dumped["claims"][0]["type"] == "alibi"
        assert dumped["claims"][1]["type"] == "accusation"
        assert MeetingTurn.model_validate(dumped) == turn

    def test_reply_turn_links_to_prior_turn(self) -> None:
        reply = MeetingTurn(
            turn_id="m-7:turn-1",
            turn_index=1,
            speaker="p-5",
            turn_kind="reply",
            reply_to="m-7:turn-0",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-3",
                    confidence=0.5,
                    reason="counter-accusation",
                ),
            ),
            free_text="I was nowhere near MedBay; p-3 is deflecting.",
        )

        assert reply.turn_kind == "reply"
        assert reply.reply_to == "m-7:turn-0"

    def test_opt_in_turn_is_terminal(self) -> None:
        opt_in = MeetingTurn(
            turn_id="m-7:turn-3",
            turn_index=3,
            speaker="p-9",
            turn_kind="opt_in",
            reply_to=None,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=400, subject="p-5", room="MEDBAY"
                ),
            ),
            free_text="I saw p-5 near MedBay around 400.",
        )

        assert opt_in.turn_kind == "opt_in"
        assert opt_in.reply_to is None

    def test_turn_kind_is_constrained(self) -> None:
        with pytest.raises(ValidationError):
            MeetingTurn.model_validate(
                {
                    "turn_id": "m-1:turn-0",
                    "turn_index": 0,
                    "speaker": "p-1",
                    "turn_kind": "monologue",
                    "reply_to": None,
                    "free_text": "",
                }
            )

    def test_observations_use_discriminated_union(self) -> None:
        with pytest.raises(ValidationError):
            MeetingTurn.model_validate(
                {
                    "turn_id": "m-1:turn-0",
                    "turn_index": 0,
                    "speaker": "p-3",
                    "turn_kind": "opening",
                    "reply_to": None,
                    "observations": [{"type": "saw_player"}],
                    "claims": [],
                    "free_text": "",
                }
            )

    def test_extra_fields_are_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MeetingTurn.model_validate(
                {
                    "turn_id": "m-1:turn-0",
                    "turn_index": 0,
                    "speaker": "p-3",
                    "turn_kind": "opening",
                    "reply_to": None,
                    "observations": [],
                    "claims": [],
                    "free_text": "",
                    "round_index": 0,
                }
            )

    def test_default_collections_are_empty_tuples(self) -> None:
        turn = MeetingTurn(
            turn_id="m-1:turn-0",
            turn_index=0,
            speaker="p-1",
            turn_kind="opening",
            reply_to=None,
            free_text="",
        )

        assert turn.observations == ()
        assert turn.claims == ()

    def test_turn_is_frozen(self) -> None:
        turn = _opening_turn()

        with pytest.raises(ValidationError):
            turn.speaker = "p-9"


class TestAlibiClaimChronology:
    """Codex P2: alibi tick ranges must be chronological.

    Reversed ranges silently corrupt DESIGN.md §5.4 contradiction
    detection (which indexes alibis by ``(agent, tick_range, location)``);
    pin the fail-loud behavior at the schema boundary.
    """

    def test_equal_from_and_to_tick_is_allowed(self) -> None:
        claim = AlibiClaim(
            type="alibi",
            subject="p-3",
            from_tick=400,
            to_tick=400,
            room="ADMIN",
        )

        assert claim.from_tick == claim.to_tick == 400

    def test_chronological_range_is_allowed(self) -> None:
        claim = AlibiClaim(
            type="alibi",
            subject="p-3",
            from_tick=380,
            to_tick=410,
            room="ADMIN",
        )

        assert claim.from_tick == 380
        assert claim.to_tick == 410

    def test_reversed_range_is_rejected_at_parse_time(self) -> None:
        with pytest.raises(ValidationError, match="chronological"):
            AlibiClaim(
                type="alibi",
                subject="p-3",
                from_tick=410,
                to_tick=380,
                room="ADMIN",
            )

    def test_reversed_range_inside_turn_is_rejected(self) -> None:
        # The chronology invariant also applies when ``AlibiClaim`` is
        # parsed via the discriminated union inside a ``MeetingTurn``.
        with pytest.raises(ValidationError, match="chronological"):
            MeetingTurn.model_validate(
                {
                    "turn_id": "m-1:turn-0",
                    "turn_index": 0,
                    "speaker": "p-3",
                    "turn_kind": "opening",
                    "reply_to": None,
                    "observations": [],
                    "claims": [
                        {
                            "type": "alibi",
                            "subject": "p-3",
                            "from_tick": 410,
                            "to_tick": 380,
                            "room": "ADMIN",
                            "evidence": [],
                        }
                    ],
                    "free_text": "",
                }
            )


class TestVoteBallot:
    def test_design_md_voting_example_validates(self) -> None:
        ballot = _vote_ballot()

        assert ballot.target == "p-5"
        assert ballot.confidence == pytest.approx(0.65)
        # primary_reason_id references a MeetingTurn turn_id (DESIGN.md §5.5).
        assert ballot.primary_reason_id == "m-7:turn-4"
        assert ballot.considered_alternatives == ("p-7",)

    def test_skip_target_is_allowed(self) -> None:
        ballot = _vote_ballot(
            target="SKIP",
            primary_reason_id=None,
            considered_alternatives=(),
        )

        assert ballot.target == "SKIP"
        assert ballot.primary_reason_id is None

    def test_confidence_must_be_in_unit_interval(self) -> None:
        with pytest.raises(ValidationError):
            _vote_ballot(confidence=-0.1)
        with pytest.raises(ValidationError):
            _vote_ballot(confidence=1.1)


class TestContradictionRef:
    def test_contradiction_ref_round_trips(self) -> None:
        contradiction = ContradictionRef(
            contradiction_id="c-1",
            kind="alibi_vs_sighting",
            event_a_id="turn:m-7:turn-0:claim:0",
            event_b_id="turn:m-7:turn-2:obs:0",
            subjects=("p-4",),
            description="p-4 alibi places them in Storage; p-6 saw them in Cafeteria.",
        )

        dumped = contradiction.model_dump(mode="json")

        assert ContradictionRef.model_validate(dumped) == contradiction

    def test_kind_is_constrained_to_known_values(self) -> None:
        with pytest.raises(ValidationError):
            ContradictionRef.model_validate(
                {
                    "contradiction_id": "c-1",
                    "kind": "made_up",
                    "event_a_id": "a",
                    "event_b_id": "b",
                    "subjects": ["p-1"],
                    "description": "",
                }
            )


class TestMeetingTranscript:
    def test_default_turns_is_empty_tuple(self) -> None:
        transcript = MeetingTranscript()

        assert transcript.turns == ()

    def test_turns_round_trip(self) -> None:
        transcript = MeetingTranscript(turns=(_opening_turn(),))

        dumped = transcript.model_dump(mode="json")

        assert MeetingTranscript.model_validate(dumped) == transcript
        assert dumped["turns"][0]["turn_kind"] == "opening"

    def test_old_reports_statements_shape_is_rejected(self) -> None:
        # The byte-breaker (Task 8.7): an old committed transcript carrying
        # ``reports`` / ``statements`` keys fails ``extra='forbid'`` against
        # the new ``turns``-only shape and is re-recorded in Task 8.12.
        with pytest.raises(ValidationError):
            MeetingTranscript.model_validate({"reports": [], "statements": []})


class TestMeetingResult:
    def _result(self) -> MeetingResult:
        return MeetingResult(
            meeting_id="m-1",
            triggered_by="p-3",
            trigger_tick=410,
            outcome="EJECTED",
            ejected_player_id="p-5",
            ballots=(
                _vote_ballot(),
                _vote_ballot(voter="p-7", target="p-5"),
            ),
            contradictions=(
                ContradictionRef(
                    contradiction_id="c-1",
                    kind="alibi_vs_sighting",
                    event_a_id="turn:m-1:turn-0:claim:0",
                    event_b_id="turn:m-1:turn-2:obs:0",
                    subjects=("p-4",),
                    description="alibi-vs-sighting conflict",
                ),
            ),
            transcript=MeetingTranscript(turns=(_opening_turn(),)),
        )

    def test_round_trip_preserves_every_subschema(self) -> None:
        result = self._result()

        dumped = result.model_dump(mode="json")

        assert MeetingResult.model_validate(dumped) == result
        assert dumped["outcome"] == "EJECTED"
        assert dumped["ejected_player_id"] == "p-5"
        assert len(dumped["ballots"]) == 2
        assert dumped["transcript"]["turns"][0]["turn_kind"] == "opening"

    def test_skip_outcome_has_no_ejected_player(self) -> None:
        result = MeetingResult(
            meeting_id="m-2",
            triggered_by="p-3",
            trigger_tick=410,
            outcome="SKIPPED",
            ejected_player_id=None,
            ballots=(),
            transcript=MeetingTranscript(),
        )

        assert result.ejected_player_id is None
        assert result.contradictions == ()
        assert result.transcript.turns == ()

    def test_ejected_outcome_without_ejected_id_is_rejected(self) -> None:
        # Codex P1: enforce the outcome/ejection invariant at parse time.
        with pytest.raises(ValidationError, match="EJECTED"):
            MeetingResult(
                meeting_id="m-4",
                triggered_by="p-3",
                trigger_tick=410,
                outcome="EJECTED",
                ejected_player_id=None,
                ballots=(),
                transcript=MeetingTranscript(),
            )

    def test_skipped_outcome_with_ejected_id_is_rejected(self) -> None:
        with pytest.raises(ValidationError, match="SKIPPED"):
            MeetingResult(
                meeting_id="m-5",
                triggered_by="p-3",
                trigger_tick=410,
                outcome="SKIPPED",
                ejected_player_id="p-5",
                ballots=(),
                transcript=MeetingTranscript(),
            )

    def test_unknown_outcome_string_is_rejected(self) -> None:
        # ``MeetingOutcome`` is the closed set ``{EJECTED, SKIPPED}``; any
        # other value (including the previously-rejected ``"TIE"``) must fail
        # Pydantic validation.
        with pytest.raises(ValidationError):
            MeetingResult.model_validate(
                {
                    "meeting_id": "m-7",
                    "triggered_by": "p-3",
                    "trigger_tick": 410,
                    "outcome": "TIE",
                    "ejected_player_id": None,
                    "ballots": [],
                    "contradictions": [],
                    "transcript": {"turns": []},
                }
            )
