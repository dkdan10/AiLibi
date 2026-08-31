"""Shared meeting-manager test helpers (Task 19.27).

The scripted-LLM harness the meeting-protocol tests drive the
:class:`~meetings.manager.MeetingManager` with: stub prompt callables that
tag each rendered prompt with greppable ``PHASE=…`` markers, the recording
:class:`_ScriptedLLMClient`, the per-speaker responder builder, and the
one-call :func:`_run_meeting` entry point.

Extracted from ``tests/meetings/test_manager.py`` (audits/
audit-phase-19-triage.md §7 item 28): five sibling modules imported that
7.5k-line test module as a library, so every one of them re-imported (and
re-collected) the whole suite to reach ~400 lines of helpers. This module
is deliberately NOT named ``test_*``: pytest never collects it, and it
defines no tests — helpers only. ``test_manager.py`` imports it back like
any other consumer.

``_participants`` / ``_obs_vote_responder`` moved here from
``tests/meetings/test_ballot_observation_citation.py`` on the same grounds
(two siblings imported them from that test module).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field, replace
from typing import TypeVar

from pydantic import BaseModel

from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from meetings.manager import (
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    PromptRenderInputs,
    ReporterContext,
    SuspicionEntry,
)
from meetings.schemas import (
    AccusationClaim,
    Claim,
    ContradictionRef,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    ObservationId,
    PlayerId,
    VentWitnessRecord,
    VoteBallot,
)

_T = TypeVar("_T")


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


# --- Stub prompt callables -------------------------------------------------


def _fellow_impostors_line(fellow_impostor_ids: tuple[PlayerId, ...]) -> str:
    if not fellow_impostor_ids:
        return ""
    return f"FELLOW_IMPOSTORS={','.join(fellow_impostor_ids)}\n"


def _living_ids_line(living_ids: tuple[PlayerId, ...]) -> str:
    if not living_ids:
        return ""
    return f"LIVING_IDS={','.join(living_ids)}\n"


def _dead_ids_line(dead_ids: tuple[PlayerId, ...]) -> str:
    if not dead_ids:
        return ""
    return f"DEAD_IDS={','.join(dead_ids)}\n"


def _crewmate_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    persona: str = "",  # Task 16.3: widened contract kwarg (inert)
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),  # Task 16.3
    render_inputs: PromptRenderInputs | None = None,  # Task 20.31
    reporter_context: ReporterContext | None = None,  # reporter-voice (inert)
    at_body: bool = False,  # reporter-voice (inert)
) -> str:
    return (
        f"PHASE=OPENING ROLE=CREWMATE agent_id={agent_id} tick={current_tick}\n"
        f"TRIGGER: {meeting_trigger}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"{_living_ids_line(living_ids)}"
        f"{_dead_ids_line(dead_ids)}"
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
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    persona: str = "",  # Task 16.3: widened contract kwarg (inert)
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),  # Task 16.3
    render_inputs: PromptRenderInputs | None = None,  # Task 20.31
    reporter_context: ReporterContext | None = None,  # reporter-voice (inert)
    at_body: bool = False,  # reporter-voice (inert)
) -> str:
    return (
        f"PHASE=OPENING ROLE=IMPOSTOR agent_id={agent_id} tick={current_tick}\n"
        f"TRIGGER: {meeting_trigger}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"{_living_ids_line(living_ids)}"
        f"{_dead_ids_line(dead_ids)}"
        f"MEMORY:\n{rendered_memory}\n"
        f"PUBLIC_TRANSCRIPT:\n{public_transcript}\n"
    )


def _statement_prompt(
    *,
    agent_id: PlayerId,
    rendered_memory: str,
    transcript: MeetingTranscript,
    contradictions: tuple[ContradictionRef, ...],
    prior_turn: MeetingTurn | None,
    turn_kind: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
    dead_ids: tuple[PlayerId, ...] = (),
    is_impostor: bool = False,
    is_body_report: bool = False,
    persona: str = "",  # Task 16.3: widened contract kwarg (inert)
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),  # Task 16.3
    render_inputs: PromptRenderInputs | None = None,  # Task 20.31
    reporter_context: ReporterContext | None = None,  # reporter-voice (inert)
    at_body: bool = False,  # reporter-voice (inert)
) -> str:
    prior = prior_turn.speaker if prior_turn is not None else "none"
    return (
        f"PHASE=TURN turn_kind={turn_kind} agent_id={agent_id} prior={prior}"
        f" is_impostor={is_impostor} is_body_report={is_body_report}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"{_living_ids_line(living_ids)}"
        f"{_dead_ids_line(dead_ids)}"
        f"MEMORY:\n{rendered_memory}\n"
        f"TURNS_COUNT={len(transcript.turns)}\n"
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
    reporter_id: PlayerId | None = None,
    persona: str = "",  # Task 16.3: widened contract kwarg (inert)
    suspicion_provenance: tuple[SuspicionEntry, ...] = (),  # Task 16.3
    render_inputs: PromptRenderInputs | None = None,  # Task 20.31
) -> str:
    # ``reporter_id`` (Task 15.5) conforms to the widened VotePromptRenderer
    # contract; surfaced only when supplied so a lever-OFF (``None``) render is
    # byte-identical to the pre-15.5 stub output.
    suspicion_block = ",".join(
        f"{entry.player_id}:{entry.suspicion:.2f}/{entry.trust:.2f}"
        for entry in suspicion_graph
    )
    reporter_line = f"reporter={reporter_id}\n" if reporter_id else ""
    return (
        "PHASE=VOTE\n"
        f"voter={voter_id}\n"
        f"candidates={','.join(candidate_targets)}\n"
        f"skip_threshold={skip_confidence_threshold:.2f}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"{reporter_line}"
        f"suspicion={suspicion_block}\n"
        f"MEMORY:\n{rendered_memory}\n"
        f"TURNS_COUNT={len(transcript.turns)}\n"
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

    The callback receives the prompt string and the schema (if any) and
    returns the JSON string the manager should consume. The client records
    every call so tests can assert on the protocol sequence.
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


def _turn_json(
    *,
    speaker: str,
    accuses: str | None = None,
    observations: tuple[ObservationClaim, ...] = (),
    claims: tuple[Claim, ...] = (),
    free_text: str | None = None,
) -> str:
    turn_claims: list[Claim] = list(claims)
    if accuses is not None:
        turn_claims.append(
            AccusationClaim(
                type="accusation",
                against=accuses,
                confidence=0.6,
                reason=f"{speaker} accuses {accuses}",
            )
        )
    if free_text is None:
        free_text = f"turn from {speaker}"
        if accuses is None:
            # Protocol-valid stance for a non-accusing stub turn (DESIGN.md
            # §5.2 PHASE 1; Task 10.3): an opening that names no accusation
            # must declare "unsure" or the manager retries it. Appended only
            # when no accusation is scripted, so accusing stubs keep their
            # pre-10.3 text; pass an explicit ``free_text`` to exercise the
            # narration-only validation itself.
            free_text += " -- unsure"
    # turn_id / turn_index / speaker / turn_kind / reply_to are overwritten by
    # the manager; the values here are placeholders.
    return MeetingTurn(
        turn_id="placeholder",
        turn_index=0,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        observations=observations,
        claims=tuple(turn_claims),
        free_text=free_text,
    ).model_dump_json()


def _vote_json(
    *,
    voter: str,
    target: str,
    confidence: float = 0.8,
    primary_reason_id: str | None = None,
) -> str:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=primary_reason_id,
        considered_alternatives=(),
        rationale_text=f"stub-vote-{voter}-{target}",
    ).model_dump_json()


def _extract_marker(prompt: str, marker: str) -> str:
    idx = prompt.find(marker)
    assert idx >= 0, f"marker {marker!r} not found in prompt {prompt!r}"
    rest = prompt[idx + len(marker) :]
    end = 0
    while end < len(rest) and not rest[end].isspace():
        end += 1
    return rest[:end]


def _make_responder(
    *,
    accusations: dict[str, str | None] | None = None,
    observations: dict[str, tuple[ObservationClaim, ...]] | None = None,
    claims_by: dict[str, tuple[Claim, ...]] | None = None,
    vote_targets: dict[str, str] | None = None,
    vote_reason_ids: dict[str, str] | None = None,
    free_text: dict[str, str] | None = None,
) -> Callable[[str, type[BaseModel] | None], str]:
    """Build a responder that dispatches by phase markers in the prompt.

    Turns (opening + reactive/opt-in) are driven by the per-speaker
    ``accusations`` (the chain target), optional ``observations`` (drive
    the opt-in co-presence gate), and optional ``claims_by`` (e.g. alibis
    for contradiction tests). Votes default to "SKIP" unless overridden;
    ``vote_reason_ids`` drives the per-voter ``primary_reason_id`` (used by
    the reason-id-integrity tests, DESIGN.md §5.5).
    """

    accusations = accusations or {}
    observations = observations or {}
    claims_by = claims_by or {}
    vote_targets = vote_targets or {}
    vote_reason_ids = vote_reason_ids or {}
    free_text = free_text or {}

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            speaker = _extract_marker(prompt, "agent_id=")
            return _turn_json(
                speaker=speaker,
                accuses=accusations.get(speaker),
                observations=observations.get(speaker, ()),
                claims=claims_by.get(speaker, ()),
                free_text=free_text.get(speaker),
            )
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            return _vote_json(
                voter=voter,
                target=vote_targets.get(voter, "SKIP"),
                primary_reason_id=vote_reason_ids.get(voter),
            )
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    return _responder


def _participant(
    agent_id: str,
    *,
    role: str = "CREWMATE",
    suspicion_graph: tuple[SuspicionEntry, ...] = (),
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    vent_witness_records: tuple[VentWitnessRecord, ...] = (),
) -> MeetingParticipant:
    return MeetingParticipant(
        agent_id=agent_id,
        role=role,  # type: ignore[arg-type]
        rendered_memory=f"## Your role: {role}\n{agent_id} memory",
        suspicion_graph=suspicion_graph,
        fellow_impostor_ids=fellow_impostor_ids,
        vent_witness_records=vent_witness_records,
    )


def _crew_participants() -> tuple[MeetingParticipant, ...]:
    return (
        _participant(
            "p-1",
            suspicion_graph=(
                SuspicionEntry(player_id="p-2", suspicion=0.4, trust=0.5),
            ),
        ),
        _participant("p-2"),
        _participant("p-3"),
        _participant("p-4"),
    )


def _make_manager(
    *,
    llm_client: LLMClient,
    deadlines: MeetingDeadlines | None = None,
    skip_confidence_threshold: float = 0.6,
) -> MeetingManager:
    config = MeetingConfig(
        deadlines=deadlines if deadlines is not None else MeetingDeadlines(),
        skip_confidence_threshold=skip_confidence_threshold,
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


def _run_meeting(
    responder: Callable[[str, type[BaseModel] | None], str],
    *,
    participants: tuple[MeetingParticipant, ...] | None = None,
    trigger: MeetingTrigger | None = None,
    meeting_id: str = "m-1",
    deadlines: MeetingDeadlines | None = None,
    skip_confidence_threshold: float = 0.6,
    dead_ids: tuple[PlayerId, ...] = (),
) -> tuple[MeetingResult, _ScriptedLLMClient]:
    client = _ScriptedLLMClient(responder=responder)
    manager = _make_manager(
        llm_client=client,
        deadlines=deadlines,
        skip_confidence_threshold=skip_confidence_threshold,
    )
    result = _run(
        manager.run(
            meeting_id=meeting_id,
            trigger=trigger if trigger is not None else _default_trigger(),
            participants=participants
            if participants is not None
            else _crew_participants(),
            dead_ids=dead_ids,
        )
    )
    return result, client


# --- The ballot-observation-citation helpers (Task 16.5) --------------------


def _participants(
    observation_ids_by_id: dict[str, tuple[ObservationId, ...]],
) -> tuple[MeetingParticipant, ...]:
    """Four living crewmates; each voter's own valid-id set threaded on."""

    return tuple(
        replace(
            _participant(agent_id),
            observation_ids=observation_ids_by_id.get(agent_id, ()),
        )
        for agent_id in ("p-1", "p-2", "p-3", "p-4")
    )


def _obs_vote_responder(
    *,
    observation_ids_by_voter: dict[str, ObservationId | None],
    targets: dict[str, str] | None = None,
) -> Callable[[str, type[BaseModel] | None], str]:
    """A responder that drives every turn to an ``unsure`` opening and emits a
    vote per voter carrying the scripted ``primary_reason_observation_id``.

    Mirrors :func:`_make_responder` but reaches the citation field (the shared
    ``_vote_json`` helper predates it)."""

    resolved_targets = targets or {}

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            return _turn_json(speaker=_extract_marker(prompt, "agent_id="))
        if "PHASE=VOTE" in prompt:
            voter = _extract_marker(prompt, "voter=")
            return VoteBallot(
                voter=voter,
                target=resolved_targets.get(voter, "SKIP"),
                confidence=0.8,
                primary_reason_id=None,
                primary_reason_observation_id=observation_ids_by_voter.get(voter),
                considered_alternatives=(),
                rationale_text=f"stub-vote-{voter}",
            ).model_dump_json()
        raise AssertionError(f"unrecognised prompt: {prompt!r}")

    return _responder
