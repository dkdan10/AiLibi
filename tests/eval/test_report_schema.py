"""Unit tests for the Phase 5 eval report schema (DESIGN.md §11.3, §11.4).

Fixtures are built by instantiating the models directly rather than by running
a tournament: this task ships the schema + its validator only, so the tests
pin field names, nesting, the ``format_version`` contract, ``extra="forbid"``,
frozen-ness, leaf-type reuse, and round-trip stability without any orchestrator
or LLM dependency.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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
    ReportDocument,
    SawPlayerObservation,
    Statement,
    VoteBallot,
)
from orchestrator.replay import LLMCallRecord, WinnerSide


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


def _game_report(
    *,
    game_id: str,
    seed: int,
    winner: WinnerSide | None,
    reason: str,
    meetings: tuple[MeetingReport, ...],
) -> GameReport:
    return GameReport(
        game_id=game_id,
        seed=seed,
        winner=winner,
        reason=reason,
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=meetings,
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

    Game 11 ejects the impostor (CREWMATES win), game 12 reaches the tick
    budget (no decisive winner), game 13 has two meetings and the impostors
    win. This exercises decisive + non-decisive outcomes and 0/1/2-meeting
    games in one fixture.
    """

    return TournamentReport(
        games=(
            _game_report(
                game_id="game-11",
                seed=11,
                winner="CREWMATES",
                reason="impostor ejected",
                meetings=(
                    _meeting_report(meeting_id="m-11-0", tick=40, ejected="p-3"),
                ),
            ),
            _game_report(
                game_id="game-12",
                seed=12,
                winner=None,
                reason="TICK_BUDGET_REACHED",
                meetings=(),
            ),
            _game_report(
                game_id="game-13",
                seed=13,
                winner="IMPOSTORS",
                reason="crew reduced to parity",
                meetings=(
                    _meeting_report(meeting_id="m-13-0", tick=30, ejected=None),
                    _meeting_report(meeting_id="m-13-1", tick=70, ejected="p-1"),
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
