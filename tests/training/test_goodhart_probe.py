"""Tests for the adversarial Goodhart probe (Task 15.14).

Exercises the probe machinery on a TINY 4p1i budget (the flat determinism/leak
roster — short games, fast), not the committed report budget: the point is the
selector-is-always-legal invariant, the determinism of the run, and the
report/verdict shape, not a full attack.
"""

from __future__ import annotations

import random

import pytest

from eval.watchability import WatchabilityGameScore, WatchabilityReport
from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import (
    GoodhartProbeReport,
    ProbeExploit,
    TraceImprovement,
    _build_exploits,
    _decompose_improvement,
    _ExploitCandidate,
    _RefereeAttackEvaluator,
    _SetAggregates,
    _SetEvaluation,
    _sweep_levers,
    build_probe_selector,
    probe_genome_length,
    run_goodhart_probe,
)
from training.env import TacticalRolloutEnv


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
