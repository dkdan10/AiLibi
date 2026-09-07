"""Actual legal movement and two meetings retain a public reset boundary."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from agents.memory.evidence_context import evidence_context_lines
from agents.memory.store import AgentMemory
from api.replay_loader import ReplayLoader
from experiments import deduction_scenarios
from experiments.deduction_scenarios import (
    ScenarioStep,
    ScriptedDeductionProvider,
    run_case,
    scenario_definition,
)
from observation.action_intent import ActionIntent
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import MeetingReplayEntry, read_all_entries


def test_public_reset_does_not_create_an_impossible_walk_or_erase_later_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)
    actions = [
        (tick, player, "move", {"to_room": room})
        for tick, room in ((0, "UPPER_HALL"), (1, "ADMIN"))
        for player in ("p-2", "p-4")
    ] + [
        (2, "p-3", "emergency", {"reason": "Compare routes."}),
        (6, "p-1", "emergency", {"reason": "Check the later account."}),
    ]
    steps = tuple(
        ScenarioStep(
            tick=tick,
            action=adapter.validate_python(
                {"actor": player, "type": kind, "payload": payload}
            ),
        )
        for tick, player, kind, payload in actions
    )
    # The engine executes only legal moves. A scripted claim supplies the later
    # impossible account, independently of the earlier public relocation.
    definition = scenario_definition("already_known_dead").model_copy(
        update={"steps": steps, "claimed_room": "REACTOR"}
    )
    monkeypatch.setattr(
        deduction_scenarios, "scenario_definition", lambda _: definition
    )
    capture = run_case(
        tmp_path,
        case="already_known_dead",
        experiment_config=RecordedExperimentConfig(
            format_version=2,
            evidence_reasoning_version=2,
            public_account_version=1,
            attributed_testimony_version=1,
            meeting_reset="hub_with_grace",
        ),
    )
    entries = read_all_entries(capture.replay_path)
    meetings = [row for row in entries if isinstance(row, MeetingReplayEntry)]
    assert [row.tick for row in meetings] == [2, 6]
    memory = capture.agents["p-2"].memory
    regroups = [
        row
        for row in memory.episodic.recent(since_tick=0)
        if row.type == "public_regroup"
    ]
    assert [row.tick for row in regroups] == [3, 7]
    lines = evidence_context_lines(memory, own_agent_id="p-2", teammate_ids=frozenset())
    assert any(
        "p-4" in line and "tick 2 to tick 3" in line and "public regroup" in line
        for line in lines
    )
    assert not any(
        "ADMIN at tick 2" in line
        and "CAFETERIA at tick 3" in line
        and "walking cannot reconcile" in line
        for line in lines
    )
    omitted_boundary = AgentMemory(
        evidence_reasoning_version=2, public_map=memory.public_map
    )
    for row in memory.episodic.recent(since_tick=0):
        if row.type != "public_regroup":
            omitted_boundary.episodic.append(row)
    assert any(
        "ADMIN at tick 2" in line
        and "CAFETERIA at tick 3" in line
        and "walking cannot reconcile" in line
        for line in evidence_context_lines(
            omitted_boundary, own_agent_id="p-2", teammate_ids=frozenset()
        )
    )
    assert any(
        "CAFETERIA at tick 5" in line
        and "REACTOR at tick 5" in line
        and "walking cannot reconcile" in line
        and "Assuming the claimed placement is accurate" in line
        for line in lines
    )
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1})
    )
    opener = meetings[1].triggered_by
    view = ReplayLoader(tmp_path).get_meeting_memory(
        "headless-seed-1", meetings[1].meeting_id, opener
    )
    assert "Public regroup at the start of tick 3" in view.rendered_memory_text
    assert isinstance(capture.provider, ScriptedDeductionProvider)
    assert any(
        agent == opener and view.rendered_memory_text in prompt
        for agent, prompt in capture.provider.prompts
    )
