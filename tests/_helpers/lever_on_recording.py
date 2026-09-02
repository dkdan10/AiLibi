"""Record a small LEVER-ON replay set offline, for tests that must read one.

`scripts/counterfactual_phase21.py`'s lever-ON mode reads bytes recorded with the
Wave-2 slate up, and the committed sets are all recorded with it down — so a test
of that mode has to make its own recording. The deterministic fake provider
records byte-identical replays with no network and no spend, which is what makes
that affordable in CI.

The recorder deliberately does NOT touch the environment. The slate is a property
of the shell a recording is made in, and a helper that exported it would let a
test pass while proving nothing about the shell discipline the mode enforces;
instead it CHECKS the ambient slate against the one the caller declares, through
the same comparison every recorder and gate uses.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from engine.world import load_canonical_map
from llm.client import LLMClient
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import substrate_slate_mismatches
from orchestrator.scheduler import TickScheduler


def record_replay_set(
    directory: Path,
    *,
    seeds: Sequence[int],
    expect_levers: Sequence[str],
    llm_client: LLMClient | None = None,
    num_players: int = 4,
    num_impostors: int = 1,
    tasks_per_crewmate: int = 2,
    max_ticks: int = 300,
) -> Path:
    """Record ``seeds`` into ``directory`` and write its roster descriptor.

    ``expect_levers`` names the toggles the CALLER believes its shell carries;
    a shell that disagrees refuses here rather than producing a recording whose
    stamp says something the test did not intend. ``llm_client`` defaults to the
    deterministic fake and exists so a test can script one turn's content — a
    spoken observation the fake never emits, for instance.

    The roster descriptor is written because a reconstruction re-seeds from it:
    without one the flat 4p/1i default applies and every ``state_hash`` check
    fails at tick 0, which is a confusing way to learn the roster was wrong.
    """

    problems = substrate_slate_mismatches(expect_levers)
    if problems:
        raise AssertionError(
            "the ambient lever slate is not the one this recording declares: "
            + "; ".join(problems)
        )
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "roster.json").write_text(
        json.dumps(
            {
                "num_impostors": num_impostors,
                "num_players": num_players,
                "tasks_per_crewmate": tasks_per_crewmate,
            }
        ),
        encoding="utf-8",
    )
    game_map = load_canonical_map()
    for seed in seeds:
        HeadlessGame(
            seed=seed,
            game_map=game_map,
            agent_factory=build_default_agent_factory(),
            replay_path=directory / f"replay-seed-{seed}.jsonl",
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
            scheduler=TickScheduler(max_ticks=max_ticks),
            meeting_runner=build_default_meeting_runner(
                llm_client=llm_client if llm_client is not None else FakeProvider()
            ),
        ).run()
    return directory
