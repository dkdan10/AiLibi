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
emits ("LABS/MEDBAY") split into their member rooms; a sighting whose
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

Task 10.6 (audit gp-1 C-C-5/C-C-4, C-C-3): non-map labels canonicalise
against the frozen :data:`CANONICAL_ROOMS` ALLOWLIST instead of a
placeholder denylist (the denylist leaked its own variants --
``VARYING_ROOMS`` minted 25% of the Wave-0 set's flag volume against one
innocent); a proxy alibi (speaker != subject) whose conflicting sighting
the SUBJECT'S OWN account agrees with is suppressed and re-targeted as a
WEAK flag at the proxy speaker (:data:`WEAK_REASON_RETARGETED_PROXY`);
and Rule-3 corroboration is relevance-gated through the named pure
predicate :func:`is_relevant_sighting` (no spawn-window vouches, no
kill-scene vouches), which Task 10.7 reuses for accusation-side
observation backing.

Task 10.7 (audit gp-2 C-C-1/C-C-2): :func:`independent_voices` derives
the INDEPENDENT VOICES against each accused subject -- the
observation-backed, relevance-gated testimony count the pre-vote
two-witness fold (belief side: :mod:`agents.memory.beliefs`) gates on.
A bare verbal accusation carries no voice, and an opt-in turn
contributes a voice only through a corroboration aligned with an
existing accuser, which is what keeps the seed-30 three-accuser
pile-on powerless (witness COUNT cannot filter pile-ons; independence
can).
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass
from typing import Final, Literal

from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
)

_ContradictionKind = Literal["alibi_conflict", "alibi_vs_sighting"]

# Why a meeting opened (DESIGN.md §5.1). The orchestrator derives this from the
# engine's MeetingTriggeredEvent (Task 10.8). Threaded into the Rule-3 relevance
# gate (Task 10.11; audit-2026-06-13-1816 B-B-1) so an EMERGENCY meeting -- which
# by design has NO kill scene -- never trusts a (fabricated) opening `found_body`
# to widen its exclusion zone. ``None`` preserves the pre-10.11 behaviour (read
# the opening body off the transcript) for callers/tests that do not carry the
# kind.
MeetingTriggerKind = Literal["report", "emergency"]

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

# Task 10.6 (audit gp-1 C-C-4, option (b) by owner decision): a proxy
# alibi (speaker != subject) whose conflicting sighting the subject's OWN
# account agrees with is not evidence against the subject -- it is the
# proxy speaker's claim that is the odd account out. The flag against the
# subject is suppressed and a re-targeted flag is minted against the
# proxy speaker, capped at weak via this reason so a re-target can never
# eject alone (the Wave-0 strong band was 3/3 proxy-shaped at 1 TP /
# 2 FP; the surviving TP -- seed 24, where the subject ECHOED the false
# alibi -- does not match the suppression condition and keeps its full
# strong flag).
WEAK_REASON_RETARGETED_PROXY: Final[str] = "re-targeted proxy alibi"

# Task 10.10 (audit-2026-06-13-1816 C-C-2, C-C-3): a contradiction whose
# BOTH events resolve to turns by ONE speaker, where that speaker is NOT
# the flag's subject, is a single unreliable narrator's two proxy-claims
# about a THIRD party conflicting with each other -- not evidence against
# the subject. On the close baseline one such case (seed-40: p-5's two
# p-4-alibis minting an alibi_conflict, plus p-5's alibi-for-p-4 vs p-5's
# own sighting of p-4 minting an alibi_vs_sighting) stacked two weak
# deltas on different lift-keys (0.5 + 0.08 + 0.08 = 0.66), crossed the
# gate, and the 10.9.2 redirect launder ejected the innocent p-4. The
# guard re-targets the flag WEAK at the speaker (whose unreliability is
# the real signal) so it can never eject the subject alone. It is
# distinct from :data:`WEAK_REASON_RETARGETED_PROXY` (Task 10.6), the
# CROSS-speaker case where a third party's sighting contradicts a proxy
# alibi the SUBJECT'S OWN account agrees with -- that rule keys on the
# subject's account, this one on a single speaker authoring both events.
# The single-speaker condition is exactly what spares the legitimate
# cross-speaker deception frame (seed-12: impostor p-1's alibi vs the
# reporter's sighting -- two speakers, so this guard never fires and the
# strong flag survives as a 10.13 probe input).
WEAK_REASON_PROXY_INTRA_TURN: Final[str] = "same-speaker proxy contradiction"

# The map's canonical room ids -- a frozen ALLOWLIST (Task 10.6; audit
# gp-1 C-C-5). The 10.1 placeholder DENYLIST ("VARIOUS", "UNKNOWN", ...)
# was blind to its own variants: ``VARYING_ROOMS`` (seed 13 m1) escaped
# it, canonicalised to a phantom room, and minted 22 of the Wave-0 set's
# 87 flags -- 25% of total volume, all against one innocent -- and the
# ``HALLS`` collective (seed 6 m1) was the same latent class. Under the
# allowlist a label whose canonical form is not a real map room is
# NON-SPATIAL: it participates in no room comparison, so it mints no
# flag and no corroboration ("somewhere" contradicts nothing and
# confirms nothing).
#
# This is DATA, not an engine import: :mod:`meetings` stays
# engine-free (``agents`` imports this module, and agents/ must not
# transitively reach engine/ -- the §1.3 observation firewall, enforced
# by import-linter). The duplication is pinned by a test asserting this
# set equals ``engine.world.load_canonical_map().rooms`` exactly, so a
# future map change fails loud here and re-triggers detector review
# instead of silently re-opening the placeholder class.
CANONICAL_ROOMS: Final[frozenset[str]] = frozenset(
    {
        "CAFETERIA",
        "UPPER_HALL",
        "ADMIN",
        "EAST_HALL",
        "ENGINEERING",
        "REACTOR",
        "STORAGE",
        "WEST_HALL",
        "MEDBAY",
        "LABS",
    }
)

# §6.3 Rule-3 relevance gate (Task 10.6; audit C-C-3). Ticks 0..1 are the
# spawn window: every player co-spawns in CAFETERIA, so a sighting there
# confirms nothing about anyone (spawn-window sightings let wide alibis
# self-corroborate -- 52% of Wave-0 impostor accusation flow cancelled
# in-meeting on this class of vouch). A sighting is outside the window
# from tick 2 onward.
SPAWN_WINDOW_LAST_TICK: Final[int] = 1

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
    """Canonical room-name set for one claim/sighting room label (Tasks 10.1, 10.6).

    The single normalisation point for every room comparison the detector
    and the corroboration path make (audit gp-2 C-C-1: canonicalise ONCE
    at claim-parse, never per comparison site). Pure string transformation
    over the frozen :data:`CANONICAL_ROOMS` data constant:

    * upper-case (the model emits ``"CAFEteria"`` / ``"cafeteria"``),
    * split compound labels on ``"/"``, ``"|"``, ``"-"``, and ``"_AND_"``
      (a compound label is a multi-room account of movement, so each
      member room is somewhere the subject claims to have been),
    * strip a trailing ``"_TRANSITION"`` token from each member,
    * keep ONLY members of the :data:`CANONICAL_ROOMS` allowlist (Task
      10.6, replacing the 10.1 placeholder denylist -- see the constant
      for the ``VARYING_ROOMS`` leak that motivated the flip).

    A label with no canonical member returns the empty set -- "no room",
    non-spatial -- which every comparison site treats as *not comparable*
    (no flag, no corroboration). Two labels are CONSISTENT when their
    canonical sets intersect and contradictory only when both are
    non-empty and disjoint.
    """

    text = room.upper()
    for joiner in _COMPOUND_ROOM_JOINERS:
        text = text.replace(joiner, "/")
    members: set[str] = set()
    for raw_part in text.split("/"):
        part = raw_part.strip().strip("_")
        if part.endswith(_ROOM_TRANSITION_SUFFIX):
            part = part[: -len(_ROOM_TRANSITION_SUFFIX)].rstrip("_")
        if part in CANONICAL_ROOMS:
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

# Task 10.10: the constant lift key shared by every proxy-intra-turn
# re-target. A re-targeted flag's sole subject is the speaker, so belief
# Rule 2's ``(subject, lift_key)`` dedup folds ALL of one speaker's
# same-turn proxy artifacts (the seed-40 shape: an ``alibi_conflict`` and
# an ``alibi_vs_sighting`` sharing the pivot claim, on distinct event-id
# pairs) into ONE weak delta -- so a single narrator's contradictory turn
# can never cross the §4.6 gate by itself (audit C-C-2: "one bad claim
# cannot mint two stacking deltas"). Distinct from a real event-id pair
# so it can never collide with a non-retarget key.
_PROXY_INTRA_TURN_LIFT_KEY: Final[str] = "proxy-intra-turn"


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

    Task 10.10: a proxy-intra-turn re-target keys on the constant
    :data:`_PROXY_INTRA_TURN_LIFT_KEY` instead, so the seed-40 stack
    (two same-speaker flags on distinct claim pairs) folds to ONE weak
    delta on the speaker rather than 0.08 + 0.08 crossing the gate
    (audit C-C-2). The re-target's sole subject is the speaker, so the
    ``(subject, key)`` dedup collapses these per speaker; every other
    flag class is unaffected.
    """

    if WEAK_REASON_PROXY_INTRA_TURN in flag.description:
        return _PROXY_INTRA_TURN_LIFT_KEY
    claim_ids = [
        event_id
        for event_id in (flag.event_a_id, flag.event_b_id)
        if _CLAIM_EVENT_SEGMENT in event_id
    ]
    if claim_ids:
        return "|".join(claim_ids)
    return f"{flag.event_a_id}|{flag.event_b_id}"


def is_relevant_sighting(
    *,
    tick: int,
    rooms: frozenset[str],
    triggering_body_rooms: frozenset[str],
) -> bool:
    """The §6.3 Rule-3 relevance predicate (Task 10.6; audit gp-2 C-C-3).

    A supporting sighting is corroboration-grade ONLY when it carries
    actual evidential weight about the subject's innocence. Two
    evidentially-empty shapes are excluded -- on the Wave-0 set they let
    52% of impostor accusation flow cancel in-meeting (30 of 58
    accused-impostor events netted to zero):

    * **Spawn-window sightings** (``tick <=``
      :data:`SPAWN_WINDOW_LAST_TICK`): everyone co-spawns in CAFETERIA,
      so a tick-0/1 sighting confirms a wide alibi for anyone. Relevant
      sightings start at tick 2.
    * **Kill-scene sightings**: a sighting whose ``rooms`` intersect the
      meeting's ``triggering_body_rooms`` places the subject AT the kill
      scene inside their corroborated alibi window -- presence at the
      scene must never exonerate (the seed-6 m1 byte walk: the accuser's
      own ADMIN@16 sighting of the impostor who had just killed there
      corroborated the killer's alibi and cancelled the accusation).

    Pure and total: ``rooms`` may be empty (a claim-stated corroboration
    carries no room -- only the spawn-window prong can gate it), and an
    empty ``triggering_body_rooms`` (an emergency meeting with no body)
    never excludes by scene. Callers pass canonical room sets
    (:func:`canonical_rooms`) on both sides; the corroboration path
    guarantees the sighting already sits inside the corroborated alibi
    window. Task 10.7 reuses this predicate verbatim for accusation-side
    observation backing (one home).
    """

    if tick <= SPAWN_WINDOW_LAST_TICK:
        return False
    if rooms & triggering_body_rooms:
        return False
    return True


def triggering_body_rooms(
    transcript: MeetingTranscript,
    *,
    trigger_kind: MeetingTriggerKind | None = None,
) -> frozenset[str]:
    """Canonical rooms of the meeting's triggering body (Task 10.6, 10.11).

    The kill-scene input to :func:`is_relevant_sighting`: the canonical
    room set of every ``found_body`` observation on the OPENING turn
    (turn 0 IS the body report -- DESIGN.md §5.2 PHASE 1), re-derivable
    from the recorded transcript alone so replay-side consumers see the
    identical scene set. An emergency meeting (no body on the opening) or
    an empty transcript yields the empty set, which the predicate treats
    as "no kill scene". Later-turn ``found_body`` echoes are deliberately
    ignored: the TRIGGERING body is the opening reporter's, and an echo
    of it adds nothing while a hallucinated late "body" must not widen
    the exclusion zone.

    Task 10.11 (audit-2026-06-13-1816 B-B-1) -- the emergency gate, the
    defense-in-depth half of the no-fabricated-body fix. An EMERGENCY
    meeting has NO kill scene by design (§5.2 PHASE 1: the opener pressed
    the button on suspicion, no body was reported), so ``trigger_kind ==
    "emergency"`` returns ``frozenset()`` UNCONDITIONALLY -- even when the
    opening turn carries a (model-fabricated) ``found_body``. This is the
    half the engine owns: the v7 prompt stops the fabrication at the
    source, but the relevance gate must never trust an emergency opening's
    body to widen the §6.3 Rule-3 exclusion zone. ``trigger_kind`` left as
    ``None`` (or ``"report"``) keeps the pre-10.11 behaviour: read the
    opening body off the transcript.
    """

    if trigger_kind == "emergency":
        return frozenset()
    turns = transcript.turns
    if not turns:
        return frozenset()
    rooms: set[str] = set()
    for observation in turns[0].observations:
        if isinstance(observation, FoundBodyObservation):
            rooms |= canonical_rooms(observation.room)
    return frozenset(rooms)


# ---------------------------------------------------------------------------
# Position reconstruction from stated sightings (Task 13.2, DESIGN.md §5.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StatedPlacement:
    """One publicly stated placement of a player at a tick (Task 13.2).

    A single ``saw_player`` observation in the transcript places its
    ``subject`` -- and every player it lists as ``co_present`` -- in the
    sighting's room(s) at the sighting tick. Each such placement is one
    :class:`StatedPlacement`:

    * ``tick`` -- the sighting tick.
    * ``rooms`` -- the sighting's canonical room set
      (:func:`canonical_rooms`, computed once at indexing so every
      consumer reads the same parse, Task 10.1). Always non-empty: a
      non-spatial label locates nobody and mints no placement.
    * ``speaker`` -- the player who *stated* the sighting
      (``turn.speaker``), kept so a consumer can tell a self-stated
      placement (``speaker`` is the placed player) from an independent one
      without re-walking the transcript -- the distinction the 13.4
      two-source conjunction needs.
    * ``event_id`` -- the contributing ``saw_player`` observation's id
      (``turn:{turn_id}:obs:{index}``, the same id
      :class:`~meetings.schemas.ContradictionRef` references), so every
      reconstructed placement traces back to exactly one public transcript
      observation (the 13.4 firewall assertion).

    Frozen and hashable (``rooms`` is a frozenset), so placements dedupe
    within an observation and sort deterministically.
    """

    tick: int
    rooms: frozenset[str]
    speaker: PlayerId
    event_id: str


def _placement_sort_key(
    placement: StatedPlacement,
) -> tuple[int, tuple[str, ...], PlayerId, str]:
    """Total-order key for a subject's placements (replay-deterministic).

    Sorts by tick, then the sorted room tuple, then the stating speaker,
    then the unique observation id -- a total order (``event_id`` is unique
    per observation), so a subject's reconstructed path is byte-identical
    across runs regardless of transcript iteration or set order.
    """

    return (
        placement.tick,
        tuple(sorted(placement.rooms)),
        placement.speaker,
        placement.event_id,
    )


def reconstruct_stated_paths(
    transcript: MeetingTranscript,
    *,
    roster: frozenset[PlayerId] | None = None,
    trigger_kind: MeetingTriggerKind | None = None,
) -> Mapping[PlayerId, tuple[StatedPlacement, ...]]:
    """Each subject's STATED room-by-tick path from the transcript (Task 13.2).

    The pure, replay-deterministic promotion of
    ``experiments/lab/inference_feasibility_probe.py::reconstruct`` from
    engine truth onto the PUBLIC meeting transcript: where the probe
    rebuilt every player's room-by-tick path from the recorded ENGINE
    actions, this rebuilds it from what speakers publicly *stated* they
    saw -- the transcript's ``saw_player`` observations ONLY. It never
    reads engine ``WorldState``, perception, or any ``observation`` packet
    (DESIGN.md §1.3 firewall: :mod:`meetings` stays engine-free), so it is
    the substrate the new STRONG inferential rules (Tasks 13.3 / 13.4)
    consume to find a stated alibi that the stated sightings make
    impossible.

    For every ``saw_player`` observation on any turn, the ``subject`` and
    each ``co_present`` player are placed in the sighting's canonical
    rooms at its tick (a co-presence is as much a stated placement as the
    subject's, traceable to the same observation). A sighting contributes
    a placement only when it *counts*:

    * its room label is spatial (:func:`canonical_rooms` non-empty), and
    * it passes the §6.3 relevance gate :func:`is_relevant_sighting`
      against this meeting's :func:`triggering_body_rooms` -- the same
      one-home gate the corroboration path uses, so a spawn-window
      (tick 0-1) or kill-scene sighting -- the evidentially-empty shapes --
      reconstructs no position. ``trigger_kind="emergency"`` drops the
      kill-scene exclusion (an emergency meeting has no body, Task 10.11).

    The ``roster`` filter mirrors :func:`detect_contradictions`:
    ``roster=None`` (the default) places every named player (unit-test
    behaviour); an explicit roster -- the live path passes the living
    participants -- drops a hallucinated id, whether it appears as a
    sighting's ``subject`` or in its ``co_present`` list.

    Returns ``{subject: placements}`` for every player with at least one
    relevant stated placement, the subjects sorted and each subject's
    placements sorted by :func:`_placement_sort_key`. Pure: the transcript
    is not mutated and the function has no side effects, so re-running it
    on the same transcript yields byte-identical paths -- the
    DESIGN.md §0 rule 1 replay invariant the downstream flags inherit.
    """

    effective_roster = _NO_ROSTER if roster is None else roster
    body_rooms = triggering_body_rooms(transcript, trigger_kind=trigger_kind)

    paths: dict[PlayerId, list[StatedPlacement]] = {}
    for sighting in _iter_sightings(transcript):
        # A non-spatial label locates nobody (Task 10.1), and the §6.3
        # relevance gate drops the evidentially-empty spawn-window /
        # kill-scene sightings -- reused verbatim so the reconstruction
        # counts exactly the sightings the detectors trust.
        if not sighting.rooms:
            continue
        if not is_relevant_sighting(
            tick=sighting.observation.tick,
            rooms=sighting.rooms,
            triggering_body_rooms=body_rooms,
        ):
            continue
        placement = StatedPlacement(
            tick=sighting.observation.tick,
            rooms=sighting.rooms,
            speaker=sighting.speaker,
            event_id=sighting.event_id,
        )
        # The subject and every co-present player are placed by this one
        # observation; the set literal collapses a player who is their own
        # co-presence so each observation places a player at most once.
        placed_players = {
            sighting.observation.subject,
            *sighting.observation.co_present,
        }
        for player in placed_players:
            if not _subject_in_roster(player, effective_roster):
                continue
            paths.setdefault(player, []).append(placement)

    return {
        subject: tuple(sorted(placements, key=_placement_sort_key))
        for subject, placements in sorted(paths.items())
    }


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
    (:func:`canonical_rooms`, computed once at indexing) -- a non-spatial
    side mints no flag, intersecting sets are consistent, and a
    defense-echo alibi is deduped to the original claim before pairing.
    Endpoint-tick mismatches and the conflict false-positive shapes carry
    the weak marker instead of being excluded: an endpoint mismatch can
    still be a real signal under corroboration, so the recorded flag set
    stays the honest full set and belief Rule 2 applies the graduated
    delta (the 9.7 down-weight convention).

    Task 10.6 (audit gp-1 C-C-4, owner option (b)): a proxy-alibi
    ``alibi_vs_sighting`` -- the alibi's speaker is not its subject --
    whose conflicting sighting the SUBJECT'S OWN account agrees with is
    suppressed and re-targeted as a weak flag against the proxy speaker
    (see :func:`_detect_alibi_vs_sightings`). The subject-account lookup
    runs on the canonical claims BEFORE echo-dedup discards the
    subject's copy: when the proxy spoke first, the dedup keeps the
    proxy's copy and drops the subject's identical restatement, which is
    exactly when the subject's own account would otherwise be invisible
    (the seed-24 turn-order dependence the audit flagged).

    Task 10.10 (audit-2026-06-13-1816 C-C-2, C-C-3): a final guard runs
    AFTER the weak classification above -- when BOTH of a flag's events
    resolve to turns by the SAME speaker and that speaker is NOT a
    subject, the flag is one narrator's two proxy-claims about a third
    party conflicting with each other, so it re-targets WEAK at the
    speaker (:func:`_apply_proxy_intra_turn_guard`,
    :data:`WEAK_REASON_PROXY_INTRA_TURN`). The single-speaker condition
    leaves every cross-speaker pairing -- the legitimate two-witness
    disagreement and the impostor-frames-innocent deception frame --
    untouched.

    The function is pure: it does not mutate the transcript and has no
    side effects.
    """

    effective_roster = _NO_ROSTER if roster is None else roster
    indexed_alibis = tuple(
        indexed
        for indexed in _iter_alibis(transcript)
        if _subject_in_roster(indexed.claim.subject, effective_roster)
    )
    alibis = _dedupe_echo_alibis(indexed_alibis)
    sightings = tuple(
        indexed
        for indexed in _iter_sightings(transcript)
        if _subject_in_roster(indexed.observation.subject, effective_roster)
    )

    flags: list[ContradictionRef] = []
    flags.extend(
        _detect_alibi_conflicts(alibis, accusation_pairs=_accusation_pairs(transcript))
    )
    flags.extend(
        _detect_alibi_vs_sightings(
            alibis=alibis,
            sightings=sightings,
            subject_accounts=_subject_account_index(
                alibis=indexed_alibis, sightings=sightings
            ),
        )
    )
    guarded = _apply_proxy_intra_turn_guard(
        flags, event_speakers=_event_speaker_index(transcript)
    )
    return tuple(sorted(guarded, key=lambda flag: flag.contradiction_id))


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
    trigger_kind: MeetingTriggerKind | None = None,
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
    not a second voice). No-room sides (non-spatial labels) corroborate
    nothing, mirroring the contradiction side.

    Relevance gate (Task 10.6; audit gp-2 C-C-3): every supporting
    sighting additionally passes :func:`is_relevant_sighting` against
    the meeting's :func:`triggering_body_rooms` -- a spawn-window
    (tick 0-1) sighting or a kill-scene sighting (subject seen in the
    triggering body's room inside the corroborated window) is
    evidentially empty and corroborates nothing. Gated at this one home
    so every detector-derived Rule-3 corroboration -- the recording-time
    path and the post-meeting belief fold alike -- sees the identical
    gate.

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
    body_rooms = triggering_body_rooms(transcript, trigger_kind=trigger_kind)

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
            if not is_relevant_sighting(
                tick=sighting.observation.tick,
                rooms=sighting.rooms,
                triggering_body_rooms=body_rooms,
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


def independent_voices(
    transcript: MeetingTranscript,
    *,
    roster: frozenset[PlayerId] | None = None,
    trigger_kind: MeetingTriggerKind | None = None,
) -> Mapping[PlayerId, tuple[PlayerId, ...]]:
    """The INDEPENDENT VOICES against each accused subject (Tasks 10.7, 10.15).

    The pure transcript half of the pre-vote testimony fold (audit gp-2
    C-C-1/C-C-2 and the 2026-06-13 audit C-C-1/H-4; the
    corroborate-within-round owner principle and the belief-spread-first
    owner decision 2026-06-14). The voice COUNT a subject carries drives
    two pre-vote channels off ONE derivation:

    * **two-witness fold** (Task 10.7) -- at least
      :data:`agents.memory.beliefs.TESTIMONY_INDEPENDENCE_BAR` distinct
      voices; the subject takes the +0.05 accused-bump pre-vote;
    * **single-witness inform** (Task 10.15;
      :data:`agents.memory.beliefs.WITNESS_INFORM_REASON`) -- exactly ONE
      voice (below the fold bar); the subject takes the SAME +0.05
      pre-vote, spreading one witness's first-hand testimony to the
      listeners so near-gate priors can cross the §4.6 gate within the
      round (it informs, it cannot eject a baseline listener alone).

    Returns ``{subject: sorted distinct voice speakers}`` for every
    subject with at least one voice; subjects accused only by voiceless
    turns are absent. The fold-vs-inform split is the caller's
    (:func:`meetings.manager.derive_belief_evidence` thresholds on
    ``len(speakers)``); this helper just counts independent voices. A
    voice is one of:

    * **A chain/opening turn accusing the subject** (``turn_kind`` in
      ``opening`` / ``reply``) that carries OBSERVATION BACKING -- at
      least one first-hand observation claim whose canonical room is
      spatial and which passes the §6.3 relevance predicate
      (:func:`is_relevant_sighting` against this meeting's
      :func:`triggering_body_rooms` -- one home, reused verbatim from
      the Task 10.6 corroboration gate). A bare verbal accusation
      carries no voice, and neither does a turn whose only located
      content is evidentially empty: spawn-window (tick 0-1)
      observations and kill-scene observations are exactly the
      everyone-can-say-it shapes (the seed-30 deflection's only
      sightings sat at the kill scene -- no voice).
    * **An opt-in corroboration aligned with an existing accuser**: an
      ``opt_in`` turn whose :class:`CorroborationClaim` supports a
      player who accused the subject this meeting, where the opt-in
      turn itself carries the same observation backing. An opt-in
      turn's DIRECT accusation never adds a voice -- the §5.2 opt-in
      phase is where pile-ons form (seed 30 m1: two opt-in accusers of
      p-7 whose corroborations aligned with an accuser of a DIFFERENT
      subject), and witness count alone cannot filter a pile-on; the
      corroboration-targeting requirement is the independence gate the
      owner decision named ("accuse-capable opt-in corroborations count
      as the second voice").

    Backing is deliberately TURN-LEVEL: the voice's turn must stake
    relevance-grade first-hand content, not specifically a sighting of
    the accused -- on the Wave-0 set the two-witness yield meetings
    (seeds 2/5 m1) carry no sighting of the folded subject anywhere in
    the transcript (the witnesses stake their own whereabouts and
    co-movement), so a subject-targeted gate would silence the channel
    the audit's §4.2 simulation proved out while the turn-level gate
    reproduces its rows exactly and still zeroes the seed-30 pile-on.

    Voices are distinct speakers and never the subject (a
    self-accusation or a subject's own vouch for their accuser adds
    nothing). ECHO-DEDUP (Task 10.15; audit 2026-06-13 H-4): distinct
    speakers whose voice-minting turns carry the SAME rationale text
    (normalised by :func:`_normalize_rationale`) collapse to ONE voice --
    the 9B's verbatim rationale copying (163 within-meeting echo pairs)
    is copied reasoning, not independent corroboration, and cannot
    manufacture the independence the fold/inform read off the count. The
    first speaker (in canonical turn order) to stake a rationale keeps
    the voice; later copies of it are echoes. A rationale that normalises
    to empty stakes no reasoning and never echo-matches. "An accuser of
    the subject" means any speaker with a recorded
    :class:`AccusationClaim` against the subject, any turn kind -- an
    opt-in accusation is as public as a chain one. The
    roster filter mirrors :func:`detect_contradictions`: ``roster=None``
    indexes every subject (unit-test behaviour); an explicit roster --
    the live path passes the living participants, the replay path the
    recorded ballot voters -- drops non-roster subjects. Claims are
    read AS RECORDED, after the per-turn chokepoint guards, so a
    teammate accusation (stripped, Task 7.12) or a non-roster subject
    (dropped, Task 10.2) can never mint a voice. Pure and
    deterministic: same transcript, byte-identical voices.
    """

    effective_roster = _NO_ROSTER if roster is None else roster
    body_rooms = triggering_body_rooms(transcript, trigger_kind=trigger_kind)

    # Transcript-wide accuser index: subject -> speakers with a recorded
    # accusation against them (never the subject accusing themselves).
    accusers: dict[PlayerId, set[PlayerId]] = {}
    for turn in transcript.turns:
        for claim in turn.claims:
            if (
                isinstance(claim, AccusationClaim)
                and claim.against != turn.speaker
                and _subject_in_roster(claim.against, effective_roster)
            ):
                accusers.setdefault(claim.against, set()).add(turn.speaker)

    voices: dict[PlayerId, set[PlayerId]] = {}
    # Echo-dedup state (Task 10.15; audit H-4): per subject, the normalised
    # non-empty rationales already counted as a voice. Turns are walked in
    # canonical order so the FIRST speaker to stake a rationale keeps the
    # voice and later copies of it drop -- deterministic regardless of how an
    # external producer ordered the transcript.
    seen_rationales: dict[PlayerId, set[str]] = {}
    for turn in sort_turns_canonically(transcript.turns):
        if not _carries_relevant_observation(turn, triggering_body_rooms=body_rooms):
            continue
        if turn.turn_kind in ("opening", "reply"):
            for claim in turn.claims:
                if not isinstance(claim, AccusationClaim):
                    continue
                subject = claim.against
                if subject == turn.speaker:
                    continue
                if not _subject_in_roster(subject, effective_roster):
                    continue
                _register_voice(
                    subject=subject,
                    turn=turn,
                    voices=voices,
                    seen_rationales=seen_rationales,
                )
        elif turn.turn_kind == "opt_in":
            for claim in turn.claims:
                if not isinstance(claim, CorroborationClaim):
                    continue
                for subject, subject_accusers in accusers.items():
                    if claim.supports not in subject_accusers:
                        continue
                    if subject == turn.speaker:
                        continue
                    _register_voice(
                        subject=subject,
                        turn=turn,
                        voices=voices,
                        seen_rationales=seen_rationales,
                    )

    return {
        subject: tuple(sorted(speakers)) for subject, speakers in sorted(voices.items())
    }


def _carries_relevant_observation(
    turn: MeetingTurn, *, triggering_body_rooms: frozenset[str]
) -> bool:
    """Whether ``turn`` stakes relevance-grade first-hand content (Task 10.7).

    The observation-backing gate of :func:`independent_voices`: at least
    one of the turn's observation claims (sighting, task completion, or
    body discovery alike -- each carries a room and a tick) must
    canonicalise to a SPATIAL room (:func:`canonical_rooms`; a
    placeholder label locates nothing, so it backs nothing) and pass
    :func:`is_relevant_sighting` against the meeting's kill scene. The
    triggering body's own ``found_body`` observation sits at the scene
    by construction and therefore never backs a voice on its own.
    """

    for observation in turn.observations:
        rooms = canonical_rooms(observation.room)
        if not rooms:
            continue
        if is_relevant_sighting(
            tick=observation.tick,
            rooms=rooms,
            triggering_body_rooms=triggering_body_rooms,
        ):
            return True
    return False


# Task 10.15 (audit 2026-06-13 H-4): the echo-dedup key. A turn's free-text
# rationale reduced to its lower-cased alphanumeric word tokens, so case,
# punctuation, and whitespace differences are erased and only a word-level
# rewrite survives. Two distinct voices that match after this normalisation are
# the 9B verbatim-copy class (the audit measured 163 within-meeting rationale
# echoes, 60-212 chars) -- copied reasoning, not independent corroboration.
_RATIONALE_ECHO_TOKEN: Final[re.Pattern[str]] = re.compile(r"[0-9a-z]+")


def _normalize_rationale(free_text: str) -> str:
    """Normalise a turn's rationale to its echo-dedup key (Task 10.15; H-4).

    Reduces ``free_text`` to space-joined lower-cased alphanumeric tokens.
    An empty / punctuation-only rationale normalises to ``""`` and is never
    treated as an echo (it stakes no reasoning to copy), so a genuine second
    witness who wrote nothing in free-text is never collapsed away.
    """

    return " ".join(_RATIONALE_ECHO_TOKEN.findall(free_text.casefold()))


def _register_voice(
    *,
    subject: PlayerId,
    turn: MeetingTurn,
    voices: dict[PlayerId, set[PlayerId]],
    seen_rationales: dict[PlayerId, set[str]],
) -> None:
    """Count ``turn.speaker`` as an independent voice against ``subject``.

    Two guards drop a non-independent voice (Tasks 10.7, 10.15):

    * **speaker dedup** -- a speaker already counted for the subject adds
      nothing however many claims or turns they stake (Task 10.7);
    * **echo dedup** -- a distinct speaker whose turn repeats a rationale
      already counted for the subject is an echo of it, not a new voice
      (Task 10.15; audit H-4). The repeated rationale is still recorded
      against the subject when the speaker is already counted, so a later
      copy of that speaker's other turns is caught too.
    """

    speakers = voices.setdefault(subject, set())
    rationale = _normalize_rationale(turn.free_text)
    seen = seen_rationales.setdefault(subject, set())
    if turn.speaker in speakers:
        # Already a voice; still register this rationale so a later distinct
        # speaker copying it is recognised as an echo.
        if rationale:
            seen.add(rationale)
        return
    if rationale and rationale in seen:
        return
    speakers.add(turn.speaker)
    if rationale:
        seen.add(rationale)


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


@dataclass(frozen=True)
class _SubjectAccount:
    """One self-stated location account: rooms over an inclusive tick range.

    The unit of the Task 10.6 proxy consistency check: a subject's own
    :class:`AlibiClaim` about themselves contributes its window, and a
    subject's own ``saw_player`` self-observation contributes its single
    tick. Built from the PRE-echo-dedup claim set, because the dedup
    keeps the FIRST statement of an account -- when a proxy speaker
    states the subject's alibi before the subject does, the subject's own
    copy is exactly the one the dedup discards (the seed-24 turn-order
    dependence).
    """

    rooms: frozenset[str]
    from_tick: int
    to_tick: int


def _subject_account_index(
    *,
    alibis: tuple[_IndexedAlibi, ...],
    sightings: tuple[_IndexedSighting, ...],
) -> Mapping[PlayerId, tuple[_SubjectAccount, ...]]:
    """Each subject's OWN location accounts, in transcript order (Task 10.6).

    ``alibis`` is the pre-dedup indexed set (see :class:`_SubjectAccount`
    for why); only self-stated artifacts qualify -- an alibi whose
    speaker is its subject, a sighting whose speaker is its subject (the
    model records its own movement as ``saw_player`` of itself, e.g. the
    seed-28 "saw myself in WEST_HALL at 17" account). Non-spatial
    accounts (no canonical room) carry no location and are skipped.
    """

    index: dict[PlayerId, list[_SubjectAccount]] = {}
    for alibi in alibis:
        if alibi.speaker == alibi.claim.subject and alibi.rooms:
            index.setdefault(alibi.claim.subject, []).append(
                _SubjectAccount(
                    rooms=alibi.rooms,
                    from_tick=alibi.claim.from_tick,
                    to_tick=alibi.claim.to_tick,
                )
            )
    for sighting in sightings:
        if sighting.speaker == sighting.observation.subject and sighting.rooms:
            index.setdefault(sighting.observation.subject, []).append(
                _SubjectAccount(
                    rooms=sighting.rooms,
                    from_tick=sighting.observation.tick,
                    to_tick=sighting.observation.tick,
                )
            )
    return {subject: tuple(accounts) for subject, accounts in index.items()}


def _subject_account_agrees(
    accounts: tuple[_SubjectAccount, ...],
    *,
    sighting_rooms: frozenset[str],
    window_from: int,
    window_to: int,
) -> bool:
    """Whether the subject's own account agrees with a conflicting sighting.

    True when ANY of the subject's own accounts places them in the
    sighting's room (canonical sets intersect) somewhere inside the
    contradicted proxy alibi's window ``[window_from, window_to]``. The
    window is the PROXY claim's, not the sighting's exact tick: the
    audited FP shape is an over-broad blanket alibi ("p-9 CAFETERIA
    0-18") contradicted by sightings the subject's own nearby account
    (WEST_HALL@17) corroborates -- demanding an exact-tick self-account
    would re-admit the FP whenever the sighting and the self-account sit
    one tick apart, while the subject admitting they were in the
    sighting's room inside the window is already the proxy claim
    refuted by its own subject.
    """

    return any(
        (account.rooms & sighting_rooms)
        and account.from_tick <= window_to
        and account.to_tick >= window_from
        for account in accounts
    )


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
    subject_accounts: Mapping[PlayerId, tuple[_SubjectAccount, ...]],
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
            # Proxy subject-account consistency (Task 10.6; audit gp-1
            # C-C-4, owner option (b)). A third-party alibi about the
            # subject can never be self-stated, so it always escaped to
            # the strong band -- the entire Wave-0 strong band was this
            # shape at 1 TP / 2 FP. When the subject's OWN pre-dedup
            # account agrees with the conflicting sighting, the subject
            # and the witness tell one story and the PROXY's claim is
            # the odd account out: suppress the flag against the subject
            # and re-target it -- capped at weak -- at the proxy
            # speaker, whose claim now conflicts with both the sighting
            # and the subject's own account. The seed-24 true positive
            # survives untouched: there the subject ECHOED the false
            # proxy alibi, so no self-account agrees with the sighting
            # and no suppression fires.
            if alibi.speaker != alibi.claim.subject and _subject_account_agrees(
                subject_accounts.get(alibi.claim.subject, ()),
                sighting_rooms=sighting.rooms,
                window_from=alibi.claim.from_tick,
                window_to=alibi.claim.to_tick,
            ):
                yield _build_contradiction(
                    kind="alibi_vs_sighting",
                    event_a_id=alibi.event_id,
                    event_b_id=sighting.event_id,
                    subjects=(alibi.speaker,),
                    description=_describe_retargeted_proxy(
                        speaker=alibi.speaker,
                        alibi=alibi.claim,
                        sighting=sighting.observation,
                    ),
                )
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


def _describe_retargeted_proxy(
    *,
    speaker: PlayerId,
    alibi: AlibiClaim,
    sighting: SawPlayerObservation,
) -> str:
    # The re-targeted flag names the PROXY speaker, so the description
    # must say who claimed what about whom and why the conflict points
    # back at the claimant -- the rendered memory view is the only place
    # a voter learns this (§5.4 "flags are information"). Always weak:
    # the WEAK_REASON_RETARGETED_PROXY marker is what caps belief Rule
    # 2's delta at the graduated band, so a re-target can never eject
    # alone (the gp-1 over-suppression tripwire).
    base = (
        f"Alibi by {speaker} places {alibi.subject} in {alibi.room} "
        f"(ticks {alibi.from_tick}-{alibi.to_tick}); sighting reports "
        f"{sighting.subject} in {sighting.room} at tick {sighting.tick}, and "
        f"{alibi.subject}'s own account agrees with the sighting -- the "
        f"conflict re-targets the alibi's speaker."
    )
    return f"{base} {WEAK_CONTRADICTION_MARKER_PREFIX}{WEAK_REASON_RETARGETED_PROXY}]"


# -- Internal: proxy-intra-turn guard (Task 10.10) --------------------------


def _event_speaker_index(transcript: MeetingTranscript) -> Mapping[str, PlayerId]:
    """Map every claim/observation event id to the player who STATED it.

    Reuses the :func:`_turn_claim_id` / :func:`_turn_observation_id`
    writers (one home for the id format, exactly the parse
    :func:`contradiction_lift_key` relies on) so a flag's
    ``event_a_id``/``event_b_id`` resolve back to ``turn.speaker``. Built
    once per :func:`detect_contradictions` call and consumed by
    :func:`_apply_proxy_intra_turn_guard`.
    """

    index: dict[str, PlayerId] = {}
    for turn in transcript.turns:
        for claim_index in range(len(turn.claims)):
            index[_turn_claim_id(turn=turn, index=claim_index)] = turn.speaker
        for obs_index in range(len(turn.observations)):
            index[_turn_observation_id(turn=turn, index=obs_index)] = turn.speaker
    return index


def _apply_proxy_intra_turn_guard(
    flags: Iterable[ContradictionRef],
    *,
    event_speakers: Mapping[str, PlayerId],
) -> list[ContradictionRef]:
    """Re-target same-speaker proxy contradictions WEAK at the speaker.

    Task 10.10 (audit-2026-06-13-1816 C-C-2, C-C-3). For each flag whose
    BOTH events resolve to the SAME speaker, the flag is one narrator's
    single unreliable turn about a third party -- a flag-stacking
    artifact, not independent evidence. Two sub-cases:

    * the flag still names the third-party subject -> rebuild it WEAK
      against the speaker (:func:`_retarget_proxy_intra_turn`); and
    * the flag was ALREADY re-targeted at this same speaker by the 10.6
      cross-speaker proxy rule (its sighting happened to be self-authored,
      so ``subjects`` is already the speaker and it carries
      :data:`WEAK_REASON_RETARGETED_PROXY`) -> fold it under the same
      proxy-intra-turn lift key (:func:`_fold_proxy_intra_turn`). Without
      this, a 10.6 + 10.10 pair on one speaker's turn keeps distinct
      per-claim keys and stacks across the §4.6 gate (0.5 + 0.08*n).

    Every other flag -- a self-pair / self-stated contradiction (the
    speaker IS the genuine subject) and all cross-speaker pairings
    (two-witness disagreements, the impostor-frames-innocent deception
    frame) -- passes through untouched. Runs AFTER the weak
    classification, so an already-weak flag stays weak.

    Order-preserving and pure: the result is re-sorted by
    ``contradiction_id`` upstream, and neither re-target nor fold changes
    the ``contradiction_id`` (kind + event-id pair are unchanged), so the
    detector stays byte-identical across runs.
    """

    guarded: list[ContradictionRef] = []
    for flag in flags:
        speaker_a = event_speakers.get(flag.event_a_id)
        speaker_b = event_speakers.get(flag.event_b_id)
        if speaker_a is None or speaker_a != speaker_b:
            # Cross-speaker or an event the index does not know: the
            # legitimate two-witness / deception frames pass through.
            guarded.append(flag)
        elif speaker_a not in flag.subjects:
            # Single author, flag aimed at a third party: re-target WEAK.
            guarded.append(_retarget_proxy_intra_turn(flag, speaker=speaker_a))
        elif WEAK_REASON_RETARGETED_PROXY in flag.description:
            # Single author already re-targeted at themselves by 10.6:
            # fold under the proxy-intra-turn key so it cannot stack with
            # this turn's 10.10 re-target on the same speaker.
            guarded.append(_fold_proxy_intra_turn(flag))
        else:
            # Single author who IS the genuine subject -- a self-pair /
            # self-stated contradiction, the weak band's own business.
            guarded.append(flag)
    return guarded


def _retarget_proxy_intra_turn(
    flag: ContradictionRef, *, speaker: PlayerId
) -> ContradictionRef:
    # Re-target the flag at the speaker who authored both events, capped
    # WEAK so a re-target can never eject alone. The factual base text and
    # any prior weak reasons are PRESERVED (the conflicting claims and
    # their geometry are still information, §5.4); the proxy-intra-turn
    # reason is appended so the marker says the conflict points back at the
    # one narrator. The event-id pair is reused verbatim so
    # :func:`_build_contradiction` recomputes the identical
    # ``contradiction_id`` (only the subject and description move).
    base, reasons = _split_weak_marker(flag.description)
    annotated = (
        f"{base} Both conflicting claims were stated by {speaker} about "
        f"another player; the conflict re-targets the speaker."
    )
    if WEAK_REASON_PROXY_INTRA_TURN not in reasons:
        reasons = (*reasons, WEAK_REASON_PROXY_INTRA_TURN)
    description = f"{annotated} {WEAK_CONTRADICTION_MARKER_PREFIX}{'; '.join(reasons)}]"
    return _build_contradiction(
        kind=flag.kind,
        event_a_id=flag.event_a_id,
        event_b_id=flag.event_b_id,
        subjects=(speaker,),
        description=description,
    )


def _fold_proxy_intra_turn(flag: ContradictionRef) -> ContradictionRef:
    # A flag the 10.6 rule already re-targeted at the single author who
    # authored BOTH its events: keep its subject and its
    # WEAK_REASON_RETARGETED_PROXY reason, but append the proxy-intra-turn
    # reason so :func:`contradiction_lift_key` returns the shared fold key
    # and belief Rule 2 collapses it with this turn's other same-author
    # re-targets (the gp-1 over-stack the 10.6+10.10 interaction would
    # otherwise re-open). Subject and event ids are unchanged, so the
    # ``contradiction_id`` is stable.
    base, reasons = _split_weak_marker(flag.description)
    if WEAK_REASON_PROXY_INTRA_TURN in reasons:
        return flag
    reasons = (*reasons, WEAK_REASON_PROXY_INTRA_TURN)
    description = f"{base} {WEAK_CONTRADICTION_MARKER_PREFIX}{'; '.join(reasons)}]"
    return _build_contradiction(
        kind=flag.kind,
        event_a_id=flag.event_a_id,
        event_b_id=flag.event_b_id,
        subjects=flag.subjects,
        description=description,
    )


def _split_weak_marker(description: str) -> tuple[str, tuple[str, ...]]:
    """Split a description into its base text and its weak-signal reasons.

    The inverse of the ``f"{base} {WEAK_CONTRADICTION_MARKER_PREFIX}{'; '
    .join(reasons)}]"`` append the describe helpers perform -- a
    deterministic operation over the detector's OWN marker format, never
    LLM free text. A description with no marker returns ``(description,
    ())``.
    """

    marker = f" {WEAK_CONTRADICTION_MARKER_PREFIX}"
    cut = description.find(marker)
    if cut == -1:
        return description, ()
    base = description[:cut]
    inner = description[cut + len(marker) :].rstrip("]")
    reasons = tuple(inner.split("; ")) if inner else ()
    return base, reasons


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
    "CANONICAL_ROOMS",
    "NARROW_ALIBI_WINDOW_TICKS",
    "SPAWN_WINDOW_LAST_TICK",
    "WEAK_CONTRADICTION_MARKER_PREFIX",
    "WEAK_REASON_ADVERSARIAL",
    "WEAK_REASON_BOUNDARY_OVERLAP",
    "WEAK_REASON_ENDPOINT_TICK",
    "WEAK_REASON_NARROW_WINDOW",
    "WEAK_REASON_PROXY_INTRA_TURN",
    "WEAK_REASON_RETARGETED_PROXY",
    "WEAK_REASON_SELF_PAIR",
    "WEAK_REASON_SELF_STATED",
    "ChainStep",
    "ChainTermination",
    "ChainWalk",
    "DetectedCorroboration",
    "StatedPlacement",
    "accusation_target",
    "canonical_rooms",
    "contradiction_lift_key",
    "detect_contradictions",
    "detect_corroborations",
    "independent_voices",
    "is_canonically_ordered",
    "is_relevant_sighting",
    "is_weak_contradiction",
    "next_chain_step",
    "reconstruct_stated_paths",
    "sort_turns_canonically",
    "triggering_body_rooms",
    "walk_chain",
]
