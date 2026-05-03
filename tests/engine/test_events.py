from __future__ import annotations

from engine.events import MovedEvent, event_to_dict


def test_typed_engine_event_serializes_to_legacy_shape() -> None:
    event = MovedEvent(
        type="Moved",
        tick=3,
        actor="player-1",
        from_room="CAFETERIA",
        to_room="ADMIN",
    )

    assert event_to_dict(event) == {
        "type": "Moved",
        "tick": 3,
        "actor": "player-1",
        "details": {"from_room": "CAFETERIA", "to_room": "ADMIN"},
    }
    assert event["details"] == {"from_room": "CAFETERIA", "to_room": "ADMIN"}
