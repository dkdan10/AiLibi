"""Entrant (4): MAP-Elites over the 15.8 behavioral descriptors (Task 15.15).

Diversity as MEASURED archive coverage, not a scalar side-channel
(audits/post-phase-14-ML-training-signal.md §4.3: reframe "watchability" as
behavioral COVERAGE). The spike's ``fo9_diversity`` diagnostic measured the
diversity of a single ES population but built no archive; this entrant is the
first real archive — an illuminated map whose FILLED-cell count is the reported
diversity number the pause reads next to the single-objective entrants'
one-point descriptor footprint.

The genome family is the SHARED
:class:`training.bakeoff.policy_es.MaskedMlpPolicy` (encoder-v2 → tanh MLP →
masked head), so MAP-Elites mutation reuses the audited ES operators
(:func:`training.bakeoff.es.mutate_genome` / :func:`~training.bakeoff.es.random_genome`,
both bit-stable pure-Python streams) and the BC warm start is an EXACT
genome-shape match (the spike's BC-then-ES lesson — a from-scratch archive on a
weak encoder illuminates fewer cells). Cell quality is the SAME inner fitness
every ES entrant optimizes
(:func:`training.bakeoff.harness.inner_episode_fitness` — the tactically-reachable
impostor terms + potential shaping, minus the anchor-CE penalty toward the
frozen FSM): MAP-Elites diverges from the ``(1 + λ)`` core only in WHERE it
keeps an elite (one champion per behavior cell, not one global champion), never
in what "good" means. The validity gate and the 15.2 referee stay SELECTION
filters the harness applies after training — never fitness terms
(training-signal audit §4).

The map is a 6×4×4 = 96-cell grid over three of the named 15.8 descriptors:
kill-timing intensity (:data:`KILL_COUNT_EDGES`), stealth exposure
(:data:`WITNESS_EXPOSURE_EDGES`), and vent reliance (:data:`VENT_USAGE_EDGES`) —
:data:`DESCRIPTOR_AXES`. Each descriptor value is the MEAN over the config's
fitness seeds of the per-episode descriptor read off
:attr:`training.rollout.EpisodeRollout.descriptors`, so a chaotic single-seed
descriptor (the spike's check-2 lesson) does not scatter one genome across
cells. Determinism discipline mirrors the ES core: every RNG stream (the random
inits, the parent pick per iteration, the mutation per iteration) is seeded
purely through :func:`training.bakeoff.es.derive_stream_seed` from
``config.seed`` and an index path, and every tie-break is lexical — the champion
is the ``max``-fitness cell with the lexically-smallest genome (a deterministic
argmax), and a genome only displaces a cell's incumbent on a STRICT fitness
improvement (the ES core's elitism semantics).

Task 18.6 adds two things without disturbing that default map. First, the
freeze now PERSISTS the whole illuminated archive, not just its champion: the
old freeze kept the max-fitness cell's genome and discarded every other elite
(audit-phase-18-planning §4 #10; the audit's cited harness lines
407-418/452-458), throwing away the behaviorally-diverse pool at the moment it
was most useful. :func:`write_archive_cell_artifacts` freezes each cell as its
own float-hex ``weights.json`` + sha256 sidecar under a ``cells/`` tree, and
:func:`load_archive_cell_genomes` reloads it bit-exactly — gated on the corpus
substrate's committed identity (:func:`bakeoff_substrate_sha`) so a Wave-1
substrate adoption makes stale cells re-run-before-use, the reloadable pool the
18.20 hall-of-fame seeds from. Second, an ADDITIVE
:class:`DescriptorConfiguration` lets a run SELECT a different three-axis
tessellation — the referee-tension axes
(:data:`REFEREE_TENSION_DESCRIPTOR_CONFIGURATION`) mirror the referee's
watchability TENSION quantities as diversity DIMENSIONS, never as fitness
(training-signal audit §4): cell quality stays :func:`inner_episode_fitness`.
The configuration is chosen EXPLICITLY; the ``None`` default is the standing
``behavior-v1`` map, so the committed champion, config, and report rows stay
byte-identical.

No ``eval.*`` import may appear here (the harness firewall test AST-scans this
module): the harness computes every reported metric.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import math
import random
import shutil
import tempfile
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from agents.tactical.features import (
    TacticalFeatureEncoder,
    weights_from_hex_json,
    weights_to_hex_json,
)
from engine.world import Map, load_canonical_map
from orchestrator.boundary import public_map_from_engine_map
from training.bakeoff import es
from training.bakeoff.harness import (
    BAKEOFF_BASELINE_ID,
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    CORPUS_SPLITS_PATH,
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    DecisionTrace,
    TrainedCandidate,
    inner_episode_fitness,
    load_train_seeds,
    rollout_candidate,
)
from training.bakeoff.policy_es import (
    KIND_SLOTS,
    MaskedMlpPolicy,
    policy_genome_length,
)
from training.rollout import DESCRIPTOR_VECTOR_FIELDS

# --------------------------------------------------------------------------- #
# The behavior map: three of the named 15.8 descriptors, with documented bins. #
# --------------------------------------------------------------------------- #

# The three descriptor axes the archive tessellates. Deliberately three of the
# eight named 15.8 descriptors (:data:`training.rollout.DESCRIPTOR_VECTOR_FIELDS`,
# and exactly its first three, so an axis mean is a slice of the descriptor
# vector): kill-timing INTENSITY (how many kills the genome lands), stealth
# EXPOSURE (the fraction the crew witnessed), and vent RELIANCE. These are the
# axes the planning audit's monoculture concern moves on
# (post-phase-14-ML-planning.md §6.3 / training-signal §4.3): a policy that
# collapses to "kill on sight, ignore witnesses, never vent" is the failure the
# pause fears, and it is exactly a corner of THIS grid — so archive coverage
# over these three axes is the direct measurement of whether the optimizer
# explored past that corner.
DESCRIPTOR_AXES: Final = ("kill_count", "witness_exposure_rate", "vent_usage")

# Kill-count bin edges (bisect_right → 6 bins): {0}, {1}, {2}, {3}, {4}, {5+}.
# Half-integer edges so a single-seed integer kill count never lands ON an edge;
# a MEAN over K seeds can, and lands (by ``bisect_right``) in the higher bin —
# a documented, deterministic convention, not a silent rounding.
KILL_COUNT_EDGES: Final = (0.5, 1.5, 2.5, 3.5, 4.5)
# Witness-exposure bin edges (bisect_right → 4 bins): the first edge is a tiny
# epsilon so exact-zero exposure (a genome no kill of which the crew witnessed)
# is its OWN cell (bin 0), distinct from a merely-low positive rate; then
# (0, 0.25], (0.25, 0.5], (0.5, 1.0].
WITNESS_EXPOSURE_EDGES: Final = (1e-9, 0.25, 0.5)
# Vent-usage bin edges (bisect_right → 4 bins): {0}, {1, 2}, {3, 4, 5}, {6+}
# vent submissions — vent reliance from none to heavy.
VENT_USAGE_EDGES: Final = (0.5, 2.5, 5.5)

KILL_COUNT_BINS: Final = len(KILL_COUNT_EDGES) + 1
WITNESS_EXPOSURE_BINS: Final = len(WITNESS_EXPOSURE_EDGES) + 1
VENT_USAGE_BINS: Final = len(VENT_USAGE_EDGES) + 1
# The archive's total cell count — the denominator of the reported coverage.
TOTAL_CELLS: Final = KILL_COUNT_BINS * WITNESS_EXPOSURE_BINS * VENT_USAGE_BINS


def bin_descriptors(
    kill_count: float, witness_exposure_rate: float, vent_usage: float
) -> tuple[int, int, int]:
    """Map three (seed-mean) descriptor values to their archive cell coordinate.

    ``bisect_right`` over each axis' edges — a value equal to an edge falls in
    the HIGHER bin (the documented convention; the half-integer / epsilon edges
    keep single-seed integer descriptors clear of the edges). The returned
    ``(i, j, k)`` indexes the 6×4×4 grid, each component in
    ``[0, <axis>_BINS)``. Public + unit-tested: it is the single source of truth
    for the archive layout the report's coverage table quotes.
    """

    i = bisect.bisect_right(KILL_COUNT_EDGES, kill_count)
    j = bisect.bisect_right(WITNESS_EXPOSURE_EDGES, witness_exposure_rate)
    k = bisect.bisect_right(VENT_USAGE_EDGES, vent_usage)
    return i, j, k


# --------------------------------------------------------------------------- #
# The descriptor configuration: the additive referee-tension axes (Task 18.6). #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class DescriptorConfiguration:
    """A named three-axis tessellation of the archive (Task 18.6).

    The archive's cell key stays ``tuple[int, int, int]`` — the 18.20 loader
    contract — so a configuration names EXACTLY three descriptor axes and the
    ``bisect_right`` edges each is binned on. The default ``behavior-v1`` map is
    the standing 6×4×4 grid over :data:`DESCRIPTOR_AXES`; a run may instead
    SELECT the referee-tension map
    (:data:`REFEREE_TENSION_DESCRIPTOR_CONFIGURATION`) to illuminate the referee's
    watchability tensions as diversity DIMENSIONS. Either way the cell QUALITY is
    the shared :func:`inner_episode_fitness` — a descriptor is never a fitness
    term (training-signal audit §4). Frozen + fail-loud validated so a malformed
    axis/edge set is unconstructable.
    """

    name: str
    axes: tuple[str, ...]
    edges: Mapping[str, tuple[float, ...]]

    def __post_init__(self) -> None:
        # Fail loud (AGENTS.md "no silent fallbacks"): exactly three DISTINCT
        # axes (the cell key is a 3-tuple), the edge map keys the axes exactly,
        # and every axis' edges are a non-empty strictly-increasing sequence (so
        # the ``bisect_right`` bins are well-ordered and non-degenerate).
        if len(self.axes) != 3:
            raise ValueError(
                f"DescriptorConfiguration {self.name!r} needs exactly 3 axes "
                f"(the archive cell key is a 3-tuple); got {self.axes!r}"
            )
        if len(set(self.axes)) != len(self.axes):
            # A repeated axis degenerates the grid (two coordinates bin the same
            # value) and collapses the per-cell descriptor dict — never silent.
            duplicates = sorted(
                {axis for axis in self.axes if self.axes.count(axis) > 1}
            )
            raise ValueError(
                f"DescriptorConfiguration {self.name!r} axes {self.axes!r} must "
                f"be distinct; repeated axis {duplicates}"
            )
        if set(self.edges) != set(self.axes):
            raise ValueError(
                f"DescriptorConfiguration {self.name!r} edge keys "
                f"{sorted(self.edges)} must match its axes {sorted(self.axes)}"
            )
        for axis in self.axes:
            axis_edges = self.edges[axis]
            if not axis_edges:
                raise ValueError(
                    f"DescriptorConfiguration {self.name!r} axis {axis!r} has no "
                    "edges (an axis needs at least one bin boundary)"
                )
            if any(lo >= hi for lo, hi in zip(axis_edges, axis_edges[1:])):
                raise ValueError(
                    f"DescriptorConfiguration {self.name!r} axis {axis!r} edges "
                    f"{axis_edges!r} must be strictly increasing"
                )

    def total_cells(self) -> int:
        """The archive's cell count — the product of each axis' bin count."""

        product = 1
        for axis in self.axes:
            product *= len(self.edges[axis]) + 1
        return product

    def bin_values(self, values: Mapping[str, float]) -> tuple[int, int, int]:
        """Bin a seed-mean value per axis to the ``(i, j, k)`` cell coordinate.

        ``bisect_right`` over each axis' edges in ``axes`` order — a value equal
        to an edge falls in the HIGHER bin, the identical convention the public
        :func:`bin_descriptors` uses (which stays the behavior map's untouched
        source of truth; under ``behavior-v1`` the two agree bit-for-bit).
        """

        bins = tuple(
            bisect.bisect_right(self.edges[axis], values[axis]) for axis in self.axes
        )
        i, j, k = bins
        return i, j, k


# The default map ``behavior-v1``: the standing 6×4×4 tessellation over the three
# named 15.8 descriptors. Selected whenever a run passes no configuration, so the
# committed champion / config.json / report rows stay byte-stable.
BEHAVIOR_DESCRIPTOR_CONFIGURATION: Final = DescriptorConfiguration(
    name="behavior-v1",
    axes=DESCRIPTOR_AXES,
    edges={
        "kill_count": KILL_COUNT_EDGES,
        "witness_exposure_rate": WITNESS_EXPOSURE_EDGES,
        "vent_usage": VENT_USAGE_EDGES,
    },
)

# Meeting-CADENCE bin edges (bisect_right → 4 bins): {0} no-meeting, (0, 0.05]
# sparse, (0.05, 0.1] moderate, (0.1, +) dense — meetings per elapsed tick. The
# epsilon first edge gives a zero-meeting episode its OWN cell; the two interior
# edges bracket the committed baseline-5 champions' footprints (bc-dagger 0.049;
# the ES/QD champions 0.125-0.134), so the cadence axis SEPARATES the shipped
# policies instead of pooling them in one bin.
MEETING_CADENCE_EDGES: Final = (1e-9, 0.05, 0.1)
# Impostor-win bin edges (bisect_right → 4 bins): {0} never-wins, (0, 0.5]
# sometimes, (0.5, 1) mostly, {1} always. Both extremes get their own cell via
# the epsilon idiom — the second edge is ``1 - epsilon`` so a seed-mean of
# exactly 1.0 lands in the top {1} bin; a mean landing ON the 0.5 edge takes the
# higher bin, the documented ``bisect_right`` convention.
IMPOSTOR_WIN_EDGES: Final = (1e-9, 0.5, 1.0 - 1e-9)

# The referee-tension map ``referee-tension-v1``: three of the referee's
# WATCHABILITY tension quantities mirrored from rollout / decision facts and used
# as diversity DIMENSIONS, never as fitness (training-signal audit §4;
# audit-phase-18-planning §4 #10). Every value is computed from
# :class:`training.rollout.EpisodeRollout` / :class:`DecisionTrace` facts ALONE —
# the referee (:mod:`eval.watchability`) is never imported (the standing AST
# firewall this module is scanned by). The three axes:
#
#   * ``witness_exposure_rate`` — the rollout-side mirror of the referee's
#     ``witnessed_event_rate`` gauge (crew-witnessed kills / kills). It diverges
#     from the referee deliberately: a zero-kill episode reads 0.0 here (its own
#     bin via the epsilon edge) where the referee reports ``None``; and the
#     archive averages per-episode rates over the fitness seeds (mean-of-ratios)
#     where the referee pools ratio-of-sums.
#   * ``meeting_trigger_rate`` — meetings per elapsed tick, the meeting-CADENCE
#     axis; a rollout-native substitute for the referee's flags-per-meeting
#     evidence-SUPPLY gauge (which needs eval-tier meeting quality + persisted
#     flags and is therefore out of this module's reach by design).
#   * ``impostor_win`` — the per-episode win fact (1.0 iff the rollout's winner is
#     the impostor side, the same comparison the harness's win_rate uses), a
#     seed-mean in [0, 1].
REFEREE_TENSION_DESCRIPTOR_CONFIGURATION: Final = DescriptorConfiguration(
    name="referee-tension-v1",
    axes=("witness_exposure_rate", "meeting_trigger_rate", "impostor_win"),
    edges={
        "witness_exposure_rate": WITNESS_EXPOSURE_EDGES,
        "meeting_trigger_rate": MEETING_CADENCE_EDGES,
        "impostor_win": IMPOSTOR_WIN_EDGES,
    },
)


# --------------------------------------------------------------------------- #
# The entrant config + committed budgets.                                      #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class MapElitesConfig:
    """The MAP-Elites entrant budget (recorded verbatim in the report row).

    Frozen so a config deserialized from the report cannot drift. ``iterations``
    mutation-and-insert steps run after the archive is seeded with the warm-start
    genome (when its length matches) plus ``random_inits`` seeded-random genomes;
    ``fitness_seeds`` is the K-seed set every descriptor and the cell-quality
    fitness are averaged over; ``sigma`` is the isotropic mutation scale; ``seed``
    is the master seed every RNG stream derives from. The roster fields mirror
    :class:`training.bakeoff.policy_es.PolicyEsConfig` so every entrant trains on
    the identical 9p2i substrate.
    """

    iterations: int
    fitness_seeds: tuple[int, ...]
    sigma: float
    seed: int
    random_inits: int
    hidden: int = 8
    anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE


def map_elites_budget(
    budget: str, *, anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
) -> MapElitesConfig:
    """The two committed budgets: ``ci`` (seconds-scale) and ``full``.

    Fitness seeds are drawn off the frozen corpus TRAIN split so training never
    touches the eval TEST split reserved for the fixed protocol. ``ci`` fills a
    handful of cells in seconds (the CI-budget smoke of the whole loop); ``full``
    is the operator-executed illumination ($0, CPU, hours-scale) whose coverage
    the report quotes.
    """

    train = load_train_seeds()
    if budget == "ci":
        return MapElitesConfig(
            iterations=2,
            fitness_seeds=train[:1],
            sigma=0.25,
            seed=0,
            random_inits=1,
            anchor_weight=anchor_weight,
        )
    if budget == "full":
        return MapElitesConfig(
            iterations=120,
            fitness_seeds=train[:4],
            sigma=0.25,
            seed=0,
            random_inits=5,
            anchor_weight=anchor_weight,
        )
    raise ValueError(f"unknown budget {budget!r}; expected 'ci' or 'full'")


# --------------------------------------------------------------------------- #
# The archive cell + entrant.                                                  #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ArchiveCell:
    """One filled behavior cell: the elite genome, its quality, its descriptors.

    ``descriptors`` carries the three MEAN axis values
    (:data:`DESCRIPTOR_AXES`) the cell was binned on — kept so the report's
    best-per-cell quality table quotes the measured descriptor next to the
    fitness, not just the bin index.
    """

    genome: tuple[float, ...]
    fitness: float
    descriptors: Mapping[str, float]


class MapElitesEntrant:
    """Entrant (4): MAP-Elites illuminating the 15.8 descriptor archive.

    ``warm_start`` is a zero-arg callable resolved AT TRAIN TIME (the CLI wires
    it to the BC entrant's champion); it returns ``None`` — or a genome of the
    wrong length (a different ``hidden`` width) — to seed the archive from the
    random inits alone. ``train`` seeds the archive, runs ``iterations``
    mutate-evaluate-insert steps, and freezes the max-fitness cell's genome as
    the champion. It computes NO reported eval metric: the harness's
    :func:`training.bakeoff.harness.evaluate_candidate` owns those. The archive
    coverage + best-per-cell quality table it DOES compute are the QD training
    diagnostics, carried verbatim into the row's metadata.
    """

    def __init__(
        self,
        *,
        config: MapElitesConfig,
        warm_start: Callable[[], tuple[float, ...] | None] | None = None,
        game_map: Map | None = None,
        descriptor_configuration: DescriptorConfiguration | None = None,
    ) -> None:
        self._config = config
        self._warm_start = warm_start
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._public_map = public_map_from_engine_map(self._game_map)
        self._sabotage_kinds = tuple(sorted(self._game_map.sabotages))
        # ``None`` selects the standing behavior map, so an unconfigured run is
        # byte-identical to the committed default (Task 18.6 is additive).
        self._descriptor_configuration = (
            BEHAVIOR_DESCRIPTOR_CONFIGURATION
            if descriptor_configuration is None
            else descriptor_configuration
        )
        # The 18.6 freeze-retention hook: the final archive the persistence
        # writer consumes, ``None`` until the first ``train()``.
        self._last_archive: Mapping[tuple[int, int, int], ArchiveCell] | None = None

    @property
    def name(self) -> str:
        return "map-elites"

    @property
    def last_archive(self) -> Mapping[tuple[int, int, int], ArchiveCell] | None:
        """The final illuminated archive from the last ``train()`` (else ``None``).

        The Task 18.6 freeze-retention hook the persistence writer
        (:func:`write_archive_cell_artifacts`) consumes: before 18.6 the freeze
        discarded every non-champion elite at the moment the behaviorally-diverse
        pool was most useful (audit-phase-18-planning §4 #10; the audit's cited
        harness lines 407-418/452-458). Retaining it lets the whole map become
        the reloadable pool the 18.20 hall-of-fame seeds from.
        """

        return self._last_archive

    def _genome_length(self) -> int:
        return policy_genome_length(
            self._public_map,
            hidden=self._config.hidden,
            encoder=TacticalFeatureEncoder(),
        )

    def _build_policy(self, genome: tuple[float, ...]) -> MaskedMlpPolicy:
        return MaskedMlpPolicy(
            genome=genome,
            public_map=self._public_map,
            sabotage_kinds=self._sabotage_kinds,
            hidden=self._config.hidden,
        )

    def _evaluate(
        self, genome: tuple[float, ...]
    ) -> tuple[float, dict[str, float], dict[str, float]]:
        """Score one genome: (cell-quality fitness, active-axis means, field means).

        The cell quality is the SHARED inner fitness — a K-seed mean of
        :func:`training.bakeoff.harness.inner_episode_fitness` over
        ``config.fitness_seeds`` — and the archive coordinate is the seed-mean of
        each ACTIVE-axis behavioral descriptor read off the same rollouts. The
        returned field means carry all 8 named descriptors PLUS the per-episode
        ``impostor_win`` fact (the referee-tension map's third axis), so any
        configuration can bin on three of them. ``math.fsum`` keeps every mean
        order-stable so the fitness and the binning are bit-reproducible across
        runs.
        """

        policy = self._build_policy(genome)
        seeds = self._config.fitness_seeds
        fitnesses: list[float] = []
        per_field: dict[str, list[float]] = {
            name: [] for name in DESCRIPTOR_VECTOR_FIELDS
        }
        # The per-episode impostor-win fact — the referee-tension map's third
        # axis — collected from the SAME rollouts (no extra RNG, no extra rollout
        # parameter), so it is byte-neutral on the default path, which never reads
        # this key.
        impostor_wins: list[float] = []
        with tempfile.TemporaryDirectory(prefix="ailibi-map-elites-") as tmp:
            output_dir = Path(tmp)
            for seed in seeds:
                trace = DecisionTrace()
                rollout = rollout_candidate(
                    policy,
                    seed,
                    output_dir=output_dir,
                    game_map=self._game_map,
                    num_players=self._config.num_players,
                    num_impostors=self._config.num_impostors,
                    tasks_per_crewmate=self._config.tasks_per_crewmate,
                    trace=trace,
                )
                fitnesses.append(
                    inner_episode_fitness(
                        rollout, trace, anchor_weight=self._config.anchor_weight
                    )
                )
                # The exact idiom the harness's win_rate uses (harness.py:943):
                # only a terminal IMPOSTORS winner counts; a truncated / ``None``
                # winner reads 0.0.
                impostor_wins.append(1.0 if rollout.winner == "IMPOSTORS" else 0.0)
                descriptors = rollout.descriptors
                for name in DESCRIPTOR_VECTOR_FIELDS:
                    per_field[name].append(float(getattr(descriptors, name)))
        count = len(seeds)
        field_means = {
            name: math.fsum(values) / count for name, values in per_field.items()
        }
        field_means["impostor_win"] = math.fsum(impostor_wins) / count
        axis_means = {
            axis: field_means[axis] for axis in self._descriptor_configuration.axes
        }
        fitness = math.fsum(fitnesses) / count
        return fitness, axis_means, field_means

    def _make_cell(
        self, genome: tuple[float, ...]
    ) -> tuple[tuple[int, int, int], ArchiveCell]:
        """Evaluate ``genome`` and place it: its cell coordinate + the elite cell.

        The coordinate comes from the ACTIVE configuration's ``bin_values`` (for
        ``behavior-v1`` this is bit-identical arithmetic to the public
        :func:`bin_descriptors` — same edges, same ``bisect_right``).
        """

        fitness, axis_means, _ = self._evaluate(genome)
        cell_key = self._descriptor_configuration.bin_values(axis_means)
        return cell_key, ArchiveCell(
            genome=genome, fitness=fitness, descriptors=axis_means
        )

    @staticmethod
    def _insert(
        archive: dict[tuple[int, int, int], ArchiveCell],
        cell_key: tuple[int, int, int],
        cell: ArchiveCell,
    ) -> None:
        """MAP-Elites insertion with the ES core's elitism semantics.

        A genome takes a cell iff the cell is EMPTY or its fitness is STRICTLY
        greater than the incumbent's; on an exact fitness tie the incumbent
        stays — so the archive never drifts across equal-quality genomes and two
        identical runs illuminate an identical map.
        """

        incumbent = archive.get(cell_key)
        if incumbent is None or cell.fitness > incumbent.fitness:
            archive[cell_key] = cell

    def train(self) -> TrainedCandidate:
        started = time.perf_counter()
        genome_length = self._genome_length()
        archive: dict[tuple[int, int, int], ArchiveCell] = {}
        evaluations = 0

        # Seed the archive: the warm-start genome first (when it matches the
        # family's shape), then ``random_inits`` seeded-random genomes.
        warm_start_used = False
        if self._warm_start is not None:
            candidate_genome = self._warm_start()
            if candidate_genome is not None and len(candidate_genome) == genome_length:
                cell_key, cell = self._make_cell(candidate_genome)
                self._insert(archive, cell_key, cell)
                evaluations += 1
                warm_start_used = True
        for index in range(self._config.random_inits):
            genome = es.random_genome(
                genome_length,
                seed=es.derive_stream_seed(self._config.seed, 0, index),
                scale=0.5,
            )
            cell_key, cell = self._make_cell(genome)
            self._insert(archive, cell_key, cell)
            evaluations += 1

        if not archive:
            raise ValueError(
                "MAP-Elites seeded no cells; give a length-matching warm start or "
                "random_inits >= 1 (a mutate step cannot pick a parent from an "
                "empty archive)"
            )

        # Illuminate: each iteration draws a uniform elite parent, mutates it
        # through the audited operator, and inserts the child.
        for it in range(self._config.iterations):
            parent_rng = random.Random(es.derive_stream_seed(self._config.seed, 1, it))
            parent_key = parent_rng.choice(sorted(archive))
            parent = archive[parent_key]
            child = es.mutate_genome(
                parent.genome,
                seed=es.derive_stream_seed(self._config.seed, 2, it),
                sigma=self._config.sigma,
            )
            cell_key, cell = self._make_cell(child)
            self._insert(archive, cell_key, cell)
            evaluations += 1

        # Champion: the max-fitness cell, tie-broken to the lexically-smallest
        # genome — a deterministic argmax (the ES core's selection idiom).
        champion_key, champion_cell = min(
            archive.items(), key=lambda item: (-item[1].fitness, item[1].genome)
        )
        champion_genome = champion_cell.genome
        policy = self._build_policy(champion_genome)
        # Retain the frozen archive so the persistence writer can reload the whole
        # behaviorally-diverse pool (Task 18.6): a shallow copy pins it against a
        # later ``train()`` mutating the same dict.
        self._last_archive = dict(archive)

        configuration = self._descriptor_configuration
        total_cells = configuration.total_cells()
        filled_cells = len(archive)
        # Generalize the per-cell descriptor keys to the ACTIVE axes, preserving
        # the ``cell``/``fitness``/<axes...> order and the ``round(..., 4)``: for
        # ``behavior-v1`` this reproduces today's literal rows exactly.
        best_per_cell: list[dict[str, object]] = [
            {
                "cell": list(key),
                "fitness": round(cell.fitness, 4),
                **{
                    axis: round(cell.descriptors[axis], 4)
                    for axis in configuration.axes
                },
            }
            for key, cell in sorted(archive.items(), key=lambda item: item[0])
        ]

        config: dict[str, object] = {
            "entrant": self.name,
            "hidden": self._config.hidden,
            "anchor_weight": self._config.anchor_weight,
            "axes": list(configuration.axes),
            "edges": {
                axis: list(configuration.edges[axis]) for axis in configuration.axes
            },
            "iterations": self._config.iterations,
            "fitness_seeds": list(self._config.fitness_seeds),
            "sigma": self._config.sigma,
            "seed": self._config.seed,
            "random_inits": self._config.random_inits,
            "total_cells": total_cells,
            "encoder_version": policy.encoder_version,
            "head": {
                "rooms": sorted(self._public_map.room_ids),
                "kind_slots": list(KIND_SLOTS),
            },
        }
        # The descriptor-config NAME is recorded ONLY when a non-default map is
        # explicitly selected: byte-stability of the committed config.json forbids
        # a new key on the default path, so the identity check against the standing
        # singleton keeps ``behavior-v1`` runs bit-identical.
        if configuration is not BEHAVIOR_DESCRIPTOR_CONFIGURATION:
            config["descriptor_config"] = configuration.name
        metadata: dict[str, object] = {
            "archive_coverage": filled_cells / total_cells,
            "filled_cells": filled_cells,
            "total_cells": total_cells,
            "evaluations": evaluations,
            "warm_start_used": warm_start_used,
            "champion_cell": list(champion_key),
            "champion_fitness": round(champion_cell.fitness, 4),
            "best_per_cell": best_per_cell,
        }
        return TrainedCandidate(
            entrant=self.name,
            policy=policy,
            weights=champion_genome,
            config=config,
            train_wall_clock_s=time.perf_counter() - started,
            train_metadata=metadata,
        )


# --------------------------------------------------------------------------- #
# Cell persistence (Task 18.6): the reloadable behaviorally-diverse pool.       #
# --------------------------------------------------------------------------- #


def _sha256_hex(data: bytes) -> str:
    # Restated one-liner mirroring the private ``harness._sha256_hex``: restating
    # the trivial digest helper is the lesser coupling versus importing a private
    # symbol across the entrant/harness seam.
    return hashlib.sha256(data).hexdigest()


# The persisted layout. Restated literals mirroring the harness artifact layout
# (:func:`training.bakeoff.harness.write_candidate_artifact`, whose filename
# constants are private), so a cell subdir looks EXACTLY like a champion
# artifact: a float-hex ``weights.json`` + its ``<digest>  weights.json`` sidecar.
_CELLS_DIRNAME: Final = "cells"
_CELL_INDEX_FILENAME: Final = "index.json"
_CELL_WEIGHTS_FILENAME: Final = "weights.json"


def historical_bakeoff_substrate_sha() -> str:
    """Reproduce the original manifest-only cell identity for historical readers.

    This definition cannot authorize current campaign seeds. New cell artifacts
    use the version-two bakeoff_substrate_sha and record its definition name.
    """

    manifest = (CORPUS_SPLITS_PATH.parent / "MANIFEST.md").read_bytes()
    return _sha256_hex(manifest)


def bakeoff_substrate_sha() -> str:
    """Version-two cell substrate over recorded inputs and their derivation."""

    from training.provenance import fit_corpus_fingerprint

    return _sha256_hex(
        (
            "cell-substrate-v2:" + fit_corpus_fingerprint(CORPUS_SPLITS_PATH.parent)
        ).encode()
    )


def write_archive_cell_artifacts(
    archive: Mapping[tuple[int, int, int], ArchiveCell],
    artifact_dir: Path,
    *,
    config: MapElitesConfig,
    descriptor_configuration: DescriptorConfiguration | None = None,
) -> Path:
    """Persist the illuminated archive as a reloadable cell tree (Task 18.6).

    The freeze-persistence half of Task 18.6: the archive that
    :meth:`MapElitesEntrant.train` used to discard becomes the reloadable
    behaviorally-diverse pool the 18.20 hall-of-fame seeds from. Each cell is
    frozen under ``cells/<i>-<j>-<k>/`` as its own float-hex ``weights.json`` +
    ``<digest>  weights.json`` sidecar — the EXACT
    :func:`training.bakeoff.harness.write_candidate_artifact` byte conventions —
    and ``cells/index.json`` records every cell's descriptors, fitness, and
    weights digest, the training config, the active descriptor configuration, and
    the corpus SUBSTRATE identity (:func:`bakeoff_substrate_sha`). That substrate
    sha is what the stale-seed refusal reads: a Wave-1 substrate adoption makes
    these cells re-run-before-use (a cheap deterministic re-run), never silently
    reused at a drifted substrate.

    A re-freeze REPLACES the persisted pool: any pre-existing ``cells/`` tree is
    removed first, so a stale cell from an earlier freeze can never linger and the
    tree stays a pure function of THIS run. Fails loud on an empty archive (a
    frozen run always illuminates at least one cell). Returns the ``cells/``
    directory.

    ``descriptor_configuration`` MUST be the configuration the archive was binned
    on — the writer verifies this BEFORE any file I/O: each cell's descriptor key
    set must equal the configuration's axes, AND re-binning the cell's descriptors
    under the configuration's edges must reproduce the cell's own coordinate. A
    mismatch — a different axis set (e.g. persisting a referee-tension archive
    while recording the behavior-v1 block) OR the same axes with shifted edges
    that re-bin a cell elsewhere — fails loud rather than writing an
    internally-inconsistent tree the loader cannot later detect.

    Operator regeneration recipe (reproduces the committed tree byte-for-byte)::

        from pathlib import Path
        from training.bakeoff.harness import load_candidate_weights
        from training.bakeoff.map_elites import (
            MapElitesEntrant, map_elites_budget, write_archive_cell_artifacts,
        )
        root = Path("training/artifacts/impostor")
        bc = load_candidate_weights(root / "bc-dagger")
        config = map_elites_budget("full")
        entrant = MapElitesEntrant(config=config, warm_start=lambda: bc)
        candidate = entrant.train()
        archive = entrant.last_archive
        assert archive is not None
        write_archive_cell_artifacts(archive, root / "map-elites", config=config)
    """

    configuration = (
        BEHAVIOR_DESCRIPTOR_CONFIGURATION
        if descriptor_configuration is None
        else descriptor_configuration
    )
    if not archive:
        raise ValueError(
            "cannot persist an empty MAP-Elites archive; a frozen run always "
            "illuminates at least one cell"
        )

    # Fail loud BEFORE any file I/O if the configuration being recorded is not the
    # one the archive was binned on: every cell's descriptor keys must equal the
    # configuration's axes, and re-binning the cell's descriptors under the
    # configuration's edges must reproduce the cell's own coordinate. Otherwise
    # the index block (axes / edges / total_cells) would misdescribe the persisted
    # cells — an inconsistency the loader cannot detect (a same-axes-different-
    # edges config re-bins some cells to a DIFFERENT coordinate yet passes any
    # per-component range check, since bin_values output is always in range).
    axis_set = set(configuration.axes)
    for cell_key in sorted(archive):
        cell = archive[cell_key]
        if set(cell.descriptors) != axis_set:
            raise ValueError(
                f"cell {cell_key} was binned on axes {sorted(cell.descriptors)} "
                f"but the configuration being recorded is "
                f"{configuration.name!r} over {sorted(axis_set)}; the writer's "
                "descriptor_configuration must be the one the archive was binned on"
            )
        if configuration.bin_values(cell.descriptors) != cell_key:
            raise ValueError(
                f"configuration {configuration.name!r} re-bins cell "
                f"{cell_key} to {configuration.bin_values(cell.descriptors)} under "
                "its recorded edges; the edges do not reproduce the archive's cell "
                "coordinates — the descriptor_configuration must be the one the "
                "archive was binned on"
            )

    cells_dir = artifact_dir / _CELLS_DIRNAME
    if cells_dir.exists():
        # A re-freeze REPLACES the pool: stale cells from a previous freeze must
        # not linger, or the tree stops being a function of the run.
        shutil.rmtree(cells_dir)
    cells_dir.mkdir(parents=True)

    index_cells: list[dict[str, object]] = []
    for cell_key in sorted(archive):
        i, j, k = cell_key
        cell = archive[cell_key]
        subdir_name = f"{i}-{j}-{k}"
        subdir = cells_dir / subdir_name
        subdir.mkdir()
        weights_json = weights_to_hex_json(cell.genome) + "\n"
        (subdir / _CELL_WEIGHTS_FILENAME).write_text(weights_json)
        digest = _sha256_hex(weights_json.encode("utf-8"))
        (subdir / f"{_CELL_WEIGHTS_FILENAME}.sha256").write_text(
            f"{digest}  {_CELL_WEIGHTS_FILENAME}\n"
        )
        index_cells.append(
            {
                "cell": [i, j, k],
                "descriptors": dict(cell.descriptors),
                "fitness": cell.fitness,
                "path": f"{_CELLS_DIRNAME}/{subdir_name}",
                "weights_sha256": digest,
            }
        )

    index: dict[str, object] = {
        "baseline_id": BAKEOFF_BASELINE_ID,
        "cells": index_cells,
        "config": {
            "anchor_weight": config.anchor_weight,
            "fitness_seeds": list(config.fitness_seeds),
            "hidden": config.hidden,
            "iterations": config.iterations,
            "num_impostors": config.num_impostors,
            "num_players": config.num_players,
            "random_inits": config.random_inits,
            "seed": config.seed,
            "sigma": config.sigma,
            "tasks_per_crewmate": config.tasks_per_crewmate,
        },
        "descriptor_config": {
            "axes": list(configuration.axes),
            "edges": {
                axis: list(configuration.edges[axis]) for axis in configuration.axes
            },
            "name": configuration.name,
            "total_cells": configuration.total_cells(),
        },
        "entrant": "map-elites",
        "filled_cells": len(archive),
        "substrate": {
            "corpus_manifest": str(CORPUS_SPLITS_PATH.parent / "MANIFEST.md"),
            "substrate_sha256": bakeoff_substrate_sha(),
            "substrate_sha_kind": "bakeoff_substrate_sha.v2",
        },
    }
    (cells_dir / _CELL_INDEX_FILENAME).write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n"
    )
    return cells_dir


def load_archive_cell_genomes(
    artifact_dir: Path,
    *,
    expected_substrate_sha: str | None = None,
    expected_substrate_kind: str | None = None,
) -> dict[tuple[int, int, int], ArchiveCell]:
    """Reload the persisted cell pool, verifying every integrity invariant.

    The reload half of Task 18.6 — the inverse of
    :func:`write_archive_cell_artifacts`, round-tripping the in-memory archive
    EXACTLY (bit-exact genomes via float-hex; exact fitness/descriptors via JSON
    repr round-trip). A missing ``cells/index.json`` raises naturally
    (:class:`FileNotFoundError`, mirroring
    :func:`training.bakeoff.harness.load_candidate_weights`' posture); every
    integrity violation fails loud with :class:`ValueError`.

    If ``expected_substrate_sha`` is given and differs from the index's recorded
    ``substrate.substrate_sha256`` the reload REFUSES — the 18.24/18.20 fence:
    stale-substrate cells must be re-run at the adopted substrate before use. The
    recorded descriptor configuration is rebuilt as a real
    :class:`DescriptorConfiguration` (so the index block gets the same fail-loud
    validation) and each entry SELF-validates: its descriptors must key on the
    recorded axes and re-bin to its own cell key under the recorded edges (a
    mislabeled or tampered index otherwise). Per cell the loader re-hashes
    ``weights.json`` and cross-checks the digest against BOTH the sidecar's first
    token and the index entry (the
    :func:`~training.bakeoff.harness.load_candidate_weights` drift posture), and
    the on-disk ``cells/`` subdirectory set must equal the index's path set — a
    stray or missing cell dir is drift, never papered over.
    """

    cells_dir = artifact_dir / _CELLS_DIRNAME
    index_path = cells_dir / _CELL_INDEX_FILENAME
    index = json.loads(index_path.read_text())

    recorded_substrate = index["substrate"]["substrate_sha256"]
    recorded_kind = index["substrate"].get(
        "substrate_sha_kind", "bakeoff_substrate_sha"
    )
    if expected_substrate_sha is not None:
        expected_kind = expected_substrate_kind or "bakeoff_substrate_sha.v2"
        if recorded_kind != expected_kind:
            raise ValueError("MAP-Elites substrate kind mismatch")
        source_sha = (
            bakeoff_substrate_sha()
            if expected_kind == "bakeoff_substrate_sha.v2"
            else historical_bakeoff_substrate_sha()
            if expected_kind == "bakeoff_substrate_sha"
            else None
        )
        if source_sha != expected_substrate_sha:
            raise ValueError(
                "MAP-Elites requested substrate does not match its named source definition"
            )

    if (
        expected_substrate_sha is not None
        and expected_substrate_sha != recorded_substrate
    ):
        raise ValueError(
            f"persisted cells at {cells_dir} were scored at substrate "
            f"{recorded_substrate} but the adopted substrate is "
            f"{expected_substrate_sha}; stale-substrate cells must be re-run at "
            "the adopted substrate before use"
        )

    # Rebuild the recorded configuration as a real DescriptorConfiguration:
    # constructing it runs __post_init__'s fail-loud validation on the index block
    # (3 distinct axes, edge keys == axes, strictly-increasing edges) for free.
    descriptor_config = index["descriptor_config"]
    configuration = DescriptorConfiguration(
        name=descriptor_config["name"],
        axes=tuple(descriptor_config["axes"]),
        edges={
            axis: tuple(edge_list)
            for axis, edge_list in descriptor_config["edges"].items()
        },
    )
    axis_set = set(configuration.axes)

    # First pass: validate every cell key (shape, no duplicates), self-validate the
    # index (each entry's descriptors must key on the recorded axes and RE-BIN to
    # the entry's own cell key under the recorded edges — a mislabeled/tampered
    # index otherwise), and collect the index's declared path set. This runs BEFORE
    # any weights read so a missing cell dir is caught by the drift cross-check
    # below as a loud ValueError, not a bare FileNotFoundError from the read loop.
    validated: list[tuple[tuple[int, int, int], Any]] = []
    index_paths: set[str] = set()
    seen_keys: set[tuple[int, int, int]] = set()
    for entry in index["cells"]:
        raw_key = entry["cell"]
        if (
            not isinstance(raw_key, list)
            or len(raw_key) != 3
            or not all(isinstance(component, int) for component in raw_key)
        ):
            raise ValueError(
                f"cell index at {index_path} has a malformed cell key "
                f"{raw_key!r} (expected a 3-list of ints)"
            )
        cell_key = (int(raw_key[0]), int(raw_key[1]), int(raw_key[2]))
        if cell_key in seen_keys:
            raise ValueError(
                f"cell index at {index_path} has a duplicate cell key {cell_key}"
            )
        seen_keys.add(cell_key)
        descriptors = entry["descriptors"]
        if set(descriptors) != axis_set:
            raise ValueError(
                f"index entry for cell {cell_key} carries descriptors "
                f"{sorted(descriptors)} but the recorded configuration "
                f"{configuration.name!r} is over {sorted(axis_set)}"
            )
        if configuration.bin_values(descriptors) != cell_key:
            raise ValueError(
                f"index entry for cell {cell_key} re-bins to "
                f"{configuration.bin_values(descriptors)} under the recorded "
                f"{configuration.name!r} edges — a mislabeled or tampered index"
            )
        validated.append((cell_key, entry))
        index_paths.add(entry["path"])

    on_disk = {
        f"{_CELLS_DIRNAME}/{child.name}"
        for child in cells_dir.iterdir()
        if child.is_dir()
    }
    if on_disk != index_paths:
        raise ValueError(
            f"on-disk cell dirs {sorted(on_disk)} do not match the index's cell "
            f"paths {sorted(index_paths)} at {cells_dir}"
        )

    # Second pass: read + sha-verify each cell's weights and rebuild the archive.
    archive: dict[tuple[int, int, int], ArchiveCell] = {}
    for cell_key, entry in validated:
        subdir = cells_dir / f"{cell_key[0]}-{cell_key[1]}-{cell_key[2]}"
        weights_path = subdir / _CELL_WEIGHTS_FILENAME
        raw = weights_path.read_text()
        actual = _sha256_hex(raw.encode("utf-8"))
        sidecar = (subdir / f"{_CELL_WEIGHTS_FILENAME}.sha256").read_text().split()[0]
        if actual != sidecar:
            raise ValueError(
                f"{weights_path} hashes to {actual} but the sidecar records {sidecar}"
            )
        recorded_index = entry["weights_sha256"]
        if actual != recorded_index:
            raise ValueError(
                f"{weights_path} hashes to {actual} but the index records "
                f"{recorded_index}"
            )
        archive[cell_key] = ArchiveCell(
            genome=weights_from_hex_json(raw),
            fitness=entry["fitness"],
            descriptors=dict(entry["descriptors"]),
        )
    return archive


__all__ = [
    "BEHAVIOR_DESCRIPTOR_CONFIGURATION",
    "DESCRIPTOR_AXES",
    "IMPOSTOR_WIN_EDGES",
    "KILL_COUNT_EDGES",
    "MEETING_CADENCE_EDGES",
    "REFEREE_TENSION_DESCRIPTOR_CONFIGURATION",
    "TOTAL_CELLS",
    "VENT_USAGE_EDGES",
    "WITNESS_EXPOSURE_EDGES",
    "ArchiveCell",
    "DescriptorConfiguration",
    "MapElitesConfig",
    "MapElitesEntrant",
    "bakeoff_substrate_sha",
    "bin_descriptors",
    "load_archive_cell_genomes",
    "map_elites_budget",
    "write_archive_cell_artifacts",
]
