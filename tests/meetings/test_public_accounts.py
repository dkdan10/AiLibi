"""Public accounts must not certify another speaker's private observations."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Literal

import pytest
from pydantic import BaseModel

from agents.strategic.prompts import build_prompt_renderers
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import (
    AgentMemory,
    absorb_meeting_evidence,
    absorb_reported_testimony,
)
from agents.perception import ingest_event_observations
from engine.world import load_map
from llm.client import CallKind, LLMResponse, TokenUsage
from meetings.evidence_profile import MeetingEvidenceProfile
from meetings.manager import (
    MeetingManager,
    MeetingConfig,
    MeetingDeadlines,
    MeetingParticipant,
    MeetingTrigger,
    derive_reported_testimony,
    extract_belief_evidence,
)
from meetings.public_accounts import (
    PublicAccountValidationError,
    detect_public_account_conflicts,
    validate_public_accounts,
)
from meetings.schemas import (
    MeetingResult,
    AccusationClaim,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawVentObservation,
    TaskActivityAccount,
    VentWitnessRecord,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import detect_contradictions
from observation.public_map import PublicMapView
from observation.packet import EventObservationBatch, PlayerView
from orchestrator.boundary import public_map_from_engine_map


def _map() -> PublicMapView:
    return public_map_from_engine_map(load_map(Path("engine/maps/canonical_1.yaml")))


def _turn(speaker: str, observations: tuple[ObservationClaim, ...]) -> MeetingTurn:
    return MeetingTurn(
        turn_id=speaker,
        turn_index=0,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        observations=observations,
        free_text="unsure",
    )


class AccountClient:
    def __init__(
        self, turns: dict[str, MeetingTurn], *, fail_reply: str | None = None
    ) -> None:
        self.turns = turns
        self.fail_reply = fail_reply
        self.prompts: dict[str, list[str]] = {}

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
        assert agent_id is not None
        self.prompts.setdefault(agent_id, []).append(prompt)
        if schema is MeetingTurn:
            if agent_id == "p-1" and len(self.prompts[agent_id]) == 2:
                if self.fail_reply == "cancel":
                    raise asyncio.CancelledError
                if self.fail_reply == "deadline":
                    await asyncio.Future[None]()
            text = self.turns[agent_id].model_dump_json()
        else:
            text = VoteBallot(
                voter=agent_id,
                target="SKIP",
                confidence=0.2,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="The public accounts are insufficient.",
            ).model_dump_json()
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=4, output_tokens=3),
            cost_usd=0.0,
            model="scripted-public-accounts",
        )


async def _meeting(
    *,
    grounded: bool,
    attributed: Literal[1] | None = 1,
    common: Literal[1] | None = 1,
    own_memory: str = "Own unchanged observations.",
    reply: bool = False,
    accuse: bool = False,
    fail_reply: str | None = None,
    expected_defaults: int = 0,
) -> tuple[MeetingResult, AccountClient]:
    client = AccountClient(
        {
            "p-1": _turn(
                "p-1",
                (
                    SawVentObservation(
                        type="saw_vent", tick=5, subject="p-3", room="LABS"
                    ),
                ),
            ),
            "p-2": _turn("p-2", ()),
            "p-3": _turn("p-3", ()),
        }
    )
    client.fail_reply = fail_reply
    if accuse:
        client.turns["p-3"] = client.turns["p-3"].model_copy(
            update={
                "claims": (
                    AccusationClaim(
                        type="accusation",
                        against="p-1",
                        confidence=0.7,
                        reason="A newly stated charge.",
                    ),
                )
            }
        )
    renderers = build_prompt_renderers(
        "qwen3_6_27b",
        env={},
        public_account_version=common,
        attributed_testimony_version=attributed,
    )
    manager = MeetingManager(
        llm_client=client,
        config=MeetingConfig(
            deadlines=MeetingDeadlines(
                turn_seconds=0.01 if fail_reply == "deadline" else None,
                vote_seconds=None,
            )
        ),
        crewmate_report_prompt=renderers.crewmate_report,
        impostor_report_prompt=renderers.impostor_report,
        statement_prompt=renderers.statement,
        vote_prompt=renderers.vote,
        reporter_reasoning=False,
        corroboration_discipline=False,
        evidence_profile=MeetingEvidenceProfile(
            public_account_version=common,
            attributed_testimony_version=attributed,
            bounded_rebuttal_version=1 if reply else None,
        ),
        public_map=_map(),
    )
    participants = (
        MeetingParticipant(
            agent_id="p-1",
            role="CREWMATE",
            rendered_memory="Unchanged rendered account.",
            vent_witness_records=(
                VentWitnessRecord(subject="p-3", room="LABS", tick=5),
            )
            if grounded
            else (),
        ),
        MeetingParticipant(agent_id="p-2", role="CREWMATE", rendered_memory=own_memory),
        MeetingParticipant(
            agent_id="p-3", role="IMPOSTOR", rendered_memory="Own private cover."
        ),
    )
    result = await manager.run(
        meeting_id="m",
        trigger=MeetingTrigger(
            triggered_by="p-1",
            trigger_tick=10,
            description="p-1 called an emergency meeting",
        ),
        participants=participants,
    )
    assert len(manager.defaulted_calls) == expected_defaults + int(
        fail_reply == "deadline"
    )
    return result, client


def _assert_private_noninterference() -> None:
    before, client_before = asyncio.run(_meeting(grounded=False))
    after, client_after = asyncio.run(_meeting(grounded=True))
    assert client_before.prompts["p-2"] == client_after.prompts["p-2"]
    assert before.contradictions == after.contradictions == ()
    assert extract_belief_evidence(
        before, attributed_testimony_version=1
    ) == extract_belief_evidence(after, attributed_testimony_version=1)
    assert derive_reported_testimony(
        before, public_account_version=1
    ) == derive_reported_testimony(after, public_account_version=1)


def test_manager_and_persistent_fold_do_not_read_other_speaker_grounding() -> None:
    _assert_private_noninterference()


def test_noninterference_gate_rejects_a_planted_private_detector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def planted(
        self: MeetingManager, transcript: MeetingTranscript, **kwargs: Any
    ) -> Any:
        return tuple(
            flag.model_copy(update={"kind": "alibi_conflict", "evidence_band": "weak"})
            for flag in detect_contradictions(transcript, **kwargs)
        )

    monkeypatch.setattr(MeetingManager, "_detect_contradictions", planted)
    with pytest.raises(AssertionError):
        _assert_private_noninterference()


def test_certified_baseline_still_uses_private_vent_grounding() -> None:
    missing, _ = asyncio.run(_meeting(grounded=False, attributed=None, common=None))
    grounded, _ = asyncio.run(_meeting(grounded=True, attributed=None, common=None))
    assert missing.contradictions == ()
    assert grounded.contradictions[0].kind == "vent_sighting"
    with pytest.raises(ValueError, match="certified evidence"):
        extract_belief_evidence(grounded, attributed_testimony_version=1)


@pytest.mark.parametrize("common,attributed", [(1, None), (None, 1), (1, 1)])
def test_independent_account_arms_complete_real_meetings(
    common: Literal[1] | None,
    attributed: Literal[1] | None,
) -> None:
    result, client = asyncio.run(
        _meeting(grounded=True, common=common, attributed=attributed)
    )
    assert len(result.ballots) == len(result.transcript.turns) == 3
    assert sum(map(len, client.prompts.values())) == 6
    assert any(flag.kind == "vent_sighting" for flag in result.contradictions) is (
        attributed is None
    )


def test_own_memory_changes_only_its_entitled_prompt_inputs() -> None:
    _, before = asyncio.run(_meeting(grounded=True))
    _, after = asyncio.run(
        _meeting(
            grounded=True, own_memory="[obs opaque-own] You witnessed p-3 vent in LABS."
        )
    )
    assert before.prompts["p-2"] != after.prompts["p-2"]
    assert before.prompts["p-1"] == after.prompts["p-1"]
    assert before.prompts["p-3"] == after.prompts["p-3"]


@pytest.mark.parametrize("interval,expected", [(2, 0), (1, 0), (0, 1)])
def test_public_route_comparison_is_conditional_and_never_role_proof(
    interval: int, expected: int
) -> None:
    transcript = MeetingTranscript(
        turns=(
            _turn(
                "p-1",
                (
                    WhereaboutsClaim(type="whereabouts", room="REACTOR", tick=5),
                    WhereaboutsClaim(
                        type="whereabouts", room="STORAGE", tick=5 + interval
                    ),
                ),
            ),
        )
    )
    flags = detect_public_account_conflicts(
        transcript, roster=frozenset({"p-1"}), room_neighbors=_map().room_neighbors
    )
    assert len(flags) == expected
    if flags:
        assert flags[0].evidence_band == "weak"
        assert "If the player walked" in flags[0].description
        assert "unseen vent is not excluded" in flags[0].description
        assert flags[0].event_a_id == "turn:p-1:whereabouts:0"


def test_one_placement_does_not_invent_an_impossible_route() -> None:
    transcript = MeetingTranscript(
        turns=(
            _turn(
                "p-1", (WhereaboutsClaim(type="whereabouts", room="STORAGE", tick=7),)
            ),
        )
    )
    assert (
        detect_public_account_conflicts(
            transcript, roster=frozenset({"p-1"}), room_neighbors=_map().room_neighbors
        )
        == ()
    )


@pytest.mark.parametrize(
    "change", [{"room": "UNKNOWN"}, {"tick": 11}, {"tick": -1}, {"subject": "foreign"}]
)
def test_public_reference_gate_rejects_invalid_context(change: dict[str, Any]) -> None:
    observation = SawVentObservation(
        type="saw_vent", tick=5, room="LABS", subject="p-3"
    ).model_copy(update=change)
    with pytest.raises(PublicAccountValidationError):
        validate_public_accounts(
            _turn("p-1", (observation,)),
            roster=frozenset({"p-1", "p-3"}),
            current_tick=10,
            room_ids=frozenset(_map().room_ids),
            task_ids=frozenset(_map().task_locations),
        )


def test_task_account_retains_attribution_without_completion_evidence() -> None:
    result, _ = asyncio.run(_meeting(grounded=False))
    activity = TaskActivityAccount(
        type="task_activity",
        task_id="fuel_reserves",
        room="STORAGE",
        from_tick=3,
        to_tick=5,
    )
    result = result.model_copy(
        update={"transcript": MeetingTranscript(turns=(_turn("p-3", (activity,)),))}
    )
    assert derive_reported_testimony(result) == ()
    (statement,) = derive_reported_testimony(result, public_account_version=1)
    assert (
        statement.kind == "task_activity"
        and statement.speaker == statement.subject == "p-3"
    )
    assert (
        statement.task_id == "fuel_reserves"
        and statement.source_event_id == "turn:p-3:obs:0"
    )
    assert extract_belief_evidence(result, public_account_version=1).corroborated == ()


def test_same_tick_adjacent_placements_can_be_an_honest_walk() -> None:
    transcript = MeetingTranscript(
        turns=(
            _turn(
                "p-1",
                (
                    WhereaboutsClaim(type="whereabouts", room="ENGINEERING", tick=5),
                    WhereaboutsClaim(type="whereabouts", room="STORAGE", tick=5),
                ),
            ),
        )
    )
    assert (
        detect_public_account_conflicts(
            transcript, roster=frozenset({"p-1"}), room_neighbors=_map().room_neighbors
        )
        == ()
    )


@pytest.mark.parametrize("own_witness", [False, True])
def test_reported_vent_does_not_pin_listener_but_own_perception_stays_reliable(
    own_witness: bool,
) -> None:
    memory = AgentMemory(public_account_version=1, attributed_testimony_version=1)
    for subject in ("p-1", "p-3"):
        memory.episodic.append(
            EpisodicEvent(
                tick=0,
                type="saw_player",
                provenance="observed",
                payload={"player_id": subject, "room": "CAFETERIA", "action": None},
            )
        )
        memory.beliefs.seed_player(subject, suspicion=0.5, trust=0.5)
    if own_witness:
        ingest_event_observations(
            batch=EventObservationBatch(
                tick=5,
                agent_id="p-2",
                witnessed_actions=(PlayerView(id="p-3", room="LABS", action="vent"),),
            ),
            memory=memory.episodic,
            beliefs=memory.beliefs,
        )
    memory.episodic.append(
        EpisodicEvent(
            tick=10,
            type="self_state",
            provenance="observed",
            payload={
                "agent_id": "p-2",
                "role": "CREWMATE",
                "room": "LABS",
                "pending_task_id": None,
            },
        )
    )
    result, _ = asyncio.run(_meeting(grounded=True))
    evidence = extract_belief_evidence(
        result, public_account_version=1, attributed_testimony_version=1
    )
    absorb_meeting_evidence(
        memory,
        accused=evidence.accused,
        corroborated=evidence.corroborated,
        contradicted=evidence.contradicted,
    )
    absorb_reported_testimony(
        memory,
        statements=derive_reported_testimony(
            result, public_account_version=1, attributed_testimony_version=1
        ),
    )
    events = memory.episodic.recent(since_tick=0)
    assert sum(
        row.provenance == "observed" and row.payload.get("action") == "vent"
        for row in events
    ) == int(own_witness)
    assert any(
        row.provenance == "reported" and row.payload.get("kind") == "saw_vent"
        for row in events
    )
    assert (memory.beliefs.view("p-3").suspicion > 0.6) is own_witness


@pytest.mark.parametrize(
    "reply,accuse", [(False, False), (True, False), (False, True), (True, True)]
)
def test_account_profiles_reuse_the_single_bounded_reply(
    reply: bool, accuse: bool
) -> None:
    result, client = asyncio.run(_meeting(grounded=False, reply=reply, accuse=accuse))
    extra = int(reply and accuse)
    assert len(result.transcript.turns) == 3 + extra
    assert sum(map(len, client.prompts.values())) == 6 + extra
    assert len(result.ballots) == 3
    if extra:
        assert result.transcript.turns[-1].speaker == "p-1"
        assert result.transcript.turns[-1].reply_to == next(
            turn.turn_id for turn in result.transcript.turns if turn.speaker == "p-3"
        )


def test_account_extra_reply_deadline_defaults_once_and_still_votes() -> None:
    result, client = asyncio.run(
        _meeting(grounded=False, reply=True, accuse=True, fail_reply="deadline")
    )
    assert len(result.transcript.turns) == 4
    assert len(result.ballots) == 3
    assert sum(map(len, client.prompts.values())) == 7


def test_account_extra_reply_cancellation_propagates() -> None:
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(
            _meeting(grounded=False, reply=True, accuse=True, fail_reply="cancel")
        )


async def _future_account(self: AccountClient, **kwargs: Any) -> LLMResponse:
    agent_id = kwargs["agent_id"]
    self.prompts.setdefault(agent_id, []).append(kwargs["prompt"])
    if kwargs["schema"] is MeetingTurn:
        turn = self.turns[agent_id]
        if agent_id == "p-1":
            turn = turn.model_copy(
                update={
                    "observations": (
                        WhereaboutsClaim(type="whereabouts", room="LABS", tick=11),
                    )
                }
            )
        text = turn.model_dump_json()
    else:
        text = VoteBallot(
            voter=agent_id,
            target="SKIP",
            confidence=0.0,
            primary_reason_id=None,
            considered_alternatives=(),
            rationale_text="unsure",
        ).model_dump_json()
    return LLMResponse(
        text=text,
        usage=TokenUsage(input_tokens=4, output_tokens=3),
        cost_usd=0.0,
        model="scripted-public-accounts",
    )


def _assert_future_account_refused() -> None:
    result, client = asyncio.run(_meeting(grounded=False, expected_defaults=1))
    assert result.transcript.turns[0].observations == ()
    assert len(result.ballots) == 3
    assert sum(map(len, client.prompts.values())) == 7  # one opening retry


def test_actual_turn_validation_rejects_future_account_before_recording(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(AccountClient, "complete", _future_account)
    _assert_future_account_refused()


def test_turn_validation_gate_rejects_a_missing_chokepoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(AccountClient, "complete", _future_account)
    monkeypatch.setattr(
        "meetings.manager.validate_public_accounts", lambda *args, **kwargs: None
    )
    with pytest.raises(AssertionError):
        _assert_future_account_refused()
