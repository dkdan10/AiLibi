"""Table tests for the pure report-normalization helper (Task 7.6).

``llm.report_normalize.normalize_report_payload`` is a pure function over a
parsed JSON value + a target schema. These tests pin its contract directly,
independent of any provider/transport: the diagnosed ``co_present``-on-
``found_body`` case, an already-valid no-op, a missing-required payload that
still fails loud, a non-union schema left untouched, and the residual-risk
wrong-discriminator case that is deliberately NOT repaired.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from llm.report_normalize import normalize_report_payload
from meetings.schemas import ReportDocument, Statement, VoteBallot


def _valid_report() -> dict[str, Any]:
    """A fully-valid ReportDocument payload (every variant exercised)."""

    return {
        "agent_id": "p-3",
        "tick": 412,
        "observations": [
            {
                "type": "saw_player",
                "tick": 380,
                "subject": "p-5",
                "room": "Electrical",
                "co_present": ["p-7"],
            },
            {"type": "found_body", "tick": 410, "body_of": "p-2", "room": "MedBay"},
            {
                "type": "completed_task",
                "tick": 395,
                "task_id": "wiring",
                "room": "Admin",
            },
        ],
        "claims": [
            {
                "type": "alibi",
                "subject": "p-3",
                "from_tick": 380,
                "to_tick": 410,
                "room": "Admin",
                "evidence": ["wiring"],
            },
            {
                "type": "accusation",
                "against": "p-5",
                "confidence": 0.4,
                "reason": "near body",
            },
            {
                "type": "corroboration",
                "supports": "p-1",
                "on_tick": 200,
                "reason": "shared task",
            },
        ],
        "free_text": "I was in Admin.",
    }


class TestDiagnosedFailure:
    """The exact failure Task 7.6 exists to fix."""

    def test_co_present_on_found_body_is_stripped_and_validates(self) -> None:
        payload: dict[str, Any] = {
            "agent_id": "p-3",
            "tick": 412,
            "observations": [
                {
                    "type": "found_body",
                    "tick": 410,
                    "body_of": "p-2",
                    "room": "MedBay",
                    # `co_present` is valid on `saw_player`, NOT on `found_body`.
                    "co_present": ["p-5"],
                }
            ],
            "claims": [],
            "free_text": "found a body",
        }
        # Raw payload is a hard validation error under extra="forbid".
        with pytest.raises(ValidationError):
            ReportDocument.model_validate(payload)

        normalized = normalize_report_payload(payload, ReportDocument)

        # The stray key is gone, the real fields survive, and it now validates.
        assert "co_present" not in normalized["observations"][0]
        assert normalized["observations"][0]["body_of"] == "p-2"
        assert normalized["observations"][0]["room"] == "MedBay"
        ReportDocument.model_validate(normalized)

    def test_input_payload_is_not_mutated(self) -> None:
        payload: dict[str, Any] = {
            "agent_id": "p-3",
            "tick": 1,
            "observations": [
                {
                    "type": "found_body",
                    "tick": 1,
                    "body_of": "p-2",
                    "room": "R",
                    "co_present": ["p-5"],
                }
            ],
            "claims": [],
            "free_text": "x",
        }
        before = copy.deepcopy(payload)
        normalize_report_payload(payload, ReportDocument)
        assert payload == before  # pure function: no in-place mutation

    def test_stray_key_on_claim_variant_is_stripped(self) -> None:
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 5,
            "observations": [],
            "claims": [
                {
                    "type": "accusation",
                    "against": "p-2",
                    "confidence": 0.5,
                    "reason": "r",
                    # not declared on AccusationClaim
                    "bogus": 1,
                }
            ],
            "free_text": "f",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        assert "bogus" not in normalized["claims"][0]
        ReportDocument.model_validate(normalized)

    def test_statement_nested_claim_extra_is_stripped(self) -> None:
        payload: dict[str, Any] = {
            "statement_id": "s1",
            "speaker": "p-1",
            "tick": 5,
            "round_index": 0,
            "target": "p-2",
            "claims": [
                {
                    "type": "accusation",
                    "against": "p-2",
                    "confidence": 0.5,
                    "reason": "r",
                    "extra": 9,
                }
            ],
            "free_text": "f",
        }
        normalized = normalize_report_payload(payload, Statement)
        assert "extra" not in normalized["claims"][0]
        Statement.model_validate(normalized)


class TestNoOpOnValid:
    """An already-valid payload is returned deep-equal (a byte-identical no-op)."""

    def test_valid_report_is_deep_equal_no_op(self) -> None:
        payload = _valid_report()
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized == payload

    def test_valid_report_keeps_legitimate_co_present(self) -> None:
        payload = _valid_report()
        normalized = normalize_report_payload(payload, ReportDocument)
        # saw_player legitimately declares co_present — it must NOT be stripped.
        assert normalized["observations"][0]["co_present"] == ["p-7"]

    def test_valid_vote_ballot_no_op(self) -> None:
        payload: dict[str, Any] = {
            "voter": "p-1",
            "target": "SKIP",
            "confidence": 0.5,
            "primary_reason_id": None,
            "considered_alternatives": ["p-2"],
            "rationale_text": "unsure",
        }
        VoteBallot.model_validate(payload)
        assert normalize_report_payload(payload, VoteBallot) == payload

    def test_empty_collections_no_op(self) -> None:
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 0,
            "observations": [],
            "claims": [],
            "free_text": "",
        }
        assert normalize_report_payload(payload, ReportDocument) == payload


class TestDoesNotMaskGenuineErrors:
    """Normalization salvages misplaced keys; it never fabricates fields."""

    def test_missing_required_field_still_fails_loud(self) -> None:
        payload: dict[str, Any] = {
            "agent_id": "p-3",
            "tick": 412,
            "observations": [
                # `body_of` is required on found_body and is absent.
                {"type": "found_body", "tick": 410, "room": "MedBay"}
            ],
            "claims": [],
            "free_text": "x",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        with pytest.raises(ValidationError) as exc:
            ReportDocument.model_validate(normalized)
        assert any(err["type"] == "missing" for err in exc.value.errors())

    def test_top_level_extra_key_is_not_stripped(self) -> None:
        # Conservative: only discriminated-union *variant* extras are pruned.
        # A stray top-level key on a plain model is left in place so validation
        # still fails loud (the diagnosed failure is a variant key, not this).
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 0,
            "observations": [],
            "claims": [],
            "free_text": "",
            "made_up_top_level": 123,
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["made_up_top_level"] == 123
        with pytest.raises(ValidationError):
            ReportDocument.model_validate(normalized)


class TestResidualRisk:
    """A wrong/unknown discriminator is trusted, not repaired (documented risk)."""

    def test_unknown_discriminator_value_left_untouched(self) -> None:
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 0,
            "observations": [{"type": "teleported", "tick": 1, "whatever": 2}],
            "claims": [],
            "free_text": "",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        # Unknown variant: the observation is left exactly as-is (we do not infer
        # a variant from body shape), so it still fails loud downstream.
        assert normalized["observations"][0] == {
            "type": "teleported",
            "tick": 1,
            "whatever": 2,
        }
        with pytest.raises(ValidationError):
            ReportDocument.model_validate(normalized)

    def test_mismatched_discriminator_strips_to_named_variant_only(self) -> None:
        # `type: saw_player` but carrying a `found_body` body field. We strip to
        # the NAMED variant (saw_player), dropping body_of — we never re-label it
        # found_body. It does not get coerced into a valid found_body.
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 0,
            "observations": [
                {
                    "type": "saw_player",
                    "tick": 1,
                    "subject": "p-2",
                    "room": "R",
                    "body_of": "p-9",
                }
            ],
            "claims": [],
            "free_text": "",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        assert "body_of" not in normalized["observations"][0]
        assert normalized["observations"][0]["type"] == "saw_player"

    def test_genuinely_mislabeled_report_stays_a_failed_call(self) -> None:
        # The contract's residual-risk example proper: `type: saw_player` on a
        # `found_body`-SHAPED body (no `subject`). Stripping to the named variant
        # cannot supply the missing required `subject`, so it remains a
        # ValidationError (FailedCall) — the normalizer never re-infers the
        # variant from body shape. This pins that the residual risk is preserved.
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 0,
            "observations": [
                {"type": "saw_player", "tick": 1, "body_of": "p-9", "room": "R"}
            ],
            "claims": [],
            "free_text": "",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        with pytest.raises(ValidationError) as exc:
            ReportDocument.model_validate(normalized)
        assert any(err["type"] == "missing" for err in exc.value.errors())

    def test_unhashable_discriminator_left_untouched_not_typeerror(self) -> None:
        # A malformed discriminator (`{"type": ["found_body"]}`) is unhashable;
        # the variant-map lookup must not leak a TypeError. The normalizer leaves
        # the payload untouched so normal validation raises ValidationError.
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 0,
            "observations": [
                {"type": ["found_body"], "tick": 1, "body_of": "p-2", "room": "R"}
            ],
            "claims": [],
            "free_text": "",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["observations"][0]["type"] == ["found_body"]
        with pytest.raises(ValidationError):
            ReportDocument.model_validate(normalized)


class TestNonUnionSchemaUntouched:
    """Schemas with no discriminated unions are left entirely alone."""

    def test_plain_model_no_op(self) -> None:
        class Plain(BaseModel):
            model_config = ConfigDict(extra="forbid")

            a: int
            b: str

        payload: dict[str, Any] = {"a": 1, "b": "z"}
        assert normalize_report_payload(payload, Plain) == payload

    def test_plain_model_extra_key_not_stripped(self) -> None:
        class Plain(BaseModel):
            model_config = ConfigDict(extra="forbid")

            a: int

        payload: dict[str, Any] = {"a": 1, "c": 99}
        # No discriminated union anywhere -> untouched (extra survives, fails loud).
        assert normalize_report_payload(payload, Plain) == payload
        with pytest.raises(ValidationError):
            Plain.model_validate(payload)

    def test_non_dict_payload_returned_unchanged(self) -> None:
        assert normalize_report_payload([1, 2, 3], ReportDocument) == [1, 2, 3]
        assert (
            normalize_report_payload("not-an-object", ReportDocument) == "not-an-object"
        )
