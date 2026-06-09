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

Phase 9 Wave 1 (Task 9.6, metric hygiene) adds a sixth, conversion-quality
analyzer defined in this module:

* *Conversion leads + SKIP sentinels* — the TWO published Wave-1 conversion
  leads (``ejection_accuracy``, the precision lead, and the
  impostor-accused -> impostor-ejected conversion rate, the recall lead) plus
  the SKIP-ballot sentinels (``missed_skip_ballots`` with its CORRECT/MISSED
  partition, and ``threshold_inversions`` as a §4.6 gate-obedience sentinel)
  (:func:`compute_conversion_report`; DESIGN.md §11.3, §5.5; audit
  audit-2026-06-09-0347 gp-2). This is the ruler fix that BLOCKS the Wave-1
  A/B: the old headline ``vote_correctness_rate`` is structurally pinned to
  1.0 (see :mod:`eval.vote_correctness`) and measures nothing, so the real
  leads are published beside it on the shipped report surface.

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
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from eval._suspicion_parse import (
    SKIP_SUSPICION_THRESHOLD,
    parse_rendered_max_suspicion,
)
from eval.accusation_calibration import (
    AccusationCalibrationReport,
    compute_accusation_calibration,
)
from eval.alibi_fabrication import (
    AlibiFabricationReport,
    compute_alibi_fabrication_rate,
)
from eval.cost_dashboard import CostDashboard, compute_cost_dashboard
from eval.report_schema import GameReport, TournamentReport
from eval.vote_correctness import VoteCorrectnessReport, compute_vote_correctness
from meetings.manager import INVALID_VOTE_TARGET_MARKER
from meetings.schemas import AccusationClaim, PlayerId

# The literal prefix (the marker text minus the ``{target!r}`` placeholder) the
# meeting layer stamps onto ``rationale_text`` when it normalizes a ballot's
# hallucinated out-of-roster target to SKIP. Matching the prefix identifies a
# by-design coercion regardless of the (quoted) id that follows, mirroring the
# audit extractor's use of the same pinned literal.
_INVALID_VOTE_MARKER_PREFIX: Final[str] = INVALID_VOTE_TARGET_MARKER.split(
    "{target!r}"
)[0]


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
    * ``skipped_meetings`` / ``ejected_meetings`` — the OUTCOME breakdown
      (``MeetingOutcome`` is binary: every meeting either ejected a player or
      skipped), which also partitions exactly into ``meetings_total``. This is
      the pairing the audit (F-F-5 / gp-7) asks for: ``meeting_rate`` measures
      "a game *reached* a meeting", which overstates "the meeting *did
      something*" when most meetings skip (88% SKIP in the audited set). A
      reader gates on ``meeting_rate`` for the Stage-A enablement floor but
      reads ``ejected_meetings`` / ``skipped_meetings`` to judge whether those
      meetings actually resolved anything.

    **Trigger breakdown is authoritative (engine-recorded).** The real trigger
    kind (body-report vs emergency-button) originates on the per-tick
    :class:`engine.events.MeetingTriggeredEvent`. It is not stored on the
    persisted meeting replay row, so the loader
    (:func:`eval.balance_eval._meeting_report_from_entry`) recovers it from the
    ``report`` / ``emergency`` action recorded in the trigger tick's per-tick
    replay row and stamps it onto :attr:`~eval.report_schema.MeetingReport.trigger`.
    This metric then counts ``body_report_meetings`` as the meetings whose
    ``trigger == "report"`` and ``emergency_meetings`` as the complement. The
    breakdown therefore matches the engine exactly — ``emergency_meetings`` is a
    positively-identified emergency-button count, NOT the old catch-all that
    leaked mislabeled body-reports (which derived the kind from the agent's
    self-reported ``FoundBodyObservation`` and so over-counted emergencies). A
    meeting whose trigger action is missing is a corrupt/truncated replay and is
    fail-loud in the loader, never silently bucketed (AGENTS.md "no silent
    fallbacks"). Replacing this loader-side reconstruction with a trigger kind
    persisted directly on the replay row (so it self-describes) is the deferred
    Option-B follow-up, only worthwhile once emergency-button play is revived.

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
    skipped_meetings: int
    ejected_meetings: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> MeetingRateReport:
        counts = (
            self.games_total,
            self.games_with_meeting,
            self.meetings_total,
            self.body_report_meetings,
            self.emergency_meetings,
            self.skipped_meetings,
            self.ejected_meetings,
        )
        if any(count < 0 for count in counts):
            raise ValueError("meeting-rate counts must be non-negative")
        if self.body_report_meetings + self.emergency_meetings != self.meetings_total:
            raise ValueError(
                "body_report_meetings + emergency_meetings must equal "
                f"meetings_total: {self.body_report_meetings} + "
                f"{self.emergency_meetings} != {self.meetings_total}"
            )
        if self.skipped_meetings + self.ejected_meetings != self.meetings_total:
            raise ValueError(
                "skipped_meetings + ejected_meetings must equal "
                f"meetings_total: {self.skipped_meetings} + "
                f"{self.ejected_meetings} != {self.meetings_total}"
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
    ``meetings_total`` sums their lengths. The trigger breakdown reads each
    meeting's engine-recorded ``trigger`` directly (``body_report_meetings`` =
    ``trigger == "report"``, ``emergency_meetings`` the complement); see the
    :class:`MeetingRateReport` docstring for why that field is authoritative
    rather than a derived heuristic. The outcome breakdown
    (``ejected_meetings`` / ``skipped_meetings``) counts each meeting's
    ``outcome`` directly (``MeetingOutcome`` is binary, so ``skipped`` is the
    complement of ``ejected``) — the pairing that distinguishes "reached a
    meeting" from "the meeting resolved anything". ``meeting_rate`` is ``None``
    when ``games_total == 0``. This metric is pure over the report; a corrupt
    replay whose meeting has no recorded trigger action is rejected upstream in
    the loader (:func:`eval.balance_eval._meeting_report_from_entry`), so every
    ``MeetingReport`` reaching here already carries a valid ``trigger``.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    games_total = len(games)
    games_with_meeting = sum(1 for game in games if game.meetings)
    meetings_total = sum(len(game.meetings) for game in games)
    body_report_meetings = sum(
        1 for game in games for meeting in game.meetings if meeting.trigger == "report"
    )
    emergency_meetings = meetings_total - body_report_meetings
    ejected_meetings = sum(
        1 for game in games for meeting in game.meetings if meeting.outcome == "EJECTED"
    )
    skipped_meetings = meetings_total - ejected_meetings
    meeting_rate = games_with_meeting / games_total if games_total > 0 else None

    return MeetingRateReport(
        games_total=games_total,
        games_with_meeting=games_with_meeting,
        meeting_rate=meeting_rate,
        meetings_total=meetings_total,
        body_report_meetings=body_report_meetings,
        emergency_meetings=emergency_meetings,
        skipped_meetings=skipped_meetings,
        ejected_meetings=ejected_meetings,
    )


class ConversionReport(BaseModel):
    """Wave-1 conversion leads + SKIP sentinels (Task 9.6; DESIGN.md §11.3, §5.5).

    Frozen value object publishing the metric surface a Wave-1 conversion A/B
    gates on (audit audit-2026-06-09-0347 gp-2). Wave 1 changes BOTH conversion
    failure surfaces of the detector pipeline, so a lead is named for each:

    * **PRECISION lead — ``ejection_accuracy``** = ``impostor_ejections /
      total_ejections`` over ALL well-formed ejections (the denominator the
      tautological ``vote_correctness_rate`` silently drops; see
      :mod:`eval.vote_correctness` for why that rate is a bug-sentinel, not a
      KPI). ``None`` (undefined, not ``0.0``) when there were no ejections.
      The three precision fields are MIRRORED from the owning
      :class:`~eval.vote_correctness.VoteCorrectnessReport` — same numbers,
      surfaced here so both leads read from one block — never recomputed.
    * **RECALL lead — ``impostor_accused_conversion_rate``** =
      ``impostor_accused_conversions / impostor_accused_meetings``: of the
      meetings whose recorded transcript verbally accused a true impostor
      (>= 1 :class:`~meetings.schemas.AccusationClaim` naming a player whose
      ground-truth role is ``IMPOSTOR``), how many converted the accusation
      into an impostor ejection (gp-1b's measurable target; 21/47 = 0.45 on
      the audited 9.5 baseline). ``None`` (undefined, not ``0.0``) when no
      meeting accused a true impostor.

    plus the SKIP-ballot sentinels over the rendered §4.6 gate verdict
    (:mod:`eval._suspicion_parse`):

    * ``skip_ballots`` partitions exactly into ``correct_skip_ballots``
      (rendered max suspicion over the LIVING ejection targets was below
      :data:`~eval._suspicion_parse.SKIP_SUSPICION_THRESHOLD`),
      ``missed_skip_ballots`` (rendered max met the threshold yet the voter
      SKIPped), and ``unclassified_skip_ballots`` (no rendered gate line was
      found for the voter — older prompt version or missing vote call).
    * ``missed_skip_ballots`` is a **SENTINEL, not a down-is-good metric**:
      it partitions exactly into ``missed_skip_firewall_coercions`` (the
      voter is an impostor whose ballot the teammate firewall coerced to
      SKIP — by-design protection, not an error),
      ``missed_skip_invalid_target`` (a hallucinated out-of-roster target
      normalized to SKIP, identified by the pinned
      :data:`~meetings.manager.INVALID_VOTE_TARGET_MARKER` audit trail), and
      ``threshold_inversions`` (the genuine remainder). On the audited 9.5
      baseline the partition is 38 = 34 firewall + 4 invalid-target + 0
      genuine — driving the count down would mostly mean breaking the
      firewall, so read the partition, not the total.
    * ``threshold_inversions`` is the **§4.6 gate-obedience (firewall)
      sentinel**: a crew voter shown a met threshold over a living target who
      SKIPped anyway with no by-design excuse. Expected ~0 on a clean
      baseline; a nonzero count is a gate-render/obedience bug to chase, NOT
      a conversion knob to optimize (the old facts-only name read as "the
      model obeyed the verdict", audit F-F-5).

    **Leak-safety.** Every field is a pure aggregate (two rates and eleven
    integers). The report carries no roles, no transcripts, and no
    engine-owned types, so it adds no leak risk to the
    ``/eval/tournament-report`` surface (``tests/api/test_leak.py``).

    The post-init validator enforces the partition invariants fail-loud so an
    inconsistent result can never be constructed (mirrors
    :class:`MeetingRateReport`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_ejections: int
    impostor_ejections: int
    ejection_accuracy: float | None
    impostor_accused_meetings: int
    impostor_accused_conversions: int
    impostor_accused_conversion_rate: float | None
    skip_ballots: int
    correct_skip_ballots: int
    missed_skip_ballots: int
    unclassified_skip_ballots: int
    missed_skip_firewall_coercions: int
    missed_skip_invalid_target: int
    threshold_inversions: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> ConversionReport:
        counts = (
            self.total_ejections,
            self.impostor_ejections,
            self.impostor_accused_meetings,
            self.impostor_accused_conversions,
            self.skip_ballots,
            self.correct_skip_ballots,
            self.missed_skip_ballots,
            self.unclassified_skip_ballots,
            self.missed_skip_firewall_coercions,
            self.missed_skip_invalid_target,
            self.threshold_inversions,
        )
        if any(count < 0 for count in counts):
            raise ValueError("conversion counts must be non-negative")
        if self.impostor_ejections > self.total_ejections:
            raise ValueError(
                "impostor_ejections cannot exceed total_ejections: "
                f"{self.impostor_ejections} > {self.total_ejections}"
            )
        if self.impostor_accused_conversions > self.impostor_accused_meetings:
            raise ValueError(
                "impostor_accused_conversions cannot exceed "
                f"impostor_accused_meetings: {self.impostor_accused_conversions} "
                f"> {self.impostor_accused_meetings}"
            )
        skip_parts = (
            self.correct_skip_ballots
            + self.missed_skip_ballots
            + self.unclassified_skip_ballots
        )
        if skip_parts != self.skip_ballots:
            raise ValueError(
                "correct + missed + unclassified skip ballots must equal "
                f"skip_ballots: {self.correct_skip_ballots} + "
                f"{self.missed_skip_ballots} + {self.unclassified_skip_ballots} "
                f"!= {self.skip_ballots}"
            )
        missed_parts = (
            self.missed_skip_firewall_coercions
            + self.missed_skip_invalid_target
            + self.threshold_inversions
        )
        if missed_parts != self.missed_skip_ballots:
            raise ValueError(
                "firewall + invalid-target + inversions must equal "
                f"missed_skip_ballots: {self.missed_skip_firewall_coercions} + "
                f"{self.missed_skip_invalid_target} + {self.threshold_inversions} "
                f"!= {self.missed_skip_ballots}"
            )
        self._validate_rate(
            "ejection_accuracy", self.ejection_accuracy, self.total_ejections
        )
        self._validate_rate(
            "impostor_accused_conversion_rate",
            self.impostor_accused_conversion_rate,
            self.impostor_accused_meetings,
        )
        return self

    @staticmethod
    def _validate_rate(name: str, rate: float | None, denominator: int) -> None:
        """Enforce the shared None-iff-undefined rate contract (not-0.0)."""

        if denominator == 0:
            if rate is not None:
                raise ValueError(
                    f"{name} must be None when its denominator is zero: the "
                    "rate is undefined, not 0.0"
                )
        else:
            if rate is None:
                raise ValueError(f"{name} must be set when its denominator > 0")
            if not 0.0 <= rate <= 1.0:
                raise ValueError(f"{name} must be in [0.0, 1.0]: {rate}")


def compute_conversion_report(
    report: TournamentReport | Sequence[GameReport],
    *,
    vote_correctness: VoteCorrectnessReport | None = None,
) -> ConversionReport:
    """Fold a tournament report (or game sequence) into the conversion summary.

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the other
    analyzers' signature). Pure: no I/O, no engine/agent/LLM calls.

    ``vote_correctness`` is the already-computed
    :class:`~eval.vote_correctness.VoteCorrectnessReport` over the SAME games,
    threaded in by :func:`build_tournament_eval_report` so the precision-lead
    fields are mirrored from the owning metric rather than recomputed; when
    omitted it is computed here via the owning module's public
    :func:`~eval.vote_correctness.compute_vote_correctness`.

    The RECALL lead folds each meeting's recorded transcript: a meeting counts
    as ``impostor_accused`` when any turn carries an
    :class:`~meetings.schemas.AccusationClaim` whose target's ground-truth
    role is ``IMPOSTOR`` (subscript on ``roles`` — an accusation target absent
    from the ground truth is malformed and fails loud, matching
    :mod:`eval.accusation_calibration`). Self-accusations count: an impostor
    naming themselves still puts a true impostor's name on the table, and the
    meeting layer already drops hallucinated / non-living targets at record
    time, so every recorded claim names a live participant. The meeting
    converts when its outcome is a well-formed ``EJECTED`` of an impostor (a
    malformed ``EJECTED`` row with no ``ejected_player_id`` cannot convert,
    mirroring the vote-correctness partial-replay rule).

    The SKIP sentinels classify each SKIP ballot against the voter's rendered
    §4.6 gate verdict, recovered from the meeting's vote-prompt LLM calls by
    the shared :func:`eval._suspicion_parse.parse_rendered_max_suspicion`
    (the voter's per-ballot gate input survives nowhere else; the rendered
    max is computed over LIVING ejection candidates by construction — the
    template filters ``candidate_targets``). A voter with no parsed gate line
    is ``unclassified``, never assumed correct. MISSED ballots partition
    firewall-first: an impostor voter is a firewall coercion regardless of
    any invalid-target marker (the firewall is the stronger by-design cause),
    then invalid-target normalizations, then the genuine
    ``threshold_inversions`` remainder.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)
    if vote_correctness is None:
        vote_correctness = compute_vote_correctness(games)

    impostor_accused_meetings = 0
    impostor_accused_conversions = 0
    skip_ballots = 0
    correct_skip_ballots = 0
    missed_skip_ballots = 0
    unclassified_skip_ballots = 0
    missed_skip_firewall_coercions = 0
    missed_skip_invalid_target = 0
    threshold_inversions = 0

    for game in games:
        for meeting in game.meetings:
            # RECALL lead: did the meeting verbally accuse a true impostor,
            # and did it convert that into an impostor ejection?
            accused_true_impostor = any(
                isinstance(claim, AccusationClaim)
                and game.roles[claim.against] == "IMPOSTOR"
                for turn in meeting.transcript.turns
                for claim in turn.claims
            )
            if accused_true_impostor:
                impostor_accused_meetings += 1
                ejected = meeting.ejected_player_id
                if (
                    meeting.outcome == "EJECTED"
                    and ejected is not None
                    and game.roles[ejected] == "IMPOSTOR"
                ):
                    impostor_accused_conversions += 1

            # SKIP sentinels: recover each voter's rendered §4.6 gate verdict
            # from the meeting's vote-prompt calls. A voter can have both a
            # turn call and a vote call; only the vote call carries the line,
            # so non-vote prompts parse to None and never overwrite.
            rendered_max_by_voter: dict[PlayerId, float] = {}
            for call in meeting.llm_calls:
                if call.agent_id is None:
                    continue
                rendered = parse_rendered_max_suspicion(call.prompt)
                if rendered is not None:
                    rendered_max_by_voter[call.agent_id] = rendered
            for ballot in meeting.ballots:
                if ballot.target != "SKIP":
                    continue
                skip_ballots += 1
                rendered_max = rendered_max_by_voter.get(ballot.voter)
                if rendered_max is None:
                    unclassified_skip_ballots += 1
                elif rendered_max < SKIP_SUSPICION_THRESHOLD:
                    correct_skip_ballots += 1
                else:
                    missed_skip_ballots += 1
                    if game.roles[ballot.voter] == "IMPOSTOR":
                        missed_skip_firewall_coercions += 1
                    elif _INVALID_VOTE_MARKER_PREFIX in ballot.rationale_text:
                        missed_skip_invalid_target += 1
                    else:
                        threshold_inversions += 1

    conversion_rate = (
        impostor_accused_conversions / impostor_accused_meetings
        if impostor_accused_meetings > 0
        else None
    )

    return ConversionReport(
        total_ejections=vote_correctness.total_ejections,
        impostor_ejections=vote_correctness.impostor_ejections,
        ejection_accuracy=vote_correctness.ejection_accuracy,
        impostor_accused_meetings=impostor_accused_meetings,
        impostor_accused_conversions=impostor_accused_conversions,
        impostor_accused_conversion_rate=conversion_rate,
        skip_ballots=skip_ballots,
        correct_skip_ballots=correct_skip_ballots,
        missed_skip_ballots=missed_skip_ballots,
        unclassified_skip_ballots=unclassified_skip_ballots,
        missed_skip_firewall_coercions=missed_skip_firewall_coercions,
        missed_skip_invalid_target=missed_skip_invalid_target,
        threshold_inversions=threshold_inversions,
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
    :data:`~eval.report_schema.CURRENT_FORMAT_VERSION` is NOT bumped. The Task
    9.6 ``conversion`` block follows the same rule: a wrapper-level aggregate
    over the unchanged inner report, so the version stays 2 (DESIGN.md §11.4
    bumps it only when older readers cannot interpret the shape).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    report: TournamentReport
    vote_correctness: VoteCorrectnessReport
    accusation_calibration: AccusationCalibrationReport
    alibi_fabrication: AlibiFabricationReport
    cost_dashboard: CostDashboard
    meeting_rate: MeetingRateReport
    conversion: ConversionReport


def build_tournament_eval_report(report: TournamentReport) -> TournamentEvalReport:
    """Run the §11.3 + W0.3 analyzers over ``report`` and wrap the results.

    Pure assembly: each metric is computed by its own public ``compute_*``
    entry point over the same :class:`~eval.report_schema.TournamentReport`, and
    the results are packed into a :class:`TournamentEvalReport`. No metric math
    is reimplemented here — this function only orchestrates the analyzers
    (including :func:`compute_meeting_rate` and
    :func:`compute_conversion_report`) and bundles their outputs with the
    source report; it never re-derives a count inline. The vote-correctness
    result is computed once and threaded into the conversion analyzer so its
    mirrored precision-lead fields come from the same fold.
    """

    vote_correctness = compute_vote_correctness(report)
    return TournamentEvalReport(
        report=report,
        vote_correctness=vote_correctness,
        accusation_calibration=compute_accusation_calibration(report),
        alibi_fabrication=compute_alibi_fabrication_rate(report),
        cost_dashboard=compute_cost_dashboard(report),
        meeting_rate=compute_meeting_rate(report),
        conversion=compute_conversion_report(report, vote_correctness=vote_correctness),
    )


__all__ = [
    "ConversionReport",
    "MeetingRateReport",
    "TournamentEvalReport",
    "build_tournament_eval_report",
    "compute_conversion_report",
    "compute_meeting_rate",
]
