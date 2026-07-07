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


__all__ = [
    "DEFAULT_SKIP_CONFIDENCE_THRESHOLD",
]
