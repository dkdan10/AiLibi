"""CLI: single headless game (DESIGN.md §1.4, §3.1).

Run a single deterministic headless game from a seed and write the
replay log. The default agent factory wires the Phase 2 tactical
policies, so this script exercises the full agent loop end-to-end.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `uv run python scripts/run_game.py ...` to find top-level packages.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from engine.world import load_canonical_map  # noqa: E402
from orchestrator.game import (  # noqa: E402
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    HeadlessGame,
    build_default_agent_factory,
)
from orchestrator.scheduler import TickScheduler  # noqa: E402


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a single headless AiLibi game from a seed.",
    )
    parser.add_argument("--seed", type=int, default=0, help="game seed (default: 0)")
    parser.add_argument(
        "--replay-path",
        type=Path,
        required=True,
        help="output path for the JSONL replay log",
    )
    parser.add_argument(
        "--audit-log-path",
        type=Path,
        default=None,
        help="output path for the observation audit log (default: alongside replay)",
    )
    parser.add_argument(
        "--num-players",
        type=int,
        default=DEFAULT_NUM_PLAYERS,
        help=f"total players including impostors (default: {DEFAULT_NUM_PLAYERS})",
    )
    parser.add_argument(
        "--num-impostors",
        type=int,
        default=DEFAULT_NUM_IMPOSTORS,
        help=f"number of impostors (default: {DEFAULT_NUM_IMPOSTORS})",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=DEFAULT_MAX_TICKS,
        help=f"tick budget before TICK_BUDGET_REACHED (default: {DEFAULT_MAX_TICKS})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    game_map = load_canonical_map()
    game = HeadlessGame(
        seed=args.seed,
        game_map=game_map,
        agent_factory=build_default_agent_factory(),
        replay_path=args.replay_path,
        audit_log_path=args.audit_log_path,
        num_players=args.num_players,
        num_impostors=args.num_impostors,
        scheduler=TickScheduler(max_ticks=args.max_ticks),
    )
    result = game.run()
    print(f"outcome: {result.outcome}")
    print(f"final_tick: {result.final_state.tick}")
    print(f"replay_path: {result.replay_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
