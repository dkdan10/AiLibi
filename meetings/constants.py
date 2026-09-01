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

The same rule homes the ``testimony_shapes`` resolver here. Both sides of the
firewall must read that ONE lever -- :mod:`meetings.manager` for the testimony
reduction and ``agents.strategic.prompts.loader`` for the render routing -- and
the ``agents ↛ meetings.manager`` import contract forbids the obvious home, so
a leaf both may import is the only place a single source of truth can sit.

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


# The testimony-shapes lever, DEFAULT OFF: what a witness may SAY and what a
# listener KEEPS of it.
ENV_TESTIMONY_SHAPES: Final[str] = "AILIBI_TESTIMONY_SHAPES"
_TESTIMONY_SHAPES_FLAG_TRUE: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)


def testimony_shapes_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the testimony-shapes lever is ON. DEFAULT OFF.

    Reads :data:`ENV_TESTIMONY_SHAPES` from ``env`` (defaulting to the real
    process environment) and accepts ``1/true/yes/on`` case-insensitively; an
    unset / empty / unrecognised value is ``False``. The ``env`` argument lets
    tests and offline re-derivations toggle the lever deterministically without
    mutating ``os.environ``.

    ON does two things. The meeting reduction
    (:func:`meetings.manager.derive_reported_testimony`) carries three more
    spoken shapes into listeners' episodic memory -- a roll-call
    ``whereabouts``, a witnessed ``saw_move`` transition and a witnessed
    ``saw_kill`` -- and the crew turn templates OFFER the witnessed-kill shape,
    which no template offers at all while the lever is OFF. OFF returns exactly
    the pre-lever tuple and exactly the committed template bytes, so every
    committed recording reconstructs unmoved.

    Read at ONE place per entry point and never cached in a module-level
    boolean: the loader binds the resolved value into its renderer partials at
    construction and ``orchestrator.game.prompt_versions_for_set`` reads the
    same lever for the stamp, which is what keeps rendered bytes and recorded
    provenance on one routing decision.
    """

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_TESTIMONY_SHAPES, "").strip().lower()
        in _TESTIMONY_SHAPES_FLAG_TRUE
    )


__all__ = [
    "DEFAULT_SKIP_CONFIDENCE_THRESHOLD",
    "ENV_TESTIMONY_SHAPES",
    "GROUNDED_PROSECUTION_MIN_SOURCES",
    "MAP_ARBITRATION_MAX_HOPS",
    "MAP_ARBITRATION_MAX_TICK_GAP",
    "testimony_shapes_enabled",
]
