"""Episodic memory store (DESIGN.md §6.1, §6.5).

Append-only log of typed events with provenance. Each agent owns its own
``MemoryStore``; the store is the single source of truth that perception
(Task 2.4) writes into and that tactical policies (Tasks 2.6 / 2.7) read
through belief and working memory.

Read paths beyond ``recent`` and prompt rendering ship in Phase 3 (Task 3.3).

Task 16.5 (C8; audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8)
adds a stable, deterministic ``observation_id`` to each first-hand
``EpisodicEvent``: the citation handle the §6.6 render surfaces (lever-ON) and
the vote ballot cites (16.6 enforces). The id is assigned at WRITE time in
perception (:func:`agents.perception.ingest_packet`) via
:func:`derive_observation_id`; the store enforces its uniqueness so downstream
dangling-id validation can rely on it.
"""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, TypeAlias

ObservationId: TypeAlias = str
"""A stable, deterministic first-hand observation id (Task 16.5, C8).

Downstream tasks import this exact name (``agents.memory.episodic.ObservationId``)
as the citation type for the vote ballot's ``primary_reason_observation_id``
(16.6). It is a plain ``str`` alias, mirroring ``meetings.schemas.TurnId``: a
render/field/reader triplet that all treat the same characters as one opaque id.
"""


def derive_observation_id(*, agent_id: str, tick: int, seq: int) -> ObservationId:
    """The ONE place the observation-id scheme lives (Task 16.5, C8).

    Deterministic ``{agent_id}:{tick}:{seq}`` — a pure function of the append
    coordinates, with NO content hashing, NO floats, and NO RNG. Determinism is
    load-bearing: two reconstructions of the SAME replay walk the identical packet
    sequence, so they regenerate byte-for-byte identical ids, and the id a ballot
    cites in a recorded meeting resolves to the same episodic row on every replay
    (DESIGN.md §5.5 / §6.6). The scheme is FOREVER once a baseline renders ids into
    recorded prompts (the 16.17 graduation): a recorded prompt's ``[obs …]`` bytes
    pin the string, so the format can never change under an adopted baseline — hence
    the deliberately minimal, content-free coordinate scheme here.
    """

    return f"{agent_id}:{tick}:{seq}"


@dataclass(frozen=True)
class EpisodicEvent:
    """One typed, agent-visible memory entry.

    ``provenance`` distinguishes how the agent learned the event (e.g.
    ``"observed"`` for first-hand perception vs. ``"reported"`` for a
    meeting claim or ``"inferred"`` for derivations from other events).

    ``observation_id`` (Task 16.5, C8) is the stable citation handle for a
    first-hand OBSERVED row, stamped at write time by
    :func:`agents.perception.ingest_packet`. It defaults to ``None`` — the
    widen-inert (MeetingParticipant) precedent: the default keeps every existing
    construction site valid and every pre-16.5 fixture parses unchanged. ``None``
    means "not a first-hand citable observation": reported testimony, the inferred
    global aggregate, and any hand-built fixture that predates the id scheme.
    """

    tick: int
    type: str
    payload: Mapping[str, Any]
    provenance: str
    observation_id: ObservationId | None = None


class MemoryStore:
    """Append-only episodic log for a single agent.

    Events are written by perception in monotonic tick order. The store
    rejects out-of-order writes so replay determinism is preserved and
    bugs in the perception layer surface immediately.

    That order guarantee is what :meth:`recent` reads with: a tick window is
    always a suffix of the log, so the store keeps the append-order tick
    sequence beside the events and locates the window with one bisection
    instead of scanning (Task 20.19, finding C-43).
    """

    def __init__(self) -> None:
        self._events: list[EpisodicEvent] = []
        # The append-order tick sequence, non-decreasing by the guard in
        # ``append`` and therefore the sorted key ``recent`` bisects.
        self._ticks: list[int] = []
        # The materialized whole-log view ``recent(since_tick=0)`` returns, held
        # until the next append invalidates it. ``None`` means "not built since
        # the last write"; the whole log is what 29 of the 32 call sites ask for.
        self._full_log: tuple[EpisodicEvent, ...] | None = None
        # Task 16.5: the set of stable observation ids already written into this
        # agent's store, for the fail-loud duplicate guard below. Downstream
        # dangling-id validation (the ballot's ``primary_reason_observation_id``,
        # 16.6) relies on an id being unique within an agent's store, so a
        # collision is a wiring bug, not a normal state.
        self._observation_ids: set[ObservationId] = set()

    def __len__(self) -> int:
        return len(self._events)

    def append(self, event: EpisodicEvent) -> None:
        if self._events and event.tick < self._events[-1].tick:
            raise ValueError(
                "episodic events must be appended in non-decreasing tick order: "
                f"got tick {event.tick} after tick {self._events[-1].tick}"
            )
        # Task 16.5 fail-loud duplicate-id guard (AGENTS.md "no silent fallbacks").
        # A non-None observation id is the deterministic ``{agent}:{tick}:{seq}``
        # handle stamped in perception; the ``seq`` continuation keeps it unique on
        # every legitimate call sequence (including repeated same-tick ingestion),
        # so a re-appeared id means two rows would share a citation handle and the
        # downstream valid-id set would be ambiguous. A ``None`` id is "not a
        # first-hand citable observation" and never enters the set, so any number of
        # ``None`` rows append freely.
        if event.observation_id is not None:
            if event.observation_id in self._observation_ids:
                raise ValueError(
                    "duplicate observation id: "
                    f"{event.observation_id!r} already present in this store"
                )
            self._observation_ids.add(event.observation_id)
        self._events.append(event)
        # Both derived views move with the log: the bisection key grows by one,
        # and the cached whole-log tuple is dropped so the next read rebuilds it.
        # Every guard above raises before this point, so a rejected append leaves
        # events, ticks and cache consistent.
        self._ticks.append(event.tick)
        self._full_log = None

    def recent(self, *, since_tick: int) -> tuple[EpisodicEvent, ...]:
        """Return events with ``tick >= since_tick`` in append order.

        Ticks are non-decreasing, so the answer is the suffix beginning at the
        first index whose tick reaches ``since_tick``: one :func:`bisect_left`
        over the tick sequence locates it. A window starting at index 0 — the
        whole log, which is what nearly every caller asks for — is served from a
        tuple materialized once per write instead of rebuilt per call.
        """

        start = bisect_left(self._ticks, since_tick)
        if start:
            return tuple(self._events[start:])
        if self._full_log is None:
            self._full_log = tuple(self._events)
        return self._full_log
