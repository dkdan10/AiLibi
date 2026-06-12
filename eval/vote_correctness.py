"""Vote-correctness metric over a tournament report (DESIGN.md §11.3).

A pure analyzer that answers DESIGN.md §11.3's vote-correctness question: when
a meeting ejects an impostor, was the ejection *driven by real evidence* -- a
genuine contradiction naming the ejected player, or a kill-witness chain --
rather than a lucky or unfounded vote? A high impostor-ejection rate that is
not evidence-backed is a worse signal than a lower rate that is; this metric
separates the two so the impostor-ejection rate alone cannot be mistaken for
*correct* voting.

**``vote_correctness_rate`` is a bug-sentinel, NOT a KPI (Task 9.6; audit
audit-2026-06-09-0347 F-F-1 / gp-2).** In the live pipeline the §4.6 vote gate
only crosses the eject threshold when the contradiction detector flagged the
ejected player, so every impostor ejection arrives already carrying the naming
``ContradictionRef`` that :func:`_has_real_evidence`'s first disjunct counts:
``evidence_backed_impostor_ejections == impostor_ejections`` by construction
and the rate is **structurally pinned to 1.0**. It measures the engine's own
trigger, not voting quality -- a Wave-1 A/B run on it is blind. It stays
computed (removing it would churn the schema) and is kept as a sentinel: any
value below 1.0 on a recorded set means an impostor ejection happened WITHOUT
its own triggering evidence -- a detector/recording bug to chase, never a
conversion metric to optimize. The published conversion leads live on
:class:`eval.meeting_quality.ConversionReport`: ``ejection_accuracy`` (the
PRECISION lead, defined below) and the impostor-accused -> impostor-ejected
conversion rate (the RECALL lead).

The module reads only :mod:`eval.report_schema` data (composed of
:mod:`meetings.schemas` leaf types) and the post-game ``roles`` ground truth on
:class:`~eval.report_schema.GameReport`. It performs no I/O and imports nothing
from ``engine``, ``agents``, or ``llm`` -- it is a fold over
``GameReport.meetings``.

Decisions baked into this metric (recorded in the PR's ``## Decisions`` block):

* **Ground truth comes only from ``roles``.** ``roles[ejected] == "IMPOSTOR"``
  decides whether an ejection hit an impostor. An impostor identity is never
  inferred from an accusation or the vote outcome -- doing so would make the
  metric circular (it would measure agreement with the vote, not the
  correctness of it).

* **"Real evidence" predicate** (:func:`_has_real_evidence`) -- an ejection is
  evidence-backed iff at least one of two *structured* signals holds (free text
  is never parsed):

  1. A :class:`~meetings.schemas.ContradictionRef` in the meeting whose
     ``subjects`` include the ejected player (the detector already flagged a
     real ``alibi_conflict`` / ``alibi_vs_sighting`` naming them).
  2. A **kill-witness chain**: some
     :class:`~meetings.schemas.FoundBodyObservation` reports a body in room R
     at tick T, and some :class:`~meetings.schemas.SawPlayerObservation` with
     ``subject == ejected`` places that player in the same room R at a tick
     within :data:`KILL_WITNESS_TICK_WINDOW` of T. The two observations may
     come from different turns (one agent finds the body on the opening turn,
     another places the suspect at the scene on a later chain / opt-in turn).

  The accusation-at-scene variant is deliberately **excluded**: an
  :class:`~meetings.schemas.AccusationClaim` carries no location or tick, so
  "someone accused the ejected player" collapses back into the circular
  accusation/vote-driven signal this metric exists to avoid (DESIGN.md §11.3
  names only "a real contradiction or kill witness"). For the same reason the
  ballot ``primary_reason_id`` -> :class:`~meetings.schemas.MeetingTurn` chain is
  *not* a counted signal: it may corroborate a vote but, derived from the same
  accusation flow, cannot be the evidence that makes an ejection correct.

* **Kill-witness tick window K = 5 ticks** (:data:`KILL_WITNESS_TICK_WINDOW`),
  applied symmetrically as ``abs(sighting_tick - found_tick) <= K``. The engine
  is tick-based at a default 2 Hz (DESIGN.md §0/§4), so 5 ticks is ~2.5 s of
  game time -- wide enough to bridge the gap between a kill and another agent
  walking in to discover the body (the canonical ``kill_cooldown_ticks`` is 4)
  and the +/-1 tick action-queue resolution, yet tight enough that an unrelated
  sighting many ticks earlier or later does not spuriously place the suspect at
  the scene.

* **Denominator = impostor ejections.** The rate is evidence-backed impostor
  ejections / impostor ejections (DESIGN.md §11.3 frames vote correctness as
  impostor ejections backed by a real contradiction or kill witness). When
  there are zero impostor ejections the rate is :data:`None` -- the rate is
  *undefined*, not ``0.0`` (reporting ``0.0`` would falsely imply impostor
  ejections occurred and were all unfounded). Because this denominator
  **excludes the wrong (crewmate) ejections**, the rate alone overstates how
  accurate the table's ejections were: a ``1.0`` rate read in isolation can be
  mistaken for "every ejection was correct" when half the ejections were
  crewmates. The companion ``ejection_accuracy`` below closes that gap.

* **``ejection_accuracy`` is the published PRECISION lead (audit C-C-4, gp-7;
  promoted to lead by Task 9.6 / gp-2).** ``ejection_accuracy =
  impostor_ejections / total_ejections`` -- the share of *all* ejections that
  hit an impostor, NOT gated on evidence. It is the number a Wave-1 reader
  gates on, never ``vote_correctness_rate``: in the audited 7p/2i artifact set
  ``vote_correctness_rate`` was ``1.0`` (3/3 evidence-backed impostor
  ejections) while ``ejection_accuracy`` was ``0.5`` (3 impostor / 6 total
  ejections), because the rate silently dropped the 3 wrong crewmate
  ejections -- and on the 9.5 baseline the rate is *structurally* 1.0 (see the
  bug-sentinel note above) while ``ejection_accuracy`` reads 22/35 = 0.6286.
  Like the rate it is :data:`None` (undefined, not ``0.0``) when there were
  zero ejections at all. :class:`eval.meeting_quality.ConversionReport`
  mirrors it (same fold, never recomputed) so both Wave-1 leads read from one
  block on the shipped report.

* **Small-n flag.** ``vote_correctness_small_n`` is ``True`` when the rate's
  denominator (``impostor_ejections``) is below
  :data:`VOTE_CORRECTNESS_MIN_SAMPLE` -- a blunt "do not trust this rate as a
  gate yet" marker (the audit's vote_correctness rested on n=3, F-F-2). It is a
  flag, not a verdict: a flagged rate is under-powered, not wrong.

* **"Contradictions flagged but ignored" secondary signal (audit F-F-2).**
  ``contradictions_flagged_but_ignored`` counts ``SKIPPED`` meetings that
  carried at least one structured contradiction yet ejected no one -- the
  table was handed a flagged inconsistency and skipped anyway (36/45 SKIPPED
  meetings in the audit). It is a coarse "the deduction signal was present but
  unused" counter that survives even when ``impostor_ejections`` is too small
  for the rate to mean anything; it is NOT scoped to contradictions naming a
  living impostor (that stricter C-C-3 cut needs role ground truth per
  contradiction subject and is deferred).

* **Malformed ``EJECTED`` meetings are skipped.** Unlike
  :class:`meetings.schemas.MeetingResult`, :class:`~eval.report_schema.MeetingReport`
  does not enforce the ``outcome == "EJECTED"`` <-> non-``None``
  ``ejected_player_id`` coupling, so an ``EJECTED`` meeting with
  ``ejected_player_id is None`` is type-possible. It is treated as malformed
  partial-replay data and skipped (contributes to no bucket) rather than
  raising, matching the stated partial-replay robustness requirement. A *real*
  ejected player absent from ``roles`` is a different case: that is an internal
  inconsistency, so the ``roles`` subscript is left to fail loud.

**Task 10.4 (Phase-10 gate metrics; audit audit-2026-06-10-1820 gp-7 / C-C-6)
adds the phase's PRIMARY progress gate to this module:**
:func:`compute_genuine_class_conversion` /
:class:`GenuineClassConversionReport` — of the meetings where the repaired
detector hands the crew a *genuine-class* (CANON-interior) contradiction
naming a true impostor, how many convert that flag into that impostor's
ejection. Phase 10 gates on THIS pair (0/4 on the audited e750b40 set), never
on raw ``ejection_accuracy`` parity with the artifact-era 0.63 — that number
was built on detector artifacts (14/22 of the old impostor convictions carried
zero genuine-shaped flags), so parity with it would be railroading regained,
not detection recovered. :data:`GENUINE_CLASS_GATE_NOTE` ships that warning on
the report itself.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from eval.report_schema import GameReport, MeetingReport, TournamentReport
from meetings.schemas import (
    FoundBodyObservation,
    PlayerId,
    SawPlayerObservation,
)
from meetings.transcript import (
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_RETARGETED_PROXY,
    detect_contradictions,
)

# Symmetric tick tolerance for the kill-witness chain: a sighting of the ejected
# player counts as placing them at a body's scene when it is in the same room
# and within this many ticks of the body-found tick. See the module docstring
# for the rationale (default 2 Hz engine, canonical kill cooldown of 4 ticks).
KILL_WITNESS_TICK_WINDOW: Final[int] = 5

# Minimum number of impostor ejections (the ``vote_correctness_rate``
# denominator) below which the rate is flagged ``vote_correctness_small_n``.
# An explicit, documented threshold (see the PR's ## Decisions block): a rate
# over fewer than this many impostor ejections is under-powered as a gate -- the
# audit's vote_correctness rested on n=3 (F-F-2). Chosen as a round "need >= 10
# samples before trusting a proportion" rule of thumb; it flags interpretation
# only and changes no computed number.
VOTE_CORRECTNESS_MIN_SAMPLE: Final[int] = 10

# The metric-hygiene warning every shipped report carries beside the
# genuine-class numbers (Task 10.4 DoD; audit audit-2026-06-10-1820 gp-7
# items 1 and 3). Pinned as a module constant so tests can assert the
# committed reports ship it verbatim.
GENUINE_CLASS_GATE_NOTE: Final[str] = (
    "genuine_class_conversion is the PRIMARY Phase-10 progress gate. Raw "
    "ejection_accuracy comparisons against pre-repair eras are INVALID: the "
    "artifact-era 0.63 (and the mixed-era 0.476) were built on detector "
    "artifacts -- 14/22 of the old impostor convictions carried zero "
    "genuine-shaped flags -- so parity with those numbers would be "
    "railroading regained, not detection recovered. Gate on this supplied/"
    "converted pair and the accumulator/testimony channels; the win split is "
    "likewise excluded as a gate signal (constant ~90/10, zero "
    "ejection-driven wins)."
)


class VoteCorrectnessReport(BaseModel):
    """Aggregated vote-correctness result (DESIGN.md §11.3).

    Frozen value object summarizing how often impostor ejections were backed by
    real evidence across the analyzed games. ``total_ejections`` counts only
    well-formed ``EJECTED`` meetings (a malformed ``EJECTED`` meeting with no
    ``ejected_player_id`` is skipped, not counted); it partitions exactly into
    ``impostor_ejections`` + ``crewmate_ejections``.

    ``evidence_backed_impostor_ejections`` is the subset of
    ``impostor_ejections`` satisfying the "real evidence" predicate
    (:func:`_has_real_evidence`). ``vote_correctness_rate`` is
    ``evidence_backed_impostor_ejections / impostor_ejections`` -- the share of
    impostor ejections actually driven by evidence -- and is ``None`` (undefined,
    not ``0.0``) when there were no impostor ejections. **It is a bug-sentinel,
    NOT a KPI (Task 9.6; audit F-F-1 / gp-2):** the live §4.6 gate only ejects
    when the detector flagged the target, so on recorded sets the rate is
    structurally pinned to ``1.0`` and a drop below ``1.0`` signals an ejection
    not backed by its own triggering evidence (a bug to chase), never a
    conversion improvement to claim. Its denominator also excludes the wrong
    crewmate ejections, so even read naively a ``1.0`` cannot be mistaken for
    full ejection accuracy (audit C-C-4 / gp-7).

    ``ejection_accuracy`` is ``impostor_ejections / total_ejections`` -- the
    share of *all* ejections that hit an impostor (the full-denominator accuracy
    the rate omits) and the published Wave-1 PRECISION lead, mirrored onto
    :class:`eval.meeting_quality.ConversionReport` -- and is ``None``
    (undefined, not ``0.0``) when there were no ejections at all.
    ``vote_correctness_small_n`` flags an under-powered rate
    (``impostor_ejections < `` :data:`VOTE_CORRECTNESS_MIN_SAMPLE`).
    ``contradictions_flagged_but_ignored`` is the secondary "deduction signal
    present but unused" count: ``SKIPPED`` meetings that carried >= 1
    contradiction yet ejected no one (audit F-F-2). All three are
    interpretation aids; none changes the rate's value.

    The post-init validator enforces the bucket invariants fail-loud so an
    inconsistent result can never be constructed (mirrors
    :class:`eval.balance_eval.BalanceReport`).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_ejections: int
    impostor_ejections: int
    crewmate_ejections: int
    evidence_backed_impostor_ejections: int
    vote_correctness_rate: float | None
    ejection_accuracy: float | None
    vote_correctness_small_n: bool
    contradictions_flagged_but_ignored: int

    @model_validator(mode="after")
    def _validate_buckets(self) -> VoteCorrectnessReport:
        counts = (
            self.total_ejections,
            self.impostor_ejections,
            self.crewmate_ejections,
            self.evidence_backed_impostor_ejections,
            self.contradictions_flagged_but_ignored,
        )
        if any(count < 0 for count in counts):
            raise ValueError("vote-correctness counts must be non-negative")
        if self.impostor_ejections + self.crewmate_ejections != self.total_ejections:
            raise ValueError(
                "impostor_ejections + crewmate_ejections must equal total_ejections: "
                f"{self.impostor_ejections} + {self.crewmate_ejections} != "
                f"{self.total_ejections}"
            )
        if self.evidence_backed_impostor_ejections > self.impostor_ejections:
            raise ValueError(
                "evidence_backed_impostor_ejections cannot exceed impostor_ejections: "
                f"{self.evidence_backed_impostor_ejections} > {self.impostor_ejections}"
            )
        # ejection_accuracy is defined over total_ejections (None iff there were
        # no ejections at all), mirroring the rate's None-iff-undefined contract
        # but on the full denominator.
        if self.total_ejections == 0:
            if self.ejection_accuracy is not None:
                raise ValueError(
                    "ejection_accuracy must be None when there are no ejections: "
                    "the accuracy is undefined, not 0.0"
                )
        else:
            if self.ejection_accuracy is None:
                raise ValueError(
                    "ejection_accuracy must be set when total_ejections > 0"
                )
            if not 0.0 <= self.ejection_accuracy <= 1.0:
                raise ValueError(
                    f"ejection_accuracy must be in [0.0, 1.0]: {self.ejection_accuracy}"
                )
        if self.impostor_ejections == 0:
            if self.vote_correctness_rate is not None:
                raise ValueError(
                    "vote_correctness_rate must be None when there are no impostor "
                    "ejections: the rate is undefined, not 0.0"
                )
        else:
            if self.vote_correctness_rate is None:
                raise ValueError(
                    "vote_correctness_rate must be set when impostor_ejections > 0"
                )
            if not 0.0 <= self.vote_correctness_rate <= 1.0:
                raise ValueError(
                    "vote_correctness_rate must be in [0.0, 1.0]: "
                    f"{self.vote_correctness_rate}"
                )
        return self


def compute_vote_correctness(
    report: TournamentReport | Sequence[GameReport],
) -> VoteCorrectnessReport:
    """Fold a tournament report (or game sequence) into a vote-correctness summary.

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (the metric only needs
    the games). Pure: no I/O, no engine/agent/LLM calls.

    The ejection buckets consider only ``EJECTED`` meetings. For each, the
    ejected player's role is looked up by subscript on the game's ``roles``
    ground truth (fail-loud if a *real* ejected player is absent -- that is an
    internal inconsistency, not partial-replay data). A malformed ``EJECTED``
    meeting whose ``ejected_player_id`` is ``None`` is skipped (see the module
    docstring). ``ejection_accuracy`` and ``vote_correctness_small_n`` are
    derived from those buckets. The separate
    ``contradictions_flagged_but_ignored`` counter folds every ``SKIPPED``
    meeting that carried >= 1 contradiction (the secondary "signal present but
    unused" cut). Meetings with an empty transcript and games with no meetings
    contribute nothing and never raise.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    total_ejections = 0
    impostor_ejections = 0
    crewmate_ejections = 0
    evidence_backed = 0
    contradictions_flagged_but_ignored = 0

    for game in games:
        for meeting in game.meetings:
            # Secondary signal: a SKIPPED meeting that nonetheless carried a
            # flagged contradiction is "deduction signal present but unused"
            # (audit F-F-2). Counted for every game, independent of the ejection
            # buckets below.
            if meeting.outcome == "SKIPPED" and meeting.contradictions:
                contradictions_flagged_but_ignored += 1
            if meeting.outcome != "EJECTED":
                continue
            ejected = meeting.ejected_player_id
            if ejected is None:
                # Malformed: MeetingReport does not enforce EJECTED <-> non-None
                # ejected_player_id. Skip rather than raise (partial-replay).
                continue
            # Subscript, not .get(): a real ejected player missing from the role
            # ground truth is an internal inconsistency that must fail loud.
            role = game.roles[ejected]
            total_ejections += 1
            if role == "IMPOSTOR":
                impostor_ejections += 1
                if _has_real_evidence(meeting, ejected):
                    evidence_backed += 1
            else:
                crewmate_ejections += 1

    rate = evidence_backed / impostor_ejections if impostor_ejections > 0 else None
    ejection_accuracy = (
        impostor_ejections / total_ejections if total_ejections > 0 else None
    )

    return VoteCorrectnessReport(
        total_ejections=total_ejections,
        impostor_ejections=impostor_ejections,
        crewmate_ejections=crewmate_ejections,
        evidence_backed_impostor_ejections=evidence_backed,
        vote_correctness_rate=rate,
        ejection_accuracy=ejection_accuracy,
        vote_correctness_small_n=impostor_ejections < VOTE_CORRECTNESS_MIN_SAMPLE,
        contradictions_flagged_but_ignored=contradictions_flagged_but_ignored,
    )


def _has_real_evidence(meeting: MeetingReport, ejected: PlayerId) -> bool:
    """True iff structured evidence names the ejected player (DESIGN.md §11.3).

    The disjunction of the two schema-expressible signals -- a naming
    contradiction or a kill-witness chain. Free text, accusations, and ballots
    are never consulted (see the module docstring for why).
    """

    return _has_naming_contradiction(meeting, ejected) or _has_kill_witness_chain(
        meeting, ejected
    )


def _has_naming_contradiction(meeting: MeetingReport, ejected: PlayerId) -> bool:
    """True iff a flagged contradiction lists the ejected player as a subject."""

    return any(ejected in ref.subjects for ref in meeting.contradictions)


def _has_kill_witness_chain(meeting: MeetingReport, ejected: PlayerId) -> bool:
    """True iff a found-body and a co-located sighting of the ejected player meet.

    Collects every ``found_body`` observation and every ``saw_player``
    observation naming the ejected player across the meeting's turns (the
    opening turn carries the body-finder's ``found_body``; any turn may carry a
    ``saw_player`` placing the suspect), then looks for a pair sharing a room
    within :data:`KILL_WITNESS_TICK_WINDOW` ticks. Empty transcripts and turns
    with no matching observations yield ``False`` (never raise).
    """

    found_bodies: list[FoundBodyObservation] = []
    sightings: list[SawPlayerObservation] = []
    for turn in meeting.transcript.turns:
        for observation in turn.observations:
            if isinstance(observation, FoundBodyObservation):
                found_bodies.append(observation)
            elif (
                isinstance(observation, SawPlayerObservation)
                and observation.subject == ejected
            ):
                sightings.append(observation)

    return any(
        sighting.room == body.room
        and abs(sighting.tick - body.tick) <= KILL_WITNESS_TICK_WINDOW
        for body in found_bodies
        for sighting in sightings
    )


class GenuineClassConversionReport(BaseModel):
    """The Phase-10 PRIMARY progress gate (Task 10.4; DESIGN.md §11.3; gp-7).

    Frozen value object publishing the genuine-class conversion pair the
    Phase-10 waves gate on (audit audit-2026-06-10-1820 C-C-6: CANON_INTERIOR
    flags naming impostors — 4 supplied / 0 converted on the audited set).

    **Genuine-class (CANON-class) definition — one home, imported.** A
    (meeting, impostor) pair is SUPPLIED when re-running the repaired Task
    10.1 detector (:func:`meetings.transcript.detect_contradictions`, with
    the meeting's ballot-voter roster — every living participant casts
    exactly one ballot, the same roster recording-time detection received)
    over the recorded transcript emits at least one ``alibi_vs_sighting``
    flag naming that true impostor whose sighting is NOT endpoint-banded
    (no :data:`meetings.transcript.WEAK_REASON_ENDPOINT_TICK` in the
    description). Under the repaired detector every emitted
    ``alibi_vs_sighting`` flag already has canonically-disjoint room sets
    and an in-window sighting (placeholders, containment-consistent pairs,
    and echo restatements mint nothing), so non-endpoint == interior-tick ==
    exactly the audit's genuinely-diagnostic CANON_INTERIOR class. The pair
    is CONVERTED when that meeting ejected that impostor.

    Two definitional consequences, both deliberate:

    * **The self-stated weak band does NOT disqualify.** A fabricated alibi
      is self-stated by construction (audit D-D-3), so on current rules the
      genuine channel rides the weak band — all 4 supplied flags on the
      audited set are weak self-stated. Requiring an unmarked "strong" flag
      would define the gate to zero; recall past weak is the explicit D-D-3
      follow-on, not this metric's job.
    * **Recorded ``ContradictionRef`` rows are IGNORED; the detector is
      re-run.** On pre-repair recordings the recorded flags are 93%
      artifacts; re-derivation through the one-home classifier is what makes
      these numbers honest. The detector is a pure function of the
      transcript, so on post-repair recordings (Task 10.5 onward) re-derived
      flags equal recorded flags byte-for-byte and the re-run is a no-op.

    ``supplied`` counts (meeting, impostor) pairs — deduped per meeting, so
    a compound alibi pairing against N interior sightings supplies once, not
    N times (the gp-2 flag-fountain lesson applied to the gate's own
    denominator). ``conversion_rate`` is ``converted / supplied`` and
    ``None`` (undefined, not ``0.0``) when nothing was supplied, mirroring
    the module's rate convention. ``note`` ships
    :data:`GENUINE_CLASS_GATE_NOTE` on every report: raw
    ``ejection_accuracy`` comparisons against pre-repair eras are invalid
    (the 0.63 was artifact-built) and the win split is excluded as a gate
    signal (gp-7 items 1 and 3).

    **Leak-safety.** Two counts, a rate, and a pinned documentation string —
    no roles, transcripts, or engine-owned types are exposed.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    supplied: int
    converted: int
    conversion_rate: float | None
    note: str = GENUINE_CLASS_GATE_NOTE

    @model_validator(mode="after")
    def _validate_buckets(self) -> GenuineClassConversionReport:
        if self.supplied < 0 or self.converted < 0:
            raise ValueError("genuine-class counts must be non-negative")
        if self.converted > self.supplied:
            raise ValueError(
                f"converted cannot exceed supplied: {self.converted} > {self.supplied}"
            )
        if self.supplied == 0:
            if self.conversion_rate is not None:
                raise ValueError(
                    "conversion_rate must be None when nothing was supplied: "
                    "the rate is undefined, not 0.0"
                )
        else:
            if self.conversion_rate is None:
                raise ValueError("conversion_rate must be set when supplied > 0")
            if not 0.0 <= self.conversion_rate <= 1.0:
                raise ValueError(
                    f"conversion_rate must be in [0.0, 1.0]: {self.conversion_rate}"
                )
        return self


def genuine_class_subjects(meeting: MeetingReport) -> frozenset[PlayerId]:
    """One meeting's genuine-class (CANON-interior) subjects (Tasks 10.4, 10.6).

    The single home of the genuine-class membership rule: re-derive flags
    via :func:`meetings.transcript.detect_contradictions` under the
    ballot-voter roster and keep every subject of an ``alibi_vs_sighting``
    flag without the endpoint band (see
    :class:`GenuineClassConversionReport` for the full definitional
    rationale). Extracted from :func:`compute_genuine_class_conversion` in
    Task 10.6 so the gp-7 supply gauges (the genuine-subject share in
    :func:`eval.meeting_quality.compute_supply_gauges`) read the identical
    rule by import instead of re-deriving it. Role-blind by design: the
    caller applies ground truth (the conversion pair keeps impostors; the
    share gauge counts any genuine-class subject as supply). Pure and
    deterministic; a meeting with no ballots derives nothing (an
    explicitly-empty roster indexes nothing).

    Re-targeted proxy flags are NOT genuine class. A Task 10.6
    :data:`meetings.transcript.WEAK_REASON_RETARGETED_PROXY` flag names
    the PROXY SPEAKER — the player whose claim about someone else
    conflicts with both the sighting and the subject's own account — not
    a player whose own location a sighting contradicted. The genuine
    class is the alibi-LIE gauge (audit gp-7 item 1: "keep
    genuine_class_conversion as the alibi-lie gauge"), and the gate was
    baselined on that semantics; admitting the lying-about-others class
    would silently inflate the PRIMARY gate's supply (and the
    genuine-subject share gauge) with a flag shape whose evidence is one
    weak re-target, exactly across the 10.9 A/B this baseline anchors.
    On the committed Wave-0 bytes every re-target names a crewmate, so
    the supplied/converted pair is identical either way; the exclusion
    pins the DEFINITION, not these bytes.
    """

    roster = frozenset(ballot.voter for ballot in meeting.ballots)
    subjects: set[PlayerId] = set()
    for flag in detect_contradictions(meeting.transcript, roster=roster):
        if flag.kind != "alibi_vs_sighting":
            continue
        if WEAK_REASON_ENDPOINT_TICK in flag.description:
            continue
        if WEAK_REASON_RETARGETED_PROXY in flag.description:
            continue
        subjects.update(flag.subjects)
    return frozenset(subjects)


def compute_genuine_class_conversion(
    report: TournamentReport | Sequence[GameReport],
) -> GenuineClassConversionReport:
    """Fold a tournament report into the genuine-class conversion pair (10.4).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the other
    analyzers' signature). Pure: no I/O, no engine/agent/LLM calls — the
    repaired detector re-run is a pure function of each recorded transcript.

    Per meeting: take the genuine CANON-interior subjects from the one-home
    :func:`genuine_class_subjects` (the import of the Task 10.1 classifier,
    never a parallel implementation) and count each flagged true impostor
    once as SUPPLIED (``roles`` subscript — a flagged subject passed the
    living-roster filter, so one absent from the ground truth is an
    internal inconsistency that fails loud). The pair CONVERTS when the
    meeting's well-formed outcome ejected that impostor. A meeting with no
    ballots derives nothing (an explicitly-empty roster indexes nothing —
    the recording path always writes one ballot per living participant, so
    this arises only on hand-built partial data).
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    supplied = 0
    converted = 0
    for game in games:
        for meeting in game.meetings:
            for subject in genuine_class_subjects(meeting):
                if game.roles[subject] != "IMPOSTOR":
                    continue
                supplied += 1
                if (
                    meeting.outcome == "EJECTED"
                    and meeting.ejected_player_id == subject
                ):
                    converted += 1

    rate = converted / supplied if supplied > 0 else None
    return GenuineClassConversionReport(
        supplied=supplied,
        converted=converted,
        conversion_rate=rate,
    )


__all__ = [
    "GENUINE_CLASS_GATE_NOTE",
    "KILL_WITNESS_TICK_WINDOW",
    "VOTE_CORRECTNESS_MIN_SAMPLE",
    "GenuineClassConversionReport",
    "VoteCorrectnessReport",
    "compute_genuine_class_conversion",
    "compute_vote_correctness",
    "genuine_class_subjects",
]
