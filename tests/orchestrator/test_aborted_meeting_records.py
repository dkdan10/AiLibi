"""Completed and aborted meetings retain every paid provider attempt once."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

from _manifest_writer import sample_provenance
from api.replay_loader import ReplayLoader
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from eval.balance_eval import load_tournament_report
from llm.budget import BudgetExceededError, GameBudget
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from llm.provider import (
    DEFAULT_MEETING_MODEL,
    AnthropicClient,
    AnthropicRawResponse,
    LLMCallFailure,
    _attach_parse_failure,  # noqa: PLC2701
    extract_parse_failure,
)
from observation.action_intent import ActionIntent, EmergencyMeetingIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    AgentFactory,
    DEFAULT_TASKS_PER_CREWMATE,
    DefaultMeetingRunner,
    HeadlessGame,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    compute_cost_usd,
    read_all_entries,
    read_meeting_entries,
)
from orchestrator.scheduler import TickScheduler


class _EmergencyCaller(TacticalAgent):
    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        super().decide(packet, public_map)
        if self.agent_id == "p-1" and packet.tick == 0:
            return EmergencyMeetingIntent(type="emergency", actor=self.agent_id)
        return WaitIntent(type="wait", actor=self.agent_id)


def _agent_factory(agent_id: PlayerId, role: Role) -> _EmergencyCaller:
    policy = (
        CrewmatePolicy(agent_id=agent_id)
        if role == "CREWMATE"
        else ImpostorPolicy(agent_id=agent_id)
    )
    return _EmergencyCaller(agent_id=agent_id, role=role, policy=policy)


def _game(
    path: Path | None,
    runner: DefaultMeetingRunner,
    *,
    agent_factory: AgentFactory | None = None,
) -> HeadlessGame:
    return HeadlessGame(
        seed=2026,
        num_players=4,
        game_map=load_canonical_map(),
        agent_factory=agent_factory or _agent_factory,
        replay_path=path,
        scheduler=TickScheduler(max_ticks=3),
        meeting_runner=runner,
    )


class _InjectedProvider:
    """Real validation and pricing around scripted, offline transport responses."""

    def __init__(
        self,
        *,
        abort_at: int | None = 2,
        invalid_at: frozenset[int] = frozenset(),
        cancel: bool = False,
        input_tokens: int = 80,
        identical_failure_metadata: bool = False,
    ) -> None:
        self.abort_at = abort_at
        self.invalid_at = invalid_at
        self.input_tokens = input_tokens
        self.identical_failure_metadata = identical_failure_metadata
        self.abort_error: BaseException = (
            asyncio.CancelledError("injected cancellation")
            if cancel
            else RuntimeError("injected transport failure")
        )
        self.attempts = 0
        self.calls: list[LLMCallRecord] = []
        self.failures: list[LLMCallFailure] = []

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
        self.attempts += 1
        if self.attempts == self.abort_at:
            raise self.abort_error
        fake = await FakeProvider().complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        raw = "{}" if self.attempts in self.invalid_at else fake.text

        async def send(**kwargs: object) -> AnthropicRawResponse:
            return AnthropicRawResponse(
                text=raw,
                model=DEFAULT_MEETING_MODEL,
                input_tokens=self.input_tokens,
                output_tokens=10,
            )

        try:
            response = await AnthropicClient(
                api_key="injected-test", send=send
            ).complete(
                prompt=prompt,
                schema=schema,
                max_tokens=max_tokens,
                temperature=temperature,
                call_kind=call_kind,
                agent_id=agent_id,
            )
        except ValidationError as exc:
            failure = extract_parse_failure(exc)
            assert failure is not None
            if self.identical_failure_metadata:
                # Plant identical metadata for distinct paid attempts. The
                # real retry prompt normally differs in length; equality of
                # response metadata must never establish call identity.
                failure = failure.model_copy(update={"prompt_length": 100})
                _attach_parse_failure(exc, failure)
            self.failures.append(failure)
            raise
        self.calls.append(
            LLMCallRecord(
                call_kind=call_kind,
                model=response.model,
                prompt=prompt,
                response_text=response.text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                cost_usd=response.cost_usd,
                agent_id=agent_id,
            )
        )
        return response


def _assert_aborted_record(
    path: Path,
    provider: _InjectedProvider,
    budget: GameBudget,
    *,
    expected_error_type: str = "RuntimeError",
) -> tuple[FailedCallReplayEntry, ...]:
    entries = read_all_entries(path)
    assert compute_cost_usd(path) == pytest.approx(budget.snapshot().cost_usd)
    assert not read_meeting_entries(path)
    assert not any(isinstance(entry, GameEndReplayEntry) for entry in entries)
    aborted = [
        entry.model_dump() for entry in entries if entry.kind == "meeting_aborted"
    ]
    assert len(aborted) == 1
    record = aborted[0]
    assert record["game_id"] == "headless-seed-2026"
    assert record["meeting_id"] == "headless-seed-2026:meeting-0"
    assert record["tick"] == 0
    assert record["prompt_versions"]
    assert record["error_type"] == expected_error_type
    assert record["error_message"]
    assert "outcome" not in record
    assert "transcript" not in record
    calls = tuple(LLMCallRecord.model_validate(call) for call in record["llm_calls"])
    assert calls == tuple(provider.calls)
    failures = tuple(
        entry
        for entry in entries
        if isinstance(entry, FailedCallReplayEntry)
        and entry.error_type != "deadline_default"
    )
    assert len(failures) == len(provider.failures)
    for recorded, expected in zip(failures, provider.failures, strict=True):
        assert (
            LLMCallFailure.model_validate(
                recorded.model_dump(include=set(LLMCallFailure.model_fields))
            )
            == expected
        )
    assert (
        sum(call.input_tokens for call in calls)
        + sum(failure.input_tokens for failure in failures)
        == budget.snapshot().input_tokens
    )
    assert (
        sum(call.output_tokens for call in calls)
        + sum(failure.output_tokens for failure in failures)
        == budget.snapshot().output_tokens
    )
    return failures


@pytest.mark.parametrize("cancel", [False, True])
def test_paid_prefix_survives_abort_and_runner_reuse(
    tmp_path: Path, cancel: bool
) -> None:
    provider = _InjectedProvider(cancel=cancel)
    budget = GameBudget(max_cost_usd=1.0)
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    aborted_path = tmp_path / "aborted.jsonl"

    with pytest.raises(type(provider.abort_error)) as excinfo:
        _game(aborted_path, runner).run()
    assert excinfo.value is provider.abort_error
    assert provider.attempts == 2
    assert len(provider.calls) == 1
    _assert_aborted_record(
        aborted_path,
        provider,
        budget,
        expected_error_type=type(provider.abort_error).__name__,
    )

    prefix = tuple(provider.calls)
    provider.abort_at = None
    retry_path = tmp_path / "retry.jsonl"
    _game(retry_path, runner).run()
    meetings = read_meeting_entries(retry_path)
    assert len(meetings) == 1
    assert meetings[0].llm_calls == tuple(provider.calls[len(prefix) :])
    assert not any(
        entry.kind == "meeting_aborted" for entry in read_all_entries(retry_path)
    )
    assert compute_cost_usd(aborted_path) + compute_cost_usd(
        retry_path
    ) == pytest.approx(budget.snapshot().cost_usd)


def test_recovered_validation_failure_and_success_survive_later_abort(
    tmp_path: Path,
) -> None:
    provider = _InjectedProvider(abort_at=3, invalid_at=frozenset({1}))
    budget = GameBudget(max_cost_usd=1.0)
    path = tmp_path / "recovered.jsonl"
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    with pytest.raises(RuntimeError, match="injected transport failure"):
        _game(path, runner).run()
    assert len(provider.calls) == 1
    assert len(provider.failures) == 1
    _assert_aborted_record(path, provider, budget)


@pytest.mark.parametrize("budget_abort", [False, True])
def test_pending_validation_failure_survives_retry_abort(
    tmp_path: Path, budget_abort: bool
) -> None:
    provider = _InjectedProvider(
        abort_at=None if budget_abort else 2,
        invalid_at=frozenset({1}),
        input_tokens=10_000 if budget_abort else 80,
    )
    budget = GameBudget(max_cost_usd=1.0, max_input_tokens=10_000)
    path = tmp_path / "pending.jsonl"
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    with pytest.raises(BudgetExceededError if budget_abort else RuntimeError):
        _game(path, runner).run()
    assert provider.attempts == (1 if budget_abort else 2)
    assert len(provider.failures) == 1
    _assert_aborted_record(
        path,
        provider,
        budget,
        expected_error_type="BudgetExceededError" if budget_abort else "RuntimeError",
    )


def test_identical_paid_invalid_attempts_remain_distinct(tmp_path: Path) -> None:
    provider = _InjectedProvider(
        abort_at=3,
        invalid_at=frozenset({1, 2}),
        identical_failure_metadata=True,
    )
    budget = GameBudget(max_cost_usd=1.0)
    path = tmp_path / "identical.jsonl"
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    with pytest.raises(RuntimeError, match="injected transport failure"):
        _game(path, runner).run()
    assert len(provider.failures) == 2
    assert provider.failures[0] == provider.failures[1]
    failures = _assert_aborted_record(path, provider, budget)
    call_ids = [failure.model_dump().get("call_id") for failure in failures]
    assert None not in call_ids
    assert len(set(call_ids)) == 2
    defaults = [
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, FailedCallReplayEntry)
        and entry.error_type == "deadline_default"
    ]
    assert len(defaults) == 1
    assert defaults[0].input_tokens == defaults[0].output_tokens == 0
    assert defaults[0].cost_usd == 0.0


@pytest.mark.parametrize("invalid_attempts", [1, 2, 100])
def test_completed_meeting_failures_reconcile_across_accounting_consumers(
    tmp_path: Path, invalid_attempts: int
) -> None:
    provider = _InjectedProvider(
        abort_at=None,
        invalid_at=frozenset(range(1, invalid_attempts + 1)),
        identical_failure_metadata=True,
    )
    budget = GameBudget(max_cost_usd=1.0)
    path = tmp_path / "replay-seed-2026.jsonl"
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    result = _game(path, runner).run()

    meetings = read_meeting_entries(path)
    assert len(meetings) == 1
    assert meetings[0].llm_calls == tuple(provider.calls)
    entries = read_all_entries(path)
    assert not any(entry.kind == "meeting_aborted" for entry in entries)
    failures = [
        entry
        for entry in entries
        if isinstance(entry, FailedCallReplayEntry)
        and entry.error_type != "deadline_default"
    ]
    assert len(failures) == len(provider.failures)
    assert len(failures) == (9 if invalid_attempts == 100 else invalid_attempts)
    call_ids = [failure.call_id for failure in failures]
    assert None not in call_ids
    assert len(set(call_ids)) == len(call_ids)
    if invalid_attempts >= 2:
        assert provider.failures[0] == provider.failures[1]
    for recorded, expected in zip(failures, provider.failures, strict=True):
        assert (
            LLMCallFailure.model_validate(
                recorded.model_dump(include=set(LLMCallFailure.model_fields))
            )
            == expected
        )

    defaults = [
        entry
        for entry in entries
        if isinstance(entry, FailedCallReplayEntry)
        and entry.error_type == "deadline_default"
    ]
    assert len(defaults) == {1: 0, 2: 1, 100: 8}[invalid_attempts]
    assert all(default.cost_usd == 0 for default in defaults)
    assert all(
        default.input_tokens == default.output_tokens == 0 for default in defaults
    )
    assert all(default.call_id is None for default in defaults)
    if invalid_attempts == 100:
        assert not provider.calls
        assert sum(default.rendered_vote_max is not None for default in defaults) == 4

    snapshot = budget.snapshot()
    assert compute_cost_usd(path) == pytest.approx(snapshot.cost_usd)
    (tmp_path / "roster.json").write_text(
        json.dumps(
            {
                "num_players": 4,
                "num_impostors": 1,
                "tasks_per_crewmate": DEFAULT_TASKS_PER_CREWMATE,
            }
        ),
        encoding="utf-8",
    )
    loader = ReplayLoader(tmp_path)
    assert loader.cost_summary().total_cost_usd == pytest.approx(snapshot.cost_usd)
    assert loader.load_replay(
        "headless-seed-2026"
    ).metadata.total_cost_usd == pytest.approx(snapshot.cost_usd)
    report = load_tournament_report(
        tmp_path,
        roles_by_seed={
            2026: {
                player_id: player.role
                for player_id, player in result.final_state.players.items()
            }
        },
        tasks_per_crewmate=DEFAULT_TASKS_PER_CREWMATE,
    )
    cost = report.games[0].cost
    assert cost.total_cost_usd == pytest.approx(snapshot.cost_usd)
    assert cost.total_input_tokens == snapshot.input_tokens
    assert cost.total_output_tokens == snapshot.output_tokens
    assert cost.by_model[DEFAULT_MEETING_MODEL] == pytest.approx(snapshot.cost_usd)
    assert sum(cost.by_model.values()) == pytest.approx(snapshot.cost_usd)
    model, versions, _, _, manifest_cost, _ = sample_provenance(
        tmp_path, 2026, "unused-fallback"
    )
    assert model == DEFAULT_MEETING_MODEL
    assert versions
    assert manifest_cost == f"{snapshot.cost_usd:.4f}"


def test_attempt_identity_survives_multiple_meetings_and_runner_reuse(
    tmp_path: Path,
) -> None:
    class SecondCaller(_EmergencyCaller):
        def decide(
            self, packet: ObservationPacket, public_map: PublicMapView
        ) -> ActionIntent:
            intent = super().decide(packet, public_map)
            if self.agent_id == "p-2" and packet.tick == 1:
                return EmergencyMeetingIntent(type="emergency", actor=self.agent_id)
            return intent

    def factory(agent_id: PlayerId, role: Role) -> SecondCaller:
        policy = (
            CrewmatePolicy(agent_id=agent_id)
            if role == "CREWMATE"
            else ImpostorPolicy(agent_id=agent_id)
        )
        return SecondCaller(agent_id=agent_id, role=role, policy=policy)

    provider = _InjectedProvider(
        abort_at=None,
        invalid_at=frozenset({1, 2, 10, 11}),
        identical_failure_metadata=True,
    )
    budget = GameBudget(max_cost_usd=1.0)
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    path = tmp_path / "first.jsonl"
    _game(path, runner, agent_factory=factory).run()
    meetings = read_meeting_entries(path)
    assert len(meetings) == 2
    failures = [
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, FailedCallReplayEntry) and entry.call_id is not None
    ]
    assert len(failures) == 4
    assert {entry.meeting_id for entry in failures} == {
        meeting.meeting_id for meeting in meetings
    }
    first_calls = len(provider.calls)
    assert compute_cost_usd(path) == pytest.approx(budget.snapshot().cost_usd)

    provider.invalid_at = frozenset({provider.attempts + 1, provider.attempts + 2})
    retry_path = tmp_path / "reuse.jsonl"
    _game(retry_path, runner).run()
    retry_meetings = read_meeting_entries(retry_path)
    assert len(retry_meetings) == 1
    assert retry_meetings[0].llm_calls == tuple(provider.calls[first_calls:])
    retry_failures = [
        entry
        for entry in read_all_entries(retry_path)
        if isinstance(entry, FailedCallReplayEntry) and entry.call_id is not None
    ]
    assert len(retry_failures) == 2
    assert len({entry.call_id for entry in [*failures, *retry_failures]}) == 6
    assert compute_cost_usd(path) + compute_cost_usd(retry_path) == pytest.approx(
        budget.snapshot().cost_usd
    )


def test_terminal_paid_success_that_exceeds_cap_is_recorded(tmp_path: Path) -> None:
    provider = _InjectedProvider(abort_at=None, input_tokens=100_000)
    budget = GameBudget(max_cost_usd=1.0, max_input_tokens=10_000)
    path = tmp_path / "overrun.jsonl"
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    with pytest.raises(BudgetExceededError):
        _game(path, runner).run()
    assert provider.attempts == 1
    assert len(provider.calls) == 1
    _assert_aborted_record(
        path, provider, budget, expected_error_type="BudgetExceededError"
    )


def test_recording_inside_budget_preserves_free_provider_cost_hints(
    tmp_path: Path,
) -> None:
    class FreeProvider(FakeProvider):
        preflight_cost_per_input_token_usd = 0.0
        preflight_cost_per_output_token_usd = 0.0

    budget = GameBudget(max_cost_usd=0.0)
    runner = build_default_meeting_runner(llm_client=FreeProvider(), budget=budget)
    path = tmp_path / "free.jsonl"
    _game(path, runner).run()
    assert len(read_meeting_entries(path)) == 1
    assert budget.snapshot().cost_usd == 0.0
    assert budget.snapshot().input_tokens > 0
    assert compute_cost_usd(path) == 0.0


@pytest.mark.parametrize(
    "boundary", ["_validate_runner_result", "apply_meeting_result"]
)
def test_completed_calls_survive_result_validation_or_application_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, boundary: str
) -> None:
    error = RuntimeError("injected result boundary failure")

    def abort(*args: object, **kwargs: object) -> None:
        raise error

    monkeypatch.setattr(f"orchestrator.game.{boundary}", abort)
    provider = _InjectedProvider(abort_at=None)
    budget = GameBudget(max_cost_usd=1.0)
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    path = tmp_path / "result-failure.jsonl"
    with pytest.raises(RuntimeError) as excinfo:
        _game(path, runner).run()
    assert excinfo.value is error
    # All four living agents spoke and voted before the boundary failed.
    assert len(provider.calls) == 8
    _assert_aborted_record(path, provider, budget)


def test_no_replay_abort_preserves_error_and_spend_without_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    def forbid_replay(*args: object, **kwargs: object) -> None:
        raise AssertionError("no-replay execution must not open a replay log")

    monkeypatch.setattr("orchestrator.game.ReplayLog", forbid_replay)
    provider = _InjectedProvider()
    budget = GameBudget(max_cost_usd=1.0)
    runner = build_default_meeting_runner(llm_client=provider, budget=budget)
    with pytest.raises(RuntimeError) as excinfo:
        _game(None, runner).run_unrecorded()
    assert excinfo.value is provider.abort_error
    assert provider.attempts == 2
    assert len(provider.calls) == 1
    call = provider.calls[0]
    assert budget.snapshot().cost_usd == pytest.approx(call.cost_usd)
    assert budget.snapshot().input_tokens == call.input_tokens
    assert budget.snapshot().output_tokens == call.output_tokens
    assert not list(tmp_path.iterdir())
