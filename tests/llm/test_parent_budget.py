"""Per-game caps and the cumulative run cap account for the same actual usage."""

from __future__ import annotations

import pytest

from llm.budget import BudgetExceededError, GameBudget
from llm.client import TokenUsage


@pytest.mark.parametrize("local_cap,parent_cap", [(1, 10), (10, 1), (1, 1)])
def test_overrun_charges_both_budgets(local_cap: int, parent_cap: int) -> None:
    parent = GameBudget(max_input_tokens=parent_cap)
    child = GameBudget(max_input_tokens=local_cap, parent=parent)
    with pytest.raises(BudgetExceededError):
        child.charge(usage=TokenUsage(input_tokens=2, output_tokens=3), cost_usd=0.1)
    assert child.snapshot().input_tokens == parent.snapshot().input_tokens == 2
    assert child.snapshot().output_tokens == parent.snapshot().output_tokens == 3
    assert child.snapshot().cost_usd == parent.snapshot().cost_usd == 0.1


def test_new_game_does_not_restore_tournament_allowance() -> None:
    parent = GameBudget(max_input_tokens=10)
    first = GameBudget(parent=parent)
    first.charge(usage=TokenUsage(input_tokens=8, output_tokens=2), cost_usd=0.02)
    second = GameBudget(parent=parent)
    with pytest.raises(BudgetExceededError):
        second.preflight(
            usage=TokenUsage(input_tokens=3, output_tokens=1), cost_usd=0.01
        )
    assert parent.snapshot().input_tokens == 8
    assert second.snapshot().input_tokens == 0


def test_invalid_charge_changes_neither_budget() -> None:
    parent = GameBudget()
    child = GameBudget(parent=parent)
    with pytest.raises(ValueError):
        child.charge(
            usage=TokenUsage(input_tokens=2, output_tokens=3), cost_usd=float("nan")
        )
    assert child.snapshot().input_tokens == parent.snapshot().input_tokens == 0
