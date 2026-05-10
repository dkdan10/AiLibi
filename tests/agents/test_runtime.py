from __future__ import annotations

import pytest
from pydantic import TypeAdapter

from agents.base import AgentInterface
from agents.runtime import AgentRuntime
from observation.action_intent import ActionIntent, MoveIntent, WaitIntent
from observation.packet import GlobalView, ObservationPacket, PlayerId, SelfView
from observation.public_map import PublicMapView

_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)


def _public_map() -> PublicMapView:
    return PublicMapView(
        map_id="canonical_1",
        room_ids=("ADMIN", "CAFETERIA"),
        room_neighbors={"ADMIN": ("CAFETERIA",), "CAFETERIA": ("ADMIN",)},
        vent_graph={},
        vent_rooms={},
        task_locations={"swipe_card": "ADMIN"},
        spawn_room="CAFETERIA",
        meeting_room="CAFETERIA",
        emergency_button_room="CAFETERIA",
    )


def _packet(*, agent_id: PlayerId = "p1") -> ObservationPacket:
    return ObservationPacket(
        tick=0,
        agent_id=agent_id,
        self_state=SelfView(room="CAFETERIA", role="CREWMATE", pending_task_id=None),
        visible_players=(),
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


def test_agent_runtime_satisfies_agent_interface_protocol() -> None:
    runtime = AgentRuntime(agent_id="p1")

    assert isinstance(runtime, AgentInterface)


def test_agent_runtime_decide_returns_wait_intent_by_default() -> None:
    runtime = AgentRuntime(agent_id="p1")

    intent = runtime.decide(_packet(), _public_map())

    assert isinstance(intent, WaitIntent)
    assert intent.type == "wait"
    assert intent.actor == "p1"


def test_agent_runtime_decide_rejects_packet_for_other_agent() -> None:
    runtime = AgentRuntime(agent_id="p1")

    with pytest.raises(ValueError, match="p2"):
        runtime.decide(_packet(agent_id="p2"), _public_map())


def test_agent_runtime_decide_invokes_hooks_in_perception_memory_tactical_order() -> (
    None
):
    calls: list[str] = []
    intent = _INTENT_ADAPTER.validate_python(
        {"type": "move", "actor": "p1", "payload": {"to_room": "ADMIN"}}
    )
    assert isinstance(intent, MoveIntent)

    class _RecordingRuntime(AgentRuntime):
        def _perceive(
            self,
            packet: ObservationPacket,
            public_map: PublicMapView,
        ) -> tuple[object, ...]:
            calls.append("perceive")
            return ("event",)

        def _update_memory(self, events: tuple[object, ...]) -> None:
            calls.append(f"memory:{events}")

        def _choose_action(
            self,
            packet: ObservationPacket,
            public_map: PublicMapView,
        ) -> ActionIntent:
            calls.append("tactical")
            return intent

    runtime = _RecordingRuntime(agent_id="p1")

    result = runtime.decide(_packet(), _public_map())

    assert calls == ["perceive", "memory:('event',)", "tactical"]
    assert result is intent


def test_agent_runtime_default_perceive_and_update_memory_are_pure_stubs() -> None:
    runtime = AgentRuntime(agent_id="p1")

    events = runtime._perceive(_packet(), _public_map())

    assert events == ()
    runtime._update_memory(events)


def test_agent_runtime_exposes_agent_id_property() -> None:
    runtime = AgentRuntime(agent_id="p1")

    assert runtime.agent_id == "p1"
