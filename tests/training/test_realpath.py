"""Definition-of-done tests for the real-path re-rank recorder (Task 18.17).

These run on the deterministic FAKE provider over the cheap 4p1i roster (the
committed baseline-5 floor block covers it, eval/watchability.py). Seeds 1 and 2
each fire exactly one meeting through the committed utility-es and policy-es
genomes on this roster and every game ends decisively (so its ``game_over``
record carries a read-back-able stamp) — verified empirically while authoring.

The tests pin the DoD contracts: K×N recording + scoring into ranking rows, the
stamp read back FROM BYTES, a hung meeting failing its seed loudly within the
timeout, the retry budget re-recording after a timeout, jsonl round-trip, the
champion-trace helper, and fail-loud input validation.
"""

from __future__ import annotations

import asyncio
import json
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
from meetings.manager import MeetingTrigger
from orchestrator.game import (
    MeetingArtifacts,
    MeetingRunner,
    build_default_meeting_runner,
)
from orchestrator.replay import read_tactical_policy_stamp
from training.bakeoff.es import ESResult
from training.bakeoff.harness import load_candidate_weights
from training.realpath import (
    MODE_CHAMPION_TRACE,
    MODE_TOP_K,
    SCHEMA_VERSION,
    RealPathCandidate,
    RealPathMeetingTimeoutError,
    RealPathRerankConfig,
    RealPathRerankResult,
    RealPathRerankRow,
    RealPathSeedExhaustedError,
    _TimeoutMeetingRunner,
    candidates_from_champion_trace,
    run_realpath_rerank,
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
