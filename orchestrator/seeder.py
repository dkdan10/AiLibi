"""Initial world-state seeder (DESIGN.md §1.4, §3.1).

Builds a deterministic initial :class:`WorldState` from a seed: assigns
roles, spawns, and task ownership. The seeder is the orchestrator's
entry into the engine — it is how a single headless game starts.

Player ids are role-neutral by design: every player is named ``p-1``,
``p-2``, ..., ``p-{num_players}`` in fixed lexical order. Role assignment
is randomised by a seed-shuffled permutation, so the id substring never
encodes role and an :class:`ObservationPacket` consumer cannot infer the
impostor from any visible player's id. Roles live on
:class:`engine.entities.PlayerState.role` only.

Shape reference: ``tests/_helpers/world_state.scripted_initial_world_state``
pins the scripted-game fixture shape. ``seed_initial_state`` reproduces
that shape from a seed so eval scripts can stop hand-rolling initial
states.
"""

from __future__ import annotations

import random

from engine.entities import PlayerId, PlayerState, Role, TaskInstanceId, TaskState
from engine.rng import EngineRng
from engine.world import Map, WorldState


def seed_initial_state(
    *,
    seed: int,
    game_map: Map,
    num_players: int,
    num_impostors: int = 1,
    tasks_per_crewmate: int = 1,
) -> WorldState:
    """Build a deterministic initial :class:`WorldState` for one headless game.

    Player ids are ``p-1`` ... ``p-{num_players}`` in fixed lexical order.
    Role assignment is randomised by a seed-shuffled permutation: the
    first ``num_impostors`` entries become impostors, the rest crewmates.
    The id substring never encodes role, so a crewmate's
    :class:`observation.packet.ObservationPacket.visible_players` cannot
    leak the impostor's identity through the id alone.

    Spawns: every player starts in ``game_map.spawn.room``.

    Task assignment: each crewmate owns ``tasks_per_crewmate`` per-player
    task *instances* keyed by the composite instance id
    ``"{owner}:{map_task_id}"`` (DESIGN.md §3.2). The map's task ids are
    shuffled once with ``random.Random(seed)`` and dealt by a wrapping
    cursor, so the assignment is a pure function of the seed and OVERLAP
    ACROSS CREWMATES is allowed — two crewmates may hold the same map task
    as independent instances with independent progress. There is no
    ``num_crewmates * tasks_per_crewmate <= len(game_map.tasks)`` cap, which
    is what lets a 9p/2i roster seed 14 instances over the 12 map tasks
    (DESIGN.md §3.5). ``tasks_per_crewmate`` defaults to ``1`` — the
    historical value — so a caller that omits it (e.g. the committed-replay
    loader) reproduces the original one-task-per-crewmate
    ``(owner, map_task_id)`` assignment, only re-keyed to the composite
    instance id. The harness/CLI layer raises this to
    ``orchestrator.game.DEFAULT_TASKS_PER_CREWMATE`` for live runs.

    Fail-loud (AGENTS.md "no silent fallbacks"): ``tasks_per_crewmate < 1``
    raises, and ``tasks_per_crewmate > len(game_map.tasks)`` raises — a
    single crewmate cannot hold the same map task twice, so its instances
    must be distinct map tasks (overlap is allowed only ACROSS crewmates).

    Cooldowns: only impostors carry a kill cooldown, initialised to 0.
    """

    if num_players < 2:
        raise ValueError(f"num_players must be at least 2, got {num_players}")
    if num_impostors < 1:
        raise ValueError(f"num_impostors must be at least 1, got {num_impostors}")
    if num_impostors >= num_players:
        raise ValueError(
            "num_impostors must be strictly less than num_players: "
            f"got num_impostors={num_impostors}, num_players={num_players}"
        )
    if tasks_per_crewmate < 1:
        raise ValueError(
            f"tasks_per_crewmate must be at least 1, got {tasks_per_crewmate}"
        )
    if not game_map.tasks:
        raise ValueError("game map must define at least one task")

    player_ids = _build_player_ids(num_players)
    role_by_id = _assign_roles(
        seed=seed, player_ids=player_ids, num_impostors=num_impostors
    )
    crewmate_ids = tuple(pid for pid in player_ids if role_by_id[pid] == "CREWMATE")
    impostor_ids = tuple(pid for pid in player_ids if role_by_id[pid] == "IMPOSTOR")

    players = _build_players(
        player_ids=player_ids,
        role_by_id=role_by_id,
        spawn_room=game_map.spawn.room,
    )
    cooldowns: dict[PlayerId, int] = {pid: 0 for pid in impostor_ids}
    tasks = _build_tasks(
        seed=seed,
        game_map=game_map,
        crewmate_ids=crewmate_ids,
        tasks_per_crewmate=tasks_per_crewmate,
    )

    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players=players,
        bodies={},
        tasks=tasks,
        sabotage=None,
        cooldowns=cooldowns,
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def _build_player_ids(num_players: int) -> tuple[PlayerId, ...]:
    return tuple(f"p-{index + 1}" for index in range(num_players))


def _assign_roles(
    *,
    seed: int,
    player_ids: tuple[PlayerId, ...],
    num_impostors: int,
) -> dict[PlayerId, Role]:
    rng = random.Random(seed)
    permutation = list(player_ids)
    rng.shuffle(permutation)
    impostor_ids = set(permutation[:num_impostors])
    return {
        pid: ("IMPOSTOR" if pid in impostor_ids else "CREWMATE") for pid in player_ids
    }


def _build_players(
    *,
    player_ids: tuple[PlayerId, ...],
    role_by_id: dict[PlayerId, Role],
    spawn_room: str,
) -> dict[PlayerId, PlayerState]:
    return {
        player_id: _new_player(
            player_id=player_id,
            role=role_by_id[player_id],
            spawn_room=spawn_room,
            position_index=index,
        )
        for index, player_id in enumerate(player_ids)
    }


def _new_player(
    *,
    player_id: PlayerId,
    role: Role,
    spawn_room: str,
    position_index: int,
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role=role,
        alive=True,
        room=spawn_room,
        position=(float(position_index), 0.0),
        last_action=None,
        in_vent=False,
    )


def _build_tasks(
    *,
    seed: int,
    game_map: Map,
    crewmate_ids: tuple[PlayerId, ...],
    tasks_per_crewmate: int,
) -> dict[TaskInstanceId, TaskState]:
    """Mint ``tasks_per_crewmate`` per-player task *instances* per crewmate.

    Per-player re-key (DESIGN.md §3.2): ``WorldState.tasks`` is keyed by the
    composite instance id ``"{owner}:{map_task_id}"`` (a
    :data:`~engine.entities.TaskInstanceId`), so several crewmates can each hold
    an instance of the SAME map task with independent progress. There is
    therefore no ``num_crewmates * tasks_per_crewmate <= len(game_map.tasks)``
    cap (the pre-instance fail-loud is gone): overlap across crewmates is allowed,
    which is what lets 9p/2i seed 14 instances over the 12 map tasks
    (DESIGN.md §3.5).

    Determinism contract (a pure function of the seed; no RNG draw beyond the one
    seeded shuffle): the map task ids are shuffled once with
    ``random.Random(seed)`` over ``sorted(game_map.tasks)`` — the unchanged prefix
    from the historical one-task-per-crewmate implementation — then dealt by a
    single cursor that wraps (``map_task_ids[cursor % len(map_task_ids)]``) so it
    never exhausts. For any roster that fits the pool (e.g. the flat 4p/1i at one
    task) the cursor never wraps, so the dealt ``(owner, map_task_id)`` pairs are
    byte-identical to the pre-instance assignment — ONLY the dict key changes
    (bare map id -> ``"{owner}:{map_task_id}"``), so the committed 4p/1i baseline
    re-seeds the same instances. Once the cursor passes the pool size the deal
    wraps and later crewmates re-draw earlier map ids as their own fresh instances.

    Within one crewmate's slice the ``tasks_per_crewmate`` consecutive cursor
    values map to distinct pool indices iff
    ``tasks_per_crewmate <= len(game_map.tasks)``; a larger value would deal one
    crewmate the same map task twice, collapsing two instances onto one composite
    key — a silent loss the seeder rejects fail-loud (AGENTS.md "no silent
    fallbacks"). Overlap is allowed only ACROSS crewmates, never within one.
    """

    if tasks_per_crewmate > len(game_map.tasks):
        raise ValueError(
            "tasks_per_crewmate exceeds the map's task pool: a single crewmate "
            f"cannot hold {tasks_per_crewmate} distinct map tasks when the map "
            f"defines only {len(game_map.tasks)}. Overlap is allowed ACROSS "
            "crewmates, but one crewmate's instances must be distinct map tasks; "
            "lower tasks_per_crewmate or use a map with more tasks."
        )

    rng = random.Random(seed)
    map_task_ids = sorted(game_map.tasks)
    rng.shuffle(map_task_ids)
    pool_size = len(map_task_ids)
    tasks: dict[TaskInstanceId, TaskState] = {}
    cursor = 0
    for crewmate_id in crewmate_ids:
        for _ in range(tasks_per_crewmate):
            map_task_id = map_task_ids[cursor % pool_size]
            cursor += 1
            task_definition = game_map.tasks[map_task_id]
            # Per-player instance (DESIGN.md §3.2): the dict key and ``id`` are the
            # composite ``"{owner}:{map_task_id}"``; the agent-facing id stays the
            # map id, which the engine resolves against ``owner``. Distinct owners
            # of the same map task get distinct composite keys, so overlap is safe.
            instance_id = f"{crewmate_id}:{map_task_id}"
            tasks[instance_id] = TaskState(
                id=instance_id,
                owner=crewmate_id,
                map_task_id=map_task_id,
                room=task_definition.room,
                progress=0,
                required_ticks=task_definition.duration_ticks,
                completed=False,
            )
    return tasks


__all__ = ["seed_initial_state"]
