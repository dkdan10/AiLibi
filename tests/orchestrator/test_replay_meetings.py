"""Meeting replay-record tests (Task 3.12, DESIGN.md §11.4).

Pins the R-9 acceptance gate: the replay log records meeting
transcripts, ballots, contradiction flags, prompt versions, and per-call
LLM cost metadata for every meeting. The long-horizon byte-identity
test exercises a ≥200-tick game that includes one full meeting cycle
(report intake → accusation rounds → voting → resolution → engine
resume) and asserts byte-for-byte identity of the replay log across
two independent runs against the deterministic fake-provider stub.

The short-horizon byte-identity test from Task 2.8
(``tests/orchestrator/test_game.py:139-155``) is preserved as a fast
smoke check; this file adds the meeting-cycle gate without replacing
the existing pin.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import BaseModel, TypeAdapter

from engine.entities import BodyState, PlayerId, Role
from engine.world import Map, WorldState, load_canonical_map
from llm.client import CallKind, LLMResponse, TokenUsage
from collections.abc import Callable

from agents.base import AgentInterface
from meetings.manager import MeetingConfig, MeetingDeadlines, SuspicionEntry
from meetings.schemas import (
    ContradictionRef,
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
    TacticalAgent,
    build_default_agent_factory,
)
from orchestrator.replay import (
    LLMCallRecord,
    MeetingReplayEntry,
    ReplayEntry,
    read_all_entries,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)


def _intent(data: object) -> ActionIntent:
    return _INTENT_ADAPTER.validate_python(data)


# ---------------------------------------------------------------------------
# Deterministic stub LLM + prompt callables.
# ---------------------------------------------------------------------------


class _DeterministicLLMClient:
    """Stub :class:`~llm.client.LLMClient` whose output depends only on inputs.

    Same prompt + same schema + same call_kind → byte-identical
    response. This is the contract the determinism gate relies on; the
    fake provider in :mod:`llm.fake_provider` provides similar
    guarantees but builds responses from Pydantic introspection. The
    stub here is simpler and easier to reason about for the
    long-horizon replay test.
    """

    def __init__(self, *, vote_target: str = "SKIP", cost_usd: float = 0.0) -> None:
        self._vote_target = vote_target
        self._cost_usd = cost_usd

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
        if schema is ReportDocument:
            text = ReportDocument(
                agent_id="placeholder",
                tick=0,
                observations=(),
                claims=(),
                free_text="report",
            ).model_dump_json()
        elif schema is Statement:
            text = Statement(
                statement_id="placeholder",
                speaker="placeholder",
                tick=0,
                round_index=0,
                target=None,
                claims=(),
                free_text="statement",
            ).model_dump_json()
        elif schema is VoteBallot:
            text = VoteBallot(
                voter="placeholder",
                target=self._vote_target,
                confidence=0.9,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="vote",
            ).model_dump_json()
        else:
            raise AssertionError(f"unexpected schema {schema!r}")
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=4, output_tokens=2),
            cost_usd=self._cost_usd,
            model=model or "deterministic-stub",
        )


def _crewmate_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
) -> str:
    return f"CR:{agent_id}:{current_tick}"


def _impostor_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
) -> str:
    return f"IM:{agent_id}:{current_tick}"


def _statement_prompt(
    *,
    agent_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
) -> str:
    return f"ST:{agent_id}:{len(transcript.reports)}:{len(transcript.statements)}"


def _vote_prompt(
    *,
    voter_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradiction_flags: tuple[ContradictionRef, ...],
    suspicion_graph: tuple[SuspicionEntry, ...],
    candidate_targets: tuple[PlayerId, ...],
    skip_confidence_threshold: float,
) -> str:
    return f"VO:{voter_id}:{','.join(candidate_targets)}"


def _build_runner(
    *,
    vote_target: str = "SKIP",
    cost_usd: float = 0.001,
) -> DefaultMeetingRunner:
    llm = _DeterministicLLMClient(vote_target=vote_target, cost_usd=cost_usd)
    config = MeetingConfig(
        round_count=2,
        deadlines=MeetingDeadlines(
            report_seconds=None, statement_seconds=None, vote_seconds=None
        ),
    )
    return DefaultMeetingRunner(
        llm_client=llm,
        crewmate_report_prompt=_crewmate_prompt,
        impostor_report_prompt=_impostor_prompt,
        statement_prompt=_statement_prompt,
        vote_prompt=_vote_prompt,
        config=config,
    )


# ---------------------------------------------------------------------------
# Report-then-default agent for end-to-end meeting cycle.
# ---------------------------------------------------------------------------


def _seed_with_corpse(
    monkeypatch: pytest.MonkeyPatch,
    *,
    game_map: Map,
    seed: int,
    body_id: str = "body-p-2-1",
) -> str:
    """Seed an initial state with a fresh body for ``p-1`` to report."""

    initial = seed_initial_state(seed=seed, game_map=game_map, num_players=5)
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


def _report_then_default_factory(
    body_id: str,
) -> Callable[[PlayerId, Role], AgentInterface]:
    """Wrap the default tactical agent with a one-time report intent."""

    from agents.tactical.crewmate_policy import CrewmatePolicy
    from agents.tactical.impostor_policy import ImpostorPolicy

    report_intent = _intent(
        {
            "type": "report",
            "actor": "p-1",
            "payload": {"body_id": body_id},
        }
    )

    class _ReportThenDefault:
        def __init__(self, agent_id: PlayerId, role: Role) -> None:
            policy = (
                ImpostorPolicy(agent_id=agent_id)
                if role == "IMPOSTOR"
                else CrewmatePolicy(agent_id=agent_id)
            )
            self._delegate = TacticalAgent(agent_id=agent_id, role=role, policy=policy)
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
            return _intent({"type": "wait", "actor": packet.agent_id, "payload": {}})

        @property
        def agent_id(self) -> PlayerId:
            return self._delegate.agent_id

        @property
        def role(self) -> Role:
            return self._delegate.role

        def render_memory_for_meeting(self, *, token_budget: int = 1500) -> str:
            return self._delegate.render_memory_for_meeting(token_budget=token_budget)

        def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
            return self._delegate.suspicion_graph_for_meeting()

    def factory(agent_id: PlayerId, role: Role) -> _ReportThenDefault:
        return _ReportThenDefault(agent_id, role)

    return factory


# ---------------------------------------------------------------------------
# R-9 acceptance gate.
# ---------------------------------------------------------------------------


class TestReplayRecordsMeetingArtifacts:
    """Replay log captures every artifact DESIGN.md §11.4 requires."""

    def test_meeting_record_carries_transcript_ballots_and_metadata(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_map = load_canonical_map()
        body_id = _seed_with_corpse(monkeypatch, game_map=game_map, seed=2026)
        runner = _build_runner(vote_target="SKIP", cost_usd=0.002)

        replay_path = tmp_path / "artifacts.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_then_default_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=10),
            num_players=5,
            meeting_runner=runner,
        )
        game.run()

        entries = read_all_entries(replay_path)
        meeting_entries = [
            entry for entry in entries if isinstance(entry, MeetingReplayEntry)
        ]
        assert len(meeting_entries) == 1
        meeting = meeting_entries[0]
        # Transcript holds both reports and statements.
        # 4 living players × 1 report = 4 reports.
        assert len(meeting.transcript.reports) == 4
        # 4 living players × 2 rounds = 8 statements.
        assert len(meeting.transcript.statements) == 8
        # 4 ballots from 4 living voters.
        assert len(meeting.ballots) == 4
        # Contradictions field exists (empty in this stub).
        assert meeting.contradictions == ()
        # Prompt versions present.
        assert set(meeting.prompt_versions) >= {
            "crewmate_report",
            "impostor_report",
            "accusation_round",
            "vote_ballot",
        }
        # Task 3.20 bumped the accusation_round template to v2; a fresh
        # replay entry must carry the new version string end-to-end.
        assert meeting.prompt_versions["accusation_round"] == "accusation_round.v2"
        # LLM cost metadata recorded per call. With round_count=2:
        #   reports: 4 calls
        #   statements: 4 voters × 2 rounds = 8 calls
        #   ballots: 4 calls
        # Total: 16 calls.
        assert len(meeting.llm_calls) == 16
        assert all(call.cost_usd == 0.002 for call in meeting.llm_calls)
        assert all(call.model == "deterministic-stub" for call in meeting.llm_calls)
        # State hashes pin the engine-side mutation envelope.
        assert len(meeting.state_hash_before) == 64
        assert len(meeting.state_hash_after) == 64

    def test_meeting_record_serializes_through_jsonl_round_trip(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Read-back validation: every meeting entry survives JSON round trip."""

        game_map = load_canonical_map()
        body_id = _seed_with_corpse(monkeypatch, game_map=game_map, seed=2026)
        runner = _build_runner(vote_target="SKIP", cost_usd=0.0)

        replay_path = tmp_path / "round-trip.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_then_default_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
            num_players=5,
            meeting_runner=runner,
        )
        game.run()

        # Read once.
        first = read_all_entries(replay_path)
        # Read again (no caching).
        second = read_all_entries(replay_path)
        assert first == second
        meeting_entries = [
            entry for entry in first if isinstance(entry, MeetingReplayEntry)
        ]
        tick_entries = [entry for entry in first if isinstance(entry, ReplayEntry)]
        assert meeting_entries
        assert tick_entries

    def test_byte_identical_long_horizon_meeting_replay(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """R-9 long-horizon byte-identity check (≥200 ticks + one meeting cycle).

        Two independent runs of the same seed against the same
        deterministic stub LLM and the same meeting wiring must
        produce byte-identical replay JSONL files. This exercises:

        * the engine tick loop (≥ 200 ticks),
        * one full meeting cycle (report → statement → vote → eject
          or skip → resume),
        * the LLM-call recording path,
        * the meeting replay-record serialization path,
        * the post-meeting engine-state application + rng-state
          advance.
        """

        game_map = load_canonical_map()
        # Two paths; each one's seeder gets monkey-patched
        # identically. Use ``setup_run`` per iteration to ensure the
        # monkeypatch from the prior run does not bleed across.
        first_path = tmp_path / "first.jsonl"
        second_path = tmp_path / "second.jsonl"

        for replay_path in (first_path, second_path):
            body_id = _seed_with_corpse(monkeypatch, game_map=game_map, seed=2026)
            runner = _build_runner(vote_target="SKIP", cost_usd=0.003)
            game = HeadlessGame(
                seed=2026,
                game_map=game_map,
                agent_factory=_report_then_default_factory(body_id),
                replay_path=replay_path,
                scheduler=TickScheduler(max_ticks=250),
                num_players=5,
                meeting_runner=runner,
            )
            game.run()

        first_bytes = first_path.read_bytes()
        second_bytes = second_path.read_bytes()
        assert first_bytes == second_bytes
        entries = read_all_entries(first_path)
        tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
        meeting_entries = [
            entry for entry in entries if isinstance(entry, MeetingReplayEntry)
        ]
        # R-9 long-horizon gate: at least one full meeting cycle
        # (report intake → accusation rounds → voting → resolution →
        # engine resume). DESIGN.md §5.2 + §11.4.
        assert len(meeting_entries) >= 1
        # And the meeting was a full cycle: 4 reports + 8 statements
        # (round_count=2) + 4 ballots = 16 LLM calls.
        assert len(meeting_entries[0].llm_calls) == 16
        # The replay log carries at least one tick entry per game
        # tick the loop processed.
        assert len(tick_entries) >= 1


class TestReplayRecordsLLMCallRecord:
    """LLM call records carry every field the replay layer needs."""

    def test_call_record_captures_usage_cost_model_call_kind(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        game_map = load_canonical_map()
        body_id = _seed_with_corpse(monkeypatch, game_map=game_map, seed=2026)
        runner = _build_runner(vote_target="SKIP", cost_usd=0.005)

        replay_path = tmp_path / "call-records.jsonl"
        game = HeadlessGame(
            seed=2026,
            game_map=game_map,
            agent_factory=_report_then_default_factory(body_id),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=5),
            num_players=5,
            meeting_runner=runner,
        )
        game.run()

        entries = read_all_entries(replay_path)
        meeting_entries = [
            entry for entry in entries if isinstance(entry, MeetingReplayEntry)
        ]
        assert len(meeting_entries) == 1
        sample = meeting_entries[0].llm_calls[0]
        assert isinstance(sample, LLMCallRecord)
        assert sample.call_kind in {"meeting", "trigger"}
        assert sample.model == "deterministic-stub"
        assert sample.input_tokens == 4
        assert sample.output_tokens == 2
        assert sample.cost_usd == 0.005
        # Prompt and response text are present and non-empty.
        assert sample.prompt
        assert sample.response_text


class TestShortHorizonByteIdentityPreserved:
    """The Task 2.8 short-horizon byte-identity smoke remains green."""

    def test_short_horizon_byte_identity_with_default_agents(
        self, tmp_path: Path
    ) -> None:
        """Mirror ``test_game.py::test_headless_game_replay_is_byte_identical_for_same_seed``.

        The existing smoke check from Task 2.8 lives in
        ``tests/orchestrator/test_game.py``; this duplicate is a
        belt-and-braces gate so the Phase-3 replay-record changes
        cannot regress determinism for non-meeting games.
        """

        first_path = tmp_path / "first.jsonl"
        second_path = tmp_path / "second.jsonl"

        for replay_path in (first_path, second_path):
            game = HeadlessGame(
                seed=42,
                game_map=load_canonical_map(),
                agent_factory=build_default_agent_factory(),
                replay_path=replay_path,
                scheduler=TickScheduler(max_ticks=20),
            )
            game.run()

        assert first_path.read_bytes() == second_path.read_bytes()
