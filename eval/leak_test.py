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
_FORBIDDEN_VISIBLE_PLAYER_ACTIONS = frozenset({"sabotage"})
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
    raw_actions = TypeAdapter(list[dict[str, object]]).validate_python(
        script["actions"]
    )
    actions_by_tick: dict[int, list[Action]] = {}
    for raw_action in raw_actions:
        action_data = dict(raw_action)
        tick = int(action_data.pop("tick"))
        action = _ACTION_ADAPTER.validate_python(action_data)
        actions_by_tick.setdefault(tick, []).append(action)
    return actions_by_tick


def _run_scripted_game(
    fixture_name: str,
    tmp_path: Path,
) -> list[tuple[dict[str, object], list[dict[str, object]]]]:
    fixture_path = Path("tests/fixtures") / fixture_name
    script = json.loads(fixture_path.read_text(encoding="utf-8"))

    game_map = load_canonical_map()
    state = _initial_world_state(seed=int(script["seed"]))
    audit_path = tmp_path / f"audit_{fixture_name}.jsonl"
    observation_service = ObservationService(
        game_map=game_map, audit_log_path=audit_path
    )
    actions_by_tick = _fixture_actions(script)

    packet_records: list[tuple[dict[str, object], list[dict[str, object]]]] = []
    for tick in range(max(actions_by_tick, default=-1) + 1):
        assert state.tick == tick
        state, events = advance_tick(
            state,
            actions_by_tick.get(tick, []),
            game_map=game_map,
        )
        for player_id, player in state.players.items():
            if player.alive:
                packet = observation_service.build_packet(
                    world_state=state,
                    agent_id=player_id,
                    engine_events=events,
                )
                packet_records.append((packet.model_dump(mode="json"), events))
        if state.phase == "GAME_OVER":
            break

    audit_packets = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    assert audit_packets == [packet for packet, _ in packet_records]
    return packet_records


def _event_witnesses(event: dict[str, object], key: str) -> tuple[str, ...]:
    details = event.get("details")
    if not isinstance(details, dict):
        return ()
    raw_witnesses = details.get(key)
    if not isinstance(raw_witnesses, (list, tuple)):
        return ()
    return tuple(witness for witness in raw_witnesses if isinstance(witness, str))


def _action_is_permitted_by_witness_event(
    *,
    action: object,
    actor_id: object,
    agent_id: object,
    engine_events: list[dict[str, object]],
) -> bool:
    if (
        not isinstance(action, str)
        or not isinstance(actor_id, str)
        or not isinstance(agent_id, str)
    ):
        return False
    for event in engine_events:
        if event.get("actor") != actor_id:
            continue
        event_type = event.get("type")
        if action == "kill" and event_type == "Killed":
            return agent_id in _event_witnesses(event, "witnesses")
        if action == "vent" and event_type in {"VentEntered", "VentExited"}:
            return agent_id in _event_witnesses(event, "witnesses")
    return False


def test_no_observation_leaks_hidden_information(tmp_path: Path) -> None:
    for fixture_name in _SCRIPTED_GAMES:
        packet_records = _run_scripted_game(fixture_name, tmp_path)
        assert packet_records, f"no packets captured for {fixture_name}"

        for packet, engine_events in packet_records:
            assert "self_state" in packet
            for visible_player in packet["visible_players"]:
                assert set(visible_player.keys()) == {"id", "room", "action"}
                assert _FORBIDDEN_VISIBLE_PLAYER_FIELDS.isdisjoint(
                    visible_player.keys()
                )
                assert visible_player["action"] not in _FORBIDDEN_VISIBLE_PLAYER_ACTIONS
                if visible_player["action"] in {"kill", "vent"}:
                    assert _action_is_permitted_by_witness_event(
                        action=visible_player["action"],
                        actor_id=visible_player["id"],
                        agent_id=packet["agent_id"],
                        engine_events=engine_events,
                    )
            for visible_body in packet["visible_bodies"]:
                assert set(visible_body.keys()) == {"id", "room"}
                assert _FORBIDDEN_BODY_FIELDS.isdisjoint(visible_body.keys())
            if packet["self_state"]["role"] == "CREWMATE":
                assert packet["cooldown"] is None
