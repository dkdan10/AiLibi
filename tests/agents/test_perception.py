from __future__ import annotations

from typing import get_args

import pytest

import agents.perception
from agents.memory.episodic import MemoryStore
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_GLOBAL_STATUS,
    EVENT_HEARD_SABOTAGE_ALARM,
    EVENT_HEARD_VENT_USE,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_INFERRED,
    PROVENANCE_OBSERVED,
    ingest_packet,
)
from agents.runtime import AgentRuntime
from observation.packet import (
    AudibleEvent,
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView


def _public_map() -> PublicMapView:
    return PublicMapView(
        map_id="canonical_1",
        room_ids=("ADMIN", "CAFETERIA", "ELECTRICAL"),
        room_neighbors={
            "ADMIN": ("CAFETERIA",),
            "CAFETERIA": ("ADMIN", "ELECTRICAL"),
            "ELECTRICAL": ("CAFETERIA",),
        },
        vent_graph={},
        vent_rooms={},
        task_locations={"swipe_card": "ADMIN"},
        spawn_room="CAFETERIA",
        meeting_room="CAFETERIA",
        emergency_button_room="CAFETERIA",
    )


def _global_view(
    *,
    tasks_completed: int = 1,
    tasks_total: int = 4,
    sabotage_active: bool = False,
    sabotage_kind: str | None = None,
) -> GlobalView:
    return GlobalView(
        tasks_completed=tasks_completed,
        tasks_total=tasks_total,
        task_completion_percent=tasks_completed / tasks_total,
        sabotage_active=sabotage_active,
        sabotage_kind=sabotage_kind,
    )


def _packet(
    *,
    tick: int = 12,
    agent_id: str = "p1",
    role: str = "CREWMATE",
    room: str = "CAFETERIA",
    pending_task_id: str | None = "swipe_card",
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
    audible_events: tuple[AudibleEvent, ...] = (),
    global_state: GlobalView | None = None,
    cooldown: int | None = None,
) -> ObservationPacket:
    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,  # type: ignore[arg-type]
            pending_task_id=pending_task_id,
        ),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=audible_events,
        global_state=global_state if global_state is not None else _global_view(),
        cooldown=cooldown,
    )


class TestIngestPacketSelfAndGlobal:
    def test_minimal_packet_writes_self_state_and_global_status(self) -> None:
        store = MemoryStore()

        ingest_packet(packet=_packet(), memory=store)

        events = store.recent(since_tick=0)
        types = tuple(e.type for e in events)
        assert types == (EVENT_SELF_STATE, EVENT_GLOBAL_STATUS)

    def test_self_state_payload_carries_room_role_and_task(self) -> None:
        store = MemoryStore()

        ingest_packet(
            packet=_packet(room="ADMIN", role="IMPOSTOR", pending_task_id=None),
            memory=store,
        )

        self_event = store.recent(since_tick=0)[0]
        assert self_event.type == EVENT_SELF_STATE
        assert self_event.provenance == PROVENANCE_OBSERVED
        assert self_event.payload == {
            "room": "ADMIN",
            "role": "IMPOSTOR",
            "pending_task_id": None,
        }

    def test_global_status_provenance_is_inferred(self) -> None:
        store = MemoryStore()

        ingest_packet(
            packet=_packet(
                global_state=_global_view(
                    tasks_completed=2,
                    tasks_total=5,
                    sabotage_active=True,
                    sabotage_kind="reactor",
                ),
            ),
            memory=store,
        )

        global_event = store.recent(since_tick=0)[-1]
        assert global_event.type == EVENT_GLOBAL_STATUS
        assert global_event.provenance == PROVENANCE_INFERRED
        assert global_event.payload == {
            "tasks_completed": 2,
            "tasks_total": 5,
            "task_completion_percent": pytest.approx(0.4),
            "sabotage_active": True,
            "sabotage_kind": "reactor",
        }

    def test_every_event_uses_packet_tick(self) -> None:
        store = MemoryStore()

        ingest_packet(
            packet=_packet(
                tick=42,
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
                visible_bodies=(
                    BodyView(id="p3-body", room="ELECTRICAL", victim_id="p3"),
                ),
                audible_events=(AudibleEvent(kind="sabotage_alarm"),),
                cooldown=4,
            ),
            memory=store,
        )

        ticks = tuple(e.tick for e in store.recent(since_tick=0))
        assert ticks == (42,) * len(ticks)


class TestIngestPacketCooldown:
    def test_cooldown_present_emits_observed_cooldown_event(self) -> None:
        store = MemoryStore()

        ingest_packet(packet=_packet(role="IMPOSTOR", cooldown=7), memory=store)

        cooldown_events = [
            e for e in store.recent(since_tick=0) if e.type == EVENT_COOLDOWN_STATUS
        ]
        assert len(cooldown_events) == 1
        assert cooldown_events[0].provenance == PROVENANCE_OBSERVED
        assert cooldown_events[0].payload == {"cooldown": 7}

    def test_cooldown_zero_still_emits_event(self) -> None:
        store = MemoryStore()

        ingest_packet(packet=_packet(role="IMPOSTOR", cooldown=0), memory=store)

        cooldown_events = [
            e for e in store.recent(since_tick=0) if e.type == EVENT_COOLDOWN_STATUS
        ]
        assert len(cooldown_events) == 1
        assert cooldown_events[0].payload == {"cooldown": 0}

    def test_cooldown_none_skips_cooldown_event(self) -> None:
        store = MemoryStore()

        ingest_packet(packet=_packet(cooldown=None), memory=store)

        types = tuple(e.type for e in store.recent(since_tick=0))
        assert EVENT_COOLDOWN_STATUS not in types


class TestIngestPacketSightings:
    def test_one_saw_player_event_per_visible_player_in_packet_order(self) -> None:
        store = MemoryStore()
        visible = (
            PlayerView(id="p2", room="ADMIN", action="task"),
            PlayerView(id="p4", room="ELECTRICAL", action=None),
        )

        ingest_packet(packet=_packet(visible_players=visible), memory=store)

        saw_events = [
            e for e in store.recent(since_tick=0) if e.type == EVENT_SAW_PLAYER
        ]
        assert len(saw_events) == 2
        assert saw_events[0].payload == {
            "player_id": "p2",
            "room": "ADMIN",
            "action": "task",
        }
        assert saw_events[1].payload == {
            "player_id": "p4",
            "room": "ELECTRICAL",
            "action": None,
        }
        assert {e.provenance for e in saw_events} == {PROVENANCE_OBSERVED}

    def test_one_saw_body_event_per_visible_body_in_packet_order(self) -> None:
        store = MemoryStore()
        bodies = (
            BodyView(id="p3-body", room="ELECTRICAL", victim_id="p3"),
            BodyView(id="p5-body", room="MEDBAY", victim_id="p5"),
        )

        ingest_packet(packet=_packet(visible_bodies=bodies), memory=store)

        body_events = [
            e for e in store.recent(since_tick=0) if e.type == EVENT_SAW_BODY
        ]
        assert len(body_events) == 2
        assert body_events[0].payload == {
            "body_id": "p3-body",
            "room": "ELECTRICAL",
            "victim_id": "p3",
        }
        assert body_events[1].payload == {
            "body_id": "p5-body",
            "room": "MEDBAY",
            "victim_id": "p5",
        }
        assert {e.provenance for e in body_events} == {PROVENANCE_OBSERVED}

    def test_saw_body_payload_carries_victim_id_from_body_view(self) -> None:
        # R-4: ``BodyView.victim_id`` is the authoritative source for the
        # body's victim player id; perception surfaces it on the
        # ``saw_body`` event payload so downstream agent code (e.g.
        # ``impostor_policy._confirmed_dead_from_bodies``) reads it
        # without parsing the body-id string.
        store = MemoryStore()
        body = BodyView(id="body-p7-42", room="ELECTRICAL", victim_id="p7")

        ingest_packet(packet=_packet(visible_bodies=(body,)), memory=store)

        body_event = next(
            e for e in store.recent(since_tick=0) if e.type == EVENT_SAW_BODY
        )
        assert body_event.payload["victim_id"] == body.victim_id
        assert body_event.payload["victim_id"] == "p7"

    def test_no_saw_events_when_nothing_visible(self) -> None:
        store = MemoryStore()

        ingest_packet(packet=_packet(), memory=store)

        types = {e.type for e in store.recent(since_tick=0)}
        assert EVENT_SAW_PLAYER not in types
        assert EVENT_SAW_BODY not in types


class TestIngestPacketAudibles:
    def test_vent_use_audible_becomes_heard_vent_use_event(self) -> None:
        store = MemoryStore()

        ingest_packet(
            packet=_packet(
                audible_events=(AudibleEvent(kind="vent_use_heard", room="ADMIN"),),
            ),
            memory=store,
        )

        heard = [
            e for e in store.recent(since_tick=0) if e.type == EVENT_HEARD_VENT_USE
        ]
        assert len(heard) == 1
        assert heard[0].provenance == PROVENANCE_OBSERVED
        assert heard[0].payload == {"kind": "vent_use_heard", "room": "ADMIN"}

    def test_sabotage_alarm_audible_becomes_heard_sabotage_alarm_event(self) -> None:
        store = MemoryStore()

        ingest_packet(
            packet=_packet(audible_events=(AudibleEvent(kind="sabotage_alarm"),)),
            memory=store,
        )

        heard = [
            e
            for e in store.recent(since_tick=0)
            if e.type == EVENT_HEARD_SABOTAGE_ALARM
        ]
        assert len(heard) == 1
        assert heard[0].provenance == PROVENANCE_OBSERVED
        assert heard[0].payload == {"kind": "sabotage_alarm", "room": None}

    def test_multiple_audibles_preserve_packet_order(self) -> None:
        store = MemoryStore()

        ingest_packet(
            packet=_packet(
                audible_events=(
                    AudibleEvent(kind="vent_use_heard", room="STORAGE"),
                    AudibleEvent(kind="sabotage_alarm"),
                    AudibleEvent(kind="vent_use_heard", room="MEDBAY"),
                ),
            ),
            memory=store,
        )

        audible_types = [
            e.type
            for e in store.recent(since_tick=0)
            if e.type in {EVENT_HEARD_VENT_USE, EVENT_HEARD_SABOTAGE_ALARM}
        ]
        assert audible_types == [
            EVENT_HEARD_VENT_USE,
            EVENT_HEARD_SABOTAGE_ALARM,
            EVENT_HEARD_VENT_USE,
        ]


class TestIngestPacketAppendOrder:
    def test_full_packet_appends_events_in_canonical_order(self) -> None:
        store = MemoryStore()

        ingest_packet(
            packet=_packet(
                role="IMPOSTOR",
                cooldown=3,
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
                visible_bodies=(
                    BodyView(id="p4-body", room="ELECTRICAL", victim_id="p4"),
                ),
                audible_events=(AudibleEvent(kind="sabotage_alarm"),),
            ),
            memory=store,
        )

        types = tuple(e.type for e in store.recent(since_tick=0))
        assert types == (
            EVENT_SELF_STATE,
            EVENT_COOLDOWN_STATUS,
            EVENT_SAW_PLAYER,
            EVENT_SAW_BODY,
            EVENT_HEARD_SABOTAGE_ALARM,
            EVENT_GLOBAL_STATUS,
        )

    def test_repeated_ingest_across_ticks_is_monotonic(self) -> None:
        store = MemoryStore()

        ingest_packet(packet=_packet(tick=1), memory=store)
        ingest_packet(packet=_packet(tick=2), memory=store)
        ingest_packet(packet=_packet(tick=2), memory=store)

        ticks = tuple(e.tick for e in store.recent(since_tick=0))
        assert ticks == tuple(sorted(ticks))


class TestRuntimeIntegration:
    def test_runtime_with_memory_writes_perception_events_into_store(self) -> None:
        store = MemoryStore()
        runtime = AgentRuntime(agent_id="p1", memory=store)
        packet = _packet(
            agent_id="p1",
            visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
            visible_bodies=(BodyView(id="p3-body", room="ELECTRICAL", victim_id="p3"),),
            audible_events=(AudibleEvent(kind="sabotage_alarm"),),
            cooldown=2,
            role="IMPOSTOR",
        )

        runtime.decide(packet, _public_map())

        types = tuple(e.type for e in store.recent(since_tick=0))
        assert types == (
            EVENT_SELF_STATE,
            EVENT_COOLDOWN_STATUS,
            EVENT_SAW_PLAYER,
            EVENT_SAW_BODY,
            EVENT_HEARD_SABOTAGE_ALARM,
            EVENT_GLOBAL_STATUS,
        )

    def test_runtime_without_memory_writes_nothing(self) -> None:
        runtime = AgentRuntime(agent_id="p1")

        runtime.decide(_packet(agent_id="p1"), _public_map())

        assert runtime.memory is None

    def test_runtime_exposes_memory_property(self) -> None:
        store = MemoryStore()
        runtime = AgentRuntime(agent_id="p1", memory=store)

        assert runtime.memory is store


class TestAudibleEventEnumCoupling:
    def test_audible_event_types_cover_every_audible_event_kind(self) -> None:
        # AudibleEvent.model_fields["kind"].annotation is the Literal alias.
        # If a new kind is added to AudibleEvent without an accompanying entry
        # in _AUDIBLE_EVENT_TYPES, perception would raise at runtime; this
        # test fails earlier (at import + assertion time) instead.
        expected_kinds = set(get_args(AudibleEvent.model_fields["kind"].annotation))

        assert set(agents.perception._AUDIBLE_EVENT_TYPES) == expected_kinds
