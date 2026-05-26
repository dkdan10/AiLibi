"""Round-trip serialization tests for the spectator DTOs (DESIGN.md §7).

Each top-level DTO is built via its direct constructor, dumped to JSON with
``model_dump_json``, validated back with ``model_validate_json``, and compared
for equality. The fixtures deliberately include at least one instance of every
discriminated-union variant (tick events, observation claims, statement
claims) so the discriminator round-trips correctly.
"""

from __future__ import annotations

import pydantic
import pytest

from api.schemas import (
    AccusationClaimView,
    AgentMemoryView,
    AgentTickStateView,
    AlibiClaimView,
    BallotView,
    BeliefEntryView,
    CompletedTaskObsView,
    ContradictionView,
    CorroborationClaimView,
    EdgeView,
    EvalCostSummaryView,
    FailedCallView,
    FoundBodyObsView,
    KillEventView,
    LLMCallView,
    MapLayoutView,
    MeetingTriggeredEventView,
    MeetingView,
    ObservationClaimView,
    PlayerView,
    PositionView,
    ReplayMetadataView,
    ReplayView,
    ReportBodyEventView,
    ReportView,
    RoomView,
    SabotageEventView,
    SawPlayerView,
    SizeView,
    StatementClaimView,
    StatementView,
    SuspicionEntryView,
    SuspicionGraphView,
    TaskCompletedEventView,
    TickView,
    VentView,
)


def _all_observation_claims() -> tuple[ObservationClaimView, ...]:
    return (
        SawPlayerView(
            type="saw_player",
            tick=3,
            subject="p2",
            room="CAFETERIA",
            co_present=("p3",),
        ),
        CompletedTaskObsView(
            type="completed_task", tick=4, task_id="wires", room="ELECTRICAL"
        ),
        FoundBodyObsView(type="found_body", tick=9, body_of="p4", room="STORAGE"),
    )


def _all_statement_claims() -> tuple[StatementClaimView, ...]:
    return (
        AlibiClaimView(
            type="alibi",
            subject="p1",
            from_tick=0,
            to_tick=5,
            room="CAFETERIA",
            evidence=("completed wires",),
        ),
        AccusationClaimView(
            type="accusation", against="p2", confidence=0.8, reason="vented"
        ),
        CorroborationClaimView(
            type="corroboration", supports="p3", on_tick=4, reason="saw together"
        ),
    )


def _report() -> ReportView:
    return ReportView(
        agent_id="p1",
        tick=10,
        observations=_all_observation_claims(),
        claims=_all_statement_claims(),
        free_text="I was doing wires.",
    )


def _statement() -> StatementView:
    return StatementView(
        statement_id="s1",
        speaker="p1",
        tick=10,
        round_index=0,
        target="p2",
        claims=_all_statement_claims(),
        free_text="p2 is sus.",
    )


def _contradiction() -> ContradictionView:
    return ContradictionView(
        contradiction_id="c1",
        kind="alibi_vs_sighting",
        event_a_id="a1",
        event_b_id="b1",
        subjects=("p2",),
        description="p2 claims storage but was seen in cafeteria",
    )


def _tick_view() -> TickView:
    return TickView(
        tick=10,
        agent_states=(
            AgentTickStateView(
                agent_id="p1",
                room_id="CAFETERIA",
                is_alive=True,
                is_venting=False,
                task_progress=0.5,
                current_action="TASK",
            ),
            AgentTickStateView(
                agent_id="p2",
                room_id="ELECTRICAL",
                is_alive=True,
                is_venting=True,
                task_progress=None,
                current_action="VENT",
            ),
            AgentTickStateView(
                agent_id="p4",
                room_id=None,
                is_alive=False,
                is_venting=False,
                task_progress=None,
                current_action="IDLE",
            ),
        ),
        events=(
            KillEventView(
                type="kill", tick=10, killer_id="p2", victim_id="p4", room_id="STORAGE"
            ),
            ReportBodyEventView(
                type="report_body",
                tick=10,
                reporter_id="p1",
                body_of="p4",
                room_id="STORAGE",
            ),
            SabotageEventView(
                type="sabotage", tick=10, kind="lights", room_id=None, actor_id="p2"
            ),
            TaskCompletedEventView(
                type="task_completed",
                tick=10,
                agent_id="p1",
                task_id="wires",
                room_id="ELECTRICAL",
            ),
            MeetingTriggeredEventView(
                type="meeting_triggered",
                tick=10,
                meeting_id="m1",
                triggered_by="p1",
                trigger_kind="body",
            ),
        ),
        sabotage_active=("lights",),
        tasks_completed_total=7,
        tasks_required_total=12,
    )


def _meeting_view() -> MeetingView:
    return MeetingView(
        meeting_id="m1",
        tick=10,
        triggered_by="p1",
        trigger_kind="body",
        outcome="EJECTED",
        ejected_player_id="p2",
        reports=(_report(),),
        statements=(_statement(),),
        ballots=(
            BallotView(
                voter="p1",
                target="p2",
                confidence=0.9,
                primary_reason_id="s1",
                considered_alternatives=("SKIP",),
                rationale_text="p2 vented",
            ),
            BallotView(
                voter="p3",
                target="SKIP",
                confidence=0.4,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="not enough info",
            ),
        ),
        contradictions=(_contradiction(),),
        llm_calls=(
            LLMCallView(
                call_kind="meeting",
                model="claude-haiku-test",
                prompt_template_id="crewmate_report@v1",
                prompt_text="## Your role: CREWMATE",
                response_text='{"vote": "p2"}',
                input_tokens=120,
                output_tokens=40,
                cost_usd=0.0,
            ),
        ),
        prompt_versions={"crewmate_report": "v1", "vote_ballot": "v2"},
        total_cost_usd=0.0,
    )


def _agent_memory_view() -> AgentMemoryView:
    return AgentMemoryView(
        agent_id="p1",
        tick=10,
        role="CREWMATE",
        tasks_completed=2,
        tasks_assigned=4,
        observations=_all_observation_claims(),
        beliefs=(
            BeliefEntryView(
                subject="p2", suspicion=0.7, confidence=0.6, last_updated_tick=9
            ),
        ),
        open_contradictions=(_contradiction(),),
        rendered_memory_text="## Your role: CREWMATE\n## Tasks completed: 2 / 4",
    )


def _replay_metadata_view() -> ReplayMetadataView:
    return ReplayMetadataView(
        game_id="headless-seed-7",
        seed=7,
        total_ticks=42,
        winner="CREWMATES",
        winner_reason="all_tasks_complete",
        meeting_count=1,
        total_cost_usd=0.0,
        prompt_versions={"crewmate_report": "v1"},
        created_at="2026-05-26T00:00:00Z",
    )


def _replay_view() -> ReplayView:
    return ReplayView(
        metadata=_replay_metadata_view(),
        map=MapLayoutView(
            rooms=(
                RoomView(
                    id="CAFETERIA",
                    name="Cafeteria",
                    position=PositionView(x=0.0, y=0.0),
                    size=SizeView(width=10.0, height=8.0),
                ),
            ),
            vents=(
                VentView(
                    id="ELECTRICAL_VENT",
                    room_id="ELECTRICAL",
                    connected_room_ids=("MEDBAY_VENT",),
                ),
            ),
            edges=(
                EdgeView(from_room_id="CAFETERIA", to_room_id="STORAGE", is_door=True),
            ),
        ),
        players=(
            PlayerView(
                agent_id="p1",
                display_name="Red",
                role="CREWMATE",
                color="#ff0000",
            ),
            PlayerView(
                agent_id="p2",
                display_name="Blue",
                role="IMPOSTOR",
                color="#0000ff",
            ),
        ),
        ticks=(_tick_view(),),
        meetings=(_meeting_view(),),
        failed_calls=(
            FailedCallView(
                meeting_id="m2",
                tick=20,
                model="claude-haiku-test",
                cost_usd=0.0,
                error_type="ValidationError",
                error_message="missing field 'vote'",
            ),
        ),
    )


def _suspicion_graph_view() -> SuspicionGraphView:
    return SuspicionGraphView(
        tick=10,
        entries=(
            SuspicionEntryView(observer="p1", subject="p2", suspicion=0.7),
            SuspicionEntryView(observer="p3", subject="p2", suspicion=0.5),
        ),
    )


def _eval_cost_summary_view() -> EvalCostSummaryView:
    return EvalCostSummaryView(
        total_replays=3,
        total_cost_usd=0.45,
        mean_cost_per_replay=0.15,
        max_cost_per_replay=0.30,
        decisive_split={"CREWMATES": 0.62, "IMPOSTORS": 0.38},
    )


_TOP_LEVEL_FIXTURES: tuple[pydantic.BaseModel, ...] = (
    _replay_view(),
    _tick_view(),
    _meeting_view(),
    _agent_memory_view(),
    _eval_cost_summary_view(),
    _replay_metadata_view(),
    _suspicion_graph_view(),
)


@pytest.mark.parametrize(
    "instance", _TOP_LEVEL_FIXTURES, ids=lambda m: type(m).__name__
)
def test_top_level_dto_round_trips(instance: pydantic.BaseModel) -> None:
    rebuilt = type(instance).model_validate_json(instance.model_dump_json())
    assert rebuilt == instance


@pytest.mark.parametrize("variant", _all_observation_claims())
def test_observation_claim_variant_round_trips(variant: pydantic.BaseModel) -> None:
    rebuilt = type(variant).model_validate_json(variant.model_dump_json())
    assert rebuilt == variant


@pytest.mark.parametrize("variant", _all_statement_claims())
def test_statement_claim_variant_round_trips(variant: pydantic.BaseModel) -> None:
    rebuilt = type(variant).model_validate_json(variant.model_dump_json())
    assert rebuilt == variant


def test_tick_events_cover_every_variant_and_round_trip() -> None:
    tick = _tick_view()
    discriminators = {event.type for event in tick.events}
    assert discriminators == {
        "kill",
        "report_body",
        "sabotage",
        "task_completed",
        "meeting_triggered",
    }
    assert TickView.model_validate_json(tick.model_dump_json()) == tick


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(pydantic.ValidationError):
        PositionView.model_validate({"x": 1.0, "y": 2.0, "z": 3.0})
