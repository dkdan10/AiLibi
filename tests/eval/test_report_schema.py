"""Unit tests for the Phase 5 eval report schema (DESIGN.md §11.3, §11.4).

Fixtures are built by instantiating the models directly rather than by running
a tournament: this task ships the schema + its validator only, so the tests
pin field names, nesting, the ``format_version`` contract, ``extra="forbid"``,
frozen-ness, leaf-type reuse, and round-trip stability without any orchestrator
or LLM dependency.
"""

from __future__ import annotations

import json
from collections.abc import Mapping

import pytest
from pydantic import ValidationError

from engine.entities import Role
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    ContradictionRef,
    MeetingOutcome,
    MeetingTranscript,
    PlayerId,
    ReportDocument,
    SawPlayerObservation,
    Statement,
    VoteBallot,
)
from orchestrator.replay import FailedCallReplayEntry, LLMCallRecord, WinnerSide

# A coherent 4-player roster with p-3 as the impostor; the default for fixture
# games where the specific assignment does not matter.
_ROLES_P3_IMPOSTOR: Mapping[PlayerId, Role] = {
    "p-0": "CREWMATE",
    "p-1": "CREWMATE",
    "p-2": "CREWMATE",
    "p-3": "IMPOSTOR",
}


# ---------------------------------------------------------------------------
# Fixture builders -- realistic, fully populated leaf payloads
# ---------------------------------------------------------------------------


def _llm_call(*, agent_id: str, model: str, cost: float) -> LLMCallRecord:
    return LLMCallRecord(
        call_kind="meeting",
        model=model,
        prompt=f"<rendered memory view for {agent_id}>",
        response_text='{"target": "p-3", "confidence": 0.8}',
        input_tokens=1200,
        output_tokens=180,
        cost_usd=cost,
        agent_id=agent_id,
    )


def _meeting_report(
    *,
    meeting_id: str,
    tick: int,
    ejected: str | None,
) -> MeetingReport:
    transcript = MeetingTranscript(
        reports=(
            ReportDocument(
                agent_id="p-0",
                tick=tick,
                observations=(
                    SawPlayerObservation(
                        type="saw_player",
                        tick=tick - 2,
                        subject="p-3",
                        room="ELECTRICAL",
                        co_present=("p-1",),
                    ),
                ),
                claims=(
                    AlibiClaim(
                        type="alibi",
                        subject="p-0",
                        from_tick=tick - 4,
                        to_tick=tick,
                        room="MEDBAY",
                        evidence=("scan_task",),
                    ),
                ),
                free_text="I was scanning in MedBay the whole time.",
            ),
        ),
        statements=(
            Statement(
                statement_id="s-1",
                speaker="p-0",
                tick=tick,
                round_index=0,
                target="p-3",
                claims=(
                    AccusationClaim(
                        type="accusation",
                        against="p-3",
                        confidence=0.8,
                        reason="seen leaving Electrical right before the body",
                    ),
                ),
                free_text="p-3 was right by the body.",
            ),
        ),
    )
    outcome: MeetingOutcome = "EJECTED" if ejected is not None else "SKIPPED"
    return MeetingReport(
        meeting_id=meeting_id,
        tick=tick,
        triggered_by="p-0",
        outcome=outcome,
        ejected_player_id=ejected,
        transcript=transcript,
        ballots=(
            VoteBallot(
                voter="p-0",
                target=ejected if ejected is not None else "SKIP",
                confidence=0.8,
                primary_reason_id="s-1",
                considered_alternatives=("p-2",),
                rationale_text="contradiction between alibi and sighting",
            ),
            VoteBallot(
                voter="p-1",
                target="SKIP",
                confidence=0.3,
                primary_reason_id=None,
                rationale_text="not enough evidence",
            ),
        ),
        contradictions=(
            ContradictionRef(
                contradiction_id="c-1",
                kind="alibi_vs_sighting",
                event_a_id="alibi:p-3",
                event_b_id="saw_player:p-3",
                subjects=("p-3",),
                description="p-3 claimed Storage but was seen in Electrical",
            ),
        ),
        llm_calls=(
            _llm_call(agent_id="p-0", model="claude-sonnet", cost=0.012),
            _llm_call(agent_id="p-1", model="claude-haiku", cost=0.001),
        ),
    )


def _failed_call(*, meeting_id: str, model: str, cost: float) -> FailedCallReplayEntry:
    return FailedCallReplayEntry(
        game_id="game-13",
        meeting_id=meeting_id,
        tick=70,
        model=model,
        prompt_length=4096,
        raw_response='{"target": "p-9"',  # truncated / invalid JSON
        input_tokens=1500,
        output_tokens=40,
        cost_usd=cost,
        error_type="ValidationError",
        error_message="target references unknown player",
    )


def _game_report(
    *,
    game_id: str,
    seed: int,
    winner: WinnerSide | None,
    reason: str,
    meetings: tuple[MeetingReport, ...],
    final_tick: int | None = 60,
    roles: Mapping[PlayerId, Role] = _ROLES_P3_IMPOSTOR,
    failed_calls: tuple[FailedCallReplayEntry, ...] = (),
) -> GameReport:
    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=winner,
        reason=reason,
        final_tick=final_tick,
        roles=roles,
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=meetings,
        failed_calls=failed_calls,
        prompt_versions={"meeting_v": "2026-05-01", "trigger_v": "2026-04-12"},
        cost=GameCostSummary(
            total_cost_usd=0.026,
            total_input_tokens=2400,
            total_output_tokens=360,
            by_model={"claude-sonnet": 0.024, "claude-haiku": 0.002},
        ),
    )


def _realistic_tournament() -> TournamentReport:
    """A multi-game / multi-meeting tournament covering every winner kind.

    Game 11 ejects the impostor p-3 (CREWMATES win, a *correct* ejection),
    game 12 reaches the tick budget (no decisive winner, no meetings), game 13
    has two meetings and wrongly ejects crewmate p-1 while impostor p-3 survives
    (IMPOSTORS win). This exercises decisive + non-decisive outcomes, 0/1/2-
    meeting games, and both correct and incorrect ejections relative to the
    role ground truth in one fixture.
    """

    return TournamentReport(
        games=(
            _game_report(
                game_id="game-11",
                seed=11,
                winner="CREWMATES",
                reason="impostor ejected",
                final_tick=52,
                roles=_ROLES_P3_IMPOSTOR,
                meetings=(
                    _meeting_report(meeting_id="m-11-0", tick=40, ejected="p-3"),
                ),
            ),
            _game_report(
                game_id="game-12",
                seed=12,
                winner=None,
                reason="TICK_BUDGET_REACHED",
                final_tick=1000,
                roles={
                    "p-0": "CREWMATE",
                    "p-1": "CREWMATE",
                    "p-2": "IMPOSTOR",
                    "p-3": "CREWMATE",
                },
                meetings=(),
            ),
            _game_report(
                game_id="game-13",
                seed=13,
                winner="IMPOSTORS",
                reason="crew reduced to parity",
                final_tick=88,
                roles=_ROLES_P3_IMPOSTOR,
                meetings=(
                    _meeting_report(meeting_id="m-13-0", tick=30, ejected=None),
                    _meeting_report(meeting_id="m-13-1", tick=70, ejected="p-1"),
                ),
                failed_calls=(
                    _failed_call(
                        meeting_id="m-13-1", model="claude-sonnet", cost=0.004
                    ),
                ),
            ),
        ),
        seeds_used=(11, 12, 13),
    )


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------


def test_full_report_round_trips_through_json() -> None:
    report = _realistic_tournament()

    dumped = report.model_dump(mode="json")
    restored = TournamentReport.model_validate(dumped)

    assert restored == report
    # Re-dumping the restored object is byte-stable, so a loader can persist
    # and reload without drift.
    assert restored.model_dump(mode="json") == dumped


def test_round_trip_preserves_nested_meeting_artifacts() -> None:
    report = _realistic_tournament()

    restored = TournamentReport.model_validate(report.model_dump(mode="json"))

    game13 = restored.games[2]
    assert game13.winner == "IMPOSTORS"
    assert tuple(m.meeting_id for m in game13.meetings) == ("m-13-0", "m-13-1")
    second_meeting = game13.meetings[1]
    assert second_meeting.ejected_player_id == "p-1"
    assert second_meeting.contradictions[0].kind == "alibi_vs_sighting"
    assert second_meeting.llm_calls[0].model == "claude-sonnet"
    assert game13.prompt_versions["meeting_v"] == "2026-05-01"


# ---------------------------------------------------------------------------
# format_version contract
# ---------------------------------------------------------------------------


def test_current_format_version_is_one() -> None:
    assert CURRENT_FORMAT_VERSION == 1


def test_format_version_defaults_to_current() -> None:
    report = TournamentReport(games=(), seeds_used=())
    assert report.format_version == CURRENT_FORMAT_VERSION


def test_format_version_accepts_current_explicitly() -> None:
    report = TournamentReport(format_version=1, games=(), seeds_used=())
    assert report.format_version == 1


def test_format_version_rejects_future_version() -> None:
    with pytest.raises(ValidationError, match="unknown report format_version 2"):
        TournamentReport(format_version=2, games=(), seeds_used=())


def test_format_version_rejects_future_version_on_deserialize() -> None:
    payload = {"format_version": 2, "games": [], "seeds_used": []}
    with pytest.raises(ValidationError, match="unknown report format_version 2"):
        TournamentReport.model_validate(payload)


def test_format_version_rejects_below_current_version() -> None:
    with pytest.raises(ValidationError, match="no migration path"):
        TournamentReport(format_version=0, games=(), seeds_used=())


def test_format_version_missing_on_deserialize_is_rejected() -> None:
    """A serialized report that lost its version marker fails loud (E-E-1).

    The audit's concern is a *report JSON* with ``format_version`` entirely
    absent: it previously defaulted silently to v1. Reading such a report back
    via ``model_validate_json`` -- the on-disk read path -- must now raise a
    clear error rather than coerce it, honoring the no-silent-fallback rule.
    """

    payload = json.dumps({"games": [], "seeds_used": []})
    with pytest.raises(ValidationError, match="missing report format_version"):
        TournamentReport.model_validate_json(payload)


def test_format_version_marker_present_round_trips_through_json() -> None:
    """The current marker ``1`` round-trips through the JSON read path.

    The complement of the missing-marker rejection above: a serialized report
    that DOES carry ``format_version == CURRENT_FORMAT_VERSION`` deserializes
    cleanly.
    """

    payload = json.dumps(
        {"format_version": CURRENT_FORMAT_VERSION, "games": [], "seeds_used": []}
    )
    report = TournamentReport.model_validate_json(payload)
    assert report.format_version == CURRENT_FORMAT_VERSION


def test_format_version_missing_on_python_construction_keeps_default() -> None:
    """The read-time guard is deliberately scoped to deserialized JSON.

    Pydantic runs ``model_validate`` of a Python dict in the same ``"python"``
    mode as in-process ``__init__``, so the two are indistinguishable; the
    tournament-report writer (``eval.balance_eval``) builds the report without
    restating the version and leans on the field default. Both in-memory paths
    therefore keep defaulting to the current version -- only a *serialized*
    (JSON) report must carry the marker. This pins that deliberate asymmetry so a
    later tightening does not silently break the writer.
    """

    constructed = TournamentReport(games=(), seeds_used=())
    validated = TournamentReport.model_validate({"games": [], "seeds_used": []})
    assert constructed.format_version == CURRENT_FORMAT_VERSION
    assert validated.format_version == CURRENT_FORMAT_VERSION


# ---------------------------------------------------------------------------
# extra="forbid" and frozen
# ---------------------------------------------------------------------------


def test_unknown_top_level_field_is_rejected() -> None:
    payload = {"format_version": 1, "games": [], "seeds_used": [], "extra": 1}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TournamentReport.model_validate(payload)


def test_unknown_nested_field_is_rejected() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        GameCostSummary.model_validate(
            {
                "total_cost_usd": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "by_model": {},
                "surprise": True,
            }
        )


def test_report_models_are_frozen() -> None:
    report = _realistic_tournament()
    with pytest.raises(ValidationError):
        report.format_version = 1
    with pytest.raises(ValidationError):
        report.games[0].seed = 99


# ---------------------------------------------------------------------------
# Leaf-type reuse (no redefinition / no drift)
# ---------------------------------------------------------------------------


def test_meeting_report_reuses_meetings_schema_leaf_types() -> None:
    """The meeting artifacts resolve to the imported leaf types, not forks."""

    fields = MeetingReport.model_fields
    assert fields["transcript"].annotation is MeetingTranscript
    assert fields["ballots"].annotation == tuple[VoteBallot, ...]
    assert fields["contradictions"].annotation == tuple[ContradictionRef, ...]
    assert fields["llm_calls"].annotation == tuple[LLMCallRecord, ...]


def test_report_schema_reuses_canonical_leaf_types_not_forks() -> None:
    """Any leaf type visible in the module is the canonical object, not a fork.

    Importing a name makes it a module attribute, so absence is not the right
    check -- identity is: each leaf type must be the same object as the one its
    owning module defines, which is what guarantees no drifting redefinition.
    """

    import eval.report_schema as report_schema
    import meetings.schemas as meetings_schemas
    import orchestrator.replay as replay

    # ``vars(module)[name]`` returns Any, sidestepping mypy's strict
    # implicit-reexport check while still asserting the runtime binding is the
    # canonical object (the names are imported, not redefined, in the module).
    module_ns = vars(report_schema)
    assert module_ns["VoteBallot"] is meetings_schemas.VoteBallot
    assert module_ns["ContradictionRef"] is meetings_schemas.ContradictionRef
    assert module_ns["MeetingTranscript"] is meetings_schemas.MeetingTranscript
    assert module_ns["MeetingOutcome"] is meetings_schemas.MeetingOutcome
    assert module_ns["PlayerId"] is meetings_schemas.PlayerId
    assert module_ns["LLMCallRecord"] is replay.LLMCallRecord
    assert module_ns["WinnerSide"] is replay.WinnerSide
    assert module_ns["FailedCallReplayEntry"] is replay.FailedCallReplayEntry


# ---------------------------------------------------------------------------
# Metric inputs: role ground truth + game length
# ---------------------------------------------------------------------------


def test_roles_ground_truth_enables_vote_correctness_lookup() -> None:
    """The role map lets a pure analyzer judge an ejection without engine state.

    This is the input Task 5.2 needs: vote correctness =
    ``roles[ejected] == "IMPOSTOR"``. The fixture's game 11 correctly ejects
    impostor p-3; game 13 wrongly ejects crewmate p-1.
    """

    report = TournamentReport.model_validate(_realistic_tournament().model_dump())

    game11 = report.games[0]
    ejected_11 = game11.meetings[0].ejected_player_id
    assert ejected_11 is not None
    assert game11.roles[ejected_11] == "IMPOSTOR"  # correct ejection

    game13 = report.games[2]
    ejected_13 = game13.meetings[1].ejected_player_id
    assert ejected_13 is not None
    assert game13.roles[ejected_13] == "CREWMATE"  # wrong ejection


def test_final_tick_round_trips_and_yields_game_length_distribution() -> None:
    """``final_tick`` survives round-trip, so §11.3 game-length is report-only."""

    report = TournamentReport.model_validate(_realistic_tournament().model_dump())

    lengths = [g.final_tick for g in report.games]
    assert lengths == [52, 1000, 88]


def test_failed_calls_are_carried_so_cost_is_not_undercounted() -> None:
    """Aborted-meeting LLM spend has a home and survives round-trip.

    Mirrors ``orchestrator.replay.compute_cost_usd``, which folds failed-call
    cost into the per-game total: a total computed from completed-meeting calls
    plus ``failed_calls`` must include the crashed call's already-charged spend.
    """

    report = TournamentReport.model_validate(_realistic_tournament().model_dump())

    game13 = report.games[2]
    assert len(game13.failed_calls) == 1
    failed = game13.failed_calls[0]
    assert failed.model == "claude-sonnet"
    assert failed.cost_usd == 0.004

    # Total spend = completed-meeting calls + failed calls (the compute_cost_usd
    # reduction). The failed call's cost is part of it, not dropped.
    meeting_call_cost = sum(
        call.cost_usd for m in game13.meetings for call in m.llm_calls
    )
    failed_cost = sum(fc.cost_usd for fc in game13.failed_calls)
    assert failed_cost == 0.004
    assert meeting_call_cost + failed_cost > meeting_call_cost

    # Games with no crashed meeting carry an empty tuple, not a missing field.
    assert report.games[0].failed_calls == ()


# ---------------------------------------------------------------------------
# BalanceReport representability (Task 5.6 will migrate; prove no info loss)
# ---------------------------------------------------------------------------


def test_report_represents_balance_report_buckets() -> None:
    """Everything ``eval.balance_eval.BalanceReport`` carries is derivable.

    Confirms the ``## Decisions`` claim that the Pydantic report can supersede
    the ``BalanceReport`` dataclass without information loss: outcome buckets
    and seeds reduce out of ``TournamentReport`` directly.
    """

    report = _realistic_tournament()

    games = len(report.games)
    crew_wins = sum(1 for g in report.games if g.winner == "CREWMATES")
    impostor_wins = sum(1 for g in report.games if g.winner == "IMPOSTORS")
    tick_budget_reached = sum(1 for g in report.games if g.winner is None)

    assert games == 3
    assert crew_wins == 1
    assert impostor_wins == 1
    assert tick_budget_reached == 1
    assert crew_wins + impostor_wins + tick_budget_reached == games
    assert report.seeds_used == (11, 12, 13)
    # The non-decisive game keeps its specific reason rather than being coerced.
    assert report.games[1].reason == "TICK_BUDGET_REACHED"


def test_partial_tournament_allows_fewer_games_than_seeds() -> None:
    """A crashed run records fewer games than seeds attempted (no equality check)."""

    report = TournamentReport(
        games=(
            _game_report(
                game_id="game-11",
                seed=11,
                winner="CREWMATES",
                reason="impostor ejected",
                meetings=(),
            ),
        ),
        seeds_used=(11, 12, 13),
    )

    assert len(report.games) == 1
    assert report.seeds_used == (11, 12, 13)
