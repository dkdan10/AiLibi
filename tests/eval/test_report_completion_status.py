"""Verified terminal outcomes and nonterminal reasons have distinct denominators."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from eval.balance_eval import (
    _balance_report_from_tournament,
    build_tournament_report,
    load_historical_tournament_report,
    load_tournament_report,
    run_tournament_eval,
)
from eval.report_schema import GameCostSummary, GameReport
from tests.eval.test_report_replay_integrity import _roles
from tests.eval.test_tournament_report import _ParseFailureMeetingRunner, _wait_factory
from tests.orchestrator.test_replay_integrity import (
    _game,
    completed_recording as completed_recording,
)


def _report(seed: int, **updates: object) -> GameReport:
    return GameReport.model_validate(
        {
            "game_id": f"headless-seed-{seed}",
            "seed": seed,
            "winner": None,
            "reason": "no game_over record in replay",
            "final_tick": None,
            "roles": {"p-1": "IMPOSTOR", "p-2": "CREWMATE"},
            "replay_ref": f"replay-seed-{seed}.jsonl",
            "meetings": (),
            "failed_calls": (),
            "prompt_versions": {},
            "cost": GameCostSummary(
                total_cost_usd=0.1,
                total_input_tokens=10,
                total_output_tokens=2,
                by_model={"injected": 0.1},
            ),
            **updates,
        }
    )


def test_mixed_statuses_do_not_treat_every_missing_winner_as_tick_limit() -> None:
    games = (
        _report(0, winner="CREWMATES", outcome_verified=True),
        _report(1, winner="IMPOSTORS", outcome_verified=True),
        _report(2, reason="TICK_BUDGET_REACHED"),
        _report(3, completion_status="aborted"),
        _report(4),
        _report(5, winner="CREWMATES"),
    )
    tournament = build_tournament_report(games=games, seeds=range(8))
    counts = _balance_report_from_tournament(tournament)
    assert counts.games == 6
    assert counts.crew_wins == counts.impostor_wins == 1
    assert counts.verified_outcomes == 2
    assert (
        counts.tick_budget_reached
        == counts.aborted
        == counts.unfinished
        == counts.unverified
        == 1
    )
    assert sum(game.cost.total_cost_usd for game in tournament.games) == pytest.approx(
        0.6
    )
    assert tournament.seeds_used == tuple(range(8))


def test_legacy_serialized_report_does_not_manufacture_verification() -> None:
    game = _report(1, winner="CREWMATES")
    raw = game.model_dump(
        mode="json", exclude={"completion_status", "outcome_verified"}
    )
    loaded = GameReport.model_validate_json(json.dumps(raw))
    assert loaded.completion_status == "completed"
    assert loaded.outcome_verified is False
    raw["winner"] = None
    assert GameReport.model_validate(raw).completion_status == "unfinished"
    with pytest.raises(ValidationError, match="verified outcome requires"):
        GameReport.model_validate({**raw, "outcome_verified": True})


def test_current_load_verifies_outcome_but_historical_profile_remains_unverified(
    completed_recording: Path,
) -> None:
    current = load_tournament_report(
        completed_recording.parent, roles_by_seed={1: _roles()}
    )
    historical = load_historical_tournament_report(
        completed_recording.parent, roles_by_seed={1: _roles()}
    )
    assert (
        current.games[0].completion_status
        == historical.games[0].completion_status
        == "completed"
    )
    assert current.games[0].outcome_verified
    assert not historical.games[0].outcome_verified
    assert current.games[0].winner == historical.games[0].winner
    assert current.games[0].cost == historical.games[0].cost


def test_stop_status_survives_reload_while_unstamped_prefix_remains_unfinished(
    tmp_path: Path,
) -> None:
    path = tmp_path / "replay-seed-1.jsonl"
    _game(path, max_ticks=5).run()
    stopped = load_tournament_report(tmp_path, roles_by_seed={1: _roles()}).games[0]
    assert stopped.completion_status == "tick_limited"
    assert stopped.reason == "TICK_BUDGET_REACHED"
    assert not stopped.outcome_verified
    lines = path.read_text().splitlines()
    path.write_text("\n".join(lines[:-1]) + "\n")
    prefix = load_tournament_report(tmp_path, roles_by_seed={1: _roles()}).games[0]
    assert prefix.completion_status == "unfinished"
    assert not prefix.outcome_verified


def test_real_eval_reports_explicit_tick_limit_and_paid_abort_separately(
    tmp_path: Path,
) -> None:
    limited = run_tournament_eval(
        seeds=(0,),
        output_dir=tmp_path / "limited",
        agent_factory=_wait_factory,
        max_ticks=1,
    )
    aborted = run_tournament_eval(
        seeds=(1,),
        output_dir=tmp_path / "aborted",
        meeting_runner_factory=_ParseFailureMeetingRunner,
        max_ticks=200,
    )
    assert limited.games[0].completion_status == "tick_limited"
    assert aborted.games[0].completion_status == "aborted"
    assert not aborted.games[0].outcome_verified
    assert aborted.games[0].cost.total_cost_usd > 0
