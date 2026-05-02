from __future__ import annotations

from pathlib import Path

from engine.entities import PlayerId
from engine.visibility import VisibilityResult, compute_visibility_for_player
from engine.world import Map, TaskId, WorldState
from observation.audit import ObservationAuditLog
from observation.packet import (
    AudibleEvent,
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)


class ObservationService:
    """Single boundary object that exposes engine truth as ObservationPackets."""

    def __init__(self, *, game_map: Map, audit_log_path: Path) -> None:
        self._game_map = game_map
        self._audit_log = ObservationAuditLog(audit_log_path)

    def build_packet(self, *, world_state: WorldState, agent_id: PlayerId) -> ObservationPacket:
        visibility = compute_visibility_for_player(
            observer_id=agent_id,
            world_state=world_state,
            game_map=self._game_map,
        )
        packet = self._build_packet_from_visibility(
            world_state=world_state,
            agent_id=agent_id,
            visibility=visibility,
        )
        self._audit_log.record_packet(packet)
        return packet

    def _build_packet_from_visibility(
        self,
        *,
        world_state: WorldState,
        agent_id: PlayerId,
        visibility: VisibilityResult,
    ) -> ObservationPacket:
        player = world_state.players.get(agent_id)
        if player is None:
            raise ValueError(f"unknown agent id: {agent_id}")

        pending_task_id = self._pending_task_id_for_agent(world_state=world_state, agent_id=agent_id)
        visible_players = [
            PlayerView(
                id=player_id,
                room=world_state.players[player_id].room,
                action=self._action_name(world_state.players[player_id].last_action),
            )
            for player_id in visibility.visible_player_ids
        ]
        visible_bodies = [
            BodyView(id=body_id, room=world_state.bodies[body_id].room)
            for body_id in visibility.visible_body_ids
        ]
        packet = ObservationPacket(
            tick=world_state.tick,
            agent_id=agent_id,
            self_state=SelfView(
                room=player.room,
                role=player.role,
                pending_task_id=pending_task_id,
            ),
            visible_players=visible_players,
            visible_bodies=visible_bodies,
            audible_events=self._audible_events(world_state=world_state, visibility=visibility),
            global_state=self._global_view(world_state=world_state),
            cooldown=world_state.cooldowns.get(agent_id),
        )
        return packet

    def _audible_events(
        self,
        *,
        world_state: WorldState,
        visibility: VisibilityResult,
    ) -> list[AudibleEvent]:
        del visibility
        events: list[AudibleEvent] = []
        if world_state.sabotage is not None and world_state.sabotage.active:
            events.append(AudibleEvent(kind="sabotage_alarm", room=None))
        return events

    def _global_view(self, *, world_state: WorldState) -> GlobalView:
        tasks_total = len(world_state.tasks)
        tasks_completed = sum(1 for task in world_state.tasks.values() if task.completed)
        task_completion_percent = (tasks_completed / tasks_total) if tasks_total > 0 else 0.0

        return GlobalView(
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            task_completion_percent=task_completion_percent,
            sabotage_active=(world_state.sabotage is not None and world_state.sabotage.active),
            sabotage_kind=world_state.sabotage.kind if world_state.sabotage is not None else None,
        )

    def _pending_task_id_for_agent(self, *, world_state: WorldState, agent_id: PlayerId) -> TaskId | None:
        owned_unfinished_tasks = [
            task.id
            for task in world_state.tasks.values()
            if task.owner == agent_id and not task.completed
        ]
        if not owned_unfinished_tasks:
            return None
        return sorted(owned_unfinished_tasks)[0]

    def _action_name(self, action: object | None) -> str | None:
        if action is None:
            return None
        action_type = getattr(action, "type", None)
        if action_type is None:
            return type(action).__name__
        if not isinstance(action_type, str):
            raise ValueError("action.type must be a string when present")
        return action_type
