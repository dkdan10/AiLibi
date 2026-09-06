"""The offline scorecard must not overwrite its evidence inputs."""

from __future__ import annotations
from pathlib import Path
from typing import Any
import pytest
import measure_reasoning_evidence as command

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "relative",
    (
        "replays/samples/4p1i/replay-seed-0.jsonl",
        "replays/samples/9p2i/roster.json",
        "uv.lock",
        "engine/maps/canonical_1.yaml",
    ),
)
def test_cli_refuses_to_replace_an_input_before_measuring(
    monkeypatch: pytest.MonkeyPatch,
    relative: str,
) -> None:
    source = ROOT / relative
    before = source.read_bytes()

    def forbidden(_: Path) -> dict[str, Any]:
        raise AssertionError("measurement must not start for an invalid destination")

    monkeypatch.setattr(command, "run_scorecard", forbidden)
    with pytest.raises(ValueError, match="overlaps"):
        command.main(["--output", str(source)])
    assert source.read_bytes() == before
