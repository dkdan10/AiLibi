"""Suspicion-provenance decomposition pins (Task 16.3).

The belief-store half of the Task 16.3 foundation (audits/post-phase-14-Voice-
and-Judgment-planning.md §3.2, the J1 foundation): every belief row carries a
:class:`~agents.memory.beliefs.SuspicionProvenance` recorded BESIDE the
``suspicion`` scalar, accumulated at each write site rather than re-derived
after the fold (the §3.2 C4 catch). These tests pin, at the belief layer:

* the sum-to-scalar invariant ``_DEFAULT_SUSPICION + provenance.total ==
  suspicion`` (within :data:`SUSPICION_PROVENANCE_ATOL`) across arbitrary write /
  decay / seed sequences, INCLUDING clamp saturation at 0 and 1;
* source tagging at every write site -- vent/kill -> ``kill_or_vent_pin``, body
  proximity -> ``body_proximity``, contradiction -> ``flag_lift`` (the capped,
  APPLIED delta), the pre-vote spread -> ``testimony_spread``, the persistent
  accusation bump and its corroboration mirror -> ``accusation_carry``, and any
  untagged / unknown-seeded movement -> ``unattributed``;
* the HARD/SOFT cross-meeting carry (DoD bullet 2): a grounded hard pin from
  meeting 1 stays a ``carried_hard`` component (never ``carried_soft``) at
  meeting 2+, through decay and successive composed folds;
* the meeting-boundary ROLL semantics: the persistent (``post_vote`` / composed
  ``None``) halves roll, the transient ``pre_vote`` half never does;
* exact-float scalar bit-identity -- the arithmetic is untouched, so the scalar
  values are the pre-16.3 constants to the ULP.

The manager pre-vote re-render threading (``_suspicion_graph_with_contradictions``
seeding provenance, the emitted ``SuspicionEntry`` provenance fields) is Stage 3
of Task 16.3 and pinned there; this module stays at the belief layer, so the
carry fixture exercises the persistent absorb path
(:func:`apply_observation_rules` + composed :func:`apply_meeting_evidence_rules`
folds) rather than the manager's transient graph.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from agents.memory.beliefs import (
    ACCUSATION_SUSPICION_DELTA,
    BODY_PROXIMITY_SUSPICION_DELTA,
    CONTRADICTION_SUSPICION_DELTA,
    CORROBORATION_SUSPICION_DELTA,
    MEETING_SUSPICION_DECAY_RATE,
    SUSPICION_PROVENANCE_ATOL,
    TESTIMONY_SPREAD_TWO_VOICE_DELTA,
    BeliefState,
    SuspicionProvenance,
    VENTING_SUSPICION_DELTA,
    WITNESSED_KILL_SUSPICION_DELTA,
    apply_contradiction_rule,
    apply_meeting_evidence_rules,
    apply_observation_rules,
)
from meetings.schemas import ContradictionRef as MeetingContradictionRef
from observation.packet import (
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)

_DEFAULT_SUSPICION = 0.5


def _packet(
    *,
    tick: int,
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
) -> ObservationPacket:
    return ObservationPacket(
        tick=tick,
        agent_id="observer",
        self_state=SelfView(room="R", role="CREWMATE", pending_task_id=None),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


def _kill_packet(*, killer: str, tick: int = 10) -> ObservationPacket:
    """A packet carrying one witness-gated kill stamp (no fellow impostors)."""

    return ObservationPacket(
        tick=tick,
        agent_id="observer",
        self_state=SelfView(room="R", role="CREWMATE", pending_task_id=None),
        visible_players=(PlayerView(id=killer, room="R", action="kill"),),
        visible_bodies=(),
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=1,
            task_completion_percent=0.0,
            sabotage_active=False,
            sabotage_kind=None,
        ),
        cooldown=None,
    )


def _strong_flag(*, subject: str) -> MeetingContradictionRef:
    """A STRONG (non-weak) contradiction flag naming one subject.

    Kind ``alibi_conflict`` with a clean description (no weak marker), so
    :func:`meetings.transcript.is_weak_contradiction` is ``False`` and
    :func:`apply_contradiction_rule` takes the full
    :data:`CONTRADICTION_SUSPICION_DELTA`.
    """

    return MeetingContradictionRef(
        contradiction_id=f"contra:alibi_conflict:{subject}",
        kind="alibi_conflict",
        event_a_id="turn:m-1:turn-1:claim:0",
        event_b_id="turn:m-1:turn-2:claim:0",
        subjects=(subject,),
        description=f"{subject} placed in two rooms at once.",
    )


def _invariant_error(state: BeliefState, player_id: str) -> float:
    """Absolute error in ``_DEFAULT_SUSPICION + provenance.total == suspicion``."""

    belief = state.view(player_id)
    return abs((_DEFAULT_SUSPICION + belief.provenance.total) - belief.suspicion)


def _assert_invariant(state: BeliefState) -> None:
    """Every known row satisfies the sum invariant within tolerance."""

    for player_id in state.known_players():
        assert _invariant_error(state, player_id) <= SUSPICION_PROVENANCE_ATOL


# --- (1) sum-to-scalar invariant, incl. clamp saturation -------------------


class TestSumToScalarInvariant:
    """The module contract: ``0.5 + provenance.total == suspicion`` everywhere.

    Holds unconditionally -- at every write, after decay's proportional scaling,
    after a seed's residual reconciliation, and at both clamp saturations (0 and
    1), where the APPLIED delta (not the requested one) is what the decomposition
    records.
    """

    def test_saturation_at_ceiling_records_only_applied_delta(self) -> None:
        # A +2.0 request from 0.5 clamps to 1.0; only the +0.5 that landed is
        # attributed, so the invariant holds at the ceiling.
        state = BeliefState()
        state.adjust_suspicion("s", delta=2.0, source="flag_lift")

        belief = state.view("s")
        assert belief.suspicion == 1.0
        assert belief.provenance.flag_lift == pytest.approx(0.5)
        assert belief.provenance.total == pytest.approx(0.5)
        _assert_invariant(state)

    def test_saturation_at_floor_records_only_applied_delta(self) -> None:
        state = BeliefState()
        state.adjust_suspicion("s", delta=-2.0, source="accusation_carry")

        belief = state.view("s")
        assert belief.suspicion == 0.0
        assert belief.provenance.accusation_carry == pytest.approx(-0.5)
        _assert_invariant(state)

    @settings(max_examples=300)
    @given(
        ops=st.lists(
            st.one_of(
                st.tuples(
                    st.just("adjust"),
                    st.floats(min_value=-1.5, max_value=1.5),
                    st.sampled_from(
                        (
                            "flag_lift",
                            "body_proximity",
                            "kill_or_vent_pin",
                            "testimony_spread",
                            "accusation_carry",
                            "carried_hard",
                            "carried_soft",
                            "unattributed",
                            None,
                        )
                    ),
                ),
                st.tuples(
                    st.just("decay"),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.none(),
                ),
                st.tuples(
                    st.just("seed"),
                    st.floats(min_value=-0.5, max_value=1.5),
                    st.none(),
                ),
            ),
            min_size=1,
            max_size=25,
        )
    )
    def test_invariant_holds_across_arbitrary_op_sequences(
        self, ops: list[tuple[str, float, str | None]]
    ) -> None:
        # Arbitrary interleavings of tagged writes (any source, incl. untagged),
        # decays toward the 0.5 prior, and reseeds -- the invariant holds after
        # EVERY op, with saturation reached whenever a delta runs past a clamp.
        state = BeliefState()
        for kind, value, source in ops:
            if kind == "adjust":
                state.adjust_suspicion("s", delta=value, source=source)  # type: ignore[arg-type]
            elif kind == "decay":
                state.decay_suspicion("s", rate=value)
            else:
                state.seed_player("s", suspicion=value, trust=0.5)
            _assert_invariant(state)

    def test_invariant_holds_through_the_persistent_fold(self) -> None:
        # The composed absorb path (accusation bump + corroboration + decay +
        # roll) keeps the invariant on every emitted row.
        state = BeliefState()
        state.seed_player("a", suspicion=0.7, trust=0.5)
        state.seed_player("b", suspicion=0.55, trust=0.5)
        folded = apply_meeting_evidence_rules(
            state,
            own_id="observer",
            accused=["a"],
            corroborated=["b"],
        )
        _assert_invariant(folded)


# --- (2) source tagging at every write site --------------------------------


class TestSourceTagging:
    """Each write site attributes its APPLIED delta to the correct source."""

    def test_vent_tags_kill_or_vent_pin(self) -> None:
        result = apply_observation_rules(
            BeliefState(),
            observation=_packet(
                tick=10,
                visible_players=(PlayerView(id="v", room="R", action="vent"),),
            ),
            previous_visible_bodies=set(),
            recent_co_presence={},
        )
        prov = result.view("v").provenance
        assert prov.kill_or_vent_pin == pytest.approx(VENTING_SUSPICION_DELTA)
        assert prov.total == pytest.approx(VENTING_SUSPICION_DELTA)
        _assert_invariant(result)

    def test_kill_tags_kill_or_vent_pin_with_clamped_applied_delta(self) -> None:
        # The +1.0 kill delta from 0.5 clamps to 1.0, so the pin records only the
        # +0.5 that landed -- not the requested 1.0 (the applied-delta rule).
        result = apply_observation_rules(
            BeliefState(),
            observation=_kill_packet(killer="k"),
            previous_visible_bodies=set(),
            recent_co_presence={},
        )
        prov = result.view("k").provenance
        assert result.view("k").suspicion == 1.0
        assert prov.kill_or_vent_pin == pytest.approx(0.5)
        assert prov.kill_or_vent_pin != WITNESSED_KILL_SUSPICION_DELTA
        _assert_invariant(result)

    def test_body_proximity_tags_body_proximity(self) -> None:
        co_presence: Mapping[str, Sequence[tuple[int, str]]] = {
            "R": ((9, "bystander"),),
        }
        result = apply_observation_rules(
            BeliefState(),
            observation=_packet(
                tick=10,
                visible_bodies=(BodyView(id="b1", room="R", victim_id="victim"),),
            ),
            previous_visible_bodies=set(),
            recent_co_presence=co_presence,
        )
        prov = result.view("bystander").provenance
        assert prov.body_proximity == pytest.approx(BODY_PROXIMITY_SUSPICION_DELTA)
        assert prov.hard_total == pytest.approx(BODY_PROXIMITY_SUSPICION_DELTA)
        assert prov.soft_total == 0.0
        _assert_invariant(result)

    def test_contradiction_tags_flag_lift_with_capped_applied_delta(self) -> None:
        lifted = apply_contradiction_rule(BeliefState(), [_strong_flag(subject="s")])
        prov = lifted.view("s").provenance
        assert prov.flag_lift == pytest.approx(CONTRADICTION_SUSPICION_DELTA)
        assert prov.hard_total == pytest.approx(CONTRADICTION_SUSPICION_DELTA)
        assert prov.soft_total == 0.0
        _assert_invariant(lifted)

    def test_pre_vote_bump_tags_testimony_spread(self) -> None:
        # A two-voice pre-vote fold lifts by the graduated spread delta, tagged to
        # the SOFT testimony_spread channel -- and the transient half never rolls,
        # so the fresh bucket is directly observable.
        folded = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=["s"],
            phase="pre_vote",
            pre_vote_folded=frozenset({"s"}),
            pre_vote_voice_counts={"s": 2},
        )
        prov = folded.view("s").provenance
        assert prov.testimony_spread == pytest.approx(TESTIMONY_SPREAD_TWO_VOICE_DELTA)
        assert prov.soft_total == pytest.approx(TESTIMONY_SPREAD_TWO_VOICE_DELTA)
        assert prov.hard_total == 0.0
        assert prov.carried_hard == 0.0
        assert prov.carried_soft == 0.0
        _assert_invariant(folded)

    def test_pre_vote_corroboration_tags_accusation_carry_negative(self) -> None:
        # Corroboration moves in the pre-vote half (no roll), so the negative
        # accusation_carry delta -- the mirror of the accusation bump -- is
        # directly observable in the fresh bucket.
        folded = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=[],
            corroborated=["s"],
            phase="pre_vote",
        )
        prov = folded.view("s").provenance
        assert prov.accusation_carry == pytest.approx(-CORROBORATION_SUSPICION_DELTA)
        assert folded.view("s").suspicion == pytest.approx(
            _DEFAULT_SUSPICION - CORROBORATION_SUSPICION_DELTA
        )
        _assert_invariant(folded)

    def test_composed_accusation_bump_lands_in_carried_soft(self) -> None:
        # The persistent composed fold tags the accusation bump to accusation_carry
        # then ROLLS it into carried_soft: a persisted verbal accusation is SOFT
        # evidence, never hard. (The fresh accusation_carry bucket is transient
        # within the fold; the pre-vote corroboration test pins its sign.)
        folded = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=["s"],
        )
        prov = folded.view("s").provenance
        assert prov.carried_soft == pytest.approx(ACCUSATION_SUSPICION_DELTA)
        assert prov.accusation_carry == 0.0
        assert prov.testimony_spread == 0.0
        assert prov.hard_total == 0.0
        assert prov.soft_total == pytest.approx(ACCUSATION_SUSPICION_DELTA)
        _assert_invariant(folded)

    def test_untagged_adjust_lands_in_unattributed(self) -> None:
        state = BeliefState()
        state.adjust_suspicion("s", delta=0.1)
        prov = state.view("s").provenance
        assert prov.unattributed == pytest.approx(0.1)
        assert prov.hard_total == 0.0
        assert prov.soft_total == 0.0
        _assert_invariant(state)

    def test_unknown_seed_lands_in_unattributed(self) -> None:
        # A seed without a decomposition attributes the whole deviation to
        # unattributed (keeps the invariant with no source claimed).
        state = BeliefState()
        state.seed_player("s", suspicion=0.7, trust=0.5)
        prov = state.view("s").provenance
        assert prov.unattributed == pytest.approx(0.2)
        assert prov.total == pytest.approx(0.2)
        _assert_invariant(state)

    def test_seed_with_provenance_reconciles_residual(self) -> None:
        # A supplied decomposition is stored, and any gap between the clamped
        # deviation and its total is reconciled into unattributed -- so an
        # inconsistent (scalar, decomposition) pair still satisfies the invariant.
        given_prov = SuspicionProvenance(carried_hard=0.1)
        state = BeliefState()
        state.seed_player("s", suspicion=0.7, trust=0.5, provenance=given_prov)
        prov = state.view("s").provenance
        assert prov.carried_hard == pytest.approx(0.1)
        assert prov.unattributed == pytest.approx(0.1)  # 0.2 deviation - 0.1 given
        _assert_invariant(state)


# --- (3) the HARD/SOFT cross-meeting carry (DoD bullet 2) ------------------


class TestHardSoftCarry:
    """A grounded hard pin stays carried_HARD (never carried_soft) at meeting 2+.

    The belief-layer half of DoD bullet 2: a witnessed vent in meeting 1 (via
    :func:`apply_observation_rules`), then the persistent composed absorb (decay
    + roll), leaves a ``carried_hard`` component with ``carried_soft == 0`` -- and
    a second composed absorb keeps it hard (scaled by decay), never reclassifying
    it soft. The manager pre-vote re-render leg is Stage 3.
    """

    def _meeting_one_vent_absorbed(self) -> BeliefState:
        vented = apply_observation_rules(
            BeliefState(),
            observation=_packet(
                tick=10,
                visible_players=(PlayerView(id="killer", room="R", action="vent"),),
            ),
            previous_visible_bodies=set(),
            recent_co_presence={},
        )
        # Composed absorb (phase=None) with no fresh evidence about the venter:
        # decay + roll -- the meeting-1 boundary.
        return apply_meeting_evidence_rules(vented, own_id="observer", accused=[])

    def test_meeting_one_hard_pin_carries_hard_after_absorb(self) -> None:
        after = self._meeting_one_vent_absorbed()
        prov = after.view("killer").provenance
        # Vent 0.5 -> suspicion 1.0; decay 25% -> 0.875, pin scaled by 0.75 ->
        # 0.375; roll folds it to carried_hard.
        assert after.view("killer").suspicion == pytest.approx(0.875)
        assert prov.carried_hard == pytest.approx(0.375)
        assert prov.carried_soft == 0.0
        assert prov.kill_or_vent_pin == 0.0
        assert prov.hard_total == pytest.approx(0.375)
        _assert_invariant(after)

    def test_hard_carry_survives_a_second_absorb_scaled_never_soft(self) -> None:
        after_one = self._meeting_one_vent_absorbed()
        after_two = apply_meeting_evidence_rules(
            after_one, own_id="observer", accused=[]
        )
        prov = after_two.view("killer").provenance
        # 0.875 -> 0.78125 (another 25% decay); carried_hard 0.375 -> 0.28125.
        assert after_two.view("killer").suspicion == pytest.approx(0.78125)
        assert prov.carried_hard == pytest.approx(0.28125)
        assert prov.carried_soft == 0.0
        assert prov.hard_total == pytest.approx(0.28125)
        _assert_invariant(after_two)

    def test_soft_and_hard_priors_are_distinguishable_at_the_same_scalar(self) -> None:
        # The whole point of the split: a carried-soft prior and a body-proximity
        # pin can sit at the same scalar yet decompose differently (today they are
        # indistinguishable; 16.4's gate needs them apart).
        body = apply_observation_rules(
            BeliefState(),
            observation=_packet(
                tick=10,
                visible_bodies=(BodyView(id="b1", room="R", victim_id="victim"),),
            ),
            previous_visible_bodies=set(),
            recent_co_presence={"R": ((9, "bystander"),)},
        )
        # Two composed accusation folds -> a purely SOFT carried prior at 0.70.
        soft = BeliefState()
        for _ in range(2):
            soft = apply_meeting_evidence_rules(soft, own_id="observer", accused=["s"])

        assert body.view("bystander").suspicion == pytest.approx(0.70)
        # 0.5 -> 0.55 -> 0.6000000000000001 (reinforced, no decay): a soft 0.60.
        assert soft.view("s").provenance.hard_total == 0.0
        assert soft.view("s").provenance.soft_total > 0.0
        assert body.view("bystander").provenance.hard_total == pytest.approx(0.20)
        assert body.view("bystander").provenance.soft_total == 0.0


# --- (4) exact-float scalar bit-identity ------------------------------------


class TestScalarBitIdentity:
    """The arithmetic is untouched -- scalars are the pre-16.3 constants exactly.

    Exact ``==`` (never ``pytest.approx``): recording provenance beside the
    scalar must not perturb a single ULP of the value the fold and the render
    read.
    """

    def test_vent_pins_exactly_one(self) -> None:
        result = apply_observation_rules(
            BeliefState(),
            observation=_packet(
                tick=10,
                visible_players=(PlayerView(id="v", room="R", action="vent"),),
            ),
            previous_visible_bodies=set(),
            recent_co_presence={},
        )
        assert result.view("v").suspicion == 1.0
        assert result.view("v").provenance.kill_or_vent_pin == 0.5

    def test_single_decay_is_exactly_zero_point_875(self) -> None:
        state = BeliefState()
        state.adjust_suspicion(
            "v", delta=VENTING_SUSPICION_DELTA, source="kill_or_vent_pin"
        )
        state.decay_suspicion("v", rate=MEETING_SUSPICION_DECAY_RATE)
        assert state.view("v").suspicion == 0.875
        # Proportional scaling by exactly 0.75: 0.5 * 0.75 = 0.375.
        assert state.view("v").provenance.kill_or_vent_pin == 0.375

    def test_single_accusation_is_exactly_zero_point_55(self) -> None:
        folded = apply_meeting_evidence_rules(
            BeliefState(), own_id="observer", accused=["s"]
        )
        assert folded.view("s").suspicion == 0.55
        # The APPLIED delta is the exact IEEE residue new-old (0.55 - 0.5 ==
        # 0.050000000000000044), not the 0.05 constant -- the decomposition
        # records what actually landed on the scalar, to the ULP.
        assert folded.view("s").provenance.carried_soft == 0.55 - _DEFAULT_SUSPICION

    def test_two_accusations_hit_the_ieee_residue(self) -> None:
        # The audit §4.3 boundary case, unchanged: 0.5 + 0.05 + 0.05 ==
        # 0.6000000000000001 -- ejectable only by IEEE luck; provenance records it
        # beside the scalar without moving it.
        state = BeliefState()
        for _ in range(2):
            state = apply_meeting_evidence_rules(
                state, own_id="observer", accused=["s"]
            )
        assert state.view("s").suspicion == 0.6000000000000001  # noqa: PLR2004
        assert _invariant_error(state, "s") <= SUSPICION_PROVENANCE_ATOL


# --- (5) roll semantics -----------------------------------------------------


class TestRollSemantics:
    """The meeting-boundary roll: persistent halves roll, the pre-vote half never.

    :meth:`SuspicionProvenance.carried` moves flag/body/pin -> carried_hard and
    spread/accusation -> carried_soft, leaving unattributed put; and the fold
    invokes it only when ``phase != "pre_vote"``.
    """

    def test_carried_moves_hard_and_soft_and_keeps_unattributed(self) -> None:
        prov = SuspicionProvenance(
            flag_lift=0.1,
            body_proximity=0.2,
            kill_or_vent_pin=0.3,
            testimony_spread=0.05,
            accusation_carry=0.04,
            carried_hard=1.0,
            carried_soft=2.0,
            unattributed=0.5,
        )
        rolled = prov.carried()
        assert rolled.carried_hard == pytest.approx(1.0 + 0.1 + 0.2 + 0.3)
        assert rolled.carried_soft == pytest.approx(2.0 + 0.05 + 0.04)
        assert rolled.unattributed == pytest.approx(0.5)
        assert rolled.flag_lift == 0.0
        assert rolled.body_proximity == 0.0
        assert rolled.kill_or_vent_pin == 0.0
        assert rolled.testimony_spread == 0.0
        assert rolled.accusation_carry == 0.0
        # Total (and therefore the scalar) is preserved by the roll.
        assert rolled.total == pytest.approx(prov.total)

    def _vent_state(self) -> BeliefState:
        return apply_observation_rules(
            BeliefState(),
            observation=_packet(
                tick=10,
                visible_players=(PlayerView(id="v", room="R", action="vent"),),
            ),
            previous_visible_bodies=set(),
            recent_co_presence={},
        )

    def test_pre_vote_fold_never_rolls(self) -> None:
        # The transient pre-vote half neither decays nor rolls: the fresh pin
        # stays a fresh kill_or_vent_pin, nothing lands in carried_hard.
        folded = apply_meeting_evidence_rules(
            self._vent_state(),
            own_id="observer",
            accused=[],
            phase="pre_vote",
        )
        prov = folded.view("v").provenance
        assert folded.view("v").suspicion == 1.0
        assert prov.kill_or_vent_pin == pytest.approx(0.5)
        assert prov.carried_hard == 0.0

    def test_post_vote_fold_rolls(self) -> None:
        folded = apply_meeting_evidence_rules(
            self._vent_state(),
            own_id="observer",
            accused=[],
            phase="post_vote",
        )
        prov = folded.view("v").provenance
        # post_vote decays (1.0 -> 0.875) then rolls the scaled pin to carried_hard.
        assert folded.view("v").suspicion == pytest.approx(0.875)
        assert prov.kill_or_vent_pin == 0.0
        assert prov.carried_hard == pytest.approx(0.375)

    def test_composed_none_fold_rolls(self) -> None:
        folded = apply_meeting_evidence_rules(
            self._vent_state(), own_id="observer", accused=[]
        )
        prov = folded.view("v").provenance
        assert prov.carried_hard == pytest.approx(0.375)
        assert prov.kill_or_vent_pin == 0.0
