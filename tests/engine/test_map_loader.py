from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.world import Map, MapValidationError, load_canonical_map  # noqa: E402


def _minimal_map_data() -> dict[str, object]:
    return {
        "map_id": "test_map",
        "name": "Test Map",
        "version": "0.1",
        "tick_rate_hz": 2,
        "visibility_defaults": {
            "base": "same_room_and_adjacent",
            "lights_sabotage": "same_room_only",
        },
        "rooms": {
            "CAFETERIA": {
                "name": "Cafeteria",
                "kind": "meeting_room",
                "position": {"x": 0, "y": 0},
                "size": {"width": 1, "height": 1},
            }
        },
        "edges": [],
        "vents": {
            "CAFETERIA_VENT": {
                "room": "CAFETERIA",
                "connects_to": [],
                "traversal_ticks": 1,
            }
        },
        "tasks": {
            "empty_trash": {
                "name": "Empty Trash",
                "room": "CAFETERIA",
                "duration_ticks": 1,
                "task_type": "common",
                "weight": 1,
            }
        },
        "sabotages": {
            "lights": {
                "affected_visibility": "same_room_only",
                "repair_rooms": ["CAFETERIA"],
                "duration_ticks": 1,
            }
        },
        "emergency": {"button_room": "CAFETERIA", "uses_per_player": 1},
        "spawn": {"room": "CAFETERIA"},
        "meeting": {"room": "CAFETERIA"},
    }


def test_load_canonical_map_counts() -> None:
    game_map = load_canonical_map()

    assert game_map.id == "canonical_1"
    assert game_map.tick_rate_hz == 2
    assert len(game_map.rooms) == 10
    assert len(game_map.edges) == 11
    assert len(game_map.vents) == 6
    assert len(game_map.tasks) == 12
    assert len(game_map.sabotages) == 1


def test_map_graph_helpers_return_sorted_neighbors() -> None:
    game_map = load_canonical_map()

    assert game_map.room_neighbors("CAFETERIA") == (
        "EAST_HALL",
        "UPPER_HALL",
        "WEST_HALL",
    )
    assert game_map.room_neighbors("ADMIN") == (
        "EAST_HALL",
        "UPPER_HALL",
        "WEST_HALL",
    )
    assert game_map.vent_neighbors("REACTOR_VENT") == (
        "ADMIN_VENT",
        "STORAGE_VENT",
    )
    assert game_map.vent_for_room("REACTOR").id == "REACTOR_VENT"
    assert game_map.vent_for_room("CAFETERIA") is None


def test_map_graph_helpers_reject_unknown_ids() -> None:
    game_map = load_canonical_map()

    with pytest.raises(MapValidationError):
        game_map.room_neighbors("UNKNOWN_ROOM")
    with pytest.raises(MapValidationError):
        game_map.vent_neighbors("UNKNOWN_VENT")
    with pytest.raises(MapValidationError):
        game_map.vent_for_room("UNKNOWN_ROOM")


def test_loaded_map_collections_reject_in_place_mutation() -> None:
    game_map = load_canonical_map()
    room = game_map.rooms["CAFETERIA"]
    vent = game_map.vents["ADMIN_VENT"]
    task = game_map.tasks["swipe_card"]
    sabotage = game_map.sabotages["lights"]

    with pytest.raises(TypeError):
        game_map.rooms["ZZ_TEST"] = room  # type: ignore[index]
    with pytest.raises(TypeError):
        game_map.vents["ZZ_TEST_VENT"] = vent  # type: ignore[index]
    with pytest.raises(TypeError):
        game_map.tasks["zz_test_task"] = task  # type: ignore[index]
    with pytest.raises(TypeError):
        game_map.sabotages["zz_test"] = sabotage  # type: ignore[index]


def test_map_model_defensively_copies_collection_inputs() -> None:
    rooms = {
        "CAFETERIA": {
            "name": "Cafeteria",
            "kind": "meeting_room",
            "position": {"x": 0, "y": 0},
            "size": {"width": 1, "height": 1},
        }
    }
    vents: dict[str, object] = {}
    tasks: dict[str, object] = {}
    sabotages = {
        "lights": {
            "affected_visibility": "same_room_only",
            "repair_rooms": ["CAFETERIA"],
            "duration_ticks": 1,
        }
    }
    game_map = Map.model_validate(
        {
            "map_id": "test_map",
            "name": "Test Map",
            "version": "0.1",
            "tick_rate_hz": 2,
            "visibility_defaults": {
                "base": "same_room_and_adjacent",
                "lights_sabotage": "same_room_only",
            },
            "rooms": rooms,
            "edges": [],
            "vents": vents,
            "tasks": tasks,
            "sabotages": sabotages,
            "emergency": {"button_room": "CAFETERIA", "uses_per_player": 1},
            "spawn": {"room": "CAFETERIA"},
            "meeting": {"room": "CAFETERIA"},
        }
    )

    rooms["ZZ_TEST"] = {
        "name": "Test",
        "kind": "room",
        "position": {"x": 1, "y": 1},
        "size": {"width": 1, "height": 1},
    }
    vents["ZZ_TEST_VENT"] = {
        "room": "CAFETERIA",
        "connects_to": [],
        "traversal_ticks": 1,
    }
    tasks["zz_test_task"] = {
        "name": "Test",
        "room": "CAFETERIA",
        "duration_ticks": 1,
        "task_type": "short",
        "weight": 1,
    }
    sabotages["zz_test"] = {
        "affected_visibility": "same_room_only",
        "repair_rooms": ["CAFETERIA"],
        "duration_ticks": 1,
    }

    assert tuple(game_map.rooms) == ("CAFETERIA",)
    assert tuple(game_map.vents) == ()
    assert tuple(game_map.tasks) == ()
    assert tuple(game_map.sabotages) == ("lights",)


def test_map_model_rejects_unexpected_top_level_fields() -> None:
    data = _minimal_map_data()
    data["unexpected"] = True

    with pytest.raises(ValidationError):
        Map.model_validate(data)


def test_map_model_rejects_unexpected_nested_fields() -> None:
    data = _minimal_map_data()
    rooms = data["rooms"]
    assert isinstance(rooms, dict)
    room = rooms["CAFETERIA"]
    assert isinstance(room, dict)
    room["unexpected"] = True

    with pytest.raises(ValidationError):
        Map.model_validate(data)


@pytest.mark.parametrize("field_name", ("rooms", "vents", "tasks"))
def test_map_model_rejects_non_mapping_collections(field_name: str) -> None:
    data = _minimal_map_data()
    data[field_name] = []

    with pytest.raises(ValidationError, match=f"{field_name} must be a mapping"):
        Map.model_validate(data)


@pytest.mark.parametrize(
    ("field_name", "item_id"),
    (
        ("rooms", "CAFETERIA"),
        ("vents", "CAFETERIA_VENT"),
        ("tasks", "empty_trash"),
    ),
)
def test_map_model_rejects_non_mapping_collection_entries(
    field_name: str,
    item_id: str,
) -> None:
    data = _minimal_map_data()
    collection = data[field_name]
    assert isinstance(collection, dict)
    collection[item_id] = "not a mapping"

    with pytest.raises(ValidationError, match=f"{field_name}.{item_id}"):
        Map.model_validate(data)


@pytest.mark.parametrize(
    ("field_name", "item_id", "wrong_id"),
    (
        ("rooms", "CAFETERIA", "ADMIN"),
        ("vents", "CAFETERIA_VENT", "ADMIN_VENT"),
        ("tasks", "empty_trash", "swipe_card"),
    ),
)
def test_map_model_rejects_mismatched_embedded_ids(
    field_name: str,
    item_id: str,
    wrong_id: str,
) -> None:
    data = _minimal_map_data()
    collection = data[field_name]
    assert isinstance(collection, dict)
    item = collection[item_id]
    assert isinstance(item, dict)
    item["id"] = wrong_id

    with pytest.raises(ValidationError, match="embedded id must match mapping key"):
        Map.model_validate(data)
