"""V2 projection from event-local state; historical witness metadata stays v1."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from engine.actions import Action, DoTaskAction
from engine.entities import SabotageState
from engine.events import (
    ActionRejectedEvent,
    EngineEvent,
    KilledEvent,
    MovedEvent,
    SabotageRepairedEvent,
    SabotageStartedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
    TickAdvancedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.visibility import compute_visibility_for_player
from engine.world import Map, WorldState
from observation.packet import (
    EventObservationBatch,
    MovedPlayerView,
    ObserverPositionView,
    OwnKillEvent,
    OwnKillView,
    OwnTaskAttemptEvent,
    OwnTaskAttemptView,
    OwnTransitionEvent,
    PlayerView,
    TemporalEventPayload,
    TemporalEventView,
    WitnessedActionEvent,
    WitnessedMoveEvent,
)


def project_temporal_events(
    *,
    source_state: WorldState,
    submitted_actions: Sequence[Action],
    engine_events: Sequence[EngineEvent],
    agent_id: str,
    game_map: Map,
) -> EventObservationBatch | None:
    """Keep source order after entitlement filtering, without global ordinals.

    Walking is atomic: watching a visible actor take a public connecting door
    entitles its endpoint. Vent observations expose only the witnessed endpoint.
    Own transitions locate the observer before later actions in the same tick.
    """

    current = source_state
    rows: list[TemporalEventView] = []
    submitted = {action.actor: action for action in submitted_actions}
    if len(submitted) != len(submitted_actions):
        raise ValueError("v2 projection requires one submitted action per actor")
    for event in engine_events:
        if isinstance(event, TickAdvancedEvent):
            continue
        if event.tick != source_state.tick:
            raise ValueError("v2 events must match their explicit source state tick")
        observer = current.players[agent_id]
        actor_id = getattr(event, "actor", None)
        actor = current.players.get(actor_id) if actor_id is not None else None
        perceived: TemporalEventPayload | None = None
        can_watch = observer.alive and not observer.in_vent
        if isinstance(event, MovedEvent):
            assert actor is not None
            if event.from_room != actor.room:
                raise ValueError("movement source does not match event-local position")
            if (
                event.to_room != event.from_room
                and event.to_room not in game_map.room_neighbors(event.from_room)
            ):
                raise ValueError("movement endpoint is not a public connecting door")
            if event.actor == agent_id and event.from_room != event.to_room:
                perceived = OwnTransitionEvent(
                    from_room=event.from_room,
                    to_room=event.to_room,
                    was_in_vent=observer.in_vent,
                    in_vent=False,
                )
            elif can_watch and event.from_room != event.to_room:
                visible = compute_visibility_for_player(
                    observer_id=agent_id, world_state=current, game_map=game_map
                )
                if event.actor in visible.visible_player_ids:
                    perceived = WitnessedMoveEvent(
                        movement=MovedPlayerView(
                            id=event.actor,
                            from_room=event.from_room,
                            to_room=event.to_room,
                        )
                    )
            current = replace(
                current,
                players={
                    **current.players,
                    event.actor: replace(actor, room=event.to_room),
                },
            )
        elif isinstance(event, KilledEvent):
            if event.actor == agent_id:
                perceived = OwnKillEvent(
                    kill=OwnKillView(victim_id=event.target, room=event.room)
                )
            elif can_watch and agent_id != event.target and observer.room == event.room:
                perceived = WitnessedActionEvent(
                    player=PlayerView(id=event.actor, room=event.room, action="kill")
                )
            current = replace(
                current,
                players={
                    **current.players,
                    event.target: replace(current.players[event.target], alive=False),
                },
            )
        elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
            assert actor is not None
            if event.actor == agent_id:
                perceived = OwnTransitionEvent(
                    from_room=event.source_room,
                    to_room=event.destination_room,
                    was_in_vent=actor.in_vent,
                    in_vent=isinstance(event, VentEnteredEvent),
                )
            elif can_watch and observer.room in (
                event.source_room,
                event.destination_room,
            ):
                perceived = WitnessedActionEvent(
                    player=PlayerView(id=event.actor, room=observer.room, action="vent")
                )
            current = replace(
                current,
                players={
                    **current.players,
                    event.actor: replace(
                        actor,
                        room=event.destination_room,
                        in_vent=isinstance(event, VentEnteredEvent),
                    ),
                },
            )
        elif isinstance(
            event, (TaskCompletedEvent, TaskProgressedEvent, ActionRejectedEvent)
        ):
            action = submitted.get(event.actor)
            is_attempt = isinstance(action, DoTaskAction) and (
                not isinstance(event, ActionRejectedEvent) or event.action == "do_task"
            )
            if event.actor == agent_id and observer.alive and is_attempt:
                assert isinstance(action, DoTaskAction)
                if (
                    not isinstance(event, ActionRejectedEvent)
                    and event.task_id != action.payload.task_id
                ):
                    raise ValueError("task receipt disagrees with the submitted task")
                perceived = OwnTaskAttemptEvent(
                    attempt=OwnTaskAttemptView(
                        task_id=action.payload.task_id,
                        room=observer.room,
                        outcome="rejected"
                        if isinstance(event, ActionRejectedEvent)
                        else (
                            "completed"
                            if isinstance(event, TaskCompletedEvent)
                            else "progressed"
                        ),
                        rejection_reason=event.reason
                        if isinstance(event, ActionRejectedEvent)
                        else None,
                    )
                )
            elif is_attempt and can_watch and event.actor != agent_id:
                visible = compute_visibility_for_player(
                    observer_id=agent_id, world_state=current, game_map=game_map
                )
                if event.actor in visible.visible_player_ids:
                    assert actor is not None
                    perceived = WitnessedActionEvent(
                        player=PlayerView(
                            id=event.actor, room=actor.room, action="task"
                        )
                    )
        elif isinstance(event, SabotageStartedEvent):
            current = replace(
                current,
                sabotage=SabotageState(
                    kind=event.kind,
                    remaining_ticks=event.duration_ticks,
                    affected_rooms=event.affected_rooms,
                    active=True,
                ),
            )
        elif isinstance(event, SabotageRepairedEvent):
            current = replace(current, sabotage=None)
        if perceived is not None:
            rows.append(
                TemporalEventView(
                    observation_order=len(rows),
                    observer_before_event=ObserverPositionView(
                        room=observer.room, in_vent=observer.in_vent
                    ),
                    event=perceived,
                )
            )
    if not rows:
        return None
    recipient = source_state.players[agent_id]
    return EventObservationBatch(
        tick=source_state.tick,
        agent_id=agent_id,
        temporal_observation_version=2,
        ordered_events=tuple(rows),
        fellow_impostor_ids=tuple(
            sorted(
                pid
                for pid, player in source_state.players.items()
                if recipient.role == "IMPOSTOR"
                and player.role == "IMPOSTOR"
                and pid != agent_id
            )
        ),
    )
