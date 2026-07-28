"""Definition-of-done tests for the real-path re-rank recorder (Task 18.17).

These run on the deterministic FAKE provider over the cheap 4p1i roster (the
committed baseline-6 floor block covers it, eval/watchability.py). Seeds 1 and 2
each fire exactly one meeting through the committed utility-es and policy-es
genomes on this roster and every game ends decisively (so its ``game_over``
record carries a read-back-able stamp) — verified empirically while authoring.

The tests pin the DoD contracts: K×N recording + scoring into ranking rows, the
stamp read back FROM BYTES, a hung meeting failing its seed loudly within the
timeout, the retry budget re-recording after a timeout, jsonl round-trip, the
champion-trace helper, and fail-loud input validation.

Task 18.31 adds two blocks, both driven by the 18.24 campaign's incurred costs
(training/reports/report-impostor-campaign.md §11): the RESUME predicate pinned
in BOTH directions (a verified element is skipped; a stamp-sha mismatch, a
truncated recording, a completeness-fence failure, a missing replay, and a
``TICK_BUDGET_REACHED`` element each re-record), and the native
pre-screen-record + append-only leg-log writers that make the blocker-4
ordering evidence a library artifact instead of a shell redirection.
"""

from __future__ import annotations

import ast
import asyncio
import fcntl
import json
import os
import shutil
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import pytest
from pydantic import ValidationError

from agents.base import AgentInterface
from engine.entities import PlayerId
from engine.world import Map, WorldState, load_canonical_map
from agents.strategic.prompts.loader import resolve_prompt_set
from orchestrator.game import PROMPT_VERSION_SETS
from eval.balance_eval import _resolve_game_budget
from llm.budget import BudgetExceededError
from meetings.manager import MeetingTrigger
from orchestrator.game import (
    MeetingArtifacts,
    MeetingRunner,
    build_default_meeting_runner,
    prompt_versions_for_set,
)
from orchestrator.replay import (
    fsm_default_tactical_policy_stamp,
    read_policy_stamps,
    read_tactical_policy_stamp,
)
import training.realpath as realpath
from training.realpath import _AUDIT_SIDECAR_SUFFIX as _AUDIT_SUFFIX
from training.bakeoff.es import ESResult
from training.bakeoff.harness import load_candidate_weights
from training.coevo.hall_of_fame import write_loadable_artifact
from training.realpath import (
    LEG_LOG_FILENAME,
    MODE_CHAMPION_TRACE,
    MODE_TOP_K,
    PRESCREEN_ADVICE_NOTE,
    PRESCREEN_SCHEMA_VERSION,
    SCHEMA_VERSION,
    PreScreenQuote,
    PreScreenRecord,
    RealPathCandidate,
    RealPathLegLog,
    RealPathMeetingTimeoutError,
    RealPathRerankConfig,
    RealPathRerankError,
    RealPathRerankResult,
    RealPathRerankRow,
    RealPathSeedExhaustedError,
    RealPathStampError,
    _build_agent_factory,
    _TimeoutMeetingRunner,
    _genome_digest,
    candidates_from_champion_trace,
    run_realpath_rerank,
    tranche_key,
    write_prescreen_record,
)

# --------------------------------------------------------------------------- #
# Committed-artifact fixtures (the two impostor champions).                    #
# --------------------------------------------------------------------------- #

_UTIL_DIR = Path("training/artifacts/impostor/utility-es")
_POL_DIR = Path("training/artifacts/impostor/policy-es")
_UTIL_ENCODER = "impostor-option-features-v1"
_POL_ENCODER = "v2"
_UTIL_DIGEST = "6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0"


def _util_weights() -> tuple[float, ...]:
    return load_candidate_weights(_UTIL_DIR)


def _pol_weights() -> tuple[float, ...]:
    return load_candidate_weights(_POL_DIR)


def _util_candidate(label: str = "utility-es") -> RealPathCandidate:
    return RealPathCandidate(
        label=label,
        genome=_util_weights(),
        encoder_version=_UTIL_ENCODER,
        policy_id="utility-es",
        method="utility-scorer-es",
    )


def _claim_entry(
    label: str, directory: str, candidate: RealPathCandidate | None = None
) -> dict[str, object]:
    """One leg-manifest candidate entry, shaped exactly as the recorder writes it.

    Fixtures must not be thinner than the real artifact: an entry without the
    identity fields is corrupted evidence the recorder refuses, so a fixture that
    omitted them would be pinning a state that cannot occur.
    """

    resolved = candidate if candidate is not None else _util_candidate(label=label)
    return {
        "dir": directory,
        "encoder_version": resolved.encoder_version,
        "hidden": resolved.hidden,
        "label": label,
        "weights_sha256": realpath._genome_digest(resolved.genome),
    }


def _pol_candidate(label: str = "policy-es") -> RealPathCandidate:
    return RealPathCandidate(
        label=label,
        genome=_pol_weights(),
        encoder_version=_POL_ENCODER,
        hidden=8,
        policy_id="policy-es",
        method="policy-net-es",
    )


def _config(**overrides: object) -> RealPathRerankConfig:
    """A cheap 4p1i config (meetings fire; games end fast on the fake provider)."""

    base: dict[str, object] = {
        "num_players": 4,
        "num_impostors": 1,
        "tasks_per_crewmate": 2,
        "meeting_timeout_seconds": 30.0,
        "max_attempts": 2,
    }
    base.update(overrides)
    return RealPathRerankConfig(**base)  # type: ignore[arg-type]


@dataclass
class _HangRunner:
    """A :class:`MeetingRunner` whose meeting never returns (simulated hang)."""

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        await asyncio.Event().wait()
        raise AssertionError("hang runner must never return")  # unreachable


@dataclass
class _BudgetStopRunner:
    """A :class:`MeetingRunner` whose meeting exhausts the per-game budget."""

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, AgentInterface],
    ) -> MeetingArtifacts:
        raise BudgetExceededError(
            dimension="cost_usd", current=0.29, delta=0.02, cap=0.30
        )


# --------------------------------------------------------------------------- #
# 1. K×N recording + scoring into ranking rows.                               #
# --------------------------------------------------------------------------- #


def test_two_candidate_ranking_records_and_scores(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    ranking_path = tmp_path / "ranking.jsonl"
    result = run_realpath_rerank(
        [_util_candidate(), _pol_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=ranking_path,
        config=_config(),
    )

    assert len(result.rows) == 2
    assert [row.rank for row in result.rows] == [1, 2]
    scores = [row.selection_score for row in result.rows]
    assert scores == sorted(scores, reverse=True)
    for row in result.rows:
        assert row.validity_passed is True
        assert row.watchability.roster_key == "4p1i"
        assert row.referee_passed is False
        assert row.watchability.integrity_ok is True
        # referee fails on the fake provider, so the score is the bare geomean.
        assert row.selection_score == pytest.approx(row.watchability.mean_score)
        assert row.core_games_total == 2
        assert isinstance(row.core_impostor_win_rate, float)

    lines = ranking_path.read_text().splitlines()
    assert len(lines) == 2
    assert [json.loads(line)["rank"] for line in lines] == [1, 2]
    for line in lines:
        RealPathRerankRow.model_validate(json.loads(line))


# --------------------------------------------------------------------------- #
# 2. The stamp is read back FROM THE RECORDED BYTES.                          #
# --------------------------------------------------------------------------- #


def test_stamp_read_back_from_bytes(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(),
    )
    row = result.top()
    assert row.stamp.weights_sha256 == _UTIL_DIGEST
    assert row.stamp.encoder_version == _UTIL_ENCODER
    assert row.weights_sha256 == _UTIL_DIGEST
    assert row.stamp_verified_games == 2
    assert row.stamp_uniform is True
    assert row.stamp_equals_computed_digest is True

    # Independently prove the bytes carry the stamp (not an echo of the config).
    candidate_dir = work_dir / "000-utility-es"
    stamps = [
        read_tactical_policy_stamp(candidate_dir / f"replay-seed-{seed}.jsonl")
        for seed in (1, 2)
    ]
    assert all(stamp is not None for stamp in stamps)
    assert stamps[0] == stamps[1]
    assert stamps[0] is not None
    assert stamps[0].weights_sha256 == _UTIL_DIGEST


# --------------------------------------------------------------------------- #
# 3. The timeout proxy raises a distinct, retryable error (pure async unit).  #
# --------------------------------------------------------------------------- #


def test_timeout_proxy_raises_distinct_error() -> None:
    game_map = load_canonical_map()
    state = seed_state(game_map)
    trigger = MeetingTrigger(triggered_by="p-1", trigger_tick=1, description="probe")
    proxy = _TimeoutMeetingRunner(_HangRunner(), 0.2)

    async def _drive() -> MeetingArtifacts:
        return await proxy.run_meeting(
            meeting_id="m-1", trigger=trigger, state=state, agents={}
        )

    start = time.monotonic()
    with pytest.raises(RealPathMeetingTimeoutError) as excinfo:
        asyncio.run(_drive())
    assert time.monotonic() - start < 2.0
    assert isinstance(excinfo.value.__cause__, TimeoutError)


def seed_state(game_map: Map) -> WorldState:
    from orchestrator.seeder import seed_initial_state

    return seed_initial_state(seed=0, game_map=game_map, num_players=4)


# --------------------------------------------------------------------------- #
# 4. A hung meeting fails its seed loudly within the timeout.                 #
# --------------------------------------------------------------------------- #


def test_hung_meeting_fails_seed_loudly_within_timeout(tmp_path: Path) -> None:
    ranking_path = tmp_path / "ranking.jsonl"

    def hang_factory() -> MeetingRunner:
        return _HangRunner()

    start = time.monotonic()
    with pytest.raises(RealPathSeedExhaustedError) as excinfo:
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=tmp_path / "work",
            ranking_path=ranking_path,
            config=_config(meeting_timeout_seconds=0.3, max_attempts=1),
            meeting_runner_factory=hang_factory,
            meeting_runner_identity="hang-factory",
        )
    elapsed = time.monotonic() - start

    assert elapsed < 10.0
    assert isinstance(excinfo.value.__cause__, RealPathMeetingTimeoutError)
    message = str(excinfo.value)
    assert "utility-es" in message
    assert "seed 1" in message
    assert "1 attempts" in message
    # No partial committed artifact is left behind.
    assert not ranking_path.exists()


# --------------------------------------------------------------------------- #
# 5. The retry budget re-records a seed after a timeout.                      #
# --------------------------------------------------------------------------- #


def test_retry_budget_re_records_after_timeout(tmp_path: Path) -> None:
    calls = {"n": 0}

    def flaky_factory() -> MeetingRunner:
        calls["n"] += 1
        if calls["n"] == 1:
            return _HangRunner()
        return build_default_meeting_runner(budget=_resolve_game_budget(num_players=4))

    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=tmp_path / "work",
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(meeting_timeout_seconds=1.0, max_attempts=3),
        meeting_runner_factory=flaky_factory,
        meeting_runner_identity="flaky-factory",
    )

    (row,) = result.rows
    (telemetry,) = row.seed_telemetry
    assert telemetry.attempts == 2
    assert telemetry.timed_out_attempts == 1
    assert telemetry.degraded_recordings == 0
    assert telemetry.error_types == ("RealPathMeetingTimeoutError",)
    # The force=True re-record cleanly overwrote the partial replay.
    assert row.stamp_verified_games == 1
    assert row.stamp.weights_sha256 == _UTIL_DIGEST


# --------------------------------------------------------------------------- #
# 6. The ranking row + result round-trip through JSON.                        #
# --------------------------------------------------------------------------- #


def test_ranking_row_round_trip(tmp_path: Path) -> None:
    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=tmp_path / "work",
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(),
    )
    row = result.top()
    assert row.schema_version == SCHEMA_VERSION
    # The core None fields exist and survive (empty-denominator sentinels).
    assert row.core_ejection_accuracy is None
    assert row.core_genuine_class_conversion is None

    reloaded = RealPathRerankRow.model_validate(json.loads(row.to_json_line()))
    assert reloaded == row
    assert reloaded.core_ejection_accuracy is None

    result_json = json.dumps(result.model_dump(mode="json"))
    reloaded_result = RealPathRerankResult.model_validate(json.loads(result_json))
    assert reloaded_result == result


# --------------------------------------------------------------------------- #
# 7. The champion-trace helper de-dups by digest.                            #
# --------------------------------------------------------------------------- #


def test_champion_trace_helper_dedups(tmp_path: Path) -> None:
    util = _util_weights()
    perturbed = (util[0] + 1e-6,) + util[1:]
    es_result = ESResult(
        champion=perturbed,
        champion_fitness=0.0,
        fitness_trace=(0.0, 0.0, 0.0),
        generation_best=(0.0, 0.0),
        champion_trace=(util, util, perturbed),
        num_evaluations=0,
    )
    candidates = candidates_from_champion_trace(
        es_result,
        encoder_version=_UTIL_ENCODER,
        policy_id="utility-es",
        method="utility-scorer-es",
    )

    assert len(candidates) == 2
    assert [c.label for c in candidates] == ["gen000", "gen002"]
    assert candidates[0].generation_indices == (0, 1)
    assert candidates[1].generation_indices == (2,)
    assert candidates[0].genome == util
    from training.realpath import _genome_digest

    assert _genome_digest(candidates[0].genome) == _UTIL_DIGEST
    assert _genome_digest(candidates[0].genome) != _genome_digest(candidates[1].genome)

    # The champion-trace MODE lands in the rows and the result end to end.
    result = run_realpath_rerank(
        candidates,
        seeds=[1],
        work_dir=tmp_path / "work",
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(),
        mode=MODE_CHAMPION_TRACE,
    )
    assert result.mode == MODE_CHAMPION_TRACE
    assert all(row.mode == MODE_CHAMPION_TRACE for row in result.rows)


# --------------------------------------------------------------------------- #
# 8. Candidate + config validation fails loud.                               #
# --------------------------------------------------------------------------- #


def test_candidate_and_config_validation_fail_loud() -> None:
    genome = _util_weights()
    # v2 family without hidden.
    with pytest.raises(ValidationError):
        RealPathCandidate(
            label="p",
            genome=genome,
            encoder_version="v2",
            policy_id="p",
            method="m",
        )
    # Utility family WITH hidden.
    with pytest.raises(ValidationError):
        RealPathCandidate(
            label="u",
            genome=genome,
            encoder_version=_UTIL_ENCODER,
            hidden=8,
            policy_id="u",
            method="m",
        )
    # Blank label.
    with pytest.raises(ValidationError):
        RealPathCandidate(
            label="  ",
            genome=genome,
            encoder_version=_UTIL_ENCODER,
            policy_id="u",
            method="m",
        )
    # Pipe in policy_id (MANIFEST-unsafe).
    with pytest.raises(ValidationError):
        RealPathCandidate(
            label="u",
            genome=genome,
            encoder_version=_UTIL_ENCODER,
            policy_id="a|b",
            method="m",
        )
    # Empty genome.
    with pytest.raises(ValidationError):
        RealPathCandidate(
            label="u",
            genome=(),
            encoder_version=_UTIL_ENCODER,
            policy_id="u",
            method="m",
        )
    # Config: non-positive timeout.
    with pytest.raises(ValidationError):
        RealPathRerankConfig(meeting_timeout_seconds=0.0)
    # Config: max_attempts < 1.
    with pytest.raises(ValidationError):
        RealPathRerankConfig(max_attempts=0)


# --------------------------------------------------------------------------- #
# 9. run_realpath_rerank input validation fails loud before any recording.    #
# --------------------------------------------------------------------------- #


def test_run_input_validation_fails_loud(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    ranking_path = tmp_path / "ranking.jsonl"

    def _run(
        candidates: list[RealPathCandidate], *, seeds: list[int], mode: str
    ) -> None:
        run_realpath_rerank(
            candidates,
            seeds=seeds,
            work_dir=work_dir,
            ranking_path=ranking_path,
            config=_config(),
            mode=mode,
        )

    # Empty candidates.
    with pytest.raises(ValueError):
        _run([], seeds=[1], mode=MODE_TOP_K)
    # Empty seeds.
    with pytest.raises(ValueError):
        _run([_util_candidate()], seeds=[], mode=MODE_TOP_K)
    # Duplicate seeds.
    with pytest.raises(ValueError):
        _run([_util_candidate()], seeds=[1, 1], mode=MODE_TOP_K)
    # Duplicate labels.
    with pytest.raises(ValueError):
        _run(
            [_util_candidate("dup"), _pol_candidate("dup")],
            seeds=[1],
            mode=MODE_TOP_K,
        )
    # Unknown mode.
    with pytest.raises(ValueError):
        _run([_util_candidate()], seeds=[1], mode="bogus")

    # Nothing was recorded and no ranking file was written.
    assert list(work_dir.iterdir()) == []
    assert not ranking_path.exists()


# --------------------------------------------------------------------------- #
# 10. Ties break on candidate input order.                                    #
# --------------------------------------------------------------------------- #


def test_tie_break_is_candidate_input_order(tmp_path: Path) -> None:
    result = run_realpath_rerank(
        [_util_candidate("a"), _util_candidate("b")],
        seeds=[1],
        work_dir=tmp_path / "work",
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(),
    )
    assert result.rows[0].selection_score == pytest.approx(
        result.rows[1].selection_score
    )
    assert result.rows[0].label == "a"
    assert result.rows[0].rank == 1
    assert result.rows[1].label == "b"
    assert result.rows[1].rank == 2


# --------------------------------------------------------------------------- #
# 11. A tick-budget game is an accepted outcome, never retried.               #
# --------------------------------------------------------------------------- #


def test_tick_budget_seed_is_accepted_not_retried(tmp_path: Path) -> None:
    # On 4p1i with the utility-es candidate, seed 2 ends decisively at ~tick 11
    # and seed 1 at ~tick 22 (verified empirically), so max_ticks=15 caps seed 1
    # while seed 2 still lands a stamped game_over.
    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=tmp_path / "work",
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(max_ticks=15, max_attempts=3),
    )

    (row,) = result.rows
    capped, decisive = row.seed_telemetry
    assert capped.seed == 1
    assert capped.tick_budget_reached is True
    assert capped.attempts == 1  # the deterministic cap is never retried
    assert capped.degraded_recordings == 0
    assert decisive.seed == 2
    assert decisive.tick_budget_reached is False
    # Provenance is proven over the decisive seed only.
    assert row.stamp_verified_games == 1
    assert row.stamp.weights_sha256 == _UTIL_DIGEST


def test_all_tick_budget_seeds_fail_loud_without_retry(tmp_path: Path) -> None:
    # max_ticks=5 caps every seed before any decisive game_over exists, so no
    # bytes can prove provenance: RealPathStampError (NOT SeedExhausted — the
    # cap is an accepted outcome, not a retried degraded recording).
    with pytest.raises(RealPathStampError) as excinfo:
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=tmp_path / "work",
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(max_ticks=5, max_attempts=3),
        )
    assert "every seed hit the tick budget" in str(excinfo.value)


# --------------------------------------------------------------------------- #
# 12. Budget exhaustion is a metering stop, never retried.                    #
# --------------------------------------------------------------------------- #


def test_budget_exceeded_is_never_retried(tmp_path: Path) -> None:
    calls = {"n": 0}

    def budget_stop_factory() -> MeetingRunner:
        calls["n"] += 1
        return _BudgetStopRunner()

    with pytest.raises(BudgetExceededError):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=tmp_path / "work",
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(max_attempts=3),
            meeting_runner_factory=budget_stop_factory,
            meeting_runner_identity="budget-stop-factory",
        )
    # One attempt only: a metering stop propagates instead of re-spending.
    assert calls["n"] == 1


# --------------------------------------------------------------------------- #
# 13. Unknown floor blocks fail BEFORE any recording is made.                 #
# --------------------------------------------------------------------------- #


def test_unknown_baseline_or_roster_fails_before_recording(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    with pytest.raises(ValueError, match="no supply-floor block pinned"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(baseline_id="baseline-999"),
        )
    with pytest.raises(ValueError, match="no supply-floor .*block for roster"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(num_players=7, num_impostors=1),
        )
    # The preflight fired before any candidate dir or recording existed.
    assert not work_dir.exists()


# --------------------------------------------------------------------------- #
# 14. Encoder-family whitelist: v3 rebuilds; unknown families fail loud.       #
# --------------------------------------------------------------------------- #


def test_unsupported_encoder_version_fails_loud() -> None:
    with pytest.raises(ValidationError, match="unsupported encoder_version"):
        RealPathCandidate(
            label="future",
            genome=_util_weights(),
            encoder_version="v9",
            hidden=8,
            policy_id="p",
            method="m",
        )


def test_v3_candidate_validates_and_rebuilds() -> None:
    # The 18.22 encoder-v3 + per-target-head family is whitelisted and rebuilds
    # through build_masked_mlp_policy's encoder_version seam (the Codex PR #308
    # review gap: a v3 candidate previously rebuilt as v2 and rejected its own
    # wider genome). _build_agent_factory's internal post-check pins the rebuilt
    # policy's encoder identity against the declared one, so constructing the
    # factory IS the rebuild assertion.
    from agents.tactical.features import TacticalFeatureEncoderV3
    from training.bakeoff.policy_es import TARGET_KILL_SLOTS, policy_genome_length
    from orchestrator.boundary import public_map_from_engine_map

    game_map = load_canonical_map()
    genome_length = policy_genome_length(
        public_map_from_engine_map(game_map),
        hidden=8,
        encoder=TacticalFeatureEncoderV3(),
        target_slots=TARGET_KILL_SLOTS,
    )
    candidate = RealPathCandidate(
        label="policy-es-v3",
        genome=(0.0,) * genome_length,
        encoder_version="v3",
        hidden=8,
        policy_id="policy-es-v3",
        method="policy-net-es",
    )
    factory = _build_agent_factory(candidate, game_map=game_map)
    assert callable(factory)


# --------------------------------------------------------------------------- #
# 15. RESUME — the conjunctive predicate, pinned in BOTH directions (18.31).   #
# --------------------------------------------------------------------------- #


def _record_two_seeds(work_dir: Path, ranking_path: Path) -> RealPathRerankResult:
    """One completed leg over seeds 1 and 2 — the substrate every resume reads."""

    return run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=ranking_path,
        config=_config(),
    )


def test_resume_skips_only_verified_complete_elements(tmp_path: Path) -> None:
    """A resume skips the verified elements and re-records everything else.

    The 18.24 campaign lost 25 recorded games to a provider 503 at hour 40
    because a re-run re-records everything (report §11 defect 1). With
    ``resume=True`` a pre-existing (candidate, seed) whose replay carries the
    candidate's own read-back stamp AND passes the byte-completeness fence is
    skipped (``attempts=0``, ``resumed=True``); the row still proves provenance
    over the SAME bytes.
    """

    work_dir = tmp_path / "work"
    first = _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    assert [entry.resumed for entry in first.top().seed_telemetry] == [False, False]
    recorded = {
        seed: (work_dir / "000-utility-es" / f"replay-seed-{seed}.jsonl").read_bytes()
        for seed in (1, 2)
    }

    resumed = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    row = resumed.top()
    assert [entry.resumed for entry in row.seed_telemetry] == [True, True]
    assert [entry.attempts for entry in row.seed_telemetry] == [0, 0]
    assert [entry.error_types for entry in row.seed_telemetry] == [(), ()]
    # Nothing was re-recorded: the committed row stands on the ORIGINAL bytes.
    for seed, payload in recorded.items():
        assert (
            work_dir / "000-utility-es" / f"replay-seed-{seed}.jsonl"
        ).read_bytes() == payload
    assert row.stamp_verified_games == 2
    assert row.stamp.weights_sha256 == _UTIL_DIGEST


@pytest.mark.parametrize("miss", ["missing", "stamp-sha", "truncated", "trailing-rows"])
def test_resume_refuses_to_skip_on_any_verification_miss(
    tmp_path: Path, miss: str
) -> None:
    """ANY miss re-records — the predicate is conjunctive (18.31 fix 1).

    Four ways an element fails verification, one per case: the replay is gone;
    its read-back ``weights_sha256`` names a different genome (a foreign or
    superseded recording); its bytes are truncated before the ``game_over`` row;
    and — the case the first three do not reach — the stamp reads back
    correctly but the byte-completeness fence rejects rows recorded AFTER the
    terminal GAME_OVER tick. Each re-records seed 1 while seed 2 is still
    skipped, so the pin is "exactly the verified elements", not "all or none".
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    replay = work_dir / "000-utility-es" / "replay-seed-1.jsonl"

    if miss == "missing":
        replay.unlink()
    elif miss == "stamp-sha":
        replay.write_text(replay.read_text().replace(_UTIL_DIGEST, "0" * 64))
    elif miss == "truncated":
        lines = replay.read_text().splitlines()
        replay.write_text("\n".join(lines[:-1]) + "\n")
    else:
        rows = [json.loads(line) for line in replay.read_text().splitlines()]
        ticks = [row for row in rows if row["kind"] == "tick"]
        trailing = dict(ticks[-1])
        trailing["tick"] = max(row["tick"] for row in ticks) + 5
        # The stamp still reads back (the game_over row is untouched) — only the
        # dir-scoped completeness fence can catch this one.
        with replay.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(trailing) + "\n")
        assert read_tactical_policy_stamp(replay) is not None

    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    seed_one, seed_two = result.top().seed_telemetry
    assert seed_one.seed == 1
    assert seed_one.resumed is False
    assert seed_one.attempts == 1
    assert seed_two.seed == 2
    assert seed_two.resumed is True
    # The re-record repaired the element: the row proves both seeds again.
    assert result.top().stamp_verified_games == 2
    assert read_tactical_policy_stamp(replay) is not None

    # The leg log states WHY it re-recorded rather than skipping.
    events = [
        json.loads(line)
        for line in (work_dir / LEG_LOG_FILENAME).read_text().splitlines()
    ]
    rerecords = [event for event in events if event["event"] == "seed-rerecord"]
    assert [event["seed"] for event in rerecords] == [1]
    assert rerecords[0]["reason"]


def test_tick_budget_element_is_never_resumable(tmp_path: Path) -> None:
    """A ``TICK_BUDGET_REACHED`` replay re-records, deliberately (18.31).

    A capped game writes no ``game_over`` row by design, so it carries no stamp
    bytes: nothing on disk can prove which genome produced it. The predicate's
    second check therefore refuses it every time — the deliberate disposition
    the resume rule states rather than leaving anyone to re-derive.
    """

    # max_ticks=15 caps seed 1 and leaves seed 2 decisive (the 18.17 fixture).
    work_dir = tmp_path / "work"
    first = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(max_ticks=15, max_attempts=3),
    )
    capped, decisive = first.top().seed_telemetry
    assert capped.tick_budget_reached is True
    assert decisive.tick_budget_reached is False

    resumed = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(max_ticks=15, max_attempts=3),
        resume=True,
    )
    capped_again, decisive_again = resumed.top().seed_telemetry
    assert capped_again.resumed is False
    assert capped_again.attempts == 1
    assert capped_again.tick_budget_reached is True
    assert decisive_again.resumed is True


def test_resume_refuses_replays_outside_the_tranche(tmp_path: Path) -> None:
    """A foreign replay in the candidate dir is refused, never folded (18.31).

    The scoring gates fold the whole DIRECTORY, so a leftover replay from
    another tranche would silently enter this invocation's committed row.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    candidate_dir = work_dir / "000-utility-es"
    (candidate_dir / "replay-seed-99.jsonl").write_text(
        (candidate_dir / "replay-seed-1.jsonl").read_text()
    )

    with pytest.raises(RealPathRerankError, match="outside this tranche"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )


def test_without_resume_a_recorded_candidate_dir_still_fails_loud(
    tmp_path: Path,
) -> None:
    """The default keeps the write-once discipline exactly as before (18.31)."""

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    with pytest.raises(FileExistsError):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
        )


# --------------------------------------------------------------------------- #
# 16. Native pre-screen records + the append-only leg log (18.31 fix 3).       #
# --------------------------------------------------------------------------- #


def _quote(label: str = "utility-es") -> PreScreenQuote:
    return PreScreenQuote(
        label=label,
        weights_sha256=_UTIL_DIGEST,
        predicted_flags_per_meeting=1.6109,
        predicted_floors_pass=True,
        generation=3,
        meetings_scored=20,
        conviction_uses=20,
        recorded_flags_fake_substrate=0.0,
    )


def test_prescreen_records_are_tranche_and_invocation_keyed(tmp_path: Path) -> None:
    """A second tranche (or re-run) never overwrites the first's record (18.31).

    Report §11 defect 3 / F9: the 18.24 pre-screen record was written IN PLACE,
    so tranche 2 overwrote tranche 1 and the provenance had to be reconstructed
    under review. The writer now allocates by exclusive creation.
    """

    first = write_prescreen_record(
        tmp_path, seeds=[4000, 4001, 4002], quotes=[_quote()]
    )
    assert first.name == "prescreen-quotes-4000-4002-000.json"
    second = write_prescreen_record(
        tmp_path, seeds=[4000, 4001, 4002], quotes=[_quote()]
    )
    assert second.name == "prescreen-quotes-4000-4002-001.json"
    other_tranche = write_prescreen_record(
        tmp_path, seeds=[4003, 4004, 4005], quotes=[_quote()]
    )
    assert other_tranche.name == "prescreen-quotes-4003-4005-000.json"
    assert first.read_bytes() != b""

    record = PreScreenRecord.model_validate(json.loads(first.read_text()))
    assert record.schema_version == PRESCREEN_SCHEMA_VERSION
    assert record.tranche == "4000-4002"
    assert record.invocation == "000"
    assert record.seeds == (4000, 4001, 4002)
    assert record.quotes[0].note == PRESCREEN_ADVICE_NOTE
    assert record.quotes[0].predicted_floors_pass is True

    # An explicit invocation writes exactly that file and never clobbers.
    explicit = write_prescreen_record(
        tmp_path, seeds=[4000, 4001, 4002], quotes=[_quote()], invocation="zzz"
    )
    assert explicit.name == "prescreen-quotes-4000-4002-zzz.json"
    with pytest.raises(FileExistsError):
        write_prescreen_record(
            tmp_path, seeds=[4000, 4001, 4002], quotes=[_quote()], invocation="zzz"
        )


def test_a_failed_prescreen_write_publishes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An interrupted pre-screen write leaves no half-record (Codex on PR #314).

    An exclusive ``open("x")`` CREATES the final path before the payload is
    complete, so a disk-full or a kill mid-``write`` leaves a truncated file
    that reads as committed invocation evidence — and the retry, seeing the
    ordinal taken, advances past it and strands the corrupt record in the audit
    set permanently. Staged-then-linked, the ordinal is either absent or a whole
    record, so the retry reclaims the SAME ordinal.
    """

    real_fsync = os.fsync

    def _explode(fd: int) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(os, "fsync", _explode)
    with pytest.raises(OSError, match="disk full"):
        write_prescreen_record(tmp_path, seeds=[4000, 4001, 4002], quotes=[_quote()])
    monkeypatch.setattr(os, "fsync", real_fsync)

    # Neither a partial record nor a leaked staging file survives.
    assert list(tmp_path.iterdir()) == []

    # The retry reclaims ordinal 000 rather than skipping past a corpse.
    retried = write_prescreen_record(
        tmp_path, seeds=[4000, 4001, 4002], quotes=[_quote()]
    )
    assert retried.name == "prescreen-quotes-4000-4002-000.json"
    assert PreScreenRecord.model_validate(
        json.loads(retried.read_text())
    ).invocation == ("000")


def test_prescreen_quote_validation_fails_loud() -> None:
    with pytest.raises(ValidationError):
        PreScreenQuote(
            label="  ",
            weights_sha256=_UTIL_DIGEST,
            predicted_flags_per_meeting=1.0,
            predicted_floors_pass=True,
        )
    with pytest.raises(ValidationError):
        PreScreenQuote(
            label="u",
            weights_sha256="not-a-sha",
            predicted_flags_per_meeting=1.0,
            predicted_floors_pass=True,
        )
    with pytest.raises(ValidationError):
        PreScreenQuote(
            label="u",
            weights_sha256=_UTIL_DIGEST,
            predicted_flags_per_meeting=float("nan"),
            predicted_floors_pass=True,
        )
    with pytest.raises(ValidationError):
        PreScreenRecord(
            tranche="1", invocation="000", seeds=(1,), recorded_at="now", quotes=()
        )


def test_leg_log_is_native_append_only_and_orders_prescreen_before_spend(
    tmp_path: Path,
) -> None:
    """The library writes its own ordering evidence (18.31 fix 3 / §12 item 10).

    Session 5 of the 18.24 campaign recorded 36 real games with NO chain log, so
    "pre-screen quoted before any spend" rested on operator testimony. The leg
    now stamps an invocation manifest and appends every event itself: the
    pre-screen events precede the first ``seed-recorded`` event, sequence
    numbers are monotone per invocation, and a second invocation APPENDS to the
    same log under its own invocation key.
    """

    work_dir = tmp_path / "work"
    run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
        prescreen=[_quote()],
    )
    log_path = work_dir / LEG_LOG_FILENAME
    events = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert all(event["tranche"] == "1-2" for event in events)
    assert all(event["invocation"] == "000" for event in events)
    assert [event["seq"] for event in events] == list(range(1, len(events) + 1))
    kinds = [event["event"] for event in events]
    assert kinds[0] == "leg-start"
    assert kinds[-1] == "leg-done"
    assert kinds.index("prescreen-quote") < kinds.index("seed-recorded")
    assert kinds.index("prescreen-record") < kinds.index("seed-recorded")
    assert "rank" in kinds

    # The invocation manifest carries the seeds/candidates/knobs and the stamp.
    manifest = json.loads((work_dir / "leg-1-2-000.json").read_text())
    assert manifest["seeds"] == [1, 2]
    assert manifest["tranche"] == "1-2"
    assert manifest["invocation"] == "000"
    assert manifest["resume"] is False
    assert manifest["candidates"][0]["weights_sha256"] == _UTIL_DIGEST
    assert manifest["started_at"]

    # A second invocation appends under a fresh key; the first's bytes survive.
    before = log_path.read_text()
    run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    after = log_path.read_text()
    assert after.startswith(before)
    second_events = [json.loads(line) for line in after[len(before) :].splitlines()]
    assert {event["invocation"] for event in second_events} == {"001"}
    assert (work_dir / "leg-1-2-001.json").exists()


def test_leg_log_records_a_failed_leg(tmp_path: Path) -> None:
    """A leg that dies mid-recording leaves its own record on disk (18.31)."""

    def hang_factory() -> MeetingRunner:
        return _HangRunner()

    work_dir = tmp_path / "work"
    with pytest.raises(RealPathSeedExhaustedError):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(meeting_timeout_seconds=0.3, max_attempts=1),
            meeting_runner_factory=hang_factory,
            meeting_runner_identity="hang-factory",
        )
    events = [
        json.loads(line)
        for line in (work_dir / LEG_LOG_FILENAME).read_text().splitlines()
    ]
    failure = events[-1]
    assert failure["event"] == "leg-failed"
    assert failure["error"] == "RealPathSeedExhaustedError"
    assert "seed 1" in failure["message"]


def test_leg_log_refuses_a_reserved_field() -> None:
    """The log owns its ordering keys; a caller field shadowing one fails loud."""

    log = RealPathLegLog(Path("unused.jsonl"), tranche="1-2", invocation="000")
    with pytest.raises(ValueError, match="reserved keys"):
        log.emit("probe", seq=7)


def test_tranche_key_matches_the_committed_artifact_names() -> None:
    assert tranche_key([4000, 4001, 4002]) == "4000-4002"
    assert tranche_key([4003]) == "4003"
    with pytest.raises(ValueError, match="no seeds"):
        tranche_key([])


# --------------------------------------------------------------------------- #
# 17. Review follow-ups (Codex on PR #314).                                    #
# --------------------------------------------------------------------------- #


def test_resume_re_records_an_unreadable_replay(tmp_path: Path) -> None:
    """A half-written replay is a resume MISS, not a leg-killing exception.

    An interrupted process leaves a partial line, and the committed reader
    RAISES on it (``ValueError: invalid replay JSON at line N``) rather than
    returning ``None``. That is precisely the state a resume exists to meet, so
    the predicate must catch it and re-record — an exception here would abort
    the leg the resume was supposed to rescue.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    replay = work_dir / "000-utility-es" / "replay-seed-1.jsonl"
    # A truncated final line: valid rows, then a partial one (the classic
    # interrupted-write signature).
    with replay.open("a", encoding="utf-8") as handle:
        handle.write('{"kind": "tic')
    with pytest.raises(ValueError, match="invalid replay JSON"):
        read_tactical_policy_stamp(replay)

    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    seed_one, seed_two = result.top().seed_telemetry
    assert seed_one.resumed is False
    assert seed_one.attempts == 1
    assert seed_two.resumed is True
    assert result.top().stamp_verified_games == 2
    events = [
        json.loads(line)
        for line in (work_dir / LEG_LOG_FILENAME).read_text().splitlines()
    ]
    reasons = [event["reason"] for event in events if event["event"] == "seed-rerecord"]
    assert len(reasons) == 1
    assert "unreadable" in reasons[0]


def test_prescreen_must_cover_this_legs_candidates(tmp_path: Path) -> None:
    """Quotes that do not name THIS leg's candidates are refused (18.31).

    Ordering evidence naming the wrong candidates is worse than none: it reads
    as proof that the recorded candidates were pre-screened when they were not.
    Coverage is checked on the genome digest, and a quote whose label matches a
    candidate must carry that candidate's digest.
    """

    def _run(quotes: list[PreScreenQuote], work: str) -> None:
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=tmp_path / work,
            ranking_path=tmp_path / f"{work}.jsonl",
            config=_config(),
            prescreen=quotes,
        )

    # A quote for a DIFFERENT genome (the policy-es digest): no coverage.
    foreign = PreScreenQuote(
        label="policy-es",
        weights_sha256=_genome_digest(_pol_weights()),
        predicted_flags_per_meeting=1.0,
        predicted_floors_pass=True,
    )
    with pytest.raises(ValueError, match="cover exactly this leg's candidates"):
        _run([foreign], "a")

    # THIS leg's label paired with another genome's digest: mispaired, not cover.
    mispaired = PreScreenQuote(
        label="utility-es",
        weights_sha256=_genome_digest(_pol_weights()),
        predicted_flags_per_meeting=1.0,
        predicted_floors_pass=True,
    )
    with pytest.raises(ValueError, match="cover exactly this leg's candidates"):
        _run([mispaired], "b")

    # An extra quote beside a correct one is still not exact coverage.
    with pytest.raises(ValueError, match="cover exactly this leg's candidates"):
        _run([_quote(), foreign], "c")

    # No recording, no record, and no ordering evidence was written for any of
    # them — the refusal precedes the log.
    for work in ("a", "b", "c"):
        assert not (tmp_path / work / "prescreen-quotes-1-000.json").exists()
        events = [
            json.loads(line)
            for line in (tmp_path / work / LEG_LOG_FILENAME).read_text().splitlines()
        ]
        assert [event["event"] for event in events] == ["leg-start", "leg-failed"]
        assert not (tmp_path / work / "000-utility-es").exists()

    # The matching quote set is accepted.
    _run([_quote()], "ok")
    assert (tmp_path / "ok" / "prescreen-quotes-1-000.json").exists()


def test_a_committed_ranking_is_never_rewritten(tmp_path: Path) -> None:
    """A recorded leg's ranking is write-once, even under resume (Codex #314).

    Before the resume path existed, a re-run died at the candidate-dir mkdir
    long before the ranking write. ``resume=True`` makes a completed leg
    re-runnable, so a plain write would REPLACE the committed rows with ones
    whose telemetry says the games were skipped rather than played — mutating
    the campaign's recorded truth instead of completing it.
    """

    work_dir = tmp_path / "work"
    ranking = tmp_path / "ranking.jsonl"
    _record_two_seeds(work_dir, ranking)
    original = ranking.read_bytes()

    with pytest.raises(RealPathRerankError, match="already exists"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=ranking,
            config=_config(),
            resume=True,
        )
    assert ranking.read_bytes() == original

    # A resume into a FRESH ranking path is the legitimate flow and still works.
    resumed = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-resumed.jsonl",
        config=_config(),
        resume=True,
    )
    assert all(entry.resumed for entry in resumed.top().seed_telemetry)


def test_prescreen_note_is_the_committed_disclaimer(tmp_path: Path) -> None:
    """``note`` is the record's blocker-4 guarantee, not caller caption text.

    A quote whose note described the prediction as gating evidence would invert
    blocker 4 inside the committed artifact (Codex on PR #314).
    """

    with pytest.raises(ValidationError, match="spend advice by contract"):
        PreScreenQuote(
            label="utility-es",
            weights_sha256=_UTIL_DIGEST,
            predicted_flags_per_meeting=1.0,
            predicted_floors_pass=True,
            note="gating read",
        )
    with pytest.raises(ValidationError, match="spend advice by contract"):
        PreScreenQuote(
            label="utility-es",
            weights_sha256=_UTIL_DIGEST,
            predicted_flags_per_meeting=1.0,
            predicted_floors_pass=True,
            note="",
        )
    # The default is the committed disclaimer, and it round-trips.
    path = write_prescreen_record(tmp_path, seeds=[1], quotes=[_quote()])
    assert json.loads(path.read_text())["quotes"][0]["note"] == PRESCREEN_ADVICE_NOTE


def test_existing_ranking_is_refused_before_any_game(tmp_path: Path) -> None:
    """The ranking-path collision is caught in the PREFLIGHT, not after spend.

    The exclusive open at the end is race protection; on its own it would let a
    simple operator path typo burn a 30–40 h leg before failing (Codex on
    PR #314). Both checks stand — this one saves the budget.
    """

    work_dir = tmp_path / "work"
    ranking = tmp_path / "ranking.jsonl"
    ranking.write_text("{}\n")

    with pytest.raises(RealPathRerankError, match="before any game is spent"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=ranking,
            config=_config(),
        )
    # Nothing was recorded, and the leg never even opened its invocation stamp.
    assert not work_dir.exists()
    assert ranking.read_text() == "{}\n"


def test_prescreen_coverage_is_by_candidate_identity_not_digest_set(
    tmp_path: Path,
) -> None:
    """Two labels over ONE genome need two quotes (Codex on PR #314).

    A leg may legitimately carry the same policy under two labels — the 18.17
    tie-break fixture does exactly that. Comparing digest SETS let a single
    quote cover both, leaving a candidate that consumed real games unnamed in
    the ordering evidence.
    """

    candidates = [_util_candidate("arm-a"), _util_candidate("arm-b")]
    with pytest.raises(ValueError, match="missing \\['arm-b'\\]"):
        run_realpath_rerank(
            candidates,
            seeds=[1],
            work_dir=tmp_path / "one",
            ranking_path=tmp_path / "one.jsonl",
            config=_config(),
            prescreen=[_quote("arm-a")],
        )

    # Naming both is coverage, even though they share a genome digest.
    result = run_realpath_rerank(
        candidates,
        seeds=[1],
        work_dir=tmp_path / "two",
        ranking_path=tmp_path / "two.jsonl",
        config=_config(),
        prescreen=[_quote("arm-a"), _quote("arm-b")],
    )
    assert {row.label for row in result.rows} == {"arm-a", "arm-b"}


def test_a_partially_written_ranking_does_not_block_a_resume(tmp_path: Path) -> None:
    """A ranking is published ATOMICALLY, so an interrupt leaves no half-file.

    Round 2 made the ranking write exclusive and round 3 rejected an existing
    one in the preflight — which together made a NEW state reachable: a crash
    between ``open("x")`` creating the file and the write completing left an
    empty or partial ranking that the preflight then read as committed truth,
    refusing a resume whose verified replays were still on disk (Codex on
    PR #314). Publishing through a staged file + ``os.link`` means the path
    either does not exist or holds every row.
    """

    work_dir = tmp_path / "work"
    ranking = tmp_path / "ranking-1.jsonl"
    _record_two_seeds(work_dir, ranking)
    complete = ranking.read_text(encoding="utf-8")

    # No stage file survives a successful publish.
    assert sorted(p.name for p in tmp_path.iterdir() if p.is_file()) == [ranking.name]

    # The failure the atomic publish exists to prevent: a zero-byte create.
    truncated = tmp_path / "ranking-truncated.jsonl"
    truncated.write_text("", encoding="utf-8")
    assert truncated.read_text(encoding="utf-8") != complete
    with pytest.raises(RealPathRerankError, match="already exists"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=tmp_path / "work-2",
            ranking_path=truncated,
            config=_config(),
        )


def test_ranking_publish_is_atomic_and_still_write_once(tmp_path: Path) -> None:
    """The staged publish keeps write-once semantics: an existing file is never clobbered."""

    from training.realpath import _publish_ranking

    target = tmp_path / "ranking.jsonl"
    _publish_ranking(target, '{"rank": 1}\n')
    assert target.read_text(encoding="utf-8") == '{"rank": 1}\n'
    with pytest.raises(RealPathRerankError, match="already exists"):
        _publish_ranking(target, '{"rank": 2}\n')
    # The committed bytes are untouched, and no stage file is left behind.
    assert target.read_text(encoding="utf-8") == '{"rank": 1}\n'
    assert [p.name for p in tmp_path.iterdir()] == [target.name]


def test_resume_ignores_audit_sidecars_left_by_an_interrupted_leg(
    tmp_path: Path,
) -> None:
    """The ordinary interruption state must not read as a foreign tranche.

    ``HeadlessGame`` writes ``replay-seed-N.audit.jsonl`` beside every replay,
    and ``_drop_audit_sidecars`` only runs AFTER a candidate's whole seed loop —
    so an interrupted leg still holds them. They MATCH the
    ``replay-seed-*.jsonl`` glob and ``_replay_seed`` cannot parse ``N.audit``,
    which made the foreign-replay guard abort every resume it was meant to
    serve (Codex on PR #314). My earlier fixtures resumed from a COMPLETED leg,
    which has no sidecars, so none of them reached this.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    candidate_dir = work_dir / "000-utility-es"
    # Exactly what an interruption leaves behind.
    for seed in (1, 2):
        (candidate_dir / f"replay-seed-{seed}.audit.jsonl").write_text(
            '{"kind": "audit"}\n', encoding="utf-8"
        )
    assert len(list(candidate_dir.glob("replay-seed-*.jsonl"))) == 4

    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    assert [entry.resumed for entry in result.top().seed_telemetry] == [True, True]


def test_resume_refuses_a_replay_whose_policy_identity_differs(
    tmp_path: Path,
) -> None:
    """The resume predicate compares the WHOLE stamp, not the genome digest.

    Identical genome bytes under a different ``policy_id`` / ``method`` /
    ``anchor_policy`` / ``encoder_version`` are a DIFFERENT policy. Comparing
    only ``weights_sha256`` would adopt the previous identity's games and
    attribute them to this candidate — and ``_verify_stamps`` cannot catch it,
    since the digest matches and the stamps stay uniform across seeds (Codex on
    PR #314).
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")

    # Resume into the SAME work dir: the recorded replays must actually be on
    # disk for the predicate to inspect, or this test passes with the whole
    # comparison deleted (my first version resumed into a fresh dir, where every
    # seed re-records because there is nothing there — Codex on PR #314).
    candidate_dir = work_dir / "000-utility-es"
    assert sorted(p.name for p in candidate_dir.glob("replay-seed-*.jsonl")) == [
        "replay-seed-1.jsonl",
        "replay-seed-2.jsonl",
    ]

    # Same genome, same digest, same label, different declared identity.
    renamed = _util_candidate().model_copy(update={"policy_id": "some-other-policy-id"})
    result = run_realpath_rerank(
        [renamed],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    # Nothing was skipped: the bytes belong to another policy identity.
    assert [entry.resumed for entry in result.top().seed_telemetry] == [False, False]


def test_resume_refuses_a_changed_recording_protocol(tmp_path: Path) -> None:
    """A resume adopts bytes recorded under the PRIOR protocol (Codex on PR #314).

    Every invocation stamps its full config into a leg manifest, but nothing
    compared them: resuming with a changed roster / baseline / tick budget /
    timeout / retry budget skipped the old recordings while ``_build_row``
    reported the NEW settings as though they produced those bytes.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")

    with pytest.raises(RealPathRerankError, match="different protocol"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(max_ticks=777),
            resume=True,
        )

    # The unchanged protocol still resumes.
    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-3.jsonl",
        config=_config(),
        resume=True,
    )
    assert [entry.resumed for entry in result.top().seed_telemetry] == [True, True]


def test_resume_refuses_a_label_whose_genome_moved(tmp_path: Path) -> None:
    """A label is not an identity: reusing one over a new genome is refused."""

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    moved = _util_candidate().model_copy(
        update={"genome": tuple(g + 1.0 for g in _util_weights())}
    )
    with pytest.raises(RealPathRerankError, match="different genome digest"):
        run_realpath_rerank(
            [moved],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )


def test_a_cleanup_failure_never_overturns_a_committed_publish(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Once ``os.link`` succeeds the ranking is committed (Codex on PR #314).

    A raising ``unlink`` in the ``finally`` used to propagate after a successful
    publish, so the caller emitted ``leg-failed``, dropped its rank events, and
    every retry then bounced off the ranking it had actually written.
    """

    from training.realpath import _publish_ranking

    target = tmp_path / "ranking.jsonl"
    original = Path.unlink

    def _explode(self: Path, *args: object, **kwargs: object) -> None:
        if self.name.endswith(".tmp"):
            raise OSError("cleanup denied")
        original(self, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(Path, "unlink", _explode)
    _publish_ranking(target, '{"rank": 1}\n')
    assert target.read_text(encoding="utf-8") == '{"rank": 1}\n'


def test_an_unpublishable_ranking_filesystem_is_refused_before_any_game(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hard-link capability is preflighted, not discovered after the spend.

    ``os.link`` is the publish primitive; on a filesystem that cannot do it
    (exFAT, some FUSE/network mounts) the leg would fail only after every paid
    game, and a resume would hit the same wall forever (Codex on PR #314).
    """

    import os

    def _no_links(src: object, dst: object) -> None:
        raise OSError("link(2) not supported")

    monkeypatch.setattr(os, "link", _no_links)
    with pytest.raises(RealPathRerankError, match="cannot publish hard links"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=tmp_path / "work",
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(),
        )
    # Refused in the preflight: no work dir, no games.
    assert not (tmp_path / "work").exists()


def test_resume_finds_recordings_after_the_slate_narrows(tmp_path: Path) -> None:
    """A NARROWED slate must still find each label's original directory.

    ``_refuse_protocol_drift`` deliberately permits narrowing — re-running the
    candidates a 503 interrupted is the normal resume. But directories were
    named from ``enumerate(candidates)``, so narrowing ``[A, B]`` to ``[B]``
    renumbered ``001-b`` to ``000-b``: the resume looked straight past every
    verified recording it exists to reuse and re-recorded the whole leg (Codex
    on PR #314). Dirs are now resolved by LABEL under resume.
    """

    work_dir = tmp_path / "work"
    first = run_realpath_rerank(
        [_util_candidate("arm-a"), _util_candidate("arm-b")],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
    )
    assert first.rows
    assert (work_dir / "000-arm-a").is_dir()
    assert (work_dir / "001-arm-b").is_dir()

    # Narrow to the SECOND candidate only; index 0 now, dir still 001-arm-b.
    result = run_realpath_rerank(
        [_util_candidate("arm-b")],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    assert [entry.resumed for entry in result.top().seed_telemetry] == [True]
    # No renumbered duplicate was created.
    assert not (work_dir / "000-arm-b").exists()


@pytest.mark.parametrize(
    "knob",
    ["AILIBI_LLM_PROVIDER", "AILIBI_PROMPT_SET"],
)
def test_resume_refuses_a_changed_recording_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, knob: str
) -> None:
    """The RECORDER is part of the protocol (Codex on PR #314).

    ``RealPathRerankConfig`` describes the game, not the backend, so a provider
    or prompt-set swap left ``wanted_config`` identical: existing seeds were
    skipped while missing ones recorded through the new recorder, committing ONE
    row whose seeds came from two different backends. Both knobs here are read
    on EVERY provider, so both are refused end to end — and the refusal lands
    before a single game is recorded, which is why a provider this environment
    cannot even construct still exercises the guard.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")

    monkeypatch.setenv(
        knob, "anthropic" if knob == "AILIBI_LLM_PROVIDER" else "qwen3_32b"
    )
    with pytest.raises(RealPathRerankError, match="different recording backend"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )


def test_one_leg_at_a_time_per_work_dir_tranche(tmp_path: Path) -> None:
    """Concurrent legs on one tranche are serialized, not interleaved (Codex #314).

    Two resumes entering one tranche both finish ``_refuse_protocol_drift``
    before either manifest exists, so the exclusive manifest publish merely
    hands them different ordinals and neither validates the other's protocol.
    They then record into the SAME candidate directories — potentially under
    different configs or backends — and score each other's half-written
    replays. Serialising the claim makes read-then-publish atomic, so the loser
    is refused instead of racing.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    claim = work_dir / f"{realpath.TRANCHE_CLAIM_FILENAME_STEM}-1-2.lock"
    assert claim.exists()

    # Stand in for the concurrent leg by holding its claim.
    fd = os.open(claim, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(RealPathRerankError, match="already holds tranche"):
            run_realpath_rerank(
                [_util_candidate()],
                seeds=[1, 2],
                work_dir=work_dir,
                ranking_path=tmp_path / "ranking-2.jsonl",
                config=_config(),
                resume=True,
            )
    finally:
        os.close(fd)

    # A DIFFERENT tranche in the same work dir is an independent leg: the claim
    # is per (work dir, tranche), never a work-dir-wide mutex.
    fd = os.open(claim, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with realpath._tranche_claim(work_dir, tranche="7"):
            pass
        with pytest.raises(RealPathRerankError, match="already holds tranche"):
            with realpath._tranche_claim(work_dir, tranche="1-2"):
                pass
    finally:
        os.close(fd)

    # Released on the way out, so the next resume of the SAME tranche proceeds.
    assert run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-4.jsonl",
        config=_config(),
        resume=True,
    ).rows


def test_a_failed_leg_releases_its_tranche_claim(tmp_path: Path) -> None:
    """A crashed leg must not leave the tranche permanently unclaimable (#314).

    An exclusive-create lock FILE would have to be deleted to release, so the
    hour-40 provider 503 this task exists to survive would strand every future
    resume behind a claim only a human could clear — the same permanently
    unresumable deadlock the round-8 runner-identity refusal created. The claim
    is a ``flock``, which the kernel drops on close and on process death.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")

    # A leg that dies mid-flight: the protocol-drift refusal fires INSIDE the
    # claim, which is exactly where a stale lock would be left behind.
    with pytest.raises(RealPathRerankError, match="different"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(tasks_per_crewmate=3),
            resume=True,
        )

    # The tranche is claimable again, with no file to delete by hand.
    assert run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-3.jsonl",
        config=_config(),
        resume=True,
    ).rows


def test_the_prompt_variant_lever_rides_the_backend_identity() -> None:
    """The prompt SET name does not determine the rendered bytes (Codex #314).

    The 18.10 impostor-answer lever (``AILIBI_IMPOSTOR_ROLL_CALL``) swaps the
    impostor-report and accusation-round templates WITHIN a set, and
    ``prompt_versions_for_set`` stamps the variant versions. A leg resumed after
    the lever flipped would skip seeds recorded under one template family and
    record the rest under another, publishing one backend digest over two prompt
    protocols.
    """

    game_map = load_canonical_map()

    def _identity(**env: str) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=False, game_map=game_map, num_players=4, environment=env
        )

    # The lever genuinely changes the RECORDED prompt versions on a
    # variant-capable set — the fact that makes it protocol, asserted here
    # rather than assumed, so this pin fails if the registry stops varying.
    off = dict(prompt_versions_for_set(env={"AILIBI_PROMPT_SET": "qwen3_6_27b"}))
    on = dict(
        prompt_versions_for_set(
            env={"AILIBI_PROMPT_SET": "qwen3_6_27b", "AILIBI_IMPOSTOR_ROLL_CALL": "1"}
        )
    )
    assert off != on
    assert off["impostor_report"] != on["impostor_report"]

    assert _identity(
        AILIBI_PROMPT_SET="qwen3_6_27b", AILIBI_IMPOSTOR_ROLL_CALL="1"
    ) != _identity(AILIBI_PROMPT_SET="qwen3_6_27b")
    # It rides EVERY provider, like the prompt set itself. Pinned on the
    # variant-capable set: since the identity now carries the RESOLVED prompt
    # versions, turning the lever on for a set with no variant registry is a
    # config error that fails loud here — the same refusal the runner would
    # give — rather than a boolean nobody can act on (Codex on PR #314).
    for provider in ("fake", "ollama", "featherless", "anthropic"):
        assert _identity(
            AILIBI_LLM_PROVIDER=provider,
            AILIBI_PROMPT_SET="qwen3_6_27b",
            AILIBI_IMPOSTOR_ROLL_CALL="1",
        ) != _identity(AILIBI_LLM_PROVIDER=provider, AILIBI_PROMPT_SET="qwen3_6_27b")
    # And the lever on a set with NO variant registry is refused, not recorded.
    with pytest.raises(ValueError, match="impostor-answer variant registry"):
        _identity(AILIBI_PROMPT_SET="qwen3_5_9b", AILIBI_IMPOSTOR_ROLL_CALL="1")


def test_concurrent_tranches_never_share_a_candidate_directory(
    tmp_path: Path,
) -> None:
    """Directory allocation is serialized ACROSS tranches (Codex on PR #314).

    The round-9 tranche claim is per ``(work dir, tranche)`` — correct for
    recording, since two tranches are independent experiments — but they
    allocate out of ONE namespace. Two resuming legs on different tranches held
    different claims, both saw ``000-<slug>`` free, and both took it; the
    recording loop's ``mkdir(exist_ok=True)`` then let both write different seed
    sets into one directory, which the scoring functions fold whole.

    Allocation now happens under a work-dir-wide claim AND creates the
    directories inside it, so the reservation is visible to the next allocator.
    """

    work_dir = tmp_path / "work"
    candidate = _util_candidate()

    # The INTERLEAVING the lock exists to prevent, reproduced deterministically:
    # tranche A resolves, and tranche B resolves before A has recorded anything.
    # Running the two legs end-to-end in sequence would NOT exercise this — A's
    # directory is already on disk by then, so B skips it whether or not the fix
    # is present. (That sequential version passed with the fix reverted, which
    # is why it is not the pin.)
    first = realpath._allocate_candidate_dirs(
        work_dir,
        tranche="1-2",
        candidates=[candidate],
        resume=True,
        publish=lambda dirs: None,
    )
    second = realpath._allocate_candidate_dirs(
        work_dir,
        tranche="7-8",
        candidates=[candidate],
        resume=True,
        publish=lambda dirs: None,
    )

    assert first[0] != second[0], (
        "two tranches were handed the same candidate directory; under resume "
        "both would mkdir(exist_ok=True) into it and interleave their seeds"
    )
    assert first[0].name == "000-utility-es"
    assert second[0].name == "001-utility-es"

    # And end to end in a clean work dir, each tranche's directory holds ONLY
    # its own seeds — the contamination this finding describes would surface
    # here as the other tranche's replays.
    live = tmp_path / "live"
    _record_two_seeds(live, tmp_path / "ranking-1.jsonl")
    assert run_realpath_rerank(
        [candidate],
        seeds=[7, 8],
        work_dir=live,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    ).rows

    def _seeds(directory: Path) -> set[int]:
        return {
            int(path.name.removeprefix("replay-seed-").removesuffix(".jsonl"))
            for path in directory.glob("replay-seed-*.jsonl")
            if not path.name.endswith(_AUDIT_SUFFIX)
        }

    assert _seeds(live / "000-utility-es") == {1, 2}
    assert _seeds(live / "001-utility-es") == {7, 8}


def test_a_fresh_leg_steps_aside_from_another_tranches_claim(tmp_path: Path) -> None:
    """A NON-resume leg reserves through its manifest (Codex on PR #314).

    Round 10 scoped the reservation to resume, reasoning that a fresh collision
    is "a loud FileExistsError rather than contamination". That was wrong about
    the ORDERING: the manifest is published before the recording loop, so the
    loser had already committed a manifest naming the shared directory — and
    every later resume of that tranche then resolved back to it and rejected the
    winner's replays as foreign, unrecoverable without hand-editing the
    manifest.

    The manifest is now published under the allocation claim, and a fresh leg
    steps aside from a directory another tranche's manifest owns.
    """

    work_dir = tmp_path / "work"
    candidate = _util_candidate()

    # Tranche 1-2 records; its manifest claims 000-utility-es.
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    assert (work_dir / "000-utility-es").is_dir()

    # A FRESH leg on another tranche must not be handed that directory.
    fresh = realpath._allocate_candidate_dirs(
        work_dir,
        tranche="7-8",
        candidates=[candidate],
        resume=False,
        publish=lambda dirs: None,
    )
    assert fresh[0].name == "001-utility-es"

    # And end to end it records into its own directory and resumes cleanly —
    # the recovery the shared-directory manifest denied.
    assert run_realpath_rerank(
        [candidate],
        seeds=[7, 8],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
    ).rows
    resumed = run_realpath_rerank(
        [candidate],
        seeds=[7, 8],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-3.jsonl",
        config=_config(),
        resume=True,
    )
    assert [entry.resumed for entry in resumed.top().seed_telemetry] == [True, True]

    # The write-once rule is UNTOUCHED: a fresh leg on a tranche that already
    # owns its directory still refuses rather than quietly picking a new name.
    with pytest.raises(FileExistsError):
        run_realpath_rerank(
            [candidate],
            seeds=[7, 8],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-4.jsonl",
            config=_config(),
        )


def test_resume_refuses_a_mode_change(tmp_path: Path) -> None:
    """The MODE is leg protocol, and the drift check was blind to it (#314).

    ``generate_campaign_tables`` treats ``mode`` as a leg-protocol field and
    refuses two tranches of an arm that disagree on it — but ``mode`` is not a
    ``RealPathRerankConfig`` field, so the config comparison never saw it. A
    ``top-k`` recording resumed as ``champion-trace`` skipped every old replay
    and emitted rows claiming the new mode with ``resumed=True``.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    with pytest.raises(RealPathRerankError, match="recorded this tranche in mode"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            mode=MODE_CHAMPION_TRACE,
            resume=True,
        )
    # The SAME mode still resumes.
    assert run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-3.jsonl",
        config=_config(),
        resume=True,
    ).rows


def test_resume_refuses_a_non_canonical_map(tmp_path: Path) -> None:
    """The completeness fence rebuilds against the canonical map only (#314).

    ``eval.kill_craft.compute_kill_craft_report`` takes no map argument and
    calls ``load_canonical_map()`` unconditionally — and this task consumes
    ``eval/kill_craft.py`` exactly as committed. On a custom map the fence
    therefore disagrees with the recorder about the topology and rejects every
    otherwise-complete replay, so the resume silently re-records every paid
    seed: the feature delivering nothing while reporting success. Refused
    instead.
    """

    altered = load_canonical_map().model_copy(
        update={"kill_cooldown_ticks": load_canonical_map().kill_cooldown_ticks + 1}
    )
    work_dir = tmp_path / "work"
    # Recorded on the custom map, so there is no backend DRIFT to report — the
    # refusal has to come from the fence rule itself.
    run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
        game_map=altered,
    )
    with pytest.raises(
        RealPathRerankError, match="resume=True needs the canonical map"
    ):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            game_map=altered,
            resume=True,
        )


def test_explicit_invocation_ids_cannot_escape_the_work_dir(tmp_path: Path) -> None:
    """An invocation id is a filename token, not a path (Codex on PR #314)."""

    outside = tmp_path / "outside"
    outside.mkdir()
    directory = tmp_path / "work"
    for bad in ("slot/../../outside/escaped", "a/b", "..", "with space", ""):
        with pytest.raises(ValueError, match="invocation must be"):
            write_prescreen_record(
                directory, seeds=[1], quotes=[_quote()], invocation=bad
            )
    assert list(outside.iterdir()) == []
    # A filename-safe token still works.
    path = write_prescreen_record(
        directory, seeds=[1], quotes=[_quote()], invocation="slot_1-a"
    )
    assert path.parent == directory


def test_ranking_path_may_not_be_a_library_owned_work_dir_file(
    tmp_path: Path,
) -> None:
    """A ranking must not name a file the leg itself creates (Codex on PR #314).

    The existence preflight runs before the leg has written anything, so
    ``work_dir/leg-log.jsonl`` passes it — and then the leg log creates that
    path, and ``_publish_ranking``'s exclusive link fails AFTER every paid game.
    The failure mode every preflight here exists to prevent: a leg that can
    never commit its ranking.
    """

    work_dir = tmp_path / "work"
    for name in (
        LEG_LOG_FILENAME,
        f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json",
        f"{realpath.PRESCREEN_FILENAME_STEM}-1-2-000.json",
        f"{realpath.TRANCHE_CLAIM_FILENAME_STEM}-1-2.lock",
    ):
        with pytest.raises(RealPathRerankError, match="library-owned namespace"):
            run_realpath_rerank(
                [_util_candidate()],
                seeds=[1, 2],
                work_dir=work_dir,
                ranking_path=work_dir / name,
                config=_config(),
            )
    # Refused BEFORE any game: no work dir contents at all.
    assert not work_dir.exists() or list(work_dir.iterdir()) == []

    # A ranking OUTSIDE the work dir is the normal arrangement and is fine, as
    # is an unrelated name inside it.
    assert run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=work_dir / "ranking-1-2.jsonl",
        config=_config(),
    ).rows


def test_ranking_path_may_not_name_a_candidate_directory(tmp_path: Path) -> None:
    """A candidate RECORDING DIR is library-owned too (Codex on PR #314).

    My round-12 guard covered the ``leg-*`` / ``prescreen-*`` / ``tranche-claim-*``
    stems and stopped there, so ``work/000-utility-es`` passed: the leg created
    it as a directory, recorded every paid game into it, and the ranking publish
    then tried to hard-link onto a directory.

    Round 18 adds the FOUR-digit ordinals. ``f"{ordinal:03d}"`` sets a minimum
    width, not a maximum, and the allocator's walk runs to ``index + 1000``, so
    ``1000-utility-es`` is a directory this code really creates — and a preflight
    that matched a three-character stem let exactly that name through to the same
    post-spend link failure it exists to prevent.
    """

    work_dir = tmp_path / "work"
    for name in (
        "000-utility-es",
        "001-utility-es",
        "007-utility-es",
        "1000-utility-es",
        "12-utility-es",
    ):
        with pytest.raises(RealPathRerankError, match="candidate recording directory"):
            run_realpath_rerank(
                [_util_candidate()],
                seeds=[1, 2],
                work_dir=work_dir,
                ranking_path=work_dir / name,
                config=_config(),
            )
    assert not work_dir.exists() or list(work_dir.iterdir()) == []
    # A name that is NOT a candidate dir for this slate still works.
    assert run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=work_dir / "000-something-else.jsonl",
        config=_config(),
    ).rows


def test_resume_refuses_a_symlinked_recorded_dir(tmp_path: Path) -> None:
    """A single COMPONENT can still point anywhere (Codex review on PR #314).

    My round-13 guard was lexical, so ``001-candidate`` satisfied every test
    while being a symlink onto another campaign's recording directory: the
    resume followed it through ``mkdir(exist_ok=True)`` — which succeeds on a
    link to an existing dir — and recorded straight through it, so the same
    evidence destruction arrived by a different route.
    """

    work_dir = tmp_path / "work"
    victim = tmp_path / "other-campaign" / "candidate"
    victim.mkdir(parents=True)
    (victim / "sentinel.jsonl").write_text("untouched", encoding="utf-8")

    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    manifest = next(work_dir.glob("leg-1-2-*.json"))
    payload = json.loads(manifest.read_text())
    recorded = payload["candidates"][0]["dir"]
    shutil.rmtree(work_dir / recorded)
    (work_dir / recorded).symlink_to(victim, target_is_directory=True)
    manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    with pytest.raises(RealPathRerankError, match="is a SYMLINK"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )
    assert sorted(p.name for p in victim.iterdir()) == ["sentinel.jsonl"]
    assert (victim / "sentinel.jsonl").read_text(encoding="utf-8") == "untouched"


def test_ranking_path_may_not_be_the_work_dir_or_nested_inside_it(
    tmp_path: Path,
) -> None:
    """Both blind spots of the parent-equality containment test (Codex #314).

    The old check compared the ranking's PARENT against the work root, so the
    work dir ITSELF read as outside (its parent is its own parent), and so did
    anything nested BELOW the root. The first records the whole leg and then
    tries to hard-link onto a directory; the second is worse, because
    ``_refuse_unpublishable_ranking_dir`` mkdirs the ranking's parent as its
    link probe — creating the very directory candidate 1 must reserve, so
    candidate 0 spends every paid seed before candidate 1 fails its mkdir.
    """

    work_dir = tmp_path / "work"
    with pytest.raises(RealPathRerankError, match="IS the work dir"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=work_dir,
            config=_config(),
        )
    for nested in ("001-utility-es/ranking.jsonl", "deeper/still/ranking.jsonl"):
        with pytest.raises(RealPathRerankError, match="NESTED inside the work dir"):
            run_realpath_rerank(
                [_util_candidate()],
                seeds=[1, 2],
                work_dir=work_dir,
                ranking_path=work_dir / nested,
                config=_config(),
            )
    # Refused before ANY filesystem mutation — the link probe never ran, so the
    # candidate directory it would have created is absent.
    assert not work_dir.exists() or list(work_dir.iterdir()) == []

    # A top-level name inside the work dir is still fine (round-13 no-over-reach).
    assert run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=work_dir / "ranking-1-2.jsonl",
        config=_config(),
    ).rows


def test_a_dangling_ranking_symlink_is_refused_before_the_spend(
    tmp_path: Path,
) -> None:
    """``exists()`` follows links; ``os.link`` does not (Codex on PR #314).

    A dangling ``ranking_path`` symlink read as absent in the preflight, so the
    leg recorded every paid game — and the publish then saw the directory ENTRY
    and raised ``FileExistsError``, leaving the leg unpublishable after the full
    spend and every retry bouncing off the same entry.
    """

    work_dir = tmp_path / "work"
    dangling = tmp_path / "ranking.jsonl"
    dangling.symlink_to(tmp_path / "nowhere.jsonl")
    assert not dangling.exists() and dangling.is_symlink()

    with pytest.raises(RealPathRerankError, match="already exists"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=dangling,
            config=_config(),
        )
    assert not work_dir.exists() or list(work_dir.iterdir()) == []


def test_resume_refuses_a_changed_per_game_cost_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The game BUDGET is recording protocol (Codex review on PR #314).

    ``run_tournament_eval`` builds every default-runner game with a budget whose
    USD cap comes from ``AILIBI_MAX_COST_USD``, and that rode neither the config
    nor the provider settings. A resume across a changed cap adopted seeds
    recorded under the old limit and recorded the rest under the new one — a
    higher cap lets later meeting calls through, so one committed row combines
    games that could end differently.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")

    monkeypatch.setenv("AILIBI_MAX_COST_USD", "9.99")
    with pytest.raises(RealPathRerankError, match="different recording backend"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )


def test_a_custom_runner_records_no_default_runner_inputs() -> None:
    """The default-runner block is present or absent WHOLE (Codex on PR #314).

    ``run_tournament_eval`` installs a supplied ``meeting_runner_factory``
    directly and only otherwise calls ``build_default_meeting_runner`` /
    ``_resolve_game_budget`` — so every input those two read is consulted on one
    branch and not the other. Recording any of them for a custom runner refuses
    a resume over a knob the recorder never read (the round-9 over-refusal), and
    worse, an unparseable one blocks such a leg from starting at all.

    Rounds 14, 15 and 16 each filed one field of this block. Asserting the whole
    block moves together is what makes a seventeenth field impossible to get
    wrong.
    """

    def _identity(custom: bool, **env: str) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=custom,
            runner_identity="stub-runner" if custom else None,
            game_map=load_canonical_map(),
            num_players=4,
            environment=env,
        )

    hostile = {
        "AILIBI_LLM_PROVIDER": "totally-unknown",
        "AILIBI_MAX_COST_USD": "not-a-number",
        "AILIBI_PROMPT_SET": "no-such-set",
    }
    custom = _identity(True, **hostile)
    # Not merely equal-valued: ABSENT. Every one of these would otherwise have
    # raised on the hostile values above, so a custom-runner leg could not start.
    assert set(custom) == {
        "custom_meeting_runner",
        "meeting_runner_identity",
        "game_map_sha256",
    }
    assert _identity(True, AILIBI_LLM_PROVIDER="fake") == _identity(
        True, AILIBI_LLM_PROVIDER="anthropic", AILIBI_LLM_MEETING_MODEL="m"
    )

    # The DEFAULT runner carries the whole block and still reads every knob —
    # this narrowing must not reopen the round-6 finding that backend is protocol.
    default = _identity(False, AILIBI_LLM_PROVIDER="fake", AILIBI_MAX_COST_USD="9.99")
    assert default[realpath._GAME_BUDGET_KEY] == {
        "max_cost_usd": 9.99,
        "max_input_tokens": 1_000_000,
        "max_output_tokens": 200_000,
    }
    for key in (
        realpath._PROMPT_SET_KEY,
        realpath._ROLL_CALL_KEY,
        realpath._PROMPT_VERSIONS_KEY,
        "provider",
    ):
        assert key in default
    assert _identity(False, AILIBI_LLM_PROVIDER="fake") != _identity(
        False, AILIBI_LLM_PROVIDER="anthropic"
    )
    with pytest.raises(RealPathRerankError, match="unknown AILIBI_LLM_PROVIDER"):
        _identity(False, AILIBI_LLM_PROVIDER="totally-unknown")


#: Where an ``AILIBI_*`` name has to appear for the scan below to call it a READ.
#: The recording path's lookups all go through a mapping the module calls some
#: variant of "environment" (``os.environ``, an injected ``env``), which is the
#: 16.8 injected-environment idiom this repository follows everywhere.
_ENV_LOOKUP_RECEIVERS = frozenset({"environ", "environment", "env", "_env"})


class _ScannedModule(NamedTuple):
    """One closure module's parsed source plus its ``from X import Y`` map."""

    tree: ast.Module
    aliases: dict[str, tuple[str, str]]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _first_party_packages() -> frozenset[str]:
    """Top-level importable packages in the repo, minus the test tree."""

    return frozenset(
        entry.name
        for entry in _repo_root().iterdir()
        if entry.is_dir() and (entry / "__init__.py").exists()
    ) - {"tests"}


def _module_source(module: str) -> Path | None:
    parts = module.split(".")
    root = _repo_root()
    for candidate in (
        root.joinpath(*parts).with_suffix(".py"),
        root.joinpath(*parts, "__init__.py"),
    ):
        if candidate.exists():
            return candidate
    return None


def _dotted(node: ast.expr) -> str:
    """``a.b.c`` for a Name/Attribute chain, ``""`` for anything else."""

    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _imports_of(
    module: str, path: Path, tree: ast.Module
) -> tuple[set[str], dict[str, tuple[str, str]]]:
    """First-party modules this one imports, and its ``name -> (module, attr)`` map."""

    package = module if path.name == "__init__.py" else module.rsplit(".", 1)[0]
    first_party = _first_party_packages()
    targets: set[str] = set()
    aliases: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                parts = package.split(".")
                parts = parts[: len(parts) - (node.level - 1)]
                target = ".".join(parts) + (f".{node.module}" if node.module else "")
            else:
                target = node.module or ""
            targets.add(target)
            for alias in node.names:
                # ``from pkg import module`` and ``from module import NAME`` are
                # the same syntax; record both readings and let the resolution
                # below pick whichever exists.
                targets.add(f"{target}.{alias.name}")
                aliases[alias.asname or alias.name] = (target, alias.name)
    return {m for m in targets if m and m.split(".")[0] in first_party}, aliases


def _first_party_import_closure(roots: Sequence[str]) -> dict[str, _ScannedModule]:
    """Every first-party module reachable from ``roots`` by import, parsed.

    A source-level walk rather than an ``importlib`` one: it needs no import side
    effects, and it sees the imports as WRITTEN, which is what a reviewer reading
    the recording path would follow.
    """

    scanned: dict[str, _ScannedModule] = {}
    queue = list(roots)
    while queue:
        module = queue.pop()
        if module in scanned:
            continue
        path = _module_source(module)
        if path is None:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        children, aliases = _imports_of(module, path, tree)
        scanned[module] = _ScannedModule(tree=tree, aliases=aliases)
        queue.extend(child for child in children if child not in scanned)
    return scanned


def _env_name_constants(tree: ast.Module) -> dict[str, str]:
    """``NAME -> "AILIBI_..."`` for this module's env-name constants."""

    constants: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            target, value = node.target.id, node.value
        elif (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            target, value = node.targets[0].id, node.value
        else:
            continue
        if (
            isinstance(value, ast.Constant)
            and isinstance(value.value, str)
            and value.value.startswith("AILIBI_")
        ):
            constants[target] = value.value
    return constants


def _env_names_mentioned(closure: Mapping[str, _ScannedModule]) -> set[str]:
    """Every ``AILIBI_*`` string literal anywhere in the closure's source."""

    return {
        node.value
        for scanned in closure.values()
        for node in ast.walk(scanned.tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and node.value.startswith("AILIBI_")
    }


def _env_names_read(closure: Mapping[str, _ScannedModule]) -> set[str]:
    """Every ``AILIBI_*`` name the closure passes to an environment lookup.

    Mention is not reading: this repository keeps a retired lever's env-var
    constant alive so replay can still stamp the flag, and those constants are
    defined and exported but never looked up. Keying on the LOOKUP is what tells
    a live protocol input apart from a retired one.
    """

    constants = {name: _env_name_constants(m.tree) for name, m in closure.items()}

    def resolve(module: str, node: ast.expr) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Name):
            local = constants[module].get(node.id)
            if local is not None:
                return local
            source = closure[module].aliases.get(node.id)
            if source is not None:
                origin, attribute = source
                return constants.get(origin, {}).get(attribute)
        return None

    read: set[str] = set()
    for module, scanned in closure.items():
        for node in ast.walk(scanned.tree):
            key: ast.expr | None = None
            if isinstance(node, ast.Subscript):
                if _dotted(node.value).rpartition(".")[2] in _ENV_LOOKUP_RECEIVERS:
                    key = node.slice
            elif isinstance(node, ast.Call):
                function = node.func
                if isinstance(function, ast.Attribute) and function.attr == "get":
                    receiver = _dotted(function.value).rpartition(".")[2]
                    if receiver in _ENV_LOOKUP_RECEIVERS and node.args:
                        key = node.args[0]
                elif _dotted(function).rpartition(".")[2] == "getenv" and node.args:
                    key = node.args[0]
            if key is None:
                continue
            name = resolve(module, key)
            if name is not None and name.startswith("AILIBI_"):
                read.add(name)
    return read


def test_the_recording_identity_covers_every_env_input_on_the_path() -> None:
    """The ENUMERATION pin: the domain is checked, not just today's members.

    Six rounds each added one field to the recording identity because each round
    fixed the witness it was handed, so round 16 replaced the witnesses with an
    enumeration — and round 17 then found the enumeration itself incomplete. The
    scan is therefore DERIVED, not listed: it walks the first-party import
    closure of :data:`RECORDING_ENV_CALL_ROOTS` and reads every module in it, so
    a knob added under either root fails here whether or not anyone remembered to
    name its module (Codex review on PR #314).

    Two questions, because they fail differently:

    * SOUNDNESS — every knob that reaches an environment lookup in the closure is
      in ``RECORDING_ENV_INPUTS``, and vice versa. This is the identity's actual
      obligation.
    * ACCOUNTING — every ``AILIBI_*`` name MENTIONED anywhere in the closure is
      either a recording input or a retired always-on lever
      (``SUBSTRATE_FLAG_KEYS``). This is the backstop for the lookup analysis
      itself: a knob read through a receiver the analysis does not recognise
      still has to be named somewhere, and lands here as unaccounted-for.
    """

    from orchestrator.replay import SUBSTRATE_FLAG_KEYS

    closure = _first_party_import_closure(realpath.RECORDING_ENV_CALL_ROOTS)
    # The closure is a real transitive walk, not the roots plus a step.
    assert len(closure) > 20, f"suspiciously shallow closure: {sorted(closure)}"
    assert {"llm.provider", "agents.strategic.prompts.loader"} <= set(closure), (
        "the closure lost the provider selector or the prompt loader, which are "
        f"the modules the identity is built from: {sorted(closure)}"
    )

    read = _env_names_read(closure)
    missing = sorted(read - realpath.RECORDING_ENV_INPUTS)
    assert not missing, (
        f"the recording path reads {missing}, which the identity does not "
        "account for. Add it to _default_runner_inputs AND to "
        "RECORDING_ENV_INPUTS — a knob the identity misses is a resume that "
        "adopts bytes recorded under different settings."
    )
    stale = sorted(realpath.RECORDING_ENV_INPUTS - read)
    assert not stale, f"RECORDING_ENV_INPUTS names knobs nothing reads: {stale}"

    retired = {f"AILIBI_{key.upper()}" for key in SUBSTRATE_FLAG_KEYS}
    unaccounted = sorted(
        _env_names_mentioned(closure) - realpath.RECORDING_ENV_INPUTS - retired
    )
    assert not unaccounted, (
        f"the recording path names {unaccounted}, which is neither a declared "
        "recording input nor a retired always-on lever. If it is read, add it to "
        "RECORDING_ENV_INPUTS and _default_runner_inputs; if it is a graduated "
        "lever, it belongs in orchestrator.replay's substrate flag keys."
    )

    # And the enumeration is actually WIRED: every knob moves the identity of a
    # default-runner leg. Each is exercised under a base env where it is READ —
    # an Ollama knob does not move a Featherless leg, and asserting otherwise
    # would re-pin the round-9 over-refusal this identity was narrowed to avoid.
    ollama = {"AILIBI_LLM_PROVIDER": "ollama"}
    featherless = {"AILIBI_LLM_PROVIDER": "featherless"}
    roll_call_capable = {
        "AILIBI_LLM_PROVIDER": "fake",
        "AILIBI_PROMPT_SET": "qwen3_6_27b",
    }
    cases: tuple[tuple[str, dict[str, str], str], ...] = (
        ("AILIBI_LLM_PROVIDER", ollama, "featherless"),
        ("AILIBI_LLM_MEETING_MODEL", ollama, "some-model"),
        ("AILIBI_LLM_TRIGGER_MODEL", ollama, "other-model"),
        ("AILIBI_OLLAMA_HOST", ollama, "elsewhere:11434"),
        ("AILIBI_OLLAMA_SEED", ollama, "77"),
        ("AILIBI_OLLAMA_NUM_CTX", ollama, "4096"),
        ("AILIBI_FEATHERLESS_BASE_URL", featherless, "https://elsewhere.example"),
        ("AILIBI_PROMPT_SET", ollama, "qwen3_32b"),
        ("AILIBI_IMPOSTOR_ROLL_CALL", roll_call_capable, "1"),
        ("AILIBI_MAX_COST_USD", ollama, "9.99"),
    )
    assert {knob for knob, _, _ in cases} == realpath.RECORDING_ENV_INPUTS

    def _identity(env: dict[str, str]) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=False,
            runner_identity=None,
            game_map=load_canonical_map(),
            num_players=4,
            environment=env,
        )

    for knob, base, value in cases:
        assert _identity({**base, knob: value}) != _identity(base), (
            f"{knob} is enumerated but does not move the recording identity"
        )


def test_resume_refuses_a_manifest_dir_that_escapes_the_work_root(
    tmp_path: Path,
) -> None:
    """A manifest's ``dir`` is a basename, never a path (Codex on PR #314).

    ``_resolve_candidate_dirs`` joins the recorded string onto ``work_dir`` and
    records into the result, so a corrupted or hand-edited manifest naming
    ``../../other-campaign/candidate`` would aim this leg's recording — and its
    force re-records — at another campaign's replay evidence.
    """

    work_dir = tmp_path / "work"
    outside = tmp_path / "other-campaign"
    outside.mkdir()
    (outside / "sentinel.jsonl").write_text("untouched", encoding="utf-8")

    for escaping in ("../other-campaign/candidate", "..", "a/b", str(outside)):
        _record_two_seeds(work_dir, tmp_path / f"ranking-{abs(hash(escaping))}.jsonl")
        manifest = next(work_dir.glob("leg-1-2-*.json"))
        payload = json.loads(manifest.read_text())
        payload["candidates"][0]["dir"] = escaping
        manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        with pytest.raises(RealPathRerankError, match="single path component"):
            run_realpath_rerank(
                [_util_candidate()],
                seeds=[1, 2],
                work_dir=work_dir,
                ranking_path=tmp_path / f"resumed-{abs(hash(escaping))}.jsonl",
                config=_config(),
                resume=True,
            )
        shutil.rmtree(work_dir)

    assert (outside / "sentinel.jsonl").read_text(encoding="utf-8") == "untouched"


def test_every_candidate_is_rebuilt_before_the_leg_reserves_anything(
    tmp_path: Path,
) -> None:
    """A bad candidate must not strand the work dir (Codex on PR #314).

    ``_build_agent_factory`` ran lazily inside the recording loop, so an invalid
    genome on candidate N raised only after 1..N-1 had consumed paid games — and
    the manifest already recorded the whole slate, so correcting the bad
    candidate changes its identity and the resume is refused as drift, while a
    fresh retry collides with the reserved directories.
    """

    good = _util_candidate("arm-good")
    bad = _util_candidate("arm-bad").model_copy(
        update={"genome": _util_candidate().genome + (0.0,)}
    )
    work_dir = tmp_path / "work"
    with pytest.raises(RealPathRerankError, match="does not rebuild as"):
        run_realpath_rerank(
            [good, bad],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-1.jsonl",
            config=_config(),
        )
    # NOTHING reserved and NOTHING recorded: no manifest, no candidate dirs.
    assert not work_dir.exists() or list(work_dir.iterdir()) == []
    # The corrected slate then runs into a clean work dir.
    assert run_realpath_rerank(
        [good],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
    ).rows


def test_a_post_commit_log_failure_does_not_fail_a_committed_leg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Once the ranking is published the leg SUCCEEDED (Codex on PR #314).

    The trailing rank / leg-done appends sat inside the broad failure handler,
    so an append failure emitted ``leg-failed`` and raised even though the
    ranking already existed — and every retry is then refused by the ranking
    preflight, making a leg that actually succeeded permanently unrepeatable.
    """

    work_dir = tmp_path / "work"
    ranking_path = tmp_path / "ranking-1.jsonl"
    real_emit = realpath.RealPathLegLog.emit

    def _fail_after_commit(
        self: realpath.RealPathLegLog, event: str, **fields: object
    ) -> None:
        if event in {"rank", "leg-done"}:
            raise OSError("no space left on device")
        real_emit(self, event, **fields)

    monkeypatch.setattr(realpath.RealPathLegLog, "emit", _fail_after_commit)
    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=ranking_path,
        config=_config(),
    )
    monkeypatch.undo()

    # The leg returned its committed result, and the ranking is on disk.
    assert result.rows
    assert ranking_path.exists()
    # The lost audit lines are REPORTED, not swallowed.
    assert "IS committed" in capsys.readouterr().err
    # And the leg log records no failure, because there was none.
    events = [
        json.loads(line)["event"]
        for line in (work_dir / LEG_LOG_FILENAME).read_text().splitlines()
    ]
    assert "leg-failed" not in events


def test_the_allocation_claim_is_held_across_resolution(tmp_path: Path) -> None:
    """The allocation lock is work-dir-wide, and blocking rather than refusing.

    Two legs on DIFFERENT tranches are legitimate concurrency and must both
    succeed — they simply cannot allocate at the same instant. That is the
    opposite posture to :func:`_tranche_claim`, which refuses outright, so the
    two are pinned apart here.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir(parents=True)
    claim = work_dir / f"{realpath.TRANCHE_CLAIM_FILENAME_STEM}-allocation.lock"

    with realpath._allocation_claim(work_dir) as path:
        assert path == claim
    assert claim.exists()

    # A tranche claim does NOT block allocation: they are different locks.
    with realpath._tranche_claim(work_dir, tranche="1-2"):
        with realpath._allocation_claim(work_dir):
            pass


def test_backend_identity_pins_only_the_selected_providers_settings() -> None:
    """The identity is the EFFECTIVE config, not the raw environment (Codex #314).

    Recording all eight ``AILIBI_*`` variables raw made the identity both too
    wide and too narrow: a fake or Featherless resume was refused because an
    unrelated ``AILIBI_OLLAMA_*`` knob moved (forfeiting the verified-resume
    benefit over a knob the recorder never reads), while setting a variable to
    the value it already resolves to read as drift. The identity now mirrors
    ``build_default_client``'s own dispatch, so it moves exactly when the
    constructed recorder would.
    """

    game_map = load_canonical_map()

    def _identity(**env: str) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=False, game_map=game_map, num_players=4, environment=env
        )

    # IRRELEVANT knobs, per provider: changing one must not move the identity.
    irrelevant = {
        "fake": (
            "AILIBI_OLLAMA_HOST",
            "AILIBI_OLLAMA_SEED",
            "AILIBI_OLLAMA_NUM_CTX",
            "AILIBI_FEATHERLESS_BASE_URL",
            "AILIBI_LLM_MEETING_MODEL",
            "AILIBI_LLM_TRIGGER_MODEL",
        ),
        "ollama": ("AILIBI_FEATHERLESS_BASE_URL",),
        "featherless": (
            "AILIBI_OLLAMA_HOST",
            "AILIBI_OLLAMA_SEED",
            "AILIBI_OLLAMA_NUM_CTX",
        ),
        "anthropic": (
            "AILIBI_OLLAMA_HOST",
            "AILIBI_OLLAMA_SEED",
            "AILIBI_OLLAMA_NUM_CTX",
            "AILIBI_FEATHERLESS_BASE_URL",
        ),
    }
    for provider, knobs in irrelevant.items():
        base = _identity(AILIBI_LLM_PROVIDER=provider)
        for knob in knobs:
            value = "7" if knob.endswith(("SEED", "NUM_CTX")) else "changed"
            assert _identity(AILIBI_LLM_PROVIDER=provider, **{knob: value}) == base, (
                f"{knob} moved the {provider} identity but {provider} never reads it"
            )

    # RELEVANT knobs, per provider: changing one MUST move the identity.
    relevant = {
        "ollama": ("AILIBI_OLLAMA_HOST", "AILIBI_OLLAMA_SEED", "AILIBI_OLLAMA_NUM_CTX"),
        "featherless": ("AILIBI_FEATHERLESS_BASE_URL",),
        "anthropic": ("AILIBI_LLM_MEETING_MODEL", "AILIBI_LLM_TRIGGER_MODEL"),
    }
    for provider, knobs in relevant.items():
        base = _identity(AILIBI_LLM_PROVIDER=provider)
        for knob in knobs:
            value = "7" if knob.endswith(("SEED", "NUM_CTX")) else "changed"
            assert _identity(AILIBI_LLM_PROVIDER=provider, **{knob: value}) != base, (
                f"{knob} left the {provider} identity unchanged but it is read"
            )

    # NORMALISED, not raw: setting a knob to the value it already resolves to is
    # not drift, and neither is whitespace or case around the provider name.
    assert _identity(AILIBI_LLM_PROVIDER=" OLLAMA ") == _identity(
        AILIBI_LLM_PROVIDER="ollama"
    )
    assert _identity(
        AILIBI_LLM_PROVIDER="ollama", AILIBI_OLLAMA_HOST="localhost:11434"
    ) == _identity(AILIBI_LLM_PROVIDER="ollama")

    # The prompt set rides EVERY provider — it picks the rendered templates and
    # the recorded prompt versions regardless of who serves the tokens.
    for provider in ("fake", "ollama", "featherless", "anthropic"):
        assert _identity(
            AILIBI_LLM_PROVIDER=provider, AILIBI_PROMPT_SET="qwen3_32b"
        ) != _identity(AILIBI_LLM_PROVIDER=provider)

    # An unbuildable provider is refused here, before any seed is recorded,
    # rather than deep inside the first game.
    with pytest.raises(RealPathRerankError, match="unknown AILIBI_LLM_PROVIDER"):
        _identity(AILIBI_LLM_PROVIDER="not-a-provider")

    # A malformed numeric knob keeps the recorder's own fail-loud parse.
    with pytest.raises(ValueError, match="base-10 integer"):
        _identity(AILIBI_LLM_PROVIDER="ollama", AILIBI_OLLAMA_SEED="not-an-int")

    # No credential is ever written into an on-disk identity mapping.
    identity = _identity(
        AILIBI_LLM_PROVIDER="anthropic", ANTHROPIC_API_KEY="sk-secret-value"
    )
    assert "sk-secret-value" not in json.dumps(identity, sort_keys=True)


def test_resume_places_labels_whose_slugs_collide(tmp_path: Path) -> None:
    """Distinct labels sharing a SLUG must still resume (Codex on PR #314 follow-up).

    ``_safe_slug`` is not injective: ``"arm a"`` and ``"arm-a"`` are two labels
    the recorder accepts as distinct (uniqueness is checked on the LABEL) that
    map onto one slug. Round 6 resolved resume directories by globbing
    ``*-<slug>``, so such a leg recorded fine into ``000-arm-a``/``001-arm-a``
    and could then NEVER resume — every lookup found two dirs and refused as
    ambiguous. The manifest now records each candidate's directory, so the
    label maps to it exactly.
    """

    work_dir = tmp_path / "work"
    candidates = [_util_candidate("arm a"), _util_candidate("arm-a")]
    run_realpath_rerank(
        candidates,
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
    )
    assert sorted(p.name for p in work_dir.iterdir() if p.is_dir()) == [
        "000-arm-a",
        "001-arm-a",
    ]
    # The manifest states which dir belongs to which label.
    manifest = json.loads((work_dir / "leg-1-000.json").read_text())
    assert {entry["label"]: entry["dir"] for entry in manifest["candidates"]} == {
        "arm a": "000-arm-a",
        "arm-a": "001-arm-a",
    }

    resumed = run_realpath_rerank(
        candidates,
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    assert all(entry.resumed for row in resumed.rows for entry in row.seed_telemetry)

    # And narrowing to one of the colliding labels still finds ITS dir.
    narrowed = run_realpath_rerank(
        [_util_candidate("arm-a")],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-3.jsonl",
        config=_config(),
        resume=True,
    )
    assert [entry.resumed for entry in narrowed.top().seed_telemetry] == [True]


def test_a_new_label_never_adopts_a_colliding_slugs_recordings(
    tmp_path: Path,
) -> None:
    """A label the manifest never saw must get a FRESH dir (Codex on PR #314).

    ``_safe_slug`` is many-to-one, so a NEW label can share a slug with exactly
    one old one. Selecting that unique match silently credits this candidate
    with another's games — and ``_resume_skip_reason`` cannot catch it, because
    the two labels may legitimately carry the same genome and stamp (this
    module permits exactly that). The manifest is the authority: a label absent
    from it is new, and new candidates never inherit bytes.
    """

    work_dir = tmp_path / "work"
    run_realpath_rerank(
        [_util_candidate("arm a")],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
    )
    assert sorted(p.name for p in work_dir.iterdir() if p.is_dir()) == ["000-arm-a"]

    # A DIFFERENT label whose slug collides with the recorded one.
    result = run_realpath_rerank(
        [_util_candidate("arm-a")],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    assert [entry.resumed for entry in result.top().seed_telemetry] == [False]
    # It recorded into its OWN directory, leaving the original untouched.
    assert sorted(p.name for p in work_dir.iterdir() if p.is_dir()) == [
        "000-arm-a",
        "001-arm-a",
    ]


def test_resume_refuses_a_changed_prompt_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``AILIBI_PROMPT_SET`` selects templates AND recorded prompt versions.

    ``build_default_meeting_runner`` resolves it, so two prompt sets are two
    recording protocols on one provider and model (Codex on PR #314).
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    monkeypatch.setenv("AILIBI_PROMPT_SET", "qwen3_32b")
    with pytest.raises(RealPathRerankError, match="different recording backend"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )


def test_resume_refuses_a_bumped_prompt_registry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The RESOLVED versions are the provenance, not the selector (Codex #314).

    ``prompt_set`` + the roll-call lever select which registry entry is read;
    bumping the registry WITHIN a set changes the rendered bytes while both
    routing inputs stay put, so the identity was unchanged and a resume skipped
    seeds rendered from the old templates while recording the rest from the new.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")

    active = resolve_prompt_set(env=dict(os.environ))
    bumped = {**PROMPT_VERSION_SETS[active], "crewmate_report": "crewmate_report.v99"}
    monkeypatch.setitem(PROMPT_VERSION_SETS, active, bumped)

    with pytest.raises(RealPathRerankError, match="different recording backend"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )


def test_a_custom_runner_records_no_default_provider_settings(
    tmp_path: Path,
) -> None:
    """A supplied runner never reads the provider knobs (Codex on PR #314).

    ``run_tournament_eval`` installs it directly and never calls
    ``build_default_meeting_runner``, so recording the selected provider/model
    refused an otherwise valid custom-runner resume — and an unknown ambient
    ``AILIBI_LLM_PROVIDER`` blocked such a leg from starting at all, even though
    nothing would have constructed a client from it.
    """

    def _identity(**env: str) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=True,
            runner_identity="stub-runner",
            game_map=load_canonical_map(),
            num_players=4,
            environment=env,
        )

    assert _identity(AILIBI_LLM_PROVIDER="fake") == _identity(
        AILIBI_LLM_PROVIDER="anthropic", AILIBI_MEETING_MODEL="some-model"
    )
    # An unknown ambient provider no longer blocks a leg that never reads it.
    assert _identity(AILIBI_LLM_PROVIDER="totally-unknown")["custom_meeting_runner"]

    # The DEFAULT runner still pins every one of those knobs — this narrowing
    # must not reopen the round-6 finding that the backend is protocol.
    def _default(**env: str) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=False,
            runner_identity=None,
            game_map=load_canonical_map(),
            num_players=4,
            environment=env,
        )

    assert _default(AILIBI_LLM_PROVIDER="fake") != _default(
        AILIBI_LLM_PROVIDER="anthropic"
    )
    with pytest.raises(RealPathRerankError, match="unknown AILIBI_LLM_PROVIDER"):
        _default(AILIBI_LLM_PROVIDER="totally-unknown")


def test_a_claim_is_matched_to_the_candidate_being_allocated(tmp_path: Path) -> None:
    """Per-CANDIDATE, not per-slate (Codex review on PR #314).

    A slate-wide "is this claim one of ours?" exemption reads a reservation for
    label A as available to label B whenever both are on the slate and share a
    slug. A reordered slate then hands A's reserved directory to B and moves A
    elsewhere — defeating the (tranche, label) rule this is the implementation
    of, and leaving later retries following the reassigned mapping.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps(
            {"tranche": "1-2", "candidates": [_claim_entry("arm a", "000-arm-a")]}
        ),
        encoding="utf-8",
    )

    # Both labels share the slug "arm-a", and the RESERVED label is second.
    resolved = realpath._resolve_candidate_dirs(
        work_dir,
        tranche="1-2",
        candidates=[_util_candidate(label="arm-a"), _util_candidate(label="arm a")],
        resume=False,
    )
    placed = dict(
        zip(["arm-a", "arm a"], [path.name for path in resolved], strict=True)
    )
    # The reservation belongs to "arm a" and must go to "arm a", whatever the
    # slate order — the other label steps aside.
    assert placed["arm a"] == "000-arm-a"
    assert placed["arm-a"] != "000-arm-a"


def test_a_reused_label_may_not_inherit_a_reservation(tmp_path: Path) -> None:
    """A reservation is the CANDIDATE's, not the label's (Codex review on PR #314).

    Round 17 let a candidate reclaim the directory a prior manifest reserved for
    its ``(tranche, label)``. If the first leg published its manifest and died
    before ``mkdir``, a later FRESH leg reusing the label for a different genome
    inherited that reservation and recorded the new bytes into it — leaving the
    tranche with two manifests that disagree about the label, which
    ``_refuse_protocol_drift`` reads as drift forever after. The refusal lands
    before any allocation, so nothing is recorded and nothing is claimed.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    original = _util_candidate(label="arm-a")
    moved = original.model_copy(
        update={"genome": tuple(original.genome[:-1]) + (original.genome[-1] + 1.0,)}
    )
    assert realpath._genome_digest(moved.genome) != realpath._genome_digest(
        original.genome
    )
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps(
            {
                "tranche": "1-2",
                "candidates": [
                    {
                        "label": "arm-a",
                        "dir": "000-arm-a",
                        "weights_sha256": realpath._genome_digest(original.genome),
                        "encoder_version": original.encoder_version,
                        "hidden": original.hidden,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(RealPathRerankError, match="A label is not an identity"):
        run_realpath_rerank(
            [moved],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(),
        )
    # Nothing was allocated: the reserved directory is still unmade, and no
    # second manifest exists to poison the tranche's future resumes.
    assert not (work_dir / "000-arm-a").exists()
    assert (
        len(list(work_dir.glob(f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-*.json")))
        == 1
    )
    # And the allocator itself refuses the inheritance even reached directly —
    # the refusal above is the fail-loud seam, this is the rule underneath it.
    resolved = realpath._resolve_candidate_dirs(
        work_dir, tranche="1-2", candidates=[moved], resume=False
    )
    assert resolved[0].name != "000-arm-a"
    # The UNCHANGED candidate still reclaims its own reservation (round 17).
    assert (
        realpath._resolve_candidate_dirs(
            work_dir, tranche="1-2", candidates=[original], resume=False
        )[0].name
        == "000-arm-a"
    )


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ({"weights_sha256": None}, "without"),
        ({"encoder_version": None}, "without"),
        ({"hidden": None}, "without"),
        ({"weights_sha256": 17}, "malformed"),
        ({"encoder_version": ["v1"]}, "malformed"),
        ({"hidden": "8"}, "malformed"),
        ({"hidden": True}, "malformed"),
    ],
    ids=[
        "no-digest",
        "no-family",
        "no-width",
        "digest-not-a-string",
        "family-not-a-string",
        "width-a-string",
        "width-a-bool",
    ],
)
def test_a_malformed_manifest_identity_is_refused_not_downgraded(
    tmp_path: Path, mutation: dict[str, object], expected: str
) -> None:
    """Unreadable identity is corrupted evidence, not a legacy format (Codex #314).

    The round-18 version returned ``None`` for an entry whose identity fields were
    missing or malformed, and callers read that as "this claim speaks for the
    label only" — a silent weakening exactly where the strength is load-bearing.
    A fresh invocation with changed bytes could reclaim the malformed manifest's
    reservation, spend its games, and leave the tranche holding contradictory
    manifests. There is no legacy format to accommodate: leg manifests arrived
    with this task and have always carried these three fields.

    ``hidden: None`` is deliberately expressed as key REMOVAL below, not as a null
    value — the utility family records a null width legitimately, and conflating
    the two is the bug the round-18 pin caught.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    original = _util_candidate(label="arm-a")
    entry = _claim_entry("arm-a", "000-arm-a", original)
    for key, value in mutation.items():
        if value is None:
            del entry[key]
        else:
            entry[key] = value
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps({"tranche": "1-2", "candidates": [entry]}), encoding="utf-8"
    )

    moved = original.model_copy(
        update={"genome": tuple(original.genome[:-1]) + (original.genome[-1] + 1.0,)}
    )
    with pytest.raises(RealPathRerankError, match=expected):
        run_realpath_rerank(
            [moved],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(),
        )
    # Refused BEFORE allocation: nothing recorded, no second manifest to poison
    # the tranche's future resumes.
    assert not (work_dir / "000-arm-a").exists()
    assert (
        len(list(work_dir.glob(f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-*.json")))
        == 1
    )
    # The allocator refuses it too, rather than reading the claim as label-only
    # and handing the reservation to whichever candidate wears the name.
    with pytest.raises(RealPathRerankError, match=expected):
        realpath._resolve_candidate_dirs(
            work_dir, tranche="1-2", candidates=[moved], resume=False
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("label", 17),
        ("label", None),
        ("label", ""),
        ("dir", 17),
        ("dir", ""),
    ],
    ids=["label-int", "label-null", "label-empty", "dir-int", "dir-empty"],
)
def test_a_malformed_claim_owner_is_refused_not_skipped(
    tmp_path: Path, field: str, value: object
) -> None:
    """A claim whose owner cannot be named is corrupted, not absent (Codex #314).

    Round 19 made a malformed IDENTITY fail loud and left the label and dir on an
    inline predicate that silently skipped them — one field over, the same silent
    weakening. The entry still names a real directory, so dropping it discards a
    durable RESERVATION: a fresh leg then allocates the claimed directory, or
    publishes a ranking into it, and the original leg is unrecoverable.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    entry = _claim_entry("arm-a", "000-arm-a")
    entry[field] = value
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps({"tranche": "1-2", "candidates": [entry]}), encoding="utf-8"
    )

    # The ALLOCATOR refuses rather than treating the directory as unclaimed.
    with pytest.raises(RealPathRerankError, match="corrupted evidence"):
        realpath._resolve_candidate_dirs(
            work_dir,
            tranche="1-2",
            candidates=[_util_candidate(label="arm-a")],
            resume=False,
        )
    # And so does the whole leg, before it spends anything.
    with pytest.raises(RealPathRerankError, match="corrupted evidence"):
        run_realpath_rerank(
            [_util_candidate(label="arm-a")],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(),
        )
    assert not (work_dir / "000-arm-a").exists()


def test_a_tranche_may_not_repeat_a_seed() -> None:
    """Uniqueness belongs in the shared key, not only the recorder (Codex #314).

    ``run_realpath_rerank`` rejects a repeated seed, but ``write_prescreen_record``
    is public and reaches ``tranche_key`` directly — so ``[1, 1, 2]`` keyed a
    distinct "gapped" tranche and would have written audit evidence for a seed
    set the recorder can never execute. A tranche IS a set; a set has no
    multiplicities.
    """

    with pytest.raises(ValueError, match="repeated seeds"):
        realpath.tranche_key([1, 1, 2])
    with pytest.raises(ValueError, match="repeated seeds"):
        realpath.tranche_key([4000, 4000])
    # NO OVER-REACH: every legitimate shape still keys, and byte-identically to
    # before — the committed contiguous names are unchanged.
    assert realpath.tranche_key([1, 2]) == "1-2"
    assert realpath.tranche_key([4000, 4001, 4002]) == "4000-4002"
    assert realpath.tranche_key([7]) == "7"
    assert realpath.tranche_key([3, 2, 1]) == "1-3"
    assert realpath.tranche_key([1, 2, 4]).startswith("1-4-")


def test_keying_a_large_tranche_stays_linear() -> None:
    """Both halves of the key must be cheap (Codex review on PR #314).

    Round 21 removed the span materialisation and my own duplicate check
    replaced it with a quadratic scan — ``list(seeds).count(seed)`` per seed, so
    a 100k-seed tranche did ~10^10 comparisons and hung just as thoroughly. A
    wall-clock bound is the only assertion that catches either shape.
    """

    import time

    seeds = list(range(0, 200_000, 2))  # 100k seeds, sparse
    started = time.monotonic()
    key = realpath.tranche_key(seeds)
    elapsed = time.monotonic() - started
    assert key.startswith("0-199998-") and len(key.split("-")[-1]) == 64
    assert elapsed < 5.0, f"tranche_key took {elapsed:.1f}s on 100k seeds"
    # And a duplicate in a large tranche is still reported, by name.
    with pytest.raises(ValueError, match=r"repeated seeds \[8\]"):
        realpath.tranche_key([*seeds, 8])


def test_the_default_backend_ignores_a_runner_identity(tmp_path: Path) -> None:
    """A field outside the block it belongs to (Codex review on PR #314).

    ``meeting_runner_identity`` is only consulted when a custom runner is
    installed. Carrying it unconditionally meant a resume that omitted an
    incidental identity — or passed a different one — read as backend drift while
    every effective recorder input agreed. Round 16's rule is present-whole /
    absent-whole per branch; this field had been sitting outside it.
    """

    def identity(custom: bool, runner_identity: str | None) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=custom,
            runner_identity=runner_identity,
            game_map=load_canonical_map(),
            num_players=4,
            environment={"AILIBI_LLM_PROVIDER": "fake"},
        )

    default_none = identity(False, None)
    assert "meeting_runner_identity" not in default_none
    assert identity(False, "incidental") == default_none
    assert identity(False, "something-else") == default_none

    # NO OVER-REACH: on the CUSTOM branch the identity is still what distinguishes
    # one runner from another — narrowing must not reopen round 8.
    assert identity(True, "runner-a")["meeting_runner_identity"] == "runner-a"
    assert identity(True, "runner-a") != identity(True, "runner-b")


def test_a_malformed_recorded_dir_is_refused_not_slug_searched(
    tmp_path: Path,
) -> None:
    """The legacy fallback may not be reachable by corruption (Codex #314).

    ``_recorded_candidate_dirs`` recorded the label as seen while omitting a
    malformed ``dir``, which dropped the resume into the legacy slug search — and
    with exactly one matching ``*-<slug>`` directory present, the resume adopted
    its recordings instead of refusing the corrupted claim. The fallback exists
    for manifests written before the ``dir`` field; corruption is not that.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / "000-utility-es").mkdir()
    entry = _claim_entry("utility-es", "000-utility-es")
    del entry["dir"]
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps({"tranche": "1-2", "candidates": [entry]}), encoding="utf-8"
    )

    with pytest.raises(RealPathRerankError, match="corrupted evidence"):
        realpath._recorded_candidate_dirs(work_dir, tranche="1-2")


def test_a_fresh_leg_refuses_an_existing_dir_before_publishing_its_claim(
    tmp_path: Path,
) -> None:
    """A failed no-clobber check must not leave a claim behind (Codex #314, P1).

    The manifest is published BEFORE the recording loop's exclusive ``mkdir``, so
    a fresh leg whose enumerated directory already existed but was unclaimed
    published a manifest naming it and only THEN collided. That manifest is
    durable: a later ``resume=True`` read it as proof of ownership and skipped
    whatever replays already sat in the directory — bytes this invocation never
    wrote and never verified against its own protocol.

    The collision is unchanged (still ``FileExistsError``, still write-once); only
    its ORDER moved, ahead of the publish.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    stale = work_dir / "000-utility-es"
    stale.mkdir()
    (stale / "replay-seed-1.jsonl").write_text("{}\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="no leg manifest claims it"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking.jsonl",
            config=_config(),
        )
    # THE POINT: no manifest was published, so nothing can later read the failed
    # invocation as the owner of those bytes.
    assert not list(work_dir.glob(f"{realpath.LEG_MANIFEST_FILENAME_STEM}-*.json"))
    assert (stale / "replay-seed-1.jsonl").read_text(encoding="utf-8") == "{}\n"


def test_resume_drift_ignores_manifests_for_unrelated_candidates(
    tmp_path: Path,
) -> None:
    """Sharing a tranche key is not sharing an experiment (Codex #314, P1).

    One work dir may legitimately hold two FRESH legs over the same seed set
    under different protocols with disjoint labels — the fresh path permits the
    protocol change and gives them separate directories. Comparing a resume
    against the unrelated manifest refused it on a config that describes bytes it
    will never read, so an interrupted 30-40 h leg became unresumable because a
    neighbour happened to share its seeds.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    # An unrelated fresh leg on the same tranche: distinct label, different
    # protocol (a different max_attempts), its own directory.
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps(
            {
                "tranche": "1-2",
                "mode": realpath.MODE_TOP_K,
                "config": _config(max_attempts=3).model_dump(mode="json"),
                "backend": {"custom_meeting_runner": True, "other": "backend"},
                "candidates": [_claim_entry("someone-else", "000-someone-else")],
            }
        ),
        encoding="utf-8",
    )

    # A resume for OUR label must not be refused by that manifest.
    realpath._refuse_protocol_drift(
        work_dir,
        tranche="1-2",
        mode=realpath.MODE_TOP_K,
        config=_config(),
        candidates=[_util_candidate(label="ours")],
        backend={"custom_meeting_runner": False},
        opponent=None,
    )

    # NO OVER-REACH: a manifest that DOES own one of our labels is still compared,
    # so the drift check has not been hollowed out.
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-001.json").write_text(
        json.dumps(
            {
                "tranche": "1-2",
                "mode": realpath.MODE_TOP_K,
                "config": _config(max_attempts=3).model_dump(mode="json"),
                "backend": {"custom_meeting_runner": False},
                "candidates": [_claim_entry("ours", "001-ours")],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(RealPathRerankError, match="different protocol"):
        realpath._refuse_protocol_drift(
            work_dir,
            tranche="1-2",
            mode=realpath.MODE_TOP_K,
            config=_config(),
            candidates=[_util_candidate(label="ours")],
            backend={"custom_meeting_runner": False},
            opponent=None,
        )


def test_a_hard_linked_replay_is_refused(tmp_path: Path) -> None:
    """``is_symlink()`` is false for a hard link (Codex review on PR #314).

    A replay hard-linked to another campaign's file passed the round-16 no-links
    guard outright. Both outcomes are silent: if the stamp and fence pass the
    resume adopts bytes owned elsewhere, and if either misses the ``force=True``
    re-record truncates the SHARED inode and destroys the other campaign's
    replay. The rule is real AND sole-owner.
    """

    foreign = tmp_path / "other-campaign" / "replay-seed-1.jsonl"
    foreign.parent.mkdir(parents=True)
    foreign.write_text('{"kind":"other-campaign"}\n', encoding="utf-8")

    linked = tmp_path / "work" / "000-utility-es" / "replay-seed-1.jsonl"
    linked.parent.mkdir(parents=True)
    os.link(foreign, linked)
    assert not linked.is_symlink() and linked.stat().st_nlink == 2

    with pytest.raises(RealPathRerankError, match="HARD LINK"):
        realpath._refuse_symlinked_recording_entry(linked, what="the replay,")
    # The other campaign's bytes are untouched.
    assert foreign.read_text(encoding="utf-8") == '{"kind":"other-campaign"}\n'

    # NO OVER-REACH: an ordinary sole-owner replay still passes, and so does an
    # absent one (the fresh case).
    linked.unlink()
    linked.write_text('{"kind":"ours"}\n', encoding="utf-8")
    realpath._refuse_symlinked_recording_entry(linked, what="the replay,")
    realpath._refuse_symlinked_recording_entry(
        linked.with_name("replay-seed-99.jsonl"), what="the replay,"
    )


def test_a_sparse_tranche_keys_without_materializing_the_span() -> None:
    """Contiguity is an adjacent-pair question (Codex review on PR #314).

    ``canonical == list(range(first, last + 1))`` allocated one element per
    integer between the endpoints, so a legitimate sparse tranche exhausted
    memory before reaching the digest path it was headed for.
    """

    key = realpath.tranche_key([0, 1_000_000_000])
    assert key.startswith("0-1000000000-") and len(key.split("-")[-1]) == 64
    # And every contiguous form is byte-unchanged, which is what the committed
    # and fixture names depend on.
    assert realpath.tranche_key([1, 2]) == "1-2"
    assert realpath.tranche_key(list(range(4000, 4010))) == "4000-4009"


def test_a_resume_honours_another_tranches_reservation(tmp_path: Path) -> None:
    """The resume allocator asked the FILESYSTEM, not the claims (Codex #314, P1).

    ``_fresh_candidate_dir`` serves a resume adding a label with no prior
    recording, and it treated a path as free whenever no directory entry
    existed. So a tranche that published a manifest and was interrupted before
    ``mkdir`` could have its reserved directory taken by a resume of ANOTHER
    tranche whose new label happened to share the slug — after which the first
    tranche cannot recover and either leg may adopt or overwrite the other's
    evidence. The fresh allocator has honoured claims since round 16; this path
    was the same question asked from the other side.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    # Tranche 1-2 reserved 000-arm-a and never created it.
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps(
            {"tranche": "1-2", "candidates": [_claim_entry("arm-a", "000-arm-a")]}
        ),
        encoding="utf-8",
    )
    assert not (work_dir / "000-arm-a").exists()

    other = _util_candidate(label="arm a")  # same slug, different label
    chosen = realpath._fresh_candidate_dir(
        work_dir, index=0, tranche="9-9", candidate=other, reserved=set()
    )
    assert chosen.name != "000-arm-a", "took another tranche's reservation"

    # NO OVER-REACH: the OWNER still gets its own reservation back.
    mine = _util_candidate(label="arm-a")
    assert (
        realpath._fresh_candidate_dir(
            work_dir, index=0, tranche="1-2", candidate=mine, reserved=set()
        ).name
        == "000-arm-a"
    )


@pytest.mark.parametrize(
    ("entries", "expected"),
    [
        ([("arm-a", "000-arm-a"), ("arm-a", "001-arm-a")], "twice"),
        ([("arm-a", "000-arm-a"), ("arm b", "000-arm-a")], "exactly one candidate"),
    ],
    ids=["one-label-two-dirs", "two-labels-one-dir"],
)
def test_an_ambiguous_manifest_mapping_is_refused(
    tmp_path: Path, entries: list[tuple[str, str]], expected: str
) -> None:
    """A manifest's candidate map is a BIJECTION (Codex review on PR #314, P1).

    Assigning by iteration order let a corrupted manifest naming one label twice
    pick a winner silently, and the resume then adopted — and could skip — that
    directory while the durable claim named two possible homes for the bytes.
    The mirror case is the one-directory-two-candidates contamination this
    module refuses everywhere else.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps(
            {
                "tranche": "1-2",
                "candidates": [
                    _claim_entry(label, directory) for label, directory in entries
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(RealPathRerankError, match=expected):
        realpath._recorded_candidate_dirs(work_dir, tranche="1-2")


def test_a_linked_roster_is_refused_before_any_seed(tmp_path: Path) -> None:
    """``roster.json`` is a recording entry too (Codex review on PR #314, P1).

    ``_write_roster_json`` calls ``write_text`` unconditionally at the end of
    the seed loop, so a linked entry in an adopted directory follows a symlink
    out of the work dir, or truncates a shared inode — modifying another
    campaign while corrupting the provenance the scoring gates read. The
    round-21 sole-owner rule covered replays, directories and the leg log; this
    was the one entry the leg WRITES that it did not cover.
    """

    foreign = tmp_path / "other" / "roster.json"
    foreign.parent.mkdir(parents=True)
    foreign.write_text('{"num_players": 99}', encoding="utf-8")

    for kind in ("symlink", "hardlink"):
        # A REAL recorded leg, so the resume genuinely resolves to this
        # directory through its own manifest — the path the defect lives on.
        work_dir = tmp_path / kind / "work"
        _record_two_seeds(work_dir, tmp_path / f"{kind}-first.jsonl")
        roster = work_dir / "000-utility-es" / "roster.json"
        assert roster.is_file()
        roster.unlink()
        if kind == "symlink":
            roster.symlink_to(foreign)
        else:
            os.link(foreign, roster)

        with pytest.raises(RealPathRerankError, match="roster descriptor"):
            run_realpath_rerank(
                [_util_candidate()],
                seeds=[1, 2],
                work_dir=work_dir,
                ranking_path=tmp_path / f"{kind}.jsonl",
                config=_config(),
                resume=True,
            )
        # The foreign roster is untouched — refused before any seed was spent.
        assert foreign.read_text(encoding="utf-8") == '{"num_players": 99}'


def test_the_leg_log_is_a_recording_entry_too(tmp_path: Path) -> None:
    """Append mode follows a symlink (Codex review on PR #314).

    The round-16 no-links rule covered candidate directories and replays; the
    log that is supposed to BE this library's own ordering evidence was the one
    entry it did not cover, so every event would be written into whatever the
    link points at, outside the claimed work dir.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    outside = tmp_path / "someone-elses.jsonl"
    outside.write_text("untouched\n", encoding="utf-8")
    (work_dir / realpath.LEG_LOG_FILENAME).symlink_to(outside)

    log = realpath.RealPathLegLog(
        work_dir / realpath.LEG_LOG_FILENAME, tranche="1-2", invocation="000"
    )
    with pytest.raises(RealPathRerankError, match="is a SYMLINK"):
        log.emit("leg-start")
    assert outside.read_text(encoding="utf-8") == "untouched\n"

    # A REAL file still appends — this log is append-only by design.
    plain = realpath.RealPathLegLog(
        work_dir / "plain-log.jsonl", tranche="1-2", invocation="000"
    )
    plain.emit("leg-start")
    plain.emit("leg-done")
    assert len((work_dir / "plain-log.jsonl").read_text().splitlines()) == 2


def test_a_prescreen_rate_may_not_be_negative() -> None:
    """A per-meeting rate is non-negative (Codex review on PR #314).

    Finiteness alone let a negative rate be persisted and logged as blocker-4
    spend advice, where it reads as a validated quote discouraging real-path
    spend. A negative event rate is not a measurement.
    """

    for field in ("predicted_flags_per_meeting", "recorded_flags_fake_substrate"):
        payload: dict[str, object] = {
            "label": "arm-a",
            "weights_sha256": "a" * 64,
            "predicted_flags_per_meeting": 1.0,
            "predicted_floors_pass": True,
        }
        payload[field] = -1.0
        with pytest.raises(ValueError, match="per-meeting rate"):
            realpath.PreScreenQuote(**payload)  # type: ignore[arg-type]

    # Zero is a real measurement and still validates.
    assert (
        realpath.PreScreenQuote(
            label="arm-a",
            weights_sha256="a" * 64,
            predicted_flags_per_meeting=0.0,
            predicted_floors_pass=False,
            recorded_flags_fake_substrate=0.0,
        ).predicted_flags_per_meeting
        == 0.0
    )


def test_tranche_keys_are_injective_over_seed_sets() -> None:
    """The key IS the lookup, so it must be a function of the SET (Codex #314).

    It keys the flock, manifest discovery, directory ownership and the drift
    check. The endpoint-only form collided two ways: gapped lists sharing
    endpoints, and the same set in a different ORDER. The docstring's excuse —
    that the manifest records the exact seeds — was false, because finding the
    manifest is what the key is for.
    """

    # Contiguous names are byte-unchanged: every committed and fixture name.
    assert tranche_key([7]) == "7"
    assert tranche_key([1, 2]) == "1-2"
    assert tranche_key([4000, 4001, 4002]) == "4000-4002"

    # A function of the SET, not the caller's order.
    assert tranche_key([1, 2, 3]) == tranche_key([3, 2, 1]) == "1-3"

    # Injective across the shapes that previously collided.
    sets = ([4000, 4001, 4003], [4000, 4002, 4003], [4000, 4001, 4002, 4003])
    keys = [tranche_key(list(seeds)) for seeds in sets]
    assert len(set(keys)) == len(keys), keys

    # Full digest, never a prefix — round 12's rule, since any prefix is the
    # same collision bargain at a different probability.
    gapped = tranche_key([4000, 4001, 4003])
    assert len(gapped.removeprefix("4000-4003-")) == 64

    # And it stays a usable filename token.
    for seeds in ([1, 2], [4000, 4001, 4003], [-3, -1]):
        realpath._validate_invocation_token(tranche_key(list(seeds)))


def test_a_symlinked_replay_is_refused_before_it_is_read_or_written(
    tmp_path: Path,
) -> None:
    """The recorder creates real files, never links (Codex on PR #314).

    A dangling ``replay-seed-N.jsonl`` symlink read as simply missing, so the
    element re-recorded — and ``ReplayLog``'s lazy append then followed the link
    and created the replay at the external target, putting this leg's evidence
    outside the candidate directory it claimed and later scored through it.
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    candidate_dir = next(work_dir.glob("000-*"))
    outside = tmp_path / "outside.jsonl"
    replay = candidate_dir / "replay-seed-1.jsonl"
    replay.unlink()
    replay.symlink_to(outside)
    assert not replay.exists() and replay.is_symlink()

    with pytest.raises(RealPathRerankError, match="is a SYMLINK"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )
    # Nothing was written through the link.
    assert not outside.exists()


def test_a_stale_same_tranche_claim_is_still_a_reservation(tmp_path: Path) -> None:
    """A claim binds a directory to ``(tranche, label)`` (Codex on PR #314).

    Excluding the caller's whole tranche let a later fresh leg with a DISTINCT
    label but a colliding slug take a reservation an earlier manifest had
    published and never created (a leg that failed before recording). A resume
    of the original label then resolved its stale manifest to that same
    directory, passed the whole-stamp check, and ranked the newer candidate's
    games under the old name.

    Both directions are pinned here, because the two loose readings of this rule
    are each a defect this PR shipped once.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    # An earlier leg on THIS tranche claimed 000-arm-a for label "arm a" and
    # never created it. ``_safe_slug`` maps "arm a" and "arm-a" onto one slug.
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-1-2-000.json").write_text(
        json.dumps(
            {"tranche": "1-2", "candidates": [_claim_entry("arm a", "000-arm-a")]}
        ),
        encoding="utf-8",
    )
    assert not (work_dir / "000-arm-a").exists()

    result = run_realpath_rerank(
        [_util_candidate(label="arm-a")],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
    )
    assert result.rows
    # It stepped aside: the reservation is untouched and the new label recorded
    # somewhere else entirely.
    assert not (work_dir / "000-arm-a").exists()
    assert (work_dir / "001-arm-a").is_dir()

    # The OPPOSITE reading must not creep back: a fresh re-run of the SAME
    # (tranche, label) whose directory exists still collides rather than
    # stepping aside to a second copy (the round-11 defect).
    with pytest.raises(FileExistsError):
        run_realpath_rerank(
            [_util_candidate(label="arm-a")],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
        )


def test_ranking_path_may_not_name_another_legs_claimed_directory(
    tmp_path: Path,
) -> None:
    """A manifest CLAIM reserves a directory that need not exist yet (Codex #314).

    The slate-derived check covers only what THIS leg will create, so a name
    another tranche's manifest already claims — whose slug is not in this slate
    — passed. The leg then spent every game before the publish collided with
    that tranche's directory, or published a FILE into the reserved path and
    left the owning tranche permanently unable to resume.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / f"{realpath.LEG_MANIFEST_FILENAME_STEM}-9-9-000.json").write_text(
        json.dumps(
            {
                "tranche": "9-9",
                "candidates": [_claim_entry("other-arm", "000-other-arm")],
            }
        ),
        encoding="utf-8",
    )
    assert not (work_dir / "000-other-arm").exists()

    with pytest.raises(RealPathRerankError, match="already CLAIMED"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=work_dir / "000-other-arm",
            config=_config(),
        )
    # Refused before any game, and the other tranche's reservation is untouched.
    assert not (work_dir / "000-other-arm").exists()

    # An unclaimed top-level name still records (the round-13 no-over-reach).
    assert run_realpath_rerank(
        [_util_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=work_dir / "ranking-1-2.jsonl",
        config=_config(),
    ).rows


def test_resume_refuses_a_changed_game_map(tmp_path: Path) -> None:
    """The MAP is part of the protocol and is a caller argument, not a config field.

    Adopting seeds recorded on one topology while recording the rest on another
    yields one row combining two different games, with nothing in it saying so
    (Codex on PR #314).
    """

    work_dir = tmp_path / "work"
    _record_two_seeds(work_dir, tmp_path / "ranking-1.jsonl")
    altered = load_canonical_map().model_copy(update={"name": "A Different Map"})
    with pytest.raises(RealPathRerankError, match="different recording backend"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            game_map=altered,
            resume=True,
        )


def test_a_custom_runner_always_requires_an_identity(tmp_path: Path) -> None:
    """A callable cannot be compared across invocations (Codex on PR #314).

    Every custom factory reduced to the same ``True``, so two DIFFERENT stubs or
    provider wrappers compared equal and a resume could adopt bytes recorded by
    one runner while recording the rest through another.

    The requirement lands on the INITIAL invocation, not only the resuming one:
    a first run that recorded ``meeting_runner_identity: null`` would be
    permanently unresumable — a retry without an identity is refused, and a
    retry WITH one is refused as backend drift against the recorded null. That
    deadlock is the round-7 fix's own defect, and refusing up front is the only
    way both doors stay open.
    """

    def runner_factory() -> MeetingRunner:
        return build_default_meeting_runner()

    work_dir = tmp_path / "work"
    # The INITIAL run is refused when the runner is unnamed — before any game.
    with pytest.raises(RealPathRerankError, match="needs meeting_runner_identity"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-0.jsonl",
            config=_config(),
            meeting_runner_factory=runner_factory,
        )
    assert not work_dir.exists()

    run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
        meeting_runner_factory=runner_factory,
        meeting_runner_identity="stub-v1",
    )
    # A DIFFERENT named runner is refused as a backend change.
    with pytest.raises(RealPathRerankError, match="different recording backend"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            meeting_runner_factory=runner_factory,
            meeting_runner_identity="stub-v2",
            resume=True,
        )
    # The SAME named runner resumes cleanly.
    resumed = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-3.jsonl",
        config=_config(),
        meeting_runner_factory=runner_factory,
        meeting_runner_identity="stub-v1",
        resume=True,
    )
    assert [entry.resumed for entry in resumed.top().seed_telemetry] == [True]


def test_two_new_colliding_labels_get_distinct_dirs(tmp_path: Path) -> None:
    """Fresh directories are RESERVED as they are allocated (Codex on PR #314).

    Directories are not created until the recording loop runs, so two new
    labels sharing a slug both saw the same free name and were handed it. The
    manifest then mapped one directory to two labels: matching stamps reuse the
    first label's provider draw, differing stamps overwrite its evidence after
    its metrics were computed.
    """

    work_dir = tmp_path / "work"
    # The first run OCCUPIES 000-arm-a. That is what forces the first new label
    # to bump to 001-arm-a — the same ordinal the second new label starts at.
    run_realpath_rerank(
        [_util_candidate("arm.a")],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
    )
    assert (work_dir / "000-arm-a").is_dir()
    # Two NEW labels whose slugs collide with each other AND with the occupant.
    result = run_realpath_rerank(
        [_util_candidate("arm a"), _util_candidate("arm-a")],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
        resume=True,
    )
    assert len(result.rows) == 2
    manifest = json.loads(
        sorted((work_dir).glob("leg-1-*.json"))[-1].read_text(encoding="utf-8")
    )
    dirs = [entry["dir"] for entry in manifest["candidates"]]
    assert len(set(dirs)) == len(dirs), f"two labels share a directory: {dirs}"
    for name in dirs:
        assert (work_dir / name).is_dir()


def test_a_partial_leg_manifest_never_blocks_a_later_resume(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Leg manifests publish atomically (Codex on PR #314).

    An interrupt between the exclusive create and the write left a partial
    manifest, and ``_refuse_protocol_drift`` refuses an unreadable one — so
    every later resume died on evidence that had to be deleted by hand.
    """

    import os as _os

    work_dir = tmp_path / "work"
    real_fsync = _os.fsync

    def _boom(fd: int) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(_os, "fsync", _boom)
    with pytest.raises(OSError, match="disk full"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-1.jsonl",
            config=_config(),
        )
    monkeypatch.setattr(_os, "fsync", real_fsync)

    # No manifest was published, so nothing poisons the next invocation.
    assert list(work_dir.glob("leg-*.json")) == []
    result = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-2.jsonl",
        config=_config(),
    )
    assert result.rows


@pytest.mark.parametrize(
    "knob",
    [
        "AILIBI_OLLAMA_HOST",
        "AILIBI_OLLAMA_SEED",
        "AILIBI_OLLAMA_NUM_CTX",
    ],
)
def test_every_effective_backend_knob_rides_the_resume_identity(knob: str) -> None:
    """The endpoint, generation seed and context window are all protocol (#314).

    ``llm/provider.py`` builds the recorder from more than the provider and
    model names, so comparing only provider+models left one ranking row able to
    combine recordings from different effective backends. Exercised against the
    provider that READS these knobs — under the fake provider they are dead
    settings, and refusing a resume over one would forfeit the verified-resume
    benefit for nothing (Codex round 9).
    """

    game_map = load_canonical_map()

    def _identity(**env: str) -> dict[str, object]:
        return realpath._recording_backend_identity(
            custom_runner=False, game_map=game_map, num_players=4, environment=env
        )

    value = "7" if knob.endswith(("SEED", "NUM_CTX")) else "some-other-endpoint:1234"
    assert _identity(AILIBI_LLM_PROVIDER="ollama", **{knob: value}) != _identity(
        AILIBI_LLM_PROVIDER="ollama"
    )


# --------------------------------------------------------------------------- #
# 25. THE CREW ARM (Task 18.32) — crew candidates, the frozen-opponent seam,   #
#     dual stamps, the v3 row, and the resume's opponent drift.                #
# --------------------------------------------------------------------------- #

_CREW_V1_DIR = Path("training/artifacts/crew/crew-utility-es")
_CREW_V2_DIR = Path("training/artifacts/crew/crew-owned-tasks-es")
_CREW_V1_ENCODER = "crew-option-features-v1"
_CREW_V2_ENCODER = "crew-option-features-v2"


def _crew_candidate(
    label: str = "crew-owned-tasks-es", *, owned_tasks: bool = True
) -> RealPathCandidate:
    """A committed crew champion as a re-rank candidate.

    The owned-task (v2) family is the default fixture because it fires meetings
    on the cheap 4p1i roster over seeds 1-2 and therefore passes the validity
    gate; the 22-weight v1 champion drives the same seeds to a kill-out with no
    meeting, which is a real behavioural difference and not something a stamp
    test should paper over.
    """

    directory = _CREW_V2_DIR if owned_tasks else _CREW_V1_DIR
    return RealPathCandidate(
        label=label,
        genome=load_candidate_weights(directory),
        encoder_version=_CREW_V2_ENCODER if owned_tasks else _CREW_V1_ENCODER,
        policy_id=directory.name,
        method="crew-option-scorer-es",
    )


def _freeze_opponent(
    artifact_dir: Path, *, policy_id: str = "frozen-utility-es"
) -> Path:
    """Freeze the committed impostor utility champion as a loadable artifact.

    The four-file shape the seam consumes, written by its own writer
    (:func:`training.coevo.hall_of_fame.write_loadable_artifact`) rather than by
    hand — a hand-built fixture would prove the reader accepts a shape nothing
    produces.
    """

    write_loadable_artifact(
        artifact_dir,
        _util_weights(),
        policy_id=policy_id,
        method="utility-scorer-es",
        encoder_version=_UTIL_ENCODER,
    )
    return artifact_dir


def test_crew_candidates_validate_and_refuse_a_hidden_width() -> None:
    """Both crew families are candidates; neither takes a masked-MLP width.

    The crew scorer rebuilds through ``build_crew_scorer``, which has no head to
    size, so a declared ``hidden`` is a width its builder does not have — the
    same false provenance ``training/coevo/driver.py``'s ``_validate_side``
    refuses one layer up.
    """

    game_map = load_canonical_map()
    for owned_tasks in (False, True):
        candidate = _crew_candidate(
            label=f"crew-{owned_tasks}", owned_tasks=owned_tasks
        )
        # Constructing the factory IS the rebuild assertion: the internal
        # post-check pins the rebuilt policy's encoder identity against the
        # declared one, so a v2 genome rebuilt through the v1 menu fails here.
        assert callable(_build_agent_factory(candidate, game_map=game_map))
        with pytest.raises(ValidationError, match="crew family .* takes no hidden"):
            RealPathCandidate(
                label="wide",
                genome=candidate.genome,
                encoder_version=candidate.encoder_version,
                hidden=8,
                policy_id="p",
                method="m",
            )


def test_a_crew_leg_records_dual_stamps_against_a_frozen_opponent(
    tmp_path: Path,
) -> None:
    """The whole arm, end to end: two identities on one recording (18.32).

    A crew candidate is interposed through the CREW slot while a frozen impostor
    artifact holds the impostor slot, and each side's stamp is READ BACK from
    the recorded bytes into its own DISTINCT row field. The two are pinned
    against the bytes themselves — not against the launch config — so the row
    cannot report provenance the recording does not carry.
    """

    opponent = _freeze_opponent(tmp_path / "opponent")
    work_dir = tmp_path / "work"
    ranking_path = tmp_path / "ranking.jsonl"
    result = run_realpath_rerank(
        [_crew_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=ranking_path,
        config=_config(),
        opponent_artifact=opponent,
    )

    row = result.top()
    assert row.schema_version == SCHEMA_VERSION == "realpath-rerank-v3"
    # The CANDIDATE is the crew side; the impostor side is the frozen opponent.
    assert row.crew_stamp is not None
    assert row.crew_stamp.encoder_version == _CREW_V2_ENCODER
    assert row.crew_stamp.weights_sha256 == row.weights_sha256
    assert row.crew_stamp_verified_games == 2
    assert row.crew_stamp_uniform is True
    assert row.crew_stamp_equals_computed_digest is True
    assert row.stamp.policy_id == "frozen-utility-es"
    assert row.stamp.weights_sha256 == _UTIL_DIGEST
    assert row.stamp_verified_games == 2
    assert row.opponent_weights_sha256 == _UTIL_DIGEST
    assert row.opponent_stamp == row.stamp
    # ... and the two identities are DISTINCT, which is what makes neither
    # re-readable as the other's.
    assert row.crew_stamp.policy_id != row.stamp.policy_id
    assert row.crew_stamp.weights_sha256 != row.stamp.weights_sha256

    # READ BACK FROM BYTES, in the two distinct replay slots.
    candidate_dir = work_dir / "000-crew-owned-tasks-es"
    for seed in (1, 2):
        stamps = read_policy_stamps(candidate_dir / f"replay-seed-{seed}.jsonl")
        assert stamps.crew is not None and stamps.crew == row.crew_stamp
        assert stamps.tactical is not None and stamps.tactical == row.stamp

    # The opponent identity rides the manifest and the leg-start event too.
    manifest = json.loads(
        sorted(work_dir.glob("leg-1-2-*.json"))[0].read_text(encoding="utf-8")
    )
    assert manifest["opponent"] == {
        "stamp": row.stamp.model_dump(mode="json"),
        "weights_sha256": _UTIL_DIGEST,
    }
    events = [
        json.loads(line)
        for line in (work_dir / LEG_LOG_FILENAME).read_text().splitlines()
    ]
    start = next(event for event in events if event["event"] == "leg-start")
    assert start["side"] == "crew"
    assert start["opponent"] == manifest["opponent"]
    assert start["opponent_artifact"] == str(opponent)

    # The mirror of the comparator cell's proof: these bytes DO name an impostor
    # side, so certifying them as scripted-FSM games fails loud rather than
    # quietly attributing an opponent's play to the untouched anchor.
    with pytest.raises(RealPathStampError, match="froze no opponent"):
        realpath._verify_stamps(
            candidate_dir,
            seeds=(1, 2),
            expected_digest=None,
            expected_crew_digest=row.weights_sha256,
            label="crew-owned-tasks-es",
        )


def test_the_comparator_cell_proves_the_impostor_side_is_scripted(
    tmp_path: Path,
) -> None:
    """``opponent_artifact=None`` records NO impostor stamp — and proves it.

    An absent impostor stamp MEANS the scripted FSM (replay.py), so the row
    carries the canonical FSM-default stamp with ZERO verified games. The
    recorder does not assume that absence: ``_verify_stamps`` refuses any
    impostor stamp on a leg that froze no opponent.
    """

    work_dir = tmp_path / "work"
    result = run_realpath_rerank(
        [_crew_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(),
    )
    row = result.top()
    assert row.stamp == fsm_default_tactical_policy_stamp()
    assert row.stamp_verified_games == 0
    assert row.opponent_weights_sha256 is None
    assert row.opponent_stamp is None
    assert row.crew_stamp is not None
    assert row.crew_stamp_verified_games == 2
    assert row.validity_passed is True

    candidate_dir = work_dir / "000-crew-owned-tasks-es"
    for seed in (1, 2):
        stamps = read_policy_stamps(candidate_dir / f"replay-seed-{seed}.jsonl")
        assert stamps.tactical is None
        assert stamps.crew is not None

    # The proof, not the assumption. These bytes cannot be certified as anything
    # but the comparator cell: claiming a frozen opponent over them fails loud,
    # because nothing in the recording names one.
    with pytest.raises(RealPathStampError, match="no tactical policy stamp"):
        realpath._verify_stamps(
            candidate_dir,
            seeds=(1, 2),
            expected_digest=_UTIL_DIGEST,
            expected_crew_digest=row.weights_sha256,
            label="crew-owned-tasks-es",
        )
    # ... and so is a CREW stamp on a leg that installs no crew policy.
    with pytest.raises(RealPathStampError, match="but this leg installs no crew"):
        realpath._verify_stamps(
            candidate_dir,
            seeds=(1, 2),
            expected_digest=None,
            expected_crew_digest=None,
            label="crew-owned-tasks-es",
        )
    # A crew digest naming other bytes is the 17.14 conflation guard, crew-side.
    with pytest.raises(RealPathStampError, match="read-back crew weights_sha256"):
        realpath._verify_stamps(
            candidate_dir,
            seeds=(1, 2),
            expected_digest=None,
            expected_crew_digest="0" * 64,
            label="crew-owned-tasks-es",
        )


def test_a_leg_is_homogeneous(tmp_path: Path) -> None:
    """Crew and impostor candidates never share a leg (18.32).

    One leg publishes ONE ranking under one protocol. A crew candidate's score
    is read against a frozen impostor side and an impostor candidate's against a
    scripted crew, so ranking them together would present two different
    measurements as one total order.
    """

    work_dir = tmp_path / "work"
    work_dir.mkdir()
    ranking_path = tmp_path / "ranking.jsonl"
    with pytest.raises(ValueError, match="a leg is homogeneous"):
        run_realpath_rerank(
            [_crew_candidate(), _util_candidate()],
            seeds=[1],
            work_dir=work_dir,
            ranking_path=ranking_path,
            config=_config(),
        )
    assert list(work_dir.iterdir()) == []
    assert not ranking_path.exists()


def test_the_opponent_seam_refuses_before_any_spend(tmp_path: Path) -> None:
    """Every frozen-opponent refusal fires BEFORE the first game (18.32).

    The seam exists to freeze the side the candidate does NOT play, and it is
    the last thing a 30-40 h crew leg should discover halfway through. Each case
    leaves the work dir untouched and no ranking behind.
    """

    def _run(
        candidates: Sequence[RealPathCandidate],
        *,
        opponent_artifact: Path | None,
        work_dir: Path,
    ) -> None:
        run_realpath_rerank(
            list(candidates),
            seeds=[1],
            work_dir=work_dir,
            ranking_path=work_dir.parent / f"{work_dir.name}-ranking.jsonl",
            config=_config(),
            opponent_artifact=opponent_artifact,
        )

    # 1. A CREW artifact in the impostor slot — the 18.19 conflation, most
    #    expensive form. Frozen through the same writer, declaring its own crew
    #    family, so the refusal is on the artifact and not on a broken fixture.
    crew_artifact = tmp_path / "crew-opponent"
    write_loadable_artifact(
        crew_artifact,
        load_candidate_weights(_CREW_V2_DIR),
        policy_id="crew-owned-tasks-es",
        method="crew-option-scorer-es",
        encoder_version=_CREW_V2_ENCODER,
    )
    with pytest.raises(RealPathRerankError, match="names a CREW policy"):
        _run(
            [_crew_candidate()],
            opponent_artifact=crew_artifact,
            work_dir=tmp_path / "w-crew-opponent",
        )

    # 2. An IMPOSTOR-family leg cannot take one at all: the candidate already
    #    occupies the impostor slot.
    good = _freeze_opponent(tmp_path / "opponent")
    with pytest.raises(ValueError, match="IMPOSTOR-family leg"):
        _run(
            [_util_candidate()],
            opponent_artifact=good,
            work_dir=tmp_path / "w-impostor-leg",
        )

    # 3. A missing artifact dir.
    with pytest.raises(RealPathRerankError, match="is not a directory"):
        _run(
            [_crew_candidate()],
            opponent_artifact=tmp_path / "nowhere",
            work_dir=tmp_path / "w-missing",
        )

    # 4. A CORRUPT stamp.json (valid dir, unreadable identity).
    corrupt = _freeze_opponent(tmp_path / "corrupt-stamp")
    (corrupt / "stamp.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(RealPathRerankError, match="is not valid JSON"):
        _run(
            [_crew_candidate()],
            opponent_artifact=corrupt,
            work_dir=tmp_path / "w-corrupt",
        )

    # 5. WEIGHTS DRIFT from the sidecar — the artifact no longer hashes to what
    #    it claims, so nothing on disk names the bytes that would play.
    drifted = _freeze_opponent(tmp_path / "drifted")
    weights = json.loads((drifted / "weights.json").read_text(encoding="utf-8"))
    assert isinstance(weights, list) and weights
    weights[0] = "0x1.0000000000000p+0"
    (drifted / "weights.json").write_text(json.dumps(weights) + "\n", encoding="utf-8")
    with pytest.raises(RealPathRerankError, match="weights load/verify failed"):
        _run(
            [_crew_candidate()],
            opponent_artifact=drifted,
            work_dir=tmp_path / "w-drifted",
        )

    # 6. A stamp naming OTHER bytes than the sidecar records (17.14).
    mis_stamped = _freeze_opponent(tmp_path / "mis-stamped")
    stamp = json.loads((mis_stamped / "stamp.json").read_text(encoding="utf-8"))
    stamp["weights_sha256"] = "0" * 64
    (mis_stamped / "stamp.json").write_text(json.dumps(stamp), encoding="utf-8")
    with pytest.raises(RealPathRerankError, match="17.14 conflation guard"):
        _run(
            [_crew_candidate()],
            opponent_artifact=mis_stamped,
            work_dir=tmp_path / "w-mis-stamped",
        )

    # 7. The candidate and the opponent must be DISTINCT identities: two stamps
    #    on one recording that share a policy_id are mutually re-readable.
    collider = _freeze_opponent(tmp_path / "collider", policy_id="crew-owned-tasks-es")
    with pytest.raises(RealPathRerankError, match="cross-stamp guard"):
        _run(
            [_crew_candidate()],
            opponent_artifact=collider,
            work_dir=tmp_path / "w-collider",
        )

    # NOTHING was recorded by any of them.
    for work_dir in sorted(tmp_path.glob("w-*")):
        if work_dir.is_dir():
            assert list(work_dir.iterdir()) == [], f"{work_dir} holds recordings"
    assert not list(tmp_path.glob("w-*-ranking.jsonl"))


def test_a_v3_crew_row_round_trips_and_refuses_a_contradiction(
    tmp_path: Path,
) -> None:
    """The ``-v3`` row is JSONL-stable, and its two proof blocks must agree."""

    opponent = _freeze_opponent(tmp_path / "opponent")
    result = run_realpath_rerank(
        [_crew_candidate()],
        seeds=[1],
        work_dir=tmp_path / "work",
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(),
        opponent_artifact=opponent,
    )
    row = result.top()
    assert RealPathRerankRow.model_validate_json(row.to_json_line()) == row
    payload = json.loads(row.to_json_line())
    assert payload["schema_version"] == "realpath-rerank-v3"
    assert set(payload) >= {
        "crew_stamp",
        "crew_stamp_equals_computed_digest",
        "crew_stamp_uniform",
        "crew_stamp_verified_games",
        "opponent_stamp",
        "opponent_weights_sha256",
    }

    # An impostor-only row keeps the exact ``-v2`` shape apart from the version:
    # every crew-arm field is present but empty, never populated by default.
    impostor = run_realpath_rerank(
        [_util_candidate()],
        seeds=[1],
        work_dir=tmp_path / "work-impostor",
        ranking_path=tmp_path / "ranking-impostor.jsonl",
        config=_config(),
    ).top()
    assert impostor.crew_stamp is None
    assert impostor.crew_stamp_verified_games == 0
    assert impostor.crew_stamp_uniform is False
    assert impostor.crew_stamp_equals_computed_digest is False
    assert impostor.opponent_weights_sha256 is None
    assert impostor.opponent_stamp is None

    # A crew proof without a crew stamp claims an identity nothing proved.
    with pytest.raises(ValidationError, match="no crew_stamp carries no crew proof"):
        RealPathRerankRow.model_validate(
            {**payload, "crew_stamp": None, "crew_stamp_verified_games": 2}
        )
    # ... and a crew stamp with zero verified games is the mirror claim.
    with pytest.raises(ValidationError, match="at least one decisive game"):
        RealPathRerankRow.model_validate({**payload, "crew_stamp_verified_games": 0})
    # The opponent's identity is whole or absent.
    with pytest.raises(ValidationError, match="whole or absent"):
        RealPathRerankRow.model_validate({**payload, "opponent_stamp": None})
    # ... and its stamp names its own bytes.
    with pytest.raises(ValidationError, match="17.14 conflation guard"):
        RealPathRerankRow.model_validate(
            {**payload, "opponent_weights_sha256": "0" * 64}
        )


def test_resume_refuses_a_changed_frozen_opponent(tmp_path: Path) -> None:
    """A crew leg is evidence about the opponent it was played against (18.32).

    Adopting bytes recorded against one impostor side into a row claiming
    another — or claiming the scripted-FSM comparator cell — relabels the arm,
    and none of it rides ``config`` or the recording backend. The matched resume
    still skips every verified element, so the refusal is about the opponent and
    not about resume being broken for crew legs.
    """

    first = _freeze_opponent(tmp_path / "opponent-a")
    second = _freeze_opponent(tmp_path / "opponent-b", policy_id="frozen-policy-es")
    work_dir = tmp_path / "work"
    run_realpath_rerank(
        [_crew_candidate()],
        seeds=[1, 2],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking-1.jsonl",
        config=_config(),
        opponent_artifact=first,
    )

    def _resume(opponent_artifact: Path | None, ranking: str) -> RealPathRerankResult:
        return run_realpath_rerank(
            [_crew_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / ranking,
            config=_config(),
            resume=True,
            opponent_artifact=opponent_artifact,
        )

    # Dropping the opponent for the comparator cell.
    with pytest.raises(RealPathRerankError, match="different frozen opponent"):
        _resume(None, "ranking-2.jsonl")
    # Swapping it for another artifact — same genome BYTES, different identity,
    # which is exactly the case a digest-only comparison would miss.
    with pytest.raises(RealPathRerankError, match="different frozen opponent"):
        _resume(second, "ranking-3.jsonl")
    # The MATCHED resume adopts the recorded bytes, so the refusals above are
    # about the opponent rather than about crew legs being unresumable.
    resumed = _resume(first, "ranking-4.jsonl")
    assert [entry.resumed for entry in resumed.top().seed_telemetry] == [True, True]
    assert resumed.top().crew_stamp_verified_games == 2


def test_resume_re_records_a_crew_element_whose_stamps_do_not_match(
    tmp_path: Path,
) -> None:
    """The conjunctive skip predicate reads BOTH sides (18.32).

    A crew leg's recordings must carry this candidate's crew stamp AND the
    impostor side this leg installs. A replay recorded against the scripted FSM
    is not a replay recorded against a frozen opponent, however complete it is —
    so an element whose impostor slot disagrees re-records rather than being
    adopted.
    """

    opponent = _freeze_opponent(tmp_path / "opponent")
    work_dir = tmp_path / "work"
    result = run_realpath_rerank(
        [_crew_candidate()],
        seeds=[1],
        work_dir=work_dir,
        ranking_path=tmp_path / "ranking.jsonl",
        config=_config(),
        opponent_artifact=opponent,
    )
    replay = work_dir / "000-crew-owned-tasks-es" / "replay-seed-1.jsonl"
    crew_stamp = result.top().crew_stamp
    assert crew_stamp is not None

    # Recorded WITH an opponent, examined as a comparator-cell element.
    reason = realpath._resume_skip_reason(
        replay,
        expected_stamp=None,
        expected_crew_stamp=crew_stamp,
        config=_config(),
    )
    assert reason is not None and "carry an IMPOSTOR stamp" in reason
    # ... and as an impostor leg's element, whose bytes must carry NO crew stamp.
    reason = realpath._resume_skip_reason(
        replay,
        expected_stamp=result.top().stamp,
        expected_crew_stamp=None,
        config=_config(),
    )
    assert reason is not None and "carry a CREW stamp" in reason
    # A crew stamp naming another policy is drift on the crew side.
    reason = realpath._resume_skip_reason(
        replay,
        expected_stamp=result.top().stamp,
        expected_crew_stamp=crew_stamp.model_copy(update={"policy_id": "someone-else"}),
        config=_config(),
    )
    assert reason is not None and "read-back crew stamp policy_id" in reason
    # The leg's OWN pairing verifies.
    assert (
        realpath._resume_skip_reason(
            replay,
            expected_stamp=result.top().stamp,
            expected_crew_stamp=crew_stamp,
            config=_config(),
        )
        is None
    )
