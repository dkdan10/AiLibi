"""Actual factory behavior and recorded vote rules survive strict projections."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal, NoReturn

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agents.base import AgentInterface
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from api.main import create_app
from api.replay_loader import ReplayLoader, ReplayPolicyMismatchError, get_replay_loader
from engine.entities import PlayerId, Role
from engine.world import WorldState, load_canonical_map
from eval.balance_eval import build_tournament_report, load_tournament_report
from eval.meeting_quality import build_tournament_eval_report
from eval.report_schema import TournamentReport
from eval.replay_walk import ReplayWalkConfig, WalkViolation, walk_replay
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from meetings.voting import tally_ballots
from observation.action_intent import ActionIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import (
    AgentFactory,
    HeadlessGame,
    MeetingArtifacts,
    MeetingRunner,
    TacticalAgent,
    build_default_agent_factory,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    TacticalPolicyStamp,
    fsm_default_tactical_policy_stamp,
)
from orchestrator.replay_integrity import ReplayIntegrityError
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state


class _WaitAgent:
    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        return WaitIntent(type="wait", actor=self.agent_id)


class _AgentSubclass(TacticalAgent):
    pass


class _CrewSubclass(CrewmatePolicy):
    pass


def _custom_factory(kind: str) -> AgentFactory:
    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        if kind == "custom":
            return _WaitAgent(agent_id)
        agent_class = _AgentSubclass if kind == "agent_subclass" else TacticalAgent
        crew_class = _CrewSubclass if kind == "policy_subclass" else CrewmatePolicy
        policy = (
            ImpostorPolicy(agent_id=agent_id)
            if role == "IMPOSTOR"
            else crew_class(agent_id=agent_id)
        )
        return agent_class(agent_id=agent_id, role=role, policy=policy)

    return factory


def _game(
    directory: Path,
    *,
    config: RecordedExperimentConfig | None = None,
    factory: AgentFactory | None = None,
    runner: MeetingRunner | None = None,
    max_ticks: int = 3,
    force: bool = False,
    policy_stamp: TacticalPolicyStamp | None = None,
) -> HeadlessGame:
    directory.mkdir(parents=True, exist_ok=True)
    return HeadlessGame(
        seed=1,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=factory or build_default_agent_factory(experiment_config=config),
        experiment_config=config,
        replay_path=directory / "replay-seed-1.jsonl",
        scheduler=TickScheduler(max_ticks=max_ticks),
        meeting_runner=runner,
        force=force,
        tactical_policy_stamp=policy_stamp,
    )


def _report(directory: Path) -> TournamentReport:
    state = seed_initial_state(
        seed=1, game_map=load_canonical_map(), num_players=7, tasks_per_crewmate=1
    )
    return load_tournament_report(
        directory,
        roles_by_seed={1: {pid: player.role for pid, player in state.players.items()}},
    )


@pytest.mark.parametrize(
    "requested",
    [
        None,
        RecordedExperimentConfig(),
        RecordedExperimentConfig(meeting_reset="hub_with_grace"),
    ],
)
def test_unstamped_experimental_factory_fails_before_replacing_evidence(
    tmp_path: Path, requested: RecordedExperimentConfig | None
) -> None:
    replay = tmp_path / "replay-seed-1.jsonl"
    audit = tmp_path / "replay-seed-1.audit.jsonl"
    replay.write_bytes(b"prior replay")
    audit.write_bytes(b"prior audit")
    factory = build_default_agent_factory(
        experiment_config=RecordedExperimentConfig(crew_idle_policy="patrol")
    )
    with pytest.raises(ValueError, match="recorded tactical experiment"):
        _game(tmp_path, config=requested, factory=factory, force=True).run()
    assert replay.read_bytes() == b"prior replay"
    assert audit.read_bytes() == b"prior audit"
    assert set(tmp_path.iterdir()) == {replay, audit}


@pytest.mark.parametrize("kind", ["custom", "agent_subclass", "policy_subclass"])
def test_custom_implementations_remain_usable_without_baseline_certification(
    tmp_path: Path, kind: str
) -> None:
    _game(tmp_path, factory=_custom_factory(kind)).run()
    report = _report(tmp_path)
    assert report.games[0].agent_factory_kind == "custom"
    assert report.provenance_groups is not None
    assert report.provenance_groups[0].agent_factory_kind == "custom"


def test_candidate_partial_identity_reaches_current_report_and_api(
    tmp_path: Path,
) -> None:
    config = RecordedExperimentConfig(crew_idle_policy="patrol")
    _game(tmp_path, config=config).run()
    report = _report(tmp_path)
    game = report.games[0]
    assert game.agent_factory_kind == "experimental"
    assert game.experiment_config == config
    assert game.substrate_flags is not None
    assert game.completion_status == "tick_limited"
    assert game.outcome_verified is False
    assert report.provenance_groups is not None
    assert report.provenance_groups[0].experiment_config == config
    (tmp_path / "tournament-eval-report.json").write_text(
        build_tournament_eval_report(report).model_dump_json(), encoding="utf-8"
    )
    loader = ReplayLoader(tmp_path)
    metadata = loader.load_replay("headless-seed-1").metadata
    assert metadata.agent_factory_kind == "experimental"
    assert metadata.experiment_config is not None
    assert metadata.experiment_config.crew_idle_policy == "patrol"
    assert metadata.substrate_flags == game.substrate_flags
    app = create_app()
    app.dependency_overrides[get_replay_loader] = lambda: loader
    with TestClient(app) as client:
        response = client.get("/eval/tournament-report")
    assert response.status_code == 200
    payload = response.json()["report"]
    assert payload["games"][0]["agent_factory_kind"] == "experimental"
    assert (
        payload["provenance_groups"][0]["experiment_config"]["crew_idle_policy"]
        == "patrol"
    )


def test_historical_absence_is_unknown_and_mixed_arms_stay_separate(
    tmp_path: Path,
) -> None:
    baseline = tmp_path / "baseline"
    candidate = tmp_path / "candidate"
    historical = tmp_path / "historical"
    _game(baseline).run()
    _game(candidate, config=RecordedExperimentConfig(crew_idle_policy="patrol")).run()
    historical.mkdir()
    rows = [
        json.loads(line)
        for line in (baseline / "replay-seed-1.jsonl").read_text().splitlines()
    ]
    for row in rows:
        row.pop("agent_factory_kind", None)
        row.pop("substrate_flags", None)
    (historical / "replay-seed-1.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    games = tuple(
        _report(directory).games[0].model_copy(update={"game_id": name})
        for name, directory in (
            ("baseline", baseline),
            ("candidate", candidate),
            ("historical", historical),
        )
    )
    report = build_tournament_report(games=games, seeds=(1, 1, 1))
    assert games[0].agent_factory_kind == "scripted"
    assert games[2].agent_factory_kind is None
    assert games[2].substrate_flags is None
    assert report.provenance_groups is not None
    assert len(report.provenance_groups) == 3
    assert {group.agent_factory_kind for group in report.provenance_groups} == {
        "scripted",
        "experimental",
        None,
    }
    corrupted = report.model_dump(mode="json")
    corrupted["provenance_groups"] = [
        {
            **corrupted["provenance_groups"][0],
            "game_ids": ["baseline", "candidate", "historical"],
        }
    ]
    with pytest.raises(ValidationError, match="provenance groups disagree"):
        TournamentReport.model_validate(corrupted)


@pytest.mark.parametrize("field", ["agent_factory_kind", "substrate_flags"])
def test_conflicting_prefix_identity_is_refused(tmp_path: Path, field: str) -> None:
    _game(tmp_path).run()
    path = tmp_path / "replay-seed-1.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    if field == "agent_factory_kind":
        rows[1][field] = "custom"
    else:
        rows[1][field]["testimony_shapes"] = True
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    with pytest.raises(ValueError, match="changes between tick rows"):
        _report(tmp_path)
    with pytest.raises(ValueError, match="changes between tick rows"):
        ReplayLoader(tmp_path).load_replay("headless-seed-1")


class _CutoffRunner:
    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        living = sorted(pid for pid, player in state.players.items() if player.alive)
        return MeetingArtifacts(
            result=MeetingResult(
                meeting_id=meeting_id,
                triggered_by=trigger.triggered_by,
                trigger_tick=trigger.trigger_tick,
                outcome="SKIPPED",
                ejected_player_id=None,
                ballots=tuple(
                    VoteBallot(
                        voter=pid,
                        target=living[0] if pid != living[0] else "SKIP",
                        confidence=0.7,
                        primary_reason_id=None,
                        considered_alternatives=(),
                        rationale_text="A candidate below the configured confidence cutoff.",
                    )
                    for pid in living
                ),
                transcript=MeetingTranscript(),
            ),
            llm_calls=(),
            prompt_versions={},
            skip_confidence_threshold=0.8,
        )


def _unexpected_tally_violation(violation: WalkViolation) -> NoReturn:
    raise AssertionError(f"valid recorded cutoff was ignored: {violation.kind}")


def test_custom_policy_footer_identity_is_retained_without_baseline_claim(
    tmp_path: Path,
) -> None:
    stamp = TacticalPolicyStamp(
        policy_id="test-scripted-wrapper",
        method="scripted-test",
        encoder_version="none",
        weights_sha256="none",
        anchor_policy="fsm-default",
    )
    _game(
        tmp_path,
        factory=_custom_factory("agent_subclass"),
        runner=_CutoffRunner(),
        max_ticks=200,
        policy_stamp=stamp,
    ).run()
    report = _report(tmp_path)
    game = report.games[0]
    assert game.outcome_verified
    assert game.agent_factory_kind == "custom"
    assert game.tactical_policy == stamp
    assert report.provenance_groups is not None
    assert report.provenance_groups[0].tactical_policy == stamp
    metadata = ReplayLoader(tmp_path).load_replay("headless-seed-1").metadata
    assert metadata.agent_factory_kind == "custom"
    assert metadata.tactical_policy is not None
    assert metadata.tactical_policy.policy_id == stamp.policy_id


@pytest.mark.parametrize("complete", [False, True])
def test_unbound_custom_factory_cannot_satisfy_an_explicit_default_policy_claim(
    tmp_path: Path, complete: bool
) -> None:
    _game(
        tmp_path,
        factory=_custom_factory("agent_subclass"),
        runner=_CutoffRunner() if complete else None,
        max_ticks=200 if complete else 3,
    ).run()
    ordinary = ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert ordinary.metadata.agent_factory_kind == "custom"
    assert ordinary.metadata.tactical_policy is None
    assert ordinary.metadata.outcome_verified is complete
    with pytest.raises(ReplayPolicyMismatchError):
        ReplayLoader(
            tmp_path, expected_tactical_policy=fsm_default_tactical_policy_stamp()
        ).load_replay("headless-seed-1")


@pytest.mark.parametrize("mutation", ["ballots", "cutoff", "legacy_cutoff"])
def test_strict_readers_use_recorded_cutoff_and_reject_unchanged_hash_forgery(
    tmp_path: Path, mutation: Literal["ballots", "cutoff", "legacy_cutoff"]
) -> None:
    _game(tmp_path, runner=_CutoffRunner(), max_ticks=200).run()
    path = tmp_path / "replay-seed-1.jsonl"
    report = _report(tmp_path)
    assert report.games[0].outcome_verified
    assert report.games[0].meetings
    assert all(
        meeting.skip_confidence_threshold == 0.8 for meeting in report.games[0].meetings
    )
    view = ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert all(meeting.gate.threshold == 0.8 for meeting in view.meetings)
    assert all(meeting.gate.threshold_source == "recorded" for meeting in view.meetings)
    assert tuple(
        walk_replay(
            path,
            seed=1,
            num_players=7,
            num_impostors=1,
            tasks_per_crewmate=1,
            game_map=load_canonical_map(),
            config=ReplayWalkConfig(
                profile="recorded-cutoff-control",
                on_violation=_unexpected_tally_violation,
                ballot_tally_threshold=0.6,
            ),
        )
    )
    rows: list[dict[str, Any]] = [
        json.loads(line) for line in path.read_text().splitlines()
    ]
    before_hashes = [
        (
            row.get("state_hash"),
            row.get("state_hash_before"),
            row.get("state_hash_after"),
        )
        for row in rows
    ]
    meeting = next(row for row in rows if row["kind"] == "meeting")
    if mutation == "ballots":
        for ballot in meeting["ballots"]:
            ballot["confidence"] = 0.9
    elif mutation == "cutoff":
        meeting["skip_confidence_threshold"] = 0.6
    else:
        del meeting["skip_confidence_threshold"]
    assert before_hashes == [
        (
            row.get("state_hash"),
            row.get("state_hash_before"),
            row.get("state_hash_after"),
        )
        for row in rows
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    with pytest.raises(ReplayIntegrityError, match="ballot_tally_mismatch"):
        _report(tmp_path)
    with pytest.raises(ReplayIntegrityError, match="ballot_tally_mismatch"):
        ReplayLoader(tmp_path).load_replay("headless-seed-1")


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate",
        "missing",
        "empty",
        "foreign_voter",
        "dead",
        "self",
        "foreign_target",
    ],
)
def test_ballot_roster_and_targets_are_checked_even_when_outcome_is_unchanged(
    tmp_path: Path, mutation: str
) -> None:
    _game(tmp_path, runner=_CutoffRunner(), max_ticks=200).run()
    path = tmp_path / "replay-seed-1.jsonl"
    assert _report(tmp_path).games[0].outcome_verified
    assert (
        ReplayLoader(tmp_path).load_replay("headless-seed-1").metadata.outcome_verified
    )
    rows: list[dict[str, Any]] = [
        json.loads(line) for line in path.read_text().splitlines()
    ]
    hashes = [
        (
            row.get("state_hash"),
            row.get("state_hash_before"),
            row.get("state_hash_after"),
        )
        for row in rows
    ]
    meeting = next(row for row in rows if row["kind"] == "meeting")
    ballots = meeting["ballots"]
    voters = {ballot["voter"] for ballot in ballots}
    if mutation == "duplicate":
        ballots.append(dict(ballots[0]))
    elif mutation == "missing":
        ballots.pop()
    elif mutation == "empty":
        ballots.clear()
    elif mutation == "foreign_voter":
        ballots[0]["voter"] = "not-a-participant"
    else:
        target = (
            next(pid for pid in (f"p-{i}" for i in range(1, 8)) if pid not in voters)
            if mutation == "dead"
            else ballots[0]["voter"]
            if mutation == "self"
            else "not-a-participant"
        )
        ballots[0].update(target=target, confidence=0.1)
    assert tally_ballots(
        tuple(VoteBallot.model_validate(ballot) for ballot in ballots),
        skip_confidence_threshold=0.8,
    ) == (meeting["outcome"], meeting["ejected_player_id"])
    assert hashes == [
        (
            row.get("state_hash"),
            row.get("state_hash_before"),
            row.get("state_hash_after"),
        )
        for row in rows
    ]
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    failure = (
        "ballot_target_mismatch"
        if mutation in ("dead", "self", "foreign_target")
        else "ballot_roster_mismatch"
    )
    with pytest.raises(ReplayIntegrityError, match=failure):
        _report(tmp_path)
    with pytest.raises(ReplayIntegrityError, match=failure):
        ReplayLoader(tmp_path).load_replay("headless-seed-1")


@pytest.mark.parametrize("cutoff", [True, "0.6", -0.1, 1.1, float("nan"), float("inf")])
def test_invalid_recorded_cutoffs_are_refused(cutoff: object) -> None:
    payload = {
        "game_id": "test",
        "meeting_id": "test:meeting",
        "tick": 0,
        "triggered_by": "p-1",
        "outcome": "SKIPPED",
        "ejected_player_id": None,
        "transcript": {"turns": []},
        "ballots": [],
        "contradictions": [],
        "llm_calls": [],
        "prompt_versions": {},
        "state_hash_before": "before",
        "state_hash_after": "after",
        "skip_confidence_threshold": cutoff,
    }
    with pytest.raises(ValidationError):
        MeetingReplayEntry.model_validate(payload)
