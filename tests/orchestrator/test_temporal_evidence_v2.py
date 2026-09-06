"""Real canonical seed/actions → observation → prompt → recorded viewer controls."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agents.memory.beliefs import BeliefState, apply_observation_rules
from agents.memory.evidence_context import evidence_context_lines
from agents.memory.store import render_for_prompt
from api.replay_loader import ReplayLoader
from engine.world import load_canonical_map
from eval.leak_scan import _reconstruct_factory_records, assert_no_factory_packet_leaks
from experiments.deduction_scenarios import (
    ScenarioCase,
    ScriptedDeductionProvider,
    run_case,
)
from observation.packet import BodyView, EventObservationBatch
from observation.service import ObservationService
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import MeetingReplayEntry, ReplayEntry, read_all_entries
from tests.observation.test_service import _base_world_state


def _config() -> RecordedExperimentConfig:
    return RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        public_account_version=1,
        attributed_testimony_version=1,
    )


@pytest.mark.parametrize(
    "case",
    [
        "honest",
        "impossible_account",
        "insufficient_evidence",
        "already_known_dead",
        "witnessed_kill",
        "witnessed_vent",
    ],
)
def test_real_cases_preserve_entitlement_clock_and_opening_reader_parity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: ScenarioCase
) -> None:
    capture = run_case(tmp_path, case=case, experiment_config=_config())
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1})
    )
    assert capture.result.final_state.phase == "GAME_OVER"
    entries = read_all_entries(capture.replay_path)
    meetings = [row for row in entries if isinstance(row, MeetingReplayEntry)]
    assert [row.tick for row in meetings] == (
        [5, 8]
        if case == "already_known_dead"
        else [capture.definition.expected_report_tick]
    )
    for meeting_row in meetings:
        assert all(not turn.annotations for turn in meeting_row.transcript.turns)
    for row in entries:
        if isinstance(row, ReplayEntry):
            assert row.temporal_observation_version == 2
    provider = capture.provider
    assert isinstance(provider, ScriptedDeductionProvider)
    assert provider.prompts
    assert all("body-p-1-4" not in prompt for _, prompt in provider.prompts)
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "0")
    monkeypatch.setenv("AILIBI_EVIDENCE_REASONING", "0")
    loader = ReplayLoader(tmp_path)
    for meeting in meetings:
        opener = meeting.triggered_by
        view = loader.get_meeting_memory("headless-seed-1", meeting.meeting_id, opener)
        assert any(
            agent == opener and view.rendered_memory_text in prompt
            for agent, prompt in provider.prompts
        )
        assert "START of each tick" in view.rendered_memory_text
    witness_events = [
        event
        for agent in capture.agents.values()
        for event in agent.memory.episodic.recent(since_tick=0)
        if event.type == "saw_player"
        and event.payload.get("action") in ("kill", "vent")
    ]
    if case in ("witnessed_kill", "witnessed_vent"):
        assert any(
            row.payload.get("action")
            == ("kill" if case == "witnessed_kill" else "vent")
            for row in witness_events
        )
    else:
        assert witness_events == []
    event_batches: list[EventObservationBatch] = []
    records = _reconstruct_factory_records(
        capture.replay_path,
        game_map=load_canonical_map(),
        seed=1,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        audit_dir=tmp_path,
        event_records=event_batches,
    )
    assert event_batches
    assert_no_factory_packet_leaks(records)
    with pytest.raises(FileExistsError):
        run_case(tmp_path, case=case, experiment_config=_config())


@pytest.mark.parametrize(
    "case", ["honest", "impossible_account", "insufficient_evidence"]
)
def test_actual_placements_support_only_conditional_account_checks(
    tmp_path: Path, case: ScenarioCase
) -> None:
    capture = run_case(tmp_path, case=case, experiment_config=_config())
    memory = capture.agents["p-2"].memory
    lines = evidence_context_lines(memory, own_agent_id="p-2", teammate_ids=frozenset())
    account = [line for line in lines if "claim by p-4" in line]
    assert account
    if case == "impossible_account":
        assert any(
            "walking cannot reconcile" in line
            and "WEST_HALL at tick 5" in line
            and "REACTOR at tick 5" in line
            for line in account
        )
    elif case == "honest":
        assert any(
            "a walk fits" in line and "does not establish innocence" in line
            for line in account
        )
    else:
        assert not any("walking cannot reconcile" in line for line in account)
        assert any("cannot establish" in line for line in account)
    # Later return sightings do not replace this earlier movement interval.
    if case != "insufficient_evidence":
        assert any(
            "ADMIN at tick 3" in line and "WEST_HALL at tick 5" in line
            for line in lines
        )
    text = render_for_prompt(memory, token_budget=10000)
    assert "moved from WEST_HALL, last seen there" not in text
    assert "Separated sightings do not establish a watched transition" in text


def test_public_death_bound_filters_only_post_announcement_proximity(
    tmp_path: Path,
) -> None:
    # An explicit adversarial rule input isolates the reviewed scalar defect.
    # It is not an observation emitted by the canonical scenario above.
    service = ObservationService(
        game_map=load_canonical_map(), audit_log_path=tmp_path / "audit"
    )
    try:
        packet = service.build_packet(
            world_state=_base_world_state(), agent_id="p-2", engine_events=()
        ).model_copy(
            update={
                "tick": 8,
                "visible_bodies": (
                    BodyView(id="body-p-1", victim_id="p-1", room="ADMIN"),
                ),
            }
        )
        legacy = apply_observation_rules(
            BeliefState(),
            observation=packet,
            previous_visible_bodies=set(),
            recent_co_presence={"ADMIN": [(6, "p-3")]},
        )
        corrected = apply_observation_rules(
            BeliefState(),
            observation=packet,
            previous_visible_bodies=set(),
            recent_co_presence={"ADMIN": [(6, "p-3")]},
            known_dead_by={"p-1": 5},
        )
        still_possible = apply_observation_rules(
            BeliefState(),
            observation=packet,
            previous_visible_bodies=set(),
            recent_co_presence={"ADMIN": [(6, "p-3")]},
            known_dead_by={"p-1": 7},
        )
        assert legacy.view("p-3").suspicion == pytest.approx(0.7)
        assert corrected.view("p-3").suspicion == pytest.approx(0.5)
        assert still_possible.view("p-3").suspicion == pytest.approx(0.7)
    finally:
        service.close()


def test_old_profiles_keep_original_breadcrumb_interpretation(tmp_path: Path) -> None:
    capture = run_case(
        tmp_path,
        case="honest",
        temporal_version=1,
        experiment_config=RecordedExperimentConfig(evidence_reasoning_version=1),
    )
    text = render_for_prompt(capture.agents["p-2"].memory, token_budget=10000)
    assert "moved from WEST_HALL" in text
    assert "START of each tick" not in text
    assert all(
        row.temporal_observation_version == 1
        for row in read_all_entries(capture.replay_path)
        if isinstance(row, ReplayEntry)
    )
