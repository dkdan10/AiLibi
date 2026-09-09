"""Public accounts must not certify another speaker's private observations."""

from __future__ import annotations

import asyncio
import re
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
from api.schemas import classify_evidence
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
    AlibiClaim,
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawKillObservation,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    TaskActivityAccount,
    VentWitnessRecord,
    VoteBallot,
    WhereaboutsClaim,
)
from meetings.transcript import (
    contradiction_lift_key,
    detect_contradictions,
    is_weak_contradiction,
)
from observation.public_map import PublicMapView
from observation.packet import EventObservationBatch, PlayerView
from orchestrator.boundary import public_map_from_engine_map


def _map() -> PublicMapView:
    return public_map_from_engine_map(load_map(Path("engine/maps/canonical_1.yaml")))


def _reader_event_id_pattern() -> re.Pattern[str]:
    """The endpoint vocabulary, read from the one file that declares it.

    ``frontend/src/lib/contradictions.ts`` calls itself the ONE place the
    segment list is written down, and ``MeetingView`` builds its turn parser
    from that list. Reading the declaration rather than copying it means a
    segment taught to the reader reaches this guard too — and a flag endpoint
    the reader could not resolve fails here.
    """

    source = Path("frontend/src/lib/contradictions.ts").read_text(encoding="utf-8")
    declaration = re.search(
        r"OBSERVATION_EVENT_SEGMENTS = \[(.*?)\] as const", source, re.DOTALL
    )
    assert declaration is not None, "the frontend segment declaration moved"
    segments = re.findall(r'"([a-z_]+)"', declaration.group(1))
    assert segments, "the frontend segment declaration is empty"
    return re.compile(rf"^turn:(.+):(?:{'|'.join(segments)}):\d+$")


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
    teammate_kill: bool = False,
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
    if teammate_kill:
        # p-3 answers the account menu with the kill sighting it offers and
        # names its own teammate p-2.
        client.turns["p-3"] = client.turns["p-3"].model_copy(
            update={
                "observations": (
                    SawKillObservation(
                        type="saw_kill", tick=4, subject="p-2", room="LABS"
                    ),
                )
            }
        )
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
        MeetingParticipant(
            agent_id="p-2",
            role="IMPOSTOR" if teammate_kill else "CREWMATE",
            rendered_memory=own_memory,
            fellow_impostor_ids=("p-3",) if teammate_kill else (),
        ),
        MeetingParticipant(
            agent_id="p-3",
            role="IMPOSTOR",
            rendered_memory="Own private cover.",
            fellow_impostor_ids=("p-2",) if teammate_kill else (),
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


def _flags(*turns: MeetingTurn, roster: frozenset[str]) -> tuple[ContradictionRef, ...]:
    return detect_public_account_conflicts(
        MeetingTranscript(turns=turns),
        roster=roster,
        room_neighbors=_map().room_neighbors,
    )


def _claim_turn(speaker: str, claims: tuple[AlibiClaim, ...]) -> MeetingTurn:
    return MeetingTurn(
        turn_id=speaker,
        turn_index=0,
        speaker=speaker,
        turn_kind="opening",
        reply_to=None,
        claims=claims,
        free_text="unsure",
    )


def _alibi(subject: str, room: str, tick: int) -> AlibiClaim:
    return AlibiClaim(
        type="alibi", subject=subject, room=room, from_tick=tick, to_tick=tick
    )


def test_one_speaker_alone_impeaches_itself_not_the_player_it_named() -> None:
    # The adverse case: p-2 alone states two mutually distant placements of
    # innocent p-5. Two sentences from one mouth are one account, so the flag
    # names p-2 and the description says whose account it impeaches. Before
    # this rule the identical transcript minted a flag whose subjects tuple
    # named p-5 alone, and that subject is what the belief fold contradicts.
    (flag,) = _flags(
        _claim_turn("p-2", (_alibi("p-5", "REACTOR", 2), _alibi("p-5", "LABS", 3))),
        roster=frozenset({"p-2", "p-5"}),
    )
    assert flag.subjects == ("p-2",)
    assert "come from p-2 alone" in flag.description
    assert "rather than p-5" in flag.description
    assert flag.evidence_band == "weak"


def test_two_speakers_who_disagree_still_name_the_player_they_disagree_about() -> None:
    # The control that keeps the repair from silencing the channel: the same
    # two placements from DIFFERENT speakers are a genuine disagreement about
    # p-5, so the flag still names p-5 and carries no re-target sentence.
    (flag,) = _flags(
        _claim_turn("p-2", (_alibi("p-5", "REACTOR", 2),)),
        _claim_turn("p-4", (_alibi("p-5", "LABS", 3),)),
        roster=frozenset({"p-2", "p-4", "p-5"}),
    )
    assert flag.subjects == ("p-5",)
    assert "alone" not in flag.description


def test_a_speaker_who_contradicts_their_own_placements_stays_the_subject() -> None:
    # A single speaker's self-placements are already about that speaker, so
    # the re-target rule leaves them exactly as they were.
    (flag,) = _flags(
        _turn(
            "p-1",
            (
                WhereaboutsClaim(type="whereabouts", room="REACTOR", tick=5),
                WhereaboutsClaim(type="whereabouts", room="LABS", tick=5),
            ),
        ),
        roster=frozenset({"p-1"}),
    )
    assert flag.subjects == ("p-1",)
    assert "alone" not in flag.description


def test_the_cheapest_lie_now_places_the_speaker_who_told_it() -> None:
    # NG3-5's adverse case: an alibi in one room plus a fabricated sighting
    # across the map. Watching an event says where the watcher was, so the
    # pair is p-2's own impossible route and the flag names p-2. Before the
    # speaker placement the identical turn raised nothing at all.
    (flag,) = _flags(
        _turn(
            "p-2",
            (
                WhereaboutsClaim(type="whereabouts", room="REACTOR", tick=5),
                SawPlayerObservation(
                    type="saw_player", tick=5, subject="p-1", room="LABS"
                ),
            ),
        ),
        roster=frozenset({"p-1", "p-2"}),
    )
    assert flag.subjects == ("p-2",)
    assert "p-2's own sighting places p-2 in LABS" in flag.description


@pytest.mark.parametrize(
    "observation",
    [
        SawVentObservation(type="saw_vent", tick=5, subject="p-1", room="LABS"),
        SawKillObservation(type="saw_kill", tick=5, subject="p-1", room="LABS"),
        SawMoveObservation(
            type="saw_move", tick=5, subject="p-1", from_room="LABS", to_room="MEDBAY"
        ),
    ],
)
def test_every_sighting_shape_places_the_speaker(
    observation: ObservationClaim,
) -> None:
    # A witnessed transition is stated from its origin room; the destination
    # is one hop away, which the vision slack already covers.
    (flag,) = _flags(
        _turn(
            "p-2",
            (WhereaboutsClaim(type="whereabouts", room="REACTOR", tick=5), observation),
        ),
        roster=frozenset({"p-1", "p-2"}),
    )
    assert flag.subjects == ("p-2",)


@pytest.mark.parametrize(
    "sighting_room,sighting_tick",
    [
        # Adjacent to the stated room at the same tick: the plainest legal
        # sighting an impostor's one-hop vision allows (DESIGN.md §3.4).
        ("WEST_HALL", 5),
        # Three rooms away one tick later: legal only because the comparison
        # grants BOTH the within-tick step it already granted every pair and
        # the hop a claimed sighting is inferred across. Removing the vision
        # hop turns this pair into a flag against an account nothing in the
        # public record excludes.
        ("LABS", 6),
    ],
)
def test_a_sighting_within_the_granted_slack_is_never_called_impossible(
    sighting_room: str, sighting_tick: int
) -> None:
    assert (
        _flags(
            _turn(
                "p-2",
                (
                    WhereaboutsClaim(type="whereabouts", room="ADMIN", tick=5),
                    SawPlayerObservation(
                        type="saw_player",
                        tick=sighting_tick,
                        subject="p-1",
                        room=sighting_room,
                    ),
                ),
            ),
            roster=frozenset({"p-1", "p-2"}),
        )
        == ()
    )


def test_a_named_bystander_is_placed_by_the_sighting_that_named_them() -> None:
    # NG2-2's second half: co_present was validated but never compared, so a
    # bystander could deny a co-presence nobody could check. p-2 places p-3
    # alongside the sighting in ADMIN; p-3 says LABS, three rooms away.
    (flag,) = _flags(
        _turn(
            "p-2",
            (
                SawPlayerObservation(
                    type="saw_player",
                    tick=5,
                    subject="p-4",
                    room="ADMIN",
                    co_present=("p-3",),
                ),
            ),
        ),
        MeetingTurn(
            turn_id="p-3",
            turn_index=1,
            speaker="p-3",
            turn_kind="opening",
            reply_to=None,
            observations=(WhereaboutsClaim(type="whereabouts", room="LABS", tick=5),),
            free_text="unsure",
        ),
        roster=frozenset({"p-2", "p-3", "p-4"}),
    )
    assert flag.subjects == ("p-3",)
    assert "p-2 places p-3 alongside that sighting in ADMIN" in flag.description


def test_a_speaker_named_among_its_own_bystanders_impeaches_nobody() -> None:
    # Review round 1: `co_present` is checked against the roster only, so a
    # speaker may name ITSELF. Its own sighting already places it -- with the
    # vision hop -- so the self-mention must add nothing. CAFETERIA is exactly
    # the same-tick sighting two rooms from ADMIN that the comparison promises
    # never to call impossible; before the skip, the identical turn minted a
    # flag against p-2 out of p-2's own two sentences, because the duplicate
    # co-present row carried no vision slack.
    speaker_named_itself = _turn(
        "p-2",
        (
            WhereaboutsClaim(type="whereabouts", room="ADMIN", tick=5),
            SawPlayerObservation(
                type="saw_player",
                tick=5,
                subject="p-1",
                room="CAFETERIA",
                co_present=("p-2",),
            ),
        ),
    )
    assert _flags(speaker_named_itself, roster=frozenset({"p-1", "p-2"})) == ()

    # The control: the skip is surgical. The same turn additionally naming
    # p-3, who places itself three rooms away, still flags that disagreement
    # and still names p-3.
    (flag,) = _flags(
        speaker_named_itself.model_copy(
            update={
                "observations": (
                    speaker_named_itself.observations[0],
                    SawPlayerObservation(
                        type="saw_player",
                        tick=5,
                        subject="p-1",
                        room="CAFETERIA",
                        co_present=("p-2", "p-3"),
                    ),
                )
            }
        ),
        MeetingTurn(
            turn_id="p-3",
            turn_index=1,
            speaker="p-3",
            turn_kind="opening",
            reply_to=None,
            observations=(WhereaboutsClaim(type="whereabouts", room="LABS", tick=5),),
            free_text="unsure",
        ),
        roster=frozenset({"p-1", "p-2", "p-3"}),
    )
    assert flag.subjects == ("p-3",)
    assert "p-2 places p-3 alongside that sighting in CAFETERIA" in flag.description


def test_every_re_target_against_one_speaker_folds_to_one_belief_lift() -> None:
    # Task 10.10's rule, applied to this channel: three mutually distant
    # placements of p-5 from one mouth are three flags, but the belief fold
    # must charge p-2 ONCE -- `contradiction_lift_key` returns its constant
    # proxy key for every flag carrying WEAK_REASON_PROXY_INTRA_TURN. Without
    # the marker each claim pair keys on its own event ids and one narrator's
    # inconsistent account stacks three weak deltas against itself.
    flags = _flags(
        _claim_turn(
            "p-2",
            (
                _alibi("p-5", "REACTOR", 2),
                _alibi("p-5", "ADMIN", 3),
                _alibi("p-5", "LABS", 4),
            ),
        ),
        roster=frozenset({"p-2", "p-5"}),
    )
    assert len(flags) == 3
    assert {flag.subjects for flag in flags} == {("p-2",)}
    assert len({contradiction_lift_key(flag) for flag in flags}) == 1

    # Non-vacuity: a genuine two-speaker disagreement is NOT folded into that
    # key, so the constant cannot be collapsing the whole channel.
    (cross_speaker,) = _flags(
        _claim_turn("p-2", (_alibi("p-5", "REACTOR", 2),)),
        _claim_turn("p-4", (_alibi("p-5", "LABS", 3),)),
        roster=frozenset({"p-2", "p-4", "p-5"}),
    )
    assert contradiction_lift_key(cross_speaker) not in {
        contradiction_lift_key(flag) for flag in flags
    }


def test_a_derived_row_flags_through_an_artifact_id_a_reader_resolves() -> None:
    # `frontend/src/lib/contradictions.ts` declares the whole endpoint
    # vocabulary (`claim`, `obs`, `whereabouts`) and `MeetingView` builds its
    # parser from that declaration, so a flag whose endpoint carried a
    # derivation suffix would attach to no turn artifact. The derivation lives
    # in the id the contradiction_id hashes instead -- which is what keeps the
    # three flags this turn produces from collapsing onto one id.
    flags = _flags(
        _turn(
            "p-2",
            (
                SawPlayerObservation(
                    type="saw_player",
                    tick=5,
                    subject="p-1",
                    room="ADMIN",
                    co_present=("p-3",),
                ),
                SawPlayerObservation(
                    type="saw_player",
                    tick=5,
                    subject="p-1",
                    room="LABS",
                    co_present=("p-3",),
                ),
            ),
        ),
        roster=frozenset({"p-1", "p-2", "p-3"}),
    )
    # Two derived pairs off ONE pair of artifacts: p-1's two stated rooms and
    # p-3's two co-present rooms. They share both endpoints and must still be
    # two distinct flags -- hashing the endpoints alone would collapse them.
    assert len(flags) == 2
    assert len({flag.contradiction_id for flag in flags}) == 2
    assert {flag.description.split(".")[0] for flag in flags} == {
        "p-2 places p-1 in ADMIN at ticks 5–5; p-2 places p-1 in LABS at ticks 5–5",
        "p-2 places p-3 alongside that sighting in ADMIN at ticks 5–5; "
        "p-2 places p-3 alongside that sighting in LABS at ticks 5–5",
    }
    endpoints = {flag.event_a_id for flag in flags} | {
        flag.event_b_id for flag in flags
    }
    assert endpoints == {"turn:p-2:obs:0", "turn:p-2:obs:1"}
    reader = _reader_event_id_pattern()
    assert all(reader.match(endpoint) for endpoint in endpoints)


def test_one_sentence_cannot_contradict_itself_into_a_role_proof() -> None:
    # Review round 2: a sighting's `subject` is checked against the roster
    # only, so a speaker may name ITSELF. That one `saw_move` yields two rows
    # -- the stated destination, and the speaker's own witness position at the
    # origin the sighting was made from -- and both keep the artifact's event
    # id, so pairing them produced a flag whose two endpoints were the SAME
    # artifact. `classify_evidence` types self-linkage as `role_proof` by rule,
    # whatever the kind, so before the skip this one sentence minted the
    # spectator's and the prompt's strongest band out of a channel that
    # promises to prove no role -- and a role-proof flag on the arm whose
    # defining count of them is zero. ADMIN -> LABS is three rooms with two
    # steps allowed (one within-tick, one for the witness row's vision hop):
    # exactly the impossible route the self-pair asserted.
    self_named = SawMoveObservation(
        type="saw_move", tick=5, subject="p-2", from_room="ADMIN", to_room="LABS"
    )
    assert _flags(_turn("p-2", (self_named,)), roster=frozenset({"p-1", "p-2"})) == ()

    # The control: the skip is per ARTIFACT, not per endpoint pair, so the
    # same sentence still answers to somebody else's account. p-3 puts p-2 in
    # REACTOR at the same tick, which both of p-2's rows are too far from, and
    # the two flags share one endpoint pair while staying distinct by
    # `contradiction_id`. Every endpoint pair the channel emits names two
    # different artifacts, which is what keeps it out of the self-linked
    # role-proof row entirely.
    flags = _flags(
        _turn("p-2", (self_named,)),
        _claim_turn("p-3", (_alibi("p-2", "REACTOR", 5),)),
        roster=frozenset({"p-1", "p-2", "p-3"}),
    )
    assert len(flags) == 2
    assert len({flag.contradiction_id for flag in flags}) == 2
    assert all(flag.event_a_id != flag.event_b_id for flag in flags)
    assert {
        classify_evidence(
            kind=flag.kind,
            event_a_id=flag.event_a_id,
            event_b_id=flag.event_b_id,
            weak=is_weak_contradiction(flag),
        )
        for flag in flags
    } == {"weak_signal"}


def test_an_impostor_menu_answer_naming_its_teammate_never_records() -> None:
    # The account menu is the first arm that hands an impostor a structured
    # observation menu, and it offers a kill sighting. p-3 answers it naming
    # teammate p-2: the turn-level firewall drops the row before it records,
    # so no listener's transcript block and no derived testimony carries it.
    result, client = asyncio.run(_meeting(grounded=False, teammate_kill=True))
    p3_turn = next(turn for turn in result.transcript.turns if turn.speaker == "p-3")
    assert p3_turn.observations == ()
    assert not any(
        statement.kind == "saw_kill"
        for statement in derive_reported_testimony(
            result, public_account_version=1, attributed_testimony_version=1
        )
    )
    # The menu itself names the shape, so the check is the transcript row a
    # recorded observation would render as.
    assert not any(
        'stated {"type":"saw_kill"' in prompt
        for prompts in client.prompts.values()
        for prompt in prompts
    )


async def _off_profile_task_account(self: AccountClient, **kwargs: Any) -> LLMResponse:
    """p-1 answers with a task-activity account the recorded profile lacks."""

    agent_id = kwargs["agent_id"]
    self.prompts.setdefault(agent_id, []).append(kwargs["prompt"])
    if kwargs["schema"] is MeetingTurn:
        turn = self.turns[agent_id]
        if agent_id == "p-1":
            turn = turn.model_copy(
                update={
                    "observations": (
                        TaskActivityAccount(
                            type="task_activity",
                            task_id="fuel_reserves",
                            room="STORAGE",
                            from_tick=3,
                            to_tick=5,
                        ),
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


def test_a_task_account_cannot_enter_a_transcript_recorded_without_the_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """NC5-03: the off-profile refusal, which no test previously exercised.

    ``MeetingTurn`` is the structured-output contract for every profile, so a
    provider can return a ``TaskActivityAccount`` in a meeting recorded with
    ``public_account_version=None``. Nothing else stops that shape: the public
    accounts validator does not run off-profile. Deleting the refusal left
    1,375 meeting tests green.
    """

    monkeypatch.setattr(AccountClient, "complete", _off_profile_task_account)
    result, _ = asyncio.run(
        _meeting(grounded=False, attributed=None, common=None, expected_defaults=1)
    )
    speaker = next(turn for turn in result.transcript.turns if turn.speaker == "p-1")
    assert speaker.observations == ()
    assert not any(
        isinstance(observation, TaskActivityAccount)
        for turn in result.transcript.turns
        for observation in turn.observations
    )
    assert len(result.ballots) == 3


def test_the_same_account_is_kept_when_its_profile_is_recorded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The control: the identical turn is accepted under the profile itself."""

    monkeypatch.setattr(AccountClient, "complete", _off_profile_task_account)
    result, _ = asyncio.run(_meeting(grounded=False))
    speaker = next(turn for turn in result.transcript.turns if turn.speaker == "p-1")
    assert [type(row) for row in speaker.observations] == [TaskActivityAccount]
