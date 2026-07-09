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

No ``eval.*`` import may appear here (the harness firewall test AST-scans this
module): the harness computes every reported metric.
"""

from __future__ import annotations

import bisect
import math
import random
import tempfile
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from agents.tactical.features import TacticalFeatureEncoder
from engine.world import Map, load_canonical_map
from orchestrator.boundary import public_map_from_engine_map
from training.bakeoff import es
from training.bakeoff.harness import (
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
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
    ) -> None:
        self._config = config
        self._warm_start = warm_start
        self._game_map = game_map if game_map is not None else load_canonical_map()
        self._public_map = public_map_from_engine_map(self._game_map)
        self._sabotage_kinds = tuple(sorted(self._game_map.sabotages))

    @property
    def name(self) -> str:
        return "map-elites"

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
        """Score one genome: (cell-quality fitness, axis means, all-8 means).

        The cell quality is the SHARED inner fitness — a K-seed mean of
        :func:`training.bakeoff.harness.inner_episode_fitness` over
        ``config.fitness_seeds`` — and the archive coordinate is derived from the
        seed-mean of each per-episode behavioral descriptor read off the same
        rollouts. ``math.fsum`` keeps every mean order-stable so the fitness and
        the binning are bit-reproducible across runs.
        """

        policy = self._build_policy(genome)
        seeds = self._config.fitness_seeds
        fitnesses: list[float] = []
        per_field: dict[str, list[float]] = {
            name: [] for name in DESCRIPTOR_VECTOR_FIELDS
        }
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
                descriptors = rollout.descriptors
                for name in DESCRIPTOR_VECTOR_FIELDS:
                    per_field[name].append(float(getattr(descriptors, name)))
        count = len(seeds)
        field_means = {
            name: math.fsum(values) / count for name, values in per_field.items()
        }
        axis_means = {axis: field_means[axis] for axis in DESCRIPTOR_AXES}
        fitness = math.fsum(fitnesses) / count
        return fitness, axis_means, field_means

    def _make_cell(
        self, genome: tuple[float, ...]
    ) -> tuple[tuple[int, int, int], ArchiveCell]:
        """Evaluate ``genome`` and place it: its cell coordinate + the elite cell."""

        fitness, axis_means, _ = self._evaluate(genome)
        cell_key = bin_descriptors(
            axis_means["kill_count"],
            axis_means["witness_exposure_rate"],
            axis_means["vent_usage"],
        )
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

        filled_cells = len(archive)
        best_per_cell: list[dict[str, object]] = [
            {
                "cell": list(key),
                "fitness": round(cell.fitness, 4),
                "kill_count": round(cell.descriptors["kill_count"], 4),
                "witness_exposure_rate": round(
                    cell.descriptors["witness_exposure_rate"], 4
                ),
                "vent_usage": round(cell.descriptors["vent_usage"], 4),
            }
            for key, cell in sorted(archive.items(), key=lambda item: item[0])
        ]

        config: dict[str, object] = {
            "entrant": self.name,
            "hidden": self._config.hidden,
            "anchor_weight": self._config.anchor_weight,
            "axes": list(DESCRIPTOR_AXES),
            "edges": {
                "kill_count": list(KILL_COUNT_EDGES),
                "witness_exposure_rate": list(WITNESS_EXPOSURE_EDGES),
                "vent_usage": list(VENT_USAGE_EDGES),
            },
            "iterations": self._config.iterations,
            "fitness_seeds": list(self._config.fitness_seeds),
            "sigma": self._config.sigma,
            "seed": self._config.seed,
            "random_inits": self._config.random_inits,
            "total_cells": TOTAL_CELLS,
            "encoder_version": policy.encoder_version,
            "head": {
                "rooms": sorted(self._public_map.room_ids),
                "kind_slots": list(KIND_SLOTS),
            },
        }
        metadata: dict[str, object] = {
            "archive_coverage": filled_cells / TOTAL_CELLS,
            "filled_cells": filled_cells,
            "total_cells": TOTAL_CELLS,
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


__all__ = [
    "DESCRIPTOR_AXES",
    "KILL_COUNT_EDGES",
    "TOTAL_CELLS",
    "VENT_USAGE_EDGES",
    "WITNESS_EXPOSURE_EDGES",
    "ArchiveCell",
    "MapElitesConfig",
    "MapElitesEntrant",
    "bin_descriptors",
    "map_elites_budget",
]
