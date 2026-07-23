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
  any hall exists on disk.

Every fixture-pinned count below (games, hall sizes, exploiter outcomes) was
obtained by running the code under the fixed seeds and then hard-pinned here
(the ``test_hall_of_fame`` idiom); float values and digests are asserted only
RELATIVE to a same-process twin run, never as absolute constants (the
platform-sensitivity lesson from the ``test_es`` hash pin).
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from llm.provider import ENV_PROVIDER, PROVIDER_FAKE, build_default_client
from orchestrator.game import MeetingRunner, build_default_meeting_runner
from training.bakeoff.es import random_genome
from training.bakeoff.harness import BakeoffPolicy
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
    EXPLOITER_ORIGIN,
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
from training.crew.options import OwnedTaskOptionBasis
from training.crew.scorer import CrewOptionScorer, CrewTrackPolicy, build_crew_scorer

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
        # Per-gen fitness channel.
        assert isinstance(row.champion_fitness, float)
        assert isinstance(row.generation_best_fitness, float)
        # The absolute anchor benchmark, both directions, every generation.
        assert isinstance(row.anchor_benchmark_champion_side, float)
        assert isinstance(row.anchor_benchmark_fsm_side, float)
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
        payoff_seeds=(),
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

    crew_hall = HallOfFame.load(tmp_path / "halls", "crew")
    assert [member.origin for member in crew_hall.members] == [SWAP_CHAMPION_ORIGIN]


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
    for sub in ("a", "b", "c", "d"):
        _assert_no_disk_mutation(tmp_path / sub)


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
