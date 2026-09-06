"""Versioned experiment identity survives partials without relabelling defaults."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from orchestrator.experiment_config import (
    RecordedExperimentConfig,
    normalize_experiment_config,
    validate_recorded_experiment_config,
)


def test_default_config_has_no_recorded_field() -> None:
    default = RecordedExperimentConfig()
    assert default.is_default
    assert normalize_experiment_config(default) is None
    assert normalize_experiment_config(None) is None
    assert validate_recorded_experiment_config([None, None]) is None


@pytest.mark.parametrize(
    "field",
    ["evidence_reasoning_version", "bounded_rebuttal_version"],
)
def test_reasoning_versions_are_independently_selectable(field: str) -> None:
    config = RecordedExperimentConfig.model_validate({field: 1})
    assert not config.is_default
    assert normalize_experiment_config(config) is config
    assert validate_recorded_experiment_config([config, config]) == config
    assert (
        validate_recorded_experiment_config(
            [config], terminal_config=config, terminal_present=True
        )
        == config
    )


@pytest.mark.parametrize(
    "raw",
    [
        {"format_version": 3},
        {"format_version": True},
        {"evidence_reasoning_version": "1"},
        {"bounded_rebuttal_version": True},
        {"redistribution_policy": "random"},
        {"self_report": "false"},
        {"anti_oscillation": True},
        {"unknown_arm": True},
        {"evidence_reasoning_version": 2},
        {"public_account_version": 1},
        {"attributed_testimony_version": 1},
        {"format_version": 2, "bounded_rebuttal_version": 2},
        {"format_version": 2, "public_account_version": True},
        {"format_version": 2, "attributed_testimony_version": "1"},
    ],
)
def test_unknown_or_coerced_configuration_is_rejected(raw: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RecordedExperimentConfig.model_validate(raw)


def test_enabled_partial_cannot_silently_switch_or_claim_default_on_completion() -> (
    None
):
    config = RecordedExperimentConfig(crew_idle_policy="patrol")
    assert validate_recorded_experiment_config([config]) == config
    for rows in ([config, None], [None, config]):
        with pytest.raises(ValueError, match="changes between tick rows"):
            validate_recorded_experiment_config(rows)
    with pytest.raises(ValueError, match="disagrees with tick rows"):
        validate_recorded_experiment_config([config], terminal_present=True)
    with pytest.raises(ValueError, match="disagrees with tick rows"):
        validate_recorded_experiment_config(
            [None], terminal_config=config, terminal_present=True
        )


def test_config_is_immutable_and_can_select_independent_arms_together() -> None:
    config = RecordedExperimentConfig(
        redistribution_policy="least_remaining_work",
        meeting_reset="hub_with_grace",
        vent_exit_policy="observed_risk",
        bounded_rebuttal_version=1,
    )
    assert config.evidence_reasoning_version is None
    assert config.crew_idle_policy == "hub_wait"
    assert config.bounded_rebuttal_version == 1
    with pytest.raises(ValidationError, match="frozen"):
        config.self_report = True


def test_version_two_profiles_preserve_version_one_encoding_and_typed_schema() -> None:
    legacy = RecordedExperimentConfig(evidence_reasoning_version=1)
    assert "public_account_version" not in legacy.model_dump()
    assert "attributed_testimony_version" not in legacy.model_dump()
    candidate = RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        public_account_version=1,
        attributed_testimony_version=1,
    )
    assert candidate.model_dump()["public_account_version"] == 1
    assert (
        RecordedExperimentConfig.model_validate_json(candidate.model_dump_json())
        == candidate
    )
    assert (
        "public_account_version"
        in RecordedExperimentConfig.model_json_schema(mode="serialization")[
            "properties"
        ]
    )
    assert (
        normalize_experiment_config(RecordedExperimentConfig(format_version=2)) is None
    )
