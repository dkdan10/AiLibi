"""Ordered v2 evidence and planted semantic failures, with explicit v1 controls."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any, cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import observation.temporal as temporal_module
from agents.memory.store import AgentMemory, render_for_prompt
from agents.perception import ingest_event_observations, ingest_packet
from engine.actions import Action
from engine.events import EngineEvent, VentExitedEvent
from engine.tick import VentWitnessRule, advance_tick
from engine.world import WorldState, load_canonical_map
from eval.temporal_entitlement import assert_temporal_batch_entitled
from observation.packet import (
    EventObservationBatch,
    OwnTaskAttemptEvent,
    OwnTransitionEvent,
    WitnessedActionEvent,
    WitnessedMoveEvent,
)
from observation.service import ObservationService
from observation.version import temporal_observation_version
from observation.temporal import project_temporal_events
from tests.engine.test_vent_witness_rule import _player as _scene_player
from tests.engine.test_vent_witness_rule import _scene, _vent, _vent_scenes
from tests.observation.test_service import (
    _action,
    _base_world_state,
    _move,
    _movement_world,
    _player,
)


@pytest.mark.parametrize("value", [True, 2.0, "2", 0, 3])
def test_packet_version_rejects_coercion_and_unknown_values(value: Any) -> None:
    with pytest.raises(ValueError):
        EventObservationBatch.model_validate(
            {"agent_id": "p-1", "tick": 0, "temporal_observation_version": value}
        )


def test_explicit_version_selection_and_legacy_bytes(tmp_path: Path) -> None:
    assert temporal_observation_version({}) is None
    assert temporal_observation_version({"AILIBI_TEMPORAL_OBSERVATIONS": "true"}) == 1
    assert temporal_observation_version({"AILIBI_TEMPORAL_OBSERVATIONS": "2"}) == 2
    with pytest.raises(ValueError):
        temporal_observation_version({"AILIBI_TEMPORAL_OBSERVATIONS": "3"})
    with pytest.raises(ValueError, match="conflicting"):
        ObservationService(
            game_map=load_canonical_map(),
            audit_log_path=tmp_path / "audit",
            temporal_observations=False,
            temporal_observation_version=2,
        )
    service = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "audit",
        temporal_observations=True,
        temporal_observation_version=2,
    )
    with pytest.raises(ValueError, match="source_state"):
        service.build_event_observations(
            world_state=_base_world_state(), agent_id="p-1", engine_events=()
        )
    legacy = EventObservationBatch(tick=0, agent_id="p-1")
    assert (
        legacy.model_dump_json()
        == '{"kind":"event_observations","tick":0,"agent_id":"p-1","own_kill":null,"witnessed_actions":[],"moved_players":[],"fellow_impostor_ids":[]}'
    )
    service.close()


@pytest.mark.parametrize("observer_first", [False, True])
def test_event_position_order_preserves_both_crossing_outcomes(
    tmp_path: Path, observer_first: bool
) -> None:
    before = _movement_world()
    game_map = load_canonical_map()
    arrival, departure = _move("p-5", "STORAGE"), _move("p-2", "ENGINEERING")
    actions = [arrival, departure] if observer_first else [departure, arrival]
    after, events = advance_tick(before, actions, game_map=game_map)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        memory = AgentMemory(evidence_reasoning_version=2)
        ingest_packet(
            packet=service.build_packet(
                world_state=before, agent_id="p-5", engine_events=()
            ),
            memory=memory.episodic,
        )
        batch = service.build_event_observations(
            world_state=after,
            source_state=before,
            submitted_actions=actions,
            engine_events=events,
            agent_id="p-5",
        )
        assert batch is not None
        assert_temporal_batch_entitled(
            batch,
            agent_id="p-5",
            source_state=before,
            state=after,
            events=events,
            submitted_actions=actions,
            game_map=game_map,
            vent_witness_rule="both_rooms",
        )
        moves = [
            row
            for row in batch.ordered_events
            if isinstance(row.event, WitnessedMoveEvent)
        ]
        assert bool(moves) is observer_first
        assert isinstance(batch.ordered_events[0].event, OwnTransitionEvent)
        if observer_first:
            assert moves[0].observer_before_event.room == "STORAGE"
            assert moves[0].observation_order == 1
        ingest_event_observations(
            batch=batch, memory=memory.episodic, beliefs=memory.beliefs
        )
        assert (
            ingest_event_observations(
                batch=batch, memory=memory.episodic, beliefs=memory.beliefs
            )
            == ()
        )
        text = render_for_prompt(memory, token_budget=5000)
        assert "START of each tick" in text
        assert "immediately before this event" in text
        assert "during tick 0" in text
    finally:
        service.close()


@pytest.mark.parametrize(
    "mutation", ["missing", "extra", "endpoint", "order", "observer", "source_tick"]
)
def test_independent_oracle_rejects_planted_temporal_defects(
    tmp_path: Path, mutation: str
) -> None:
    source = _movement_world()
    game_map = load_canonical_map()
    actions = [_move("p-5", "STORAGE"), _move("p-2", "ENGINEERING")]
    state, events = advance_tick(source, actions, game_map=game_map)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        batch = service.build_event_observations(
            world_state=state,
            source_state=source,
            submitted_actions=actions,
            engine_events=events,
            agent_id="p-5",
        )
        assert batch is not None
        rows = list(batch.ordered_events)
        if mutation == "missing":
            rows.pop()
        elif mutation == "extra":
            rows.append(rows[-1])
        elif mutation == "endpoint":
            movement = rows[-1].event
            assert isinstance(movement, WitnessedMoveEvent)
            rows[-1] = rows[-1].model_copy(
                update={
                    "event": movement.model_copy(
                        update={
                            "movement": movement.movement.model_copy(
                                update={"to_room": "ADMIN"}
                            )
                        }
                    )
                }
            )
        elif mutation == "order":
            rows.reverse()
        elif mutation == "observer":
            rows[-1] = rows[-1].model_copy(
                update={
                    "observer_before_event": rows[-1].observer_before_event.model_copy(
                        update={"room": "ADMIN"}
                    )
                }
            )
        forged = batch.model_copy(
            update={
                "ordered_events": tuple(rows),
                "tick": 1 if mutation == "source_tick" else batch.tick,
            }
        )
        with pytest.raises(AssertionError):
            assert_temporal_batch_entitled(
                forged,
                agent_id="p-5",
                source_state=source,
                state=state,
                events=events,
                submitted_actions=actions,
                game_map=game_map,
                vent_witness_rule="both_rooms",
            )
    finally:
        service.close()


def test_v2_entitlement_ignores_forged_legacy_witness_metadata(tmp_path: Path) -> None:
    from engine.events import MovedEvent

    source = _movement_world()
    game_map = load_canonical_map()
    actions = [_move("p-2", "ENGINEERING")]
    state, events = advance_tick(source, actions, game_map=game_map)
    forged = [
        replace(event, witnesses=("p-5",)) if isinstance(event, MovedEvent) else event
        for event in events
    ]
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        assert (
            service.build_event_observations(
                world_state=state,
                source_state=source,
                submitted_actions=actions,
                engine_events=forged,
                agent_id="p-5",
            )
            is None
        )
    finally:
        service.close()


def test_actor_task_rejection_is_private_and_never_completion(tmp_path: Path) -> None:
    source = _base_world_state()
    source = replace(
        source,
        players={
            **source.players,
            "p-2": _player("p-2", "CREWMATE", "STORAGE", (0.0, 0.0)),
        },
    )
    game_map = load_canonical_map()
    actions = [
        _action(
            {"actor": "p-4", "type": "do_task", "payload": {"task_id": "upload_logs"}}
        )
    ]
    state, events = advance_tick(source, actions, game_map=game_map)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        for recipient in ("p-4", "p-2"):
            batch = service.build_event_observations(
                world_state=state,
                source_state=source,
                submitted_actions=actions,
                engine_events=events,
                agent_id=recipient,
            )
            assert batch is not None
            assert_temporal_batch_entitled(
                batch,
                agent_id=recipient,
                source_state=source,
                state=state,
                events=events,
                submitted_actions=actions,
                game_map=game_map,
                vent_witness_rule="both_rooms",
            )
            payload = batch.ordered_events[0].event
            if recipient == "p-4":
                assert isinstance(payload, OwnTaskAttemptEvent)
                assert payload.attempt.outcome == "rejected"
            else:
                assert isinstance(payload, WitnessedActionEvent)
                assert payload.player.action == "task"
                assert "rejected" not in batch.model_dump_json()
                assert "upload_logs" not in batch.model_dump_json()
    finally:
        service.close()


@pytest.mark.parametrize("witnesses", [(), ("p-5",), None])
def test_engine_movement_metadata_is_checked_independently(
    witnesses: tuple[str, ...] | None,
) -> None:
    from engine.events import MovedEvent
    from eval.witness_entitlement import assert_event_witnesses_match_source_state

    source = _movement_world()
    game_map = load_canonical_map()
    state, events = advance_tick(
        source, [_move("p-2", "ENGINEERING")], game_map=game_map
    )
    assert_event_witnesses_match_source_state(
        pre_state=source,
        state=state,
        events=events,
        game_map=game_map,
        vent_witness_rule="both_rooms",
    )
    forged = [
        replace(event, witnesses=witnesses) if isinstance(event, MovedEvent) else event
        for event in events
    ]
    with pytest.raises(AssertionError, match="movement witness"):
        assert_event_witnesses_match_source_state(
            pre_state=source,
            state=state,
            events=forged,
            game_map=game_map,
            vent_witness_rule="both_rooms",
        )


def test_witness_remembers_before_death_but_receives_nothing_after(
    tmp_path: Path,
) -> None:
    source = _base_world_state()
    source = replace(
        source,
        players={
            **source.players,
            "p-2": _player("p-2", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "p-3": _player("p-3", "IMPOSTOR", "STORAGE", (0.0, 0.0)),
        },
        cooldowns={"p-3": 0, "p-4": 0},
    )
    game_map = load_canonical_map()
    actions = [
        _action({"actor": "p-4", "type": "kill", "payload": {"target": "p-1"}}),
        _action({"actor": "p-3", "type": "kill", "payload": {"target": "p-2"}}),
        _action(
            {"actor": "p-2", "type": "do_task", "payload": {"task_id": "upload_logs"}}
        ),
    ]
    state, events = advance_tick(source, actions, game_map=game_map)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        batch = service.build_event_observations(
            world_state=state,
            source_state=source,
            submitted_actions=actions,
            engine_events=events,
            agent_id="p-2",
        )
        assert batch is not None
        assert_temporal_batch_entitled(
            batch,
            agent_id="p-2",
            source_state=source,
            state=state,
            events=events,
            submitted_actions=actions,
            game_map=game_map,
            vent_witness_rule="both_rooms",
        )
        assert len(batch.ordered_events) == 1
        witnessed = batch.ordered_events[0].event
        assert isinstance(witnessed, WitnessedActionEvent)
        assert witnessed.player.id == "p-4" and witnessed.player.action == "kill"
    finally:
        service.close()


def test_hidden_actions_do_not_change_local_order_or_source_identity(
    tmp_path: Path,
) -> None:
    source = _movement_world()
    game_map = load_canonical_map()
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        outputs = []
        for hidden_wait in (False, True):
            actions = (
                [_action({"actor": "p-1", "type": "wait", "payload": {}})]
                if hidden_wait
                else []
            ) + [_move("p-5", "STORAGE"), _move("p-2", "ENGINEERING")]
            state, events = advance_tick(source, actions, game_map=game_map)
            batch = service.build_event_observations(
                world_state=state,
                source_state=source,
                submitted_actions=actions,
                engine_events=events,
                agent_id="p-5",
            )
            assert batch is not None
            memory = AgentMemory()
            rows = ingest_event_observations(batch=batch, memory=memory.episodic)
            outputs.append(
                (
                    batch.model_dump_json(),
                    [row.payload["source_event_id"] for row in rows],
                )
            )
        assert outputs[0] == outputs[1]
    finally:
        service.close()


def test_real_owned_task_receipts_distinguish_progress_and_completion(
    tmp_path: Path,
) -> None:
    from orchestrator.seeder import seed_initial_state

    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=1, num_players=4, num_impostors=1, tasks_per_crewmate=1, game_map=game_map
    )
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    outcomes = []
    try:
        for tick in range(8):
            source = state
            action = (
                _move("p-2", "EAST_HALL" if tick == 0 else "ADMIN")
                if tick < 2
                else _action(
                    {
                        "actor": "p-2",
                        "type": "do_task",
                        "payload": {"task_id": "upload_logs"},
                    }
                )
            )
            state, events = advance_tick(source, [action], game_map=game_map)
            batch = service.build_event_observations(
                world_state=state,
                source_state=source,
                submitted_actions=[action],
                engine_events=events,
                agent_id="p-2",
            )
            assert batch is not None
            assert_temporal_batch_entitled(
                batch,
                agent_id="p-2",
                source_state=source,
                state=state,
                events=events,
                submitted_actions=[action],
                game_map=game_map,
                vent_witness_rule="both_rooms",
            )
            if tick == 2:
                passive_state, passive_events = advance_tick(
                    state, [], game_map=game_map
                )
                assert (
                    service.build_event_observations(
                        world_state=passive_state,
                        source_state=state,
                        submitted_actions=[],
                        engine_events=passive_events,
                        agent_id="p-2",
                    )
                    is None
                )
            payload = batch.ordered_events[0].event
            if isinstance(payload, OwnTaskAttemptEvent):
                outcomes.append(payload.attempt.outcome)
        assert outcomes == ["progressed"] * 5 + ["completed"]
        # No submitted action means this transport must not invent a new attempt.
        source = state
        state, events = advance_tick(source, [], game_map=game_map)
        assert (
            service.build_event_observations(
                world_state=state,
                source_state=source,
                submitted_actions=[],
                engine_events=events,
                agent_id="p-2",
            )
            is None
        )
    finally:
        service.close()


@pytest.mark.parametrize("mutation", ["version", "tick", "task", "position"])
def test_snapshot_gate_rejects_version_clock_or_invented_action(
    tmp_path: Path, mutation: str
) -> None:
    from eval.leak_scan import PacketContext, assert_packet_is_leak_clean
    from orchestrator.seeder import seed_initial_state

    game_map = load_canonical_map()
    source = seed_initial_state(
        seed=1, num_players=4, num_impostors=1, tasks_per_crewmate=1, game_map=game_map
    )
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        packet = service.build_packet(
            world_state=source, agent_id="p-2", engine_events=()
        )
        context = PacketContext(
            (),
            source,
            game_map,
            temporal_observations=True,
            temporal_observation_version=2,
        )
        assert_packet_is_leak_clean(packet, context)
        if mutation == "version":
            forged = packet.model_copy(update={"temporal_observation_version": None})
        elif mutation == "tick":
            forged = packet.model_copy(update={"tick": 777})
        elif mutation == "task":
            forged = packet.model_copy(
                update={
                    "visible_players": (
                        packet.visible_players[0].model_copy(update={"action": "task"}),
                        *packet.visible_players[1:],
                    )
                }
            )
        else:
            forged = packet.model_copy(
                update={
                    "self_state": packet.self_state.model_copy(update={"room": "ADMIN"})
                }
            )
        with pytest.raises(AssertionError, match="v2"):
            assert_packet_is_leak_clean(forged, context)
    finally:
        service.close()


def _vented_impostor_world(acting: str) -> WorldState:
    """``_movement_world`` with the impostor p-4 hidden in a vent in STORAGE.

    The movers p-1 and p-2 stand in STORAGE with it, so an observer that were
    not entitlement-filtered would resolve everything the room does. For the
    kill case p-1 becomes the second impostor, so the kill happens in the room
    p-4 is hidden under.
    """

    source = _movement_world()
    players = dict(source.players)
    players["p-4"] = replace(players["p-4"], in_vent=True)
    if acting == "kill":
        players["p-1"] = _player("p-1", "IMPOSTOR", "STORAGE", (0.0, 0.0))
    return replace(source, players=players, cooldowns={**source.cooldowns, "p-1": 0})


@pytest.mark.parametrize("acting", ["move", "kill", "task"])
def test_a_vented_observer_perceives_nothing_in_the_room_above_it(
    tmp_path: Path, acting: str
) -> None:
    """A player inside a vent witnesses none of the room it is hidden under.

    The v2 entitlement rule is ``observer.alive and not observer.in_vent``, and
    engine visibility only hides vented SUBJECTS -- a vented observer still
    resolves the players around it. Without the vent term a hiding impostor
    would be handed the movements, kills and task attempts happening above it.
    """

    game_map = load_canonical_map()
    source = _vented_impostor_world(acting)
    if acting == "move":
        actions = [_move("p-2", "ENGINEERING")]
    elif acting == "kill":
        actions = [
            _action({"type": "kill", "actor": "p-1", "payload": {"target": "p-2"}})
        ]
    else:
        actions = [
            _action(
                {
                    "actor": "p-2",
                    "type": "do_task",
                    "payload": {"task_id": "upload_logs"},
                }
            )
        ]
    state, events = advance_tick(source, actions, game_map=game_map)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit",
        temporal_observation_version=2,
    )
    try:
        assert (
            service.build_event_observations(
                world_state=state,
                source_state=source,
                submitted_actions=actions,
                engine_events=events,
                agent_id="p-4",
            )
            is None
        )
        # Control: the same tick reaches an entitled participant standing in
        # STORAGE, so the vented observer's empty batch is the guard, not an
        # empty tick.
        entitled = service.build_event_observations(
            world_state=state,
            source_state=source,
            submitted_actions=actions,
            engine_events=events,
            agent_id="p-1",
        )
        assert entitled is not None
        assert_temporal_batch_entitled(
            entitled,
            agent_id="p-1",
            source_state=source,
            state=state,
            events=events,
            submitted_actions=actions,
            game_map=game_map,
            vent_witness_rule="both_rooms",
        )
    finally:
        service.close()


# --------------------------------------------------------------------------- #
# The vent witness rule: a vent reaches exactly the event's own witnesses     #
# --------------------------------------------------------------------------- #

_MAP = load_canonical_map()


def _cross_room_exit(
    rule: VentWitnessRule,
) -> tuple[WorldState, WorldState, list[Action], list[EngineEvent]]:
    """p-0 exits ADMIN_VENT through REACTOR_VENT.

    p-2 stands in ADMIN, the room left; p-4 in REACTOR, where the impostor
    surfaces; p-5 in UPPER_HALL, which sees neither room.
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
    actions = [_vent("REACTOR_VENT")]
    after, events = advance_tick(before, actions, game_map=_MAP, vent_witness_rule=rule)
    return before, after, actions, events


@pytest.mark.parametrize("rule", ["both_rooms", "physical"])
def test_a_room_left_crewmate_sees_the_exit_only_under_both_rooms(
    tmp_path: Path, rule: VentWitnessRule
) -> None:
    before, after, actions, events = _cross_room_exit(rule)
    room_left_sees = rule == "both_rooms"
    legacy = ObservationService(game_map=_MAP, audit_log_path=tmp_path / "legacy")
    temporal = ObservationService(
        game_map=_MAP,
        audit_log_path=tmp_path / "temporal",
        temporal_observation_version=2,
    )
    try:
        for agent_id, room, sees in (
            ("p-2", "ADMIN", room_left_sees),
            ("p-4", "REACTOR", True),
            ("p-5", "UPPER_HALL", False),
        ):
            packet = legacy.build_packet(
                world_state=after, agent_id=agent_id, engine_events=events
            )
            assert [
                (view.id, view.room)
                for view in packet.visible_players
                if view.action == "vent"
            ] == ([("p-0", room)] if sees else [])
            batch = temporal.build_event_observations(
                world_state=after,
                source_state=before,
                submitted_actions=actions,
                engine_events=events,
                agent_id=agent_id,
            )
            if sees:
                assert batch is not None
                (row,) = batch.ordered_events
                assert isinstance(row.event, WitnessedActionEvent)
                assert (row.event.player.id, row.event.player.room) == ("p-0", room)
                assert row.event.player.action == "vent"
            else:
                assert batch is None
            assert_temporal_batch_entitled(
                batch,
                agent_id=agent_id,
                source_state=before,
                state=after,
                events=events,
                submitted_actions=actions,
                game_map=_MAP,
                vent_witness_rule=rule,
            )
    finally:
        legacy.close()
        temporal.close()


def test_the_temporal_oracle_takes_the_rule_the_events_were_made_under(
    tmp_path: Path,
) -> None:
    service = ObservationService(
        game_map=_MAP, audit_log_path=tmp_path / "audit", temporal_observation_version=2
    )
    try:
        pairs: tuple[tuple[VentWitnessRule, VentWitnessRule], ...] = (
            ("physical", "both_rooms"),
            ("both_rooms", "physical"),
        )
        for rule, other in pairs:
            before, after, actions, events = _cross_room_exit(rule)
            batch = service.build_event_observations(
                world_state=after,
                source_state=before,
                submitted_actions=actions,
                engine_events=events,
                agent_id="p-2",
            )
            assert (batch is None) is (rule == "physical")
            arguments: dict[str, Any] = {
                "agent_id": "p-2",
                "source_state": before,
                "state": after,
                "events": events,
                "submitted_actions": actions,
                "game_map": _MAP,
            }
            assert_temporal_batch_entitled(batch, **arguments, vent_witness_rule=rule)
            # Planted: the oracle handed the other rule rejects the same batch.
            message = (
                "entitled event batch was not delivered"
                if rule == "physical"
                else "empty v2 evidence must not produce a batch"
            )
            with pytest.raises(AssertionError, match=message):
                assert_temporal_batch_entitled(
                    batch, **arguments, vent_witness_rule=other
                )
    finally:
        service.close()


@pytest.mark.parametrize("rule", ["PHYSICAL", "both", ""])
def test_the_temporal_oracle_raises_on_an_unknown_rule(rule: str) -> None:
    before, after, actions, events = _cross_room_exit("both_rooms")
    with pytest.raises(ValueError, match="unknown vent witness rule"):
        assert_temporal_batch_entitled(
            None,
            agent_id="p-5",
            source_state=before,
            state=after,
            events=events,
            submitted_actions=actions,
            game_map=_MAP,
            vent_witness_rule=rule,  # type: ignore[arg-type]
        )


# The vent predicate before the rule existed, kept here as the reference: a
# watching observer standing in either room the event names.
_ROOM_PREDICATE = """            elif can_watch and observer.room in (
                event.source_room,
                event.destination_room,
            ):
"""
# The vent branch, and the clause in it that hands a watching observer the
# vent: located by the branch header and the body it opens, so the reference
# replaces whatever condition the module holds today.
_VENT_BRANCH = "        elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):\n"
_CLAUSE_START = "            elif "
_CLAUSE_BODY = "                perceived = WitnessedActionEvent(\n"

_Projection = Callable[..., EventObservationBatch | None]


def _room_predicate_projection() -> _Projection:
    """``project_temporal_events`` with the old room predicate in place of today's."""

    source = inspect.getsource(temporal_module)
    assert source.count(_VENT_BRANCH) == 1
    start = source.index(_CLAUSE_START, source.index(_VENT_BRANCH))
    end = source.index(_CLAUSE_BODY, start)
    reference = source[:start] + _ROOM_PREDICATE + source[end:]
    namespace: dict[str, object] = {"__name__": "room_predicate_reference"}
    # The module's own source with only the vent clause's condition swapped, so
    # the comparisons below isolate that one condition.
    exec(compile(reference, "<room-predicate reference>", "exec"), namespace)
    return cast(_Projection, namespace["project_temporal_events"])


_REFERENCE = _room_predicate_projection()


def _projections(
    projection: _Projection,
    before: WorldState,
    actions: Sequence[Action],
    events: Sequence[EngineEvent],
) -> dict[str, EventObservationBatch | None]:
    return {
        agent_id: projection(
            source_state=before,
            submitted_actions=actions,
            engine_events=events,
            agent_id=agent_id,
            game_map=_MAP,
        )
        for agent_id in sorted(before.players)
    }


def test_the_room_predicate_would_hand_the_physical_exit_to_the_room_left() -> None:
    """Planted: the old predicate restored fails the physical case above."""

    before, _after, actions, events = _cross_room_exit("physical")
    today = _projections(project_temporal_events, before, actions, events)
    restored = _projections(_REFERENCE, before, actions, events)
    assert today["p-2"] is None
    assert restored["p-2"] is not None
    assert {agent: today[agent] for agent in today if agent != "p-2"} == {
        agent: restored[agent] for agent in restored if agent != "p-2"
    }


@st.composite
def _scenes_with_moves(
    draw: st.DrawFn,
) -> tuple[WorldState, list[Action]]:
    """A vent scene plus bystander moves, in a drawn order around the vent."""

    state, vent_id, _kind = draw(_vent_scenes())
    moves: list[Action] = []
    for player_id, player in sorted(state.players.items()):
        if player_id == "p-0" or not draw(st.booleans()):
            continue
        to_room = draw(st.sampled_from(_MAP.room_neighbors(player.room)))
        moves.append(_move(player_id, to_room))
    position = draw(st.integers(min_value=0, max_value=len(moves)))
    return state, [*moves[:position], _vent(vent_id), *moves[position:]]


@settings(deadline=None, max_examples=200)
@given(_scenes_with_moves())
def test_on_both_rooms_scenes_the_witness_lists_deliver_as_the_room_predicate(
    scene: tuple[WorldState, list[Action]],
) -> None:
    """Byte identity for every temporal recording made under the default rule."""

    before, actions = scene
    _after, events = advance_tick(
        before, actions, game_map=_MAP, vent_witness_rule="both_rooms"
    )
    assert _projections(project_temporal_events, before, actions, events) == (
        _projections(_REFERENCE, before, actions, events)
    )


def test_a_vent_listing_a_vented_or_dead_observer_still_reaches_neither() -> None:
    """Planted metadata: the watch guard stands between the lists and delivery.

    The engine never lists a vented or dead player, so this event is forged:
    it names p-6, hidden in a vent in ADMIN, and p-7, dead in ADMIN, among the
    room-left witnesses.
    """

    before = _scene(
        actor_room="ADMIN",
        actor_in_vent=True,
        bystanders=(
            _scene_player("p-2", "ADMIN"),
            _scene_player("p-6", "ADMIN", role="IMPOSTOR", in_vent=True),
            _scene_player("p-7", "ADMIN", alive=False),
        ),
    )
    actions = [_vent("REACTOR_VENT")]
    _after, events = advance_tick(
        before, actions, game_map=_MAP, vent_witness_rule="both_rooms"
    )
    exit_event = events[0]
    assert isinstance(exit_event, VentExitedEvent)
    assert exit_event.source_witnesses == ("p-2",)
    forged = [
        replace(exit_event, source_witnesses=("p-2", "p-6", "p-7")),
        *events[1:],
    ]
    batches = _projections(project_temporal_events, before, actions, forged)
    assert batches["p-2"] is not None
    assert batches["p-6"] is None and batches["p-7"] is None


def test_the_scan_context_hands_its_rule_to_the_temporal_oracle(
    tmp_path: Path,
) -> None:
    """A context left at its default checks under ``both_rooms``."""

    from eval.leak_scan import PacketContext, assert_event_observations_are_entitled

    service = ObservationService(
        game_map=_MAP, audit_log_path=tmp_path / "audit", temporal_observation_version=2
    )
    try:
        for rule in ("both_rooms", "physical"):
            before, after, actions, events = _cross_room_exit(rule)
            batch = service.build_event_observations(
                world_state=after,
                source_state=before,
                submitted_actions=actions,
                engine_events=events,
                agent_id="p-2",
            )
            context = PacketContext(
                events,
                after,
                _MAP,
                temporal_observations=True,
                temporal_observation_version=2,
                source_state=before,
                submitted_actions=actions,
            )
            if rule == "both_rooms":
                assert context.vent_witness_rule == "both_rooms"
                assert_event_observations_are_entitled(batch, context)
                with pytest.raises(AssertionError):
                    assert_event_observations_are_entitled(
                        batch, replace(context, vent_witness_rule="physical")
                    )
            else:
                with pytest.raises(AssertionError):
                    assert_event_observations_are_entitled(
                        batch, context, agent_id="p-2"
                    )
                assert_event_observations_are_entitled(
                    batch,
                    replace(context, vent_witness_rule="physical"),
                    agent_id="p-2",
                )
    finally:
        service.close()
