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

Phase 10 Wave 0 (Task 10.4, gate metrics) adds a seventh, the Phase-10 A/B
ruler defined in this module:

* *Gate metrics* — the Phase-10 gate surface specified by audit
  audit-2026-06-10-1820 gp-7 (:func:`compute_gate_metrics` /
  :class:`GateMetricsReport`): the genuine-class conversion pair (the
  phase's PRIMARY progress gate, computed by the owning
  :func:`eval.vote_correctness.compute_genuine_class_conversion`), the
  lost-opening-accusation count split from cap-defaulted turns (H-H-5 vs
  H-H-2 — different causes, same chain-killing symptom, so an A/B must read
  them separately), and accused-impostor survival partitioned by the
  rendered §4.6 verdict (D-D-2) so Wave-2 deception claims are
  conversion-controlled from day one. The win split is deliberately NOT on
  this surface: it is a constant of the race structure (~90/10, zero
  ejection-driven wins, B-B-1) and gates nothing.

Phase 10 Wave 1 (Task 10.6, gate spec) adds the gp-7 companions defined in
this module (audit audit-2026-06-11-2218 C-C-6):

* *Multi-signal conversion* — impostor ejections whose rendered pre-vote
  lift decomposes into 2+ distinct §6.3 design channels over the quantized
  rule lattice (:func:`compute_multi_signal_conversion` /
  :class:`MultiSignalConversionReport`; per-ejection decomposition via
  :func:`decompose_ejection_channels`). The genuine-class ruler credited 1
  of the Wave-0 set's 5 real conversions; the intended multi-signal
  pipeline produced the other 4 invisibly.
* *Supply gauges* — the evidence-supply context (re-derived flag census,
  zero-contradiction share, genuine-subject share, flag-subject role split,
  over-gate listeners per accused-impostor meeting)
  (:func:`compute_supply_gauges` / :class:`SupplyGaugesReport`).

Neither joins :class:`TournamentEvalReport` yet: the committed Wave-0
sample reports stay single-era (no regeneration without a re-record), so
the report builder publishes both and the corrected Wave-0 baseline
fixture (``tests/fixtures/phase10/corrected_w0_baseline.json``) is their
committed home until the 10.9 re-record.

Phase 10 Wave 1 repair (Task 10.9.1, PR #147 F1) extends the SKIP
partition with a DEFAULTED class in this module:

* *Defaulted-ballot census* — the ballots the meeting layer's vote
  fail-soft degraded to SKIP, keyed on
  :data:`~meetings.manager.VOTE_PARSE_DEFAULT_MARKER` and split by the
  rendered §4.6 verdict (:func:`compute_defaulted_ballots` /
  :class:`DefaultedBallotReport`). The decision census in
  :func:`compute_conversion_report` diverts these ballots (a degraded
  SKIP is never a missed skip and never a threshold inversion); like the
  Task 10.6 metrics this surface stays off the frozen
  :class:`TournamentEvalReport` wrapper until the 10.9 re-record.

Phase 10 Wave 1 repair (Task 10.9.2, PR #147 F2) adds the redirect
census in this module:

* *Ballot-target redirect census* — the eject ballots the meeting
  layer's ballot-target graph guard rewrote because their target carried
  no over-gate rendered row under a MUST-vote verdict, keyed on
  :data:`~meetings.manager.BALLOT_TARGET_REDIRECT_MARKER` and split by
  the guard's outcome (:func:`compute_ballot_target_redirects` /
  :class:`BallotTargetRedirectReport`), published beside the
  invalid-target and teammate-coercion counts. Recorded ballots are
  post-guard, so the gp-7 channel decomposition
  (:func:`decompose_ejection_channels`) and every graph-consistency read
  over ballots / ejections see the REDIRECTED target by construction —
  the seed-12 unattributed-impostor-ejection class is structurally
  impossible on post-guard recordings. Same single-era rule: off the
  frozen wrapper until the 10.9 re-record.

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

import re
from collections.abc import Sequence
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from agents.memory.beliefs import (
    ACCUSATION_SUSPICION_DELTA,
    VENTING_SUSPICION_DELTA,
    BeliefState,
    apply_contradiction_rule,
)
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
from eval.report_schema import GameReport, MeetingReport, TournamentReport
from eval.vote_correctness import (
    GenuineClassConversionReport,
    VoteCorrectnessReport,
    compute_genuine_class_conversion,
    compute_vote_correctness,
    genuine_class_subjects,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
)
from meetings.schemas import AccusationClaim, PlayerId
from meetings.transcript import detect_contradictions, is_weak_contradiction

# The literal prefixes (the marker text minus the ``{target!r}`` placeholder)
# the meeting layer stamps onto ``rationale_text`` when it normalizes a
# ballot: a hallucinated out-of-roster target rewritten to SKIP, and a
# teammate-betrayal target the §7.12 guard
# (:func:`meetings.manager.coerce_teammate_ballot_to_skip`) coerced to SKIP.
# Matching the prefix identifies the by-design rewrite regardless of the
# (quoted) id that follows, mirroring the audit extractor's use of the same
# pinned literals.
_INVALID_VOTE_MARKER_PREFIX: Final[str] = INVALID_VOTE_TARGET_MARKER.split(
    "{target!r}"
)[0]
_TEAMMATE_VOTE_MARKER_PREFIX: Final[str] = TEAMMATE_VOTE_TARGET_MARKER.split(
    "{target!r}"
)[0]
# The Task 10.9.1 parse-default marker prefix (the text minus the
# ``{head!r}`` placeholder): the manager's vote fail-soft stamps it as the
# WHOLE ``rationale_text`` of a ballot that degraded to SKIP after its
# completion failed schema validation (PR #147 F1, the seed-8
# vote-truncation abort). The prefix keys the DEFAULTED class of the SKIP
# partition below.
_VOTE_PARSE_DEFAULT_MARKER_PREFIX: Final[str] = VOTE_PARSE_DEFAULT_MARKER.split(
    "{head!r}"
)[0]
# The Task 10.9.2 ballot-target redirect marker prefix (the text minus the
# ``{target!r}`` placeholder): the manager's ballot-target graph guard
# stamps it onto a ballot whose eject target carried no over-gate rendered
# row under a MUST-vote verdict (PR #147 F2, the seed-12 m0 unattributed
# ejection). The prefix keys the redirect census below, published beside
# the invalid-target and teammate-coercion counts.
_BALLOT_REDIRECT_MARKER_PREFIX: Final[str] = BALLOT_TARGET_REDIRECT_MARKER.split(
    "{target!r}"
)[0]

# ---------------------------------------------------------------------------
# Task 10.4 gate-metric parses (ported from the audit extractor's derivations,
# audits/workflows/extract_gameplay_facts.py — the gp-7 instruction is to ship
# those derivations here so later waves read them off the report instead of
# re-deriving operator-inline).
# ---------------------------------------------------------------------------

# The §6.6 vote prompt renders the voter's OWN suspicion graph under a
# "## Your suspicion graph" header, one row per known player:
#
#     ## Your suspicion graph
#     - `p-2`: suspicion 0.70, trust 0.50- `p-6`: suspicion 0.78, trust 0.50
#
# This is the only place a per-TARGET (not just the per-voter max) §4.6
# suspicion value survives into the replay, so the deception-control split
# reads an accused impostor's rendered suspicion off the OTHER voters' graph
# rows (a voter holds no row about itself). Both literals are produced by the
# committed ``vote_ballot.j2`` template; the row regex pins the production
# ``p-{n}`` id shape, so a non-roster garbage row (audit C-C-8) can never
# match. The per-voter MAX line stays the shared
# :mod:`eval._suspicion_parse` parse — this block adds only the per-target
# graph read that parse does not cover.
_SUSPICION_GRAPH_HEADER: Final[str] = "## Your suspicion graph"
_SUSPICION_GRAPH_ROW_RE: Final[re.Pattern[str]] = re.compile(
    r"`(?P<pid>p-\d+)`: suspicion (?P<sus>[0-9]*\.?[0-9]+), "
    r"trust (?P<trust>[0-9]*\.?[0-9]+)"
)

# A defaulted-turn ``deadline_default`` failed-call row carries the turn
# coordinates in its ``error_message``, written by
# ``orchestrator.game._default_error_message``: "reply turn (turn 1)
# defaulted (validation); p-9 submitted no turn ...". A defaulted VOTE
# writes "vote defaulted (...); p-9 submitted no ballot" instead and is NOT
# a cap-defaulted turn. Counting distinct parsed coordinates (rather than
# raw rows) keeps the count stable even if a single default ever writes
# multiple rows again (the pre-9.10 duplicate shape, or one row per burned
# parse-failure call).
_DEFAULTED_TURN_RE: Final[re.Pattern[str]] = re.compile(
    r"(?P<kind>opening|reply|opt_in) turn \(turn (?P<index>\d+)\) defaulted"
    r"[^;]*;\s*(?P<speaker>\S+) submitted no turn"
)
_DEFAULTED_VOTE_PREFIX: Final[str] = "vote defaulted"


def _parse_suspicion_graph(prompt: str) -> dict[PlayerId, float]:
    """Return ``{player_id: rendered_suspicion}`` from a vote prompt's graph.

    Empty when the prompt carries no ``## Your suspicion graph`` section (a
    voter with no beliefs about anyone, or a non-vote prompt). The block ends
    at the next ``## `` header. See the constants above for why this parse
    lives here.
    """

    if _SUSPICION_GRAPH_HEADER not in prompt:
        return {}
    after = prompt.split(_SUSPICION_GRAPH_HEADER, 1)[1]
    block = after.split("## ", 1)[0]
    return {
        match.group("pid"): float(match.group("sus"))
        for match in _SUSPICION_GRAPH_ROW_RE.finditer(block)
    }


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
      Task 10.9.1 narrows the census to voter DECISIONS: a SKIP stamped with
      the parse-default marker
      (:data:`~meetings.manager.VOTE_PARSE_DEFAULT_MARKER`, the manager's
      vote fail-soft over an unparseable completion — PR #147 F1) enters
      these buckets only when it coincides with a correct skip; under a
      MUST-vote render or with no rendered verdict it is DIVERTED to the
      standalone :class:`DefaultedBallotReport` census instead, so a
      degraded SKIP can never read as a missed skip or a genuine
      ``threshold_inversions`` entry.
    * ``missed_skip_ballots`` is a **SENTINEL, not a down-is-good metric**:
      it partitions exactly into ``missed_skip_impostor_voters`` (the voter
      is an impostor — the audited exclusion class: impostor in-character
      voting is sanctioned by the vote prompt, so a met-threshold SKIP by an
      impostor is adversarial play / teammate protection by design, never a
      crew gate bug), ``missed_skip_invalid_target`` (a hallucinated
      out-of-roster target normalized to SKIP, identified by the pinned
      :data:`~meetings.manager.INVALID_VOTE_TARGET_MARKER` audit trail), and
      ``threshold_inversions`` (the genuine remainder). On the audited 9.5
      baseline the partition is 38 = 34 impostor-voter + 4 invalid-target +
      0 genuine — driving the count down would mostly mean breaking impostor
      play, so read the partition, not the total.
    * ``missed_skip_teammate_coerced`` annotates the impostor bucket (a
      sub-count, NOT a fourth partition bucket): how many of those missed
      skips carry the pinned
      :data:`~meetings.manager.TEAMMATE_VOTE_TARGET_MARKER` — i.e. the §7.12
      output guard (:func:`meetings.manager.coerce_teammate_ballot_to_skip`)
      actually rewrote a recorded betrayal ballot, as opposed to the model
      declining on its own. It is 0 on the audited 9.5 baseline: the guard
      never fired there — every impostor missed skip was a voluntary
      in-character decline — so this count is what keeps deterministic
      coercions and voluntary declines from being fused under one number in
      a later A/B.
    * ``threshold_inversions`` is the **§4.6 gate-obedience (firewall)
      sentinel**, scoped to CREW voters: a crew voter shown a met threshold
      over a living target who SKIPped anyway with no by-design excuse.
      Expected ~0 on a clean baseline; a nonzero count is a
      gate-render/obedience bug to chase, NOT a conversion knob to optimize
      (the old facts-only name read as "the model obeyed the verdict", audit
      F-F-5).

    **Leak-safety.** Every field is a pure aggregate (two rates and twelve
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
    missed_skip_impostor_voters: int
    missed_skip_teammate_coerced: int
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
            self.missed_skip_impostor_voters,
            self.missed_skip_teammate_coerced,
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
            self.missed_skip_impostor_voters
            + self.missed_skip_invalid_target
            + self.threshold_inversions
        )
        if missed_parts != self.missed_skip_ballots:
            raise ValueError(
                "impostor-voter + invalid-target + inversions must equal "
                f"missed_skip_ballots: {self.missed_skip_impostor_voters} + "
                f"{self.missed_skip_invalid_target} + {self.threshold_inversions} "
                f"!= {self.missed_skip_ballots}"
            )
        # The coerced count annotates the impostor bucket (a marker-verified
        # subset), so it can never exceed it.
        if self.missed_skip_teammate_coerced > self.missed_skip_impostor_voters:
            raise ValueError(
                "missed_skip_teammate_coerced cannot exceed "
                f"missed_skip_impostor_voters: {self.missed_skip_teammate_coerced} "
                f"> {self.missed_skip_impostor_voters}"
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
    template filters ``candidate_targets``). A parse-DEFAULTED skip (Task
    10.9.1: the ``VOTE_PARSE_DEFAULT_MARKER``-stamped fail-soft ballot) is
    counted here only as a correct skip under a MUST-skip render; otherwise
    it is diverted to :func:`compute_defaulted_ballots` (see the
    :class:`ConversionReport` docstring). A voter with no parsed gate line
    is ``unclassified``, never assumed correct. MISSED ballots partition
    role-first: an impostor voter lands in ``missed_skip_impostor_voters``
    regardless of any normalization marker (the audited exclusion class —
    impostor in-character voting is sanctioned by the vote prompt, so it is
    never a crew gate bug), then invalid-target normalizations, then the
    genuine ``threshold_inversions`` remainder. Within the impostor bucket,
    ballots stamped with the §7.12
    :data:`~meetings.manager.TEAMMATE_VOTE_TARGET_MARKER` are additionally
    counted as ``missed_skip_teammate_coerced`` — the guard-rewritten
    betrayal ballots, as opposed to the model declining on its own — so the
    two by-design causes stay separately measurable.
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
    missed_skip_impostor_voters = 0
    missed_skip_teammate_coerced = 0
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
                rendered_max = rendered_max_by_voter.get(ballot.voter)
                # DEFAULTED diversion (Task 10.9.1; PR #147 F1): a SKIP
                # stamped with the parse-default marker is the manager's
                # fail-soft net, never the voter's decision, so it enters
                # this decision census only when it coincides with a
                # correct skip -- under a MUST-skip render the recorded
                # SKIP complies with the verdict and counts correct as
                # ever. Under a MUST-vote render, or with no rendered
                # verdict at all (a REAL provider's failed call raises
                # before the recording client logs its prompt), the ballot
                # is censused by :func:`compute_defaulted_ballots` instead:
                # NEVER a missed skip and NEVER a threshold inversion -- a
                # degraded SKIP miscounted as a genuine inversion would
                # poison the §4.6 0-inversion HARD line on the very
                # re-record the fail-soft exists to unblock.
                if _VOTE_PARSE_DEFAULT_MARKER_PREFIX in ballot.rationale_text and (
                    rendered_max is None or rendered_max >= SKIP_SUSPICION_THRESHOLD
                ):
                    continue
                skip_ballots += 1
                if rendered_max is None:
                    unclassified_skip_ballots += 1
                elif rendered_max < SKIP_SUSPICION_THRESHOLD:
                    correct_skip_ballots += 1
                else:
                    missed_skip_ballots += 1
                    if game.roles[ballot.voter] == "IMPOSTOR":
                        missed_skip_impostor_voters += 1
                        if _TEAMMATE_VOTE_MARKER_PREFIX in ballot.rationale_text:
                            missed_skip_teammate_coerced += 1
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
        missed_skip_impostor_voters=missed_skip_impostor_voters,
        missed_skip_teammate_coerced=missed_skip_teammate_coerced,
        missed_skip_invalid_target=missed_skip_invalid_target,
        threshold_inversions=threshold_inversions,
    )


class DefaultedBallotReport(BaseModel):
    """The DEFAULTED extension of the SKIP partition (Task 10.9.1; PR #147 F1).

    Frozen value object censusing the ballots the meeting layer's vote
    fail-soft degraded to SKIP -- keyed on the pinned
    :data:`~meetings.manager.VOTE_PARSE_DEFAULT_MARKER` -- split by the
    voter's rendered §4.6 verdict, reported beside the coerced/missed
    counts so the two by-design SKIP rewrites (teammate coercion, parse
    default) stay separately measurable:

    * ``defaulted_skip_ballots`` -- every marker-bearing SKIP ballot (the
      census headline; partitions exactly into the three buckets below).
    * ``defaulted_under_must_vote`` -- the rendered max met the threshold
      (the verdict read MUST vote). The DoD class: such a ballot is the
      system's net over an unparseable response, NEVER a genuine
      ``threshold_inversions`` entry and never a silent
      ``missed_skip_ballots`` entry -- :func:`compute_conversion_report`
      diverts it out of the decision census entirely, because a degraded
      SKIP miscounted as an inversion would poison the §4.6 0-inversion
      HARD line.
    * ``defaulted_under_must_skip`` -- the rendered max was below the
      threshold, so the degraded SKIP coincides with the correct decision:
      it stays a ``correct_skip_ballots`` entry in the decision census and
      appears here as telemetry only (the one deliberate overlap between
      the two surfaces).
    * ``defaulted_without_render`` -- no rendered gate line was recovered
      for the voter. This is the common REAL-provider shape: a provider
      that validates internally raises before the recording client can
      log the vote call, so the prompt (and its rendered verdict) never
      reaches ``llm_calls`` -- the marker is then the only witness, which
      is why the bucket is keyed on it rather than left to drown in
      ``unclassified_skip_ballots``.

    Like the Task 10.6 gate-spec metrics this does NOT join
    :class:`TournamentEvalReport` yet: the committed sample reports stay
    single-era (no regeneration without a re-record), so
    :class:`ConversionReport`'s serialized shape is frozen and this
    surface ships standalone until the 10.9 re-record turns the era over.

    **Leak-safety.** Four integers; no roles, transcripts, or engine-owned
    types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    defaulted_skip_ballots: int
    defaulted_under_must_vote: int
    defaulted_under_must_skip: int
    defaulted_without_render: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> DefaultedBallotReport:
        counts = (
            self.defaulted_skip_ballots,
            self.defaulted_under_must_vote,
            self.defaulted_under_must_skip,
            self.defaulted_without_render,
        )
        if any(count < 0 for count in counts):
            raise ValueError("defaulted-ballot counts must be non-negative")
        parts = (
            self.defaulted_under_must_vote
            + self.defaulted_under_must_skip
            + self.defaulted_without_render
        )
        if parts != self.defaulted_skip_ballots:
            raise ValueError(
                "must-vote + must-skip + without-render must equal "
                f"defaulted_skip_ballots: {self.defaulted_under_must_vote} + "
                f"{self.defaulted_under_must_skip} + "
                f"{self.defaulted_without_render} != {self.defaulted_skip_ballots}"
            )
        return self


def compute_defaulted_ballots(
    report: TournamentReport | Sequence[GameReport],
) -> DefaultedBallotReport:
    """Fold a tournament report into the DEFAULTED-ballot census (Task 10.9.1).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the other
    analyzers' signature). Pure: no I/O, no engine/agent/LLM calls.

    A ballot is DEFAULTED iff it is a SKIP carrying the pinned
    :data:`~meetings.manager.VOTE_PARSE_DEFAULT_MARKER` prefix; its bucket
    is the voter's rendered §4.6 verdict, recovered through the same
    :func:`eval._suspicion_parse.parse_rendered_max_suspicion` walk the
    decision census uses, so the two surfaces can never disagree about a
    voter's verdict. Role-blind: the degrade fires on response bytes, not
    on who voted.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    defaulted = 0
    under_must_vote = 0
    under_must_skip = 0
    without_render = 0

    for game in games:
        for meeting in game.meetings:
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
                if _VOTE_PARSE_DEFAULT_MARKER_PREFIX not in ballot.rationale_text:
                    continue
                defaulted += 1
                rendered_max = rendered_max_by_voter.get(ballot.voter)
                if rendered_max is None:
                    without_render += 1
                elif rendered_max >= SKIP_SUSPICION_THRESHOLD:
                    under_must_vote += 1
                else:
                    under_must_skip += 1

    return DefaultedBallotReport(
        defaulted_skip_ballots=defaulted,
        defaulted_under_must_vote=under_must_vote,
        defaulted_under_must_skip=under_must_skip,
        defaulted_without_render=without_render,
    )


class BallotTargetRedirectReport(BaseModel):
    """The ballot-target redirect census (Task 10.9.2; PR #147 F2).

    Frozen value object censusing the ballots the meeting layer's
    ballot-target graph guard
    (:func:`meetings.manager.guard_ballot_target_graph`) rewrote -- keyed
    on the pinned :data:`~meetings.manager.BALLOT_TARGET_REDIRECT_MARKER`
    -- published beside the invalid-target
    (``missed_skip_invalid_target``) and teammate-coercion
    (``missed_skip_teammate_coerced``) counts so every deterministic
    ballot rewrite stays separately measurable:

    * ``redirected_ballots`` -- every marker-bearing ballot (the census
      headline; partitions exactly into the two buckets below).
    * ``redirected_eject_ballots`` -- the recorded target is the guard's
      argmax-rendered eligible candidate (the seed-12 m0 repair shape:
      the under-gate target was rewritten, the ballot still ejects). The
      ballot never enters the SKIP partition, so ``threshold_inversions``
      and ``missed_skip_ballots`` are untouched by construction.
    * ``redirect_coerced_skip_ballots`` -- the eligible pool's max was
      below the gate (an impostor voter whose only over-gate row is a
      teammate) and the ballot coerced to SKIP. Structurally an
      impostor-voter-only shape, so in the decision census it lands in
      ``missed_skip_impostor_voters`` exactly like the §7.12 teammate
      coercion -- by-design play, never a genuine
      ``threshold_inversions`` entry.

    Like the Task 10.9.1 DEFAULTED census this does NOT join
    :class:`TournamentEvalReport` yet: the committed sample reports stay
    single-era (no regeneration without a re-record), so the surface
    ships standalone until the 10.9 re-record turns the era over.

    **Leak-safety.** Three integers; no roles, transcripts, or
    engine-owned types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    redirected_ballots: int
    redirected_eject_ballots: int
    redirect_coerced_skip_ballots: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> BallotTargetRedirectReport:
        counts = (
            self.redirected_ballots,
            self.redirected_eject_ballots,
            self.redirect_coerced_skip_ballots,
        )
        if any(count < 0 for count in counts):
            raise ValueError("ballot-redirect counts must be non-negative")
        parts = self.redirected_eject_ballots + self.redirect_coerced_skip_ballots
        if parts != self.redirected_ballots:
            raise ValueError(
                "eject + coerced-skip must equal redirected_ballots: "
                f"{self.redirected_eject_ballots} + "
                f"{self.redirect_coerced_skip_ballots} != {self.redirected_ballots}"
            )
        return self


def compute_ballot_target_redirects(
    report: TournamentReport | Sequence[GameReport],
) -> BallotTargetRedirectReport:
    """Fold a tournament report into the redirect census (Task 10.9.2).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the other
    analyzers' signature). Pure: no I/O, no engine/agent/LLM calls.

    A ballot is REDIRECTED iff its ``rationale_text`` carries the pinned
    :data:`~meetings.manager.BALLOT_TARGET_REDIRECT_MARKER` prefix; the
    recorded target splits the bucket (an eject kept ejecting at the
    guard's redirect, a SKIP is the coerced teammate-only-over-gate
    shape). Role-blind: the guard fires on the rendered graph, not on who
    voted.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    redirected = 0
    redirected_eject = 0
    coerced_skip = 0

    for game in games:
        for meeting in game.meetings:
            for ballot in meeting.ballots:
                if _BALLOT_REDIRECT_MARKER_PREFIX not in ballot.rationale_text:
                    continue
                redirected += 1
                if ballot.target == "SKIP":
                    coerced_skip += 1
                else:
                    redirected_eject += 1

    return BallotTargetRedirectReport(
        redirected_ballots=redirected,
        redirected_eject_ballots=redirected_eject,
        redirect_coerced_skip_ballots=coerced_skip,
    )


class GateMetricsReport(BaseModel):
    """The Phase-10 A/B gate surface (Task 10.4; DESIGN.md §11.3; audit gp-7).

    Frozen value object publishing the counters the Phase-10 waves gate on,
    so 10.5 and every later wave reads them off the shipped report instead of
    deriving them operator-inline (audit audit-2026-06-10-1820 gp-7: B-B-1,
    C-C-6, D-D-2, H-H-5, H-H-7). The win split is deliberately ABSENT: it is
    a constant of the race structure (~90/10 with zero ejection-driven wins,
    B-B-1) and is excluded from every Phase-10 gate. H-H-7's confidence
    calibration cleared (monotone bins, informative spread), so no
    quantization caveat ships either.

    * ``genuine_class_conversion`` — the phase's PRIMARY progress gate,
      computed by the owning
      :func:`eval.vote_correctness.compute_genuine_class_conversion` (the
      CANON-class definition imports the Task 10.1 detector classifier — one
      home, never a parallel implementation) and carried here so the whole
      gate surface reads from one block. Its ``note`` field documents why
      raw ``ejection_accuracy`` parity with the artifact-era 0.63 is an
      invalid gate.
    * ``lost_opening_accusations`` — meetings whose opening turn carries
      ZERO accusation claims (the chain dies on turn 0: ``chain_length=1``
      SKIP; H-H-5). Counted SEPARATELY from ``cap_defaulted_turns`` —
      different causes, same chain-killing symptom, and a conversion A/B
      that fuses them cannot tell a narration tail from a token-cap
      truncation (5 vs 2 on the audited set, and the seed-23 opening sits
      in both counters by design: it defaulted AND lost its accusation).
    * ``cap_defaulted_turns`` — distinct defaulted turns (opening / reply /
      opt_in), i.e. ``deadline_default`` failed-call rows whose
      ``error_message`` names a turn, deduped on (game, meeting, kind,
      index, speaker); defaulted VOTES are not turns and are excluded. A
      ``deadline_default`` row naming neither a turn nor a vote is foreign
      data and fails loud rather than being silently dropped from the count
      (AGENTS.md "no silent fallbacks").
    * ``accused_impostor_events`` / ``accused_impostor_survivals`` — the
      D-D-2 deception-control denominator: one event per (meeting, living
      true impostor verbally accused by someone else); self-accusations are
      excluded (an impostor naming themselves is not crew pressure —
      deliberately stricter than the recall lead's self-inclusive
      convention, matching the audited 55/45). The impostor SURVIVES unless
      that meeting's well-formed outcome ejected them.
    * The survival partition (``rendered_met`` + ``sheltered_sub_gate`` +
      ``unevidenced`` == ``survivals``) is the deception-vs-under-conversion
      split, classified against the rendered §4.6 suspicion the OTHER
      voters' graph rows carried for the impostor
      (:data:`_SUSPICION_GRAPH_ROW_RE`; threshold =
      :data:`eval._suspicion_parse.SKIP_SUSPICION_THRESHOLD`):

      - ``survivals_rendered_met`` — some voter was shown a met-threshold
        verdict on the impostor yet the table failed to convert. These are
        CREW-conversion failures; reading them as impostor deception is the
        exact misread D-D-2 warns against (32/45 on the audited set).
      - ``survivals_sheltered_sub_gate`` — a rendered row existed, stayed
        below the threshold, AND at least one re-derived detector flag named
        the impostor: their account was actively challenged and the weak
        band genuinely sheltered them. This is the conversion-controlled
        deception-credit count Wave-2 claims must cite (n=1/45 audited:
        seed 8 m1 at 0.58).
      - ``survivals_unevidenced`` — the remainder: no rendered row at all,
        or sub-gate with zero flags. Evidence starvation, not deception.

    **Leak-safety.** Pure aggregates (counts plus the nested genuine-class
    block: two counts, a rate, and a pinned documentation string). No roles,
    no transcripts, no engine-owned types, so the block adds no leak risk to
    the ``/eval/tournament-report`` surface (``tests/api/test_leak.py``).

    The post-init validator enforces the partition invariants fail-loud so an
    inconsistent result can never be constructed (mirrors
    :class:`ConversionReport`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    genuine_class_conversion: GenuineClassConversionReport
    lost_opening_accusations: int
    cap_defaulted_turns: int
    accused_impostor_events: int
    accused_impostor_survivals: int
    survivals_rendered_met: int
    survivals_sheltered_sub_gate: int
    survivals_unevidenced: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> GateMetricsReport:
        counts = (
            self.lost_opening_accusations,
            self.cap_defaulted_turns,
            self.accused_impostor_events,
            self.accused_impostor_survivals,
            self.survivals_rendered_met,
            self.survivals_sheltered_sub_gate,
            self.survivals_unevidenced,
        )
        if any(count < 0 for count in counts):
            raise ValueError("gate-metric counts must be non-negative")
        if self.accused_impostor_survivals > self.accused_impostor_events:
            raise ValueError(
                "accused_impostor_survivals cannot exceed accused_impostor_events: "
                f"{self.accused_impostor_survivals} > {self.accused_impostor_events}"
            )
        survival_parts = (
            self.survivals_rendered_met
            + self.survivals_sheltered_sub_gate
            + self.survivals_unevidenced
        )
        if survival_parts != self.accused_impostor_survivals:
            raise ValueError(
                "met + sheltered + unevidenced survivals must equal "
                f"accused_impostor_survivals: {self.survivals_rendered_met} + "
                f"{self.survivals_sheltered_sub_gate} + "
                f"{self.survivals_unevidenced} != {self.accused_impostor_survivals}"
            )
        return self


def compute_gate_metrics(
    report: TournamentReport | Sequence[GameReport],
) -> GateMetricsReport:
    """Fold a tournament report into the Phase-10 gate surface (Task 10.4).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the other
    analyzers' signature). Pure: no I/O, no engine/agent/LLM calls — every
    derivation is a fold over recorded artifacts, ported from the audit
    extractor (``audits/workflows/extract_gameplay_facts.py``) so the shipped
    surface and the audited numbers share one definition.

    The genuine-class pair is produced by the owning
    :func:`eval.vote_correctness.compute_genuine_class_conversion`, never
    re-derived here. Lost openings count meetings whose first turn carries no
    :class:`~meetings.schemas.AccusationClaim` (an empty transcript vacuously
    counts — its opening supplied nothing). Cap-defaults walk each game's
    ``failed_calls`` for ``deadline_default`` rows and dedupe parsed turn
    coordinates; an unparseable ``deadline_default`` row fails loud. The
    survival partition reads each accused impostor's rendered suspicion off
    the other voters' §6.6 graph rows and — for the sub-gate shelter test
    only — re-derives detector flags through
    :func:`meetings.transcript.detect_contradictions` under the ballot-voter
    roster (the same one-home classifier the genuine-class pair imports).
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    lost_opening_accusations = 0
    defaulted_turn_keys: set[tuple[str, str, str, int, str]] = set()
    accused_impostor_events = 0
    accused_impostor_survivals = 0
    survivals_rendered_met = 0
    survivals_sheltered_sub_gate = 0
    survivals_unevidenced = 0

    for game in games:
        for failed_call in game.failed_calls:
            if failed_call.error_type != "deadline_default":
                continue
            parsed = _DEFAULTED_TURN_RE.search(failed_call.error_message)
            if parsed is not None:
                defaulted_turn_keys.add(
                    (
                        game.game_id,
                        failed_call.meeting_id,
                        parsed.group("kind"),
                        int(parsed.group("index")),
                        parsed.group("speaker"),
                    )
                )
            elif not failed_call.error_message.startswith(_DEFAULTED_VOTE_PREFIX):
                raise ValueError(
                    "unclassifiable deadline_default failed-call row in game "
                    f"{game.game_id!r}: {failed_call.error_message!r} names "
                    "neither a defaulted turn nor a defaulted vote. The "
                    "cap-default count would silently drift on foreign data, "
                    "so this fails loud."
                )

        for meeting in game.meetings:
            turns = meeting.transcript.turns
            opening_has_accusation = bool(turns) and any(
                isinstance(claim, AccusationClaim) for claim in turns[0].claims
            )
            if not opening_has_accusation:
                lost_opening_accusations += 1

            # D-D-2 deception control: living true impostors verbally accused
            # by someone else this meeting (self-accusations are not crew
            # pressure; roles subscript fails loud like the recall lead).
            accused_impostors = sorted(
                {
                    claim.against
                    for turn in turns
                    for claim in turn.claims
                    if isinstance(claim, AccusationClaim)
                    and claim.against != turn.speaker
                    and game.roles[claim.against] == "IMPOSTOR"
                }
            )
            if not accused_impostors:
                continue

            rendered = _rendered_suspicion_by_target(meeting)
            # Re-derived flag subjects, computed lazily: only a sub-gate
            # survivor needs the shelter test (the detector re-run is pure
            # and deterministic — the same one-home classifier the
            # genuine-class pair imports).
            flagged_subjects: frozenset[PlayerId] | None = None
            for impostor in accused_impostors:
                accused_impostor_events += 1
                if (
                    meeting.outcome == "EJECTED"
                    and meeting.ejected_player_id == impostor
                ):
                    continue
                accused_impostor_survivals += 1
                rendered_max = rendered.get(impostor)
                if (
                    rendered_max is not None
                    and rendered_max >= SKIP_SUSPICION_THRESHOLD
                ):
                    survivals_rendered_met += 1
                    continue
                if flagged_subjects is None:
                    roster = frozenset(ballot.voter for ballot in meeting.ballots)
                    flagged_subjects = frozenset(
                        subject
                        for flag in detect_contradictions(
                            meeting.transcript, roster=roster
                        )
                        for subject in flag.subjects
                    )
                if rendered_max is not None and impostor in flagged_subjects:
                    survivals_sheltered_sub_gate += 1
                else:
                    survivals_unevidenced += 1

    return GateMetricsReport(
        genuine_class_conversion=compute_genuine_class_conversion(games),
        lost_opening_accusations=lost_opening_accusations,
        cap_defaulted_turns=len(defaulted_turn_keys),
        accused_impostor_events=accused_impostor_events,
        accused_impostor_survivals=accused_impostor_survivals,
        survivals_rendered_met=survivals_rendered_met,
        survivals_sheltered_sub_gate=survivals_sheltered_sub_gate,
        survivals_unevidenced=survivals_unevidenced,
    )


def _rendered_suspicion_by_target(meeting: MeetingReport) -> dict[PlayerId, float]:
    """Max §4.6 suspicion any OTHER voter's graph rendered per target.

    A voter holds no row about itself, so a player's rendered value comes
    from the other voters' prompts; the max is the strongest verdict anyone
    at the table was shown (the audit extractor's
    ``rendered_suspicion_by_target`` derivation). Non-vote prompts carry no
    graph and contribute nothing.
    """

    rendered: dict[PlayerId, float] = {}
    for call in meeting.llm_calls:
        if call.agent_id is None:
            continue
        for target, suspicion in _parse_suspicion_graph(call.prompt).items():
            if target == call.agent_id:
                continue
            best = rendered.get(target)
            if best is None or suspicion > best:
                rendered[target] = suspicion
    return rendered


# ---------------------------------------------------------------------------
# Task 10.6 gate-spec metrics (audit audit-2026-06-11-2218 gp-7: C-C-6).
#
# The Wave-1 A/B companions to the genuine-class pair: the 10.4 ruler credits
# only the alibi-lie pipeline, which produced 1 of the Wave-0 set's 5 real
# impostor ejections — the intended multi-signal §6.3 pipeline (flag +
# proximity + vent + carry) produced the other 4 and was invisible to the
# gate. ``compute_multi_signal_conversion`` makes that pipeline measurable;
# ``compute_supply_gauges`` publishes the evidence-supply context every
# conversion number must be read against. Neither joins
# :class:`TournamentEvalReport` — the committed Wave-0 sample reports stay
# single-era (no regeneration without a re-record); the report builder
# publishes both, and the corrected Wave-0 baseline fixture
# (``tests/fixtures/phase10/corrected_w0_baseline.json``) is their one
# committed home until the 10.9 re-record folds them into the wrapper.
# ---------------------------------------------------------------------------

# The four §6.3 design channels an ejection's rendered pre-vote lift can
# decompose into over the quantized rule lattice. Pinned literals: the
# fixture, the report builder, and the 10.9 A/B all read these names.
CHANNEL_CONTRADICTION_FLAG: Final[str] = "contradiction_flag"
CHANNEL_BODY_PROXIMITY: Final[str] = "body_proximity"
CHANNEL_VENT_WITNESS: Final[str] = "vent_witness"
CHANNEL_PRIOR_MEETING_CARRY: Final[str] = "prior_meeting_carry"

# Float guard for lattice arithmetic on 2-decimal rendered values.
_CHANNEL_EPS: Final[float] = 1e-9


def decompose_ejection_channels(
    game: GameReport, meeting_index: int
) -> frozenset[str] | None:
    """Design channels behind one impostor ejection's rendered lift (10.6).

    Returns ``None`` unless ``game.meetings[meeting_index]`` is a
    well-formed ``EJECTED`` meeting whose ejected player is a true
    impostor; otherwise the subset of the four ``CHANNEL_*`` constants the
    ejection's rendered pre-vote verdict decomposes into over the
    quantized §6.3 rule lattice. Pure and deterministic — a fold over
    recorded artifacts plus the one-home belief math:

    * ``contradiction_flag`` — THIS meeting's re-derived flags name the
      ejected player; the flag mass ``F`` is computed by running
      :func:`agents.memory.beliefs.apply_contradiction_rule` from the 0.5
      prior (the identical dedup-and-cap arithmetic the vote-time lift
      applied), never a parallel sum.
    * The remaining channels read the PRE-MEETING carry-in ``C = R − F``
      (``R`` = the ejected player's max rendered §6.6 graph row across
      the other voters), whose persistent mass ``P = C − 0.5`` is
      quantized by construction: vent +0.5, body proximity +0.2,
      accusation carry +0.05 per prior accused meeting, decay only ever
      shrinking those quanta.
    * ``prior_meeting_carry`` — the ejected player was verbally accused
      by another speaker in an EARLIER meeting of this game AND ``P > 0``
      (presence-based: at the 1.0 clamp the bump mass is arithmetically
      invisible — the audited seed-8 vent witness — but the accusation
      history is recorded fact).
    * ``vent_witness`` — ``P >=`` the Rule-4 delta: on the lattice no
      other single channel reaches +0.5 (the Wave-0 census: the only 1.0
      is the vent-witnessed impostor).
    * ``body_proximity`` — mass remains after subtracting the vent delta
      and the carry ceiling (``ACCUSATION_SUSPICION_DELTA`` x prior
      accused meetings, floored at the remainder): decayed carry can only
      shrink below its ceiling, so a positive remainder cannot be carry
      and the only §6.3 channel left is Rule 1.

    **The 1.0 clamp is a special case.** A row at the rendered ceiling may
    have absorbed any amount of over-mass, so subtracting ``F`` from it is
    NOT a faithful carry-in inverse: a vent witness (carry-in 1.0) plus
    any same-meeting flag would read ``P = 0.5 − F``, lose the vent
    channel, and mis-attribute the residue to body proximity. At the
    ceiling the decomposition therefore switches to bounds: the persistent
    mass is read WITHOUT the flag subtraction (its upper bound, exactly
    the Rule-4 delta), ``vent_witness`` is attributed — §6.3 calls a
    witnessed vent "almost certain" and the Wave-0 census found every
    observed 1.0 to be the vent-witnessed impostor, so the ceiling is
    Rule 4's signature on this lattice — and ``body_proximity`` is never
    attributed from the un-invertible remainder (carry stays
    presence-based). The one ambiguity this trades away (a no-vent stack
    landing on exactly 1.00 — e.g. an undeacayed strong flag + one body
    proximity — reading vent instead of proximity) cannot change the
    multi-signal verdict, only swap which perception channel is named.

    A meeting with no rendered row for the ejected player decomposes to
    the flag channel alone (nothing else is attributable without the
    rendered surface).
    """

    meeting = game.meetings[meeting_index]
    if meeting.outcome != "EJECTED":
        return None
    ejected = meeting.ejected_player_id
    if ejected is None:
        return None
    if game.roles[ejected] != "IMPOSTOR":
        return None

    channels: set[str] = set()

    roster = frozenset(ballot.voter for ballot in meeting.ballots)
    naming_flags = [
        flag
        for flag in detect_contradictions(meeting.transcript, roster=roster)
        if ejected in flag.subjects
    ]
    flag_mass = 0.0
    if naming_flags:
        beliefs = BeliefState()
        beliefs.seed_player(ejected, suspicion=0.5, trust=0.5)
        lifted = apply_contradiction_rule(beliefs, naming_flags)
        flag_mass = lifted.view(ejected).suspicion - 0.5
    if flag_mass > _CHANNEL_EPS:
        channels.add(CHANNEL_CONTRADICTION_FLAG)

    rendered = _rendered_suspicion_by_target(meeting).get(ejected)
    if rendered is None:
        return frozenset(channels)
    # At the rendered ceiling the clamp may have absorbed mass, so the
    # flag subtraction is not a faithful carry-in inverse (see the
    # docstring's clamp paragraph): read the persistent mass without it.
    clamped = rendered >= 1.0 - _CHANNEL_EPS
    persistent = round(rendered - 0.5 if clamped else rendered - flag_mass - 0.5, 4)
    if persistent <= _CHANNEL_EPS:
        return frozenset(channels)

    prior_accused_meetings = sum(
        1
        for earlier in game.meetings[:meeting_index]
        if any(
            isinstance(claim, AccusationClaim)
            and claim.against == ejected
            and turn.speaker != ejected
            for turn in earlier.transcript.turns
            for claim in turn.claims
        )
    )
    if prior_accused_meetings > 0:
        channels.add(CHANNEL_PRIOR_MEETING_CARRY)

    if clamped:
        # The ceiling is Rule 4's lattice signature: attribute the vent
        # witness, never body proximity (the remainder under a clamp is
        # un-invertible — inventing proximity from it was exactly the
        # mis-attribution the clamp paragraph describes).
        if persistent >= VENTING_SUSPICION_DELTA - _CHANNEL_EPS:
            channels.add(CHANNEL_VENT_WITNESS)
        return frozenset(channels)

    remaining = persistent
    if remaining >= VENTING_SUSPICION_DELTA - _CHANNEL_EPS:
        channels.add(CHANNEL_VENT_WITNESS)
        remaining = round(remaining - VENTING_SUSPICION_DELTA, 4)
    carry_ceiling = ACCUSATION_SUSPICION_DELTA * prior_accused_meetings
    remaining = round(remaining - min(remaining, carry_ceiling), 4)
    if remaining > _CHANNEL_EPS:
        channels.add(CHANNEL_BODY_PROXIMITY)
    return frozenset(channels)


class MultiSignalConversionReport(BaseModel):
    """The gp-7 companion conversion metric (Task 10.6; audit C-C-6).

    Frozen value object counting the impostor ejections whose rendered
    pre-vote lift decomposes into 2+ DISTINCT §6.3 design channels
    (:func:`decompose_ejection_channels`) — the intended multi-signal
    pipeline the genuine-class ruler is blind to. On the Wave-0 bytes the
    ruler credited 1 of 5 real conversions; the other 4 (seeds 8/11/26/39)
    converted via flag+proximity+carry / vent+carry stacks, so a detector-
    precision repair that shifts flag composition cannot masquerade as a
    conversion regression once this companion is on the gate surface
    (audit gp-7 item 1).

    * ``impostor_ejections`` — decomposable impostor ejections (the
      denominator; matches the precision lead's impostor bucket).
    * ``multi_signal_conversions`` — ejections with >= 2 channels.
    * ``single_signal_conversions`` — exactly 1 channel (the seed-24
      flag-only conversion lives here).
    * ``unattributed_conversions`` — zero channels: an ejection whose
      lift the lattice cannot explain. Always counted, never dropped — a
      non-zero value is a decomposition bug or an off-lattice mechanism
      to chase.
    * ``conversions_with_*`` — per-channel presence counts (an ejection
      counts in every channel it decomposes into).
    * ``multi_signal_rate`` — ``multi_signal_conversions /
      impostor_ejections``; ``None`` (undefined, not 0.0) with no
      impostor ejections, the module's rate convention.

    **Leak-safety.** Pure aggregates; no roles, transcripts, or
    engine-owned types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    impostor_ejections: int
    multi_signal_conversions: int
    single_signal_conversions: int
    unattributed_conversions: int
    conversions_with_contradiction_flag: int
    conversions_with_body_proximity: int
    conversions_with_vent_witness: int
    conversions_with_prior_meeting_carry: int
    multi_signal_rate: float | None

    @model_validator(mode="after")
    def _validate_buckets(self) -> MultiSignalConversionReport:
        counts = (
            self.impostor_ejections,
            self.multi_signal_conversions,
            self.single_signal_conversions,
            self.unattributed_conversions,
            self.conversions_with_contradiction_flag,
            self.conversions_with_body_proximity,
            self.conversions_with_vent_witness,
            self.conversions_with_prior_meeting_carry,
        )
        if any(count < 0 for count in counts):
            raise ValueError("multi-signal counts must be non-negative")
        partition = (
            self.multi_signal_conversions
            + self.single_signal_conversions
            + self.unattributed_conversions
        )
        if partition != self.impostor_ejections:
            raise ValueError(
                "multi + single + unattributed must equal impostor_ejections: "
                f"{self.multi_signal_conversions} + "
                f"{self.single_signal_conversions} + "
                f"{self.unattributed_conversions} != {self.impostor_ejections}"
            )
        if self.impostor_ejections == 0:
            if self.multi_signal_rate is not None:
                raise ValueError(
                    "multi_signal_rate must be None with no impostor ejections: "
                    "the rate is undefined, not 0.0"
                )
        else:
            if self.multi_signal_rate is None:
                raise ValueError(
                    "multi_signal_rate must be set when impostor_ejections > 0"
                )
            if not 0.0 <= self.multi_signal_rate <= 1.0:
                raise ValueError(
                    f"multi_signal_rate must be in [0.0, 1.0]: {self.multi_signal_rate}"
                )
        return self


def compute_multi_signal_conversion(
    report: TournamentReport | Sequence[GameReport],
) -> MultiSignalConversionReport:
    """Fold a tournament report into the multi-signal companion (Task 10.6).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a
    bare sequence of :class:`~eval.report_schema.GameReport`. Pure: every
    number is a fold of :func:`decompose_ejection_channels` over the
    well-formed impostor ejections (a malformed ``EJECTED`` meeting with
    no ejected id, a crewmate ejection, and a SKIP all contribute
    nothing).
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    impostor_ejections = 0
    multi_signal = 0
    single_signal = 0
    unattributed = 0
    with_channel = {
        CHANNEL_CONTRADICTION_FLAG: 0,
        CHANNEL_BODY_PROXIMITY: 0,
        CHANNEL_VENT_WITNESS: 0,
        CHANNEL_PRIOR_MEETING_CARRY: 0,
    }
    for game in games:
        for meeting_index in range(len(game.meetings)):
            channels = decompose_ejection_channels(game, meeting_index)
            if channels is None:
                continue
            impostor_ejections += 1
            if len(channels) >= 2:
                multi_signal += 1
            elif len(channels) == 1:
                single_signal += 1
            else:
                unattributed += 1
            for channel in channels:
                with_channel[channel] += 1

    rate = multi_signal / impostor_ejections if impostor_ejections > 0 else None
    return MultiSignalConversionReport(
        impostor_ejections=impostor_ejections,
        multi_signal_conversions=multi_signal,
        single_signal_conversions=single_signal,
        unattributed_conversions=unattributed,
        conversions_with_contradiction_flag=with_channel[CHANNEL_CONTRADICTION_FLAG],
        conversions_with_body_proximity=with_channel[CHANNEL_BODY_PROXIMITY],
        conversions_with_vent_witness=with_channel[CHANNEL_VENT_WITNESS],
        conversions_with_prior_meeting_carry=with_channel[CHANNEL_PRIOR_MEETING_CARRY],
        multi_signal_rate=rate,
    )


class SupplyGaugesReport(BaseModel):
    """The gp-7 evidence-supply gauges (Task 10.6; audit C-C-6, B-B-3, C-C-8).

    Frozen value object publishing the supply context every Wave-1
    conversion number must be read against — supply, not follow-through,
    is the audited binding constraint (62% of Wave-0 meetings carried
    zero contradictions; crew compliance with the rendered verdict was
    already 100%). Every flag-derived field re-runs the one-home detector
    under the ballot-voter roster, so the gauges read the CORRECTED
    instrument on any era's bytes:

    * ``meetings_total`` / ``total_flags`` / ``weak_flags`` /
      ``strong_flags`` — the re-derived flag census (the corrected
      Wave-0 baseline's headline volume row).
    * ``zero_contradiction_meetings`` (+ ``..._share``) — meetings whose
      re-derived flag set is empty (B-B-3's 62%).
    * ``genuine_subject_meetings`` (+ ``..._share``) — meetings
      supplying at least one genuine-class subject
      (:func:`eval.vote_correctness.genuine_class_subjects`, one home —
      role-blind: supply is about the detector handing the table a
      diagnostic flag at all).
    * ``flag_subjects_crew`` / ``flag_subjects_impostor`` — the
      flag-subject role split, counted per (flag, subject): the cascade
      base-rate denominator any future magnitude change multiplies
      (C-C-8: the honest detector still points at innocents more often
      than impostors).
    * ``accused_impostor_meetings`` / ``over_gate_listener_rows`` (+
      ``over_gate_listeners_per_accused_impostor_meeting``) — for every
      meeting with a living verbally-accused true impostor (the D-D-2
      event population), the number of OTHER voters whose rendered §6.6
      row for an accused impostor met the §4.6 threshold. THE Wave-1
      success gauge: 10.6's job is growing the over-gate POPULATION past
      the 4-7 mandatory-skip bloc, not witness follow-through. ``None``
      share/rate fields follow the undefined-not-zero convention.

    **Leak-safety.** Pure aggregates; no roles, transcripts, or
    engine-owned types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    meetings_total: int
    total_flags: int
    weak_flags: int
    strong_flags: int
    zero_contradiction_meetings: int
    zero_contradiction_share: float | None
    genuine_subject_meetings: int
    genuine_subject_share: float | None
    flag_subjects_crew: int
    flag_subjects_impostor: int
    accused_impostor_meetings: int
    over_gate_listener_rows: int
    over_gate_listeners_per_accused_impostor_meeting: float | None

    @model_validator(mode="after")
    def _validate_buckets(self) -> SupplyGaugesReport:
        counts = (
            self.meetings_total,
            self.total_flags,
            self.weak_flags,
            self.strong_flags,
            self.zero_contradiction_meetings,
            self.genuine_subject_meetings,
            self.flag_subjects_crew,
            self.flag_subjects_impostor,
            self.accused_impostor_meetings,
            self.over_gate_listener_rows,
        )
        if any(count < 0 for count in counts):
            raise ValueError("supply-gauge counts must be non-negative")
        if self.weak_flags + self.strong_flags != self.total_flags:
            raise ValueError(
                "weak_flags + strong_flags must equal total_flags: "
                f"{self.weak_flags} + {self.strong_flags} != {self.total_flags}"
            )
        for name, share, denominator in (
            (
                "zero_contradiction_share",
                self.zero_contradiction_share,
                self.meetings_total,
            ),
            ("genuine_subject_share", self.genuine_subject_share, self.meetings_total),
            (
                "over_gate_listeners_per_accused_impostor_meeting",
                self.over_gate_listeners_per_accused_impostor_meeting,
                self.accused_impostor_meetings,
            ),
        ):
            if denominator == 0:
                if share is not None:
                    raise ValueError(
                        f"{name} must be None when its denominator is 0: "
                        "the value is undefined, not 0.0"
                    )
            elif share is None:
                raise ValueError(f"{name} must be set when its denominator > 0")
        return self


def compute_supply_gauges(
    report: TournamentReport | Sequence[GameReport],
) -> SupplyGaugesReport:
    """Fold a tournament report into the gp-7 supply gauges (Task 10.6).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a
    bare sequence of :class:`~eval.report_schema.GameReport`. Pure: the
    flag census re-runs the one-home detector per meeting, the genuine
    share reads :func:`eval.vote_correctness.genuine_class_subjects`, and
    the over-gate gauge reads each accused impostor's rendered row off the
    other voters' recorded §6.6 graphs (``roles`` subscripts fail loud on
    internal inconsistency, the module convention).
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    meetings_total = 0
    total_flags = 0
    weak_flags = 0
    strong_flags = 0
    zero_contradiction_meetings = 0
    genuine_subject_meetings = 0
    flag_subjects_crew = 0
    flag_subjects_impostor = 0
    accused_impostor_meetings = 0
    over_gate_listener_rows = 0

    for game in games:
        for meeting in game.meetings:
            meetings_total += 1
            roster = frozenset(ballot.voter for ballot in meeting.ballots)
            flags = detect_contradictions(meeting.transcript, roster=roster)
            total_flags += len(flags)
            if not flags:
                zero_contradiction_meetings += 1
            for flag in flags:
                if is_weak_contradiction(flag):
                    weak_flags += 1
                else:
                    strong_flags += 1
                for subject in flag.subjects:
                    if game.roles[subject] == "IMPOSTOR":
                        flag_subjects_impostor += 1
                    else:
                        flag_subjects_crew += 1
            if genuine_class_subjects(meeting):
                genuine_subject_meetings += 1

            accused_impostors = sorted(
                {
                    claim.against
                    for turn in meeting.transcript.turns
                    for claim in turn.claims
                    if isinstance(claim, AccusationClaim)
                    and claim.against != turn.speaker
                    and game.roles[claim.against] == "IMPOSTOR"
                }
            )
            if not accused_impostors:
                continue
            accused_impostor_meetings += 1
            rendered = _rendered_suspicion_by_target_per_voter(meeting)
            for impostor in accused_impostors:
                for voter, rows in rendered.items():
                    if voter == impostor:
                        continue
                    row = rows.get(impostor)
                    if row is not None and row >= SKIP_SUSPICION_THRESHOLD:
                        over_gate_listener_rows += 1

    return SupplyGaugesReport(
        meetings_total=meetings_total,
        total_flags=total_flags,
        weak_flags=weak_flags,
        strong_flags=strong_flags,
        zero_contradiction_meetings=zero_contradiction_meetings,
        zero_contradiction_share=(
            zero_contradiction_meetings / meetings_total if meetings_total else None
        ),
        genuine_subject_meetings=genuine_subject_meetings,
        genuine_subject_share=(
            genuine_subject_meetings / meetings_total if meetings_total else None
        ),
        flag_subjects_crew=flag_subjects_crew,
        flag_subjects_impostor=flag_subjects_impostor,
        accused_impostor_meetings=accused_impostor_meetings,
        over_gate_listener_rows=over_gate_listener_rows,
        over_gate_listeners_per_accused_impostor_meeting=(
            over_gate_listener_rows / accused_impostor_meetings
            if accused_impostor_meetings
            else None
        ),
    )


def _rendered_suspicion_by_target_per_voter(
    meeting: MeetingReport,
) -> dict[PlayerId, dict[PlayerId, float]]:
    """Each voter's rendered §6.6 graph rows, keyed voter -> target.

    The per-VOTER companion of :func:`_rendered_suspicion_by_target` (which
    keeps only the cross-voter max): the over-gate-listener gauge counts
    LISTENERS, so it needs every voter's own row for the accused impostor.
    A voter with several calls keeps the highest row per target (the vote
    call is the graph-bearing one; non-vote prompts contribute nothing).
    """

    rendered: dict[PlayerId, dict[PlayerId, float]] = {}
    for call in meeting.llm_calls:
        if call.agent_id is None:
            continue
        for target, suspicion in _parse_suspicion_graph(call.prompt).items():
            if target == call.agent_id:
                continue
            rows = rendered.setdefault(call.agent_id, {})
            best = rows.get(target)
            if best is None or suspicion > best:
                rows[target] = suspicion
    return rendered


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
    bumps it only when older readers cannot interpret the shape). The Task
    10.4 ``gate_metrics`` block follows it again — wrapper-level only, inner
    shape untouched, version stays 2 — and both committed reports are
    regenerated in the same PR, so no pre-10.4 wrapper JSON survives to be
    read.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    report: TournamentReport
    vote_correctness: VoteCorrectnessReport
    accusation_calibration: AccusationCalibrationReport
    alibi_fabrication: AlibiFabricationReport
    cost_dashboard: CostDashboard
    meeting_rate: MeetingRateReport
    conversion: ConversionReport
    gate_metrics: GateMetricsReport


def build_tournament_eval_report(report: TournamentReport) -> TournamentEvalReport:
    """Run the §11.3 + W0.3 analyzers over ``report`` and wrap the results.

    Pure assembly: each metric is computed by its own public ``compute_*``
    entry point over the same :class:`~eval.report_schema.TournamentReport`, and
    the results are packed into a :class:`TournamentEvalReport`. No metric math
    is reimplemented here — this function only orchestrates the analyzers
    (including :func:`compute_meeting_rate`, :func:`compute_conversion_report`,
    and :func:`compute_gate_metrics`) and bundles their outputs with the
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
        gate_metrics=compute_gate_metrics(report),
    )


__all__ = [
    "CHANNEL_BODY_PROXIMITY",
    "CHANNEL_CONTRADICTION_FLAG",
    "CHANNEL_PRIOR_MEETING_CARRY",
    "CHANNEL_VENT_WITNESS",
    "BallotTargetRedirectReport",
    "ConversionReport",
    "DefaultedBallotReport",
    "GateMetricsReport",
    "MeetingRateReport",
    "MultiSignalConversionReport",
    "SupplyGaugesReport",
    "TournamentEvalReport",
    "build_tournament_eval_report",
    "compute_ballot_target_redirects",
    "compute_conversion_report",
    "compute_defaulted_ballots",
    "compute_gate_metrics",
    "compute_meeting_rate",
    "compute_multi_signal_conversion",
    "compute_supply_gauges",
    "decompose_ejection_channels",
]
