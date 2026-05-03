from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from observation.action_intent import ActionIntent
from observation.public_map import PublicMapView

_ACTION_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)


def test_action_intent_union_accepts_supported_intent_types() -> None:
    payloads = [
        {"type": "move", "actor": "player-1", "payload": {"to_room": "ADMIN"}},
        {"type": "do_task", "actor": "player-1", "payload": {"task_id": "swipe_card"}},
        {"type": "kill", "actor": "impostor", "payload": {"target": "player-1"}},
        {"type": "vent", "actor": "impostor", "payload": {"vent_id": "ADMIN_VENT"}},
        {"type": "report", "actor": "player-1", "payload": {"body_id": "body-1"}},
        {"type": "emergency", "actor": "player-1", "payload": {"reason": "test"}},
        {"type": "sabotage", "actor": "impostor", "payload": {"kind": "lights"}},
        {"type": "repair_sabotage", "actor": "player-1", "payload": {"kind": "lights"}},
        {"type": "wait", "actor": "player-1", "payload": {}},
    ]

    intents = [_ACTION_INTENT_ADAPTER.validate_python(payload) for payload in payloads]

    assert [intent.type for intent in intents] == [
        "move",
        "do_task",
        "kill",
        "vent",
        "report",
        "emergency",
        "sabotage",
        "repair_sabotage",
        "wait",
    ]


def test_action_intent_union_rejects_unknown_or_malformed_intents() -> None:
    invalid_payloads = [
        {"type": "repair_sabotage", "actor": "player-1", "payload": {}},
        {"type": "move", "actor": "player-1", "payload": {"room": "ADMIN"}},
        {
            "type": "do_task",
            "actor": "player-1",
            "payload": {"task_id": "swipe_card", "unexpected": True},
        },
        {"type": "kill", "actor": "player-1", "payload": {"target": "player-1"}},
    ]

    for payload in invalid_payloads:
        with pytest.raises(ValidationError):
            _ACTION_INTENT_ADAPTER.validate_python(payload)


def test_public_map_view_schema_is_engine_free_and_forbids_extra_fields() -> None:
    view = PublicMapView(
        map_id="canonical_1",
        room_ids=("ADMIN", "CAFETERIA"),
        room_neighbors={"ADMIN": ("CAFETERIA",), "CAFETERIA": ("ADMIN",)},
        vent_graph={"ADMIN_VENT": ()},
        vent_rooms={"ADMIN_VENT": "ADMIN"},
        task_locations={"swipe_card": "ADMIN"},
        spawn_room="CAFETERIA",
        meeting_room="CAFETERIA",
        emergency_button_room="CAFETERIA",
    )

    assert view.emergency_button_room == "CAFETERIA"
    with pytest.raises(ValidationError):
        PublicMapView.model_validate(
            {
                **view.model_dump(mode="python"),
                "unexpected": True,
            }
        )
