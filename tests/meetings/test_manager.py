"""Tests for the meeting state machine (Task 8.7).

The contract exercised here is the reactive accusation chain (DESIGN.md
§5.2):

* :class:`MeetingManager` runs one ordered ``transcript.turns`` list --
  opening -> reactive chain -> opt-in info-share -> vote -> resolution.
* The chain's next speaker is the player just accused; it terminates
  deterministically (no new accusation / accused-not-living /
  re-accusation cycle / turn-count cap), and a replay walks the recorded
  turn list without re-calling the LLM.
* Opt-in is limited to living non-speakers with a relevant observation
  (a co-presence gate with the body / accused), one terminal turn each,
  and never extends the chain.
* Every turn-kind flows through one chokepoint, so the 7.12 teammate
  firewall, self-alibi normalization, and the 7.10 fail-soft wrap every
  turn; the vote inherits the teammate-ballot guard.
* Contradictions (§5.4) recompute once over the full transcript before
  voting; the tally + tie->SKIP rule are preserved.

Tests use a controllable in-memory LLM client (no Anthropic SDK calls)
and stub prompt callables. The fake provider in ``llm/fake_provider.py``
is also exercised to confirm Protocol compatibility + determinism.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel, ValidationError

from agents.memory.beliefs import (
    ACCUSATION_SUSPICION_DELTA,
    CORROBORATION_SUSPICION_DELTA,
    TESTIMONY_INDEPENDENCE_BAR,
    BeliefState,
    apply_meeting_evidence_rules,
)
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import AgentMemory, absorb_meeting_evidence, render_for_prompt
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.provider import LLMCallFailure, _attach_parse_failure  # noqa: PLC2701
from llm.fake_provider import FakeProvider
from meetings.manager import (
    BALLOT_TARGET_REDIRECT_MARKER,
    DEFAULT_TURN_FREE_TEXT,
    DEFAULT_VOTE_RATIONALE,
    EMERGENCY_BODY_STRIP_MARKER,
    EMERGENCY_NO_BODY_RETRY_FEEDBACK,
    INVALID_ACCUSATION_TARGET_MARKER,
    INVALID_ALIBI_SUBJECT_MARKER,
    INVALID_CORROBORATION_SUPPORTS_MARKER,
    INVALID_REASON_ID_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    MARKER_QUOTED_ORIGINAL_MAX_CHARS,
    OPENING_RETRY_FEEDBACK_DEMAND,
    OPENING_RETRY_FEEDBACK_HEADER,
    OPENING_RETRY_FEEDBACK_NO_POSITION,
    OPENING_UNSURE_DEGRADE_MARKER,
    OPENING_UNSURE_MARKER,
    OPENING_UNSURE_MAX_FREE_TEXT_CHARS,
    TEAMMATE_VOTE_TARGET_MARKER,
    VOTE_PARSE_DEFAULT_MARKER,
    LLMProviderError,
    MeetingBeliefEvidence,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    SuspicionEntry,
    _drop_non_roster_claims,  # noqa: PLC2701
    _opening_takes_position,  # noqa: PLC2701
    _normalize_self_alibi_subjects,  # noqa: PLC2701
    _suspicion_graph_with_contradictions,  # noqa: PLC2701
    _trigger_is_emergency,  # noqa: PLC2701
    coerce_teammate_ballot_to_skip,
    derive_belief_evidence,
    drop_teammate_statement_target,
    exclude_teammate_accusation_claims,
    extract_belief_evidence,
    guard_ballot_target_graph,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    PlayerId,
    SawPlayerObservation,
    VoteBallot,
)
from meetings.transcript import (
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_SELF_STATED,
    detect_contradictions,
    detect_corroborations,
    independent_voices,
    is_canonically_ordered,
    walk_chain,
)

_T = TypeVar("_T")

# Default per-player suspicion prior in agents.memory.beliefs (the score a
# player starts at before any belief rule fires). Mirrored here so the Rule-2
# wiring tests can assert "strictly above the default" without importing the
# agents-side constant.
_DEFAULT_TEST_SUSPICION = 0.5


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
) -> MeetingParticipant:
    return MeetingParticipant(
        agent_id=agent_id,
        role=role,  # type: ignore[arg-type]
        rendered_memory=f"## Your role: {role}\n{agent_id} memory",
        suspicion_graph=suspicion_graph,
        fellow_impostor_ids=fellow_impostor_ids,
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


# --- Construction / configuration ------------------------------------------


class TestConstruction:
    def test_default_config_is_used_when_none_passed(self) -> None:
        manager = MeetingManager(
            llm_client=_ScriptedLLMClient(responder=_make_responder()),
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=_vote_prompt,
        )
        result = _run(
            manager.run(
                meeting_id="m-default",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )
        assert isinstance(result, MeetingResult)

    def test_out_of_range_skip_threshold_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="skip_confidence_threshold"):
            MeetingManager(
                llm_client=_ScriptedLLMClient(responder=_make_responder()),
                crewmate_report_prompt=_crewmate_report_prompt,
                impostor_report_prompt=_impostor_report_prompt,
                statement_prompt=_statement_prompt,
                vote_prompt=_vote_prompt,
                config=MeetingConfig(skip_confidence_threshold=1.5),
            )


class TestRunPreconditions:
    def test_empty_participants_is_rejected(self) -> None:
        manager = _make_manager(llm_client=_ScriptedLLMClient(_make_responder()))
        with pytest.raises(ValueError, match="at least one living participant"):
            _run(
                manager.run(meeting_id="m", trigger=_default_trigger(), participants=())
            )

    def test_empty_meeting_id_is_rejected(self) -> None:
        manager = _make_manager(llm_client=_ScriptedLLMClient(_make_responder()))
        with pytest.raises(ValueError, match="meeting_id"):
            _run(
                manager.run(
                    meeting_id="",
                    trigger=_default_trigger(),
                    participants=_crew_participants(),
                )
            )

    def test_duplicate_participant_ids_rejected(self) -> None:
        manager = _make_manager(llm_client=_ScriptedLLMClient(_make_responder()))
        with pytest.raises(ValueError, match="unique agent_ids"):
            _run(
                manager.run(
                    meeting_id="m",
                    trigger=_default_trigger(),
                    participants=(_participant("p-1"), _participant("p-1")),
                )
            )

    def test_non_participant_reporter_is_rejected(self) -> None:
        manager = _make_manager(llm_client=_ScriptedLLMClient(_make_responder()))
        trigger = MeetingTrigger(
            triggered_by="p-99", trigger_tick=1, description="ghost report"
        )
        with pytest.raises(ValueError, match="not in"):
            _run(
                manager.run(
                    meeting_id="m",
                    trigger=trigger,
                    participants=_crew_participants(),
                )
            )


# --- Opening turn ----------------------------------------------------------


class TestOpeningTurn:
    def test_opening_is_turn_zero_with_authoritative_identity(self) -> None:
        result, _ = _run_meeting(_make_responder())

        opening = result.transcript.turns[0]
        assert opening.turn_id == "m-1:turn-0"
        assert opening.turn_index == 0
        assert opening.turn_kind == "opening"
        assert opening.reply_to is None
        assert opening.speaker == "p-1"  # the reporter (trigger.triggered_by)

    def test_opening_observations_are_recorded(self) -> None:
        # found_body / saw_player observations live on the opening turn and
        # are preserved (vote_correctness reads them there).
        obs: tuple[ObservationClaim, ...] = (
            FoundBodyObservation(
                type="found_body", tick=410, body_of="p-9", room="MEDBAY"
            ),
            SawPlayerObservation(
                type="saw_player", tick=400, subject="p-2", room="MEDBAY"
            ),
        )
        result, _ = _run_meeting(_make_responder(observations={"p-1": obs}))

        opening = result.transcript.turns[0]
        assert opening.observations == obs

    def test_impostor_opener_uses_the_impostor_opening_prompt(self) -> None:
        participants = (
            _participant("p-1", role="IMPOSTOR"),
            _participant("p-2"),
            _participant("p-3"),
        )
        _, client = _run_meeting(_make_responder(), participants=participants)

        opening_call = client.calls[0]
        assert "PHASE=OPENING ROLE=IMPOSTOR" in opening_call.prompt

    def test_opening_missed_deadline_records_default_turn(self) -> None:
        async def _slow(prompt: str) -> str:
            await asyncio.sleep(1.0)
            return _turn_json(speaker="never")

        @dataclass
        class _SleepOnOpening:
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
                if "PHASE=OPENING" in prompt:
                    text = await _slow(prompt)
                else:
                    text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="sleep",
                )

        manager = _make_manager(
            llm_client=_SleepOnOpening(),
            deadlines=MeetingDeadlines(turn_seconds=0.01, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        opening = result.transcript.turns[0]
        assert opening.free_text == DEFAULT_TURN_FREE_TEXT
        assert opening.turn_kind == "opening"
        assert opening.claims == ()


# --- Reactive chain --------------------------------------------------------


class TestReactiveChain:
    def test_accusation_passes_floor_to_the_accused(self) -> None:
        result, _ = _run_meeting(_make_responder(accusations={"p-1": "p-3"}))

        turns = result.transcript.turns
        assert turns[0].speaker == "p-1"
        assert turns[1].speaker == "p-3"
        assert turns[1].turn_kind == "reply"
        assert turns[1].reply_to == "m-1:turn-0"

    def test_chain_follows_successive_accusations(self) -> None:
        result, _ = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": "p-3", "p-3": None})
        )

        chain = [t.speaker for t in result.transcript.turns if t.turn_kind != "opt_in"]
        assert chain == ["p-1", "p-2", "p-3"]

    def test_no_new_accusation_terminates_chain(self) -> None:
        result, _ = _run_meeting(_make_responder(accusations={"p-1": None}))

        # Opening with no accusation -> chain is just the opening turn.
        assert [t.turn_kind for t in result.transcript.turns] == ["opening"]

    def test_re_accusation_cycle_terminates_chain(self) -> None:
        # p-1 accuses p-2; p-2 re-accuses p-1, who already opened.
        result, _ = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": "p-1"})
        )

        chain = [t.speaker for t in result.transcript.turns if t.turn_kind != "opt_in"]
        assert chain == ["p-1", "p-2"]

    def test_chain_never_exceeds_living_player_count(self) -> None:
        # Everyone accuses the next; the last accusation must cycle/cap.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-2", "p-2": "p-3", "p-3": "p-4", "p-4": "p-1"}
            )
        )

        chain = [t.speaker for t in result.transcript.turns if t.turn_kind != "opt_in"]
        assert chain == ["p-1", "p-2", "p-3", "p-4"]
        assert len(chain) == 4  # == living-player count

    def test_accusation_of_non_living_player_terminates_chain(self) -> None:
        result, _ = _run_meeting(_make_responder(accusations={"p-1": "p-99"}))

        # The floor cannot pass to a non-participant -> chain stops at opening.
        # (Since Task 10.3 the dropped target also makes the opening
        # narration-only, so the deterministic stub burns its single retry
        # and the opening records as the fail-soft default -- still exactly
        # one opening turn, never a reply.)
        assert [t.turn_kind for t in result.transcript.turns] == ["opening"]


# --- Opt-in info-share -----------------------------------------------------


class TestOptIn:
    def _opening_obs(
        self, *subjects: str, room: str = "MEDBAY"
    ) -> dict[str, tuple[ObservationClaim, ...]]:
        obs: tuple[ObservationClaim, ...] = (
            FoundBodyObservation(type="found_body", tick=410, body_of="p-9", room=room),
            *(
                SawPlayerObservation(type="saw_player", tick=400, subject=s, room=room)
                for s in subjects
            ),
        )
        return {"p-1": obs}

    def test_relevant_non_speaker_takes_one_opt_in_turn(self) -> None:
        # Opening places p-2 in the body room; p-2 (a non-speaker) becomes
        # opt-in eligible. p-4 is never observed and stays silent.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-3"},
                observations=self._opening_obs("p-2"),
            )
        )

        opt_ins = [t for t in result.transcript.turns if t.turn_kind == "opt_in"]
        assert [t.speaker for t in opt_ins] == ["p-2"]
        speakers = {t.speaker for t in result.transcript.turns}
        assert "p-4" not in speakers

    def test_opt_in_is_in_player_id_order(self) -> None:
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-3"},
                observations=self._opening_obs("p-4", "p-2"),
            )
        )

        opt_ins = [
            t.speaker for t in result.transcript.turns if t.turn_kind == "opt_in"
        ]
        assert opt_ins == ["p-2", "p-4"]

    def test_opt_in_turn_does_not_extend_the_chain(self) -> None:
        # p-2's opt-in accuses p-4, but an opt-in never passes the floor:
        # p-4 gets no reply turn.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-3", "p-2": "p-4"},
                observations=self._opening_obs("p-2"),
            )
        )

        kinds = [t.turn_kind for t in result.transcript.turns]
        assert kinds == ["opening", "reply", "opt_in"]
        # p-4 never speaks (the opt-in accusation did not extend the chain).
        assert all(t.speaker != "p-4" for t in result.transcript.turns)

    def test_no_eligible_non_speaker_means_no_opt_in(self) -> None:
        # No observations -> no co-presence -> no opt-in turns.
        result, _ = _run_meeting(_make_responder(accusations={"p-1": "p-3"}))

        assert all(t.turn_kind != "opt_in" for t in result.transcript.turns)


# --- Turn ids --------------------------------------------------------------


class TestTurnIds:
    def test_turn_ids_are_sequential_and_unique(self) -> None:
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-2", "p-2": "p-3", "p-3": None},
            ),
            meeting_id="m-xyz",
        )

        turns = result.transcript.turns
        assert [t.turn_id for t in turns] == [
            f"m-xyz:turn-{i}" for i in range(len(turns))
        ]
        assert len({t.turn_id for t in turns}) == len(turns)
        assert [t.turn_index for t in turns] == list(range(len(turns)))


# --- Replay walk (the deterministic chain-replay-walk test) ----------------


class TestReplayWalk:
    def test_recorded_chain_walks_without_re_calling_the_llm(self) -> None:
        participants = _crew_participants()
        result, client = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-2", "p-2": "p-3", "p-3": None},
                observations={
                    "p-1": (
                        SawPlayerObservation(
                            type="saw_player", tick=400, subject="p-4", room="MEDBAY"
                        ),
                        FoundBodyObservation(
                            type="found_body", tick=410, body_of="p-9", room="MEDBAY"
                        ),
                    )
                },
            ),
            participants=participants,
        )
        calls_during_recording = len(client.calls)

        # The replay-walk is a pure function of the recorded turns + the
        # living set; it must reconstruct the chain and make zero LLM calls.
        living_ids = frozenset(p.agent_id for p in participants)
        walk = walk_chain(result.transcript, living_ids=living_ids)

        assert len(client.calls) == calls_during_recording  # no new LLM calls
        recorded_chain = [
            t.speaker for t in result.transcript.turns if t.turn_kind != "opt_in"
        ]
        assert list(walk.chain_speakers) == recorded_chain
        assert walk.termination == "no_new_accusation"
        # p-4 was placed in the body room -> opt-in eligible -> recorded.
        assert walk.opt_in_speakers == ("p-4",)
        assert is_canonically_ordered(result.transcript.turns)

    def test_walk_is_deterministic_across_repeats(self) -> None:
        result, _ = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": None})
        )
        living_ids = frozenset({"p-1", "p-2", "p-3", "p-4"})

        first = walk_chain(result.transcript, living_ids=living_ids)
        second = walk_chain(result.transcript, living_ids=living_ids)
        assert first == second


# --- Voting and resolution -------------------------------------------------


class TestVotingAndResolution:
    def test_skip_when_all_participants_skip(self) -> None:
        result, _ = _run_meeting(_make_responder())

        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None

    def test_eject_on_plurality(self) -> None:
        result, _ = _run_meeting(
            _make_responder(
                vote_targets={"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP", "p-4": "p-3"}
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"

    def test_tied_non_skip_targets_resolve_to_skipped(self) -> None:
        result, _ = _run_meeting(
            _make_responder(
                vote_targets={"p-1": "p-2", "p-2": "p-3", "p-3": "p-2", "p-4": "p-3"}
            )
        )

        assert result.outcome == "SKIPPED"

    def test_skip_plurality_skips_even_with_one_non_skip_vote(self) -> None:
        result, _ = _run_meeting(
            _make_responder(
                vote_targets={"p-1": "p-3", "p-2": "SKIP", "p-3": "SKIP", "p-4": "SKIP"}
            )
        )

        assert result.outcome == "SKIPPED"

    def test_ballot_voter_is_overridden_to_participant_id(self) -> None:
        # The responder is told to vote as a fixed voter; the manager must
        # overwrite ``voter`` with the canonical participant id.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                return _turn_json(speaker=_extract_marker(prompt, "agent_id="))
            return _vote_json(voter="impersonated", target="SKIP")

        result, _ = _run_meeting(_responder)

        assert sorted(b.voter for b in result.ballots) == ["p-1", "p-2", "p-3", "p-4"]

    def test_missed_vote_deadline_defaults_to_skip(self) -> None:
        async def _slow(prompt: str) -> str:
            await asyncio.sleep(1.0)
            return _vote_json(voter="x", target="p-3")

        @dataclass
        class _SleepOnVote:
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
                    text = await _slow(prompt)
                else:
                    text = _make_responder()(prompt, schema)
                if schema is not None:
                    schema.model_validate_json(text)
                return LLMResponse(
                    text=text,
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="sleep",
                )

        manager = _make_manager(
            llm_client=_SleepOnVote(),
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=0.01),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        assert all(b.rationale_text == DEFAULT_VOTE_RATIONALE for b in result.ballots)


# --- Vote prompt inputs ----------------------------------------------------


class TestVotePromptInputs:
    def test_candidate_targets_exclude_voter_and_are_sorted(self) -> None:
        _, client = _run_meeting(_make_responder())

        vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
        p1_call = next(c for c in vote_calls if "voter=p-1\n" in c.prompt)
        assert "candidates=p-2,p-3,p-4\n" in p1_call.prompt

    def test_suspicion_graph_is_surfaced_to_prompt(self) -> None:
        _, client = _run_meeting(_make_responder())

        vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
        p1_call = next(c for c in vote_calls if "voter=p-1\n" in c.prompt)
        # p-1's prior for p-2 (0.40) surfaces verbatim.
        assert "p-2:0.40/0.50" in p1_call.prompt

    def test_full_transcript_is_surfaced_to_vote_prompt(self) -> None:
        _, client = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": None})
        )

        vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
        # opening + one reply = 2 turns visible at the vote.
        assert all("TURNS_COUNT=2" in c.prompt for c in vote_calls)


class TestTurnPromptLivingRoster:
    """Task 9.9 (DESIGN.md §5.1, §5.2, §5.5; audit gp-3): every turn prompt
    receives the living-roster accusation list -- living participants minus
    the turn's own speaker -- through the same ``_candidate_targets`` filter
    the vote ballot uses for its eject targets (living minus voter)."""

    def test_opening_roster_is_living_minus_speaker_sorted(self) -> None:
        _, client = _run_meeting(_make_responder())

        opening = next(c for c in client.calls if "PHASE=OPENING" in c.prompt)
        # p-1 opens; the roster is the other three living players, sorted.
        assert "LIVING_IDS=p-2,p-3,p-4\n" in opening.prompt

    def test_reply_roster_excludes_the_replying_speaker(self) -> None:
        _, client = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": None})
        )

        reply = next(c for c in client.calls if "PHASE=TURN" in c.prompt)
        assert "agent_id=p-2" in reply.prompt
        assert "LIVING_IDS=p-1,p-3,p-4\n" in reply.prompt


class TestTurnPromptDeadRoster:
    """Task 10.3 (DESIGN.md §5.1, §5.2; audit gp-9 H-H-3, D-D-8): the
    orchestrator-supplied dead / ejected roster threads into every turn
    prompt as the explicit do-not-accuse list; the default ``()`` renders
    no line, and a dead id overlapping the living roster fails loud."""

    def test_dead_ids_thread_into_every_turn_prompt_sorted(self) -> None:
        _, client = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": None}),
            dead_ids=("p-9", "p-5"),
        )

        opening = next(c for c in client.calls if "PHASE=OPENING" in c.prompt)
        assert "DEAD_IDS=p-5,p-9\n" in opening.prompt  # sorted at run() entry
        reply = next(c for c in client.calls if "PHASE=TURN" in c.prompt)
        assert "DEAD_IDS=p-5,p-9\n" in reply.prompt

    def test_default_empty_dead_ids_render_no_line(self) -> None:
        _, client = _run_meeting(_make_responder())

        assert all("DEAD_IDS=" not in c.prompt for c in client.calls)

    def test_dead_id_overlapping_living_roster_fails_loud(self) -> None:
        manager = _make_manager(llm_client=_ScriptedLLMClient(_make_responder()))
        with pytest.raises(ValueError, match="dead_ids overlap living"):
            _run(
                manager.run(
                    meeting_id="m-1",
                    trigger=_default_trigger(),
                    participants=_crew_participants(),
                    dead_ids=("p-2",),
                )
            )


# --- Contradictions wiring -------------------------------------------------


class TestContradictionsWiring:
    def _conflict_responder(
        self, **kwargs: object
    ) -> Callable[[str, type[BaseModel] | None], str]:
        # Opening (p-1) and the reply (p-3) plant conflicting alibis for p-2.
        return _make_responder(
            accusations={"p-1": "p-3", "p-3": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-2",
                        from_tick=100,
                        to_tick=200,
                        room="STORAGE",
                    ),
                ),
                "p-3": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-2",
                        from_tick=150,
                        to_tick=180,
                        room="CAFETERIA",
                    ),
                ),
            },
            **kwargs,  # type: ignore[arg-type]
        )

    def test_claim_free_transcript_carries_no_contradictions(self) -> None:
        result, _ = _run_meeting(_make_responder(accusations={"p-1": "p-3"}))

        assert result.contradictions == ()

    def test_contradiction_recomputed_over_full_transcript_and_threaded(self) -> None:
        result, client = _run_meeting(self._conflict_responder())

        assert len(result.contradictions) == 1
        assert result.contradictions[0].kind == "alibi_conflict"
        assert result.contradictions[0].subjects == ("p-2",)
        # The flag count is threaded into every vote prompt.
        vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
        assert all("FLAGS_COUNT=1" in c.prompt for c in vote_calls)

    def test_contradiction_shifts_vote_suspicion_graph(self) -> None:
        _, client = _run_meeting(self._conflict_responder())

        # p-4 has no prior row for p-2; belief Rule 2 materialises a default
        # 0.5 then bumps it, so p-2's suspicion in p-4's ballot prompt is
        # strictly above the default.
        vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
        p4_call = next(c for c in vote_calls if "voter=p-4\n" in c.prompt)
        suspicion_line = next(
            line
            for line in p4_call.prompt.splitlines()
            if line.startswith("suspicion=")
        )
        assert _suspicion_of("p-2", suspicion_line) > _DEFAULT_TEST_SUSPICION


def _suspicion_of(player_id: str, suspicion_line: str) -> float:
    body = suspicion_line[len("suspicion=") :]
    for part in body.split(","):
        if part.startswith(f"{player_id}:"):
            return float(part.split(":")[1].split("/")[0])
    raise AssertionError(f"{player_id} not found in {suspicion_line!r}")


def _vote_prompt_suspicion(client: _ScriptedLLMClient, *, voter: str, of: str) -> float:
    """The rendered suspicion of ``of`` in ``voter``'s ballot prompt."""

    vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
    call = next(c for c in vote_calls if f"voter={voter}\n" in c.prompt)
    suspicion_line = next(
        line for line in call.prompt.splitlines() if line.startswith("suspicion=")
    )
    return _suspicion_of(of, suspicion_line)


# --- Detector precision: graduated weak-contradiction weight (Task 9.7) -----


class TestDetectorPrecisionGraduatedSuspicion:
    """Task 9.7 (DESIGN.md §5.4, §6.3 Rule 2, §4.6; audit gp-1 precision).

    The production path end-to-end: ``detect_contradictions`` over the
    final transcript -> belief Rule 2 -> the ballot-prompt suspicion
    graph. A lone weak ``alibi_vs_sighting`` (self-stated / narrow
    window) lands the subject in [0.5, 0.60) -- below the §4.6 0.60
    eject gate the meeting runs with (``skip_confidence_threshold=0.6``
    here, matching the production default), so the audited seed-3/16/47
    railroad shapes no longer auto-eject. Corroboration -- a second
    independent sighting, a strong contradiction, or a body-proximity
    prior -- still carries the subject across the gate.
    """

    def test_seed3_shape_lone_self_stated_contradiction_stays_below_gate(
        self,
    ) -> None:
        # The seed-3 audited false positive: the reporter p-1 self-states
        # an alibi (CAFETERIA) and a third party's sighting places them
        # in EAST_HALL inside the window. One weak flag: 0.5 + 0.08 =
        # 0.58, suspicious but below the 0.60 gate.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-1",
                        from_tick=100,
                        to_tick=200,
                        room="CAFETERIA",
                    ),
                ),
            },
            observations={
                "p-2": (
                    SawPlayerObservation(
                        type="saw_player",
                        subject="p-1",
                        room="EAST_HALL",
                        tick=150,
                    ),
                ),
            },
        )
        result, client = _run_meeting(responder)

        assert len(result.contradictions) == 1
        flag = result.contradictions[0]
        assert flag.kind == "alibi_vs_sighting"
        assert flag.subjects == ("p-1",)
        assert WEAK_CONTRADICTION_MARKER_PREFIX in flag.description
        assert WEAK_REASON_SELF_STATED in flag.description

        for voter in ("p-2", "p-3", "p-4"):
            suspicion = _vote_prompt_suspicion(client, voter=voter, of="p-1")
            assert suspicion == pytest.approx(0.58)
            assert _DEFAULT_TEST_SUSPICION < suspicion < 0.6

    def test_narrow_window_shape_stays_below_gate(self) -> None:
        # The narrow-window false positive: a third party's 2-tick alibi
        # claim about p-3 vs a sighting at the range edge is transit
        # noise, not a lie. Weak flag -> 0.58 < 0.60.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-3",
                        from_tick=3,
                        to_tick=4,
                        room="STORAGE",
                    ),
                ),
            },
            observations={
                "p-2": (
                    SawPlayerObservation(
                        type="saw_player", subject="p-3", room="MEDBAY", tick=3
                    ),
                ),
            },
        )
        result, client = _run_meeting(responder)

        assert len(result.contradictions) == 1
        suspicion = _vote_prompt_suspicion(client, voter="p-4", of="p-3")
        assert suspicion == pytest.approx(0.58)
        assert suspicion < 0.6

    def test_sighting_fountain_against_one_claim_lifts_once(self) -> None:
        # Task 10.1 (audit gp-2 C-C-3): two third parties sighting the
        # self-alibi'd reporter elsewhere still emit two flags, but both
        # ride the SAME alibi claim, so the lift dedups to one weak delta
        # -> 0.58 < 0.60. Pre-10.1 these summed per flag (0.66) -- the
        # fountain that let one truthful alibi rail an innocent over the
        # gate on sighting volume alone.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": "p-3", "p-3": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-1",
                        from_tick=100,
                        to_tick=200,
                        room="CAFETERIA",
                    ),
                ),
            },
            observations={
                "p-2": (
                    SawPlayerObservation(
                        type="saw_player",
                        subject="p-1",
                        room="EAST_HALL",
                        tick=150,
                    ),
                ),
                "p-3": (
                    SawPlayerObservation(
                        type="saw_player", subject="p-1", room="MEDBAY", tick=180
                    ),
                ),
            },
        )
        result, client = _run_meeting(responder)

        assert len(result.contradictions) == 2
        suspicion = _vote_prompt_suspicion(client, voter="p-4", of="p-1")
        assert suspicion == pytest.approx(0.58)
        assert suspicion < 0.6

    def test_second_signal_from_an_independent_claim_corroborates(self) -> None:
        # Corroboration still converts under the Task 10.1 dedup when the
        # second weak signal rides a DIFFERENT claim: the reporter's two
        # separate alibi claims each draw a contradicting sighting ->
        # two lift groups -> 0.5 + 0.08 + 0.08 = 0.66 >= 0.60.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": "p-3", "p-3": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-1",
                        from_tick=100,
                        to_tick=200,
                        room="CAFETERIA",
                    ),
                    AlibiClaim(
                        type="alibi",
                        subject="p-1",
                        from_tick=300,
                        to_tick=400,
                        room="STORAGE",
                    ),
                ),
            },
            observations={
                "p-2": (
                    SawPlayerObservation(
                        type="saw_player",
                        subject="p-1",
                        room="EAST_HALL",
                        tick=150,
                    ),
                ),
                "p-3": (
                    SawPlayerObservation(
                        type="saw_player", subject="p-1", room="MEDBAY", tick=350
                    ),
                ),
            },
        )
        result, client = _run_meeting(responder)

        assert len(result.contradictions) == 2
        suspicion = _vote_prompt_suspicion(client, voter="p-4", of="p-1")
        assert suspicion == pytest.approx(0.66)
        assert suspicion >= 0.6

    def test_body_proximity_prior_plus_weak_flag_crosses_gate(self) -> None:
        # The second signal can come from outside the meeting: a voter
        # whose persistent beliefs already hold a Rule-1 body-proximity
        # prior (0.5 + 0.2 = 0.7) sees the weak flag land on it ->
        # 0.78 >= 0.60, while a prior-free voter stays at 0.58 < 0.60.
        participants = (
            _participant("p-1"),
            _participant("p-2"),
            _participant("p-3"),
            _participant(
                "p-4",
                suspicion_graph=(
                    SuspicionEntry(player_id="p-1", suspicion=0.7, trust=0.5),
                ),
            ),
        )
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-1",
                        from_tick=100,
                        to_tick=200,
                        room="CAFETERIA",
                    ),
                ),
            },
            observations={
                "p-2": (
                    SawPlayerObservation(
                        type="saw_player",
                        subject="p-1",
                        room="EAST_HALL",
                        tick=150,
                    ),
                ),
            },
        )
        _, client = _run_meeting(responder, participants=participants)

        corroborated = _vote_prompt_suspicion(client, voter="p-4", of="p-1")
        assert corroborated == pytest.approx(0.78)
        assert corroborated >= 0.6

        prior_free = _vote_prompt_suspicion(client, voter="p-3", of="p-1")
        assert prior_free == pytest.approx(0.58)
        assert prior_free < 0.6

    def test_third_party_contradiction_keeps_full_weight_and_crosses(self) -> None:
        # Recall control: two third parties disagreeing about p-3 is the
        # STRONG pattern and keeps the full 0.3 delta -> 0.8 >= 0.60.
        # The graduated weight narrows precision; it does not weaken
        # strong evidence.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-3",
                        from_tick=100,
                        to_tick=200,
                        room="STORAGE",
                    ),
                ),
            },
            observations={
                "p-2": (
                    SawPlayerObservation(
                        type="saw_player",
                        subject="p-3",
                        room="CAFETERIA",
                        tick=150,
                    ),
                ),
            },
        )
        result, client = _run_meeting(responder)

        assert len(result.contradictions) == 1
        assert (
            WEAK_CONTRADICTION_MARKER_PREFIX not in result.contradictions[0].description
        )
        suspicion = _vote_prompt_suspicion(client, voter="p-4", of="p-3")
        assert suspicion == pytest.approx(0.8)
        assert suspicion >= 0.6

    def test_graph_helper_applies_graduated_weight(self) -> None:
        # Unit pin at the manager seam: a weak flag lifts a default-prior
        # subject to 0.58, a strong flag to 0.8, in the same graph.
        contradictions = (
            ContradictionRef(
                contradiction_id="c-weak",
                kind="alibi_vs_sighting",
                event_a_id="a",
                event_b_id="b",
                subjects=("p-2",),
                description=(
                    f"x {WEAK_CONTRADICTION_MARKER_PREFIX}{WEAK_REASON_SELF_STATED}]"
                ),
            ),
            ContradictionRef(
                contradiction_id="c-strong",
                kind="alibi_vs_sighting",
                event_a_id="c",
                event_b_id="d",
                subjects=("p-3",),
                description="strong third-party flag",
            ),
        )
        graph = _suspicion_graph_with_contradictions(
            voter_id="p-1",
            suspicion_graph=(),
            contradictions=contradictions,
        )

        by_id = {entry.player_id: entry.suspicion for entry in graph}
        assert by_id["p-2"] == pytest.approx(0.58)
        assert by_id["p-2"] < 0.6
        assert by_id["p-3"] == pytest.approx(0.8)
        assert by_id["p-3"] >= 0.6


# --- Self-alibi normalization ----------------------------------------------


class TestSelfAlibiNormalization:
    def test_helper_rewrites_placeholder_variants_to_speaker_id(self) -> None:
        claims: tuple[Claim, ...] = (
            AlibiClaim(
                type="alibi", subject="self", from_tick=1, to_tick=2, room="ADMIN"
            ),
            AlibiClaim(
                type="alibi", subject="p-self", from_tick=1, to_tick=2, room="ADMIN"
            ),
        )
        result = _normalize_self_alibi_subjects(claims, speaker_id="p-7")

        assert all(isinstance(c, AlibiClaim) and c.subject == "p-7" for c in result)

    def test_helper_passes_non_self_subjects_through(self) -> None:
        claims: tuple[Claim, ...] = (
            AlibiClaim(
                type="alibi", subject="p-3", from_tick=1, to_tick=2, room="ADMIN"
            ),
        )
        result = _normalize_self_alibi_subjects(claims, speaker_id="p-7")

        assert result == claims

    def test_turn_self_alibi_is_canonicalized_in_transcript(self) -> None:
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": None},
                claims_by={
                    "p-1": (
                        AlibiClaim(
                            type="alibi",
                            subject="p-self",
                            from_tick=1,
                            to_tick=2,
                            room="ADMIN",
                        ),
                    )
                },
            )
        )

        opening = result.transcript.turns[0]
        alibi = next(c for c in opening.claims if isinstance(c, AlibiClaim))
        assert alibi.subject == "p-1"


# --- Teammate firewall guards (Task 7.12) ----------------------------------


class TestTeammateGuardHelpers:
    def test_exclude_teammate_accusation_claims(self) -> None:
        claims: tuple[Claim, ...] = (
            AccusationClaim(
                type="accusation", against="p-5", confidence=0.6, reason="r"
            ),
            AccusationClaim(
                type="accusation", against="p-9", confidence=0.6, reason="r"
            ),
            CorroborationClaim(
                type="corroboration", supports="p-5", on_tick=1, reason="r"
            ),
        )
        result = exclude_teammate_accusation_claims(
            claims, fellow_impostor_ids=("p-5",)
        )

        # The accusation of teammate p-5 is dropped; the corroboration of a
        # teammate (which helps the team) is kept.
        accusation_targets = [
            c.against for c in result if isinstance(c, AccusationClaim)
        ]
        assert accusation_targets == ["p-9"]
        assert any(isinstance(c, CorroborationClaim) for c in result)

    def test_drop_teammate_statement_target(self) -> None:
        assert (
            drop_teammate_statement_target("p-5", fellow_impostor_ids=("p-5",)) is None
        )
        assert (
            drop_teammate_statement_target("p-9", fellow_impostor_ids=("p-5",)) == "p-9"
        )
        assert (
            drop_teammate_statement_target(None, fellow_impostor_ids=("p-5",)) is None
        )

    def test_coerce_teammate_ballot_to_skip(self) -> None:
        # The coerced ballot is also stripped of its now-stale reason id
        # (DESIGN.md §5.5; audit gp-3): once the vote collapses to SKIP the
        # reason id that justified the betrayal target is meaningless.
        ballot = VoteBallot(
            voter="p-4",
            target="p-5",
            confidence=0.9,
            primary_reason_id="m-1:turn-0",
            rationale_text="betrayal",
        )
        coerced = coerce_teammate_ballot_to_skip(
            ballot=ballot, fellow_impostor_ids=("p-5",)
        )

        assert coerced.target == "SKIP"
        assert coerced.primary_reason_id is None
        assert coerced.rationale_text.startswith(
            TEAMMATE_VOTE_TARGET_MARKER.format(target="p-5")
        )

    def test_coerce_leaves_non_teammate_untouched(self) -> None:
        ballot = VoteBallot(
            voter="p-4",
            target="p-9",
            confidence=0.9,
            primary_reason_id=None,
            rationale_text="legit",
        )
        assert (
            coerce_teammate_ballot_to_skip(ballot=ballot, fellow_impostor_ids=("p-5",))
            is ballot
        )


class TestTeammateGuardOnProductionPath:
    def _impostor_team(self) -> tuple[MeetingParticipant, ...]:
        # p-4 and p-5 are impostors and each other's teammate.
        return (
            _participant("p-1"),
            _participant("p-2"),
            _participant("p-3"),
            _participant("p-4", role="IMPOSTOR", fellow_impostor_ids=("p-5",)),
            _participant("p-5", role="IMPOSTOR", fellow_impostor_ids=("p-4",)),
        )

    def test_impostor_opening_accusation_of_teammate_is_dropped(self) -> None:
        # p-4 (impostor) opens and accuses teammate p-5 -> the accusation
        # is stripped, so the chain never passes the floor to p-5 and p-5 is
        # not publicly incriminated. (Since Task 10.3 the stripped opening is
        # also narration-only, so the deterministic stub burns its single
        # retry and the opening records as the fail-soft default -- the
        # firewall outcome is identical either way: no teammate accusation,
        # no floor pass.)
        trigger = MeetingTrigger(
            triggered_by="p-4", trigger_tick=1, description="p-4 reports"
        )
        result, _ = _run_meeting(
            _make_responder(accusations={"p-4": "p-5"}),
            participants=self._impostor_team(),
            trigger=trigger,
        )

        opening = result.transcript.turns[0]
        assert all(
            not (isinstance(c, AccusationClaim) and c.against == "p-5")
            for c in opening.claims
        )
        # No reply by p-5 (the chain did not pass to the teammate).
        assert all(t.speaker != "p-5" for t in result.transcript.turns[1:])

    def test_impostor_reply_accusation_of_teammate_is_dropped(self) -> None:
        # p-1 opens accusing p-4 (impostor); p-4 replies accusing teammate
        # p-5 -> dropped, chain stops, p-5 never speaks.
        result, _ = _run_meeting(
            _make_responder(accusations={"p-1": "p-4", "p-4": "p-5"}),
            participants=self._impostor_team(),
        )

        reply = result.transcript.turns[1]
        assert reply.speaker == "p-4"
        assert all(
            not (isinstance(c, AccusationClaim) and c.against == "p-5")
            for c in reply.claims
        )
        assert all(t.speaker != "p-5" for t in result.transcript.turns)

    def test_no_impostor_ejected_by_teammate_betrayal_vote(self) -> None:
        # Both impostors are told to vote the OTHER impostor; the guard
        # coerces both to SKIP so the betrayal cannot eject a teammate.
        result, _ = _run_meeting(
            _make_responder(vote_targets={"p-4": "p-5", "p-5": "p-4"}),
            participants=self._impostor_team(),
        )

        p4_ballot = next(b for b in result.ballots if b.voter == "p-4")
        p5_ballot = next(b for b in result.ballots if b.voter == "p-5")
        assert p4_ballot.target == "SKIP"
        assert p5_ballot.target == "SKIP"
        assert result.ejected_player_id not in {"p-4", "p-5"}

    def test_teammate_list_threaded_into_impostor_prompts_only(self) -> None:
        _, client = _run_meeting(_make_responder(), participants=self._impostor_team())

        for call in client.calls:
            agent_id = call.agent_id
            if agent_id in {"p-4", "p-5"}:
                assert "FELLOW_IMPOSTORS=" in call.prompt
            else:
                assert "FELLOW_IMPOSTORS=" not in call.prompt

    def test_crew_meeting_is_unaffected_by_guards(self) -> None:
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-3"},
                vote_targets={"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP", "p-4": "p-3"},
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"


# --- Teammate-perception firewall, input side (Task 9.3) -------------------


def _vote_suspicion_line(client: _ScriptedLLMClient, voter: str) -> str:
    call = next(
        c
        for c in client.calls
        if "PHASE=VOTE" in c.prompt and f"voter={voter}\n" in c.prompt
    )
    return next(
        line for line in call.prompt.splitlines() if line.startswith("suspicion=")
    )


class TestSuspicionGraphTeammateMask:
    """Task 9.3 voter-side backstop (DESIGN.md §4.7).

    ``_suspicion_graph_with_contradictions`` masks fellow-impostor edges for an
    impostor voter, mirroring the 7.12 ballot coercion on the input side: even
    if a teammate-incriminating sighting slips through perception/render, the
    impostor's ballot prompt carries no team suspicion. A no-op for crew (empty
    ``fellow_impostor_ids``) so the no-flag path stays byte-identical.
    """

    def test_crew_no_flag_path_returns_graph_unchanged(self) -> None:
        graph = (SuspicionEntry(player_id="p-2", suspicion=0.7, trust=0.3),)
        result = _suspicion_graph_with_contradictions(
            voter_id="p-1", suspicion_graph=graph, contradictions=()
        )
        assert result is graph

    def test_impostor_incoming_teammate_edge_masked_without_contradiction(
        self,
    ) -> None:
        graph = (
            SuspicionEntry(player_id="p-5", suspicion=0.9, trust=0.1),
            SuspicionEntry(player_id="p-3", suspicion=0.6, trust=0.4),
        )
        result = _suspicion_graph_with_contradictions(
            voter_id="p-4",
            suspicion_graph=graph,
            contradictions=(),
            fellow_impostor_ids=("p-5",),
        )
        # Teammate p-5 dropped; the non-teammate edge survives.
        assert [entry.player_id for entry in result] == ["p-3"]

    def test_contradiction_against_teammate_masked_for_impostor_voter(self) -> None:
        contradictions = (
            ContradictionRef(
                contradiction_id="c-team",
                kind="alibi_vs_sighting",
                event_a_id="a",
                event_b_id="b",
                subjects=("p-5",),
                description="teammate flagged",
            ),
            ContradictionRef(
                contradiction_id="c-other",
                kind="alibi_vs_sighting",
                event_a_id="c",
                event_b_id="d",
                subjects=("p-3",),
                description="other flagged",
            ),
        )
        impostor_graph = _suspicion_graph_with_contradictions(
            voter_id="p-4",
            suspicion_graph=(),
            contradictions=contradictions,
            fellow_impostor_ids=("p-5",),
        )
        # Teammate p-5 masked even though it was contradicted; p-3 lifted.
        assert all(entry.player_id != "p-5" for entry in impostor_graph)
        assert any(entry.player_id == "p-3" for entry in impostor_graph)

        # A crew voter (no teammates) sees the contradicted p-5 lifted normally.
        crew_graph = _suspicion_graph_with_contradictions(
            voter_id="p-1",
            suspicion_graph=(),
            contradictions=contradictions,
            fellow_impostor_ids=(),
        )
        assert any(entry.player_id == "p-5" for entry in crew_graph)


class TestTeammateFirewallInputSide:
    """Task 9.3 input-side firewall on the production meeting path (§4.7)."""

    def _impostor_team(self) -> tuple[MeetingParticipant, ...]:
        return (
            _participant("p-1"),
            _participant("p-2"),
            _participant("p-3"),
            _participant("p-4", role="IMPOSTOR", fellow_impostor_ids=("p-5",)),
            _participant("p-5", role="IMPOSTOR", fellow_impostor_ids=("p-4",)),
        )

    def test_impostor_voter_graph_masks_contradicted_teammate(self) -> None:
        # p-1 (crew) alibis p-5 and a DIFFERENT crew witness p-2 places p-5
        # elsewhere -> a cross-speaker alibi_vs_sighting names p-5 (the 10.10
        # same-speaker guard does not fire on two distinct authors). The
        # impostor voter p-4's ballot-prompt suspicion graph carries no p-5
        # edge; crew p-1's does.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": None},
            claims_by={
                "p-1": (
                    AlibiClaim(
                        type="alibi",
                        subject="p-5",
                        from_tick=100,
                        to_tick=200,
                        room="STORAGE",
                    ),
                ),
            },
            observations={
                "p-2": (
                    SawPlayerObservation(
                        type="saw_player",
                        subject="p-5",
                        room="CAFETERIA",
                        tick=150,
                    ),
                ),
            },
        )
        result, client = _run_meeting(responder, participants=self._impostor_team())

        assert any(
            c.kind == "alibi_vs_sighting" and "p-5" in c.subjects
            for c in result.contradictions
        )
        assert "p-5:" not in _vote_suspicion_line(client, "p-4")
        assert "p-5:" in _vote_suspicion_line(client, "p-1")

    def test_recorded_contradictions_exclude_impostor_teammate_self_sighting(
        self,
    ) -> None:
        # Pinned invariant (Task 9.3 DoD, DESIGN.md §4.7): no recorded
        # alibi_vs_sighting has a supporting sighting that is an impostor's own
        # observation of a fellow impostor (the seed-47 class). Driven by the
        # render guard: the impostor reasons from its rendered memory, and a
        # responder that can only surface what that memory shows therefore
        # cannot place the teammate at the scene.
        def _witness_memory(*, role: str, fellow: tuple[str, ...]) -> AgentMemory:
            memory = AgentMemory()
            memory.episodic.append(
                EpisodicEvent(
                    tick=0,
                    type="self_state",
                    payload={
                        "agent_id": "p-4",
                        "room": "ADMIN",
                        "role": role,
                        "pending_task_id": None,
                        "fellow_impostor_ids": fellow,
                    },
                    provenance="observed",
                )
            )
            # Witnessed teammate p-5 killing in ADMIN at tick 7.
            memory.episodic.append(
                EpisodicEvent(
                    tick=7,
                    type="saw_player",
                    payload={"player_id": "p-5", "room": "ADMIN", "action": "kill"},
                    provenance="observed",
                )
            )
            memory.episodic.append(
                EpisodicEvent(
                    tick=8,
                    type="saw_body",
                    payload={"body_id": "b", "victim_id": "p-3", "room": "ADMIN"},
                    provenance="observed",
                )
            )
            return memory

        impostor_render = render_for_prompt(
            _witness_memory(role="IMPOSTOR", fellow=("p-5",))
        )
        crew_render = render_for_prompt(_witness_memory(role="CREWMATE", fellow=()))
        # The render guard masks the teammate kill-witness row for the impostor;
        # a crewmate witness keeps it (the control below leans on that).
        assert "You witnessed p-5 kill in ADMIN" in crew_render
        assert "You witnessed p-5 kill in ADMIN" not in impostor_render

        def _responder_for(
            render: str,
        ) -> Callable[[str, type[BaseModel] | None], str]:
            def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
                if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                    speaker = _extract_marker(prompt, "agent_id=")
                    if speaker == "p-4":
                        # A real impostor can only surface what its rendered
                        # memory shows; echo the teammate sighting iff present.
                        observations: tuple[ObservationClaim, ...] = ()
                        if "You witnessed p-5 kill in ADMIN" in prompt:
                            observations = (
                                SawPlayerObservation(
                                    type="saw_player",
                                    subject="p-5",
                                    room="ADMIN",
                                    tick=7,
                                ),
                            )
                        return _turn_json(
                            speaker="p-4", accuses="p-1", observations=observations
                        )
                    if speaker == "p-1":
                        return _turn_json(speaker="p-1", accuses="p-5")
                    if speaker == "p-5":
                        return _turn_json(
                            speaker="p-5",
                            accuses=None,
                            claims=(
                                AlibiClaim(
                                    type="alibi",
                                    subject="p-5",
                                    from_tick=5,
                                    to_tick=9,
                                    room="CAFETERIA",
                                ),
                            ),
                        )
                    return _turn_json(speaker=speaker, accuses=None)
                if "PHASE=VOTE" in prompt:
                    return _vote_json(
                        voter=_extract_marker(prompt, "voter="), target="SKIP"
                    )
                raise AssertionError(f"unrecognised prompt: {prompt!r}")

            return _responder

        def _participants(render: str) -> tuple[MeetingParticipant, ...]:
            return (
                _participant("p-1"),
                _participant("p-2"),
                _participant("p-3"),
                MeetingParticipant(
                    agent_id="p-4",
                    role="IMPOSTOR",
                    rendered_memory=render,
                    suspicion_graph=(),
                    fellow_impostor_ids=("p-5",),
                ),
                _participant("p-5", role="IMPOSTOR", fellow_impostor_ids=("p-4",)),
            )

        trigger = MeetingTrigger(
            triggered_by="p-4", trigger_tick=8, description="p-4 reports"
        )

        # Guarded render -> p-4 cannot surface the teammate sighting -> no
        # alibi_vs_sighting names the teammate.
        guarded_result, _ = _run_meeting(
            _responder_for(impostor_render),
            participants=_participants(impostor_render),
            trigger=trigger,
        )
        assert not any(
            c.kind == "alibi_vs_sighting" and "p-5" in c.subjects
            for c in guarded_result.contradictions
        )

        # Control: the same meeting flow with the UNMASKED render DOES record
        # the team flag -- proving the absence above is the render guard, not a
        # vacuous test (the manager does not strip turn observations).
        control_result, _ = _run_meeting(
            _responder_for(crew_render),
            participants=_participants(crew_render),
            trigger=trigger,
        )
        assert any(
            c.kind == "alibi_vs_sighting" and "p-5" in c.subjects
            for c in control_result.contradictions
        )


# --- Fail-soft on a malformed turn (Task 7.10) -----------------------------


class TestTurnFailSoft:
    def test_single_malformed_turn_degrades_and_meeting_resolves(self) -> None:
        # The opening returns unparseable JSON; it degrades to a default
        # opening turn and the meeting still reaches a vote + resolution.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt:
                return "{ this is not valid turn json"
            if "PHASE=TURN" in prompt:
                return _turn_json(speaker=_extract_marker(prompt, "agent_id="))
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")

        result, _ = _run_meeting(_responder)

        opening = result.transcript.turns[0]
        assert opening.free_text == DEFAULT_TURN_FREE_TEXT
        assert result.outcome == "SKIPPED"

    def test_reversed_alibi_turn_fails_soft(self) -> None:
        # An AlibiClaim with a reversed (non-chronological) range fails
        # schema validation; the turn degrades rather than aborting.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt:
                speaker = _extract_marker(prompt, "agent_id=")
                return (
                    '{"turn_id":"x","turn_index":0,"speaker":"' + speaker + '",'
                    '"turn_kind":"opening","reply_to":null,"observations":[],'
                    '"claims":[{"type":"alibi","subject":"' + speaker + '",'
                    '"from_tick":410,"to_tick":380,"room":"ADMIN","evidence":[]}],'
                    '"free_text":"reversed"}'
                )
            if "PHASE=TURN" in prompt:
                return _turn_json(speaker=_extract_marker(prompt, "agent_id="))
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")

        result, _ = _run_meeting(_responder)

        assert result.transcript.turns[0].free_text == DEFAULT_TURN_FREE_TEXT
        assert result.outcome == "SKIPPED"


# --- Provider timeout vs deadline ------------------------------------------


class TestProviderTimeoutDistinctFromDeadline:
    @dataclass
    class _ProviderTimeoutClient:
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

    def test_provider_timeout_in_opening_propagates(self) -> None:
        manager = _make_manager(llm_client=self._ProviderTimeoutClient())
        with pytest.raises(LLMProviderError):
            _run(
                manager.run(
                    meeting_id="m",
                    trigger=_default_trigger(),
                    participants=_crew_participants(),
                )
            )

    def test_provider_timeout_in_vote_propagates(self) -> None:
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
                if "PHASE=VOTE" in prompt:
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

        manager = _make_manager(llm_client=_PhaseSpecificClient())
        with pytest.raises(LLMProviderError):
            _run(
                manager.run(
                    meeting_id="m",
                    trigger=_default_trigger(),
                    participants=_crew_participants(),
                )
            )

    def test_meeting_deadline_still_defaults_when_inner_does_not_raise(self) -> None:
        # The legitimate deadline-expiry path (LLM just slow) still produces
        # the default response rather than raising.
        async def _slow(prompt: str) -> str:
            await asyncio.sleep(1.0)
            return _turn_json(speaker="never")

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
                if "PHASE=OPENING" in prompt:
                    text = await _slow(prompt)
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

        manager = _make_manager(
            llm_client=_SleepingClient(),
            deadlines=MeetingDeadlines(turn_seconds=0.01, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.transcript.turns[0].free_text == DEFAULT_TURN_FREE_TEXT


# --- Engine independence ---------------------------------------------------


class TestEngineIndependence:
    def test_manager_module_does_not_import_engine(self) -> None:
        source = Path("meetings/manager.py").read_text(encoding="utf-8")
        assert "import engine" not in source
        assert "from engine" not in source

    def test_run_returns_pure_dto(self) -> None:
        result, _ = _run_meeting(_make_responder())
        assert isinstance(result, MeetingResult)
        # Re-validate via the schema: a pure, engine-free payload.
        assert MeetingResult.model_validate(result.model_dump(mode="json")) == result


# --- Fake provider interop -------------------------------------------------


class TestFakeProviderInterop:
    def test_meeting_runs_end_to_end_with_fake_provider(self) -> None:
        manager = _make_manager(llm_client=FakeProvider())
        result = _run(
            manager.run(
                meeting_id="m-fake",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )
        # FakeProvider emits an accusation-free opening -> chain is just the
        # opening, votes normalise to SKIP -> SKIPPED.
        assert result.outcome == "SKIPPED"
        assert [t.turn_kind for t in result.transcript.turns] == ["opening"]

    def test_two_runs_with_fake_provider_are_byte_identical(self) -> None:
        def _once() -> MeetingResult:
            manager = _make_manager(llm_client=FakeProvider())
            return _run(
                manager.run(
                    meeting_id="m-fake",
                    trigger=_default_trigger(),
                    participants=_crew_participants(),
                )
            )

        assert _once().model_dump_json() == _once().model_dump_json()


# --- Participant order canonicalised ---------------------------------------


class TestParticipantOrderCanonicalised:
    def test_outcome_is_independent_of_input_order(self) -> None:
        targets = {"p-1": "p-3", "p-2": "p-3", "p-3": "SKIP", "p-4": "p-3"}
        forward, _ = _run_meeting(
            _make_responder(vote_targets=targets), participants=_crew_participants()
        )
        reversed_participants = tuple(reversed(_crew_participants()))
        backward, _ = _run_meeting(
            _make_responder(vote_targets=targets), participants=reversed_participants
        )

        assert forward.outcome == backward.outcome == "EJECTED"
        assert forward.ejected_player_id == backward.ejected_player_id == "p-3"

    def test_turns_are_canonically_ordered_regardless_of_input(self) -> None:
        _, _ = _run_meeting(
            _make_responder(), participants=tuple(reversed(_crew_participants()))
        )
        result, _ = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": None}),
            participants=tuple(reversed(_crew_participants())),
        )

        assert is_canonically_ordered(result.transcript.turns)


# --- Invalid ballot target normalised --------------------------------------


class TestInvalidBallotTargetNormalised:
    def test_hallucinated_target_is_normalised_to_skip(self) -> None:
        result, _ = _run_meeting(_make_responder(vote_targets={"p-1": "p-99"}))

        p1 = next(b for b in result.ballots if b.voter == "p-1")
        assert p1.target == "SKIP"
        assert p1.rationale_text.startswith(
            INVALID_VOTE_TARGET_MARKER.format(target="p-99")
        )

    def test_voter_voting_for_self_is_normalised_to_skip(self) -> None:
        # p-1 is excluded from its own candidate set, so a self-vote is an
        # invalid target.
        result, _ = _run_meeting(_make_responder(vote_targets={"p-1": "p-1"}))

        p1 = next(b for b in result.ballots if b.voter == "p-1")
        assert p1.target == "SKIP"

    def test_valid_target_passes_through(self) -> None:
        result, _ = _run_meeting(_make_responder(vote_targets={"p-1": "p-3"}))

        p1 = next(b for b in result.ballots if b.voter == "p-1")
        assert p1.target == "p-3"


# --- Invalid accusation target dropped (qwen3.5:9b "imp-2" hallucination) -----


class TestInvalidAccusationTargetDropped:
    """Accusations naming a non-living target are dropped before recording.

    qwen3.5:9b occasionally hallucinates an accusation target id (e.g.
    ``"imp-2"``) that names no living player. The reactive chain already
    terminates on such a target, but recording the claim crashed the §11.3
    accusation-calibration metric (it resolves every target's role); the
    per-turn guard drops it and preserves the original on ``free_text``,
    mirroring the ballot-target normalisation.
    """

    def test_unit_drops_only_the_invalid_accusation(self) -> None:
        claims: tuple[Claim, ...] = (
            AccusationClaim(
                type="accusation", against="imp-2", confidence=0.9, reason="r"
            ),
            AccusationClaim(
                type="accusation", against="p-3", confidence=0.6, reason="r"
            ),
            CorroborationClaim(
                type="corroboration", supports="p-3", on_tick=1, reason="r"
            ),
        )
        surviving, markers = _drop_non_roster_claims(
            claims, living_ids=frozenset({"p-1", "p-2", "p-3", "p-4"})
        )

        # The hallucinated 'imp-2' accusation is dropped; the valid 'p-3'
        # accusation and the (valid-supports) corroboration survive in order.
        assert markers == (INVALID_ACCUSATION_TARGET_MARKER.format(target="imp-2"),)
        accusation_targets = [
            c.against for c in surviving if isinstance(c, AccusationClaim)
        ]
        assert accusation_targets == ["p-3"]
        assert any(isinstance(c, CorroborationClaim) for c in surviving)

    def test_unit_no_op_when_every_target_living(self) -> None:
        claims: tuple[Claim, ...] = (
            AccusationClaim(
                type="accusation", against="p-3", confidence=0.6, reason="r"
            ),
        )
        surviving, markers = _drop_non_roster_claims(
            claims, living_ids=frozenset({"p-1", "p-2", "p-3", "p-4"})
        )
        assert markers == ()
        assert surviving == claims

    def test_hallucinated_opening_accusation_retries_then_degrades(self) -> None:
        # p-1 (the opener) accuses a non-living id; the accusation is dropped
        # before the turn is recorded, which leaves the opening with neither
        # an accusation nor an unsure declaration -- the Task 10.3 opening
        # validation treats that exactly like a parse failure, so the
        # deterministic stub burns its single retry. Both attempts PARSED,
        # so the Task 10.6 fail-soft degrades to an UNSURE opening built
        # from the last attempt (audit gp-5 H-H-2: the full default cost
        # the whole meeting) instead of the placeholder default.
        result, client = _run_meeting(_make_responder(accusations={"p-1": "imp-2"}))

        opening = result.transcript.turns[0]
        assert opening.speaker == "p-1"
        assert opening.free_text.startswith(OPENING_UNSURE_DEGRADE_MARKER)
        assert OPENING_UNSURE_MARKER in opening.free_text.lower()
        assert opening.free_text != DEFAULT_TURN_FREE_TEXT
        assert not any(isinstance(c, AccusationClaim) for c in opening.claims)
        # Exactly one retry: two opening attempts, then the degrade.
        opening_calls = [c for c in client.calls if "PHASE=OPENING" in c.prompt]
        assert len(opening_calls) == 2
        # The retry prompt states the failure reason: it names the dropped
        # dead target and demands a LIVING target or unsure (gp-5 H-H-1 --
        # the byte-identical re-ask was provably a no-op at temp 0.4).
        retry_prompt = opening_calls[1].prompt
        assert OPENING_RETRY_FEEDBACK_HEADER in retry_prompt
        assert "'imp-2'" in retry_prompt
        assert "LIVING" in retry_prompt
        assert OPENING_RETRY_FEEDBACK_DEMAND in retry_prompt
        assert OPENING_RETRY_FEEDBACK_HEADER not in opening_calls[0].prompt
        # No recorded accusation names a non-living id, so the §11.3 accusation
        # metrics can resolve every target's role (the gp surfaced by seed 24).
        all_targets = {
            c.against
            for turn in result.transcript.turns
            for c in turn.claims
            if isinstance(c, AccusationClaim)
        }
        assert "imp-2" not in all_targets

    def test_hallucinated_opening_accusation_with_unsure_records_marked(self) -> None:
        # The opener accuses a non-living id but ALSO declares unsure in its
        # free_text: the drop+marker shape records on the first attempt (no
        # retry), preserving the original target for replay analysis -- the
        # pre-10.3 marker pin, now reachable via the unsure declaration.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                speaker = _extract_marker(prompt, "agent_id=")
                return _turn_json(
                    speaker=speaker,
                    accuses="imp-2" if speaker == "p-1" else None,
                    free_text=f"unsure, but imp-2 felt off to {speaker}",
                )
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")

        result, client = _run_meeting(_responder)

        opening = result.transcript.turns[0]
        assert opening.speaker == "p-1"
        assert not any(isinstance(c, AccusationClaim) for c in opening.claims)
        assert opening.free_text.startswith(
            INVALID_ACCUSATION_TARGET_MARKER.format(target="imp-2")
        )
        # Recorded on the first attempt: the unsure declaration satisfies the
        # opening validation, so no retry fires.
        opening_calls = [c for c in client.calls if "PHASE=OPENING" in c.prompt]
        assert len(opening_calls) == 1

    def test_valid_opening_accusation_passes_through(self) -> None:
        result, _ = _run_meeting(_make_responder(accusations={"p-1": "p-3"}))

        opening = result.transcript.turns[0]
        targets = [c.against for c in opening.claims if isinstance(c, AccusationClaim)]
        assert targets == ["p-3"]
        assert not opening.free_text.startswith("[invalid accusation target")


class TestOpeningUnsureGuard:
    """``_opening_takes_position`` gates the unsure marker on free_text STRUCTURE.

    Task 10.12 (audit 2026-06-13-1816 H-H-1): the bare substring match accepted
    a 5266-char reasoning-relocation husk (claims=[] observations=[],
    incidentally containing "unsure") as a deliberate position, so the 10.3
    retry never fired (seed-30 m1, all 7 ballots SKIP). The structural guard
    rejects only the hollow relocation SHAPE; a short genuine "unsure", or one
    carrying observations / claims, still passes.
    """

    _OBSERVATION = SawPlayerObservation(
        type="saw_player", tick=10, subject="p-3", room="CAFETERIA"
    )

    def test_short_unsure_opening_passes(self) -> None:
        assert _opening_takes_position(
            claims=(),
            observations=(),
            free_text="I'm genuinely unsure who to accuse this round.",
        )

    def test_hollow_relocation_husk_with_unsure_is_rejected(self) -> None:
        # The seed-30 m1 shape: free_text far above the p95 with empty claims
        # AND empty observations, incidentally containing "unsure".
        husk = "chain of thought ... " * 300 + " ... unsure ... "
        assert len(husk) > OPENING_UNSURE_MAX_FREE_TEXT_CHARS
        assert not _opening_takes_position(
            claims=(),
            observations=(),
            free_text=husk,
        )

    def test_seed30_5266_char_hollow_opening_no_longer_passes(self) -> None:
        # The byte-verified seed-30 m1 tail: 5266 chars, claims=[] observations=[],
        # containing "unsure". Must route to the retry, not a silent valid-unsure.
        free_text = "x" * 5000 + " unsure " + "y" * 258
        assert len(free_text) == 5266
        assert not _opening_takes_position(
            claims=(), observations=(), free_text=free_text
        )

    def test_long_unsure_opening_with_observations_still_passes(self) -> None:
        # Far above the bound, but it carries observations -- a real body report
        # that declined to accuse, NOT a hollow relocation.
        long_text = "Here is my detailed account ... " * 50 + " unsure"
        assert len(long_text) > OPENING_UNSURE_MAX_FREE_TEXT_CHARS
        assert _opening_takes_position(
            claims=(),
            observations=(self._OBSERVATION,),
            free_text=long_text,
        )

    def test_long_unsure_opening_with_surviving_claims_still_passes(self) -> None:
        long_text = "Here is my detailed account ... " * 50 + " unsure"
        claims: tuple[Claim, ...] = (
            CorroborationClaim(
                type="corroboration", supports="p-2", on_tick=5, reason="r"
            ),
        )
        assert _opening_takes_position(
            claims=claims,
            observations=(),
            free_text=long_text,
        )

    def test_accusation_passes_regardless_of_length_or_marker(self) -> None:
        claims: tuple[Claim, ...] = (
            AccusationClaim(
                type="accusation", against="p-3", confidence=0.6, reason="r"
            ),
        )
        assert _opening_takes_position(
            claims=claims,
            observations=(),
            free_text="x" * (OPENING_UNSURE_MAX_FREE_TEXT_CHARS + 1),
        )

    def test_no_marker_and_no_accusation_is_no_position(self) -> None:
        assert not _opening_takes_position(
            claims=(),
            observations=(),
            free_text="Just narrating what I saw, no commitment.",
        )


# --- primary_reason_id integrity (DESIGN.md §5.5; audit gp-3) ----------------


class TestBallotReasonIdIntegrity:
    """``_collect_one_ballot`` validates ``primary_reason_id`` against the
    transcript's turn-id set: a canonical id passes, a recoverable
    ``:turn-{k}`` suffix form normalizes to the canonical id, and an
    unresolvable id is nulled with :data:`INVALID_REASON_ID_MARKER`.

    The default meeting (no opening accusation) records exactly one turn,
    the opening at ``m-1:turn-0``, so that is the only valid reason id.
    """

    def test_canonical_reason_id_passes_through(self) -> None:
        result, _ = _run_meeting(_make_responder(vote_reason_ids={"p-2": "m-1:turn-0"}))

        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_id == "m-1:turn-0"
        assert not p2.rationale_text.startswith("[invalid primary_reason_id")

    def test_suffix_form_normalizes_to_canonical(self) -> None:
        # A wrong meeting prefix with a real ``:turn-0`` ordinal (the 7B
        # model echoing a short / wrong-prefix id) re-anchors to the
        # canonical turn id rather than being nulled.
        result, _ = _run_meeting(
            _make_responder(vote_reason_ids={"p-2": "meeting-1:turn-0"})
        )

        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_id == "m-1:turn-0"
        assert not p2.rationale_text.startswith("[invalid primary_reason_id")

    def test_dangling_reason_id_is_nulled_with_marker(self) -> None:
        # A hallucinated ordinal (no turn-14 in a one-turn meeting) is
        # nulled, never guessed, with the audit marker prefixed.
        result, _ = _run_meeting(
            _make_responder(vote_reason_ids={"p-2": "m-3:turn-14"})
        )

        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_id is None
        assert p2.rationale_text.startswith(
            INVALID_REASON_ID_MARKER.format(reason_id="m-3:turn-14")
        )

    def test_hardcoded_prompt_example_is_nulled(self) -> None:
        # The old hardcoded example `m-7:turn-4` (copied verbatim by the
        # model across meetings) has no matching ordinal here and is nulled.
        result, _ = _run_meeting(_make_responder(vote_reason_ids={"p-2": "m-7:turn-4"}))

        p2 = next(b for b in result.ballots if b.voter == "p-2")
        assert p2.primary_reason_id is None
        assert p2.rationale_text.startswith(
            INVALID_REASON_ID_MARKER.format(reason_id="m-7:turn-4")
        )

    def test_coercion_nulls_stale_reason_id_on_production_path(self) -> None:
        # An impostor voting a teammate WITH a reason id: the 7.12 coercion
        # collapses the ballot to SKIP and nulls the now-stale reason id end
        # to end (DESIGN.md §5.5; audit gp-3 seed-3 repro).
        participants = (
            _participant("p-1"),
            _participant("p-2"),
            _participant("p-3"),
            _participant("p-4", role="IMPOSTOR", fellow_impostor_ids=("p-5",)),
            _participant("p-5", role="IMPOSTOR", fellow_impostor_ids=("p-4",)),
        )
        result, _ = _run_meeting(
            _make_responder(
                vote_targets={"p-4": "p-5"},
                vote_reason_ids={"p-4": "m-1:turn-0"},
            ),
            participants=participants,
        )

        p4 = next(b for b in result.ballots if b.voter == "p-4")
        assert p4.target == "SKIP"
        assert p4.primary_reason_id is None
        assert p4.rationale_text.startswith(
            TEAMMATE_VOTE_TARGET_MARKER.format(target="p-5")
        )


# --- Confidence threshold enforcement --------------------------------------


class TestConfidenceThreshold:
    def _vote_with_confidence(
        self, target: str, confidence: float
    ) -> Callable[[str, type[BaseModel] | None], str]:
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                return _turn_json(speaker=_extract_marker(prompt, "agent_id="))
            voter = _extract_marker(prompt, "voter=")
            # Everyone votes the target so it has a strict plurality.
            return _vote_json(voter=voter, target=target, confidence=confidence)

        return _responder

    def test_low_confidence_plurality_skips_not_ejects(self) -> None:
        result, _ = _run_meeting(
            self._vote_with_confidence("p-3", 0.4), skip_confidence_threshold=0.6
        )
        assert result.outcome == "SKIPPED"

    def test_confidence_above_threshold_ejects(self) -> None:
        result, _ = _run_meeting(
            self._vote_with_confidence("p-3", 0.8), skip_confidence_threshold=0.6
        )
        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-3"

    def test_threshold_is_inclusive_at_cutoff(self) -> None:
        result, _ = _run_meeting(
            self._vote_with_confidence("p-3", 0.6), skip_confidence_threshold=0.6
        )
        assert result.outcome == "EJECTED"


# --- Negative deadlines rejected -------------------------------------------


class TestDeadlineValidation:
    def test_negative_turn_deadline_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="turn_seconds"):
            _make_manager(
                llm_client=_ScriptedLLMClient(_make_responder()),
                deadlines=MeetingDeadlines(turn_seconds=-1.0),
            )

    def test_negative_vote_deadline_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="vote_seconds"):
            _make_manager(
                llm_client=_ScriptedLLMClient(_make_responder()),
                deadlines=MeetingDeadlines(vote_seconds=-1.0),
            )

    def test_zero_deadline_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="turn_seconds"):
            _make_manager(
                llm_client=_ScriptedLLMClient(_make_responder()),
                deadlines=MeetingDeadlines(turn_seconds=0.0),
            )

    def test_none_deadline_is_accepted_for_headless_mode(self) -> None:
        result, _ = _run_meeting(
            _make_responder(),
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        assert isinstance(result, MeetingResult)


# --- Defaults surfaced + opening retry (audit gp-2) ------------------------


@dataclass
class _OpeningValidationClient:
    """Returns invalid turn JSON for the first ``invalid_opening_attempts``
    opening calls, then a valid turn; replies/opt-ins and votes are valid.

    Unlike :class:`_ScriptedLLMClient` it does NOT self-validate, so the
    manager's own ``MeetingTurn.model_validate_json`` raises the
    ``ValidationError`` -> default (the real-provider parse-failure path that
    deadline-free headless recording can still hit -- audit gp-2).
    """

    invalid_opening_attempts: int
    opening_calls: int = 0

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
        if "PHASE=OPENING" in prompt:
            self.opening_calls += 1
            text = (
                "{}"  # missing required fields -> MeetingTurn validation fails
                if self.opening_calls <= self.invalid_opening_attempts
                else _turn_json(speaker=_extract_marker(prompt, "agent_id="))
            )
        elif "PHASE=TURN" in prompt:
            text = _turn_json(speaker=_extract_marker(prompt, "agent_id="))
        else:  # PHASE=VOTE
            text = _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "opening-validation",
        )


@dataclass
class _ProviderRaisesOnOpeningClient:
    """Mimics a REAL provider: ``complete()`` validates internally and RAISES a
    ``ValidationError`` carrying ``LLMCallFailure`` metadata on the first
    ``raise_attempts`` openings (the Anthropic/Ollama ``_attach_parse_failure``
    pattern), so the recording client never logs the burned call and its spend
    would be lost unless surfaced. Later openings, replies/opt-ins and votes are
    valid. ``raise_attempts`` defaults large enough to fail every opening
    attempt (so the opening defaults); set it to 1 to recover on the retry.
    """

    input_tokens: int = 123
    raise_attempts: int = 999
    raised: int = 0

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
        if "PHASE=OPENING" in prompt and self.raised < self.raise_attempts:
            self.raised += 1
            try:
                MeetingTurn.model_validate_json("{}")
            except ValidationError as exc:
                _attach_parse_failure(
                    exc,
                    LLMCallFailure(
                        model="qwen2.5:7b-instruct",
                        prompt_length=len(prompt),
                        raw_response="not valid turn json",
                        input_tokens=self.input_tokens,
                        output_tokens=7,
                        cost_usd=0.0,
                        error_type="ValidationError",
                        error_message="bad turn",
                    ),
                )
                raise
            raise AssertionError(
                "model_validate_json('{}') must raise"
            )  # pragma: no cover
        if "PHASE=VOTE" in prompt:
            text = _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
        else:
            text = _turn_json(speaker=_extract_marker(prompt, "agent_id="))
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "provider-raises",
        )


@dataclass
class _ReplyValidationClient:
    """Valid opening that accuses p-3, then invalid JSON for the reply turn.

    Exercises a NON-opening default: only the opening retries (audit gp-2), so
    the reply defaults after a single attempt.
    """

    reply_calls: int = 0

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
        if "PHASE=OPENING" in prompt:
            text = _turn_json(
                speaker=_extract_marker(prompt, "agent_id="), accuses="p-3"
            )
        elif "PHASE=TURN" in prompt:
            self.reply_calls += 1
            text = "{}"  # invalid -> the reply defaults (not retried)
        else:  # PHASE=VOTE
            text = _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "reply-validation",
        )


@dataclass
class _SleepOnPhaseClient:
    """Sleeps (forcing a deadline miss) on whichever phase marker is set."""

    sleep_phase: str

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
        if self.sleep_phase in prompt:
            await asyncio.sleep(1.0)
        text = _make_responder()(prompt, schema)
        if schema is not None:
            schema.model_validate_json(text)
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "sleep",
        )


class TestDefaultsSurfacedAndOpeningRetry:
    def test_opening_retries_once_and_recovers_before_defaulting(self) -> None:
        # First opening attempt is invalid; the single retry succeeds, so the
        # opening is the real turn and NO default fires.
        client = _OpeningValidationClient(invalid_opening_attempts=1)
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        opening = result.transcript.turns[0]
        assert opening.turn_kind == "opening"
        assert opening.free_text != DEFAULT_TURN_FREE_TEXT
        # Attempted twice: the first (invalid) + the recovering retry.
        assert client.opening_calls == 2
        assert manager.defaulted_calls == ()

    def test_opening_defaults_after_retry_and_surfaces_validation(self) -> None:
        # Both opening attempts are invalid -> the opening defaults after the
        # single retry, and the fired default is surfaced for the orchestrator.
        client = _OpeningValidationClient(invalid_opening_attempts=2)
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.transcript.turns[0].free_text == DEFAULT_TURN_FREE_TEXT
        # Retried once before defaulting: exactly two attempts.
        assert client.opening_calls == 2
        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "opening"
        assert default.agent_id == "p-1"
        assert default.trigger == "validation"
        assert default.turn_index == 0

    def test_provider_validation_default_carries_parse_failure_spend(self) -> None:
        # A real provider raises (with metadata) before the recording client can
        # log the call, so the surfaced default must carry that spend -- one
        # entry per burned attempt (the opening is tried twice).
        client = _ProviderRaisesOnOpeningClient()
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.transcript.turns[0].free_text == DEFAULT_TURN_FREE_TEXT
        assert client.raised == 2  # opening attempted twice (retry)
        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "opening"
        assert default.trigger == "validation"
        # Both burned provider calls' real spend is preserved, not zeroed.
        assert len(default.parse_failures) == 2
        assert all(f.model == "qwen2.5:7b-instruct" for f in default.parse_failures)
        assert all(f.input_tokens == 123 for f in default.parse_failures)
        # The deterministic-retry shape (Task 9.10, audit gp-4): the retry of
        # an unchanged prompt against a deterministic provider regenerates the
        # SAME failing response, so the two carried failures are byte-equal —
        # the manager surfaces every burned attempt faithfully, and
        # ``ReplayLog.record_failed_call`` collapses the byte-identical write
        # so a defaulted turn whose parse failed records exactly ONE
        # failed_call row (seeds 8/36/39 no longer double-count).
        assert default.parse_failures[0] == default.parse_failures[1]

    def test_recovered_failure_surfaced_when_retry_succeeds(self) -> None:
        # First opening attempt raises (provider-side); the retry parses, so the
        # turn is NOT a default -- but the burned first attempt's spend would be
        # lost unless surfaced via recovered_call_failures.
        client = _ProviderRaisesOnOpeningClient(raise_attempts=1)
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        # Recovered on the retry: a real opening turn, no default fired.
        assert result.transcript.turns[0].free_text != DEFAULT_TURN_FREE_TEXT
        assert client.raised == 1
        assert manager.defaulted_calls == ()
        # The burned first attempt's spend is surfaced for the orchestrator.
        assert len(manager.recovered_call_failures) == 1
        assert manager.recovered_call_failures[0].model == "qwen2.5:7b-instruct"
        assert manager.recovered_call_failures[0].input_tokens == 123

    def test_clean_run_surfaces_no_recovered_failures(self) -> None:
        # The happy path (no retries needed) surfaces nothing.
        manager = _make_manager(
            llm_client=_ScriptedLLMClient(_make_responder()),
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )
        assert manager.recovered_call_failures == ()

    def test_manager_side_validation_default_carries_no_parse_failure(self) -> None:
        # When the provider RETURNS invalid text (not raises), the recording
        # client already logged the spend, so the default carries no
        # parse_failure (the orchestrator writes a zero-spend marker -> no
        # double-count).
        manager = _make_manager(
            llm_client=_OpeningValidationClient(invalid_opening_attempts=2),
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert len(manager.defaulted_calls) == 1
        assert manager.defaulted_calls[0].parse_failures == ()

    def test_reply_default_is_surfaced_and_not_retried(self) -> None:
        client = _ReplyValidationClient()
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        # opening (p-1 -> p-3) then a defaulted reply by p-3.
        assert [t.turn_kind for t in result.transcript.turns] == ["opening", "reply"]
        assert result.transcript.turns[1].free_text == DEFAULT_TURN_FREE_TEXT
        # Only the opening retries; the reply is attempted exactly once.
        assert client.reply_calls == 1
        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "reply"
        assert default.agent_id == "p-3"
        assert default.trigger == "validation"
        assert default.turn_index == 1

    def test_missed_turn_deadline_surfaces_deadline_trigger(self) -> None:
        manager = _make_manager(
            llm_client=_SleepOnPhaseClient(sleep_phase="PHASE=OPENING"),
            deadlines=MeetingDeadlines(turn_seconds=0.01, vote_seconds=None),
        )
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "opening"
        assert default.trigger == "deadline"
        assert default.turn_index == 0

    def test_missed_vote_deadline_surfaces_each_default(self) -> None:
        manager = _make_manager(
            llm_client=_SleepOnPhaseClient(sleep_phase="PHASE=VOTE"),
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=0.01),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        votes = manager.defaulted_calls
        # One per living participant (the opening is accusation-free, so the
        # chain is just the opening turn -> 4 ballots).
        assert len(votes) == 4
        assert all(v.phase == "vote" for v in votes)
        assert all(v.trigger == "deadline" for v in votes)
        assert all(v.turn_index is None for v in votes)
        assert sorted(v.agent_id for v in votes) == ["p-1", "p-2", "p-3", "p-4"]

    def test_defaulted_vote_rendered_max_is_rounded_to_prompt_precision(self) -> None:
        # Task 10.12 (audit H-H-2): the persisted §4.6 max must match the
        # 2-decimal precision the vote_ballot.j2 line renders and
        # parse_rendered_max_suspicion recovers, so a defaulted ballot near the
        # gate classifies IDENTICALLY whether read from the persisted field or a
        # logged prompt. A raw 0.596 renders as **0.60** (-> MUST-vote); the
        # persisted value must be 0.60, not the raw 0.596 (which would read
        # MUST-skip and split the two telemetry surfaces).
        participants = (
            _participant(
                "p-1",
                suspicion_graph=(
                    SuspicionEntry(player_id="p-2", suspicion=0.596, trust=0.5),
                ),
            ),
            _participant("p-2"),
            _participant("p-3"),
            _participant("p-4"),
        )
        manager = _make_manager(
            llm_client=_SleepOnPhaseClient(sleep_phase="PHASE=VOTE"),
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=0.01),
        )
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=participants,
            )
        )

        p1_vote = next(
            v
            for v in manager.defaulted_calls
            if v.phase == "vote" and v.agent_id == "p-1"
        )
        assert p1_vote.rendered_vote_max == 0.60
        # The other voters hold no row over a candidate -> rendered max 0.00.
        p2_vote = next(
            v
            for v in manager.defaulted_calls
            if v.phase == "vote" and v.agent_id == "p-2"
        )
        assert p2_vote.rendered_vote_max == 0.0

    def test_defaulted_calls_reset_between_runs(self) -> None:
        # The manager is reused across a game's meetings, so its default ledger
        # must reset each run. ``invalid_opening_attempts=2`` makes run 1's
        # opening (calls 1-2) default; run 2's opening (call 3) is valid, so a
        # stale entry would only survive if the ledger were not reset.
        client = _OpeningValidationClient(invalid_opening_attempts=2)
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )
        after_first_run = manager.defaulted_calls
        assert len(after_first_run) == 1  # run 1 defaulted
        assert after_first_run[0].phase == "opening"

        _run(
            manager.run(
                meeting_id="m-2",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )
        assert manager.defaulted_calls == ()  # run 2 clean -> ledger reset


# --- Opening accuse-or-unsure validation (Task 10.3, audit gp-9) ------------


@dataclass
class _ScriptedOpeningsClient:
    """Returns the scripted opening payloads in order (repeating the last);
    replies / opt-ins and votes are standard valid stubs.

    Unlike :class:`_OpeningValidationClient` every payload here is
    schema-VALID: the scripted shapes exercise the Task 10.3 opening
    CONTENT validation (accuse-or-declare-unsure), not the parse path.
    """

    opening_payloads: tuple[str, ...]
    opening_calls: int = 0
    opening_prompts: list[str] = field(default_factory=list)

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
        if "PHASE=OPENING" in prompt:
            index = min(self.opening_calls, len(self.opening_payloads) - 1)
            self.opening_calls += 1
            self.opening_prompts.append(prompt)
            text = self.opening_payloads[index]
        elif "PHASE=TURN" in prompt:
            text = _turn_json(speaker=_extract_marker(prompt, "agent_id="))
        else:  # PHASE=VOTE
            text = _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "scripted-openings",
        )


def _run_with_openings(
    *payloads: str,
) -> tuple[MeetingResult, _ScriptedOpeningsClient, MeetingManager]:
    client = _ScriptedOpeningsClient(opening_payloads=payloads)
    manager = _make_manager(
        llm_client=client,
        deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
    )
    result = _run(
        manager.run(
            meeting_id="m-1",
            trigger=_default_trigger(),
            participants=_crew_participants(),
        )
    )
    return result, client, manager


class TestOpeningAccuseOrUnsureValidation:
    """Task 10.3 (DESIGN.md §5.2 PHASE 1; audit gp-9 H-H-1).

    A narration-only opening -- recorded claims carry no accusation, model
    free_text carries no "unsure" declaration -- killed the chain on turn 0
    in 5 of 76 audited meetings. The manager now treats it as a validation
    failure through the EXISTING gp-2 single-retry path: one retry, then
    the standing fail-soft default. Replies / opt-ins are never
    content-validated (a defensive reply is a legitimate terminator).
    """

    _NARRATION = "I was in MEDBAY doing wiring, then walked to CAFETERIA."

    def test_unsure_marker_literal_is_pinned(self) -> None:
        # The opening templates instruct the model to write this exact word;
        # the manager matches it case-insensitively. A drive-by change here
        # silently un-aligns prompt and validation.
        assert OPENING_UNSURE_MARKER == "unsure"

    def test_narration_only_opening_retries_once_and_recovers(self) -> None:
        # The DoD pin: a stub that returns narration-only once, then a valid
        # accusing opening -- the retry recovers and no default fires.
        result, client, manager = _run_with_openings(
            _turn_json(speaker="p-1", free_text=self._NARRATION),
            _turn_json(speaker="p-1", accuses="p-3"),
        )

        assert client.opening_calls == 2
        assert manager.defaulted_calls == ()
        opening = result.transcript.turns[0]
        targets = [c.against for c in opening.claims if isinstance(c, AccusationClaim)]
        assert targets == ["p-3"]
        # The recovered accusation drives the chain: the floor passes to p-3.
        assert result.transcript.turns[1].speaker == "p-3"

    def test_narration_only_twice_degrades_to_an_unsure_opening(self) -> None:
        # Both attempts narration-only -> exactly one retry (never a loop),
        # then the Task 10.6 fail-soft: the attempts PARSED, so the opening
        # degrades to an unsure turn that keeps the model's prose instead of
        # the chain-killing placeholder default (audit gp-5 H-H-2).
        result, client, manager = _run_with_openings(
            _turn_json(speaker="p-1", free_text=self._NARRATION),
        )

        assert client.opening_calls == 2
        opening = result.transcript.turns[0]
        assert opening.free_text == OPENING_UNSURE_DEGRADE_MARKER + self._NARRATION
        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "opening"
        assert default.trigger == "validation"
        assert default.turn_index == 0
        # The gp-5 telemetry split: this is a validation-DEGRADE, not a
        # cap/deadline default.
        assert default.degraded is True
        # The narration-only retry feedback states the no-position reason
        # (no dropped target to name).
        assert OPENING_RETRY_FEEDBACK_NO_POSITION in client.opening_prompts[1]
        assert OPENING_RETRY_FEEDBACK_NO_POSITION not in client.opening_prompts[0]
        # The payloads RETURNED (the recording client logged their spend), so
        # the default carries no provider parse-failures and nothing was
        # "recovered" -- no double-count (mirrors the manager-side
        # validation-default contract).
        assert default.parse_failures == ()
        assert manager.recovered_call_failures == ()

    def test_unsure_opening_records_on_first_attempt(self) -> None:
        result, client, manager = _run_with_openings(
            _turn_json(speaker="p-1", free_text="I am unsure who did this."),
        )

        assert client.opening_calls == 1
        assert manager.defaulted_calls == ()
        assert result.transcript.turns[0].free_text == "I am unsure who did this."

    def test_unsure_marker_matches_case_insensitively(self) -> None:
        result, client, _ = _run_with_openings(
            _turn_json(speaker="p-1", free_text="Unsure. No one stood out."),
        )

        assert client.opening_calls == 1
        assert result.transcript.turns[0].free_text == "Unsure. No one stood out."

    def test_accusing_opening_records_on_first_attempt(self) -> None:
        result, client, manager = _run_with_openings(
            _turn_json(speaker="p-1", accuses="p-2", free_text="It was p-2."),
        )

        assert client.opening_calls == 1
        assert manager.defaulted_calls == ()
        assert result.transcript.turns[1].speaker == "p-2"

    def test_dead_id_opening_accusation_retries_and_recovers(self) -> None:
        # The audit's seed-13-m0 shape with a recovering retry: the first
        # attempt's only accusation names a non-living player and is dropped
        # (leaving the opening narration-only); the retry accuses a living
        # player and records normally.
        result, client, manager = _run_with_openings(
            _turn_json(speaker="p-1", accuses="p-99", free_text="p-99 did it."),
            _turn_json(speaker="p-1", accuses="p-3"),
        )

        assert client.opening_calls == 2
        assert manager.defaulted_calls == ()
        opening = result.transcript.turns[0]
        targets = [c.against for c in opening.claims if isinstance(c, AccusationClaim)]
        assert targets == ["p-3"]

    def test_drop_marker_text_never_self_certifies_unsure(self) -> None:
        # A hallucinated target literally named "unsure" produces a drop
        # marker quoting it ("[invalid accusation target 'unsure' ...]").
        # The validation reads the MODEL-AUTHORED free_text, never the
        # marker-prefixed text, so the quoted value cannot satisfy the
        # unsure check and the opening still retries -- then degrades,
        # with the drop marker preserved AFTER the degrade marker.
        result, client, manager = _run_with_openings(
            _turn_json(speaker="p-1", accuses="unsure", free_text="It was them."),
        )

        assert client.opening_calls == 2
        opening = result.transcript.turns[0]
        assert opening.free_text == (
            OPENING_UNSURE_DEGRADE_MARKER
            + INVALID_ACCUSATION_TARGET_MARKER.format(target="unsure")
            + "It was them."
        )
        assert not any(isinstance(c, AccusationClaim) for c in opening.claims)
        assert len(manager.defaulted_calls) == 1
        assert manager.defaulted_calls[0].trigger == "validation"
        assert manager.defaulted_calls[0].degraded is True

    def test_narration_only_reply_records_without_retry(self) -> None:
        # The content validation is opening-only: a purely defensive reply
        # (no accusation, no unsure declaration) is a legitimate chain
        # terminator and records on its single attempt.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt:
                return _turn_json(speaker="p-1", accuses="p-3")
            if "PHASE=TURN" in prompt:
                return _turn_json(
                    speaker=_extract_marker(prompt, "agent_id="),
                    free_text="I deny that completely.",
                )
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")

        result, client = _run_meeting(_responder)

        reply = result.transcript.turns[1]
        assert reply.turn_kind == "reply"
        assert reply.free_text == "I deny that completely."
        turn_calls = [c for c in client.calls if "PHASE=TURN" in c.prompt]
        assert len(turn_calls) == 1


class TestCoverDirectiveThreading:
    """Task 11.2 (PR #159 review): the reply path threads BOTH ``is_impostor``
    and ``is_body_report`` into the statement renderer, so the cover directive
    fires only for an impostor reply in a body-report meeting -- never for a
    crewmate, and never on a body-less emergency reply.
    """

    @staticmethod
    def _impostor_reply_responder(prompt: str, schema: type[BaseModel] | None) -> str:
        # The opening (p-1, crewmate) accuses p-3, so the floor passes to the
        # impostor p-3 for a reply turn.
        if "PHASE=OPENING" in prompt:
            return _turn_json(speaker="p-1", accuses="p-3")
        if "PHASE=TURN" in prompt:
            return _turn_json(
                speaker=_extract_marker(prompt, "agent_id="),
                free_text="I deny that.",
            )
        return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")

    @staticmethod
    def _participants() -> tuple[MeetingParticipant, ...]:
        return (
            _participant("p-1"),
            _participant("p-2"),
            _participant("p-3", role="IMPOSTOR"),
            _participant("p-4"),
        )

    def test_impostor_reply_in_body_meeting_threads_both_flags(self) -> None:
        result, client = _run_meeting(
            self._impostor_reply_responder, participants=self._participants()
        )

        assert result.transcript.turns[1].turn_kind == "reply"
        p3_reply = next(
            c
            for c in client.calls
            if "PHASE=TURN" in c.prompt and "agent_id=p-3" in c.prompt
        )
        assert "is_impostor=True" in p3_reply.prompt
        assert "is_body_report=True" in p3_reply.prompt

    def test_impostor_reply_in_emergency_meeting_gates_off_body_report(
        self,
    ) -> None:
        emergency_trigger = MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=410,
            description="p-1 called an emergency meeting at tick 410",
        )
        result, client = _run_meeting(
            self._impostor_reply_responder,
            participants=self._participants(),
            trigger=emergency_trigger,
        )

        assert result.transcript.turns[1].turn_kind == "reply"
        p3_reply = next(
            c
            for c in client.calls
            if "PHASE=TURN" in c.prompt and "agent_id=p-3" in c.prompt
        )
        # The impostor still gets is_impostor=True, but the body-report gate is
        # off (no body), so the cover block never renders the "a body was found"
        # copy in an emergency reply.
        assert "is_impostor=True" in p3_reply.prompt
        assert "is_body_report=False" in p3_reply.prompt

    def test_crewmate_reply_in_body_meeting_is_not_impostor(self) -> None:
        # A crewmate reply (opening accuses crewmate p-2) carries is_impostor
        # False even though the body-report gate is True -- the role gate keeps
        # the cover directive impostor-only.
        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt:
                return _turn_json(speaker="p-1", accuses="p-2")
            if "PHASE=TURN" in prompt:
                return _turn_json(
                    speaker=_extract_marker(prompt, "agent_id="),
                    free_text="Not me.",
                )
            return _vote_json(voter=_extract_marker(prompt, "voter="), target="SKIP")

        _result, client = _run_meeting(_responder, participants=self._participants())

        p2_reply = next(
            c
            for c in client.calls
            if "PHASE=TURN" in c.prompt and "agent_id=p-2" in c.prompt
        )
        assert "is_impostor=False" in p2_reply.prompt
        assert "is_body_report=True" in p2_reply.prompt


# --- Unknown role rejected -------------------------------------------------


class TestRoleValidation:
    def test_typo_role_is_rejected(self) -> None:
        manager = _make_manager(llm_client=_ScriptedLLMClient(_make_responder()))
        with pytest.raises(ValueError, match="role must be one of"):
            _run(
                manager.run(
                    meeting_id="m",
                    trigger=_default_trigger(),
                    participants=(_participant("p-1", role="impostor"),),
                )
            )

    def test_crew_with_fellow_impostor_ids_is_rejected(self) -> None:
        manager = _make_manager(llm_client=_ScriptedLLMClient(_make_responder()))
        with pytest.raises(ValueError, match="must be empty for a"):
            _run(
                manager.run(
                    meeting_id="m",
                    trigger=_default_trigger(),
                    participants=(
                        _participant(
                            "p-1", role="CREWMATE", fellow_impostor_ids=("p-2",)
                        ),
                    ),
                )
            )

    def test_impostor_with_fellow_impostor_ids_is_accepted(self) -> None:
        participants = (
            _participant("p-1"),
            _participant("p-2", role="IMPOSTOR", fellow_impostor_ids=("p-3",)),
            _participant("p-3", role="IMPOSTOR", fellow_impostor_ids=("p-2",)),
        )
        result, _ = _run_meeting(_make_responder(), participants=participants)
        assert isinstance(result, MeetingResult)


# --- LLM call agent-id attribution -----------------------------------------


class TestLLMCallAgentIdAttribution:
    def test_each_call_carries_the_speaking_participants_agent_id(self) -> None:
        _, client = _run_meeting(
            _make_responder(accusations={"p-1": "p-2", "p-2": None})
        )

        # Opening (p-1) + reply (p-2) + 4 votes; every call's agent_id is the
        # speaking participant.
        opening = client.calls[0]
        assert opening.agent_id == "p-1"
        assert opening.call_kind == "meeting"
        reply = client.calls[1]
        assert reply.agent_id == "p-2"
        vote_calls = [c for c in client.calls if "PHASE=VOTE" in c.prompt]
        assert sorted(c.agent_id for c in vote_calls if c.agent_id is not None) == [
            "p-1",
            "p-2",
            "p-3",
            "p-4",
        ]


# --- Post-meeting belief evidence extraction (Task 9.8) ---------------------


def _result_with(
    *,
    turns: tuple[MeetingTurn, ...] = (),
    contradictions: tuple[ContradictionRef, ...] = (),
    voters: tuple[str, ...] = (),
) -> MeetingResult:
    # ``voters`` materialises one default-SKIP ballot per id: in a
    # production result every living participant casts exactly one ballot,
    # and ``extract_belief_evidence`` reads the voter set as the meeting's
    # living roster for its detector-derived corroborations (Task 10.1).
    return MeetingResult(
        meeting_id="m-1",
        triggered_by="p-1",
        trigger_tick=410,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=tuple(
            VoteBallot(
                voter=voter,
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="skip",
            )
            for voter in voters
        ),
        contradictions=contradictions,
        transcript=MeetingTranscript(turns=turns),
    )


def _evidence_turn(
    *,
    turn_index: int,
    speaker: str,
    accuses: tuple[str, ...] = (),
    corroborates: tuple[str, ...] = (),
) -> MeetingTurn:
    claims: list[Claim] = [
        AccusationClaim(
            type="accusation",
            against=target,
            confidence=0.6,
            reason=f"{speaker} accuses {target}",
        )
        for target in accuses
    ]
    claims.extend(
        CorroborationClaim(
            type="corroboration",
            supports=subject,
            on_tick=400,
            reason=f"{speaker} vouches for {subject}",
        )
        for subject in corroborates
    )
    return MeetingTurn(
        turn_id=f"m-1:turn-{turn_index}",
        turn_index=turn_index,
        speaker=speaker,
        turn_kind="opening" if turn_index == 0 else "reply",
        reply_to=None,
        observations=(),
        claims=tuple(claims),
        free_text=f"turn from {speaker}",
    )


class TestExtractBeliefEvidence:
    """Task 9.8 (DESIGN.md §6.3 Rules 3 + 5, §4.6; audit gp-1 recall).

    ``extract_belief_evidence`` reduces a resolved ``MeetingResult`` to
    the deduplicated public subject sets the post-meeting hook folds
    into each living agent's persistent beliefs.
    """

    def test_collects_accused_corroborated_and_contradicted_sorted(self) -> None:
        result = _result_with(
            turns=(
                _evidence_turn(turn_index=0, speaker="p-1", accuses=("p-3",)),
                _evidence_turn(
                    turn_index=1,
                    speaker="p-3",
                    accuses=("p-2",),
                    corroborates=("p-4",),
                ),
            ),
            contradictions=(
                ContradictionRef(
                    contradiction_id="contra:alibi_vs_sighting:a|b",
                    kind="alibi_vs_sighting",
                    event_a_id="a",
                    event_b_id="b",
                    subjects=("p-5",),
                    description="Alibi places p-5 in A; sighting reports p-5 in B.",
                ),
            ),
        )

        evidence = extract_belief_evidence(result)

        assert evidence == MeetingBeliefEvidence(
            accused=("p-2", "p-3"),
            corroborated=("p-4",),
            contradicted=("p-5",),
        )

    def test_pile_on_accusations_deduplicate_to_one_meeting_event(self) -> None:
        # The accusation bump is per MEETING, not per accuser: three
        # turns piling onto p-3 are one "was accused" event, so audit
        # G-G-2's herding (0.935 ballot concentration) cannot multiply
        # the delta within a round.
        result = _result_with(
            turns=(
                _evidence_turn(turn_index=0, speaker="p-1", accuses=("p-3",)),
                _evidence_turn(turn_index=1, speaker="p-3", accuses=()),
                _evidence_turn(turn_index=2, speaker="p-2", accuses=("p-3",)),
                _evidence_turn(turn_index=3, speaker="p-4", accuses=("p-3",)),
            )
        )

        assert extract_belief_evidence(result).accused == ("p-3",)

    def test_empty_meeting_yields_empty_evidence(self) -> None:
        evidence = extract_belief_evidence(_result_with())

        assert evidence == MeetingBeliefEvidence(
            accused=(), corroborated=(), contradicted=()
        )

    def test_ballots_are_not_evidence(self) -> None:
        # Ballots are post-hoc transparency, never visible to agents
        # (DESIGN.md §5.5) -- a vote target must not feed the accumulator.
        ballot = VoteBallot(
            voter="p-1",
            target="p-2",
            confidence=0.9,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="vote p-2",
        )
        result = _result_with().model_copy(
            update={
                "outcome": "EJECTED",
                "ejected_player_id": "p-2",
                "ballots": (ballot,),
            }
        )

        assert extract_belief_evidence(result).accused == ()

    def test_production_meeting_round_trips_into_evidence(self) -> None:
        # Drift guard: a manager-produced MeetingResult (not a hand-built
        # one) feeds the extractor -- the chain p-1 -> p-2 -> p-3 records
        # two accusations plus p-4's opt-in corroboration of p-1.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-2", "p-2": "p-3", "p-3": None},
                observations={
                    "p-1": (
                        SawPlayerObservation(
                            type="saw_player",
                            tick=400,
                            subject="p-2",
                            room="CAFETERIA",
                            co_present=("p-4",),
                        ),
                    ),
                },
                claims_by={
                    "p-4": (
                        CorroborationClaim(
                            type="corroboration",
                            supports="p-1",
                            on_tick=400,
                            reason="p-4 vouches for p-1",
                        ),
                    ),
                },
            )
        )

        evidence = extract_belief_evidence(result)

        assert evidence.accused == ("p-2", "p-3")
        assert evidence.corroborated == ("p-1",)

    def test_teammate_accusation_never_reaches_the_evidence(self) -> None:
        # 7.12 interplay: an impostor opener's accusation of its teammate
        # is stripped at the per-turn chokepoint BEFORE recording, so the
        # accumulator sees no teammate subject from any agent's fold --
        # the evidence path inherits the firewall it rides on.
        result, _ = _run_meeting(
            _make_responder(accusations={"p-1": "p-2"}),
            participants=(
                _participant("p-1", role="IMPOSTOR", fellow_impostor_ids=("p-2",)),
                _participant("p-2", role="IMPOSTOR", fellow_impostor_ids=("p-1",)),
                _participant("p-3"),
                _participant("p-4"),
            ),
        )

        assert extract_belief_evidence(result).accused == ()


# --- Task 10.1: detector-derived corroboration feeds the Rule-3 fold --------


class TestDetectorCorroborationFold:
    """The corroboration fold ACCEPTS a detector-derived pair (Task 10.1).

    Audit gp-2 C-C-1: the old detector flagged containment-consistent
    (alibi, sighting) pairs as contradictions; canonicalisation now reads
    them as CONSISTENT and they must flow into the §6.3 Rule-3 channel --
    a containment pair that silently no-op'd would leave half the
    canonicalisation inert (the audit proved Rule 3 never fired, so this
    is the second never-exercised ingestion path). Magnitude is the
    Rule-3 delta, applied once per subject per meeting by the fold's
    set-dedup.
    """

    def _containment_result(self) -> MeetingResult:
        # p-1's self-alibi (MEDBAY t100-200) confirmed by p-2's sighting
        # of p-1 in MEDBAY at t150. NO CorroborationClaim anywhere: the
        # evidence is detector-derived only.
        turns = (
            MeetingTurn(
                turn_id="m-1:turn-0",
                turn_index=0,
                speaker="p-1",
                turn_kind="opening",
                reply_to=None,
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="p-1",
                        from_tick=100,
                        to_tick=200,
                        room="MEDBAY",
                    ),
                ),
                free_text="self alibi",
            ),
            MeetingTurn(
                turn_id="m-1:turn-1",
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                reply_to=None,
                observations=(
                    SawPlayerObservation(
                        type="saw_player", tick=150, subject="p-1", room="MEDBAY"
                    ),
                ),
                free_text="confirming sighting",
            ),
        )
        return _result_with(turns=turns, voters=("p-1", "p-2", "p-3", "p-4"))

    def test_containment_pair_lands_in_corroborated(self) -> None:
        evidence = extract_belief_evidence(self._containment_result())

        assert evidence.corroborated == ("p-1",)
        assert evidence.accused == ()
        assert evidence.contradicted == ()

    def test_hallucinated_subject_cannot_corroborate_itself(self) -> None:
        # The detector-derived path is roster-filtered to the recorded
        # ballot voters, mirroring the recording-time detection call: a
        # hallucinated non-player subject (audit C-8) whose alibi and
        # sighting happen to agree must not materialise a phantom belief
        # row through the fold.
        turns = (
            MeetingTurn(
                turn_id="m-1:turn-0",
                turn_index=0,
                speaker="p-1",
                turn_kind="opening",
                reply_to=None,
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="p-99",
                        from_tick=100,
                        to_tick=200,
                        room="MEDBAY",
                    ),
                ),
                free_text="alibi for a hallucinated id",
            ),
            MeetingTurn(
                turn_id="m-1:turn-1",
                turn_index=1,
                speaker="p-2",
                turn_kind="reply",
                reply_to=None,
                observations=(
                    SawPlayerObservation(
                        type="saw_player", tick=150, subject="p-99", room="MEDBAY"
                    ),
                ),
                free_text="matching hallucinated sighting",
            ),
        )
        result = _result_with(turns=turns, voters=("p-1", "p-2", "p-3", "p-4"))

        assert extract_belief_evidence(result).corroborated == ()

    def test_containment_pair_lowers_suspicion_through_the_fold(self) -> None:
        # Integration pin: the detector-derived subject moves the stored
        # belief by exactly the Rule-3 delta through the production fold
        # -- the path is alive end-to-end, not just extracted.
        evidence = extract_belief_evidence(self._containment_result())
        beliefs = BeliefState()
        beliefs.seed_player("p-1", suspicion=0.55, trust=0.5)

        updated = apply_meeting_evidence_rules(
            beliefs,
            own_id="p-4",
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
        )

        assert updated.view("p-1").suspicion == pytest.approx(
            0.55 - CORROBORATION_SUSPICION_DELTA
        )

    def test_production_meeting_detector_corroboration_round_trips(self) -> None:
        # The same pair through a manager-RUN meeting (not a hand-built
        # result): p-1 self-alibis in the opening; the accused p-2's
        # reply carries the sighting that confirms it.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-2", "p-2": None},
                claims_by={
                    "p-1": (
                        AlibiClaim(
                            type="alibi",
                            subject="p-1",
                            from_tick=100,
                            to_tick=200,
                            room="MEDBAY",
                        ),
                    ),
                },
                observations={
                    "p-2": (
                        SawPlayerObservation(
                            type="saw_player",
                            tick=150,
                            subject="p-1",
                            room="MEDBAY",
                        ),
                    ),
                },
            )
        )

        assert detect_corroborations(result.transcript) != ()
        assert "p-1" in extract_belief_evidence(result).corroborated

    def test_claim_stated_corroboration_still_folds(self) -> None:
        # The pre-10.1 ingestion path is untouched: a CorroborationClaim
        # without any containment pair still lands.
        result = _result_with(
            turns=(_evidence_turn(turn_index=0, speaker="p-2", corroborates=("p-4",)),)
        )

        assert extract_belief_evidence(result).corroborated == ("p-4",)


# --- Task 10.1 acceptance pins against the committed replay bytes -----------
#
# Originally (at 10.1 merge time) these fed the e750b40 era's RECORDED defect
# flags (the seed-9 19-flag fountain, the seed-26 defense-echo inversion)
# through the repaired vote-time lift and proved the collapse offline. The
# Task 10.5 re-record replaced the committed bytes with a set RECORDED UNDER
# the repaired detector+lift, so those defect inputs no longer exist anywhere
# in the tree; the per-scenario proofs are preserved in git history (the 10.1
# acceptance gate) and by the synthetic lift tests above. What remains
# meaningful on the new bytes is the INVARIANT the scenarios instantiated,
# pinned set-wide below. Audit anchor:
# audit-2026-06-10-1820-gameplay-data.md gp-2 (C-C-3).

import json  # noqa: E402
import re  # noqa: E402

from orchestrator.replay import (  # noqa: E402
    MeetingReplayEntry,
    read_all_entries,
)

_COMMITTED_9P2I_DIR = (
    Path(__file__).resolve().parents[2] / "replays" / "samples" / "9p2i"
)

# The committed vote_ballot.j2 renders the voter's suspicion graph as
# "- `p-N`: suspicion X, trust Y" rows under this header (the same parse the
# audit extractor used to read the decomposition's rendered values).
_SUSPICION_GRAPH_HEADER = "## Your suspicion graph"
_SUSPICION_GRAPH_ROW_RE = re.compile(
    r"`(?P<pid>p-\d+)`: suspicion (?P<sus>[0-9]*\.?[0-9]+), "
    r"trust (?P<trust>[0-9]*\.?[0-9]+)"
)


def _committed_meeting(seed: int, meeting_index: int) -> MeetingReplayEntry:
    path = _COMMITTED_9P2I_DIR / f"replay-seed-{seed}.jsonl"
    meetings = [
        entry
        for entry in read_all_entries(path)
        if isinstance(entry, MeetingReplayEntry)
    ]
    return meetings[meeting_index]


def _recorded_rendered_suspicions(entry: MeetingReplayEntry, *, of: str) -> list[float]:
    """Every suspicion value the committed vote prompts rendered for ``of``."""

    values: list[float] = []
    for call in entry.llm_calls:
        if _SUSPICION_GRAPH_HEADER not in call.prompt:
            continue
        block = call.prompt.split(_SUSPICION_GRAPH_HEADER, 1)[1].split("## ", 1)[0]
        values.extend(
            float(match.group("sus"))
            for match in _SUSPICION_GRAPH_ROW_RE.finditer(block)
            if match.group("pid") == of
        )
    return values


class TestCommittedBytesLiftPins:
    """The 10.1 lift invariant on the RECORDED bytes (gp-2 C-C-3).

    Set-wide successor to the per-scenario era pins (see the section
    comment): on a set recorded under the repaired lift, no crew member
    may render at a clamped 1.0 in ANY committed vote prompt off stacked
    same-meeting contradiction flags — the railroad class the seed-9
    fountain (19 flags -> 1.0, ejected 5-0) and the seed-26 defense-echo
    inversion instantiated on the e750b40 era bytes.
    """

    def test_no_crew_member_renders_at_one_on_the_committed_set(self) -> None:
        # Roles come from the committed report's per-game role map (derived
        # from the same bytes at report-build time; the eval-layer pins in
        # tests/eval/test_gate_metrics.py hold the report to those bytes),
        # so this stays a meetings-layer walk: every meeting's vote
        # prompts, every rendered crew row.
        # On the Task 10.5 set the recorded truth is stronger than the
        # invariant needs: NO crew member renders at 1.0 at all (an
        # impostor legitimately can, e.g. kill-witness + contradiction).
        # A future re-record may carry a legitimate crew 1.0 (e.g. stacked
        # ACROSS meetings by the 9.8 accumulator) — if this fires, check
        # the same-meeting flag count before treating it as the railroad:
        # the 10.1 cap bounds the per-meeting contradiction lift at one
        # strong flag's worth (0.3), so a same-meeting flag-stacked 1.0 is
        # the repaired defect re-appearing.
        report = json.loads(
            (_COMMITTED_9P2I_DIR / "tournament-eval-report.json").read_text(
                encoding="utf-8"
            )
        )
        roles_by_seed: dict[int, dict[str, str]] = {
            game["seed"]: game["roles"] for game in report["report"]["games"]
        }
        prompts_scanned = 0
        for seed in range(50):
            path = _COMMITTED_9P2I_DIR / f"replay-seed-{seed}.jsonl"
            roles = roles_by_seed[seed]
            for entry in read_all_entries(path):
                if not isinstance(entry, MeetingReplayEntry):
                    continue
                for player_id, role in roles.items():
                    if role != "CREWMATE":
                        continue
                    rendered = _recorded_rendered_suspicions(entry, of=player_id)
                    prompts_scanned += len(rendered)
                    assert all(value < 1.0 for value in rendered), (
                        f"crew {player_id} rendered at 1.0 in {entry.meeting_id}"
                    )
        # Non-vacuous: the walk actually read rendered crew rows.
        assert prompts_scanned > 0


def _living_voters(entry: MeetingReplayEntry) -> set[str]:
    return {ballot.voter for ballot in entry.ballots}


# --- Task 10.2: roster validation for every subject-bearing claim field -------
#
# Audit gp-6 (C-C-8, H-H-6): the fb3cfa5 guard covered accusation targets
# only, so the 9B's hallucinated structural ids in ``alibi.subject`` /
# ``corroboration.supports`` were recorded, folded into persistent belief
# rows, and rendered as §6.6 suspicion-graph rows -- and 15 corroborations
# no-op'd on phantom subjects, which is why belief Rule 3 never fired in
# any recorded set. DESIGN.md §5.2, §6.3.


def _voter_memory(
    agent_id: str,
    *,
    sightings: tuple[str, ...] = ("p-2", "p-3", "p-4"),
) -> AgentMemory:
    """A production-shaped ``AgentMemory`` for the post-meeting fold.

    Mirrors what perception leaves behind by meeting time: a ``self_state``
    carrying the agent's own id (the 9.3 self channel the fold requires)
    plus tick-0 co-spawn sightings of the roster (what makes the Task 10.2
    fold filter a no-op on real-player evidence).
    """

    memory = AgentMemory()
    memory.episodic.append(
        EpisodicEvent(
            tick=0,
            type="self_state",
            payload={
                "agent_id": agent_id,
                "room": "CAFETERIA",
                "role": "CREWMATE",
                "pending_task_id": None,
            },
            provenance="observed",
        )
    )
    for player_id in sightings:
        memory.episodic.append(
            EpisodicEvent(
                tick=0,
                type="saw_player",
                payload={"player_id": player_id, "room": "CAFETERIA", "action": None},
                provenance="observed",
            )
        )
    return memory


class TestNonRosterClaimSubjectsDropped:
    """Alibi subjects / corroboration supports are living-roster validated.

    The Task 10.2 extension of the fb3cfa5 chokepoint: an
    :class:`AlibiClaim` whose ``subject`` -- or a
    :class:`CorroborationClaim` whose ``supports`` -- is not a living
    meeting participant is dropped before the turn is recorded, the
    original preserved on ``free_text`` via its per-field audit marker.
    Same rule as accusations, so a DEAD roster player drops too.
    """

    def test_unit_drops_each_non_roster_field_with_its_marker(self) -> None:
        claims: tuple[Claim, ...] = (
            AlibiClaim(
                type="alibi",
                subject="headless-seed-9",
                from_tick=2,
                to_tick=7,
                room="MEDBAY",
            ),
            AlibiClaim(
                type="alibi", subject="p-1", from_tick=2, to_tick=7, room="MEDBAY"
            ),
            AccusationClaim(
                type="accusation", against="imp-2", confidence=0.9, reason="r"
            ),
            CorroborationClaim(
                type="corroboration", supports="m-1:turn-0", on_tick=6, reason="r"
            ),
            CorroborationClaim(
                type="corroboration", supports="p-3", on_tick=6, reason="r"
            ),
        )

        surviving, markers = _drop_non_roster_claims(
            claims, living_ids=frozenset({"p-1", "p-2", "p-3", "p-4"})
        )

        # Markers carry each dropped field's original value, in claim order.
        assert markers == (
            INVALID_ALIBI_SUBJECT_MARKER.format(subject="headless-seed-9"),
            INVALID_ACCUSATION_TARGET_MARKER.format(target="imp-2"),
            INVALID_CORROBORATION_SUPPORTS_MARKER.format(supports="m-1:turn-0"),
        )
        # The valid alibi and corroboration survive, in order.
        assert [c.subject for c in surviving if isinstance(c, AlibiClaim)] == ["p-1"]
        assert [c.supports for c in surviving if isinstance(c, CorroborationClaim)] == [
            "p-3"
        ]

    def test_seed9_shape_garbage_subject_and_supports_drop_and_mark(self) -> None:
        # The seed-9 m1 turns 2-3 shape live through the chokepoint: an
        # alibi whose subject is the game id and a corroboration whose
        # supports is the game id both drop, each marker preserving the
        # original on ``free_text`` in claim order; the valid
        # corroboration of a living participant survives.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": None},
                claims_by={
                    "p-1": (
                        AlibiClaim(
                            type="alibi",
                            subject="headless-seed-9",
                            from_tick=2,
                            to_tick=7,
                            room="MEDBAY",
                        ),
                        CorroborationClaim(
                            type="corroboration",
                            supports="p-3",
                            on_tick=6,
                            reason="real vouch",
                        ),
                        CorroborationClaim(
                            type="corroboration",
                            supports="headless-seed-9",
                            on_tick=6,
                            reason="vouch for a game id",
                        ),
                    ),
                },
            )
        )

        opening = result.transcript.turns[0]
        assert not any(isinstance(c, AlibiClaim) for c in opening.claims)
        kept = [c.supports for c in opening.claims if isinstance(c, CorroborationClaim)]
        assert kept == ["p-3"]
        assert opening.free_text.startswith(
            INVALID_ALIBI_SUBJECT_MARKER.format(subject="headless-seed-9")
            + INVALID_CORROBORATION_SUPPORTS_MARKER.format(supports="headless-seed-9")
        )

    def test_corroboration_naming_a_dead_roster_player_is_dropped(self) -> None:
        # The seed-40 shape generalised: p-2 is a real roster id but DEAD
        # (not a meeting participant), so a corroboration naming them
        # drops under the same living-roster rule as accusations. (The
        # literal recorded value was the free-text phrase "p-2 dead"; the
        # committed-bytes pin below covers it.)
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": None},
                claims_by={
                    "p-1": (
                        CorroborationClaim(
                            type="corroboration",
                            supports="p-2",
                            on_tick=7,
                            reason="vouch for the dead",
                        ),
                    ),
                },
            ),
            participants=(
                _participant("p-1"),
                _participant("p-3"),
                _participant("p-4"),
            ),
        )

        opening = result.transcript.turns[0]
        assert not any(isinstance(c, CorroborationClaim) for c in opening.claims)
        assert opening.free_text.startswith(
            INVALID_CORROBORATION_SUPPORTS_MARKER.format(supports="p-2")
        )
        assert "p-2" not in extract_belief_evidence(result).corroborated

    def test_valid_alibi_and_corroboration_pass_through_unmarked(self) -> None:
        # The no-op guarantee: claims naming living participants record
        # byte-unchanged, so a clean replay is unaffected.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": None},
                claims_by={
                    "p-1": (
                        AlibiClaim(
                            type="alibi",
                            subject="p-1",
                            from_tick=2,
                            to_tick=7,
                            room="MEDBAY",
                        ),
                        CorroborationClaim(
                            type="corroboration",
                            supports="p-2",
                            on_tick=6,
                            reason="vouch",
                        ),
                    ),
                },
            )
        )

        opening = result.transcript.turns[0]
        assert len(opening.claims) == 2
        assert opening.free_text == "turn from p-1 -- unsure"

    def test_dropped_garbage_subject_never_reaches_detection_or_the_fold(
        self,
    ) -> None:
        # Ordering pin (the 10.2 hint): the chokepoint runs BEFORE §5.4
        # detection and before the post-meeting fold. p-1's garbage alibi
        # meets p-2's same-id sighting in a different room over the same
        # ticks -- the shape that would pair into an alibi_vs_sighting
        # flag were the claim recorded and indexed. Dropped at the
        # chokepoint, it mints no flag (so it can never consume any 10.1
        # lift/cap accounting), reaches no evidence set, and materialises
        # no belief row through the production fold.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-2", "p-2": None},
                claims_by={
                    "p-1": (
                        AlibiClaim(
                            type="alibi",
                            subject="headless-seed-9",
                            from_tick=2,
                            to_tick=7,
                            room="MEDBAY",
                        ),
                    ),
                },
                observations={
                    "p-2": (
                        SawPlayerObservation(
                            type="saw_player",
                            tick=4,
                            subject="headless-seed-9",
                            room="STORAGE",
                        ),
                    ),
                },
            )
        )

        # Never recorded -> never detected -> never folded.
        assert not any(
            isinstance(c, AlibiClaim)
            for turn in result.transcript.turns
            for c in turn.claims
        )
        assert result.transcript.turns[0].free_text.startswith(
            INVALID_ALIBI_SUBJECT_MARKER.format(subject="headless-seed-9")
        )
        assert all(
            "headless-seed-9" not in flag.subjects for flag in result.contradictions
        )
        evidence = extract_belief_evidence(result)
        assert "headless-seed-9" not in (
            evidence.accused + evidence.corroborated + evidence.contradicted
        )
        memory = _voter_memory("p-3")
        absorb_meeting_evidence(
            memory,
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
        )
        assert "headless-seed-9" not in memory.beliefs.known_players()


class TestCorroborationRule3FiresEndToEnd:
    """Belief Rule 3's first live path (Task 10.2 DoD, the hard line).

    Every prior recorded set carried only invalid ``supports`` values, so
    the corroboration channel was structurally dead: the -0.05 delta had
    never travelled meeting -> evidence -> fold -> store -> render. This
    pins the whole production seam: a real :class:`MeetingManager` run
    records the valid claim through the chokepoint,
    ``extract_belief_evidence`` carries the subject, and the same
    ``absorb_meeting_evidence`` fold the orchestrator fans out
    (``orchestrator.game._absorb_meeting_beliefs``) lowers the supported
    player's PERSISTED suspicion by exactly the Rule-3 delta -- which is
    what the next meeting's §6.6 render and suspicion graph then show.
    """

    def test_valid_corroboration_lowers_suspicion_by_the_rule3_delta(self) -> None:
        # p-1 opens accusing p-4; the accused p-4's reply corroborates
        # p-2 (a living participant), ending the chain.
        result, _ = _run_meeting(
            _make_responder(
                accusations={"p-1": "p-4", "p-4": None},
                claims_by={
                    "p-4": (
                        CorroborationClaim(
                            type="corroboration",
                            supports="p-2",
                            on_tick=400,
                            reason="p-4 vouches for p-2",
                        ),
                    ),
                },
            )
        )

        # The chokepoint recorded the valid claim (no drop, no marker).
        recorded = [
            c.supports
            for turn in result.transcript.turns
            for c in turn.claims
            if isinstance(c, CorroborationClaim)
        ]
        assert recorded == ["p-2"]
        evidence = extract_belief_evidence(result)
        assert "p-2" in evidence.corroborated

        # The orchestrator fan-out shape: fold the evidence into a living
        # voter's production store.
        memory = _voter_memory("p-3")
        absorb_meeting_evidence(
            memory,
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
        )

        # Rule 3 FIRED: the supported player's persisted suspicion moved
        # down by exactly the Rule-3 delta; the accused moved up by the
        # accusation bump (the fold ran wholesale, not just Rule 3).
        assert memory.beliefs.view("p-2").suspicion == pytest.approx(
            _DEFAULT_TEST_SUSPICION - CORROBORATION_SUSPICION_DELTA
        )
        assert memory.beliefs.view("p-4").suspicion > _DEFAULT_TEST_SUSPICION
        # And the lowered score is what the NEXT meeting's prompts see.
        assert "p-2: suspicion 0.45" in render_for_prompt(memory)


class TestCommittedBytesRosterDropPins:
    """The 10.2 chokepoint held during the 10.5 recording (gp-6, offline).

    The original pins fed the e750b40 era's RECORDED garbage claims (seed 9's
    "headless-seed-9" subjects, seed 40's "p-2 dead" supports — recorded
    before the guard existed) through ``_drop_non_roster_claims`` and proved
    the drop. The Task 10.5 set was recorded WITH the guard in the manager,
    so garbage never reaches the bytes; the set-wide successor pin asserts
    exactly that: replaying the chokepoint over every recorded turn is a
    NO-OP (every subject-bearing claim field already names a living
    participant — zero drops, zero markers). The drop machinery itself stays
    covered by the synthetic ``TestNonRosterClaimSubjectsDropped`` above.
    """

    def test_every_recorded_claim_field_is_living_roster_valid(self) -> None:
        turns_walked = 0
        subject_bearing_claims = 0
        for seed in range(50):
            path = _COMMITTED_9P2I_DIR / f"replay-seed-{seed}.jsonl"
            for entry in read_all_entries(path):
                if not isinstance(entry, MeetingReplayEntry):
                    continue
                living = frozenset(_living_voters(entry))
                for turn in entry.transcript.turns:
                    turns_walked += 1
                    subject_bearing_claims += sum(
                        1
                        for claim in turn.claims
                        if isinstance(claim, (AlibiClaim, CorroborationClaim))
                    )
                    surviving, markers = _drop_non_roster_claims(
                        turn.claims, living_ids=living
                    )
                    assert markers == (), (
                        f"recorded claim would drop in {entry.meeting_id} "
                        f"turn {turn.turn_index}: {markers}"
                    )
                    assert surviving == turn.claims
        # Non-vacuous: the walk exercised real subject-bearing claims.
        assert turns_walked > 0
        assert subject_bearing_claims > 0


# ---------------------------------------------------------------------------
# Task 10.6: fail-soft degrade, retry feedback, bounded markers, Rule-3 gate
# at the evidence seam (audit gp-5 H-H-1/H-H-2, gp-6 H-H-4, gp-2 C-C-3).
# ---------------------------------------------------------------------------


class TestOpeningUnsureDegrade:
    """A degraded opening keeps the meeting alive (audit gp-5 H-H-2).

    The seed-12 m0 shape: the opener's body report parsed fine, only its
    accusation named a dead player. The old full default erased the body
    report too, reducing the meeting to a 1-turn SKIP husk; the degrade
    keeps the observations, so the opt-in co-presence gate and the
    ballots still see them.
    """

    def _run_degraded(self) -> tuple[MeetingResult, MeetingManager]:
        # p-1's opening carries the body report (ADMIN) plus a sighting
        # placing p-3 there -- and accuses only the dead "p-99", which the
        # chokepoint drops on both attempts.
        responder = _make_responder(
            accusations={"p-1": "p-99"},
            observations={
                "p-1": (
                    FoundBodyObservation(
                        type="found_body", tick=410, body_of="p-9", room="ADMIN"
                    ),
                    SawPlayerObservation(
                        type="saw_player", tick=409, subject="p-3", room="ADMIN"
                    ),
                ),
            },
        )
        client = _ScriptedLLMClient(responder)
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )
        return result, manager

    def test_degraded_opening_keeps_observations_and_reaches_opt_ins(self) -> None:
        result, manager = self._run_degraded()

        opening = result.transcript.turns[0]
        assert opening.turn_kind == "opening"
        assert opening.free_text.startswith(OPENING_UNSURE_DEGRADE_MARKER)
        # The body report SURVIVES the degrade -- the whole point.
        assert any(isinstance(o, FoundBodyObservation) for o in opening.observations)
        assert not any(isinstance(c, AccusationClaim) for c in opening.claims)
        # The kept sighting makes p-3 opt-in-eligible (co-present with the
        # body room), so the meeting still has an info-share phase...
        opt_ins = [t for t in result.transcript.turns if t.turn_kind == "opt_in"]
        assert [t.speaker for t in opt_ins] == ["p-3"]
        # ...and every living participant still casts a ballot.
        assert sorted(b.voter for b in result.ballots) == [
            "p-1",
            "p-2",
            "p-3",
            "p-4",
        ]

    def test_degrade_telemetry_split(self) -> None:
        _, manager = self._run_degraded()

        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "opening"
        assert default.trigger == "validation"
        assert default.degraded is True

    def test_parse_failed_opening_still_full_defaults(self) -> None:
        # The other tier: nothing ever PARSED (schema-invalid payloads),
        # so there is no attempt to degrade from -- the placeholder
        # default fires and the telemetry reads degraded=False
        # (cap/deadline-default class, not validation-degrade).
        client = _OpeningValidationClient(invalid_opening_attempts=2)
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.transcript.turns[0].free_text == DEFAULT_TURN_FREE_TEXT
        assert len(manager.defaulted_calls) == 1
        assert manager.defaulted_calls[0].degraded is False


class TestBoundedDropMarkers:
    """Audit gp-6 H-H-4: the quoted-original in a drop marker is bounded."""

    def test_mega_subject_yields_a_bounded_marker(self) -> None:
        # The seed-35 m1 shape: a 3499-char reasoning blob hallucinated AS
        # the alibi SUBJECT. The marker quotes only the bounded head.
        blob = "I think the body was found near ADMIN and " * 80
        assert len(blob) > 3000  # the audited ~3.5k-char scale
        claims: tuple[Claim, ...] = (
            AlibiClaim(
                type="alibi", subject=blob, from_tick=400, to_tick=410, room="ADMIN"
            ),
        )
        surviving, markers = _drop_non_roster_claims(
            claims, living_ids=frozenset({"p-1", "p-2"})
        )

        assert surviving == ()
        assert markers == (
            INVALID_ALIBI_SUBJECT_MARKER.format(
                subject=blob[:MARKER_QUOTED_ORIGINAL_MAX_CHARS] + "..."
            ),
        )
        assert len(markers[0]) < 120

    def test_sibling_markers_share_the_bound(self) -> None:
        blob = "x" * 500
        claims: tuple[Claim, ...] = (
            AccusationClaim(
                type="accusation", against=blob, confidence=0.5, reason="r"
            ),
            CorroborationClaim(
                type="corroboration", supports=blob, on_tick=400, reason="r"
            ),
        )
        _, markers = _drop_non_roster_claims(claims, living_ids=frozenset({"p-1"}))

        bounded = blob[:MARKER_QUOTED_ORIGINAL_MAX_CHARS] + "..."
        assert markers == (
            INVALID_ACCUSATION_TARGET_MARKER.format(target=bounded),
            INVALID_CORROBORATION_SUPPORTS_MARKER.format(supports=bounded),
        )

    def test_real_player_ids_pass_through_verbatim(self) -> None:
        claims: tuple[Claim, ...] = (
            AccusationClaim(
                type="accusation", against="p-99", confidence=0.5, reason="r"
            ),
        )
        _, markers = _drop_non_roster_claims(claims, living_ids=frozenset({"p-1"}))
        assert markers == (INVALID_ACCUSATION_TARGET_MARKER.format(target="p-99"),)


class TestRule3RelevanceGateAtTheEvidenceSeam:
    """Audit gp-2 C-C-3: claim-stated vouches pass the same relevance gate."""

    def test_spawn_window_corroboration_claim_is_not_evidence(self) -> None:
        # "I can vouch for p-4 (tick 0)" is the everyone-was-at-spawn
        # shape: it confirms nothing and must not cancel an accusation
        # bump at the fold.
        turn = MeetingTurn(
            turn_id="m-1:turn-0",
            turn_index=0,
            speaker="p-2",
            turn_kind="opening",
            reply_to=None,
            claims=(
                CorroborationClaim(
                    type="corroboration", supports="p-4", on_tick=0, reason="spawn"
                ),
                CorroborationClaim(
                    type="corroboration", supports="p-3", on_tick=1, reason="spawn"
                ),
            ),
            free_text="unsure",
        )
        evidence = extract_belief_evidence(_result_with(turns=(turn,)))
        assert evidence.corroborated == ()

    def test_post_spawn_corroboration_claim_still_counts(self) -> None:
        evidence = extract_belief_evidence(
            _result_with(
                turns=(
                    _evidence_turn(turn_index=0, speaker="p-2", corroborates=("p-4",)),
                )
            )
        )
        # _evidence_turn vouches at on_tick=400 -- far outside the spawn
        # window; the claim-stated channel survives the gate.
        assert evidence.corroborated == ("p-4",)

    def test_kill_scene_detector_pair_is_not_evidence(self) -> None:
        # The seed-6 m1 fold shape: the opening reports the body in ADMIN
        # and sights the subject there inside their own alibi window. The
        # detector-derived pair dies at the one-home gate inside
        # detect_corroborations, so the fold never sees it.
        opening = MeetingTurn(
            turn_id="m-1:turn-0",
            turn_index=0,
            speaker="p-3",
            turn_kind="opening",
            reply_to=None,
            observations=(
                FoundBodyObservation(
                    type="found_body", tick=410, body_of="p-9", room="ADMIN"
                ),
                SawPlayerObservation(
                    type="saw_player", tick=409, subject="p-6", room="ADMIN"
                ),
            ),
            free_text="unsure",
        )
        alibi_turn = MeetingTurn(
            turn_id="m-1:turn-1",
            turn_index=1,
            speaker="p-6",
            turn_kind="reply",
            reply_to=None,
            claims=(
                AlibiClaim(
                    type="alibi",
                    subject="p-6",
                    from_tick=405,
                    to_tick=410,
                    room="ADMIN",
                ),
            ),
            free_text="I was in ADMIN doing the swipe task.",
        )
        evidence = extract_belief_evidence(
            _result_with(turns=(opening, alibi_turn), voters=("p-3", "p-6", "p-7"))
        )
        assert evidence.corroborated == ()


# --- Task 10.7: testimony ingestion (pre-vote, two-witness) -------------------
#
# Audit gp-2 (C-C-1, C-C-2, C-C-3, D-D-3, C-C-6); DESIGN.md §5.2, §6.3, §4.6;
# the corroborate-within-round owner principle. The meeting fold runs in two
# deterministic halves: the manager derives the evidence from the FINAL
# transcript and applies the pre-vote half (two-witness testimony bumps +
# this meeting's relevance-gated corroborations) to every voter's suspicion
# graph before the ballot prompts render; the post-vote half (single-voice
# bumps + Rule-5 decay) stays the orchestrator's standing absorb. Synthetic
# production-path shapes first; the committed-bytes DoD pins (the seed-30
# pile-on STOP pin, the seed-2/5 yield pins, the seed-28 same-phase shape)
# close the section.

from agents.strategic.prompts import vote_ballot_prompt  # noqa: E402
from eval._suspicion_parse import parse_rendered_max_suspicion  # noqa: E402,PLC2701


def _backed_observations(
    *, body_room: str = "MEDBAY", seen: tuple[tuple[str, str, int], ...]
) -> tuple[ObservationClaim, ...]:
    """A found-body observation plus (subject, room, tick) sightings."""

    observations: list[ObservationClaim] = [
        FoundBodyObservation(type="found_body", tick=405, body_of="p-9", room=body_room)
    ]
    observations.extend(
        SawPlayerObservation(type="saw_player", tick=tick, subject=subject, room=room)
        for subject, room, tick in seen
    )
    return tuple(observations)


def _two_voice_responder() -> Callable[[str, type[BaseModel] | None], str]:
    """p-1 opens accusing p-2 with relevant backing; p-3's opt-in vouches
    for p-1 with its own backing -- two independent voices on p-2 (and the
    corroboration makes p-1 a defended subject in the same meeting)."""

    return _make_responder(
        accusations={"p-1": "p-2", "p-2": None},
        observations={
            "p-1": _backed_observations(
                seen=(("p-2", "ADMIN", 402), ("p-3", "MEDBAY", 404))
            ),
            "p-3": (
                SawPlayerObservation(
                    type="saw_player", tick=402, subject="p-2", room="ADMIN"
                ),
            ),
        },
        claims_by={
            "p-3": (
                CorroborationClaim(
                    type="corroboration",
                    supports="p-1",
                    on_tick=402,
                    reason="p-3 vouches for p-1",
                ),
            ),
        },
    )


def _single_voice_responder() -> Callable[[str, type[BaseModel] | None], str]:
    """The two-voice shape minus the second voice: p-3 opts in with the
    same backing but vouches for nobody -- the channel must stay invisible."""

    return _make_responder(
        accusations={"p-1": "p-2", "p-2": None},
        observations={
            "p-1": _backed_observations(
                seen=(("p-2", "ADMIN", 402), ("p-3", "MEDBAY", 404))
            ),
            "p-3": (
                SawPlayerObservation(
                    type="saw_player", tick=402, subject="p-2", room="ADMIN"
                ),
            ),
        },
    )


def _fold_participants(
    *, p4_role: str = "CREWMATE", p4_teammates: tuple[PlayerId, ...] = ()
) -> tuple[MeetingParticipant, ...]:
    return (
        _participant(
            "p-1",
            suspicion_graph=(
                SuspicionEntry(player_id="p-2", suspicion=0.75, trust=0.5),
            ),
        ),
        _participant("p-2", role="IMPOSTOR" if p4_teammates else "CREWMATE"),
        _participant("p-3"),
        _participant(
            "p-4",
            role=p4_role,
            suspicion_graph=(
                SuspicionEntry(player_id="p-1", suspicion=0.5, trust=0.5),
                SuspicionEntry(player_id="p-2", suspicion=0.55, trust=0.5),
            ),
            fellow_impostor_ids=p4_teammates,
        ),
    )


def _stub_vote_graph(client: _ScriptedLLMClient, *, voter: str) -> str:
    """The ``suspicion=...`` block the stub vote prompt rendered for ``voter``."""

    prompt = next(
        call.prompt
        for call in client.calls
        if "PHASE=VOTE" in call.prompt and f"voter={voter}" in call.prompt
    )
    return next(line for line in prompt.splitlines() if line.startswith("suspicion="))


class TestDeriveBeliefEvidenceFolded:
    """``derive_belief_evidence`` marks the two-witness subjects (Task 10.7).

    The folded mark lives on the meeting context
    (``MeetingBeliefEvidence.pre_vote_folded``), never in the belief
    store, and ``extract_belief_evidence`` delegates to the same
    derivation -- one home, two invocation points.
    """

    def _two_voice_turns(self) -> tuple[MeetingTurn, ...]:
        opening = MeetingTurn(
            turn_id="m-1:turn-0",
            turn_index=0,
            speaker="p-1",
            turn_kind="opening",
            reply_to=None,
            observations=_backed_observations(seen=(("p-2", "ADMIN", 402),)),
            claims=(
                AccusationClaim(
                    type="accusation", against="p-2", confidence=0.7, reason="seen"
                ),
            ),
            free_text="I accuse p-2.",
        )
        opt_in = MeetingTurn(
            turn_id="m-1:turn-1",
            turn_index=1,
            speaker="p-3",
            turn_kind="opt_in",
            reply_to=None,
            observations=(
                SawPlayerObservation(
                    type="saw_player", tick=402, subject="p-2", room="ADMIN"
                ),
            ),
            claims=(
                CorroborationClaim(
                    type="corroboration",
                    supports="p-1",
                    on_tick=402,
                    reason="vouch",
                ),
            ),
            free_text="I vouch for p-1.",
        )
        return (opening, opt_in)

    def test_two_voice_subject_is_marked_folded(self) -> None:
        evidence = derive_belief_evidence(
            MeetingTranscript(turns=self._two_voice_turns()),
            contradictions=(),
            roster=frozenset({"p-1", "p-2", "p-3", "p-4"}),
        )

        assert evidence.pre_vote_folded == ("p-2",)
        # Two voices is the fold band, not the single-witness inform band.
        assert evidence.pre_vote_informed == ()
        assert evidence.accused == ("p-2",)
        # The corroboration moves in the same evidence -- the symmetric
        # defended-subject channel.
        assert evidence.corroborated == ("p-1",)

    def test_single_voice_subject_is_marked_informed(self) -> None:
        # Task 10.15: one observation-backed voice is below the fold bar but
        # is the single-witness INFORM band -- marked ``pre_vote_informed``,
        # never ``pre_vote_folded``.
        opening, _ = self._two_voice_turns()
        evidence = derive_belief_evidence(
            MeetingTranscript(turns=(opening,)),
            contradictions=(),
            roster=frozenset({"p-1", "p-2", "p-3", "p-4"}),
        )

        assert evidence.pre_vote_folded == ()
        assert evidence.pre_vote_informed == ("p-2",)
        assert evidence.accused == ("p-2",)

    def test_extract_delegates_to_the_one_derivation(self) -> None:
        result = _result_with(
            turns=self._two_voice_turns(), voters=("p-1", "p-2", "p-3", "p-4")
        )

        extracted = extract_belief_evidence(result)
        derived = derive_belief_evidence(
            result.transcript,
            contradictions=result.contradictions,
            roster=frozenset(ballot.voter for ballot in result.ballots),
        )

        assert extracted == derived
        assert extracted.pre_vote_folded == ("p-2",)


class TestPreVoteFoldOnProductionPath:
    """The two-half fold through ``MeetingManager.run`` (Task 10.7).

    The pre-vote half lands on every voter's rendered suspicion graph
    exactly once; the single-voice / bare-verbal channel is invisible
    (byte-identical to pre-change behaviour); the persistent per-meeting
    total for a folded subject equals the unfolded total (the mandatory
    double-fold pin); the teammate guard holds on the new channel.
    """

    def test_two_voice_fold_moves_every_living_listener_once(self) -> None:
        result, client = _run_meeting(
            _two_voice_responder(), participants=_fold_participants()
        )

        evidence = extract_belief_evidence(result)
        assert evidence.pre_vote_folded == ("p-2",)
        assert evidence.pre_vote_voice_counts == (("p-2", 2),)
        # Every living listener's rendered view of p-2 moved by the graduated
        # TWO-voice +0.12 (Task 13.7) over their snapshot -- once, on the
        # quantized lattice (the stub renders the same %.2f the production
        # template uses): p-1's 0.75 eyewitness prior reads 0.87; p-3 had no
        # row and the fold materialises the 0.5-prior bump at 0.62 (now ACROSS
        # the §4.6 gate where the flat +0.05 inform left it at 0.55); p-4's
        # 0.55 parked-listener prior crosses to 0.67. The same-phase
        # corroboration of p-1 (the vouched accuser) renders symmetrically and
        # stays the flat -0.05: p-4's existing 0.50 row reads 0.45.
        assert _stub_vote_graph(client, voter="p-1") == "suspicion=p-2:0.87/0.50"
        assert (
            _stub_vote_graph(client, voter="p-3")
            == "suspicion=p-1:0.45/0.50,p-2:0.62/0.50"
        )
        assert (
            _stub_vote_graph(client, voter="p-4")
            == "suspicion=p-1:0.45/0.50,p-2:0.67/0.50"
        )
        # The subject votes too: no self row, and the defended accuser
        # renders lowered in their graph as well.
        assert _stub_vote_graph(client, voter="p-2") == "suspicion=p-1:0.45/0.50"

    def test_folded_per_meeting_total_equals_unfolded_total(self) -> None:
        # THE mandatory double-fold pin, meeting-level: the pre-vote fold
        # REPLACES the post-vote accused-bump, so after the orchestrator's
        # standing absorb the folded subject's persistent total is the
        # identical single +0.05 a single-voice meeting produces.
        folded_result, _ = _run_meeting(
            _two_voice_responder(), participants=_fold_participants()
        )
        single_result, _ = _run_meeting(
            _single_voice_responder(), participants=_fold_participants()
        )
        folded_evidence = extract_belief_evidence(folded_result)
        single_evidence = extract_belief_evidence(single_result)
        assert folded_evidence.pre_vote_folded == ("p-2",)
        assert single_evidence.pre_vote_folded == ()

        def absorb(evidence: MeetingBeliefEvidence) -> AgentMemory:
            memory = _voter_memory("p-4", sightings=("p-1", "p-2", "p-3"))
            absorb_meeting_evidence(
                memory,
                accused=evidence.accused,
                corroborated=evidence.corroborated,
                contradicted=evidence.contradicted,
            )
            return memory

        folded_view = absorb(folded_evidence).beliefs.view("p-2")
        single_view = absorb(single_evidence).beliefs.view("p-2")

        assert folded_view.suspicion == pytest.approx(
            _DEFAULT_TEST_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )
        assert folded_view.suspicion == single_view.suspicion

    def test_single_voice_inform_moves_every_living_listener_once(self) -> None:
        # Task 10.15 single-witness inform (audit 2026-06-13 C-C-1): one
        # observation-backed accuser is below the two-witness bar but is an
        # INFORM voice -- it spreads +0.05 to every living listener's view of
        # p-2 PRE-VOTE, on the same quantized lattice as the fold. The pin is
        # wired to the owner principle:
        #   * p-3 is a BASELINE listener (no prior row, 0.50): the inform
        #     materialises 0.55, which STAYS UNDER the 0.60 gate -- informs,
        #     never ejects a baseline listener alone (the anti-single-signal
        #     tripwire);
        #   * p-4 is a NEAR-GATE listener (0.55 prior): the inform CROSSES it
        #     to 0.60 (its own prior PLUS the witness's inform);
        #   * p-1's 0.75 eyewitness prior reads 0.80.
        # The single-voice responder vouches for nobody, so there is no
        # corroboration: p-1's rows are unmoved.
        result, client = _run_meeting(
            _single_voice_responder(), participants=_fold_participants()
        )

        evidence = extract_belief_evidence(result)
        assert evidence.pre_vote_folded == ()
        assert evidence.pre_vote_informed == ("p-2",)
        assert _stub_vote_graph(client, voter="p-1") == "suspicion=p-2:0.80/0.50"
        assert _stub_vote_graph(client, voter="p-3") == "suspicion=p-2:0.55/0.50"
        assert (
            _stub_vote_graph(client, voter="p-4")
            == "suspicion=p-1:0.50/0.50,p-2:0.60/0.50"
        )

        # The pre-vote inform REPLACES the post-vote single-accuser bump, so
        # the persistent per-meeting total stays a single +0.05 -- the inform
        # changes WHEN the listener sees the bump (pre-vote), never how much
        # persists (the double-fold guard on the new channel).
        memory = _voter_memory("p-4", sightings=("p-1", "p-2", "p-3"))
        absorb_meeting_evidence(
            memory,
            accused=evidence.accused,
            corroborated=evidence.corroborated,
            contradicted=evidence.contradicted,
        )
        assert memory.beliefs.view("p-2").suspicion == pytest.approx(
            _DEFAULT_TEST_SUSPICION + ACCUSATION_SUSPICION_DELTA
        )

    def test_bare_verbal_pile_on_folds_nothing(self) -> None:
        # THE bare-accusation pin (Task 10.15 owner-principle tripwire): any
        # number of bare verbal accusers with NO first-hand observation
        # backing stays below BOTH bands -- a three-accuser chain whose only
        # located content sits at the kill scene derives no voices, so the
        # single-witness inform folds NOTHING (the seed-30-class pile-on
        # still converts nothing), renders unchanged snapshots, and keeps
        # the standing post-vote accumulator math.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": "p-3", "p-3": "p-1"},
            observations={
                "p-1": _backed_observations(seen=(("p-2", "MEDBAY", 404),)),
            },
        )
        result, client = _run_meeting(responder, participants=_fold_participants())

        evidence = extract_belief_evidence(result)
        assert evidence.accused == ("p-1", "p-2", "p-3")
        assert evidence.pre_vote_folded == ()
        assert evidence.pre_vote_informed == ()
        assert (
            _stub_vote_graph(client, voter="p-4")
            == "suspicion=p-1:0.50/0.50,p-2:0.55/0.50"
        )

    def test_echoed_accusers_inform_not_fold_on_production_path(self) -> None:
        # The H-4 fix end-to-end: two distinct observation-backed accusers
        # of p-2 whose free-text rationales are verbatim copies collapse to
        # ONE voice -- so p-2 takes the single-witness INFORM (one +0.05
        # pre-vote spread), NOT the two-witness fold the copied independence
        # would otherwise manufacture.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": "p-3"},
            observations={
                "p-1": _backed_observations(seen=(("p-2", "ADMIN", 402),)),
                "p-3": (
                    SawPlayerObservation(
                        type="saw_player", tick=402, subject="p-2", room="ADMIN"
                    ),
                ),
            },
            free_text={
                "p-1": "p-2 left the scene without helping.",
                "p-3": "p-2 left the scene without helping.",
            },
        )
        result, client = _run_meeting(responder, participants=_fold_participants())

        evidence = extract_belief_evidence(result)
        assert evidence.pre_vote_folded == ()
        assert evidence.pre_vote_informed == ("p-2",)
        # The inform still spreads exactly one +0.05: p-4's near-gate 0.55
        # crosses to 0.60, never to 0.65 (no doubled fold from the echo).
        assert (
            _stub_vote_graph(client, voter="p-4")
            == "suspicion=p-1:0.50/0.50,p-2:0.60/0.50"
        )

    def test_inform_leaves_the_equal_tally_and_tie_skip_frozen(self) -> None:
        # Frozen-tally regression (Task 10.15 DoD): the inform is
        # belief-spread, NOT a tally reweight. p-2 is informed (one
        # observation-backed voice) and the listeners' rendered suspicion
        # moves, but the tally still counts equal votes and resolves a
        # 2-eject / 2-SKIP tie to SKIP -- byte-unchanged from the frozen
        # rule. A freshly-informed listener crossing the gate is the
        # listener's MUST-vote, never a tally-side reweight.
        responder = _make_responder(
            accusations={"p-1": "p-2", "p-2": None},
            observations={
                "p-1": _backed_observations(seen=(("p-2", "ADMIN", 402),)),
            },
            vote_targets={"p-1": "p-2", "p-4": "p-2", "p-2": "SKIP", "p-3": "SKIP"},
        )
        result, _ = _run_meeting(responder, participants=_fold_participants())

        assert extract_belief_evidence(result).pre_vote_informed == ("p-2",)
        # Two eject-p-2 vs two SKIP: the frozen tie -> SKIP rule holds.
        assert result.outcome == "SKIPPED"
        assert result.ejected_player_id is None

    def test_no_fold_evidence_keeps_the_snapshot_object(self) -> None:
        # The fast-path identity: evidence that folds nothing (no
        # two-voice subject, no relevance-gated corroboration) returns
        # the voter's snapshot graph object untouched -- the channel is
        # invisible until independence is met, byte-identically.
        graph = (SuspicionEntry(player_id="p-2", suspicion=0.55, trust=0.5),)
        evidence = MeetingBeliefEvidence(
            accused=("p-2",), corroborated=(), contradicted=()
        )

        out = _suspicion_graph_with_contradictions(
            voter_id="p-1",
            suspicion_graph=graph,
            contradictions=(),
            evidence=evidence,
        )

        assert out is graph

    def test_teammate_guard_holds_on_the_fold_channel(self) -> None:
        # DESIGN.md §4.7 on the new channel: the folded subject is the
        # impostor voter's teammate, so the impostor's rendered graph
        # carries NO p-2 edge at all (no bump, no row), while crew
        # listeners take the fold normally.
        result, client = _run_meeting(
            _two_voice_responder(),
            participants=_fold_participants(p4_role="IMPOSTOR", p4_teammates=("p-2",)),
        )

        assert extract_belief_evidence(result).pre_vote_folded == ("p-2",)
        # The impostor voter (p-4) carries NO teammate edge -- the graduated
        # two-voice lift rides the §4.7 guard exactly as the flat bump did.
        assert _stub_vote_graph(client, voter="p-4") == "suspicion=p-1:0.45/0.50"
        # The crew listener takes the graduated +0.12 fold: 0.75 -> 0.87.
        assert _stub_vote_graph(client, voter="p-1") == "suspicion=p-2:0.87/0.50"

    def test_fold_is_deterministic_across_runs(self) -> None:
        first_result, first_client = _run_meeting(
            _two_voice_responder(), participants=_fold_participants()
        )
        second_result, second_client = _run_meeting(
            _two_voice_responder(), participants=_fold_participants()
        )

        assert first_result == second_result
        assert [call.prompt for call in first_client.calls] == [
            call.prompt for call in second_client.calls
        ]


class TestRenderAfterFoldConsistency:
    """The render-after-fold DoD pin, against the REAL vote template.

    When a listener's view of a folded subject crosses 0.60 pre-vote,
    the rendered vote prompt shows the post-fold value AND the in-prompt
    §4.6 verdict reads MUST vote -- graph and verdict computed from ONE
    post-fold state source (the template derives the verdict max from
    the same ``suspicion_graph`` rows it renders, so a stale pre-fold
    graph anywhere in the path would break both assertions at once).
    """

    @staticmethod
    def _real_template_responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            return _two_voice_responder()(prompt, schema)
        # The real vote_ballot.j2 prompt: the manager overrides the voter
        # field, so a fixed stub ballot suffices.
        return _vote_json(voter="p-0", target="SKIP")

    @staticmethod
    def _single_voice_real_template_responder(
        prompt: str, schema: type[BaseModel] | None
    ) -> str:
        # The single-witness inform (one voice -> the flat +0.05): post-13.7
        # this is the band that still leaves a no-prior listener UNDER the
        # gate, so it is the only fold that can demonstrate the sub-gate
        # MUST-SKIP verdict against the real template.
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            return _single_voice_responder()(prompt, schema)
        return _vote_json(voter="p-0", target="SKIP")

    def _vote_prompts(
        self, responder: Callable[[str, type[BaseModel] | None], str]
    ) -> dict[str, str]:
        client = _ScriptedLLMClient(responder=responder)
        manager = MeetingManager(
            llm_client=client,
            crewmate_report_prompt=_crewmate_report_prompt,
            impostor_report_prompt=_impostor_report_prompt,
            statement_prompt=_statement_prompt,
            vote_prompt=vote_ballot_prompt,
        )
        _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_fold_participants(),
            )
        )
        prompts: dict[str, str] = {}
        for call in client.calls:
            if call.schema_name == "VoteBallot":
                assert call.agent_id is not None
                prompts[call.agent_id] = call.prompt
        return prompts

    def test_fold_crossed_listener_renders_post_fold_value_and_must_vote(
        self,
    ) -> None:
        # The graduated two-voice fold (Task 13.7, +0.12): p-4's 0.55 prior
        # crosses to 0.67 -- the graph row and the §4.6 verdict are computed
        # from ONE post-fold source, so both read the same post-fold value.
        prompts = self._vote_prompts(self._real_template_responder)
        crossed = prompts["p-4"]

        # The graph row shows the post-fold value, on the quantized
        # 2-decimal lattice...
        assert "- `p-2`: suspicion 0.67, trust 0.50" in crossed
        # ...and the §4.6 verdict -- computed by the frozen template from
        # the SAME rendered graph -- reads the post-fold max and the
        # MUST-vote imperative (the gate computation itself untouched).
        assert parse_rendered_max_suspicion(crossed) == pytest.approx(0.67)
        assert "you MUST vote to eject; you may NOT skip" in crossed
        assert 'you MUST set `target` to `"SKIP"`' not in crossed

    def test_sub_gate_listener_still_reads_must_skip(self) -> None:
        # The single-witness inform materialises p-2 at 0.55 for the no-prior
        # listener: below the gate, so the same one-source verdict reads MUST
        # SKIP -- the fold moves values, never the §4.6 rule. (Two voices would
        # cross this same listener to 0.62 by design, so the sub-gate case is
        # the single-voice band post-13.7.)
        prompts = self._vote_prompts(self._single_voice_real_template_responder)
        sub_gate = prompts["p-3"]

        assert "- `p-2`: suspicion 0.55, trust 0.50" in sub_gate
        assert parse_rendered_max_suspicion(sub_gate) == pytest.approx(0.55)
        assert 'you MUST set `target` to `"SKIP"`' in sub_gate


class TestCommittedBytes107FoldPins:
    """The Task 10.7 fold pins, walked offline against the W2 re-record.

    The two-witness fold, replayed over the recorded per-voter rendered
    suspicion graphs, lifts additional listeners over the §4.6 gate on the
    converting meetings (seed 27 m1 on the phase-11 Wave-1 re-record), and the
    lone bare pile-on (seed 20 m1, p-2: two accusers, no observation-backed
    voice) still folds nothing -- the fold leaves p-2 byte-unchanged, so the
    voiceless pile-on drives no conversion (the STOP-pin tripwire holds; the
    owner principle was re-verified set-wide -- no voiceless subject is folded
    in any committed meeting). Re-anchored from the W1 coordinates (seed 30 m1 /
    seed 38 m0 / seed 3 m0), kept as stable identifiers, to the meeting now
    exhibiting each shape: vents thinned the bare pile-ons to one, and it now
    sits on an impostor (p-2) already carrying over-gate suspicion, so the
    'under-gate everywhere / zero votes' extras of the prior pin give way to the
    mechanism-level invariant the tripwire actually guards.
    """

    @staticmethod
    def _recorded_vote_graphs(
        entry: MeetingReplayEntry,
    ) -> dict[str, dict[str, float]]:
        """Per-voter rendered suspicion graph from the committed vote prompts."""

        graphs: dict[str, dict[str, float]] = {}
        for call in entry.llm_calls:
            if _SUSPICION_GRAPH_HEADER not in call.prompt:
                continue
            assert call.agent_id is not None
            block = call.prompt.split(_SUSPICION_GRAPH_HEADER, 1)[1].split("## ", 1)[0]
            graphs[call.agent_id] = {
                match.group("pid"): float(match.group("sus"))
                for match in _SUSPICION_GRAPH_ROW_RE.finditer(block)
            }
        return graphs

    @staticmethod
    def _replay_pre_vote_fold(
        entry: MeetingReplayEntry,
    ) -> tuple[
        MeetingBeliefEvidence, dict[str, dict[str, float]], dict[str, dict[str, float]]
    ]:
        """Replay the implemented rule over the recorded voter graphs.

        Returns ``(evidence, recorded_graphs, folded_graphs)`` where the
        folded graphs are each voter's recorded rendered graph with the
        pre-vote half applied through the production helper -- exactly
        the values the vote prompts would have rendered had the fold
        been live at recording time.
        """

        roster = frozenset(ballot.voter for ballot in entry.ballots)
        evidence = derive_belief_evidence(
            entry.transcript, contradictions=entry.contradictions, roster=roster
        )
        recorded = TestCommittedBytes107FoldPins._recorded_vote_graphs(entry)
        folded: dict[str, dict[str, float]] = {}
        for voter, graph in recorded.items():
            entries = _suspicion_graph_with_contradictions(
                voter_id=voter,
                suspicion_graph=tuple(
                    SuspicionEntry(player_id=pid, suspicion=value, trust=0.5)
                    for pid, value in sorted(graph.items())
                ),
                contradictions=(),
                evidence=evidence,
            )
            folded[voter] = {item.player_id: item.suspicion for item in entries}
        return evidence, recorded, folded

    def test_seed30_m1_pile_on_stop_pin(self) -> None:
        # THE owner-principle tripwire, re-anchored to the phase-11 Wave-1
        # re-record. The prior bare pile-on (W2 seed 16 m0) dissolved with the
        # bytes; the lone bare pile-on left is seed 20 m1, subject p-2: TWO
        # accusers (p-6, p-9), NEITHER an observation-backed voice -- so
        # independent voices counts ZERO for p-2 and the rule must fold nothing.
        # The owner principle scoped to p-2: NO pre-vote fold and no
        # corroboration for p-2, and the fold leaves p-2's rendered value
        # BYTE-UNCHANGED for every voter -- the voiceless pile-on adds nothing
        # through the fold, so it creates no new gate-crossing. Unlike the prior
        # clean pin, p-2 is an IMPOSTOR already carrying over-gate suspicion from
        # earlier meetings (rendered 1.0/0.7/1.0 for p-1/p-6/p-9), so it draws
        # those three carried-suspicion votes -- but a 3-3 split ties to SKIP and
        # p-2 is NOT ejected: the bare pile-on still converts nothing. (The
        # owner-principle invariant was re-verified set-wide: no voiceless
        # subject is folded in any committed meeting.) A qualifying second VOICE
        # folding p-2 here is the STOP-and-escalate condition of the task
        # contract.
        entry = _committed_meeting(20, 1)
        roster = frozenset(ballot.voter for ballot in entry.ballots)
        rederived_flags = detect_contradictions(entry.transcript, roster=roster)
        evidence = derive_belief_evidence(
            entry.transcript, contradictions=rederived_flags, roster=roster
        )
        # p-2 is a bona-fide bare pile-on: two distinct accusers, zero voices.
        accusers = sorted(
            {
                turn.speaker
                for turn in entry.transcript.turns
                for claim in turn.claims
                if isinstance(claim, AccusationClaim)
                and claim.against == "p-2"
                and turn.speaker != "p-2"
            }
        )
        assert accusers == ["p-6", "p-9"]
        voices = independent_voices(entry.transcript, roster=roster)
        assert voices.get("p-2", ()) == ()

        _, recorded, folded = self._replay_pre_vote_fold(entry)
        assert "p-2" not in evidence.pre_vote_folded
        assert "p-2" not in evidence.corroborated
        assert recorded and folded
        for voter, graph in folded.items():
            if "p-2" in recorded[voter]:
                # The fold leaves p-2 byte-unchanged: any over-gate value is
                # carried suspicion, not the voiceless pile-on, and the fold
                # creates no NEW gate-crossing on p-2.
                assert graph["p-2"] == pytest.approx(recorded[voter]["p-2"])
                assert (graph["p-2"] >= 0.60) == (recorded[voter]["p-2"] >= 0.60)
        # The recorded meeting ejected nobody: the bare pile-on converted nothing
        # (p-2's sub-plurality votes ride carried suspicion, not the pile-on).
        assert entry.ejected_player_id is None

    def test_seed38_m0_fold_lifts_listeners_over_gate_and_converts(self) -> None:
        # The two-witness fold's conversion on the phase-11 Wave-1 re-record.
        # NOTE: the fold is LIVE at record time, so the recorded vote graphs are
        # ALREADY post-fold -- read them directly (replaying the fold over them
        # would double-apply). The W1 seed-38 m0 row moved with the bytes; its
        # analog here is seed 27 m1: a two-voice fold on impostor p-4 (voices
        # p-3/p-8) lifts the three LISTENERS p-1/p-2/p-9 over the §4.6 gate in
        # the recorded graphs; all three MUST-vote and target p-4, and p-4 is
        # ejected. The §6.3 fold conversion, end to end on real bytes.
        entry = _committed_meeting(27, 1)
        assert entry.ejected_player_id == "p-4"
        _, recorded, _ = self._replay_pre_vote_fold(entry)
        voices = set(
            independent_voices(
                entry.transcript,
                roster=frozenset(ballot.voter for ballot in entry.ballots),
            ).get("p-4", ())
        )
        assert len(voices) >= 2  # the two-witness fold drove the conversion
        ballots = {ballot.voter: ballot.target for ballot in entry.ballots}
        listeners_over_gate = sorted(
            voter
            for voter, graph in recorded.items()
            if voter not in voices
            and graph.get("p-4", 0.0) >= 0.60
            and ballots.get(voter) == "p-4"
        )
        assert listeners_over_gate == ["p-1", "p-2", "p-9"]

    def test_seed3_m0_defended_subject_corroborated_not_folded(self) -> None:
        # Same-phase symmetry (re-anchored to the phase-11 Wave-3 re-record): a
        # defended subject's vouches are ingested as a CORROBORATION (which
        # lowers its suspicion same-phase), never as a pile-on fold. The W1
        # seed-3 m0 row moved with the bytes (seed 3 collapsed to a single
        # meeting under the sabotage stall, dropping the shape off the seed); its
        # analog here is seed 16 m0: the corroborated subject p-4 (a crewmate,
        # with ZERO accusation voices, so it can only reach the corroboration
        # channel) is never folded, while a separate impostor p-1 takes the fold.
        # The audited suspicion-math (a corroboration drops the defended subject
        # below the §4.6 gate) is covered by the synthetic corroboration-delta
        # tests; here we pin that the bytes route the defended subject to the
        # corroboration channel, not the fold.
        entry = _committed_meeting(16, 0)
        roster = frozenset(ballot.voter for ballot in entry.ballots)
        rederived_flags = detect_contradictions(entry.transcript, roster=roster)
        evidence = derive_belief_evidence(
            entry.transcript, contradictions=rederived_flags, roster=roster
        )

        # The defended subject reaches the corroboration channel with no
        # accusation voice of its own, so the fold could never have claimed it.
        assert independent_voices(entry.transcript, roster=roster).get("p-4", ()) == ()
        assert "p-4" in evidence.corroborated
        assert "p-4" not in evidence.pre_vote_folded
        assert evidence.pre_vote_folded == ("p-1",)


# ---------------------------------------------------------------------------
# Task 10.9.1: vote-ballot fail-soft (PR #147 finding F1 — the seed-8
# vote-truncation abort). A ballot completion that fails schema validation
# degrades to the default SKIP with VOTE_PARSE_DEFAULT_MARKER instead of
# propagating and killing the game; the deadline path is byte-unchanged.
# ---------------------------------------------------------------------------

# The seed-8 shape: a rationale rambles toward the frozen 1024-token vote cap
# and the JSON is cut mid-string ("Invalid JSON: EOF while parsing a string").
_TRUNCATED_BALLOT_JSON = (
    '{"voter": "p-2", "target": "p-4", "confidence": 0.72, '
    '"primary_reason_id": null, "considered_alternatives": [], '
    '"rationale_text": "p-4 was in ELECTRICAL with the body and I saw them '
    "leave right before the report, which means the only consistent story"
)


def _expected_parse_default_rationale(raw_response: str) -> str:
    head = raw_response
    if len(head) > MARKER_QUOTED_ORIGINAL_MAX_CHARS:
        head = head[:MARKER_QUOTED_ORIGINAL_MAX_CHARS] + "..."
    return VOTE_PARSE_DEFAULT_MARKER.format(head=head)


@dataclass
class _TruncatedVoteClient:
    """Returns an unparseable (cap-truncated) payload for selected voters'
    vote calls; turns and the other votes are valid.

    Unlike :class:`_ScriptedLLMClient` it does NOT self-validate, so the
    manager's own ``VoteBallot.model_validate_json`` raises the
    ``ValidationError`` — the manager-side parse path, whose spend the
    recording client has already captured (``parse_failures`` stays empty).
    """

    truncated_voters: frozenset[str]
    truncated_text: str = _TRUNCATED_BALLOT_JSON
    vote_targets: dict[str, str] = field(default_factory=dict)

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
            voter = _extract_marker(prompt, "voter=")
            if voter in self.truncated_voters:
                text = self.truncated_text
            else:
                text = _vote_json(
                    voter=voter, target=self.vote_targets.get(voter, "SKIP")
                )
        else:
            text = _turn_json(speaker=_extract_marker(prompt, "agent_id="))
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "truncated-vote",
        )


@dataclass
class _ProviderRaisesOnVoteClient:
    """Mimics a REAL provider on the VOTE call: ``complete()`` validates
    internally and RAISES a ``ValidationError`` carrying ``LLMCallFailure``
    metadata for the selected voters (the Anthropic/Ollama
    ``_attach_parse_failure`` pattern — the provider-level retry has already
    failed by the time this surfaces), so the recording client never logs
    the burned call and the spend must ride the surfaced default. Turns and
    the other votes are valid.
    """

    truncated_voters: frozenset[str]
    truncated_text: str = _TRUNCATED_BALLOT_JSON
    input_tokens: int = 321

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
            voter = _extract_marker(prompt, "voter=")
            if voter in self.truncated_voters:
                try:
                    VoteBallot.model_validate_json(self.truncated_text)
                except ValidationError as exc:
                    _attach_parse_failure(
                        exc,
                        LLMCallFailure(
                            model="qwen3.5:9b",
                            prompt_length=len(prompt),
                            raw_response=self.truncated_text,
                            input_tokens=self.input_tokens,
                            output_tokens=1024,
                            cost_usd=0.0,
                            error_type="ValidationError",
                            error_message="Invalid JSON: EOF while parsing a string",
                        ),
                    )
                    raise
                raise AssertionError(
                    "truncated ballot json must fail validation"
                )  # pragma: no cover
            text = _vote_json(voter=voter, target="SKIP")
        else:
            text = _turn_json(speaker=_extract_marker(prompt, "agent_id="))
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "provider-raises-vote",
        )


class TestVoteBallotFailSoft:
    """A twice-failed ballot degrades to a marked SKIP; the game continues."""

    def test_truncated_ballot_degrades_to_skip_and_meeting_tallies(self) -> None:
        # p-2's ballot is the seed-8 truncation; the other three voters
        # still produce a real tally (p-4 ejected 2-1-1), proving the
        # meeting TALLIES and the run continues instead of aborting —
        # the manager-level integration pin for the F1 repair.
        client = _TruncatedVoteClient(
            truncated_voters=frozenset({"p-2"}),
            vote_targets={"p-1": "p-4", "p-3": "p-4", "p-4": "p-1"},
        )
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.outcome == "EJECTED"
        assert result.ejected_player_id == "p-4"
        assert sorted(b.voter for b in result.ballots) == ["p-1", "p-2", "p-3", "p-4"]

        degraded = next(b for b in result.ballots if b.voter == "p-2")
        assert degraded.target == "SKIP"
        assert degraded.confidence == 0.0
        assert degraded.primary_reason_id is None
        assert degraded.rationale_text == _expected_parse_default_rationale(
            _TRUNCATED_BALLOT_JSON
        )
        assert degraded.rationale_text.startswith(
            VOTE_PARSE_DEFAULT_MARKER.split("{head!r}")[0]
        )

        # Telemetry: one DefaultedCall with phase vote / trigger validation.
        # The manager-side parse of a returned payload carries no
        # parse_failures (its spend is already in llm_calls — no
        # double-count) and never reads as the opening unsure-degrade.
        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "vote"
        assert default.agent_id == "p-2"
        assert default.trigger == "validation"
        assert default.turn_index is None
        assert default.parse_failures == ()
        assert default.degraded is False
        assert manager.recovered_call_failures == ()

    def test_provider_raised_ballot_degrades_and_carries_spend(self) -> None:
        # The REAL-provider path: complete() raises before the recording
        # client can log the call, so the surfaced default carries the
        # burned spend and the marker head comes off the carried
        # LLMCallFailure.raw_response — the same bytes, hence the same
        # recorded ballot as the manager-side path.
        client = _ProviderRaisesOnVoteClient(truncated_voters=frozenset({"p-2"}))
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert result.outcome == "SKIPPED"
        degraded = next(b for b in result.ballots if b.voter == "p-2")
        assert degraded.target == "SKIP"
        assert degraded.rationale_text == _expected_parse_default_rationale(
            _TRUNCATED_BALLOT_JSON
        )

        assert len(manager.defaulted_calls) == 1
        default = manager.defaulted_calls[0]
        assert default.phase == "vote"
        assert default.trigger == "validation"
        assert len(default.parse_failures) == 1
        failure = default.parse_failures[0]
        assert failure.raw_response == _TRUNCATED_BALLOT_JSON
        assert failure.input_tokens == 321
        assert failure.output_tokens == 1024

    def test_marker_head_is_bounded_for_a_3000_char_blob(self) -> None:
        # The 10.6 60-char rule on the vote marker: a 3,000-char
        # unparseable response quotes only its bounded head.
        blob = "I must now explain every tick of my reasoning in detail " * 60
        assert len(blob) > 3000
        client = _TruncatedVoteClient(
            truncated_voters=frozenset({"p-2"}), truncated_text=blob
        )
        manager = _make_manager(
            llm_client=client,
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        degraded = next(b for b in result.ballots if b.voter == "p-2")
        assert degraded.rationale_text == VOTE_PARSE_DEFAULT_MARKER.format(
            head=blob[:MARKER_QUOTED_ORIGINAL_MAX_CHARS] + "..."
        )
        assert blob[:MARKER_QUOTED_ORIGINAL_MAX_CHARS] in degraded.rationale_text
        assert blob[MARKER_QUOTED_ORIGINAL_MAX_CHARS + 1 :] not in (
            degraded.rationale_text
        )
        assert len(degraded.rationale_text) < 200

    def test_degrade_is_deterministic_and_total_failure_still_resolves(self) -> None:
        # Every ballot truncated: the meeting still resolves (4 SKIP
        # defaults -> SKIPPED) and re-running the identical bytes yields
        # byte-identical ballots — the degrade is a pure function of the
        # failed response, so replay reconstruction cannot drift.
        def _run_once() -> MeetingResult:
            client = _TruncatedVoteClient(
                truncated_voters=frozenset({"p-1", "p-2", "p-3", "p-4"})
            )
            manager = _make_manager(
                llm_client=client,
                deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=None),
            )
            return _run(
                manager.run(
                    meeting_id="m-1",
                    trigger=_default_trigger(),
                    participants=_crew_participants(),
                )
            )

        first = _run_once()
        second = _run_once()

        assert first.outcome == "SKIPPED"
        assert first.ballots == second.ballots
        expected = _expected_parse_default_rationale(_TRUNCATED_BALLOT_JSON)
        assert all(b.rationale_text == expected for b in first.ballots)
        assert all(b.target == "SKIP" for b in first.ballots)

    def test_deadline_default_ballot_is_byte_unchanged(self) -> None:
        # The 10.9.1 net must not touch the deadline path: a wall-clock
        # miss still records the pre-existing DEFAULT_VOTE_RATIONALE
        # literal (no parse marker) with trigger="deadline".
        manager = _make_manager(
            llm_client=_SleepOnPhaseClient(sleep_phase="PHASE=VOTE"),
            deadlines=MeetingDeadlines(turn_seconds=None, vote_seconds=0.01),
        )
        result = _run(
            manager.run(
                meeting_id="m-1",
                trigger=_default_trigger(),
                participants=_crew_participants(),
            )
        )

        assert all(b.rationale_text == DEFAULT_VOTE_RATIONALE for b in result.ballots)
        assert all(
            v.trigger == "deadline" and v.parse_failures == ()
            for v in manager.defaulted_calls
        )


# ---------------------------------------------------------------------------
# Task 10.9.2: ballot-target graph guard (PR #147 finding F2 — the seed-12
# m0 unattributed ejection). An eject ballot under a MUST-vote verdict must
# name a target whose rendered suspicion meets the threshold; an under-gate
# target redirects to the argmax-rendered eligible candidate with
# BALLOT_TARGET_REDIRECT_MARKER (SKIP-coerced when only a teammate row is
# over the gate). SKIP ballots and MUST-skip verdicts are byte-unchanged.
# ---------------------------------------------------------------------------


def _graph(*rows: tuple[str, float]) -> tuple[SuspicionEntry, ...]:
    return tuple(
        SuspicionEntry(player_id=player_id, suspicion=suspicion, trust=0.5)
        for player_id, suspicion in rows
    )


def _guard_ballot(
    *,
    voter: str,
    target: str,
    confidence: float = 0.85,
    primary_reason_id: str | None = None,
    rationale_text: str = "model rationale",
) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=confidence,
        primary_reason_id=primary_reason_id,
        considered_alternatives=(),
        rationale_text=rationale_text,
    )


# The PR #147 evidence-branch fixture (branch ``phase-10-wave1-rerecord``,
# ``replays/samples/9p2i/replay-seed-12.jsonl``, meeting
# ``headless-seed-12:meeting-0``), reproduced here as recorded constants so
# the pin survives the branch being pruned. Living voters p-1..p-9 minus the
# dead p-4 / p-8; impostors p-1 and p-7 (each the other's fellow). The
# rendered per-voter graphs below are exactly the "## Your suspicion graph"
# rows of the recorded vote prompts (teammates already masked upstream), and
# the ballots are the recorded ones: p-1 was ejected 3-2-2 off three ballots
# whose voters' graphs carried NO p-1 row — their MUST-vote verdicts were
# driven by other players' over-gate rows, and they adopted the opening's
# bare verbal accusation of p-1 as ballot target instead.
_SEED12_LIVING: tuple[str, ...] = ("p-1", "p-2", "p-3", "p-5", "p-6", "p-7", "p-9")
_SEED12_TURN_0 = "headless-seed-12:meeting-0:turn-0"
_SEED12_TURN_3 = "headless-seed-12:meeting-0:turn-3"
_SEED12_GRAPHS: dict[str, tuple[SuspicionEntry, ...]] = {
    "p-1": _graph(("p-5", 0.70), ("p-6", 0.80)),
    "p-2": _graph(("p-6", 0.80)),
    "p-3": _graph(("p-6", 0.80)),
    "p-5": _graph(("p-6", 0.80)),
    "p-6": _graph(("p-5", 0.70), ("p-7", 0.70)),
    "p-7": _graph(("p-5", 0.70), ("p-6", 0.80)),
    "p-9": _graph(("p-6", 0.80)),
}
_SEED12_FELLOWS: dict[str, tuple[str, ...]] = {"p-1": ("p-7",), "p-7": ("p-1",)}
_SEED12_BALLOTS: dict[str, VoteBallot] = {
    "p-1": _guard_ballot(voter="p-1", target="SKIP", confidence=0.95),
    "p-2": _guard_ballot(
        voter="p-2", target="p-1", confidence=0.85, primary_reason_id=_SEED12_TURN_3
    ),
    "p-3": _guard_ballot(
        voter="p-3", target="p-1", confidence=0.95, primary_reason_id=_SEED12_TURN_0
    ),
    "p-5": _guard_ballot(voter="p-5", target="p-6", confidence=0.82),
    "p-6": _guard_ballot(
        voter="p-6", target="p-1", confidence=0.75, primary_reason_id=_SEED12_TURN_3
    ),
    "p-7": _guard_ballot(voter="p-7", target="SKIP", confidence=0.95),
    "p-9": _guard_ballot(voter="p-9", target="p-6", confidence=0.85),
}


def _seed12_guarded(voter: str) -> VoteBallot:
    return guard_ballot_target_graph(
        ballot=_SEED12_BALLOTS[voter],
        voter_id=voter,
        suspicion_graph=_SEED12_GRAPHS[voter],
        candidate_targets=tuple(p for p in _SEED12_LIVING if p != voter),
        skip_confidence_threshold=0.6,
        fellow_impostor_ids=_SEED12_FELLOWS.get(voter, ()),
    )


class TestBallotTargetGuardSeed12Pin:
    """The seed-12 m0 byte pin: recorded graphs + ballots through the guard."""

    def test_no_row_p1_ballots_redirect_to_the_rendered_argmax(self) -> None:
        # p-2 and p-3 MUST-vote off p-6 at 0.80 — the only row each graph
        # carries — yet both ballots named p-1 (no row at all). The guard
        # redirects each to the 0.80 argmax, p-6, preserving the original.
        for voter in ("p-2", "p-3"):
            redirected = _seed12_guarded(voter)
            assert redirected.target == "p-6"
            assert redirected.rationale_text.startswith(
                BALLOT_TARGET_REDIRECT_MARKER.format(target="p-1")
            )
            # The redirect constrains the target only: confidence and the
            # deliberation link survive.
            assert redirected.confidence == _SEED12_BALLOTS[voter].confidence
            assert (
                redirected.primary_reason_id == _SEED12_BALLOTS[voter].primary_reason_id
            )

    def test_third_no_row_ballot_redirects_by_the_pinned_tie_break(self) -> None:
        # The third no-row p-1 ballot is voter p-6's own, whose rendered
        # graph reads p-5/p-7 at 0.70 each (it holds no row about itself,
        # so the 0.80 argmax the contract names is unreachable for this
        # voter): MUST-vote at 0.70, redirect ties at 0.70, and the pinned
        # tie-break (lowest player id) lands on p-5.
        redirected = _seed12_guarded("p-6")
        assert redirected.target == "p-5"
        assert redirected.rationale_text.startswith(
            BALLOT_TARGET_REDIRECT_MARKER.format(target="p-1")
        )

    def test_over_gate_consistent_ballots_are_byte_unchanged(self) -> None:
        # p-5 and p-9 voted p-6, whose rendered row (0.80) meets the gate:
        # the guard never touches an over-gate-consistent eject ballot.
        for voter in ("p-5", "p-9"):
            assert _seed12_guarded(voter) == _SEED12_BALLOTS[voter]

    def test_skip_ballots_are_byte_unchanged(self) -> None:
        # The two impostor SKIPs (p-1, p-7) pass through untouched even
        # under their MUST-vote renders: the guard NEVER fires on a SKIP
        # ballot — eject-vs-skip stays the frozen §4.6 semantics.
        for voter in ("p-1", "p-7"):
            assert _seed12_guarded(voter) == _SEED12_BALLOTS[voter]


class TestBallotTargetGuardUnit:
    """Pure-function contract of :func:`guard_ballot_target_graph`."""

    _CANDIDATES = ("p-2", "p-3", "p-4", "p-5")

    def test_over_gate_freedom_any_met_row_passes_unredirected(self) -> None:
        # A ballot naming ANY target whose row meets the threshold passes
        # even when a higher row exists — no argmax-only over-constraint;
        # the model keeps free choice among over-gate targets.
        ballot = _guard_ballot(voter="p-1", target="p-3")
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-2", 0.90), ("p-3", 0.65)),
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
        )
        assert guarded == ballot

    def test_exactly_at_threshold_row_passes(self) -> None:
        # The gate is inclusive at the cutoff (mirrors the tally rule).
        ballot = _guard_ballot(voter="p-1", target="p-3")
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-3", 0.60)),
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
        )
        assert guarded == ballot

    def test_must_skip_verdict_eject_ballot_is_byte_unchanged(self) -> None:
        # No candidate row meets the gate: the verdict reads MUST-skip, so
        # an eject ballot stays a recorded inversion — frozen measurement
        # semantics, never papered by the guard.
        ballot = _guard_ballot(voter="p-1", target="p-4")
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-2", 0.55), ("p-3", 0.40)),
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
        )
        assert guarded == ballot

    def test_non_candidate_row_never_trips_the_verdict(self) -> None:
        # A high-suspicion row for a player OUTSIDE candidate_targets (a
        # dead / ejected player still carried in the belief rows) does not
        # produce a MUST-vote verdict — the same candidate filter the
        # frozen template applies, so guard and rendered verdict agree.
        ballot = _guard_ballot(voter="p-1", target="p-4")
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-9", 0.95), ("p-2", 0.40)),
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
        )
        assert guarded == ballot

    def test_under_gate_target_redirects_with_marker(self) -> None:
        ballot = _guard_ballot(voter="p-1", target="p-4", rationale_text="weak hunch")
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-2", 0.75), ("p-4", 0.30)),
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
        )
        assert guarded.target == "p-2"
        assert guarded.rationale_text == (
            BALLOT_TARGET_REDIRECT_MARKER.format(target="p-4") + "weak hunch"
        )

    def test_redirect_never_names_the_voter_or_a_teammate(self) -> None:
        # The eligible pool is candidate_targets minus the voter minus
        # fellow_impostor_ids: even when a teammate row is the argmax, the
        # redirect lands on the best NON-teammate row — the guard composes
        # with the §7.12 firewall by construction and can never mint the
        # betrayal ballot the firewall exists to coerce.
        ballot = _guard_ballot(voter="p-1", target="p-4")
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-5", 0.95), ("p-2", 0.70)),
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=("p-5",),
        )
        assert guarded.target == "p-2"

    def test_teammate_only_over_gate_coerces_to_skip(self) -> None:
        # An impostor voter whose ONLY over-gate row is a teammate: the
        # eligible pool's max is below the gate, so the ballot coerces to
        # SKIP with the marker and the now-stale reason id nulled (the
        # teammate-coercion discipline) — betrayal stays 0 by construction.
        ballot = _guard_ballot(
            voter="p-1",
            target="p-3",
            primary_reason_id="m-1:turn-2",
            rationale_text="pressed",
        )
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-5", 0.90), ("p-3", 0.40)),
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
            fellow_impostor_ids=("p-5",),
        )
        assert guarded.target == "SKIP"
        assert guarded.primary_reason_id is None
        assert guarded.rationale_text == (
            BALLOT_TARGET_REDIRECT_MARKER.format(target="p-3") + "pressed"
        )

    def test_tie_break_is_lowest_player_id_and_input_order_free(self) -> None:
        ballot = _guard_ballot(voter="p-1", target="p-4")
        for rows in (
            (("p-3", 0.70), ("p-2", 0.70)),
            (("p-2", 0.70), ("p-3", 0.70)),
        ):
            guarded = guard_ballot_target_graph(
                ballot=ballot,
                voter_id="p-1",
                suspicion_graph=_graph(*rows),
                candidate_targets=self._CANDIDATES,
                skip_confidence_threshold=0.6,
            )
            assert guarded.target == "p-2"

    def test_guard_is_deterministic(self) -> None:
        ballot = _guard_ballot(voter="p-1", target="p-4")
        results = {
            guard_ballot_target_graph(
                ballot=ballot,
                voter_id="p-1",
                suspicion_graph=_graph(("p-2", 0.75), ("p-3", 0.65)),
                candidate_targets=self._CANDIDATES,
                skip_confidence_threshold=0.6,
            ).model_dump_json()
            for _ in range(5)
        }
        assert len(results) == 1

    def test_marker_quoted_target_is_bounded(self) -> None:
        # The 10.6 rule: the marker quotes a bounded head of the original
        # target. Unreachable for a real roster id (roster normalization
        # runs first), pinned for the discipline.
        blob = "p-" + "9" * 3000
        ballot = _guard_ballot(voter="p-1", target=blob)
        guarded = guard_ballot_target_graph(
            ballot=ballot,
            voter_id="p-1",
            suspicion_graph=_graph(("p-2", 0.75)),
            candidate_targets=(blob, "p-2"),
            skip_confidence_threshold=0.6,
        )
        assert guarded.target == "p-2"
        assert blob[:MARKER_QUOTED_ORIGINAL_MAX_CHARS] in guarded.rationale_text
        assert len(guarded.rationale_text) < 200


class TestBallotTargetGuardVerdictEquality:
    """The guard's MUST-vote derivation equals the rendered in-prompt verdict.

    Renders the REAL frozen ``vote_ballot.j2`` over the same
    ``suspicion_graph`` / ``candidate_targets`` /
    ``skip_confidence_threshold`` the guard receives and parses the §4.6
    line back out via the shared eval helper: the guard fires on a no-row
    eject ballot exactly when the rendered verdict reads MUST-vote.
    """

    _CANDIDATES = ("p-2", "p-3", "p-4")

    def _rendered_prompt(self, graph: tuple[SuspicionEntry, ...]) -> str:
        return vote_ballot_prompt(
            voter_id="p-1",
            rendered_memory="## Your role: CREWMATE",
            transcript=MeetingTranscript(turns=()),
            contradiction_flags=(),
            suspicion_graph=graph,
            candidate_targets=self._CANDIDATES,
            skip_confidence_threshold=0.6,
        )

    def _guard_fired(self, graph: tuple[SuspicionEntry, ...]) -> bool:
        ballot = _guard_ballot(voter="p-1", target="p-4")
        return (
            guard_ballot_target_graph(
                ballot=ballot,
                voter_id="p-1",
                suspicion_graph=graph,
                candidate_targets=self._CANDIDATES,
                skip_confidence_threshold=0.6,
            )
            != ballot
        )

    @pytest.mark.parametrize(
        ("graph_rows", "expect_must_vote"),
        [
            ((("p-2", 0.80),), True),
            ((("p-2", 0.60),), True),
            ((("p-2", 0.55),), False),
            # The dead-player filter: p-9 is not a candidate, so its 0.95
            # row trips neither the rendered verdict nor the guard.
            ((("p-9", 0.95), ("p-2", 0.40)), False),
            ((), False),
        ],
    )
    def test_guard_fires_iff_rendered_verdict_reads_must_vote(
        self,
        graph_rows: tuple[tuple[str, float], ...],
        expect_must_vote: bool,
    ) -> None:
        graph = _graph(*graph_rows)
        prompt = self._rendered_prompt(graph)

        rendered_max = parse_rendered_max_suspicion(prompt)
        assert rendered_max is not None
        must_vote_rendered = rendered_max >= 0.6
        assert must_vote_rendered == expect_must_vote
        assert ("you MUST vote to eject" in prompt) == expect_must_vote

        assert self._guard_fired(graph) == expect_must_vote


class TestBallotTargetGuardOnProductionPath:
    """Chain order at the chokepoint: roster -> teammate coercion -> guard."""

    def _participants(self) -> tuple[MeetingParticipant, ...]:
        return (
            _participant("p-1"),
            _participant(
                "p-2",
                suspicion_graph=_graph(("p-3", 0.80)),
            ),
            _participant("p-3"),
            _participant("p-4"),
        )

    def test_under_gate_eject_target_is_redirected_on_the_recorded_ballot(
        self,
    ) -> None:
        # p-2's verdict reads MUST-vote off p-3 at 0.80; its ballot names
        # p-4 (no row). The RECORDED ballot carries the redirected target
        # and the marker — the seed-12 leak closed at the chokepoint.
        result, _ = _run_meeting(
            _make_responder(vote_targets={"p-2": "p-4"}),
            participants=self._participants(),
        )

        ballot = next(b for b in result.ballots if b.voter == "p-2")
        assert ballot.target == "p-3"
        assert ballot.rationale_text.startswith(
            BALLOT_TARGET_REDIRECT_MARKER.format(target="p-4")
        )

    def test_hallucinated_target_normalizes_to_skip_and_is_never_redirected(
        self,
    ) -> None:
        # Roster normalization runs FIRST: an out-of-roster target becomes
        # a marked SKIP, and the guard never fires on a SKIP — one rewrite,
        # not two, even under a MUST-vote verdict.
        result, _ = _run_meeting(
            _make_responder(vote_targets={"p-2": "p-99"}),
            participants=self._participants(),
        )

        ballot = next(b for b in result.ballots if b.voter == "p-2")
        assert ballot.target == "SKIP"
        assert INVALID_VOTE_TARGET_MARKER.format(target="p-99") in (
            ballot.rationale_text
        )
        assert BALLOT_TARGET_REDIRECT_MARKER.split("{target!r}")[0] not in (
            ballot.rationale_text
        )

    def test_teammate_ballot_coerces_to_skip_and_is_never_redirected(self) -> None:
        # The §7.12 coercion runs SECOND: an impostor's betrayal ballot is
        # already a marked SKIP by the time the guard sees it, so the
        # guard cannot redirect it back onto a living target.
        participants = (
            _participant("p-1"),
            _participant(
                "p-2",
                role="IMPOSTOR",
                suspicion_graph=_graph(("p-3", 0.80)),
                fellow_impostor_ids=("p-4",),
            ),
            _participant("p-3"),
            _participant("p-4", role="IMPOSTOR", fellow_impostor_ids=("p-2",)),
        )
        result, _ = _run_meeting(
            _make_responder(vote_targets={"p-2": "p-4"}),
            participants=participants,
        )

        ballot = next(b for b in result.ballots if b.voter == "p-2")
        assert ballot.target == "SKIP"
        assert TEAMMATE_VOTE_TARGET_MARKER.format(target="p-4") in (
            ballot.rationale_text
        )
        assert BALLOT_TARGET_REDIRECT_MARKER.split("{target!r}")[0] not in (
            ballot.rationale_text
        )

    def test_no_redirect_meeting_is_byte_identical(self) -> None:
        # Frozen-semantics regression: with every ballot either SKIP or
        # over-gate-consistent the guard is invisible — no marker anywhere.
        result, _ = _run_meeting(
            _make_responder(vote_targets={"p-2": "p-3"}),
            participants=self._participants(),
        )

        prefix = BALLOT_TARGET_REDIRECT_MARKER.split("{target!r}")[0]
        assert all(prefix not in b.rationale_text for b in result.ballots)
        ballot = next(b for b in result.ballots if b.voter == "p-2")
        assert ballot.target == "p-3"
        assert ballot.rationale_text == "stub-vote-p-2-p-3"


# ---------------------------------------------------------------------------
# Task 10.15: the single-witness inform yield, re-derived offline against the
# committed bytes (audit 2026-06-13-1816 C-C-1; re-anchored to the phase-11
# Wave-1 re-record). The inform is now LIVE at record time, so the conversions
# are the measured recording-side belief-spread (W1 read them counterfactually).
# The methodology is self-validating -- it reproduces the §4(3) partition exactly
# from the recorded vote-prompt graphs (W2: 75 / 64; W1: 59 / 37) -- before
# counting the inform yield on top. Reuses _COMMITTED_9P2I_DIR /
# _SUSPICION_GRAPH_* and the replay loader from the committed-bytes section
# above.
# ---------------------------------------------------------------------------

# A voter's own role line in a recorded prompt (the rendered memory leads with
# "## Your role: CREWMATE|IMPOSTOR"), the engine-authoritative role channel for
# identifying which living players are impostors without a separate role map.
_ROLE_LINE_RE = re.compile(r"## Your role:\s*(CREWMATE|IMPOSTOR)")


def _voter_rendered_suspicion(vote_prompt: str, *, of: str) -> float | None:
    """The suspicion the committed vote prompt rendered for ``of`` to ONE voter.

    The §6.6 graph lists only players the voter holds a non-default belief
    about, so an absent subject returns ``None`` (its default 0.50 prior, which
    the inform lifts only to 0.55 -- under the gate, never a crossing).
    """

    if _SUSPICION_GRAPH_HEADER not in vote_prompt:
        return None
    block = vote_prompt.split(_SUSPICION_GRAPH_HEADER, 1)[1].split("## ", 1)[0]
    for match in _SUSPICION_GRAPH_ROW_RE.finditer(block):
        if match.group("pid") == of:
            return float(match.group("sus"))
    return None


@dataclass(frozen=True)
class _InformYield:
    accused_not_ejected: int  # the §4(3) denominator (W2: 75, W1: 59)
    over_gate_lost_plurality: int  # the lens-C bucket (c) (W2: 63, W1: 37)
    informed_candidates: int  # of the bucket, the single-witness (1-voice) subset
    conversions: tuple[tuple[int, str, str], ...]  # (seed, meeting_id, impostor)


def _derive_inform_yield() -> _InformYield:
    """Re-derive the single-witness inform yield over the committed bytes.

    Pure function of whatever 9p2i bytes are committed (W2 after the phase-11
    Wave-1 re-record). For every meeting, for every living-and-accused impostor
    S the recorded ballots did not eject:

    * count it in the accused-not-ejected denominator (W2: 75, W1: 59);
    * if at least one living voter rendered S over the §4.6 gate, count it in
      the over-gate-lost-plurality bucket (the audit's lens-C; W2: 63,
      W1: 37);
    * if S carries exactly one independent voice (the single-witness INFORM
      band, below ``TESTIMONY_INDEPENDENCE_BAR``, under the echo-deduped
      :func:`independent_voices`), it is an inform candidate. Apply the +0.05
      inform: a CREW voter who SKIPPED and rendered S in
      ``[gate - inform, gate)`` crosses the gate and flips to eject-S (a
      baseline below that band cannot cross on the inform alone -- the owner
      principle). Re-tally with the frozen equal-votes + tie->SKIP rule; S
      CONVERTS when it becomes the strict plurality. The flip set is
      deliberately conservative (only recorded SKIP voters), so the count is a
      floor.
    """

    gate = 0.60
    inform = ACCUSATION_SUSPICION_DELTA  # the reused 9.8 +0.05 unit
    accused_not_ejected = 0
    over_gate = 0
    informed = 0
    conversions: list[tuple[int, str, str]] = []

    seeds = sorted(
        int(path.stem.split("-")[-1])
        for path in _COMMITTED_9P2I_DIR.glob("replay-seed-*.jsonl")
    )
    for seed in seeds:
        entries = [
            entry
            for entry in read_all_entries(
                _COMMITTED_9P2I_DIR / f"replay-seed-{seed}.jsonl"
            )
            if isinstance(entry, MeetingReplayEntry)
        ]
        impostors = {
            call.agent_id
            for entry in entries
            for call in entry.llm_calls
            if call.agent_id is not None
            and (match := _ROLE_LINE_RE.search(call.prompt)) is not None
            and match.group(1) == "IMPOSTOR"
        }
        for entry in entries:
            voters = [ballot.voter for ballot in entry.ballots]
            roster = frozenset(voters)
            living_impostors = sorted(impostors & roster)
            if not living_impostors:
                continue
            accused = {
                claim.against
                for turn in entry.transcript.turns
                for claim in turn.claims
                if isinstance(claim, AccusationClaim) and claim.against != turn.speaker
            }
            vote_prompts = {
                call.agent_id: call.prompt
                for call in entry.llm_calls
                if "maximum suspicion among the living ejection targets" in call.prompt
            }
            ballot_target = {ballot.voter: ballot.target for ballot in entry.ballots}
            voices = independent_voices(entry.transcript, roster=roster)
            for subject in living_impostors:
                if subject not in accused or entry.ejected_player_id == subject:
                    continue
                accused_not_ejected += 1
                rendered = {
                    voter: _voter_rendered_suspicion(vote_prompts[voter], of=subject)
                    for voter in voters
                    if voter in vote_prompts
                }
                if not any(v is not None and v >= gate for v in rendered.values()):
                    continue
                over_gate += 1
                if not 0 < len(voices.get(subject, ())) < TESTIMONY_INDEPENDENCE_BAR:
                    continue  # folded (>= bar) or bare (0) -- not the inform band
                informed += 1
                flips = [
                    voter
                    for voter in voters
                    if voter not in living_impostors
                    and ballot_target.get(voter) == "SKIP"
                    and (value := rendered.get(voter)) is not None
                    and gate - inform <= value < gate
                ]
                if not flips:
                    continue
                tally: dict[str, int] = {}
                for target in ballot_target.values():
                    tally[target] = tally.get(target, 0) + 1
                tally["SKIP"] = tally.get("SKIP", 0) - len(flips)
                tally[subject] = tally.get(subject, 0) + len(flips)
                best = max(tally.values())
                winners = [target for target, count in tally.items() if count == best]
                if winners == [subject]:
                    conversions.append((seed, entry.meeting_id, subject))

    return _InformYield(
        accused_not_ejected=accused_not_ejected,
        over_gate_lost_plurality=over_gate,
        informed_candidates=informed,
        conversions=tuple(sorted(conversions)),
    )


class TestSingleWitnessInformYieldOnCommittedBytes:
    """The Task 10.15 inform-yield bloc, walked offline over the W2 bytes.

    The deliverable number, re-anchored to the phase-11 Wave-3 re-record. The
    derivation first reproduces the §4(3) partition EXACTLY off the committed
    bytes (W2: 75 accused living-impostor meeting-subjects the ballots did not
    eject; 63 of them rendered over the §4.6 gate yet lost plurality -- the W1
    audit-2026-06-13-1816 read 59 / 37), which validates the offline oracle,
    then counts how many the single-witness inform converts WITHOUT any tally
    change.
    """

    def test_methodology_reproduces_the_audit_partition(self) -> None:
        result = _derive_inform_yield()

        # The §4(3) partition, re-derived from the phase-11 Wave-3 committed
        # bytes. The W1 audit read 59 accused-not-ejected /
        # 37 over-gate-lost-plurality; the re-record moved both (75 / 63) -- a
        # legitimate era move (the denominator and the lens-C bucket are pure
        # functions of the bytes, re-derived by the SAME offline oracle, no
        # methodology change). The accused-not-ejected 75 cross-checks the
        # effective-deflection survivals (test_wave2_metrics) exactly.
        assert result.accused_not_ejected == 75
        assert result.over_gate_lost_plurality == 63

    def test_single_witness_inform_converts_seven_of_the_sixty_three(self) -> None:
        result = _derive_inform_yield()

        # 27 of the 63 over-gate-lost-plurality subjects are
        # single-witness-informed (one observation-backed voice under
        # echo-dedup); the inform lifts a plurality of listeners over 0.60 in
        # 7 of them on the phase-11 Wave-3 re-record (prior W2: 14 of 21),
        # flipping a SKIP-plurality to an impostor-eject with the frozen
        # equal-votes + tie->SKIP tally. The flip set is still the conservative
        # one (only recorded SKIP voters whose rendered value sits in
        # [gate - inform, gate) -- a baseline below that band still cannot cross
        # on the inform alone, the owner principle); the yield FALLING despite
        # the same candidate count (the sabotage stall dropped seed-17:m1 out of
        # the over-gate bucket) is data-drift, not a rule change.
        assert result.informed_candidates == 27
        assert len(result.conversions) == 7
        assert result.conversions == (
            (9, "headless-seed-9:meeting-1", "p-4"),
            (15, "headless-seed-15:meeting-0", "p-3"),
            (19, "headless-seed-19:meeting-0", "p-6"),
            (22, "headless-seed-22:meeting-0", "p-6"),
            (31, "headless-seed-31:meeting-0", "p-3"),
            (35, "headless-seed-35:meeting-1", "p-5"),
            (41, "headless-seed-41:meeting-0", "p-1"),
        )

    def test_derivation_is_deterministic(self) -> None:
        assert _derive_inform_yield() == _derive_inform_yield()


class TestEmergencyOpeningNoBody:
    """Task 10.11.1: an EMERGENCY opening never RECORDS a found_body.

    The crewmate_report v7 emergency branch asks the model not to report a
    body, but the 9B can ignore it (flat seed 11 m0 re-narrated a stale
    corpse, which the orchestrator fail-loud guard aborted the re-record on).
    The manager re-asks ONCE, then DETERMINISTICALLY strips any
    FoundBodyObservation from the emergency opening so
    ``orchestrator.game._assert_no_emergency_opening_body`` is unreachable.
    Body-report openings keep their body untouched (the strip is gated on the
    emergency opening alone).
    """

    @staticmethod
    def _emergency_trigger() -> MeetingTrigger:
        return MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=410,
            description="p-1 called an emergency meeting at tick 410",
        )

    @staticmethod
    def _body() -> FoundBodyObservation:
        return FoundBodyObservation(
            type="found_body", tick=406, body_of="p-9", room="STORAGE"
        )

    def test_detection_keys_off_the_trigger_description(self) -> None:
        # The meeting layer carries no structured trigger kind; the manager
        # detects an emergency off the same description phrase the renderer does.
        assert _trigger_is_emergency(self._emergency_trigger())
        assert not _trigger_is_emergency(_default_trigger())

    def test_stubborn_body_is_stripped_after_one_retry(self) -> None:
        # The opener fabricates a stale body on BOTH the opening AND the retry
        # (the stubborn-9B case): the body is stripped, the strip is audited on
        # free_text, the real accusation keeps the opening a position, and the
        # orchestrator guard the recording runs is now unreachable.
        from orchestrator.game import (  # noqa: PLC0415
            _assert_no_emergency_opening_body,
        )

        body = self._body()

        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                speaker = _extract_marker(prompt, "agent_id=")
                # p-1 always re-narrates the stale body next to a real accusation.
                return _turn_json(
                    speaker=speaker,
                    accuses="p-2" if speaker == "p-1" else None,
                    observations=(body,) if speaker == "p-1" else (),
                )
            if "PHASE=VOTE" in prompt:
                return _vote_json(
                    voter=_extract_marker(prompt, "voter="), target="SKIP"
                )
            raise AssertionError(f"unrecognised prompt: {prompt!r}")

        result, client = _run_meeting(_responder, trigger=self._emergency_trigger())
        opening = result.transcript.turns[0]

        assert not any(
            isinstance(o, FoundBodyObservation) for o in opening.observations
        )
        assert opening.free_text.startswith(EMERGENCY_BODY_STRIP_MARKER)
        assert any(
            isinstance(c, AccusationClaim) and c.against == "p-2"
            for c in opening.claims
        )
        opening_calls = [c for c in client.calls if "PHASE=OPENING" in c.prompt]
        assert len(opening_calls) == 2  # one retry before the strip
        assert EMERGENCY_NO_BODY_RETRY_FEEDBACK in opening_calls[1].prompt
        # The exact condition the orchestrator guard checks now holds.
        _assert_no_emergency_opening_body(trigger_kind="emergency", result=result)

    def test_retry_recovers_a_clean_opening_without_stripping(self) -> None:
        # When the retry COMPLIES (a body-free, suspicion-framed opening) the
        # richer model opening is kept and NO strip marker is recorded.
        body = self._body()

        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                speaker = _extract_marker(prompt, "agent_id=")
                if speaker == "p-1":
                    if EMERGENCY_NO_BODY_RETRY_FEEDBACK in prompt:
                        return _turn_json(speaker=speaker, accuses="p-2")
                    return _turn_json(
                        speaker=speaker, accuses="p-2", observations=(body,)
                    )
                return _turn_json(speaker=speaker)
            if "PHASE=VOTE" in prompt:
                return _vote_json(
                    voter=_extract_marker(prompt, "voter="), target="SKIP"
                )
            raise AssertionError(f"unrecognised prompt: {prompt!r}")

        result, client = _run_meeting(_responder, trigger=self._emergency_trigger())
        opening = result.transcript.turns[0]

        assert not any(
            isinstance(o, FoundBodyObservation) for o in opening.observations
        )
        assert EMERGENCY_BODY_STRIP_MARKER not in opening.free_text
        opening_calls = [c for c in client.calls if "PHASE=OPENING" in c.prompt]
        assert len(opening_calls) == 2

    def test_body_report_opening_keeps_found_body(self) -> None:
        # Byte-stable: the strip is gated on the emergency opening, so a body
        # report's found_body is preserved exactly as before (the guard is a
        # no-op for body reports).
        body = self._body()
        result, _ = _run_meeting(
            _make_responder(observations={"p-1": (body,)}, accusations={"p-1": "p-2"}),
            trigger=_default_trigger(),
        )
        opening = result.transcript.turns[0]

        assert body in opening.observations
        assert EMERGENCY_BODY_STRIP_MARKER not in opening.free_text

    def test_body_only_emergency_opening_degrades_to_unsure_after_strip(self) -> None:
        # When the body was the opening's ONLY content, the post-strip opening
        # is position-less and degrades to unsure: both markers appear and the
        # meeting still reaches its ballots (no body survives).
        body = self._body()

        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                speaker = _extract_marker(prompt, "agent_id=")
                if speaker == "p-1":
                    return _turn_json(
                        speaker=speaker,
                        observations=(body,),
                        free_text="found a body",
                    )
                return _turn_json(speaker=speaker)
            if "PHASE=VOTE" in prompt:
                return _vote_json(
                    voter=_extract_marker(prompt, "voter="), target="SKIP"
                )
            raise AssertionError(f"unrecognised prompt: {prompt!r}")

        result, _ = _run_meeting(_responder, trigger=self._emergency_trigger())
        opening = result.transcript.turns[0]

        assert not any(
            isinstance(o, FoundBodyObservation) for o in opening.observations
        )
        assert OPENING_UNSURE_DEGRADE_MARKER in opening.free_text
        assert EMERGENCY_BODY_STRIP_MARKER in opening.free_text

    def test_emergency_opening_without_a_body_is_unchanged(self) -> None:
        # The desired case: a suspicion-framed emergency opening with no body
        # passes straight through -- no retry, no marker.
        result, client = _run_meeting(
            _make_responder(accusations={"p-1": "p-2"}),
            trigger=self._emergency_trigger(),
        )
        opening = result.transcript.turns[0]

        assert opening.observations == ()
        assert EMERGENCY_BODY_STRIP_MARKER not in opening.free_text
        opening_calls = [c for c in client.calls if "PHASE=OPENING" in c.prompt]
        assert len(opening_calls) == 1

    def test_strip_is_deterministic(self) -> None:
        body = self._body()

        def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
            if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
                speaker = _extract_marker(prompt, "agent_id=")
                return _turn_json(
                    speaker=speaker,
                    accuses="p-2" if speaker == "p-1" else None,
                    observations=(body,) if speaker == "p-1" else (),
                )
            if "PHASE=VOTE" in prompt:
                return _vote_json(
                    voter=_extract_marker(prompt, "voter="), target="SKIP"
                )
            raise AssertionError(f"unrecognised prompt: {prompt!r}")

        first, _ = _run_meeting(_responder, trigger=self._emergency_trigger())
        second, _ = _run_meeting(_responder, trigger=self._emergency_trigger())
        assert (
            first.transcript.turns[0].model_dump_json()
            == second.transcript.turns[0].model_dump_json()
        )
