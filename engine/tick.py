from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from engine.actions import (
    Action,
    DoTaskAction,
    EmergencyMeetingAction,
    KillAction,
    MoveAction,
    ReportBodyAction,
    SabotageAction,
    VentAction,
    WaitAction,
)
from engine.entities import PlayerId, PlayerState, SabotageState, TaskState
from engine.rng import EngineRng
from engine.rules import (
    ActionRejectedError,
    RuleEvent,
    resolve_emergency_meeting,
    resolve_kill,
    resolve_report,
    resolve_sabotage,
    resolve_vent,
    resolve_win_conditions,
)
from engine.world import Map, WorldState, load_canonical_map


EngineEvent = dict[str, Any]
_KILL_COOLDOWN_TICKS = 10


def _decrement_cooldowns(
    state: WorldState,
    *,
    skip_players: set[PlayerId],
) -> dict[PlayerId, int]:
    return {
        player_id: ticks if player_id in skip_players else max(0, ticks - 1)
        for player_id, ticks in state.cooldowns.items()
    }


def _advance_sabotage(sabotage: SabotageState | None) -> SabotageState | None:
    if sabotage is None or not sabotage.active:
        return sabotage
    return replace(sabotage, remaining_ticks=max(0, sabotage.remaining_ticks - 1))


def _advance_tasks(tasks: dict[str, TaskState]) -> dict[str, TaskState]:
    return tasks


def _load_state_map(state: WorldState) -> Map:
    game_map = load_canonical_map()
    if state.map != game_map.id:
        raise ValueError(f"unsupported map id for Phase 1 engine: {state.map}")
    return game_map


def _get_live_player(state: WorldState, player_id: PlayerId) -> PlayerState:
    player = state.players.get(player_id)
    if player is None:
        raise ActionRejectedError(f"unknown player: {player_id}")
    if not player.alive:
        raise ActionRejectedError(f"player is dead: {player_id}")
    return player


def _with_actor_last_action(
    state: WorldState, action: Action
) -> dict[PlayerId, PlayerState]:
    players = dict(state.players)
    actor = _get_live_player(state, action.actor)
    players[action.actor] = replace(actor, last_action=action)
    return players


def _event_from_rule(rule_event: RuleEvent, *, tick: int) -> EngineEvent:
    return {
        "type": rule_event.type,
        "tick": tick,
        "actor": rule_event.actor,
        "details": dict(rule_event.details),
    }


def _rejection_event(
    *,
    tick: int,
    action: Action,
    reason: str,
) -> EngineEvent:
    return {
        "type": "ActionRejected",
        "tick": tick,
        "actor": action.actor,
        "action": action.type,
        "reason": reason,
    }


def _apply_move(
    state: WorldState, game_map: Map, action: MoveAction
) -> tuple[WorldState, RuleEvent]:
    actor = _get_live_player(state, action.actor)
    if actor.in_vent:
        raise ActionRejectedError("cannot move while in vent")
    if actor.room not in game_map.rooms:
        raise ValueError(f"actor is in unknown room: {actor.room}")
    if action.payload.to_room not in game_map.rooms:
        raise ActionRejectedError(f"unknown destination room: {action.payload.to_room}")
    if (
        action.payload.to_room != actor.room
        and action.payload.to_room not in game_map.room_neighbors(actor.room)
    ):
        raise ActionRejectedError("move destination must be current or adjacent room")

    players = _with_actor_last_action(state, action)
    players[action.actor] = replace(
        players[action.actor],
        room=action.payload.to_room,
        in_vent=False,
    )
    event = RuleEvent(
        type="Moved",
        actor=action.actor,
        details={"from_room": actor.room, "to_room": action.payload.to_room},
    )
    return replace(state, players=players), event


def _apply_do_task(
    state: WorldState, action: DoTaskAction
) -> tuple[WorldState, RuleEvent]:
    actor = _get_live_player(state, action.actor)
    if actor.in_vent:
        raise ActionRejectedError("cannot do task while in vent")

    task = state.tasks.get(action.payload.task_id)
    if task is None:
        raise ActionRejectedError(f"unknown task id: {action.payload.task_id}")
    if task.owner != action.actor:
        raise ActionRejectedError("task is not owned by actor")
    if task.room != actor.room:
        raise ActionRejectedError("task requires actor in task room")
    if task.completed:
        raise ActionRejectedError("task already completed")
    if task.required_ticks < 1:
        raise ValueError(f"task has invalid required_ticks: {task.id}")

    next_progress = min(task.required_ticks, task.progress + 1)
    completed = next_progress >= task.required_ticks
    tasks = dict(state.tasks)
    tasks[task.id] = replace(task, progress=next_progress, completed=completed)
    players = _with_actor_last_action(state, action)
    event = RuleEvent(
        type="TaskCompleted" if completed else "TaskProgressed",
        actor=action.actor,
        details={
            "task_id": task.id,
            "progress": next_progress,
            "required_ticks": task.required_ticks,
        },
    )
    return replace(state, players=players, tasks=tasks), event


def _apply_kill(state: WorldState, action: KillAction) -> tuple[WorldState, RuleEvent]:
    body, event = resolve_kill(state, action)
    if body.id in state.bodies:
        raise ActionRejectedError(f"body id already exists: {body.id}")

    players = _with_actor_last_action(state, action)
    target = state.players[action.payload.target]
    players[action.payload.target] = replace(target, alive=False)
    bodies = dict(state.bodies)
    bodies[body.id] = body
    cooldowns = dict(state.cooldowns)
    cooldowns[action.actor] = _KILL_COOLDOWN_TICKS
    return replace(state, players=players, bodies=bodies, cooldowns=cooldowns), event


def _apply_vent(
    state: WorldState, game_map: Map, action: VentAction
) -> tuple[WorldState, RuleEvent]:
    event = resolve_vent(state, game_map, action)
    vent = game_map.vents[action.payload.vent_id]
    players = _with_actor_last_action(state, action)
    actor = players[action.actor]
    players[action.actor] = replace(actor, room=vent.room, in_vent=not actor.in_vent)
    return replace(state, players=players), event


def _apply_report(
    state: WorldState, action: ReportBodyAction
) -> tuple[WorldState, RuleEvent]:
    event = resolve_report(state, action)
    players = _with_actor_last_action(state, action)
    bodies = dict(state.bodies)
    body = bodies[action.payload.body_id]
    bodies[action.payload.body_id] = replace(body, discovered_by=action.actor)
    return replace(state, phase="MEETING", players=players, bodies=bodies), event


def _apply_emergency(
    state: WorldState,
    game_map: Map,
    action: EmergencyMeetingAction,
) -> tuple[WorldState, RuleEvent]:
    event = resolve_emergency_meeting(
        state,
        action,
        emergency_uses_per_player=game_map.emergency.uses_per_player,
        emergency_uses_by_player=state.emergency_uses,
    )
    players = _with_actor_last_action(state, action)
    emergency_uses = dict(state.emergency_uses)
    emergency_uses[action.actor] = emergency_uses.get(action.actor, 0) + 1
    return replace(
        state,
        phase="MEETING",
        players=players,
        emergency_uses=emergency_uses,
    ), event


def _apply_sabotage(
    state: WorldState,
    game_map: Map,
    action: SabotageAction,
) -> tuple[WorldState, RuleEvent]:
    event = resolve_sabotage(state, game_map, action)
    sabotage_definition = game_map.sabotages[action.payload.kind]
    sabotage = SabotageState(
        kind=action.payload.kind,
        remaining_ticks=sabotage_definition.duration_ticks,
        affected_rooms=sabotage_definition.repair_rooms,
        active=True,
    )
    players = _with_actor_last_action(state, action)
    return replace(state, players=players, sabotage=sabotage), event


def _apply_wait(state: WorldState, action: WaitAction) -> tuple[WorldState, RuleEvent]:
    _ = _get_live_player(state, action.actor)
    players = _with_actor_last_action(state, action)
    event = RuleEvent(type="Waited", actor=action.actor, details={})
    return replace(state, players=players), event


def _apply_action(
    state: WorldState, game_map: Map, action: Action
) -> tuple[WorldState, RuleEvent]:
    if state.phase != "PLAY":
        raise ActionRejectedError(f"cannot apply gameplay action during {state.phase}")
    if isinstance(action, MoveAction):
        return _apply_move(state, game_map, action)
    if isinstance(action, DoTaskAction):
        return _apply_do_task(state, action)
    if isinstance(action, KillAction):
        return _apply_kill(state, action)
    if isinstance(action, VentAction):
        return _apply_vent(state, game_map, action)
    if isinstance(action, ReportBodyAction):
        return _apply_report(state, action)
    if isinstance(action, EmergencyMeetingAction):
        return _apply_emergency(state, game_map, action)
    if isinstance(action, SabotageAction):
        return _apply_sabotage(state, game_map, action)
    if isinstance(action, WaitAction):
        return _apply_wait(state, action)
    raise TypeError(f"unsupported action type: {type(action).__name__}")


def advance_tick(
    state: WorldState, actions: Sequence[Action]
) -> tuple[WorldState, list[EngineEvent]]:
    """Advance one engine tick using the DESIGN.md §3.1 seven-step loop."""

    if state.phase != "PLAY":
        raise ValueError(f"cannot advance tick during {state.phase}")

    game_map = _load_state_map(state)
    events: list[EngineEvent] = []
    working_state = state
    cooldown_skip_players: set[PlayerId] = set()

    # 1) Apply queued actions from previous tick.
    for action in actions:
        try:
            working_state, rule_event = _apply_action(working_state, game_map, action)
            events.append(_event_from_rule(rule_event, tick=state.tick))
            if rule_event.type == "Killed":
                cooldown_skip_players.add(action.actor)
            if working_state.phase == "MEETING":
                return working_state, events
        except ActionRejectedError as exc:
            events.append(
                _rejection_event(tick=state.tick, action=action, reason=str(exc))
            )

    # 2) Resolve passive effects.
    cooldowns = _decrement_cooldowns(
        working_state,
        skip_players=cooldown_skip_players,
    )
    sabotage = _advance_sabotage(working_state.sabotage)
    tasks = _advance_tasks(dict(working_state.tasks))

    working_state = replace(
        working_state, cooldowns=cooldowns, sabotage=sabotage, tasks=tasks
    )

    # 3) Check victory.
    win_result = resolve_win_conditions(working_state)
    if win_result is not None:
        game_over_state = replace(working_state, phase="GAME_OVER")
        events.append(
            {
                "type": "GameOver",
                "tick": state.tick,
                "winner": win_result.winner,
                "reason": win_result.reason,
            }
        )
        return game_over_state, events

    # 4) Compute observations (owned by observation service; placeholder event).
    events.append({"type": "ObservationsComputed", "tick": state.tick})

    # 5) Solicit actions (owned by orchestrator/agents; placeholder event).
    events.append({"type": "ActionsSolicited", "tick": state.tick})

    # RNG state is explicitly threaded through the tick transition.
    rng = EngineRng.from_state(state.rng_state)
    _, next_rng_state = rng.randint(0, 2**31 - 1)

    next_state = replace(working_state, tick=state.tick + 1, rng_state=next_rng_state)

    # 6) Emit tick event.
    events.append({"type": "TickAdvanced", "tick": next_state.tick})

    # 7) Tick increment happens in next_state above.
    return next_state, events
