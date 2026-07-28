"""Tests for the alternating-freeze co-evolution driver (Task 18.21).

A miniature two-swap campaign on tiny budgets (4p1i, one ES generation per
swap, single-seed fitness/benchmark/payoff sets, a 1×1 exploiter probe) pins
the definition-of-done contract of :mod:`training.coevo.driver`:

* the campaign runs deterministically twice with identical
  :meth:`CoevoCampaignResult.digest` values (row-for-row equality, plus the
  on-disk ``campaign-rows.jsonl`` round-trips to the same rows);
* the hall of fame grows with full provenance (halls reloaded from disk
  through ``HallOfFame.load``'s eager two-pass verification; swap champions
  carry :data:`SWAP_CHAMPION_ORIGIN` and honest ``trained_against`` — the
  scripted-FSM sentinel for the cold-start swap, the most-faced opponent sha
  afterwards);
* the absolute-benchmark and exploiter rows are emitted per generation, and
  the row schema carries everything 18.24's report needs (per-gen fitness,
  anchor benchmarks both directions, opponent slate shas, exploiter outcomes,
  conviction/surrogate consumption);
* one side moves at a time, always — structurally asserted over the rows
  (moving ≠ frozen everywhere, one moving side per swap, alternation across
  swaps, and the frozen side's standing champion sha constant within a swap);
* the up-front budget guard refuses an over-ceiling configuration without the
  explicit override (and the baseline fixture itself runs UNDER the override,
  proving that branch);
* the two additive seams are inert when unset: a scenario provider returning
  no terms is digest-identical to no provider at all, an explicitly-fake
  meeting-runner factory changes no game-derived row field (only the honest
  ``meeting_runner`` label), and an active scenario term shifts the swap's ES
  fitness by exactly its constant while leaving selection and the absolute
  benchmark untouched;
* the staleness ledger retires a capped opponent (retire-and-replace, never a
  reset) and an exhausted pool stops the campaign loudly mid-file (the rows
  written so far survive, flushed per generation);
* MAP-Elites founders ingest through the substrate fence BEFORE any pool
  build or sampling, and the exploiter probe's found exploits join the frozen
  side's hall with honest provenance;
* wrong-family/misconfigured campaigns fail loud at validation time, BEFORE
  any hall exists on disk;
* (Task 18.31) every GENERATION's champion is persisted beside the rows as a
  four-file loadable artifact and every hall freeze writes one too — both
  provably digest-inert (the double-run row digest is asserted again against
  the same fixture, and no row field was added), both byte-deterministic across
  two runs, and both loading END TO END through
  ``scripts/run_tournament.py``'s ``_load_candidate_policy``; the work-dir
  no-clobber discipline covers the new artifacts, and a side that would freeze
  a MIS-STAMPED artifact (a masked-MLP family with no declared ``hidden``, an
  alternative anchor with no stamp label, a blank/unsafe run label) is refused
  before any hall exists.

Every fixture-pinned count below (games, hall sizes, exploiter outcomes) was
obtained by running the code under the fixed seeds and then hard-pinned here
(the ``test_hall_of_fame`` idiom); float values and digests are asserted only
RELATIVE to a same-process twin run, never as absolute constants (the
platform-sensitivity lesson from the ``test_es`` hash pin).
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import cast

import pytest

from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from orchestrator.game import MeetingRunner, build_default_meeting_runner
from training.anchor_study import compute_substrate_sha
from training.bakeoff.es import random_genome
from training.bakeoff.harness import (
    BakeoffPolicy,
    ConvictionFitnessTerm,
    load_conviction_fitness_term,
)
from training.bakeoff.map_elites import (
    BEHAVIOR_DESCRIPTOR_CONFIGURATION,
    ArchiveCell,
    bakeoff_substrate_sha,
    map_elites_budget,
    write_archive_cell_artifacts,
)
from training.bakeoff.utility_es import build_utility_scorer_policy
from training.coevo.driver import (
    COEVO_CAMPAIGN_ROW_SCHEMA_VERSION,
    COEVO_FREEZE_METHOD,
    EXPLOITER_ORIGIN,
    GENERATION_CHAMPION_ORIGIN,
    SWAP_CHAMPION_ORIGIN,
    CoevoCampaignConfig,
    CoevoCampaignResult,
    CoevoCampaignRow,
    CoevoComposedRunnerConfig,
    CoevoScenarioTerm,
    CoevoSideConfig,
    projected_game_bound,
    run_alternating_freeze,
)
from training.coevo.hall_of_fame import (
    MAP_ELITES_FOUNDER_ORIGIN,
    TRAINED_AGAINST_FSM,
    HallOfFame,
    OpponentStalenessCap,
    Side,
)
from training.conviction.model import ConvictionStalenessCap, ConvictionUseCounter
from training.crew.options import OwnedTaskOptionBasis
from training.crew.scorer import CrewOptionScorer, CrewTrackPolicy, build_crew_scorer

# ``scripts/`` is a bare-module namespace: the 18.31 loadable-freeze pin needs
# the CONSUMING entry point ``run_tournament._load_candidate_policy``, so put
# ``scripts/`` on sys.path the way tests/scripts/conftest.py does.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import run_tournament  # noqa: E402

# The two committed cheap linear families (the shared artifact/weights layout):
# the 19-gene utility scorer (impostor encoder v1) and the 27-gene owned-task
# crew scorer (crew encoder v2). The campaign families are pinned on them.
_IMPOSTOR_GENOME_LENGTH = 19
_CREW_GENOME_LENGTH = 27
_IMPOSTOR_ENCODER = "impostor-option-features-v1"
_CREW_ENCODER = "crew-option-features-v2"

# A valid 64-lowercase-hex substrate for runs that never touch founder cells
# (the founder run uses the real ``bakeoff_substrate_sha()``).
_SUBSTRATE = "ab" * 32

# The miniature budget: 4p1i games at a small tick cap complete (or truncate)
# in well under a second each; the whole baseline campaign is 13 games.
_MASTER_SEED = 18021
_SEED = 1000
_MAX_TICKS = 60

# Fixture-pinned baseline facts (run once under the fixed seeds, hard-pinned):
# 2 swaps × 1 generation; swap 0 = impostor vs the empty-pool scripted FSM
# (3 ES games + 1 benchmark + 2 exploiter), swap 1 = crew vs the one-member
# impostor hall (1 payoff + 3 ES + 1 benchmark + 2 exploiter).
_BASELINE_GAMES = 13
_BASELINE_BOUND = 26


def _crew_builder(genome: tuple[float, ...]) -> CrewOptionScorer:
    return build_crew_scorer(genome, basis=OwnedTaskOptionBasis())


def _impostor_side(**overrides: object) -> CoevoSideConfig[BakeoffPolicy]:
    base = CoevoSideConfig[BakeoffPolicy](
        side="impostor",
        genome_length=_IMPOSTOR_GENOME_LENGTH,
        build_policy=build_utility_scorer_policy,
        encoder_version=_IMPOSTOR_ENCODER,
        population=2,
        sigma=0.15,
    )
    return replace(base, **overrides)  # type: ignore[arg-type]


def _crew_side(**overrides: object) -> CoevoSideConfig[CrewTrackPolicy]:
    base = CoevoSideConfig[CrewTrackPolicy](
        side="crew",
        genome_length=_CREW_GENOME_LENGTH,
        build_policy=_crew_builder,
        encoder_version=_CREW_ENCODER,
        population=2,
        sigma=0.15,
    )
    return replace(base, **overrides)  # type: ignore[arg-type]


def _make_config(base: Path, **overrides: object) -> CoevoCampaignConfig:
    """The miniature two-swap campaign configuration (fresh dirs under ``base``).

    ``game_ceiling`` is deliberately BELOW the projected bound with
    ``allow_over_ceiling=True``, so every fixture run exercises the explicit
    override branch of the budget guard (the refusal branch is tested with the
    override off).
    """

    config = CoevoCampaignConfig(
        work_dir=base / "work",
        hall_root=base / "halls",
        substrate_sha256=_SUBSTRATE,
        substrate_sha_kind="bakeoff_substrate_sha",
        impostor=_impostor_side(),
        crew=_crew_side(),
        master_seed=_MASTER_SEED,
        num_swaps=2,
        generations_per_swap=1,
        fitness_seeds=(_SEED,),
        benchmark_seeds=(_SEED,),
        payoff_seeds=(_SEED,),
        slate_size=2,
        exploiter_population=1,
        exploiter_generations=1,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=2,
        max_ticks=_MAX_TICKS,
        game_ceiling=_BASELINE_GAMES,
        allow_over_ceiling=True,
    )
    return replace(config, **overrides)  # type: ignore[arg-type]


def _explicitly_fake_meeting_runner() -> MeetingRunner:
    """Exactly the runner ``rollout_coevo`` builds on its default ``None`` path."""

    return build_default_meeting_runner(
        llm_client=build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})
    )


def _empty_provider(swap_index: int, side: Side) -> tuple[CoevoScenarioTerm, ...]:
    del swap_index, side
    return ()


_SCENARIO_OFFSET = 2.5


def _swap0_constant_provider(
    swap_index: int, side: Side
) -> tuple[CoevoScenarioTerm, ...]:
    del side
    if swap_index != 0:
        return ()
    return (
        CoevoScenarioTerm(label="skill-probe", fitness=lambda genome: _SCENARIO_OFFSET),
    )


@pytest.fixture(scope="module")
def baseline_runs(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[CoevoCampaignResult, CoevoCampaignResult, Path]:
    """The miniature campaign run TWICE (separate dirs) — the determinism pair."""

    base = tmp_path_factory.mktemp("coevo-driver-baseline")
    first = run_alternating_freeze(_make_config(base / "one"))
    second = run_alternating_freeze(_make_config(base / "two"))
    return first, second, base / "one"


@pytest.fixture(scope="module")
def custom_runner_run(
    tmp_path_factory: pytest.TempPathFactory,
) -> CoevoCampaignResult:
    """The same campaign with an explicitly-fake meeting-runner factory."""

    base = tmp_path_factory.mktemp("coevo-driver-custom-runner")
    return run_alternating_freeze(
        _make_config(base, meeting_runner_factory=_explicitly_fake_meeting_runner)
    )


@pytest.fixture(scope="module")
def empty_provider_run(
    tmp_path_factory: pytest.TempPathFactory,
) -> CoevoCampaignResult:
    """The same campaign with a scenario provider that returns no terms."""

    base = tmp_path_factory.mktemp("coevo-driver-empty-provider")
    return run_alternating_freeze(_make_config(base, scenario_provider=_empty_provider))


@pytest.fixture(scope="module")
def scenario_run(tmp_path_factory: pytest.TempPathFactory) -> CoevoCampaignResult:
    """The same campaign with one constant scenario term on swap 0 only."""

    base = tmp_path_factory.mktemp("coevo-driver-scenario")
    return run_alternating_freeze(
        _make_config(base, scenario_provider=_swap0_constant_provider)
    )


# --------------------------------------------------------------------------- #
# Determinism.                                                                 #
# --------------------------------------------------------------------------- #


def test_two_swap_campaign_is_deterministic_twice(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    first, second, _ = baseline_runs
    # Identical digests across two full runs (different work/hall dirs — row
    # bytes carry no paths), and row-for-row equality behind the digest.
    assert first.digest() == second.digest()
    assert first.rows == second.rows
    assert first.total_games == second.total_games == _BASELINE_GAMES
    assert first.projected_game_bound == _BASELINE_BOUND
    # One row per driver generation: 2 swaps × 1 generation.
    assert len(first.rows) == 2
    # Both champions returned; genomes stay in their pinned families.
    assert len(first.impostor_champion) == _IMPOSTOR_GENOME_LENGTH
    assert len(first.crew_champion) == _CREW_GENOME_LENGTH
    assert first.impostor_champion == second.impostor_champion
    assert first.crew_champion == second.crew_champion


def test_rows_file_round_trips_the_emitted_rows(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    first, _, _ = baseline_runs
    lines = first.rows_path.read_text().splitlines()
    assert len(lines) == len(first.rows)
    parsed = tuple(CoevoCampaignRow(**json.loads(line)) for line in lines)
    assert parsed == first.rows


# --------------------------------------------------------------------------- #
# One side moves at a time (structural).                                       #
# --------------------------------------------------------------------------- #


def test_never_updates_both_sides_in_one_step(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    first, _, _ = baseline_runs
    for row in first.rows:
        # The barred simultaneous form is unreachable: every generation names
        # exactly one moving side and one (different) frozen side.
        assert row.moving_side != row.frozen_side
    # Impostor-first alternation across swaps; one moving side per swap.
    swap_sides = {row.swap_index: row.moving_side for row in first.rows}
    assert swap_sides == {0: "impostor", 1: "crew"}
    for row in first.rows:
        assert row.moving_side == swap_sides[row.swap_index]
    # The frozen side's standing champion never moves within a swap: swap 0
    # froze the crew side before any crew champion existed (None), and swap 1's
    # frozen impostor champion is exactly the sha swap 0 froze.
    assert first.rows[0].frozen_champion_sha is None
    assert first.rows[0].champion_frozen is True
    assert first.rows[1].frozen_champion_sha == first.rows[0].champion_frozen_sha


# --------------------------------------------------------------------------- #
# Hall-of-fame growth + provenance.                                            #
# --------------------------------------------------------------------------- #


def test_hall_growth_with_full_provenance(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    first, _, base = baseline_runs
    # Reload both halls from disk through the eager two-pass verifier — the
    # grown pools are bit-exact, fully indexed trees, not in-memory state.
    impostor_hall = HallOfFame.load(base / "halls", "impostor")
    crew_hall = HallOfFame.load(base / "halls", "crew")
    assert impostor_hall.substrate_sha256 == _SUBSTRATE
    assert crew_hall.substrate_sha256 == _SUBSTRATE

    # Fixture-pinned growth: neither exploiter probe found an exploit under
    # these seeds, so each hall grew by exactly its swap champion.
    row0, row1 = first.rows
    assert row0.exploiter_outcome == "not-found"
    assert row1.exploiter_outcome == "not-found"
    assert len(impostor_hall.members) == 1
    assert len(crew_hall.members) == 1

    # Swap 0: the impostor champion, bred against the empty-pool scripted FSM
    # — provenance carries the reserved sentinel, never None/arbitrary.
    impostor_member = impostor_hall.members[0]
    assert impostor_member.origin == SWAP_CHAMPION_ORIGIN
    assert impostor_member.generation == 1
    assert impostor_member.trained_against == TRAINED_AGAINST_FSM
    assert impostor_member.weights_sha256 == row0.champion_frozen_sha
    assert row0.champion_frozen is True
    assert row0.champion_frozen_sha == row0.champion_weights_sha256
    assert row0.champion_trained_against == TRAINED_AGAINST_FSM

    # Swap 1: the crew champion, bred against the frozen impostor champion —
    # trained_against names the most-faced opponent sha of the swap.
    crew_member = crew_hall.members[0]
    assert crew_member.origin == SWAP_CHAMPION_ORIGIN
    assert crew_member.generation == 2
    assert crew_member.trained_against == row0.champion_frozen_sha
    assert row1.champion_frozen is True
    assert row1.champion_trained_against == row0.champion_frozen_sha

    # The frozen genomes reload bit-exactly and stay in their pinned families
    # (the single-family-per-campaign discipline).
    assert (
        len(impostor_hall.load_member_genome(impostor_member.weights_sha256))
        == _IMPOSTOR_GENOME_LENGTH
    )
    assert (
        len(crew_hall.load_member_genome(crew_member.weights_sha256))
        == _CREW_GENOME_LENGTH
    )


# --------------------------------------------------------------------------- #
# The row schema (everything 18.24's report needs).                            #
# --------------------------------------------------------------------------- #


def test_rows_carry_the_report_channels(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    first, _, _ = baseline_runs
    row0, row1 = first.rows

    for row in first.rows:
        assert row.schema_version == COEVO_CAMPAIGN_ROW_SCHEMA_VERSION
        # The substrate pin names WHICH committed sha definition was passed.
        assert row.substrate_sha256 == _SUBSTRATE
        assert row.substrate_sha_kind == "bakeoff_substrate_sha"
        # Per-gen fitness channel (finite — the ES core refuses NaN/inf, and
        # the truncation sentinel is a finite documented constant).
        assert math.isfinite(row.champion_fitness)
        assert math.isfinite(row.generation_best_fitness)
        # The absolute anchor benchmark, both directions, every generation.
        assert math.isfinite(row.anchor_benchmark_champion_side)
        assert math.isfinite(row.anchor_benchmark_fsm_side)
        # The exploiter row, every generation (baseline == the scripted FSM's
        # own reading from the SAME benchmark games).
        assert row.exploiter_outcome in {"frozen", "duplicate", "not-found"}
        assert row.exploiter_baseline_fitness == row.anchor_benchmark_fsm_side
        # Conviction/surrogate consumption: structurally absent on the plain
        # fake path — None, never a zero-ghost.
        assert row.conviction_uses is None
        assert row.surrogate_uses is None
        assert row.adoption_constraints == ()
        assert row.meeting_runner == "fake-provider"
        assert row.scenario_labels == ()
        # The family pins ride the rows (HoF rows deliberately carry none).
        assert {row.moving_encoder_version, row.frozen_encoder_version} == {
            _IMPOSTOR_ENCODER,
            _CREW_ENCODER,
        }
        assert row.games_played_generation > 0

    # Swap 0 (cold start): the empty-pool scripted FSM is the slate, spelled
    # with the reserved sentinel — visibly not a member sha — and there is no
    # payoff row to sample from.
    assert row0.opponent_pool_size == 0
    assert row0.opponent_slate_shas == (TRAINED_AGAINST_FSM,)
    assert row0.opponent_payoffs is None
    assert row0.opponent_uses == {}

    # Swap 1: the slate is drawn (with replacement) from the one-member
    # impostor pool; the payoff row exactly covers the pool; the ledger
    # metered ONE generation use for the distinct member.
    champion_sha = row0.champion_frozen_sha
    assert champion_sha is not None
    assert row1.opponent_pool_size == 1
    assert row1.opponent_slate_shas == (champion_sha, champion_sha)
    assert row1.opponent_payoffs is not None
    assert set(row1.opponent_payoffs) == {champion_sha}
    assert row1.opponent_uses == {champion_sha: 1}
    assert row1.retired_opponent_shas == ()

    # The row mappings are READ-ONLY views (the machine-readable campaign
    # truth cannot drift from the on-disk JSONL after emission). The casts
    # satisfy the type checker so the RUNTIME immutability is what's pinned.
    with pytest.raises(TypeError):
        cast("dict[str, int]", row1.opponent_uses)["tamper"] = 1
    with pytest.raises(TypeError):
        cast("dict[str, float]", row1.opponent_payoffs)["tamper"] = 1.0

    # Games are counted per generation and cumulatively.
    assert row0.games_played_cumulative == row0.games_played_generation
    assert (
        row1.games_played_cumulative
        == row0.games_played_generation + row1.games_played_generation
    )
    assert row1.games_played_cumulative == first.total_games


# --------------------------------------------------------------------------- #
# The up-front budget guard.                                                   #
# --------------------------------------------------------------------------- #


def test_budget_guard_refuses_over_ceiling_without_override(tmp_path: Path) -> None:
    config = _make_config(tmp_path, allow_over_ceiling=False)
    # The stated bound: 2 generations × (ES (1+2)×2×1 + payoff 4×1 +
    # benchmark 1 + exploiter (1+1×1)×1) = 2 × 13 = 26, over the ceiling of 13.
    assert projected_game_bound(config) == _BASELINE_BOUND
    with pytest.raises(ValueError, match="exceeds the stated ceiling"):
        run_alternating_freeze(config)
    # Refused BEFORE any disk mutation: no halls, no rows, no plan.
    assert not (tmp_path / "halls").exists()
    assert not (tmp_path / "work").exists()


# --------------------------------------------------------------------------- #
# The two additive seams.                                                      #
# --------------------------------------------------------------------------- #


def test_meeting_runner_factory_seam_plumbs_without_perturbing_games(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
    custom_runner_run: CoevoCampaignResult,
) -> None:
    first, _, _ = baseline_runs
    assert len(custom_runner_run.rows) == len(first.rows)
    for custom_row, base_row in zip(custom_runner_run.rows, first.rows, strict=True):
        # The rows honestly record which runner served training games...
        assert custom_row.meeting_runner == "custom"
        # ...and EVERY game-derived field is byte-identical to the unset-seam
        # run: an explicitly-fake factory perturbs nothing but the label.
        assert custom_row.model_dump(exclude={"meeting_runner"}) == base_row.model_dump(
            exclude={"meeting_runner"}
        )


def test_scenario_provider_returning_no_terms_is_digest_identical(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
    empty_provider_run: CoevoCampaignResult,
) -> None:
    first, _, _ = baseline_runs
    assert empty_provider_run.rows == first.rows
    assert empty_provider_run.digest() == first.digest()


def test_scenario_terms_shift_swap_fitness_by_exactly_their_value(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
    scenario_run: CoevoCampaignResult,
) -> None:
    first, _, _ = baseline_runs
    base0, base1 = first.rows
    active0, active1 = scenario_run.rows
    # The term's label rides the swap it was provided for.
    assert active0.scenario_labels == ("skill-probe",)
    assert active1.scenario_labels == ()
    # A constant term shifts the swap's ES fitness channel by exactly its
    # value and cannot move selection (all offspring shift equally), so the
    # champion genome/sha and the absolute benchmark are untouched.
    assert active0.champion_fitness == base0.champion_fitness + _SCENARIO_OFFSET
    assert (
        active0.generation_best_fitness
        == base0.generation_best_fitness + _SCENARIO_OFFSET
    )
    assert active0.champion_weights_sha256 == base0.champion_weights_sha256
    assert (
        active0.anchor_benchmark_champion_side == base0.anchor_benchmark_champion_side
    )
    assert active0.anchor_benchmark_fsm_side == base0.anchor_benchmark_fsm_side
    # Swap 1 provided no terms and is untouched end to end.
    assert active1 == base1
    # The digests honestly differ (the fitness channel moved).
    assert scenario_run.digest() != first.digest()


# --------------------------------------------------------------------------- #
# The conviction term is SERVED into training fitness (the 18.30 wrap).       #
# --------------------------------------------------------------------------- #


def _tightly_capped_term(max_uses: int) -> ConvictionFitnessTerm:
    """The committed GO conviction term with OUR OWN tight counter.

    Reads the committed artifact bundle (read-only) and meters exclusively a
    test-local counter (tighter than the committed cap — the loader's
    tighten-never-loosen rule), so the committed staleness budget is never
    consumed by CI.
    """

    probe = load_conviction_fitness_term()
    assert probe is not None  # the committed verdict is GO
    counter = ConvictionUseCounter(
        ConvictionStalenessCap(
            weights_sha256=probe.weights_sha256,
            max_uses=max_uses,
            unit=probe.use_counter.cap.unit,
        )
    )
    term = load_conviction_fitness_term(use_counter=counter)
    assert term is not None
    return term


def test_conviction_term_is_served_into_training_fitness(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
    tmp_path: Path,
) -> None:
    """The configured term is served live, metered once, and moves fitness.

    Each run gets its OWN tight counter (consumption is cumulative per run and
    rides the rows, so a shared counter would break the double-run digest);
    under the pinned seeds at least one training meeting is predicted, so the
    consumption column moves off zero, the final row quotes exactly the shared
    counter's cumulative reads, and the fitness channel visibly differs from
    the unserved baseline — the term is training pressure, never a
    zero-weighted ghost.
    """

    first_plain, _, _ = baseline_runs
    served_one = run_alternating_freeze(
        _make_config(tmp_path / "one", conviction=_tightly_capped_term(500))
    )
    term_two = _tightly_capped_term(500)
    served_two = run_alternating_freeze(
        _make_config(tmp_path / "two", conviction=term_two)
    )
    # Deterministic under serving: two runs with fresh counters are identical.
    assert served_one.digest() == served_two.digest()
    # Consumption: cumulative, non-decreasing, quoted from the ONE counter.
    uses = [row.conviction_uses for row in served_two.rows]
    assert all(count is not None for count in uses)
    assert uses == sorted(cast("list[int]", uses))
    assert uses[-1] == term_two.use_counter.uses
    assert term_two.use_counter.uses > 0
    # The served term reaches the training-fitness channel: the campaign rows
    # visibly differ from the unserved baseline (selection pressure changed).
    assert served_one.digest() != first_plain.digest()


# --------------------------------------------------------------------------- #
# Staleness: retire-and-replace + the loud exhausted-pool stop.                #
# --------------------------------------------------------------------------- #


def test_staleness_cap_retires_and_exhausted_pool_stops_loudly(
    tmp_path: Path,
) -> None:
    # max_ticks=3 truncates every game to the fitness sentinel, so no exploit
    # is ever strictly better than the FSM baseline — the impostor pool can
    # never gain a fresh replacement, and a 1-generation cap must exhaust it
    # on the second crew generation.
    config = _make_config(
        tmp_path,
        impostor=_impostor_side(population=1),
        crew=_crew_side(population=1),
        master_seed=77,
        generations_per_swap=2,
        slate_size=1,
        staleness_cap=OpponentStalenessCap(max_generations=1, unit="generations"),
        max_ticks=3,
    )
    with pytest.raises(RuntimeError, match="opponent pool is exhausted"):
        run_alternating_freeze(config)
    # The campaign stopped mid-swap, loudly — but every completed generation's
    # row was already flushed to disk (swap 0's two + swap 1's first).
    lines = (tmp_path / "work" / "campaign-rows.jsonl").read_text().splitlines()
    assert len(lines) == 3
    last = CoevoCampaignRow(**json.loads(lines[-1]))
    assert last.swap_index == 1
    assert last.generation_in_swap == 1
    # The one impostor member served exactly its capped single generation.
    assert list(last.opponent_uses.values()) == [1]


# --------------------------------------------------------------------------- #
# Founders + the exploiter probe's hall integration.                           #
# --------------------------------------------------------------------------- #


def _founder_cells(base: Path) -> Path:
    """Persist three 19-gene founder cells through the public 18.6 writer."""

    specs = [
        ({"kill_count": 0.0, "witness_exposure_rate": 0.0, "vent_usage": 0.0}, 1),
        ({"kill_count": 2.0, "witness_exposure_rate": 0.3, "vent_usage": 4.0}, 2),
        ({"kill_count": 5.0, "witness_exposure_rate": 0.9, "vent_usage": 7.0}, 3),
    ]
    archive: dict[tuple[int, int, int], ArchiveCell] = {}
    for descriptors, index in specs:
        cell_key = BEHAVIOR_DESCRIPTOR_CONFIGURATION.bin_values(descriptors)
        archive[cell_key] = ArchiveCell(
            genome=random_genome(_IMPOSTOR_GENOME_LENGTH, seed=index, scale=0.5),
            fitness=float(index),
            descriptors=descriptors,
        )
    artifact_dir = base / "me"
    write_archive_cell_artifacts(
        archive,
        artifact_dir,
        config=map_elites_budget("ci"),
        descriptor_configuration=BEHAVIOR_DESCRIPTOR_CONFIGURATION,
    )
    return artifact_dir


def test_founders_seed_the_pool_and_exploits_join_the_hall(tmp_path: Path) -> None:
    # A one-swap crew campaign against a founder-seeded impostor pool: the
    # founders ingest through the substrate fence BEFORE any sampling, the
    # payoff row exactly covers them, and (fixture-pinned under these seeds)
    # the exploiter probe finds an impostor exploit and freezes it.
    cells = _founder_cells(tmp_path)
    config = _make_config(
        tmp_path,
        substrate_sha256=bakeoff_substrate_sha(),
        impostor=_impostor_side(population=1, founder_cells_dir=cells),
        crew=_crew_side(population=1),
        master_seed=42,
        num_swaps=1,
        first_side="crew",
    )
    result = run_alternating_freeze(config)
    row = result.rows[0]

    impostor_hall = HallOfFame.load(tmp_path / "halls", "impostor")
    founder_shas = {
        member.weights_sha256
        for member in impostor_hall.members
        if member.origin == MAP_ELITES_FOUNDER_ORIGIN
    }
    assert len(founder_shas) == 3
    # Founders were the sampling pool: the payoff row covers exactly them, the
    # slate drew from them, and the crew champion's provenance names one.
    assert row.opponent_pool_size == 3
    assert row.opponent_payoffs is not None
    assert set(row.opponent_payoffs) == founder_shas
    assert set(row.opponent_slate_shas) <= founder_shas
    assert row.champion_frozen is True
    assert row.champion_trained_against in founder_shas

    # Fixture-pinned: the exploiter beat the scripted FSM's own reading of the
    # champion matchup, so its exploit joined the impostor hall with honest
    # provenance (bred against exactly this generation's champion genome).
    assert row.exploiter_outcome == "frozen"
    assert row.exploiter_fitness > row.exploiter_baseline_fitness
    exploits = [
        member for member in impostor_hall.members if member.origin == EXPLOITER_ORIGIN
    ]
    assert len(exploits) == 1
    assert exploits[0].weights_sha256 == row.exploiter_sha
    assert exploits[0].trained_against == row.champion_weights_sha256
    assert exploits[0].generation == 1

    # Task 18.31: EVERY freeze path on this hall — MAP-Elites founders included —
    # writes the four-file loadable artifact with the side's declared family.
    for member in impostor_hall.members:
        member_dir = tmp_path / "halls" / "impostor" / member.path
        assert _artifact_files(member_dir) == _LOADABLE_FILES
        assert (
            json.loads((member_dir / "stamp.json").read_text())["encoder_version"]
            == _IMPOSTOR_ENCODER
        )
        policy, _ = run_tournament._load_candidate_policy(member_dir)
        assert policy.encoder_version == _IMPOSTOR_ENCODER

    crew_hall = HallOfFame.load(tmp_path / "halls", "crew")
    assert [member.origin for member in crew_hall.members] == [SWAP_CHAMPION_ORIGIN]


# --------------------------------------------------------------------------- #
# Campaign ergonomics (Task 18.31): per-generation champions + loadable freezes.#
# --------------------------------------------------------------------------- #


def _artifact_files(artifact_dir: Path) -> list[str]:
    return sorted(path.name for path in artifact_dir.iterdir())


_LOADABLE_FILES = ["config.json", "stamp.json", "weights.json", "weights.json.sha256"]


def test_every_generation_champion_is_persisted_as_a_loadable_artifact(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    """Each generation's champion lands beside the rows, loadable (18.31 fix 2).

    The 18.24 campaign persisted swap champions and exploiter finds only, so its
    intermediate generations had to be re-bred and hand-stamped: 66 real games
    and two recovery passes (report §11 defect 2 / F1). Every row now has its
    genome on disk under ``gen-champions/gen-<N>/<sha>/`` as the four-file
    artifact, keyed by the row's OWN ``champion_weights_sha256``, and it loads
    through the consuming entry point.
    """

    first, _, _ = baseline_runs
    gen_dir = first.gen_champions_dir
    assert gen_dir.is_dir()
    assert sorted(child.name for child in gen_dir.iterdir()) == sorted(
        f"gen-{row.generation_index}" for row in first.rows
    )
    for row in first.rows:
        artifact_dir = (
            gen_dir / f"gen-{row.generation_index}" / (row.champion_weights_sha256)
        )
        assert _artifact_files(artifact_dir) == _LOADABLE_FILES
        stamp = json.loads((artifact_dir / "stamp.json").read_text())
        assert stamp["weights_sha256"] == row.champion_weights_sha256
        assert stamp["encoder_version"] == row.moving_encoder_version
        assert stamp["method"] == COEVO_FREEZE_METHOD
        # The id carries the SIDE and a weights discriminator as well as the
        # origin and generation, so two artifacts never share one (Codex #314).
        assert stamp["policy_id"].endswith(
            f"-{row.moving_side}-{GENERATION_CHAMPION_ORIGIN}"
            f"-gen{row.generation_index}-{row.champion_weights_sha256[:8]}"
        )
        config = json.loads((artifact_dir / "config.json").read_text())
        assert config["side"] == row.moving_side
        assert config["swap_index"] == row.swap_index
        assert config["generation_in_swap"] == row.generation_in_swap
        assert config["champion_updated"] == row.champion_updated
        assert config["hall_origin"] == GENERATION_CHAMPION_ORIGIN
        # The impostor family is the utility scorer here, so no hidden width
        # is declared — and none is invented.
        assert "hidden" not in config

    # The impostor-moving generations load END TO END through the consuming
    # entry point (the §11 defect-4 / F14 invariant this task satisfies).
    impostor_rows = [row for row in first.rows if row.moving_side == "impostor"]
    assert impostor_rows
    for row in impostor_rows:
        artifact_dir = (
            gen_dir / f"gen-{row.generation_index}" / (row.champion_weights_sha256)
        )
        policy, stamp_model = run_tournament._load_candidate_policy(artifact_dir)
        assert policy.encoder_version == _IMPOSTOR_ENCODER
        assert stamp_model.weights_sha256 == row.champion_weights_sha256


def test_generation_champion_artifacts_are_digest_inert_and_deterministic(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    """The persistence moved no row byte, and its own bytes reproduce (18.31).

    The 18.21 double-run digest pin is asserted again HERE against the same
    fixture (rows are the digest's only input, and no row field was added), and
    the new artifacts are themselves a pure function of the campaign: two
    independent runs write byte-identical trees under different work dirs.
    """

    first, second, _ = baseline_runs
    assert first.digest() == second.digest()
    assert first.rows_path.read_bytes() == second.rows_path.read_bytes()
    # No row carries a persistence field — the schema is unchanged.
    assert not {
        key
        for key in first.rows[0].model_dump()
        if "champion_path" in key or "gen_champion" in key
    }

    first_files = sorted(
        path.relative_to(first.gen_champions_dir)
        for path in first.gen_champions_dir.rglob("*")
        if path.is_file()
    )
    second_files = sorted(
        path.relative_to(second.gen_champions_dir)
        for path in second.gen_champions_dir.rglob("*")
        if path.is_file()
    )
    assert first_files == second_files
    assert first_files
    for relative in first_files:
        assert (first.gen_champions_dir / relative).read_bytes() == (
            second.gen_champions_dir / relative
        ).read_bytes()


def test_hall_freezes_are_loadable_four_file_artifacts(
    baseline_runs: tuple[CoevoCampaignResult, CoevoCampaignResult, Path],
) -> None:
    """Every driver hall freeze writes the four-file artifact (18.31 fix 4).

    Swap champions and exploiter finds alike: the campaign's own halls now hold
    artifacts that load through ``_load_candidate_policy`` with no hand-stamping
    pass, with ``encoder_version`` taken from the SIDE CONFIG (never re-derived
    from genome length — §12 Errata item 1).
    """

    first, _, base = baseline_runs
    hall_root = base / "halls"
    for side, encoder in (("impostor", _IMPOSTOR_ENCODER), ("crew", _CREW_ENCODER)):
        hall = HallOfFame.load(hall_root, cast(Side, side))
        assert hall.members
        for member in hall.members:
            member_dir = hall_root / side / member.path
            assert _artifact_files(member_dir) == _LOADABLE_FILES
            stamp = json.loads((member_dir / "stamp.json").read_text())
            assert stamp["encoder_version"] == encoder
            assert stamp["weights_sha256"] == member.weights_sha256
            config = json.loads((member_dir / "config.json").read_text())
            assert config["hall_origin"] == member.origin
            assert config["trained_against"] == member.trained_against
            assert config["side"] == side

    # The impostor members are the ones the consuming entry point loads (a crew
    # artifact belongs to --crew-artifact — the standing 18.19 guard).
    impostor_hall = HallOfFame.load(hall_root, "impostor")
    for member in impostor_hall.members:
        policy, stamp_model = run_tournament._load_candidate_policy(
            hall_root / "impostor" / member.path
        )
        assert policy.encoder_version == _IMPOSTOR_ENCODER
        assert stamp_model.weights_sha256 == member.weights_sha256
    assert first.total_games == _BASELINE_GAMES


def test_existing_generation_champions_dir_is_refused(tmp_path: Path) -> None:
    """The work-dir no-clobber discipline extends to the new artifacts (18.31)."""

    config = _make_config(tmp_path)
    (config.work_dir / "gen-champions").mkdir(parents=True)
    with pytest.raises(FileExistsError, match="per-generation champion artifacts"):
        run_alternating_freeze(config)
    assert not (tmp_path / "halls").exists()


@dataclass(frozen=True)
class _StubPolicy:
    """A build_policy result carrying only the family tag the pin reads."""

    encoder_version: str


def test_masked_mlp_side_without_hidden_fails_loud(tmp_path: Path) -> None:
    """A non-utility impostor family must DECLARE its head width (18.31).

    ``_load_candidate_policy`` reads ``hidden`` from the artifact's config.json
    to rebuild a masked-MLP family; a side that freezes without declaring it
    produces unloadable artifacts — the §12 Errata item-1 failure. It is refused
    before any hall exists, and the width is never guessed from genome length.
    """

    def build_v2(genome: tuple[float, ...]) -> BakeoffPolicy:
        del genome
        return cast(BakeoffPolicy, _StubPolicy("v2"))

    config = _make_config(
        tmp_path,
        impostor=_impostor_side(build_policy=build_v2, encoder_version="v2"),
    )
    with pytest.raises(ValueError, match="needs an integer 'hidden'"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_anchor_policy_without_a_stamp_label_fails_loud(tmp_path: Path) -> None:
    """A side bred on an alternative anchor must NAME it in the stamp (18.31)."""

    stub_anchor = cast(BakeoffPolicy, object())
    config = _make_config(tmp_path, impostor=_impostor_side(anchor_policy=stub_anchor))
    with pytest.raises(ValueError, match="anchor_policy_label is still"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_blank_run_label_is_refused(tmp_path: Path) -> None:
    """The stamp-grade run label rides every artifact, so it is validated (18.31)."""

    with pytest.raises(ValueError, match="run_label must be non-blank"):
        run_alternating_freeze(_make_config(tmp_path / "a", run_label="   "))
    with pytest.raises(ValueError, match="run_label must be MANIFEST-safe"):
        run_alternating_freeze(_make_config(tmp_path / "b", run_label="a|b"))


# --------------------------------------------------------------------------- #
# Fail-loud validation (before any hall exists).                               #
# --------------------------------------------------------------------------- #


def _assert_no_disk_mutation(base: Path) -> None:
    assert not (base / "halls").exists()
    assert not (base / "work").exists()


def test_crew_slot_rejects_an_anchor_policy(tmp_path: Path) -> None:
    stub_anchor = cast(BakeoffPolicy, object())
    config = _make_config(tmp_path, crew=_crew_side(anchor_policy=stub_anchor))
    with pytest.raises(ValueError, match="crew side has no anchor-policy seam"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_conflation_guard_rejects_a_crew_family_in_the_impostor_slot(
    tmp_path: Path,
) -> None:
    wrong_family = _impostor_side(
        genome_length=_CREW_GENOME_LENGTH,
        build_policy=_crew_builder,
        encoder_version=_CREW_ENCODER,
    )
    config = _make_config(tmp_path, impostor=wrong_family)
    with pytest.raises(ValueError, match="impostor side built a crew policy"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_encoder_family_pin_mismatch_fails_loud(tmp_path: Path) -> None:
    # The free-policy-family default pin ("v2") against the utility-scorer
    # builder: the campaign family pin and the builder drifted apart.
    config = _make_config(tmp_path, impostor=_impostor_side(encoder_version="v2"))
    with pytest.raises(ValueError, match="pins encoder_version"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_misconfigurations_fail_loud_before_any_game(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="fitness_seeds must be unique"):
        run_alternating_freeze(
            _make_config(tmp_path / "a", fitness_seeds=(_SEED, _SEED))
        )
    with pytest.raises(ValueError, match="mutually exclusive"):
        run_alternating_freeze(
            _make_config(
                tmp_path / "b",
                meeting_runner_factory=_explicitly_fake_meeting_runner,
                composed=CoevoComposedRunnerConfig(),
            )
        )
    with pytest.raises(ValueError, match="64 lowercase hex"):
        run_alternating_freeze(
            _make_config(tmp_path / "c", substrate_sha256="not-a-sha")
        )
    with pytest.raises(ValueError, match="not interchangeable"):
        run_alternating_freeze(
            _make_config(tmp_path / "d", impostor=_impostor_side(side="crew"))
        )
    # The payoff protocol is never a silent whole-campaign PFSP bypass: the
    # empty seed set is refused (the sampler's cold-start exception is
    # gen-1-shaped and the driver measures even generation 1's row).
    with pytest.raises(ValueError, match="payoff_seeds must be non-empty"):
        run_alternating_freeze(_make_config(tmp_path / "e", payoff_seeds=()))
    # A typo'd first_side from an untyped/deserialized config must never
    # silently run the campaign in the opposite order.
    with pytest.raises(ValueError, match="first_side must be"):
        run_alternating_freeze(_make_config(tmp_path / "f", first_side="imposter"))
    # inf passes a bare positivity check; the ES scale knobs must be finite
    # before any hall or rollout artifact exists.
    with pytest.raises(ValueError, match="sigma must be finite"):
        run_alternating_freeze(
            _make_config(tmp_path / "g", impostor=_impostor_side(sigma=float("inf")))
        )
    # The substrate-kind provenance label would otherwise first fail at row
    # construction — AFTER a generation's games ran.
    with pytest.raises(ValueError, match="substrate_sha_kind must be"):
        run_alternating_freeze(
            _make_config(tmp_path / "h", substrate_sha_kind="bogus-kind")
        )
    # Roster/tick knobs reach the seeder/scheduler only inside the first
    # rollout; they must fail before the rows file exists (whose clobber
    # guard would block the retry).
    with pytest.raises(ValueError, match="num_impostors must be"):
        run_alternating_freeze(_make_config(tmp_path / "i", num_impostors=0))
    with pytest.raises(ValueError, match="num_players must be"):
        run_alternating_freeze(
            _make_config(tmp_path / "j", num_players=1, num_impostors=1)
        )
    with pytest.raises(ValueError, match="max_ticks must be"):
        run_alternating_freeze(_make_config(tmp_path / "k", max_ticks=0))
    # The seeder's own upper bound on tasks-per-crewmate, checked pre-mutation
    # against the canonical map.
    with pytest.raises(ValueError, match="canonical map's task count"):
        run_alternating_freeze(_make_config(tmp_path / "m", tasks_per_crewmate=999))
    # A NaN/inf seed genome could play whole games and freeze NaN weights
    # into a hall; a corrupted seed artifact never enters the campaign.
    with pytest.raises(ValueError, match="non-finite genes"):
        run_alternating_freeze(
            _make_config(
                tmp_path / "l",
                impostor=_impostor_side(
                    initial_genome=(float("nan"),) * _IMPOSTOR_GENOME_LENGTH
                ),
            )
        )
    for sub in ("a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m"):
        _assert_no_disk_mutation(tmp_path / sub)


def test_spent_conviction_meter_is_refused_before_any_disk_mutation(
    tmp_path: Path,
) -> None:
    # A caller-supplied term whose shared counter is already at its cap must
    # refuse at engine init — never after the plan/rows/halls exist.
    term = _tightly_capped_term(1)
    term.use_counter.record_use(weights_sha256=term.weights_sha256)
    with pytest.raises(RuntimeError, match="already spent"):
        run_alternating_freeze(_make_config(tmp_path, conviction=term))
    _assert_no_disk_mutation(tmp_path)


def test_stale_founder_archive_is_refused_before_any_disk_mutation(
    tmp_path: Path,
) -> None:
    # The founder archive records the real bakeoff substrate; a campaign
    # pinned at a DIFFERENT substrate must fail the fence read-only, before
    # the work dir or either hall exists (previously the fence fired at
    # ingest time, behind a freshly created empty hall).
    cells = _founder_cells(tmp_path)
    config = _make_config(
        tmp_path,
        substrate_sha256=_SUBSTRATE,
        impostor=_impostor_side(founder_cells_dir=cells),
    )
    with pytest.raises(ValueError, match="adopted substrate"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_dirty_hall_root_is_refused_before_any_side_is_created(
    tmp_path: Path,
) -> None:
    # A committed crew hall already at the root: the read-only preflight
    # refuses BEFORE the impostor hall (or the work dir) is created — no
    # half-initialized campaign tree for a retry to trip on.
    HallOfFame.create(tmp_path / "halls", "crew", substrate_sha256=_SUBSTRATE)
    with pytest.raises(FileExistsError, match="never clobbers a committed pool"):
        run_alternating_freeze(_make_config(tmp_path))
    assert not (tmp_path / "halls" / "impostor").exists()
    assert not (tmp_path / "work").exists()


def test_composed_adoption_fails_loud_on_missing_artifacts(tmp_path: Path) -> None:
    # The gated adoption path reads the committed caps/verdicts up front: a
    # composed configuration pointing at nothing fails BEFORE any disk
    # mutation — never a campaign that discovers the gap mid-swap.
    config = _make_config(
        tmp_path,
        composed=CoevoComposedRunnerConfig(
            conviction_artifact_dir=tmp_path / "missing-conviction",
            surrogate_artifact_dir=tmp_path / "missing-surrogate",
            composed_artifact_dir=tmp_path / "missing-composed",
        ),
    )
    with pytest.raises(FileNotFoundError):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


# --------------------------------------------------------------------------- #
# The committed impostor-campaign rows (Task 18.24).                           #
#                                                                              #
# Five sequential fresh driver runs, their campaign rows concatenated into one #
# committed JSONL, in run order:                                               #
#                                                                              #
#   1. run-01-utility-champion         12 rows (4 swaps × 3 generations)       #
#   2. run-02-utility-lambda4          12 rows                                 #
#   3. run-03-utility-bcanchor         12 rows                                 #
#   4. run-04-freepolicy-v3            12 rows                                 #
#   5. run-05-freepolicy-v2-founders    4 rows (2 swaps × 2 generations)       #
#                                                                              #
# The runs are recoverable from the concatenation because ``generation_index`` #
# (global per run, ge=1, monotone) restarts at 1 at each run boundary. These   #
# are pure file-read STRUCTURAL pins on the shipped campaign (the             #
# ``test_bakeoff`` committed-artifact idiom): no rollouts run here, and — the   #
# module's pin doctrine — NO campaign float value or digest is pinned as an     #
# absolute constant. The two substrate shas are pinned by DYNAMIC self-        #
# consistency against their live definitions (guarding the two-definition       #
# dispatch), never as hardcoded hex. A missing rows file fails the read loudly, #
# which is the correct behaviour for a committed-artifact pin (the file lands   #
# once the campaign runs finish).                                              #
# --------------------------------------------------------------------------- #

_CAMPAIGN_ROWS_PATH: Path = Path("training/reports/results-impostor-campaign.jsonl")

# Per-run (block) structural facts, in file order; the last block is the
# shorter 2-swap founder run.
_EXPECTED_BLOCK_LENGTHS: tuple[int, ...] = (12, 12, 12, 12, 4)
_BLOCK_NUM_SWAPS: tuple[int, ...] = (4, 4, 4, 4, 2)
# The impostor-moving encoder family per block: the utility scorer's v1 for the
# three utility runs, then the free-policy family's "v3"/"v2" pins.
_BLOCK_IMPOSTOR_ENCODERS: tuple[str, ...] = (
    _IMPOSTOR_ENCODER,
    _IMPOSTOR_ENCODER,
    _IMPOSTOR_ENCODER,
    "v3",
    "v2",
)
# Blocks 1-3 bind to the anchor-study corpus/floor substrate; blocks 4-5 to the
# MAP-Elites corpus MANIFEST substrate.
_COMPUTE_SUBSTRATE_BLOCKS: frozenset[int] = frozenset({0, 1, 2})
_BAKEOFF_SUBSTRATE_BLOCKS: frozenset[int] = frozenset({3, 4})
# The projected per-run game ceiling every run stayed under.
_CAMPAIGN_GAME_CEILING: int = 25000


def _committed_campaign_rows() -> list[CoevoCampaignRow]:
    """Every committed campaign row, parsed in file order (loud on a bad line).

    The ``CoevoCampaignRow(**json.loads(line))`` round-trip idiom — the same one
    ``test_rows_file_round_trips_the_emitted_rows`` uses — so a schema drift (an
    added/removed/renamed field under ``extra="forbid"``) trips HERE too. A
    missing file raises at ``read_text`` (the committed-artifact pin contract).
    """

    lines = _CAMPAIGN_ROWS_PATH.read_text().splitlines()
    return [CoevoCampaignRow(**json.loads(line)) for line in lines if line.strip()]


def _campaign_blocks() -> list[list[CoevoCampaignRow]]:
    """Recover the five runs by splitting on the per-run ``generation_index``.

    ``generation_index`` is global WITHIN a run (ge=1, monotone) and restarts at
    1 at each run boundary, so a fresh block opens exactly when a row's
    ``generation_index`` is 1.
    """

    blocks: list[list[CoevoCampaignRow]] = []
    current: list[CoevoCampaignRow] = []
    for row in _committed_campaign_rows():
        if row.generation_index == 1 and current:
            blocks.append(current)
            current = []
        current.append(row)
    if current:
        blocks.append(current)
    return blocks


class TestCommittedImpostorCampaignRows:
    """Structural pins on the committed five-run impostor campaign JSONL."""

    def test_every_line_parses_and_total_row_count(self) -> None:
        rows = _committed_campaign_rows()
        # Every line round-trips through the row schema; the campaign is the
        # concatenation of the five runs' rows: 4×12 + 4 == 52.
        assert sum(_EXPECTED_BLOCK_LENGTHS) == 52
        assert len(rows) == 52

    def test_generation_index_split_yields_five_blocks(self) -> None:
        blocks = _campaign_blocks()
        # Splitting on generation_index == 1 recovers exactly the five runs.
        assert len(blocks) == 5
        assert tuple(len(block) for block in blocks) == _EXPECTED_BLOCK_LENGTHS

    def test_every_row_carries_the_fixed_protocol_columns(self) -> None:
        for row in _committed_campaign_rows():
            assert row.schema_version == COEVO_CAMPAIGN_ROW_SCHEMA_VERSION
            # The non-composed + conviction protocol decision: training games
            # ran on the fake-provider meeting path, no adoption constraints, no
            # scenario terms, and the surrogate instrument is absent (None, not
            # a zero-ghost).
            assert row.meeting_runner == "fake-provider"
            assert row.adoption_constraints == ()
            assert row.scenario_labels == ()
            assert row.surrogate_uses is None
            # One side moves per generation, always.
            assert row.moving_side != row.frozen_side

    def test_conviction_term_served_non_decreasing_per_block(self) -> None:
        for block in _campaign_blocks():
            uses = [row.conviction_uses for row in block]
            # Served every generation (never a None zero-ghost), cumulative and
            # non-decreasing within the run, and strictly positive by the end —
            # the conviction term reached the training-fitness channel.
            assert all(count is not None for count in uses)
            metered = cast("list[int]", uses)
            assert metered == sorted(metered)
            assert metered[-1] > 0

    def test_each_block_alternates_from_an_impostor_first_swap(self) -> None:
        for block in _campaign_blocks():
            # first_side impostor: the opening swap of every run moves the
            # impostor side.
            assert block[0].moving_side == "impostor"
            # Games accrue strictly within a run (the per-run cumulative clock),
            # and every run stays under the projected ceiling.
            cumulative = [row.games_played_cumulative for row in block]
            assert all(
                earlier < later
                for earlier, later in zip(cumulative, cumulative[1:], strict=False)
            )
            assert cumulative[-1] <= _CAMPAIGN_GAME_CEILING

    def test_substrate_sha_kind_and_value_dispatch_per_block(self) -> None:
        # A DYNAMIC self-consistency pin: the recorded shas must equal the live
        # definitions, guarding the two-definition dispatch (never hardcoded).
        compute_sha = compute_substrate_sha()
        bakeoff_sha = bakeoff_substrate_sha()
        for index, block in enumerate(_campaign_blocks()):
            if index in _COMPUTE_SUBSTRATE_BLOCKS:
                for row in block:
                    assert row.substrate_sha_kind == "compute_substrate_sha"
                    assert row.substrate_sha256 == compute_sha
            else:
                assert index in _BAKEOFF_SUBSTRATE_BLOCKS
                for row in block:
                    assert row.substrate_sha_kind == "bakeoff_substrate_sha"
                    assert row.substrate_sha256 == bakeoff_sha

    def test_moving_encoder_version_per_block_and_side(self) -> None:
        for index, block in enumerate(_campaign_blocks()):
            impostor_encoder = _BLOCK_IMPOSTOR_ENCODERS[index]
            for row in block:
                if row.moving_side == "impostor":
                    assert row.moving_encoder_version == impostor_encoder
                else:
                    assert row.moving_encoder_version == _CREW_ENCODER

    def test_swap_champions_are_frozen_once_per_swap(self) -> None:
        for index, block in enumerate(_campaign_blocks()):
            frozen_rows = [row for row in block if row.champion_frozen]
            # One freeze per swap, each carrying a real champion sha.
            assert len(frozen_rows) == _BLOCK_NUM_SWAPS[index]
            for row in frozen_rows:
                assert row.champion_frozen_sha is not None

    def test_founder_pool_serves_the_final_run(self) -> None:
        block5 = _campaign_blocks()[4]
        # The 30 MAP-Elites founders in the impostor hall are the frozen pool
        # the crew-moving swap trains against (opponent_pool_size is the FROZEN
        # side's active pool for the moving side's generation).
        assert any(row.opponent_pool_size >= 30 for row in block5)


def test_unloadable_impostor_family_is_refused(tmp_path: Path) -> None:
    """A family the CONSUMER cannot rebuild is refused up front (Codex #314).

    ``_load_candidate_policy`` sends every non-utility tag to
    ``build_masked_mlp_policy``, which accepts only ``v2`` / ``v3``. Declaring
    any other impostor family would freeze artifacts nothing can load — and the
    campaign would only discover it after paying for every generation.
    """

    def build_v9(genome: tuple[float, ...]) -> BakeoffPolicy:
        del genome
        return cast(BakeoffPolicy, _StubPolicy("v9"))

    config = _make_config(
        tmp_path,
        impostor=_impostor_side(build_policy=build_v9, encoder_version="v9", hidden=8),
    )
    with pytest.raises(ValueError, match="not one the consuming entry point"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_bad_stamp_tokens_are_refused_before_any_disk_mutation(tmp_path: Path) -> None:
    """Stamp tokens are validated in the preflight, not at hall-build time.

    ``LoadableArtifactMetadata`` would otherwise first reject a malformed
    ``anchor_policy_label`` while the halls are being constructed — after the
    work dir and campaign plan exist — leaving a half-started tree behind a
    configuration typo (Codex on PR #314).
    """

    # A custom anchor WITH a MANIFEST-unsafe label: the anchor identity rule is
    # satisfied (anchor supplied, label named), so the token check is what must
    # catch it — and it must do so before any mkdir.
    stub_anchor = cast(BakeoffPolicy, object())
    with pytest.raises(ValueError, match="MANIFEST-safe"):
        run_alternating_freeze(
            _make_config(
                tmp_path / "a",
                impostor=_impostor_side(
                    anchor_policy=stub_anchor, anchor_policy_label="a|b"
                ),
            )
        )
    _assert_no_disk_mutation(tmp_path / "a")

    with pytest.raises(ValueError, match="non-blank"):
        run_alternating_freeze(
            _make_config(tmp_path / "b", crew=_crew_side(anchor_policy_label="   "))
        )
    _assert_no_disk_mutation(tmp_path / "b")


def test_anchor_label_without_an_anchor_policy_is_refused(tmp_path: Path) -> None:
    """The anchor identity is enforced in BOTH directions (Codex on PR #314).

    Naming an anchor artifact while supplying none means the campaign trains
    against the scripted FSM and every stamp claims otherwise — the mirror of
    the custom-anchor-without-a-label case, and the same false provenance.
    """

    config = _make_config(
        tmp_path, impostor=_impostor_side(anchor_policy_label="filtered-bc-anchor")
    )
    with pytest.raises(ValueError, match="supplies no anchor_policy"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_declared_hidden_is_proven_against_the_consuming_builder(
    tmp_path: Path,
) -> None:
    """A mis-declared ``hidden`` is caught by the CONSUMER's own builder (18.31).

    A width that is merely positive is not enough: if the side declares 4 while
    ``build_policy`` captured 8, training and the encoder probe both succeed,
    every artifact records 4, and ``_load_candidate_policy`` rebuilds with 4 and
    rejects the genome length — after the campaign has run (Codex on PR #314).
    The preflight therefore runs ``build_masked_mlp_policy`` at the declared
    width over the real genome, which is exactly the reconstruction the frozen
    artifact must survive.
    """

    from orchestrator.boundary import public_map_from_engine_map
    from training.bakeoff.policy_es import (
        TARGET_KILL_SLOTS,
        build_masked_mlp_policy,
        policy_genome_length,
    )

    from agents.tactical.features import TacticalFeatureEncoderV3
    from engine.world import load_canonical_map

    hidden = 8
    genome_length = policy_genome_length(
        public_map_from_engine_map(load_canonical_map()),
        hidden=hidden,
        encoder=TacticalFeatureEncoderV3(),
        target_slots=TARGET_KILL_SLOTS,
    )

    def build_v3(genome: tuple[float, ...]) -> BakeoffPolicy:
        return build_masked_mlp_policy(
            genome,
            game_map=load_canonical_map(),
            hidden=hidden,
            encoder_version="v3",
        )

    # The honest declaration passes the preflight (it fails later, on the
    # over-ceiling guard, which proves validation was cleared).
    honest = _make_config(
        tmp_path / "ok",
        impostor=_impostor_side(
            genome_length=genome_length,
            build_policy=build_v3,
            encoder_version="v3",
            hidden=hidden,
            initial_genome=(0.0,) * genome_length,
        ),
        game_ceiling=1,
        allow_over_ceiling=False,
    )
    with pytest.raises(ValueError, match="exceeds the stated ceiling"):
        run_alternating_freeze(honest)

    # The mis-declared width is refused by the consuming builder itself.
    wrong = _make_config(
        tmp_path / "bad",
        impostor=_impostor_side(
            genome_length=genome_length,
            build_policy=build_v3,
            encoder_version="v3",
            hidden=4,
            initial_genome=(0.0,) * genome_length,
        ),
    )
    with pytest.raises(ValueError, match="cannot rebuild"):
        run_alternating_freeze(wrong)
    _assert_no_disk_mutation(tmp_path / "bad")


def test_utility_family_rejects_a_declared_hidden_width(tmp_path: Path) -> None:
    """The utility scorer takes no head width, so declaring one is refused.

    The consumer ignores ``hidden`` for this family, so such artifacts still
    load — but every ``config.json`` would falsely claim a masked-MLP width.
    ``RealPathCandidate`` rejects the same combination for the same family
    (Codex on PR #314).
    """

    config = _make_config(tmp_path, impostor=_impostor_side(hidden=8))
    with pytest.raises(ValueError, match="takes no hidden width"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_a_boolean_hidden_width_is_refused_not_coerced(tmp_path: Path) -> None:
    """``hidden=True`` is a guess, not a width of 1 (Codex on PR #314).

    ``bool`` is an ``int`` subtype, so ``True`` satisfies the ``>= 1`` check and
    reads as width 1 — and ``CoevoSideConfig`` is a plain dataclass, so nothing
    coerces or rejects it on the way in. "Yes, this family has a hidden layer"
    would silently become "width 1", which is exactly the inferred width §12
    Errata item 1 records the cost of. Refused at the side config, before any
    work dir exists.
    """

    for boolean in (True, False):
        config = _make_config(
            tmp_path,
            impostor=_impostor_side(hidden=boolean),
        )
        with pytest.raises(ValueError, match="non-boolean integer"):
            run_alternating_freeze(config)
        _assert_no_disk_mutation(tmp_path)


def test_crew_family_rejects_a_declared_hidden_width(tmp_path: Path) -> None:
    """The crew scorer takes no head width either (Codex on PR #314).

    The round-3 family rules were written inside the ``impostor`` branch, so a
    crew side declaring ``hidden`` passed validation and stamped that width into
    every crew freeze's ``config.json``. Crew artifacts rebuild through
    ``build_crew_scorer``, which has no width input — exactly the false
    masked-MLP provenance the utility-family guard rejects, reachable on the
    other side.
    """

    config = _make_config(tmp_path, crew=_crew_side(hidden=8))
    with pytest.raises(ValueError, match="crew family .* takes no hidden width"):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)


def test_crew_family_must_be_one_the_consumer_can_rebuild(tmp_path: Path) -> None:
    """The crew side gets the SAME loadability preflight the impostor side has.

    The 18.19 namespace guard only proves a tag starts with ``crew-``, so an
    arbitrary ``crew-option-features-v9`` passed validation and froze artifacts
    ``_load_crew_artifact_policy`` cannot rebuild — discovered only after the
    campaign was paid for (Codex on PR #314).
    """

    class _ExoticCrewPolicy:
        """A crew policy in the ``crew-*`` namespace that no loader can rebuild."""

        def __init__(self, inner: object) -> None:
            self._inner = inner
            self.encoder_version = "crew-option-features-v9"

        def __getattr__(self, name: str) -> object:
            return getattr(self._inner, name)

    def _exotic_crew_builder(genome: tuple[float, ...]) -> object:
        return _ExoticCrewPolicy(_crew_builder(genome))

    config = _make_config(
        tmp_path,
        crew=_crew_side(
            build_policy=_exotic_crew_builder,
            encoder_version="crew-option-features-v9",
        ),
    )
    with pytest.raises(
        ValueError, match="not one the consuming entry point can rebuild"
    ):
        run_alternating_freeze(config)
    _assert_no_disk_mutation(tmp_path)
