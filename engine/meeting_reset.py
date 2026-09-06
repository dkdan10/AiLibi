"""Pure, explicitly selected regrouping for the meeting-reset comparison."""

from __future__ import annotations

from dataclasses import replace

from engine.world import Map, WorldState


def regroup_after_meeting(state: WorldState, *, game_map: Map) -> WorldState:
    """Gather survivors, clear vent occupancy/corpses, and restart kill grace.

    Call only after resolving the vote and checking victory. Task progress,
    sabotage state and emergency uses survive; ongoing player actions stop.
    The caller advances the meeting tick and RNG exactly once as usual.
    """

    if state.phase != "MEETING":
        raise ValueError("meeting regrouping requires the unresolved meeting phase")
    positions = {
        pid: (float(index), 0.0)
        for index, pid in enumerate(
            sorted(pid for pid, player in state.players.items() if player.alive)
        )
    }
    players = {
        pid: replace(
            player,
            room=game_map.meeting.room if player.alive else player.room,
            position=positions[pid] if player.alive else player.position,
            in_vent=False,
            last_action=None,
        )
        for pid, player in state.players.items()
    }
    cooldowns = {
        pid: game_map.kill_cooldown_ticks
        for pid, player in players.items()
        if player.alive and player.role == "IMPOSTOR"
    }
    return replace(state, players=players, cooldowns=cooldowns, bodies={})
