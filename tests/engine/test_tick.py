from __future__ import annotations

from dataclasses import replace

from engine.actions import (
    DoTaskAction,
    EmergencyMeetingAction,
    KillAction,
    MoveAction,
    ReportBodyAction,
    SabotageAction,
    VentAction,
)
from engine.entities import BodyState, PlayerState, TaskState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState


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
            "player-1": _player("player-1", "CREWMATE", "CAFETERIA", (0.0, 0.0)),
            "player-2": _player("player-2", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "player-3": _player("player-3", "CREWMATE", "MEDBAY", (0.0, 0.0)),
            "impostor-1": _player("impostor-1", "IMPOSTOR", "CAFETERIA", (1.0, 0.0)),
        },
        bodies={},
        tasks={"swipe_card": _task("swipe_card", "player-2", "ADMIN")},
        sabotage=None,
        cooldowns={"impostor-1": 0},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def test_valid_kill_mutates_state_and_emits_event() -> None:
    state = _state()

    next_state, events = advance_tick(
        state,
        [KillAction(type="kill", actor="impostor-1", payload={"target": "player-1"})],
    )

    assert not next_state.players["player-1"].alive
    assert "body-player-1-0" in next_state.bodies
    assert any(event["type"] == "Killed" for event in events)
    assert next_state.phase == "PLAY"


def test_invalid_kill_emits_rejection_and_leaves_state_unchanged() -> None:
    state = replace(_state(), cooldowns={"impostor-1": 1})

    next_state, events = advance_tick(
        state,
        [KillAction(type="kill", actor="impostor-1", payload={"target": "player-1"})],
    )

    assert next_state.players["player-1"].alive
    assert next_state.bodies == {}
    assert next_state.cooldowns["impostor-1"] == 0
    assert any(event["type"] == "ActionRejected" for event in events)


def test_move_and_task_actions_apply_expected_mutations() -> None:
    moved_state, move_events = advance_tick(
        _state(),
        [MoveAction(type="move", actor="player-1", payload={"to_room": "UPPER_HALL"})],
    )
    task_state = replace(
        moved_state,
        players={
            **dict(moved_state.players),
            "player-2": replace(moved_state.players["player-2"], room="ADMIN"),
        },
        tasks={"swipe_card": _task("swipe_card", "player-2", "ADMIN")},
    )

    next_state, task_events = advance_tick(
        task_state,
        [DoTaskAction(type="do_task", actor="player-2", payload={"task_id": "swipe_card"})],
    )

    assert moved_state.players["player-1"].room == "UPPER_HALL"
    assert any(event["type"] == "Moved" for event in move_events)
    assert next_state.tasks["swipe_card"].completed
    assert next_state.tasks["swipe_card"].progress == 1
    assert any(event["type"] == "TaskCompleted" for event in task_events)


def test_vent_sabotage_and_passive_effects_apply() -> None:
    state = replace(
        _state(),
        players={
            **dict(_state().players),
            "impostor-1": replace(_state().players["impostor-1"], room="ADMIN"),
        },
        cooldowns={"impostor-1": 2},
    )

    next_state, events = advance_tick(
        state,
        [
            VentAction(type="vent", actor="impostor-1", payload={"vent_id": "ADMIN_VENT"}),
            SabotageAction(type="sabotage", actor="impostor-1", payload={"kind": "lights"}),
        ],
    )

    assert next_state.players["impostor-1"].in_vent
    assert next_state.sabotage is not None
    assert next_state.sabotage.kind == "lights"
    assert next_state.sabotage.remaining_ticks == 89
    assert next_state.cooldowns["impostor-1"] == 1
    assert [event["type"] for event in events[:2]] == ["VentEntered", "SabotageStarted"]


def test_report_and_emergency_transition_to_meeting() -> None:
    body = BodyState(
        id="body-player-2-0",
        player_id="player-2",
        room="CAFETERIA",
        position=(0.0, 0.0),
        killed_by="impostor-1",
        discovered_by=None,
    )
    report_state = replace(_state(), bodies={body.id: body})

    next_state, report_events = advance_tick(
        report_state,
        [
            ReportBodyAction(
                type="report",
                actor="player-1",
                payload={"body_id": "body-player-2-0"},
            )
        ],
    )

    assert next_state.phase == "MEETING"
    assert next_state.bodies["body-player-2-0"].discovered_by == "player-1"
    assert any(event["type"] == "MeetingTriggered" for event in report_events)

    emergency_state, emergency_events = advance_tick(
        _state(),
        [EmergencyMeetingAction(type="emergency", actor="player-1", payload={})],
    )

    assert emergency_state.phase == "MEETING"
    assert any(event["type"] == "MeetingTriggered" for event in emergency_events)
