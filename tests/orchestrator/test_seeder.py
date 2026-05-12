from __future__ import annotations

import pytest

from engine.world import load_canonical_map
from orchestrator.seeder import seed_initial_state


def test_seed_initial_state_is_deterministic_for_same_seed() -> None:
    game_map = load_canonical_map()

    first = seed_initial_state(seed=42, game_map=game_map, num_players=4)
    second = seed_initial_state(seed=42, game_map=game_map, num_players=4)

    assert first == second


def test_seed_initial_state_uses_canonical_phase_and_tick() -> None:
    game_map = load_canonical_map()

    state = seed_initial_state(seed=42, game_map=game_map, num_players=4)

    assert state.tick == 0
    assert state.phase == "PLAY"
    assert state.map == game_map.id
    assert state.seed == 42
    assert state.bodies == {}
    assert state.sabotage is None
    assert state.emergency_uses == {}


def test_seed_initial_state_spawns_every_player_at_spawn_room() -> None:
    game_map = load_canonical_map()

    state = seed_initial_state(seed=1, game_map=game_map, num_players=5)

    for player in state.players.values():
        assert player.room == game_map.spawn.room
        assert player.alive is True
        assert player.in_vent is False
        assert player.last_action is None


def test_seed_initial_state_partitions_roles_by_id_prefix() -> None:
    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=7, game_map=game_map, num_players=5, num_impostors=2
    )

    crewmates = {pid for pid, p in state.players.items() if p.role == "CREWMATE"}
    impostors = {pid for pid, p in state.players.items() if p.role == "IMPOSTOR"}

    assert crewmates == {"player-1", "player-2", "player-3"}
    assert impostors == {"impostor-1", "impostor-2"}
    assert state.cooldowns == {"impostor-1": 0, "impostor-2": 0}


def test_seed_initial_state_assigns_only_crewmates_to_tasks() -> None:
    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=3, game_map=game_map, num_players=4, num_impostors=1
    )
    crewmate_ids = {pid for pid, p in state.players.items() if p.role == "CREWMATE"}

    assert len(state.tasks) == len(crewmate_ids)
    for task in state.tasks.values():
        assert task.owner in crewmate_ids
        assert task.completed is False
        assert task.progress == 0
        assert task.required_ticks == game_map.tasks[task.id].duration_ticks
        assert task.room == game_map.tasks[task.id].room


def test_seed_initial_state_changes_task_assignment_per_seed() -> None:
    game_map = load_canonical_map()

    assignments = {
        seed: tuple(
            sorted(
                seed_initial_state(seed=seed, game_map=game_map, num_players=4).tasks
            )
        )
        for seed in (0, 1, 2, 3, 4, 5, 6, 7)
    }

    # At least two distinct task sets across these seeds.
    assert len({tuple(sorted(taskset)) for taskset in assignments.values()}) >= 2


def test_seed_initial_state_rng_state_round_trips_through_engine_rng() -> None:
    from engine.rng import EngineRng

    game_map = load_canonical_map()
    state = seed_initial_state(seed=99, game_map=game_map, num_players=4)

    # Replay should re-deserialize the rng cursor without raising.
    rng = EngineRng.from_state(state.rng_state)
    value, next_state = rng.randint(0, 100)
    assert 0 <= value <= 100
    assert isinstance(next_state, bytes)


def test_seed_initial_state_rejects_too_few_players() -> None:
    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="num_players"):
        seed_initial_state(seed=1, game_map=game_map, num_players=1)


def test_seed_initial_state_rejects_zero_impostors() -> None:
    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="num_impostors"):
        seed_initial_state(seed=1, game_map=game_map, num_players=4, num_impostors=0)


def test_seed_initial_state_rejects_impostor_parity_at_start() -> None:
    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="strictly less"):
        seed_initial_state(seed=1, game_map=game_map, num_players=2, num_impostors=2)


def test_seed_initial_state_supports_three_player_two_one_split() -> None:
    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=11, game_map=game_map, num_players=3, num_impostors=1
    )

    roles = {pid: player.role for pid, player in state.players.items()}
    assert roles == {
        "player-1": "CREWMATE",
        "player-2": "CREWMATE",
        "impostor-1": "IMPOSTOR",
    }
