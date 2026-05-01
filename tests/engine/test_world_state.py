from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.entities import BodyState, PlayerState, TaskState  # noqa: E402
from engine.world import WorldState  # noqa: E402


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


def _task(task_id: str, owner: str) -> TaskState:
    return TaskState(
        id=task_id,
        owner=owner,
        room="CAFETERIA",
        progress=0,
        required_ticks=3,
        completed=False,
    )


def test_world_state_defensively_copies_mapping_inputs() -> None:
    players = {"player-1": _player("player-1")}
    bodies = {"body-1": _body("body-1", "player-2")}
    tasks = {"task-1": _task("task-1", "player-1")}
    cooldowns = {"player-3": 5}

    state = WorldState(
        tick=7,
        phase="PLAY",
        map="canonical_1",
        players=players,
        bodies=bodies,
        tasks=tasks,
        sabotage=None,
        cooldowns=cooldowns,
        rng_state=b"rng",
        seed=42,
    )

    players["player-4"] = _player("player-4")
    bodies["body-2"] = _body("body-2", "player-5")
    tasks["task-2"] = _task("task-2", "player-4")
    cooldowns["player-6"] = 1

    assert tuple(state.players) == ("player-1",)
    assert tuple(state.bodies) == ("body-1",)
    assert tuple(state.tasks) == ("task-1",)
    assert tuple(state.cooldowns) == ("player-3",)


def test_world_state_mapping_fields_reject_in_place_mutation() -> None:
    state = WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players={"player-1": _player("player-1")},
        bodies={"body-1": _body("body-1", "player-2")},
        tasks={"task-1": _task("task-1", "player-1")},
        sabotage=None,
        cooldowns={"player-3": 5},
        rng_state=b"rng",
        seed=42,
    )

    with pytest.raises(TypeError):
        state.players["player-2"] = _player("player-2")  # type: ignore[index]
    with pytest.raises(TypeError):
        state.bodies["body-2"] = _body("body-2", "player-3")  # type: ignore[index]
    with pytest.raises(TypeError):
        state.tasks["task-2"] = _task("task-2", "player-2")  # type: ignore[index]
    with pytest.raises(TypeError):
        state.cooldowns["player-4"] = 0  # type: ignore[index]


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
        rng_state=b"rng",
        seed=42,
    )

    assert state.players == {}
    assert state.bodies == {}
    assert state.tasks == {}
    assert state.cooldowns == {}
