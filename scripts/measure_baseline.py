"""The R-gate baseline measurement CLI — core folds over a replay set (Task 15.1).

The R-gate is a MEASUREMENT on a valid baseline (audits/audit-phase-14-close.md
§3, §8), not a gate: it folds a replay set's committed bytes into the numbers the
Phase-14 close reports (ejection accuracy, genuine-class conversion, meeting rate,
win split + reason histogram, accusation calibration). It reproduces baseline 2
EXACTLY from committed bytes and re-runs unchanged on baseline 3 (Task 15.7). Task
19.5 wires the Task-17.6 successor canary — supplied-channel conversion, the only
canary-eligible genuine-class cell from baseline 5 onward — beside the historical
genuine-class cell, so the measurement CLI reports the cell the canary bands read.

This module owns the CORE-folds region. The Task-15.2 watchability folds and the
Task-15.3 information-funnel folds are LATER, disjoint regions added to this same
file. Everything here WIRES existing tested folds — it never re-implements a
metric that already has a home:

* ejection accuracy / genuine-class conversion / supplied-channel conversion —
  :mod:`eval.vote_correctness`
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
    uv run python scripts/measure_baseline.py --vj --json       # Task-16.10 V&J
    uv run python scripts/measure_baseline.py --solvability     # the 20.14 ceiling
    uv run python scripts/measure_baseline.py --honesty         # the 20.15 cells

``--json`` emits a JSON array of :class:`BaselineMeasurementReport` (schema below),
the machine-readable report the 15.15 harness and the 15.7 / 15.18 audits consume.
``--funnel`` selects the Task-15.3 information-funnel diagnostics instead — a JSON
array of :class:`eval.funnel.InformationFunnelReport` (schema in that module),
consumed by Task 15.7 for the before/after close finding. The flag is the funnel
fold region's entry point; the 15.1 core folds and the 15.2 watchability folds are
disjoint regions selected by their own (absence of a) flag. ``--vj`` selects the
Task-16.10 V&J instruments — a JSON array of
:class:`eval.vj_instruments.VJInstrumentReport` (judgment metrics + deterministic
voice tier + the embedded ``eval.funnel`` pooling census; schema in that module's
docstring), the machine-readable before/after report the Task 16.17 close
consumes. ``--solvability`` selects the solvability ceiling — a JSON array of
:class:`eval.solvability.SolvabilityReport` (schema in that module's docstring):
per body-triggered meeting, how much of the killer's identity the crew's own
pooled sightings could have resolved, and how often an ejection landed on a
player that pooling had already cleared. ``--honesty`` selects the evidence-honesty
instrument set — a JSON array of :class:`eval.evidence_honesty.EvidenceHonestyReport`
(schema in that module's docstring): the Phase-20 pre-registration's instrument rows
I-2…I-11 recomputed from committed bytes, so every bar's "before" can be re-run
rather than quoted.

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
      "supplied_channel_supplied": int, "supplied_channel_converted": int,
      "supplied_channel_conversion": float | null,   # Task-17.6 successor canary
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
from eval.deduction_metrics import WilsonRateCell  # noqa: E402

# Task-20.15 evidence-honesty fold region (disjoint from every region below): the
# pre-registration's instrument rows I-2…I-11 over committed bytes, emitted under
# ``--honesty``.
from eval.evidence_honesty import (  # noqa: E402
    EvidenceHonestyReport,
    compute_evidence_honesty,
)

# Task-15.3 information-funnel fold region (disjoint from the 15.1 core folds and
# the 15.2 watchability folds): the oracle / possession / transmission diagnostics,
# emitted under ``--funnel``.
from eval.funnel import (  # noqa: E402
    InformationFunnelReport,
    compute_information_funnel,
)
from eval.meeting_quality import compute_meeting_rate  # noqa: E402
from eval.report_schema import TournamentReport  # noqa: E402

# Task-20.14 solvability fold region (disjoint from the 15.1 core folds, the 15.2
# watchability folds, the 15.3 funnel folds and the 16.10 V&J folds): the
# candidate-set ceiling computed from living crewmates' own perception, emitted
# under ``--solvability``.
from eval.solvability import (  # noqa: E402
    SolvabilityReport,
    compute_solvability_report,
)
from eval.validity import assemble_tournament_report, seeds_on_disk  # noqa: E402

# Task-16.10 V&J fold region (disjoint from the 15.1 core folds, the 15.2
# watchability folds, and the 15.3 funnel folds): judgment metrics + the
# deterministic voice tier + the embedded pooling census, emitted under
# ``--vj`` for the 16.17 close.
from eval.vj_instruments import (  # noqa: E402
    VJInstrumentReport,
    compute_vj_instruments,
)
from eval.vote_correctness import (  # noqa: E402
    compute_genuine_class_conversion,
    compute_supplied_channel_conversion,
    compute_vote_correctness,
)
from eval.watchability import (  # noqa: E402
    _DEFAULT_BASELINE_ID,
    WatchabilityReport,
    compute_watchability,
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
    # The Task-17.6 successor cell wired by 19.5 — the ONLY canary-eligible
    # genuine-class cell from baseline 5 onward (audits/audit-phase-16-close.md
    # §8), the historical genuine-class trio above having read 0/0 on two
    # consecutive substrates. Computed by the owning
    # :func:`eval.vote_correctness.compute_supplied_channel_conversion` and
    # never re-derived here. The headline pair only: the per-channel cells
    # (witnessed vent / sighting contradiction / whereabouts lie) and the
    # legacy alibi-anchored column live on the shipped report's gate_metrics
    # block, not on this measurement row.
    supplied_channel_supplied: int
    supplied_channel_converted: int
    supplied_channel_conversion: float | None
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
    supplied_channel = compute_supplied_channel_conversion(report)
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
        supplied_channel_supplied=supplied_channel.supplied,
        supplied_channel_converted=supplied_channel.converted,
        supplied_channel_conversion=supplied_channel.conversion_rate,
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
    canary = report.supplied_channel_conversion
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
            f"  supplied-channel conversion (canary): "
            f"{canary if canary is None else round(canary, 4)}"
            f"  ({report.supplied_channel_converted}/"
            f"{report.supplied_channel_supplied})",
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
# Task 15.2 watchability fold region (disjoint from the 15.1 core-folds region  #
# above and the 15.3 funnel region): the selection referee's per-game +         #
# aggregate results, emitted under `--watchability` for the 15.15 harness and    #
# the 15.7 / 15.18 audits (see eval.watchability for the doctrine + schema).     #
# --------------------------------------------------------------------------- #


def _render_watchability(report: WatchabilityReport) -> str:
    gauges = "\n".join(
        f"    {g.name}: measured "
        f"{g.measured if g.measured is None else round(g.measured, 4)} "
        f">= floor {g.floor} -> {'PASS' if g.passed else 'FAIL'}"
        for g in report.supply_gauges
    )
    top = report.per_game[0] if report.per_game else None
    top_line = (
        f"  top game: seed {top.seed} ({top.reason}) score {top.score}"
        if top is not None
        else "  (no games)"
    )
    return "\n".join(
        [
            f"Watchability referee over {report.replay_set_dir} "
            f"({report.games_total} games; baseline {report.baseline_id} / "
            f"{report.roster_key}):",
            f"  referee: {'PASS' if report.referee_passed else 'FAIL'} "
            f"(supply floors {'PASS' if report.supply_floors_passed else 'FAIL'}, "
            f"integrity {'OK' if report.integrity_ok else 'BREACH'})",
            "  evidence-supply floors:",
            gauges,
            f"  geomean: mean {report.mean_score} / median {report.median_score}",
            top_line,
        ]
    )


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


def _emit_watchability_json(reports: Sequence[WatchabilityReport]) -> str:
    import json

    return json.dumps([report.model_dump() for report in reports], indent=2)


# --------------------------------------------------------------------------- #
# Task-15.3 --funnel fold region                                              #
# --------------------------------------------------------------------------- #


def _emit_funnel_json(reports: Sequence[InformationFunnelReport]) -> str:
    import json

    return json.dumps([report.model_dump() for report in reports], indent=2)


# --------------------------------------------------------------------------- #
# Task-16.10 --vj fold region (disjoint from the 15.1 core folds, the 15.2    #
# watchability folds, and the 15.3 funnel folds): the V&J instruments —       #
# judgment metrics + the deterministic voice tier + the embedded pooling      #
# census — emitted under `--vj` for the 16.17 close (diagnostics the close    #
# quotes; the referee alone gates).                                           #
# --------------------------------------------------------------------------- #


def _round(value: float | None) -> float | None:
    return value if value is None else round(value, 4)


def _render_vj_human(report: VJInstrumentReport) -> str:
    pooling = report.pooling
    return "\n".join(
        [
            f"V&J instruments over {report.replay_set_dir} "
            f"({report.games_total} games, {report.meetings_total} meetings):",
            f"  zero-flag convictions: {report.zero_flag_convictions}/"
            f"{report.convictions_total}"
            f" (rate {_round(report.zero_flag_conviction_rate)};"
            f" crew {report.zero_flag_crew_convictions} /"
            f" impostor {report.zero_flag_impostor_convictions})",
            f"  typed split: hard {report.zero_flag_hard_backed}"
            f" / soft {report.zero_flag_soft_only}"
            f" / unattributed {report.zero_flag_unattributed_only}"
            f" / no-row {report.zero_flag_no_row};"
            f" proxy: hard {report.zero_flag_proxy_hard_backed}"
            f" / soft {report.zero_flag_proxy_soft_only}"
            f" / sub-gate {report.zero_flag_proxy_sub_gate}"
            f" / no-render {report.zero_flag_proxy_no_render}"
            f" (hard-axis agreement {report.zero_flag_split_agreements}/"
            f"{report.zero_flag_split_agreements + report.zero_flag_split_disagreements})",
            f"  reconstruction: provenance sums {report.provenance_sum_breaches}"
            f" breaches / {report.provenance_rows_checked} rows;"
            f" rendered values {report.rendered_row_mismatches} mismatches /"
            f" {report.rendered_rows_compared} compared",
            f"  citations: turn {report.turn_citations_valid} valid /"
            f" {report.turn_citations_dangling} dangling;"
            f" observation {report.observation_citations_valid} valid /"
            f" {report.observation_citations_dangling} dangling;"
            f" cited eject ballots {report.cited_eject_ballots}/"
            f"{report.eject_ballots}"
            f" (rate {_round(report.citation_compliance_rate)};"
            f" markers {report.nulled_reason_id_markers}/"
            f"{report.nulled_observation_id_markers}/"
            f"{report.coerced_zero_flag_markers})",
            f"  ballot calibration: Brier "
            f"{_round(report.ballot_confidence_brier)}"
            f" / ECE {_round(report.ballot_confidence_ece)}"
            f" (n={report.ballot_calibration_total}"
            f"{', LOW POWER' if report.ballot_calibration_low_power else ''})",
            f"  voice: echo {report.echo_ballots}/{report.voice_ballots_total}"
            f" (rate {_round(report.within_meeting_echo_rate)});"
            f" skeleton share {_round(report.response_skeleton_share)};"
            f" distinct skeletons {report.distinct_skeletons}"
            f" ({_round(report.distinct_skeleton_ratio)});"
            f" distinct-1 {_round(report.distinct_1)}"
            f" / distinct-2 {_round(report.distinct_2)}"
            f" (guard-authored ballots excluded "
            f"{report.guard_authored_ballots_excluded})",
            f"  pooling: roll-call {_round(pooling.roll_call_coverage_mean)}"
            f" ({pooling.whereabouts_claims_total} whereabouts claims);"
            f" vouch {_round(pooling.vouch_rate_mean)}"
            f" / grounded {_round(pooling.grounded_vouch_rate_mean)}"
            f" (share {_round(pooling.grounded_vouch_share)});"
            f" absence mean {_round(pooling.absence_set_size_mean)}"
            f" median {pooling.absence_set_size_median};"
            f" whereabouts lies {pooling.whereabouts_lies_detected}"
            f" (rate {_round(pooling.whereabouts_lie_detection_rate)})",
        ]
    )


def _emit_vj_json(reports: Sequence[VJInstrumentReport]) -> str:
    import json

    return json.dumps([report.model_dump() for report in reports], indent=2)


# --------------------------------------------------------------------------- #
# Task-20.14 --solvability fold region (disjoint from the 15.1 core folds, the #
# 15.2 watchability folds, the 15.3 funnel folds and the 16.10 V&J folds): the #
# solvability ceiling — at each body-triggered meeting, who the crew's own     #
# pooled sightings could not rule out, and where the ejection landed.          #
# --------------------------------------------------------------------------- #


def _solvability_line(label: str, cell: WilsonRateCell) -> str:
    interval = (
        "undefined"
        if cell.wilson_low is None or cell.wilson_high is None
        else f"[{round(cell.wilson_low, 4)}, {round(cell.wilson_high, 4)}]"
    )
    advisory = "  (rare count — read the interval)" if cell.advisory else ""
    return (
        f"  {label}: {_round(cell.rate)}"
        f"  ({cell.numerator}/{cell.denominator})  95% CI {interval}{advisory}"
    )


def _render_solvability_human(report: SolvabilityReport) -> str:
    return "\n".join(
        [
            f"Solvability ceiling over {report.replay_set_dir} "
            f"({report.games_total} games, {report.body_meetings} body meetings, "
            f"{report.ejections_at_body_meetings} ejections at them):",
            _solvability_line("killer in candidate set", report.killer_in_set),
            _solvability_line("one candidate", report.singleton_sets),
            _solvability_line("  ... and it is the killer", report.singleton_correct),
            _solvability_line("at most two candidates", report.at_most_two_sets),
            _solvability_line(
                "  ... containing the killer", report.at_most_two_contains_killer
            ),
            _solvability_line(
                "ejected a player the crew had already cleared",
                report.cleared_player_ejections,
            ),
            _solvability_line(
                "killer in candidate set, last-kill anchor",
                report.killer_in_set_last_kill_anchor,
            ),
        ]
    )


def _emit_solvability_json(reports: Sequence[SolvabilityReport]) -> str:
    import json

    return json.dumps([report.model_dump() for report in reports], indent=2)


# --------------------------------------------------------------------------- #
# Task-20.15 --honesty fold region (disjoint from every region above): the      #
# evidence-honesty instrument set — the pre-registration's rows I-2…I-11        #
# recomputed from committed bytes, so every bar's "before" can be re-run.       #
# --------------------------------------------------------------------------- #


def _render_honesty_human(report: EvidenceHonestyReport) -> str:
    whereabouts = report.false_whereabouts
    sole = report.sole_flag_precision
    grounded = report.grounded_sighting
    fabricated = report.fabricated_completions
    adjacent = report.adjacent_room_flags
    movement = report.movement_origin_flags
    markers = report.marker_contamination
    persona = report.singular_persona
    physicality = report.meeting_physicality
    targeting = report.impostor_targeting
    budget = report.render_budget
    persona_line = (
        _solvability_line(
            "I-9 singular-persona prompts", persona.prompts_with_singular_persona
        )
        if persona.applicable
        else (
            "  I-9 singular-persona prompts: NOT-APPLICABLE (one impostor — the "
            f"singular persona is true)  ({persona.prompts_with_singular_persona.numerator}"
            f"/{persona.prompts_with_singular_persona.denominator})"
        )
    )
    mean_lines = budget.rendered_lines_mean
    return "\n".join(
        [
            f"Evidence-honesty instruments over {report.replay_set_dir} "
            f"({report.games_total} games, {physicality.meetings} meetings; "
            f"+1 agent clock proved on {report.clock_alignment_checked} "
            "discriminating sightings):",
            _solvability_line("I-2 false crew self-placement", whereabouts.crew_false),
            _solvability_line(
                "  ... agent-frame reading", whereabouts.crew_false_agent_frame
            ),
            _solvability_line("  ... impostor claims", whereabouts.impostor_false),
            _solvability_line(
                "  ... copyable from a rendered self-location line",
                whereabouts.copyable_self_location,
            ),
            _solvability_line(
                "I-3 sole-flag precision (per victim)", sole.per_victim_precision
            ),
            _solvability_line(
                "  ... per meeting: crewmates ejected",
                sole.per_meeting_crewmate_ejections,
            )
            + f"  [{sole.per_meeting_sole_flag_meetings} sole-flag meetings]",
            _solvability_line("  ... class impostor share", sole.class_impostor_share),
            _solvability_line(
                "  ... living-voter base rate", sole.living_voter_base_rate
            ),
            _solvability_line(
                "I-4 grounded sighting side (+-0)", grounded.grounded_at_tick
            ),
            _solvability_line("  ... (+-1)", grounded.grounded_within_1),
            _solvability_line("  ... (+-2)", grounded.grounded_within_2)
            + f"  [{grounded.unresolvable_sides} of {grounded.strong_sides}"
            " sides unresolvable]",
            _solvability_line("I-5 fabricated completion lines", fabricated.fabricated)
            + f"  [+1 render offset {fabricated.render_offset_matches}"
            f"/{fabricated.render_offset_checked}; {fabricated.games_hit} games hit]",
            _solvability_line("I-6 adjacent-room STRONG share", adjacent.adjacent)
            + f"  [distance 2: {adjacent.distance_two}; >=3:"
            f" {adjacent.distance_three_or_more}; single-tick window:"
            f" {adjacent.single_tick_window}]",
            _solvability_line(
                "  ... adjacency alone, any tick gap", adjacent.adjacent_any_gap
            ),
            _solvability_line("I-7 movement-origin flags", movement.spoke_origin)
            + f"  [move-backed {movement.backed_by_move_line}; destination"
            f" {movement.spoke_destination}; STRONG {movement.origin_strong};"
            f" memory-truthful {movement.memory_truthful_spoken_false}]",
            _solvability_line(
                "I-8 marker contamination (turns)", markers.turns_with_marker
            ),
            _solvability_line("  ... (prompts)", markers.prompts_with_marker)
            + f"  [{markers.meetings_with_marker} meetings,"
            f" {markers.games_with_marker} games]",
            persona_line,
            _solvability_line(
                "I-10 meetings with a venting participant",
                physicality.venting_participants,
            ),
            _solvability_line(
                "  ... reporter killed within 3 ticks",
                physicality.reporter_killed_within_three,
            )
            + f"  [{physicality.body_triggered_meetings} body-triggered]",
            # The mode is part of the I-11 label, not a footnote: these cells are
            # produced by whichever policy was folded over the frozen bytes, and an
            # operator reading a fold of today's policy must not take it for the
            # ratified pre-registration baseline.
            _solvability_line(
                f"I-11 [{targeting.policy_mode}] free zero-witness kills declined",
                targeting.free_kills_declined,
            )
            + f"  [ranking {targeting.decline_reason_ranking};"
            f" fellow-defer {targeting.decline_reason_fellow_defer};"
            f" cover {targeting.decline_reason_cover};"
            f" other {targeting.decline_reason_other}]",
            _solvability_line("  ... ghost-top decisions", targeting.ghost_top)
            + f"  [{targeting.ghost_top_ejected} ejected /"
            f" {targeting.ghost_top_unseen_death} unseen death;"
            f" {targeting.reconstruction_mismatches} mismatches over"
            f" {targeting.decisions_reconstructed} decisions]",
            "  render budget: mean rendered lines/snapshot "
            f"{mean_lines if mean_lines is None else round(mean_lines, 2)}"
            f" over {budget.snapshots} snapshots;"
            f" reported-testimony rows {budget.testimony_rows_total}"
            f" {dict(budget.testimony_rows_by_living_bucket)}",
        ]
    )


def _emit_honesty_json(reports: Sequence[EvidenceHonestyReport]) -> str:
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
    parser.add_argument(
        "--watchability",
        action="store_true",
        help=(
            "emit the Task-15.2 selection-referee fold (evidence-supply floors + "
            "the D1-D4 geomean) instead of the core R-gate folds"
        ),
    )
    parser.add_argument(
        "--baseline-id",
        default=_DEFAULT_BASELINE_ID,
        help=(
            "the per-baseline supply-floor block the referee reads "
            f"(default: {_DEFAULT_BASELINE_ID}, the committed canonical set; "
            "pass baseline-2 to score against the pre-Wave-0 floors)"
        ),
    )
    parser.add_argument(
        "--vj",
        action="store_true",
        help=(
            "emit the Task-16.10 V&J instruments (zero-flag conviction channel "
            "+ citation compliance + ballot calibration + deterministic voice "
            "tier + the pooling census) instead of the core R-gate folds; the "
            "16.17 close consumes the --vj --json rows for the before/after "
            "finding"
        ),
    )
    parser.add_argument(
        "--solvability",
        action="store_true",
        help=(
            "emit the solvability ceiling (killer-in-candidate-set containment, "
            "singleton rate and correctness, and ejections landing on a player "
            "the crew's own pooled perception had already cleared) instead of "
            "the core R-gate folds"
        ),
    )
    parser.add_argument(
        "--honesty",
        action="store_true",
        help=(
            "emit the evidence-honesty instrument set (the Phase-20 "
            "pre-registration's rows I-2…I-11: false self-placement, sole-flag "
            "precision, grounded sighting sides, fabricated completions, "
            "adjacent-room and movement-origin flags, marker contamination, "
            "singular persona, meeting physicality, impostor targeting) instead "
            "of the core R-gate folds"
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

    if args.watchability:
        watchability_reports = [
            compute_watchability(sample_dir, baseline_id=args.baseline_id)
            for sample_dir in targets
        ]
        if emit_json:
            print(_emit_watchability_json(watchability_reports))
        else:
            print(
                "\n\n".join(
                    _render_watchability(report) for report in watchability_reports
                )
            )
        return 0

    if funnel:
        funnel_reports = [compute_information_funnel(d) for d in targets]
        if emit_json:
            print(_emit_funnel_json(funnel_reports))
        else:
            print("\n\n".join(_render_funnel_human(r) for r in funnel_reports))
        return 0

    if args.vj:
        vj_reports = [compute_vj_instruments(d) for d in targets]
        if emit_json:
            print(_emit_vj_json(vj_reports))
        else:
            print("\n\n".join(_render_vj_human(r) for r in vj_reports))
        return 0

    if args.solvability:
        solvability_reports = [compute_solvability_report(d) for d in targets]
        if emit_json:
            print(_emit_solvability_json(solvability_reports))
        else:
            print(
                "\n\n".join(_render_solvability_human(r) for r in solvability_reports)
            )
        return 0

    if args.honesty:
        honesty_reports = [compute_evidence_honesty(d) for d in targets]
        if emit_json:
            print(_emit_honesty_json(honesty_reports))
        else:
            print("\n\n".join(_render_honesty_human(r) for r in honesty_reports))
        return 0

    reports = [measure_baseline(sample_dir) for sample_dir in targets]
    if emit_json:
        print(_emit_json(reports))
    else:
        print("\n\n".join(_render_human(report) for report in reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
