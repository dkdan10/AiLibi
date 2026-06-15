"""Meeting / orchestrator integration tests (Task 3.12).

Anchored to DESIGN.md §3.1, §5.1, §11.4. The orchestrator owns the
engine ↔ MeetingManager handoff: when the engine transitions to
``MEETING`` phase the runner is dispatched, the returned
:class:`MeetingResult` flows through :func:`apply_meeting_result`, and
the game loop resumes at tick ``t+1``. These tests pin the contract:

* an ``EJECTED`` outcome marks the named player dead, drops their
  incomplete tasks, removes their cooldown entry, and advances the
  tick;
* a ``SKIPPED`` outcome leaves living players untouched but still
  advances tick + rng;
* an ejection that satisfies a win condition emits a
  :class:`GameOverEvent` instead of resuming;
* the orchestrator refuses to apply a meeting result outside ``MEETING``
  phase (engine purity gate);
* the legacy ``MEETING_PHASE_REACHED`` outcome is preserved when no
  :class:`MeetingRunner` is configured;
* the runner sees the engine's :class:`MeetingTrigger` payload built
  from the emitted :class:`MeetingTriggeredEvent`;
* the runner cannot mutate engine state directly — every state change
  goes through the orchestrator.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel, TypeAdapter

from engine.entities import BodyState, PlayerId, PlayerState, Role
from engine.world import Map, WorldState, load_canonical_map
from llm.budget import GameBudget
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingTrigger,
    SuspicionEntry,
)
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    TurnKind,
    VoteBallot,
)
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    DefaultMeetingRunner,
    HeadlessGame,
    MeetingArtifacts,
    TacticalAgent,
    _assert_no_emergency_opening_body,  # noqa: PLC2701
    _build_participants,  # noqa: PLC2701
    apply_meeting_result,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    MeetingReplayEntry,
    read_all_entries,
    read_meeting_entries,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)
_T = TypeVar("_T")


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


def _intent(data: object) -> ActionIntent:
    return _INTENT_ADAPTER.validate_python(data)


class _ScriptedAgent:
    """Test-only agent that replays a fixed intent sequence."""

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        intents: Iterable[ActionIntent] = (),
    ) -> None:
        self._agent_id = agent_id
        self._intents = list(intents)
        self._default = _intent({"type": "wait", "actor": agent_id, "payload": {}})
        self._cursor = 0

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        if self._cursor < len(self._intents):
            intent = self._intents[self._cursor]
            self._cursor += 1
            return intent
        return self._default


@dataclass
class _CannedMeetingRunner:
    """Test runner that returns a hand-built :class:`MeetingArtifacts`.

    The runner records every dispatch it sees so tests can assert on
    the trigger payload, the state snapshot it received, and the agent
    mapping. It accepts a callable that maps ``meeting_id`` to a
    :class:`MeetingResult`; the default returns a ``SKIPPED`` result.
    """

    result_builder: Callable[[str, MeetingTrigger], MeetingResult]
    llm_calls_per_meeting: int = 0
    prompt_versions: Mapping[str, str] = field(
        default_factory=lambda: {"crewmate_report": "test.v0"}
    )
    received: list[tuple[str, MeetingTrigger, WorldState, tuple[PlayerId, ...]]] = (
        field(default_factory=list)
    )

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, object],
    ) -> MeetingArtifacts:
        self.received.append((meeting_id, trigger, state, tuple(sorted(agents))))
        result = self.result_builder(meeting_id, trigger)
        # Synthesize a fake ``llm_calls`` tuple of the requested
        # length so the replay record carries non-trivial metadata.
        from orchestrator.replay import LLMCallRecord

        llm_calls = tuple(
            LLMCallRecord(
                call_kind="meeting",
                model="canned-model",
                prompt=f"prompt-{idx}",
                response_text=f"response-{idx}",
                input_tokens=10 + idx,
                output_tokens=5 + idx,
                cost_usd=0.001 * (idx + 1),
            )
            for idx in range(self.llm_calls_per_meeting)
        )
        return MeetingArtifacts(
            result=result,
            llm_calls=llm_calls,
            prompt_versions=dict(self.prompt_versions),
        )


def _skip_result(meeting_id: str, trigger: MeetingTrigger) -> MeetingResult:
    return MeetingResult(
        meeting_id=meeting_id,
        triggered_by=trigger.triggered_by,
        trigger_tick=trigger.trigger_tick,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
        contradictions=(),
        transcript=MeetingTranscript(),
    )


def _eject_result(target: PlayerId) -> Callable[[str, MeetingTrigger], MeetingResult]:
    def _build(meeting_id: str, trigger: MeetingTrigger) -> MeetingResult:
        ballot = VoteBallot(
            voter=trigger.triggered_by,
            target=target,
            confidence=0.9,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=f"eject {target}",
        )
        return MeetingResult(
            meeting_id=meeting_id,
            triggered_by=trigger.triggered_by,
            trigger_tick=trigger.trigger_tick,
            outcome="EJECTED",
            ejected_player_id=target,
            ballots=(ballot,),
            contradictions=(),
            transcript=MeetingTranscript(),
        )

    return _build


# ---------------------------------------------------------------------------
# apply_meeting_result — pure orchestrator function.
# ---------------------------------------------------------------------------


def _meeting_state_with_body(game_map: Map) -> tuple[WorldState, str]:
    """Build a state in MEETING phase with one dead player and a body."""

    base = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
    body_id = "body-p-2-1"
    body = BodyState(
        id=body_id,
        player_id="p-2",
        room=game_map.spawn.room,
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by="p-1",
    )
    players: dict[PlayerId, PlayerState] = dict(base.players)
    players["p-2"] = replace(players["p-2"], alive=False)
    return (
        replace(
            base,
            phase="MEETING",
            bodies={body_id: body},
            players=players,
            tick=42,
        ),
        body_id,
    )


class TestApplyMeetingResult:
    def test_skip_advances_tick_and_phase(self) -> None:
        game_map = load_canonical_map()
        state, _ = _meeting_state_with_body(game_map)
        trigger = MeetingTrigger(triggered_by="p-1", trigger_tick=42, description="x")
        result = _skip_result("g-1:meeting-0", trigger)

        next_state, events = apply_meeting_result(state, result, game_map=game_map)

        assert next_state.phase == "PLAY"
        assert next_state.tick == state.tick + 1
        assert events == []
        # Living players unchanged.
        for player_id, before in state.players.items():
            assert next_state.players[player_id].alive == before.alive

    def test_eject_kills_player_and_drops_incomplete_tasks(self) -> None:
        game_map = load_canonical_map()
        # Use a larger lobby so ejecting one crewmate doesn't reach parity.
        base = seed_initial_state(seed=2026, game_map=game_map, num_players=5)
        state = replace(base, phase="MEETING", tick=42)
        # Pick the first crewmate with an incomplete task; eject them.
        target = next(
            pid
            for pid, p in sorted(state.players.items())
            if p.alive and p.role == "CREWMATE"
        )
        assert any(
            task.owner == target and not task.completed for task in state.tasks.values()
        ), "fixture must include at least one incomplete task for the target"

        trigger = MeetingTrigger(triggered_by="p-1", trigger_tick=42, description="x")
        result = _eject_result(target)("g-1:meeting-0", trigger)

        next_state, events = apply_meeting_result(state, result, game_map=game_map)

        assert next_state.players[target].alive is False
        assert next_state.players[target].last_action is None
        assert target not in next_state.cooldowns
        assert not any(
            task.owner == target and not task.completed
            for task in next_state.tasks.values()
        )
        # No game-over event because not at win condition yet.
        from engine.events import GameOverEvent

        assert not any(isinstance(e, GameOverEvent) for e in events)

    def test_eject_triggering_impostor_parity_emits_game_over(self) -> None:
        game_map = load_canonical_map()
        base = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
        # Build near-parity meeting state: 1 impostor, 2 crewmates alive.
        impostor_id = next(
            pid for pid, p in base.players.items() if p.role == "IMPOSTOR"
        )
        crewmates = [pid for pid, p in base.players.items() if p.role == "CREWMATE"]
        players: dict[PlayerId, PlayerState] = dict(base.players)
        players[crewmates[0]] = replace(players[crewmates[0]], alive=False)
        state = replace(base, phase="MEETING", players=players, tick=99)

        trigger = MeetingTrigger(
            triggered_by=crewmates[1], trigger_tick=99, description="emergency"
        )
        # Ejecting another crewmate puts impostors at parity.
        result = _eject_result(crewmates[1])("g-1:meeting-0", trigger)
        next_state, events = apply_meeting_result(state, result, game_map=game_map)

        from engine.events import GameOverEvent

        assert next_state.phase == "GAME_OVER"
        # Tick NOT advanced when game-over fires (mirrors engine).
        assert next_state.tick == state.tick
        assert any(
            isinstance(e, GameOverEvent) and e.winner == "IMPOSTORS" for e in events
        ), events
        # And the ejected player is dead.
        assert next_state.players[crewmates[1]].alive is False
        # Impostor still alive.
        assert next_state.players[impostor_id].alive is True

    def test_eject_impostor_completing_crew_tasks_emits_crew_win(self) -> None:
        """If ejecting the impostor drops all incomplete tasks (because crew
        finished the rest), the win check resolves to CREWMATES."""

        game_map = load_canonical_map()
        base = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
        impostor_id = next(
            pid for pid, p in base.players.items() if p.role == "IMPOSTOR"
        )
        # Mark every crew-owned task as completed; no incomplete remains.
        finished_tasks = {
            task_id: replace(task, progress=task.required_ticks, completed=True)
            for task_id, task in base.tasks.items()
        }
        state = replace(base, phase="MEETING", tasks=finished_tasks, tick=33)

        trigger = MeetingTrigger(
            triggered_by="p-1", trigger_tick=33, description="vote impostor"
        )
        result = _eject_result(impostor_id)("g-1:meeting-0", trigger)
        next_state, events = apply_meeting_result(state, result, game_map=game_map)

        from engine.events import GameOverEvent

        assert next_state.phase == "GAME_OVER"
        assert any(
            isinstance(e, GameOverEvent) and e.winner == "CREWMATES" for e in events
        ), events

    def test_apply_outside_meeting_phase_fails_loud(self) -> None:
        game_map = load_canonical_map()
        state = seed_initial_state(seed=1, game_map=game_map, num_players=4)
        trigger = MeetingTrigger(triggered_by="p-1", trigger_tick=0, description="x")
        result = _skip_result("g-1:meeting-0", trigger)

        with pytest.raises(ValueError, match="MEETING"):
            apply_meeting_result(state, result, game_map=game_map)

    def test_apply_eject_dead_player_fails_loud(self) -> None:
        game_map = load_canonical_map()
        state, _ = _meeting_state_with_body(game_map)
        trigger = MeetingTrigger(triggered_by="p-1", trigger_tick=42, description="x")
        # ``p-2`` is dead in the fixture.
        result = _eject_result("p-2")("g-1:meeting-0", trigger)

        with pytest.raises(ValueError, match="already-dead"):
            apply_meeting_result(state, result, game_map=game_map)

    def test_apply_advances_rng_state(self) -> None:
        game_map = load_canonical_map()
        state, _ = _meeting_state_with_body(game_map)
        trigger = MeetingTrigger(triggered_by="p-1", trigger_tick=42, description="x")
        result = _skip_result("g-1:meeting-0", trigger)

        next_state, _ = apply_meeting_result(state, result, game_map=game_map)

        assert next_state.rng_state != state.rng_state


# ---------------------------------------------------------------------------
# HeadlessGame end-to-end with a meeting runner.
# ---------------------------------------------------------------------------


def _report_body_factory(
    body_id: str,
) -> Callable[[PlayerId, Role], _ScriptedAgent]:
    def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        if agent_id == "p-1":
            return _ScriptedAgent(
                agent_id=agent_id,
                intents=[
                    _intent(
                        {
                            "type": "report",
                            "actor": "p-1",
                            "payload": {"body_id": body_id},
                        }
                    )
                ],
            )
        return _ScriptedAgent(agent_id=agent_id)

    return factory


def _seed_meeting_setup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    game_map: Map,
    seed: int = 2026,
) -> str:
    """Pre-seed a world state with a corpse so the report action validates."""

    initial = seed_initial_state(seed=seed, game_map=game_map, num_players=4)
    body_id = "body-p-2-1"
    body = BodyState(
        id=body_id,
        player_id="p-2",
        room=game_map.spawn.room,
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    state_with_body = replace(
        initial,
        bodies={body_id: body},
        players={
            **initial.players,
            "p-2": replace(initial.players["p-2"], alive=False),
        },
    )

    def _stub(
        *,
        seed: int,
        game_map: Map,
        num_players: int,
        num_impostors: int = 1,
        tasks_per_crewmate: int = 1,
    ) -> WorldState:
        return state_with_body

    monkeypatch.setattr("orchestrator.game.seed_initial_state", _stub)
    return body_id


class TestHeadlessGameMeetingDispatch:
    def test_meeting_phase_reached_when_no_runner_configured(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Legacy behaviour: no runner → orchestrator pauses at MEETING."""

        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)
        replay_path = tmp_path / "no-runner.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
        )

        result = game.run()

        assert result.outcome == "MEETING_PHASE_REACHED"
        assert result.final_state.phase == "MEETING"

    def test_runner_dispatch_skip_resumes_game(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A configured runner returning SKIPPED resumes the game."""

        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)
        runner = _CannedMeetingRunner(result_builder=_skip_result)

        replay_path = tmp_path / "skip-runner.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=8),
            meeting_runner=runner,
        )

        result = game.run()

        # Runner was called exactly once at the report tick.
        assert len(runner.received) == 1
        meeting_id, trigger, snapshot_state, _ = runner.received[0]
        assert meeting_id == "headless-seed-2026:meeting-0"
        assert trigger.triggered_by == "p-1"
        assert snapshot_state.phase == "MEETING"
        # Game ran past the meeting tick → outcome is hit-budget (skipped).
        assert result.outcome == "TICK_BUDGET_REACHED"
        assert result.final_state.phase == "PLAY"
        # Replay log has both tick and meeting entries.
        entries = read_all_entries(replay_path)
        meeting_entries = [
            entry for entry in entries if isinstance(entry, MeetingReplayEntry)
        ]
        assert len(meeting_entries) == 1
        meeting_entry = meeting_entries[0]
        assert meeting_entry.outcome == "SKIPPED"
        assert meeting_entry.meeting_id == "headless-seed-2026:meeting-0"
        assert meeting_entry.state_hash_before != meeting_entry.state_hash_after

    def test_runner_dispatch_eject_marks_player_dead_and_resumes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)
        runner = _CannedMeetingRunner(result_builder=_eject_result("p-4"))

        replay_path = tmp_path / "eject-runner.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
            meeting_runner=runner,
        )

        result = game.run()

        assert result.final_state.players["p-4"].alive is False
        assert "p-4" not in result.final_state.cooldowns
        # And the runner's MeetingResult was persisted.
        entries = read_all_entries(replay_path)
        meeting_entries = [
            entry for entry in entries if isinstance(entry, MeetingReplayEntry)
        ]
        assert len(meeting_entries) == 1
        assert meeting_entries[0].outcome == "EJECTED"
        assert meeting_entries[0].ejected_player_id == "p-4"

    def test_runner_returning_wrong_meeting_id_is_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)

        def _bad_builder(meeting_id: str, trigger: MeetingTrigger) -> MeetingResult:
            return _skip_result("WRONG", trigger)

        runner = _CannedMeetingRunner(result_builder=_bad_builder)
        replay_path = tmp_path / "wrong-id.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
            meeting_runner=runner,
        )

        with pytest.raises(ValueError, match="meeting_id"):
            game.run()

    def test_runner_returning_wrong_triggered_by_is_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Codex P2: validate ``triggered_by`` against the engine trigger."""

        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)

        def _bad_builder(meeting_id: str, trigger: MeetingTrigger) -> MeetingResult:
            return MeetingResult(
                meeting_id=meeting_id,
                triggered_by="p-99",  # diverges from engine event actor.
                trigger_tick=trigger.trigger_tick,
                outcome="SKIPPED",
                ejected_player_id=None,
                ballots=(),
                contradictions=(),
                transcript=MeetingTranscript(),
            )

        runner = _CannedMeetingRunner(result_builder=_bad_builder)
        replay_path = tmp_path / "wrong-triggered-by.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
            meeting_runner=runner,
        )

        with pytest.raises(ValueError, match="triggered_by"):
            game.run()

    def test_runner_returning_wrong_trigger_tick_is_rejected(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Codex P2: validate ``trigger_tick`` against the engine trigger."""

        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)

        def _bad_builder(meeting_id: str, trigger: MeetingTrigger) -> MeetingResult:
            return MeetingResult(
                meeting_id=meeting_id,
                triggered_by=trigger.triggered_by,
                trigger_tick=trigger.trigger_tick + 99,  # drift.
                outcome="SKIPPED",
                ejected_player_id=None,
                ballots=(),
                contradictions=(),
                transcript=MeetingTranscript(),
            )

        runner = _CannedMeetingRunner(result_builder=_bad_builder)
        replay_path = tmp_path / "wrong-trigger-tick.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
            meeting_runner=runner,
        )

        with pytest.raises(ValueError, match="trigger_tick"):
            game.run()

    def test_resume_preserves_pre_meeting_engine_events(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Codex P1: pre-meeting engine events stay visible on the resume tick.

        Pin: when a report shares a tick with another engine event
        (e.g. a kill earlier in the same action queue), the
        orchestrator's ``last_events`` after the meeting must contain
        the pre-meeting events so the next observation pass surfaces
        the kill / vent to witnesses via
        ``ObservationService._observed_actions_for_agent``.

        Setup: pre-seed roles so p-1 is the impostor (its actions
        sort first in the action queue). On the meeting tick, p-1
        kills p-3 (in the shared spawn room) and p-2 reports a
        pre-existing body. The engine processes p-1's kill (emitting
        ``KilledEvent``) before p-2's report (emitting
        ``MeetingTriggeredEvent`` and returning early). After the
        runner returns SKIP, the witness p-4 should see the kill in
        its next observation packet.
        """

        from agents.tactical.crewmate_policy import CrewmatePolicy
        from agents.tactical.impostor_policy import ImpostorPolicy

        from orchestrator.game import TacticalAgent

        game_map = load_canonical_map()
        base = seed_initial_state(seed=2026, game_map=game_map, num_players=4)

        # Force role assignment: p-1 impostor, others crewmates.
        forced_players: dict[PlayerId, PlayerState] = {}
        for pid, player in base.players.items():
            new_role: Role = "IMPOSTOR" if pid == "p-1" else "CREWMATE"
            forced_players[pid] = replace(player, role=new_role)
        # Seed a pre-existing body for p-2 to report.
        body_id = "body-existing-1"
        existing_body = BodyState(
            id=body_id,
            player_id="p-2",  # never-was-alive marker; only used as report target
            room=game_map.spawn.room,
            position=(0.0, 0.0),
            killed_by="p-1",
            discovered_by=None,
        )
        # p-2 needs to be alive to perform the report; pick a different victim
        # id for the body so the discoverer isn't dead.
        state_pre = replace(
            base,
            players=forced_players,
            bodies={body_id: existing_body},
            cooldowns={"p-1": 0},
        )

        def _stub_seed(
            *,
            seed: int,
            game_map: Map,
            num_players: int,
            num_impostors: int = 1,
            tasks_per_crewmate: int = 1,
        ) -> WorldState:
            return state_pre

        monkeypatch.setattr("orchestrator.game.seed_initial_state", _stub_seed)

        # p-4 is a passive witness that captures every observation
        # packet it receives so we can inspect the post-meeting one.
        captured: list[ObservationPacket] = []

        class _WitnessAgent:
            def __init__(self, agent_id: PlayerId, role: Role) -> None:
                self._agent_id = agent_id
                self._role: Role = role
                policy = (
                    ImpostorPolicy(agent_id=agent_id)
                    if role == "IMPOSTOR"
                    else CrewmatePolicy(agent_id=agent_id)
                )
                self._delegate = TacticalAgent(
                    agent_id=agent_id, role=role, policy=policy
                )

            def decide(
                self,
                packet: ObservationPacket,
                public_map: PublicMapView,
            ) -> ActionIntent:
                captured.append(packet)
                self._delegate.decide(packet, public_map)
                return _intent(
                    {"type": "wait", "actor": packet.agent_id, "payload": {}}
                )

            @property
            def agent_id(self) -> PlayerId:
                return self._agent_id

            @property
            def role(self) -> Role:
                return self._role

            def render_memory_for_meeting(self, *, token_budget: int = 1500) -> str:
                return self._delegate.render_memory_for_meeting(
                    token_budget=token_budget
                )

            def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
                return self._delegate.suspicion_graph_for_meeting()

        def factory(agent_id: PlayerId, role: Role):  # type: ignore[no-untyped-def]
            if agent_id == "p-1":
                return _ScriptedAgent(
                    agent_id=agent_id,
                    intents=[
                        _intent(
                            {
                                "type": "kill",
                                "actor": "p-1",
                                "payload": {"target": "p-3"},
                            }
                        )
                    ],
                )
            if agent_id == "p-2":
                return _ScriptedAgent(
                    agent_id=agent_id,
                    intents=[
                        _intent(
                            {
                                "type": "report",
                                "actor": "p-2",
                                "payload": {"body_id": body_id},
                            }
                        )
                    ],
                )
            return _WitnessAgent(agent_id, role)

        runner = _CannedMeetingRunner(result_builder=_skip_result)
        replay_path = tmp_path / "preserve-events.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=factory,
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=3),
            meeting_runner=runner,
        )
        game.run()

        # The witness should receive at least two packets: tick 0
        # (pre-kill) and tick 1 (post-meeting resume). The tick-1
        # packet must surface p-1's kill via ``PlayerView.action``.
        # Find p-4's packets in order.
        p4_packets = [p for p in captured if p.agent_id == "p-4"]
        assert len(p4_packets) >= 2, (
            "expected p-4 to observe at least two ticks (pre + post meeting)"
        )
        resume_packet = p4_packets[1]
        # ``PlayerView.action`` is the action label the observer saw
        # the other player perform on the previous tick. The kill
        # must be visible on the resume tick because p-4 was in the
        # spawn room when p-1 killed p-3.
        p1_view = next(
            (view for view in resume_packet.visible_players if view.id == "p-1"),
            None,
        )
        assert p1_view is not None, (
            f"p-4 should see p-1 in visible_players on the resume tick; "
            f"visible_players={[v.id for v in resume_packet.visible_players]}"
        )
        assert p1_view.action == "kill", (
            f"p-4 should observe p-1's kill action on the resume tick; "
            f"got action={p1_view.action!r}"
        )

    def test_reported_body_is_consumed_after_meeting(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Codex P2: the reported body is removed when gameplay resumes.

        Defense in depth — visibility hides discovered bodies from
        default tactical agents, but the engine's ``resolve_report``
        does not reject already-discovered bodies. Consuming the body
        on meeting close prevents an adversarial intent from
        re-triggering the same meeting on the same corpse.
        """

        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)
        runner = _CannedMeetingRunner(result_builder=_skip_result)

        replay_path = tmp_path / "consume-body.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=4),
            meeting_runner=runner,
        )

        result = game.run()

        assert body_id not in result.final_state.bodies


# ---------------------------------------------------------------------------
# DefaultMeetingRunner — exercises the default LLM-backed wiring.
# ---------------------------------------------------------------------------


class _ScriptedLLMClient:
    """Deterministic stub LLM client for default-runner tests."""

    def __init__(
        self,
        *,
        vote_target: str = "SKIP",
        cost_usd: float = 0.0,
    ) -> None:
        self._vote_target = vote_target
        self._cost_usd = cost_usd
        self.calls: list[tuple[type[BaseModel] | None, CallKind]] = []

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
        self.calls.append((schema, call_kind))
        if schema is MeetingTurn:
            # Identity fields are placeholders: the manager overrides
            # turn_id / turn_index / speaker / turn_kind / reply_to. A
            # claim-free turn never extends the accusation chain, so the
            # meeting is exactly: opening turn -> ballots. The free_text
            # declares "unsure" so the claim-free OPENING satisfies the
            # Task 10.3 accuse-or-declare-unsure validation and records on
            # its first attempt (no retry call, no default).
            text = MeetingTurn(
                turn_id="placeholder",
                turn_index=0,
                speaker="placeholder",
                turn_kind="opening",
                reply_to=None,
                observations=(),
                claims=(),
                free_text="stub-turn (unsure)",
            ).model_dump_json()
        elif schema is VoteBallot:
            text = VoteBallot(
                voter="placeholder",
                target=self._vote_target,
                confidence=0.9,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="stub-vote",
            ).model_dump_json()
        else:
            raise AssertionError(f"unexpected schema {schema!r}")

        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=self._cost_usd,
            model=model or "stub-model",
        )


def _stub_crewmate_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
) -> str:
    return f"CREWMATE_REPORT agent_id={agent_id} tick={current_tick}"


def _stub_impostor_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
) -> str:
    return f"IMPOSTOR_REPORT agent_id={agent_id} tick={current_tick}"


def _stub_statement_prompt(
    *,
    agent_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
    prior_turn: MeetingTurn | None,
    turn_kind: TurnKind,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    is_impostor: bool = False,
    is_body_report: bool = False,
) -> str:
    return f"STATEMENT_PROMPT agent_id={agent_id} kind={turn_kind}"


def _stub_vote_prompt(
    *,
    voter_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradiction_flags: tuple[ContradictionRef, ...],
    suspicion_graph: tuple[SuspicionEntry, ...],
    candidate_targets: tuple[PlayerId, ...],
    skip_confidence_threshold: float,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    return f"VOTE voter={voter_id}"


def _build_default_runner(
    *,
    llm_client: _ScriptedLLMClient,
) -> DefaultMeetingRunner:
    from meetings.manager import MeetingConfig

    config = MeetingConfig(
        deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
    )
    return DefaultMeetingRunner(
        llm_client=llm_client,
        crewmate_report_prompt=_stub_crewmate_prompt,
        impostor_report_prompt=_stub_impostor_prompt,
        statement_prompt=_stub_statement_prompt,
        vote_prompt=_stub_vote_prompt,
        config=config,
    )


class TestDefaultMeetingRunner:
    def test_default_runner_skips_when_votes_are_skip(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """End-to-end: report → meeting runs → SKIP → game resumes."""

        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)
        llm = _ScriptedLLMClient(vote_target="SKIP", cost_usd=0.01)
        runner = _build_default_runner(llm_client=llm)

        replay_path = tmp_path / "default-runner-skip.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=build_default_agent_factory(),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=20),
            meeting_runner=runner,
        )

        # Inject a single report intent into a tactical agent through
        # an action override: monkey-patch p-1's policy to call report
        # at the first opportunity. Simpler: use a hybrid factory.
        report_intent = _intent(
            {
                "type": "report",
                "actor": "p-1",
                "payload": {"body_id": body_id},
            }
        )

        class _ReportThenDefault:
            def __init__(self, agent_id: PlayerId, role: Role) -> None:
                from orchestrator.game import TacticalAgent
                from agents.tactical.crewmate_policy import CrewmatePolicy
                from agents.tactical.impostor_policy import ImpostorPolicy

                self._delegate = TacticalAgent(
                    agent_id=agent_id,
                    role=role,
                    policy=(
                        ImpostorPolicy(agent_id=agent_id)
                        if role == "IMPOSTOR"
                        else CrewmatePolicy(agent_id=agent_id)
                    ),
                )
                self._fired = False

            def decide(
                self,
                packet: ObservationPacket,
                public_map: PublicMapView,
            ) -> ActionIntent:
                self._delegate.decide(packet, public_map)
                if packet.agent_id == "p-1" and not self._fired:
                    self._fired = True
                    return report_intent
                return _intent(
                    {"type": "wait", "actor": packet.agent_id, "payload": {}}
                )

            def render_memory_for_meeting(self, *, token_budget: int = 1500) -> str:
                return self._delegate.render_memory_for_meeting(
                    token_budget=token_budget
                )

            def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
                return self._delegate.suspicion_graph_for_meeting()

            @property
            def agent_id(self) -> PlayerId:
                return self._delegate.agent_id

            @property
            def role(self) -> Role:
                return self._delegate.role

        def factory(agent_id: PlayerId, role: Role) -> _ReportThenDefault:
            return _ReportThenDefault(agent_id, role)

        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=factory,
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=10),
            meeting_runner=runner,
        )
        result = game.run()

        assert result.outcome in {"TICK_BUDGET_REACHED", "IMPOSTORS", "CREWMATES"}
        entries = read_all_entries(replay_path)
        meeting_entries = [
            entry for entry in entries if isinstance(entry, MeetingReplayEntry)
        ]
        assert len(meeting_entries) == 1
        meeting = meeting_entries[0]
        assert meeting.outcome == "SKIPPED"
        # The chain protocol with a claim-free stub: 1 opening turn + 3
        # ballots from the 3 living players = 4 LLM calls (no accusation, so
        # no reply chain; no observations, so no opt-in turn).
        assert len(meeting.llm_calls) == 4
        # Each call carries cost metadata.
        assert all(call.cost_usd == 0.01 for call in meeting.llm_calls)
        # Transcript is the ordered turn chain: the reporter's opening only.
        assert len(meeting.transcript.turns) == 1
        assert meeting.transcript.turns[0].turn_kind == "opening"
        assert meeting.transcript.turns[0].speaker == "p-1"
        # Prompt versions metadata persisted.
        assert "crewmate_report" in meeting.prompt_versions
        assert "vote_ballot" in meeting.prompt_versions

    def test_failed_meeting_does_not_leak_llm_calls_into_next_meeting(
        self,
    ) -> None:
        """Codex P2: a mid-meeting failure drains the recording buffer.

        If ``MeetingManager.run`` raises after one or more
        ``complete()`` calls, the recorded calls must not be attached
        to the next successful meeting's replay payload. Pin: dispatch
        two meetings against the same :class:`DefaultMeetingRunner`,
        force the first one to raise mid-meeting, and assert the
        second meeting's artifacts only count the second meeting's
        calls.
        """

        from meetings.manager import MeetingConfig

        class _RaiseAfterFirstCallClient:
            def __init__(self) -> None:
                self._count = 0

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
                self._count += 1
                if schema is MeetingTurn and self._count == 1:
                    # "unsure" satisfies the Task 10.3 opening validation, so
                    # the meeting still aborts on the SECOND call (the vote),
                    # not on an opening retry.
                    return LLMResponse(
                        text=MeetingTurn(
                            turn_id="placeholder",
                            turn_index=0,
                            speaker="x",
                            turn_kind="opening",
                            reply_to=None,
                            observations=(),
                            claims=(),
                            free_text="r (unsure)",
                        ).model_dump_json(),
                        usage=TokenUsage(input_tokens=1, output_tokens=1),
                        cost_usd=0.0,
                        model="stub",
                    )
                raise RuntimeError("boom")

        config = MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        runner = DefaultMeetingRunner(
            llm_client=_RaiseAfterFirstCallClient(),
            crewmate_report_prompt=_stub_crewmate_prompt,
            impostor_report_prompt=_stub_impostor_prompt,
            statement_prompt=_stub_statement_prompt,
            vote_prompt=_stub_vote_prompt,
            config=config,
        )
        trigger = MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=10,
            description="x",
        )
        participants_seed = seed_initial_state(
            seed=1, game_map=load_canonical_map(), num_players=3
        )

        # Build a thin MeetingAware proxy over the seeded TacticalAgents
        # so the runner's _build_participants can render memory.
        class _MinimalAware:
            def __init__(self, agent_id: PlayerId, role: Role) -> None:
                from agents.tactical.crewmate_policy import CrewmatePolicy
                from agents.tactical.impostor_policy import ImpostorPolicy

                from orchestrator.game import TacticalAgent

                policy = (
                    ImpostorPolicy(agent_id=agent_id)
                    if role == "IMPOSTOR"
                    else CrewmatePolicy(agent_id=agent_id)
                )
                self._delegate = TacticalAgent(
                    agent_id=agent_id, role=role, policy=policy
                )
                # Prime memory with a self-state event so the renderer
                # doesn't raise on missing role.
                from agents.memory.episodic import EpisodicEvent

                self._delegate.memory.episodic.append(
                    EpisodicEvent(
                        tick=0,
                        type="self_state",
                        payload={"room": "CAFETERIA", "role": role},
                        provenance="observed",
                    )
                )

            def decide(self, packet, public_map):  # type: ignore[no-untyped-def]
                return self._delegate.decide(packet, public_map)

            @property
            def agent_id(self) -> PlayerId:
                return self._delegate.agent_id

            @property
            def role(self) -> Role:
                return self._delegate.role

            def render_memory_for_meeting(self, *, token_budget: int = 1500) -> str:
                return self._delegate.render_memory_for_meeting(
                    token_budget=token_budget
                )

            def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
                return self._delegate.suspicion_graph_for_meeting()

        agents: dict[PlayerId, object] = {
            pid: _MinimalAware(pid, players.role)
            for pid, players in participants_seed.players.items()
        }

        # First meeting raises mid-flight.
        with pytest.raises(RuntimeError, match="boom"):
            _run(
                runner.run_meeting(
                    meeting_id="m-1",
                    trigger=trigger,
                    state=participants_seed,
                    agents=agents,  # type: ignore[arg-type]
                )
            )

        # Swap the client for a clean one so the next meeting succeeds.
        runner._recording_client = runner._recording_client.__class__(
            _ScriptedLLMClient(vote_target="SKIP")
        )
        runner._manager._llm_client = runner._recording_client

        artifacts = _run(
            runner.run_meeting(
                meeting_id="m-2",
                trigger=trigger.__class__(
                    triggered_by="p-1", trigger_tick=20, description="y"
                ),
                state=participants_seed,
                agents=agents,  # type: ignore[arg-type]
            )
        )

        # The second meeting's artifacts must NOT include records
        # from the first (failed) meeting. The second meeting issues
        # 1 opening turn + 3 votes = 4 calls; if leakage occurred,
        # we'd see > 4 here (the failed meeting recorded its one
        # successful opening-turn call before raising on the vote).
        assert len(artifacts.llm_calls) == 4


class TestMeetingFirewallContract:
    """Engine purity — MeetingManager must not mutate engine state."""

    def test_runner_cannot_observe_mutations_propagating_to_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The runner sees a frozen WorldState snapshot.

        Any mutation attempt to ``state.players`` would fail because
        the engine state stores ``MappingProxyType`` views. We assert
        the snapshot the runner receives is read-only.
        """

        game_map = load_canonical_map()
        body_id = _seed_meeting_setup(monkeypatch, game_map=game_map)
        observed: list[WorldState] = []

        def builder(meeting_id: str, trigger: MeetingTrigger) -> MeetingResult:
            return _skip_result(meeting_id, trigger)

        @dataclass
        class _Recording:
            async def run_meeting(
                self,
                *,
                meeting_id: str,
                trigger: MeetingTrigger,
                state: WorldState,
                agents: Mapping[PlayerId, object],
            ) -> MeetingArtifacts:
                observed.append(state)
                return MeetingArtifacts(
                    result=builder(meeting_id, trigger),
                    llm_calls=(),
                    prompt_versions={},
                )

        replay_path = tmp_path / "firewall.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_body_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
            meeting_runner=_Recording(),
        )

        game.run()

        assert len(observed) == 1
        snapshot = observed[0]
        # WorldState's player mapping is wrapped in MappingProxyType so
        # mutation raises TypeError.
        with pytest.raises(TypeError):
            snapshot.players["p-99"] = snapshot.players["p-1"]  # type: ignore[index]


class TestMeetingTriggerExtraction:
    def test_emergency_trigger_renders_emergency_description(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_map = load_canonical_map()
        initial = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
        # Move p-1 to the emergency button room so the action validates.
        players: dict[PlayerId, PlayerState] = dict(initial.players)
        players["p-1"] = replace(players["p-1"], room=game_map.emergency.button_room)
        state = replace(initial, players=players)
        monkeypatch.setattr(
            "orchestrator.game.seed_initial_state",
            lambda **_: state,
        )

        def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
            if agent_id == "p-1":
                return _ScriptedAgent(
                    agent_id=agent_id,
                    intents=[
                        _intent(
                            {
                                "type": "emergency",
                                "actor": "p-1",
                                "payload": {},
                            }
                        )
                    ],
                )
            return _ScriptedAgent(agent_id=agent_id)

        observed_triggers: list[MeetingTrigger] = []

        @dataclass
        class _CaptureRunner:
            async def run_meeting(
                self,
                *,
                meeting_id: str,
                trigger: MeetingTrigger,
                state: WorldState,
                agents: Mapping[PlayerId, object],
            ) -> MeetingArtifacts:
                observed_triggers.append(trigger)
                return MeetingArtifacts(
                    result=_skip_result(meeting_id, trigger),
                    llm_calls=(),
                    prompt_versions={},
                )

        replay_path = tmp_path / "emergency.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=factory,
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=3),
            meeting_runner=_CaptureRunner(),
        )
        game.run()

        assert len(observed_triggers) == 1
        trigger = observed_triggers[0]
        assert trigger.triggered_by == "p-1"
        assert "emergency" in trigger.description.lower()
        # Task 10.8: the exact phrase is load-bearing — crewmate_report v6
        # selects its emergency-opening branch on this substring of the
        # rendered ``meeting_trigger`` (no structured trigger kind reaches
        # the prompt renderers). The template-side half of this pin lives in
        # tests/agents/test_strategic_prompts.py.
        assert "called an emergency meeting" in trigger.description


class TestPublicCliMeetingWireUp:
    """R-1 / R-5 regression: meetings fire from the public CLI factory path.

    Pins that a :class:`HeadlessGame` constructed exactly the way
    :mod:`scripts.run_game` constructs it -- the default tactical agent
    factory plus a :func:`build_default_meeting_runner` wrapping the
    canonical :class:`llm.fake_provider.FakeProvider` and a per-game
    :class:`GameBudget` -- runs an LLM-driven meeting end-to-end and
    resumes the game. This is the gap the Pre-Phase-4 audit flagged as
    R-1: before Task 3.13 the public path constructed ``HeadlessGame``
    with no ``meeting_runner`` and every game stalled at
    ``MEETING_PHASE_REACHED`` (``meeting_entries=0`` across a 100-game
    reconstruction). The R-5 closure is folded in for free: this routes
    the full ``HeadlessGame`` + ``DefaultMeetingRunner`` +
    ``MeetingManager`` path through the canonical ``FakeProvider`` rather
    than an inline stub.
    """

    # Seed whose default-agent game fires a body-report meeting (~tick 7)
    # under the canonical map AT ONE TASK PER CREWMATE (the committed 4p/1i
    # config). The harness default is now 2 tasks/crewmate (Task 7.1), which
    # lengthens the game past this meeting, so these meeting-wireup tests pin
    # tasks_per_crewmate=1 to keep exercising the body-report path. Used by the
    # budget-cap regression in tests/llm/test_budgeted_client.py too.
    _MEETING_SEED = 22

    def test_meetings_fire_and_game_resumes_from_public_factory_path(
        self, tmp_path: Path
    ) -> None:
        replay_path = tmp_path / "public-cli.jsonl"
        # Mirror scripts/run_game.py: default agents + FakeProvider-backed
        # runner + a fresh per-game GameBudget. No inline LLM stub.
        game = HeadlessGame(
            seed=self._MEETING_SEED,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=replay_path,
            tasks_per_crewmate=1,
            scheduler=TickScheduler(max_ticks=40),
            meeting_runner=build_default_meeting_runner(budget=GameBudget()),
        )

        result = game.run()

        # (b) the game resumed past the meeting and reached a real
        # terminal state -- never the engine-only opt-out outcome.
        assert result.outcome != "MEETING_PHASE_REACHED"
        # (a) at least one meeting actually ran and was recorded. A
        # reverted wire-up (meeting_runner=None) would stall at
        # MEETING_PHASE_REACHED and write zero meeting entries, failing
        # both assertions.
        meeting_entries = read_meeting_entries(replay_path)
        assert len(meeting_entries) >= 1

    def test_no_runner_still_reaches_meeting_phase_opt_out(
        self, tmp_path: Path
    ) -> None:
        """Counterpart: the same seed with meeting_runner=None (the Phase 2
        byte-identity opt-out) stalls at MEETING_PHASE_REACHED and writes
        no meeting entry. This is what the public path looked like before
        Task 3.13 and is the assertion the wire-up regression flips."""

        replay_path = tmp_path / "no-runner.jsonl"
        game = HeadlessGame(
            seed=self._MEETING_SEED,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=replay_path,
            tasks_per_crewmate=1,
            scheduler=TickScheduler(max_ticks=40),
        )

        result = game.run()

        assert result.outcome == "MEETING_PHASE_REACHED"
        assert read_meeting_entries(replay_path) == ()


# ---------------------------------------------------------------------------
# Task 7.12 — orchestrator populates MeetingParticipant.fellow_impostor_ids,
# and the seed-6 multi-impostor coordination anchor (population + guard).
# ---------------------------------------------------------------------------


@dataclass
class _MeetingAwareStub:
    """Minimal :class:`~orchestrator.game.MeetingAwareAgent` for participant
    construction tests — it only needs to render a (role-bearing) memory
    string and an empty suspicion graph."""

    _agent_id: PlayerId
    _role: Role

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return self._role

    def render_memory_for_meeting(self, *, token_budget: int = 1500) -> str:
        return f"## Your role: {self._role}\nmemory for {self._agent_id}"

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return ()


def _stub_agents_for(state: WorldState) -> dict[PlayerId, object]:
    return {
        pid: _MeetingAwareStub(_agent_id=pid, _role=player.role)
        for pid, player in state.players.items()
    }


class TestBuildParticipantsFellowImpostorIds:
    """The orchestrator derives ``fellow_impostor_ids`` from world-state
    roles (Task 7.12): the other impostors for an impostor, ``()`` for a
    crewmate / sole impostor, never the participant's own id."""

    def test_multi_impostor_seed6_populates_teammates(self) -> None:
        # Seed-6 7p/2i: impostors are p-3 and p-6 (matches the audit repro).
        state = seed_initial_state(
            seed=6,
            game_map=load_canonical_map(),
            num_players=7,
            num_impostors=2,
            tasks_per_crewmate=2,
        )
        participants = _build_participants(
            state=state,
            agents=_stub_agents_for(state),  # type: ignore[arg-type]
            token_budget=1500,
        )
        by_id = {p.agent_id: p for p in participants}

        assert by_id["p-3"].fellow_impostor_ids == ("p-6",)
        assert by_id["p-6"].fellow_impostor_ids == ("p-3",)
        # Every crewmate gets the empty tuple (the firewall-correct value).
        for crew_id in ("p-1", "p-2", "p-4", "p-5", "p-7"):
            assert by_id[crew_id].fellow_impostor_ids == ()
        # An impostor's own id is never in its own teammate list.
        for impostor_id in ("p-3", "p-6"):
            assert impostor_id not in by_id[impostor_id].fellow_impostor_ids

    def test_sole_impostor_gets_empty_teammate_list(self) -> None:
        # The default 4p/1i roster has a single impostor → empty everywhere.
        state = seed_initial_state(
            seed=2026, game_map=load_canonical_map(), num_players=4
        )
        participants = _build_participants(
            state=state,
            agents=_stub_agents_for(state),  # type: ignore[arg-type]
            token_budget=1500,
        )
        assert all(p.fellow_impostor_ids == () for p in participants)

    def test_three_impostors_each_sees_the_other_two_sorted(self) -> None:
        state = seed_initial_state(
            seed=11,
            game_map=load_canonical_map(),
            num_players=7,
            num_impostors=3,
            tasks_per_crewmate=2,
        )
        impostor_ids = sorted(
            pid for pid, p in state.players.items() if p.role == "IMPOSTOR"
        )
        assert len(impostor_ids) == 3
        by_id = {
            p.agent_id: p
            for p in _build_participants(
                state=state,
                agents=_stub_agents_for(state),  # type: ignore[arg-type]
                token_budget=1500,
            )
        }
        for impostor_id in impostor_ids:
            expected = tuple(pid for pid in impostor_ids if pid != impostor_id)
            assert by_id[impostor_id].fellow_impostor_ids == expected


class _Seed6BetrayalClient:
    """LLM client that makes every impostor accuse + vote its teammate.

    Drives the seed-6 meeting-0 repro end-to-end through the production
    :class:`DefaultMeetingRunner` (orchestrator population + meeting guard):
    the deterministic guard must strip every betrayal regardless of the
    model output, so no impostor ballot or accusation targets a teammate.

    Under the chain protocol the guard only matters on a turn an impostor
    actually takes, so a crewmate turn accuses impostor ``p-3`` — handing
    the chain to an impostor — and the impostor's reply then attempts the
    teammate accusation the guard must strip (which also terminates the
    chain, since the stripped turn carries no accusation).
    """

    def __init__(self, teammate_of: Mapping[PlayerId, PlayerId]) -> None:
        self._teammate_of = teammate_of

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
        mate = self._teammate_of.get(agent_id or "")
        if schema is MeetingTurn:
            # An impostor always tries to frame its teammate; a crewmate
            # accuses impostor p-3, passing the chain floor to an impostor.
            accused = mate if mate is not None else "p-3"
            text = MeetingTurn(
                turn_id="placeholder",
                turn_index=0,
                speaker=agent_id or "x",
                turn_kind="opening",
                reply_to=None,
                observations=(),
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against=accused,
                        confidence=0.9,
                        reason="frame teammate" if mate is not None else "suspect",
                    ),
                ),
                free_text="t",
            ).model_dump_json()
        elif schema is VoteBallot:
            text = VoteBallot(
                voter=agent_id or "x",
                target=mate if mate is not None else "SKIP",
                confidence=0.9,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="v",
            ).model_dump_json()
        else:
            raise AssertionError(f"unexpected schema {schema!r}")
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "stub",
        )


class TestSeed6ImpostorMeetingCoordination:
    """Behavioral regression anchor (Task 7.12, audit D-D-1..D-D-4).

    Repro fixture: seed-6 meeting-0 (impostors p-3 + p-6; in the recorded
    baseline p-6's betrayal vote was the pivotal 2nd vote that ejected
    teammate p-3). Run a meeting end-to-end through the production runner
    with both impostors scripted to betray each other and assert the
    orchestrator-populated teammate list + the meeting guard together stop
    every betrayal — no impostor produces a ballot or accusation targeting
    a teammate (firewall-known, no role inference).
    """

    def test_impostor_never_targets_teammate_end_to_end(self) -> None:
        state = seed_initial_state(
            seed=6,
            game_map=load_canonical_map(),
            num_players=7,
            num_impostors=2,
            tasks_per_crewmate=2,
        )
        teammate_of = {"p-3": "p-6", "p-6": "p-3"}
        runner = DefaultMeetingRunner(
            llm_client=_Seed6BetrayalClient(teammate_of),
            crewmate_report_prompt=_stub_crewmate_prompt,
            impostor_report_prompt=_stub_impostor_prompt,
            statement_prompt=_stub_statement_prompt,
            vote_prompt=_stub_vote_prompt,
            config=MeetingConfig(
                deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
            ),
        )
        trigger = MeetingTrigger(
            triggered_by="p-1", trigger_tick=8, description="p-1 reported a body"
        )

        artifacts = _run(
            runner.run_meeting(
                meeting_id="headless-seed-6:meeting-0",
                trigger=trigger,
                state=state,
                agents=_stub_agents_for(state),  # type: ignore[arg-type]
            )
        )
        result = artifacts.result

        ballots = {b.voter: b for b in result.ballots}
        for impostor_id, mate in teammate_of.items():
            # The scripted betrayal ballot is coerced away from the teammate.
            assert ballots[impostor_id].target != mate
            assert ballots[impostor_id].target == "SKIP"
        # The chain handed the floor to an impostor: the crewmate opening
        # accused p-3, whose reply is the guard's real test surface.
        turns = result.transcript.turns
        assert len(turns) == 2
        assert turns[0].speaker == "p-1"
        assert turns[1].turn_kind == "reply"
        assert turns[1].speaker == "p-3"
        # No turn authored by an impostor names a teammate: the scripted
        # teammate accusation was stripped by the guard (which is also what
        # terminated the chain — the stripped turn carries no accusation).
        for turn in turns:
            turn_mate = teammate_of.get(turn.speaker)
            if turn_mate is not None:
                assert not any(
                    isinstance(c, AccusationClaim) and c.against == turn_mate
                    for c in turn.claims
                )
        # The teammate-betrayal votes removed, the table does not eject an
        # impostor (the audit's seed-6 outcome flip).
        assert result.outcome == "SKIPPED"


# ---------------------------------------------------------------------------
# Task 9.8 — the persistent post-meeting belief path through the game loop.
# ---------------------------------------------------------------------------


class _PerceivingScriptedAgent:
    """A real :class:`TacticalAgent`'s memory behind a scripted intent stream.

    Perception runs through the production ``TacticalAgent.decide`` path
    (so the composite memory holds a genuine self_state channel), but the
    returned intent is overridden by the script -- the test needs p-1 to
    report two seeded bodies on consecutive resumable ticks, which the
    tactical policy's task-seeking movement would not guarantee. Implements
    the :class:`orchestrator.game.BeliefPersistingAgent` capability by
    delegating to the wrapped production agent.
    """

    def __init__(
        self,
        *,
        inner: TacticalAgent,
        intents: Iterable[ActionIntent] = (),
    ) -> None:
        self._inner = inner
        self._intents = list(intents)
        self._cursor = 0

    @property
    def memory_beliefs_suspicion_of(self) -> Callable[[str], float]:
        return lambda player_id: self._inner.memory.beliefs.view(player_id).suspicion

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        self._inner.decide(packet, public_map)
        if self._cursor < len(self._intents):
            intent = self._intents[self._cursor]
            self._cursor += 1
            return intent
        return _intent({"type": "wait", "actor": self._inner.agent_id, "payload": {}})

    def absorb_meeting_evidence(
        self,
        *,
        accused: tuple[PlayerId, ...],
        corroborated: tuple[PlayerId, ...],
        contradicted: tuple[PlayerId, ...],
    ) -> None:
        self._inner.absorb_meeting_evidence(
            accused=accused,
            corroborated=corroborated,
            contradicted=contradicted,
        )


@dataclass
class _AccusingMeetingRunner:
    """Canned runner whose every meeting publicly accuses ``accused``.

    Snapshots each living agent's PERSISTED suspicion of the accused at
    meeting entry, so the test can assert meeting N+1's inputs carry
    meeting N's fold (the across-meeting persistence the task builds).
    """

    accused: PlayerId
    suspicion_at_entry: list[dict[PlayerId, float]] = field(default_factory=list)

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, object],
    ) -> MeetingArtifacts:
        self.suspicion_at_entry.append(
            {
                pid: agent.memory_beliefs_suspicion_of(self.accused)
                for pid, agent in agents.items()
                if isinstance(agent, _PerceivingScriptedAgent)
                and state.players[pid].alive
            }
        )
        turn = MeetingTurn(
            turn_id=f"{meeting_id}:turn-0",
            turn_index=0,
            speaker=trigger.triggered_by,
            turn_kind="opening",
            reply_to=None,
            observations=(),
            claims=(
                AccusationClaim(
                    type="accusation",
                    against=self.accused,
                    confidence=0.6,
                    reason=f"accuse {self.accused}",
                ),
            ),
            free_text=f"{trigger.triggered_by} accuses {self.accused}",
        )
        result = MeetingResult(
            meeting_id=meeting_id,
            triggered_by=trigger.triggered_by,
            trigger_tick=trigger.trigger_tick,
            outcome="SKIPPED",
            ejected_player_id=None,
            ballots=(),
            contradictions=(),
            transcript=MeetingTranscript(turns=(turn,)),
        )
        return MeetingArtifacts(
            result=result,
            llm_calls=(),
            prompt_versions={"crewmate_report": "test.v0"},
        )


def _two_body_meeting_setup(
    monkeypatch: pytest.MonkeyPatch,
    *,
    game_map: Map,
    seed: int = 2026,
) -> tuple[str, str]:
    """Pre-seed a world with TWO corpses so two report meetings can fire."""

    initial = seed_initial_state(seed=seed, game_map=game_map, num_players=4)
    bodies = {
        body_id: BodyState(
            id=body_id,
            player_id="p-2",
            room=game_map.spawn.room,
            position=(0.0, 0.0),
            killed_by="p-3",
            discovered_by=None,
        )
        for body_id in ("body-a", "body-b")
    }
    state_with_bodies = replace(
        initial,
        bodies=bodies,
        players={
            **initial.players,
            "p-2": replace(initial.players["p-2"], alive=False),
        },
    )

    def _stub(
        *,
        seed: int,
        game_map: Map,
        num_players: int,
        num_impostors: int = 1,
        tasks_per_crewmate: int = 1,
    ) -> WorldState:
        return state_with_bodies

    monkeypatch.setattr("orchestrator.game.seed_initial_state", _stub)
    return "body-a", "body-b"


class TestPostMeetingBeliefPersistence:
    """Task 9.8 (DESIGN.md §6.3 Rules 3 + 5, §4.6; audit gp-1 recall).

    The orchestrator's post-meeting hook folds each meeting's public
    accusations into every living agent's PERSISTENT beliefs, so the
    second meeting's inputs carry the first meeting's bump -- unlike the
    vote-time contradiction lift, which is rebuilt and discarded.
    """

    def test_accusation_bump_persists_across_two_meetings(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_map = load_canonical_map()
        body_a, body_b = _two_body_meeting_setup(monkeypatch, game_map=game_map)
        runner = _AccusingMeetingRunner(accused="p-4")
        agents: dict[PlayerId, _PerceivingScriptedAgent] = {}
        inner_factory = build_default_agent_factory()

        def factory(agent_id: PlayerId, role: Role) -> _PerceivingScriptedAgent:
            inner = inner_factory(agent_id, role)
            assert isinstance(inner, TacticalAgent)
            intents = (
                [
                    _intent(
                        {
                            "type": "report",
                            "actor": "p-1",
                            "payload": {"body_id": body_id},
                        }
                    )
                    for body_id in (body_a, body_b)
                ]
                if agent_id == "p-1"
                else []
            )
            agent = _PerceivingScriptedAgent(inner=inner, intents=intents)
            agents[agent_id] = agent
            return agent

        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=factory,
            replay_path=tmp_path / "belief-persistence.jsonl",
            scheduler=TickScheduler(max_ticks=8),
            meeting_runner=runner,
        )

        result = game.run()

        assert result.outcome == "TICK_BUDGET_REACHED"
        assert len(runner.suspicion_at_entry) == 2
        # Meeting 0 opens on untouched priors: nobody suspects p-4 yet.
        assert runner.suspicion_at_entry[0] == {
            "p-1": 0.5,
            "p-3": 0.5,
            "p-4": 0.5,
        }
        # Meeting 1's INPUTS carry meeting 0's persisted fold: every other
        # living agent holds the accusation bump, while p-4's own store
        # never grows a self row (the own-id guard at loop level).
        assert runner.suspicion_at_entry[1]["p-1"] == pytest.approx(0.55)
        assert runner.suspicion_at_entry[1]["p-3"] == pytest.approx(0.55)
        assert runner.suspicion_at_entry[1]["p-4"] == 0.5
        # After both meetings the second consecutive accusation has
        # accumulated to the 0.60 §4.6 gate in the persistent store the
        # next vote's suspicion graph would be built from.
        assert agents["p-1"].memory_beliefs_suspicion_of("p-4") == pytest.approx(0.60)
        assert agents["p-1"].memory_beliefs_suspicion_of("p-4") >= 0.60
        # The dead player's agent (p-2, the seeded victim) never absorbs:
        # its belief store holds no p-4 row.
        assert agents["p-2"].memory_beliefs_suspicion_of("p-4") == 0.5


# ---------------------------------------------------------------------------
# Task 10.8 — crew emergency meeting end-to-end (DESIGN.md §3.2, §5.2; audit
# gp-3 B-B-4): an unwitnessed kill, suspicion accumulation, the button walk,
# and an EMERGENCY-triggered meeting with the caller as opener.
# ---------------------------------------------------------------------------

_EMERGENCY_SEED = 4242


class _MeetingAwareScriptedAgent:
    """A real :class:`TacticalAgent` behind a scripted intent stream.

    Like :class:`_PerceivingScriptedAgent`, perception runs through the
    production decide path so the composite memory is genuine; unlike it,
    the full :class:`~orchestrator.game.MeetingAwareAgent` surface is
    delegated too, because the Task 10.8 scenario runs a REAL
    :class:`DefaultMeetingRunner` meeting in which the scripted impostor is
    a living participant.
    """

    def __init__(
        self,
        *,
        inner: TacticalAgent,
        intents: Iterable[ActionIntent] = (),
    ) -> None:
        self._inner = inner
        self._intents = list(intents)
        self._cursor = 0

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        self._inner.decide(packet, public_map)
        if self._cursor < len(self._intents):
            intent = self._intents[self._cursor]
            self._cursor += 1
            return intent
        return _intent({"type": "wait", "actor": self._inner.agent_id, "payload": {}})

    @property
    def agent_id(self) -> PlayerId:
        return self._inner.agent_id

    @property
    def role(self) -> Role:
        return self._inner.role

    def render_memory_for_meeting(self, *, token_budget: int = 1500) -> str:
        return self._inner.render_memory_for_meeting(token_budget=token_budget)

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return self._inner.suspicion_graph_for_meeting()


class _EmergencyChainLLMClient:
    """Deterministic LLM stub for the Task 10.8 emergency meeting.

    Turn calls in protocol order: the FIRST turn is the caller's opening —
    an accusation against the impostor backed by a first-hand ``saw_player``
    observation whose ``co_present`` makes the remaining crewmate opt-in
    eligible (no ``found_body`` observation: the meeting is body-less).
    Every later turn (the accused's reply, the opt-in) carries no claims, so
    the §5.2 chain terminates exactly as in a body meeting. Ballots all name
    ``vote_target`` (the accused's own ballot self-target is normalized to
    SKIP by the manager).
    """

    def __init__(self, *, vote_target: str) -> None:
        self._vote_target = vote_target
        self._turn_calls = 0

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
        if schema is MeetingTurn:
            self._turn_calls += 1
            if self._turn_calls == 1:
                turn = MeetingTurn(
                    turn_id="placeholder",
                    turn_index=0,
                    speaker="placeholder",
                    turn_kind="opening",
                    reply_to=None,
                    observations=(
                        SawPlayerObservation(
                            type="saw_player",
                            tick=0,
                            subject="p-3",
                            room="WEST_HALL",
                            co_present=("p-2",),
                        ),
                    ),
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against="p-3",
                            confidence=0.9,
                            reason="alone with the victim in WEST_HALL",
                        ),
                    ),
                    free_text=(
                        "I called this meeting: p-3 was alone with p-4 in "
                        "WEST_HALL and p-4 has not been seen since."
                    ),
                )
            else:
                turn = MeetingTurn(
                    turn_id="placeholder",
                    turn_index=0,
                    speaker="placeholder",
                    turn_kind="reply",
                    reply_to=None,
                    observations=(),
                    claims=(),
                    free_text="stub-defense (unsure)",
                )
            text = turn.model_dump_json()
        elif schema is VoteBallot:
            text = VoteBallot(
                voter="placeholder",
                target=self._vote_target,
                confidence=0.9,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="stub-vote",
            ).model_dump_json()
        else:
            raise AssertionError(f"unexpected schema {schema!r}")
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "stub-model",
        )


def _emergency_scenario_setup(
    monkeypatch: pytest.MonkeyPatch, *, game_map: Map
) -> WorldState:
    """Seed the audit gp-3 B-B-4 shape: an about-to-be-unwitnessed kill.

    p-3 (forced impostor, cooldown 0) and its victim p-4 stand in WEST_HALL;
    crewmate p-1 works an ADMIN task next door (ADMIN is adjacent to
    WEST_HALL, so p-1 sees the players and later the body, but the kill is
    not in p-1's OWN room — the witnessed-kill interrupt never fires and the
    body is never reportable from ADMIN); crewmate p-2 works the REACTOR
    task two rooms away and observes nothing. The crew task pool is exactly
    p-1's and p-2's instances, so the SKIP variant ends in a clean
    CREWMATE_TASKS game-over for the eval readers.
    """

    from engine.entities import TaskState

    base = seed_initial_state(seed=_EMERGENCY_SEED, game_map=game_map, num_players=4)
    rooms = {
        "p-1": "ADMIN",
        "p-2": "REACTOR",
        "p-3": "WEST_HALL",
        "p-4": "WEST_HALL",
    }
    players: dict[PlayerId, PlayerState] = {}
    for pid, player in base.players.items():
        forced_role: Role = "IMPOSTOR" if pid == "p-3" else "CREWMATE"
        players[pid] = replace(player, role=forced_role, room=rooms[pid])
    tasks = {
        "p-1:upload_logs": TaskState(
            id="p-1:upload_logs",
            owner="p-1",
            map_task_id="upload_logs",
            room="ADMIN",
            progress=0,
            required_ticks=6,
            completed=False,
        ),
        "p-2:start_reactor": TaskState(
            id="p-2:start_reactor",
            owner="p-2",
            map_task_id="start_reactor",
            room="REACTOR",
            progress=0,
            required_ticks=10,
            completed=False,
        ),
    }
    state = replace(base, players=players, tasks=tasks, cooldowns={"p-3": 0})

    def _stub(
        *,
        seed: int,
        game_map: Map,
        num_players: int,
        num_impostors: int = 1,
        tasks_per_crewmate: int = 1,
    ) -> WorldState:
        return state

    monkeypatch.setattr("orchestrator.game.seed_initial_state", _stub)
    return state


def _emergency_agent_factory() -> Callable[[PlayerId, Role], object]:
    """p-1 / p-2 are production tactical agents; p-3 kills p-4 then idles."""

    from agents.tactical.crewmate_policy import CrewmatePolicy
    from agents.tactical.impostor_policy import ImpostorPolicy

    def factory(agent_id: PlayerId, role: Role) -> object:
        policy = (
            ImpostorPolicy(agent_id=agent_id)
            if role == "IMPOSTOR"
            else CrewmatePolicy(agent_id=agent_id)
        )
        inner = TacticalAgent(agent_id=agent_id, role=role, policy=policy)
        if agent_id == "p-3":
            return _MeetingAwareScriptedAgent(
                inner=inner,
                intents=[
                    _intent(
                        {
                            "type": "kill",
                            "actor": "p-3",
                            "payload": {"target": "p-4"},
                        }
                    )
                ],
            )
        if agent_id == "p-4":
            return _MeetingAwareScriptedAgent(inner=inner)
        return inner

    return factory


def _emergency_runner(vote_target: str) -> DefaultMeetingRunner:
    """A :class:`DefaultMeetingRunner` over the REAL prompt templates."""

    from agents.strategic.prompts import (
        accusation_round_prompt,
        crewmate_report_prompt,
        impostor_report_prompt,
        vote_ballot_prompt,
    )

    return DefaultMeetingRunner(
        llm_client=_EmergencyChainLLMClient(vote_target=vote_target),
        crewmate_report_prompt=crewmate_report_prompt,
        impostor_report_prompt=impostor_report_prompt,
        statement_prompt=accusation_round_prompt,
        vote_prompt=vote_ballot_prompt,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        ),
    )


def _run_emergency_game(
    *,
    replay_path: Path,
    vote_target: str,
    max_ticks: int = 40,
) -> tuple[WorldState, str]:
    game_map = load_canonical_map()
    game = HeadlessGame(
        seed=_EMERGENCY_SEED,
        game_map=game_map,
        agent_factory=_emergency_agent_factory(),  # type: ignore[arg-type]
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=max_ticks),
        meeting_runner=_emergency_runner(vote_target),
    )
    result = game.run()
    return result.final_state, result.outcome


class TestEmergencySuspicionMeetingEndToEnd:
    """The Task 10.8 DoD scenario, through the production game loop.

    Tick 0: p-3 kills p-4 in WEST_HALL — unwitnessed (no other player in
    that room). Tick 1: p-1 sees the body from adjacent ADMIN; §6.3 Rule 1
    lifts p-3 across the §4.6 gate in p-1's private beliefs. Ticks 1-2: p-1
    abandons its task and walks ADMIN -> EAST_HALL -> CAFETERIA (the A*
    tie-break avoids the body room, so the body stays unreported). Tick 3:
    p-1 presses the button; the engine opens an EMERGENCY meeting with p-1
    as caller/opener and the meeting runs the unchanged §5.2 protocol.
    """

    def test_unwitnessed_kill_produces_emergency_meeting(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_map = load_canonical_map()
        _emergency_scenario_setup(monkeypatch, game_map=game_map)
        replay_dir = tmp_path / "eject"
        replay_dir.mkdir()
        replay_path = replay_dir / f"replay-seed-{_EMERGENCY_SEED}.jsonl"

        final_state, outcome = _run_emergency_game(
            replay_path=replay_path, vote_target="p-3"
        )

        # Ejecting the sole impostor ends the game: CREWMATE_EJECT.
        assert outcome == "CREWMATES"
        assert final_state.players["p-3"].alive is False
        # The caller's one emergency call per game is spent — engine truth.
        assert final_state.emergency_uses == {"p-1": 1}

        entries = read_all_entries(replay_path)
        meetings = [e for e in entries if isinstance(e, MeetingReplayEntry)]
        assert len(meetings) == 1
        meeting = meetings[0]

        # EMERGENCY-triggered, caller as opener, at the post-walk tick.
        assert meeting.triggered_by == "p-1"
        assert meeting.tick == 3
        opening = meeting.transcript.turns[0]
        assert opening.turn_kind == "opening"
        assert opening.speaker == "p-1"

        # §5.2 chain rules unchanged: the accused replies, the chain
        # terminates on the claim-free reply, and the co-present
        # non-speaker takes a terminal opt-in turn.
        kinds = [(t.turn_kind, t.speaker) for t in meeting.transcript.turns]
        assert kinds == [("opening", "p-1"), ("reply", "p-3"), ("opt_in", "p-2")]
        assert meeting.transcript.turns[1].reply_to == opening.turn_id

        # Ballots run normally: one per living participant; the accused's
        # self-target ballot is normalized to SKIP, the two crew votes
        # carry the plurality over the §4.6 threshold.
        assert len(meeting.ballots) == 3
        assert meeting.outcome == "EJECTED"
        assert meeting.ejected_player_id == "p-3"

        # Body-less meeting: no found_body observation anywhere in the
        # transcript (the body was never discovered in-room).
        for turn in meeting.transcript.turns:
            assert not any(
                isinstance(obs, FoundBodyObservation) for obs in turn.observations
            )

        # A fresh replay records the v7 template revision (DoD version pin).
        assert meeting.prompt_versions["crewmate_report"] == "crewmate_report.v7"

        # The opening prompt rendered through the REAL crewmate template
        # carries the emergency trigger description and the v7
        # called-on-suspicion frame — the orchestrator phrase and the
        # template branch met end-to-end. Task 10.11: the frame now forbids
        # a found_body observation.
        opening_call = meeting.llm_calls[0]
        assert opening_call.call_kind == "meeting"
        assert "called an emergency meeting" in opening_call.prompt
        assert "YOU called this emergency meeting" in opening_call.prompt
        assert "no body was reported" in opening_call.prompt
        assert "do NOT emit a `found_body` observation" in opening_call.prompt

    def test_eval_readers_run_clean_on_emergency_meeting_replay(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # DoD: nothing downstream assumes a body — the eval loaders and
        # every §11.3 analyzer run clean over an EMERGENCY meeting replay,
        # and the trigger breakdown positively identifies it.
        from eval.balance_eval import load_tournament_report
        from eval.meeting_quality import build_tournament_eval_report

        game_map = load_canonical_map()
        scenario = _emergency_scenario_setup(monkeypatch, game_map=game_map)
        replay_dir = tmp_path / "eval-read"
        replay_dir.mkdir()
        replay_path = replay_dir / f"replay-seed-{_EMERGENCY_SEED}.jsonl"
        _run_emergency_game(replay_path=replay_path, vote_target="p-3")

        roles = {pid: player.role for pid, player in scenario.players.items()}
        report = load_tournament_report(
            replay_dir,
            roles_by_seed={_EMERGENCY_SEED: roles},
            game_map=game_map,
            derive_kill_gift=False,
        )
        evaluated = build_tournament_eval_report(report)

        assert evaluated.meeting_rate.meetings_total == 1
        assert evaluated.meeting_rate.emergency_meetings == 1
        assert evaluated.meeting_rate.body_report_meetings == 0
        # The ejection resolved against the impostor, so the conversion
        # analyzers see a well-formed meeting (no crash, sane scalars).
        assert evaluated.conversion.ejection_accuracy == 1.0

    def test_skip_outcome_paces_exactly_one_meeting(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # After a SKIP resolution the crossed flag resets and the caller's
        # call is spent, so the same accumulated suspicion cannot spam a
        # second meeting; the game runs on to a clean CREWMATE_TASKS end.
        game_map = load_canonical_map()
        _emergency_scenario_setup(monkeypatch, game_map=game_map)
        replay_path = tmp_path / f"replay-seed-{_EMERGENCY_SEED}.jsonl"

        final_state, outcome = _run_emergency_game(
            replay_path=replay_path, vote_target="SKIP"
        )

        assert outcome == "CREWMATES"
        entries = read_all_entries(replay_path)
        meetings = [e for e in entries if isinstance(e, MeetingReplayEntry)]
        assert len(meetings) == 1
        assert meetings[0].outcome == "SKIPPED"
        assert final_state.emergency_uses == {"p-1": 1}
        # The impostor survived the skip; the crew won on tasks, so the
        # single emergency meeting neither railroaded nor stalled the game.
        assert final_state.players["p-3"].alive is True

    def test_emergency_game_replays_byte_identically(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Determinism DoD: trigger evaluation and cooldown bookkeeping are
        # deterministic, so two fresh runs of the identical scenario write
        # byte-identical replay logs (meeting included).
        game_map = load_canonical_map()
        _emergency_scenario_setup(monkeypatch, game_map=game_map)
        first_path = tmp_path / "first.jsonl"
        second_path = tmp_path / "second.jsonl"

        _run_emergency_game(replay_path=first_path, vote_target="SKIP")
        _run_emergency_game(replay_path=second_path, vote_target="SKIP")

        assert first_path.read_bytes() == second_path.read_bytes()


def _emergency_opening_result(
    *,
    observations: tuple[ObservationClaim, ...],
    meeting_id: str = "g-1:meeting-0",
) -> MeetingResult:
    """A resolved emergency meeting whose opening carries ``observations``."""

    opening = MeetingTurn(
        turn_id=f"{meeting_id}:turn-0",
        turn_index=0,
        speaker="p-1",
        turn_kind="opening",
        reply_to=None,
        observations=observations,
        free_text="I called this on suspicion (unsure).",
    )
    return MeetingResult(
        meeting_id=meeting_id,
        triggered_by="p-1",
        trigger_tick=3,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
        contradictions=(),
        transcript=MeetingTranscript(turns=(opening,)),
    )


class TestEmergencyOpeningNoBodySelfCheck:
    """Task 10.11 fail-loud self-check (audit-2026-06-13-1816 B-B-1).

    The 10.8 self-check ("engine body_id is None") was TRUE yet masked the
    transcript-level fabrication. This one reads the OPENING TURN, so a model
    that ignores the v7 prompt and re-narrates a stale corpse as a found_body
    on an emergency opening is caught at the source.
    """

    def test_emergency_opening_with_fabricated_body_fails_loud(self) -> None:
        result = _emergency_opening_result(
            observations=(
                FoundBodyObservation(
                    type="found_body", tick=8, body_of="p-2", room="REACTOR"
                ),
            )
        )
        with pytest.raises(RuntimeError, match="emergency meeting"):
            _assert_no_emergency_opening_body(trigger_kind="emergency", result=result)

    def test_emergency_opening_without_body_passes(self) -> None:
        result = _emergency_opening_result(
            observations=(
                SawPlayerObservation(
                    type="saw_player",
                    tick=2,
                    subject="p-3",
                    room="WEST_HALL",
                    co_present=(),
                ),
            )
        )
        # No raise: a suspicion-led opening is the v7 contract.
        _assert_no_emergency_opening_body(trigger_kind="emergency", result=result)

    def test_report_meeting_with_a_body_is_a_no_op(self) -> None:
        # The body-report opening LEADS with the found_body; the check must
        # never fire for a report-triggered meeting.
        result = _emergency_opening_result(
            observations=(
                FoundBodyObservation(
                    type="found_body", tick=8, body_of="p-2", room="REACTOR"
                ),
            )
        )
        _assert_no_emergency_opening_body(trigger_kind="report", result=result)

    def test_empty_transcript_is_a_no_op(self) -> None:
        result = MeetingResult(
            meeting_id="g-1:meeting-0",
            triggered_by="p-1",
            trigger_tick=3,
            outcome="SKIPPED",
            ejected_player_id=None,
            ballots=(),
            contradictions=(),
            transcript=MeetingTranscript(),
        )
        _assert_no_emergency_opening_body(trigger_kind="emergency", result=result)
