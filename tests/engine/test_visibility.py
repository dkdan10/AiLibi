from __future__ import annotations

from dataclasses import replace

import pytest

from engine.entities import PlayerState, Role, SabotageState
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
    role: Role = "CREWMATE",
    alive: bool = True,
    in_vent: bool = False,
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role=role,
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
    observer_role: Role = "CREWMATE",
    observer_room: str = "ADMIN",
    other_room: str = "ADMIN",
) -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "observer": _player("observer", observer_room, role=observer_role),
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
    # UPPER_HALL is directly adjacent to ADMIN. The observer is an IMPOSTOR so
    # that the base case carries adjacent sight to LOSE: under asymmetric
    # visibility (Task 13.8) the impostor keeps `same_room_and_adjacent` at base,
    # so the other player is visible with the lights on — and an ACTIVE blackout
    # collapses EVERYONE (the impostor included) to `same_room_only`, hiding the
    # adjacent player. (A crewmate observer would already be room-only at base;
    # the asymmetric base behaviour is pinned separately below.)
    game_map = load_canonical_map()
    lit = _sabotage_world_state(
        sabotage=None,
        observer_role="IMPOSTOR",
        observer_room="ADMIN",
        other_room="UPPER_HALL",
    )
    blackout = _sabotage_world_state(
        sabotage=_lights_sabotage(),
        observer_role="IMPOSTOR",
        observer_room="ADMIN",
        other_room="UPPER_HALL",
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


# ---------------------------------------------------------------------------
# Asymmetric role-parameterized visibility (Task 13.8).
#
# At BASE visibility (no active sabotage degrade) a CREWMATE is downgraded to
# `same_room_only` while an IMPOSTOR keeps the base `same_room_and_adjacent` —
# the genre-correct impostor sight edge (crew must INFER private kills from
# testimony rather than witness them). An ACTIVE sabotage degrade still collapses
# EVERYONE to `same_room_only`, the impostor included. The seam lives inside
# `compute_visibility_for_player` (it holds the observer with `.role`); the
# predicate mirrors `experiments/lab/visibility_resim_asymmetric.py`. The base
# map mode stays `same_room_and_adjacent` — the asymmetry is role-parameterized
# in code, NOT a yaml base flip.
#
# UPPER_HALL is directly adjacent to ADMIN in canonical_1, so it is the probe
# for "did the observer keep adjacent sight": visible iff the observer's
# effective mode is `same_room_and_adjacent`.
# ---------------------------------------------------------------------------


def test_crew_observer_at_base_sees_only_own_room() -> None:
    # No active sabotage -> base visibility. A CREWMATE observer is downgraded to
    # `same_room_only`, so a player in the directly-adjacent UPPER_HALL is NOT
    # visible (the crew must deduce, not witness).
    game_map = load_canonical_map()
    state = _sabotage_world_state(
        sabotage=None,
        observer_role="CREWMATE",
        observer_room="ADMIN",
        other_room="UPPER_HALL",
    )

    visibility = compute_visibility_for_player(
        observer_id="observer", world_state=state, game_map=game_map
    )

    assert visibility.visible_rooms == ("ADMIN",)
    assert "other-crew" not in visibility.visible_player_ids


def test_crew_observer_at_base_still_sees_co_located_player() -> None:
    # The room-only downgrade must not blind the crewmate to its OWN room: a
    # co-located player stays visible (the kill the crew CAN witness).
    game_map = load_canonical_map()
    state = _sabotage_world_state(
        sabotage=None,
        observer_role="CREWMATE",
        observer_room="ADMIN",
        other_room="ADMIN",
    )

    visibility = compute_visibility_for_player(
        observer_id="observer", world_state=state, game_map=game_map
    )

    assert visibility.visible_rooms == ("ADMIN",)
    assert "other-crew" in visibility.visible_player_ids


def test_impostor_observer_at_base_keeps_adjacent_sight() -> None:
    # No active sabotage -> base visibility. An IMPOSTOR observer keeps the base
    # `same_room_and_adjacent`, so a player in the directly-adjacent UPPER_HALL
    # remains visible — the predator's sight edge.
    game_map = load_canonical_map()
    state = _sabotage_world_state(
        sabotage=None,
        observer_role="IMPOSTOR",
        observer_room="ADMIN",
        other_room="UPPER_HALL",
    )

    visibility = compute_visibility_for_player(
        observer_id="observer", world_state=state, game_map=game_map
    )

    expected_rooms = tuple(sorted({"ADMIN", *game_map.room_neighbors("ADMIN")}))
    assert visibility.visible_rooms == expected_rooms
    assert "UPPER_HALL" in visibility.visible_rooms
    assert "other-crew" in visibility.visible_player_ids


def test_active_sabotage_degrades_impostor_to_same_room_only() -> None:
    # The asymmetry is a BASE-only edge: an ACTIVE sabotage degrade (lights ->
    # `same_room_only`, a mode != base) still degrades EVERYONE, so even the
    # IMPOSTOR collapses to its own room and loses the adjacent player.
    game_map = load_canonical_map()
    state = _sabotage_world_state(
        sabotage=_lights_sabotage(),
        observer_role="IMPOSTOR",
        observer_room="ADMIN",
        other_room="UPPER_HALL",
    )

    visibility = compute_visibility_for_player(
        observer_id="observer", world_state=state, game_map=game_map
    )

    assert visibility.visible_rooms == ("ADMIN",)
    assert "other-crew" not in visibility.visible_player_ids
