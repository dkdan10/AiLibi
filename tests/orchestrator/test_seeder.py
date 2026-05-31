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


def test_seed_initial_state_uses_role_neutral_ids() -> None:
    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=7, game_map=game_map, num_players=5, num_impostors=2
    )

    assert set(state.players) == {"p-1", "p-2", "p-3", "p-4", "p-5"}
    crewmates = {pid for pid, p in state.players.items() if p.role == "CREWMATE"}
    impostors = {pid for pid, p in state.players.items() if p.role == "IMPOSTOR"}

    # Seed=7 with num_players=5 shuffles the lexical id list to
    # ['p-5', 'p-1', 'p-4', 'p-2', 'p-3']; the first two become impostors.
    assert impostors == {"p-1", "p-5"}
    assert crewmates == {"p-2", "p-3", "p-4"}
    assert state.cooldowns == {pid: 0 for pid in impostors}


def test_seed_initial_state_id_substring_does_not_encode_role() -> None:
    game_map = load_canonical_map()

    for seed in (0, 1, 2, 3, 7, 42, 100):
        state = seed_initial_state(
            seed=seed, game_map=game_map, num_players=4, num_impostors=1
        )
        for player_id, player in state.players.items():
            # Role-bearing substrings would let a packet consumer decode
            # the impostor from a visible player's id.
            assert "impostor" not in player_id.lower()
            assert "crewmate" not in player_id.lower()
            assert "crew" not in player_id.lower()
            assert player_id.startswith("p-")
            # Role lives only on PlayerState.role, not in the id.
            assert player.role in {"CREWMATE", "IMPOSTOR"}


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
    # Seed=11 with num_players=3 shuffles to ['p-1', 'p-3', 'p-2']; p-1 is
    # the single impostor and the other two are crewmates.
    assert roles == {
        "p-1": "IMPOSTOR",
        "p-2": "CREWMATE",
        "p-3": "CREWMATE",
    }


def test_seed_initial_state_defaults_to_one_task_per_crewmate() -> None:
    """The seeder's own parameter default stays 1 (NOT 2).

    The locked default-of-2 lives at the harness/CLI layer
    (``orchestrator.game.DEFAULT_TASKS_PER_CREWMATE``); the seeder default must
    remain 1 so ``api/replay_loader.py``'s default-driven ``_walk`` call keeps
    re-seeding the committed 4p/1i baseline byte-identically (Task 7.1 contract).
    """

    game_map = load_canonical_map()

    state = seed_initial_state(seed=3, game_map=game_map, num_players=4)
    crewmate_ids = {pid for pid, p in state.players.items() if p.role == "CREWMATE"}

    assert len(state.tasks) == len(crewmate_ids)


def test_seed_initial_state_one_task_assignment_matches_historical_bytes() -> None:
    """``tasks_per_crewmate=1`` reproduces the pre-task assignment byte-for-byte.

    Pins the historical one-task-per-crewmate assignment for fixed seeds so the
    committed 4p/1i baseline path stays unchanged. These golden ``(owner,
    task_id)`` pairs — in dict-insertion order — were captured from the seeder
    BEFORE Task 7.1 widened it; any drift in the RNG draw order or the
    assignment would change them and break committed-replay reconstruction.
    """

    game_map = load_canonical_map()

    for seed, expected in (
        (
            0,
            [
                ("p-1", "analyze_specimen"),
                ("p-2", "submit_scan"),
                ("p-4", "start_reactor"),
            ],
        ),
        (
            42,
            [
                ("p-1", "log_findings"),
                ("p-2", "fuel_reserves"),
                ("p-4", "calibrate_distributor"),
            ],
        ),
    ):
        # The explicit tasks_per_crewmate=1 and the omitted default must agree.
        for kwargs in ({}, {"tasks_per_crewmate": 1}):
            state = seed_initial_state(
                seed=seed, game_map=game_map, num_players=4, num_impostors=1, **kwargs
            )
            assert [(t.owner, tid) for tid, t in state.tasks.items()] == expected


def test_seed_initial_state_assigns_distinct_ids_per_crewmate() -> None:
    """Each crewmate owns exactly ``tasks_per_crewmate`` distinct map task ids.

    Covers the structural invariant the engine enforces
    (``engine/tick.py``): ``len(state.tasks) == num_crewmates *
    tasks_per_crewmate``, every assigned id is unique, and every
    ``TaskState.id`` equals its ``WorldState.tasks`` dict key — so no two
    crewmates can share a map task id.
    """

    game_map = load_canonical_map()
    tasks_per_crewmate = 2

    state = seed_initial_state(
        seed=7,
        game_map=game_map,
        num_players=7,
        num_impostors=2,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    crewmate_ids = [pid for pid, p in state.players.items() if p.role == "CREWMATE"]

    assert len(state.tasks) == len(crewmate_ids) * tasks_per_crewmate
    # Every id unique and equal to its dict key (the engine invariant).
    assert len(set(state.tasks)) == len(state.tasks)
    for task_id, task in state.tasks.items():
        assert task.id == task_id
        assert task.owner in crewmate_ids
    # Each crewmate owns exactly tasks_per_crewmate of them.
    owners = [task.owner for task in state.tasks.values()]
    for crewmate_id in crewmate_ids:
        assert owners.count(crewmate_id) == tasks_per_crewmate


def test_seed_initial_state_multi_task_uses_flat_cursor_not_modulo() -> None:
    """Multiple tasks per crewmate are dealt by a flat cursor over the pool.

    Pins the exact seed-0 two-task partition: crewmates [p-1, p-2, p-4] take the
    shuffled pool's ids in consecutive pairs (NOT a modulo, which would repeat
    ids). The shuffled seed-0 pool starts
    ``[analyze_specimen, submit_scan, start_reactor, fuel_reserves, swipe_card,
    calibrate_distributor, ...]``.
    """

    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=2,
    )

    assert [(t.owner, tid) for tid, t in state.tasks.items()] == [
        ("p-1", "analyze_specimen"),
        ("p-1", "submit_scan"),
        ("p-2", "start_reactor"),
        ("p-2", "fuel_reserves"),
        ("p-4", "swipe_card"),
        ("p-4", "calibrate_distributor"),
    ]


def test_seed_initial_state_rejects_tasks_per_crewmate_below_one() -> None:
    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="tasks_per_crewmate"):
        seed_initial_state(
            seed=1,
            game_map=game_map,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=0,
        )


def test_seed_initial_state_rejects_exhausted_task_pool() -> None:
    """A valid roster that needs more distinct ids than the map has fails loud.

    The canonical map has 12 tasks; 10p/1i is 9 crewmates, and at
    ``tasks_per_crewmate=2`` that needs 18 distinct ids > 12 — so the seeder
    raises rather than silently reusing an id (which would violate the engine's
    ``TaskState.id == <dict key>`` invariant). 0 impostors is rejected earlier,
    so the pool can only be exhausted with a valid ``1 <= num_impostors <
    num_players`` roster.
    """

    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="task pool exhausted"):
        seed_initial_state(
            seed=1,
            game_map=game_map,
            num_players=10,
            num_impostors=1,
            tasks_per_crewmate=2,
        )
