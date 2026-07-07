"""Tests for the policy determinism harness (Task 15.10)."""

from __future__ import annotations

import json

import pytest

from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from agents.memory.store import AgentMemory
from agents.tactical.features import ENCODER_VERSION
from training.determinism import (
    FramePolicy,
    PolicyDeterminismReport,
    PolicyFrame,
    ReferenceFrozenPolicy,
    build_reference_policy,
    reference_determinism_report,
    run_policy_determinism,
)


def test_reference_policy_is_frame_policy() -> None:
    policy = build_reference_policy()
    assert isinstance(policy, ReferenceFrozenPolicy)
    assert isinstance(policy, FramePolicy)
    assert policy.encoder_version == ENCODER_VERSION


def test_reference_policy_is_deterministic_4p1i() -> None:
    report = reference_determinism_report(seeds=[0, 1])
    assert report.deterministic is True
    assert report.encoder_version == ENCODER_VERSION
    assert report.num_frames > 0
    assert report.num_state_hashes > 0
    assert report.seeds == (0, 1)


def test_reference_policy_is_deterministic_9p2i() -> None:
    # The 9-player roster exercises all 9 belief/last-seen slots inside a real
    # game, not just the 4p1i default.
    policy = build_reference_policy(genome_seed=3)
    report = run_policy_determinism(
        policy,
        seeds=[0],
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=2,
    )
    assert report.deterministic is True
    assert report.num_players == 9
    assert report.num_frames > 0


def test_report_to_json_is_machine_readable() -> None:
    report = reference_determinism_report(seeds=[0])
    payload = json.loads(report.to_json())
    assert payload["encoder_version"] == ENCODER_VERSION
    assert payload["deterministic"] is True
    assert payload["frame_stream_sha256"] == report.frame_stream_sha256
    assert payload["state_hash_sha256"] == report.state_hash_sha256
    assert payload["seeds"] == [0]
    # Both digests are hex SHA-256.
    assert len(report.frame_stream_sha256) == 64
    assert len(report.state_hash_sha256) == 64


def test_two_reference_reports_agree_across_independent_runs() -> None:
    # The frozen genome is a pure function of genome_seed, so two INDEPENDENT
    # harness invocations must land on the same digests — the frozen-genome
    # full-game equality is stable, not just self-consistent within one call.
    first = reference_determinism_report(seeds=[0], genome_seed=7)
    second = reference_determinism_report(seeds=[0], genome_seed=7)
    assert first.frame_stream_sha256 == second.frame_stream_sha256
    assert first.state_hash_sha256 == second.state_hash_sha256


class _DriftingPolicy:
    """A deliberately NON-deterministic policy: a call counter leaks into logits.

    The counter accumulates across the harness's two runs (the policy instance is
    reused), so the second run's ``(features, logits, intent)`` stream differs from
    the first even though the intents — pure FSM delegation — drive an identical
    game. This proves the harness CATCHES a determinism violation at the artifact
    (a gate that cannot fail is not a gate).
    """

    encoder_version = ENCODER_VERSION

    def __init__(self) -> None:
        self._counter = 0.0

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
    ) -> PolicyFrame:
        self._counter += 1.0
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(0.0,),
            logits=(self._counter,),  # drifts across runs — non-deterministic
            intent=fsm_intent,
        )


def test_harness_detects_nondeterministic_policy() -> None:
    report = run_policy_determinism(_DriftingPolicy(), seeds=[0])
    assert report.deterministic is False
    # The trajectory (intents = FSM) is identical, so the STATE hashes still
    # match; only the frame stream drifted. Both must be checked — the harness
    # ANDs them, so a frame-only drift is still a failure.
    assert report.num_state_hashes > 0


def test_run_policy_determinism_requires_seeds() -> None:
    with pytest.raises(ValueError, match="at least one seed"):
        run_policy_determinism(build_reference_policy(), seeds=[])


def test_report_is_public_type() -> None:
    report = reference_determinism_report(seeds=[0])
    assert isinstance(report, PolicyDeterminismReport)
