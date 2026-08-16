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
    python scripts/build_sample_report.py --sample-dir DIR --baseline-out PATH

The default writes the report and prints a one-line summary;
``refresh_samples.sh`` invokes it after every real refresh. ``--check`` rebuilds
in memory and diffs against the committed report, exiting non-zero on drift (the
consistency gate that ``tests/scripts/test_build_sample_report.py`` and CI use).

``--baseline-out`` (Task 10.6; audit gp-7) derives the CORRECTED Wave-0
baseline from the committed bytes WITHOUT touching the committed
``tournament-eval-report.json`` (the sample dir stays single-era): the
re-derived flag census plus the Task 10.6 gate-spec metrics
(:func:`eval.meeting_quality.compute_multi_signal_conversion` /
``compute_supply_gauges``) and the per-ejection channel decomposition,
written as deterministic JSON. The committed home is
``tests/fixtures/phase10/corrected_w0_baseline.json`` — the exact file the
10.9 A/B reads as its baseline; a fixture test pins it byte-identical to a
re-derivation, so the artifact cannot drift from the committed bytes.
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
from eval.action_ingest import tally_actions_by_role  # noqa: E402
from eval.kill_craft import compute_kill_craft_report  # noqa: E402
from eval.meeting_quality import (  # noqa: E402
    TournamentEvalReport,
    build_tournament_eval_report,
    compute_ballot_target_redirects,
    compute_conversion_per_meeting,
    compute_defaulted_ballots,
    compute_effective_deflection,
    compute_indistinguishability,
    compute_multi_signal_conversion,
    compute_supply_gauges,
    decompose_ejection_channels,
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

    Mirrors the loader's dedup (and the ``_committed_9p2i_seeds`` test helper):
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
    """Rebuild the eval report for ``sample_dir`` from its committed replays.

    Task 19.14: the Task-18.2 kill-craft fold runs beside the tournament load so
    the deduction block's witnessed / co-present evidence-supply cells can be
    ADOPTED (never recomputed). It is the one input the assembled report cannot
    supply — those cells need a state-hash-verified engine walk over the replay
    DIRECTORY — so this offline entry point, which has the directory, is where
    they enter. A live tournament (``scripts/run_tournament.py``) has no
    committed directory to walk at assembly time and leaves them ``None``.
    """

    num_players, num_impostors, tasks_per_crewmate = _roster_knobs(sample_dir)
    roles_by_seed = _roles_by_seed(
        sample_dir,
        num_players=num_players,
        num_impostors=num_impostors,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    if not roles_by_seed:
        raise SystemExit(f"no replay-seed-*.jsonl found under {sample_dir}")
    # Task 8.17: the kill-gift accounting walk re-seeds from the same roster, so
    # pass tasks_per_crewmate (roles_by_seed encodes only player/impostor counts).
    # game_map defaults to load_canonical_map() inside load_tournament_report,
    # matching the map _roles_by_seed seeded with.
    report = load_tournament_report(
        sample_dir,
        roles_by_seed=roles_by_seed,
        tasks_per_crewmate=tasks_per_crewmate,
    )
    return build_tournament_eval_report(
        report, kill_craft=compute_kill_craft_report(sample_dir)
    )


def _serialize(report: TournamentEvalReport) -> str:
    """Serialize exactly as ``run_tournament.py``'s ``_emit_report_json`` does.

    ``model_dump_json(indent=2)`` + a trailing newline, round-trip-gated: a report
    that cannot be read back is not a report.
    """

    json_text = report.model_dump_json(indent=2)
    TournamentEvalReport.model_validate_json(json_text)
    return json_text + "\n"


def _summary(report: TournamentEvalReport, sample_dir: Path) -> str:
    games = report.report.games
    crew = sum(1 for game in games if game.winner == "CREWMATES")
    impostor = sum(1 for game in games if game.winner == "IMPOSTORS")
    budget = sum(1 for game in games if game.winner is None)
    meeting = report.meeting_rate
    # The Task 9.6 Wave-1 conversion leads (gp-2): precision (ejection_accuracy),
    # recall (impostor-accused conversion), and the missed-SKIP sentinel — NOT
    # vote_correctness_rate, which is a bug-sentinel structurally pinned to 1.0.
    conversion = report.conversion
    accuracy = (
        f"{conversion.ejection_accuracy:.4f}"
        if conversion.ejection_accuracy is not None
        else "n/a"
    )
    recall = (
        f"{conversion.impostor_accused_conversion_rate:.4f}"
        if conversion.impostor_accused_conversion_rate is not None
        else "n/a"
    )
    # The Task 10.4 Phase-10 gate surface (gp-7), led by the PRIMARY gate:
    # genuine-class conversion. The Task 19.5 successor canary
    # (supplied-channel conversion, the Task-17.6 re-anchor) prints beside that
    # historical genuine-class cell: the successor is the only canary-eligible
    # genuine-class cell from baseline 5 onward
    # (audits/audit-phase-16-close.md §8), the historical pair staying printed
    # as the era it anchors. ejection_accuracy stays printed above but is
    # NOT a gate against pre-repair eras (the 0.63 was artifact-built — see
    # eval.vote_correctness.GENUINE_CLASS_GATE_NOTE on the report itself).
    gate = report.gate_metrics
    genuine = gate.genuine_class_conversion
    scc = gate.supplied_channel_conversion
    # The Task 10.6 gp-7 companions: the multi-signal conversion split and
    # the supply gauges, derived fresh per run (they live on no committed
    # report block until the 10.9 re-record). The win split prints with an
    # explicit NON-GATE label: it is a constant of the race structure
    # (~90/10, zero ejection-driven wins) and gates nothing.
    multi = compute_multi_signal_conversion(games)
    gauges = compute_supply_gauges(games)
    # The Task 10.9.1/10.9.2 PR #147 repair censuses (standalone, off the frozen
    # committed report exactly like the gp-7 companions): the vote fail-soft
    # defaulted-ballot count and the ballot-target redirect count. The 10.9 gate
    # requires both reported (zero is fine, unreported is not), so they ride the
    # summary the operator generates rather than living only in their analyzers.
    defaulted = compute_defaulted_ballots(games)
    redirects = compute_ballot_target_redirects(games)
    over_gate = (
        f"{gauges.over_gate_listeners_per_accused_impostor_meeting:.2f}"
        if gauges.over_gate_listeners_per_accused_impostor_meeting is not None
        else "n/a"
    )
    # The Task 10.16 Wave-2 gate-spec metrics (standalone, off the frozen
    # committed report exactly like the gp-7 companions): the pacing-proof
    # conversion KPI, the active-deflection subcount, the inform-channel
    # attribution, and the "never-tasks" indistinguishability fingerprint. The
    # impostor win RATE prints with an explicit GUARDRAIL label (the Wave-2
    # outcome split is confounded — see eval.meeting_quality.WAVE2_GATE_SPEC).
    cpm = compute_conversion_per_meeting(games)
    deflection = compute_effective_deflection(games)
    tally = tally_actions_by_role(sample_dir, games)
    indist = compute_indistinguishability(tally)
    cpm_str = (
        f"{cpm.conversion_per_meeting:.3f}"
        if cpm.conversion_per_meeting is not None
        else "n/a"
    )
    imp_wait = (
        f"{indist.impostor_wait_share:.2f}"
        if indist.impostor_wait_share is not None
        else "n/a"
    )
    crew_wait = (
        f"{indist.crewmate_wait_share:.2f}"
        if indist.crewmate_wait_share is not None
        else "n/a"
    )
    top_idler = (
        f"{indist.top_idler_wait_share:.2f}"
        if indist.top_idler_wait_share is not None
        else "n/a"
    )
    imp_win_rate = f"{impostor / len(games):.2f}" if games else "n/a"
    # The Task 19.14 deduction headline, printed under BOTH partition names so
    # the operator never reads one partition's numerator against the other's
    # denominator (audits/audit-phase-19-triage.md §7 item 15; the C5
    # define-before-counting lesson). The block itself rides on the report.
    deduction = report.deduction
    meeting_flag = deduction.meeting_flag_cross_tab
    ejectee_proof = deduction.ejectee_proof_cross_tab
    unflagged_acc = meeting_flag.unflagged_meeting_accuracy
    non_direct_acc = ejectee_proof.non_direct_accuracy
    unflagged_str = (
        f"{unflagged_acc.rate:.3f}" if unflagged_acc.rate is not None else "n/a"
    )
    non_direct_str = (
        f"{non_direct_acc.rate:.3f}" if non_direct_acc.rate is not None else "n/a"
    )
    supply = deduction.witnessed_supply
    supply_str = (
        f"{supply.crew_witnessed_kills}/{supply.kills_total} witnessed "
        f"(co-present {supply.co_present_crew_kills})"
        if supply is not None
        else "not supplied"
    )
    return (
        f"{len(games)} games | win split (non-gate) "
        f"CREW {crew} / IMP {impostor} / budget {budget} | "
        f"meeting_rate {meeting.meeting_rate:.2f} ({meeting.meetings_total} meetings)"
        f" | ejection_accuracy {accuracy} "
        f"({conversion.impostor_ejections}/{conversion.total_ejections}) | "
        f"conversion {recall} ({conversion.impostor_accused_conversions}/"
        f"{conversion.impostor_accused_meetings}) | "
        f"missed_skip {conversion.missed_skip_ballots} | "
        f"genuine_class {genuine.converted}/{genuine.supplied} | "
        f"supplied_channel {scc.converted}/{scc.supplied} | "
        f"multi_signal {multi.multi_signal_conversions}/{multi.impostor_ejections} | "
        f"lost_openings {gate.lost_opening_accusations} "
        f"(defaults {gate.cap_defaulted_turns}) | "
        f"vote_defaults {defaulted.defaulted_skip_ballots}"
        f" (must_vote {defaulted.defaulted_under_must_vote}) | "
        f"ballot_redirects {redirects.redirected_ballots}"
        f" (eject {redirects.redirected_eject_ballots}) | "
        f"sheltered_survival {gate.survivals_sheltered_sub_gate}/"
        f"{gate.accused_impostor_survivals} | "
        f"flags {gauges.total_flags} ({gauges.weak_flags}w/{gauges.strong_flags}s) | "
        f"zero_contra {gauges.zero_contradiction_meetings}/{gauges.meetings_total} | "
        f"genuine_subject_meetings {gauges.genuine_subject_meetings} | "
        f"flag_roles {gauges.flag_subjects_crew}c/{gauges.flag_subjects_impostor}i | "
        f"over_gate_listeners/meeting {over_gate} | "
        f"[W2] conv/meeting {cpm_str} "
        f"({cpm.impostor_ejections}/{cpm.resolved_meetings}) | "
        f"effective_deflection {deflection.effective_deflections}/"
        f"{deflection.active_survivals}active "
        f"(survivals {deflection.accused_impostor_survivals}) | "
        f"inform_conversions {multi.conversions_with_single_witness_inform} | "
        f"imp_do_task {indist.impostor_do_task} (crew {indist.crewmate_do_task}) | "
        f"wait_share imp {imp_wait}/crew {crew_wait} | top_idler {top_idler} | "
        f"impostor_win_rate (GUARDRAIL, non-gate) {imp_win_rate} | "
        f"[19.14 MEETING-flag partition] flagged {meeting_flag.flagged_meetings}m "
        f"-> {meeting_flag.flagged_ejections_impostor}imp/"
        f"{meeting_flag.flagged_ejections_innocent}inn, unflagged "
        f"{meeting_flag.unflagged_meetings}m -> "
        f"{meeting_flag.unflagged_ejections_impostor}imp/"
        f"{meeting_flag.unflagged_ejections_innocent}inn "
        f"(unflagged accuracy {unflagged_acc.numerator}/{unflagged_acc.denominator} "
        f"= {unflagged_str}) | "
        f"[19.14 EJECTEE-proof partition] proof-present "
        f"{ejectee_proof.proof_present_ejections}/{ejectee_proof.ejections_total} "
        f"(non-direct accuracy {non_direct_acc.numerator}/"
        f"{non_direct_acc.denominator} = {non_direct_str}) | "
        f"weak_flag_only {deduction.weak_flag_conviction.weak_flag_only_convictions}"
        f"/{deduction.weak_flag_conviction.flag_named_ejections} "
        f"(innocent {deduction.weak_flag_conviction.weak_flag_only_innocent}) | "
        f"turn->ballot {deduction.turn_ballot_consistency.consistent_ballots}/"
        f"{deduction.turn_ballot_consistency.accusing_ballots} | "
        f"roll_call pooled crew "
        f"{deduction.public_response_coverage.crew_turns_with_whereabouts}/"
        f"{deduction.public_response_coverage.crew_turns} vs imp "
        f"{deduction.public_response_coverage.impostor_turns_with_whereabouts}/"
        f"{deduction.public_response_coverage.impostor_turns} | "
        f"redirected {deduction.redirected_ballots.redirected_ballots} "
        f"(eject {deduction.redirected_ballots.redirected_eject_ballots}) | "
        f"kill_supply {supply_str}"
    )


def write_report(sample_dir: Path) -> TournamentEvalReport:
    """Rebuild and write ``sample_dir/tournament-eval-report.json``."""

    report = build_report(sample_dir)
    (sample_dir / _REPORT_FILENAME).write_text(_serialize(report), encoding="utf-8")
    return report


def corrected_baseline_from_report(
    report: TournamentEvalReport, *, sample_dir: Path
) -> dict[str, object]:
    """Derive the corrected baseline table from a rebuilt report (10.6, 10.16).

    The A/B baseline (read by 10.9 for the W0 anchor, by 10.17 for the W1
    set): the 10.4 re-deriver (the eval analyzers, which re-run the one-home
    repaired detector per meeting) plus the Task 10.6 gate-spec metrics AND
    the Task 10.16 Wave-2 metrics, folded over the committed replays WITHOUT
    touching the committed report. Every number is produced by its owning
    ``compute_*`` analyzer (the flag census and role split live on the supply
    gauges; the indistinguishability tally reads the per-tick action stream
    via :func:`eval.action_ingest.tally_actions_by_role`, roles from the
    seeder), plus the per-ejection channel decomposition keyed
    ``"seed-{seed}:m{index}"``. Pure and deterministic over a fixed sample
    dir: re-running over the same bytes is byte-identical, which the fixture
    test pins.
    """

    games = report.report.games
    genuine = report.gate_metrics.genuine_class_conversion
    multi = compute_multi_signal_conversion(games)
    gauges = compute_supply_gauges(games)
    conversion_per_meeting = compute_conversion_per_meeting(games)
    effective_deflection = compute_effective_deflection(games)
    indistinguishability = compute_indistinguishability(
        tally_actions_by_role(sample_dir, games)
    )
    ejection_channels = {
        f"seed-{game.seed}:m{meeting_index}": sorted(channels)
        for game in games
        for meeting_index in range(len(game.meetings))
        if (channels := decompose_ejection_channels(game, meeting_index)) is not None
    }
    return {
        "sample_dir": sample_dir.name,
        "genuine_class_conversion": genuine.model_dump(mode="json"),
        "multi_signal_conversion": multi.model_dump(mode="json"),
        "supply_gauges": gauges.model_dump(mode="json"),
        "conversion_per_meeting": conversion_per_meeting.model_dump(mode="json"),
        "effective_deflection": effective_deflection.model_dump(mode="json"),
        "indistinguishability": indistinguishability.model_dump(mode="json"),
        "impostor_ejection_channels": ejection_channels,
    }


def serialize_corrected_baseline(baseline: dict[str, object]) -> str:
    """Deterministic baseline JSON: sorted keys, 2-space indent, newline."""

    return json.dumps(baseline, indent=2, sort_keys=True) + "\n"


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
        default=_REPO_ROOT / "replays" / "samples" / "4p1i",
        help="Sample set directory (default: replays/samples/4p1i, the flat 4p/1i set).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Rebuild and diff against the committed report; exit 1 on drift.",
    )
    parser.add_argument(
        "--baseline-out",
        type=Path,
        default=None,
        help=(
            "Derive the Task 10.6 corrected baseline from the committed bytes "
            "and write it to this path (the committed report is NOT touched)."
        ),
    )
    args = parser.parse_args()
    sample_dir: Path = args.sample_dir

    if args.check:
        return check_report(sample_dir)
    if args.baseline_out is not None:
        report = build_report(sample_dir)
        baseline = corrected_baseline_from_report(report, sample_dir=sample_dir)
        baseline_out: Path = args.baseline_out
        baseline_out.parent.mkdir(parents=True, exist_ok=True)
        baseline_out.write_text(
            serialize_corrected_baseline(baseline), encoding="utf-8"
        )
        print(f"Wrote {baseline_out}: {_summary(report, sample_dir)}")
        return 0
    report = write_report(sample_dir)
    print(f"Wrote {sample_dir / _REPORT_FILENAME}: {_summary(report, sample_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
