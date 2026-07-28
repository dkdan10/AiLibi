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

import asyncio
import fcntl
import json
import os
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pytest
from pydantic import ValidationError

from agents.base import AgentInterface
from engine.entities import PlayerId
from engine.world import Map, WorldState, load_canonical_map
from eval.balance_eval import _resolve_game_budget
from llm.budget import BudgetExceededError
from meetings.manager import MeetingTrigger
from orchestrator.game import (
    MeetingArtifacts,
    MeetingRunner,
    build_default_meeting_runner,
)
from orchestrator.replay import read_tactical_policy_stamp
import training.realpath as realpath
from training.bakeoff.es import ESResult
from training.bakeoff.harness import load_candidate_weights
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

    monkeypatch.setenv(knob, "anthropic" if knob == "AILIBI_LLM_PROVIDER" else "9b-alt")
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
            custom_runner=False, game_map=game_map, environment=env
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
            AILIBI_LLM_PROVIDER=provider, AILIBI_PROMPT_SET="9b-alt"
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
    monkeypatch.setenv("AILIBI_PROMPT_SET", "some-other-set")
    with pytest.raises(RealPathRerankError, match="different recording backend"):
        run_realpath_rerank(
            [_util_candidate()],
            seeds=[1, 2],
            work_dir=work_dir,
            ranking_path=tmp_path / "ranking-2.jsonl",
            config=_config(),
            resume=True,
        )


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
            custom_runner=False, game_map=game_map, environment=env
        )

    value = "7" if knob.endswith(("SEED", "NUM_CTX")) else "some-other-endpoint:1234"
    assert _identity(AILIBI_LLM_PROVIDER="ollama", **{knob: value}) != _identity(
        AILIBI_LLM_PROVIDER="ollama"
    )
