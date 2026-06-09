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
from meetings.transcript import is_weak_contradiction
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
Corroboration still converts: a second weak flag (0.66), a strong
contradiction (0.88), or a body-proximity / vent-elevated prior all
carry the subject across 0.60, so innocents stay ejectable on a second
independent signal. Strong contradictions keep the full
``CONTRADICTION_SUSPICION_DELTA``; recall is not paid for globally."""

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
    lone self-stated / narrow-window ``alibi_vs_sighting`` lands in the
    suspicious-but-below-gate band [0.5, 0.60) rather than mechanically
    crossing the §4.6 eject gate. The classification is read off the
    flag itself (:func:`meetings.transcript.is_weak_contradiction`), so
    the rule stays a pure function of its arguments.

    A subject appearing in multiple flags is bumped once per flag,
    matching "each detected contradiction is one piece of evidence" --
    which is also the corroboration path: two weak flags, or a weak plus
    a strong one, still accumulate past the gate.
    Subjects are processed in sorted order per flag so the resulting
    state is deterministic regardless of subject tuple ordering -- a
    precondition for replay-stable belief snapshots.
    """

    result = beliefs.copy()
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
        for subject in sorted(contradiction.subjects):
            result.record_contradiction(subject, belief_ref)
            result.adjust_suspicion(subject, delta=delta)
    return result


__all__ = [
    "BODY_PROXIMITY_SUSPICION_DELTA",
    "BODY_PROXIMITY_WINDOW_TICKS",
    "CONTRADICTION_SUSPICION_DELTA",
    "OBSERVED_VENT_ACTION",
    "VENTING_SUSPICION_DELTA",
    "WEAK_CONTRADICTION_SUSPICION_DELTA",
    "AlibiClaim",
    "BeliefState",
    "ContradictionRef",
    "PlayerBelief",
    "apply_contradiction_rule",
    "apply_observation_rules",
]
