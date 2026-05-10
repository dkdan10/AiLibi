"""Episodic memory store (DESIGN.md §6.1, §6.5).

Append-only log of typed events with provenance. Each agent owns its own
``MemoryStore``; the store is the single source of truth that perception
(Task 2.4) writes into and that tactical policies (Tasks 2.6 / 2.7) read
through belief and working memory.

Read paths beyond ``recent`` and prompt rendering ship in Phase 3 (Task 3.3).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EpisodicEvent:
    """One typed, agent-visible memory entry.

    ``provenance`` distinguishes how the agent learned the event (e.g.
    ``"observed"`` for first-hand perception vs. ``"reported"`` for a
    meeting claim or ``"inferred"`` for derivations from other events).
    """

    tick: int
    type: str
    payload: Mapping[str, Any]
    provenance: str


class MemoryStore:
    """Append-only episodic log for a single agent.

    Events are written by perception in monotonic tick order. The store
    rejects out-of-order writes so replay determinism is preserved and
    bugs in the perception layer surface immediately.
    """

    def __init__(self) -> None:
        self._events: list[EpisodicEvent] = []

    def __len__(self) -> int:
        return len(self._events)

    def append(self, event: EpisodicEvent) -> None:
        if self._events and event.tick < self._events[-1].tick:
            raise ValueError(
                "episodic events must be appended in non-decreasing tick order: "
                f"got tick {event.tick} after tick {self._events[-1].tick}"
            )
        self._events.append(event)

    def recent(self, *, since_tick: int) -> tuple[EpisodicEvent, ...]:
        """Return events with ``tick >= since_tick`` in append order."""

        return tuple(event for event in self._events if event.tick >= since_tick)
