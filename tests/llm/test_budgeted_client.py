"""Tests for the :class:`~llm.budgeted_client.BudgetedLLMClient` adapter
(Task 3.9 C-5).

The adapter wraps an :class:`~llm.client.LLMClient` plus a
:class:`~llm.budget.GameBudget` and enforces
:meth:`GameBudget.preflight` + :meth:`GameBudget.charge_response`
around every :meth:`complete` call. The tests pin the four contracts
the strategic reasoner and the meeting manager will rely on:

* the adapter implements the same :class:`LLMClient` Protocol as the
  real and fake providers (no signature surprises for consumers),
* pre-flight runs *before* the inner client is invoked (no silent
  partial spend on a doomed call),
* a sequence of calls accumulates cumulative cost until the cap trips
  pre-flight (the meeting-shaped flow contract),
* no Anthropic-specific concept (extended thinking, ``cache_control``,
  prompt-caching beta headers) leaks through the adapter's public
  surface (cross-provider portability).
"""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable
from dataclasses import dataclass, field
from typing import TypeVar

import pytest
from pydantic import BaseModel

from llm.budget import BudgetExceededError, GameBudget
from llm.budgeted_client import BudgetedLLMClient
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider

_T = TypeVar("_T")


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Recording / scripted inner clients
# ---------------------------------------------------------------------------


@dataclass
class _RecordingClient:
    """Inner client that returns a configurable response and records calls."""

    response_text: str = "ok"
    response_cost_usd: float = 0.0
    response_input_tokens: int = 1
    response_output_tokens: int = 1
    response_model: str = "fake-recording"
    calls: list[dict[str, object]] = field(default_factory=list)

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
        self.calls.append(
            {
                "prompt": prompt,
                "schema": schema,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "call_kind": call_kind,
                "model": model,
            }
        )
        return LLMResponse(
            text=self.response_text,
            usage=TokenUsage(
                input_tokens=self.response_input_tokens,
                output_tokens=self.response_output_tokens,
            ),
            cost_usd=self.response_cost_usd,
            model=self.response_model,
        )


class _BlowUpClient:
    """Inner client that raises if invoked.

    Used to prove that pre-flight rejection short-circuits *before* the
    underlying call would be made. If pre-flight ever falls through,
    this client's ``AssertionError`` surfaces clearly in the test.
    """

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
        raise AssertionError(
            "BudgetedLLMClient invoked the inner client when pre-flight "
            "should have rejected the call"
        )


# ---------------------------------------------------------------------------
# Protocol conformance / portability
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    def test_budgeted_client_is_an_llm_client(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(inner=FakeProvider(), budget=budget)

        assert isinstance(adapter, LLMClient)

    def test_complete_signature_matches_protocol(self) -> None:
        protocol_params = tuple(inspect.signature(LLMClient.complete).parameters.keys())
        adapter_params = tuple(
            inspect.signature(BudgetedLLMClient.complete).parameters.keys()
        )

        assert protocol_params == adapter_params

    def test_meeting_manager_protocol_signature_is_compatible(self) -> None:
        # MeetingManager.__init__ accepts `llm_client: LLMClient`. Adding
        # a positional or required-keyword argument that the manager
        # does not pass would silently break Phase 3 integration.
        sig = inspect.signature(BudgetedLLMClient.complete)
        required = [
            name
            for name, param in sig.parameters.items()
            if param.default is inspect.Parameter.empty
            and param.kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            and name != "self"
        ]
        assert set(required) == {"prompt", "schema", "max_tokens", "temperature"}


# ---------------------------------------------------------------------------
# Normal-path delegation
# ---------------------------------------------------------------------------


class TestDelegation:
    def test_complete_returns_inner_response(self) -> None:
        inner = _RecordingClient(
            response_text="hello",
            response_cost_usd=0.001,
            response_input_tokens=5,
            response_output_tokens=2,
            response_model="recording-1",
        )
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(inner=inner, budget=budget)

        response = _run(
            adapter.complete(prompt="hi", schema=None, max_tokens=10, temperature=0.0)
        )

        assert response.text == "hello"
        assert response.cost_usd == pytest.approx(0.001)
        assert response.model == "recording-1"

    def test_complete_passes_through_all_kwargs(self) -> None:
        inner = _RecordingClient()
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(inner=inner, budget=budget)

        _run(
            adapter.complete(
                prompt="hi",
                schema=None,
                max_tokens=10,
                temperature=0.5,
                call_kind="trigger",
                model="forced-model",
            )
        )

        assert len(inner.calls) == 1
        call = inner.calls[0]
        assert call["prompt"] == "hi"
        assert call["max_tokens"] == 10
        assert call["temperature"] == pytest.approx(0.5)
        assert call["call_kind"] == "trigger"
        assert call["model"] == "forced-model"

    def test_actual_cost_is_charged_after_call(self) -> None:
        inner = _RecordingClient(
            response_cost_usd=0.012,
            response_input_tokens=100,
            response_output_tokens=20,
        )
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(inner=inner, budget=budget)

        _run(adapter.complete(prompt="hi", schema=None, max_tokens=10, temperature=0.0))

        snapshot = budget.snapshot()
        assert snapshot.cost_usd == pytest.approx(0.012)
        assert snapshot.input_tokens == 100
        assert snapshot.output_tokens == 20


# ---------------------------------------------------------------------------
# Pre-flight ordering / fail-loud semantics
# ---------------------------------------------------------------------------


class TestPreflightOrdering:
    def test_preflight_runs_before_inner_client(self) -> None:
        # A budget that is already maxed should reject pre-flight on
        # the very first call. _BlowUpClient asserts if invoked.
        budget = GameBudget(max_cost_usd=0.01)
        # Drive the budget to its cap so the next call's pre-flight is
        # guaranteed to exceed it.
        budget.charge_response(
            LLMResponse(
                text="x",
                usage=TokenUsage(input_tokens=0, output_tokens=0),
                cost_usd=0.01,
                model="seed",
            )
        )
        adapter = BudgetedLLMClient(
            inner=_BlowUpClient(),
            budget=budget,
            # Force a large output estimate so the doomed call cannot
            # squeak past the slack tolerance.
            cost_per_output_token_usd=1.0,
        )

        with pytest.raises(BudgetExceededError) as excinfo:
            _run(
                adapter.complete(
                    prompt="this call must be rejected before the inner runs",
                    schema=None,
                    max_tokens=1_000,
                    temperature=0.0,
                )
            )

        assert excinfo.value.dimension == "cost_usd"

    def test_preflight_exhaustion_does_not_charge_state(self) -> None:
        # A pre-flight rejection must not mutate the budget snapshot;
        # downstream retries against a fresh ceiling stay accurate.
        budget = GameBudget(max_cost_usd=0.0)
        adapter = BudgetedLLMClient(
            inner=_BlowUpClient(),
            budget=budget,
            cost_per_input_token_usd=1.0,
            cost_per_output_token_usd=1.0,
        )

        before = budget.snapshot()
        with pytest.raises(BudgetExceededError):
            _run(
                adapter.complete(
                    prompt="will reject",
                    schema=None,
                    max_tokens=1,
                    temperature=0.0,
                )
            )
        after = budget.snapshot()

        assert before == after

    def test_input_token_cap_trips_preflight_before_inner_call(self) -> None:
        # Pre-flight enforces the token caps too -- a maxed input_tokens
        # cap must short-circuit before the inner client runs.
        budget = GameBudget(
            max_cost_usd=1_000.0,
            max_input_tokens=5,
        )
        adapter = BudgetedLLMClient(
            inner=_BlowUpClient(),
            budget=budget,
        )

        # A 100-character prompt estimates as ~25 input tokens >> 5.
        long_prompt = "a" * 100

        with pytest.raises(BudgetExceededError) as excinfo:
            _run(
                adapter.complete(
                    prompt=long_prompt,
                    schema=None,
                    max_tokens=1,
                    temperature=0.0,
                )
            )

        assert excinfo.value.dimension == "input_tokens"


# ---------------------------------------------------------------------------
# Meeting-shaped flow (the C-5 acceptance gate)
# ---------------------------------------------------------------------------


class TestMeetingShapedFlow:
    """End-to-end pin: cumulative spend across a sequence of calls
    trips pre-flight on the offending call, not via silent truncation,
    and not after the underlying client has been called.

    The contract requires at least one test that drives the adapter
    through a manager-shaped flow (multiple complete() calls in
    sequence with cumulative spend tracked). The recording client +
    GameBudget here mirror the meeting protocol's report -> statement
    -> vote sequence at the call shape the manager uses.
    """

    def test_sequence_of_calls_accumulates_to_cap(self) -> None:
        # Charge a small flat cost per call so we can predict exactly
        # which call trips the cap.
        inner = _RecordingClient(response_cost_usd=0.10)
        budget = GameBudget(max_cost_usd=0.30)
        adapter = BudgetedLLMClient(
            inner=inner,
            budget=budget,
            # Zero out the estimator so pre-flight only checks the
            # *running total* of charged costs against the cap; the
            # next call after the cumulative total reaches the cap
            # is the one that should trip.
            cost_per_input_token_usd=0.0,
            cost_per_output_token_usd=0.0,
        )

        _run(adapter.complete(prompt="r1", schema=None, max_tokens=1, temperature=0.0))
        _run(adapter.complete(prompt="r2", schema=None, max_tokens=1, temperature=0.0))
        _run(adapter.complete(prompt="r3", schema=None, max_tokens=1, temperature=0.0))

        # Three calls at $0.10 each lands exactly at the $0.30 cap.
        assert budget.snapshot().cost_usd == pytest.approx(0.30)
        # 3 inner calls invoked so far.
        assert len(inner.calls) == 3

    def test_meeting_ceiling_trips_preflight_not_silent_truncation(self) -> None:
        # Drive the adapter through a manager-shaped sequence; the
        # call after the cumulative total reaches the cap must raise
        # in pre-flight, and the inner client must NOT be called for
        # the rejected attempt.
        inner = _RecordingClient(response_cost_usd=0.10)
        budget = GameBudget(max_cost_usd=0.30)
        adapter = BudgetedLLMClient(
            inner=inner,
            budget=budget,
            # Per-call pre-flight estimate = 1 * 0.01 = $0.01 (above
            # the 1e-6 cap-slack, well below the per-call charge so
            # the first three calls fit comfortably).
            cost_per_input_token_usd=0.0,
            cost_per_output_token_usd=0.01,
        )

        for label in ("r1", "r2", "r3"):
            _run(
                adapter.complete(
                    prompt=label,
                    schema=None,
                    max_tokens=1,
                    temperature=0.0,
                )
            )
        assert len(inner.calls) == 3
        # After three charges of $0.10 the running total is at the
        # $0.30 cap (modulo IEEE-754 noise, which the cap-slack
        # absorbs -- see TestFloatSafeCapComparison in test_budget.py).
        assert budget.snapshot().cost_usd == pytest.approx(0.30)

        # The fourth call's pre-flight estimate adds $0.01 to the
        # running total ($0.30 + $0.01 = $0.31), exceeding the $0.30
        # cap by far more than the 1e-6 slack tolerance. Pre-flight
        # raises *before* the inner client is touched.
        with pytest.raises(BudgetExceededError) as excinfo:
            _run(
                adapter.complete(
                    prompt="r4-over-cap",
                    schema=None,
                    max_tokens=1,
                    temperature=0.0,
                )
            )

        assert excinfo.value.dimension == "cost_usd"
        # The decisive assertion: the inner client was NOT called for
        # the rejected attempt. If pre-flight had been bypassed (silent
        # truncation), inner.calls would be 4.
        assert len(inner.calls) == 3
        # And state stays clean.
        assert budget.snapshot().cost_usd == pytest.approx(0.30)

    def test_meeting_protocol_call_kind_routing(self) -> None:
        # Routes meeting-strength + triggered-check calls through the
        # same adapter; both call_kinds spend from the same budget.
        inner = _RecordingClient(response_cost_usd=0.05)
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(
            inner=inner,
            budget=budget,
            cost_per_input_token_usd=0.0,
            cost_per_output_token_usd=0.0,
        )

        _run(
            adapter.complete(
                prompt="meeting-call",
                schema=None,
                max_tokens=1,
                temperature=0.0,
                call_kind="meeting",
            )
        )
        _run(
            adapter.complete(
                prompt="trigger-call",
                schema=None,
                max_tokens=1,
                temperature=0.0,
                call_kind="trigger",
            )
        )

        assert {call["call_kind"] for call in inner.calls} == {"meeting", "trigger"}
        assert budget.snapshot().cost_usd == pytest.approx(0.10)


# ---------------------------------------------------------------------------
# Estimator exposure / validation
# ---------------------------------------------------------------------------


class TestEstimator:
    def test_estimate_returns_input_from_prompt_length(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(
            inner=FakeProvider(),
            budget=budget,
            cost_per_input_token_usd=1e-3,
            cost_per_output_token_usd=2e-3,
        )

        usage, cost = adapter.estimate(prompt="abcd" * 25, max_tokens=64)

        # 100 chars / 4 chars-per-token = 25 input tokens.
        assert usage.input_tokens == 25
        assert usage.output_tokens == 64
        assert cost == pytest.approx(25 * 1e-3 + 64 * 2e-3)

    def test_estimate_rejects_non_positive_max_tokens(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(inner=FakeProvider(), budget=budget)

        with pytest.raises(ValueError, match="max_tokens"):
            adapter.estimate(prompt="hi", max_tokens=0)

    def test_negative_per_token_cost_rejected_at_construction(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)
        with pytest.raises(ValueError, match="cost_per_input_token_usd"):
            BudgetedLLMClient(
                inner=FakeProvider(),
                budget=budget,
                cost_per_input_token_usd=-1.0,
            )

        with pytest.raises(ValueError, match="cost_per_output_token_usd"):
            BudgetedLLMClient(
                inner=FakeProvider(),
                budget=budget,
                cost_per_output_token_usd=-1.0,
            )


class TestBudgetExposure:
    def test_budget_property_returns_wrapped_instance(self) -> None:
        budget = GameBudget(max_cost_usd=1.0)
        adapter = BudgetedLLMClient(inner=FakeProvider(), budget=budget)

        assert adapter.budget is budget


# ---------------------------------------------------------------------------
# Concurrency / serialized budget checks
# ---------------------------------------------------------------------------


@dataclass
class _ControllableInnerClient:
    """Inner client that blocks on an external event before responding.

    Lets the concurrency tests force several ``complete`` coroutines
    into the same in-flight window so a race against budget state is
    observable. Without serialization, multiple coroutines would all
    pass preflight against the same un-charged snapshot, then all
    invoke the inner client. With the adapter's :class:`asyncio.Lock`
    in place, only one coroutine holds the lock at a time so the
    second's preflight sees the first's charge.
    """

    response_cost_usd: float = 0.0
    response_input_tokens: int = 1
    response_output_tokens: int = 1
    calls: list[str] = field(default_factory=list)
    release: asyncio.Event | None = None

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
        self.calls.append(prompt)
        if self.release is not None:
            await self.release.wait()
        return LLMResponse(
            text="ok",
            usage=TokenUsage(
                input_tokens=self.response_input_tokens,
                output_tokens=self.response_output_tokens,
            ),
            cost_usd=self.response_cost_usd,
            model="controllable",
        )


class TestConcurrentBudgetChecks:
    """Concurrent ``complete`` calls must NOT all pass preflight against
    the same un-charged snapshot before any charge lands.

    ``MeetingManager`` runs Phase-1 reports and Phase-3 votes through
    :func:`asyncio.TaskGroup`, so the adapter sees several in-flight
    calls per phase. Without the per-adapter :class:`asyncio.Lock`,
    every concurrent caller would see budget=0 in preflight, all pass,
    all spend, and the cumulative charge would overrun the cap silently.
    """

    def test_concurrent_calls_do_not_all_pass_stale_preflight(self) -> None:
        # Budget cap at $0.30, three concurrent calls each estimating
        # $0.20 in preflight and charging $0.20 on completion. Without
        # serialization all three preflights would see a zero spend
        # snapshot and all three would race past into the inner client.
        # With the lock in place, the second call's preflight sees the
        # first's charge ($0.20) and rejects ($0.20 + $0.20 = $0.40 >
        # $0.30) BEFORE invoking the inner client.
        budget = GameBudget(max_cost_usd=0.30)

        async def _drive() -> tuple[int, int, int]:
            inner = _ControllableInnerClient(response_cost_usd=0.20)
            adapter = BudgetedLLMClient(
                inner=inner,
                budget=budget,
                cost_per_input_token_usd=0.0,
                # 1 output token * $0.20/token = $0.20 estimated cost.
                cost_per_output_token_usd=0.20,
            )

            async def _one(label: str) -> bool:
                try:
                    await adapter.complete(
                        prompt=label,
                        schema=None,
                        max_tokens=1,
                        temperature=0.0,
                    )
                except BudgetExceededError:
                    return False
                return True

            results = await asyncio.gather(
                _one("c1"),
                _one("c2"),
                _one("c3"),
                return_exceptions=False,
            )
            successes = sum(1 for r in results if r)
            failures = sum(1 for r in results if not r)
            return successes, failures, len(inner.calls)

        successes, failures, inner_calls = _run(_drive())

        # Exactly one call can succeed: the second's preflight sees
        # the first's $0.20 charge and rejects.
        assert successes == 1, (
            f"BudgetedLLMClient let {successes} of 3 concurrent calls succeed "
            "with a $0.30 cap and $0.20-per-call estimates; budget state "
            "was raced past."
        )
        assert successes + failures == 3
        # The inner client is only invoked for the call that passed
        # preflight; doomed calls short-circuit at the lock with no
        # spend on the underlying provider.
        assert inner_calls == 1, (
            f"BudgetedLLMClient invoked the inner client {inner_calls} times "
            "when only 1 call's preflight should have passed; the other "
            "calls bypassed the 'reject before invoking inner client' guarantee."
        )
        # And the final budget total never exceeds the cap.
        assert budget.snapshot().cost_usd <= 0.30 + 1e-6

    def test_serialization_preserves_first_to_arrive_ordering(self) -> None:
        # When two calls race for a budget that admits exactly one of
        # them, the lock guarantees one succeeds and one fails -- not
        # both succeed or both fail.
        budget = GameBudget(max_cost_usd=0.10)

        async def _drive() -> tuple[list[bool], int]:
            inner = _ControllableInnerClient(response_cost_usd=0.10)
            adapter = BudgetedLLMClient(
                inner=inner,
                budget=budget,
                cost_per_input_token_usd=0.0,
                # $0.10/token * 1 token = $0.10 estimated cost; the
                # first call fills the cap and the second's preflight
                # ($0.10 + $0.10 > $0.10 + slack) rejects before
                # invoking inner.
                cost_per_output_token_usd=0.10,
            )

            async def _one(label: str) -> bool:
                try:
                    await adapter.complete(
                        prompt=label,
                        schema=None,
                        max_tokens=1,
                        temperature=0.0,
                    )
                except BudgetExceededError:
                    return False
                return True

            results = list(
                await asyncio.gather(_one("a"), _one("b"), return_exceptions=False)
            )
            return results, len(inner.calls)

        results, inner_calls = _run(_drive())

        assert sum(results) == 1
        assert sum(1 for r in results if not r) == 1
        # The rejected call's inner is never invoked.
        assert inner_calls == 1


class TestProviderAwaitNotSerialized:
    """The adapter must NOT hold its lock across the inner ``complete``
    await. ``MeetingManager`` issues parallel calls under per-call
    ``asyncio.wait_for`` deadlines; serializing the provider await
    would cause late callers to time out queued behind earlier
    callers' provider latency. The fix uses an in-flight reservation
    pool so concurrent preflights see each other's pending charges
    while their provider awaits overlap.
    """

    def test_concurrent_provider_awaits_overlap_when_budget_admits(self) -> None:
        # Budget cap and per-call estimate sized so all three calls
        # individually fit (3 * $0.05 = $0.15 < $0.30 cap). Each
        # inner call blocks on a shared event. Without the in-flight
        # tracking refactor, the second/third callers' provider
        # awaits would queue behind the first under a held lock; with
        # the fix, all three inner.complete() awaits run in parallel.
        budget = GameBudget(max_cost_usd=0.30)
        release = asyncio.Event()
        started = asyncio.Event()
        seen_starts: list[str] = []

        async def _drive() -> tuple[list[str], list[bool]]:
            inner = _ControllableInnerClient(
                response_cost_usd=0.05,
                release=release,
            )

            # Patch the inner so we can observe the start of each call
            # before it suspends on the release event. The
            # ``_ControllableInnerClient`` stores its prompt in
            # ``calls`` BEFORE awaiting the release event, so we can
            # read ``calls`` to see how many providers are in flight.

            adapter = BudgetedLLMClient(
                inner=inner,
                budget=budget,
                cost_per_input_token_usd=0.0,
                cost_per_output_token_usd=0.05,
            )

            async def _one(label: str) -> bool:
                try:
                    await adapter.complete(
                        prompt=label,
                        schema=None,
                        max_tokens=1,
                        temperature=0.0,
                    )
                except BudgetExceededError:
                    return False
                return True

            # Launch three concurrent calls; they will all start the
            # provider await before any can complete (the event is
            # unset).
            tasks = [asyncio.create_task(_one(label)) for label in ("a", "b", "c")]

            # Yield repeatedly until all three inner calls have
            # started (recorded their prompts on inner.calls). The
            # spin-yield is bounded to a few iterations because we
            # are inside the same event loop.
            for _ in range(20):
                if len(inner.calls) >= 3:
                    break
                await asyncio.sleep(0)
            seen_starts.extend(inner.calls)
            started.set()

            # Release the inner calls so they complete.
            release.set()
            results = await asyncio.gather(*tasks)
            return seen_starts, list(results)

        starts, results = _run(_drive())

        # The decisive assertion: all three provider awaits ran
        # concurrently. If the lock were held across the provider
        # await, only one call would have reached inner.complete()
        # before the test snapshot.
        assert len(starts) == 3, (
            f"BudgetedLLMClient held its lock across the provider await: "
            f"only {len(starts)} inner.complete() calls had started after "
            "all three coroutines were launched (expected 3)."
        )
        # And all three calls succeed because the budget admits them.
        assert all(results)
        assert budget.snapshot().cost_usd == pytest.approx(0.15)

    def test_in_flight_reservation_released_on_provider_failure(self) -> None:
        # If the provider raises, the in-flight reservation must be
        # released so subsequent calls and retries against a fresh
        # ceiling see the correct headroom. Without the release, a
        # transient provider failure would permanently consume budget
        # headroom on the adapter side.
        class _RaisingClient:
            calls: list[str] = []

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
                self.calls.append(prompt)
                raise RuntimeError("provider down")

        budget = GameBudget(max_cost_usd=0.10)
        adapter = BudgetedLLMClient(
            inner=_RaisingClient(),
            budget=budget,
            cost_per_input_token_usd=0.0,
            cost_per_output_token_usd=0.05,
        )

        async def _drive() -> None:
            with pytest.raises(RuntimeError, match="provider down"):
                await adapter.complete(
                    prompt="will fail",
                    schema=None,
                    max_tokens=1,
                    temperature=0.0,
                )

        _run(_drive())

        # The in-flight reservation released; budget shows zero spend.
        # If the reservation leaked, a second call would see the
        # in-flight pool include the failed call's estimate.
        assert budget.snapshot().cost_usd == 0.0
        assert adapter._in_flight_cost_usd == 0.0  # noqa: SLF001
        assert adapter._in_flight_input_tokens == 0  # noqa: SLF001
        assert adapter._in_flight_output_tokens == 0  # noqa: SLF001
