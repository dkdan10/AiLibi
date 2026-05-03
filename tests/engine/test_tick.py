from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest
from pydantic import TypeAdapter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.actions import Action  # noqa: E402
from engine.entities import BodyState, PlayerState, SabotageState, TaskState  # noqa: E402
from engine.rng import EngineRng  # noqa: E402
from engine.tick import advance_tick  # noqa: E402
from engine.world import WorldState, load_canonical_map  # noqa: E402

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
            "player-1": _player("player-1", "CREWMATE", "CAFETERIA", (0.0, 0.0)),
            "player-2": _player("player-2", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "player-3": _player("player-3", "CREWMATE", "MEDBAY", (0.0, 0.0)),
            "impostor-1": _player("impostor-1", "IMPOSTOR", "CAFETERIA", (1.0, 0.0)),
        },
        bodies={},
        tasks={"swipe_card": _task("swipe_card", "player-2", "ADMIN")},
        sabotage=None,
        cooldowns={"impostor-1": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
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
                    "actor": "impostor-1",
                    "payload": {"target": "player-1"},
                }
            )
        ],
        game_map=game_map,
    )

    assert not next_state.players["player-1"].alive
    assert "body-player-1-0" in next_state.bodies
    assert next_state.cooldowns["impostor-1"] == 10
    killed_event = next(event for event in events if event["type"] == "Killed")
    assert killed_event["details"]["witnesses"] == ("crew-a", "crew-b")
    assert next_state.phase == "PLAY"

    later_state, _ = advance_tick(next_state, [], game_map=game_map)

    assert later_state.cooldowns["impostor-1"] == 9


def test_invalid_kill_emits_rejection_and_leaves_state_unchanged() -> None:
    game_map = load_canonical_map()
    state = replace(_state(), cooldowns={"impostor-1": 1})

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "kill",
                    "actor": "impostor-1",
                    "payload": {"target": "player-1"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["player-1"].alive
    assert next_state.bodies == {}
    assert next_state.cooldowns["impostor-1"] == 0
    assert any(event["type"] == "ActionRejected" for event in events)


def test_move_and_task_actions_apply_expected_mutations() -> None:
    game_map = load_canonical_map()
    moved_state, move_events = advance_tick(
        _state(),
        [
            _action(
                {
                    "type": "move",
                    "actor": "player-1",
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
            "player-2": replace(moved_state.players["player-2"], room="ADMIN"),
        },
        tasks={"swipe_card": _task("swipe_card", "player-2", "ADMIN")},
    )

    next_state, task_events = advance_tick(
        task_state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "player-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert moved_state.players["player-1"].room == "UPPER_HALL"
    assert any(event["type"] == "Moved" for event in move_events)
    assert next_state.tasks["swipe_card"].completed
    assert next_state.tasks["swipe_card"].progress == 1
    assert any(event["type"] == "TaskCompleted" for event in task_events)


def test_vent_sabotage_and_passive_effects_apply() -> None:
    game_map = load_canonical_map()
    base_state = _state()
    state = replace(
        base_state,
        players={
            **dict(base_state.players),
            "impostor-1": replace(base_state.players["impostor-1"], room="ADMIN"),
            "player-3": replace(
                base_state.players["player-3"], room="ADMIN", in_vent=True
            ),
            "dead-admin": replace(
                _player("dead-admin", "CREWMATE", "ADMIN", (2.0, 0.0)),
                alive=False,
            ),
        },
        cooldowns={"impostor-1": 2},
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "impostor-1",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            ),
            _action(
                {
                    "type": "sabotage",
                    "actor": "impostor-1",
                    "payload": {"kind": "lights"},
                }
            ),
        ],
        game_map=game_map,
    )

    assert next_state.players["impostor-1"].in_vent
    assert next_state.sabotage is not None
    assert next_state.sabotage.kind == "lights"
    assert next_state.sabotage.remaining_ticks == 89
    assert next_state.cooldowns["impostor-1"] == 1
    assert [event["type"] for event in events[:2]] == ["VentEntered", "SabotageStarted"]
    assert events[0]["details"]["witnesses"] == ("player-2",)
    assert events[0]["details"]["source_witnesses"] == ("player-2",)
    assert events[0]["details"]["destination_witnesses"] == ("player-2",)


def test_vent_can_exit_through_connected_destination_vent() -> None:
    game_map = load_canonical_map()
    base_state = _state()
    state = replace(
        base_state,
        players={
            **dict(base_state.players),
            "impostor-1": replace(base_state.players["impostor-1"], room="ADMIN"),
            "player-3": replace(base_state.players["player-3"], room="REACTOR"),
        },
    )

    in_vent_state, enter_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "impostor-1",
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
                    "actor": "impostor-1",
                    "payload": {"vent_id": "REACTOR_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    assert in_vent_state.players["impostor-1"].room == "ADMIN"
    assert in_vent_state.players["impostor-1"].in_vent
    assert enter_events[0]["type"] == "VentEntered"
    assert exited_state.players["impostor-1"].room == "REACTOR"
    assert not exited_state.players["impostor-1"].in_vent
    assert exit_events[0]["type"] == "VentExited"
    assert exit_events[0]["details"]["source_vent_id"] == "ADMIN_VENT"
    assert exit_events[0]["details"]["destination_vent_id"] == "REACTOR_VENT"
    assert exit_events[0]["details"]["witnesses"] == ("player-2", "player-3")
    assert exit_events[0]["details"]["source_witnesses"] == ("player-2",)
    assert exit_events[0]["details"]["destination_witnesses"] == ("player-3",)


def test_vent_rejects_unconnected_destination_vent() -> None:
    game_map = load_canonical_map()
    state = replace(
        _state(),
        players={
            **dict(_state().players),
            "impostor-1": replace(_state().players["impostor-1"], room="ADMIN"),
        },
    )
    in_vent_state, _ = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "impostor-1",
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
                    "actor": "impostor-1",
                    "payload": {"vent_id": "STORAGE_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["impostor-1"].room == "ADMIN"
    assert next_state.players["impostor-1"].in_vent
    assert events[0]["type"] == "ActionRejected"


def test_report_and_emergency_transition_to_meeting() -> None:
    game_map = load_canonical_map()
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
            _action(
                {
                    "type": "report",
                    "actor": "player-1",
                    "payload": {"body_id": "body-player-2-0"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.bodies["body-player-2-0"].discovered_by == "player-1"
    assert any(event["type"] == "MeetingTriggered" for event in report_events)

    emergency_state, emergency_events = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "player-1", "payload": {}})],
        game_map=game_map,
    )

    assert emergency_state.phase == "MEETING"
    assert emergency_state.emergency_uses["player-1"] == 1
    assert any(event["type"] == "MeetingTriggered" for event in emergency_events)


def test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks() -> (
    None
):
    game_map = load_canonical_map()
    body = BodyState(
        id="body-player-2-0",
        player_id="player-2",
        room="CAFETERIA",
        position=(0.0, 0.0),
        killed_by="impostor-1",
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
                    "actor": "player-1",
                    "payload": {"body_id": "body-player-2-0"},
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
    assert [event["type"] for event in events] == ["MeetingTriggered"]


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
        [_action({"type": "emergency", "actor": "player-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.tick == state.tick
    assert next_state.rng_state == state.rng_state
    assert next_state.sabotage is not None
    assert next_state.sabotage.remaining_ticks == 1
    assert [event["type"] for event in events] == ["MeetingTriggered"]


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
                    "actor": "player-1",
                    "payload": {"to_room": "UPPER_HALL"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["player-1"].room == "UPPER_HALL"
    assert any(event["type"] == "Moved" for event in events)


def test_repeated_emergency_use_is_rejected() -> None:
    game_map = load_canonical_map()
    meeting_state, _ = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "player-1", "payload": {}})],
        game_map=game_map,
    )
    resumed_state = replace(meeting_state, phase="PLAY")

    next_state, events = advance_tick(
        resumed_state,
        [_action({"type": "emergency", "actor": "player-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "PLAY"
    assert next_state.emergency_uses["player-1"] == 1
    assert events[0]["type"] == "ActionRejected"
