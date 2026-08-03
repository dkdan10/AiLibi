"""Tests for the shared ES core (Task 15.14; portable sampler, Task 19.3).

Pins the three properties the 15.14 task contract names: deterministic-under-seed
(hash-pinned double run), K-seed fitness averaging, and lexical tie-breaking — plus
the 19.3 sampler pins: the replacement normal sampler is built only from portable
operations AND is provably Gaussian (an approximation check against an independent
``math.erfc`` reference, and distribution-quality assertions over a fixed stream), so
a portable-but-degenerate sampler cannot silently replace the isotropic mutation
distribution the module documents.
"""

from __future__ import annotations

import ast
import inspect
import math
import random
import statistics
from collections.abc import Sequence

import pytest

from training.bakeoff import es as es_module

# The sampler internals are private on purpose (one sampler, one stream — no second
# entry point for callers to reach), but the 19.3 contract pins their behaviour, so
# this module tests them directly.
from training.bakeoff.es import (
    _LN2_HI,
    _LN2_LO,
    ESConfig,
    ESResult,
    FitnessFn,
    _ln,
    _normal_quantile,
    _standard_normal,
    evolve,
    k_seed_mean,
    mutate_genome,
)


def _sphere(target: tuple[float, ...]) -> FitnessFn:
    """A deterministic concave fitness: negative squared distance to ``target``.

    Squares as ``d * d``, not ``d ** 2``: float ``**`` is libm ``pow``, and the
    pinned digest below hashes the FITNESS trace as well as the champion, so a
    caller-side libm call would put the same portability hazard back into the pin
    that Task 19.3 took out of the sampler. (Both spellings agree bit-for-bit on
    this host — the digest is unchanged by the switch — but only one of them is
    guaranteed to.)
    """

    def fitness(genome: tuple[float, ...]) -> float:
        return -sum((g - t) * (g - t) for g, t in zip(genome, target, strict=True))

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


def test_esconfig_rejects_duplicate_seeds() -> None:
    # A duplicate seed silently double-weights the K-seed average — and a
    # replay-set evaluator keyed on the seed overwrites that seed's games, so the
    # stated K-seed budget would be a lie. Fail loud at config time.
    with pytest.raises(ValueError):
        ESConfig(
            generations=4, population=4, sigma=0.1, seed=0, fitness_seeds=(0, 1, 0)
        )


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


def test_k_seed_mean_rejects_duplicate_seeds() -> None:
    with pytest.raises(ValueError):
        k_seed_mean(lambda genome, seed: 0.0, (2, 4, 2))


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
    # Hash-pinned. Scope of the pin (es.py "Reproducibility scope", Task 19.3):
    #   * same-runtime repeatability is GUARANTEED — this constant must hold for
    #     every run of this interpreter build on this host;
    #   * cross-platform bit-identity is DESIGNED FOR but NOT YET CONFIRMED. The
    #     sampler uses only IEEE-754-correctly-rounded operations, so the digest
    #     SHOULD be the same everywhere, but so far it has only been observed on
    #     Linux/x86-64. Darwin-arm64 (the host that recorded the OLD stream's
    #     divergence — tasks/phase-18.md:2656-2659 and the Codex phase-19 audit,
    #     audits/audit-phase-19-triage.md C1 + §8 row 1) has NOT been run against
    #     this constant yet; that owner-assisted run is what would upgrade the
    #     module's claim from "designed-portable" to "portable". Record the result
    #     here when it happens.
    # The constant moved at Task 19.3 (previous value
    # e3b67c69295f8cd2f609e68cdf1b7141a53ee915ece08d1ac7f42cf51ad609a7): swapping
    # libm-backed `rng.gauss` for the in-module inverse-CDF sampler changes the
    # offspring stream, so this is a DELIBERATE, documented ES drift — the golden
    # pins the optimizer stream, not any shipped artifact, and no artifact was
    # retrained. If this pin ever trips WITHOUT such a documented change, the ES
    # core drifted: investigate, do not re-pin.
    assert (
        first.digest()
        == "e72e24fe30d58f8ba573550b3d7aa4ec90a50d541669f22608ecdc6ff55024a8"
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


def test_evolve_rejects_non_finite_fitness() -> None:
    # A shared optimizer must fail loud on NaN/inf fitness (bad downstream reward
    # math) rather than record a meaningless champion / poisoned digest.
    config = ESConfig(
        generations=3, population=3, sigma=0.2, seed=0, fitness_seeds=(0,)
    )
    with pytest.raises(ValueError):
        evolve(lambda genome: float("nan"), genome_length=2, config=config)

    # A non-finite fitness that appears only for an offspring is also caught.
    calls = {"n": 0}

    def fitness_nan_after_first(genome: tuple[float, ...]) -> float:
        calls["n"] += 1
        return 0.0 if calls["n"] == 1 else float("inf")

    with pytest.raises(ValueError):
        evolve(fitness_nan_after_first, genome_length=2, config=config)


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


# --------------------------------------------------------------------------- #
# The portable normal sampler (Task 19.3).                                      #
#                                                                               #
# The old sample path called ``random.Random.gauss``, whose Box-Muller draw      #
# rides math.log/cos/sin — libm, which IEEE-754 does NOT require to round        #
# correctly — and the digest pin above was green on Linux and red on             #
# Darwin-arm64 twice. The replacement is an in-module inverse-CDF sampler        #
# (Wichura AS241 over a pure-arithmetic ``_ln``). These tests hold it to BOTH    #
# halves of the bargain: portable by construction (no libm transcendental        #
# anywhere in the module) and actually GAUSSIAN — approximation error against    #
# an independent ``math.erfc`` reference, plus distribution-quality pins over    #
# the fixed stream, so a portable-but-degenerate sampler cannot quietly take     #
# the place of the documented isotropic mutation distribution.                   #
# --------------------------------------------------------------------------- #

_SQRT2: float = math.sqrt(2.0)

# The fixed stream every distribution assertion below reads: 40k draws through the
# SHIPPED operator (``mutate_genome`` off a zero genome), at a non-unit sigma so the
# scale is exercised too. Fixed seed -> these are deterministic assertions, not
# flaky statistics: each tolerance is >= 4 standard errors wide at this N, so a
# faithful sampler passes with room while a degenerate one (constant, uniform,
# truncated, mis-scaled) misses by orders of magnitude.
_STREAM_SIZE: int = 40_000
_STREAM_SIGMA: float = 2.5
_STREAM_SEED: int = 190301


def _normal_cdf(x: float) -> float:
    """``Phi(x)`` via ``math.erfc`` — the reference route ``es.py`` never takes."""

    return 0.5 * math.erfc(-x / _SQRT2)


def _reference_quantile(p: float) -> float:
    """``Phi^-1(p)`` for ``0 < p <= 0.5`` by bisecting :func:`_normal_cdf`.

    Wholly independent of AS241: it inverts the ``erfc``-based CDF numerically. Only
    the lower half is bracketed — above ``p = 0.5`` the CDF saturates against 1.0 and
    a bisection reference would measure float cancellation rather than the sampler
    (the quantile's own antisymmetry test covers the upper half).
    """

    low, high = -40.0, 0.5
    for _ in range(200):
        mid = 0.5 * (low + high)
        if _normal_cdf(mid) < p:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


def _stream() -> tuple[float, ...]:
    """The pinned sampler stream, drawn through the shipped mutation operator."""

    return mutate_genome((0.0,) * _STREAM_SIZE, seed=_STREAM_SEED, sigma=_STREAM_SIGMA)


class _ScriptedRandom(random.Random):
    """A ``random.Random`` whose ``random()`` replays a fixed script of draws."""

    def __init__(self, draws: Sequence[float]) -> None:
        super().__init__(0)
        self._draws = tuple(draws)
        self.consumed = 0

    def random(self) -> float:
        value = self._draws[self.consumed]
        self.consumed += 1
        return value


def _called_names(source: str) -> set[str]:
    """Every function/method name CALLED in ``source`` (docstrings excluded)."""

    called: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute):
            called.add(node.func.attr)
        elif isinstance(node.func, ast.Name):
            called.add(node.func.id)
    return called


def test_sample_path_calls_no_libm_transcendental() -> None:
    # The portability property is a property of the CODE, not of a comment: every
    # libm transcendental is unimplementable portably (C leaves their last ulp to
    # the vendor), and `rng.gauss` is exactly how they got in. Guard the module by
    # parsing it — a docstring may name `math.log`, a CALL may not.
    source = inspect.getsource(es_module)
    called = _called_names(source)
    forbidden = {
        # libm transcendentals: not correctly rounded, platform-dependent.
        "log",
        "log1p",
        "log2",
        "log10",
        "exp",
        "expm1",
        "pow",
        "cos",
        "sin",
        "tan",
        "acos",
        "asin",
        "atan",
        "atan2",
        "hypot",
        "cosh",
        "sinh",
        "tanh",
        "erf",
        "erfc",
        "gamma",
        "lgamma",
        # ...and the random.Random samplers built on top of them.
        "gauss",
        "normalvariate",
        "lognormvariate",
        "expovariate",
        "gammavariate",
        "betavariate",
        "vonmisesvariate",
        "paretovariate",
        "weibullvariate",
    }
    assert not called & forbidden, (
        f"{es_module.__name__} calls libm-backed name(s) "
        f"{sorted(called & forbidden)}: the ES stream's portability rests on using "
        "only correctly-rounded IEEE-754 operations — implement the routine "
        "in-module instead (Task 19.3)"
    )
    # The guard is looking at the right file: the portable primitives ARE called.
    assert {"sqrt", "frexp", "random"} <= called
    # `**` on floats is libm `pow` by another name; the module uses `x * x`.
    assert not any(
        isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow)
        for node in ast.walk(ast.parse(source))
    )


def test_ln_matches_libm_to_a_few_ulp() -> None:
    # `_ln` replaces `math.log` in the sample path, so its VALUE is checked against
    # `math.log` here (the test may call libm; the module may not). A few ulp is the
    # whole budget: the series truncation is ~1e-22, so any real deviation means a
    # broken reduction, not an approximation limit.
    assert _LN2_HI + _LN2_LO == math.log(2.0)
    probes = [2.0**-53, 1e-12, 0.01, 0.2, 0.5, _SQRT2 / 2.0, 0.9, 1.0]
    probes += [random.Random(seed).random() for seed in range(2000)]
    probes += [2.0**-exponent * 1.3 for exponent in range(1, 60)]
    for x in probes:
        expected = math.log(x)
        if expected == 0.0:
            assert _ln(x) == 0.0
            continue
        assert abs(_ln(x) - expected) / abs(expected) < 1e-15
    with pytest.raises(ValueError):
        _ln(0.0)
    with pytest.raises(ValueError):
        _ln(-1.0)


def test_normal_quantile_matches_an_independent_erfc_reference() -> None:
    # "Provably Gaussian, not merely deterministic", part 1: the map from uniform to
    # normal IS the normal quantile function, to ~1e-13. Checked two ways against
    # `math.erfc` (which es.py never calls): round-tripping Phi(Phi^-1(p)) back to p
    # over a log grid down to the smallest draw `random()` can return, and a direct
    # comparison against a bisection inverse. Both cover all three AS241 branches:
    # central, near tail (p >= ~1.4e-11) and far tail (below it). The grid stays in
    # the lower half, where the erfc CDF still resolves p (above 0.5 it saturates
    # against 1.0 and a reference built on it would measure cancellation, not the
    # sampler); the upper half is the exact mirror of it — see the antisymmetry test.
    probabilities: list[float] = []
    p = 2.0**-53
    while p < 0.5:
        probabilities.append(p)
        p *= 1.7
    probabilities += [index / 400.0 for index in range(1, 200)]
    for probability in probabilities:
        quantile = _normal_quantile(probability)
        assert abs(_normal_cdf(quantile) - probability) / probability < 1e-12
        reference = _reference_quantile(probability)
        # Absolute near p = 0.5 (the quantile itself goes to zero there, and so does
        # the bisection reference's own resolution), relative out in the tails.
        assert abs(quantile - reference) < 1e-13 + 1e-13 * abs(reference)
    # Textbook percentage points, to the digits the published algorithm claims.
    assert _normal_quantile(0.975) == pytest.approx(1.959963984540054, abs=1e-12)
    assert _normal_quantile(0.995) == pytest.approx(2.5758293035489004, abs=1e-12)
    assert _normal_quantile(0.5) == 0.0
    # The far-tail branch is reachable from a real draw (`random()` bottoms out at
    # 2**-53), so it is pinned rather than left to chance.
    assert _normal_quantile(2.0**-53) == pytest.approx(-8.209536151601386, abs=1e-12)
    # Unbounded outside the open unit interval: raise, never invent a value.
    for bad in (0.0, 1.0, -0.5, 1.5):
        with pytest.raises(ValueError):
            _normal_quantile(bad)


def test_normal_quantile_is_exactly_antisymmetric() -> None:
    # Symmetry by CONSTRUCTION (both tails are evaluated on min(p, 1-p) and mirrored
    # by sign), not merely in distribution: an asymmetric sampler would bias every
    # mutation direction, and the isotropy claim would be false.
    for probability in (0.25, 0.125, 0.0625, 2.0**-10, 2.0**-20, 2.0**-40, 2.0**-53):
        assert _normal_quantile(probability) == -_normal_quantile(1.0 - probability)


def test_standard_normal_takes_one_draw_and_rejects_the_unmappable_zero() -> None:
    # One uniform draw per sample (no cached second variate the way Box-Muller has),
    # so the stream's index arithmetic stays trivial.
    single = _ScriptedRandom([0.25])
    assert _standard_normal(single) == _normal_quantile(0.25)
    assert single.consumed == 1
    # `random()` can return exactly 0.0 (probability 2**-53) and 0.0 has no finite
    # quantile. It is REJECTED and redrawn — a documented rejection step, not a
    # silent clamp to some invented value (AGENTS.md: no silent fallbacks).
    rejecting = _ScriptedRandom([0.0, 0.0, 0.75])
    assert _standard_normal(rejecting) == _normal_quantile(0.75)
    assert rejecting.consumed == 3


def test_sampler_stream_is_gaussian_in_its_moments_and_tails() -> None:
    # "Provably Gaussian, not merely deterministic", part 2: the DISTRIBUTION of the
    # fixed stream. A portable-but-degenerate sampler (constant, uniform, truncated,
    # mis-scaled) is deterministic and would pass the digest pin — it fails here.
    samples = _stream()
    assert len(samples) == _STREAM_SIZE
    standardized = [sample / _STREAM_SIGMA for sample in samples]

    # Mean 0 and variance 1 after de-scaling (4+ standard errors of slack: the SE of
    # the mean is 1/sqrt(N) = 0.005, of the variance sqrt(2/N) = 0.0071).
    assert abs(statistics.fmean(standardized)) < 0.02
    assert abs(statistics.pvariance(standardized) - 1.0) < 0.03
    # Symmetry: the sign split and the median both sit on zero.
    positive = sum(1 for value in standardized if value > 0.0)
    assert abs(positive / _STREAM_SIZE - 0.5) < 0.01
    assert abs(statistics.median(standardized)) < 0.02

    # Sigma-scaled tails: the fraction beyond k*sigma matches erfc(k/sqrt2) — this is
    # what catches a sampler that is normal-ish in the middle but wrong in the tails
    # (or one that ignores sigma), which is precisely where mutation gets its
    # exploration. Tolerances are ~5 SE of a binomial at this N.
    for multiple, tolerance in ((1.0, 0.010), (2.0, 0.005), (3.0, 0.0015)):
        beyond = sum(
            1 for sample in samples if abs(sample) > multiple * _STREAM_SIGMA
        ) / len(samples)
        assert abs(beyond - math.erfc(multiple / _SQRT2)) < tolerance

    # Shape, end to end: the Kolmogorov-Smirnov distance from the exact normal CDF.
    # 1.95/sqrt(N) is the asymptotic 99.9% critical value (0.00975 here).
    ordered = sorted(standardized)
    deviation = max(
        max(
            abs((index + 1) / _STREAM_SIZE - _normal_cdf(value)),
            abs(index / _STREAM_SIZE - _normal_cdf(value)),
        )
        for index, value in enumerate(ordered)
    )
    assert deviation < 1.95 / math.sqrt(_STREAM_SIZE)
