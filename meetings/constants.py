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

Keep this module stdlib-only (no ``meetings.*`` / ``agents.*`` /
``engine.*`` imports) so it stays a true leaf every layer can depend on.
"""

from __future__ import annotations

from typing import Final

# DESIGN.md §4.6 default skip-confidence threshold: a voter whose maximum
# rendered suspicion over the living ejection candidates lands below this
# reads MUST-skip; at or above it reads MUST-vote (the inclusive cutoff the
# deterministic tally in :func:`meetings.voting.tally_votes` applies). The
# committed baseline sets were recorded under this value; the eval-side
# re-declaration (``eval._suspicion_parse.SKIP_SUSPICION_THRESHOLD``) is
# pinned equal to it by ``tests/eval/test_suspicion_parse_pin.py``.
DEFAULT_SKIP_CONFIDENCE_THRESHOLD: Final[float] = 0.6


# The minimum number of DISTINCT SPEAKERS that must stand behind the case
# against one subject before an ``alibi_vs_sighting`` flag may band STRONG. A
# speaker counts once however many records they hold, sightings they speak, or channels they
# speak through: a ``vent_sighting`` or ``alibi_vs_physical`` flag naming the
# same subject substitutes for a second WITNESS, never for a second account by
# the same one. Homed in this leaf so the pre-registration memo and the audit
# workflows can cite the threshold without importing the 3-KLoC detector.
GROUNDED_PROSECUTION_MIN_SOURCES: Final[int] = 2

# The two thresholds of map-aware flag arbitration
# (:func:`meetings.transcript.detect_contradictions`): how far apart the
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
    "GROUNDED_PROSECUTION_MIN_SOURCES",
    "MAP_ARBITRATION_MAX_HOPS",
    "MAP_ARBITRATION_MAX_TICK_GAP",
]
