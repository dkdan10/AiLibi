"""The alternating-freeze co-evolution driver + stabilizers (Task 18.21).

The campaign engine the planning audit priced as option #8
(audits/audit-phase-18-planning.md §4) with the §6 AlphaStar/PSRO transfer as
its stabilizer kit: evolve ONE side's population (the standing
:func:`training.bakeoff.es.evolve` ES) against a PFSP-sampled slate of FROZEN
opponents while the other side is frozen, freeze the champion into the 18.20
hall of fame, swap sides, repeat. One side moves at a time, ALWAYS — the naive
simultaneous two-population form audits/audit-phase-15-pause.md decision 4
barred stays structurally unreachable (there is exactly one moving
:class:`_SideState` per swap, the frozen side's standing champion is
snapshot-guarded across the swap, and the guard raises rather than papers
over). Decision 4's entry condition — "the stabilizer stack as the entry
condition, never the naive two-population form" — is what this driver
satisfies.

The per-generation stabilizer instrumentation (every generation emits one
machine-readable :class:`CoevoCampaignRow`):

* **The absolute anchor benchmark, both directions** — the moving champion vs
  the fully scripted FSM (``rollout_coevo(champion, None)`` / the mirrored
  crew shape), recording BOTH sides' fitness from the same games: the
  champion side's absolute progress AND the scripted side's reading of the
  matchup. This is the cycling detector
  ``experiments/lab/ml_spike/fo2_coevolution.py`` establishes: an oscillating
  co-matchup (the per-generation payoff row vs the pool) with a FLAT anchor
  benchmark is Red-Queen cycling; a monotone anchor benchmark is real
  progress. The benchmark ALWAYS runs the default deterministic fake-provider
  path — champion numbers are never composed-runner-scored (the 18.29
  standing rule).
* **The per-side short-horizon exploiter probe** — a small ES (the standing
  optimizer at a tiny budget, e.g. 5×6) breeding the FROZEN side's family
  purely to beat the current champion (``anchor_weight=0`` on the exploiter
  side; the scripted FSM's own fitness vs the same champion, on the same
  seeds, is the bar). A found exploit freezes into the frozen side's hall of
  fame (origin :data:`EXPLOITER_ORIGIN`) and is registered with the ledger —
  fresh opponent pressure without ever advancing the frozen side's standing
  champion.
* **The anchor-CE term retained toward the FIXED scripted FSM on both sides**
  — every trace accumulator inherits ``anchor_policy`` from the SIDE CONFIG
  (``None`` = the scripted FSM proposal itself; the 18.5 filtered-BC artifact
  is the intended alternative), NEVER from an accumulator and never the
  moving opponent (the #306 P2 fix: fresh per-episode traces, folded into
  accumulators AFTER scoring — :func:`training.coevo.rollout.rollout_coevo`'s
  committed discipline).

Hall-of-fame consumption discipline (the 18.20 hand-off, binding): ONE
:class:`~training.coevo.hall_of_fame.OpponentStalenessLedger` is constructed
per run from the cap + both halls' member shas and threaded across the whole
loop; every freshly frozen member (swap champion or exploit) is ``register``ed;
"one generation use" is one use per DISTINCT sampled member per driver
generation (``sample_opponents`` draws WITH replacement, so the slate is
deduped before metering — game evaluation weights distinct opponents by their
draw multiplicity, arithmetically identical to replaying duplicates); a capped
opponent is RETIRE-AND-REPLACE — excluded from every future slate for this
run, its replacements being the freshly frozen champions/exploits (fresh shas)
— never an in-place counter reset, and a pool whose every member is retired
stops the campaign loudly. Payoff maps passed to the sampler are measured
fresh each generation (current champion vs every active member — the exact
deterministic payoff row the §6 note calls a luxury) and therefore exactly
cover the pool; the driver never passes the empty map at all — the sampler's
cold-start-uniform exception is gen-1-shaped and this driver measures even
generation 1's row, strictly stronger than the exception. Founders ingest
through the substrate-fenced ``ingest_map_elites_founders`` BEFORE any pool
build or sampling. ``HallOfFame.create`` pins the campaign substrate sha, and
because TWO sha definitions exist (``compute_substrate_sha`` composite vs
``bakeoff_substrate_sha`` raw MANIFEST — the 18.24 block), the config and
every row name WHICH definition was passed (``substrate_sha_kind``).

Two ADDITIVE seams, each inert when unset (digest-identical):

* **The per-swap scenario-provider callable** (18.23's install point): called
  once per swap with ``(swap_index, moving_side)``, returning
  :class:`CoevoScenarioTerm` s whose fitness callables ADD to that swap's ES
  fitness (labels ride the rows). Unset ⇒ no terms ⇒ byte-identical fitness.
* **The optional meeting-runner factory per campaign configuration** (default:
  the fake provider). The 18.29 composed runner is adopted ONLY via
  :func:`training.composed_runner.load_composed_runner_factory` on its
  DEFAULT gated path (:class:`CoevoComposedRunnerConfig` types
  ``composed_artifact_dir`` as ``Path``, so the diagnostics-only
  ``composed_artifact_dir=None`` escape is structurally unreachable from a
  campaign configuration), and only at a swap boundary — the factory is
  loaded/re-validated at each swap start, never mid-swap. Under a composed
  configuration the row's conviction/surrogate consumption columns read BOTH
  component counters (gate reads + probe reads) and
  ``verdict.json.adoption_constraints`` is surfaced VERBATIM in every row.
  The generic ``meeting_runner_factory`` slot is the future-GO-verdict-runner
  seam; both serve TRAINING games only (ES evals + payoff rows) — benchmark
  and exploiter games stay on the fake path (see above).

The driver owns ALL the meters, threaded once and cumulative (the harness's
one-term/one-counter ``resolved_conviction_term()`` pattern): the ONE
:class:`~training.bakeoff.harness.ConvictionFitnessTerm` (when configured) is
SERVED LIVE on every training game of a non-composed campaign — each game's
runner is wrapped in the committed 18.30
:class:`~training.conviction.serving.ConvictionServingMeetingRunner` (one
metered prediction per meeting on the shared counter), the predictions are
recorded into BOTH sides' episode traces, and both fitnesses are recomposed
through the pure ``inner_episode_fitness`` / ``crew_inner_episode_fitness``
functions — the 18.16 doctrine's "SAME term object serves BOTH sides", now
actually delivered into training pressure (Codex review on PR #311; the
18.30 asymmetry note says the loops stay anchor-composed "until the 18.24
campaign threads the same term", and the campaign threads it by configuring
this seam). Under a COMPOSED configuration the term is NOT double-wrapped:
the composed runner's own gate reads meter the SAME shared
:class:`~training.conviction.model.ConvictionUseCounter`, and conviction
pressure reaches training through actual ejection outcomes; the surrogate
counter (composed configurations only) meters every composed meeting's probe
read. Benchmark and exploiter games never serve the term (``conviction=None``
— the absolute meter stays pure). A campaign whose meter is already spent
refuses to start — at engine init BEFORE any disk mutation, and again at
every swap boundary (the loud boundary stop the hint names — the natural
re-grounding point); a mid-swap exhaustion raises from the counter itself.

Integration-risk guard: compounding budgets (population × generations × seeds
× slate) are computed UP FRONT as :func:`projected_game_bound` (a stated
upper bound over the fake-path game count), logged into
``campaign-plan.json``, and a configuration whose bound exceeds
``game_ceiling`` (default :data:`DEFAULT_GAME_CEILING`) is REFUSED unless
``allow_over_ceiling=True`` — no accidental week-long runs.

V3-family entrant configs (the 18.22 hand-off): each
:class:`CoevoSideConfig` carries ``encoder_version`` (the free-policy-family
``"v2"`` default) and the driver PINS the family — the built policy's
``encoder_version`` must equal the pin (checked before any game, alongside
the 18.19 crew-namespace conflation guard), every frozen-member reload is
length-checked against the side's ``genome_length`` (a mixed family would
otherwise fail only deep in the encoder), and a hall/side stays SINGLE-FAMILY
per campaign. HoF rows deliberately carry no encoder stamp — the campaign
config and the campaign rows carry it instead.

Campaign ergonomics (Task 18.31, from the 18.24 campaign's operational cost
evidence — report-impostor-campaign.md §11): every generation's champion is
persisted the moment it exists, as a four-file LOADABLE artifact under
``<work_dir>/gen-champions/gen-<N>/<sha>/`` (fix 2 — §11 defect 2 / F1 cost 66
real games and two recovery passes to re-breed intermediates the driver had
already computed), and every freeze path — swap champion, exploiter find,
MAP-Elites founder, per-generation champion — writes ``stamp.json`` +
``config.json`` beside the weights through
:func:`training.coevo.hall_of_fame.write_loadable_artifact` (fix 4 — §11 defect
4 / F14: the whole 18.24 shortlist was unloadable through
``scripts/run_tournament.py``'s ``_load_candidate_policy`` until review caught
it). ``encoder_version`` / ``hidden`` are DISPATCHED FROM THE SIDE CONFIG, never
re-derived from genome length (§12 Errata item 1 is the mis-stamp that rule
kills). Both are strictly ADDITIVE and DIGEST-INERT: no campaign row field
moves, so the 18.21 double-run row digest is unchanged; the work-dir
no-clobber preflight extends to the new artifacts.

Deterministic end-to-end on the fake/surrogate path: every RNG stream derives
from ``master_seed`` via :func:`training.bakeoff.es.derive_stream_seed`, all
iteration is over sorted structures, and two identical runs emit identical
rows — :meth:`CoevoCampaignResult.digest` is the double-run pin.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Generic, Literal, TypeAlias, TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from agents.tactical.features import weights_to_hex_json
from engine.world import load_canonical_map
from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from orchestrator.game import (
    DEFAULT_MAX_TICKS,
    MeetingRunner,
    build_default_meeting_runner,
)
from training.bakeoff.es import (
    ESConfig,
    ESResult,
    derive_stream_seed,
    evolve,
    random_genome,
)
from training.bakeoff.goodhart import MeetingRunnerFactory
from training.bakeoff.harness import (
    BAKEOFF_NUM_IMPOSTORS,
    BAKEOFF_NUM_PLAYERS,
    BAKEOFF_TASKS_PER_CREWMATE,
    CONVICTION_ARTIFACT_DIR,
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    SURROGATE_ARTIFACT_DIR,
    BakeoffPolicy,
    ConvictionFitnessTerm,
    DecisionTrace,
    inner_episode_fitness,
)
from training.bakeoff.map_elites import load_archive_cell_genomes

# The CONSUMER's masked-MLP builder (``_load_candidate_policy`` rebuilds through
# exactly this): the preflight runs it at the declared ``hidden`` width so a
# mis-declared width fails before the campaign, not after.
from training.bakeoff.policy_es import build_masked_mlp_policy

# The utility family's encoder tag names the ONE impostor family that rebuilds
# without a ``hidden`` width (the same private-alias import realpath.py uses).
from training.bakeoff.utility_es import ENCODER_VERSION as _UTILITY_ENCODER_VERSION
from training.coevo.factory import CREW_ENCODER_NAMESPACE_PREFIX
from training.coevo.hall_of_fame import (
    DEFAULT_ANCHOR_POLICY,
    DEFAULT_COEVO_ARTIFACT_ROOT,
    DEFAULT_EXPLORATION_FLOOR,
    TRAINED_AGAINST_FSM,
    HallOfFame,
    LoadableArtifactMetadata,
    OpponentStalenessCap,
    OpponentStalenessLedger,
    Side,
    sample_opponents,
    write_loadable_artifact,
)
from training.coevo.rollout import CoevoRolloutResult, rollout_coevo
from training.composed_runner import (
    load_composed_runner_factory,
    load_composed_verdict,
)
from training.conviction.model import (
    ConvictionPrediction,
    ConvictionUseCounter,
    load_conviction_staleness_cap,
)
from training.conviction.serving import ConvictionServingMeetingRunner
from training.crew.scorer import (
    CrewDecisionTrace,
    CrewTrackPolicy,
    crew_inner_episode_fitness,
)
from training.surrogate.ballots import load_staleness_cap
from training.surrogate.runner import SurrogateUseCounter

# --------------------------------------------------------------------------- #
# Module constants (the driver-owned campaign constants).                      #
# --------------------------------------------------------------------------- #

#: The campaign row schema identity (rows are consumed by 18.24's report).
COEVO_CAMPAIGN_ROW_SCHEMA_VERSION: Final[str] = "coevo-campaign-v1"

#: ``origin`` for a champion frozen at a swap boundary by this driver.
SWAP_CHAMPION_ORIGIN: Final[str] = "alternating-freeze-champion"

#: ``origin`` for an exploiter-probe find frozen mid-swap by this driver.
EXPLOITER_ORIGIN: Final[str] = "exploiter-probe"

#: ``origin`` for a PER-GENERATION champion persisted beside the campaign rows
#: (Task 18.31 fix 2). These are NOT hall members — they are the intermediate
#: genomes the 18.24 campaign had to re-breed and hand-stamp after the fact
#: (report §11 defect 2 / F1: 66 real games and two recovery passes), persisted
#: here as loadable artifacts the moment they exist.
GENERATION_CHAMPION_ORIGIN: Final[str] = "generation-champion"

#: The ``stamp.json`` ``method`` every driver freeze records — the training
#: method that produced the genome (the committed 18.24 members' value).
COEVO_FREEZE_METHOD: Final[str] = "alternating-freeze-es"

#: The default stamp-grade run label. A real campaign names its run (e.g.
#: ``"run-01-utility-champion"``); the default keeps the field additive and
#: digest-inert for existing configurations.
DEFAULT_RUN_LABEL: Final[str] = "coevo-campaign"

#: The impostor encoder families the CONSUMING entry point can actually rebuild:
#: ``scripts/run_tournament.py`` ``_load_candidate_policy`` sends the utility tag
#: to ``build_utility_scorer_policy`` and EVERY other tag to
#: ``build_masked_mlp_policy``, whose ``policy_es._encoder_for_version`` accepts
#: only ``"v2"`` / ``"v3"``. A campaign pinning any other impostor family would
#: freeze artifacts nothing can load — and would only discover it after paying
#: for every generation (Codex review on PR #314), so the pin is refused up
#: front. Restated here (the hall_of_fame restated-literal idiom) rather than
#: importing a private symbol across the seam; ``training.realpath``'s
#: ``_SUPPORTED_ENCODER_VERSIONS`` states the same set for the same reason. A
#: new family extends BOTH lists and the builder dispatch — never just this one.
_LOADABLE_IMPOSTOR_ENCODERS: Final[tuple[str, ...]] = (
    _UTILITY_ENCODER_VERSION,
    "v2",
    "v3",
)

#: The CREW families ``scripts/run_tournament.py``'s ``_load_crew_artifact_policy``
#: can rebuild — the same rule as the impostor list above, which the round-4
#: crew guard left unstated: the 18.19 namespace check only proves a tag starts
#: with ``crew-``, so ``crew-option-features-v9`` passed it and froze artifacts
#: nothing can load (Codex review on PR #314). Restated literals, per the
#: hall_of_fame idiom; a new crew family extends this AND the loader dispatch.
_LOADABLE_CREW_ENCODERS: Final[tuple[str, ...]] = (
    "crew-option-features-v1",
    "crew-option-features-v2",
)

#: The stated fake-path game-count ceiling (the integration-risk guard): at the
#: measured ~0.5 s/fake game this is a same-day run, never a week-long one. A
#: configuration whose :func:`projected_game_bound` exceeds the configured
#: ceiling is refused unless ``allow_over_ceiling=True``.
DEFAULT_GAME_CEILING: Final[int] = 25_000

#: The driver-owned default opponent staleness cap (generations one frozen
#: member may serve this run before retire-and-replace). 18.24 may tighten it
#: per campaign via ``CoevoCampaignConfig.staleness_cap``.
DEFAULT_OPPONENT_STALENESS_CAP: Final[OpponentStalenessCap] = OpponentStalenessCap(
    max_generations=8, unit="generations"
)

# Restated literal mirroring ``training.composed_runner._COMPOSED_ARTIFACT_DIR``
# (private there — the hall_of_fame restated-literal idiom): the committed
# composed-verdict artifact dir the gated adoption path defaults to.
COMPOSED_ARTIFACT_DIR: Final[Path] = Path("training/artifacts/composed")

#: The machine-readable campaign rows land here under ``work_dir``.
CAMPAIGN_ROWS_FILENAME: Final[str] = "campaign-rows.jsonl"

#: The up-front budget log lands here under ``work_dir``.
CAMPAIGN_PLAN_FILENAME: Final[str] = "campaign-plan.json"

#: Per-generation champions land under ``<work_dir>/gen-champions/gen-<N>/<sha>/``
#: as four-file loadable artifacts (Task 18.31 fix 2) — BESIDE the rows file,
#: never inside it: the row schema, and therefore
#: :meth:`CoevoCampaignResult.digest`, does not move.
GEN_CHAMPIONS_DIRNAME: Final[str] = "gen-champions"

# Deterministic stream tags for ``derive_stream_seed`` (arbitrary fixed ints;
# distinct tags can never collide by construction of the stream derivation).
_STREAM_INIT: Final[int] = 1821
_STREAM_ES: Final[int] = 1822
_STREAM_SLATE: Final[int] = 1823
_STREAM_EXPLOITER: Final[int] = 1824

# A stable per-side ordinal for seed-stream derivation.
_SIDE_ORDINAL: Final[Mapping[Side, int]] = {"impostor": 0, "crew": 1}

_SHA256_HEX_RE: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{64}")

#: Which committed substrate-sha definition the campaign passed to
#: ``HallOfFame.create`` (the 18.24 block: two definitions exist and the
#: driver must name the one it uses, in the row schema).
SubstrateShaKind: TypeAlias = Literal["compute_substrate_sha", "bakeoff_substrate_sha"]

#: Which meeting runner served the swap's TRAINING games (benchmark/exploiter
#: games are always ``fake-provider`` — champion numbers are never
#: composed-runner-scored).
MeetingRunnerKind: TypeAlias = Literal["fake-provider", "composed", "custom"]

PolicyT = TypeVar("PolicyT")


def _genome_sha(genome: Sequence[float]) -> str:
    """The would-be hall-of-fame identity of ``genome`` (float-hex byte digest).

    Exactly the digest :meth:`HallOfFame.add_member` derives — computed here so
    provenance (an exploiter's ``trained_against``, the row's champion sha) can
    name a genome BEFORE (or without) freezing it.
    """

    weights_json = weights_to_hex_json(tuple(genome)) + "\n"
    return hashlib.sha256(weights_json.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# The two additive seams.                                                      #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CoevoScenarioTerm:
    """One named additive scenario fitness term (the 18.23 seam's unit).

    ``fitness`` MUST be a pure deterministic function of the genome (the ES
    purity contract — a nondeterministic term is the only way a provider can
    break the double-run digest); its value ADDS to the moving side's slate
    fitness for every genome evaluated during the swap it was provided for.
    ``label`` rides the campaign rows as provenance.
    """

    label: str
    fitness: Callable[[tuple[float, ...]], float]


#: The per-swap scenario-provider seam (18.23 implements a conformer): called
#: once per swap with ``(swap_index, moving_side)``; the returned terms apply
#: to that swap's ES fitness only. Unset ⇒ inert (digest-identical).
CoevoScenarioProvider: TypeAlias = Callable[[int, Side], Sequence[CoevoScenarioTerm]]


@dataclass(frozen=True)
class CoevoComposedRunnerConfig:
    """The campaign configuration adopting 18.29's composed meeting runner.

    Adoption happens ONLY through
    :func:`training.composed_runner.load_composed_runner_factory` on its
    DEFAULT gated path: ``composed_artifact_dir`` is typed ``Path`` (never
    ``None``), so the committed-GO gate + component-sha cross-check always run
    — the diagnostics-only ``None`` escape is structurally unreachable from a
    campaign configuration. The driver loads (and re-validates) the factory at
    each swap boundary, threads its two component use-counters ONCE per run
    (cumulative), and surfaces ``verdict.json.adoption_constraints`` verbatim
    in every campaign row.
    """

    conviction_artifact_dir: Path = CONVICTION_ARTIFACT_DIR
    surrogate_artifact_dir: Path = SURROGATE_ARTIFACT_DIR
    composed_artifact_dir: Path = COMPOSED_ARTIFACT_DIR
    corpus_dir: Path | None = None


# --------------------------------------------------------------------------- #
# Configuration.                                                               #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class CoevoSideConfig(Generic[PolicyT]):
    """One side's entrant configuration (the per-side campaign constants).

    ``build_policy`` turns a flat genome into the side's frozen policy (the
    committed artifact-reload seam: ``build_utility_scorer_policy`` /
    ``build_masked_mlp_policy`` / ``build_crew_scorer``). ``encoder_version``
    PINS the policy family for the campaign (the 18.22 hand-off; ``"v2"`` is
    the free-policy-family default): the built policy's ``encoder_version``
    must equal the pin, checked before any game — a hall/side stays
    SINGLE-FAMILY per campaign, and every frozen-member reload is
    length-checked against ``genome_length`` so a mixed family fails loud at
    reload, never deep in an encoder. ``anchor_policy`` (impostor side only —
    the crew trace has no anchor seam) re-keys the side's anchor CE onto a
    FIXED alternative anchor artifact (the 18.5 filtered-BC seam); it is
    config, never an accumulator, and never the moving opponent.
    ``exploration_floor`` applies when THIS side's hall is sampled as the
    opponent pool. ``initial_genome`` seeds the side's standing champion
    (18.24 seeds entrants from committed champions/study candidates); ``None``
    draws a ``random_genome`` from the campaign master seed.
    ``founder_cells_dir`` (the 18.6 artifact dir — the parent of its
    ``cells/`` tree, exactly what ``ingest_map_elites_founders`` takes)
    ingests MAP-Elites cells as behaviorally diverse founders through the
    substrate-fenced ingest BEFORE any pool build or sampling.

    Two ADDITIVE, default-valued, DIGEST-INERT stamp-metadata fields (Task
    18.31 — they ride no campaign row, so the row digest cannot move):
    ``hidden`` is the masked-MLP head width every freeze on this side stamps
    into its ``config.json`` (REQUIRED for a non-utility impostor family — the
    consumer rebuilds through it, and re-deriving it from genome length is
    exactly the ambiguity the 18.24 report's §12 Errata item 1 records the cost
    of), and ``anchor_policy_label`` NAMES the anchor artifact in the stamp
    (``fsm-default`` = the scripted FSM proposal; a side that actually carries
    an ``anchor_policy`` must name it, else every frozen member mis-stamps its
    anchor).
    """

    side: Side
    genome_length: int
    build_policy: Callable[[tuple[float, ...]], PolicyT]
    encoder_version: str = "v2"
    population: int = 6
    sigma: float = 0.15
    init_scale: float = 0.5
    anchor_weight: float = DEFAULT_ANCHOR_PENALTY_WEIGHT
    exploration_floor: float = DEFAULT_EXPLORATION_FLOOR
    initial_genome: tuple[float, ...] | None = None
    anchor_policy: BakeoffPolicy | None = None
    founder_cells_dir: Path | None = None
    hidden: int | None = None
    anchor_policy_label: str = DEFAULT_ANCHOR_POLICY


@dataclass(frozen=True)
class CoevoCampaignConfig:
    """The full alternating-freeze campaign configuration (Task 18.21).

    ``substrate_sha256`` + ``substrate_sha_kind`` pin the campaign substrate
    and NAME which committed definition produced it
    (``training.anchor_study.compute_substrate_sha`` composite vs
    ``training.bakeoff.map_elites.bakeoff_substrate_sha`` raw MANIFEST) — both
    ride every row. ``hall_root=None`` resolves to the contract-named
    :data:`~training.coevo.hall_of_fame.DEFAULT_COEVO_ARTIFACT_ROOT`; tests
    pass a tmp path. ``payoff_seeds`` is REQUIRED and non-empty: the payoff
    row (the PFSP hardness weighting) is measured fresh each generation with
    exact pool cover, so the sampler's empty-map cold-start branch is never
    taken — the contract allows the empty map ONLY as the gen-1 cold-start
    exception, never as a whole-campaign PFSP bypass. ``meeting_runner_factory``
    (the generic future-GO-verdict-runner slot) and ``composed`` (the gated
    18.29 adoption) are mutually exclusive; both serve TRAINING games only.

    ``run_label`` (Task 18.31) is the ADDITIVE, default-valued, DIGEST-INERT
    stamp-grade run name every frozen artifact records (``policy_id`` /
    ``campaign`` / ``entrant`` / ``source_lineage``) — the provenance the 18.24
    record had to be reconstructed with by hand. It rides no campaign row.
    """

    work_dir: Path
    substrate_sha256: str
    substrate_sha_kind: SubstrateShaKind
    impostor: CoevoSideConfig[BakeoffPolicy]
    crew: CoevoSideConfig[CrewTrackPolicy]
    master_seed: int
    num_swaps: int
    generations_per_swap: int
    fitness_seeds: tuple[int, ...]
    benchmark_seeds: tuple[int, ...]
    payoff_seeds: tuple[int, ...]
    slate_size: int = 3
    first_side: Side = "impostor"
    hall_root: Path | None = None
    staleness_cap: OpponentStalenessCap = DEFAULT_OPPONENT_STALENESS_CAP
    exploiter_population: int = 5
    exploiter_generations: int = 6
    num_players: int = BAKEOFF_NUM_PLAYERS
    num_impostors: int = BAKEOFF_NUM_IMPOSTORS
    tasks_per_crewmate: int = BAKEOFF_TASKS_PER_CREWMATE
    max_ticks: int = DEFAULT_MAX_TICKS
    conviction: ConvictionFitnessTerm | None = None
    meeting_runner_factory: MeetingRunnerFactory | None = None
    composed: CoevoComposedRunnerConfig | None = None
    scenario_provider: CoevoScenarioProvider | None = None
    game_ceiling: int = DEFAULT_GAME_CEILING
    allow_over_ceiling: bool = False
    run_label: str = DEFAULT_RUN_LABEL

    @property
    def resolved_hall_root(self) -> Path:
        return (
            self.hall_root
            if self.hall_root is not None
            else DEFAULT_COEVO_ARTIFACT_ROOT
        )


# --------------------------------------------------------------------------- #
# The campaign row (the machine-readable truth 18.24's report reads).          #
# --------------------------------------------------------------------------- #


class CoevoCampaignRow(BaseModel):
    """One driver generation's full stabilizer readout (Task 18.21 public type).

    Everything 18.24's report needs, per generation: the per-gen fitness
    channel (``champion_fitness`` / ``generation_best_fitness`` vs the slate),
    the absolute anchor benchmark BOTH directions
    (``anchor_benchmark_champion_side`` = the moving champion's own-side
    fitness vs the scripted FSM; ``anchor_benchmark_fsm_side`` = the scripted
    side's fitness in the SAME games — flat-anchor + oscillating
    ``opponent_payoffs`` is the fo2 cycling signature), the opponent slate
    shas (draw order, with replacement; the reserved
    :data:`~training.coevo.hall_of_fame.TRAINED_AGAINST_FSM` sentinel when the
    pool is empty and the frozen side is the scripted FSM), the exploiter
    outcome, and the conviction/surrogate consumption columns (cumulative
    counter reads; ``None`` = the instrument is structurally absent, never a
    zero-ghost — under a composed configuration these are BOTH component
    counters: gate reads + probe reads). ``substrate_sha_kind`` names which
    committed sha definition the campaign passed to ``HallOfFame.create``.
    Swap-boundary freeze provenance (``champion_frozen*``) rides the swap's
    final generation row.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = COEVO_CAMPAIGN_ROW_SCHEMA_VERSION
    swap_index: int = Field(ge=0)
    generation_index: int = Field(ge=1)
    generation_in_swap: int = Field(ge=1)
    moving_side: Side
    frozen_side: Side
    moving_encoder_version: str
    frozen_encoder_version: str
    substrate_sha256: str = Field(min_length=64, max_length=64)
    substrate_sha_kind: SubstrateShaKind
    meeting_runner: MeetingRunnerKind
    scenario_labels: tuple[str, ...]
    opponent_pool_size: int = Field(ge=0)
    opponent_slate_shas: tuple[str, ...]
    opponent_payoffs: Mapping[str, float] | None
    opponent_uses: Mapping[str, int]
    retired_opponent_shas: tuple[str, ...]
    champion_fitness: float
    generation_best_fitness: float
    champion_updated: bool
    champion_weights_sha256: str = Field(min_length=64, max_length=64)
    moving_anchor_ce_mean: float
    anchor_benchmark_champion_side: float
    anchor_benchmark_fsm_side: float
    exploiter_fitness: float
    exploiter_baseline_fitness: float
    exploiter_outcome: Literal["frozen", "duplicate", "not-found"]
    exploiter_sha: str | None
    champion_frozen: bool
    champion_frozen_sha: str | None
    champion_trained_against: str | None
    frozen_champion_sha: str | None
    conviction_uses: int | None
    surrogate_uses: int | None
    adoption_constraints: tuple[str, ...]
    games_played_generation: int = Field(ge=0)
    games_played_cumulative: int = Field(ge=0)

    @field_validator("opponent_payoffs", mode="after")
    @classmethod
    def _freeze_payoffs(
        cls, value: Mapping[str, float] | None
    ) -> Mapping[str, float] | None:
        # A read-only proxy over a PRIVATE copy (the HallOfFameMember
        # descriptors idiom): ``frozen=True`` alone leaves the nested mapping
        # mutable through the attribute, and a caller-side mutation after
        # ``_emit`` would silently drift ``to_json_line``/``digest`` away from
        # the on-disk JSONL (Codex review on PR #311).
        return None if value is None else MappingProxyType(dict(value))

    @field_validator("opponent_uses", mode="after")
    @classmethod
    def _freeze_uses(cls, value: Mapping[str, int]) -> Mapping[str, int]:
        return MappingProxyType(dict(value))

    @field_serializer("opponent_payoffs")
    def _serialize_payoffs(
        self, value: Mapping[str, float] | None
    ) -> dict[str, float] | None:
        # pydantic cannot serialise a mappingproxy; hand it a plain dict.
        return None if value is None else dict(value)

    @field_serializer("opponent_uses")
    def _serialize_uses(self, value: Mapping[str, int]) -> dict[str, int]:
        return dict(value)

    def to_json_line(self) -> str:
        return json.dumps(self.model_dump(mode="json"), sort_keys=True)


@dataclass(frozen=True)
class CoevoCampaignResult:
    """The finished campaign: rows + grown halls + the double-run digest pin.

    ``gen_champions_dir`` (Task 18.31) locates the per-generation champion
    artifacts written beside ``rows_path``; it names a location only, so
    :meth:`digest` — computed over the row bytes alone — is unaffected.
    """

    rows: tuple[CoevoCampaignRow, ...]
    impostor_hall: HallOfFame
    crew_hall: HallOfFame
    impostor_champion: tuple[float, ...]
    crew_champion: tuple[float, ...]
    total_games: int
    projected_game_bound: int
    rows_path: Path
    gen_champions_dir: Path

    def digest(self) -> str:
        """SHA-256 over the emitted row bytes — the determinism pin."""

        hasher = hashlib.sha256()
        for row in self.rows:
            hasher.update(row.to_json_line().encode("utf-8"))
            hasher.update(b"\n")
        return hasher.hexdigest()


# --------------------------------------------------------------------------- #
# The up-front budget guard.                                                   #
# --------------------------------------------------------------------------- #


def _count_founder_cells(founder_cells_dir: Path | None) -> int:
    """How many MAP-Elites cells a founder dir would ingest (0 when unset).

    Counts the ``<i>-<j>-<k>`` subdirectories of the 18.6 ``cells/`` tree
    (``founder_cells_dir`` is the artifact dir the ingest reads — the parent
    of ``cells/``, exactly what ``ingest_map_elites_founders`` takes); a
    configured-but-missing tree fails loud HERE (before any disk mutation)
    rather than at ingest time.
    """

    if founder_cells_dir is None:
        return 0
    cells_dir = founder_cells_dir / "cells"
    if not cells_dir.is_dir():
        raise ValueError(
            f"founder_cells_dir {founder_cells_dir} is configured but holds no "
            "cells/ tree (expected the 18.6 write_archive_cell_artifacts layout)"
        )
    return sum(1 for child in cells_dir.iterdir() if child.is_dir())


def projected_game_bound(config: CoevoCampaignConfig) -> int:
    """A stated UPPER BOUND on the campaign's fake-path game count.

    Computed up front (the integration-risk guard): per driver generation the
    ES step costs at most ``(1 + population) × slate_size × |fitness_seeds|``
    games (the incumbent re-evaluates each generation; slate dedup can only
    lower the actual count), the payoff row at most ``pool_bound ×
    |payoff_seeds|`` where ``pool_bound`` is every member either hall could
    ever hold (founders + one champion per swap + one exploit per
    generation), the benchmark exactly ``|benchmark_seeds|``, and the
    exploiter probe ``(1 + exploiter_population × exploiter_generations) ×
    |benchmark_seeds|``. Scenario-provider terms are the provider's own
    budget and deliberately outside this bound (the seam is opaque here).
    """

    founders = _count_founder_cells(
        config.impostor.founder_cells_dir
    ) + _count_founder_cells(config.crew.founder_cells_dir)
    total_generations = config.num_swaps * config.generations_per_swap
    pool_bound = founders + config.num_swaps + total_generations
    max_population = max(config.impostor.population, config.crew.population)
    es_per_generation = (
        (1 + max_population) * config.slate_size * len(config.fitness_seeds)
    )
    payoff_per_generation = pool_bound * len(config.payoff_seeds)
    benchmark_per_generation = len(config.benchmark_seeds)
    exploiter_per_generation = (
        1 + config.exploiter_population * config.exploiter_generations
    ) * len(config.benchmark_seeds)
    return total_generations * (
        es_per_generation
        + payoff_per_generation
        + benchmark_per_generation
        + exploiter_per_generation
    )


# --------------------------------------------------------------------------- #
# Validation (fail loud BEFORE any disk mutation or game).                     #
# --------------------------------------------------------------------------- #


def _validate_seeds(name: str, seeds: tuple[int, ...]) -> None:
    if not seeds:
        raise ValueError(f"{name} must be non-empty")
    if len(set(seeds)) != len(seeds):
        raise ValueError(
            f"{name} must be unique, got {seeds!r}: a duplicate seed silently "
            "double-weights that seed's games"
        )


def _validate_side(
    config: CoevoSideConfig[Any], *, expected_side: Side, master_seed: int
) -> tuple[float, ...]:
    """Validate one side's config; return its resolved initial genome.

    Builds a probe policy from the initial genome and pins the family: the
    policy's ``encoder_version`` must equal the config pin, and the crew
    namespace guard (the 18.19 conflation-guard convention) must hold — a
    wrong-family builder fails HERE, before any hall exists.
    """

    if config.side != expected_side:
        raise ValueError(
            f"the {expected_side} slot carries a CoevoSideConfig for side "
            f"{config.side!r} — the two side configs are not interchangeable"
        )
    if config.genome_length < 1:
        raise ValueError(f"genome_length must be >= 1, got {config.genome_length}")
    if config.population < 1:
        raise ValueError(f"population must be >= 1, got {config.population}")
    # The finiteness checks mirror anchor_weight's: ``inf > 0`` is True, so a
    # bare positivity check would let a non-finite knob from a deserialized
    # config reach the ES/rollout layers before failing (Codex review on
    # PR #311 — fail before any training artifact is written).
    if not math.isfinite(config.sigma) or not config.sigma > 0.0:
        raise ValueError(f"sigma must be finite and > 0, got {config.sigma!r}")
    if not math.isfinite(config.init_scale) or not config.init_scale > 0.0:
        raise ValueError(
            f"init_scale must be finite and > 0, got {config.init_scale!r}"
        )
    if not math.isfinite(config.anchor_weight) or config.anchor_weight < 0.0:
        raise ValueError(
            f"anchor_weight must be finite and >= 0, got {config.anchor_weight!r}"
        )
    if not math.isfinite(config.exploration_floor) or config.exploration_floor < 0.0:
        raise ValueError(
            f"exploration_floor must be finite and >= 0, got "
            f"{config.exploration_floor!r}"
        )
    if expected_side == "crew" and config.anchor_policy is not None:
        raise ValueError(
            "the crew side has no anchor-policy seam (CrewDecisionTrace anchors "
            "on the scripted FSM only); anchor_policy belongs to the impostor "
            "side config"
        )
    # The anchor identity is enforced in BOTH directions (Codex review on
    # PR #314): a custom anchor must be named, AND a name must correspond to a
    # custom anchor. One-directional enforcement still permits a campaign that
    # trains against the scripted FSM while every stamp claims some other
    # artifact — the same mis-stamp defect, mirrored. A blank/unsafe label
    # falls through to the stamp-token validation (which names the real
    # problem) rather than being reported as a mismatched anchor.
    if config.anchor_policy is not None and (
        config.anchor_policy_label == DEFAULT_ANCHOR_POLICY
    ):
        raise ValueError(
            f"the {expected_side} side config carries an anchor_policy but its "
            f"anchor_policy_label is still {DEFAULT_ANCHOR_POLICY!r}; name the "
            "anchor artifact so every frozen member's stamp records the anchor "
            "it was actually bred against"
        )
    if (
        config.anchor_policy is None
        and config.anchor_policy_label.strip()
        and config.anchor_policy_label != DEFAULT_ANCHOR_POLICY
    ):
        raise ValueError(
            f"the {expected_side} side config names anchor_policy_label "
            f"{config.anchor_policy_label!r} but supplies no anchor_policy, so it "
            f"trains against the scripted FSM; a stamp claiming another anchor "
            f"is false provenance (use {DEFAULT_ANCHOR_POLICY!r}, or supply the "
            "anchor artifact the label names)"
        )

    if config.initial_genome is not None:
        initial = tuple(float(gene) for gene in config.initial_genome)
        if len(initial) != config.genome_length:
            raise ValueError(
                f"{expected_side} initial_genome length {len(initial)} != "
                f"genome_length {config.genome_length}"
            )
        if not all(math.isfinite(gene) for gene in initial):
            # A corrupted seed artifact/config must fail here — a NaN genome
            # can play whole games and even freeze NaN weights into a hall
            # (Codex review on PR #311), never a loud stop downstream.
            raise ValueError(
                f"{expected_side} initial_genome contains non-finite genes; a "
                "corrupted seed never enters the campaign"
            )
    else:
        initial = random_genome(
            config.genome_length,
            seed=derive_stream_seed(
                master_seed, _STREAM_INIT, _SIDE_ORDINAL[expected_side]
            ),
            scale=config.init_scale,
        )

    probe = config.build_policy(initial)
    probe_encoder = cast(str, probe.encoder_version)
    if probe_encoder != config.encoder_version:
        raise ValueError(
            f"the {expected_side} side config pins encoder_version "
            f"{config.encoder_version!r} but build_policy produced "
            f"{probe_encoder!r} — the campaign family pin and the builder "
            "drifted apart (a hall/side stays single-family per campaign)"
        )
    is_crew_namespace = probe_encoder.startswith(CREW_ENCODER_NAMESPACE_PREFIX)
    if expected_side == "crew" and not is_crew_namespace:
        raise ValueError(
            f"the crew side built a non-crew policy (encoder_version="
            f"{probe_encoder!r}); every crew encoder tag starts with "
            f"{CREW_ENCODER_NAMESPACE_PREFIX!r} (the 18.19 conflation guard)"
        )
    if expected_side == "impostor" and is_crew_namespace:
        raise ValueError(
            f"the impostor side built a crew policy (encoder_version="
            f"{probe_encoder!r}); crew encoder tags never belong in the "
            "impostor slot (the 18.19 conflation guard)"
        )
    # The freeze-stamp family rule (Task 18.31), checked AFTER the family pin so
    # a drifted pin still reports itself first. Every impostor family except the
    # utility scorer rebuilds through ``build_masked_mlp_policy``, whose
    # ``hidden`` width the consumer reads from the artifact's config.json
    # (``scripts/run_tournament.py`` ``_read_candidate_hidden``): a side that
    # freezes without declaring it produces unloadable artifacts.
    if config.hidden is not None and config.hidden < 1:
        raise ValueError(
            f"the {expected_side} side config declares hidden={config.hidden!r}; "
            "a masked-MLP head width must be >= 1"
        )
    if expected_side == "crew" and probe_encoder not in _LOADABLE_CREW_ENCODERS:
        # The same consumer-loadability preflight the impostor side gets. The
        # crew loader (`scripts/run_tournament.py` `_load_crew_artifact_policy`)
        # dispatches on the stamp and rebuilds only these two families, so any
        # other `crew-*` tag passes the 18.19 namespace guard and still freezes
        # artifacts nothing can load — discovered after the campaign ran
        # (Codex review on PR #314).
        raise ValueError(
            f"the crew family {probe_encoder!r} is not one the consuming entry "
            f"point can rebuild (loadable: {_LOADABLE_CREW_ENCODERS!r}); every "
            "artifact this campaign froze would be unloadable through "
            "_load_crew_artifact_policy, discovered only after the generations "
            "were paid for — refusing before the first game"
        )
    if expected_side == "crew" and config.hidden is not None:
        # The crew scorer rebuilds through ``build_crew_scorer``, which takes NO
        # head width, so a declared one would stamp every crew freeze's
        # config.json with a masked-MLP width its family does not have — the
        # same false provenance the utility-family guard below rejects, and it
        # was reachable because the family rules sat inside the impostor branch
        # (Codex review on PR #314).
        raise ValueError(
            f"the crew family ({probe_encoder!r}) takes no hidden width; got "
            f"hidden={config.hidden!r}. Declaring one would stamp every frozen "
            "crew artifact with a width its builder does not have"
        )
    if expected_side == "impostor":
        if probe_encoder not in _LOADABLE_IMPOSTOR_ENCODERS:
            raise ValueError(
                f"the impostor family {probe_encoder!r} is not one the consuming "
                f"entry point can rebuild (loadable: {_LOADABLE_IMPOSTOR_ENCODERS!r}); "
                "every artifact this campaign froze would be unloadable through "
                "_load_candidate_policy, discovered only after the generations "
                "were paid for — refusing before the first game"
            )
        if probe_encoder == _UTILITY_ENCODER_VERSION and config.hidden is not None:
            # The utility scorer takes NO head width, so a declared one would
            # put a false masked-MLP width into every artifact's config.json.
            # ``RealPathCandidate`` rejects the same combination for the same
            # family (Codex review on PR #314).
            raise ValueError(
                f"the utility family ({_UTILITY_ENCODER_VERSION!r}) takes no hidden "
                f"width; got hidden={config.hidden!r}. Declaring one would stamp "
                "every frozen artifact with a width its family does not have"
            )
        if probe_encoder != _UTILITY_ENCODER_VERSION and config.hidden is None:
            raise ValueError(
                f"the impostor family {probe_encoder!r} rebuilds through the "
                "masked-MLP builder, so every artifact it freezes needs an integer "
                "'hidden' in config.json; declare it on the side config (it is "
                "NEVER re-derived from genome length — the 18.24 report §12 Errata "
                "item 1 is the cost of guessing)"
            )
        if probe_encoder != _UTILITY_ENCODER_VERSION and config.hidden is not None:
            # A DECLARED width that is not the width ``build_policy`` actually
            # captured is a silent mis-stamp: training succeeds, every artifact
            # records the wrong number, and ``_load_candidate_policy`` rebuilds
            # with it and rejects the genome length — after the campaign ran
            # (Codex review on PR #314). Proving it means running the CONSUMER's
            # own builder at the declared width over the real genome, which is
            # exactly the reconstruction the artifact will have to survive.
            try:
                build_masked_mlp_policy(
                    initial,
                    game_map=load_canonical_map(),
                    hidden=config.hidden,
                    encoder_version=probe_encoder,
                )
            except ValueError as exc:
                raise ValueError(
                    f"the impostor side declares hidden={config.hidden} for family "
                    f"{probe_encoder!r}, but the consuming builder cannot rebuild a "
                    f"{len(initial)}-gene genome at that width ({exc}); every "
                    "artifact this campaign froze would be unloadable"
                ) from exc
    return initial


def _preflight_fresh_hall_root(hall_root: Path) -> None:
    """Refuse a dirty hall root for EITHER side before creating ANY hall.

    ``HallOfFame.create`` runs the same two refusals per side, but creating
    side-by-side would mutate the first side before discovering the second
    side's dirt — a half-initialized campaign tree whose retry then trips on
    the freshly created half instead of the original problem (Codex review on
    PR #311). The checks are restated read-only over BOTH sides (the
    hall_of_fame restated-literal idiom — its filename constant is private),
    with ``create``'s own guards remaining the authoritative backstop.
    """

    for side in ("impostor", "crew"):
        side_dir = hall_root / side
        index_path = side_dir / "hall_of_fame.json"
        if index_path.exists():
            raise FileExistsError(
                f"a hall of fame already exists at {index_path}; the campaign "
                "never clobbers a committed pool (pick a fresh hall_root)"
            )
        if side_dir.exists():
            stray = sorted(
                child.name
                for child in side_dir.iterdir()
                if child.name.startswith("gen-")
            )
            if stray:
                raise ValueError(
                    f"cannot create a fresh {side} hall of fame at {side_dir}: "
                    f"stray member artifacts {stray} exist without an index — a "
                    "dirty tree is never silently adopted"
                )


def _side_artifact_metadata(
    config: CoevoCampaignConfig, side_config: CoevoSideConfig[Any]
) -> LoadableArtifactMetadata:
    """The side's stamp-grade freeze metadata (Task 18.31 fix 4).

    ``encoder_version`` / ``hidden`` / ``anchor_policy`` come from the SIDE
    CONFIG — the campaign's declared family — never from a genome length or a
    builder probe. Every freeze on that side (swap champion, exploiter find,
    MAP-Elites founder, and the per-generation champions written beside the
    rows) therefore stamps the same, family-correct identity.

    A module-level function so ``_validate_config`` can CONSTRUCT it as part of
    the preflight: the model's own stamp-token rules (non-blank, MANIFEST-safe)
    would otherwise first run while the halls are being built — after the work
    dir and campaign plan already exist, leaving a half-started campaign tree
    behind a configuration typo (Codex review on PR #314).
    """

    return LoadableArtifactMetadata(
        run_label=config.run_label,
        method=COEVO_FREEZE_METHOD,
        encoder_version=side_config.encoder_version,
        anchor_policy=side_config.anchor_policy_label,
        hidden=side_config.hidden,
        anchor_weight=side_config.anchor_weight,
    )


def _validate_config(
    config: CoevoCampaignConfig,
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Full fail-loud config validation; returns both resolved initial genomes."""

    if config.num_swaps < 1:
        raise ValueError(f"num_swaps must be >= 1, got {config.num_swaps}")
    if config.generations_per_swap < 1:
        raise ValueError(
            f"generations_per_swap must be >= 1, got {config.generations_per_swap}"
        )
    if config.slate_size < 1:
        raise ValueError(f"slate_size must be >= 1, got {config.slate_size}")
    if config.exploiter_population < 1 or config.exploiter_generations < 1:
        raise ValueError(
            "exploiter_population and exploiter_generations must be >= 1 (the "
            "exploiter probe is a contract stabilizer, never disabled); got "
            f"{config.exploiter_population}×{config.exploiter_generations}"
        )
    if config.game_ceiling < 1:
        raise ValueError(f"game_ceiling must be >= 1, got {config.game_ceiling}")
    if config.first_side not in ("impostor", "crew"):
        # A deserialized/untyped config bypasses the Literal, and a typo must
        # never silently run the campaign in the opposite order (Codex review
        # on PR #311).
        raise ValueError(
            f"first_side must be 'impostor' or 'crew'; got {config.first_side!r}"
        )
    if config.substrate_sha_kind not in (
        "compute_substrate_sha",
        "bakeoff_substrate_sha",
    ):
        # Same deserialized-config shape as first_side: without this check the
        # first validation would be CoevoCampaignRow's Literal — AFTER a whole
        # generation's games ran and halls were written (Codex review on
        # PR #311).
        raise ValueError(
            "substrate_sha_kind must be 'compute_substrate_sha' or "
            f"'bakeoff_substrate_sha'; got {config.substrate_sha_kind!r}"
        )
    # The roster/tick knobs reach the seeder/scheduler only inside the first
    # rollout — after the work dir, plan, halls, and rows file exist, whose
    # clobber guard would then block the retry (Codex review on PR #311).
    if config.num_impostors < 1:
        raise ValueError(f"num_impostors must be >= 1, got {config.num_impostors}")
    if config.num_players < config.num_impostors + 1:
        raise ValueError(
            "num_players must be >= num_impostors + 1 (at least one crewmate); "
            f"got {config.num_players} players with {config.num_impostors} "
            "impostors"
        )
    if config.tasks_per_crewmate < 1:
        raise ValueError(
            f"tasks_per_crewmate must be >= 1, got {config.tasks_per_crewmate}"
        )
    canonical_task_count = len(load_canonical_map().tasks)
    if config.tasks_per_crewmate > canonical_task_count:
        # The seeder enforces the same bound — but only inside the first
        # rollout, after the campaign tree exists (Codex review on PR #311).
        raise ValueError(
            f"tasks_per_crewmate must be <= {canonical_task_count} (the "
            f"canonical map's task count); got {config.tasks_per_crewmate}"
        )
    if config.max_ticks < 1:
        raise ValueError(f"max_ticks must be >= 1, got {config.max_ticks}")
    _validate_seeds("fitness_seeds", config.fitness_seeds)
    _validate_seeds("benchmark_seeds", config.benchmark_seeds)
    _validate_seeds("payoff_seeds", config.payoff_seeds)
    if _SHA256_HEX_RE.fullmatch(config.substrate_sha256) is None:
        raise ValueError(
            "substrate_sha256 must be exactly 64 lowercase hex chars; got "
            f"{config.substrate_sha256!r}"
        )
    if config.meeting_runner_factory is not None and config.composed is not None:
        raise ValueError(
            "meeting_runner_factory and composed are mutually exclusive: the "
            "composed runner adopts ONLY through its gated loader, and a second "
            "runner seam beside it would be ambiguous about which served "
            "training games"
        )
    if not config.run_label.strip():
        raise ValueError(f"run_label must be non-blank; got {config.run_label!r}")
    for forbidden, human in (("|", "pipe"), ("\n", "newline"), ("\r", "CR")):
        if forbidden in config.run_label:
            # The label rides every frozen artifact's stamp, whose fields are
            # MANIFEST-safe by contract; a bad label must fail before any hall.
            raise ValueError(
                f"run_label must be MANIFEST-safe (no {human}); got "
                f"{config.run_label!r}"
            )
    rows_path = config.work_dir / CAMPAIGN_ROWS_FILENAME
    if rows_path.exists():
        raise FileExistsError(
            f"campaign rows already exist at {rows_path}; the driver never "
            "clobbers a recorded campaign (pick a fresh work_dir)"
        )
    gen_champions_dir = config.work_dir / GEN_CHAMPIONS_DIRNAME
    if gen_champions_dir.exists():
        # The standing work-dir no-clobber discipline, extended to the 18.31
        # per-generation champion artifacts: they are campaign evidence, so a
        # second run never writes into a recorded tree.
        raise FileExistsError(
            f"per-generation champion artifacts already exist at "
            f"{gen_champions_dir}; the driver never clobbers a recorded "
            "campaign (pick a fresh work_dir)"
        )
    impostor_initial = _validate_side(
        config.impostor, expected_side="impostor", master_seed=config.master_seed
    )
    crew_initial = _validate_side(
        config.crew, expected_side="crew", master_seed=config.master_seed
    )
    # Constructing BOTH sides' freeze metadata is the preflight for every stamp
    # token the campaign will write (run label, anchor label, family): the model
    # validates them here, before the work dir or plan exist, rather than at
    # hall-creation time behind a half-built tree.
    for side_config in (config.impostor, config.crew):
        _side_artifact_metadata(config, side_config)
    return impostor_initial, crew_initial


# --------------------------------------------------------------------------- #
# Internal state.                                                              #
# --------------------------------------------------------------------------- #


@dataclass
class _SideState:
    """One side's mutable campaign state (an explicit object — no globals)."""

    side: Side
    config: CoevoSideConfig[Any]
    hall: HallOfFame
    champion: tuple[float, ...]
    last_frozen_sha: str | None = None


def _ordered_pair(
    moving_side: Side, mover: object, opponent: object
) -> tuple[BakeoffPolicy | None, CrewTrackPolicy | None]:
    """Route (mover, opponent) into rollout_coevo's (impostor, crew) slots."""

    if moving_side == "impostor":
        return (
            cast("BakeoffPolicy | None", mover),
            cast("CrewTrackPolicy | None", opponent),
        )
    return (
        cast("BakeoffPolicy | None", opponent),
        cast("CrewTrackPolicy | None", mover),
    )


def _side_fitness(result: CoevoRolloutResult, side: Side) -> float:
    return result.impostor_fitness if side == "impostor" else result.crew_fitness


def _mean(values: Sequence[float]) -> float:
    return math.fsum(values) / len(values)


class _CampaignEngine:
    """The run-scoped alternating-freeze loop (constructed once per campaign)."""

    def __init__(self, config: CoevoCampaignConfig) -> None:
        impostor_initial, crew_initial = _validate_config(config)
        self._config = config
        self._bound = projected_game_bound(config)
        if self._bound > config.game_ceiling and not config.allow_over_ceiling:
            raise ValueError(
                f"the projected fake-path game bound {self._bound} exceeds the "
                f"stated ceiling {config.game_ceiling} "
                "(population × generations × seeds × slate compounds — the "
                "integration-risk guard); shrink the configuration or pass "
                "allow_over_ceiling=True to run it deliberately"
            )

        # The run-scoped meters, resolved ONCE (threaded, cumulative — the
        # resolved_conviction_term() pattern). Reading committed caps fails
        # loud here, before any disk mutation.
        self._conviction_counter: ConvictionUseCounter | None = None
        self._surrogate_counter: SurrogateUseCounter | None = None
        if config.conviction is not None:
            self._conviction_counter = config.conviction.use_counter
        if config.composed is not None:
            if self._conviction_counter is None:
                self._conviction_counter = ConvictionUseCounter(
                    load_conviction_staleness_cap(
                        config.composed.conviction_artifact_dir
                    )
                )
            self._surrogate_counter = SurrogateUseCounter(
                load_staleness_cap(config.composed.surrogate_artifact_dir)
            )
            # The adoption gate runs once up front too (fail loud BEFORE the
            # halls are created), then again at every swap boundary.
            self._load_composed_factory()
        # The conviction term is served live on training games ONLY on the
        # non-composed path — the composed runner's own gate reads meter the
        # same shared counter, and a second serving wrap would double-meter
        # every meeting.
        self._serve_conviction = config.conviction is not None and (
            config.composed is None
        )
        # A meter already spent at campaign start is refused HERE — before the
        # plan, rows file, or either hall exists (Codex review on PR #311) —
        # not discovered at the first swap boundary behind a half-built tree.
        self._check_meters_at_boundary(0)

        # Disk: preflight founder archives + BOTH hall roots read-only, then
        # plan log, rows file, the two per-side halls, founders, ledger.
        hall_root = config.resolved_hall_root
        for side_config in (config.impostor, config.crew):
            if side_config.founder_cells_dir is not None:
                # The substrate-fenced loader ingest re-runs at ingest time;
                # running it read-only FIRST means a stale/corrupt founder
                # archive fails before any mkdir or hall exists (Codex review
                # on PR #311).
                load_archive_cell_genomes(
                    side_config.founder_cells_dir,
                    expected_substrate_sha=config.substrate_sha256,
                )
        _preflight_fresh_hall_root(hall_root)
        config.work_dir.mkdir(parents=True, exist_ok=True)
        self._rows_path = config.work_dir / CAMPAIGN_ROWS_FILENAME
        self._gen_champions_dir = config.work_dir / GEN_CHAMPIONS_DIRNAME
        self._write_plan()
        self._states: dict[Side, _SideState] = {}
        for side, side_config, initial in (
            ("impostor", config.impostor, impostor_initial),
            ("crew", config.crew, crew_initial),
        ):
            hall = HallOfFame.create(
                hall_root,
                cast(Side, side),
                substrate_sha256=config.substrate_sha256,
                artifact_metadata=self._artifact_metadata(side_config),
            )
            if side_config.founder_cells_dir is not None:
                hall.ingest_map_elites_founders(side_config.founder_cells_dir)
            self._states[cast(Side, side)] = _SideState(
                side=cast(Side, side),
                config=side_config,
                hall=hall,
                champion=initial,
            )
        self._ledger = OpponentStalenessLedger(
            config.staleness_cap,
            tuple(self._states["impostor"].hall.member_shas)
            + tuple(self._states["crew"].hall.member_shas),
        )
        self._retired: dict[Side, set[str]] = {"impostor": set(), "crew": set()}
        self._rows: list[CoevoCampaignRow] = []
        self._games_total = 0
        self._rollout_counter = 0

    # -- plumbing ------------------------------------------------------------ #

    def _artifact_metadata(
        self, side_config: CoevoSideConfig[Any]
    ) -> LoadableArtifactMetadata:
        """This campaign's freeze metadata for one side (already preflighted)."""

        return _side_artifact_metadata(self._config, side_config)

    def _persist_generation_champion(
        self,
        *,
        moving: _SideState,
        swap_index: int,
        generation_in_swap: int,
        global_generation: int,
        champion_sha: str,
        trained_against: str,
        champion_updated: bool,
    ) -> Path:
        """Freeze THIS generation's champion beside the rows (Task 18.31 fix 2).

        The 18.24 campaign persisted only swap champions and exploiter finds, so
        its intermediate generations had to be re-bred and hand-stamped later —
        66 real games and two recovery passes (report §11 defect 2 / F1). Every
        generation's champion now lands as a four-file loadable artifact under
        ``<work_dir>/gen-champions/gen-<N>/<sha>/`` the moment it exists.

        Strictly ADDITIVE and DIGEST-INERT: no campaign row field changes, the
        rows file is untouched, and the write happens after the ES step has
        already produced the champion. The per-generation dir name is the global
        generation, and exactly one side moves per generation, so two artifacts
        can never contend for one path.
        """

        metadata = self._artifact_metadata(moving.config)
        relative = f"{GEN_CHAMPIONS_DIRNAME}/gen-{global_generation}/{champion_sha}"
        provenance = metadata.provenance(
            side=moving.side,
            generation=global_generation,
            origin=GENERATION_CHAMPION_ORIGIN,
            trained_against=trained_against,
            path=relative,
        )
        provenance["swap_index"] = swap_index
        provenance["generation_in_swap"] = generation_in_swap + 1
        provenance["champion_updated"] = champion_updated
        artifact_dir = self._config.work_dir / relative
        written = write_loadable_artifact(
            artifact_dir,
            moving.champion,
            policy_id=metadata.policy_id_for(
                origin=GENERATION_CHAMPION_ORIGIN, generation=global_generation
            ),
            method=metadata.method,
            encoder_version=metadata.encoder_version,
            anchor_policy=metadata.anchor_policy,
            hidden=metadata.hidden,
            config=provenance,
        )
        if written != champion_sha:  # pragma: no cover - same bytes, same digest
            raise RuntimeError(
                f"persisted generation champion digest {written} != the row's "
                f"champion sha {champion_sha}"
            )
        return artifact_dir

    def _write_plan(self) -> None:
        """Log the up-front budget (the 'compute and log' half of the guard)."""

        plan = {
            "allow_over_ceiling": self._config.allow_over_ceiling,
            "game_ceiling": self._config.game_ceiling,
            "generations_per_swap": self._config.generations_per_swap,
            "num_swaps": self._config.num_swaps,
            "projected_game_bound": self._bound,
            "schema_version": COEVO_CAMPAIGN_ROW_SCHEMA_VERSION,
            "substrate_sha256": self._config.substrate_sha256,
            "substrate_sha_kind": self._config.substrate_sha_kind,
        }
        (self._config.work_dir / CAMPAIGN_PLAN_FILENAME).write_text(
            json.dumps(plan, indent=2, sort_keys=True) + "\n"
        )

    def _load_composed_factory(self) -> tuple[MeetingRunnerFactory, tuple[str, ...]]:
        """Adopt 18.29 through its gated DEFAULT loader path (swap boundaries only)."""

        composed = self._config.composed
        if composed is None:  # pragma: no cover - callers gate on the config
            raise RuntimeError(
                "_load_composed_factory called without a composed configuration"
            )
        factory = load_composed_runner_factory(
            conviction_artifact_dir=composed.conviction_artifact_dir,
            surrogate_artifact_dir=composed.surrogate_artifact_dir,
            conviction_use_counter=self._conviction_counter,
            surrogate_use_counter=self._surrogate_counter,
            corpus_dir=composed.corpus_dir,
            composed_artifact_dir=composed.composed_artifact_dir,
        )
        verdict = load_composed_verdict(composed.composed_artifact_dir)
        return factory, tuple(verdict.adoption_constraints)

    def _swap_runner(
        self,
    ) -> tuple[MeetingRunnerFactory | None, tuple[str, ...], MeetingRunnerKind]:
        """Resolve the swap's TRAINING meeting runner at the swap boundary."""

        if self._config.composed is not None:
            factory, constraints = self._load_composed_factory()
            return factory, constraints, "composed"
        if self._config.meeting_runner_factory is not None:
            return self._config.meeting_runner_factory, (), "custom"
        return None, (), "fake-provider"

    def _check_meters_at_boundary(self, swap_index: int) -> None:
        """Refuse to START a swap on a spent meter (the loud boundary stop)."""

        for name, uses, cap in (
            (
                "conviction",
                None
                if self._conviction_counter is None
                else self._conviction_counter.uses,
                None
                if self._conviction_counter is None
                else self._conviction_counter.cap.max_uses,
            ),
            (
                "surrogate",
                None
                if self._surrogate_counter is None
                else self._surrogate_counter.uses,
                None
                if self._surrogate_counter is None
                else self._surrogate_counter.cap.max_uses,
            ),
        ):
            if uses is not None and cap is not None and uses >= cap:
                raise RuntimeError(
                    f"the {name} staleness cap ({uses}/{cap} uses) is already "
                    f"spent at the swap-{swap_index} boundary; the campaign "
                    "stops loudly here — re-ground the instrument before "
                    "resuming (the swap boundary is the natural re-grounding "
                    "point)"
                )

    def _play(
        self,
        *,
        moving_side: Side,
        mover: object,
        opponent: object,
        seed: int,
        conviction: ConvictionFitnessTerm | None,
        meeting_runner_factory: MeetingRunnerFactory | None,
        impostor_anchor_weight: float,
        crew_anchor_weight: float,
        impostor_trace: DecisionTrace,
        crew_trace: CrewDecisionTrace,
    ) -> CoevoRolloutResult:
        """One metered co-evo game (fold-after-scoring accumulators threaded).

        With a conviction term on a non-composed campaign, the game's meeting
        runner is wrapped in the committed 18.30
        :class:`ConvictionServingMeetingRunner` (one metered prediction per
        meeting, buffered), the predictions are recorded into BOTH sides'
        returned episode traces, and both fitnesses are recomposed through the
        pure fitness functions — the term's addend actually reaches the
        training signal (Codex review on PR #311). The caller accumulators
        were folded inside ``rollout_coevo`` before the post-hoc recording, so
        their conviction sums deliberately stay episode-trace-only; the
        row-level consumption column reads the shared counter directly.
        """

        impostor_policy, crew_policy = _ordered_pair(moving_side, mover, opponent)
        output_dir = (
            self._config.work_dir / "rollouts" / f"r{self._rollout_counter:06d}"
        )
        self._rollout_counter += 1
        self._games_total += 1

        predictions: list[ConvictionPrediction] = []
        resolved_factory = meeting_runner_factory
        if conviction is not None and self._serve_conviction:
            term = conviction
            base_factory = meeting_runner_factory

            def serving_factory() -> MeetingRunner:
                if base_factory is not None:
                    inner: MeetingRunner = base_factory()
                else:
                    # Exactly the runner rollout_coevo builds on its None path.
                    inner = build_default_meeting_runner(
                        llm_client=build_default_client(
                            env={ENV_PROVIDER: PROVIDER_FAKE}
                        )
                    )
                return ConvictionServingMeetingRunner(
                    inner=inner,
                    predict=term.predict_meeting,
                    record=predictions.append,
                )

            resolved_factory = serving_factory

        result = rollout_coevo(
            impostor_policy,
            crew_policy,
            seed,
            output_dir=output_dir,
            num_players=self._config.num_players,
            num_impostors=self._config.num_impostors,
            tasks_per_crewmate=self._config.tasks_per_crewmate,
            meeting_runner_factory=resolved_factory,
            max_ticks=self._config.max_ticks,
            impostor_anchor_weight=impostor_anchor_weight,
            crew_anchor_weight=crew_anchor_weight,
            conviction=conviction,
            impostor_trace=impostor_trace,
            crew_trace=crew_trace,
        )
        if conviction is None or not predictions:
            return result
        # Record the served predictions into BOTH sides' episode traces (the
        # 18.16 "same term object serves both sides" doctrine) and recompose
        # both fitnesses through the pure (rollout, trace) functions — the
        # per-meeting supply sums are order-free, so post-hoc recording is
        # exactly the serving-time aggregate.
        for prediction in predictions:
            result.impostor_trace.record_conviction_prediction(prediction)
            result.crew_trace.record_conviction_prediction(prediction)
        return CoevoRolloutResult(
            rollout=result.rollout,
            impostor_fitness=inner_episode_fitness(
                result.rollout,
                result.impostor_trace,
                anchor_weight=impostor_anchor_weight,
                conviction=conviction,
            ),
            crew_fitness=crew_inner_episode_fitness(
                result.rollout,
                result.crew_trace,
                anchor_weight=crew_anchor_weight,
                conviction=conviction,
            ),
            impostor_trace=result.impostor_trace,
            crew_trace=result.crew_trace,
        )

    def _fresh_traces(self) -> tuple[DecisionTrace, CrewDecisionTrace]:
        """Purpose-scoped accumulators, anchor_policy inherited from CONFIG.

        The #306 P2 discipline: the impostor accumulator carries the side
        config's fixed ``anchor_policy`` (never a moving opponent, never an
        accumulator's), so every episode-local trace inherits it.
        """

        return (
            DecisionTrace(anchor_policy=self._config.impostor.anchor_policy),
            CrewDecisionTrace(),
        )

    def _build_opponent(self, frozen: _SideState, weights_sha256: str) -> object:
        """Reload + length-check + build one frozen opponent policy."""

        genome = frozen.hall.load_member_genome(weights_sha256)
        if len(genome) != frozen.config.genome_length:
            raise ValueError(
                f"hall member {weights_sha256} reloads {len(genome)} genes but "
                f"the {frozen.side} campaign family is pinned at "
                f"{frozen.config.genome_length} — a mixed-family hall fails "
                "loud at genome-length reload (single-family per campaign)"
            )
        policy: object = frozen.config.build_policy(genome)
        return policy

    # -- the campaign loop ----------------------------------------------------#

    def run(self) -> CoevoCampaignResult:
        config = self._config
        sides: tuple[Side, ...] = (
            ("impostor", "crew")
            if config.first_side == "impostor"
            else ("crew", "impostor")
        )
        with self._rows_path.open("x") as rows_file:
            for swap_index in range(config.num_swaps):
                moving = self._states[sides[swap_index % 2]]
                frozen = self._states[sides[(swap_index + 1) % 2]]
                self._run_swap(swap_index, moving, frozen, rows_file)
        return CoevoCampaignResult(
            rows=tuple(self._rows),
            impostor_hall=self._states["impostor"].hall,
            crew_hall=self._states["crew"].hall,
            impostor_champion=self._states["impostor"].champion,
            crew_champion=self._states["crew"].champion,
            total_games=self._games_total,
            projected_game_bound=self._bound,
            rows_path=self._rows_path,
            gen_champions_dir=self._gen_champions_dir,
        )

    def _run_swap(
        self,
        swap_index: int,
        moving: _SideState,
        frozen: _SideState,
        rows_file: Any,
    ) -> None:
        # The barred simultaneous form is structurally unreachable: exactly one
        # moving side per swap, asserted, and the frozen side's standing
        # champion is snapshot-guarded across the whole swap.
        if moving.side == frozen.side:
            raise RuntimeError(
                "structural invariant violated: the moving and frozen sides "
                "must differ (one side moves at a time, always)"
            )
        frozen_champion_snapshot = frozen.champion
        self._check_meters_at_boundary(swap_index)
        runner_factory, adoption_constraints, runner_kind = self._swap_runner()
        scenario_terms: tuple[CoevoScenarioTerm, ...] = ()
        if self._config.scenario_provider is not None:
            scenario_terms = tuple(
                self._config.scenario_provider(swap_index, moving.side)
            )
        swap_use_counts: Counter[str] = Counter()

        for generation_in_swap in range(self._config.generations_per_swap):
            row = self._run_generation(
                swap_index=swap_index,
                generation_in_swap=generation_in_swap,
                moving=moving,
                frozen=frozen,
                runner_factory=runner_factory,
                runner_kind=runner_kind,
                adoption_constraints=adoption_constraints,
                scenario_terms=scenario_terms,
                swap_use_counts=swap_use_counts,
            )
            if generation_in_swap == self._config.generations_per_swap - 1:
                # The swap boundary: freeze the champion (fresh sha) into the
                # moving side's hall and stamp the provenance onto the swap's
                # final generation row.
                frozen_flag, frozen_sha, trained_against = self._freeze_swap_champion(
                    swap_index, moving, swap_use_counts
                )
                row = row.model_copy(
                    update={
                        "champion_frozen": frozen_flag,
                        "champion_frozen_sha": frozen_sha,
                        "champion_trained_against": trained_against,
                    }
                )
            self._emit(row, rows_file)

        if frozen.champion != frozen_champion_snapshot:
            raise RuntimeError(
                "structural invariant violated: the frozen side's standing "
                "champion moved during a swap (both sides updated in one step "
                "— the barred simultaneous form)"
            )

    def _freeze_swap_champion(
        self,
        swap_index: int,
        moving: _SideState,
        swap_use_counts: Counter[str],
    ) -> tuple[bool, str, str | None]:
        """Freeze the swap champion (fresh sha) or record the unchanged one.

        ``trained_against`` is the opponent with the greatest CUMULATIVE SLATE
        WEIGHT this swap — draw multiplicities summed across the swap's
        generations, matching the ES fitness weighting exactly, so the named
        opponent is the one that dominated the champion's training signal
        (ties break to the lexically smallest sha — deterministic) — or the
        reserved scripted-FSM sentinel when the whole swap ran against the
        empty-pool scripted FSM. A champion whose genome is already a member
        (no strict improvement over a previously frozen seed) is NOT re-frozen
        — the sha is the member identity — and the row says so
        (``champion_frozen=False``), never a silent duplicate.
        """

        champion_sha = _genome_sha(moving.champion)
        if champion_sha in moving.hall.member_shas:
            moving.last_frozen_sha = champion_sha
            return False, champion_sha, None
        if swap_use_counts:
            trained_against = min(
                swap_use_counts, key=lambda sha: (-swap_use_counts[sha], sha)
            )
        else:
            trained_against = TRAINED_AGAINST_FSM
        global_generation = (swap_index + 1) * self._config.generations_per_swap
        moving.hall.add_member(
            moving.champion,
            generation=global_generation,
            origin=SWAP_CHAMPION_ORIGIN,
            trained_against=trained_against,
        )
        self._ledger.register(weights_sha256=champion_sha)
        moving.last_frozen_sha = champion_sha
        return True, champion_sha, trained_against

    def _run_generation(
        self,
        *,
        swap_index: int,
        generation_in_swap: int,
        moving: _SideState,
        frozen: _SideState,
        runner_factory: MeetingRunnerFactory | None,
        runner_kind: MeetingRunnerKind,
        adoption_constraints: tuple[str, ...],
        scenario_terms: tuple[CoevoScenarioTerm, ...],
        swap_use_counts: Counter[str],
    ) -> CoevoCampaignRow:
        config = self._config
        global_generation = swap_index * config.generations_per_swap + (
            generation_in_swap + 1
        )
        games_before = self._games_total

        # 1. Retire capped opponents (retire-and-replace: the replacements are
        #    the freshly frozen champions/exploits already registered with
        #    fresh shas — never an in-place counter reset).
        retired_set = self._retired[frozen.side]
        newly_retired = tuple(
            sorted(
                sha
                for sha in frozen.hall.member_shas
                if sha not in retired_set
                and self._ledger.uses(weights_sha256=sha)
                >= config.staleness_cap.max_generations
            )
        )
        retired_set.update(newly_retired)
        active = [
            member
            for member in frozen.hall.members
            if member.weights_sha256 not in retired_set
        ]
        fsm_mode = not frozen.hall.members
        if not fsm_mode and not active:
            raise RuntimeError(
                f"every {frozen.side} hall member is retired at its staleness "
                f"cap ({config.staleness_cap.max_generations} generations) and "
                "no fresh replacement exists — the opponent pool is exhausted; "
                "the campaign stops loudly rather than silently re-serve a "
                "capped opponent or fall back to the scripted FSM"
            )

        # 2. The payoff row: the moving champion's exact deterministic fitness
        #    vs EVERY active member this generation — exact pool cover, the
        #    sampler contract. Measured for every non-FSM generation
        #    (payoff_seeds is validated non-empty), so the sampler's empty-map
        #    cold-start branch is never taken by this driver (Codex review on
        #    PR #311: the contract's cold-start exception is gen-1-shaped,
        #    never a whole-campaign PFSP bypass). ``None`` = FSM mode only.
        payoffs: dict[str, float] | None = None
        if not fsm_mode:
            payoff_imp_trace, payoff_crew_trace = self._fresh_traces()
            champion_policy = moving.config.build_policy(moving.champion)
            payoffs = {}
            for member in active:  # hall members are sha-sorted already
                opponent_policy = self._build_opponent(frozen, member.weights_sha256)
                payoffs[member.weights_sha256] = _mean(
                    [
                        _side_fitness(
                            self._play(
                                moving_side=moving.side,
                                mover=champion_policy,
                                opponent=opponent_policy,
                                seed=seed,
                                conviction=config.conviction,
                                meeting_runner_factory=runner_factory,
                                impostor_anchor_weight=config.impostor.anchor_weight,
                                crew_anchor_weight=config.crew.anchor_weight,
                                impostor_trace=payoff_imp_trace,
                                crew_trace=payoff_crew_trace,
                            ),
                            moving.side,
                        )
                        for seed in config.payoff_seeds
                    ]
                )

        # 3. Sample the slate (WITH replacement), dedupe for metering: one use
        #    per DISTINCT sampled member per driver generation.
        if fsm_mode:
            slate_shas: tuple[str, ...] = (TRAINED_AGAINST_FSM,)
            distinct_entries: list[tuple[str, int, object]] = [
                (TRAINED_AGAINST_FSM, 1, None)
            ]
            slate_total = 1
        else:
            if payoffs is None:  # pragma: no cover - structurally unreachable
                raise RuntimeError(
                    "the payoff row is measured for every non-FSM generation; "
                    "sampling without one is unreachable by construction"
                )
            slate = sample_opponents(
                active,
                payoffs,
                slate_size=config.slate_size,
                seed=derive_stream_seed(
                    config.master_seed, _STREAM_SLATE, swap_index, generation_in_swap
                ),
                exploration_floor=frozen.config.exploration_floor,
            )
            slate_shas = tuple(member.weights_sha256 for member in slate)
            multiplicities = Counter(slate_shas)
            distinct_entries = [
                (sha, multiplicities[sha], self._build_opponent(frozen, sha))
                for sha in sorted(multiplicities)
            ]
            slate_total = len(slate_shas)
            for sha, multiplicity, _ in distinct_entries:
                # The LEDGER meters one use per DISTINCT member per driver
                # generation (the hand-off's staleness unit); the PROVENANCE
                # counter weights by draw multiplicity, because a slate like
                # (A, A, B) trains 2/3 against A and trained_against should
                # name the opponent that dominated the training signal
                # (Codex review on PR #311).
                self._ledger.record_generation_use(weights_sha256=sha)
                swap_use_counts[sha] += multiplicity
        opponent_uses = {
            sha: self._ledger.uses(weights_sha256=sha)
            for sha, _, _ in distinct_entries
            if sha != TRAINED_AGAINST_FSM
        }
        # The generation's dominant opponent, by the SAME draw-multiplicity rule
        # the swap freeze uses (ties break to the lexically smallest sha), so a
        # persisted generation champion names the opponent that dominated its
        # training signal — the FSM sentinel in cold-start/empty-pool mode.
        generation_multiplicities = {
            sha: multiplicity
            for sha, multiplicity, _ in distinct_entries
            if sha != TRAINED_AGAINST_FSM
        }
        generation_trained_against = (
            min(
                generation_multiplicities,
                key=lambda sha: (-generation_multiplicities[sha], sha),
            )
            if generation_multiplicities
            else TRAINED_AGAINST_FSM
        )

        # 4. The ES step vs the slate (distinct opponents weighted by draw
        #    multiplicity — arithmetically the slate mean with replacement).
        gen_imp_trace, gen_crew_trace = self._fresh_traces()

        def es_fitness(genome: tuple[float, ...]) -> float:
            mover_policy = moving.config.build_policy(genome)
            weighted_parts = [
                multiplicity
                * _mean(
                    [
                        _side_fitness(
                            self._play(
                                moving_side=moving.side,
                                mover=mover_policy,
                                opponent=opponent_policy,
                                seed=seed,
                                conviction=config.conviction,
                                meeting_runner_factory=runner_factory,
                                impostor_anchor_weight=config.impostor.anchor_weight,
                                crew_anchor_weight=config.crew.anchor_weight,
                                impostor_trace=gen_imp_trace,
                                crew_trace=gen_crew_trace,
                            ),
                            moving.side,
                        )
                        for seed in config.fitness_seeds
                    ]
                )
                for _, multiplicity, opponent_policy in distinct_entries
            ]
            fitness = math.fsum(weighted_parts) / slate_total
            for term in scenario_terms:
                fitness += term.fitness(genome)
            return fitness

        previous_champion = moving.champion
        es_result: ESResult = evolve(
            es_fitness,
            genome_length=moving.config.genome_length,
            config=ESConfig(
                generations=1,
                population=moving.config.population,
                sigma=moving.config.sigma,
                seed=derive_stream_seed(
                    config.master_seed, _STREAM_ES, swap_index, generation_in_swap
                ),
                fitness_seeds=config.fitness_seeds,
                init_scale=moving.config.init_scale,
            ),
            initial_genome=previous_champion,
        )
        moving.champion = es_result.champion
        champion_sha = _genome_sha(moving.champion)
        # Fix 2: persist THIS generation's champion beside the rows, before the
        # benchmark/exploiter games spend anything further — an interrupted
        # campaign keeps every genome it has already bred.
        self._persist_generation_champion(
            moving=moving,
            swap_index=swap_index,
            generation_in_swap=generation_in_swap,
            global_generation=global_generation,
            champion_sha=champion_sha,
            trained_against=generation_trained_against,
            champion_updated=moving.champion != previous_champion,
        )
        moving_anchor_ce_mean = (
            gen_imp_trace.mean_anchor_ce()
            if moving.side == "impostor"
            else gen_crew_trace.mean_anchor_ce()
        )

        # 5. The absolute anchor benchmark, both directions, ALWAYS on the
        #    default fake path (champion numbers are never
        #    composed-runner-scored) — one game set serves both directions AND
        #    the exploiter's scripted-FSM baseline (same seeds, same substrate).
        bench_imp_trace, bench_crew_trace = self._fresh_traces()
        champion_policy_after = moving.config.build_policy(moving.champion)
        bench_results = [
            self._play(
                moving_side=moving.side,
                mover=champion_policy_after,
                opponent=None,
                seed=seed,
                conviction=None,
                meeting_runner_factory=None,
                impostor_anchor_weight=config.impostor.anchor_weight,
                crew_anchor_weight=config.crew.anchor_weight,
                impostor_trace=bench_imp_trace,
                crew_trace=bench_crew_trace,
            )
            for seed in config.benchmark_seeds
        ]
        anchor_champion_side = _mean(
            [_side_fitness(result, moving.side) for result in bench_results]
        )
        anchor_fsm_side = _mean(
            [_side_fitness(result, frozen.side) for result in bench_results]
        )

        # 6. The short-horizon exploiter probe: breed the FROZEN side's family
        #    purely to beat the current champion (anchor weight 0 on the
        #    exploiter side; fake path; the scripted FSM's own reading of the
        #    same matchup is the bar). Found exploits join the frozen side's
        #    hall — fresh opponent pressure, never a standing-champion update.
        exploiter_imp_weight = (
            config.impostor.anchor_weight if moving.side == "impostor" else 0.0
        )
        exploiter_crew_weight = (
            config.crew.anchor_weight if moving.side == "crew" else 0.0
        )

        def exploiter_fitness(genome: tuple[float, ...]) -> float:
            exploiter_policy = frozen.config.build_policy(genome)
            exploiter_imp_trace, exploiter_crew_trace = self._fresh_traces()
            return _mean(
                [
                    _side_fitness(
                        self._play(
                            moving_side=moving.side,
                            mover=champion_policy_after,
                            opponent=exploiter_policy,
                            seed=seed,
                            conviction=None,
                            meeting_runner_factory=None,
                            impostor_anchor_weight=exploiter_imp_weight,
                            crew_anchor_weight=exploiter_crew_weight,
                            impostor_trace=exploiter_imp_trace,
                            crew_trace=exploiter_crew_trace,
                        ),
                        frozen.side,
                    )
                    for seed in config.benchmark_seeds
                ]
            )

        exploiter_result = evolve(
            exploiter_fitness,
            genome_length=frozen.config.genome_length,
            config=ESConfig(
                generations=config.exploiter_generations,
                population=config.exploiter_population,
                sigma=frozen.config.sigma,
                seed=derive_stream_seed(
                    config.master_seed,
                    _STREAM_EXPLOITER,
                    swap_index,
                    generation_in_swap,
                ),
                fitness_seeds=config.benchmark_seeds,
                init_scale=frozen.config.init_scale,
            ),
            initial_genome=frozen.champion,
        )
        exploiter_baseline = anchor_fsm_side
        exploiter_outcome: Literal["frozen", "duplicate", "not-found"]
        exploiter_sha: str | None = None
        if exploiter_result.champion_fitness > exploiter_baseline:
            exploiter_sha = _genome_sha(exploiter_result.champion)
            if exploiter_sha in frozen.hall.member_shas:
                exploiter_outcome = "duplicate"
            else:
                frozen.hall.add_member(
                    exploiter_result.champion,
                    generation=global_generation,
                    origin=EXPLOITER_ORIGIN,
                    trained_against=champion_sha,
                )
                self._ledger.register(weights_sha256=exploiter_sha)
                exploiter_outcome = "frozen"
        else:
            exploiter_outcome = "not-found"

        return CoevoCampaignRow(
            swap_index=swap_index,
            generation_index=global_generation,
            generation_in_swap=generation_in_swap + 1,
            moving_side=moving.side,
            frozen_side=frozen.side,
            moving_encoder_version=moving.config.encoder_version,
            frozen_encoder_version=frozen.config.encoder_version,
            substrate_sha256=config.substrate_sha256,
            substrate_sha_kind=config.substrate_sha_kind,
            meeting_runner=runner_kind,
            scenario_labels=tuple(term.label for term in scenario_terms),
            opponent_pool_size=len(active),
            opponent_slate_shas=slate_shas,
            opponent_payoffs=payoffs,
            opponent_uses=opponent_uses,
            retired_opponent_shas=newly_retired,
            champion_fitness=es_result.champion_fitness,
            generation_best_fitness=es_result.generation_best[0],
            champion_updated=moving.champion != previous_champion,
            champion_weights_sha256=champion_sha,
            moving_anchor_ce_mean=moving_anchor_ce_mean,
            anchor_benchmark_champion_side=anchor_champion_side,
            anchor_benchmark_fsm_side=anchor_fsm_side,
            exploiter_fitness=exploiter_result.champion_fitness,
            exploiter_baseline_fitness=exploiter_baseline,
            exploiter_outcome=exploiter_outcome,
            exploiter_sha=exploiter_sha,
            champion_frozen=False,
            champion_frozen_sha=None,
            champion_trained_against=None,
            frozen_champion_sha=frozen.last_frozen_sha,
            conviction_uses=(
                None
                if self._conviction_counter is None
                else self._conviction_counter.uses
            ),
            surrogate_uses=(
                None
                if self._surrogate_counter is None
                else self._surrogate_counter.uses
            ),
            adoption_constraints=adoption_constraints,
            games_played_generation=self._games_total - games_before,
            games_played_cumulative=self._games_total,
        )

    def _emit(self, row: CoevoCampaignRow, rows_file: Any) -> None:
        self._rows.append(row)
        rows_file.write(row.to_json_line() + "\n")
        rows_file.flush()


def run_alternating_freeze(config: CoevoCampaignConfig) -> CoevoCampaignResult:
    """Run one alternating-freeze co-evolution campaign (Task 18.21 public type).

    Validates the configuration and the up-front game bound (refusing an
    over-ceiling configuration without the explicit override), creates the two
    per-side halls at the pinned substrate (founders ingest first through the
    substrate fence), constructs the ONE run-scoped
    :class:`~training.coevo.hall_of_fame.OpponentStalenessLedger`, then runs
    ``num_swaps`` swaps of the alternating-freeze loop — one moving side per
    swap, always — emitting one :class:`CoevoCampaignRow` per driver
    generation (also appended live to ``<work_dir>/campaign-rows.jsonl``).
    Deterministic end-to-end on the fake/surrogate path: identical configs
    (up to ``work_dir``/``hall_root`` locations, which never enter rows)
    produce identical :meth:`CoevoCampaignResult.digest` values.
    """

    return _CampaignEngine(config).run()


__all__ = [
    "CAMPAIGN_PLAN_FILENAME",
    "CAMPAIGN_ROWS_FILENAME",
    "COEVO_CAMPAIGN_ROW_SCHEMA_VERSION",
    "COEVO_FREEZE_METHOD",
    "COMPOSED_ARTIFACT_DIR",
    "DEFAULT_GAME_CEILING",
    "DEFAULT_OPPONENT_STALENESS_CAP",
    "DEFAULT_RUN_LABEL",
    "EXPLOITER_ORIGIN",
    "GEN_CHAMPIONS_DIRNAME",
    "GENERATION_CHAMPION_ORIGIN",
    "SWAP_CHAMPION_ORIGIN",
    "CoevoCampaignConfig",
    "CoevoCampaignResult",
    "CoevoCampaignRow",
    "CoevoComposedRunnerConfig",
    "CoevoScenarioProvider",
    "CoevoScenarioTerm",
    "CoevoSideConfig",
    "MeetingRunnerKind",
    "SubstrateShaKind",
    "projected_game_bound",
    "run_alternating_freeze",
]
