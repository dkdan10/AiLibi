from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.actions import KillAction, MoveAction  # noqa: E402
from engine.entities import PlayerState  # noqa: E402
from engine.rng import EngineRng  # noqa: E402
from engine.tick import advance_tick  # noqa: E402
from engine.world import WorldState, load_canonical_map  # noqa: E402
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


def test_visible_player_action_does_not_reveal_unseen_kill(tmp_path: Path) -> None:
    state, _ = advance_tick(
        _base_world_state(),
        [KillAction(type="kill", actor="impostor", payload={"target": "victim"})],
    )
    state, _ = advance_tick(
        state,
        [
            MoveAction(
                type="move",
                actor="observer",
                payload={"to_room": "ENGINEERING"},
            )
        ],
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="observer",
    )

    visible_impostor = next(
        player for player in packet.visible_players if player.id == "impostor"
    )
    assert visible_impostor.action is None


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
    )

    assert packet.cooldown == 6


def test_audit_log_records_sanitized_packet(tmp_path: Path) -> None:
    state, _ = advance_tick(
        _base_world_state(),
        [KillAction(type="kill", actor="impostor", payload={"target": "victim"})],
    )
    state, _ = advance_tick(
        state,
        [
            MoveAction(
                type="move",
                actor="observer",
                payload={"to_room": "ENGINEERING"},
            )
        ],
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

    service.build_packet(world_state=state_with_bad_cooldown, agent_id="observer")

    [audit_entry] = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    visible_impostor = next(
        player for player in audit_entry["visible_players"] if player["id"] == "impostor"
    )
    assert visible_impostor["action"] is None
    assert audit_entry["cooldown"] is None
