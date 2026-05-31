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

Phase 7 Wave 0 (W0.3) adds a fifth, enablement-gate analyzer defined in this
module:

* *Meeting rate* — how often games reach a meeting, with a body-report /
  emergency trigger breakdown (:func:`compute_meeting_rate`). This makes the
  Stage-A close gate (``meeting_rate ≥ 0.60`` with ≥ 30 resolved meetings) a
  measurable scalar, and surfaces the currently-dead emergency-button pathway
  so any later feature that revives it becomes visible.

:class:`~eval.report_schema.TournamentReport` is frozen with
``extra="forbid"``, so the metric outputs cannot be added as fields on it.
They live instead on :class:`TournamentEvalReport`, a frozen wrapper that
holds the immutable report plus the metric results as named fields. This
wrapper is the single typed shape the dashboard (Task 5.7) and the regression
suite (Task 5.8) consume.

:func:`build_tournament_eval_report` is the assembler: it calls each public
``compute_*`` analyzer over a :class:`TournamentReport` and packs the results.
It consumes the metrics' public APIs and duplicates no metric logic — every
number on a :class:`TournamentEvalReport` is produced by the owning metric
module, never re-derived here.
"""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, model_validator

from eval.accusation_calibration import (
    AccusationCalibrationReport,
    compute_accusation_calibration,
)
from eval.alibi_fabrication import (
    AlibiFabricationReport,
    compute_alibi_fabrication_rate,
)
from eval.cost_dashboard import CostDashboard, compute_cost_dashboard
from eval.report_schema import GameReport, MeetingReport, TournamentReport
from eval.vote_correctness import VoteCorrectnessReport, compute_vote_correctness
from meetings.schemas import FoundBodyObservation


class MeetingRateReport(BaseModel):
    """Aggregated meeting-rate result (DESIGN.md §11.3; Phase 7 W0.3).

    Frozen value object summarizing how often games reached a meeting across the
    analyzed games, plus a body-report / emergency trigger breakdown.

    * ``games_total`` — number of games folded.
    * ``games_with_meeting`` — games whose ``meetings`` tuple is non-empty.
    * ``meeting_rate`` — ``games_with_meeting / games_total``, the Stage-A
      close-gate scalar. It is ``None`` (undefined, **not** ``0.0``) when
      ``games_total == 0``, mirroring the
      :attr:`~eval.vote_correctness.VoteCorrectnessReport.vote_correctness_rate`
      convention (reporting ``0.0`` would falsely imply games ran and none
      reached a meeting).
    * ``meetings_total`` — ``sum(len(game.meetings))`` across all games (a game
      may hold more than one meeting, so this is ``>= games_with_meeting``).
    * ``body_report_meetings`` / ``emergency_meetings`` — the trigger breakdown,
      which partitions exactly into ``meetings_total``.

    **Trigger-breakdown heuristic and its two-fold catch-all limitation.** The
    real trigger kind (body-report vs emergency-button) lives only on the
    per-tick :class:`engine.events.MeetingTriggeredEvent`; it is not carried on
    :class:`~eval.report_schema.MeetingReport` or the persisted replay record,
    so this metric *derives* the breakdown (:func:`_is_body_report`): a meeting
    is ``body_report`` iff the report submitted by its ``triggered_by`` player
    contains at least one :class:`~meetings.schemas.FoundBodyObservation`, and
    ``emergency`` otherwise. Consequently ``emergency_meetings`` is a CATCH-ALL,
    not a positively-identified emergency-button count: it equals
    {true emergency-button meetings} ∪ {body-report meetings whose triggering
    report carried no ``FoundBodyObservation`` — e.g. malformed / partial
    replay}. Today both addends are ~0 (the Phase 7 diagnosis observed 0/50
    emergencies and a clean body-report path), so the bucket is accurate now;
    but a future Wave that revives emergency-button play MUST NOT trust
    ``emergency_meetings`` as a pure emergency count without first adding a real
    persisted ``trigger_kind`` (a later-phase change to ``orchestrator/replay.py``
    + ``eval/balance_eval.py``, out of scope for Wave 0).

    **Leak-safety.** Every field is a pure aggregate of counts (a rate and five
    integers). The report carries no roles, no transcripts, and no engine-owned
    types, so it exposes no hidden / engine state and adds no leak risk to the
    ``/eval/tournament-report`` surface (``tests/api/test_leak.py``).

    The post-init validator enforces the bucket invariants fail-loud so an
    inconsistent result can never be constructed (mirrors
    :class:`eval.vote_correctness.VoteCorrectnessReport`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    games_total: int
    games_with_meeting: int
    meeting_rate: float | None
    meetings_total: int
    body_report_meetings: int
    emergency_meetings: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> MeetingRateReport:
        counts = (
            self.games_total,
            self.games_with_meeting,
            self.meetings_total,
            self.body_report_meetings,
            self.emergency_meetings,
        )
        if any(count < 0 for count in counts):
            raise ValueError("meeting-rate counts must be non-negative")
        if self.body_report_meetings + self.emergency_meetings != self.meetings_total:
            raise ValueError(
                "body_report_meetings + emergency_meetings must equal "
                f"meetings_total: {self.body_report_meetings} + "
                f"{self.emergency_meetings} != {self.meetings_total}"
            )
        if self.games_with_meeting > self.games_total:
            raise ValueError(
                "games_with_meeting cannot exceed games_total: "
                f"{self.games_with_meeting} > {self.games_total}"
            )
        if self.games_total == 0:
            if self.meeting_rate is not None:
                raise ValueError(
                    "meeting_rate must be None when there are no games: the rate "
                    "is undefined, not 0.0"
                )
        else:
            if self.meeting_rate is None:
                raise ValueError("meeting_rate must be set when games_total > 0")
            if not 0.0 <= self.meeting_rate <= 1.0:
                raise ValueError(
                    f"meeting_rate must be in [0.0, 1.0]: {self.meeting_rate}"
                )
        return self


def compute_meeting_rate(
    report: TournamentReport | Sequence[GameReport],
) -> MeetingRateReport:
    """Fold a tournament report (or game sequence) into a meeting-rate summary.

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the
    :func:`eval.vote_correctness.compute_vote_correctness` signature; the metric
    only needs the games). Pure: no I/O, no engine/agent/LLM calls.

    ``games_with_meeting`` counts games with a non-empty ``meetings`` tuple;
    ``meetings_total`` sums their lengths. The trigger breakdown is derived from
    :class:`~eval.report_schema.MeetingReport` data only (see
    :func:`_is_body_report` and the :class:`MeetingRateReport` docstring's
    two-fold catch-all note). ``meeting_rate`` is ``None`` when ``games_total ==
    0``. A meeting with no matching triggering report (malformed / partial
    replay) classifies as ``emergency`` and never raises — matching the
    partial-replay robustness the other §11.3 analyzers state.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    games_total = len(games)
    games_with_meeting = sum(1 for game in games if game.meetings)
    meetings_total = sum(len(game.meetings) for game in games)
    body_report_meetings = sum(
        1 for game in games for meeting in game.meetings if _is_body_report(meeting)
    )
    emergency_meetings = meetings_total - body_report_meetings
    meeting_rate = games_with_meeting / games_total if games_total > 0 else None

    return MeetingRateReport(
        games_total=games_total,
        games_with_meeting=games_with_meeting,
        meeting_rate=meeting_rate,
        meetings_total=meetings_total,
        body_report_meetings=body_report_meetings,
        emergency_meetings=emergency_meetings,
    )


def _is_body_report(meeting: MeetingReport) -> bool:
    """True iff the meeting's triggering report names a found body.

    Scans ``meeting.transcript.reports`` for the report submitted by the
    meeting's ``triggered_by`` player (matched by ``document.agent_id ==
    meeting.triggered_by``) and returns ``True`` iff that report carries any
    :class:`~meetings.schemas.FoundBodyObservation`. A meeting with no matching
    report (malformed / partial replay) yields ``False`` and never raises, so it
    falls into the ``emergency`` catch-all bucket. See the
    :class:`MeetingRateReport` docstring for why this derived classification is
    accurate today but must not be trusted as a pure emergency count by a future
    emergency-reviving Wave.
    """

    return any(
        isinstance(observation, FoundBodyObservation)
        for document in meeting.transcript.reports
        if document.agent_id == meeting.triggered_by
        for observation in document.observations
    )


class TournamentEvalReport(BaseModel):
    """A tournament report bundled with its Phase 5 / W0.3 metric results.

    Frozen and ``extra="forbid"``, mirroring the report-schema convention: it is
    an immutable value object and an unexpected field is a bug, not something to
    silently absorb (AGENTS.md "no silent fallbacks").

    ``report`` is the immutable :class:`~eval.report_schema.TournamentReport`
    (the raw per-game / per-meeting artifacts and role ground truth). The metric
    fields are the outputs of the DESIGN.md §11.3 analyzers (plus the Phase 7
    W0.3 :class:`MeetingRateReport`) over that report. Because every member is a
    frozen Pydantic model, the whole bundle round-trips through
    ``model_dump_json`` / ``model_validate_json``, which is how Task 5.7
    (dashboard) and Task 5.8 (regression suite) load it.

    ``meeting_rate`` is added to this WRAPPER, which is not version-stamped;
    ``format_version`` lives only on the inner persisted ``report`` and is
    unchanged by this metric (it adds no persisted report/replay field), so
    :data:`~eval.report_schema.CURRENT_FORMAT_VERSION` is NOT bumped.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    report: TournamentReport
    vote_correctness: VoteCorrectnessReport
    accusation_calibration: AccusationCalibrationReport
    alibi_fabrication: AlibiFabricationReport
    cost_dashboard: CostDashboard
    meeting_rate: MeetingRateReport


def build_tournament_eval_report(report: TournamentReport) -> TournamentEvalReport:
    """Run the §11.3 + W0.3 analyzers over ``report`` and wrap the results.

    Pure assembly: each metric is computed by its own public ``compute_*``
    entry point over the same :class:`~eval.report_schema.TournamentReport`, and
    the results are packed into a :class:`TournamentEvalReport`. No metric math
    is reimplemented here — this function only orchestrates the analyzers
    (including :func:`compute_meeting_rate`) and bundles their outputs with the
    source report; it never re-derives a count inline.
    """

    return TournamentEvalReport(
        report=report,
        vote_correctness=compute_vote_correctness(report),
        accusation_calibration=compute_accusation_calibration(report),
        alibi_fabrication=compute_alibi_fabrication_rate(report),
        cost_dashboard=compute_cost_dashboard(report),
        meeting_rate=compute_meeting_rate(report),
    )


__all__ = [
    "MeetingRateReport",
    "TournamentEvalReport",
    "build_tournament_eval_report",
    "compute_meeting_rate",
]
