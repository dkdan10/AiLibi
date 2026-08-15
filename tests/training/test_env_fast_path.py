"""Tests for the training env's RNG fast-path + no-replay knobs (Task 15.8.1).

``TacticalRolloutEnv`` gains two DEFAULT-OFF knobs: ``no_replay`` (drive each
rollout through :meth:`HeadlessGame.run_unrecorded`, writing nothing to disk and
assembling the episode from the live trajectory) and ``rng_hash_policy`` (the
opt-in :attr:`~engine.rng.RngStateHashPolicy.TRAINING_FAST` fast path). These
tests pin:

* the knobs default OFF, so the env is byte-identical to the 15.8 baseline;
* the fast path is refused unless ``no_replay`` is set (mirroring the
  HeadlessGame guard);
* TRAJECTORY EQUIVALENCE — for a frozen (FSM) policy on a fixed seed set, the
  full action / event streams are IDENTICAL under the recorded default path and
  the no-replay fast path; only the (skipped) rng-state hashing differs;
* a no-replay episode is a scoreable full game, and its shaped reward equals the
  recorded path's.
"""

from __future__ import annotations

import pytest

from engine.rng import RngStateHashPolicy
from training.env import TacticalRolloutEnv
from training.rewards import compute_shaped_reward

_NUM_PLAYERS = 9
_NUM_IMPOSTORS = 2
_TASKS = 2
_SEEDS = (1, 2, 3, 7, 11)


def _env(**overrides: object) -> TacticalRolloutEnv:
    kwargs: dict[str, object] = {
        "num_players": _NUM_PLAYERS,
        "num_impostors": _NUM_IMPOSTORS,
        "tasks_per_crewmate": _TASKS,
    }
    kwargs.update(overrides)
    return TacticalRolloutEnv(**kwargs)  # type: ignore[arg-type]


def test_knobs_default_off() -> None:
    env = _env()
    assert env.no_replay is False
    assert env.rng_hash_policy is RngStateHashPolicy.FULL


def test_fast_path_requires_no_replay() -> None:
    with pytest.raises(ValueError, match="requires no_replay=True"):
        _env(rng_hash_policy=RngStateHashPolicy.TRAINING_FAST)


def test_no_replay_full_rng_is_a_valid_construction() -> None:
    # no_replay without the fast path is legal (full rng, just unrecorded).
    env = _env(no_replay=True)
    assert env.no_replay is True
    assert env.rng_hash_policy is RngStateHashPolicy.FULL
    rollout = env.rollout(1)
    assert rollout.frames  # produced a real episode


@pytest.mark.parametrize("seed", _SEEDS)
def test_trajectory_equivalence_recorded_vs_fast_no_replay(seed: int) -> None:
    recorded = _env().rollout(seed)
    fast = _env(
        no_replay=True, rng_hash_policy=RngStateHashPolicy.TRAINING_FAST
    ).rollout(seed)

    # The full ACTION / EVENT streams are identical under both modes.
    assert recorded.events == fast.events
    assert recorded.meetings == fast.meetings
    assert recorded.descriptors == fast.descriptors
    assert recorded.outcome == fast.outcome
    assert recorded.winner == fast.winner
    assert recorded.final_tick == fast.final_tick

    # Per-frame SCALARS match tick-for-tick; only the state HASH differs (the
    # fast codec vs the committed JSON encoding) -- "only hashing cost differs".
    assert len(recorded.frames) == len(fast.frames)
    for recorded_frame, fast_frame in zip(recorded.frames, fast.frames, strict=True):
        assert recorded_frame.tick == fast_frame.tick
        assert recorded_frame.kind == fast_frame.kind
        assert recorded_frame.phase == fast_frame.phase
        assert recorded_frame.tasks_completed == fast_frame.tasks_completed
        assert recorded_frame.alive_crew == fast_frame.alive_crew
        assert recorded_frame.alive_impostors == fast_frame.alive_impostors
        assert recorded_frame.cumulative_kills == fast_frame.cumulative_kills
        assert (
            recorded_frame.crew_shadowing_impostor == fast_frame.crew_shadowing_impostor
        )


@pytest.mark.parametrize("seed", _SEEDS)
def test_fast_no_replay_frames_skip_the_state_hash(seed: int) -> None:
    # The fast path never verifies these hashes (no replay to verify against), so
    # it skips the per-frame full-WorldState serialization and carries an empty
    # placeholder -- otherwise the fast rollout re-pays the cost it exists to
    # avoid. FULL no-replay keeps a real, reconstruct-comparable hash.
    fast = _env(
        no_replay=True, rng_hash_policy=RngStateHashPolicy.TRAINING_FAST
    ).rollout(seed)
    assert fast.frames
    assert all(frame.state_hash == "" for frame in fast.frames)
    assert all(state_hash == "" for state_hash in fast.state_hashes)

    full = _env(no_replay=True).rollout(seed)
    assert all(frame.state_hash for frame in full.frames)


@pytest.mark.parametrize("seed", _SEEDS)
def test_no_replay_full_matches_recorded_reconstruction_exactly(seed: int) -> None:
    # no_replay with FULL rng must be identical to the recorded reconstruction in
    # EVERY field, including the state-hash chain (same encoding, same states).
    recorded = _env().rollout(seed)
    no_replay = _env(no_replay=True).rollout(seed)

    assert recorded.state_hashes == no_replay.state_hashes
    assert recorded.events == no_replay.events
    assert recorded.descriptors == no_replay.descriptors
    assert recorded.frames == no_replay.frames


@pytest.mark.parametrize("seed", _SEEDS)
def test_fast_no_replay_shaped_reward_matches_recorded(seed: int) -> None:
    recorded = _env().rollout(seed)
    fast = _env(
        no_replay=True, rng_hash_policy=RngStateHashPolicy.TRAINING_FAST
    ).rollout(seed)

    # Both are scoreable full games (unless the seed is a rare tick-budget cap),
    # and the shaped reward is identical because the trajectory is identical.
    if recorded.complete:
        assert fast.complete
        for side in ("IMPOSTOR", "CREWMATE"):
            recorded_reward = compute_shaped_reward(recorded, side)
            fast_reward = compute_shaped_reward(fast, side)
            assert recorded_reward.total() == fast_reward.total()
