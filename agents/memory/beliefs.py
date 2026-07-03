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
from typing import Final, Literal, TypeAlias

from meetings.schemas import ContradictionRef as MeetingContradictionRef
from meetings.schemas import MeetingTranscript
from meetings.transcript import (
    contradiction_lift_key,
    is_weak_contradiction,
    self_refuted_alibi_claim_ids,
)
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

WITNESSED_KILL_SUSPICION_DELTA: Final[float] = 1.0
"""Suspicion added when a player is *witnessed* committing a kill (Task 13.5.3;
the 2026-06-25 design-thread eyewitness-strength decision).

A witnessed kill is the single most conclusive act in the game -- only
impostors kill, and unlike a vent (which the §6.3 Rule-4 witness weights
"almost certain" at :data:`VENTING_SUSPICION_DELTA` = 0.5) it is the killer
caught in the act itself. The owner decision is that a first-hand kill view IS
conclusive for the witness: unforgeable, read from the agent's OWN memory, no
corroboration needed. So the delta is the largest in the file -- ``1.0``,
``>= VENTING_SUSPICION_DELTA`` -- and from any prior it pins the killer's
suspicion to the ``1.0`` clamp, near-certain and well over the §4.6 0.60 eject
gate. With both a vent and a kill witnessed for the same player the kill weighs
``>=`` the vent by construction (its delta is the larger, both clamp to 1.0).

Unconditional since Task 14.9 (the adopted 13.5.3 lever is the default
substrate; the ``AILIBI_WITNESSED_KILL_EVIDENCE`` gate is retired). The
witness-time rule lives in :func:`apply_observation_rules`; see there for the
§4.7 team-internal firewall (an impostor that witnesses a TEAMMATE's kill
accrues nothing)."""

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

CONTRADICTION_RENDER_CEIL: Final[float] = 0.97
"""Certain-guilt exclusion ceiling for flag/testimony-driven lift
(Task 14.10 bound 1; audit 2026-07-01 §3/§3a).

The 14.8 measurement reproduced the production vote-time fold exactly
(2482/2482 recorded rows) and found the caps HOLD -- the crew-railroad
mechanism is that one saturated STRONG contradiction group (+0.30)
lands in every voter's graph in lockstep, and the voters carrying the
Phase-10 Rule-1 body-proximity prior (0.70 = 0.50 +
:data:`BODY_PROXIMITY_SUSPICION_DELTA`) clamp to certain-guilt 1.00 --
in all 5 pinned railroad rows the 1.00-renderers are the impostors,
handed a false "certain guilt" row on an innocent. This ceiling, just
below the clamp, extends the 13.14 joint-cap discipline with a third
bound: with the :data:`ENV_EVIDENCE_QUALITY_LIFT` lever ON, a subject's
flag/testimony-driven transient lift renders at most
``min(lifted, prior + 0.3, max(prior, CONTRADICTION_RENDER_CEIL))`` --
no same-meeting stack can reach the 1.0 clamp. Zero conversion cost:
every 0.97 stays a §4.6 MUST-vote (the gate is 0.60). The ``max(prior,
...)`` term is the first-hand-conclusive exemption -- a witnessed
kill/vent pin (or any standing prior already at the clamp) legitimately
reads ~1.0 and is never dragged down; the ceiling bounds the LIFT,
never the prior. Applied only to the transient render channels
(:func:`apply_contradiction_rule` and the ``pre_vote`` testimony
spread); the persistent absorb is untouched, so the across-meeting 9.8
accumulator stays the allowed channel."""

# Task 14.10 evidence-quality lift lever — UNCONDITIONAL since the Task-14.12
# phase close (PR follow-up). The lever was adopted by the baseline-2 re-record,
# so — mirroring the Task-14.9 move for the four Phase-13.5 levers — it is now the
# default substrate rather than an env-gated toggle: the certain-guilt exclusion
# and self-refuted-alibi downgrade always apply. This is byte-identical to the
# baseline-2 recording (which ran the lever ON), and it lets the committed set
# reconstruct/serve under a BARE environment (no AILIBI_* export). The lever is
# stamped unconditionally ON via ``orchestrator.replay._RETIRED_ALWAYS_ON_LEVERS``;
# a stamp recording it OFF is a legacy artifact that fails loud (no cross-substrate
# replay). ``ENV_EVIDENCE_QUALITY_LIFT`` is retained (no longer read) for the stamp
# key's naming provenance and backward-compatible imports.
ENV_EVIDENCE_QUALITY_LIFT: Final[str] = "AILIBI_EVIDENCE_QUALITY_LIFT"


def evidence_quality_lift_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the Task 14.10 evidence-quality lift lever is ON — now always True.

    Retired to UNCONDITIONAL at the Task-14.12 close (the 14.9 move for the 13.5
    levers, applied to this lever after baseline 2 adopted it): the
    :data:`CONTRADICTION_RENDER_CEIL` certain-guilt exclusion and the
    self-refuted-alibi WEAK downgrade in :func:`apply_contradiction_rule`, plus
    the ceiling on the ``pre_vote`` testimony spread in
    :func:`apply_meeting_evidence_rules`, are the default substrate. The ``env``
    argument is accepted and ignored (retained so the belief-fold call sites and
    the substrate stamp read one source of truth without a signature churn).
    """

    del env  # retired: the lever is unconditional, no environment is consulted
    return True


ACCUSATION_SUSPICION_DELTA: Final[float] = 0.05
"""Accusation-driven suspicion bump (Tasks 9.8, 10.7; audit gp-1 recall).

The persistent delta a subject gains, once per meeting, for being named
by an accusation claim in that meeting's transcript. Deliberately the
smallest evidence weight in the file -- below the weak-contradiction
0.08 band and far below the §4.6 0.60 eject gate -- because a verbal
accusation is the weakest signal the belief store tracks: one meeting
lands at 0.55, well under the gate, while the same subject accused
across 2-3 meetings accumulates over it (0.60 / 0.65).

Fold timing (Task 10.7; audit gp-2 C-C-1/C-C-2). The bump moves in one
of the two halves of the meeting fold, never both: a subject with
:data:`TESTIMONY_INDEPENDENCE_BAR` or more independent voices behind
the accusation (``pre_vote_folded``) takes it in the PRE-VOTE half --
so an eyewitness with observation-backed corroboration can recruit a
plurality within the round -- while every other accused subject keeps
the POST-VOTE path, where the bump can never move the meeting it was
uttered in. The owner principle is unchanged in substance, sharpened in
wording: no single VOICE ejects -- a lone accuser or any number of bare
verbal pile-on accusers stays post-vote; only independence-gated
testimony moves early. The pre-vote fold REPLACES the post-vote bump
for that subject-meeting (the phase routing in
:func:`apply_meeting_evidence_rules`), so the per-meeting total is
+0.05 either way -- the channel is reused, not re-tuned (the 9.8
constants are frozen through Phase 10)."""

TESTIMONY_INDEPENDENCE_BAR: Final[int] = 2
"""Distinct independent voices required before testimony folds PRE-VOTE
(Task 10.7; audit gp-2 C-C-2, the fold-timing owner decision).

The two-witness independence requirement: a subject takes the pre-vote
``ACCUSATION_SUSPICION_DELTA`` only when at least this many distinct
speakers stand behind the accusation as voices --
:func:`meetings.transcript.independent_voices`, where a voice must
carry relevance-gated observation backing and an opt-in turn counts
only through a corroboration aligned with an existing accuser. The
audit's §4.2 fold-timing table is the spec: single-witness pre-vote
roughly doubled wrong-ejection games (+14 impostor meetings at 9
innocent meetings -- an owner-principle violation, REJECTED) while the
two-witness point converts at 3:1 meeting-level yield/cost; the
seed-30 m1 three-accuser pile-on is the tripwire a bare witness COUNT
cannot filter and the voice definition does."""

WITNESS_INFORM_REASON: Final[str] = "single-witness inform"
"""The single-witness inform channel marker (Task 10.15; audit
2026-06-13-1816 C-C-1 + H-4; the owner belief-spread-first decision
2026-06-14; [[project_ejection_suspicion_principle]]).

Names the crew belief-spread lever: a SINGLE observation-backed,
relevance-passing witness -- one independent voice, below the two-witness
:data:`TESTIMONY_INDEPENDENCE_BAR`
(:func:`meetings.transcript.independent_voices`) -- spreads the same
``ACCUSATION_SUSPICION_DELTA`` (+0.05) to every living listener's view of the
subject PRE-VOTE (``pre_vote_informed`` in
:func:`apply_meeting_evidence_rules`). The dominant Wave-1 residual was the
SKIP-plurality bloc (37/59 over-gate-lost-plurality meetings): the impostor
rendered over the gate for ONE witness while the listeners stayed under it, so
the equal tally's SKIP bloc won. The inform SPREADS that one witness's
first-hand testimony to the listeners so enough near-gate priors cross the
§4.6 gate and the EQUAL tally convicts on its own -- no tally reweight (the
V3 skip-halfweight was rejected by the owner decision).

It INFORMS but never EJECTS alone -- the structural owner-principle guarantee:
the +0.05 inform is strictly less than the 0.10 gate-distance from the 0.50
baseline, so a baseline listener lands at 0.55, still UNDER the 0.60 gate.
Only a listener already at >= 0.55 from their own prior
(accumulate-across-rounds) crosses on the witness's inform
(corroborate-within-round) -- never a single signal, never a bare-verbal
cascade. A bare verbal accusation carries no voice and folds nothing.

No magnitude is added (the 9.8 +0.05 unit is reused, not re-tuned): this is a
human-readable channel marker, exported so the Wave-2 attribution
(Tasks 10.16/10.17) can name the single-witness-inform channel distinctly from
the Task 10.7 two-witness fold, and read by the disjointness guard in
:func:`apply_meeting_evidence_rules`. The inform REPLACES the subject-meeting's
post-vote single-accuser bump (the phase routing below), so the per-meeting
total stays +0.05 -- never double-counted."""

TESTIMONY_SPREAD_TWO_VOICE_DELTA: Final[float] = 0.12
"""Graduated PRE-VOTE testimony spread for exactly TWO independent voices
(Task 13.7; report-phase-b-plan testimony-spread; the R1/R3 lever).

The first rung above the single-voice :data:`ACCUSATION_SUSPICION_DELTA`
inform. When :data:`TESTIMONY_INDEPENDENCE_BAR` (2) distinct independent
voices (:func:`meetings.transcript.independent_voices`) stand behind an
accusation, the PRE-VOTE bump is this delta instead of +0.05, so two
corroborating observation-backed accounts lift a 0.50 baseline listener
to 0.62 -- ACROSS the §4.6 0.60 eject gate within the round (the first
gate-cross). This is the conversion lever for the richer shared testimony
Task 13.6 elicits: two witnesses now EJECT where one only INFORMS.

TRANSIENT, not persistent. The graduated delta moves only the
vote-time suspicion graph (the ``phase="pre_vote"`` half consumed by the
ballot prompt); the persistent post-meeting absorb folds the flat
:data:`ACCUSATION_SUSPICION_DELTA` (+0.05) -- it passes no voice counts,
so a gate-crossing transient lift NEVER railroads the next round (the
"persist only +0.05" owner constraint, audit phase-b-plan line 34/74).
A single voice stays byte-identical to the pre-13.7 inform (the
no-regression pin): crew / no-witness games are unmoved."""

TESTIMONY_SPREAD_CAP_DELTA: Final[float] = 0.15
"""Graduated PRE-VOTE testimony-spread CAP for THREE-OR-MORE independent
voices (Task 13.7; report-phase-b-plan testimony-spread).

Three or more independent voices behind an accusation lift the PRE-VOTE
bump to this ceiling (0.50 -> 0.65) -- a deliberately small margin over
the two-voice :data:`TESTIMONY_SPREAD_TWO_VOICE_DELTA` so a large opt-in
pile-on cannot run the prior away. The spread is bounded, mirroring the
:data:`MEETING_CONTRADICTION_LIFT_CAP` discipline on the contradiction
channel: more corroboration raises confidence past the gate but the
magnitude is capped, never linear in voice count. Like the two-voice
rung this is TRANSIENT pre-vote only; the persistent per-meeting total
stays :data:`ACCUSATION_SUSPICION_DELTA`."""


def graduated_spread_delta(voice_count: int) -> float:
    """The graduated PRE-VOTE bump for ``voice_count`` independent voices.

    The graduated testimony-spread curve keyed on the
    :func:`meetings.transcript.independent_voices` COUNT (Task 13.7):

    * 1 voice (below :data:`TESTIMONY_INDEPENDENCE_BAR`) ->
      :data:`ACCUSATION_SUSPICION_DELTA` (+0.05) -- BYTE-IDENTICAL to the
      pre-13.7 single-witness inform, the no-regression pin;
    * exactly 2 voices (the bar) -> :data:`TESTIMONY_SPREAD_TWO_VOICE_DELTA`
      (+0.12) -- the first §4.6 gate-cross;
    * 3+ voices -> :data:`TESTIMONY_SPREAD_CAP_DELTA` (+0.15) -- capped.

    Pure mapping; the persistence decoupling lives in
    :func:`apply_meeting_evidence_rules` (only the ``pre_vote`` half reads
    this curve; the persistent composed fold always folds the flat +0.05).
    """

    if voice_count > TESTIMONY_INDEPENDENCE_BAR:
        return TESTIMONY_SPREAD_CAP_DELTA
    if voice_count == TESTIMONY_INDEPENDENCE_BAR:
        return TESTIMONY_SPREAD_TWO_VOICE_DELTA
    return ACCUSATION_SUSPICION_DELTA


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
corroboration, not the bump, has the last word).

Same-phase movement (Task 10.7; audit gp-2 C-C-3 "corroborations must
move at the SAME phase as accusations"): in the two-half fold protocol
this delta belongs to the PRE-VOTE half alongside the two-witness
testimony bumps -- a defended subject is cleared before ballots, not a
meeting late (the seed-28 shape: three live corroborations of the
wrongly-accused arrived structurally post-vote). Within the pre-vote
half the within-meeting order is unchanged: folded bumps first, then
corroborations, so the clamp-ceiling last word stays with the
corroboration.

Relevance-gated input (Task 10.6; audit gp-2 C-C-3). The ``corroborated``
set this delta is applied over is built EXCLUSIVELY through the §6.3
Rule-3 relevance gate, :func:`meetings.transcript.is_relevant_sighting`
-- both halves of the evidence: detector-derived containment pairs are
gated inside :func:`meetings.transcript.detect_corroborations`, and
claim-stated :class:`~meetings.schemas.CorroborationClaim` vouches are
gated by :func:`meetings.manager.extract_belief_evidence` (the only
producer of the fold's ``corroborated`` argument). Spawn-window
(tick 0-1) and kill-scene vouches are evidentially empty -- on the
Wave-0 set they cancelled 52% of impostor accusation flow in-meeting,
the C-C-3 asymmetry: the +0.05 accusation side dedupes per meeting
while the -0.05 side needed only one sloppy vouch. The MAGNITUDE is
untouched: the gate changes which subjects arrive here, never how far
they move."""

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

# The action label the observation layer stamps on a ``PlayerView`` when the
# observer *witnesses* a player committing a kill (observation/service.py
# ``_observed_actions_for_agent``, ~:351 -- a witness-gated ``KilledEvent``).
# Seeing the kill is the player-attributed signal the Task 13.5.3 witness rule
# keys on; it is never mirrored onto a crewmate-visible channel for a kill the
# observer did NOT witness (the leak test), so a ``PlayerView`` carrying it is
# always a first-hand, witness-permitted view.
OBSERVED_KILL_ACTION: Final[str] = "kill"

# The two deterministic halves of the per-meeting belief fold (Task 10.7;
# audit gp-2). ``pre_vote`` runs BEFORE ballots: two-witness testimony
# bumps plus this meeting's relevance-gated corroborations, both
# directions symmetric, never Rule-5 decay. ``post_vote`` runs after
# resolution: the single-voice accused-bumps plus Rule-5 decay, exactly
# the pre-10.7 path. ``None`` (the default, and the standing
# ``agents.memory.store.absorb_meeting_evidence`` call shape) composes
# both halves in one call -- byte-identical to the pre-10.7 fold, which
# is what keeps the persistent per-meeting total for a folded subject
# equal to the unfolded total (the double-fold guard).
MeetingFoldPhase: TypeAlias = Literal["pre_vote", "post_vote"]


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
    """Immutable snapshot of beliefs about a single other player.

    ``alibis`` is DEAD in production today (2026-06-25 memory-pipeline
    diagnosis, workflow `wg54kfoxy`): its only writer is :meth:`BeliefState.record_alibi`,
    which has zero non-test callers, and the §6.6 memory render
    (``agents/memory/store.py``) reads this field nowhere -- testimony reaches
    beliefs only as a scalar suspicion delta, never as stored alibi content. It
    is scaffolding, NOT dead code to delete: Wave C (Task 13.5.2,
    testimony-as-content) is the lever that wires it (the ``"reported"``
    provenance write path → ``record_alibi`` → render).
    """

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
        """Append an alibi claim to ``claim.player_id``'s belief row.

        DEAD in production today (2026-06-25 memory-pipeline diagnosis,
        workflow `wg54kfoxy`): this method has zero non-test callers, so no
        live path writes the ``PlayerBelief.alibis`` list, and the §6.6 render
        does not read it -- testimony currently reaches beliefs only as a
        scalar suspicion delta. Kept as scaffolding (NOT dead code to delete):
        Wave C (Task 13.5.2, testimony-as-content) wires this as the persistence
        target for the ``"reported"`` provenance write path.
        """

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

    def drop_player(self, player_id: PlayerId) -> None:
        """Remove ``player_id``'s belief row entirely; no-op when unknown.

        The roster purge primitive (Task 10.2; audit gp-6 C-C-8): a row
        whose id is not a real player -- a phantom subject materialised
        before the roster filters existed, or by a hypothetical future
        write path they do not cover -- is deleted by
        :func:`apply_meeting_evidence_rules` rather than left to decay,
        so the belief store carries roster ids only after any
        post-meeting fold. Deliberately a full-row removal: a non-player
        "row" holds no evidence about anyone, so there is nothing to
        preserve.
        """

        self._beliefs.pop(player_id, None)

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

    Witnessed kill (``WITNESSED_KILL_SUSPICION_DELTA``, Task 13.5.3 -- the
    2026-06-25 eyewitness-strength decision). A kill is even more conclusive
    than a vent (only impostors kill, and this is the act itself), so a
    ``PlayerView`` carrying ``action == "kill"`` -- the witness-gated kill stamp
    (observation/service.py) -- lifts the killer's suspicion by the largest
    delta in the file, pinning to the ~1.0 clamp (near-certain, over the §4.6
    gate). It mirrors the vent branch with ONE added guard: the §4.7
    team-internal firewall. An impostor frequently co-locates with a teammate's
    kill, so a killer in ``observation.self_state.fellow_impostor_ids`` is
    SKIPPED (the vent branch needs no such guard -- a crew never vents to be
    witnessed by a teammate, but a teammate kill is routine). The witness
    reasons from its OWN first-hand view -- unforgeable, no corroboration -- and
    because this runs at perception (via ``ingest_packet``), the bump persists
    into the stored :class:`BeliefState` the meeting suspicion graph reads.
    Unconditional since Task 14.9 (the adopted 13.5.3 lever is the default
    substrate; the ``AILIBI_WITNESSED_KILL_EVIDENCE`` gate is retired).

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

    fellow_impostor_ids = frozenset(observation.self_state.fellow_impostor_ids)

    for player in observation.visible_players:
        if player.action == OBSERVED_VENT_ACTION:
            result.adjust_suspicion(player.id, delta=VENTING_SUSPICION_DELTA)
        elif (
            player.action == OBSERVED_KILL_ACTION
            and player.id not in fellow_impostor_ids
        ):
            result.adjust_suspicion(player.id, delta=WITNESSED_KILL_SUSPICION_DELTA)

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
    *,
    transcript: MeetingTranscript | None = None,
    env: Mapping[str, str] | None = None,
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

    New STRONG inferential classes (Task 13.5; report-phase-b-plan
    belief-band). The 13.3 genuinely-independent cross-speaker
    ``alibi_conflict`` and the 13.4 ``alibi_vs_physical`` route through this
    SAME marker-keyed handling -- no new branch (the Task 10.10 precedent: a
    new weak reason or kind needs no logic change here, only the marker).
    A cross-speaker conflict and the 13.4 TWO-SOURCE conjunction (>= the
    detector's ``PHYSICAL_CONTRADICTION_MIN_VOICES`` distinct co-presence
    voices contradicting an uncorroborated self-alibi) carry no weak marker,
    so :func:`is_weak_contradiction` is ``False`` and they take the full
    ``CONTRADICTION_SUSPICION_DELTA``. A LONE 13.4 reconstruction atom -- a
    single contradicting voice, the detector's ``WEAK_REASON_LONE_PHYSICAL``
    marker -- is weak-classified and takes the sub-gate
    ``WEAK_CONTRADICTION_SUSPICION_DELTA``: it INFORMS but cannot eject a
    baseline listener alone (0.5 + 0.08 = 0.58, strictly under both the 0.60
    §4.6 gate and the 0.10 gate-distance the single-witness inform's +0.05
    also respects). Keeping full-0.3 strictly behind the two-source
    conjunction is load-bearing -- a lone atom reaching 0.60 alone re-opens
    the single-signal wrong-ejection path the weak delta closed (the 13/13
    baseline). The 13.4 conjunction emits one flag per contradicting
    placement, all sharing the subject's OWN alibi-claim event, so the
    per-(subject, claim) dedup below folds them onto one key (one 0.3, never
    N x 0.3) within the ``MEETING_CONTRADICTION_LIFT_CAP``.

    Kill-scene ``alibi_vs_physical`` (Task 13.5.3) routes through this SAME
    marker-keyed handling -- again no new branch. A LONE kill-scene placement
    (the accused placed at the body's room within the kill window by ONE
    independent voice, contradicting an alibi elsewhere) carries the detector's
    :data:`meetings.transcript.WEAK_REASON_KILL_SCENE` marker, so
    :func:`is_weak_contradiction` is ``True`` and it takes the sub-gate
    ``WEAK_CONTRADICTION_SUSPICION_DELTA`` -- it INFORMS but cannot eject a
    baseline listener alone (the owner-LOCKED STRICT strictness: no single
    forgeable kill-accusation railroads a crewmate). The placement crosses to
    the full ``CONTRADICTION_SUSPICION_DELTA`` only under the two-source
    conjunction (>= ``PHYSICAL_CONTRADICTION_MIN_VOICES`` distinct contradicting
    voices, kill-scene or not), exactly like the 13.4 atom.

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

    Evidence-quality bounds (Task 14.10; audit 2026-07-01 §3a). Behind the
    default-OFF :func:`evidence_quality_lift_enabled` lever (``env``-resolved,
    defaulting to the process environment -- the retired 13.5 pattern), two
    MEASURED bounds tighten the lift; OFF is byte-identical to the pre-14.10
    fold:

    * **Self-refuted-alibi downgrade (bound 2).** A flag whose referenced
      alibi claim is self-refuted -- the subject's OWN same-turn
      ``completed_task`` observation places them in a contradictory room at a
      tick inside the alibi span
      (:func:`meetings.transcript.self_refuted_alibi_claim_ids`, derived from
      ``transcript`` at fold time) -- contributes the WEAK delta (0.08), not
      STRONG (0.30): testimony the speaker disproved within their own turn is
      sloppy, not probative. Measured on baseline 1: the class costs 0/57
      flagged impostor ejections while keeping the seed-16/44 railroad
      rosters sub-gate (0.50 + 0.08 = 0.58 < 0.60). ``transcript=None`` (the
      analysis-caller default) applies no downgrade -- the production vote
      path threads the meeting transcript.
    * **Certain-guilt exclusion (bound 1).** A subject's lifted suspicion is
      additionally bounded by ``max(prior, CONTRADICTION_RENDER_CEIL)``, so
      flag-driven lift can never reach the 1.0 clamp (0.70 body-proximity
      prior + 0.30 now renders ~0.97, still a §4.6 MUST-vote) while a
      first-hand conclusive prior already at the clamp -- the witnessed-kill
      pin -- keeps rendering 1.0 (the ``max`` exemption; the ceiling bounds
      the lift, never the prior).

    The audit REJECTED witness-count weighting (an anti-signal: honest greedy
    alibis attract MORE independent refuting witnesses) and >=2-group gating
    (over-damps: 54/57 flagged impostor ejections ride exactly ONE group) --
    neither is implemented, by measurement, not oversight.

    Subjects are processed in sorted order so the resulting state is
    deterministic regardless of input ordering -- a precondition for
    replay-stable belief snapshots.
    """

    lift_enabled = evidence_quality_lift_enabled(env)
    self_refuted: frozenset[str] = frozenset()
    if lift_enabled and transcript is not None:
        self_refuted = self_refuted_alibi_claim_ids(transcript)

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
        # Task 14.10 bound 2: a flag riding a self-refuted alibi claim is
        # downgraded to the WEAK delta. ``self_refuted`` holds claim event
        # ids only, so an ``:obs:``-side id can never match; the flag is
        # still recorded on the inconsistency list below (§5.4 "flags are
        # information" -- the downgrade is about the score, never the flag).
        if self_refuted and (
            contradiction.event_a_id in self_refuted
            or contradiction.event_b_id in self_refuted
        ):
            delta = WEAK_CONTRADICTION_SUSPICION_DELTA
        lift_key = contradiction_lift_key(contradiction)
        for subject in sorted(contradiction.subjects):
            result.record_contradiction(subject, belief_ref)
            group = (subject, lift_key)
            lift_groups[group] = max(lift_groups.get(group, 0.0), delta)

    lift_by_subject: dict[PlayerId, float] = {}
    for (subject, _), delta in lift_groups.items():
        lift_by_subject[subject] = lift_by_subject.get(subject, 0.0) + delta
    for subject in sorted(lift_by_subject):
        capped = min(lift_by_subject[subject], MEETING_CONTRADICTION_LIFT_CAP)
        if lift_enabled:
            # Task 14.10 bound 1: never lift a subject INTO the 1.0 clamp --
            # the render ceiling caps the delta so the result stays at or
            # under max(prior, CONTRADICTION_RENDER_CEIL). A prior already at
            # the clamp (the witnessed-kill pin) is exempt by the max: its
            # ceiling equals the prior, so the value holds rather than drops.
            prior = result.view(subject).suspicion
            capped = min(capped, max(prior, CONTRADICTION_RENDER_CEIL) - prior)
        result.adjust_suspicion(subject, delta=capped)
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
    phase: MeetingFoldPhase | None = None,
    pre_vote_folded: AbstractSet[PlayerId] = frozenset(),
    pre_vote_informed: AbstractSet[PlayerId] = frozenset(),
    pre_vote_voice_counts: Mapping[PlayerId, int] | None = None,
    env: Mapping[str, str] | None = None,
) -> BeliefState:
    """Fold one meeting's public evidence into persistent beliefs (Tasks 9.8, 10.7, 10.15).

    Pure: returns a new :class:`BeliefState`; ``beliefs`` is not mutated.
    Runs on every living agent's stored beliefs (DESIGN.md §4.4 step 4's
    belief-update hook, rule-based), so the suspicion it writes carries
    forward into the NEXT meeting's suspicion graph -- unlike Rule 2's
    vote-time contradiction lift, which stays transient inside the
    meeting that detected the flag. Three rules:

    * **Accusation bump** (``ACCUSATION_SUSPICION_DELTA``, audit gp-1
      recall): every subject in ``accused`` -- the deduplicated set of
      players named by an accusation claim in the meeting -- gains the
      small delta once. The caller deduplicates per meeting, so a
      pile-on of accusers is one meeting-level "was accused" event. A
      subject with NO independent voice (a bare verbal accusation) takes
      the bump in the post-vote half, where one round can never eject
      through it; a ``pre_vote_folded`` (two-witness) OR
      ``pre_vote_informed`` (single-witness, Task 10.15) subject takes
      the identical bump in the pre-vote half instead (see *Fold phases*
      below).
    * **Rule 3 corroboration** (``CORROBORATION_SUSPICION_DELTA``):
      every subject in ``corroborated`` loses the mirror delta --
      a public vouch is the collective clear. The set arrives
      relevance-gated (Task 10.6): every producer routes both
      claim-stated and detector-derived corroborations through
      :func:`meetings.transcript.is_relevant_sighting` before this
      seam, so a spawn-window or kill-scene vouch never reaches the
      delta (see ``CORROBORATION_SUSPICION_DELTA``'s docstring for the
      gate's two homes).
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
    (``agents.memory.store._known_roster_ids``) -- two filters run, so
    the RETURNED state carries roster ids only:

    * input side, like the teammate guard: an evidence subject outside
      the roster is dropped from all three sets -- a hallucinated
      structural id (a game id such as ``"headless-seed-9"``, a turn id,
      a free-text phrase) never materialises a belief row, never bumps
      or lowers a score, and never counts as reinforced;
    * output side, the purge: a PRE-EXISTING non-roster row (one
      materialised before these filters existed, or by a hypothetical
      future write path they do not cover) is dropped from the returned
      state via :meth:`BeliefState.drop_player` rather than left to
      decay -- so the store self-heals at every fold and every
      downstream snapshot (the §6.6 render, the next meeting's
      suspicion graph) is roster-only by construction.

    This is the defense-in-depth backstop behind the Task 10.2
    meeting-layer chokepoint
    (``meetings.manager._drop_non_roster_claims``): even if a garbage
    subject slips through a future claim type, the belief store -- and
    therefore every prompt surface built from it -- stays roster-only.
    ``roster=None`` (the default) applies neither filter, preserving
    the pure-math call shape for callers without a roster channel.

    **Fold phases (Task 10.7; audit gp-2 C-C-1/C-C-2).** One fold
    function, a ``phase`` argument, called twice per meeting -- never
    duplicated logic. ``pre_vote_folded`` names the subjects with
    :data:`TESTIMONY_INDEPENDENCE_BAR`+ independent voices and
    ``pre_vote_informed`` the subjects with exactly one
    (:data:`WITNESS_INFORM_REASON`, Task 10.15 -- the single-witness
    inform), both from :func:`meetings.transcript.independent_voices`,
    derived by ``meetings.manager.derive_belief_evidence`` and carried on
    the meeting context (this store never knows about phases beyond the
    routing below). Each must be a subset of ``accused`` and the two must
    be DISJOINT (fail-loud otherwise: a folded/informed subject nobody
    accused, or a subject in both bands, is caller drift). The two bands
    take the IDENTICAL pre-vote bump -- the inform is the single-witness
    extension of the fold, at the same +0.05, in the same pre-vote half
    (audit 2026-06-13 C-C-1: belief-spread, not a tally reweight):

    * ``phase="pre_vote"`` -- the half the meeting manager applies to
      every living listener BEFORE ballots: the accusation bump for
      ``pre_vote_folded`` AND ``pre_vote_informed`` subjects, plus ALL of
      this meeting's relevance-gated corroborations (same-phase movement,
      both directions symmetric -- a defended subject is cleared before
      ballots). Never decays: Rule 5 is the post-vote half's.
    * ``phase="post_vote"`` -- the half that runs after resolution,
      exactly the pre-10.7 path for everything it touches: the
      accusation bump for every accused subject in NEITHER pre-vote band
      (the pre-vote fold/inform REPLACES the post-vote bump for that
      subject-meeting -- the double-fold guard), no corroboration deltas
      (they moved pre-vote), and Rule-5 decay. The decay exemption still
      reads the FULL evidence -- a folded, informed, or corroborated
      subject got new evidence this meeting and must not decay -- so
      ``accused`` / ``corroborated`` are passed whole to both phases,
      never pre-partitioned by the caller.
    * ``phase=None`` (default) -- both halves composed in one call: the
      pre-10.7 behaviour, byte-for-byte, and the call shape of the
      standing post-meeting absorb
      (:func:`agents.memory.store.absorb_meeting_evidence`). Because
      the composition bumps each accused subject exactly once, the
      persistent per-meeting total for a folded/informed subject equals
      the unfolded total by construction -- the inform changes WHEN the
      listener sees the +0.05 (pre-vote, so it can recruit a plurality
      this round), never how much persists. (At a clamp boundary the
      composed call keeps the pre-10.7 bump-then-corroborate order;
      the split phases order a single-voice bump after the pre-vote
      corroborations -- interior values are order-independent.)

    **Graduated testimony spread (Task 13.7; report-phase-b-plan
    testimony-spread; the R1/R3 lever).** ``pre_vote_voice_counts`` maps a
    voiced subject to its :func:`meetings.transcript.independent_voices`
    COUNT. When supplied, the ``phase="pre_vote"`` accusation bump is
    GRADUATED by that count via :func:`graduated_spread_delta` -- 1 voice
    keeps the flat :data:`ACCUSATION_SUSPICION_DELTA` (+0.05, byte-identical
    to the pre-13.7 inform), 2 voices take
    :data:`TESTIMONY_SPREAD_TWO_VOICE_DELTA` (+0.12, the first §4.6
    gate-cross), 3+ take :data:`TESTIMONY_SPREAD_CAP_DELTA` (+0.15, capped).
    The graduation is consulted ONLY in the ``pre_vote`` half, so it lifts
    the transient vote-time graph the ballot reads; the ``post_vote`` and
    composed (``None``) halves ALWAYS fold the flat +0.05 regardless of any
    counts, which is the structural "persist only +0.05" guarantee -- the
    persistent post-meeting absorb passes no counts, so a gate-crossing
    transient lift can never railroad the next round (audit phase-b-plan
    line 34/74). A subject in the pre-vote bump set with NO count entry --
    every existing caller, which passes no counts -- takes the flat +0.05,
    so the channel is byte-identical until a caller threads the count in.
    Each count key must be a voiced subject (in ``pre_vote_folded`` or
    ``pre_vote_informed``); a count for an un-voiced subject is caller
    drift and fails loud (AGENTS.md "no silent fallbacks").

    The impostor teammate guard applies to both new channels exactly as
    to the old: ``pre_vote_folded`` and ``pre_vote_informed`` are
    intersected with the teammate-and-self-filtered bump set, so an
    impostor listener never takes a pre-vote bump against a fellow
    impostor.

    **Certain-guilt exclusion on the spread (Task 14.10 bound 1; audit
    2026-07-01 §3a).** With the default-OFF
    :func:`evidence_quality_lift_enabled` lever ON (``env``-resolved,
    defaulting to the process environment), the ``pre_vote`` bump is
    additionally bounded so a bumped subject renders at or under
    ``max(prior, CONTRADICTION_RENDER_CEIL)`` -- testimony-driven transient
    lift can never reach the 1.0 clamp, mirroring the contradiction-lift
    ceiling in :func:`apply_contradiction_rule` (the two channels stack on
    one graph at vote time, so both must respect the render bound). ONLY the
    ``pre_vote`` half is ceilinged: the ``post_vote`` and composed halves are
    the persistent absorb, whose flat +0.05 across-meeting accumulation is
    the legitimate 9.8 channel and stays untouched (lever ON or OFF). OFF is
    byte-identical to the pre-14.10 fold.

    All subject sets are processed in sorted order; the result is a
    deterministic function of its arguments (replay-stable).
    """

    unknown_folded = set(pre_vote_folded) - set(accused)
    if unknown_folded:
        raise ValueError(
            "pre_vote_folded must be a subset of accused; "
            f"unknown folded subjects: {sorted(unknown_folded)}"
        )
    unknown_informed = set(pre_vote_informed) - set(accused)
    if unknown_informed:
        raise ValueError(
            "pre_vote_informed must be a subset of accused; "
            f"unknown informed subjects: {sorted(unknown_informed)}"
        )
    both_bands = set(pre_vote_folded) & set(pre_vote_informed)
    if both_bands:
        raise ValueError(
            "pre_vote_folded and pre_vote_informed must be disjoint "
            f"(the fold is the two-witness band, {WITNESS_INFORM_REASON!r} the "
            f"single-witness one); subjects in both: {sorted(both_bands)}"
        )
    voice_counts = dict(pre_vote_voice_counts) if pre_vote_voice_counts else {}
    if voice_counts:
        voiced = set(pre_vote_folded) | set(pre_vote_informed)
        unknown_counts = set(voice_counts) - voiced
        if unknown_counts:
            raise ValueError(
                "pre_vote_voice_counts keys must be voiced subjects "
                "(in pre_vote_folded or pre_vote_informed); unknown count "
                f"subjects: {sorted(unknown_counts)}"
            )
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
    # Phase routing (Tasks 10.7, 10.15). The teammate / own-id / roster
    # guards above already shaped ``bumped``, so intersecting the
    # folded/informed sets with it applies every guard to both testimony
    # channels for free. The two-witness fold and the single-witness inform
    # share the pre-vote half; together they REPLACE the post-vote bump for
    # their subjects (the double-fold guard). The magnitude is graduated by
    # voice count in the pre-vote half (Task 13.7) but the per-meeting
    # PERSISTED total stays the flat +0.05 -- only the pre-vote half reads
    # ``voice_counts`` below.
    pre_vote_bumped = bumped & (set(pre_vote_folded) | set(pre_vote_informed))
    if phase == "pre_vote":
        bump_now = pre_vote_bumped
        lower_now = lowered
        decay_now = False
    elif phase == "post_vote":
        bump_now = bumped - pre_vote_bumped
        lower_now = set()
        decay_now = True
    else:
        bump_now = bumped
        lower_now = lowered
        decay_now = True

    result = beliefs.copy()
    if roster is not None:
        for player_id in result.known_players():
            if player_id not in roster:
                result.drop_player(player_id)
    # Task 14.10 bound 1: the render ceiling applies to the TRANSIENT
    # pre-vote half only (the graph the ballot reads); the persistent
    # halves never consult the lever, so the 9.8 across-meeting
    # accumulator -- and the OFF-branch byte-identity -- are untouched.
    ceil_lift = phase == "pre_vote" and evidence_quality_lift_enabled(env)
    for subject in sorted(bump_now):
        # Graduated testimony spread (Task 13.7): the PRE-VOTE half lifts a
        # voiced subject by its voice-count delta (1->+0.05, 2->+0.12,
        # 3+->+0.15); every other path -- the persistent composed fold, the
        # post-vote half, and any pre-vote subject with no threaded count --
        # keeps the flat +0.05, which is what bounds the persisted lift.
        if phase == "pre_vote" and subject in voice_counts:
            delta = graduated_spread_delta(voice_counts[subject])
        else:
            delta = ACCUSATION_SUSPICION_DELTA
        if ceil_lift:
            # Never bump a subject INTO the 1.0 clamp (mirrors the
            # contradiction-lift ceiling); a prior already at the clamp is
            # exempt via the max -- the ceiling bounds the lift, not the prior.
            prior = result.view(subject).suspicion
            delta = min(delta, max(prior, CONTRADICTION_RENDER_CEIL) - prior)
        result.adjust_suspicion(subject, delta=delta)
    for subject in sorted(lower_now):
        result.adjust_suspicion(subject, delta=-CORROBORATION_SUSPICION_DELTA)
    if decay_now:
        for player_id in sorted(result.known_players()):
            if player_id == own_id or player_id in reinforced:
                continue
            result.decay_suspicion(player_id, rate=MEETING_SUSPICION_DECAY_RATE)
    return result


__all__ = [
    "ACCUSATION_SUSPICION_DELTA",
    "BODY_PROXIMITY_SUSPICION_DELTA",
    "BODY_PROXIMITY_WINDOW_TICKS",
    "CONTRADICTION_RENDER_CEIL",
    "CONTRADICTION_SUSPICION_DELTA",
    "CORROBORATION_SUSPICION_DELTA",
    "ENV_EVIDENCE_QUALITY_LIFT",
    "MEETING_CONTRADICTION_LIFT_CAP",
    "MEETING_SUSPICION_DECAY_RATE",
    "OBSERVED_KILL_ACTION",
    "OBSERVED_VENT_ACTION",
    "TESTIMONY_INDEPENDENCE_BAR",
    "TESTIMONY_SPREAD_CAP_DELTA",
    "TESTIMONY_SPREAD_TWO_VOICE_DELTA",
    "VENTING_SUSPICION_DELTA",
    "WEAK_CONTRADICTION_SUSPICION_DELTA",
    "WITNESS_INFORM_REASON",
    "WITNESSED_KILL_SUSPICION_DELTA",
    "AlibiClaim",
    "BeliefState",
    "ContradictionRef",
    "MeetingFoldPhase",
    "PlayerBelief",
    "apply_contradiction_rule",
    "apply_meeting_evidence_rules",
    "apply_observation_rules",
    "evidence_quality_lift_enabled",
    "graduated_spread_delta",
]
