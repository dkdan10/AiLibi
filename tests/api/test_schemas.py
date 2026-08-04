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
    AdvantageView,
    AgentMemoryView,
    AgentTickStateView,
    AlibiClaimView,
    BallotView,
    BeliefEntryView,
    BeliefErrorView,
    BeliefFrameView,
    BodyView,
    CompletedTaskObsView,
    ContradictionView,
    CorroborationClaimView,
    EdgeView,
    EvalCostSummaryView,
    FailedCallView,
    FinaleAgentRecapView,
    FinaleEventView,
    FoundBodyObsView,
    GameFinale,
    GateView,
    KillEventView,
    LLMCallView,
    MapLayoutView,
    MeetingResolutionView,
    MeetingTriggeredEventView,
    MeetingView,
    ObservationClaimView,
    PlayerView,
    PositionView,
    ReplayMetadataView,
    ReplayView,
    ReportBodyEventView,
    RoomView,
    RubricGameView,
    RubricView,
    SabotageDetailView,
    SabotageEventView,
    SawPlayerView,
    SizeView,
    StatementClaimView,
    SuspicionEntryView,
    SuspicionGraphView,
    TaskCompletedEventView,
    TickView,
    TurnView,
    VentEventView,
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


def _turns() -> tuple[TurnView, ...]:
    # The reactive accusation chain (DESIGN.md §5.2): an opening turn that
    # carries the reporter's observations + claims, then a reply turn whose
    # ``reply_to`` threads back to it. One ordered list — no "round" grouping.
    return (
        TurnView(
            turn_id="m1:turn-0",
            turn_index=0,
            speaker="p1",
            turn_kind="opening",
            reply_to=None,
            observations=_all_observation_claims(),
            claims=_all_statement_claims(),
            free_text="I was doing wires; I found p4 in storage. p2 is sus.",
            fabricated_opening=False,
        ),
        TurnView(
            turn_id="m1:turn-1",
            turn_index=1,
            speaker="p2",
            turn_kind="reply",
            reply_to="m1:turn-0",
            observations=(),
            claims=_all_statement_claims(),
            free_text="It wasn't me — I was in electrical.",
            fabricated_opening=False,
        ),
    )


def _contradiction() -> ContradictionView:
    return ContradictionView(
        contradiction_id="c1",
        kind="alibi_vs_sighting",
        event_a_id="a1",
        event_b_id="b1",
        subjects=("p2",),
        description="p2 claims storage but was seen in cafeteria",
        weak=False,
        severity="strong",
    )


def _meeting_resolution_view() -> MeetingResolutionView:
    """The Task 19.10 pre/post-resolution label for a RESOLVED meeting frame.

    Populated (not ``None``) on purpose: a ``None`` would round-trip trivially
    and prove nothing about the nested :class:`AdvantageView`. ``pre_advantage``
    is the frame's advantage BEFORE the ejection applied, so it carries one more
    living impostor than the tick's (post-resolution) ``advantage`` — the two
    vintages the label exists to keep apart.
    """

    return MeetingResolutionView(
        meeting_id="m1",
        ejected_player_id="p2",
        pre_advantage=AdvantageView(
            crew_alive=6,
            impostors_alive=2,
            tasks_completed=9,
            tasks_required=14,
            tasks_required_total=14,
            advantage=0.21,
        ),
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
            VentEventView(
                type="vent",
                tick=10,
                actor_id="p2",
                phase="enter",
                from_room_id="ELECTRICAL",
                to_room_id="MEDBAY",
                traversal_ticks=2,
            ),
        ),
        sabotage_active=("lights",),
        # Per-player task instances (DESIGN.md §3.2/§3.5): the canonical 9p/2i
        # roster mints 7 crew × tasks_per_crewmate=2 = 14 instances over the 12
        # map tasks, so the spectator total exceeds the old map-task pool.
        tasks_completed_total=9,
        tasks_required_total=14,
        # Phase-12 additive projections (DESIGN.md §7).
        bodies=(
            BodyView(
                body_id="body-p4-7", victim_id="p4", room_id="STORAGE", killed_by="p2"
            ),
        ),
        sabotage=SabotageDetailView(
            kind="lights",
            remaining_ticks=42,
            affected_rooms=("ADMIN",),
            repair_progress={"ADMIN": 3},
        ),
        advantage=AdvantageView(
            crew_alive=6,
            impostors_alive=1,
            tasks_completed=9,
            tasks_required=14,
            tasks_required_total=14,
            advantage=0.47,
        ),
        # Task 19.10 additive label. Named explicitly (rather than left to its
        # ``None`` default) because the house style is exhaustive construction,
        # and because a populated value is what round-trips the nested DTO.
        meeting_resolution=_meeting_resolution_view(),
    )


def _meeting_view() -> MeetingView:
    return MeetingView(
        meeting_id="m1",
        tick=10,
        triggered_by="p1",
        trigger_kind="body",
        outcome="EJECTED",
        ejected_player_id="p2",
        turns=_turns(),
        ballots=(
            BallotView(
                voter="p1",
                target="p2",
                confidence=0.9,
                primary_reason_id="m1:turn-1",
                considered_alternatives=("SKIP",),
                rationale_text="p2 vented",
                rewrite_reasons=(),
                rationale_text_clean="p2 vented",
            ),
            BallotView(
                voter="p3",
                target="SKIP",
                confidence=0.4,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="[teammate target 'p2' coerced to SKIP] cover",
                rewrite_reasons=("teammate_coerced",),
                rationale_text_clean="cover",
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
                agent_id="p1",
            ),
        ),
        prompt_versions={"crewmate_report": "v1", "vote_ballot": "v2"},
        total_cost_usd=0.0,
        gate=GateView(
            leader="p2", leader_max_confidence=0.9, threshold=0.6, passed=True
        ),
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
                subject="p2", suspicion=0.7, confidence=0.6, snapshot_tick=9
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


def _game_finale() -> GameFinale:
    """The Task 19.10 composed outcome view.

    Covers all four ``FinaleEventView`` kinds in one fixture so the inlined
    ``kind`` literal round-trips on every branch, and both recap shapes: an agent
    who named a real impostor (``final_vote_named_impostor=True``) and one whose
    ``SKIP`` names nobody (``None`` — the question does not apply, distinct from
    ``False`` = named a crewmate).
    """

    return GameFinale(
        winner="CREWMATES",
        winner_reason="CREWMATE_EJECT",
        final_tick=42,
        decisive_events=(
            FinaleEventView(tick=10, kind="kill", actor_id="p2", subject_id="p4"),
            FinaleEventView(
                tick=20, kind="meeting_skipped", actor_id="p1", subject_id=None
            ),
            FinaleEventView(tick=42, kind="ejection", actor_id="p1", subject_id="p2"),
            FinaleEventView(tick=42, kind="game_end", actor_id=None, subject_id=None),
        ),
        agent_recaps=(
            FinaleAgentRecapView(
                agent_id="p1",
                role="CREWMATE",
                alive_at_end=True,
                final_vote_target="p2",
                final_vote_named_impostor=True,
            ),
            FinaleAgentRecapView(
                agent_id="p2",
                role="IMPOSTOR",
                alive_at_end=False,
                final_vote_target="SKIP",
                final_vote_named_impostor=None,
            ),
        ),
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
        # Task 19.10 additive field; populated so the nested finale round-trips
        # as part of the full replay payload, not only standalone.
        finale=_game_finale(),
    )


def _belief_frame_view() -> BeliefFrameView:
    # A per-meeting belief × truth snapshot: one observer→subject cell whose
    # error is the signed Belief − Truth (suspicion 0.8 of a real impostor →
    # error −0.2, "nearly got it"), and one cell over a crewmate.
    return BeliefFrameView(
        meeting_id="m1",
        tick=10,
        entries=(
            BeliefErrorView(
                observer="p1",
                subject="p2",
                suspicion=0.8,
                confidence=0.6,
                subject_is_impostor=True,
                error=0.8 - 1.0,
                has_belief=True,
            ),
            # A NO-BELIEF cell: neutral 0.5 prior, has_belief False ("no belief
            # yet" ≠ 0, rendered as a hatch, not a low-suspicion belief).
            BeliefErrorView(
                observer="p1",
                subject="p3",
                suspicion=0.5,
                confidence=0.0,
                subject_is_impostor=False,
                error=0.5,
                has_belief=False,
            ),
        ),
    )


def _rubric_view() -> RubricView:
    return RubricView(
        seedset="9p2i",
        git_head="d8cb869c0bea65fdb0b1864b5d89f1249a58c5ed",
        manifest_sha="1e48c40",
        stale=True,
        per_game=(
            RubricGameView(
                seed=5,
                score=80.0,
                reason="CREWMATE_EJECT",
                n_meetings=3,
                win_shape="eject-decided",
                ejected_impostors=1,
                accused_impostors=2,
                survived_accused=0,
                r1_decisive=1.0,
                r2_deception=0.6,
                r3_arcs=1.0,
                r7_legible=1.0,
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
    _belief_frame_view(),
    _rubric_view(),
    _game_finale(),
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
        "vent",
    }
    assert TickView.model_validate_json(tick.model_dump_json()) == tick


def test_extra_fields_are_rejected() -> None:
    with pytest.raises(pydantic.ValidationError):
        PositionView.model_validate({"x": 1.0, "y": 2.0, "z": 3.0})


def test_belief_entry_rejects_old_field_name() -> None:
    with pytest.raises(pydantic.ValidationError):
        BeliefEntryView(  # type: ignore[call-arg]
            subject="p-2",
            suspicion=0.7,
            confidence=0.4,
            last_updated_tick=5,  # old name
        )


# The canonical map has 12 tasks (engine/maps/canonical_1.yaml; pinned in
# tests/engine/test_map_loader.py). Under per-player task instances (DESIGN.md
# §3.2) the spectator/agent task counts are over instances minted WITH overlap,
# so the denominator is no longer bounded by this pool: the canonical 9p/2i
# roster (7 crew × tasks_per_crewmate=2) deals 14 instances over these 12 tasks.
_CANONICAL_MAP_TASK_COUNT = 12


def test_tick_view_task_total_is_uncapped_per_player_denominator() -> None:
    """``TickView`` task counts are over per-player instances, not the map pool.

    DESIGN.md §3.2/§3.5: per-player task instances are minted WITH overlap, so the
    spectator denominator is the live instance count (14 at the canonical 9p/2i)
    and is no longer bounded by the 12 map tasks (the old per-game cap). This pins
    that the ``int`` field accepts and round-trips a denominator above the
    map-task pool without truncation — the 1:1 frontend mirror keeps it ``number``.
    """

    tick = _tick_view()
    assert tick.tasks_required_total > _CANONICAL_MAP_TASK_COUNT
    assert 0 <= tick.tasks_completed_total <= tick.tasks_required_total
    assert TickView.model_validate_json(tick.model_dump_json()) == tick

    # A higher tasks_per_crewmate pushes the instance count well past 12; the
    # field must carry it faithfully (no implicit cap on the denominator).
    bigger = tick.model_copy(
        update={"tasks_completed_total": 18, "tasks_required_total": 27}
    )
    assert bigger.tasks_required_total > _CANONICAL_MAP_TASK_COUNT
    assert TickView.model_validate_json(bigger.model_dump_json()) == bigger


def test_agent_memory_view_task_counts_are_own_instances() -> None:
    """``AgentMemoryView`` task counts are this agent's OWN instances.

    DESIGN.md §3.2: owner-scoped under the per-player keyspace — ``tasks_assigned``
    is the agent's owned instance count (a per-player deal, e.g. 2 at the canonical
    ``tasks_per_crewmate``, bounded by its distinct map tasks, NOT the global pool)
    and ``tasks_completed`` ≤ it. Both round-trip faithfully as ``int`` (the 1:1
    frontend mirror keeps them ``number``).
    """

    memory = _agent_memory_view()
    assert 0 <= memory.tasks_completed <= memory.tasks_assigned
    assert AgentMemoryView.model_validate_json(memory.model_dump_json()) == memory

    # Counts move as a pair as the agent finishes its deal: completing every owned
    # instance leaves completed == assigned. Round-trips without special-casing.
    done = memory.model_copy(update={"tasks_completed": memory.tasks_assigned})
    assert done.tasks_completed == done.tasks_assigned
    assert AgentMemoryView.model_validate_json(done.model_dump_json()) == done
