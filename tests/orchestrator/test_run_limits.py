"""One external wall deadline stops synchronous ticks and awaited meetings."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from agents.tactical.crewmate_policy import CrewmatePolicy
from engine.world import load_canonical_map
from llm.budget import GameBudget
from llm.client import LLMResponse
from llm.fake_provider import FakeProvider
from observation.action_intent import ActionIntent, EmergencyMeetingIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import HeadlessGame, TacticalAgent, build_default_meeting_runner
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    compute_cost_usd,
    read_all_entries,
    read_replay_entries,
)
from orchestrator.run_limits import RunDeadline, RunDeadlineExceeded
from orchestrator.scheduler import TickScheduler


class EmergencyCaller(TacticalAgent):
    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        super().decide(packet, public_map)
        if self.agent_id == "p-1" and packet.tick == 0:
            return EmergencyMeetingIntent(type="emergency", actor=self.agent_id)
        return WaitIntent(type="wait", actor=self.agent_id)


class HangingProvider(FakeProvider):
    def __init__(self) -> None:
        super().__init__()
        self.attempts = 0
        self.cancelled = False

    async def complete(self, **kwargs: Any) -> LLMResponse:
        self.attempts += 1
        if self.attempts == 2:
            try:
                await asyncio.Future[None]()
            except asyncio.CancelledError:
                self.cancelled = True
                raise
        response = await super().complete(**kwargs)
        return response.model_copy(update={"cost_usd": 0.01})


def test_wall_deadline_cancels_meeting_and_retains_success(tmp_path: Path) -> None:
    provider = HangingProvider()
    budget = GameBudget()
    deadline = RunDeadline(0.25)
    game = HeadlessGame(
        seed=2026,
        num_players=4,
        game_map=load_canonical_map(),
        agent_factory=lambda agent_id, role: EmergencyCaller(
            agent_id=agent_id, role=role, policy=CrewmatePolicy(agent_id=agent_id)
        ),
        replay_path=tmp_path / "replay.jsonl",
        scheduler=TickScheduler(max_ticks=3),
        meeting_runner=build_default_meeting_runner(
            llm_client=provider, budget=budget, deadline=deadline
        ),
        deadline=deadline,
    )
    with pytest.raises(RunDeadlineExceeded):
        game.run()
    assert provider.attempts == 2
    assert provider.cancelled
    entries = read_all_entries(tmp_path / "replay.jsonl")
    aborted = [
        entry for entry in entries if isinstance(entry, AbortedMeetingReplayEntry)
    ]
    assert len(aborted) == len(aborted[0].llm_calls) == 1
    assert aborted[0].error_type == "RunDeadlineExceeded"
    assert (
        compute_cost_usd(tmp_path / "replay.jsonl")
        == budget.snapshot().cost_usd
        == 0.01
    )


def test_tick_loop_checks_deadline_without_a_meeting(tmp_path: Path) -> None:
    class WaitingAgent(EmergencyCaller):
        def decide(
            self, packet: ObservationPacket, public_map: PublicMapView
        ) -> ActionIntent:
            return WaitIntent(type="wait", actor=self.agent_id)

    clock = iter([0.0, 0.0, 2.0])
    deadline = RunDeadline(1, clock=lambda: next(clock))
    game = HeadlessGame(
        seed=1,
        num_players=4,
        game_map=load_canonical_map(),
        agent_factory=lambda agent_id, role: WaitingAgent(
            agent_id=agent_id, role=role, policy=CrewmatePolicy(agent_id=agent_id)
        ),
        replay_path=tmp_path / "replay.jsonl",
        scheduler=TickScheduler(max_ticks=3),
        deadline=deadline,
    )
    with pytest.raises(RunDeadlineExceeded):
        game.run()
    assert len(read_replay_entries(tmp_path / "replay.jsonl")) == 1
