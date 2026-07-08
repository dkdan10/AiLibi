"""Tests for the adversarial Goodhart probe (Task 15.14).

Exercises the probe machinery on a TINY 4p1i budget (the flat determinism/leak
roster — short games, fast), not the committed report budget: the point is the
selector-is-always-legal invariant, the determinism of the run, and the
report/verdict shape, not a full attack.
"""

from __future__ import annotations

import random

from training.bakeoff.es import ESConfig
from training.bakeoff.goodhart import (
    GoodhartProbeReport,
    ProbeExploit,
    TraceImprovement,
    build_probe_selector,
    probe_genome_length,
    run_goodhart_probe,
)
from training.env import TacticalRolloutEnv

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
        assert improvement.moving_term in ("d1", "d2", "d3", "d4", "floor")
        assert improvement.behavioral_cause


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
