from __future__ import annotations

import math

import pytest

from llm.budget import BudgetExceededError, BudgetSnapshot, GameBudget
from llm.client import LLMResponse, TokenUsage


def _usage(*, input_tokens: int = 0, output_tokens: int = 0) -> TokenUsage:
    return TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens)


def _response(
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
) -> LLMResponse:
    return LLMResponse(
        text="ok",
        usage=_usage(input_tokens=input_tokens, output_tokens=output_tokens),
        cost_usd=cost_usd,
        model="fake-meeting",
    )


class TestBudgetSnapshot:
    def test_initial_snapshot_reports_zero_spend(self) -> None:
        budget = GameBudget()

        snapshot = budget.snapshot()

        assert snapshot.cost_usd == 0.0
        assert snapshot.input_tokens == 0
        assert snapshot.output_tokens == 0

    def test_remaining_fields_reflect_caps(self) -> None:
        budget = GameBudget(
            max_cost_usd=0.30,
            max_input_tokens=10_000,
            max_output_tokens=2_000,
        )

        snapshot = budget.snapshot()

        assert snapshot.remaining_cost_usd == pytest.approx(0.30)
        assert snapshot.remaining_input_tokens == 10_000
        assert snapshot.remaining_output_tokens == 2_000


class TestBudgetCharge:
    def test_charge_accumulates_running_totals(self) -> None:
        budget = GameBudget(
            max_cost_usd=1.0,
            max_input_tokens=10_000,
            max_output_tokens=2_000,
        )

        snapshot = budget.charge(
            usage=_usage(input_tokens=100, output_tokens=20),
            cost_usd=0.10,
        )

        assert isinstance(snapshot, BudgetSnapshot)
        assert snapshot.cost_usd == pytest.approx(0.10)
        assert snapshot.input_tokens == 100
        assert snapshot.output_tokens == 20

    def test_charge_response_extracts_usage_and_cost(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)

        snapshot = budget.charge_response(
            _response(input_tokens=10, output_tokens=4, cost_usd=0.01),
        )

        assert snapshot.cost_usd == pytest.approx(0.01)
        assert snapshot.input_tokens == 10
        assert snapshot.output_tokens == 4

    def test_multiple_charges_sum_correctly(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)

        budget.charge(usage=_usage(input_tokens=10), cost_usd=0.05)
        budget.charge(usage=_usage(output_tokens=20), cost_usd=0.07)

        snapshot = budget.snapshot()

        assert snapshot.cost_usd == pytest.approx(0.12)
        assert snapshot.input_tokens == 10
        assert snapshot.output_tokens == 20


class TestBudgetFailLoudOnOverrun:
    def test_cost_overrun_raises_typed_exception(self) -> None:
        budget = GameBudget(max_cost_usd=0.10)
        budget.charge(usage=_usage(), cost_usd=0.09)

        with pytest.raises(BudgetExceededError) as excinfo:
            budget.charge(usage=_usage(), cost_usd=0.02)

        assert excinfo.value.dimension == "cost_usd"
        assert excinfo.value.cap == pytest.approx(0.10)
        assert excinfo.value.current == pytest.approx(0.09)
        assert excinfo.value.delta == pytest.approx(0.02)
        assert budget.snapshot().cost_usd == pytest.approx(0.11)

    def test_input_token_overrun_raises_typed_exception(self) -> None:
        budget = GameBudget(
            max_cost_usd=1_000.0,
            max_input_tokens=100,
        )
        budget.charge(usage=_usage(input_tokens=80), cost_usd=0.0)

        with pytest.raises(BudgetExceededError) as excinfo:
            budget.charge(usage=_usage(input_tokens=30), cost_usd=0.0)

        assert excinfo.value.dimension == "input_tokens"
        assert budget.snapshot().input_tokens == 110

    def test_output_token_overrun_raises_typed_exception(self) -> None:
        budget = GameBudget(
            max_cost_usd=1_000.0,
            max_output_tokens=50,
        )
        budget.charge(usage=_usage(output_tokens=40), cost_usd=0.0)

        with pytest.raises(BudgetExceededError) as excinfo:
            budget.charge(usage=_usage(output_tokens=20), cost_usd=0.0)

        assert excinfo.value.dimension == "output_tokens"
        assert budget.snapshot().output_tokens == 60

    def test_overrun_records_all_incurred_spend_and_blocks_new_calls(self) -> None:
        budget = GameBudget(max_cost_usd=0.10)
        budget.charge(usage=_usage(), cost_usd=0.09)

        with pytest.raises(BudgetExceededError):
            budget.charge(
                usage=_usage(input_tokens=80, output_tokens=10), cost_usd=0.02
            )
        snapshot = budget.snapshot()

        assert snapshot.cost_usd == pytest.approx(0.11)
        assert snapshot.input_tokens == 80
        assert snapshot.output_tokens == 10
        assert snapshot.remaining_cost_usd == pytest.approx(-0.01)
        with pytest.raises(BudgetExceededError):
            budget.preflight(usage=_usage(), cost_usd=0.0)
        assert budget.snapshot() == snapshot

    def test_exact_cap_is_allowed_not_an_overrun(self) -> None:
        budget = GameBudget(max_cost_usd=0.10)

        snapshot = budget.charge(usage=_usage(), cost_usd=0.10)

        assert snapshot.cost_usd == pytest.approx(0.10)


class TestPreflight:
    def test_preflight_does_not_mutate_state(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)
        before = budget.snapshot()

        budget.preflight(usage=_usage(input_tokens=10), cost_usd=0.01)

        after = budget.snapshot()
        assert before == after

    def test_preflight_raises_before_a_doomed_call(self) -> None:
        budget = GameBudget(max_cost_usd=0.05)

        with pytest.raises(BudgetExceededError) as excinfo:
            budget.preflight(usage=_usage(), cost_usd=0.10)

        assert excinfo.value.dimension == "cost_usd"

    def test_preflight_against_token_caps(self) -> None:
        budget = GameBudget(
            max_cost_usd=1_000.0,
            max_input_tokens=5,
        )

        with pytest.raises(BudgetExceededError) as excinfo:
            budget.preflight(usage=_usage(input_tokens=10), cost_usd=0.0)

        assert excinfo.value.dimension == "input_tokens"


class TestChargeInputValidation:
    def test_nan_cost_is_rejected(self) -> None:
        budget = GameBudget()

        with pytest.raises(ValueError, match="cost_usd"):
            budget.charge(usage=_usage(), cost_usd=math.nan)

        # State stays clean.
        assert budget.snapshot().cost_usd == 0.0

    def test_inf_cost_is_rejected(self) -> None:
        budget = GameBudget()

        with pytest.raises(ValueError, match="finite"):
            budget.charge(usage=_usage(), cost_usd=math.inf)

    def test_negative_cost_is_rejected(self) -> None:
        budget = GameBudget()
        budget.charge(usage=_usage(), cost_usd=0.05)
        before = budget.snapshot()

        with pytest.raises(ValueError, match="cost_usd"):
            budget.charge(usage=_usage(), cost_usd=-0.01)

        # A negative delta must NOT free budget; running total is unchanged.
        assert budget.snapshot() == before

    def test_negative_input_tokens_rejected(self) -> None:
        budget = GameBudget()

        with pytest.raises(ValueError, match="input_tokens"):
            budget.charge(usage=_usage(input_tokens=-1), cost_usd=0.0)

    def test_negative_output_tokens_rejected(self) -> None:
        budget = GameBudget()

        with pytest.raises(ValueError, match="output_tokens"):
            budget.charge(usage=_usage(output_tokens=-1), cost_usd=0.0)


class TestBudgetValidation:
    def test_negative_max_cost_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_cost_usd"):
            GameBudget(max_cost_usd=-0.01)

    def test_negative_max_input_tokens_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_input_tokens"):
            GameBudget(max_input_tokens=-1)

    def test_negative_max_output_tokens_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_output_tokens"):
            GameBudget(max_output_tokens=-1)

    def test_nan_max_cost_is_rejected(self) -> None:
        # A NaN cap would silently disable enforcement because every
        # `x > nan` comparison is False; fail loud at construction.
        with pytest.raises(ValueError, match="max_cost_usd"):
            GameBudget(max_cost_usd=math.nan)

    def test_inf_max_cost_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_cost_usd"):
            GameBudget(max_cost_usd=math.inf)


class TestFloatSafeCapComparison:
    def test_three_dimes_does_not_false_trip_thirty_cent_cap(self) -> None:
        # 0.10 + 0.10 + 0.10 == 0.30000000000000004 in IEEE-754; without
        # cap slack this would raise BudgetExceededError on the third
        # charge even though the logical spend is exactly at the cap.
        budget = GameBudget(max_cost_usd=0.30)

        budget.charge(usage=_usage(), cost_usd=0.10)
        budget.charge(usage=_usage(), cost_usd=0.10)
        budget.charge(usage=_usage(), cost_usd=0.10)

        # We reached the cap; the snapshot total is whatever float math
        # produced, but no overrun was raised.
        assert budget.snapshot().cost_usd == pytest.approx(0.30)

    def test_meaningful_overrun_still_raises(self) -> None:
        # Slack is 1e-6; a charge of 0.01 over the cap is far above slack
        # and must still raise.
        budget = GameBudget(max_cost_usd=0.30)
        budget.charge(usage=_usage(), cost_usd=0.30)

        with pytest.raises(BudgetExceededError):
            budget.charge(usage=_usage(), cost_usd=0.01)


class TestSlackBoundary:
    """L-1 boundary pin (audits/audit-2026-05-16-2239-claude.md §L-1).

    ``llm.budget._COST_USD_CAP_SLACK`` is currently ``1e-6``. The two
    tests below pin the documented slack size at the boundary: a
    charge ``1e-3`` over the cap must raise; a charge ``1e-9`` over
    must not. A future silent slack widening (e.g. ``1e-6`` -> ``1e-3``)
    would let the strictly-over-slack case slip through and would fail
    this test.
    """

    def test_charge_exceeding_slack_raises(self) -> None:
        # 1e-3 is 1000x larger than the documented 1e-6 slack so this
        # is a clear overrun; if the slack ever silently widens to 1e-3
        # this test fails.
        budget = GameBudget(max_cost_usd=0.30)

        with pytest.raises(BudgetExceededError) as excinfo:
            budget.charge(usage=_usage(), cost_usd=0.30 + 1e-3)

        assert excinfo.value.dimension == "cost_usd"

    def test_charge_within_slack_does_not_raise(self) -> None:
        # 1e-9 is well below the 1e-6 slack so this must not raise;
        # the budget is at the cap and we accept it as such.
        budget = GameBudget(max_cost_usd=0.30)

        snapshot = budget.charge(usage=_usage(), cost_usd=0.30 + 1e-9)

        assert snapshot.cost_usd == pytest.approx(0.30 + 1e-9)


class TestBudgetExceededErrorMessage:
    def test_error_message_carries_all_dimensions(self) -> None:
        err = BudgetExceededError(
            dimension="cost_usd",
            current=0.29,
            delta=0.02,
            cap=0.30,
        )

        message = str(err)
        assert "cost_usd" in message
        assert "0.29" in message
        assert "0.02" in message
        assert "0.3" in message
