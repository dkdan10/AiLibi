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
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.manager import MeetingDeadlines, MeetingTrigger, SuspicionEntry
from meetings.schemas import (
    ContradictionRef,
    MeetingResult,
    MeetingTranscript,
    ReportDocument,
    Statement,
    VoteBallot,
)
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.game import (
    DefaultMeetingRunner,
    HeadlessGame,
    MeetingArtifacts,
    apply_meeting_result,
    build_default_agent_factory,
)
from orchestrator.replay import MeetingReplayEntry, read_all_entries
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
        transcript=MeetingTranscript(reports=(), statements=()),
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
            transcript=MeetingTranscript(reports=(), statements=()),
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
        *, seed: int, game_map: Map, num_players: int, num_impostors: int = 1
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
    ) -> LLMResponse:
        self.calls.append((schema, call_kind))
        if schema is ReportDocument:
            text = ReportDocument(
                agent_id="placeholder",
                tick=0,
                observations=(),
                claims=(),
                free_text="stub-report",
            ).model_dump_json()
        elif schema is Statement:
            text = Statement(
                statement_id="placeholder",
                speaker="placeholder",
                tick=0,
                round_index=0,
                target=None,
                claims=(),
                free_text="stub-statement",
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
) -> str:
    return f"CREWMATE_REPORT agent_id={agent_id} tick={current_tick}"


def _stub_impostor_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
) -> str:
    return f"IMPOSTOR_REPORT agent_id={agent_id} tick={current_tick}"


def _stub_statement_prompt(
    *,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
) -> str:
    return "STATEMENT_PROMPT"


def _stub_vote_prompt(
    *,
    voter_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradiction_flags: tuple[ContradictionRef, ...],
    suspicion_graph: tuple[SuspicionEntry, ...],
    candidate_targets: tuple[PlayerId, ...],
    skip_confidence_threshold: float,
) -> str:
    return f"VOTE voter={voter_id}"


def _build_default_runner(
    *,
    llm_client: _ScriptedLLMClient,
) -> DefaultMeetingRunner:
    from meetings.manager import MeetingConfig

    config = MeetingConfig(
        round_count=1,
        deadlines=MeetingDeadlines(
            report_seconds=None, statement_seconds=None, vote_seconds=None
        ),
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
        # 3 living crewmates × (1 report + 1 statement + 1 vote) = 9 LLM calls.
        assert len(meeting.llm_calls) == 9
        # Each call carries cost metadata.
        assert all(call.cost_usd == 0.01 for call in meeting.llm_calls)
        # Transcript fields are populated.
        assert len(meeting.transcript.reports) == 3
        assert len(meeting.transcript.statements) == 3
        # Prompt versions metadata persisted.
        assert "crewmate_report" in meeting.prompt_versions
        assert "vote_ballot" in meeting.prompt_versions


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
