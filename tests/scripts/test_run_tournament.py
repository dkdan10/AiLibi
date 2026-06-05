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
