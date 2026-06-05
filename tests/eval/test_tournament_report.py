"""Tests for the Task 5.6 tournament metric integration (DESIGN.md §11.3).

Two layers:

* **Integration** — a small FAKE-provider tournament (no network) run through
  :func:`eval.balance_eval.run_tournament_eval`, asserting the loader captured
  role ground truth from the in-memory result, the emitted JSON validates, all
  four metric blocks are present, and per-game spend matches the canonical
  cost reducer (no double-count).
* **Loader unit tests** — the JSONL→``GameReport`` fold
  (``eval.balance_eval._game_report_from_replay``) against hand-written replay
  files: nonzero-cost no-double-count, the empty-roles fail-loud guard
  (the silent-zero trap), and the doubled-file ``CorruptedFileError`` propagation.

The fake provider always reports ``cost_usd == 0.0``, so the integration
no-double-count check is trivially ``0.0 == 0.0``; the synthetic-cost loader
unit test pins the real arithmetic.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import pytest
from pydantic import TypeAdapter, ValidationError

from agents.base import AgentInterface
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from eval.accusation_calibration import AccusationCalibrationReport
from eval.alibi_fabrication import AlibiFabricationReport
from eval.balance_eval import (
    _game_report_from_replay,
    run_tournament_eval,
)
from eval.cost_dashboard import CostDashboard
from eval.meeting_quality import (
    MeetingRateReport,
    TournamentEvalReport,
    build_tournament_eval_report,
    compute_meeting_rate,
)
from eval.report_schema import (
    GameCostSummary,
    GameReport,
    MeetingReport,
    TournamentReport,
)
from eval.vote_correctness import VoteCorrectnessReport
from llm.provider import LLMCallFailure, _attach_parse_failure
from meetings.schemas import (
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
)
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from orchestrator.replay import (
    FailedCallReplayEntry,
    GameEndReplayEntry,
    LLMCallRecord,
    MeetingReplayEntry,
    ReplayEntry,
    ReplayLog,
    ReplayLogEntry,
    compute_cost_usd,
)
from orchestrator.seeder import seed_initial_state

_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)


class _WaitAgent:
    """Test-only agent that always waits, so no meeting ever fires.

    Mirrors the wait agent in ``tests/eval/test_balance_eval.py`` so a tiny tick
    budget yields a ``TICK_BUDGET_REACHED`` game with no ``game_over`` row — the
    partial-run shape the loader must tolerate.
    """

    def __init__(self, *, agent_id: PlayerId) -> None:
        self._agent_id = agent_id

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        return _INTENT_ADAPTER.validate_python(
            {"type": "wait", "actor": self._agent_id, "payload": {}}
        )


def _wait_factory(agent_id: PlayerId, role: Role) -> AgentInterface:
    return _WaitAgent(agent_id=agent_id)


def _write_jsonl(path: Path, entries: list[ReplayLogEntry]) -> None:
    lines = [json.dumps(entry.model_dump(mode="json")) for entry in entries]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Integration: a small FAKE-provider tournament end-to-end
# ---------------------------------------------------------------------------

# Seeds that fire at least one meeting under the fake provider at this config.
# Re-probed for the canonical 7p/2i roster after Task 7.9 made the impostor kill
# policy teammate-aware: at the former 5p/2i config two impostors now reach parity
# on a single kill before any body is reported, so every 5p/2i game ends in a fast
# impostor win with zero meetings. The integration test therefore runs on the
# meeting-heavy 7p/2i roster (5 crew, the canonical Phase 7 eval roster), where
# bodies still outlive the win condition and trigger meetings. Picked so the loader
# exercises the MeetingReplayEntry -> MeetingReport mapping, not just empty games.
_MEETING_FIRING_SEEDS = (0, 1, 2)
_NUM_PLAYERS = 7
_NUM_IMPOSTORS = 2
_MAX_TICKS = 300


def test_tournament_eval_report_full_integration(tmp_path: Path) -> None:
    report = run_tournament_eval(
        seeds=_MEETING_FIRING_SEEDS,
        output_dir=tmp_path,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        max_ticks=_MAX_TICKS,
    )

    # One GameReport per seed, in seed order.
    assert tuple(game.seed for game in report.games) == _MEETING_FIRING_SEEDS
    assert report.seeds_used == _MEETING_FIRING_SEEDS

    game_map = load_canonical_map()
    for game in report.games:
        # roles come from the in-memory seeded result, never the replay JSONL:
        # non-empty, exactly the game's players, exactly num_impostors impostors.
        assert game.roles, "roles must be populated (the silent-zero trap)"
        expected_players = set(
            seed_initial_state(
                seed=game.seed,
                game_map=game_map,
                num_players=_NUM_PLAYERS,
                num_impostors=_NUM_IMPOSTORS,
            ).players
        )
        assert set(game.roles) == expected_players
        impostor_count = sum(1 for role in game.roles.values() if role == "IMPOSTOR")
        assert impostor_count == _NUM_IMPOSTORS
        assert all(role in ("CREWMATE", "IMPOSTOR") for role in game.roles.values())

        # No double-count: per-game total equals the canonical reducer for that
        # seed's replay file (compute_cost_usd already folds in failed calls).
        replay_path = tmp_path / game.replay_ref
        assert game.cost.total_cost_usd == pytest.approx(compute_cost_usd(replay_path))

    # The MeetingReplayEntry -> MeetingReport path is actually exercised.
    assert any(game.meetings for game in report.games)

    # The wrapper carries all four Phase 5 metric blocks plus the W0.3 fifth.
    eval_report = build_tournament_eval_report(report)
    assert isinstance(eval_report.vote_correctness, VoteCorrectnessReport)
    assert isinstance(eval_report.accusation_calibration, AccusationCalibrationReport)
    assert isinstance(eval_report.alibi_fabrication, AlibiFabricationReport)
    assert isinstance(eval_report.cost_dashboard, CostDashboard)
    # meeting_rate is packed and consistent with the games (this seed set fires
    # at least one meeting, so the rate is > 0 and the buckets partition).
    mr = eval_report.meeting_rate
    assert isinstance(mr, MeetingRateReport)
    assert mr.games_total == len(report.games)
    assert mr.games_with_meeting == sum(1 for game in report.games if game.meetings)
    assert mr.meetings_total == sum(len(game.meetings) for game in report.games)
    assert mr.body_report_meetings + mr.emergency_meetings == mr.meetings_total
    assert mr.meeting_rate is not None and mr.meeting_rate > 0.0

    # The emitted JSON validates against the schema and round-trips byte-for-byte.
    json_text = eval_report.model_dump_json()
    restored = TournamentEvalReport.model_validate_json(json_text)
    assert restored == eval_report
    # The embedded TournamentReport validates against its own schema too.
    assert TournamentReport.model_validate(report.model_dump(mode="json")) == report

    # BalanceReport migration: the buckets are recoverable from winner without
    # information loss (every game lands in exactly one bucket).
    crew = sum(1 for game in report.games if game.winner == "CREWMATES")
    impostor = sum(1 for game in report.games if game.winner == "IMPOSTORS")
    tick_budget = sum(1 for game in report.games if game.winner is None)
    assert crew + impostor + tick_budget == len(report.games)


def test_tournament_eval_report_emits_cost_dashboard_consistent_with_games(
    tmp_path: Path,
) -> None:
    """The cost dashboard's total equals the sum of per-game totals (one source)."""

    report = run_tournament_eval(
        seeds=_MEETING_FIRING_SEEDS,
        output_dir=tmp_path,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        max_ticks=_MAX_TICKS,
    )
    eval_report = build_tournament_eval_report(report)

    per_game_total = sum(game.cost.total_cost_usd for game in report.games)
    assert eval_report.cost_dashboard.total_cost_usd == pytest.approx(per_game_total)
    assert eval_report.cost_dashboard.game_count == len(report.games)


# ---------------------------------------------------------------------------
# Partial-run robustness via the public runner (TICK_BUDGET_REACHED)
# ---------------------------------------------------------------------------


def test_partial_run_without_game_over_yields_none_winner(tmp_path: Path) -> None:
    """A tick-budget game writes no game_over row; the loader must not raise."""

    report = run_tournament_eval(
        seeds=(0, 1),
        output_dir=tmp_path,
        agent_factory=_wait_factory,
        max_ticks=1,
    )

    assert tuple(game.seed for game in report.games) == (0, 1)
    for game in report.games:
        assert game.winner is None
        assert game.final_tick is None
        assert game.reason == "TICK_BUDGET_REACHED"
        # roles still captured from the in-memory result even with no game_over.
        assert game.roles
        assert game.meetings == ()
        assert game.failed_calls == ()

    # The wrapper still builds; with no meetings every metric is the empty case.
    eval_report = build_tournament_eval_report(report)
    assert eval_report.vote_correctness.total_ejections == 0
    assert eval_report.alibi_fabrication.total_impostor_alibis == 0
    # Two games, neither reaching a meeting: rate is a defined 0.0 (games ran),
    # not None (None is reserved for the zero-games case).
    mr = eval_report.meeting_rate
    assert mr.games_total == 2
    assert mr.games_with_meeting == 0
    assert mr.meeting_rate == 0.0
    assert mr.meetings_total == 0
    assert mr.body_report_meetings == 0
    assert mr.emergency_meetings == 0


# ---------------------------------------------------------------------------
# Loader unit tests over hand-written replay files
# ---------------------------------------------------------------------------


def test_loader_does_not_double_count_failed_call_cost(tmp_path: Path) -> None:
    """total_cost_usd == compute_cost_usd == single-counted meeting+failed spend."""

    path = tmp_path / "replay-seed-99.jsonl"
    entries: list[ReplayLogEntry] = [
        ReplayEntry(game_id="g", tick=0, actions=(), state_hash="h0"),
        # The trigger tick records the report action that opened the meeting;
        # the loader recovers MeetingReport.trigger from it (no trigger field is
        # persisted on the meeting row).
        ReplayEntry(
            game_id="g",
            tick=1,
            actions=({"type": "report", "actor": "p-0", "payload": {"body_id": "b"}},),
            state_hash="h1",
        ),
        MeetingReplayEntry(
            game_id="g",
            meeting_id="g:meeting-0",
            tick=1,
            triggered_by="p-0",
            outcome="SKIPPED",
            ejected_player_id=None,
            transcript=MeetingTranscript(),
            ballots=(),
            contradictions=(),
            llm_calls=(
                LLMCallRecord(
                    call_kind="meeting",
                    model="model-a",
                    prompt="p",
                    response_text="r",
                    input_tokens=100,
                    output_tokens=20,
                    cost_usd=0.01,
                    agent_id="p-0",
                ),
                LLMCallRecord(
                    call_kind="meeting",
                    model="model-b",
                    prompt="p",
                    response_text="r",
                    input_tokens=200,
                    output_tokens=30,
                    cost_usd=0.02,
                    agent_id="p-1",
                ),
            ),
            prompt_versions={"meeting_v": "v1"},
            state_hash_before="hb",
            state_hash_after="ha",
        ),
        FailedCallReplayEntry(
            game_id="g",
            meeting_id="g:meeting-1",
            tick=2,
            model="model-c",
            prompt_length=10,
            raw_response="{",
            input_tokens=50,
            output_tokens=5,
            cost_usd=0.005,
            error_type="ValidationError",
            error_message="bad",
        ),
        GameEndReplayEntry(game_id="g", tick=3, winner="CREWMATES", reason="done"),
    ]
    _write_jsonl(path, entries)

    game = _game_report_from_replay(
        seed=99,
        roles={"p-0": "IMPOSTOR", "p-1": "CREWMATE"},
        fallback_reason="CREWMATES",
        replay_path=path,
    )

    # Spend is counted once: meeting calls (0.01 + 0.02) + failed call (0.005).
    assert game.cost.total_cost_usd == pytest.approx(0.035)
    assert game.cost.total_cost_usd == pytest.approx(compute_cost_usd(path))
    # Tokens + by_model are summed across meeting llm_calls AND failed_calls.
    assert game.cost.total_input_tokens == 350
    assert game.cost.total_output_tokens == 55
    assert dict(game.cost.by_model) == pytest.approx(
        {"model-a": 0.01, "model-b": 0.02, "model-c": 0.005}
    )

    # Outcome + structure folded from the replay rows.
    assert game.winner == "CREWMATES"
    assert game.reason == "done"
    assert game.final_tick == 3
    assert game.replay_ref == "replay-seed-99.jsonl"
    assert len(game.meetings) == 1
    assert game.meetings[0].meeting_id == "g:meeting-0"
    # trigger is reconstructed from the trigger-tick's report action.
    assert game.meetings[0].trigger == "report"
    assert len(game.failed_calls) == 1
    assert dict(game.prompt_versions) == {"meeting_v": "v1"}


def test_loader_fails_loud_on_empty_roles(tmp_path: Path) -> None:
    """An empty roles map for a finished game is a fail-loud error."""

    path = tmp_path / "replay-seed-1.jsonl"
    _write_jsonl(path, [ReplayEntry(game_id="g", tick=0, actions=(), state_hash="h")])

    with pytest.raises(ValueError, match="empty"):
        _game_report_from_replay(
            seed=1,
            roles={},
            fallback_reason="CREWMATES",
            replay_path=path,
        )


def test_loader_fails_loud_on_doubled_file(tmp_path: Path) -> None:
    """A doubled/corrupted replay file propagates CorruptedFileError."""

    path = tmp_path / "replay-seed-2.jsonl"
    _write_jsonl(
        path,
        [
            ReplayEntry(game_id="g", tick=0, actions=(), state_hash="h0"),
            ReplayEntry(game_id="g", tick=0, actions=(), state_hash="h1"),
        ],
    )

    with pytest.raises(ReplayLog.CorruptedFileError):
        _game_report_from_replay(
            seed=2,
            roles={"p-0": "IMPOSTOR"},
            fallback_reason="CREWMATES",
            replay_path=path,
        )


# ---------------------------------------------------------------------------
# Per-seed meeting-abort recovery in run_tournament_eval
# (a real-provider parse failure records spend + re-raises; the tournament must
#  fold the partial game instead of discarding the whole run)
# ---------------------------------------------------------------------------


class _AbortingHeadlessGame:
    """Stub game whose run() mimics a real-provider meeting abort.

    Writes a partial replay (a tick + a FailedCallReplayEntry, no game_over),
    exactly as ``HeadlessGame`` does before re-raising, then raises an exception
    carrying the parse-failure metadata ``extract_parse_failure`` reads.
    """

    _COST = 0.02

    def __init__(
        self,
        *,
        seed: int,
        game_map: object,
        agent_factory: object,
        replay_path: Path,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        scheduler: object,
        meeting_runner: object,
        force: bool,
    ) -> None:
        self._seed = seed
        self._replay_path = replay_path

    @property
    def replay_path(self) -> Path:
        return self._replay_path

    def run(self) -> object:
        game_id = f"headless-seed-{self._seed}"
        _write_jsonl(
            self._replay_path,
            [
                ReplayEntry(game_id=game_id, tick=0, actions=(), state_hash="h0"),
                FailedCallReplayEntry(
                    game_id=game_id,
                    meeting_id=f"{game_id}:meeting-0",
                    tick=1,
                    model="model-x",
                    prompt_length=10,
                    raw_response="{",
                    input_tokens=100,
                    output_tokens=10,
                    cost_usd=self._COST,
                    error_type="ValidationError",
                    error_message="bad",
                ),
            ],
        )
        exc = RuntimeError("meeting aborted on parse failure")
        _attach_parse_failure(
            exc,
            LLMCallFailure(
                model="model-x",
                prompt_length=10,
                raw_response="{",
                input_tokens=100,
                output_tokens=10,
                cost_usd=self._COST,
                error_type="ValidationError",
                error_message="bad",
            ),
        )
        raise exc


class _BuggyHeadlessGame:
    """Stub game whose run() raises a plain (non-parse-failure) exception."""

    def __init__(self, **kwargs: object) -> None:
        pass

    def run(self) -> object:
        raise RuntimeError("genuine bug with no parse-failure metadata")


def test_tournament_recovers_partial_game_on_meeting_abort(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A meeting abort yields a partial GameReport (winner=None) carrying the
    failed-call spend — the whole tournament is not discarded, and the spend is
    counted exactly once."""

    monkeypatch.setattr("eval.balance_eval.HeadlessGame", _AbortingHeadlessGame)

    report = run_tournament_eval(
        seeds=(7,),
        output_dir=tmp_path,
        num_players=4,
        num_impostors=1,
        max_ticks=50,
    )

    assert len(report.games) == 1
    game = report.games[0]
    assert game.seed == 7
    assert game.winner is None
    assert game.final_tick is None
    assert "aborted" in game.reason

    # The failed call (and its spend) survives into the report.
    assert len(game.failed_calls) == 1
    assert game.failed_calls[0].cost_usd == pytest.approx(0.02)

    # roles recovered from the seeded setup (re-seeded, not the replay JSONL).
    assert game.roles
    assert sum(1 for role in game.roles.values() if role == "IMPOSTOR") == 1

    # No double-count: per-game total == the canonical reducer over the replay.
    replay_path = tmp_path / game.replay_ref
    assert game.cost.total_cost_usd == pytest.approx(0.02)
    assert game.cost.total_cost_usd == pytest.approx(compute_cost_usd(replay_path))

    # The failed-call spend reaches the cost dashboard exactly once.
    eval_report = build_tournament_eval_report(report)
    assert eval_report.cost_dashboard.total_cost_usd == pytest.approx(0.02)


def test_tournament_reraises_non_parse_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A non-parse-failure exception is not swallowed — it propagates fail-loud."""

    monkeypatch.setattr("eval.balance_eval.HeadlessGame", _BuggyHeadlessGame)

    with pytest.raises(RuntimeError, match="genuine bug"):
        run_tournament_eval(seeds=(7,), output_dir=tmp_path, max_ticks=50)


# ---------------------------------------------------------------------------
# compute_meeting_rate unit coverage (Phase 7 W0.3, DESIGN.md §11.3)
#
# compute_meeting_rate lives in eval/meeting_quality.py (the wrapper/builder
# module), so its focused unit tests live here rather than in a separate
# test_meeting_quality.py (deliberate asymmetry vs. vote_correctness, which has
# its own test module).
# ---------------------------------------------------------------------------

_EMPTY_COST = GameCostSummary(
    total_cost_usd=0.0, total_input_tokens=0, total_output_tokens=0, by_model={}
)
_FOUND_BODY = FoundBodyObservation(
    type="found_body", tick=9, body_of="p-2", room="MedBay"
)
_SAW_PLAYER = SawPlayerObservation(
    type="saw_player", tick=9, subject="p-2", room="MedBay"
)


def _report_doc(
    agent_id: PlayerId,
    observations: tuple[ObservationClaim, ...] = (),
) -> MeetingTurn:
    """An ``opening`` chain turn carrying ``agent_id``'s observations (§5.2)."""

    return MeetingTurn(
        turn_id=f"turn-{agent_id}",
        turn_index=0,
        speaker=agent_id,
        turn_kind="opening",
        reply_to=None,
        observations=observations,
        claims=(),
        free_text="",
    )


def _meeting(
    meeting_id: str,
    triggered_by: PlayerId,
    *,
    trigger: Literal["report", "emergency"] = "report",
    reports: tuple[MeetingTurn, ...] = (),
) -> MeetingReport:
    return MeetingReport(
        meeting_id=meeting_id,
        tick=10,
        triggered_by=triggered_by,
        trigger=trigger,
        outcome="SKIPPED",
        ejected_player_id=None,
        transcript=MeetingTranscript(turns=reports),
        ballots=(),
        contradictions=(),
        llm_calls=(),
    )


def _game(seed: int, *, meetings: tuple[MeetingReport, ...] = ()) -> GameReport:
    return GameReport(
        game_id=f"g-{seed}",
        seed=seed,
        winner="CREWMATES",
        reason="CREWMATE_TASKS",
        final_tick=10,
        roles={"p-1": "CREWMATE"},
        replay_ref=f"replay-seed-{seed}.jsonl",
        meetings=meetings,
        failed_calls=(),
        prompt_versions={},
        cost=_EMPTY_COST,
    )


def test_meeting_rate_none_when_no_games() -> None:
    """meeting_rate is None (undefined), not 0.0, when there are zero games."""

    result = compute_meeting_rate(())
    assert result.games_total == 0
    assert result.games_with_meeting == 0
    assert result.meeting_rate is None
    assert result.meetings_total == 0
    assert result.body_report_meetings == 0
    assert result.emergency_meetings == 0
    assert result.skipped_meetings == 0
    assert result.ejected_meetings == 0


def test_meeting_rate_counts_games_meetings_and_partitions() -> None:
    """Rate / totals / partition over a mix of meeting and meeting-free games."""

    body_meeting = _meeting("g-0:m0", "p-1", trigger="report")
    emergency_meeting = _meeting("g-0:m1", "p-1", trigger="emergency")
    games = (
        _game(0, meetings=(body_meeting, emergency_meeting)),  # 2 meetings
        _game(1, meetings=()),  # no meeting
        _game(2, meetings=(body_meeting,)),  # 1 meeting
    )

    result = compute_meeting_rate(games)

    assert result.games_total == 3
    assert result.games_with_meeting == 2
    assert result.meeting_rate == pytest.approx(2 / 3)
    assert result.meetings_total == 3
    # Two report-triggered (body_meeting x2) + one emergency-triggered.
    assert result.body_report_meetings == 2
    assert result.emergency_meetings == 1
    assert result.body_report_meetings + result.emergency_meetings == 3
    # All fixture meetings default to SKIPPED, so the outcome split is 3/0.
    assert result.skipped_meetings == 3
    assert result.ejected_meetings == 0
    assert result.skipped_meetings + result.ejected_meetings == 3


def test_meeting_classified_body_report_when_trigger_is_report() -> None:
    """A report-triggered meeting counts as body_report (engine trigger decides)."""

    meeting = _meeting("m", "p-1", trigger="report")
    result = compute_meeting_rate((_game(0, meetings=(meeting,)),))
    assert result.body_report_meetings == 1
    assert result.emergency_meetings == 0


def test_meeting_classified_emergency_when_trigger_is_emergency() -> None:
    """An emergency-triggered meeting counts as emergency (engine trigger decides)."""

    meeting = _meeting("m", "p-1", trigger="emergency")
    result = compute_meeting_rate((_game(0, meetings=(meeting,)),))
    assert result.body_report_meetings == 0
    assert result.emergency_meetings == 1


def test_trigger_breakdown_ignores_transcript_contents() -> None:
    """Classification keys off the engine trigger, not the report transcript.

    The old heuristic derived the kind from the triggering player's
    ``FoundBodyObservation``; the breakdown now reads the engine-recorded
    ``trigger``. So a found-body report on an *emergency* meeting still counts as
    emergency, and a found-body-less *report* meeting still counts as a body
    report — the transcript no longer drives the bucket.
    """

    emergency_with_body = _meeting(
        "m-e",
        "p-1",
        trigger="emergency",
        reports=(_report_doc("p-1", (_FOUND_BODY,)),),
    )
    report_without_body = _meeting(
        "m-r",
        "p-2",
        trigger="report",
        reports=(_report_doc("p-2", (_SAW_PLAYER,)),),
    )
    result = compute_meeting_rate(
        (_game(0, meetings=(emergency_with_body, report_without_body)),)
    )
    assert result.body_report_meetings == 1
    assert result.emergency_meetings == 1


def test_meeting_rate_empty_transcript_classifies_by_trigger() -> None:
    """An empty transcript no longer forces emergency; the engine trigger decides."""

    report = _meeting("m-r", "p-1", trigger="report")  # empty transcript
    emergency = _meeting("m-e", "p-2", trigger="emergency")  # empty transcript
    result = compute_meeting_rate((_game(0, meetings=(report, emergency)),))
    assert result.meetings_total == 2
    assert result.body_report_meetings == 1
    assert result.emergency_meetings == 1


def test_compute_meeting_rate_accepts_report_and_bare_sequence() -> None:
    """A TournamentReport and a bare GameReport sequence yield the same result."""

    meeting = _meeting("m", "p-1", reports=(_report_doc("p-1", (_FOUND_BODY,)),))
    games = (_game(0, meetings=(meeting,)), _game(1))
    via_sequence = compute_meeting_rate(games)
    via_report = compute_meeting_rate(
        TournamentReport(format_version=1, games=games, seeds_used=(0, 1))
    )
    assert via_sequence == via_report
    assert via_report.meeting_rate == pytest.approx(0.5)


def test_meeting_rate_outcome_split_counts_ejected_and_skipped() -> None:
    """ejected_meetings / skipped_meetings split each meeting's outcome (F-F-5)."""

    ejected = MeetingReport(
        meeting_id="g-0:m-eject",
        tick=10,
        triggered_by="p-1",
        trigger="report",
        outcome="EJECTED",
        ejected_player_id="p-2",
        transcript=MeetingTranscript(turns=(_report_doc("p-1", (_FOUND_BODY,)),)),
        ballots=(),
        contradictions=(),
        llm_calls=(),
    )
    skipped = _meeting(
        "g-0:m-skip", "p-1", reports=(_report_doc("p-1", (_FOUND_BODY,)),)
    )
    result = compute_meeting_rate((_game(0, meetings=(ejected, skipped)),))

    assert result.meetings_total == 2
    assert result.ejected_meetings == 1
    assert result.skipped_meetings == 1
    assert result.skipped_meetings + result.ejected_meetings == result.meetings_total


def test_meeting_rate_validator_rejects_bad_partition() -> None:
    """body + emergency must equal meetings_total (fail-loud)."""

    with pytest.raises(ValidationError, match="must equal meetings_total"):
        MeetingRateReport(
            games_total=1,
            games_with_meeting=1,
            meeting_rate=1.0,
            meetings_total=2,
            body_report_meetings=1,
            emergency_meetings=0,  # 1 + 0 != 2
            skipped_meetings=2,
            ejected_meetings=0,
        )


def test_meeting_rate_validator_rejects_bad_outcome_partition() -> None:
    """skipped + ejected must equal meetings_total (fail-loud)."""

    with pytest.raises(
        ValidationError, match="skipped_meetings \\+ ejected_meetings must equal"
    ):
        MeetingRateReport(
            games_total=1,
            games_with_meeting=1,
            meeting_rate=1.0,
            meetings_total=2,
            body_report_meetings=2,
            emergency_meetings=0,
            skipped_meetings=1,
            ejected_meetings=0,  # 1 + 0 != 2
        )


def test_meeting_rate_validator_rejects_games_with_meeting_over_total() -> None:
    """games_with_meeting cannot exceed games_total (fail-loud)."""

    with pytest.raises(ValidationError, match="cannot exceed games_total"):
        MeetingRateReport(
            games_total=1,
            games_with_meeting=2,  # > games_total
            meeting_rate=1.0,
            meetings_total=0,
            body_report_meetings=0,
            emergency_meetings=0,
            skipped_meetings=0,
            ejected_meetings=0,
        )


def test_meeting_rate_validator_rejects_rate_set_with_zero_games() -> None:
    """meeting_rate must be None when games_total == 0."""

    with pytest.raises(ValidationError, match="must be None when there are no games"):
        MeetingRateReport(
            games_total=0,
            games_with_meeting=0,
            meeting_rate=0.0,  # must be None
            meetings_total=0,
            body_report_meetings=0,
            emergency_meetings=0,
            skipped_meetings=0,
            ejected_meetings=0,
        )


def test_meeting_rate_validator_rejects_none_rate_with_games() -> None:
    """meeting_rate must be set when games_total > 0."""

    with pytest.raises(ValidationError, match="must be set when games_total"):
        MeetingRateReport(
            games_total=1,
            games_with_meeting=0,
            meeting_rate=None,  # must be a float
            meetings_total=0,
            body_report_meetings=0,
            emergency_meetings=0,
            skipped_meetings=0,
            ejected_meetings=0,
        )


def test_meeting_rate_validator_rejects_negative_counts() -> None:
    """Negative counts are rejected (fail-loud)."""

    with pytest.raises(ValidationError, match="must be non-negative"):
        MeetingRateReport(
            games_total=1,
            games_with_meeting=-1,
            meeting_rate=0.0,
            meetings_total=0,
            body_report_meetings=0,
            emergency_meetings=0,
            skipped_meetings=0,
            ejected_meetings=0,
        )
