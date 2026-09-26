"""The gameplay census: every cell planted on a hand-built carrier.

Each test below builds a :class:`eval.gameplay_census.CensusInputs` by hand and
folds it, so no replay is read unless the test says so. The few tests that read
committed bytes go through ``tests/_helpers/committed.py``: the figures test
reads only the committed JSON, and the loader tests replay a perturbed copy of
one committed game's walk.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import typing
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType, ModuleType
from typing import Any, get_args, get_origin

import pytest
from hypothesis import given
from hypothesis import settings as hypothesis_settings
from hypothesis import strategies as st
from pydantic import BaseModel

import eval.gameplay_census as census
from engine.events import (
    KilledEvent,
    MovedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
)
from engine.world import load_canonical_map
from eval.balance_eval import _CURRENT_REPORT_WALK_CONFIG
from eval.gameplay_census import (
    CELLS,
    CENSUS_THREADED_LAYERS,
    CENSUS_WALK_CONFIG,
    FIELD_CLASSIFICATION,
    FRESH_KILL_WINDOW_TICKS,
    IN_VENT_CAP_TICKS,
    KILL_TICK_BODY_HANDLE_PATTERN,
    OWN_KILL_ROW_TEXT,
    PREDICATES,
    SETTING_DEFAULTS,
    TABLES,
    AlibiFact,
    BallotFact,
    BodyFact,
    CellCount,
    CensusCell,
    CensusInputs,
    CensusTable,
    CensusTally,
    DiscardedAction,
    EraKey,
    FieldUse,
    Frame,
    GameFacts,
    GameplayCensusConformanceError,
    GameplayCensusEraError,
    GameplayCensusFieldError,
    KillFact,
    MeetingFact,
    ObservationFact,
    OwnKillRowFact,
    SettingPredicate,
    SettingValue,
    TurnFact,
    VentFact,
    canonical_settings,
    census_from_inputs,
    fold_set,
    pool,
    prompt_stamps_from_cell,
    resolve_era,
    section_from_tally,
    selector_pick,
    served_own_kill_rows,
    setting_value,
)
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    ReplayWalkEvent,
    TickAdvanced,
    TickOpened,
    WalkComplete,
)
from eval.validity import roles_by_seed
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    TaskActivityAccount,
    WhereaboutsClaim,
)
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    RecordedExperimentConfig,
    wave_settings,
)
from tests._helpers.committed import (
    SAMPLES_4P1I,
    SAMPLES_9P2I,
    census_inputs,
    census_walk_events,
    repo_root,
)

MAP = load_canonical_map()
PLANTED = "planted/set"
SEED = 7
ROLES: Mapping[str, str] = MappingProxyType(
    {
        "p-0": "IMPOSTOR",
        "p-1": "IMPOSTOR",
        "p-2": "CREWMATE",
        "p-3": "CREWMATE",
        "p-4": "CREWMATE",
    }
)
ROOM = "STORAGE"
NEIGHBOUR = MAP.room_neighbors(ROOM)[0]
FAR = next(
    room
    for room in sorted(MAP.rooms)
    if room != ROOM and room not in MAP.room_neighbors(ROOM)
)


# --------------------------------------------------------------------------- #
# Builders                                                                     #
# --------------------------------------------------------------------------- #


def era(**settings: SettingValue) -> EraKey:
    return EraKey(
        settings=canonical_settings(settings),
        temporal_observation_version=None,
        substrate_flags=None,
        prompt_stamps=None,
    )


def frame(rooms: Mapping[str, str], *, sabotage: bool = False) -> Frame:
    return Frame(rooms=MappingProxyType(dict(rooms)), sabotage_active=sabotage)


def entry(
    tick: int,
    actor: str = "p-0",
    room: str = ROOM,
    *,
    source: Iterable[str] = (),
    destination: Iterable[str] = (),
) -> VentFact:
    return VentFact(
        tick=tick,
        actor=actor,
        kind="entry",
        source_room=room,
        destination_room=room,
        source_witnesses=frozenset(source),
        destination_witnesses=frozenset(destination),
    )


def exit_(
    tick: int,
    actor: str = "p-0",
    source_room: str = ROOM,
    destination_room: str = NEIGHBOUR,
    *,
    source: Iterable[str] = (),
    destination: Iterable[str] = (),
) -> VentFact:
    return VentFact(
        tick=tick,
        actor=actor,
        kind="exit",
        source_room=source_room,
        destination_room=destination_room,
        source_witnesses=frozenset(source),
        destination_witnesses=frozenset(destination),
    )


def kill(
    tick: int,
    killer: str = "p-0",
    room: str = ROOM,
    witnesses: Iterable[str] = (),
) -> KillFact:
    return KillFact(
        tick=tick,
        killer=killer,
        room=room,
        witnesses=frozenset(witnesses),
    )


def turn(
    index: int,
    speaker: str,
    *,
    accuses: Iterable[str] = (),
    reply_to: str | None = None,
    observations: Iterable[ObservationFact] = (),
    alibis: Iterable[AlibiFact] = (),
) -> TurnFact:
    return TurnFact(
        turn_id=f"t{index}",
        index=index,
        speaker=speaker,
        reply_to=reply_to,
        accusations=tuple(accuses),
        observations=tuple(observations),
        alibis=tuple(alibis),
    )


def seen(kind: str, tick: int, subject: str | None = None) -> ObservationFact:
    return ObservationFact(kind=kind, from_tick=tick, to_tick=tick, subject=subject)


def ballot(
    voter: str,
    target: str,
    *,
    authored: str | None = None,
    confidence: float = 0.9,
    label: str | None = None,
    cited: str | None = None,
) -> BallotFact:
    return BallotFact(
        voter=voter,
        target=target,
        authored_target=target if authored is None else authored,
        confidence=confidence,
        grounding_label=label,
        cited_observation_id=cited,
    )


def meeting(**overrides: Any) -> MeetingFact:
    fields: dict[str, Any] = {
        "meeting_id": "meeting-0",
        "tick": 20,
        "trigger_kind": "emergency",
        "opener": "p-2",
        "trigger_body": None,
        "bodies_at_open": (),
        "in_vent_at_open": frozenset(),
        "impostor_cooldowns_at_open": (),
        "living": frozenset(ROLES),
        "sabotage_active": False,
        "outcome": "SKIPPED",
        "ejected": None,
        "vent_flag_subjects": (),
        "turns": (),
        "ballots": (),
        "ballot_floor": 0.6,
        "selector_pick": None,
        "opener_prompt_has_kill_tick_handle": None,
        "own_kill_rows": (),
        "trigger_tick_dropped_events": (),
        "phase_after": "PLAY",
        "in_vent_after": frozenset(),
        "bodies_after": frozenset(),
        "regrouped": False,
    }
    fields.update(overrides)
    return MeetingFact(**fields)


def game(
    settings: Mapping[str, SettingValue] | None = None, **overrides: Any
) -> GameFacts:
    fields: dict[str, Any] = {
        "seed": SEED,
        "roles": ROLES,
        "era": era(**(settings or {})),
        "kills": (),
        "vents": (),
        "bodies": (),
        "frames": MappingProxyType({}),
        "meetings": (),
        "discarded": (),
        "rows_without_dispositions": 0,
        "winner": "CREWMATES",
        "terminal_tick": 60,
    }
    fields.update(overrides)
    if isinstance(fields["frames"], dict):
        fields["frames"] = MappingProxyType(fields["frames"])
    return GameFacts(**fields)


def inputs(*games: GameFacts, label: str = PLANTED) -> CensusInputs:
    return CensusInputs(
        label=label,
        source=f"replays/{label}",
        era=resolve_era(tuple(item.era for item in games)),
        kill_cooldown_ticks=MAP.kill_cooldown_ticks,
        neighbours=MappingProxyType(
            {room: MAP.room_neighbors(room) for room in sorted(MAP.rooms)}
        ),
        games=games,
    )


def cell(key: str, *games: GameFacts) -> CensusCell:
    return section_from_tally(fold_set(inputs(*games))).cells[key]


def counts(key: str, *games: GameFacts) -> tuple[int, int, int]:
    folded = cell(key, *games)
    return (folded.numerator, folded.denominator, folded.not_evaluable)


def table(key: str, *games: GameFacts) -> dict[str, int]:
    return dict(section_from_tally(fold_set(inputs(*games))).tables[key].counts)


def report(
    tick: int, body: str, *, meeting_id: str = "meeting-0", **overrides: Any
) -> MeetingFact:
    return meeting(
        meeting_id=meeting_id,
        tick=tick,
        trigger_kind="report",
        trigger_body=body,
        **overrides,
    )


def body(body_id: str, kill_tick: int) -> BodyFact:
    return BodyFact(body_id=body_id, kill_tick=kill_tick)


# --------------------------------------------------------------------------- #
# Shape: a carrier of ids, rooms, ticks, kinds, labels and booleans           #
# --------------------------------------------------------------------------- #

#: Every carrier field allowed to hold text: ids, rooms, kinds and labels.
ALLOWED_STRING_FIELDS = frozenset(
    {
        "CensusInputs.label",
        "CensusInputs.source",
        "CensusInputs.neighbours",
        "EraKey.settings",
        "EraKey.substrate_flags",
        "EraKey.prompt_stamps",
        "GameFacts.roles",
        "GameFacts.frames",
        "GameFacts.winner",
        "KillFact.killer",
        "KillFact.room",
        "KillFact.witnesses",
        "VentFact.actor",
        "VentFact.source_room",
        "VentFact.destination_room",
        "VentFact.source_witnesses",
        "VentFact.destination_witnesses",
        "BodyFact.body_id",
        "Frame.rooms",
        "ObservationFact.kind",
        "ObservationFact.subject",
        "AlibiFact.subject",
        "AlibiFact.legs",
        "TurnFact.turn_id",
        "TurnFact.speaker",
        "TurnFact.reply_to",
        "TurnFact.accusations",
        "BallotFact.voter",
        "BallotFact.target",
        "BallotFact.authored_target",
        "BallotFact.grounding_label",
        "BallotFact.cited_observation_id",
        "OwnKillRowFact.holder",
        "OwnKillRowFact.subject",
        "OwnKillRowFact.room",
        "OwnKillRowFact.citation_id",
        "MeetingFact.meeting_id",
        "MeetingFact.trigger_kind",
        "MeetingFact.opener",
        "MeetingFact.trigger_body",
        "MeetingFact.bodies_at_open",
        "MeetingFact.in_vent_at_open",
        "MeetingFact.impostor_cooldowns_at_open",
        "MeetingFact.living",
        "MeetingFact.outcome",
        "MeetingFact.ejected",
        "MeetingFact.vent_flag_subjects",
        "MeetingFact.selector_pick",
        "MeetingFact.trigger_tick_dropped_events",
        "MeetingFact.phase_after",
        "MeetingFact.in_vent_after",
        "MeetingFact.bodies_after",
        "DiscardedAction.action_type",
    }
)


def _parts(annotation: Any) -> Iterator[Any]:
    yield annotation
    for argument in get_args(annotation):
        yield from _parts(argument)


def carrier_problems(root: type) -> list[str]:
    """Every carrier field that holds unapproved text, is mutable, or is thawed."""

    problems: list[str] = []
    seen_types: set[type] = set()
    pending = [root]
    while pending:
        model = pending.pop()
        if model in seen_types:
            continue
        seen_types.add(model)
        if not dataclasses.is_dataclass(model):
            continue
        if not model.__dataclass_params__.frozen:  # type: ignore[attr-defined]
            problems.append(f"{model.__name__} is not frozen")
        hints = typing.get_type_hints(model, globalns={**vars(census), **globals()})
        for entry_field in dataclasses.fields(model):
            name = f"{model.__name__}.{entry_field.name}"
            for part in _parts(hints[entry_field.name]):
                if part is str and name not in ALLOWED_STRING_FIELDS:
                    problems.append(f"{name} holds text")
                if (get_origin(part) or part) in (dict, list, set):
                    problems.append(f"{name} is a mutable container")
                if isinstance(part, type) and dataclasses.is_dataclass(part):
                    pending.append(part)
    return sorted(set(problems))


def test_the_carrier_holds_only_ids_rooms_kinds_and_labels() -> None:
    assert carrier_problems(CensusInputs) == []


@dataclasses.dataclass(frozen=True)
class Planted:
    rationale: str


@dataclasses.dataclass(frozen=True)
class Carrier:
    label: str
    rows: tuple[Planted, ...]


@dataclasses.dataclass
class Thawed:
    rows: list[int]


def test_a_carrier_holding_a_rationale_fails_the_shape_check() -> None:
    assert carrier_problems(Carrier) == [
        "Carrier.label holds text",
        "Planted.rationale holds text",
    ]


def test_a_thawed_or_mutable_carrier_fails_the_shape_check() -> None:
    assert carrier_problems(Thawed) == [
        "Thawed is not frozen",
        "Thawed.rows is a mutable container",
    ]


def test_every_census_record_type_is_frozen() -> None:
    """Explicit objects own state: only the fold's own accumulator is mutable."""

    records = [
        value
        for value in vars(census).values()
        if isinstance(value, type) and value.__module__ == census.__name__
    ]
    dataclass_types = [value for value in records if dataclasses.is_dataclass(value)]
    models = [value for value in records if issubclass(value, BaseModel)]
    assert len(dataclass_types) > 10 and len(models) > 5
    thawed = {
        value.__name__
        for value in dataclass_types
        if not value.__dataclass_params__.frozen  # type: ignore[attr-defined]
    }
    assert thawed == {"_Accumulator"}
    assert all(model.model_config.get("frozen") for model in models)


def test_the_json_keeps_text_as_written() -> None:
    view = census.EraView(
        settings={},
        temporal_observation_version=None,
        substrate_flags=None,
        prompt_stamps=("caf\u00e9.x.v1",),
    )
    assert "caf\u00e9.x.v1" in census.serialize_json(view)


def test_pool_adds_counts_and_recomputes_the_rate_from_them() -> None:
    small = fold_set(inputs(game(kills=(kill(5, witnesses=("p-2",)),))))
    large = fold_set(
        inputs(
            game(kills=tuple(kill(tick) for tick in range(10, 19))),
            label="planted/other",
        )
    )
    pooled = section_from_tally(pool([small, large], label="both"))
    folded = pooled.cells["kills_seen_by_crew"]
    assert (folded.numerator, folded.denominator) == (1, 10)
    assert folded.rate == 0.1  # not the mean of 1/1 and 0/9
    assert pooled.sources == ("replays/planted/set", "replays/planted/other")
    assert pooled.games == 2


def test_pool_adds_tables_and_their_not_evaluable_counts() -> None:
    first = fold_set(inputs(game(discarded=(DiscardedAction(3, "move"),))))
    second = fold_set(
        inputs(
            game(discarded=(DiscardedAction(4, "move"),), rows_without_dispositions=2),
            label="planted/other",
        )
    )
    pooled = section_from_tally(pool([first, second], label="both"))
    thrown = pooled.tables["actions_thrown_away_on_trigger_ticks"]
    assert dict(thrown.counts) == {"move": 2}
    assert thrown.not_evaluable == 2


# --------------------------------------------------------------------------- #
# The walk profile and the field classification                               #
# --------------------------------------------------------------------------- #


def test_the_walk_profile_is_the_current_report_profile_plus_three_refusals() -> None:
    assert CENSUS_WALK_CONFIG == replace(
        _CURRENT_REPORT_WALK_CONFIG,
        profile="gameplay-census",
        missing_meeting_row="violation",
        reject_duplicate_meeting_rows=True,
        require_terminal_tick=True,
        threaded_layers=CENSUS_THREADED_LAYERS,
    )
    assert CENSUS_WALK_CONFIG.supports_experiments
    assert CENSUS_WALK_CONFIG.verify_tick_hashes
    assert CENSUS_WALK_CONFIG.verify_meeting_post_hashes


def test_the_census_declares_its_own_layers_every_one_it_classifies() -> None:
    """The census names each declarable layer, and classifies every field in it.

    The declaration is the census's own: the profile above sets it in its
    ``replace``, so a change to the current-report profile's layers cannot reach
    it. Engine fields are the spine helper's; the format field is read by every
    walk.
    """

    assert CENSUS_WALK_CONFIG.threaded_layers == CENSUS_THREADED_LAYERS
    assert CENSUS_THREADED_LAYERS == frozenset({"orchestrator", "tactical", "meeting"})
    assert CENSUS_THREADED_LAYERS == frozenset(FIELD_LAYER.values()) - {
        "engine",
        "format",
    }
    for name, layer in FIELD_LAYER.items():
        if layer in CENSUS_THREADED_LAYERS:
            assert name in FIELD_CLASSIFICATION, name


def classification_problems(
    fields: Iterable[str], classification: Mapping[str, FieldUse]
) -> list[str]:
    """Each recorded field left unclassified, and each classified name not recorded."""

    declared = set(fields)
    return [
        f"unclassified {name}" for name in sorted(declared - set(classification))
    ] + [
        f"not a recorded field {name}"
        for name in sorted(set(classification) - declared)
    ]


def test_every_recorded_setting_field_is_classified() -> None:
    assert (
        classification_problems(
            RecordedExperimentConfig.model_fields, FIELD_CLASSIFICATION
        )
        == []
    )


def test_a_classification_missing_one_field_fails() -> None:
    planted = {
        name: use
        for name, use in FIELD_CLASSIFICATION.items()
        if name != "meeting_reset"
    }
    assert classification_problems(RecordedExperimentConfig.model_fields, planted) == [
        "unclassified meeting_reset"
    ]


# History: a tripwire held five fields undeclared until the spine merged (8df69e15).
def test_a_classification_naming_an_undeclared_field_fails() -> None:
    planted = {
        **FIELD_CLASSIFICATION,
        "hidden_travel": FieldUse(predicates=("always",)),
    }
    assert classification_problems(RecordedExperimentConfig.model_fields, planted) == [
        "not a recorded field hidden_travel"
    ]


def test_the_defaults_match_the_config_model() -> None:
    for name, declared in RecordedExperimentConfig.model_fields.items():
        assert SETTING_DEFAULTS[name] == declared.default, name


def test_a_default_follows_the_config_models_declaration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Moved(RecordedExperimentConfig):
        vent_entry_policy: typing.Literal["any_body", "own_fresh_kill"] = (
            "own_fresh_kill"
        )

    assert census._field_default("vent_entry_policy") == "any_body"
    monkeypatch.setattr(census, "RecordedExperimentConfig", _Moved)
    assert census._field_default("vent_entry_policy") == "own_fresh_kill"


def test_a_classified_field_the_config_does_not_declare_has_no_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        census,
        "FIELD_CLASSIFICATION",
        MappingProxyType(
            {**FIELD_CLASSIFICATION, "hidden_travel": FieldUse(predicates=("always",))}
        ),
    )
    with pytest.raises(GameplayCensusFieldError, match="not declared on the recorded"):
        census._field_default("hidden_travel")


def test_the_classification_and_the_predicates_name_each_other() -> None:
    for predicate in PREDICATES.values():
        for name, _value in predicate.conditions:
            assert predicate.key in FIELD_CLASSIFICATION[name].predicates, name
    for name, use in FIELD_CLASSIFICATION.items():
        for key in use.predicates:
            assert name in {field for field, _ in PREDICATES[key].conditions}, name
    guards = {spec.guard.key for spec in CELLS.values() if spec.guard is not None}
    assert guards == set(PREDICATES)


def test_an_unknown_recorded_setting_raises() -> None:
    with pytest.raises(GameplayCensusFieldError, match="not classified"):
        canonical_settings({"hidden_travel": "on"})
    with pytest.raises(GameplayCensusFieldError, match="not classified"):
        setting_value({}, "hidden_travel")
    with pytest.raises(GameplayCensusFieldError, match="not classified"):
        game(
            era=EraKey(
                settings=(("hidden_travel", "on"),),
                temporal_observation_version=None,
                substrate_flags=None,
                prompt_stamps=None,
            )
        )


def test_an_era_holding_a_default_value_is_refused() -> None:
    with pytest.raises(GameplayCensusFieldError, match="canonical"):
        EraKey(
            settings=(("meeting_reset", "preserve"),),
            temporal_observation_version=None,
            substrate_flags=None,
            prompt_stamps=None,
        )


def test_a_missing_setting_reads_its_historical_default() -> None:
    assert setting_value({}, "vent_witness_rule") == "both_rooms"
    assert setting_value({}, "meeting_reset") == "preserve"
    assert setting_value({"meeting_reset": "hub_with_grace"}, "meeting_reset") == (
        "hub_with_grace"
    )


def test_a_default_is_read_only_for_a_classified_field() -> None:
    assert census._field_default("vent_entry_policy") == "any_body"
    assert census._field_default("sabotage_threshold") == "six_sevenths"
    with pytest.raises(GameplayCensusFieldError, match="not classified"):
        census._field_default("hidden_travel")


def test_predicates_and_field_uses_refuse_an_ambiguous_shape() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        SettingPredicate(key="both", conditions=(("self_report", True),), always=True)
    with pytest.raises(ValueError, match="exactly one"):
        SettingPredicate(key="neither", conditions=())
    with pytest.raises(ValueError, match="for a reason"):
        FieldUse(predicates=())
    with pytest.raises(ValueError, match="for a reason"):
        FieldUse(predicates=("always",), reason="both")


def test_a_predicate_describes_its_setting_and_value() -> None:
    assert census.NO_IMPOSTOR_SELF_REPORT.describe() == (
        "self_report = off and contextual_self_report_version = unset"
    )
    assert census.PUBLIC_BODY_HANDLE.describe() == "report_body_handle_version = 1"
    assert census.ALWAYS.describe() == "always"
    assert census.ALWAYS.holds({})
    assert not census.PHYSICAL_VENT_WITNESS.holds({})
    assert census.PHYSICAL_VENT_WITNESS.holds({"vent_witness_rule": "physical"})
    assert census.OWN_FRESH_KILL_ENTRY.holds({"vent_entry_policy": "own_fresh_kill"})
    assert census.LOOK_AND_WAIT_EXIT.holds({"vent_exit_policy": "look_and_wait"})
    assert census.MEETING_REGROUP.holds({"meeting_reset": "hub_with_grace"})
    assert census.BOUNDED_REBUTTAL.holds({"bounded_rebuttal_version": 1})
    assert census.NO_REBUTTAL.holds({})
    assert census.OWN_KILL_BALLOT_ROW.holds({"ballot_kill_row_version": 1})
    assert "on" == census._render_value(True)


# --------------------------------------------------------------------------- #
# The figures, read from the committed JSON                                    #
# --------------------------------------------------------------------------- #


def _published() -> dict[str, Any]:
    payload: dict[str, Any] = json.loads(
        (repo_root / "docs" / "gameplay-census.json").read_text(encoding="utf-8")
    )
    return payload


def _pair(section: Mapping[str, Any], key: str) -> tuple[int, int]:
    folded = section["cells"][key]
    return (folded["numerator"], folded["denominator"])


def test_the_committed_json_reproduces_the_figures() -> None:
    """The acceptance figures, re-measured at the branch head through the fold."""

    payload = _published()
    pooled = payload["pooled"]
    nine = payload["pooled_9p2i"]
    assert _pair(pooled, "kills_seen_by_crew") == (20, 849)
    assert _pair(pooled, "vent_entries_seen_by_crew") == (73, 587)
    assert _pair(pooled, "vent_exits_seen_by_crew") == (313, 512)
    assert _pair(pooled, "vent_exits_seen_from_exit_room") == (251, 512)
    assert _pair(pooled, "vent_exits_seen_only_from_room_left") == (62, 512)
    assert _pair(pooled, "impostors_seen_venting_ejected") == (330, 355)
    assert _pair(pooled, "impostors_vented_unseen_ejected") == (13, 89)
    assert _pair(pooled, "impostors_never_vented_ejected") == (26, 56)
    proof = _pair(pooled, "meetings_with_vent_proof")
    assert proof == (330, 676) and proof[1] - proof[0] == 346
    assert _pair(pooled, "vent_band_impostor_ejections") == (326, 369)
    assert pooled["tables"]["vent_band_by_moment"]["counts"] == {
        "both": 10,
        "entry only": 63,
        "exit only": 253,
    }
    assert _pair(pooled, "impostor_ejections_without_vent_proof") == (43, 369)
    assert _pair(pooled, "vent_band_resting_only_on_room_left") == (50, 326)
    assert _pair(nine, "stale_report_meetings") == (167, 551)
    assert _pair(pooled, "meetings_opening_with_another_unreported_corpse") == (
        335,
        676,
    )
    assert _pair(pooled, "first_reply_accuses_opener") == (521, 676)
    assert _pair(pooled, "opener_speaks_again") == (0, 676)
    assert _pair(pooled, "openers_among_innocent_ejections") == (38, 42)
    assert pooled["tables"]["innocent_opener_ejections_by_trigger"]["counts"] == {
        "emergency": 1,
        "report": 37,
    }
    thrown = pooled["tables"]["actions_thrown_away_on_trigger_ticks"]
    assert thrown["counts"]["move"] == 809
    assert thrown["not_evaluable"] == 0


def test_the_two_meeting_structure_counts_the_direction_cites() -> None:
    """The dated direction sentence cites these two; editing either reddens this."""

    pooled = _published()["pooled"]
    assert _pair(pooled, "first_reply_accuses_opener") == (521, 676)
    assert _pair(pooled, "opener_speaks_again") == (0, 676)
    direction = (
        repo_root / "tasks" / "direction-2026-09-19-process-over-outcome.md"
    ).read_text(encoding="utf-8")
    assert "521 of 676" in direction
    assert "0 of 676" in direction
    assert "uv run python scripts/publish_gameplay_census.py --check" in direction


def test_the_committed_sets_are_one_era() -> None:
    payload = _published()
    eras = [section["era"] for section in payload["sets"]]
    assert all(item == payload["pooled"]["era"] for item in eras)
    assert payload["pooled"]["era"]["settings"] == {}


def test_on_baseline_9_every_scoped_cell_and_table_reads_n_a() -> None:
    """No committed recording carries the in-vent cap, a regroup or a rebuttal.

    So each cell and table counted only under one of those settings publishes
    nothing in every column, and the page shows n/a rather than a measured 0.
    """

    payload = _published()
    for section in (*payload["sets"], payload["pooled_9p2i"], payload["pooled"]):
        for key, view in section["cells"].items():
            scope = SCOPED_CELLS.get(key)
            assert view["scope"] == (None if scope is None else scope.describe()), key
            assert view["in_scope"] is (scope is None), key
            if scope is not None:
                counted = (view["numerator"], view["denominator"], view["rate"])
                assert counted == (0, 0, None), key
                assert view["not_evaluable"] == 0, key
        for key, view in section["tables"].items():
            scope = SCOPED_TABLES.get(key)
            assert view["scope"] == (None if scope is None else scope.describe()), key
            assert view["in_scope"] is (scope is None), key
            if scope is not None:
                assert (view["counts"], view["not_evaluable"]) == ({}, 0), key
    page = (repo_root / "docs" / "gameplay-census.md").read_text(encoding="utf-8")
    six = " n/a |" * 6
    assert f"| Vent trips ended by a regroup |{six}" in page
    assert f"| Surfacings at the cap |{six}" in page
    assert page.count(f"| (none) |{six}") == len(SCOPED_TABLES)


# --------------------------------------------------------------------------- #
# The body's kill tick comes from the kill event                              #
# --------------------------------------------------------------------------- #


def test_corpse_age_reads_the_kill_event_tick_never_the_body_id() -> None:
    planted = game(
        kills=(kill(12),),
        bodies=(body("body-p-4-99", 12),),
        meetings=(report(20, "body-p-4-99"),),
    )
    assert table("corpse_age_at_report", planted) == {"8": 1}


def test_a_report_whose_corpse_joins_no_kill_raises() -> None:
    planted = game(meetings=(report(20, "body-p-4-99"),))
    with pytest.raises(ValueError, match="joins to no kill"):
        fold_set(inputs(planted))


# --------------------------------------------------------------------------- #
# Actions thrown away, from the recorded dispositions                          #
# --------------------------------------------------------------------------- #


def test_a_move_discarded_on_a_game_ending_trigger_tick_is_counted() -> None:
    planted = game(
        terminal_tick=30,
        winner="IMPOSTORS",
        discarded=(DiscardedAction(30, "move"), DiscardedAction(30, "do_task")),
    )
    assert table("actions_thrown_away_on_trigger_ticks", planted) == {
        "do_task": 1,
        "move": 1,
    }


def test_the_loader_reads_the_game_ending_trigger_tick_of_samples_4p1i_seed_3() -> None:
    """The 808 to 809 case: the trigger tick that ended the game is read."""

    game_three = next(
        item for item in census_inputs(SAMPLES_4P1I).games if item.seed == 3
    )
    assert game_three.terminal_tick is not None
    assert game_three.terminal_tick not in {item.tick for item in game_three.meetings}
    assert any(
        item.tick == game_three.terminal_tick and item.action_type == "move"
        for item in game_three.discarded
    )


# --------------------------------------------------------------------------- #
# Exit witnesses                                                               #
# --------------------------------------------------------------------------- #


def test_an_exit_seen_only_from_the_room_left_flips_when_the_crewmate_leaves() -> None:
    watched = game(
        vents=(entry(10), exit_(11, source=("p-2",))),
        frames={11: frame({"p-2": ROOM})},
    )
    assert counts("vent_exits_seen_by_crew", watched) == (1, 1, 0)
    assert counts("vent_exits_seen_only_from_room_left", watched) == (1, 1, 0)
    assert counts("vent_exits_seen_from_exit_room", watched) == (0, 1, 0)
    moved = game(vents=(entry(10), exit_(11)), frames={11: frame({"p-2": FAR})})
    assert counts("vent_exits_seen_by_crew", moved) == (0, 1, 0)
    assert counts("vent_exits_seen_only_from_room_left", moved) == (0, 1, 0)


def test_exit_witnesses_are_crew_only() -> None:
    planted = game(
        vents=(entry(10, source=("p-1",)), exit_(11, destination=("p-1",))),
        frames={11: frame({})},
    )
    assert counts("vent_entries_seen_by_crew", planted) == (0, 1, 0)
    assert counts("vent_exits_seen_by_crew", planted) == (0, 1, 0)
    crew = game(
        vents=(entry(10, destination=("p-3",)), exit_(11, destination=("p-3",))),
        frames={11: frame({})},
    )
    assert counts("vent_entries_seen_by_crew", crew) == (1, 1, 0)
    assert counts("vent_exits_seen_from_exit_room", crew) == (1, 1, 0)


def test_kills_seen_by_crew_ignore_an_impostor_witness() -> None:
    planted = game(kills=(kill(5, witnesses=("p-1",)), kill(9, witnesses=("p-3",))))
    assert counts("kills_seen_by_crew", planted) == (1, 2, 0)


def test_impostor_fate_splits_seen_unseen_and_never_vented() -> None:
    planted = game(
        vents=(entry(4, source=("p-2",)), exit_(5), entry(8, "p-1"), exit_(9, "p-1")),
        frames={5: frame({}), 9: frame({})},
        meetings=(meeting(outcome="EJECTED", ejected="p-1"),),
    )
    assert counts("impostors_seen_venting_ejected", planted) == (0, 1, 0)
    assert counts("impostors_vented_unseen_ejected", planted) == (1, 1, 0)
    never = game(meetings=(meeting(outcome="EJECTED", ejected="p-0"),))
    assert counts("impostors_never_vented_ejected", never) == (1, 2, 0)


# --------------------------------------------------------------------------- #
# Stale reports                                                                #
# --------------------------------------------------------------------------- #


def _stale_pair(kill_tick: int, floor: tuple[tuple[str, str | None], ...]) -> GameFacts:
    return game(
        kills=(kill(kill_tick),),
        bodies=(body("body-x", kill_tick),),
        meetings=(
            meeting(meeting_id="meeting-0", tick=10, bodies_at_open=floor),
            report(20, "body-x", meeting_id="meeting-1"),
        ),
    )


def test_a_stale_corpse_flips_to_fresh_when_its_kill_moves_after_the_last_open() -> (
    None
):
    stale = _stale_pair(8, (("body-x", None),))
    assert counts("stale_report_meetings", stale) == (1, 1, 0)
    fresh = _stale_pair(12, ())
    assert counts("stale_report_meetings", fresh) == (0, 1, 0)


def test_the_first_report_of_a_game_is_never_stale() -> None:
    planted = game(
        kills=(kill(8),),
        bodies=(body("body-x", 8),),
        meetings=(report(20, "body-x"),),
    )
    assert counts("stale_report_meetings", planted) == (0, 1, 0)


def test_a_corpse_killed_on_the_regroup_tick_is_older_than_the_regroup() -> None:
    """A kill on the regroup meeting's own tick came before that meeting opened."""

    def reported_after_regroup(kill_tick: int) -> GameFacts:
        return game(
            kills=(kill(kill_tick),),
            bodies=(body("body-x", kill_tick),),
            meetings=(
                meeting(meeting_id="meeting-0", tick=10, regrouped=True),
                report(20, "body-x", meeting_id="meeting-1"),
            ),
        )

    key = "report_corpses_older_than_last_close"
    assert counts(key, reported_after_regroup(10)) == (1, 1, 0)
    assert counts(key, reported_after_regroup(11)) == (0, 1, 0)


# --------------------------------------------------------------------------- #
# Vent proof against the vent band                                             #
# --------------------------------------------------------------------------- #


def _banded(flagged: str) -> GameFacts:
    return game(
        vents=(entry(4), exit_(5, destination=("p-2",))),
        frames={5: frame({})},
        meetings=(
            meeting(
                outcome="EJECTED",
                ejected="p-0",
                vent_flag_subjects=(frozenset({flagged}),),
            ),
        ),
    )


def test_moving_the_flag_leaves_the_band_but_keeps_the_proof() -> None:
    banded = _banded("p-0")
    assert counts("meetings_with_vent_proof", banded) == (1, 1, 0)
    assert counts("vent_band_impostor_ejections", banded) == (1, 1, 0)
    assert table("vent_band_by_moment", banded) == {"exit only": 1}
    moved = _banded("p-3")
    assert counts("meetings_with_vent_proof", moved) == (1, 1, 0)
    assert counts("vent_band_impostor_ejections", moved) == (0, 1, 0)
    assert table("vent_band_by_moment", moved) == {}


def test_a_flag_naming_only_a_dead_player_is_no_proof() -> None:
    planted = game(
        meetings=(
            meeting(
                living=frozenset(ROLES) - {"p-4"},
                vent_flag_subjects=(frozenset({"p-4"}),),
            ),
        )
    )
    assert counts("meetings_with_vent_proof", planted) == (0, 1, 0)


def test_the_moment_table_names_entry_both_and_neither() -> None:
    def ejected_after(vents: tuple[VentFact, ...]) -> GameFacts:
        return game(
            vents=vents,
            frames={tick: frame({}) for tick in range(1, 20)},
            meetings=(
                meeting(
                    outcome="EJECTED",
                    ejected="p-0",
                    vent_flag_subjects=(frozenset({"p-0"}),),
                ),
            ),
        )

    assert table(
        "vent_band_by_moment", ejected_after((entry(3, source=("p-2",)), exit_(4)))
    ) == {"entry only": 1}
    assert table(
        "vent_band_by_moment",
        ejected_after((entry(3, source=("p-2",)), exit_(4, destination=("p-3",)))),
    ) == {"both": 1}
    assert table("vent_band_by_moment", ejected_after((entry(3), exit_(4)))) == {
        "neither": 1
    }
    late = ejected_after((entry(30, source=("p-2",)),))
    assert table("vent_band_by_moment", late) == {"neither": 1}


def test_a_vent_on_the_trigger_tick_came_before_the_meeting() -> None:
    planted = game(
        vents=(entry(19), exit_(20, source=("p-2",))),
        frames={20: frame({})},
        meetings=(
            meeting(
                tick=20,
                outcome="EJECTED",
                ejected="p-0",
                vent_flag_subjects=(frozenset({"p-0"}),),
            ),
        ),
    )
    assert table("vent_band_by_moment", planted) == {"exit only": 1}
    assert counts("vent_band_resting_only_on_room_left", planted) == (1, 1, 0)


def _band_after(
    vents: tuple[VentFact, ...],
    *,
    settings: Mapping[str, SettingValue] | None = None,
    living: frozenset[str] = frozenset(ROLES),
) -> GameFacts:
    return game(
        settings,
        vents=vents,
        frames={tick: frame({}) for tick in range(1, 20)},
        meetings=(
            meeting(
                outcome="EJECTED",
                ejected="p-0",
                living=living,
                vent_flag_subjects=(frozenset({"p-0"}),),
            ),
        ),
    )


def test_resting_on_the_room_left_needs_a_living_crew_sighting() -> None:
    key = "vent_band_resting_only_on_room_left"
    seen_left = (entry(10), exit_(11, source=("p-2",)))
    assert counts(key, _band_after(seen_left)) == (1, 1, 0)
    dead_witness = _band_after(seen_left, living=frozenset(ROLES) - {"p-2"})
    assert counts(key, dead_witness) == (0, 1, 0)
    physical = {"vent_witness_rule": "physical"}
    for vents in ((), (entry(10), exit_(11))):
        unseen = _band_after(vents, settings=physical)
        assert counts(key, unseen) == (0, 1, 0), vents


def test_the_no_vent_proof_cells_and_the_crew_vent_band() -> None:
    planted = game(
        meetings=(
            meeting(meeting_id="meeting-0", tick=10, outcome="EJECTED", ejected="p-0"),
            meeting(meeting_id="meeting-1", tick=20, outcome="EJECTED", ejected="p-3"),
            meeting(
                meeting_id="meeting-2",
                tick=30,
                outcome="EJECTED",
                ejected="p-2",
                vent_flag_subjects=(frozenset({"p-2"}),),
            ),
            meeting(meeting_id="meeting-3", tick=40),
        )
    )
    assert counts("meetings_without_vent_proof_ejecting", planted) == (2, 3, 0)
    assert counts("ejections_without_vent_proof_of_impostors", planted) == (1, 2, 0)
    assert counts("impostor_ejections_without_vent_proof", planted) == (1, 1, 0)
    assert counts("vent_band_crew_ejections", planted) == (1, 2, 0)
    assert counts("button_meetings_with_vent_proof", planted) == (1, 4, 0)
    assert counts("role_correct_ejections", planted) == (1, 3, 0)


# --------------------------------------------------------------------------- #
# Impostor ballots                                                             #
# --------------------------------------------------------------------------- #


def test_an_authored_teammate_target_counts_while_the_recorded_target_skips() -> None:
    planted = game(
        meetings=(meeting(ballots=(ballot("p-0", "SKIP", authored="p-1"),)),)
    )
    assert counts("authored_teammate_ballot_targets", planted) == (1, 1, 0)
    assert counts("recorded_teammate_ballot_targets", planted) == (0, 1, 0)
    assert counts("impostor_skip_ballots", planted) == (1, 1, 0)


def test_impostor_ballot_cells_read_only_impostor_ballots() -> None:
    planted = game(
        meetings=(
            meeting(
                ballots=(
                    ballot("p-0", "p-2", label="supported"),
                    ballot("p-1", "p-3", label="uncited"),
                    ballot("p-2", "p-0", label="supported"),
                    ballot("p-3", "SKIP"),
                )
            ),
        )
    )
    assert counts("impostor_eject_ballots", planted) == (2, 2, 0)
    assert counts("impostor_skip_ballots", planted) == (0, 2, 0)
    assert counts("impostor_ejects_labelled_supported", planted) == (1, 2, 0)


def test_an_ejection_carried_only_by_impostor_ballots_reads_the_recorded_floor() -> (
    None
):
    def ejection(floor: float) -> GameFacts:
        return game(
            meetings=(
                meeting(
                    outcome="EJECTED",
                    ejected="p-2",
                    ballot_floor=floor,
                    ballots=(
                        ballot("p-0", "p-2", confidence=0.9),
                        ballot("p-1", "p-2", confidence=0.9),
                        ballot("p-3", "p-2", confidence=0.5),
                    ),
                ),
            )
        )

    assert counts("ejections_carried_only_by_impostor_ballots", ejection(0.6)) == (
        1,
        1,
        0,
    )
    assert counts("ejections_carried_only_by_impostor_ballots", ejection(0.5)) == (
        0,
        1,
        0,
    )


def test_a_kill_witness_held_voted_and_ejected() -> None:
    planted = game(
        kills=(
            kill(5, witnesses=("p-2",)),
            kill(15, witnesses=("p-3",)),
            kill(50, witnesses=("p-4",)),
        ),
        meetings=(
            meeting(
                meeting_id="meeting-0",
                tick=10,
                outcome="EJECTED",
                ejected="p-0",
                ballots=(ballot("p-2", "p-0"),),
            ),
            meeting(
                meeting_id="meeting-1",
                tick=20,
                living=frozenset(ROLES) - {"p-3"},
            ),
        ),
    )
    assert counts("crew_witnessed_kills_held_at_next_meeting", planted) == (1, 2, 1)
    assert counts("held_kill_witnesses_voting_killer", planted) == (1, 1, 0)
    assert counts("held_kill_killers_ejected", planted) == (1, 1, 0)


def test_a_kill_on_the_trigger_tick_is_held_by_that_meeting() -> None:
    planted = game(
        kills=(kill(20, witnesses=("p-2",)),),
        meetings=(meeting(tick=20, ballots=(ballot("p-2", "p-0"),)),),
    )
    assert counts("crew_witnessed_kills_held_at_next_meeting", planted) == (1, 1, 0)
    assert counts("held_kill_witnesses_voting_killer", planted) == (1, 1, 0)


def test_only_a_living_witness_naming_the_killer_votes_the_killer() -> None:
    for ballots in (
        (ballot("p-2", "SKIP"), ballot("p-3", "p-0")),
        (ballot("p-2", "p-1"),),
    ):
        planted = game(
            kills=(kill(5, witnesses=("p-2",)),),
            meetings=(meeting(tick=10, ballots=ballots),),
        )
        assert counts("held_kill_witnesses_voting_killer", planted) == (0, 1, 0)


# --------------------------------------------------------------------------- #
# Eras                                                                         #
# --------------------------------------------------------------------------- #


def test_pooling_two_eras_raises() -> None:
    baseline = fold_set(inputs(game()))
    regrouped = fold_set(
        inputs(game({"meeting_reset": "hub_with_grace"}), label="planted/other")
    )
    with pytest.raises(GameplayCensusEraError, match="settings"):
        pool([baseline, regrouped], label="both")


def test_a_set_mixing_two_eras_raises() -> None:
    mixed = (game(), game({"meeting_reset": "hub_with_grace"}, seed=8))
    with pytest.raises(GameplayCensusEraError):
        inputs(*mixed)
    with pytest.raises(GameplayCensusEraError, match="differ in settings"):
        fold_set(replace(inputs(mixed[0]), games=mixed))
    with pytest.raises(GameplayCensusEraError, match="disagrees"):
        fold_set(replace(inputs(mixed[0]), era=mixed[1].era))


def test_eras_differ_by_temporal_version_substrate_or_prompt_stamps() -> None:
    base = era()
    for changed in (
        replace(base, temporal_observation_version=2),
        replace(base, substrate_flags=(("reporter_reasoning", True),)),
    ):
        with pytest.raises(GameplayCensusEraError):
            resolve_era((base, changed))
    stamped = replace(base, prompt_stamps=("vote_ballot.qwen3_6_27b.v8",))
    restamped = replace(base, prompt_stamps=("vote_ballot.qwen3_6_27b.v9",))
    with pytest.raises(GameplayCensusEraError, match="prompt stamps"):
        resolve_era((stamped, restamped))
    assert resolve_era((base, stamped)) == stamped
    with pytest.raises(GameplayCensusEraError, match="no games"):
        resolve_era(())


def test_the_ruled_prompt_stamp_reads_samples_4p1i_as_one_era() -> None:
    """Perturbed: taking a stamp from every MANIFEST row splits the set."""

    loaded = census_inputs(SAMPLES_4P1I)
    assert resolve_era(tuple(item.era for item in loaded.games)) == loaded.era
    without_meetings = [item for item in loaded.games if not item.meetings]
    assert len(without_meetings) == 11
    assert all(item.era.prompt_stamps is None for item in without_meetings)
    cells = census._manifest_prompt_cells(SAMPLES_4P1I)
    every_row = tuple(
        replace(item.era, prompt_stamps=tuple(cells[item.seed].split(", ")))
        for item in loaded.games
    )
    with pytest.raises(GameplayCensusEraError, match="prompt stamps"):
        resolve_era(every_row)


def test_a_manifest_cell_naming_no_stamp_is_refused_for_a_game_with_a_meeting() -> None:
    assert prompt_stamps_from_cell("b.x.v2, a.x.v1") == ("a.x.v1", "b.x.v2")
    with pytest.raises(ValueError, match="names no prompt stamp"):
        prompt_stamps_from_cell("(none — no meetings)")
    with pytest.raises(ValueError, match="names no prompt stamp"):
        prompt_stamps_from_cell("a.x.v1, ")


# --------------------------------------------------------------------------- #
# Conformance guards: one pair per row                                         #
# --------------------------------------------------------------------------- #


def _exit_only_from_room_left(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        vents=(entry(10), exit_(11, source=("p-2",))),
        frames={11: frame({"p-2": FAR})},
    )


def _band_on_room_left(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        vents=(entry(10), exit_(11, source=("p-2",), destination=("p-3",))),
        frames={11: frame({})},
        meetings=(
            meeting(
                outcome="EJECTED",
                ejected="p-0",
                living=frozenset(ROLES) - {"p-3"},
                vent_flag_subjects=(frozenset({"p-0"}),),
            ),
        ),
    )


def _entry_without_fresh_kill(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(settings, vents=(entry(10), exit_(11)), frames={11: frame({})})


def _surfacing_in_view(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        vents=(entry(10), exit_(11)),
        frames={11: frame({"p-2": ROOM})},
    )


def _trip_over_cap(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(settings, vents=(entry(10), exit_(15)), frames={15: frame({})})


def _stale(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        kills=(kill(8),),
        bodies=(body("body-x", 8),),
        meetings=(
            meeting(
                meeting_id="meeting-0", tick=10, bodies_at_open=(("body-x", None),)
            ),
            report(20, "body-x", meeting_id="meeting-1"),
        ),
    )


def _resume_in_vent(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(settings, meetings=(meeting(in_vent_after=frozenset({"p-0"})),))


def _resume_with_corpse(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(settings, meetings=(meeting(bodies_after=frozenset({"body-x"})),))


def _grace_kill(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        kills=(kill(10 + MAP.kill_cooldown_ticks),),
        meetings=(meeting(tick=10, regrouped=True),),
    )


def _corpse_before_close(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        kills=(kill(9),),
        bodies=(body("body-x", 9),),
        meetings=(
            meeting(meeting_id="meeting-0", tick=10, regrouped=True),
            report(20, "body-x", meeting_id="meeting-1"),
        ),
    )


def _handle_in_opening(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        kills=(kill(18),),
        bodies=(body("body-x", 18),),
        meetings=(report(20, "body-x", opener_prompt_has_kill_tick_handle=True),),
    )


def _rebuttal_off_pick(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-2",), reply_to="t0"),
                    turn(2, "p-2", reply_to="t1"),
                ),
                selector_pick=("p-3", "t0"),
            ),
        ),
    )


def _repeat_speaker(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2", accuses=("p-0",)),
                    turn(1, "p-3", accuses=("p-0",), reply_to="t0"),
                    turn(2, "p-4", accuses=("p-3",), reply_to="t1"),
                    turn(3, "p-3", reply_to="t2"),
                ),
                selector_pick=("p-3", "t2"),
            ),
        ),
    )


def _opener_answers(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-2",), reply_to="t0"),
                    turn(2, "p-2", reply_to="t1"),
                ),
                selector_pick=("p-2", "t1"),
            ),
        ),
    )


def _impostor_opener(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(settings, meetings=(meeting(opener="p-0"),))


def _own_kill_row_of_teammate(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        kills=(kill(12, witnesses=("p-1",)),),
        meetings=(
            meeting(
                own_kill_rows=(OwnKillRowFact("p-1", "p-0", ROOM, 13, "p-1:13:0"),)
            ),
        ),
    )


def _own_kill_row_of_non_witness(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        kills=(kill(12),),
        meetings=(
            meeting(
                own_kill_rows=(OwnKillRowFact("p-2", "p-0", ROOM, 13, "p-2:13:0"),)
            ),
        ),
    )


def _own_kill_row_of_teammate_citing_nothing(
    settings: Mapping[str, SettingValue],
) -> GameFacts:
    """The row names its killer, so a teammate row breaches with no citation."""

    return game(
        settings,
        kills=(kill(12, witnesses=("p-1",)),),
        meetings=(
            meeting(own_kill_rows=(OwnKillRowFact("p-1", "p-0", ROOM, 13, None),)),
        ),
    )


def _own_kill_row_citing_nothing(settings: Mapping[str, SettingValue]) -> GameFacts:
    """A witness's row served without its kill's id joins no kill."""

    return game(
        settings,
        kills=(kill(12, witnesses=("p-2",)),),
        meetings=(
            meeting(own_kill_rows=(OwnKillRowFact("p-2", "p-0", ROOM, 13, None),)),
        ),
    )


def _own_kill_row_naming_another_killer(
    settings: Mapping[str, SettingValue],
) -> GameFacts:
    """The cited kill was witnessed, but the row names someone else as killer."""

    return game(
        settings,
        kills=(kill(12, killer="p-1", witnesses=("p-2",)),),
        meetings=(
            meeting(
                own_kill_rows=(OwnKillRowFact("p-2", "p-0", ROOM, 13, "p-2:13:0"),)
            ),
        ),
    )


GUARD_PAIRS: tuple[
    tuple[
        str,
        Callable[[Mapping[str, SettingValue]], GameFacts],
        Mapping[str, SettingValue],
        Mapping[str, SettingValue],
        str,
    ],
    ...,
] = (
    (
        "vent_exits_seen_only_from_room_left",
        _exit_only_from_room_left,
        {"vent_witness_rule": "physical"},
        {},
        "tick 11",
    ),
    (
        "vent_band_resting_only_on_room_left",
        _band_on_room_left,
        {"vent_witness_rule": "physical"},
        {},
        "meeting meeting-0",
    ),
    (
        "vent_entries_not_after_own_fresh_kill",
        _entry_without_fresh_kill,
        {"vent_entry_policy": "own_fresh_kill"},
        {},
        "tick 10",
    ),
    (
        "surfacings_before_cap_in_view",
        _surfacing_in_view,
        {"vent_exit_policy": "look_and_wait"},
        {},
        "tick 11",
    ),
    (
        "trips_longer_than_cap",
        _trip_over_cap,
        {"vent_exit_policy": "look_and_wait"},
        {},
        "tick 15",
    ),
    (
        "stale_report_meetings",
        _stale,
        {"meeting_reset": "hub_with_grace"},
        {},
        "meeting meeting-1",
    ),
    (
        "play_resumes_with_impostor_in_vent",
        _resume_in_vent,
        {"meeting_reset": "hub_with_grace"},
        {},
        "meeting meeting-0",
    ),
    (
        "play_resumes_with_corpse",
        _resume_with_corpse,
        {"meeting_reset": "hub_with_grace"},
        {},
        "meeting meeting-0",
    ),
    (
        "kills_in_grace_window_after_regroup",
        _grace_kill,
        {"meeting_reset": "hub_with_grace"},
        {},
        "tick 14 after meeting meeting-0",
    ),
    (
        "report_corpses_older_than_last_close",
        _corpse_before_close,
        {"meeting_reset": "hub_with_grace"},
        {},
        "meeting meeting-1",
    ),
    (
        "report_openings_with_kill_tick_handle",
        _handle_in_opening,
        {"report_body_handle_version": 1},
        {},
        "meeting meeting-0",
    ),
    (
        "meetings_with_repeat_speaker",
        _repeat_speaker,
        {},
        {"bounded_rebuttal_version": 1},
        "meeting meeting-0",
    ),
    (
        "accused_opener_answers",
        _opener_answers,
        {},
        {"bounded_rebuttal_version": 1},
        "meeting meeting-0",
    ),
    (
        "impostor_openers",
        _impostor_opener,
        {},
        {"self_report": True},
        "meeting meeting-0",
    ),
    (
        "own_kill_rows_breaching",
        _own_kill_row_of_teammate,
        {"ballot_kill_row_version": 1},
        {},
        "meeting meeting-0, holder p-1",
    ),
    (
        "own_kill_rows_breaching",
        _own_kill_row_of_non_witness,
        {"ballot_kill_row_version": 1},
        {},
        "meeting meeting-0, holder p-2",
    ),
    (
        "own_kill_rows_breaching",
        _own_kill_row_of_teammate_citing_nothing,
        {"ballot_kill_row_version": 1},
        {},
        "meeting meeting-0, holder p-1",
    ),
    (
        "own_kill_rows_breaching",
        _own_kill_row_citing_nothing,
        {"ballot_kill_row_version": 1},
        {},
        "meeting meeting-0, holder p-2",
    ),
    (
        "own_kill_rows_breaching",
        _own_kill_row_naming_another_killer,
        {"ballot_kill_row_version": 1},
        {},
        "meeting meeting-0, holder p-2",
    ),
)


@pytest.mark.parametrize(
    ("key", "build", "on", "off", "where"),
    GUARD_PAIRS,
    ids=[f"{row[0]}-{row[1].__name__}" for row in GUARD_PAIRS],
)
def test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off(
    key: str,
    build: Callable[[Mapping[str, SettingValue]], GameFacts],
    on: Mapping[str, SettingValue],
    off: Mapping[str, SettingValue],
    where: str,
) -> None:
    with pytest.raises(GameplayCensusConformanceError) as raised:
        fold_set(inputs(build(on)))
    message = str(raised.value)
    assert CELLS[key].title in message
    assert f"set {PLANTED}, seed {SEED}, {where} " in message
    guard = CELLS[key].guard
    assert guard is not None and guard.describe() in message
    published = cell(key, build(off))
    assert published.numerator == 1 and published.denominator >= 1
    assert published.by_construction is None


def test_every_guarded_cell_has_a_planted_pair() -> None:
    planted = {row[0] for row in GUARD_PAIRS}
    always = {key for key, spec in CELLS.items() if spec.guard is census.ALWAYS}
    bounded = {"rebuttals_differing_from_selector"}
    guarded = {key for key, spec in CELLS.items() if spec.guard is not None}
    assert guarded == planted | always | bounded


def test_a_rebuttal_off_the_selector_raises_under_either_value() -> None:
    """The selector guard's pair has no publishing twin.

    With the rebuttal setting at version 1 the selector guard raises; at its
    historical default no rebuttal may exist at all, so the same fact raises the
    repeat-speaker guard instead. Two values exist, so no third publishes it.
    """

    with pytest.raises(GameplayCensusConformanceError, match="would not have chosen"):
        fold_set(inputs(_rebuttal_off_pick({"bounded_rebuttal_version": 1})))
    with pytest.raises(GameplayCensusConformanceError, match="accused opener answers"):
        fold_set(inputs(_rebuttal_off_pick({})))
    matched = _opener_answers({"bounded_rebuttal_version": 1})
    assert counts("rebuttals_differing_from_selector", matched) == (0, 1, 0)
    assert counts("opener_speaks_again", matched) == (1, 1, 0)
    assert counts("accused_opener_answers", matched) == (1, 1, 0)


@pytest.mark.parametrize("settings", ({}, {"bounded_rebuttal_version": 1}))
def test_the_always_guards_raise_under_every_setting(
    settings: Mapping[str, SettingValue],
) -> None:
    teammate = game(settings, meetings=(meeting(ballots=(ballot("p-0", "p-1"),)),))
    with pytest.raises(GameplayCensusConformanceError, match="against a teammate"):
        fold_set(inputs(teammate))
    twice = game(
        settings,
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2", accuses=("p-0",)),
                    turn(1, "p-3", accuses=("p-4",), reply_to="t0"),
                    turn(2, "p-4", accuses=("p-3",), reply_to="t1"),
                    turn(3, "p-3", reply_to="t2"),
                    turn(4, "p-4", reply_to="t3"),
                ),
                selector_pick=("p-3", "t2"),
            ),
        ),
    )
    with pytest.raises(GameplayCensusConformanceError):
        fold_set(inputs(twice))


def test_the_second_repeat_turn_is_its_own_guard() -> None:
    twice = game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2", accuses=("p-0",)),
                    turn(1, "p-3", accuses=("p-4",), reply_to="t0"),
                    turn(2, "p-4", accuses=("p-3",), reply_to="t1"),
                    turn(3, "p-3", reply_to="t2"),
                    turn(4, "p-4", reply_to="t3"),
                ),
                selector_pick=("p-3", "t2"),
            ),
        ),
    )
    with pytest.raises(GameplayCensusConformanceError, match="two repeat-speaker"):
        fold_set(inputs(twice))


def test_with_the_setting_on_an_empty_denominator_reads_n_a_never_zero() -> None:
    vacuous = cell(
        "vent_exits_seen_only_from_room_left", game({"vent_witness_rule": "physical"})
    )
    assert (vacuous.numerator, vacuous.denominator, vacuous.rate) == (0, 0, None)
    assert vacuous.by_construction == "vent_witness_rule = physical"
    zero = cell(
        "vent_exits_seen_only_from_room_left",
        game(
            {"vent_witness_rule": "physical"},
            vents=(entry(10), exit_(11, destination=("p-2",))),
            frames={11: frame({})},
        ),
    )
    assert (zero.numerator, zero.denominator, zero.rate) == (0, 1, 0.0)
    assert zero.by_construction == "vent_witness_rule = physical"


def test_a_published_cell_cannot_carry_a_nonzero_count_by_construction() -> None:
    fields: dict[str, Any] = {
        "title": "t",
        "heading": "h",
        "definition": "d",
        "reads": (),
        "numerator": 1,
        "denominator": 2,
        "not_evaluable": 0,
        "rate": 0.5,
        "guard": "always",
        "by_construction": None,
        "scope": None,
        "in_scope": True,
    }
    CensusCell(**fields)
    with pytest.raises(ValueError, match="by construction"):
        CensusCell(**{**fields, "by_construction": "always"})
    with pytest.raises(ValueError, match="quotient"):
        CensusCell(**{**fields, "rate": 0.4})
    with pytest.raises(ValueError, match="quotient"):
        CensusCell(**{**fields, "numerator": 0, "denominator": 0, "rate": 0.0})
    with pytest.raises(ValueError, match="exceeds"):
        CensusCell(**{**fields, "numerator": 3, "rate": 1.5})
    with pytest.raises(ValueError, match="non-negative"):
        CensusCell(**{**fields, "not_evaluable": -1})


def test_a_published_cell_or_table_out_of_its_scope_counts_nothing() -> None:
    """Out of its scope a cell has an empty denominator and a table no rows."""

    empty: dict[str, Any] = {
        "title": "t",
        "heading": "h",
        "definition": "d",
        "reads": (),
        "numerator": 0,
        "denominator": 0,
        "not_evaluable": 0,
        "rate": None,
        "guard": None,
        "by_construction": None,
        "scope": "meeting_reset = hub_with_grace",
        "in_scope": False,
    }
    CensusCell(**empty)
    with pytest.raises(ValueError, match="out of its scope"):
        CensusCell(**{**empty, "denominator": 2, "rate": 0.0})
    with pytest.raises(ValueError, match="out of its scope"):
        CensusCell(**{**empty, "not_evaluable": 1})
    with pytest.raises(ValueError, match="without a scope"):
        CensusCell(**{**empty, "scope": None})
    table_fields: dict[str, Any] = {
        "title": "t",
        "heading": "h",
        "definition": "d",
        "reads": (),
        "counts": {},
        "not_evaluable": 0,
        "scope": "meeting_reset = hub_with_grace",
        "in_scope": False,
    }
    CensusTable(**table_fields)
    with pytest.raises(ValueError, match="out of its scope"):
        CensusTable(**{**table_fields, "counts": {"Moved": 1}})
    with pytest.raises(ValueError, match="out of its scope"):
        CensusTable(**{**table_fields, "not_evaluable": 1})
    with pytest.raises(ValueError, match="without a scope"):
        CensusTable(**{**table_fields, "scope": None})
    CensusTable(**{**table_fields, "scope": None, "in_scope": True, "counts": {"a": 1}})


# --------------------------------------------------------------------------- #
# Scopes: counted only in games recorded with a setting                        #
# --------------------------------------------------------------------------- #

#: Every cell counted only under a recorded setting, with that setting. Each has
#: a planted case reading n/a outside it: ``forced_surfacings`` in
#: ``test_without_the_look_and_wait_exit_no_surfacing_is_at_a_cap`` and
#: ``trips_closed_by_regroup`` in
#: ``test_where_no_meeting_regroups_no_trip_is_ended_by_a_regroup``.
SCOPED_CELLS: Mapping[str, SettingPredicate] = MappingProxyType(
    {
        "forced_surfacings": census.LOOK_AND_WAIT_EXIT,
        "trips_closed_by_regroup": census.MEETING_REGROUP,
    }
)

#: Every table counted only under a recorded setting. Planted in
#: ``test_where_no_meeting_regroups_the_dropped_events_table_reads_n_a`` and
#: ``test_the_rebuttal_beneficiaries_table_is_counted_only_with_the_rebuttal_on``.
SCOPED_TABLES: Mapping[str, SettingPredicate] = MappingProxyType(
    {
        "trigger_tick_events_dropped_by_regroup": census.MEETING_REGROUP,
        "rebuttal_beneficiaries": census.BOUNDED_REBUTTAL,
    }
)


def test_the_scoped_cells_and_tables_are_exactly_these() -> None:
    cells = {key: spec.scope for key, spec in CELLS.items() if spec.scope is not None}
    tables = {key: spec.scope for key, spec in TABLES.items() if spec.scope is not None}
    assert cells == dict(SCOPED_CELLS)
    assert tables == dict(SCOPED_TABLES)
    for scope in (*cells.values(), *tables.values()):
        assert PREDICATES[scope.key] is scope


def _expected_in_scope(
    scope: SettingPredicate | None, values: Mapping[str, SettingValue]
) -> bool:
    """The scope rule restated independently of the module's helper."""

    if scope is None:
        return True
    return all(
        values.get(name, SETTING_DEFAULTS[name]) == value
        for name, value in scope.conditions
    )


_SCOPE_SETTINGS = st.fixed_dictionaries(
    {},
    optional={
        "meeting_reset": st.sampled_from(("preserve", "hub_with_grace")),
        "vent_exit_policy": st.sampled_from(
            ("target_distance", "observed_risk", "look_and_wait")
        ),
        "bounded_rebuttal_version": st.sampled_from((None, 1)),
        "vent_witness_rule": st.sampled_from(("both_rooms", "physical")),
    },
)


@hypothesis_settings(max_examples=60, deadline=None)
@given(values=_SCOPE_SETTINGS, hits=st.lists(st.booleans(), min_size=1, max_size=4))
def test_every_cell_and_table_counts_exactly_when_its_scope_holds(
    values: dict[str, SettingValue], hits: list[bool]
) -> None:
    """Property over every cell and table and a generated family of settings.

    A cell out of its scope keeps an empty denominator whatever it is handed,
    and a table out of its scope keeps no row; in scope both count as usual.
    """

    for key, spec in CELLS.items():
        accumulator = census._Accumulator(label=PLANTED, values=values)
        guard_on = spec.guard is not None and spec.guard.holds(values)
        for hit in hits:
            accumulator.count(key, hit and not guard_on, seed=SEED, where="tick 1")
        numerator = sum(hit and not guard_on for hit in hits)
        expected = (
            [numerator, len(hits), 0]
            if _expected_in_scope(spec.scope, values)
            else [0, 0, 0]
        )
        assert accumulator.cells[key] == expected, key
    for name, table_spec in TABLES.items():
        accumulator = census._Accumulator(label=PLANTED, values=values)
        accumulator.tally(name, "row", len(hits))
        rows = dict(accumulator.tables[name])
        counted = _expected_in_scope(table_spec.scope, values)
        assert rows == ({"row": len(hits)} if counted else {}), name


def setting_meaning_gaps(meanings: Mapping[str, str]) -> tuple[set[str], set[str]]:
    """Fields a guard or scope reads with no meaning, and meanings naming none."""

    predicates = [
        predicate
        for spec in CELLS.values()
        for predicate in (spec.guard, spec.scope)
        if predicate is not None
    ]
    predicates.extend(spec.scope for spec in TABLES.values() if spec.scope is not None)
    named = {name for predicate in predicates for name, _ in predicate.conditions}
    return named - set(meanings), set(meanings) - named


def test_every_setting_a_guard_or_scope_reads_has_its_meaning_on_the_page() -> None:
    assert setting_meaning_gaps(census.SETTING_MEANINGS) == (set(), set())
    missing = {
        name: meaning
        for name, meaning in census.SETTING_MEANINGS.items()
        if name != "meeting_reset"
    }
    assert setting_meaning_gaps(missing) == ({"meeting_reset"}, set())
    extra = {**census.SETTING_MEANINGS, "sabotage_threshold": "a win rule."}
    assert setting_meaning_gaps(extra) == (set(), {"sabotage_threshold"})


# --------------------------------------------------------------------------- #
# The own-kill extraction                                                      #
# --------------------------------------------------------------------------- #


def _row_line(description: str, cite: str) -> str:
    return f"- `p-0` — {description} (first-hand: you saw this yourself; {cite})"


def test_the_row_is_found_in_the_specified_wording_and_nowhere_else(
    capsys: pytest.CaptureFixture[str],
) -> None:
    exact = OWN_KILL_ROW_TEXT.format(room="STORAGE", tick=13)
    prompt = "\n".join(
        [
            "Evidence you hold:",
            _row_line(exact, "cite `p-2:13:0`"),
            _row_line("you watched them VENT in STORAGE at tick 13", "cite `p-2:13:1`"),
            _row_line(exact, "nothing here you could cite"),
        ]
    )
    assert served_own_kill_rows(prompt, holder="p-2") == (
        OwnKillRowFact("p-2", "p-0", "STORAGE", 13, "p-2:13:0"),
        OwnKillRowFact("p-2", "p-0", "STORAGE", 13, None),
    )
    reworded = prompt.replace("watched them KILL", "saw them kill")
    assert served_own_kill_rows(reworded, holder="p-2") == ()
    assert served_own_kill_rows("no rows at all", holder="p-2") == ()
    assert capsys.readouterr() == ("", "")


def test_the_rows_found_are_the_denominator_so_a_mismatch_reads_n_a() -> None:
    silent = game({"ballot_kill_row_version": 1}, meetings=(meeting(),))
    breaching = cell("own_kill_rows_breaching", silent)
    assert (breaching.denominator, breaching.rate) == (0, None)
    for build in (
        _own_kill_row_citing_nothing,
        _own_kill_row_of_teammate_citing_nothing,
    ):
        assert counts("own_kill_rows_breaching", build({})) == (1, 1, 0), build


def test_a_row_joined_to_a_kill_its_holder_saw_is_no_breach() -> None:
    witnessed = game(
        {"ballot_kill_row_version": 1},
        kills=(kill(12, witnesses=("p-2",)),),
        meetings=(
            meeting(
                own_kill_rows=(OwnKillRowFact("p-2", "p-0", ROOM, 13, "p-2:13:0"),),
                ballots=(ballot("p-2", "p-0", cited="p-2:13:0"),),
            ),
        ),
    )
    assert counts("own_kill_rows_breaching", witnessed) == (0, 1, 0)
    assert counts("own_kill_rows_cited_by_holder", witnessed) == (1, 1, 0)
    for held, row_citation in (
        (ballot("p-2", "p-0", cited="p-2:14:0"), "p-2:13:0"),
        (ballot("p-2", "p-0"), None),
        (ballot("p-3", "p-0", cited="p-2:13:0"), "p-2:13:0"),
    ):
        other = game(
            kills=(kill(12, witnesses=("p-2",)),),
            meetings=(
                meeting(
                    own_kill_rows=(
                        OwnKillRowFact("p-2", "p-0", ROOM, 13, row_citation),
                    ),
                    ballots=(held,),
                ),
            ),
        )
        assert counts("own_kill_rows_cited_by_holder", other) == (0, 1, 0), held
    for citation in ("p-3:13:0", "not-an-id", "p-2:12:0"):
        wrong = game(
            kills=(kill(12, witnesses=("p-2",)),),
            meetings=(
                meeting(
                    own_kill_rows=(OwnKillRowFact("p-2", "p-0", ROOM, 13, citation),),
                ),
            ),
        )
        assert counts("own_kill_rows_breaching", wrong) == (1, 1, 0), citation
        assert counts("own_kill_rows_cited_by_holder", wrong) == (0, 1, 0)


def test_the_kill_tick_handle_pattern_is_the_held_out_generators() -> None:
    from experiments.held_out_prefixes import LEGACY_BODY_HANDLE_PATTERN

    assert KILL_TICK_BODY_HANDLE_PATTERN.pattern == LEGACY_BODY_HANDLE_PATTERN.pattern
    assert KILL_TICK_BODY_HANDLE_PATTERN.search("the corpse body-p-3-12 lies")
    assert KILL_TICK_BODY_HANDLE_PATTERN.search("the corpse body-p-3 lies") is None


# --------------------------------------------------------------------------- #
# The exit-policy predicate is the policy's own view                           #
# --------------------------------------------------------------------------- #


def _surfacing_under_sabotage(crew_room: str) -> GameFacts:
    return game(
        {"vent_exit_policy": "look_and_wait"},
        vents=(entry(10), exit_(11)),
        frames={11: frame({"p-2": crew_room}, sabotage=True)},
    )


def test_a_reactor_surfacing_with_crew_in_a_visible_neighbour_is_no_breach() -> None:
    """Under any sabotage the policy counts its own room only.

    The engine still shows the neighbour during a reactor sabotage; the census
    reads the policy's inference, never the engine's visibility.
    """

    assert counts(
        "surfacings_before_cap_in_view", _surfacing_under_sabotage(NEIGHBOUR)
    ) == (
        0,
        1,
        0,
    )
    with pytest.raises(GameplayCensusConformanceError, match="in view"):
        fold_set(inputs(_surfacing_under_sabotage(ROOM)))


def test_without_sabotage_a_neighbour_is_in_view_and_a_teammate_never_is() -> None:
    neighbour = game(
        vents=(entry(10), exit_(11)), frames={11: frame({"p-2": NEIGHBOUR})}
    )
    assert counts("surfacings_before_cap_in_view", neighbour) == (1, 1, 0)
    far = game(vents=(entry(10), exit_(11)), frames={11: frame({"p-2": FAR})})
    assert counts("surfacings_before_cap_in_view", far) == (0, 1, 0)
    teammate = game(vents=(entry(10), exit_(11)), frames={11: frame({"p-1": ROOM})})
    assert counts("surfacings_before_cap_in_view", teammate) == (0, 1, 0)


def _with_room_neighbours(
    game_facts: GameFacts, room_neighbours: tuple[str, ...]
) -> CensusInputs:
    """A carrier for ``game_facts`` whose table gives ``ROOM`` the planted rooms."""

    carrier = inputs(game_facts)
    planted = {**carrier.neighbours, ROOM: room_neighbours}
    return replace(carrier, neighbours=MappingProxyType(planted))


def _counts_on(carrier: CensusInputs, key: str) -> tuple[int, int, int]:
    folded = section_from_tally(fold_set(carrier)).cells[key]
    return (folded.numerator, folded.denominator, folded.not_evaluable)


def _surfacing_beside(
    crew_room: str, settings: Mapping[str, SettingValue]
) -> GameFacts:
    """A two-tick trip out of ``ROOM`` into ``crew_room``, where one crewmate stands."""

    return game(
        settings,
        vents=(entry(10), exit_(11, destination_room=crew_room)),
        frames={11: frame({"p-2": crew_room})},
    )


def test_the_in_vent_view_follows_the_neighbours_the_carrier_holds() -> None:
    """Planted: the carrier's neighbour table, not the canonical map, gives the view.

    On the canonical map the vent room's one neighbour is ``NEIGHBOUR``. A carrier
    that gives the vent room no neighbour hides a crewmate in ``NEIGHBOUR``, and
    one that joins it to ``FAR`` alone shows a crewmate in ``FAR``.
    """

    in_view = "surfacings_before_cap_in_view"
    visibly = "vent_exits_into_visibly_occupied_room"
    near = _surfacing_beside(NEIGHBOUR, {})
    far = _surfacing_beside(FAR, {})
    assert _counts_on(inputs(near), in_view) == (1, 1, 0)
    assert _counts_on(inputs(near), visibly) == (1, 1, 0)
    assert _counts_on(inputs(far), in_view) == (0, 1, 0)
    assert _counts_on(inputs(far), visibly) == (0, 1, 0)
    isolated = _with_room_neighbours(near, ())
    assert _counts_on(isolated, in_view) == (0, 1, 0)
    assert _counts_on(isolated, visibly) == (0, 1, 0)
    joined = _with_room_neighbours(far, (FAR,))
    assert _counts_on(joined, in_view) == (1, 1, 0)
    assert _counts_on(joined, visibly) == (1, 1, 0)
    # The exit is counted as occupied on every table: only the view moves.
    for carrier in (inputs(near), inputs(far), isolated, joined):
        assert _counts_on(carrier, "vent_exits_into_occupied_room") == (1, 1, 0)


def test_the_exit_policy_guard_judges_on_the_neighbours_the_carrier_holds() -> None:
    """Planted: under ``look_and_wait`` the breach follows the carrier's table."""

    in_view = "surfacings_before_cap_in_view"
    look_and_wait = {"vent_exit_policy": "look_and_wait"}
    near = _surfacing_beside(NEIGHBOUR, look_and_wait)
    far = _surfacing_beside(FAR, look_and_wait)
    with pytest.raises(GameplayCensusConformanceError, match="in view"):
        fold_set(inputs(near))
    assert _counts_on(_with_room_neighbours(near, ()), in_view) == (0, 1, 0)
    assert _counts_on(inputs(far), in_view) == (0, 1, 0)
    with pytest.raises(GameplayCensusConformanceError, match="in view"):
        fold_set(_with_room_neighbours(far, (FAR,)))


def _capped_trip(settings: Mapping[str, SettingValue]) -> GameFacts:
    return game(
        settings,
        vents=(entry(10), exit_(10 + IN_VENT_CAP_TICKS)),
        frames={10 + IN_VENT_CAP_TICKS: frame({"p-2": ROOM})},
    )


def test_a_surfacing_at_the_cap_is_forced_not_a_breach() -> None:
    capped = _capped_trip({"vent_exit_policy": "look_and_wait"})
    assert counts("surfacings_before_cap_in_view", capped) == (0, 1, 0)
    assert counts("forced_surfacings", capped) == (1, 1, 0)
    assert counts("trips_longer_than_cap", capped) == (0, 1, 0)
    assert table("ticks_inside_per_trip", capped) == {str(IN_VENT_CAP_TICKS): 1}


@pytest.mark.parametrize("settings", ({}, {"vent_exit_policy": "observed_risk"}))
def test_without_the_look_and_wait_exit_no_surfacing_is_at_a_cap(
    settings: Mapping[str, SettingValue],
) -> None:
    """Planted: the same four-tick trip reads n/a where no cap exists."""

    uncapped = _capped_trip(settings)
    forced = cell("forced_surfacings", uncapped)
    assert (forced.numerator, forced.denominator, forced.rate) == (0, 0, None)
    assert (forced.scope, forced.in_scope) == (
        "vent_exit_policy = look_and_wait",
        False,
    )
    assert table("ticks_inside_per_trip", uncapped) == {str(IN_VENT_CAP_TICKS): 1}
    assert counts("surfacings_before_cap_in_view", uncapped) == (0, 1, 0)


def test_a_surfacing_with_no_recorded_state_before_it_raises() -> None:
    with pytest.raises(ValueError, match="no recorded state before tick 11"):
        fold_set(inputs(game(vents=(entry(10), exit_(11)))))


# --------------------------------------------------------------------------- #
# The grace window is the map's                                                #
# --------------------------------------------------------------------------- #


def test_the_grace_window_is_the_maps_kill_cooldown() -> None:
    assert census_inputs(SAMPLES_4P1I).kill_cooldown_ticks == MAP.kill_cooldown_ticks
    constants = _published()["constants"]
    assert constants["grace_window_ticks"] == MAP.kill_cooldown_ticks
    assert constants["in_vent_cap_ticks"] == IN_VENT_CAP_TICKS
    assert constants["fresh_kill_window_ticks"] == FRESH_KILL_WINDOW_TICKS


def test_a_kill_at_the_first_legal_tick_is_an_ordinary_post_meeting_kill() -> None:
    last_illegal = 10 + MAP.kill_cooldown_ticks
    outside = game(
        {"meeting_reset": "hub_with_grace"},
        kills=(kill(last_illegal + 1),),
        meetings=(meeting(tick=10, regrouped=True),),
    )
    assert counts("kills_in_grace_window_after_regroup", outside) == (0, 1, 0)
    assert counts("post_meeting_kills_soon_after", outside) == (0, 1, 0)
    with pytest.raises(GameplayCensusConformanceError, match=f"tick {last_illegal} "):
        fold_set(inputs(_grace_kill({"meeting_reset": "hub_with_grace"})))


def test_the_grace_window_follows_the_kill_cooldown_the_carrier_holds() -> None:
    """Planted: a map whose kill cooldown is 6, not the canonical map's 4."""

    cooldown = MAP.kill_cooldown_ticks + 2
    regroup = {"meeting_reset": "hub_with_grace"}

    def walked_on_it(kill_tick: int) -> CensusInputs:
        return replace(
            inputs(
                game(
                    regroup,
                    kills=(kill(kill_tick),),
                    meetings=(meeting(tick=10, regrouped=True),),
                ),
                label="samples/9p2i",
            ),
            kill_cooldown_ticks=cooldown,
        )

    with pytest.raises(GameplayCensusConformanceError, match=f"tick {10 + cooldown} "):
        fold_set(walked_on_it(10 + cooldown))
    outside = section_from_tally(fold_set(walked_on_it(10 + cooldown + 1)))
    grace = outside.cells["kills_in_grace_window_after_regroup"]
    assert (grace.numerator, grace.denominator) == (0, 1)
    published = census_from_inputs([walked_on_it(10 + cooldown + 1)])
    assert published.constants["grace_window_ticks"] == cooldown


def test_the_loader_reads_the_kill_cooldown_from_the_map_it_loads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the loaded map's cooldown and connections move, and the carrier's follow.

    The set is loaded on one map, once: the carrier's cooldown, its neighbour
    table, the role seeding and every game's walk come from it. The planted map adds a room and
    reconnects the vent room: it loses its one canonical neighbour and is joined
    to ``FAR`` and to the added room.
    """

    added = "PLANTED_ANNEX"
    assert added not in MAP.rooms
    rewired = tuple(
        edge for edge in MAP.edges if ROOM not in (edge.from_room, edge.to_room)
    )
    template = next(
        edge for edge in MAP.edges if ROOM in (edge.from_room, edge.to_room)
    )
    planted_map = MAP.model_copy(
        update={
            "kill_cooldown_ticks": MAP.kill_cooldown_ticks + 2,
            "rooms": MappingProxyType(
                {**MAP.rooms, added: MAP.rooms[ROOM].model_copy(update={"id": added})}
            ),
            "edges": (
                *rewired,
                template.model_copy(update={"from_room": ROOM, "to_room": FAR}),
                template.model_copy(update={"from_room": added, "to_room": ROOM}),
            ),
        }
    )
    assert planted_map.room_neighbors(ROOM) == tuple(sorted((FAR, added)))
    assert MAP.room_neighbors(ROOM) == (NEIGHBOUR,)
    set_dir = tmp_path / "planted" / "4p1i"
    set_dir.mkdir(parents=True)
    (set_dir / f"replay-seed-{LOADER_SEED}.jsonl").write_text("", encoding="utf-8")
    (set_dir / "MANIFEST.md").write_text(
        f"| {LOADER_SEED} | model | a.x.v1 |\n", encoding="utf-8"
    )
    committed = _committed_game()
    loads: list[object] = []
    walked_on: list[object] = []
    seeded_on: list[object] = []

    def load_map() -> object:
        loads.append(planted_map)
        return planted_map

    def seed_roles(sample_dir: Path, **kwargs: Any) -> Mapping[int, Mapping[str, str]]:
        seeded_on.append(kwargs.get("game_map"))
        return roles_by_seed(sample_dir, **kwargs)

    def load_game(path: Path, **kwargs: Any) -> GameFacts:
        walked_on.append(kwargs["game_map"])
        return committed

    monkeypatch.setattr(census, "load_canonical_map", load_map)
    monkeypatch.setattr(census, "roles_by_seed", seed_roles)
    monkeypatch.setattr(census, "_load_game", load_game)
    loaded = census.load_census_inputs(set_dir)
    assert loaded.kill_cooldown_ticks == planted_map.kill_cooldown_ticks
    assert dict(loaded.neighbours) == {
        room: planted_map.room_neighbors(room) for room in sorted(planted_map.rooms)
    }
    assert loaded.neighbours[ROOM] == tuple(sorted((FAR, added)))
    assert loaded.neighbours[added] == (ROOM,)
    assert ROOM not in loaded.neighbours[NEIGHBOUR]
    # One map per set: loaded once, the roles are seeded on it, and every game
    # walks on it.
    assert loads == [planted_map]
    assert seeded_on == [planted_map]
    assert walked_on == [planted_map]


def _census_executed_again(monkeypatch: pytest.MonkeyPatch) -> ModuleType:
    """A second, independent execution of the census module's source.

    Its module-level constants bind to whatever their sources hold now, so a
    test can move a source and read the constant that follows it. The module
    lives under its own name for the test only; the imported module is untouched.
    """

    spec = importlib.util.spec_from_file_location(
        "_gameplay_census_again", census.__file__
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    return module


def test_the_constants_bound_from_a_source_follow_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: each source moves, and the census constant bound to it follows."""

    from agents.tactical import crewmate_policy
    from eval import balance_eval, process_scorecard

    class _Moved(RecordedExperimentConfig):
        vent_entry_policy: typing.Literal["any_body", "own_fresh_kill"] = (
            "own_fresh_kill"
        )

    button = crewmate_policy.EMERGENCY_COOLDOWN_TICKS + 3
    sets = ("replays/planted/9p2i", "replays/planted/4p1i")
    base = replace(_CURRENT_REPORT_WALK_CONFIG, supports_temporal_observations=False)
    monkeypatch.setattr(crewmate_policy, "EMERGENCY_COOLDOWN_TICKS", button)
    monkeypatch.setattr(process_scorecard, "COMMITTED_SETS", sets)
    monkeypatch.setattr(process_scorecard, "NINE_PLAYER_SETS", sets[:1])
    monkeypatch.setattr(experiment_config, "RecordedExperimentConfig", _Moved)
    monkeypatch.setattr(balance_eval, "_CURRENT_REPORT_WALK_CONFIG", base)
    again = _census_executed_again(monkeypatch)
    assert again.BUTTON_COOLDOWN_TICKS == button
    assert again.CENSUS_SETS == sets
    assert again.CENSUS_NINE_PLAYER_SETS == sets[:1]
    assert again.SETTING_DEFAULTS["vent_entry_policy"] == "own_fresh_kill"
    assert census.SETTING_DEFAULTS["vent_entry_policy"] == "any_body"
    assert not again.CENSUS_WALK_CONFIG.supports_temporal_observations
    assert CENSUS_WALK_CONFIG.supports_temporal_observations


def test_the_own_kill_join_reads_the_scorecards_clock_offset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: the agent clock offset moves, and the citation that joins follows."""

    def cited(citation: str) -> tuple[int, int, int]:
        return counts(
            "own_kill_rows_breaching",
            game(
                kills=(kill(12, witnesses=("p-2",)),),
                meetings=(
                    meeting(
                        own_kill_rows=(
                            OwnKillRowFact("p-2", "p-0", ROOM, 12, citation),
                        ),
                    ),
                ),
            ),
        )

    from eval.process_scorecard import AGENT_CLOCK_OFFSET as offset

    assert cited(f"p-2:{12 + offset}:0") == (0, 1, 0)
    monkeypatch.setattr(census, "AGENT_CLOCK_OFFSET", offset + 2)
    assert cited(f"p-2:{12 + offset}:0") == (1, 1, 0)
    assert cited(f"p-2:{12 + offset + 2}:0") == (0, 1, 0)


def test_census_from_inputs_refuses_sets_walked_on_different_maps() -> None:
    first = inputs(game())
    with pytest.raises(ValueError, match="different kill cooldowns"):
        census_from_inputs([first, replace(first, kill_cooldown_ticks=5)])
    with pytest.raises(ValueError, match="no replay sets"):
        census_from_inputs([])


# --------------------------------------------------------------------------- #
# The added cells                                                              #
# --------------------------------------------------------------------------- #


def test_ticks_inside_restart_at_a_meeting_the_trip_spans() -> None:
    """Perturbed: counting from the entry alone would read 3, not 2."""

    spanning = game(
        vents=(entry(10), exit_(13)),
        frames={13: frame({})},
        meetings=(meeting(tick=11),),
    )
    assert table("ticks_inside_per_trip", spanning) == {"2": 1}
    assert counts("trips_longer_than_cap", spanning) == (0, 1, 0)


REGROUP: Mapping[str, SettingValue] = MappingProxyType(
    {"meeting_reset": "hub_with_grace"}
)


def test_a_trip_is_closed_by_a_regroup_an_ejection_or_the_game_end() -> None:
    regrouped = game(
        REGROUP, vents=(entry(10),), meetings=(meeting(tick=12, regrouped=True),)
    )
    assert counts("trips_closed_by_regroup", regrouped) == (1, 1, 0)
    assert counts("trips_longer_than_cap", regrouped) == (0, 1, 0)
    ejected = game(
        REGROUP,
        vents=(entry(10),),
        meetings=(meeting(tick=12, outcome="EJECTED", ejected="p-0", regrouped=True),),
    )
    assert counts("trips_closed_by_regroup", ejected) == (0, 1, 0)
    ended = game(REGROUP, vents=(entry(10),), terminal_tick=14)
    assert counts("trips_closed_by_regroup", ended) == (0, 1, 0)
    unrecorded_winner = game(REGROUP, vents=(entry(10),), winner=None)
    assert counts("trips_closed_by_regroup", unrecorded_winner) == (0, 1, 0)
    assert counts("impostor_wins", unrecorded_winner) == (0, 0, 1)
    preserved = game(vents=(entry(10),), meetings=(meeting(tick=12),), terminal_tick=14)
    assert counts("trips_longer_than_cap", preserved) == (0, 1, 0)


def test_where_no_meeting_regroups_no_trip_is_ended_by_a_regroup() -> None:
    """Planted: under the historical reset the cell reads n/a, not 0 of N.

    Even a carrier whose meeting is marked regrouped counts nothing there, so
    the n/a comes from the recorded reset and not from the trips it holds.
    """

    for meetings in ((meeting(tick=12),), (meeting(tick=12, regrouped=True),)):
        preserved = game(vents=(entry(10),), meetings=meetings, terminal_tick=14)
        closed = cell("trips_closed_by_regroup", preserved)
        assert (closed.numerator, closed.denominator, closed.rate) == (0, 0, None)
        assert (closed.scope, closed.in_scope) == (
            "meeting_reset = hub_with_grace",
            False,
        )


def test_a_long_trip_closed_without_an_exit_counts_against_the_cap() -> None:
    over = game(vents=(entry(10),), meetings=(meeting(tick=16, regrouped=True),))
    assert counts("trips_longer_than_cap", over) == (1, 1, 0)


def test_a_malformed_vent_sequence_raises() -> None:
    with pytest.raises(ValueError, match="entered a vent twice"):
        fold_set(inputs(game(vents=(entry(10), entry(11)))))
    with pytest.raises(ValueError, match="never entered"):
        fold_set(inputs(game(vents=(exit_(11),), frames={11: frame({})})))


def test_in_place_surfacings_count_a_crewmate_arriving_before_the_walk_out() -> None:
    def in_place(later: dict[int, Frame]) -> GameFacts:
        return game(
            vents=(entry(10), exit_(11, destination_room=ROOM)),
            frames={11: frame({}), **later},
        )

    arrived = in_place(
        {
            12: frame({"p-0": ROOM}),
            13: frame({"p-0": ROOM, "p-3": ROOM}),
        }
    )
    assert counts("in_place_surfacings_near_crew", arrived) == (1, 1, 0)
    walked_out = in_place(
        {
            12: frame({"p-0": NEIGHBOUR}),
            13: frame({"p-3": ROOM}),
        }
    )
    assert counts("in_place_surfacings_near_crew", walked_out) == (0, 1, 0)
    teammate_only = in_place({12: frame({"p-0": ROOM, "p-1": ROOM})})
    assert counts("in_place_surfacings_near_crew", teammate_only) == (0, 1, 0)
    elsewhere = game(vents=(entry(10), exit_(11)), frames={11: frame({})})
    assert counts("in_place_surfacings_near_crew", elsewhere) == (0, 0, 0)


def test_kills_soon_after_the_killer_surfaced() -> None:
    soon = game(
        vents=(entry(8), exit_(10)),
        frames={10: frame({})},
        kills=(kill(12), kill(13), kill(12, killer="p-1")),
    )
    assert counts("kills_soon_after_surfacing", soon) == (1, 3, 0)


def test_exits_into_rooms_a_crewmate_stood_in() -> None:
    planted = game(
        vents=(entry(8), exit_(10), entry(11), exit_(13, destination_room=FAR)),
        frames={
            10: frame({"p-2": NEIGHBOUR, "p-3": ROOM}),
            13: frame({"p-2": FAR}),
        },
    )
    assert counts("vent_exits_into_occupied_room", planted) == (2, 2, 0)
    assert counts("vent_exits_into_visibly_occupied_room", planted) == (1, 2, 0)
    assert counts("vent_exits_while_room_left_occupied", planted) == (1, 2, 0)


def test_entries_keep_the_fresh_kill_window_and_the_meeting_boundary() -> None:
    window = FRESH_KILL_WINDOW_TICKS

    def entering(
        kill_fact: KillFact, meetings: tuple[MeetingFact, ...] = ()
    ) -> GameFacts:
        return game(
            kills=(kill_fact,), vents=(entry(20),), meetings=meetings, terminal_tick=21
        )

    assert counts(
        "vent_entries_not_after_own_fresh_kill", entering(kill(20 - window))
    ) == (
        0,
        1,
        0,
    )
    for stale in (
        entering(kill(20 - window - 1)),
        entering(kill(19, room=FAR)),
        entering(kill(19, killer="p-1")),
        entering(kill(20)),
        entering(kill(18), (meeting(tick=19),)),
    ):
        assert counts("vent_entries_not_after_own_fresh_kill", stale) == (1, 1, 0)


def test_the_regroup_cells_read_regroups_only() -> None:
    regroup = meeting(
        meeting_id="meeting-0",
        tick=10,
        regrouped=True,
        sabotage_active=True,
        trigger_tick_dropped_events=(("Moved", 2), ("TaskProgressed", 1)),
    )
    button = meeting(meeting_id="meeting-1", tick=15, opener="p-3")
    planted = game(kills=(kill(12, witnesses=("p-3",)),), meetings=(regroup, button))
    assert counts("sabotage_active_at_regroup", planted) == (1, 1, 0)
    assert table(
        "trigger_tick_events_dropped_by_regroup", game(REGROUP, meetings=(regroup,))
    ) == {
        "Moved": 2,
        "TaskProgressed": 1,
    }
    assert counts("kill_witness_button_calls_soon_after_regroup", planted) == (1, 1, 0)
    late = replace(button, tick=10 + census.BUTTON_COOLDOWN_TICKS + 1)
    assert counts(
        "kill_witness_button_calls_soon_after_regroup",
        game(kills=(kill(12, witnesses=("p-3",)),), meetings=(regroup, late)),
    ) == (0, 1, 0)
    unwitnessed = game(kills=(kill(12),), meetings=(regroup, button))
    assert counts("kill_witness_button_calls_soon_after_regroup", unwitnessed) == (
        0,
        1,
        0,
    )
    reported = game(
        kills=(kill(12, witnesses=("p-3",)),),
        bodies=(body("body-x", 12),),
        meetings=(regroup, report(15, "body-x", meeting_id="meeting-1", opener="p-3")),
    )
    assert counts("kill_witness_button_calls_soon_after_regroup", reported) == (0, 0, 0)
    kept = game(REGROUP, meetings=(replace(regroup, regrouped=False),))
    assert counts("sabotage_active_at_regroup", kept) == (0, 0, 0)
    assert table("trigger_tick_events_dropped_by_regroup", kept) == {}


def test_where_no_meeting_regroups_the_dropped_events_table_reads_n_a() -> None:
    """Planted: under the historical reset the table counts nothing at all.

    Even a carrier whose meeting is marked regrouped adds no row there, so the
    table is out of scope rather than an empty count.
    """

    regroup = meeting(regrouped=True, trigger_tick_dropped_events=(("Moved", 2),))
    for settings in (REGROUP, {}):
        dropped = section_from_tally(
            fold_set(inputs(game(settings, meetings=(regroup,))))
        ).tables["trigger_tick_events_dropped_by_regroup"]
        expected = settings == REGROUP
        assert dropped.in_scope is expected
        assert dict(dropped.counts) == ({"Moved": 2} if expected else {})
        assert dropped.scope == "meeting_reset = hub_with_grace"


def test_a_kill_witness_button_at_the_cooldown_tick_counts() -> None:
    edge = meeting(
        meeting_id="meeting-1", tick=10 + census.BUTTON_COOLDOWN_TICKS, opener="p-3"
    )
    planted = game(
        kills=(kill(12, witnesses=("p-3",)),),
        meetings=(meeting(meeting_id="meeting-0", tick=10, regrouped=True), edge),
    )
    assert counts("kill_witness_button_calls_soon_after_regroup", planted) == (1, 1, 0)


def test_opening_state_cells() -> None:
    planted = game(
        meetings=(
            meeting(
                in_vent_at_open=frozenset({"p-0"}),
                impostor_cooldowns_at_open=(("p-0", 0), ("p-1", 3)),
                bodies_at_open=(("body-y", None), ("body-z", "p-2")),
            ),
        )
    )
    assert counts("meetings_opening_with_impostor_in_vent", planted) == (1, 1, 0)
    assert counts("impostor_cooldown_zero_at_open", planted) == (1, 2, 0)
    assert counts("meetings_opening_with_another_unreported_corpse", planted) == (
        1,
        1,
        0,
    )
    ended = game(
        meetings=(meeting(phase_after="GAME_OVER", in_vent_after=frozenset({"p-0"})),)
    )
    assert counts("play_resumes_with_impostor_in_vent", ended) == (0, 0, 0)


def test_post_meeting_kills_count_until_the_next_meeting() -> None:
    planted = game(
        kills=(kill(11), kill(15), kill(20), kill(21), kill(9)),
        meetings=(
            meeting(meeting_id="meeting-0", tick=10),
            meeting(meeting_id="meeting-1", tick=20),
        ),
    )
    assert counts("post_meeting_kills_soon_after", planted) == (2, 4, 0)


def test_meeting_structure_cells() -> None:
    planted = game(
        meetings=(
            meeting(
                meeting_id="meeting-0",
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-2",), reply_to="t0"),
                ),
            ),
            meeting(
                meeting_id="meeting-1",
                tick=30,
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-0",), reply_to="t0"),
                    turn(2, "p-4", accuses=("p-2",), reply_to="t1"),
                ),
                outcome="EJECTED",
                ejected="p-2",
            ),
            meeting(meeting_id="meeting-2", tick=40, turns=(turn(0, "p-2"),)),
        )
    )
    assert counts("first_reply_accuses_opener", planted) == (1, 3, 0)
    assert counts("opener_accused_after_opening", planted) == (2, 3, 0)
    assert counts("opener_speaks_again", planted) == (0, 3, 0)
    assert counts("accused_opener_answers", planted) == (0, 2, 0)
    assert counts("openers_among_innocent_ejections", planted) == (1, 1, 0)
    assert table("innocent_opener_ejections_by_trigger", planted) == {"emergency": 1}
    assert table("meetings_by_trigger", planted) == {"emergency": 3}


def test_report_meetings_that_skip_and_openings_without_a_prompt() -> None:
    planted = game(
        kills=(kill(8), kill(28)),
        bodies=(body("body-x", 8), body("body-y", 28)),
        meetings=(
            report(10, "body-x"),
            report(
                30,
                "body-y",
                meeting_id="meeting-1",
                outcome="EJECTED",
                ejected="p-0",
                opener_prompt_has_kill_tick_handle=False,
            ),
        ),
    )
    assert counts("skipped_report_meetings", planted) == (1, 2, 0)
    assert counts("report_openings_with_kill_tick_handle", planted) == (0, 1, 1)


def test_the_win_split_reads_the_recorded_winner() -> None:
    assert counts("impostor_wins", game(winner="IMPOSTORS"), game(seed=8)) == (1, 2, 0)


def _rebuttal_meeting(*turns: TurnFact, opener: str = "p-2") -> MeetingFact:
    return meeting(opener=opener, turns=turns, selector_pick=None)


def test_rebuttal_claim_structure() -> None:
    alibi = AlibiFact("p-2", ((ROOM, 3, 6),))
    planted = game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-2",), reply_to="t0"),
                    turn(
                        2,
                        "p-2",
                        reply_to="t1",
                        accuses=("p-3", "p-0"),
                        observations=(
                            seen("whereabouts", 4),
                            seen("saw_player", 4, "p-0"),
                        ),
                        alibis=(alibi, AlibiFact("p-4", ((ROOM, 1, 2),))),
                    ),
                ),
                selector_pick=("p-2", "t1"),
            ),
            meeting(
                meeting_id="meeting-1",
                tick=30,
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-4",), reply_to="t0"),
                    turn(2, "p-4", accuses=("p-3",), reply_to="t1"),
                    turn(3, "p-3", accuses=("p-0",), reply_to="t2"),
                ),
                selector_pick=("p-3", "t2"),
            ),
        ),
    )
    assert counts("rebuttals_with_alibi", planted) == (1, 2, 0)
    assert counts("rebuttals_with_whereabouts", planted) == (1, 2, 0)
    assert counts("rebuttals_with_sighting", planted) == (1, 2, 0)
    assert counts("rebuttals_redirect_only", planted) == (1, 2, 0)
    assert counts("rebuttal_accusations_against_earlier_speakers", planted) == (1, 3, 0)
    assert table("rebuttal_beneficiaries", planted) == {
        "another crewmate, answering a crewmate": 1,
        "the opener, answering a crewmate": 1,
    }
    assert counts("rebuttals_differing_from_selector", planted) == (0, 2, 0)


def test_an_alibi_about_another_player_is_no_alibi_of_the_rebuttal() -> None:
    planted = game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-2",), reply_to="t0"),
                    turn(
                        2,
                        "p-2",
                        reply_to="t1",
                        accuses=("p-3",),
                        alibis=(AlibiFact("p-4", ((ROOM, 3, 6),)),),
                    ),
                ),
                selector_pick=("p-2", "t1"),
            ),
        ),
    )
    assert counts("rebuttals_with_alibi", planted) == (0, 1, 0)
    assert counts("rebuttals_redirect_only", planted) == (1, 1, 0)


def test_rebuttal_beneficiaries_name_the_accusers_role() -> None:
    planted = game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2", accuses=("p-0",)),
                    turn(1, "p-0", accuses=("p-3",), reply_to="t0"),
                    turn(2, "p-3", accuses=("p-0",), reply_to="t1"),
                    turn(3, "p-0", reply_to="t2"),
                ),
                selector_pick=("p-0", "t2"),
            ),
            meeting(
                meeting_id="meeting-1",
                tick=30,
                turns=(
                    turn(0, "p-2", accuses=("p-0",)),
                    turn(1, "p-0", accuses=("p-3",)),
                    turn(2, "p-0", reply_to="t9"),
                ),
                selector_pick=("p-0", "t9"),
            ),
        ),
    )
    assert table("rebuttal_beneficiaries", planted) == {
        "another impostor, answering a crewmate": 1,
        "another impostor, answering no recorded turn": 1,
    }


def test_the_rebuttal_beneficiaries_table_is_counted_only_with_the_rebuttal_on() -> (
    None
):
    """Planted: with no rebuttal setting the table is out of scope, not empty.

    At the historical default any rebuttal already raises the repeat-speaker
    guard, so there the table can only be out of scope; with the setting on and
    no rebuttal it is an empty count.
    """

    quiet = meeting(turns=(turn(0, "p-2"), turn(1, "p-3", reply_to="t0")))
    for settings, expected in (({}, False), ({"bounded_rebuttal_version": 1}, True)):
        beneficiaries = section_from_tally(
            fold_set(inputs(game(settings, meetings=(quiet,))))
        ).tables["rebuttal_beneficiaries"]
        assert beneficiaries.in_scope is expected
        assert dict(beneficiaries.counts) == {}
        assert beneficiaries.scope == "bounded_rebuttal_version = 1"


def test_opener_rebuttals_answer_the_charged_tick() -> None:
    def answered(
        *evidence: ObservationFact,
        alibi: AlibiFact | None = None,
        charge_tick: int | None = 5,
        charged: str = "p-2",
    ) -> GameFacts:
        charge_observations = (
            () if charge_tick is None else (seen("saw_vent", charge_tick, charged),)
        )
        return game(
            {"bounded_rebuttal_version": 1},
            meetings=(
                meeting(
                    turns=(
                        turn(0, "p-2"),
                        turn(
                            1,
                            "p-3",
                            accuses=("p-2",),
                            reply_to="t0",
                            observations=charge_observations,
                        ),
                        turn(
                            2,
                            "p-2",
                            reply_to="t1",
                            observations=evidence,
                            alibis=() if alibi is None else (alibi,),
                        ),
                    ),
                    selector_pick=("p-2", "t1"),
                ),
            ),
        )

    key = "opener_rebuttals_answering_charged_tick"
    assert counts(key, answered(seen("whereabouts", 5))) == (1, 1, 0)
    assert counts(key, answered(seen("saw_player", 5, "p-4"))) == (1, 1, 0)
    assert counts(key, answered(alibi=AlibiFact("p-2", ((ROOM, 3, 6),)))) == (1, 1, 0)
    assert counts(key, answered(seen("whereabouts", 7))) == (0, 1, 0)
    assert counts(key, answered(alibi=AlibiFact("p-4", ((ROOM, 3, 6),)))) == (0, 1, 0)
    assert counts(key, answered(seen("completed_task", 5))) == (0, 1, 0)
    assert counts(key, answered(seen("whereabouts", 5), charge_tick=None)) == (0, 0, 1)
    assert counts(key, answered(seen("whereabouts", 5), charged="p-4")) == (0, 0, 1)
    for first, last in ((5, 7), (2, 5)):
        edge = AlibiFact("p-2", ((ROOM, first, last),))
        assert counts(key, answered(alibi=edge)) == (1, 1, 0), (first, last)
    assert counts(key, answered(alibi=AlibiFact("p-2", ((ROOM, 6, 7),)))) == (0, 1, 0)
    ranged = ObservationFact("task_activity", 4, 6, "p-2")
    spanning = game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(
                        1,
                        "p-3",
                        accuses=("p-2",),
                        reply_to="t0",
                        observations=(ranged,),
                    ),
                    turn(
                        2, "p-2", reply_to="t1", observations=(seen("whereabouts", 6),)
                    ),
                ),
                selector_pick=("p-2", "t1"),
            ),
        ),
    )
    assert counts(key, spanning) == (1, 1, 0)


# --------------------------------------------------------------------------- #
# Joins, boundaries and exclusions, one planted case each                      #
# --------------------------------------------------------------------------- #


def test_an_impostors_teammates_exclude_the_impostor_itself() -> None:
    planted = game()
    assert census._teammates(planted, "p-0") == frozenset({"p-1"})
    assert census._teammates(planted, "p-2") == frozenset()


def test_a_meeting_carrier_couples_the_outcome_and_the_ejected_player() -> None:
    with pytest.raises(ValueError, match="exactly when the outcome is EJECTED"):
        meeting(outcome="SKIPPED", ejected="p-0")
    with pytest.raises(ValueError, match="exactly when the outcome is EJECTED"):
        meeting(outcome="EJECTED", ejected=None)


def test_a_new_trip_after_a_regroup_closes_the_old_one_first() -> None:
    planted = game(
        REGROUP,
        vents=(entry(5), entry(15), exit_(16)),
        frames={16: frame({})},
        meetings=(meeting(tick=10, regrouped=True),),
    )
    assert counts("trips_closed_by_regroup", planted) == (1, 2, 0)
    assert table("ticks_inside_per_trip", planted) == {"1": 1}


def test_an_entry_seen_through_either_witness_list_is_seen() -> None:
    planted = game(
        vents=(entry(10, source=("p-2",)), exit_(11)), frames={11: frame({})}
    )
    assert counts("vent_entries_seen_by_crew", planted) == (1, 1, 0)
    for seen_entry in (entry(10, source=("p-2",)), entry(10, destination=("p-2",))):
        banded = _band_after((seen_entry, exit_(11)))
        assert table("vent_band_by_moment", banded) == {"entry only": 1}, seen_entry


def test_a_kill_on_the_surfacing_tick_is_not_after_the_surfacing() -> None:
    planted = game(
        vents=(entry(8), exit_(10)), frames={10: frame({})}, kills=(kill(10),)
    )
    assert counts("kills_soon_after_surfacing", planted) == (0, 1, 0)


def test_a_crewmate_on_the_first_tick_after_an_in_place_surfacing_counts() -> None:
    planted = game(
        vents=(entry(10), exit_(11, destination_room=ROOM)),
        frames={
            11: frame({}),
            12: frame({"p-0": ROOM, "p-3": ROOM}),
            13: frame({"p-0": NEIGHBOUR}),
        },
    )
    assert counts("in_place_surfacings_near_crew", planted) == (1, 1, 0)


def test_only_an_undiscovered_corpse_other_than_the_reported_one_counts() -> None:
    def opened_with(bodies: tuple[tuple[str, str | None], ...]) -> GameFacts:
        return game(
            kills=(kill(18),),
            bodies=(body("body-x", 18),),
            meetings=(report(20, "body-x", bodies_at_open=bodies),),
        )

    key = "meetings_opening_with_another_unreported_corpse"
    assert counts(key, opened_with((("body-x", None),))) == (0, 1, 0)
    assert counts(key, opened_with((("body-x", "p-2"), ("body-y", "p-3")))) == (
        0,
        1,
        0,
    )
    assert counts(key, opened_with((("body-x", "p-2"), ("body-y", None)))) == (1, 1, 0)


def test_a_button_soon_after_a_regroup_with_no_kill_since_is_no_witness_call() -> None:
    planted = game(
        meetings=(
            meeting(meeting_id="meeting-0", tick=10, regrouped=True),
            meeting(meeting_id="meeting-1", tick=13, opener="p-3"),
        ),
    )
    assert counts("kill_witness_button_calls_soon_after_regroup", planted) == (0, 1, 0)


def test_the_opener_accusing_themself_is_no_one_accusing_the_opener() -> None:
    planted = game(meetings=(meeting(turns=(turn(0, "p-2", accuses=("p-2",)),)),))
    assert counts("opener_accused_after_opening", planted) == (0, 1, 0)


def _one_rebuttal(**claims: Any) -> GameFacts:
    return game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-2",), reply_to="t0"),
                    turn(2, "p-2", reply_to="t1", **claims),
                ),
                selector_pick=("p-2", "t1"),
            ),
        ),
    )


def test_rebuttal_claim_kinds_are_told_apart() -> None:
    alibi = AlibiFact("p-2", ((ROOM, 3, 6),))
    sighting_only = _one_rebuttal(observations=(seen("saw_player", 4, "p-0"),))
    assert counts("rebuttals_with_whereabouts", sighting_only) == (0, 1, 0)
    assert counts("rebuttals_with_sighting", sighting_only) == (1, 1, 0)
    whereabouts_only = _one_rebuttal(observations=(seen("whereabouts", 4),))
    assert counts("rebuttals_with_whereabouts", whereabouts_only) == (1, 1, 0)
    assert counts("rebuttals_with_sighting", whereabouts_only) == (0, 1, 0)
    assert counts("rebuttals_redirect_only", _one_rebuttal()) == (0, 1, 0)
    for claims in (
        {"alibis": (alibi,)},
        {"observations": (seen("whereabouts", 4),)},
        {"observations": (seen("saw_player", 4, "p-0"),)},
    ):
        backed = _one_rebuttal(accuses=("p-3",), **claims)
        assert counts("rebuttals_redirect_only", backed) == (0, 1, 0), claims
    assert counts("rebuttals_redirect_only", _one_rebuttal(accuses=("p-3",))) == (
        1,
        1,
        0,
    )


#: The observation kinds that name a player seen, written out here from the
#: meeting schema's observation shapes, never read from the census.
SIGHTING_KINDS = ("saw_player", "saw_vent", "saw_kill", "saw_move")

#: The other observation kinds a turn can carry, besides whereabouts: each names
#: a task or a body, never a player seen.
NAMING_NO_PLAYER_SEEN = ("completed_task", "found_body", "task_activity")


def test_the_sighting_kinds_are_the_observations_that_name_a_player_seen() -> None:
    """Pinned to the schema: a sighting is an observation with a ``subject``.

    A turn's observation kinds are the members of the meeting schema's
    observation union. The members with a ``subject`` field name the player the
    speaker saw; the others name a task, a body or the speaker's own room. The
    census's kinds, the list above and the schema's subject-carrying kinds are
    one set, so a kind the schema adds with a subject turns this red until the
    census decides whether it is a sighting.
    """

    union, _discriminator = get_args(ObservationClaim)
    by_kind = {
        get_args(model.model_fields["type"].annotation)[0]: model
        for model in get_args(union)
    }
    with_subject = {
        kind for kind, model in by_kind.items() if "subject" in model.model_fields
    }
    assert with_subject == set(SIGHTING_KINDS)
    assert census._SIGHTING_KINDS == with_subject
    assert set(by_kind) - with_subject == {*NAMING_NO_PLAYER_SEEN, "whereabouts"}


def _opener_answering(evidence: ObservationFact) -> GameFacts:
    """An opener rebuttal to a turn that saw the opener at tick 5."""

    return game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(
                        1,
                        "p-3",
                        accuses=("p-2",),
                        reply_to="t0",
                        observations=(seen("saw_player", 5, "p-2"),),
                    ),
                    turn(2, "p-2", reply_to="t1", observations=(evidence,)),
                ),
                selector_pick=("p-2", "t1"),
            ),
        ),
    )


@pytest.mark.parametrize("kind", SIGHTING_KINDS)
def test_every_sighting_kind_is_a_sighting_on_the_three_rebuttal_cells(
    kind: str,
) -> None:
    """Planted, one kind at a time, on each cell that reads a sighting.

    A rebuttal that redirects and carries one observation of this kind carries a
    sighting and does not only redirect, whether the observation names another
    player or the speaker. An opener rebuttal whose observation of this kind
    falls on the tick its accuser saw the opener answers that tick; one two
    ticks later does not.
    """

    for subject in ("p-0", "p-2"):
        backed = _one_rebuttal(accuses=("p-3",), observations=(seen(kind, 4, subject),))
        assert counts("rebuttals_with_sighting", backed) == (1, 1, 0), subject
        assert counts("rebuttals_redirect_only", backed) == (0, 1, 0), subject
    key = "opener_rebuttals_answering_charged_tick"
    assert counts(key, _opener_answering(seen(kind, 5, "p-4"))) == (1, 1, 0)
    assert counts(key, _opener_answering(seen(kind, 7, "p-4"))) == (0, 1, 0)


@pytest.mark.parametrize("kind", NAMING_NO_PLAYER_SEEN)
def test_an_observation_naming_no_player_seen_is_no_sighting(kind: str) -> None:
    """Planted: the same three cells read these kinds as no sighting."""

    backed = _one_rebuttal(accuses=("p-3",), observations=(seen(kind, 4),))
    assert counts("rebuttals_with_sighting", backed) == (0, 1, 0)
    assert counts("rebuttals_redirect_only", backed) == (1, 1, 0)
    key = "opener_rebuttals_answering_charged_tick"
    assert counts(key, _opener_answering(seen(kind, 5))) == (0, 1, 0)


def test_the_charged_tick_cell_reads_opener_rebuttals_only() -> None:
    key = "opener_rebuttals_answering_charged_tick"
    other = game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-4",), reply_to="t0"),
                    turn(
                        2,
                        "p-4",
                        accuses=("p-3",),
                        reply_to="t1",
                        observations=(seen("saw_vent", 5, "p-2"),),
                    ),
                    turn(
                        3, "p-3", reply_to="t2", observations=(seen("whereabouts", 5),)
                    ),
                ),
                selector_pick=("p-3", "t2"),
            ),
        ),
    )
    assert counts(key, other) == (0, 0, 0)
    unrecorded = game(
        {"bounded_rebuttal_version": 1},
        meetings=(
            meeting(
                turns=(
                    turn(0, "p-2"),
                    turn(1, "p-3", accuses=("p-2",)),
                    turn(
                        2, "p-2", reply_to="t9", observations=(seen("whereabouts", 5),)
                    ),
                ),
                selector_pick=("p-2", "t9"),
            ),
        ),
    )
    assert counts(key, unrecorded) == (0, 0, 1)


def test_a_row_joins_the_one_kill_it_cites_among_several() -> None:
    planted = game(
        {"ballot_kill_row_version": 1},
        kills=(kill(12, witnesses=("p-2",)), kill(30, killer="p-1")),
        meetings=(
            meeting(
                own_kill_rows=(OwnKillRowFact("p-2", "p-0", ROOM, 13, "p-2:13:0"),)
            ),
        ),
    )
    assert counts("own_kill_rows_breaching", planted) == (0, 1, 0)


def test_the_impostor_only_floor_reads_only_confident_ballots_for_the_ejected() -> None:
    def ejection(*ballots: BallotFact) -> GameFacts:
        return game(
            meetings=(meeting(outcome="EJECTED", ejected="p-2", ballots=ballots),)
        )

    key = "ejections_carried_only_by_impostor_ballots"
    elsewhere = ejection(
        ballot("p-0", "p-2", confidence=0.9), ballot("p-4", "p-3", confidence=0.9)
    )
    assert counts(key, elsewhere) == (1, 1, 0)
    unconfident = ejection(ballot("p-0", "p-2", confidence=0.1))
    assert counts(key, unconfident) == (0, 1, 0)


# --------------------------------------------------------------------------- #
# The loader, on a perturbed copy of one committed game's walk                 #
# --------------------------------------------------------------------------- #

LOADER_SEED = 5


def _events() -> list[ReplayWalkEvent]:
    return list(census_walk_events(SAMPLES_4P1I, LOADER_SEED))


def _committed_game() -> GameFacts:
    return next(
        item for item in census_inputs(SAMPLES_4P1I).games if item.seed == LOADER_SEED
    )


def _load(
    monkeypatch: pytest.MonkeyPatch,
    events: Sequence[ReplayWalkEvent],
    *,
    manifest_cell: str = "a.x.v1, b.x.v1",
) -> GameFacts:
    loaded = census_inputs(SAMPLES_4P1I)
    monkeypatch.setattr(census, "walk_replay", lambda *args, **kwargs: iter(events))
    return census._load_game(
        Path("unused"),
        seed=LOADER_SEED,
        roles=next(item.roles for item in loaded.games if item.seed == LOADER_SEED),
        manifest_cell=manifest_cell,
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=MAP,
    )


def test_the_perturbation_harness_reproduces_the_committed_game(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    committed = next(
        item for item in census_inputs(SAMPLES_4P1I).games if item.seed == LOADER_SEED
    )
    stamps_cell = ", ".join(committed.era.prompt_stamps or ())
    assert _load(monkeypatch, _events(), manifest_cell=stamps_cell) == committed


def test_the_loader_refuses_a_corpse_without_a_kill(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, TickAdvanced)
        and any(isinstance(item, KilledEvent) for item in event.events)
    )
    advanced = events[index]
    assert isinstance(advanced, TickAdvanced)
    events[index] = replace(
        advanced,
        events=tuple(
            item for item in advanced.events if not isinstance(item, KilledEvent)
        ),
    )
    with pytest.raises(ValueError, match="no kill of its victim"):
        _load(monkeypatch, events)


def test_the_loader_counts_rows_without_dispositions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    committed = _load(monkeypatch, list(events))
    index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, TickAdvanced)
        and "discarded_by_meeting" in (event.entry.action_dispositions or ())
    )
    advanced = events[index]
    assert isinstance(advanced, TickAdvanced)
    events[index] = replace(
        advanced, entry=advanced.entry.model_copy(update={"action_dispositions": None})
    )
    stripped = _load(monkeypatch, events)
    assert stripped.rows_without_dispositions == 1
    assert len(stripped.discarded) < len(committed.discarded)


def test_the_loader_refuses_a_meeting_applied_without_opening(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = [event for event in _events() if not isinstance(event, MeetingOpened)]
    with pytest.raises(ValueError, match="applied without opening"):
        _load(monkeypatch, events)


def test_the_loader_refuses_a_meeting_without_its_trigger(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = [
        replace(event, trigger=None) if isinstance(event, MeetingOpened) else event
        for event in _events()
    ]
    with pytest.raises(ValueError, match="no trigger event"):
        _load(monkeypatch, events)


def test_the_loader_reads_the_recorded_reset(monkeypatch: pytest.MonkeyPatch) -> None:
    regroup = RecordedExperimentConfig(meeting_reset="hub_with_grace")

    def stamped(event: ReplayWalkEvent) -> ReplayWalkEvent:
        if isinstance(event, TickOpened):
            return replace(
                event,
                entry=event.entry.model_copy(update={"experiment_config": regroup}),
            )
        if isinstance(event, WalkComplete) and event.game_end is not None:
            return replace(
                event,
                game_end=event.game_end.model_copy(
                    update={"experiment_config": regroup}
                ),
            )
        return event

    events = [stamped(event) for event in _events()]
    loaded = _load(monkeypatch, events)
    assert loaded.era.settings == (("meeting_reset", "hub_with_grace"),)
    assert [item.regrouped for item in loaded.meetings] == [
        item.phase_after == "PLAY" for item in loaded.meetings
    ]
    assert any(item.regrouped for item in loaded.meetings)
    baseline = _load(monkeypatch, _events())
    assert not any(item.regrouped for item in baseline.meetings)
    ending = [
        replace(event, state=replace(event.state, phase="GAME_OVER"))
        if isinstance(event, MeetingApplied)
        else event
        for event in events
    ]
    ended = _load(monkeypatch, ending)
    assert [item.phase_after for item in ended.meetings] == ["GAME_OVER"]
    assert not any(item.regrouped for item in ended.meetings)


def test_the_loader_reads_the_temporal_observation_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    first = next(event for event in events if isinstance(event, TickOpened))
    assert first.entry.substrate_flags is not None
    flags = {**first.entry.substrate_flags, "temporal_observations": True}

    def delivered(event: ReplayWalkEvent) -> ReplayWalkEvent:
        if isinstance(event, TickOpened):
            update: dict[str, Any] = {"temporal_observation_version": 2}
            if event is first:
                update["substrate_flags"] = flags
            return replace(event, entry=event.entry.model_copy(update=update))
        if isinstance(event, WalkComplete) and event.game_end is not None:
            return replace(
                event,
                game_end=event.game_end.model_copy(update={"substrate_flags": flags}),
            )
        return event

    loaded = _load(monkeypatch, [delivered(event) for event in events])
    assert loaded.era.temporal_observation_version == 2
    assert dict(loaded.era.substrate_flags or ())["temporal_observations"] is True
    assert _load(monkeypatch, events).era.temporal_observation_version is None


def test_the_loader_copies_ids_the_floor_ballots_and_sabotage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from engine.entities import SabotageState
    from orchestrator.replay_integrity import resolve_ballot_tally_threshold

    events = _events()
    index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, MeetingOpened)
    )
    opened = events[index]
    assert isinstance(opened, MeetingOpened)
    entry = opened.entry
    fact = _load(monkeypatch, events).meetings[0]
    assert fact.meeting_id == entry.meeting_id
    assert fact.ballot_floor == resolve_ballot_tally_threshold(entry) > 0
    assert [ballot.confidence for ballot in fact.ballots] == [
        ballot.confidence for ballot in entry.ballots
    ]
    assert any(ballot.confidence for ballot in fact.ballots)
    cited = entry.ballots[0].model_copy(
        update={"primary_reason_observation_id": "p-2:9:0"}
    )
    events[index] = replace(
        opened,
        entry=entry.model_copy(update={"ballots": (cited, *entry.ballots[1:])}),
        state=replace(
            opened.state,
            sabotage=SabotageState(
                kind="reactor", remaining_ticks=5, affected_rooms=(), active=True
            ),
        ),
    )
    changed = _load(monkeypatch, events).meetings[0]
    assert changed.ballots[0].cited_observation_id == "p-2:9:0"
    assert changed.sabotage_active is True
    assert fact.sabotage_active is False


def test_the_ballot_floor_is_the_threshold_the_meeting_recorded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: every committed meeting's floor is 0.6, so move one to 0.75.

    A meeting that recorded no threshold reads the tally's historical rule.
    """

    from orchestrator.replay_integrity import LEGACY_SKIP_CONFIDENCE_THRESHOLD

    events = _events()
    index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, MeetingOpened)
    )
    opened = events[index]
    assert isinstance(opened, MeetingOpened)
    assert _load(monkeypatch, events).meetings[0].ballot_floor == 0.6
    for recorded, floor in ((0.75, 0.75), (None, LEGACY_SKIP_CONFIDENCE_THRESHOLD)):
        events[index] = replace(
            opened,
            entry=opened.entry.model_copy(
                update={"skip_confidence_threshold": recorded}
            ),
        )
        assert _load(monkeypatch, events).meetings[0].ballot_floor == floor, recorded


def test_the_loader_reads_the_openers_first_prompt_and_served_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, MeetingOpened)
    )
    opened = events[index]
    assert isinstance(opened, MeetingOpened)
    baseline = _load(monkeypatch, list(events))
    assert baseline.meetings[0].opener_prompt_has_kill_tick_handle is (
        opened.trigger is not None and opened.trigger.trigger == "report"
    )
    row = (
        "- `p-0` — "
        + OWN_KILL_ROW_TEXT.format(room=ROOM, tick=9)
        + (" (first-hand: you saw this yourself; cite `p-2:9:0`)")
    )
    calls = tuple(
        call.model_copy(update={"prompt": row})
        if call.agent_id != opened.entry.triggered_by
        else call
        for call in opened.entry.llm_calls
    )
    events[index] = replace(
        opened, entry=opened.entry.model_copy(update={"llm_calls": calls})
    )
    served = _load(monkeypatch, events)
    holders = {
        call.agent_id for call in calls if call.agent_id != opened.entry.triggered_by
    }
    assert {item.holder for item in served.meetings[0].own_kill_rows} == holders
    silent = tuple(
        call
        for call in opened.entry.llm_calls
        if call.agent_id != opened.entry.triggered_by
    )
    events[index] = replace(
        opened, entry=opened.entry.model_copy(update={"llm_calls": silent})
    )
    assert (
        _load(monkeypatch, events).meetings[0].opener_prompt_has_kill_tick_handle
        is None
    )


def test_the_loader_counts_the_trigger_ticks_movement_and_task_events(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    opened = next(event for event in events if isinstance(event, MeetingOpened))
    expected = Counter(
        item.type
        for item in opened.events
        if isinstance(item, (MovedEvent, TaskProgressedEvent, TaskCompletedEvent))
    )
    loaded = _load(monkeypatch, events)
    assert dict(loaded.meetings[0].trigger_tick_dropped_events) == dict(expected)
    assert sum(expected.values()) > 0


def test_the_loader_counts_task_events_on_committed_trigger_ticks_that_hold_them() -> (
    None
):
    """Pinned on committed bytes whose trigger ticks hold task events.

    The harness game above holds only moves on its trigger tick. On
    ``samples/9p2i``, 42 of the 145 trigger ticks hold a task event. Seed 19
    opens its first meeting on a tick where two players moved, one task
    progressed and two completed, beside the trigger itself, which the loader
    does not count. Its third meeting opens on a tick with one progress, one
    completion and no move. The counts were measured once, count-only, from the
    walk's own event types, and are written here as literals, never derived
    from the event types the loader reads.
    """

    opened = next(
        event
        for event in census_walk_events(SAMPLES_9P2I, 19)
        if isinstance(event, MeetingOpened)
    )
    assert Counter(event.type for event in opened.events) == {
        "MeetingTriggered": 1,
        "Moved": 2,
        "TaskProgressed": 1,
        "TaskCompleted": 2,
    }
    dropped = {
        meeting.meeting_id: dict(meeting.trigger_tick_dropped_events)
        for game in census_inputs(SAMPLES_9P2I).games
        for meeting in game.meetings
    }
    assert dropped[opened.entry.meeting_id] == {
        "Moved": 2,
        "TaskProgressed": 1,
        "TaskCompleted": 2,
    }
    assert dropped["headless-seed-19:meeting-2"] == {
        "TaskProgressed": 1,
        "TaskCompleted": 1,
    }
    assert dropped["headless-seed-44:meeting-0"] == {
        "Moved": 2,
        "TaskProgressed": 3,
        "TaskCompleted": 1,
    }
    totals: Counter[str] = Counter()
    for kinds in dropped.values():
        totals.update(kinds)
    assert len(dropped) == 145
    assert totals == {"Moved": 89, "TaskProgressed": 43, "TaskCompleted": 17}
    with_task_events = [
        kinds
        for kinds in dropped.values()
        if "TaskProgressed" in kinds or "TaskCompleted" in kinds
    ]
    assert len(with_task_events) == 42


def test_the_loader_takes_the_selector_pick_and_the_turn_facts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, MeetingOpened)
    )
    opened = events[index]
    assert isinstance(opened, MeetingOpened)
    first = opened.entry.transcript.turns[0]
    charge = first.model_copy(
        update={
            "turn_id": "t-charge",
            "turn_index": 1,
            "speaker": "p-3",
            "turn_kind": "reply",
            "reply_to": first.turn_id,
            "claims": (
                AccusationClaim(
                    type="accusation", against=first.speaker, confidence=0.9, reason="r"
                ),
            ),
        }
    )
    answer = first.model_copy(
        update={
            "turn_id": "t-answer",
            "turn_index": 2,
            "turn_kind": "reply",
            "reply_to": "t-charge",
        }
    )
    transcript = MeetingTranscript(turns=(first, charge, answer))
    events[index] = replace(
        opened, entry=opened.entry.model_copy(update={"transcript": transcript})
    )
    applied_index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, MeetingApplied)
    )
    loaded = _load(
        monkeypatch, events[: applied_index + 1] + events[applied_index + 1 :]
    )
    fact = loaded.meetings[0]
    living = frozenset(
        pid for pid, player in opened.state.players.items() if player.alive
    )
    assert fact.selector_pick == selector_pick(transcript.turns, living)
    assert fact.selector_pick == (first.speaker, "t-charge")
    assert fact.turns[1].accusations == (first.speaker,)


def test_the_loader_takes_stamps_only_from_games_with_meetings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ValueError, match="names no prompt stamp"):
        _load(monkeypatch, _events(), manifest_cell="(none — no meetings)")
    without = [
        event
        for event in _events()
        if not isinstance(event, (MeetingOpened, MeetingApplied))
    ]
    assert (
        _load(
            monkeypatch, without, manifest_cell="(none — no meetings)"
        ).era.prompt_stamps
        is None
    )


def test_turn_facts_keep_ids_ticks_and_alibi_legs() -> None:
    speech = MeetingTurn(
        turn_id="t0",
        turn_index=3,
        speaker="p-2",
        turn_kind="reply",
        reply_to="t9",
        observations=(
            SawPlayerObservation(type="saw_player", tick=4, subject="p-0", room=ROOM),
            WhereaboutsClaim(type="whereabouts", tick=5, room=ROOM),
            TaskActivityAccount(
                type="task_activity",
                task_id="fix_wiring",
                room=ROOM,
                from_tick=2,
                to_tick=3,
            ),
        ),
        claims=(
            AccusationClaim(
                type="accusation", against="p-0", confidence=0.9, reason="r"
            ),
            AlibiClaim(
                type="alibi",
                subject="p-2",
                route=(AlibiSegment(room=ROOM, from_tick=1, to_tick=5),),
            ),
        ),
        free_text="words",
    )
    assert census._turn_fact(speech) == TurnFact(
        turn_id="t0",
        index=3,
        speaker="p-2",
        reply_to="t9",
        accusations=("p-0",),
        observations=(
            ObservationFact("saw_player", 4, 4, "p-0"),
            ObservationFact("whereabouts", 5, 5, None),
            ObservationFact("task_activity", 2, 3, None),
        ),
        alibis=(AlibiFact("p-2", ((ROOM, 1, 5),)),),
    )


def _first_meeting(
    events: Sequence[ReplayWalkEvent],
) -> tuple[MeetingOpened, MeetingApplied]:
    opened = next(event for event in events if isinstance(event, MeetingOpened))
    applied = next(event for event in events if isinstance(event, MeetingApplied))
    return opened, applied


def test_the_frame_holds_living_players_outside_the_vents_and_live_sabotage() -> None:
    from engine.entities import SabotageState

    opened = next(event for event in _events() if isinstance(event, TickOpened))
    state = opened.state
    assert all(p.alive and not p.in_vent for p in state.players.values())
    venting, dead = sorted(state.players)[:2]
    players = dict(state.players)
    players[venting] = replace(players[venting], in_vent=True)
    players[dead] = replace(players[dead], alive=False)
    shown = census._frame_of(replace(state, players=players))
    assert set(shown.rooms) == set(state.players) - {venting, dead}
    for active in (True, False):
        sabotage = SabotageState(
            kind="reactor", remaining_ticks=5, affected_rooms=(), active=active
        )
        framed = census._frame_of(replace(state, sabotage=sabotage))
        assert framed.sabotage_active is active


def test_the_meeting_fact_reads_living_impostor_cooldowns_and_live_sabotage() -> None:
    from engine.entities import SabotageState

    opened, applied = _first_meeting(_events())
    state = opened.state
    impostor = next(
        pid for pid, player in state.players.items() if player.role == "IMPOSTOR"
    )
    crewmate = next(
        pid
        for pid, player in state.players.items()
        if player.role == "CREWMATE" and player.alive
    )
    cooled = replace(state, cooldowns={impostor: 3, crewmate: 0})
    fact = census._meeting_fact(
        replace(opened, state=cooled), applied, regroup_recorded=False
    )
    assert fact.impostor_cooldowns_at_open == ((impostor, 3),)
    players = dict(cooled.players)
    players[impostor] = replace(players[impostor], alive=False)
    dead = census._meeting_fact(
        replace(opened, state=replace(cooled, players=players)),
        applied,
        regroup_recorded=False,
    )
    assert dead.impostor_cooldowns_at_open == ()
    for active in (True, False):
        sabotage = SabotageState(
            kind="reactor", remaining_ticks=5, affected_rooms=(), active=active
        )
        sabotaged = census._meeting_fact(
            replace(opened, state=replace(state, sabotage=sabotage)),
            applied,
            regroup_recorded=False,
        )
        assert sabotaged.sabotage_active is active


def test_an_unrewritten_ballot_was_authored_as_recorded() -> None:
    opened, applied = _first_meeting(_events())
    fact = census._meeting_fact(opened, applied, regroup_recorded=False)
    pairs = [
        (loaded.authored_target, recorded.target)
        for loaded, recorded in zip(fact.ballots, opened.entry.ballots, strict=True)
        if recorded.guard_rewrite_reason is None
    ]
    assert pairs and all(authored == target for authored, target in pairs)


def test_the_loader_refuses_a_meeting_applied_under_another_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = [
        replace(event, entry=event.entry.model_copy(update={"meeting_id": "other"}))
        if isinstance(event, MeetingApplied)
        else event
        for event in _events()
    ]
    with pytest.raises(ValueError, match="applied without opening"):
        _load(monkeypatch, events)


def test_the_game_over_row_joins_the_era_and_names_the_winner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    regroup = RecordedExperimentConfig(meeting_reset="hub_with_grace")
    footer_only = [
        replace(
            event,
            game_end=event.game_end.model_copy(update={"experiment_config": regroup}),
        )
        if isinstance(event, WalkComplete) and event.game_end is not None
        else event
        for event in events
    ]
    with pytest.raises(ValueError, match="terminal experiment configuration"):
        _load(monkeypatch, footer_only)
    assert _load(monkeypatch, events).winner in ("CREWMATES", "IMPOSTORS")
    without = [
        replace(event, game_end=None) if isinstance(event, WalkComplete) else event
        for event in events
    ]
    assert _load(monkeypatch, without).winner is None


def test_the_loader_refuses_dispositions_that_do_not_pair_with_the_actions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = _events()
    index = next(
        position
        for position, event in enumerate(events)
        if isinstance(event, TickAdvanced) and event.entry.action_dispositions
    )
    advanced = events[index]
    assert isinstance(advanced, TickAdvanced)
    dispositions = advanced.entry.action_dispositions
    assert dispositions is not None
    events[index] = replace(
        advanced,
        entry=advanced.entry.model_copy(
            update={"action_dispositions": dispositions[:-1]}
        ),
    )
    with pytest.raises(ValueError, match="zip"):
        _load(monkeypatch, events)


def test_the_loader_refuses_a_walk_that_never_ended(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events = [
        replace(event, terminal_tick=None) if isinstance(event, WalkComplete) else event
        for event in _events()
    ]
    with pytest.raises(ValueError, match="never reached its terminal tick"):
        _load(monkeypatch, events)


def test_the_loader_reads_a_recording_without_substrate_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unstamped(event: ReplayWalkEvent) -> ReplayWalkEvent:
        if isinstance(event, TickOpened):
            return replace(
                event, entry=event.entry.model_copy(update={"substrate_flags": None})
            )
        if isinstance(event, WalkComplete) and event.game_end is not None:
            return replace(
                event,
                game_end=event.game_end.model_copy(update={"substrate_flags": None}),
            )
        return event

    loaded = _load(monkeypatch, [unstamped(event) for event in _events()])
    assert loaded.era.substrate_flags is None


def test_the_selector_pick_reads_the_turns_before_the_first_repeat() -> None:
    def spoken(
        index: int,
        speaker: str,
        *,
        accuses: str | None = None,
        reply_to: str | None = None,
    ) -> MeetingTurn:
        return MeetingTurn(
            turn_id=f"t{index}",
            turn_index=index,
            speaker=speaker,
            turn_kind="opening" if index == 0 else "reply",
            reply_to=reply_to,
            claims=()
            if accuses is None
            else (
                AccusationClaim(
                    type="accusation", against=accuses, confidence=0.9, reason="r"
                ),
            ),
            free_text="",
        )

    living = frozenset(ROLES)
    turns = (
        spoken(0, "p-2"),
        spoken(1, "p-3", accuses="p-2", reply_to="t0"),
        spoken(2, "p-2", reply_to="t1"),
    )
    assert selector_pick(turns, living) == ("p-2", "t1")
    assert selector_pick(tuple(reversed(turns)), living) == ("p-2", "t1")
    assert selector_pick(turns[:2], living) is None
    unanswerable = (spoken(0, "p-2"), spoken(1, "p-3"), spoken(2, "p-2"))
    assert selector_pick(unanswerable, living) is None


# --------------------------------------------------------------------------- #
# Recorded settings reach the census walk by the spine's contract              #
# --------------------------------------------------------------------------- #


def _later_settings() -> tuple[tuple[str, SettingValue], ...]:
    """Every Stage-B setting outside the engine layer, derived from the spine.

    A value qualifies when the spine's own :func:`wave_settings` reports it: its
    field or the value itself did not exist before the wave. Engine settings are
    the helper's, tested below with a threaded field.
    """

    settings: list[tuple[str, SettingValue]] = []
    for name, info in RecordedExperimentConfig.model_fields.items():
        if FIELD_LAYER[name] in ("engine", "format"):
            continue
        for value in _literal_values(info.annotation):
            constructed: dict[str, Any] = {name: value}
            if wave_settings(RecordedExperimentConfig.model_construct(**constructed)):
                settings.append((name, value))
    return tuple(settings)


def _literal_values(annotation: Any) -> tuple[SettingValue, ...]:
    """The values a ``Literal`` annotation allows, through a union with ``None``."""

    if get_origin(annotation) is typing.Literal:
        return get_args(annotation)
    return tuple(
        value for part in get_args(annotation) for value in _literal_values(part)
    )


LATER_SETTINGS: tuple[tuple[str, SettingValue], ...] = _later_settings()


def test_the_later_settings_cover_every_layer_the_census_declares() -> None:
    assert {FIELD_LAYER[name] for name, _value in LATER_SETTINGS} == (
        CENSUS_THREADED_LAYERS
    )


def _open_pending_arms(monkeypatch: pytest.MonkeyPatch) -> None:
    """Let a planted recording carry an ON value no arm card has built yet."""

    monkeypatch.setattr(
        experiment_config, "WAVE_ARMS_PENDING", MappingProxyType({}), raising=False
    )


def _stamped_copy(directory: Path, settings: Mapping[str, object]) -> Path:
    """A copy of one committed game whose tick rows and footer record ``settings``."""

    source = SAMPLES_4P1I / f"replay-seed-{LOADER_SEED}.jsonl"
    rows = [
        json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()
    ]
    stamped = 0
    for row in rows:
        if row["kind"] in ("tick", "game_over"):
            row["experiment_config"] = {"format_version": 1, **settings}
            stamped += 1
    assert stamped > 1
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / source.name
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    return path


def _walked(path: Path) -> GameFacts:
    """``path`` loaded through the census's own walk, as the loader runs it."""

    committed = _committed_game()
    return census._load_game(
        path,
        seed=LOADER_SEED,
        roles=committed.roles,
        manifest_cell=", ".join(committed.era.prompt_stamps or ()),
        num_players=4,
        num_impostors=1,
        tasks_per_crewmate=1,
        game_map=MAP,
    )


def _spied_walk(monkeypatch: pytest.MonkeyPatch) -> list[ReplayWalkEvent]:
    """Record every event the census's walk yields, to see where it refused."""

    yielded: list[ReplayWalkEvent] = []
    from eval.replay_walk import walk_replay as real

    def spy(*args: Any, **kwargs: Any) -> Iterator[ReplayWalkEvent]:
        for event in real(*args, **kwargs):
            yielded.append(event)
            yield event

    monkeypatch.setattr(census, "walk_replay", spy)
    return yielded


def test_the_census_walk_reads_every_later_setting_it_declares(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A full-config copy walks with every hash verified, and each value is read.

    The copy carries every later setting outside the engine layer at its ON
    value. The walk verifies every recorded state hash, so the facts equal the
    committed game's; only the era differs, and it holds the recorded values.
    """

    _open_pending_arms(monkeypatch)
    settings = dict(LATER_SETTINGS)
    walked = _walked(_stamped_copy(tmp_path, settings))
    committed = _committed_game()
    assert dict(walked.era.values) == settings
    assert walked == replace(
        committed, era=replace(committed.era, settings=canonical_settings(settings))
    )
    for key in (
        "look_and_wait_exit",
        "own_fresh_kill_entry",
        "public_body_handle",
        "own_kill_ballot_row",
    ):
        assert PREDICATES[key].holds(walked.era.values), key
        assert not PREDICATES[key].holds(committed.era.values), key


def test_the_recorded_body_handle_setting_reaches_its_guard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """End to end: the committed opening carries the kill-tick handle.

    Read from a recording that says the public handle was ON, that opening is a
    breach naming the set, seed and meeting; the same game without the setting
    folds.
    """

    _open_pending_arms(monkeypatch)
    committed = _committed_game()
    assert any(item.opener_prompt_has_kill_tick_handle for item in committed.meetings)
    walked = _walked(_stamped_copy(tmp_path, {"report_body_handle_version": 1}))
    with pytest.raises(
        GameplayCensusConformanceError,
        match=f"report_body_handle_version = 1, but set {PLANTED}, seed {LOADER_SEED}, "
        "meeting ",
    ):
        fold_set(inputs(walked))
    fold_set(inputs(committed))


@pytest.mark.parametrize(("name", "value"), LATER_SETTINGS)
def test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: SettingValue,
) -> None:
    """Planted: the census profile with that setting's layer taken out."""

    _open_pending_arms(monkeypatch)
    path = _stamped_copy(tmp_path, {name: value})
    layer = FIELD_LAYER[name]
    monkeypatch.setattr(
        census,
        "CENSUS_WALK_CONFIG",
        replace(CENSUS_WALK_CONFIG, threaded_layers=CENSUS_THREADED_LAYERS - {layer}),
    )
    yielded = _spied_walk(monkeypatch)
    with pytest.raises(ValueError) as refused:
        _walked(path)
    message = str(refused.value)
    assert f"{name}={value!r}" in message and "'gameplay-census'" in message
    assert yielded == []
    monkeypatch.setattr(census, "CENSUS_WALK_CONFIG", CENSUS_WALK_CONFIG)
    assert dict(_walked(path).era.values) == {name: value}


def test_the_census_walk_takes_its_engine_settings_from_the_spines_helper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the helper patched to thread no engine field refuses one.

    Unpatched, the same copy walks and its era reads the recorded engine
    setting, so the refusal comes from the helper the walk goes through.
    """

    path = _stamped_copy(tmp_path, {"redistribution_policy": "least_remaining_work"})
    assert dict(_walked(path).era.values) == {
        "redistribution_policy": "least_remaining_work"
    }
    monkeypatch.setattr(experiment_config, "_THREADED_ENGINE_FIELDS", ())
    yielded = _spied_walk(monkeypatch)
    with pytest.raises(
        ValueError, match="redistribution_policy='least_remaining_work'"
    ):
        _walked(path)
    assert yielded == []


def test_a_recorded_setting_no_one_declared_is_refused_before_advancing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: a recording naming a field the config does not declare."""

    path = _stamped_copy(tmp_path, {"hidden_travel": "on"})
    yielded = _spied_walk(monkeypatch)
    with pytest.raises(ValueError, match="hidden_travel"):
        _walked(path)
    assert yielded == []


def test_a_declared_setting_the_census_has_not_classified_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: a stand-in field on the recorded config the census never reviewed."""

    class _StandIn(RecordedExperimentConfig):
        stand_in_rule: typing.Literal["old", "new"] = "old"

    stand_in = _StandIn(stand_in_rule="new")

    def stamped(event: ReplayWalkEvent) -> ReplayWalkEvent:
        if isinstance(event, TickOpened):
            return replace(
                event,
                entry=event.entry.model_copy(update={"experiment_config": stand_in}),
            )
        if isinstance(event, WalkComplete) and event.game_end is not None:
            return replace(
                event,
                game_end=event.game_end.model_copy(
                    update={"experiment_config": stand_in}
                ),
            )
        return event

    with pytest.raises(GameplayCensusFieldError, match="stand_in_rule"):
        _load(monkeypatch, [stamped(event) for event in _events()])


# --------------------------------------------------------------------------- #
# The loader's own refusals                                                    #
# --------------------------------------------------------------------------- #


def test_a_census_walk_outside_the_shared_cache_is_flagged() -> None:
    """The single-home pin names the census loader, so a second walk is caught."""

    from tests._helpers.test_committed_single_home import (
        WalkCall,
        committed_walk_calls,
    )

    planted = (
        "from tests._helpers.committed import SAMPLES_9P2I\n"
        "def test_planted() -> None:\n"
        "    load_census_inputs(SAMPLES_9P2I)\n"
    )
    assert committed_walk_calls(planted) == (
        WalkCall("load_census_inputs", "test_planted", 3),
    )


def test_the_loader_refuses_a_seed_in_the_unseen_band_before_reading_it(
    tmp_path: Path,
) -> None:
    (tmp_path / "replay-seed-2150.jsonl").write_text(
        "not a recording\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="no census walk may read"):
        census.load_census_inputs(tmp_path)


@pytest.mark.parametrize("seed", (2100, 2999))
def test_the_loader_refuses_both_edges_of_the_unseen_band(
    tmp_path: Path, seed: int
) -> None:
    (tmp_path / f"replay-seed-{seed}.jsonl").write_text(
        "not a recording\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="no census walk may read"):
        census.load_census_inputs(tmp_path)


def test_the_unseen_band_ends_at_its_edges() -> None:
    band = census.UNSEEN_SEED_BAND
    assert (2099 in band, 2100 in band, 2999 in band, 3000 in band) == (
        False,
        True,
        True,
        False,
    )


def test_the_loader_refuses_a_set_without_its_manifest_rows(tmp_path: Path) -> None:
    source = SAMPLES_4P1I / "replay-seed-0.jsonl"
    (tmp_path / "replay-seed-0.jsonl").write_bytes(source.read_bytes())
    with pytest.raises(FileNotFoundError, match="no MANIFEST.md"):
        census.load_census_inputs(tmp_path)
    (tmp_path / "MANIFEST.md").write_text(
        "| seed | model | prompt_versions |\n|---|---|---|\n| 1 | m | a.x.v1 |\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="no MANIFEST row"):
        census.load_census_inputs(tmp_path)


def test_the_manifest_reader_takes_the_third_cell_of_every_seed_row(
    tmp_path: Path,
) -> None:
    (tmp_path / "MANIFEST.md").write_text(
        "# title\n\nprose | with a pipe\n| seed | model | prompt_versions |\n"
        "|------|-------|-----------------|\n| 3 | m | a.x.v1, b.x.v2 | f | p |\n| 4 | m |\n",
        encoding="utf-8",
    )
    assert dict(census._manifest_prompt_cells(tmp_path)) == {3: "a.x.v1, b.x.v2"}


def test_the_manifest_reader_skips_prose_and_reads_a_three_cell_row(
    tmp_path: Path,
) -> None:
    (tmp_path / "MANIFEST.md").write_text(
        "5 | m | prose.x.v1\n| 6 | m | a.x.v1 |\n", encoding="utf-8"
    )
    assert dict(census._manifest_prompt_cells(tmp_path)) == {6: "a.x.v1"}


def test_the_cell_count_adds_field_by_field() -> None:
    assert CellCount(1, 2, 3) + CellCount(4, 5, 6) == CellCount(5, 7, 9)


def test_every_cell_and_table_is_published_and_ordered_under_a_heading() -> None:
    published = section_from_tally(fold_set(inputs(game())))
    assert list(published.cells) == list(CELLS)
    assert list(published.tables) == list(TABLES)
    assert {spec.heading for spec in CELLS.values()} <= set(census.HEADINGS)
    assert {spec.heading for spec in TABLES.values()} <= set(census.HEADINGS)
    ordered = section_from_tally(
        fold_set(
            inputs(
                game(
                    kills=(kill(1), kill(2), kill(3)),
                    bodies=(
                        body("a", 1),
                        body("b", 2),
                        body("c", 3),
                    ),
                    meetings=(
                        report(3, "a", meeting_id="m0"),
                        report(12, "b", meeting_id="m1"),
                        report(13, "c", meeting_id="m2"),
                    ),
                )
            )
        )
    )
    assert list(ordered.tables["corpse_age_at_report"].counts) == ["2", "10"]
    assert isinstance(ordered, census.CensusSection)
    assert isinstance(CensusTally, type)
