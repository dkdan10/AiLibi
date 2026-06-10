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

from agents.memory.episodic import EpisodicEvent
from agents.memory.store import AgentMemory, render_for_prompt
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.provider import LLMCallFailure, _attach_parse_failure  # noqa: PLC2701
from llm.fake_provider import FakeProvider
from meetings.manager import (
    DEFAULT_TURN_FREE_TEXT,
    DEFAULT_VOTE_RATIONALE,
    INVALID_ACCUSATION_TARGET_MARKER,
    INVALID_REASON_ID_MARKER,
    INVALID_VOTE_TARGET_MARKER,
    TEAMMATE_VOTE_TARGET_MARKER,
    LLMProviderError,
    MeetingBeliefEvidence,
    MeetingConfig,
    MeetingDeadlines,
    MeetingManager,
    MeetingParticipant,
    MeetingTrigger,
    SuspicionEntry,
    _drop_invalid_accusation_targets,  # noqa: PLC2701
    _normalize_self_alibi_subjects,  # noqa: PLC2701
    _suspicion_graph_with_contradictions,  # noqa: PLC2701
    coerce_teammate_ballot_to_skip,
    drop_teammate_statement_target,
    exclude_teammate_accusation_claims,
    extract_belief_evidence,
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


def _crewmate_report_prompt(
    *,
    agent_id: PlayerId,
    current_tick: int,
    meeting_trigger: str,
    rendered_memory: str,
    public_transcript: str,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
    living_ids: tuple[PlayerId, ...] = (),
) -> str:
    return (
        f"PHASE=OPENING ROLE=CREWMATE agent_id={agent_id} tick={current_tick}\n"
        f"TRIGGER: {meeting_trigger}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"{_living_ids_line(living_ids)}"
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
) -> str:
    return (
        f"PHASE=OPENING ROLE=IMPOSTOR agent_id={agent_id} tick={current_tick}\n"
        f"TRIGGER: {meeting_trigger}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"{_living_ids_line(living_ids)}"
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
) -> str:
    prior = prior_turn.speaker if prior_turn is not None else "none"
    return (
        f"PHASE=TURN turn_kind={turn_kind} agent_id={agent_id} prior={prior}\n"
        f"{_fellow_impostors_line(fellow_impostor_ids)}"
        f"{_living_ids_line(living_ids)}"
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
        free_text=f"turn from {speaker}",
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

    def _responder(prompt: str, schema: type[BaseModel] | None) -> str:
        if "PHASE=OPENING" in prompt or "PHASE=TURN" in prompt:
            speaker = _extract_marker(prompt, "agent_id=")
            return _turn_json(
                speaker=speaker,
                accuses=accusations.get(speaker),
                observations=observations.get(speaker, ()),
                claims=claims_by.get(speaker, ()),
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

    def test_second_independent_sighting_corroborates_across_gate(self) -> None:
        # Corroboration converts: TWO third parties independently sight
        # the self-alibi'd reporter elsewhere -> two weak flags ->
        # 0.5 + 0.08 + 0.08 = 0.66 >= 0.60. The reporter stays ejectable
        # on a second signal; only the lone-signal railroad is gone.
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
        # not publicly incriminated.
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
        # p-1 (crew) opens with an alibi for p-5 AND a sighting placing p-5
        # elsewhere -> alibi_vs_sighting names p-5. The impostor voter p-4's
        # ballot-prompt suspicion graph carries no p-5 edge; crew p-1's does.
        responder = _make_responder(
            accusations={"p-1": None},
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
                "p-1": (
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
        surviving, dropped = _drop_invalid_accusation_targets(
            claims, living_ids=frozenset({"p-1", "p-2", "p-3", "p-4"})
        )

        # The hallucinated 'imp-2' accusation is dropped; the valid 'p-3'
        # accusation and the (non-accusation) corroboration survive in order.
        assert dropped == ("imp-2",)
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
        surviving, dropped = _drop_invalid_accusation_targets(
            claims, living_ids=frozenset({"p-1", "p-2", "p-3", "p-4"})
        )
        assert dropped == ()
        assert surviving == claims

    def test_hallucinated_opening_accusation_is_dropped_and_marked(self) -> None:
        # p-1 (the opener) accuses a non-living id; the chain cannot pass to it
        # and the metrics cannot resolve its role, so the accusation is dropped
        # before the turn is recorded, with the original preserved in free_text.
        result, _ = _run_meeting(_make_responder(accusations={"p-1": "imp-2"}))

        opening = result.transcript.turns[0]
        assert opening.speaker == "p-1"
        assert not any(isinstance(c, AccusationClaim) for c in opening.claims)
        assert opening.free_text.startswith(
            INVALID_ACCUSATION_TARGET_MARKER.format(target="imp-2")
        )
        # No recorded accusation names a non-living id, so the §11.3 accusation
        # metrics can resolve every target's role (the gp surfaced by seed 24).
        all_targets = {
            c.against
            for turn in result.transcript.turns
            for c in turn.claims
            if isinstance(c, AccusationClaim)
        }
        assert "imp-2" not in all_targets

    def test_valid_opening_accusation_passes_through(self) -> None:
        result, _ = _run_meeting(_make_responder(accusations={"p-1": "p-3"}))

        opening = result.transcript.turns[0]
        targets = [c.against for c in opening.claims if isinstance(c, AccusationClaim)]
        assert targets == ["p-3"]
        assert not opening.free_text.startswith("[invalid accusation target")


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
) -> MeetingResult:
    return MeetingResult(
        meeting_id="m-1",
        triggered_by="p-1",
        trigger_tick=410,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
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
