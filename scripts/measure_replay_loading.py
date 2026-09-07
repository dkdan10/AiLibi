"""Measure offline replay-reader work, payload and memory without timing gates.

Each repetition runs in a fresh interpreter; "cold" refers to application
caches, never an OS page-cache flush. ASGI timings include route dispatch and
serialization, but no network or browser rendering. Peak RSS includes temporary
request/serialization objects, not just retained caches. Gzip sizes are diagnostic
and do not assert that a deployed host enables compression.

Run ``uv run python scripts/measure_replay_loading.py --output /tmp/loading.json``.
The default cases cover a no-meeting game and the median/largest 9p2i recordings.
"""

from __future__ import annotations

import argparse
import asyncio
import gc
import gzip
import hashlib
import json
import os
import platform
import resource
import sys
import tempfile
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TypeVar

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import httpx  # noqa: E402
from pydantic import BaseModel, ConfigDict  # noqa: E402

from api.main import create_app  # noqa: E402
from api.replay_loader import (  # noqa: E402
    ReplayLoader,
    _WalkResult,
    get_replay_loader,
)
from build_demo_bundle import _Writer, _bake_set  # noqa: E402
from orchestrator.replay import substrate_flag_snapshot  # noqa: E402

_T = TypeVar("_T")
_DEFAULT_CASES = ("4p1i:31", "4p1i:29", "9p2i:31", "9p2i:23")


class _Value(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Selection(_Value):
    set_name: str
    seed: int

    @property
    def game_id(self) -> str:
        return f"headless-seed-{self.seed}"

    @property
    def key(self) -> str:
        return f"{self.set_name}:{self.seed}"


class WalkMeasurement(_Value):
    memory: bool
    visibility: bool
    elapsed_ms: float


class RequestMeasurement(_Value):
    elapsed_ms: float
    bytes: int
    gzip_bytes: int


class BatchMeasurement(_Value):
    requests: tuple[RequestMeasurement, ...]
    walks: tuple[WalkMeasurement, ...]


class SampleMeasurement(_Value):
    selection: Selection
    timings_ms: dict[str, float]
    payload_bytes: dict[str, int]
    peak_rss_bytes: dict[str, int]
    sequential_walks: tuple[WalkMeasurement, ...]
    concurrent: dict[str, BatchMeasurement]


class LoadingMeasurement(_Value):
    format_version: int = 1
    measured_at_utc: str
    platform: str
    python: str
    clock: str = "perf_counter; application-cold caches; OS cache unchanged"
    transport: str = "in-process ASGI; no network; gzip is diagnostic only"
    memory: str = (
        "process peak RSS including temporary objects, not retained-cache size"
    )
    repetitions: int
    concurrency: int
    source_hashes: dict[str, str]
    substrate: dict[str, bool]
    static_payload_bytes: dict[str, int]
    samples: tuple[SampleMeasurement, ...]


class _ObservedLoader(ReplayLoader):
    def __init__(self, replay_dir: Path) -> None:
        super().__init__(replay_dir)
        self.walks: list[WalkMeasurement] = []

    def _walk(
        self,
        path: Path,
        seed: int,
        *,
        collect_memory: bool,
        collect_visibility: bool = False,
    ) -> _WalkResult:
        start = time.perf_counter()
        result = super()._walk(
            path,
            seed,
            collect_memory=collect_memory,
            collect_visibility=collect_visibility,
        )
        self.walks.append(
            WalkMeasurement(
                memory=collect_memory,
                visibility=collect_visibility,
                elapsed_ms=(time.perf_counter() - start) * 1000,
            )
        )
        return result


def _timed(work: Callable[[], _T]) -> tuple[_T, float]:
    start = time.perf_counter()
    result = work()
    return result, (time.perf_counter() - start) * 1000


def _peak_rss_bytes() -> int:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(peak if sys.platform == "darwin" else peak * 1024)


async def _request(client: httpx.AsyncClient, path: str) -> RequestMeasurement:
    start = time.perf_counter()
    response = await client.get(path)
    response.raise_for_status()
    elapsed = (time.perf_counter() - start) * 1000
    return RequestMeasurement(
        elapsed_ms=elapsed,
        bytes=len(response.content),
        gzip_bytes=len(gzip.compress(response.content, mtime=0)),
    )


async def probe_sample(
    samples_dir: Path, selection: Selection, concurrency: int
) -> SampleMeasurement:
    """Measure one genuine recording; call in a fresh process for cold RSS."""
    if not 1 <= concurrency <= 8:
        raise ValueError("concurrency must be between 1 and 8")
    loader = _ObservedLoader(samples_dir / selection.set_name)
    rss = {"imports": _peak_rss_bytes()}
    replay, cold = _timed(lambda: loader.load_replay(selection.game_id))
    _, warm = _timed(lambda: loader.load_replay(selection.game_id))
    raw, serialize = _timed(lambda: replay.model_dump_json(by_alias=True).encode())
    rss["replay"] = _peak_rss_bytes()
    frames, beliefs = _timed(lambda: loader.belief_frames(selection.game_id))
    _, beliefs_warm = _timed(lambda: loader.belief_frames(selection.game_id))
    frame_bytes = json.dumps(
        [frame.model_dump(mode="json", by_alias=True) for frame in frames],
        separators=(",", ":"),
    ).encode()
    rss["beliefs"] = _peak_rss_bytes()
    sequential = tuple(loader.walks)
    app = create_app(replay_dir=samples_dir)
    app.dependency_overrides[get_replay_loader] = lambda: loader
    batches: dict[str, BatchMeasurement] = {}
    path = f"/replays/{selection.game_id}"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://measurement"
    ) as client:
        full = await _request(client, path)
        loader.clear_cache()
        lean_cold = await _request(client, f"{path}?include_llm_bodies=false")
        lean_warm = await _request(client, f"{path}?include_llm_bodies=false")
        for label, endpoint in (
            ("replay", f"{path}?include_llm_bodies=false"),
            ("beliefs", f"{path}/beliefs"),
        ):
            loader.clear_cache()
            for temperature in ("cold", "warm"):
                loader.walks.clear()
                requests = await asyncio.gather(
                    *(_request(client, endpoint) for _ in range(concurrency))
                )
                batches[f"{label}_{temperature}"] = BatchMeasurement(
                    requests=tuple(requests), walks=tuple(loader.walks)
                )
    rss["concurrent"] = _peak_rss_bytes()
    loader.clear_cache()
    gc.collect()
    return SampleMeasurement(
        selection=selection,
        timings_ms={
            "load_cold": cold,
            "load_warm": warm,
            "serialize_full": serialize,
            "beliefs_cold": beliefs,
            "beliefs_warm": beliefs_warm,
            "http_warm_full": full.elapsed_ms,
            "http_cold_requested_lean": lean_cold.elapsed_ms,
            "http_warm_requested_lean": lean_warm.elapsed_ms,
        },
        payload_bytes={
            "serialized_full": len(raw),
            "http_full": full.bytes,
            "http_requested_lean": lean_warm.bytes,
            "http_full_gzip": full.gzip_bytes,
            "http_requested_lean_gzip": lean_warm.gzip_bytes,
            "beliefs": len(frame_bytes),
        },
        peak_rss_bytes=rss,
        sequential_walks=sequential,
        concurrent=batches,
    )


def _source_hashes(
    samples_dir: Path, selections: Sequence[Selection]
) -> dict[str, str]:
    """Hash selected recordings, complete input sets and implementation files."""
    paths = {Path(__file__).resolve(), _REPO_ROOT / "scripts/build_demo_bundle.py"}
    for package in (
        "engine",
        "observation",
        "agents",
        "meetings",
        "llm",
        "orchestrator",
        "api",
    ):
        paths.update((_REPO_ROOT / package).rglob("*.py"))
    paths.update((_REPO_ROOT / "engine/maps").glob("*.yaml"))
    hashes: dict[str, str] = {}
    code_digest = hashlib.sha256()
    for path in sorted(paths):
        code_digest.update(str(path.relative_to(_REPO_ROOT)).encode() + b"\0")
        code_digest.update(path.read_bytes() + b"\0")
    hashes["reader_implementation"] = code_digest.hexdigest()
    for selection in selections:
        path = samples_dir / selection.set_name / f"replay-seed-{selection.seed}.jsonl"
        hashes[selection.key] = hashlib.sha256(path.read_bytes()).hexdigest()
    for set_name in sorted({selection.set_name for selection in selections}):
        digest = hashlib.sha256()
        for path in sorted((samples_dir / set_name).iterdir()):
            if path.name in {"roster.json", "MANIFEST.md"} or (
                path.suffix == ".jsonl"
                and path.stem.removeprefix("replay-seed-").isdigit()
            ):
                digest.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
        hashes[f"set:{set_name}"] = digest.hexdigest()
    return hashes


def _static_payload_bytes(
    samples_dir: Path, selections: Sequence[Selection]
) -> dict[str, int]:
    """Measure actual data files produced by the static builder, without npm."""
    with tempfile.TemporaryDirectory(prefix="ailibi-loading-static-") as temporary:
        root = Path(temporary)
        writer = _Writer(root)
        for set_name in sorted({selection.set_name for selection in selections}):
            _bake_set(
                writer,
                set_name=set_name,
                seeds=tuple(s.seed for s in selections if s.set_name == set_name),
                samples_dir=samples_dir,
            )
        return {
            selection.key: (
                root / selection.set_name / "replays" / f"{selection.game_id}.json"
            )
            .stat()
            .st_size
            for selection in selections
        }


async def measure(
    samples_dir: Path,
    selections: Sequence[Selection],
    repetitions: int,
    concurrency: int,
) -> LoadingMeasurement:
    if not 1 <= repetitions <= 10 or not 1 <= concurrency <= 8:
        raise ValueError("repetitions must be 1–10 and concurrency 1–8")
    if not 1 <= len(selections) <= 16 or len({s.key for s in selections}) != len(
        selections
    ):
        raise ValueError("select 1–16 distinct recordings")
    before = _source_hashes(samples_dir, selections)
    static_bytes = _static_payload_bytes(samples_dir, selections)
    samples: list[SampleMeasurement] = []
    env = dict(os.environ)
    env["AILIBI_LLM_PROVIDER"] = "fake"
    for _ in range(repetitions):
        for selection in selections:
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                selection.key,
                "--samples-dir",
                str(samples_dir.resolve()),
                "--concurrency",
                str(concurrency),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise RuntimeError(f"reader measurement failed: {stderr.decode()}")
            samples.append(SampleMeasurement.model_validate_json(stdout))
    if _source_hashes(samples_dir, selections) != before:
        raise ValueError(
            "measurement source changed during the run; retry after source freeze"
        )
    return LoadingMeasurement(
        measured_at_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        platform=platform.platform(),
        python=platform.python_version(),
        repetitions=repetitions,
        concurrency=concurrency,
        source_hashes=before,
        substrate=substrate_flag_snapshot(),
        static_payload_bytes=static_bytes,
        samples=tuple(samples),
    )


def _selection(value: str) -> Selection:
    try:
        set_name, seed = value.split(":")
        if not set_name or any(
            c not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for c in set_name
        ):
            raise ValueError("invalid set name")
        parsed_seed = int(seed)
        if parsed_seed < 0:
            raise ValueError("negative seed")
        return Selection(set_name=set_name, seed=parsed_seed)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "recording must be SET:NONNEGATIVE_SEED"
        ) from exc


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--samples-dir", type=Path, default=_REPO_ROOT / "replays/samples"
    )
    parser.add_argument("--case", action="append", type=_selection)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", type=_selection, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.worker is not None:
        result = asyncio.run(
            probe_sample(args.samples_dir, args.worker, args.concurrency)
        )
        print(result.model_dump_json())
        return 0
    if args.output is not None and (args.output.exists() or args.output.is_symlink()):
        parser.error(f"output already exists: {args.output}")
    selections = args.case or [_selection(value) for value in _DEFAULT_CASES]
    try:
        measured = asyncio.run(
            measure(args.samples_dir, selections, args.repetitions, args.concurrency)
        )
    except (ValueError, OSError, RuntimeError) as exc:
        parser.error(str(exc))
    rendered = measured.model_dump_json(indent=2) + "\n"
    if args.output is None:
        print(rendered, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            stream.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
