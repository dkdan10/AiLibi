"""Tournament eval-report wrapper + builder (DESIGN.md §11.3).

The Phase 5 convergence shape. DESIGN.md §11.3 defines four behavioral /
cost analyzers over the typed tournament report:

* *Vote correctness* — were impostor ejections driven by real evidence?
  (:func:`eval.vote_correctness.compute_vote_correctness`)
* *Accusation calibration* — are high-confidence accusations more often
  correct? (:func:`eval.accusation_calibration.compute_accusation_calibration`)
* *Alibi-fabrication rate* — how often do impostor alibis survive contradiction
  detection? (:func:`eval.alibi_fabrication.compute_alibi_fabrication_rate`)
* *Cost dashboard* — per-tournament spend roll-up
  (:func:`eval.cost_dashboard.compute_cost_dashboard`)

:class:`~eval.report_schema.TournamentReport` is frozen with
``extra="forbid"``, so the metric outputs cannot be added as fields on it.
They live instead on :class:`TournamentEvalReport`, a new frozen wrapper that
holds the immutable report plus the four metric results as named fields. This
wrapper is the single typed shape the dashboard (Task 5.7) and the regression
suite (Task 5.8) consume.

:func:`build_tournament_eval_report` is the assembler: it calls each public
``compute_*`` analyzer over a :class:`TournamentReport` and packs the results.
It consumes the metrics' public APIs and duplicates no metric logic — every
number on a :class:`TournamentEvalReport` is produced by the owning metric
module, never re-derived here.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from eval.accusation_calibration import (
    AccusationCalibrationReport,
    compute_accusation_calibration,
)
from eval.alibi_fabrication import (
    AlibiFabricationReport,
    compute_alibi_fabrication_rate,
)
from eval.cost_dashboard import CostDashboard, compute_cost_dashboard
from eval.report_schema import TournamentReport
from eval.vote_correctness import VoteCorrectnessReport, compute_vote_correctness


class TournamentEvalReport(BaseModel):
    """A tournament report bundled with its four Phase 5 metric results.

    Frozen and ``extra="forbid"``, mirroring the report-schema convention: it is
    an immutable value object and an unexpected field is a bug, not something to
    silently absorb (AGENTS.md "no silent fallbacks").

    ``report`` is the immutable :class:`~eval.report_schema.TournamentReport`
    (the raw per-game / per-meeting artifacts and role ground truth). The four
    metric fields are the outputs of the DESIGN.md §11.3 analyzers over that
    report. Because all five members are frozen Pydantic models, the whole
    bundle round-trips through ``model_dump_json`` / ``model_validate_json``,
    which is how Task 5.7 (dashboard) and Task 5.8 (regression suite) load it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    report: TournamentReport
    vote_correctness: VoteCorrectnessReport
    accusation_calibration: AccusationCalibrationReport
    alibi_fabrication: AlibiFabricationReport
    cost_dashboard: CostDashboard


def build_tournament_eval_report(report: TournamentReport) -> TournamentEvalReport:
    """Run the four §11.3 analyzers over ``report`` and wrap the results.

    Pure assembly: each metric is computed by its own public ``compute_*``
    entry point over the same :class:`~eval.report_schema.TournamentReport`, and
    the results are packed into a :class:`TournamentEvalReport`. No metric math
    is reimplemented here — this function only orchestrates the four analyzers
    and bundles their outputs with the source report.
    """

    return TournamentEvalReport(
        report=report,
        vote_correctness=compute_vote_correctness(report),
        accusation_calibration=compute_accusation_calibration(report),
        alibi_fabrication=compute_alibi_fabrication_rate(report),
        cost_dashboard=compute_cost_dashboard(report),
    )


__all__ = [
    "TournamentEvalReport",
    "build_tournament_eval_report",
]
