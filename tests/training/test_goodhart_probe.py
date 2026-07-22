"""Tests for the adversarial Goodhart probe (Task 15.14; surrogate re-run 17.15).

Exercises the probe machinery on a TINY 4p1i budget (the flat determinism/leak
roster — short games, fast), not the committed report budget: the point is the
selector-is-always-legal invariant, the determinism of the run, the
report/verdict shape, and (Task 17.15) the surrogate-path regime pins — not a
full attack.
"""

from __future__ import annotations

import dataclasses
import json
import random
import shutil
from pathlib import Path

import pytest

from eval.watchability import WatchabilityGameScore, WatchabilityReport
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import (
    CarriedExploitReread,
    ConvictionLeverRead,
    ConvictionPathProbeReport,
    GoodhartProbeReport,
    ProbeExploit,
    TraceImprovement,
    _build_conviction_findings,
    _build_conviction_read,
    _build_exploits,
    _build_gate_check,
    _ConvictionArmReader,
    _ConvictionSetRead,
    _decompose_improvement,
    _ExploitCandidate,
    _forced_genome,
    _RefereeAttackEvaluator,
    _SetAggregates,
    _SetEvaluation,
    _sweep_levers,
    build_probe_selector,
    probe_genome_length,
    reread_carried_4p1i_exploit,
    run_conviction_path_probe,
    run_goodhart_probe,
)
from training.bakeoff.harness import load_conviction_fitness_term
from training.conviction.fidelity import (
    CONVICTION_CONVERSION_DECISION_THRESHOLD,
    VERDICT_FILENAME,
)
from training.conviction.model import (
    STALENESS_FILENAME,
    WEIGHTS_FILENAME,
    WEIGHTS_SHA256_FILENAME,
)
from training.env import TacticalRolloutEnv
from training.surrogate.ballots import load_staleness_cap
from training.surrogate.runner import SurrogateUseCounter, load_surrogate_runner_factory

# The COMMITTED re-grounded artifact (Task 17.10) the 17.15 re-run consumes —
# read-only here; the probe never writes to it.
_SURROGATE_ARTIFACT_DIR = Path("training/artifacts/surrogate")


def _watchability(
    *,
    referee_passed: bool,
    mean_score: float,
    per_game: tuple[WatchabilityGameScore, ...] = (),
) -> WatchabilityReport:
    """A minimal WatchabilityReport fixture (only the fields _build_exploits reads)."""

    return WatchabilityReport(
        replay_set_dir="x",
        baseline_id="baseline-5",
        roster_key="9p2i",
        games_total=len(per_game),
        integrity_ok=True,
        referee_passed=referee_passed,
        supply_floors_passed=referee_passed,
        supply_gauges=(),
        mean_score=mean_score,
        median_score=mean_score,
        per_game=per_game,
    )


def _game(score: float) -> WatchabilityGameScore:
    """A minimal per-game score fixture (only ``score`` matters to aggregates)."""

    return WatchabilityGameScore(
        seed=0,
        reason="crew_win_tasks",
        n_meetings=1,
        floor_multiplier=1.0,
        d1_resolution=0.5,
        d2_deduction=0.1,
        d3_craft=0.0,
        d4_arc=0.2,
        d2_separation_norm=0.1,
        d2_conversion=0.0,
        d4_arc_term=0.1,
        d4_swing_term=0.0,
        d4_contest_term=0.0,
        score=score,
    )


# A cheap budget: 1 generation x 2 offspring over 2 seeds on the short 4p1i roster.
_TINY = ESConfig(generations=1, population=2, sigma=0.4, seed=0, fitness_seeds=(0, 1))


def _run_tiny() -> GoodhartProbeReport:
    return run_goodhart_probe(
        config=_TINY,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        materiality_bar=0.25,
    )


def test_probe_genome_length_matches_mlp() -> None:
    # input 8 -> hidden 4 -> output 6 : 8*4 + 4 + 4*6 + 6
    assert probe_genome_length() == 8 * 4 + 4 + 4 * 6 + 6


def test_selector_only_emits_legal_intents() -> None:
    # A random-genome impostor rolled through the env: the env RAISES on any
    # non-submission-legal intent, so a clean full rollout IS the legality proof.
    rng = random.Random(0)
    genome = tuple(rng.gauss(0.0, 0.6) for _ in range(probe_genome_length()))
    env = TacticalRolloutEnv(
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        intent_selector=build_probe_selector(genome),
    )
    rollout = env.rollout(0)
    assert rollout.complete or rollout.truncated


def test_probe_report_shape_and_verdict() -> None:
    report = _run_tiny()
    assert isinstance(report, GoodhartProbeReport)
    assert report.roster_key == "4p1i"
    assert report.verdict in ("HELD", "EXPLOITS_FOUND")
    assert report.genome_length == probe_genome_length()
    # Budget is stated honestly (generations x population x seeds).
    assert report.budget.generations == 1
    assert report.budget.population == 2
    assert report.budget.num_seeds == 2
    assert report.budget.total_evaluations == 1 + 1 * 2
    # The reachability sweep forces every non-FSM lever.
    assert report.budget.lever_sweep_evaluations == len(report.lever_sweep)
    assert len(report.lever_sweep) >= 1
    # The strongest reachable score is never below the honest baseline.
    assert report.strongest_reachable_score >= report.baseline_mean_score
    # The fitness trace has one entry per generation (+ the seeded genome).
    assert len(report.fitness_trace) == _TINY.generations + 1
    # The surrogate re-run obligation is always stated (never "referee safe").
    assert "surrogate" in report.surrogate_rerun_obligation.lower()
    assert "15.15" in report.surrogate_rerun_obligation
    assert report.supply_floor_note


def test_every_improvement_is_decomposed() -> None:
    # "No undecomposed gains": every strict increase in the trace has exactly one
    # improvement record naming the moving term + behavioral cause.
    report = _run_tiny()
    improving = [
        gen
        for gen in range(1, len(report.fitness_trace))
        if report.fitness_trace[gen] > report.fitness_trace[gen - 1] + 1e-9
    ]
    assert len(report.improvements) == len(improving)
    for improvement in report.improvements:
        assert isinstance(improvement, TraceImprovement)
        assert improvement.moving_term in (
            "d1",
            "d2",
            "d3",
            "d4",
            "floor",
            "validity_gate",
            "referee_gate",
        )
        assert improvement.behavioral_cause
        # Under fake meetings the composed gate never clears, so no trace
        # improvement can be a gate flip.
        assert improvement.referee_passed_before is False
        assert improvement.referee_passed_after is False


def test_verdict_matches_exploits() -> None:
    report = _run_tiny()
    if report.verdict == "EXPLOITS_FOUND":
        assert report.exploits
        for exploit in report.exploits:
            assert isinstance(exploit, ProbeExploit)
            assert exploit.recommended_floor
            assert exploit.trajectory_evidence
    else:
        assert not report.exploits


def test_probe_is_deterministic() -> None:
    first = _run_tiny()
    second = _run_tiny()
    assert first.es_digest == second.es_digest
    assert first.fitness_trace == second.fitness_trace
    assert first.verdict == second.verdict
    assert first.champion_mean_score == second.champion_mean_score


def test_probe_report_round_trips_json() -> None:
    report = _run_tiny()
    restored = GoodhartProbeReport.model_validate_json(report.to_json())
    assert restored == report


def test_probe_reruns_end_to_end_on_the_regrounded_surrogate() -> None:
    # Task 17.15: the probe runs end-to-end with the COMMITTED re-grounded
    # surrogate (17.10's artifact) threaded through the probe's own
    # meeting_runner_factory seam. Pins the surrogate-path regime the
    # regenerated report documents: the evidence text flips to the surrogate
    # branch, the staleness counter meters real simulated meetings against the
    # committed cap, and the HARD validity gate FAIL-CLOSES every
    # surrogate-scored set (cost_and_provenance_exact: surrogate meetings
    # record no model provenance) — so a surrogate-path HELD is the
    # wrong-reason regime, never exploit-caught. A future synthetic-provenance
    # stamp must flip these pins consciously.
    counter = SurrogateUseCounter(load_staleness_cap(_SURROGATE_ARTIFACT_DIR))
    factory = load_surrogate_runner_factory(
        _SURROGATE_ARTIFACT_DIR, use_counter=counter
    )
    report = run_goodhart_probe(
        config=_TINY,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        materiality_bar=0.25,
        meeting_runner_factory=factory,
    )
    assert isinstance(report, GoodhartProbeReport)
    assert report.baseline_id == "baseline-6"
    assert report.verdict in ("HELD", "EXPLOITS_FOUND")
    # The surrogate meeting path was actually exercised and metered.
    assert counter.uses > 0
    assert counter.uses <= counter.cap.max_uses
    # The evidence text is on the surrogate branch, not the fake-meeting one.
    assert "the surrogate meeting path" in report.supply_floor_note
    # The validity gate fail-closes surrogate sets (no model provenance rows),
    # including the scripted-FSM baseline — the structural finding the report
    # states alongside the verdict.
    assert report.baseline_validity_passed is False
    assert report.champion_validity_passed is False
    # With every set inadmissible, no candidate can clear the composed referee.
    assert report.baseline_referee_passed is False
    assert report.champion_referee_passed is False


def _champion_eval(
    *, referee_passed: bool, mean_score: float, validity_passed: bool = True
) -> _SetEvaluation:
    return _SetEvaluation(
        fitness=mean_score if validity_passed else -1.0,
        watchability=_watchability(
            referee_passed=referee_passed, mean_score=mean_score
        ),
        validity_passed=validity_passed,
    )


def test_gate_laundering_is_flagged_without_geomean_gain() -> None:
    # A champion that CLEARS the referee gate the baseline does NOT is a material
    # exploit even with a BELOW-BAR (here NEGATIVE) geomean gain — the referee
    # would select this laundered champion (the 15.15 surrogate-path threat).
    exploits, strongest = _build_exploits(
        baseline_score=10.0,
        baseline_aggs=_SetAggregates(*([0.0] * 12)),
        baseline_referee_passed=False,
        champion_eval=_champion_eval(referee_passed=True, mean_score=8.0),
        champion_score=8.0,
        champion_gain=-0.2,  # LOWER geomean than the baseline, but clears the gate
        lever_candidates=(),
        materiality_bar=0.25,
        fake_meetings=False,
    )
    assert len(exploits) == 1
    assert exploits[0].moving_term == "referee_gate"
    assert "LAUNDERED" in exploits[0].trajectory_evidence
    assert strongest == 10.0  # baseline is still the strongest ADMISSIBLE score here


def test_gate_pass_not_flagged_when_baseline_also_passes() -> None:
    # If the honest baseline already clears the gate, a champion also clearing it
    # (with no geomean gain) is NOT laundering — no exploit.
    exploits, _ = _build_exploits(
        baseline_score=10.0,
        baseline_aggs=_SetAggregates(*([0.0] * 12)),
        baseline_referee_passed=True,
        champion_eval=_champion_eval(referee_passed=True, mean_score=9.0),
        champion_score=9.0,
        champion_gain=-0.1,
        lever_candidates=(),
        materiality_bar=0.25,
        fake_meetings=False,
    )
    assert exploits == ()


def test_below_bar_geomean_gain_is_not_promoted() -> None:
    # A gain just under the bar must not be promoted (unrounded threshold).
    exploits, _ = _build_exploits(
        baseline_score=10.0,
        baseline_aggs=_SetAggregates(*([0.0] * 12)),
        baseline_referee_passed=False,
        champion_eval=_champion_eval(referee_passed=False, mean_score=12.4996),
        champion_score=12.4996,
        champion_gain=0.24996,
        lever_candidates=(),
        materiality_bar=0.25,
        fake_meetings=True,
    )
    assert exploits == ()


def _lever_candidate(
    *, label: str, score: float, gain: float, aggs: _SetAggregates
) -> _ExploitCandidate:
    return _ExploitCandidate(
        label=label,
        score=score,
        gain=gain,
        referee_passed=False,
        validity_passed=True,
        aggs=aggs,
    )


def _d2_aggs(*, separation: float = 0.0, conversion: float = 0.0) -> _SetAggregates:
    return _SetAggregates(
        mean_score=0.0,
        mean_d1=0.0,
        mean_d2=0.5,
        mean_d3=0.0,
        mean_d4=0.0,
        mean_d2_separation=separation,
        mean_d2_conversion=conversion,
        mean_d4_arc=0.0,
        mean_d4_swing=0.0,
        mean_d4_contest=0.0,
        mean_meetings=0.0,
        floor_trip_rate=0.0,
    )


def test_distinct_mechanisms_on_same_dimension_are_both_reported() -> None:
    # Two material candidates that move the SAME top-level D dimension (d2)
    # through DIFFERENT mechanisms (separation theater vs conversion) are two
    # distinct exploits — the dedupe key is the mechanism, not the dimension.
    exploits, _ = _build_exploits(
        baseline_score=10.0,
        baseline_aggs=_SetAggregates(*([0.0] * 12)),
        baseline_referee_passed=False,
        champion_eval=_champion_eval(referee_passed=False, mean_score=10.0),
        champion_score=10.0,
        champion_gain=0.0,  # the ES champion itself is not material here
        lever_candidates=(
            _lever_candidate(
                label="forced-kill lever",
                score=20.0,
                gain=1.0,
                aggs=_d2_aggs(separation=0.5),
            ),
            _lever_candidate(
                label="forced-report lever",
                score=15.0,
                gain=0.5,
                aggs=_d2_aggs(conversion=0.5),
            ),
        ),
        materiality_bar=0.25,
        fake_meetings=True,
    )
    assert len(exploits) == 2
    assert all(exploit.moving_term == "d2" for exploit in exploits)
    assert {exploit.mechanism for exploit in exploits} == {
        "d2-separation-theater",
        "d2-conversion",
    }
    # Each mechanism carries ITS OWN recommended floor, not the dimension's.
    by_mechanism = {exploit.mechanism: exploit for exploit in exploits}
    assert (
        "GATE the D2 separation"
        in by_mechanism["d2-separation-theater"].recommended_floor
    )
    assert (
        "audit HOW the D2 conversions"
        in by_mechanism["d2-conversion"].recommended_floor
    )


def test_same_mechanism_is_deduped_to_worst_case() -> None:
    # Two candidates with the SAME mechanism collapse to one exploit carrying the
    # worst-case (highest-scoring) evidence.
    exploits, _ = _build_exploits(
        baseline_score=10.0,
        baseline_aggs=_SetAggregates(*([0.0] * 12)),
        baseline_referee_passed=False,
        champion_eval=_champion_eval(referee_passed=False, mean_score=10.0),
        champion_score=10.0,
        champion_gain=0.0,
        lever_candidates=(
            _lever_candidate(
                label="forced-kill lever",
                score=18.0,
                gain=0.8,
                aggs=_d2_aggs(separation=0.4),
            ),
            _lever_candidate(
                label="forced-sabotage lever",
                score=20.0,
                gain=1.0,
                aggs=_d2_aggs(separation=0.5),
            ),
        ),
        materiality_bar=0.25,
        fake_meetings=True,
    )
    assert len(exploits) == 1
    assert exploits[0].mechanism == "d2-separation-theater"
    assert exploits[0].score_champion == 20.0


def test_gate_flip_improvement_decomposes_to_referee_gate() -> None:
    # A trace improvement that FLIPS referee_passed includes the dominating
    # referee-pass bonus; it must decompose to the referee_gate term (with the
    # gate state carried through), never to whichever D-term drifted alongside.
    improvement = _decompose_improvement(
        1,
        5.0,
        1004.0,
        _champion_eval(referee_passed=False, mean_score=5.0),
        _champion_eval(referee_passed=True, mean_score=4.0),
    )
    assert improvement.moving_term == "referee_gate"
    assert improvement.referee_passed_before is False
    assert improvement.referee_passed_after is True
    assert "referee-pass bonus" in improvement.behavioral_cause


def test_non_flip_improvement_keeps_dterm_decomposition() -> None:
    improvement = _decompose_improvement(
        1,
        5.0,
        6.0,
        _champion_eval(referee_passed=False, mean_score=5.0),
        _champion_eval(referee_passed=False, mean_score=6.0),
    )
    assert improvement.moving_term in ("d1", "d2", "d3", "d4", "floor")
    assert improvement.referee_passed_before is False
    assert improvement.referee_passed_after is False
    assert improvement.validity_passed_before is True
    assert improvement.validity_passed_after is True


def test_validity_flip_improvement_decomposes_to_validity_gate() -> None:
    # An improvement out of _INVALID_FITNESS is constraint satisfaction — the
    # whole gain is the first ADMISSIBLE set's referee score, never a D-term
    # move, regardless of the D-term deltas alongside it.
    improvement = _decompose_improvement(
        1,
        -1.0,
        5.0,
        _champion_eval(referee_passed=False, mean_score=0.0, validity_passed=False),
        _champion_eval(referee_passed=False, mean_score=5.0),
    )
    assert improvement.moving_term == "validity_gate"
    assert improvement.validity_passed_before is False
    assert improvement.validity_passed_after is True
    assert "constraint satisfaction" in improvement.behavioral_cause

    # When validity AND the referee gate flip together, the validity flip wins:
    # the previous fitness was pinned at _INVALID_FITNESS, so the jump is
    # admission first (the cause still names the after gate state).
    both = _decompose_improvement(
        1,
        -1.0,
        1005.0,
        _champion_eval(referee_passed=False, mean_score=0.0, validity_passed=False),
        _champion_eval(referee_passed=True, mean_score=5.0),
    )
    assert both.moving_term == "validity_gate"
    assert "referee_passed=True" in both.behavioral_cause


class _StubEvaluator:
    """A stand-in returning one fixed evaluation for every genome."""

    def __init__(self, evaluation: _SetEvaluation) -> None:
        self._evaluation = evaluation

    def evaluate_set(self, genome: tuple[float, ...] | None) -> _SetEvaluation:
        return self._evaluation


def test_lever_materiality_uses_unrounded_set_mean() -> None:
    # The referee's report-level mean_score is rounded to 2 decimals: a set whose
    # per-game mean is 12.4996 reports mean_score=12.5, which against a 10.0
    # baseline reads as EXACTLY the 25% bar. The sweep must threshold on the
    # unrounded per-game mean (24.996% — below the bar), so nothing is promoted.
    games = (_game(12.4996), _game(12.4996))
    evaluation = _SetEvaluation(
        fitness=12.5,
        watchability=_watchability(
            referee_passed=False, mean_score=12.5, per_game=games
        ),
        validity_passed=True,
    )
    baseline_aggs = _SetAggregates(*([0.0] * 12))
    levers, candidates = _sweep_levers(
        _StubEvaluator(evaluation),  # type: ignore[arg-type]
        10.0,
        baseline_aggs,
    )
    assert all(candidate.gain < 0.25 for candidate in candidates)
    exploits, _ = _build_exploits(
        baseline_score=10.0,
        baseline_aggs=baseline_aggs,
        baseline_referee_passed=False,
        champion_eval=_champion_eval(referee_passed=False, mean_score=10.0),
        champion_score=10.0,
        champion_gain=0.0,
        lever_candidates=candidates,
        materiality_bar=0.25,
        fake_meetings=True,
    )
    assert exploits == ()
    # The display row keeps the referee's own rounded value.
    assert all(lever.mean_score == 12.5 for lever in levers)


def test_evaluator_rejects_duplicate_fitness_seeds() -> None:
    # The evaluator writes one replay-seed-{seed}.jsonl per rollout, so a
    # duplicate seed would overwrite its earlier replay and the referee would
    # score fewer games than the stated K-seed budget. ESConfig rejects
    # duplicates too; this pins the evaluator's own guard.
    with pytest.raises(ValueError):
        _RefereeAttackEvaluator(
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            fitness_seeds=(0, 1, 0),
            baseline_id="baseline-5",
        )


# --------------------------------------------------------------------------- #
# The 18.18 conviction-path arms — predicted supply vs recorded reality.        #
# --------------------------------------------------------------------------- #

# The committed 18.16 conviction bundle the arms consume read-only (the probe
# never writes to it): a GO verdict, prescreen_role "gating", weights 4841f8e0…,
# a committed cap of 52481 predicted meetings.
_CONVICTION_ARTIFACT_DIR = Path("training/artifacts/conviction")


@pytest.fixture(scope="module")
def conviction_report() -> ConvictionPathProbeReport:
    """One tiny 4p1i conviction-path run, shared by every shape test.

    The full entry point is EXPENSIVE relative to the other tests (it re-rolls
    the scripted-FSM baseline, every forced lever, and the ES champion corner
    through the committed instrument), so it runs AT MOST ONCE per session — the
    module scope — and the shape tests read structure off this single report.
    Determinism of the entry point is pinned at the UNIT level
    (test_conviction_reader_determinism_at_unit_level), never by a second full
    run.
    """

    return run_conviction_path_probe(
        config=_TINY,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        materiality_bar=0.25,
    )


def test_conviction_path_report_shape(
    conviction_report: ConvictionPathProbeReport,
) -> None:
    report = conviction_report
    assert isinstance(report, ConvictionPathProbeReport)
    assert report.roster_key == "4p1i"
    # The reads are the scripted-FSM baseline first, then the forced levers in
    # menu order, then the ES champion corner (the reachability net's shape).
    assert [read.tactic for read in report.reads] == [
        "fsm-baseline",
        "emergency",
        "report",
        "wait",
        "kill",
        "sabotage",
        "es-champion",
    ]
    baseline_read = report.reads[0]
    assert baseline_read.tactic == "fsm-baseline"
    # The scripted-FSM baseline anchors every delta — gain 0.0 by definition,
    # zero term delta, and never a laundering finding (the delta convention).
    assert baseline_read.launders_supply is False
    assert baseline_read.conviction_term_delta == 0.0
    assert baseline_read.predicted_supply_gain == 0.0
    # The embedded standing report is the UNCHANGED probe — its budget/verdict
    # pins match the tiny config exactly (test_probe_report_shape_and_verdict).
    assert isinstance(report.probe, GoodhartProbeReport)
    assert report.probe.roster_key == "4p1i"
    assert report.probe.verdict in ("HELD", "EXPLOITS_FOUND")
    assert report.probe.budget.generations == 1
    assert report.probe.budget.population == 2
    assert report.probe.budget.num_seeds == 2
    assert report.probe.budget.total_evaluations == 1 + 1 * 2
    # champion_genome is the ADDITIVE 18.18 field — the exact ES champion the
    # arms re-roll, the same length the standing genome reports.
    assert len(report.probe.champion_genome) == probe_genome_length()
    # The committed 18.16 verdict is consumed as machine-readable fields.
    assert report.conviction_model_verdict == "GO"
    assert report.prescreen_role == "gating"
    assert report.conversion_threshold == CONVICTION_CONVERSION_DECISION_THRESHOLD


def test_conviction_path_consumption_is_metered_and_quoted(
    conviction_report: ConvictionPathProbeReport,
) -> None:
    report = conviction_report
    # The consumption discipline: every recorded meeting is predicted exactly
    # twice on the ONE shared sha-keyed counter — the fitness-term read and the
    # composed-gate pre-screen read — so the spend is 2x the recorded meetings.
    recorded_meetings = sum(read.meetings for read in report.reads)
    assert report.conviction_uses == 2 * recorded_meetings
    assert report.conviction_uses > 0
    assert report.conviction_uses_total >= report.conviction_uses
    # The committed cap is QUOTED, not re-pinned to a brittle exact number — the
    # cumulative spend stays inside it.
    assert report.conviction_max_uses > 0
    assert report.conviction_uses_total <= report.conviction_max_uses
    # The note quotes both the spend and the cap (never a silent caveat).
    assert str(report.conviction_uses) in report.consumption_note
    assert str(report.conviction_max_uses) in report.consumption_note


def test_conviction_path_verdict_composes_blockers(
    conviction_report: ConvictionPathProbeReport,
) -> None:
    report = conviction_report
    # The verdict composes over the LIST of blockers — the conviction-path
    # findings AND the standing probe's exploits — never a prose caveat.
    assert (report.verdict == "EXPLOITS_FOUND") == bool(report.blockers)
    for finding in report.findings:
        # Every conviction-path finding contributes its NAMED blocker.
        assert finding.blocker in report.blockers
        # The conviction-path mechanisms: the term paying for predicted supply;
        # the pre-screen floors flipping past the honest baseline; the baseline-
        # shared substrate divergence.
        assert finding.mechanism in (
            "conviction-supply-laundering",
            "prescreen-gate-laundering",
            "prescreen-substrate-divergence",
        )
        # The scripted-FSM baseline is the anchor, never itself a per-read finding.
        assert finding.tactic != "fsm-baseline"
    # Every standing above-bar exploit is carried across as a blocker naming its
    # mechanism (the 18.24 protocol consumes the merged list).
    for exploit in report.probe.exploits:
        assert any(exploit.mechanism in blocker for blocker in report.blockers)


def test_conviction_path_report_round_trips_json(
    conviction_report: ConvictionPathProbeReport,
) -> None:
    report = conviction_report
    restored = ConvictionPathProbeReport.model_validate_json(report.to_json())
    assert restored == report


def test_carried_4p1i_reread(
    conviction_report: ConvictionPathProbeReport,
) -> None:
    report = conviction_report
    reread = reread_carried_4p1i_exploit(report)
    assert isinstance(reread, CarriedExploitReread)
    # The carried finding is the 4p1i d4-contest-farming exploit
    # (audits/audit-phase-17-close.md §6), re-read on the emergency lever.
    assert reread.mechanism == "d4-contest-farming"
    assert reread.tactic == "emergency"
    assert reread.roster_key == "4p1i"
    # The carried pins are the audit-committed NUMBERS, never re-measured.
    assert reread.carried_baseline_mean_score == 0.85
    assert reread.carried_lever_mean_score == 1.38
    assert reread.carried_relative_gain == 0.618
    # The re-read numbers are the report's OWN emergency lever (the current
    # substrate stated beside the carried pins).
    lever = next(
        entry for entry in report.probe.lever_sweep if entry.tactic == "emergency"
    )
    assert reread.reread_lever_mean_score == lever.mean_score
    assert reread.reread_relative_gain == lever.relative_gain
    # still_above_bar keeps or releases the carried blocker on the honest
    # validity-gated relative gain.
    assert reread.still_above_bar == (
        lever.validity_passed and lever.relative_gain >= report.materiality_bar
    )
    # The materiality arithmetic states the carried numbers explicitly.
    assert "0.85" in reread.materiality_arithmetic
    assert "1.38" in reread.materiality_arithmetic


def test_carried_reread_requires_the_reference_roster(
    conviction_report: ConvictionPathProbeReport,
) -> None:
    # The carried finding is roster-SPECIFIC: re-reading it off a non-4p1i
    # report fails loud rather than silently mis-attributing the pins. The model
    # is frozen, so model_copy is the sanctioned way to build the off-roster
    # variant.
    off_roster = conviction_report.model_copy(update={"roster_key": "9p2i"})
    with pytest.raises(ValueError):
        reread_carried_4p1i_exploit(off_roster)


def test_champion_genome_is_additive_for_old_report_json(
    conviction_report: ConvictionPathProbeReport,
) -> None:
    # champion_genome defaults to () so pre-18.18 report JSON (which never
    # carried the field) still validates — the additive-field contract.
    data = conviction_report.probe.model_dump(mode="json")
    del data["champion_genome"]
    restored = GoodhartProbeReport.model_validate(data)
    assert restored.champion_genome == ()


# A neutral raw conviction-set read: material-free defaults the laundering
# fixtures below override one axis at a time (no rollouts — the delta logic is
# unit-tested straight off constructed reads).
_NEUTRAL_SET_READ = _ConvictionSetRead(
    label="forced-emergency lever",
    tactic="emergency",
    games=2,
    meetings=2,
    validity_passed=True,
    referee_passed=False,
    supply_floors_passed=False,
    mean_score=1.0,
    episode_predicted_supply=1.0,
    episode_actual_flags=1.0,
    predicted_flags_per_meeting=1.0,
    actual_flags_per_meeting=1.0,
    predicted_converting_share=0.0,
    predicted_mean_conversion_prob=0.0,
    actual_converting_share=0.0,
    prescreen_flags_pass=False,
    prescreen_conversion_pass=False,
    prescreen_floors_pass=False,
    prescreen_advisory_only=False,
)


def _set_read(**overrides: bool | float | str) -> _ConvictionSetRead:
    """One raw conviction-set read with neutral defaults (override per axis)."""

    fields = dataclasses.asdict(_NEUTRAL_SET_READ)
    fields.update(overrides)
    return _ConvictionSetRead(**fields)


def test_conviction_read_launders_on_predicted_gain_without_reality() -> None:
    baseline = _set_read(
        tactic="fsm-baseline", episode_predicted_supply=1.0, episode_actual_flags=1.0
    )
    # Material predicted-supply gain (1.0 -> 1.5, +50%) with the recorded flags
    # flat (1.0 -> 1.0): the term bought fitness the play's bytes never minted —
    # the probe's UNCHANGED delta convention flags it.
    launders = _build_conviction_read(
        baseline,
        _set_read(episode_predicted_supply=1.5, episode_actual_flags=1.0),
        weight=0.5,
        materiality_bar=0.25,
    )
    assert launders.launders_supply is True
    assert "vs the 25% bar" in launders.materiality_arithmetic

    # Both channels material (predicted 1.0 -> 1.5, actual 1.0 -> 1.5): reality
    # keeps pace, so nothing is laundered.
    both = _build_conviction_read(
        baseline,
        _set_read(episode_predicted_supply=1.5, episode_actual_flags=1.5),
        weight=0.5,
        materiality_bar=0.25,
    )
    assert both.launders_supply is False

    # Below-bar predicted gain (1.0 -> 1.2, +20%): under the 25% bar, not
    # material.
    below = _build_conviction_read(
        baseline,
        _set_read(episode_predicted_supply=1.2, episode_actual_flags=1.0),
        weight=0.5,
        materiality_bar=0.25,
    )
    assert below.launders_supply is False

    # Validity-gated: an inadmissible set is never a reachable attack, however
    # material its predicted gain (the standing doctrine).
    invalid = _build_conviction_read(
        baseline,
        _set_read(
            episode_predicted_supply=1.5,
            episode_actual_flags=1.0,
            validity_passed=False,
        ),
        weight=0.5,
        materiality_bar=0.25,
    )
    assert invalid.launders_supply is False

    # Non-positive baseline supply (0.0 -> 0.5): the gain is +inf, so it clears
    # the bar and launders, but the DISPLAYED gain is the standing non-finite
    # convention (-1.0) while the arithmetic keeps the honest "+inf% (baseline 0)".
    zero_baseline = _build_conviction_read(
        _set_read(
            tactic="fsm-baseline",
            episode_predicted_supply=0.0,
            episode_actual_flags=0.0,
        ),
        _set_read(episode_predicted_supply=0.5, episode_actual_flags=0.0),
        weight=0.5,
        materiality_bar=0.25,
    )
    assert zero_baseline.launders_supply is True
    assert zero_baseline.predicted_supply_gain == -1.0
    assert "+inf% (baseline 0)" in zero_baseline.materiality_arithmetic

    # The term arithmetic: conviction_term = weight x predicted supply, and the
    # delta is weight x (lever - baseline supply) — priced exactly as
    # inner_episode_fitness composes it.
    term_read = _build_conviction_read(
        baseline,
        _set_read(episode_predicted_supply=1.5),
        weight=0.5,
        materiality_bar=0.25,
    )
    assert term_read.conviction_term == round(0.5 * 1.5, 4)
    assert term_read.conviction_term_delta == round(0.5 * (1.5 - 1.0), 4)


# A neutral conviction lever read the gate/finding fixtures override per axis.
_NEUTRAL_LEVER_READ = ConvictionLeverRead(
    label="forced-emergency lever",
    tactic="emergency",
    games=2,
    meetings=2,
    validity_passed=True,
    referee_passed=False,
    supply_floors_passed=False,
    mean_score=1.0,
    mean_episode_predicted_supply=1.0,
    mean_episode_actual_flags=1.0,
    conviction_term=0.5,
    conviction_term_delta=0.0,
    predicted_supply_gain=0.0,
    actual_supply_gain=0.0,
    predicted_flags_per_meeting=1.0,
    actual_flags_per_meeting=1.0,
    predicted_converting_share=0.0,
    predicted_mean_conversion_prob=0.0,
    actual_converting_share=0.0,
    prescreen_flags_pass=False,
    prescreen_conversion_pass=False,
    prescreen_floors_pass=False,
    prescreen_advisory_only=False,
    launders_supply=False,
    materiality_arithmetic="neutral read",
)


def _lever_read(**overrides: bool | float | str) -> ConvictionLeverRead:
    """One conviction lever read with neutral defaults (override per axis)."""

    return _NEUTRAL_LEVER_READ.model_copy(update=overrides)


def test_gate_check_flags_prediction_laundering() -> None:
    # The composed-gate check splits on the BASELINE-RELATIVE gate convention: a
    # predicted-PASS / recorded-FAIL divergence is LAUNDERING only when the
    # honest scripted baseline does not share it (a lever flipped the gate).

    # A clean honest baseline — its predicted floors do NOT pass, so no lever's
    # divergence is shared by it.
    clean_baseline = _lever_read(
        tactic="fsm-baseline",
        validity_passed=True,
        prescreen_floors_pass=False,
        supply_floors_passed=False,
    )
    # A lever that FLIPS the predicted gate (predicted PASS / recorded FAIL) the
    # honest baseline does not — the true laundering seam.
    laundered_read = _lever_read(
        tactic="emergency",
        validity_passed=True,
        prescreen_floors_pass=True,
        supply_floors_passed=False,
    )
    # The reverse divergence (predicted FAIL, recorded PASS) is an efficiency
    # loss — false_blocked, never a blocker.
    false_blocked_read = _lever_read(
        tactic="kill",
        validity_passed=True,
        prescreen_floors_pass=False,
        supply_floors_passed=True,
    )
    # An inadmissible set with the laundering pattern is excluded from all three
    # (validity-gated).
    invalid_read = _lever_read(
        tactic="sabotage",
        validity_passed=False,
        prescreen_floors_pass=True,
        supply_floors_passed=False,
    )
    gate = _build_gate_check(
        (clean_baseline, laundered_read, false_blocked_read, invalid_read),
        prescreen_is_gating=True,
    )
    assert gate.laundered == ("emergency",)
    assert gate.substrate_divergent == ()
    assert gate.false_blocked == ("kill",)
    assert "sabotage" not in gate.laundered
    assert "sabotage" not in gate.substrate_divergent
    assert "sabotage" not in gate.false_blocked
    assert "PREDICTION-LAUNDERED" in gate.verdict

    # When the HONEST baseline diverges too, no lever flipped anything: all
    # divergent tactics (baseline included) land in substrate_divergent and
    # laundered is empty — the substrate speaking, not a lever flip.
    diverging_baseline = _lever_read(
        tactic="fsm-baseline",
        validity_passed=True,
        prescreen_floors_pass=True,
        supply_floors_passed=False,
    )
    substrate = _build_gate_check(
        (diverging_baseline, laundered_read), prescreen_is_gating=True
    )
    assert substrate.laundered == ()
    assert substrate.substrate_divergent == ("fsm-baseline", "emergency")
    assert "SUBSTRATE-DIVERGENT" in substrate.verdict

    # The check REQUIRES the scripted-FSM baseline read — a divergence is
    # measured against it, never in isolation.
    with pytest.raises(ValueError):
        _build_gate_check((laundered_read,), prescreen_is_gating=True)


def test_gate_laundering_becomes_named_finding() -> None:
    # The laundered case (a lever flips the predicted gate past a clean honest
    # baseline) becomes a NAMED prescreen-gate-laundering finding whose blocker
    # names the tactic and roster; a launders_supply read becomes a
    # conviction-supply-laundering finding; the baseline itself is skipped.
    clean_baseline = _lever_read(
        tactic="fsm-baseline",
        validity_passed=True,
        prescreen_floors_pass=False,
        supply_floors_passed=False,
        launders_supply=False,
    )
    gate_laundered = _lever_read(
        tactic="emergency",
        validity_passed=True,
        prescreen_floors_pass=True,
        supply_floors_passed=False,
        launders_supply=False,
    )
    supply_laundered = _lever_read(
        tactic="kill",
        launders_supply=True,
        validity_passed=True,
        prescreen_floors_pass=False,
        supply_floors_passed=False,
    )
    reads = (clean_baseline, gate_laundered, supply_laundered)
    gate_check = _build_gate_check(reads, prescreen_is_gating=True)
    findings = _build_conviction_findings(
        reads, gate_check=gate_check, roster_key="4p1i"
    )
    assert len(findings) == 2
    by_mechanism = {finding.mechanism: finding for finding in findings}
    assert set(by_mechanism) == {
        "conviction-supply-laundering",
        "prescreen-gate-laundering",
    }
    gate_finding = by_mechanism["prescreen-gate-laundering"]
    assert gate_finding.tactic == "emergency"
    assert "emergency" in gate_finding.blocker
    assert "4p1i" in gate_finding.blocker
    assert by_mechanism["conviction-supply-laundering"].tactic == "kill"
    assert all(finding.tactic != "fsm-baseline" for finding in findings)

    # The substrate case (the honest baseline shares the divergence) emits ONE
    # aggregate prescreen-substrate-divergence finding — no per-lever gate
    # finding, the baseline-shared divergence folded into a single named seam.
    diverging_baseline = _lever_read(
        tactic="fsm-baseline",
        validity_passed=True,
        prescreen_floors_pass=True,
        supply_floors_passed=False,
        launders_supply=False,
    )
    diverging_lever = _lever_read(
        tactic="emergency",
        validity_passed=True,
        prescreen_floors_pass=True,
        supply_floors_passed=False,
        launders_supply=False,
    )
    substrate_reads = (diverging_baseline, diverging_lever)
    substrate_gate = _build_gate_check(substrate_reads, prescreen_is_gating=True)
    substrate_findings = _build_conviction_findings(
        substrate_reads, gate_check=substrate_gate, roster_key="4p1i"
    )
    assert len(substrate_findings) == 1
    assert substrate_findings[0].mechanism == "prescreen-substrate-divergence"
    assert substrate_findings[0].tactic == "fsm-baseline+emergency"
    assert "4p1i" in substrate_findings[0].blocker


def test_conviction_path_requires_a_go_verdict(tmp_path: Path) -> None:
    # The arms attack the LIVE 18.16 term; under a committed NO-GO the term is
    # structurally absent, so the entry point fails loud BEFORE any ES work (the
    # loader runs first). Build a NO-GO bundle by copying the committed
    # weights/sha/cap unchanged (keeps the sha-coherence checks passing) and
    # rewriting only verdict.json's verdict fields.
    for filename in (WEIGHTS_FILENAME, WEIGHTS_SHA256_FILENAME, STALENESS_FILENAME):
        shutil.copy(_CONVICTION_ARTIFACT_DIR / filename, tmp_path / filename)
    verdict = json.loads((_CONVICTION_ARTIFACT_DIR / VERDICT_FILENAME).read_text())
    verdict["verdict"] = "NO-GO"
    verdict["fitness_term"] = "absent"
    verdict["prescreen_role"] = "advisory"
    verdict["model_role"] = "diagnostic-only"
    verdict["meets_spearman_bar"] = False
    verdict["meets_conversion_bar"] = False
    (tmp_path / VERDICT_FILENAME).write_text(json.dumps(verdict, sort_keys=True) + "\n")
    with pytest.raises(ValueError, match="NO-GO"):
        run_conviction_path_probe(
            config=_TINY,
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            materiality_bar=0.25,
            conviction_artifact_dir=tmp_path,
        )


def test_conviction_reader_determinism_at_unit_level() -> None:
    # The entry point's determinism is pinned at the UNIT level (a second full
    # run is too slow): the env is a pure function of the seed and the weights
    # are frozen, so two independent _ConvictionArmReader reads of the same
    # forced genome — each with its own fresh counter — produce byte-identical
    # reads (the frozen dataclass equality pins predictions, labels, and the
    # pre-screen booleans together).
    def _read_emergency() -> _ConvictionSetRead:
        term = load_conviction_fitness_term(_CONVICTION_ARTIFACT_DIR)
        assert term is not None  # the committed verdict is GO
        reader = _ConvictionArmReader(
            num_players=4,
            num_impostors=1,
            tasks_per_crewmate=1,
            fitness_seeds=(0, 1),
            baseline_id="baseline-6",
            term=term,
            conviction_artifact_dir=_CONVICTION_ARTIFACT_DIR,
        )
        return reader.read(
            _forced_genome("emergency"),
            label="forced-emergency lever",
            tactic="emergency",
        )

    assert _read_emergency() == _read_emergency()
