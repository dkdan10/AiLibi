"""Check event witnesses from ordered player state, independently of their lists."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from engine.events import (
    EngineEvent,
    KilledEvent,
    MovedEvent,
    SabotageStartedEvent,
    SabotageRepairedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.world import Map, WorldState


def assert_event_witnesses_match_source_state(
    *,
    pre_state: WorldState,
    state: WorldState,
    events: Sequence[EngineEvent],
    game_map: Map,
) -> None:
    """Reconstruct position/life/vent changes before each kill or vent event.

    Witnesses must be alive, outside a vent and in the relevant room when the
    action happens. Later movement or death cannot grant or erase that witness.
    This checks the same-room event contract, not the broader snapshot visibility
    contract. It neither imports the engine's witness helper nor trusts its lists.
    """
    players = dict(pre_state.players)
    mode = game_map.visibility_defaults.base
    if pre_state.sabotage is not None and pre_state.sabotage.active:
        mode = game_map.sabotages[pre_state.sabotage.kind].affected_visibility

    def in_room(room: str, excluded: set[str]) -> tuple[str, ...]:
        return tuple(
            sorted(
                pid
                for pid, player in players.items()
                if pid not in excluded
                and player.alive
                and not player.in_vent
                and player.room == room
            )
        )

    for event in events:
        if isinstance(event, MovedEvent):
            actor = players[event.actor]
            assert event.from_room == actor.room, "move source contradicts player state"
            assert (
                event.to_room == event.from_room
                or event.to_room in game_map.room_neighbors(event.from_room)
            ), "move destination contradicts map"
            expected_movement: list[str] = []
            for observer_id, observer in sorted(players.items()):
                if (
                    observer_id == event.actor
                    or not observer.alive
                    or not actor.alive
                    or actor.in_vent
                ):
                    continue
                visible = {observer.room}
                observer_mode = mode
                if (
                    mode == game_map.visibility_defaults.base
                    and observer.role != "IMPOSTOR"
                ):
                    observer_mode = "same_room_only"
                if observer_mode == "same_room_and_adjacent":
                    visible.update(game_map.room_neighbors(observer.room))
                if actor.room in visible:
                    expected_movement.append(observer_id)
            assert event.witnesses == tuple(expected_movement), (
                "movement witness entitlement"
            )
            players[event.actor] = replace(actor, room=event.to_room)
        elif isinstance(event, KilledEvent):
            actor, target = players[event.actor], players[event.target]
            assert actor.room == target.room == event.room, (
                "kill room contradicts player state"
            )
            expected = in_room(event.room, {event.actor, event.target})
            assert event.witnesses == expected, (
                f"kill witness entitlement: {event.witnesses} != {expected}"
            )
            players[event.target] = replace(target, alive=False)
        elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
            actor = players[event.actor]
            destination = game_map.vents[event.destination_vent_id].room
            assert actor.room == event.source_room, (
                "vent source contradicts player state"
            )
            assert destination == event.destination_room, (
                "vent destination contradicts map"
            )
            source = in_room(actor.room, {event.actor})
            arrival = in_room(destination, {event.actor})
            assert event.source_witnesses == source, "vent source witness entitlement"
            assert event.destination_witnesses == arrival, (
                "vent destination witness entitlement"
            )
            assert event.witnesses == tuple(sorted(set(source) | set(arrival))), (
                "vent combined witness entitlement"
            )
            players[event.actor] = replace(
                actor, room=destination, in_vent=isinstance(event, VentEnteredEvent)
            )
        elif isinstance(event, SabotageStartedEvent):
            mode = game_map.sabotages[event.kind].affected_visibility
        elif isinstance(event, SabotageRepairedEvent):
            mode = game_map.visibility_defaults.base

    expected_players = {
        pid: (player.room, player.alive, player.in_vent)
        for pid, player in players.items()
    }
    actual_players = {
        pid: (player.room, player.alive, player.in_vent)
        for pid, player in state.players.items()
    }
    assert actual_players == expected_players, (
        "player changes lack ordered event support"
    )
