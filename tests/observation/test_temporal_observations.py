"""Adverse privacy, audible entitlement and sequential movement controls."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from engine.entities import BodyState, SabotageState
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval.leak_scan import PacketContext, assert_packet_is_leak_clean
from observation.action_intent import ActionIntent
from observation.packet import AudibleEvent
from observation.service import ObservationService
from orchestrator.boundary import translate_action_intent
from tests.observation.test_service import (
    _action,
    _base_world_state,
    _move,
    _movement_world,
    _player,
)


def test_hidden_death_time_cannot_be_recovered_from_public_body_handle(
    tmp_path: Path,
) -> None:
    game_map = load_canonical_map()
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    packets = []
    try:
        for death_tick in (17, 29):
            state = replace(_base_world_state(), tick=death_tick)
            state, _ = advance_tick(
                state,
                [
                    _action(
                        {"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}}
                    )
                ],
                game_map=game_map,
            )
            players = dict(state.players)
            players["p-2"] = _player("p-2", "CREWMATE", "STORAGE", (0.0, 0.0))
            state = replace(state, tick=35, players=players)
            packet = service.build_packet(
                world_state=state, agent_id="p-2", engine_events=()
            )
            assert packet.visible_bodies[0].id == "body-p-1"
            intent: ActionIntent = TypeAdapter(ActionIntent).validate_python(
                {
                    "type": "report",
                    "actor": "p-2",
                    "payload": {"body_id": packet.visible_bodies[0].id},
                }
            )
            translated = translate_action_intent(intent, world_state=state)
            assert translated.type == "report"
            assert translated.payload.body_id == f"body-p-1-{death_tick}"
            assert_packet_is_leak_clean(packet, PacketContext((), state, game_map))
            packets.append(packet)
        assert packets[0] == packets[1]
    finally:
        service.close()


def test_public_handle_selection_preserves_multi_digit_roster_order(
    tmp_path: Path,
) -> None:
    state = _base_world_state()
    bodies = {
        f"body-{victim}-{tick}": BodyState(
            id=f"body-{victim}-{tick}",
            player_id=victim,
            room="STORAGE",
            position=(0.0, 0.0),
            killed_by="p-4",
            discovered_by=None,
        )
        for victim, tick in (("p-1", 92), ("p-10", 3), ("p-2", 8))
    }
    state = replace(state, bodies=bodies)
    service = ObservationService(
        game_map=load_canonical_map(), audit_log_path=tmp_path / "audit"
    )
    try:
        packet = service.build_packet(
            world_state=state, agent_id="p-1", engine_events=()
        )
        public = sorted(body.id for body in packet.visible_bodies)
        translated = []
        for handle in public:
            intent: ActionIntent = TypeAdapter(ActionIntent).validate_python(
                {"type": "report", "actor": "p-1", "payload": {"body_id": handle}}
            )
            action = translate_action_intent(intent, world_state=state)
            assert action.type == "report"
            translated.append(action.payload.body_id)
        assert translated == sorted(bodies)
    finally:
        service.close()


@pytest.mark.parametrize("active", [False, True])
@pytest.mark.parametrize(
    "mutation", ["invented_vent", "wrong_room", "duplicate", "missing"]
)
def test_audible_gate_rejects_unearned_or_missing_cues(
    tmp_path: Path, active: bool, mutation: str
) -> None:
    state = _base_world_state()
    if active:
        state = replace(
            state,
            sabotage=SabotageState(
                kind="lights",
                remaining_ticks=4,
                repair_progress={},
                affected_rooms=(),
                active=True,
            ),
        )
    service = ObservationService(
        game_map=load_canonical_map(), audit_log_path=tmp_path / "audit"
    )
    try:
        packet = service.build_packet(
            world_state=state, agent_id="p-1", engine_events=()
        )
        context = PacketContext((), state, load_canonical_map())
        assert_packet_is_leak_clean(packet, context)
        audio: tuple[AudibleEvent, ...]
        if mutation == "invented_vent":
            audio = (AudibleEvent(kind="vent_use_heard", room="ADMIN"),)
        elif mutation == "wrong_room":
            audio = (AudibleEvent(kind="sabotage_alarm", room="ADMIN"),)
        elif mutation == "duplicate":
            audio = (AudibleEvent(kind="sabotage_alarm", room=None),) * 2
        else:
            audio = () if active else (AudibleEvent(kind="sabotage_alarm", room=None),)
        with pytest.raises(AssertionError, match="audible events"):
            assert_packet_is_leak_clean(
                packet.model_copy(update={"audible_events": audio}), context
            )
    finally:
        service.close()


@pytest.mark.parametrize("observer_moves_first", [False, True])
@pytest.mark.parametrize("observer_action", ["arrive", "leave"])
def test_move_witness_is_bound_to_actual_sequential_departure(
    tmp_path: Path, observer_moves_first: bool, observer_action: str
) -> None:
    game_map = load_canonical_map()
    state = _movement_world()
    # p-5 starts in the destination and arrives at the source either before or
    # after p-2 leaves it. Whole-tick pre/post snapshots cannot distinguish this.
    if observer_action == "leave":
        state = replace(
            state,
            players={
                **state.players,
                "p-5": replace(state.players["p-5"], room="STORAGE"),
            },
        )
    arrival = _move("p-5", "STORAGE" if observer_action == "arrive" else "ENGINEERING")
    departure = _move("p-2", "ENGINEERING")
    actions = [arrival, departure] if observer_moves_first else [departure, arrival]
    state, events = advance_tick(state, actions, game_map=game_map)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit", temporal_observations=True
    )
    try:
        batch = service.build_event_observations(
            world_state=state, agent_id="p-5", engine_events=events
        )
        moves = () if batch is None else batch.moved_players
        assert [move.id for move in moves] == (
            ["p-2"] if observer_moves_first == (observer_action == "arrive") else []
        )
        packet = service.build_packet(
            world_state=state, agent_id="p-5", engine_events=events
        )
        assert packet.moved_players == ()
        assert all(
            player.action not in ("kill", "vent") for player in packet.visible_players
        )
    finally:
        service.close()


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_action",
        "invented_action",
        "wrong_action_room",
        "duplicate_action",
        "invented_move",
        "own_kill",
        "team",
        "tick",
    ],
)
def test_event_gate_rejects_forged_or_missing_entitlement(
    tmp_path: Path, mutation: str
) -> None:
    from engine.events import KilledEvent
    from eval.leak_scan import assert_event_observations_are_entitled
    from observation.packet import MovedPlayerView, OwnKillView, PlayerView

    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["p-2"] = _player("p-2", "CREWMATE", "STORAGE", (0.0, 0.0))
    state = replace(state, players=players)
    state, events = advance_tick(
        state,
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )
    assert any(
        isinstance(event, KilledEvent) and "p-2" in event.witnesses for event in events
    )
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit", temporal_observations=True
    )
    try:
        batch = service.build_event_observations(
            world_state=state, agent_id="p-2", engine_events=events
        )
        assert batch is not None
        context = PacketContext(events, state, game_map, temporal_observations=True)
        assert_event_observations_are_entitled(batch, context)
        with pytest.raises(AssertionError, match="was not delivered"):
            assert_event_observations_are_entitled(None, context, agent_id="p-2")
        if mutation == "missing_action":
            forged = batch.model_copy(update={"witnessed_actions": ()})
        elif mutation == "invented_action":
            forged = batch.model_copy(
                update={
                    "witnessed_actions": (
                        PlayerView(id="p-3", room="STORAGE", action="kill"),
                    )
                }
            )
        elif mutation == "wrong_action_room":
            forged = batch.model_copy(
                update={
                    "witnessed_actions": (
                        PlayerView(id="p-4", room="ADMIN", action="kill"),
                    )
                }
            )
        elif mutation == "duplicate_action":
            forged = batch.model_copy(
                update={"witnessed_actions": batch.witnessed_actions * 2}
            )
        elif mutation == "invented_move":
            forged = batch.model_copy(
                update={
                    "moved_players": (
                        MovedPlayerView(id="p-3", from_room="ADMIN", to_room="STORAGE"),
                    )
                }
            )
        elif mutation == "own_kill":
            forged = batch.model_copy(
                update={"own_kill": OwnKillView(victim_id="p-1", room="STORAGE")}
            )
        elif mutation == "team":
            forged = batch.model_copy(update={"fellow_impostor_ids": ("p-4",)})
        else:
            forged = batch.model_copy(update={"tick": batch.tick + 1})
        with pytest.raises(AssertionError):
            assert_event_observations_are_entitled(forged, context)
    finally:
        service.close()


@pytest.mark.parametrize(
    "channel", ["witnessed_actions", "moved_players", "fellow_impostor_ids"]
)
def test_batch_schema_rejects_duplicate_delivery_identity(channel: str) -> None:
    from observation.packet import EventObservationBatch, MovedPlayerView, PlayerView

    data = {
        "witnessed_actions": [PlayerView(id="p-2", room="ADMIN", action="vent")] * 2,
        "moved_players": [
            MovedPlayerView(id="p-2", from_room="ADMIN", to_room="STORAGE")
        ]
        * 2,
        "fellow_impostor_ids": ["p-2"] * 2,
    }
    with pytest.raises(ValueError, match="duplicate"):
        EventObservationBatch.model_validate(
            {"tick": 0, "agent_id": "p-1", channel: data[channel]}
        )


@pytest.mark.parametrize("handle", ["body-p-1", "body-p-1-0", "body-unknown"])
def test_public_and_legacy_reports_preserve_engine_legality(
    tmp_path: Path, handle: str
) -> None:
    from engine.events import ActionRejectedEvent, MeetingTriggeredEvent

    game_map = load_canonical_map()
    state, _ = advance_tick(
        _base_world_state(),
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )
    players = dict(state.players)
    players["p-2"] = _player("p-2", "CREWMATE", "STORAGE", (0.0, 0.0))
    state = replace(state, players=players)
    intent: ActionIntent = TypeAdapter(ActionIntent).validate_python(
        {"type": "report", "actor": "p-2", "payload": {"body_id": handle}}
    )
    action = translate_action_intent(intent, world_state=state)
    post, events = advance_tick(state, [action], game_map=game_map)
    if handle == "body-unknown":
        assert any(
            isinstance(event, ActionRejectedEvent) and event.action == "report"
            for event in events
        )
        assert not any(isinstance(event, MeetingTriggeredEvent) for event in events)
    else:
        assert any(isinstance(event, MeetingTriggeredEvent) for event in events)
        service = ObservationService(
            game_map=game_map, audit_log_path=tmp_path / "audit"
        )
        try:
            assert (
                service.build_packet(
                    world_state=post, agent_id="p-2", engine_events=events
                ).visible_bodies
                == ()
            )
        finally:
            service.close()
        from meetings.schemas import MeetingResult, MeetingTranscript
        from orchestrator.game import apply_meeting_result

        resumed, _ = apply_meeting_result(
            post,
            MeetingResult(
                meeting_id="test-meeting",
                triggered_by="p-2",
                trigger_tick=state.tick,
                outcome="SKIPPED",
                ejected_player_id=None,
                transcript=MeetingTranscript(),
                ballots=(),
            ),
            game_map=game_map,
            triggering_body_id="body-p-1-0",
        )
        repeated, repeat_events = advance_tick(
            resumed,
            [translate_action_intent(intent, world_state=resumed)],
            game_map=game_map,
        )
        assert repeated.phase != "MEETING"
        assert any(
            isinstance(event, ActionRejectedEvent) and event.action == "report"
            for event in repeat_events
        )


def test_explicit_legacy_projection_remains_readable(tmp_path: Path) -> None:
    state, events = advance_tick(
        _base_world_state(),
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=load_canonical_map(),
    )
    service = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "audit",
        legacy_body_ids=True,
    )
    try:
        packet = service.build_packet(
            world_state=state, agent_id="p-4", engine_events=events
        )
        assert [body.id for body in packet.visible_bodies] == ["body-p-1-0"]
        assert_packet_is_leak_clean(
            packet,
            PacketContext(events, state, load_canonical_map(), legacy_body_ids=True),
        )
        with pytest.raises(AssertionError):
            assert_packet_is_leak_clean(
                packet, PacketContext(events, state, load_canonical_map())
            )
    finally:
        service.close()
