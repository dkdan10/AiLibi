from __future__ import annotations

import json
from pathlib import Path

from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import PlayerState, TaskState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from observation.service import ObservationService

_SCRIPTED_GAMES = (
    "scripted_game_basic_tasks.json",
    "scripted_game_kill_report_meeting.json",
    "scripted_game_vent_and_emergency.json",
)
_FORBIDDEN_VISIBLE_PLAYER_FIELDS = frozenset({"role", "kill_attribution", "killed_by"})
_FORBIDDEN_BODY_FIELDS = frozenset({"killed_by", "kill_attribution", "player_id"})
_ACTION_ADAPTER = TypeAdapter(Action)


def _initial_world_state(*, seed: int) -> WorldState:
    game_map = load_canonical_map()
    rng_state = EngineRng.from_seed(seed).snapshot()
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
            "impostor-1": PlayerState(
                id="impostor-1",
                role="IMPOSTOR",
                alive=True,
                room=game_map.spawn.room,
                position=(2.0, 0.0),
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
        rng_state=rng_state,
        seed=seed,
    )


def _fixture_actions(script: dict[str, object]) -> dict[int, list[Action]]:
    raw_actions = TypeAdapter(list[dict[str, object]]).validate_python(script["actions"])
    actions_by_tick: dict[int, list[Action]] = {}
    for raw_action in raw_actions:
        action_data = dict(raw_action)
        tick = int(action_data.pop("tick"))
        action = _ACTION_ADAPTER.validate_python(action_data)
        actions_by_tick.setdefault(tick, []).append(action)
    return actions_by_tick


def _run_scripted_game(fixture_name: str, tmp_path: Path) -> list[dict[str, object]]:
    fixture_path = Path("tests/fixtures") / fixture_name
    script = json.loads(fixture_path.read_text(encoding="utf-8"))

    game_map = load_canonical_map()
    state = _initial_world_state(seed=int(script["seed"]))
    audit_path = tmp_path / f"audit_{fixture_name}.jsonl"
    observation_service = ObservationService(game_map=game_map, audit_log_path=audit_path)
    actions_by_tick = _fixture_actions(script)

    for tick in range(max(actions_by_tick, default=-1) + 1):
        assert state.tick == tick
        state, _ = advance_tick(state, actions_by_tick.get(tick, []))
        for player_id, player in state.players.items():
            if player.alive:
                observation_service.build_packet(world_state=state, agent_id=player_id)
        if state.phase == "GAME_OVER":
            break

    return [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]


def test_no_observation_leaks_hidden_information(tmp_path: Path) -> None:
    for fixture_name in _SCRIPTED_GAMES:
        packets = _run_scripted_game(fixture_name, tmp_path)
        assert packets, f"no packets captured for {fixture_name}"

        for packet in packets:
            assert "self_state" in packet
            for visible_player in packet["visible_players"]:
                assert set(visible_player.keys()) == {"id", "room", "action"}
                assert _FORBIDDEN_VISIBLE_PLAYER_FIELDS.isdisjoint(visible_player.keys())
            for visible_body in packet["visible_bodies"]:
                assert set(visible_body.keys()) == {"id", "room"}
                assert _FORBIDDEN_BODY_FIELDS.isdisjoint(visible_body.keys())
            if packet["self_state"]["role"] == "CREWMATE":
                assert packet["cooldown"] is None
