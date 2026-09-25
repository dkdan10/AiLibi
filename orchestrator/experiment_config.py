"""Describe independently selectable experiments without changing the baseline.

The orchestrator decomposes this recording contract into engine and agent
arguments. Neither side imports this privileged wiring module. Missing config
means the historical defaults; an enabled config must agree across a recording.
``docs/experiment-arms.md`` states the Stage-B arms this module declares: each
field's layer, the omit-at-default rule, the pending guard and the one
engine-arguments helper.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any, Final, Literal, TypedDict, cast

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

#: The consumer that reads a config field: the recording format itself, the
#: engine tick, the orchestrator's own wiring, the tactical policies, or the
#: meeting evidence profile.
ConfigLayer = Literal["format", "engine", "orchestrator", "tactical", "meeting"]


class RecordedExperimentConfig(BaseModel):
    """A closed, immutable description of the offline experimental arms."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    format_version: Literal[1, 2, 3] = 1
    redistribution_policy: Literal["lowest_id", "least_remaining_work"] = "lowest_id"
    meeting_reset: Literal["preserve", "hub_with_grace"] = "preserve"
    crew_idle_policy: Literal["hub_wait", "patrol", "accompany"] = "hub_wait"
    vent_exit_policy: Literal["target_distance", "observed_risk", "look_and_wait"] = (
        "target_distance"
    )
    post_meeting_retarget: StrictBool = False
    self_report: StrictBool = False
    sabotage_threshold: Literal["six_sevenths", "two_thirds"] = "six_sevenths"
    evidence_reasoning_version: Literal[1, 2] | None = None
    bounded_rebuttal_version: Literal[1] | None = None
    public_account_version: Literal[1] | None = None
    attributed_testimony_version: Literal[1] | None = None
    investigation_version: Literal[1] | None = None
    contextual_self_report_version: Literal[1] | None = None
    # The Stage-B fields. Each is omitted from every payload while it holds its
    # default (``_omit_wave_fields_at_default``), so a recording without the key
    # reads as the historical default.
    vent_witness_rule: Literal["both_rooms", "physical"] = "both_rooms"
    vent_entry_policy: Literal["any_body", "own_fresh_kill"] = "any_body"
    report_body_handle_version: Literal[1] | None = None
    ballot_kill_row_version: Literal[1] | None = None
    impostor_ballot_version: Literal[1] | None = None

    @field_validator(
        "format_version",
        "evidence_reasoning_version",
        "bounded_rebuttal_version",
        "public_account_version",
        "attributed_testimony_version",
        "investigation_version",
        "contextual_self_report_version",
        "report_body_handle_version",
        "ballot_kill_row_version",
        "impostor_ballot_version",
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

    @model_validator(mode="after")
    def _meeting_reset_guards(self) -> RecordedExperimentConfig:
        """Refuse the two settings the regroup reset would silently break."""

        if self.meeting_reset != "hub_with_grace":
            return self
        if self.evidence_reasoning_version == 1:
            raise ValueError(
                "evidence_reasoning_version 1 cannot run with meeting_reset "
                "hub_with_grace: version 1 evidence does not see the regroup, so "
                "it would accuse every player the reset moved of impossible travel"
            )
        if self.post_meeting_retarget:
            raise ValueError(
                "post_meeting_retarget cannot run with meeting_reset "
                "hub_with_grace: the follow-through acts only while meeting "
                "positions are preserved, so under the reset it would be "
                "recorded ON and never act"
            )
        return self

    @model_validator(mode="after")
    def _refuse_pending_arms(self) -> RecordedExperimentConfig:
        refuse_pending_values(
            {field: getattr(self, field) for field in WAVE_ARMS_PENDING},
            source="experiment configuration",
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
        return self._omit_wave_fields_at_default(payload)

    def _omit_wave_fields_at_default(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Drop each Stage-B field that holds its default, under every format.

        The version-one rule above keys omission on ``format_version``; this one
        keys it on the value, so a new field adds no key to any payload until it
        is switched ON and ``format_version`` stays 1 for the wave's config. A
        missing key therefore always means the historical default, and a
        recording that adopts a value must write it explicitly.
        """

        for field in OMITTED_AT_DEFAULT:
            if getattr(self, field) == type(self).model_fields[field].default:
                del payload[field]
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
        """Whether any tactical-layer field leaves its default.

        The experimental policies are built only when this holds, so it reads
        every field :data:`FIELD_LAYER` assigns to the tactical layer.
        """

        return any(
            getattr(self, field) != type(self).model_fields[field].default
            for field in fields_in_layer("tactical")
        )


#: Every config field, classified by the consumer that reads it. The meeting
#: fields are exactly :class:`meetings.evidence_profile.MeetingEvidenceProfile`'s
#: fields and the tactical fields are exactly
#: :class:`agents.tactical.experimental.TacticalExperimentOptions`' fields
#: except its derived ``meeting_positions_preserved``; tests hold both equal.
FIELD_LAYER: Final[Mapping[str, ConfigLayer]] = MappingProxyType(
    {
        "format_version": "format",
        "redistribution_policy": "engine",
        "meeting_reset": "orchestrator",
        "crew_idle_policy": "tactical",
        "vent_exit_policy": "tactical",
        "post_meeting_retarget": "tactical",
        "self_report": "tactical",
        "sabotage_threshold": "tactical",
        "evidence_reasoning_version": "meeting",
        "bounded_rebuttal_version": "meeting",
        "public_account_version": "meeting",
        "attributed_testimony_version": "meeting",
        "investigation_version": "tactical",
        "contextual_self_report_version": "tactical",
        "vent_witness_rule": "engine",
        "vent_entry_policy": "tactical",
        "report_body_handle_version": "orchestrator",
        "ballot_kill_row_version": "meeting",
        "impostor_ballot_version": "meeting",
    }
)

#: The Stage-B fields the serializer omits while they hold their default.
OMITTED_AT_DEFAULT: Final[tuple[str, ...]] = (
    "vent_witness_rule",
    "vent_entry_policy",
    "report_body_handle_version",
    "ballot_kill_row_version",
    "impostor_ballot_version",
)

#: Each Stage-B ON value whose behaviour is not built yet. Validation, the
#: ``HeadlessGame`` constructor and the meeting-runner constructor refuse every
#: value listed here. Each arm card deletes its own names when it builds the
#: behaviour; the last one deletes this guard, its call sites and its test.
WAVE_ARMS_PENDING: Final[Mapping[str, frozenset[object]]] = MappingProxyType(
    {
        "vent_witness_rule": frozenset({"physical"}),
        "vent_exit_policy": frozenset({"look_and_wait"}),
        "vent_entry_policy": frozenset({"own_fresh_kill"}),
        "report_body_handle_version": frozenset({1}),
        "ballot_kill_row_version": frozenset({1}),
        "impostor_ballot_version": frozenset({1}),
    }
)

#: Every field and value that existed before the Stage-B wave. A walk profile's
#: ``supports_experiments`` flag covers exactly these; any other recorded
#: setting (a later field off its default, or a later value of one of these
#: fields) must be read by a layer the profile declares.
_PRE_WAVE_VALUES: Final[Mapping[str, frozenset[object]]] = MappingProxyType(
    {
        "format_version": frozenset({1, 2, 3}),
        "redistribution_policy": frozenset({"lowest_id", "least_remaining_work"}),
        "meeting_reset": frozenset({"preserve", "hub_with_grace"}),
        "crew_idle_policy": frozenset({"hub_wait", "patrol", "accompany"}),
        "vent_exit_policy": frozenset({"target_distance", "observed_risk"}),
        "post_meeting_retarget": frozenset({False, True}),
        "self_report": frozenset({False, True}),
        "sabotage_threshold": frozenset({"six_sevenths", "two_thirds"}),
        "evidence_reasoning_version": frozenset({None, 1, 2}),
        "bounded_rebuttal_version": frozenset({None, 1}),
        "public_account_version": frozenset({None, 1}),
        "attributed_testimony_version": frozenset({None, 1}),
        "investigation_version": frozenset({None, 1}),
        "contextual_self_report_version": frozenset({None, 1}),
    }
)


def _same_value(value: object, candidates: frozenset[object]) -> bool:
    """Membership that keeps ``True`` apart from ``1`` and ``False`` from ``0``."""

    return any(
        value == candidate and type(value) is type(candidate)
        for candidate in candidates
    )


def fields_in_layer(layer: ConfigLayer) -> tuple[str, ...]:
    """The fields :data:`FIELD_LAYER` assigns to ``layer``, in declaration order."""

    return tuple(field for field, owner in FIELD_LAYER.items() if owner == layer)


def refuse_pending_values(values: Mapping[str, object], *, source: str) -> None:
    """Raise, naming field and value, for any value :data:`WAVE_ARMS_PENDING` lists.

    ``values`` may carry any subset of the config's fields (a meeting profile
    carries only its own), and only the fields it carries are checked.
    """

    for field, refused in WAVE_ARMS_PENDING.items():
        if field in values and _same_value(values[field], refused):
            raise ValueError(
                f"{source} sets {field}={values[field]!r}, a Stage-B arm whose "
                "behaviour is not built yet; it stays refused until its arm card "
                "removes it from WAVE_ARMS_PENDING"
            )


def wave_settings(config: RecordedExperimentConfig) -> tuple[tuple[str, object], ...]:
    """The recorded settings a pre-wave reader cannot know, in declaration order.

    A setting qualifies when its field left its default and either the field or
    that value did not exist before the Stage-B wave (:data:`_PRE_WAVE_VALUES`).
    """

    settings: list[tuple[str, object]] = []
    for field, info in type(config).model_fields.items():
        value = getattr(config, field)
        if _same_value(value, frozenset({info.default})):
            continue
        if field in _PRE_WAVE_VALUES and _same_value(value, _PRE_WAVE_VALUES[field]):
            continue
        settings.append((field, value))
    return tuple(settings)


def meeting_values(config: RecordedExperimentConfig) -> dict[str, object]:
    """The meeting-layer values a recorded config selects, by :data:`FIELD_LAYER`.

    :func:`meetings.evidence_profile.profile_from_config` builds the runner's
    profile from exactly these, so the meeting package never imports this
    wiring module.
    """

    return {field: getattr(config, field) for field in fields_in_layer("meeting")}


class EngineArguments(TypedDict):
    """The ``advance_tick`` keyword arguments a recorded config selects."""

    redistribution_policy: Literal["lowest_id", "least_remaining_work"]


#: The engine-layer fields :func:`engine_arguments` threads, in the order the
#: TypedDict declares them.
_THREADED_ENGINE_FIELDS: Final[tuple[str, ...]] = tuple(EngineArguments.__annotations__)


def engine_arguments(config: RecordedExperimentConfig | None) -> EngineArguments:
    """The ``advance_tick`` / ``_apply_action`` keywords for one recording.

    The live tick, the replay loader, the shared replay walk and the tactical
    lab take their advance keywords from here (an ``ast`` scan in the tests
    pins those four modules), so an engine-layer field reaches all of them or
    none. A field :data:`FIELD_LAYER` assigns to the engine that this function
    does not thread raises when set off its default, rather than re-simulating
    the default in its place: a witness list lives only in the events, so a
    site that dropped such a field could still reproduce every state hash.
    ``None`` means the historical defaults.
    """

    resolved = config if config is not None else RecordedExperimentConfig()
    unthreaded = [
        field
        for field in fields_in_layer("engine")
        if field not in _THREADED_ENGINE_FIELDS
        and getattr(resolved, field) != type(resolved).model_fields[field].default
    ]
    if unthreaded:
        raise ValueError(
            "the recorded engine setting "
            + ", ".join(f"{field}={getattr(resolved, field)!r}" for field in unthreaded)
            + " is not threaded into the engine tick; a re-simulation would "
            "run the default instead"
        )
    return cast(
        EngineArguments,
        {field: getattr(resolved, field) for field in _THREADED_ENGINE_FIELDS},
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
