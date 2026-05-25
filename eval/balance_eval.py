"""Headless tournament harness (DESIGN.md §11.3).

Aggregates outcomes across many :class:`HeadlessGame` runs. The harness
reuses the single-game orchestrator from Task 2.8 — it does not implement
its own tick loop. :func:`run_balance_eval` runs one game per seed and
returns a :class:`BalanceReport` whose buckets account for every outcome
:data:`orchestrator.game.Outcome` can produce.

``TICK_BUDGET_REACHED`` is a first-class field alongside the decisive
``CREWMATES`` / ``IMPOSTORS`` totals: a non-decisive outcome must never be
silently dropped or coerced into a decisive bucket. The Phase 2 merge
criteria say "both decisive sides win > 20% of decisive games"; consumers
can compute that ratio from ``crew_wins`` / ``impostor_wins`` without
touching the non-decisive buckets.

``MEETING_PHASE_REACHED`` is **not** a bucket here. Task 3.13 made the
meeting runner the production default (every game runs through a
:func:`orchestrator.game.build_default_meeting_runner`), so the public
tournament path always resumes after a meeting and can never end at
``MEETING_PHASE_REACHED``. That outcome is the engine-only opt-out for
Phase 2 byte-identity tests; if a public tournament game ever produces
it, the runner wire-up has regressed and :func:`run_balance_eval` raises
fail-loud rather than silently bucketing it (AGENTS.md "no silent
fallbacks").
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from engine.world import Map, load_canonical_map
from llm.budget import GameBudget
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    AgentFactory,
    HeadlessGame,
    Outcome,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler


@dataclass(frozen=True)
class BalanceReport:
    """Aggregated outcomes for one tournament run.

    ``games == crew_wins + impostor_wins + tick_budget_reached``. The
    constructor verifies this invariant so a bucket can never be silently
    dropped. There is no ``meeting_phase_reached`` bucket: meetings fire
    end-to-end from the public tournament path (Task 3.13), so every game
    is decisive or hits the tick budget.
    """

    games: int
    crew_wins: int
    impostor_wins: int
    tick_budget_reached: int
    seeds_used: tuple[int, ...]

    def __post_init__(self) -> None:
        bucket_total = self.crew_wins + self.impostor_wins + self.tick_budget_reached
        if bucket_total != self.games:
            raise ValueError(
                "BalanceReport bucket totals must sum to games: "
                f"crew={self.crew_wins} impostors={self.impostor_wins} "
                f"tick_budget={self.tick_budget_reached} != games={self.games}"
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

    Each game runs through a fresh meeting runner and a fresh
    :class:`llm.budget.GameBudget` built by
    :func:`orchestrator.game.build_default_meeting_runner` (Task 3.13):
    meetings fire end-to-end via the canonical
    :class:`llm.fake_provider.FakeProvider`, and the ``<= $0.30/game``
    cap is enforced at call time. A new runner + budget is constructed
    per game so the budget resets and the per-game recording state is
    not shared across the tournament.

    Because the runner is always wired, a custom ``agent_factory`` must
    yield agents that satisfy the
    :class:`~orchestrator.game.MeetingAwareAgent` protocol whenever a
    seed can reach a meeting; the default factory
    (:func:`orchestrator.game.build_default_agent_factory`) does. A
    non-MeetingAware factory only stays valid for sweeps whose tick
    budget is too small to trigger any meeting (e.g. the wait-agent
    unit tests). If such a factory is paired with a budget large enough
    to open a meeting, participant construction raises ``TypeError``
    fail-loud rather than silently degrading (AGENTS.md "no silent
    fallbacks").
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
            meeting_runner=build_default_meeting_runner(budget=GameBudget()),
        )
        result = game.run()
        if result.outcome == "MEETING_PHASE_REACHED":
            raise RuntimeError(
                f"seed {seed} ended at MEETING_PHASE_REACHED; the public "
                "tournament path always wires a meeting runner, so this "
                "outcome indicates the Task 3.13 runner wire-up regressed"
            )
        counter[result.outcome] += 1

    return BalanceReport(
        games=len(seeds_tuple),
        crew_wins=counter["CREWMATES"],
        impostor_wins=counter["IMPOSTORS"],
        tick_budget_reached=counter["TICK_BUDGET_REACHED"],
        seeds_used=seeds_tuple,
    )


__all__ = ["BalanceReport", "run_balance_eval"]
