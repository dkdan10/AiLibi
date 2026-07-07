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

2. **Potential-based shaping (Ng et al. 1999, policy-invariant).** A per-step
   shaping term ``F(s_t, s_{t+1}) = γ·Φ(s_{t+1}) − Φ(s_t)`` over a side-specific
   potential Φ read from the per-step engine-state scalars
   (:class:`training.rollout.EpisodeFrame`). At ``γ = 1`` the shaping TELESCOPES:
   ``Σ_t F = Φ(terminal) − Φ(initial)`` for ANY episode, so it cannot change the
   optimal policy. Φ is a pure integer count (impostor: cumulative kills; crew:
   completed task instances) — no float belief state — so the identity is exact.

The reward channel REFUSES to score a truncated episode as a full game
(:class:`TruncatedEpisodeError`): :func:`compute_shaped_reward` gates on
:attr:`EpisodeRollout.complete`, so a first-meeting opt-in episode (or a
tick-budget-capped one) can never be read as a terminal outcome — silent
truncation is never a fitness path (Task 15.8 definition of done).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TypeAlias, get_args

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
    raises this rather than returning a terminal reward for a first-meeting
    opt-in episode or a tick-budget-capped full-game episode.
    """


def _side_potential(side: Role, frame: EpisodeFrame) -> float:
    """The side-specific potential Φ at one step.

    A pure, monotonic integer count of engine-truth progress toward the side's
    win — impostor: cumulative resolved kills; crew: completed task instances.
    No float belief state crosses into Φ, so the telescoping identity is exact
    and byte-stable (the §7 determinism note)."""

    if side == "IMPOSTOR":
        return float(frame.cumulative_kills)
    return float(frame.tasks_completed)


class PotentialShaper:
    """Potential-based shaping over a side-specific potential Φ (Ng 1999).

    ``F(s_t, s_{t+1}) = γ·Φ(s_{t+1}) − Φ(s_t)``. At ``γ = 1`` the per-episode
    shaping sum telescopes to ``Φ(terminal) − Φ(initial)`` — the policy-invariance
    guarantee the telescoping test pins. numpy carries the per-step vector math
    (numpy is training-confined by the import-linter contract).
    """

    def __init__(self, *, side: Role, gamma: float = 1.0) -> None:
        _validate_side(side)
        self._side = side
        self._gamma = gamma

    @property
    def side(self) -> Role:
        return self._side

    @property
    def gamma(self) -> float:
        return self._gamma

    def potentials(self, rollout: EpisodeRollout) -> NDArray[np.float64]:
        """The per-frame potential Φ series (numpy lands here)."""

        return np.asarray(
            [_side_potential(self._side, frame) for frame in rollout.frames],
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

        At ``γ = 1`` this equals ``Φ(terminal) − Φ(initial)`` for ANY episode
        (the telescoping identity), so shaping cannot change the optimal policy.
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
        "kills": float(len(kills)),
        "unwitnessed_kills": float(unwitnessed),
        "survival": impostors_alive / max(1, rollout.num_impostors),
        "meetings_survived": float(meetings_survived),
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
        "correct_reports": float(correct_reports),
        "patrol_coverage": patrol_coverage,
    }


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
    terminal win/loss is only defined for a full game, so a first-meeting opt-in
    episode or a tick-budget-capped one is never scored as one — the structural
    guard that keeps silent truncation off every fitness path.
    """

    _validate_side(side)
    if not rollout.complete:
        raise TruncatedEpisodeError(
            f"refusing to score a non-terminal episode as a full game "
            f"(seed={rollout.seed}, boundary={rollout.episode_boundary!r}, "
            f"truncated={rollout.truncated}, winner={rollout.winner!r})"
        )
    shaper = PotentialShaper(side=side, gamma=gamma)
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
    "PotentialShaper",
    "RewardSide",
    "ShapedReward",
    "TruncatedEpisodeError",
    "compute_shaped_reward",
    "side_specific_terms",
]
