"""Check event witnesses from ordered player state, independently of their lists."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from engine.events import (
    EngineEvent,
    KilledEvent,
    MovedEvent,
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
