"""Tests for the potential-based reward channel (Task 15.8).

Pins: the shaping is potential-based (it TELESCOPES to Φ(terminal) − Φ(initial)
over any episode, so it cannot change the optimal policy — Ng et al. 1999); the
channel REFUSES to score a truncated / incomplete episode as a full game; and the
side-specific tactically-reachable terms are read from the typed event log.
"""

from __future__ import annotations

import pytest

from training.env import TacticalRolloutEnv
from training.rewards import (
    PotentialShaper,
    ShapedReward,
    TruncatedEpisodeError,
    compute_shaped_reward,
    side_specific_terms,
)
from training.rollout import (
    BehavioralDescriptors,
    EpisodeRollout,
)

_NUM_PLAYERS = 9
_NUM_IMPOSTORS = 2
_TASKS = 2


def _env(**overrides: object) -> TacticalRolloutEnv:
    kwargs: dict[str, object] = {
        "num_players": _NUM_PLAYERS,
        "num_impostors": _NUM_IMPOSTORS,
        "tasks_per_crewmate": _TASKS,
    }
    kwargs.update(overrides)
    return TacticalRolloutEnv(**kwargs)  # type: ignore[arg-type]


def _empty_descriptors() -> BehavioralDescriptors:
    return BehavioralDescriptors(
        kill_ticks=(),
        witness_exposure_rate=0.0,
        vent_usage=0,
        meeting_count=0,
        meeting_trigger_rate=0.0,
        do_task_emissions=0,
        do_task_cadence=0.0,
        win_shape="IMPOSTORS",
    )


def _rollout(*, truncated: bool, winner: str | None) -> EpisodeRollout:
    """A minimal hand-built rollout for the truncation-guard unit tests."""

    return EpisodeRollout(
        seed=0,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS,
        episode_boundary="first_meeting" if truncated else "full_game",
        truncated=truncated,
        outcome="FIRST_MEETING" if truncated else "IMPOSTORS",
        winner=winner,  # type: ignore[arg-type]
        win_reason=None if winner is None else "IMPOSTOR_PARITY",
        final_tick=0,
        roles={"p0": "IMPOSTOR"},
        frames=(),
        events=(),
        meetings=(),
        descriptors=_empty_descriptors(),
    )


# --------------------------------------------------------------------------- #
# Potential-based shaping telescopes (policy invariance)                       #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("side", ["IMPOSTOR", "CREWMATE"])
def test_shaping_telescopes_to_phi_terminal_minus_initial(seed: int, side: str) -> None:
    rollout = _env().rollout(seed)
    shaper = PotentialShaper(side=side, gamma=1.0)  # type: ignore[arg-type]
    phi = shaper.potentials(rollout)
    assert phi.shape[0] == len(rollout.frames)
    # The Ng-1999 identity: with gamma == 1 the shaping sum equals the endpoint
    # potential difference for ANY episode, so shaping cannot change the optimum.
    expected = float(phi[-1] - phi[0]) if phi.shape[0] else 0.0
    assert shaper.shaping_sum(rollout) == pytest.approx(expected)


def test_shaping_series_is_the_potential_difference() -> None:
    rollout = _env().rollout(2)
    shaper = PotentialShaper(side="IMPOSTOR", gamma=1.0)
    phi = shaper.potentials(rollout)
    series = shaper.shaping_series(rollout)
    assert series.shape[0] == max(0, phi.shape[0] - 1)
    for index, term in enumerate(series):
        assert term == pytest.approx(float(phi[index + 1] - phi[index]))


def test_discounted_shaping_does_not_telescope_to_endpoints() -> None:
    # A sanity check that gamma is actually wired: at gamma != 1 the sum is the
    # discounted form, NOT the plain endpoint difference (unless Φ is flat).
    rollout = _env().rollout(0)
    shaper = PotentialShaper(side="IMPOSTOR", gamma=0.9)
    phi = shaper.potentials(rollout)
    endpoint = float(phi[-1] - phi[0]) if phi.shape[0] else 0.0
    if phi.shape[0] >= 2 and float(phi[-1]) != float(phi[0]):
        assert shaper.shaping_sum(rollout) != pytest.approx(endpoint)


# --------------------------------------------------------------------------- #
# The channel refuses to score a truncated / incomplete episode                #
# --------------------------------------------------------------------------- #


def test_reward_refuses_truncated_episode() -> None:
    truncated = _rollout(truncated=True, winner=None)
    assert not truncated.complete
    for side in ("IMPOSTOR", "CREWMATE"):
        with pytest.raises(TruncatedEpisodeError):
            compute_shaped_reward(truncated, side)


def test_reward_refuses_tick_budget_episode_without_winner() -> None:
    incomplete = _rollout(truncated=True, winner=None)
    with pytest.raises(TruncatedEpisodeError):
        compute_shaped_reward(incomplete, "IMPOSTOR")


def test_reward_scores_a_complete_episode() -> None:
    complete = _rollout(truncated=False, winner="IMPOSTORS")
    assert complete.complete
    reward = compute_shaped_reward(complete, "IMPOSTOR")
    assert isinstance(reward, ShapedReward)
    assert reward.terminal_reward == 1.0  # impostor won
    crew_reward = compute_shaped_reward(complete, "CREWMATE")
    assert crew_reward.terminal_reward == -1.0  # crew lost


# --------------------------------------------------------------------------- #
# Side-specific tactically-reachable terms from the typed event log            #
# --------------------------------------------------------------------------- #


def test_impostor_terms_read_the_typed_event_log() -> None:
    rollout = _env().rollout(0)
    terms = side_specific_terms(rollout, "IMPOSTOR")
    assert set(terms) == {"kills", "unwitnessed_kills", "survival", "meetings_survived"}
    # kills matches the descriptor's kill count (both from the typed KilledEvents).
    assert terms["kills"] == float(rollout.descriptors.kill_count)
    assert 0.0 <= terms["unwitnessed_kills"] <= terms["kills"]
    assert 0.0 <= terms["survival"] <= 1.0


def test_crew_terms_read_the_typed_state() -> None:
    rollout = _env().rollout(0)
    terms = side_specific_terms(rollout, "CREWMATE")
    assert set(terms) == {
        "task_progress",
        "survival",
        "correct_reports",
        "report_coverage",
    }
    assert 0.0 <= terms["task_progress"] <= 1.0
    assert 0.0 <= terms["survival"] <= 1.0
    assert terms["correct_reports"] >= 0.0


def test_shaped_reward_total_combines_terminal_dense_and_shaping() -> None:
    complete = _rollout(truncated=False, winner="IMPOSTORS")
    reward = compute_shaped_reward(complete, "IMPOSTOR")
    dense = sum(reward.dense_terms.values())
    assert reward.total() == pytest.approx(
        reward.terminal_reward + dense + reward.shaping_sum
    )
