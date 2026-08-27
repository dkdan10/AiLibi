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
from eval.evidence_honesty import (
    LIVE_POLICY_FOLD,
    RATIFIED_BASELINE,
    RATIFIED_I11_CELLS,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def test_9p2i_reproduces_baseline_6_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 31/50 (the vent-widening re-record shifts three
    # eject-leg wins into the tasks leg vs the pre-widening baseline-6 34/50).
    assert report.r1_eject_decided_wins == 38  # was 31
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {"CREWMATE_EJECT": 38, "IMPOSTOR_PARITY": 12}
    # Ejection accuracy 0.7723 = 78 impostor / 23 crew of 101 ejections (was 80/20
    # of 100 = 0.80 pre-widening: the widened vent trajectories surface three more
    # crew ejections -- the precision cost of the corrected substrate).
    assert report.total_ejections == 99
    assert report.impostor_ejections == 85
    assert report.crewmate_ejections == 14
    assert report.ejection_accuracy == pytest.approx(85 / 99)  # was 78 / 101
    # The genuine impostor-subject flag class is EMPTY on the recorded census:
    # exactly one recorded alibi_vs_sighting flag survives the three frozen
    # weak-reason exclusions on this set, and it names a crewmate. So the rate
    # is the None sentinel, not 0.0.
    assert report.genuine_class_supplied == 0  # was 1
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None  # was 0.0
    # Task 19.5 wires the Task-17.6 successor here too: the CANARY cell, the
    # only canary-eligible genuine-class instrument from baseline 5 onward.
    # 76 supplied (meeting, impostor) pairs across the three recorded channels,
    # 69 converted -> 0.9079 (baseline 6: 70/79 -> 0.8861).
    assert report.supplied_channel_supplied == 76
    assert report.supplied_channel_converted == 69
    assert report.supplied_channel_conversion == pytest.approx(69 / 76)
    # Impostor win 0.24; win split CREW 38 / IMP 12 (baseline 6: 35 / 15, 0.30).
    assert report.crew_wins == 38
    assert report.impostor_wins == 12
    assert report.impostor_win_rate == pytest.approx(0.24)
    # Meeting rate 1.00 / 152 resolved (baseline 6: 165).
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 152


def test_4p1i_reproduces_baseline_6_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 0.8333 = 10 impostor / 2 crew of 12 (was 11/2 of 13 =
    # 0.8462 pre-widening: the widening drops one impostor ejection).
    assert report.total_ejections == 21  # was 12
    assert report.impostor_ejections == 20  # was 10
    assert report.crewmate_ejections == 1  # was 2
    assert report.ejection_accuracy == pytest.approx(20 / 21)  # was 10 / 12
    # The genuine impostor-subject flag class is EMPTY on this set (baseline 6
    # read 1 supplied / 1 converted), so its rate is the None sentinel.
    assert report.genuine_class_supplied == 0
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None
    # The Task-19.5 canary cell on this set: 19 supplied, 19 converted -> 1.0
    # (baseline 6: 11 supplied / 10 converted -> 0.9091).
    assert report.supplied_channel_supplied == 19
    assert report.supplied_channel_converted == 19
    assert report.supplied_channel_conversion == pytest.approx(1.0)
    # Meeting rate 0.80 / 40 (baseline 6: 0.78 / 39).
    assert report.meeting_rate == pytest.approx(0.8)
    assert report.resolved_meetings == 40


def test_default_measures_both_canonical_sets(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([]) == 0
    out = capsys.readouterr().out
    assert "9p2i" in out
    assert "4p1i" in out
    # The load-bearing numbers surface in the human output.
    assert "38/50" in out
    assert "85 impostor / 14 crew of 99 ejections" in out
    # Task 19.5: the canary line renders for BOTH sets, rate then headline pair.
    assert "supplied-channel conversion (canary): 0.9079  (69/76)" in out
    assert "supplied-channel conversion (canary): 1.0  (19/19)" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(85 / 99)  # was 78 / 101
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 38  # was 31
    assert nine["r1_eject_decided_wins"] == 38  # was 31
    # Task 19.5: the canary trio ships on the JSON surface too (payload[0] is 9p2i).
    assert nine["supplied_channel_supplied"] == 76  # was 79
    assert "supplied_channel_conversion" in nine


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(20 / 21)  # was 10 / 12


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
    assert "50 games, 144 body meetings, 91 ejections at them" in out
    assert "killer in candidate set: 0.875  (126/144)  95% CI [0.8111, 0.9194]" in out
    assert "one candidate: 0.1389  (20/144)" in out
    assert "... and it is the killer: 0.7  (14/20)" in out
    assert "at most two candidates: 0.3194  (46/144)" in out
    assert "ejected a player the crew had already cleared: 0.2088  (19/91)" in out
    assert "killer in candidate set, last-kill anchor: 0.9375  (135/144)" in out


def test_solvability_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--solvability", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["body_meetings"] == 144  # was 151
    assert nine["ejections_at_body_meetings"] == 91  # was 87
    assert nine["killer_in_set"]["numerator"] == 126  # was 132
    assert nine["singleton_correct"] == {
        "numerator": 14,
        "denominator": 20,
        "rate": pytest.approx(14 / 20),
        "wilson_low": pytest.approx(0.4810232237710206),
        "wilson_high": pytest.approx(0.854524726031006),
        "advisory": False,
    }
    # The rare-count flag rides on the small set's cells (numerator 5 of 37).
    assert four["body_meetings"] == 37
    assert four["singleton_sets"]["numerator"] == 5
    assert four["singleton_sets"]["advisory"] is True


def test_solvability_rare_cells_render_their_advisory(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main(["--solvability", str(_FOUR)]) == 0
    out = capsys.readouterr().out
    assert "one candidate: 0.1351  (5/37)" in out
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
    assert "50 games, 152 meetings" in out
    assert "+1 agent clock proved on 2845 discriminating sightings" in out
    assert "I-2 false crew self-placement: 0.0046  (3/659)" in out
    assert "I-3 sole-flag precision (per victim): None  (0/0)" in out
    assert "I-4 grounded sighting side (+-0): None  (0/0)" in out
    assert "I-5 fabricated completion lines: 0.0  (0/308)" in out
    assert "I-6 adjacent-room STRONG share: None  (0/0)" in out
    assert "I-7 movement-origin flags: 0.0  (0/27)" in out
    assert "I-8 marker contamination (turns): 0.0  (0/871)" in out
    assert "I-9 singular-persona prompts: 0.0  (0/1746)" in out
    assert "I-10 meetings with a venting participant: 0.1711  (26/152)" in out
    # I-11 is the one block the emitter no longer renders as a reproduction of
    # the recorded policy: since the 20.32 mover repair the fold re-invokes the
    # REPAIRED policy over the frozen bytes, so these are counterfactual cells and
    # the mismatch count is the size of the behaviour change. The ratified
    # "before" is quoted from eval.evidence_honesty.RATIFIED_I11_CELLS.
    assert (
        f"I-11 [{LIVE_POLICY_FOLD}] free zero-witness kills declined: 0.0351  (8/228)"
        in out
    )
    # The label is what separates the two modes on the human surface; the ratified
    # "before" is a different string and must never render as this one.
    assert f"I-11 [{RATIFIED_BASELINE}]" not in out
    assert "ghost-top decisions: 0.0029  (5/1750)" in out
    assert "0 mismatches over 1750 decisions" in out
    assert "render budget: mean rendered lines/snapshot 37.03" in out


def test_honesty_one_impostor_set_reports_not_applicable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main(["--honesty", str(_FOUR)]) == 0
    out = capsys.readouterr().out
    # A zero here would read as "clean"; with one impostor the singular persona
    # is simply true, so the cell says so instead.
    assert "I-9 singular-persona prompts: NOT-APPLICABLE" in out
    assert "(240/240)" in out
    assert "(rare count — read the interval)" in out


def test_honesty_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--honesty", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["games_total"] == 50
    assert nine["clock_alignment_checked"] == 2845  # was 4501
    assert nine["false_whereabouts"]["crew_false"]["numerator"] == 3  # was 152
    # Marker contamination went to ZERO on the recorded prompts: the structured
    # turn markers are typed annotations now, so nothing splices an audit marker
    # into a rendered prompt (baseline 6: 246/1,956).
    contaminated = nine["marker_contamination"]["prompts_with_marker"]
    assert (contaminated["numerator"], contaminated["denominator"]) == (0, 1746)
    assert contaminated["rate"] == pytest.approx(0.0)
    assert contaminated["advisory"] is True
    # The JSON block labels its own mode, so a reader can tell the live fold from
    # the ratified baseline constants without knowing which sha produced it.
    assert nine["impostor_targeting"]["policy_mode"] == LIVE_POLICY_FOLD
    assert RATIFIED_I11_CELLS["samples/9p2i"].policy_mode == RATIFIED_BASELINE
    # ZERO mismatches on the recorded bytes (baseline 6 read 419): the record was
    # made with the 20.32-repaired mover, so the live fold IS the recorded policy
    # and the I-11 cells are a reproduction rather than a counterfactual.
    assert nine["impostor_targeting"]["reconstruction_mismatches"] == 0
    assert nine["impostor_targeting"]["recorded_kill_decisions"] == 220
    assert nine["impostor_targeting"]["recorded_kills_reproduced"] == 220
    assert four["singular_persona"]["applicable"] is False
    assert four["meeting_physicality"]["meetings"] == 40


def test_honesty_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path / "nope")]) == 2


def test_honesty_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path)]) == 2
