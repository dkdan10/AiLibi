from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from engine.actions import Action

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def test_action_union_accepts_known_action_types() -> None:
    payloads = [
        {"type": "move", "actor": "p-1", "payload": {"to_room": "ADMIN"}},
        {"type": "do_task", "actor": "p-1", "payload": {"task_id": "swipe_card"}},
        {"type": "kill", "actor": "impostor", "payload": {"target": "p-1"}},
        {"type": "vent", "actor": "impostor", "payload": {"vent_id": "ADMIN_VENT"}},
        {"type": "report", "actor": "p-1", "payload": {"body_id": "body-1"}},
        {"type": "emergency", "actor": "p-1", "payload": {"reason": "test"}},
        {"type": "sabotage", "actor": "impostor", "payload": {"kind": "lights"}},
        {
            "type": "repair_sabotage",
            "actor": "p-1",
            "payload": {"kind": "lights"},
        },
        {"type": "wait", "actor": "p-1", "payload": {}},
    ]

    actions = [_ACTION_ADAPTER.validate_python(payload) for payload in payloads]

    assert [action.type for action in actions] == [
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


def test_action_union_rejects_unknown_action_type() -> None:
    with pytest.raises(ValidationError):
        _ACTION_ADAPTER.validate_python(
            {"type": "dance", "actor": "p-1", "payload": {}}
        )


def test_action_union_rejects_invalid_payload_shape() -> None:
    with pytest.raises(ValidationError):
        _ACTION_ADAPTER.validate_python(
            {"type": "move", "actor": "p-1", "payload": {"room": "ADMIN"}}
        )


def test_action_union_rejects_extra_payload_fields() -> None:
    with pytest.raises(ValidationError):
        _ACTION_ADAPTER.validate_python(
            {
                "type": "do_task",
                "actor": "p-1",
                "payload": {"task_id": "swipe_card", "unexpected": True},
            }
        )


def test_kill_action_rejects_self_target() -> None:
    with pytest.raises(ValidationError):
        _ACTION_ADAPTER.validate_python(
            {"type": "kill", "actor": "p-1", "payload": {"target": "p-1"}}
        )
