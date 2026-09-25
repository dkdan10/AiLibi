"""Versioned experiment identity survives partials without relabelling defaults."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType, NoneType
from typing import Any, Literal, cast, get_args

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, ValidationError

from agents.tactical.experimental import (
    UNBUILT_OPTION_VALUES,
    ExperimentalImpostorPolicy,
    TacticalExperimentOptions,
    UnbuiltTacticalOptionError,
)
from engine.entities import BodyState
from engine.events import MeetingTriggeredEvent
from engine.world import WorldState, load_canonical_map
from experiments.tactical_gameplay import candidate_configs
from llm.fake_provider import FakeProvider
from meetings.evidence_profile import MeetingEvidenceProfile
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    OMITTED_AT_DEFAULT,
    ConfigLayer,
    RecordedExperimentConfig,
    fields_in_layer,
    normalize_experiment_config,
    validate_recorded_experiment_config,
    wave_settings,
)
from orchestrator.game import (  # noqa: PLC2701
    HeadlessGame,
    _build_meeting_trigger,
    _tactical_experiment_options,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state


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
        {"report_body_handle_version": True},
        {"ballot_kill_row_version": "1"},
        {"impostor_ballot_version": True},
        {"report_body_handle_version": 2},
        {"vent_witness_rule": "PHYSICAL"},
        {"vent_entry_policy": "any_kill"},
        {"vent_exit_policy": "look_first"},
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


def test_the_retired_citation_relevance_key_is_gone_and_refused() -> None:
    """The lever is retired (ruling D6 of 2026-09-19), field and all.

    It was never ON in a committed recording and was omitted from the
    serialization whenever it was OFF, so deleting it removes no recorded key
    from any format-1 or format-2 row -- which is what lets the retirement land
    without a re-record. ``extra="forbid"`` is what makes that checkable: a
    config still passing the keyword is refused loud rather than carrying a
    field nothing reads.
    """

    for version in (1, 2):
        off = RecordedExperimentConfig(
            format_version=version,
            evidence_reasoning_version=2 if version == 2 else 1,
        )
        assert "citation_relevance_version" not in off.model_dump()
        assert "citation_relevance_version" not in off.model_dump_json()
    assert (
        "citation_relevance_version"
        not in RecordedExperimentConfig.model_json_schema(mode="serialization")[
            "properties"
        ]
    )
    with pytest.raises(ValidationError):
        RecordedExperimentConfig(
            format_version=2,
            citation_relevance_version=1,  # type: ignore[call-arg]
        )
    # A bare format-2 config still normalizes away entirely.
    assert RecordedExperimentConfig(format_version=2).is_default


# ---------------------------------------------------------------------------
# The Stage-B fields: one layer per field, omission at default, the two reset
# guards, the tactical options mirror and the trigger keyword.
# ---------------------------------------------------------------------------

#: The wave's version plan (decision memo section 3.3): field -> layer.
_VERSION_PLAN: dict[str, ConfigLayer] = {
    "vent_witness_rule": "engine",
    "vent_exit_policy": "tactical",
    "vent_entry_policy": "tactical",
    "meeting_reset": "orchestrator",
    "bounded_rebuttal_version": "meeting",
    "report_body_handle_version": "orchestrator",
    "ballot_kill_row_version": "meeting",
    "impostor_ballot_version": "meeting",
}


def _constructed(values: dict[str, object]) -> RecordedExperimentConfig:
    """A config built past validation (the pending guard's bypass route)."""

    return RecordedExperimentConfig.model_construct(**cast(dict[str, Any], values))


def _literal_values(model: type[BaseModel], field: str) -> tuple[object, ...]:
    """Every value a Literal (or optional Literal, or bool) field accepts."""

    annotation = model.model_fields[field].annotation
    if annotation is bool:
        return (False, True)
    values: list[object] = []
    pending: list[object] = [annotation]
    while pending:
        node = pending.pop(0)
        if node is NoneType:
            values.append(None)
            continue
        args = get_args(node)
        if getattr(node, "__origin__", None) is Literal:
            values.extend(args)
        else:
            pending.extend(args)
    return tuple(values)


def _on_value(field: str) -> object:
    """The first value of ``field`` other than its default."""

    default = RecordedExperimentConfig.model_fields[field].default
    values = _literal_values(RecordedExperimentConfig, field)
    return next(value for value in values if value != default)


def _classification_problems(model: type[BaseModel]) -> list[str]:
    fields, classified = set(model.model_fields), set(FIELD_LAYER)
    return [f"unclassified {name}" for name in sorted(fields - classified)] + [
        f"classified but absent {name}" for name in sorted(classified - fields)
    ]


def test_every_config_field_has_exactly_one_layer() -> None:
    assert _classification_problems(RecordedExperimentConfig) == []
    assert isinstance(FIELD_LAYER, MappingProxyType)
    assert set(FIELD_LAYER.values()) <= set(get_args(ConfigLayer))


def test_an_unclassified_field_fails_the_classification() -> None:
    # Planted: a config model carrying one extra field FIELD_LAYER does not name.
    class _StandIn(RecordedExperimentConfig):
        stand_in_rule: Literal["old", "new"] = "old"

    assert _classification_problems(_StandIn) == ["unclassified stand_in_rule"]


def test_the_wave_fields_and_the_derived_rows_sit_in_their_layers() -> None:
    assert {field: FIELD_LAYER[field] for field in _VERSION_PLAN} == _VERSION_PLAN
    # The rows no consumer-equality test below derives: the format field, and
    # the one engine field the engine-arguments helper threads today.
    assert FIELD_LAYER["format_version"] == "format"
    assert fields_in_layer("engine") == ("redistribution_policy", "vent_witness_rule")
    assert fields_in_layer("orchestrator") == (
        "meeting_reset",
        "report_body_handle_version",
    )


def test_the_meeting_layer_is_exactly_the_evidence_profile() -> None:
    assert set(fields_in_layer("meeting")) == set(MeetingEvidenceProfile.model_fields)


def test_the_tactical_layer_is_exactly_the_options_minus_the_derived_flag() -> None:
    assert set(fields_in_layer("tactical")) == set(
        TacticalExperimentOptions.model_fields
    ) - {"meeting_positions_preserved"}


def test_layer_drift_breaks_both_consumer_equalities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Planted drift: one meeting and one tactical field moved to another layer.
    drifted = dict(FIELD_LAYER)
    drifted["impostor_ballot_version"] = "orchestrator"
    drifted["vent_entry_policy"] = "orchestrator"
    monkeypatch.setattr(experiment_config, "FIELD_LAYER", MappingProxyType(drifted))
    assert set(fields_in_layer("meeting")) != set(MeetingEvidenceProfile.model_fields)
    assert set(fields_in_layer("tactical")) != set(
        TacticalExperimentOptions.model_fields
    ) - {"meeting_positions_preserved"}


def test_the_omitted_fields_are_exactly_the_fields_the_wave_added() -> None:
    added = set(RecordedExperimentConfig.model_fields) - set(
        experiment_config._PRE_WAVE_VALUES
    )
    assert set(OMITTED_AT_DEFAULT) == added
    assert len(OMITTED_AT_DEFAULT) == 5


@pytest.mark.parametrize(
    "config",
    [
        RecordedExperimentConfig(),
        RecordedExperimentConfig(evidence_reasoning_version=1),
        RecordedExperimentConfig(
            format_version=2,
            evidence_reasoning_version=2,
            public_account_version=1,
            attributed_testimony_version=1,
        ),
        RecordedExperimentConfig(
            format_version=3, evidence_reasoning_version=2, investigation_version=1
        ),
        RecordedExperimentConfig(
            meeting_reset="hub_with_grace", bounded_rebuttal_version=1
        ),
    ],
    ids=["default", "format1", "format2", "format3", "existing-arms"],
)
def test_a_wave_field_at_its_default_adds_no_key_under_any_format(
    config: RecordedExperimentConfig,
) -> None:
    for payload in (
        config.model_dump(),
        config.model_dump(mode="json"),
        json.loads(config.model_dump_json()),
    ):
        assert not set(OMITTED_AT_DEFAULT) & set(payload)
    # Explicit defaults are the same config and dump the same bytes.
    spelled = RecordedExperimentConfig.model_validate(
        {
            **config.model_dump(),
            **{
                field: RecordedExperimentConfig.model_fields[field].default
                for field in OMITTED_AT_DEFAULT
            },
        }
    )
    assert spelled == config
    assert spelled.model_dump_json() == config.model_dump_json()


@pytest.mark.parametrize("field", OMITTED_AT_DEFAULT)
def test_an_on_wave_value_dumps_its_own_key_only(field: str) -> None:
    value = _on_value(field)
    config = _constructed({field: value})
    assert config.model_dump()[field] == value
    assert json.loads(config.model_dump_json())[field] == value
    assert set(OMITTED_AT_DEFAULT) & set(config.model_dump()) == {field}
    assert not config.is_default
    assert normalize_experiment_config(config) is config


def test_the_schema_still_lists_every_typed_field() -> None:
    for mode in ("serialization", "validation"):
        properties = RecordedExperimentConfig.model_json_schema(mode=mode)["properties"]
        assert set(properties) == set(RecordedExperimentConfig.model_fields)


def test_default_wave_fields_keep_reading_all_off() -> None:
    for version in (1, 2):
        config = RecordedExperimentConfig(
            format_version=version,
            vent_witness_rule="both_rooms",
            vent_entry_policy="any_body",
            report_body_handle_version=None,
            ballot_kill_row_version=None,
            impostor_ballot_version=None,
        )
        assert config.is_default
        assert normalize_experiment_config(config) is None


# The two reset guards --------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "other_field"),
    [
        ({"evidence_reasoning_version": 1}, "evidence_reasoning_version"),
        ({"post_meeting_retarget": True}, "post_meeting_retarget"),
    ],
)
def test_the_reset_refuses_the_two_settings_it_would_silently_break(
    raw: dict[str, object], other_field: str
) -> None:
    with pytest.raises(ValidationError) as refused:
        RecordedExperimentConfig.model_validate(
            {**raw, "meeting_reset": "hub_with_grace"}
        )
    message = str(refused.value)
    assert other_field in message and "meeting_reset hub_with_grace" in message
    # Each setting alone still validates.
    assert RecordedExperimentConfig.model_validate(raw)


def test_evidence_version_two_with_the_reset_still_validates() -> None:
    config = RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        meeting_reset="hub_with_grace",
    )
    assert config.meeting_reset == "hub_with_grace"


def test_no_lab_candidate_combines_either_reset_pair() -> None:
    candidates = candidate_configs()
    assert len(candidates) == 9
    combined = [
        name
        for name, config in candidates.items()
        if config.meeting_reset == "hub_with_grace"
        and (config.evidence_reasoning_version == 1 or config.post_meeting_retarget)
    ]
    assert combined == []


# Tactical changes, the options mirror and the unbuilt refusal ---------------


@pytest.mark.parametrize("field", fields_in_layer("tactical"))
def test_every_tactical_field_counts_as_a_tactical_change(field: str) -> None:
    config = _constructed({field: _on_value(field)})
    assert config.has_tactical_changes


@pytest.mark.parametrize(
    "field", [field for field, layer in FIELD_LAYER.items() if layer != "tactical"]
)
def test_no_other_layer_counts_as_a_tactical_change(field: str) -> None:
    config = _constructed({field: _on_value(field)})
    assert not config.has_tactical_changes
    assert not RecordedExperimentConfig().has_tactical_changes


@pytest.mark.parametrize("field", fields_in_layer("tactical"))
def test_the_options_carry_every_tactical_field(field: str) -> None:
    value = _on_value(field)
    options = _tactical_experiment_options(_constructed({field: value}))
    assert getattr(options, field) == value


def test_the_options_carry_the_two_unbuilt_values_too() -> None:
    options = _tactical_experiment_options(
        RecordedExperimentConfig.model_construct(
            vent_exit_policy="look_and_wait", vent_entry_policy="own_fresh_kill"
        )
    )
    assert options.vent_exit_policy == "look_and_wait"
    assert options.vent_entry_policy == "own_fresh_kill"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (field, value)
        for field, values in UNBUILT_OPTION_VALUES.items()
        for value in sorted(values)
    ],
)
def test_an_unbuilt_option_value_refuses_to_build_a_policy(
    field: str, value: str
) -> None:
    options = TacticalExperimentOptions.model_validate({field: value})
    with pytest.raises(UnbuiltTacticalOptionError, match=f"{field}={value!r}"):
        ExperimentalImpostorPolicy(agent_id="p-1", options=options)


def test_the_built_vent_values_still_build_a_policy() -> None:
    for options in (
        TacticalExperimentOptions(vent_exit_policy="observed_risk"),
        TacticalExperimentOptions(vent_exit_policy="target_distance"),
        TacticalExperimentOptions(vent_entry_policy="any_body"),
    ):
        assert ExperimentalImpostorPolicy(agent_id="p-1", options=options)


def test_the_factory_refuses_an_unbuilt_value_rather_than_running_the_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}))
    config = RecordedExperimentConfig(vent_entry_policy="own_fresh_kill")
    factory = build_default_agent_factory(experiment_config=config)
    with pytest.raises(UnbuiltTacticalOptionError, match="vent_entry_policy"):
        factory("p-1", "IMPOSTOR")


# The settings a pre-wave reader cannot know ------------------------------------


def test_wave_settings_name_only_what_the_wave_added() -> None:
    assert wave_settings(RecordedExperimentConfig()) == ()
    for config in candidate_configs().values():
        assert wave_settings(config) == ()
    mixed = RecordedExperimentConfig.model_construct(
        crew_idle_policy="patrol",
        vent_exit_policy="look_and_wait",
        impostor_ballot_version=1,
        vent_witness_rule="physical",
    )
    assert wave_settings(mixed) == (
        ("vent_exit_policy", "look_and_wait"),
        ("vent_witness_rule", "physical"),
        ("impostor_ballot_version", 1),
    )
    # A pre-wave value keeps the older meaning; True is not the version 1.
    assert (
        wave_settings(
            RecordedExperimentConfig.model_construct(vent_exit_policy="observed_risk")
        )
        == ()
    )
    assert wave_settings(
        RecordedExperimentConfig.model_construct(bounded_rebuttal_version=True)
    ) == (("bounded_rebuttal_version", True),)


# The trigger keyword -----------------------------------------------------------


def _trigger_inputs(
    *, kind: Literal["report", "emergency"], tick: int, victim: str
) -> tuple[WorldState, tuple[MeetingTriggeredEvent, ...]]:
    body_id = f"body-{victim}-{max(0, tick - 3)}"
    state = seed_initial_state(
        seed=0, game_map=load_canonical_map(), num_players=9, num_impostors=2
    )
    state = replace(
        state,
        phase="MEETING",
        bodies={
            body_id: BodyState(
                id=body_id,
                player_id=victim,
                room="MEDBAY",
                position=(0.0, 0.0),
                killed_by="p-9",
                discovered_by=None,
            )
        },
    )
    event = MeetingTriggeredEvent(
        type="MeetingTriggered",
        tick=tick,
        actor="p-3",
        trigger=kind,
        body_id=body_id if kind == "report" else None,
    )
    return state, (event,)


@given(
    kind=st.sampled_from(("report", "emergency")),
    tick=st.integers(min_value=0, max_value=5_000),
    victim=st.integers(min_value=1, max_value=9).map(lambda n: f"p-{n}"),
    temporal=st.booleans(),
)
# Each example parses the map and seeds a world.
@settings(deadline=None, max_examples=40)
def test_no_body_handle_arm_builds_todays_trigger_byte_for_byte(
    kind: Literal["report", "emergency"], tick: int, victim: str, temporal: bool
) -> None:
    state, events = _trigger_inputs(kind=kind, tick=tick, victim=victim)
    today = _build_meeting_trigger(
        state=state,
        events=events,
        temporal_observations=temporal,
    )
    explicit = _build_meeting_trigger(
        state=state,
        events=events,
        temporal_observations=temporal,
        report_body_handle_version=None,
    )
    assert explicit == today
    assert explicit[0].description == today[0].description
    with pytest.raises(ValueError, match="report_body_handle_version=1"):
        _build_meeting_trigger(
            state=state,
            events=events,
            temporal_observations=temporal,
            report_body_handle_version=1,
        )


def test_the_live_meeting_passes_the_recorded_body_handle_arm(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # With the guard patched open, the first meeting reaches the builder with
    # the recorded value and is refused there, before any model call.
    monkeypatch.setattr(experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}))
    config = RecordedExperimentConfig(report_body_handle_version=1)
    game = HeadlessGame(
        seed=1000,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=tmp_path / "replay-seed-1000.jsonl",
        scheduler=TickScheduler(max_ticks=96),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider(), env={}),
        experiment_config=config,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
    )
    with pytest.raises(ValueError, match="report_body_handle_version=1"):
        game.run()


@pytest.mark.parametrize(
    "raw",
    [
        {"ballot_kill_row_version": True},
        {"impostor_ballot_version": "1"},
        {"ballot_kill_row_version": 2},
    ],
)
def test_the_profile_refuses_a_coerced_ballot_version(raw: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        MeetingEvidenceProfile.model_validate(raw)
