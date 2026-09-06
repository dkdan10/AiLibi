"""Planted measurement failures and source-binding checks for the scorecard."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import eval.reasoning_evidence as scorecard
from agents.memory.store import render_for_prompt

ROOT = Path(__file__).resolve().parents[2]


def test_scorecard_records_denominators_and_separates_fixed_outcomes() -> None:
    result = scorecard.run_scorecard(ROOT)
    assert result["passed"] == result["eligible"] > 0
    assert result["model_quality_measured"] is False
    corpus = result["historical_diagnostics"]
    assert corpus["files"] == 300
    assert corpus["proof_meetings"] + corpus["no_proof_meetings"] == corpus["meetings"]
    assert corpus["raw_flags"] > corpus["independent_flags"]
    assert corpus["fixed_ejections"] + corpus["fixed_skips"] == corpus["meetings"]
    assert len(result["inputs"]) == corpus["files"]
    assert result["candidate_decision_quality"]["wrongful_ejections"]["rate"] is None
    for stratum in corpus["fixed_outcomes_by_proof"].values():
        assert stratum["meetings"] == (
            stratum["correct_ejections"]
            + stratum["wrongful_ejections"]
            + stratum["skips"]
        )
    assert result["sources"]["meetings/manager.py"]
    assert {row["population"] for row in result["cases"]} == {
        "development",
        "held_out_engineering",
    }


def test_invented_rendered_citation_fails_the_semantic_scorecard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = render_for_prompt

    def corrupt(*args: Any, **kwargs: Any) -> str:
        return original(*args, **kwargs) + " [obs invented]"

    monkeypatch.setattr(scorecard, "render_for_prompt", corrupt)
    result = scorecard.run_scorecard(ROOT)
    failures = [row["case"] for row in result["cases"] if not row["passed"]]
    assert all(f"memory-citations-{budget}" in failures for budget in (300, 600, 1500))


def test_mid_measurement_source_change_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    snapshots = iter(({"source": "before"}, {"source": "after"}))
    monkeypatch.setattr(scorecard, "_source_hashes", lambda _: next(snapshots))
    with pytest.raises(ValueError, match="implementation changed"):
        scorecard.run_scorecard(ROOT)


def test_unbound_checkout_is_refused(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="one checkout"):
        scorecard.run_scorecard(tmp_path)


def _copy_recording(tmp_path: Path) -> tuple[Path, ...]:
    import shutil

    directory = tmp_path / "replays" / "samples" / "9p2i"
    directory.mkdir(parents=True)
    original = ROOT / "replays" / "samples" / "9p2i"
    path = directory / "replay-seed-0.jsonl"
    shutil.copyfile(original / path.name, path)
    shutil.copyfile(original / "roster.json", directory / "roster.json")
    return (path,)


@pytest.mark.parametrize("mutation", ("winner", "chronology", "roster"))
def test_altered_recording_cannot_publish_fixed_outcome_counts(
    tmp_path: Path,
    mutation: str,
) -> None:
    import json

    files = _copy_recording(tmp_path)
    path = files[0]
    if mutation == "roster":
        roster = path.parent / "roster.json"
        data = json.loads(roster.read_text())
        data["tasks_per_crewmate"] += 1
        roster.write_text(json.dumps(data))
    else:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if mutation == "winner":
            terminal = next(row for row in rows if row["kind"] == "game_over")
            terminal["winner"] = (
                "CREWMATES" if terminal["winner"] == "IMPOSTORS" else "IMPOSTORS"
            )
        else:
            ticks = [index for index, row in enumerate(rows) if row["kind"] == "tick"]
            rows[ticks[0]], rows[ticks[1]] = rows[ticks[1]], rows[ticks[0]]
        path.write_text("".join(json.dumps(row) + "\n" for row in rows))
    snapshot = scorecard._input_snapshot(tmp_path, files)
    with pytest.raises(ValueError):
        scorecard._measure_historical_inputs(tmp_path, files, snapshot)


def test_recording_changed_after_validation_is_refused(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from orchestrator.replay import read_all_entries

    files = _copy_recording(tmp_path)
    snapshot = scorecard._input_snapshot(tmp_path, files)

    def mutate(path: Path) -> Any:
        entries = read_all_entries(path)
        path.write_bytes(path.read_bytes() + b"\n")
        return entries

    monkeypatch.setattr(scorecard, "read_all_entries", mutate)
    with pytest.raises(ValueError, match="inputs changed"):
        scorecard._measure_historical_inputs(tmp_path, files, snapshot)


def test_missing_roster_or_incomplete_population_is_not_defaulted(
    tmp_path: Path,
) -> None:
    files = _copy_recording(tmp_path)
    with pytest.raises(ValueError, match="inventory"):
        scorecard._fixed_recording_inventory(tmp_path)
    (files[0].parent / "roster.json").unlink()
    with pytest.raises(ValueError, match="explicit roster"):
        scorecard._input_snapshot(tmp_path, files)
