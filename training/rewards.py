"""Potential-based reward channel + side-specific reward terms (Task 15.8).

The single typed home for training rewards, so a trainer never re-derives a
reward from replay bytes: it consumes a :class:`training.rollout.EpisodeRollout`
(the typed, reconstructed episode) and this module turns it into a
:class:`ShapedReward`.

Two pieces, per the training-signal doctrine (audit
post-phase-14-ML-training-signal.md §3; DESIGN.md §"balance is a finding"):

1. **Side-specific tactically-reachable terms.** Computed from the typed engine
   event log — impostor: resolved kills, un-witnessed-ness (``KilledEvent.witnesses``
   empty), survival, meetings survived; crew: task progress, survival, correctly-
   routed reports (a meeting that ejected an impostor), report coverage — plus the
   terminal win as a sparse reward. These are the only quantities any optimizer
   maximizes.

2. **Potential-based shaping (the Ng et al. 1999 FORM — NOT policy-invariant
   here).** A per-step shaping term ``F(s_t, s_{t+1}) = γ·Φ(s_{t+1}) − Φ(s_t)``
   over a side-specific potential Φ read from the per-step engine-state scalars
   (:class:`training.rollout.EpisodeFrame`). At ``γ = 1`` the shaping TELESCOPES:
   ``Σ_t F = Φ(terminal) − Φ(initial)`` for ANY episode. Φ is a progress count
   divided by that episode's own win-condition total (:func:`potential_scale` —
   impostor: kills over the initial crew; crew: completed task instances over the
   task total), so Φ ∈ [0, 1] and the shaping pays the side's win condition ONCE
   rather than once per unit of progress. The scale is a per-episode constant, so
   it factors straight through ``Φ(terminal) − Φ(initial)`` and the telescoping
   identity is untouched.

   TELESCOPING IS NOT INVARIANCE. Ng-1999 policy invariance needs one more
   hypothesis this module does not satisfy: a trajectory-INdependent terminal
   potential (canonically ``Φ ≡ 0`` at the absorbing/terminal state, or an
   infinite-horizon discounted setting). Here Φ is a CUMULATIVE count, so
   ``Φ(terminal)`` is trajectory-DEPENDENT: with ``Φ(initial) = 0`` the shaping sum
   EQUALS the episode's terminal progress FRACTION. The shaping is therefore a real
   ``+1/initial_crew``-per-kill (impostor) / ``+1/tasks_total``-per-completed-task
   (crew) incentive added to the return — two episodes with equal environment reward
   and different terminal counts get different shaped returns — and it CAN change
   the optimal policy. The prior claim here ("so it cannot change the optimal
   policy") was mathematically FALSE; the telescoping test pins telescoping only,
   never invariance. Finding + disposition: Task 19.4,
   audits/audit-phase-19-triage.md §7 item 4 (§8 row 2, VERIFIED) — DOCUMENTED, NOT
   REPAIRED; bounding Φ shrinks the incentive's magnitude, it does not remove it.

3. **Weights that rank a win above a loss.** Every dense term and the shaping sit
   in [0, 1], which lets the sparse terminal's weight be DERIVED rather than
   guessed: at :func:`derive_terminal_weight` — one more than the count of bounded
   channels — the worst reachable WIN outranks the best reachable LOSS by
   ``bounded_term_count + 2``. :class:`ObjectiveWeights` is the profile the two
   inner-fitness functions forward, and :data:`FITNESS_OBJECTIVE_ID` names the
   objective a fitness number was produced under, so numbers from two different
   objectives can never be silently compared.

The reward channel REFUSES to score a truncated episode as a full game
(:class:`TruncatedEpisodeError`): :func:`compute_shaped_reward` gates on
:attr:`EpisodeRollout.complete`, so a tick-budget-capped episode can never be
read as a terminal outcome — silent truncation is never a fitness path (Task
15.8 definition of done).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final, TypeAlias, get_args

import numpy as np
from numpy.typing import NDArray

from engine.entities import Role
from engine.events import KilledEvent
from training.rollout import EpisodeFrame, EpisodeRollout, crew_witnesses

# A reward is always scored for one side (Task 15.8): the impostor is the
# primary/deeper track, the crew rides the shared machinery once.
RewardSide: TypeAlias = Role

# The runtime-valid reward sides, derived from the ``Role`` Literal so they never
# drift. Deliberately distinct from the PLURAL winner literals
# (``IMPOSTORS`` / ``CREWMATES``) — a common typo that must not silently score.
_VALID_REWARD_SIDES: frozenset[str] = frozenset(get_args(Role))


def _validate_side(side: str) -> None:
    """Fail loud on an unknown reward side (AGENTS.md no silent fallbacks).

    A side deserialized from config/CLI as a plain string — especially the plural
    winner literal ``"IMPOSTORS"`` — would otherwise fall through the ``side ==
    "IMPOSTOR"`` branch and be scored with CREW dense terms + a loss terminal,
    silently corrupting the selected side's results."""

    if side not in _VALID_REWARD_SIDES:
        raise ValueError(
            f"unknown reward side {side!r}; expected one of "
            f"{sorted(_VALID_REWARD_SIDES)} (the plural winner literals "
            "'IMPOSTORS'/'CREWMATES' are NOT valid sides)"
        )


class TruncatedEpisodeError(ValueError):
    """Raised when a truncated / incomplete episode is scored as a full game.

    The structural guard behind the Task 15.8 invariant "no fitness term ever
    reads a truncated episode as a full game": :func:`compute_shaped_reward`
    raises this rather than returning a terminal reward for a tick-budget-capped
    episode.
    """


def potential_scale(rollout: EpisodeRollout, side: Role) -> float:
    """The side's win total — the episode constant Φ is expressed as a fraction of.

    Impostor: the INITIAL crew count — the kills that end the game. Crew: the
    episode's total task instances. Both are fixed for the whole episode, so
    dividing by one is a per-episode rescale that leaves ``Φ(terminal) −
    Φ(initial)`` proportional and the telescoping identity intact, while capping
    the shaping's contribution at the side's win condition instead of re-paying it
    once per unit of progress. Never zero (``max(1, …)``, the module's existing
    denominator style).
    """

    _validate_side(side)
    if side == "IMPOSTOR":
        return float(max(1, rollout.num_players - rollout.num_impostors))
    last = rollout.frames[-1] if rollout.frames else None
    return float(max(1, last.tasks_total)) if last is not None else 1.0


def _side_potential(side: Role, frame: EpisodeFrame, scale: float) -> float:
    """The side-specific potential Φ at one step, as a fraction of the win total.

    A monotonic count of engine-truth progress toward the side's win — impostor:
    cumulative resolved kills; crew: completed task instances — over the episode's
    :func:`potential_scale`. No float belief state crosses into Φ, so Φ is a
    byte-stable function of the engine's integer scalars (the §7 determinism note)
    and lands in [0, 1].

    Being CUMULATIVE is precisely why the shaping is NOT policy-invariant (Task
    19.4; module docstring item 2): a cumulative count makes ``Φ(terminal)``
    trajectory-DEPENDENT, which is the one hypothesis Ng-1999 invariance requires
    and this Φ does not supply. From ``Φ(initial) = 0`` the γ = 1 shaping sum is the
    terminal progress FRACTION — a real, bounded per-kill / per-task incentive, not
    a wash."""

    if side == "IMPOSTOR":
        return frame.cumulative_kills / scale
    return frame.tasks_completed / scale


class PotentialShaper:
    """Shaping in the Ng-1999 FORM over a side-specific potential Φ.

    ``F(s_t, s_{t+1}) = γ·Φ(s_{t+1}) − Φ(s_t)``. At ``γ = 1`` the per-episode
    shaping sum telescopes to ``Φ(terminal) − Φ(initial)`` — the identity the
    telescoping test pins, and ALL it pins. That is NOT a policy-invariance
    guarantee: Φ is a cumulative count, so ``Φ(terminal)`` is trajectory-dependent
    and the shaping is a real bounded per-kill (impostor) / per-completed-task
    (crew) incentive (Task 19.4; module docstring item 2 carries the finding and its
    documented-not-repaired disposition).

    ``scale`` is REQUIRED and keyword-only: it is the episode's own
    :func:`potential_scale`, and a shaper built with a different one computes a
    different Φ than :func:`compute_shaped_reward` does for the same rollout. A
    default would let a caller's own shaper diverge silently, so there is none.
    numpy carries the per-step vector math (numpy is training-confined by the
    import-linter contract).
    """

    def __init__(self, *, side: Role, scale: float, gamma: float = 1.0) -> None:
        _validate_side(side)
        if scale <= 0.0:
            raise ValueError(
                f"PotentialShaper scale must be positive, got {scale!r}; use "
                "training.rewards.potential_scale(rollout, side)"
            )
        self._side = side
        self._scale = scale
        self._gamma = gamma

    @property
    def side(self) -> Role:
        return self._side

    @property
    def scale(self) -> float:
        return self._scale

    @property
    def gamma(self) -> float:
        return self._gamma

    def potentials(self, rollout: EpisodeRollout) -> NDArray[np.float64]:
        """The per-frame potential Φ series (numpy lands here)."""

        return np.asarray(
            [
                _side_potential(self._side, frame, self._scale)
                for frame in rollout.frames
            ],
            dtype=np.float64,
        )

    def shaping_series(self, rollout: EpisodeRollout) -> NDArray[np.float64]:
        """The per-step shaping term ``γ·Φ(s_{t+1}) − Φ(s_t)``.

        Empty when the episode has fewer than two frames (no transition to
        shape)."""

        phi = self.potentials(rollout)
        if phi.shape[0] < 2:
            return np.zeros(0, dtype=np.float64)
        return self._gamma * phi[1:] - phi[:-1]

    def shaping_sum(self, rollout: EpisodeRollout) -> float:
        """Total shaping over the episode.

        At ``γ = 1`` this equals ``Φ(terminal) − Φ(initial)`` for ANY episode —
        the telescoping identity, which is true and pinned by test. Telescoping is
        NOT invariance: ``Φ(terminal)`` is a trajectory-dependent cumulative count,
        so from ``Φ(initial) = 0`` this total IS the episode's terminal kill share
        (impostor) / completed-task share (crew). Two trajectories with equal
        environment reward and different terminal counts therefore get different
        shaped returns — the shaping CAN change the optimal policy (Task 19.4;
        module docstring item 2).
        """

        return float(self.shaping_series(rollout).sum())


@dataclass(frozen=True)
class ShapedReward:
    """One side's shaped reward for one episode (Task 15.8 public type).

    ``terminal_reward`` is the sparse win/loss (±1). ``dense_terms`` are the
    side-specific tactically-reachable terms. ``shaping_sum`` is the potential-
    based shaping total (``= potential_terminal − potential_initial`` at
    ``gamma == 1``). :meth:`total` is the scalar an optimizer maximizes. Signature
    is stable per the task contract.
    """

    side: Role
    terminal_reward: float
    dense_terms: Mapping[str, float]
    shaping_sum: float
    potential_initial: float
    potential_terminal: float
    gamma: float = 1.0
    dense_weight: float = 1.0
    shaping_weight: float = 1.0
    terminal_weight: float = 1.0

    def total(self) -> float:
        """The scalar fitness: terminal + weighted dense terms + shaping."""

        dense = sum(self.dense_terms.values())
        return (
            self.terminal_weight * self.terminal_reward
            + self.dense_weight * dense
            + self.shaping_weight * self.shaping_sum
        )


def _impostor_terms(rollout: EpisodeRollout) -> dict[str, float]:
    # Kill VOLUME is not a term here: the shaping already pays exactly the kill
    # count (as a share of the initial crew), so a raw ``kills`` term would price
    # the same quantity a second time and rank arms by kill volume rather than by
    # winning. What survives is what kills cannot buy — stealth, survival, and
    # riding out the meetings.
    kills = [event for event in rollout.events if isinstance(event, KilledEvent)]
    # Un-witnessed-ness is CREW evidence (the stealth signal): a kill seen only by
    # a fellow impostor produced no crew testimony, so it counts as un-witnessed
    # (see :func:`training.rollout.crew_witnesses`).
    unwitnessed = sum(1 for event in kills if not crew_witnesses(event, rollout.roles))
    last = rollout.frames[-1] if rollout.frames else None
    impostors_alive = last.alive_impostors if last is not None else 0
    meetings_survived = sum(
        1
        for meeting in rollout.meetings
        if meeting.ejected_player_id is None
        or rollout.roles.get(meeting.ejected_player_id) != "IMPOSTOR"
    )
    return {
        "unwitnessed_kills": unwitnessed / max(1, len(kills)),
        "survival": impostors_alive / max(1, rollout.num_impostors),
        "meetings_survived": meetings_survived / max(1, len(rollout.meetings)),
    }


def _crew_terms(rollout: EpisodeRollout) -> dict[str, float]:
    last = rollout.frames[-1] if rollout.frames else None
    task_progress = (
        last.tasks_completed / max(1, last.tasks_total) if last is not None else 0.0
    )
    crew_alive = last.alive_crew if last is not None else 0
    initial_crew = max(1, rollout.num_players - rollout.num_impostors)
    # correctly-routed reports: count only meetings a crewmate ROUTED via a body
    # report that ejected an impostor — never an emergency or an impostor-triggered
    # report, which credit the crew for outcomes it did not produce.
    correct_reports = sum(
        1
        for meeting in rollout.meetings
        if meeting.trigger == "report"
        and rollout.roles.get(meeting.triggered_by) == "CREWMATE"
        and meeting.ejected_player_id is not None
        and rollout.roles.get(meeting.ejected_player_id) == "IMPOSTOR"
    )
    # buddy/patrol coverage of last-seen suspects: the fraction of genuine PLAY
    # ticks a crewmate shadowed a suspect's ACTUAL position (an impostor). Reads
    # engine truth (like every reward term), so a crew that shadows a suspect
    # WITHOUT filing a report is rewarded and an unrelated body report is not —
    # the Phase-15 crew coverage term the contract names. Trivial spawn / meeting
    # co-presence is excluded by reading only ``kind="tick"`` PLAY frames.
    play_frames = [
        frame
        for frame in rollout.frames
        if frame.kind == "tick" and frame.phase == "PLAY"
    ]
    patrol_coverage = (
        sum(1 for frame in play_frames if frame.crew_shadowing_impostor)
        / len(play_frames)
        if play_frames
        else 0.0
    )
    return {
        "task_progress": task_progress,
        "survival": crew_alive / initial_crew,
        # As a SHARE of the impostors there are to route out: a meeting ejects at
        # most one player and an ejected player is never ejected twice, so the
        # count cannot exceed ``num_impostors`` and the share stays in [0, 1].
        "correct_reports": correct_reports / max(1, rollout.num_impostors),
        "patrol_coverage": patrol_coverage,
    }


# The dense terms each side scores, in the order the term functions emit them.
# EVERY name here is a bounded share in [0, 1] — that boundedness is what makes
# :func:`derive_terminal_weight` a derivation rather than a guess, so a new term
# belongs in this map only once it is bounded too.
DENSE_TERM_NAMES: Final[Mapping[Role, tuple[str, ...]]] = {
    "IMPOSTOR": ("unwitnessed_kills", "survival", "meetings_survived"),
    "CREWMATE": ("task_progress", "survival", "correct_reports", "patrol_coverage"),
}


def bounded_term_count(side: Role) -> int:
    """How many [0, 1] channels the side's shaped reward carries: dense + shaping."""

    _validate_side(side)
    return len(DENSE_TERM_NAMES[side]) + 1


def derive_terminal_weight(side: Role) -> float:
    """The terminal weight at which the worst WIN outranks the best LOSS.

    With every dense term and the shaping in [0, 1], the worst reachable WIN scores
    ``+w`` and the best reachable LOSS ``−w + bounded_term_count``, so any
    ``w > bounded_term_count / 2`` orders wins above losses. This returns
    ``bounded_term_count + 1``, which additionally leaves a margin of
    ``bounded_term_count + 2`` between them — comfortably above the float noise of
    summing that many shares, and DERIVED from the term census so adding a term
    moves the weight instead of quietly shrinking the margin.
    """

    return float(bounded_term_count(side) + 1)


@dataclass(frozen=True)
class ObjectiveWeights:
    """How one side's fitness weights the three shaped-reward channels.

    The profile the inner-fitness functions forward to
    :func:`compute_shaped_reward`, so an experiment re-weights the objective
    through a parameter instead of an edit. :data:`DEFAULT_OBJECTIVE_WEIGHTS`
    carries each side's derived profile.
    """

    dense_weight: float = 1.0
    shaping_weight: float = 1.0
    terminal_weight: float = 1.0


DEFAULT_OBJECTIVE_WEIGHTS: Final[Mapping[Role, ObjectiveWeights]] = {
    side: ObjectiveWeights(terminal_weight=derive_terminal_weight(side))
    for side in DENSE_TERM_NAMES
}

# Names the objective the code below computes. A fitness number is only comparable
# to another produced under the SAME id, so a re-ground stamps its own rows with
# this and never compares them against rows that carry no id (those predate the
# bounded-term objective and were produced under raw-count dense terms).
FITNESS_OBJECTIVE_ID: Final[str] = "bounded-terms-win-dominant.v1"


def side_specific_terms(rollout: EpisodeRollout, side: Role) -> dict[str, float]:
    """The side-specific tactically-reachable reward terms (Task 15.8).

    Reads only the typed event log + per-step frames + roster roles — never the
    replay bytes. Available for a truncated episode too (the DENSE terms are
    always well-defined); only the TERMINAL sparse reward is gated on
    completeness (see :func:`compute_shaped_reward`).
    """

    _validate_side(side)
    if side == "IMPOSTOR":
        return _impostor_terms(rollout)
    return _crew_terms(rollout)


def _terminal_reward(rollout: EpisodeRollout, side: Role) -> float:
    won = (side == "IMPOSTOR" and rollout.winner == "IMPOSTORS") or (
        side == "CREWMATE" and rollout.winner == "CREWMATES"
    )
    return 1.0 if won else -1.0


def compute_shaped_reward(
    rollout: EpisodeRollout,
    side: Role,
    *,
    gamma: float = 1.0,
    dense_weight: float = 1.0,
    shaping_weight: float = 1.0,
    terminal_weight: float = 1.0,
) -> ShapedReward:
    """Score one COMPLETE episode's shaped reward for ``side`` (Task 15.8).

    Refuses a truncated / incomplete episode (:class:`TruncatedEpisodeError`): a
    terminal win/loss is only defined for a full game, so a tick-budget-capped
    episode is never scored as one — the structural guard that keeps silent
    truncation off every fitness path.
    """

    _validate_side(side)
    if not rollout.complete:
        raise TruncatedEpisodeError(
            f"refusing to score a non-terminal episode as a full game "
            f"(seed={rollout.seed}, boundary={rollout.episode_boundary!r}, "
            f"truncated={rollout.truncated}, winner={rollout.winner!r})"
        )
    shaper = PotentialShaper(
        side=side, scale=potential_scale(rollout, side), gamma=gamma
    )
    phi = shaper.potentials(rollout)
    potential_initial = float(phi[0]) if phi.shape[0] else 0.0
    potential_terminal = float(phi[-1]) if phi.shape[0] else 0.0
    return ShapedReward(
        side=side,
        terminal_reward=_terminal_reward(rollout, side),
        dense_terms=side_specific_terms(rollout, side),
        shaping_sum=shaper.shaping_sum(rollout),
        potential_initial=potential_initial,
        potential_terminal=potential_terminal,
        gamma=gamma,
        dense_weight=dense_weight,
        shaping_weight=shaping_weight,
        terminal_weight=terminal_weight,
    )


__all__ = [
    "DEFAULT_OBJECTIVE_WEIGHTS",
    "DENSE_TERM_NAMES",
    "FITNESS_OBJECTIVE_ID",
    "ObjectiveWeights",
    "PotentialShaper",
    "RewardSide",
    "ShapedReward",
    "TruncatedEpisodeError",
    "bounded_term_count",
    "compute_shaped_reward",
    "derive_terminal_weight",
    "potential_scale",
    "side_specific_terms",
]
