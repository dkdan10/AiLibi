"""Tests for scripts/measure_baseline.py (Task 15.1).

Pins the R-gate baseline numbers EXACTLY from the committed bytes (any mismatch
is a task failure, not a number to retrofit) and covers the CLI surface: default
two-set run, explicit dir, ``--json``, and the usage-error path. The 4p1i pins
read the baseline-9 process re-record (prompt set ``qwen3_6_27b`` at v6 for the
accusation round and both reports, v8 for the vote ballot); the 9p2i pins read the
promoted set, candidate round 2 (its own era since 2026-10-02, the same prompt set
with the era's ballot arms), each ``was`` the baseline-9 reading.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import measure_baseline
from eval.evidence_honesty import (
    LIVE_POLICY_FOLD,
    RECORDED_ARM_POLICY_FOLD,
)
from tests._helpers.committed import report_9p2i

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def test_9p2i_reproduces_the_promoted_set_exactly() -> None:
    report = measure_baseline.measure_baseline(_NINE)
    assert report.games_total == 50
    # R1 eject-decided win share 13/50: of the 26 crew wins on the promoted
    # bytes, 13 are eject-decided and 13 are tasks wins.
    assert report.r1_eject_decided_wins == 13  # was 38
    # Reason histogram exact (ordered desc by count).
    # was CREWMATE_EJECT 38 / IMPOSTOR_PARITY 11 / CREWMATE_TASKS 1
    assert report.reason_histogram == {
        "IMPOSTOR_PARITY": 24,
        "CREWMATE_EJECT": 13,
        "CREWMATE_TASKS": 13,
    }
    # Ejection accuracy 0.6667 = 44 impostor / 22 crew of 66 ejections.
    assert report.total_ejections == 66  # was 90
    assert report.impostor_ejections == 44  # was 81
    assert report.crewmate_ejections == 22  # was 9
    assert report.ejection_accuracy == pytest.approx(44 / 66)  # was 81 / 90
    # The genuine impostor-subject flag class is EMPTY on the recorded census
    # of this set, so the rate is the None sentinel, not 0.0.
    assert report.genuine_class_supplied == 0
    assert report.genuine_class_converted == 0
    assert report.genuine_class_conversion is None
    # Task 19.5 wires the Task-17.6 successor here too: the CANARY cell, the
    # only canary-eligible genuine-class instrument from baseline 5 onward.
    # 25 supplied (meeting, impostor) pairs across the three recorded channels,
    # 24 converted -> 0.96.
    assert report.supplied_channel_supplied == 25  # was 74
    assert report.supplied_channel_converted == 24  # was 70
    assert report.supplied_channel_conversion == pytest.approx(24 / 25)  # was 70 / 74
    # Impostor win 0.48; win split CREW 26 / IMP 24.
    assert report.crew_wins == 26  # was 39
    assert report.impostor_wins == 24  # was 11
    assert report.impostor_win_rate == pytest.approx(0.48)  # was 0.22
    # Meeting rate 1.00 / 117 resolved.
    assert report.meeting_rate == pytest.approx(1.0)
    assert report.resolved_meetings == 117  # was 145


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

    assert (measured.crew_wins, measured.impostor_wins) == (26, 24)  # was (39, 11)
    assert measured.impostor_win_rate == pytest.approx(24 / 50)  # was 11 / 50
    assert all(not game.outcome_verified for game in historical.games)


def test_default_measures_both_canonical_sets(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([]) == 0
    out = capsys.readouterr().out
    assert "9p2i" in out
    assert "4p1i" in out
    # The load-bearing numbers surface in the human output.
    assert "R1 eject-decided win share: 13/50" in out  # was 38/50
    assert "44 impostor / 22 crew of 66 ejections" in out  # was 81 / 9 of 90
    # Task 19.5: the canary line renders for BOTH sets, rate then headline pair.
    assert (  # was 0.9459  (70/74)
        "supplied-channel conversion (canary): 0.96  (24/25)" in out
    )
    assert "supplied-channel conversion (canary): 1.0  (19/19)" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    assert nine["ejection_accuracy"] == pytest.approx(44 / 66)  # was 81 / 90
    assert nine["reason_histogram"]["CREWMATE_EJECT"] == 13  # was 38
    assert nine["r1_eject_decided_wins"] == 13  # was 38
    # Task 19.5: the canary trio ships on the JSON surface too (payload[0] is 9p2i).
    assert nine["supplied_channel_supplied"] == 25  # was 74
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
    # was: 135 body meetings, 80 ejections at them
    assert "50 games, 114 body meetings, 63 ejections at them" in out
    # was 0.8889  (120/135)  95% CI [0.8248, 0.9315]
    assert "killer in candidate set: 1.0  (114/114)  95% CI [0.9674, 1.0]" in out
    assert "one candidate: 0.2018  (23/114)" in out  # was 0.1556  (21/135)
    assert "... and it is the killer: 1.0  (23/23)" in out  # was 0.7619  (16/21)
    assert "at most two candidates: 0.3333  (38/114)" in out  # was 0.3407  (46/135)
    # was 0.15  (12/80)
    assert "ejected a player the crew had already cleared: 0.1746  (11/63)" in out
    # was 0.9556  (129/135)
    assert "killer in candidate set, last-kill anchor: 1.0  (114/114)" in out


def test_solvability_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--solvability", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    assert nine["body_meetings"] == 114  # was 135
    assert nine["ejections_at_body_meetings"] == 63  # was 80
    assert nine["killer_in_set"]["numerator"] == 114  # was 120
    assert nine["singleton_correct"] == {  # was 16/21, wilson [0.5490…, 0.8937…]
        "numerator": 23,
        "denominator": 23,
        "rate": pytest.approx(1.0),
        "wilson_low": pytest.approx(0.8568788745827374),
        "wilson_high": pytest.approx(1.0),
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
    assert "50 games, 117 meetings" in out  # was 145 meetings
    # was 2996 discriminating sightings
    assert "+1 agent clock proved on 7789 discriminating sightings" in out
    assert "I-2 false crew self-placement: 0.0063  (4/632)" in out  # was 0.0074 (5/679)
    assert "I-3 sole-flag precision (per victim): None  (0/0)" in out
    assert "I-4 grounded sighting side (+-0): None  (0/0)" in out
    assert "I-5 fabricated completion lines: 0.0  (0/307)" in out  # was (0/271)
    assert "I-6 adjacent-room STRONG share: None  (0/0)" in out
    assert "I-7 movement-origin flags: 0.0  (0/9)" in out  # was (0/8)
    assert "I-8 marker contamination (turns): 0.0  (0/808)" in out  # was (0/845)
    assert "I-9 singular-persona prompts: 0.0  (0/1502)" in out  # was (0/1694)
    # was 0.2  (29/145)
    assert "I-10 meetings with a venting participant: 0.5641  (66/117)" in out
    # I-11 labels the policy its fold re-decides with. The promoted set was
    # recorded with its era's tactical arms, so the fold re-invokes that recorded
    # arm policy and reproduces every recorded decision; on the baseline-9 bytes
    # it was the live (20.32-repaired) policy.
    assert (  # was [live-policy-fold] 0.0388  (9/232)
        f"I-11 [{RECORDED_ARM_POLICY_FOLD}] free zero-witness kills declined: "
        "0.1852  (55/297)" in out
    )
    # The label is what separates the modes on the human surface; the live fold
    # does not render for this set.
    assert f"I-11 [{LIVE_POLICY_FOLD}]" not in out
    assert "ghost-top decisions: 0.0015  (5/3230)" in out  # was 0.0029  (5/1754)
    assert "0 mismatches over 3230 decisions" in out  # was over 1754 decisions
    assert "render budget: mean rendered lines/snapshot 38.17" in out  # was 37.89


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
    assert nine["clock_alignment_checked"] == 7789  # was 2996
    assert nine["false_whereabouts"]["crew_false"]["numerator"] == 4  # was 5
    # Marker contamination went to ZERO on the recorded prompts: the structured
    # turn markers are typed annotations now, so nothing splices an audit marker
    # into a rendered prompt (baseline 6: 246/1,956).
    contaminated = nine["marker_contamination"]["prompts_with_marker"]
    # was (0, 1694)
    assert (contaminated["numerator"], contaminated["denominator"]) == (0, 1502)
    assert contaminated["rate"] == pytest.approx(0.0)
    assert contaminated["advisory"] is True
    # The JSON block labels its own mode, so a reader can tell which fold it ran
    # without knowing which sha produced it.
    # was LIVE_POLICY_FOLD on the baseline-9 bytes
    assert nine["impostor_targeting"]["policy_mode"] == RECORDED_ARM_POLICY_FOLD
    # ZERO mismatches on the recorded bytes (baseline 6 read 419): the record was
    # made with its era's tactical arms, so the fold re-decides with the recorded
    # arm policy and the I-11 cells are a reproduction rather than a
    # counterfactual.
    assert nine["impostor_targeting"]["reconstruction_mismatches"] == 0
    assert nine["impostor_targeting"]["recorded_kill_decisions"] == 242  # was 223
    assert nine["impostor_targeting"]["recorded_kills_reproduced"] == 242  # was 223
    assert four["singular_persona"]["applicable"] is False
    assert four["meeting_physicality"]["meetings"] == 39


def test_honesty_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path / "nope")]) == 2


def test_honesty_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path)]) == 2
