"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline numbers EXACTLY from the committed bytes (any mismatch
is a task failure, not a number to retrofit) and covers the CLI surface: default
two-set run, explicit dir, ``--json``, and the usage-error path. Re-pinned for the
Task 21.15 baseline-8 re-record (prompt set ``qwen3_6_27b`` v5, the twenty-one
retired levers plus ``impostor_roll_call`` OFF).
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
from tests._helpers.committed import report_9p2i

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def test_9p2i_reproduces_baseline_8_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 35/50: on the baseline-8 bytes every crew win is
    # eject-decided (the tasks leg is empty on this set), so this equals crew_wins.
    assert report.r1_eject_decided_wins == 35  # was 38
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {  # was CREWMATE_EJECT 38 / IMPOSTOR_PARITY 12
        "CREWMATE_EJECT": 35,
        "IMPOSTOR_PARITY": 15,
    }
    # Ejection accuracy 0.8632 = 82 impostor / 13 crew of 95 ejections.
    assert report.total_ejections == 95  # was 99
    assert report.impostor_ejections == 82  # was 85
    assert report.crewmate_ejections == 13  # was 14
    assert report.ejection_accuracy == pytest.approx(82 / 95)  # was 85 / 99
    # The genuine impostor-subject flag class is EMPTY on the recorded census:
    # exactly one recorded alibi_vs_sighting flag survives the three frozen
    # weak-reason exclusions on this set, and it names a crewmate. So the rate
    # is the None sentinel, not 0.0.
    assert report.genuine_class_supplied == 0  # was 1
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None  # was 0.0
    # Task 19.5 wires the Task-17.6 successor here too: the CANARY cell, the
    # only canary-eligible genuine-class instrument from baseline 5 onward.
    # 75 supplied (meeting, impostor) pairs across the three recorded channels,
    # 69 converted -> 0.92.
    assert report.supplied_channel_supplied == 75  # was 76
    assert report.supplied_channel_converted == 69
    assert report.supplied_channel_conversion == pytest.approx(69 / 75)  # was 69 / 76
    # Impostor win 0.30; win split CREW 35 / IMP 15.
    assert report.crew_wins == 35  # was 38
    assert report.impostor_wins == 15  # was 12
    assert report.impostor_win_rate == pytest.approx(0.30)  # was 0.24
    # Meeting rate 1.00 / 151 resolved.
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 151  # was 152


def test_4p1i_reproduces_baseline_8_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 0.8333 = 20 impostor / 4 crew of 24 ejections.
    assert report.total_ejections == 24  # was 21
    assert report.impostor_ejections == 20
    assert report.crewmate_ejections == 4  # was 1
    assert report.ejection_accuracy == pytest.approx(20 / 24)  # was 20 / 21
    # The genuine impostor-subject flag class is EMPTY on this set (baseline 6
    # read 1 supplied / 1 converted), so its rate is the None sentinel.
    assert report.genuine_class_supplied == 0
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None
    # The Task-19.5 canary cell on this set: 19 supplied, 19 converted -> 1.0.
    assert report.supplied_channel_supplied == 19
    assert report.supplied_channel_converted == 19
    assert report.supplied_channel_conversion == pytest.approx(1.0)
    # Meeting rate 0.78 / 39 resolved.
    assert report.meeting_rate == pytest.approx(0.78)  # was 0.8
    assert report.resolved_meetings == 39  # was 40


def test_historical_win_census_does_not_certify_recorded_outcomes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    source = report_9p2i().report
    historical = source.model_copy(
        update={
            "games": tuple(
                game.model_copy(update={"outcome_verified": False})
                for game in source.games
            )
        }
    )
    monkeypatch.setattr(
        measure_baseline, "assemble_tournament_report", lambda _path: historical
    )

    measured = measure_baseline.measure_baseline(tmp_path)

    assert (measured.crew_wins, measured.impostor_wins) == (35, 15)
    assert measured.impostor_win_rate == pytest.approx(15 / 50)
    assert all(not game.outcome_verified for game in historical.games)


def test_default_measures_both_canonical_sets(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([]) == 0
    out = capsys.readouterr().out
    assert "9p2i" in out
    assert "4p1i" in out
    # The load-bearing numbers surface in the human output.
    assert "35/50" in out  # was 38/50
    assert "82 impostor / 13 crew of 95 ejections" in out  # was 85 / 14 of 99
    # Task 19.5: the canary line renders for BOTH sets, rate then headline pair.
    assert (  # was 0.9079  (69/76)
        "supplied-channel conversion (canary): 0.92  (69/75)" in out
    )
    assert "supplied-channel conversion (canary): 1.0  (19/19)" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(82 / 95)  # was 85 / 99
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 35  # was 38
    assert nine["r1_eject_decided_wins"] == 35  # was 38
    # Task 19.5: the canary trio ships on the JSON surface too (payload[0] is 9p2i).
    assert nine["supplied_channel_supplied"] == 75  # was 76
    assert "supplied_channel_conversion" in nine


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(20 / 24)  # was 20 / 21


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
    # was: 144 body meetings, 91 ejections at them
    assert "50 games, 141 body meetings, 85 ejections at them" in out
    # was 0.875  (126/144)  95% CI [0.8111, 0.9194]
    assert "killer in candidate set: 0.9007  (127/141)  95% CI [0.8402, 0.9399]" in out
    assert "one candidate: 0.1844  (26/141)" in out  # was 0.1389  (20/144)
    assert "... and it is the killer: 0.8077  (21/26)" in out  # was 0.7  (14/20)
    assert "at most two candidates: 0.3688  (52/141)" in out  # was 0.3194  (46/144)
    # was 0.2088  (19/91)
    assert "ejected a player the crew had already cleared: 0.1882  (16/85)" in out
    # was 0.9375  (135/144)
    assert "killer in candidate set, last-kill anchor: 0.9362  (132/141)" in out


def test_solvability_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--solvability", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["body_meetings"] == 141  # was 144
    assert nine["ejections_at_body_meetings"] == 85  # was 91
    assert nine["killer_in_set"]["numerator"] == 127  # was 126
    assert nine["singleton_correct"] == {  # was 14/20, wilson [0.4810…, 0.8545…]
        "numerator": 21,
        "denominator": 26,
        "rate": pytest.approx(21 / 26),
        "wilson_low": pytest.approx(0.6212336384535001),
        "wilson_high": pytest.approx(0.9149306422821174),
        "advisory": False,
    }
    # The rare-count flag rides on the small set's cells (numerator 5 of 36).
    assert four["body_meetings"] == 36  # was 37
    assert four["singleton_sets"]["numerator"] == 5
    assert four["singleton_sets"]["advisory"] is True


def test_solvability_rare_cells_render_their_advisory(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main(["--solvability", str(_FOUR)]) == 0
    out = capsys.readouterr().out
    assert "one candidate: 0.1389  (5/36)" in out  # was 0.1351  (5/37)
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
    assert "50 games, 151 meetings" in out  # was 152 meetings
    # was 2845 discriminating sightings
    assert "+1 agent clock proved on 2984 discriminating sightings" in out
    assert "I-2 false crew self-placement: 0.0091  (6/660)" in out  # was 0.0046 (3/659)
    assert "I-3 sole-flag precision (per victim): 0.0  (0/1)" in out  # was None  (0/0)
    assert "I-4 grounded sighting side (+-0): 1.0  (2/2)" in out  # was None  (0/0)
    assert "I-5 fabricated completion lines: 0.0  (0/311)" in out  # was (0/308)
    assert "I-6 adjacent-room STRONG share: 0.0  (0/2)" in out  # was None  (0/0)
    assert "I-7 movement-origin flags: 0.0  (0/30)" in out  # was (0/27)
    assert "I-8 marker contamination (turns): 0.0  (0/869)" in out  # was (0/871)
    assert "I-9 singular-persona prompts: 0.0  (0/1740)" in out  # was (0/1746)
    # was 0.1711  (26/152)
    assert "I-10 meetings with a venting participant: 0.1788  (27/151)" in out
    # I-11 is the one block the emitter no longer renders as a reproduction of
    # the recorded policy: since the 20.32 mover repair the fold re-invokes the
    # REPAIRED policy over the frozen bytes, so these are counterfactual cells and
    # the mismatch count is the size of the behaviour change. The ratified
    # "before" is quoted from eval.evidence_honesty.RATIFIED_I11_CELLS.
    assert (  # was 0.0351  (8/228)
        f"I-11 [{LIVE_POLICY_FOLD}] free zero-witness kills declined: 0.0338  (8/237)"
        in out
    )
    # The label is what separates the two modes on the human surface; the ratified
    # "before" is a different string and must never render as this one.
    assert f"I-11 [{RATIFIED_BASELINE}]" not in out
    assert "ghost-top decisions: 0.0016  (3/1826)" in out  # was 0.0029  (5/1750)
    assert "0 mismatches over 1826 decisions" in out  # was over 1750 decisions
    assert "render budget: mean rendered lines/snapshot 36.57" in out  # was 37.03


def test_honesty_one_impostor_set_reports_not_applicable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main(["--honesty", str(_FOUR)]) == 0
    out = capsys.readouterr().out
    # A zero here would read as "clean"; with one impostor the singular persona
    # is simply true, so the cell says so instead.
    assert "I-9 singular-persona prompts: NOT-APPLICABLE" in out
    assert "(234/234)" in out  # was (240/240)
    assert "(rare count — read the interval)" in out


def test_honesty_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--honesty", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["games_total"] == 50
    assert nine["clock_alignment_checked"] == 2984  # was 2845
    assert nine["false_whereabouts"]["crew_false"]["numerator"] == 6  # was 3
    # Marker contamination went to ZERO on the recorded prompts: the structured
    # turn markers are typed annotations now, so nothing splices an audit marker
    # into a rendered prompt (baseline 6: 246/1,956).
    contaminated = nine["marker_contamination"]["prompts_with_marker"]
    # was (0, 1746)
    assert (contaminated["numerator"], contaminated["denominator"]) == (0, 1740)
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
    assert nine["impostor_targeting"]["recorded_kill_decisions"] == 229  # was 220
    assert nine["impostor_targeting"]["recorded_kills_reproduced"] == 229  # was 220
    assert four["singular_persona"]["applicable"] is False
    assert four["meeting_physicality"]["meetings"] == 39  # was 40


def test_honesty_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path / "nope")]) == 2


def test_honesty_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path)]) == 2
