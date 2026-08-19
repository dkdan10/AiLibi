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
from eval.deduction_metrics import DeductionMetricsReport
from eval.meeting_quality import TournamentEvalReport, build_tournament_eval_report
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
    MeetingTurn,
    PlayerId,
    SawPlayerObservation,
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
        turns=(
            MeetingTurn(
                turn_id=f"{meeting_id}:turn-0",
                turn_index=0,
                speaker="p-0",
                turn_kind="opening",
                reply_to=None,
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
            MeetingTurn(
                turn_id="s-1",
                turn_index=1,
                speaker="p-0",
                turn_kind="reply",
                reply_to=f"{meeting_id}:turn-0",
                observations=(),
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
        trigger="report",
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
    kill_gifted: bool = False,
    instances_dropped: int = 0,
    instances_complete_at_win: int = 0,
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
        kill_gifted=kill_gifted,
        instances_dropped=instances_dropped,
        instances_complete_at_win=instances_complete_at_win,
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
        format_version=CURRENT_FORMAT_VERSION,
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


def test_current_format_version_is_two() -> None:
    # Bumped 1 -> 2 in Task 8.11: the meeting-chain reshape (8.7 / 8.10) changed
    # MeetingReport.transcript, so v1 reports are no longer readable.
    assert CURRENT_FORMAT_VERSION == 2


def test_format_version_missing_on_construction_is_rejected() -> None:
    """In-process construction without the marker fails loud (no default).

    ``format_version`` is a required field with no default, so building a
    report in Python without it raises rather than silently assuming v1
    (audit E-E-1). The writer (``eval.balance_eval``) stamps the current
    version explicitly.
    """

    with pytest.raises(ValidationError, match="missing report format_version"):
        TournamentReport(games=(), seeds_used=())  # type: ignore[call-arg]


def test_format_version_accepts_current_explicitly() -> None:
    report = TournamentReport(format_version=2, games=(), seeds_used=())
    assert report.format_version == 2 == CURRENT_FORMAT_VERSION


def test_format_version_rejects_future_version() -> None:
    with pytest.raises(ValidationError, match="unknown report format_version 3"):
        TournamentReport(format_version=3, games=(), seeds_used=())


def test_format_version_rejects_future_version_on_deserialize() -> None:
    payload = {"format_version": 3, "games": [], "seeds_used": []}
    with pytest.raises(ValidationError, match="unknown report format_version 3"):
        TournamentReport.model_validate(payload)


def test_format_version_rejects_v1_no_migration() -> None:
    """A v1 report is rejected fail-loud with the no-migration message (8.11).

    The 1 -> 2 bump ships no back-migration, so the committed v1 reports become
    invalid the moment 8.11 lands; Task 8.12 regenerates them to v2. v1 hits the
    ``value < CURRENT_FORMAT_VERSION`` branch (1 < 2) and raises rather than
    being coerced (AGENTS.md "no silent fallbacks").
    """

    with pytest.raises(ValidationError, match="no migration path"):
        TournamentReport(format_version=1, games=(), seeds_used=())


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


def test_format_version_missing_on_dict_validate_is_rejected() -> None:
    """``model_validate`` of a Python dict missing the marker also fails loud.

    Codex review follow-up to the original JSON-only guard: because
    ``format_version`` is now a required field with no default, the common
    ``json.loads(...)`` + ``model_validate(dict)`` read path raises the same
    clear error as ``model_validate_json`` and as in-process construction, so
    the no-silent-fallback rule (E-E-1) holds on every read path, not just JSON.
    """

    with pytest.raises(ValidationError, match="missing report format_version"):
        TournamentReport.model_validate({"games": [], "seeds_used": []})


def test_format_version_missing_on_nested_dict_validate_is_rejected() -> None:
    """The guard reaches a ``TournamentReport`` nested under the eval bundle.

    A :class:`~eval.meeting_quality.TournamentEvalReport` whose embedded report
    lost its marker is rejected even on the python-dict ``model_validate`` path:
    the required field runs the guard in every mode, top-level and nested. This
    closes the nested half of the no-silent-fallback guarantee (E-E-1).
    """

    bundle = build_tournament_eval_report(_realistic_tournament())
    payload = bundle.model_dump()
    del payload["report"]["format_version"]
    with pytest.raises(ValidationError, match="missing report format_version"):
        TournamentEvalReport.model_validate(payload)


# ---------------------------------------------------------------------------
# extra="forbid" and frozen
# ---------------------------------------------------------------------------


def test_eval_wrapper_carries_the_deduction_block() -> None:
    """Task 19.14's ``deduction`` block is a REAL field on the canonical owner.

    ``TournamentEvalReport`` is ``extra="forbid"``, so the new cells could not
    ride as loose extras: the block is a declared field
    (:class:`~eval.deduction_metrics.DeductionMetricsReport`) whose two cross-tab
    partitions each span the report's own totals. ``format_version`` stays at 2 —
    the block is a wrapper-level aggregate over an unchanged inner report, the
    same rule ``meeting_rate`` / ``conversion`` / ``gate_metrics`` followed.
    """

    bundle = build_tournament_eval_report(_realistic_tournament())

    assert isinstance(bundle.deduction, DeductionMetricsReport)
    assert bundle.report.format_version == CURRENT_FORMAT_VERSION
    meetings_total = sum(len(game.meetings) for game in bundle.report.games)
    assert bundle.deduction.meetings_total == meetings_total
    assert bundle.deduction.meeting_flag_cross_tab.meetings_total == meetings_total
    assert (
        bundle.deduction.ejectee_proof_cross_tab.ejections_total
        == bundle.deduction.ejections_total
    )
    # The block round-trips through the exact serialization the committed
    # ``tournament-eval-report.json`` views ride on.
    restored = TournamentEvalReport.model_validate_json(bundle.model_dump_json())
    assert restored.deduction == bundle.deduction


def test_eval_wrapper_rejects_a_payload_missing_the_deduction_block() -> None:
    """A pre-19.14 wrapper JSON is rejected fail-loud, not defaulted.

    ``deduction`` is REQUIRED with no default (unlike the Task 8.17 additive
    per-game facts, which are defaulted so pre-fields reports still load). All
    four committed reports are regenerated in the same PR, so no pre-19.14
    wrapper JSON survives to be read — and one that turned up would be stale
    rather than old-but-valid.
    """

    payload = build_tournament_eval_report(_realistic_tournament()).model_dump()
    del payload["deduction"]
    with pytest.raises(ValidationError, match="deduction"):
        TournamentEvalReport.model_validate(payload)


def test_unknown_top_level_field_is_rejected() -> None:
    payload = {
        "format_version": CURRENT_FORMAT_VERSION,
        "games": [],
        "seeds_used": [],
        "extra": 1,
    }
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
        report.format_version = CURRENT_FORMAT_VERSION
    with pytest.raises(ValidationError):
        report.games[0].seed = 99


# ---------------------------------------------------------------------------
# The two-mirror tripwire
# ---------------------------------------------------------------------------


def test_tournament_report_field_set_is_pinned_to_its_two_mirrors() -> None:
    """A new field on TournamentReport must land on both mirrors in one change.

    ``api/routes/eval.py::_TournamentReportEvalView`` forbids extras, so an
    unmirrored field 500s ``/eval/tournament-report`` on the redaction
    round-trip; ``tests/api/test_leak.py::EXPECTED_EVAL_REPORT_FIELDS`` snapshots
    the recursive served field set. Neither failure points at this model, which
    is why the field set is pinned here.
    """

    assert set(TournamentReport.model_fields) == {
        "format_version",
        "games",
        "seeds_used",
        "kill_gifted_wins",
        "instances_dropped_total",
        "mean_instances_complete_at_win",
    }, (
        "TournamentReport's field set changed. A field added here must be "
        "mirrored on api/routes/eval.py::_TournamentReportEvalView (extra="
        "'forbid' — an unmirrored field breaks /eval/tournament-report) and on "
        "tests/api/test_leak.py::EXPECTED_EVAL_REPORT_FIELDS (the recursive "
        "served-field snapshot), in the same change. Instrument blocks that need "
        "neither — such as eval.solvability.SolvabilityReport — belong in their "
        "own module instead."
    )


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
        format_version=CURRENT_FORMAT_VERSION,
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


# ---------------------------------------------------------------------------
# Kill-gifted win accounting (Task 8.17; DESIGN.md §3.5; audit gp-4)
# ---------------------------------------------------------------------------


def test_kill_gift_fields_default_to_no_gift() -> None:
    """A report built without the kill-gift fields carries the no-gift defaults.

    The fields are additive with defaults, so a caller (and a pre-8.17 report)
    that never sets them reads ``kill_gifted=False`` / ``0`` / ``0`` per game and
    ``0`` / ``0`` / ``None`` in the roll-ups.
    """

    report = TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=(
            _game_report(
                game_id="g",
                seed=1,
                winner="CREWMATES",
                reason="CREWMATE_TASKS",
                meetings=(),
            ),
        ),
        seeds_used=(1,),
    )

    game = report.games[0]
    assert game.kill_gifted is False
    assert game.instances_dropped == 0
    assert game.instances_complete_at_win == 0
    assert report.kill_gifted_wins == 0
    assert report.instances_dropped_total == 0
    assert report.mean_instances_complete_at_win is None


def test_kill_gift_fields_round_trip_through_json() -> None:
    """A populated kill-gift report (per-game facts + roll-ups) round-trips."""

    report = TournamentReport(
        format_version=CURRENT_FORMAT_VERSION,
        games=(
            _game_report(
                game_id="gift",
                seed=22,
                winner="CREWMATES",
                reason="CREWMATE_TASKS",
                meetings=(),
                kill_gifted=True,
                instances_dropped=3,
                instances_complete_at_win=11,
            ),
            _game_report(
                game_id="organic",
                seed=1,
                winner="CREWMATES",
                reason="CREWMATE_TASKS",
                meetings=(),
                kill_gifted=False,
                instances_dropped=2,
                instances_complete_at_win=14,
            ),
        ),
        seeds_used=(1, 22),
        kill_gifted_wins=1,
        instances_dropped_total=5,
        mean_instances_complete_at_win=12.5,
    )

    restored = TournamentReport.model_validate(report.model_dump(mode="json"))
    assert restored == report
    gift = restored.games[0]
    assert gift.kill_gifted is True
    assert (gift.instances_dropped, gift.instances_complete_at_win) == (3, 11)
    assert restored.games[1].kill_gifted is False
    assert restored.kill_gifted_wins == 1
    assert restored.instances_dropped_total == 5
    assert restored.mean_instances_complete_at_win == 12.5


def test_pre_fields_v2_report_loads_via_defaults() -> None:
    """A committed pre-8.17 v2 report (no kill-gift fields) still validates.

    The fields are additive with defaults under ``extra="forbid"``: a *missing*
    field is permitted (only an unknown field is rejected), so a v2 report
    serialized before this task loads cleanly and reads the no-gift defaults.
    This is the backward-compat contract Task 8.18 relies on until it regenerates
    the committed reports.
    """

    payload = _realistic_tournament().model_dump(mode="json")
    assert payload["format_version"] == 2
    # Strip every additive kill-gift field, reproducing a pre-8.17 v2 report.
    for key in (
        "kill_gifted_wins",
        "instances_dropped_total",
        "mean_instances_complete_at_win",
    ):
        del payload[key]
    for game in payload["games"]:
        for key in ("kill_gifted", "instances_dropped", "instances_complete_at_win"):
            del game[key]

    restored = TournamentReport.model_validate(payload)

    assert restored.format_version == CURRENT_FORMAT_VERSION  # still v2, not migrated
    assert restored.kill_gifted_wins == 0
    assert restored.instances_dropped_total == 0
    assert restored.mean_instances_complete_at_win is None
    assert all(game.kill_gifted is False for game in restored.games)
    assert all(game.instances_dropped == 0 for game in restored.games)
    assert all(game.instances_complete_at_win == 0 for game in restored.games)


def test_pre_fields_v2_report_loads_via_json_read_path() -> None:
    """The same pre-fields v2 report loads through ``model_validate_json`` too."""

    payload = _realistic_tournament().model_dump(mode="json")
    del payload["kill_gifted_wins"]
    del payload["instances_dropped_total"]
    del payload["mean_instances_complete_at_win"]
    for game in payload["games"]:
        del game["kill_gifted"]
        del game["instances_dropped"]
        del game["instances_complete_at_win"]

    restored = TournamentReport.model_validate_json(json.dumps(payload))
    assert restored.format_version == 2
    assert restored.mean_instances_complete_at_win is None
