"""The Stage-B arm spine: committed bytes, the pending guard, one engine helper,
a runner built from the recorded config, derived arm stamps, the spectator
view and the contract page (``docs/experiment-arms.md``).

No arm behaviour exists yet, so every ON value here is either refused (the
pending guard) or reached with that guard patched open to prove the plumbing
around it. The last arm card deletes the guard's refusal tests with the guard.
"""

from __future__ import annotations

import ast
import json
import os
import re
from collections.abc import Iterator
from pathlib import Path
from types import MappingProxyType, NoneType
from typing import Any, Literal, cast, get_args

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel, ValidationError

import orchestrator.game as game_module
from agents.tactical.experimental import UNBUILT_OPTION_VALUES
from api.replay_loader import ReplayLoader
from api.schemas import ExperimentConfigView
from engine.events import MeetingTriggeredEvent
from engine.world import load_canonical_map
from experiments.tactical_gameplay import candidate_configs
from llm.fake_provider import FakeProvider
from meetings.evidence_profile import (
    CONFIG_ONLY_PROFILE_FIELDS,
    EXPERIMENT_ENV_NAMES,
    MeetingEvidenceProfile,
    profile_from_config,
)
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    OMITTED_AT_DEFAULT,
    WAVE_ARMS_PENDING,
    RecordedExperimentConfig,
    engine_arguments,
    fields_in_layer,
    meeting_values,
)
from orchestrator.game import (  # noqa: PLC2701
    PROMPT_VERSION_SETS,
    HeadlessGame,
    _arm_is_served,
    _build_meeting_trigger,
    build_default_agent_factory,
    build_default_meeting_runner,
    experiment_arm_suffix,
    prompt_versions_for_set,
)
from orchestrator.replay import _stable_json  # noqa: PLC2701
from orchestrator.seeder import seed_initial_state

_REPO = Path(__file__).resolve().parents[2]
_SET = "qwen3_6_27b"

#: The eight fields of the wave's version plan (decision memo section 3.3).
_WAVE_FIELDS: tuple[str, ...] = (
    "vent_witness_rule",
    "vent_exit_policy",
    "vent_entry_policy",
    "meeting_reset",
    "bounded_rebuttal_version",
    "report_body_handle_version",
    "ballot_kill_row_version",
    "impostor_ballot_version",
)

#: The round-1 config the decision memo declares (section 1, "Arms").
_WAVE_CONFIG: dict[str, object] = {
    "format_version": 1,
    "meeting_reset": "hub_with_grace",
    "vent_exit_policy": "look_and_wait",
    "vent_entry_policy": "own_fresh_kill",
    "vent_witness_rule": "physical",
    "bounded_rebuttal_version": 1,
    "report_body_handle_version": 1,
    "ballot_kill_row_version": 1,
    "impostor_ballot_version": 1,
}


def _open_the_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}))


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
        if getattr(node, "__origin__", None) is Literal:
            values.extend(get_args(node))
        else:
            pending.extend(get_args(node))
    return tuple(values)


# ---------------------------------------------------------------------------
# Committed payloads re-serialize byte for byte.
# ---------------------------------------------------------------------------

_ARCHIVE = _REPO / "audits" / "deduction-candidate" / "run-2026-09-16"


def _payloads(node: object) -> Iterator[dict[str, object]]:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "experiment_config" and isinstance(value, dict):
                yield value
            else:
                yield from _payloads(value)
    elif isinstance(node, list):
        for value in node:
            yield from _payloads(value)


def _committed_files(suffix: str) -> list[Path]:
    return sorted(
        path
        for root in (_REPO / "audits", _REPO / "tests" / "fixtures")
        for path in root.rglob(f"*{suffix}")
        if '"experiment_config"' in path.read_text(encoding="utf-8")
    )


def _first_recorded_mismatch() -> tuple[str | None, int, int]:
    """(first mismatching row, payload rows, files) over every committed JSONL row.

    Rows are written by ``_stable_json`` (compact, sorted keys), so the
    re-serialized payload must appear verbatim inside the committed line.
    """

    rows = 0
    files = 0
    for path in _committed_files(".jsonl"):
        carried = False
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            for payload in _payloads(json.loads(line)):
                carried = True
                rows += 1
                dumped = RecordedExperimentConfig.model_validate(payload).model_dump(
                    mode="json"
                )
                if f'"experiment_config":{_stable_json(dumped)}' not in line:
                    return f"{path.relative_to(_REPO)}:{number}", rows, files
        files += carried
    return None, rows, files


def test_every_committed_recorded_payload_reserializes_byte_for_byte() -> None:
    mismatch, rows, files = _first_recorded_mismatch()
    assert mismatch is None
    # The census the card states, re-measured by this walk.
    assert (rows, files) == (956, 101)


def test_every_committed_audit_json_payload_reserializes_unchanged() -> None:
    counts: dict[str, int] = {}
    for path in _committed_files(".json"):
        payloads = list(_payloads(json.loads(path.read_text(encoding="utf-8"))))
        if not payloads:
            continue
        counts[str(path.relative_to(_REPO))] = len(payloads)
        for payload in payloads:
            dumped = RecordedExperimentConfig.model_validate(payload).model_dump(
                mode="json"
            )
            assert _stable_json(dumped) == _stable_json(payload)
            # Committed in declaration order or sorted; either way the same keys.
            assert list(payload) in (list(dumped), sorted(dumped))
    assert counts == {
        "audits/deduction-candidate/2026-09-06-mechanisms.json": 41,
        "audits/deduction-candidate/run-2026-09-16/usage-reconciliation.json": 100,
        "audits/investigation-candidate/2026-09-06-meetings.json": 41,
        "audits/investigation-candidate/2026-09-06-normal-policies.json": 42,
        "audits/investigation-candidate/candidate-handoff.json": 13,
    }


def test_without_the_omission_rule_the_first_archive_row_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Perturbed: the omit-at-default rule switched off.
    monkeypatch.setattr(experiment_config, "OMITTED_AT_DEFAULT", ())
    mismatch, rows, _files = _first_recorded_mismatch()
    first_file = min(_ARCHIVE.glob("*.jsonl"))
    assert mismatch == f"{first_file.relative_to(_REPO)}:1"
    assert rows == 1


def test_the_declared_wave_config_serializes_as_format_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _open_the_guard(monkeypatch)
    config = RecordedExperimentConfig.model_validate(_WAVE_CONFIG)
    dumped = config.model_dump(mode="json")
    assert dumped["format_version"] == 1
    assert {key: dumped[key] for key in _WAVE_CONFIG} == _WAVE_CONFIG
    assert RecordedExperimentConfig.model_validate_json(config.model_dump_json()) == (
        config
    )


# ---------------------------------------------------------------------------
# The pending guard, parametrized from its live contents.
# ---------------------------------------------------------------------------

_PENDING: list[tuple[str, object]] = [
    (field, value)
    for field, values in WAVE_ARMS_PENDING.items()
    for value in sorted(values, key=repr)
]
_PENDING_PROFILE = [
    (field, value)
    for field, value in _PENDING
    if field in MeetingEvidenceProfile.model_fields
]


def _unbuilt_values() -> set[tuple[str, object]]:
    """Every wave ON value whose behaviour is not built, read off the behaviour.

    An engine value is unbuilt while the engine-arguments helper does not
    thread its field; a tactical value while the policies refuse it; the body
    handle while the trigger builder refuses it; a ballot value while no
    template is registered for its stamp. An arm card builds the behaviour and
    deletes the pending name together, so this equality needs no edit.
    """

    unbuilt: set[tuple[str, object]] = set()
    for field in fields_in_layer("engine"):
        if field not in experiment_config._THREADED_ENGINE_FIELDS:
            default = RecordedExperimentConfig.model_fields[field].default
            unbuilt |= {
                (field, value)
                for value in _literal_values(RecordedExperimentConfig, field)
                if value != default
            }
    for field, values in UNBUILT_OPTION_VALUES.items():
        unbuilt |= {(field, value) for value in values}
    state = seed_initial_state(seed=0, game_map=load_canonical_map(), num_players=4)
    event = MeetingTriggeredEvent(
        type="MeetingTriggered", tick=4, actor="p-1", trigger="emergency"
    )
    try:
        _build_meeting_trigger(
            state=state, events=(event,), report_body_handle_version=1
        )
    except ValueError:
        unbuilt.add(("report_body_handle_version", 1))
    for field in CONFIG_ONLY_PROFILE_FIELDS:
        if field not in game_module.EXPERIMENT_ARM_TEMPLATES:
            unbuilt.add((field, 1))
    return unbuilt


def test_a_value_is_pending_exactly_while_its_behaviour_is_unbuilt() -> None:
    assert set(_PENDING) == _unbuilt_values()


def test_the_pending_guard_still_lists_an_arm() -> None:
    assert _PENDING, (
        "WAVE_ARMS_PENDING is empty: the last arm card deletes the guard, its "
        "call sites and this module's refusal tests"
    )
    assert isinstance(WAVE_ARMS_PENDING, MappingProxyType)


@pytest.mark.parametrize(("field", "value"), _PENDING)
def test_validation_refuses_a_pending_value(field: str, value: object) -> None:
    with pytest.raises(ValidationError, match=re.escape(f"{field}={value!r}")):
        RecordedExperimentConfig.model_validate({field: value})


@pytest.mark.parametrize(("field", "value"), _PENDING)
def test_construction_refuses_a_pending_value_built_past_validation(
    field: str, value: object
) -> None:
    config = _constructed({field: value})
    with pytest.raises(ValueError, match=re.escape(f"{field}={value!r}")):
        HeadlessGame(
            seed=1,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=None,
            experiment_config=config,
        )


@pytest.mark.parametrize(("field", "value"), _PENDING_PROFILE)
def test_the_runner_refuses_a_profile_carrying_a_pending_value(
    field: str, value: object
) -> None:
    profile = MeetingEvidenceProfile.model_validate({field: value})
    with pytest.raises(ValueError, match=re.escape(f"{field}={value!r}")):
        build_default_meeting_runner(llm_client=FakeProvider(), env={}, profile=profile)


_EXISTING_ON: dict[str, dict[str, object]] = {
    "least_remaining_work": {"redistribution_policy": "least_remaining_work"},
    "hub_with_grace": {"meeting_reset": "hub_with_grace"},
    "patrol": {"crew_idle_policy": "patrol"},
    "accompany": {"crew_idle_policy": "accompany"},
    "observed_risk": {"vent_exit_policy": "observed_risk"},
    "post_meeting_retarget": {"post_meeting_retarget": True},
    "self_report": {"self_report": True},
    "two_thirds": {"sabotage_threshold": "two_thirds"},
    "bounded_rebuttal_version": {"bounded_rebuttal_version": 1},
}


@pytest.mark.parametrize("raw", list(_EXISTING_ON.values()), ids=list(_EXISTING_ON))
def test_every_arm_that_exists_today_still_validates_and_constructs(
    raw: dict[str, object],
) -> None:
    config = RecordedExperimentConfig.model_validate(raw)
    game = HeadlessGame(
        seed=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=None,
        experiment_config=config,
    )
    assert game._experiment_config == config  # noqa: PLC2701


# ---------------------------------------------------------------------------
# One engine-arguments helper, and the scan that holds every site to it.
# ---------------------------------------------------------------------------


def test_no_config_threads_todays_engine_arguments() -> None:
    assert engine_arguments(None) == {"redistribution_policy": "lowest_id"}
    assert engine_arguments(RecordedExperimentConfig()) == engine_arguments(None)
    workload = RecordedExperimentConfig(redistribution_policy="least_remaining_work")
    assert engine_arguments(workload) == {
        "redistribution_policy": "least_remaining_work"
    }
    assert set(experiment_config._THREADED_ENGINE_FIELDS) <= set(
        fields_in_layer("engine")
    )


@pytest.mark.parametrize(
    "field",
    [
        field
        for field in fields_in_layer("engine")
        if field not in experiment_config._THREADED_ENGINE_FIELDS
    ],
)
def test_an_engine_field_the_helper_does_not_thread_is_refused(field: str) -> None:
    value = next(
        value
        for value in _literal_values(RecordedExperimentConfig, field)
        if value != RecordedExperimentConfig.model_fields[field].default
    )
    with pytest.raises(ValueError, match=re.escape(f"{field}={value!r}")):
        engine_arguments(_constructed({field: value}))


def test_a_stand_in_engine_field_raises_where_hand_threading_runs_the_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Planted: FIELD_LAYER extended with a fake engine field set non-default.
    class _StandIn(RecordedExperimentConfig):
        stand_in_engine_rule: Literal["old", "new"] = "old"

    monkeypatch.setattr(
        experiment_config,
        "FIELD_LAYER",
        MappingProxyType({**FIELD_LAYER, "stand_in_engine_rule": "engine"}),
    )
    config = _StandIn(stand_in_engine_rule="new")
    # A hand-threaded site passes what it names and silently runs the default
    # for the rest; the helper refuses instead.
    hand_threaded = {"redistribution_policy": config.redistribution_policy}
    assert "stand_in_engine_rule" not in hand_threaded
    with pytest.raises(ValueError, match="stand_in_engine_rule='new'"):
        engine_arguments(config)
    assert engine_arguments(_StandIn()) == {"redistribution_policy": "lowest_id"}


def test_dropping_a_threaded_field_makes_the_helper_refuse_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(experiment_config, "_THREADED_ENGINE_FIELDS", ())
    workload = RecordedExperimentConfig(redistribution_policy="least_remaining_work")
    with pytest.raises(
        ValueError, match="redistribution_policy='least_remaining_work'"
    ):
        engine_arguments(workload)


_RESIMULATION_MODULES: tuple[str, ...] = (
    "orchestrator/game.py",
    "api/replay_loader.py",
    "eval/replay_walk.py",
    "experiments/tactical_gameplay.py",
)
_ENGINE_CALLS = frozenset({"advance_tick", "_apply_action"})


def _call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def _engine_call_problems(source: str) -> tuple[int, list[str]]:
    """(engine calls found, problems) for one module's source.

    A call passes when it takes exactly one ``**`` argument that is either a
    call to ``engine_arguments`` or a name bound to one in the module, and names
    no engine-layer field by hand. An aliased import of either engine function
    is a problem, since the scan matches by name.
    """

    tree = ast.parse(source)
    bound = {
        ast.unparse(target)
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Call)
        and _call_name(node.value) == "engine_arguments"
        for target in node.targets
    }
    engine_fields = set(fields_in_layer("engine"))
    problems: list[str] = []
    calls = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in _ENGINE_CALLS and alias.asname is not None:
                    problems.append(f"line {node.lineno}: aliased {alias.name}")
        if not isinstance(node, ast.Call) or _call_name(node) not in _ENGINE_CALLS:
            continue
        calls += 1
        spread = [keyword.value for keyword in node.keywords if keyword.arg is None]
        by_hand = sorted(
            keyword.arg for keyword in node.keywords if keyword.arg in engine_fields
        )
        helper = len(spread) == 1 and (
            (
                isinstance(spread[0], ast.Call)
                and _call_name(spread[0]) == "engine_arguments"
            )
            or ast.unparse(spread[0]) in bound
        )
        if not helper or by_hand:
            problems.append(
                f"line {node.lineno}: {_call_name(node)} without the helper's "
                f"arguments (by hand: {by_hand})"
            )
    return calls, problems


@pytest.mark.parametrize("module", _RESIMULATION_MODULES)
def test_every_resimulation_advance_takes_the_helpers_arguments(module: str) -> None:
    calls, problems = _engine_call_problems(
        (_REPO / module).read_text(encoding="utf-8")
    )
    assert calls >= 1, f"{module} no longer advances the engine; update the scan"
    assert problems == []


@pytest.mark.parametrize(
    ("source", "passes"),
    [
        (
            "engine = engine_arguments(config)\n"
            "advance_tick(state, actions, game_map=m, **engine)\n"
            "_apply_action(state, m, action, **engine_arguments(config))\n",
            True,
        ),
        (
            "advance_tick(state, actions, game_map=m,"
            " redistribution_policy=config.redistribution_policy)\n",
            False,
        ),
        ("advance_tick(state, actions, game_map=m)\n", False),
        (
            "advance_tick(state, actions, game_map=m, redistribution_policy='x',"
            " **engine_arguments(config))\n",
            False,
        ),
        ("options = {}\nadvance_tick(state, actions, game_map=m, **options)\n", False),
        (
            "from engine.tick import advance_tick as step\n"
            "step(state, actions, game_map=m)\n",
            False,
        ),
    ],
    ids=["helper", "by-hand", "bare", "helper-plus-hand", "other-spread", "alias"],
)
def test_the_scan_bites_a_site_that_threads_by_hand(source: str, passes: bool) -> None:
    _calls, problems = _engine_call_problems(source)
    assert (problems == []) is passes


# ---------------------------------------------------------------------------
# A runner built from the recorded config.
# ---------------------------------------------------------------------------


def _clear_ailibi_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in list(os.environ):
        if name.startswith("AILIBI_"):
            monkeypatch.delenv(name)


def test_the_profile_is_built_from_exactly_the_meeting_layer() -> None:
    config = RecordedExperimentConfig(
        format_version=2,
        evidence_reasoning_version=2,
        bounded_rebuttal_version=1,
        public_account_version=1,
    )
    profile = profile_from_config(meeting_values(config))
    assert profile.model_dump() == {
        field: getattr(config, field) for field in MeetingEvidenceProfile.model_fields
    }


def test_meeting_value_drift_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    # Planted drift: one profile field no longer in the meeting layer.
    drifted = dict(FIELD_LAYER)
    drifted["bounded_rebuttal_version"] = "orchestrator"
    monkeypatch.setattr(experiment_config, "FIELD_LAYER", MappingProxyType(drifted))
    with pytest.raises(ValueError, match="missing.*bounded_rebuttal_version"):
        profile_from_config(meeting_values(RecordedExperimentConfig()))
    with pytest.raises(ValueError, match="unknown.*stand_in"):
        profile_from_config(
            {**MeetingEvidenceProfile().model_dump(), "stand_in_version": None}
        )


def test_a_declared_profile_is_served_instead_of_the_environment() -> None:
    profile = profile_from_config(
        meeting_values(RecordedExperimentConfig(bounded_rebuttal_version=1))
    )
    declared = build_default_meeting_runner(
        llm_client=FakeProvider(), env={}, profile=profile
    )
    assert declared.evidence_profile == profile
    assert declared.evidence_profile.bounded_rebuttal_version == 1
    ambient = build_default_meeting_runner(llm_client=FakeProvider(), env={})
    assert ambient.evidence_profile == MeetingEvidenceProfile()


@pytest.mark.parametrize("name", sorted(EXPERIMENT_ENV_NAMES))
def test_an_ambient_switch_beside_a_declared_profile_raises(name: str) -> None:
    with pytest.raises(ValueError, match=name):
        build_default_meeting_runner(
            llm_client=FakeProvider(),
            env={name: "1"},
            profile=MeetingEvidenceProfile(),
        )
    # A switch exported OFF is not a second source.
    assert build_default_meeting_runner(
        llm_client=FakeProvider(), env={name: "0"}, profile=MeetingEvidenceProfile()
    )


def test_the_ballot_fields_are_config_only() -> None:
    assert len(EXPERIMENT_ENV_NAMES) == 4
    assert CONFIG_ONLY_PROFILE_FIELDS == (
        "ballot_kill_row_version",
        "impostor_ballot_version",
    )
    switched = set(EXPERIMENT_ENV_NAMES.values())
    assert not switched & set(CONFIG_ONLY_PROFILE_FIELDS)
    assert switched | set(CONFIG_ONLY_PROFILE_FIELDS) == set(
        MeetingEvidenceProfile.model_fields
    )


_ENV_NAMES = [
    *EXPERIMENT_ENV_NAMES,
    "AILIBI_BALLOT_KILL_ROW_VERSION",
    "AILIBI_IMPOSTOR_BALLOT_VERSION",
    "AILIBI_BALLOT_KILL_ROW",
    "AILIBI_IMPOSTOR_BALLOT",
]


@given(
    env=st.dictionaries(
        keys=st.sampled_from(_ENV_NAMES),
        values=st.sampled_from(["", "0", "1", "2", "true", "on", "off"]),
    )
)
@settings(deadline=None)
def test_no_environment_sets_a_config_only_field(env: dict[str, str]) -> None:
    try:
        profile = MeetingEvidenceProfile.from_environment(env)
    except ValueError:
        return  # a malformed boolean switch is refused, never read as a field
    for field in CONFIG_ONLY_PROFILE_FIELDS:
        assert getattr(profile, field) is None


def _game(
    *,
    runner: game_module.DefaultMeetingRunner,
    config: RecordedExperimentConfig | None,
) -> HeadlessGame:
    return HeadlessGame(
        seed=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=None,
        meeting_runner=runner,
        experiment_config=config,
    )


@pytest.mark.parametrize("field", CONFIG_ONLY_PROFILE_FIELDS)
def test_a_config_only_field_must_equal_the_runners_both_ways(
    monkeypatch: pytest.MonkeyPatch, field: str
) -> None:
    _open_the_guard(monkeypatch)
    served = build_default_meeting_runner(
        llm_client=FakeProvider(),
        env={},
        profile=MeetingEvidenceProfile.model_validate({field: 1}),
    )
    bare = build_default_meeting_runner(llm_client=FakeProvider(), env={})
    carrying = RecordedExperimentConfig.model_validate({field: 1})
    with pytest.raises(ValueError, match=f"disagrees with runner {field}"):
        _game(runner=served, config=None)
    with pytest.raises(ValueError, match=f"disagrees with runner {field}"):
        _game(runner=bare, config=carrying)
    agreeing = _game(runner=served, config=carrying)
    assert agreeing._experiment_config == carrying  # noqa: PLC2701


def test_the_four_switch_fields_keep_their_one_way_rule() -> None:
    served = build_default_meeting_runner(
        llm_client=FakeProvider(), env={"AILIBI_BOUNDED_REBUTTAL": "1"}
    )
    recorded = _game(runner=served, config=None)._experiment_config  # noqa: PLC2701
    assert recorded is not None and recorded.bounded_rebuttal_version == 1
    bare = build_default_meeting_runner(llm_client=FakeProvider(), env={})
    with pytest.raises(ValueError, match="disagrees with runner bounded_rebuttal"):
        _game(runner=bare, config=RecordedExperimentConfig(bounded_rebuttal_version=1))


def test_a_declared_config_records_both_arms_on_every_row_in_a_bare_shell(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _clear_ailibi_environment(monkeypatch)
    config = RecordedExperimentConfig(
        meeting_reset="hub_with_grace", bounded_rebuttal_version=1
    )
    runner = build_default_meeting_runner(
        llm_client=FakeProvider(),
        env={},
        profile=profile_from_config(meeting_values(config)),
    )
    path = tmp_path / "replay-seed-7.jsonl"
    HeadlessGame(
        seed=7,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(experiment_config=config),
        replay_path=path,
        meeting_runner=runner,
        experiment_config=config,
        num_players=9,
        num_impostors=2,
    ).run()
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    ticks = [row for row in rows if row["kind"] == "tick"]
    footers = [row for row in rows if row["kind"] == "game_over"]
    assert ticks and len(footers) == 1
    assert any(row["kind"] == "meeting" for row in rows)
    for row in [*ticks, *footers]:
        assert row["experiment_config"]["meeting_reset"] == "hub_with_grace"
        assert row["experiment_config"]["bounded_rebuttal_version"] == 1
    # The bare-shell loader re-simulates it from the recorded config.
    (tmp_path / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}),
        encoding="utf-8",
    )
    replay = ReplayLoader(tmp_path).load_replay("headless-seed-7")
    assert replay.metadata.outcome_verified
    # The same config beside a runner built from the bare environment raises.
    with pytest.raises(ValueError, match="disagrees with runner bounded_rebuttal"):
        _game(
            runner=build_default_meeting_runner(llm_client=FakeProvider(), env={}),
            config=config,
        )


# ---------------------------------------------------------------------------
# Experiment-arm stamps, derived and never hand-written.
# ---------------------------------------------------------------------------


def test_the_suffix_is_derived_from_the_field_name() -> None:
    assert experiment_arm_suffix("ballot_kill_row_version", 1) == "ballot_kill_row_v1"
    assert experiment_arm_suffix("impostor_ballot_version", 1) == "impostor_ballot_v1"
    assert experiment_arm_suffix("bounded_rebuttal_version", 1) == "bounded_rebuttal_v1"
    for field in ("vent_witness_rule", "meeting_reset", "_version"):
        with pytest.raises(ValueError, match="_version field"):
            experiment_arm_suffix(field, 1)
    for value in (None, True, 0, "1"):
        with pytest.raises(ValueError, match="positive integer"):
            experiment_arm_suffix("ballot_kill_row_version", value)


def _registry_problems(registry: object) -> list[str]:
    """Each entry names a meeting-layer ``*_version`` field and templates only,
    and the fold serves exactly the derived stamp for them."""

    problems: list[str] = []
    default = PROMPT_VERSION_SETS[_SET]
    assert isinstance(registry, MappingProxyType)
    for field, templates in registry.items():
        if FIELD_LAYER.get(field) != "meeting":
            problems.append(f"{field}: not a meeting-layer field")
            continue
        if (
            not isinstance(templates, tuple)
            or not templates
            or not all(template in default for template in templates)
        ):
            problems.append(f"{field}: must name templates, got {templates!r}")
            continue
        value = next(
            value
            for value in _literal_values(RecordedExperimentConfig, field)
            if value is not None
        )
        served = prompt_versions_for_set(
            _SET,
            env={},
            experiment_config=_constructed({field: value}),
        )
        for template, stamp in served.items():
            expected = (
                f"{default[template]}.{experiment_arm_suffix(field, value)}"
                if template in templates
                else default[template]
            )
            if stamp != expected:
                problems.append(f"{field}: {template} served {stamp!r}")
    return problems


def test_every_registered_arm_serves_its_derived_stamp() -> None:
    assert _registry_problems(game_module.EXPERIMENT_ARM_TEMPLATES) == []


def test_a_hand_written_stamp_fails_the_derivation_test() -> None:
    # Planted: an entry supplying a literal stamp instead of templates.
    literal = MappingProxyType(
        {"ballot_kill_row_version": {"vote_ballot": "vote_ballot.qwen3_6_27b.v8.kr1"}}
    )
    assert _registry_problems(literal) == [
        "ballot_kill_row_version: must name templates, got "
        "{'vote_ballot': 'vote_ballot.qwen3_6_27b.v8.kr1'}"
    ]
    stamp_as_template = MappingProxyType(
        {"ballot_kill_row_version": ("vote_ballot.qwen3_6_27b.v8.kr1",)}
    )
    assert len(_registry_problems(stamp_as_template)) == 1
    tactical = MappingProxyType({"vent_entry_policy": ("vote_ballot",)})
    assert _registry_problems(tactical) == [
        "vent_entry_policy: not a meeting-layer field"
    ]


def _register(
    monkeypatch: pytest.MonkeyPatch, entries: dict[str, tuple[str, ...]]
) -> None:
    monkeypatch.setattr(
        game_module, "EXPERIMENT_ARM_TEMPLATES", MappingProxyType(entries)
    )


def test_a_registered_arm_is_served_only_for_a_config_carrying_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _register(monkeypatch, {"bounded_rebuttal_version": ("accusation_round",)})
    default = PROMPT_VERSION_SETS[_SET]
    carrying = RecordedExperimentConfig(bounded_rebuttal_version=1)
    served = prompt_versions_for_set(_SET, env={}, experiment_config=carrying)
    assert dict(served) == {
        **default,
        "accusation_round": "accusation_round.qwen3_6_27b.v6.bounded_rebuttal_v1",
    }
    assert _registry_problems(game_module.EXPERIMENT_ARM_TEMPLATES) == []
    for without in (
        None,
        RecordedExperimentConfig(),
        RecordedExperimentConfig(meeting_reset="hub_with_grace"),
    ):
        assert prompt_versions_for_set(_SET, env={}, experiment_config=without) is (
            default
        )
    # With a lever ON the two lineages compose by the per-template + rule.
    both = prompt_versions_for_set(
        _SET, env={"AILIBI_REPORTER_REASONING": "1"}, experiment_config=carrying
    )
    assert both["accusation_round"] == (
        "accusation_round.qwen3_6_27b.v6.reporter_reasoning"
        "+accusation_round.qwen3_6_27b.v6.bounded_rebuttal_v1"
    )
    assert (
        both["crewmate_report"] == "crewmate_report.qwen3_6_27b.v6.reporter_reasoning"
    )
    assert both["vote_ballot"] == default["vote_ballot"]
    assert _arm_is_served(
        both,
        template="accusation_round",
        arm="accusation_round.qwen3_6_27b.v6.bounded_rebuttal_v1",
    )


def test_two_arms_fold_in_field_declaration_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Registered in the reverse of declaration order; the fold follows the
    # config's declaration, which yields the round-1 ballot stamp.
    _register(
        monkeypatch,
        {
            "impostor_ballot_version": ("vote_ballot",),
            "ballot_kill_row_version": ("vote_ballot",),
        },
    )
    config = RecordedExperimentConfig.model_construct(
        ballot_kill_row_version=1, impostor_ballot_version=1
    )
    served = prompt_versions_for_set(_SET, env={}, experiment_config=config)
    assert served["vote_ballot"] == (
        "vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1"
        "+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1"
    )
    only = RecordedExperimentConfig.model_construct(impostor_ballot_version=1)
    assert prompt_versions_for_set(_SET, env={}, experiment_config=only)[
        "vote_ballot"
    ] == ("vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1")


def test_the_runner_stamps_the_profile_it_renders(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _register(monkeypatch, {"bounded_rebuttal_version": ("accusation_round",)})
    env = {"AILIBI_PROMPT_SET": _SET}
    declared = build_default_meeting_runner(
        llm_client=FakeProvider(),
        env=env,
        profile=MeetingEvidenceProfile(bounded_rebuttal_version=1),
    )
    ambient = build_default_meeting_runner(
        llm_client=FakeProvider(), env={**env, "AILIBI_BOUNDED_REBUTTAL": "1"}
    )
    bare = build_default_meeting_runner(llm_client=FakeProvider(), env=env)
    stamp = "accusation_round.qwen3_6_27b.v6.bounded_rebuttal_v1"
    assert declared._prompt_versions["accusation_round"] == stamp  # noqa: PLC2701
    assert ambient._prompt_versions == declared._prompt_versions  # noqa: PLC2701
    assert bare._prompt_versions == dict(PROMPT_VERSION_SETS[_SET])  # noqa: PLC2701


# ---------------------------------------------------------------------------
# The spectator view mirror.
# ---------------------------------------------------------------------------


def test_the_view_mirrors_every_config_field_value_and_default() -> None:
    assert list(ExperimentConfigView.model_fields) == list(
        RecordedExperimentConfig.model_fields
    )
    for field, info in RecordedExperimentConfig.model_fields.items():
        assert _literal_values(ExperimentConfigView, field) == _literal_values(
            RecordedExperimentConfig, field
        ), field
        assert ExperimentConfigView.model_fields[field].default == info.default


def test_an_older_payload_without_the_wave_keys_reads_as_defaults() -> None:
    older = RecordedExperimentConfig(crew_idle_policy="patrol").model_dump()
    assert not set(OMITTED_AT_DEFAULT) & set(older)
    view = ExperimentConfigView.model_validate(older)
    for field in OMITTED_AT_DEFAULT:
        assert (
            getattr(view, field) == RecordedExperimentConfig.model_fields[field].default
        )


def test_a_wave_payload_reaches_the_view_unchanged(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _open_the_guard(monkeypatch)
    config = RecordedExperimentConfig.model_validate(_WAVE_CONFIG)
    view = ExperimentConfigView.model_validate(config.model_dump())
    assert {field: getattr(view, field) for field in _WAVE_CONFIG} == _WAVE_CONFIG


# ---------------------------------------------------------------------------
# The contract page.
# ---------------------------------------------------------------------------

_PAGE = _REPO / "docs" / "experiment-arms.md"
_ARCHITECTURE = _REPO / "docs" / "architecture.md"
_SECTION = "### Explicit cleanup experiments"


def _page_problems(page: str, architecture: str) -> list[str]:
    problems: list[str] = []
    for field in _WAVE_FIELDS:
        layer = FIELD_LAYER[field]
        row = re.search(
            rf"^\| `{field}` \|(?P<values>[^|\n]*)\| {layer} \|", page, re.M
        )
        if row is None:
            problems.append(f"the page does not state {field} in the {layer} layer")
            continue
        for value in _literal_values(RecordedExperimentConfig, field):
            spelled = "none" if value is None else f"`{value}`"
            if spelled not in row.group("values"):
                problems.append(f"the page omits {field}'s value {spelled}")
    for symbol in (
        "FIELD_LAYER",
        "OMITTED_AT_DEFAULT",
        "WAVE_ARMS_PENDING",
        "engine_arguments",
        "profile_from_config",
        "EXPERIMENT_ARM_TEMPLATES",
    ):
        if f"`{symbol}`" not in page:
            problems.append(f"the page does not name {symbol}")
    section = architecture.split(_SECTION, 1)[-1].split("\n### ", 1)[0]
    if _SECTION not in architecture or "](experiment-arms.md)" not in section:
        problems.append("the architecture section does not link the page")
    return problems


def test_the_contract_page_states_every_wave_field_and_is_linked() -> None:
    assert (
        _page_problems(
            _PAGE.read_text(encoding="utf-8"), _ARCHITECTURE.read_text(encoding="utf-8")
        )
        == []
    )


def test_the_page_check_bites_a_missing_field_and_a_missing_link() -> None:
    page = _PAGE.read_text(encoding="utf-8")
    architecture = _ARCHITECTURE.read_text(encoding="utf-8")
    without_field = page.replace("`impostor_ballot_version`", "`impostor_ballot`")
    assert _page_problems(without_field, architecture) == [
        "the page does not state impostor_ballot_version in the meeting layer"
    ]
    without_value = page.replace("`look_and_wait` |", "|", 1)
    assert _page_problems(without_value, architecture) == [
        "the page omits vent_exit_policy's value `look_and_wait`"
    ]
    unlinked = architecture.replace("](experiment-arms.md)", "](elsewhere.md)")
    assert _page_problems(page, unlinked) == [
        "the architecture section does not link the page"
    ]


def test_the_lab_candidates_are_all_arms_that_exist_today() -> None:
    for config in candidate_configs().values():
        assert not set(OMITTED_AT_DEFAULT) & set(config.model_dump())
