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
  unused: a pure-Python stream has no BLAS reduction order to drift with thread
  counts (the ``training.env`` inference-path posture). What that pure-Python
  stream does and does NOT promise across MACHINES is stated below.
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

Reproducibility scope of the optimizer stream (Task 19.3)
---------------------------------------------------------

Two scopes, stated separately because only one of them is confirmed. They are the
optimizer half of the three reproducibility scopes the README states repo-wide
(Task 19.1) — the third, replay integrity, is an engine property and is not this
module's to promise; the README's cross-platform scope quotes the outcome below and
the two texts must keep saying the same thing:

* **Same-runtime repeatability — GUARANTEED, and pinned.** Two runs under the same
  interpreter on the same host produce bit-identical champions, traces and digests;
  ``tests/training/test_es.py`` pins the digest as a fixed constant.
* **Cross-platform bit-identity — DESIGNED FOR, NOT YET CONFIRMED.** The sample path
  is built only out of operations IEEE-754 requires to be correctly rounded, so the
  same seed SHOULD yield the same bytes on any conforming platform — but that has
  only been observed on Linux/x86-64. Until an owner-assisted Darwin-arm64 run (the
  recorded failure host) reproduces the pinned digest, cross-platform portability is
  a design property of this module, not a supported guarantee, and no caller should
  rely on it.

Until Task 19.3 this module claimed the stronger, unsupported version of the second
scope verbatim: "a pure-Python ``random.Random`` stream is bit-stable across machines
/ thread counts where BLAS is not". That promise was false in practice — the digest
pin was green on Linux and red on Darwin-arm64 twice (``tasks/phase-18.md:2656-2659``
at the phase-18 close, and the Codex phase-19 audit run,
``audits/audit-phase-19-triage.md`` C1 + §8 row 1).

**What was platform-sensitive** (the verify-then-fix step, recorded here because the
promise it invalidates lived here): the old sample path called
``random.Random.gauss()``, which draws its variate as
``cos(2*pi*u1) * sqrt(-2*log(1-u2))`` (CPython ``Lib/random.py``) — so every gene
rode three libm entry points: ``math.log``, ``math.cos``, ``math.sin``. None of the
three is required by IEEE-754 to be correctly rounded, each platform's libm (glibc
vs Apple's) is free to round its last ulp differently, and selection amplifies a
single-ulp gene difference into a different champion and a different digest. Nothing
else in the stream can drift: ``random.Random`` is MT19937 (integer state, seeded
from an int — pure integer arithmetic), ``random()`` composes a 27-bit and a 26-bit
word as ``(a * 2**26 + b) * 2**-53``, every step of which is exact in float64 (the
sum is below 2**53 and the scaling is by a power of two), and the loop's own
arithmetic is +, -, * and comparisons. So the libm calls were the whole exposure the
sample path had, and removing them is what this module can do about it; the
CONFIRMATION that nothing else in the toolchain diverges is the Darwin-arm64 run the
second scope above is waiting on.

**The replacement** (one sampler, one stream — ``rng.gauss`` is now called nowhere):
:func:`_standard_normal` maps ONE ``rng.random()`` draw through the inverse normal
CDF, Wichura's AS241 ``PPND16``, in +, -, *, / and one ``math.sqrt`` (IEEE-754
requires division and square root to be correctly rounded, so both are portable).
AS241's tail branch needs a logarithm — which libm would supply non-portably — so
:func:`_ln` implements it in-module out of the same correctly-rounded basic ops.
Regenerating the golden digest for the new stream is a deliberate, documented ES
drift (Task 19.3); the ES program is otherwise frozen — no artifact retrains, and the
golden pins the OPTIMIZER stream, not any shipped artifact.
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


# --------------------------------------------------------------------------- #
# The portable normal sampler (Task 19.3).                                      #
#                                                                               #
# ``rng.gauss`` rode libm (``log``/``cos``/``sin``) and is called nowhere in     #
# this module any more — see the module docstring for the divergence record.     #
# Everything below is +, -, *, / and ``math.sqrt`` on float64, which IEEE-754    #
# requires to be correctly rounded, plus ``math.frexp``, which is exact (it      #
# only reads the exponent field). One sampler, one stream.                       #
# --------------------------------------------------------------------------- #

# ``ln(2)`` split hi/lo the way fdlibm's ``e_log.c`` splits it: ``_LN2_HI`` holds
# 30 significant bits, so ``exponent * _LN2_HI`` is EXACT for every exponent a
# float64 can carry (|e| <= 1074 needs 11 bits; 30 + 11 < 53) and the reduction's
# rounding error stays in the small ``_LN2_LO`` term. ``_LN2_HI + _LN2_LO`` is the
# correctly-rounded double nearest ln(2) (asserted by the test).
_LN2_HI: float = 6.93147180369123816490e-01
_LN2_LO: float = 1.90821492927058770002e-10

# The mantissa fold point, ``sqrt(1/2)`` to double precision: folding ``m`` from
# ``[1/2, 1)`` into ``[sqrt(1/2), sqrt(2))`` bounds the series argument at
# ``|s| <= (sqrt(2) - 1) / (sqrt(2) + 1) = 0.1716``.
_SQRT_HALF: float = 0.7071067811865476

# The odd ``atanh`` series ``s + s**3/3 + ... + s**25/25`` divided through by ``s``,
# as a polynomial in ``s**2``, highest degree first. The coefficients are the exact
# rationals ``1 / (2k + 1)`` — computed here rather than transcribed, so there are no
# fitted digits in the logarithm at all, and each is the correctly-rounded double for
# its rational (float division is correctly rounded per IEEE-754, so this tuple is
# itself bit-identical everywhere). Thirteen terms: the first DROPPED term is bounded
# by ``|s|**27 / 27 < 1e-22``, far below the double-precision floor at ``|ln(m)| ~
# 0.35``, so truncation never reaches the result's last bit.
_ATANH_SERIES: tuple[float, ...] = tuple(
    1.0 / float(2 * power + 1) for power in range(12, -1, -1)
)


def _horner(coefficients: tuple[float, ...], x: float) -> float:
    """Evaluate a polynomial at ``x``, coefficients HIGHEST degree first.

    Horner's rule, fixed order: ``((c0 * x + c1) * x + c2) ...``. Only + and *,
    both correctly rounded by IEEE-754, in an order fixed by the tuple — so the
    value is a pure function of the coefficients and ``x`` on any conforming
    platform. Every polynomial in the sampler goes through here, so there is one
    evaluation order to audit rather than one per approximation.
    """

    total = coefficients[0]
    for coefficient in coefficients[1:]:
        total = total * x + coefficient
    return total


def _ln(x: float) -> float:
    """``ln(x)`` for ``x > 0`` in pure IEEE-754 arithmetic — never ``math.log``.

    ``math.log`` is a libm call and libm is not required to round correctly, which
    is exactly how the old stream diverged across platforms (module docstring). The
    sample path needs a logarithm for AS241's tails, so it gets this one instead.

    Algorithm — the textbook ``atanh``-series logarithm:

    1. **Range reduction.** ``math.frexp`` splits ``x = m * 2**e`` with
       ``m in [1/2, 1)`` exactly — it reads the exponent field, so there is no
       arithmetic to round and no libm approximation involved. An ``m`` below
       ``sqrt(1/2)`` is doubled and ``e`` decremented (also exact: a power-of-two
       scaling), leaving ``m in [sqrt(1/2), sqrt(2))``.
    2. **Series.** With ``s = (m - 1) / (m + 1)``, so ``|s| <= 0.1716``,
       ``ln(m) = 2 * atanh(s) = 2 * (s + s**3/3 + s**5/5 + ...)``, evaluated as
       ``2 * s * _horner(_ATANH_SERIES, s * s)``.
    3. **Recombination.** ``ln(x) = e * ln(2) + ln(m)``, with ``ln(2)`` in the
       exact-hi / small-lo split above so the exponent term contributes no rounding
       error of its own.

    Deviation is bounded by the series truncation (``< 1e-22``, see
    :data:`_ATANH_SERIES`) plus a handful of correctly-rounded operations; measured
    against ``math.log``, max relative deviation ~5e-16 (a few ulp) over the whole
    input range this module uses. The test pins that comparison.

    Raises on a non-positive argument (AGENTS.md: no silent fallbacks) — the sample
    path only ever calls it with a strictly positive probability.
    """

    if not x > 0.0:
        raise ValueError(f"_ln requires x > 0, got {x!r}")

    mantissa, exponent = math.frexp(x)
    if mantissa < _SQRT_HALF:
        mantissa *= 2.0
        exponent -= 1

    s = (mantissa - 1.0) / (mantissa + 1.0)
    return exponent * _LN2_HI + (
        2.0 * s * _horner(_ATANH_SERIES, s * s) + exponent * _LN2_LO
    )


# Wichura's AS241 ``PPND16`` coefficients (M. J. Wichura, "Algorithm AS 241: The
# Percentage Points of the Normal Distribution", *Applied Statistics* 37(3):477-484,
# 1988), transcribed from the published algorithm and reordered highest-degree-first
# for :func:`_horner`. The paper writes each denominator with an implicit unit
# constant term; it is spelled out as the trailing ``1.0`` here. Transcription is not
# trusted on inspection: ``tests/training/test_es.py`` re-derives the whole quantile
# function from ``math.erfc`` (which this module never calls) and fails on a mistyped
# digit.
_AS241_CENTRAL_NUMERATOR: tuple[float, ...] = (
    2.5090809287301226727e3,
    3.3430575583588128105e4,
    6.7265770927008700853e4,
    4.5921953931549871457e4,
    1.3731693765509461125e4,
    1.9715909503065514427e3,
    1.3314166789178437745e2,
    3.3871328727963666080e0,
)
_AS241_CENTRAL_DENOMINATOR: tuple[float, ...] = (
    5.2264952788528545610e3,
    2.8729085735721942674e4,
    3.9307895800092710610e4,
    2.1213794301586595867e4,
    5.3941960214247511077e3,
    6.8718700749205790830e2,
    4.2313330701600911252e1,
    1.0,
)
_AS241_NEAR_TAIL_NUMERATOR: tuple[float, ...] = (
    7.74545014278341407640e-4,
    2.27238449892691845833e-2,
    2.41780725177450611770e-1,
    1.27045825245236838258e0,
    3.64784832476320460504e0,
    5.76949722146069140550e0,
    4.63033784615654529590e0,
    1.42343711074968357734e0,
)
_AS241_NEAR_TAIL_DENOMINATOR: tuple[float, ...] = (
    1.05075007164441684324e-9,
    5.47593808499534494600e-4,
    1.51986665636164571966e-2,
    1.48103976427480074590e-1,
    6.89767334985100004550e-1,
    1.67638483018380384940e0,
    2.05319162663775882187e0,
    1.0,
)
_AS241_FAR_TAIL_NUMERATOR: tuple[float, ...] = (
    2.01033439929228813265e-7,
    2.71155556874348757815e-5,
    1.24266094738807843860e-3,
    2.65321895265761230930e-2,
    2.96560571828504891230e-1,
    1.78482653991729133580e0,
    5.46378491116411436990e0,
    6.65790464350110377720e0,
)
_AS241_FAR_TAIL_DENOMINATOR: tuple[float, ...] = (
    2.04426310338993978564e-15,
    1.42151175831644588870e-7,
    1.84631831751005468180e-5,
    7.86869131145613259100e-4,
    1.48753612908506148525e-2,
    1.36929880922735805310e-1,
    5.99832206555887937690e-1,
    1.0,
)


def _normal_quantile(p: float) -> float:
    """The standard-normal inverse CDF ``Phi^-1(p)`` for ``0 < p < 1`` (AS241).

    Wichura's AS241 ``PPND16`` — the standard double-precision probit — as three
    rational approximations selected on ``|p - 0.5|`` and then on the tail's reduced
    argument, each a ratio of two degree-7 polynomials (coefficients above):

    * **central**, ``|p - 0.5| <= 0.425``: in ``r = 0.180625 - (p - 0.5)**2``;
    * **near tail**, ``sqrt(-ln(min(p, 1 - p))) <= 5`` (i.e. down to
      ``p ~ 1.4e-11``): in that root minus 1.6;
    * **far tail**: in that root minus 5 — reachable, because ``random()`` can
      return values as small as ``2**-53``.

    Why each operation is portable: the polynomials are + and * only
    (:func:`_horner`), combined by a single division; IEEE-754 requires division
    and ``math.sqrt`` to be correctly rounded, so both are bit-identical across
    conforming platforms; and the logarithm the tails need is :func:`_ln`, this
    module's pure-arithmetic routine, never ``math.log``. Nothing here reaches libm.

    Accuracy: AS241 ``PPND16``'s published deviation is ~16 significant figures.
    Measured here against an independent ``math.erfc``-inverted reference over
    ``[2**-53, 1 - 2**-53]``: relative deviation under 1e-13 wherever
    ``|Phi^-1(p)| >= 1e-3``, absolute deviation under 1e-14 everywhere (near
    ``p = 0.5`` the quantile itself goes to zero, so the absolute bound is the
    meaningful one — and the reference's own inversion error is inside both
    figures). So the sampler tracks the true Gaussian quantile to within a rounding
    wobble, not merely "some deterministic monotone map". The test pins that
    comparison.

    The two tail branches are evaluated on ``min(p, 1 - p)`` and mirrored by sign,
    so ``Phi^-1(p) = -Phi^-1(1 - p)`` holds EXACTLY whenever ``1 - p`` is exact —
    the sampler is symmetric by construction, not just in distribution.

    Raises outside ``0 < p < 1``: the quantile is unbounded there and
    :func:`_standard_normal` never asks for it (AGENTS.md: no silent fallbacks).
    """

    if not 0.0 < p < 1.0:
        raise ValueError(f"_normal_quantile requires 0 < p < 1, got {p!r}")

    centered = p - 0.5
    if abs(centered) <= 0.425:
        r = 0.180625 - centered * centered
        return (
            centered
            * _horner(_AS241_CENTRAL_NUMERATOR, r)
            / _horner(_AS241_CENTRAL_DENOMINATOR, r)
        )

    r = math.sqrt(-_ln(p if centered < 0.0 else 1.0 - p))
    if r <= 5.0:
        r -= 1.6
        value = _horner(_AS241_NEAR_TAIL_NUMERATOR, r) / _horner(
            _AS241_NEAR_TAIL_DENOMINATOR, r
        )
    else:
        r -= 5.0
        value = _horner(_AS241_FAR_TAIL_NUMERATOR, r) / _horner(
            _AS241_FAR_TAIL_DENOMINATOR, r
        )
    return -value if centered < 0.0 else value


def _standard_normal(rng: random.Random) -> float:
    """One ``N(0, 1)`` draw: :func:`_normal_quantile` of one uniform draw.

    Inverse-CDF sampling — ``Phi^-1(U)`` is standard normal for ``U ~ U(0, 1)`` —
    consuming exactly ONE ``rng.random()`` per sample, which keeps the stream's
    index arithmetic trivial and (unlike ``random.gauss``'s Box-Muller pair) leaves
    no cached second variate to carry state between calls.

    ``random()`` returns ``k / 2**53`` for a uniform 53-bit ``k``, so ``0.0`` is a
    (vanishingly rare, ``2**-53``) possible draw and has no finite quantile. It is
    REJECTED and redrawn — a documented rejection step, not a silent clamp, so the
    sampler never has to invent a value for it. ``1.0`` cannot be drawn.
    """

    uniform = rng.random()
    while uniform <= 0.0:
        uniform = rng.random()
    return _normal_quantile(uniform)


def _mutate(genome: tuple[float, ...], *, seed: int, sigma: float) -> tuple[float, ...]:
    """Isotropic Gaussian mutation over the portable inverse-CDF sampler (19.3)."""

    rng = random.Random(seed)
    return tuple(gene + sigma * _standard_normal(rng) for gene in genome)


def _random_genome(length: int, *, seed: int, scale: float) -> tuple[float, ...]:
    rng = random.Random(seed)
    return tuple(scale * _standard_normal(rng) for _ in range(length))


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


def derive_stream_seed(master_seed: int, *indices: int) -> int:
    """A deterministic 64-bit stream seed for ``(master_seed, *indices)`` (15.15).

    The shared-core extension the bake-off entrants ride for every RNG stream
    that is NOT the ``evolve`` loop's own offspring stream (MAP-Elites parent
    picks / mutations, BC minibatch shuffles): a pure SHA-256 mix of the master
    seed and an arbitrary index path, so two runs derive bit-identical streams
    and two DIFFERENT index paths never collide by construction. Deliberately a
    NEW payload scheme (``"stream:"`` prefix) rather than a re-export of the
    internal :func:`_derive_seed` — the internal payload feeds the committed
    15.14 double-run digests and must never gain callers that could pressure a
    format change.
    """

    payload = "stream:" + ":".join(str(index) for index in (master_seed, *indices))
    return int.from_bytes(hashlib.sha256(payload.encode()).digest()[:8], "big")


def mutate_genome(
    genome: Sequence[float], *, seed: int, sigma: float
) -> tuple[float, ...]:
    """Isotropic Gaussian mutation of ``genome`` (Task 15.15 shared-core extension).

    The SAME bit-stable pure-Python operator the ``(1 + λ)`` loop uses
    internally, exposed so the MAP-Elites entrant mutates genomes through one
    audited operator instead of re-implementing it. ``sigma`` must be positive.
    """

    if not sigma > 0.0:
        raise ValueError(f"sigma must be > 0, got {sigma}")
    return _mutate(tuple(float(gene) for gene in genome), seed=seed, sigma=sigma)


def random_genome(length: int, *, seed: int, scale: float = 0.5) -> tuple[float, ...]:
    """A seeded Gaussian genome (Task 15.15 shared-core extension).

    The initial-genome draw the ``evolve`` loop performs internally, exposed so
    entrants that seed their own populations (MAP-Elites, the CI-budget tests)
    draw through the same bit-stable operator. ``scale`` must be positive.
    """

    if length < 1:
        raise ValueError(f"length must be >= 1, got {length}")
    if not scale > 0.0:
        raise ValueError(f"scale must be > 0, got {scale}")
    return _random_genome(length, seed=seed, scale=scale)


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
    "derive_stream_seed",
    "evolve",
    "k_seed_mean",
    "mutate_genome",
    "random_genome",
]
