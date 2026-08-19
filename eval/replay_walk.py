"""The parameterized replay walker — shared MECHANICS, per-consumer PROFILES.

Task 19.25 (audits/audit-phase-19-triage.md §7 item 25 + C3, closing §7 items
1–2): eight eval modules carried nine independent ``advance_tick`` /
``apply_meeting_result`` reconstruction loop bodies. This module is their one
home for the MECHANICS — and deliberately nothing more, because the owner
review established the per-module differences are partly DELIBERATE, not
drift: ``eval/validity.py`` tolerates a partial-meeting replay by design while
``eval/funnel.py`` fails it loudly, and the leak-scan factory walk performs no
integrity checking at all. A union of checks would CHANGE validation behavior
(locked decision 1 forbids it), so EVERY integrity check — state-hash
verification and doubled-record detection included — is a profile-declared
OPTION on :class:`ReplayWalkConfig`. NO check is core-mandatory.

Scope of that claim, precisely: it covers every check THE WALKER ITSELF
performs. The walker parses recordings through
:func:`orchestrator.replay.read_all_entries`, which keeps its own pre-existing
mandatory malformed-bytes rejections (two ``tick`` rows sharing a tick, or a
second ``game_over`` row — the doubled-FILE corruption pattern, DESIGN.md
§11.4 / Task 4.16 — plus Pydantic validation of each row). Those parse-layer
rejections applied identically to ALL NINE pre-migration loop bodies (every
one called ``read_all_entries``), so they are not profile options and
loosening them here would WIDEN what the no-check profile accepts — the exact
behavior change this task forbids. The profile-optional "doubled-record
detection" is the doubled MEETING-row check, which the parser cannot see: a
tick-keyed lookup silently collapses it unless a profile enables
``reject_duplicate_meeting_rows``.

The mechanics core (always on, check-free)
------------------------------------------
Re-seed via :func:`orchestrator.seeder.seed_initial_state`; per recorded tick
row deserialize the recorded actions and :func:`engine.tick.advance_tick`; on
a MEETING transition rebuild the :class:`~meetings.schemas.MeetingResult` from
the recorded meeting row and :func:`orchestrator.game.apply_meeting_result`
(``triggering_body_id`` from the tick's :class:`MeetingTriggeredEvent`;
``None`` when absent — the engine stamps ``body_id=None`` on emergency
triggers); stop at GAME_OVER. ``last_events`` is threaded exactly as
``orchestrator.game.HeadlessGame._run_loop`` threads it — the previous tick's
events, or across a meeting the pre-meeting play events plus the meeting's
post-events — so packet-building consumers see the live loop's contract.

Callers FOLD, never subclass: :func:`walk_replay` is a generator of typed
per-tick events —

* :class:`TickOpened` — before the advance: the recorded row, the PRE-advance
  state, and ``last_events`` (the packet-building seam: the leak scan and both
  funnel walks build/ingest observation packets here);
* :class:`TickAdvanced` — after the advance (and after the profile's tick-hash
  check): pre-state, post-state, and the tick's events (the fact-collection
  seam: kills, frames, vent sightings, zero-impostor census);
* :class:`MeetingOpened` — a meeting row matched to its trigger tick, after
  the profile's pre-hash/tally checks but BEFORE ``apply_meeting_result`` (the
  pre-resolution seam: funnel's report-meeting collection, the vj walk's
  meeting-open memory snapshots and its trigger/living-vs-voters checks);
* :class:`MeetingApplied` — after ``apply_meeting_result`` and the profile's
  post-hash check (the post-resolution seam: belief absorption, post-meeting
  ``GameOverEvent`` collection);
* :class:`WalkComplete` — after the loop and the profile's post-walk checks:
  the final state, the recorded ``game_over`` row, and the terminal tick.

A check that fails calls the profile's ``on_violation`` hook with a typed
:class:`WalkViolation` and REQUIRES it to raise (the walker raises
``RuntimeError`` if a hook returns — no silent fallbacks), so every consumer
keeps its own exception type and byte-identical message.

The config, events, and violation records are FROZEN DATACLASSES, not
Pydantic, deliberately: they carry engine frozen dataclasses
(:class:`~engine.world.WorldState`, ``EngineEvent``) across an eval-internal
seam — the :class:`eval.funnel._VJMeeting` / ``_VJGameWalk`` precedent (the
same kind of walk carrier, crossing the same kind of boundary). A Pydantic
wrapper would need ``arbitrary_types_allowed`` for every engine field and
would re-validate already-typed parser/engine values per tick per game while
validating nothing new; AGENTS.md's Pydantic rule targets boundary DTOs, and
its companion rule ("frozen dataclasses for engine state") is the one these
carriers follow.

The profile table (the Task 19.25 drift record)
-----------------------------------------------
Each consumer declares a NAMED profile preserving its current, deliberate
semantics. The negative fixtures live in ``tests/eval/test_replay_walk.py``
(one per profile, proving each still bites — or still tolerates — what it did
before the migration).

=========================  =====  ====  ============  ====  =====  ====  ==========================
Profile                    tick   dup   missing-      pre   tally  post  post-walk checks
(consumer)                 hash   rows  meeting row   hash         hash
=========================  =====  ====  ============  ====  =====  ====  ==========================
``validity-gate``          ON     off   truncate      off   off    ON    none
(eval/validity)
``win-condition-           ON     off   truncate      off   off    ON    none
selfcheck``
(eval/win_condition_
selfcheck)
``kill-gift``              ON     off   truncate      off   off    ON    none
(eval/balance_eval)
``watchability-referee``   ON     ON    violation     ON    ON     ON    terminal + reconstructed
(eval/watchability)                                                      outcome + trailing rows +
                                                                         game_over row + forged
                                                                         winner/reason
``kill-craft``             ON     ON    violation     ON    off    ON    terminal + trailing rows +
(eval/kill_craft)                                                        game_over row
``solvability``            ON     ON    violation     ON    off    ON    terminal + trailing rows +
(eval/solvability)                                                       game_over row
``funnel-instrument``      ON     off   violation     ON    off    ON    none
(eval/funnel, both walks)
``leak-scan-factory``      off    off   violation     off   off    off   none
(eval/leak_scan)
=========================  =====  ====  ============  ====  =====  ====  ==========================

What each profile deliberately relaxes, and why:

* ``validity-gate`` / ``win-condition-selfcheck`` / ``kill-gift`` — a MEETING
  tick with no meeting row TRUNCATES the walk (a run that crashed mid-meeting;
  the recorded timeline stops there), matching ``api.replay_loader``'s
  partial-replay serving. This tolerance is BY DESIGN: these passes score what
  a recording contains, and validity's separate checks (its game-over /
  duplicate-row checks) own completeness. They verify the per-tick
  ``state_hash`` and each meeting's ``state_hash_after`` but deliberately not
  ``state_hash_before`` (the pre-hash equals the just-verified tick hash on
  every recording these walks accept), and none of the referee-grade
  completeness checks.
* ``funnel-instrument`` — the same hash discipline PLUS ``state_hash_before``,
  and a missing meeting row is a loud :class:`~eval.funnel.FunnelReconstructionError`:
  funnel's comment declares the divergence from the loader deliberate — a
  measurement instrument must never silently under-count. The vj walk layers
  two more checks in its OWN fold (a MEETING transition without a
  :class:`MeetingTriggeredEvent`; the reconstructed living set differing from
  the recorded ballot voters) — consumer semantics, not walker options.
* ``watchability-referee`` — every option ON: the referee floors a candidate
  set on ANY integrity breach (all violations collapse to the same bare
  ``_IntegrityBreach``), including the checks no other consumer wants
  (ballots re-tallied against the recorded outcome; a forged ``game_over``
  winner/reason vs the reconstructed terminal event; trailing rows after the
  terminal tick).
* ``kill-craft`` — the watchability set MINUS the ballot tally,
  reconstructed-outcome, and forged-outcome checks (its folds never read
  ballots or the recorded winner), each violation carrying its own
  fail-loud message.
* ``solvability`` — the same check set as ``kill-craft`` and for the same
  reason: the fold reads only meeting trigger bodies and per-tick states, never
  ballots or the recorded winner, and a truncated recording would silently
  under-count the body meetings its whole denominator is made of.
* ``leak-scan-factory`` — NO checks at all, deliberately: the factory walk
  scans packets reconstructed from replays the harness itself recorded moments
  earlier in the same process, and it performed neither hash verification nor
  doubled-record detection before Task 19.25 — enabling either would change
  what it accepts. Its ``on_violation`` preserves the pre-migration byte
  behavior for the one policy it must declare (a missing meeting row raises
  ``KeyError(tick)``, exactly what the old direct dict index raised), and its
  fold fails loud on a MEETING transition with no
  :class:`MeetingTriggeredEvent` (pre-migration a bare ``StopIteration`` from
  a defaultless ``next()``; ``StopIteration`` cannot propagate through a
  generator — PEP 479 — so an explicit ``RuntimeError`` keeps the path
  fail-loud instead of silently continuing over an engine-invariant
  violation).

Byte-parity contract: migrating a consumer onto its profile changes NO
committed pin, report cell, or metric value. A behavior difference between a
consumer's old walk and its declared profile stops the migration and is
recorded as a finding — never silently reconciled in either direction
(tasks/phase-19.md Task 19.25).

``eval/off_menu.py`` is frozen (Task 19.18) and keeps its own loop; the API
and training walks are backlog by the Phase-19 cut line.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, NoReturn, TypeAlias

from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyId
from engine.events import EngineEvent, GameOverEvent, MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, WorldState
from meetings.schemas import MeetingResult
from meetings.voting import tally_ballots
from orchestrator.game import apply_meeting_result
from orchestrator.replay import (
    GameEndReplayEntry,
    MeetingReplayEntry,
    ReplayEntry,
    WinnerSide,
    _state_hash,
    read_all_entries,
)
from orchestrator.seeder import seed_initial_state

_ACTION_ADAPTER: Final[TypeAdapter[Action]] = TypeAdapter(Action)

WalkViolationKind: TypeAlias = Literal[
    "duplicate_meeting_rows",
    "tick_hash_mismatch",
    "missing_meeting_row",
    "meeting_pre_hash_mismatch",
    "ballot_tally_mismatch",
    "meeting_post_hash_mismatch",
    "missing_terminal_tick",
    "missing_reconstructed_outcome",
    "trailing_replay_rows",
    "missing_game_end_row",
    "recorded_outcome_mismatch",
]

# What a profile does when a tick enters MEETING with no recorded meeting row:
# "truncate" stops the walk there (the loader's partial-replay serving);
# "violation" routes through the profile's on_violation hook.
MissingMeetingRowPolicy: TypeAlias = Literal["truncate", "violation"]


@dataclass(frozen=True)
class WalkViolation:
    """One failed profile check, with the data every consumer message needs.

    ``expected`` / ``actual`` are the recorded vs reconstructed state hashes on
    the hash kinds; ``phase`` / ``state_tick`` are the walk-final engine phase
    and tick on ``missing_terminal_tick``; ``terminal_tick`` is set on
    ``trailing_replay_rows``. Fields not meaningful for a kind are ``None``.
    """

    kind: WalkViolationKind
    game_id: str
    tick: int | None = None
    expected: str | None = None
    actual: str | None = None
    phase: str | None = None
    state_tick: int | None = None
    terminal_tick: int | None = None


@dataclass(frozen=True)
class ReplayWalkConfig:
    """One consumer's NAMED validation profile over the shared walk mechanics.

    Every check is an OPTION (module docstring: no check is core-mandatory).
    ``on_violation`` MUST raise; the walker raises ``RuntimeError`` if it
    returns. ``ballot_tally_threshold`` non-``None`` enables the recorded
    ballots-tally-to-outcome check under that skip-confidence threshold
    (:func:`meetings.voting.tally_ballots`). ``verify_meeting_pre_hashes``
    compares each meeting row's ``state_hash_before`` against the
    reconstructed post-advance hash of its trigger tick (equal to the recorded
    tick hash whenever the tick-hash check is also on).
    """

    profile: str
    on_violation: Callable[[WalkViolation], NoReturn]
    verify_tick_hashes: bool = False
    reject_duplicate_meeting_rows: bool = False
    missing_meeting_row: MissingMeetingRowPolicy = "truncate"
    verify_meeting_pre_hashes: bool = False
    ballot_tally_threshold: float | None = None
    verify_meeting_post_hashes: bool = False
    require_terminal_tick: bool = False
    require_reconstructed_outcome: bool = False
    reject_trailing_rows: bool = False
    require_game_end_row: bool = False
    verify_recorded_outcome: bool = False


@dataclass(frozen=True)
class TickOpened:
    """Before the advance: the recorded row, PRE-advance state, ``last_events``.

    ``last_events`` is exactly what the live loop hands ``build_packet`` on
    this tick: the previous tick's events, or across a meeting the pre-meeting
    play events plus the meeting's post-events.
    """

    entry: ReplayEntry
    state: WorldState
    last_events: tuple[EngineEvent, ...]


@dataclass(frozen=True)
class TickAdvanced:
    """After the advance (and the profile's tick-hash check)."""

    entry: ReplayEntry
    pre_state: WorldState
    state: WorldState
    events: tuple[EngineEvent, ...]


@dataclass(frozen=True)
class MeetingOpened:
    """A matched meeting row, checked but NOT yet applied.

    ``state`` is the post-advance state the meeting resolves against;
    ``events`` are the trigger tick's events; ``trigger`` is the tick's
    :class:`MeetingTriggeredEvent` (``None`` only on engine-invariant-breaking
    bytes) and ``body_id`` its reported body (``None`` for an emergency
    meeting).
    """

    entry: MeetingReplayEntry
    trigger: MeetingTriggeredEvent | None
    body_id: BodyId | None
    state: WorldState
    events: tuple[EngineEvent, ...]


@dataclass(frozen=True)
class MeetingApplied:
    """After ``apply_meeting_result`` (and the profile's post-hash check)."""

    entry: MeetingReplayEntry
    result: MeetingResult
    body_id: BodyId | None
    state: WorldState
    post_events: tuple[EngineEvent, ...]


@dataclass(frozen=True)
class WalkComplete:
    """After the loop and the profile's post-walk checks.

    ``state`` is the final walked state (terminal, or where a tolerant profile
    truncated); ``game_end`` the recorded ``game_over`` row if any;
    ``terminal_tick`` the tick whose advance/meeting reached GAME_OVER
    (``None`` when the walk never did).
    """

    state: WorldState
    game_end: GameEndReplayEntry | None
    terminal_tick: int | None


ReplayWalkEvent: TypeAlias = (
    TickOpened | TickAdvanced | MeetingOpened | MeetingApplied | WalkComplete
)


def _violate(config: ReplayWalkConfig, violation: WalkViolation) -> NoReturn:
    config.on_violation(violation)
    raise RuntimeError(  # no silent fallbacks: a hook that returns is a bug
        f"profile {config.profile!r}: on_violation returned instead of raising "
        f"for {violation.kind!r}"
    )


def _meeting_result_from_entry(entry: MeetingReplayEntry) -> MeetingResult:
    return MeetingResult(
        meeting_id=entry.meeting_id,
        triggered_by=entry.triggered_by,
        trigger_tick=entry.tick,
        outcome=entry.outcome,
        ejected_player_id=entry.ejected_player_id,
        ballots=entry.ballots,
        contradictions=entry.contradictions,
        transcript=entry.transcript,
    )


def walk_replay(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    game_map: Map,
    config: ReplayWalkConfig,
) -> Iterator[ReplayWalkEvent]:
    """Re-seed + replay one recording under ``config``'s profile.

    Yields the typed per-tick events the module docstring describes, in walk
    order: ``TickOpened`` → ``TickAdvanced`` → (on a meeting tick)
    ``MeetingOpened`` → ``MeetingApplied`` → … → ``WalkComplete``. Profile
    checks run at their documented points; a failed check calls the profile's
    ``on_violation`` hook, which raises the consumer's own exception.
    """

    game_id = f"headless-seed-{seed}"
    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_entries = [
        entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    ]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in meeting_entries
    }
    game_end = next(
        (entry for entry in entries if isinstance(entry, GameEndReplayEntry)), None
    )

    # A doubled meeting row (same tick or meeting id) is silently collapsed by
    # the dict above, leaving the dropped row's hashes never validated.
    if config.reject_duplicate_meeting_rows and (
        len(meeting_by_tick) != len(meeting_entries)
        or len({entry.meeting_id for entry in meeting_entries}) != len(meeting_entries)
    ):
        _violate(config, WalkViolation(kind="duplicate_meeting_rows", game_id=game_id))

    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )

    hash_needed = config.verify_tick_hashes or config.verify_meeting_pre_hashes
    last_events: tuple[EngineEvent, ...] = ()
    terminal_tick: int | None = None
    reconstructed_winner: WinnerSide | None = None
    reconstructed_reason: str | None = None

    for entry in tick_entries:
        yield TickOpened(entry=entry, state=state, last_events=last_events)

        pre_state = state
        actions = [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in entry.actions]
        state, raw_events = advance_tick(state, actions, game_map=game_map)
        events = tuple(raw_events)
        actual = _state_hash(state) if hash_needed else None
        if config.verify_tick_hashes and actual != entry.state_hash:
            _violate(
                config,
                WalkViolation(
                    kind="tick_hash_mismatch",
                    game_id=game_id,
                    tick=entry.tick,
                    expected=entry.state_hash,
                    actual=actual,
                ),
            )
        for event in events:
            if isinstance(event, GameOverEvent):
                reconstructed_winner = event.winner
                reconstructed_reason = event.reason
        yield TickAdvanced(entry=entry, pre_state=pre_state, state=state, events=events)

        if state.phase == "GAME_OVER":
            terminal_tick = entry.tick
            break
        if state.phase != "MEETING":
            last_events = events
            continue

        meeting_entry = meeting_by_tick.get(entry.tick)
        if meeting_entry is None:
            if config.missing_meeting_row == "truncate":
                # Partial replay: a meeting opened but never resolved (the run
                # crashed mid-meeting). The recorded timeline stops here.
                break
            _violate(
                config,
                WalkViolation(
                    kind="missing_meeting_row", game_id=game_id, tick=entry.tick
                ),
            )
        if (
            config.verify_meeting_pre_hashes
            and meeting_entry.state_hash_before != actual
        ):
            _violate(
                config,
                WalkViolation(
                    kind="meeting_pre_hash_mismatch",
                    game_id=game_id,
                    tick=entry.tick,
                    expected=meeting_entry.state_hash_before,
                    actual=actual,
                ),
            )
        if config.ballot_tally_threshold is not None and tally_ballots(
            meeting_entry.ballots,
            skip_confidence_threshold=config.ballot_tally_threshold,
        ) != (meeting_entry.outcome, meeting_entry.ejected_player_id):
            _violate(
                config,
                WalkViolation(
                    kind="ballot_tally_mismatch", game_id=game_id, tick=entry.tick
                ),
            )

        trigger = next(
            (event for event in events if isinstance(event, MeetingTriggeredEvent)),
            None,
        )
        body_id = trigger.body_id if trigger is not None else None
        yield MeetingOpened(
            entry=meeting_entry,
            trigger=trigger,
            body_id=body_id,
            state=state,
            events=events,
        )

        result = _meeting_result_from_entry(meeting_entry)
        state, raw_post_events = apply_meeting_result(
            state, result, game_map=game_map, triggering_body_id=body_id
        )
        post_events = tuple(raw_post_events)
        if config.verify_meeting_post_hashes:
            after = _state_hash(state)
            if after != meeting_entry.state_hash_after:
                _violate(
                    config,
                    WalkViolation(
                        kind="meeting_post_hash_mismatch",
                        game_id=game_id,
                        tick=entry.tick,
                        expected=meeting_entry.state_hash_after,
                        actual=after,
                    ),
                )
        for event in post_events:
            if isinstance(event, GameOverEvent):
                reconstructed_winner = event.winner
                reconstructed_reason = event.reason
        yield MeetingApplied(
            entry=meeting_entry,
            result=result,
            body_id=body_id,
            state=state,
            post_events=post_events,
        )

        last_events = events + post_events
        if state.phase == "GAME_OVER":
            terminal_tick = entry.tick
            break

    if config.require_terminal_tick and terminal_tick is None:
        _violate(
            config,
            WalkViolation(
                kind="missing_terminal_tick",
                game_id=game_id,
                phase=state.phase,
                state_tick=state.tick,
            ),
        )
    if config.require_reconstructed_outcome and (
        game_end is None or reconstructed_reason is None or terminal_tick is None
    ):
        _violate(
            config,
            WalkViolation(kind="missing_reconstructed_outcome", game_id=game_id),
        )
    # Trailing rows are only decidable against a terminal tick; both profiles
    # that enable this check also require the terminal tick, which raised above.
    if (
        config.reject_trailing_rows
        and terminal_tick is not None
        and (
            any(entry.tick > terminal_tick for entry in tick_entries)
            or any(entry.tick > terminal_tick for entry in meeting_entries)
        )
    ):
        _violate(
            config,
            WalkViolation(
                kind="trailing_replay_rows",
                game_id=game_id,
                terminal_tick=terminal_tick,
            ),
        )
    if config.require_game_end_row and game_end is None:
        _violate(config, WalkViolation(kind="missing_game_end_row", game_id=game_id))
    if (
        config.verify_recorded_outcome
        and game_end is not None
        and (
            game_end.winner != reconstructed_winner
            or game_end.reason != reconstructed_reason
        )
    ):
        _violate(
            config,
            WalkViolation(kind="recorded_outcome_mismatch", game_id=game_id),
        )

    yield WalkComplete(state=state, game_end=game_end, terminal_tick=terminal_tick)


__all__ = [
    "MeetingApplied",
    "MeetingOpened",
    "MissingMeetingRowPolicy",
    "ReplayWalkConfig",
    "ReplayWalkEvent",
    "TickAdvanced",
    "TickOpened",
    "WalkComplete",
    "WalkViolation",
    "WalkViolationKind",
    "walk_replay",
]
