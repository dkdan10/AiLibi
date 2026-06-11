"""Belief state (DESIGN.md §6.1, §6.3).

Per other-player view tracking ``trust``, ``suspicion``, ``alibi_map``,
and ``inconsistencies``. The store exposes write-path primitives that
perception (Task 2.4) and contradiction detection (Phase 3) drive — the
specific update weights from §6.3 are config that lives outside this
module so they can be tuned against the eval harness.

Read paths beyond the simple ``view`` accessor and prompt rendering ship
in Phase 3 (Task 3.3).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass, field
from typing import Final, TypeAlias

from meetings.schemas import ContradictionRef as MeetingContradictionRef
from meetings.transcript import contradiction_lift_key, is_weak_contradiction
from observation.packet import ObservationPacket

PlayerId: TypeAlias = str
RoomId: TypeAlias = str
BodyId: TypeAlias = str

_TRUST_FLOOR = 0.0
_TRUST_CEIL = 1.0
_SUSPICION_FLOOR = 0.0
_SUSPICION_CEIL = 1.0
_DEFAULT_TRUST = 0.5
_DEFAULT_SUSPICION = 0.5

# DESIGN.md §6.3 belief-update weights. The design is explicit that "these
# weights are config, not constants -- they will be tuned against the eval
# harness", so they live here as the single tuning point (a one-line edit
# each) until a Phase-5 config layer lands. Task 4.14 wires only Rules 1 and
# 4; Rules 2, 3, and 5 from §6.3 are deferred to Phase 5.
VENTING_SUSPICION_DELTA: Final[float] = 0.5
"""DESIGN.md §6.3 Rule 4: suspicion added when a player is observed venting."""

BODY_PROXIMITY_SUSPICION_DELTA: Final[float] = 0.2
"""DESIGN.md §6.3 Rule 1: suspicion added for co-presence near a fresh body."""

BODY_PROXIMITY_WINDOW_TICKS: Final[int] = 3
"""DESIGN.md §6.3 Rule 1 window: how many ticks before a body's discovery
count as "shortly before" for the proximity adjustment."""

CONTRADICTION_SUSPICION_DELTA: Final[float] = 0.3
"""DESIGN.md §6.3 Rule 2: suspicion added when a player's claimed alibi
contradicts another agent's testimony (a detected meeting contradiction)."""

WEAK_CONTRADICTION_SUSPICION_DELTA: Final[float] = 0.08
"""Graduated §6.3 Rule 2 delta for detector-flagged WEAK contradictions
(Task 9.7; audit gp-1 precision).

A self-stated or narrow-window ``alibi_vs_sighting``
(:func:`meetings.transcript.is_weak_contradiction`) is the audited
false-positive pattern: under the full 0.3 delta one such flag lifted
the default 0.5 prior to 0.8, crossing the §4.6 0.60 eject gate alone
and railroading 13/13 wrong ejections. The graduated delta keeps a lone
weak flag *suspicious but below the gate* -- 0.5 + 0.08 = 0.58, inside
[0.5, 0.60) -- not zeroed: a self-stated conflict IS mildly suspicious.
Corroboration still converts: a second weak flag from an independent
claim (0.66), a strong contradiction, or a body-proximity /
vent-elevated prior all carry the subject across 0.60, so innocents
stay ejectable on a second independent signal. Strong contradictions
keep the full ``CONTRADICTION_SUSPICION_DELTA``; recall is not paid for
globally. Task 10.1 extends the weak classification to the
``alibi_conflict`` kind (self-pair / adversarial / narrow /
boundary-overlap flags), which previously always carried the full
delta."""

MEETING_CONTRADICTION_LIFT_CAP: Final[float] = CONTRADICTION_SUSPICION_DELTA
"""Per-subject cap on one meeting's total Rule-2 contradiction lift
(Task 10.1; audit gp-2 C-C-3).

The detector emits one flag per (alibi, sighting) pair, so a verbose
truthful alibi paired against N repeated sightings minted N flags -- and
the vote-time lift summed per flag, lifting one innocent from the 0.5
prior to a clamped 1.0 off 19 near-duplicate weak flags (seed 9 m1,
ejected 5-0). Flag fountains anti-correlate with guilt (the audited set:
23 crew vs 11 impostor containment-class flags), so unbounded stacking
inverts the signal. Two layers repair it: the per-(subject, alibi-claim)
dedup in :func:`apply_contradiction_rule` (one delta per claim however
many sightings it pairs against), and this cap bounding a subject's
TOTAL transient lift per meeting at one strong flag's worth -- a single
strong contradiction still lands its full weight (the cap never bites a
lone flag), while no volume of flags can exceed it. Transient: the cap
applies inside one ``apply_contradiction_rule`` call (the per-meeting
vote-time lift); cross-meeting accumulation stays the 9.8 channel."""

ACCUSATION_SUSPICION_DELTA: Final[float] = 0.05
"""Accusation-driven suspicion bump (Task 9.8; audit gp-1 recall).

The persistent delta a subject gains, once per meeting, for being named
by an accusation claim in that meeting's transcript. Deliberately the
smallest evidence weight in the file -- below the weak-contradiction
0.08 band and far below the §4.6 0.60 eject gate -- because a verbal
accusation is the weakest signal the belief store tracks: one meeting
lands at 0.55, well under the gate, while the same subject accused
across 2-3 meetings accumulates over it (0.60 / 0.65). The bump is
applied POST-meeting (:func:`apply_meeting_evidence_rules`), so it can
never move the meeting it was uttered in -- the owner principle that no
single round ejects is structural, not tuned."""

CORROBORATION_SUSPICION_DELTA: Final[float] = 0.05
"""DESIGN.md §6.3 Rule 3 magnitude: suspicion REMOVED when a subject is
publicly corroborated in a meeting (Task 9.8).

§6.3 frames Rule 3 as corroboration-lowers-suspicion (its original
-0.4 example is a *verified* shared task); the meeting-layer signal is
a :class:`meetings.schemas.CorroborationClaim`, which is verbal and
therefore weighted to mirror the accusation bump exactly -- one vouch
cancels one accusation-meeting, the "collective clear" half of the
owner's collective-suspicion model. Applied once per subject per
meeting, after the accusation bumps (so at the clamp ceiling the
corroboration, not the bump, has the last word)."""

MEETING_SUSPICION_DECAY_RATE: Final[float] = 0.25
"""DESIGN.md §6.3 Rule 5 decay rate, per meeting round (Task 9.8).

Fraction of the distance to the 0.5 prior a player's suspicion drifts
after a meeting that produced no new evidence about them
(:meth:`BeliefState.decay_suspicion` ``rate``). "Rounds" in Rule 5 are
meeting rounds: gameplay-phase ticks never decay, so the perception
rules (1/4) keep their per-tick semantics and a no-meeting game is
byte-identical. 0.25 erodes an unreinforced accusation bump in a few
quiet meetings (0.55 -> 0.5375 -> 0.528 ...) while a Rule-4 vent
witness (1.0) stays over the 0.60 gate for several rounds -- strong
evidence outlives weak evidence."""

# The action label the observation layer stamps on a ``PlayerView`` when the
# observer *witnesses* a player using a vent (observation/service.py
# ``_vent_observation_for_agent``). Seeing the vent is the player-attributed
# signal Rule 4 keys on; the room-only ``vent_use_heard`` AudibleEvent carries
# no subject and is deliberately not used.
OBSERVED_VENT_ACTION: Final[str] = "vent"


@dataclass(frozen=True)
class AlibiClaim:
    """A claim that ``player_id`` was in ``room`` at ``tick``.

    ``source`` is the player who reported the claim (which may be the
    subject themself). Stored verbatim; contradiction detection is
    out of scope for this task.
    """

    player_id: PlayerId
    tick: int
    room: RoomId
    source: PlayerId


@dataclass(frozen=True)
class ContradictionRef:
    """Pointer to two facts that cannot both be true.

    The fields are intentionally untyped beyond strings so this scaffold
    does not pin the contradiction-detector data model that Phase 3 owns.
    """

    summary: str
    left_ref: str
    right_ref: str


@dataclass(frozen=True)
class PlayerBelief:
    """Immutable snapshot of beliefs about a single other player."""

    trust: float = _DEFAULT_TRUST
    suspicion: float = _DEFAULT_SUSPICION
    alibis: tuple[AlibiClaim, ...] = ()
    inconsistencies: tuple[ContradictionRef, ...] = ()


def _clamp(value: float, *, floor: float, ceil: float) -> float:
    if value < floor:
        return floor
    if value > ceil:
        return ceil
    return value


@dataclass
class _MutableBelief:
    trust: float = _DEFAULT_TRUST
    suspicion: float = _DEFAULT_SUSPICION
    alibis: list[AlibiClaim] = field(default_factory=list)
    inconsistencies: list[ContradictionRef] = field(default_factory=list)

    def snapshot(self) -> PlayerBelief:
        return PlayerBelief(
            trust=self.trust,
            suspicion=self.suspicion,
            alibis=tuple(self.alibis),
            inconsistencies=tuple(self.inconsistencies),
        )


def _clone_belief(belief: _MutableBelief) -> _MutableBelief:
    # ``alibis``/``inconsistencies`` hold frozen dataclasses, so copying the
    # list containers is a sufficient deep copy.
    return _MutableBelief(
        trust=belief.trust,
        suspicion=belief.suspicion,
        alibis=list(belief.alibis),
        inconsistencies=list(belief.inconsistencies),
    )


class BeliefState:
    """Per-agent belief tracker.

    Adjustments are clamped to ``[0, 1]``. ``view`` returns an immutable
    snapshot so callers cannot mutate internal state. Players appear in
    the store the first time any write touches them.
    """

    def __init__(self) -> None:
        self._beliefs: dict[PlayerId, _MutableBelief] = {}

    def seed_player(
        self, player_id: PlayerId, *, suspicion: float, trust: float
    ) -> None:
        """Initialise ``player_id``'s belief to the given prior scores.

        Lets a caller reconstruct a :class:`BeliefState` from an existing
        suspicion-graph snapshot (e.g. the meeting's per-voter graph) before
        applying a belief rule on top, so the rule's delta lands on the real
        prior rather than the default 0.5. Overwrites any existing entry.
        """

        self._beliefs[player_id] = _MutableBelief(
            trust=_clamp(trust, floor=_TRUST_FLOOR, ceil=_TRUST_CEIL),
            suspicion=_clamp(suspicion, floor=_SUSPICION_FLOOR, ceil=_SUSPICION_CEIL),
        )

    def known_players(self) -> tuple[PlayerId, ...]:
        return tuple(self._beliefs.keys())

    def view(self, player_id: PlayerId) -> PlayerBelief:
        belief = self._beliefs.get(player_id)
        if belief is None:
            return PlayerBelief()
        return belief.snapshot()

    def adjust_suspicion(self, player_id: PlayerId, *, delta: float) -> PlayerBelief:
        belief = self._ensure(player_id)
        belief.suspicion = _clamp(
            belief.suspicion + delta,
            floor=_SUSPICION_FLOOR,
            ceil=_SUSPICION_CEIL,
        )
        return belief.snapshot()

    def adjust_trust(self, player_id: PlayerId, *, delta: float) -> PlayerBelief:
        belief = self._ensure(player_id)
        belief.trust = _clamp(
            belief.trust + delta,
            floor=_TRUST_FLOOR,
            ceil=_TRUST_CEIL,
        )
        return belief.snapshot()

    def record_alibi(self, claim: AlibiClaim) -> PlayerBelief:
        belief = self._ensure(claim.player_id)
        belief.alibis.append(claim)
        return belief.snapshot()

    def record_contradiction(
        self,
        player_id: PlayerId,
        contradiction: ContradictionRef,
    ) -> PlayerBelief:
        belief = self._ensure(player_id)
        belief.inconsistencies.append(contradiction)
        return belief.snapshot()

    def decay_suspicion(
        self,
        player_id: PlayerId,
        *,
        toward: float = _DEFAULT_SUSPICION,
        rate: float,
    ) -> PlayerBelief:
        """Pull suspicion toward ``toward`` by ``rate`` (DESIGN.md §6.3).

        ``rate`` must be in ``[0, 1]``: ``0`` is a no-op, ``1`` snaps to
        ``toward``. The actual per-tick rate is config that lives outside
        this module.
        """

        if not 0.0 <= rate <= 1.0:
            raise ValueError(f"decay rate must be in [0, 1], got {rate}")
        belief = self._ensure(player_id)
        belief.suspicion = _clamp(
            belief.suspicion + (toward - belief.suspicion) * rate,
            floor=_SUSPICION_FLOOR,
            ceil=_SUSPICION_CEIL,
        )
        return belief.snapshot()

    def copy(self) -> BeliefState:
        """Return a deep copy whose mutations do not touch this instance.

        :func:`apply_observation_rules` uses this to stay a pure function:
        it mutates the copy and returns it, leaving the caller's state intact.
        """

        clone = BeliefState()
        clone._beliefs = {
            player_id: _clone_belief(belief)
            for player_id, belief in self._beliefs.items()
        }
        return clone

    def load_from(self, other: BeliefState) -> None:
        """Replace this state's contents with a deep copy of ``other``.

        Lets perception keep :func:`apply_observation_rules` pure while still
        updating the ``AgentMemory``-owned :class:`BeliefState` in place: the
        rule function returns a fresh state and the live instance adopts it.
        """

        self._beliefs = {
            player_id: _clone_belief(belief)
            for player_id, belief in other._beliefs.items()
        }

    def _ensure(self, player_id: PlayerId) -> _MutableBelief:
        belief = self._beliefs.get(player_id)
        if belief is None:
            belief = _MutableBelief()
            self._beliefs[player_id] = belief
        return belief


def apply_observation_rules(
    beliefs: BeliefState,
    *,
    observation: ObservationPacket,
    previous_visible_bodies: AbstractSet[BodyId],
    recent_co_presence: Mapping[RoomId, Sequence[tuple[int, PlayerId]]],
) -> BeliefState:
    """Apply DESIGN.md §6.3 rule-based belief updates (Rules 1 and 4).

    Pure: returns a new :class:`BeliefState`; ``beliefs`` is not mutated.

    Rule 4 -- observed venting (``VENTING_SUSPICION_DELTA``). Venting is
    impostor-exclusive, so a *witnessed* vent is the strongest signal an agent
    can hold ("almost certain"). The witness lands as a ``PlayerView`` carrying
    ``action == "vent"`` in ``visible_players``; the room-only
    ``vent_use_heard`` AudibleEvent is deliberately ignored because it has no
    player attribution and would smear suspicion across the whole room.

    Rule 1 -- body proximity (``BODY_PROXIMITY_SUSPICION_DELTA``). On the tick a
    body is *first* seen (``body.id`` absent from ``previous_visible_bodies``),
    every other player the agent observed in that body's room within the prior
    ``BODY_PROXIMITY_WINDOW_TICKS`` ticks gains suspicion. Firing only on first
    sighting keeps a lingering body from re-elevating bystanders every tick, and
    the body's own ``victim_id`` is skipped -- a corpse seen alive in the room
    moments earlier is not a suspect.

    ``recent_co_presence`` is keyed by room and pre-computed by the caller from
    the agent's own episodic memory; this function never reaches into a store,
    which preserves both the observation firewall and its own purity.
    """

    result = beliefs.copy()

    for player in observation.visible_players:
        if player.action == OBSERVED_VENT_ACTION:
            result.adjust_suspicion(player.id, delta=VENTING_SUSPICION_DELTA)

    for body in observation.visible_bodies:
        if body.id in previous_visible_bodies:
            continue
        co_present = {
            player_id
            for tick, player_id in recent_co_presence.get(body.room, ())
            if 0 <= observation.tick - tick <= BODY_PROXIMITY_WINDOW_TICKS
            and player_id != body.victim_id
        }
        for player_id in sorted(co_present):
            result.adjust_suspicion(player_id, delta=BODY_PROXIMITY_SUSPICION_DELTA)

    return result


def apply_contradiction_rule(
    beliefs: BeliefState,
    contradictions: Sequence[MeetingContradictionRef],
) -> BeliefState:
    """Apply DESIGN.md §6.3 Rule 2 for detected meeting contradictions.

    Pure: returns a new :class:`BeliefState`; ``beliefs`` is not mutated.

    Each :class:`meetings.schemas.ContradictionRef` names one or more
    ``subjects`` -- the players whose claims cannot both be true. For
    every such subject this records the contradiction on that player's
    belief (``record_contradiction``) and lifts their suspicion by
    ``CONTRADICTION_SUSPICION_DELTA`` (``adjust_suspicion``), so the
    vote suspicion graph reflects the detected lie (audit J-J-4). The
    meeting-side :class:`ContradictionRef` is translated into the
    agents-side belief :class:`ContradictionRef` so the inconsistency
    list stays engine-free and renders in the §6.6 memory view; the
    two shapes are deliberately distinct (the belief store predates the
    detector's data model).

    Detector-flagged weak contradictions (Task 9.7, audit gp-1) lift by
    the graduated ``WEAK_CONTRADICTION_SUSPICION_DELTA`` instead, so a
    lone self-stated / narrow-window ``alibi_vs_sighting`` -- and, since
    Task 10.1, a weak-classified ``alibi_conflict`` -- lands in the
    suspicious-but-below-gate band [0.5, 0.60) rather than mechanically
    crossing the §4.6 eject gate. The classification is read off the
    flag itself (:func:`meetings.transcript.is_weak_contradiction`), so
    the rule stays a pure function of its arguments.

    Lift dedup + cap (Task 10.1; audit gp-2 C-C-3). "Each detected
    contradiction is one piece of evidence" turned out to multiply: the
    detector emits one flag per (alibi, sighting) pair, so one alibi
    against N repeated sightings was N flags and the per-flag sum lifted
    an innocent to a clamped 1.0 (seed 9 m1: 19 near-duplicate weak
    flags = +1.52). The lift is therefore deduplicated per
    (subject, alibi-claim) pair -- one delta per underlying claim,
    however many sightings it pairs against, keyed by
    :func:`meetings.transcript.contradiction_lift_key`; a key whose
    flags classify both weak and strong contributes its strongest delta
    once. Flags from DIFFERENT claims still accumulate (two independent
    weak signals remain corroboration), but a subject's total lift per
    call is capped at ``MEETING_CONTRADICTION_LIFT_CAP`` (one strong
    flag's worth), so no flag volume alone reaches 1.0. Every flag is
    still recorded on the subject's inconsistency list -- the dedup is
    about the score, never the information (§5.4 "flags are
    information").

    Subjects are processed in sorted order so the resulting state is
    deterministic regardless of input ordering -- a precondition for
    replay-stable belief snapshots.
    """

    result = beliefs.copy()
    lift_groups: dict[tuple[PlayerId, str], float] = {}
    for contradiction in contradictions:
        belief_ref = ContradictionRef(
            summary=contradiction.description,
            left_ref=contradiction.event_a_id,
            right_ref=contradiction.event_b_id,
        )
        delta = (
            WEAK_CONTRADICTION_SUSPICION_DELTA
            if is_weak_contradiction(contradiction)
            else CONTRADICTION_SUSPICION_DELTA
        )
        lift_key = contradiction_lift_key(contradiction)
        for subject in sorted(contradiction.subjects):
            result.record_contradiction(subject, belief_ref)
            group = (subject, lift_key)
            lift_groups[group] = max(lift_groups.get(group, 0.0), delta)

    lift_by_subject: dict[PlayerId, float] = {}
    for (subject, _), delta in lift_groups.items():
        lift_by_subject[subject] = lift_by_subject.get(subject, 0.0) + delta
    for subject in sorted(lift_by_subject):
        result.adjust_suspicion(
            subject,
            delta=min(lift_by_subject[subject], MEETING_CONTRADICTION_LIFT_CAP),
        )
    return result


def apply_meeting_evidence_rules(
    beliefs: BeliefState,
    *,
    own_id: PlayerId,
    accused: Sequence[PlayerId],
    corroborated: Sequence[PlayerId] = (),
    contradicted: Sequence[PlayerId] = (),
    fellow_impostor_ids: Sequence[PlayerId] = (),
    roster: AbstractSet[PlayerId] | None = None,
) -> BeliefState:
    """Fold one meeting's public evidence into persistent beliefs (Task 9.8).

    Pure: returns a new :class:`BeliefState`; ``beliefs`` is not mutated.
    Runs POST-meeting on every living agent's stored beliefs (DESIGN.md
    §4.4 step 4's belief-update hook, rule-based), so the suspicion it
    writes carries forward into the NEXT meeting's suspicion graph --
    unlike Rule 2's vote-time contradiction lift, which stays transient
    inside the meeting that detected the flag. Three rules:

    * **Accusation bump** (``ACCUSATION_SUSPICION_DELTA``, audit gp-1
      recall): every subject in ``accused`` -- the deduplicated set of
      players named by an accusation claim in the meeting -- gains the
      small delta once. The caller deduplicates per meeting, so a
      pile-on of accusers is one meeting-level "was accused" event, and
      because the fold runs after the vote, one round can never eject
      through it.
    * **Rule 3 corroboration** (``CORROBORATION_SUSPICION_DELTA``):
      every subject in ``corroborated`` loses the mirror delta --
      a public vouch is the collective clear.
    * **Rule 5 decay** (``MEETING_SUSPICION_DECAY_RATE``): every
      *already-known* player about whom this meeting produced no new
      evidence (not accused, not corroborated, not a subject of a
      detected contradiction) drifts toward the 0.5 prior. Decay never
      materialises a row -- a player the agent holds no belief about
      has nothing to drift.

    Team-internal firewall (DESIGN.md §4.7, the 7.12/9.3 guard): a
    subject in ``fellow_impostor_ids`` is dropped from the accusation
    and contradiction evidence on the input side, so an impostor never
    accrues the accusation bump against a teammate -- and an unreinforced
    teammate row decays toward neutral like any other. Corroboration of
    a teammate is retained (it lowers suspicion, which helps the team --
    the same asymmetry as :func:`exclude_teammate_accusation_claims`
    keeping teammate alibis). The caller role-gates the list: it is
    empty for every crewmate and a sole impostor, making the guard a
    no-op on the crew path. ``own_id`` is excluded from every rule -- an
    agent holds no belief row about itself (a recorded self-accusation
    bumps everyone else's view of the speaker, never the speaker's own).

    Roster filter (Task 10.2; audit gp-6 C-C-8, H-H-6). When ``roster``
    is supplied -- the production fold passes the agent's
    engine-witnessed player-id set
    (``agents.memory.store._known_roster_ids``) -- an evidence subject
    outside it is dropped from all three sets on the input side, like
    the teammate guard: a hallucinated structural id (a game id such as
    ``"headless-seed-9"``, a turn id, a free-text phrase) never
    materialises a belief row, never bumps or lowers a score, and never
    counts as reinforced. This is the defense-in-depth backstop behind
    the Task 10.2 meeting-layer chokepoint
    (``meetings.manager._drop_non_roster_claims``): even if a garbage
    subject slips through a future claim type, the belief store -- and
    therefore every suspicion-graph / §6.6 prompt surface built from it
    -- stays roster-only. ``roster=None`` (the default) applies no
    filter, preserving the pure-math call shape for callers without a
    roster channel.

    All subject sets are processed in sorted order; the result is a
    deterministic function of its arguments (replay-stable).
    """

    if roster is not None:
        accused = [subject for subject in accused if subject in roster]
        corroborated = [subject for subject in corroborated if subject in roster]
        contradicted = [subject for subject in contradicted if subject in roster]
    teammates = frozenset(fellow_impostor_ids)
    bumped = {
        subject for subject in accused if subject != own_id and subject not in teammates
    }
    lowered = {subject for subject in corroborated if subject != own_id}
    reinforced = (
        bumped
        | lowered
        | {
            subject
            for subject in contradicted
            if subject != own_id and subject not in teammates
        }
    )

    result = beliefs.copy()
    for subject in sorted(bumped):
        result.adjust_suspicion(subject, delta=ACCUSATION_SUSPICION_DELTA)
    for subject in sorted(lowered):
        result.adjust_suspicion(subject, delta=-CORROBORATION_SUSPICION_DELTA)
    for player_id in sorted(result.known_players()):
        if player_id == own_id or player_id in reinforced:
            continue
        result.decay_suspicion(player_id, rate=MEETING_SUSPICION_DECAY_RATE)
    return result


__all__ = [
    "ACCUSATION_SUSPICION_DELTA",
    "BODY_PROXIMITY_SUSPICION_DELTA",
    "BODY_PROXIMITY_WINDOW_TICKS",
    "CONTRADICTION_SUSPICION_DELTA",
    "CORROBORATION_SUSPICION_DELTA",
    "MEETING_CONTRADICTION_LIFT_CAP",
    "MEETING_SUSPICION_DECAY_RATE",
    "OBSERVED_VENT_ACTION",
    "VENTING_SUSPICION_DELTA",
    "WEAK_CONTRADICTION_SUSPICION_DELTA",
    "AlibiClaim",
    "BeliefState",
    "ContradictionRef",
    "PlayerBelief",
    "apply_contradiction_rule",
    "apply_meeting_evidence_rules",
    "apply_observation_rules",
]
