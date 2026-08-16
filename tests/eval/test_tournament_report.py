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
from tempfile import TemporaryDirectory
from typing import Literal

import pytest
from pydantic import TypeAdapter, ValidationError

from agents.base import AgentInterface
from engine.actions import Action
from engine.entities import PlayerId, Role
from engine.events import GameOverEvent
from engine.tick import advance_tick
from engine.world import Map, load_canonical_map
from eval.accusation_calibration import AccusationCalibrationReport
from eval.alibi_fabrication import AlibiFabricationReport
from eval.balance_eval import (
    _game_report_from_replay,
    _kill_gift_accounting,
    load_tournament_report,
    run_tournament_eval,
)
from eval.cost_dashboard import CostDashboard
from eval.deduction_metrics import DeductionMetricsReport
from eval.meeting_quality import (
    MeetingRateReport,
    TournamentEvalReport,
    build_tournament_eval_report,
    compute_meeting_rate,
)
from eval.report_schema import (
    CURRENT_FORMAT_VERSION,
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

    # Task 19.14: the deduction block rides on the wrapper and spans the same
    # games/meetings the rest of the report does. Its two cross-tab partitions
    # are cut differently but must BOTH span every ejection — the assembly-side
    # half of the define-before-counting rule (the module's own validators cover
    # the within-partition arithmetic; `tests/eval/test_deduction_metrics.py`
    # carries the committed-bytes pins).
    deduction = eval_report.deduction
    assert isinstance(deduction, DeductionMetricsReport)
    assert deduction.games_total == len(report.games)
    assert deduction.meetings_total == mr.meetings_total
    assert deduction.ejections_total == mr.ejected_meetings
    assert deduction.meeting_flag_cross_tab.meetings_total == mr.meetings_total
    assert deduction.ejectee_proof_cross_tab.ejections_total == mr.ejected_meetings
    # No kill-craft report was supplied (a live tournament has no committed
    # replay directory to walk at assembly time), so the supply cells are the
    # explicit "not supplied" sentinel rather than zeros.
    assert deduction.witnessed_supply is None

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
    # Task 19.5's None-iff-undefined convention: with no impostor alibis the
    # survival rate is undefined (None), never the retired division-safe 0.0.
    assert eval_report.alibi_fabrication.survival_rate is None
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
        tactical_policy_stamp: object = None,
        # The Task-18.7 additive crew-stamp kwarg the harness threads (default
        # None, mirroring HeadlessGame): the stub accepts it so the seam stays
        # signature-faithful; the abort path never records a game_over to stamp.
        crew_tactical_policy_stamp: object = None,
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
        TournamentReport(
            format_version=CURRENT_FORMAT_VERSION, games=games, seeds_used=(0, 1)
        )
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


# ---------------------------------------------------------------------------
# Kill-gifted win accounting derivation (Task 8.17; DESIGN.md §3.5; audit gp-4).
# The flag is now VICTIM-anchored: kill-gifted iff a CREWMATE_TASKS win's final
# tick resolves a kill whose victim held >= 1 incomplete instance at kill
# resolution (Task 9.1, audit A-A-2 -- the old "no TaskCompleted on the final
# tick" definition undercounted 8/46 vs the true 11/46 because a same-tick
# completion by another player masked a genuine gift).
#
# The flag is deterministic from the replay: the loader re-seeds and re-applies
# the recorded action stream through the engine (the win-condition-selfcheck
# pattern). These tests build SYNTHETIC replays on a custom map whose tasks all
# sit in the spawn room and complete in one tick, so a tiny scripted game can
# force each ending precisely -- a kill-gifted task win, an organic task win, a
# MASKED gift (a same-tick completion by ANOTHER player still flags), a victim
# self-completion the same tick (NOT gifted), and a kill-driven impostor win --
# and the engine walk reconstructs them byte-faithfully (state_hash verified).
# ---------------------------------------------------------------------------

# All map tasks moved into the spawn room with duration 1: every crewmate spawns
# on its task and completes it in a single do_task tick, so the scripted games
# below need no movement. ``kill_cooldown_ticks`` is set to 1 (the map minimum)
# so the Task 8.14 round-start cooldown re-seed (impostors start at
# ``kill_cooldown_ticks``) decrements to 0 after a single tick-0 wait -- every
# scripted kill below fires on tick 1+, so it is accepted under both the
# round-start cooldown and the historical zero-cooldown seeder. The map id is
# unchanged, so the engine's state-map guard and the seeder accept it; the walk is
# handed this SAME map so its reconstructed state_hash matches the recording.
_KILL_GIFT_MAP: Map = load_canonical_map().model_copy(
    update={
        "kill_cooldown_ticks": 1,
        # The kill-gift mechanic is a DROP-rule property (a kill that removes the
        # crew's last incomplete instance gifts the task-win). The Task 13.12 flip
        # made the canonical map ``redistribute`` (which re-keys instead of
        # dropping, so a kill never gifts), so pin the rule EXPLICITLY to ``drop``
        # here — this map tests the drop-rule kill-gift semantics, independent of
        # the canonical default.
        "dead_task_rule": "drop",
        "tasks": {
            task_id: task.model_copy(
                update={"room": load_canonical_map().spawn.room, "duration_ticks": 1}
            )
            for task_id, task in load_canonical_map().tasks.items()
        },
    }
)

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _wait(actor: PlayerId) -> Action:
    return _ACTION_ADAPTER.validate_python(
        {"type": "wait", "actor": actor, "payload": {}}
    )


def _do_task(actor: PlayerId, map_task_id: str) -> Action:
    return _ACTION_ADAPTER.validate_python(
        {"type": "do_task", "actor": actor, "payload": {"task_id": map_task_id}}
    )


def _kill(actor: PlayerId, target: PlayerId) -> Action:
    return _ACTION_ADAPTER.validate_python(
        {"type": "kill", "actor": actor, "payload": {"target": target}}
    )


def _kill_gift_layout(
    seed: int, *, num_players: int, num_impostors: int
) -> tuple[list[PlayerId], PlayerId, dict[PlayerId, str]]:
    """Return (sorted crewmates, the impostor, owner -> own map task id) for a seed.

    Reads the deterministic seeding on ``_KILL_GIFT_MAP`` so a scripted game can
    target the actual seeded roles + each crewmate's own (map) task id.
    """

    state = seed_initial_state(
        seed=seed,
        game_map=_KILL_GIFT_MAP,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=1,
    )
    crew = [
        pid for pid in sorted(state.players) if state.players[pid].role == "CREWMATE"
    ]
    impostor = next(
        pid for pid in sorted(state.players) if state.players[pid].role == "IMPOSTOR"
    )
    own = {task.owner: task.map_task_id for task in state.tasks.values()}
    return crew, impostor, own


def _seeded_roles_for(
    seed: int, *, num_players: int, num_impostors: int
) -> dict[PlayerId, Role]:
    """Role ground truth for a seed on ``_KILL_GIFT_MAP`` (the loader's input)."""

    state = seed_initial_state(
        seed=seed,
        game_map=_KILL_GIFT_MAP,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=1,
    )
    return {pid: player.role for pid, player in state.players.items()}


def _record_scripted_game(
    replay_path: Path,
    *,
    seed: int,
    num_players: int,
    num_impostors: int,
    scripted: list[list[Action]],
) -> None:
    """Drive a seeded game through ``advance_tick`` and record the replay JSONL.

    Mirrors the orchestrator's recording convention exactly
    (``record_tick(state.tick_before, actions, state_after)`` +
    ``record_game_end`` from the ``GameOverEvent``), so the loader's engine walk
    reconstructs it byte-faithfully. Asserts the script actually reaches
    ``GAME_OVER`` so a mis-scripted fixture fails loud here, not as a silent
    no-gift default.
    """

    state = seed_initial_state(
        seed=seed,
        game_map=_KILL_GIFT_MAP,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=1,
    )
    game_over: GameOverEvent | None = None
    final_tick: int | None = None
    with ReplayLog(replay_path, game_id=f"headless-seed-{seed}", force=True) as log:
        for actions in scripted:
            input_tick = state.tick
            state, events = advance_tick(state, actions, game_map=_KILL_GIFT_MAP)
            log.record_tick(input_tick, actions, state)
            final_tick = input_tick
            if state.phase == "GAME_OVER":
                game_over = next(e for e in events if isinstance(e, GameOverEvent))
                break
        assert game_over is not None, "scripted kill-gift fixture never ended"
        log.record_game_end(
            winner=game_over.winner, reason=game_over.reason, tick=final_tick
        )


def test_kill_gifted_win_is_flagged() -> None:
    """A CREWMATE_TASKS win whose final tick is a kill (no completion) is gifted.

    4p/1i: two crewmates finish their tasks, then the impostor kills the third
    (its incomplete instance drops via §3.5), completing the pool on the kill
    tick without reaching parity -- the gp-4 / A-A-1 kill-gift signature.
    """

    seed = 1
    crew, impostor, own = _kill_gift_layout(seed, num_players=4, num_impostors=1)
    finisher_a, finisher_b, victim = crew
    with TemporaryDirectory() as tmp:
        replay = Path(tmp) / f"replay-seed-{seed}.jsonl"
        _record_scripted_game(
            replay,
            seed=seed,
            num_players=4,
            num_impostors=1,
            scripted=[
                [
                    _do_task(finisher_a, own[finisher_a]),
                    _do_task(finisher_b, own[finisher_b]),
                    _wait(victim),
                    _wait(impostor),
                ],
                [
                    _kill(impostor, victim),
                    _wait(finisher_a),
                    _wait(finisher_b),
                ],
            ],
        )
        facts = _kill_gift_accounting(
            replay,
            seed=seed,
            roles=_seeded_roles_for(seed, num_players=4, num_impostors=1),
            tasks_per_crewmate=1,
            game_map=_KILL_GIFT_MAP,
        )

    assert facts.kill_gifted is True
    assert facts.instances_dropped == 1  # the victim's incomplete instance
    assert facts.instances_complete_at_win == 2  # the two finishers


def test_organic_task_win_is_not_kill_gifted() -> None:
    """A CREWMATE_TASKS win completed by a do_task (no final-tick kill) is organic."""

    seed = 2
    crew, impostor, own = _kill_gift_layout(seed, num_players=4, num_impostors=1)
    finisher_a, finisher_b, finisher_c = crew
    with TemporaryDirectory() as tmp:
        replay = Path(tmp) / f"replay-seed-{seed}.jsonl"
        _record_scripted_game(
            replay,
            seed=seed,
            num_players=4,
            num_impostors=1,
            scripted=[
                [
                    _do_task(finisher_a, own[finisher_a]),
                    _do_task(finisher_b, own[finisher_b]),
                    _wait(finisher_c),
                    _wait(impostor),
                ],
                [
                    _do_task(finisher_c, own[finisher_c]),
                    _wait(finisher_a),
                    _wait(finisher_b),
                    _wait(impostor),
                ],
            ],
        )
        facts = _kill_gift_accounting(
            replay,
            seed=seed,
            roles=_seeded_roles_for(seed, num_players=4, num_impostors=1),
            tasks_per_crewmate=1,
            game_map=_KILL_GIFT_MAP,
        )

    assert facts.kill_gifted is False
    assert facts.instances_dropped == 0  # no kill, nothing dropped
    assert facts.instances_complete_at_win == 3  # all three completed


def test_masked_gift_same_tick_completion_by_another_player_still_flags() -> None:
    """A same-tick completion by ANOTHER player does NOT mask a genuine gift (DoD).

    5p/1i: two crewmates finish early; on the final tick a third completes its
    OWN task AND the impostor kills the fourth, who still held an incomplete
    instance. The kill's §3.5 drop of that incomplete instance is what tips the
    pool to complete -- the win could not have fired without it -- so it IS
    kill-gifted even though an unrelated completion also resolved this tick. This
    is the audit A-A-2 masked-gift class (seed 11 tick 20) the old completion-based
    definition wrongly excluded; the corrected predicate is victim-anchored, not
    tick-completion-anchored.
    """

    seed = 3
    crew, impostor, own = _kill_gift_layout(seed, num_players=5, num_impostors=1)
    finisher_a, finisher_b, finisher_c, victim = crew
    with TemporaryDirectory() as tmp:
        replay = Path(tmp) / f"replay-seed-{seed}.jsonl"
        _record_scripted_game(
            replay,
            seed=seed,
            num_players=5,
            num_impostors=1,
            scripted=[
                [
                    _do_task(finisher_a, own[finisher_a]),
                    _do_task(finisher_b, own[finisher_b]),
                    _wait(finisher_c),
                    _wait(victim),
                    _wait(impostor),
                ],
                [
                    _do_task(finisher_c, own[finisher_c]),
                    _kill(impostor, victim),
                    _wait(finisher_a),
                    _wait(finisher_b),
                ],
            ],
        )
        facts = _kill_gift_accounting(
            replay,
            seed=seed,
            roles=_seeded_roles_for(seed, num_players=5, num_impostors=1),
            tasks_per_crewmate=1,
            game_map=_KILL_GIFT_MAP,
        )

    # The victim held an incomplete instance at kill resolution; finisher_c's
    # same-tick completion is on a DIFFERENT player, so it cannot mask the gift.
    assert facts.kill_gifted is True
    assert facts.instances_dropped == 1  # the victim's incomplete instance
    assert facts.instances_complete_at_win == 3


def test_victim_self_completed_same_tick_is_not_kill_gifted() -> None:
    """A victim that self-completed its last instance before the kill is NOT gifted.

    5p/1i: three crewmates finish early; on the final tick the fourth completes
    its OWN last instance FIRST and is THEN killed (the action order puts the
    victim's do_task before the impostor's kill, as the orchestrator's id-ordered
    resolution does when the victim's id precedes the killer's). The victim holds
    NO incomplete instance at kill resolution, so the §3.5 drop removes nothing
    and the win rode the victim's own completion, not the kill -- correctly
    excluded. This is the audit A-A-2 counter-example (seed 40 tick 22) that the
    victim-anchored predicate keeps excluded where reading the pre-tick incomplete
    count alone would wrongly flag it.
    """

    seed = 5
    crew, impostor, own = _kill_gift_layout(seed, num_players=5, num_impostors=1)
    finisher_a, finisher_b, finisher_c, victim = crew
    with TemporaryDirectory() as tmp:
        replay = Path(tmp) / f"replay-seed-{seed}.jsonl"
        _record_scripted_game(
            replay,
            seed=seed,
            num_players=5,
            num_impostors=1,
            scripted=[
                [
                    _do_task(finisher_a, own[finisher_a]),
                    _do_task(finisher_b, own[finisher_b]),
                    _do_task(finisher_c, own[finisher_c]),
                    _wait(victim),
                    _wait(impostor),
                ],
                [
                    # Victim self-completes BEFORE the kill resolves this tick, so
                    # its now-complete instance survives the §3.5 drop.
                    _do_task(victim, own[victim]),
                    _kill(impostor, victim),
                    _wait(finisher_a),
                    _wait(finisher_b),
                ],
            ],
        )
        facts = _kill_gift_accounting(
            replay,
            seed=seed,
            roles=_seeded_roles_for(seed, num_players=5, num_impostors=1),
            tasks_per_crewmate=1,
            game_map=_KILL_GIFT_MAP,
        )

    assert facts.kill_gifted is False  # victim held no incomplete instance
    assert facts.instances_dropped == 0  # the completed instance survives the drop
    assert facts.instances_complete_at_win == 4


def test_kill_driven_impostor_win_is_not_kill_gifted() -> None:
    """A kill that ends the game as an IMPOSTOR parity win is not kill-gifted.

    The flag is gated on a CREWMATE_TASKS win; a final-tick kill that reaches
    parity (3p/1i -> 1 impostor vs 1 crewmate) is an impostor win, so even though
    the deciding event is a kill it is not gifted, and ``instances_dropped`` still
    reflects the victim's dropped instance.
    """

    seed = 4
    crew, impostor, _own = _kill_gift_layout(seed, num_players=3, num_impostors=1)
    victim = crew[0]
    with TemporaryDirectory() as tmp:
        replay = Path(tmp) / f"replay-seed-{seed}.jsonl"
        _record_scripted_game(
            replay,
            seed=seed,
            num_players=3,
            num_impostors=1,
            # Tick 0 waits so the round-start kill cooldown decrements to 0; the
            # parity kill fires on tick 1.
            scripted=[
                [_wait(impostor), _wait(crew[0]), _wait(crew[1])],
                [_kill(impostor, victim), _wait(crew[1])],
            ],
        )
        facts = _kill_gift_accounting(
            replay,
            seed=seed,
            roles=_seeded_roles_for(seed, num_players=3, num_impostors=1),
            tasks_per_crewmate=1,
            game_map=_KILL_GIFT_MAP,
        )

    assert facts.kill_gifted is False
    assert facts.instances_dropped == 1


def test_load_tournament_report_rolls_up_kill_gift_aggregates(tmp_path: Path) -> None:
    """load_tournament_report folds the per-game facts and the tournament roll-ups.

    Records a gifted game and an organic game in one dir and loads them through
    the public report path, asserting both the per-game flag/counts and the
    aggregate roll-ups (kill-gifted win count, total dropped, mean complete-at-win
    over the CREWMATE_TASKS wins).
    """

    roles_by_seed: dict[int, dict[PlayerId, Role]] = {}
    # Gifted (seed 1): two finishers + a final-tick kill.
    crew, impostor, own = _kill_gift_layout(1, num_players=4, num_impostors=1)
    _record_scripted_game(
        tmp_path / "replay-seed-1.jsonl",
        seed=1,
        num_players=4,
        num_impostors=1,
        scripted=[
            [
                _do_task(crew[0], own[crew[0]]),
                _do_task(crew[1], own[crew[1]]),
                _wait(crew[2]),
                _wait(impostor),
            ],
            [_kill(impostor, crew[2]), _wait(crew[0]), _wait(crew[1])],
        ],
    )
    roles_by_seed[1] = _seeded_roles_for(1, num_players=4, num_impostors=1)
    # Organic (seed 2): the pool finishes by a do_task.
    crew2, impostor2, own2 = _kill_gift_layout(2, num_players=4, num_impostors=1)
    _record_scripted_game(
        tmp_path / "replay-seed-2.jsonl",
        seed=2,
        num_players=4,
        num_impostors=1,
        scripted=[
            [
                _do_task(crew2[0], own2[crew2[0]]),
                _do_task(crew2[1], own2[crew2[1]]),
                _wait(crew2[2]),
                _wait(impostor2),
            ],
            [
                _do_task(crew2[2], own2[crew2[2]]),
                _wait(crew2[0]),
                _wait(crew2[1]),
                _wait(impostor2),
            ],
        ],
    )
    roles_by_seed[2] = _seeded_roles_for(2, num_players=4, num_impostors=1)

    report = load_tournament_report(
        tmp_path,
        roles_by_seed=roles_by_seed,
        tasks_per_crewmate=1,
        game_map=_KILL_GIFT_MAP,
    )

    by_seed = {game.seed: game for game in report.games}
    assert by_seed[1].kill_gifted is True
    assert by_seed[1].instances_dropped == 1
    assert by_seed[1].instances_complete_at_win == 2
    assert by_seed[2].kill_gifted is False
    assert by_seed[2].instances_dropped == 0
    assert by_seed[2].instances_complete_at_win == 3

    # Roll-ups: one gifted win; total dropped = 1 + 0; mean complete-at-win over
    # the two CREWMATE_TASKS wins = (2 + 3) / 2 = 2.5.
    assert report.kill_gifted_wins == 1
    assert report.instances_dropped_total == 1
    assert report.mean_instances_complete_at_win == pytest.approx(2.5)


def test_mean_complete_at_win_is_none_without_a_task_win(tmp_path: Path) -> None:
    """The mean is None (undefined) when no game is a CREWMATE_TASKS win.

    A lone impostor-parity game has no task win to average, so the roll-up uses
    the same undefined-not-zero sentinel the other eval rates use.
    """

    crew, impostor, _own = _kill_gift_layout(4, num_players=3, num_impostors=1)
    _record_scripted_game(
        tmp_path / "replay-seed-4.jsonl",
        seed=4,
        num_players=3,
        num_impostors=1,
        # Tick 0 waits out the round-start cooldown; the parity kill is on tick 1.
        scripted=[
            [_wait(impostor), _wait(crew[0]), _wait(crew[1])],
            [_kill(impostor, crew[0]), _wait(crew[1])],
        ],
    )
    report = load_tournament_report(
        tmp_path,
        roles_by_seed={4: _seeded_roles_for(4, num_players=3, num_impostors=1)},
        tasks_per_crewmate=1,
        game_map=_KILL_GIFT_MAP,
    )

    assert report.games[0].winner == "IMPOSTORS"
    assert report.kill_gifted_wins == 0
    assert report.mean_instances_complete_at_win is None
