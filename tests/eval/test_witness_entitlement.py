from __future__ import annotations

import ast
import inspect
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from typing import get_args

import pytest
from pydantic import TypeAdapter

import eval.temporal_entitlement as temporal_entitlement
import eval.witness_entitlement as witness_entitlement
from engine.actions import Action
from engine.events import EngineEvent, KilledEvent, VentExitedEvent
from engine.tick import VentWitnessRule, advance_tick
from engine.world import Map, Vent, WorldState, load_canonical_map
from eval.leak_scan import (
    PacketContext,
    assert_no_factory_packet_leaks,
    _reconstruct_factory_records,
)
from eval.witness_entitlement import assert_event_witnesses_match_source_state
from observation.service import ObservationService
from orchestrator.seeder import seed_initial_state
from tests.engine.test_vent_witness_rule import _player as _scene_player
from tests.engine.test_vent_witness_rule import _scene, _vent


def _action(kind: str, actor: str, **payload: str) -> Action:
    return TypeAdapter(Action).validate_python(
        {"type": kind, "actor": actor, "payload": payload}
    )


@pytest.mark.parametrize("moves_first", [False, True])
def test_witnesses_follow_event_order_not_the_final_snapshot(moves_first: bool) -> None:
    game_map = load_canonical_map()
    before = seed_initial_state(
        seed=0, game_map=game_map, num_players=9, num_impostors=2
    )
    impostor = next(pid for pid, p in before.players.items() if p.role == "IMPOSTOR")
    victim, observer = [
        pid for pid, p in before.players.items() if p.role == "CREWMATE"
    ][:2]
    before = replace(before, cooldowns={pid: 0 for pid in before.cooldowns})
    kill = _action("kill", impostor, target=victim)
    move = _action("move", observer, to_room="EAST_HALL")
    after, events = advance_tick(
        before, [move, kill] if moves_first else [kill, move], game_map=game_map
    )
    killed = next(event for event in events if isinstance(event, KilledEvent))
    assert (observer in killed.witnesses) is not moves_first
    assert_event_witnesses_match_source_state(
        pre_state=before,
        state=after,
        events=events,
        game_map=game_map,
        vent_witness_rule="both_rooms",
    )
    corrupted = replace(
        killed,
        witnesses=tuple(pid for pid in killed.witnesses if pid != observer)
        if not moves_first
        else tuple(sorted((*killed.witnesses, observer))),
    )
    poisoned: Sequence[EngineEvent] = [
        corrupted if event is killed else event for event in events
    ]
    with pytest.raises(AssertionError, match="kill witness entitlement"):
        assert_event_witnesses_match_source_state(
            pre_state=before,
            state=after,
            events=poisoned,
            game_map=game_map,
            vent_witness_rule="both_rooms",
        )


def test_a_witness_killed_later_keeps_the_earlier_entitlement() -> None:
    game_map = load_canonical_map()
    before = seed_initial_state(
        seed=0, game_map=game_map, num_players=9, num_impostors=2
    )
    impostors = [pid for pid, p in before.players.items() if p.role == "IMPOSTOR"]
    first, second = [pid for pid, p in before.players.items() if p.role == "CREWMATE"][
        :2
    ]
    before = replace(before, cooldowns={pid: 0 for pid in before.cooldowns})
    after, events = advance_tick(
        before,
        [
            _action("kill", impostors[0], target=first),
            _action("kill", impostors[1], target=second),
        ],
        game_map=game_map,
    )
    first_kill = next(event for event in events if isinstance(event, KilledEvent))
    assert second in first_kill.witnesses and not after.players[second].alive
    assert_event_witnesses_match_source_state(
        pre_state=before,
        state=after,
        events=events,
        game_map=game_map,
        vent_witness_rule="both_rooms",
    )


def test_factory_scan_rejects_another_crewmates_valid_task_id(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=9, num_impostors=2
    )
    observer = next(pid for pid, p in state.players.items() if p.role == "CREWMATE")
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    try:
        packet = service.build_packet(
            world_state=state, agent_id=observer, engine_events=()
        )
    finally:
        service.close()
    context = PacketContext((), state, game_map)
    assert_no_factory_packet_leaks([(packet, context)])
    foreign = next(
        task.map_task_id
        for task in state.tasks.values()
        if task.owner != observer
        and task.map_task_id not in packet.self_state.owned_task_ids
    )
    poisoned = packet.model_copy(
        update={
            "self_state": packet.self_state.model_copy(
                update={"owned_task_ids": (foreign,), "pending_task_id": None}
            )
        }
    )
    with pytest.raises(AssertionError, match="engine-truth own unfinished set"):
        assert_no_factory_packet_leaks([(poisoned, context)])


def test_factory_reconstruction_checks_the_actual_engine_witness_producer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A missing witness list changes no engine hash, so strict hash equality
    # alone cannot detect this producer mutation.
    monkeypatch.setattr("engine.rules._witnesses_in_room", lambda *args, **kwargs: ())
    source = Path("replays/samples/9p2i/replay-seed-23.jsonl")
    with pytest.raises(AssertionError, match="witness entitlement"):
        _reconstruct_factory_records(
            source,
            game_map=load_canonical_map(),
            seed=23,
            num_players=9,
            num_impostors=2,
            tasks_per_crewmate=2,
            audit_dir=tmp_path,
        )


# --------------------------------------------------------------------------- #
# The vent witness rule: the oracle re-derives each list under the rule the   #
# recording was made under                                                     #
# --------------------------------------------------------------------------- #

_MAP = load_canonical_map()


def _cross_room_exit(
    rule: VentWitnessRule, *, game_map: Map = _MAP
) -> tuple[WorldState, WorldState, list[EngineEvent]]:
    """p-0 exits ADMIN_VENT through REACTOR_VENT.

    p-2 stands in ADMIN, the room left, and p-4 in REACTOR, where the impostor
    surfaces; p-5 stands in UPPER_HALL, a room with no vent.
    """

    before = _scene(
        actor_room="ADMIN",
        actor_in_vent=True,
        bystanders=(
            _scene_player("p-2", "ADMIN"),
            _scene_player("p-4", "REACTOR"),
            _scene_player("p-5", "UPPER_HALL"),
        ),
    )
    after, events = advance_tick(
        before, [_vent("REACTOR_VENT")], game_map=game_map, vent_witness_rule=rule
    )
    return before, after, events


def _check(
    before: WorldState,
    after: WorldState,
    events: Sequence[EngineEvent],
    rule: VentWitnessRule,
    *,
    game_map: Map = _MAP,
) -> None:
    assert_event_witnesses_match_source_state(
        pre_state=before,
        state=after,
        events=events,
        game_map=game_map,
        vent_witness_rule=rule,
    )


def test_a_room_left_source_witness_is_rejected_under_physical_only() -> None:
    before, after, events = _cross_room_exit("both_rooms")
    exit_event = events[0]
    assert isinstance(exit_event, VentExitedEvent)
    assert exit_event.source_witnesses == ("p-2",)
    _check(before, after, events, "both_rooms")
    with pytest.raises(AssertionError, match="vent source witness entitlement"):
        _check(before, after, events, "physical")


def test_a_correct_physical_exit_fails_an_oracle_left_at_both_rooms() -> None:
    """The refuter's hard-fail: the unthreaded oracle rejects a correct recording."""

    before, after, events = _cross_room_exit("physical")
    exit_event = events[0]
    assert isinstance(exit_event, VentExitedEvent)
    assert exit_event.source_witnesses == ()
    assert exit_event.witnesses == exit_event.destination_witnesses == ("p-4",)
    _check(before, after, events, "physical")
    with pytest.raises(AssertionError, match="vent source witness entitlement"):
        _check(before, after, events, "both_rooms")


_Forgery = Callable[[VentExitedEvent], VentExitedEvent]


@pytest.mark.parametrize(
    ("forge", "message"),
    [
        (
            lambda event: replace(event, witnesses=("p-2", "p-4")),
            "vent combined witness entitlement",
        ),
        (
            lambda event: replace(event, destination_witnesses=()),
            "vent destination witness entitlement",
        ),
        (
            lambda event: replace(event, source_witnesses=("p-4",)),
            "vent source witness entitlement",
        ),
    ],
)
def test_a_poisoned_physical_exit_is_rejected(forge: _Forgery, message: str) -> None:
    before, after, events = _cross_room_exit("physical")
    exit_event = events[0]
    assert isinstance(exit_event, VentExitedEvent)
    poisoned = [forge(exit_event), *events[1:]]
    with pytest.raises(AssertionError, match=message):
        _check(before, after, poisoned, "physical")


def test_the_physical_expectation_follows_the_maps_vent_room() -> None:
    """Planted map: REACTOR_VENT moved into UPPER_HALL, a room with no vent."""

    reactor = _MAP.vents["REACTOR_VENT"]
    moved = Vent(
        id=reactor.id,
        room="UPPER_HALL",
        connects_to=reactor.connects_to,
        traversal_ticks=reactor.traversal_ticks,
    )
    planted = _MAP.model_copy(update={"vents": {**_MAP.vents, moved.id: moved}})
    before, after, events = _cross_room_exit("physical", game_map=planted)
    exit_event = events[0]
    assert isinstance(exit_event, VentExitedEvent)
    assert exit_event.witnesses == ("p-5",)
    _check(before, after, events, "physical", game_map=planted)
    # The canonical map's REACTOR occupant is no witness on the planted map.
    poisoned = [replace(exit_event, destination_witnesses=("p-4",), witnesses=("p-4",))]
    with pytest.raises(AssertionError, match="vent destination witness entitlement"):
        _check(before, after, [*poisoned, *events[1:]], "physical", game_map=planted)
    # An exit in place through the moved vent is one-room in UPPER_HALL.
    in_place = _scene(
        actor_room="UPPER_HALL",
        actor_in_vent=True,
        bystanders=(_scene_player("p-5", "UPPER_HALL"),),
    )
    surfaced, in_place_events = advance_tick(
        in_place,
        [_vent("REACTOR_VENT")],
        game_map=planted,
        vent_witness_rule="physical",
    )
    _check(in_place, surfaced, in_place_events, "physical", game_map=planted)
    in_place_exit = in_place_events[0]
    assert isinstance(in_place_exit, VentExitedEvent)
    assert in_place_exit.source_witnesses == ("p-5",)
    emptied = [replace(in_place_exit, source_witnesses=()), *in_place_events[1:]]
    with pytest.raises(AssertionError, match="vent source witness entitlement"):
        _check(in_place, surfaced, emptied, "physical", game_map=planted)


@pytest.mark.parametrize("rule", ["PHYSICAL", "both", ""])
def test_an_unknown_rule_raises(rule: str) -> None:
    before, after, events = _cross_room_exit("both_rooms")
    with pytest.raises(ValueError, match="unknown vent witness rule"):
        _check(before, after, events, rule)  # type: ignore[arg-type]


def _imported_modules(module: object) -> set[str]:
    tree = ast.parse(inspect.getsource(module))  # type: ignore[arg-type]
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
        elif isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
    return names


@pytest.mark.parametrize("oracle", [witness_entitlement, temporal_entitlement])
def test_each_oracle_states_the_rule_for_itself(oracle: object) -> None:
    """Independent re-derivations: no engine rule module, the same rule names."""

    imported = _imported_modules(oracle)
    assert not imported & {"engine.rules", "engine.tick", "observation.temporal"}
    assert getattr(oracle, "VENT_WITNESS_RULES") == get_args(VentWitnessRule)


@pytest.mark.parametrize("rule", ["both_rooms", "physical"])
def test_an_entry_and_an_exit_in_place_keep_their_one_room_witnesses(
    rule: VentWitnessRule,
) -> None:
    """p-2 stands in ADMIN under both rules; only an exit elsewhere drops it."""

    for in_vent in (False, True):
        before = _scene(
            actor_room="ADMIN",
            actor_in_vent=in_vent,
            bystanders=(_scene_player("p-2", "ADMIN"), _scene_player("p-4", "REACTOR")),
        )
        after, events = advance_tick(
            before, [_vent("ADMIN_VENT")], game_map=_MAP, vent_witness_rule=rule
        )
        vent = events[0]
        assert vent.type == ("VentExited" if in_vent else "VentEntered")
        _check(before, after, events, rule)
        poisoned = [replace(vent, source_witnesses=(), witnesses=("p-2",)), *events[1:]]
        with pytest.raises(AssertionError, match="vent source witness entitlement"):
            _check(before, after, poisoned, rule)
