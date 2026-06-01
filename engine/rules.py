from __future__ import annotations

from collections.abc import Mapping

from engine.actions import (
    EmergencyMeetingAction,
    KillAction,
    RepairSabotageAction,
    ReportBodyAction,
    SabotageAction,
    VentAction,
)
from engine.entities import BodyState, PlayerId, PlayerState, RoomId
from engine.events import (
    KilledEvent,
    MeetingTriggeredEvent,
    SabotageStartedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.win_conditions import WinResult, evaluate_win_conditions
from engine.world import Map, WorldState


class ActionRejectedError(ValueError):
    """Raised when an action violates engine rules."""


def _witnesses_in_room(
    state: WorldState,
    *,
    room: str,
    exclude: set[PlayerId],
) -> tuple[PlayerId, ...]:
    return tuple(
        sorted(
            player_id
            for player_id, player in state.players.items()
            if player_id not in exclude
            and player.alive
            and not player.in_vent
            and player.room == room
        )
    )


def _get_live_player(state: WorldState, player_id: PlayerId) -> PlayerState:
    player = state.players.get(player_id)
    if player is None:
        raise ActionRejectedError(f"unknown player: {player_id}")
    if not player.alive:
        raise ActionRejectedError(f"player is dead: {player_id}")
    return player


def resolve_kill(
    state: WorldState, action: KillAction
) -> tuple[BodyState, KilledEvent]:
    actor = _get_live_player(state, action.actor)
    target = _get_live_player(state, action.payload.target)

    if actor.role != "IMPOSTOR":
        raise ActionRejectedError("only impostors can kill")
    # Friendly-fire guard (DESIGN.md §3.4; Phase 7 Wave 0.5): the target must be
    # a CREWMATE — a fellow impostor is never a valid kill target. This is
    # defense-in-depth: the impostor tactical policy already excludes teammates
    # from target selection (agents/tactical/impostor_policy.py), but a buggy or
    # future LLM-driven policy must not be able to self-sabotage the impostor
    # team. The actor-is-impostor, cooldown, and same-room checks below are
    # unchanged.
    if target.role == "IMPOSTOR":
        raise ActionRejectedError("kill target must be a crewmate")
    if state.cooldowns.get(action.actor, 0) != 0:
        raise ActionRejectedError("kill is on cooldown")
    if actor.room != target.room:
        raise ActionRejectedError("kill requires same room")

    body_id = f"body-{target.id}-{state.tick}"
    body = BodyState(
        id=body_id,
        player_id=target.id,
        room=target.room,
        position=target.position,
        killed_by=actor.id,
        discovered_by=None,
    )
    event = KilledEvent(
        type="Killed",
        tick=state.tick,
        actor=action.actor,
        target=target.id,
        room=target.room,
        witnesses=_witnesses_in_room(
            state,
            room=target.room,
            exclude={actor.id, target.id},
        ),
    )
    return body, event


def resolve_vent(
    state: WorldState, game_map: Map, action: VentAction
) -> VentEnteredEvent | VentExitedEvent:
    actor = _get_live_player(state, action.actor)
    if actor.role != "IMPOSTOR":
        raise ActionRejectedError("only impostors can vent")

    destination_vent = game_map.vents.get(action.payload.vent_id)
    if destination_vent is None:
        raise ActionRejectedError(f"unknown vent id: {action.payload.vent_id}")

    is_exit: bool
    source_vent_id: str
    source_room: RoomId
    if actor.in_vent:
        current_vent = game_map.vent_for_room(actor.room)
        if current_vent is None:
            raise ValueError(f"actor is in a ventless room while in vent: {actor.room}")
        if (
            destination_vent.id != current_vent.id
            and destination_vent.id not in current_vent.connects_to
        ):
            raise ActionRejectedError(
                "destination vent must be current or connected vent"
            )
        is_exit = True
        source_vent_id = current_vent.id
        source_room = current_vent.room
    else:
        if destination_vent.room != actor.room:
            raise ActionRejectedError("cannot enter vent from another room")
        is_exit = False
        source_vent_id = destination_vent.id
        source_room = actor.room

    source_witnesses = _witnesses_in_room(
        state,
        room=source_room,
        exclude={actor.id},
    )
    destination_witnesses = _witnesses_in_room(
        state,
        room=destination_vent.room,
        exclude={actor.id},
    )
    witnesses = tuple(sorted(set(source_witnesses) | set(destination_witnesses)))

    if is_exit:
        return VentExitedEvent(
            type="VentExited",
            tick=state.tick,
            actor=action.actor,
            vent_id=destination_vent.id,
            room=destination_vent.room,
            source_vent_id=source_vent_id,
            destination_vent_id=destination_vent.id,
            source_room=source_room,
            destination_room=destination_vent.room,
            traversal_ticks=destination_vent.traversal_ticks,
            witnesses=witnesses,
            source_witnesses=source_witnesses,
            destination_witnesses=destination_witnesses,
        )
    return VentEnteredEvent(
        type="VentEntered",
        tick=state.tick,
        actor=action.actor,
        vent_id=destination_vent.id,
        room=destination_vent.room,
        source_vent_id=source_vent_id,
        destination_vent_id=destination_vent.id,
        source_room=source_room,
        destination_room=destination_vent.room,
        traversal_ticks=destination_vent.traversal_ticks,
        witnesses=witnesses,
        source_witnesses=source_witnesses,
        destination_witnesses=destination_witnesses,
    )


def resolve_report(
    state: WorldState, action: ReportBodyAction
) -> MeetingTriggeredEvent:
    actor = _get_live_player(state, action.actor)
    body = state.bodies.get(action.payload.body_id)
    if body is None:
        raise ActionRejectedError(f"unknown body id: {action.payload.body_id}")
    if body.room != actor.room:
        raise ActionRejectedError("report requires actor and body in same room")
    return MeetingTriggeredEvent(
        type="MeetingTriggered",
        tick=state.tick,
        actor=action.actor,
        trigger="report",
        body_id=body.id,
    )


def resolve_emergency_meeting(
    state: WorldState,
    action: EmergencyMeetingAction,
    *,
    emergency_button_room: RoomId,
    emergency_uses_per_player: int,
    emergency_uses_by_player: Mapping[PlayerId, int],
) -> MeetingTriggeredEvent:
    actor = _get_live_player(state, action.actor)
    if actor.in_vent:
        raise ActionRejectedError("cannot call emergency meeting while in vent")
    used = emergency_uses_by_player.get(action.actor, 0)
    if used >= emergency_uses_per_player:
        raise ActionRejectedError("emergency meeting use limit exceeded")
    if actor.room != emergency_button_room:
        raise ActionRejectedError("emergency meeting requires emergency button room")
    return MeetingTriggeredEvent(
        type="MeetingTriggered",
        tick=state.tick,
        actor=action.actor,
        trigger="emergency",
        body_id=None,
    )


def resolve_sabotage(
    state: WorldState, game_map: Map, action: SabotageAction
) -> SabotageStartedEvent:
    actor = _get_live_player(state, action.actor)
    if actor.role != "IMPOSTOR":
        raise ActionRejectedError("only impostors can sabotage")
    if state.sabotage is not None and state.sabotage.active:
        raise ActionRejectedError("sabotage already active")

    sabotage_def = game_map.sabotages.get(action.payload.kind)
    if sabotage_def is None:
        raise ActionRejectedError(f"unknown sabotage kind: {action.payload.kind}")

    return SabotageStartedEvent(
        type="SabotageStarted",
        tick=state.tick,
        actor=action.actor,
        kind=action.payload.kind,
        duration_ticks=sabotage_def.duration_ticks,
        affected_rooms=sabotage_def.repair_rooms,
    )


def resolve_repair_sabotage(
    state: WorldState, game_map: Map, action: RepairSabotageAction
) -> None:
    """Validate a repair-sabotage action; raise if invalid."""

    actor = _get_live_player(state, action.actor)
    if actor.in_vent:
        raise ActionRejectedError("cannot repair sabotage while in vent")

    sabotage_def = game_map.sabotages.get(action.payload.kind)
    if sabotage_def is None:
        raise ActionRejectedError(f"unknown sabotage kind: {action.payload.kind}")
    if state.sabotage is None or not state.sabotage.active:
        raise ActionRejectedError("no active sabotage to repair")
    if state.sabotage.kind != action.payload.kind:
        raise ActionRejectedError("active sabotage kind does not match repair action")
    if actor.room not in sabotage_def.repair_rooms:
        raise ActionRejectedError("repair requires actor in a sabotage repair room")


def resolve_win_conditions(state: WorldState) -> WinResult | None:
    return evaluate_win_conditions(state)
