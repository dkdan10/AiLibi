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

from engine.entities import PlayerId, PlayerState, Role, TaskState
from engine.rng import EngineRng
from engine.world import Map, TaskId, WorldState


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

    Task assignment: each crewmate owns exactly ``tasks_per_crewmate``
    *distinct* map task ids. The map's task ids are shuffled once with
    ``random.Random(seed)`` and dealt out by a flat cursor — the first
    crewmate takes the first ``tasks_per_crewmate`` ids, the next crewmate
    the following ``tasks_per_crewmate``, and so on — so no two crewmates
    ever share a task id (the engine keys ``WorldState.tasks`` by
    :class:`~engine.world.TaskId` and enforces ``TaskState.id == <dict
    key>``, so a shared id would corrupt the world). ``tasks_per_crewmate``
    defaults to ``1`` — the historical value — so a caller that omits it
    (e.g. the committed-replay loader) reproduces the original
    one-task-per-crewmate assignment byte-for-byte. The harness/CLI layer
    raises this to ``orchestrator.game.DEFAULT_TASKS_PER_CREWMATE`` for live
    runs. Tasks not dealt out are simply omitted from ``WorldState.tasks``.

    Fail-loud (AGENTS.md "no silent fallbacks"): ``tasks_per_crewmate < 1``
    raises, and a roster that would need more distinct ids than the map has
    (``num_crewmates * tasks_per_crewmate > len(game_map.tasks)``) raises
    rather than reusing an id.

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
) -> dict[TaskId, TaskState]:
    """Deal ``tasks_per_crewmate`` distinct map task ids to each crewmate.

    Determinism contract: the shuffle prefix is unchanged from the original
    one-task-per-crewmate implementation (``random.Random(seed)`` then
    ``rng.shuffle(sorted(game_map.tasks))``), and the ids are dealt by a flat
    cursor over the shuffled pool. For ``tasks_per_crewmate == 1`` this deals
    ``shuffled[i]`` to crewmate ``i`` — identical to the historical
    ``map_task_ids[index % len(map_task_ids)]`` for any roster that fits the
    pool — so the committed 4p/1i baseline reconstructs byte-for-byte. A flat
    cursor (never a modulo) guarantees every dealt id is unique, so the engine's
    ``TaskState.id == <dict key>`` invariant (``engine/tick.py``) holds across
    the whole roster.
    """

    required = len(crewmate_ids) * tasks_per_crewmate
    if required > len(game_map.tasks):
        raise ValueError(
            "task pool exhausted: assigning tasks_per_crewmate="
            f"{tasks_per_crewmate} distinct task(s) to each of "
            f"{len(crewmate_ids)} crewmate(s) needs {required} distinct map task "
            f"ids, but the map defines only {len(game_map.tasks)}. Lower "
            "tasks_per_crewmate or num_players, or use a map with more tasks."
        )

    rng = random.Random(seed)
    map_task_ids = sorted(game_map.tasks)
    rng.shuffle(map_task_ids)
    tasks: dict[TaskId, TaskState] = {}
    cursor = 0
    for crewmate_id in crewmate_ids:
        for _ in range(tasks_per_crewmate):
            task_id = map_task_ids[cursor]
            cursor += 1
            task_definition = game_map.tasks[task_id]
            tasks[task_id] = TaskState(
                id=task_id,
                owner=crewmate_id,
                room=task_definition.room,
                progress=0,
                required_ticks=task_definition.duration_ticks,
                completed=False,
            )
    return tasks


__all__ = ["seed_initial_state"]
