"""Walker mechanics + per-profile negative fixtures for eval/replay_walk.py.

Task 19.25. Two layers:

* **Mechanics** — :func:`eval.replay_walk.walk_replay` under throwaway test
  profiles: the typed event stream's shape, the live-loop ``last_events``
  threading, and every profile-declared check firing (or staying silent) as an
  OPTION, never as core behavior.
* **Per-profile negative fixtures** (the Task 19.25 drift record's proof
  obligation) — each consumer's NAMED profile still bites, or still tolerates,
  exactly what it did before the migration, exercised through the CONSUMER's
  own walk function so the pins hold both before and after each consumer's
  migration commit: validity/win-condition/kill-gift tolerate a
  partial-meeting replay while funnel and kill-craft fail it loudly; the
  watchability referee floors untallying ballots and a forged outcome; the
  leak-scan factory walk accepts a tampered hash and a doubled meeting row.

All fixtures tamper copies of committed ``replays/samples/4p1i`` bytes (the
kill-craft test module's tamper idiom).
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import NoReturn, cast

import pytest
from pydantic import TypeAdapter

from api.replay_loader import ReplayLoader
from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import GameOverEvent
from engine.tick import advance_tick
from engine.world import Map, load_canonical_map
from eval._suspicion_parse import SKIP_SUSPICION_THRESHOLD
from eval import (
    balance_eval,
    evidence_honesty,
    funnel,
    kill_craft,
    leak_scan,
    solvability,
    validity,
    watchability,
    win_condition_selfcheck,
)
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    ReplayWalkConfig,
    ReplayWalkEvent,
    TickAdvanced,
    TickOpened,
    WalkComplete,
    WalkViolation,
    walk_replay,
)
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    ReplayLog,
    classify_action_dispositions,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"
_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


# --------------------------------------------------------------------------- #
# Fixture helpers — tampered copies of committed 4p1i bytes.                    #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def game_map() -> Map:
    return load_canonical_map()


@pytest.fixture(scope="module")
def knobs() -> tuple[int, int, int]:
    return validity.resolve_roster_knobs(_FOUR)


def _game_lines(seed: int) -> list[str]:
    return (
        (_FOUR / f"replay-seed-{seed}.jsonl").read_text(encoding="utf-8").splitlines()
    )


def _write_game(tmp_path: Path, seed: int, lines: list[str]) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / f"replay-seed-{seed}.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _seeds() -> list[int]:
    return sorted(
        int(path.stem.rsplit("-", 1)[1]) for path in _FOUR.glob("replay-seed-*.jsonl")
    )


def _meeting_game() -> tuple[int, list[str], list[int]]:
    """First committed 4p1i game with a meeting row: (seed, lines, row indexes)."""

    for seed in _seeds():
        lines = _game_lines(seed)
        indexes = [
            i for i, line in enumerate(lines) if json.loads(line)["kind"] == "meeting"
        ]
        if indexes:
            return seed, lines, indexes
    pytest.fail("no committed 4p1i sample game carries a meeting row")


def _ejected_meeting_game() -> tuple[int, list[str], int]:
    """First committed 4p1i game with an EJECTED meeting: (seed, lines, index)."""

    for seed in _seeds():
        lines = _game_lines(seed)
        for i, line in enumerate(lines):
            row = json.loads(line)
            if row["kind"] == "meeting" and row["outcome"] == "EJECTED":
                return seed, lines, i
    pytest.fail("no committed 4p1i sample game carries an EJECTED meeting")


def _flip_first_tick_hash(lines: list[str]) -> list[str]:
    row = json.loads(lines[0])
    assert row["kind"] == "tick"
    recorded = row["state_hash"]
    row["state_hash"] = ("0" if recorded[0] != "0" else "f") + recorded[1:]
    return [json.dumps(row), *lines[1:]]


def _drop_meeting_row(lines: list[str], index: int) -> list[str]:
    return [line for i, line in enumerate(lines) if i != index]


def _roles(
    seed: int, knobs: tuple[int, int, int], game_map: Map
) -> dict[PlayerId, Role]:
    num_players, num_impostors, tasks_per_crewmate = knobs
    per_seed = validity.roles_by_seed(
        _FOUR,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    return dict(per_seed[seed])


class _Violation(Exception):
    """The test profiles' violation carrier."""

    def __init__(self, violation: WalkViolation) -> None:
        super().__init__(violation.kind)
        self.violation = violation


def _raise_violation(violation: WalkViolation) -> NoReturn:
    raise _Violation(violation)


def _drain(
    path: Path,
    *,
    seed: int,
    knobs: tuple[int, int, int],
    game_map: Map,
    config: ReplayWalkConfig,
) -> list[ReplayWalkEvent]:
    num_players, num_impostors, tasks_per_crewmate = knobs
    return list(
        walk_replay(
            path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
            config=config,
        )
    )


# --------------------------------------------------------------------------- #
# Mechanics — the typed event stream.                                          #
# --------------------------------------------------------------------------- #


def test_event_stream_shape_and_termination(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """TickOpened/TickAdvanced pair per walked row; meetings pair Opened/Applied;
    the stream ends with one WalkComplete carrying the terminal tick + row."""

    seed, lines, meeting_indexes = _meeting_game()
    path = _write_game(tmp_path, seed, lines)
    config = ReplayWalkConfig(
        profile="test-strict",
        on_violation=_raise_violation,
        verify_tick_hashes=True,
        reject_duplicate_meeting_rows=True,
        missing_meeting_row="violation",
        verify_meeting_pre_hashes=True,
        verify_meeting_post_hashes=True,
        require_terminal_tick=True,
        reject_trailing_rows=True,
        require_game_end_row=True,
    )
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=config)

    assert isinstance(events[0], TickOpened)
    assert isinstance(events[-1], WalkComplete)
    opened = [event for event in events if isinstance(event, TickOpened)]
    advanced = [event for event in events if isinstance(event, TickAdvanced)]
    assert len(opened) == len(advanced)
    assert [event.entry.tick for event in opened] == [
        event.entry.tick for event in advanced
    ]
    meetings_opened = [event for event in events if isinstance(event, MeetingOpened)]
    meetings_applied = [event for event in events if isinstance(event, MeetingApplied)]
    assert len(meetings_opened) == len(meetings_applied) == len(meeting_indexes)
    for before, after in zip(meetings_opened, meetings_applied):
        assert before.entry is after.entry
        assert before.trigger is not None
    complete = events[-1]
    assert complete.game_end is not None
    assert complete.terminal_tick == advanced[-1].entry.tick
    assert complete.state.phase == "GAME_OVER"
    # The advance really advanced: pre-state is the previous post-state.
    assert advanced[0].pre_state is opened[0].state


def test_last_events_threading_matches_live_loop(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """TickOpened.last_events is the prior tick's events — or, across a meeting,
    the pre-meeting play events plus the meeting's post-events (the exact
    ``HeadlessGame._run_loop`` contract the leak/funnel packet folds rely on)."""

    seed, lines, _ = _meeting_game()
    path = _write_game(tmp_path, seed, lines)
    config = ReplayWalkConfig(profile="test-open", on_violation=_raise_violation)
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=config)

    expected: tuple[object, ...] = ()
    checked_across_meeting = False
    for event in events:
        if isinstance(event, TickOpened):
            assert event.last_events == expected
        elif isinstance(event, TickAdvanced):
            expected = event.events
        elif isinstance(event, MeetingApplied):
            expected = tuple(expected) + event.post_events
            checked_across_meeting = True
    assert checked_across_meeting


def test_on_violation_must_raise(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """A profile hook that returns is a bug the walker refuses to paper over."""

    seed = _seeds()[0]
    path = _write_game(tmp_path, seed, _flip_first_tick_hash(_game_lines(seed)))

    def _returns(violation: WalkViolation) -> None:
        return None

    config = ReplayWalkConfig(
        profile="test-broken-hook",
        on_violation=cast(Callable[[WalkViolation], NoReturn], _returns),
        verify_tick_hashes=True,
    )
    with pytest.raises(RuntimeError, match="returned instead of raising"):
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=config)


# --------------------------------------------------------------------------- #
# Mechanics — every check is an OPTION (fires when declared, silent when not).  #
# --------------------------------------------------------------------------- #


def test_tick_hash_check_is_an_option(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed = _seeds()[0]
    path = _write_game(tmp_path, seed, _flip_first_tick_hash(_game_lines(seed)))

    on = ReplayWalkConfig(
        profile="test-on", on_violation=_raise_violation, verify_tick_hashes=True
    )
    with pytest.raises(_Violation) as info:
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert info.value.violation.kind == "tick_hash_mismatch"
    assert info.value.violation.tick == 0
    assert info.value.violation.expected != info.value.violation.actual

    off = ReplayWalkConfig(profile="test-off", on_violation=_raise_violation)
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off)
    assert isinstance(events[-1], WalkComplete)


def test_missing_meeting_row_policy_truncates_or_violates(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed, lines, meeting_indexes = _meeting_game()
    path = _write_game(tmp_path, seed, _drop_meeting_row(lines, meeting_indexes[0]))

    truncate = ReplayWalkConfig(
        profile="test-truncate",
        on_violation=_raise_violation,
        verify_tick_hashes=True,
        missing_meeting_row="truncate",
    )
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=truncate)
    complete = events[-1]
    assert isinstance(complete, WalkComplete)
    assert complete.state.phase == "MEETING"  # stopped where the timeline stops
    assert complete.terminal_tick is None

    violate = ReplayWalkConfig(
        profile="test-violate",
        on_violation=_raise_violation,
        verify_tick_hashes=True,
        missing_meeting_row="violation",
    )
    with pytest.raises(_Violation) as info:
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=violate)
    assert info.value.violation.kind == "missing_meeting_row"


def test_duplicate_meeting_rows_check_is_an_option(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed, lines, meeting_indexes = _meeting_game()
    index = meeting_indexes[0]
    doubled = [*lines[: index + 1], lines[index], *lines[index + 1 :]]
    path = _write_game(tmp_path, seed, doubled)

    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        reject_duplicate_meeting_rows=True,
    )
    with pytest.raises(_Violation) as info:
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert info.value.violation.kind == "duplicate_meeting_rows"

    off = ReplayWalkConfig(profile="test-off", on_violation=_raise_violation)
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off)
    assert isinstance(events[-1], WalkComplete)  # collapsed silently, as before


def test_retired_lever_stamp_check_is_an_option(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """A stamp naming a graduated lever OFF describes a substrate this build
    cannot reproduce; only the profiles that ask for the check see it."""

    seed = _seeds()[0]
    lines = _game_lines(seed)
    retired = next(
        key
        for key in json.loads(lines[-1])["substrate_flags"]
        if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
    )
    stamped_off: list[str] = []
    for line in lines:
        row = json.loads(line)
        if row["kind"] == "game_over":
            row["substrate_flags"][retired] = False
            stamped_off.append(json.dumps(row))
        else:
            stamped_off.append(line)
    path = _write_game(tmp_path, seed, stamped_off)

    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        reject_retired_levers_stamped_off=True,
    )
    with pytest.raises(_Violation) as info:
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert info.value.violation.kind == "retired_levers_stamped_off"
    assert info.value.violation.levers == (retired,)

    off = ReplayWalkConfig(profile="test-off", on_violation=_raise_violation)
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off)
    assert isinstance(events[-1], WalkComplete)  # walked clean, as before

    # A live toggle recorded the other way is a substrate this build can still
    # reach, so the retired-half filter must let it through.
    toggled: list[str] = []
    for line in lines:
        row = json.loads(line)
        if row["kind"] == "game_over":
            key = TOGGLEABLE_SUBSTRATE_FLAG_KEYS[0]
            row["substrate_flags"][key] = not row["substrate_flags"][key]
            toggled.append(json.dumps(row))
        else:
            toggled.append(line)
    toggled_path = _write_game(tmp_path / "toggled", seed, toggled)
    events = _drain(toggled_path, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert isinstance(events[-1], WalkComplete)


def test_funnel_profile_bites_a_retired_lever_stamped_off(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """The shared funnel/VJ profile refuses earlier-substrate bytes by name."""

    seed = _seeds()[0]
    lines = _game_lines(seed)
    retired = next(
        key
        for key in json.loads(lines[-1])["substrate_flags"]
        if key not in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
    )
    rewritten: list[str] = []
    for line in lines:
        row = json.loads(line)
        if row["kind"] == "game_over":
            row["substrate_flags"][retired] = False
            rewritten.append(json.dumps(row))
        else:
            rewritten.append(line)
    path = _write_game(tmp_path, seed, rewritten)
    num_players, num_impostors, tasks_per_crewmate = knobs
    with pytest.raises(funnel.FunnelReconstructionError, match=retired):
        _drain(
            path,
            seed=seed,
            knobs=(num_players, num_impostors, tasks_per_crewmate),
            game_map=game_map,
            config=funnel._WALK_CONFIG,
        )


def test_meeting_pre_and_post_hash_checks_are_options(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed, lines, meeting_indexes = _meeting_game()
    index = meeting_indexes[0]

    for field, kind in (
        ("state_hash_before", "meeting_pre_hash_mismatch"),
        ("state_hash_after", "meeting_post_hash_mismatch"),
    ):
        row = json.loads(lines[index])
        row[field] = "0" * len(row[field])
        path = _write_game(
            tmp_path, seed, [*lines[:index], json.dumps(row), *lines[index + 1 :]]
        )
        on = ReplayWalkConfig(
            profile="test-on",
            on_violation=_raise_violation,
            verify_tick_hashes=True,
            verify_meeting_pre_hashes=True,
            verify_meeting_post_hashes=True,
        )
        with pytest.raises(_Violation) as info:
            _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)
        assert info.value.violation.kind == kind

        off = ReplayWalkConfig(profile="test-off", on_violation=_raise_violation)
        events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off)
        assert isinstance(events[-1], WalkComplete)


def test_ballot_tally_check_is_an_option(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed, lines, index = _ejected_meeting_game()
    row = json.loads(lines[index])
    row["ballots"] = []  # empty ballots tally to SKIPPED, not the recorded ejection
    path = _write_game(
        tmp_path, seed, [*lines[:index], json.dumps(row), *lines[index + 1 :]]
    )

    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        ballot_tally_threshold=SKIP_SUSPICION_THRESHOLD,
    )
    with pytest.raises(_Violation) as info:
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert info.value.violation.kind == "ballot_tally_mismatch"

    off = ReplayWalkConfig(profile="test-off", on_violation=_raise_violation)
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off)
    assert isinstance(events[-1], WalkComplete)  # hashes still verify, as before


def test_post_walk_completeness_checks_are_options(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed = _seeds()[0]
    lines = _game_lines(seed)
    rows = [json.loads(line) for line in lines]

    # Truncated mid-play: no terminal tick.
    truncated = _write_game(tmp_path / "truncated", seed, lines[:1])
    on = ReplayWalkConfig(
        profile="test-on", on_violation=_raise_violation, require_terminal_tick=True
    )
    with pytest.raises(_Violation) as info:
        _drain(truncated, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert info.value.violation.kind == "missing_terminal_tick"
    assert info.value.violation.phase is not None

    # game_over row deleted: both the row requirement and the reconstructed-
    # outcome requirement fire (the latter is watchability's combined check).
    no_game_end_lines = [
        line for line in lines if json.loads(line)["kind"] != "game_over"
    ]
    no_game_end = _write_game(tmp_path / "no-game-end", seed, no_game_end_lines)
    for config, kind in (
        (
            ReplayWalkConfig(
                profile="test-on",
                on_violation=_raise_violation,
                require_game_end_row=True,
            ),
            "missing_game_end_row",
        ),
        (
            ReplayWalkConfig(
                profile="test-on",
                on_violation=_raise_violation,
                require_reconstructed_outcome=True,
            ),
            "missing_reconstructed_outcome",
        ),
    ):
        with pytest.raises(_Violation) as info:
            _drain(
                no_game_end, seed=seed, knobs=knobs, game_map=game_map, config=config
            )
        assert info.value.violation.kind == kind

    # A fabricated row after the terminal tick.
    terminal_tick = next(r["tick"] for r in rows if r["kind"] == "game_over")
    trailing_row = dict(next(r for r in rows if r["kind"] == "tick"))
    trailing_row["tick"] = terminal_tick + 100
    trailing = _write_game(
        tmp_path / "trailing", seed, [*lines, json.dumps(trailing_row)]
    )
    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        require_terminal_tick=True,
        reject_trailing_rows=True,
    )
    with pytest.raises(_Violation) as info:
        _drain(trailing, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert info.value.violation.kind == "trailing_replay_rows"
    assert info.value.violation.terminal_tick == terminal_tick

    # A forged game_over winner (the hash chain does not cover it).
    forged_lines: list[str] = []
    for line in lines:
        row = json.loads(line)
        if row["kind"] == "game_over":
            row["winner"] = "IMPOSTORS" if row["winner"] == "CREWMATES" else "CREWMATES"
            forged_lines.append(json.dumps(row))
        else:
            forged_lines.append(line)
    forged = _write_game(tmp_path / "forged", seed, forged_lines)
    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        verify_recorded_outcome=True,
    )
    with pytest.raises(_Violation) as info:
        _drain(forged, seed=seed, knobs=knobs, game_map=game_map, config=on)
    assert info.value.violation.kind == "recorded_outcome_mismatch"

    # And with no post-walk option declared, every one of these files walks
    # to completion — no check is core-mandatory.
    for path in (truncated, no_game_end, trailing, forged):
        off = ReplayWalkConfig(profile="test-off", on_violation=_raise_violation)
        events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off)
        assert isinstance(events[-1], WalkComplete)


# --------------------------------------------------------------------------- #
# Per-profile negative fixtures — each consumer's semantics are UNCHANGED.      #
# These call the CONSUMER walks, so they pin behavior across the migration.     #
# --------------------------------------------------------------------------- #


def test_validity_gate_profile_tolerates_partial_meeting(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """validity DELIBERATELY serves a partial-meeting replay (truncation)."""

    seed, lines, meeting_indexes = _meeting_game()
    path = _write_game(tmp_path, seed, _drop_meeting_row(lines, meeting_indexes[0]))
    num_players, num_impostors, tasks_per_crewmate = knobs
    reconstruction = validity._reconstruct_game(
        path,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        roles=_roles(seed, knobs, game_map),
        game_map=game_map,
    )
    assert reconstruction.seed == seed  # returned, not raised


def test_validity_gate_profile_bites_tampered_hash(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed = _seeds()[0]
    path = _write_game(tmp_path, seed, _flip_first_tick_hash(_game_lines(seed)))
    num_players, num_impostors, tasks_per_crewmate = knobs
    with pytest.raises(ValueError, match="validity-gate reconstruction diverged"):
        validity._reconstruct_game(
            path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=_roles(seed, knobs, game_map),
            game_map=game_map,
        )


def test_win_condition_profile_tolerates_partial_meeting(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed, lines, meeting_indexes = _meeting_game()
    path = _write_game(tmp_path, seed, _drop_meeting_row(lines, meeting_indexes[0]))
    num_players, num_impostors, tasks_per_crewmate = knobs
    check = win_condition_selfcheck.check_replay_win_condition(
        path,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    assert check.seed == seed  # returned, not raised


def test_win_condition_profile_bites_tampered_hash(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed = _seeds()[0]
    path = _write_game(tmp_path, seed, _flip_first_tick_hash(_game_lines(seed)))
    num_players, num_impostors, tasks_per_crewmate = knobs
    with pytest.raises(
        ValueError, match="win-condition self-check reconstruction diverged"
    ):
        win_condition_selfcheck.check_replay_win_condition(
            path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
        )


def test_kill_gift_profile_tolerates_partial_meeting(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed, lines, meeting_indexes = _meeting_game()
    path = _write_game(tmp_path, seed, _drop_meeting_row(lines, meeting_indexes[0]))
    _, _, tasks_per_crewmate = knobs
    facts = balance_eval._kill_gift_accounting(
        path,
        seed=seed,
        roles=_roles(seed, knobs, game_map),
        tasks_per_crewmate=tasks_per_crewmate,
        game_map=game_map,
    )
    assert facts.kill_gifted is False  # returned, not raised


def test_kill_gift_profile_bites_tampered_hash(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed = _seeds()[0]
    path = _write_game(tmp_path, seed, _flip_first_tick_hash(_game_lines(seed)))
    _, _, tasks_per_crewmate = knobs
    with pytest.raises(
        ValueError, match="kill-gift accounting reconstruction diverged"
    ):
        balance_eval._kill_gift_accounting(
            path,
            seed=seed,
            roles=_roles(seed, knobs, game_map),
            tasks_per_crewmate=tasks_per_crewmate,
            game_map=game_map,
        )


def test_watchability_profile_bites_untallying_ballots(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """The referee's DISTINCTIVE check: ballots must tally to the recorded
    outcome (the hash chain does not cover ballots)."""

    seed, lines, index = _ejected_meeting_game()
    row = json.loads(lines[index])
    row["ballots"] = []
    path = _write_game(
        tmp_path, seed, [*lines[:index], json.dumps(row), *lines[index + 1 :]]
    )
    num_players, num_impostors, tasks_per_crewmate = knobs
    with pytest.raises(watchability._IntegrityBreach):
        watchability._reconstruct_game_kills(
            path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=_roles(seed, knobs, game_map),
            game_map=game_map,
        )


def test_watchability_profile_bites_forged_outcome(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """The referee's other distinctive check: the recorded game_over label must
    match the reconstructed terminal event."""

    seed = _seeds()[0]
    forged_lines: list[str] = []
    for line in _game_lines(seed):
        row = json.loads(line)
        if row["kind"] == "game_over":
            row["winner"] = "IMPOSTORS" if row["winner"] == "CREWMATES" else "CREWMATES"
            forged_lines.append(json.dumps(row))
        else:
            forged_lines.append(line)
    path = _write_game(tmp_path, seed, forged_lines)
    num_players, num_impostors, tasks_per_crewmate = knobs
    with pytest.raises(watchability._IntegrityBreach):
        watchability._reconstruct_game_kills(
            path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=_roles(seed, knobs, game_map),
            game_map=game_map,
        )


def test_kill_craft_profile_bites_partial_meeting(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """kill-craft fails a partial-meeting replay LOUD (validity tolerates it)."""

    seed, lines, meeting_indexes = _meeting_game()
    path = _write_game(tmp_path, seed, _drop_meeting_row(lines, meeting_indexes[0]))
    num_players, num_impostors, tasks_per_crewmate = knobs
    with pytest.raises(kill_craft.KillCraftReconstructionError, match="no meeting row"):
        kill_craft._walk_game(
            path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=_roles(seed, knobs, game_map),
            game_map=game_map,
        )


def test_funnel_profile_bites_partial_meeting(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """funnel's deliberate divergence from the loader: an instrument must never
    silently under-count, so the missing meeting row raises."""

    seed, lines, meeting_indexes = _meeting_game()
    path = _write_game(tmp_path, seed, _drop_meeting_row(lines, meeting_indexes[0]))
    num_players, num_impostors, tasks_per_crewmate = knobs
    with pytest.raises(funnel.FunnelReconstructionError, match="no meeting row"):
        funnel._walk_game(
            path,
            seed=seed,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            roles=_roles(seed, knobs, game_map),
            game_map=game_map,
        )


def test_leak_scan_profile_tolerates_tampered_hash(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """The factory walk performs NO hash verification — deliberately (it scans
    replays the harness itself just recorded); a mandatory check would change
    what it accepts."""

    seed, lines, _ = _meeting_game()
    num_players, num_impostors, tasks_per_crewmate = knobs

    baseline = leak_scan._reconstruct_factory_records(
        _write_game(tmp_path / "clean", seed, lines),
        game_map=game_map,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        audit_dir=tmp_path / "clean",
    )
    tampered = leak_scan._reconstruct_factory_records(
        _write_game(tmp_path / "tampered", seed, _flip_first_tick_hash(lines)),
        game_map=game_map,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        audit_dir=tmp_path / "tampered",
    )
    assert len(baseline) > 0
    assert [packet.model_dump() for packet, _ in tampered] == [
        packet.model_dump() for packet, _ in baseline
    ]


def test_leak_scan_profile_tolerates_doubled_meeting_row(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """No doubled-record detection either: the tick-keyed lookup collapses the
    duplicate silently, exactly as before the migration."""

    seed, lines, meeting_indexes = _meeting_game()
    index = meeting_indexes[0]
    doubled = [*lines[: index + 1], lines[index], *lines[index + 1 :]]
    num_players, num_impostors, tasks_per_crewmate = knobs

    baseline = leak_scan._reconstruct_factory_records(
        _write_game(tmp_path / "clean", seed, lines),
        game_map=game_map,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        audit_dir=tmp_path / "clean",
    )
    collapsed = leak_scan._reconstruct_factory_records(
        _write_game(tmp_path / "doubled", seed, doubled),
        game_map=game_map,
        seed=seed,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        audit_dir=tmp_path / "doubled",
    )
    assert [packet.model_dump() for packet, _ in collapsed] == [
        packet.model_dump() for packet, _ in baseline
    ]


# --------------------------------------------------------------------------- #
# verify_action_dispositions — the check that makes a recorded row trustworthy. #
# --------------------------------------------------------------------------- #


def _dispositions_by_tick(
    path: Path, *, seed: int, knobs: tuple[int, int, int], game_map: Map
) -> dict[int, tuple[str, ...]]:
    """The TRUE disposition tuple for each tick row, from the engine's own events."""

    off = ReplayWalkConfig(profile="test-derive", on_violation=_raise_violation)
    derived: dict[int, tuple[str, ...]] = {}
    for event in _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off):
        if not isinstance(event, TickAdvanced):
            continue
        actions = [
            _ACTION_ADAPTER.validate_python(dict(raw)) for raw in event.entry.actions
        ]
        derived[event.entry.tick] = classify_action_dispositions(actions, event.events)
    return derived


def _game_with_a_discarded_action(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> tuple[int, list[str], int]:
    """A committed 4p1i game whose truthful dispositions include a discard.

    Returns ``(seed, lines_carrying_true_dispositions, tick_of_a_discard)``.
    """

    for seed in _seeds():
        lines = _game_lines(seed)
        path = _write_game(tmp_path / f"derive-{seed}", seed, lines)
        derived = _dispositions_by_tick(path, seed=seed, knobs=knobs, game_map=game_map)
        discard_tick = next(
            (
                tick
                for tick, tuple_ in sorted(derived.items())
                if "discarded_by_meeting" in tuple_
            ),
            None,
        )
        if discard_tick is None:
            continue
        stamped: list[str] = []
        for line in lines:
            row = json.loads(line)
            if row["kind"] == "tick" and row["tick"] in derived:
                row["action_dispositions"] = list(derived[row["tick"]])
            stamped.append(json.dumps(row))
        return seed, stamped, discard_tick
    pytest.fail("no committed 4p1i sample game discards an action behind a meeting")


def _relabel_discards_as_applied(lines: list[str], tick: int) -> list[str]:
    """The plant: one tick's discarded actions claim they were carried out."""

    doctored: list[str] = []
    for line in lines:
        row = json.loads(line)
        if row["kind"] == "tick" and row["tick"] == tick:
            row["action_dispositions"] = [
                "applied" if value == "discarded_by_meeting" else value
                for value in row["action_dispositions"]
            ]
        doctored.append(json.dumps(row))
    return doctored


def test_action_disposition_check_bites_a_doctored_tuple(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """The planted case: a discarded action relabelled ``applied`` is caught.

    The tick hash cannot see this class — a discarded action was never applied,
    so the doctored row still reconstructs byte-identically. Both checks run
    here, and only the disposition one fires.
    """

    seed, stamped, discard_tick = _game_with_a_discarded_action(
        tmp_path, knobs, game_map
    )
    path = _write_game(
        tmp_path / "doctored", seed, _relabel_discards_as_applied(stamped, discard_tick)
    )

    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        verify_tick_hashes=True,
        verify_action_dispositions=True,
    )
    with pytest.raises(_Violation) as info:
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)

    assert info.value.violation.kind == "action_disposition_mismatch"
    assert info.value.violation.tick == discard_tick
    # ``expected`` is what the doctored row CLAIMS, ``actual`` what the engine did.
    assert "discarded_by_meeting" not in cast(str, info.value.violation.expected)
    assert "discarded_by_meeting" in cast(str, info.value.violation.actual)


def test_action_disposition_check_passes_a_truthful_recording(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    seed, stamped, _discard_tick = _game_with_a_discarded_action(
        tmp_path, knobs, game_map
    )
    path = _write_game(tmp_path / "truthful", seed, stamped)

    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        verify_tick_hashes=True,
        verify_action_dispositions=True,
    )
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)

    assert isinstance(events[-1], WalkComplete)


def test_a_row_without_dispositions_is_skipped_not_failed(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """An absent field is not a claim, so the check has nothing to disagree with.

    This is what lets the option be turned on over the committed corpus, which
    carries no dispositions at all.
    """

    seed, _lines, _discard_tick = _game_with_a_discarded_action(
        tmp_path, knobs, game_map
    )
    path = _write_game(tmp_path / "committed-shape", seed, _game_lines(seed))

    on = ReplayWalkConfig(
        profile="test-on",
        on_violation=_raise_violation,
        verify_tick_hashes=True,
        verify_action_dispositions=True,
    )
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=on)

    assert isinstance(events[-1], WalkComplete)


def test_action_disposition_check_is_an_option(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """OFF, the same doctored bytes walk clean — no check is core-mandatory."""

    seed, stamped, discard_tick = _game_with_a_discarded_action(
        tmp_path, knobs, game_map
    )
    path = _write_game(
        tmp_path / "doctored-off",
        seed,
        _relabel_discards_as_applied(stamped, discard_tick),
    )

    off = ReplayWalkConfig(
        profile="test-off", on_violation=_raise_violation, verify_tick_hashes=True
    )
    events = _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=off)

    assert isinstance(events[-1], WalkComplete)


# --------------------------------------------------------------------------- #
# The decided trigger (Task 21.6): the shape the baseline-8 record captured,    #
# and the hash refusals around it.                                              #
# --------------------------------------------------------------------------- #

_NEW_SHAPE_KNOBS = (4, 1, 1)

_PRODUCTION_PROFILES: tuple[ReplayWalkConfig, ...] = (
    validity._WALK_CONFIG,
    win_condition_selfcheck._WALK_CONFIG,
    balance_eval._KILL_GIFT_WALK_CONFIG,
    watchability._REFEREE_WALK_CONFIG,
    kill_craft._WALK_CONFIG,
    solvability._WALK_CONFIG,
    evidence_honesty._WALK_CONFIG,
    funnel._WALK_CONFIG,
    leak_scan._FACTORY_WALK_CONFIG,
)


def _wait(actor: str) -> Action:
    return _ACTION_ADAPTER.validate_python(
        {"actor": actor, "type": "wait", "payload": {}}
    )


def _kill(actor: str, target: str) -> Action:
    return _ACTION_ADAPTER.validate_python(
        {"actor": actor, "type": "kill", "payload": {"target": target}}
    )


def _report(actor: str, body_id: str) -> Action:
    return _ACTION_ADAPTER.validate_python(
        {"actor": actor, "type": "report", "payload": {"body_id": body_id}}
    )


def _write_decided_trigger_game(directory: Path, *, seed: int = 0) -> Path:
    """Record a 4p1i game whose meeting trigger decides it — the 21.15 shape.

    The impostor's second kill reaches parity on the tick a survivor reports the
    first body, and a wait ordered behind that report is dropped, so the row
    carries a ``discarded_by_meeting`` disposition on a concluded tick. Driven
    through ``advance_tick`` and ``ReplayLog`` so every hash is one the engine
    actually produced.
    """

    game_map = load_canonical_map()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"replay-seed-{seed}.jsonl"
    state = seed_initial_state(
        seed=seed, game_map=game_map, num_players=4, num_impostors=1
    )
    impostor = next(p.id for p in state.players.values() if p.role == "IMPOSTOR")
    first_victim, second_victim, reporter = sorted(
        p.id for p in state.players.values() if p.role == "CREWMATE"
    )

    log = ReplayLog(path=path, game_id=f"headless-seed-{seed}")
    body_id: str | None = None
    while state.phase == "PLAY":
        alive = sorted(pid for pid, p in state.players.items() if p.alive)
        off_cooldown = state.cooldowns.get(impostor, 0) == 0
        if off_cooldown and body_id is None:
            actions = [_wait(pid) for pid in alive if pid != impostor]
            actions.append(_kill(impostor, first_victim))
        elif off_cooldown and body_id is not None:
            actions = [
                _kill(impostor, second_victim),
                _report(reporter, body_id),
                _wait(second_victim),
            ]
        else:
            actions = [_wait(pid) for pid in alive]

        input_tick = state.tick
        state, events = advance_tick(state, actions, game_map=game_map)
        log.record_tick(input_tick, actions, state, events=events)
        if body_id is None and any(event.type == "Killed" for event in events):
            body_id = f"body-{first_victim}-{input_tick}"
        if state.phase == "GAME_OVER":
            over = next(event for event in events if isinstance(event, GameOverEvent))
            log.record_game_end(winner=over.winner, reason=over.reason, tick=input_tick)
            return path
    pytest.fail("the decided-trigger fixture never reached GAME_OVER")


def _tick_row_index(lines: list[str], tick: int) -> int:
    for index, line in enumerate(lines):
        row = json.loads(line)
        if row["kind"] == "tick" and row["tick"] == tick:
            return index
    pytest.fail(f"no tick row at {tick}")


def test_a_hash_that_diverges_for_another_reason_still_violates(
    tmp_path: Path, knobs: tuple[int, int, int], game_map: Map
) -> None:
    """Plant (a): an ordinary meeting trigger with a flipped hash still fails."""

    seed, lines, meeting_indexes = _meeting_game()
    trigger_tick = json.loads(lines[meeting_indexes[0]])["tick"]
    index = _tick_row_index(lines, trigger_tick)
    row = json.loads(lines[index])
    recorded = row["state_hash"]
    row["state_hash"] = ("0" if recorded[0] != "0" else "f") + recorded[1:]
    path = _write_game(
        tmp_path, seed, [*lines[:index], json.dumps(row), *lines[index + 1 :]]
    )
    config = ReplayWalkConfig(
        profile="test-on", on_violation=_raise_violation, verify_tick_hashes=True
    )

    with pytest.raises(_Violation) as info:
        _drain(path, seed=seed, knobs=knobs, game_map=game_map, config=config)
    assert info.value.violation.kind == "tick_hash_mismatch"
    assert info.value.violation.tick == trigger_tick


def test_a_decided_trigger_ends_the_walk_at_game_over(
    tmp_path: Path, game_map: Map
) -> None:
    """The shape the corrected engine records: GAME_OVER, and no meeting row.

    A tick whose state already satisfies a win condition concludes there, so the
    walk ends at GAME_OVER on the trigger tick and opens no meeting. This needs
    no allowance and no restore — the inverse that used to reconstruct the
    pre-ruling pair retired at the baseline-8 record, once the census over all
    four re-recorded sets read zero decided meeting-trigger ticks.
    """

    config = ReplayWalkConfig(
        profile="test-on", on_violation=_raise_violation, verify_tick_hashes=True
    )
    new_shape = _write_decided_trigger_game(tmp_path / "new-shape")

    events = _drain(
        new_shape, seed=0, knobs=_NEW_SHAPE_KNOBS, game_map=game_map, config=config
    )

    complete = events[-1]
    assert isinstance(complete, WalkComplete)
    assert complete.state.phase == "GAME_OVER"
    assert not [event for event in events if isinstance(event, MeetingOpened)]


@pytest.mark.parametrize(
    "config", _PRODUCTION_PROFILES, ids=[c.profile for c in _PRODUCTION_PROFILES]
)
def test_the_new_shape_walks_clean_under_every_profile(
    tmp_path: Path, game_map: Map, config: ReplayWalkConfig
) -> None:
    """The recording Task 21.15 will produce loads in all nine named profiles.

    The six that treat a missing meeting row as a violation are never reached:
    the walk breaks at GAME_OVER on the trigger tick first.
    """

    path = _write_decided_trigger_game(tmp_path / "new-shape")
    events = _drain(
        path, seed=0, knobs=_NEW_SHAPE_KNOBS, game_map=game_map, config=config
    )

    complete = events[-1]
    assert isinstance(complete, WalkComplete)
    assert complete.state.phase == "GAME_OVER"
    assert complete.game_end is not None
    assert complete.terminal_tick is not None


def test_the_new_shape_carries_a_verified_disposition_tuple(
    tmp_path: Path, game_map: Map
) -> None:
    """The concluded tick's row labels the action behind the report discarded."""

    path = _write_decided_trigger_game(tmp_path / "new-shape")
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if json.loads(line)["kind"] == "tick"
    ]
    assert rows[-1]["action_dispositions"][-1] == "discarded_by_meeting"

    config = ReplayWalkConfig(
        profile="test-dispositions",
        on_violation=_raise_violation,
        verify_tick_hashes=True,
        verify_action_dispositions=True,
    )
    events = _drain(
        path, seed=0, knobs=_NEW_SHAPE_KNOBS, game_map=game_map, config=config
    )
    assert isinstance(events[-1], WalkComplete)


def test_the_new_shape_serves_through_the_replay_loader(tmp_path: Path) -> None:
    """The spectator serves the concluded trigger tick with no meeting to link."""

    set_dir = tmp_path / "new-shape"
    _write_decided_trigger_game(set_dir)
    replay = ReplayLoader(replay_dir=set_dir).load_replay("headless-seed-0")

    assert replay.meetings == ()
    assert replay.finale is not None
    assert (replay.finale.winner, replay.finale.winner_reason) == (
        "IMPOSTORS",
        "IMPOSTOR_PARITY",
    )
    final = replay.ticks[-1]
    kinds = [event.type for event in final.events]
    assert "kill" in kinds and "report_body" in kinds
    # No meeting convened, so no meeting_triggered chip points at a missing id.
    assert "meeting_triggered" not in kinds


def test_a_set_carrying_the_new_shape_passes_the_validity_gate(
    tmp_path: Path,
) -> None:
    """The gate Task 21.15 runs on every recorded leg accepts the new shape.

    Two hermetic meeting-bearing games ride along because the gate's meeting-rate
    and cost floors are population properties a lone no-meeting game cannot meet;
    the subject is the decided-trigger recording beside them.
    """

    set_dir = tmp_path / "gate-set"
    _write_decided_trigger_game(set_dir, seed=0)
    for seed in (1, 2):
        HeadlessGame(
            seed=seed,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=set_dir / f"replay-seed-{seed}.jsonl",
            audit_log_path=Path(os.devnull),
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
            scheduler=TickScheduler(max_ticks=300),
        ).run()

    report = validity.run_validity_gate(set_dir)

    failed = [check.name for check in report.checks if not check.passed]
    assert failed == []
    assert report.passed
