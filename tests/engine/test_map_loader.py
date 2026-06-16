from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.world import Map, MapValidationError, load_canonical_map, load_map

MapData = dict[str, object]
MapMutator = Callable[[MapData], None]


def _minimal_map_data() -> MapData:
    return {
        "map_id": "test_map",
        "name": "Test Map",
        "version": "0.1",
        "tick_rate_hz": 2,
        "kill_cooldown_ticks": 10,
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


def _mapping(data: MapData, key: str) -> dict[str, object]:
    value = data[key]
    assert isinstance(value, dict)
    return value


def _sequence(data: MapData, key: str) -> list[object]:
    value = data[key]
    assert isinstance(value, list)
    return value


def _entry(data: MapData, collection_key: str, item_key: str) -> dict[str, object]:
    value = _mapping(data, collection_key)[item_key]
    assert isinstance(value, dict)
    return value


def _admin_room() -> dict[str, object]:
    return {
        "name": "Admin",
        "kind": "task_room",
        "position": {"x": 2, "y": 0},
        "size": {"width": 1, "height": 1},
    }


def _add_admin_room(data: MapData) -> None:
    _mapping(data, "rooms")["ADMIN"] = _admin_room()


def _connect_cafeteria_to_admin(data: MapData) -> None:
    _sequence(data, "edges").append(
        {
            "from": "CAFETERIA",
            "to": "ADMIN",
            "kind": "doorway",
            "traversal_ticks": 1,
            "door_id": None,
        }
    )


def _unknown_edge_room(data: MapData) -> None:
    _sequence(data, "edges").append(
        {
            "from": "CAFETERIA",
            "to": "UNKNOWN_ROOM",
            "kind": "doorway",
            "traversal_ticks": 1,
            "door_id": None,
        }
    )


def _disconnected_room(data: MapData) -> None:
    _add_admin_room(data)


def _unknown_vent_reference(data: MapData) -> None:
    _entry(data, "vents", "CAFETERIA_VENT")["connects_to"] = ["UNKNOWN_VENT"]


def _asymmetric_vent_reference(data: MapData) -> None:
    _add_admin_room(data)
    _connect_cafeteria_to_admin(data)
    _mapping(data, "vents")["ADMIN_VENT"] = {
        "room": "ADMIN",
        "connects_to": [],
        "traversal_ticks": 1,
    }
    _entry(data, "vents", "CAFETERIA_VENT")["connects_to"] = ["ADMIN_VENT"]


def _task_in_hallway(data: MapData) -> None:
    _entry(data, "rooms", "CAFETERIA")["kind"] = "hallway"


def _task_unknown_room(data: MapData) -> None:
    _entry(data, "tasks", "empty_trash")["room"] = "UNKNOWN_ROOM"


def _unknown_sabotage_repair_room(data: MapData) -> None:
    _entry(data, "sabotages", "lights")["repair_rooms"] = ["UNKNOWN_ROOM"]


def _unknown_special_room(data: MapData) -> None:
    _mapping(data, "spawn")["room"] = "UNKNOWN_ROOM"


def _invalid_room_id(data: MapData) -> None:
    rooms = _mapping(data, "rooms")
    rooms["bad_room"] = rooms.pop("CAFETERIA")


def _negative_room_position(data: MapData) -> None:
    _entry(data, "rooms", "CAFETERIA")["position"] = {"x": -1, "y": 0}


def _non_positive_room_size(data: MapData) -> None:
    _entry(data, "rooms", "CAFETERIA")["size"] = {"width": 0, "height": 1}


def _non_positive_tick_rate(data: MapData) -> None:
    data["tick_rate_hz"] = 0


def _non_positive_kill_cooldown(data: MapData) -> None:
    data["kill_cooldown_ticks"] = 0


def _non_positive_edge_traversal(data: MapData) -> None:
    _add_admin_room(data)
    _sequence(data, "edges").append(
        {
            "from": "CAFETERIA",
            "to": "ADMIN",
            "kind": "doorway",
            "traversal_ticks": 0,
            "door_id": None,
        }
    )


def _non_positive_vent_traversal(data: MapData) -> None:
    _entry(data, "vents", "CAFETERIA_VENT")["traversal_ticks"] = 0


def _non_positive_task_duration(data: MapData) -> None:
    _entry(data, "tasks", "empty_trash")["duration_ticks"] = 0


def _non_positive_sabotage_repair_ticks(data: MapData) -> None:
    _entry(data, "sabotages", "lights")["repair_ticks"] = 0


def test_load_canonical_map_counts() -> None:
    game_map = load_canonical_map()

    assert game_map.id == "canonical_1"
    assert game_map.tick_rate_hz == 2
    assert game_map.kill_cooldown_ticks == 4
    assert len(game_map.rooms) == 10
    assert len(game_map.edges) == 11
    assert len(game_map.vents) == 6
    assert len(game_map.tasks) == 12
    assert len(game_map.sabotages) == 2
    assert game_map.sabotages["lights"].repair_ticks == 3


def test_reactor_sabotage_loads_with_gating_flag() -> None:
    # Task 11.5 (DESIGN.md §8.3): the task-gating ``reactor`` kind loads from data
    # with ``gates_tasks`` true, two repair rooms, and base (non-degrading)
    # visibility -- it contests the task clock, not sightlines.
    game_map = load_canonical_map()

    reactor = game_map.sabotages["reactor"]
    assert reactor.gates_tasks is True
    assert reactor.affected_visibility == "same_room_and_adjacent"
    assert reactor.repair_rooms == ("REACTOR", "ENGINEERING")
    # Geometry-anchored timer: CAFETERIA->REACTOR hop count (3) + repair_ticks (3)
    # + 1 for the start-tick decrement (the sabotage is decremented on its start
    # tick, so the full reach-a-panel-and-hold-it window needs the extra tick).
    assert reactor.duration_ticks == 7
    assert reactor.repair_ticks == 3


def test_gates_tasks_defaults_false_for_lights() -> None:
    # The ``gates_tasks`` field is optional and defaults False, so ``lights``
    # (and every existing map-loader pin) stays byte-stable (Task 11.5).
    game_map = load_canonical_map()

    assert game_map.sabotages["lights"].gates_tasks is False


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
    reactor_vent = game_map.vent_for_room("REACTOR")
    assert reactor_vent is not None
    assert reactor_vent.id == "REACTOR_VENT"
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
            "kill_cooldown_ticks": 10,
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


@pytest.mark.parametrize(
    ("mutate", "match"),
    (
        (_unknown_edge_room, "edge references unknown room"),
        (_disconnected_room, "room graph is not fully connected"),
        (_unknown_vent_reference, "references unknown vent"),
        (_asymmetric_vent_reference, "vent link must be symmetric"),
        (_task_in_hallway, "task assigned to hallway"),
        (_task_unknown_room, "task references unknown room"),
        (_unknown_sabotage_repair_room, "references unknown room"),
        (_unknown_special_room, "spawn.room references unknown room"),
        (_invalid_room_id, "invalid room id"),
        (_negative_room_position, "room positions must be non-negative"),
        (_non_positive_room_size, "room sizes must be positive"),
        (_non_positive_tick_rate, "tick_rate_hz must be positive"),
        (_non_positive_kill_cooldown, "kill_cooldown_ticks must be at least 1"),
        (_non_positive_edge_traversal, "edge traversal_ticks must be at least 1"),
        (_non_positive_vent_traversal, "vent traversal_ticks must be at least 1"),
        (_non_positive_task_duration, "task duration_ticks must be at least 1"),
        (
            _non_positive_sabotage_repair_ticks,
            "sabotage repair_ticks must be at least 1",
        ),
    ),
)
def test_map_model_rejects_documented_validation_errors(
    mutate: MapMutator,
    match: str,
) -> None:
    data = _minimal_map_data()
    mutate(data)

    with pytest.raises(ValidationError, match=match):
        Map.model_validate(data)


_MINIMAL_YAML_BODY = """\
map_id: yaml_features
name: YAML Features
version: "0.1"
tick_rate_hz: 2
kill_cooldown_ticks: 10
visibility_defaults:
  base: same_room_and_adjacent
  lights_sabotage: same_room_only
edges: []
vents:
  CAFETERIA_VENT:
    room: CAFETERIA
    connects_to: []
    traversal_ticks: 1
tasks:
  empty_trash:
    name: Empty Trash
    room: CAFETERIA
    duration_ticks: 1
    task_type: common
    weight: 1
sabotages:
  lights:
    affected_visibility: same_room_only
    repair_rooms:
      - CAFETERIA
    duration_ticks: 1
emergency: { button_room: CAFETERIA, uses_per_player: 1 }
spawn: { room: CAFETERIA }
meeting: { room: CAFETERIA }
"""


def _write_minimal_yaml(tmp_path: Path, rooms_block: str) -> Path:
    map_path = tmp_path / "map.yaml"
    map_path.write_text(rooms_block + _MINIMAL_YAML_BODY, encoding="utf-8")
    return map_path


def test_load_map_accepts_colon_in_room_notes(tmp_path: Path) -> None:
    """PyYAML must round-trip a notes string that contains a colon."""

    rooms_block = (
        "rooms:\n"
        "  CAFETERIA:\n"
        "    name: Cafeteria\n"
        "    kind: meeting_room\n"
        "    position: { x: 0, y: 0 }\n"
        "    size: { width: 1, height: 1 }\n"
        '    notes: "Hub: central room with multiple exits"\n'
    )

    game_map = load_map(_write_minimal_yaml(tmp_path, rooms_block))

    assert game_map.rooms["CAFETERIA"].notes == (
        "Hub: central room with multiple exits"
    )


def test_load_map_accepts_folded_block_scalar_notes(tmp_path: Path) -> None:
    """PyYAML must accept a folded `>` block-scalar note."""

    rooms_block = (
        "rooms:\n"
        "  CAFETERIA:\n"
        "    name: Cafeteria\n"
        "    kind: meeting_room\n"
        "    position: { x: 0, y: 0 }\n"
        "    size: { width: 1, height: 1 }\n"
        "    notes: >\n"
        "      First line of folded notes\n"
        "      that wraps onto a second line.\n"
    )

    game_map = load_map(_write_minimal_yaml(tmp_path, rooms_block))

    notes = game_map.rooms["CAFETERIA"].notes
    assert "First line of folded notes" in notes
    assert "second line" in notes


def test_load_map_rejects_non_integer_tick_rate(tmp_path: Path) -> None:
    """A YAML float for tick_rate_hz must raise; the schema requires int."""

    map_path = tmp_path / "map.yaml"
    map_path.write_text(
        _MINIMAL_YAML_BODY.replace(
            "tick_rate_hz: 2",
            "tick_rate_hz: 2.5",
        ).replace(
            "edges:",
            "rooms:\n"
            "  CAFETERIA:\n"
            "    name: Cafeteria\n"
            "    kind: meeting_room\n"
            "    position: { x: 0, y: 0 }\n"
            "    size: { width: 1, height: 1 }\n"
            "edges:",
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_map(map_path)


def test_load_map_rejects_non_mapping_top_level(tmp_path: Path) -> None:
    """A YAML document whose root is not a mapping must fail with a clear error."""

    map_path = tmp_path / "list.yaml"
    map_path.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(MapValidationError, match="top-level mapping"):
        load_map(map_path)
