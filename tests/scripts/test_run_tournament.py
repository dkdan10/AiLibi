"""Unit tests for scripts/run_tournament.py roster + tasks-per-crewmate wiring.

Drives ``main()`` (bare-module import via ``tests/scripts/conftest.py``) on a
tiny seed range and a low tick budget so the fake-provider run is fast, and
asserts the roster config threaded into ``run_tournament_eval``: the locked
default of 2 tasks/crewmate, a named ``--roster-preset``, explicit roster flags,
and the fail-loud conflict when a preset is combined with explicit flags.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest

import run_tournament as rt
from eval.balance_eval import run_tournament_eval as _real_run_tournament_eval
from eval.report_schema import TournamentReport
from orchestrator.replay import (
    TacticalPolicyStamp,
    fsm_default_tactical_policy_stamp,
    read_tactical_policy_stamp,
)


def test_force_rerun_preserves_fresh_replay_and_audit_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    args = ["--num-games", "2", "--output-dir", str(tmp_path), "--max-ticks", "2"]
    assert rt.main(args) == 0
    paths = [
        tmp_path / f"replay-seed-{seed}{suffix}.jsonl"
        for seed in range(2)
        for suffix in ("", ".audit")
    ]
    original = {path: path.read_bytes() for path in paths}
    with pytest.raises(FileExistsError):
        rt.main(args)
    assert {path: path.read_bytes() for path in paths} == original
    assert rt.main([*args, "--force"]) == 0
    assert {path: path.read_bytes() for path in paths} == original


def _install_capturing_spy(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, int]
) -> None:
    """Patch ``run_tournament.run_tournament_eval`` to record the threaded config.

    The spy records the roster knobs ``main`` passes through, then delegates to
    the real harness (imported directly, same function object ``main`` calls) so
    ``main`` still produces a valid report end-to-end.
    """

    def spy(
        *,
        seeds: Sequence[int],
        output_dir: Path,
        num_players: int,
        num_impostors: int,
        tasks_per_crewmate: int,
        max_ticks: int,
        force: bool,
        tactical_policy_stamp: TacticalPolicyStamp | None = None,
    ) -> TournamentReport:
        captured["num_players"] = num_players
        captured["num_impostors"] = num_impostors
        captured["tasks_per_crewmate"] = tasks_per_crewmate
        return _real_run_tournament_eval(
            seeds=seeds,
            output_dir=output_dir,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            max_ticks=max_ticks,
            force=force,
            tactical_policy_stamp=tactical_policy_stamp,
        )

    monkeypatch.setattr(rt, "run_tournament_eval", spy)


def test_main_defaults_to_four_one_two(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No roster flags: 4 players / 1 impostor / locked default of 2 tasks."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        ["--num-games", "1", "--output-dir", str(tmp_path), "--max-ticks", "2"]
    )

    assert rc == 0
    assert captured == {"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 2}


def test_main_roster_preset_supplies_all_three_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--roster-preset 9p2i`` threads 9 players / 2 impostors / 2 tasks."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--roster-preset",
            "9p2i",
            "--max-ticks",
            "2",
        ]
    )

    assert rc == 0
    assert captured == {"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}


def test_main_roster_preset_4p1i_pins_committed_baseline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--roster-preset 4p1i`` pins 1 task/crewmate (the committed baseline)."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--roster-preset",
            "4p1i",
            "--max-ticks",
            "2",
        ]
    )

    assert rc == 0
    assert captured == {"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1}


def test_main_explicit_flags_thread_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Explicit roster flags stay usable for ad-hoc configs."""

    captured: dict[str, int] = {}
    _install_capturing_spy(monkeypatch, captured)

    rc = rt.main(
        [
            "--num-games",
            "1",
            "--output-dir",
            str(tmp_path),
            "--num-players",
            "5",
            "--num-impostors",
            "2",
            "--tasks-per-crewmate",
            "1",
            "--max-ticks",
            "2",
        ]
    )

    assert rc == 0
    assert captured == {"num_players": 5, "num_impostors": 2, "tasks_per_crewmate": 1}


def test_main_rejects_preset_combined_with_explicit_roster_flag(
    tmp_path: Path,
) -> None:
    """A preset is mutually exclusive with explicit roster flags (fail loud)."""

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--roster-preset",
                "9p2i",
                "--num-players",
                "5",
            ]
        )


def test_main_rejects_preset_combined_with_tasks_flag(tmp_path: Path) -> None:
    """The conflict also fires for --tasks-per-crewmate, not just player count."""

    with pytest.raises(SystemExit, match="mutually exclusive"):
        rt.main(
            [
                "--num-games",
                "1",
                "--output-dir",
                str(tmp_path),
                "--roster-preset",
                "4p1i",
                "--tasks-per-crewmate",
                "3",
            ]
        )


# -- tactical-policy stamp flag (Task 15.9) -----------------------------------


def test_resolve_tactical_policy_stamp_none_is_absent() -> None:
    assert rt._resolve_tactical_policy_stamp(None) is None


def test_resolve_tactical_policy_stamp_fsm_default_literal() -> None:
    assert (
        rt._resolve_tactical_policy_stamp("fsm-default")
        == fsm_default_tactical_policy_stamp()
    )


def test_resolve_tactical_policy_stamp_json_file(tmp_path: Path) -> None:
    stamp = TacticalPolicyStamp(
        policy_id="wave2-champion-7",
        method="neuroevolution",
        encoder_version="encoder.v3",
        weights_sha256="a" * 64,
        anchor_policy="fsm-default",
    )
    path = tmp_path / "champion.json"
    path.write_text(stamp.model_dump_json(), encoding="utf-8")
    assert rt._resolve_tactical_policy_stamp(str(path)) == stamp


def test_resolve_tactical_policy_stamp_missing_file_is_fail_loud(
    tmp_path: Path,
) -> None:
    with pytest.raises(SystemExit, match="cannot read stamp file"):
        rt._resolve_tactical_policy_stamp(str(tmp_path / "nope.json"))


def test_resolve_tactical_policy_stamp_malformed_json_is_fail_loud(
    tmp_path: Path,
) -> None:
    # A JSON file missing required fields must fail loud, never silently record an
    # FSM default (AGENTS.md "no silent fallbacks").
    path = tmp_path / "bad.json"
    path.write_text('{"policy_id": "x"}', encoding="utf-8")
    with pytest.raises(SystemExit, match="not a valid TacticalPolicyStamp"):
        rt._resolve_tactical_policy_stamp(str(path))


def test_main_stamps_replay_on_disk_via_cli(tmp_path: Path) -> None:
    # The production seam the Task-15.12 corpus wrapper drives: a real end-to-end
    # CLI run with --tactical-policy-stamp fsm-default lands the stamp ON DISK.
    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "200",
            "--tactical-policy-stamp",
            "fsm-default",
        ]
    )
    assert rc == 0
    stamp = read_tactical_policy_stamp(tmp_path / "replay-seed-0.jsonl")
    assert stamp == fsm_default_tactical_policy_stamp()


def test_main_without_stamp_records_absent_via_cli(tmp_path: Path) -> None:
    # Omitting the flag records the absent = FSM default (no stamp on disk),
    # byte-identical to today's path.
    rc = rt.main(
        [
            "--num-games",
            "1",
            "--start-seed",
            "0",
            "--output-dir",
            str(tmp_path),
            "--max-ticks",
            "200",
        ]
    )
    assert rc == 0
    assert read_tactical_policy_stamp(tmp_path / "replay-seed-0.jsonl") is None
