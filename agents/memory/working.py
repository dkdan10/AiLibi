"""Working memory (DESIGN.md §6.1).

Per-agent scratch and bounded tactical state: goal/path scaffolding, a derived
last_seen lookup, and an optional investigation intention. These objects belong
to one agent throughout a run; they do not persist across runs. Investigation
state survives tick and meeting boundaries without becoming witness evidence.

This module ships the write paths that perception (Task 2.4) and tactical
policies (Tasks 2.6 / 2.7) need to set and overwrite scratch state. Higher
level rendering of working memory belongs to Task 3.3.

CURRENT STATUS — ``last_seen`` is WIRED; ``set_goal`` / ``set_path`` remain
without a production writer. ``record_sighting`` has exactly one production
caller, ``agents/memory/store.py``'s ``_record_last_seen_sightings`` at render
time, which records each subject's LATEST first-hand sighting so ``_last_seen``
fills and the §6.6 belief-line suffix renders. Every first-hand row counts — a
witnessed room→room transition and an ordinary look alike — so the rendered
suffix is the argmax over the agent's own log and cannot contradict an
observation printed above it. The writer is idempotent (it skips a row not after the
recorded last-seen) so the repeated renders a meeting drives never trip
``record_sighting``'s non-decreasing-tick guard, and it is
§4.7-firewall-suppressed. ``set_goal`` / ``set_path`` are still scaffolding (zero
non-test callers), NOT dead code to delete.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

from agents.memory.investigation import InvestigationState

PlayerId: TypeAlias = str
RoomId: TypeAlias = str

#: A role as ANNOUNCED at the table. Spelled as a local literal alias rather than
#: imported from ``engine``: ``agents/`` may not import the engine (.importlinter),
#: and the only role that ever reaches this module is the confirm-ejects
#: announcement the orchestrator translates.
RevealedRole: TypeAlias = Literal["CREWMATE", "IMPOSTOR"]


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
    """One concluded meeting's PUBLIC result.

    Every field is a fact ANNOUNCED at the table, which is what makes the row
    firewall-clean by construction (DESIGN.md §4.7, the same public footing as a
    meeting's ``dead_ids``):

    * ``end_tick`` -- the tick gameplay resumed at.
    * ``ejected_id`` -- the player the vote removed; ``None`` on a skip or tie.
    * ``revealed_role`` -- the confirm-ejects announcement of that player's role,
      public at the table on exactly the ejection's own footing. ``None`` on a
      skip, and never set for a player who was KILLED: nobody saw that role.
    * ``votes_for_ejected`` / ``skip_votes`` -- the announced tally.
    * ``roster_impostor_count`` -- the impostor count stated at game start, which
      :meth:`MeetingHistory.impostors_remaining_after` counts down from.

    The four optional fields default to ``None`` so a fold that knows only the
    resume tick and the ejection still records, and the v3 tactical feature
    encoder's three-scalar meeting-history channel reads exactly what it read
    before they existed.
    """

    end_tick: int
    ejected_id: PlayerId | None
    revealed_role: RevealedRole | None = None
    votes_for_ejected: int | None = None
    skip_votes: int | None = None
    roster_impostor_count: int | None = None


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
        self._investigation: InvestigationState | None = None

    @property
    def investigation(self) -> InvestigationState | None:
        return self._investigation

    def cancel_investigation_plan(self) -> None:
        """Cancel at a public meeting boundary, preserving sources and decision cache.

        This lifecycle transition cannot replace a decision or restart its
        clock. The next gameplay packet receives an ordinary fresh decision.
        """

        if self._investigation is not None:
            self._investigation = self._investigation.model_copy(
                update={"active_plan": None}
            )

    def set_investigation_state(
        self, state: InvestigationState, *, known_player_ids: tuple[str, ...]
    ) -> None:
        """Store one transition without losing source consumption or cached inputs."""

        known = set(known_player_ids)
        if len(known) != len(known_player_ids):
            raise ValueError("known investigation identities must be distinct")
        consumed = {row.target_id: row for row in state.consumed_sources}
        if not set(consumed) <= known or (
            state.active_plan is not None and state.active_plan.target_id not in known
        ):
            raise ValueError("investigation state exceeds the known player roster")
        previous = self._investigation
        if previous is not None:
            if previous.last_processed_tick is not None:
                if (
                    state.last_processed_tick is None
                    or state.last_processed_tick < previous.last_processed_tick
                ):
                    raise ValueError(
                        "investigation decision tick cannot move backwards"
                    )
                if (
                    state.last_processed_tick == previous.last_processed_tick
                    and state != previous
                ):
                    raise ValueError(
                        "conflicting investigation state for one decision tick"
                    )
            for prior in previous.consumed_sources:
                current = consumed.get(prior.target_id)
                if current is None or current.source_tick < prior.source_tick:
                    raise ValueError("investigation cannot forget a consumed source")
                if current.source_tick == prior.source_tick and current != prior:
                    raise ValueError(
                        "consumed source identity cannot change at one tick"
                    )
        self._investigation = state

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

    def forget_sighting(self, player_id: PlayerId) -> None:
        """Drop a recorded placement outright; a no-op if none is recorded.

        The retraction :meth:`record_sighting`'s non-decreasing-tick guard cannot
        express. A placement is not only superseded by a later one — it can stop
        being sayable at all, when evidence appended since it was recorded makes
        the sighting it came from §4.7-suppressed. Rewinding to an earlier tick is
        still refused; erasing is the whole retraction.
        """

        self._last_seen.pop(player_id, None)

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

    def impostors_remaining_after(self, index: int) -> int | None:
        """Impostors still at large once the outcome at ``index`` was announced.

        The roster impostor count stated at game start minus the ejections
        CONFIRMED impostor up to and including ``index``. A kill never moves the
        number: only a confirm-ejects announcement removes an impostor the table
        can account for. ``None`` when no outcome at or before ``index`` carries
        the roster count -- the number is then underivable and the caller states
        nothing rather than guessing (AGENTS.md "no silent fallbacks").
        """

        if not 0 <= index < len(self._outcomes):
            raise IndexError(
                f"no recorded meeting outcome at index {index} "
                f"({len(self._outcomes)} recorded)"
            )
        considered = self._outcomes[: index + 1]
        roster: int | None = None
        for outcome in reversed(considered):
            if outcome.roster_impostor_count is not None:
                roster = outcome.roster_impostor_count
                break
        if roster is None:
            return None
        confirmed = sum(
            1 for outcome in considered if outcome.revealed_role == "IMPOSTOR"
        )
        return roster - confirmed

    def record(
        self,
        *,
        end_tick: int,
        ejected_id: PlayerId | None,
        revealed_role: RevealedRole | None = None,
        votes_for_ejected: int | None = None,
        skip_votes: int | None = None,
        roster_impostor_count: int | None = None,
    ) -> None:
        if end_tick < 0:
            raise ValueError(f"meeting end_tick must be non-negative, got {end_tick}")
        if ejected_id is None and revealed_role is not None:
            raise ValueError(
                "a skipped meeting reveals no role: got revealed_role "
                f"{revealed_role!r} with ejected_id=None"
            )
        previous = self._outcomes[-1] if self._outcomes else None
        if previous is not None and end_tick < previous.end_tick:
            raise ValueError(
                "meeting outcomes must be recorded in non-decreasing end_tick "
                f"order: got tick {end_tick} after tick {previous.end_tick}"
            )
        self._outcomes.append(
            MeetingOutcome(
                end_tick=end_tick,
                ejected_id=ejected_id,
                revealed_role=revealed_role,
                votes_for_ejected=votes_for_ejected,
                skip_votes=skip_votes,
                roster_impostor_count=roster_impostor_count,
            )
        )
