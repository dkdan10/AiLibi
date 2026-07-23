"""Working memory (DESIGN.md §6.1).

Volatile, per-tick scratch state: the agent's current goal, current path,
and last_seen lookup. Working memory is rebuilt each tick from episodic
events plus belief state — it does not persist across runs.

This module ships the write paths that perception (Task 2.4) and tactical
policies (Tasks 2.6 / 2.7) need to set and overwrite scratch state. Higher
level rendering of working memory belongs to Task 3.3.

CURRENT STATUS — ``last_seen`` is WIRED by Task 13.5.4 (movement perception);
``set_goal`` / ``set_path`` remain without a production writer (2026-06-25
memory-pipeline diagnosis, workflow `wg54kfoxy`). ``record_sighting`` is called
by ``agents/memory/store.py`` (``_record_movement_sightings``, at render time)
for every witnessed room→room transition, so ``_last_seen`` fills and the §6.6
belief-line suffix renders -- unconditionally since Task 14.9 (the adopted
13.5.4 lever is the default substrate).
The writer is idempotent (skips a row not after the recorded
last-seen) so the repeated renders a meeting drives never trip
``record_sighting``'s non-decreasing-tick guard, and §4.7-firewall-suppressed.
``set_goal`` / ``set_path`` are still scaffolding (zero non-test callers), NOT
dead code to delete.
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


@dataclass(frozen=True)
class MeetingOutcome:
    """One concluded meeting's PUBLIC result (Task 18.22).

    Both fields are facts every player at the table observed: ``end_tick`` is
    the tick gameplay resumed at, and ``ejected_id`` is the player the vote
    tally removed -- ``None`` when the meeting skipped or tied. The channel is
    fed only from the ``note_meeting_concluded`` hook payload (the resume tick
    plus the announced ejection outcome), so no engine-private state crosses
    into agent memory and the row is firewall-clean by construction (DESIGN.md
    §4.7, the same public footing as a meeting's ``dead_ids``). Consumed only
    by the v3 tactical feature encoder's meeting-history channel; inert to
    prompt rendering.
    """

    end_tick: int
    ejected_id: PlayerId | None


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


class MeetingHistory:
    """Append-only log of concluded-meeting outcomes (Task 18.22).

    The per-agent meeting-history channel the v3 tactical feature encoder
    reads. It owns its own list -- no singleton, no module-level state -- and
    grows only through :meth:`record`, called once per living agent from the
    ``note_meeting_concluded`` hook (via
    :func:`agents.memory.store.record_meeting_outcome`). The hook reaches
    LIVING agents only, so ``len(self)`` IS the number of meetings this agent
    survived; :meth:`ejection_count` and :meth:`skip_count` partition those
    survived meetings by whether a player was ejected.

    :meth:`record` mirrors :meth:`WorkingMemory.record_sighting`'s guards: it
    rejects a negative ``end_tick`` and enforces non-decreasing ``end_tick``
    order. Meetings conclude in gameplay-tick order, so an out-of-order write
    is a wiring bug, not a normal state (AGENTS.md "no silent fallbacks"). An
    ``end_tick`` EQUAL to the previous one is allowed for the same reason the
    sighting guard allows it -- a repeated fold of the same resume tick must
    not raise.
    """

    def __init__(self) -> None:
        self._outcomes: list[MeetingOutcome] = []

    @property
    def outcomes(self) -> tuple[MeetingOutcome, ...]:
        """Recorded outcomes in insertion (non-decreasing ``end_tick``) order."""

        return tuple(self._outcomes)

    def __len__(self) -> int:
        return len(self._outcomes)

    def ejection_count(self) -> int:
        """Recorded meetings that EJECTED a player (``ejected_id is not None``)."""

        return sum(1 for outcome in self._outcomes if outcome.ejected_id is not None)

    def skip_count(self) -> int:
        """Recorded meetings that SKIPPED or tied (``ejected_id is None``)."""

        return sum(1 for outcome in self._outcomes if outcome.ejected_id is None)

    def record(self, *, end_tick: int, ejected_id: PlayerId | None) -> None:
        if end_tick < 0:
            raise ValueError(f"meeting end_tick must be non-negative, got {end_tick}")
        previous = self._outcomes[-1] if self._outcomes else None
        if previous is not None and end_tick < previous.end_tick:
            raise ValueError(
                "meeting outcomes must be recorded in non-decreasing end_tick "
                f"order: got tick {end_tick} after tick {previous.end_tick}"
            )
        self._outcomes.append(MeetingOutcome(end_tick=end_tick, ejected_id=ejected_id))
