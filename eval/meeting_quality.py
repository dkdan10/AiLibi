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
  partition, and ``threshold_inversions`` as the crew discretionary-decline
  census at the rendered §4.6 reference line — nonzero INTENDED post-13.13,
  see the Phase 19 Wave 1 block below)
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
  :func:`eval.vote_correctness.compute_genuine_class_conversion` — Phase 19
  (Task 19.5) wires the Task-17.6 successor ``supplied_channel_conversion``
  beside it on this surface, and the legacy cell is a labeled historical
  column from then on), the
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

Phase 17 Wave 0 (Task 17.2) teaches the SKIP partition the citation-gate
coercion in this module:

* *Citation-coerced SKIPs* — the ballots the Task 16.6 citation gate
  (``citation_gate_enabled`` lever ON) rewrote from an uncited zero-flag
  EJECT to SKIP, keyed on
  :data:`~meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER` and censused as a
  fourth by-design bucket of the SKIP partition
  (``citation_coerced_skip_ballots``, beside correct / missed /
  unclassified). :func:`compute_conversion_report` diverts these ballots
  BEFORE the tri-split, role- and verdict-blind: the gate working is never a
  voter decision, so a coerced SKIP is never a missed skip and never a §4.6
  ``threshold_inversions`` entry (audits/audit-phase-16-close.md §8 routed
  contract (b); the 17.2 designer ruling tasks/phase-17.md, the
  invalid-target / teammate precedent). Unlike the Task 10.6 / 10.9 surfaces
  this is a field ON the frozen :class:`ConversionReport`, defaulting to 0 so
  the committed single-era reports (predating the field) still parse until
  the 17.9 re-record.

Phase 19 Wave 1 (Task 19.5, metric truth) rewires the gate surface and
retires a doctrine in this module (audits/audit-phase-19-triage.md §7 items
5+6, row C6):

* *The canary joins the gate surface* — :class:`GateMetricsReport` gains
  ``supplied_channel_conversion``, the Task-17.6 successor instrument
  (:func:`eval.vote_correctness.compute_supplied_channel_conversion`) and the
  ONLY canary-eligible genuine-class cell from baseline 5 onward
  (audits/audit-phase-16-close.md §8 re-anchor). The declared canary had been
  wired to nothing; the Phase-10 ``genuine_class_conversion`` cell it succeeds
  stays computed beside it as a labeled HISTORICAL column — starved (0/0 on
  baselines 4 and 5), reported only, never a canary.
* *The ``threshold_inversions`` re-doctrine* — Task 13.13 de-imperatived the
  §4.6 vote gate (``vote_ballot.j2`` renders the voter's max suspicion and the
  0.60 reference threshold as a NON-directive evidence line; only the
  deterministic tally floor in :func:`meetings.voting.tally_ballots`
  constrains outcomes), so a crew voter who declines over a met reference line
  is exercising sanctioned discretion. The bucket is a conservatism gauge and
  its nonzero value is INTENDED on post-13.13 recordings — the old "expected
  ~0 … a gate-render/obedience bug to chase" reading is retired (see the
  :class:`ConversionReport` bullet for the 19.5 recount that grounds it).
* *The recount analyzer* — :func:`recount_threshold_inversions` /
  :class:`ThresholdInversionRecount`, the by-cause table behind that
  re-doctrine: marker-freedom, the rendered-max bands, and the meeting
  outcomes the inversions sit in. It folds the SAME module-private per-ballot
  classification :func:`compute_conversion_report` consumes
  (:func:`_iter_skip_ballot_views`), so the recount can never drift from the
  partition it recounts.

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
from collections.abc import Iterator, Mapping, Sequence
from typing import Final, Literal, NamedTuple

from pydantic import BaseModel, ConfigDict, model_validator

from agents.memory.beliefs import (
    ACCUSATION_SUSPICION_DELTA,
    BODY_PROXIMITY_SUSPICION_DELTA,
    VENTING_SUSPICION_DELTA,
    WITNESS_INFORM_REASON,
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
from eval.deduction_metrics import (
    DeductionMetricsReport,
    KillCraftSupplyCells,
    compute_deduction_metrics,
)
from eval.report_schema import GameReport, MeetingReport, TournamentReport
from eval.vote_correctness import (
    GenuineClassConversionReport,
    SuppliedChannelConversionReport,
    VoteCorrectnessReport,
    compute_genuine_class_conversion,
    compute_supplied_channel_conversion,
    compute_vote_correctness,
    genuine_class_subjects,
)
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    UNCITED_ZERO_FLAG_EJECT_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    derive_belief_evidence,
)
from meetings.schemas import AccusationClaim, ContradictionRef, PlayerId, VoteBallot
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

# The Task 17.2 citation-gate coercion marker (Task 16.6, J2). UNLIKE the four
# naive prefix constants above, this one is matched with the established
# ``{x!r}`` repr-aware convention rather than a raw ``in``/prefix scan:
#
# * The pattern is built from the imported production literal
#   (:data:`~meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER`), never
#   re-spelled here -- the head and tail are sliced off the constant so a
#   change to the marker text can never silently desync the parse.
# * The marker interpolates its payload with ``{target!r}`` -- a Python repr,
#   always a quoted literal -- so matching the QUOTED value (rather than the
#   static tail alone) makes the parse robust when the original target text
#   itself contains the marker's tail (``... coerced to SKIP] ``): the
#   quote-matching consumes the whole repr first, so the match ends at the
#   REAL marker boundary, not inside the payload.
# * Anchored ``^`` because the citation gate is the LAST guard in the
#   manager's ballot chain (Task 16.6), so the coercion marker is always the
#   OUTERMOST prefix; any stacked 16.5/16.6-era markers (e.g. a nulled
#   :data:`~meetings.manager.INVALID_OBSERVATION_ID_MARKER`) ride INSIDE it.
# * Mirrors :func:`api.replay_loader._marker_pattern`, replicated locally
#   because that helper is private to the api layer (a cross-layer import of
#   it would couple eval to api internals).
_MARKER_REPR_VALUE: Final[str] = r"(?:'(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")"
_UNCITED_ZERO_FLAG_MARKER_PATTERN: Final[re.Pattern[str]] = re.compile(
    "^"
    + re.escape(UNCITED_ZERO_FLAG_EJECT_MARKER.partition("{")[0])
    + _MARKER_REPR_VALUE
    + re.escape(UNCITED_ZERO_FLAG_EJECT_MARKER.partition("}")[2])
)

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
# The vote template's suspicion-graph header changed with the qwen3_32b.v3
# prompt set (Task 14.7): "## Your suspicion of each player" replaces the legacy
# qwen3.5:9b "## Your suspicion graph". Both emit the identical row shape below,
# so the parser accepts either header (newest first) and only the header string
# alternates. Recognizing both keeps the frozen 9B-era prompt_regression
# fixtures parsing while the canonical set is on the new header.
# FROZEN (Phase 19 tier map, training/README.md): rendered-prose scrape —
# unreliable under prompt-shape change. Bug fixes and evidence readers only; no
# new search. (The suspicion-graph read below regex-parses rendered prompt
# text; non-matching rows are silently skipped.)
_SUSPICION_GRAPH_HEADERS: Final[tuple[str, ...]] = (
    "## Your suspicion of each player",
    "## Your suspicion graph",
)
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
# The defaulted-VOTE row names its voter the same way; capture it so the
# persisted §4.6 verdict max (``FailedCallReplayEntry.rendered_vote_max``, Task
# 10.12) can be joined back to the defaulted SKIP ballot it belongs to. The
# voter is the run of non-"; " characters so a trailing " [error: ...]" suffix
# (a REAL provider's parse failure appended to the message) is excluded.
_DEFAULTED_VOTE_RE: Final[re.Pattern[str]] = re.compile(
    r"vote defaulted[^;]*;\s*(?P<voter>\S+) submitted no ballot"
)


def _persisted_vote_verdict_maxes(
    game: GameReport,
) -> dict[tuple[str, PlayerId], float]:
    """Map ``(meeting_id, voter)`` -> the persisted §4.6 max of a DEFAULTED vote.

    A defaulted ballot's vote call fails before the recording client logs its
    prompt, so the rendered max is absent from ``llm_calls``; the manager stamps
    it onto the ``deadline_default`` failed-call row instead (Task 10.12, audit
    2026-06-13-1816 H-H-2). Both SKIP-census surfaces
    (:func:`compute_conversion_report`'s decision census and
    :func:`compute_defaulted_ballots`'s telemetry census) read this ONE map as
    the fallback when no logged vote prompt is recoverable, so they can never
    disagree about a defaulted voter's verdict. Empty for committed single-era
    replays, which predate the field -- those defaulted ballots stay
    verdict-less (``defaulted_without_render`` / diverted) in both surfaces.
    """

    rendered: dict[tuple[str, PlayerId], float] = {}
    for failed_call in game.failed_calls:
        if (
            failed_call.error_type != "deadline_default"
            or failed_call.rendered_vote_max is None
        ):
            continue
        match = _DEFAULTED_VOTE_RE.match(failed_call.error_message)
        if match is not None:
            rendered[(failed_call.meeting_id, match.group("voter"))] = (
                failed_call.rendered_vote_max
            )
    return rendered


def _parse_suspicion_graph(prompt: str) -> dict[PlayerId, float]:
    """Return ``{player_id: rendered_suspicion}`` from a vote prompt's graph.

    Empty when the prompt carries no suspicion-graph section (a voter with no
    beliefs about anyone, or a non-vote prompt). The block ends at the next
    ``## `` header. Accepts either the qwen3_32b.v3 or the legacy 9B header (see
    the constants above for why this parse lives here).
    """

    header = next((h for h in _SUSPICION_GRAPH_HEADERS if h in prompt), None)
    if header is None:
        return {}
    after = prompt.split(header, 1)[1]
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
      SKIPped), ``unclassified_skip_ballots`` (no rendered gate line was
      found for the voter — older prompt version or missing vote call), and
      ``citation_coerced_skip_ballots`` (the 16.6 citation-gate coercion; see
      the dedicated bullet below).
      Task 10.9.1 narrows the census to voter DECISIONS: a SKIP stamped with
      the parse-default marker
      (:data:`~meetings.manager.VOTE_PARSE_DEFAULT_MARKER`, the manager's
      vote fail-soft over an unparseable completion — PR #147 F1) enters
      these buckets only when it coincides with a correct skip; under a
      MUST-vote render or with no rendered verdict it is DIVERTED to the
      standalone :class:`DefaultedBallotReport` census instead, so a
      degraded SKIP can never read as a missed skip or a genuine
      ``threshold_inversions`` entry.
    * ``citation_coerced_skip_ballots`` is the 16.6 citation-gate coercion
      class (:func:`meetings.manager.guard_ballot_citation`, marker
      :data:`~meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER`): the gate
      rewrote an uncited zero-flag EJECT to SKIP — the gate working, never
      the voter's decision, so a marker-anchored SKIP is neither a correct
      skip, a missed skip, nor a §4.6 ``threshold_inversions`` entry. It is
      diverted BEFORE the correct/missed/unclassified tri-split and the
      divert is role- and verdict-blind (Task 17.2 designer ruling
      tasks/phase-17.md; audits/audit-phase-16-close.md §8 routed contract
      (b)): a sub-threshold coerced SKIP is never a chosen correct skip and
      an impostor's coerced SKIP is never an in-character decline, because a
      coerced ballot is a forced eject, not a decision (the 17.10 ruling).
      On the committed baseline-5 9p2i bytes it is 2 — one crew ballot the
      pre-17.2 partition mis-filed as a ``threshold_inversions`` entry and
      one impostor ballot the role-first impostor bucket absorbed — which is
      why moving them out drops the recorded inversions 99 → 98 and the
      impostor voters 42 → 41. The field DEFAULTS to 0: the committed
      single-era eval reports (the baseline-5 samples and the stale
      ml_corpus reports) predate this field and are NOT regenerated before
      the 17.9 corpus re-record, so the model must still parse them; on those
      artifacts the coerced ballots stay folded where the old partition put
      them (the recorded truth), and every FRESH recompute populates the
      bucket.
    * ``missed_skip_ballots`` is a **SENTINEL, not a down-is-good metric**:
      it partitions exactly into ``missed_skip_impostor_voters`` (the voter
      is an impostor — the audited exclusion class: impostor in-character
      voting is sanctioned by the vote prompt, so a met-threshold SKIP by an
      impostor is adversarial play / teammate protection by design, never a
      crew gate bug), ``missed_skip_invalid_target`` (a hallucinated
      out-of-roster target normalized to SKIP, identified by the pinned
      :data:`~meetings.manager.INVALID_VOTE_TARGET_MARKER` audit trail), and
      ``threshold_inversions`` (the crew discretionary-decline remainder).
      On the audited 9.5 baseline the partition is 38 = 34 impostor-voter +
      4 invalid-target + 0 genuine — driving the count down would mostly mean
      breaking impostor play, so read the partition, not the total.
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
    * ``threshold_inversions`` is the **crew DISCRETIONARY-DECLINE census at
      the rendered §4.6 reference line**, scoped to CREW voters: a crew voter
      whose rendered max met
      :data:`~eval._suspicion_parse.SKIP_SUSPICION_THRESHOLD` over a living
      target who SKIPped anyway, carrying no normalization marker. Since Task
      13.13 de-imperatived the vote gate — ``vote_ballot.j2`` renders the max
      and the 0.60 reference threshold as ONE non-directive evidence line
      beside the transcript, the contradiction flags, and the memory view,
      and only the deterministic tally floor
      (:func:`meetings.voting.tally_ballots`) constrains the outcome — such a
      decline is sanctioned voter discretion, not disobedience. The count is
      therefore **EXPECTED NONZERO on post-13.13 recordings** and the
      pre-13.13 reading ("expected ~0 on a clean baseline; a nonzero count is
      a gate-render/obedience bug to chase") is RETIRED
      (audits/audit-phase-19-triage.md row C6).
      The Task-19.5 recount (:func:`recount_threshold_inversions`) is what
      grounds the re-doctrine: over ALL FOUR committed sets every recorded
      inversion is marker-free, and the rendered mass sits AT the advisory
      line rather than deep above it (samples 9p2i: 81 of 87 in
      ``[0.60, 0.70)``, 36 of those exactly at 0.60). So the bucket is a
      CONSERVATISM GAUGE — read its distribution, not its total. It is not a
      conversion knob to optimize and it is not a gate-obedience firewall.
      What WOULD be a bug is a MARKER-BEARING ballot landing here: the
      diversions above (invalid target, teammate coercion, parse default,
      citation gate) exist precisely to keep by-design rewrites out of this
      remainder, which is why the recount's ``marker_free`` cell measures
      exactly that.

    **Leak-safety.** Every field is a pure aggregate (two rates and thirteen
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
    citation_coerced_skip_ballots: int = 0
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
            self.citation_coerced_skip_ballots,
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
            + self.citation_coerced_skip_ballots
        )
        if skip_parts != self.skip_ballots:
            raise ValueError(
                "correct + missed + unclassified + citation_coerced skip "
                f"ballots must equal skip_ballots: {self.correct_skip_ballots} "
                f"+ {self.missed_skip_ballots} + {self.unclassified_skip_ballots} "
                f"+ {self.citation_coerced_skip_ballots} != {self.skip_ballots}"
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


_SkipBallotCategory = Literal[
    "diverted_defaulted",
    "citation_coerced",
    "unclassified",
    "correct_skip",
    "missed_impostor",
    "missed_invalid_target",
    "threshold_inversion",
]


class _SkipBallotView(NamedTuple):
    """One SKIP ballot with its decision-census classification (Task 19.5).

    The carrier of the ONE per-ballot partition: the decision census
    (:func:`compute_conversion_report`) and the by-cause recount
    (:func:`recount_threshold_inversions`) both fold
    :func:`_iter_skip_ballot_views`, so a recount can never disagree with the
    partition it recounts. ``rendered_max`` is the voter's recovered §4.6
    verdict (``None`` when none was recoverable); ``category`` is the bucket
    the census assigns, with the two by-design diversions
    (``diverted_defaulted``, ``citation_coerced``) named rather than dropped
    so a consumer can tell "excluded from ``skip_ballots``" from "counted in a
    by-design bucket".
    """

    meeting: MeetingReport
    ballot: VoteBallot
    rendered_max: float | None
    category: _SkipBallotCategory


def _iter_skip_ballot_views(game: GameReport) -> Iterator[_SkipBallotView]:
    """Classify every SKIP ballot in one game (the Task 9.6 decision census).

    Pure generator over recorded artifacts; the classification order IS the
    census order, so the buckets are exactly what
    :func:`compute_conversion_report` publishes (see its docstring and the
    :class:`ConversionReport` bullets for what each bucket means).
    """

    # Persisted §4.6 verdict for each DEFAULTED vote (Task 10.12, audit
    # H-H-2): the same map :func:`compute_defaulted_ballots` reads, so a
    # defaulted MUST-skip ballot whose vote prompt never logged still lands
    # in correct_skip_ballots (the documented overlap) and a defaulted
    # MUST-vote ballot still diverts -- never a missed skip / inversion.
    rendered_from_failed = _persisted_vote_verdict_maxes(game)
    for meeting in game.meetings:
        # Recover each voter's rendered §4.6 gate verdict from the meeting's
        # vote-prompt calls. A voter can have both a turn call and a vote
        # call; only the vote call carries the line, so non-vote prompts
        # parse to None and never overwrite.
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
            is_marked_default = (
                _VOTE_PARSE_DEFAULT_MARKER_PREFIX in ballot.rationale_text
            )
            if rendered_max is None and is_marked_default:
                # A parse-defaulted vote logged no prompt; recover its
                # rendered §4.6 max from the persisted failed-call field
                # (Task 10.12). Gated on the marker: an UNMARKED deadline
                # default (interactive vote_seconds miss -- plain
                # ``DEFAULT_VOTE_RATIONALE``, no marker) also stamps a
                # ``rendered_vote_max`` on its failed-call row, but the
                # divert below is marker-gated and cannot catch it, so
                # lending it a rendered max would falsely score it as a
                # missed skip / threshold inversion. Unmarked defaults keep
                # ``rendered_max is None`` and stay ``unclassified``, exactly
                # as before this field existed.
                rendered_max = rendered_from_failed.get(
                    (meeting.meeting_id, ballot.voter)
                )
            category: _SkipBallotCategory
            # DEFAULTED diversion (Task 10.9.1; PR #147 F1): a SKIP
            # stamped with the parse-default marker is the manager's
            # fail-soft net, never the voter's decision, so it enters
            # this decision census only when it coincides with a
            # correct skip -- under a MUST-skip render the recorded
            # SKIP complies with the verdict and counts correct as
            # ever. Under a MUST-vote render, or with no rendered
            # verdict at all (a defaulted ballot whose persisted field
            # is absent -- a committed single-era replay), the ballot
            # is censused by :func:`compute_defaulted_ballots` instead:
            # NEVER a missed skip and NEVER a threshold inversion -- a
            # degraded SKIP miscounted as a genuine inversion would
            # poison the §4.6 0-inversion HARD line on the very
            # re-record the fail-soft exists to unblock.
            if is_marked_default and (
                rendered_max is None or rendered_max >= SKIP_SUSPICION_THRESHOLD
            ):
                category = "diverted_defaulted"
            # CITATION-COERCED diversion (Task 17.2; audit §8 routed
            # contract (b)): a SKIP whose rationale is anchored by the
            # 16.6 citation-gate coercion marker is the gate working,
            # never the voter's decision, so it is diverted to its own
            # by-design bucket BEFORE the correct/missed/unclassified
            # tri-split and stays out of every decision read -- an
            # impostor's coerced SKIP is not an in-character decline, a
            # crew voter's is not a threshold inversion, and a
            # sub-threshold one is not a chosen correct skip (the 17.10
            # ruling: a forced eject poisons the decision channel the
            # verdict hinges on). The role- and verdict-blind divert
            # matches the invalid-target / teammate precedent. The
            # anchored match is sound because the citation gate is the
            # LAST guard in the manager's ballot chain, so this marker is
            # always the outermost prefix; any stacked 16.5/16.6 markers
            # ride inside it.
            elif _UNCITED_ZERO_FLAG_MARKER_PATTERN.match(ballot.rationale_text):
                category = "citation_coerced"
            elif rendered_max is None:
                category = "unclassified"
            elif rendered_max < SKIP_SUSPICION_THRESHOLD:
                category = "correct_skip"
            # MISSED ballots split role-first: an impostor voter is the
            # audited exclusion class regardless of any normalization
            # marker (in-character voting is sanctioned by the vote
            # prompt), then invalid-target normalizations, then the crew
            # discretionary-decline remainder.
            elif game.roles[ballot.voter] == "IMPOSTOR":
                category = "missed_impostor"
            elif _INVALID_VOTE_MARKER_PREFIX in ballot.rationale_text:
                category = "missed_invalid_target"
            else:
                category = "threshold_inversion"
            yield _SkipBallotView(
                meeting=meeting,
                ballot=ballot,
                rendered_max=rendered_max,
                category=category,
            )


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
    :class:`ConversionReport` docstring). A SKIP whose ``rationale_text`` is
    anchored by the 16.6 citation-gate coercion marker
    (:data:`~meetings.manager.UNCITED_ZERO_FLAG_EJECT_MARKER`) is diverted to
    ``citation_coerced_skip_ballots`` BEFORE the correct/missed/unclassified
    tri-split, regardless of the voter's role or rendered verdict (Task 17.2;
    audits/audit-phase-16-close.md §8 routed contract (b)). A voter with no
    parsed gate line is ``unclassified``, never assumed correct. MISSED ballots partition
    role-first: an impostor voter lands in ``missed_skip_impostor_voters``
    regardless of any normalization marker (the audited exclusion class —
    impostor in-character voting is sanctioned by the vote prompt, so it is
    never a crew gate bug), then invalid-target normalizations, then the crew
    discretionary-decline ``threshold_inversions`` remainder. Within the
    impostor bucket,
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
    citation_coerced_skip_ballots = 0
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

        # SKIP sentinels: fold the one-home per-ballot classification. The
        # DEFAULTED diversion is excluded from ``skip_ballots`` entirely
        # (it is censused by :func:`compute_defaulted_ballots`); the
        # citation-gate diversion IS a bucket of the partition.
        for view in _iter_skip_ballot_views(game):
            if view.category == "diverted_defaulted":
                continue
            skip_ballots += 1
            if view.category == "citation_coerced":
                citation_coerced_skip_ballots += 1
            elif view.category == "unclassified":
                unclassified_skip_ballots += 1
            elif view.category == "correct_skip":
                correct_skip_ballots += 1
            else:
                missed_skip_ballots += 1
                if view.category == "missed_impostor":
                    missed_skip_impostor_voters += 1
                    # The §7.12 guard-rewritten betrayal ballots, read off
                    # the impostor bucket's marker prefix so deterministic
                    # coercions and voluntary declines stay separable.
                    if _TEAMMATE_VOTE_MARKER_PREFIX in view.ballot.rationale_text:
                        missed_skip_teammate_coerced += 1
                elif view.category == "missed_invalid_target":
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
        citation_coerced_skip_ballots=citation_coerced_skip_ballots,
        missed_skip_impostor_voters=missed_skip_impostor_voters,
        missed_skip_teammate_coerced=missed_skip_teammate_coerced,
        missed_skip_invalid_target=missed_skip_invalid_target,
        threshold_inversions=threshold_inversions,
    )


class ThresholdInversionRecount(BaseModel):
    """The by-cause table behind the 19.5 re-doctrine (Task 19.5; triage C6).

    Frozen value object recounting :attr:`ConversionReport.threshold_inversions`
    by CAUSE — the instrument the post-13.13 reading of that bucket rests on
    (see the :class:`ConversionReport` bullet). The triage's proposed mechanism
    for the committed 87 was "unrecognized citation-gated SKIPs"; this recount
    refutes it over the bytes (the partition already diverts that marker and
    censuses it as ``citation_coerced_skip_ballots``) and replaces it with the
    measured shape: marker-free declines whose rendered mass sits at the
    advisory line.

    * ``threshold_inversions`` — the recount's own total, folded from the same
      per-ballot classification the census publishes, so it equals the
      published count by construction.
    * ``marker_free`` — inversions whose ``rationale_text`` carries NONE of the
      five manager markers this module pins (invalid target, teammate
      coercion, parse default, ballot redirect, citation gate). This is the
      bug cell: the diversions exist to keep by-design rewrites out of the
      remainder, so ``marker_free < threshold_inversions`` means a rewrite
      leaked in. It is FULL on all four committed sets.
    * ``rendered_below_0_70`` / ``rendered_0_70_to_0_80`` /
      ``rendered_at_or_above_0_80`` — the rendered-max distribution, a
      partition of the total. 0.70 and 0.80 are DESCRIPTIVE decimal band
      edges for reading the mass, NOT thresholds with semantics; the only
      threshold in the partition is
      :data:`~eval._suspicion_parse.SKIP_SUSPICION_THRESHOLD`, which is the
      lower edge of the first band by construction.
    * ``rendered_at_threshold`` — inversions rendered EXACTLY at the reference
      threshold (a sub-count of ``rendered_below_0_70``): the voters who
      declined at the advisory line itself, not above it.
    * ``in_skipped_meetings`` / ``in_crew_ejected_meetings`` /
      ``in_impostor_ejected_meetings`` — the outcome the meeting the ballot
      sat in actually reached, also a partition of the total: a discretionary
      decline in a meeting that still ejected an impostor cost nothing, while
      the SKIPPED mass is where the conservatism reads. A malformed
      ``EJECTED`` row with no ``ejected_player_id`` resolved nothing, so it
      counts as SKIPPED here — the module's malformed-EJECTED convention.

    Standalone, like the gp-7 companions: this is an analysis instrument
    pinned over committed bytes by its fixture test, NOT a field on
    :class:`TournamentEvalReport` (the committed wrapper shape is untouched).

    **Leak-safety.** Nine integers; no roles, transcripts, or engine-owned
    types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    threshold_inversions: int
    marker_free: int
    rendered_at_threshold: int
    rendered_below_0_70: int
    rendered_0_70_to_0_80: int
    rendered_at_or_above_0_80: int
    in_skipped_meetings: int
    in_crew_ejected_meetings: int
    in_impostor_ejected_meetings: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> ThresholdInversionRecount:
        counts = (
            self.threshold_inversions,
            self.marker_free,
            self.rendered_at_threshold,
            self.rendered_below_0_70,
            self.rendered_0_70_to_0_80,
            self.rendered_at_or_above_0_80,
            self.in_skipped_meetings,
            self.in_crew_ejected_meetings,
            self.in_impostor_ejected_meetings,
        )
        if any(count < 0 for count in counts):
            raise ValueError("threshold-inversion recount cells must be non-negative")
        bands = (
            self.rendered_below_0_70
            + self.rendered_0_70_to_0_80
            + self.rendered_at_or_above_0_80
        )
        if bands != self.threshold_inversions:
            raise ValueError(
                "the three rendered bands must equal threshold_inversions: "
                f"{self.rendered_below_0_70} + {self.rendered_0_70_to_0_80} + "
                f"{self.rendered_at_or_above_0_80} != {self.threshold_inversions}"
            )
        outcomes = (
            self.in_skipped_meetings
            + self.in_crew_ejected_meetings
            + self.in_impostor_ejected_meetings
        )
        if outcomes != self.threshold_inversions:
            raise ValueError(
                "the three outcome cells must equal threshold_inversions: "
                f"{self.in_skipped_meetings} + {self.in_crew_ejected_meetings} + "
                f"{self.in_impostor_ejected_meetings} != {self.threshold_inversions}"
            )
        # The at-threshold cell is a sub-count of the first band, not a
        # fourth band: the threshold IS that band's lower edge.
        if self.rendered_at_threshold > self.rendered_below_0_70:
            raise ValueError(
                "rendered_at_threshold cannot exceed rendered_below_0_70: "
                f"{self.rendered_at_threshold} > {self.rendered_below_0_70}"
            )
        if self.marker_free > self.threshold_inversions:
            raise ValueError(
                "marker_free cannot exceed threshold_inversions: "
                f"{self.marker_free} > {self.threshold_inversions}"
            )
        return self


def recount_threshold_inversions(
    report: TournamentReport | Sequence[GameReport],
) -> ThresholdInversionRecount:
    """Recount the §4.6 threshold inversions by cause (Task 19.5).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the other
    analyzers' signature). Pure: no I/O, no engine/agent/LLM calls.

    Folds the SAME module-private per-ballot classification the decision
    census consumes (:func:`_iter_skip_ballot_views`) and keeps only the
    ``threshold_inversion`` bucket, so ``threshold_inversions`` here is the
    published count by construction and the recount cannot drift from the
    partition it recounts. ``marker_free`` tests the five marker anchors this
    module pins; the rendered bands read the voter's recovered §4.6 max (never
    ``None`` in this bucket — the classification is defined over one, so a
    missing max fails loud); and the outcome cells read each ballot's meeting
    outcome plus ``roles[ejected_player_id]``, with a malformed ``EJECTED``
    row (no ejected id) counted as SKIPPED because it resolved nothing.

    See :class:`ThresholdInversionRecount` for what the cells mean and why
    0.70 / 0.80 are descriptive band edges rather than thresholds.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    threshold_inversions = 0
    marker_free = 0
    rendered_at_threshold = 0
    rendered_below_0_70 = 0
    rendered_0_70_to_0_80 = 0
    rendered_at_or_above_0_80 = 0
    in_skipped_meetings = 0
    in_crew_ejected_meetings = 0
    in_impostor_ejected_meetings = 0

    for game in games:
        for view in _iter_skip_ballot_views(game):
            if view.category != "threshold_inversion":
                continue
            threshold_inversions += 1

            rationale = view.ballot.rationale_text
            if not (
                _INVALID_VOTE_MARKER_PREFIX in rationale
                or _TEAMMATE_VOTE_MARKER_PREFIX in rationale
                or _VOTE_PARSE_DEFAULT_MARKER_PREFIX in rationale
                or _BALLOT_REDIRECT_MARKER_PREFIX in rationale
                or _UNCITED_ZERO_FLAG_MARKER_PATTERN.match(rationale)
            ):
                marker_free += 1

            rendered_max = view.rendered_max
            if rendered_max is None:
                raise ValueError(
                    "a threshold-inversion ballot cannot lack a rendered §4.6 "
                    "max: the classification is defined over one, so a missing "
                    f"value is a partition bug ({view.ballot.voter!r} in meeting "
                    f"{view.meeting.meeting_id!r})"
                )
            if rendered_max == SKIP_SUSPICION_THRESHOLD:
                rendered_at_threshold += 1
            if rendered_max < 0.70:
                rendered_below_0_70 += 1
            elif rendered_max < 0.80:
                rendered_0_70_to_0_80 += 1
            else:
                rendered_at_or_above_0_80 += 1

            ejected = view.meeting.ejected_player_id
            if view.meeting.outcome == "EJECTED" and ejected is not None:
                if game.roles[ejected] == "IMPOSTOR":
                    in_impostor_ejected_meetings += 1
                else:
                    in_crew_ejected_meetings += 1
            else:
                in_skipped_meetings += 1

    return ThresholdInversionRecount(
        threshold_inversions=threshold_inversions,
        marker_free=marker_free,
        rendered_at_threshold=rendered_at_threshold,
        rendered_below_0_70=rendered_below_0_70,
        rendered_0_70_to_0_80=rendered_0_70_to_0_80,
        rendered_at_or_above_0_80=rendered_at_or_above_0_80,
        in_skipped_meetings=in_skipped_meetings,
        in_crew_ejected_meetings=in_crew_ejected_meetings,
        in_impostor_ejected_meetings=in_impostor_ejected_meetings,
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
      HARD line. Before Task 10.12 this bucket was 0 BY CONSTRUCTION: a
      defaulted ballot's vote call fails before the recording client logs
      its prompt, so the rendered max was unrecoverable and EVERY defaulted
      ballot fell to ``defaulted_without_render`` (audit 2026-06-13-1816
      H-H-2). The manager now persists the rendered §4.6 max onto the
      ``deadline_default`` failed-call row
      (:attr:`~orchestrator.replay.FailedCallReplayEntry.rendered_vote_max`),
      so a defaulted ballot recorded under the field's era is classified
      here -- including a CREWMATE default under a real MUST-vote, the
      missed-eject this census exists to surface.
    * ``defaulted_under_must_skip`` -- the rendered max was below the
      threshold, so the degraded SKIP coincides with the correct decision:
      it stays a ``correct_skip_ballots`` entry in the decision census and
      appears here as telemetry only (the one deliberate overlap between
      the two surfaces).
    * ``defaulted_without_render`` -- no rendered gate line was recovered
      for the voter, from ``llm_calls`` OR the persisted
      ``rendered_vote_max`` failed-call field. Post-10.12 this is only a
      committed single-era replay (recorded before the field existed); the
      marker is then the only witness, which is why the bucket is keyed on
      it rather than left to drown in ``unclassified_skip_ballots``.

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
        # Persisted §4.6 verdict for each DEFAULTED vote (Task 10.12; audit
        # H-H-2): the same fallback the decision census reads, so the two
        # surfaces can never disagree about a defaulted voter's verdict.
        rendered_from_failed = _persisted_vote_verdict_maxes(game)
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
                    rendered_max = rendered_from_failed.get(
                        (meeting.meeting_id, ballot.voter)
                    )
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

    * ``genuine_class_conversion`` — the HISTORICAL Phase-10 cell. It WAS
      the phase's PRIMARY progress gate, computed by the owning
      :func:`eval.vote_correctness.compute_genuine_class_conversion` (the
      CANON-class definition imports the Task 10.1 detector classifier — one
      home, never a parallel implementation) and carried here so the whole
      gate surface reads from one block; its ``note`` field documents why
      raw ``ejection_accuracy`` parity with the artifact-era 0.63 is an
      invalid gate. Since Task 17.6 it is preserved as a LABELED,
      REPORTED-ONLY column: STARVED on this substrate (0/0 on baselines 4 and
      5 — the NO-DATA branch, not a regression) and NEVER a canary. The
      successor cell beside it is what canary bands read; see
      :data:`~eval.vote_correctness.LEGACY_ALIBI_CELL_NOTE`, which rides on
      that successor's ``legacy_note``.
    * ``supplied_channel_conversion`` — the Task-17.6 SUCCESSOR instrument,
      wired onto this gate surface by Task 19.5: the ONLY canary-eligible
      genuine-class cell from baseline 5 onward
      (audits/audit-phase-16-close.md §8 re-anchor, on the channels this
      substrate actually supplies — vents, sightings, whereabouts-lies). It
      is computed by the owning
      :func:`eval.vote_correctness.compute_supplied_channel_conversion` and
      never re-derived here; its ``note`` / ``legacy_note`` fields ship the
      pinned documentation strings
      (:data:`~eval.vote_correctness.SUPPLIED_CHANNEL_GATE_NOTE`,
      :data:`~eval.vote_correctness.LEGACY_ALIBI_CELL_NOTE`) so a reader of
      the report alone can tell the live canary from the historical column.
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

    **Leak-safety.** Pure aggregates (counts plus two nested blocks: the
    genuine-class cell's two counts, a rate, and a pinned documentation
    string, and the supplied-channel cell's per-channel counts, two rates,
    and two pinned documentation strings). No roles, no transcripts, no
    engine-owned types, so the blocks add no leak risk to the
    ``/eval/tournament-report`` surface (``tests/api/test_leak.py``).

    The post-init validator enforces the partition invariants fail-loud so an
    inconsistent result can never be constructed (mirrors
    :class:`ConversionReport`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    genuine_class_conversion: GenuineClassConversionReport
    supplied_channel_conversion: SuppliedChannelConversionReport
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
    :func:`eval.vote_correctness.compute_genuine_class_conversion`, and the
    Task-17.6 successor canary beside it by the owning
    :func:`eval.vote_correctness.compute_supplied_channel_conversion` (Task
    19.5) — never re-derived here. Lost openings count meetings whose first
    turn carries no
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
        supplied_channel_conversion=compute_supplied_channel_conversion(games),
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
# The Task 10.16 fifth channel, the crew belief-spread lever's signature
# (audit 2026-06-13-1816 C-C-1; the owner belief-spread-first decision
# 2026-06-14). Keyed on the 10.15 marker itself
# (:data:`agents.memory.beliefs.WITNESS_INFORM_REASON`) so the channel name
# IS the 10.15 band name and the attribution cannot drift from the lever it
# credits. See :func:`decompose_ejection_channels` for why it is
# MASS-attributed (visible-quantum), not band-presence-attributed: the
# single-witness inform is a recording-time fold (Task 10.15), so on the
# pre-inform committed W1 bytes its +0.05 was never applied and is absent
# from every rendered row — the channel correctly credits 0 there.
CHANNEL_SINGLE_WITNESS_INFORM: Final[str] = WITNESS_INFORM_REASON

# Float guard for lattice arithmetic on 2-decimal rendered values.
_CHANNEL_EPS: Final[float] = 1e-9


def decompose_ejection_channels(
    game: GameReport, meeting_index: int
) -> frozenset[str] | None:
    """Design channels behind one impostor ejection's rendered lift (10.6).

    Returns ``None`` unless ``game.meetings[meeting_index]`` is a
    well-formed ``EJECTED`` meeting whose ejected player is a true
    impostor; otherwise the subset of the five ``CHANNEL_*`` constants the
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
    * ``single_witness_inform`` (Task 10.16; the 10.15 belief-spread
      lever, keyed on :data:`agents.memory.beliefs.WITNESS_INFORM_REASON`)
      — the ejected subject re-derives into THIS meeting's single-witness
      inform band (``derive_belief_evidence(...).pre_vote_informed``, one
      home with the live fold) AND its +0.05 quantum is VISIBLE in the
      persistent mass: after the vent and carry quanta the residue is a
      whole number of body-proximity quanta plus exactly one
      ``ACCUSATION_SUSPICION_DELTA``. Unlike ``prior_meeting_carry``, the
      inform is MASS-attributed, not band-presence-attributed, and the
      reason is era-correctness: the band is re-derivable from any era's
      transcript, but the inform fold is recording-time (Task 10.15), so on
      the pre-inform committed W1 bytes the +0.05 was never applied and is
      absent from every rendered row — the channel credits 0 there
      (a band-presence rule would instead mis-credit the W1 ejections whose
      lift was body-proximity / accumulator driven) and the four prior
      channels stay byte-identical (the inform branch only fires, and only
      consumes its quantum, when that quantum is present, which never
      happens on the inform-inactive W1 set). On the 10.17 re-record, where
      the inform is freshly applied in the conversion meeting (pre-decay,
      lattice-clean), the +0.05 is aligned and the channel separates
      crew-lever conversions from toolkit effects. The conservative edge: an
      inform stacked on an already-DECAYED body quantum (a non-0.20-aligned
      residue) reads as body proximity, not inform — the 10.17 operator
      validates the inform-conversion count against the offline 37-bloc
      prediction (Task 10.15 DoD) rather than relying on this attribution
      alone for the headline.
    * ``body_proximity`` — mass remains after subtracting the vent delta,
      the carry ceiling (``ACCUSATION_SUSPICION_DELTA`` x prior accused
      meetings, floored at the remainder), and a visible single-witness
      inform quantum: decayed carry can only shrink below its ceiling, so a
      positive remainder cannot be carry and the only §6.3 channel left is
      Rule 1.

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
    all_flags = detect_contradictions(meeting.transcript, roster=roster)
    naming_flags = [flag for flag in all_flags if ejected in flag.subjects]
    flag_mass = 0.0
    if naming_flags:
        beliefs = BeliefState()
        beliefs.seed_player(ejected, suspicion=0.5, trust=0.5)
        # Thread THIS meeting's transcript so the offline flag-mass fold applies
        # the SAME self-refuted-alibi downgrade the vote-time render did (the
        # evidence-quality lever is unconditional since the Task-14.12 close; PR
        # #218 Codex review). Without it a self-refuted alibi would be scored at
        # full STRONG mass here while production rendered it WEAK, over-crediting
        # the contradiction channel and under-reading the persistent carry-in.
        lifted = apply_contradiction_rule(
            beliefs, naming_flags, transcript=meeting.transcript
        )
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
    # Single-witness inform (Task 10.16; the 10.15 crew belief-spread lever).
    # The ejected subject re-derives into THIS meeting's single-witness inform
    # band AND its +0.05 quantum is VISIBLE in the persistent mass: after the
    # vent and prior-meeting-carry quanta, the residue is a whole number of
    # body-proximity quanta (0.20) plus exactly one ACCUSATION_SUSPICION_DELTA.
    # The mass test is load-bearing, not the band alone: the band is
    # re-derivable from ANY era's transcript, but the inform fold is
    # recording-time (Task 10.15), so on the pre-inform committed W1 bytes the
    # +0.05 was never applied and is absent from every rendered row — a
    # band-presence rule would mis-credit the W1 ejections whose conversion was
    # body-proximity / accumulator driven, whereas this visible-quantum rule
    # credits 0 there and the existing channels stay byte-identical (the
    # consume below only runs when the quantum is present, which never happens
    # on W1). It consumes the 0.05 so a bare inform reads as the inform channel
    # alone, not a spurious sub-quantum body proximity.
    if _ejected_in_inform_band(meeting, ejected, roster, all_flags):
        remainder_hundredths = round(remaining * 100)
        inform_hundredths = round(ACCUSATION_SUSPICION_DELTA * 100)
        body_hundredths = round(BODY_PROXIMITY_SUSPICION_DELTA * 100)
        if (
            remainder_hundredths >= inform_hundredths
            and (remainder_hundredths - inform_hundredths) % body_hundredths == 0
        ):
            channels.add(CHANNEL_SINGLE_WITNESS_INFORM)
            remaining = round(remaining - ACCUSATION_SUSPICION_DELTA, 4)
    if remaining > _CHANNEL_EPS:
        channels.add(CHANNEL_BODY_PROXIMITY)
    return frozenset(channels)


def _ejected_in_inform_band(
    meeting: MeetingReport,
    ejected: PlayerId,
    roster: frozenset[PlayerId],
    flags: Sequence[ContradictionRef],
) -> bool:
    """Whether ``ejected`` re-derives into this meeting's single-witness inform band.

    One home: the band is exactly ``derive_belief_evidence(...).pre_vote_informed``
    (:func:`meetings.manager.derive_belief_evidence` over the recorded transcript,
    the SAME producer the live pre-vote fold uses), never a parallel
    re-implementation of the voice count. ``flags`` is the caller's already-derived
    contradiction set under the ballot-voter roster (matching the recording-time
    scope); it feeds the §6.3 Rule-5 ``contradicted`` exemption only and never the
    voice count, so passing it threaded keeps the detector re-run single.
    """

    evidence = derive_belief_evidence(
        meeting.transcript,
        contradictions=flags,
        roster=roster,
        trigger_kind=meeting.trigger,
    )
    return ejected in evidence.pre_vote_informed


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
      ``conversions_with_single_witness_inform`` (Task 10.16) is the fifth
      channel; it is 0 on the inform-inactive committed W1 bytes and only
      moves once the 10.17 re-record applies the 10.15 belief-spread lever
      (see :func:`decompose_ejection_channels`). It is a PRESENCE count like
      the others, NOT a partition bucket, so it does not enter the
      multi/single/unattributed sum.
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
    conversions_with_single_witness_inform: int
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
            self.conversions_with_single_witness_inform,
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
        CHANNEL_SINGLE_WITNESS_INFORM: 0,
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
        conversions_with_single_witness_inform=with_channel[
            CHANNEL_SINGLE_WITNESS_INFORM
        ],
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


# ---------------------------------------------------------------------------
# Task 10.16 Wave-2 metrics + gate spec (DESIGN.md §9, §11; audit
# 2026-06-13-1816 B-B-2 pacing inversion / C-C-1 conversion / D-D-1 toolkit /
# D-D-2 active-deflection; experiments/lab/report-deception-battery*.md). The
# gate the 10.17 re-record is judged on.
#
# The Wave-2 re-record measures TWO adversarial changes at once (the impostor
# toolkit AND the crew belief-spread lever) in ONE record, so the outcome win
# split is CONFOUNDED and is a GUARDRAIL, not a signal: the gate reads
# attribution-decomposed conversion + indistinguishability, never the split.
# Like the gp-7 companions these ship STANDALONE off the frozen
# TournamentEvalReport wrapper until the 10.17 re-record turns the era over;
# the metric CODE is independent of the source tasks — it reads whatever the
# bytes carry (do_task impostor = 0 on the committed W1 bytes, > 0 after the
# toolkit; inform conversions = 0 on W1 bytes, > 0 after the crew lever).
# ---------------------------------------------------------------------------

WAVE2_GATE_SPEC: Final[str] = """\
Wave-2 (10.17) gate spec — the THREE tiers are read SEPARATELY (audit
2026-06-13-1816; tasks/phase-10.md Stage 5). Two adversarial changes ride one
re-record (impostor toolkit + crew belief-spread), so the outcome win split is
confounded: it is a GUARDRAIL, never a directional signal.

HARD lines (validity — any red STOPS the re-record, nothing frozen is touched
to chase a number): game_over 50/50 on BOTH committed sets; friendly-fire 0;
betrayal 0 (the §7.12 teammate firewall holds); byte-identical reconstruction;
threshold_inversions 0 over every ballot (the §4.6 gate render + threshold are
frozen — a freshly-informed MUST-vote ballot is NOT an inversion); no
emergency-no-body fail-loud crash.

Wave-2 DIRECTIONAL gates (the attribution-decomposed signal, read against the
W1 baseline this module pins): impostor do_task > 0 and impostor wait-share
moving toward crew levels (IndistinguishabilityReport — the D-D-1 "never-tasks"
fingerprint the toolkit must erase, W1 baseline impostor do_task 0 / wait-share
~0.52 vs crew ~0.10); effective_deflection UP vs the ~5-9 W1 baseline
(EffectiveDeflectionReport — the active-deflection subcount, NOT the raw 27
counter-accused, which is dominated by SKIP-saved survivals, audit D-D-2);
conversion_per_meeting UP (ConversionPerMeetingReport — the pacing-inversion-
proof KPI, since raw meeting COUNT correlates with impostor wins, audit B-B-2);
the 10.15 single-witness inform conversions REALIZED vs the offline 37-bloc
prediction (decompose_ejection_channels' single_witness_inform channel — 0 on
W1 by construction, the crew-lever credit legible from the toolkit's effects);
the anti-railroad condition holds (wrong-ejection games do not rise even as
meetings lengthen).

Balance GUARDRAIL (reported, explicitly NOT a hard gate): impostor win rate in
a sane band. The split is a constant of the race structure with the W1
adversarial changes confounded into one record, so a single number cannot be
read as a Wave-2 signal — it is published with a NON-GATE label and bounds
sanity only. An A/B that lengthens games without raising conversion_per_meeting
REGRESSES the split (B-B-2); that is caught by the directional gates, not the
guardrail.
"""


class ConversionPerMeetingReport(BaseModel):
    """Impostor ejections per resolved meeting (Task 10.16; audit B-B-2/C-C-1).

    Frozen value object publishing the pacing-inversion-proof conversion KPI.
    The W1 close audit re-derived the pacing inversion (B-B-2): every impostor
    win sat in a 3-or-4-meeting game and ``corr(meetings, kills) = 0.73``, so a
    raw impostor-ejection COUNT rewards games that simply ran more meetings —
    exactly the games the impostor tends to win. Normalising by the resolved
    meeting count removes that confound: a Wave-2 A/B that lengthens games
    without converting more impostors per meeting does not move this number up,
    and the audit's sizing rule is to gate Wave-2 on it rather than on meeting
    count.

    * ``impostor_ejections`` — well-formed ``EJECTED`` meetings whose ejected
      player is a true impostor (mirrored from the owning
      :func:`eval.vote_correctness.compute_vote_correctness`, never re-derived).
    * ``resolved_meetings`` — every recorded meeting: a ``MeetingReport`` exists
      only once a meeting reached a vote and tallied a binary
      ``EJECTED``/``SKIPPED`` outcome (a meeting that aborted before resolving
      is a ``failed_call``, never a ``MeetingReport``), so each one is resolved.
    * ``conversion_per_meeting`` — ``impostor_ejections / resolved_meetings``;
      ``None`` (undefined, not 0.0) with no resolved meetings, the module's
      rate convention.

    **Leak-safety.** Two integers and a rate; no roles, transcripts, or
    engine-owned types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    impostor_ejections: int
    resolved_meetings: int
    conversion_per_meeting: float | None

    @model_validator(mode="after")
    def _validate(self) -> ConversionPerMeetingReport:
        if self.impostor_ejections < 0 or self.resolved_meetings < 0:
            raise ValueError("conversion-per-meeting counts must be non-negative")
        if self.impostor_ejections > self.resolved_meetings:
            raise ValueError(
                "impostor_ejections cannot exceed resolved_meetings (a meeting "
                f"ejects at most one player): {self.impostor_ejections} > "
                f"{self.resolved_meetings}"
            )
        if self.resolved_meetings == 0:
            if self.conversion_per_meeting is not None:
                raise ValueError(
                    "conversion_per_meeting must be None with no resolved "
                    "meetings: the rate is undefined, not 0.0"
                )
        else:
            if self.conversion_per_meeting is None:
                raise ValueError(
                    "conversion_per_meeting must be set when resolved_meetings > 0"
                )
            if not 0.0 <= self.conversion_per_meeting <= 1.0:
                raise ValueError(
                    "conversion_per_meeting must be in [0.0, 1.0]: "
                    f"{self.conversion_per_meeting}"
                )
        return self


def compute_conversion_per_meeting(
    report: TournamentReport | Sequence[GameReport],
    *,
    vote_correctness: VoteCorrectnessReport | None = None,
) -> ConversionPerMeetingReport:
    """Fold a tournament report into the conversion-per-meeting KPI (Task 10.16).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport`. Pure: no I/O. The
    numerator is mirrored from the owning
    :func:`eval.vote_correctness.compute_vote_correctness` (threaded in by the
    report builder so it is folded once, computed here otherwise); the
    denominator counts every recorded meeting, each of which resolved by
    construction.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)
    if vote_correctness is None:
        vote_correctness = compute_vote_correctness(games)
    resolved_meetings = sum(len(game.meetings) for game in games)
    rate = (
        vote_correctness.impostor_ejections / resolved_meetings
        if resolved_meetings > 0
        else None
    )
    return ConversionPerMeetingReport(
        impostor_ejections=vote_correctness.impostor_ejections,
        resolved_meetings=resolved_meetings,
        conversion_per_meeting=rate,
    )


def _strict_eject_plurality(meeting: MeetingReport) -> PlayerId | None:
    """The UNIQUE most-voted non-SKIP eject target, or ``None``.

    Returns ``None`` when no ballot named a player (every voter SKIPped) or
    when the top eject-vote count is tied — a tie resolves to SKIP under the
    frozen §5.2 tally (ties stay SKIPPED, the gp-8 owner decision), so it
    moved the plurality nowhere. Pure over the recorded ballots.
    """

    counts: dict[PlayerId, int] = {}
    for ballot in meeting.ballots:
        target = ballot.target
        if target == "SKIP":
            continue
        counts[target] = counts.get(target, 0) + 1
    if not counts:
        return None
    top = max(counts.values())
    leaders = [pid for pid, count in counts.items() if count == top]
    if len(leaders) != 1:
        return None
    return leaders[0]


class EffectiveDeflectionReport(BaseModel):
    """The active-deflection subcount, not the raw counter-accused (Task 10.16).

    Frozen value object isolating the impostor's actual deception SKILL from
    SKIP-saved survival (audit 2026-06-13-1816 D-D-2). Of the accused impostors
    who survived, many "counter-accused" (active) yet were saved only because
    the SKIP bloc won the plurality — survival, not deflection. The Wave-2 A/B
    must anchor to the subcount where the impostor's counter-accusation
    actually MOVED the eject-plurality OFF itself, NOT the raw active count
    (the audit's ~5-9 of 59, not the raw 27).

    The denominator chain (the audit's 68 / 59 / 27 on the committed W1 bytes):

    * ``accused_impostor_events`` — (meeting, living true impostor verbally
      accused by ANOTHER speaker) pairs; self-accusations excluded, the D-D-2
      convention shared with :class:`GateMetricsReport`.
    * ``accused_impostor_survivals`` — the subset the meeting did NOT eject.
    * ``active_survivals`` — survivals where the impostor COUNTER-ACCUSED
      (emitted at least one :class:`~meetings.schemas.AccusationClaim` against
      a player other than itself this meeting); the rest are passive.

    The active partition (``effective_deflections + skip_saved_active_survivals
    == active_survivals``):

    * ``effective_deflections`` — active survivals with a UNIQUE eject-vote
      plurality (:func:`_strict_eject_plurality`) on a player OTHER than the
      impostor: the plurality genuinely moved off. Splits exactly into
      ``named_target_deflections`` (the plurality landed on a player the
      impostor counter-accused — the counter-accusation steered the table) and
      ``third_party_deflections`` (it landed on a non-named third party). THIS
      is the gate subcount (~5-9 on W1: 5 named + 4 third-party).
    * ``skip_saved_active_survivals`` — the remainder: the eject-plurality
      still pointed at the impostor, or there was no unique plurality (a tie or
      an all-SKIP table). Saved by SKIP, lens-C territory, never deflection.

    **Leak-safety.** Seven integers; no roles, transcripts, or engine-owned
    types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    accused_impostor_events: int
    accused_impostor_survivals: int
    active_survivals: int
    effective_deflections: int
    named_target_deflections: int
    third_party_deflections: int
    skip_saved_active_survivals: int

    @model_validator(mode="after")
    def _validate(self) -> EffectiveDeflectionReport:
        counts = (
            self.accused_impostor_events,
            self.accused_impostor_survivals,
            self.active_survivals,
            self.effective_deflections,
            self.named_target_deflections,
            self.third_party_deflections,
            self.skip_saved_active_survivals,
        )
        if any(count < 0 for count in counts):
            raise ValueError("effective-deflection counts must be non-negative")
        if self.accused_impostor_survivals > self.accused_impostor_events:
            raise ValueError(
                "accused_impostor_survivals cannot exceed accused_impostor_events: "
                f"{self.accused_impostor_survivals} > {self.accused_impostor_events}"
            )
        if self.active_survivals > self.accused_impostor_survivals:
            raise ValueError(
                "active_survivals cannot exceed accused_impostor_survivals: "
                f"{self.active_survivals} > {self.accused_impostor_survivals}"
            )
        if (
            self.named_target_deflections + self.third_party_deflections
            != self.effective_deflections
        ):
            raise ValueError(
                "named + third-party deflections must equal effective_deflections: "
                f"{self.named_target_deflections} + {self.third_party_deflections} "
                f"!= {self.effective_deflections}"
            )
        if (
            self.effective_deflections + self.skip_saved_active_survivals
            != self.active_survivals
        ):
            raise ValueError(
                "effective + skip-saved must equal active_survivals: "
                f"{self.effective_deflections} + "
                f"{self.skip_saved_active_survivals} != {self.active_survivals}"
            )
        return self


def compute_effective_deflection(
    report: TournamentReport | Sequence[GameReport],
) -> EffectiveDeflectionReport:
    """Fold a tournament report into the effective-deflection split (Task 10.16).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport`. Pure: no I/O. The
    accused-impostor population reuses the D-D-2 convention (living true
    impostors verbally accused by ANOTHER speaker; ``roles`` subscripts fail
    loud like the recall lead); the eject-plurality is the frozen-tally-aware
    unique-non-tie :func:`_strict_eject_plurality`.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    events = 0
    survivals = 0
    active = 0
    named = 0
    third = 0
    skip_saved = 0

    for game in games:
        for meeting in game.meetings:
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
            plurality = _strict_eject_plurality(meeting)
            for impostor in accused_impostors:
                events += 1
                if (
                    meeting.outcome == "EJECTED"
                    and meeting.ejected_player_id == impostor
                ):
                    continue
                survivals += 1
                # ACTIVE: the impostor counter-accused another player this
                # meeting (a self-accusation is the ineffective D-D-6 class,
                # excluded — it names no deflection target).
                named_targets = {
                    claim.against
                    for turn in meeting.transcript.turns
                    if turn.speaker == impostor
                    for claim in turn.claims
                    if isinstance(claim, AccusationClaim) and claim.against != impostor
                }
                if not named_targets:
                    continue
                active += 1
                if plurality is None or plurality == impostor:
                    skip_saved += 1
                elif plurality in named_targets:
                    named += 1
                else:
                    third += 1

    return EffectiveDeflectionReport(
        accused_impostor_events=events,
        accused_impostor_survivals=survivals,
        active_survivals=active,
        effective_deflections=named + third,
        named_target_deflections=named,
        third_party_deflections=third,
        skip_saved_active_survivals=skip_saved,
    )


class ActionRoleTally(BaseModel):
    """The per-tick action-by-role ingest output (Task 10.16; audit D-D-1).

    Frozen carrier between the replay-walk ingest
    (:func:`eval.action_ingest.tally_actions_by_role`, the one path that reads
    the tick action stream the meeting-only eval model does not carry) and the
    pure :func:`compute_indistinguishability` fold. The seam is documented
    there; roles are re-derived from the seeder
    (:attr:`~eval.report_schema.GameReport.roles`, filled by the loader from
    the seeded setup), NEVER inferred from behaviour — the whole point is to
    measure whether behaviour BETRAYS the seeded role.

    * ``crewmate_action_counts`` / ``impostor_action_counts`` — set-wide
      counts of every recorded action type (``"wait"``, ``"do_task"``,
      ``"move"``, ``"kill"``, ...) keyed by the actor's seeded role. An action
      type absent for a role reads 0 (``do_task`` for impostors on W1).
    * ``per_game_player_wait_counts`` — for each game, the per-player count of
      ``"wait"`` actions, role-blind (for the top-idler concentration gauge,
      which is a per-game property: a player id repeats across games as a
      different agent, so concentration is never pooled cross-game).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    crewmate_action_counts: Mapping[str, int]
    impostor_action_counts: Mapping[str, int]
    per_game_player_wait_counts: tuple[tuple[int, ...], ...]


class IndistinguishabilityReport(BaseModel):
    """The "never-tasks" impostor fingerprint (Task 10.16; audit D-D-1).

    Frozen value object publishing how distinguishable an impostor is from a
    crewmate by tactical behaviour alone. On the committed W1 bytes the
    impostor ``do_task`` path is policy-unreachable (0 emissions) and impostors
    wait ~52% of their actions vs crew ~10% — a perfect fingerprint. The 10.17
    toolkit (Task 10.14) seeds pretend-task instances to fire the dormant
    ``do_task`` branch; this report is the baseline it must move (do_task > 0,
    wait-share toward crew).

    * ``crewmate_do_task`` / ``impostor_do_task`` — ``do_task`` emission counts
      by seeded role (impostor 0 on W1 — the dormant branch).
    * ``crewmate_wait`` / ``impostor_wait`` — ``wait`` emission counts by role.
    * ``crewmate_actions_total`` / ``impostor_actions_total`` — all recorded
      actions by role (the wait-share denominators).
    * ``crewmate_wait_share`` / ``impostor_wait_share`` — ``wait / total`` by
      role; ``None`` (undefined, not 0.0) when a role emitted no actions.
    * ``top_idler_wait_share`` — the share of a game's ``wait`` actions emitted
      by its single most-idle player, averaged over games with any waits: a
      concentration gauge (low = idle spread across seats; high = a few seats
      carry the idle). ``None`` when no game recorded a wait. D-D-1's idle is
      spread across slots, NOT a degenerate 2-player concentration, so this is
      a context gauge, not a hard gate.

    **Leak-safety.** Counts, rates, and one concentration share; no roles
    leak (the role split is the ground-truth axis being measured, never an
    agent-visible field), no transcripts, no engine-owned types.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    crewmate_do_task: int
    impostor_do_task: int
    crewmate_wait: int
    impostor_wait: int
    crewmate_actions_total: int
    impostor_actions_total: int
    crewmate_wait_share: float | None
    impostor_wait_share: float | None
    top_idler_wait_share: float | None

    @model_validator(mode="after")
    def _validate(self) -> IndistinguishabilityReport:
        counts = (
            self.crewmate_do_task,
            self.impostor_do_task,
            self.crewmate_wait,
            self.impostor_wait,
            self.crewmate_actions_total,
            self.impostor_actions_total,
        )
        if any(count < 0 for count in counts):
            raise ValueError("indistinguishability counts must be non-negative")
        for label, part, total in (
            ("crewmate_do_task", self.crewmate_do_task, self.crewmate_actions_total),
            ("impostor_do_task", self.impostor_do_task, self.impostor_actions_total),
            ("crewmate_wait", self.crewmate_wait, self.crewmate_actions_total),
            ("impostor_wait", self.impostor_wait, self.impostor_actions_total),
        ):
            if part > total:
                raise ValueError(f"{label} cannot exceed its role action total")
        for label, share, total in (
            (
                "crewmate_wait_share",
                self.crewmate_wait_share,
                self.crewmate_actions_total,
            ),
            (
                "impostor_wait_share",
                self.impostor_wait_share,
                self.impostor_actions_total,
            ),
        ):
            if total == 0:
                if share is not None:
                    raise ValueError(
                        f"{label} must be None when its role emitted no actions: "
                        "the share is undefined, not 0.0"
                    )
            elif share is None:
                raise ValueError(f"{label} must be set when its role acted")
            elif not 0.0 <= share <= 1.0:
                raise ValueError(f"{label} must be in [0.0, 1.0]: {share}")
        if self.top_idler_wait_share is not None and not (
            0.0 <= self.top_idler_wait_share <= 1.0
        ):
            raise ValueError(
                "top_idler_wait_share must be in [0.0, 1.0] or None: "
                f"{self.top_idler_wait_share}"
            )
        return self


def compute_indistinguishability(tally: ActionRoleTally) -> IndistinguishabilityReport:
    """Fold an action-by-role tally into the fingerprint report (Task 10.16).

    Pure over the tally (the I/O happened in
    :func:`eval.action_ingest.tally_actions_by_role`). Wait-share is per-role
    ``wait / total``; the top-idler concentration is the mean over games of the
    single most-idle player's share of that game's waits, computed only over
    games that recorded a wait (a zero-wait game has no top idler and is
    excluded rather than counted as 0).
    """

    crew = tally.crewmate_action_counts
    impostor = tally.impostor_action_counts
    crew_total = sum(crew.values())
    impostor_total = sum(impostor.values())

    per_game_shares = [
        max(waits) / sum(waits)
        for waits in tally.per_game_player_wait_counts
        if sum(waits) > 0
    ]
    top_idler = sum(per_game_shares) / len(per_game_shares) if per_game_shares else None

    return IndistinguishabilityReport(
        crewmate_do_task=crew.get("do_task", 0),
        impostor_do_task=impostor.get("do_task", 0),
        crewmate_wait=crew.get("wait", 0),
        impostor_wait=impostor.get("wait", 0),
        crewmate_actions_total=crew_total,
        impostor_actions_total=impostor_total,
        crewmate_wait_share=(
            crew.get("wait", 0) / crew_total if crew_total > 0 else None
        ),
        impostor_wait_share=(
            impostor.get("wait", 0) / impostor_total if impostor_total > 0 else None
        ),
        top_idler_wait_share=top_idler,
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
    bumps it only when older readers cannot interpret the shape). The Task
    10.4 ``gate_metrics`` block follows it again — wrapper-level only, inner
    shape untouched, version stays 2 — and both committed reports are
    regenerated in the same PR, so no pre-10.4 wrapper JSON survives to be
    read.

    The Task 19.14 ``deduction`` block is the same rule a fourth time: a
    wrapper-level aggregate (:class:`~eval.deduction_metrics
    .DeductionMetricsReport`) over the unchanged inner report, so
    ``format_version`` stays 2, and all four committed
    ``tournament-eval-report.json`` views are regenerated in the same PR so no
    pre-19.14 wrapper JSON survives to be read. It carries the proof-vs-inference
    cross-tab under BOTH of its partitions plus the rest of the deduction
    instrument (audits/audit-phase-19-triage.md §7 item 15); the metric logic
    lives entirely in its own module — this one only assembles.
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
    deduction: DeductionMetricsReport


def build_tournament_eval_report(
    report: TournamentReport, *, kill_craft: KillCraftSupplyCells | None = None
) -> TournamentEvalReport:
    """Run the §11.3 + W0.3 analyzers over ``report`` and wrap the results.

    Pure assembly: each metric is computed by its own public ``compute_*``
    entry point over the same :class:`~eval.report_schema.TournamentReport`, and
    the results are packed into a :class:`TournamentEvalReport`. No metric math
    is reimplemented here — this function only orchestrates the analyzers
    (including :func:`compute_meeting_rate`, :func:`compute_conversion_report`,
    :func:`compute_gate_metrics`, and Task 19.14's
    :func:`~eval.deduction_metrics.compute_deduction_metrics`) and bundles their
    outputs with the source report; it never re-derives a count inline. The
    vote-correctness result is computed once and threaded into the conversion
    analyzer so its mirrored precision-lead fields come from the same fold.

    ``kill_craft`` is the one OPTIONAL input that is not derivable from the
    report: the Task-18.2 witnessed / co-present evidence-supply cells need a
    state-hash-verified engine walk over a replay-set DIRECTORY. Callers that
    have one (``scripts/build_sample_report.py``) pass
    :func:`eval.kill_craft.compute_kill_craft_report`'s result and the deduction
    block carries ``witnessed_supply``; callers that do not (a live tournament,
    a hand-built test report) leave it ``None`` — the explicit "not supplied"
    sentinel, never a zero that would read as "no kills".
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
        deduction=compute_deduction_metrics(report, kill_craft=kill_craft),
    )


__all__ = [
    "CHANNEL_BODY_PROXIMITY",
    "CHANNEL_CONTRADICTION_FLAG",
    "CHANNEL_PRIOR_MEETING_CARRY",
    "CHANNEL_SINGLE_WITNESS_INFORM",
    "CHANNEL_VENT_WITNESS",
    "WAVE2_GATE_SPEC",
    "ActionRoleTally",
    "BallotTargetRedirectReport",
    "ConversionPerMeetingReport",
    "ConversionReport",
    "DefaultedBallotReport",
    "EffectiveDeflectionReport",
    "GateMetricsReport",
    "IndistinguishabilityReport",
    "MeetingRateReport",
    "MultiSignalConversionReport",
    "SupplyGaugesReport",
    "ThresholdInversionRecount",
    "TournamentEvalReport",
    "build_tournament_eval_report",
    "compute_ballot_target_redirects",
    "compute_conversion_per_meeting",
    "compute_conversion_report",
    "compute_defaulted_ballots",
    "compute_effective_deflection",
    "compute_gate_metrics",
    "compute_indistinguishability",
    "compute_meeting_rate",
    "compute_multi_signal_conversion",
    "compute_supply_gauges",
    "decompose_ejection_channels",
    "recount_threshold_inversions",
]
