from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest

from agents.memory.beliefs import (
    BODY_PROXIMITY_SUSPICION_DELTA,
    CONTRADICTION_SUSPICION_DELTA,
    WEAK_CONTRADICTION_SUSPICION_DELTA,
    BeliefState,
    PlayerBelief,
    VENTING_SUSPICION_DELTA,
    apply_contradiction_rule,
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
        # Two independent weak signals (e.g. two third-party sightings
        # against the same self-stated alibi) ARE corroboration: the
        # subject stays ejectable, the lone-signal railroad is gone.
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

    def test_weak_plus_strong_crosses_gate(self) -> None:
        updated = apply_contradiction_rule(
            BeliefState(),
            [
                _meeting_flag(subject="p-5", weak=True, pair="a|b"),
                _meeting_flag(subject="p-5", weak=False, pair="c|d"),
            ],
        )

        suspicion = updated.view("p-5").suspicion
        assert suspicion == pytest.approx(
            _DEFAULT_SUSPICION
            + WEAK_CONTRADICTION_SUSPICION_DELTA
            + CONTRADICTION_SUSPICION_DELTA
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

    def test_marker_on_alibi_conflict_keeps_full_weight(self) -> None:
        # The graduated delta is kind-gated to alibi_vs_sighting; an
        # alibi_conflict is two positive claims that cannot both be true
        # and keeps the full Rule-2 weight even if its description ever
        # carried the marker text.
        updated = apply_contradiction_rule(
            BeliefState(),
            [_meeting_flag(subject="p-5", weak=True, kind="alibi_conflict")],
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
