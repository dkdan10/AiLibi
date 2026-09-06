"""Compare the allocation rule through actual kills with conservation controls."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

import pytest

from engine.actions import KillAction
from engine.entities import TaskState
from engine.tick import RedistributionPolicy, advance_tick
from engine.world import WorldState, load_canonical_map
from orchestrator.replay import _state_hash
from orchestrator.seeder import seed_initial_state


def _task(owner: str, task_id: str, *, progress: int = 0) -> TaskState:
    definition = load_canonical_map().tasks[task_id]
    return TaskState(
        id=f"{owner}:{task_id}",
        owner=owner,
        map_task_id=task_id,
        room=definition.room,
        progress=progress,
        required_ticks=definition.duration_ticks,
        completed=progress == definition.duration_ticks,
    )


def _world() -> WorldState:
    game_map = load_canonical_map()
    state = seed_initial_state(seed=1, game_map=game_map, num_players=5)
    tasks = (
        _task("p-1", "start_reactor"),
        _task("p-2", "align_engine_output", progress=7),
        _task("p-3", "submit_scan", progress=7),
        _task("p-4", "upload_logs", progress=4),
    )
    return replace(
        state,
        players={
            pid: replace(player, role="IMPOSTOR" if pid == "p-5" else "CREWMATE")
            for pid, player in state.players.items()
        },
        tasks={task.id: task for task in tasks},
        cooldowns={"p-5": 0},
    )


def _kill(state: WorldState, policy: RedistributionPolicy) -> WorldState:
    return advance_tick(
        state,
        [
            KillAction.model_validate(
                {"type": "kill", "actor": "p-5", "payload": {"target": "p-3"}}
            )
        ],
        game_map=load_canonical_map(),
        redistribution_policy=policy,
    )[0]


def test_actual_kill_moves_partial_work_to_the_least_busy_eligible_recipient() -> None:
    state = _world()
    baseline = _kill(state, "lowest_id")
    candidate = _kill(state, "least_remaining_work")
    assert "p-1:submit_scan" in baseline.tasks
    assert "p-2:submit_scan" in candidate.tasks
    assert candidate.tasks["p-2:submit_scan"].progress == 7
    assert candidate.tasks["p-2:submit_scan"].required_ticks == 10
    assert candidate.rng_state == baseline.rng_state
    assert candidate.players == baseline.players
    assert sum(t.required_ticks - t.progress for t in candidate.tasks.values()) == sum(
        t.required_ticks - t.progress for t in state.tasks.values()
    )
    assert _state_hash(candidate) == _state_hash(_kill(state, "least_remaining_work"))
    assert _state_hash(candidate) != _state_hash(baseline)


def test_completed_duplicate_excludes_an_otherwise_less_busy_recipient() -> None:
    state = _world()
    duplicate = _task("p-2", "submit_scan", progress=10)
    state = replace(state, tasks={**state.tasks, duplicate.id: duplicate})
    after = _kill(state, "least_remaining_work")
    assert after.tasks[duplicate.id] == duplicate
    assert after.tasks["p-4:submit_scan"].progress == 7


def test_each_allocation_recomputes_work_and_ties_use_the_player_id() -> None:
    state = _world()
    second = _task("p-3", "swipe_card")
    state = replace(state, tasks={**state.tasks, second.id: second})
    after = _kill(state, "least_remaining_work")
    assert "p-2:submit_scan" in after.tasks
    assert "p-4:swipe_card" in after.tasks

    task = state.tasks["p-4:upload_logs"]
    tied = replace(state, tasks={**state.tasks, task.id: replace(task, progress=5)})
    assert "p-2:submit_scan" in _kill(tied, "least_remaining_work").tasks


def test_no_eligible_recipient_preserves_the_existing_drop_rule() -> None:
    state = _world()
    completed = [
        _task(pid, "submit_scan", progress=10) for pid in ("p-1", "p-2", "p-4")
    ]
    state = replace(state, tasks={**state.tasks, **{t.id: t for t in completed}})
    after = _kill(state, "least_remaining_work")
    assert "p-3:submit_scan" not in after.tasks
    assert all(after.tasks[t.id] == t for t in completed)
    assert len(after.tasks) == len(state.tasks) - 1


def test_unknown_policy_and_incompatible_task_rule_raise() -> None:
    state = _world()
    with pytest.raises(ValueError, match="unknown redistribution policy"):
        _kill(state, cast(RedistributionPolicy, "random"))
    with pytest.raises(ValueError, match="requires the redistribute"):
        advance_tick(
            state,
            [],
            game_map=load_canonical_map().model_copy(update={"dead_task_rule": "drop"}),
            redistribution_policy="least_remaining_work",
        )


def test_ejection_uses_the_same_workload_rule_before_optional_regrouping() -> None:
    from meetings.schemas import MeetingResult, MeetingTranscript
    from orchestrator.game import apply_meeting_result

    state = replace(_world(), phase="MEETING")
    result = MeetingResult(
        meeting_id="m",
        triggered_by="p-1",
        trigger_tick=state.tick,
        outcome="EJECTED",
        ejected_player_id="p-3",
        ballots=(),
        transcript=MeetingTranscript(turns=()),
    )
    baseline, _ = apply_meeting_result(state, result, game_map=load_canonical_map())
    candidate, _ = apply_meeting_result(
        state,
        result,
        game_map=load_canonical_map(),
        redistribution_policy="least_remaining_work",
        meeting_reset="hub_with_grace",
    )
    assert "p-1:submit_scan" in baseline.tasks
    assert "p-2:submit_scan" in candidate.tasks
    assert not candidate.players["p-3"].alive
    assert candidate.phase == "PLAY" and candidate.tick == state.tick + 1
    assert candidate.rng_state == baseline.rng_state
    assert candidate.cooldowns == {"p-5": load_canonical_map().kill_cooldown_ticks}
