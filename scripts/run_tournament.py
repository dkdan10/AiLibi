"""CLI: headless tournament harness (DESIGN.md §11.3).

Runs many headless games and emits a single typed
:class:`~eval.meeting_quality.TournamentEvalReport` as JSON — the
:class:`~eval.report_schema.TournamentReport` plus all four Phase 5 metrics
(vote correctness, accusation calibration, alibi-fabrication rate, cost
dashboard). The single-game loop comes from
:class:`orchestrator.game.HeadlessGame` (Task 2.8); this script only wires CLI
flags, builds the seed range, calls
:func:`eval.balance_eval.run_tournament_eval` +
:func:`eval.meeting_quality.build_tournament_eval_report`, writes the JSON, and
prints a short summary.

The JSON report supersedes the old ``BalanceReport`` text summary as the
tournament artifact (Task 5.6 / Task 5.1 ``## Decisions``); the crew / impostor
/ tick-budget buckets remain derivable from it and are still printed for the
operator.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `uv run python scripts/run_tournament.py ...` to find top-level packages.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from eval.balance_eval import run_tournament_eval  # noqa: E402
from eval.meeting_quality import (  # noqa: E402
    TournamentEvalReport,
    build_tournament_eval_report,
)
from orchestrator.game import (  # noqa: E402
    DEFAULT_MAX_TICKS,
    DEFAULT_NUM_IMPOSTORS,
    DEFAULT_NUM_PLAYERS,
    DEFAULT_TASKS_PER_CREWMATE,
    ROSTER_PRESETS,
)

_DEFAULT_REPORT_FILENAME = "tournament-eval-report.json"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a headless AiLibi tournament and emit a JSON eval report.",
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
        "--report-output",
        type=Path,
        default=None,
        help=(
            "path for the JSON TournamentEvalReport "
            f"(default: <output-dir>/{_DEFAULT_REPORT_FILENAME})"
        ),
    )
    # The roster flags default to None (not their constants) so main() can tell
    # an explicitly-passed value from an omitted one and reject combining any of
    # them with --roster-preset. Omitted flags resolve to the shared defaults in
    # _resolve_roster.
    parser.add_argument(
        "--num-players",
        type=int,
        default=None,
        help=f"total players per game (default: {DEFAULT_NUM_PLAYERS})",
    )
    parser.add_argument(
        "--num-impostors",
        type=int,
        default=None,
        help=f"impostors per game (default: {DEFAULT_NUM_IMPOSTORS})",
    )
    parser.add_argument(
        "--tasks-per-crewmate",
        type=int,
        default=None,
        help=(
            "distinct map tasks assigned to each crewmate "
            f"(default: {DEFAULT_TASKS_PER_CREWMATE}). Raising this lengthens "
            "games so bodies can outlive the win condition (Phase 7 W0.1)."
        ),
    )
    parser.add_argument(
        "--roster-preset",
        choices=sorted(ROSTER_PRESETS),
        default=None,
        help=(
            "named roster config supplying num-players, num-impostors, and "
            "tasks-per-crewmate together; mutually exclusive with passing any of "
            "those flags explicitly. Choices: " + ", ".join(sorted(ROSTER_PRESETS))
        ),
    )
    parser.add_argument(
        "--max-ticks",
        type=int,
        default=DEFAULT_MAX_TICKS,
        help=f"per-game tick budget (default: {DEFAULT_MAX_TICKS})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "overwrite existing per-seed replay files in --output-dir. "
            "Without it, re-using an --output-dir whose replay files already "
            "exist raises ReplayLog.AlreadyExistsError and exits non-zero, "
            "guarding against the silent doubled-file corruption that broke "
            "replay reads in Phase 4 (DESIGN.md §11.4)."
        ),
    )
    return parser.parse_args(argv)


def _format_summary(eval_report: TournamentEvalReport) -> str:
    """Human-readable balance + meeting-rate + cost summary from the eval report.

    The crew / impostor / tick-budget buckets reduce out of
    ``GameReport.winner`` (``winner is None`` is the non-decisive tick-budget
    bucket); the meeting numbers come from the Phase 7 W0.3
    :class:`~eval.meeting_quality.MeetingRateReport` (``meeting_rate`` is
    rendered as a percentage and guards the ``None``/no-games case the way
    ``decisive_split`` guards the no-decisive-games case); the cost numbers come
    from the bundled cost dashboard.
    """

    report = eval_report.report
    games = len(report.games)
    crew_wins = sum(1 for game in report.games if game.winner == "CREWMATES")
    impostor_wins = sum(1 for game in report.games if game.winner == "IMPOSTORS")
    tick_budget_reached = sum(1 for game in report.games if game.winner is None)
    meeting = eval_report.meeting_rate
    dashboard = eval_report.cost_dashboard

    lines = [
        f"games:                {games}",
        f"crew_wins:            {crew_wins}",
        f"impostor_wins:        {impostor_wins}",
        f"tick_budget_reached:  {tick_budget_reached}",
    ]
    decisive = crew_wins + impostor_wins
    if decisive > 0:
        lines.append(
            "decisive_split:       "
            f"CREWMATES={crew_wins / decisive:.2%} "
            f"IMPOSTORS={impostor_wins / decisive:.2%} of {decisive} decisive"
        )
    else:
        lines.append("decisive_split:       (no decisive games)")
    lines.append(f"meetings_total:       {meeting.meetings_total}")
    if meeting.meeting_rate is not None:
        lines.append(
            "meeting_rate:         "
            f"{meeting.meeting_rate:.2%} "
            f"({meeting.games_with_meeting}/{meeting.games_total} games)"
        )
    else:
        lines.append("meeting_rate:         (no games)")
    lines.append(
        "meeting_triggers:     "
        f"body={meeting.body_report_meetings} "
        f"emergency={meeting.emergency_meetings}"
    )
    lines.append(f"total_cost_usd:       {dashboard.total_cost_usd:.4f}")
    lines.append(f"mean_cost_per_game:   {dashboard.mean_cost_per_game:.4f}")
    return "\n".join(lines)


def _resolve_roster(args: argparse.Namespace) -> tuple[int, int, int]:
    """Resolve ``(num_players, num_impostors, tasks_per_crewmate)`` from CLI args.

    A ``--roster-preset`` supplies all three values at once and is mutually
    exclusive with passing ``--num-players`` / ``--num-impostors`` /
    ``--tasks-per-crewmate`` explicitly — combining them raises ``SystemExit``
    rather than silently letting one win (AGENTS.md "no silent fallbacks"). When
    no preset is given, each omitted roster flag falls back to its shared default
    constant, so an unflagged run uses the 4p/1i roster at the locked default of
    2 tasks/crewmate (``DEFAULT_TASKS_PER_CREWMATE``).
    """

    explicit = [
        flag
        for flag, value in (
            ("--num-players", args.num_players),
            ("--num-impostors", args.num_impostors),
            ("--tasks-per-crewmate", args.tasks_per_crewmate),
        )
        if value is not None
    ]
    if args.roster_preset is not None:
        if explicit:
            raise SystemExit(
                f"--roster-preset {args.roster_preset!r} is mutually exclusive "
                f"with explicit roster flags ({', '.join(explicit)}); pass a "
                "named preset or explicit roster flags, not both"
            )
        preset = ROSTER_PRESETS[args.roster_preset]
        return preset.num_players, preset.num_impostors, preset.tasks_per_crewmate

    num_players = (
        args.num_players if args.num_players is not None else DEFAULT_NUM_PLAYERS
    )
    num_impostors = (
        args.num_impostors if args.num_impostors is not None else DEFAULT_NUM_IMPOSTORS
    )
    tasks_per_crewmate = (
        args.tasks_per_crewmate
        if args.tasks_per_crewmate is not None
        else DEFAULT_TASKS_PER_CREWMATE
    )
    return num_players, num_impostors, tasks_per_crewmate


def _emit_report_json(eval_report: TournamentEvalReport, report_output: Path) -> None:
    """Serialize the eval report to JSON, validating the round-trip first.

    A report that cannot be read back is not a report: ``model_validate_json``
    re-parses the dumped JSON and raises on any drift before it is persisted
    (the DoD's ``model_validate_json(model_dump_json(...))`` gate).
    """

    json_text = eval_report.model_dump_json(indent=2)
    TournamentEvalReport.model_validate_json(json_text)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.write_text(json_text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.num_games < 1:
        raise SystemExit(f"--num-games must be at least 1, got {args.num_games}")
    num_players, num_impostors, tasks_per_crewmate = _resolve_roster(args)
    seeds = range(args.start_seed, args.start_seed + args.num_games)
    # ``force`` is threaded into each per-seed ReplayLog construction inside
    # run_tournament_eval, so a conflicting replay-seed-{seed}.jsonl is truncated
    # immediately before that game writes it. A crash partway through a re-run
    # therefore never deletes a later seed's replay that was never reached;
    # without --force, the first existing file raises and exits non-zero
    # (DESIGN.md §11.4; Task 4.16).
    report = run_tournament_eval(
        seeds=seeds,
        output_dir=args.output_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
        max_ticks=args.max_ticks,
        force=args.force,
    )
    eval_report = build_tournament_eval_report(report)

    report_output: Path = (
        args.report_output
        if args.report_output is not None
        else args.output_dir / _DEFAULT_REPORT_FILENAME
    )
    _emit_report_json(eval_report, report_output)

    print(_format_summary(eval_report))
    print(f"report:               {report_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
