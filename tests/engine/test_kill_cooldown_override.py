"""The recorded kill cooldown: the field, the one resolver and the three writes.

``kill_cooldown_ticks`` is an engine-layer field of the recorded config. ``None``
means the map's own value; a recorded integer sets the cooldown an impostor
holds at round start, on the state after each of its kills and after each
regroup. One engine function turns the recorded value into the cooldown, and
every entry point that writes or may write a cooldown resolves through it
before it changes any state.

The plants at the bottom restore each write, alone, to the map's value and
show that exactly that write's case fails.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import replace
from typing import Any, Final

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

import engine.meeting_reset as meeting_reset_module
import engine.tick as tick_module
import orchestrator.seeder as seeder_module
from engine.actions import KillAction, WaitAction
from engine.entities import PlayerId
from engine.meeting_reset import regroup_after_meeting
from engine.tick import _apply_action, _apply_kill, advance_tick
from engine.world import Map, WorldState, load_canonical_map, resolve_kill_cooldown
from meetings.schemas import MeetingResult, MeetingTranscript
from orchestrator import experiment_config
from orchestrator.experiment_config import (
    FIELD_LAYER,
    OMITTED_AT_DEFAULT,
    RecordedExperimentConfig,
    normalize_experiment_config,
    wave_settings,
)
from orchestrator.game import apply_meeting_result
from orchestrator.seeder import seed_initial_state

MAP: Final[Map] = load_canonical_map()
#: The value round 2 records, against the canonical map's 4.
SIX: Final[int] = 6
#: The 9-player sample roster.
ROSTER: Final[Mapping[str, int]] = {
    "num_players": 9,
    "num_impostors": 2,
    "tasks_per_crewmate": 2,
}

#: Round 1's declared config, byte for byte, and round 2's: the same eight
#: fields with the cooldown appended before the closing brace.
ROUND_ONE_JSON: Final[str] = (
    '{"format_version": 1, "meeting_reset": "hub_with_grace", '
    '"vent_exit_policy": "look_and_wait", "vent_entry_policy": "own_fresh_kill", '
    '"vent_witness_rule": "physical", "bounded_rebuttal_version": 1, '
    '"report_body_handle_version": 1, "ballot_kill_row_version": 1, '
    '"impostor_ballot_version": 1}'
)
ROUND_TWO_JSON: Final[str] = ROUND_ONE_JSON[:-1] + ', "kill_cooldown_ticks": 6}'


def _impostors(state: WorldState) -> tuple[PlayerId, ...]:
    return tuple(
        sorted(
            pid for pid, player in state.players.items() if player.role == "IMPOSTOR"
        )
    )


def _crewmate(state: WorldState) -> PlayerId:
    return min(
        pid
        for pid, player in state.players.items()
        if player.role == "CREWMATE" and player.alive
    )


# --------------------------------------------------------------------------- #
# The field                                                                   #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        (0, "at least 1 tick"),
        (-1, "at least 1 tick"),
        (True, "an integer number of ticks"),
        (6.0, "an integer number of ticks"),
        ("6", "an integer number of ticks"),
    ],
    ids=repr,
)
def test_only_a_true_integer_of_at_least_one_validates(
    value: object, reason: str
) -> None:
    with pytest.raises(ValidationError, match=f"kill_cooldown_ticks must be {reason}"):
        RecordedExperimentConfig.model_validate({"kill_cooldown_ticks": value})


def test_a_set_value_round_trips_and_dumps_its_key() -> None:
    config = RecordedExperimentConfig(kill_cooldown_ticks=SIX)
    payload = config.model_dump(mode="json")
    assert payload["kill_cooldown_ticks"] == SIX
    assert json.loads(config.model_dump_json())["kill_cooldown_ticks"] == SIX
    assert RecordedExperimentConfig.model_validate(payload) == config
    assert RecordedExperimentConfig.model_validate_json(config.model_dump_json()) == (
        config
    )
    assert not config.is_default
    assert normalize_experiment_config(config) is config


def test_the_default_dumps_no_key_and_reads_as_no_config() -> None:
    for config in (
        RecordedExperimentConfig(),
        RecordedExperimentConfig(kill_cooldown_ticks=None),
        RecordedExperimentConfig.model_validate({"kill_cooldown_ticks": None}),
    ):
        assert config.kill_cooldown_ticks is None
        assert "kill_cooldown_ticks" not in config.model_dump()
        assert "kill_cooldown_ticks" not in json.loads(config.model_dump_json())
        assert config.is_default
        assert normalize_experiment_config(config) is None


def test_a_cooldown_only_config_changes_no_tactical_policy() -> None:
    assert not RecordedExperimentConfig(kill_cooldown_ticks=SIX).has_tactical_changes


def test_the_field_is_an_engine_setting_omitted_at_default_and_new_to_the_wave() -> (
    None
):
    names = list(RecordedExperimentConfig.model_fields)
    assert (
        names.index("kill_cooldown_ticks") == names.index("impostor_ballot_version") + 1
    )
    assert FIELD_LAYER["kill_cooldown_ticks"] == "engine"
    assert "kill_cooldown_ticks" in OMITTED_AT_DEFAULT
    assert "kill_cooldown_ticks" not in experiment_config._PRE_WAVE_VALUES
    assert wave_settings(RecordedExperimentConfig(kill_cooldown_ticks=SIX)) == (
        ("kill_cooldown_ticks", SIX),
    )


def test_the_round_two_declaration_validates_in_the_first_format() -> None:
    round_one = RecordedExperimentConfig.model_validate_json(ROUND_ONE_JSON)
    round_two = RecordedExperimentConfig.model_validate_json(ROUND_TWO_JSON)
    assert round_two.format_version == 1
    assert round_two.kill_cooldown_ticks == SIX
    assert round_two.model_dump() == {
        **round_one.model_dump(),
        "kill_cooldown_ticks": SIX,
    }
    assert "kill_cooldown_ticks" not in round_one.model_dump()
    non_default = {
        field
        for field, info in RecordedExperimentConfig.model_fields.items()
        if getattr(round_two, field) != info.default
    }
    assert non_default == set(json.loads(ROUND_ONE_JSON)) - {"format_version"} | {
        "kill_cooldown_ticks"
    }


def test_without_the_omission_rule_the_first_archive_row_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Perturbed: the field left out of the omit-at-default list.

    Every committed payload then gains a ``"kill_cooldown_ticks": null`` key,
    so the committed-payload walk fails at its first archive row.
    """

    from tests.orchestrator.test_experiment_arms import (
        _ARCHIVE,
        _REPO,
        _first_recorded_mismatch,
    )

    assert _first_recorded_mismatch()[0] is None
    monkeypatch.setattr(
        experiment_config,
        "OMITTED_AT_DEFAULT",
        tuple(name for name in OMITTED_AT_DEFAULT if name != "kill_cooldown_ticks"),
    )
    mismatch, rows, _files = _first_recorded_mismatch()
    first_file = min(_ARCHIVE.glob("*.jsonl"))
    assert mismatch == f"{first_file.relative_to(_REPO)}:1"
    assert rows == 1


# --------------------------------------------------------------------------- #
# The resolver                                                                #
# --------------------------------------------------------------------------- #


def test_the_resolver_reads_the_map_for_none_and_the_override_otherwise() -> None:
    assert MAP.kill_cooldown_ticks == 4
    assert resolve_kill_cooldown(MAP, None) == MAP.kill_cooldown_ticks
    assert resolve_kill_cooldown(MAP, SIX) == SIX
    assert resolve_kill_cooldown(MAP, 1) == 1
    other = MAP.model_copy(update={"kill_cooldown_ticks": 9})
    assert resolve_kill_cooldown(other, None) == 9
    assert resolve_kill_cooldown(other, SIX) == SIX


@pytest.mark.parametrize("value", [0, -1, True, False, 6.0, "6"], ids=repr)
def test_the_resolver_refuses_anything_but_an_integer_of_at_least_one(
    value: object,
) -> None:
    with pytest.raises(ValueError, match="kill cooldown must be") as refused:
        resolve_kill_cooldown(MAP, value)  # type: ignore[arg-type]
    # The message names the value it refused.
    assert str(refused.value).endswith(f"got {value!r}")


@given(value=st.integers(min_value=1, max_value=10_000))
def test_every_integer_of_at_least_one_resolves_to_itself(value: int) -> None:
    assert resolve_kill_cooldown(MAP, value) == value


@given(value=st.integers(max_value=0))
def test_every_integer_below_one_is_refused(value: int) -> None:
    with pytest.raises(ValueError, match="kill cooldown"):
        resolve_kill_cooldown(MAP, value)


# --------------------------------------------------------------------------- #
# The three writes                                                            #
# --------------------------------------------------------------------------- #


def round_start(kill_cooldown_ticks: int | None) -> dict[PlayerId, int]:
    """Every seeded impostor's cooldown."""

    state = seed_initial_state(
        seed=0, game_map=MAP, kill_cooldown_ticks=kill_cooldown_ticks, **ROSTER
    )
    impostors = _impostors(state)
    assert len(impostors) == ROSTER["num_impostors"]
    return {pid: state.cooldowns[pid] for pid in impostors}


def _ready_to_kill() -> tuple[WorldState, KillAction]:
    """A seeded state whose first impostor may kill a crewmate in its room."""

    state = seed_initial_state(seed=0, game_map=MAP, **ROSTER)
    killer = _impostors(state)[0]
    target = _crewmate(state)
    assert state.players[killer].room == state.players[target].room
    action = KillAction.model_validate(
        {"type": "kill", "actor": killer, "payload": {"target": target}}
    )
    return replace(state, cooldowns={pid: 0 for pid in state.cooldowns}), action


def after_kill(kill_cooldown_ticks: int | None) -> dict[PlayerId, int]:
    """The killer's cooldown on its kill tick's resulting state."""

    state, action = _ready_to_kill()
    after, events = advance_tick(
        state, [action], game_map=MAP, kill_cooldown_ticks=kill_cooldown_ticks
    )
    assert [event.type for event in events][:1] == ["Killed"]
    assert after.phase == "PLAY"
    assert not after.players[action.payload.target].alive
    return {action.actor: after.cooldowns[action.actor]}


def _in_meeting() -> WorldState:
    """A seeded state at a meeting, every impostor's cooldown run down to 0."""

    state = seed_initial_state(seed=0, game_map=MAP, **ROSTER)
    return replace(
        state, phase="MEETING", cooldowns={pid: 0 for pid in state.cooldowns}
    )


def _skipped(state: WorldState) -> MeetingResult:
    return MeetingResult(
        meeting_id="meeting-0",
        triggered_by=_crewmate(state),
        trigger_tick=state.tick,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
        transcript=MeetingTranscript(),
    )


def regroup(kill_cooldown_ticks: int | None) -> dict[PlayerId, int]:
    """Every living impostor's cooldown after a regroup, through both entry points."""

    state = _in_meeting()
    direct = regroup_after_meeting(
        state, game_map=MAP, kill_cooldown_ticks=kill_cooldown_ticks
    )
    applied, events = apply_meeting_result(
        state,
        _skipped(state),
        game_map=MAP,
        meeting_reset="hub_with_grace",
        kill_cooldown_ticks=kill_cooldown_ticks,
    )
    assert events == [] and applied.phase == "PLAY"
    assert applied.cooldowns == direct.cooldowns
    living = {
        pid
        for pid, player in applied.players.items()
        if player.alive and player.role == "IMPOSTOR"
    }
    assert set(applied.cooldowns) == living and len(living) == 2
    return dict(applied.cooldowns)


#: Each write, by the name of the writer, with the module whose binding of the
#: resolver that writer calls.
WRITES: Final[Mapping[str, Callable[[int | None], dict[PlayerId, int]]]] = {
    "round_start": round_start,
    "after_kill": after_kill,
    "regroup": regroup,
}
WRITER_MODULES: Final[Mapping[str, Any]] = {
    "round_start": seeder_module,
    "after_kill": tick_module,
    "regroup": meeting_reset_module,
}


def _holds(write: Callable[[int | None], dict[PlayerId, int]], value: int) -> bool:
    written = write(SIX)
    return bool(written) and set(written.values()) == {value}


@pytest.mark.parametrize("writer", sorted(WRITES))
def test_a_recorded_value_is_written_and_none_writes_the_maps(writer: str) -> None:
    write = WRITES[writer]
    assert set(write(SIX).values()) == {SIX}
    assert set(write(None).values()) == {MAP.kill_cooldown_ticks}


@settings(deadline=None, max_examples=25)
@given(value=st.one_of(st.none(), st.integers(min_value=1, max_value=40)))
def test_every_write_holds_the_resolved_value(value: int | None) -> None:
    expected = MAP.kill_cooldown_ticks if value is None else value
    for writer, write in WRITES.items():
        assert set(write(value).values()) == {expected}, writer


def _entry_points() -> dict[str, Callable[[int], object]]:
    """Each entry point that takes the keyword, called with ``value``."""

    ready, action = _ready_to_kill()
    wait = WaitAction.model_validate(
        {"type": "wait", "actor": action.actor, "payload": {}}
    )
    meeting = _in_meeting()
    return {
        "seed_initial_state": lambda value: seed_initial_state(
            seed=0, game_map=MAP, kill_cooldown_ticks=value, **ROSTER
        ),
        "advance_tick": lambda value: advance_tick(
            ready, [action], game_map=MAP, kill_cooldown_ticks=value
        ),
        "_apply_action": lambda value: _apply_action(
            ready, MAP, action, kill_cooldown_ticks=value
        ),
        "_apply_action (wait)": lambda value: _apply_action(
            ready, MAP, wait, kill_cooldown_ticks=value
        ),
        "_apply_kill": lambda value: _apply_kill(
            ready, MAP, action, kill_cooldown_ticks=value
        ),
        "regroup_after_meeting": lambda value: regroup_after_meeting(
            meeting, game_map=MAP, kill_cooldown_ticks=value
        ),
        "apply_meeting_result": lambda value: apply_meeting_result(
            meeting,
            _skipped(meeting),
            game_map=MAP,
            meeting_reset="hub_with_grace",
            kill_cooldown_ticks=value,
        ),
        "apply_meeting_result (preserve)": lambda value: apply_meeting_result(
            meeting, _skipped(meeting), game_map=MAP, kill_cooldown_ticks=value
        ),
    }


@pytest.mark.parametrize("entry_point", sorted(_entry_points()))
@pytest.mark.parametrize("value", [0, -3, True, 6.0], ids=repr)
def test_an_invalid_value_raises_at_every_entry_point_before_any_change(
    entry_point: str, value: object
) -> None:
    ready, _action = _ready_to_kill()
    meeting = _in_meeting()
    before = (replace(ready), replace(meeting))
    with pytest.raises(ValueError, match="kill cooldown"):
        _entry_points()[entry_point](value)  # type: ignore[arg-type]
    assert (ready, meeting) == before


def test_advance_tick_refuses_before_applying_any_action(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ready, action = _ready_to_kill()

    def _applied(*args: object, **kwargs: object) -> object:
        raise AssertionError("an action was applied under an invalid cooldown")

    monkeypatch.setattr(tick_module, "_apply_action", _applied)
    with pytest.raises(ValueError, match="kill cooldown"):
        advance_tick(ready, [action], game_map=MAP, kill_cooldown_ticks=0)


# --------------------------------------------------------------------------- #
# Planted: each write restored to the map's value                             #
# --------------------------------------------------------------------------- #


def _map_value(game_map: Map, kill_cooldown_ticks: int | None) -> int:
    """The planted resolver: the map's value whatever was recorded."""

    return game_map.kill_cooldown_ticks


@pytest.mark.parametrize("planted", sorted(WRITES))
def test_restoring_one_write_to_the_map_fails_that_case_and_only_it(
    planted: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(WRITER_MODULES[planted], "resolve_kill_cooldown", _map_value)
    holding = {writer: _holds(write, SIX) for writer, write in WRITES.items()}
    assert holding == {writer: writer != planted for writer in WRITES}


def test_every_writer_module_binds_the_one_resolver() -> None:
    for writer, module in WRITER_MODULES.items():
        assert module.resolve_kill_cooldown is resolve_kill_cooldown, writer
