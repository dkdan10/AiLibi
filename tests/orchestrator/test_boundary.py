from __future__ import annotations

import pytest
from pydantic import TypeAdapter

from observation.action_intent import ActionIntent
from orchestrator.action_ordering import ActionBatchValidationError
from orchestrator.boundary import (
    public_map_from_engine_map,
    translate_action_intent,
    translate_action_intents_for_tick,
)
from engine.world import load_canonical_map

_ACTION_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)


def _intent(data: object) -> ActionIntent:
    return _ACTION_INTENT_ADAPTER.validate_python(data)


def test_public_map_from_engine_map_exposes_sorted_public_topology() -> None:
    public_map = public_map_from_engine_map(load_canonical_map())

    assert public_map.map_id == "canonical_1"
    assert public_map.room_ids == tuple(sorted(public_map.room_ids))
    assert public_map.room_neighbors["CAFETERIA"] == (
        "EAST_HALL",
        "UPPER_HALL",
        "WEST_HALL",
    )
    assert public_map.vent_graph["REACTOR_VENT"] == (
        "ADMIN_VENT",
        "STORAGE_VENT",
    )
    assert public_map.vent_rooms["ADMIN_VENT"] == "ADMIN"
    assert public_map.task_locations["swipe_card"] == "ADMIN"
    assert public_map.spawn_room == "CAFETERIA"
    assert public_map.meeting_room == "CAFETERIA"
    assert public_map.emergency_button_room == "CAFETERIA"
    assert set(public_map.model_dump(mode="json")) == {
        "map_id",
        "room_ids",
        "room_neighbors",
        "vent_graph",
        "vent_rooms",
        "task_locations",
        "spawn_room",
        "meeting_room",
        "emergency_button_room",
    }


def test_translate_action_intent_returns_matching_engine_action() -> None:
    action = translate_action_intent(
        _intent(
            {
                "type": "move",
                "actor": "p-1",
                "payload": {"to_room": "ADMIN"},
            }
        )
    )

    assert action.type == "move"
    assert action.actor == "p-1"
    assert action.payload.to_room == "ADMIN"


def test_translate_repair_sabotage_intent_returns_matching_engine_action() -> None:
    action = translate_action_intent(
        _intent(
            {
                "type": "repair_sabotage",
                "actor": "p-1",
                "payload": {"kind": "lights"},
            }
        )
    )

    assert action.type == "repair_sabotage"
    assert action.actor == "p-1"
    assert action.payload.kind == "lights"


def test_translate_action_intents_for_tick_returns_deterministic_order() -> None:
    intents = [
        _intent({"type": "wait", "actor": "p-2", "payload": {}}),
        _intent(
            {
                "type": "move",
                "actor": "p-1",
                "payload": {"to_room": "ADMIN"},
            }
        ),
        _intent({"type": "wait", "actor": "p-3", "payload": {}}),
    ]

    actions = translate_action_intents_for_tick(intents)

    assert [action.actor for action in actions] == [
        "p-1",
        "p-2",
        "p-3",
    ]
    assert [intent.actor for intent in intents] == [
        "p-2",
        "p-1",
        "p-3",
    ]


def test_translate_action_intents_for_tick_rejects_duplicate_actors() -> None:
    intents = [
        _intent({"type": "wait", "actor": "p-1", "payload": {}}),
        _intent(
            {
                "type": "move",
                "actor": "p-1",
                "payload": {"to_room": "ADMIN"},
            }
        ),
    ]

    with pytest.raises(ActionBatchValidationError, match="p-1"):
        translate_action_intents_for_tick(intents)
