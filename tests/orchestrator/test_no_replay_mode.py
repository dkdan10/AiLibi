"""Tests for the no-replay training mode + RNG fast-path guards (Task 15.8.1).

``HeadlessGame`` gains an explicit NO-REPLAY training mode (``replay_path=None``)
that writes NOTHING to disk and is the ONLY construction that accepts the opt-in
:attr:`~engine.rng.RngStateHashPolicy.TRAINING_FAST` fast path. These tests pin
the contract the definition of done spells out:

* a no-replay game constructs, runs to completion, and leaves nothing on disk;
* every replay-WRITING construction refuses the fast path (fail loud, not a
  silent downgrade);
* a no-replay construction that receives a Task-15.9 ``tactical_policy_stamp``
  raises (a stamp with nothing to record it is a caller bug);
* the recorded and no-replay paths are trajectory-identical — the same seed
  yields the same per-tick actions and the same winner — and the fast rng path
  differs only in the (skipped) rng-state serialization.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.rng import RngStateHashPolicy
from engine.world import load_canonical_map
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    HeadlessGame,
    UnrecordedGameResult,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    _serialize_actions,
    fsm_default_tactical_policy_stamp,
    read_game_outcome,
    read_replay_entries,
)
from orchestrator.scheduler import TickScheduler

_NUM_PLAYERS = 9
_NUM_IMPOSTORS = 2
_TASKS = 2


def _runner() -> object:
    # A fresh runner per game (runners carry per-game recording/budget state);
    # the fake provider keeps the run $0 / offline / deterministic.
    return build_default_meeting_runner(llm_client=FakeProvider())


def _game(
    *,
    seed: int,
    replay_path: Path | None,
    rng_hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
) -> HeadlessGame:
    return HeadlessGame(
        seed=seed,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=replay_path,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS,
        scheduler=TickScheduler(max_ticks=1000),
        meeting_runner=_runner(),  # type: ignore[arg-type]
        rng_hash_policy=rng_hash_policy,
    )


def test_no_replay_game_writes_nothing_and_runs_to_completion(
    tmp_path: Path,
) -> None:
    # The game is pointed at an empty temp dir via a would-be replay location it
    # must NOT create, and the audit is routed to the null device.
    would_be_replay = tmp_path / "should-not-exist.jsonl"
    game = _game(
        seed=3,
        replay_path=None,
        rng_hash_policy=RngStateHashPolicy.TRAINING_FAST,
    )

    result = game.run_unrecorded()

    assert isinstance(result, UnrecordedGameResult)
    assert result.outcome in ("CREWMATES", "IMPOSTORS", "TICK_BUDGET_REACHED")
    assert result.final_state.phase in ("GAME_OVER", "PLAY")
    assert result.tick_steps  # the game actually ran ticks
    # Nothing was written to disk.
    assert not would_be_replay.exists()
    assert list(tmp_path.iterdir()) == []


def test_run_requires_a_replay_path() -> None:
    game = _game(seed=1, replay_path=None)
    with pytest.raises(ValueError, match="run_unrecorded"):
        game.run()


def test_run_unrecorded_requires_no_replay_path(tmp_path: Path) -> None:
    game = _game(seed=1, replay_path=tmp_path / "replay.jsonl")
    with pytest.raises(ValueError, match="requires replay_path=None"):
        game.run_unrecorded()


def test_replay_writing_construction_refuses_the_fast_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="fast path"):
        HeadlessGame(
            seed=1,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=tmp_path / "replay.jsonl",
            meeting_runner=_runner(),  # type: ignore[arg-type]
            rng_hash_policy=RngStateHashPolicy.TRAINING_FAST,
        )


def test_no_replay_construction_refuses_an_explicit_audit_log_path(
    tmp_path: Path,
) -> None:
    # An explicit audit_log_path would leave an ObservationAuditLog JSONL on disk,
    # contradicting the "nothing on disk" no-replay contract -- refuse it loudly.
    with pytest.raises(ValueError, match="audit_log_path is refused|writes NOTHING"):
        HeadlessGame(
            seed=1,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=None,
            audit_log_path=tmp_path / "audit.jsonl",
            meeting_runner=_runner(),  # type: ignore[arg-type]
        )


def test_no_replay_construction_refuses_a_tactical_policy_stamp() -> None:
    with pytest.raises(ValueError, match="tactical_policy_stamp|nothing to attribute"):
        HeadlessGame(
            seed=1,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=None,
            meeting_runner=_runner(),  # type: ignore[arg-type]
            tactical_policy_stamp=fsm_default_tactical_policy_stamp(),
        )


def test_fast_path_is_accepted_only_with_no_replay() -> None:
    # The one legal construction of the fast path: replay_path=None (no stamp).
    game = _game(
        seed=5,
        replay_path=None,
        rng_hash_policy=RngStateHashPolicy.TRAINING_FAST,
    )
    result = game.run_unrecorded()
    assert result.tick_steps


@pytest.mark.parametrize("seed", [1, 2, 7])
def test_recorded_and_no_replay_paths_are_trajectory_identical(
    seed: int, tmp_path: Path
) -> None:
    replay_path = tmp_path / f"replay-{seed}.jsonl"
    recorded = _game(seed=seed, replay_path=replay_path).run()
    entries = read_replay_entries(replay_path)
    recorded_winner = read_game_outcome(replay_path)

    unrecorded = _game(seed=seed, replay_path=None).run_unrecorded()

    # Same per-tick submitted actions...
    assert [entry.tick for entry in entries] == [
        step.input_tick for step in unrecorded.tick_steps
    ]
    for entry, step in zip(entries, unrecorded.tick_steps, strict=True):
        assert list(entry.actions) == _serialize_actions(list(step.actions))
    # ...and the same terminal outcome.
    assert recorded.outcome == unrecorded.outcome
    assert recorded_winner == recorded.outcome


@pytest.mark.parametrize("seed", [1, 2, 7])
def test_fast_and_full_no_replay_traces_are_event_identical(seed: int) -> None:
    full = _game(
        seed=seed, replay_path=None, rng_hash_policy=RngStateHashPolicy.FULL
    ).run_unrecorded()
    fast = _game(
        seed=seed,
        replay_path=None,
        rng_hash_policy=RngStateHashPolicy.TRAINING_FAST,
    ).run_unrecorded()

    assert full.outcome == fast.outcome
    assert [s.events for s in full.tick_steps] == [s.events for s in fast.tick_steps]
    assert [s.actions for s in full.tick_steps] == [s.actions for s in fast.tick_steps]
    assert [m.result for m in full.meeting_steps] == [
        m.result for m in fast.meeting_steps
    ]
