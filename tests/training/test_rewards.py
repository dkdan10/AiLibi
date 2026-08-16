"""Tests for the potential-based reward channel (Task 15.8).

Pins: the shaping TELESCOPES to Φ(terminal) − Φ(initial) over any episode — and
telescoping is ALL these tests prove (Task 19.4). Ng-1999 policy invariance would
additionally require Φ(terminal) to be trajectory-INdependent (canonically Φ = 0 at
the absorbing state); here Φ is a CUMULATIVE count (impostor: kills; crew: completed
tasks) starting at 0, so the shaping sum EQUALS the episode's terminal kill /
completed-task count — a real +1-per-kill (+1-per-task) incentive on the return, NOT
policy-invariant. Also pinned: the channel REFUSES to score a truncated / incomplete
episode as a full game; and the side-specific tactically-reachable terms are read
from the typed event log.
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
    *,
    tasks_completed: int,
    alive_crew: int,
    alive_impostors: int,
    cumulative_kills: int = 0,
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
        cumulative_kills=cumulative_kills,
    )


def _play_frame(*, shadowing: bool) -> EpisodeFrame:
    return EpisodeFrame(
        tick=1,
        kind="tick",
        phase="PLAY",
        state_hash="0" * 64,
        tasks_completed=0,
        tasks_total=1,
        alive_crew=1,
        alive_impostors=1,
        cumulative_kills=0,
        crew_shadowing_impostor=shadowing,
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
        episode_boundary="full_game",
        truncated=truncated,
        # The EpisodeRollout invariant requires outcome == winner for a completed
        # episode, so the outcome tracks the winner when not truncated. A
        # truncated full-game episode is the tick-budget cap (Task 19.19 retired
        # the first_meeting boundary, the only other truncation source).
        outcome="TICK_BUDGET" if truncated else winner,  # type: ignore[arg-type]
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


def _kill_count_rollout(terminal_kills: int) -> EpisodeRollout:
    """A complete impostor-win rollout whose ONLY free variable is Φ(terminal).

    Everything the ENVIRONMENT reward reads is fixed: the winner (the ±1 terminal),
    the roster, the empty event log and meeting log, and the last frame's
    ``alive_impostors`` / task scalars — i.e. every input to the impostor dense
    terms. Only ``cumulative_kills`` at the terminal frame varies, so two of these
    differ in environment reward by exactly nothing and in Φ(terminal) by
    ``terminal_kills``. Two frames, so one shaping transition exists (Task 19.4).

    Synthetic by construction: a REAL ``terminal_kills=2`` episode would also carry
    two ``KilledEvent``s and so move the dense ``kills`` term with it. The reward
    channel's domain is the typed :class:`EpisodeRollout` — exactly what this
    exercises — and the seed-0 value pin corroborates the same +1-per-kill identity
    on a real engine rollout (``shaping_sum == dense kills == 5.0``)."""

    return _make_rollout(
        truncated=False,
        winner="IMPOSTORS",
        roles={"p0": "IMPOSTOR", "c1": "CREWMATE"},
        events=(),
        meetings=(),
        frames=(
            _frame(
                tasks_completed=0, alive_crew=1, alive_impostors=1, cumulative_kills=0
            ),
            _frame(
                tasks_completed=0,
                alive_crew=1,
                alive_impostors=1,
                cumulative_kills=terminal_kills,
            ),
        ),
    )


# --------------------------------------------------------------------------- #
# Potential-based shaping telescopes (telescoping ONLY — not invariance)       #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("side", ["IMPOSTOR", "CREWMATE"])
def test_shaping_telescopes_to_phi_terminal_minus_initial(seed: int, side: str) -> None:
    rollout = _env().rollout(seed)
    shaper = PotentialShaper(side=side, gamma=1.0)  # type: ignore[arg-type]
    phi = shaper.potentials(rollout)
    assert phi.shape[0] == len(rollout.frames)
    # The telescoping identity: with gamma == 1 the shaping sum equals the endpoint
    # potential difference for ANY episode. That identity — and NOTHING more — is
    # what this pins (Task 19.4): Ng-1999 invariance would also need Φ(terminal) to
    # be trajectory-INdependent, and a cumulative count is not (see
    # ``test_shaping_is_not_policy_invariant_across_equal_env_reward_episodes``).
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
# ...but telescoping is NOT policy invariance (Task 19.4)                      #
# --------------------------------------------------------------------------- #


def test_shaping_is_not_policy_invariant_across_equal_env_reward_episodes() -> None:
    """The shaping is a real +1-per-kill incentive (Task 19.4).

    Ng-1999 policy invariance needs MORE than telescoping: it needs Φ(terminal) to
    be trajectory-INdependent (canonically Φ = 0 at the absorbing state). Φ here is
    a cumulative kill count opening at 0, so the γ=1 shaping sum IS the episode's
    terminal kill count. Two trajectories carrying IDENTICAL environment reward —
    same sparse terminal, same dense terms — therefore receive DIFFERENT shaped
    returns, ranked by kills, which is exactly what an invariant transform may not
    do (audits/audit-phase-19-triage.md §7 item 4; §8 row 2 VERIFIED). The finding
    is DOCUMENTED, not repaired: the ML program is frozen and this pins the real
    behavior rather than changing it."""

    quiet = compute_shaped_reward(_kill_count_rollout(0), "IMPOSTOR")
    lethal = compute_shaped_reward(_kill_count_rollout(2), "IMPOSTOR")

    # The environment reward is identical on both channels: sparse and dense.
    assert quiet.terminal_reward == 1.0
    assert lethal.terminal_reward == 1.0
    assert quiet.dense_terms == lethal.dense_terms

    # The shaping is not: each side's sum is exactly its terminal kill count, so
    # the "invariant" term prices kills at +1 apiece.
    assert quiet.shaping_sum == 0.0
    assert lethal.shaping_sum == 2.0
    assert quiet.shaping_sum != lethal.shaping_sum

    # ...and the scalar an optimizer maximizes differs by exactly the kill delta.
    assert lethal.total() - quiet.total() == 2.0


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


def test_reward_rejects_unknown_side() -> None:
    """A side from config/CLI — especially the PLURAL winner literal — must fail
    loud rather than silently fall through to the crew branch."""

    complete = _rollout(truncated=False, winner="IMPOSTORS")
    for bad in ("IMPOSTORS", "CREWMATES", "crew", "impostor", ""):
        with pytest.raises(ValueError, match="unknown reward side"):
            compute_shaped_reward(complete, bad)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="unknown reward side"):
            side_specific_terms(complete, bad)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="unknown reward side"):
            PotentialShaper(side=bad)  # type: ignore[arg-type]


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
        "patrol_coverage",
    }
    assert 0.0 <= terms["task_progress"] <= 1.0
    assert 0.0 <= terms["survival"] <= 1.0
    assert terms["correct_reports"] >= 0.0
    assert 0.0 <= terms["patrol_coverage"] <= 1.0


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


def test_correct_reports_count_only_crew_triggered_body_reports() -> None:
    """``correct_reports`` credits only a crewmate-routed body report that ejected
    an impostor — never an emergency or an impostor-triggered report."""

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
            # A crew body-report that ejected an impostor: counts.
            _meeting(trigger="report", triggered_by="c1", ejected="p0"),
            # A crew body-report that ejected a crewmate: no credit.
            _meeting(trigger="report", triggered_by="c2", ejected="c1"),
            # An impostor-triggered body report that ejected an impostor: no credit.
            _meeting(trigger="report", triggered_by="p1", ejected="p1"),
            # An emergency meeting that ejected an impostor: no credit.
            _meeting(trigger="emergency", triggered_by="c1", ejected="p1"),
        ),
        frames=(_frame(tasks_completed=1, alive_crew=1, alive_impostors=0),),
    )
    terms = side_specific_terms(rollout, "CREWMATE")
    assert terms["correct_reports"] == 1.0  # only the crew report that got an impostor


def test_patrol_coverage_rewards_shadowing_without_a_report() -> None:
    """``patrol_coverage`` is the fraction of PLAY ticks a crewmate shadowed a
    live impostor — rewarding buddy/patrol play with no body report at all."""

    roles: dict[str, Role] = {"p0": "IMPOSTOR", "c1": "CREWMATE"}
    frames = (
        _play_frame(shadowing=True),
        _play_frame(shadowing=False),
        _play_frame(shadowing=True),
        _play_frame(shadowing=True),
    )
    rollout = _make_rollout(
        truncated=False, winner="CREWMATES", roles=roles, frames=frames
    )
    terms = side_specific_terms(rollout, "CREWMATE")
    assert terms["patrol_coverage"] == pytest.approx(3 / 4)  # 3 of 4 PLAY ticks
    # No meetings at all, so shadowing alone produces the coverage signal.
    assert terms["correct_reports"] == 0.0


# --------------------------------------------------------------------------- #
# Frozen-ML value pin: not one computed number moved (Task 19.4)               #
# --------------------------------------------------------------------------- #


def test_shaped_reward_values_on_seed_zero_are_byte_identical() -> None:
    """Every computed value of the reward channel, pinned EXACTLY (Task 19.4).

    Task 19.4 corrects the false policy-invariance PROSE and adds tests — nothing
    else: the ML program is frozen, no retraining happens, and no computed value
    may move. These literals are seed 0's shaped reward at the pre-19.4 HEAD, read
    off the deterministic engine, so the guard is the diff-proof that the docstring
    correction was prose-only. They are exact IEEE doubles from a byte-deterministic
    rollout, so they are compared with ``==`` — never ``pytest.approx``, which would
    let a real drift in Φ, the dense terms, or the weighting slip through."""

    rollout = _env().rollout(0)

    impostor = compute_shaped_reward(rollout, "IMPOSTOR")
    assert impostor.terminal_reward == 1.0
    assert impostor.dense_terms == {
        "kills": 5.0,
        "unwitnessed_kills": 3.0,
        "survival": 1.0,
        "meetings_survived": 4.0,
    }
    assert impostor.shaping_sum == 5.0
    assert impostor.potential_initial == 0.0
    assert impostor.potential_terminal == 5.0
    assert impostor.total() == 19.0

    crew = compute_shaped_reward(rollout, "CREWMATE")
    assert crew.terminal_reward == -1.0
    assert crew.dense_terms == {
        "task_progress": 0.8571428571428571,
        "survival": 0.2857142857142857,
        "correct_reports": 0.0,
        "patrol_coverage": 0.782608695652174,
    }
    assert crew.shaping_sum == 12.0
    assert crew.potential_initial == 0.0
    assert crew.potential_terminal == 12.0
    assert crew.total() == 12.925465838509316
