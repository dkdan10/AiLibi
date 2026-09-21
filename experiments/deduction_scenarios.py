"""Finite scripted mechanics cases; provider output is not model-quality evidence."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, TypeAdapter

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.perception import ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import Role
from engine.world import load_canonical_map
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from meetings.schemas import MeetingTurn, ModelAuthoredVoteBallot
from observation.action_intent import ActionIntent, WaitIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import (
    HeadlessGame,
    HeadlessGameResult,
    TacticalAgent,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler

ScenarioCase: TypeAlias = Literal[
    "honest",
    "impossible_account",
    "insufficient_evidence",
    "already_known_dead",
    "witnessed_kill",
    "witnessed_vent",
    "late_accusation",
]


class ScenarioStep(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    tick: int
    action: ActionIntent


class ScenarioDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    version: Literal[1, 2] = 2
    case: ScenarioCase
    seed: Literal[1] = 1
    num_players: Literal[4] = 4
    num_impostors: Literal[1] = 1
    tasks_per_crewmate: Literal[1] = 1
    max_ticks: Literal[14] = 14
    steps: tuple[ScenarioStep, ...]
    claimed_room: str
    claimed_tick: Literal[5] = 5
    expected_kill_tick: Literal[4] = 4
    expected_report_tick: int
    information_limit: str
    route_rationale: str = (
        "Seed 1 starts all four players in CAFETERIA with a four-tick kill cooldown. "
        "ADMIN is reachable by two legal doors and contains p-2's assigned upload task. "
        "The reporter can leave before the kill and return before the killer's ordered departure, "
        "creating movement evidence without a witnessed kill or vent. "
        "WEST_HALL and REACTOR are four walking doors apart, beyond one same-tick move."
    )


def scenario_definition(case: ScenarioCase) -> ScenarioDefinition:
    """Freeze legal inputs before capture; every unlisted action is an explicit wait."""
    if case not in (
        "honest",
        "impossible_account",
        "insufficient_evidence",
        "already_known_dead",
        "witnessed_kill",
        "witnessed_vent",
        "late_accusation",
    ):
        raise ValueError("unknown deduction scenario")
    routes = {
        "p-1": {0: "UPPER_HALL", 1: "ADMIN"},
        "p-2": {0: "EAST_HALL", 1: "ADMIN", 3: "UPPER_HALL", 5: "ADMIN"},
        "p-3": {0: "WEST_HALL", 1: "MEDBAY", 2: "LABS"},
        "p-4": {0: "UPPER_HALL", 1: "ADMIN", 5: "WEST_HALL", 8: "ADMIN"},
    }
    report_tick = 6
    if case == "insufficient_evidence":
        routes["p-2"] = {
            0: "WEST_HALL",
            1: "MEDBAY",
            2: "LABS",
            3: "MEDBAY",
            4: "WEST_HALL",
            6: "ADMIN",
        }
        report_tick = 7
        routes["p-4"][5] = "EAST_HALL"
    if case == "already_known_dead":
        # p-3 calls before p-4's action at tick 5. The rejected/discarded
        # departure creates no movement observation or actor receipt.
        routes["p-4"].pop(5)
        routes["p-3"] = {
            0: "WEST_HALL",
            1: "MEDBAY",
            2: "WEST_HALL",
            3: "CAFETERIA",
            6: "UPPER_HALL",
            7: "ADMIN",
            9: "UPPER_HALL",
        }
        routes["p-2"].pop(5)
        routes["p-2"][7] = "ADMIN"
        report_tick = 8
    if case == "witnessed_kill":
        routes["p-2"].pop(3)
        routes["p-2"].pop(5)
    if case == "witnessed_vent":
        routes["p-4"].pop(5)
        routes["p-4"].pop(8)
    raw: list[tuple[int, str, str, dict[str, str]]] = [
        (tick, actor, "move", {"to_room": room})
        for actor, route in routes.items()
        for tick, room in route.items()
    ]
    raw.extend(
        [
            (2, "p-4", "do_task", {"task_id": "upload_logs"}),
            (4, "p-4", "kill", {"target": "p-1"}),
            (report_tick, "p-2", "report", {"body_id": "body-p-1"}),
            (12, "p-4", "kill", {"target": "p-2"}),
        ]
    )
    if case == "witnessed_vent":
        raw.extend(
            [
                (5, "p-4", "vent", {"vent_id": "ADMIN_VENT"}),
                (8, "p-4", "vent", {"vent_id": "ADMIN_VENT"}),
            ]
        )
    if case != "insufficient_evidence":
        raw.append((2, "p-2", "do_task", {"task_id": "upload_logs"}))
    if case == "already_known_dead":
        raw.append(
            (5, "p-3", "emergency", {"reason": "We should compare what we know."})
        )
    steps = tuple(
        ScenarioStep(
            tick=tick,
            action=TypeAdapter(ActionIntent).validate_python(
                {"actor": actor, "type": kind, "payload": payload}
            ),
        )
        for tick, actor, kind, payload in sorted(raw, key=lambda row: (row[0], row[1]))
    )
    return ScenarioDefinition(
        case=case,
        steps=steps,
        expected_report_tick=report_tick,
        claimed_room="REACTOR"
        if case in ("impossible_account", "insufficient_evidence")
        else "ADMIN"
        if case == "already_known_dead"
        else "WEST_HALL",
        information_limit=(
            "Direct-evidence positive control. "
            if case in ("witnessed_kill", "witnessed_vent")
            else "No witnessed kill or vent. "
        )
        + "Scripted testimony and votes demonstrate mechanics only; the scenario has no fresh-model quality verdict.",
    )


class _ScenarioAgent(TacticalAgent):
    def __init__(
        self,
        *,
        agent_id: str,
        role: Role,
        definition: ScenarioDefinition,
        memory: AgentMemory,
        perception_beliefs: dict[tuple[int, str], Mapping[str, float]],
    ) -> None:
        policy = (
            ImpostorPolicy(agent_id=agent_id)
            if role == "IMPOSTOR"
            else CrewmatePolicy(agent_id=agent_id)
        )
        super().__init__(agent_id=agent_id, policy=policy, role=role, memory=memory)
        self._definition = definition
        self._perception_beliefs = perception_beliefs

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        # Preserve the real typed perception seam, without an unused tactical
        # action mutating policy state before the predetermined legal action.
        del public_map
        ingest_packet(
            packet=packet, memory=self.memory.episodic, beliefs=self.memory.beliefs
        )
        self._perception_beliefs[(packet.tick, self.agent_id)] = MappingProxyType(
            {
                pid: self.memory.beliefs.view(pid).suspicion
                for pid in self.memory.beliefs.known_players()
            }
        )
        for step in self._definition.steps:
            if step.tick == packet.tick and step.action.actor == self.agent_id:
                return step.action
        return WaitIntent(type="wait", actor=self.agent_id)


class ScriptedDeductionProvider(FakeProvider):
    """Closed, deterministic speech fixture. Claims are deliberately not certified."""

    def __init__(
        self, definition: ScenarioDefinition, *, public_accounts: bool = False
    ) -> None:
        if definition.version != 2:
            raise ValueError("scripted provider requires scenario definition version 2")
        self.definition = definition
        self.public_accounts = public_accounts
        self.prompts: list[tuple[str | None, str]] = []
        self._turn_counts: dict[str | None, int] = {}

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
        self.prompts.append((agent_id, prompt))
        response: BaseModel
        if schema is MeetingTurn:
            prior_turns = self._turn_counts.get(agent_id, 0)
            self._turn_counts[agent_id] = prior_turns + 1
            observations: list[dict[str, object]] = []
            claims: list[dict[str, object]] = []
            free_text = (
                "I am unsure; compare these placements with what you actually observed."
            )
            if agent_id == "p-2":
                observations.append(
                    {
                        "type": "found_body",
                        "tick": self.definition.expected_report_tick,
                        "body_of": "p-1",
                        "room": "ADMIN",
                    }
                )
                claims.append(
                    {
                        "type": "accusation",
                        "against": "p-4",
                        "confidence": 0.5,
                        "reason": "Please explain your route around the discovery.",
                    }
                )
                movement = self._supplied_movement(prompt)
                if movement is not None:
                    observations.append(
                        {
                            "type": "saw_move",
                            "tick": movement.tick,
                            "subject": "p-4",
                            "from_room": "ADMIN",
                            "to_room": "WEST_HALL",
                        }
                    )
                    free_text = (
                        f"I saw p-4 move from ADMIN to WEST_HALL at tick {movement.tick}. "
                        "Please explain where you were around that departure. "
                        "I did not witness the kill."
                    )
            if self.definition.case == "late_accusation" and agent_id == "p-3":
                claims.append(
                    {
                        "type": "accusation",
                        "against": "p-2",
                        "confidence": 0.5,
                        "reason": "Reporter, explain why you returned to the body room.",
                    }
                )
            if agent_id == "p-4":
                observations.append(
                    {
                        "type": "whereabouts",
                        "tick": self.definition.claimed_tick,
                        "room": self.definition.claimed_room,
                    }
                )
            if agent_id == "p-2" and self.definition.case in (
                "witnessed_kill",
                "witnessed_vent",
            ):
                observations.append(
                    {
                        "type": "saw_kill"
                        if self.definition.case == "witnessed_kill"
                        else "saw_vent",
                        "subject": "p-4",
                        "room": "ADMIN",
                        "tick": 4 if self.definition.case == "witnessed_kill" else 5,
                    }
                )
            if self.public_accounts and (
                agent_id == "p-4"
                or (
                    agent_id == "p-2"
                    and self.definition.case != "insufficient_evidence"
                )
            ):
                observations.append(
                    {
                        "type": "task_activity",
                        "task_id": "upload_logs",
                        "room": "ADMIN",
                        "from_tick": 2,
                        "to_tick": 2,
                    }
                )
            # The emergency before the later body report cannot assert future
            # discovery. It opens with honest uncertainty and no accusation.
            if (
                self.definition.case == "already_known_dead"
                and agent_id == "p-2"
                and prior_turns == 0
            ):
                observations, claims = [], []
            if (
                self.definition.case == "late_accusation"
                and agent_id == "p-2"
                and prior_turns > 0
            ):
                observations = [
                    {"type": "whereabouts", "tick": 5, "room": "UPPER_HALL"},
                    {"type": "whereabouts", "tick": 6, "room": "ADMIN"},
                ]
                claims = []
                free_text = (
                    "I was in UPPER_HALL before returning to ADMIN, where I had been "
                    "working on upload logs. I found the body after returning; "
                    "I did not witness the kill."
                )
            response = MeetingTurn.model_validate(
                {
                    "turn_id": "script",
                    "turn_index": 0,
                    "speaker": agent_id,
                    "turn_kind": "opening",
                    "reply_to": None,
                    "observations": observations,
                    "claims": claims,
                    "free_text": free_text,
                }
            )
        elif schema is ModelAuthoredVoteBallot:
            movement = self._supplied_movement(prompt) if agent_id == "p-2" else None
            response = ModelAuthoredVoteBallot(
                voter=agent_id or "p-2",
                target="SKIP",
                confidence=1.0,
                primary_reason_id=None,
                primary_reason_observation_id=movement.observation_id
                if movement is not None
                else None,
                considered_alternatives=(),
                rationale_text=(
                    "I saw the departure, but a placement alone does not identify the killer. "
                    if movement is not None
                    else ""
                )
                + "The scripted control abstains; these votes do not measure reasoning quality.",
            )
        else:
            return await super().complete(
                prompt=prompt,
                schema=schema,
                max_tokens=max_tokens,
                temperature=temperature,
                call_kind=call_kind,
                model=model,
                agent_id=agent_id,
            )
        text = response.model_dump_json()
        return LLMResponse(
            text=text,
            usage=TokenUsage(
                input_tokens=max(1, len(prompt) // 4),
                output_tokens=max(1, len(text) // 4),
            ),
            cost_usd=0.0,
            model="scripted-deduction-control",
        )

    def _supplied_movement(self, prompt: str) -> _SuppliedMovement | None:
        """Copy this fixture's real movement line; IDs never supply its clock.

        Restrict extraction to the supplied private-memory block. Public claims,
        earlier calls and the privileged scenario capture cannot supply a missing
        observation. Legacy display time remains legacy display time.
        """
        if self.definition.case not in (
            "honest",
            "impossible_account",
            "late_accusation",
        ):
            return None
        if "<memory>" in prompt:
            memory, closing, _ = prompt.partition("<memory>")[2].partition("</memory>")
            if not closing:
                return None
        else:
            _, opening, memory = prompt.partition("## Your private memory\n")
            if not opening:
                return None
            boundaries = [
                index
                for marker in (
                    "\n## What players said",
                    "\nPublic accounts are statements",
                )
                if (index := memory.find(marker)) >= 0
            ]
            if not boundaries:
                return None
            memory = memory[: min(boundaries)]
        matches: list[_SuppliedMovement] = []
        for line in memory.splitlines():
            match = re.fullmatch(
                r"- \[obs ([^\]\n]+)\] \[(?:tick (\d+)|during tick (\d+), your observation \d+)\] "
                r"You (?:saw|witnessed) p-4 move from ADMIN to WEST_HALL\."
                r"(?: You were in ADMIN immediately before this event\.)?",
                line,
            )
            if match is not None:
                matches.append(
                    _SuppliedMovement(
                        observation_id=match.group(1),
                        tick=int(match.group(2) or match.group(3)),
                    )
                )
        return matches[0] if len(matches) == 1 else None


@dataclass(frozen=True)
class _SuppliedMovement:
    observation_id: str
    tick: int


@dataclass(frozen=True)
class ScenarioCapture:
    """Privileged test instrumentation; never serialize hidden memories publicly."""

    definition: ScenarioDefinition
    replay_path: Path
    result: HeadlessGameResult
    agents: Mapping[str, TacticalAgent]
    provider: LLMClient
    perception_beliefs: Mapping[tuple[int, str], Mapping[str, float]]


def run_case(
    output_dir: Path,
    *,
    case: ScenarioCase,
    experiment_config: RecordedExperimentConfig,
    temporal_version: Literal[1, 2] | None = 2,
    llm_client: LLMClient | None = None,
) -> ScenarioCapture:
    definition = scenario_definition(case)
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    provider = (
        llm_client
        if llm_client is not None
        else ScriptedDeductionProvider(
            definition, public_accounts=experiment_config.public_account_version == 1
        )
    )
    env = {
        "AILIBI_LLM_PROVIDER": "fake",
        "AILIBI_PROMPT_SET": "qwen3_6_27b",
        "AILIBI_TEMPORAL_OBSERVATIONS": str(temporal_version or 0),
        "AILIBI_EVIDENCE_REASONING": str(
            experiment_config.evidence_reasoning_version or 0
        ),
        "AILIBI_PUBLIC_ACCOUNTS": str(experiment_config.public_account_version or 0),
        "AILIBI_ATTRIBUTED_TESTIMONY": str(
            experiment_config.attributed_testimony_version or 0
        ),
        "AILIBI_BOUNDED_REBUTTAL": str(experiment_config.bounded_rebuttal_version or 0),
    }
    runner = build_default_meeting_runner(
        llm_client=provider, env=env, public_map=public_map
    )
    agents: dict[str, TacticalAgent] = {}
    perception_beliefs: dict[tuple[int, str], Mapping[str, float]] = {}

    def factory(agent_id: str, role: Role) -> AgentInterface:
        agent = _ScenarioAgent(
            agent_id=agent_id,
            role=role,
            definition=definition,
            perception_beliefs=perception_beliefs,
            memory=AgentMemory(
                evidence_reasoning_version=experiment_config.evidence_reasoning_version,
                public_account_version=experiment_config.public_account_version,
                attributed_testimony_version=experiment_config.attributed_testimony_version,
                public_map=public_map,
            ),
        )
        agents[agent_id] = agent
        return agent

    path = output_dir / "replay-seed-1.jsonl"
    result = HeadlessGame(
        seed=definition.seed,
        num_players=definition.num_players,
        num_impostors=definition.num_impostors,
        tasks_per_crewmate=definition.tasks_per_crewmate,
        game_map=game_map,
        agent_factory=factory,
        replay_path=path,
        scheduler=TickScheduler(max_ticks=definition.max_ticks),
        meeting_runner=runner,
        experiment_config=experiment_config,
        temporal_observation_version=temporal_version,
        substrate_flags=runner.substrate_flags,
    ).run()
    return ScenarioCapture(
        definition=definition,
        replay_path=path,
        result=result,
        agents=MappingProxyType(agents),
        provider=provider,
        perception_beliefs=MappingProxyType(perception_beliefs),
    )
