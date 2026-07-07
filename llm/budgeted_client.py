"""Budget-enforcing :class:`~llm.client.LLMClient` adapter (Task 3.9 C-5).

``MeetingManager`` (Task 3.8) accepts an :class:`~llm.client.LLMClient`
Protocol implementation. This module adds a provider-neutral adapter that
wraps any :class:`~llm.client.LLMClient` plus a
:class:`~llm.budget.GameBudget` and enforces :meth:`GameBudget.preflight` +
:meth:`GameBudget.charge` around every :meth:`complete` call.

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
  pass their own rates. When neither is passed, the rates resolve from
  the wrapped client's optional :class:`_SupportsPreflightCostRates`
  hint — a free provider (the local Ollama client) exposes ``0.0`` so
  the USD pre-flight dimension is disabled while the token caps stay
  intact — falling back to the frontier defaults otherwise. The token
  estimator is unaffected, so the token ceiling still backstops a
  rambling local model.

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

import asyncio
from typing import Final, Protocol, runtime_checkable

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


@runtime_checkable
class _SupportsPreflightCostRates(Protocol):
    """Optional hint a provider client may expose to override the default
    pre-flight cost-estimation rates (USD per single token).

    This lets the budget layer zero the USD pre-flight dimension for a
    free provider WITHOUT naming it here — the module stays
    provider-neutral (it references no extended-thinking / cache-control /
    provider-name concept). A provider whose completions are always free —
    a local model that reports ``cost_usd == 0.0`` — exposes both rates as
    ``0.0`` so the USD pre-flight cannot block a free run while the token
    caps stay intact (a local model can ramble; the token ceiling is the
    real backstop). Clients that do not implement this Protocol (Anthropic,
    the fake) keep the frontier-calibrated defaults, so their budget
    behavior is unchanged.
    """

    preflight_cost_per_input_token_usd: float
    preflight_cost_per_output_token_usd: float


def _default_cost_rates(inner: LLMClient) -> tuple[float, float]:
    """Resolve the ``(input, output)`` pre-flight USD/token rates for ``inner``.

    Reads the optional :class:`_SupportsPreflightCostRates` hint a provider
    client may expose; falls back to the frontier-calibrated module
    defaults for clients that don't (Anthropic, the fake), so their
    pre-flight estimate is byte-identical to before the hint existed.
    """

    if isinstance(inner, _SupportsPreflightCostRates):
        return (
            inner.preflight_cost_per_input_token_usd,
            inner.preflight_cost_per_output_token_usd,
        )
    return (_DEFAULT_COST_PER_INPUT_TOKEN_USD, _DEFAULT_COST_PER_OUTPUT_TOKEN_USD)


class BudgetedLLMClient:
    """Wrap an :class:`LLMClient` + :class:`GameBudget` (DESIGN.md §7).

    Each :meth:`complete` call follows this sequence:

    1. Estimate the call's cost (input tokens from prompt length,
       output tokens from ``max_tokens``, USD from the configured
       per-token rates).
    2. Atomically pre-flight against the budget's running total plus
       any in-flight reservations from sibling concurrent calls. If
       the combined total would exceed a cap,
       :class:`~llm.budget.BudgetExceededError` raises *before* the
       underlying call. On pass, the estimate is added to the
       in-flight reservation pool.
    3. Invoke the wrapped client's ``complete`` (no lock held).
    4. Atomically release the in-flight reservation and charge the
       actual response cost via :meth:`GameBudget.charge_response`.

    The adapter conforms to :class:`LLMClient` structurally so it slots
    into :class:`meetings.manager.MeetingManager` and the strategic
    reasoner without signature changes.

    Concurrency
    -----------

    :class:`meetings.manager.MeetingManager` runs Phase-1 reports and
    Phase-3 votes through :func:`asyncio.TaskGroup` so multiple agents'
    :meth:`complete` calls are in flight at once, each under its own
    :func:`asyncio.wait_for` deadline. The adapter must therefore (a)
    prevent the "all preflights pass against the same stale snapshot"
    race, AND (b) allow the actual provider awaits to overlap so a
    late caller does not eat its own deadline waiting in a queue.

    The implementation tracks in-flight reservations in an adapter-
    local counter pool (``_in_flight_*``). The :class:`asyncio.Lock`
    is held ONLY for the brief synchronous budget mutations
    (preflight + reserve, then release-reserve + charge) — never
    across the ``await self._inner.complete(...)``. Concurrent callers
    therefore (1) see each other's reservations during preflight so
    no overrun slips through, and (2) overlap their provider awaits
    so deadlines are not artificially serialized.
    """

    def __init__(
        self,
        *,
        inner: LLMClient,
        budget: GameBudget,
        cost_per_input_token_usd: float | None = None,
        cost_per_output_token_usd: float | None = None,
    ) -> None:
        # An explicit rate always wins; ``None`` (the default) resolves from
        # the inner client's optional hint, then the frontier defaults. This
        # lets a free provider (the Ollama client) zero the USD pre-flight
        # dimension via its hint without any change at the construction site
        # (orchestrator.game wraps the provider with no explicit rates),
        # while the Anthropic / fake path keeps the frontier defaults exactly.
        default_input, default_output = _default_cost_rates(inner)
        resolved_input = (
            cost_per_input_token_usd
            if cost_per_input_token_usd is not None
            else default_input
        )
        resolved_output = (
            cost_per_output_token_usd
            if cost_per_output_token_usd is not None
            else default_output
        )
        if resolved_input < 0:
            raise ValueError(
                f"cost_per_input_token_usd must be non-negative, got {resolved_input}"
            )
        if resolved_output < 0:
            raise ValueError(
                f"cost_per_output_token_usd must be non-negative, got {resolved_output}"
            )
        self._inner = inner
        self._budget = budget
        self._cost_per_input_token_usd = resolved_input
        self._cost_per_output_token_usd = resolved_output
        # Lazily-created lock so the adapter does not bind to an event
        # loop at construction time (the MeetingManager constructs the
        # adapter outside its own event-loop context).
        self._lock: asyncio.Lock | None = None
        # In-flight reservation pool: the sum of every concurrent
        # call's estimated cost / token usage that has passed preflight
        # but has not yet been charged. Mutated only under ``_lock`` so
        # preflight and charge see a consistent view.
        self._in_flight_cost_usd: float = 0.0
        self._in_flight_input_tokens: int = 0
        self._in_flight_output_tokens: int = 0

    def _ensure_lock(self) -> asyncio.Lock:
        """Return the per-adapter :class:`asyncio.Lock`, creating it lazily.

        Created on first use so callers that construct the adapter on
        a different thread/loop than they call it on do not bind to a
        stale loop. The lock itself is loop-agnostic in Python 3.10+
        as long as it is awaited from the right loop.
        """

        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

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
        agent_id: str | None = None,
    ) -> LLMResponse:
        """Pre-flight, call inner, charge actual cost.

        The :attr:`_lock` is held only for the brief synchronous
        budget mutations (preflight + reserve up front, then
        release-reserve + charge after the inner call returns); the
        ``await self._inner.complete(...)`` runs *outside* the lock so
        concurrent callers' provider awaits overlap and each retains
        its own deadline budget. The in-flight reservation pool
        (``_in_flight_*``) ensures concurrent preflights see each
        other's pending charges and reject doomed calls before they
        touch the inner client.
        """

        estimated_usage, estimated_cost_usd = self.estimate(
            prompt=prompt, max_tokens=max_tokens
        )

        # Step 1: brief locked region -- preflight against
        # budget + in-flight reservations, then reserve.
        async with self._ensure_lock():
            self._budget.preflight(
                usage=TokenUsage(
                    input_tokens=(
                        estimated_usage.input_tokens + self._in_flight_input_tokens
                    ),
                    output_tokens=(
                        estimated_usage.output_tokens + self._in_flight_output_tokens
                    ),
                ),
                cost_usd=estimated_cost_usd + self._in_flight_cost_usd,
            )
            self._in_flight_cost_usd += estimated_cost_usd
            self._in_flight_input_tokens += estimated_usage.input_tokens
            self._in_flight_output_tokens += estimated_usage.output_tokens

        # Step 2: provider call -- NO lock held. Sibling concurrent
        # callers' provider awaits run in parallel; each retains its
        # own asyncio.wait_for deadline.
        try:
            response = await self._inner.complete(
                prompt=prompt,
                schema=schema,
                max_tokens=max_tokens,
                temperature=temperature,
                call_kind=call_kind,
                model=model,
                agent_id=agent_id,
            )
        except BaseException:
            # The provider failed; release the in-flight reservation
            # so future calls and retries against a fresh ceiling see
            # the correct headroom.
            async with self._ensure_lock():
                self._in_flight_cost_usd -= estimated_cost_usd
                self._in_flight_input_tokens -= estimated_usage.input_tokens
                self._in_flight_output_tokens -= estimated_usage.output_tokens
            raise

        # Step 3: brief locked region -- settle up. Charge the actual
        # response cost and release the in-flight reservation. The
        # release happens in ``finally`` so even when the actual cost
        # overruns the cap (charge_response raises) the in-flight
        # counter stays consistent with no leak.
        async with self._ensure_lock():
            try:
                self._budget.charge_response(response)
            finally:
                self._in_flight_cost_usd -= estimated_cost_usd
                self._in_flight_input_tokens -= estimated_usage.input_tokens
                self._in_flight_output_tokens -= estimated_usage.output_tokens
        return response


__all__ = ["BudgetedLLMClient"]
