"""A bounded search transition using only the actor's entitled observations."""

from __future__ import annotations

from typing import Literal

from agents.memory.episodic import MemoryStore
from agents.memory.investigation import (
    MAX_SOURCE_AGE_TICKS,
    MAX_VISITED_ROOMS,
    MISSING_SIGHTING_TICKS,
    SEARCH_DURATION_TICKS,
    ConsumedInvestigationSource,
    InvestigationEvidence,
    InvestigationPlan,
    InvestigationState,
    investigation_packet_sha256,
)
from agents.tactical.pathing import find_path
from observation.action_intent import ActionIntent, MoveIntent, ReportBodyIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView


def has_recent_witnessed_danger(
    memory: MemoryStore, *, packet: ObservationPacket
) -> bool:
    """Retain a source-time kill through its next decision, until a meeting.

    Event delivery precedes the next snapshot. Looking only at that snapshot's
    tick loses a just-witnessed kill, especially after the observer moves away.
    A meeting boundary ends this immediate response; old claims cannot renew it.
    """

    events = memory.recent(since_tick=max(0, packet.tick - 1))
    boundary = max(
        (row.tick for row in events if row.type == "meeting_boundary"), default=-1
    )
    return any(
        row.type == "saw_player"
        and row.provenance == "observed"
        and row.payload.get("action") == "kill"
        and row.tick == packet.tick - 1
        and row.tick >= boundary
        and row.payload.get("source_tick") == row.tick
        and row.payload.get("observation_phase") == "event"
        and row.observation_id is not None
        for row in events
    )


def _visible_body_intent(
    packet: ObservationPacket, public_map: PublicMapView
) -> ActionIntent | None:
    """Approach only a currently visible corpse, one public-map step at a time."""

    choices: list[tuple[int, str, tuple[str, ...]]] = []
    for body in packet.visible_bodies:
        if body.room not in public_map.room_ids:
            raise ValueError("visible body room is absent from the public map")
        try:
            path = find_path(
                public_map=public_map, start=packet.self_state.room, goal=body.room
            )
        except ValueError:
            continue
        choices.append((len(path), body.id, path))
    if not choices:
        return None
    _, body_id, path = min(choices)
    if len(path) == 1:
        return ReportBodyIntent.model_validate(
            {
                "type": "report",
                "actor": packet.agent_id,
                "payload": {"body_id": body_id},
            }
        )
    return MoveIntent.model_validate(
        {"type": "move", "actor": packet.agent_id, "payload": {"to_room": path[1]}}
    )


def _search_step(
    plan: InvestigationPlan,
    *,
    packet: ObservationPacket,
    public_map: PublicMapView,
) -> tuple[InvestigationPlan | None, ActionIntent | None]:
    """Inspect actual arrival rooms, then choose one reachable search step."""

    room = packet.self_state.room
    visited = plan.visited_rooms
    neighbors = public_map.room_neighbors[plan.last_known_room]
    if room not in visited and (
        room == plan.last_known_room
        or (plan.last_known_room in visited and room in neighbors)
    ):
        visited = (*visited, room)
    if len(visited) >= MAX_VISITED_ROOMS:
        return None, None
    plan = plan.model_copy(update={"visited_rooms": visited})
    goals = (
        (plan.last_known_room,)
        if plan.last_known_room not in visited
        else tuple(candidate for candidate in neighbors if candidate not in visited)
    )
    paths: list[tuple[int, str, tuple[str, ...]]] = []
    for goal in goals:
        try:
            path = find_path(public_map=public_map, start=room, goal=goal)
        except ValueError:
            # Disconnection is a legitimate end to a bounded search.
            continue
        paths.append((len(path), goal, path))
    if not paths:
        return None, None
    _, _, path = min(paths)
    return plan, MoveIntent.model_validate(
        {"type": "move", "actor": packet.agent_id, "payload": {"to_room": path[1]}}
    )


def transition_investigation(
    state: InvestigationState | None,
    *,
    packet: ObservationPacket,
    evidence: InvestigationEvidence,
    public_map: PublicMapView,
    anchor_intent: ActionIntent,
    investigation_version: Literal[1] | None,
    urgent: bool = False,
) -> InvestigationState:
    """Return the complete next plan/cache without mutating memory or the FSM.

    The runtime checks the cache before ingesting a repeated packet. This pure
    duplicate check additionally protects direct callers. ``urgent`` identifies
    the ordinary policy's danger/emergency walk, which has the same intent shape
    as discretionary task travel.
    """

    if investigation_version is not None and (
        type(investigation_version) is not int or investigation_version != 1
    ):
        raise ValueError("unsupported investigation version")
    if anchor_intent.actor != packet.agent_id:
        raise ValueError("investigation anchor belongs to a different actor")
    if packet.self_state.room not in public_map.room_ids:
        raise ValueError("investigation actor room is absent from the public map")
    digest = investigation_packet_sha256(packet)
    previous = state or InvestigationState()
    if previous.last_processed_tick is not None:
        if packet.tick < previous.last_processed_tick:
            raise ValueError("investigation decision tick moved backwards")
        if packet.tick == previous.last_processed_tick:
            if digest != previous.last_packet_sha256:
                raise ValueError("conflicting investigation packets on one tick")
            return previous

    enabled = investigation_version == 1 and packet.self_state.role == "CREWMATE"
    if enabled and packet.temporal_observation_version != 2:
        raise ValueError("investigation requires clock-corrected observations")
    for sighting in evidence.sightings:
        if sighting.source_tick > packet.tick:
            raise ValueError("investigation received a future sighting")
        if sighting.last_known_room not in public_map.room_ids:
            raise ValueError(
                "investigation sighting room is absent from the public map"
            )

    consumed = {entry.target_id: entry for entry in previous.consumed_sources}
    plan = previous.active_plan if enabled else None
    visible = {player.id for player in packet.visible_players}
    known_dead = set(evidence.known_dead_ids)
    protected = (
        urgent
        or anchor_intent.type in ("report", "emergency", "repair_sabotage", "do_task")
        or bool(packet.visible_bodies)
        or (
            packet.global_state.sabotage_active
            and packet.global_state.sabotage_is_gating
        )
        or any(player.action == "kill" for player in packet.visible_players)
    )
    ended = False
    if plan is not None and (
        packet.tick >= plan.expires_tick
        or plan.target_id in known_dead | visible
        or any(
            sighting.target_id == plan.target_id
            and sighting.source_observation_id != plan.source_observation_id
            and sighting.source_tick >= plan.source_tick
            for sighting in evidence.sightings
        )
    ):
        plan, ended = None, True

    if enabled and plan is None and not ended and not protected:
        candidates = sorted(
            (
                sighting
                for sighting in evidence.sightings
                if sighting.target_id in evidence.known_player_ids
                and sighting.target_id not in known_dead | visible | {packet.agent_id}
                and MISSING_SIGHTING_TICKS
                <= packet.tick - sighting.source_tick
                <= MAX_SOURCE_AGE_TICKS
                and (
                    sighting.target_id not in consumed
                    or sighting.source_tick > consumed[sighting.target_id].source_tick
                )
            ),
            key=lambda sighting: (
                sighting.source_tick,
                sighting.target_id,
                sighting.source_observation_id,
            ),
        )
        if candidates:
            source = candidates[0]
            consumed[source.target_id] = ConsumedInvestigationSource(
                target_id=source.target_id,
                source_observation_id=source.source_observation_id,
                source_tick=source.source_tick,
            )
            plan = InvestigationPlan(
                target_id=source.target_id,
                source_observation_id=source.source_observation_id,
                source_tick=source.source_tick,
                last_known_room=source.last_known_room,
                started_tick=packet.tick,
                expires_tick=packet.tick + SEARCH_DURATION_TICKS,
                visited_rooms=(),
            )

    intent = (
        _visible_body_intent(packet, public_map) if enabled else None
    ) or anchor_intent
    if plan is not None:
        plan, search_intent = _search_step(plan, packet=packet, public_map=public_map)
        if not protected and search_intent is not None:
            intent = search_intent
    return InvestigationState(
        active_plan=plan,
        consumed_sources=tuple(consumed[target] for target in sorted(consumed)),
        last_processed_tick=packet.tick,
        last_packet_sha256=digest,
        last_intent=intent,
    )
