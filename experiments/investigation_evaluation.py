"""Recorded normal-policy development controls; fixed speech is not model quality."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from agents.base import AgentInterface
from agents.memory.episodic import EpisodicEvent
from api.replay_loader import ReplayLoader
from api.schemas import InvestigationPlanView
from engine.entities import Role
from engine.world import load_canonical_map
from eval.balance_eval import load_tournament_report
from eval.report_schema import GameCostSummary, GameProvenance
from experiments.deduction_evaluation import source_hashes
from llm.client import CallKind, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from meetings.schemas import MeetingTurn, ModelAuthoredVoteBallot
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import (
    HeadlessGame,
    HeadlessGameResult,
    TacticalAgent,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.replay import (
    CompletionStatus,
    MeetingReplayEntry,
    ReplayEntry,
    read_all_entries,
)


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class InvestigationCaseDefinition(_Frozen):
    """Seeded inputs only: no injected position, action schedule or observer fact."""

    version: Literal[1] = 1
    name: str
    seed: int = Field(ge=0)
    num_players: int = Field(ge=4)
    num_impostors: Literal[1] = 1
    tasks_per_crewmate: int = Field(ge=1)
    max_ticks: int = Field(ge=1)
    selection_scope: Literal["development"] = "development"


class InvestigationArm(_Frozen):
    name: str
    temporal_version: Literal[2] = 2
    experiment_config: RecordedExperimentConfig


def development_cases() -> tuple[InvestigationCaseDefinition, ...]:
    """Selected from the disclosed 0–15 OFF scan, not held-out confirmation."""
    return tuple(
        InvestigationCaseDefinition(
            name=f"five-player-seed-{seed}",
            seed=seed,
            num_players=5,
            tasks_per_crewmate=2,
            max_ticks=80,
        )
        for seed in (0, 1, 6, 7, 14)
    )


def comparison_arms() -> tuple[InvestigationArm, ...]:
    """Compare components first, then their interaction and existing follow control."""
    shared = RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        public_account_version=1,
        attributed_testimony_version=1,
    )
    return (
        InvestigationArm(name="off", experiment_config=shared),
        InvestigationArm(
            name="search",
            experiment_config=RecordedExperimentConfig(
                **{
                    **shared.model_dump(),
                    "format_version": 3,
                    "investigation_version": 1,
                }
            ),
        ),
        InvestigationArm(
            name="contextual_self_report",
            experiment_config=RecordedExperimentConfig(
                **{
                    **shared.model_dump(),
                    "format_version": 3,
                    "contextual_self_report_version": 1,
                }
            ),
        ),
        InvestigationArm(
            name="unconditional_self_report",
            experiment_config=RecordedExperimentConfig(
                **{**shared.model_dump(), "self_report": True}
            ),
        ),
        InvestigationArm(
            name="old_patrol",
            experiment_config=RecordedExperimentConfig(
                **{**shared.model_dump(), "crew_idle_policy": "patrol"}
            ),
        ),
        InvestigationArm(
            name="old_accompany",
            experiment_config=RecordedExperimentConfig(
                **{**shared.model_dump(), "crew_idle_policy": "accompany"}
            ),
        ),
        InvestigationArm(
            name="combined_search_report",
            experiment_config=RecordedExperimentConfig(
                **{
                    **shared.model_dump(),
                    "format_version": 3,
                    "investigation_version": 1,
                    "contextual_self_report_version": 1,
                }
            ),
        ),
    )


class InvestigationControlProvider(FakeProvider):
    """Neutral fixed meetings leave tactical decisions to the built-in policies."""

    def __init__(self) -> None:
        self.prompts: list[tuple[str | None, str]] = []

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if agent_id is None:
            raise ValueError("investigation control requires its supplied speaker")
        self.prompts.append((agent_id, prompt))
        response: BaseModel
        if schema is MeetingTurn:
            response = MeetingTurn(
                turn_id="control",
                turn_index=0,
                speaker=agent_id,
                turn_kind="opening",
                reply_to=None,
                observations=(),
                claims=(),
                free_text="I have no additional account to add. I am unsure.",
            )
        elif schema is ModelAuthoredVoteBallot:
            response = ModelAuthoredVoteBallot(
                voter=agent_id,
                target="SKIP",
                confidence=1.0,
                primary_reason_id=None,
                primary_reason_observation_id=None,
                considered_alternatives=(),
                rationale_text="The fixed control abstains; this does not measure model quality.",
            )
        else:
            raise ValueError(
                "investigation control only supports ordinary meeting schemas"
            )
        text = response.model_dump_json()
        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=max(1, len(prompt) // 4),
                output_tokens=max(1, len(text) // 4),
            ),
            cost_usd=0,
            model="scripted-investigation-control",
        )


@dataclass(frozen=True)
class InvestigationCapture:
    """Privileged instrumentation of exact built-ins, never public agent evidence."""

    definition: InvestigationCaseDefinition
    arm: InvestigationArm
    result: HeadlessGameResult
    agents: Mapping[str, TacticalAgent]
    provider: InvestigationControlProvider

    @property
    def replay_path(self) -> Path:
        return self.result.replay_path


def run_case(
    output_dir: Path,
    *,
    definition: InvestigationCaseDefinition,
    arm: InvestigationArm,
) -> InvestigationCapture:
    """Run ordinary role policies and real meetings from a canonical seeded start."""
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    config = arm.experiment_config
    provider = InvestigationControlProvider()
    env = {
        "AILIBI_LLM_PROVIDER": "fake",
        "AILIBI_PROMPT_SET": "qwen3_6_27b",
        "AILIBI_TEMPORAL_OBSERVATIONS": "2",
        "AILIBI_EVIDENCE_REASONING": str(config.evidence_reasoning_version or 0),
        "AILIBI_PUBLIC_ACCOUNTS": str(config.public_account_version or 0),
        "AILIBI_ATTRIBUTED_TESTIMONY": str(config.attributed_testimony_version or 0),
        "AILIBI_BOUNDED_REBUTTAL": str(config.bounded_rebuttal_version or 0),
    }
    runner = build_default_meeting_runner(
        llm_client=provider, env=env, public_map=public_map
    )
    builtin = build_default_agent_factory(experiment_config=config)
    agents: dict[str, TacticalAgent] = {}

    def factory(agent_id: str, role: Role) -> AgentInterface:
        agent = builtin(agent_id, role)
        if type(agent) is not TacticalAgent:
            raise ValueError("normal-policy control requires exact built-in agents")
        agents[agent_id] = agent
        return agent

    output_dir.mkdir(parents=True, exist_ok=False)
    result = HeadlessGame(
        seed=definition.seed,
        game_map=game_map,
        num_players=definition.num_players,
        num_impostors=definition.num_impostors,
        tasks_per_crewmate=definition.tasks_per_crewmate,
        agent_factory=factory,
        replay_path=output_dir / f"replay-seed-{definition.seed}.jsonl",
        scheduler=TickScheduler(max_ticks=definition.max_ticks),
        meeting_runner=runner,
        experiment_config=config,
        temporal_observation_version=arm.temporal_version,
        substrate_flags=runner.substrate_flags,
    ).run()
    with (output_dir / "roster.json").open("x") as stream:
        json.dump(
            {
                "num_players": definition.num_players,
                "num_impostors": definition.num_impostors,
                "tasks_per_crewmate": definition.tasks_per_crewmate,
            },
            stream,
            sort_keys=True,
        )
        stream.write("\n")
    return InvestigationCapture(
        definition=definition,
        arm=arm,
        result=result,
        agents=MappingProxyType(agents),
        provider=provider,
    )


class PlanDecision(_Frozen):
    observer_id: str
    plan: InvestigationPlanView
    submitted_action: str


class ObservedFact(_Frozen):
    observer_id: str
    observation_id: str
    tick: int
    kind: str
    subject_id: str | None
    room: str | None
    from_room: str | None = None
    to_room: str | None = None
    action: str | None = None


class TaskCompletion(_Frozen):
    observer_id: str
    task_id: str
    tick: int


class InvestigationMeasurement(_Frozen):
    arm: str
    case: str
    replay_ref: str
    definition: InvestigationCaseDefinition
    provenance: GameProvenance
    winner: Literal["CREWMATES", "IMPOSTORS"] | None
    winner_reason: str | None
    completion_status: CompletionStatus
    outcome_verified: bool
    final_recorded_tick: int
    trajectory_sha256: str
    submitted_actions_sha256: str
    reader_projection_sha256: str
    memory_projection_sha256: str
    cost: GameCostSummary
    meetings: int
    calls: int
    ballots: int
    voluntary_skips: int
    wrongful_accusations: int
    body_report_ticks: tuple[int, ...]
    impostor_report_ticks: tuple[int, ...]
    action_counts: Mapping[str, int]
    action_dispositions: Mapping[str, int]
    plans: tuple[PlanDecision, ...]
    observed_facts: tuple[ObservedFact, ...]
    task_completions: tuple[TaskCompletion, ...]


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def _text(event: EpisodicEvent, name: str) -> str | None:
    value = event.payload.get(name)
    return value if isinstance(value, str) else None


def validate_plan_sources(
    capture: InvestigationCapture, decisions: Sequence[PlanDecision]
) -> None:
    """Bind intentions to one observer's actual past fact, by exact ID equality."""
    starts: dict[tuple[str, str], int] = {}
    for row in decisions:
        plan = row.plan
        agent = capture.agents.get(row.observer_id)
        if agent is None or agent.role != "CREWMATE":
            raise ValueError("search plan is not owned by a real crewmate")
        matches = [
            event
            for event in agent.memory.episodic.recent(since_tick=0)
            if event.observation_id == plan.source_observation_id
        ]
        if len(matches) != 1:
            raise ValueError("search source is not an exact observation of its owner")
        (event,) = matches
        room_field = "to_room" if event.type == "saw_player_move" else "room"
        if (
            event.provenance != "observed"
            or event.type not in ("saw_player", "saw_player_move")
            or _text(event, "player_id") != plan.target_id
            or _text(event, room_field) != plan.last_known_room
            or event.tick != plan.source_tick
            or not 4 <= plan.started_tick - plan.source_tick <= 12
            or plan.expires_tick != plan.started_tick + 6
            or not plan.started_tick <= plan.decision_tick < plan.expires_tick
            or len(set(plan.visited_rooms)) != len(plan.visited_rooms)
            or len(plan.visited_rooms) > 3
        ):
            raise ValueError(
                "search plan is not supported by its actual source and bounds"
            )
        key = (row.observer_id, plan.source_observation_id)
        prior = starts.setdefault(key, plan.started_tick)
        if prior != plan.started_tick:
            raise ValueError("search restarted from the same consumed source")


def measure_capture(capture: InvestigationCapture) -> InvestigationMeasurement:
    """Use strict replay/API folds; keep plans separate from actual observations."""
    directory = capture.replay_path.parent
    roles = {
        pid: player.role for pid, player in capture.result.final_state.players.items()
    }
    (report,) = load_tournament_report(
        directory,
        roles_by_seed={capture.definition.seed: roles},
        tasks_per_crewmate=capture.definition.tasks_per_crewmate,
    ).games
    loader = ReplayLoader(directory)
    replay = loader.load_replay(report.game_id)
    config = capture.arm.experiment_config
    expected_kind = "experimental" if config.has_tactical_changes else "scripted"
    if (
        report.agent_factory_kind != expected_kind
        or replay.metadata.agent_factory_kind != expected_kind
        or report.experiment_config != config
        or replay.metadata.experiment_config is None
        or RecordedExperimentConfig.model_validate(
            replay.metadata.experiment_config.model_dump()
        )
        != config
    ):
        raise ValueError("normal-policy recording identity disagrees with its arm")
    if report.completion_status == "completed" and (
        not report.outcome_verified or not replay.metadata.outcome_verified
    ):
        raise ValueError("completed control lacks a verified outcome")
    if report.failed_calls or any(
        call.model != "scripted-investigation-control"
        for meeting in report.meetings
        for call in meeting.llm_calls
    ):
        raise ValueError(
            "normal-policy control contains unexpected provider or failed calls"
        )
    ticks = [
        row
        for row in read_all_entries(capture.replay_path)
        if isinstance(row, ReplayEntry)
    ]
    if not ticks or any(row.temporal_observation_version != 2 for row in ticks):
        raise ValueError("normal-policy control requires recorded temporal version 2")
    actions = {
        (row.tick, str(action["actor"])): str(action["type"])
        for row in ticks
        for action in row.actions
    }
    plans = tuple(
        PlanDecision(
            observer_id=agent.agent_id,
            plan=agent.investigation_plan,
            submitted_action=actions[(frame.tick, agent.agent_id)],
        )
        for frame in replay.ticks
        for agent in frame.agent_states
        if agent.investigation_plan is not None
    )
    if config.investigation_version is None and plans:
        raise ValueError("OFF control contains an investigation plan")
    validate_plan_sources(capture, plans)
    memories = {
        f"{meeting.meeting_id}/{ballot.voter}": loader.get_meeting_memory(
            report.game_id, meeting.meeting_id, ballot.voter
        )
        for meeting in report.meetings
        for ballot in meeting.ballots
    }
    for memory in memories.values():
        if not any(
            agent == memory.agent_id and memory.rendered_memory_text in prompt
            for agent, prompt in capture.provider.prompts
        ):
            raise ValueError(
                "reconstructed opening memory differs from supplied live input"
            )
    facts: list[ObservedFact] = []
    completions: list[TaskCompletion] = []
    for observer, agent in sorted(capture.agents.items()):
        for event in agent.memory.episodic.recent(since_tick=0):
            if event.provenance != "observed":
                continue
            if (
                event.type == "own_task_attempt"
                and event.payload.get("outcome") == "completed"
            ):
                task = _text(event, "task_id")
                if task is None:
                    raise ValueError("completed task receipt has no task identity")
                completions.append(
                    TaskCompletion(observer_id=observer, task_id=task, tick=event.tick)
                )
            if event.type not in ("saw_player", "saw_player_move", "saw_body"):
                continue
            if event.observation_id is None:
                raise ValueError("observed fact has no source identity")
            facts.append(
                ObservedFact(
                    observer_id=observer,
                    observation_id=event.observation_id,
                    tick=event.tick,
                    kind=event.type,
                    subject_id=_text(
                        event, "victim_id" if event.type == "saw_body" else "player_id"
                    ),
                    room=_text(event, "room"),
                    from_room=_text(event, "from_room"),
                    to_room=_text(event, "to_room"),
                    action=_text(event, "action"),
                )
            )
    for name, value in (
        ("view.json", replay.model_dump(mode="json")),
        (
            "memories.json",
            {key: value.model_dump(mode="json") for key, value in memories.items()},
        ),
        ("report.json", report.model_dump(mode="json")),
    ):
        with (directory / name).open("x") as stream:
            json.dump(value, stream, sort_keys=True, indent=2)
            stream.write("\n")
    ballots = [ballot for meeting in replay.meetings for ballot in meeting.ballots]
    measurement = InvestigationMeasurement(
        arm=capture.arm.name,
        case=capture.definition.name,
        replay_ref=capture.replay_path.name,
        definition=capture.definition,
        provenance=report.recorded_provenance(),
        winner=replay.metadata.winner,
        winner_reason=replay.metadata.winner_reason,
        completion_status=report.completion_status,
        outcome_verified=report.outcome_verified,
        final_recorded_tick=ticks[-1].tick,
        trajectory_sha256=_digest(
            {
                "ticks": [
                    {"tick": row.tick, "state_hash": row.state_hash} for row in ticks
                ],
                "meeting_results": [
                    {"tick": row.tick, "state_hash_after": row.state_hash_after}
                    for row in read_all_entries(capture.replay_path)
                    if isinstance(row, MeetingReplayEntry)
                ],
            }
        ),
        submitted_actions_sha256=_digest(
            [
                {
                    "tick": row.tick,
                    "actions": row.actions,
                    "dispositions": row.action_dispositions,
                }
                for row in ticks
            ]
        ),
        reader_projection_sha256=_digest(
            replay.model_dump(mode="json", exclude={"metadata": {"created_at"}})
        ),
        memory_projection_sha256=_digest(
            {key: value.model_dump(mode="json") for key, value in memories.items()}
        ),
        cost=report.cost,
        meetings=len(report.meetings),
        calls=sum(len(meeting.llm_calls) for meeting in report.meetings),
        ballots=len(ballots),
        voluntary_skips=sum(
            b.target == "SKIP" and not b.rewrite_reasons for b in ballots
        ),
        wrongful_accusations=sum(
            claim.type == "accusation" and roles[claim.against] == "CREWMATE"
            for meeting in report.meetings
            for turn in meeting.transcript.turns
            for claim in turn.claims
        ),
        body_report_ticks=tuple(
            m.tick for m in report.meetings if m.trigger == "report"
        ),
        impostor_report_ticks=tuple(
            m.tick
            for m in report.meetings
            if m.trigger == "report" and roles[m.triggered_by] == "IMPOSTOR"
        ),
        action_counts=dict(sorted(Counter(actions.values()).items())),
        action_dispositions=dict(
            sorted(
                Counter(
                    d for row in ticks for d in row.action_dispositions or ()
                ).items()
            )
        ),
        plans=plans,
        observed_facts=tuple(facts),
        task_completions=tuple(completions),
    )
    with (directory / "measurement.json").open("x") as stream:
        stream.write(measurement.model_dump_json(indent=2) + "\n")
    return measurement


class PairedInvestigationComparison(_Frozen):
    arm: str
    case: str
    reference: str = "off"
    changed_trajectory: bool
    changed_submitted_actions: bool
    common_horizon_tick: int
    added_observation_signatures: int
    removed_observation_signatures: int
    completed_task_difference_at_common_horizon: int
    matched_completion_delays: tuple[int, ...]
    unmatched_reference_completions: int
    additional_body_reports: int
    additional_calls: int


def compare_pair(
    reference: InvestigationMeasurement,
    candidate: InvestigationMeasurement,
    *,
    reference_name: str = "off",
) -> PairedInvestigationComparison:
    if reference.arm != reference_name or reference.definition != candidate.definition:
        raise ValueError(
            "paired controls must share exact seeded inputs and an OFF reference"
        )
    horizon = min(reference.final_recorded_tick, candidate.final_recorded_tick)

    def signatures(row: InvestigationMeasurement) -> set[str]:
        return {
            _digest(fact.model_dump(exclude={"observation_id"}))
            for fact in row.observed_facts
            if fact.tick <= horizon
        }

    before, after = signatures(reference), signatures(candidate)
    old_tasks = {(x.observer_id, x.task_id): x.tick for x in reference.task_completions}
    new_tasks = {(x.observer_id, x.task_id): x.tick for x in candidate.task_completions}
    return PairedInvestigationComparison(
        arm=candidate.arm,
        case=candidate.case,
        reference=reference_name,
        changed_trajectory=reference.trajectory_sha256 != candidate.trajectory_sha256,
        changed_submitted_actions=reference.submitted_actions_sha256
        != candidate.submitted_actions_sha256,
        common_horizon_tick=horizon,
        added_observation_signatures=len(after - before),
        removed_observation_signatures=len(before - after),
        completed_task_difference_at_common_horizon=sum(
            t <= horizon for t in new_tasks.values()
        )
        - sum(t <= horizon for t in old_tasks.values()),
        matched_completion_delays=tuple(
            new_tasks[key] - old_tasks[key]
            for key in sorted(old_tasks.keys() & new_tasks.keys())
        ),
        unmatched_reference_completions=len(old_tasks.keys() - new_tasks.keys()),
        additional_body_reports=len(candidate.body_report_ticks)
        - len(reference.body_report_ticks),
        additional_calls=candidate.calls - reference.calls,
    )


def paired_comparisons(
    captures: Sequence[InvestigationMeasurement],
    *,
    arms: Sequence[InvestigationArm],
    definitions: Sequence[InvestigationCaseDefinition],
) -> tuple[PairedInvestigationComparison, ...]:
    indexed = {(row.arm, row.case): row for row in captures}
    expected = {
        (arm.name, definition.name) for arm in arms for definition in definitions
    }
    if (
        not expected
        or not arms
        or arms[0].name != "off"
        or len(indexed) != len(captures)
        or set(indexed) != expected
    ):
        raise ValueError("comparison requires the complete frozen matrix")
    for arm in arms:
        for definition in definitions:
            row = indexed[(arm.name, definition.name)]
            if (
                row.definition != definition
                or row.provenance.experiment_config != arm.experiment_config
            ):
                raise ValueError("measurement disagrees with frozen input identity")
    results = tuple(
        compare_pair(
            indexed[("off", definition.name)], indexed[(arm.name, definition.name)]
        )
        for arm in arms[1:]
        for definition in definitions
    )
    if {"old_patrol", "old_accompany"} <= {arm.name for arm in arms}:
        results += tuple(
            compare_pair(
                indexed[("old_patrol", definition.name)],
                indexed[("old_accompany", definition.name)],
                reference_name="old_patrol",
            )
            for definition in definitions
        )
    if {"search", "combined_search_report"} <= {arm.name for arm in arms}:
        results += tuple(
            compare_pair(
                indexed[("search", definition.name)],
                indexed[("combined_search_report", definition.name)],
                reference_name="search",
            )
            for definition in definitions
        )
    return results


class InvestigationEvaluation(_Frozen):
    format_version: Literal[1] = 1
    verdict: Literal["MECHANICS_ONLY"] = "MECHANICS_ONLY"
    provider: Literal["scripted-investigation-control"] = (
        "scripted-investigation-control"
    )
    limitations: tuple[str, ...] = (
        "Seed-selected development trials use exact built-in tactical policies and fixed neutral/SKIP speech; no model-quality or adoption verdict.",
        "Observed signatures include observer, actual tick, subject, room and action; counts are neither independent clues nor quality scores.",
        "Changed submitted actions are separate from changed engine trajectories; discarded or rejected attempts do not necessarily change any state.",
        "Task delays match only tasks completed in both trajectories; unmatched completion counts remain explicit, not zero delays.",
        "Plans are intentions, separate from later observations. Privileged replay views and role labels never supply tactical inputs.",
        "The combination is measured after independent components; old accompaniment is compared with old patrol. No new bounded-follow version is adopted or exposed.",
    )
    source_hashes: Mapping[str, str]
    input_sha256: str
    python: str
    arms: tuple[InvestigationArm, ...]
    definitions: tuple[InvestigationCaseDefinition, ...]
    captures: tuple[InvestigationMeasurement, ...]
    comparisons: tuple[PairedInvestigationComparison, ...]
    artifact_hashes: Mapping[str, str]


def evaluate(output_dir: Path, *, root: Path) -> InvestigationEvaluation:
    """Record a finite matrix and bind it with the existing source inventory."""
    arms, definitions = comparison_arms(), development_cases()
    sources = source_hashes(root)
    inputs = _digest(
        {
            "arms": [a.model_dump(mode="json") for a in arms],
            "definitions": [d.model_dump(mode="json") for d in definitions],
        }
    )
    output_dir.mkdir(parents=True, exist_ok=False)
    captures: list[InvestigationMeasurement] = []
    for arm in arms:
        for definition in definitions:
            capture = run_case(
                output_dir / arm.name / definition.name, definition=definition, arm=arm
            )
            if capture.definition != definition or capture.arm != arm:
                raise ValueError("actual capture disagrees with its frozen inputs")
            captures.append(measure_capture(capture))
    if source_hashes(root) != sources:
        raise ValueError("implementation sources changed during capture")
    if arms != comparison_arms() or definitions != development_cases():
        raise ValueError("investigation inputs changed during capture")
    comparisons = paired_comparisons(captures, arms=arms, definitions=definitions)
    result = InvestigationEvaluation(
        source_hashes=sources,
        input_sha256=inputs,
        python=platform.python_version(),
        arms=arms,
        definitions=definitions,
        captures=tuple(captures),
        comparisons=comparisons,
        artifact_hashes={
            str(path.relative_to(output_dir)): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in sorted(output_dir.rglob("*"))
            if path.is_file()
        },
    )
    with (output_dir / "evaluation.json").open("x") as stream:
        stream.write(result.model_dump_json(indent=2) + "\n")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    result = evaluate(args.output_dir, root=Path(__file__).resolve().parents[1])
    print(
        f"{result.verdict}: {len(result.captures)} normal-policy development controls"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
