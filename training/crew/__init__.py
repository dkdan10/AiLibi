"""The Phase-15 crew track (Task 15.16).

The secondary track of the mid-phase measurement wave, run on 15.15's shared
machinery consumed strictly read-only: a learned utility scorer over a FIXED,
observable-only crew option set — continue-to-task, buddy-toward the nearest
visible/belief-trusted group, patrol-toward last-seen suspect, report, emergency
(through the existing ``EmergencyPacingTracker`` gate semantics), repair, hold
(audits/post-phase-14-ML-planning.md §4.1/§5.2). The scorer is trained with the
15.14 ES core against the frozen scripted impostor, anchored (cross-entropy) to
:class:`agents.tactical.crewmate_policy.CrewmatePolicy`, and evaluated under the
15.15 protocol shape (gate/referee/fitness/determinism/leak) into its own report
+ jsonl (``training/reports/report-crew-track.md`` /
``results-crew-track.jsonl``).

Two modules:

* :mod:`training.crew.options` — the observable option set + per-option
  features (:class:`~training.crew.options.CrewOption`,
  :func:`~training.crew.options.enumerate_crew_options`). Every feature derives
  from the observation packet + the crew agent's OWN memory; nothing
  role-derived crosses in.
* :mod:`training.crew.scorer` — the learned scorer
  (:class:`~training.crew.scorer.CrewOptionScorer`), the crew-side rollout /
  eval twin of the 15.15 harness, and the training entry point.

Task-ordering is EXPLICITLY OUT of this track: the packet exposes a single
engine-fed ``pending_task_id`` and no owned-task set, so ordering is
un-observable — the report states the surface ask for the pause instead of
widening the observation surface (the pause owns that decision).
"""

from __future__ import annotations
