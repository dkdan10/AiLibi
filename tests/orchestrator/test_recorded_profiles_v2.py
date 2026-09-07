"""Versioned evidence refuses forged clocks without reinterpreting older bytes."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from meetings.evidence_profile import MeetingEvidenceProfile
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import (
    ReplayEntry,
    ReplayLog,
    recorded_experiment_config,
    recorded_temporal_observation_version,
    substrate_flag_snapshot,
)


@pytest.mark.parametrize("value", [True, False, 2.0, "2", 3, 0])
def test_tick_version_rejects_unknown_and_coerced_identity(value: object) -> None:
    with pytest.raises(ValidationError):
        ReplayEntry.model_validate(
            {
                "game_id": "test",
                "tick": 0,
                "actions": [],
                "state_hash": "hash",
                "temporal_observation_version": value,
            }
        )


def test_explicit_v2_and_mixed_v1_prefixes_are_distinct() -> None:
    first = ReplayEntry(
        game_id="test",
        tick=0,
        actions=(),
        state_hash="hash",
        temporal_observation_version=2,
    )
    assert recorded_temporal_observation_version([first]) == 2
    old = first.model_copy(update={"tick": 1, "temporal_observation_version": 1})
    with pytest.raises(ValueError, match="mixed temporal"):
        recorded_temporal_observation_version([first, old])


def test_new_evidence_cannot_be_stamped_over_legacy_clock() -> None:
    first = ReplayEntry(
        game_id="test",
        tick=0,
        actions=(),
        state_hash="hash",
        temporal_observation_version=1,
        experiment_config=RecordedExperimentConfig(
            format_version=2, evidence_reasoning_version=2
        ),
    )
    with pytest.raises(ValueError, match="require temporal"):
        recorded_experiment_config([first])
    assert (
        recorded_experiment_config(
            [first.model_copy(update={"temporal_observation_version": 2})]
        )
        == first.experiment_config
    )


def test_writer_refuses_conflicting_flag_before_replacing_output(
    tmp_path: Path,
) -> None:
    path = tmp_path / "recording.jsonl"
    path.write_text("prior evidence")
    flags = substrate_flag_snapshot({})
    with pytest.raises(ValueError, match="supplied substrate_flags"):
        ReplayLog(
            path,
            "test",
            force=True,
            temporal_observation_version=2,
            substrate_flags=flags,
        )
    assert path.read_text() == "prior evidence"


def test_meeting_profile_captures_explicit_versions_without_environment_drift() -> None:
    env = {
        "AILIBI_EVIDENCE_REASONING": "2",
        "AILIBI_PUBLIC_ACCOUNTS": "1",
        "AILIBI_ATTRIBUTED_TESTIMONY": "1",
    }
    profile = MeetingEvidenceProfile.from_environment(env)
    env.clear()
    assert profile.evidence_reasoning_version == 2
    assert profile.public_account_version == profile.attributed_testimony_version == 1
    assert MeetingEvidenceProfile.from_environment(env) == MeetingEvidenceProfile()
