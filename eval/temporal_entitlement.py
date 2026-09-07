"""Independent v2 channel oracle using ordered engine facts and public topology."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from engine.actions import Action, DoTaskAction
from engine.events import (
    ActionRejectedEvent,
    EngineEvent,
    KilledEvent,
    MovedEvent,
    SabotageRepairedEvent,
    SabotageStartedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.world import Map, WorldState
from observation.packet import EventObservationBatch


def assert_temporal_batch_entitled(
    batch: EventObservationBatch | None,
    *,
    agent_id: str,
    source_state: WorldState,
    state: WorldState,
    events: Sequence[EngineEvent],
    submitted_actions: Sequence[Action],
    game_map: Map,
) -> None:
    """Assert exact channels without using the producer or its visibility helper.

    Historical engine witness lists are deliberately irrelevant to this oracle.
    Both missing and extra evidence fail, including altered endpoints/order and
    the observer's event-local position. Player state after folding must match
    the actual engine result so an omitted transition cannot hide a bad frame.
    """
    positions = {pid: player.room for pid, player in source_state.players.items()}
    alive = {pid for pid, player in source_state.players.items() if player.alive}
    vented = {pid for pid, player in source_state.players.items() if player.in_vent}
    sabotage = source_state.sabotage
    mode = game_map.visibility_defaults.base
    if sabotage is not None and sabotage.active:
        mode = game_map.sabotages[sabotage.kind].affected_visibility
    expected: list[dict[str, Any]] = []
    attempts = {
        action.actor: action.payload.task_id
        for action in submitted_actions
        if isinstance(action, DoTaskAction)
    }
    for event in events:
        room = positions[agent_id]
        outside = agent_id in alive and agent_id not in vented
        before = {"room": room, "in_vent": agent_id in vented}
        effective_mode = mode
        if (
            mode == game_map.visibility_defaults.base
            and source_state.players[agent_id].role != "IMPOSTOR"
        ):
            effective_mode = "same_room_only"
        visible_rooms = {room}
        if effective_mode == "same_room_and_adjacent":
            visible_rooms.update(game_map.room_neighbors(room))
        payload: dict[str, Any] | None = None
        if isinstance(event, MovedEvent):
            assert event.from_room == positions[event.actor], (
                "movement source contradicts ordered positions"
            )
            assert (
                event.to_room == event.from_room
                or event.to_room in game_map.room_neighbors(event.from_room)
            ), "movement destination is not adjacent"
            if event.from_room != event.to_room:
                if event.actor == agent_id:
                    payload = {
                        "kind": "own_transition",
                        "from_room": event.from_room,
                        "to_room": event.to_room,
                        "was_in_vent": agent_id in vented,
                        "in_vent": False,
                    }
                elif (
                    outside
                    and event.actor in alive
                    and event.actor not in vented
                    and positions[event.actor] in visible_rooms
                ):
                    payload = {
                        "kind": "witnessed_move",
                        "movement": {
                            "id": event.actor,
                            "from_room": event.from_room,
                            "to_room": event.to_room,
                        },
                    }
            positions[event.actor] = event.to_room
        elif isinstance(event, KilledEvent):
            assert positions[event.actor] == positions[event.target] == event.room, (
                "kill room contradicts ordered positions"
            )
            if agent_id == event.actor:
                payload = {
                    "kind": "own_kill",
                    "kill": {"victim_id": event.target, "room": event.room},
                }
            elif outside and agent_id != event.target and room == event.room:
                payload = {
                    "kind": "witnessed_action",
                    "player": {"id": event.actor, "room": event.room, "action": "kill"},
                }
            alive.remove(event.target)
        elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
            assert event.source_room == positions[event.actor], (
                "vent source contradicts ordered positions"
            )
            assert (
                event.destination_room == game_map.vents[event.destination_vent_id].room
            ), "vent destination contradicts map"
            if agent_id == event.actor:
                payload = {
                    "kind": "own_transition",
                    "from_room": event.source_room,
                    "to_room": event.destination_room,
                    "was_in_vent": agent_id in vented,
                    "in_vent": isinstance(event, VentEnteredEvent),
                }
            elif outside and room in {event.source_room, event.destination_room}:
                payload = {
                    "kind": "witnessed_action",
                    "player": {"id": event.actor, "room": room, "action": "vent"},
                }
            positions[event.actor] = event.destination_room
            if isinstance(event, VentEnteredEvent):
                vented.add(event.actor)
            else:
                vented.discard(event.actor)
        elif isinstance(
            event, (TaskCompletedEvent, TaskProgressedEvent, ActionRejectedEvent)
        ):
            actual_attempt = event.actor in attempts and (
                not isinstance(event, ActionRejectedEvent) or event.action == "do_task"
            )
            if actual_attempt:
                if not isinstance(event, ActionRejectedEvent):
                    assert event.task_id == attempts[event.actor], (
                        "receipt task differs from submitted attempt"
                    )
                if event.actor == agent_id and agent_id in alive:
                    outcome = (
                        "rejected"
                        if isinstance(event, ActionRejectedEvent)
                        else "completed"
                        if isinstance(event, TaskCompletedEvent)
                        else "progressed"
                    )
                    payload = {
                        "kind": "own_task_attempt",
                        "attempt": {
                            "task_id": attempts[event.actor],
                            "room": room,
                            "outcome": outcome,
                            "rejection_reason": event.reason
                            if isinstance(event, ActionRejectedEvent)
                            else None,
                        },
                    }
                elif (
                    outside
                    and event.actor != agent_id
                    and event.actor in alive
                    and event.actor not in vented
                    and positions[event.actor] in visible_rooms
                ):
                    payload = {
                        "kind": "witnessed_action",
                        "player": {
                            "id": event.actor,
                            "room": positions[event.actor],
                            "action": "task",
                        },
                    }
        elif isinstance(event, SabotageStartedEvent):
            mode = game_map.sabotages[event.kind].affected_visibility
        elif isinstance(event, SabotageRepairedEvent):
            mode = game_map.visibility_defaults.base
        if payload is not None:
            assert event.tick == source_state.tick, (
                "event source tick differs from explicit pre-state"
            )
            expected.append(
                {
                    "observation_order": len(expected),
                    "observer_before_event": before,
                    "event": payload,
                }
            )
    assert positions == {pid: player.room for pid, player in state.players.items()}, (
        "ordered events do not explain final positions"
    )
    assert alive == {pid for pid, player in state.players.items() if player.alive}, (
        "ordered events do not explain final life state"
    )
    assert vented == {pid for pid, player in state.players.items() if player.in_vent}, (
        "ordered events do not explain final vent state"
    )
    if batch is None:
        assert not expected, "entitled event batch was not delivered"
        return
    assert expected, "empty v2 evidence must not produce a batch"
    assert batch.agent_id == agent_id and batch.tick == source_state.tick, (
        "wrong batch recipient or source tick"
    )
    assert batch.temporal_observation_version == 2, "wrong batch version"
    assert (
        not batch.own_kill and not batch.witnessed_actions and not batch.moved_players
    ), "v2 mixed legacy channels"
    assert [row.model_dump() for row in batch.ordered_events] == expected, (
        "v2 missing, extra or incorrectly ordered/positioned evidence"
    )
    fellows = tuple(
        sorted(
            pid
            for pid, player in source_state.players.items()
            if source_state.players[agent_id].role == "IMPOSTOR"
            and player.role == "IMPOSTOR"
            and pid != agent_id
        )
    )
    assert batch.fellow_impostor_ids == fellows, "v2 team identity is unearned"
