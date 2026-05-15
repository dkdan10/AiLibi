"""CLI: headless tournament harness (DESIGN.md §11.3).

Aggregates many headless games into a single balance report. The single-
game loop comes from :class:`orchestrator.game.HeadlessGame` (Task 2.8);
this script only wires CLI flags, builds the seed range, calls
:func:`eval.balance_eval.run_balance_eval`, and prints the report.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `uv run python scripts/run_tournament.py ...` to find top-level packages.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from eval.balance_eval import BalanceReport, run_balance_eval  # noqa: E402
from orchestrator.game import (  # noqa: E402
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a headless AiLibi tournament and report balance.",
    )
    parser.add_argument(
        "--num-games",
        type=int,
        default=100,
        help="number of games to run (default: 100)",
    )
    parser.add_argument(
        "--start-seed",
        type=int,
        default=0,
        help="first seed in the tournament; seeds are start..start+num_games-1",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="directory for per-seed replay and audit logs",
    )
    parser.add_argument(
        "--num-players",
        type=int,
        default=DEFAULT_NUM_PLAYERS,
        help=f"total players per game (default: {DEFAULT_NUM_PLAYERS})",
    )
    parser.add_argument(
        "--num-impostors",
        type=int,
        default=DEFAULT_NUM_IMPOSTORS,
        help=f"impostors per game (default: {DEFAULT_NUM_IMPOSTORS})",
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=DEFAULT_MAX_TICKS,
        help=f"per-game tick budget (default: {DEFAULT_MAX_TICKS})",
    )
    return parser.parse_args(argv)


def _format_report(report: BalanceReport) -> str:
    lines = [
        f"games:                {report.games}",
        f"crew_wins:            {report.crew_wins}",
        f"impostor_wins:        {report.impostor_wins}",
        f"tick_budget_reached:  {report.tick_budget_reached}",
        f"meeting_phase_reached:{report.meeting_phase_reached}",
    ]
    decisive = report.crew_wins + report.impostor_wins
    if decisive > 0:
        crew_ratio = report.crew_wins / decisive
        impostor_ratio = report.impostor_wins / decisive
        lines.append(
            f"decisive_split:       "
            f"CREWMATES={crew_ratio:.2%} IMPOSTORS={impostor_ratio:.2%} "
            f"of {decisive} decisive"
        )
    else:
        lines.append("decisive_split:       (no decisive games)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.num_games < 1:
        raise SystemExit(f"--num-games must be at least 1, got {args.num_games}")
    seeds = range(args.start_seed, args.start_seed + args.num_games)
    report = run_balance_eval(
        seeds=seeds,
        output_dir=args.output_dir,
        num_players=args.num_players,
        num_impostors=args.num_impostors,
        max_ticks=args.max_ticks,
    )
    print(_format_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
