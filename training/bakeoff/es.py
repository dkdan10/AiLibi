"""The shared strict-typed evolution-strategy core (Task 15.14).

A ``(1 + λ)`` evolution strategy ported from the ml-spike's pure-Python loop
(``experiments/lab/ml_spike/check2_learnability.py::es`` — the spike is
mypy-excluded and NOT imported). Task 15.14 lands it so 15.15 (the impostor
bake-off) and 15.16 (the crew track) extend ONE audited optimizer behind their
dependency edge; the Goodhart probe (:mod:`training.bakeoff.goodhart`) is its
first client.

The loop, per generation:

1. mutate the incumbent champion ``population`` times (isotropic Gaussian, σ);
2. evaluate every offspring's fitness (K-seed averaged — see below);
3. keep the strictly-better offspring, else the incumbent (elitism), breaking
   ties among offspring LEXICALLY on the genome (deterministic argmax).

Three properties the task contract pins:

* **Deterministic under seed.** Every mutation RNG stream is derived purely from
  ``ESConfig.seed`` + the generation and member indices (no wall-clock, no global
  RNG, no ``numpy`` BLAS reduction), and the fitness function is required to be a
  pure function of the genome. So two identical runs produce identical champion
  genomes AND identical fitness traces — :meth:`ESResult.digest` hashes both and
  the test pins the digest. numpy is *permitted* by the task but deliberately
  unused: a pure-Python ``random.Random`` stream is bit-stable across machines /
  thread counts where BLAS is not (the ``training.env`` inference-path posture).
* **K-seed fitness averaging.** Chaotic per-seed fitness (the spike's check-2
  lesson: a genome's kills swing seed-to-seed) is averaged over a fixed K-seed set
  before selection. :func:`k_seed_mean` binds a per-seed evaluator to
  ``ESConfig.fitness_seeds`` and is the reusable averaging entry point 15.15's
  per-episode reward rides; a caller with an already-set-level fitness (the
  Goodhart probe scores a whole replay SET through the referee at once) passes a
  plain genome→scalar :data:`FitnessFn` instead.
* **Lexical tie-break.** When two offspring tie for best fitness the
  lexicographically-smallest genome wins (a total order over the float tuple), and
  an offspring only displaces the champion on a STRICT improvement — so the argmax
  is reproducible and the champion never drifts across equal-fitness genomes.
"""

from __future__ import annotations

import hashlib
import math
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, field_validator

# A fitness maps a genome to a scalar an optimizer MAXIMIZES. It MUST be a pure
# function of the genome (deterministic) — the ES core derives every other source
# of randomness from the seed, so a non-deterministic fitness is the only way to
# break the double-run digest.
FitnessFn: TypeAlias = Callable[[tuple[float, ...]], float]

# A per-seed fitness maps (genome, seed) to a scalar; :func:`k_seed_mean` averages
# it over a fixed seed set into a :data:`FitnessFn`.
SeedFitnessFn: TypeAlias = Callable[[tuple[float, ...], int], float]


class ESConfig(BaseModel):
    """The ``(1 + λ)`` ES hyper-parameters (Task 15.14 public type).

    Frozen + ``extra="forbid"`` so a config deserialized from a report / CLI fails
    loud on an unknown or missing knob rather than silently defaulting. Downstream
    tasks (15.15/15.16) import this symbol; keep the signature stable.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    generations: int
    population: int
    sigma: float
    seed: int
    fitness_seeds: tuple[int, ...]
    init_scale: float = 0.5

    @field_validator("generations", "population")
    @classmethod
    def _positive_int(cls, value: int) -> int:
        if value < 1:
            raise ValueError("generations and population must be >= 1")
        return value

    @field_validator("sigma", "init_scale")
    @classmethod
    def _positive_float(cls, value: float) -> float:
        if not value > 0.0:
            raise ValueError("sigma and init_scale must be > 0")
        return value

    @field_validator("fitness_seeds")
    @classmethod
    def _nonempty_unique_seeds(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if not value:
            raise ValueError("fitness_seeds must be non-empty (K >= 1)")
        if len(set(value)) != len(value):
            raise ValueError(
                f"fitness_seeds must be unique, got {value!r}: a duplicate seed "
                "silently double-weights the K-seed average, and a replay-set "
                "evaluator keyed on the seed overwrites that seed's games — the "
                "stated K-seed budget would be a lie"
            )
        return value


def k_seed_mean(evaluate: SeedFitnessFn, seeds: Sequence[int]) -> FitnessFn:
    """Bind a per-seed evaluator into a K-seed-averaged :data:`FitnessFn`.

    ``fitness(genome) = mean_s evaluate(genome, s)`` over ``seeds`` — the built-in
    averaging that tames chaotic per-seed fitness before selection (the spike's
    check-2 lesson). ``math.fsum`` keeps the mean order-stable so the averaged
    fitness is bit-reproducible. Raises on an empty seed set (an un-averaged
    fitness is never a silent fallback) and on duplicate seeds (a silent
    double-weighting of one seed's games).
    """

    seed_tuple = tuple(seeds)
    if not seed_tuple:
        raise ValueError("k_seed_mean requires at least one seed")
    if len(set(seed_tuple)) != len(seed_tuple):
        raise ValueError(
            f"k_seed_mean requires unique seeds, got {seed_tuple!r}: a duplicate "
            "seed silently double-weights that seed in the K-seed average"
        )

    def fitness(genome: tuple[float, ...]) -> float:
        return math.fsum(evaluate(genome, seed) for seed in seed_tuple) / len(
            seed_tuple
        )

    return fitness


@dataclass(frozen=True)
class ESResult:
    """The champion + full trace of one ES run (Task 15.14).

    ``fitness_trace`` is the incumbent champion's fitness after each generation
    (index 0 = the seeded initial genome, so its length is
    ``generations + 1``); ``generation_best`` is the best OFFSPRING fitness each
    generation (length ``generations``), which the probe diffs against the
    champion trace to attribute every improvement; ``champion_trace`` is the
    champion genome after each generation, so a client can re-score any
    intermediate champion. :meth:`digest` hashes the champion + fitness trace —
    the double-run determinism pin.
    """

    champion: tuple[float, ...]
    champion_fitness: float
    fitness_trace: tuple[float, ...]
    generation_best: tuple[float, ...]
    champion_trace: tuple[tuple[float, ...], ...]
    num_evaluations: int

    def digest(self) -> str:
        """SHA-256 over the champion genome + fitness trace (exact float hex)."""

        hasher = hashlib.sha256()
        hasher.update(b"champion:")
        for gene in self.champion:
            hasher.update(float(gene).hex().encode("utf-8"))
            hasher.update(b",")
        hasher.update(b"trace:")
        for value in self.fitness_trace:
            hasher.update(float(value).hex().encode("utf-8"))
            hasher.update(b",")
        return hasher.hexdigest()


def _derive_seed(master_seed: int, generation: int, member: int) -> int:
    """A deterministic mutation seed for one (generation, member) offspring.

    Pure function of the master seed + indices (SHA-256 mixed into a 64-bit int),
    so the offspring stream is reproducible and independent of iteration order —
    the double-run genomes are bit-identical.
    """

    payload = f"{master_seed}:{generation}:{member}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _mutate(genome: tuple[float, ...], *, seed: int, sigma: float) -> tuple[float, ...]:
    """Isotropic Gaussian mutation via a pure-Python (bit-stable) RNG stream."""

    rng = random.Random(seed)
    return tuple(gene + rng.gauss(0.0, sigma) for gene in genome)


def _random_genome(length: int, *, seed: int, scale: float) -> tuple[float, ...]:
    rng = random.Random(seed)
    return tuple(rng.gauss(0.0, scale) for _ in range(length))


def _finite_fitness(value: float, *, context: str) -> float:
    """Fail loud on a non-finite fitness (AGENTS.md no silent fallbacks).

    A ``NaN`` / ``inf`` fitness from a downstream reward (a divide-by-zero term,
    an ``exp`` overflow) would poison selection — ``NaN`` breaks the ``key <
    best_offspring_key`` tuple ordering and silently corrupts the champion, trace,
    and digest. The ES core refuses it rather than record a meaningless champion.
    """

    if not math.isfinite(value):
        raise ValueError(
            f"fitness returned a non-finite value {value!r} for {context}; a shared "
            "optimizer refuses NaN/inf fitness rather than corrupt the champion trace"
        )
    return value


def evolve(
    fitness: FitnessFn,
    *,
    genome_length: int,
    config: ESConfig,
    initial_genome: Sequence[float] | None = None,
) -> ESResult:
    """Run the ``(1 + λ)`` ES and return the champion + full trace (Task 15.14).

    ``fitness`` MUST be a pure function of the genome (wrap a per-seed evaluator
    with :func:`k_seed_mean` for the built-in K-seed averaging). The incumbent
    champion seeds generation 0 (either ``initial_genome`` or a
    ``config.seed``-drawn Gaussian genome); each subsequent generation mutates it
    ``config.population`` times, keeps the strictly-better offspring (lexical
    tie-break among offspring), and records the champion's fitness + genome.
    Deterministic under ``config.seed`` — two identical runs return an equal
    :class:`ESResult` (and equal :meth:`ESResult.digest`).
    """

    if genome_length < 1:
        raise ValueError(f"genome_length must be >= 1, got {genome_length}")

    if initial_genome is None:
        champion = _random_genome(
            genome_length, seed=config.seed, scale=config.init_scale
        )
    else:
        champion = tuple(float(gene) for gene in initial_genome)
        if len(champion) != genome_length:
            raise ValueError(
                f"initial_genome length {len(champion)} != genome_length "
                f"{genome_length}"
            )

    champion_fitness = _finite_fitness(fitness(champion), context="initial genome")
    num_evaluations = 1
    fitness_trace: list[float] = [champion_fitness]
    champion_trace: list[tuple[float, ...]] = [champion]
    generation_best: list[float] = []

    for generation in range(config.generations):
        # Evaluate this generation's offspring, tracking the best by the total
        # order (fitness DESC, genome ASC) so the argmax is a deterministic
        # lexical tie-break rather than an iteration-order accident.
        best_offspring: tuple[float, ...] | None = None
        best_offspring_fitness = -math.inf
        best_offspring_key: tuple[float, tuple[float, ...]] | None = None
        for member in range(config.population):
            candidate = _mutate(
                champion,
                seed=_derive_seed(config.seed, generation, member),
                sigma=config.sigma,
            )
            value = _finite_fitness(
                fitness(candidate),
                context=f"generation {generation} member {member}",
            )
            num_evaluations += 1
            key = (-value, candidate)
            if best_offspring_key is None or key < best_offspring_key:
                best_offspring_key = key
                best_offspring = candidate
                best_offspring_fitness = value

        generation_best.append(best_offspring_fitness)
        # Elitism: an offspring only displaces the champion on a STRICT
        # improvement, so the incumbent wins fitness ties and never drifts.
        if best_offspring is not None and best_offspring_fitness > champion_fitness:
            champion = best_offspring
            champion_fitness = best_offspring_fitness
        fitness_trace.append(champion_fitness)
        champion_trace.append(champion)

    return ESResult(
        champion=champion,
        champion_fitness=champion_fitness,
        fitness_trace=tuple(fitness_trace),
        generation_best=tuple(generation_best),
        champion_trace=tuple(champion_trace),
        num_evaluations=num_evaluations,
    )


__all__ = [
    "ESConfig",
    "ESResult",
    "FitnessFn",
    "SeedFitnessFn",
    "evolve",
    "k_seed_mean",
]
