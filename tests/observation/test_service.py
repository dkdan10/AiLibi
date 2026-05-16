from __future__ import annotations

import dataclasses
from collections.abc import Sequence
import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyState, PlayerState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from observation.packet import PlayerView
from observation.service import ObservationService

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


def _base_world_state(*, seed: int = 42) -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "p-1": _player("p-1", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "p-2": _player("p-2", "CREWMATE", "REACTOR", (0.0, 0.0)),
            "p-3": _player("p-3", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "p-4": _player("p-4", "IMPOSTOR", "STORAGE", (1.0, 0.0)),
        },
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={"p-4": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def _observation_service(tmp_path: Path) -> ObservationService:
    return ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "observation_audit.jsonl",
    )


def _visible_player(packet_id: str, packet_players: Sequence[PlayerView]) -> PlayerView:
    return next(player for player in packet_players if player.id == packet_id)


def test_kill_witness_sees_killer_action(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["p-2"] = _player("p-2", "CREWMATE", "STORAGE", (2.0, 0.0))
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
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=events,
    )

    visible_impostor = _visible_player("p-4", packet.visible_players)
    assert visible_impostor.action == "kill"


def test_visible_player_action_does_not_reveal_unseen_kill(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _base_world_state(),
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )
    state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "ENGINEERING"},
                }
            )
        ],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=events,
    )

    visible_impostor = _visible_player("p-4", packet.visible_players)
    assert visible_impostor.action is None


def test_vent_witness_sees_vent_action_and_audible_event(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["p-4"] = _player("p-4", "IMPOSTOR", "ADMIN", (1.0, 0.0))
    players["p-2"] = _player("p-2", "CREWMATE", "ADMIN", (0.0, 0.0))
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
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-4",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=events,
    )

    visible_impostor = _visible_player("p-4", packet.visible_players)
    assert visible_impostor.action == "vent"
    assert [event.model_dump(mode="json") for event in packet.audible_events] == [
        {"kind": "vent_use_heard", "room": "ADMIN"},
    ]


def test_vented_player_is_hidden_without_same_tick_event(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["p-4"] = _player("p-4", "IMPOSTOR", "ADMIN", (1.0, 0.0))
    players["p-2"] = _player("p-2", "CREWMATE", "ADMIN", (0.0, 0.0))
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
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-4",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=[],
    )

    assert "p-4" not in {player.id for player in packet.visible_players}


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
        cooldowns={**dict(state.cooldowns), "p-2": 7},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state_with_bad_cooldown,
        agent_id="p-2",
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
        cooldowns={"p-4": 6},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state_with_cooldown,
        agent_id="p-4",
        engine_events=[],
    )

    assert packet.cooldown == 6


def test_audit_log_records_sanitized_packet(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _base_world_state(),
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )
    state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "ENGINEERING"},
                }
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
        cooldowns={**dict(state.cooldowns), "p-2": 7},
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
        agent_id="p-2",
        engine_events=events,
    )

    [audit_entry] = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    visible_impostor = next(
        player for player in audit_entry["visible_players"] if player["id"] == "p-4"
    )
    assert audit_entry == packet.model_dump(mode="json")
    assert visible_impostor["action"] is None
    assert audit_entry["cooldown"] is None


def test_discovered_body_is_hidden_from_subsequent_packets(tmp_path: Path) -> None:
    # Pins today's engine/visibility.py rule (DESIGN.md §3.6 / §4.2): once a
    # body has discovered_by set, it is filtered out of every observer's
    # visible_bodies — including the discoverer's own packet on the same tick.
    state = _base_world_state()
    body = BodyState(
        id="body-p-1-0",
        player_id="p-1",
        room="REACTOR",
        position=(0.0, 0.0),
        killed_by="p-4",
        discovered_by=None,
    )
    state_with_body = dataclasses.replace(state, bodies={body.id: body})
    service = _observation_service(tmp_path)

    packet_before = service.build_packet(
        world_state=state_with_body,
        agent_id="p-2",
        engine_events=[],
    )
    assert "body-p-1-0" in {b.id for b in packet_before.visible_bodies}

    discovered_body = dataclasses.replace(body, discovered_by="p-2")
    state_after_discovery = dataclasses.replace(
        state_with_body, bodies={discovered_body.id: discovered_body}
    )

    packet_after = service.build_packet(
        world_state=state_after_discovery,
        agent_id="p-2",
        engine_events=[],
    )

    assert packet_after.visible_bodies == ()


def test_observation_packet_collections_are_immutable(tmp_path: Path) -> None:
    packet = _observation_service(tmp_path).build_packet(
        world_state=_base_world_state(),
        agent_id="p-2",
        engine_events=[],
    )

    assert isinstance(packet.visible_players, tuple)
    assert isinstance(packet.visible_bodies, tuple)
    assert isinstance(packet.audible_events, tuple)
    with pytest.raises(AttributeError):
        packet.visible_players.append(PlayerView(id="x", room="ADMIN", action=None))  # type: ignore[attr-defined]


def test_audit_log_appends_across_two_instances(tmp_path: Path) -> None:
    """R-13 regression: two ``ObservationService`` instances pointed at the
    same audit-log path must each *append*, not overwrite. Pins
    ``observation/audit.py:20-23`` open mode ``"a"`` — flipping to ``"w"``
    silently slips past single-instance tests today.
    """

    state = _base_world_state()
    service_one = _observation_service(tmp_path)
    service_one.build_packet(world_state=state, agent_id="p-1", engine_events=[])
    del service_one

    service_two = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "observation_audit.jsonl",
    )
    service_two.build_packet(world_state=state, agent_id="p-2", engine_events=[])

    audit_path = tmp_path / "observation_audit.jsonl"
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first_entry = json.loads(lines[0])
    second_entry = json.loads(lines[1])
    assert first_entry["agent_id"] == "p-1"
    assert second_entry["agent_id"] == "p-2"
