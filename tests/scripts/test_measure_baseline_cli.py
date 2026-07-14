"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline-5 numbers EXACTLY from the committed bytes (any mismatch
is a task failure, not a number to retrofit) and covers the CLI surface: default
two-set run, explicit dir, ``--json``, and the usage-error path. Re-pinned for the
Task 16.17 baseline-5 re-record (model Qwen/Qwen3.6-27B held, prompt set
qwen3_6_27b.v3 + the graduated slate).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import measure_baseline

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def test_9p2i_reproduces_baseline_5_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 25/50.
    assert report.r1_eject_decided_wins == 25
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {
        "CREWMATE_EJECT": 25,
        "IMPOSTOR_PARITY": 18,
        "CREWMATE_TASKS": 7,
    }
    # Ejection accuracy 0.9143 = 64 impostor / 6 crew of 70 ejections.
    assert report.total_ejections == 70
    assert report.impostor_ejections == 64
    assert report.crewmate_ejections == 6
    assert report.ejection_accuracy == pytest.approx(0.9142857142857143)
    # Genuine-class supply stays at zero on the baseline-5 model/set (the
    # genuine impostor-subject flag class has ZERO instances now), so the
    # conversion ratio is 0/0 -> None. Pin the honest new census.
    assert report.genuine_class_supplied == 0
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None
    # Impostor win 0.36; win split CREW 32 / IMP 18.
    assert report.crew_wins == 32
    assert report.impostor_wins == 18
    assert report.impostor_win_rate == pytest.approx(0.36)
    # Meeting rate 1.00 / 179 resolved.
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 179


def test_4p1i_reproduces_baseline_5_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 1.0 (10 impostor / 0 crew of 10).
    assert report.total_ejections == 10
    assert report.impostor_ejections == 10
    assert report.crewmate_ejections == 0
    assert report.ejection_accuracy == pytest.approx(1.0)
    # Genuine-class supply stays at zero on baseline-5 (ZERO on both sets),
    # so the conversion ratio is 0/0 -> None. Pin the honest new census.
    assert report.genuine_class_supplied == 0
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None
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
    assert "25/50" in out
    assert "0.9143" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(0.9142857142857143)
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 25
    assert nine["r1_eject_decided_wins"] == 25


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(1.0)


def test_report_json_round_trips() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    text = report.model_dump_json()
    back = measure_baseline.BaselineMeasurementReport.model_validate_json(text)
    assert back == report


def test_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path / "nope")]) == 2


def test_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path)]) == 2
