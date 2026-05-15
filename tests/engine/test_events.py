from __future__ import annotations

from engine.events import MovedEvent, event_to_dict


def test_typed_engine_event_serializes_to_legacy_shape() -> None:
    event = MovedEvent(
        type="Moved",
        tick=3,
        actor="p-1",
        from_room="CAFETERIA",
        to_room="ADMIN",
    )

    serialized = event_to_dict(event)
    assert serialized == {
        "type": "Moved",
        "tick": 3,
        "actor": "p-1",
        "details": {"from_room": "CAFETERIA", "to_room": "ADMIN"},
    }
    assert serialized["details"] == {"from_room": "CAFETERIA", "to_room": "ADMIN"}
