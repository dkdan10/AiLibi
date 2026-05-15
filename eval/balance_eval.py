"""Headless tournament harness (DESIGN.md §11.3).

Aggregates outcomes across many :class:`HeadlessGame` runs. The harness
reuses the single-game orchestrator from Task 2.8 — it does not implement
its own tick loop. :func:`run_balance_eval` runs one game per seed and
returns a :class:`BalanceReport` whose buckets account for every outcome
:data:`orchestrator.game.Outcome` can produce.

``TICK_BUDGET_REACHED`` and ``MEETING_PHASE_REACHED`` are first-class
fields alongside the decisive ``CREWMATES`` / ``IMPOSTORS`` totals: a
non-decisive outcome must never be silently dropped or coerced into a
decisive bucket. The Phase 2 merge criteria say "both decisive sides win
> 20% of decisive games"; consumers can compute that ratio from
``crew_wins`` / ``impostor_wins`` without touching the non-decisive
buckets.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from engine.world import Map, load_canonical_map
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    AgentFactory,
    HeadlessGame,
    Outcome,
    build_default_agent_factory,
)
from orchestrator.scheduler import TickScheduler


@dataclass(frozen=True)
class BalanceReport:
    """Aggregated outcomes for one tournament run.

    ``games == crew_wins + impostor_wins + tick_budget_reached +
    meeting_phase_reached``. The constructor verifies this invariant so a
    bucket can never be silently dropped.
    """

    games: int
    crew_wins: int
    impostor_wins: int
    tick_budget_reached: int
    meeting_phase_reached: int
    seeds_used: tuple[int, ...]

    def __post_init__(self) -> None:
        bucket_total = (
            self.crew_wins
            + self.impostor_wins
            + self.tick_budget_reached
            + self.meeting_phase_reached
        )
        if bucket_total != self.games:
            raise ValueError(
                "BalanceReport bucket totals must sum to games: "
                f"crew={self.crew_wins} impostors={self.impostor_wins} "
                f"tick_budget={self.tick_budget_reached} "
                f"meeting={self.meeting_phase_reached} != games={self.games}"
            )
        if self.games != len(self.seeds_used):
            raise ValueError(
                f"games={self.games} must equal len(seeds_used)={len(self.seeds_used)}"
            )


def run_balance_eval(
    *,
    seeds: Sequence[int],
    output_dir: Path,
    game_map: Map | None = None,
    agent_factory: AgentFactory | None = None,
    num_players: int = DEFAULT_NUM_PLAYERS,
    num_impostors: int = DEFAULT_NUM_IMPOSTORS,
    max_ticks: int = DEFAULT_MAX_TICKS,
) -> BalanceReport:
    """Run one :class:`HeadlessGame` per seed and aggregate outcomes.

    ``output_dir`` receives one ``replay-seed-{seed}.jsonl`` plus its
    matching audit log per seed (see
    :class:`orchestrator.replay.ReplayLog` and
    :class:`observation.audit.ObservationAuditLog`). Seeds must be unique
    so per-seed replay paths do not clobber each other. ``game_map`` and
    ``agent_factory`` default to :func:`engine.world.load_canonical_map`
    and :func:`orchestrator.game.build_default_agent_factory` so the
    common case is a one-line call.
    """

    if not seeds:
        raise ValueError("seeds must be non-empty")
    seeds_tuple = tuple(seeds)
    if len(set(seeds_tuple)) != len(seeds_tuple):
        raise ValueError("seeds must be unique")

    resolved_map = game_map if game_map is not None else load_canonical_map()
    resolved_factory = (
        agent_factory if agent_factory is not None else build_default_agent_factory()
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    counter: Counter[Outcome] = Counter()

    for seed in seeds_tuple:
        replay_path = output_dir / f"replay-seed-{seed}.jsonl"
        game = HeadlessGame(
            seed=seed,
            game_map=resolved_map,
            agent_factory=resolved_factory,
            replay_path=replay_path,
            num_players=num_players,
            num_impostors=num_impostors,
            scheduler=TickScheduler(max_ticks=max_ticks),
        )
        result = game.run()
        counter[result.outcome] += 1

    return BalanceReport(
        games=len(seeds_tuple),
        crew_wins=counter["CREWMATES"],
        impostor_wins=counter["IMPOSTORS"],
        tick_budget_reached=counter["TICK_BUDGET_REACHED"],
        meeting_phase_reached=counter["MEETING_PHASE_REACHED"],
        seeds_used=seeds_tuple,
    )


__all__ = ["BalanceReport", "run_balance_eval"]
