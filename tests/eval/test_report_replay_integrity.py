"""Current reports certify the same recorded timeline as spectator playback."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from api.replay_loader import ReplayLoader
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from eval.balance_eval import (
    load_historical_tournament_report,
    load_tournament_report,
    run_tournament_eval,
)
from eval.validity import run_validity_gate
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    HeadlessGame,
    HeadlessGameResult,
    build_default_meeting_runner,
)
from orchestrator.replay import compute_cost_usd
from orchestrator.replay_integrity import ReplayIntegrityError
from orchestrator.seeder import seed_initial_state
from tests.eval.test_tournament_report import _ParseFailureMeetingRunner
from tests.orchestrator.test_replay_integrity import (
    Mutation,
    _alter,
    _game,
    _rows,
    _write,
    completed_recording as completed_recording,
    ejection_recording as ejection_recording,
)


def _roles(seed: int = 1) -> dict[PlayerId, Role]:
    state = seed_initial_state(
        seed=seed,
        game_map=load_canonical_map(),
        num_players=7,
        num_impostors=1,
        tasks_per_crewmate=1,
    )
    return {pid: player.role for pid, player in state.players.items()}


@pytest.mark.parametrize("derive_kill_gift", [False, True])
@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ("terminal_winner", "recorded_outcome_mismatch"),
        ("terminal_reason", "recorded_outcome_mismatch"),
        ("tick_label", "tick_label_mismatch"),
        ("terminal_tick", "terminal_tick_mismatch"),
        ("premature_terminal", "recorded_outcome_mismatch"),
        ("reordered_meetings", "row_order"),
        ("orphan_meeting", "meeting_trigger_mismatch"),
        ("duplicate_meeting", "row_order"),
        ("mixed_game_ids", "row_order"),
        ("post_terminal_tick", "row_order"),
        ("reticked_meeting", "row_order"),
        ("missing_meeting", "row_order"),
        ("meeting_pre_hash", "meeting_pre_hash_mismatch"),
        ("meeting_reporter", "meeting_trigger_mismatch"),
    ],
)
def test_current_report_rejects_playback_corruption(
    completed_recording: Path,
    tmp_path: Path,
    mutation: Mutation,
    code: str,
    derive_kill_gift: bool,
) -> None:
    _alter(completed_recording, tmp_path / completed_recording.name, mutation)
    with pytest.raises(ReplayIntegrityError) as playback:
        ReplayLoader(tmp_path).load_replay("headless-seed-1")
    assert playback.value.code == code
    with pytest.raises(ReplayIntegrityError) as report:
        load_tournament_report(
            tmp_path,
            roles_by_seed={1: _roles()},
            derive_kill_gift=derive_kill_gift,
        )
    assert report.value.code == code


@pytest.mark.parametrize("derive_kill_gift", [False, True])
def test_current_report_accepts_genuine_complete_recording(
    completed_recording: Path,
    derive_kill_gift: bool,
) -> None:
    report = load_tournament_report(
        completed_recording.parent,
        roles_by_seed={1: _roles()},
        derive_kill_gift=derive_kill_gift,
    )
    assert report.games[0].winner == "CREWMATES"
    assert report.games[0].reason == "CREWMATE_TASKS"
    assert len(report.games[0].meetings) == 2


@pytest.mark.parametrize("derive_kill_gift", [False, True])
@pytest.mark.parametrize("fail_meeting", [False, True])
def test_current_report_accepts_unfinished_or_aborted_game(
    tmp_path: Path,
    derive_kill_gift: bool,
    fail_meeting: bool,
) -> None:
    path = tmp_path / "replay-seed-1.jsonl"
    game = _game(path, max_ticks=200 if fail_meeting else 5, fail_meeting=fail_meeting)
    if fail_meeting:
        with pytest.raises(RuntimeError, match="injected provider failure"):
            game.run()
    else:
        game.run()
    report = load_tournament_report(
        tmp_path,
        roles_by_seed={1: _roles()},
        derive_kill_gift=derive_kill_gift,
    )
    assert report.games[0].winner is None
    assert report.games[0].final_tick is None


def test_current_report_accepts_meeting_terminal_and_legacy_missing_tick(
    ejection_recording: Path,
    tmp_path: Path,
) -> None:
    rows = _rows(ejection_recording)
    del rows[-1]["tick"]
    _write(tmp_path / ejection_recording.name, rows)
    report = load_tournament_report(tmp_path, roles_by_seed={1: _roles()})
    assert report.games[0].winner == "CREWMATES"
    assert report.games[0].reason == "CREWMATE_EJECT"
    assert report.games[0].final_tick is None


@pytest.mark.parametrize("derive_kill_gift", [False, True])
def test_supplied_role_truth_must_match_the_seeded_setup(
    completed_recording: Path,
    derive_kill_gift: bool,
) -> None:
    roles = _roles()
    crew = next(pid for pid, role in roles.items() if role == "CREWMATE")
    impostor = next(pid for pid, role in roles.items() if role == "IMPOSTOR")
    roles[crew], roles[impostor] = roles[impostor], roles[crew]
    with pytest.raises(ReplayIntegrityError, match="role_setup_mismatch"):
        load_tournament_report(
            completed_recording.parent,
            roles_by_seed={1: roles},
            derive_kill_gift=derive_kill_gift,
        )


@pytest.mark.parametrize("derive_kill_gift", [False, True])
def test_wrong_task_count_cannot_bypass_validation(
    completed_recording: Path,
    derive_kill_gift: bool,
) -> None:
    with pytest.raises(ReplayIntegrityError, match="tick_hash_mismatch"):
        load_tournament_report(
            completed_recording.parent,
            roles_by_seed={1: _roles()},
            tasks_per_crewmate=2,
            derive_kill_gift=derive_kill_gift,
        )


def test_historical_fold_and_raw_cost_remain_available(
    completed_recording: Path,
    tmp_path: Path,
) -> None:
    rows = _rows(completed_recording)
    meeting = next(row for row in rows if row["kind"] == "meeting")
    calls = meeting["llm_calls"]
    assert isinstance(calls, list) and calls
    calls[0]["cost_usd"] = 0.25
    rows[-1]["winner"] = "IMPOSTORS"
    path = tmp_path / completed_recording.name
    _write(path, rows)
    before = path.read_bytes()
    assert compute_cost_usd(path) == pytest.approx(0.25)
    with pytest.raises(ReplayIntegrityError, match="recorded_outcome_mismatch"):
        load_tournament_report(tmp_path, roles_by_seed={1: _roles()})
    historical = load_historical_tournament_report(
        tmp_path,
        roles_by_seed={1: _roles()},
    )
    assert historical.games[0].winner == "IMPOSTORS"
    assert historical.games[0].cost.total_cost_usd == pytest.approx(0.25)
    assert compute_cost_usd(path) == pytest.approx(0.25)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "mutation", ["terminal_winner", "tick_label", "reordered_meetings"]
)
def test_sample_report_builder_cannot_publish_corrupt_outcome(
    completed_recording: Path,
    tmp_path: Path,
    mutation: Mutation,
) -> None:
    from build_sample_report import write_report

    _alter(completed_recording, tmp_path / completed_recording.name, mutation)
    (tmp_path / "roster.json").write_text(
        json.dumps(
            {
                "num_players": 7,
                "num_impostors": 1,
                "tasks_per_crewmate": 1,
            }
        )
    )
    report_path = tmp_path / "tournament-eval-report.json"
    report_path.write_text("previous report\n")
    with pytest.raises(ReplayIntegrityError):
        write_report(tmp_path)
    assert report_path.read_text() == "previous report\n"


def test_full_validity_gate_rejects_forged_winner(
    completed_recording: Path,
    tmp_path: Path,
) -> None:
    (tmp_path / "roster.json").write_text(
        json.dumps(
            {
                "num_players": 7,
                "num_impostors": 1,
                "tasks_per_crewmate": 1,
            }
        )
    )
    (tmp_path / completed_recording.name).write_bytes(completed_recording.read_bytes())
    clean = run_validity_gate(tmp_path)
    clean_integrity = next(
        check for check in clean.checks if check.name == "byte_identical_reconstruction"
    )
    assert clean_integrity.passed
    _alter(completed_recording, tmp_path / completed_recording.name, "terminal_winner")
    altered = run_validity_gate(tmp_path)
    assert not altered.passed
    integrity = next(
        check
        for check in altered.checks
        if check.name == "byte_identical_reconstruction"
    )
    assert not integrity.passed
    assert integrity.facts["drifted_samples"] == 1
    assert "headless-seed-1" in str(integrity.violations)


@pytest.mark.parametrize("abort", [False, True])
def test_live_report_validates_before_folding_a_completed_or_aborted_game(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    abort: bool,
) -> None:
    original_run = HeadlessGame.run

    def corrupted_run(game: HeadlessGame) -> HeadlessGameResult:
        replay_path = game.replay_path
        assert replay_path is not None
        try:
            result = original_run(game)
        except RuntimeError:
            assert abort
            rows = _rows(replay_path)
            rows[0]["tick"] = 9999
            _write(replay_path, rows)
            raise
        assert not abort
        rows = _rows(replay_path)
        rows[-1]["winner"] = "IMPOSTORS"
        _write(replay_path, rows)
        return result

    monkeypatch.setattr(HeadlessGame, "run", corrupted_run)
    with pytest.raises(ReplayIntegrityError):
        run_tournament_eval(
            seeds=(1,),
            output_dir=tmp_path,
            num_players=7,
            num_impostors=1,
            tasks_per_crewmate=1,
            max_ticks=200,
            meeting_runner_factory=(
                _ParseFailureMeetingRunner
                if abort
                else lambda: build_default_meeting_runner(llm_client=FakeProvider())
            ),
        )
    if abort:
        assert compute_cost_usd(tmp_path / "replay-seed-1.jsonl") == pytest.approx(0.02)
