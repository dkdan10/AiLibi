#!/usr/bin/env python3
"""Rebuild a sample set's ``tournament-eval-report.json`` offline from its replays.

``scripts/refresh_samples.sh`` regenerates the replay JSONL + ``MANIFEST.md`` but
NOT the derived eval report. A stale report otherwise survives
``bash scripts/check.sh`` because the determinism gate only verifies replay
``state_hash`` reconstruction, never the report (the CI-invisible failure mode
noted at the Phase 7 Wave 0 close). This script closes that gap.

It re-derives each game's roles from the seed + the set's ``roster.json`` (roles
are firewalled out of the replay JSONL), folds the recorded replays into a
:class:`~eval.meeting_quality.TournamentEvalReport` through the SAME loader
``run_tournament.py`` uses (:func:`eval.balance_eval.load_tournament_report` ->
:func:`eval.meeting_quality.build_tournament_eval_report`, so the offline and
live entry points cannot drift), and writes the report in the SAME format
``run_tournament.py`` emits (``model_dump_json(indent=2)`` + a trailing newline,
guarded by a ``model_validate_json`` round-trip).

It is $0 and deterministic: no live model, and ``load_tournament_report`` does no
engine re-run (it folds recorded outcomes), so it is unaffected by the Wave 0.5
friendly-fire guard that breaks raw replay reconstruction.

Usage::

    python scripts/build_sample_report.py [--sample-dir DIR] [--check]

The default writes the report and prints a one-line summary;
``refresh_samples.sh`` invokes it after every real refresh. ``--check`` rebuilds
in memory and diffs against the committed report, exiting non-zero on drift (the
consistency gate that ``tests/scripts/test_build_sample_report.py`` and CI use).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from api import replay_loader  # noqa: E402
from engine.entities import PlayerId, Role  # noqa: E402
from engine.world import load_canonical_map  # noqa: E402
from eval.balance_eval import load_tournament_report  # noqa: E402
from eval.meeting_quality import (  # noqa: E402
    TournamentEvalReport,
    build_tournament_eval_report,
)
from orchestrator.seeder import seed_initial_state  # noqa: E402

_REPORT_FILENAME = "tournament-eval-report.json"

# The flat 4p/1i MVP baseline is the ONLY committed set without a roster.json
# (api.replay_loader: a directory with no roster.json is the single path that
# defaults). Every other roster ships a roster.json, so this default is reached
# only for that one set; ``test_rebuild_matches_committed_flat_4p1i`` pins
# rebuild == committed for it, which would fail loud if the assumption broke.
_FLAT_DEFAULT_NUM_PLAYERS = 4
_FLAT_DEFAULT_NUM_IMPOSTORS = 1
_FLAT_DEFAULT_TASKS_PER_CREWMATE = 1


def _roster_knobs(sample_dir: Path) -> tuple[int, int, int]:
    """Resolve ``(num_players, num_impostors, tasks_per_crewmate)`` for a set.

    Reuses :func:`api.replay_loader._load_roster_config` (the single, fail-loud
    roster parser) so a malformed ``roster.json`` raises here exactly as it does
    on the replay-load path; ``None`` (no descriptor) is the flat 4p/1i default.
    """

    roster = replay_loader._load_roster_config(sample_dir)
    if roster is None:
        return (
            _FLAT_DEFAULT_NUM_PLAYERS,
            _FLAT_DEFAULT_NUM_IMPOSTORS,
            _FLAT_DEFAULT_TASKS_PER_CREWMATE,
        )
    return (roster.num_players, roster.num_impostors, roster.tasks_per_crewmate)


def _seeds_on_disk(sample_dir: Path) -> list[int]:
    """Seeds with a committed ``replay-seed-{n}.jsonl`` in ``sample_dir``.

    Mirrors the loader's dedup (and the ``_committed_7p2i_seeds`` test helper):
    parse the trailing integer of each glob match and return them sorted and
    de-duplicated, so a zero-padded alias cannot double-count a seed.
    """

    return sorted(
        {
            int(path.stem.rsplit("-", 1)[1])
            for path in sample_dir.glob("replay-seed-*.jsonl")
        }
    )


def _roles_by_seed(
    sample_dir: Path,
    *,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
) -> dict[int, dict[PlayerId, Role]]:
    game_map = load_canonical_map()
    roles: dict[int, dict[PlayerId, Role]] = {}
    for seed in _seeds_on_disk(sample_dir):
        state = seed_initial_state(
            seed=seed,
            game_map=game_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )
        roles[seed] = {pid: player.role for pid, player in state.players.items()}
    return roles


def build_report(sample_dir: Path) -> TournamentEvalReport:
    """Rebuild the eval report for ``sample_dir`` from its committed replays."""

    num_players, num_impostors, tasks_per_crewmate = _roster_knobs(sample_dir)
    roles_by_seed = _roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    if not roles_by_seed:
        raise SystemExit(f"no replay-seed-*.jsonl found under {sample_dir}")
    report = load_tournament_report(sample_dir, roles_by_seed=roles_by_seed)
    return build_tournament_eval_report(report)


def _serialize(report: TournamentEvalReport) -> str:
    """Serialize exactly as ``run_tournament.py``'s ``_emit_report_json`` does.

    ``model_dump_json(indent=2)`` + a trailing newline, round-trip-gated: a report
    that cannot be read back is not a report.
    """

    json_text = report.model_dump_json(indent=2)
    TournamentEvalReport.model_validate_json(json_text)
    return json_text + "\n"


def _summary(report: TournamentEvalReport) -> str:
    games = report.report.games
    crew = sum(1 for game in games if game.winner == "CREWMATES")
    impostor = sum(1 for game in games if game.winner == "IMPOSTORS")
    budget = sum(1 for game in games if game.winner is None)
    meeting = report.meeting_rate
    return (
        f"{len(games)} games | CREW {crew} / IMP {impostor} / budget {budget} | "
        f"meeting_rate {meeting.meeting_rate:.2f} ({meeting.meetings_total} meetings)"
    )


def write_report(sample_dir: Path) -> TournamentEvalReport:
    """Rebuild and write ``sample_dir/tournament-eval-report.json``."""

    report = build_report(sample_dir)
    (sample_dir / _REPORT_FILENAME).write_text(_serialize(report), encoding="utf-8")
    return report


def check_report(sample_dir: Path) -> int:
    """Diff a rebuild against the committed report; 0 if consistent, 1 if not."""

    report_path = sample_dir / _REPORT_FILENAME
    if not report_path.exists():
        print(f"--check: no committed report at {report_path}")
        return 1
    rebuilt = build_report(sample_dir).model_dump(mode="json")
    committed = json.loads(report_path.read_text(encoding="utf-8"))
    if rebuilt != committed:
        print(
            f"--check: {report_path} is STALE — it does not match a rebuild from "
            f"its own replays. Re-run `python scripts/build_sample_report.py "
            f"--sample-dir {sample_dir}` and commit the result."
        )
        return 1
    print(f"--check: {report_path} is consistent with its replays.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild a sample set's tournament-eval-report.json from its replays."
        )
    )
    parser.add_argument(
        "--sample-dir",
        type=Path,
        default=_REPO_ROOT / "replays" / "samples",
        help="Sample set directory (default: replays/samples, the flat 4p/1i set).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Rebuild and diff against the committed report; exit 1 on drift.",
    )
    args = parser.parse_args()
    sample_dir: Path = args.sample_dir

    if args.check:
        return check_report(sample_dir)
    report = write_report(sample_dir)
    print(f"Wrote {sample_dir / _REPORT_FILENAME}: {_summary(report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
