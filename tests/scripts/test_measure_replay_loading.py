"""The offline reader measurement rejects bad requests and unstable sources."""

from __future__ import annotations

import asyncio
import argparse
from collections.abc import Sequence
from pathlib import Path

import httpx
import pytest

import measure_replay_loading as measurement
from tests.api.fixtures.sample_replay import write_meeting_replay


@pytest.fixture
def sample(tmp_path: Path) -> tuple[Path, measurement.Selection]:
    directory = tmp_path / "samples" / "small"
    directory.mkdir(parents=True)
    write_meeting_replay(directory / "replay-seed-0.jsonl")
    return directory.parent, measurement.Selection(set_name="small", seed=0)


def test_fresh_worker_measures_actual_lean_api_and_static_bytes(
    sample: tuple[Path, measurement.Selection],
) -> None:
    parent, selection = sample
    report = asyncio.run(measurement.measure(parent, (selection,), 1, 2))
    row = report.samples[0]
    assert row.selection == selection
    assert len(report.source_hashes[selection.key]) == 64
    assert row.payload_bytes["http_requested_lean"] < row.payload_bytes["http_full"]
    assert row.payload_bytes["http_full"] == row.payload_bytes["serialized_full"]
    assert (
        report.static_payload_bytes[selection.key]
        == row.payload_bytes["http_requested_lean"]
    )
    assert all(value >= 0 for value in row.timings_ms.values())
    assert row.peak_rss_bytes["replay"] >= row.peak_rss_bytes["imports"] > 0
    assert sum(walk.visibility for walk in row.sequential_walks) == 1
    assert sum(walk.memory for walk in row.sequential_walks) == 1
    for key, batch in row.concurrent.items():
        assert len(batch.requests) == 2
        if key.endswith("warm"):
            assert not batch.walks
        else:
            assert 1 <= len(batch.walks) <= 2


def test_changed_source_rejects_a_comparison(
    sample: tuple[Path, measurement.Selection], monkeypatch: pytest.MonkeyPatch
) -> None:
    parent, selection = sample
    original = measurement._static_payload_bytes

    def mutate(
        directory: Path, selections: Sequence[measurement.Selection]
    ) -> dict[str, int]:
        result = original(directory, selections)
        path = directory / selection.set_name / "replay-seed-0.jsonl"
        path.write_bytes(path.read_bytes() + b"\n")
        return result

    monkeypatch.setattr(measurement, "_static_payload_bytes", mutate)
    with pytest.raises(ValueError, match="source changed"):
        asyncio.run(measurement.measure(parent, (selection,), 1, 1))


def test_http_error_cannot_be_reported_as_a_fast_small_response() -> None:
    async def probe() -> None:
        transport = httpx.MockTransport(lambda request: httpx.Response(404))
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            await measurement._request(client, "/missing")

    with pytest.raises(httpx.HTTPStatusError):
        asyncio.run(probe())


def test_existing_output_is_never_replaced(tmp_path: Path) -> None:
    output = tmp_path / "record.json"
    output.write_text("retained")
    with pytest.raises(SystemExit):
        measurement.main(
            ["--output", str(output), "--samples-dir", str(tmp_path / "missing")]
        )
    assert output.read_text() == "retained"


@pytest.mark.parametrize("value", ["../small:0", "small:-1", "small:NaN", "small:0:1"])
def test_invalid_selection_is_rejected(value: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError):
        measurement._selection(value)
