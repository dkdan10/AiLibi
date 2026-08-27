"""Vote-correctness metric over a tournament report (DESIGN.md §11.3).

A pure analyzer that answers DESIGN.md §11.3's vote-correctness question: when
a meeting ejects an impostor, was the ejection *driven by real evidence* -- a
genuine contradiction naming the ejected player, or a kill-witness chain --
rather than a lucky or unfounded vote? A high impostor-ejection rate that is
not evidence-backed is a worse signal than a lower rate that is; this metric
separates the two so the impostor-ejection rate alone cannot be mistaken for
*correct* voting.

**``vote_correctness_rate`` is a diagnostic, NOT a KPI.** It reports the share
of impostor ejections whose meeting ALSO carried one of the two structured
signals above naming the ejected player. Co-occurrence, not attribution: the
predicate never reads a ballot, so it cannot say the evidence is what
convicted -- only that the table had it on the record. A value below 1.0 is a
legal reading of this substrate, not a bug to chase. A
zero-flag EJECT is convictable by design: the citation gate
(:func:`meetings.manager.guard_ballot_citation`, unconditional) coerces an
eject ballot against an unflagged target to ``SKIP`` only when it cites
NOTHING, so a target the contradiction detector never flagged still converts on
a ballot citing a transcript turn or a private observation id. Never gate a
prompt A/B on this rate: the published conversion leads live on
:class:`eval.meeting_quality.ConversionReport` -- ``ejection_accuracy`` (the
PRECISION lead, defined below) and the impostor-accused -> impostor-ejected
conversion rate (the RECALL lead).

What the recorded sets read (evidence-backed / impostor ejections). All four were
recorded at the Phase-20 evidence-honesty slate -- model ``Qwen/Qwen3.6-27B``,
every template at ``qwen3_6_27b.v4``, the eight levers ON -- as each set's
``MANIFEST.md`` records. That slate is now the ``baseline-7`` substrate: the
record missed two of its own pre-registered bars -- the rule's verdict is FINDING
-- and the owner adopted it as canon regardless, by explicit override
(``audits/audit-phase-20-baseline-7.md`` §6.1).

* ``replays/samples/9p2i``: 78/85 = 0.9176
* ``replays/samples/4p1i``: 19/20 = 0.9500
* ``replays/ml_corpus/9p2i``: 229/254 = 0.9016
* ``replays/ml_corpus/4p1i``: 26/28 = 0.9286

``scripts/check_doc_facts.py`` re-derives all four rates from the committed
reports and the model and prompt-set tokens from the four manifests, and fails
when a stamp or the provenance drifts, or when this module claims a structural
pin the data contradicts -- so a re-record re-stamps these lines rather than
rotting them. The seven samples/9p2i ejections behind the shortfall are censused
seed by seed -- and classified -- in ``tests/eval/test_vote_correctness.py``.
Mind the two populations: **16** of those 85 ejections carry no naming
``ContradictionRef`` at all, and 9 of the 16 are evidence-backed anyway through
the kill-witness disjunct, so "zero-flag" is a strictly wider set than "not
evidence-backed" -- 16 zero-flag against 7 unbacked. (Baseline 6 read 8 of 78,
2 rescued, 6 unbacked.)

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
  ejections. The gap survives on the recorded sets: samples/9p2i reads
  ``vote_correctness_rate`` 0.9176 beside ``ejection_accuracy`` 85/99 =
  0.8586, because 14 of those 99 ejections took a crewmate.
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

**Task 17.6 (the genuine-class re-anchor; audits/audit-phase-16-close.md §8 +
§6; audits/audit-phase-16-baseline-4.md §6) adds the SUCCESSOR instrument
beside the legacy cell:** :func:`compute_supplied_channel_conversion` /
:class:`SuppliedChannelConversionReport`. The Phase-10 instrument above reads
0/0 (NO-DATA) on two consecutive substrates — the bespoke model stopped
volunteering checkable alibi lies (alibi claims 281 → 109, ``alibi_vs_*``
transcript flags 190 → 7, every one crew-subject; baseline-4 audit §6) and
single-tick roll-call placements are endpoint-banded out of the CANON-interior
class — so the close routed a re-anchor "on channels this substrate actually
supplies (vents, sightings, whereabouts-lies)" (close §8). The successor
measures the SAME question (supplied hard evidence against a subject →
conviction?) over the RECORDED :class:`~meetings.schemas.ContradictionRef`
rows (16.10's recorded-contradiction-id read discipline — never a detector
re-run) and is the canary-eligible genuine-class cell from baseline 5 onward;
the legacy alibi-anchored pair stays computed and rides the successor report
as a labeled, starved, reported-only column (:data:`LEGACY_ALIBI_CELL_NOTE`).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator

from eval.report_schema import GameReport, MeetingReport, TournamentReport
from meetings.schemas import (
    FoundBodyObservation,
    PlayerId,
    SawPlayerObservation,
    WhereaboutsClaim,
)
from meetings.transcript import (
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_PROXY_INTRA_TURN,
    WEAK_REASON_RETARGETED_PROXY,
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
    impostor ejections whose meeting ALSO carried structured evidence naming the
    ejectee -- and is ``None`` (undefined, not ``0.0``) when there were no
    impostor ejections. **It is a diagnostic, NOT a KPI:** the predicate reads
    no ballot, so the rate is co-occurrence, never attribution; and a value
    below ``1.0`` is legal on this substrate, because the citation gate lets an
    eject ballot convict a target the detector never flagged whenever the ballot
    cites a transcript turn or a private observation id. Its denominator also
    excludes the wrong crewmate ejections,
    so even a ``1.0`` cannot be read as full ejection accuracy. The recorded
    values per sample set, and the census of the six samples/9p2i ejections the
    predicate does not account for, are in the module docstring.

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
    (meeting, impostor) pair is SUPPLIED when the meeting's RECORDED flags
    (:func:`eval.meeting_quality.recorded_contradiction_flags` — the
    byte-exact output of the recording-time detector, which held the private
    grounding channels a transcript-only re-run cannot reach) carry at least
    one ``alibi_vs_sighting``
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
    * **The recorded ``ContradictionRef`` rows ARE the census.** The
      recording-time detector held the meeting's trigger kind and its three
      private grounding channels, none of which survive into the transcript,
      so a transcript-only re-run prices a different game — on the committed
      corpus it loses 43 of 120 non-vent flags and mints 46 the game never
      had. The gate reads the record
      (:func:`eval.meeting_quality.recorded_contradiction_flags`); the
      pre-repair recordings whose flags were 93% artifacts left the tree at
      the Task-10.5 re-record.

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

    The single home of the genuine-class membership rule: read the meeting's
    RECORDED flags via
    :func:`eval.meeting_quality.recorded_contradiction_flags` and keep every
    subject of an ``alibi_vs_sighting`` flag without the endpoint band (see
    :class:`GenuineClassConversionReport` for the full definitional
    rationale). Extracted from :func:`compute_genuine_class_conversion` in
    Task 10.6 so the gp-7 supply gauges (the genuine-subject share in
    :func:`eval.meeting_quality.compute_supply_gauges`) read the identical
    rule by import instead of re-deriving it. Role-blind by design: the
    caller applies ground truth (the conversion pair keeps impostors; the
    share gauge counts any genuine-class subject as supply). Pure and
    deterministic; a meeting the record carries no flags for derives nothing.

    Re-targeted proxy flags are NOT genuine class. A Task 10.6
    :data:`meetings.transcript.WEAK_REASON_RETARGETED_PROXY` flag (the
    CROSS-speaker case) and a Task 10.10
    :data:`meetings.transcript.WEAK_REASON_PROXY_INTRA_TURN` flag (the
    SAME-speaker case) both name the PROXY SPEAKER — the player whose
    claim about someone else is the odd account out — not a player whose
    own location a sighting contradicted. The genuine class is the
    alibi-LIE gauge (audit gp-7 item 1: "keep genuine_class_conversion as
    the alibi-lie gauge"), and the gate was baselined on that semantics;
    admitting either lying-about-others class would silently inflate the
    PRIMARY gate's supply (and the genuine-subject share gauge) with a
    flag shape whose evidence is one weak re-target, exactly across the
    10.9 A/B this baseline anchors. On the committed bytes the
    proxy-intra-turn re-targets are endpoint-banded or name a crewmate, so
    the supplied/converted pair is identical either way; the exclusion
    pins the DEFINITION, not these bytes.
    """

    # Local import: :mod:`eval.meeting_quality` imports this module at module
    # scope, so the shared census reaches this reader function-locally — the
    # ``training.bakeoff.goodhart`` acyclic-graph precedent. One home, not a
    # mirror.
    from eval.meeting_quality import recorded_contradiction_flags

    subjects: set[PlayerId] = set()
    # FROZEN (Phase 19 tier map, training/README.md): weak-reason membership is
    # English-substring matching on ContradictionRef.description — unreliable
    # under flag-wording/prompt-shape change. Bug fixes and evidence readers
    # only; no new search.
    for flag in recorded_contradiction_flags(meeting):
        if flag.kind != "alibi_vs_sighting":
            continue
        if WEAK_REASON_ENDPOINT_TICK in flag.description:
            continue
        if WEAK_REASON_RETARGETED_PROXY in flag.description:
            continue
        if WEAK_REASON_PROXY_INTRA_TURN in flag.description:
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
    census is a filter over each meeting's recorded flags.

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


# ---------------------------------------------------------------------------
# Task 17.6 — the successor instrument: supplied-channel conversion
# ---------------------------------------------------------------------------


SuppliedChannel: TypeAlias = Literal[
    "witnessed_vent", "sighting_contradiction", "whereabouts_lie"
]
"""The three evidence channels the baseline-5 substrate actually supplies.

The close audit's routing triple verbatim — "vents, sightings,
whereabouts-lies" (audits/audit-phase-16-close.md §8) — as channel keys:

* ``witnessed_vent`` — a recorded ``vent_sighting``
  :class:`~meetings.schemas.ContradictionRef` (Task 15.4): a spoken
  :class:`~meetings.schemas.SawVentObservation` grounded against the
  speaker's own typed witness records. Role-proving, always STRONG.
* ``sighting_contradiction`` — a recorded ``alibi_vs_sighting`` flag that
  does not reference a whereabouts claim: a subject's stated account
  contradicted by another speaker's first-hand sighting, held to the same
  interior-tick / non-proxy discipline as the legacy genuine class.
* ``whereabouts_lie`` — a recorded flag (any kind) whose event ids name a
  roll-call :class:`~meetings.schemas.WhereaboutsClaim` (Task 16.7): the
  claim's speaker self-placed on the public record and a recorded
  contradiction caught the placement out. Matched by event id, the 16.10
  fold's read (``eval.funnel._whereabouts_lies_detected``).
"""

SUPPLIED_CHANNELS: Final[tuple[SuppliedChannel, ...]] = (
    "witnessed_vent",
    "sighting_contradiction",
    "whereabouts_lie",
)

# The weak-reason markers that disqualify a recorded ``alibi_vs_sighting``
# flag from the sighting-contradiction channel — exactly the legacy
# genuine-class exclusions (endpoint band + both proxy re-target shapes), kept
# so the successor's sighting channel stays the interior-tick, own-location
# hard-evidence class the Phase-10 gate was defined over. Deliberately NOT
# applied to the whereabouts channel: a single-tick whereabouts claim is an
# endpoint of its own degenerate range by construction, so the endpoint band
# is what starved roll-call out of the legacy class — admitting the banded
# flags THERE, by event id, is the eval-side re-anchor (the detector's band
# itself is untouched; the record-time relaxation is routed elsewhere, per
# the Phase-17 designer ruling).
# Frozen metric site — same substring-membership caveat as the tier-map label
# in ``genuine_class_subjects`` above (Phase 19 tier map, training/README.md).
_SIGHTING_CHANNEL_EXCLUDED_MARKERS: Final[tuple[str, ...]] = (
    WEAK_REASON_ENDPOINT_TICK,
    WEAK_REASON_RETARGETED_PROXY,
    WEAK_REASON_PROXY_INTRA_TURN,
)

# The successor's on-report documentation string (mirrors
# GENUINE_CLASS_GATE_NOTE's role; pinned so tests can assert reports ship it
# verbatim).
SUPPLIED_CHANNEL_GATE_NOTE: Final[str] = (
    "supplied_channel_conversion is the Task-17.6 successor of "
    "genuine_class_conversion and the ONLY canary-eligible genuine-class cell "
    "from baseline 5 onward (audits/audit-phase-16-close.md §8: re-anchor on "
    "channels this substrate actually supplies). It reads the RECORDED "
    "contradiction rows — witnessed vents (vent_sighting), sighting "
    "contradictions (interior non-proxy alibi_vs_sighting), and "
    "whereabouts-lies (recorded flags naming a whereabouts claim by event "
    "id) — and measures the same question as the legacy cell: supplied hard "
    "evidence against a true impostor -> that impostor's ejection. The "
    "legacy alibi-anchored cell rides along as a reported column only; see "
    "legacy_note."
)

# The label the DoD requires on the preserved legacy cell: starved, reported
# only, never a canary — with the re-examination pointer for a future
# substrate that re-supplies checkable alibi lies.
LEGACY_ALIBI_CELL_NOTE: Final[str] = (
    "legacy_alibi_* is the Phase-10 alibi-anchored genuine-class cell "
    "(compute_genuine_class_conversion), preserved as a labeled REPORTED "
    "column: STARVED on this substrate and NEVER a canary. The alibi-lie "
    "supply collapsed across baselines 4 and 5 (alibi claims 281 -> 109, "
    "alibi_vs_* transcript flags 190 -> 7, every one crew-subject; "
    "audits/audit-phase-16-baseline-4.md §6) and single-tick roll-call "
    "placements are endpoint-banded out of the CANON-interior class, so the "
    "cell reads 0/0 (NO-DATA, not REGRESSION) on both sets. A future "
    "substrate that re-supplies checkable alibi lies re-examines this cell "
    "(audits/audit-phase-16-close.md §8)."
)


class SuppliedChannelConversionReport(BaseModel):
    """The Task-17.6 successor instrument — the canary-eligible cell.

    Frozen value object publishing the supplied-channel conversion pair the
    Phase-17 close (17.17) and any future canary bands read, beside the
    legacy alibi-anchored cell it succeeds.

    **The re-anchor decision and its provenance.** The Phase-10 primary
    instrument (:class:`GenuineClassConversionReport`) reads 0/0 on baselines
    4 AND 5 — the NO-DATA canary branch fired twice: the bespoke model
    stopped volunteering checkable alibi lies (alibi claims 281 → 109,
    ``alibi_vs_*`` transcript flags 190 → 7, every one crew-subject;
    audits/audit-phase-16-baseline-4.md §6) and roll-call placements are
    endpoint-banded out of the CANON-interior class (single-tick claims are
    endpoints of their own range by construction). The Phase-16 close routed
    the repair: "re-anchoring the instrument on channels this substrate
    actually supplies (vents, sightings, whereabouts-lies)"
    (audits/audit-phase-16-close.md §8; the §6 roll-call finding records the
    second consecutive 0/0). The Phase-17 designer ruling pins the shape:
    the re-anchor is EVAL-SIDE — the detector's endpoint band is untouched
    (a record-time substrate change routed to the absence gate's record or
    Phase 18) — and the old alibi-class cell stays a reported column. This
    report is that ruling made concrete; a future substrate that re-supplies
    alibi lies re-examines the legacy cell (see
    :data:`LEGACY_ALIBI_CELL_NOTE`).

    **Definition.** A (meeting, impostor) pair is SUPPLIED on a channel when
    the meeting's RECORDED :class:`~meetings.schemas.ContradictionRef` rows
    carry at least one qualifying flag naming that true impostor (see
    :func:`supplied_channel_subjects` for the one-home channel rule); it is
    CONVERTED when that meeting ejected that impostor (the same
    ejection→roles→subject join every conversion fold in this module uses).
    ``supplied`` / ``converted`` are the headline pair: the per-meeting UNION
    over channels, so a subject flagged on two channels in one meeting counts
    once (the gp-2 flag-fountain lesson, applied per channel AND across
    channels — the denominator-inflation guard the 17.6 hint names). The
    per-channel cells count the same pairs before the union, so they sum to
    at least the headline and each is bounded by it.

    **Recorded rows, never a re-run.** Unlike the legacy cell (which
    re-derives detection because pre-repair recordings carried artifact
    flags), the successor reads the recorded rows byte-for-byte — 16.10's
    recorded-contradiction-id discipline (``eval.funnel``'s whereabouts-lie
    fold; ``eval.vj_instruments``' flagged-subject read). Post-repair
    recordings are detector-pure by construction, and the ``vent_sighting``
    kind exists ONLY as a recording-time artifact (its grounding channel is
    private to the speaker and not reconstructible from report bytes), so
    the recorded rows are both necessary and sufficient here.

    **Witness-vs-testimony split — recorded as degenerate, not minted as a
    column (the 17.6 hint's design risk, answered).** A recorded
    ``vent_sighting`` flag exists only when the grounding chokepoint matched
    the SPOKEN claim against the speaker's OWN
    :class:`~meetings.schemas.VentWitnessRecord` (Task 15.4), so every
    vent-channel pair is witness-anchored by construction: the witness took
    a turn and casts a ballot at the same meeting, and a second-hand spoken
    vent claim mints no flag at all — it never enters the denominator. The
    ``alibi_vs_sighting`` channels carry no grounding marker in the recorded
    bytes, so witness-vs-testimony is not schema-measurable there. The
    committed bytes therefore make the split degenerate (all-witness) on the
    vent channel and unmeasurable on the others; it is documented here
    rather than shipped as an unmeasurable column.

    ``conversion_rate`` is ``converted / supplied`` and ``None`` (undefined,
    not ``0.0``) when nothing was supplied, mirroring the module's rate
    convention. ``legacy_alibi_supplied`` / ``legacy_alibi_converted`` /
    ``legacy_alibi_conversion_rate`` mirror
    :func:`compute_genuine_class_conversion` over the same games (one home,
    imported — never a parallel implementation), labeled by
    :data:`LEGACY_ALIBI_CELL_NOTE`. ``note`` ships
    :data:`SUPPLIED_CHANNEL_GATE_NOTE` on every report.

    **Leak-safety.** Counts, rates, and two pinned documentation strings —
    no roles, transcripts, or engine-owned types are exposed.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    supplied: int
    converted: int
    conversion_rate: float | None
    witnessed_vent_supplied: int
    witnessed_vent_converted: int
    sighting_contradiction_supplied: int
    sighting_contradiction_converted: int
    whereabouts_lie_supplied: int
    whereabouts_lie_converted: int
    legacy_alibi_supplied: int
    legacy_alibi_converted: int
    legacy_alibi_conversion_rate: float | None
    note: str = SUPPLIED_CHANNEL_GATE_NOTE
    legacy_note: str = LEGACY_ALIBI_CELL_NOTE

    @model_validator(mode="after")
    def _validate_buckets(self) -> SuppliedChannelConversionReport:
        channel_pairs = (
            (self.witnessed_vent_supplied, self.witnessed_vent_converted),
            (
                self.sighting_contradiction_supplied,
                self.sighting_contradiction_converted,
            ),
            (self.whereabouts_lie_supplied, self.whereabouts_lie_converted),
        )
        counts = (
            self.supplied,
            self.converted,
            self.legacy_alibi_supplied,
            self.legacy_alibi_converted,
            *(count for pair in channel_pairs for count in pair),
        )
        if any(count < 0 for count in counts):
            raise ValueError("supplied-channel counts must be non-negative")
        if self.converted > self.supplied:
            raise ValueError(
                f"converted cannot exceed supplied: {self.converted} > {self.supplied}"
            )
        for supplied, converted in channel_pairs:
            if converted > supplied:
                raise ValueError(
                    "a channel's converted cannot exceed its supplied: "
                    f"{converted} > {supplied}"
                )
        # The headline pair is the per-meeting union of the channel pairs, so
        # each channel is bounded by the headline and the headline by the sum.
        if any(supplied > self.supplied for supplied, _ in channel_pairs):
            raise ValueError("a channel's supplied cannot exceed the headline supplied")
        if any(converted > self.converted for _, converted in channel_pairs):
            raise ValueError(
                "a channel's converted cannot exceed the headline converted"
            )
        if self.supplied > sum(supplied for supplied, _ in channel_pairs):
            raise ValueError(
                "headline supplied cannot exceed the sum of the channel cells"
            )
        if self.converted > sum(converted for _, converted in channel_pairs):
            raise ValueError(
                "headline converted cannot exceed the sum of the channel cells"
            )
        if self.legacy_alibi_converted > self.legacy_alibi_supplied:
            raise ValueError(
                "legacy converted cannot exceed legacy supplied: "
                f"{self.legacy_alibi_converted} > {self.legacy_alibi_supplied}"
            )
        for supplied, rate, cell in (
            (self.supplied, self.conversion_rate, "conversion_rate"),
            (
                self.legacy_alibi_supplied,
                self.legacy_alibi_conversion_rate,
                "legacy_alibi_conversion_rate",
            ),
        ):
            if supplied == 0:
                if rate is not None:
                    raise ValueError(
                        f"{cell} must be None when nothing was supplied: "
                        "the rate is undefined, not 0.0"
                    )
            else:
                if rate is None:
                    raise ValueError(f"{cell} must be set when supplied > 0")
                if not 0.0 <= rate <= 1.0:
                    raise ValueError(f"{cell} must be in [0.0, 1.0]: {rate}")
        return self


def _whereabouts_claim_speakers(meeting: MeetingReport) -> dict[str, PlayerId]:
    """Every whereabouts claim's contradiction event id, mapped to its speaker.

    Mirrors ``meetings.transcript._turn_whereabouts_id`` exactly
    (``turn:{turn_id}:whereabouts:{index}``, ``index`` = the observation's
    position in ``turn.observations``) — the same byte-for-byte mirror
    ``eval.funnel._whereabouts_claim_event_ids`` (16.10's fold) keeps — so a
    recorded :class:`~meetings.schemas.ContradictionRef` referencing the
    claim is matched exactly. The speaker IS the claim's subject by the
    16.7 construction (a whereabouts claim carries no subject field), which
    is what lets the channel attribute a flagged claim to the player it
    incriminates. No living-roster filter is needed at this layer: taking a
    turn requires being a living participant, and the recorded flags already
    passed the production detector's roster chokepoint.
    """

    speakers: dict[str, PlayerId] = {}
    for turn in meeting.transcript.turns:
        for index, observation in enumerate(turn.observations):
            if isinstance(observation, WhereaboutsClaim):
                speakers[f"turn:{turn.turn_id}:whereabouts:{index}"] = turn.speaker
    return speakers


def supplied_channel_subjects(
    meeting: MeetingReport,
) -> Mapping[SuppliedChannel, frozenset[PlayerId]]:
    """One meeting's supplied-channel subjects, per channel (Task 17.6).

    The single home of the successor instrument's membership rule, the
    role-blind sibling of :func:`genuine_class_subjects` (the caller applies
    the ``roles`` ground truth). Reads ONLY the meeting's RECORDED
    :class:`~meetings.schemas.ContradictionRef` rows — never a detector
    re-run (the 16.10 discipline; see
    :class:`SuppliedChannelConversionReport`). Channel attribution is a
    partition of the recorded flags:

    * A flag whose ``event_a_id`` / ``event_b_id`` references a
      :class:`~meetings.schemas.WhereaboutsClaim` (matched by the
      ``turn:{turn_id}:whereabouts:{index}`` id scheme, order-independent
      because the detector sorts the pair) is the ``whereabouts_lie``
      channel, WHATEVER its kind — a lying roll-call answer is prosecuted
      through the existing alibi flag paths (its 16.7 design), so the kind
      varies while the event id is the stable anchor. The subject is the
      claim's speaker, guarded by ``speaker in flag.subjects`` so a flag
      that references a claim while naming someone else attributes nothing.
      The weak bands do NOT disqualify here — a single-tick claim is
      endpoint-banded by construction, and admitting the banded flag by
      event id is precisely the eval-side re-anchor (the detector band
      itself is untouched by this task).
    * A ``vent_sighting`` flag is the ``witnessed_vent`` channel: grounded,
      role-proving, always STRONG by construction (Task 15.4) — no band to
      filter.
    * Any other ``alibi_vs_sighting`` flag is the ``sighting_contradiction``
      channel iff its description carries none of the legacy exclusions
      (endpoint band, both proxy re-target shapes,
      :data:`_SIGHTING_CHANNEL_EXCLUDED_MARKERS`): the multi-tick sighting
      class keeps the CANON-interior, own-location discipline the Phase-10
      gate was defined over.
    * ``alibi_conflict`` / ``alibi_vs_physical`` flags that reference no
      whereabouts claim are NOT a supplied channel — they are the starved
      alibi-anchored substrate the legacy cell already reports (7 flags on
      baseline 4, every one crew-subject).

    Pure and deterministic; a meeting with no recorded contradictions
    supplies nothing on every channel.
    """

    whereabouts_speakers = _whereabouts_claim_speakers(meeting)
    subjects: dict[SuppliedChannel, set[PlayerId]] = {
        channel: set() for channel in SUPPLIED_CHANNELS
    }
    for flag in meeting.contradictions:
        flagged_claim_ids = tuple(
            event_id
            for event_id in (flag.event_a_id, flag.event_b_id)
            if event_id in whereabouts_speakers
        )
        if flagged_claim_ids:
            for event_id in flagged_claim_ids:
                speaker = whereabouts_speakers[event_id]
                if speaker in flag.subjects:
                    subjects["whereabouts_lie"].add(speaker)
            continue
        if flag.kind == "vent_sighting":
            subjects["witnessed_vent"].update(flag.subjects)
        elif flag.kind == "alibi_vs_sighting":
            if any(
                marker in flag.description
                for marker in _SIGHTING_CHANNEL_EXCLUDED_MARKERS
            ):
                continue
            subjects["sighting_contradiction"].update(flag.subjects)
    return {
        channel: frozenset(channel_subjects)
        for channel, channel_subjects in subjects.items()
    }


def compute_supplied_channel_conversion(
    report: TournamentReport | Sequence[GameReport],
) -> SuppliedChannelConversionReport:
    """Fold a tournament report into the successor conversion pair (17.6).

    Accepts either a :class:`~eval.report_schema.TournamentReport` or a bare
    sequence of :class:`~eval.report_schema.GameReport` (matching the other
    analyzers' signature). Pure: no I/O, no engine/agent/LLM calls — a fold
    over each meeting's recorded rows.

    Per meeting: take the per-channel subjects from the one-home
    :func:`supplied_channel_subjects` and count each flagged true impostor
    once per channel as that channel's SUPPLIED (``roles`` subscript — a
    subject absent from the ground truth is an internal inconsistency that
    fails loud, matching the legacy fold), and once in the headline pair via
    the cross-channel union (the denominator-inflation guard). A pair
    CONVERTS — per channel and in the headline — when the meeting's
    well-formed outcome ejected that impostor; a malformed ``EJECTED``
    meeting with no ``ejected_player_id`` can supply but never convert
    (partial-replay robustness, the module convention). The legacy
    alibi-anchored cell is computed by
    :func:`compute_genuine_class_conversion` over the same games and
    mirrored onto the report as its labeled, reported-only column.
    """

    games = report.games if isinstance(report, TournamentReport) else tuple(report)

    channel_supplied: dict[SuppliedChannel, int] = {
        channel: 0 for channel in SUPPLIED_CHANNELS
    }
    channel_converted: dict[SuppliedChannel, int] = {
        channel: 0 for channel in SUPPLIED_CHANNELS
    }
    supplied = 0
    converted = 0

    for game in games:
        for meeting in game.meetings:
            per_channel = supplied_channel_subjects(meeting)
            union: set[PlayerId] = set()
            for channel in SUPPLIED_CHANNELS:
                for subject in per_channel[channel]:
                    if game.roles[subject] != "IMPOSTOR":
                        continue
                    channel_supplied[channel] += 1
                    union.add(subject)
                    if (
                        meeting.outcome == "EJECTED"
                        and meeting.ejected_player_id == subject
                    ):
                        channel_converted[channel] += 1
            for subject in union:
                supplied += 1
                if (
                    meeting.outcome == "EJECTED"
                    and meeting.ejected_player_id == subject
                ):
                    converted += 1

    legacy = compute_genuine_class_conversion(games)
    return SuppliedChannelConversionReport(
        supplied=supplied,
        converted=converted,
        conversion_rate=converted / supplied if supplied > 0 else None,
        witnessed_vent_supplied=channel_supplied["witnessed_vent"],
        witnessed_vent_converted=channel_converted["witnessed_vent"],
        sighting_contradiction_supplied=channel_supplied["sighting_contradiction"],
        sighting_contradiction_converted=channel_converted["sighting_contradiction"],
        whereabouts_lie_supplied=channel_supplied["whereabouts_lie"],
        whereabouts_lie_converted=channel_converted["whereabouts_lie"],
        legacy_alibi_supplied=legacy.supplied,
        legacy_alibi_converted=legacy.converted,
        legacy_alibi_conversion_rate=legacy.conversion_rate,
    )


__all__ = [
    "GENUINE_CLASS_GATE_NOTE",
    "KILL_WITNESS_TICK_WINDOW",
    "LEGACY_ALIBI_CELL_NOTE",
    "SUPPLIED_CHANNELS",
    "SUPPLIED_CHANNEL_GATE_NOTE",
    "VOTE_CORRECTNESS_MIN_SAMPLE",
    "GenuineClassConversionReport",
    "SuppliedChannel",
    "SuppliedChannelConversionReport",
    "VoteCorrectnessReport",
    "compute_genuine_class_conversion",
    "compute_supplied_channel_conversion",
    "compute_vote_correctness",
    "genuine_class_subjects",
    "supplied_channel_subjects",
]
