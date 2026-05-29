from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from engine.entities import PlayerId
from engine.events import EngineEvent, KilledEvent, VentEnteredEvent, VentExitedEvent
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


@dataclass(frozen=True)
class _ObservedAction:
    action: str
    room: str
    audible_room: str | None = None


class ObservationService:
    """Single boundary object that exposes engine truth as ObservationPackets."""

    def __init__(self, *, game_map: Map, audit_log_path: Path) -> None:
        self._game_map = game_map
        self._audit_log = ObservationAuditLog(audit_log_path)

    def close(self) -> None:
        """Release the audit log's append handle (idempotent).

        The service owns the :class:`ObservationAuditLog`; closing it flushes
        and releases the file descriptor at end of game. Builds after a close
        re-open the handle lazily, so close is safe to call between batches.
        """

        self._audit_log.close()

    def build_packet(
        self,
        *,
        world_state: WorldState,
        agent_id: PlayerId,
        engine_events: Sequence[EngineEvent],
    ) -> ObservationPacket:
        visibility = compute_visibility_for_player(
            observer_id=agent_id,
            world_state=world_state,
            game_map=self._game_map,
        )
        packet = self._build_packet_from_visibility(
            world_state=world_state,
            agent_id=agent_id,
            visibility=visibility,
            engine_events=engine_events,
        )
        self._audit_log.record_packet(packet)
        return packet

    def _build_packet_from_visibility(
        self,
        *,
        world_state: WorldState,
        agent_id: PlayerId,
        visibility: VisibilityResult,
        engine_events: Sequence[EngineEvent],
    ) -> ObservationPacket:
        player = world_state.players.get(agent_id)
        if player is None:
            raise ValueError(f"unknown agent id: {agent_id}")

        pending_task_id = self._pending_task_id_for_agent(
            world_state=world_state, agent_id=agent_id
        )
        observed_actions = self._observed_actions_for_agent(
            agent_id=agent_id,
            engine_events=engine_events,
        )
        visible_players = self._visible_players(
            world_state=world_state,
            visibility=visibility,
            observed_actions=observed_actions,
        )
        cooldown = (
            world_state.cooldowns.get(agent_id) if player.role == "IMPOSTOR" else None
        )
        visible_bodies = tuple(
            BodyView(
                id=body_id,
                room=world_state.bodies[body_id].room,
                victim_id=world_state.bodies[body_id].player_id,
            )
            for body_id in visibility.visible_body_ids
        )
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
            audible_events=self._audible_events(
                world_state=world_state,
                observed_actions=observed_actions,
            ),
            global_state=self._global_view(world_state=world_state),
            cooldown=cooldown,
        )
        return packet

    def _visible_players(
        self,
        *,
        world_state: WorldState,
        visibility: VisibilityResult,
        observed_actions: Mapping[PlayerId, _ObservedAction],
    ) -> tuple[PlayerView, ...]:
        visible_players_by_id: dict[PlayerId, PlayerView] = {}
        for player_id in visibility.visible_player_ids:
            observed_action = observed_actions.get(player_id)
            visible_players_by_id[player_id] = PlayerView(
                id=player_id,
                room=observed_action.room
                if observed_action is not None
                else world_state.players[player_id].room,
                action=observed_action.action if observed_action is not None else None,
            )

        for player_id, observed_action in observed_actions.items():
            if player_id not in world_state.players:
                raise ValueError(f"event references unknown actor: {player_id}")
            if player_id not in visible_players_by_id:
                visible_players_by_id[player_id] = PlayerView(
                    id=player_id,
                    room=observed_action.room,
                    action=observed_action.action,
                )

        return tuple(
            visible_players_by_id[player_id]
            for player_id in sorted(visible_players_by_id)
        )

    def _audible_events(
        self,
        *,
        world_state: WorldState,
        observed_actions: Mapping[PlayerId, _ObservedAction],
    ) -> tuple[AudibleEvent, ...]:
        events: list[AudibleEvent] = []
        vent_rooms = tuple(
            sorted(
                {
                    observed_action.audible_room
                    for observed_action in observed_actions.values()
                    if observed_action.action == "vent"
                    and observed_action.audible_room is not None
                }
            )
        )
        events.extend(
            AudibleEvent(kind="vent_use_heard", room=room) for room in vent_rooms
        )
        if world_state.sabotage is not None and world_state.sabotage.active:
            events.append(AudibleEvent(kind="sabotage_alarm", room=None))
        return tuple(events)

    def _observed_actions_for_agent(
        self,
        *,
        agent_id: PlayerId,
        engine_events: Sequence[EngineEvent],
    ) -> dict[PlayerId, _ObservedAction]:
        observed_actions: dict[PlayerId, _ObservedAction] = {}
        for event in engine_events:
            if isinstance(event, KilledEvent):
                if agent_id in event.witnesses:
                    observed_actions[event.actor] = _ObservedAction(
                        action="kill",
                        room=event.room,
                    )
            elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
                vent_observation = self._vent_observation_for_agent(
                    event=event,
                    agent_id=agent_id,
                )
                if vent_observation is not None:
                    observed_actions[event.actor] = vent_observation
        return observed_actions

    def _vent_observation_for_agent(
        self,
        *,
        event: VentEnteredEvent | VentExitedEvent,
        agent_id: PlayerId,
    ) -> _ObservedAction | None:
        witnessed_rooms: list[str] = []
        if agent_id in event.source_witnesses:
            witnessed_rooms.append(event.source_room)
        if agent_id in event.destination_witnesses:
            witnessed_rooms.append(event.destination_room)
        if not witnessed_rooms:
            return None
        return _ObservedAction(
            action="vent",
            room=witnessed_rooms[0],
            audible_room=witnessed_rooms[0],
        )

    def _global_view(self, *, world_state: WorldState) -> GlobalView:
        tasks_total = len(world_state.tasks)
        tasks_completed = sum(
            1 for task in world_state.tasks.values() if task.completed
        )
        task_completion_percent = (
            (tasks_completed / tasks_total) if tasks_total > 0 else 0.0
        )

        return GlobalView(
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            task_completion_percent=task_completion_percent,
            sabotage_active=(
                world_state.sabotage is not None and world_state.sabotage.active
            ),
            sabotage_kind=world_state.sabotage.kind
            if world_state.sabotage is not None
            else None,
        )

    def _pending_task_id_for_agent(
        self, *, world_state: WorldState, agent_id: PlayerId
    ) -> TaskId | None:
        owned_unfinished_tasks = [
            task.id
            for task in world_state.tasks.values()
            if task.owner == agent_id and not task.completed
        ]
        if not owned_unfinished_tasks:
            return None
        return sorted(owned_unfinished_tasks)[0]
