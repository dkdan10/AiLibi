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

Task 13.3 (report-phase-b-plan B2; report-grounding-audit P1 "add an
inferential path"): a genuinely-INDEPENDENT cross-speaker
``alibi_conflict`` -- two DISTINCT non-subject speakers placing the same
subject in two disjoint rooms over overlapping ticks -- is a real
inferential STRONG signal, the one contradiction class derived from
testimony alone rather than from "was the impostor seen?". It is already
not self-stated, so its only weak markers are the four
:func:`_conflict_weak_reasons` guards (self-pair / adversarial / narrow /
boundary); when NONE of those fire the conflict carries no marker, so
:func:`is_weak_contradiction` returns ``False`` and a $0 re-extraction of
the committed replays stamps ``strong=True`` (the extractor re-runs this
detector over the recorded transcript). The four guards stay byte-identical
-- the adversarial guard in particular MUST remain, because an impostor
weaponised a counter-alibi (seed 13 m2) -- so promotion reaches ONLY the
independent shape, never an accuser/accused, self, narrow, or movement-pair
conflict. A STRONG flag naming a CREWMATE is a false positive (it both
Goodharts R7 and risks a wrong ejection), so the promotion is deliberately
confined to the genuinely-independent shape and role-gated downstream.

Task 13.4 (report-phase-b-plan B3/B4): the ``alibi_vs_physical`` kind -- the
R7 lever 13.3 could not light (the committed transcripts held nothing to
promote). It reconstructs each subject's STATED room-by-tick path from the
public ``saw_player`` observations (:func:`reconstruct_stated_paths`) and flags
a subject's OWN alibi that independent CO-PRESENCE placements physically
contradict -- a disjoint room at a strictly interior tick of the alibi window.
Co-presence ONLY: a self-alibi contradicted by a DIRECT sighting of the subject
is the audited seed-3 shape (8/13 wrong ejections) and stays the 9.7 weak
``alibi_vs_sighting`` band; the net-new signal is a witness placing the subject
ALONGSIDE someone else, which the alibi-vs-sighting path (a sighting's OWN
subject only) cannot reach. THE CRUX is role-gating: a STRONG flag is reserved
for the TWO-SOURCE conjunction -- the subject's UNCORROBORATED alibi AND
>= :data:`PHYSICAL_CONTRADICTION_MIN_VOICES` distinct non-adversarial
co-presence voices contradicting it -- never mere two-source co-placement; a
LONE contradicting voice still emits, but WEAK (informs, cannot eject alone).
The ceiling probe (``experiments/lab/inference_testimony_probe.py``) found 26
impostor- but ALSO 28 crewmate-subjects share two-source COVERAGE, so a
co-placement detector false-positives on crew; keying on the subject's
CONTRADICTED, uncorroborated alibi does not. Perception-time absence/last-seen
forms are DROPPED: the firewall exposes no per-player liveness channel, so all
such inference lives in the meeting layer over public testimony
(:func:`_detect_alibi_vs_physical`).

Task 15.4 (vent observability): the ``vent_sighting`` kind -- the game's
hardest evidence made speakable. A spoken
:class:`~meetings.schemas.SawVentObservation` is role-proving (vents are
impostor-only, DESIGN.md §3.4) but speech alone must NEVER mint hard
evidence: a model that hallucinates a vent sighting against an innocent
would otherwise fabricate a STRONG flag, re-opening the railroad class
Phase 14 eliminated. The GROUNDING chokepoint is the whole defense:
:func:`detect_contradictions` takes the speakers' own typed
:class:`~meetings.schemas.VentWitnessRecord` channels
(``vent_witness_records``, threaded by the manager from the
``MeetingAwareAgent.vent_witness_records_for_meeting()`` accessor) and a
STRONG flag fires only when the spoken observation matches one of the
SPEAKER'S OWN records (same subject, canonically intersecting room, tick
within :data:`VENT_GROUNDING_TICK_TOLERANCE`) -- a deterministic comparison
against reconstructed memory, never LLM judgment and never rendered prose.
An ungrounded spoken vent claim records as ordinary testimony and raises NO
flag. A grounded flag can only name a genuine venter (engine event ->
witness-gated packet -> episodic record -> typed channel), so the
"a STRONG flag naming a CREWMATE is a false positive" crux is satisfied by
construction. The flag's description quotes the RECORD (the deterministic
memory), while both event ids reference the spoken observation -- the
public, citable surface ``VoteBallot.primary_reason_id`` reaches through
the turn id. Vent flags are appended AFTER the 10.10 proxy-intra-turn
guard by design: that guard re-targets one narrator's two conflicting
proxy CLAIMS, while a grounded vent flag is a single memory-confirmed
observation, not a claim pair -- gutting it there would delete exactly the
evidence this rule exists to carry.

Task 16.7 (pooling substrate): sightings made speakable-and-checkable the
way 15.4 made vents so, with the polarity INVERTED. A spoken
:class:`~meetings.schemas.SawPlayerObservation` that matches one of the
SPEAKER'S OWN typed :class:`~meetings.schemas.SightingRecord` rows
(same subject, canonically intersecting room, tick within
:data:`SIGHTING_GROUNDING_TICK_TOLERANCE`) is a GROUNDED VOUCH:
:func:`grounded_vouch_subjects` surfaces its subject into the meeting's
relevance-gated ``corroborated`` set (the existing -0.05 exculpation
channel priced by
:data:`agents.memory.beliefs.CORROBORATION_SUSPICION_DELTA`), NEVER a
contradiction flag and NEVER the dead trust field -- grounding a sighting
proves the speaker honestly reported what they saw, not that the subject
is innocent. An ungrounded vouch stays ordinary testimony, and a
FABRICATED vouch (no matching record) moves nothing -- the anti-collusion
floor. Known property (not a bug): grounding cannot catch an impostor who
TRUTHFULLY vouches for its partner ("I really did see them in Medbay") --
the sighting is true, so the -0.05 is earned legitimately; it is small by
design, and the collusion PATTERN (mutual vouching) stays visible in the
transcript as material for Phase 17's detectors. The mechanism ships
INERT: committed transcripts already carry speaker-groundable sightings,
so the production pre-vote call does not pass the participant record
mapping yet -- the live feed graduates under the phase's byte-identity
lever doctrine (see :func:`meetings.manager.derive_belief_evidence`). The
``whereabouts`` observation kind (a SELF-placement, "I was in
``room`` at ``tick``") is PROSECUTABLE but never EXCULPATORY -- the same
polarity the vouch channel draws. It is indexed by :func:`_iter_alibis` as
a degenerate single-tick self-alibi, so lying in it is prosecuted by the
EXISTING alibi rules (``alibi_vs_sighting`` / ``alibi_conflict``, no new
flag kind), and :func:`reconstruct_stated_paths` places its speaker by it
so answering roll-call puts you on the public record (out of Task 16.8's
absent set). But it is deliberately kept OUT of the two channels a
self-placement has no business feeding: :func:`detect_corroborations`
(``include_whereabouts=False``) -- a colluder confirming a roll-call answer
with a fabricated sighting must not earn the subject an ungrounded -0.05,
the anti-collusion floor -- and :func:`_carries_relevant_observation`'s
accusation-backing gate -- a self-placement is no evidence about the
accused, so it cannot promote a bare accusation into an independent voice.

Two INDEPENDENT flag-minting rules (audit-phase-18-planning.md §3.3;
audit-phase-17-close.md §6 item 4). (1) The endpoint-band
whereabouts exemption: a spoken
:class:`~meetings.schemas.WhereaboutsClaim` indexes as a DEGENERATE SINGLE-TICK
SELF-ALIBI (``from_tick == to_tick``, speaker is subject), so BEFORE the exemption
a contradicting first-hand sighting sat on an endpoint tick and was banded WEAK --
§3.3's finding that roll-call lies could NEVER mint a STRONG flag (25 corpus lies,
all weak). The exemption adjudicates that single tick as the claim's INTERIOR (not
its edge) for exactly this class: the narrow-window and endpoint-tick weak reasons
drop and a contradicting sighting mints a STRONG ``alibi_vs_sighting`` flag.
Genuine multi-tick alibis keep the endpoint band and the two-source
discipline unchanged; a genuine single-tick self-stated
:class:`~meetings.schemas.AlibiClaim` is the SAME class by construction and is
exempted too. (2) The vent-placement flag variant: the 17.5 scope firewall's
flag-minting arm, routed by the close. A spoken
:class:`~meetings.schemas.SawVentObservation` GROUNDED against the speaker's own
typed :class:`~meetings.schemas.VentWitnessRecord` (the 15.4 chokepoint reused
VERBATIM) whose RECORD contradicts the subject's OWN stated path mints a STRONG
``alibi_vs_physical`` flag. Grounded-only is the whole firewall: an UNGROUNDED
spoken vent claim mints NOTHING (a fabrication channel otherwise). STRONG with
no weak band mirrors the 15.4 vent doctrine -- the grounding chain proves a
genuine venter (impostor-only), so the "STRONG flag naming a CREWMATE" false
positive is structurally unreachable, which is also why the record-side window
is INCLUSIVE here (endpoint band prices coarse spoken recollection fuzz between
two testimonies, but the record side is typed engine truth). No corroboration
suppression and no adversarial-pair guard: engine truth beats forgeable
testimony, mirroring kill_scene's "can only CONTRADICT, never corroborate".

Movement claims
===============

A witnessed transition is two facts -- the subject was in A at ``T-1`` and in B
at ``T`` -- and a witness with only the static
:class:`~meetings.schemas.SawPlayerObservation` to speak with must pick one
room. Picking the ORIGIN states a placement that was already false when the
witness saw it, and the detector then prosecutes the SUBJECT's truthful answer
for disagreeing with it. Two arms close that, both grounded on the
SPEAKER'S OWN typed :class:`~meetings.schemas.MoveWitnessRecord` channel: a
spoken placement the speaker's own record moved the subject OUT of at that exact
tick is re-read at the DESTINATION before pairing, and a spoken
:class:`~meetings.schemas.SawMoveObservation` participates as the destination
placement. Grounding is the firewall -- an UNGROUNDED spoken sighting is never
rewritten, so the rule can only re-read testimony the speaker demonstrably
held and can never launder a fabrication into a different room. The resolution
rewrites the indexed sighting's ROOM only: the event id, the speaker and every
id-keyed downstream surface are untouched.
This is the movement-driven contradiction rule Task 13.5.4 deferred when it
shipped the render (tasks/phase-13-5.md:271).

Grounded prosecution
====================

A spoken vent grounds against the speaker's own record before it can mint a
flag, and a spoken sighting grounds against the speaker's own record before it
can earn its subject the -0.05 vouch. The PROSECUTORIAL half of the sighting
channel was never checked: any spoken
:class:`~meetings.schemas.SawPlayerObservation` could mint a STRONG
``alibi_vs_sighting`` flag on the strength of speech alone. Three rules bind
that ONE kind, gated on ONE predicate -- the caller supplied a
``sighting_records`` mapping:

* **grounding** -- a spoken sighting is GROUNDED iff the speaker holds a
  matching own :class:`~meetings.schemas.SightingRecord`
  (:func:`sighting_observation_matches_record`, the vouch channel's predicate
  verbatim). An ungrounded sighting still mints its flag -- flags are
  information (DESIGN.md §5.4) -- but never a STRONG one. A placement the
  movement chokepoint produced is grounded by construction (it required the
  speaker's own :class:`~meetings.schemas.MoveWitnessRecord`) and is exempt:
  the two episodic channels are disjoint, so a witness who saw a DEPARTURE
  holds no ``SightingRecord`` at the destination.
* **two sources** -- a STRONG ``alibi_vs_sighting`` needs
  :data:`meetings.constants.GROUNDED_PROSECUTION_MIN_SOURCES` distinct SPEAKERS
  behind the case: grounded speakers contradicting one subject over one claim,
  plus the speakers behind any ``vent_sighting`` / ``alibi_vs_physical`` flag
  naming that subject in this meeting. One narrator counts once however many
  channels they speak through, and the two parties to the dispute -- the
  subject and the author of the contradicted claim -- never count at all.
* **single-tick endpoint** -- the degenerate ``from_tick == to_tick``
  self-placement is no longer adjudicated as its own interior, so it keeps the
  narrow-window / endpoint band.

Two rulings are superseded by these rules, and stand untouched only for a caller
supplying no ``sighting_records`` mapping:

* the 2026-06-22 LONE-STRONG relaxation (tasks/phase-13.md:700, "a
  single-witness ``alibi_vs_sighting`` contradiction MAY cross the gate") --
  superseded by rule two;
* the Task 18.9 endpoint-band whereabouts exemption, which promoted roll-call
  answers to STRONG -- superseded by rule three.

Map-aware arbitration
=====================

The one cross-agent aggregation this module performs is geometry-blind: it
compares a room-at-a-tick to a room-at-a-tick, and nothing under ``meetings``
knows the station is a graph. Two rooms that share a doorway are one tick of
walking apart, so an alibi in one and a sighting in the other at the window's
edge are two honest accounts of one transit -- and the engine enforces exactly
that geometry, permitting no non-adjacent step on any tick of any game. The
detector reads the map: such a pair carries
:data:`WEAK_REASON_ADJACENT_ONE_TICK` and informs instead of convicting, while a
two-hop pair, or a sighting two or more ticks inside a claim of continuous
presence, keeps its STRONG band -- an out-and-back excursion costs two ticks,
which the claim's interior rules out anyway. Adjacency is
:data:`CANONICAL_ROOM_NEIGHBORS`, frozen beside :data:`CANONICAL_ROOMS` under
the same "DATA, not an engine import" discipline and pinned against the map.
The flag is demoted, never dropped: flags are information (DESIGN.md §5.4), the
id set is identical either way, and :func:`is_weak_contradiction` routes the
pair through belief Rule 2's graduated down-weight.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Literal

from meetings.constants import (
    GROUNDED_PROSECUTION_MIN_SOURCES,
    MAP_ARBITRATION_MAX_HOPS,
    MAP_ARBITRATION_MAX_TICK_GAP,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    MoveWitnessRecord,
    PlayerId,
    RoomId,
    SawKillObservation,
    SawMoveObservation,
    TaskActivityAccount,
    SawPlayerObservation,
    SawVentObservation,
    SightingRecord,
    VentWitnessRecord,
    WhereaboutsClaim,
)

_ContradictionKind = Literal[
    "alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical", "vent_sighting"
]

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

# Task 13.4 (report-phase-b-plan B3/B4): the lone-atom weak band of the new
# ``alibi_vs_physical`` kind. A SINGLE independent co-presence placement
# contradicting an uncorroborated self-alibi is a real inferential atom but
# below the two-source bar, so it carries this marker -- :func:`is_weak_
# contradiction` returns True and belief Rule 2 down-weights it: it INFORMS but
# cannot eject alone (the phase-B plan's "a single inferential atom emits at the
# weak/mid band"). A SECOND independent voice promotes the same contradiction to
# STRONG (no marker).
WEAK_REASON_LONE_PHYSICAL: Final[str] = "single-voice physical contradiction"

# Task 13.5.3 (the witnessed-kill kill-scene intensification; owner-LOCKED
# STRICT 2026-06-26): the lone-atom weak band of a KILL-SCENE
# ``alibi_vs_physical`` placement -- a SINGLE independent co-presence placing
# the accused at the BODY's room within the kill window, contradicting an alibi
# elsewhere. Such placements are normally DROPPED by the reconstruction's
# kill-scene relevance gate ("presence at the scene must never EXONERATE"); the
# kill-scene recovery (unconditional since Task 14.9) restores them so a
# kill-scene placement
# can CONTRADICT a contradicting alibi. STRICT strictness: a lone kill-scene
# placement carries this marker -> :func:`is_weak_contradiction` is True and
# belief Rule 2 down-weights it to the sub-gate band, so a single forgeable
# kill-accusation INFORMS but cannot eject a crewmate alone. A SECOND
# independent source (another contradicting placement -- kill-scene or not --
# reaching :data:`PHYSICAL_CONTRADICTION_MIN_VOICES` voices) promotes it to
# STRONG (no marker), exactly the 13.4 two-source conjunction. Distinct from
# :data:`WEAK_REASON_LONE_PHYSICAL` only to name the kill-scene origin in the
# rendered flag; both are read identically by :func:`is_weak_contradiction`.
WEAK_REASON_KILL_SCENE: Final[str] = "single-voice kill-scene placement"

# The two grounded-prosecution bands on ``alibi_vs_sighting``. Ungrounded: the sighting
# side is speech the speaker's own typed record does not support, so it informs
# but cannot convict. Lone grounded source: the sighting side IS grounded, but
# one speaker is the whole prosecution -- below
# :data:`meetings.constants.GROUNDED_PROSECUTION_MIN_SOURCES` and with no
# physical anchor naming the subject. Both are read by
# :func:`is_weak_contradiction` exactly like their siblings above; they are
# appended in this order when a flag earns both.
WEAK_REASON_UNGROUNDED_SIGHTING: Final[str] = "ungrounded sighting"
WEAK_REASON_LONE_GROUNDED_SOURCE: Final[str] = "single grounded source"

# The band map-aware arbitration adds to ``alibi_vs_sighting``. The alibi room and the
# sighting room share a doorway and the sighting sits within one tick of the
# window's nearest edge, so one tick of walking reconciles both accounts: the
# pair informs, but a corridor may not convict. Read by
# :func:`is_weak_contradiction` exactly like its siblings above, and appended
# LAST when a flag earns it alongside another reason.
WEAK_REASON_ADJACENT_ONE_TICK: Final[str] = "adjacent room one tick away"

# Task 13.4 (report-phase-b-plan B3/B4): the minimum number of DISTINCT
# independent CO-PRESENCE voices that must place a subject OUTSIDE their own
# stated alibi for the inferential ``alibi_vs_physical`` flag to fire STRONG.
# This is the "two-source conjunction" the ceiling probe (inference_testimony_
# probe.py) defines -- "subjects placed by >=2 DISTINCT other speakers" -- and
# it is the load-bearing role-gate. Requiring a SECOND independent voice makes
# the contradiction robust to a single mistaken co-presence mention, which is
# what separates a genuine fabricated alibi (multiple honest witnesses place the
# impostor away from their claim) from a one-off recall slip. A LONE voice still
# emits, but WEAK (:data:`WEAK_REASON_LONE_PHYSICAL`): it informs, cannot eject.
# (A direct sighting of the subject is a different lever -- the 9.7 weak
# ``alibi_vs_sighting`` band, the audited seed-3 shape behind 8/13 wrong
# ejections -- and is excluded from the physical detector entirely.)
PHYSICAL_CONTRADICTION_MIN_VOICES: Final[int] = 2

# Task 15.4 (vent observability): the tick tolerance of the vent grounding
# chokepoint. A spoken :class:`~meetings.schemas.SawVentObservation` grounds
# against one of the SPEAKER'S OWN typed
# :class:`~meetings.schemas.VentWitnessRecord` rows only when the subject
# matches, the canonical room sets intersect, and the spoken tick sits within
# this many ticks of the record's tick. The rendered memory line quotes the
# exact tick ("[tick N] You witnessed p-3 vent in X."), so a faithful model
# copies it verbatim; the tolerance absorbs small transcription slips without
# opening the window wide enough for a speaker to re-time a genuine record
# into a materially different account. Sized to match
# :data:`NARROW_ALIBI_WINDOW_TICKS` -- the detector's existing notion of a
# tick-scale rounding error.
VENT_GROUNDING_TICK_TOLERANCE: Final[int] = 2

# Task 16.7 (pooling substrate): the tick tolerance of the sighting-vouch
# grounding chokepoint -- the vent constant's polarity-inverted sibling. A
# spoken :class:`~meetings.schemas.SawPlayerObservation` grounds against one
# of the SPEAKER'S OWN typed :class:`~meetings.schemas.SightingRecord` rows
# only when the subject matches, the canonical room sets intersect, and the
# spoken tick sits within this many ticks of the record's tick
# (:func:`grounded_vouch_subjects`). Starts at the vent value; a NAMED
# constant precisely so the Task 16.17 measurement can retune the vouch
# window independently of the vent one.
SIGHTING_GROUNDING_TICK_TOLERANCE: Final[int] = 2

# The tick tolerance of the MOVEMENT grounding chokepoint: zero, unlike its two
# siblings above. A spoken placement grounds against one of the SPEAKER'S OWN
# :class:`~meetings.schemas.MoveWitnessRecord` rows only when the spoken tick
# EQUALS the record's tick. A window is unsafe here because the record names a
# transition rather than a position: a subject who crossed two rooms in
# consecutive ticks has two records, and a +-1 window would let a placement
# resolve to the wrong transition's destination -- re-reading testimony as a
# room the speaker never claimed. Exactness costs nothing the siblings' windows
# buy: the rendered movement line quotes the tick the placement must reuse.
MOVE_GROUNDING_TICK_TOLERANCE: Final[int] = 0

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

# Which canonical rooms share a doorway -- the map's room graph, frozen beside
# the room allowlist above and read for the same reason: :mod:`meetings` must
# stay engine-free (``agents`` imports this module, and agents/ must not
# transitively reach engine/ -- the §1.3 observation firewall, enforced by
# import-linter), so this is DATA, not an engine import.
#
# The station is a graph and every one of its room edges costs one tick of
# walking, which is what lets map-aware arbitration read "two
# adjacent rooms one tick apart" as transit rather than a lie. The duplication
# is pinned by a test asserting this table equals
# ``engine.world.load_canonical_map().room_neighbors`` for every room AND that
# every room edge's ``traversal_ticks`` is 1, so a map change that adds a
# multi-tick corridor fails loud here instead of quietly making "one hop = one
# tick" false.
CANONICAL_ROOM_NEIGHBORS: Final[Mapping[str, frozenset[str]]] = MappingProxyType(
    {
        "ADMIN": frozenset({"UPPER_HALL", "EAST_HALL", "WEST_HALL"}),
        "CAFETERIA": frozenset({"UPPER_HALL", "EAST_HALL", "WEST_HALL"}),
        "EAST_HALL": frozenset({"ADMIN", "CAFETERIA", "ENGINEERING"}),
        "ENGINEERING": frozenset({"EAST_HALL", "REACTOR", "STORAGE"}),
        "LABS": frozenset({"MEDBAY"}),
        "MEDBAY": frozenset({"LABS", "WEST_HALL"}),
        "REACTOR": frozenset({"ENGINEERING"}),
        "STORAGE": frozenset({"ENGINEERING"}),
        "UPPER_HALL": frozenset({"ADMIN", "CAFETERIA"}),
        "WEST_HALL": frozenset({"ADMIN", "CAFETERIA", "MEDBAY"}),
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
    """Read candidate strength from typed detector output, with legacy fallback.

    Candidate producers assign the band from their semantic checks. Quoted
    description text cannot override it. Historical flags have no typed band
    and retain their recorded marker-based interpretation. Belief updates and
    public projections share this predicate.
    """

    if flag.evidence_band is not None:
        return flag.evidence_band == "weak"
    return WEAK_CONTRADICTION_MARKER_PREFIX in flag.description


# The event-id segment that identifies an alibi-claim event
# (:func:`_turn_claim_id` writes ``turn:{turn_id}:claim:{index}``;
# sightings get ``:obs:``). Kept beside the id writers so the lift-key
# parser below can never drift from the id format.
_CLAIM_EVENT_SEGMENT: Final[str] = ":claim:"

# Task 16.7: the event-id segment for a whereabouts self-placement indexed as a
# degenerate alibi (:func:`_turn_whereabouts_id`). A whereabouts lives on
# ``turn.observations`` but is an ALIBI-SIDE account, not a sighting, so it gets
# its own segment (never ``:obs:``, which would make :func:`contradiction_lift_key`
# fall back to the full event-id pair and let one roll-call answer contradicted by
# N sightings stack N deltas). Recognised as an account-side key beside
# ``:claim:`` so one whereabouts folds to at most one contradiction lift.
_WHEREABOUTS_EVENT_SEGMENT: Final[str] = ":whereabouts:"

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
    # Task 16.7: a whereabouts self-placement is an alibi-side account
    # (:data:`_WHEREABOUTS_EVENT_SEGMENT`), so it keys like a ``:claim:`` id --
    # one roll-call answer paired against N sightings shares its key and folds
    # to a single lift, the same per-account dedup a real alibi gets.
    claim_ids = [
        event_id
        for event_id in (flag.event_a_id, flag.event_b_id)
        if _CLAIM_EVENT_SEGMENT in event_id or _WHEREABOUTS_EVENT_SEGMENT in event_id
    ]
    if claim_ids:
        return "|".join(claim_ids)
    return f"{flag.event_a_id}|{flag.event_b_id}"


def self_refuted_alibi_claim_ids(transcript: MeetingTranscript) -> frozenset[str]:
    """Claim event ids of self-alibis refuted in their OWN turn (Task 14.10).

    The evidence-quality classification behind the belief fold's
    sloppy-testimony downgrade (audit 2026-07-01 §3a bound 2): a self-stated
    :class:`~meetings.schemas.AlibiClaim` (``turn.speaker == claim.subject``)
    whose SAME turn carries the speaker's own ``completed_task`` observation
    at a tick inside the alibi span (inclusive, the
    :class:`~meetings.schemas.AlibiClaim` range contract) but in a
    contradictory room is self-refuted testimony -- the speaker disproved
    their own account within one turn (the audited greedy-span defect;
    10.2% of baseline-1 self-alibis). Room comparison is the detector's:
    :func:`canonical_rooms` sets that are both non-empty and disjoint
    contradict; a non-spatial label is not comparable and refutes nothing.
    A ``completed_task`` observation carries no subject by schema -- it is
    definitionally the turn speaker's own task -- so the speaker-equals-
    subject guard is what makes the observation "the subject's OWN".

    Returns the ids in the :func:`_turn_claim_id` format
    (``turn:{turn_id}:claim:{index}``), i.e. the exact event ids a detector
    flag references and :func:`contradiction_lift_key` keys groups on --
    kept in this module beside the id writers so the formats can never
    drift (the :func:`is_weak_contradiction` precedent: fold-side
    classification lives next to what it classifies). Detector behavior is
    untouched: flags are still detected and recorded identically; only the
    Rule-2 WEIGHT read by
    :func:`agents.memory.beliefs.apply_contradiction_rule` consumes this.
    Pure and deterministic -- a function of the
    transcript alone, so the replay-side re-derivation folds the identical
    classification.

    The classification is a function of the ACCOUNT, never the copy: once
    a self-stated copy is refuted by its own turn's observation, EVERY
    restatement of that account -- same ``(subject, canonical rooms, tick
    range)``, the :func:`_dedupe_echo_alibis` echo key -- is marked,
    whichever speaker or turn stated it. The detector dedups echoes
    FIRST-statement-wins before pairing, so a flag may reference an
    earlier copy than the one stated beside the refuting observation (a
    subject re-asserting their alibi after an accusation, or a proxy
    stating it first -- the seed-24/seed-26 turn-order shapes); marking
    all copies keeps the fold's membership check turn-order-independent,
    the same bug class the detector's own echo handling guards against.
    """

    refuted_accounts: set[tuple[PlayerId, frozenset[str], int, int]] = set()
    for turn in transcript.turns:
        own_task_observations = [
            observation
            for observation in turn.observations
            if isinstance(observation, CompletedTaskObservation)
        ]
        if not own_task_observations:
            continue
        for claim in turn.claims:
            if not isinstance(claim, AlibiClaim) or claim.subject != turn.speaker:
                continue
            alibi_rooms = canonical_rooms(claim.room)
            if not alibi_rooms:
                continue
            for observation in own_task_observations:
                if not claim.from_tick <= observation.tick <= claim.to_tick:
                    continue
                observed_rooms = canonical_rooms(observation.room)
                if observed_rooms and not (observed_rooms & alibi_rooms):
                    refuted_accounts.add(
                        (
                            claim.subject,
                            alibi_rooms,
                            claim.from_tick,
                            claim.to_tick,
                        )
                    )
                    break
    if not refuted_accounts:
        return frozenset()
    return frozenset(
        _turn_claim_id(turn=turn, index=index)
        for turn in transcript.turns
        for index, claim in enumerate(turn.claims)
        if isinstance(claim, AlibiClaim)
        and (
            claim.subject,
            canonical_rooms(claim.room),
            claim.from_tick,
            claim.to_tick,
        )
        in refuted_accounts
    )


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
    include_kill_scene: bool = False,
    movement_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]]
    | None = None,
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

    ``include_kill_scene`` (Task 13.5.3, the witnessed-kill lever; default
    ``False`` -> byte-identical for every existing caller). When ``True`` the
    relevance gate's KILL-SCENE prong is dropped (the spawn-window prong still
    applies), so a sighting placing a player at the meeting's
    :func:`triggering_body_rooms` -- normally excluded because "presence at the
    scene must never EXONERATE" -- is RETAINED. The kill-scene path needs those
    recovered placements not to corroborate but to CONTRADICT a stated alibi
    that puts the accused elsewhere; :func:`_detect_alibi_vs_physical` partitions
    them back out by intersecting each placement's rooms with the body rooms.
    The returned mapping is therefore a SUPERSET of the default reconstruction
    (the same regular placements, plus the recovered kill-scene ones).

    ``movement_witness_records`` (default ``None`` -> byte-identical for every
    existing caller, the ``include_kill_scene`` shape). Supplied, the indexed
    sightings are routed through :func:`_apply_movement_claim_shape` before the
    placement loop, so this reconstruction reads the movement channel the way
    the rest of the meeting layer does: a spoken ``saw_move`` the speaker's own
    record confirms places its subject at the DESTINATION
    (:func:`sighting_placement`), and an origin-half ``saw_player`` the same
    record moved out of that room is re-read where it left them. Withheld, a
    ``saw_move`` places nobody -- which is what :func:`detect_contradictions`
    wants for its physical detector, and what the corroboration ledger's
    walkable-transit clause does not.

    ``whereabouts`` self-placements (Task 16.7). A spoken
    :class:`~meetings.schemas.WhereaboutsClaim` places its SPEAKER (the
    claim carries no subject -- the speaker is the subject by construction)
    in its canonical rooms at its tick, on the SPATIAL-label gate ONLY. It
    deliberately SKIPS the §6.3 relevance gate the sightings above pass: that
    gate drops spawn-window and kill-scene sightings as evidentially empty
    for EXCULPATION, but whether a self-placement EXISTS on the public record
    is a different question -- answering roll-call (even trivially, at spawn
    or in the body room) accounts for the speaker, so it must remove them
    from Task 16.8's absent set (the roster minus these keys). The placement
    is inert for the current contradiction consumer: a self-placement's
    ``speaker`` equals its placed player, so the 13.4 physical detector's
    independence filter (``placement.speaker != subject``) excludes it from
    contradicting-voice material exactly as it excludes a self-stated
    sighting.

    Returns ``{subject: placements}`` for every player with at least one
    relevant stated placement, the subjects sorted and each subject's
    placements sorted by :func:`_placement_sort_key`. Pure: the transcript
    is not mutated and the function has no side effects, so re-running it
    on the same transcript yields byte-identical paths -- the
    DESIGN.md §0 rule 1 replay invariant the downstream flags inherit.
    """

    effective_roster = _NO_ROSTER if roster is None else roster
    body_rooms = triggering_body_rooms(transcript, trigger_kind=trigger_kind)
    # Task 13.5.3: ``include_kill_scene`` drops ONLY the kill-scene prong by
    # passing an empty body-room set to the relevance gate (the spawn-window
    # prong still applies), so kill-scene placements are recovered.
    relevance_body_rooms = frozenset() if include_kill_scene else body_rooms

    spoken = tuple(_iter_sightings(transcript))
    entries = _placement_entries(
        transcript,
        spoken=spoken,
        movement_witness_records=movement_witness_records,
        roster=effective_roster,
    )

    paths: dict[PlayerId, list[StatedPlacement]] = {}
    for sighting, placed_players in entries:
        # A non-spatial label locates nobody (Task 10.1), and the §6.3
        # relevance gate drops the evidentially-empty spawn-window /
        # kill-scene sightings -- reused verbatim so the reconstruction
        # counts exactly the sightings the detectors trust.
        if not sighting.rooms:
            continue
        if not is_relevant_sighting(
            tick=sighting.observation.tick,
            rooms=sighting.rooms,
            triggering_body_rooms=relevance_body_rooms,
        ):
            continue
        placement = StatedPlacement(
            tick=sighting.observation.tick,
            rooms=sighting.rooms,
            speaker=sighting.speaker,
            event_id=sighting.event_id,
        )
        for player in placed_players:
            if not _subject_in_roster(player, effective_roster):
                continue
            paths.setdefault(player, []).append(placement)

    # Task 16.7: whereabouts self-placements -- the speaker placing THEMSELVES
    # on the public record. Gated on the SPATIAL label ONLY (a non-spatial
    # "VARIOUS" locates nobody), never the §6.3 RELEVANCE gate: that gate drops
    # spawn-window and kill-scene SIGHTINGS because they are evidentially empty
    # for EXCULPATION, but whether a self-placement EXISTS on the public record
    # is a different question -- a player who answers roll-call "I was in
    # CAFETERIA at tick 1" or in the body room HAS accounted for themselves and
    # must not read as absent (Task 16.8 derives the absent set as the roster
    # minus these keys). The placement stays inert for the current
    # contradiction consumer: :func:`_detect_alibi_vs_physical` reads only
    # placements with ``speaker != subject``, and a self-placement's speaker IS
    # its subject.
    for turn in transcript.turns:
        if not _subject_in_roster(turn.speaker, effective_roster):
            continue
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, WhereaboutsClaim):
                continue
            rooms = canonical_rooms(observation.room)
            if not rooms:
                continue
            paths.setdefault(turn.speaker, []).append(
                StatedPlacement(
                    tick=observation.tick,
                    rooms=rooms,
                    speaker=turn.speaker,
                    event_id=_turn_whereabouts_id(turn=turn, index=index),
                )
            )

    return {
        subject: tuple(sorted(placements, key=_placement_sort_key))
        for subject, placements in sorted(paths.items())
    }


def _placement_entries(
    transcript: MeetingTranscript,
    *,
    spoken: tuple[_IndexedSighting, ...],
    movement_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]] | None,
    roster: frozenset[PlayerId],
) -> tuple[tuple[_IndexedSighting, frozenset[PlayerId]], ...]:
    """Each sighting to place, paired with the players THAT reading places.

    Without ``movement_witness_records`` every sighting places its subject and
    every co-present player it lists -- one observation, one placement, the
    whole company.

    With them, the sightings are the movement-shaped ones
    (:func:`_apply_movement_claim_shape`) and the company splits. A RESOLUTION
    re-read says the SUBJECT was really at the destination the witness's own
    record left them in; it says nothing new about the people seen WITH them,
    who were where the witness said they were. Placing the company at the
    destination would invent a placement nobody spoke -- and, in the
    corroboration ledger, could hand an unrelated accused a walk on it. So a
    re-read places the subject alone, and the sighting AS SPOKEN keeps placing
    its co-present players -- MINUS the subject, whom the schema lets a speaker
    list among their own company
    (:class:`~meetings.schemas.SawPlayerObservation`). Left in, the subject
    would stand in the origin room and the destination at one tick, and a
    consumer reading the pair as two statements could certify a walk out of a
    room this speaker's own record says they had already left. Every other
    shaped sighting -- an untouched one, or a transition indexed as its
    destination arrival -- places its company as it always did.
    """

    if movement_witness_records is None:
        return tuple(
            (
                sighting,
                frozenset(
                    {sighting.observation.subject, *sighting.observation.co_present}
                ),
            )
            for sighting in spoken
        )
    by_id = {sighting.event_id: sighting for sighting in spoken}
    entries: list[tuple[_IndexedSighting, frozenset[PlayerId]]] = []
    for sighting in _apply_movement_claim_shape(
        transcript,
        sightings=spoken,
        move_witness_records=movement_witness_records,
        roster=roster,
    ):
        origin = by_id.get(sighting.event_id)
        if origin is not None and origin.rooms != sighting.rooms:
            entries.append((sighting, frozenset({sighting.observation.subject})))
            company = frozenset(origin.observation.co_present) - {
                sighting.observation.subject
            }
            if company:
                entries.append((origin, company))
            continue
        entries.append(
            (
                sighting,
                frozenset(
                    {sighting.observation.subject, *sighting.observation.co_present}
                ),
            )
        )
    return tuple(entries)


def absent_players(
    transcript: MeetingTranscript,
    *,
    roster: frozenset[PlayerId],
    trigger_kind: MeetingTriggerKind | None = None,
    include_vent_sightings: bool = False,
    vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]]
    | None = None,
) -> tuple[PlayerId, ...]:
    """The publicly UNPLACED living players -- Task 16.8's absent set.

    The complement of :func:`reconstruct_stated_paths` over the meeting's
    living roster: every roster player whom NOBODY'S public testimony -- a
    ``saw_player`` sighting (as subject or ``co_present``) or the player's
    own :class:`~meetings.schemas.WhereaboutsClaim` self-placement (Task
    16.7's roll-call answer) -- placed anywhere this meeting. Answering
    roll-call therefore removes a player from this set (the loop the 16.7
    docstrings promise), while staying publicly unseen keeps them in it:
    the set the Task 16.8 absence prior prices.

    Derived from the PUBLIC transcript ONLY, exactly as the reconstruction
    it complements: no engine state, no perception packet, and no private
    memory of others feeds it (the DESIGN.md §1.3 firewall -- this module
    stays engine-free, and a privately-witnessed sighting that nobody SPOKE
    leaves its subject absent by construction). The same gates apply too: a
    kill-scene or spawn-window sighting reconstructs no position (§6.3
    relevance), so it removes nobody, while a whereabouts self-placement
    needs only a spatial label (see the Task 16.7 asymmetry note on
    :func:`reconstruct_stated_paths`).

    ``roster`` is REQUIRED and must be the meeting's LIVING-participant set
    (the same set the manager passes to :func:`detect_contradictions`):
    the complement of a placement mapping is only meaningful against an
    explicit universe, and a living-only universe excludes dead players by
    construction (a dead player named in testimony is filtered out of the
    reconstruction AND absent from the roster, so it can never surface
    here). ``trigger_kind`` threads through to the reconstruction's
    relevance gate unchanged.

    ``include_vent_sightings`` (Task 17.5, the PR #264 vent-placement
    widening; default ``False`` -> byte-identical for every existing
    caller). The widening SHIPS since the Task-18.12 baseline-6 record (the
    17.7 HOLD was lifted by the 18.11 CREW-ONLY ruling C -- it travels with
    the vent package). Production applies it through the EQUIVALENT flag
    channel (:func:`grounded_vent_subjects_from_flags`, driven by the
    recorded/computed ``vent_sighting`` flags), which this docstring
    guarantees equals the record-driven set below; this ``vent_witness_records``
    signature is the record-driven form the tests pin. When ``True``, a GROUNDED vent
    sighting also places its subject: a spoken
    :class:`~meetings.schemas.SawVentObservation` matched against the
    SPEAKER'S OWN typed :class:`~meetings.schemas.VentWitnessRecord`
    channel (``vent_witness_records``, keyed by speaker id -- the 15.4
    chokepoint, :func:`_vent_observation_matches_record`, never a fresh
    text parse) removes its subject from the absent set. A witnessed vent
    is as much a public account of the subject as a ``saw_player`` row --
    the double-count the widening retires is a vent-flagged subject ALSO
    priced as absent -- but only the GROUNDED class may place: a spoken
    but ungrounded vent claim stays ordinary testimony and places nobody
    (speech alone never re-places a player), and ``None`` / an absent
    speaker entry grounds nothing, exactly as the flag detector treats
    legacy callers. Like the 16.7 whereabouts asymmetry, grounding is the
    ONLY gate -- the §6.3 relevance gate does not apply, because whether a
    grounded vent account EXISTS is a different question from whether it
    exculpates. The widening feeds ONLY this derivation:
    :func:`reconstruct_stated_paths` -- the alibi-contradiction substrate
    -- never learns vents, so every stated-path contradiction read is
    untouched.

    Returns a sorted tuple (replay-deterministic, like every fold in this
    module). Pure: the transcript is not mutated.
    """

    placed = reconstruct_stated_paths(
        transcript, roster=roster, trigger_kind=trigger_kind
    )
    unplaced = frozenset(player for player in roster if player not in placed)
    if include_vent_sightings and vent_witness_records is not None:
        unplaced -= _grounded_vent_subjects(
            transcript, vent_witness_records=vent_witness_records, roster=roster
        )
    return tuple(sorted(unplaced))


def grounded_vent_subjects_from_flags(
    contradictions: Sequence[ContradictionRef],
) -> frozenset[PlayerId]:
    """The vent-placement widening's subject set, read off the flag channel.

    The Task-18.12 production driver for the Task-17.5 absent-set widening (shipped
    with the vent package under the 18.11 CREW-ONLY ruling C). A GROUNDED vent
    sighting is recorded as a ``vent_sighting`` flag naming its subject, and
    :func:`_grounded_vent_subjects` (the record-driven form) is guaranteed to return
    exactly those same subjects (they share one grounding predicate --
    :func:`_vent_observation_matches_record`). So reading the widened set off the
    ``vent_sighting`` flags is byte-identical to the record-driven widening AND
    identical live vs replay: at record time the flags are freshly computed from the
    private records; at replay time they are read from the recorded bytes. Pure.
    """

    return frozenset(
        subject
        for flag in contradictions
        if flag.kind == "vent_sighting"
        for subject in flag.subjects
    )


def detect_contradictions(
    transcript: MeetingTranscript,
    *,
    roster: frozenset[PlayerId] | None = None,
    trigger_kind: MeetingTriggerKind | None = None,
    vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]]
    | None = None,
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]]
    | None = None,
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]] | None = None,
    evidence_reasoning_version: Literal[1, 2] | None = None,
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
    * ``alibi_vs_physical`` (Task 13.4, report-phase-b-plan B3/B4) -- the
      inferential kind: a subject's OWN stated alibi is physically contradicted
      by independent CO-PRESENCE placements of them (the subject named in another
      player's ``saw_player`` co-presence, via :func:`reconstruct_stated_paths`)
      in disjoint rooms at strictly interior ticks. STRONG only under the
      two-source conjunction -- the alibi is uncorroborated AND >=
      :data:`PHYSICAL_CONTRADICTION_MIN_VOICES` distinct non-adversarial
      co-presence voices contradict it; a LONE contradicting voice emits WEAK
      (informs, cannot eject alone). Direct sightings of the subject stay the
      9.7 weak ``alibi_vs_sighting`` band (:func:`_detect_alibi_vs_physical`).
      ``trigger_kind`` threads to the reconstruction's relevance gate so an
      EMERGENCY meeting drops the (possibly fabricated) opening body's kill-scene
      exclusion (Task 10.11), mirroring :func:`detect_corroborations`. Task
      13.5.3 (unconditional since Task 14.9 — the adopted lever is the default
      substrate) intensifies this kind at the KILL SCENE: a
      co-presence placing the accused at the body's room within the kill window
      (normally dropped by the relevance gate) is RECOVERED and made to
      CONTRADICT an alibi placed elsewhere, STRICT -- a lone kill-scene
      placement is sub-gate (:data:`WEAK_REASON_KILL_SCENE`) and crosses to
      STRONG only under the same two-source conjunction.
    * ``vent_sighting`` (Task 15.4) -- the role-proving kind: a spoken
      :class:`~meetings.schemas.SawVentObservation` GROUNDED against the
      speaker's own typed :class:`~meetings.schemas.VentWitnessRecord`
      channel (``vent_witness_records``, keyed by speaker id -- the live
      path threads each participant's
      ``vent_witness_records_for_meeting()`` output). Always STRONG (vents
      are impostor-only, so a grounded sighting proves the subject's role);
      an UNGROUNDED spoken vent claim -- no matching record in the
      speaker's own channel -- raises NO flag at all and stays ordinary
      testimony, so speech alone can never mint hard evidence. ``None`` /
      an absent speaker entry (legacy callers, replay re-derivation without
      the typed channel, non-witnesses) grounds nothing: committed
      transcripts re-derive byte-identically. The grounding comparison is
      deterministic (:data:`VENT_GROUNDING_TICK_TOLERANCE`); the flag is
      exempt from the 10.10 proxy-intra-turn guard by construction (it is
      one grounded observation, not one narrator's conflicting claim pair).

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

    The endpoint-band whereabouts exemption (audit-phase-18-planning.md §3.3): a
    DEGENERATE SINGLE-TICK SELF-ALIBI (a :class:`~meetings.schemas.WhereaboutsClaim`
    roll-call answer, or a genuine single-tick self-stated
    :class:`~meetings.schemas.AlibiClaim` -- the same class by construction)
    contradicted by a first-hand sighting mints a STRONG ``alibi_vs_sighting``
    flag instead of the endpoint-banded WEAK one, the single tick adjudicated
    as the claim's interior (:func:`_detect_alibi_vs_sightings`). Multi-tick
    endpoint semantics and the narrow-window band are untouched.

    The vent-placement variant (audit-phase-17-close.md §6 item 4): a spoken
    :class:`~meetings.schemas.SawVentObservation` GROUNDED against the
    speaker's own typed :class:`~meetings.schemas.VentWitnessRecord` (the 15.4
    chokepoint) whose RECORD contradicts the subject's OWN stated path mints a
    STRONG ``alibi_vs_physical`` flag beside the ``vent_sighting`` flag
    (:func:`_detect_vent_placement_contradictions`, joined after the 10.10
    proxy guard). Grounded-only is the firewall -- an ungrounded spoken vent
    claim mints nothing.

    Movement claims. ``move_witness_records`` is the per-speaker
    :class:`~meetings.schemas.MoveWitnessRecord` channel, keyed by speaker id
    exactly like ``vent_witness_records`` -- the live path threads each
    participant's ``move_witness_records_for_meeting()`` output. The indexed
    sightings pass one chokepoint before pairing
    (:func:`_apply_movement_claim_shape`): a spoken placement the SPEAKER's own
    record moved the subject OUT of at that exact tick is re-read at the
    record's ``to_room``, and a spoken
    :class:`~meetings.schemas.SawMoveObservation` joins as one destination
    placement. ``None`` / an absent speaker entry grounds nothing, so a
    record-free caller re-derives the pre-movement placements.

    Grounded prosecution. ``sighting_records`` is the per-speaker
    :class:`~meetings.schemas.SightingRecord` channel -- the SAME rows the
    grounded-vouch path reads (:func:`grounded_vouch_subjects`), keyed by
    speaker id exactly like the two channels above; the live path threads each
    participant's ``sighting_records_for_meeting()`` output. Its three
    rules apply only when this mapping is non-empty:
    a caller that supplies no records (the record-free re-derivers in ``eval/``
    and ``audits/workflows/``, legacy unit tests) keeps the pre-grounding rules by
    construction rather than reading every spoken sighting as fabricated. With
    records, an ``alibi_vs_sighting`` whose sighting side the speaker's own records do
    not support bands WEAK, one that fewer than
    :data:`meetings.constants.GROUNDED_PROSECUTION_MIN_SOURCES` distinct
    speakers stand behind -- grounded contradicting speakers plus the speakers
    behind any ``vent_sighting`` / ``alibi_vs_physical`` flag on the same
    subject, neither party to the dispute counting -- bands WEAK, and a
    degenerate single-tick self-placement loses the interior exemption above.
    Only descriptions move: ids, kinds, event pairs and subjects are stable, so
    every ballot citation and the detector's sort survive a demotion.

    Map-aware arbitration. No channel and no call-site wiring: the rule is a
    pure function of the transcript and the frozen
    :data:`CANONICAL_ROOM_NEIGHBORS` table. An ``alibi_vs_sighting`` whose two
    canonical room sets share a doorway and whose sighting sits within one tick
    of the alibi window's nearest edge carries
    :data:`WEAK_REASON_ADJACENT_ONE_TICK` -- one tick of walking reconciles both
    accounts, so a corridor informs but cannot convict. Two hops apart, or two
    or more ticks inside a claim of continuous presence, keeps the STRONG band.
    Like the rules above it re-bands only descriptions, so the flag set is
    unchanged.

    The function is pure: it does not mutate the transcript and has no
    side effects.
    """

    if evidence_reasoning_version is not None:
        transcript = _escape_untrusted_band_markers(transcript)

    # The three grounded-prosecution rules need the records to ground against:
    # a caller with no mapping keeps the pre-grounding rules, which is what makes
    # the record-free re-derivers safe.
    grounded_prosecution = bool(sighting_records)

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
    # ONE chokepoint, before the sightings reach any detector: the placements
    # every consumer below sees are the ones the witnesses meant.
    sightings = _apply_movement_claim_shape(
        transcript,
        sightings=sightings,
        move_witness_records=move_witness_records or {},
        roster=effective_roster,
    )

    accusation_pairs = _accusation_pairs(transcript)
    flags: list[ContradictionRef] = []
    flags.extend(
        _detect_alibi_conflicts(
            alibis,
            accusation_pairs=accusation_pairs,
            evidence_reasoning_version=evidence_reasoning_version,
        )
    )
    flags.extend(
        _detect_alibi_vs_sightings(
            alibis=alibis,
            sightings=sightings,
            subject_accounts=_subject_account_index(
                alibis=indexed_alibis, sightings=sightings
            ),
            grounded_prosecution=grounded_prosecution,
            evidence_reasoning_version=evidence_reasoning_version,
        )
    )
    # Task 13.4 (B3/B4): the inferential physical path.
    # ``reconstruct_stated_paths`` rebuilds each subject's stated room-by-tick
    # positions from the PUBLIC ``saw_player`` observations (incl. co-presence)
    # under the same roster + trigger kind, so :func:`_detect_alibi_vs_physical`
    # can find a subject's OWN alibi an independent speaker physically
    # contradicts. Three inputs gate it to evidence-grade co-presence:
    #   * ``self_alibis`` -- the subject's OWN alibis, de-echoed AMONG
    #     self-statements only, so a proxy/defender stating the same alibi first
    #     cannot let the global echo-dedup drop (and hide) the subject's own
    #     claim (the seed-24-style turn-order dependence, here on the physical
    #     path);
    #   * ``direct_sighting_events`` -- the event ids on which a player was the
    #     observation's OWN ``saw_player`` subject, so those (the 9.7 weak
    #     ``alibi_vs_sighting`` band) are excluded and only CO-PRESENCE
    #     placements feed the physical detector;
    #   * ``roster_sighting_events`` -- the event ids of roster-valid sightings
    #     (subject in roster), so a co-presence anchored on a HALLUCINATED
    #     primary subject (dropped from ``sightings`` but still placed by the
    #     reconstruction) never backs a physical flag.
    self_alibis = _dedupe_echo_alibis(
        tuple(a for a in indexed_alibis if a.speaker == a.claim.subject)
    )
    paths = reconstruct_stated_paths(
        transcript, roster=roster, trigger_kind=trigger_kind
    )
    # Task 13.5.3 (the witnessed-kill kill-scene intensification; unconditional
    # since Task 14.9 — the adopted lever is the default substrate). When the
    # meeting HAS a kill scene, a second reconstruction recovers the kill-scene
    # placements (the relevance gate normally drops them) so a co-presence at
    # the body's room can CONTRADICT an alibi placed elsewhere.
    kill_scene_paths: Mapping[PlayerId, tuple[StatedPlacement, ...]] | None = None
    body_rooms = triggering_body_rooms(transcript, trigger_kind=trigger_kind)
    if body_rooms:
        kill_scene_paths = reconstruct_stated_paths(
            transcript,
            roster=roster,
            trigger_kind=trigger_kind,
            include_kill_scene=True,
        )
    flags.extend(
        _detect_alibi_vs_physical(
            self_alibis=self_alibis,
            paths=paths,
            direct_sighting_events=_direct_sighting_events(sightings),
            roster_sighting_events=frozenset(s.event_id for s in sightings),
            accusation_pairs=accusation_pairs,
            kill_scene_paths=kill_scene_paths,
            body_rooms=body_rooms,
            evidence_reasoning_version=evidence_reasoning_version,
        )
    )
    event_speakers = _event_speaker_index(transcript)
    guarded = _apply_proxy_intra_turn_guard(flags, event_speakers=event_speakers)
    # Task 15.4: grounded vent flags join AFTER the proxy-intra-turn guard --
    # deliberately, not incidentally. Both of a vent flag's event ids resolve
    # to the one spoken observation (same speaker, subject a third party), so
    # the 10.10 guard would re-target it WEAK at the speaker; but that guard
    # exists for one narrator's two CONFLICTING proxy claims, while a grounded
    # vent flag is a single observation confirmed against the speaker's own
    # typed memory channel -- exactly the evidence the guard must not delete.
    if vent_witness_records:
        guarded.extend(
            _detect_grounded_vent_flags(
                transcript,
                vent_witness_records=vent_witness_records,
                roster=effective_roster,
                evidence_reasoning_version=evidence_reasoning_version,
            )
        )
        # The vent-placement variant joins AFTER the grounded vent flags -- and,
        # like them, after the 10.10 proxy-intra-turn guard. The join point is
        # deliberate (grounded evidence must never be re-targeted; structurally
        # the guard could not hit these flags anyway -- two distinct speakers:
        # the venter subject and the witness).
        guarded.extend(
            _detect_vent_placement_contradictions(
                transcript,
                self_alibis=self_alibis,
                vent_witness_records=vent_witness_records,
                roster=effective_roster,
                evidence_reasoning_version=evidence_reasoning_version,
            )
        )
    if grounded_prosecution:
        # LAST, so the physical-anchor set is complete: the vent flags above
        # are part of it, and a demotion must never be re-read by an earlier
        # pass as a fresh flag.
        guarded = _apply_grounded_prosecution(
            guarded,
            sightings=sightings,
            sighting_records=sighting_records or {},
            event_speakers=event_speakers,
        )
    if evidence_reasoning_version == 1 and any(
        flag.evidence_band is None for flag in guarded
    ):
        raise ValueError("candidate detector emitted a flag without typed strength")
    return tuple(sorted(guarded, key=lambda flag: flag.contradiction_id))


def _escape_untrusted_band_markers(transcript: MeetingTranscript) -> MeetingTranscript:
    """Quote marker-like room text before the detector appends its own markers.

    Only the detector's local copy changes. Transcript artifacts and their IDs
    stay intact; a room spelling cannot author an internal strength annotation.
    """

    turns: list[MeetingTurn] = []
    for turn in transcript.turns:
        observations = []
        for observation in turn.observations:
            update = {}
            for field in ("room", "from_room", "to_room"):
                value = getattr(observation, field, None)
                if isinstance(value, str) and WEAK_CONTRADICTION_MARKER_PREFIX in value:
                    update[field] = value.replace(
                        WEAK_CONTRADICTION_MARKER_PREFIX, "[quoted weak signal:"
                    )
            observations.append(observation.model_copy(update=update))
        claims = []
        for claim in turn.claims:
            if isinstance(claim, AlibiClaim):
                claim = claim.model_copy(
                    update={
                        "room": claim.room.replace(
                            WEAK_CONTRADICTION_MARKER_PREFIX, "[quoted weak signal:"
                        )
                    }
                )
            claims.append(claim)
        turns.append(
            turn.model_copy(
                update={"observations": tuple(observations), "claims": tuple(claims)}
            )
        )
    return transcript.model_copy(update={"turns": tuple(turns)})


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
    # Task 16.7: ``include_whereabouts=False`` -- a roll-call self-placement is
    # prosecutable (the contradiction path indexes it) but NEVER an ungrounded
    # exculpation surface. Pairing a WhereaboutsClaim with a confederate's
    # confirming sighting would corroborate the subject with no grounding
    # record behind either side, the anti-collusion hole the grounded-vouch
    # channel exists to close.
    alibis = tuple(
        indexed
        for indexed in _iter_alibis(transcript, include_whereabouts=False)
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

    Task 15.4: a :class:`~meetings.schemas.SawVentObservation` is
    relevance-grade WITHOUT the kill-scene prong -- that prong exists
    because "presence at the scene must never EXONERATE" (a vouch-side
    rule), while a witnessed vent is incrimination, and an impostor
    venting at the kill scene is exactly the shape the evidence must
    reach. The spawn-window prong still applies, matching every other
    observation kind.

    Task 16.7: a :class:`~meetings.schemas.WhereaboutsClaim` is NOT
    observation backing. A roll-call self-placement carries zero
    information about the ACCUSED -- it locates only the speaker -- so it
    cannot promote a bare verbal accusation into an observation-backed
    independent voice. Once roll-call is elicited (Task 16.15) every
    accuser answers it, so counting it as backing would make the
    testimony-spread gate always-pass and silently retire the
    bare-accusation exclusion; excluded HERE keeps the voice count keyed
    on genuine evidence about the subject.

    A :class:`~meetings.schemas.SawKillObservation` is excluded too, for a
    different reason: the shape is testimony CONTENT with no grounding channel
    behind it, so it mints no flag, no band and no suspicion delta anywhere.
    Backing a voice IS a suspicion delta -- it promotes a bare accusation into
    an independent one and lifts testimony spread -- and an ungrounded spoken
    kill is precisely the claim a fabricator would reach for. A witnessed vent
    is scored here because vents are impostor-only and the STRONG flag behind
    them is typed-record grounded; kills have no equivalent channel, and adding
    one is a separate change with its own entitlement question.
    """

    for observation in turn.observations:
        # A roll-call self-placement locates only the speaker (above), a
        # movement claim carries no single room to gate on (it participates
        # ONLY as the lever's grounded destination placement,
        # :func:`_iter_move_placements`), and a spoken kill is ungrounded
        # content that must move no suspicion. None backs an accusation here.
        if isinstance(
            observation,
            (
                WhereaboutsClaim,
                SawMoveObservation,
                SawKillObservation,
                TaskActivityAccount,
            ),
        ):
            continue
        rooms = canonical_rooms(observation.room)
        if not rooms:
            continue
        if isinstance(observation, SawVentObservation):
            if observation.tick > SPAWN_WINDOW_LAST_TICK:
                return True
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

    ``movement_grounded`` marks a placement :func:`_apply_movement_claim_shape`
    produced from the speaker's own :class:`~meetings.schemas.MoveWitnessRecord`
    -- either arm. Such a placement is grounded in a channel DISJOINT from the
    ``saw_player`` records the grounded-prosecution lever checks (a witness who
    saw a departure holds no sighting record at the destination), so the lever
    reads it as grounded rather than as unsupported speech.
    """

    event_id: str
    speaker: PlayerId
    observation: SawPlayerObservation
    rooms: frozenset[str]
    movement_grounded: bool = False


def _iter_alibis(
    transcript: MeetingTranscript, *, include_whereabouts: bool = True
) -> Iterator[_IndexedAlibi]:
    """Yield every location account: alibi claims + whereabouts self-placements.

    A spoken :class:`~meetings.schemas.WhereaboutsClaim` ("I was
    in ``room`` at ``tick``") is indexed as a DEGENERATE SINGLE-TICK
    SELF-ALIBI (subject = the speaker, ``from_tick == to_tick == tick``) so
    the CONTRADICTION consumers of the alibi indexing -- the conflict /
    sighting / physical detectors, the subject-account proxy check, the echo
    dedup -- prosecute a lying self-placement with the alibi rules they
    already have, no new flag kind and no duplicated chronology discipline (a
    single tick satisfies the :class:`~meetings.schemas.AlibiClaim` range
    validator by construction). The synthesized claim uses the distinct
    whereabouts id (:func:`_turn_whereabouts_id`), preserving its role as a
    self-placement account while resolving through :func:`_event_speaker_index`
    and the spectator surface. Per turn, claims index before observations -- a fixed
    order, so the echo dedup's first-statement-wins is deterministic.

    ``include_whereabouts=False`` (the :func:`detect_corroborations` caller)
    yields ONLY genuine :class:`~meetings.schemas.AlibiClaim` accounts. A
    roll-call self-placement is deliberately PROSECUTABLE but never
    EXCULPATORY: pairing it with another speaker's confirming sighting would
    mint a detector-derived corroboration with NO grounding record behind it,
    so two colluders (one answering roll-call, one confirming it with a
    fabricated sighting) could earn the subject a -0.05 that the
    anti-collusion floor forbids. Exculpation for a self-placement's
    companions must travel the GROUNDED-vouch channel
    (:func:`grounded_vouch_subjects`), which checks the speaker's OWN typed
    record; the contradiction channel (default ``True``) needs no such
    check because a flag INCRIMINATES -- fabricating one only exposes the
    liar.
    """

    for turn in transcript.turns:
        for index, claim in enumerate(turn.claims):
            if isinstance(claim, AlibiClaim):
                yield _IndexedAlibi(
                    event_id=_turn_claim_id(turn=turn, index=index),
                    speaker=turn.speaker,
                    claim=claim,
                    rooms=canonical_rooms(claim.room),
                )
        if not include_whereabouts:
            continue
        for index, observation in enumerate(turn.observations):
            if isinstance(observation, WhereaboutsClaim):
                yield _IndexedAlibi(
                    event_id=_turn_whereabouts_id(turn=turn, index=index),
                    speaker=turn.speaker,
                    claim=AlibiClaim(
                        type="alibi",
                        subject=turn.speaker,
                        from_tick=observation.tick,
                        to_tick=observation.tick,
                        room=observation.room,
                    ),
                    rooms=canonical_rooms(observation.room),
                )


def _iter_sightings(transcript: MeetingTranscript) -> Iterator[_IndexedSighting]:
    for turn in transcript.turns:
        for index, observation in enumerate(turn.observations):
            if isinstance(observation, SawPlayerObservation):
                yield _IndexedSighting(
                    event_id=turn_observation_id(turn=turn, index=index),
                    speaker=turn.speaker,
                    observation=observation,
                    rooms=canonical_rooms(observation.room),
                )


def _apply_movement_claim_shape(
    transcript: MeetingTranscript,
    *,
    sightings: tuple[_IndexedSighting, ...],
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]],
    roster: frozenset[PlayerId],
) -> tuple[_IndexedSighting, ...]:
    """Read every spoken placement as the room the witness's own record left them in.

    The movement channel's one chokepoint,
    applied to the indexed sightings before any detector sees them, so the
    contradiction path, the subject-account index and the direct-sighting
    exclusion set all read ONE set of placements -- and, through
    :func:`reconstruct_stated_paths`'s ``movement_witness_records`` keyword, the
    corroboration ledger's walkable-transit clause too. Two arms:

    * **resolution** -- a spoken ``saw_player`` whose SPEAKER's own
      :class:`~meetings.schemas.MoveWitnessRecord` moved the subject OUT of that
      room at that exact tick is re-read at the record's ``to_room``
      (:func:`_resolve_movement_sighting`);
    * **shape** -- a spoken :class:`~meetings.schemas.SawMoveObservation` the
      speaker's own records confirm joins as ONE destination placement
      (:func:`_iter_move_placements`).

    A speaker with no records grounds nothing, so their testimony is untouched.
    The resolution rewrites only the room: the event id, the speaker and the
    tick are preserved, which is what keeps every id-keyed surface downstream --
    the direct-sighting exclusion set, the proxy-intra-turn guard,
    :func:`reconstruct_stated_paths`, the absent-set derivation -- unable to
    notice the rewrite.
    """

    resolved = tuple(
        _resolve_movement_sighting(
            sighting, records=move_witness_records.get(sighting.speaker, ())
        )
        for sighting in sightings
    )
    return resolved + tuple(
        _iter_move_placements(
            transcript, move_witness_records=move_witness_records, roster=roster
        )
    )


def _resolve_movement_sighting(
    sighting: _IndexedSighting, *, records: tuple[MoveWitnessRecord, ...]
) -> _IndexedSighting:
    """Re-index one spoken placement at its destination, or return it untouched."""

    destination = _movement_destination(
        subject=sighting.observation.subject,
        tick=sighting.observation.tick,
        spoken_rooms=sighting.rooms,
        records=records,
    )
    if destination is None:
        return sighting
    return _IndexedSighting(
        event_id=sighting.event_id,
        speaker=sighting.speaker,
        observation=sighting.observation.model_copy(update={"room": destination}),
        rooms=canonical_rooms(destination),
        movement_grounded=True,
    )


def _movement_destination(
    *,
    subject: PlayerId,
    tick: int,
    spoken_rooms: frozenset[str],
    records: tuple[MoveWitnessRecord, ...],
) -> RoomId | None:
    """The room a spoken placement re-reads as, or ``None`` to leave it alone.

    The stated conjunction, and only it: one of the speaker's records names this
    ``subject``, its tick EQUALS the spoken tick
    (:data:`MOVE_GROUNDING_TICK_TOLERANCE`), its ``from_room`` canonically
    intersects the spoken room and its ``to_room`` is canonically disjoint from
    it. Disjointness is what confines the rewrite to the origin half: a
    placement already naming the destination intersects ``to_room`` and is left
    exactly as spoken.

    Ambiguity is adjudicated BEFORE the conjunction, over every record naming
    this subject at this tick: if any two disagree about the destination the
    placement is left untouched, whatever room they came from. Engine truth
    forbids a subject having two transitions land on one tick, so such a channel
    is not describing the transition the speaker meant; narrowing to the record
    whose origin happens to match the spoken room would pick a destination out
    of a channel already known to be wrong.
    """

    if not spoken_rooms:
        return None
    at_tick = _records_at_tick(records, subject=subject, tick=tick)
    if _destinations_conflict(at_tick):
        return None
    destinations: dict[frozenset[str], RoomId] = {}
    for record in at_tick:
        if not (canonical_rooms(record.from_room) & spoken_rooms):
            continue
        to_rooms = canonical_rooms(record.to_room)
        if not to_rooms or (to_rooms & spoken_rooms):
            continue
        destinations.setdefault(to_rooms, record.to_room)
    if len(destinations) != 1:
        return None
    return next(iter(destinations.values()))


def _records_at_tick(
    records: tuple[MoveWitnessRecord, ...], *, subject: PlayerId, tick: int
) -> tuple[MoveWitnessRecord, ...]:
    """The speaker's records naming ``subject`` at ``tick``."""

    return tuple(
        record
        for record in records
        if record.subject == subject
        and abs(record.tick - tick) <= MOVE_GROUNDING_TICK_TOLERANCE
    )


def _destinations_conflict(records: tuple[MoveWitnessRecord, ...]) -> bool:
    """Whether these records disagree about where the subject landed.

    Engine truth forbids two transitions of one subject landing on one tick, so
    a channel that says otherwise is wrong about something and neither arm may
    take a destination from it. Both arms consult this BEFORE matching, so an
    invalid channel cannot resolve through whichever record happens to fit the
    spoken rooms.
    """

    return len({canonical_rooms(record.to_room) for record in records}) > 1


def move_observation_matches_record(
    observation: SawMoveObservation,
    record: MoveWitnessRecord,
) -> bool:
    """Whether one spoken transition matches one typed record.

    The vent / sighting grounding predicates' movement sibling: same
    ``subject``, canonically intersecting rooms on BOTH halves of the
    transition, and an EXACT tick match
    (:data:`MOVE_GROUNDING_TICK_TOLERANCE`). Pure function of its two
    arguments -- no prose parsing, no LLM judgment.
    """

    if observation.subject != record.subject:
        return False
    if abs(observation.tick - record.tick) > MOVE_GROUNDING_TICK_TOLERANCE:
        return False
    spoken_from = canonical_rooms(observation.from_room)
    spoken_to = canonical_rooms(observation.to_room)
    if not spoken_from or not spoken_to:
        return False
    return bool(
        canonical_rooms(record.from_room) & spoken_from
        and canonical_rooms(record.to_room) & spoken_to
    )


def sighting_placement(artifact: object) -> SawPlayerObservation | None:
    """The placement one spoken artifact puts on the record, or ``None``.

    Two sayable shapes place another player, and every first-hand-sighting
    predicate must read the pair as one placement:

    * a :class:`~meetings.schemas.SawPlayerObservation` places its subject in
      the room it names;
    * a :class:`~meetings.schemas.SawMoveObservation` "``subject`` moved A -> B,
      arriving at ``tick``" places the subject at the DESTINATION, ``to_room``
      at ``tick``, and nowhere else — the origin half is deliberately not placed
      at ``tick - 1``.

    Every other observation shape places nobody: a whereabouts locates only the
    speaker, a vent sighting is a first-hand sighting but names no room the
    subject can be placed in for a geometry compare, and a found-body names a
    dead victim.

    This is the same :class:`~meetings.schemas.SawPlayerObservation`
    :func:`_iter_move_placements` builds from a grounded transition, so an
    instrument reading it agrees with the detector by construction rather than
    by a re-derivation that can drift.
    """

    if isinstance(artifact, SawPlayerObservation):
        return artifact
    if isinstance(artifact, SawMoveObservation):
        return SawPlayerObservation(
            type="saw_player",
            tick=artifact.tick,
            subject=artifact.subject,
            room=artifact.to_room,
        )
    return None


def _iter_move_placements(
    transcript: MeetingTranscript,
    *,
    move_witness_records: Mapping[PlayerId, tuple[MoveWitnessRecord, ...]],
    roster: frozenset[PlayerId],
) -> Iterator[_IndexedSighting]:
    """Index each GROUNDED spoken transition as its ONE destination placement.

    "``subject`` in ``to_room`` at ``tick``" -- the arrival the transition
    asserts, carried on the observation's own event id so it resolves to its
    speaker exactly like any other observation. The origin half is deliberately
    not placed at ``tick - 1``; see
    :class:`~meetings.schemas.SawMoveObservation`. An UNGROUNDED transition (no
    matching record in the speaker's own channel) is ordinary testimony and
    places nobody, and a channel whose records disagree about the destination
    (:func:`_destinations_conflict`) grounds nothing here either -- the same
    adjudication the resolution arm applies, so one invalid channel cannot be
    trusted by one arm and distrusted by the other.
    """

    for turn in transcript.turns:
        records = move_witness_records.get(turn.speaker, ())
        if not records:
            continue
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawMoveObservation):
                continue
            if not _subject_in_roster(observation.subject, roster):
                continue
            at_tick = _records_at_tick(
                records, subject=observation.subject, tick=observation.tick
            )
            if _destinations_conflict(at_tick):
                continue
            if not any(
                move_observation_matches_record(observation, record)
                for record in at_tick
            ):
                continue
            yield _IndexedSighting(
                event_id=turn_observation_id(turn=turn, index=index),
                speaker=turn.speaker,
                observation=SawPlayerObservation(
                    type="saw_player",
                    tick=observation.tick,
                    subject=observation.subject,
                    room=observation.to_room,
                ),
                rooms=canonical_rooms(observation.to_room),
                movement_grounded=True,
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
    evidence_reasoning_version: Literal[1, 2] | None = None,
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
            # Task 13.3 (B2): the genuinely-INDEPENDENT cross-speaker conflict
            # -- two distinct non-subject speakers, none of the four
            # :func:`_conflict_weak_reasons` guards firing -- yields empty
            # ``weak_reasons``, so :func:`_describe_alibi_conflict` appends no
            # weak marker and the flag is STRONG (the one inferential STRONG
            # class). When a guard fires (self-pair / adversarial / narrow /
            # boundary) the marker is appended and the flag stays weak; the
            # guards are byte-identical to keep the impostor from gaming the
            # adversarial counter-alibi.
            yield _build_contradiction(
                kind="alibi_conflict",
                event_a_id=left.event_id,
                event_b_id=right.event_id,
                subjects=(left.claim.subject,),
                description=_describe_alibi_conflict(
                    left.claim,
                    right.claim,
                    weak_reasons=_conflict_weak_reasons(
                        left,
                        right,
                        accusation_pairs=accusation_pairs,
                        evidence_reasoning_version=evidence_reasoning_version,
                    ),
                ),
                evidence_band=(
                    "weak"
                    if _conflict_weak_reasons(
                        left,
                        right,
                        accusation_pairs=accusation_pairs,
                        evidence_reasoning_version=evidence_reasoning_version,
                    )
                    else "strong"
                )
                if evidence_reasoning_version == 1
                else None,
            )


def _detect_alibi_vs_sightings(
    *,
    alibis: tuple[_IndexedAlibi, ...],
    sightings: tuple[_IndexedSighting, ...],
    subject_accounts: Mapping[PlayerId, tuple[_SubjectAccount, ...]],
    grounded_prosecution: bool = False,
    evidence_reasoning_version: Literal[1, 2] | None = None,
) -> Iterator[ContradictionRef]:
    for alibi in alibis:
        if not alibi.rooms:
            continue
        # The endpoint-band whereabouts exemption. A DEGENERATE SINGLE-TICK
        # SELF-ALIBI -- ``from_tick == to_tick`` AND the speaker is its own
        # subject -- is exactly how a
        # :class:`~meetings.schemas.WhereaboutsClaim` roll-call answer indexes
        # per :func:`_iter_alibis` (and how a genuine single-tick self-stated
        # :class:`~meetings.schemas.AlibiClaim` reads too -- the same class by
        # construction, exempted identically). The exemption adjudicates
        # the single tick as the claim's INTERIOR, not its edge: a contradicting
        # first-hand sighting mints a STRONG flag. For this class the only weak
        # reason ``base_reasons`` could ever carry is WEAK_REASON_NARROW_WINDOW
        # (``to - from == 0 < NARROW_ALIBI_WINDOW_TICKS``), whose transit-fuzz
        # rationale does not apply to an adjudicated interior tick, so
        # ``base_reasons`` is emptied and the endpoint-tick append below is
        # skipped. Proxy alibis (speaker != subject) never satisfy the class, so
        # the re-targeted-proxy path is structurally untouched; multi-tick
        # alibis keep the endpoint band and narrow-window band verbatim.
        #
        # ``grounded_prosecution`` -- true exactly when the caller handed
        # :func:`detect_contradictions` per-speaker sighting records -- WITHDRAWS
        # the exemption: with records to ground against, the degenerate
        # single-tick self-placement takes the narrow-window / endpoint band
        # instead of being adjudicated as its own interior. A record-free caller
        # keeps the exemption, so both branches are live.
        interior_exempt = not grounded_prosecution and (
            alibi.claim.from_tick == alibi.claim.to_tick
            and alibi.speaker == alibi.claim.subject
        )
        # Task 13.14: the sighting path no longer down-weights a self-stated
        # alibi (the owner LONE-STRONG reversal of audit-9.7) -- a self-stated
        # alibi contradicted by a third party's sighting now classifies STRONG.
        # The narrow-window guard (and the endpoint-tick guard appended below)
        # STAY weak, EXCEPT for the 18.9-exempt interior class above.
        base_reasons = (
            ()
            if interior_exempt
            else _weak_signal_reasons(alibi, include_self_stated=False)
        )
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
                    evidence_band=("weak") if evidence_reasoning_version == 1 else None,
                )
                continue
            weak_reasons = base_reasons
            # Endpoint-tick weak band (Task 10.1, audit gp-2 C-C-1): a
            # sighting exactly on the window's edge tick is movement fuzz
            # -- weak-banded rather than excluded, because an endpoint
            # mismatch can still be a real signal once corroborated. Task
            # 18.9: skipped for the interior-exempt single-tick self-alibi
            # class -- its one tick IS the claim's interior, not an edge.
            if not interior_exempt and sighting.observation.tick in (
                alibi.claim.from_tick,
                alibi.claim.to_tick,
            ):
                weak_reasons = (*base_reasons, WEAK_REASON_ENDPOINT_TICK)
            # Map-aware arbitration: two rooms that share a doorway, and a
            # sighting close enough to the window's edge that one tick of walking
            # covers the difference, are two honest accounts of one transit. The
            # reason joins the endpoint band LAST so a flag that already carries
            # one keeps its existing marker text and gains this in a fixed,
            # byte-stable position.
            if _adjacent_within_one_tick(alibi=alibi, sighting=sighting):
                weak_reasons = (*weak_reasons, WEAK_REASON_ADJACENT_ONE_TICK)
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
                evidence_band=("weak" if weak_reasons else "strong")
                if evidence_reasoning_version == 1
                else None,
            )


def room_hops(
    origin: frozenset[str], destination: frozenset[str], *, max_hops: int
) -> int | None:
    """Fewest doorway hops from ``origin`` to ``destination``, or ``None``.

    A bounded breadth-first walk over :data:`CANONICAL_ROOM_NEIGHBORS`, room SET
    to room SET (a compound label like ``"LABS/MEDBAY"`` canonicalises to more
    than one room, and the subject claims to have been at each). Returns 0 when
    the two sets intersect, and ``None`` when nothing in ``destination`` is
    reachable within ``max_hops`` -- including when either side is non-spatial.
    """

    if not origin or not destination:
        return None
    if origin & destination:
        return 0
    reached = set(origin)
    frontier = set(origin)
    for hops in range(1, max_hops + 1):
        frontier = {
            neighbor
            for room in frontier
            for neighbor in CANONICAL_ROOM_NEIGHBORS.get(room, frozenset())
        } - reached
        if not frontier:
            return None
        if frontier & destination:
            return hops
        reached |= frontier
    return None


def _adjacent_within_one_tick(
    *, alibi: _IndexedAlibi, sighting: _IndexedSighting
) -> bool:
    """Whether walking reconciles this alibi/sighting pair (Phase 20 R1).

    True when the two canonical room sets sit within
    :data:`~meetings.constants.MAP_ARBITRATION_MAX_HOPS` doorway hops of each
    other AND the sighting tick sits within
    :data:`~meetings.constants.MAP_ARBITRATION_MAX_TICK_GAP` of the nearest edge
    of the alibi window. The gap is measured to the window's ENDPOINTS, not to
    the window as a whole: the caller only reaches here for a sighting already
    INSIDE the window, and a sighting buried deeper than that names an interior
    tick of a claim of continuous presence, which no single hop reconciles.
    """

    hops = room_hops(alibi.rooms, sighting.rooms, max_hops=MAP_ARBITRATION_MAX_HOPS)
    if hops is None or hops == 0:
        return False
    gap = min(
        sighting.observation.tick - alibi.claim.from_tick,
        alibi.claim.to_tick - sighting.observation.tick,
    )
    return gap <= MAP_ARBITRATION_MAX_TICK_GAP


def _direct_sighting_events(
    sightings: tuple[_IndexedSighting, ...],
) -> Mapping[PlayerId, frozenset[str]]:
    """Per subject, the ``saw_player`` event ids that name them DIRECTLY.

    A ``saw_player`` observation places its ``subject`` (a DIRECT sighting) and
    each ``co_present`` player (a co-presence mention) at the same room/tick,
    all sharing one ``event_id`` in :func:`reconstruct_stated_paths`. This index
    records, per player, the event ids on which they were the observation's OWN
    ``subject`` -- so :func:`_detect_alibi_vs_physical` can keep those (the 9.7
    weak ``alibi_vs_sighting`` material) out of the physical detector and read
    only the CO-PRESENCE placements (``event_id`` absent here) that the
    alibi-vs-sighting path structurally cannot reach.
    """

    direct: dict[PlayerId, set[str]] = {}
    for sighting in sightings:
        direct.setdefault(sighting.observation.subject, set()).add(sighting.event_id)
    return {subject: frozenset(events) for subject, events in direct.items()}


def _detect_alibi_vs_physical(
    *,
    self_alibis: tuple[_IndexedAlibi, ...],
    paths: Mapping[PlayerId, tuple[StatedPlacement, ...]],
    direct_sighting_events: Mapping[PlayerId, frozenset[str]],
    roster_sighting_events: frozenset[str],
    accusation_pairs: frozenset[tuple[PlayerId, PlayerId]],
    kill_scene_paths: Mapping[PlayerId, tuple[StatedPlacement, ...]] | None = None,
    body_rooms: frozenset[str] = frozenset(),
    evidence_reasoning_version: Literal[1, 2] | None = None,
) -> Iterator[ContradictionRef]:
    """The Task 13.4 inferential ``alibi_vs_physical`` flags (B3/B4).

    Task 13.5.3 (the witnessed-kill kill-scene intensification; unconditional
    since Task 14.9). ``kill_scene_paths`` (the
    kill-scene-inclusive reconstruction; ``None`` -> byte-identical 13.4 path)
    ADDS kill-scene contradicting placements -- co-presences at the meeting's
    ``body_rooms`` that the relevance gate normally DROPS. They never enter the
    CORROBORATION check (which keeps reading the relevance-gated ``paths`` only),
    so the §6.3 invariant holds: presence at the scene must never EXONERATE -- a
    recovered scene placement can only CONTRADICT. A kill-scene placement that is
    the LONE contradicting voice carries :data:`WEAK_REASON_KILL_SCENE`
    (sub-gate, owner-LOCKED STRICT: a single forgeable kill-accusation INFORMS
    but cannot eject), and it crosses to STRONG only under the SAME two-source
    conjunction (>= :data:`PHYSICAL_CONTRADICTION_MIN_VOICES` distinct
    contradicting voices, kill-scene or not -- "another placement, or the
    body+placement two-source conjunction"). ``body_rooms`` empty (the default /
    an emergency meeting with no body) -> no scene placements, so the result is
    the 13.4 set exactly.

    The R7 lever. ``self_alibis`` is the caller's de-echoed set of the subjects'
    OWN alibis (``speaker == subject`` already); for each (room set A over an
    inclusive window) the reconstructed stated path
    (:func:`reconstruct_stated_paths`) is scanned for CO-PRESENCE placements
    that physically contradict it: an independent speaker who, sighting a THIRD
    player, named the subject as ``co_present`` in a room DISJOINT from A at a
    STRICTLY INTERIOR tick of the window.

    Why co-presence ONLY (not a direct ``saw_player(subject)``): a self-stated
    alibi contradicted by a direct sighting of the subject is the audited seed-3
    shape (8/13 wrong ejections were the body reporter railroaded by ONE coarse
    sighting of their own alibi) -- that material stays the 9.7 weak
    ``alibi_vs_sighting`` band, untouched. A co-presence placement is the genuine
    NET-NEW inferential signal the alibi-vs-sighting path (which only reads a
    sighting's OWN ``subject``) structurally cannot reach: a witness placing the
    subject alongside someone else, somewhere the subject's claim says they were
    not. Endpoints are excluded (transit fuzz) and spawn-window / kill-scene
    placements are already dropped by the reconstruction's relevance gate, so
    every placement here is evidence-grade and traces to one public
    ``saw_player`` (its ``event_id``) -- the 13.4 firewall assertion.

    Banding (the crux's role-gate). A CORROBORATED alibi -- some independent
    voice places the subject INSIDE A within the window -- is co-placement
    agreement (the shape the ceiling probe found 28 crewmate-subjects share) and
    mints NOTHING, so the detector keys on the subject's own CONTRADICTED alibi,
    not on two-source coverage. Otherwise each contradicting placement emits a
    flag whose band is the distinct contradicting-voice count:

    * **>= :data:`PHYSICAL_CONTRADICTION_MIN_VOICES` voices** -> STRONG (no weak
      marker): the contradiction is attested by independent (non-self,
      non-adversarial) speakers, so one mistaken co-presence cannot mint it;
    * **exactly one voice** -> WEAK (:data:`WEAK_REASON_LONE_PHYSICAL`): a single
      inferential atom informs but cannot eject alone.

    Two soundness gates beyond co-presence: a placement must trace to a
    ROSTER-VALID sighting (``roster_sighting_events`` -- its source observation's
    OWN subject is in the roster, so a co-presence anchored on a hallucinated
    player never backs a flag), and direct ``saw_player(subject)`` placements
    (``direct_sighting_events`` -- the 9.7 weak ``alibi_vs_sighting`` band) are
    excluded so only genuine co-presence feeds the detector. Endpoints are
    excluded (transit fuzz); spawn-window / kill-scene placements are already
    dropped by the reconstruction's relevance gate.

    One flag is emitted per qualifying contradicting placement (each is its own
    public ``saw_player``, so belief Rule 2 folds them on the shared alibi-claim
    lift key); the alibi is reported once via ``subjects=(subject,)``. Pure and
    deterministic: ``self_alibis`` is walked in transcript order and each
    subject's ``paths`` are pre-sorted, so flags emit in a stable order
    (``detect_contradictions`` re-sorts by ``contradiction_id`` regardless).
    """

    for alibi in self_alibis:
        subject = alibi.claim.subject
        # ``self_alibis`` is already self-stated (the caller filters), so only a
        # non-spatial alibi (locating nobody) is skipped here.
        if not alibi.rooms:
            continue
        from_tick = alibi.claim.from_tick
        to_tick = alibi.claim.to_tick
        direct_events = direct_sighting_events.get(subject, frozenset())
        # Independent (non-self) placements of the subject inside the alibi
        # window, from the RELEVANCE-GATED ``paths`` (kill-scene placements
        # excluded). ``reconstruct_stated_paths`` already relevance-gated them.
        independent = tuple(
            placement
            for placement in paths.get(subject, ())
            if placement.speaker != subject and from_tick <= placement.tick <= to_tick
        )
        # Corroboration = ANY independent voice places the subject INSIDE the
        # alibi's rooms within the window. A corroborated alibi is co-placement
        # agreement (the crewmate shape), never a clean lie -- suppress it. This
        # reads ONLY the relevance-gated ``independent`` (kill-scene placements
        # NEVER enter here), so the §6.3 invariant holds even with the 13.5.3
        # lever ON: presence at the scene must never EXONERATE -- a kill-scene
        # placement can CONTRADICT below, never corroborate.
        if any(placement.rooms & alibi.rooms for placement in independent):
            continue
        # Contradicting placements: a roster-valid CO-PRESENCE (event id is a
        # roster sighting but NOT a direct sighting of the subject) in a DISJOINT
        # room at a strictly INTERIOR tick, stated by an independent voice NOT
        # across the accusation chain from the subject (the 13.3 adversarial
        # guard -- an accuser's counter-placement must not manufacture a flag).
        contradicting = tuple(
            placement
            for placement in independent
            if placement.event_id in roster_sighting_events
            and placement.event_id not in direct_events
            and from_tick < placement.tick < to_tick
            and not (placement.rooms & alibi.rooms)
            and (placement.speaker, subject) not in accusation_pairs
            and (subject, placement.speaker) not in accusation_pairs
        )
        # Task 13.5.3: kill-scene contradicting placements -- co-presences at the
        # body's room (``body_rooms``) the relevance gate normally DROPS, recovered
        # via ``kill_scene_paths`` (the kill-scene-inclusive reconstruction; the
        # 13.5.3 lever is unconditional since Task 14.9, so a kill-scene meeting
        # always supplies it). Same soundness filters as the regular set, plus
        # ``placement.rooms & body_rooms`` (it IS the scene) and disjoint-from-alibi
        # (the accused claimed elsewhere). The body-room filter makes this set
        # DISJOINT from ``contradicting`` above (which excludes scene placements by
        # the relevance gate), so the union never double-counts a placement. Empty
        # when the meeting has no kill scene -> byte-identical to the 13.4 path.
        kill_scene_contradicting: tuple[StatedPlacement, ...] = ()
        if kill_scene_paths is not None and body_rooms:
            kill_scene_contradicting = tuple(
                placement
                for placement in kill_scene_paths.get(subject, ())
                if placement.speaker != subject
                and from_tick < placement.tick < to_tick
                and bool(placement.rooms & body_rooms)
                and not (placement.rooms & alibi.rooms)
                and placement.event_id in roster_sighting_events
                and placement.event_id not in direct_events
                and (placement.speaker, subject) not in accusation_pairs
                and (subject, placement.speaker) not in accusation_pairs
            )
        contradicting = contradicting + kill_scene_contradicting
        n_voices = len({placement.speaker for placement in contradicting})
        if n_voices == 0:
            continue
        # The two-source conjunction is STRONG; a lone voice is WEAK (informs,
        # cannot eject alone) -- the phase-B "single inferential atom" band. A
        # lone KILL-SCENE atom (Task 13.5.3, ``body_rooms`` non-empty) carries
        # the distinct kill-scene marker but is read identically by
        # :func:`is_weak_contradiction`; ``body_rooms`` empty -> the marker can
        # never apply, so the banding is byte-identical to the 13.4 path.
        strong = n_voices >= PHYSICAL_CONTRADICTION_MIN_VOICES
        weak_reasons: tuple[str, ...]
        for placement in contradicting:
            is_kill_scene = bool(placement.rooms & body_rooms)
            if strong:
                weak_reasons = ()
            elif is_kill_scene:
                weak_reasons = (WEAK_REASON_KILL_SCENE,)
            else:
                weak_reasons = (WEAK_REASON_LONE_PHYSICAL,)
            yield _build_contradiction(
                kind="alibi_vs_physical",
                event_a_id=alibi.event_id,
                event_b_id=placement.event_id,
                subjects=(subject,),
                description=_describe_alibi_vs_physical(
                    alibi=alibi.claim,
                    placement=placement,
                    weak_reasons=weak_reasons,
                    kill_scene=is_kill_scene,
                ),
                evidence_band=("weak" if weak_reasons else "strong")
                if evidence_reasoning_version == 1
                else None,
            )


def _vent_observation_matches_record(
    observation: SawVentObservation,
    record: VentWitnessRecord,
) -> bool:
    """Whether one spoken vent observation matches one typed record (Task 15.4).

    The deterministic grounding comparison: same ``subject``, canonically
    intersecting rooms (:func:`canonical_rooms` -- the detector's one room
    normalisation point, so a compound spoken label like ``"LABS/MEDBAY"``
    still matches the record's canonical engine room, while a non-spatial
    label matches nothing), and a spoken tick within
    :data:`VENT_GROUNDING_TICK_TOLERANCE` of the record's tick. Pure function
    of its two arguments -- no prose parsing, no LLM judgment.
    """

    if observation.subject != record.subject:
        return False
    if abs(observation.tick - record.tick) > VENT_GROUNDING_TICK_TOLERANCE:
        return False
    observation_rooms = canonical_rooms(observation.room)
    record_rooms = canonical_rooms(record.room)
    return bool(observation_rooms and record_rooms & observation_rooms)


def sighting_observation_matches_record(
    observation: SawPlayerObservation,
    record: SightingRecord,
) -> bool:
    """Whether one spoken sighting matches one typed record (Task 16.7).

    :func:`_vent_observation_matches_record`'s polarity-inverted sibling --
    the same deterministic comparison: same ``subject``, canonically
    intersecting rooms (:func:`canonical_rooms`, so a compound spoken label
    still matches the record's canonical engine room while a non-spatial
    label matches nothing), and a spoken tick within
    :data:`SIGHTING_GROUNDING_TICK_TOLERANCE` of the record's tick.
    ``co_present`` is deliberately NOT part of the match key: the record's
    companion projection is completeness for downstream consumers, while
    grounding needs only "did the speaker really see this subject there,
    then". Pure function of its two arguments -- no prose parsing, no LLM
    judgment.
    """

    if observation.subject != record.subject:
        return False
    if abs(observation.tick - record.tick) > SIGHTING_GROUNDING_TICK_TOLERANCE:
        return False
    observation_rooms = canonical_rooms(observation.room)
    record_rooms = canonical_rooms(record.room)
    return bool(observation_rooms and record_rooms & observation_rooms)


def grounded_vouch_subjects(
    transcript: MeetingTranscript,
    *,
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]],
    roster: frozenset[PlayerId] | None = None,
    trigger_kind: MeetingTriggerKind | None = None,
) -> frozenset[PlayerId]:
    """Subjects of GROUNDED VOUCHES -- corroboration-class, never flags (Task 16.7).

    The vent grounding chokepoint's polarity-inverted sibling
    (:func:`_detect_grounded_vent_flags`): for every spoken
    :class:`~meetings.schemas.SawPlayerObservation` naming ANOTHER player,
    the SPEAKER'S OWN typed records are searched for a match
    (:func:`sighting_observation_matches_record`). A match proves the
    speaker honestly reported what they saw -- it does NOT prove the
    subject innocent -- so the subject earns exactly the weak exculpation
    the existing corroboration channel already prices: the returned set
    feeds :func:`meetings.manager.derive_belief_evidence`'s
    ``corroborated`` set (the
    :data:`agents.memory.beliefs.CORROBORATION_SUSPICION_DELTA` -0.05,
    deduplicated per subject per meeting by the set fold), NEVER a
    :class:`~meetings.schemas.ContradictionRef` and NEVER the dead trust
    field. An ungrounded spoken sighting stays ordinary testimony, and a
    FABRICATED vouch (no matching record) contributes nothing -- the
    anti-collusion floor: two impostors vouching for each other with
    invented sightings earn zero exculpation.

    Known property, not a bug: an impostor who TRUTHFULLY vouches for its
    partner grounds legitimately -- the sighting is true. The delta is
    small by design and the mutual-vouching PATTERN stays visible in the
    transcript for Phase 17's collusion detectors.

    Three gates beyond the record match, mirroring the channel's existing
    discipline:

    * **self-vouch exclusion** -- a sighting whose subject IS the speaker
      grounds nothing (self-exculpation would let any player mint their
      own -0.05 from their own log);
    * **roster** -- a non-roster subject (hallucinated id, dead player)
      never reaches the fold, matching :func:`detect_corroborations`;
    * **Rule-3 relevance** (:func:`is_relevant_sighting` against this
      meeting's :func:`triggering_body_rooms`) -- a spawn-window or
      kill-scene vouch is evidentially empty and never exculpates,
      preserving the documented invariant that EVERY producer of the
      ``corroborated`` set routes through the one relevance gate
      (:data:`agents.memory.beliefs.CORROBORATION_SUSPICION_DELTA`). The
      gate reads each candidate RECORD's tick and room, never the
      model-stated observation: the +-:data:`SIGHTING_GROUNDING_TICK_TOLERANCE`
      match window would otherwise let a spawn-window record be re-timed one
      tick past the window and exculpate off an evidentially-empty sighting.
      A vouch grounds iff SOME record both matches and is relevant, so an
      irrelevant record never masks a later relevant one within the window.

    Pure and deterministic: a function of the transcript, the typed
    records, and the trigger kind alone. A caller with no records gets the
    empty set -- in particular the replay-side re-derivation
    (:func:`meetings.manager.extract_belief_evidence`) has no private
    records by construction, so a grounded vouch can only ever move the
    PRE-VOTE fold, the same record/replay boundary the vent channel draws.
    The production pre-vote call does not pass the participant mapping YET:
    committed transcripts already carry speaker-groundable sightings, so
    the live feed is a behavioral change that graduates under the phase's
    byte-identity lever doctrine (see
    :func:`meetings.manager.derive_belief_evidence`), not here.
    """

    effective_roster = _NO_ROSTER if roster is None else roster
    body_rooms = triggering_body_rooms(transcript, trigger_kind=trigger_kind)
    grounded: set[PlayerId] = set()
    for turn in transcript.turns:
        records = sighting_records.get(turn.speaker, ())
        if not records:
            continue
        for observation in turn.observations:
            if not isinstance(observation, SawPlayerObservation):
                continue
            if observation.subject == turn.speaker:
                continue
            if observation.subject in grounded:
                continue
            if not _subject_in_roster(observation.subject, effective_roster):
                continue
            # The vouch grounds iff the speaker holds AT LEAST ONE record that
            # both MATCHES the spoken sighting and is itself relevance-grade.
            # The Rule-3 relevance gate reads each candidate RECORD (the private
            # ground truth), NEVER the model-stated observation tick/room: the
            # match tolerance (+-SIGHTING_GROUNDING_TICK_TOLERANCE) would
            # otherwise let a spawn-window record be re-timed one tick past the
            # window and slip an evidentially-empty sighting through the
            # exculpation channel. Testing match-AND-relevance per record (not
            # "pick the first match, then gate it") means an irrelevant
            # spawn-window/kill-scene record never masks a later relevant one
            # for the same subject/room within the window. The record's
            # canonical rooms are non-empty by construction on a match (it
            # required them to intersect the spoken rooms).
            if any(
                sighting_observation_matches_record(observation, record)
                and is_relevant_sighting(
                    tick=record.tick,
                    rooms=canonical_rooms(record.room),
                    triggering_body_rooms=body_rooms,
                )
                for record in records
            ):
                grounded.add(observation.subject)
    return frozenset(grounded)


def _detect_grounded_vent_flags(
    transcript: MeetingTranscript,
    *,
    vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]],
    roster: frozenset[PlayerId],
    evidence_reasoning_version: Literal[1, 2] | None = None,
) -> Iterator[ContradictionRef]:
    """Yield one STRONG ``vent_sighting`` flag per grounded vent observation.

    Task 15.4's hard-flag rule -- the grounding chokepoint. For every spoken
    :class:`~meetings.schemas.SawVentObservation` whose subject is in the
    roster, the SPEAKER'S OWN typed records are searched for a match
    (:func:`_vent_observation_matches_record`); the first matching record (in
    the accessor's append/tick order -- deterministic) grounds the flag. The
    description quotes the RECORD, never the spoken values: the hard evidence
    derives from what the witness's own deterministic memory holds, with the
    spoken observation as the public, citable surface (both event ids
    reference it, so ``VoteBallot.primary_reason_id`` reaches the flag
    through the observation's turn id).

    No weak band exists for this kind: an unmatched observation yields
    NOTHING (testimony, not evidence), and a matched one is STRONG -- the
    grounding chain (engine event -> witness-gated packet -> episodic record
    -> typed channel) means a grounded flag can only name a genuine venter,
    so the "STRONG flag naming a CREWMATE" false-positive class is
    structurally unreachable. Score-side, the flag rides the standard Rule-2
    path (:func:`contradiction_lift_key` falls back to the event-id pair, one
    key per observation) under ``MEETING_CONTRADICTION_LIFT_CAP`` and the
    manager's joint cap -- no new stacking channel.
    """

    for turn in transcript.turns:
        records = vent_witness_records.get(turn.speaker, ())
        if not records:
            continue
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawVentObservation):
                continue
            if not _subject_in_roster(observation.subject, roster):
                continue
            matched = next(
                (
                    record
                    for record in records
                    if _vent_observation_matches_record(observation, record)
                ),
                None,
            )
            if matched is None:
                continue
            event_id = turn_observation_id(turn=turn, index=index)
            yield _build_contradiction(
                kind="vent_sighting",
                event_a_id=event_id,
                event_b_id=event_id,
                subjects=(observation.subject,),
                description=_describe_vent_sighting(
                    speaker=turn.speaker, record=matched
                ),
                evidence_band=("strong") if evidence_reasoning_version == 1 else None,
            )


def _detect_vent_placement_contradictions(
    transcript: MeetingTranscript,
    *,
    self_alibis: tuple[_IndexedAlibi, ...],
    vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]],
    roster: frozenset[PlayerId],
    evidence_reasoning_version: Literal[1, 2] | None = None,
) -> Iterator[ContradictionRef]:
    """Yield STRONG ``alibi_vs_physical`` flags for grounded vent placements.

    The 17.5 scope firewall's flag-minting arm (audit-phase-17-close.md §6
    item 4). This arm ALWAYS feeds
    the DETECTOR on the production path; the absent-set derivation the widening
    once fed alone (:func:`absent_players`) now takes its Task-18.12 production
    driver from :func:`grounded_vent_subjects_from_flags`, reading the
    ``vent_sighting`` flag channel. For every spoken
    :class:`~meetings.schemas.SawVentObservation` on any turn (indexed with
    :func:`turn_observation_id`) whose subject is in the
    roster, the SPEAKER'S OWN typed records must exist; for each of the
    SUBJECT'S OWN de-echoed self-alibis (``self_alibis``, the tuple
    :func:`detect_contradictions` already computes) with non-empty canonical
    rooms and ``claim.subject == observation.subject``, the flag mints iff SOME
    record BOTH:

    * matches the spoken observation via
      :func:`_vent_observation_matches_record` (the 15.4 chokepoint reused
      VERBATIM -- never a re-derivation), AND
    * contradicts the alibi reading the RECORD's fields:
      ``from_tick <= record.tick <= to_tick`` (INCLUSIVE window) and
      ``canonical_rooms(record.room)`` non-empty and disjoint from
      ``alibi.rooms``.

    Testing match-AND-contradict per record (the 16.7 lesson) means a
    matching-but-CONSISTENT record never masks a later matching-and-contradicting
    one; the first such record in channel order (the accessor's append/tick
    order -- deterministic) grounds the flag. One flag per (grounded observation,
    contradicted self-alibi) pair.

    Doctrine (mirrors the 15.4 ``vent_sighting`` firewall). GROUNDED-ONLY is the
    whole defense: an UNGROUNDED spoken vent claim mints NOTHING (a fabrication
    channel otherwise). STRONG with NO weak band: the grounding chain (engine
    event -> witness-gated packet -> episodic record -> typed channel) proves the
    subject a genuine venter (impostor-only, DESIGN.md §3.4), so the "STRONG flag
    naming a CREWMATE" false-positive class is structurally unreachable -- which
    is ALSO why the record-side window is INCLUSIVE here (the endpoint band
    prices coarse spoken recollection fuzz between two TESTIMONIES, but the record
    side is typed engine truth and the flag can never name a crewmate). No
    corroboration suppression (engine truth beats forgeable testimony -- a
    colluder corroborating the false alibi must not suppress it) and no
    voice-counting / adversarial-pair guard (the record grounds regardless of
    chain position), mirroring kill_scene's "can only CONTRADICT, never
    corroborate". The description QUOTES THE RECORD (room/tick), never the spoken
    values, and both event ids reference the public surface (the alibi's event id
    and the observation's turn id). Pure and deterministic; a caller with no
    records yields nothing.
    """

    for turn in transcript.turns:
        records = vent_witness_records.get(turn.speaker, ())
        if not records:
            continue
        for index, observation in enumerate(turn.observations):
            if not isinstance(observation, SawVentObservation):
                continue
            if not _subject_in_roster(observation.subject, roster):
                continue
            observation_id = turn_observation_id(turn=turn, index=index)
            for alibi in self_alibis:
                if not alibi.rooms:
                    continue
                if alibi.claim.subject != observation.subject:
                    continue
                matched = next(
                    (
                        record
                        for record in records
                        if _vent_observation_matches_record(observation, record)
                        and alibi.claim.from_tick <= record.tick <= alibi.claim.to_tick
                        and canonical_rooms(record.room)
                        and not (canonical_rooms(record.room) & alibi.rooms)
                    ),
                    None,
                )
                if matched is None:
                    continue
                yield _build_contradiction(
                    kind="alibi_vs_physical",
                    event_a_id=alibi.event_id,
                    event_b_id=observation_id,
                    subjects=(observation.subject,),
                    description=_describe_vent_placement(
                        speaker=turn.speaker, record=matched, alibi=alibi.claim
                    ),
                    evidence_band=("strong")
                    if evidence_reasoning_version == 1
                    else None,
                )


def _grounded_vent_subjects(
    transcript: MeetingTranscript,
    *,
    vent_witness_records: Mapping[PlayerId, tuple[VentWitnessRecord, ...]],
    roster: frozenset[PlayerId],
) -> frozenset[PlayerId]:
    """Subjects of GROUNDED vent sightings -- Task 17.5's placement input.

    The subject set behind :func:`absent_players`'s
    ``include_vent_sightings`` widening: exactly the subjects
    :func:`_detect_grounded_vent_flags` would flag, computed through the
    SAME 15.4 chokepoint gates -- for every spoken
    :class:`~meetings.schemas.SawVentObservation` on any turn, the
    SPEAKER'S OWN typed records are searched for a match
    (:func:`_vent_observation_matches_record`; roster-filtered subjects,
    no relevance gate -- grounding is the only gate, see the flag
    detector's docstring). Because a recorded ``vent_sighting`` flag and a
    grounded placement share one predicate, the widened absent set can
    never disagree with the flag channel about WHO was seen venting.

    Only the SUBJECT set is returned (the widening removes players; it
    mints no event ids and no descriptions), mirroring
    :func:`grounded_vouch_subjects` -- the 16.7 sibling that reduces the
    same turn walk to a subject fold. Pure and deterministic; a caller
    with no records gets the empty set.
    """

    grounded: set[PlayerId] = set()
    for turn in transcript.turns:
        records = vent_witness_records.get(turn.speaker, ())
        if not records:
            continue
        for observation in turn.observations:
            if not isinstance(observation, SawVentObservation):
                continue
            if observation.subject in grounded:
                continue
            if not _subject_in_roster(observation.subject, roster):
                continue
            if any(
                _vent_observation_matches_record(observation, record)
                for record in records
            ):
                grounded.add(observation.subject)
    return frozenset(grounded)


def _weak_signal_reasons(
    alibi: _IndexedAlibi, *, include_self_stated: bool = True
) -> tuple[str, ...]:
    """The Task 9.7 false-positive patterns ``alibi`` matches, if any.

    Both patterns are properties of the alibi side alone, so the
    classification is computed once per alibi regardless of how many
    sightings it is paired with. Order is fixed (self-stated, then
    narrow window) so the rendered marker is byte-stable across runs.
    The Task 10.1 conflict classification reuses this helper per side,
    so the two paths share one definition of self-stated / narrow.

    Task 13.14 (owner LONE-STRONG decision, 2026-06-22; DESIGN.md §5.4 +
    §6.4) reverses the audit-9.7 self-stated down-weight for the
    ``alibi_vs_sighting`` band: a self-stated-only alibi contradicted by a
    third party's sighting now classifies STRONG and drives Rule 2's full
    gate-crossing delta (the Probe-3 R7 lever, report-forward-redesign-probes.md).
    The sighting path therefore passes ``include_self_stated=False`` so the
    self-stated reason is no longer emitted there. The genuine shaky guards
    -- narrow window (here), and endpoint-tick (appended by the caller at
    :func:`_detect_alibi_vs_sightings`) -- STAY weak (real precision guards,
    not the self-stated down-weight). The ``alibi_conflict`` path keeps the
    default ``include_self_stated=True``: :func:`_conflict_weak_reasons`
    needs the per-side self-stated classification to derive the
    self-PAIR weak reason, which the task explicitly keeps weak.
    """

    reasons: list[str] = []
    if include_self_stated and alibi.speaker == alibi.claim.subject:
        reasons.append(WEAK_REASON_SELF_STATED)
    if alibi.claim.to_tick - alibi.claim.from_tick < NARROW_ALIBI_WINDOW_TICKS:
        reasons.append(WEAK_REASON_NARROW_WINDOW)
    return tuple(reasons)


def _conflict_weak_reasons(
    left: _IndexedAlibi,
    right: _IndexedAlibi,
    *,
    accusation_pairs: frozenset[tuple[PlayerId, PlayerId]],
    evidence_reasoning_version: Literal[1, 2] | None = None,
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
    if not (
        evidence_reasoning_version == 1
        and left.claim.from_tick == left.claim.to_tick
        and right.claim.from_tick == right.claim.to_tick
    ) and (
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
    evidence_band: Literal["weak", "strong"] | None = None,
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
        evidence_band=evidence_band,
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


def _describe_alibi_vs_physical(
    *,
    alibi: AlibiClaim,
    placement: StatedPlacement,
    weak_reasons: tuple[str, ...] = (),
    kill_scene: bool = False,
) -> str:
    # The placement's rooms are a canonical set (one or more member rooms);
    # join them sorted so the rendered memory view (§5.4 "flags are
    # information") is byte-stable regardless of frozenset order. ``speaker``
    # names the independent voice whose placement contradicts the subject's own
    # alibi -- the deductive content a voter reads. A lone-voice atom carries the
    # weak marker (:data:`WEAK_REASON_LONE_PHYSICAL`); the two-source conjunction
    # carries none and is STRONG (:func:`_detect_alibi_vs_physical`).
    placed_in = "/".join(sorted(placement.rooms))
    base = (
        f"{alibi.subject}'s own alibi places them in {alibi.room} "
        f"(ticks {alibi.from_tick}-{alibi.to_tick}), but {placement.speaker} "
        f"placed {alibi.subject} in {placed_in} at tick {placement.tick} -- "
        f"physically incompatible with the stated alibi."
    )
    # Task 13.5.3: name the kill scene in the rendered flag (legibility only --
    # ``kill_scene`` is False on every non-kill-scene path, so this is
    # byte-identical to the 13.4 text there).
    if kill_scene:
        base = f"{base} The sighting places them at the kill scene."
    if not weak_reasons:
        return base
    return f"{base} {WEAK_CONTRADICTION_MARKER_PREFIX}{'; '.join(weak_reasons)}]"


def _describe_vent_sighting(*, speaker: PlayerId, record: VentWitnessRecord) -> str:
    # Quote the RECORD (the witness's deterministic memory), never the spoken
    # observation's values: the flag's factual content must be exactly what
    # the grounding chokepoint confirmed. No weak-marker branch exists for
    # this kind -- a vent flag is only ever minted grounded, and grounded is
    # STRONG (:func:`_detect_grounded_vent_flags`).
    return (
        f"{speaker} witnessed {record.subject} vent in {record.room} at tick "
        f"{record.tick}; venting is impostor-only, and the spoken observation "
        f"matches the witness's own record."
    )


def _describe_vent_placement(
    *, speaker: PlayerId, record: VentWitnessRecord, alibi: AlibiClaim
) -> str:
    # Task 18.9 lever 2: quote the RECORD (the witness's deterministic memory),
    # never the spoken observation's values -- the grounded fact is exactly what
    # the 15.4 chokepoint confirmed -- and name the contradicted STATED account
    # so the rendered memory view carries the deductive content (§5.4 "flags are
    # information"). No weak-marker branch exists for this variant: a grounded
    # vent placement is only ever minted STRONG (the grounding chain proves an
    # impostor-only venter, so the STRONG-flag-naming-a-crewmate false positive is
    # structurally unreachable -- :func:`_detect_vent_placement_contradictions`).
    return (
        f"{speaker} witnessed {record.subject} vent in {record.room} at tick "
        f"{record.tick}, but {record.subject}'s own account places them in "
        f"{alibi.room} (ticks {alibi.from_tick}-{alibi.to_tick}) -- venting is "
        f"impostor-only, physically incompatible with the stated account."
    )


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

    Reuses the :func:`_turn_claim_id` / :func:`turn_observation_id`
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
        for obs_index, observation in enumerate(turn.observations):
            # Task 16.7: a whereabouts self-placement is cited by its alibi-side
            # id (:func:`_turn_whereabouts_id`), so register THAT id here or a
            # whereabouts-alibi flag's ``event_a_id`` would not resolve to its
            # speaker in the proxy-intra-turn guard.
            if isinstance(observation, WhereaboutsClaim):
                index[_turn_whereabouts_id(turn=turn, index=obs_index)] = turn.speaker
            else:
                index[turn_observation_id(turn=turn, index=obs_index)] = turn.speaker
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
        evidence_band="weak" if flag.evidence_band is not None else None,
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
        evidence_band="weak" if flag.evidence_band is not None else None,
    )


def _apply_grounded_prosecution(
    flags: Sequence[ContradictionRef],
    *,
    sightings: tuple[_IndexedSighting, ...],
    sighting_records: Mapping[PlayerId, tuple[SightingRecord, ...]],
    event_speakers: Mapping[str, PlayerId],
) -> list[ContradictionRef]:
    """Band an ``alibi_vs_sighting`` WEAK unless grounded testimony carries it.

    The grounding and two-source rules, applied as a
    post-pass over the finished flag set so the physical-anchor set is complete.
    A flag survives STRONG only when its own sighting side is GROUNDED in the
    speaker's own records AND
    :data:`~meetings.constants.GROUNDED_PROSECUTION_MIN_SOURCES` distinct
    CARRIERS stand behind the case against that subject.

    A carrier is a SPEAKER ID, counted once however many times they speak: a
    grounded speaker contradicting that subject over that claim, or the speaker
    behind a ``vent_sighting`` / ``alibi_vs_physical`` flag naming the subject
    in this meeting (the two channels grounded by construction). Neither the
    subject nor the alibi's own speaker is ever a carrier, and one narrator who
    supplies both a direct sighting and a co-presence placement is still ONE --
    the anchor substitutes for a second WITNESS, never for a second account by
    the same one.

    A speaker whose own flag is already banded weak (an endpoint-tick or
    narrow-window sighting) still carries -- the earlier bands price that one
    account's fuzz, not the speaker's existence -- but is never re-banded here.

    Only descriptions move: every flag keeps its id, kind, event pair and
    subjects, so citations and the detector's sort are unaffected. Flags of
    another kind pass through untouched.
    """

    indexed = {sighting.event_id: sighting for sighting in sightings}
    grounded = {
        sighting.event_id: _sighting_is_grounded(
            sighting, records=sighting_records.get(sighting.speaker, ())
        )
        for sighting in sightings
    }
    # Per subject, the SPEAKERS behind the grounded-by-construction flags naming
    # them. Keeping the identity (not just the subject) is what stops one
    # narrator supplying both halves of the two-carrier bar -- a direct sighting
    # plus their own co-presence placement of the same subject.
    anchors: dict[PlayerId, set[PlayerId]] = {}
    for flag in flags:
        if flag.kind not in ("vent_sighting", "alibi_vs_physical"):
            continue
        speakers = {
            speaker
            for event_id in (flag.event_a_id, flag.event_b_id)
            if (speaker := event_speakers.get(event_id)) is not None
        }
        for subject in flag.subjects:
            anchors.setdefault(subject, set()).update(speakers - {subject})

    # Pass 1: resolve each flag of this kind to (claim, sighting) and collect,
    # per (subject, claim), the DISTINCT grounded speakers prosecuting it.
    # ALREADY-WEAK flags contribute a source too: an endpoint-tick sighting is
    # transit fuzz on its own but a second honest account of the same claim
    # (the 10.1 "an endpoint mismatch can still be a real signal once
    # corroborated" band). They are excluded from RE-BANDING below, not from
    # the count.
    resolved: dict[str, tuple[tuple[PlayerId, str], str]] = {}
    sources: dict[tuple[PlayerId, str], set[PlayerId]] = {}
    for flag in flags:
        if flag.kind != "alibi_vs_sighting":
            continue
        sides = _grounded_prosecution_sides(flag, sightings=indexed)
        if sides is None:
            continue
        claim_id, sighting_id = sides
        subject = flag.subjects[0]
        claim_key = (subject, claim_id)
        sources.setdefault(claim_key, set())
        if not is_weak_contradiction(flag):
            resolved[flag.contradiction_id] = (claim_key, sighting_id)
        speaker = indexed[sighting_id].speaker
        if grounded[sighting_id] and speaker not in (
            subject,
            event_speakers.get(claim_id),
        ):
            sources[claim_key].add(speaker)

    # Pass 2: re-band. Reason order is fixed so the rendered marker is stable.
    banded: list[ContradictionRef] = []
    for flag in flags:
        candidate = resolved.get(flag.contradiction_id)
        if candidate is None:
            banded.append(flag)
            continue
        prosecution_key, sighting_id = candidate
        subject, claim_id = prosecution_key
        # The alibi's own author is a party to the dispute, not a witness to it:
        # excluded from the anchor half exactly as from the source half above.
        claim_speaker = event_speakers.get(claim_id)
        carriers = sources[prosecution_key] | {
            speaker
            for speaker in anchors.get(subject, set())
            if speaker != claim_speaker
        }
        reasons: list[str] = []
        if not grounded[sighting_id]:
            reasons.append(WEAK_REASON_UNGROUNDED_SIGHTING)
        elif len(carriers) < GROUNDED_PROSECUTION_MIN_SOURCES:
            reasons.append(WEAK_REASON_LONE_GROUNDED_SOURCE)
        banded.append(
            flag if not reasons else _demote_prosecution(flag, reasons=tuple(reasons))
        )
    return banded


def _grounded_prosecution_sides(
    flag: ContradictionRef, *, sightings: Mapping[str, _IndexedSighting]
) -> tuple[str, str] | None:
    """``(claim event id, sighting event id)`` of one flag, or ``None``.

    Read by TYPE, never by position: ``_build_contradiction`` sorts the event
    pair, so which of ``event_a_id`` / ``event_b_id`` is the sighting depends on
    the turn ids. An alibi side is a claim / whereabouts id and a sighting side
    an observation id, so exactly one of the two is in the sighting index;
    anything else (a flag whose sighting was not indexed, a subject-less flag)
    is left for the caller to pass through untouched.
    """

    if len(flag.subjects) != 1:
        return None
    a_indexed = flag.event_a_id in sightings
    b_indexed = flag.event_b_id in sightings
    if a_indexed == b_indexed:
        return None
    if a_indexed:
        return flag.event_b_id, flag.event_a_id
    return flag.event_a_id, flag.event_b_id


def _sighting_is_grounded(
    sighting: _IndexedSighting, *, records: tuple[SightingRecord, ...]
) -> bool:
    """Whether the speaker's own typed memory supports this spoken placement.

    A movement-derived placement is grounded by construction -- it exists only
    because the speaker's own :class:`~meetings.schemas.MoveWitnessRecord`
    confirmed the transition -- and its channel is disjoint from the
    ``saw_player`` rows below, so it is exempted rather than searched for a
    record it could not hold. Everything else grounds through the vouch
    channel's predicate, unchanged.
    """

    if sighting.movement_grounded:
        return True
    return any(
        sighting_observation_matches_record(sighting.observation, record)
        for record in records
    )


def _demote_prosecution(
    flag: ContradictionRef, *, reasons: tuple[str, ...]
) -> ContradictionRef:
    # Rebuild through the shared marker format: the factual base text is
    # PRESERVED (the claim and the sighting are still information, §5.4) and the
    # new reasons append after any the flag already carries. The event-id pair
    # and subjects are reused verbatim, so :func:`_build_contradiction`
    # recomputes the identical ``contradiction_id``.
    base, existing = _split_weak_marker(flag.description)
    merged = (*existing, *(r for r in reasons if r not in existing))
    return _build_contradiction(
        kind=flag.kind,
        event_a_id=flag.event_a_id,
        event_b_id=flag.event_b_id,
        subjects=flag.subjects,
        description=(f"{base} {WEAK_CONTRADICTION_MARKER_PREFIX}{'; '.join(merged)}]"),
        evidence_band="weak" if flag.evidence_band is not None else None,
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


def turn_observation_id(*, turn: MeetingTurn, index: int) -> str:
    return f"turn:{turn.turn_id}:obs:{index}"


def _turn_whereabouts_id(*, turn: MeetingTurn, index: int) -> str:
    # Task 16.7: a whereabouts self-placement is an alibi-side account carried on
    # ``turn.observations``; it gets its OWN segment (not ``:obs:``) so
    # :func:`contradiction_lift_key` recognises it as an account key. ``index``
    # is the observation index, matching :func:`_event_speaker_index`.
    return f"turn:{turn.turn_id}:whereabouts:{index}"


def _ranges_overlap(a_from: int, a_to: int, b_from: int, b_to: int) -> bool:
    # Inclusive overlap, matching :class:`AlibiClaim`'s "tick ranges
    # are inclusive" contract.
    return a_from <= b_to and b_from <= a_to


__all__ = [
    "CANONICAL_ROOMS",
    "CANONICAL_ROOM_NEIGHBORS",
    "MOVE_GROUNDING_TICK_TOLERANCE",
    "NARROW_ALIBI_WINDOW_TICKS",
    "PHYSICAL_CONTRADICTION_MIN_VOICES",
    "SIGHTING_GROUNDING_TICK_TOLERANCE",
    "SPAWN_WINDOW_LAST_TICK",
    "VENT_GROUNDING_TICK_TOLERANCE",
    "WEAK_CONTRADICTION_MARKER_PREFIX",
    "WEAK_REASON_ADJACENT_ONE_TICK",
    "WEAK_REASON_ADVERSARIAL",
    "WEAK_REASON_BOUNDARY_OVERLAP",
    "WEAK_REASON_ENDPOINT_TICK",
    "WEAK_REASON_KILL_SCENE",
    "WEAK_REASON_LONE_GROUNDED_SOURCE",
    "WEAK_REASON_LONE_PHYSICAL",
    "WEAK_REASON_NARROW_WINDOW",
    "WEAK_REASON_PROXY_INTRA_TURN",
    "WEAK_REASON_RETARGETED_PROXY",
    "WEAK_REASON_SELF_PAIR",
    "WEAK_REASON_SELF_STATED",
    "WEAK_REASON_UNGROUNDED_SIGHTING",
    "ChainStep",
    "ChainTermination",
    "ChainWalk",
    "DetectedCorroboration",
    "StatedPlacement",
    "absent_players",
    "accusation_target",
    "canonical_rooms",
    "contradiction_lift_key",
    "detect_contradictions",
    "detect_corroborations",
    "grounded_vent_subjects_from_flags",
    "grounded_vouch_subjects",
    "independent_voices",
    "is_canonically_ordered",
    "is_relevant_sighting",
    "is_weak_contradiction",
    "move_observation_matches_record",
    "next_chain_step",
    "reconstruct_stated_paths",
    "room_hops",
    "self_refuted_alibi_claim_ids",
    "sighting_observation_matches_record",
    "sighting_placement",
    "sort_turns_canonically",
    "triggering_body_rooms",
    "turn_observation_id",
    "walk_chain",
]
