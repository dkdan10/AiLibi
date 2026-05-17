"""Meeting transcript helpers (DESIGN.md §5.2, §5.4).

This module hosts the statement-ordering helpers that
:class:`meetings.manager.MeetingManager` produces under the
producer-guaranteed canonical order contract (Task 3.8 C-3 resolution,
audit ``audits/audit-2026-05-16-0611-claude.md``), plus the
:func:`detect_contradictions` flag detector that indexes alibi /
saw-player claims across reports and statements (Task 3.11; DESIGN.md
§5.4 + §6.4).

Canonical statement order
=========================

A meeting transcript stores ``statements`` as a tuple. The canonical
order is:

* ascending :attr:`meetings.schemas.Statement.round_index`, then
* ascending insertion order within a round (i.e. the order in which
  participants submitted their statements, or were recorded with a
  default no-statement entry on deadline).

:class:`meetings.manager.MeetingManager` emits statements directly in
this order, so consumers may read ``transcript.statements`` in tuple
order without re-sorting. :func:`sort_statements_canonically` is
exposed for external producers (e.g. a future replay reconstructor)
that need to normalise a transcript they assembled out of order; it
uses a stable sort so insertion order within a round is preserved.

Contradiction detection
=======================

:func:`detect_contradictions` is data, not a verdict (DESIGN.md §5.4
"Flags are *information*, not a verdict"). It cross-references alibi
claims with publicly stated ``saw_player`` observations and returns a
sorted tuple of :class:`meetings.schemas.ContradictionRef` flags.
Downstream consumers -- the statement / vote prompt renderers, the
agent-side rendered memory view in §6.6 -- decide how to surface and
weigh these flags.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Literal

from meetings.schemas import (
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    PlayerId,
    ReportDocument,
    SawPlayerObservation,
    Statement,
)

_ContradictionKind = Literal["alibi_conflict", "alibi_vs_sighting"]


def sort_statements_canonically(
    statements: Iterable[Statement],
) -> tuple[Statement, ...]:
    """Return ``statements`` sorted by canonical ``(round_index, insertion_order)``.

    The sort is stable: within a round the input order is preserved.
    Manager-produced transcripts are already canonically ordered; this
    helper exists for external producers that need to normalise a
    transcript assembled out of order.
    """

    return tuple(sorted(statements, key=lambda statement: statement.round_index))


def is_canonically_ordered(statements: Iterable[Statement]) -> bool:
    """Return ``True`` if ``statements`` is sorted by ``round_index``.

    "Insertion order within a round" is, by definition, the tuple's
    own order, so this predicate cannot check it -- it only verifies
    the cross-round invariant. ``MeetingManager`` is the contract
    holder for the insertion-order half; downstream consumers may use
    this predicate as a cheap pre-condition check before processing
    a transcript.
    """

    last_round = -1
    for statement in statements:
        if statement.round_index < last_round:
            return False
        last_round = statement.round_index
    return True


# ---------------------------------------------------------------------------
# Contradiction detection (DESIGN.md §5.4, §6.4)
# ---------------------------------------------------------------------------


def detect_contradictions(
    transcript: MeetingTranscript,
) -> tuple[ContradictionRef, ...]:
    """Flag incompatible alibi and saw-player claims (DESIGN.md §5.4, §6.4).

    Indexes every :class:`AlibiClaim` and :class:`SawPlayerObservation`
    that appears in the transcript (across both Phase-1 reports and
    Phase-2 statement claims) and emits a
    :class:`ContradictionRef` per pair that cannot both be true:

    * ``alibi_conflict`` -- two alibis name the same ``subject`` in
      different rooms over overlapping tick ranges. Includes the case
      where a single reporter contradicts themselves and the case
      where two reporters disagree about a third party's location.
    * ``alibi_vs_sighting`` -- an alibi places ``subject`` in room R
      over a tick range, but another agent's ``saw_player(subject)``
      observation places them in a different room at a tick that
      falls inside the alibi range.

    Flags are *information*, not verdicts. The returned tuple is
    sorted by ``contradiction_id`` so the detector is deterministic
    across calls with the same transcript -- a precondition for the
    flags landing in a replay-stable rendered memory view (§6.6) and
    for the byte-identical replay invariant in DESIGN.md §0 rule 1.
    Sightings that match an alibi (same room, in-range tick) are
    silently ignored; the detector reports only what *cannot* both
    be true, not absence of evidence.

    The function is pure: it does not mutate the transcript and has
    no side effects. The same input always produces the same output.
    """

    alibis = tuple(_iter_alibis(transcript))
    sightings = tuple(_iter_sightings(transcript))

    flags: list[ContradictionRef] = []
    flags.extend(_detect_alibi_conflicts(alibis))
    flags.extend(_detect_alibi_vs_sightings(alibis=alibis, sightings=sightings))
    return tuple(sorted(flags, key=lambda flag: flag.contradiction_id))


# -- Internal: indexing -----------------------------------------------------


class _IndexedAlibi:
    """An :class:`AlibiClaim` paired with its synthetic event id."""

    __slots__ = ("event_id", "claim")

    def __init__(self, *, event_id: str, claim: AlibiClaim) -> None:
        self.event_id = event_id
        self.claim = claim


class _IndexedSighting:
    """A :class:`SawPlayerObservation` paired with its synthetic event id."""

    __slots__ = ("event_id", "observation")

    def __init__(self, *, event_id: str, observation: SawPlayerObservation) -> None:
        self.event_id = event_id
        self.observation = observation


def _iter_alibis(transcript: MeetingTranscript) -> Iterator[_IndexedAlibi]:
    for report in transcript.reports:
        for index, claim in enumerate(report.claims):
            if isinstance(claim, AlibiClaim):
                yield _IndexedAlibi(
                    event_id=_report_claim_id(report=report, index=index),
                    claim=claim,
                )
    for statement in transcript.statements:
        for index, claim in enumerate(statement.claims):
            if isinstance(claim, AlibiClaim):
                yield _IndexedAlibi(
                    event_id=_statement_claim_id(statement=statement, index=index),
                    claim=claim,
                )


def _iter_sightings(transcript: MeetingTranscript) -> Iterator[_IndexedSighting]:
    # Phase-1 reports are the only schema-defined source of
    # ``saw_player`` observations (DESIGN.md §5.3). Phase-2 statements
    # carry alibis / accusations / corroborations but not raw
    # observations, so this loop deliberately covers only reports.
    for report in transcript.reports:
        for index, observation in enumerate(report.observations):
            if isinstance(observation, SawPlayerObservation):
                yield _IndexedSighting(
                    event_id=_report_observation_id(report=report, index=index),
                    observation=observation,
                )


# -- Internal: detectors ----------------------------------------------------


def _detect_alibi_conflicts(
    alibis: tuple[_IndexedAlibi, ...],
) -> Iterator[ContradictionRef]:
    for i, left in enumerate(alibis):
        for right in alibis[i + 1 :]:
            if left.claim.subject != right.claim.subject:
                continue
            if left.claim.room == right.claim.room:
                continue
            if not _ranges_overlap(
                left.claim.from_tick,
                left.claim.to_tick,
                right.claim.from_tick,
                right.claim.to_tick,
            ):
                continue
            yield _build_contradiction(
                kind="alibi_conflict",
                event_a_id=left.event_id,
                event_b_id=right.event_id,
                subjects=(left.claim.subject,),
                description=_describe_alibi_conflict(left.claim, right.claim),
            )


def _detect_alibi_vs_sightings(
    *,
    alibis: tuple[_IndexedAlibi, ...],
    sightings: tuple[_IndexedSighting, ...],
) -> Iterator[ContradictionRef]:
    for alibi in alibis:
        for sighting in sightings:
            if sighting.observation.subject != alibi.claim.subject:
                continue
            if sighting.observation.room == alibi.claim.room:
                continue
            if not (
                alibi.claim.from_tick
                <= sighting.observation.tick
                <= alibi.claim.to_tick
            ):
                continue
            yield _build_contradiction(
                kind="alibi_vs_sighting",
                event_a_id=alibi.event_id,
                event_b_id=sighting.event_id,
                subjects=(alibi.claim.subject,),
                description=_describe_alibi_vs_sighting(
                    alibi=alibi.claim, sighting=sighting.observation
                ),
            )


# -- Internal: construction -------------------------------------------------


def _build_contradiction(
    *,
    kind: _ContradictionKind,
    event_a_id: str,
    event_b_id: str,
    subjects: tuple[PlayerId, ...],
    description: str,
) -> ContradictionRef:
    # Canonicalise the event-id pair so the same logical contradiction
    # produces the same :attr:`ContradictionRef.contradiction_id`
    # regardless of which iteration path discovered it first. This is
    # the replay-determinism guarantee: re-running the detector on the
    # same transcript yields byte-identical flags.
    a_id, b_id = sorted((event_a_id, event_b_id))
    contradiction_id = f"contra:{kind}:{a_id}|{b_id}"
    return ContradictionRef(
        contradiction_id=contradiction_id,
        kind=kind,
        event_a_id=a_id,
        event_b_id=b_id,
        subjects=subjects,
        description=description,
    )


def _describe_alibi_conflict(left: AlibiClaim, right: AlibiClaim) -> str:
    # Order the two alibis lexically by room so the description is
    # stable regardless of iteration order. The contradiction_id is
    # already canonicalised; doing the same for free text keeps the
    # rendered memory view byte-stable across replays.
    first, second = sorted((left, right), key=lambda claim: claim.room)
    return (
        f"Alibis place {first.subject} in {first.room} "
        f"(ticks {first.from_tick}-{first.to_tick}) and in {second.room} "
        f"(ticks {second.from_tick}-{second.to_tick}); intervals overlap."
    )


def _describe_alibi_vs_sighting(
    *, alibi: AlibiClaim, sighting: SawPlayerObservation
) -> str:
    return (
        f"Alibi places {alibi.subject} in {alibi.room} "
        f"(ticks {alibi.from_tick}-{alibi.to_tick}); sighting reports "
        f"{sighting.subject} in {sighting.room} at tick {sighting.tick}."
    )


# -- Internal: event ids and predicates -------------------------------------


def _report_claim_id(*, report: ReportDocument, index: int) -> str:
    return f"report:{report.agent_id}@{report.tick}:claim:{index}"


def _report_observation_id(*, report: ReportDocument, index: int) -> str:
    return f"report:{report.agent_id}@{report.tick}:obs:{index}"


def _statement_claim_id(*, statement: Statement, index: int) -> str:
    return f"stmt:{statement.statement_id}:claim:{index}"


def _ranges_overlap(a_from: int, a_to: int, b_from: int, b_to: int) -> bool:
    # Inclusive overlap, matching :class:`AlibiClaim`'s "tick ranges
    # are inclusive" contract.
    return a_from <= b_to and b_from <= a_to


__all__ = [
    "detect_contradictions",
    "is_canonically_ordered",
    "sort_statements_canonically",
]
