from __future__ import annotations

from dataclasses import dataclass
from math import dist

from engine.actions import (
    EmergencyMeetingAction,
    KillAction,
    ReportBodyAction,
    SabotageAction,
    VentAction,
)
from engine.entities import BodyState, PlayerId, PlayerState
from engine.win_conditions import WinResult, evaluate_win_conditions
from engine.world import Map, WorldState


class ActionRejectedError(ValueError):
    """Raised when an action violates engine rules."""


@dataclass(frozen=True)
class RuleEvent:
    type: str
    actor: PlayerId
    details: dict[str, str | int | float | tuple[str, ...]]


_KILL_RADIUS = 2.0


def _get_live_player(state: WorldState, player_id: PlayerId) -> PlayerState:
    player = state.players.get(player_id)
    if player is None:
        raise ActionRejectedError(f"unknown player: {player_id}")
    if not player.alive:
        raise ActionRejectedError(f"player is dead: {player_id}")
    return player


def resolve_kill(state: WorldState, action: KillAction) -> tuple[BodyState, RuleEvent]:
    actor = _get_live_player(state, action.actor)
    target = _get_live_player(state, action.payload.target)

    if actor.role != "IMPOSTOR":
        raise ActionRejectedError("only impostors can kill")
    if state.cooldowns.get(action.actor, 0) != 0:
        raise ActionRejectedError("kill is on cooldown")
    if actor.room != target.room:
        raise ActionRejectedError("kill requires same room")
    if dist(actor.position, target.position) > _KILL_RADIUS:
        raise ActionRejectedError("target outside kill radius")

    body_id = f"body-{target.id}-{state.tick}"
    body = BodyState(
        id=body_id,
        player_id=target.id,
        room=target.room,
        position=target.position,
        killed_by=actor.id,
        discovered_by=None,
    )
    return body, RuleEvent(
        type="Killed",
        actor=action.actor,
        details={"target": target.id, "room": target.room},
    )


def resolve_vent(state: WorldState, game_map: Map, action: VentAction) -> RuleEvent:
    actor = _get_live_player(state, action.actor)
    if actor.role != "IMPOSTOR":
        raise ActionRejectedError("only impostors can vent")

    vent = game_map.vents.get(action.payload.vent_id)
    if vent is None:
        raise ActionRejectedError(f"unknown vent id: {action.payload.vent_id}")

    if actor.in_vent:
        if vent.room != actor.room:
            raise ActionRejectedError("cannot exit to vent in different room")
        event_type = "VentExited"
    else:
        if vent.room != actor.room:
            raise ActionRejectedError("cannot enter vent from another room")
        event_type = "VentEntered"

    return RuleEvent(
        type=event_type,
        actor=action.actor,
        details={"vent_id": vent.id, "room": vent.room, "traversal_ticks": vent.traversal_ticks},
    )


def resolve_report(state: WorldState, action: ReportBodyAction) -> RuleEvent:
    actor = _get_live_player(state, action.actor)
    body = state.bodies.get(action.payload.body_id)
    if body is None:
        raise ActionRejectedError(f"unknown body id: {action.payload.body_id}")
    if body.room != actor.room:
        raise ActionRejectedError("report requires actor and body in same room")
    return RuleEvent(type="MeetingTriggered", actor=action.actor, details={"trigger": "report", "body_id": body.id})


def resolve_emergency_meeting(
    state: WorldState,
    action: EmergencyMeetingAction,
    *,
    emergency_uses_per_player: int,
    emergency_uses_by_player: dict[PlayerId, int],
) -> RuleEvent:
    _ = _get_live_player(state, action.actor)
    used = emergency_uses_by_player.get(action.actor, 0)
    if used >= emergency_uses_per_player:
        raise ActionRejectedError("emergency meeting use limit exceeded")
    return RuleEvent(type="MeetingTriggered", actor=action.actor, details={"trigger": "emergency"})


def resolve_sabotage(state: WorldState, game_map: Map, action: SabotageAction) -> RuleEvent:
    actor = _get_live_player(state, action.actor)
    if actor.role != "IMPOSTOR":
        raise ActionRejectedError("only impostors can sabotage")
    if state.sabotage is not None and state.sabotage.active:
        raise ActionRejectedError("sabotage already active")

    sabotage_def = game_map.sabotages.get(action.payload.kind)
    if sabotage_def is None:
        raise ActionRejectedError(f"unknown sabotage kind: {action.payload.kind}")

    return RuleEvent(
        type="SabotageStarted",
        actor=action.actor,
        details={
            "kind": action.payload.kind,
            "duration_ticks": sabotage_def.duration_ticks,
            "affected_rooms": sabotage_def.repair_rooms,
        },
    )


def resolve_win_conditions(state: WorldState) -> WinResult | None:
    return evaluate_win_conditions(state)
