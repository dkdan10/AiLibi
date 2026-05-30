"""Wiring tests for the dormant belief substrate (Task 6.4).

Two audit findings are covered here:

* **J-J-4** — belief Rule 2 (DESIGN.md §6.3 "+0.3 suspicion if claimed
  alibi contradicts another agent's testimony") was defined but never
  called in production. :func:`agents.memory.beliefs.apply_contradiction_rule`
  is the agents-side write-path that calls ``record_contradiction`` +
  ``adjust_suspicion`` on a detected contradiction; these tests assert the
  suspicion graph reflects the detected lie.
* **A-A-4** — :class:`agents.runtime.AgentRuntime` called ``ingest_packet``
  without a :class:`BeliefState`, leaving the implemented Rules 1 and 4
  dormant in headless games. These tests assert the runtime now threads a
  belief state so a witnessed-vent (Rule 4) update occurs in a headless run.
"""

from __future__ import annotations

import pytest

from agents.memory.beliefs import (
    CONTRADICTION_SUSPICION_DELTA,
    VENTING_SUSPICION_DELTA,
    BeliefState,
    apply_contradiction_rule,
)
from agents.memory.episodic import MemoryStore
from agents.runtime import AgentRuntime
from meetings.schemas import ContradictionRef
from observation.packet import (
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView

_DEFAULT_SUSPICION = 0.5


def _public_map() -> PublicMapView:
    return PublicMapView(
        map_id="canonical_1",
        room_ids=("ADMIN", "ELECTRICAL"),
        room_neighbors={"ADMIN": ("ELECTRICAL",), "ELECTRICAL": ("ADMIN",)},
        vent_graph={},
        vent_rooms={},
        task_locations={"swipe_card": "ADMIN"},
        spawn_room="ELECTRICAL",
        meeting_room="ELECTRICAL",
        emergency_button_room="ELECTRICAL",
    )


def _packet(
    *,
    agent_id: str = "p1",
    tick: int = 5,
    room: str = "ELECTRICAL",
    visible_players: tuple[PlayerView, ...] = (),
) -> ObservationPacket:
    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(room=room, role="CREWMATE", pending_task_id=None),
        visible_players=visible_players,
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


def _contradiction(*, subject: str) -> ContradictionRef:
    return ContradictionRef(
        contradiction_id=f"contra:alibi_conflict:{subject}",
        kind="alibi_conflict",
        event_a_id="report:p-1@10:claim:0",
        event_b_id="report:p-2@10:claim:0",
        subjects=(subject,),
        description=f"Alibis place {subject} in two rooms over overlapping ticks.",
    )


class TestBeliefRule2:
    """DESIGN.md §6.3 Rule 2 wiring (audit J-J-4)."""

    def test_detected_contradiction_raises_subject_suspicion(self) -> None:
        beliefs = BeliefState()

        updated = apply_contradiction_rule(beliefs, [_contradiction(subject="p-3")])

        assert updated.view("p-3").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + CONTRADICTION_SUSPICION_DELTA
        )

    def test_detected_contradiction_records_inconsistency(self) -> None:
        beliefs = BeliefState()

        updated = apply_contradiction_rule(beliefs, [_contradiction(subject="p-3")])

        inconsistencies = updated.view("p-3").inconsistencies
        assert len(inconsistencies) == 1
        assert inconsistencies[0].left_ref == "report:p-1@10:claim:0"
        assert inconsistencies[0].right_ref == "report:p-2@10:claim:0"

    def test_apply_contradiction_rule_is_pure(self) -> None:
        beliefs = BeliefState()

        apply_contradiction_rule(beliefs, [_contradiction(subject="p-3")])

        # The input state is untouched; the rule returns a fresh state.
        assert beliefs.view("p-3").suspicion == _DEFAULT_SUSPICION
        assert beliefs.view("p-3").inconsistencies == ()

    def test_multiple_subjects_each_get_bumped(self) -> None:
        beliefs = BeliefState()
        flag = ContradictionRef(
            contradiction_id="contra:alibi_conflict:multi",
            kind="alibi_conflict",
            event_a_id="a",
            event_b_id="b",
            subjects=("p-3", "p-5"),
            description="multi-subject conflict",
        )

        updated = apply_contradiction_rule(beliefs, [flag])

        for subject in ("p-3", "p-5"):
            assert updated.view(subject).suspicion == pytest.approx(
                _DEFAULT_SUSPICION + CONTRADICTION_SUSPICION_DELTA
            )

    def test_no_contradictions_leaves_state_unchanged(self) -> None:
        beliefs = BeliefState()
        beliefs.adjust_suspicion("p-3", delta=0.1)

        updated = apply_contradiction_rule(beliefs, [])

        assert updated.view("p-3").suspicion == pytest.approx(_DEFAULT_SUSPICION + 0.1)


class TestRuntimeBeliefPerception:
    """AgentRuntime threads a BeliefState into perception (audit A-A-4)."""

    def test_runtime_owns_belief_state_when_memory_present(self) -> None:
        runtime = AgentRuntime(agent_id="p1", memory=MemoryStore())

        assert runtime.beliefs is not None

    def test_runtime_without_memory_has_no_belief_state(self) -> None:
        runtime = AgentRuntime(agent_id="p1")

        assert runtime.beliefs is None

    def test_witnessed_vent_updates_belief_in_headless_run(self) -> None:
        # Rule 4: a witnessed vent (a visible player whose action is "vent")
        # must lift that player's suspicion when the runtime drives a tick in
        # a headless game — the runtime must pass its BeliefState into
        # ingest_packet for the rule to fire.
        runtime = AgentRuntime(agent_id="p1", memory=MemoryStore())
        packet = _packet(
            visible_players=(PlayerView(id="p2", room="ELECTRICAL", action="vent"),)
        )

        runtime.decide(packet, _public_map())

        assert runtime.beliefs is not None
        assert runtime.beliefs.view("p2").suspicion == pytest.approx(
            _DEFAULT_SUSPICION + VENTING_SUSPICION_DELTA
        )

    def test_injected_belief_state_is_used(self) -> None:
        shared = BeliefState()
        runtime = AgentRuntime(agent_id="p1", memory=MemoryStore(), beliefs=shared)

        runtime.decide(
            _packet(
                visible_players=(PlayerView(id="p2", room="ELECTRICAL", action="vent"),)
            ),
            _public_map(),
        )

        # The injected instance is the one updated in place.
        assert runtime.beliefs is shared
        assert shared.view("p2").suspicion > _DEFAULT_SUSPICION
