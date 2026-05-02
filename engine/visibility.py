from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from engine.entities import BodyId, BodyState, PlayerId, PlayerState, RoomId
from engine.world import Map, VisibilityMode, WorldState


@dataclass(frozen=True)
class VisibilityResult:
    """Visibility-constrained world slice for a single observer.

    This structure intentionally includes only entity ids for other players and
    bodies, preserving hidden engine information (roles, kill attribution,
    cooldowns, and other private fields) behind the observation firewall.
    """

    observer_id: PlayerId
    visible_rooms: tuple[RoomId, ...]
    visible_player_ids: tuple[PlayerId, ...]
    visible_body_ids: tuple[BodyId, ...]


def resolve_visibility_mode(world_state: WorldState, game_map: Map) -> VisibilityMode:
    """Return the effective visibility mode for the current world state."""

    if world_state.sabotage is None or not world_state.sabotage.active:
        return game_map.visibility_defaults.base

    sabotage_definition = game_map.sabotages.get(world_state.sabotage.kind)
    if sabotage_definition is None:
        raise ValueError(f"unknown sabotage kind: {world_state.sabotage.kind}")
    return sabotage_definition.affected_visibility


def visible_rooms_for_player(
    *,
    observer: PlayerState,
    game_map: Map,
    mode: VisibilityMode,
) -> tuple[RoomId, ...]:
    """Compute observer-visible rooms using MVP simplifications.

    Phase-1 simplification rules:
      - ``same_room_only``: observer can only see their current room.
      - ``same_room_and_adjacent``: observer can see their room + directly
        adjacent rooms in the map graph.
    """

    if observer.room not in game_map.rooms:
        raise ValueError(f"observer is in unknown room: {observer.room}")

    if mode == "same_room_only":
        return (observer.room,)

    if mode == "same_room_and_adjacent":
        room_ids = {observer.room, *game_map.room_neighbors(observer.room)}
        return tuple(sorted(room_ids))

    raise ValueError(f"unsupported visibility mode: {mode}")


def _visible_player_ids(
    *,
    observer_id: PlayerId,
    players: Mapping[PlayerId, PlayerState],
    visible_rooms: tuple[RoomId, ...],
) -> tuple[PlayerId, ...]:
    visible_room_set = set(visible_rooms)
    return tuple(
        sorted(
            player_id
            for player_id, player in players.items()
            if player_id != observer_id
            and player.alive
            and player.room in visible_room_set
            and not player.in_vent
        )
    )


def _visible_body_ids(
    *,
    bodies: Mapping[BodyId, BodyState],
    visible_rooms: tuple[RoomId, ...],
) -> tuple[BodyId, ...]:
    visible_room_set = set(visible_rooms)
    return tuple(
        sorted(
            body_id
            for body_id, body in bodies.items()
            if body.discovered_by is None and body.room in visible_room_set
        )
    )


def compute_visibility_for_player(
    *,
    observer_id: PlayerId,
    world_state: WorldState,
    game_map: Map,
) -> VisibilityResult:
    """Compute visibility-constrained entity ids for one observer."""

    observer = world_state.players.get(observer_id)
    if observer is None:
        raise ValueError(f"unknown observer id: {observer_id}")
    if not observer.alive:
        return VisibilityResult(
            observer_id=observer_id,
            visible_rooms=(),
            visible_player_ids=(),
            visible_body_ids=(),
        )

    mode = resolve_visibility_mode(world_state, game_map)
    visible_rooms = visible_rooms_for_player(
        observer=observer, game_map=game_map, mode=mode
    )

    return VisibilityResult(
        observer_id=observer_id,
        visible_rooms=visible_rooms,
        visible_player_ids=_visible_player_ids(
            observer_id=observer_id,
            players=world_state.players,
            visible_rooms=visible_rooms,
        ),
        visible_body_ids=_visible_body_ids(
            bodies=world_state.bodies,
            visible_rooms=visible_rooms,
        ),
    )
