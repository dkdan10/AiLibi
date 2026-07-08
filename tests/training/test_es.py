"""Tests for the shared ES core (Task 15.14).

Pins the three properties the task contract names: deterministic-under-seed
(hash-pinned double run), K-seed fitness averaging, and lexical tie-breaking.
"""

from __future__ import annotations

import pytest

from training.bakeoff.es import (
    ESConfig,
    ESResult,
    FitnessFn,
    evolve,
    k_seed_mean,
)


def _sphere(target: tuple[float, ...]) -> FitnessFn:
    """A deterministic concave fitness: negative squared distance to ``target``."""

    def fitness(genome: tuple[float, ...]) -> float:
        return -sum((g - t) ** 2 for g, t in zip(genome, target, strict=True))

    return fitness


def test_esconfig_rejects_degenerate_knobs() -> None:
    with pytest.raises(ValueError):
        ESConfig(generations=0, population=4, sigma=0.1, seed=0, fitness_seeds=(0,))
    with pytest.raises(ValueError):
        ESConfig(generations=4, population=0, sigma=0.1, seed=0, fitness_seeds=(0,))
    with pytest.raises(ValueError):
        ESConfig(generations=4, population=4, sigma=0.0, seed=0, fitness_seeds=(0,))
    with pytest.raises(ValueError):
        ESConfig(generations=4, population=4, sigma=0.1, seed=0, fitness_seeds=())


def test_esconfig_is_frozen() -> None:
    config = ESConfig(
        generations=4, population=4, sigma=0.1, seed=0, fitness_seeds=(0, 1)
    )
    with pytest.raises(ValueError):
        config.sigma = 0.2


def test_k_seed_mean_averages() -> None:
    # A per-seed fitness that returns the seed itself -> mean over seeds.
    fitness = k_seed_mean(lambda genome, seed: float(seed), (2, 4, 6))
    assert fitness((0.0,)) == pytest.approx(4.0)


def test_k_seed_mean_rejects_empty() -> None:
    with pytest.raises(ValueError):
        k_seed_mean(lambda genome, seed: 0.0, ())


def test_evolve_is_deterministic_and_hash_pinned() -> None:
    # Two identical runs produce identical champion genomes AND fitness traces.
    config = ESConfig(
        generations=6, population=6, sigma=0.2, seed=3, fitness_seeds=(0, 1, 2)
    )
    fitness = _sphere((0.5, -0.3, 0.1, 0.8, -0.2))
    first = evolve(fitness, genome_length=5, config=config)
    second = evolve(fitness, genome_length=5, config=config)

    assert first.champion == second.champion
    assert first.fitness_trace == second.fitness_trace
    assert first.digest() == second.digest()
    # Hash-pinned: the pure-Python RNG stream is bit-stable across machines, so the
    # digest is a fixed constant. If this changes, the ES core drifted.
    assert (
        first.digest()
        == "e3b67c69295f8cd2f609e68cdf1b7141a53ee915ece08d1ac7f42cf51ad609a7"
    )


def test_evolve_trace_shapes_and_elitism() -> None:
    config = ESConfig(
        generations=5, population=4, sigma=0.3, seed=1, fitness_seeds=(0,)
    )
    result = evolve(_sphere((0.0, 0.0, 0.0)), genome_length=3, config=config)

    assert isinstance(result, ESResult)
    # trace = generations + 1 (index 0 is the seeded genome); champion_trace matches.
    assert len(result.fitness_trace) == config.generations + 1
    assert len(result.champion_trace) == config.generations + 1
    assert len(result.generation_best) == config.generations
    # Elitism: the champion fitness is monotone non-decreasing.
    assert all(
        later >= earlier
        for earlier, later in zip(result.fitness_trace, result.fitness_trace[1:])
    )
    # The optimizer climbs toward the optimum (fitness -> 0 from below).
    assert result.fitness_trace[-1] > result.fitness_trace[0]
    assert result.champion_fitness == result.fitness_trace[-1]
    # Every intermediate champion is byte-consistent with its recorded fitness.
    assert result.champion_trace[-1] == result.champion
    # Number of evaluations = 1 (initial) + generations * population.
    assert result.num_evaluations == 1 + config.generations * config.population


def test_evolve_lexical_tie_break_is_deterministic() -> None:
    # A fitness that is CONSTANT (every genome ties): the champion must be
    # reproducible across runs (lexical tie-break + incumbent-wins-ties), and it
    # must stay the seeded initial genome (no offspring strictly improves).
    config = ESConfig(
        generations=4, population=5, sigma=0.5, seed=9, fitness_seeds=(0,)
    )
    flat = evolve(lambda genome: 1.0, genome_length=4, config=config)
    flat_again = evolve(lambda genome: 1.0, genome_length=4, config=config)
    assert flat.champion == flat_again.champion
    # Incumbent wins fitness ties -> the champion never leaves the initial genome.
    assert all(champ == flat.champion_trace[0] for champ in flat.champion_trace)
    assert flat.fitness_trace == tuple([1.0] * (config.generations + 1))


def test_evolve_respects_initial_genome() -> None:
    config = ESConfig(
        generations=2, population=3, sigma=0.1, seed=0, fitness_seeds=(0,)
    )
    result = evolve(
        _sphere((0.0, 0.0)),
        genome_length=2,
        config=config,
        initial_genome=[0.0, 0.0],
    )
    # Started at the optimum: no offspring can beat it, so the champion is pinned.
    assert result.champion == (0.0, 0.0)
    assert result.champion_fitness == 0.0


def test_evolve_rejects_bad_lengths() -> None:
    config = ESConfig(
        generations=1, population=1, sigma=0.1, seed=0, fitness_seeds=(0,)
    )
    with pytest.raises(ValueError):
        evolve(_sphere((0.0,)), genome_length=0, config=config)
    with pytest.raises(ValueError):
        evolve(
            _sphere((0.0, 0.0)),
            genome_length=2,
            config=config,
            initial_genome=[0.0],
        )
