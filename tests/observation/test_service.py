from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.actions import KillAction, MoveAction, VentAction  # noqa: E402
from engine.entities import PlayerState  # noqa: E402
from engine.rng import EngineRng  # noqa: E402
from engine.tick import advance_tick  # noqa: E402
from engine.world import WorldState, load_canonical_map  # noqa: E402
from observation.packet import PlayerView  # noqa: E402
from observation.service import ObservationService  # noqa: E402


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


def _base_world_state(*, seed: int = 42) -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "victim": _player("victim", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "observer": _player("observer", "CREWMATE", "REACTOR", (0.0, 0.0)),
            "crew-2": _player("crew-2", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "impostor": _player("impostor", "IMPOSTOR", "STORAGE", (1.0, 0.0)),
        },
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={"impostor": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def _observation_service(tmp_path: Path) -> ObservationService:
    return ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "observation_audit.jsonl",
    )


def _visible_player(packet_id: str, packet_players: list[PlayerView]) -> PlayerView:
    return next(player for player in packet_players if player.id == packet_id)


def test_kill_witness_sees_killer_action(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["observer"] = _player("observer", "CREWMATE", "STORAGE", (2.0, 0.0))
    state = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns=state.cooldowns,
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    state, events = advance_tick(
        state,
        [KillAction(type="kill", actor="impostor", payload={"target": "victim"})],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="observer",
        engine_events=events,
    )

    visible_impostor = _visible_player("impostor", packet.visible_players)
    assert visible_impostor.action == "kill"


def test_visible_player_action_does_not_reveal_unseen_kill(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _base_world_state(),
        [KillAction(type="kill", actor="impostor", payload={"target": "victim"})],
        game_map=game_map,
    )
    state, events = advance_tick(
        state,
        [
            MoveAction(
                type="move",
                actor="observer",
                payload={"to_room": "ENGINEERING"},
            )
        ],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="observer",
        engine_events=events,
    )

    visible_impostor = _visible_player("impostor", packet.visible_players)
    assert visible_impostor.action is None


def test_vent_witness_sees_vent_action_and_audible_event(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["impostor"] = _player("impostor", "IMPOSTOR", "ADMIN", (1.0, 0.0))
    players["observer"] = _player("observer", "CREWMATE", "ADMIN", (0.0, 0.0))
    state = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns=state.cooldowns,
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    state, events = advance_tick(
        state,
        [VentAction(type="vent", actor="impostor", payload={"vent_id": "ADMIN_VENT"})],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="observer",
        engine_events=events,
    )

    visible_impostor = _visible_player("impostor", packet.visible_players)
    assert visible_impostor.action == "vent"
    assert [event.model_dump(mode="json") for event in packet.audible_events] == [
        {"kind": "vent_use_heard", "room": "ADMIN"},
    ]


def test_vented_player_is_hidden_without_same_tick_event(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["impostor"] = _player("impostor", "IMPOSTOR", "ADMIN", (1.0, 0.0))
    players["observer"] = _player("observer", "CREWMATE", "ADMIN", (0.0, 0.0))
    state = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns=state.cooldowns,
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )
    state, _ = advance_tick(
        state,
        [VentAction(type="vent", actor="impostor", payload={"vent_id": "ADMIN_VENT"})],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="observer",
        engine_events=[],
    )

    assert "impostor" not in {player.id for player in packet.visible_players}


def test_crewmate_cooldown_is_never_exposed(tmp_path: Path) -> None:
    state = _base_world_state()
    state_with_bad_cooldown = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=state.players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns={**dict(state.cooldowns), "observer": 7},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state_with_bad_cooldown,
        agent_id="observer",
        engine_events=[],
    )

    assert packet.cooldown is None


def test_impostor_receives_own_cooldown(tmp_path: Path) -> None:
    state = _base_world_state()
    state_with_cooldown = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=state.players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns={"impostor": 6},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state_with_cooldown,
        agent_id="impostor",
        engine_events=[],
    )

    assert packet.cooldown == 6


def test_audit_log_records_sanitized_packet(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _base_world_state(),
        [KillAction(type="kill", actor="impostor", payload={"target": "victim"})],
        game_map=game_map,
    )
    state, events = advance_tick(
        state,
        [
            MoveAction(
                type="move",
                actor="observer",
                payload={"to_room": "ENGINEERING"},
            )
        ],
        game_map=game_map,
    )
    state_with_bad_cooldown = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=state.players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns={**dict(state.cooldowns), "observer": 7},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )
    audit_path = tmp_path / "observation_audit.jsonl"
    service = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=audit_path,
    )

    packet = service.build_packet(
        world_state=state_with_bad_cooldown,
        agent_id="observer",
        engine_events=events,
    )

    [audit_entry] = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    visible_impostor = next(
        player
        for player in audit_entry["visible_players"]
        if player["id"] == "impostor"
    )
    assert audit_entry == packet.model_dump(mode="json")
    assert visible_impostor["action"] is None
    assert audit_entry["cooldown"] is None
