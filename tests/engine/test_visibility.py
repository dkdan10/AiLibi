from __future__ import annotations

from dataclasses import replace

import pytest

from engine.entities import PlayerState, SabotageState
from engine.rng import EngineRng
from engine.visibility import (
    compute_visibility_for_player,
    resolve_visibility_mode,
    visible_rooms_for_player,
)
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


# ---------------------------------------------------------------------------
# Active lights-out sabotage (audit I-I-1).
#
# Lights-out is the sole MVP sabotage and collapses visibility to same-room-
# only, but no prior test exercised the active-sabotage branch of
# `resolve_visibility_mode` (engine/visibility.py): the two tests above and all
# seven `test_service.py` world states use `sabotage=None`. A regression that
# dropped the `world_state.sabotage.active` lookup would pass the whole suite
# while letting crewmates see through a blackout. These tests pin that branch.
# ---------------------------------------------------------------------------


def _lights_sabotage(*, active: bool = True, kind: str = "lights") -> SabotageState:
    """Build a lights sabotage state for the visibility tests.

    ``affected_rooms`` mirrors the canonical map's ``lights`` repair room. The
    visibility resolver does not read it — it keys off ``kind`` plus the map's
    sabotage definition — so its value is immaterial to these tests.
    """

    return SabotageState(
        kind=kind,
        remaining_ticks=90,
        affected_rooms=("ADMIN",),
        active=active,
    )


def _sabotage_world_state(
    *,
    sabotage: SabotageState | None,
    observer_room: str = "ADMIN",
    other_room: str = "ADMIN",
) -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "observer": _player("observer", observer_room),
            "other-crew": _player("other-crew", other_room),
        },
        bodies={},
        tasks={},
        sabotage=sabotage,
        cooldowns={},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def test_active_lights_sabotage_resolves_to_same_room_only() -> None:
    game_map = load_canonical_map()
    state = _sabotage_world_state(sabotage=_lights_sabotage())

    assert resolve_visibility_mode(state, game_map) == "same_room_only"


def test_inactive_lights_sabotage_keeps_base_visibility() -> None:
    # The `active` flag is load-bearing: an inactive (e.g. fully repaired)
    # sabotage must fall back to the map's base mode, not the blackout mode.
    game_map = load_canonical_map()
    state = _sabotage_world_state(sabotage=_lights_sabotage(active=False))

    assert resolve_visibility_mode(state, game_map) == game_map.visibility_defaults.base
    assert resolve_visibility_mode(state, game_map) == "same_room_and_adjacent"


def test_active_lights_sabotage_collapses_visible_rooms_to_own_room() -> None:
    game_map = load_canonical_map()
    state = _sabotage_world_state(sabotage=_lights_sabotage())
    observer = state.players["observer"]

    mode = resolve_visibility_mode(state, game_map)
    visible_rooms = visible_rooms_for_player(
        observer=observer, game_map=game_map, mode=mode
    )

    assert visible_rooms == (observer.room,)


def test_active_lights_sabotage_hides_player_in_adjacent_room() -> None:
    # UPPER_HALL is directly adjacent to ADMIN, so the other crewmate is
    # visible with the lights on and disappears under an active blackout.
    game_map = load_canonical_map()
    lit = _sabotage_world_state(
        sabotage=None, observer_room="ADMIN", other_room="UPPER_HALL"
    )
    blackout = _sabotage_world_state(
        sabotage=_lights_sabotage(), observer_room="ADMIN", other_room="UPPER_HALL"
    )

    lit_visibility = compute_visibility_for_player(
        observer_id="observer", world_state=lit, game_map=game_map
    )
    assert "other-crew" in lit_visibility.visible_player_ids

    blackout_visibility = compute_visibility_for_player(
        observer_id="observer", world_state=blackout, game_map=game_map
    )
    assert blackout_visibility.visible_rooms == ("ADMIN",)
    assert "other-crew" not in blackout_visibility.visible_player_ids


def test_unknown_sabotage_kind_raises_value_error() -> None:
    # An active sabotage whose kind is absent from the map's sabotage table
    # must fail loud (no silent fallback to base visibility).
    game_map = load_canonical_map()
    state = _sabotage_world_state(sabotage=_lights_sabotage(kind="reactor_meltdown"))

    with pytest.raises(ValueError, match="unknown sabotage kind: reactor_meltdown"):
        resolve_visibility_mode(state, game_map)
