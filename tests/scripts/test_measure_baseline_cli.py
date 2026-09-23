"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline numbers EXACTLY from the committed bytes (any mismatch
is a task failure, not a number to retrofit) and covers the CLI surface: default
two-set run, explicit dir, ``--json``, and the usage-error path. Re-pinned for the
baseline-9 process re-record (prompt set ``qwen3_6_27b`` at v6 for the accusation
round and both reports, v8 for the vote ballot; same seeds as baseline 8).
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


def test_9p2i_reproduces_baseline_9_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 38/50: of the 39 crew wins on the baseline-9
    # bytes, 38 are eject-decided and one is a tasks win.
    assert report.r1_eject_decided_wins == 38  # was 35
    # Reason histogram exact (ordered desc by count).
    assert report.reason_histogram == {  # was CREWMATE_EJECT 35 / IMPOSTOR_PARITY 15
        "CREWMATE_EJECT": 38,
        "IMPOSTOR_PARITY": 11,
        "CREWMATE_TASKS": 1,
    }
    # Ejection accuracy 0.90 = 81 impostor / 9 crew of 90 ejections.
    assert report.total_ejections == 90  # was 95
    assert report.impostor_ejections == 81  # was 82
    assert report.crewmate_ejections == 9  # was 13
    assert report.ejection_accuracy == pytest.approx(81 / 90)  # was 82 / 95
    # The genuine impostor-subject flag class is EMPTY on the recorded census:
    # four recorded alibi_vs_sighting subjects survive the three frozen
    # weak-reason exclusions on this set, and every one is a crewmate. So the
    # rate is the None sentinel, not 0.0.
    assert report.genuine_class_supplied == 0
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None
    # Task 19.5 wires the Task-17.6 successor here too: the CANARY cell, the
    # only canary-eligible genuine-class instrument from baseline 5 onward.
    # 74 supplied (meeting, impostor) pairs across the three recorded channels,
    # 70 converted -> 0.9459.
    assert report.supplied_channel_supplied == 74  # was 75
    assert report.supplied_channel_converted == 70  # was 69
    assert report.supplied_channel_conversion == pytest.approx(70 / 74)  # was 69 / 75
    # Impostor win 0.22; win split CREW 39 / IMP 11.
    assert report.crew_wins == 39  # was 35
    assert report.impostor_wins == 11  # was 15
    assert report.impostor_win_rate == pytest.approx(0.22)  # was 0.30
    # Meeting rate 1.00 / 145 resolved.
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 145  # was 151


def test_4p1i_reproduces_baseline_9_exactly() -> None:
    report = measure_baseline.measure_baseline(_FOUR)
    # Ejection accuracy 1.0 = 20 impostor / 0 crew of 20 ejections.
    assert report.total_ejections == 20  # was 24
    assert report.impostor_ejections == 20
    assert report.crewmate_ejections == 0  # was 4
    assert report.ejection_accuracy == pytest.approx(20 / 20)  # was 20 / 24
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
    assert report.meeting_rate == pytest.approx(0.78)
    assert report.resolved_meetings == 39


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

    assert (measured.crew_wins, measured.impostor_wins) == (39, 11)  # was (35, 15)
    assert measured.impostor_win_rate == pytest.approx(11 / 50)  # was 15 / 50
    assert all(not game.outcome_verified for game in historical.games)


def test_default_measures_both_canonical_sets(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([]) == 0
    out = capsys.readouterr().out
    assert "9p2i" in out
    assert "4p1i" in out
    # The load-bearing numbers surface in the human output.
    assert "38/50" in out  # was 35/50
    assert "81 impostor / 9 crew of 90 ejections" in out  # was 82 / 13 of 95
    # Task 19.5: the canary line renders for BOTH sets, rate then headline pair.
    assert (  # was 0.92  (69/75)
        "supplied-channel conversion (canary): 0.9459  (70/74)" in out
    )
    assert "supplied-channel conversion (canary): 1.0  (19/19)" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(81 / 90)  # was 82 / 95
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 38  # was 35
    assert nine["r1_eject_decided_wins"] == 38  # was 35
    # Task 19.5: the canary trio ships on the JSON surface too (payload[0] is 9p2i).
    assert nine["supplied_channel_supplied"] == 74  # was 75
    assert "supplied_channel_conversion" in nine


def test_explicit_dir_measures_one_set(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main([str(_FOUR), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 1
    assert payload[0]["replay_set_dir"].endswith("4p1i")
    assert payload[0]["ejection_accuracy"] == pytest.approx(20 / 20)  # was 20 / 24


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
    # was: 141 body meetings, 85 ejections at them
    assert "50 games, 135 body meetings, 80 ejections at them" in out
    # was 0.9007  (127/141)  95% CI [0.8402, 0.9399]
    assert "killer in candidate set: 0.8889  (120/135)  95% CI [0.8248, 0.9315]" in out
    assert "one candidate: 0.1556  (21/135)" in out  # was 0.1844  (26/141)
    assert "... and it is the killer: 0.7619  (16/21)" in out  # was 0.8077  (21/26)
    assert "at most two candidates: 0.3407  (46/135)" in out  # was 0.3688  (52/141)
    # was 0.1882  (16/85)
    assert "ejected a player the crew had already cleared: 0.15  (12/80)" in out
    # was 0.9362  (132/141)
    assert "killer in candidate set, last-kill anchor: 0.9556  (129/135)" in out


def test_solvability_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--solvability", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["body_meetings"] == 135  # was 141
    assert nine["ejections_at_body_meetings"] == 80  # was 85
    assert nine["killer_in_set"]["numerator"] == 120  # was 127
    assert nine["singleton_correct"] == {  # was 21/26, wilson [0.6212…, 0.9149…]
        "numerator": 16,
        "denominator": 21,
        "rate": pytest.approx(16 / 21),
        "wilson_low": pytest.approx(0.5490841802765407),
        "wilson_high": pytest.approx(0.8937214361088772),
        "advisory": False,
    }
    # The rare-count flag rides on the small set's cells (numerator 5 of 36).
    assert four["body_meetings"] == 36
    assert four["singleton_sets"]["numerator"] == 5
    assert four["singleton_sets"]["advisory"] is True


def test_solvability_rare_cells_render_their_advisory(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main(["--solvability", str(_FOUR)]) == 0
    out = capsys.readouterr().out
    assert "one candidate: 0.1389  (5/36)" in out
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
    assert "50 games, 145 meetings" in out  # was 151 meetings
    # was 2984 discriminating sightings
    assert "+1 agent clock proved on 2996 discriminating sightings" in out
    assert "I-2 false crew self-placement: 0.0074  (5/679)" in out  # was 0.0091 (6/660)
    assert "I-3 sole-flag precision (per victim): None  (0/0)" in out  # was 0.0  (0/1)
    assert "I-4 grounded sighting side (+-0): None  (0/0)" in out  # was 1.0  (2/2)
    assert "I-5 fabricated completion lines: 0.0  (0/271)" in out  # was (0/311)
    assert "I-6 adjacent-room STRONG share: None  (0/0)" in out  # was 0.0  (0/2)
    assert "I-7 movement-origin flags: 0.0  (0/8)" in out  # was (0/30)
    assert "I-8 marker contamination (turns): 0.0  (0/845)" in out  # was (0/869)
    assert "I-9 singular-persona prompts: 0.0  (0/1694)" in out  # was (0/1740)
    # was 0.1788  (27/151)
    assert "I-10 meetings with a venting participant: 0.2  (29/145)" in out
    # I-11 is the one block the emitter no longer renders as a reproduction of
    # the recorded policy: since the 20.32 mover repair the fold re-invokes the
    # REPAIRED policy over the frozen bytes, so these are counterfactual cells and
    # the mismatch count is the size of the behaviour change. The ratified
    # "before" is quoted from eval.evidence_honesty.RATIFIED_I11_CELLS.
    assert (  # was 0.0338  (8/237)
        f"I-11 [{LIVE_POLICY_FOLD}] free zero-witness kills declined: 0.0388  (9/232)"
        in out
    )
    # The label is what separates the two modes on the human surface; the ratified
    # "before" is a different string and must never render as this one.
    assert f"I-11 [{RATIFIED_BASELINE}]" not in out
    assert "ghost-top decisions: 0.0029  (5/1754)" in out  # was 0.0016  (3/1826)
    assert "0 mismatches over 1754 decisions" in out  # was over 1826 decisions
    assert "render budget: mean rendered lines/snapshot 37.89" in out  # was 36.57


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
    assert nine["clock_alignment_checked"] == 2996  # was 2984
    assert nine["false_whereabouts"]["crew_false"]["numerator"] == 5  # was 6
    # Marker contamination went to ZERO on the recorded prompts: the structured
    # turn markers are typed annotations now, so nothing splices an audit marker
    # into a rendered prompt (baseline 6: 246/1,956).
    contaminated = nine["marker_contamination"]["prompts_with_marker"]
    # was (0, 1740)
    assert (contaminated["numerator"], contaminated["denominator"]) == (0, 1694)
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
    assert nine["impostor_targeting"]["recorded_kill_decisions"] == 223  # was 229
    assert nine["impostor_targeting"]["recorded_kills_reproduced"] == 223  # was 229
    assert four["singular_persona"]["applicable"] is False
    assert four["meeting_physicality"]["meetings"] == 39


def test_honesty_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path / "nope")]) == 2


def test_honesty_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path)]) == 2
