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
    # Task 19.5 wires the Task-17.6 successor here too: the CANARY cell, the
    # only canary-eligible genuine-class instrument from baseline 5 onward.
    # 79 supplied (meeting, impostor) pairs across the three recorded channels,
    # 70 converted -> 0.8861.
    assert report.supplied_channel_supplied == 79
    assert report.supplied_channel_converted == 70
    assert report.supplied_channel_conversion == pytest.approx(70 / 79)
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
    # The Task-19.5 canary cell on this set: 11 supplied, 10 converted -> 0.9091.
    assert report.supplied_channel_supplied == 11
    assert report.supplied_channel_converted == 10
    assert report.supplied_channel_conversion == pytest.approx(10 / 11)
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
    # Task 19.5: the canary line renders for BOTH sets, rate then headline pair.
    assert "supplied-channel conversion (canary): 0.8861  (70/79)" in out
    assert "supplied-channel conversion (canary): 0.9091  (10/11)" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(78 / 101)
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 31
    assert nine["r1_eject_decided_wins"] == 31
    # Task 19.5: the canary trio ships on the JSON surface too (payload[0] is 9p2i).
    assert nine["supplied_channel_supplied"] == 79
    assert "supplied_channel_conversion" in nine


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


# ---------------------------------------------------------------------------
# --solvability: the candidate-set ceiling from the crew's own perception.
# ---------------------------------------------------------------------------


def test_solvability_human_rendering(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--solvability", str(_NINE)]) == 0
    out = capsys.readouterr().out
    assert "50 games, 151 body meetings, 87 ejections at them" in out
    assert "killer in candidate set: 0.8742  (132/151)  95% CI [0.8118, 0.9179]" in out
    assert "one candidate: 0.2715  (41/151)" in out
    assert "... and it is the killer: 0.9024  (37/41)" in out
    assert "at most two candidates: 0.4437  (67/151)" in out
    assert "ejected a player the crew had already cleared: 0.2414  (21/87)" in out
    assert "killer in candidate set, last-kill anchor: 0.9073  (137/151)" in out


def test_solvability_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--solvability", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["body_meetings"] == 151
    assert nine["ejections_at_body_meetings"] == 87
    assert nine["killer_in_set"]["numerator"] == 132
    assert nine["singleton_correct"] == {
        "numerator": 37,
        "denominator": 41,
        "rate": pytest.approx(37 / 41),
        "wilson_low": pytest.approx(0.7745202448096945),
        "wilson_high": pytest.approx(0.9614035402470386),
        "advisory": False,
    }
    # The rare-count flag rides on the small set's cells (numerator 6 of 35).
    assert four["body_meetings"] == 35
    assert four["singleton_sets"]["numerator"] == 6
    assert four["singleton_sets"]["advisory"] is True


def test_solvability_rare_cells_render_their_advisory(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main(["--solvability", str(_FOUR)]) == 0
    out = capsys.readouterr().out
    assert "one candidate: 0.1714  (6/35)" in out
    assert "(rare count — read the interval)" in out


def test_solvability_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--solvability", str(tmp_path / "nope")]) == 2


def test_solvability_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--solvability", str(tmp_path)]) == 2


# ---------------------------------------------------------------------------
# --honesty: the evidence-honesty instrument set (the pre-registration's
# "before", recomputed from committed bytes).
# ---------------------------------------------------------------------------


def test_honesty_human_rendering(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--honesty", str(_NINE)]) == 0
    out = capsys.readouterr().out
    assert "50 games, 165 meetings" in out
    assert "+1 agent clock proved on 4408 discriminating sightings" in out
    assert "I-2 false crew self-placement: 0.2102  (152/723)" in out
    assert "I-3 sole-flag precision (per victim): 0.0952  (2/21)" in out
    assert "I-4 grounded sighting side (+-0): 0.5345  (31/58)" in out
    assert "I-5 fabricated completion lines: 0.0415  (19/458)" in out
    assert "I-6 adjacent-room STRONG share: 0.6552  (38/58)" in out
    assert "I-7 movement-origin flags: 0.0921  (7/76)" in out
    assert "I-8 marker contamination (turns): 0.0546  (53/971)" in out
    assert "I-9 singular-persona prompts: 1.0  (1956/1956)" in out
    assert "I-10 meetings with a venting participant: 0.097  (16/165)" in out
    assert "I-11 free zero-witness kills declined: 0.4578  (190/415)" in out
    assert "ghost-top decisions: 0.1231  (303/2461)" in out
    assert "0 mismatches over 2461 decisions" in out
    assert "render budget: mean rendered lines/snapshot 41.74" in out


def test_honesty_one_impostor_set_reports_not_applicable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main(["--honesty", str(_FOUR)]) == 0
    out = capsys.readouterr().out
    # A zero here would read as "clean"; with one impostor the singular persona
    # is simply true, so the cell says so instead.
    assert "I-9 singular-persona prompts: NOT-APPLICABLE" in out
    assert "(234/234)" in out
    assert "(rare count — read the interval)" in out


def test_honesty_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--honesty", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["games_total"] == 50
    assert nine["clock_alignment_checked"] == 4408
    assert nine["false_whereabouts"]["crew_false"]["numerator"] == 152
    assert nine["marker_contamination"]["prompts_with_marker"] == {
        "numerator": 246,
        "denominator": 1956,
        "rate": pytest.approx(246 / 1956),
        "wilson_low": pytest.approx(0.11180156109543679),
        "wilson_high": pytest.approx(0.14119929366751957),
        "advisory": False,
    }
    assert nine["impostor_targeting"]["reconstruction_mismatches"] == 0
    assert four["singular_persona"]["applicable"] is False
    assert four["meeting_physicality"]["meetings"] == 39


def test_honesty_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path / "nope")]) == 2


def test_honesty_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path)]) == 2
