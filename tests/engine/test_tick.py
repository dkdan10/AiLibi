from __future__ import annotations

from dataclasses import replace

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyState, PlayerState, SabotageState, TaskState
from engine.events import event_to_dict
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _action(data: object) -> Action:
    return _ACTION_ADAPTER.validate_python(data)


def _player(
    player_id: str,
    role: str,
    room: str,
    position: tuple[float, float],
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="IMPOSTOR" if role == "IMPOSTOR" else "CREWMATE",
        alive=True,
        room=room,
        position=position,
        last_action=None,
        in_vent=False,
    )


def _task(
    map_task_id: str, owner: str, room: str, required_ticks: int = 1
) -> TaskState:
    # Per-player instance (DESIGN.md §3.2): the instance ``id`` is the composite
    # ``"{owner}:{map_task_id}"`` and equals its ``WorldState.tasks`` dict key.
    return TaskState(
        id=f"{owner}:{map_task_id}",
        owner=owner,
        map_task_id=map_task_id,
        room=room,
        progress=0,
        required_ticks=required_ticks,
        completed=False,
    )


def _state() -> WorldState:
    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players={
            "p-1": _player("p-1", "CREWMATE", "CAFETERIA", (0.0, 0.0)),
            "p-2": _player("p-2", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "p-4": _player("p-4", "CREWMATE", "MEDBAY", (0.0, 0.0)),
            "p-3": _player("p-3", "IMPOSTOR", "CAFETERIA", (1.0, 0.0)),
        },
        bodies={},
        tasks={"p-2:swipe_card": _task("swipe_card", "p-2", "ADMIN")},
        sabotage=None,
        cooldowns={"p-3": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def _long_task_state() -> WorldState:
    return replace(
        _state(),
        tasks={"p-2:swipe_card": _task("swipe_card", "p-2", "ADMIN", 3)},
    )


def test_valid_kill_mutates_state_and_emits_event() -> None:
    game_map = load_canonical_map()
    state = _state()
    players = dict(state.players)
    players["crew-b"] = _player("crew-b", "CREWMATE", "CAFETERIA", (2.0, 0.0))
    players["crew-a"] = _player("crew-a", "CREWMATE", "CAFETERIA", (3.0, 0.0))
    players["dead-crew"] = replace(
        _player("dead-crew", "CREWMATE", "CAFETERIA", (4.0, 0.0)),
        alive=False,
    )
    players["vented-crew"] = replace(
        _player("vented-crew", "CREWMATE", "CAFETERIA", (5.0, 0.0)),
        in_vent=True,
    )
    state = replace(state, players=players)

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "kill",
                    "actor": "p-3",
                    "payload": {"target": "p-1"},
                }
            )
        ],
        game_map=game_map,
    )

    assert not next_state.players["p-1"].alive
    assert "body-p-1-0" in next_state.bodies
    assert next_state.cooldowns["p-3"] == 4
    killed_event = next(event for event in events if event.type == "Killed")
    assert event_to_dict(killed_event)["details"]["witnesses"] == ("crew-a", "crew-b")
    assert next_state.phase == "PLAY"

    later_state, _ = advance_tick(next_state, [], game_map=game_map)

    assert later_state.cooldowns["p-3"] == 3


def test_invalid_kill_emits_rejection_and_leaves_state_unchanged() -> None:
    game_map = load_canonical_map()
    state = replace(_state(), cooldowns={"p-3": 1})

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "kill",
                    "actor": "p-3",
                    "payload": {"target": "p-1"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["p-1"].alive
    assert next_state.bodies == {}
    assert next_state.cooldowns["p-3"] == 0
    assert any(event.type == "ActionRejected" for event in events)


def test_continuing_task_progresses_without_repeated_action() -> None:
    game_map = load_canonical_map()
    started_state, start_events = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    continued_state, continue_events = advance_tick(
        started_state,
        [],
        game_map=game_map,
    )

    assert started_state.tasks["p-2:swipe_card"].progress == 1
    assert not started_state.tasks["p-2:swipe_card"].completed
    assert [event.type for event in start_events].count("TaskProgressed") == 1
    assert continued_state.tasks["p-2:swipe_card"].progress == 2
    assert not continued_state.tasks["p-2:swipe_card"].completed
    assert continue_events[0].type == "TaskProgressed"
    assert event_to_dict(continue_events[0])["details"] == {
        "task_id": "swipe_card",
        "progress": 2,
        "required_ticks": 3,
    }


def test_continuing_task_completes_and_can_trigger_crew_win() -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )
    state, _ = advance_tick(state, [], game_map=game_map)

    completed_state, events = advance_tick(state, [], game_map=game_map)

    assert completed_state.tasks["p-2:swipe_card"].progress == 3
    assert completed_state.tasks["p-2:swipe_card"].completed
    assert completed_state.phase == "GAME_OVER"
    assert [event.type for event in events] == ["TaskCompleted", "GameOver"]
    assert event_to_dict(events[1])["winner"] == "CREWMATES"
    assert event_to_dict(events[1])["reason"] == "CREWMATE_TASKS"


def test_submitted_wait_suppresses_continuing_task_progress() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    waited_state, events = advance_tick(
        started_state,
        [_action({"type": "wait", "actor": "p-2", "payload": {}})],
        game_map=game_map,
    )

    assert waited_state.tasks["p-2:swipe_card"].progress == 1
    assert [event.type for event in events].count("TaskProgressed") == 0
    assert events[0].type == "Waited"


def test_submitted_move_suppresses_continuing_task_progress() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    moved_state, events = advance_tick(
        started_state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "UPPER_HALL"},
                }
            )
        ],
        game_map=game_map,
    )

    assert moved_state.tasks["p-2:swipe_card"].progress == 1
    assert moved_state.players["p-2"].room == "UPPER_HALL"
    assert [event.type for event in events].count("TaskProgressed") == 0
    assert events[0].type == "Moved"


def test_rejected_action_suppresses_continuing_task_progress_for_that_tick() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    rejected_state, rejected_events = advance_tick(
        started_state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "REACTOR"},
                }
            )
        ],
        game_map=game_map,
    )
    continued_state, continued_events = advance_tick(
        rejected_state,
        [],
        game_map=game_map,
    )

    assert rejected_state.tasks["p-2:swipe_card"].progress == 1
    assert rejected_events[0].type == "ActionRejected"
    assert [event.type for event in rejected_events].count("TaskProgressed") == 0
    assert continued_state.tasks["p-2:swipe_card"].progress == 2
    assert continued_events[0].type == "TaskProgressed"


def test_repeated_do_task_action_increments_once_per_tick() -> None:
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    next_state, events = advance_tick(
        started_state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.tasks["p-2:swipe_card"].progress == 2
    assert [event.type for event in events].count("TaskProgressed") == 1


def test_move_and_task_actions_apply_expected_mutations() -> None:
    game_map = load_canonical_map()
    moved_state, move_events = advance_tick(
        _state(),
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-1",
                    "payload": {"to_room": "UPPER_HALL"},
                }
            )
        ],
        game_map=game_map,
    )
    task_state = replace(
        moved_state,
        players={
            **dict(moved_state.players),
            "p-2": replace(moved_state.players["p-2"], room="ADMIN"),
        },
        tasks={"p-2:swipe_card": _task("swipe_card", "p-2", "ADMIN")},
    )

    next_state, task_events = advance_tick(
        task_state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert moved_state.players["p-1"].room == "UPPER_HALL"
    assert any(event.type == "Moved" for event in move_events)
    assert next_state.tasks["p-2:swipe_card"].completed
    assert next_state.tasks["p-2:swipe_card"].progress == 1
    assert any(event.type == "TaskCompleted" for event in task_events)


def test_do_task_advances_only_the_actors_own_instance() -> None:
    # Per-player re-key (DESIGN.md §3.2): p-2 and p-4 each hold an INSTANCE of the
    # SAME map task ("swipe_card") in ADMIN with independent progress. p-2 doing the
    # task advances ONLY p-2's instance; p-4's instance never moves. The agent-facing
    # id stays the map id — the engine resolves (actor, map_task_id) to the actor's
    # own instance, so two owners of one map task can never corrupt each other.
    game_map = load_canonical_map()
    base = _state()
    players = dict(base.players)
    players["p-4"] = replace(players["p-4"], room="ADMIN")
    state = replace(
        base,
        players=players,
        tasks={
            "p-2:swipe_card": _task("swipe_card", "p-2", "ADMIN", required_ticks=3),
            "p-4:swipe_card": _task("swipe_card", "p-4", "ADMIN", required_ticks=3),
        },
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    # Only p-2's instance advanced; p-4's instance of the same map task is untouched.
    assert next_state.tasks["p-2:swipe_card"].progress == 1
    assert next_state.tasks["p-4:swipe_card"].progress == 0
    # The progress event carries the MAP id; the owner is disambiguated by actor.
    progressed = [event for event in events if event.type == "TaskProgressed"]
    assert len(progressed) == 1
    progressed_dump = event_to_dict(progressed[0])
    assert progressed_dump["actor"] == "p-2"
    assert progressed_dump["details"]["task_id"] == "swipe_card"


def test_do_task_fails_loud_for_unowned_or_out_of_pool_map_id() -> None:
    # DESIGN.md §3.2 ownership guarantee: an actor can only advance ITS OWN instance.
    # p-1 owns no instance of "swipe_card" (p-2 does), and "no_such_task" is out of
    # pool entirely — both resolve to nothing and fail loud (rejected), advancing
    # no instance.
    game_map = load_canonical_map()
    base = _state()
    # Co-locate p-1 in ADMIN so the rejection is about ownership, not the room.
    players = dict(base.players)
    players["p-1"] = replace(players["p-1"], room="ADMIN")
    state = replace(base, players=players)

    # (a) Foreign owner: p-1 submits p-2's map task; p-1 holds no such instance.
    foreign_state, foreign_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-1",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )
    assert foreign_events[0].type == "ActionRejected"
    assert "swipe_card" in event_to_dict(foreign_events[0])["reason"]
    # p-2's instance is untouched by p-1's rejected attempt.
    assert foreign_state.tasks["p-2:swipe_card"].progress == 0

    # (b) Out-of-pool map id: nobody owns "no_such_task".
    _, out_of_pool_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "no_such_task"},
                }
            )
        ],
        game_map=game_map,
    )
    assert out_of_pool_events[0].type == "ActionRejected"
    assert "no_such_task" in event_to_dict(out_of_pool_events[0])["reason"]


def test_vent_sabotage_and_passive_effects_apply() -> None:
    game_map = load_canonical_map()
    base_state = _state()
    state = replace(
        base_state,
        players={
            **dict(base_state.players),
            "p-3": replace(base_state.players["p-3"], room="ADMIN"),
            "p-4": replace(base_state.players["p-4"], room="ADMIN", in_vent=True),
            "dead-admin": replace(
                _player("dead-admin", "CREWMATE", "ADMIN", (2.0, 0.0)),
                alive=False,
            ),
        },
        cooldowns={"p-3": 2},
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            ),
            _action(
                {
                    "type": "sabotage",
                    "actor": "p-3",
                    "payload": {"kind": "lights"},
                }
            ),
        ],
        game_map=game_map,
    )

    assert next_state.players["p-3"].in_vent
    assert next_state.sabotage is not None
    assert next_state.sabotage.kind == "lights"
    assert next_state.sabotage.remaining_ticks == 89
    assert next_state.cooldowns["p-3"] == 1
    assert [event.type for event in events[:2]] == ["VentEntered", "SabotageStarted"]
    assert event_to_dict(events[0])["details"]["witnesses"] == ("p-2",)
    assert event_to_dict(events[0])["details"]["source_witnesses"] == ("p-2",)
    assert event_to_dict(events[0])["details"]["destination_witnesses"] == ("p-2",)


def _active_lights_state(*, remaining_ticks: int = 5) -> WorldState:
    return replace(
        _state(),
        sabotage=SabotageState(
            kind="lights",
            remaining_ticks=remaining_ticks,
            affected_rooms=("ADMIN",),
            active=True,
        ),
    )


def test_timed_sabotage_repair_completes_after_configured_ticks() -> None:
    game_map = load_canonical_map()
    state = _active_lights_state()

    first_state, first_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )
    second_state, second_events = advance_tick(
        first_state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )
    repaired_state, repaired_events = advance_tick(
        second_state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )

    assert first_events[0].type == "SabotageRepairProgressed"
    assert event_to_dict(first_events[0])["details"]["progress"] == 1
    assert first_state.sabotage is not None
    assert first_state.sabotage.repair_progress["ADMIN"] == 1
    assert event_to_dict(second_events[0])["details"]["progress"] == 2
    assert repaired_events[0].type == "SabotageRepaired"
    assert event_to_dict(repaired_events[0])["details"]["required_ticks"] == 3
    assert repaired_state.sabotage is not None
    assert not repaired_state.sabotage.active
    assert not any(event.type == "GameOver" for event in repaired_events)


def test_repair_prevents_same_tick_sabotage_timeout_when_completed() -> None:
    game_map = load_canonical_map()
    sabotage = SabotageState(
        kind="lights",
        remaining_ticks=1,
        affected_rooms=("ADMIN",),
        active=True,
        repair_progress={"ADMIN": 2},
    )
    state = replace(_state(), sabotage=sabotage)

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "lights"},
                }
            )
        ],
        game_map=game_map,
    )

    assert events[0].type == "SabotageRepaired"
    assert next_state.sabotage is not None
    assert not next_state.sabotage.active
    assert not any(event.type == "GameOver" for event in events)


def test_unrepaired_sabotage_timeout_still_wins() -> None:
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        _active_lights_state(remaining_ticks=1),
        [],
        game_map=game_map,
    )

    assert next_state.phase == "GAME_OVER"
    assert events[0].type == "GameOver"
    assert event_to_dict(events[0])["winner"] == "IMPOSTORS"
    assert event_to_dict(events[0])["reason"] == "IMPOSTOR_SABOTAGE"


def _active_reactor_state(
    *, remaining_ticks: int = 5, repair_progress: dict[str, int] | None = None
) -> WorldState:
    # The task-gating reactor sabotage (Task 11.5, DESIGN.md §3.1, §8.3): its map
    # ``SabotageDefinition.gates_tasks`` is true, so an active instance halts the
    # crew task race through both ``_apply_do_task`` and ``_advance_tasks``.
    return replace(
        _state(),
        sabotage=SabotageState(
            kind="reactor",
            remaining_ticks=remaining_ticks,
            affected_rooms=("REACTOR", "ENGINEERING"),
            active=True,
            repair_progress=repair_progress or {},
        ),
    )


def test_gating_sabotage_rejects_do_task_initiation() -> None:
    # Initiation path (DESIGN.md §3.1, §8.3): a fresh ``do_task`` is rejected while
    # a gating sabotage is active -- no progress, no ``TaskProgressed`` event.
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        _active_reactor_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert events[0].type == "ActionRejected"
    assert "sabotage" in event_to_dict(events[0])["reason"]
    assert next_state.tasks["p-2:swipe_card"].progress == 0
    assert not any(event.type == "TaskProgressed" for event in events)


def test_gating_sabotage_suppresses_task_continuation() -> None:
    # Continuation path (DESIGN.md §3.1, §8.3): a task accepted before the sabotage
    # stops accruing progress while the gate is active -- ``_advance_tasks`` skips
    # the increment and emits no ``TaskProgressed`` event.
    game_map = load_canonical_map()
    started_state, _ = advance_tick(
        _long_task_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )
    assert started_state.tasks["p-2:swipe_card"].progress == 1

    gated_state = replace(
        started_state,
        sabotage=SabotageState(
            kind="reactor",
            remaining_ticks=5,
            affected_rooms=("REACTOR", "ENGINEERING"),
            active=True,
        ),
    )

    next_state, events = advance_tick(gated_state, [], game_map=game_map)

    assert next_state.tasks["p-2:swipe_card"].progress == 1
    assert not any(event.type == "TaskProgressed" for event in events)


def test_non_gating_lights_does_not_gate_task_progress() -> None:
    # The non-gating ``lights`` sabotage leaves the task race byte-identical to
    # today: a ``do_task`` still advances and completes (DESIGN.md §8.3).
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        _active_lights_state(),
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.tasks["p-2:swipe_card"].completed
    assert any(event.type == "TaskCompleted" for event in events)


def test_repair_clears_task_gate() -> None:
    # Repairing the gating sabotage clears the gate: the same ``do_task`` that was
    # rejected while active resumes progressing once the sabotage is inactive.
    game_map = load_canonical_map()
    players = dict(_state().players)
    players["p-2"] = replace(players["p-2"], room="ENGINEERING")
    state = replace(
        _state(),
        players=players,
        tasks={
            "p-2:align_engine_output": _task(
                "align_engine_output", "p-2", "ENGINEERING", required_ticks=2
            )
        },
        sabotage=SabotageState(
            kind="reactor",
            remaining_ticks=5,
            affected_rooms=("REACTOR", "ENGINEERING"),
            active=True,
            repair_progress={"ENGINEERING": 2},
        ),
    )

    gated_state, gated_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "align_engine_output"},
                }
            )
        ],
        game_map=game_map,
    )
    assert gated_events[0].type == "ActionRejected"
    assert gated_state.tasks["p-2:align_engine_output"].progress == 0

    repaired_state, repaired_events = advance_tick(
        gated_state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "reactor"},
                }
            )
        ],
        game_map=game_map,
    )
    assert repaired_events[0].type == "SabotageRepaired"
    assert repaired_state.sabotage is not None
    assert not repaired_state.sabotage.active

    done_state, done_events = advance_tick(
        repaired_state,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "align_engine_output"},
                }
            )
        ],
        game_map=game_map,
    )
    assert done_state.tasks["p-2:align_engine_output"].progress == 1
    assert any(event.type == "TaskProgressed" for event in done_events)


def test_reactor_timeout_yields_impostor_sabotage_win() -> None:
    # The dormant §3.5 IMPOSTOR_SABOTAGE win fires end-to-end under the short
    # reactor timer: left to ``remaining_ticks==0`` with ``active`` true, the
    # crew loses (engine/win_conditions.py:30-35 -- no win-condition edit needed).
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        _active_reactor_state(remaining_ticks=1),
        [],
        game_map=game_map,
    )

    assert next_state.phase == "GAME_OVER"
    assert events[0].type == "GameOver"
    assert event_to_dict(events[0])["winner"] == "IMPOSTORS"
    assert event_to_dict(events[0])["reason"] == "IMPOSTOR_SABOTAGE"


def test_reactor_same_tick_repair_saves_crew() -> None:
    # A repair completing on the timer-expiry tick still saves the crew: the
    # repair sets ``active=False`` in step 1, so the §3.5 sabotage win never fires.
    game_map = load_canonical_map()
    players = dict(_state().players)
    players["p-2"] = replace(players["p-2"], room="ENGINEERING")
    state = replace(
        _state(),
        players=players,
        sabotage=SabotageState(
            kind="reactor",
            remaining_ticks=1,
            affected_rooms=("REACTOR", "ENGINEERING"),
            active=True,
            repair_progress={"ENGINEERING": 2},
        ),
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": "p-2",
                    "payload": {"kind": "reactor"},
                }
            )
        ],
        game_map=game_map,
    )

    assert events[0].type == "SabotageRepaired"
    assert next_state.sabotage is not None
    assert not next_state.sabotage.active
    assert not any(event.type == "GameOver" for event in events)


@pytest.mark.parametrize(
    ("state", "action_actor", "kind", "match"),
    (
        (_state(), "p-2", "lights", "no active sabotage"),
        (_active_lights_state(), "p-1", "lights", "repair room"),
        (_active_lights_state(), "p-2", "unknown", "unknown sabotage"),
        (
            replace(
                _active_lights_state(),
                players={
                    **dict(_active_lights_state().players),
                    "p-2": replace(_active_lights_state().players["p-2"], in_vent=True),
                },
            ),
            "p-2",
            "lights",
            "while in vent",
        ),
    ),
)
def test_invalid_sabotage_repairs_are_rejected(
    state: WorldState,
    action_actor: str,
    kind: str,
    match: str,
) -> None:
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "repair_sabotage",
                    "actor": action_actor,
                    "payload": {"kind": kind},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.sabotage == state.sabotage or state.sabotage is not None
    assert events[0].type == "ActionRejected"
    assert match in event_to_dict(events[0])["reason"]


def test_vent_can_exit_through_connected_destination_vent() -> None:
    game_map = load_canonical_map()
    base_state = _state()
    state = replace(
        base_state,
        players={
            **dict(base_state.players),
            "p-3": replace(base_state.players["p-3"], room="ADMIN"),
            "p-4": replace(base_state.players["p-4"], room="REACTOR"),
        },
    )

    in_vent_state, enter_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )
    exited_state, exit_events = advance_tick(
        in_vent_state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "REACTOR_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    assert in_vent_state.players["p-3"].room == "ADMIN"
    assert in_vent_state.players["p-3"].in_vent
    assert enter_events[0].type == "VentEntered"
    assert exited_state.players["p-3"].room == "REACTOR"
    assert not exited_state.players["p-3"].in_vent
    assert exit_events[0].type == "VentExited"
    assert event_to_dict(exit_events[0])["details"]["source_vent_id"] == "ADMIN_VENT"
    assert (
        event_to_dict(exit_events[0])["details"]["destination_vent_id"]
        == "REACTOR_VENT"
    )
    assert event_to_dict(exit_events[0])["details"]["witnesses"] == (
        "p-2",
        "p-4",
    )
    assert event_to_dict(exit_events[0])["details"]["source_witnesses"] == ("p-2",)
    assert event_to_dict(exit_events[0])["details"]["destination_witnesses"] == ("p-4",)


def test_vent_rejects_unconnected_destination_vent() -> None:
    game_map = load_canonical_map()
    state = replace(
        _state(),
        players={
            **dict(_state().players),
            "p-3": replace(_state().players["p-3"], room="ADMIN"),
        },
    )
    in_vent_state, _ = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    next_state, events = advance_tick(
        in_vent_state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-3",
                    "payload": {"vent_id": "STORAGE_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["p-3"].room == "ADMIN"
    assert next_state.players["p-3"].in_vent
    assert events[0].type == "ActionRejected"


def test_report_and_emergency_transition_to_meeting() -> None:
    game_map = load_canonical_map()
    body = BodyState(
        id="body-p-2-0",
        player_id="p-2",
        room="CAFETERIA",
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    report_state = replace(_state(), bodies={body.id: body})

    next_state, report_events = advance_tick(
        report_state,
        [
            _action(
                {
                    "type": "report",
                    "actor": "p-1",
                    "payload": {"body_id": "body-p-2-0"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.bodies["body-p-2-0"].discovered_by == "p-1"
    assert any(event.type == "MeetingTriggered" for event in report_events)

    emergency_state, emergency_events = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert emergency_state.phase == "MEETING"
    assert emergency_state.emergency_uses["p-1"] == 1
    assert any(event.type == "MeetingTriggered" for event in emergency_events)


def test_meeting_trigger_interrupts_tick_before_passive_effects_and_win_checks() -> (
    None
):
    game_map = load_canonical_map()
    body = BodyState(
        id="body-p-2-0",
        player_id="p-2",
        room="CAFETERIA",
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    state = replace(
        _state(),
        bodies={body.id: body},
        sabotage=SabotageState(
            kind="lights",
            remaining_ticks=1,
            affected_rooms=("ADMIN",),
            active=True,
        ),
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "report",
                    "actor": "p-1",
                    "payload": {"body_id": "body-p-2-0"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.tick == state.tick
    assert next_state.rng_state == state.rng_state
    assert next_state.sabotage is not None
    assert next_state.sabotage.remaining_ticks == 1
    assert [event.type for event in events] == ["MeetingTriggered"]


def test_emergency_trigger_interrupts_tick_before_passive_effects_and_win_checks() -> (
    None
):
    game_map = load_canonical_map()
    state = replace(
        _state(),
        sabotage=SabotageState(
            kind="lights",
            remaining_ticks=1,
            affected_rooms=("ADMIN",),
            active=True,
        ),
    )

    next_state, events = advance_tick(
        state,
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "MEETING"
    assert next_state.tick == state.tick
    assert next_state.rng_state == state.rng_state
    assert next_state.sabotage is not None
    assert next_state.sabotage.remaining_ticks == 1
    assert [event.type for event in events] == ["MeetingTriggered"]


def test_emergency_requires_actor_in_button_room() -> None:
    game_map = load_canonical_map()

    next_state, events = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "p-2", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "PLAY"
    assert "p-2" not in next_state.emergency_uses
    assert events[0].type == "ActionRejected"
    assert "emergency button room" in event_to_dict(events[0])["reason"]


def test_emergency_rejects_actor_in_vent() -> None:
    game_map = load_canonical_map()
    state = _state()
    players = dict(state.players)
    players["p-1"] = replace(players["p-1"], in_vent=True)

    next_state, events = advance_tick(
        replace(state, players=players),
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "PLAY"
    assert "p-1" not in next_state.emergency_uses
    assert next_state.players["p-1"].in_vent
    assert events[0].type == "ActionRejected"
    assert "while in vent" in event_to_dict(events[0])["reason"]


def test_advance_tick_rejects_non_play_phases() -> None:
    game_map = load_canonical_map()
    with pytest.raises(ValueError, match="MEETING"):
        advance_tick(replace(_state(), phase="MEETING"), [], game_map=game_map)
    with pytest.raises(ValueError, match="GAME_OVER"):
        advance_tick(replace(_state(), phase="GAME_OVER"), [], game_map=game_map)


def test_advance_tick_rejects_mismatched_state_map() -> None:
    game_map = load_canonical_map()

    with pytest.raises(ValueError, match="unsupported map id"):
        advance_tick(replace(_state(), map="other_map"), [], game_map=game_map)


def test_advance_tick_uses_supplied_map_without_loading_canonical_map(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    game_map = load_canonical_map()

    def fail_if_loaded() -> None:
        pytest.fail("advance_tick must not load the canonical map")

    monkeypatch.setattr("engine.world.load_canonical_map", fail_if_loaded)

    next_state, events = advance_tick(
        _state(),
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-1",
                    "payload": {"to_room": "UPPER_HALL"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.players["p-1"].room == "UPPER_HALL"
    assert any(event.type == "Moved" for event in events)


def test_repeated_emergency_use_is_rejected() -> None:
    game_map = load_canonical_map()
    meeting_state, _ = advance_tick(
        _state(),
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )
    resumed_state = replace(meeting_state, phase="PLAY")

    next_state, events = advance_tick(
        resumed_state,
        [_action({"type": "emergency", "actor": "p-1", "payload": {}})],
        game_map=game_map,
    )

    assert next_state.phase == "PLAY"
    assert next_state.emergency_uses["p-1"] == 1
    assert events[0].type == "ActionRejected"


def test_dead_crewmate_incomplete_task_is_dropped_and_crew_can_still_win() -> None:
    """R-5 (DESIGN.md §3.5 `dropped` rule).

    When a crewmate dies with an incomplete task, that task is removed
    from ``state.tasks`` so crew victory remains reachable via the
    remaining alive-owned tasks. Already-completed tasks owned by the
    dead crewmate stay so they continue to count toward ``crew_tasks_done``.
    """

    game_map = load_canonical_map()
    state = _state()
    players = dict(state.players)
    # Add a second crewmate co-located with the impostor in CAFETERIA so
    # the kill is valid, and three crewmate-owned tasks: one incomplete
    # for the soon-to-die victim, one already complete for the victim
    # (must survive removal), and one alive-owned task in ADMIN that the
    # crew will complete after the kill.
    players["victim"] = _player("victim", "CREWMATE", "CAFETERIA", (2.0, 0.0))
    state = replace(
        state,
        players=players,
        tasks={
            "p-2:swipe_card": _task("swipe_card", "p-2", "ADMIN"),
            "victim:victim_incomplete": _task(
                "victim_incomplete", "victim", "CAFETERIA", required_ticks=1
            ),
            "victim:victim_done": replace(
                _task("victim_done", "victim", "CAFETERIA", required_ticks=1),
                progress=1,
                completed=True,
            ),
        },
    )

    after_kill, kill_events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "kill",
                    "actor": "p-3",
                    "payload": {"target": "victim"},
                }
            )
        ],
        game_map=game_map,
    )

    assert not after_kill.players["victim"].alive
    assert any(event.type == "Killed" for event in kill_events)
    # (a) Victim's incomplete task instance is gone.
    assert "victim:victim_incomplete" not in after_kill.tasks
    # (b) Victim's already-completed task instance remains and still counts.
    assert "victim:victim_done" in after_kill.tasks
    assert after_kill.tasks["victim:victim_done"].completed
    # The alive-owned instance survives unchanged.
    assert "p-2:swipe_card" in after_kill.tasks
    assert not after_kill.tasks["p-2:swipe_card"].completed

    # (c) Completing the surviving alive-owned task reaches CREWMATE_TASKS.
    final_state, final_events = advance_tick(
        after_kill,
        [
            _action(
                {
                    "type": "do_task",
                    "actor": "p-2",
                    "payload": {"task_id": "swipe_card"},
                }
            )
        ],
        game_map=game_map,
    )

    assert final_state.phase == "GAME_OVER"
    game_over = next(event for event in final_events if event.type == "GameOver")
    assert event_to_dict(game_over)["winner"] == "CREWMATES"
    assert event_to_dict(game_over)["reason"] == "CREWMATE_TASKS"


def test_kill_removing_last_incomplete_task_triggers_crew_win_same_tick() -> None:
    """R-2 (DESIGN.md §3.5 same-tick consequence of the ``dropped`` rule).

    When an impostor kill removes the last incomplete task from
    ``state.tasks`` and every surviving task is already completed,
    ``advance_tick`` resolves crew victory on the same tick. Pin the
    consequence so a future refactor of the tick loop cannot silently
    regress it.
    """

    game_map = load_canonical_map()
    state = _state()
    players = dict(state.players)
    players["victim"] = _player("victim", "CREWMATE", "CAFETERIA", (2.0, 0.0))
    # Tasks: one incomplete owned by the about-to-die victim (will be
    # dropped on kill) and one already-completed task owned by an alive
    # crewmate. After the kill, ``state.tasks`` contains only the
    # completed task, so ``completed_tasks == total_tasks > 0`` and the
    # CREWMATE_TASKS branch fires inside the same ``advance_tick`` call.
    state = replace(
        state,
        players=players,
        tasks={
            "p-2:swipe_card_done": replace(
                _task("swipe_card_done", "p-2", "ADMIN", required_ticks=1),
                progress=1,
                completed=True,
            ),
            "victim:victim_incomplete": _task(
                "victim_incomplete", "victim", "CAFETERIA", required_ticks=1
            ),
        },
    )

    next_state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "kill",
                    "actor": "p-3",
                    "payload": {"target": "victim"},
                }
            )
        ],
        game_map=game_map,
    )

    assert next_state.phase == "GAME_OVER"
    game_over_events = [event for event in events if event.type == "GameOver"]
    assert len(game_over_events) == 1
    assert event_to_dict(game_over_events[0])["winner"] == "CREWMATES"
    assert event_to_dict(game_over_events[0])["reason"] == "CREWMATE_TASKS"


def test_kill_reaching_parity_with_last_task_completion_yields_impostor_win() -> None:
    """DESIGN.md §3.5 ordering: when a kill simultaneously reaches
    impostor parity AND removes the last incomplete task, the impostor
    wins (parity is checked before crew tasks). Counterpart to
    ``test_kill_removing_last_incomplete_task_triggers_crew_win_same_tick``,
    which exercises the same kill mechanic without reaching parity.
    """

    game_map = load_canonical_map()
    state = _state()
    # ``_state()`` supplies p-1/p-2/p-4 crewmates + p-3 impostor; override
    # to a tight 1 impostor + 2 crewmate setup so the kill reaches parity.
    players = {
        "p-3": _player("p-3", "IMPOSTOR", "CAFETERIA", (0.0, 0.0)),
        "p-1": _player("p-1", "CREWMATE", "ADMIN", (1.0, 0.0)),
        "victim": _player("victim", "CREWMATE", "CAFETERIA", (2.0, 0.0)),
    }
    state = replace(
        state,
        players=players,
        cooldowns={"p-3": 0},
        tasks={
            "p-1:swipe_card_done": replace(
                _task("swipe_card_done", "p-1", "ADMIN", required_ticks=1),
                progress=1,
                completed=True,
            ),
            "victim:victim_incomplete": _task(
                "victim_incomplete", "victim", "CAFETERIA", required_ticks=1
            ),
        },
    )

    next_state, events = advance_tick(
        state,
        [_action({"type": "kill", "actor": "p-3", "payload": {"target": "victim"}})],
        game_map=game_map,
    )

    assert next_state.phase == "GAME_OVER"
    game_over_events = [event for event in events if event.type == "GameOver"]
    assert len(game_over_events) == 1
    assert event_to_dict(game_over_events[0])["winner"] == "IMPOSTORS"
    assert event_to_dict(game_over_events[0])["reason"] == "IMPOSTOR_PARITY"
