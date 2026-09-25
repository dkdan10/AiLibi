"""The gameplay census: every cell planted on a hand-built carrier.

Each test below builds a :class:`eval.gameplay_census.CensusInputs` by hand and
folds it, so no replay is read unless the test says so. The few tests that read
committed bytes go through ``tests/_helpers/committed.py``: the figures test
reads only the committed JSON, and the loader tests replay a perturbed copy of
one committed game's walk.
"""

from __future__ import annotations

import dataclasses
import json
import typing
from collections import Counter
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, get_args, get_origin

import pytest

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
from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    AlibiSegment,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
    TaskActivityAccount,
    WhereaboutsClaim,
)
from orchestrator.experiment_config import RecordedExperimentConfig
from tests._helpers.committed import (
    SAMPLES_4P1I,
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
    )


def unclassified(
    fields: Iterable[str], classification: Mapping[str, FieldUse]
) -> list[str]:
    return sorted(set(fields) - set(classification))


def test_every_recorded_setting_field_is_classified() -> None:
    assert (
        unclassified(RecordedExperimentConfig.model_fields, FIELD_CLASSIFICATION) == []
    )


def test_a_classification_missing_one_field_fails() -> None:
    planted = {
        name: use
        for name, use in FIELD_CLASSIFICATION.items()
        if name != "meeting_reset"
    }
    assert unclassified(RecordedExperimentConfig.model_fields, planted) == [
        "meeting_reset"
    ]


def test_the_names_read_before_the_spine_declares_them() -> None:
    """Five names are read ahead of their declaration; this fails once they land.

    When the arm spine declares them on the config, this difference empties and
    the test goes red, so the census's own defaults are retired in the same
    change that brings the declared ones.
    """

    assert set(FIELD_CLASSIFICATION) - set(RecordedExperimentConfig.model_fields) == {
        "vent_witness_rule",
        "vent_entry_policy",
        "report_body_handle_version",
        "ballot_kill_row_version",
        "impostor_ballot_version",
    }


def test_the_defaults_match_the_config_model() -> None:
    for name, declared in RecordedExperimentConfig.model_fields.items():
        assert SETTING_DEFAULTS[name] == declared.default, name


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
    uncitable = game(
        {"ballot_kill_row_version": 1},
        meetings=(
            meeting(own_kill_rows=(OwnKillRowFact("p-2", "p-0", ROOM, 13, None),)),
        ),
    )
    assert counts("own_kill_rows_breaching", uncitable) == (0, 0, 1)


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


def test_a_surfacing_at_the_cap_is_forced_not_a_breach() -> None:
    capped = game(
        {"vent_exit_policy": "look_and_wait"},
        vents=(entry(10), exit_(10 + IN_VENT_CAP_TICKS)),
        frames={10 + IN_VENT_CAP_TICKS: frame({"p-2": ROOM})},
    )
    assert counts("surfacings_before_cap_in_view", capped) == (0, 1, 0)
    assert counts("forced_surfacings", capped) == (1, 1, 0)
    assert counts("trips_longer_than_cap", capped) == (0, 1, 0)
    assert table("ticks_inside_per_trip", capped) == {str(IN_VENT_CAP_TICKS): 1}


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


def test_a_trip_is_closed_by_a_regroup_an_ejection_or_the_game_end() -> None:
    regrouped = game(vents=(entry(10),), meetings=(meeting(tick=12, regrouped=True),))
    assert counts("trips_closed_by_regroup", regrouped) == (1, 1, 0)
    assert counts("trips_longer_than_cap", regrouped) == (0, 1, 0)
    ejected = game(
        vents=(entry(10),),
        meetings=(meeting(tick=12, outcome="EJECTED", ejected="p-0"),),
    )
    assert counts("trips_closed_by_regroup", ejected) == (0, 1, 0)
    preserved = game(vents=(entry(10),), meetings=(meeting(tick=12),), terminal_tick=14)
    assert counts("trips_closed_by_regroup", preserved) == (0, 1, 0)
    assert counts("trips_longer_than_cap", preserved) == (0, 1, 0)
    unfinished = game(vents=(entry(10),), terminal_tick=None, winner=None)
    assert counts("trips_closed_by_regroup", unfinished) == (0, 0, 0)
    assert counts("impostor_wins", unfinished) == (0, 0, 1)


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
    assert table("trigger_tick_events_dropped_by_regroup", planted) == {
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
    kept = game(meetings=(replace(regroup, regrouped=False),))
    assert counts("sabotage_active_at_regroup", kept) == (0, 0, 0)
    assert table("trigger_tick_events_dropped_by_regroup", kept) == {}


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


def test_opener_rebuttals_answer_the_charged_tick() -> None:
    def answered(
        *evidence: ObservationFact,
        alibi: AlibiFact | None = None,
        charge_tick: int | None = 5,
    ) -> GameFacts:
        charge_observations = (
            () if charge_tick is None else (seen("saw_vent", charge_tick, "p-2"),)
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
# The loader, on a perturbed copy of one committed game's walk                 #
# --------------------------------------------------------------------------- #

LOADER_SEED = 5


def _events() -> list[ReplayWalkEvent]:
    return list(census_walk_events(SAMPLES_4P1I, LOADER_SEED))


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
