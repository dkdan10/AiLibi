"""Headless throughput benchmark (DESIGN.md §9 Phase 5 perf target).

Times a batch of fake-provider :class:`~orchestrator.game.HeadlessGame` runs
and reports games/min. The measurement is deterministic and network-free: it
pins :class:`llm.fake_provider.FakeProvider` (instant LLM stubs) regardless of
``AILIBI_LLM_PROVIDER``, so the cost it measures is ENGINE + serialization
throughput per tick — NOT LLM latency (Task 5.9).

This lives in ``eval/`` as a reusable harness (rather than inline in the test)
so the same code backs both the skipped-by-default
``tests/eval/test_performance.py`` record and ad-hoc manual measurement from a
REPL. It deliberately exposes a plain function returning a typed
:class:`BenchmarkResult`; the caller decides whether to print the rate, assert
a floor, or just smoke-check it is positive.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from engine.world import Map, load_canonical_map
from llm.budget import GameBudget
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    AgentFactory,
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler


@dataclass(frozen=True)
class BenchmarkResult:
    """Outcome of one throughput benchmark batch.

    ``elapsed_seconds`` is the wall-clock time (``time.perf_counter``) to run
    ``num_games`` headless games end-to-end. ``games_per_minute`` is the
    derived rate the DESIGN.md §9 ``>= 1 game/min`` target is checked against.
    Both inputs are validated fail-loud (AGENTS.md "no silent fallbacks") so a
    degenerate measurement raises rather than reporting an infinite rate.
    """

    num_games: int
    elapsed_seconds: float

    def __post_init__(self) -> None:
        if self.num_games < 1:
            raise ValueError(f"num_games must be >= 1, got {self.num_games}")
        if self.elapsed_seconds <= 0.0:
            raise ValueError(
                f"elapsed_seconds must be positive, got {self.elapsed_seconds}"
            )

    @property
    def games_per_minute(self) -> float:
        return self.num_games / self.elapsed_seconds * 60.0

    @property
    def seconds_per_game(self) -> float:
        return self.elapsed_seconds / self.num_games


def run_throughput_benchmark(
    *,
    seeds: Sequence[int],
    output_dir: Path,
    game_map: Map | None = None,
    agent_factory: AgentFactory | None = None,
    num_players: int = DEFAULT_NUM_PLAYERS,
    num_impostors: int = DEFAULT_NUM_IMPOSTORS,
    max_ticks: int = DEFAULT_MAX_TICKS,
) -> BenchmarkResult:
    """Run one fake-provider :class:`HeadlessGame` per seed and time the batch.

    Each game is wired exactly as the production tournament path
    (:func:`eval.balance_eval.run_tournament_eval`) — default agent factory, a
    fresh meeting runner plus a fresh :class:`~llm.budget.GameBudget` per game —
    except the LLM client is pinned to :class:`~llm.fake_provider.FakeProvider`
    so the batch is deterministic and never touches the network. The cost
    measured is therefore the per-tick engine + serialization work (state hash,
    replay/audit writes, observation packets), which is what Task 5.9 targets.

    The map and agent factory are built once and shared across seeds so the
    timed window is per-game work, not fixture setup. ``force=True`` is passed
    to every per-seed :class:`~orchestrator.replay.ReplayLog`, so re-running
    over the same ``output_dir`` overwrites rather than tripping the Task 4.16
    already-exists guard (benchmark I/O is throwaway; callers should pass a
    temporary directory).

    Returns a :class:`BenchmarkResult`. The caller decides how to report or
    assert on the rate; the committed test only smoke-checks that it is finite
    and positive (see ``tests/eval/test_performance.py``), with the real
    ``>= 1 game/min`` DESIGN.md §9 target verified manually and documented.
    """

    seeds_tuple = tuple(seeds)
    if not seeds_tuple:
        raise ValueError("seeds must be non-empty")
    if len(set(seeds_tuple)) != len(seeds_tuple):
        raise ValueError("seeds must be unique")

    resolved_map = game_map if game_map is not None else load_canonical_map()
    resolved_factory = (
        agent_factory if agent_factory is not None else build_default_agent_factory()
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    def run_one(seed: int) -> None:
        game = HeadlessGame(
            seed=seed,
            game_map=resolved_map,
            agent_factory=resolved_factory,
            replay_path=output_dir / f"replay-seed-{seed}.jsonl",
            num_players=num_players,
            num_impostors=num_impostors,
            scheduler=TickScheduler(max_ticks=max_ticks),
            meeting_runner=build_default_meeting_runner(
                llm_client=FakeProvider(),
                budget=GameBudget(max_cost_usd=1.00),
            ),
            force=True,
        )
        game.run()

    start = time.perf_counter()
    for seed in seeds_tuple:
        run_one(seed)
    elapsed = time.perf_counter() - start
    return BenchmarkResult(num_games=len(seeds_tuple), elapsed_seconds=elapsed)


__all__ = ["BenchmarkResult", "run_throughput_benchmark"]
