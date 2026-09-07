"""Real orchestration delivers source-time evidence before meetings exactly once."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from agents.base import AgentInterface
from agents.memory.store import AgentMemory
from agents.perception import ingest_event_observations
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from api.replay_loader import ReplayLoader
from api.schemas import AgentMemoryView
from engine.entities import BodyState, PlayerId, Role
from engine.world import WorldState, load_canonical_map
from llm.fake_provider import FakeProvider
from meetings.manager import MeetingTrigger
from meetings.schemas import MeetingResult, MeetingTranscript, VoteBallot
from observation.action_intent import ActionIntent, WaitIntent
from observation.packet import EventObservationBatch, ObservationPacket, PlayerView
from observation.public_map import PublicMapView
from orchestrator.game import (
    HeadlessGame,
    MeetingArtifacts,
    TacticalAgent,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    ReplayEntry,
    read_all_entries,
    recorded_temporal_observations,
)
from orchestrator.replay_integrity import ReplayIntegrityError
from orchestrator.scheduler import TickScheduler
from tests.observation.test_service import _base_world_state, _player


class _ScenarioAgent(TacticalAgent):
    def __init__(self, agent_id: str, role: Role, *, kill_witness: bool) -> None:
        policy = (
            ImpostorPolicy(agent_id=agent_id)
            if role == "IMPOSTOR"
            else CrewmatePolicy(agent_id=agent_id)
        )
        super().__init__(agent_id=agent_id, policy=policy, role=role)
        self.kill_witness = kill_witness

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        super().decide(packet, public_map)
        if packet.tick == 0:
            planned: dict[str, tuple[str, dict[str, str]]] = {
                "p-1": ("vent", {"vent_id": "ADMIN_VENT"}),
                "p-6": ("report", {"body_id": "body-p-8"}),
            }
            if self.kill_witness:
                planned["p-3"] = ("kill", {"target": "p-2"})
            if self.agent_id in planned:
                kind, payload = planned[self.agent_id]
                return TypeAdapter(ActionIntent).validate_python(
                    {"type": kind, "actor": self.agent_id, "payload": payload}
                )
        return WaitIntent(type="wait", actor=self.agent_id)


class _InspectMeeting:
    def __init__(self, *, eject_witness: bool) -> None:
        self.eject_witness = eject_witness
        self.vent_ticks: list[int] = []

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        witness = agents["p-2"]
        assert isinstance(witness, TacticalAgent)
        self.vent_ticks = [
            record.tick for record in witness.vent_witness_records_for_meeting()
        ]
        target = "p-2" if self.eject_witness else None
        return MeetingArtifacts(
            result=MeetingResult(
                meeting_id=meeting_id,
                triggered_by=trigger.triggered_by,
                trigger_tick=trigger.trigger_tick,
                outcome="EJECTED" if target else "SKIPPED",
                ejected_player_id=target,
                transcript=MeetingTranscript(),
                ballots=tuple(
                    VoteBallot(
                        voter=pid,
                        target=target if target and pid != target else "SKIP",
                        confidence=1.0,
                        primary_reason_id=None,
                        considered_alternatives=(),
                        rationale_text="scripted vote",
                    )
                    for pid, player in state.players.items()
                    if player.alive
                ),
            ),
            llm_calls=(),
            prompt_versions={},
        )


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("fate", ["alive", "killed", "ejected"])
def test_same_tick_vent_reaches_meeting_and_survives_witness_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, enabled: bool, fate: str
) -> None:
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1" if enabled else "0")
    initial = _base_world_state()
    players = {
        pid: _player(
            pid, "IMPOSTOR" if pid in ("p-1", "p-3") else "CREWMATE", room, (0.0, 0.0)
        )
        for pid, room in (
            ("p-1", "ADMIN"),
            ("p-2", "ADMIN"),
            ("p-3", "ADMIN"),
            ("p-4", "STORAGE"),
            ("p-5", "ENGINEERING"),
            ("p-6", "CAFETERIA"),
            ("p-7", "CAFETERIA"),
            ("p-8", "CAFETERIA"),
        )
    }
    players["p-8"] = replace(players["p-8"], alive=False)
    initial = replace(
        initial,
        players=players,
        cooldowns={"p-1": 0, "p-3": 0},
        bodies={
            "body-p-8-0": BodyState(
                id="body-p-8-0",
                player_id="p-8",
                room="CAFETERIA",
                position=(0.0, 0.0),
                killed_by="p-1",
                discovered_by=None,
            )
        },
    )
    agents: dict[str, _ScenarioAgent] = {}

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        agent = _ScenarioAgent(agent_id, role, kill_witness=fate == "killed")
        agents[agent_id] = agent
        return agent

    meeting = _InspectMeeting(eject_witness=fate == "ejected")
    game = HeadlessGame(
        seed=initial.seed,
        num_players=8,
        num_impostors=2,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=factory,
        replay_path=None,
        initial_state=initial,
        scheduler=TickScheduler(max_ticks=2),
        meeting_runner=meeting,
    )
    game.run_unrecorded()
    assert meeting.vent_ticks == ([0] if enabled else [])
    after = agents["p-2"].vent_witness_records_for_meeting()
    assert [event.tick for event in after] == (
        [0] if enabled else [1] if fate == "alive" else []
    )
    observed = [
        event
        for event in agents["p-2"].memory.episodic.recent(since_tick=0)
        if event.observation_id is not None
    ]
    assert len({event.observation_id for event in observed}) == len(observed)


def test_redelivery_does_not_reapply_beliefs_or_add_citations() -> None:
    memory = AgentMemory()
    batch = EventObservationBatch(
        tick=0,
        agent_id="p-1",
        witnessed_actions=(PlayerView(id="p-2", room="ADMIN", action="vent"),),
    )
    first = ingest_event_observations(
        batch=batch, memory=memory.episodic, beliefs=memory.beliefs
    )
    memory.beliefs.adjust_suspicion("p-2", delta=-0.2)
    before = memory.beliefs.copy()
    assert (
        ingest_event_observations(
            batch=batch, memory=memory.episodic, beliefs=memory.beliefs
        )
        == ()
    )
    assert memory.beliefs.view("p-2") == before.view("p-2")
    assert memory.episodic.recent(since_tick=0) == first


@pytest.mark.parametrize("mutation", [None, "mixed", "stamp"])
def test_versioned_real_recording_loads_and_rejects_conflicting_metadata(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutation: str | None
) -> None:
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1")
    path = tmp_path / "replay-seed-1.jsonl"
    HeadlessGame(
        seed=1,
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=80),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
    ).run()
    entries = read_all_entries(path)
    assert recorded_temporal_observations(entries)
    assert all(
        entry.temporal_observation_version == 1
        for entry in entries
        if isinstance(entry, ReplayEntry)
    )
    if mutation is not None:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if mutation == "mixed":
            rows[0].pop("temporal_observation_version")
        else:
            rows[-1]["substrate_flags"]["temporal_observations"] = False
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
        with pytest.raises(ReplayIntegrityError, match="observation_version_mismatch"):
            ReplayLoader(tmp_path).load_replay("headless-seed-1")
    else:
        replay = ReplayLoader(tmp_path).load_replay("headless-seed-1")
        assert replay.metadata.outcome_verified
        assert replay.metadata.meeting_count > 0


class _CaptureMeeting:
    def __init__(self) -> None:
        self.inner = build_default_meeting_runner(llm_client=FakeProvider())
        self.snapshots: dict[
            tuple[str, str], tuple[str, dict[str, float], tuple[str, ...]]
        ] = {}

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        for pid, agent in agents.items():
            assert isinstance(agent, TacticalAgent)
            self.snapshots[(meeting_id, pid)] = (
                agent.render_memory_for_meeting(),
                {
                    subject: agent.memory.beliefs.view(subject).suspicion
                    for subject in agent.memory.beliefs.known_players()
                },
                tuple(
                    event.observation_id
                    for event in agent.memory.episodic.recent(since_tick=0)
                    if event.observation_id is not None
                ),
            )
        return await self.inner.run_meeting(
            meeting_id=meeting_id, trigger=trigger, state=state, agents=agents
        )


class _InspectLoader(ReplayLoader):
    def __init__(self, directory: Path) -> None:
        super().__init__(directory)
        self.ids: dict[tuple[str, str], tuple[str, ...]] = {}

    def _agent_memory_view(
        self,
        *,
        agent_id: str,
        tick: int,
        meeting_state: WorldState,
        memory: AgentMemory,
        meeting_entry: MeetingReplayEntry | None,
        observation_scene_ticks: Mapping[str, int] | None = None,
    ) -> AgentMemoryView:
        assert meeting_entry is not None
        self.ids[(meeting_entry.meeting_id, agent_id)] = tuple(
            event.observation_id
            for event in memory.episodic.recent(since_tick=0)
            if event.observation_id is not None
        )
        return super()._agent_memory_view(
            agent_id=agent_id,
            tick=tick,
            meeting_state=meeting_state,
            memory=memory,
            meeting_entry=meeting_entry,
            observation_scene_ticks=observation_scene_ticks,
        )


@pytest.mark.parametrize("enabled", [False, True])
def test_real_live_and_reader_meeting_memory_are_identical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, enabled: bool
) -> None:
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1" if enabled else "0")
    meeting = _CaptureMeeting()
    path = tmp_path / "replay-seed-1.jsonl"
    HeadlessGame(
        seed=1,
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=80),
        meeting_runner=meeting,
    ).run()
    assert len(meeting.snapshots) >= 14  # At least two boundaries, all seven memories.
    loader = _InspectLoader(tmp_path)
    for (meeting_id, pid), (text, suspicion, ids) in meeting.snapshots.items():
        memory = loader.get_meeting_memory("headless-seed-1", meeting_id, pid)
        assert memory.rendered_memory_text == text, (meeting_id, pid)
        assert {
            belief.subject: belief.suspicion for belief in memory.beliefs
        } == suspicion
        assert loader.ids[(meeting_id, pid)] == ids


def test_partial_recording_selects_own_temporal_profile_when_environment_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1")
    path = tmp_path / "replay-seed-1.jsonl"
    HeadlessGame(
        seed=1,
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=1),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
    ).run()
    entries = read_all_entries(path)
    assert recorded_temporal_observations(entries)
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "0")
    replay = ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert replay.metadata.completion_status == "tick_limited"
    assert not replay.metadata.outcome_verified


@pytest.mark.parametrize("enabled", [False, True])
def test_opening_prompt_body_handle_privacy_is_explicitly_versioned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, enabled: bool
) -> None:
    import re

    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1" if enabled else "0")
    path = tmp_path / "replay-seed-1.jsonl"
    HeadlessGame(
        seed=1,
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=80),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
    ).run()
    entries = read_all_entries(path)
    prompts = [
        call.prompt
        for entry in entries
        if isinstance(entry, MeetingReplayEntry)
        for call in entry.llm_calls
    ]
    assert prompts
    body_triggers = [prompt for prompt in prompts if "reported body body-p-" in prompt]
    assert body_triggers
    hidden_handles = [
        match
        for prompt in prompts
        for match in re.findall(r"\bbody-p-\d+-\d+\b", prompt)
    ]
    if enabled:
        assert hidden_handles == []
        assert any(
            "reported body body-p-3 at tick 8" in prompt for prompt in body_triggers
        )
    else:
        # Compatibility control: the known model-facing exposure remains OFF.
        assert "body-p-3-4" in hidden_handles
        assert any(
            "reported body body-p-3-4 at tick 8" in prompt for prompt in body_triggers
        )


@pytest.mark.parametrize("enabled", [False, True])
def test_frozen_walk_profiles_refuse_unimplemented_temporal_delivery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, enabled: bool
) -> None:
    from typing import NoReturn
    from eval.replay_walk import ReplayWalkConfig, WalkViolation, walk_replay

    def reject(violation: WalkViolation) -> NoReturn:
        raise AssertionError(violation)

    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1" if enabled else "0")
    path = tmp_path / "replay-seed-1.jsonl"
    HeadlessGame(
        seed=1,
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=1),
    ).run()
    stream = walk_replay(
        path,
        seed=1,
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        config=ReplayWalkConfig(profile="frozen-instrument", on_violation=reject),
    )
    from tests.meetings.test_prompt_byte_golden import walk_replay_meetings

    frozen_prompts = walk_replay_meetings(
        path, game_map=load_canonical_map(), renderers_for_set={}
    )
    if enabled:
        with pytest.raises(ValueError, match="does not support temporal observations"):
            list(stream)
        with pytest.raises(
            ValueError,
            match="frozen prompt-byte reconstruction does not support temporal observations",
        ):
            list(frozen_prompts)
    else:
        assert list(stream)
        assert list(frozen_prompts) == []


def test_missing_post_record_flag_means_legacy_and_default_tick_bytes_stay_unchanged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "0")
    path = tmp_path / "replay-seed-1.jsonl"
    HeadlessGame(
        seed=1,
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=80),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
    ).run()
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert all("temporal_observation_version" not in row for row in rows)
    flags = rows[-1]["substrate_flags"]
    assert flags.pop("temporal_observations") is False
    assert len(flags) == 25
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    assert not recorded_temporal_observations(read_all_entries(path))
    assert (
        ReplayLoader(tmp_path).load_replay("headless-seed-1").metadata.outcome_verified
    )


def test_temporal_factory_sweep_scans_entitled_event_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from eval.leak_scan import scan_factory_packets

    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1")
    assert scan_factory_packets(build_default_agent_factory(), seeds=(0, 1)) > 0


@pytest.mark.parametrize("enabled", [False, True])
def test_frozen_surrogate_table_rejects_temporal_sources(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, enabled: bool
) -> None:
    from training.surrogate.dataset import build_meeting_table

    monkeypatch.setenv("AILIBI_TEMPORAL_OBSERVATIONS", "1" if enabled else "0")
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2})
    )
    path = tmp_path / "replay-seed-12.jsonl"
    HeadlessGame(
        seed=12,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=path,
        scheduler=TickScheduler(max_ticks=120),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
    ).run()
    if enabled:
        with pytest.raises(
            ValueError,
            match="frozen surrogate meeting table does not support temporal observations",
        ):
            build_meeting_table(tmp_path)
    else:
        assert build_meeting_table(tmp_path).rows
