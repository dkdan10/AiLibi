"""Leaf home for the meeting-layer numeric constants (Task 15.6).

The §4.6 skip-confidence gate is read on BOTH sides of the observation
firewall: :mod:`meetings.manager` (the redirect guard + the vote-ballot
render input) and :mod:`agents.tactical.crewmate_policy` (the rule-based
emergency-call gate). Homing the constant here -- a stdlib-only leaf with
no ``meetings.manager`` import -- lets ``agents/`` read it WITHOUT importing
the 3-KLoC manager module, which is what makes the ``agents ↛
meetings.manager`` import contract satisfiable (audit post-phase-14-pause
§3, constant homing). ``meetings.manager`` re-exports it for its existing
callers, so no downstream import path breaks.

The Task 16.6 ``citation_gate_enabled`` lever resolver is homed here for the
same reason: :mod:`meetings.manager` gates its ballot citation guard on it,
and :mod:`orchestrator.replay` registers it in the lever-stamp table --
homing the resolver in this leaf keeps the manager import-clean (no
``orchestrator``/``agents`` import for a one-line env read) and lets the
replay registry import it without touching the 3-KLoC manager module.

Keep this module stdlib-only (no ``meetings.*`` / ``agents.*`` /
``engine.*`` imports) so it stays a true leaf every layer can depend on.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Final

# DESIGN.md §4.6 default skip-confidence threshold: a voter whose maximum
# rendered suspicion over the living ejection candidates lands below this
# reads MUST-skip; at or above it reads MUST-vote (the inclusive cutoff the
# deterministic tally in :func:`meetings.voting.tally_votes` applies). The
# committed baseline sets were recorded under this value; the eval-side
# re-declaration (``eval._suspicion_parse.SKIP_SUSPICION_THRESHOLD``) is
# pinned equal to it by ``tests/eval/test_suspicion_parse_pin.py``.
DEFAULT_SKIP_CONFIDENCE_THRESHOLD: Final[float] = 0.6


# Task 16.6 citation-gate lever — UNCONDITIONAL since the Task-16.17 baseline-5
# record (the graduation slate, audits/audit-phase-16-close.md §0.1.3). The
# lever was adopted by the baseline-5 re-record, so — mirroring the
# 14.9/14.12/15.7 graduations — it is now the default substrate rather than an
# env-gated toggle: the J2 ballot citation guard always applies. This is
# byte-identical to the baseline-5 recording (which ran the lever ON), and it
# lets the committed set reconstruct/serve under a BARE environment (no
# AILIBI_* export). The lever is stamped unconditionally ON via
# ``orchestrator.replay._RETIRED_ALWAYS_ON_LEVERS``; a stamp recording it OFF
# is a legacy (baseline-3/4) artifact that fails loud (no cross-substrate
# replay). ``ENV_CITATION_GATE`` is retained (no longer read) for the stamp
# key's naming provenance and backward-compatible imports.
ENV_CITATION_GATE: Final[str] = "AILIBI_CITATION_GATE"


def citation_gate_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the Task 16.6 citation-gate (J2) lever is ON — now always True.

    Retired to UNCONDITIONAL at the Task-16.17 baseline-5 record (the 15.7 move,
    applied to this lever once baseline 5 adopted it per the graduation slate —
    the soundness counterfactual read near-zero honest catches blocked, and
    16.5's rendered ids + 16.15's citation asks supply the citation channel the
    gate honors). The J2 citation guard applies at exactly ONE read-site --
    :meth:`meetings.manager.MeetingManager._collect_one_ballot`, where a
    zero-flag EJECT ballot (its target carries NO contradiction flag this
    meeting) whose ``primary_reason_id`` AND ``primary_reason_observation_id``
    are both null after validation is coerced to SKIP with an audit marker
    (:func:`meetings.manager.guard_ballot_citation`) -- never a crash, never a
    re-prompt. The ``env`` argument is accepted and ignored (retained so the
    call site and the substrate stamp read one source of truth without a
    signature churn).
    """

    del env  # retired: the lever is unconditional, no environment is consulted
    return True


# The minimum number of DISTINCT SPEAKERS that must stand behind the case
# against one subject before an ``alibi_vs_sighting`` flag may band STRONG under
# :func:`meetings.transcript.grounded_prosecution_enabled`. A speaker counts
# once however many records they hold, sightings they speak, or channels they
# speak through: a ``vent_sighting`` or ``alibi_vs_physical`` flag naming the
# same subject substitutes for a second WITNESS, never for a second account by
# the same one. Homed in this leaf so the pre-registration memo and the audit
# workflows can cite the threshold without importing the 3-KLoC detector.
GROUNDED_PROSECUTION_MIN_SOURCES: Final[int] = 2

# The two thresholds of map-aware flag arbitration
# (:func:`meetings.transcript.map_aware_arbitration_enabled`): how far apart the
# two rooms of an ``alibi_vs_sighting`` pair may sit, in doorway hops on the
# canonical map, and how close the sighting tick must sit to the nearest edge of
# the alibi window, for one tick of walking to reconcile both statements.
#
# One hop is one tick: every room edge on the canonical map costs
# ``traversal_ticks: 1`` (pinned beside
# :data:`meetings.transcript.CANONICAL_ROOM_NEIGHBORS`), so a single hop is
# exactly what one tick of window slack buys. A sighting two or more ticks
# inside a claim of continuous presence stays a contradiction: leaving and
# returning costs two ticks, which the claim's interior rules out anyway.
# Homed in this leaf so an audit workflow can cite the thresholds without
# importing the 3-KLoC detector.
MAP_ARBITRATION_MAX_HOPS: Final[int] = 1
MAP_ARBITRATION_MAX_TICK_GAP: Final[int] = 1


__all__ = [
    "DEFAULT_SKIP_CONFIDENCE_THRESHOLD",
    "ENV_CITATION_GATE",
    "GROUNDED_PROSECUTION_MIN_SOURCES",
    "MAP_ARBITRATION_MAX_HOPS",
    "MAP_ARBITRATION_MAX_TICK_GAP",
    "citation_gate_enabled",
]
