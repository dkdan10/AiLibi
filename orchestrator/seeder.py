"""Initial world-state seeder (DESIGN.md §1.4, §3.1).

Builds a deterministic initial :class:`WorldState` from a seed: assigns
roles, spawns, and task ownership. The seeder is the orchestrator's
entry into the engine — it is how a single headless game starts.

Shape reference: ``tests/_helpers/world_state.scripted_initial_world_state``
pins the scripted-game fixture shape. ``seed_initial_state`` reproduces
that shape from a seed so eval scripts can stop hand-rolling initial
states.
"""

from __future__ import annotations

import random
from typing import Final

from engine.entities import PlayerId, PlayerState, Role, TaskState
from engine.rng import EngineRng
from engine.world import Map, TaskId, WorldState

_CREWMATE_ID_PREFIX: Final[str] = "player-"
_IMPOSTOR_ID_PREFIX: Final[str] = "impostor-"


def seed_initial_state(
    *,
    seed: int,
    game_map: Map,
    num_players: int,
    num_impostors: int = 1,
) -> WorldState:
    """Build a deterministic initial :class:`WorldState` for one headless game.

    Role assignment is implicit in id naming: crewmates get
    ``player-1`` ... ``player-{num_crewmates}`` and impostors get
    ``impostor-1`` ... ``impostor-{num_impostors}``. The id set is stable
    across seeds; only the task assignment and rng state depend on the
    seed. This mirrors the shape of
    ``tests/_helpers/world_state.scripted_initial_world_state``.

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

    num_crewmates = num_players - num_impostors
    crewmate_ids = _build_player_ids(_CREWMATE_ID_PREFIX, num_crewmates)
    impostor_ids = _build_player_ids(_IMPOSTOR_ID_PREFIX, num_impostors)

    players = _build_players(
        crewmate_ids=crewmate_ids,
        impostor_ids=impostor_ids,
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


def _build_player_ids(prefix: str, count: int) -> tuple[PlayerId, ...]:
    return tuple(f"{prefix}{index + 1}" for index in range(count))


def _build_players(
    *,
    crewmate_ids: tuple[PlayerId, ...],
    impostor_ids: tuple[PlayerId, ...],
    spawn_room: str,
) -> dict[PlayerId, PlayerState]:
    players: dict[PlayerId, PlayerState] = {}
    position_index = 0
    for player_id in crewmate_ids:
        players[player_id] = _new_player(
            player_id=player_id,
            role="CREWMATE",
            spawn_room=spawn_room,
            position_index=position_index,
        )
        position_index += 1
    for player_id in impostor_ids:
        players[player_id] = _new_player(
            player_id=player_id,
            role="IMPOSTOR",
            spawn_room=spawn_room,
            position_index=position_index,
        )
        position_index += 1
    return players


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
