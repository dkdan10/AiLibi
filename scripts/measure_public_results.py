"""Measure public-summary cache reuse against the same reader with reuse bypassed."""

from __future__ import annotations

import argparse
import hashlib
import platform
import re
import sys
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from api.public_results import _build_public_results, build_public_results  # noqa: E402
from orchestrator.recording_fingerprint import recording_fingerprint  # noqa: E402
from orchestrator.replay import substrate_flag_snapshot  # noqa: E402
from measure_replay_loading import (  # noqa: E402
    Selection,
    _ObservedLoader,
    _source_hashes,
)


class SummarySample(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    mode: Literal["reuse", "bypass"]
    repetition: int
    request: Literal["cold", "warm"]
    elapsed_ms: float
    walks: int
    games: int
    response_bytes: int


class SummaryMeasurement(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    source_hashes: dict[str, str]
    substrate: dict[str, bool]
    python: str
    platform: str
    measured_at_utc: str
    scope: str = (
        "Sequential in-process summary generation, including serialization. "
        "Application-cold loaders; OS cache unchanged; no HTTP/network, RSS "
        "or concurrent-request claim. Bypass uses the same reader without "
        "whole-summary reuse."
    )
    samples: tuple[SummarySample, ...]


def measure(directory: Path, repetitions: int) -> SummaryMeasurement:
    if not 1 <= repetitions <= 10:
        raise ValueError("repetitions must be between 1 and 10")
    paths = sorted(
        path
        for path in directory.glob("replay-seed-*.jsonl")
        if re.fullmatch(r"replay-seed-\d+\.jsonl", path.name)
    )
    if not paths:
        raise ValueError("no recordings to measure")
    selection = Selection(
        set_name=directory.name,
        seed=int(paths[0].stem.removeprefix("replay-seed-")),
    )
    sources = _source_hashes(directory.parent, (selection,))
    # The shared reader inventory predates this summary-specific instrument.
    sources["summary_instrument"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    substrate = substrate_flag_snapshot()
    expected: str | None = None
    rows = []
    modes: tuple[Literal["reuse", "bypass"], ...] = ("bypass", "reuse")
    requests: tuple[Literal["cold", "warm"], ...] = ("cold", "warm")
    for repetition in range(repetitions):
        for mode in modes:
            loader = _ObservedLoader(directory)
            for request in requests:
                before_walks = len(loader.walks)
                started = time.perf_counter()
                result = (
                    build_public_results(loader)
                    if mode == "reuse"
                    else _build_public_results(loader, recording_fingerprint(directory))
                )
                serialized = result.model_dump_json()
                elapsed = (time.perf_counter() - started) * 1000
                if expected is None:
                    expected = serialized
                if serialized != expected:
                    raise ValueError("summary changed across measurement arms")
                rows.append(
                    SummarySample(
                        mode=mode,
                        repetition=repetition,
                        request=request,
                        elapsed_ms=elapsed,
                        walks=len(loader.walks) - before_walks,
                        games=result.games,
                        response_bytes=len(serialized.encode()),
                    )
                )
    after = _source_hashes(directory.parent, (selection,))
    after["summary_instrument"] = hashlib.sha256(
        Path(__file__).read_bytes()
    ).hexdigest()
    if after != sources or substrate_flag_snapshot() != substrate:
        raise ValueError("measurement inputs or implementation changed")
    return SummaryMeasurement(
        source_hashes=sources,
        substrate=substrate,
        python=platform.python_version(),
        platform=platform.platform(),
        measured_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        samples=tuple(rows),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=3)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists")
    if output.is_relative_to(args.set_dir.resolve()):
        parser.error("output must be outside the input recording directory")
    result = measure(args.set_dir.resolve(), args.repetitions)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        stream.write(result.model_dump_json(indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
