"""Tests for the dual-role co-evolution rollout + factory (Task 18.19).

Pins the definition-of-done contract for :mod:`training.coevo`, the seam that
composes the 15.15 impostor bake-off wrapper (``training.bakeoff.harness._CandidateAgent``)
and the 15.16 crew wrapper (``training.crew.scorer._CrewCandidateAgent``) into ONE
game so BOTH sides can be independently scripted-FSM, a live candidate, or a
frozen learned artifact:

* a dual-learned rollout is byte-deterministic (identical state-hash chain across
  two runs) and scores BOTH sides' inner fitness off the ONE reconstructed
  episode, each from its OWN trace object threaded through the factory;
* every SINGLE-side path is byte-identical to its single-side twin — the co-evo
  factory reduces to ``build_candidate_factory`` when the crew policy is ``None``,
  to ``build_crew_candidate_factory`` when the impostor policy is ``None``, and to
  the fully-scripted FSM when both are ``None`` (the interposed side's trace
  accumulators match the single-side run's byte-for-byte);
* the encoder-namespace conflation guard fails loud at factory-build time —
  BEFORE any game runs — when a crew policy lands in the impostor slot or a
  non-crew policy in the crew slot, so ``rollout_coevo`` raises without writing a
  replay (AGENTS.md: no silent fallbacks);
* a truncated (tick-budget-capped) episode scores both sides at the documented
  ``TRUNCATED_EPISODE_FITNESS`` sentinel, never a silent skip;
* the anchor-weight seam is exact arithmetic over the pure ``(rollout, trace)``
  fitness functions (weight 0 == the shaped total; the default-weight fitness ==
  shaped minus ``weight × mean_anchor_ce``) — no extra games needed;
* the two-identity read-back (:func:`orchestrator.replay.read_policy_stamps`)
  round-trips zero/one/two stamps into DISTINCT named slots, and the committed
  canonical sets read back the zero-stamp pair.

Every game runs at a modest CI budget (a handful of 9p2i fake-provider rollouts
through ``rollout_coevo``, reused across assertions), not an operator protocol.
The rollout functions hard-wire the deterministic fake provider, so no ambient
provider env is needed (the root autouse fixture pins it anyway).
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from orchestrator.replay import (
    CrewTacticalPolicyStamp,
    PolicyStamps,
    ReplayLog,
    TacticalPolicyStamp,
    read_policy_stamps,
)
from training.bakeoff.harness import (
    DEFAULT_ANCHOR_PENALTY_WEIGHT,
    TRUNCATED_EPISODE_FITNESS,
    BakeoffPolicy,
    DecisionTrace,
    inner_episode_fitness,
    load_candidate_weights,
    rollout_candidate,
)
from training.bakeoff.utility_es import build_utility_scorer_policy
from training.coevo.factory import CREW_ENCODER_NAMESPACE_PREFIX, build_coevo_factory
from training.coevo.rollout import CoevoRolloutResult, rollout_coevo
from training.crew.options import OwnedTaskOptionBasis
from training.crew.scorer import (
    CrewDecisionTrace,
    CrewTrackPolicy,
    build_crew_scorer,
    crew_inner_episode_fitness,
    rollout_crew_candidate,
)
from training.rewards import compute_shaped_reward

# The committed cheap linear scorers (the shared artifact/weights layout): the
# 19-genome utility scorer (impostor encoder ``impostor-option-features-v1``) and
# the 27-genome owned-task crew scorer (crew encoder ``crew-option-features-v2``).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_IMPOSTOR_ARTIFACT = _REPO_ROOT / "training" / "artifacts" / "impostor" / "utility-es"
_CREW_ARTIFACT = _REPO_ROOT / "training" / "artifacts" / "crew" / "crew-owned-tasks-es"

# A low seed that lands a DECISIVE game_over for the committed learned pair within
# the default 9p2i budget (empirically IMPOSTORS at tick 28), so the dual-learned
# game completes and both anchor-CE channels are non-zero. (The dual-learned pair
# runs long on many seeds — 1004 hits TICK_BUDGET — so the completing seed is
# pinned empirically, the test_crew_scorer seed-1000 idiom.)
_SEED = 1000
# The truncation-sentinel budget: max_ticks=3 truncates almost immediately (the
# crew scorer test's idiom).
_TRUNCATION_MAX_TICKS = 3


@pytest.fixture(scope="module")
def impostor_policy() -> BakeoffPolicy:
    return build_utility_scorer_policy(load_candidate_weights(_IMPOSTOR_ARTIFACT))


@pytest.fixture(scope="module")
def crew_policy() -> CrewTrackPolicy:
    return build_crew_scorer(
        load_candidate_weights(_CREW_ARTIFACT), basis=OwnedTaskOptionBasis()
    )


@pytest.fixture(scope="module")
def dual_pair(
    impostor_policy: BakeoffPolicy,
    crew_policy: CrewTrackPolicy,
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[CoevoRolloutResult, CoevoRolloutResult, Path]:
    """Two dual-learned rollouts at the SAME seed, separate output dirs.

    Module-scoped so the two full games run ONCE and are reused across the
    determinism/fitness pins (test 1) and the anchor-weight seam pin (test 5).
    Returns both results plus the first run's output dir (for the on-disk
    replay-file pin).
    """

    base = tmp_path_factory.mktemp("dual")
    first_dir = base / "first"
    first = rollout_coevo(impostor_policy, crew_policy, _SEED, output_dir=first_dir)
    second = rollout_coevo(
        impostor_policy, crew_policy, _SEED, output_dir=base / "second"
    )
    return first, second, first_dir


def test_dual_learned_is_deterministic_and_scores_both_sides(
    dual_pair: tuple[CoevoRolloutResult, CoevoRolloutResult, Path],
) -> None:
    first, second, first_dir = dual_pair
    # Byte-determinism: the state-hash chain is identical across the two runs.
    assert first.rollout.state_hashes == second.rollout.state_hashes
    assert first.impostor_fitness == second.impostor_fitness
    assert first.crew_fitness == second.crew_fitness
    # BOTH sides actually decided (each side's OWN trace object was threaded).
    assert first.impostor_trace.impostor_decisions > 0
    assert first.crew_trace.crew_decisions > 0
    # Each fitness is the pure (rollout, trace) fitness over its OWN trace — the
    # default weight/None-conviction call rode the result.
    assert first.impostor_fitness == inner_episode_fitness(
        first.rollout, first.impostor_trace
    )
    assert first.crew_fitness == crew_inner_episode_fitness(
        first.rollout, first.crew_trace
    )
    # The rollout wrote its replay to disk.
    assert (first_dir / f"replay-seed-{_SEED}.jsonl").exists()


def test_single_side_paths_are_byte_identical_to_the_single_side_twins(
    impostor_policy: BakeoffPolicy,
    crew_policy: CrewTrackPolicy,
    tmp_path: Path,
) -> None:
    # Impostor-only: the co-evo factory reduces to build_candidate_factory (crew
    # side scripted-FSM), so the trajectory AND the interposed impostor trace
    # match rollout_candidate byte-for-byte.
    coevo_imp = rollout_coevo(
        impostor_policy, None, _SEED, output_dir=tmp_path / "coevo-imp"
    )
    single_imp_trace = DecisionTrace()
    single_imp = rollout_candidate(
        impostor_policy,
        _SEED,
        output_dir=tmp_path / "single-imp",
        trace=single_imp_trace,
    )
    assert coevo_imp.rollout.state_hashes == single_imp.state_hashes
    assert coevo_imp.impostor_trace.anchor_ce_sum == single_imp_trace.anchor_ce_sum
    assert (
        coevo_imp.impostor_trace.impostor_decisions
        == single_imp_trace.impostor_decisions
    )

    # Crew-only: reduces to build_crew_candidate_factory (impostor side
    # scripted-FSM); the crew trace matches rollout_crew_candidate.
    coevo_crew = rollout_coevo(
        None, crew_policy, _SEED, output_dir=tmp_path / "coevo-crew"
    )
    single_crew_trace = CrewDecisionTrace()
    single_crew = rollout_crew_candidate(
        crew_policy,
        _SEED,
        output_dir=tmp_path / "single-crew",
        trace=single_crew_trace,
    )
    assert coevo_crew.rollout.state_hashes == single_crew.state_hashes
    assert coevo_crew.crew_trace.anchor_ce_sum == single_crew_trace.anchor_ce_sum
    assert coevo_crew.crew_trace.crew_decisions == single_crew_trace.crew_decisions

    # FSM/FSM: both scripted; identical to a fully-scripted rollout_candidate(None).
    coevo_fsm = rollout_coevo(None, None, _SEED, output_dir=tmp_path / "coevo-fsm")
    single_fsm = rollout_candidate(None, _SEED, output_dir=tmp_path / "single-fsm")
    assert coevo_fsm.rollout.state_hashes == single_fsm.state_hashes


def test_conflation_guard_fails_loud_before_any_game(
    impostor_policy: BakeoffPolicy,
    crew_policy: CrewTrackPolicy,
    tmp_path: Path,
) -> None:
    from engine.world import load_canonical_map

    game_map = load_canonical_map()
    # A crew policy in the IMPOSTOR slot: the guard keys on the crew encoder
    # namespace prefix and raises at build time.
    assert crew_policy.encoder_version.startswith(CREW_ENCODER_NAMESPACE_PREFIX)
    with pytest.raises(ValueError, match="impostor slot"):
        build_coevo_factory(cast(BakeoffPolicy, crew_policy), None, game_map=game_map)
    # A non-crew (impostor) policy in the CREW slot.
    assert not impostor_policy.encoder_version.startswith(CREW_ENCODER_NAMESPACE_PREFIX)
    with pytest.raises(ValueError, match="crew slot"):
        build_coevo_factory(
            None, cast(CrewTrackPolicy, impostor_policy), game_map=game_map
        )

    # Same guard through rollout_coevo: it raises BEFORE writing a replay file.
    out = tmp_path / "guarded"
    with pytest.raises(ValueError, match="impostor slot"):
        rollout_coevo(cast(BakeoffPolicy, crew_policy), None, _SEED, output_dir=out)
    assert not list(out.glob("replay-seed-*.jsonl"))


def test_truncated_episode_scores_the_sentinel_on_both_sides(
    impostor_policy: BakeoffPolicy,
    crew_policy: CrewTrackPolicy,
    tmp_path: Path,
) -> None:
    result = rollout_coevo(
        impostor_policy,
        crew_policy,
        _SEED,
        output_dir=tmp_path,
        max_ticks=_TRUNCATION_MAX_TICKS,
    )
    assert not result.rollout.complete
    assert result.impostor_fitness == TRUNCATED_EPISODE_FITNESS
    assert result.crew_fitness == TRUNCATED_EPISODE_FITNESS


def test_anchor_weight_seam_is_exact_arithmetic(
    dual_pair: tuple[CoevoRolloutResult, CoevoRolloutResult, Path],
) -> None:
    first, _, _ = dual_pair
    # A complete episode is required for the shaped-reward channel; the sentinel
    # branch would make the arithmetic degenerate.
    assert first.rollout.complete
    # Impostor side: weight 0 == the shaped total; the default-weight fitness ==
    # shaped minus weight × mean anchor CE. Both computed over the SAME returned
    # rollout/trace (the fitness functions are pure) — no extra games.
    imp_shaped = compute_shaped_reward(first.rollout, "IMPOSTOR").total()
    assert (
        inner_episode_fitness(first.rollout, first.impostor_trace, anchor_weight=0.0)
        == imp_shaped
    )
    assert first.impostor_fitness == (
        imp_shaped
        - DEFAULT_ANCHOR_PENALTY_WEIGHT * first.impostor_trace.mean_anchor_ce()
    )
    # Crew side: the same seam with the reward side flipped.
    crew_shaped = compute_shaped_reward(first.rollout, "CREWMATE").total()
    assert (
        crew_inner_episode_fitness(first.rollout, first.crew_trace, anchor_weight=0.0)
        == crew_shaped
    )
    assert first.crew_fitness == (
        crew_shaped - DEFAULT_ANCHOR_PENALTY_WEIGHT * first.crew_trace.mean_anchor_ce()
    )


# A distinct impostor + crew stamp pair (all ten fields non-default, disjoint
# policy_id / weights_sha256) to prove every field round-trips and the two
# identities land in DISTINCT typed slots.
_IMPOSTOR_STAMP = TacticalPolicyStamp(
    policy_id="utility-es",
    method="utility-scorer-es",
    encoder_version="impostor-option-features-v1",
    weights_sha256="a" * 64,
    anchor_policy="fsm-default",
)
_CREW_STAMP = CrewTacticalPolicyStamp(
    policy_id="crew-owned-tasks-es",
    method="crew-utility-scorer-es",
    encoder_version="crew-option-features-v2",
    weights_sha256="b" * 64,
    anchor_policy="fsm-default",
)


def test_read_policy_stamps_round_trips_zero_one_two(tmp_path: Path) -> None:
    # Zero stamps: the scripted-default pair.
    none_path = tmp_path / "none.jsonl"
    ReplayLog(none_path, game_id="g-none").record_game_end(
        winner="CREWMATES", reason="CREWMATE_TASKS", tick=5
    )
    assert read_policy_stamps(none_path) == PolicyStamps(tactical=None, crew=None)

    # Impostor only: crew slot stays the scripted crew default.
    imp_path = tmp_path / "imp.jsonl"
    ReplayLog(
        imp_path, game_id="g-imp", tactical_policy_stamp=_IMPOSTOR_STAMP
    ).record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=6)
    imp_only = read_policy_stamps(imp_path)
    assert imp_only.tactical == _IMPOSTOR_STAMP
    assert imp_only.crew is None

    # Crew only: impostor slot stays the scripted FSM default.
    crew_path = tmp_path / "crew.jsonl"
    ReplayLog(
        crew_path, game_id="g-crew", crew_tactical_policy_stamp=_CREW_STAMP
    ).record_game_end(winner="CREWMATES", reason="CREWMATE_TASKS", tick=7)
    crew_only = read_policy_stamps(crew_path)
    assert crew_only.tactical is None
    assert crew_only.crew == _CREW_STAMP

    # Both: the dual-stamp co-evo recording round-trips all ten fields into the
    # two DISTINCT named slots.
    both_path = tmp_path / "both.jsonl"
    ReplayLog(
        both_path,
        game_id="g-both",
        tactical_policy_stamp=_IMPOSTOR_STAMP,
        crew_tactical_policy_stamp=_CREW_STAMP,
    ).record_game_end(winner="IMPOSTORS", reason="IMPOSTOR_PARITY", tick=8)
    both = read_policy_stamps(both_path)
    assert both == PolicyStamps(tactical=_IMPOSTOR_STAMP, crew=_CREW_STAMP)
    assert both.tactical is not None and both.crew is not None
    # Named-slot access + disjoint identities (never positionally conflated).
    assert both.tactical.encoder_version == "impostor-option-features-v1"
    assert both.crew.encoder_version == "crew-option-features-v2"
    assert both.tactical.policy_id != both.crew.policy_id
    assert both.tactical.weights_sha256 != both.crew.weights_sha256


@pytest.mark.parametrize("set_name", ["9p2i", "4p1i"])
def test_read_policy_stamps_reads_committed_samples_as_zero_stamp(
    set_name: str,
) -> None:
    # The committed canonical sets predate BOTH stamps, so the dual reader returns
    # the zero-stamp pair (each side its scripted default).
    path = _REPO_ROOT / "replays" / "samples" / set_name / "replay-seed-0.jsonl"
    assert read_policy_stamps(path) == PolicyStamps(tactical=None, crew=None)
