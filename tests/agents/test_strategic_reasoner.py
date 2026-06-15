"""Tests for the strategic reasoner (Task 3.9 / 8.8, DESIGN.md §4.4, §5.2, §6.6).

The reasoner composes agent memory, the four reshaped ``.j2`` prompt
templates, the structured-output schemas, and the budget-wrapped LLM
client into one class. Task 8.8 re-sequenced its producers against the
reactive accusation-chain schema (DESIGN.md §5.2): ``produce_report``
emits the **opening** :class:`~meetings.schemas.MeetingTurn`,
``produce_statement`` emits a reactive **reply / opt-in**
:class:`~meetings.schemas.MeetingTurn` (with ``reply_to`` derived from a
``prior_turn`` input), and ``produce_vote`` emits the
:class:`~meetings.schemas.VoteBallot`.

The tests pin every contract downstream code relies on:

* the pipeline runs end to end against the fake provider with no
  network traffic,
* the right prompt template is chosen by role,
* the LLM is never authoritative for identity bookkeeping (the
  reasoner overrides the turn identity fields and ``voter``),
* the rendered prompt inputs are scanned with the canonical packet
  leak scanners from ``eval/leak_test.py`` before they reach the
  LLM, and a planted role-bearing string trips the scanner (R-10
  acceptance gate + C-1 closure),
* the Task 7.12 teammate firewall guard runs on every turn-kind and on
  the vote,
* the same inputs against the deterministic fake provider produce
  byte-identical parsed outputs (determinism check),
* budget overruns from a wrapped :class:`BudgetedLLMClient`
  propagate through the reasoner without being swallowed.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TypeVar

import pytest
from pydantic import BaseModel

from agents.memory.beliefs import ContradictionRef as MemoryContradictionRef
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import AgentMemory, render_for_prompt
from agents.strategic.prompts import (
    accusation_round_prompt as _default_accusation_round_prompt,
)
from agents.strategic.prompts import (
    crewmate_report_prompt as _default_crewmate_report_prompt,
)
from agents.strategic.prompts import (
    impostor_report_prompt as _default_impostor_report_prompt,
)
from agents.strategic.prompts import (
    vote_ballot_prompt as _default_vote_ballot_prompt,
)
from agents.strategic.reasoner import StrategicReasoner
from llm.budget import BudgetExceededError, GameBudget
from llm.budgeted_client import BudgetedLLMClient
from llm.client import CallKind, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from meetings.manager import SuspicionEntry
from meetings.schemas import (
    AccusationClaim,
    Claim,
    ContradictionRef,
    CorroborationClaim,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
    VoteBallot,
)

_T = TypeVar("_T")


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _self_state_event(
    *,
    tick: int,
    role: str = "CREWMATE",
    room: str = "CAFETERIA",
    pending_task_id: str | None = None,
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="self_state",
        payload={
            "room": room,
            "role": role,
            "pending_task_id": pending_task_id,
        },
        provenance="observed",
    )


def _global_status_event(*, tick: int, completed: int, total: int) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="global_status",
        payload={"tasks_completed": completed, "tasks_total": total},
        provenance="inferred",
    )


def _saw_player_event(
    *,
    tick: int,
    player_id: str,
    room: str,
    action: str | None = None,
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type="saw_player",
        payload={"player_id": player_id, "room": room, "action": action},
        provenance="observed",
    )


def _build_memory(role: str = "CREWMATE") -> AgentMemory:
    memory = AgentMemory()
    memory.episodic.append(_self_state_event(tick=0, role=role))
    memory.episodic.append(_global_status_event(tick=0, completed=2, total=12))
    memory.episodic.append(
        _saw_player_event(tick=100, player_id="p-2", room="ELECTRICAL", action=None)
    )
    memory.beliefs.adjust_suspicion("p-2", delta=0.2)
    return memory


def _build_memory_with_leak(
    forbidden_id: str = "crewmate_role_leak_fixture",
) -> AgentMemory:
    """Plant a forbidden role-bearing string into a saw_player payload.

    Mirrors the pattern from eval/leak_test.py and
    tests/agents/test_memory_rendering.py: the leaky string lives in an
    ``id`` slot the rendered memory legitimately surfaces, so the value
    scanner is the one that must trip.
    """

    memory = AgentMemory()
    memory.episodic.append(_self_state_event(tick=0, role="CREWMATE"))
    memory.episodic.append(
        _saw_player_event(tick=10, player_id=forbidden_id, room="STORAGE", action=None)
    )
    return memory


def _opening_turn(*, meeting_id: str = "m-1", speaker: str = "p-1") -> MeetingTurn:
    """An opening turn the reasoner's reply producer can answer."""

    return MeetingTurn(
        turn_id=f"{meeting_id}:turn-0",
        turn_index=0,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        observations=(),
        claims=(
            AccusationClaim(
                type="accusation", against="p-3", confidence=0.6, reason="near body"
            ),
        ),
        free_text="opening turn",
    )


# ---------------------------------------------------------------------------
# Recording LLM client to capture prompts the reasoner emits
# ---------------------------------------------------------------------------


@dataclass
class _RecordingClient:
    """Inner client that returns a configurable response and records calls."""

    responder: Callable[[str, type[BaseModel] | None], str]
    calls: list[dict[str, object]] = field(default_factory=list)
    response_cost_usd: float = 0.0

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
        text = self.responder(prompt, schema)
        if schema is not None:
            schema.model_validate_json(text)
        self.calls.append(
            {
                "prompt": prompt,
                "schema": schema,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "call_kind": call_kind,
                "model": model,
                "agent_id": agent_id,
            }
        )
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=self.response_cost_usd,
            model="fake-recording",
        )


def _stub_turn_json(
    *,
    speaker: str = "lies",
    turn_kind: str = "opening",
    claims: tuple[Claim, ...] = (),
) -> str:
    return MeetingTurn(
        turn_id="ignored-by-reasoner",
        turn_index=99,
        speaker=speaker,
        turn_kind=turn_kind,  # type: ignore[arg-type]
        reply_to="ignored",
        observations=(),
        claims=claims,
        free_text="stub-turn",
    ).model_dump_json()


def _stub_vote_json(*, voter: str = "lies", target: str = "SKIP") -> str:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.7,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text="stub-vote",
    ).model_dump_json()


def _default_responder(prompt: str, schema: type[BaseModel] | None) -> str:
    if schema is MeetingTurn:
        return _stub_turn_json()
    if schema is VoteBallot:
        return _stub_vote_json()
    raise AssertionError(f"unexpected schema {schema!r}; prompt={prompt!r}")


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_default_prompt_callables_are_loader_builtins(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())

        assert reasoner._crewmate_report_prompt is _default_crewmate_report_prompt  # noqa: SLF001
        assert reasoner._impostor_report_prompt is _default_impostor_report_prompt  # noqa: SLF001
        assert reasoner._statement_prompt is _default_accusation_round_prompt  # noqa: SLF001
        assert reasoner._vote_prompt is _default_vote_ballot_prompt  # noqa: SLF001

    def test_zero_token_budget_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="token_budget"):
            StrategicReasoner(llm_client=FakeProvider(), token_budget=0)

    def test_negative_turn_max_tokens_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="turn_max_tokens"):
            StrategicReasoner(llm_client=FakeProvider(), turn_max_tokens=0)

    def test_negative_vote_max_tokens_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="vote_max_tokens"):
            StrategicReasoner(llm_client=FakeProvider(), vote_max_tokens=0)

    def test_out_of_range_skip_threshold_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="skip_confidence_threshold"):
            StrategicReasoner(llm_client=FakeProvider(), skip_confidence_threshold=1.5)

    def test_llm_client_property_exposes_inner_client(self) -> None:
        client = FakeProvider()
        reasoner = StrategicReasoner(llm_client=client)

        assert reasoner.llm_client is client


# ---------------------------------------------------------------------------
# Pipeline -- opening turn
# ---------------------------------------------------------------------------


class TestProduceReport:
    def test_pipeline_calls_llm_and_returns_opening_turn(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="CREWMATE")

        turn = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="p-3 reported a body at tick 410",
            )
        )

        assert isinstance(turn, MeetingTurn)
        assert len(client.calls) == 1
        call = client.calls[0]
        assert call["schema"] is MeetingTurn
        assert call["call_kind"] == "meeting"

    def test_role_routes_to_crewmate_template(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="CREWMATE")

        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )

        prompt = str(client.calls[0]["prompt"])
        assert "**crewmate**" in prompt
        assert "Your role for this match is IMPOSTOR" not in prompt

    def test_role_routes_to_impostor_template(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="IMPOSTOR",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )

        prompt = str(client.calls[0]["prompt"])
        assert "Your role for this match is IMPOSTOR" in prompt
        assert "**crewmate**" not in prompt

    def test_opening_identity_fields_are_overridden_to_canonical_values(
        self,
    ) -> None:
        # The fake stub emits speaker="lies", turn_kind="opening",
        # turn_index=99, reply_to="ignored"; the reasoner must overwrite
        # them with the canonical opening-turn identity.
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="CREWMATE")

        turn = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )

        assert turn.turn_id == "m-1:turn-0"
        assert turn.turn_index == 0
        assert turn.speaker == "p-3"
        assert turn.turn_kind == "opening"
        assert turn.reply_to is None

    def test_invalid_role_rejected_fail_loud(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="role"):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="m-1",
                    agent_id="p-3",
                    role="UNKNOWN",  # type: ignore[arg-type]
                    current_tick=412,
                    meeting_trigger="trigger",
                )
            )

    def test_empty_meeting_id_rejected(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="meeting_id"):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="",
                    agent_id="p-3",
                    role="CREWMATE",
                    current_tick=412,
                    meeting_trigger="trigger",
                )
            )


# ---------------------------------------------------------------------------
# Pipeline -- reactive reply / opt-in turn
# ---------------------------------------------------------------------------


class TestProduceStatement:
    def test_pipeline_calls_llm_and_returns_turn(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        turn = _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-1",
                speaker="p-3",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(),
                prior_turn=_opening_turn(),
            )
        )

        assert isinstance(turn, MeetingTurn)
        assert len(client.calls) == 1
        assert client.calls[0]["schema"] is MeetingTurn

    def test_identity_fields_are_overridden_with_reply_to_from_prior_turn(
        self,
    ) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()
        prior = _opening_turn(meeting_id="m-meeting-id", speaker="p-1")

        turn = _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-meeting-id",
                speaker="p-3",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(turns=(prior,)),
                prior_turn=prior,
            )
        )

        assert turn.turn_id == "m-meeting-id:turn-1"
        assert turn.speaker == "p-3"
        assert turn.turn_index == 1
        assert turn.turn_kind == "reply"
        assert turn.reply_to == "m-meeting-id:turn-0"

    def test_opt_in_turn_has_no_reply_to(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        turn = _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-1",
                speaker="p-7",
                turn_index=3,
                turn_kind="opt_in",
                transcript=MeetingTranscript(),
                prior_turn=None,
            )
        )

        assert turn.turn_kind == "opt_in"
        assert turn.reply_to is None

    def test_empty_meeting_id_rejected(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="meeting_id"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                )
            )

    def test_negative_turn_index_rejected(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="turn_index"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=-1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                )
            )

    def test_opening_turn_kind_rejected_fail_loud(self) -> None:
        # The opening turn is produce_report's job; passing "opening" to
        # produce_statement is a wiring bug and must fail loud.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="turn_kind"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="opening",
                    transcript=MeetingTranscript(),
                )
            )

    def test_reply_without_prior_turn_rejected_fail_loud(self) -> None:
        # A reply must reference the accusing turn it answers; without a
        # prior_turn it would record reply_to=None and the transcript could
        # not reconstruct the accusation edge. Fail loud before the LLM call.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="prior_turn"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                    prior_turn=None,
                )
            )

    def test_opt_in_with_prior_turn_rejected_fail_loud(self) -> None:
        # An opt-in info-share turn is terminal and answers no specific turn,
        # so it must not carry a prior_turn.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="opt_in"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-7",
                    turn_index=3,
                    turn_kind="opt_in",
                    transcript=MeetingTranscript(),
                    prior_turn=_opening_turn(),
                )
            )


# ---------------------------------------------------------------------------
# Pipeline -- vote
# ---------------------------------------------------------------------------


class TestProduceVote:
    def test_pipeline_calls_llm_and_returns_parsed_vote(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        ballot = _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
            )
        )

        assert isinstance(ballot, VoteBallot)
        assert len(client.calls) == 1
        assert client.calls[0]["schema"] is VoteBallot

    def test_voter_is_overridden_to_canonical_id(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        ballot = _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
            )
        )

        assert ballot.voter == "p-3"

    def test_per_call_skip_threshold_overrides_default(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
                skip_confidence_threshold=0.42,
            )
        )

        prompt = str(client.calls[0]["prompt"])
        assert "0.42" in prompt

    def test_out_of_range_per_call_skip_threshold_rejected(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="skip_confidence_threshold"):
            _run(
                reasoner.produce_vote(
                    memory=memory,
                    voter="p-3",
                    transcript=MeetingTranscript(),
                    candidate_targets=("p-1", "p-2"),
                    skip_confidence_threshold=1.5,
                )
            )

    def test_suspicion_graph_is_forwarded_to_prompt(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
                suspicion_graph=(
                    SuspicionEntry(player_id="p-1", suspicion=0.4, trust=0.5),
                    SuspicionEntry(player_id="p-2", suspicion=0.8, trust=0.2),
                ),
            )
        )

        prompt = str(client.calls[0]["prompt"])
        assert "suspicion 0.80" in prompt
        assert "trust 0.20" in prompt


# ---------------------------------------------------------------------------
# Per-call agent_id attribution (Task 4.7 follow-up: trigger-path calls)
# ---------------------------------------------------------------------------


class TestTriggerCallAgentIdAttribution:
    """The reasoner tags every trigger-path ``complete()`` with its agent id.

    Mirrors the meeting-manager attribution so the recording wrapper stamps a
    non-None ``LLMCallRecord.agent_id`` on calls made through the per-agent
    ``kill_witnessed`` / ``body_found`` trigger paths (Task 4.7, DESIGN.md §5,
    §11.4).
    """

    def test_produce_report_passes_agent_id(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)

        _run(
            reasoner.produce_report(
                memory=_build_memory(role="CREWMATE"),
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )

        assert client.calls[0]["agent_id"] == "p-3"

    def test_produce_statement_passes_speaker_as_agent_id(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)

        _run(
            reasoner.produce_statement(
                memory=_build_memory(),
                meeting_id="m-1",
                speaker="p-2",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(),
                prior_turn=_opening_turn(),
            )
        )

        assert client.calls[0]["agent_id"] == "p-2"

    def test_produce_vote_passes_voter_as_agent_id(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)

        _run(
            reasoner.produce_vote(
                memory=_build_memory(),
                voter="p-4",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
            )
        )

        assert client.calls[0]["agent_id"] == "p-4"


# ---------------------------------------------------------------------------
# Determinism (DESIGN.md §0 + integration-risk note)
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_memory_same_provider_yields_byte_identical_turn(self) -> None:
        # Run the same reasoning twice and assert byte-identical
        # outputs. FakeProvider derives all values from prompt content,
        # so this exercises the full pipeline's determinism contract.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")

        first = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )
        second = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )

        assert first == second
        assert first.model_dump_json() == second.model_dump_json()

    def test_same_memory_same_provider_yields_byte_identical_vote(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")

        first = _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
            )
        )
        second = _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
            )
        )

        assert first == second


# ---------------------------------------------------------------------------
# R-10 acceptance gate (planted leak + clean memory)
# ---------------------------------------------------------------------------


class TestR10LeakScannerAcceptanceGate:
    """R-10 acceptance gate (audits/audit-2026-05-15-0225-reconciled.md §R-10).

    Closes C-1 from audits/audit-2026-05-16-2239-claude.md by reusing
    the canonical scanners from eval/leak_test.py directly. A regression
    that silently suppresses the scanner (or re-implements it) must
    fail these tests. The scan runs on every turn-kind and the vote.
    """

    def test_clean_memory_passes_through_pipeline(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")

        # Should not raise.
        turn = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )
        assert turn.speaker == "p-3"

    def test_planted_role_bearing_player_id_trips_scanner(self) -> None:
        # The canonical value scanner allow-lists `self_state.role`
        # only. A forbidden substring ("crewmate") planted into an
        # observed `player_id` surfaces inside the rendered observations
        # body when render_for_prompt runs, and the scanner must trip
        # before the prompt reaches the LLM.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory_with_leak(forbidden_id="crewmate_leak_id")

        with pytest.raises(AssertionError, match="role-bearing value"):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="m-1",
                    agent_id="p-3",
                    role="CREWMATE",
                    current_tick=412,
                    meeting_trigger="trigger",
                )
            )

    def test_planted_role_bearing_contradiction_trips_scanner(self) -> None:
        # A second planted negative test: inject a forbidden substring
        # into a contradiction summary. The contradictions section is
        # part of the rendered memory the reasoner scans before sending
        # to the LLM. Exercised on the reactive-turn (reply) path.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")
        memory.beliefs.record_contradiction(
            "p-4",
            MemoryContradictionRef(
                summary="impostor sighting near MEDBAY",
                left_ref="alibi:p-4",
                right_ref="sighting:p-5:p-4",
            ),
        )

        with pytest.raises(AssertionError, match="role-bearing value"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                )
            )

    def test_planted_role_bearing_meeting_trigger_trips_scanner(self) -> None:
        # A free-text input the reasoner OWNS (the meeting_trigger
        # string) gets scanned too. A forbidden substring there must
        # trip even when the rendered memory itself is clean.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")

        with pytest.raises(AssertionError, match="role-bearing value"):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="m-1",
                    agent_id="p-3",
                    role="CREWMATE",
                    current_tick=412,
                    meeting_trigger="this trigger names an impostor explicitly",
                )
            )

    def test_killed_by_substring_in_contradiction_summary_trips_scanner(
        self,
    ) -> None:
        """Defense-in-depth pin (P2 review, round 2): the canonical
        ``_assert_no_recursive_hidden_fields`` scanner walks JSON KEY
        names, not string VALUES. A free-text input containing the
        forbidden field-name substring ``killed_by`` would slip past
        it. The supplementary substring check catches the text-surface
        case.
        """

        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")
        memory.beliefs.record_contradiction(
            "p-4",
            MemoryContradictionRef(
                summary="p-2 was killed_by p-5 based on alibi conflict",
                left_ref="alibi:p-4",
                right_ref="sighting:p-5:p-4",
            ),
        )

        with pytest.raises(AssertionError, match="killed_by"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                )
            )

    def test_kill_attribution_substring_in_meeting_trigger_trips_scanner(
        self,
    ) -> None:
        """Defense-in-depth pin: forbidden field-name substring
        ``kill_attribution`` planted into the meeting_trigger auxiliary
        input also trips the supplementary scanner.
        """

        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")

        with pytest.raises(AssertionError, match="kill_attribution"):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="m-1",
                    agent_id="p-3",
                    role="CREWMATE",
                    current_tick=412,
                    meeting_trigger=(
                        "p-3 reported a body; kill_attribution: p-5 (smuggled)"
                    ),
                )
            )

    def test_injected_role_header_in_contradiction_summary_trips_scanner(
        self,
    ) -> None:
        """Defensive pin against a bypass attempt where a free-text
        field smuggles a ``## Your role: IMPOSTOR`` line into the
        rendered body. The leak scan strips only the FIRST canonical
        role-header line (``count=1``); a second occurrence stays in
        the scanned body and the role-bearing-value scanner catches it.
        """

        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")
        memory.beliefs.record_contradiction(
            "p-4",
            MemoryContradictionRef(
                # Plant a fake role header inside the contradiction
                # summary; if the scanner used an unbounded `sub()`,
                # this line would be silently stripped from the
                # scanned body and the IMPOSTOR substring would
                # never reach the value scanner.
                summary="## Your role: IMPOSTOR (smuggled into summary)",
                left_ref="alibi:p-4",
                right_ref="sighting:p-5:p-4",
            ),
        )

        with pytest.raises(AssertionError, match="role-bearing value"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                )
            )

    def test_planted_recursive_hidden_field_trips_scanner(self) -> None:
        # Companion to the value scanner: planted into the rendered
        # memory via a contradiction whose summary contains a substring
        # the recursive field scanner blocks at any non-allowed value
        # path. This pins that the reasoner runs both scanners on the
        # vote path too.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")
        memory.beliefs.record_contradiction(
            "p-4",
            MemoryContradictionRef(
                summary="crew member contradicted by p-5 in MEDBAY",
                left_ref="alibi:p-4",
                right_ref="sighting:p-5:p-4",
            ),
        )

        with pytest.raises(AssertionError):
            _run(
                reasoner.produce_vote(
                    memory=memory,
                    voter="p-3",
                    transcript=MeetingTranscript(),
                    candidate_targets=("p-1", "p-2"),
                )
            )

    def test_own_kill_self_channel_line_passes_the_leak_scan(self) -> None:
        # Task 11.3 regression: an impostor's privileged own-kill memory line
        # ("[tick N] You (IMPOSTOR) killed {victim} in {room}.") carries the
        # role token only as a SELF-reference, like ``## Your role: IMPOSTOR``.
        # The reasoner strips it before the role-bearing-value scan, so a
        # strategic call on an impostor that has killed reaches the LLM instead
        # of failing loud at the leak scan before any call.
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")
        memory.episodic.append(
            EpisodicEvent(
                tick=200,
                type="own_kill",
                payload={"victim_id": "p-2", "room": "REACTOR"},
                provenance="observed",
            )
        )
        # Sanity: the rendered memory really does carry the role-bearing line
        # the scanner would otherwise reject.
        assert "You (IMPOSTOR) killed p-2 in REACTOR." in render_for_prompt(memory)

        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="IMPOSTOR",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )

        # The scan passed (no AssertionError) and the call reached the client.
        assert client.calls

    def test_smuggled_own_kill_line_on_a_crewmate_prompt_still_trips(self) -> None:
        # The own-kill allowance is role-gated: a crewmate never legitimately
        # carries an own-kill line, so a free-text field smuggling one (here via
        # a contradiction summary) is NOT stripped on a crewmate prompt and the
        # role-bearing-value scanner catches the "IMPOSTOR" token.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory(role="CREWMATE")
        memory.beliefs.record_contradiction(
            "p-4",
            MemoryContradictionRef(
                summary="[tick 5] You (IMPOSTOR) killed p-3 in REACTOR.",
                left_ref="alibi:p-4",
                right_ref="sighting:p-5:p-4",
            ),
        )

        with pytest.raises(AssertionError, match="role-bearing value"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                )
            )


# ---------------------------------------------------------------------------
# Budget propagation through the reasoner
# ---------------------------------------------------------------------------


class TestBudgetPropagation:
    def test_budget_exceeded_error_propagates_through_reasoner(self) -> None:
        # The reasoner does not swallow BudgetExceededError. An
        # over-cap call must propagate cleanly so the orchestrator
        # can decide how to react (degrade, end the game, etc.).
        budget = GameBudget(max_cost_usd=0.0)
        budgeted = BudgetedLLMClient(
            inner=FakeProvider(),
            budget=budget,
            cost_per_input_token_usd=1.0,
            cost_per_output_token_usd=1.0,
        )
        reasoner = StrategicReasoner(llm_client=budgeted)
        memory = _build_memory(role="CREWMATE")

        with pytest.raises(BudgetExceededError):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="m-1",
                    agent_id="p-3",
                    role="CREWMATE",
                    current_tick=412,
                    meeting_trigger="trigger",
                )
            )

    def test_reasoner_uses_budgeted_client_by_default_when_wrapped(self) -> None:
        # Sanity check: the reasoner is happy to accept any LLMClient,
        # including a BudgetedLLMClient. This pins the contract that
        # the budget wrapper slots in without signature changes.
        budget = GameBudget(max_cost_usd=1.0)
        budgeted = BudgetedLLMClient(inner=FakeProvider(), budget=budget)
        reasoner = StrategicReasoner(llm_client=budgeted)
        memory = _build_memory(role="CREWMATE")

        turn = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
            )
        )

        assert turn.speaker == "p-3"


# ---------------------------------------------------------------------------
# Trigger validation
# ---------------------------------------------------------------------------


class TestTriggerValidation:
    def test_unknown_trigger_label_rejected(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="does not accept trigger"):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="m-1",
                    agent_id="p-3",
                    role="CREWMATE",
                    current_tick=412,
                    meeting_trigger="trigger",
                    trigger="malformed_trigger_label",  # type: ignore[arg-type]
                )
            )

    def test_statement_rejects_kill_witnessed_trigger(self) -> None:
        # produce_statement is only valid for meeting-phase calls;
        # a kill_witnessed label is a wiring bug that would otherwise
        # silently route to the trigger model tier. The label itself
        # is a valid StrategicTrigger so mypy accepts it; the per-
        # method runtime guard is what rejects it.
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="produce_statement.*kill_witnessed"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                    trigger="kill_witnessed",
                )
            )

    def test_statement_rejects_meeting_vote_trigger(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="produce_statement.*meeting_vote"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                    trigger="meeting_vote",
                )
            )

    def test_vote_rejects_body_found_trigger(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="produce_vote.*body_found"):
            _run(
                reasoner.produce_vote(
                    memory=memory,
                    voter="p-3",
                    transcript=MeetingTranscript(),
                    candidate_targets=("p-1", "p-2"),
                    trigger="body_found",
                )
            )

    def test_vote_rejects_meeting_report_trigger(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="produce_vote.*meeting_report"):
            _run(
                reasoner.produce_vote(
                    memory=memory,
                    voter="p-3",
                    transcript=MeetingTranscript(),
                    candidate_targets=("p-1", "p-2"),
                    trigger="meeting_report",
                )
            )

    def test_report_rejects_meeting_statement_trigger(self) -> None:
        reasoner = StrategicReasoner(llm_client=FakeProvider())
        memory = _build_memory()

        with pytest.raises(ValueError, match="produce_report.*meeting_statement"):
            _run(
                reasoner.produce_report(
                    memory=memory,
                    meeting_id="m-1",
                    agent_id="p-3",
                    role="CREWMATE",
                    current_tick=412,
                    meeting_trigger="trigger",
                    trigger="meeting_statement",
                )
            )

    def test_kill_witnessed_trigger_is_accepted(self) -> None:
        # DESIGN.md §4.4 lists kill_witnessed / body_found as valid
        # specified trigger points outside of meetings.
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
                trigger="kill_witnessed",
            )
        )

        assert len(client.calls) == 1


# ---------------------------------------------------------------------------
# Trigger -> CallKind routing (DESIGN.md §4.4)
# ---------------------------------------------------------------------------


class TestTriggerCallKindRouting:
    """The strategic trigger label controls which model tier the LLM
    call routes through. Meeting-protocol calls use the meeting tier
    (Sonnet in production); the kill-witnessed / body-found triggered
    checks use the cheaper trigger tier (Haiku in production). A
    regression that hard-codes ``call_kind="meeting"`` mis-routes
    triggered checks to the meeting tier and breaks cost attribution.
    """

    def test_meeting_report_routes_to_meeting_tier(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
                trigger="meeting_report",
            )
        )

        assert client.calls[0]["call_kind"] == "meeting"

    def test_kill_witnessed_trigger_routes_to_trigger_tier(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
                trigger="kill_witnessed",
            )
        )

        assert client.calls[0]["call_kind"] == "trigger"

    def test_body_found_trigger_routes_to_trigger_tier(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="CREWMATE",
                current_tick=412,
                meeting_trigger="trigger",
                trigger="body_found",
            )
        )

        assert client.calls[0]["call_kind"] == "trigger"

    def test_statement_meeting_trigger_routes_to_meeting_tier(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-1",
                speaker="p-3",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(),
                prior_turn=_opening_turn(),
            )
        )

        assert client.calls[0]["call_kind"] == "meeting"

    def test_vote_meeting_trigger_routes_to_meeting_tier(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()

        _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
            )
        )

        assert client.calls[0]["call_kind"] == "meeting"


# ---------------------------------------------------------------------------
# Scripted-client pass-through of forwarded inputs
# ---------------------------------------------------------------------------


class TestForwardedInputs:
    def test_contradiction_flags_forwarded_to_statement_prompt(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()
        contradictions = (
            ContradictionRef(
                contradiction_id="c-1",
                kind="alibi_conflict",
                event_a_id="m-1:turn-0:claim-0",
                event_b_id="m-1:turn-1:claim-0",
                subjects=("p-5",),
                description="alibi conflict for p-5 around tick 405",
            ),
        )

        _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-1",
                speaker="p-3",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(),
                contradictions=contradictions,
                prior_turn=_opening_turn(),
            )
        )

        prompt = str(client.calls[0]["prompt"])
        assert "alibi_conflict" in prompt
        assert "alibi conflict for p-5 around tick 405" in prompt

    def test_prior_turn_forwarded_to_statement_prompt(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()
        prior = _opening_turn(meeting_id="m-1", speaker="p-1")

        _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-1",
                speaker="p-3",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(turns=(prior,)),
                prior_turn=prior,
            )
        )

        prompt = str(client.calls[0]["prompt"])
        # The reply prompt names the accuser (the prior turn's speaker).
        assert "`p-1`" in prompt

    def test_candidate_targets_forwarded_to_vote_prompt(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory()
        targets: tuple[PlayerId, ...] = ("p-1", "p-2", "p-4")

        _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=targets,
            )
        )

        prompt = str(client.calls[0]["prompt"])
        for target in targets:
            assert f"`{target}`" in prompt


# ---------------------------------------------------------------------------
# Task 7.12 — teammate firewall guard + leak-scanner allow-list
# ---------------------------------------------------------------------------


class TestTeammateFirewallGuard:
    """Deterministic teammate guard over the reasoner (Task 7.12).

    Anchored to audit ``audits/audit-2026-06-02-2112-gameplay-data.md``
    gp-imp-1 / D-D-1..D-D-4: an impostor must never PRODUCE a ballot or
    accusation that targets a fellow impostor, regardless of what the
    model emits. The guard is a pure function of ``fellow_impostor_ids``
    (no RNG, no new LLM call) and an exact no-op for a crewmate / sole
    impostor, so replay reconstruction of the committed sets is
    unaffected. In the reactive chain the accusation lives in a turn's
    ``claims`` (there is no separate ``target`` field), so the operative
    guard is dropping a teammate accusation claim from every turn.
    """

    @staticmethod
    def _vote_responder(target: str) -> Callable[[str, type[BaseModel] | None], str]:
        def responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if schema is VoteBallot:
                return _stub_vote_json(voter="lies", target=target)
            return _default_responder(prompt, schema)

        return responder

    def test_ballot_targeting_teammate_coerced_to_skip(self) -> None:
        client = _RecordingClient(responder=self._vote_responder("p-5"))
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        ballot = _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-5"),
                fellow_impostor_ids=("p-5",),
            )
        )

        assert ballot.target == "SKIP"
        assert ballot.voter == "p-3"
        # The original (teammate) target is preserved in the audit marker.
        assert "teammate target" in ballot.rationale_text
        assert "p-5" in ballot.rationale_text

    def test_ballot_targeting_crewmate_is_unchanged(self) -> None:
        # Control: a non-teammate target survives the guard untouched.
        client = _RecordingClient(responder=self._vote_responder("p-1"))
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        ballot = _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-5"),
                fellow_impostor_ids=("p-5",),
            )
        )

        assert ballot.target == "p-1"
        assert "teammate target" not in ballot.rationale_text

    def test_opening_accusation_against_teammate_dropped_corroboration_kept(
        self,
    ) -> None:
        accusation = AccusationClaim(
            type="accusation", against="p-5", confidence=0.8, reason="framing teammate"
        )
        corroboration = CorroborationClaim(
            type="corroboration", supports="p-5", on_tick=10, reason="back teammate"
        )

        def responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if schema is MeetingTurn:
                return _stub_turn_json(
                    turn_kind="opening", claims=(accusation, corroboration)
                )
            return _default_responder(prompt, schema)

        client = _RecordingClient(responder=responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        turn = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="IMPOSTOR",
                current_tick=412,
                meeting_trigger="trigger",
                fellow_impostor_ids=("p-5",),
            )
        )

        # The accusation against the teammate is gone; corroboration (which
        # HELPS the teammate) is retained.
        assert not any(
            isinstance(c, AccusationClaim) and c.against == "p-5" for c in turn.claims
        )
        assert any(
            isinstance(c, CorroborationClaim) and c.supports == "p-5"
            for c in turn.claims
        )

    def test_reply_accusation_against_teammate_dropped(self) -> None:
        accusation = AccusationClaim(
            type="accusation", against="p-5", confidence=0.8, reason="x"
        )

        def responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if schema is MeetingTurn:
                return _stub_turn_json(turn_kind="reply", claims=(accusation,))
            return _default_responder(prompt, schema)

        client = _RecordingClient(responder=responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        turn = _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-1",
                speaker="p-3",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(),
                prior_turn=_opening_turn(),
                fellow_impostor_ids=("p-5",),
            )
        )

        # The chain reads its next speaker off the recorded accusation
        # claims, so dropping the teammate accusation keeps the floor from
        # passing to a teammate.
        assert not any(
            isinstance(c, AccusationClaim) and c.against == "p-5" for c in turn.claims
        )

    def test_teammate_incriminating_observation_dropped_on_turn(self) -> None:
        # The MeetingTurn schema added an `observations` channel; a saw_player
        # observation naming a teammate publicly places that teammate near the
        # body / accused and would bypass the accusation-claim guard. The
        # deterministic guard drops a teammate-subject sighting and filters a
        # teammate id out of a non-teammate sighting's co_present list.
        teammate_sighting = SawPlayerObservation(
            type="saw_player", tick=400, subject="p-5", room="MEDBAY", co_present=()
        )
        crew_sighting_with_teammate = SawPlayerObservation(
            type="saw_player",
            tick=405,
            subject="p-1",
            room="ELECTRICAL",
            co_present=("p-5", "p-2"),
        )

        def responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if schema is MeetingTurn:
                return MeetingTurn(
                    turn_id="ignored",
                    turn_index=99,
                    speaker="lies",
                    turn_kind="reply",
                    reply_to="ignored",
                    observations=(teammate_sighting, crew_sighting_with_teammate),
                    claims=(),
                    free_text="s",
                ).model_dump_json()
            return _default_responder(prompt, schema)

        client = _RecordingClient(responder=responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        turn = _run(
            reasoner.produce_statement(
                memory=memory,
                meeting_id="m-1",
                speaker="p-3",
                turn_index=1,
                turn_kind="reply",
                transcript=MeetingTranscript(),
                prior_turn=_opening_turn(),
                fellow_impostor_ids=("p-5",),
            )
        )

        # The teammate-subject sighting is gone entirely; the crewmate sighting
        # survives with the teammate id stripped from co_present.
        saw = [o for o in turn.observations if isinstance(o, SawPlayerObservation)]
        assert all(o.subject != "p-5" for o in saw)
        assert any(o.subject == "p-1" for o in saw)
        surviving = next(o for o in saw if o.subject == "p-1")
        assert "p-5" not in surviving.co_present
        assert "p-2" in surviving.co_present

    def test_observation_guard_is_noop_for_sole_impostor(self) -> None:
        # A sole impostor (empty fellow list) keeps a teammate-shaped sighting
        # untouched — there is no teammate to protect, so replay is unaffected.
        sighting = SawPlayerObservation(
            type="saw_player", tick=400, subject="p-5", room="MEDBAY", co_present=()
        )

        def responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if schema is MeetingTurn:
                return MeetingTurn(
                    turn_id="ignored",
                    turn_index=99,
                    speaker="lies",
                    turn_kind="opening",
                    reply_to=None,
                    observations=(sighting,),
                    claims=(),
                    free_text="o",
                ).model_dump_json()
            return _default_responder(prompt, schema)

        client = _RecordingClient(responder=responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        turn = _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="IMPOSTOR",
                current_tick=412,
                meeting_trigger="trigger",
                fellow_impostor_ids=(),
            )
        )

        assert any(
            isinstance(o, SawPlayerObservation) and o.subject == "p-5"
            for o in turn.observations
        )

    def test_guard_is_noop_for_sole_impostor(self) -> None:
        # Empty fellow list (a sole impostor) leaves a teammate-shaped
        # target untouched — there is no teammate to protect.
        client = _RecordingClient(responder=self._vote_responder("p-5"))
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        ballot = _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-5"),
                fellow_impostor_ids=(),
            )
        )

        assert ballot.target == "p-5"

    def test_impostor_own_teammate_ids_do_not_trip_leak_scanner(self) -> None:
        # The impostor's own teammate ids are legitimate self-channel data
        # (like the role line) and must NOT trip the leak scanner; the
        # teammate block reaches the impostor's prompt.
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="IMPOSTOR")

        # Should not raise.
        _run(
            reasoner.produce_report(
                memory=memory,
                meeting_id="m-1",
                agent_id="p-3",
                role="IMPOSTOR",
                current_tick=412,
                meeting_trigger="trigger",
                fellow_impostor_ids=("p-5",),
            )
        )

        prompt = str(client.calls[0]["prompt"])
        assert "fellow impostors" in prompt.lower()
        assert "p-5" in prompt

    def test_crewmate_meeting_prompt_carries_no_teammate_block(self) -> None:
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="CREWMATE")

        _run(
            reasoner.produce_vote(
                memory=memory,
                voter="p-3",
                transcript=MeetingTranscript(),
                candidate_targets=("p-1", "p-2"),
                fellow_impostor_ids=(),
            )
        )

        prompt = str(client.calls[0]["prompt"])
        assert "fellow impostors" not in prompt.lower()

    def test_teammate_ids_on_a_crewmate_prompt_trip_the_leak_scanner(self) -> None:
        # Firewall teeth: a crew-misroute — a non-empty teammate list on a
        # CREWMATE prompt — is a leak (it would tell a crewmate who the
        # impostors are) and must fail loud, mirroring the 7.2 crew-empty
        # invariant.
        client = _RecordingClient(responder=_default_responder)
        reasoner = StrategicReasoner(llm_client=client)
        memory = _build_memory(role="CREWMATE")

        with pytest.raises(AssertionError, match="non-impostor prompt"):
            _run(
                reasoner.produce_statement(
                    memory=memory,
                    meeting_id="m-1",
                    speaker="p-3",
                    turn_index=1,
                    turn_kind="reply",
                    transcript=MeetingTranscript(),
                    fellow_impostor_ids=("p-5",),
                )
            )

    def test_determinism_guard_is_replay_stable(self) -> None:
        # The guard is a pure function: two identical calls produce
        # byte-identical guarded ballots (no RNG, no new LLM call).
        memory = _build_memory(role="IMPOSTOR")
        results = []
        for _ in range(2):
            client = _RecordingClient(responder=self._vote_responder("p-5"))
            reasoner = StrategicReasoner(llm_client=client)
            results.append(
                _run(
                    reasoner.produce_vote(
                        memory=memory,
                        voter="p-3",
                        transcript=MeetingTranscript(),
                        candidate_targets=("p-1", "p-5"),
                        fellow_impostor_ids=("p-5",),
                    )
                ).model_dump_json()
            )
        assert results[0] == results[1]
