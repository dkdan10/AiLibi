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


class TestNonChronologicalAlibi:
    """Reversed ``from_tick``/``to_tick`` on an ``AlibiClaim`` (Task 7.10, gp-2).

    ``qwen2.5:7b-instruct`` emits an ``AlibiClaim`` with ``from_tick > to_tick``
    in ~6% of the committed 7p/2i set; the strict chronological validator on
    ``AlibiClaim`` rejects it, and (before this) the whole game aborted with no
    ``game_over``. The normalizer swaps the bounds *before* validation so the
    strict schema accepts the claim — the schema itself is NOT relaxed.
    """

    def _reversed_alibi_statement(self) -> dict[str, Any]:
        # The seed-36 repro shape: from_tick=8 > to_tick=1 inside a Statement.
        return {
            "statement_id": "s1",
            "speaker": "p-3",
            "tick": 11,
            "round_index": 0,
            "target": None,
            "claims": [
                {
                    "type": "alibi",
                    "subject": "p-3",
                    "from_tick": 8,
                    "to_tick": 1,
                    "room": "CAFETERIA",
                }
            ],
            "free_text": "I was around.",
        }

    def test_reversed_alibi_in_statement_is_swapped_and_validates(self) -> None:
        payload = self._reversed_alibi_statement()
        # Raw payload is a hard chronological-validator error.
        with pytest.raises(ValidationError):
            Statement.model_validate(payload)

        normalized = normalize_report_payload(payload, Statement)

        claim = normalized["claims"][0]
        # Bounds swapped (both tick values preserved), not coerced away.
        assert claim["from_tick"] == 1
        assert claim["to_tick"] == 8
        # Other fields untouched, and it now validates on the strict schema.
        assert claim["subject"] == "p-3"
        assert claim["room"] == "CAFETERIA"
        Statement.model_validate(normalized)

    def test_reversed_alibi_in_report_is_swapped_and_validates(self) -> None:
        # The repair fires wherever AlibiClaim is reached via the Claim union —
        # ReportDocument.claims as well as Statement.claims.
        payload: dict[str, Any] = {
            "agent_id": "p-3",
            "tick": 14,
            "observations": [],
            "claims": [
                {
                    "type": "alibi",
                    "subject": "p-3",
                    "from_tick": 9,
                    "to_tick": 1,
                    "room": "MEDBAY",
                }
            ],
            "free_text": "alibi",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["claims"][0]["from_tick"] == 1
        assert normalized["claims"][0]["to_tick"] == 9
        ReportDocument.model_validate(normalized)

    def test_chronological_alibi_is_deep_equal_no_op(self) -> None:
        payload = _valid_report()  # its alibi is already chronological (380..410)
        assert normalize_report_payload(payload, ReportDocument) == payload

    def test_equal_bounds_alibi_is_no_op(self) -> None:
        # from_tick == to_tick is a valid one-tick window: no swap, no change.
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 5,
            "observations": [],
            "claims": [
                {
                    "type": "alibi",
                    "subject": "p-1",
                    "from_tick": 5,
                    "to_tick": 5,
                    "room": "R",
                }
            ],
            "free_text": "f",
        }
        assert normalize_report_payload(payload, ReportDocument) == payload
        ReportDocument.model_validate(payload)

    def test_reversed_alibi_repair_does_not_mutate_input(self) -> None:
        payload = self._reversed_alibi_statement()
        before = copy.deepcopy(payload)
        normalize_report_payload(payload, Statement)
        assert payload == before  # pure function: input untouched

    def test_reversed_alibi_missing_other_field_still_fails_loud(self) -> None:
        # The swap fixes the ordering but never fabricates a missing required
        # field: a reversed alibi that ALSO omits ``room`` is salvaged on the
        # range but still fails validation — the "claim still malformed after
        # normalization fails" half of the DoD.
        payload: dict[str, Any] = {
            "agent_id": "p-1",
            "tick": 5,
            "observations": [],
            "claims": [
                {
                    "type": "alibi",
                    "subject": "p-1",
                    "from_tick": 8,
                    "to_tick": 1,
                    # ``room`` (required) is absent.
                }
            ],
            "free_text": "f",
        }
        normalized = normalize_report_payload(payload, ReportDocument)
        # Range was repaired...
        assert normalized["claims"][0]["from_tick"] == 1
        assert normalized["claims"][0]["to_tick"] == 8
        # ...but the missing required field still fails loud.
        with pytest.raises(ValidationError) as exc:
            ReportDocument.model_validate(normalized)
        assert any(err["type"] == "missing" for err in exc.value.errors())

    def _report_with_bounds(self, from_tick: Any, to_tick: Any) -> dict[str, Any]:
        return {
            "agent_id": "p-1",
            "tick": 5,
            "observations": [],
            "claims": [
                {
                    "type": "alibi",
                    "subject": "p-1",
                    "from_tick": from_tick,
                    "to_tick": to_tick,
                    "room": "R",
                }
            ],
            "free_text": "f",
        }

    def test_reversed_string_bounds_are_swapped_and_validate(self) -> None:
        # A model can emit tick bounds as JSON strings; Pydantic's int field
        # coerces "8"->8, so a reversed STRING range must be swapped too (the
        # exact-int guard would have missed it and degraded a salvageable claim).
        # The ORIGINAL string values are reordered; Pydantic coerces downstream.
        payload = self._report_with_bounds("8", "1")
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["claims"][0]["from_tick"] == "1"
        assert normalized["claims"][0]["to_tick"] == "8"
        ReportDocument.model_validate(normalized)

    def test_reversed_whole_float_bounds_are_swapped_and_validate(self) -> None:
        # Whole floats (8.0) coerce to int 8 in Pydantic, so a reversed
        # whole-float range is salvageable and must be swapped.
        payload = self._report_with_bounds(8.0, 1.0)
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["claims"][0]["from_tick"] == 1.0
        assert normalized["claims"][0]["to_tick"] == 8.0
        ReportDocument.model_validate(normalized)

    def test_reversed_mixed_str_int_bounds_are_swapped(self) -> None:
        payload = self._report_with_bounds("8", 1)
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["claims"][0]["from_tick"] == 1
        assert normalized["claims"][0]["to_tick"] == "8"
        ReportDocument.model_validate(normalized)

    def test_chronological_string_bounds_are_no_op(self) -> None:
        # Already chronological after coercion ("1" <= "8"): no swap, deep-equal.
        payload = self._report_with_bounds("1", "8")
        assert normalize_report_payload(payload, ReportDocument) == payload
        ReportDocument.model_validate(payload)

    def test_non_coercible_string_bound_not_swapped_and_fails_loud(self) -> None:
        # A non-numeric bound is not an int Pydantic accepts -> left untouched so
        # it still fails loud at validation (the normalizer never masks it).
        payload = self._report_with_bounds("abc", "1")
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized == payload
        with pytest.raises(ValidationError):
            ReportDocument.model_validate(normalized)

    def test_non_integer_float_bound_not_swapped(self) -> None:
        # Pydantic rejects a non-integer float for an int field, so 8.5 is not a
        # salvageable bound: leave it untouched (it fails validation regardless).
        payload = self._report_with_bounds(8.5, 1.0)
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["claims"][0]["from_tick"] == 8.5
        assert normalized["claims"][0]["to_tick"] == 1.0

    def test_bool_bounds_not_swapped(self) -> None:
        # A boolean is not a meaningful tick; it is excluded even though lax mode
        # would coerce True->1 / False->0. Left untouched (no swap).
        payload = self._report_with_bounds(True, False)
        normalized = normalize_report_payload(payload, ReportDocument)
        assert normalized["claims"][0]["from_tick"] is True
        assert normalized["claims"][0]["to_tick"] is False
