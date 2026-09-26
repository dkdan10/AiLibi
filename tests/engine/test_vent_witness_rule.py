"""The vent witness rule: who witnesses a vent entry or exit.

``advance_tick(vent_witness_rule=...)`` selects it. Under ``both_rooms``, the
default, a vent is witnessed by the living, non-vented occupants of the room
left and of the room surfaced into. Under ``physical`` an exit into another
room is witnessed only from the room surfaced into; an entry and an exit in
place are one-room under both. The connected-vent exit pair (the ``both_rooms``
pin and its ``physical`` twin) lives in ``tests/engine/test_tick.py``.
"""

from __future__ import annotations

import inspect
import re
from dataclasses import replace
from pathlib import Path
from typing import Literal, get_args

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import TypeAdapter

from engine.actions import Action, VentAction
from engine.entities import PlayerState, TaskState
from engine.events import EngineEvent, VentEnteredEvent, VentExitedEvent
from engine.rng import EngineRng
from engine.tick import VentWitnessRule, _apply_action, _apply_vent, advance_tick
from engine.world import Map, Vent, WorldState, load_canonical_map
from orchestrator.experiment_config import RecordedExperimentConfig

_MAP = load_canonical_map()
_ACTION: TypeAdapter[Action] = TypeAdapter(Action)
_CONTRACT = Path(__file__).resolve().parents[2] / "docs" / "observation-contract.md"
_ACTOR = "p-0"


def _vent(vent_id: str) -> Action:
    return _ACTION.validate_python(
        {"type": "vent", "actor": _ACTOR, "payload": {"vent_id": vent_id}}
    )


def _player(
    player_id: str,
    room: str,
    *,
    role: Literal["CREWMATE", "IMPOSTOR"] = "CREWMATE",
    alive: bool = True,
    in_vent: bool = False,
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role=role,
        alive=alive,
        room=room,
        position=(0.0, 0.0),
        last_action=None,
        in_vent=in_vent,
    )


def _scene(
    *, actor_room: str, actor_in_vent: bool, bystanders: tuple[PlayerState, ...]
) -> WorldState:
    """One impostor, ``p-0``, beside ``bystanders``, on the canonical map."""

    players = {
        _ACTOR: _player(_ACTOR, actor_room, role="IMPOSTOR", in_vent=actor_in_vent),
        **{player.id: player for player in bystanders},
    }
    owner = next(
        (
            player.id
            for player in bystanders
            if player.role == "CREWMATE" and player.alive
        ),
        None,
    )
    tasks = (
        {}
        if owner is None
        else {
            f"{owner}:swipe_card": TaskState(
                id=f"{owner}:swipe_card",
                owner=owner,
                map_task_id="swipe_card",
                room="ADMIN",
                progress=0,
                required_ticks=3,
                completed=False,
            )
        }
    )
    return WorldState(
        tick=0,
        phase="PLAY",
        map=_MAP.id,
        players=players,
        bodies={},
        tasks=tasks,
        sabotage=None,
        cooldowns={_ACTOR: 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(42).snapshot(),
        seed=42,
    )


def _advance(
    state: WorldState,
    vent_id: str,
    rule: VentWitnessRule,
    *,
    game_map: Map = _MAP,
) -> tuple[WorldState, list[EngineEvent]]:
    return advance_tick(
        state, [_vent(vent_id)], game_map=game_map, vent_witness_rule=rule
    )


# --------------------------------------------------------------------------- #
# Entries and exits in place are one-room under both rules                    #
# --------------------------------------------------------------------------- #


def test_an_entry_is_witnessed_from_its_one_room_under_both_rules() -> None:
    """p-2 stands in ADMIN, the room entered from; p-4 in REACTOR, beyond the vent."""

    state = _scene(
        actor_room="ADMIN",
        actor_in_vent=False,
        bystanders=(_player("p-2", "ADMIN"), _player("p-4", "REACTOR")),
    )
    outcomes = {
        rule: _advance(state, "ADMIN_VENT", rule) for rule in get_args(VentWitnessRule)
    }
    for _state, events in outcomes.values():
        entry = events[0]
        assert isinstance(entry, VentEnteredEvent)
        assert entry.source_room == entry.destination_room == "ADMIN"
        assert entry.witnesses == ("p-2",)
        assert entry.source_witnesses == ("p-2",)
        assert entry.destination_witnesses == ("p-2",)
        assert "p-4" not in entry.witnesses
    assert outcomes["physical"] == outcomes["both_rooms"]


def test_an_exit_in_place_is_witnessed_by_every_occupant_under_both_rules() -> None:
    """The impostor surfaces from ADMIN_VENT back into ADMIN, where p-1 and p-2 stand."""

    state = _scene(
        actor_room="ADMIN",
        actor_in_vent=True,
        bystanders=(
            _player("p-1", "ADMIN"),
            _player("p-2", "ADMIN"),
            _player("p-4", "REACTOR"),
        ),
    )
    outcomes = {
        rule: _advance(state, "ADMIN_VENT", rule) for rule in get_args(VentWitnessRule)
    }
    for _state, events in outcomes.values():
        exit_event = events[0]
        assert isinstance(exit_event, VentExitedEvent)
        assert exit_event.source_room == exit_event.destination_room == "ADMIN"
        assert exit_event.witnesses == ("p-1", "p-2")
        assert exit_event.source_witnesses == ("p-1", "p-2")
        assert exit_event.destination_witnesses == ("p-1", "p-2")
    assert outcomes["physical"] == outcomes["both_rooms"]


def test_a_physical_exit_follows_the_maps_vent_room() -> None:
    """Planted map: REACTOR_VENT moved into UPPER_HALL, a room with no vent.

    The exit from ADMIN_VENT through REACTOR_VENT now surfaces in UPPER_HALL,
    so the physical witnesses are UPPER_HALL's occupant, not REACTOR's; an exit
    in place through the moved vent is one-room in UPPER_HALL.
    """

    moved = Vent(
        id="REACTOR_VENT",
        room="UPPER_HALL",
        connects_to=_MAP.vents["REACTOR_VENT"].connects_to,
        traversal_ticks=_MAP.vents["REACTOR_VENT"].traversal_ticks,
    )
    planted = _MAP.model_copy(update={"vents": {**_MAP.vents, moved.id: moved}})
    state = _scene(
        actor_room="ADMIN",
        actor_in_vent=True,
        bystanders=(
            _player("p-2", "ADMIN"),
            _player("p-4", "REACTOR"),
            _player("p-5", "UPPER_HALL"),
        ),
    )
    _after, events = _advance(state, "REACTOR_VENT", "physical", game_map=planted)
    exit_event = events[0]
    assert isinstance(exit_event, VentExitedEvent)
    assert exit_event.destination_room == "UPPER_HALL"
    assert exit_event.witnesses == exit_event.destination_witnesses == ("p-5",)
    assert exit_event.source_witnesses == ()
    _after, canonical = _advance(state, "REACTOR_VENT", "physical")
    assert isinstance(canonical[0], VentExitedEvent)
    assert canonical[0].witnesses == ("p-4",)
    # An exit in place through the moved vent surfaces in UPPER_HALL, the room
    # it left, so its occupant stays a witness from both lists.
    in_place = _scene(
        actor_room="UPPER_HALL",
        actor_in_vent=True,
        bystanders=(_player("p-5", "UPPER_HALL"), _player("p-4", "REACTOR")),
    )
    _after, events = _advance(in_place, "REACTOR_VENT", "physical", game_map=planted)
    exit_event = events[0]
    assert isinstance(exit_event, VentExitedEvent)
    assert exit_event.source_room == exit_event.destination_room == "UPPER_HALL"
    assert exit_event.source_witnesses == exit_event.destination_witnesses == ("p-5",)


# --------------------------------------------------------------------------- #
# The default is today's rule, and an unknown rule raises                     #
# --------------------------------------------------------------------------- #


def test_the_default_rule_is_both_rooms_at_every_layer() -> None:
    assert get_args(VentWitnessRule) == ("both_rooms", "physical")
    signature = inspect.signature(advance_tick)
    assert signature.parameters["vent_witness_rule"].default == "both_rooms"
    field = RecordedExperimentConfig.model_fields["vent_witness_rule"]
    assert field.default == "both_rooms"
    assert get_args(field.annotation) == get_args(VentWitnessRule)


def test_the_per_action_entry_points_default_to_both_rooms() -> None:
    """The lab applies single actions; left unset, they run today's rule."""

    state = _scene(
        actor_room="ADMIN",
        actor_in_vent=True,
        bystanders=(_player("p-2", "ADMIN"), _player("p-4", "REACTOR")),
    )
    action = _vent("REACTOR_VENT")
    assert isinstance(action, VentAction)
    outcomes = [
        (
            _apply_action(state, _MAP, action),
            _apply_action(state, _MAP, action, vent_witness_rule="both_rooms"),
            _apply_action(state, _MAP, action, vent_witness_rule="physical"),
        ),
        (
            _apply_vent(state, _MAP, action),
            _apply_vent(state, _MAP, action, vent_witness_rule="both_rooms"),
            _apply_vent(state, _MAP, action, vent_witness_rule="physical"),
        ),
    ]
    for default, both, physical in outcomes:
        assert default == both != physical
        exit_event = physical[1]
        assert isinstance(exit_event, VentExitedEvent)
        assert exit_event.source_witnesses == ()


@pytest.mark.parametrize("rule", ["PHYSICAL", "both", "", "physical "])
def test_an_unknown_rule_raises_before_any_action_applies(rule: str) -> None:
    state = _scene(
        actor_room="ADMIN",
        actor_in_vent=False,
        bystanders=(_player("p-2", "ADMIN"),),
    )
    for actions in ([_vent("ADMIN_VENT")], []):
        with pytest.raises(
            ValueError, match=re.escape(f"unknown vent witness rule: {rule!r}")
        ):
            advance_tick(
                state,
                actions,
                game_map=_MAP,
                vent_witness_rule=rule,  # type: ignore[arg-type]
            )


# --------------------------------------------------------------------------- #
# The property over generated vent scenes                                     #
# --------------------------------------------------------------------------- #

_VENT_ROOMS: tuple[str, ...] = tuple(sorted(vent.room for vent in _MAP.vents.values()))
_ROOMS: tuple[str, ...] = tuple(sorted(_MAP.rooms))
_KINDS = ("entry", "exit_in_place", "exit_across")
_ROLES: tuple[Literal["CREWMATE", "IMPOSTOR"], ...] = ("CREWMATE", "IMPOSTOR")


@st.composite
def _vent_scenes(draw: st.DrawFn) -> tuple[WorldState, str, str]:
    """A scene, the vent the impostor uses, and which of the three kinds it is.

    Bystanders stand mostly in the room left or the room surfaced into, and are
    living, vented or dead crewmates or a teammate.
    """

    actor_room = draw(st.sampled_from(_VENT_ROOMS))
    current = _MAP.vent_for_room(actor_room)
    assert current is not None
    kind = draw(st.sampled_from(_KINDS))
    vent_id = (
        draw(st.sampled_from(sorted(current.connects_to)))
        if kind == "exit_across"
        else current.id
    )
    destination_room = _MAP.vents[vent_id].room
    rooms = st.one_of(
        st.sampled_from((actor_room, destination_room)), st.sampled_from(_ROOMS)
    )
    count = draw(st.integers(min_value=0, max_value=8))
    bystanders: list[PlayerState] = []
    for index in range(1, count + 1):
        status = draw(st.sampled_from(("alive", "vented", "dead")))
        role = draw(st.sampled_from(_ROLES))
        bystanders.append(
            _player(
                f"p-{index}",
                draw(rooms),
                role=role,
                alive=status != "dead",
                in_vent=status == "vented",
            )
        )
    state = _scene(
        actor_room=actor_room,
        actor_in_vent=kind != "entry",
        bystanders=tuple(bystanders),
    )
    return state, vent_id, kind


@settings(deadline=None, max_examples=300)
@given(_vent_scenes())
def test_the_rule_changes_only_a_cross_room_exits_room_left(
    scene: tuple[WorldState, str, str],
) -> None:
    state, vent_id, kind = scene
    default = advance_tick(state, [_vent(vent_id)], game_map=_MAP)
    both = _advance(state, vent_id, "both_rooms")
    physical = _advance(state, vent_id, "physical")
    # The default call is today's rule, byte for byte.
    assert default == both
    both_state, both_events = both
    physical_state, physical_events = physical
    vent = both_events[0]
    assert isinstance(vent, VentEnteredEvent if kind == "entry" else VentExitedEvent)
    assert (vent.source_room != vent.destination_room) == (kind == "exit_across")
    # The rule never touches state, nor any event after the vent.
    assert physical_state == both_state
    assert physical_events[1:] == both_events[1:]
    if kind == "exit_across":
        assert physical_events[0] == replace(
            vent, source_witnesses=(), witnesses=vent.destination_witnesses
        )
    else:
        assert physical_events[0] == vent


# --------------------------------------------------------------------------- #
# The observation contract states the rule                                    #
# --------------------------------------------------------------------------- #


def _contract_problems(
    text: str, *, values: tuple[str, ...], default: str
) -> list[str]:
    """What the contract's vent-witness paragraph fails to state."""

    paragraphs = [
        " ".join(block.split())
        for block in re.split(r"\n\s*\n", text)
        if "`vent_witness_rule`" in block
    ]
    if len(paragraphs) != 1:
        return [
            f"expected one paragraph naming `vent_witness_rule`, found {len(paragraphs)}"
        ]
    paragraph = paragraphs[0]
    problems = [
        f"the paragraph does not name the value `{value}`"
        for value in values
        if f"`{value}`" not in paragraph
    ]
    if not re.search(rf"default, `{re.escape(default)}`", paragraph):
        problems.append(f"the paragraph does not name `{default}` as the default")
    if f"without the key reads as `{default}`" not in paragraph:
        problems.append("the paragraph does not say what a missing key reads as")
    return problems


def _rule_default() -> str:
    default = inspect.signature(advance_tick).parameters["vent_witness_rule"].default
    assert isinstance(default, str)
    return default


def test_the_contract_names_every_rule_and_the_default() -> None:
    assert (
        _contract_problems(
            _CONTRACT.read_text(encoding="utf-8"),
            values=get_args(VentWitnessRule),
            default=_rule_default(),
        )
        == []
    )


def test_the_contract_check_bites_a_new_value_and_a_deleted_sentence() -> None:
    text = _CONTRACT.read_text(encoding="utf-8")
    widened = (*get_args(VentWitnessRule), "hidden_travel")
    assert _contract_problems(text, values=widened, default=_rule_default()) == [
        "the paragraph does not name the value `hidden_travel`"
    ]
    paragraph = next(
        block for block in re.split(r"\n\s*\n", text) if "`vent_witness_rule`" in block
    )
    deleted = text.replace(paragraph, "")
    assert _contract_problems(
        deleted, values=get_args(VentWitnessRule), default=_rule_default()
    ) == ["expected one paragraph naming `vent_witness_rule`, found 0"]
    flipped = text.replace("default, `both_rooms`", "default, `physical`")
    assert _contract_problems(
        flipped, values=get_args(VentWitnessRule), default=_rule_default()
    ) == ["the paragraph does not name `both_rooms` as the default"]
