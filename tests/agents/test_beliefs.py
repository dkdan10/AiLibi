from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest

from agents.memory.beliefs import (
    ACCUSATION_SUSPICION_DELTA,
    BODY_PROXIMITY_SUSPICION_DELTA,
    CONTRADICTION_SUSPICION_DELTA,
    CORROBORATION_SUSPICION_DELTA,
    MEETING_CONTRADICTION_LIFT_CAP,
    MEETING_SUSPICION_DECAY_RATE,
    TESTIMONY_INDEPENDENCE_BAR,
    WEAK_CONTRADICTION_SUSPICION_DELTA,
    BeliefState,
    PlayerBelief,
    VENTING_SUSPICION_DELTA,
    apply_contradiction_rule,
    apply_meeting_evidence_rules,
    apply_observation_rules,
)
from meetings.schemas import AlibiClaim as SchemaAlibiClaim
from meetings.schemas import ContradictionRef as MeetingContradictionRef
from meetings.schemas import (
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
)
from meetings.transcript import (
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_SELF_STATED,
    detect_contradictions,
)
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


def _snapshot(state: BeliefState) -> dict[str, PlayerBelief]:
    return {player_id: state.view(player_id) for player_id in state.known_players()}


class TestApplyObservationRulesPurity:
    def test_pure_function_does_not_mutate_input_and_is_deterministic(self) -> None:
        base = BeliefState()
        # Pre-existing belief: the copy must carry it forward untouched.
        base.adjust_suspicion("prior_suspect", delta=0.1)

        packet = _packet(
            tick=10,
            visible_players=(PlayerView(id="venter", room="R", action="vent"),),
            visible_bodies=(BodyView(id="b1", room="R", victim_id="victim"),),
        )
        co_presence: Mapping[str, Sequence[tuple[int, str]]] = {
            "R": ((9, "bystander"),),
        }
        previous_bodies: set[str] = set()
        before = _snapshot(base)

        first = apply_observation_rules(
            base,
            observation=packet,
            previous_visible_bodies=previous_bodies,
            recent_co_presence=co_presence,
        )
        second = apply_observation_rules(
            base,
            observation=packet,
            previous_visible_bodies=previous_bodies,
            recent_co_presence=co_presence,
        )

        # Input is untouched: same players, same values, distinct object.
        assert _snapshot(base) == before
        assert base.known_players() == ("prior_suspect",)
        assert first is not base

        # Identical inputs produce equal — but independent — results.
        assert _snapshot(first) == _snapshot(second)
        assert first is not second

        # The deltas landed on the copy, not the input.
        assert first.view("venter").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + VENTING_SUSPICION_DELTA
        )
        assert first.view("bystander").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + BODY_PROXIMITY_SUSPICION_DELTA
        )
        assert first.view("prior_suspect").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 0.1
        )

    def test_victim_is_not_suspected_for_own_body(self) -> None:
        # The corpse was alive in the room moments before discovery, so it sits
        # in recent_co_presence; Rule 1 must skip body.victim_id and only
        # elevate the genuine bystander.
        base = BeliefState()
        packet = _packet(
            tick=10,
            visible_bodies=(BodyView(id="b1", room="R", victim_id="victim"),),
        )
        co_presence: Mapping[str, Sequence[tuple[int, str]]] = {
            "R": ((9, "victim"), (9, "bystander")),
        }

        result = apply_observation_rules(
            base,
            observation=packet,
            previous_visible_bodies=set(),
            recent_co_presence=co_presence,
        )

        assert result.view("victim").suspicion == _DEFAULT_SUSPICION
        assert result.view("bystander").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + BODY_PROXIMITY_SUSPICION_DELTA
        )

    def test_seen_body_does_not_refire(self) -> None:
        base = BeliefState()
        packet = _packet(
            tick=10,
            visible_bodies=(BodyView(id="b1", room="R", victim_id="victim"),),
        )
        co_presence: Mapping[str, Sequence[tuple[int, str]]] = {
            "R": ((9, "bystander"),),
        }

        result = apply_observation_rules(
            base,
            observation=packet,
            previous_visible_bodies={"b1"},
            recent_co_presence=co_presence,
        )

        assert result.known_players() == ()
        assert result.view("bystander").suspicion == _DEFAULT_SUSPICION


class TestTeamInternalFirewallContract:
    """Task 9.3 layering pin (DESIGN.md §4.7).

    The team-internal firewall on the belief side lives in perception, which
    omits fellow impostors from ``recent_co_presence`` before calling
    :func:`apply_observation_rules`. The rule function itself has no team
    concept -- a player simply absent from ``recent_co_presence`` accrues no
    body-proximity suspicion. This pins the exact mechanism the perception
    guard relies on, so beliefs.py stays role-agnostic.
    """

    def test_player_absent_from_co_presence_gets_no_proximity_suspicion(self) -> None:
        base = BeliefState()
        packet = _packet(
            tick=10,
            visible_bodies=(BodyView(id="b1", room="R", victim_id="victim"),),
        )
        # "present" is in the room; "filtered" was dropped upstream (exactly as
        # perception drops a fellow impostor from co-presence), so it never
        # reaches the rule and must not be elevated.
        co_presence: Mapping[str, Sequence[tuple[int, str]]] = {
            "R": ((9, "present"),),
        }

        result = apply_observation_rules(
            base,
            observation=packet,
            previous_visible_bodies=set(),
            recent_co_presence=co_presence,
        )

        assert result.view("present").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + BODY_PROXIMITY_SUSPICION_DELTA
        )
        assert result.view("filtered").suspicion == _DEFAULT_SUSPICION


# --- Rule 2 graduated weak-contradiction weight (Task 9.7; audit gp-1) ------


def _meeting_flag(
    *,
    subject: str,
    weak: bool,
    kind: str = "alibi_vs_sighting",
    pair: str = "a|b",
) -> MeetingContradictionRef:
    """A meeting-side flag shaped like detector output.

    ``weak=True`` appends the exact audit marker
    :func:`meetings.transcript.detect_contradictions` writes for a
    self-stated alibi, so the predicate path under test is the
    production one (the detector round-trip test below guards against
    the marker format drifting).
    """

    description = f"Alibi places {subject} in A (ticks 0-9); sighting reports {subject} in B at tick 5."
    if weak:
        description = f"{description} {WEAK_CONTRADICTION_MARKER_PREFIX}{WEAK_REASON_SELF_STATED}]"
    return MeetingContradictionRef(
        contradiction_id=f"contra:{kind}:{pair}",
        kind=kind,  # type: ignore[arg-type]
        event_a_id=pair.split("|")[0],
        event_b_id=pair.split("|")[1],
        subjects=(subject,),
        description=description,
    )


class TestContradictionRuleGraduatedWeight:
    """Task 9.7 precision fix (DESIGN.md §6.3 Rule 2, §4.6; audit gp-1).

    A lone detector-flagged WEAK contradiction (self-stated / narrow
    window) lands in the suspicious-but-below-gate band [0.5, 0.60) --
    raised, not zeroed, and not crossing the §4.6 0.60 eject gate that
    railroaded 13/13 wrong ejections. Corroboration still converts: a
    second weak flag, a strong flag, or an elevated prior (body
    proximity / vent) carries the subject across 0.60.
    """

    def test_lone_weak_flag_lands_in_suspicious_below_gate_band(self) -> None:
        updated = apply_contradiction_rule(
            BeliefState(), [_meeting_flag(subject="p-5", weak=True)]
        )

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + WEAK_CONTRADICTION_SUSPICION_DELTA
        )
        # The contract band: suspicious (above the 0.5 prior) but below
        # the 0.60 eject gate.
        assert _DEFAULT_SUSPICION < suspicion < 0.60

    def test_lone_strong_flag_keeps_full_weight_and_crosses_gate(self) -> None:
        updated = apply_contradiction_rule(
            BeliefState(), [_meeting_flag(subject="p-5", weak=False)]
        )

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + CONTRADICTION_SUSPICION_DELTA
        )
        assert suspicion >= 0.60

    def test_two_weak_flags_corroborate_across_the_gate(self) -> None:
        # Two independent weak signals -- flags riding two DIFFERENT
        # alibi claims (distinct lift keys; Task 10.1 dedups only flags
        # that share a claim) -- ARE corroboration: the subject stays
        # ejectable, the lone-signal railroad is gone.
        updated = apply_contradiction_rule(
            BeliefState(),
            [
                _meeting_flag(subject="p-5", weak=True, pair="a|b"),
                _meeting_flag(subject="p-5", weak=True, pair="c|d"),
            ],
        )

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 2 * WEAK_CONTRADICTION_SUSPICION_DELTA
        )
        assert suspicion >= 0.60

    def test_weak_plus_strong_crosses_gate_at_the_capped_lift(self) -> None:
        # Task 10.1: the per-subject per-meeting cap bounds the summed
        # lift at one strong flag's worth (0.3), so weak + strong lands
        # at 0.8 -- still decisively over the gate; the cap trims the
        # stack, never the conversion.
        updated = apply_contradiction_rule(
            BeliefState(),
            [
                _meeting_flag(subject="p-5", weak=True, pair="a|b"),
                _meeting_flag(subject="p-5", weak=False, pair="c|d"),
            ],
        )

        suspicion = updated.view("p-5").suspicion
        assert (
            WEAK_CONTRADICTION_SUSPICION_DELTA + CONTRADICTION_SUSPICION_DELTA
            > MEETING_CONTRADICTION_LIFT_CAP
        )
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + MEETING_CONTRADICTION_LIFT_CAP
        )
        assert suspicion >= 0.60

    def test_weak_flag_on_body_proximity_prior_crosses_gate(self) -> None:
        # The "second independent signal" need not be a contradiction: a
        # Rule-1 body-proximity prior (0.5 + 0.2 = 0.7) plus the weak
        # delta crosses, so a reporter who ALSO lingered near the body
        # is still ejectable.
        beliefs = BeliefState()
        beliefs.seed_player(
            "p-5",
            suspicion=_DEFAULT_SUSPICION + BODY_PROXIMITY_SUSPICION_DELTA,
            trust=0.5,
        )

        updated = apply_contradiction_rule(
            beliefs, [_meeting_flag(subject="p-5", weak=True)]
        )

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION
            + BODY_PROXIMITY_SUSPICION_DELTA
            + WEAK_CONTRADICTION_SUSPICION_DELTA
        )
        assert suspicion >= 0.60

    def test_marked_alibi_conflict_takes_the_graduated_delta(self) -> None:
        # Task 10.1 (audit gp-2 C-C-2): the conflict path now carries the
        # 9.7 weak classification -- the detector marks self-pair /
        # adversarial / narrow / boundary-overlap conflicts, and Rule 2
        # honours the marker on either kind. Pre-10.1 this flag kept the
        # full delta and drove 5 of the 11 audited wrong ejections.
        updated = apply_contradiction_rule(
            BeliefState(),
            [_meeting_flag(subject="p-5", weak=True, kind="alibi_conflict")],
        )

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + WEAK_CONTRADICTION_SUSPICION_DELTA
        )
        assert suspicion < 0.60

    def test_unmarked_alibi_conflict_keeps_full_weight(self) -> None:
        updated = apply_contradiction_rule(
            BeliefState(),
            [_meeting_flag(subject="p-5", weak=False, kind="alibi_conflict")],
        )

        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + CONTRADICTION_SUSPICION_DELTA
        )

    def test_weak_flag_still_records_the_inconsistency(self) -> None:
        # Down-weighted, not discarded: the flag still lands in the
        # subject's inconsistency list (information for the §6.6 render).
        updated = apply_contradiction_rule(
            BeliefState(), [_meeting_flag(subject="p-5", weak=True)]
        )

        assert len(updated.view("p-5").inconsistencies) == 1

    def test_detector_output_round_trips_into_graduated_delta(self) -> None:
        # Drift guard: feed REAL detector output (not a hand-built
        # marker) through the rule -- the seed-3 audited shape, the
        # reporter's own alibi vs a third party's sighting of them.
        transcript = MeetingTranscript(
            turns=(
                MeetingTurn(
                    turn_id="m-1:turn-0",
                    turn_index=0,
                    speaker="p-5",
                    turn_kind="opening",
                    reply_to=None,
                    claims=(
                        SchemaAlibiClaim(
                            type="alibi",
                            subject="p-5",
                            from_tick=100,
                            to_tick=200,
                            room="CAFETERIA",
                        ),
                    ),
                    free_text="reporter self-alibi",
                ),
                MeetingTurn(
                    turn_id="m-1:turn-1",
                    turn_index=1,
                    speaker="p-2",
                    turn_kind="reply",
                    reply_to=None,
                    observations=(
                        SawPlayerObservation(
                            type="saw_player",
                            tick=150,
                            subject="p-5",
                            room="EAST_HALL",
                        ),
                    ),
                    free_text="third-party sighting",
                ),
            )
        )
        flags = detect_contradictions(transcript)
        assert len(flags) == 1

        updated = apply_contradiction_rule(BeliefState(), flags)

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + WEAK_CONTRADICTION_SUSPICION_DELTA
        )
        assert _DEFAULT_SUSPICION < suspicion < 0.60


# --- Task 10.1 lift dedup + per-meeting cap (audit gp-2 C-C-3) --------------


def _fountain_flag(
    *, subject: str, claim_ordinal: int, sighting_ordinal: int, weak: bool = True
) -> MeetingContradictionRef:
    """A detector-shaped flag with realistic claim/obs event ids.

    ``claim_ordinal`` selects the alibi claim's turn, so flags sharing it
    share the Task 10.1 lift key (one alibi paired against many
    sightings) while distinct ordinals are independent claims.
    """

    claim_id = f"turn:m-1:turn-{claim_ordinal}:claim:0"
    obs_id = f"turn:m-1:turn-{sighting_ordinal}:obs:0"
    return _meeting_flag(subject=subject, weak=weak, pair=f"{claim_id}|{obs_id}")


class TestContradictionLiftDedupAndCap:
    """Task 10.1 (DESIGN.md §6.3 Rule 2; audit gp-2 C-C-3).

    The detector emits one flag per (alibi, sighting) pair, so one alibi
    against N sightings is N flags; pre-10.1 the lift summed per flag and
    19 near-duplicate weak flags lifted an innocent from 0.5 to a clamped
    1.0 (seed 9 m1, ejected 5-0). The lift now dedups per
    (subject, alibi-claim) and the per-subject sum caps at one strong
    flag's worth -- flag volume can never substitute for evidence.
    """

    def test_fountain_of_same_claim_weak_flags_lifts_once(self) -> None:
        # The seed-9 m1 shape, synthetic: ONE alibi claim paired against
        # 19 repeated sightings. 19 flags, one effective weak delta.
        flags = [
            _fountain_flag(subject="p-8", claim_ordinal=1, sighting_ordinal=n)
            for n in range(2, 21)
        ]
        updated = apply_contradiction_rule(BeliefState(), flags)

        suspicion = updated.view("p-8").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + WEAK_CONTRADICTION_SUSPICION_DELTA
        )
        assert suspicion < 0.60

    def test_flags_from_distinct_claims_still_accumulate(self) -> None:
        # Dedup is per claim, not per subject: two weak flags riding two
        # DIFFERENT alibi claims remain two pieces of evidence (the 9.7
        # corroboration path survives the dedup).
        flags = [
            _fountain_flag(subject="p-8", claim_ordinal=1, sighting_ordinal=3),
            _fountain_flag(subject="p-8", claim_ordinal=2, sighting_ordinal=4),
        ]
        updated = apply_contradiction_rule(BeliefState(), flags)

        assert updated.view("p-8").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 2 * WEAK_CONTRADICTION_SUSPICION_DELTA
        )

    def test_mixed_weak_and_strong_on_one_claim_takes_the_strongest(self) -> None:
        # One claim, two sightings -- one endpoint-weak, one interior
        # strong: the claim is strong-contradicted once, the weak
        # duplicate adds nothing.
        flags = [
            _fountain_flag(
                subject="p-8", claim_ordinal=1, sighting_ordinal=2, weak=True
            ),
            _fountain_flag(
                subject="p-8", claim_ordinal=1, sighting_ordinal=3, weak=False
            ),
        ]
        updated = apply_contradiction_rule(BeliefState(), flags)

        assert updated.view("p-8").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + CONTRADICTION_SUSPICION_DELTA
        )

    def test_per_subject_lift_caps_at_one_strong_flag(self) -> None:
        # Two independent STRONG claims would sum to 0.6; the per-subject
        # per-meeting cap bounds the transient lift at one strong flag's
        # worth. Cross-meeting accumulation stays the 9.8 channel.
        flags = [
            _fountain_flag(
                subject="p-8", claim_ordinal=1, sighting_ordinal=3, weak=False
            ),
            _fountain_flag(
                subject="p-8", claim_ordinal=2, sighting_ordinal=4, weak=False
            ),
        ]
        updated = apply_contradiction_rule(BeliefState(), flags)

        assert updated.view("p-8").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + MEETING_CONTRADICTION_LIFT_CAP
        )

    def test_no_flag_volume_reaches_certainty_from_the_default_prior(self) -> None:
        # The headline property: however many flags (weak, strong, any
        # mix of claims), one meeting's lift cannot carry a default-prior
        # subject to 1.0 -- the audited railroad ceiling.
        flags = [
            _fountain_flag(
                subject="p-8",
                claim_ordinal=claim,
                sighting_ordinal=10 + sighting,
                weak=sighting % 2 == 0,
            )
            for claim in range(8)
            for sighting in range(6)
        ]
        updated = apply_contradiction_rule(BeliefState(), flags)

        assert updated.view("p-8").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + MEETING_CONTRADICTION_LIFT_CAP
        )
        assert updated.view("p-8").suspicion < 1.0

    def test_single_strong_flag_is_never_capped(self) -> None:
        # The cap bounds stacking only: a lone strong flag keeps its
        # existing single-flag weight exactly.
        updated = apply_contradiction_rule(
            BeliefState(),
            [
                _fountain_flag(
                    subject="p-8", claim_ordinal=1, sighting_ordinal=2, weak=False
                )
            ],
        )

        assert updated.view("p-8").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + CONTRADICTION_SUSPICION_DELTA
        )

    def test_deduped_flags_still_record_every_inconsistency(self) -> None:
        # The dedup is about the score, never the information: all N
        # flags land on the subject's inconsistency list (§5.4 "flags
        # are information").
        flags = [
            _fountain_flag(subject="p-8", claim_ordinal=1, sighting_ordinal=n)
            for n in range(2, 7)
        ]
        updated = apply_contradiction_rule(BeliefState(), flags)

        assert len(updated.view("p-8").inconsistencies) == 5

    def test_detector_fountain_round_trips_into_one_lift(self) -> None:
        # Drift guard on the real pipeline: one self-stated alibi, three
        # third-party sightings elsewhere -> three weak flags from the
        # detector -> ONE effective weak delta through the rule.
        turns = [
            MeetingTurn(
                turn_id="m-1:turn-0",
                turn_index=0,
                speaker="p-5",
                turn_kind="opening",
                reply_to=None,
                claims=(
                    SchemaAlibiClaim(
                        type="alibi",
                        subject="p-5",
                        from_tick=100,
                        to_tick=200,
                        room="CAFETERIA",
                    ),
                ),
                free_text="reporter self-alibi",
            ),
        ]
        for n, tick in enumerate((150, 160, 170), start=1):
            turns.append(
                MeetingTurn(
                    turn_id=f"m-1:turn-{n}",
                    turn_index=n,
                    speaker=f"p-{n + 5}",
                    turn_kind="reply",
                    reply_to=None,
                    observations=(
                        SawPlayerObservation(
                            type="saw_player",
                            tick=tick,
                            subject="p-5",
                            room="EAST_HALL",
                        ),
                    ),
                    free_text="third-party sighting",
                )
            )
        flags = detect_contradictions(MeetingTranscript(turns=tuple(turns)))
        assert len(flags) == 3

        updated = apply_contradiction_rule(BeliefState(), flags)

        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + WEAK_CONTRADICTION_SUSPICION_DELTA
        )


# --- Task 9.8 accusation accumulator + Rule 3 / Rule 5 (audit gp-1 recall) --

# The §4.6 eject gate the accumulator's numeric pins are calibrated against
# (DESIGN.md §4.6: max suspicion < 0.6 -> the ballot verdict is MUST-SKIP).
_EJECT_GATE = 0.60


def _absorb_meetings(
    beliefs: BeliefState,
    evidence_per_meeting: Sequence[Mapping[str, Sequence[str]]],
    *,
    own_id: str = "observer",
    fellow_impostor_ids: Sequence[str] = (),
) -> BeliefState:
    """Apply :func:`apply_meeting_evidence_rules` once per meeting in order."""

    state = beliefs
    for evidence in evidence_per_meeting:
        state = apply_meeting_evidence_rules(
            state,
            own_id=own_id,
            accused=evidence.get("accused", ()),
            corroborated=evidence.get("corroborated", ()),
            contradicted=evidence.get("contradicted", ()),
            fellow_impostor_ids=fellow_impostor_ids,
        )
    return state


class TestMeetingEvidenceRules:
    """Task 9.8 (DESIGN.md §6.3 Rules 3 + 5, §4.6; audit gp-1 recall).

    The decaying accusation accumulator: a single accusation lands well
    under the 0.60 gate, the same subject accused across 2-3 meetings
    accumulates over it, an unreinforced bump decays back toward 0.5,
    and a corroboration lowers suspicion. All pinned numerically.
    """

    def test_single_accusation_adds_small_delta_well_under_gate(self) -> None:
        updated = _absorb_meetings(BeliefState(), [{"accused": ["p-5"]}])

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        # Well under the gate: under the weak-contradiction band (0.58)
        # too -- a verbal accusation is the weakest tracked signal.
        assert suspicion < _DEFAULT_SUSPICION + WEAK_CONTRADICTION_SUSPICION_DELTA
        assert suspicion < _EJECT_GATE

    def test_accusations_across_meetings_accumulate_over_gate(self) -> None:
        # Reinforced every meeting, so Rule 5 never erodes the bump: the
        # trajectory is 0.55 -> 0.60 -> 0.65. The second consecutive
        # accusation reaches the inclusive >= 0.60 gate and the third
        # clears it with margin, pinning "across 2-3 meetings converts"
        # while one meeting never does.
        meeting = {"accused": ["p-5"]}

        after_one = _absorb_meetings(BeliefState(), [meeting])
        after_two = _absorb_meetings(BeliefState(), [meeting, meeting])
        after_three = _absorb_meetings(BeliefState(), [meeting, meeting, meeting])

        assert after_one.view("p-5").suspicion < _EJECT_GATE
        assert after_two.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 2 * ACCUSATION_SUSPICION_DELTA
        )
        assert after_two.view("p-5").suspicion >= _EJECT_GATE
        assert after_three.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 3 * ACCUSATION_SUSPICION_DELTA
        )
        assert after_three.view("p-5").suspicion > _EJECT_GATE

    def test_unreinforced_bump_decays_back_toward_default(self) -> None:
        # Rule 5: accused once, then two evidence-free meetings. Each
        # quiet round pulls suspicion 25% of the way back to the 0.5
        # prior: 0.55 -> 0.5375 -> 0.528125, monotonically toward 0.5
        # and never past it.
        bumped = _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        decayed_once = bumped + (_DEFAULT_SUSPICION - bumped) * (
            MEETING_SUSPICION_DECAY_RATE
        )

        after_quiet_one = _absorb_meetings(BeliefState(), [{"accused": ["p-5"]}, {}])
        after_quiet_two = _absorb_meetings(
            BeliefState(), [{"accused": ["p-5"]}, {}, {}]
        )

        one = after_quiet_one.view("p-5").suspicion
        two = after_quiet_two.view("p-5").suspicion
        assert one == pytest.approx(decayed_once)
        assert two == pytest.approx(
            decayed_once
            + (_DEFAULT_SUSPICION - decayed_once) * (MEETING_SUSPICION_DECAY_RATE)
        )
        assert bumped > one > two > _DEFAULT_SUSPICION

    def test_decay_drifts_low_suspicion_up_toward_default(self) -> None:
        # Rule 5 is "drift toward 0.5", not "drift down": a cleared
        # (below-prior) row also relaxes back when unreinforced.
        beliefs = BeliefState()
        beliefs.seed_player("p-5", suspicion=0.45, trust=0.5)

        updated = _absorb_meetings(beliefs, [{}])

        assert updated.view("p-5").suspicion == pytest.approx(
            0.45 + (_DEFAULT_SUSPICION - 0.45) * MEETING_SUSPICION_DECAY_RATE
        )

    def test_reinforced_subject_does_not_decay(self) -> None:
        # "Unreinforced" is the Rule 5 trigger: a subject accused THIS
        # meeting has new evidence, so the bump lands on the undecayed
        # prior (0.55 + 0.05, not 0.5375 + 0.05).
        updated = _absorb_meetings(
            BeliefState(), [{"accused": ["p-5"]}, {"accused": ["p-5"]}]
        )

        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + 2 * ACCUSATION_SUSPICION_DELTA
        )

    def test_corroboration_lowers_suspicion(self) -> None:
        # Rule 3: one vouch cancels one accusation-meeting exactly
        # (0.55 -> 0.50), and a corroborated subject is reinforced, so
        # no decay stacks on top of the lowering.
        updated = _absorb_meetings(
            BeliefState(), [{"accused": ["p-5"]}, {"corroborated": ["p-5"]}]
        )

        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION
            + ACCUSATION_SUSPICION_DELTA
            - CORROBORATION_SUSPICION_DELTA
        )

    def test_accused_and_corroborated_same_meeting_net_zero(self) -> None:
        updated = _absorb_meetings(
            BeliefState(), [{"accused": ["p-5"], "corroborated": ["p-5"]}]
        )

        assert updated.view("p-5").suspicion == pytest.approx(_DEFAULT_SUSPICION)

    def test_contradicted_subject_is_exempt_from_decay_but_not_lifted(self) -> None:
        # A detected contradiction is NEW evidence (no Rule-5 drift this
        # round) but its persistent lift stays Rule 2's transient
        # vote-time mechanism -- the stored score is unchanged.
        beliefs = BeliefState()
        beliefs.seed_player("p-5", suspicion=0.7, trust=0.5)
        beliefs.seed_player("p-6", suspicion=0.7, trust=0.5)

        updated = _absorb_meetings(beliefs, [{"contradicted": ["p-5"]}])

        assert updated.view("p-5").suspicion == pytest.approx(0.7)
        assert updated.view("p-6").suspicion == pytest.approx(
            0.7 + (_DEFAULT_SUSPICION - 0.7) * MEETING_SUSPICION_DECAY_RATE
        )

    def test_impostor_accrues_no_accusation_bump_against_teammate(self) -> None:
        # §1.3 / §4.7 firewall (the 7.12/9.3 teammate guard): the bump is
        # dropped on the input side for a fellow impostor -- no row is
        # even materialised -- while the same accusation against a
        # non-teammate lands normally.
        updated = _absorb_meetings(
            BeliefState(),
            [{"accused": ["p-2", "p-5"]}],
            fellow_impostor_ids=("p-2",),
        )

        assert "p-2" not in updated.known_players()
        assert updated.view("p-2").suspicion == _DEFAULT_SUSPICION
        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )

    def test_accused_teammate_row_still_decays_toward_neutral(self) -> None:
        # The guard drops teammate evidence entirely (input-side, like
        # 9.3): an accused teammate is NOT "reinforced", so any residual
        # teammate suspicion decays toward 0.5 like an unreinforced row.
        beliefs = BeliefState()
        beliefs.seed_player("p-2", suspicion=0.6, trust=0.5)

        updated = _absorb_meetings(
            beliefs,
            [{"accused": ["p-2"], "contradicted": ["p-2"]}],
            fellow_impostor_ids=("p-2",),
        )

        assert updated.view("p-2").suspicion == pytest.approx(
            0.6 + (_DEFAULT_SUSPICION - 0.6) * MEETING_SUSPICION_DECAY_RATE
        )

    def test_own_id_is_excluded_from_every_rule(self) -> None:
        # A recorded self-accusation (audit: 5 across the baseline) bumps
        # everyone ELSE's view of the speaker; the speaker's own store
        # never grows a self row, and an existing (defensive) self row is
        # never decayed.
        updated = _absorb_meetings(
            BeliefState(),
            [{"accused": ["observer"], "corroborated": ["observer"]}],
        )

        assert updated.known_players() == ()

    def test_decay_never_materialises_a_row(self) -> None:
        updated = _absorb_meetings(BeliefState(), [{}])

        assert updated.known_players() == ()

    def test_pure_function_does_not_mutate_input_and_is_deterministic(self) -> None:
        base = BeliefState()
        base.adjust_suspicion("prior_suspect", delta=0.2)
        before = _snapshot(base)
        evidence: Mapping[str, Sequence[str]] = {
            "accused": ["p-5", "p-3"],
            "corroborated": ["p-7"],
        }

        first = _absorb_meetings(base, [evidence])
        second = _absorb_meetings(base, [evidence])

        assert _snapshot(base) == before
        assert first is not base
        assert _snapshot(first) == _snapshot(second)
        # Unordered evidence lands deterministically: both accused rows
        # bumped, the corroborated row lowered, the stale prior decayed.
        assert first.view("p-3").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert first.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert first.view("p-7").suspicion == pytest.approx(
            _DEFAULT_SUSPICION - CORROBORATION_SUSPICION_DELTA
        )
        assert first.view("prior_suspect").suspicion == pytest.approx(
            0.7 + (_DEFAULT_SUSPICION - 0.7) * MEETING_SUSPICION_DECAY_RATE
        )


class TestMeetingEvidenceRosterFilter:
    """Task 10.2 (DESIGN.md §6.3; audit gp-6 C-C-8, H-H-6).

    ``apply_meeting_evidence_rules`` with a ``roster`` drops non-roster
    evidence subjects on the input side AND purges pre-existing
    non-roster rows from the returned state -- the belief-store half of
    the defense-in-depth behind the meeting-layer chokepoint, so a
    hallucinated structural id never materialises a row however it
    arrives, and a row that somehow predates the filters does not
    survive a fold. ``roster=None`` preserves the unfiltered legacy
    shape (no input filter, no purge).
    """

    def test_non_roster_subjects_are_dropped_from_every_channel(self) -> None:
        # The audit's garbage shapes (a game id, a turn id, a free-text
        # phrase) across all three channels: no row materialises, while
        # the roster subjects folded alongside land at the exact deltas.
        updated = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("headless-seed-9", "p-5"),
            corroborated=("headless-seed-12:meeting-0:turn-0", "p-3"),
            contradicted=("p-2 dead",),
            roster=frozenset({"observer", "p-2", "p-3", "p-4", "p-5"}),
        )

        assert set(updated.known_players()) == {"p-3", "p-5"}
        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert updated.view("p-3").suspicion == pytest.approx(
            _DEFAULT_SUSPICION - CORROBORATION_SUSPICION_DELTA
        )

    def test_pre_existing_non_roster_row_is_purged_by_the_fold(self) -> None:
        # The output-side half (Codex review, PR #140): a garbage row
        # that already exists -- pollution predating the filters, or a
        # hypothetical write path they do not cover -- is DELETED by the
        # fold, not decayed, so the returned state and every snapshot
        # built from it (the §6.6 render, the next vote prompt's
        # suspicion graph) carry roster ids only. New garbage evidence
        # about the same id is likewise ignored; the roster row alongside
        # decays normally, untouched by the purge.
        beliefs = BeliefState()
        beliefs.seed_player(
            "headless-seed-12:meeting-0:turn-0", suspicion=0.45, trust=0.5
        )
        beliefs.seed_player("p-3", suspicion=0.7, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=(),
            corroborated=("headless-seed-12:meeting-0:turn-0",),
            contradicted=("headless-seed-12:meeting-0:turn-0",),
            roster=frozenset({"observer", "p-3"}),
        )

        assert updated.known_players() == ("p-3",)
        assert updated.view("p-3").suspicion == pytest.approx(
            0.7 + (_DEFAULT_SUSPICION - 0.7) * MEETING_SUSPICION_DECAY_RATE
        )
        # Purity holds: the purge mutated the returned copy, never the
        # caller's state.
        assert "headless-seed-12:meeting-0:turn-0" in beliefs.known_players()

    def test_none_roster_applies_no_filter_and_no_purge(self) -> None:
        # The legacy / pure-math call shape: without a roster channel the
        # rules behave exactly as before this task -- non-roster evidence
        # lands, and a pre-existing unknown row decays instead of being
        # purged.
        beliefs = BeliefState()
        beliefs.seed_player("stale-unknown-id", suspicion=0.7, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=("headless-seed-9",),
            roster=None,
        )

        assert updated.view("headless-seed-9").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert updated.view("stale-unknown-id").suspicion == pytest.approx(
            0.7 + (_DEFAULT_SUSPICION - 0.7) * MEETING_SUSPICION_DECAY_RATE
        )


# ---------------------------------------------------------------------------
# Task 10.7: the two-witness fold phases (audit gp-2 C-C-1/C-C-2; the
# corroborate-within-round owner principle). One fold function, a phase
# argument: ``pre_vote`` moves the folded testimony bumps + this meeting's
# corroborations, ``post_vote`` moves the single-voice bumps + Rule-5 decay,
# and the default composed call stays byte-identical to the pre-10.7 fold.
# ---------------------------------------------------------------------------


class TestMeetingFoldPhases:
    """The Task 10.7 phase routing in ``apply_meeting_evidence_rules``.

    The double-fold hazard -- a folded subject bumped pre-vote AND
    post-vote, silently doubling the +0.05 constant -- is the one bug
    class the contract names non-negotiable; the composition and
    per-meeting-total pins below are its guards.
    """

    def test_independence_bar_is_two_witnesses(self) -> None:
        # The owner decision (audit §4.2): two-witness, not single
        # (single-witness pre-vote was REJECTED at +14/-9 meetings).
        assert TESTIMONY_INDEPENDENCE_BAR == 2

    def test_pre_vote_bumps_only_folded_subjects(self) -> None:
        updated = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("p-2", "p-5"),
            phase="pre_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )

        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        # The single-voice subject is untouched pre-vote -- the channel
        # is invisible until independence is met.
        assert "p-2" not in updated.known_players()

    def test_pre_vote_applies_corroborations_same_phase(self) -> None:
        # Same-phase symmetry (audit C-C-3 "corroborations must move at
        # the SAME phase as accusations"): a defended subject is cleared
        # before ballots, in the same half the folded bumps move.
        beliefs = BeliefState()
        beliefs.seed_player("p-3", suspicion=0.58, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=(),
            corroborated=("p-3",),
            phase="pre_vote",
        )

        assert updated.view("p-3").suspicion == pytest.approx(
            0.58 - CORROBORATION_SUSPICION_DELTA
        )

    def test_pre_vote_never_decays(self) -> None:
        # Rule 5 belongs to the post-vote half; an uninvolved row is
        # byte-untouched by the pre-vote fold.
        beliefs = BeliefState()
        beliefs.seed_player("p-7", suspicion=0.7, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=("p-5",),
            phase="pre_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )

        assert updated.view("p-7").suspicion == pytest.approx(0.7)

    def test_post_vote_skips_the_folded_subjects_bump(self) -> None:
        # The pre-vote fold REPLACES the post-vote accused-bump for that
        # subject-meeting: the post-vote half demonstrably skips it,
        # while the single-voice subject takes its bump exactly as
        # before 10.7.
        updated = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("p-2", "p-5"),
            phase="post_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )

        assert updated.view("p-2").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert "p-5" not in updated.known_players()

    def test_post_vote_applies_no_corroboration_delta_but_exempts_decay(
        self,
    ) -> None:
        # The corroboration delta moved pre-vote; post-vote the
        # corroborated subject is still REINFORCED (new evidence this
        # meeting), so Rule 5 does not erode them either.
        beliefs = BeliefState()
        beliefs.seed_player("p-3", suspicion=0.55, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=(),
            corroborated=("p-3",),
            phase="post_vote",
        )

        assert updated.view("p-3").suspicion == pytest.approx(0.55)

    def test_post_vote_decay_exempts_folded_subjects(self) -> None:
        # A folded subject got new evidence this meeting: the post-vote
        # half skips its bump AND its decay -- the bump landed pre-vote
        # and must not erode in the same meeting.
        beliefs = BeliefState()
        beliefs.seed_player(
            "p-5",
            suspicion=_DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA,
            trust=0.5,
        )

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=("p-5",),
            phase="post_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )

        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )

    def test_phases_compose_to_the_default_call(self) -> None:
        # THE function-level double-fold guard: pre_vote then post_vote
        # over the same evidence equals the composed default call -- each
        # accused subject is bumped exactly once whichever half carried
        # it, corroborations land once, decay runs once.
        beliefs = BeliefState()
        beliefs.seed_player("p-2", suspicion=0.55, trust=0.5)
        beliefs.seed_player("p-7", suspicion=0.7, trust=0.5)
        evidence: Mapping[str, Sequence[str]] = {
            "accused": ["p-2", "p-5"],
            "corroborated": ["p-3"],
            "contradicted": ["p-6"],
        }

        composed = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=evidence["accused"],
            corroborated=evidence["corroborated"],
            contradicted=evidence["contradicted"],
        )
        pre = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=evidence["accused"],
            corroborated=evidence["corroborated"],
            contradicted=evidence["contradicted"],
            phase="pre_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )
        split = apply_meeting_evidence_rules(
            pre,
            own_id="observer",
            accused=evidence["accused"],
            corroborated=evidence["corroborated"],
            contradicted=evidence["contradicted"],
            phase="post_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )

        assert _snapshot(split) == _snapshot(composed)

    def test_folded_subject_per_meeting_total_equals_unfolded(self) -> None:
        # The DoD double-fold pin at the store level: run the two-phase
        # protocol with the subject FOLDED and the composed call with the
        # subject unfolded -- the persistent per-meeting total is the
        # identical single +0.05 either way.
        evidence: Mapping[str, Sequence[str]] = {"accused": ["p-5"]}

        folded_pre = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=evidence["accused"],
            phase="pre_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )
        folded_total = apply_meeting_evidence_rules(
            folded_pre,
            own_id="observer",
            accused=evidence["accused"],
            phase="post_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )
        unfolded_total = _absorb_meetings(BeliefState(), [evidence])

        assert folded_total.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert _snapshot(folded_total) == _snapshot(unfolded_total)

    def test_default_call_result_is_independent_of_folded_marks(self) -> None:
        # The composed call (the standing post-meeting absorb shape)
        # bumps each accused subject exactly once whether or not the
        # caller marks it folded -- the persistent path cannot
        # double-fold by construction.
        with_marks = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("p-2", "p-5"),
            pre_vote_folded=frozenset({"p-5"}),
        )
        without_marks = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("p-2", "p-5"),
        )

        assert _snapshot(with_marks) == _snapshot(without_marks)

    def test_teammate_guard_holds_on_the_pre_vote_channel(self) -> None:
        # DESIGN.md §4.7 (the 7.12/9.3 firewall) applies to the new
        # channel: an impostor listener never takes a pre-vote testimony
        # bump against a fellow impostor, however many voices stood
        # behind the accusation.
        updated = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("p-2", "p-5"),
            fellow_impostor_ids=("p-2",),
            phase="pre_vote",
            pre_vote_folded=frozenset({"p-2", "p-5"}),
        )

        assert "p-2" not in updated.known_players()
        assert updated.view("p-5").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )

    def test_own_id_is_excluded_from_the_pre_vote_channel(self) -> None:
        updated = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("observer",),
            phase="pre_vote",
            pre_vote_folded=frozenset({"observer"}),
        )

        assert updated.known_players() == ()

    def test_roster_filter_applies_to_the_folded_channel(self) -> None:
        updated = apply_meeting_evidence_rules(
            BeliefState(),
            own_id="observer",
            accused=("headless-seed-9",),
            roster=frozenset({"observer", "p-5"}),
            phase="pre_vote",
            pre_vote_folded=frozenset({"headless-seed-9"}),
        )

        assert updated.known_players() == ()

    def test_folded_subject_nobody_accused_fails_loud(self) -> None:
        # A folded subject outside ``accused`` is caller drift between
        # the evidence derivation and the fold -- never silently ignored
        # (AGENTS.md "no silent fallbacks").
        with pytest.raises(ValueError, match="pre_vote_folded"):
            apply_meeting_evidence_rules(
                BeliefState(),
                own_id="observer",
                accused=("p-2",),
                phase="pre_vote",
                pre_vote_folded=frozenset({"p-5"}),
            )

    def test_phase_calls_are_pure_and_deterministic(self) -> None:
        beliefs = BeliefState()
        beliefs.seed_player("p-5", suspicion=0.55, trust=0.5)
        before = _snapshot(beliefs)

        first = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=("p-5",),
            phase="pre_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )
        second = apply_meeting_evidence_rules(
            beliefs,
            own_id="observer",
            accused=("p-5",),
            phase="pre_vote",
            pre_vote_folded=frozenset({"p-5"}),
        )

        assert _snapshot(beliefs) == before
        assert _snapshot(first) == _snapshot(second)


# ---------------------------------------------------------------------------
# Task 10.6: the Rule-3 relevance gate at the fold, walked on committed bytes
# (audit gp-2 C-C-3 -- the seed-6 cancellation byte walk).
# ---------------------------------------------------------------------------


class TestRelevanceGatedFoldOnCommittedBytes:
    """The seed-6 trajectory pin: gated Rule 3 lets accusation carry climb.

    Audit C-C-3: impostor p-6 was accused in m0+m1+m2 yet rendered flat
    0.5/0.5/0.55 -- each meeting's accusation bump cancelled in-meeting by
    an evidentially-empty Rule-3 vouch (at m1, the accuser's OWN
    kill-scene sighting: p-6 in ADMIN@16, where p-6 had just killed p-4,
    body found @17). Under the relevance gate the kill-scene vouches die,
    so the re-derived cross-meeting fold RISES across the accused
    meetings instead of netting to zero.
    """

    def _seed6_trajectory(self) -> list[float]:
        from pathlib import Path

        from meetings.manager import extract_belief_evidence
        from meetings.schemas import MeetingResult
        from orchestrator.replay import MeetingReplayEntry, read_all_entries

        replay = (
            Path(__file__).resolve().parents[2]
            / "replays"
            / "samples"
            / "9p2i"
            / "replay-seed-6.jsonl"
        )
        beliefs = BeliefState()
        trajectory: list[float] = []
        for entry in read_all_entries(replay):
            if not isinstance(entry, MeetingReplayEntry):
                continue
            result = MeetingResult(
                meeting_id=entry.meeting_id,
                triggered_by=entry.transcript.turns[0].speaker,
                trigger_tick=0,
                outcome=entry.outcome,
                ejected_player_id=entry.ejected_player_id,
                ballots=entry.ballots,
                contradictions=entry.contradictions,
                transcript=entry.transcript,
            )
            evidence = extract_belief_evidence(result)
            beliefs = apply_meeting_evidence_rules(
                beliefs,
                own_id="observer",
                accused=evidence.accused,
                corroborated=evidence.corroborated,
                contradicted=evidence.contradicted,
            )
            trajectory.append(beliefs.view("p-6").suspicion)
        return trajectory

    def test_seed6_p6_trajectory_rises_instead_of_rendering_flat(self) -> None:
        trajectory = self._seed6_trajectory()

        # Four committed meetings; p-6 is accused in m0/m1/m2. Pre-gate
        # the fold read 0.5 / 0.5 / 0.55 / ... (m0's and m1's bumps each
        # cancelled by a same-meeting vouch -- m0's survives the gate as a
        # genuine EAST_HALL@8 sighting, m1's was the kill-scene vouch and
        # dies). Post-gate: m1's and m2's bumps land uncancelled and the
        # trajectory CLIMBS to the 0.60 gate by m2.
        assert len(trajectory) == 4
        assert trajectory[0] == pytest.approx(0.5)
        assert trajectory[1] == pytest.approx(0.5 + ACCUSATION_SUSPICION_DELTA)
        assert trajectory[2] == pytest.approx(0.5 + 2 * ACCUSATION_SUSPICION_DELTA)
        # Strictly rising across the accused meetings -- the flat-render
        # cancellation is gone.
        assert trajectory[1] > trajectory[0]
        assert trajectory[2] > trajectory[1]

    def test_corroboration_magnitude_is_untouched(self) -> None:
        # "No constant changes": the gate filters subjects, never re-tunes
        # the §6.3 weights (freeze-during-measurement).
        assert CORROBORATION_SUSPICION_DELTA == 0.05
        assert ACCUSATION_SUSPICION_DELTA == 0.05
