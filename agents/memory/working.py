"""Working memory (DESIGN.md §6.1).

Volatile, per-tick scratch state: the agent's current goal, current path,
and last_seen lookup. Working memory is rebuilt each tick from episodic
events plus belief state — it does not persist across runs.

This module ships the write paths that perception (Task 2.4) and tactical
policies (Tasks 2.6 / 2.7) need to set and overwrite scratch state. Higher
level rendering of working memory belongs to Task 3.3.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

PlayerId: TypeAlias = str
RoomId: TypeAlias = str


@dataclass(frozen=True)
class Goal:
    """Current tactical objective.

    ``kind`` is a short string discriminator (e.g. ``"do_task"``,
    ``"move_to_room"``, ``"report_body"``). ``target`` is the optional
    object of the goal — a task id, a room id, or a body id depending on
    ``kind``. The string-typed shape is intentional so this scaffold does
    not pin a richer goal protocol that later tasks may need to evolve.
    """

    kind: str
    target: str | None = None


@dataclass(frozen=True)
class LastSeen:
    """Most recent first-hand sighting of another player."""

    tick: int
    room: RoomId


class WorkingMemory:
    """Per-agent volatile scratch state.

    Reads return either ``None`` (when the value has never been set) or
    the most recent value written. The store does not silently coerce
    invalid input — empty paths must be set with ``clear_path`` and
    ``record_sighting`` rejects negative ticks.
    """

    def __init__(self) -> None:
        self._goal: Goal | None = None
        self._path: tuple[RoomId, ...] = ()
        self._last_seen: dict[PlayerId, LastSeen] = {}

    @property
    def goal(self) -> Goal | None:
        return self._goal

    @property
    def path(self) -> tuple[RoomId, ...]:
        return self._path

    def set_goal(self, goal: Goal) -> None:
        self._goal = goal

    def clear_goal(self) -> None:
        self._goal = None

    def set_path(self, path: tuple[RoomId, ...]) -> None:
        if not path:
            raise ValueError("set_path requires a non-empty path; use clear_path()")
        self._path = path

    def clear_path(self) -> None:
        self._path = ()

    def record_sighting(
        self,
        *,
        player_id: PlayerId,
        room: RoomId,
        tick: int,
    ) -> None:
        if tick < 0:
            raise ValueError(f"sighting tick must be non-negative, got {tick}")
        previous = self._last_seen.get(player_id)
        if previous is not None and tick < previous.tick:
            raise ValueError(
                "sightings must be recorded in non-decreasing tick order: "
                f"got tick {tick} after tick {previous.tick} for {player_id!r}"
            )
        self._last_seen[player_id] = LastSeen(tick=tick, room=room)

    def last_seen(self, player_id: PlayerId) -> LastSeen | None:
        return self._last_seen.get(player_id)
