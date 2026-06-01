"""§6.3 win-condition self-check (DESIGN.md §3.5, §6.3; audit A-A-3 / gp-7).

A reconstruction-based verification pass, not a metric. It re-derives, for a
recorded game, two ticks and asserts they are equal:

* ``first_zero_impostor_tick`` — the FIRST tick at which zero impostors remain
  alive (whether they were ejected at a meeting or killed, e.g. friendly fire).
* ``game_over_tick`` — the tick the game actually ended (the recorded
  ``game_over`` row).

DESIGN.md §6.3 / §3.5 require the engine to declare a crew win the moment the
last impostor is eliminated, so a faithful recording must have
``first_zero_impostor_tick == game_over_tick``. A game that ran on past the
all-impostors-eliminated tick is the win-condition regression the gameplay-data
audit (A-A-3) confirmed CLOSED; this check keeps it closed as a durable,
in-suite assertion (the in-repo form of the audit's
``audits/workflows/extract_gameplay_facts.py`` extract self-check). When the
impostors are never all eliminated (crew win by tasks, impostor win by parity,
or a non-decisive game) ``first_zero_impostor_tick`` is ``None`` and the
invariant is vacuously satisfied.

The replay JSONL persists only ``state_hash`` + the recorded action stream
(``orchestrator/replay.py``), never per-tick alive flags, so this module
re-seeds the engine and re-applies the recorded actions through
:func:`engine.tick.advance_tick` / :func:`orchestrator.game.apply_meeting_result`
to recover the alive-impostor count per tick — the same read-only engine
playback :class:`api.replay_loader.ReplayLoader` and :mod:`eval.leak_test`
already perform (``eval`` is the privileged eval surface, not behind the
observation firewall). Every reconstructed ``state_hash`` is checked against the
recording, so a wrong roster or a determinism break fails loud rather than
silently producing a misleading tick.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, TypeAdapter

from engine.actions import Action
from engine.events import MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, load_canonical_map
from meetings.schemas import MeetingResult
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


def win_condition_is_consistent(
    first_zero_impostor_tick: int | None, game_over_tick: int | None
) -> bool:
    """Return whether the §6.3 win-condition invariant holds for one game.

    Pure predicate. When ``first_zero_impostor_tick`` is ``None`` the impostors
    were never all eliminated, so the invariant is vacuously satisfied
    (``True``). Otherwise the game must end on exactly that tick:
    ``game_over_tick == first_zero_impostor_tick``. A game that eliminated every
    impostor but recorded a later (or absent) ``game_over`` tick is the §6.3
    regression and returns ``False``.
    """

    if first_zero_impostor_tick is None:
        return True
    return game_over_tick == first_zero_impostor_tick


class WinConditionSelfCheck(BaseModel):
    """One game's §6.3 win-condition self-check result (DESIGN.md §6.3).

    Frozen value object. ``first_zero_impostor_tick`` is the first reconstructed
    tick with zero impostors alive (``None`` if they were never all eliminated);
    ``game_over_tick`` is the recorded ``game_over`` tick (``None`` for a
    partial / non-decisive game). :attr:`is_consistent` applies
    :func:`win_condition_is_consistent`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    game_id: str
    seed: int
    winner: WinnerSide | None
    reason: str | None
    first_zero_impostor_tick: int | None
    game_over_tick: int | None

    @property
    def is_consistent(self) -> bool:
        """True iff the §6.3 invariant holds (see :func:`win_condition_is_consistent`)."""

        return win_condition_is_consistent(
            self.first_zero_impostor_tick, self.game_over_tick
        )


class WinConditionRegressionError(RuntimeError):
    """A recorded game ran past the tick its last impostor was eliminated.

    The §6.3 win-condition regression (DESIGN.md §6.3): alive impostors reached
    zero at ``first_zero_impostor_tick`` but ``game_over`` was recorded later (or
    not at all). Raised by :func:`assert_win_condition_consistent`.
    """

    def __init__(self, check: WinConditionSelfCheck) -> None:
        self.check = check
        super().__init__(
            f"§6.3 win-condition regression in {check.game_id!r} (seed "
            f"{check.seed}): alive impostors reached zero at tick "
            f"{check.first_zero_impostor_tick}, but game_over was recorded at "
            f"tick {check.game_over_tick} ({check.winner}/{check.reason}). The "
            "game ran past the crew-win point — verify the replay was recorded "
            "with the §6.3 alive-impostors==0 win condition."
        )


def assert_win_condition_consistent(check: WinConditionSelfCheck) -> None:
    """Raise :class:`WinConditionRegressionError` if ``check`` is inconsistent."""

    if not check.is_consistent:
        raise WinConditionRegressionError(check)


def check_replay_win_condition(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
    game_map: Map | None = None,
) -> WinConditionSelfCheck:
    """Reconstruct one recorded replay and compute its §6.3 self-check.

    Re-seeds from ``seed`` + the given roster and re-applies the recorded action
    stream (and meeting outcomes) through the engine, tracking the alive-impostor
    count after every tick AND after every meeting resolution. Every
    reconstructed ``state_hash`` is verified against the recording, so a wrong
    roster (or a determinism break) raises :class:`ValueError` rather than
    yielding a misleading tick. ``game_over_tick`` / ``winner`` / ``reason`` come
    from the authoritative recorded ``game_over`` row (``None`` when the run
    never wrote one — a partial / aborted game).
    """

    resolved_map = game_map if game_map is not None else load_canonical_map()
    game_id = f"headless-seed-{seed}"

    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: Mapping[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }
    game_end = next(
        (entry for entry in entries if isinstance(entry, GameEndReplayEntry)), None
    )

    state = seed_initial_state(
        seed=seed,
        game_map=resolved_map,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )

    first_zero_impostor_tick: int | None = None

    def _record_zero(tick: int) -> None:
        nonlocal first_zero_impostor_tick
        if first_zero_impostor_tick is not None:
            return
        alive_impostors = sum(
            1
            for player in state.players.values()
            if player.alive and player.role == "IMPOSTOR"
        )
        if alive_impostors == 0:
            first_zero_impostor_tick = tick

    for entry in tick_entries:
        actions = [_ACTION_ADAPTER.validate_python(dict(raw)) for raw in entry.actions]
        state, events = advance_tick(state, actions, game_map=resolved_map)
        _verify_hash(game_id, entry.tick, entry.state_hash, _state_hash(state))
        _record_zero(entry.tick)

        if state.phase == "GAME_OVER":
            break
        if state.phase != "MEETING":
            continue

        meeting_entry = meeting_by_tick.get(entry.tick)
        if meeting_entry is None:
            # Partial replay: a meeting opened but never resolved (the run
            # crashed mid-meeting). The recorded timeline stops here, so stop the
            # walk — matching the loader's partial-replay handling.
            break

        body_id = next(
            (
                event.body_id
                for event in events
                if isinstance(event, MeetingTriggeredEvent)
            ),
            None,
        )
        result = MeetingResult(
            meeting_id=meeting_entry.meeting_id,
            triggered_by=meeting_entry.triggered_by,
            trigger_tick=meeting_entry.tick,
            outcome=meeting_entry.outcome,
            ejected_player_id=meeting_entry.ejected_player_id,
            ballots=meeting_entry.ballots,
            contradictions=meeting_entry.contradictions,
            transcript=meeting_entry.transcript,
        )
        state, _ = apply_meeting_result(
            state, result, game_map=resolved_map, triggering_body_id=body_id
        )
        _verify_hash(
            game_id, entry.tick, meeting_entry.state_hash_after, _state_hash(state)
        )
        _record_zero(meeting_entry.tick)
        if state.phase == "GAME_OVER":
            break

    return WinConditionSelfCheck(
        game_id=game_id,
        seed=seed,
        winner=game_end.winner if game_end is not None else None,
        reason=game_end.reason if game_end is not None else None,
        first_zero_impostor_tick=first_zero_impostor_tick,
        game_over_tick=game_end.tick if game_end is not None else None,
    )


def _verify_hash(game_id: str, tick: int, expected: str, actual: str) -> None:
    """Fail loud if a reconstructed ``state_hash`` diverges from the recording."""

    if actual != expected:
        raise ValueError(
            f"win-condition self-check reconstruction diverged for {game_id!r} at "
            f"tick {tick}: recorded {expected!r}, reconstructed {actual!r}. The "
            "roster passed to check_replay_win_condition does not match the "
            "recording, or engine playback is non-deterministic."
        )


__all__ = [
    "WinConditionRegressionError",
    "WinConditionSelfCheck",
    "assert_win_condition_consistent",
    "check_replay_win_condition",
    "win_condition_is_consistent",
]
