from __future__ import annotations

from collections.abc import Mapping, Sequence

import pytest

from agents.memory.beliefs import (
    BODY_PROXIMITY_SUSPICION_DELTA,
    BeliefState,
    PlayerBelief,
    VENTING_SUSPICION_DELTA,
    apply_observation_rules,
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
