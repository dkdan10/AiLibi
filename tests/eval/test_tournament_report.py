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
