from __future__ import annotations

from collections.abc import Mapping

import pytest

from agents.tactical.pathing import find_path
from observation.public_map import PublicMapView, RoomId


def _build_map(
    *,
    rooms: tuple[RoomId, ...],
    neighbors: Mapping[RoomId, tuple[RoomId, ...]],
) -> PublicMapView:
    return PublicMapView(
        map_id="test_map",
        room_ids=rooms,
        room_neighbors=neighbors,
        vent_graph={},
        vent_rooms={},
        task_locations={},
        spawn_room=rooms[0],
        meeting_room=rooms[0],
        emergency_button_room=rooms[0],
    )


def test_find_path_returns_single_room_when_start_equals_goal() -> None:
    public_map = _build_map(
        rooms=("ADMIN", "CAFETERIA"),
        neighbors={"ADMIN": ("CAFETERIA",), "CAFETERIA": ("ADMIN",)},
    )

    assert find_path(public_map=public_map, start="ADMIN", goal="ADMIN") == ("ADMIN",)


def test_find_path_returns_inclusive_two_room_path_for_direct_neighbor() -> None:
    public_map = _build_map(
        rooms=("ADMIN", "CAFETERIA"),
        neighbors={"ADMIN": ("CAFETERIA",), "CAFETERIA": ("ADMIN",)},
    )

    assert find_path(public_map=public_map, start="ADMIN", goal="CAFETERIA") == (
        "ADMIN",
        "CAFETERIA",
    )


def test_find_path_walks_chain_through_multiple_rooms() -> None:
    public_map = _build_map(
        rooms=("A", "B", "C", "D"),
        neighbors={
            "A": ("B",),
            "B": ("A", "C"),
            "C": ("B", "D"),
            "D": ("C",),
        },
    )

    assert find_path(public_map=public_map, start="A", goal="D") == ("A", "B", "C", "D")


def test_find_path_prefers_shorter_path_over_longer_alphabetical_route() -> None:
    # Direct A-D is one hop; A-B-C-D is three hops. The shorter path wins
    # even though sorted-id tie-breaking would otherwise prefer "B" first.
    public_map = _build_map(
        rooms=("A", "B", "C", "D"),
        neighbors={
            "A": ("B", "D"),
            "B": ("A", "C"),
            "C": ("B", "D"),
            "D": ("A", "C"),
        },
    )

    assert find_path(public_map=public_map, start="A", goal="D") == ("A", "D")


def test_find_path_breaks_ties_on_sorted_room_id() -> None:
    # Diamond graph: A->B->D and A->C->D are both length 3. With sorted-id
    # tie-breaking the path through "B" must win over the path through "C".
    public_map = _build_map(
        rooms=("A", "B", "C", "D"),
        neighbors={
            "A": ("B", "C"),
            "B": ("A", "D"),
            "C": ("A", "D"),
            "D": ("B", "C"),
        },
    )

    assert find_path(public_map=public_map, start="A", goal="D") == ("A", "B", "D")


def test_find_path_tie_break_is_independent_of_neighbor_listing_order() -> None:
    # Same diamond as above but neighbors listed in reverse order. The
    # function must still return the alphabetically-first tied path.
    public_map = _build_map(
        rooms=("A", "B", "C", "D"),
        neighbors={
            "A": ("C", "B"),
            "B": ("D", "A"),
            "C": ("D", "A"),
            "D": ("C", "B"),
        },
    )

    assert find_path(public_map=public_map, start="A", goal="D") == ("A", "B", "D")


def test_find_path_is_deterministic_across_repeated_calls() -> None:
    public_map = _build_map(
        rooms=("A", "B", "C", "D", "E"),
        neighbors={
            "A": ("B", "C"),
            "B": ("A", "D"),
            "C": ("A", "D"),
            "D": ("B", "C", "E"),
            "E": ("D",),
        },
    )

    paths = [find_path(public_map=public_map, start="A", goal="E") for _ in range(5)]

    assert all(path == paths[0] for path in paths)
    assert paths[0] == ("A", "B", "D", "E")


def test_find_path_raises_when_start_room_is_unknown() -> None:
    public_map = _build_map(
        rooms=("ADMIN", "CAFETERIA"),
        neighbors={"ADMIN": ("CAFETERIA",), "CAFETERIA": ("ADMIN",)},
    )

    with pytest.raises(ValueError, match="unknown start room"):
        find_path(public_map=public_map, start="STORAGE", goal="ADMIN")


def test_find_path_raises_when_goal_room_is_unknown() -> None:
    public_map = _build_map(
        rooms=("ADMIN", "CAFETERIA"),
        neighbors={"ADMIN": ("CAFETERIA",), "CAFETERIA": ("ADMIN",)},
    )

    with pytest.raises(ValueError, match="unknown goal room"):
        find_path(public_map=public_map, start="ADMIN", goal="STORAGE")


def test_find_path_raises_when_goal_is_disconnected_from_start() -> None:
    # Two disconnected components: {A, B} and {C, D}.
    public_map = _build_map(
        rooms=("A", "B", "C", "D"),
        neighbors={
            "A": ("B",),
            "B": ("A",),
            "C": ("D",),
            "D": ("C",),
        },
    )

    with pytest.raises(ValueError, match="no path"):
        find_path(public_map=public_map, start="A", goal="C")


def test_find_path_raises_when_start_has_no_neighbors_and_is_not_goal() -> None:
    public_map = _build_map(
        rooms=("ISLAND", "MAINLAND"),
        neighbors={"ISLAND": (), "MAINLAND": ()},
    )

    with pytest.raises(ValueError, match="no path"):
        find_path(public_map=public_map, start="ISLAND", goal="MAINLAND")


def test_find_path_handles_self_loop_in_graph_without_revisiting() -> None:
    # A self-loop on the start room must not produce a path that revisits it.
    public_map = _build_map(
        rooms=("A", "B"),
        neighbors={"A": ("A", "B"), "B": ("A",)},
    )

    assert find_path(public_map=public_map, start="A", goal="B") == ("A", "B")
