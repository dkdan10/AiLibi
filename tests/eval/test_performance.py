"""Throughput benchmark record for DESIGN.md §9 (Task 5.9).

The timed benchmark is **skipped by default** and opt-in via
``AILIBI_RUN_PERF_BENCHMARK=1`` — the same mechanism as the real-provider gate
in ``tests/llm/test_client.py`` — so single-laptop hardware variance never
flakes CI on the ``>= 1 game/min`` DESIGN.md §9 target. The committed
assertions are record-only: the rate must be finite and positive, never a
tight threshold. The real target is verified manually and documented in the
PR's ``## Decisions``.

A small non-gated smoke test runs a tiny batch on every CI run so the harness
(``eval/benchmark.py``) cannot silently bitrot, without asserting any rate
floor.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import pytest

from eval.benchmark import BenchmarkResult, run_throughput_benchmark

# Opt-in gate, identical mechanism to the real-provider marker in
# tests/llm/test_client.py: skipped unless AILIBI_RUN_PERF_BENCHMARK == "1",
# so the timed run never executes (and so never flakes) in CI.
perf_benchmark = pytest.mark.skipif(
    os.environ.get("AILIBI_RUN_PERF_BENCHMARK") != "1",
    reason=(
        "performance benchmark skipped by default; set "
        "AILIBI_RUN_PERF_BENCHMARK=1 to record the games/min rate"
    ),
)

# A seed range wide enough to include games that reach a meeting (so the
# meeting path is exercised), per the Task 5.9 implementation hint.
_BENCHMARK_SEEDS = tuple(range(60))


def test_benchmark_result_derives_rate_from_elapsed() -> None:
    """BenchmarkResult math: games/min and s/game derive from the inputs."""

    result = BenchmarkResult(num_games=120, elapsed_seconds=60.0)
    assert result.games_per_minute == pytest.approx(120.0)
    assert result.seconds_per_game == pytest.approx(0.5)


@pytest.mark.parametrize(
    ("num_games", "elapsed"),
    [(0, 1.0), (-1, 1.0), (1, 0.0), (1, -1.0)],
)
def test_benchmark_result_rejects_degenerate_inputs(
    num_games: int, elapsed: float
) -> None:
    """A non-positive game count or elapsed time fails loud, not an inf rate."""

    with pytest.raises(ValueError):
        BenchmarkResult(num_games=num_games, elapsed_seconds=elapsed)


def test_perf_benchmark_marker_is_opt_in_skipif() -> None:
    """The benchmark gate is a skipif keyed on AILIBI_RUN_PERF_BENCHMARK.

    Pins that the timed run stays opt-in so CI never asserts a hardware-
    sensitive rate threshold (Task 5.9 DoD: record-only, never a tight CI
    floor).
    """

    assert perf_benchmark.mark.name == "skipif"
    expected_condition = os.environ.get("AILIBI_RUN_PERF_BENCHMARK") != "1"
    assert perf_benchmark.mark.args[0] is expected_condition


def test_throughput_benchmark_smoke(tmp_path: Path) -> None:
    """Non-gated guard: the harness runs and reports a finite positive rate.

    Runs a tiny batch (cheap enough for CI) so ``eval/benchmark.py`` cannot
    silently break. Asserts only that the rate is finite and positive — never
    a floor — so it never flakes on hardware variance (Task 5.9 DoD).
    """

    result = run_throughput_benchmark(seeds=range(3), output_dir=tmp_path)

    assert result.num_games == 3
    assert result.elapsed_seconds > 0.0
    assert math.isfinite(result.games_per_minute)
    assert result.games_per_minute > 0.0
    assert result.seconds_per_game > 0.0


@perf_benchmark
def test_records_phase5_throughput(tmp_path: Path) -> None:
    """Record games/min on the target hardware (opt-in; record-only).

    Skipped unless ``AILIBI_RUN_PERF_BENCHMARK=1``. When run, it times a
    representative fake-provider batch and prints the rate; the assertion is
    record-only (finite + positive), with the DESIGN.md §9 ``>= 1 game/min``
    target verified manually and recorded in the PR — never a tight CI
    threshold, because single-laptop variance makes that flaky (Task 5.9 DoD).
    """

    result = run_throughput_benchmark(seeds=_BENCHMARK_SEEDS, output_dir=tmp_path)

    print(
        f"\n[perf] {result.num_games} games in {result.elapsed_seconds:.3f}s "
        f"-> {result.games_per_minute:.1f} games/min "
        f"({result.seconds_per_game * 1000:.2f} ms/game)"
    )
    assert math.isfinite(result.games_per_minute)
    assert result.games_per_minute > 0.0
