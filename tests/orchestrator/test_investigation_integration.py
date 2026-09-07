"""Real version-3 policies are reproduced; rejected actions cannot hide drift."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from agents.base import AgentInterface
import api.replay_loader as replay_module
from api.replay_loader import ReplayLoader
from engine.entities import Role
from engine.world import load_canonical_map
from experiments.investigation_evaluation import (
    InvestigationCaseDefinition,
    comparison_arms,
    run_case,
)
from observation.service import ObservationService
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import HeadlessGame, TacticalAgent, build_default_agent_factory
from orchestrator.replay import (
    ReplayEntry,
    read_all_entries,
    require_baseline_experiments,
    substrate_flag_snapshot,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state


def _config() -> RecordedExperimentConfig:
    return RecordedExperimentConfig(
        format_version=3, evidence_reasoning_version=2, investigation_version=1
    )


@pytest.mark.parametrize(
    "field", ["investigation_version", "contextual_self_report_version"]
)
@pytest.mark.parametrize("value", [True, False, "1", 1.0, 2])
def test_versions_refuse_coercion(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        RecordedExperimentConfig.model_validate(
            {**_config().model_dump(), field: value}
        )


@pytest.mark.parametrize(
    "overrides",
    [
        {"format_version": 2},
        {"evidence_reasoning_version": 1},
        {"crew_idle_policy": "accompany"},
        {"crew_idle_policy": "patrol"},
        {"contextual_self_report_version": 1, "self_report": True},
    ],
)
def test_conflicting_options_refuse(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RecordedExperimentConfig.model_validate({**_config().model_dump(), **overrides})


def test_old_envelopes_do_not_emit_new_fields() -> None:
    for version in (1, 2):
        config = RecordedExperimentConfig.model_validate({"format_version": version})
        encoded = config.model_dump_json()
        assert "investigation_version" not in encoded
        assert "contextual_self_report_version" not in encoded
        assert RecordedExperimentConfig.model_validate_json(encoded) == config


def test_subclass_cannot_claim_reproducible_policy_before_output(
    tmp_path: Path,
) -> None:
    class Custom(TacticalAgent):
        pass

    config = _config()
    builtin = build_default_agent_factory(experiment_config=config)

    def custom(pid: str, role: Role) -> AgentInterface:
        original = builtin(pid, role)
        assert isinstance(original, TacticalAgent)
        return Custom(agent_id=pid, role=role, policy=original._policy)

    flags = substrate_flag_snapshot({"AILIBI_TEMPORAL_OBSERVATIONS": "2"})
    path = tmp_path / "must-not-exist.jsonl"
    game = HeadlessGame(
        seed=0,
        game_map=load_canonical_map(),
        agent_factory=custom,
        replay_path=path,
        scheduler=TickScheduler(max_ticks=2),
        experiment_config=config,
        temporal_observation_version=2,
        substrate_flags=flags,
    )
    with pytest.raises(ValueError, match="exact built-in"):
        game.run()
    assert not path.exists()
    assert not path.with_suffix(".audit.jsonl").exists()


def test_duplicate_decision_returns_before_any_second_ingestion(tmp_path: Path) -> None:
    config = _config()
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    state = seed_initial_state(seed=0, game_map=game_map, num_players=4)
    pid = sorted(state.players)[0]
    agent = build_default_agent_factory(experiment_config=config)(
        pid, state.players[pid].role
    )
    assert isinstance(agent, TacticalAgent)
    agent.bind_experiment(config, public_map)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit.jsonl",
        temporal_observations=True,
        temporal_observation_version=2,
    )
    try:
        packet = service.build_packet(world_state=state, agent_id=pid, engine_events=())
        first = agent.decide(packet, public_map)
        events = agent.memory.episodic.recent(since_tick=0)
        working = agent.memory.working.investigation
        assert agent.decide(packet, public_map) is first
        assert agent.memory.episodic.recent(since_tick=0) == events
        assert agent.memory.working.investigation is working
        # Same tick and identity, different own observation: reject before a fold.
        changed = packet.model_copy(
            update={
                "self_state": packet.self_state.model_copy(update={"room": "ADMIN"})
            }
        )
        with pytest.raises(ValueError, match="different observation packet"):
            agent.decide(changed, public_map)
        assert agent.memory.episodic.recent(since_tick=0) == events
    finally:
        service.close()


def test_real_policy_reader_prefix_and_discarded_action_plant(tmp_path: Path) -> None:
    arm = next(a for a in comparison_arms() if a.name == "search")
    capture = run_case(
        tmp_path / "real",
        definition=InvestigationCaseDefinition(
            name="integration",
            seed=7,
            num_players=5,
            tasks_per_crewmate=2,
            max_ticks=80,
        ),
        arm=arm,
    )
    roster = {"num_players": 5, "num_impostors": 1, "tasks_per_crewmate": 2}
    (capture.replay_path.parent / "roster.json").write_text(json.dumps(roster))
    replay = ReplayLoader(capture.replay_path.parent).load_replay("headless-seed-7")
    assert replay.metadata.outcome_verified
    assert any(
        a.investigation_plan is not None for t in replay.ticks for a in t.agent_states
    )
    entries = read_all_entries(capture.replay_path)
    with pytest.raises(ValueError, match="does not support experimental"):
        require_baseline_experiments(entries, consumer="baseline training")

    rows = [json.loads(line) for line in capture.replay_path.read_text().splitlines()]
    prefix = tmp_path / "prefix"
    prefix.mkdir()
    (prefix / "roster.json").write_text(json.dumps(roster))
    tick_rows = [r for r in rows if r["kind"] == "tick"][:4]
    (prefix / capture.replay_path.name).write_text(
        "".join(json.dumps(r) + "\n" for r in tick_rows)
    )
    partial = ReplayLoader(prefix).load_replay("headless-seed-7")
    assert partial.metadata.winner is None
    assert partial.metadata.experiment_config is not None
    assert partial.metadata.experiment_config.investigation_version == 1

    # A later actor's discarded action cannot affect engine hashes. The reader
    # must still verify the decision, rather than certifying its plan from hashes.
    row = next(
        r
        for r in rows
        if r["kind"] == "tick"
        and "discarded_by_meeting" in (r.get("action_dispositions") or [])
    )
    index = row["action_dispositions"].index("discarded_by_meeting")
    action = row["actions"][index]
    replacement = {"actor": action["actor"], "type": "wait"}
    if action["type"] == "wait":
        replacement = {
            "actor": action["actor"],
            "type": "move",
            "payload": {"to_room": "ADMIN"},
        }
    row["actions"][index] = replacement
    capture.replay_path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(ValueError, match="recorded tactical actions disagree"):
        ReplayLoader(capture.replay_path.parent).load_replay("headless-seed-7")
    # Parsing still accepts the structural row; semantic action checking bites.
    assert any(
        isinstance(e, ReplayEntry) for e in read_all_entries(capture.replay_path)
    )


def test_reader_constructor_failure_closes_its_observation_service(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    arm = next(a for a in comparison_arms() if a.name == "search")
    capture = run_case(
        tmp_path / "real",
        definition=InvestigationCaseDefinition(
            name="constructor-control",
            seed=0,
            num_players=5,
            tasks_per_crewmate=2,
            max_ticks=80,
        ),
        arm=arm,
    )
    closed: list[ObservationService] = []
    original = ObservationService.close

    def close(service: ObservationService) -> None:
        closed.append(service)
        original(service)

    def broken_constructor(**kwargs: object) -> None:
        raise RuntimeError("planted reconstruction setup failure")

    monkeypatch.setattr(ObservationService, "close", close)
    monkeypatch.setattr(replay_module, "PolicyReconstruction", broken_constructor)
    with pytest.raises(RuntimeError, match="planted reconstruction setup"):
        ReplayLoader(capture.replay_path.parent).load_replay("headless-seed-0")
    assert len(closed) == 1
