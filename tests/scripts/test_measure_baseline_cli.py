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
from collections import Counter
from pathlib import Path

import pytest

import measure_baseline
from eval.evidence_honesty import (
    LIVE_POLICY_FOLD,
    RECORDED_ARM_POLICY_FOLD,
    compute_evidence_honesty,
)
from tests._helpers.committed import report_9p2i, solvability_report
from tests._helpers.recorded_counts import recorded_counts

_REPO_ROOT = Path(__file__).resolve().parents[2]
_NINE = _REPO_ROOT / "replays" / "samples" / "9p2i"
_FOUR = _REPO_ROOT / "replays" / "samples" / "4p1i"


def _manifest_winners(set_dir: Path) -> Counter[str]:
    """The winner column of a set's MANIFEST, the record-time surface."""

    winners: Counter[str] = Counter()
    for line in (set_dir / "MANIFEST.md").read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.split("|")]
        if len(cells) > 2 and cells[1].isdigit():
            winners[cells[-2]] += 1
    return winners


def _line(out: str, prefix: str) -> str:
    """The one output line that carries ``prefix``."""

    (found,) = (row for row in out.splitlines() if prefix in row)
    return found


def test_9p2i_reproduces_the_promoted_set_exactly() -> None:
    # The shown set's figures, held to the surfaces that record them rather
    # than transcribed: the MANIFEST's winner column, the recorded rows and the
    # committed report (the baseline-9 bytes read 39 crew / 11 impostor wins,
    # 38 eject-decided, 81 of 90 ejections correct).
    report = measure_baseline.measure_baseline(_NINE)
    rows = recorded_counts(_NINE)
    winners = _manifest_winners(_NINE)
    assert report.games_total == rows.games == sum(winners.values())
    assert (report.crew_wins, report.impostor_wins) == (
        winners["CREWMATES"],
        winners["IMPOSTORS"],
    )
    assert report.impostor_win_rate == pytest.approx(
        report.impostor_wins / report.games_total
    )
    # The reason histogram partitions the games, and R1 reads its eject row.
    assert sum(report.reason_histogram.values()) == report.games_total
    assert report.r1_eject_decided_wins == report.reason_histogram.get(
        "CREWMATE_EJECT", 0
    )
    # Ejection accuracy over every recorded ejection, split by role as the
    # committed report splits it.
    assert report.total_ejections == rows.ejections
    assert report.impostor_ejections == report_9p2i().conversion.impostor_ejections
    assert report.crewmate_ejections == (
        report.total_ejections - report.impostor_ejections
    )
    assert report.ejection_accuracy == pytest.approx(
        report.impostor_ejections / report.total_ejections
    )
    # An empty genuine impostor-subject class reads the None sentinel, not 0.0.
    assert (report.genuine_class_conversion is None) == (
        report.genuine_class_supplied == 0
    )
    # Task 19.5 wires the Task-17.6 successor here too: the CANARY cell, the
    # only canary-eligible genuine-class instrument from baseline 5 onward.
    assert report.supplied_channel_conversion == pytest.approx(
        report.supplied_channel_converted / report.supplied_channel_supplied
    )
    assert report.resolved_meetings <= rows.meetings


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

    winners = _manifest_winners(_NINE)
    assert (measured.crew_wins, measured.impostor_wins) == (
        winners["CREWMATES"],
        winners["IMPOSTORS"],
    )
    assert measured.impostor_win_rate == pytest.approx(
        winners["IMPOSTORS"] / sum(winners.values())
    )
    assert all(not game.outcome_verified for game in historical.games)


def test_default_measures_both_canonical_sets(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert measure_baseline.main([]) == 0
    out = capsys.readouterr().out
    assert "9p2i" in out
    assert "4p1i" in out
    # The load-bearing numbers surface in the human output, read off the
    # shown set's own measurement rather than transcribed.
    nine = measure_baseline.measure_baseline(_NINE)
    assert (
        f"R1 eject-decided win share: {nine.r1_eject_decided_wins}/{nine.games_total}"
        in out
    )
    assert (
        f"{nine.impostor_ejections} impostor / {nine.crewmate_ejections} crew of "
        f"{nine.total_ejections} ejections"
    ) in out
    # Task 19.5: the canary line renders for BOTH sets, rate then headline pair.
    assert (
        f"supplied-channel conversion (canary): {nine.supplied_channel_conversion:.4g}"
        f"  ({nine.supplied_channel_converted}/{nine.supplied_channel_supplied})"
    ) in out
    assert "supplied-channel conversion (canary): 1.0  (19/19)" in out


def test_json_emits_array_of_reports(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 2
    nine = payload[0]
    measured = measure_baseline.measure_baseline(_NINE)
    assert nine["ejection_accuracy"] == pytest.approx(measured.ejection_accuracy)
    assert nine["reason_histogram"] == measured.reason_histogram
    assert nine["r1_eject_decided_wins"] == measured.r1_eject_decided_wins
    # Task 19.5: the canary trio ships on the JSON surface too (payload[0] is 9p2i).
    assert nine["supplied_channel_supplied"] == measured.supplied_channel_supplied
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
    # Every line carries the shown set's own cells, read off the instrument
    # rather than transcribed (the baseline-9 bytes read 135 body meetings).
    solved = solvability_report(_NINE)
    assert (
        f"{solved.games_total} games, {solved.body_meetings} body meetings, "
        f"{solved.ejections_at_body_meetings} ejections at them"
    ) in out
    for prefix, cell in (
        ("killer in candidate set:", solved.killer_in_set),
        ("one candidate:", solved.singleton_sets),
        ("... and it is the killer:", solved.singleton_correct),
        ("at most two candidates:", solved.at_most_two_sets),
        (
            "ejected a player the crew had already cleared:",
            solved.cleared_player_ejections,
        ),
        (
            "killer in candidate set, last-kill anchor:",
            solved.killer_in_set_last_kill_anchor,
        ),
    ):
        assert f"({cell.numerator}/{cell.denominator})" in _line(out, prefix), prefix


def test_solvability_json_emits_array(capsys: pytest.CaptureFixture[str]) -> None:
    assert measure_baseline.main(["--solvability", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert len(payload) == 2
    nine, four = payload
    assert nine["replay_set_dir"].endswith("9p2i")
    # The JSON surface carries the instrument's own cells, whole.
    solved = solvability_report(_NINE)
    assert nine["body_meetings"] == solved.body_meetings
    assert nine["ejections_at_body_meetings"] == solved.ejections_at_body_meetings
    assert nine["killer_in_set"] == solved.killer_in_set.model_dump(mode="json")
    assert nine["singleton_correct"] == solved.singleton_correct.model_dump(mode="json")
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
    # Every cell line carries the shown set's own counts, read off the
    # instrument rather than transcribed (the baseline-9 bytes read 145
    # meetings and 2996 discriminating sightings).
    honesty = compute_evidence_honesty(_NINE)
    meetings = honesty.meeting_physicality.meetings
    assert f"{honesty.games_total} games, {meetings} meetings" in out
    assert (
        f"+1 agent clock proved on {honesty.clock_alignment_checked} discriminating "
        "sightings"
    ) in out
    for prefix, cell in (
        ("I-2 false crew self-placement:", honesty.false_whereabouts.crew_false),
        (
            "I-3 sole-flag precision (per victim):",
            honesty.sole_flag_precision.per_victim_precision,
        ),
        (
            "I-4 grounded sighting side (+-0):",
            honesty.grounded_sighting.grounded_at_tick,
        ),
        (
            "I-5 fabricated completion lines:",
            honesty.fabricated_completions.fabricated,
        ),
        ("I-6 adjacent-room STRONG share:", honesty.adjacent_room_flags.adjacent),
        ("I-7 movement-origin flags:", honesty.movement_origin_flags.spoke_origin),
        (
            "I-8 marker contamination (turns):",
            honesty.marker_contamination.turns_with_marker,
        ),
        (
            "I-9 singular-persona prompts:",
            honesty.singular_persona.prompts_with_singular_persona,
        ),
        (
            "I-10 meetings with a venting participant:",
            honesty.meeting_physicality.venting_participants,
        ),
    ):
        assert f"({cell.numerator}/{cell.denominator})" in _line(out, prefix), prefix
    # I-11 labels the policy its fold re-decides with. The promoted set was
    # recorded with its era's tactical arms, so the fold re-invokes that recorded
    # arm policy and reproduces every recorded decision; on the baseline-9 bytes
    # it was the live (20.32-repaired) policy.
    declined = honesty.impostor_targeting.free_kills_declined
    assert f"({declined.numerator}/{declined.denominator})" in _line(
        out, f"I-11 [{RECORDED_ARM_POLICY_FOLD}] free zero-witness kills declined:"
    )
    # The label is what separates the modes on the human surface; the live fold
    # does not render for this set.
    assert f"I-11 [{LIVE_POLICY_FOLD}]" not in out
    targeting = honesty.impostor_targeting
    ghost = targeting.ghost_top
    assert f"({ghost.numerator}/{ghost.denominator})" in _line(
        out, "ghost-top decisions:"
    )
    assert f"0 mismatches over {targeting.decisions_reconstructed} decisions" in out
    assert (
        "render budget: mean rendered lines/snapshot "
        f"{honesty.render_budget.rendered_lines_mean:.2f}"
    ) in out


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
    rows = recorded_counts(_NINE)
    assert nine["games_total"] == rows.games
    assert nine["clock_alignment_checked"] > 0
    # Marker contamination went to ZERO on the recorded prompts: the structured
    # turn markers are typed annotations now, so nothing splices an audit marker
    # into a rendered prompt (baseline 6: 246/1,956).
    contaminated = nine["marker_contamination"]["prompts_with_marker"]
    assert (contaminated["numerator"], contaminated["denominator"]) == (
        0,
        rows.prompts,
    )
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
    kills = rows.actions.get("kill", 0)
    assert nine["impostor_targeting"]["recorded_kill_decisions"] == kills
    assert nine["impostor_targeting"]["recorded_kills_reproduced"] == kills
    assert four["singular_persona"]["applicable"] is False
    assert four["meeting_physicality"]["meetings"] == 39


def test_honesty_missing_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path / "nope")]) == 2


def test_honesty_empty_dir_is_usage_error(tmp_path: Path) -> None:
    assert measure_baseline.main(["--honesty", str(tmp_path)]) == 2
