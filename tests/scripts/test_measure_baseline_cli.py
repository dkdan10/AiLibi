"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline-4 numbers EXACTLY from the committed bytes (any mismatch
is a task failure, not a number to retrofit) and covers the CLI surface: default
two-set run, explicit dir, ``--json``, and the usage-error path. Re-pinned for the
Task 16.14 baseline-4 re-record (model Qwen/Qwen3.6-27B, prompt set qwen3_6_27b.v1).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import measure_baseline

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def test_9p2i_reproduces_baseline_4_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 34/50.
    assert report.r1_eject_decided_wins == 34
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {
        "CREWMATE_EJECT": 34,
        "IMPOSTOR_PARITY": 12,
        "CREWMATE_TASKS": 4,
    }
    # Ejection accuracy 0.8652 = 77 impostor / 12 crew of 89 ejections.
    assert report.total_ejections == 89
    assert report.impostor_ejections == 77
    assert report.crewmate_ejections == 12
    assert report.ejection_accuracy == pytest.approx(0.8651685393258427)
    # Genuine-class supply collapsed to zero on the baseline-4 model/set (the
    # genuine impostor-subject flag class has ZERO instances now), so the
    # conversion ratio is 0/0 -> None. Pin the honest new census.
    assert report.genuine_class_supplied == 0
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None
    # Impostor win 0.24; win split CREW 38 / IMP 12.
    assert report.crew_wins == 38
    assert report.impostor_wins == 12
    assert report.impostor_win_rate == pytest.approx(0.24)
    # Meeting rate 1.00 / 160 resolved.
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 160


def test_4p1i_reproduces_baseline_4_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 0.8947 (17 impostor / 2 crew of 19).
    assert report.total_ejections == 19
    assert report.impostor_ejections == 17
    assert report.crewmate_ejections == 2
    assert report.ejection_accuracy == pytest.approx(0.8947368421052632)
    # Genuine-class supply collapsed to zero on baseline-4 (ZERO on both sets),
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
    assert "34/50" in out
    assert "0.8652" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(0.8651685393258427)
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 34
    assert nine["r1_eject_decided_wins"] == 34


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(0.8947368421052632)


def test_report_json_round_trips() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    text = report.model_dump_json()
    back = measure_baseline.BaselineMeasurementReport.model_validate_json(text)
    assert back == report


def test_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path / "nope")]) == 2


def test_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path)]) == 2
