from __future__ import annotations

from dataclasses import replace

from engine.entities import PlayerState
from engine.rng import EngineRng
from engine.visibility import compute_visibility_for_player
from engine.world import WorldState, load_canonical_map


def _player(
    player_id: str,
    room: str,
    *,
    alive: bool = True,
    in_vent: bool = False,
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="CREWMATE",
        alive=alive,
        room=room,
        position=(0.0, 0.0),
        last_action=None,
        in_vent=in_vent,
    )


def _world_state() -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "observer": _player("observer", "ADMIN"),
            "visible-crew": _player("visible-crew", "ADMIN"),
            "vented-crew": _player("vented-crew", "ADMIN", in_vent=True),
            "dead-vented-crew": _player(
                "dead-vented-crew",
                "ADMIN",
                alive=False,
                in_vent=True,
            ),
        },
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def test_visible_player_ids_hide_other_players_in_vents() -> None:
    visibility = compute_visibility_for_player(
        observer_id="observer",
        world_state=_world_state(),
        game_map=load_canonical_map(),
    )

    assert visibility.visible_player_ids == ("visible-crew",)


def test_in_vent_observer_still_receives_normal_visibility() -> None:
    state = _world_state()
    players = dict(state.players)
    players["observer"] = replace(players["observer"], in_vent=True)

    visibility = compute_visibility_for_player(
        observer_id="observer",
        world_state=replace(state, players=players),
        game_map=load_canonical_map(),
    )

    assert "ADMIN" in visibility.visible_rooms
    assert visibility.visible_player_ids == ("visible-crew",)
