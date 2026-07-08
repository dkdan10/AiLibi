"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline-3 numbers EXACTLY from the committed bytes (any mismatch
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


def test_9p2i_reproduces_baseline_3_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 34/50.
    assert report.r1_eject_decided_wins == 34
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {
        "CREWMATE_EJECT": 34,
        "IMPOSTOR_PARITY": 15,
        "CREWMATE_TASKS": 1,
    }
    # Ejection accuracy 0.697 = 76 impostor / 33 crew of 109 ejections.
    assert report.total_ejections == 109
    assert report.impostor_ejections == 76
    assert report.crewmate_ejections == 33
    assert report.ejection_accuracy == pytest.approx(0.6972477064220184)
    # Genuine-class conversion 0.769 (10/13).
    assert report.genuine_class_supplied == 13
    assert report.genuine_class_converted == 10
    assert report.genuine_class_conversion == pytest.approx(0.7692307692307693)
    # Impostor win 0.30; win split CREW 35 / IMP 15.
    assert report.crew_wins == 35
    assert report.impostor_wins == 15
    assert report.impostor_win_rate == pytest.approx(0.30)
    # Meeting rate 1.00 / 139 resolved.
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 139


def test_4p1i_reproduces_baseline_3_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 0.808 (21 impostor / 5 crew of 26).
    assert report.total_ejections == 26
    assert report.impostor_ejections == 21
    assert report.crewmate_ejections == 5
    assert report.ejection_accuracy == pytest.approx(0.8076923076923077)
    # Genuine-class conversion 3/3.
    assert report.genuine_class_supplied == 3
    assert report.genuine_class_converted == 3
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
    assert "34/50" in out
    assert "0.6972" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(0.6972477064220184)
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 34
    assert nine["r1_eject_decided_wins"] == 34


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(0.8076923076923077)


def test_report_json_round_trips() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    text = report.model_dump_json()
    back = measure_baseline.BaselineMeasurementReport.model_validate_json(text)
    assert back == report


def test_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path / "nope")]) == 2


def test_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path)]) == 2
