from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from observation.action_intent import ActionIntent
from observation.packet import BodyView
from observation.public_map import PublicMapView

_ACTION_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)


def test_action_intent_union_accepts_supported_intent_types() -> None:
    payloads = [
        {"type": "move", "actor": "p-1", "payload": {"to_room": "ADMIN"}},
        {"type": "do_task", "actor": "p-1", "payload": {"task_id": "swipe_card"}},
        {"type": "kill", "actor": "impostor", "payload": {"target": "p-1"}},
        {"type": "vent", "actor": "impostor", "payload": {"vent_id": "ADMIN_VENT"}},
        {"type": "report", "actor": "p-1", "payload": {"body_id": "body-1"}},
        {"type": "emergency", "actor": "p-1", "payload": {"reason": "test"}},
        {"type": "sabotage", "actor": "impostor", "payload": {"kind": "lights"}},
        {"type": "repair_sabotage", "actor": "p-1", "payload": {"kind": "lights"}},
        {"type": "wait", "actor": "p-1", "payload": {}},
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
        {"type": "repair_sabotage", "actor": "p-1", "payload": {}},
        {"type": "move", "actor": "p-1", "payload": {"room": "ADMIN"}},
        {
            "type": "do_task",
            "actor": "p-1",
            "payload": {"task_id": "swipe_card", "unexpected": True},
        },
        {"type": "kill", "actor": "p-1", "payload": {"target": "p-1"}},
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


def test_body_view_requires_non_empty_victim_id() -> None:
    # R-4: ``victim_id`` is part of the typed boundary contract between
    # ObservationService and agent code. A body without ``victim_id``
    # (or with an empty string) must fail Pydantic validation rather
    # than silently surfacing a missing field downstream.
    with pytest.raises(ValidationError):
        BodyView.model_validate({"id": "body-p-1-0", "room": "REACTOR"})
    with pytest.raises(ValidationError):
        BodyView.model_validate(
            {"id": "body-p-1-0", "room": "REACTOR", "victim_id": ""}
        )


def test_body_view_round_trip_preserves_victim_id() -> None:
    # The boundary contract for ``BodyView`` includes ``id``, ``room``,
    # and ``victim_id`` — and only those keys (``extra="forbid"``).
    # ``victim_id`` must equal what the engine-side ``BodyState.player_id``
    # populated when ObservationService built the view.
    body = BodyView(id="body-p-3-7", room="REACTOR", victim_id="p-3")

    dumped = body.model_dump(mode="json")

    assert dumped == {"id": "body-p-3-7", "room": "REACTOR", "victim_id": "p-3"}
    assert BodyView.model_validate(dumped) == body
    with pytest.raises(ValidationError):
        BodyView.model_validate(
            {
                "id": "body-p-3-7",
                "room": "REACTOR",
                "victim_id": "p-3",
                "killed_by": "p-4",
            }
        )
