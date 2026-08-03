"""Alibi-fabrication-rate metric (DESIGN.md §11.3, §5.4).

A pure analyzer over :class:`eval.report_schema.TournamentReport` that answers
DESIGN.md §11.3's alibi-fabrication question: *how often do impostors produce
alibis that survive contradiction detection?* A high survival rate means
impostors are getting away with fabricated cover; a low rate means the §5.4
contradiction detector is catching them. This is an impostor-effectiveness /
detector-effectiveness signal, **not** a per-agent score.

The metric reads only :mod:`eval.report_schema` data (plus the leaf
:mod:`meetings.schemas` types and :data:`engine.entities.Role`); it does no
I/O and makes no engine / agent / LLM calls.

Author -> role resolution
--------------------------
An *impostor alibi* is one whose **enclosing author** is an impostor, NOT one
whose :attr:`~meetings.schemas.AlibiClaim.subject` is an impostor (DESIGN.md
§11.3): an impostor may file an alibi *about another player*, so the subject
role is irrelevant to whether the alibi was fabricated by an impostor. The
author is the enclosing turn's :attr:`~meetings.schemas.MeetingTurn.speaker`
(every claim -- opening, reply, or opt-in -- is spoken by its turn's speaker).
The author's role is looked up by **subscript**
``roles[author]`` against the per-game ground-truth map. ``roles`` covers every
player by construction (:class:`eval.report_schema.GameReport`), so an author
absent from it signals a malformed report and is allowed to raise ``KeyError``
rather than being silently treated as a crewmate (AGENTS.md "no silent
fallbacks"). The all-crewmate / no-impostor-participant case is *not* malformed:
those authors resolve to ``"CREWMATE"`` and simply contribute nothing.

The alibi <-> contradiction join (the core decision)
----------------------------------------------------
:class:`~meetings.schemas.ContradictionRef` exposes only ``contradiction_id``,
``kind`` (``"alibi_conflict"`` / ``"alibi_vs_sighting"``), ``event_a_id``,
``event_b_id``, ``subjects`` and ``description`` -- it carries **no tick and no
room** -- so the "subject + tick-overlap + room" join DESIGN.md §5.4 uses
internally is NOT reconstructable from a ``ContradictionRef`` alone. This
analyzer uses the **subject-membership** rule:

    An impostor alibi about subject ``S`` is *caught* when some contradiction in
    the same meeting has an ``alibi_*`` ``kind`` and names ``S`` in its
    ``subjects``; otherwise the alibi *survives*.

Subject-membership is chosen over **event-id reconstruction** (rebuilding the
``report:{agent_id}@{tick}:claim:{index}`` / ``stmt:{statement_id}:claim:{index}``
ids the private ``meetings.transcript`` helpers emit and testing membership in
``{event_a_id, event_b_id}``) because event-id reconstruction would couple
``eval/`` to *private*, underscore-prefixed transcript helpers whose id format
could drift silently, and would also re-derive claim indices over the mixed
``claims`` tuples -- a fragile duplication. Subject-membership depends only on
the public, stable schema fields ``subjects`` and ``kind``.

**Accepted failure mode of subject-membership.** Because the §5.4 detector only
ever stamps a single alibi subject into ``ContradictionRef.subjects`` (see
``meetings/transcript.py``), naming is *coarse*:

* *Cross-author false positive* -- a contradiction between two OTHER authors'
  alibis about ``S`` still names ``S``, so an impostor's own (uninvolved) alibi
  about ``S`` is counted as caught.
* *Over-attribution* -- one contradiction naming ``S`` marks EVERY distinct
  impostor alibi about ``S`` as caught, even those the detector never paired.

Both errors push in the same direction: they over-count catches and therefore
**under-count survival**, so ``survival_rate`` is a conservative *lower bound*
on true fabrication survival. The rule is *exact* for the common case the
denominator leans on -- an impostor self-alibi (``subject == author``) where a
subject has a single alibi author -- which is why this metric is reported as a
detector/impostor-effectiveness signal rather than a precise per-alibi verdict.

Denominator
-----------
The denominator is *every* impostor-authored alibi (by author role), not only
self-alibis: DESIGN.md §11.3 counts "impostor alibis", and an impostor alibi
about another player is still fabricated cover. Self-alibis (``subject ==
author``) are merely the common case where subject-membership is exact (above);
they are not filtered out.

Multiplicity
------------
The same alibi *value* tuple ``(author, subject, from_tick, to_tick, room)`` can
appear more than once in one meeting -- e.g. an impostor restates a report alibi
verbatim in a statement. :class:`~meetings.schemas.AlibiClaim` has no id, so
such duplicates are collapsed by that value tuple and counted **once per
meeting** (``evidence`` is intentionally excluded from the key: it is supporting
detail, not part of the spatiotemporal claim). The dedup is per meeting because
the §5.4 detector runs per transcript; the same tuple in a *different* meeting
is a distinct alibi and counts again.

Rate convention
---------------
``survival_rate = survived / total_impostor_alibis``, or ``None`` when there are
no impostor alibis: the rate is **undefined, not 0.0** — the package's
None-iff-undefined convention, shared with
:attr:`eval.vote_correctness.VoteCorrectnessReport.vote_correctness_rate`,
:attr:`eval.meeting_quality.MeetingRateReport.meeting_rate`, and every rate on
:class:`eval.meeting_quality.ConversionReport`.

The pre-19.5 ``0.0`` is RETIRED (Task 19.5; audits/audit-phase-19-triage.md §7
item 6). It was chosen as a vacuous, division-safe value so Task 5.7 rendering
and the Task 5.8 regression suite need not special-case it, and that trade
inverted: a ``0.0`` here reads as "impostors filed alibis and NONE survived" —
the strongest possible detector result — when it actually means no impostor
filed an alibi at all. The dashboard's null-safe formatter renders ``None`` as
``n/a`` with no special case (so the papering-over is deleted, not moved), and
:class:`eval.prompt_regression.PromptRegressionMetrics` widens its
``alibi_survival_rate`` with it.

Partial-replay robustness: meetings with no alibis, no contradictions, or no
impostor participants contribute zero without raising, and a game with no
meetings contributes nothing.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Final

from pydantic import BaseModel, ConfigDict, model_validator

from engine.entities import Role
from eval.report_schema import MeetingReport, TournamentReport
from meetings.schemas import AlibiClaim, PlayerId, RoomId

# The ``alibi_*`` contradiction kinds the subject-membership join considers.
# Today this is the whole of :class:`~meetings.schemas.ContradictionRef`'s
# ``kind`` Literal, so the filter is currently total; it is kept explicit so a
# future non-alibi contradiction kind cannot silently start crediting catches.
# ``alibi_vs_physical`` (Task 13.4) IS an alibi contradiction -- an impostor
# whose fabricated alibi is exposed only by that STRONG kind must count as
# caught, not survived -- so it joins the set.
_ALIBI_CONTRADICTION_KINDS: Final[frozenset[str]] = frozenset(
    {"alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical"}
)

# Per-meeting dedup key for an alibi value: (author, subject, from_tick,
# to_tick, room). ``evidence`` is deliberately excluded -- it is supporting
# detail, not part of the spatiotemporal claim the detector reasons over.
_AlibiKey = tuple[PlayerId, PlayerId, int, int, RoomId]


class _FrozenModel(BaseModel):
    """Frozen, ``extra="forbid"`` base, matching the report-schema convention."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class AlibiFabricationReport(_FrozenModel):
    """Tournament-level alibi-fabrication result (DESIGN.md §11.3).

    * ``total_impostor_alibis`` -- distinct impostor-authored alibis across the
      tournament, deduped per meeting by their value tuple.
    * ``survived`` -- how many of those were *not* caught by any ``alibi_*``
      contradiction under the subject-membership rule.
    * ``survival_rate`` -- ``survived / total_impostor_alibis``, or ``None``
      when there are no impostor alibis -- the rate is undefined, not 0.0 (the
      package's None-iff-undefined convention; the pre-19.5 division-safe 0.0
      is retired). This is the fabrication-survival rate: high means impostors
      get away with fabricated cover, low means the §5.4 detector catches it.

    The post-init validator enforces the count and rate invariants fail-loud so
    an inconsistent result can never be constructed, mirroring
    :class:`eval.meeting_quality.ConversionReport`'s None-iff-undefined
    enforcement (AGENTS.md "no silent fallbacks").
    """

    total_impostor_alibis: int
    survived: int
    survival_rate: float | None

    @model_validator(mode="after")
    def _validate_rate(self) -> AlibiFabricationReport:
        if self.total_impostor_alibis < 0 or self.survived < 0:
            raise ValueError("alibi-fabrication counts must be non-negative")
        if self.survived > self.total_impostor_alibis:
            raise ValueError(
                "survived cannot exceed total_impostor_alibis: "
                f"{self.survived} > {self.total_impostor_alibis}"
            )
        if self.total_impostor_alibis == 0:
            if self.survival_rate is not None:
                raise ValueError(
                    "survival_rate must be None when there are no impostor "
                    "alibis: the rate is undefined, not 0.0"
                )
        else:
            if self.survival_rate is None:
                raise ValueError(
                    "survival_rate must be set when total_impostor_alibis > 0"
                )
            if not 0.0 <= self.survival_rate <= 1.0:
                raise ValueError(
                    f"survival_rate must be in [0.0, 1.0]: {self.survival_rate}"
                )
        return self


def compute_alibi_fabrication_rate(report: TournamentReport) -> AlibiFabricationReport:
    """Compute the alibi-fabrication-survival rate over a tournament report.

    Pure function (DESIGN.md §11.3): walks every meeting, counts the distinct
    impostor-authored alibis, and tests each against that meeting's
    contradictions under the subject-membership rule documented at module level.
    Survival is decided per meeting because the §5.4 contradiction detector runs
    per transcript.
    """

    total = 0
    survived = 0
    for game in report.games:
        roles = game.roles
        for meeting in game.meetings:
            caught_subjects = _subjects_named_in_alibi_contradictions(meeting)
            for _author, subject, _from_tick, _to_tick, _room in _impostor_alibi_keys(
                meeting, roles
            ):
                total += 1
                if subject not in caught_subjects:
                    survived += 1

    survival_rate = survived / total if total > 0 else None
    return AlibiFabricationReport(
        total_impostor_alibis=total,
        survived=survived,
        survival_rate=survival_rate,
    )


def _impostor_alibi_keys(
    meeting: MeetingReport, roles: Mapping[PlayerId, Role]
) -> set[_AlibiKey]:
    """Distinct impostor-authored alibi value tuples in one meeting.

    Returning a ``set`` performs the per-meeting multiplicity dedup; because the
    caller only counts and the survival check reads the ``subject`` carried in
    each key, the (unordered) iteration order does not affect the result.
    """

    return {
        (author, alibi.subject, alibi.from_tick, alibi.to_tick, alibi.room)
        for author, alibi in _iter_impostor_alibis(meeting, roles)
    }


def _iter_impostor_alibis(
    meeting: MeetingReport, roles: Mapping[PlayerId, Role]
) -> Iterator[tuple[PlayerId, AlibiClaim]]:
    """Yield ``(author, alibi)`` for every impostor-authored alibi in a meeting.

    The author is the enclosing turn's ``speaker``; its role is resolved by
    subscript so a player absent from ``roles`` fails loud.
    """

    transcript = meeting.transcript
    for turn in transcript.turns:
        author = turn.speaker
        if roles[author] != "IMPOSTOR":
            continue
        for claim in turn.claims:
            if isinstance(claim, AlibiClaim):
                yield author, claim


def _subjects_named_in_alibi_contradictions(meeting: MeetingReport) -> set[PlayerId]:
    """Subjects named by any ``alibi_*`` contradiction in the meeting.

    This is the subject-membership "caught" set: an impostor alibi about subject
    ``S`` is caught iff ``S`` appears here.
    """

    caught: set[PlayerId] = set()
    for contradiction in meeting.contradictions:
        if contradiction.kind in _ALIBI_CONTRADICTION_KINDS:
            caught.update(contradiction.subjects)
    return caught


__all__ = [
    "AlibiFabricationReport",
    "compute_alibi_fabrication_rate",
]
