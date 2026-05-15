from __future__ import annotations

from dataclasses import replace

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyState, PlayerState, SabotageState, TaskState
from engine.events import event_to_dict
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _action(data: object) -> Action:
    return _ACTION_ADAPTER.validate_python(data)


def _player(
    player_id: str,
    role: str,
    room: str,
    position: tuple[float, float],
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="IMPOSTOR" if role == "IMPOSTOR" else "CREWMATE",
        alive=True,
        room=room,
        position=position,
        last_action=None,
        in_vent=False,
    )


def _task(task_id: str, owner: str, room: str, required_ticks: int = 1) -> TaskState:
    return TaskState(
        id=task_id,
        owner=owner,
        room=room,
        progress=0,
        required_ticks=required_ticks,
        completed=False,
    )


def _state() -> WorldState:
    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players={
            "p-1": _player("p-1", "CREWMATE", "CAFETERIA", (0.0, 0.0)),
            "p-2": _player("p-2", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "p-4": _player("p-4", "CREWMATE", "MEDBAY", (0.0, 0.0)),
            "p-3": _player("p-3", "IMPOSTOR", "CAFETERIA", (1.0, 0.0)),
        },
        bodies={},
        tasks={"swipe_card": _task("swipe_card", "p-2", "ADMIN")},
        sabotage=None,
        cooldowns={"p-3": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def _long_task_state() -> WorldState:
    return replace(
        _state(),
        tasks={"swipe_card": _task("swipe_card", "p-2", "ADMIN", 3)},
    )


def test_valid_kill_mutates_state_and_emits_event() -> None:
    game_map = load_canonical_map()
    state = _state()
    players = dict(state.players)
    players["crew-b"] = _player("crew-b", "CREWMATE", "CAFETERIA", (2.0, 0.0))
    players["crew-a"] = _player("crew-a", "CREWMATE", "CAFETERIA", (3.0, 0.0))
    players["dead-crew"] = replace(
        _player("dead-crew", "CREWMATE", "CAFETERIA", (4.0, 0.0)),
        alive=False,
    )
    players["vented-crew"] = replace(
        _player("vented-crew", "CREWMATE", "CAFETERIA", (5.0, 0.0)),
        in_vent=True,
    )
    state = replace(state, players=players)

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "kill",
                    "actor": "p-3",
                    "payload": {"target": "p-1"},
                }
            )
        ],
        game_map=game_map,
    )

    assert not next_state.players["p-1"].alive
    assert "body-p-1-0" in next_state.bodies
    assert next_state.cooldowns["p-3"] == 10
    killed_event = next(event for event in events if event.type == "Killed")
    assert event_to_dict(killed_event)["details"]["witnesses"] == ("crew-a", "crew-b")
    assert next_state.phase == "PLAY"

    later_state, _ = advance_tick(next_state, [], game_map=game_map)

    assert later_state.cooldowns["p-3"] == 9


def test_invalid_kill_emits_rejection_and_leaves_state_unchanged() -> None:
    game_map = load_canonical_map()
    state = replace(_state(), cooldowns={"p-3": 1})

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "kill",
                    "actor": "p-3",
                    "payload": {"target": "p-1"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["p-1"].alive
    assert next_state.bodies == {}
    assert next_state.cooldowns["p-3"] == 0
    assert any(event.type == "ActionRejected" for event in events)


def test_continuing_task_progresses_without_repeated_action() -> None:
    game_map = load_canonical_map()
    started_state, start_events = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    continued_state, continue_events = advance_tick(
        started_state,
        [],
        game_map=game_map,
    )

    assert started_state.tasks["swipe_card"].progress == 1
    assert not started_state.tasks["swipe_card"].completed
    assert [event.type for event in start_events].count("TaskProgressed") == 1
    assert continued_state.tasks["swipe_card"].progress == 2
    assert not continued_state.tasks["swipe_card"].completed
    assert continue_events[0].type == "TaskProgressed"
    assert event_to_dict(continue_events[0])["details"] == {
        "task_id": "swipe_card",
        "progress": 2,
        "required_ticks": 3,
    }


def test_continuing_task_completes_and_can_trigger_crew_win() -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )
    state, _ = advance_tick(state, [], game_map=game_map)

    completed_state, events = advance_tick(state, [], game_map=game_map)

    assert completed_state.tasks["swipe_card"].progress == 3
    assert completed_state.tasks["swipe_card"].completed
    assert completed_state.phase == "GAME_OVER"
    assert [event.type for event in events] == ["TaskCompleted", "GameOver"]
    assert event_to_dict(events[1])["winner"] == "CREWMATES"
    assert event_to_dict(events[1])["reason"] == "CREWMATE_TASKS"


def test_submitted_wait_suppresses_continuing_task_progress() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    waited_state, events = advance_tick(
        started_state,
        [_action({"type": "wait", "actor": "p-2", "payload": {}})],
        game_map=game_map,
    )

    assert waited_state.tasks["swipe_card"].progress == 1
    assert [event.type for event in events].count("TaskProgressed") == 0
    assert events[0].type == "Waited"


def test_submitted_move_suppresses_continuing_task_progress() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    moved_state, events = advance_tick(
        started_state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "UPPER_HALL"},
                }
            )
        ],
        game_map=game_map,
    )

    assert moved_state.tasks["swipe_card"].progress == 1
    assert moved_state.players["p-2"].room == "UPPER_HALL"
    assert [event.type for event in events].count("TaskProgressed") == 0
    assert events[0].type == "Moved"


def test_rejected_action_suppresses_continuing_task_progress_for_that_tick() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    rejected_state, rejected_events = advance_tick(
        started_state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "REACTOR"},
                }
            )
        ],
        game_map=game_map,
    )
    continued_state, continued_events = advance_tick(
        rejected_state,
        [],
        game_map=game_map,
    )

    assert rejected_state.tasks["swipe_card"].progress == 1
    assert rejected_events[0].type == "ActionRejected"
    assert [event.type for event in rejected_events].count("TaskProgressed") == 0
    assert continued_state.tasks["swipe_card"].progress == 2
    assert continued_events[0].type == "TaskProgressed"


def test_repeated_do_task_action_increments_once_per_tick() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    next_state, events = advance_tick(
        started_state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.tasks["swipe_card"].progress == 2
    assert [event.type for event in events].count("TaskProgressed") == 1


def test_move_and_task_actions_apply_expected_mutations() -> None:
    game_map = load_canonical_map()
    moved_state, move_events = advance_tick(
        _state(),
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-1",
                    "payload": {"to_room": "UPPER_HALL"},
                }
            )
        ],
        game_map=game_map,
    )
    task_state = replace(
        moved_state,
        players={
            **dict(moved_state.players),
            "p-2": replace(moved_state.players["p-2"], room="ADMIN"),
        },
        tasks={"swipe_card": _task("swipe_card", "p-2", "ADMIN")},
    )

    next_state, task_events = advance_tick(
        task_state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert moved_state.players["p-1"].room == "UPPER_HALL"
    assert any(event.type == "Moved" for event in move_events)
    assert next_state.tasks["swipe_card"].completed
    assert next_state.tasks["swipe_card"].progress == 1
    assert any(event.type == "TaskCompleted" for event in task_events)


def test_vent_sabotage_and_passive_effects_apply() -> None:
    game_map = load_canonical_map()
    base_state = _state()
    state = replace(
        base_state,
        players={
            **dict(base_state.players),
            "p-3": replace(base_state.players["p-3"], room="ADMIN"),
            "p-4": replace(base_state.players["p-4"], room="ADMIN", in_vent=True),
            "dead-admin": replace(
                _player("dead-admin", "CREWMATE", "ADMIN", (2.0, 0.0)),
                alive=False,
            ),
        },
        cooldowns={"p-3": 2},
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            ),
            _action(
                {
                    "type": "sabotage",
                    "actor": "p-3",
                    "payload": {"kind": "lights"},
                }
            ),
        ],
        game_map=game_map,
    )

    assert next_state.players["p-3"].in_vent
    assert next_state.sabotage is not None
    assert next_state.sabotage.kind == "lights"
    assert next_state.sabotage.remaining_ticks == 89
    assert next_state.cooldowns["p-3"] == 1
    assert [event.type for event in events[:2]] == ["VentEntered", "SabotageStarted"]
    assert event_to_dict(events[0])["details"]["witnesses"] == ("p-2",)
    assert event_to_dict(events[0])["details"]["source_witnesses"] == ("p-2",)
    assert event_to_dict(events[0])["details"]["destination_witnesses"] == ("p-2",)


def _active_lights_state(*, remaining_ticks: int = 5) -> WorldState:
    return replace(
        _state(),
        sabotage=SabotageState(
            kind="lights",
            remaining_ticks=remaining_ticks,
            affected_rooms=("ADMIN",),
            active=True,
        ),
    )


def test_timed_sabotage_repair_completes_after_configured_ticks() -> None:
    game_map = load_canonical_map()
    state = _active_lights_state()

    first_state, first_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )
    second_state, second_events = advance_tick(
        first_state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )
    repaired_state, repaired_events = advance_tick(
        second_state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )

    assert first_events[0].type == "SabotageRepairProgressed"
    assert event_to_dict(first_events[0])["details"]["progress"] == 1
    assert first_state.sabotage is not None
    assert first_state.sabotage.repair_progress["ADMIN"] == 1
    assert event_to_dict(second_events[0])["details"]["progress"] == 2
    assert repaired_events[0].type == "SabotageRepaired"
    assert event_to_dict(repaired_events[0])["details"]["required_ticks"] == 3
    assert repaired_state.sabotage is not None
    assert not repaired_state.sabotage.active
    assert not any(event.type == "GameOver" for event in repaired_events)


def test_repair_prevents_same_tick_sabotage_timeout_when_completed() -> None:
    game_map = load_canonical_map()
    sabotage = SabotageState(
        kind="lights",
        remaining_ticks=1,
        affected_rooms=("ADMIN",),
        active=True,
        repair_progress={"ADMIN": 2},
    )
    state = replace(_state(), sabotage=sabotage)

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )

    assert events[0].type == "SabotageRepaired"
    assert next_state.sabotage is not None
    assert not next_state.sabotage.active
    assert not any(event.type == "GameOver" for event in events)


def test_unrepaired_sabotage_timeout_still_wins() -> None:
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        _active_lights_state(remaining_ticks=1),
        [],
        game_map=game_map,
    )

    assert next_state.phase == "GAME_OVER"
    assert events[0].type == "GameOver"
    assert event_to_dict(events[0])["winner"] == "IMPOSTORS"
    assert event_to_dict(events[0])["reason"] == "IMPOSTOR_SABOTAGE"


@pytest.mark.parametrize(
    ("state", "action_actor", "kind", "match"),
    (
        (_state(), "p-2", "lights", "no active sabotage"),
        (_active_lights_state(), "p-1", "lights", "repair room"),
        (_active_lights_state(), "p-2", "unknown", "unknown sabotage"),
        (
            replace(
                _active_lights_state(),
                players={
                    **dict(_active_lights_state().players),
                    "p-2": replace(_active_lights_state().players["p-2"], in_vent=True),
                },
            ),
            "p-2",
            "lights",
            "while in vent",
        ),
    ),
)
def test_invalid_sabotage_repairs_are_rejected(
    state: WorldState,
    action_actor: str,
    kind: str,
    match: str,
) -> None:
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": action_actor,
                    "payload": {"kind": kind},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.sabotage == state.sabotage or state.sabotage is not None
    assert events[0].type == "ActionRejected"
    assert match in event_to_dict(events[0])["reason"]


def test_vent_can_exit_through_connected_destination_vent() -> None:
    game_map = load_canonical_map()
    base_state = _state()
    state = replace(
        base_state,
        players={
            **dict(base_state.players),
            "p-3": replace(base_state.players["p-3"], room="ADMIN"),
            "p-4": replace(base_state.players["p-4"], room="REACTOR"),
        },
    )

    in_vent_state, enter_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )
    exited_state, exit_events = advance_tick(
        in_vent_state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "REACTOR_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    assert in_vent_state.players["p-3"].room == "ADMIN"
    assert in_vent_state.players["p-3"].in_vent
    assert enter_events[0].type == "VentEntered"
    assert exited_state.players["p-3"].room == "REACTOR"
    assert not exited_state.players["p-3"].in_vent
    assert exit_events[0].type == "VentExited"
    assert event_to_dict(exit_events[0])["details"]["source_vent_id"] == "ADMIN_VENT"
    assert (
        event_to_dict(exit_events[0])["details"]["destination_vent_id"]
        == "REACTOR_VENT"
    )
    assert event_to_dict(exit_events[0])["details"]["witnesses"] == (
        "p-2",
        "p-4",
    )
    assert event_to_dict(exit_events[0])["details"]["source_witnesses"] == ("p-2",)
    assert event_to_dict(exit_events[0])["details"]["destination_witnesses"] == ("p-4",)


def test_vent_rejects_unconnected_destination_vent() -> None:
    game_map = load_canonical_map()
    state = replace(
        _state(),
        players={
            **dict(_state().players),
            "p-3": replace(_state().players["p-3"], room="ADMIN"),
        },
    )
    in_vent_state, _ = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    next_state, events = advance_tick(
        in_vent_state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "STORAGE_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["p-3"].room == "ADMIN"
    assert next_state.players["p-3"].in_vent
    assert events[0].type == "ActionRejected"


def test_report_and_emergency_transition_to_meeting() -> None:
    game_map = load_canonical_map()
    body = BodyState(
        id="body-p-2-0",
        player_id="p-2",
        room="CAFETERIA",
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    report_state = replace(_state(), bodies={body.id: body})

    next_state, report_events = advance_tick(
        report_state,
        [
            _action(
                {
                    "type": "report",
                    "actor": "p-1",
                    "payload": {"body_id": "body-p-2-0"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.bodies["body-p-2-0"].discovered_by == "p-1"
    assert any(event.type == "MeetingTriggered" for event in report_events)

    emergency_state, emergency_events = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert emergency_state.phase == "MEETING"
    assert emergency_state.emergency_uses["p-1"] == 1
    assert any(event.type == "MeetingTriggered" for event in emergency_events)


def test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks() -> (
    None
):
    game_map = load_canonical_map()
    body = BodyState(
        id="body-p-2-0",
        player_id="p-2",
        room="CAFETERIA",
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    state = replace(
        _state(),
        bodies={body.id: body},
        sabotage=SabotageState(
            kind="lights",
            remaining_ticks=1,
            affected_rooms=("ADMIN",),
            active=True,
        ),
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "report",
                    "actor": "p-1",
                    "payload": {"body_id": "body-p-2-0"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.tick == state.tick
    assert next_state.rng_state == state.rng_state
    assert next_state.sabotage is not None
    assert next_state.sabotage.remaining_ticks == 1
    assert [event.type for event in events] == ["MeetingTriggered"]


def test_emergency_trigger_interrupts_tick_before_passive_effects_and_win_checks() -> (
    None
):
    game_map = load_canonical_map()
    state = replace(
        _state(),
        sabotage=SabotageState(
            kind="lights",
            remaining_ticks=1,
            affected_rooms=("ADMIN",),
            active=True,
        ),
    )

    next_state, events = advance_tick(
        state,
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.tick == state.tick
    assert next_state.rng_state == state.rng_state
    assert next_state.sabotage is not None
    assert next_state.sabotage.remaining_ticks == 1
    assert [event.type for event in events] == ["MeetingTriggered"]


def test_emergency_requires_actor_in_button_room() -> None:
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "p-2", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "PLAY"
    assert "p-2" not in next_state.emergency_uses
    assert events[0].type == "ActionRejected"
    assert "emergency button room" in event_to_dict(events[0])["reason"]


def test_emergency_rejects_actor_in_vent() -> None:
    game_map = load_canonical_map()
    state = _state()
    players = dict(state.players)
    players["p-1"] = replace(players["p-1"], in_vent=True)

    next_state, events = advance_tick(
        replace(state, players=players),
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "PLAY"
    assert "p-1" not in next_state.emergency_uses
    assert next_state.players["p-1"].in_vent
    assert events[0].type == "ActionRejected"
    assert "while in vent" in event_to_dict(events[0])["reason"]


def test_advance_tick_rejects_non_play_phases() -> None:
    game_map = load_canonical_map()
    with pytest.raises(ValueError, match="MEETING"):
        advance_tick(replace(_state(), phase="MEETING"), [], game_map=game_map)
    with pytest.raises(ValueError, match="GAME_OVER"):
        advance_tick(replace(_state(), phase="GAME_OVER"), [], game_map=game_map)


def test_advance_tick_rejects_mismatched_state_map() -> None:
    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="unsupported map id"):
        advance_tick(replace(_state(), map="other_map"), [], game_map=game_map)


def test_advance_tick_uses_supplied_map_without_loading_canonical_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    game_map = load_canonical_map()

    def fail_if_loaded() -> None:
        pytest.fail("advance_tick must not load the canonical map")

    monkeypatch.setattr("engine.world.load_canonical_map", fail_if_loaded)

    next_state, events = advance_tick(
        _state(),
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-1",
                    "payload": {"to_room": "UPPER_HALL"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["p-1"].room == "UPPER_HALL"
    assert any(event.type == "Moved" for event in events)


def test_repeated_emergency_use_is_rejected() -> None:
    game_map = load_canonical_map()
    meeting_state, _ = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )
    resumed_state = replace(meeting_state, phase="PLAY")

    next_state, events = advance_tick(
        resumed_state,
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "PLAY"
    assert next_state.emergency_uses["p-1"] == 1
    assert events[0].type == "ActionRejected"
