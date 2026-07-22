"""The seam co-evolution package (Task 18.19).

The dual-role co-evolution seam: where the 15.15 impostor bake-off
(``training/bakeoff/harness.py``) and the 15.16 crew track
(``training/crew/scorer.py``) each freeze the OPPOSITE role to the scripted
FSM, this package composes their two interposition wrappers into one game so
BOTH sides can be independently the scripted FSM (``None``), a live candidate,
or a frozen learned artifact — the shape 18.20's hall of fame and 18.21's
alternating-freeze driver optimize over.

Two modules land in this wave:

* :mod:`training.coevo.factory` — :func:`~training.coevo.factory.build_coevo_factory`,
  the role-branching factory that wraps impostors in the harness's
  ``_CandidateAgent`` and crew in the scorer's ``_CrewCandidateAgent`` (the two
  wrappers are imported and mirrored, never rewired), with the encoder-namespace
  conflation guard that fails loud BEFORE any game runs.
* :mod:`training.coevo.rollout` — :func:`~training.coevo.rollout.rollout_coevo`,
  the co-evo twin of ``rollout_candidate`` / ``rollout_crew_candidate`` that
  scores BOTH sides' inner fitness off the ONE reconstructed episode.

Tasks 18.20 (the hall of fame) and 18.21 (the alternating-freeze driver) grow
this package; this wave adds only the factory + the rollout. No re-exports —
callers import the two public symbols from the submodules directly (the
``training.crew`` package-marker idiom).
"""

from __future__ import annotations
