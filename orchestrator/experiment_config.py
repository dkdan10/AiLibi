"""Describe independently selectable experiments without changing the baseline.

The orchestrator decomposes this recording contract into engine and agent
arguments. Neither side imports this privileged wiring module. Missing config
means the historical defaults; an enabled config must agree across a recording.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    GetJsonSchemaHandler,
    SerializerFunctionWrapHandler,
    StrictBool,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema

from meetings.schemas import _core_schema_without_serializer


class RecordedExperimentConfig(BaseModel):
    """A closed, immutable description of the offline experimental arms."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    format_version: Literal[1, 2, 3] = 1
    redistribution_policy: Literal["lowest_id", "least_remaining_work"] = "lowest_id"
    meeting_reset: Literal["preserve", "hub_with_grace"] = "preserve"
    crew_idle_policy: Literal["hub_wait", "patrol", "accompany"] = "hub_wait"
    vent_exit_policy: Literal["target_distance", "observed_risk"] = "target_distance"
    post_meeting_retarget: StrictBool = False
    self_report: StrictBool = False
    sabotage_threshold: Literal["six_sevenths", "two_thirds"] = "six_sevenths"
    evidence_reasoning_version: Literal[1, 2] | None = None
    bounded_rebuttal_version: Literal[1] | None = None
    public_account_version: Literal[1] | None = None
    attributed_testimony_version: Literal[1] | None = None

    investigation_version: Literal[1] | None = None
    contextual_self_report_version: Literal[1] | None = None

    @field_validator(
        "format_version",
        "evidence_reasoning_version",
        "bounded_rebuttal_version",
        "public_account_version",
        "attributed_testimony_version",
        "investigation_version",
        "contextual_self_report_version",
        mode="before",
    )
    @classmethod
    def _literal_versions_are_integers(cls, value: object) -> object:
        if value is not None and type(value) is not int:
            raise ValueError("experiment versions must be integer version numbers")
        return value

    @model_validator(mode="after")
    def _new_features_require_v2(self) -> RecordedExperimentConfig:
        if self.format_version == 1 and (
            self.evidence_reasoning_version == 2
            or self.public_account_version is not None
            or self.attributed_testimony_version is not None
        ):
            raise ValueError(
                "new evidence and account profiles require experiment format version 2"
            )
        if self.format_version == 3 and self.evidence_reasoning_version != 2:
            raise ValueError("experiment format 3 requires evidence version 2")
        if (
            self.investigation_version is not None
            or self.contextual_self_report_version is not None
        ):
            if self.format_version != 3 or self.evidence_reasoning_version != 2:
                raise ValueError(
                    "investigation and contextual self-report require format 3 and evidence version 2"
                )
        if (
            self.investigation_version is not None
            and self.crew_idle_policy != "hub_wait"
        ):
            raise ValueError("investigation conflicts with the old crew idle policy")
        if self.contextual_self_report_version is not None and self.self_report:
            raise ValueError(
                "contextual self-report conflicts with unconditional self-report"
            )
        return self

    @model_serializer(mode="wrap")
    def _preserve_version_one_bytes(
        self, handler: SerializerFunctionWrapHandler
    ) -> dict[str, Any]:
        payload: dict[str, Any] = handler(self)
        if self.format_version == 1:
            del payload["public_account_version"]
            del payload["attributed_testimony_version"]
        if self.format_version < 3:
            del payload["investigation_version"]
            del payload["contextual_self_report_version"]
        return payload

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Retain typed fields in serialization schemas despite omitted v1 defaults."""
        return handler(_core_schema_without_serializer(core_schema))

    @property
    def is_default(self) -> bool:
        """Whether a writer must omit this configuration to retain old bytes."""

        return (
            self.model_copy(update={"format_version": 1}) == RecordedExperimentConfig()
        )

    @property
    def has_tactical_changes(self) -> bool:
        return (
            self.crew_idle_policy != "hub_wait"
            or self.vent_exit_policy != "target_distance"
            or self.post_meeting_retarget
            or self.self_report
            or self.investigation_version is not None
            or self.contextual_self_report_version is not None
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
