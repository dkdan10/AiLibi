"""Budget-enforcing :class:`~llm.client.LLMClient` adapter (Task 3.9 C-5).

``MeetingManager`` (Task 3.8) and ``StrategicReasoner`` (Task 3.9) both
accept an :class:`~llm.client.LLMClient` Protocol implementation. This
module adds a provider-neutral adapter that wraps any
:class:`~llm.client.LLMClient` plus a :class:`~llm.budget.GameBudget`
and enforces :meth:`GameBudget.preflight` + :meth:`GameBudget.charge`
around every :meth:`complete` call.

Failure semantics
=================

Pre-flight is fail-loud: if the estimated cost would push the running
total past any cap, :class:`~llm.budget.BudgetExceededError` propagates
*before* the underlying client is invoked. No silent truncation, no
partial spend on a doomed call. After a successful inner call the
actual cost (the provider-reported ``LLMResponse.cost_usd`` and
``usage`` totals) is charged. Estimates may over-charge slightly
relative to actuals; that is the desired direction (conservative).

Cost estimation
===============

The adapter has no insight into per-provider pricing — that lives
inside the wrapped adapter (e.g. :mod:`llm.provider`). Pre-flight
estimation therefore uses two engine-free knobs the constructor
accepts:

* A token estimator that converts ``prompt`` + ``max_tokens`` into a
  conservative :class:`~llm.client.TokenUsage` upper bound (input is
  estimated from prompt length using the standard four-chars-per-token
  heuristic; output is the full ``max_tokens``).
* A USD-per-token rate pair (``cost_per_input_token``,
  ``cost_per_output_token``) used to derive the estimated USD cost
  from the token estimate. Defaults are calibrated to a generous tier
  so the estimator is conservative without baking in any
  provider-specific name; call sites that want a tighter estimate
  pass their own rates.

Cross-provider portability
==========================

The adapter implements the same :class:`~llm.client.LLMClient`
Protocol as the real and fake providers, and never references any
provider-specific concept (extended thinking, ``cache_control``,
prompt-caching beta headers). Consumers including
:class:`meetings.manager.MeetingManager` accept it without signature
changes.
"""

from __future__ import annotations

from typing import Final

from pydantic import BaseModel

from llm.budget import GameBudget
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage

# Conservative defaults. These are intentionally on the high end of
# realistic frontier-model pricing so the pre-flight estimate cannot
# silently undercount and let a doomed call through. Values are in
# USD per single token (not per million); rates calibrated to be
# roughly twice typical premium-tier pricing so a tight budget tripped
# in pre-flight is a true ceiling, not a false ceiling that a real
# call would slip past. Call sites that want tighter estimates pass
# explicit rates via the constructor.
_DEFAULT_COST_PER_INPUT_TOKEN_USD: Final[float] = 6e-6
_DEFAULT_COST_PER_OUTPUT_TOKEN_USD: Final[float] = 30e-6

# Character-to-token ratio for the input-estimator. Mirrors the
# heuristic in :mod:`agents.memory.store` so the two estimators give
# byte-identical numbers on the same prompt text (helpful for
# determinism tests in the strategic reasoner).
_CHARS_PER_TOKEN: Final[int] = 4


def _estimate_input_tokens(prompt: str) -> int:
    """Conservative input-token estimate from prompt length.

    Uses ceiling division on the four-chars-per-token heuristic so the
    estimator never undercounts the true token cost of a string.
    Returns at least 1 to avoid a zero estimate slipping through a
    zero-token cap as "below the cap by definition".
    """

    if not prompt:
        return 1
    return max(1, (len(prompt) + _CHARS_PER_TOKEN - 1) // _CHARS_PER_TOKEN)


class BudgetedLLMClient:
    """Wrap an :class:`LLMClient` + :class:`GameBudget` (DESIGN.md §7).

    Each :meth:`complete` call follows this sequence:

    1. Estimate the call's cost (input tokens from prompt length,
       output tokens from ``max_tokens``, USD from the configured
       per-token rates).
    2. Invoke :meth:`GameBudget.preflight` with that estimate. If the
       running total + estimate would exceed any cap,
       :class:`~llm.budget.BudgetExceededError` raises *before* the
       underlying call.
    3. Invoke the wrapped client's ``complete``.
    4. Charge the actual response cost via
       :meth:`GameBudget.charge_response`.

    The adapter conforms to :class:`LLMClient` structurally so it slots
    into :class:`meetings.manager.MeetingManager` and the strategic
    reasoner without signature changes.
    """

    def __init__(
        self,
        *,
        inner: LLMClient,
        budget: GameBudget,
        cost_per_input_token_usd: float = _DEFAULT_COST_PER_INPUT_TOKEN_USD,
        cost_per_output_token_usd: float = _DEFAULT_COST_PER_OUTPUT_TOKEN_USD,
    ) -> None:
        if cost_per_input_token_usd < 0:
            raise ValueError(
                "cost_per_input_token_usd must be non-negative, "
                f"got {cost_per_input_token_usd}"
            )
        if cost_per_output_token_usd < 0:
            raise ValueError(
                "cost_per_output_token_usd must be non-negative, "
                f"got {cost_per_output_token_usd}"
            )
        self._inner = inner
        self._budget = budget
        self._cost_per_input_token_usd = cost_per_input_token_usd
        self._cost_per_output_token_usd = cost_per_output_token_usd

    @property
    def budget(self) -> GameBudget:
        """The wrapped :class:`GameBudget` (read-only handle)."""

        return self._budget

    def estimate(
        self,
        *,
        prompt: str,
        max_tokens: int,
    ) -> tuple[TokenUsage, float]:
        """Return the conservative pre-flight ``(usage, cost_usd)`` pair.

        Exposed publicly so tests and call sites can mirror the
        estimator without re-deriving the math. The returned
        :class:`TokenUsage` uses ``max_tokens`` for the output side
        (worst-case completion length) and the prompt-length-based
        estimate for the input side.
        """

        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")
        input_tokens = _estimate_input_tokens(prompt)
        output_tokens = max_tokens
        cost_usd = (
            input_tokens * self._cost_per_input_token_usd
            + output_tokens * self._cost_per_output_token_usd
        )
        return (
            TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens),
            cost_usd,
        )

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
    ) -> LLMResponse:
        """Pre-flight, call inner, charge actual cost."""

        estimated_usage, estimated_cost_usd = self.estimate(
            prompt=prompt, max_tokens=max_tokens
        )
        # Pre-flight raises BudgetExceededError if the estimate would
        # push us past any cap. Crucially, this happens BEFORE the
        # wrapped client is invoked so no token spend leaks on a
        # doomed call.
        self._budget.preflight(usage=estimated_usage, cost_usd=estimated_cost_usd)
        response = await self._inner.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
        )
        # Charge the actual response cost. ``charge_response`` itself
        # raises BudgetExceededError if the actual cost would overrun
        # (e.g. estimator under-counted), but only after the inner
        # call has already returned — the orchestrator can still log
        # the response for audit before the overrun cascades.
        self._budget.charge_response(response)
        return response


__all__ = ["BudgetedLLMClient"]
