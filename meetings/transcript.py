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

Task 10.1 (audit gp-2 C-C-1/C-C-2/C-C-3): rooms are canonicalised ONCE
at claim-parse (:func:`canonical_rooms` at indexing time), so every
comparison -- alibi vs alibi, alibi vs sighting, and the corroboration
path -- sees the same canonical room set. Compound labels the 9B freely
emits ("LABS/MEDBAY") split into their member rooms; placeholder labels
("VARIOUS") canonicalise to *no room* and mint no flag; a sighting whose
room sits inside the alibi's room set is CONSISTENT and surfaces through
:func:`detect_corroborations` instead of a contradiction. The 9.7 weak
classification now also covers ``alibi_conflict`` (self-pair /
adversarial / narrow / boundary-overlap reasons) and endpoint-tick-only
``alibi_vs_sighting`` mismatches; a defense-echo alibi (an exact
restatement of an earlier alibi about the same subject) dedupes to the
original claim before contradiction pairing (the corroboration path
instead pairs every stated version -- its per-pair independence gate
does the filtering). :func:`contradiction_lift_key` is the per-claim
dedup key belief Rule 2 caps its lift on.
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

# Reason literals joined (in fixed order, "; "-separated) inside the weak
# marker. Self-stated: the alibi's speaker is its own subject, so a third
# party's sighting contradicts only the subject's own coarse recollection
# (8/13 audited wrong ejections were the body reporter railroaded this
# way). Narrow window: see ``NARROW_ALIBI_WINDOW_TICKS``. The Task 10.1
# additions (audit gp-2): endpoint-tick -- the sighting sits exactly on
# the alibi window's edge tick (movement resolves one room per tick, so
# an edge-tick sighting elsewhere is transit fuzz; 31 such flags split
# crew/impostor evenly with no guilt signal); self-pair -- BOTH conflicting
# alibis are the subject's own claims (the subject's coarse recollection
# disagreeing with itself, the 9.7 self-stated rationale a fortiori);
# adversarial -- a non-subject speaker in an accuser/accused relation with
# the subject stated one side (accusation-chain adversaries manufacture
# counter-alibis; seed 13 m2's impostor weaponised exactly this);
# boundary overlap -- the two alibis overlap only on the junction tick
# where one ends and the other begins (a movement pair, not a lie).
WEAK_REASON_SELF_STATED: Final[str] = "self-stated alibi"
WEAK_REASON_NARROW_WINDOW: Final[str] = "narrow alibi window"
WEAK_REASON_ENDPOINT_TICK: Final[str] = "endpoint-tick sighting"
WEAK_REASON_SELF_PAIR: Final[str] = "self-stated alibi pair"
WEAK_REASON_ADVERSARIAL: Final[str] = "adversarial testimony"
WEAK_REASON_BOUNDARY_OVERLAP: Final[str] = "endpoint-tick overlap"

# Room labels that name no actual room (Task 10.1; audit gp-2 C-C-1).
# qwen3.5:9b emits these as alibi rooms when it cannot or will not commit
# to a location; under exact string comparison they mismatched every real
# room and minted 11 artifact flags on the audited set. They canonicalise
# to *no room*: a claim with no canonical room participates in no room
# comparison and therefore mints no flag (DESIGN.md §5.4 -- the detector
# reports what cannot both be true, and "somewhere" contradicts nothing).
# The set is the complete inventory observed across both committed replay
# sets; membership is case-insensitive via the :func:`canonical_rooms`
# upper-casing.
PLACEHOLDER_ROOM_LABELS: Final[frozenset[str]] = frozenset(
    {
        "VARIOUS",
        "VARIABLE",
        "VARYING",
        "UNKNOWN",
        "UNKNOWN_ROOM",
    }
)

# Compound-label separators observed in the committed sets ("LABS/MEDBAY",
# "WEST_HALL|LABS", "ENGINEERING-EAST_HALL_TRANSITION",
# "EAST_HALL_AND_ADMIN_TRANSITION"). "_AND_" is replaced before "-" so the
# word joiner never half-splits; "_" alone is NOT a separator (canonical
# room ids are UPPERCASE_SNAKE, e.g. EAST_HALL).
_COMPOUND_ROOM_JOINERS: Final[tuple[str, ...]] = ("_AND_", "|", "-")

# Trailing token the model appends to a room it names as transit
# ("ADMIN_TRANSITION" = "moving through ADMIN"); stripped so the member
# room matches its canonical id.
_ROOM_TRANSITION_SUFFIX: Final[str] = "_TRANSITION"


def canonical_rooms(room: str) -> frozenset[str]:
    """Canonical room-name set for one claim/sighting room label (Task 10.1).

    The single normalisation point for every room comparison the detector
    and the corroboration path make (audit gp-2 C-C-1: canonicalise ONCE
    at claim-parse, never per comparison site). Pure string transformation
    -- :mod:`meetings` is firewalled from the engine map, so membership in
    the canonical map is deliberately NOT checked here:

    * upper-case (the model emits ``"CAFEteria"`` / ``"cafeteria"``),
    * split compound labels on ``"/"``, ``"|"``, ``"-"``, and ``"_AND_"``
      (a compound label is a multi-room account of movement, so each
      member room is somewhere the subject claims to have been),
    * strip a trailing ``"_TRANSITION"`` token from each member,
    * drop :data:`PLACEHOLDER_ROOM_LABELS` members and empties.

    An all-placeholder label returns the empty set -- "no room" -- which
    every comparison site treats as *not comparable* (no flag, no
    corroboration). Two labels are CONSISTENT when their canonical sets
    intersect and contradictory only when both are non-empty and disjoint.
    """

    text = room.upper()
    for joiner in _COMPOUND_ROOM_JOINERS:
        text = text.replace(joiner, "/")
    members: set[str] = set()
    for raw_part in text.split("/"):
        part = raw_part.strip().strip("_")
        if part.endswith(_ROOM_TRANSITION_SUFFIX):
            part = part[: -len(_ROOM_TRANSITION_SUFFIX)].rstrip("_")
        if not part or part in PLACEHOLDER_ROOM_LABELS:
            continue
        members.add(part)
    return frozenset(members)


def is_weak_contradiction(flag: ContradictionRef) -> bool:
    """Whether ``flag`` is a detector-flagged weak signal (Tasks 9.7, 10.1).

    True iff the flag's description carries the
    :data:`WEAK_CONTRADICTION_MARKER_PREFIX` audit marker the detector
    appended -- for an ``alibi_vs_sighting``: a self-stated or
    narrow-window alibi (9.7) or an endpoint-tick sighting (10.1); for an
    ``alibi_conflict``: a self-pair, adversarial testimony, a narrow
    window, or a boundary-tick-only overlap (10.1 -- the conflict path
    previously never received the 9.7 classification, so self-pairs
    carried the full Rule-2 delta and drove 5 wrong ejections). Belief
    Rule 2 (:func:`agents.memory.beliefs.apply_contradiction_rule`) keys
    its graduated down-weight on this predicate; keeping the predicate
    beside the marker writer means the two cannot drift. Re-derivable:
    re-running the pure detector on the same transcript re-produces the
    same marker, so the classification survives any record/replay
    round-trip without a schema field.
    """

    return WEAK_CONTRADICTION_MARKER_PREFIX in flag.description


# The event-id segment that identifies an alibi-claim event
# (:func:`_turn_claim_id` writes ``turn:{turn_id}:claim:{index}``;
# sightings get ``:obs:``). Kept beside the id writers so the lift-key
# parser below can never drift from the id format.
_CLAIM_EVENT_SEGMENT: Final[str] = ":claim:"


def contradiction_lift_key(flag: ContradictionRef) -> str:
    """The per-claim dedup key for belief Rule 2's lift (Task 10.1).

    Audit gp-2 C-C-3: the detector emits one ``alibi_vs_sighting`` flag
    per (alibi, sighting) pair, so one alibi paired against N sightings
    is N flags -- and the vote-time lift summed per flag, letting one
    truthful compound alibi stack 19 weak deltas to suspicion 1.0 (seed 9
    m1). The repair caps the lift at one delta per (subject, alibi-claim)
    pair; this function supplies the alibi-claim half of that key: the
    flag's claim event id(s), i.e. ``event_a_id``/``event_b_id`` filtered
    to the ``:claim:`` segment :func:`_turn_claim_id` writes. For an
    ``alibi_vs_sighting`` that is the single alibi claim (every sighting
    paired against it shares the key); for an ``alibi_conflict`` it is
    the claim pair (each distinct pair of claims stays its own piece of
    evidence). A flag built outside the detector whose event ids carry no
    claim segment falls back to its full event-id pair -- one key per
    flag, the pre-10.1 behaviour.
    """

    claim_ids = [
        event_id
        for event_id in (flag.event_a_id, flag.event_b_id)
        if _CLAIM_EVENT_SEGMENT in event_id
    ]
    if claim_ids:
        return "|".join(claim_ids)
    return f"{flag.event_a_id}|{flag.event_b_id}"


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

    Task 10.1 (audit gp-2): rooms are compared as canonical sets
    (:func:`canonical_rooms`, computed once at indexing) -- a placeholder
    side mints no flag, intersecting sets are consistent, and a
    defense-echo alibi is deduped to the original claim before pairing.
    Endpoint-tick mismatches and the conflict false-positive shapes carry
    the weak marker instead of being excluded: an endpoint mismatch can
    still be a real signal under corroboration, so the recorded flag set
    stays the honest full set and belief Rule 2 applies the graduated
    delta (the 9.7 down-weight convention).

    The function is pure: it does not mutate the transcript and has no
    side effects.
    """

    effective_roster = _NO_ROSTER if roster is None else roster
    alibis = _dedupe_echo_alibis(
        tuple(
            indexed
            for indexed in _iter_alibis(transcript)
            if _subject_in_roster(indexed.claim.subject, effective_roster)
        )
    )
    sightings = tuple(
        indexed
        for indexed in _iter_sightings(transcript)
        if _subject_in_roster(indexed.observation.subject, effective_roster)
    )

    flags: list[ContradictionRef] = []
    flags.extend(
        _detect_alibi_conflicts(alibis, accusation_pairs=_accusation_pairs(transcript))
    )
    flags.extend(_detect_alibi_vs_sightings(alibis=alibis, sightings=sightings))
    return tuple(sorted(flags, key=lambda flag: flag.contradiction_id))


@dataclass(frozen=True)
class DetectedCorroboration:
    """A containment-consistent (alibi, sighting) pair (Task 10.1).

    Audit gp-2 C-C-1: a third-party sighting whose room sits inside the
    subject's stated alibi rooms, at a tick inside the alibi window, is
    *corroboration-class* evidence -- the old detector string-compared
    the rooms and flagged exactly these confirmations as contradictions
    (34 of 83 flags on the audited set). ``subject`` is the corroborated
    player; the event ids reference the contributing turn artifacts the
    same way :class:`~meetings.schemas.ContradictionRef` does. Consumed
    by :func:`meetings.manager.extract_belief_evidence`, which folds the
    subject into the meeting's ``corroborated`` set -- the §6.3 Rule-3
    channel, so the magnitude is exactly the Rule-3 delta and the fold's
    per-meeting subject dedup caps it once per subject.
    """

    subject: PlayerId
    alibi_event_id: str
    sighting_event_id: str


def detect_corroborations(
    transcript: MeetingTranscript,
    *,
    roster: frozenset[PlayerId] | None = None,
) -> tuple[DetectedCorroboration, ...]:
    """Containment-consistent (alibi, sighting) pairs (Task 10.1; §6.3 Rule 3).

    The corroboration-path twin of :func:`detect_contradictions`: the
    same roster filter and the same :func:`canonical_rooms` parse (one
    canonicalisation, every consumer), but it pairs an alibi with the
    sightings that CONFIRM it: the sighting's canonical rooms intersect
    the alibi's and the sighting tick falls inside the alibi window.
    Pure and deterministic; the result is sorted by
    ``(subject, alibi_event_id, sighting_event_id)``.

    Independence gate: the sighting speaker must differ from BOTH the
    alibi's subject (you cannot vouch for yourself) and the alibi's
    speaker (one witness restating their own account in two formats is
    not a second voice). No-room sides (placeholders) corroborate
    nothing, mirroring the contradiction side.

    Unlike the contradiction path, echo alibis are NOT deduped here.
    The echo dedup exists to stop flag multiplication and classification
    flips on the contradiction side; corroboration needs every stated
    version of an account, because the independence gate is per
    (claim-speaker, sighting-speaker) pair -- when a witness vouches an
    alibi for the subject FIRST (alongside their own matching sighting)
    and the subject restates it later, the subject's echo is exactly the
    self-stated account that witness's sighting independently confirms;
    deduping it to the witness's claim would orphan the sighting on the
    same-speaker gate and silently drop a genuine Rule-3 signal. No
    inflation is possible: the belief fold reduces these pairs to a
    per-meeting subject set, so a subject is corroborated once however
    many stated versions and sightings agree.
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

    corroborations: list[DetectedCorroboration] = []
    for alibi in alibis:
        if not alibi.rooms:
            continue
        for sighting in sightings:
            if sighting.observation.subject != alibi.claim.subject:
                continue
            if sighting.speaker == alibi.claim.subject:
                continue
            if sighting.speaker == alibi.speaker:
                continue
            if not sighting.rooms or not (sighting.rooms & alibi.rooms):
                continue
            if not (
                alibi.claim.from_tick
                <= sighting.observation.tick
                <= alibi.claim.to_tick
            ):
                continue
            corroborations.append(
                DetectedCorroboration(
                    subject=alibi.claim.subject,
                    alibi_event_id=alibi.event_id,
                    sighting_event_id=sighting.event_id,
                )
            )
    return tuple(
        sorted(
            corroborations,
            key=lambda c: (c.subject, c.alibi_event_id, c.sighting_event_id),
        )
    )


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
    """An :class:`AlibiClaim` paired with its event id, speaker, and rooms.

    ``speaker`` is the player who *stated* the claim (``turn.speaker``),
    which the Task 9.7 weak-signal classification compares against the
    claim's ``subject`` to recognise a self-stated alibi. ``rooms`` is
    the claim's canonical room set (:func:`canonical_rooms`), computed
    once at indexing so every comparison site -- conflicts, sightings,
    corroborations -- reads the same canonical parse (Task 10.1).
    """

    event_id: str
    speaker: PlayerId
    claim: AlibiClaim
    rooms: frozenset[str]


@dataclass(frozen=True)
class _IndexedSighting:
    """A :class:`SawPlayerObservation` with its event id, speaker, and rooms.

    ``rooms`` is the canonical parse of the sighting's room label
    (:func:`canonical_rooms`) -- the model occasionally emits compound or
    case-variant sighting rooms too, so both sides of every comparison
    canonicalise identically (Task 10.1).
    """

    event_id: str
    speaker: PlayerId
    observation: SawPlayerObservation
    rooms: frozenset[str]


def _iter_alibis(transcript: MeetingTranscript) -> Iterator[_IndexedAlibi]:
    for turn in transcript.turns:
        for index, claim in enumerate(turn.claims):
            if isinstance(claim, AlibiClaim):
                yield _IndexedAlibi(
                    event_id=_turn_claim_id(turn=turn, index=index),
                    speaker=turn.speaker,
                    claim=claim,
                    rooms=canonical_rooms(claim.room),
                )


def _iter_sightings(transcript: MeetingTranscript) -> Iterator[_IndexedSighting]:
    for turn in transcript.turns:
        for index, observation in enumerate(turn.observations):
            if isinstance(observation, SawPlayerObservation):
                yield _IndexedSighting(
                    event_id=_turn_observation_id(turn=turn, index=index),
                    speaker=turn.speaker,
                    observation=observation,
                    rooms=canonical_rooms(observation.room),
                )


def _dedupe_echo_alibis(
    alibis: tuple[_IndexedAlibi, ...],
) -> tuple[_IndexedAlibi, ...]:
    """Drop alibi restatements, keeping each account's FIRST statement.

    Task 10.1 (audit gp-2 C-C-2, the defense-echo shape): a speaker
    restating an alibi already on the record -- a defender repeating the
    accused's own self-alibi (seed 26 m1: p-2's echo of p-6 minted 4
    strong flags against the player being defended), or the subject
    re-asserting their alibi after an accusation -- adds no new location
    account. An echo is an alibi whose (subject, canonical rooms, tick
    range) exactly matches an earlier claim in transcript order; it is
    deduped to that original BEFORE pairing, so it mints no flag of its
    own and the original's speaker keeps deciding the weak/strong
    classification. A restatement that changes the rooms or the window
    asserts new information and is NOT an echo. Deterministic: turns are
    walked in transcript order, so "first" is the chain's own order.

    Contradiction-side only: :func:`detect_corroborations` deliberately
    pairs against every stated version of an account, because its
    independence gate is per claim-speaker -- see its docstring for the
    witness-vouches-first shape the dedup would otherwise silently drop.
    """

    seen: set[tuple[PlayerId, frozenset[str], int, int]] = set()
    deduped: list[_IndexedAlibi] = []
    for alibi in alibis:
        key = (
            alibi.claim.subject,
            alibi.rooms,
            alibi.claim.from_tick,
            alibi.claim.to_tick,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(alibi)
    return tuple(deduped)


def _accusation_pairs(
    transcript: MeetingTranscript,
) -> frozenset[tuple[PlayerId, PlayerId]]:
    """Every recorded ``(accuser, accused)`` pair in the transcript.

    Feeds the Task 10.1 adversarial classification: an alibi about
    subject S stated by a speaker who accused S -- or whom S accused --
    is testimony from across the accusation chain, capped at weak
    (audit gp-2 C-C-2: an accused impostor's counter-alibi about their
    accuser put a strong flag on the accuser in seeds 13/17).
    """

    return frozenset(
        (turn.speaker, claim.against)
        for turn in transcript.turns
        for claim in turn.claims
        if isinstance(claim, AccusationClaim)
    )


# -- Internal: detectors ----------------------------------------------------


def _detect_alibi_conflicts(
    alibis: tuple[_IndexedAlibi, ...],
    *,
    accusation_pairs: frozenset[tuple[PlayerId, PlayerId]],
) -> Iterator[ContradictionRef]:
    for i, left in enumerate(alibis):
        for right in alibis[i + 1 :]:
            if left.claim.subject != right.claim.subject:
                continue
            # Canonical room comparison (Task 10.1): a no-room side
            # (placeholder label) is not comparable and mints no flag;
            # intersecting sets are a CONSISTENT multi-room account, not
            # a conflict -- only two non-empty, disjoint sets cannot both
            # be true.
            if not left.rooms or not right.rooms:
                continue
            if left.rooms & right.rooms:
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
                description=_describe_alibi_conflict(
                    left.claim,
                    right.claim,
                    weak_reasons=_conflict_weak_reasons(
                        left, right, accusation_pairs=accusation_pairs
                    ),
                ),
            )


def _detect_alibi_vs_sightings(
    *,
    alibis: tuple[_IndexedAlibi, ...],
    sightings: tuple[_IndexedSighting, ...],
) -> Iterator[ContradictionRef]:
    for alibi in alibis:
        if not alibi.rooms:
            continue
        base_reasons = _weak_signal_reasons(alibi)
        for sighting in sightings:
            if sighting.observation.subject != alibi.claim.subject:
                continue
            # Canonical room comparison (Task 10.1): a no-room sighting
            # is not comparable; a sighting room inside the alibi's room
            # set is CONSISTENT (corroboration-class evidence surfaced by
            # :func:`detect_corroborations`, never a flag).
            if not sighting.rooms or (sighting.rooms & alibi.rooms):
                continue
            if not (
                alibi.claim.from_tick
                <= sighting.observation.tick
                <= alibi.claim.to_tick
            ):
                continue
            weak_reasons = base_reasons
            # Endpoint-tick weak band (Task 10.1, audit gp-2 C-C-1): a
            # sighting exactly on the window's edge tick is movement fuzz
            # -- weak-banded rather than excluded, because an endpoint
            # mismatch can still be a real signal once corroborated.
            if sighting.observation.tick in (
                alibi.claim.from_tick,
                alibi.claim.to_tick,
            ):
                weak_reasons = (*base_reasons, WEAK_REASON_ENDPOINT_TICK)
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
    The Task 10.1 conflict classification reuses this helper per side,
    so the two paths share one definition of self-stated / narrow.
    """

    reasons: list[str] = []
    if alibi.speaker == alibi.claim.subject:
        reasons.append(WEAK_REASON_SELF_STATED)
    if alibi.claim.to_tick - alibi.claim.from_tick < NARROW_ALIBI_WINDOW_TICKS:
        reasons.append(WEAK_REASON_NARROW_WINDOW)
    return tuple(reasons)


def _conflict_weak_reasons(
    left: _IndexedAlibi,
    right: _IndexedAlibi,
    *,
    accusation_pairs: frozenset[tuple[PlayerId, PlayerId]],
) -> tuple[str, ...]:
    """The Task 10.1 weak patterns an alibi-conflict pair matches, if any.

    The conflict-path counterpart of :func:`_weak_signal_reasons` -- the
    9.7 classification the audit found the conflict path never received
    (gp-2 C-C-2), built from the same per-side helper rather than a
    parallel implementation. Order is fixed (self-pair, narrow window,
    adversarial, boundary overlap) so the marker is byte-stable:

    * self-pair -- BOTH claims are the subject's own statements (the
      9.7 self-stated rationale a fortiori: the subject's coarse
      recollection disagreeing with itself; seeds 11 m2 / 17 m0).
    * narrow window -- either claim spans fewer than
      :data:`NARROW_ALIBI_WINDOW_TICKS` ticks (a 1-2 tick claim is one
      transit observation; a conflict built on it inherits the fuzz).
    * adversarial -- a non-subject speaker on either side sits across the
      accusation chain from the subject (they accused the subject, or
      the subject accused them): capped at weak so an accused player's
      counter-alibi cannot mint a strong flag on their accuser (the
      seed 13 m2 impostor deflection).
    * boundary overlap -- the windows overlap ONLY on the junction tick
      where one claim ends and the other begins: a movement pair
      ("CAFETERIA t0-6" + "STORAGE t6-9"), not two incompatible accounts.
    """

    subject = left.claim.subject
    left_reasons = _weak_signal_reasons(left)
    right_reasons = _weak_signal_reasons(right)

    reasons: list[str] = []
    if (
        WEAK_REASON_SELF_STATED in left_reasons
        and WEAK_REASON_SELF_STATED in right_reasons
    ):
        reasons.append(WEAK_REASON_SELF_PAIR)
    if (
        WEAK_REASON_NARROW_WINDOW in left_reasons
        or WEAK_REASON_NARROW_WINDOW in right_reasons
    ):
        reasons.append(WEAK_REASON_NARROW_WINDOW)
    if any(
        speaker != subject
        and (
            (speaker, subject) in accusation_pairs
            or (subject, speaker) in accusation_pairs
        )
        for speaker in (left.speaker, right.speaker)
    ):
        reasons.append(WEAK_REASON_ADVERSARIAL)
    if (
        left.claim.to_tick == right.claim.from_tick
        or right.claim.to_tick == left.claim.from_tick
    ):
        reasons.append(WEAK_REASON_BOUNDARY_OVERLAP)
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


def _describe_alibi_conflict(
    left: AlibiClaim,
    right: AlibiClaim,
    *,
    weak_reasons: tuple[str, ...] = (),
) -> str:
    # Order the two alibis lexically by room so the description is
    # stable regardless of iteration order. The contradiction_id is
    # already canonicalised; doing the same for free text keeps the
    # rendered memory view byte-stable across replays.
    first, second = sorted((left, right), key=lambda claim: claim.room)
    base = (
        f"Alibis place {first.subject} in {first.room} "
        f"(ticks {first.from_tick}-{first.to_tick}) and in {second.room} "
        f"(ticks {second.from_tick}-{second.to_tick}); intervals overlap."
    )
    if not weak_reasons:
        return base
    return f"{base} {WEAK_CONTRADICTION_MARKER_PREFIX}{'; '.join(weak_reasons)}]"


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
    "PLACEHOLDER_ROOM_LABELS",
    "WEAK_CONTRADICTION_MARKER_PREFIX",
    "WEAK_REASON_ADVERSARIAL",
    "WEAK_REASON_BOUNDARY_OVERLAP",
    "WEAK_REASON_ENDPOINT_TICK",
    "WEAK_REASON_NARROW_WINDOW",
    "WEAK_REASON_SELF_PAIR",
    "WEAK_REASON_SELF_STATED",
    "ChainStep",
    "ChainTermination",
    "ChainWalk",
    "DetectedCorroboration",
    "accusation_target",
    "canonical_rooms",
    "contradiction_lift_key",
    "detect_contradictions",
    "detect_corroborations",
    "is_canonically_ordered",
    "is_weak_contradiction",
    "next_chain_step",
    "sort_turns_canonically",
    "walk_chain",
]
