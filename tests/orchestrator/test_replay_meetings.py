"""Meeting replay-record tests (Task 3.12, DESIGN.md §11.4).

Pins the R-9 acceptance gate: the replay log records meeting
transcripts, ballots, contradiction flags, prompt versions, and per-call
LLM cost metadata for every meeting. The long-horizon byte-identity
test exercises a ≥200-tick game that includes one full meeting cycle
(opening turn → reactive accusation chain → voting → resolution →
engine resume) and asserts byte-for-byte identity of the replay log
across two independent runs against the deterministic stub LLM.

Re-pointed to the Task 8.7 accusation-chain protocol (DESIGN.md §5.2):
the transcript is the single ordered ``turns`` list (opening → reply →
opt_in), the manager requests one ``MeetingTurn`` per turn, and
``MeetingConfig`` no longer carries a fixed ``round_count`` — the chain
terminates deterministically off the recorded turns. The deterministic
stub drives a real two-turn chain (the opening accuses a living player,
who replies without re-accusing) so the reply path and its ``reply_to``
wiring are recorded and round-tripped.

The short-horizon byte-identity test from Task 2.8
(``tests/orchestrator/test_game.py``) is preserved as a fast smoke
check; this file adds the meeting-cycle gate without replacing the
existing pin.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import BaseModel, TypeAdapter

from agents.base import AgentInterface
from engine.entities import BodyState, PlayerId, Role
from engine.world import Map, WorldState, load_canonical_map
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.manager import MeetingConfig, MeetingDeadlines, SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    TurnKind,
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

# The living player the stub's OPENING turn accuses. Passing the chain to a
# fixed accused keeps the meeting's turn sequence a pure function of the
# wiring: opening (the reporter) → reply (the accused, who does not
# re-accuse) → chain termination → ballots. p-2 is the corpse in the seeded
# setup below, so p-3 is always living when the meeting opens.
_ACCUSED: str = "p-3"


class _DeterministicLLMClient:
    """Stub :class:`~llm.client.LLMClient` whose output depends only on inputs.

    Same prompt + same schema + same call_kind → byte-identical response.
    This is the contract the determinism gate relies on; the fake provider
    in :mod:`llm.fake_provider` provides similar guarantees but builds
    responses from Pydantic introspection. The stub here is simpler and
    easier to reason about for the long-horizon replay test.

    Turn calls (``schema is MeetingTurn``) are dispatched off the prompt
    prefix rendered by the stub prompt callables below: an opening prompt
    (``CR:`` / ``IM:``) yields a turn accusing :data:`_ACCUSED`, which
    hands the chain to that player; a reply / opt-in prompt (``ST:``)
    yields a claim-free turn, which terminates the chain. The manager is
    authoritative for the identity fields (turn_id / turn_index / speaker /
    turn_kind / reply_to), so the placeholders here never reach the record.
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
        if schema is MeetingTurn:
            claims = (
                (
                    AccusationClaim(
                        type="accusation",
                        against=_ACCUSED,
                        confidence=0.6,
                        reason="deterministic stub accusation",
                    ),
                )
                if prompt.startswith(("CR:", "IM:"))
                else ()
            )
            text = MeetingTurn(
                turn_id="placeholder",
                turn_index=0,
                speaker="placeholder",
                turn_kind="opening",
                reply_to=None,
                observations=(),
                claims=claims,
                free_text="turn",
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
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
) -> str:
    return f"CR:{agent_id}:{current_tick}"


def _impostor_prompt(
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
    return f"IM:{agent_id}:{current_tick}"


def _statement_prompt(
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
) -> str:
    return f"ST:{agent_id}:{turn_kind}:{len(transcript.turns)}"


def _vote_prompt(
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
    return f"VO:{voter_id}:{','.join(candidate_targets)}"


def _build_runner(
    *,
    vote_target: str = "SKIP",
    cost_usd: float = 0.001,
) -> DefaultMeetingRunner:
    llm = _DeterministicLLMClient(vote_target=vote_target, cost_usd=cost_usd)
    config = MeetingConfig(
        deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
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
        # Transcript is the ordered chain (DESIGN.md §5.2): the reporter's
        # opening turn accuses _ACCUSED, who replies without re-accusing,
        # terminating the chain. The stub provides no observations, so no
        # opt-in turn is eligible.
        assert len(meeting.transcript.turns) == 2
        opening, reply = meeting.transcript.turns
        assert opening.turn_kind == "opening"
        assert opening.speaker == "p-1"  # the reporter opens
        assert reply.turn_kind == "reply"
        assert reply.speaker == _ACCUSED  # the chain passes to the accused
        assert reply.reply_to == opening.turn_id
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
        # Task 8.8 introduced the reactive chain-turn accusation prompt; the
        # Phase 9 conversion wave bumped it to v5 (decisive reply + opt-in
        # corroboration), Task 9.9 to v6 (free_text length discipline +
        # the living-roster accusation constraint), and Task 10.3 to v7
        # (anti-repetition + the DEAD do-not-accuse line) alongside
        # crewmate_report v5 and impostor_report v4 (accuse-or-declare-unsure
        # openings). A fresh replay entry must carry the live version strings
        # end-to-end; the committed sample bytes still record v6/v4/v3 until
        # the Task 10.5 re-record.
        assert meeting.prompt_versions["accusation_round"] == "accusation_round.v7"
        assert meeting.prompt_versions["crewmate_report"] == "crewmate_report.v5"
        assert meeting.prompt_versions["impostor_report"] == "impostor_report_v4"
        # LLM cost metadata recorded per call. The chain protocol:
        #   turns: 1 opening + 1 reply = 2 calls
        #   ballots: 4 living voters = 4 calls
        # Total: 6 calls.
        assert len(meeting.llm_calls) == 6
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
        * one full meeting cycle (opening → reply chain → vote →
          eject or skip → resume),
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
        # (opening turn → reactive chain → voting → resolution →
        # engine resume). DESIGN.md §5.2 + §11.4.
        assert len(meeting_entries) >= 1
        # And the meeting was a full chain cycle: 2 turns (opening +
        # reply) + 4 ballots = 6 LLM calls.
        assert len(meeting_entries[0].llm_calls) == 6
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
