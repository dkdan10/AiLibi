from __future__ import annotations

from collections import Counter

import pytest

from engine.actions import KillAction
from engine.tick import advance_tick
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
    # Round-start kill cooldown (DESIGN.md §3.4): impostors seed to the map's
    # ``kill_cooldown_ticks`` (4 on the canonical map), NOT 0; crewmates carry none.
    assert state.cooldowns == {pid: game_map.kill_cooldown_ticks for pid in impostors}


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
    for instance_id, task in state.tasks.items():
        # Per-player re-key (DESIGN.md §3.2): the dict key is the composite
        # instance id and the instance ``id`` equals it.
        assert instance_id == task.id == f"{task.owner}:{task.map_task_id}"
        assert task.owner in crewmate_ids
        assert task.completed is False
        assert task.progress == 0
        # Anchor room + duration come from the MAP task (``map_task_id``), never
        # the composite key.
        assert task.required_ticks == game_map.tasks[task.map_task_id].duration_ticks
        assert task.room == game_map.tasks[task.map_task_id].room


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


def test_seed_initial_state_one_task_keeps_pairs_rekeys_to_instances() -> None:
    """4p/1i mints the SAME ``(owner, map_task_id)`` deal — only the key shape changes.

    Per-player re-key (DESIGN.md §3.2): ``WorldState.tasks`` is keyed by the
    composite instance id ``"{owner}:{map_task_id}"``. The historical
    one-task-per-crewmate ``(owner, map_task_id)`` assignment (captured for fixed
    seeds before the re-key) is unchanged — the wrapping cursor never wraps for a
    roster that fits the pool — so the committed 4p/1i baseline re-seeds the same
    instances; only the dict key changes from the bare map id to the composite id.
    These goldens are the Task 8.2 analogue of the pre-instance golden tuples.
    """

    game_map = load_canonical_map()

    for seed, expected_pairs in (
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
            # The (owner, map_task_id) deal is byte-identical to the pre-re-key
            # golden — the assignment did not move, only the key shape.
            assert [
                (t.owner, t.map_task_id) for t in state.tasks.values()
            ] == expected_pairs
            # ...now re-keyed to the composite instance id, with id == key.
            assert list(state.tasks) == [
                f"{owner}:{map_task_id}" for owner, map_task_id in expected_pairs
            ]
            for instance_id, task in state.tasks.items():
                assert task.id == instance_id


def test_seed_initial_state_mints_per_player_instances_with_overlap() -> None:
    """9p/2i mints 14 instances over 12 map tasks — the old 12-cap is gone.

    Each crewmate owns exactly ``tasks_per_crewmate`` instances keyed by the
    composite ``"{owner}:{map_task_id}"`` with ``TaskState.id`` equal to its key.
    Overlap ACROSS crewmates is allowed (DESIGN.md §3.2/§3.5): 7 crewmates × 2 =
    14 > 12 map tasks, so the deal wraps and at least one map task is held by two
    owners as independent instances. Within a single crewmate the map tasks are
    distinct.
    """

    game_map = load_canonical_map()
    tasks_per_crewmate = 2

    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    crewmate_ids = [pid for pid, p in state.players.items() if p.role == "CREWMATE"]

    assert len(crewmate_ids) == 7
    assert len(state.tasks) == len(crewmate_ids) * tasks_per_crewmate == 14

    # Composite-keyed; instance id == key; every owner is a crewmate; keys unique.
    for instance_id, task in state.tasks.items():
        assert instance_id == task.id == f"{task.owner}:{task.map_task_id}"
        assert task.owner in crewmate_ids
    assert len(set(state.tasks)) == len(state.tasks)

    # Each crewmate owns exactly tasks_per_crewmate instances, all DISTINCT map
    # tasks (overlap is allowed across crewmates, never within one).
    for crewmate_id in crewmate_ids:
        owned = [t.map_task_id for t in state.tasks.values() if t.owner == crewmate_id]
        assert len(owned) == tasks_per_crewmate
        assert len(set(owned)) == tasks_per_crewmate

    # Overlap exists: some map task is owned by >= 2 crewmates.
    map_task_counts = Counter(t.map_task_id for t in state.tasks.values())
    assert max(map_task_counts.values()) >= 2


def test_seed_initial_state_9p2i_deal_is_a_pure_function_of_the_seed() -> None:
    """Pin the exact seed-0 9p/2i instance deal (the wrapping cursor).

    Replaces the pre-instance flat-cursor golden. The shuffled seed-0 pool is
    dealt by a single cursor that wraps past the 12th id, so the 7th crewmate
    (p-9) re-draws the pool's first two ids as its OWN instances — overlapping
    p-1's map tasks but under distinct composite keys.
    """

    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )

    expected_pairs = [
        ("p-1", "analyze_specimen"),
        ("p-1", "submit_scan"),
        ("p-2", "start_reactor"),
        ("p-2", "fuel_reserves"),
        ("p-3", "swipe_card"),
        ("p-3", "calibrate_distributor"),
        ("p-4", "empty_trash"),
        ("p-4", "log_findings"),
        ("p-5", "fix_wiring_cafeteria"),
        ("p-5", "align_engine_output"),
        ("p-7", "upload_logs"),
        ("p-7", "inspect_samples"),
        # cursor wraps here (index 12, 13 -> pool[0], pool[1]):
        ("p-9", "analyze_specimen"),
        ("p-9", "submit_scan"),
    ]
    assert [(t.owner, t.map_task_id) for t in state.tasks.values()] == expected_pairs
    assert list(state.tasks) == [
        f"{owner}:{map_task_id}" for owner, map_task_id in expected_pairs
    ]


def test_seed_initial_state_two_owners_hold_same_map_task_as_instances() -> None:
    """Two crewmates hold one map task as independent per-player instances.

    The per-player model (DESIGN.md §3.2): the seed-0 9p/2i deal wraps so p-1 and
    p-9 both own ``analyze_specimen`` — but as two distinct instances with
    distinct composite keys and independent progress.
    """

    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )

    owners_of_analyze = sorted(
        task.owner
        for task in state.tasks.values()
        if task.map_task_id == "analyze_specimen"
    )
    assert owners_of_analyze == ["p-1", "p-9"]

    # Distinct composite keys -> two independent instances of one map task.
    assert "p-1:analyze_specimen" in state.tasks
    assert "p-9:analyze_specimen" in state.tasks
    first = state.tasks["p-1:analyze_specimen"]
    second = state.tasks["p-9:analyze_specimen"]
    assert first.map_task_id == second.map_task_id == "analyze_specimen"
    # Same anchor room (one map task), but independent (separate) progress fields.
    assert first.room == second.room == game_map.tasks["analyze_specimen"].room
    assert first.progress == 0
    assert second.progress == 0


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


def test_seed_initial_state_allows_more_instances_than_map_tasks() -> None:
    """The old ``num_crewmates * tasks_per_crewmate <= 12`` cap is gone.

    Inverts the pre-instance ``rejects_exhausted_task_pool`` test. 10p/1i is 9
    crewmates; at ``tasks_per_crewmate=2`` that is 18 instances over the 12 map
    tasks — which the pre-instance seeder rejected as an "exhausted task pool".
    Per-player instances with overlap across crewmates (DESIGN.md §3.5) make this
    seed successfully: 18 instances, every one a distinct composite key.
    """

    game_map = load_canonical_map()

    state = seed_initial_state(
        seed=1,
        game_map=game_map,
        num_players=10,
        num_impostors=1,
        tasks_per_crewmate=2,
    )
    crewmate_ids = [pid for pid, p in state.players.items() if p.role == "CREWMATE"]

    assert len(crewmate_ids) == 9
    assert len(state.tasks) == len(crewmate_ids) * 2 == 18
    assert len(set(state.tasks)) == 18  # all composite keys distinct


def test_seed_initial_state_rejects_tasks_per_crewmate_beyond_pool() -> None:
    """A single crewmate cannot hold more distinct map tasks than the map defines.

    Overlap is allowed ACROSS crewmates, but one crewmate's instances must be
    distinct map tasks, so ``tasks_per_crewmate > len(map.tasks)`` fails loud
    rather than silently collapsing two same-map instances onto one composite key
    (AGENTS.md "no silent fallbacks"). The canonical map has 12 map tasks.
    """

    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="tasks_per_crewmate"):
        seed_initial_state(
            seed=1,
            game_map=game_map,
            num_players=3,
            num_impostors=1,
            tasks_per_crewmate=13,
        )


def test_seed_initial_state_seeds_round_start_kill_cooldown() -> None:
    """Every impostor's cooldown seeds to ``kill_cooldown_ticks``, not 0.

    Round-start kill cooldown (DESIGN.md §3.4; audit gp-1): the seeder used to
    initialise impostor cooldowns to 0, granting a free unwitnessed tick-1 spawn
    kill in 26/50 committed games. Seeding to the map's ``kill_cooldown_ticks``
    (4 on the canonical map) makes the first kill obey the same cadence as every
    later one. The value is read off ``game_map``, never a literal.
    """

    game_map = load_canonical_map()
    assert game_map.kill_cooldown_ticks == 4  # canonical map value

    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )
    impostor_ids = {pid for pid, p in state.players.items() if p.role == "IMPOSTOR"}

    assert impostor_ids  # the roster has impostors
    assert state.cooldowns == {
        pid: game_map.kill_cooldown_ticks for pid in impostor_ids
    }
    # Only impostors carry a cooldown — crewmates never appear in the map.
    assert set(state.cooldowns) == impostor_ids


def test_seed_initial_state_blocks_tick_one_spawn_kill() -> None:
    """A kill queued at tick 1 from the seeded state is engine-rejected (gp-1).

    Every player spawns in the same room, so the ONLY precondition the kill
    fails is the seeded round-start cooldown. Pins the engine's literal
    rejection reason ``"kill is on cooldown"`` (engine/rules.py) EXACTLY — the
    audit's mechanical passes grep this string, so it must not be matched
    loosely.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0,
        game_map=game_map,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )
    impostor_id = next(pid for pid, p in state.players.items() if p.role == "IMPOSTOR")
    crewmate_id = next(pid for pid, p in state.players.items() if p.role == "CREWMATE")
    # The kill's only failing precondition is the cooldown: same room, both
    # alive, impostor actor, crewmate target.
    assert state.players[impostor_id].room == state.players[crewmate_id].room
    assert state.cooldowns[impostor_id] == game_map.kill_cooldown_ticks > 0

    kill = KillAction.model_validate(
        {"type": "kill", "actor": impostor_id, "payload": {"target": crewmate_id}}
    )
    next_state, events = advance_tick(state, [kill], game_map=game_map)

    # The engine rejects the queued kill as an ``ActionRejectedEvent`` (it never
    # raises out of ``advance_tick``); the reason is the exact cooldown literal.
    rejections = [e for e in events if e.type == "ActionRejected"]
    assert len(rejections) == 1
    assert rejections[0].actor == impostor_id
    assert rejections[0].reason == "kill is on cooldown"

    # No kill resolved: no Killed event and no body spawned this tick.
    assert not any(e.type == "Killed" for e in events)
    assert next_state.bodies == {}
