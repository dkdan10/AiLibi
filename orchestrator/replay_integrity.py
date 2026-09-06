"""Bind replay metadata to the engine transitions a reader already reconstructs.

Raw parsing and cost accounting can inspect incomplete artifacts without playing
them. A spectator must additionally check row order, transition labels, and
outcome claims before presenting the reconstructed timeline as a game.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import NoReturn

from engine.events import EngineEvent, GameOverEvent, MeetingTriggeredEvent
from engine.world import WorldState
from orchestrator.replay import (
    AbortedMeetingReplayEntry,
    FailedCallReplayEntry,
    GameEndReplayEntry,
    GameStopReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    ReplayLogEntry,
    recorded_experiment_config,
    recorded_testimony_shapes,
    recorded_temporal_observations,
)


class ReplayIntegrityError(ValueError):
    """A recording's metadata contradicts its ordered engine timeline."""

    def __init__(
        self, *, game_id: str, code: str, detail: str, tick: int | None = None
    ) -> None:
        self.game_id = game_id
        self.code = code
        self.tick = tick
        location = f" at tick {tick}" if tick is not None else ""
        super().__init__(f"Replay {game_id}{location}: {code}: {detail}")


class ReplayIntegrityValidator:
    """Check one complete walk without advancing or hashing engine state twice.

    Call ``check_tick`` before each advance, ``check_advance`` after its hash
    passes, and ``check_meeting_result`` after each verified meeting application.
    ``finish`` is required even for a truncated walk. It distinguishes a valid
    partial file from one whose remaining rows were silently ignored.
    """

    def __init__(self, entries: Sequence[ReplayLogEntry], *, game_id: str) -> None:
        self._game_id = game_id
        try:
            recorded_temporal_observations(entries)
        except ValueError as exc:
            self._fail("observation_version_mismatch", str(exc))
        try:
            recorded_experiment_config(entries)
            recorded_testimony_shapes(entries)
        except ValueError as exc:
            self._fail("substrate_version_mismatch", str(exc))
        self._ticks: list[ReplayEntry] = []
        self._meetings: dict[int, MeetingReplayEntry | AbortedMeetingReplayEntry] = {}
        self._side_ids: dict[int, str] = {}
        self._game_end: GameEndReplayEntry | None = None
        self._game_stop: GameStopReplayEntry | None = None
        self._next_tick = 0
        self._pending_meeting = False
        self._consumed_ticks = 0
        self._terminal: GameOverEvent | None = None
        meeting_ids: set[str] = set()
        meeting_ticks: dict[str, int] = {}
        call_ids: set[tuple[str, str]] = set()
        last_tick: ReplayEntry | None = None
        for entry in entries:
            if entry.game_id != game_id:
                self._fail("row_order", "row belongs to another game", entry.tick)
            if self._game_end is not None or self._game_stop is not None:
                self._fail(
                    "row_order", "record follows a final outcome or stop", entry.tick
                )
            if isinstance(entry, ReplayEntry):
                self._ticks.append(entry)
                last_tick = entry
                continue
            if isinstance(entry, GameEndReplayEntry):
                self._game_end = entry
                continue
            if isinstance(entry, GameStopReplayEntry):
                self._game_stop = entry
                continue
            if last_tick is None or entry.tick != last_tick.tick:
                self._fail(
                    "row_order",
                    "meeting record is outside its trigger tick",
                    entry.tick,
                )
            if not entry.meeting_id:
                self._fail("row_order", "meeting identity is empty", entry.tick)
            if isinstance(entry, (MeetingReplayEntry, AbortedMeetingReplayEntry)):
                if entry.tick in self._meetings or entry.meeting_id in meeting_ids:
                    self._fail("row_order", "duplicate meeting record", entry.tick)
                self._meetings[entry.tick] = entry
                meeting_ids.add(entry.meeting_id)
            # Failed calls may follow a resolved/aborted row or stand alone at
            # an interrupted meeting. All rows at the boundary name one meeting.
            if isinstance(
                entry,
                (MeetingReplayEntry, AbortedMeetingReplayEntry, FailedCallReplayEntry),
            ):
                previous_tick = meeting_ticks.setdefault(entry.meeting_id, entry.tick)
                if previous_tick != entry.tick:
                    self._fail(
                        "row_order",
                        "meeting identity refers to multiple ticks",
                        entry.tick,
                    )
                previous_id = self._side_ids.setdefault(entry.tick, entry.meeting_id)
                if previous_id != entry.meeting_id:
                    self._fail(
                        "row_order",
                        "conflicting meeting identities at one tick",
                        entry.tick,
                    )
            if isinstance(entry, FailedCallReplayEntry) and entry.call_id is not None:
                identity = (entry.meeting_id, entry.call_id)
                if identity in call_ids:
                    self._fail(
                        "row_order", "duplicate failed-call identity", entry.tick
                    )
                call_ids.add(identity)

    def _fail(self, code: str, detail: str, tick: int | None = None) -> NoReturn:
        raise ReplayIntegrityError(
            game_id=self._game_id, code=code, detail=detail, tick=tick
        )

    def meeting_id_for_tick(self, tick: int) -> str | None:
        """Return the consistent identity retained at a meeting boundary."""
        return self._side_ids.get(tick)

    def check_tick(self, entry: ReplayEntry, pre_state: WorldState) -> None:
        """Bind the next row's label to the input tick of the engine step."""
        if (
            self._consumed_ticks >= len(self._ticks)
            or entry != self._ticks[self._consumed_ticks]
            or pre_state.phase != "PLAY"
        ):
            self._fail(
                "row_order", "tick cannot follow the reconstructed state", entry.tick
            )
        if entry.tick != pre_state.tick:
            self._fail(
                "tick_label_mismatch",
                f"recorded tick {entry.tick}, expected {pre_state.tick}",
                entry.tick,
            )
        self._consumed_ticks += 1

    def check_advance(
        self, entry: ReplayEntry, state: WorldState, events: Sequence[EngineEvent]
    ) -> None:
        """Match meeting metadata to the verified tick and its actual trigger."""
        self._observe_events(events)
        meeting = self._meetings.get(entry.tick)
        self._next_tick = state.tick
        self._pending_meeting = state.phase == "MEETING"
        if state.phase != "MEETING":
            if entry.tick in self._side_ids:
                self._fail(
                    "meeting_trigger_mismatch",
                    "record has no engine meeting",
                    entry.tick,
                )
            return
        trigger = next(
            (event for event in events if isinstance(event, MeetingTriggeredEvent)),
            None,
        )
        if trigger is None or trigger.tick != entry.tick:
            self._fail(
                "meeting_trigger_mismatch",
                "engine meeting lacks its trigger",
                entry.tick,
            )
        if isinstance(meeting, MeetingReplayEntry):
            if meeting.triggered_by != trigger.actor:
                self._fail(
                    "meeting_trigger_mismatch",
                    "record names a different reporter",
                    entry.tick,
                )
            if meeting.state_hash_before != entry.state_hash:
                self._fail(
                    "meeting_pre_hash_mismatch",
                    "meeting pre-state differs from the verified trigger state",
                    entry.tick,
                )

    def check_meeting_result(
        self, state: WorldState, events: Sequence[EngineEvent]
    ) -> None:
        """Bind the next stop to the actual, hash-verified meeting result state."""
        if not self._pending_meeting or state.phase == "MEETING":
            self._fail(
                "row_order", "meeting result has no pending transition", state.tick
            )
        self._next_tick = state.tick
        self._pending_meeting = False
        self._observe_events(events)

    def _observe_events(self, events: Sequence[EngineEvent]) -> None:
        """Retain the engine's terminal event from a tick or meeting resolution."""
        for event in events:
            if isinstance(event, GameOverEvent):
                if self._terminal is not None:
                    self._fail(
                        "row_order", "multiple reconstructed game endings", event.tick
                    )
                self._terminal = event

    def finish(self) -> None:
        """Reject ignored rows and forged endings while allowing a valid prefix."""
        if self._consumed_ticks != len(self._ticks):
            self._fail(
                "row_order", "unconsumed ticks follow an interrupted or terminal game"
            )
        end = self._game_end
        stop = self._game_stop
        if stop is not None:
            if self._terminal is not None:
                self._fail(
                    "recorded_outcome_mismatch",
                    "stop replaces an engine terminal outcome",
                    stop.tick,
                )
            if stop.tick != self._next_tick:
                self._fail(
                    "stop_tick_mismatch",
                    f"recorded stop tick {stop.tick}, expected {self._next_tick}",
                    stop.tick,
                )
            if (stop.reason == "MEETING_PHASE_REACHED") != self._pending_meeting:
                self._fail(
                    "stop_reason_mismatch",
                    "stop reason does not match the reconstructed phase",
                    stop.tick,
                )
            if any(
                isinstance(row, AbortedMeetingReplayEntry)
                for row in self._meetings.values()
            ):
                self._fail(
                    "row_order", "normal stop follows an aborted meeting", stop.tick
                )
        if end is None:
            return
        terminal = self._terminal
        if (
            terminal is None
            or end.winner != terminal.winner
            or end.reason != terminal.reason
        ):
            self._fail(
                "recorded_outcome_mismatch",
                "game_over does not match a reconstructed terminal event",
                end.tick,
            )
        if end.tick is not None and end.tick != terminal.tick:
            self._fail(
                "terminal_tick_mismatch",
                f"recorded terminal tick {end.tick}, expected {terminal.tick}",
                end.tick,
            )
