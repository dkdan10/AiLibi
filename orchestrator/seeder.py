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
) -> WorldState:
    """Build a deterministic initial :class:`WorldState` for one headless game.

    Player ids are ``p-1`` ... ``p-{num_players}`` in fixed lexical order.
    Role assignment is randomised by a seed-shuffled permutation: the
    first ``num_impostors`` entries become impostors, the rest crewmates.
    The id substring never encodes role, so a crewmate's
    :class:`observation.packet.ObservationPacket.visible_players` cannot
    leak the impostor's identity through the id alone.

    Spawns: every player starts in ``game_map.spawn.room``.

    Task assignment: each crewmate owns exactly one task. Tasks are
    drawn round-robin from a seed-shuffled list of all map task ids,
    so the same seed produces the same per-crewmate task. Tasks not
    assigned in this round are simply omitted from ``WorldState.tasks``.

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
) -> dict[TaskId, TaskState]:
    rng = random.Random(seed)
    map_task_ids = sorted(game_map.tasks)
    rng.shuffle(map_task_ids)
    tasks: dict[TaskId, TaskState] = {}
    for index, crewmate_id in enumerate(crewmate_ids):
        task_id = map_task_ids[index % len(map_task_ids)]
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
