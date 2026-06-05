"""Vote-correctness metric over a tournament report (DESIGN.md §11.3).

A pure analyzer that answers DESIGN.md §11.3's vote-correctness question: when
a meeting ejects an impostor, was the ejection *driven by real evidence* -- a
genuine contradiction naming the ejected player, or a kill-witness chain --
rather than a lucky or unfounded vote? A high impostor-ejection rate that is
not evidence-backed is a worse signal than a lower rate that is; this metric
separates the two so the impostor-ejection rate alone cannot be mistaken for
*correct* voting.

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

* **``ejection_accuracy`` is the honest accuracy denominator (audit C-C-4,
  gp-7).** ``ejection_accuracy = impostor_ejections / total_ejections`` -- the
  share of *all* ejections that hit an impostor, NOT gated on evidence. It is
  the field a Wave-1 reader should pair with ``vote_correctness_rate``: in the
  audited 7p/2i artifact set ``vote_correctness_rate`` was ``1.0`` (3/3
  evidence-backed impostor ejections) while ``ejection_accuracy`` was ``0.5``
  (3 impostor / 6 total ejections), because the rate silently dropped the 3
  wrong crewmate ejections. Like the rate it is :data:`None` (undefined, not
  ``0.0``) when there were zero ejections at all.

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
    not ``0.0``) when there were no impostor ejections. **It must be paired with
    ``ejection_accuracy`` to be read honestly:** the rate's denominator is
    impostor ejections ONLY, so it excludes the wrong crewmate ejections and a
    ``1.0`` rate read in isolation cannot be mistaken for full ejection accuracy
    (audit C-C-4 / gp-7).

    ``ejection_accuracy`` is ``impostor_ejections / total_ejections`` -- the
    share of *all* ejections that hit an impostor (the full-denominator accuracy
    the rate omits) -- and is ``None`` (undefined, not ``0.0``) when there were
    no ejections at all. ``vote_correctness_small_n`` flags an under-powered rate
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


__all__ = [
    "KILL_WITNESS_TICK_WINDOW",
    "VOTE_CORRECTNESS_MIN_SAMPLE",
    "VoteCorrectnessReport",
    "compute_vote_correctness",
]
