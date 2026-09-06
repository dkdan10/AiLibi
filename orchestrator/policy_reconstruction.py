"""Reproduce supported version-3 tactical decisions from entitled observations.

Readers still apply the original recorded engine actions. Reproducing an intent
is an additional check, never a way to repair or replace a divergent recording.
"""

from __future__ import annotations

from collections.abc import Sequence

from agents.memory.episodic import EpisodicEvent
from agents.memory.evidence_context import (
    ingest_public_meeting_roster,
    ingest_public_regroup,
)
from engine.actions import Action
from engine.events import EngineEvent
from engine.world import Map, WorldState
from meetings.schemas import MeetingResult
from meetings.manager import derive_meeting_outcome_summary
from observation.service import ObservationService
from orchestrator.boundary import (
    public_map_from_engine_map,
    translate_action_intents_for_tick,
)
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import (
    TacticalAgent,
    _absorb_meeting_beliefs,
    _notify_meeting_concluded,
    build_default_agent_factory,
)
from orchestrator.observation_delivery import ingest_event_observations_for_memories


class PolicyReconstruction:
    """Own real policy/FSM, pacing and plan state across one recorded game."""

    def __init__(
        self,
        *,
        initial_state: WorldState,
        game_map: Map,
        experiment: RecordedExperimentConfig,
        service: ObservationService,
        testimony_shapes: bool,
    ) -> None:
        if experiment.format_version != 3 or service.temporal_observation_version != 2:
            raise ValueError(
                "policy reconstruction requires format 3 and temporal version 2"
            )
        self.experiment = experiment
        self.service = service
        self.public_map = public_map_from_engine_map(game_map)
        self.testimony_shapes = testimony_shapes
        self.roster_impostor_count = sum(
            p.role == "IMPOSTOR" for p in initial_state.players.values()
        )
        self.agents: dict[str, TacticalAgent] = {}
        factory = build_default_agent_factory(experiment_config=experiment)
        for pid, player in sorted(initial_state.players.items()):
            agent = factory(pid, player.role)
            if type(agent) is not TacticalAgent:
                raise ValueError("version-3 reconstruction requires built-in agents")
            agent.bind_experiment(experiment, self.public_map)
            self.agents[pid] = agent
        self.memories = {pid: agent.memory for pid, agent in self.agents.items()}

    def before_tick(
        self,
        *,
        state: WorldState,
        last_events: Sequence[EngineEvent],
        actions: Sequence[Action],
    ) -> dict[str, tuple[EpisodicEvent, ...]]:
        intents = []
        delivered: dict[str, tuple[EpisodicEvent, ...]] = {}
        for pid, player in sorted(state.players.items()):
            if not player.alive:
                continue
            memory = self.memories[pid].episodic
            packet = self.service.build_packet(
                world_state=state, agent_id=pid, engine_events=last_events
            )
            before = len(memory.recent(since_tick=packet.tick))
            intents.append(self.agents[pid].decide(packet, self.public_map))
            delivered[pid] = memory.recent(since_tick=packet.tick)[before:]
        reproduced = translate_action_intents_for_tick(intents, world_state=state)
        if reproduced != tuple(actions):
            raise ValueError(
                f"recorded tactical actions disagree with the version-3 policy at tick {state.tick}"
            )
        return delivered

    def after_tick(
        self,
        *,
        source_state: WorldState,
        state: WorldState,
        events: Sequence[EngineEvent],
        actions: Sequence[Action],
    ) -> dict[str, tuple[EpisodicEvent, ...]]:
        return ingest_event_observations_for_memories(
            service=self.service,
            state=state,
            events=events,
            memories=self.memories,
            source_state=source_state,
            submitted_actions=actions,
        )

    def open_meeting(self, state: WorldState) -> None:
        living = tuple(sorted(pid for pid, p in state.players.items() if p.alive))
        dead = tuple(sorted(pid for pid, p in state.players.items() if not p.alive))
        for pid in living:
            ingest_public_meeting_roster(
                self.memories[pid], tick=state.tick, living_ids=living, dead_ids=dead
            )

    def complete_meeting(
        self, *, state: WorldState, result: MeetingResult, emergency: bool
    ) -> None:
        _absorb_meeting_beliefs(
            result=result,
            state=state,
            agents=self.agents,
            trigger_kind="emergency" if emergency else "report",
            testimony_shapes=self.testimony_shapes,
            evidence_reasoning_version=self.experiment.evidence_reasoning_version,
            public_account_version=self.experiment.public_account_version,
            attributed_testimony_version=self.experiment.attributed_testimony_version,
        )
        _notify_meeting_concluded(
            state=state,
            agents=self.agents,
            emergency_caller_id=result.triggered_by if emergency else None,
            outcome=derive_meeting_outcome_summary(result),
            roster_impostor_count=self.roster_impostor_count,
        )
        if self.experiment.meeting_reset == "hub_with_grace" and state.phase == "PLAY":
            living = tuple(sorted(pid for pid, p in state.players.items() if p.alive))
            for pid in living:
                ingest_public_regroup(
                    self.memories[pid],
                    tick=state.tick,
                    room=self.public_map.meeting_room,
                    player_ids=living,
                )
