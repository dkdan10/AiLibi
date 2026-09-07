from __future__ import annotations

from collections.abc import Sequence

from pydantic import TypeAdapter

from engine.actions import Action
from engine.world import Map, WorldState
from observation.action_intent import ActionIntent
from observation.body_ids import public_body_id
from observation.public_map import PublicMapView
from orchestrator.action_ordering import order_actions_for_tick

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def public_map_from_engine_map(game_map: Map) -> PublicMapView:
    """Translate engine-owned map data into public agent topology."""

    room_ids = tuple(sorted(game_map.rooms))
    vent_ids = tuple(sorted(game_map.vents))
    task_ids = tuple(sorted(game_map.tasks))
    return PublicMapView(
        map_id=game_map.id,
        room_ids=room_ids,
        room_neighbors={
            room_id: game_map.room_neighbors(room_id) for room_id in room_ids
        },
        vent_graph={vent_id: game_map.vent_neighbors(vent_id) for vent_id in vent_ids},
        vent_rooms={vent_id: game_map.vents[vent_id].room for vent_id in vent_ids},
        task_locations={task_id: game_map.tasks[task_id].room for task_id in task_ids},
        spawn_room=game_map.spawn.room,
        meeting_room=game_map.meeting.room,
        emergency_button_room=game_map.emergency.button_room,
    )


def translate_action_intent(
    intent: ActionIntent, *, world_state: WorldState | None = None
) -> Action:
    """Translate public body handles at the privileged engine boundary.

    Recorded engine actions and callers using established internal identifiers
    remain valid. Unknown handles reach the engine's ordinary report rejection;
    translation never grants report legality or guesses a victim from a string.
    """

    action_data = intent.model_dump(mode="python")
    if intent.type == "report" and world_state is not None:
        matches = [
            body.id
            for body in world_state.bodies.values()
            if public_body_id(body.player_id) == intent.payload.body_id
        ]
        if len(matches) > 1:
            raise ValueError("multiple engine bodies share one public victim handle")
        if matches:
            action_data["payload"]["body_id"] = matches[0]
    return _ACTION_ADAPTER.validate_python(action_data)


def translate_action_intents_for_tick(
    intents: Sequence[ActionIntent],
    *,
    world_state: WorldState | None = None,
) -> tuple[Action, ...]:
    """Translate and sort the only action batch shape future agents may submit."""

    actions = [
        translate_action_intent(intent, world_state=world_state) for intent in intents
    ]
    return order_actions_for_tick(actions)
