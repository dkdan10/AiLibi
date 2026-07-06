"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline-2 numbers EXACTLY from the committed bytes (any mismatch
is a task failure, not a number to retrofit) and covers the CLI surface: default
two-set run, explicit dir, ``--json``, and the usage-error path.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import measure_baseline

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def test_9p2i_reproduces_baseline_2_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 24/50.
    assert report.r1_eject_decided_wins == 24
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {
        "CREWMATE_EJECT": 24,
        "IMPOSTOR_PARITY": 20,
        "CREWMATE_TASKS": 6,
    }
    # Ejection accuracy 0.525 = 62 impostor / 56 crew of 118 ejections.
    assert report.total_ejections == 118
    assert report.impostor_ejections == 62
    assert report.crewmate_ejections == 56
    assert report.ejection_accuracy == pytest.approx(0.5254237288135594)
    # Genuine-class conversion 0.625 (10/16).
    assert report.genuine_class_supplied == 16
    assert report.genuine_class_converted == 10
    assert report.genuine_class_conversion == pytest.approx(0.625)
    # Impostor win 0.40; win split CREW 30 / IMP 20.
    assert report.crew_wins == 30
    assert report.impostor_wins == 20
    assert report.impostor_win_rate == pytest.approx(0.40)
    # Meeting rate 1.00 / 142 resolved.
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 142


def test_4p1i_reproduces_baseline_2_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 0.923 (12 impostor / 1 crew of 13).
    assert report.total_ejections == 13
    assert report.impostor_ejections == 12
    assert report.crewmate_ejections == 1
    assert report.ejection_accuracy == pytest.approx(0.9230769230769231)
    # Genuine-class conversion 4/4.
    assert report.genuine_class_supplied == 4
    assert report.genuine_class_converted == 4
    assert report.genuine_class_conversion == pytest.approx(1.0)
    # Meeting rate 0.78 / 39.
    assert report.meeting_rate == pytest.approx(0.78)
    assert report.resolved_meetings == 39


def test_default_measures_both_canonical_sets(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([]) == 0
    out = capsys.readouterr().out
    assert "9p2i" in out
    assert "4p1i" in out
    # The load-bearing numbers surface in the human output.
    assert "24/50" in out
    assert "0.5254" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(0.5254237288135594)
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 24
    assert nine["r1_eject_decided_wins"] == 24


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(0.9230769230769231)


def test_report_json_round_trips() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    text = report.model_dump_json()
    back = measure_baseline.BaselineMeasurementReport.model_validate_json(text)
    assert back == report


def test_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path / "nope")]) == 2


def test_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path)]) == 2
