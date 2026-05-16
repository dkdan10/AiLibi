"""Per-game LLM budget enforcement (DESIGN.md §7, §10.4).

A :class:`GameBudget` enforces both a USD ceiling and a token-count
ceiling for one game. Enforcement is **fail-loud**: the moment a charge
would push the running total past the ceiling, the budget raises
:class:`BudgetExceededError`. The caller decides what to do next
(transition to a degraded path, end the game, surface the failure to
the orchestrator) — silent truncation is not an option.

The budget is layered above :class:`~llm.client.LLMClient` like the
cache:

::

    budget.charge(response.usage, cost_usd=response.cost_usd)

so it stays provider-neutral. The caller may also pre-flight a call
with :meth:`GameBudget.preflight` to fail fast before invoking the
LLM, which avoids spending a turn waiting on a response that the
budget would reject anyway.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from llm.client import LLMResponse, TokenUsage


_DEFAULT_MAX_COST_USD: Final[float] = 0.30
_DEFAULT_MAX_INPUT_TOKENS: Final[int] = 1_000_000
_DEFAULT_MAX_OUTPUT_TOKENS: Final[int] = 200_000


class BudgetExceededError(RuntimeError):
    """Raised when an LLM call would push spending past the cap.

    Carries the dimension that tripped (``"cost_usd"``,
    ``"input_tokens"``, ``"output_tokens"``), the current running total,
    the proposed delta, and the configured cap so callers can render
    actionable error messages without re-deriving the math.
    """

    def __init__(
        self,
        *,
        dimension: str,
        current: float,
        delta: float,
        cap: float,
    ) -> None:
        self.dimension = dimension
        self.current = current
        self.delta = delta
        self.cap = cap
        super().__init__(
            f"LLM budget exceeded on {dimension}: "
            f"current={current!r} + delta={delta!r} > cap={cap!r}"
        )


@dataclass(frozen=True)
class BudgetSnapshot:
    """Immutable view of a :class:`GameBudget`'s running totals."""

    cost_usd: float
    input_tokens: int
    output_tokens: int
    max_cost_usd: float
    max_input_tokens: int
    max_output_tokens: int

    @property
    def remaining_cost_usd(self) -> float:
        return self.max_cost_usd - self.cost_usd

    @property
    def remaining_input_tokens(self) -> int:
        return self.max_input_tokens - self.input_tokens

    @property
    def remaining_output_tokens(self) -> int:
        return self.max_output_tokens - self.output_tokens


class GameBudget:
    """Per-game LLM spend tracker (DESIGN.md §10.4 — \"cost overruns\").

    The orchestrator constructs one budget per game and threads it through
    every strategic call. Charges accumulate; over-cap charges raise
    :class:`BudgetExceededError` *before* the spend is recorded so retries
    against a fresh ceiling stay accurate.
    """

    def __init__(
        self,
        *,
        max_cost_usd: float = _DEFAULT_MAX_COST_USD,
        max_input_tokens: int = _DEFAULT_MAX_INPUT_TOKENS,
        max_output_tokens: int = _DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> None:
        if max_cost_usd < 0:
            raise ValueError(f"max_cost_usd must be non-negative, got {max_cost_usd}")
        if max_input_tokens < 0:
            raise ValueError(
                f"max_input_tokens must be non-negative, got {max_input_tokens}"
            )
        if max_output_tokens < 0:
            raise ValueError(
                f"max_output_tokens must be non-negative, got {max_output_tokens}"
            )
        self._max_cost_usd = max_cost_usd
        self._max_input_tokens = max_input_tokens
        self._max_output_tokens = max_output_tokens
        self._cost_usd = 0.0
        self._input_tokens = 0
        self._output_tokens = 0

    def snapshot(self) -> BudgetSnapshot:
        return BudgetSnapshot(
            cost_usd=self._cost_usd,
            input_tokens=self._input_tokens,
            output_tokens=self._output_tokens,
            max_cost_usd=self._max_cost_usd,
            max_input_tokens=self._max_input_tokens,
            max_output_tokens=self._max_output_tokens,
        )

    def preflight(self, *, usage: TokenUsage, cost_usd: float) -> None:
        """Raise :class:`BudgetExceededError` if charging would overrun.

        Does not mutate state; safe to call before invoking the LLM to
        skip a doomed request.
        """

        if self._cost_usd + cost_usd > self._max_cost_usd:
            raise BudgetExceededError(
                dimension="cost_usd",
                current=self._cost_usd,
                delta=cost_usd,
                cap=self._max_cost_usd,
            )
        if self._input_tokens + usage.input_tokens > self._max_input_tokens:
            raise BudgetExceededError(
                dimension="input_tokens",
                current=float(self._input_tokens),
                delta=float(usage.input_tokens),
                cap=float(self._max_input_tokens),
            )
        if self._output_tokens + usage.output_tokens > self._max_output_tokens:
            raise BudgetExceededError(
                dimension="output_tokens",
                current=float(self._output_tokens),
                delta=float(usage.output_tokens),
                cap=float(self._max_output_tokens),
            )

    def charge(self, *, usage: TokenUsage, cost_usd: float) -> BudgetSnapshot:
        """Apply a charge after the LLM call returns.

        Raises :class:`BudgetExceededError` *before* mutating state if
        the charge would push any dimension past its cap.
        """

        self.preflight(usage=usage, cost_usd=cost_usd)
        self._cost_usd += cost_usd
        self._input_tokens += usage.input_tokens
        self._output_tokens += usage.output_tokens
        return self.snapshot()

    def charge_response(self, response: LLMResponse) -> BudgetSnapshot:
        """Convenience wrapper that pulls ``usage`` / ``cost_usd`` from a response."""

        return self.charge(usage=response.usage, cost_usd=response.cost_usd)


__all__ = [
    "BudgetExceededError",
    "BudgetSnapshot",
    "GameBudget",
]
