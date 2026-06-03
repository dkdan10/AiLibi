"""Tests for the meeting state machine (Task 3.8).

The contract exercised here:

* :class:`MeetingManager` follows DESIGN.md §5.1 trigger lifecycle.
* The four phases (report intake, accusation rounds, voting,
  resolution) run in order per DESIGN.md §5.2 and consume the
  appropriate prompt callable.
* Missed deadlines yield default no-statement / no-vote entries that
  still land in the transcript (audit-trail requirement).
* The manager returns a structured :class:`MeetingResult`; it does
  not mutate engine state.
* C-3 statement-ordering pin -- statements are sorted by
  ``(round_index, insertion_order)`` after two rounds with multiple
  participants. The pin fails against an implementation that allows
  ambiguous ordering.

Tests use a controllable in-memory LLM client (no Anthropic SDK calls)
and stub prompt callables. The fake provider in
``llm/fake_provider.py`` is also exercised to confirm Protocol
compatibility.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TypeVar

import pytest
from pydantic import BaseModel, ValidationError

from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from llm.provider import _extract_json_block  # noqa: PLC2701
from meetings.manager import (
    DEFAULT_REPORT_FREE_TEXT,
    DEFAULT_ROUND_COUNT,
    DEFAULT_STATEMENT_FREE_TEXT,
    DEFAULT_VOTE_RATIONALE,
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    LLMProviderError,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    SuspicionEntry,
    _normalize_self_alibi_subjects,  # noqa: PLC2701
    coerce_teammate_ballot_to_skip,
    drop_teammate_statement_target,
    exclude_teammate_accusation_claims,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    ContradictionRef,
    CorroborationClaim,
    MeetingResult,
    MeetingTranscript,
    PlayerId,
    ReportDocument,
    Statement,
    VoteBallot,
)
from meetings.transcript import is_canonically_ordered

_T = TypeVar("_T")

# Default per-player suspicion prior in agents.memory.beliefs (the score a
# player starts at before any belief rule fires). Mirrored here so the Rule-2
# wiring tests can assert "strictly above the default" without importing the
# agents-side constant.
_DEFAULT_TEST_SUSPICION = 0.5


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


# --- Stub prompt callables -------------------------------------------------


# Task 7.12: the four stub renderers accept ``fellow_impostor_ids`` so they
# satisfy the updated renderer Protocols the manager now calls with the
# teammate list. They surface it on a ``FELLOW_IMPOSTORS=`` line ONLY when
# non-empty, so every existing (crewmate / sole-impostor) prompt assertion in
# this module stays byte-stable while the multi-impostor tests can assert the
# manager threaded the teammate list into the prompt.
def _fellow_impostors_line(fellow_impostor_ids: tuple[PlayerId, ...]) -> str:
    if not fellow_impostor_ids:
        return ""
    return f"FELLOW_IMPOSTORS={','.join(fellow_impostor_ids)}\n"


def _crewmate_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    return (
        f"PHASE=REPORT ROLE=CREWMATE agent_id={agent_id} tick={current_tick}\n"
        f"TRIGGER: {meeting_trigger}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"MEMORY:\n{rendered_memory}\n"
        f"PUBLIC_TRANSCRIPT:\n{public_transcript}\n"
    )


def _impostor_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    return (
        f"PHASE=REPORT ROLE=IMPOSTOR agent_id={agent_id} tick={current_tick}\n"
        f"TRIGGER: {meeting_trigger}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"MEMORY:\n{rendered_memory}\n"
        f"PUBLIC_TRANSCRIPT:\n{public_transcript}\n"
    )


def _statement_prompt(
    *,
    agent_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> str:
    return (
        "PHASE=STATEMENT\n"
        f"agent_id={agent_id}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"MEMORY:\n{rendered_memory}\n"
        f"REPORTS_COUNT={len(transcript.reports)}\n"
        f"STATEMENTS_COUNT={len(transcript.statements)}\n"
        f"CONTRADICTIONS_COUNT={len(contradictions)}\n"
    )


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
    suspicion_block = ",".join(
        f"{entry.player_id}:{entry.suspicion:.2f}/{entry.trust:.2f}"
        for entry in suspicion_graph
    )
    return (
        "PHASE=VOTE\n"
        f"voter={voter_id}\n"
        f"candidates={','.join(candidate_targets)}\n"
        f"skip_threshold={skip_confidence_threshold:.2f}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"suspicion={suspicion_block}\n"
        f"MEMORY:\n{rendered_memory}\n"
        f"REPORTS_COUNT={len(transcript.reports)}\n"
        f"STATEMENTS_COUNT={len(transcript.statements)}\n"
        f"FLAGS_COUNT={len(contradiction_flags)}\n"
    )


# --- Test helpers: scripted/recording LLM clients --------------------------


@dataclass
class _CallRecord:
    prompt: str
    schema_name: str | None
    call_kind: CallKind
    agent_id: str | None = None


@dataclass
class _ScriptedLLMClient:
    """LLM client whose response is chosen by a callback from each prompt.

    The callback receives the prompt string and the schema (if any)
    and returns the JSON string the manager should consume. The
    client records every call so tests can assert on the protocol
    sequence (number of report calls, statement calls, vote calls).
    Uses a deterministic ``cost_usd=0.0`` and a fixed model id so
    response equality is byte-stable across calls.
    """

    responder: Callable[[str, type[BaseModel] | None], str]
    calls: list[_CallRecord] = field(default_factory=list)

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
            _CallRecord(
                prompt=prompt,
                schema_name=schema.__name__ if schema is not None else None,
                call_kind=call_kind,
                agent_id=agent_id,
            )
        )
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "scripted-test",
        )


def _stub_report_json(*, agent_id: str, tick: int) -> str:
    # Use values that pass schema validation; manager will override
    # agent_id and tick from the participant.
    return ReportDocument(
        agent_id=agent_id,
        tick=tick,
        observations=(),
        claims=(),
        free_text=f"stub-report-{agent_id}",
    ).model_dump_json()


def _stub_statement_json(*, speaker: str, round_index: int) -> str:
    return Statement(
        statement_id="ignored",
        speaker=speaker,
        tick=0,
        round_index=round_index,
        target=None,
        claims=(),
        free_text=f"stub-statement-{speaker}-r{round_index}",
    ).model_dump_json()


def _stub_vote_json(
    *,
    voter: str,
    target: str,
    confidence: float = 0.8,
) -> str:
    if target == "SKIP":
        return VoteBallot(
            voter=voter,
            target="SKIP",
            confidence=confidence,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text=f"stub-vote-{voter}-skip",
        ).model_dump_json()
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=f"stub-vote-{voter}-{target}",
    ).model_dump_json()


def _make_responder(
    *,
    vote_targets: dict[str, str] | None = None,
) -> Callable[[str, type[BaseModel] | None], str]:
    """Build a responder that dispatches by phase markers in the prompt.

    The phase markers come from the stub prompt callables above. Vote
    targets default to "SKIP" for every voter unless overridden.
    """

    vote_targets = vote_targets or {}

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=REPORT" in prompt:
            agent_id = _extract_marker(prompt, "agent_id=")
            tick_str = _extract_marker(prompt, "tick=")
            return _stub_report_json(agent_id=agent_id, tick=int(tick_str))
        if "PHASE=STATEMENT" in prompt:
            return _stub_statement_json(speaker="placeholder", round_index=0)
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            target = vote_targets.get(voter, "SKIP")
            return _stub_vote_json(voter=voter, target=target)
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    return _responder


def _stub_report_with_alibi_json(
    *, agent_id: str, tick: int, subject: str, room: str, from_tick: int, to_tick: int
) -> str:
    return ReportDocument(
        agent_id=agent_id,
        tick=tick,
        observations=(),
        claims=(
            AlibiClaim(
                type="alibi",
                subject=subject,
                from_tick=from_tick,
                to_tick=to_tick,
                room=room,
            ),
        ),
        free_text=f"stub-report-{agent_id}",
    ).model_dump_json()


def _make_contradiction_responder(
    *,
    subject: str,
    vote_targets: dict[str, str] | None = None,
) -> Callable[[str, type[BaseModel] | None], str]:
    """Responder whose Phase-1 reports plant a genuine alibi conflict.

    Every reporter submits an alibi for ``subject`` but in a different
    room over an overlapping tick range, so ``detect_contradictions``
    raises at least one ``alibi_conflict`` flag naming ``subject``.
    Statements and votes use the standard stubs.
    """

    vote_targets = vote_targets or {}
    # Distinct rooms per reporter id so the alibis genuinely conflict.
    rooms = ("ADMIN", "CAFETERIA", "STORAGE", "MEDBAY", "ELECTRICAL")

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=REPORT" in prompt:
            agent_id = _extract_marker(prompt, "agent_id=")
            tick = int(_extract_marker(prompt, "tick="))
            # Index the room deterministically by the reporter's id suffix
            # so each reporter names a different room for the same subject.
            digit = "".join(ch for ch in agent_id if ch.isdigit()) or "0"
            room = rooms[int(digit) % len(rooms)]
            return _stub_report_with_alibi_json(
                agent_id=agent_id,
                tick=tick,
                subject=subject,
                room=room,
                from_tick=1,
                to_tick=20,
            )
        if "PHASE=STATEMENT" in prompt:
            return _stub_statement_json(speaker="placeholder", round_index=0)
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            target = vote_targets.get(voter, "SKIP")
            return _stub_vote_json(voter=voter, target=target)
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    return _responder


def _extract_marker(prompt: str, marker: str) -> str:
    idx = prompt.find(marker)
    assert idx >= 0, f"marker {marker!r} not found in prompt {prompt!r}"
    rest = prompt[idx + len(marker) :]
    # Marker value runs until the next whitespace or newline.
    end = 0
    while end < len(rest) and not rest[end].isspace():
        end += 1
    return rest[:end]


def _make_participants() -> tuple[MeetingParticipant, ...]:
    return (
        MeetingParticipant(
            agent_id="p-1",
            role="CREWMATE",
            rendered_memory="## Your role: CREWMATE\np-1 memory",
            suspicion_graph=(
                SuspicionEntry(player_id="p-2", suspicion=0.4, trust=0.5),
            ),
        ),
        MeetingParticipant(
            agent_id="p-2",
            role="CREWMATE",
            rendered_memory="## Your role: CREWMATE\np-2 memory",
        ),
        MeetingParticipant(
            agent_id="p-3",
            role="IMPOSTOR",
            rendered_memory="## Your role: IMPOSTOR\np-3 memory",
        ),
    )


def _make_manager(
    *,
    llm_client: LLMClient,
    deadlines: MeetingDeadlines | None = None,
    # Matches the production default (DEFAULT_ROUND_COUNT, 1 since Task 7.10).
    # Tests that exercise multi-round behavior pass round_count=2/3 explicitly.
    round_count: int = 1,
) -> MeetingManager:
    config = MeetingConfig(
        round_count=round_count,
        deadlines=deadlines if deadlines is not None else MeetingDeadlines(),
    )
    return MeetingManager(
        llm_client=llm_client,
        crewmate_report_prompt=_crewmate_report_prompt,
        impostor_report_prompt=_impostor_report_prompt,
        statement_prompt=_statement_prompt,
        vote_prompt=_vote_prompt,
        config=config,
    )


def _default_trigger() -> MeetingTrigger:
    return MeetingTrigger(
        triggered_by="p-1",
        trigger_tick=410,
        description="p-1 reported a body at tick 410",
    )


# --- Construction / configuration ------------------------------------------


class TestConstruction:
    def test_default_config_is_used_when_none_passed(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())

        manager = MeetingManager(
            llm_client=client,
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
        )

        # The manager is a state machine that should not start until
        # `run` is called. Construction must not produce any LLM
        # traffic (DESIGN.md §5.1 trigger lifecycle).
        assert client.calls == []
        assert isinstance(manager, MeetingManager)

    def test_zero_rounds_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())

        with pytest.raises(ValueError, match="round_count"):
            MeetingManager(
                llm_client=client,
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(round_count=0),
            )

    def test_out_of_range_skip_threshold_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())

        with pytest.raises(ValueError, match="skip_confidence_threshold"):
            MeetingManager(
                llm_client=client,
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(skip_confidence_threshold=1.5),
            )


class TestRunPreconditions:
    def test_empty_participants_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)

        with pytest.raises(ValueError, match="at least one"):
            _run(
                manager.run(
                    meeting_id="m-1",
                    trigger=_default_trigger(),
                    participants=(),
                )
            )

    def test_empty_meeting_id_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)

        with pytest.raises(ValueError, match="meeting_id"):
            _run(
                manager.run(
                    meeting_id="",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )

    def test_duplicate_participant_ids_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)

        participants = (
            MeetingParticipant(agent_id="p-1", role="CREWMATE", rendered_memory="m1"),
            MeetingParticipant(
                agent_id="p-1", role="CREWMATE", rendered_memory="m1-dup"
            ),
        )

        with pytest.raises(ValueError, match="unique agent_ids"):
            _run(
                manager.run(
                    meeting_id="m-1",
                    trigger=_default_trigger(),
                    participants=participants,
                )
            )


# --- Phase 1: report intake ------------------------------------------------


class TestReportIntake:
    def test_one_report_per_living_participant(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)

        result = _run(
            manager.run(
                meeting_id="m-reports",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert len(result.transcript.reports) == 3
        assert {r.agent_id for r in result.transcript.reports} == {
            "p-1",
            "p-2",
            "p-3",
        }

    def test_report_tick_matches_trigger_tick(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)
        trigger = MeetingTrigger(
            triggered_by="p-1", trigger_tick=999, description="tick 999"
        )

        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=trigger,
                participants=_make_participants(),
            )
        )

        for report in result.transcript.reports:
            assert report.tick == 999

    def test_role_selects_prompt_template(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)

        _run(
            manager.run(
                meeting_id="m-roles",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        report_calls = [c for c in client.calls if "PHASE=REPORT" in c.prompt]
        crewmate_prompts = [c for c in report_calls if "ROLE=CREWMATE" in c.prompt]
        impostor_prompts = [c for c in report_calls if "ROLE=IMPOSTOR" in c.prompt]
        assert len(crewmate_prompts) == 2
        assert len(impostor_prompts) == 1
        impostor_prompt = impostor_prompts[0].prompt
        assert "agent_id=p-3" in impostor_prompt

    def test_report_agent_id_is_overridden_to_canonical_participant_id(self) -> None:
        # Even if the LLM produces a wrong agent_id, the manager must
        # rewrite it to the participant's id. This is the "identity
        # is bookkept by the manager" contract in the prompt templates.
        def _liar_responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=REPORT" in prompt:
                return _stub_report_json(agent_id="impostor-lies", tick=0)
            if "PHASE=STATEMENT" in prompt:
                return _stub_statement_json(speaker="liar", round_index=0)
            if "PHASE=VOTE" in prompt:
                voter = _extract_marker(prompt, "voter=")
                return _stub_vote_json(voter=voter, target="SKIP")
            raise AssertionError(prompt)

        client = _ScriptedLLMClient(responder=_liar_responder)
        manager = _make_manager(llm_client=client)

        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        agent_ids = sorted(r.agent_id for r in result.transcript.reports)
        assert agent_ids == ["p-1", "p-2", "p-3"]
        for report in result.transcript.reports:
            assert report.tick == 410

    def test_report_missed_deadline_records_default(self) -> None:
        async def _slow_responder(prompt: str) -> str:  # noqa: ARG001
            await asyncio.sleep(1.0)
            return _stub_report_json(agent_id="never", tick=0)

        # A client whose `complete` always sleeps longer than the
        # report deadline -> every report should hit the timeout
        # branch.
        class _SleepingClient:
            calls: list[_CallRecord] = []

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
                if "PHASE=REPORT" in prompt:
                    text = await _slow_responder(prompt)
                else:
                    # Statement / vote responses still need to be
                    # schema-valid so the meeting completes.
                    text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="sleeping",
                )

        client = _SleepingClient()
        manager = MeetingManager(
            llm_client=client,
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(
                round_count=1,
                deadlines=MeetingDeadlines(
                    report_seconds=0.01,
                    statement_seconds=None,
                    vote_seconds=None,
                ),
            ),
        )

        result = _run(
            manager.run(
                meeting_id="m-deadline",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert len(result.transcript.reports) == 3
        for report in result.transcript.reports:
            assert report.free_text == DEFAULT_REPORT_FREE_TEXT
            assert report.observations == ()
            assert report.claims == ()


# --- LLM-call agent_id attribution (Task 4.7, DESIGN.md §5, §11.4) ----------


class TestLLMCallAgentIdAttribution:
    """Every meeting ``complete()`` call is tagged with the speaking agent.

    Task 4.7 threads ``agent_id`` from the participant through the
    ``LLMClient`` protocol so the recording layer attributes each captured
    ``LLMCallRecord`` to its originating agent (R-3 substrate for the 4.8
    ThoughtStream).
    """

    def test_each_call_carries_the_speaking_participants_agent_id(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=2)
        participants = _make_participants()
        participant_ids = {p.agent_id for p in participants}

        _run(
            manager.run(
                meeting_id="m-agent-id",
                trigger=_default_trigger(),
                participants=participants,
            )
        )

        # The meeting drove LLM calls, and every one is attributed to a
        # participant -- never None, never a stray id.
        assert client.calls
        assert all(c.agent_id is not None for c in client.calls)
        assert all(c.agent_id in participant_ids for c in client.calls)

        # Phase-1 reports: exactly one per participant, each tagged with that
        # participant's own id (cross-checked against the speaker the prompt
        # was rendered for).
        report_calls = [c for c in client.calls if "PHASE=REPORT" in c.prompt]
        assert len(report_calls) == len(participants)
        assert {c.agent_id for c in report_calls} == participant_ids
        for call in report_calls:
            assert call.agent_id == _extract_marker(call.prompt, "agent_id=")

        # Phase-3 ballots: one per participant, the kwarg matching the voter
        # the prompt was rendered for.
        vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
        assert len(vote_calls) == len(participants)
        assert {c.agent_id for c in vote_calls} == participant_ids
        for call in vote_calls:
            assert call.agent_id == _extract_marker(call.prompt, "voter=")


# --- Phase 2: accusation rounds --------------------------------------------


class TestAccusationRounds:
    def test_round_count_controls_statement_count(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=3)
        participants = _make_participants()

        result = _run(
            manager.run(
                meeting_id="m-rc",
                trigger=_default_trigger(),
                participants=participants,
            )
        )

        # 3 participants * 3 rounds = 9 statements.
        assert len(result.transcript.statements) == 9

    def test_speaker_order_is_cyclic_rotation_starting_from_reporter(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)
        # Trigger reporter is p-2 (not the lexically-first id). True
        # round-robin rotates the sorted sequence at the reporter's
        # index: sorted=[p-1, p-2, p-3] rotated to start at p-2 ->
        # [p-2, p-3, p-1]. NOT "reporter then ascending others"
        # (which would be [p-2, p-1, p-3]).
        trigger = MeetingTrigger(
            triggered_by="p-2",
            trigger_tick=410,
            description="p-2 reported",
        )

        result = _run(
            manager.run(
                meeting_id="m-order",
                trigger=trigger,
                participants=_make_participants(),
            )
        )

        speakers = [s.speaker for s in result.transcript.statements]
        assert speakers == ["p-2", "p-3", "p-1"]

    def test_speaker_order_cyclic_wraparound_from_last_id(self) -> None:
        # If the reporter is the lexically-last id, the rotation must
        # wrap around to the front of the sorted sequence. Pins the
        # "cyclic" semantics directly.
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)
        trigger = MeetingTrigger(
            triggered_by="p-3",
            trigger_tick=410,
            description="p-3 reported",
        )

        result = _run(
            manager.run(
                meeting_id="m-wrap",
                trigger=trigger,
                participants=_make_participants(),
            )
        )

        speakers = [s.speaker for s in result.transcript.statements]
        assert speakers == ["p-3", "p-1", "p-2"]

    def test_non_participant_reporter_is_rejected_at_meeting_entry(
        self,
    ) -> None:
        # Codex P2: a trigger whose ``triggered_by`` is not in the
        # living participant set is an upstream orchestrator bug.
        # Silently falling back to a sorted-only speaker order would
        # produce a transcript whose ordering is no longer tied to the
        # reporter -- masking the wiring error. AGENTS.md "no silent
        # fallbacks" applies; meeting entry rejects the trigger before
        # any LLM traffic is spent.
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)
        trigger = MeetingTrigger(
            triggered_by="p-99",
            trigger_tick=410,
            description="p-99 (ejected) reported",
        )

        with pytest.raises(ValueError, match="triggered_by"):
            _run(
                manager.run(
                    meeting_id="m-no-reporter",
                    trigger=trigger,
                    participants=_make_participants(),
                )
            )

        # No LLM traffic was spent before the validation raised.
        assert client.calls == []

    def test_statement_identity_fields_are_authoritative(self) -> None:
        # The LLM returns garbage statement_id, speaker, tick, and
        # round_index; the manager must override all four.
        def _liar(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=STATEMENT" in prompt:
                return Statement(
                    statement_id="liar-id",
                    speaker="ghost",
                    tick=-1,
                    round_index=999,
                    target=None,
                    claims=(),
                    free_text="liar",
                ).model_dump_json()
            return _make_responder()(prompt, schema)

        client = _ScriptedLLMClient(responder=_liar)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-id",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        for statement in result.transcript.statements:
            assert statement.statement_id.startswith("m-id:r0:")
            assert statement.speaker in {"p-1", "p-2", "p-3"}
            assert statement.tick == 410
            assert statement.round_index == 0

    def test_missed_statement_deadline_records_default(self) -> None:
        async def _slow_responder(prompt: str) -> str:  # noqa: ARG001
            await asyncio.sleep(1.0)
            return _stub_statement_json(speaker="never", round_index=0)

        class _SleepingClient:
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
                if "PHASE=STATEMENT" in prompt:
                    text = await _slow_responder(prompt)
                else:
                    text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="sleeping",
                )

        manager = MeetingManager(
            llm_client=_SleepingClient(),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(
                round_count=1,
                deadlines=MeetingDeadlines(
                    report_seconds=None,
                    statement_seconds=0.01,
                    vote_seconds=None,
                ),
            ),
        )

        result = _run(
            manager.run(
                meeting_id="m-stmt-deadline",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        for statement in result.transcript.statements:
            assert statement.free_text == DEFAULT_STATEMENT_FREE_TEXT
            assert statement.target is None
            assert statement.claims == ()


# --- Phase 3 + 4: voting and resolution ------------------------------------


class TestVotingAndResolution:
    def test_skip_when_all_participants_skip(self) -> None:
        responder = _make_responder()  # default: all SKIP
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-skip",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None
        assert len(result.ballots) == 3

    def test_eject_on_plurality(self) -> None:
        # p-1 and p-2 both vote for p-3 (impostor); p-3 votes SKIP.
        responder = _make_responder(
            vote_targets={"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP"}
        )
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-eject",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"

    def test_tied_non_skip_targets_resolve_to_skipped(self) -> None:
        # p-1 -> p-2, p-2 -> p-1, p-3 -> SKIP. With SKIP counted as a
        # tally target, the leaders are sorted=[SKIP, p-1, p-2] all at
        # 1 vote -- SKIP is in leaders so the meeting resolves to
        # SKIPPED. DESIGN.md §5.1 + §5.2 only define ejection or
        # skip; the previously-returned ``TIE`` outcome was removed in
        # response to codex review.
        responder = _make_responder(
            vote_targets={"p-1": "p-2", "p-2": "p-1", "p-3": "SKIP"}
        )
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-tie",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None

    def test_skip_plurality_skips_even_with_one_non_skip_vote(self) -> None:
        # Codex P1 + P3 scenario: 2 SKIPs + 1 non-SKIP vote should
        # resolve to SKIPPED. The previous tally dropped SKIPs and
        # would have ejected the single non-SKIP target -- forcing
        # a low-evidence elimination that the protocol says should
        # skip.
        responder = _make_responder(
            vote_targets={"p-1": "SKIP", "p-2": "SKIP", "p-3": "p-2"}
        )
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-skip-plurality",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None

    def test_non_skip_target_with_strict_plurality_still_ejects(self) -> None:
        # Regression: with SKIP counted, a real plurality still
        # ejects. 2 votes for p-3 vs 1 SKIP -> p-3 leads -> EJECTED.
        responder = _make_responder(
            vote_targets={"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP"}
        )
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-strict-plurality",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"

    def test_skip_tied_with_player_resolves_to_skipped(self) -> None:
        # Edge case for the SKIP-in-leaders rule. With p-1->p-3 and
        # p-3->SKIP (p-2 missing here for the simplest 2-way tie),
        # the tally is {p-3: 1, SKIP: 1}; SKIP is in leaders so the
        # meeting resolves to SKIPPED -- the table did not converge.
        responder = _make_responder(vote_targets={"p-1": "p-3", "p-3": "SKIP"})
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)
        participants = (
            MeetingParticipant(agent_id="p-1", role="CREWMATE", rendered_memory="m1"),
            MeetingParticipant(agent_id="p-3", role="IMPOSTOR", rendered_memory="m3"),
        )

        result = _run(
            manager.run(
                meeting_id="m-skip-tied-with-player",
                trigger=MeetingTrigger(
                    triggered_by="p-1",
                    trigger_tick=410,
                    description="p-1 reported",
                ),
                participants=participants,
            )
        )

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None

    def test_ballot_voter_is_overridden_to_participant_id(self) -> None:
        def _liar(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=VOTE" in prompt:
                return _stub_vote_json(voter="ghost", target="SKIP")
            return _make_responder()(prompt, schema)

        client = _ScriptedLLMClient(responder=_liar)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-voter-id",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        voters = sorted(b.voter for b in result.ballots)
        assert voters == ["p-1", "p-2", "p-3"]

    def test_missed_vote_deadline_defaults_to_skip(self) -> None:
        async def _slow_responder(prompt: str) -> str:  # noqa: ARG001
            await asyncio.sleep(1.0)
            return _stub_vote_json(voter="never", target="SKIP")

        class _SleepingClient:
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
                if "PHASE=VOTE" in prompt:
                    text = await _slow_responder(prompt)
                else:
                    text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="sleeping",
                )

        manager = MeetingManager(
            llm_client=_SleepingClient(),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(
                round_count=1,
                deadlines=MeetingDeadlines(
                    report_seconds=None,
                    statement_seconds=None,
                    vote_seconds=0.01,
                ),
            ),
        )

        result = _run(
            manager.run(
                meeting_id="m-vote-deadline",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        for ballot in result.ballots:
            assert ballot.target == "SKIP"
            assert ballot.rationale_text == DEFAULT_VOTE_RATIONALE
            assert ballot.confidence == 0.0
        assert result.outcome == "SKIPPED"


# --- Vote prompt input wiring ---------------------------------------------


class TestVotePromptInputs:
    def test_candidate_targets_exclude_voter_and_are_sorted(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)

        _run(
            manager.run(
                meeting_id="m-cands",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        vote_prompts = [c.prompt for c in client.calls if "PHASE=VOTE" in c.prompt]
        # Three voters -> three prompts. Each must list the other two
        # participants as candidate targets in ascending order.
        candidate_lines = {
            _extract_marker(p, "voter="): _extract_marker(p, "candidates=")
            for p in vote_prompts
        }
        assert candidate_lines == {
            "p-1": "p-2,p-3",
            "p-2": "p-1,p-3",
            "p-3": "p-1,p-2",
        }

    def test_suspicion_graph_is_surfaced_to_prompt(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)

        _run(
            manager.run(
                meeting_id="m-sus",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        vote_prompts = [c.prompt for c in client.calls if "PHASE=VOTE" in c.prompt]
        p1_prompt = next(p for p in vote_prompts if "voter=p-1" in p)
        # p-1's suspicion graph carries one entry: p-2 with
        # suspicion=0.4, trust=0.5.
        assert "p-2:0.40/0.50" in p1_prompt


# --- C-3 statement-ordering pin --------------------------------------------


class TestStatementOrderingContract:
    """C-3 pin (option a) per ``audits/audit-2026-05-16-0611-claude.md``.

    Drives :class:`MeetingManager` through two accusation rounds with
    three participants and asserts the returned
    :class:`MeetingTranscript` is canonically ordered:

    * all round-0 statements appear before any round-1 statement;
    * within each round, the speaker order is the reporter first then
      ascending ``agent_id``.

    The test fails against any implementation that allows ambiguous
    ordering -- e.g. asyncio.gather'd statements within a round, or
    rounds emitted in arbitrary order.
    """

    def test_two_round_transcript_is_canonically_ordered(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=2)
        # Reporter is p-2 so the round-internal order is NOT the
        # lexical id order; a wrong implementation that ignores the
        # reporter-first rule would fail this test.
        trigger = MeetingTrigger(
            triggered_by="p-2",
            trigger_tick=410,
            description="p-2 reported",
        )

        result = _run(
            manager.run(
                meeting_id="m-c3",
                trigger=trigger,
                participants=_make_participants(),
            )
        )

        statements = result.transcript.statements
        # Cross-round invariant: round_index is non-decreasing.
        round_indices = [s.round_index for s in statements]
        assert round_indices == sorted(round_indices)
        assert is_canonically_ordered(statements) is True

        # 3 participants * 2 rounds = 6 statements.
        assert len(statements) == 6

        # Insertion-order half of the contract: speaker order within a
        # round is a cyclic rotation of the sorted ids starting from
        # the reporter, and that order is the same in every round.
        # Sorted=[p-1, p-2, p-3] rotated at p-2 -> [p-2, p-3, p-1].
        round0 = [s for s in statements if s.round_index == 0]
        round1 = [s for s in statements if s.round_index == 1]
        assert [s.speaker for s in round0] == ["p-2", "p-3", "p-1"]
        assert [s.speaker for s in round1] == ["p-2", "p-3", "p-1"]

        # The tuple order must literally be round0 first then round1
        # -- a sort that interleaves rounds (e.g. by speaker) would
        # still produce non-decreasing round_index per speaker but
        # would break the round-grouping invariant.
        assert statements[:3] == tuple(round0)
        assert statements[3:] == tuple(round1)

    def test_pin_would_fail_against_speaker_grouped_interleaving(self) -> None:
        # This is the explicit "fail against ambiguous ordering"
        # gate. We construct what an *incorrect* manager output would
        # look like (statements grouped by speaker instead of by
        # round) and assert the C-3 invariants reject it.
        bad_statements = (
            Statement(
                statement_id="m-c3:r0:p-2",
                speaker="p-2",
                tick=410,
                round_index=0,
                target=None,
                claims=(),
                free_text="r0 p-2",
            ),
            Statement(
                statement_id="m-c3:r1:p-2",
                speaker="p-2",
                tick=410,
                round_index=1,
                target=None,
                claims=(),
                free_text="r1 p-2",
            ),
            Statement(
                statement_id="m-c3:r0:p-1",
                speaker="p-1",
                tick=410,
                round_index=0,
                target=None,
                claims=(),
                free_text="r0 p-1",
            ),
        )

        # The cross-round invariant must trip on the round-1 then
        # round-0 transition.
        assert is_canonically_ordered(bad_statements) is False


# --- Engine-independence ---------------------------------------------------


class TestEngineIndependence:
    def test_manager_module_does_not_import_engine(self) -> None:
        # The manager module must not import from engine/. The DoD
        # gates this via lint-imports; this test gives a fast, local
        # signal that complements the import-linter sweep.
        import meetings.manager as manager_module

        source = open(manager_module.__file__, encoding="utf-8").read()
        assert "from engine" not in source
        assert "import engine" not in source

    def test_run_returns_pure_dto(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-dto",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert isinstance(result, MeetingResult)
        # MeetingResult round-trips through Pydantic -- it carries no
        # engine references that would break serialisation.
        dumped = result.model_dump_json()
        assert MeetingResult.model_validate_json(dumped) == result


# --- Compatibility with the FakeProvider -----------------------------------


class TestFakeProviderInterop:
    """Sanity-check that the default fake provider satisfies the
    manager's LLM contract end-to-end (DoD: "tests pass using fake
    strategic participants. Use the existing llm/fake_provider.py
    plus shim participants -- no real Anthropic calls").
    """

    def test_meeting_runs_end_to_end_with_fake_provider(self) -> None:
        manager = MeetingManager(
            llm_client=FakeProvider(),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(round_count=1),
        )

        result = _run(
            manager.run(
                meeting_id="m-fake",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert len(result.transcript.reports) == 3
        assert len(result.transcript.statements) == 3
        assert len(result.ballots) == 3
        # Fake-provider responses have ascending round_index within
        # the bounds the manager imposes (override).
        for statement in result.transcript.statements:
            assert statement.round_index == 0

    def test_two_runs_with_fake_provider_are_byte_identical(self) -> None:
        # Determinism guard: same inputs + fake provider -> same
        # transcript. The fake provider is byte-deterministic by
        # design (SHA-256 of the prompt), and the manager imposes a
        # deterministic speaker order, so the result must be stable
        # across runs.
        def _produce() -> MeetingResult:
            manager = MeetingManager(
                llm_client=FakeProvider(),
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(round_count=1),
            )
            return _run(
                manager.run(
                    meeting_id="m-det",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )

        first = _produce()
        second = _produce()
        assert first == second


# --- Contradiction-free transcript wiring ---------------------------------


class TestContradictionsWiring:
    """Task 6.4 (audit J-J-1): the manager runs ``detect_contradictions``
    over the transcript-so-far and threads the live tuple into the
    statement prompts, the ballot prompts, and the persisted result.

    A claim-free transcript still yields no flags, so the no-contradiction
    path is pinned alongside the populated path to catch any future change
    that injects spurious flags.
    """

    def test_claim_free_transcript_carries_no_contradictions(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-contradictions",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.contradictions == ()
        statement_prompts = [
            c.prompt for c in client.calls if "PHASE=STATEMENT" in c.prompt
        ]
        for prompt in statement_prompts:
            assert "CONTRADICTIONS_COUNT=0" in prompt
        vote_prompts = [c.prompt for c in client.calls if "PHASE=VOTE" in c.prompt]
        for prompt in vote_prompts:
            assert "FLAGS_COUNT=0" in prompt

    def test_detected_contradiction_is_threaded_into_prompts_and_result(self) -> None:
        # Two reports place p-3 in different rooms over overlapping tick
        # ranges -> one alibi_conflict flag. The manager must compute it
        # from the transcript-so-far and thread it into the second-round
        # statement prompts, the ballot prompts, and the persisted result.
        client = _ScriptedLLMClient(
            responder=_make_contradiction_responder(subject="p-3")
        )
        manager = _make_manager(llm_client=client, round_count=2)

        result = _run(
            manager.run(
                meeting_id="m-live-contradiction",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert len(result.contradictions) >= 1
        assert all(
            flag.kind in ("alibi_conflict", "alibi_vs_sighting")
            for flag in result.contradictions
        )
        assert any("p-3" in flag.subjects for flag in result.contradictions)

        # Round 0 sees no flags (no statements/reports indexed yet at the
        # time the round-0 detector runs over the reports). The reports DO
        # already conflict, so the first detector pass — before round 0 —
        # already surfaces the flag; every statement prompt therefore sees
        # a non-zero count.
        statement_counts = [
            int(_extract_marker(c.prompt, "CONTRADICTIONS_COUNT="))
            for c in client.calls
            if "PHASE=STATEMENT" in c.prompt
        ]
        assert max(statement_counts) >= 1

        vote_flag_counts = [
            int(_extract_marker(c.prompt, "FLAGS_COUNT="))
            for c in client.calls
            if "PHASE=VOTE" in c.prompt
        ]
        assert vote_flag_counts and all(count >= 1 for count in vote_flag_counts)

    def test_contradiction_shifts_vote_suspicion_graph(self) -> None:
        # Belief Rule 2 (audit J-J-4): a detected contradiction naming p-3
        # must lift p-3's suspicion in every voter's rendered suspicion
        # graph relative to its incoming prior. p-1's incoming graph has
        # p-2 at 0.40 and no p-3 row; after the rule p-3 appears at
        # 0.5 (default prior) + 0.3 (Rule 2 delta) = 0.8.
        client = _ScriptedLLMClient(
            responder=_make_contradiction_responder(subject="p-3")
        )
        manager = _make_manager(llm_client=client, round_count=1)

        _run(
            manager.run(
                meeting_id="m-rule2",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # p-1's incoming graph had p-2 at 0.40 and no p-3 row. After Rule 2,
        # p-3 appears in p-1's graph at an elevated suspicion (default 0.50
        # prior + one or more +0.3 Rule-2 bumps, clamped to <= 1.0), strictly
        # above the unflagged default. p-2 (unflagged) stays at its prior.
        p1_block = next(
            _extract_marker(c.prompt, "suspicion=")
            for c in client.calls
            if "PHASE=VOTE" in c.prompt and "voter=p-1" in c.prompt
        )
        p3_scores = {
            entry.split(":")[0]: float(entry.split(":")[1].split("/")[0])
            for entry in p1_block.split(",")
            if entry
        }
        assert "p-3" in p3_scores
        assert p3_scores["p-3"] > _DEFAULT_TEST_SUSPICION
        # The voter never accrues suspicion about themselves.
        p3_block = next(
            _extract_marker(c.prompt, "suspicion=")
            for c in client.calls
            if "PHASE=VOTE" in c.prompt and "voter=p-3" in c.prompt
        )
        assert "p-3:" not in p3_block


# --- Statement prompt receives transcript-so-far ---------------------------


class TestStatementPromptInputs:
    def test_each_round_sees_accumulated_transcript(self) -> None:
        # The transcript-so-far passed to each statement prompt must
        # grow monotonically as participants speak. This is the
        # mechanical pin that says "round-robin statements feed each
        # other's transcript view, not just round-N's prior round".
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=2)

        _run(
            manager.run(
                meeting_id="m-cumulative",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        statement_prompts = [
            c.prompt for c in client.calls if "PHASE=STATEMENT" in c.prompt
        ]
        # 3 participants * 2 rounds = 6 statement prompts. The first
        # statement sees 0 prior statements; the last sees 5.
        expected_statements_counts = [0, 1, 2, 3, 4, 5]
        actual = [
            int(_extract_marker(prompt, "STATEMENTS_COUNT="))
            for prompt in statement_prompts
        ]
        assert actual == expected_statements_counts

    def test_every_statement_prompt_sees_all_reports(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=2)

        _run(
            manager.run(
                meeting_id="m-reports-visible",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        statement_prompts = [
            c.prompt for c in client.calls if "PHASE=STATEMENT" in c.prompt
        ]
        for prompt in statement_prompts:
            assert "REPORTS_COUNT=3" in prompt


# --- Codex P1 + P2 review feedback pins -----------------------------------


class TestNegativeDeadlinesRejected:
    """Codex P2: negative per-phase deadlines must fail-loud at config time.

    Without this check, a misconfigured deadline (e.g. ``-1.0``) would
    reach :func:`asyncio.wait_for`, immediately raise ``TimeoutError``,
    and silently default every report / statement / vote to the
    no-response branch -- a configuration error masquerading as a real
    meeting outcome.
    """

    def test_negative_report_deadline_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        with pytest.raises(ValueError, match="report_seconds"):
            MeetingManager(
                llm_client=client,
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(deadlines=MeetingDeadlines(report_seconds=-1.0)),
            )

    def test_negative_statement_deadline_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        with pytest.raises(ValueError, match="statement_seconds"):
            MeetingManager(
                llm_client=client,
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(
                    deadlines=MeetingDeadlines(statement_seconds=-0.5)
                ),
            )

    def test_negative_vote_deadline_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        with pytest.raises(ValueError, match="vote_seconds"):
            MeetingManager(
                llm_client=client,
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(deadlines=MeetingDeadlines(vote_seconds=-10.0)),
            )

    def test_zero_deadline_is_rejected(self) -> None:
        # A deadline of exactly 0 is also a misconfiguration: it
        # ensures every call times out before the LLM can respond.
        client = _ScriptedLLMClient(responder=_make_responder())
        with pytest.raises(ValueError, match="report_seconds"):
            MeetingManager(
                llm_client=client,
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(deadlines=MeetingDeadlines(report_seconds=0.0)),
            )

    def test_none_deadline_is_accepted_for_headless_mode(self) -> None:
        # ``None`` opts out of the deadline entirely (DESIGN.md §1.4
        # headless mode). Construction must not raise.
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = MeetingManager(
            llm_client=client,
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(
                deadlines=MeetingDeadlines(
                    report_seconds=None,
                    statement_seconds=None,
                    vote_seconds=None,
                )
            ),
        )
        assert isinstance(manager, MeetingManager)


class TestUnknownRoleRejected:
    """Codex P2: unknown participant roles must fail-loud at entry.

    Without this check, any role string other than ``"IMPOSTOR"``
    silently falls through to the crewmate prompt path in
    ``_collect_one_report`` -- a typo like ``"impostor"`` would be
    treated as a crewmate without any error signal.
    """

    def test_typo_role_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)
        # Bypass the ``Role`` Literal at the call site by going through
        # a `cast`-like dict; the dataclass accepts the wrong string
        # at runtime so the manager must catch it.
        bad_participants = (
            MeetingParticipant(
                agent_id="p-1",
                role="impostor",  # type: ignore[arg-type]
                rendered_memory="memory",
            ),
        )

        with pytest.raises(ValueError, match="MeetingParticipant.role"):
            _run(
                manager.run(
                    meeting_id="m-typo",
                    trigger=_default_trigger(),
                    participants=bad_participants,
                )
            )

    def test_unknown_role_string_is_rejected(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)
        bad_participants = (
            MeetingParticipant(
                agent_id="p-1",
                role="GHOST",  # type: ignore[arg-type]
                rendered_memory="memory",
            ),
        )

        with pytest.raises(ValueError, match="GHOST"):
            _run(
                manager.run(
                    meeting_id="m-ghost",
                    trigger=_default_trigger(),
                    participants=bad_participants,
                )
            )


class TestParticipantOrderCanonicalised:
    """Codex P1: meeting must be deterministic regardless of caller order.

    Real callers (orchestrator, eval harness) may build the participant
    list from a ``set``, ``dict.values()``, or another container whose
    iteration order is not seed-stable. Without canonicalisation, the
    transcript embedded into every statement prompt would change byte
    content between runs with the same seed, breaking the
    determinism contract.
    """

    def test_meeting_outcome_is_independent_of_input_order(self) -> None:
        # Two runs with the same trigger and participants but different
        # input order must produce equal MeetingResults.
        responder = _make_responder(
            vote_targets={"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP"}
        )

        def _produce(participants: tuple[MeetingParticipant, ...]) -> MeetingResult:
            client = _ScriptedLLMClient(responder=responder)
            manager = _make_manager(llm_client=client, round_count=2)
            return _run(
                manager.run(
                    meeting_id="m-order-indep",
                    trigger=_default_trigger(),
                    participants=participants,
                )
            )

        sorted_participants = _make_participants()
        reverse_participants = tuple(reversed(sorted_participants))

        sorted_result = _produce(sorted_participants)
        reverse_result = _produce(reverse_participants)

        # Reports, statements, ballots, contradictions, and outcome
        # are all byte-identical between the two runs.
        assert sorted_result == reverse_result

    def test_reports_are_in_canonical_order_regardless_of_input(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)
        # Pass participants in reverse-lexical order; the manager must
        # rebuild them in ascending agent_id order before phase 1.
        reverse_participants = tuple(reversed(_make_participants()))

        result = _run(
            manager.run(
                meeting_id="m-canon-reports",
                trigger=_default_trigger(),
                participants=reverse_participants,
            )
        )

        assert [r.agent_id for r in result.transcript.reports] == [
            "p-1",
            "p-2",
            "p-3",
        ]

    def test_ballots_are_in_canonical_order_regardless_of_input(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client, round_count=1)
        reverse_participants = tuple(reversed(_make_participants()))

        result = _run(
            manager.run(
                meeting_id="m-canon-ballots",
                trigger=_default_trigger(),
                participants=reverse_participants,
            )
        )

        assert [b.voter for b in result.ballots] == ["p-1", "p-2", "p-3"]


class TestInvalidBallotTargetNormalised:
    """Codex P1: hallucinated or stale eject targets must not corrupt the tally.

    If the LLM returns a ``target`` that is neither ``"SKIP"`` nor in
    the voter's ``candidate_targets``, the manager normalises the
    ballot to ``SKIP`` and marks ``rationale_text`` so the audit trail
    preserves the original (invalid) target. Without this, ``_tally``
    would count the bogus id as a real vote and could resolve to
    ``EJECTED`` against a non-participant -- corrupting outcome
    application and replay.
    """

    def test_hallucinated_target_is_normalised_to_skip(self) -> None:
        # Every voter returns target="ghost" (not a participant).
        def _ghost_responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=VOTE" in prompt:
                voter = _extract_marker(prompt, "voter=")
                return VoteBallot(
                    voter=voter,
                    target="ghost",
                    confidence=0.9,
                    primary_reason_id=None,
                    considered_alternatives=(),
                    rationale_text="ghost did it",
                ).model_dump_json()
            return _make_responder()(prompt, schema)

        client = _ScriptedLLMClient(responder=_ghost_responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-ghost-target",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # Tally must NOT have counted "ghost" as an eject -- every
        # ballot was normalised to SKIP, so the outcome is SKIPPED
        # and no non-participant is ejected.
        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None
        for ballot in result.ballots:
            assert ballot.target == "SKIP"
            assert ballot.rationale_text.startswith(
                INVALID_VOTE_TARGET_MARKER.format(target="ghost")
            )
            # The original rationale is preserved after the marker.
            assert "ghost did it" in ballot.rationale_text

    def test_voter_voting_for_self_is_normalised_to_skip(self) -> None:
        # Voting for oneself is excluded from candidate_targets; it is
        # treated the same as a hallucinated id and normalised to SKIP.
        def _self_responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=VOTE" in prompt:
                voter = _extract_marker(prompt, "voter=")
                return VoteBallot(
                    voter=voter,
                    target=voter,  # voting for self
                    confidence=0.5,
                    primary_reason_id=None,
                    considered_alternatives=(),
                    rationale_text="meta vote",
                ).model_dump_json()
            return _make_responder()(prompt, schema)

        client = _ScriptedLLMClient(responder=_self_responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-self-vote",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        for ballot in result.ballots:
            assert ballot.target == "SKIP"
            marker = INVALID_VOTE_TARGET_MARKER.format(target=ballot.voter)
            assert ballot.rationale_text.startswith(marker)

    def test_valid_target_passes_through_unchanged(self) -> None:
        # Regression: a ballot with a real candidate target must NOT
        # be modified.
        responder = _make_responder(
            vote_targets={"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP"}
        )
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-valid-target",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        ballots_by_voter = {b.voter: b for b in result.ballots}
        assert ballots_by_voter["p-1"].target == "p-3"
        assert ballots_by_voter["p-2"].target == "p-3"
        assert ballots_by_voter["p-3"].target == "SKIP"
        for ballot in result.ballots:
            assert not ballot.rationale_text.startswith("[invalid target")
        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"


class TestConfidenceThresholdEnforcement:
    """Codex P1: ``_tally`` mechanically enforces ``skip_confidence_threshold``.

    DESIGN.md §5.2 PHASE 4: "If a player has plurality and meets
    threshold, eject. If tie or below threshold, skip." DESIGN.md
    §4.6: "the default voting heuristic does not vote-eject if max
    suspicion confidence < 0.6; instead it skips".

    The vote prompt already instructs the LLM to ``SKIP`` when
    confidence is below the threshold (decision rule 1 in
    ``vote_ballot.j2``). The mechanical check below is the
    fail-loud backstop: protocol behavior is deterministic even
    when the LLM fails to follow the prompt instruction. The check
    uses the *max* of the plurality target's ballot confidences,
    matching §4.6 ("max suspicion confidence") -- the eject
    requires at least one voter to be confident, not all of them.
    """

    @staticmethod
    def _low_confidence_responder() -> Callable[[str, type[BaseModel] | None], str]:
        # Every non-SKIP voter votes for p-3 with confidence below
        # the default threshold (0.6); p-3 itself SKIPs. Without the
        # threshold check the tally would eject on plurality alone.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=VOTE" in prompt:
                voter = _extract_marker(prompt, "voter=")
                if voter == "p-3":
                    return _stub_vote_json(voter=voter, target="SKIP")
                return _stub_vote_json(voter=voter, target="p-3", confidence=0.4)
            return _make_responder()(prompt, schema)

        return _responder

    def test_low_confidence_plurality_skips_not_ejects(self) -> None:
        # Two non-SKIP voters both pick p-3 with confidence=0.4
        # (below the default threshold of 0.6). Without the threshold
        # check, the tally would return EJECTED p-3 -- a low-evidence
        # ejection the protocol says should resolve to SKIP.
        client = _ScriptedLLMClient(responder=self._low_confidence_responder())
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-low-conf",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None
        # Confidence levels in the recorded ballots match what the
        # LLM produced (the manager does not rewrite them; the tally
        # just refuses to eject).
        targets = [b.target for b in result.ballots]
        assert targets.count("p-3") == 2

    def test_max_confidence_above_threshold_does_eject(self) -> None:
        # Two voters pick p-3: one at the threshold (0.6) and one
        # well below it (0.2). Because *max* across the plurality
        # target's ballots is >= threshold (per §4.6), the eject
        # proceeds even though the other ballot is low-confidence.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=VOTE" in prompt:
                voter = _extract_marker(prompt, "voter=")
                if voter == "p-1":
                    return _stub_vote_json(voter=voter, target="p-3", confidence=0.2)
                if voter == "p-2":
                    return _stub_vote_json(voter=voter, target="p-3", confidence=0.6)
                return _stub_vote_json(voter=voter, target="SKIP")
            return _make_responder()(prompt, schema)

        client = _ScriptedLLMClient(responder=_responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-max-conf",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"

    def test_threshold_is_inclusive_at_exactly_the_cutoff(self) -> None:
        # confidence == threshold must allow ejection -- the rule is
        # "below threshold, skip", so the threshold itself is the
        # eject side.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=VOTE" in prompt:
                voter = _extract_marker(prompt, "voter=")
                if voter in {"p-1", "p-2"}:
                    return _stub_vote_json(voter=voter, target="p-3", confidence=0.6)
                return _stub_vote_json(voter=voter, target="SKIP")
            return _make_responder()(prompt, schema)

        client = _ScriptedLLMClient(responder=_responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-cutoff",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"

    def test_configurable_threshold_is_respected(self) -> None:
        # Override the default threshold to 0.9 via MeetingConfig;
        # ballots at 0.8 (which would normally eject) must now skip.
        responder = _make_responder(
            vote_targets={"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP"}
        )
        client = _ScriptedLLMClient(responder=responder)
        manager = MeetingManager(
            llm_client=client,
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(round_count=1, skip_confidence_threshold=0.9),
        )

        result = _run(
            manager.run(
                meeting_id="m-high-threshold",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # Default stub confidence is 0.8, which is below the
        # configured 0.9 threshold -- so even with a clean plurality
        # the tally must skip.
        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None

    def test_threshold_does_not_apply_when_skip_wins(self) -> None:
        # Even with the threshold check in place, SKIP-as-leader
        # short-circuits to SKIPPED before the threshold logic runs.
        # This documents the resolution-rule ordering in ``_tally``.
        responder = _make_responder(
            vote_targets={"p-1": "SKIP", "p-2": "SKIP", "p-3": "SKIP"}
        )
        client = _ScriptedLLMClient(responder=responder)
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-skip-wins",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None


class TestProviderTimeoutDistinctFromDeadline:
    """Codex P1: provider timeouts must not silently become defaults.

    In Python 3.11+, :class:`asyncio.TimeoutError` is the same class
    as :class:`TimeoutError`. The manager's deadline handler used to
    catch the unified type and would coerce *any* ``TimeoutError`` --
    including transport / provider failures from the SDK -- into a
    default no-report / no-statement / default-skip entry. The fix
    wraps the LLM call with :func:`_isolate_provider_timeout` which
    re-tags inner timeouts as :class:`LLMProviderError`; only true
    deadline expiry from :func:`asyncio.wait_for` reaches the
    handler.
    """

    @dataclass
    class _ProviderTimeoutClient:
        """LLM client that always raises ``TimeoutError`` from inside.

        Mimics a transport / SDK timeout. With the prior code this
        would be indistinguishable from a meeting-deadline expiry and
        would silently produce a default response.
        """

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
            raise TimeoutError("simulated provider timeout")

    def test_provider_timeout_in_report_phase_propagates_as_llm_provider_error(
        self,
    ) -> None:
        manager = MeetingManager(
            llm_client=self._ProviderTimeoutClient(),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(round_count=1),
        )

        # Should NOT silently default. The provider error must
        # propagate so the orchestrator can decide how to handle the
        # infrastructure failure.
        with pytest.raises(LLMProviderError):
            _run(
                manager.run(
                    meeting_id="m-provider-timeout-report",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )

    def test_provider_timeout_in_statement_phase_propagates(self) -> None:
        # Reports succeed; statements raise provider timeout. We use
        # a client that succeeds on the report schema and raises on
        # the statement schema so the meeting reaches phase 2 before
        # failing.
        @dataclass
        class _PhaseSpecificClient:
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
                if schema is not None and schema.__name__ == "Statement":
                    raise TimeoutError("simulated provider timeout")
                # Reports + ballots succeed via the normal responder.
                text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="phase-specific",
                )

        manager = MeetingManager(
            llm_client=_PhaseSpecificClient(),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(round_count=1),
        )

        with pytest.raises(LLMProviderError):
            _run(
                manager.run(
                    meeting_id="m-provider-timeout-statement",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )

    def test_provider_timeout_in_vote_phase_propagates(self) -> None:
        @dataclass
        class _PhaseSpecificClient:
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
                if schema is not None and schema.__name__ == "VoteBallot":
                    raise TimeoutError("simulated provider timeout")
                text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="phase-specific",
                )

        manager = MeetingManager(
            llm_client=_PhaseSpecificClient(),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(round_count=1),
        )

        with pytest.raises(LLMProviderError):
            _run(
                manager.run(
                    meeting_id="m-provider-timeout-vote",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )

    def test_meeting_deadline_still_defaults_when_inner_does_not_raise(
        self,
    ) -> None:
        # Regression: the legitimate deadline-expiry path (LLM is just
        # slow, deadline trips) must still produce the default
        # response. We re-use the sleeping client pattern from the
        # earlier deadline tests but only sleep for the report phase.
        async def _slow_responder(prompt: str) -> str:  # noqa: ARG001
            await asyncio.sleep(1.0)
            return _stub_report_json(agent_id="never", tick=0)

        @dataclass
        class _SleepingClient:
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
                if "PHASE=REPORT" in prompt:
                    text = await _slow_responder(prompt)
                else:
                    text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="sleeping",
                )

        manager = MeetingManager(
            llm_client=_SleepingClient(),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
            config=MeetingConfig(
                round_count=1,
                deadlines=MeetingDeadlines(
                    report_seconds=0.01,
                    statement_seconds=None,
                    vote_seconds=None,
                ),
            ),
        )

        result = _run(
            manager.run(
                meeting_id="m-real-deadline",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # No raise: the deadline branch is still reachable and still
        # produces default reports.
        for report in result.transcript.reports:
            assert report.free_text == DEFAULT_REPORT_FREE_TEXT


class TestSequentialPhaseShortCircuitsOnFailure:
    """A failing phase call stops sequential collection before the rest.

    Report and ballot collection run sequentially -- one LLM call at a
    time -- because a local single-GPU provider gets no speedup from
    concurrency and concurrent calls bust their own per-call deadlines
    (see ``MeetingManager._collect_reports``). So when one participant's
    call raises, the error propagates out of the phase loop and the
    participants ordered after it are never called: the meeting fails and
    no work is spent on calls past the failure. These tests pin that
    contract for the two phases that were previously collected in parallel.
    """

    def test_failing_report_short_circuits_later_reports(self) -> None:
        # p-2 is the 2nd of three participants; its report call raises.
        client = _SequentialFailureClient(failing_voter="p-2", target_phase="REPORT")
        manager = _make_manager(llm_client=client, round_count=1)

        with pytest.raises(RuntimeError, match="simulated"):
            _run(
                manager.run(
                    meeting_id="m-fail-report",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )

        # p-1's report ran and p-2's raised, so the loop stopped before
        # p-3: exactly two report calls started, the third never attempted.
        assert client.started_calls == 2

    def test_failing_ballot_short_circuits_later_ballots(self) -> None:
        client = _SequentialFailureClient(failing_voter="p-2", target_phase="VOTE")
        manager = _make_manager(llm_client=client, round_count=1)

        with pytest.raises(RuntimeError, match="simulated"):
            _run(
                manager.run(
                    meeting_id="m-fail-vote",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )

        # Reports + statements completed; voting started p-1 then p-2
        # (which raised) and never reached p-3.
        vote_starts = [call for call in client.recorded_calls if "PHASE=VOTE" in call]
        assert len(vote_starts) == 2


@dataclass
class _SequentialFailureClient:
    """Helper LLM client for the sequential short-circuit tests.

    * Calls whose prompt does NOT match ``target_phase`` respond normally
      (via the standard responder) so the meeting reaches the target phase.
    * Within the target phase, the failing voter's call raises
      :class:`RuntimeError`; every other call also responds normally. With
      sequential collection the failure propagates out of the phase loop,
      so participants ordered after the failing one are never called.
    """

    failing_voter: str
    target_phase: str
    started_calls: int = 0
    recorded_calls: list[str] = field(default_factory=list)

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
        self.recorded_calls.append(prompt)
        if f"PHASE={self.target_phase}" in prompt:
            self.started_calls += 1
            # Failing voter id appears as voter= (vote) or agent_id= (report).
            is_failing = (
                f"voter={self.failing_voter}" in prompt
                or f"agent_id={self.failing_voter}" in prompt
            )
            if is_failing:
                raise RuntimeError("simulated phase failure")
        text = _make_responder()(prompt, schema)
        if schema is not None:
            schema.model_validate_json(text)
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model="sequential-failure-test",
        )


# --- Task 3.20: self-alibi subject normalization ---------------------------


def _alibi_subjects(claims: tuple[Claim, ...]) -> list[PlayerId]:
    """Extract the ``subject`` of every ``AlibiClaim`` (order-preserving)."""

    return [claim.subject for claim in claims if isinstance(claim, AlibiClaim)]


class TestSelfAlibiSubjectNormalization:
    """`_normalize_self_alibi_subjects` (Task 3.20, DESIGN.md §5.3, §5.4).

    The normalizer rewrites the deterministic self-alibi placeholder
    subjects the model leaks ("self", "p-self", an unrendered Jinja
    placeholder) to the speaker's canonical id, and passes every other
    subject through untouched (it does NOT validate against the roster).
    """

    def test_rewrites_placeholder_variants_to_speaker_id(self) -> None:
        # Three AlibiClaims: two placeholders ("self", "p-self") and the
        # real speaker id ("p-4"). After normalization for speaker "p-4"
        # all three subjects must equal "p-4".
        report = ReportDocument(
            agent_id="p-4",
            tick=10,
            claims=(
                AlibiClaim(
                    type="alibi", subject="self", from_tick=1, to_tick=5, room="ADMIN"
                ),
                AlibiClaim(
                    type="alibi",
                    subject="p-self",
                    from_tick=2,
                    to_tick=6,
                    room="CAFETERIA",
                ),
                AlibiClaim(
                    type="alibi",
                    subject="p-4",
                    from_tick=3,
                    to_tick=7,
                    room="STORAGE",
                ),
            ),
            free_text="report",
        )

        normalized = _normalize_self_alibi_subjects(report.claims, speaker_id="p-4")

        assert _alibi_subjects(normalized) == ["p-4", "p-4", "p-4"]

    def test_passes_non_self_subjects_through_unchanged(self) -> None:
        # "p-2" (another real player) and "p-99" (a hallucination that is
        # neither in the self-placeholder set nor in the roster) must
        # both pass through unchanged: this task does not validate
        # subjects against the meeting roster.
        statement = Statement(
            statement_id="s",
            speaker="p-4",
            tick=10,
            round_index=0,
            target=None,
            claims=(
                AlibiClaim(
                    type="alibi", subject="p-2", from_tick=1, to_tick=5, room="ADMIN"
                ),
                AlibiClaim(
                    type="alibi",
                    subject="p-99",
                    from_tick=2,
                    to_tick=6,
                    room="CAFETERIA",
                ),
            ),
            free_text="statement",
        )

        normalized = _normalize_self_alibi_subjects(statement.claims, speaker_id="p-4")

        assert _alibi_subjects(normalized) == ["p-2", "p-99"]

    def test_unrendered_jinja_placeholder_is_rewritten(self) -> None:
        claims: tuple[Claim, ...] = (
            AlibiClaim(
                type="alibi",
                subject="{{ agent_id }}",
                from_tick=1,
                to_tick=5,
                room="ADMIN",
            ),
        )

        normalized = _normalize_self_alibi_subjects(claims, speaker_id="p-4")

        assert _alibi_subjects(normalized) == ["p-4"]

    def test_non_alibi_claims_pass_through_untouched(self) -> None:
        # Only AlibiClaims are inspected; accusation / corroboration
        # claims are returned as-is even when an alibi is rewritten.
        claims: tuple[Claim, ...] = (
            AccusationClaim(
                type="accusation", against="p-2", confidence=0.5, reason="near body"
            ),
            AlibiClaim(
                type="alibi", subject="self", from_tick=1, to_tick=5, room="ADMIN"
            ),
        )

        normalized = _normalize_self_alibi_subjects(claims, speaker_id="p-4")

        accusation = normalized[0]
        assert isinstance(accusation, AccusationClaim)
        assert accusation.against == "p-2"
        assert _alibi_subjects(normalized) == ["p-4"]

    def test_empty_claims_returns_empty_tuple(self) -> None:
        assert _normalize_self_alibi_subjects((), speaker_id="p-4") == ()


class TestRosterAwareContradictionMatching:
    """Roster-aware subject matching in the live meeting path (J-J-9).

    A non-roster subject (e.g. a hallucinated ``p-99``) is dropped
    deterministically by ``detect_contradictions(roster=...)`` rather
    than silently surviving into a half-matched flag, while a roster
    subject is still matched. Self-placeholders are normalised to the
    speaker (an in-roster id) before the detector runs, so a normalised
    self-alibi remains matchable.
    """

    def test_non_roster_subject_conflict_is_dropped(self) -> None:
        # Every reporter plants a conflicting alibi for "p-99", which is
        # NOT a living participant. The roster filter must drop it so the
        # persisted result and the rendered prompts carry zero flags.
        client = _ScriptedLLMClient(
            responder=_make_contradiction_responder(subject="p-99")
        )
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-nonroster",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.contradictions == ()
        vote_flag_counts = [
            int(_extract_marker(c.prompt, "FLAGS_COUNT="))
            for c in client.calls
            if "PHASE=VOTE" in c.prompt
        ]
        assert vote_flag_counts and all(count == 0 for count in vote_flag_counts)

    def test_roster_subject_conflict_is_kept(self) -> None:
        # The same conflict shape, but the subject "p-3" IS a living
        # participant: the flag must survive the roster filter. This is
        # the positive control for the drop test above.
        client = _ScriptedLLMClient(
            responder=_make_contradiction_responder(subject="p-3")
        )
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-roster",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert len(result.contradictions) >= 1
        assert any("p-3" in flag.subjects for flag in result.contradictions)


class TestSelfAlibiNormalizationWiring:
    """The normalizer is invoked on both meeting parse paths (Task 3.20).

    A scripted provider emits a self-alibi placeholder subject in every
    report ("self") and every statement ("p-self"); after the meeting
    the persisted transcript must carry the speaker's canonical id, not
    the placeholder.
    """

    @staticmethod
    def _placeholder_responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=REPORT" in prompt:
            agent_id = _extract_marker(prompt, "agent_id=")
            return ReportDocument(
                agent_id=agent_id,
                tick=0,
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="self",
                        from_tick=1,
                        to_tick=2,
                        room="ADMIN",
                    ),
                ),
                free_text=f"report-{agent_id}",
            ).model_dump_json()
        if "PHASE=STATEMENT" in prompt:
            return Statement(
                statement_id="ignored",
                speaker="ignored",
                tick=0,
                round_index=0,
                target=None,
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="p-self",
                        from_tick=1,
                        to_tick=2,
                        room="ADMIN",
                    ),
                ),
                free_text="statement",
            ).model_dump_json()
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            return _stub_vote_json(voter=voter, target="SKIP")
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    def test_report_and_statement_self_alibis_are_canonicalized(self) -> None:
        client = _ScriptedLLMClient(responder=self._placeholder_responder)
        manager = _make_manager(llm_client=client)

        result = _run(
            manager.run(
                meeting_id="m-normalize",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # Report path (`_collect_one_report`): every report's self-alibi
        # "self" placeholder is rewritten to the report's own agent_id.
        for report in result.transcript.reports:
            subjects = _alibi_subjects(report.claims)
            assert subjects, "expected a self-alibi on every report"
            assert all(subject == report.agent_id for subject in subjects)

        # Statement path (`_collect_statement`): every statement's
        # "p-self" placeholder is rewritten to the statement's speaker.
        for statement in result.transcript.statements:
            subjects = _alibi_subjects(statement.claims)
            assert subjects, "expected a self-alibi on every statement"
            assert all(subject == statement.speaker for subject in subjects)

        # And no placeholder token survives anywhere in the transcript.
        dumped = result.transcript.model_dump_json()
        assert '"subject":"self"' not in dumped
        assert '"subject":"p-self"' not in dumped


class TestAccusationRoundPromptVersionInReplay:
    """The bumped accusation_round version reaches the replay record.

    Task 3.20 bumps the template header to v2; the orchestrator's
    `DEFAULT_PROMPT_VERSIONS` map (copied verbatim into every
    `MeetingReplayEntry`) must carry "accusation_round.v2".
    """

    def test_meeting_replay_entry_shows_accusation_round_v2(self) -> None:
        from orchestrator.game import DEFAULT_PROMPT_VERSIONS
        from orchestrator.replay import MeetingReplayEntry

        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)
        result = _run(
            manager.run(
                meeting_id="m-version",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # Build the replay entry exactly as
        # `orchestrator.replay.ReplayWriter.record_meeting` does: the
        # prompt-version map flows in verbatim from the production
        # default. A fresh entry must show the bumped v2 string.
        entry = MeetingReplayEntry(
            game_id="g-version",
            meeting_id=result.meeting_id,
            tick=result.trigger_tick,
            triggered_by=result.triggered_by,
            outcome=result.outcome,
            ejected_player_id=result.ejected_player_id,
            transcript=result.transcript,
            ballots=result.ballots,
            contradictions=result.contradictions,
            llm_calls=(),
            prompt_versions=dict(DEFAULT_PROMPT_VERSIONS),
            state_hash_before="hash-before",
            state_hash_after="hash-after",
        )

        assert entry.prompt_versions["accusation_round"] == "accusation_round.v2"
        assert entry.prompt_versions["accusation_round"] != "accusation_round.v1"


# --- Task 7.10: fail-soft statements + single accusation round -------------


@dataclass
class _NormalizingScriptedClient:
    """Scripted client that mirrors the real provider's extract→validate seam.

    The plain :class:`_ScriptedLLMClient` validates ``responder`` output
    directly, so it cannot exercise the Task 7.6/7.10 parse-tolerance
    normalization the way a real run does. The Anthropic and Ollama adapters
    route every structured response through
    :func:`llm.provider._extract_json_block` (which runs the normalizer) before
    validating; this client does the same, so a near-miss statement — e.g. a
    reversed ``AlibiClaim`` range — is salvaged exactly as in production before
    the manager consumes ``LLMResponse.text``.
    """

    responder: Callable[[str, type[BaseModel] | None], str]

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
        raw = self.responder(prompt, schema)
        text = _extract_json_block(raw, schema) if schema is not None else raw
        if schema is not None:
            schema.model_validate_json(text)
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "normalizing-test",
        )


def _reversed_alibi_statement_json(*, speaker: str) -> str:
    """A Statement carrying a reversed (``from_tick > to_tick``) AlibiClaim.

    Built via ``json.dumps`` rather than the Statement model so the invalid
    range survives to the client (the model would reject it at construction).
    This is the seed-25/36/40 crash shape.
    """

    return json.dumps(
        {
            "statement_id": "ignored",
            "speaker": speaker,
            "tick": 0,
            "round_index": 0,
            "target": None,
            "claims": [
                {
                    "type": "alibi",
                    "subject": speaker,
                    "from_tick": 8,
                    "to_tick": 1,
                    "room": "CAFETERIA",
                }
            ],
            "free_text": f"reversed-alibi-{speaker}",
        }
    )


class TestStatementFailSoft:
    """A malformed statement degrades to a placeholder; the meeting continues.

    Task 7.10 / audit ``audits/audit-2026-06-01-1425-gameplay-data.md`` gp-2,
    E-E-1, A-A-2: before this, a single statement whose structured output
    failed schema validation (e.g. a reversed-chronology ``AlibiClaim``)
    propagated out of the meeting and aborted the game with no ``game_over``
    (seeds 25/36/40). The statement phase now fails soft: the bad statement
    becomes the missed-deadline placeholder and the meeting runs to resolution.
    """

    def _statement_only_responder(
        self,
        *,
        statement_for: Callable[[str], str],
    ) -> Callable[[str, type[BaseModel] | None], str]:
        # Reports/votes use the standard valid stubs; statements are produced by
        # ``statement_for(speaker)`` so a single speaker can be made malformed.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=STATEMENT" in prompt:
                speaker = _extract_marker(prompt, "agent_id=")
                return statement_for(speaker)
            return _make_responder()(prompt, schema)

        return _responder

    def test_single_malformed_statement_degrades_and_meeting_resolves(self) -> None:
        # p-3's statement is unparseable JSON (the hardest malformation); the
        # other two speakers return valid stubs. The meeting must still resolve.
        def _statement_for(speaker: str) -> str:
            if speaker == "p-3":
                return "this is not json at all {{"
            return _stub_statement_json(speaker=speaker, round_index=0)

        client = _ScriptedLLMClient(
            responder=self._statement_only_responder(statement_for=_statement_for)
        )
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-failsoft",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # The meeting reached resolution (no raise) with a ballot per player.
        assert result.outcome in {"EJECTED", "SKIPPED"}
        assert len(result.ballots) == 3
        # One statement per speaker (round_count=1). p-3's is the placeholder;
        # the other two are the real stubbed statements, untouched.
        by_speaker = {s.speaker: s for s in result.transcript.statements}
        assert by_speaker["p-3"].free_text == DEFAULT_STATEMENT_FREE_TEXT
        assert by_speaker["p-3"].claims == ()
        assert by_speaker["p-1"].free_text != DEFAULT_STATEMENT_FREE_TEXT
        assert by_speaker["p-2"].free_text != DEFAULT_STATEMENT_FREE_TEXT

    def test_reversed_alibi_statement_fails_soft_without_normalization(self) -> None:
        # If a reversed-chronology alibi reaches schema validation unrepaired
        # (the _ScriptedLLMClient does not normalize), the manager must NOT
        # abort: it degrades that one statement and resolves the meeting.
        client = _ScriptedLLMClient(
            responder=self._statement_only_responder(
                statement_for=lambda speaker: _reversed_alibi_statement_json(
                    speaker=speaker
                )
            )
        )
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-reversed",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        # Every statement degraded to the placeholder; the meeting still
        # resolved instead of raising a ValidationError out of the phase loop.
        assert result.outcome in {"EJECTED", "SKIPPED"}
        assert len(result.transcript.statements) == 3
        for statement in result.transcript.statements:
            assert statement.free_text == DEFAULT_STATEMENT_FREE_TEXT

    def test_reversed_alibi_normalizes_then_meeting_resolves_with_real_statement(
        self,
    ) -> None:
        # The primary fix (gp-2 part 1): through the real provider seam the
        # reversed alibi is normalized to a chronological one, so the statement
        # validates and lands as a REAL statement (bounds swapped), NOT the
        # fail-soft placeholder. This is the path a live Ollama run takes.
        client = _NormalizingScriptedClient(
            responder=self._statement_only_responder(
                statement_for=lambda speaker: _reversed_alibi_statement_json(
                    speaker=speaker
                )
            )
        )
        manager = _make_manager(llm_client=client, round_count=1)

        result = _run(
            manager.run(
                meeting_id="m-normalized",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert result.outcome in {"EJECTED", "SKIPPED"}
        assert len(result.transcript.statements) == 3
        for statement in result.transcript.statements:
            # Salvaged, not degraded: the real free_text survived...
            assert statement.free_text != DEFAULT_STATEMENT_FREE_TEXT
            alibis = [c for c in statement.claims if isinstance(c, AlibiClaim)]
            assert len(alibis) == 1
            # ...and the reversed range was swapped into chronological order.
            assert alibis[0].from_tick == 1
            assert alibis[0].to_tick == 8

    def test_report_validation_error_still_propagates(self) -> None:
        # Fail-soft is deliberately statement-only (Task 7.10 scope). A report
        # whose structured output fails validation still propagates so the
        # orchestrator records a failed_call — unchanged behavior.
        def _bad_report_responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=REPORT" in prompt:
                return "not json {{"
            return _make_responder()(prompt, schema)

        client = _ScriptedLLMClient(responder=_bad_report_responder)
        manager = _make_manager(llm_client=client, round_count=1)

        with pytest.raises(ValidationError):
            _run(
                manager.run(
                    meeting_id="m-bad-report",
                    trigger=_default_trigger(),
                    participants=_make_participants(),
                )
            )


class TestDefaultRoundCount:
    """R reduced 2→1 (Task 7.10, audit §6 R=2 statement-sink)."""

    def test_default_round_count_constant_is_one(self) -> None:
        assert DEFAULT_ROUND_COUNT == 1

    def test_default_config_round_count_is_one(self) -> None:
        assert MeetingConfig().round_count == 1

    def test_default_config_runs_a_single_accusation_round(self) -> None:
        # Build the manager with NO config so it exercises the PRODUCTION
        # default (MeetingConfig() -> DEFAULT_ROUND_COUNT). 3 participants ×
        # 1 round == 3 statements, all at round_index 0.
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = MeetingManager(
            llm_client=client,
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
        )

        result = _run(
            manager.run(
                meeting_id="m-one-round",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        assert len(result.transcript.statements) == 3
        assert {s.round_index for s in result.transcript.statements} == {0}
        statement_calls = [c for c in client.calls if "PHASE=STATEMENT" in c.prompt]
        assert len(statement_calls) == 3


# ---------------------------------------------------------------------------
# Task 7.12 — teammate firewall guard on the production meeting path
# ---------------------------------------------------------------------------


# p-3 and p-6 are mutual-teammate impostors; p-1, p-2 are crewmates.
_TEAMMATE_OF: dict[PlayerId, PlayerId] = {"p-3": "p-6", "p-6": "p-3"}


def _multi_impostor_participants() -> tuple[MeetingParticipant, ...]:
    return (
        MeetingParticipant(
            agent_id="p-1",
            role="CREWMATE",
            rendered_memory="## Your role: CREWMATE\np-1 memory",
        ),
        MeetingParticipant(
            agent_id="p-2",
            role="CREWMATE",
            rendered_memory="## Your role: CREWMATE\np-2 memory",
        ),
        MeetingParticipant(
            agent_id="p-3",
            role="IMPOSTOR",
            rendered_memory="## Your role: IMPOSTOR\np-3 memory",
            fellow_impostor_ids=("p-6",),
        ),
        MeetingParticipant(
            agent_id="p-6",
            role="IMPOSTOR",
            rendered_memory="## Your role: IMPOSTOR\np-6 memory",
            fellow_impostor_ids=("p-3",),
        ),
    )


def _betrayal_responder() -> Callable[[str, type[BaseModel] | None], str]:
    """Make every impostor accuse and vote its own teammate.

    The deterministic guard must neutralise all of it: ballots coerce to
    SKIP, accusation claims against a teammate drop, and a teammate-naming
    statement target degrades to ``None`` (audit gp-imp-1 / D-D-1..D-D-4;
    seed-6 meeting-0 repro). Crewmates SKIP.
    """

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=REPORT" in prompt:
            agent_id = _extract_marker(prompt, "agent_id=")
            tick = int(_extract_marker(prompt, "tick="))
            mate = _TEAMMATE_OF.get(agent_id)
            if mate is not None:
                return ReportDocument(
                    agent_id=agent_id,
                    tick=tick,
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against=mate,
                            confidence=0.9,
                            reason="fabricated frame of my teammate",
                        ),
                    ),
                    free_text=f"betray-{agent_id}",
                ).model_dump_json()
            return _stub_report_json(agent_id=agent_id, tick=tick)
        if "PHASE=STATEMENT" in prompt:
            agent_id = _extract_marker(prompt, "agent_id=")
            mate = _TEAMMATE_OF.get(agent_id)
            if mate is not None:
                return Statement(
                    statement_id="ignored",
                    speaker=agent_id,
                    tick=0,
                    round_index=0,
                    target=mate,
                    claims=(
                        AccusationClaim(
                            type="accusation",
                            against=mate,
                            confidence=0.9,
                            reason="incriminate my teammate",
                        ),
                    ),
                    free_text=f"betray-stmt-{agent_id}",
                ).model_dump_json()
            return _stub_statement_json(speaker="placeholder", round_index=0)
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            target = _TEAMMATE_OF.get(voter, "SKIP")
            return _stub_vote_json(voter=voter, target=target)
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    return _responder


class TestMeetingParticipantFellowImpostorIds:
    """The new ``fellow_impostor_ids`` field (Task 7.12)."""

    def test_default_is_empty_tuple(self) -> None:
        participant = MeetingParticipant(
            agent_id="p-1", role="CREWMATE", rendered_memory="m"
        )
        assert participant.fellow_impostor_ids == ()

    def test_accepts_teammate_ids(self) -> None:
        participant = MeetingParticipant(
            agent_id="p-3",
            role="IMPOSTOR",
            rendered_memory="m",
            fellow_impostor_ids=("p-6",),
        )
        assert participant.fellow_impostor_ids == ("p-6",)


class TestTeammateGuardHelpers:
    """Pure deterministic guard helpers (Task 7.12)."""

    def test_coerce_teammate_ballot_to_skip(self) -> None:
        ballot = VoteBallot(
            voter="p-3",
            target="p-6",
            confidence=0.9,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="vote my teammate",
        )
        guarded = coerce_teammate_ballot_to_skip(
            ballot=ballot, fellow_impostor_ids=("p-6",)
        )
        assert guarded.target == "SKIP"
        assert guarded.rationale_text.startswith(
            TEAMMATE_VOTE_TARGET_MARKER.format(target="p-6")
        )
        # Original (teammate) target preserved for audit.
        assert "p-6" in guarded.rationale_text

    def test_coerce_leaves_non_teammate_and_skip_untouched(self) -> None:
        ballot = VoteBallot(
            voter="p-3",
            target="p-1",
            confidence=0.9,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="vote a crewmate",
        )
        assert (
            coerce_teammate_ballot_to_skip(ballot=ballot, fellow_impostor_ids=("p-6",))
            is ballot
        )
        # Empty fellow list (sole impostor / crew) is an exact no-op.
        teammate_shaped = ballot.model_copy(update={"target": "p-6"})
        assert (
            coerce_teammate_ballot_to_skip(
                ballot=teammate_shaped, fellow_impostor_ids=()
            )
            is teammate_shaped
        )

    def test_exclude_teammate_accusation_claims(self) -> None:
        accusation = AccusationClaim(
            type="accusation", against="p-6", confidence=0.9, reason="frame"
        )
        corroboration = CorroborationClaim(
            type="corroboration", supports="p-6", on_tick=10, reason="back"
        )
        other_accusation = AccusationClaim(
            type="accusation", against="p-1", confidence=0.5, reason="real"
        )
        claims: tuple[Claim, ...] = (accusation, corroboration, other_accusation)
        guarded = exclude_teammate_accusation_claims(
            claims, fellow_impostor_ids=("p-6",)
        )
        assert accusation not in guarded
        # Corroboration of a teammate HELPS them — kept. Accusation of a
        # non-teammate is untouched.
        assert corroboration in guarded
        assert other_accusation in guarded
        # Empty fellow list is an exact no-op (same object).
        assert exclude_teammate_accusation_claims(claims, fellow_impostor_ids=()) is (
            claims
        )

    def test_drop_teammate_statement_target(self) -> None:
        assert drop_teammate_statement_target("p-6", fellow_impostor_ids=("p-6",)) is (
            None
        )
        assert (
            drop_teammate_statement_target("p-1", fellow_impostor_ids=("p-6",)) == "p-1"
        )
        assert drop_teammate_statement_target(None, fellow_impostor_ids=("p-6",)) is (
            None
        )
        assert drop_teammate_statement_target("p-6", fellow_impostor_ids=()) == "p-6"


class TestTeammateGuardOnProductionPath:
    """End-to-end guard through ``MeetingManager.run`` (the recorded path).

    This is the production meeting path that records the committed eval
    sets; the seed-6 meeting-0 repro (impostors p-3 + p-6) is reproduced
    here with a scripted client that makes both impostors betray each
    other. The guard must neutralise every betrayal regardless of the
    model output.
    """

    def test_impostor_ballots_against_teammate_are_coerced_to_skip(self) -> None:
        client = _ScriptedLLMClient(responder=_betrayal_responder())
        manager = _make_manager(llm_client=client)

        result = _run(
            manager.run(
                meeting_id="m-betray",
                trigger=_default_trigger(),
                participants=_multi_impostor_participants(),
            )
        )

        ballots = {b.voter: b for b in result.ballots}
        # Both impostors tried to vote their teammate; both coerced to SKIP.
        assert ballots["p-3"].target == "SKIP"
        assert ballots["p-6"].target == "SKIP"
        assert "teammate target" in ballots["p-3"].rationale_text
        assert "teammate target" in ballots["p-6"].rationale_text
        # No ballot from any impostor targets a teammate.
        for voter, mate in _TEAMMATE_OF.items():
            assert ballots[voter].target != mate

    def test_no_impostor_ejected_by_teammate_betrayal(self) -> None:
        # With the betrayal votes removed (coerced to SKIP) and crew SKIP,
        # the meeting resolves to SKIPPED — the audit's seed-6 outcome flip
        # (a 2-vote eject becomes a SKIP once the teammate vote is gone).
        client = _ScriptedLLMClient(responder=_betrayal_responder())
        manager = _make_manager(llm_client=client)

        result = _run(
            manager.run(
                meeting_id="m-betray",
                trigger=_default_trigger(),
                participants=_multi_impostor_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None

    def test_impostor_report_and_statement_accusations_against_teammate_dropped(
        self,
    ) -> None:
        client = _ScriptedLLMClient(responder=_betrayal_responder())
        manager = _make_manager(llm_client=client)

        result = _run(
            manager.run(
                meeting_id="m-betray",
                trigger=_default_trigger(),
                participants=_multi_impostor_participants(),
            )
        )

        # No report or statement authored by an impostor names a teammate
        # in an accusation claim or as a statement target.
        for report in result.transcript.reports:
            mate = _TEAMMATE_OF.get(report.agent_id)
            if mate is None:
                continue
            assert not any(
                isinstance(c, AccusationClaim) and c.against == mate
                for c in report.claims
            )
        for statement in result.transcript.statements:
            mate = _TEAMMATE_OF.get(statement.speaker)
            if mate is None:
                continue
            assert statement.target != mate
            assert not any(
                isinstance(c, AccusationClaim) and c.against == mate
                for c in statement.claims
            )

    def test_manager_threads_teammate_list_into_impostor_prompts_only(self) -> None:
        client = _ScriptedLLMClient(responder=_make_responder())
        manager = _make_manager(llm_client=client)

        _run(
            manager.run(
                meeting_id="m-thread",
                trigger=_default_trigger(),
                participants=_multi_impostor_participants(),
            )
        )

        impostor_prompts = [
            c.prompt for c in client.calls if "agent_id=p-3" in c.prompt
        ] + [c.prompt for c in client.calls if "voter=p-3" in c.prompt]
        crew_prompts = [
            c.prompt for c in client.calls if "agent_id=p-1" in c.prompt
        ] + [c.prompt for c in client.calls if "voter=p-1" in c.prompt]
        assert impostor_prompts
        assert crew_prompts
        # The stub renderers surface a FELLOW_IMPOSTORS= line only when the
        # teammate list is non-empty: every impostor (p-3) prompt carries
        # its teammate p-6; no crewmate (p-1) prompt carries any.
        assert all("FELLOW_IMPOSTORS=p-6" in p for p in impostor_prompts)
        assert all("FELLOW_IMPOSTORS=" not in p for p in crew_prompts)

    def test_crew_and_sole_impostor_meeting_is_unaffected(self) -> None:
        # The default single-impostor roster (p-3 sole impostor) carries an
        # empty teammate list everywhere, so the guard and the prompt block
        # are no-ops — a sole impostor's vote for a crewmate survives.
        client = _ScriptedLLMClient(
            responder=_make_responder(vote_targets={"p-3": "p-1"})
        )
        manager = _make_manager(llm_client=client)

        result = _run(
            manager.run(
                meeting_id="m-sole",
                trigger=_default_trigger(),
                participants=_make_participants(),
            )
        )

        impostor_ballot = next(b for b in result.ballots if b.voter == "p-3")
        assert impostor_ballot.target == "p-1"
        assert "teammate target" not in impostor_ballot.rationale_text
        # No teammate block leaked into any prompt (all lists empty).
        assert all("FELLOW_IMPOSTORS=" not in c.prompt for c in client.calls)
