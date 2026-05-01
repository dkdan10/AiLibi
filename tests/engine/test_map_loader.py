from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.world import MapValidationError, load_canonical_map  # noqa: E402


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
