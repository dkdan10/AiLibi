"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline-6 numbers EXACTLY from the committed bytes (any mismatch
is a task failure, not a number to retrofit) and covers the CLI surface: default
two-set run, explicit dir, ``--json``, and the usage-error path. Re-pinned for the
Task 18.12 baseline-6 re-record (model Qwen/Qwen3.6-27B held, the CREW-ONLY
meeting-layer graduation slate).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import measure_baseline

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def test_9p2i_reproduces_baseline_6_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 34/50 (rose from 25/50 on baseline 5 -- the
    # graduated meeting layer decides more games on the eject leg).
    assert report.r1_eject_decided_wins == 34
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {
        "CREWMATE_EJECT": 34,
        "IMPOSTOR_PARITY": 15,
        "CREWMATE_TASKS": 1,
    }
    # Ejection accuracy 0.80 = 80 impostor / 20 crew of 100 ejections (was 64/6 of
    # 70 = 0.9143 on baseline 5: the graduated flags surface more ejections, 20 of
    # them on crew -- the precision cost of the meeting-layer graduation).
    assert report.total_ejections == 100
    assert report.impostor_ejections == 80
    assert report.crewmate_ejections == 20
    assert report.ejection_accuracy == pytest.approx(0.8)
    # Genuine impostor-subject flag class now has supply on baseline 6 (was 0/0 on
    # baseline 5): 8 supplied, 4 converted -> 0.5.
    assert report.genuine_class_supplied == 8
    assert report.genuine_class_converted == 4
    assert report.genuine_class_conversion == pytest.approx(0.5)
    # Impostor win 0.30 (was 0.36); win split CREW 35 / IMP 15.
    assert report.crew_wins == 35
    assert report.impostor_wins == 15
    assert report.impostor_win_rate == pytest.approx(0.3)
    # Meeting rate 1.00 / 156 resolved (was 179).
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 156


def test_4p1i_reproduces_baseline_6_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 0.8462 = 11 impostor / 2 crew of 13 (was 10/0 of 10 = 1.0).
    assert report.total_ejections == 13
    assert report.impostor_ejections == 11
    assert report.crewmate_ejections == 2
    assert report.ejection_accuracy == pytest.approx(11 / 13)
    # Genuine impostor-subject flag class now has one instance on baseline 6 (was
    # 0/0): 1 supplied, 1 converted -> 1.0.
    assert report.genuine_class_supplied == 1
    assert report.genuine_class_converted == 1
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
    assert "80 impostor / 20 crew of 100 ejections" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(0.8)
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 34
    assert nine["r1_eject_decided_wins"] == 34


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(11 / 13)


def test_report_json_round_trips() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    text = report.model_dump_json()
    back = measure_baseline.BaselineMeasurementReport.model_validate_json(text)
    assert back == report


def test_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path / "nope")]) == 2


def test_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path)]) == 2
