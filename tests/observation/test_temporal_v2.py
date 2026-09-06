"""Ordered v2 evidence and planted semantic failures, with explicit v1 controls."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from agents.memory.store import AgentMemory, render_for_prompt
from agents.perception import ingest_event_observations, ingest_packet
from engine.tick import advance_tick
from engine.world import load_canonical_map
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
        pre_state=source, state=state, events=events, game_map=game_map
    )
    forged = [
        replace(event, witnesses=witnesses) if isinstance(event, MovedEvent) else event
        for event in events
    ]
    with pytest.raises(AssertionError, match="movement witness"):
        assert_event_witnesses_match_source_state(
            pre_state=source, state=state, events=forged, game_map=game_map
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
