"""Describe independently selectable experiments without changing the baseline.

The orchestrator decomposes this recording contract into engine and agent
arguments. Neither side imports this privileged wiring module. Missing config
means the historical defaults; an enabled config must agree across a recording.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictBool, field_validator


class RecordedExperimentConfig(BaseModel):
    """A closed, immutable description of the offline experimental arms."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    format_version: Literal[1] = 1
    redistribution_policy: Literal["lowest_id", "least_remaining_work"] = "lowest_id"
    meeting_reset: Literal["preserve", "hub_with_grace"] = "preserve"
    crew_idle_policy: Literal["hub_wait", "patrol", "accompany"] = "hub_wait"
    vent_exit_policy: Literal["target_distance", "observed_risk"] = "target_distance"
    post_meeting_retarget: StrictBool = False
    self_report: StrictBool = False
    sabotage_threshold: Literal["six_sevenths", "two_thirds"] = "six_sevenths"
    evidence_reasoning_version: Literal[1] | None = None
    bounded_rebuttal_version: Literal[1] | None = None

    @field_validator(
        "format_version",
        "evidence_reasoning_version",
        "bounded_rebuttal_version",
        mode="before",
    )
    @classmethod
    def _literal_versions_are_integers(cls, value: object) -> object:
        if value is not None and type(value) is not int:
            raise ValueError("experiment versions must be integer version numbers")
        return value

    @property
    def is_default(self) -> bool:
        """Whether a writer must omit this configuration to retain old bytes."""

        return self == RecordedExperimentConfig()

    @property
    def has_tactical_changes(self) -> bool:
        return (
            self.crew_idle_policy != "hub_wait"
            or self.vent_exit_policy != "target_distance"
            or self.post_meeting_retarget
            or self.self_report
            or self.sabotage_threshold != "six_sevenths"
        )


def normalize_experiment_config(
    config: RecordedExperimentConfig | None,
) -> RecordedExperimentConfig | None:
    """Represent all-OFF settings by the absent historical field."""

    return None if config is None or config.is_default else config


def validate_recorded_experiment_config(
    tick_configs: Sequence[RecordedExperimentConfig | None],
    *,
    terminal_config: RecordedExperimentConfig | None = None,
    terminal_present: bool = False,
) -> RecordedExperimentConfig | None:
    """Resolve one recording, rejecting switched modes or a conflicting footer.

    Tick rows identify an interrupted run before a terminal footer exists. The
    caller supplies whether a footer exists, so an absent footer and a footer
    falsely claiming the baseline are distinguishable. Parsing rejects unknown
    fields and versions before this consistency check runs.
    """

    normalized = tuple(normalize_experiment_config(item) for item in tick_configs)
    first = normalized[0] if normalized else None
    if any(item != first for item in normalized):
        raise ValueError("experiment configuration changes between tick rows")
    if terminal_present and normalize_experiment_config(terminal_config) != first:
        raise ValueError("terminal experiment configuration disagrees with tick rows")
    return first
