"""Tests for the potential-based reward channel (Task 15.8).

Pins: the shaping TELESCOPES to Φ(terminal) − Φ(initial) over any episode — and
telescoping is ALL these tests prove (Task 19.4). Ng-1999 policy invariance would
additionally require Φ(terminal) to be trajectory-INdependent (canonically Φ = 0 at
the absorbing state); here Φ is a CUMULATIVE count over the side's win total
(impostor: kills over the initial crew; crew: completed tasks over the task total)
starting at 0, so the shaping sum EQUALS the episode's terminal progress SHARE — a
real, bounded per-kill (per-task) incentive on the return, NOT policy-invariant.

Also pinned: every dense term and the shaping land in [0, 1], so the derived
terminal weight ranks every reachable WIN above every reachable LOSS; the channel
REFUSES to score a truncated / incomplete episode as a full game; and the
side-specific tactically-reachable terms are read from the typed event log.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence

import pytest

from engine.entities import Role
from engine.events import EngineEvent, KilledEvent
from training import rewards as rewards_module
from training.env import TacticalRolloutEnv
from training.rewards import (
    DEFAULT_OBJECTIVE_WEIGHTS,
    DENSE_TERM_NAMES,
    ObjectiveWeights,
    PotentialShaper,
    ShapedReward,
    TruncatedEpisodeError,
    bounded_term_count,
    compute_shaped_reward,
    derive_terminal_weight,
    potential_scale,
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
    two ``KilledEvent``s and so move the stealth-share term with it. The reward
    channel's domain is the typed :class:`EpisodeRollout` — exactly what this
    exercises — and the seed-0 value pin corroborates the same per-kill identity on
    a real engine rollout (``shaping_sum == 5/7``, its 5 kills over 7 crew)."""

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
    """Telescoping survives the per-episode scale, EXACTLY.

    ``scale`` is one constant for the whole episode, so it factors straight through
    ``Φ(terminal) − Φ(initial)``. Compared with ``==``, never ``approx``: an
    approximate comparison would hide a scale applied per-frame rather than
    per-episode, which is the one way bounding Φ could break the identity.
    """

    rollout = _env().rollout(seed)
    shaper = PotentialShaper(
        side=side,  # type: ignore[arg-type]
        scale=potential_scale(rollout, side),  # type: ignore[arg-type]
        gamma=1.0,
    )
    phi = shaper.potentials(rollout)
    assert phi.shape[0] == len(rollout.frames)
    # The telescoping identity: with gamma == 1 the shaping sum equals the endpoint
    # potential difference for ANY episode. That identity — and NOTHING more — is
    # what this pins (Task 19.4): Ng-1999 invariance would also need Φ(terminal) to
    # be trajectory-INdependent, and a cumulative count is not (see
    # ``test_shaping_is_not_policy_invariant_across_equal_env_reward_episodes``).
    expected = float(phi[-1] - phi[0]) if phi.shape[0] else 0.0
    assert shaper.shaping_sum(rollout) == expected
    # ...and the bounded half: Φ is a fraction of the side's win total, so the whole
    # episode's shaping pays that win condition at most once.
    assert 0.0 <= shaper.shaping_sum(rollout) <= 1.0
    assert all(0.0 <= float(value) <= 1.0 for value in phi)


def test_potential_scale_is_the_sides_win_total() -> None:
    """The scale is the side's win condition, read off the episode's own numbers."""

    rollout = _env().rollout(0)
    assert potential_scale(rollout, "IMPOSTOR") == float(
        rollout.num_players - rollout.num_impostors
    )
    assert potential_scale(rollout, "CREWMATE") == float(rollout.frames[-1].tasks_total)


def test_potential_shaper_requires_a_positive_scale() -> None:
    """No default and no zero: a shaper without the episode's scale computes a
    different Φ than ``compute_shaped_reward`` and would rot the sum identity
    ``experiments/lab/torch_probe`` asserts (which mypy does not read)."""

    for bad in (0.0, -1.0):
        with pytest.raises(ValueError, match="finite positive"):
            PotentialShaper(side="IMPOSTOR", scale=bad)


def test_shaping_series_is_the_potential_difference() -> None:
    rollout = _env().rollout(2)
    shaper = PotentialShaper(
        side="IMPOSTOR", scale=potential_scale(rollout, "IMPOSTOR"), gamma=1.0
    )
    phi = shaper.potentials(rollout)
    series = shaper.shaping_series(rollout)
    assert series.shape[0] == max(0, phi.shape[0] - 1)
    for index, term in enumerate(series):
        assert term == pytest.approx(float(phi[index + 1] - phi[index]))


def test_discounted_shaping_does_not_telescope_to_endpoints() -> None:
    # A sanity check that gamma is actually wired: at gamma != 1 the sum is the
    # discounted form, NOT the plain endpoint difference (unless Φ is flat).
    rollout = _env().rollout(0)
    shaper = PotentialShaper(
        side="IMPOSTOR", scale=potential_scale(rollout, "IMPOSTOR"), gamma=0.9
    )
    phi = shaper.potentials(rollout)
    endpoint = float(phi[-1] - phi[0]) if phi.shape[0] else 0.0
    if phi.shape[0] >= 2 and float(phi[-1]) != float(phi[0]):
        assert shaper.shaping_sum(rollout) != pytest.approx(endpoint)


# --------------------------------------------------------------------------- #
# ...but telescoping is NOT policy invariance (Task 19.4)                      #
# --------------------------------------------------------------------------- #


def test_shaping_is_not_policy_invariant_across_equal_env_reward_episodes() -> None:
    """The shaping is a real per-kill incentive, bounded but not removed (19.4).

    Ng-1999 policy invariance needs MORE than telescoping: it needs Φ(terminal) to
    be trajectory-INdependent (canonically Φ = 0 at the absorbing state). Φ here is
    a cumulative kill count over the initial crew, opening at 0, so the γ=1 shaping
    sum IS the episode's terminal kill SHARE. Two trajectories carrying IDENTICAL
    environment reward — same sparse terminal, same dense terms — therefore still
    receive DIFFERENT shaped returns, ranked by kills, which is exactly what an
    invariant transform may not do (audits/audit-phase-19-triage.md §7 item 4; §8
    row 2 VERIFIED). Bounding Φ shrinks the incentive's magnitude; it does not make
    the transform invariant, so the finding stays DOCUMENTED, not repaired."""

    quiet = compute_shaped_reward(_kill_count_rollout(0), "IMPOSTOR")
    lethal = compute_shaped_reward(_kill_count_rollout(2), "IMPOSTOR")
    # 9 players, 2 impostors -> the shaping denominator is the 7-strong initial crew.
    crew = float(_NUM_PLAYERS - _NUM_IMPOSTORS)

    # The environment reward is identical on both channels: sparse and dense.
    assert quiet.terminal_reward == 1.0
    assert lethal.terminal_reward == 1.0
    assert quiet.dense_terms == lethal.dense_terms

    # The shaping is not: each side's sum is its terminal kill share, so the
    # "invariant" term still prices kills — now at 1/crew apiece.
    assert quiet.shaping_sum == 0.0
    assert lethal.shaping_sum == 2.0 / crew
    assert quiet.shaping_sum != lethal.shaping_sum

    # ...and the scalar an optimizer maximizes differs by exactly the kill delta.
    assert lethal.total() - quiet.total() == pytest.approx(2.0 / crew)


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
            PotentialShaper(side=bad, scale=1.0)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="unknown reward side"):
            potential_scale(complete, bad)  # type: ignore[arg-type]


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
    assert set(terms) == set(DENSE_TERM_NAMES["IMPOSTOR"])
    # Kill VOLUME is not a term: the shaping already pays exactly the kill count,
    # so a raw ``kills`` term would price the same quantity twice.
    assert "kills" not in terms
    # ...but the stealth SHARE of those kills still is, read off the typed events.
    assert 0.0 <= terms["unwitnessed_kills"] <= 1.0
    assert 0.0 <= terms["survival"] <= 1.0
    assert 0.0 <= terms["meetings_survived"] <= 1.0


def test_crew_terms_read_the_typed_state() -> None:
    rollout = _env().rollout(0)
    terms = side_specific_terms(rollout, "CREWMATE")
    assert set(terms) == set(DENSE_TERM_NAMES["CREWMATE"])
    assert 0.0 <= terms["task_progress"] <= 1.0
    assert 0.0 <= terms["survival"] <= 1.0
    assert 0.0 <= terms["correct_reports"] <= 1.0
    assert 0.0 <= terms["patrol_coverage"] <= 1.0


@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("side", ["IMPOSTOR", "CREWMATE"])
def test_every_dense_term_is_a_bounded_share(seed: int, side: str) -> None:
    """Every dense term lands in [0, 1] on real engine rollouts.

    The premise ``derive_terminal_weight`` rests on: an unbounded term would let a
    LOSS outscore a WIN however heavy the terminal weight is.
    """

    rollout = _env().rollout(seed)
    terms = side_specific_terms(rollout, side)  # type: ignore[arg-type]
    assert set(terms) == set(DENSE_TERM_NAMES[side])  # type: ignore[index]
    for name, value in terms.items():
        assert 0.0 <= value <= 1.0, f"{side} term {name} = {value} escapes [0, 1]"


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
    # Only the third of three kills has a crew witness (p3), so the stealth SHARE
    # is 2 of 3 — a share, so more kills no longer buy more stealth credit.
    assert terms["unwitnessed_kills"] == 2.0 / 3.0


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
    # Only the crew report that got an impostor counts — as a SHARE of the two
    # impostors there were to route out.
    assert terms["correct_reports"] == 1.0 / _NUM_IMPOSTORS


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
# Value pin: the seed-0 decomposition, re-derived on the current bytes          #
# --------------------------------------------------------------------------- #


def test_shaped_reward_values_on_seed_zero_are_byte_identical() -> None:
    """Every computed value of the reward channel, pinned EXACTLY.

    These literals are seed 0's shaped reward read off the deterministic engine, so
    they are the diff-proof that a change to Φ, the dense terms or the weighting was
    the intended one. They are exact IEEE doubles from a byte-deterministic rollout,
    so they are compared with ``==`` — never ``pytest.approx``, which would let a
    real drift slip through.

    What the bounded objective changed, side by side. IMPOSTOR: the raw ``kills``
    term (5.0) is gone, ``unwitnessed_kills`` 5.0 -> the 5-of-5 stealth share 1.0,
    ``meetings_survived`` 5.0 -> the 5-of-5 share 1.0, shaping 5.0 -> 5/7, and the
    composed total 22.0 -> 8.714285714285714 under the derived terminal weight 5.0.
    CREW: ``correct_reports`` is a share of the two impostors (0.0 either way),
    shaping 12.0 -> 12/14, and the recorded seed-0 LOSS 12.829131652661065 ->
    −3.3137254901960786 — which is now below every reachable crew WIN (+6.0 at
    worst), the inversion this objective exists to close."""

    rollout = _env().rollout(0)

    impostor = compute_shaped_reward(rollout, "IMPOSTOR")
    assert impostor.terminal_reward == 1.0
    assert impostor.dense_terms == {
        "unwitnessed_kills": 1.0,
        "survival": 1.0,
        "meetings_survived": 1.0,
    }
    assert impostor.shaping_sum == 0.7142857142857143
    assert impostor.potential_initial == 0.0
    assert impostor.potential_terminal == 0.7142857142857143
    assert impostor.total() == 4.714285714285714
    assert _composed(rollout, "IMPOSTOR") == 8.714285714285714  # was 22.0

    crew = compute_shaped_reward(rollout, "CREWMATE")
    assert crew.terminal_reward == -1.0
    assert crew.dense_terms == {
        "task_progress": 0.8571428571428571,
        "survival": 0.2857142857142857,
        "correct_reports": 0.0,
        "patrol_coverage": 0.6862745098039216,
    }
    assert crew.shaping_sum == 0.8571428571428571
    assert crew.potential_initial == 0.0
    assert crew.potential_terminal == 0.8571428571428571
    assert crew.total() == 1.6862745098039214
    # was 12.829131652661065, which outranked every crew WIN with <= 7 tasks.
    assert _composed(rollout, "CREWMATE") == -3.3137254901960786


def _composed(rollout: EpisodeRollout, side: Role) -> float:
    """The side's total under its default objective profile."""

    profile = DEFAULT_OBJECTIVE_WEIGHTS[side]
    return compute_shaped_reward(
        rollout,
        side,
        dense_weight=profile.dense_weight,
        shaping_weight=profile.shaping_weight,
        terminal_weight=profile.terminal_weight,
    ).total()


# --------------------------------------------------------------------------- #
# The ordering invariant: the worst WIN outranks the best LOSS                  #
# --------------------------------------------------------------------------- #


def _declared_term_ceilings(side: Role) -> dict[str, float]:
    """Each dense term's DECLARED ceiling — 1.0, because every term is a share."""

    return {name: 1.0 for name in DENSE_TERM_NAMES[side]}


def _reachable_extremes(
    term_ceilings: Mapping[str, float], profile: ObjectiveWeights
) -> tuple[float, float]:
    """(worst reachable WIN, best reachable LOSS) from the declared term ceilings.

    Derived from the ceilings and the profile, never hand-typed: a worst WIN scores
    every bounded channel at its floor of 0, a best LOSS every one at its ceiling.
    """

    worst_win = profile.terminal_weight * 1.0
    best_loss = (
        profile.terminal_weight * -1.0
        + profile.dense_weight * math.fsum(term_ceilings.values())
        + profile.shaping_weight * 1.0
    )
    return worst_win, best_loss


@pytest.mark.parametrize("side", ["IMPOSTOR", "CREWMATE"])
def test_worst_win_outranks_best_loss(side: str) -> None:
    """The derived terminal weight makes winning dominate, by the derived margin.

    Both ends come from the DECLARED per-term ceilings and the derivation the
    constant itself came from — a hand-typed 5 and 6 would make this tautological.
    """

    profile = DEFAULT_OBJECTIVE_WEIGHTS[side]  # type: ignore[index]
    assert profile.terminal_weight == derive_terminal_weight(side)  # type: ignore[arg-type]
    worst_win, best_loss = _reachable_extremes(
        _declared_term_ceilings(side),  # type: ignore[arg-type]
        profile,
    )
    assert worst_win > best_loss
    # The margin the derivation promises: bounded_term_count + 2.
    assert worst_win - best_loss == bounded_term_count(side) + 2  # type: ignore[arg-type]


@pytest.mark.parametrize("side", ["IMPOSTOR", "CREWMATE"])
def test_ordering_gate_bites_on_an_unbounded_declared_ceiling(side: str) -> None:
    """The planted case, arithmetic half: one term whose ceiling is not 1.

    Re-adds the DELETED raw ``kills`` term at its true ceiling — the roster size, the
    exact shape it had — and the best LOSS overtakes the worst WIN. The derivation is
    only sound while every ceiling is 1.
    """

    profile = DEFAULT_OBJECTIVE_WEIGHTS[side]  # type: ignore[index]
    planted = _declared_term_ceilings(side) | {"kills": float(_NUM_PLAYERS)}  # type: ignore[arg-type]
    worst_win, best_loss = _reachable_extremes(planted, profile)
    assert best_loss > worst_win


def test_ordering_gate_bites_when_a_production_term_regresses_to_a_raw_count(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The planted case, PRODUCTION half: perturb the real term function.

    The arithmetic gate above guards the declared ceilings; this one guards the code
    that has to honour them. It scores a real recorded crew LOSS through
    ``compute_shaped_reward`` (holds today), then regresses ONE crew term to the raw
    count it used to be — and the same recorded LOSS now outranks the worst reachable
    crew WIN. A gate nobody can fail is prose.
    """

    rollout = _env().rollout(0)
    assert rollout.winner != "CREWMATES"  # the recorded seed-0 crew LOSS
    profile = DEFAULT_OBJECTIVE_WEIGHTS["CREWMATE"]
    worst_win, _ = _reachable_extremes(_declared_term_ceilings("CREWMATE"), profile)
    assert _composed(rollout, "CREWMATE") < worst_win

    bounded_terms = rewards_module._crew_terms

    def unbounded(perturbed_rollout: EpisodeRollout) -> dict[str, float]:
        terms = dict(bounded_terms(perturbed_rollout))
        last = perturbed_rollout.frames[-1]
        terms["correct_reports"] = float(last.tasks_completed)  # the raw count again
        return terms

    monkeypatch.setattr(rewards_module, "_crew_terms", unbounded)
    assert _composed(rollout, "CREWMATE") > worst_win


@pytest.mark.parametrize("seed", range(6))
def test_a_real_crew_loss_never_outranks_a_reachable_crew_win(seed: int) -> None:
    """The finding, closed on real bytes: a recorded LOSS scores below any WIN.

    The seed-0 crew LOSS used to score 12.829131652661065 while a crew WIN with 7
    of 14 tasks topped out at 12.500. Now every LOSS sits below the worst reachable
    WIN, whatever the trajectory.
    """

    rollout = _env().rollout(seed)
    profile = DEFAULT_OBJECTIVE_WEIGHTS["CREWMATE"]
    worst_win, _ = _reachable_extremes(_declared_term_ceilings("CREWMATE"), profile)
    composed = _composed(rollout, "CREWMATE")
    if rollout.winner == "CREWMATES":
        assert composed >= worst_win
    else:
        assert composed < worst_win


def test_the_default_objective_registries_are_read_only() -> None:
    """The derived weights and the truncation floor read these at import time, so a
    process-wide mutation would silently desynchronise them."""

    with pytest.raises(TypeError):
        DENSE_TERM_NAMES["IMPOSTOR"] = ()  # type: ignore[index]
    with pytest.raises(TypeError):
        DEFAULT_OBJECTIVE_WEIGHTS["IMPOSTOR"] = ObjectiveWeights()  # type: ignore[index]


def test_potential_shaper_rejects_a_non_finite_scale() -> None:
    """NaN passes ``<= 0`` and poisons every Φ; +inf collapses progress to zero."""

    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError, match="finite positive"):
            PotentialShaper(side="IMPOSTOR", scale=bad)
