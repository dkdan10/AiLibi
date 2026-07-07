"""The R-gate baseline measurement CLI — core folds over a replay set (Task 15.1).

The R-gate is a MEASUREMENT on a valid baseline (audits/audit-phase-14-close.md
§3, §8), not a gate: it folds a replay set's committed bytes into the numbers the
Phase-14 close reports (ejection accuracy, genuine-class conversion, meeting rate,
win split + reason histogram, accusation calibration). It reproduces baseline 2
EXACTLY from committed bytes and re-runs unchanged on baseline 3 (Task 15.7).

This module owns the CORE-folds region. The Task-15.2 watchability folds and the
Task-15.3 information-funnel folds are LATER, disjoint regions added to this same
file. Everything here WIRES existing tested folds — it never re-implements a
metric that already has a home:

* ejection accuracy / genuine-class conversion — :mod:`eval.vote_correctness`
* meeting rate — :func:`eval.meeting_quality.compute_meeting_rate`
* accusation calibration — :func:`eval.accusation_calibration`
* win split + reason histogram — the ``GameReport.winner`` / ``.reason``
  reduction (:func:`eval.balance_eval._balance_report_from_tournament`,
  eval/balance_eval.py:893-894) over
  :func:`eval.balance_eval.load_tournament_report`

Usage::

    uv run python scripts/measure_baseline.py               # both canonical sets
    uv run python scripts/measure_baseline.py replays/samples/9p2i
    uv run python scripts/measure_baseline.py --json
    uv run python scripts/measure_baseline.py --funnel --json   # Task-15.3 funnel

``--json`` emits a JSON array of :class:`BaselineMeasurementReport` (schema below),
the machine-readable report the 15.15 harness and the 15.7 / 15.18 audits consume.
``--funnel`` selects the Task-15.3 information-funnel diagnostics instead — a JSON
array of :class:`eval.funnel.InformationFunnelReport` (schema in that module),
consumed by Task 15.7 for the before/after close finding. The flag is the funnel
fold region's entry point; the 15.1 core folds and the 15.2 watchability folds are
disjoint regions selected by their own (absence of a) flag.

JSON report schema (one object per measured set) — STABLE::

    {
      "replay_set_dir": str,
      "games_total": int,
      "crew_wins": int, "impostor_wins": int, "tick_budget_reached": int,
      "impostor_win_rate": float,
      "reason_histogram": {str: int, ...},      # game.reason counts, desc by count
      "r1_eject_decided_wins": int,             # count of CREWMATE_EJECT-reason wins
      "total_ejections": int, "impostor_ejections": int, "crewmate_ejections": int,
      "ejection_accuracy": float | null,        # impostor_ejections / total_ejections
      "genuine_class_supplied": int, "genuine_class_converted": int,
      "genuine_class_conversion": float | null,
      "meeting_rate": float | null, "resolved_meetings": int,
      "accusation_claim_ece": float | null, "accusation_claim_total": int,
      "vote_ballot_ece": float | null, "vote_ballot_total": int
    }

Pure + offline: no network, no ``AILIBI_*`` env.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict

# Allow `uv run python scripts/measure_baseline.py ...` to find top-level packages
# (mirrors scripts/_verify_samples.py + scripts/build_sample_report.py).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from eval.accusation_calibration import compute_accusation_calibration  # noqa: E402
from eval.balance_eval import _balance_report_from_tournament  # noqa: E402

# Task-15.3 information-funnel fold region (disjoint from the 15.1 core folds and
# the 15.2 watchability folds): the oracle / possession / transmission diagnostics,
# emitted under ``--funnel``.
from eval.funnel import (  # noqa: E402
    InformationFunnelReport,
    compute_information_funnel,
)
from eval.meeting_quality import compute_meeting_rate  # noqa: E402
from eval.report_schema import TournamentReport  # noqa: E402
from eval.validity import assemble_tournament_report, seeds_on_disk  # noqa: E402
from eval.vote_correctness import (  # noqa: E402
    compute_genuine_class_conversion,
    compute_vote_correctness,
)

# The two canonical committed baseline-2 sets measured when no dir is given.
_CANONICAL_SETS: tuple[Path, ...] = (
    _REPO_ROOT / "replays" / "samples" / "9p2i",
    _REPO_ROOT / "replays" / "samples" / "4p1i",
)
# The R1 eject-decided win share counts games won on this game-over reason.
_R1_EJECT_DECIDED_REASON = "CREWMATE_EJECT"


class BaselineMeasurementReport(BaseModel):
    """The core R-gate folds over one replay set (frozen value object).

    Reproduces the Phase-14 close numbers exactly (audit §3). See the module JSON
    schema. ``ejection_accuracy`` / ``genuine_class_conversion`` / ``meeting_rate``
    are ``None`` (undefined, not ``0.0``) with an empty denominator — the
    convention the underlying folds use.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    replay_set_dir: str
    games_total: int
    crew_wins: int
    impostor_wins: int
    tick_budget_reached: int
    impostor_win_rate: float
    reason_histogram: Mapping[str, int]
    r1_eject_decided_wins: int
    total_ejections: int
    impostor_ejections: int
    crewmate_ejections: int
    ejection_accuracy: float | None
    genuine_class_supplied: int
    genuine_class_converted: int
    genuine_class_conversion: float | None
    meeting_rate: float | None
    resolved_meetings: int
    accusation_claim_ece: float | None
    accusation_claim_total: int
    vote_ballot_ece: float | None
    vote_ballot_total: int


def _reason_histogram(report: TournamentReport) -> dict[str, int]:
    """Count each game's ``game_over`` reason, ordered by count desc then name.

    No dedicated fold exists for the reason histogram (the audit computes it ad
    hoc); this is the ``GameReport.reason`` census the R1 eject-decided share
    reads (audits/audit-phase-14-close.md §3).
    """

    counts = Counter(game.reason for game in report.games)
    return {
        reason: count
        for reason, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    }


def measure_baseline(sample_dir: Path) -> BaselineMeasurementReport:
    """Fold one replay set's committed bytes into the core R-gate measurement."""

    report = assemble_tournament_report(sample_dir)
    balance = _balance_report_from_tournament(report)
    vote = compute_vote_correctness(report)
    genuine = compute_genuine_class_conversion(report)
    meeting = compute_meeting_rate(report)
    calibration = compute_accusation_calibration(report)
    histogram = _reason_histogram(report)

    games_total = balance.games
    impostor_win_rate = balance.impostor_wins / games_total if games_total else 0.0
    return BaselineMeasurementReport(
        replay_set_dir=str(sample_dir),
        games_total=games_total,
        crew_wins=balance.crew_wins,
        impostor_wins=balance.impostor_wins,
        tick_budget_reached=balance.tick_budget_reached,
        impostor_win_rate=impostor_win_rate,
        reason_histogram=histogram,
        r1_eject_decided_wins=histogram.get(_R1_EJECT_DECIDED_REASON, 0),
        total_ejections=vote.total_ejections,
        impostor_ejections=vote.impostor_ejections,
        crewmate_ejections=vote.crewmate_ejections,
        ejection_accuracy=vote.ejection_accuracy,
        genuine_class_supplied=genuine.supplied,
        genuine_class_converted=genuine.converted,
        genuine_class_conversion=genuine.conversion_rate,
        meeting_rate=meeting.meeting_rate,
        resolved_meetings=meeting.meetings_total,
        accusation_claim_ece=calibration.accusation_claim_ece,
        accusation_claim_total=calibration.accusation_claim_total,
        vote_ballot_ece=calibration.vote_ballot_ece,
        vote_ballot_total=calibration.vote_ballot_total,
    )


def _render_human(report: BaselineMeasurementReport) -> str:
    n = report.games_total
    acc = report.ejection_accuracy
    conv = report.genuine_class_conversion
    rate = report.meeting_rate
    claim_ece = report.accusation_claim_ece
    ballot_ece = report.vote_ballot_ece
    return "\n".join(
        [
            f"R-gate baseline measurement over {report.replay_set_dir} ({n} games):",
            f"  win split: CREW {report.crew_wins} / IMP {report.impostor_wins}"
            f" / tick-budget {report.tick_budget_reached}"
            f"  (impostor win {report.impostor_win_rate:.2f})",
            f"  reason histogram: {report.reason_histogram}",
            f"  R1 eject-decided win share: {report.r1_eject_decided_wins}/{n}",
            f"  ejection accuracy: {acc if acc is None else round(acc, 4)}"
            f"  ({report.impostor_ejections} impostor / {report.crewmate_ejections}"
            f" crew of {report.total_ejections} ejections)",
            f"  genuine-class conversion: "
            f"{conv if conv is None else round(conv, 4)}"
            f"  ({report.genuine_class_converted}/{report.genuine_class_supplied})",
            f"  meeting rate: {rate if rate is None else round(rate, 4)}"
            f"  ({report.resolved_meetings} resolved meetings)",
            f"  accusation-claim ECE: "
            f"{claim_ece if claim_ece is None else round(claim_ece, 4)}"
            f" (n={report.accusation_claim_total});"
            f"  vote-ballot ECE: "
            f"{ballot_ece if ballot_ece is None else round(ballot_ece, 4)}"
            f" (n={report.vote_ballot_total})",
        ]
    )


def _emit_json(reports: Sequence[BaselineMeasurementReport]) -> str:
    import json

    return json.dumps([report.model_dump() for report in reports], indent=2)


# --------------------------------------------------------------------------- #
# Task-15.3 --funnel fold region                                              #
# --------------------------------------------------------------------------- #


def _render_funnel_human(report: InformationFunnelReport) -> str:
    n = report.report_meetings
    med = report.candidate_set_median
    mean = report.candidate_set_mean
    pm1 = report.candidate_set_pm1_mean
    return "\n".join(
        [
            f"Information-funnel diagnostics over {report.replay_set_dir} "
            f"({report.games_total} games, {n} body-report meetings):",
            "  Stage 1 (oracle): candidate-set median "
            f"{med if med is None else round(med, 2)}"
            f" / mean {mean if mean is None else round(mean, 2)};"
            f" ±1-window mean {pm1 if pm1 is None else round(pm1, 2)},"
            f" singleton {report.candidate_singleton_pm1}/{n}"
            f" (killer-unique {report.unique_killer_pm1}),"
            f" <=2 {report.candidate_le2_pm1}/{n};"
            f" killer-in-set {report.killer_in_set}/{n}",
            "  Stage 2 (possession): hard clue held "
            f"{report.hard_clue_held}/{n}"
            f" (vent {report.vent_witnessed}, last-seen-with "
            f"{report.last_seen_with_killer}, scene {report.killer_at_scene},"
            f" kill witnessed {report.kill_witnessed})",
            "  Stage 3 (transmission): vent mentioned "
            f"{report.vent_mentioned}/{report.vent_meetings};"
            f" structured vent observations "
            f"{report.structured_vent_observed}/{report.vent_meetings};"
            f" killer accused {report.killer_accused}/{n};"
            f" votes outside a <=3 set {report.votes_outside_small_set}/"
            f"{report.small_set_ejections};"
            f" reporter ejected {report.reporter_ejected}/{report.report_ejections}"
            f" ({report.reporter_ejected_innocent} innocent);"
            f" killer self-reported {report.killer_self_reported}",
        ]
    )


def _emit_funnel_json(reports: Sequence[InformationFunnelReport]) -> str:
    import json

    return json.dumps([report.model_dump() for report in reports], indent=2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fold a replay set into the core R-gate baseline measurement (Task "
            "15.1; audits/audit-phase-14-close.md §3). Pure, offline, CPU only."
        ),
    )
    parser.add_argument(
        "replay_set_dir",
        nargs="?",
        type=Path,
        default=None,
        help=(
            "directory of replay-seed-*.jsonl files; omit to measure both "
            "canonical committed sets (replays/samples/9p2i + 4p1i)"
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit the machine-readable JSON array",
    )
    parser.add_argument(
        "--funnel",
        action="store_true",
        help=(
            "emit the Task-15.3 information-funnel diagnostics (oracle / possession "
            "/ transmission) instead of the core R-gate folds; 15.7 consumes the "
            "--funnel --json rows for the before/after close finding"
        ),
    )
    args = parser.parse_args(argv)
    explicit_dir: Path | None = args.replay_set_dir
    emit_json: bool = args.json
    funnel: bool = args.funnel

    if explicit_dir is not None:
        targets = [explicit_dir]
    else:
        targets = list(_CANONICAL_SETS)

    for sample_dir in targets:
        if not sample_dir.is_dir():
            print(f"Replay-set directory not found: {sample_dir}", file=sys.stderr)
            return 2
        if not seeds_on_disk(sample_dir):
            print(f"No replay-seed-*.jsonl files in {sample_dir}", file=sys.stderr)
            return 2

    if funnel:
        funnel_reports = [compute_information_funnel(d) for d in targets]
        if emit_json:
            print(_emit_funnel_json(funnel_reports))
        else:
            print("\n\n".join(_render_funnel_human(r) for r in funnel_reports))
        return 0

    reports = [measure_baseline(sample_dir) for sample_dir in targets]
    if emit_json:
        print(_emit_json(reports))
    else:
        print("\n\n".join(_render_human(report) for report in reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
