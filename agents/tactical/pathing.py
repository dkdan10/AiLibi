"""Deterministic A* pathing over :class:`PublicMapView` (DESIGN.md §4.4).

Tactical policies (Tasks 2.6 / 2.7) call :func:`find_path` to plan room-to-room
moves. The map graph carries no spatial information so the admissible
heuristic is zero — A* therefore reduces to uniform-cost search over the
adjacency graph. Determinism is guaranteed by:

* iterating neighbors in sorted ``RoomId`` order,
* breaking heap ties on sorted ``RoomId``,
* updating ``came_from`` only on a strictly better cost so the first
  optimal path discovered is the one returned.

The function raises :class:`ValueError` for unknown endpoints and for
destinations unreachable from the start.
"""

from __future__ import annotations

import heapq

from observation.public_map import PublicMapView, RoomId


def find_path(
    *,
    public_map: PublicMapView,
    start: RoomId,
    goal: RoomId,
) -> tuple[RoomId, ...]:
    """Return the inclusive shortest path from ``start`` to ``goal``.

    Determinism: ties between equal-cost expansions are broken by sorted
    ``RoomId``. Calling this function with the same inputs always returns
    the same tuple.

    Raises:
        ValueError: if ``start`` or ``goal`` is not a known room, or if
            ``goal`` is unreachable from ``start``.
    """

    known_rooms = set(public_map.room_ids)
    if start not in known_rooms:
        raise ValueError(f"unknown start room: {start!r}")
    if goal not in known_rooms:
        raise ValueError(f"unknown goal room: {goal!r}")

    if start == goal:
        return (start,)

    came_from: dict[RoomId, RoomId] = {}
    g_score: dict[RoomId, int] = {start: 0}
    closed: set[RoomId] = set()
    open_heap: list[tuple[int, RoomId]] = [(0, start)]

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        if current == goal:
            return _reconstruct_path(came_from=came_from, start=start, goal=goal)
        closed.add(current)

        for neighbor in sorted(public_map.room_neighbors.get(current, ())):
            if neighbor in closed:
                continue
            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                heapq.heappush(open_heap, (tentative_g, neighbor))

    raise ValueError(f"no path from {start!r} to {goal!r}")


def _reconstruct_path(
    *,
    came_from: dict[RoomId, RoomId],
    start: RoomId,
    goal: RoomId,
) -> tuple[RoomId, ...]:
    path: list[RoomId] = [goal]
    while path[-1] != start:
        path.append(came_from[path[-1]])
    path.reverse()
    return tuple(path)


__all__ = ["find_path"]
