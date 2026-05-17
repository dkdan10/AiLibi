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
