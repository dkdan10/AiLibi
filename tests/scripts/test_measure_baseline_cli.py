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
    # R1 eject-decided win share 31/50 (the vent-widening re-record shifts three
    # eject-leg wins into the tasks leg vs the pre-widening baseline-6 34/50).
    assert report.r1_eject_decided_wins == 31
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {
        "CREWMATE_EJECT": 31,
        "IMPOSTOR_PARITY": 15,
        "CREWMATE_TASKS": 4,
    }
    # Ejection accuracy 0.7723 = 78 impostor / 23 crew of 101 ejections (was 80/20
    # of 100 = 0.80 pre-widening: the widened vent trajectories surface three more
    # crew ejections -- the precision cost of the corrected substrate).
    assert report.total_ejections == 101
    assert report.impostor_ejections == 78
    assert report.crewmate_ejections == 23
    assert report.ejection_accuracy == pytest.approx(78 / 101)
    # Genuine impostor-subject flag class supply on baseline 6 (was 8/4 -> 0.5
    # pre-widening): 4 supplied, 3 converted -> 0.75.
    assert report.genuine_class_supplied == 4
    assert report.genuine_class_converted == 3
    assert report.genuine_class_conversion == pytest.approx(0.75)
    # Impostor win 0.30; win split CREW 35 / IMP 15 (unchanged by the widening).
    assert report.crew_wins == 35
    assert report.impostor_wins == 15
    assert report.impostor_win_rate == pytest.approx(0.3)
    # Meeting rate 1.00 / 165 resolved (was 156 pre-widening).
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 165


def test_4p1i_reproduces_baseline_6_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 0.8333 = 10 impostor / 2 crew of 12 (was 11/2 of 13 =
    # 0.8462 pre-widening: the widening drops one impostor ejection).
    assert report.total_ejections == 12
    assert report.impostor_ejections == 10
    assert report.crewmate_ejections == 2
    assert report.ejection_accuracy == pytest.approx(10 / 12)
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
    assert "31/50" in out
    assert "78 impostor / 23 crew of 101 ejections" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(78 / 101)
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 31
    assert nine["r1_eject_decided_wins"] == 31


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(10 / 12)


def test_report_json_round_trips() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    text = report.model_dump_json()
    back = measure_baseline.BaselineMeasurementReport.model_validate_json(text)
    assert back == report


def test_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path / "nope")]) == 2


def test_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main([str(tmp_path)]) == 2
