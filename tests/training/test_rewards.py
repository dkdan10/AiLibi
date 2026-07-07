"""Tests for the potential-based reward channel (Task 15.8).

Pins: the shaping is potential-based (it TELESCOPES to Φ(terminal) − Φ(initial)
over any episode, so it cannot change the optimal policy — Ng et al. 1999); the
channel REFUSES to score a truncated / incomplete episode as a full game; and the
side-specific tactically-reachable terms are read from the typed event log.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest

from engine.entities import Role
from engine.events import EngineEvent, KilledEvent
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
    EpisodeFrame,
    EpisodeRollout,
    MeetingRecord,
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

    return _make_rollout(
        truncated=truncated,
        winner=winner,
        roles={"p0": "IMPOSTOR"},
    )


def _frame(
    *, tasks_completed: int, alive_crew: int, alive_impostors: int
) -> EpisodeFrame:
    return EpisodeFrame(
        tick=1,
        kind="tick",
        phase="GAME_OVER",
        state_hash="0" * 64,
        tasks_completed=tasks_completed,
        tasks_total=max(1, tasks_completed),
        alive_crew=alive_crew,
        alive_impostors=alive_impostors,
        cumulative_kills=0,
    )


def _make_rollout(
    *,
    truncated: bool,
    winner: str | None,
    roles: Mapping[str, Role],
    events: Sequence[EngineEvent] = (),
    meetings: Sequence[MeetingRecord] = (),
    frames: Sequence[EpisodeFrame] = (),
) -> EpisodeRollout:
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
        final_tick=1,
        roles=roles,
        frames=tuple(frames),
        events=tuple(events),
        meetings=tuple(meetings),
        descriptors=_empty_descriptors(),
    )


def _kill(actor: str, target: str, witnesses: tuple[str, ...]) -> KilledEvent:
    return KilledEvent(
        type="Killed",
        tick=3,
        actor=actor,
        target=target,
        room="CAFETERIA",
        witnesses=witnesses,
    )


def _meeting(*, trigger: str, triggered_by: str, ejected: str | None) -> MeetingRecord:
    return MeetingRecord(
        tick=4,
        meeting_id="m",
        trigger=trigger,  # type: ignore[arg-type]
        triggered_by=triggered_by,
        outcome="EJECTED" if ejected is not None else "SKIPPED",
        ejected_player_id=ejected,
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


# --------------------------------------------------------------------------- #
# Reward scoping: teammate witnesses + crew-only report credit                 #
# --------------------------------------------------------------------------- #


def test_impostor_unwitnessed_kills_ignore_teammate_witnesses() -> None:
    """A kill seen only by a fellow impostor produced no crew evidence, so it
    counts as un-witnessed — not withheld from stealth credit."""

    roles: dict[str, Role] = {
        "p0": "IMPOSTOR",
        "p1": "IMPOSTOR",
        "p2": "CREWMATE",
        "p3": "CREWMATE",
    }
    rollout = _make_rollout(
        truncated=False,
        winner="IMPOSTORS",
        roles=roles,
        events=(
            _kill("p0", "p2", ("p1",)),  # teammate-only witness -> un-witnessed
            _kill("p0", "p3", ("p1", "p3b")),  # no real crew witness id -> un-witnessed
            _kill("p1", "p2", ("p3",)),  # a crew witness -> witnessed
        ),
        frames=(_frame(tasks_completed=0, alive_crew=0, alive_impostors=2),),
    )
    terms = side_specific_terms(rollout, "IMPOSTOR")
    assert terms["kills"] == 3.0
    # Only the third kill has a crew witness (p3), so two are crew-un-witnessed.
    assert terms["unwitnessed_kills"] == 2.0


def test_crew_reports_count_only_crew_triggered_body_reports() -> None:
    """``correct_reports`` / ``report_coverage`` credit only meetings a crewmate
    routed via a body report — never an emergency or an impostor-triggered one."""

    roles: dict[str, Role] = {
        "p0": "IMPOSTOR",
        "p1": "IMPOSTOR",
        "c1": "CREWMATE",
        "c2": "CREWMATE",
    }
    rollout = _make_rollout(
        truncated=False,
        winner="CREWMATES",
        roles=roles,
        meetings=(
            # A crew body-report that ejected an impostor: counts for both.
            _meeting(trigger="report", triggered_by="c1", ejected="p0"),
            # A crew body-report that ejected a crewmate: coverage only.
            _meeting(trigger="report", triggered_by="c2", ejected="c1"),
            # An impostor-triggered body report that ejected an impostor: neither.
            _meeting(trigger="report", triggered_by="p1", ejected="p1"),
            # An emergency meeting that ejected an impostor: neither.
            _meeting(trigger="emergency", triggered_by="c1", ejected="p1"),
        ),
        frames=(_frame(tasks_completed=1, alive_crew=1, alive_impostors=0),),
    )
    terms = side_specific_terms(rollout, "CREWMATE")
    assert terms["report_coverage"] == 2.0  # the two crew body-reports
    assert terms["correct_reports"] == 1.0  # only the crew report that got an impostor
