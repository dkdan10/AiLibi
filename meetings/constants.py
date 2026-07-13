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

import os
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


# Task 16.6 citation-gate lever — DEFAULT-OFF (the 16.4/16.5 live-toggle
# pattern, env-gated, NOT retired). Third entry in the
# ``orchestrator.replay._TOGGLEABLE_LEVER_RESOLVERS`` registry chain, behind
# 16.5's ``observation_id_rendering``: OFF (the default) leaves the ballot
# guard chain byte-identical to the committed baseline-3 substrate, and the
# 16.17 graduation decision re-measures the soundness counterfactual on the
# adopting baseline's bytes and may record it with the lever measured ON.
ENV_CITATION_GATE: Final[str] = "AILIBI_CITATION_GATE"
_CITATION_GATE_FLAG_TRUE: Final[frozenset[str]] = frozenset({"1", "true", "yes", "on"})


def citation_gate_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the Task 16.6 citation-gate (J2) lever is ON. DEFAULT OFF.

    Reads :data:`ENV_CITATION_GATE` from ``env`` (defaulting to the real
    process environment), mirroring the 16.4 ``hard_evidence_gate`` / 16.5
    ``observation_id_rendering`` resolvers it clones. Default OFF: an unset /
    empty / unrecognised value is ``False`` so the ballot guard chain stays
    byte-identical to the committed baseline-3 substrate
    (``scripts/verify_samples.sh`` reconstructs clean); the live re-measure of
    the soundness counterfactual and the graduation decision are Task 16.17.
    Accepts ``1/true/yes/on`` (case-insensitive). The ``env`` argument lets
    tests + the offline counterfactual toggle the lever deterministically
    without mutating ``os.environ``.

    ON gates the J2 citation guard at exactly ONE read-site --
    :meth:`meetings.manager.MeetingManager._collect_one_ballot`, where a
    zero-flag EJECT ballot (its target carries NO contradiction flag this
    meeting) whose ``primary_reason_id`` AND ``primary_reason_observation_id``
    are both null after validation is coerced to SKIP with an audit marker
    (:func:`meetings.manager.guard_ballot_citation`) -- never a crash, never a
    re-prompt. Lever gating lives at the call site (the 15.5/16.4 in-line
    pattern), never inside the pure guard helper.
    """

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_CITATION_GATE, "").strip().lower()
        in _CITATION_GATE_FLAG_TRUE
    )


__all__ = [
    "DEFAULT_SKIP_CONFIDENCE_THRESHOLD",
    "ENV_CITATION_GATE",
    "citation_gate_enabled",
]
