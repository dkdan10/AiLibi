"""Summary measurements compare actual results and refuse changing evidence."""

from __future__ import annotations

from pathlib import Path

import pytest

import measure_public_results as measurement
from measure_replay_loading import _ObservedLoader
from api.public_results import build_public_results
from api.schemas import PublicResultsView
from tests.api.fixtures.sample_replay import write_meeting_replay


@pytest.fixture
def sample(tmp_path: Path) -> Path:
    directory = tmp_path / "small"
    directory.mkdir()
    write_meeting_replay(directory / "replay-seed-0.jsonl")
    # An observation sidecar must never become the selected replay input.
    (directory / "replay-seed-0.audit.jsonl").write_text("audit bytes\n")
    return directory


def test_measurement_compares_equal_responses_and_walks(sample: Path) -> None:
    result = measurement.measure(sample, 1)
    assert len(result.samples) == 4
    assert len({row.response_bytes for row in result.samples}) == 1
    warm = next(
        row for row in result.samples if row.mode == "reuse" and row.request == "warm"
    )
    assert warm.walks == 0 and warm.games == 1
    assert "summary_instrument" in result.source_hashes


def test_source_drift_refuses_measurement(
    sample: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def alter(loader: _ObservedLoader) -> PublicResultsView:
        result = build_public_results(loader)
        (sample / "MANIFEST.md").write_text("changed provenance\n")
        return result

    monkeypatch.setattr(measurement, "build_public_results", alter)
    with pytest.raises(ValueError, match="changed"):
        measurement.measure(sample, 1)


def test_existing_output_is_preserved(sample: Path, tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    output.write_text("previous result")
    with pytest.raises(SystemExit):
        measurement.main(["--set-dir", str(sample), "--output", str(output)])
    assert output.read_text() == "previous result"


def test_output_cannot_enter_recording_directory(sample: Path) -> None:
    output = sample / "replay-seed-999.jsonl"
    with pytest.raises(SystemExit):
        measurement.main(["--set-dir", str(sample), "--output", str(output)])
    assert not output.exists()
