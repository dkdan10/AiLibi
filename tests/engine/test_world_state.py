from __future__ import annotations

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyState, PlayerState, TaskState
from engine.world import WorldState

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _action(data: object) -> Action:
    return _ACTION_ADAPTER.validate_python(data)


def _player(player_id: str) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="CREWMATE",
        alive=True,
        room="CAFETERIA",
        position=(0.0, 0.0),
        last_action=None,
        in_vent=False,
    )


def _body(body_id: str, player_id: str) -> BodyState:
    return BodyState(
        id=body_id,
        player_id=player_id,
        room="CAFETERIA",
        position=(1.0, 1.0),
        killed_by="impostor",
        discovered_by=None,
    )


def _task(task_id: str, owner: str, *, map_task_id: str = "swipe_card") -> TaskState:
    return TaskState(
        id=task_id,
        owner=owner,
        map_task_id=map_task_id,
        room="CAFETERIA",
        progress=0,
        required_ticks=3,
        completed=False,
    )


def test_world_state_defensively_copies_mapping_inputs() -> None:
    players = {"p-1": _player("p-1")}
    bodies = {"body-1": _body("body-1", "p-2")}
    tasks = {"task-1": _task("task-1", "p-1")}
    cooldowns = {"p-3": 5}
    emergency_uses = {"p-1": 1}

    state = WorldState(
        tick=7,
        phase="PLAY",
        map="canonical_1",
        players=players,
        bodies=bodies,
        tasks=tasks,
        sabotage=None,
        cooldowns=cooldowns,
        emergency_uses=emergency_uses,
        rng_state=b"rng",
        seed=42,
    )

    players["p-4"] = _player("p-4")
    bodies["body-2"] = _body("body-2", "p-5")
    tasks["task-2"] = _task("task-2", "p-4")
    cooldowns["p-6"] = 1
    emergency_uses["p-2"] = 1

    assert tuple(state.players) == ("p-1",)
    assert tuple(state.bodies) == ("body-1",)
    assert tuple(state.tasks) == ("task-1",)
    assert tuple(state.cooldowns) == ("p-3",)
    assert tuple(state.emergency_uses) == ("p-1",)


def test_world_state_mapping_fields_reject_in_place_mutation() -> None:
    state = WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players={"p-1": _player("p-1")},
        bodies={"body-1": _body("body-1", "p-2")},
        tasks={"task-1": _task("task-1", "p-1")},
        sabotage=None,
        cooldowns={"p-3": 5},
        emergency_uses={"p-1": 1},
        rng_state=b"rng",
        seed=42,
    )

    with pytest.raises(TypeError):
        state.players["p-2"] = _player("p-2")  # type: ignore[index]
    with pytest.raises(TypeError):
        state.bodies["body-2"] = _body("body-2", "p-3")  # type: ignore[index]
    with pytest.raises(TypeError):
        state.tasks["task-2"] = _task("task-2", "p-2")  # type: ignore[index]
    with pytest.raises(TypeError):
        state.cooldowns["p-4"] = 0  # type: ignore[index]
    with pytest.raises(TypeError):
        state.emergency_uses["p-2"] = 1  # type: ignore[index]


def test_world_state_keeps_public_mapping_field_names() -> None:
    state = WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players={},
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={},
        emergency_uses={},
        rng_state=b"rng",
        seed=42,
    )

    assert state.players == {}
    assert state.bodies == {}
    assert state.tasks == {}
    assert state.cooldowns == {}
    assert state.emergency_uses == {}


def test_player_state_accepts_none_last_action() -> None:
    player = _player("p-1")

    assert player.last_action is None


def test_player_state_accepts_engine_action_last_action() -> None:
    action = _action({"type": "move", "actor": "p-1", "payload": {"to_room": "ADMIN"}})
    player = PlayerState(
        id="p-1",
        role="CREWMATE",
        alive=True,
        room="CAFETERIA",
        position=(0.0, 0.0),
        last_action=action,
        in_vent=False,
    )

    assert player.last_action == action


def test_player_state_rejects_non_action_last_action() -> None:
    with pytest.raises(TypeError, match="last_action"):
        PlayerState(
            id="p-1",
            role="CREWMATE",
            alive=True,
            room="CAFETERIA",
            position=(0.0, 0.0),
            last_action=[],  # type: ignore[arg-type]
            in_vent=False,
        )
