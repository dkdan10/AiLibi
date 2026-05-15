from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
)
from agents.tactical.crewmate_policy import (
    KILL_ACTION,
    KILL_WITNESS_REASON,
    CrewmatePolicy,
)
from observation.action_intent import (
    DoTaskIntent,
    EmergencyMeetingIntent,
    MoveIntent,
    ReportBodyIntent,
    WaitIntent,
)
from observation.public_map import PublicMapView, RoomId


def _public_map(
    *,
    rooms: tuple[RoomId, ...] = ("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
    neighbors: Mapping[RoomId, tuple[RoomId, ...]] | None = None,
    task_locations: Mapping[str, RoomId] | None = None,
    emergency_button_room: RoomId = "CAFETERIA",
    meeting_room: RoomId = "CAFETERIA",
    spawn_room: RoomId = "CAFETERIA",
) -> PublicMapView:
    if neighbors is None:
        neighbors = {
            "ADMIN": ("CAFETERIA",),
            "CAFETERIA": ("ADMIN", "ELECTRICAL", "MEDBAY"),
            "ELECTRICAL": ("CAFETERIA",),
            "MEDBAY": ("CAFETERIA",),
        }
    if task_locations is None:
        task_locations = {"swipe_card": "ADMIN", "wires_electrical": "ELECTRICAL"}
    return PublicMapView(
        map_id="test_map",
        room_ids=rooms,
        room_neighbors=neighbors,
        vent_graph={},
        vent_rooms={},
        task_locations=task_locations,
        spawn_room=spawn_room,
        meeting_room=meeting_room,
        emergency_button_room=emergency_button_room,
    )


def _self_state_event(
    *,
    tick: int,
    room: RoomId,
    pending_task_id: str | None,
    role: str = "CREWMATE",
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "room": room,
        "role": role,
        "pending_task_id": pending_task_id,
    }
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SELF_STATE,
        payload=payload,
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_body_event(*, tick: int, body_id: str, room: RoomId) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_BODY,
        payload={"body_id": body_id, "room": room},
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_player_event(
    *,
    tick: int,
    player_id: str,
    room: RoomId,
    action: str | None,
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_PLAYER,
        payload={"player_id": player_id, "room": room, "action": action},
        provenance=PROVENANCE_OBSERVED,
    )


def _store_with(*events: EpisodicEvent) -> MemoryStore:
    store = MemoryStore()
    for event in events:
        store.append(event)
    return store


class TestCrewmateNormalFsm:
    def test_idle_with_no_pending_task_returns_wait(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)
        assert intent.actor == "p1"

    def test_do_task_when_already_in_task_room(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, DoTaskIntent)
        assert intent.payload.task_id == "swipe_card"
        assert intent.actor == "p1"

    def test_move_toward_task_returns_first_step_on_a_star_path(self) -> None:
        # CAFETERIA -> ADMIN is a one-hop neighbour: next step is ADMIN itself.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="swipe_card"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"
        assert intent.actor == "p1"

    def test_move_toward_task_takes_one_hop_along_multi_room_path(self) -> None:
        # Chain: ADMIN <-> CAFETERIA <-> ELECTRICAL. From ADMIN to ELECTRICAL,
        # the first step must be CAFETERIA.
        store = _store_with(
            _self_state_event(
                tick=10, room="ADMIN", pending_task_id="wires_electrical"
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    def test_pending_task_with_unknown_location_falls_back_to_wait(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="ghost_task"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)


class TestCrewmateBodyVisibleInterrupt:
    def test_visible_body_triggers_report_intent(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY", pending_task_id="swipe_card"),
            _saw_body_event(tick=10, body_id="p3-body", room="MEDBAY"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, ReportBodyIntent)
        assert intent.payload.body_id == "p3-body"
        assert intent.actor == "p1"

    def test_body_visible_overrides_pending_task_movement(self) -> None:
        # Even though the agent has a task in ADMIN, the body in the current
        # room takes priority and the agent reports.
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY", pending_task_id="swipe_card"),
            _saw_body_event(tick=10, body_id="p3-body", room="MEDBAY"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, ReportBodyIntent)

    def test_multiple_visible_bodies_break_ties_alphabetically(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY", pending_task_id=None),
            _saw_body_event(tick=10, body_id="p7-body", room="MEDBAY"),
            _saw_body_event(tick=10, body_id="p3-body", room="MEDBAY"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, ReportBodyIntent)
        assert intent.payload.body_id == "p3-body"

    def test_stale_body_event_from_earlier_tick_does_not_trigger_report(self) -> None:
        # A body seen on an earlier tick is no longer visible. Only events at
        # the latest tick can fire BODY_VISIBLE.
        store = _store_with(
            _self_state_event(tick=5, room="MEDBAY", pending_task_id=None),
            _saw_body_event(tick=5, body_id="p3-body", room="MEDBAY"),
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)


class TestCrewmateKillWitnessedInterrupt:
    def test_kill_in_current_room_routes_toward_emergency_button_room(self) -> None:
        # Agent is in ELECTRICAL when a kill happens; emergency button is in
        # CAFETERIA. Path is ELECTRICAL -> CAFETERIA, so we move to CAFETERIA.
        store = _store_with(
            _self_state_event(tick=10, room="ELECTRICAL", pending_task_id=None),
            _saw_player_event(
                tick=10, player_id="p2", room="ELECTRICAL", action=KILL_ACTION
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    def test_kill_witness_when_already_in_emergency_room_calls_meeting(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
            _saw_player_event(
                tick=10, player_id="p2", room="CAFETERIA", action=KILL_ACTION
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, EmergencyMeetingIntent)
        assert intent.payload.reason == KILL_WITNESS_REASON
        assert intent.actor == "p1"

    def test_kill_in_other_room_is_ignored(self) -> None:
        # The kill action is reported by perception with a room mismatch
        # (defensive: we only react to kills in the agent's own room).
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
            _saw_player_event(
                tick=10, player_id="p2", room="ELECTRICAL", action=KILL_ACTION
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        # No interrupt fires; agent is in ADMIN with the task in ADMIN -> DO_TASK.
        assert isinstance(intent, DoTaskIntent)

    def test_non_kill_player_action_does_not_trigger_flee(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="swipe_card"),
            _saw_player_event(tick=10, player_id="p2", room="CAFETERIA", action="task"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"

    def test_body_visible_takes_priority_over_kill_witnessed(self) -> None:
        # If both interrupts fire on the same tick, BODY_VISIBLE wins.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
            _saw_player_event(
                tick=10, player_id="p2", room="CAFETERIA", action=KILL_ACTION
            ),
            _saw_body_event(tick=10, body_id="p9-body", room="CAFETERIA"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, ReportBodyIntent)
        assert intent.payload.body_id == "p9-body"


class TestCrewmateDeterminism:
    def test_repeated_decide_calls_return_equal_intents(self) -> None:
        store = _store_with(
            _self_state_event(
                tick=10, room="ADMIN", pending_task_id="wires_electrical"
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")
        public_map = _public_map()

        intents = [policy.decide(store, public_map) for _ in range(5)]

        first = intents[0]
        assert isinstance(first, MoveIntent)
        for intent in intents:
            assert isinstance(intent, MoveIntent)
            assert intent.payload.to_room == first.payload.to_room
            assert intent.actor == first.actor

    def test_path_choice_is_independent_of_neighbor_listing_order(self) -> None:
        # Diamond graph ADMIN -> {B, C} -> ELECTRICAL. With sorted-id tie-
        # breaking the path through "B" must win regardless of the input order.
        neighbors_forward = {
            "ADMIN": ("B", "C"),
            "B": ("ADMIN", "ELECTRICAL"),
            "C": ("ADMIN", "ELECTRICAL"),
            "ELECTRICAL": ("B", "C"),
        }
        neighbors_reverse = {
            "ADMIN": ("C", "B"),
            "B": ("ELECTRICAL", "ADMIN"),
            "C": ("ELECTRICAL", "ADMIN"),
            "ELECTRICAL": ("C", "B"),
        }
        rooms = ("ADMIN", "B", "C", "ELECTRICAL")
        store = _store_with(
            _self_state_event(
                tick=10, room="ADMIN", pending_task_id="wires_electrical"
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent_forward = policy.decide(
            store,
            _public_map(
                rooms=rooms,
                neighbors=neighbors_forward,
                task_locations={"wires_electrical": "ELECTRICAL"},
                emergency_button_room="ADMIN",
                meeting_room="ADMIN",
                spawn_room="ADMIN",
            ),
        )
        intent_reverse = policy.decide(
            store,
            _public_map(
                rooms=rooms,
                neighbors=neighbors_reverse,
                task_locations={"wires_electrical": "ELECTRICAL"},
                emergency_button_room="ADMIN",
                meeting_room="ADMIN",
                spawn_room="ADMIN",
            ),
        )

        assert isinstance(intent_forward, MoveIntent)
        assert isinstance(intent_reverse, MoveIntent)
        assert intent_forward.payload.to_room == "B"
        assert intent_reverse.payload.to_room == "B"


class TestCrewmateInputValidation:
    def test_decide_raises_when_memory_is_empty(self) -> None:
        policy = CrewmatePolicy(agent_id="p1")

        with pytest.raises(ValueError, match="at least one episodic event"):
            policy.decide(MemoryStore(), _public_map())

    def test_decide_raises_when_no_self_state_event_present(self) -> None:
        store = _store_with(
            _saw_body_event(tick=10, body_id="p3-body", room="MEDBAY"),
        )
        policy = CrewmatePolicy(agent_id="p1")

        with pytest.raises(ValueError, match="self_state event"):
            policy.decide(store, _public_map())


class TestCrewmateAgentIdProperty:
    def test_agent_id_is_exposed_as_property(self) -> None:
        policy = CrewmatePolicy(agent_id="p7")

        assert policy.agent_id == "p7"


class TestCrewmateTaskCompletionCycle:
    def test_consecutive_decide_calls_yield_do_task_until_completion(self) -> None:
        # Drive a full task-completion cycle through CrewmatePolicy.decide:
        # the crewmate sits at the task room across several ticks with a
        # pending task; the policy must emit DoTaskIntent every tick until
        # the task completes and pending_task_id becomes None.
        store = MemoryStore()
        public_map = _public_map(task_locations={"swipe_card": "ADMIN"})
        policy = CrewmatePolicy(agent_id="p-1")

        # While pending_task_id is set, consecutive decide() calls must
        # return DoTaskIntent for the matching task_id.
        for tick in range(5):
            store.append(
                _self_state_event(tick=tick, room="ADMIN", pending_task_id="swipe_card")
            )
            intent = policy.decide(store, public_map)
            assert isinstance(intent, DoTaskIntent), (
                f"tick {tick}: expected DoTaskIntent, got {type(intent).__name__}"
            )
            assert intent.payload.task_id == "swipe_card"

        # After completion the agent stops emitting DoTaskIntent.
        store.append(_self_state_event(tick=5, room="ADMIN", pending_task_id=None))
        intent = policy.decide(store, public_map)
        assert not isinstance(intent, DoTaskIntent)

    def test_body_in_adjacent_room_does_not_interrupt_task_completion(self) -> None:
        # Regression: bodies in *adjacent* rooms are visible to the agent
        # (perception emits saw_body events for them) but
        # ReportBodyAction requires the actor to share the body's room.
        # The BODY_VISIBLE -> REPORT interrupt must restrict itself to
        # bodies in the agent's own room, otherwise the crewmate fires
        # ReportBodyIntent forever and the engine rejects every one,
        # blocking the IDLE -> MOVE_TO_TASK -> DO_TASK cycle.
        store = MemoryStore()
        public_map = _public_map(task_locations={"swipe_card": "ADMIN"})
        policy = CrewmatePolicy(agent_id="p-1")

        # Body sits in CAFETERIA (adjacent to ADMIN). At every tick the
        # crewmate is at the task room with the task pending; the policy
        # must continue emitting DoTaskIntent until the task completes,
        # ignoring the unreachable body interrupt.
        for tick in range(5):
            store.append(
                _self_state_event(tick=tick, room="ADMIN", pending_task_id="swipe_card")
            )
            store.append(
                _saw_body_event(tick=tick, body_id="leftover-body", room="CAFETERIA")
            )
            intent = policy.decide(store, public_map)
            assert isinstance(intent, DoTaskIntent), (
                f"tick {tick}: expected DoTaskIntent, got {type(intent).__name__}"
            )
            assert intent.payload.task_id == "swipe_card"


class TestCrewmateIdleHubRouting:
    def test_idle_with_no_pending_task_at_meeting_room_returns_wait(self) -> None:
        # When the crewmate is already at the meeting room with nothing
        # tactical to do, IDLE means wait. This is the natural terminal
        # state of the IDLE -> MOVE_TO_TASK -> DO_TASK -> IDLE FSM.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)

    def test_idle_with_no_pending_task_away_from_meeting_room_moves_back(self) -> None:
        # IDLE crewmate not at the meeting room walks one A* step toward it.
        # Without this routing the surviving crewmates would stay inside
        # their finished task rooms and never re-enter the impostor's
        # visibility window.
        store = _store_with(
            _self_state_event(tick=10, room="ELECTRICAL", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    def test_idle_with_disconnected_meeting_room_falls_back_to_wait(self) -> None:
        # If the meeting room is unreachable from the crewmate's current
        # room (degenerate map), routing fails and the policy degrades
        # to WaitIntent instead of raising.
        rooms = ("ADMIN", "CAFETERIA", "ELECTRICAL")
        neighbors: Mapping[RoomId, tuple[RoomId, ...]] = {
            "ADMIN": (),
            "CAFETERIA": ("ELECTRICAL",),
            "ELECTRICAL": ("CAFETERIA",),
        }
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(
            store,
            _public_map(
                rooms=rooms,
                neighbors=neighbors,
                task_locations={},
                meeting_room="CAFETERIA",
                emergency_button_room="CAFETERIA",
                spawn_room="ADMIN",
            ),
        )

        assert isinstance(intent, WaitIntent)


class TestCrewmateBodyInAdjacentRoom:
    def test_body_in_adjacent_room_does_not_trigger_report(self) -> None:
        # Bodies in adjacent rooms appear in saw_body events because
        # the agent can see them, but the engine rejects ReportBodyAction
        # unless the actor shares the body's room. The interrupt must
        # only fire when the report would actually succeed.
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY", pending_task_id="swipe_card"),
            _saw_body_event(tick=10, body_id="leftover-body", room="CAFETERIA"),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        # The body sits in CAFETERIA (adjacent to MEDBAY). Without the
        # own-room filter the policy would emit ReportBodyIntent (which
        # the engine then rejects); with the filter the policy routes
        # toward the pending task.
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"


class TestCrewmateDisconnectedGoal:
    def test_disconnected_task_room_falls_back_to_wait(self) -> None:
        # ADMIN sits in its own component; ELECTRICAL is unreachable from there.
        rooms = ("ADMIN", "CAFETERIA", "ELECTRICAL")
        neighbors: Mapping[RoomId, tuple[RoomId, ...]] = {
            "ADMIN": (),
            "CAFETERIA": ("ELECTRICAL",),
            "ELECTRICAL": ("CAFETERIA",),
        }
        store = _store_with(
            _self_state_event(
                tick=10, room="ADMIN", pending_task_id="wires_electrical"
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(
            store,
            _public_map(
                rooms=rooms,
                neighbors=neighbors,
                task_locations={"wires_electrical": "ELECTRICAL"},
                emergency_button_room="ADMIN",
                meeting_room="ADMIN",
                spawn_room="ADMIN",
            ),
        )

        assert isinstance(intent, WaitIntent)
        assert intent.actor == "p1"

    def test_disconnected_emergency_room_under_kill_witness_falls_back_to_wait(
        self,
    ) -> None:
        # Agent witnesses a kill in their own room, but the emergency button
        # room is unreachable: crewmate must emit WaitIntent instead of raising.
        rooms = ("ADMIN", "CAFETERIA", "ELECTRICAL")
        neighbors: Mapping[RoomId, tuple[RoomId, ...]] = {
            "ADMIN": (),
            "CAFETERIA": ("ELECTRICAL",),
            "ELECTRICAL": ("CAFETERIA",),
        }
        store = _store_with(
            _self_state_event(tick=10, room="ELECTRICAL", pending_task_id=None),
            _saw_player_event(
                tick=10, player_id="p2", room="ELECTRICAL", action=KILL_ACTION
            ),
        )
        policy = CrewmatePolicy(agent_id="p1")

        intent = policy.decide(
            store,
            _public_map(
                rooms=rooms,
                neighbors=neighbors,
                task_locations={},
                emergency_button_room="ADMIN",
                meeting_room="ADMIN",
                spawn_room="ADMIN",
            ),
        )

        assert isinstance(intent, WaitIntent)
        assert intent.actor == "p1"
