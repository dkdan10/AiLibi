"""Recorded memory behavior and live stamps cannot follow a later env change."""

from __future__ import annotations

from pathlib import Path
from collections.abc import Mapping
import json

import pytest

from engine.world import load_canonical_map
from engine.world import WorldState
from agents.base import AgentInterface
from engine.entities import PlayerId
from meetings.manager import MeetingTrigger
from api.replay_loader import ReplayLoader
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
    prompt_versions_for_set,
    MeetingArtifacts,
    TacticalAgent,
    DefaultMeetingRunner,
)
from orchestrator.replay import (
    GameEndReplayEntry,
    MeetingReplayEntry,
    read_all_entries,
    recorded_testimony_shapes,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import substrate_flag_snapshot
from agents.strategic.prompts import build_prompt_renderers
from llm.fake_provider import FakeProvider
from fastapi.testclient import TestClient
from api.main import create_app
from api.replay_loader import get_replay_loader


def test_explicit_testimony_stamp_must_match_rendered_arm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AILIBI_PROMPT_SET", "qwen3_6_27b")
    versions = prompt_versions_for_set(env={})
    monkeypatch.setenv("AILIBI_TESTIMONY_SHAPES", "1")
    with pytest.raises(ValueError, match="AILIBI_TESTIMONY_SHAPES"):
        build_default_meeting_runner(prompt_versions=versions)


def test_explicit_game_substrate_is_validated_copied_and_checked_against_runner(
    tmp_path: Path,
) -> None:
    flags = substrate_flag_snapshot({})
    game = HeadlessGame(
        seed=3,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=tmp_path / "replay.jsonl",
        scheduler=TickScheduler(max_ticks=1),
        substrate_flags=flags,
    )
    flags["testimony_shapes"] = True
    assert game._substrate_flags["testimony_shapes"] is False
    for bad in ({}, {**substrate_flag_snapshot({}), "testimony_shapes": 1}):
        with pytest.raises(ValueError, match="substrate_flags"):
            HeadlessGame(
                seed=3,
                game_map=load_canonical_map(),
                agent_factory=build_default_agent_factory(),
                replay_path=tmp_path / "invalid.jsonl",
                substrate_flags=bad,  # type: ignore[arg-type]
            )
    with pytest.raises(ValueError, match="substrate_flags.*Runner"):
        HeadlessGame(
            seed=3,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=tmp_path / "invalid.jsonl",
            meeting_runner=build_default_meeting_runner(env={}),
            substrate_flags=flags,
        )


@pytest.mark.parametrize("defect", ["experiment", "testimony"])
def test_api_profile_mismatch_is_a_controlled_integrity_refusal(
    tmp_path: Path, defect: str
) -> None:
    source = Path("replays/samples/9p2i")
    (tmp_path / "roster.json").write_bytes((source / "roster.json").read_bytes())
    path = tmp_path / "replay-seed-23.jsonl"
    original = (source / path.name).read_text()
    path.write_text(original)
    app = create_app()
    app.dependency_overrides[get_replay_loader] = lambda: ReplayLoader(
        replay_dir=tmp_path
    )
    with TestClient(app, raise_server_exceptions=False) as client:
        assert client.get("/replays/headless-seed-23").status_code == 200
        rows = [json.loads(line) for line in original.splitlines()]
        if defect == "experiment":
            rows[0]["experiment_config"] = {"evidence_reasoning_version": 1}
        else:
            rows[-1]["substrate_flags"]["testimony_shapes"] = True
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        response = client.get("/replays/headless-seed-23")
    assert response.status_code == 500
    assert response.json()["game_id"] == "headless-seed-23"
    assert response.json()["code"] == "substrate_version_mismatch"


def test_live_runner_freezes_memory_arm_and_terminal_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    monkeypatch.setenv("AILIBI_PROMPT_SET", "qwen3_6_27b")
    monkeypatch.setenv("AILIBI_TESTIMONY_SHAPES", "1")
    runner = build_default_meeting_runner()
    monkeypatch.setenv("AILIBI_TESTIMONY_SHAPES", "0")
    path = tmp_path / "game.jsonl"
    HeadlessGame(
        seed=3,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        meeting_runner=runner,
        scheduler=TickScheduler(max_ticks=100),
    ).run()
    entries = read_all_entries(path)
    assert any(isinstance(entry, GameEndReplayEntry) for entry in entries)
    assert recorded_testimony_shapes(entries)
    for entry in entries:
        if isinstance(entry, GameEndReplayEntry):
            assert entry.substrate_flags is not None
            assert entry.substrate_flags["testimony_shapes"]


def test_recorded_testimony_reads_versions_without_ambient_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = Path("replays/samples/9p2i/replay-seed-23.jsonl")
    entries = read_all_entries(path)
    monkeypatch.setenv("AILIBI_TESTIMONY_SHAPES", "1")
    assert not recorded_testimony_shapes(entries)
    meeting = next(entry for entry in entries if isinstance(entry, MeetingReplayEntry))
    shaped = meeting.model_copy(
        update={
            "prompt_versions": dict(
                prompt_versions_for_set(
                    "qwen3_6_27b", env={"AILIBI_TESTIMONY_SHAPES": "1"}
                )
            )
        }
    )
    assert recorded_testimony_shapes((shaped,))
    with pytest.raises(ValueError, match="changes between meetings"):
        recorded_testimony_shapes((meeting, shaped))
    with pytest.raises(ValueError, match="disagrees with substrate stamp"):
        terminal = next(
            entry for entry in entries if isinstance(entry, GameEndReplayEntry)
        )
        recorded_testimony_shapes((shaped, terminal))


def test_candidate_live_and_api_memory_match_after_environment_change(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    monkeypatch.setenv("AILIBI_EVIDENCE_REASONING", "1")
    runner = build_default_meeting_runner()
    original = runner.run_meeting
    snapshots: dict[tuple[str, str], str] = {}

    async def capture(
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        for pid, player in state.players.items():
            agent = agents[pid]
            if player.alive and isinstance(agent, TacticalAgent):
                snapshots[meeting_id, pid] = agent.render_memory_for_meeting()
        return await original(
            meeting_id=meeting_id, trigger=trigger, state=state, agents=agents
        )

    monkeypatch.setattr(runner, "run_meeting", capture)
    config = RecordedExperimentConfig(evidence_reasoning_version=1)
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2})
    )
    HeadlessGame(
        seed=23,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=tmp_path / "replay-seed-23.jsonl",
        meeting_runner=runner,
        num_players=9,
        num_impostors=2,
        scheduler=TickScheduler(max_ticks=96),
        experiment_config=config,
    ).run()
    assert len({meeting for meeting, _ in snapshots}) >= 2
    monkeypatch.setenv("AILIBI_EVIDENCE_REASONING", "0")
    loader = ReplayLoader(tmp_path)
    for (meeting, pid), rendered in snapshots.items():
        assert (
            loader.get_meeting_memory(
                "headless-seed-23", meeting, pid
            ).rendered_memory_text
            == rendered
        )


def test_direct_runner_binds_environment_and_explicit_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    renderers = build_prompt_renderers(env={})

    def build(
        *, override: bool | None = None, flags: Mapping[str, bool] | None = None
    ) -> DefaultMeetingRunner:
        return DefaultMeetingRunner(
            llm_client=FakeProvider(),
            crewmate_report_prompt=renderers.crewmate_report,
            impostor_report_prompt=renderers.impostor_report,
            statement_prompt=renderers.statement,
            vote_prompt=renderers.vote,
            reporter_reasoning=override,
            corroboration_discipline=override,
            substrate_flags=flags,
        )

    monkeypatch.setenv("AILIBI_REPORTER_REASONING", "1")
    monkeypatch.setenv("AILIBI_CORROBORATION_DISCIPLINE", "1")
    runner = build()
    monkeypatch.setenv("AILIBI_REPORTER_REASONING", "0")
    monkeypatch.setenv("AILIBI_CORROBORATION_DISCIPLINE", "0")
    assert runner._manager._reporter_reasoning is True
    assert runner._manager._corroboration_discipline is True
    assert build(override=True).substrate_flags["reporter_reasoning"] is True
    assert build(override=False).substrate_flags["corroboration_discipline"] is False
    with pytest.raises(ValueError, match="disagrees with substrate_flags"):
        build(override=True, flags=substrate_flag_snapshot({}))
