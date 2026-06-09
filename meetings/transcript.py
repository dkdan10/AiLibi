"""Meeting transcript helpers (DESIGN.md §5.2, §5.4).

This module hosts the pure, deterministic chain logic that backs the
reactive accusation chain (DESIGN.md §5.2) plus the
:func:`detect_contradictions` flag detector (DESIGN.md §5.4 + §6.4).

Pure chain logic (replay-safe)
==============================

The chain's next speaker and its termination are **pure functions of
the recorded turns** -- never of the LLM, the clock, or any hidden
state -- so a replay can walk the recorded ``transcript.turns`` and
reconstruct the discussion byte-for-byte without re-calling the model
(DESIGN.md §0 rule 1; Task 8.7 replay-walk):

* :func:`accusation_target` -- the player a turn accuses (its first
  :class:`~meetings.schemas.AccusationClaim`), or ``None``.
* :func:`next_chain_step` -- given the prior turn, who has spoken, the
  living-player count, and the turn count, returns the next speaker or a
  deterministic termination reason (the DESIGN.md §5.2 three-condition
  rule: no new accusation / re-accusation cycle / turn-count cap).
* :func:`walk_chain` -- replays a recorded transcript through
  :func:`next_chain_step`, validating that every recorded ``reply`` is
  exactly the turn the rule predicts and that the tail is ``opt_in``.

:class:`meetings.manager.MeetingManager` records turns in turn-index
order, so consumers may read ``transcript.turns`` in tuple order;
:func:`is_canonically_ordered` is the cheap pre-condition predicate.

Contradiction detection
========================

:func:`detect_contradictions` is data, not a verdict (DESIGN.md §5.4
"Flags are *information*, not a verdict"). It cross-references alibi
claims with publicly stated ``saw_player`` observations across every
turn and returns a sorted tuple of
:class:`meetings.schemas.ContradictionRef` flags. Downstream consumers
-- the turn / vote prompt renderers, the agent-side rendered memory view
in §6.6 -- decide how to surface and weigh these flags.

Task 9.7 (audit gp-1 precision): an ``alibi_vs_sighting`` flag whose
alibi is *self-stated* (the speaker is the alibi's own subject) or whose
alibi window is *narrow* (below :data:`NARROW_ALIBI_WINDOW_TICKS`) is a
known false-positive pattern -- 13/13 wrong ejections in the 9.5
baseline were lone contradictions of this shape. The detector still
emits the flag (the recorded flag set stays the honest full set) but
appends a :data:`WEAK_CONTRADICTION_MARKER_PREFIX` audit marker to the
description; :func:`is_weak_contradiction` is the predicate consumers
(belief Rule 2 in :mod:`agents.memory.beliefs`) use to apply a
graduated, below-gate suspicion delta instead of the full one.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Final, Literal

from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
)

_ContradictionKind = Literal["alibi_conflict", "alibi_vs_sighting"]

# Deterministic termination reasons for the reactive chain (DESIGN.md §5.2
# PHASE 2). Surfaced by :func:`next_chain_step` / :func:`walk_chain` so the
# replay-walk can assert *why* a recorded chain stopped, not just that it did.
# ``target_not_living`` is the practical fourth guard alongside DESIGN.md's
# three: the chain passes the floor to "the accused", so the accused must be a
# living participant -- an accusation of a dead / hallucinated id cannot be
# answered and terminates the chain (it would otherwise have no recorded reply
# to walk).
TERMINATION_NO_NEW_ACCUSATION: Literal["no_new_accusation"] = "no_new_accusation"
TERMINATION_TARGET_NOT_LIVING: Literal["target_not_living"] = "target_not_living"
TERMINATION_RE_ACCUSATION_CYCLE: Literal["re_accusation_cycle"] = "re_accusation_cycle"
TERMINATION_TURN_COUNT_CAP: Literal["turn_count_cap"] = "turn_count_cap"

ChainTermination = Literal[
    "no_new_accusation",
    "target_not_living",
    "re_accusation_cycle",
    "turn_count_cap",
]

# Sentinel distinguishing "no roster supplied" (legacy callers / unit tests
# that exercise the detector in isolation: index every subject) from an
# explicitly-empty roster (a meeting with no living participants: index
# nothing). ``frozenset() is not _NO_ROSTER`` so the empty-roster case is
# honoured rather than collapsed into "match everything".
_NO_ROSTER: frozenset[PlayerId] = frozenset({"\x00__no_roster_sentinel__\x00"})


# ---------------------------------------------------------------------------
# Pure chain logic (DESIGN.md §5.2) -- shared by the manager and the replay-walk
# ---------------------------------------------------------------------------


def accusation_target(turn: MeetingTurn) -> PlayerId | None:
    """Return the player ``turn`` accuses, or ``None`` (DESIGN.md §5.2).

    A turn accuses at most one player for chain-passing: the ``against``
    of its first :class:`~meetings.schemas.AccusationClaim` in claim
    order. A turn with no accusation claim (a defensive / "unsure" turn)
    returns ``None``, which terminates the chain.

    The manager records the *teammate-guarded* claims (Task 7.12 drops an
    impostor's accusation of a fellow impostor before the turn is
    stored), so this reads the same target the manager used to pass the
    chain -- the property that lets a replay reconstruct the chain from
    the recorded turns alone.
    """

    for claim in turn.claims:
        if isinstance(claim, AccusationClaim):
            return claim.against
    return None


@dataclass(frozen=True)
class ChainStep:
    """The deterministic decision after a chain turn (DESIGN.md §5.2 PHASE 2).

    Exactly one of the two fields is set: ``next_speaker`` names the
    player who speaks next (the accused), or ``termination`` gives the
    reason the chain stops. Pure data, no LLM.
    """

    next_speaker: PlayerId | None
    termination: ChainTermination | None


def next_chain_step(
    *,
    prev_turn: MeetingTurn,
    spoken: frozenset[PlayerId],
    living_ids: frozenset[PlayerId],
    turns_recorded: int,
) -> ChainStep:
    """Decide the next reactive-chain speaker or terminate (DESIGN.md §5.2).

    The chain passes the floor to the player ``prev_turn`` accused. It
    terminates (deterministically, replay-safe) when ANY of these holds,
    checked in order:

    (a) ``prev_turn`` names no new accusation ("unsure" / defensive),
    (-) the accused is not a living participant (dead / hallucinated id;
        the floor cannot pass to someone who is not at the table),
    (b) the accused has already taken a turn this meeting (cycle), or
    (c) ``turns_recorded`` has reached the living-player count (hard cap).

    Because every reply is spoken by a not-yet-spoken living accused, the
    cap (c) coincides with the cycle check (b) at the boundary; it is kept
    as an explicit, defensive bound so the chain can never run longer than
    the table.

    Args:
        prev_turn: the most recent chain turn (opening or reply).
        spoken: ids of every player who has already taken a turn.
        living_ids: ids of every living participant (the §5.2 cap is
            ``len(living_ids)``; the accused must be a member).
        turns_recorded: number of turns recorded so far (opening + chain).
    """

    target = accusation_target(prev_turn)
    if target is None:
        return ChainStep(None, TERMINATION_NO_NEW_ACCUSATION)
    if target not in living_ids:
        return ChainStep(None, TERMINATION_TARGET_NOT_LIVING)
    if target in spoken:
        return ChainStep(None, TERMINATION_RE_ACCUSATION_CYCLE)
    if turns_recorded >= len(living_ids):
        return ChainStep(None, TERMINATION_TURN_COUNT_CAP)
    return ChainStep(target, None)


@dataclass(frozen=True)
class ChainWalk:
    """The reconstruction of a recorded meeting's structure (Task 8.7).

    Produced by :func:`walk_chain` from a recorded transcript alone (no
    LLM). ``chain_speakers`` is the opening speaker followed by every
    reactive ``reply`` speaker in order; ``termination`` is why the chain
    stopped; ``opt_in_speakers`` are the terminal info-share speakers.
    """

    chain_speakers: tuple[PlayerId, ...]
    termination: ChainTermination | None
    opt_in_speakers: tuple[PlayerId, ...]


def walk_chain(
    transcript: MeetingTranscript, *, living_ids: frozenset[PlayerId]
) -> ChainWalk:
    """Replay-walk a recorded transcript without the LLM (DESIGN.md §5.2).

    Re-derives the chain by feeding the recorded turns back through
    :func:`next_chain_step` and asserting that every recorded ``reply``
    is exactly the turn the rule predicts (right speaker, ``reply_to``
    linked to the prior turn) and that the tail turns are ``opt_in``.
    This is the load-bearing replay invariant: the recorded
    ``transcript.turns`` reconstruct the discussion deterministically, so
    replay never re-calls the model. ``living_ids`` is the living-player
    set the meeting ran with (at replay time, the set of ballot voters).

    Raises:
        ValueError: if the transcript is not a well-formed chain (a
            reply whose speaker is not the predicted accused, a missing
            ``opening`` head, a broken ``reply_to`` link, or a non-
            ``opt_in`` turn after the chain). Failing loud here surfaces a
            non-deterministic / corrupted record rather than silently
            accepting an un-replayable meeting (AGENTS.md "no silent
            fallbacks").
    """

    turns = transcript.turns
    if not turns:
        return ChainWalk((), None, ())

    opening = turns[0]
    if opening.turn_kind != "opening" or opening.reply_to is not None:
        raise ValueError(
            "walk_chain: turn 0 must be an opening turn with reply_to=None; "
            f"got turn_kind={opening.turn_kind!r}, reply_to={opening.reply_to!r}"
        )

    chain: list[MeetingTurn] = [opening]
    spoken: set[PlayerId] = {opening.speaker}
    prev = opening
    index = 1
    termination: ChainTermination | None
    while True:
        step = next_chain_step(
            prev_turn=prev,
            spoken=frozenset(spoken),
            living_ids=living_ids,
            turns_recorded=len(chain),
        )
        if step.next_speaker is None:
            termination = step.termination
            break
        if index >= len(turns):
            raise ValueError(
                "walk_chain: chain predicts a reply by "
                f"{step.next_speaker!r} but the transcript has no turn at "
                f"index {index}; the recorded chain is truncated"
            )
        turn = turns[index]
        if turn.turn_kind != "reply":
            raise ValueError(
                f"walk_chain: expected a reply turn at index {index}, "
                f"got turn_kind={turn.turn_kind!r}"
            )
        if turn.speaker != step.next_speaker:
            raise ValueError(
                f"walk_chain: reply at index {index} is by {turn.speaker!r} "
                f"but the accusation chain predicts {step.next_speaker!r}"
            )
        if turn.reply_to != prev.turn_id:
            raise ValueError(
                f"walk_chain: reply at index {index} links to "
                f"{turn.reply_to!r}, expected the prior turn {prev.turn_id!r}"
            )
        chain.append(turn)
        spoken.add(turn.speaker)
        prev = turn
        index += 1

    opt_in_turns = turns[index:]
    for turn in opt_in_turns:
        if turn.turn_kind != "opt_in":
            raise ValueError(
                f"walk_chain: turn {turn.turn_index} after the chain must be "
                f"opt_in, got turn_kind={turn.turn_kind!r}"
            )

    return ChainWalk(
        chain_speakers=tuple(turn.speaker for turn in chain),
        termination=termination,
        opt_in_speakers=tuple(turn.speaker for turn in opt_in_turns),
    )


# ---------------------------------------------------------------------------
# Turn ordering (DESIGN.md §5.2)
# ---------------------------------------------------------------------------


def sort_turns_canonically(turns: Iterable[MeetingTurn]) -> tuple[MeetingTurn, ...]:
    """Return ``turns`` sorted by ascending ``turn_index``.

    The sort is stable: turns sharing a ``turn_index`` keep input order
    (a manager-produced transcript never does, since ``turn_index`` is a
    unique ordinal). This helper exists for an external producer that
    assembled a transcript out of order; the manager already emits turns
    in ``turn_index`` order.
    """

    return tuple(sorted(turns, key=lambda turn: turn.turn_index))


def is_canonically_ordered(turns: Iterable[MeetingTurn]) -> bool:
    """Return ``True`` if ``turns`` is in canonical chain-turn order.

    Canonical order is the contiguous ordinal sequence the chain emits:
    each turn's ``turn_index`` equals its position (0, 1, 2, ...). This
    replaces the old ``round_index``-keyed predicate -- a chain has no
    rounds, only the single ordered turn list (DESIGN.md §5.2).
    Consumers may use this as a cheap pre-condition check before
    processing a transcript.
    """

    for position, turn in enumerate(turns):
        if turn.turn_index != position:
            return False
    return True


# ---------------------------------------------------------------------------
# Contradiction detection (DESIGN.md §5.4, §6.4)
# ---------------------------------------------------------------------------

# Task 9.7 weak-signal classification (DESIGN.md §5.4; audit
# audit-2026-06-09-0347 gp-1 precision). An ``alibi_vs_sighting`` whose
# alibi window spans fewer than this many ticks is tick-boundary noise:
# movement resolves one room per tick, so a 1-2 tick claim and a sighting
# at the range edge can both be honest accounts of the same transit.
NARROW_ALIBI_WINDOW_TICKS: Final[int] = 2

# Audit-trail marker appended to a weak ``alibi_vs_sighting`` description.
# Mirrors the canonical-marker convention in :mod:`meetings.manager`
# (``INVALID_VOTE_TARGET_MARKER`` et al.): a pinned literal downstream
# code matches on. :func:`is_weak_contradiction` is the one reader; the
# description also renders into turn / ballot prompts, so the LLM sees
# *why* the flag is down-weighted (§5.4 "flags are information"). The
# marker is detector-appended, never parsed back out of LLM free text,
# and the full flag set is still emitted -- weak flags are down-weighted
# by belief Rule 2, not filtered. Pin the literal exactly.
WEAK_CONTRADICTION_MARKER_PREFIX: Final[str] = "[weak signal: "

# Reason literals joined (in this order, "; "-separated) inside the weak
# marker. Self-stated: the alibi's speaker is its own subject, so a third
# party's sighting contradicts only the subject's own coarse recollection
# (8/13 audited wrong ejections were the body reporter railroaded this
# way). Narrow window: see ``NARROW_ALIBI_WINDOW_TICKS``.
WEAK_REASON_SELF_STATED: Final[str] = "self-stated alibi"
WEAK_REASON_NARROW_WINDOW: Final[str] = "narrow alibi window"


def is_weak_contradiction(flag: ContradictionRef) -> bool:
    """Whether ``flag`` is a detector-flagged weak signal (Task 9.7).

    True iff the flag is an ``alibi_vs_sighting`` whose description
    carries the :data:`WEAK_CONTRADICTION_MARKER_PREFIX` audit marker the
    detector appended for a self-stated or narrow-window alibi. Belief
    Rule 2 (:func:`agents.memory.beliefs.apply_contradiction_rule`) keys
    its graduated down-weight on this predicate; keeping the predicate
    beside the marker writer means the two cannot drift. Re-derivable:
    re-running the pure detector on the same transcript re-produces the
    same marker, so the classification survives any record/replay
    round-trip without a schema field.
    """

    return (
        flag.kind == "alibi_vs_sighting"
        and WEAK_CONTRADICTION_MARKER_PREFIX in flag.description
    )


def detect_contradictions(
    transcript: MeetingTranscript,
    *,
    roster: frozenset[PlayerId] | None = None,
) -> tuple[ContradictionRef, ...]:
    """Flag incompatible alibi and saw-player claims (DESIGN.md §5.4, §6.4).

    Indexes every :class:`AlibiClaim` and :class:`SawPlayerObservation`
    that appears on any turn in the transcript and emits a
    :class:`ContradictionRef` per pair that cannot both be true:

    * ``alibi_conflict`` -- two alibis name the same ``subject`` in
      different rooms over overlapping tick ranges. Includes the case
      where a single speaker contradicts themselves and the case where
      two speakers disagree about a third party's location.
    * ``alibi_vs_sighting`` -- an alibi places ``subject`` in room R
      over a tick range, but another agent's ``saw_player(subject)``
      observation places them in a different room at a tick that falls
      inside the alibi range.

    Flags are *information*, not verdicts. The returned tuple is sorted
    by ``contradiction_id`` so the detector is deterministic across calls
    with the same transcript -- a precondition for the flags landing in a
    replay-stable rendered memory view (§6.6) and for the byte-identical
    replay invariant in DESIGN.md §0 rule 1. Sightings that match an
    alibi (same room, in-range tick) are silently ignored; the detector
    reports only what *cannot* both be true, not absence of evidence.

    Roster-aware subject filtering (audit J-J-9). When ``roster`` is
    supplied (the live-meeting path passes the set of living participant
    ids), only alibis and sightings whose ``subject`` is in the roster
    are indexed; a hallucinated ``"p-99"`` or an un-normalised
    self-placeholder is dropped *deterministically and explicitly here*
    rather than surviving into a half-matched flag. ``roster=None`` (the
    default) indexes every subject, preserving behaviour for
    callers/tests that exercise the detector without a roster.

    The function is pure: it does not mutate the transcript and has no
    side effects.
    """

    effective_roster = _NO_ROSTER if roster is None else roster
    alibis = tuple(
        indexed
        for indexed in _iter_alibis(transcript)
        if _subject_in_roster(indexed.claim.subject, effective_roster)
    )
    sightings = tuple(
        indexed
        for indexed in _iter_sightings(transcript)
        if _subject_in_roster(indexed.observation.subject, effective_roster)
    )

    flags: list[ContradictionRef] = []
    flags.extend(_detect_alibi_conflicts(alibis))
    flags.extend(_detect_alibi_vs_sightings(alibis=alibis, sightings=sightings))
    return tuple(sorted(flags, key=lambda flag: flag.contradiction_id))


def _subject_in_roster(subject: PlayerId, roster: frozenset[PlayerId]) -> bool:
    """Whether ``subject`` should be indexed given the effective roster.

    The :data:`_NO_ROSTER` sentinel means "no roster supplied": index
    every subject (legacy / unit-test behaviour). Any other roster --
    including an explicitly-empty one -- gates membership exactly.
    """

    if roster is _NO_ROSTER:
        return True
    return subject in roster


# -- Internal: indexing -----------------------------------------------------


@dataclass(frozen=True)
class _IndexedAlibi:
    """An :class:`AlibiClaim` paired with its event id and speaker.

    ``speaker`` is the player who *stated* the claim (``turn.speaker``),
    which the Task 9.7 weak-signal classification compares against the
    claim's ``subject`` to recognise a self-stated alibi.
    """

    event_id: str
    speaker: PlayerId
    claim: AlibiClaim


@dataclass(frozen=True)
class _IndexedSighting:
    """A :class:`SawPlayerObservation` paired with its event id and speaker."""

    event_id: str
    speaker: PlayerId
    observation: SawPlayerObservation


def _iter_alibis(transcript: MeetingTranscript) -> Iterator[_IndexedAlibi]:
    for turn in transcript.turns:
        for index, claim in enumerate(turn.claims):
            if isinstance(claim, AlibiClaim):
                yield _IndexedAlibi(
                    event_id=_turn_claim_id(turn=turn, index=index),
                    speaker=turn.speaker,
                    claim=claim,
                )


def _iter_sightings(transcript: MeetingTranscript) -> Iterator[_IndexedSighting]:
    for turn in transcript.turns:
        for index, observation in enumerate(turn.observations):
            if isinstance(observation, SawPlayerObservation):
                yield _IndexedSighting(
                    event_id=_turn_observation_id(turn=turn, index=index),
                    speaker=turn.speaker,
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
        weak_reasons = _weak_signal_reasons(alibi)
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
                    alibi=alibi.claim,
                    sighting=sighting.observation,
                    weak_reasons=weak_reasons,
                ),
            )


def _weak_signal_reasons(alibi: _IndexedAlibi) -> tuple[str, ...]:
    """The Task 9.7 false-positive patterns ``alibi`` matches, if any.

    Both patterns are properties of the alibi side alone, so the
    classification is computed once per alibi regardless of how many
    sightings it is paired with. Order is fixed (self-stated, then
    narrow window) so the rendered marker is byte-stable across runs.
    """

    reasons: list[str] = []
    if alibi.speaker == alibi.claim.subject:
        reasons.append(WEAK_REASON_SELF_STATED)
    if alibi.claim.to_tick - alibi.claim.from_tick < NARROW_ALIBI_WINDOW_TICKS:
        reasons.append(WEAK_REASON_NARROW_WINDOW)
    return tuple(reasons)


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
    *,
    alibi: AlibiClaim,
    sighting: SawPlayerObservation,
    weak_reasons: tuple[str, ...] = (),
) -> str:
    base = (
        f"Alibi places {alibi.subject} in {alibi.room} "
        f"(ticks {alibi.from_tick}-{alibi.to_tick}); sighting reports "
        f"{sighting.subject} in {sighting.room} at tick {sighting.tick}."
    )
    if not weak_reasons:
        return base
    return f"{base} {WEAK_CONTRADICTION_MARKER_PREFIX}{'; '.join(weak_reasons)}]"


# -- Internal: event ids and predicates -------------------------------------


def _turn_claim_id(*, turn: MeetingTurn, index: int) -> str:
    return f"turn:{turn.turn_id}:claim:{index}"


def _turn_observation_id(*, turn: MeetingTurn, index: int) -> str:
    return f"turn:{turn.turn_id}:obs:{index}"


def _ranges_overlap(a_from: int, a_to: int, b_from: int, b_to: int) -> bool:
    # Inclusive overlap, matching :class:`AlibiClaim`'s "tick ranges
    # are inclusive" contract.
    return a_from <= b_to and b_from <= a_to


__all__ = [
    "NARROW_ALIBI_WINDOW_TICKS",
    "WEAK_CONTRADICTION_MARKER_PREFIX",
    "WEAK_REASON_NARROW_WINDOW",
    "WEAK_REASON_SELF_STATED",
    "ChainStep",
    "ChainTermination",
    "ChainWalk",
    "accusation_target",
    "detect_contradictions",
    "is_canonically_ordered",
    "is_weak_contradiction",
    "next_chain_step",
    "sort_turns_canonically",
    "walk_chain",
]
