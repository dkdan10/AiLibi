from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import Any

import pytest

from agents.memory.beliefs import BeliefState
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
)
from agents.tactical.crewmate_policy import (
    EMERGENCY_COOLDOWN_TICKS,
    KILL_ACTION,
    KILL_WITNESS_REASON,
    SUSPICION_ACCUMULATION_REASON,
    CrewmatePolicy,
    EmergencyButtonView,
    EmergencyPacingTracker,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from meetings.manager import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
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


def _saw_body_event(
    *,
    tick: int,
    body_id: str,
    room: RoomId,
    victim_id: str | None = None,
) -> EpisodicEvent:
    payload: dict[str, Any] = {"body_id": body_id, "room": room}
    if victim_id is not None:
        payload["victim_id"] = victim_id
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_BODY,
        payload=payload,
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


# ---------------------------------------------------------------------------
# Task 10.8 — suspicion-accumulation emergency trigger (DESIGN.md §3.2, §5.2;
# audit gp-3 B-B-4): EmergencyPacingTracker bookkeeping pins, the policy-side
# trigger beside the witnessed-kill interrupt, and the impostor non-behavior
# assertion.
# ---------------------------------------------------------------------------

_GATE = DEFAULT_SKIP_CONFIDENCE_THRESHOLD


def _beliefs_with(suspicions: Mapping[str, float]) -> BeliefState:
    beliefs = BeliefState()
    for player_id, suspicion in suspicions.items():
        beliefs.seed_player(player_id, suspicion=suspicion, trust=0.5)
    return beliefs


def _eligible_view() -> EmergencyButtonView:
    return EmergencyButtonView(
        over_gate=True,
        crossed_since_meeting=True,
        call_available=True,
        cooldown_remaining=0,
    )


class TestEmergencyPacingTracker:
    """Bookkeeping pins for the Task 10.8 trigger inputs.

    The tracker is the one stateful piece; every transition below is a
    deterministic function of the agent's own episodic store, its belief
    state, and the orchestrator's meeting-end notifications, so the
    sequences pinned here replay identically.
    """

    def test_crossing_the_gate_arms_the_trigger(self) -> None:
        # The §4.6 gate constant is read from its one home and the
        # comparison is inclusive at the cutoff (exactly the threshold
        # counts, mirroring the vote tally's semantics).
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )

        below = tracker.observe_tick(
            tick=0,
            memory=memory,
            beliefs=_beliefs_with({"p-3": _GATE - 0.05}),
            own_id="p-1",
        )
        assert not below.over_gate
        assert not below.crossed_since_meeting
        assert not below.is_eligible

        at_gate = tracker.observe_tick(
            tick=1,
            memory=memory,
            beliefs=_beliefs_with({"p-3": _GATE}),
            own_id="p-1",
        )
        assert at_gate.over_gate
        assert at_gate.crossed_since_meeting
        assert at_gate.call_available
        assert at_gate.cooldown_remaining == 0
        assert at_gate.is_eligible

    def test_below_threshold_never_arms(self) -> None:
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        beliefs = _beliefs_with({"p-3": _GATE - 0.01, "p-4": 0.5})

        for tick in range(4):
            view = tracker.observe_tick(
                tick=tick, memory=memory, beliefs=beliefs, own_id="p-1"
            )
            assert not view.over_gate
            assert not view.is_eligible

    def test_seen_body_victim_is_excluded_from_the_max(self) -> None:
        # A dead player's stale suspicion row is not actionable at a
        # meeting: a victim the agent saw first-hand (saw_body victim_id)
        # never lifts the max.
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None),
            _saw_body_event(tick=0, body_id="p-9-body", room="MEDBAY", victim_id="p-9"),
        )

        view = tracker.observe_tick(
            tick=0,
            memory=memory,
            beliefs=_beliefs_with({"p-9": 0.95}),
            own_id="p-1",
        )

        assert not view.over_gate

    def test_meeting_announced_dead_are_excluded_from_the_max(self) -> None:
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        beliefs = _beliefs_with({"p-9": 0.95})

        tracker.observe_meeting_end(
            end_tick=5,
            announced_dead=("p-9",),
            was_own_emergency_call=False,
            memory=memory,
            beliefs=beliefs,
            own_id="p-1",
        )
        view = tracker.observe_tick(
            tick=5 + EMERGENCY_COOLDOWN_TICKS,
            memory=memory,
            beliefs=beliefs,
            own_id="p-1",
        )

        assert not view.over_gate
        assert not view.is_eligible

    def test_own_belief_row_is_excluded_defensively(self) -> None:
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )

        view = tracker.observe_tick(
            tick=0,
            memory=memory,
            beliefs=_beliefs_with({"p-1": 0.95}),
            own_id="p-1",
        )

        assert not view.over_gate

    def test_global_cooldown_counts_from_meeting_end(self) -> None:
        # EMERGENCY_COOLDOWN_TICKS is anchored to the W0 mean kill interval
        # (~6 ticks); the gate reopens exactly when that many ticks have
        # elapsed since gameplay resumed.
        assert EMERGENCY_COOLDOWN_TICKS == 6
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        below = _beliefs_with({"p-3": 0.5})
        over = _beliefs_with({"p-3": _GATE + 0.1})

        tracker.observe_meeting_end(
            end_tick=10,
            announced_dead=(),
            was_own_emergency_call=False,
            memory=memory,
            beliefs=below,
            own_id="p-1",
        )
        for tick in range(10, 10 + EMERGENCY_COOLDOWN_TICKS):
            view = tracker.observe_tick(
                tick=tick, memory=memory, beliefs=over, own_id="p-1"
            )
            assert view.cooldown_remaining == 10 + EMERGENCY_COOLDOWN_TICKS - tick
            assert not view.is_eligible
        reopened = tracker.observe_tick(
            tick=10 + EMERGENCY_COOLDOWN_TICKS,
            memory=memory,
            beliefs=over,
            own_id="p-1",
        )
        assert reopened.cooldown_remaining == 0
        assert reopened.is_eligible

    def test_no_cooldown_before_the_first_meeting(self) -> None:
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )

        view = tracker.observe_tick(
            tick=0,
            memory=memory,
            beliefs=_beliefs_with({"p-3": _GATE + 0.1}),
            own_id="p-1",
        )

        assert view.cooldown_remaining == 0
        assert view.is_eligible

    def test_one_emergency_call_per_player_per_game(self) -> None:
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        below = _beliefs_with({"p-3": 0.5})
        over = _beliefs_with({"p-3": _GATE + 0.1})

        tracker.observe_meeting_end(
            end_tick=4,
            announced_dead=(),
            was_own_emergency_call=True,
            memory=memory,
            beliefs=below,
            own_id="p-1",
        )
        # Even a fresh crossing long after the cooldown cannot re-fire: the
        # one call per game is spent.
        view = tracker.observe_tick(
            tick=4 + EMERGENCY_COOLDOWN_TICKS + 5,
            memory=memory,
            beliefs=over,
            own_id="p-1",
        )

        assert view.over_gate
        assert view.crossed_since_meeting
        assert not view.call_available
        assert not view.is_eligible

    def test_anothers_call_does_not_spend_this_agents_call(self) -> None:
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        below = _beliefs_with({"p-3": 0.5})

        tracker.observe_meeting_end(
            end_tick=4,
            announced_dead=(),
            was_own_emergency_call=False,
            memory=memory,
            beliefs=below,
            own_id="p-1",
        )

        view = tracker.observe_tick(
            tick=4 + EMERGENCY_COOLDOWN_TICKS,
            memory=memory,
            beliefs=_beliefs_with({"p-3": _GATE + 0.1}),
            own_id="p-1",
        )
        assert view.call_available
        assert view.is_eligible

    def test_meeting_resets_the_cross_until_a_fresh_crossing(self) -> None:
        # A belief that crossed BEFORE a meeting had its discussion
        # opportunity: after the meeting the trigger stays disarmed while
        # the value merely stays over the gate, and re-arms only on a
        # fresh below-to-above crossing.
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        over = _beliefs_with({"p-3": _GATE + 0.1})
        below = _beliefs_with({"p-3": _GATE - 0.05})

        armed = tracker.observe_tick(tick=0, memory=memory, beliefs=over, own_id="p-1")
        assert armed.is_eligible

        tracker.observe_meeting_end(
            end_tick=3,
            announced_dead=(),
            was_own_emergency_call=False,
            memory=memory,
            beliefs=over,
            own_id="p-1",
        )
        past_cooldown = 3 + EMERGENCY_COOLDOWN_TICKS
        still_over = tracker.observe_tick(
            tick=past_cooldown, memory=memory, beliefs=over, own_id="p-1"
        )
        assert still_over.over_gate
        assert not still_over.crossed_since_meeting
        assert not still_over.is_eligible

        dipped = tracker.observe_tick(
            tick=past_cooldown + 1, memory=memory, beliefs=below, own_id="p-1"
        )
        assert not dipped.over_gate

        recrossed = tracker.observe_tick(
            tick=past_cooldown + 2, memory=memory, beliefs=over, own_id="p-1"
        )
        assert recrossed.crossed_since_meeting
        assert recrossed.is_eligible

    def test_observe_tick_is_idempotent_within_a_tick(self) -> None:
        # The agent runtime samples once per decide(); repeated decide()
        # calls against the same state must see the same view (the
        # policy-determinism contract).
        tracker = EmergencyPacingTracker()
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        beliefs = _beliefs_with({"p-3": _GATE + 0.1})

        first = tracker.observe_tick(
            tick=0, memory=memory, beliefs=beliefs, own_id="p-1"
        )
        second = tracker.observe_tick(
            tick=0, memory=memory, beliefs=beliefs, own_id="p-1"
        )

        assert first == second

    def test_identical_input_sequences_replay_identically(self) -> None:
        # Cooldown bookkeeping replays identically: two trackers fed the
        # same deterministic input sequence emit the same view sequence.
        memory = _store_with(
            _self_state_event(tick=0, room="CAFETERIA", pending_task_id=None)
        )
        sequence = [
            _beliefs_with({"p-3": 0.5}),
            _beliefs_with({"p-3": _GATE + 0.1}),
            _beliefs_with({"p-3": _GATE + 0.1}),
            _beliefs_with({"p-3": _GATE - 0.05}),
            _beliefs_with({"p-3": _GATE}),
        ]

        def run() -> list[EmergencyButtonView]:
            tracker = EmergencyPacingTracker()
            views: list[EmergencyButtonView] = []
            for tick, beliefs in enumerate(sequence):
                if tick == 3:
                    tracker.observe_meeting_end(
                        end_tick=tick,
                        announced_dead=(),
                        was_own_emergency_call=False,
                        memory=memory,
                        beliefs=beliefs,
                        own_id="p-1",
                    )
                views.append(
                    tracker.observe_tick(
                        tick=tick, memory=memory, beliefs=beliefs, own_id="p-1"
                    )
                )
            return views

        assert run() == run()


class TestCrewmateSuspicionEmergencyTrigger:
    """Policy-side pins: the second producer of the button walk."""

    def test_eligible_at_button_room_presses_the_button(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map(), emergency=_eligible_view())

        assert isinstance(intent, EmergencyMeetingIntent)
        assert intent.payload.reason == SUSPICION_ACCUMULATION_REASON
        assert intent.actor == "p-1"

    def test_eligible_away_from_button_walks_toward_it(self) -> None:
        # The walk stays — it is the counterplay cost. The trigger preempts
        # the pending task exactly like the witnessed-kill interrupt.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map(), emergency=_eligible_view())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    @pytest.mark.parametrize(
        "view",
        [
            EmergencyButtonView(
                over_gate=False,
                crossed_since_meeting=False,
                call_available=True,
                cooldown_remaining=0,
            ),
            EmergencyButtonView(
                over_gate=True,
                crossed_since_meeting=True,
                call_available=True,
                cooldown_remaining=3,
            ),
            EmergencyButtonView(
                over_gate=True,
                crossed_since_meeting=True,
                call_available=False,
                cooldown_remaining=0,
            ),
            EmergencyButtonView(
                over_gate=True,
                crossed_since_meeting=False,
                call_available=True,
                cooldown_remaining=0,
            ),
        ],
        ids=["below-gate", "during-cooldown", "call-spent", "no-fresh-cross"],
    )
    def test_ineligible_views_run_the_normal_fsm(
        self, view: EmergencyButtonView
    ) -> None:
        # Each eligibility gate independently suppresses the trigger: below
        # the threshold, during the global cooldown, after the one call is
        # spent, and without a fresh post-meeting crossing.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map(), emergency=view)

        assert isinstance(intent, DoTaskIntent)

    def test_body_report_outranks_the_suspicion_trigger(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY", pending_task_id=None),
            _saw_body_event(tick=10, body_id="p-3-body", room="MEDBAY"),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map(), emergency=_eligible_view())

        assert isinstance(intent, ReportBodyIntent)

    def test_witnessed_kill_outranks_the_suspicion_trigger(self) -> None:
        # Both producers take the same walk; the witnessed-kill interrupt
        # keeps priority so the emitted reason stays the harder evidence.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
            _saw_player_event(
                tick=10, player_id="p-2", room="CAFETERIA", action=KILL_ACTION
            ),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map(), emergency=_eligible_view())

        assert isinstance(intent, EmergencyMeetingIntent)
        assert intent.payload.reason == KILL_WITNESS_REASON

    def test_decide_without_emergency_kwarg_is_unchanged(self) -> None:
        # Callers without belief wiring (the pre-10.8 call shape) keep the
        # plain FSM: no emergency snapshot, no trigger.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)

    def test_trigger_decision_is_pure(self) -> None:
        # Same inputs -> same intent, repeatedly: the eligibility snapshot
        # is data, so decide() stays a pure function of its arguments.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id=None),
        )
        policy = CrewmatePolicy(agent_id="p-1")
        view = _eligible_view()
        public_map = _public_map()

        intents = [policy.decide(store, public_map, emergency=view) for _ in range(5)]

        for intent in intents:
            assert isinstance(intent, EmergencyMeetingIntent)
            assert intent.payload.reason == SUSPICION_ACCUMULATION_REASON

    def test_tracker_to_policy_cross_fires_with_no_meeting_since(self) -> None:
        # The DoD unit pin end-to-end at the agents layer: private max
        # suspicion crosses the §4.6 gate (a Rule-1-sized lift), no meeting
        # has been held since the cross, so the next decide walks; at the
        # button it presses.
        tracker = EmergencyPacingTracker()
        policy = CrewmatePolicy(agent_id="p-1")
        public_map = _public_map()
        store = _store_with(
            _self_state_event(tick=0, room="ADMIN", pending_task_id=None),
        )

        quiet = tracker.observe_tick(
            tick=0,
            memory=store,
            beliefs=_beliefs_with({"p-3": 0.5}),
            own_id="p-1",
        )
        assert isinstance(policy.decide(store, public_map, emergency=quiet), MoveIntent)

        crossed_beliefs = _beliefs_with({"p-3": _GATE + 0.1})
        store.append(_self_state_event(tick=1, room="ADMIN", pending_task_id=None))
        crossed = tracker.observe_tick(
            tick=1, memory=store, beliefs=crossed_beliefs, own_id="p-1"
        )
        walking = policy.decide(store, public_map, emergency=crossed)
        assert isinstance(walking, MoveIntent)
        assert walking.payload.to_room == "CAFETERIA"

        store.append(_self_state_event(tick=2, room="CAFETERIA", pending_task_id=None))
        at_button = tracker.observe_tick(
            tick=2, memory=store, beliefs=crossed_beliefs, own_id="p-1"
        )
        pressed = policy.decide(store, public_map, emergency=at_button)
        assert isinstance(pressed, EmergencyMeetingIntent)
        assert pressed.payload.reason == SUSPICION_ACCUMULATION_REASON


class TestImpostorPolicyHasNoEmergencyBehavior:
    """Impostor policy untouched (Task 10.8): no button behavior until Wave 2.

    Asserted against impostor policy OUTPUT per the task contract: an
    impostor in the same over-gate world never emits an
    :class:`EmergencyMeetingIntent`, and its decide() exposes no emergency
    channel at all (beliefs are not even an input).
    """

    @staticmethod
    def _impostor_store(*, cooldown: int) -> MemoryStore:
        store = MemoryStore()
        store.append(
            _self_state_event(
                tick=10, room="CAFETERIA", pending_task_id=None, role="IMPOSTOR"
            )
        )
        store.append(
            EpisodicEvent(
                tick=10,
                type=EVENT_COOLDOWN_STATUS,
                payload={"cooldown": cooldown},
                provenance=PROVENANCE_OBSERVED,
            )
        )
        return store

    def test_impostor_never_emits_emergency_intent_while_idle(self) -> None:
        policy = ImpostorPolicy(agent_id="p-1")

        intent = policy.decide(self._impostor_store(cooldown=3), _public_map())

        assert not isinstance(intent, EmergencyMeetingIntent)

    def test_impostor_never_emits_emergency_intent_with_kill_ready(self) -> None:
        store = self._impostor_store(cooldown=0)
        store.append(
            _saw_player_event(tick=10, player_id="p-2", room="CAFETERIA", action=None)
        )
        policy = ImpostorPolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, EmergencyMeetingIntent)

    def test_impostor_decide_exposes_no_emergency_channel(self) -> None:
        # Structural pin behind the output assertions: the impostor FSM
        # takes no eligibility snapshot and no belief state — there is no
        # input through which button behavior could fire.
        parameters = inspect.signature(ImpostorPolicy.decide).parameters

        assert "emergency" not in parameters
        assert "beliefs" not in parameters
