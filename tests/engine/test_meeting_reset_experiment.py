"""Regrouping resets all coupled spatial state and preserves ongoing resources."""

from __future__ import annotations

from dataclasses import replace

import pytest

from engine.actions import DoTaskAction, KillAction
from engine.entities import BodyState, SabotageState
from engine.meeting_reset import regroup_after_meeting
from engine.tick import advance_tick
from engine.world import load_canonical_map
from orchestrator.seeder import seed_initial_state


def test_regrouping_clears_every_corpse_and_vent_without_resetting_progress() -> None:
    game_map = load_canonical_map()
    state = seed_initial_state(seed=2, game_map=game_map, num_players=6)
    players = dict(state.players)
    players["p-1"] = replace(
        players["p-1"],
        room="MEDBAY",
        in_vent=True,
        role="IMPOSTOR",
        last_action=DoTaskAction.model_validate(
            {"type": "do_task", "actor": "p-1", "payload": {"task_id": "submit_scan"}}
        ),
    )
    for pid in ("p-2", "p-3", "p-4", "p-5", "p-6"):
        players[pid] = replace(players[pid], role="CREWMATE")
    players["p-5"] = replace(players["p-5"], alive=False)
    players["p-6"] = replace(players["p-6"], alive=False)
    bodies = {
        f"body-{pid}": BodyState(
            id=f"body-{pid}",
            player_id=pid,
            room="MEDBAY",
            position=(0.0, 0.0),
            killed_by="p-1",
            discovered_by="p-2" if pid == "p-5" else None,
        )
        for pid in ("p-5", "p-6")
    }
    sabotage = SabotageState(
        kind="reactor",
        remaining_ticks=4,
        affected_rooms=(),
        active=True,
        repair_progress={"REACTOR": 1},
    )
    state = replace(
        state,
        phase="MEETING",
        players=players,
        bodies=bodies,
        cooldowns={"p-1": 0},
        sabotage=sabotage,
        emergency_uses={"p-2": 1},
    )
    after = regroup_after_meeting(state, game_map=game_map)
    assert after.bodies == {}
    assert all(
        not player.in_vent and player.last_action is None
        for player in after.players.values()
    )
    assert {p.room for p in after.players.values() if p.alive} == {
        game_map.meeting.room
    }
    assert len({p.position for p in after.players.values() if p.alive}) == 4
    assert after.cooldowns == {"p-1": game_map.kill_cooldown_ticks}
    assert after.tasks == state.tasks
    assert after.sabotage == sabotage
    assert after.emergency_uses == state.emergency_uses
    assert after.tick == state.tick and after.rng_state == state.rng_state
    assert len(state.bodies) == 2 and state.players["p-1"].in_vent

    resumed = replace(after, phase="PLAY", sabotage=None)
    action = KillAction.model_validate(
        {"type": "kill", "actor": "p-1", "payload": {"target": "p-2"}}
    )
    for _ in range(game_map.kill_cooldown_ticks):
        resumed, events = advance_tick(resumed, [action], game_map=game_map)
        assert resumed.players["p-2"].alive
        assert any(event.type == "ActionRejected" for event in events)
    resumed, events = advance_tick(resumed, [action], game_map=game_map)
    assert not resumed.players["p-2"].alive
    assert any(event.type == "Killed" for event in events)


def test_regrouping_cannot_run_as_an_arbitrary_play_tick_mutation() -> None:
    game_map = load_canonical_map()
    state = seed_initial_state(seed=2, game_map=game_map, num_players=5)
    with pytest.raises(ValueError, match="requires"):
        regroup_after_meeting(state, game_map=game_map)


def test_terminal_ejection_is_not_followed_by_an_unnecessary_reset() -> None:
    from meetings.schemas import MeetingResult, MeetingTranscript
    from orchestrator.game import apply_meeting_result

    game_map = load_canonical_map()
    state = seed_initial_state(seed=2, game_map=game_map, num_players=5)
    impostor = next(
        pid for pid, player in state.players.items() if player.role == "IMPOSTOR"
    )
    state = replace(
        state,
        phase="MEETING",
        players={
            pid: replace(player, room="MEDBAY") for pid, player in state.players.items()
        },
    )
    result = MeetingResult(
        meeting_id="m",
        triggered_by="p-1",
        trigger_tick=state.tick,
        outcome="EJECTED",
        ejected_player_id=impostor,
        ballots=(),
        transcript=MeetingTranscript(turns=()),
    )
    baseline = apply_meeting_result(state, result, game_map=game_map)
    candidate = apply_meeting_result(
        state, result, game_map=game_map, meeting_reset="hub_with_grace"
    )
    assert candidate == baseline
    assert candidate[0].phase == "GAME_OVER"
    assert candidate[0].tick == state.tick and candidate[0].rng_state == state.rng_state
    assert {player.room for player in candidate[0].players.values()} == {"MEDBAY"}
