"""Tests for the shared meeting / output schemas (Task 3.2).

These tests pin the schema surface that strategic LLM outputs target
(DESIGN.md §5.3, §5.5, Appendix A) and the engine-free DTO that
:class:`MeetingManager` will return in Task 3.8. The agent-side
re-export module (``agents/strategic/output_schemas.py``) must remain a
pure re-export -- never a duplicate -- so the round-trip identity
assertions below act as an anti-drift guard.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agents.strategic import output_schemas as agent_output_schemas
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    ObservationClaim,
    ReportDocument,
    SawPlayerObservation,
    Statement,
    VoteBallot,
)


def _report_document(**overrides: object) -> ReportDocument:
    defaults: dict[str, object] = {
        "agent_id": "p-3",
        "tick": 412,
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
            "I was doing wiring in Admin from tick 380. "
            "I saw p-5 head toward Electrical with p-7. "
            "p-2's body was in MedBay; p-5 was in the right corridor."
        ),
    }
    defaults.update(overrides)
    return ReportDocument.model_validate(defaults)


def _vote_ballot(**overrides: object) -> VoteBallot:
    defaults: dict[str, object] = {
        "voter": "p-3",
        "target": "p-5",
        "confidence": 0.65,
        "primary_reason_id": "stmt_12",
        "considered_alternatives": ("p-7",),
        "rationale_text": (
            "p-5's claim to be in Electrical is contradicted by p-1's alibi..."
        ),
    }
    defaults.update(overrides)
    return VoteBallot.model_validate(defaults)


class TestReportDocument:
    def test_design_md_example_round_trips_through_pydantic(self) -> None:
        # DESIGN.md §5.3 worked example. The structured-plus-free-text
        # contract round-trips through ``model_dump`` and ``model_validate``
        # without losing or renaming fields.
        report = _report_document()

        dumped = report.model_dump(mode="json")

        assert dumped["agent_id"] == "p-3"
        assert dumped["tick"] == 412
        assert dumped["observations"][0]["type"] == "saw_player"
        assert dumped["observations"][2]["type"] == "found_body"
        assert dumped["claims"][0]["type"] == "alibi"
        assert dumped["claims"][1]["type"] == "accusation"
        assert ReportDocument.model_validate(dumped) == report

    def test_observations_use_discriminated_union(self) -> None:
        # The ``type`` discriminator lets Pydantic dispatch to the right
        # observation subclass and reject malformed entries.
        with pytest.raises(ValidationError):
            ReportDocument.model_validate(
                {
                    "agent_id": "p-3",
                    "tick": 1,
                    "observations": [{"type": "saw_player"}],
                    "claims": [],
                    "free_text": "",
                }
            )

    def test_extra_fields_are_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ReportDocument.model_validate(
                {
                    "agent_id": "p-3",
                    "tick": 1,
                    "observations": [],
                    "claims": [],
                    "free_text": "",
                    "unexpected": True,
                }
            )

    def test_default_collections_are_empty_tuples(self) -> None:
        report = ReportDocument(agent_id="p-1", tick=0, free_text="")

        assert report.observations == ()
        assert report.claims == ()

    def test_report_document_is_frozen(self) -> None:
        report = _report_document()

        with pytest.raises(ValidationError):
            report.agent_id = "p-9"


class TestStatement:
    def test_target_is_optional_for_defensive_statements(self) -> None:
        statement = Statement(
            statement_id="stmt_1",
            speaker="p-3",
            tick=420,
            round_index=0,
            target=None,
            claims=(),
            free_text="I was with p-1 in Storage between tick 145 and 160.",
        )

        assert statement.target is None
        assert statement.round_index == 0

    def test_accusation_statement_carries_target_and_claims(self) -> None:
        statement = Statement(
            statement_id="stmt_4",
            speaker="p-3",
            tick=422,
            round_index=1,
            target="p-5",
            claims=(
                AccusationClaim(
                    type="accusation",
                    against="p-5",
                    confidence=0.6,
                    reason="contradicted alibi",
                ),
            ),
            free_text="I think p-5 is the impostor because their alibi conflicts.",
        )

        assert statement.target == "p-5"
        accusation = statement.claims[0]
        assert isinstance(accusation, AccusationClaim)
        assert accusation.against == "p-5"


class TestVoteBallot:
    def test_design_md_voting_example_validates(self) -> None:
        ballot = _vote_ballot()

        assert ballot.target == "p-5"
        assert ballot.confidence == pytest.approx(0.65)
        assert ballot.primary_reason_id == "stmt_12"
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
            event_a_id="claim:p-4:alibi:400-410",
            event_b_id="stmt:p-6:tick-405:saw_player:p-4",
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
                    event_a_id="claim:p-4:alibi:400-410",
                    event_b_id="stmt:p-6:tick-405:saw_player:p-4",
                    subjects=("p-4",),
                    description="alibi-vs-sighting conflict",
                ),
            ),
            transcript=MeetingTranscript(
                reports=(_report_document(),),
                statements=(
                    Statement(
                        statement_id="stmt_1",
                        speaker="p-3",
                        tick=420,
                        round_index=0,
                        target=None,
                        free_text="defensive opener",
                    ),
                ),
            ),
        )

    def test_round_trip_preserves_every_subschema(self) -> None:
        result = self._result()

        dumped = result.model_dump(mode="json")

        assert MeetingResult.model_validate(dumped) == result
        assert dumped["outcome"] == "EJECTED"
        assert dumped["ejected_player_id"] == "p-5"
        assert len(dumped["ballots"]) == 2

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
        assert result.transcript.reports == ()
        assert result.transcript.statements == ()


class TestAgentOutputSchemasReExport:
    """``agents/strategic/output_schemas.py`` must re-export -- not duplicate."""

    def test_re_export_modules_are_object_identical(self) -> None:
        # Re-export uses ``from meetings.schemas import ...``; the class
        # objects in both modules must be the same Python objects.
        assert agent_output_schemas.ReportDocument is ReportDocument
        assert agent_output_schemas.Statement is Statement
        assert agent_output_schemas.VoteBallot is VoteBallot
        assert agent_output_schemas.MeetingResult is MeetingResult
        assert agent_output_schemas.ContradictionRef is ContradictionRef
        assert agent_output_schemas.MeetingTranscript is MeetingTranscript
        assert agent_output_schemas.ObservationClaim is ObservationClaim
        assert agent_output_schemas.Claim is Claim
        assert agent_output_schemas.SawPlayerObservation is SawPlayerObservation
        assert agent_output_schemas.CompletedTaskObservation is CompletedTaskObservation
        assert agent_output_schemas.FoundBodyObservation is FoundBodyObservation
        assert agent_output_schemas.AlibiClaim is AlibiClaim
        assert agent_output_schemas.AccusationClaim is AccusationClaim
        assert agent_output_schemas.CorroborationClaim is CorroborationClaim

    def test_re_export_does_not_add_independent_definitions(self) -> None:
        # If a second-source schema ever sneaks in, the union types break.
        report = agent_output_schemas.ReportDocument.model_validate_json(
            _report_document().model_dump_json()
        )
        assert isinstance(report, ReportDocument)
