"""The ``training/`` package — the Phase-15 rollout environment (Task 15.8).

Strict-typed from day one (no mypy exclusion). Holds the rollout environment
every trainer in this phase rides, plus the legal-action mask, the potential-
based reward channel, and the per-episode rollout records. ``numpy`` is a pinned
dependency confined to THIS package by an import-linter contract (``agents`` must
not import ``training``): production inference under ``agents/`` stays pure-Python
because BLAS reductions are not bit-stable across machines/thread counts (Task
15.8 integration risk; DESIGN.md locked dependency posture).

Public surface (stable signatures — downstream tasks import these):

* :class:`training.env.TacticalRolloutEnv` — the injected-factory rollout env.
* :class:`training.env.ActionMask` — the legal-action / observation-meaningful mask.
* :class:`training.rollout.EpisodeRollout` — one typed, reconstructed episode.
* :class:`training.rewards.ShapedReward` — one side's potential-based reward.
"""

from __future__ import annotations

from training.env import (
    ActionMask,
    IntentSelector,
    MaskedDecision,
    TacticalRolloutEnv,
    build_action_mask,
    build_interposition_factory,
)
from training.rewards import (
    PotentialShaper,
    RewardSide,
    ShapedReward,
    TruncatedEpisodeError,
    compute_shaped_reward,
    side_specific_terms,
)
from training.rollout import (
    BehavioralDescriptors,
    EpisodeBoundary,
    EpisodeFrame,
    EpisodeOutcome,
    EpisodeRollout,
    MeetingRecord,
    RolloutReconstructionError,
    reconstruct_episode,
)

__all__ = [
    "ActionMask",
    "BehavioralDescriptors",
    "EpisodeBoundary",
    "EpisodeFrame",
    "EpisodeOutcome",
    "EpisodeRollout",
    "IntentSelector",
    "MaskedDecision",
    "MeetingRecord",
    "PotentialShaper",
    "RewardSide",
    "RolloutReconstructionError",
    "ShapedReward",
    "TacticalRolloutEnv",
    "TruncatedEpisodeError",
    "build_action_mask",
    "build_interposition_factory",
    "compute_shaped_reward",
    "reconstruct_episode",
    "side_specific_terms",
]
