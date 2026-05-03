from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Literal

from engine.actions import (
    Action,
    DoTaskAction,
    EmergencyMeetingAction,
    KillAction,
    MoveAction,
    RepairSabotageAction,
    ReportBodyAction,
    SabotageAction,
    VentAction,
    WaitAction,
)
from engine.entities import PlayerId, PlayerState, RoomId, SabotageState, TaskState
from engine.events import (
    ActionRejectedEvent,
    EngineEvent,
    GameOverEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    MovedEvent,
    SabotageRepairedEvent,
    SabotageRepairProgressedEvent,
    SabotageStartedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
    TickAdvancedEvent,
    VentEnteredEvent,
    VentExitedEvent,
    WaitedEvent,
)
from engine.rng import EngineRng
from engine.rules import (
    ActionRejectedError,
    RuleEvent,
    resolve_emergency_meeting,
    resolve_kill,
    resolve_repair_sabotage,
    resolve_report,
    resolve_sabotage,
    resolve_vent,
    resolve_win_conditions,
)
from engine.world import Map, WorldState

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


def _task_progress_event(*, actor: PlayerId, task: TaskState) -> RuleEvent:
    return RuleEvent(
        type="TaskCompleted" if task.completed else "TaskProgressed",
        actor=actor,
        details={
            "task_id": task.id,
            "progress": task.progress,
            "required_ticks": task.required_ticks,
        },
    )


def _advance_tasks(
    state: WorldState,
    *,
    submitted_actors: set[PlayerId],
) -> tuple[dict[str, TaskState], list[RuleEvent]]:
    tasks = dict(state.tasks)
    events: list[RuleEvent] = []

    for player_id in sorted(state.players):
        if player_id in submitted_actors:
            continue

        player = state.players[player_id]
        last_action = player.last_action
        if not isinstance(last_action, DoTaskAction):
            continue

        task_id = last_action.payload.task_id
        task = tasks.get(task_id)
        if task is None:
            raise ValueError(f"continuing task references unknown task id: {task_id}")
        if task.id != task_id:
            raise ValueError(f"task id mismatch for task mapping key: {task_id}")
        if task.owner != player_id:
            raise ValueError(f"continuing task is not owned by actor: {task_id}")
        if task.required_ticks < 1:
            raise ValueError(f"task has invalid required_ticks: {task.id}")

        if (
            task.completed
            or not player.alive
            or player.in_vent
            or player.room != task.room
        ):
            continue

        next_progress = min(task.required_ticks, task.progress + 1)
        next_task = replace(
            task,
            progress=next_progress,
            completed=next_progress >= task.required_ticks,
        )
        tasks[task.id] = next_task
        events.append(_task_progress_event(actor=player_id, task=next_task))

    return tasks, events


def _validate_state_map(state: WorldState, game_map: Map) -> None:
    if state.map != game_map.id:
        raise ValueError(f"unsupported map id for Phase 1 engine: {state.map}")


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


def _event_detail_string(rule_event: RuleEvent, key: str) -> str:
    value = rule_event.details.get(key)
    if not isinstance(value, str):
        raise ValueError(f"{rule_event.type} event {key} must be a string")
    return value


def _event_detail_int(rule_event: RuleEvent, key: str) -> int:
    value = rule_event.details.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{rule_event.type} event {key} must be an int")
    return value


def _event_detail_string_tuple(rule_event: RuleEvent, key: str) -> tuple[str, ...]:
    value = rule_event.details.get(key)
    if not isinstance(value, tuple):
        raise ValueError(f"{rule_event.type} event {key} must be a tuple")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{rule_event.type} event {key} must contain strings")
    return value


def _event_from_rule(rule_event: RuleEvent, *, tick: int) -> EngineEvent:
    if rule_event.type == "Moved":
        return MovedEvent(
            type="Moved",
            tick=tick,
            actor=rule_event.actor,
            from_room=_event_detail_string(rule_event, "from_room"),
            to_room=_event_detail_string(rule_event, "to_room"),
        )
    if rule_event.type == "TaskProgressed":
        return TaskProgressedEvent(
            type="TaskProgressed",
            tick=tick,
            actor=rule_event.actor,
            task_id=_event_detail_string(rule_event, "task_id"),
            progress=_event_detail_int(rule_event, "progress"),
            required_ticks=_event_detail_int(rule_event, "required_ticks"),
        )
    if rule_event.type == "TaskCompleted":
        return TaskCompletedEvent(
            type="TaskCompleted",
            tick=tick,
            actor=rule_event.actor,
            task_id=_event_detail_string(rule_event, "task_id"),
            progress=_event_detail_int(rule_event, "progress"),
            required_ticks=_event_detail_int(rule_event, "required_ticks"),
        )
    if rule_event.type == "Killed":
        return KilledEvent(
            type="Killed",
            tick=tick,
            actor=rule_event.actor,
            target=_event_detail_string(rule_event, "target"),
            room=_event_detail_string(rule_event, "room"),
            witnesses=_event_detail_string_tuple(rule_event, "witnesses"),
        )
    if rule_event.type in {"VentEntered", "VentExited"}:
        vent_id = _event_detail_string(rule_event, "vent_id")
        room = _event_detail_string(rule_event, "room")
        source_vent_id = _event_detail_string(rule_event, "source_vent_id")
        destination_vent_id = _event_detail_string(rule_event, "destination_vent_id")
        source_room = _event_detail_string(rule_event, "source_room")
        destination_room = _event_detail_string(rule_event, "destination_room")
        traversal_ticks = _event_detail_int(rule_event, "traversal_ticks")
        witnesses = _event_detail_string_tuple(rule_event, "witnesses")
        source_witnesses = _event_detail_string_tuple(rule_event, "source_witnesses")
        destination_witnesses = _event_detail_string_tuple(
            rule_event, "destination_witnesses"
        )
        if rule_event.type == "VentEntered":
            return VentEnteredEvent(
                type="VentEntered",
                tick=tick,
                actor=rule_event.actor,
                vent_id=vent_id,
                room=room,
                source_vent_id=source_vent_id,
                destination_vent_id=destination_vent_id,
                source_room=source_room,
                destination_room=destination_room,
                traversal_ticks=traversal_ticks,
                witnesses=witnesses,
                source_witnesses=source_witnesses,
                destination_witnesses=destination_witnesses,
            )
        return VentExitedEvent(
            type="VentExited",
            tick=tick,
            actor=rule_event.actor,
            vent_id=vent_id,
            room=room,
            source_vent_id=source_vent_id,
            destination_vent_id=destination_vent_id,
            source_room=source_room,
            destination_room=destination_room,
            traversal_ticks=traversal_ticks,
            witnesses=witnesses,
            source_witnesses=source_witnesses,
            destination_witnesses=destination_witnesses,
        )
    if rule_event.type == "SabotageStarted":
        return SabotageStartedEvent(
            type="SabotageStarted",
            tick=tick,
            actor=rule_event.actor,
            kind=_event_detail_string(rule_event, "kind"),
            duration_ticks=_event_detail_int(rule_event, "duration_ticks"),
            affected_rooms=_event_detail_string_tuple(rule_event, "affected_rooms"),
        )
    if rule_event.type == "MeetingTriggered":
        raw_trigger = _event_detail_string(rule_event, "trigger")
        trigger: Literal["report", "emergency"]
        if raw_trigger == "report":
            trigger = "report"
        elif raw_trigger == "emergency":
            trigger = "emergency"
        else:
            raise ValueError(f"unsupported meeting trigger: {raw_trigger}")
        body_id = rule_event.details.get("body_id")
        if body_id is not None and not isinstance(body_id, str):
            raise ValueError("MeetingTriggered event body_id must be a string")
        return MeetingTriggeredEvent(
            type="MeetingTriggered",
            tick=tick,
            actor=rule_event.actor,
            trigger=trigger,
            body_id=body_id,
        )
    if rule_event.type == "Waited":
        return WaitedEvent(type="Waited", tick=tick, actor=rule_event.actor)
    raise ValueError(f"unsupported rule event type: {rule_event.type}")


def _rejection_event(
    *,
    tick: int,
    action: Action,
    reason: str,
) -> EngineEvent:
    return ActionRejectedEvent(
        type="ActionRejected",
        tick=tick,
        actor=action.actor,
        action=action.type,
        reason=reason,
    )


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
    event = _task_progress_event(
        actor=action.actor,
        task=tasks[task.id],
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
        emergency_button_room=game_map.emergency.button_room,
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


def _repair_progress_event(
    *,
    action: RepairSabotageAction,
    kind: str,
    room: RoomId,
    progress: int,
    required_ticks: int,
    tick: int,
    completed: bool,
) -> EngineEvent:
    if completed:
        return SabotageRepairedEvent(
            type="SabotageRepaired",
            tick=tick,
            actor=action.actor,
            kind=kind,
            room=room,
            progress=progress,
            required_ticks=required_ticks,
        )
    return SabotageRepairProgressedEvent(
        type="SabotageRepairProgressed",
        tick=tick,
        actor=action.actor,
        kind=kind,
        room=room,
        progress=progress,
        required_ticks=required_ticks,
    )


def _apply_repair_sabotage(
    state: WorldState,
    game_map: Map,
    action: RepairSabotageAction,
) -> tuple[WorldState, EngineEvent]:
    validation_event = resolve_repair_sabotage(state, game_map, action)
    kind = _event_detail_string(validation_event, "kind")
    room = _event_detail_string(validation_event, "room")
    sabotage = state.sabotage
    if sabotage is None:
        raise ValueError("repair validation passed without active sabotage")

    sabotage_definition = game_map.sabotages[kind]
    prior_progress = sabotage.repair_progress.get(room, 0)
    progress = min(sabotage_definition.repair_ticks, prior_progress + 1)
    completed = progress >= sabotage_definition.repair_ticks
    repair_progress = dict(sabotage.repair_progress)
    repair_progress[room] = progress
    next_sabotage = replace(
        sabotage,
        active=not completed,
        repair_progress=repair_progress,
    )
    players = _with_actor_last_action(state, action)
    event = _repair_progress_event(
        action=action,
        kind=kind,
        room=room,
        progress=progress,
        required_ticks=sabotage_definition.repair_ticks,
        tick=state.tick,
        completed=completed,
    )
    return replace(state, players=players, sabotage=next_sabotage), event


def _apply_wait(state: WorldState, action: WaitAction) -> tuple[WorldState, RuleEvent]:
    _ = _get_live_player(state, action.actor)
    players = _with_actor_last_action(state, action)
    event = RuleEvent(type="Waited", actor=action.actor, details={})
    return replace(state, players=players), event


def _apply_action(
    state: WorldState, game_map: Map, action: Action
) -> tuple[WorldState, RuleEvent | EngineEvent]:
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
    if isinstance(action, RepairSabotageAction):
        return _apply_repair_sabotage(state, game_map, action)
    if isinstance(action, WaitAction):
        return _apply_wait(state, action)
    raise TypeError(f"unsupported action type: {type(action).__name__}")


def advance_tick(
    state: WorldState, actions: Sequence[Action], *, game_map: Map
) -> tuple[WorldState, list[EngineEvent]]:
    """Advance one engine tick using the DESIGN.md §3.1 seven-step loop."""

    if state.phase != "PLAY":
        raise ValueError(f"cannot advance tick during {state.phase}")

    _validate_state_map(state, game_map)
    events: list[EngineEvent] = []
    working_state = state
    cooldown_skip_players: set[PlayerId] = set()
    submitted_actors = {action.actor for action in actions}

    # 1) Apply queued actions from previous tick.
    for action in actions:
        try:
            working_state, resolved_event = _apply_action(
                working_state, game_map, action
            )
            event = (
                _event_from_rule(resolved_event, tick=state.tick)
                if isinstance(resolved_event, RuleEvent)
                else resolved_event
            )
            events.append(event)
            if event.type == "Killed":
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
    tasks, task_events = _advance_tasks(
        working_state,
        submitted_actors=submitted_actors,
    )

    working_state = replace(
        working_state, cooldowns=cooldowns, sabotage=sabotage, tasks=tasks
    )
    events.extend(_event_from_rule(event, tick=state.tick) for event in task_events)

    # 3) Check victory.
    win_result = resolve_win_conditions(working_state)
    if win_result is not None:
        game_over_state = replace(working_state, phase="GAME_OVER")
        events.append(
            GameOverEvent(
                type="GameOver",
                tick=state.tick,
                winner=win_result.winner,
                reason=win_result.reason,
            )
        )
        return game_over_state, events

    # RNG state is explicitly threaded through the tick transition.
    rng = EngineRng.from_state(state.rng_state)
    _, next_rng_state = rng.randint(0, 2**31 - 1)

    next_state = replace(working_state, tick=state.tick + 1, rng_state=next_rng_state)

    # 4/5 are orchestrator responsibilities: observations and action solicitation.
    # 6) Emit tick event.
    events.append(TickAdvancedEvent(type="TickAdvanced", tick=next_state.tick))

    # 7) Tick increment happens in next_state above.
    return next_state, events
