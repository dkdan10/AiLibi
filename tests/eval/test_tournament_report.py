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

import pytest
from pydantic import TypeAdapter

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
    TournamentEvalReport,
    build_tournament_eval_report,
)
from eval.report_schema import TournamentReport
from eval.vote_correctness import VoteCorrectnessReport
from llm.provider import LLMCallFailure, _attach_parse_failure
from meetings.schemas import MeetingTranscript
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

# Seeds that fire at least one meeting under the fake provider at this config
# (probed at HEAD: each ends CREWMATES after one meeting). Picked so the loader
# exercises the MeetingReplayEntry -> MeetingReport mapping, not just empty games.
_MEETING_FIRING_SEEDS = (3, 4, 5)
_NUM_PLAYERS = 5
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

    # The wrapper carries all four Phase 5 metric blocks.
    eval_report = build_tournament_eval_report(report)
    assert isinstance(eval_report.vote_correctness, VoteCorrectnessReport)
    assert isinstance(eval_report.accusation_calibration, AccusationCalibrationReport)
    assert isinstance(eval_report.alibi_fabrication, AlibiFabricationReport)
    assert isinstance(eval_report.cost_dashboard, CostDashboard)

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


# ---------------------------------------------------------------------------
# Loader unit tests over hand-written replay files
# ---------------------------------------------------------------------------


def test_loader_does_not_double_count_failed_call_cost(tmp_path: Path) -> None:
    """total_cost_usd == compute_cost_usd == single-counted meeting+failed spend."""

    path = tmp_path / "replay-seed-99.jsonl"
    entries: list[ReplayLogEntry] = [
        ReplayEntry(game_id="g", tick=0, actions=(), state_hash="h0"),
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
