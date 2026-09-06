"""Owned-source reduction and bounded intention state, with adverse controls."""

from __future__ import annotations

from dataclasses import replace
from typing import Any

import pytest

from agents.memory.episodic import EpisodicEvent
from agents.memory.evidence_context import ingest_public_meeting_roster
from agents.memory.investigation import (
    ConsumedInvestigationSource,
    InvestigationEvidence,
    InvestigationObservation,
    InvestigationPlan,
    InvestigationState,
    investigation_packet_sha256,
    reduce_investigation_evidence,
)
from agents.memory.store import AgentMemory
from agents.memory.working import WorkingMemory
from agents.perception import ingest_packet
from observation.action_intent import WaitIntent
from observation.packet import BodyView, PlayerView
from tests.agents.test_perception import _packet, _public_map


def _memory() -> AgentMemory:
    memory = AgentMemory(evidence_reasoning_version=2)
    packet = _packet(
        tick=2, visible_players=(PlayerView(id="p2", room="ADMIN", action=None),)
    ).model_copy(update={"temporal_observation_version": 2})
    ingest_packet(packet=packet, memory=memory.episodic)
    return memory


def _reduce(memory: AgentMemory, tick: int = 8) -> InvestigationEvidence:
    return reduce_investigation_evidence(
        memory, observer_id="p1", tick=tick, public_map=_public_map()
    )


def _movement(
    *,
    room: str = "ELECTRICAL",
    order: int = 1,
    observation_id: str = "opaque-future-looking:9999",
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=2,
        type="saw_player_move",
        provenance="observed",
        observation_id=observation_id,
        payload={
            "player_id": "p2",
            "from_room": "ADMIN",
            "to_room": room,
            "source_tick": 2,
            "observation_phase": "event",
            "observation_order": order,
        },
    )


def _plan(**updates: Any) -> InvestigationPlan:
    values: dict[str, Any] = dict(
        target_id="p2",
        source_observation_id="owned-source",
        source_tick=2,
        last_known_room="ADMIN",
        started_tick=6,
        expires_tick=12,
        visited_rooms=(),
    )
    values.update(updates)
    return InvestigationPlan.model_validate(values)


def _state(
    *, tick: int = 6, active: bool = True, source_tick: int = 2
) -> InvestigationState:
    return InvestigationState(
        active_plan=_plan() if active else None,
        consumed_sources=(
            ConsumedInvestigationSource(
                target_id="p2",
                source_observation_id="owned-source",
                source_tick=source_tick,
            ),
        ),
        last_processed_tick=tick,
        last_packet_sha256="a" * 64,
        last_intent=WaitIntent(actor="p1", type="wait"),
    )


def test_actual_perception_and_event_clock_beat_ids_and_render_cache() -> None:
    memory = _memory()
    memory.episodic.append(_movement(order=2, observation_id="earliest-looking-id"))
    memory.episodic.append(_movement(room="CAFETERIA", order=1))
    memory.working.record_sighting(player_id="p2", room="ADMIN", tick=999)
    evidence = _reduce(memory)
    assert evidence.sightings == (
        InvestigationObservation(
            target_id="p2",
            source_observation_id="earliest-looking-id",
            source_tick=2,
            last_known_room="ELECTRICAL",
            observation_phase="event",
            observation_order=2,
        ),
    )
    assert evidence.known_dead_ids == ()
    assert memory.working.last_seen("p2") is not None


def test_later_snapshot_reacquires_at_its_actual_later_time() -> None:
    memory = _memory()
    memory.episodic.append(_movement())
    packet = _packet(
        tick=7, visible_players=(PlayerView(id="p2", room="CAFETERIA", action=None),)
    ).model_copy(update={"temporal_observation_version": 2})
    ingest_packet(packet=packet, memory=memory.episodic)
    sighting = _reduce(memory).sightings[0]
    assert (
        sighting.source_tick,
        sighting.last_known_room,
        sighting.observation_phase,
    ) == (7, "CAFETERIA", "snapshot")


@pytest.mark.parametrize("provenance", ["reported", "inferred", "public"])
def test_testimony_or_public_relocation_cannot_replace_owned_sighting(
    provenance: str,
) -> None:
    memory = _memory()
    before = _reduce(memory)
    memory.episodic.append(replace(_movement(), provenance=provenance))
    memory.episodic.append(
        EpisodicEvent(
            tick=3,
            type="public_regroup",
            payload={"room": "ELECTRICAL", "player_ids": ("p1", "p2")},
            provenance="public",
        )
    )
    assert _reduce(memory) == before


def test_another_agents_private_memory_does_not_supply_a_candidate() -> None:
    own, other = _memory(), _memory()
    before = _reduce(own)
    other.episodic.append(_movement())
    other.working.record_sighting(player_id="hidden-player", room="ELECTRICAL", tick=8)
    assert _reduce(own) == before
    assert _reduce(other).sightings != before.sightings


def test_known_deaths_union_owned_bodies_and_announcements_only() -> None:
    memory = _memory()
    packet = _packet(
        tick=3,
        visible_bodies=(BodyView(id="body-p3", victim_id="p3", room="CAFETERIA"),),
    ).model_copy(update={"temporal_observation_version": 2})
    ingest_packet(packet=packet, memory=memory.episodic)
    ingest_public_meeting_roster(
        memory, tick=4, living_ids=("p1", "p2", "p4", "p5"), dead_ids=("p3", "p6")
    )
    memory.meeting_history.record(end_tick=5, ejected_id="p4")
    evidence = _reduce(memory)
    assert evidence.known_dead_ids == ("p3", "p4", "p6")
    assert "p5" in evidence.known_player_ids
    assert "p5" not in evidence.known_dead_ids


@pytest.mark.parametrize(
    "updates",
    [
        {"source_tick": 999},
        {"source_tick": True},
        {"observation_phase": "snapshot", "observation_order": 2},
        {"observation_phase": "event", "observation_order": None},
        {"to_room": "PRIVATE_ROOM"},
    ],
)
def test_planted_invalid_sighting_is_refused(updates: dict[str, Any]) -> None:
    memory = _memory()
    row = _movement()
    memory.episodic.append(replace(row, payload={**row.payload, **updates}))
    with pytest.raises(ValueError):
        _reduce(memory)


def test_legacy_timing_is_not_silently_promoted() -> None:
    memory = AgentMemory()
    ingest_packet(
        packet=_packet(
            tick=2, visible_players=(PlayerView(id="p2", room="ADMIN", action=None),)
        ),
        memory=memory.episodic,
    )
    with pytest.raises(ValueError, match="actual source tick"):
        _reduce(memory)


def test_future_memory_and_foreign_observer_are_refused() -> None:
    with pytest.raises(ValueError, match="future"):
        _reduce(_memory(), tick=1)
    with pytest.raises(ValueError, match="different observer"):
        reduce_investigation_evidence(
            _memory(), observer_id="p2", tick=8, public_map=_public_map()
        )


@pytest.mark.parametrize("superseded", [False, True])
def test_conflicting_same_order_rooms_are_not_tiebroken_by_id(
    superseded: bool,
) -> None:
    memory = _memory()
    if superseded:
        memory.episodic.append(_movement(order=2, observation_id="latest"))
    memory.episodic.append(_movement(observation_id="a"))
    memory.episodic.append(_movement(room="CAFETERIA", observation_id="z"))
    with pytest.raises(ValueError, match="ambiguous"):
        _reduce(memory)


@pytest.mark.parametrize(
    "updates",
    [
        {"expires_tick": 13},
        {"expires_tick": 6},
        {"started_tick": 1},
        {"source_tick": True},
        {"visited_rooms": ("A", "B", "C", "D")},
        {"visited_rooms": ("A", "A")},
    ],
)
def test_plan_rejects_unbounded_or_ambiguous_state(updates: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        _plan(**updates)


@pytest.mark.parametrize(
    "partial",
    [
        {"last_processed_tick": 2},
        {"last_packet_sha256": "a" * 64},
        {"last_intent": {"actor": "p1", "type": "wait"}},
    ],
)
def test_cache_requires_complete_input_and_output(partial: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="cache requires"):
        InvestigationState.model_validate(partial)


def test_hash_binds_same_tick_input_changes_and_is_repeatable() -> None:
    packet = _packet(tick=6)
    assert investigation_packet_sha256(packet) == investigation_packet_sha256(
        packet.model_copy()
    )
    changed = packet.model_copy(update={"cooldown": 7})
    assert investigation_packet_sha256(packet) != investigation_packet_sha256(changed)


def test_working_state_is_single_immutable_value_and_clear_preserves_sources() -> None:
    working = WorkingMemory()
    active = _state()
    working.set_investigation_state(active, known_player_ids=("p1", "p2"))
    working.set_investigation_state(active, known_player_ids=("p1", "p2"))
    completed = _state(tick=7, active=False)
    working.set_investigation_state(completed, known_player_ids=("p1", "p2"))
    assert working.investigation == completed
    assert working.goal is None and working.path == ()
    with pytest.raises(ValueError, match="frozen"):
        active.active_plan = None
    with pytest.raises(ValueError, match="forget"):
        working.set_investigation_state(
            InvestigationState(
                last_processed_tick=8,
                last_packet_sha256="a" * 64,
                last_intent=WaitIntent(actor="p1", type="wait"),
            ),
            known_player_ids=("p1", "p2"),
        )


def test_working_rejects_roster_growth_tick_rewind_and_same_tick_rewrite() -> None:
    working = WorkingMemory()
    with pytest.raises(ValueError, match="roster"):
        working.set_investigation_state(_state(), known_player_ids=("p1",))
    working.set_investigation_state(_state(), known_player_ids=("p1", "p2"))
    with pytest.raises(ValueError, match="backwards"):
        working.set_investigation_state(
            _state(tick=5, active=False), known_player_ids=("p1", "p2")
        )
    with pytest.raises(ValueError, match="conflicting"):
        working.set_investigation_state(
            _state(active=False), known_player_ids=("p1", "p2")
        )
    with pytest.raises(ValueError, match="distinct target"):
        InvestigationState(consumed_sources=(_state().consumed_sources[0],) * 2)
    changed = _state(tick=7).model_copy(
        update={
            "consumed_sources": (
                ConsumedInvestigationSource(
                    target_id="p2",
                    source_observation_id="forged-replacement",
                    source_tick=2,
                ),
            )
        }
    )
    with pytest.raises(ValueError, match="identity cannot change"):
        working.set_investigation_state(changed, known_player_ids=("p1", "p2"))


def test_public_lifecycle_cancellation_preserves_cache_and_consumption() -> None:
    working = WorkingMemory()
    working.cancel_investigation_plan()
    assert working.investigation is None
    state = _state()
    working.set_investigation_state(state, known_player_ids=("p1", "p2"))
    working.cancel_investigation_plan()
    expected = state.model_copy(update={"active_plan": None})
    assert working.investigation == expected
    working.cancel_investigation_plan()
    assert working.investigation == expected
    with pytest.raises(ValueError, match="conflicting"):
        working.set_investigation_state(state, known_player_ids=("p1", "p2"))
