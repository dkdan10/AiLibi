from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from pydantic import TypeAdapter

from engine.entities import BodyState, PlayerState, TaskState
from engine.rng import EngineRng
from engine.world import WorldState, load_canonical_map
from observation.service import ObservationService

_SCRIPTED_GAMES = (
    "scripted_game_basic_tasks.json",
    "scripted_game_kill_report_meeting.json",
    "scripted_game_vent_and_emergency.json",
)
_FORBIDDEN_VISIBLE_PLAYER_FIELDS = frozenset({"role", "kill_attribution", "killed_by"})


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
        },
        sabotage=None,
        cooldowns={"impostor-1": 0},
        rng_state=rng_state,
        seed=seed,
    )


def _apply_action(state: WorldState, action: dict[str, object], *, valid_rooms: set[str]) -> WorldState:
    actor = str(action["actor"])
    action_type = str(action["type"])
    payload = action.get("payload", {})
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    players = dict(state.players)
    tasks = dict(state.tasks)
    bodies = dict(state.bodies)

    if actor in players:
        players[actor] = replace(players[actor], last_action=action)

    if action_type == "move" and actor in players:
        to_room = str(payload["to_room"])
        if to_room in valid_rooms:
            players[actor] = replace(players[actor], room=to_room, in_vent=False)
    elif action_type == "do_task":
        task_id = str(payload["task_id"])
        if task_id in tasks:
            tasks[task_id] = replace(tasks[task_id], completed=True, progress=tasks[task_id].required_ticks)
    elif action_type == "kill":
        target = str(payload["target"])
        if target in players and actor in players:
            players[target] = replace(players[target], alive=False)
            bodies[f"body-{target}"] = BodyState(
                id=f"body-{target}",
                player_id=target,
                room=players[target].room,
                position=players[target].position,
                killed_by=actor,
                discovered_by=None,
            )
    elif action_type == "report":
        body_id = str(payload["body_id"])
        if body_id in bodies:
            bodies[body_id] = replace(bodies[body_id], discovered_by=actor)
    elif action_type == "vent" and actor in players:
        players[actor] = replace(players[actor], in_vent=True)

    return replace(state, players=players, tasks=tasks, bodies=bodies)


def _run_scripted_game(fixture_name: str, tmp_path: Path) -> list[dict[str, object]]:
    fixture_path = Path("tests/fixtures") / fixture_name
    script = json.loads(fixture_path.read_text(encoding="utf-8"))
    actions = TypeAdapter(list[dict[str, object]]).validate_python(script["actions"])

    game_map = load_canonical_map()
    state = _initial_world_state(seed=int(script["seed"]))
    audit_path = tmp_path / f"audit_{fixture_name}.jsonl"
    observation_service = ObservationService(game_map=game_map, audit_log_path=audit_path)

    actions_by_tick: dict[int, list[dict[str, object]]] = {}
    for action in actions:
        tick = int(action["tick"])
        actions_by_tick.setdefault(tick, []).append(action)

    for tick in sorted(actions_by_tick):
        state = replace(state, tick=tick)
        for action in actions_by_tick[tick]:
            state = _apply_action(state, action, valid_rooms=set(game_map.rooms))
        for player_id, player in state.players.items():
            if player.alive:
                observation_service.build_packet(world_state=state, agent_id=player_id)

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
