from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict, TypeAdapter

from engine.actions import Action
from engine.entities import PlayerState, TaskState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from orchestrator.replay import ReplayLog, read_replay_entries

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)
_SCRIPTED_GAMES = (
    "scripted_game_basic_tasks.json",
    "scripted_game_kill_report_meeting.json",
    "scripted_game_vent_and_emergency.json",
)


class _ScriptedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tick: int
    type: str
    actor: str
    payload: dict[str, object]


class _ScriptedGame(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    seed: int
    actions: list[_ScriptedAction]


def _initial_world_state(*, seed: int) -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "player-1": PlayerState(
                id="player-1",
                role="CREWMATE",
                alive=True,
                room=game_map.spawn.room,
                position=(0.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
            "player-2": PlayerState(
                id="player-2",
                role="CREWMATE",
                alive=True,
                room=game_map.spawn.room,
                position=(1.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
            "player-3": PlayerState(
                id="player-3",
                role="CREWMATE",
                alive=True,
                room=game_map.spawn.room,
                position=(3.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
            "impostor-1": PlayerState(
                id="impostor-1",
                role="IMPOSTOR",
                alive=True,
                room=game_map.spawn.room,
                position=(2.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
        },
        bodies={},
        tasks={
            "swipe_card": TaskState(
                id="swipe_card",
                owner="player-1",
                room="ADMIN",
                progress=0,
                required_ticks=1,
                completed=False,
            ),
            "submit_scan": TaskState(
                id="submit_scan",
                owner="player-2",
                room="MEDBAY",
                progress=0,
                required_ticks=1,
                completed=False,
            ),
            "empty_trash": TaskState(
                id="empty_trash",
                owner="player-3",
                room="CAFETERIA",
                progress=0,
                required_ticks=1,
                completed=False,
            ),
        },
        sabotage=None,
        cooldowns={"impostor-1": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def _fixture_actions(fixture_name: str) -> tuple[int, dict[int, list[Action]]]:
    fixture_path = Path("tests/fixtures") / fixture_name
    script = _ScriptedGame.model_validate_json(fixture_path.read_text(encoding="utf-8"))
    actions_by_tick: dict[int, list[Action]] = {}
    for raw_action in script.actions:
        action_data = raw_action.model_dump(exclude={"tick"})
        action = _ACTION_ADAPTER.validate_python(action_data)
        actions_by_tick.setdefault(raw_action.tick, []).append(action)
    return script.seed, actions_by_tick


def _write_fixture_replay(fixture_name: str, path: Path) -> bytes:
    seed, actions_by_tick = _fixture_actions(fixture_name)
    game_map = load_canonical_map()
    state = _initial_world_state(seed=seed)
    replay = ReplayLog(path, game_id=fixture_name)

    for tick in range(max(actions_by_tick, default=-1) + 1):
        assert state.tick == tick
        actions = actions_by_tick.get(tick, [])
        state, _ = advance_tick(state, actions, game_map=game_map)
        replay.record_tick(tick, actions, state)
        if state.phase == "GAME_OVER":
            break

    return path.read_bytes()


def test_replay_log_writes_jsonl_for_dataclass_world_state(tmp_path: Path) -> None:
    state = _initial_world_state(seed=101)
    replay_path = tmp_path / "replay.jsonl"

    ReplayLog(replay_path, game_id="dataclass-state").record_tick(0, [], state)

    entry = json.loads(replay_path.read_text(encoding="utf-8"))
    assert entry["game_id"] == "dataclass-state"
    assert entry["tick"] == 0
    assert entry["actions"] == []
    assert isinstance(entry["state_hash"], str)
    assert len(entry["state_hash"]) == 64


def test_replay_log_reads_written_entries(tmp_path: Path) -> None:
    state = _initial_world_state(seed=303)
    action = _ACTION_ADAPTER.validate_python(
        {"type": "move", "actor": "player-1", "payload": {"to_room": "UPPER_HALL"}}
    )
    replay_path = tmp_path / "roundtrip.jsonl"
    replay = ReplayLog(replay_path, game_id="roundtrip")

    replay.record_tick(0, [], state)
    moved_state, _ = advance_tick(state, [action], game_map=load_canonical_map())
    replay.record_tick(1, [action], moved_state)

    entries = replay.read_entries()

    assert entries == read_replay_entries(replay_path)
    assert [entry.tick for entry in entries] == [0, 1]
    assert entries[0].game_id == "roundtrip"
    assert entries[0].actions == ()
    assert entries[1].actions == (
        {"actor": "player-1", "payload": {"to_room": "UPPER_HALL"}, "type": "move"},
    )
    assert all(len(entry.state_hash) == 64 for entry in entries)


@pytest.mark.parametrize("fixture_name", _SCRIPTED_GAMES)
def test_identical_seed_and_actions_produce_byte_identical_replay(
    tmp_path: Path,
    fixture_name: str,
) -> None:
    first = _write_fixture_replay(
        fixture_name,
        tmp_path / "first.jsonl",
    )
    second = _write_fixture_replay(
        fixture_name,
        tmp_path / "second.jsonl",
    )

    assert first == second


def test_state_hash_changes_when_state_changes(tmp_path: Path) -> None:
    state = _initial_world_state(seed=202)
    changed_state = replace(state, tick=state.tick + 1)
    replay_path = tmp_path / "changed.jsonl"
    replay = ReplayLog(replay_path, game_id="state-hash")

    replay.record_tick(0, [], state)
    replay.record_tick(1, [], changed_state)

    first, second = [
        json.loads(line)
        for line in replay_path.read_text(encoding="utf-8").splitlines()
    ]
    assert first["state_hash"] != second["state_hash"]
