"""The ballot-surrogate substrate — the meeting training table + fidelity harness.

Task 15.11 (tasks/phase-15.md; audits/post-phase-14-ML-training-signal.md §2,
§5.4-5.5, §7.2) builds the supervised substrate the ballot surrogate (Task 15.13)
trains on and every meeting model is judged against — reconstructed OFFLINE from the
committed replay bytes, LLM-free and replay-deterministic.

Two committed folds:

* :mod:`training.surrogate.dataset` — the per-(meeting, voter) feature table. Each
  row reconstructs the pre-meeting belief-fold suspicion (the LLM-free fold in
  ``agents/memory/beliefs.py``, folded over PRIOR meetings' public evidence via
  ``meetings.manager.extract_belief_evidence`` — the ``derive_belief_evidence``
  derivation, roster off ``result.ballots``), the contradiction-flag structure
  (including the Task-15.4 ``vent_sighting`` flags), sighting/co-presence,
  reporter identity, kill-proximity and isolation, movement, and task cadence —
  joined to the ACTUAL recorded ballot ``{voter, target, confidence,
  primary_reason_id}`` and to roles ground truth.
* :mod:`training.surrogate.fidelity` — the by-GAME cross-validation harness every
  meeting model is judged with: top-1/top-2 ejected-target ranking, SKIP-vs-eject
  accuracy, Brier/ECE calibration, and the HONEST CEILING (the measured
  voice-driven share of ejections a physical+belief surrogate structurally cannot
  see, §2.2). It re-runs the FO-6 logistic (the failed prior,
  ``experiments/lab/ml_spike/fo6_learned_vote_surrogate.py``) to pin the true prior
  baseline and expose its always-SKIP collapse.

Public surface (stable signatures — downstream tasks import these):

* :class:`training.surrogate.dataset.MeetingTableRow`
* :func:`training.surrogate.dataset.build_meeting_table`
* :class:`training.surrogate.fidelity.SurrogateFidelityReport`
"""

from __future__ import annotations

from training.surrogate.dataset import (
    CandidateFeatures,
    MeetingTable,
    MeetingTableRow,
    SurrogateSplits,
    build_meeting_table,
    load_splits,
)
from training.surrogate.fidelity import (
    HonestCeiling,
    SurrogateFidelityReport,
    fo6_rebaseline,
    run_surrogate_fidelity,
)

__all__ = [
    "CandidateFeatures",
    "HonestCeiling",
    "MeetingTable",
    "MeetingTableRow",
    "SurrogateFidelityReport",
    "SurrogateSplits",
    "build_meeting_table",
    "fo6_rebaseline",
    "load_splits",
    "run_surrogate_fidelity",
]
