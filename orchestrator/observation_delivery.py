"""Shared live/reconstruction delivery of entitled source-time observations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from agents.memory.episodic import EpisodicEvent
from agents.memory.store import AgentMemory
from agents.perception import ingest_event_observations
from engine.events import EngineEvent
from engine.world import WorldState
from observation.packet import EventObservationBatch
from observation.service import ObservationService


def event_observation_batches(
    *,
    service: ObservationService,
    state: WorldState,
    events: Sequence[EngineEvent],
) -> dict[str, EventObservationBatch]:
    """Include recipients killed later in the batch; their witnessed facts persist."""

    if not service.temporal_observations:
        return {}
    batches: dict[str, EventObservationBatch] = {}
    for agent_id in sorted(state.players):
        batch = service.build_event_observations(
            world_state=state, agent_id=agent_id, engine_events=events
        )
        if batch is not None:
            batches[agent_id] = batch
    return batches


def ingest_event_observations_for_memories(
    *,
    service: ObservationService,
    state: WorldState,
    events: Sequence[EngineEvent],
    memories: Mapping[str, AgentMemory],
) -> dict[str, tuple[EpisodicEvent, ...]]:
    """Apply the live batch projection and return newly delivered citation rows."""

    delivered: dict[str, tuple[EpisodicEvent, ...]] = {}
    for agent_id, batch in event_observation_batches(
        service=service, state=state, events=events
    ).items():
        memory = memories.get(agent_id)
        if memory is None:
            continue
        delivered[agent_id] = ingest_event_observations(
            batch=batch, memory=memory.episodic, beliefs=memory.beliefs
        )
    return delivered
