from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Literal, TypeAlias

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
from engine.entities import (
    PlayerId,
    PlayerState,
    SabotageState,
    TaskId,
    TaskInstanceId,
    TaskState,
)
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
from engine.rng import EngineRng, RngStateHashPolicy
from engine.rules import (
    ActionRejectedError,
    resolve_emergency_meeting,
    resolve_kill,
    resolve_repair_sabotage,
    resolve_report,
    resolve_sabotage,
    resolve_vent,
    resolve_win_conditions,
)
from engine.world import Map, WorldState
from engine.visibility import compute_visibility_for_player

RedistributionPolicy: TypeAlias = Literal["lowest_id", "least_remaining_work"]


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


def _tasks_gated(state: WorldState, game_map: Map) -> bool:
    """Whether an active sabotage HALTS the crew task race (DESIGN.md §3.1, §8.3).

    The single source of truth for both task paths (``_apply_do_task`` initiation
    and ``_advance_tasks`` continuation) so they cannot drift. Gating is read from
    the map's ``SabotageDefinition.gates_tasks`` flag, NOT by string-matching the
    sabotage ``kind`` (the codebase deliberately avoids kind string-matching). A
    non-gating sabotage (e.g. ``lights``) leaves the task race byte-identical.
    """

    sabotage = state.sabotage
    return (
        sabotage is not None
        and sabotage.active
        and game_map.sabotages[sabotage.kind].gates_tasks
    )


def _task_progress_event(
    *, tick: int, actor: PlayerId, task: TaskState
) -> TaskProgressedEvent | TaskCompletedEvent:
    # The event carries the MAP task id (DESIGN.md §3.2; impact-map §5 decision 3),
    # not the composite instance id: the owner is disambiguated by ``actor``, and
    # downstream consumers resolve the room via ``game_map.tasks[task_id]``.
    if task.completed:
        return TaskCompletedEvent(
            type="TaskCompleted",
            tick=tick,
            actor=actor,
            task_id=task.map_task_id,
            progress=task.progress,
            required_ticks=task.required_ticks,
        )
    return TaskProgressedEvent(
        type="TaskProgressed",
        tick=tick,
        actor=actor,
        task_id=task.map_task_id,
        progress=task.progress,
        required_ticks=task.required_ticks,
    )


def _resolve_owned_task_instance(
    tasks: Mapping[TaskInstanceId, TaskState],
    *,
    actor: PlayerId,
    map_task_id: TaskId,
) -> TaskState | None:
    """Resolve the actor's own instance of ``map_task_id`` (DESIGN.md §3.2).

    Per-player tasks key ``WorldState.tasks`` by the composite instance id
    ``"{owner}:{map_task_id}"`` while the agent-facing id stays the MAP id, so
    the engine resolves ``(actor, map_task_id)`` to the single instance the actor
    owns for that map task — never another owner's instance of the same map task
    (the progress-isolation guarantee). Returns ``None`` when the actor holds no
    such instance (a foreign / out-of-pool / unowned map id), which callers turn
    into a loud rejection. Each ``(owner, map_task_id)`` pair is unique, so at
    most one instance matches.
    """

    for task in tasks.values():
        if task.owner == actor and task.map_task_id == map_task_id:
            return task
    return None


def _advance_tasks(
    state: WorldState,
    game_map: Map,
    *,
    tick: int,
    submitted_actors: set[PlayerId],
) -> tuple[dict[str, TaskState], list[TaskProgressedEvent | TaskCompletedEvent]]:
    tasks = dict(state.tasks)
    events: list[TaskProgressedEvent | TaskCompletedEvent] = []

    # A gating sabotage halts the task race: skip every continuation increment so
    # no progress accrues and no ``TaskProgressed`` event is emitted while active
    # (DESIGN.md §3.1, §8.3). Mirrors the ``_apply_do_task`` initiation gate.
    if _tasks_gated(state, game_map):
        return tasks, events

    for player_id in sorted(state.players):
        if player_id in submitted_actors:
            continue

        player = state.players[player_id]
        last_action = player.last_action
        if not isinstance(last_action, DoTaskAction):
            continue

        # The payload carries the MAP task id; resolve it to this actor's own
        # per-player instance (DESIGN.md §3.2). A continuing task was accepted on
        # an earlier tick, so the instance must still exist — a miss is a bug.
        map_task_id = last_action.payload.task_id
        task = _resolve_owned_task_instance(
            tasks, actor=player_id, map_task_id=map_task_id
        )
        if task is None:
            raise ValueError(
                "continuing task references no owned instance: "
                f"actor={player_id} map_task_id={map_task_id}"
            )
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
        events.append(_task_progress_event(tick=tick, actor=player_id, task=next_task))

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


def _rejection_event(
    *,
    tick: int,
    action: Action,
    reason: str,
) -> ActionRejectedEvent:
    return ActionRejectedEvent(
        type="ActionRejected",
        tick=tick,
        actor=action.actor,
        action=action.type,
        reason=reason,
    )


def _apply_move(
    state: WorldState, game_map: Map, action: MoveAction
) -> tuple[WorldState, MovedEvent]:
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
    event = MovedEvent(
        type="Moved",
        tick=state.tick,
        actor=action.actor,
        from_room=actor.room,
        to_room=action.payload.to_room,
        witnesses=tuple(
            observer_id
            for observer_id in sorted(state.players)
            if observer_id != action.actor
            and action.actor
            in compute_visibility_for_player(
                observer_id=observer_id, world_state=state, game_map=game_map
            ).visible_player_ids
        ),
    )
    return replace(state, players=players), event


def _apply_do_task(
    state: WorldState, game_map: Map, action: DoTaskAction
) -> tuple[WorldState, TaskProgressedEvent | TaskCompletedEvent]:
    # A gating sabotage halts the task race: reject task initiation while active
    # (DESIGN.md §3.1, §8.3). Mirrors the ``_advance_tasks`` continuation gate so
    # the two paths cannot drift (``_tasks_gated`` is the single source of truth).
    if _tasks_gated(state, game_map):
        raise ActionRejectedError("cannot do task while a sabotage gates tasks")
    actor = _get_live_player(state, action.actor)
    if actor.in_vent:
        raise ActionRejectedError("cannot do task while in vent")

    # The agent submits the MAP task id; resolve it to this actor's own per-player
    # instance (DESIGN.md §3.2). A foreign / out-of-pool / unowned map id resolves
    # to nothing and fails loud — the actor can only advance its own instance.
    map_task_id = action.payload.task_id
    task = _resolve_owned_task_instance(
        state.tasks, actor=action.actor, map_task_id=map_task_id
    )
    if task is None:
        raise ActionRejectedError(
            f"actor owns no task instance for map task: {map_task_id}"
        )
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
        tick=state.tick,
        actor=action.actor,
        task=tasks[task.id],
    )
    return replace(state, players=players, tasks=tasks), event


def redistribute_dead_tasks(
    *,
    surviving_tasks: dict[TaskInstanceId, TaskState],
    pre_death_tasks: Mapping[TaskInstanceId, TaskState],
    players: Mapping[PlayerId, PlayerState],
    victim: PlayerId,
    redistribution_policy: RedistributionPolicy = "lowest_id",
) -> dict[TaskInstanceId, TaskState]:
    """Re-key a dead crewmate's incomplete task instances onto living crewmates.

    Carry progress, room and required duration; change only instance ID and
    owner. The default chooses the lowest-ID eligible living crewmate. The
    explicit workload comparison chooses least remaining task work, breaking
    ties by ID and recomputing after each allocation. Completed or incomplete
    ownership of the same map task excludes a recipient under either policy;
    the instance is dropped only when no eligible living crewmate remains.

    Roles are engine-only eligibility facts. Recipients learn their new task
    through the existing owner-filtered observation, without death attribution.
    Both policies are deterministic and consume no RNG draws.
    """
    if redistribution_policy not in ("lowest_id", "least_remaining_work"):
        raise ValueError(f"unknown redistribution policy: {redistribution_policy!r}")
    living_crew = sorted(
        pid
        for pid, player in players.items()
        if player.alive and player.role == "CREWMATE"
    )
    if not living_crew:
        return surviving_tasks
    for task in pre_death_tasks.values():
        if task.owner != victim or task.completed:
            continue
        eligible = [
            crew
            for crew in living_crew
            if f"{crew}:{task.map_task_id}" not in surviving_tasks
        ]
        if not eligible:
            continue  # every living crewmate already owns this map task; drop it
        if redistribution_policy == "least_remaining_work":
            recipient = min(
                eligible,
                key=lambda crew: (
                    sum(
                        item.required_ticks - item.progress
                        for item in surviving_tasks.values()
                        if item.owner == crew and not item.completed
                    ),
                    crew,
                ),
            )
        else:
            recipient = eligible[0]
        new_id = f"{recipient}:{task.map_task_id}"
        surviving_tasks[new_id] = replace(task, id=new_id, owner=recipient)
    return surviving_tasks


def _apply_kill(
    state: WorldState,
    game_map: Map,
    action: KillAction,
    *,
    redistribution_policy: RedistributionPolicy = "lowest_id",
) -> tuple[WorldState, KilledEvent]:
    body, event = resolve_kill(state, action)
    if body.id in state.bodies:
        raise ActionRejectedError(f"body id already exists: {body.id}")

    players = _with_actor_last_action(state, action)
    target = state.players[action.payload.target]
    # Dead-crewmate task rule: DESIGN.md §3.5 (dropped). Clear the victim's
    # ``last_action`` so the next tick's `_advance_tasks` does not try to
    # continue a `DoTaskAction` for a task that has just been removed.
    players[action.payload.target] = replace(target, alive=False, last_action=None)
    bodies = dict(state.bodies)
    bodies[body.id] = body
    cooldowns = dict(state.cooldowns)
    cooldowns[action.actor] = game_map.kill_cooldown_ticks
    # Dead-crewmate task rule: DESIGN.md §3.5. Drop the killed player's
    # incomplete task *instances* so the crew win check counts only alive-owned
    # instances; completed instances remain (even the victim's) so they still
    # count toward `crew_tasks_done`. The owner-filter is unchanged by the
    # per-player re-key — it already keys on ``task.owner`` per instance.
    surviving_tasks = {
        instance_id: task
        for instance_id, task in state.tasks.items()
        if not (task.owner == action.payload.target and not task.completed)
    }
    # Under ``redistribute`` the dropped incomplete instances are re-keyed to
    # living crewmates instead of vanishing (DESIGN.md §3.5; map-flag-gated). The
    # default ``drop`` leaves ``surviving_tasks`` byte-identical to before.
    if game_map.dead_task_rule == "redistribute":
        tasks = redistribute_dead_tasks(
            surviving_tasks=surviving_tasks,
            pre_death_tasks=state.tasks,
            players=players,
            victim=action.payload.target,
            redistribution_policy=redistribution_policy,
        )
    else:
        tasks = surviving_tasks
    return (
        replace(
            state,
            players=players,
            bodies=bodies,
            cooldowns=cooldowns,
            tasks=tasks,
        ),
        event,
    )


def _apply_vent(
    state: WorldState, game_map: Map, action: VentAction
) -> tuple[WorldState, VentEnteredEvent | VentExitedEvent]:
    event = resolve_vent(state, game_map, action)
    vent = game_map.vents[action.payload.vent_id]
    players = _with_actor_last_action(state, action)
    actor = players[action.actor]
    players[action.actor] = replace(actor, room=vent.room, in_vent=not actor.in_vent)
    return replace(state, players=players), event


def _apply_report(
    state: WorldState, action: ReportBodyAction
) -> tuple[WorldState, MeetingTriggeredEvent]:
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
) -> tuple[WorldState, MeetingTriggeredEvent]:
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
) -> tuple[WorldState, SabotageStartedEvent]:
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


def _apply_repair_sabotage(
    state: WorldState,
    game_map: Map,
    action: RepairSabotageAction,
) -> tuple[WorldState, SabotageRepairProgressedEvent | SabotageRepairedEvent]:
    resolve_repair_sabotage(state, game_map, action)
    sabotage = state.sabotage
    if sabotage is None:
        raise ValueError("repair validation passed without active sabotage")

    actor = state.players[action.actor]
    kind = action.payload.kind
    room = actor.room
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
    next_state = replace(state, players=players, sabotage=next_sabotage)
    if completed:
        return next_state, SabotageRepairedEvent(
            type="SabotageRepaired",
            tick=state.tick,
            actor=action.actor,
            kind=kind,
            room=room,
            progress=progress,
            required_ticks=sabotage_definition.repair_ticks,
        )
    return next_state, SabotageRepairProgressedEvent(
        type="SabotageRepairProgressed",
        tick=state.tick,
        actor=action.actor,
        kind=kind,
        room=room,
        progress=progress,
        required_ticks=sabotage_definition.repair_ticks,
    )


def _apply_wait(
    state: WorldState, action: WaitAction
) -> tuple[WorldState, WaitedEvent]:
    _ = _get_live_player(state, action.actor)
    players = _with_actor_last_action(state, action)
    event = WaitedEvent(type="Waited", tick=state.tick, actor=action.actor)
    return replace(state, players=players), event


def _apply_action(
    state: WorldState,
    game_map: Map,
    action: Action,
    *,
    redistribution_policy: RedistributionPolicy = "lowest_id",
) -> tuple[WorldState, EngineEvent]:
    if state.phase != "PLAY":
        raise ActionRejectedError(f"cannot apply gameplay action during {state.phase}")
    if isinstance(action, MoveAction):
        return _apply_move(state, game_map, action)
    if isinstance(action, DoTaskAction):
        return _apply_do_task(state, game_map, action)
    if isinstance(action, KillAction):
        if redistribution_policy == "lowest_id":
            return _apply_kill(state, game_map, action)
        return _apply_kill(
            state, game_map, action, redistribution_policy=redistribution_policy
        )
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
    state: WorldState,
    actions: Sequence[Action],
    *,
    game_map: Map,
    rng_hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
    redistribution_policy: RedistributionPolicy = "lowest_id",
) -> tuple[WorldState, list[EngineEvent]]:
    """Advance one engine tick using the DESIGN.md §3.1 seven-step loop.

    ``rng_hash_policy`` selects the per-tick rng-state serialization (Task
    15.8.1). It DEFAULTS to :attr:`RngStateHashPolicy.FULL`, which is
    byte-identical to the pre-15.8.1 tick — every recorder, reconstructor, and
    committed-replay path uses it, so ``state_hash`` chains stay stable. The
    opt-in :attr:`RngStateHashPolicy.TRAINING_FAST` skips the ~43%-of-engine-cost
    ``json.dumps`` snapshot for non-recorded training rollouts; the DRAW is
    unchanged, so the action / event stream is identical under either policy
    (only the ``rng_state`` encoding, and hence any hash of it, differs)."""

    if state.phase != "PLAY":
        raise ValueError(f"cannot advance tick during {state.phase}")
    if redistribution_policy not in ("lowest_id", "least_remaining_work"):
        raise ValueError(f"unknown redistribution policy: {redistribution_policy!r}")
    if (
        redistribution_policy != "lowest_id"
        and game_map.dead_task_rule != "redistribute"
    ):
        raise ValueError("workload redistribution requires the redistribute task rule")

    _validate_state_map(state, game_map)
    events: list[EngineEvent] = []
    working_state = state
    cooldown_skip_players: set[PlayerId] = set()
    submitted_actors = {action.actor for action in actions}

    # 1) Apply queued actions from previous tick.
    for action in actions:
        try:
            working_state, event = _apply_action(
                working_state,
                game_map,
                action,
                redistribution_policy=redistribution_policy,
            )
            events.append(event)
            if event.type == "Killed":
                cooldown_skip_players.add(action.actor)
            if working_state.phase == "MEETING":
                # A tick that decides the game does not open a meeting. The win
                # check runs here so the §3.5 order holds on every tick — a kill
                # that reaches parity beside a report attributes to the offense
                # instead of being handed to a meeting that can invert it.
                # Task 21.6 overrides the Phase-1 skip.
                win_result = resolve_win_conditions(working_state)
                if win_result is not None:
                    events.append(
                        GameOverEvent(
                            type="GameOver",
                            tick=state.tick,
                            winner=win_result.winner,
                            reason=win_result.reason,
                        )
                    )
                    return replace(working_state, phase="GAME_OVER"), events
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
        game_map,
        tick=state.tick,
        submitted_actors=submitted_actors,
    )

    working_state = replace(
        working_state, cooldowns=cooldowns, sabotage=sabotage, tasks=tasks
    )
    events.extend(task_events)

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

    # FROZEN (Phase 19 tier map, training/README.md): the byte-frozen RNG-draw
    # apparatus — the draw's value is discarded; it exists to advance the RNG
    # cursor so state_hash chains stay byte-identical on every committed
    # replay. Removing or consuming it would shift every hash chain and break
    # replay byte-identity. Bug fixes and evidence readers only; no new search.
    # (A note, not a module freeze: the engine is live.)
    # RNG state is explicitly threaded through the tick transition. The DRAW
    # happens under either policy (the cursor advances identically); only the
    # snapshot encoding of the advanced state differs (Task 15.8.1). Under the
    # default FULL policy this is byte-identical to the pre-15.8.1 tick.
    rng = EngineRng.from_state(state.rng_state)
    _, next_rng_state = rng.randint(0, 2**31 - 1, hash_policy=rng_hash_policy)

    next_state = replace(working_state, tick=state.tick + 1, rng_state=next_rng_state)

    # 4/5 are orchestrator responsibilities: observations and action solicitation.
    # 6) Emit tick event.
    events.append(TickAdvancedEvent(type="TickAdvanced", tick=next_state.tick))

    # 7) Tick increment happens in next_state above.
    return next_state, events
