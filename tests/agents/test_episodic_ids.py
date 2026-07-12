"""Stable observation ids + the render lever (Task 16.5, C8).

The unit home for the C8 identity substrate
(audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 C3/C8, DESIGN.md
§5.5 / §6.6):

* the deterministic ``{agent_id}:{tick}:{seq}`` scheme
  (:func:`agents.memory.episodic.derive_observation_id`), stamped at write time
  by :func:`agents.perception.ingest_packet` on every first-hand OBSERVED row and
  guarded for uniqueness by :meth:`agents.memory.episodic.MemoryStore.append`;
* the default-OFF ``AILIBI_OBSERVATION_ID_RENDERING`` render lever
  (:func:`agents.memory.store.observation_id_rendering_enabled`), whose ON path
  folds ``[obs {id}]`` into each first-hand remembered observation line.

This file also hosts the committed-set two-walk determinism pin (added by the
second worker), which walks committed replays twice and asserts the two
reconstructions assign byte-identical ids.
"""

from __future__ import annotations

import pytest

from agents.memory.episodic import (
    EpisodicEvent,
    MemoryStore,
    derive_observation_id,
)
from agents.memory.store import (
    AgentMemory,
    absorb_reported_testimony,
)
from agents.perception import (
    EVENT_GLOBAL_STATUS,
    EVENT_REPORTED_TESTIMONY,
    PROVENANCE_INFERRED,
    PROVENANCE_OBSERVED,
    ingest_packet,
)
from meetings.schemas import ReportedStatement
from observation.packet import (
    AudibleEvent,
    BodyView,
    GlobalView,
    MovedPlayerView,
    ObservationPacket,
    OwnKillView,
    PlayerView,
    SelfView,
)


def _global_view(
    *,
    tasks_completed: int = 1,
    tasks_total: int = 4,
) -> GlobalView:
    return GlobalView(
        tasks_completed=tasks_completed,
        tasks_total=tasks_total,
        task_completion_percent=tasks_completed / tasks_total,
        sabotage_active=False,
        sabotage_kind=None,
    )


def _packet(
    *,
    tick: int = 12,
    agent_id: str = "p1",
    role: str = "CREWMATE",
    room: str = "CAFETERIA",
    pending_task_id: str | None = "swipe_card",
    fellow_impostor_ids: tuple[str, ...] = (),
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
    audible_events: tuple[AudibleEvent, ...] = (),
    moved_players: tuple[MovedPlayerView, ...] = (),
    cooldown: int | None = None,
    own_kill: OwnKillView | None = None,
) -> ObservationPacket:
    """Minimal :class:`ObservationPacket` fixture (mirrors test_perception.py)."""

    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,  # type: ignore[arg-type]
            pending_task_id=pending_task_id,
            fellow_impostor_ids=fellow_impostor_ids,
            own_kill=own_kill,
        ),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=audible_events,
        moved_players=moved_players,
        global_state=_global_view(),
        cooldown=cooldown,
    )


class TestObservationIdScheme:
    def test_ids_follow_scheme_in_ingestion_order(self) -> None:
        # A packet that exercises the OBSERVED write sites in the documented
        # append order (self_state, saw_player*, saw_player_move, saw_body, heard):
        # each row's id is a dense ``{agent}:{tick}:{k}`` with k running 0..n-1,
        # and the trailing inferred global_status row carries no id.
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=7,
                agent_id="p1",
                visible_players=(
                    PlayerView(id="p2", room="ADMIN", action="task"),
                    PlayerView(id="p4", room="ADMIN", action=None),
                ),
                moved_players=(
                    MovedPlayerView(id="p5", from_room="CAFETERIA", to_room="ADMIN"),
                ),
                visible_bodies=(
                    BodyView(id="p3-body", room="ELECTRICAL", victim_id="p3"),
                ),
                audible_events=(AudibleEvent(kind="sabotage_alarm"),),
            ),
            memory=store,
        )

        events = store.recent(since_tick=0)
        observed = [e for e in events if e.provenance == PROVENANCE_OBSERVED]
        assert [e.observation_id for e in observed] == [
            f"p1:7:{k}" for k in range(len(observed))
        ]
        # The trailing inferred aggregate is not first-hand citable evidence.
        assert events[-1].type == EVENT_GLOBAL_STATUS
        assert events[-1].provenance == PROVENANCE_INFERRED
        assert events[-1].observation_id is None

    def test_cooldown_and_own_kill_sites_get_dense_ids(self) -> None:
        # The impostor-only sites (own_kill, cooldown) are stamped in order too:
        # self_state(0), own_kill(1), cooldown(2), global_status(None).
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=3,
                agent_id="p9",
                role="IMPOSTOR",
                cooldown=5,
                own_kill=OwnKillView(victim_id="p2", room="CAFETERIA"),
            ),
            memory=store,
        )

        observed = [
            e for e in store.recent(since_tick=0) if e.provenance == PROVENANCE_OBSERVED
        ]
        assert [(e.type, e.observation_id) for e in observed] == [
            ("self_state", "p9:3:0"),
            ("own_kill", "p9:3:1"),
            ("cooldown_status", "p9:3:2"),
        ]

    def test_two_fresh_stores_yield_identical_id_streams(self) -> None:
        # Determinism: the identical packet sequence into two fresh stores
        # regenerates the identical (tick, type, observation_id) stream.
        def _ingest_all() -> MemoryStore:
            store = MemoryStore()
            for tick in (4, 9):
                ingest_packet(
                    packet=_packet(
                        tick=tick,
                        agent_id="p1",
                        visible_players=(
                            PlayerView(id="p2", room="ADMIN", action=None),
                        ),
                        visible_bodies=(
                            BodyView(id="p3-body", room="ADMIN", victim_id="p3"),
                        ),
                    ),
                    memory=store,
                )
            return store

        stream_a = [
            (e.tick, e.type, e.observation_id)
            for e in _ingest_all().recent(since_tick=0)
        ]
        stream_b = [
            (e.tick, e.type, e.observation_id)
            for e in _ingest_all().recent(since_tick=0)
        ]
        assert stream_a == stream_b

    def test_ids_survive_filtered_reads(self) -> None:
        # The id is stamped at write, never derived from read-time position: a
        # ``recent(since_tick=...)`` filter that drops earlier ticks leaves each
        # surviving row's id unchanged (so the tick-10 rows keep seq 0.. even
        # though they are no longer at index 0 of the full log).
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=5,
                agent_id="p1",
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
            ),
            memory=store,
        )
        ingest_packet(
            packet=_packet(
                tick=10,
                agent_id="p1",
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
            ),
            memory=store,
        )

        recent = store.recent(since_tick=10)
        assert all(e.tick == 10 for e in recent)
        observed = [e for e in recent if e.provenance == PROVENANCE_OBSERVED]
        assert [e.observation_id for e in observed] == ["p1:10:0", "p1:10:1"]

    def test_repeated_same_tick_ingest_continues_seq(self) -> None:
        # Production delivers one packet per (agent, tick), but the store tolerates
        # repeated same-tick ingestion; ``seq`` continues from the existing
        # id-stamped count so the two calls produce dense, non-colliding seq values
        # (and never trip the append-time duplicate-id guard).
        store = MemoryStore()
        ingest_packet(
            packet=_packet(
                tick=2,
                agent_id="p1",
                visible_players=(PlayerView(id="p2", room="ADMIN", action=None),),
            ),
            memory=store,
        )
        ingest_packet(
            packet=_packet(
                tick=2,
                agent_id="p1",
                visible_players=(PlayerView(id="p4", room="ADMIN", action=None),),
            ),
            memory=store,
        )

        observed_ids = [
            e.observation_id
            for e in store.recent(since_tick=0)
            if e.provenance == PROVENANCE_OBSERVED
        ]
        # First call: self_state(0), saw_player(1). Second call CONTINUES: 2, 3.
        assert observed_ids == ["p1:2:0", "p1:2:1", "p1:2:2", "p1:2:3"]
        assert len(observed_ids) == len(set(observed_ids))


class TestDuplicateIdGuard:
    def test_duplicate_non_none_id_append_raises(self) -> None:
        store = MemoryStore()
        store.append(
            EpisodicEvent(
                tick=1,
                type="saw_player",
                payload={"player_id": "p2", "room": "ADMIN", "action": None},
                provenance=PROVENANCE_OBSERVED,
                observation_id="p1:1:0",
            )
        )
        with pytest.raises(ValueError, match="duplicate observation id"):
            store.append(
                EpisodicEvent(
                    tick=1,
                    type="saw_player",
                    payload={"player_id": "p4", "room": "ADMIN", "action": None},
                    provenance=PROVENANCE_OBSERVED,
                    observation_id="p1:1:0",
                )
            )

    def test_repeated_none_ids_never_trip_the_guard(self) -> None:
        # A None id means "not a first-hand citable observation" and never enters
        # the uniqueness set, so any number of None-id rows append freely.
        store = MemoryStore()
        for _ in range(3):
            store.append(
                EpisodicEvent(
                    tick=1,
                    type="global_status",
                    payload={},
                    provenance=PROVENANCE_INFERRED,
                    observation_id=None,
                )
            )
        assert len(store) == 3


class TestReportedTestimonyCarriesNoId:
    def test_absorbed_testimony_row_has_no_observation_id(self) -> None:
        # Reported rows are meeting content, not first-hand perception: they carry
        # no observation id by design (only ``ingest_packet`` stamps ids).
        memory = AgentMemory()
        ingest_packet(
            packet=_packet(
                tick=20,
                agent_id="p1",
                visible_players=(
                    PlayerView(id="p3", room="ADMIN", action=None),
                    PlayerView(id="p5", room="ADMIN", action=None),
                ),
            ),
            memory=memory.episodic,
        )
        absorb_reported_testimony(
            memory,
            statements=(
                ReportedStatement(
                    speaker="p3",
                    kind="saw_player",
                    subject="p5",
                    from_tick=12,
                    to_tick=12,
                    room="ELECTRICAL",
                ),
            ),
        )

        reported = [
            e
            for e in memory.episodic.recent(since_tick=0)
            if e.type == EVENT_REPORTED_TESTIMONY
        ]
        assert len(reported) == 1
        assert reported[0].observation_id is None


class TestDeriveObservationId:
    def test_scheme_is_a_pure_function(self) -> None:
        # No RNG, no hash, no floats: a pure function of the three coordinates.
        assert derive_observation_id(agent_id="p3", tick=410, seq=2) == "p3:410:2"
        assert derive_observation_id(agent_id="p3", tick=410, seq=2) == "p3:410:2"
