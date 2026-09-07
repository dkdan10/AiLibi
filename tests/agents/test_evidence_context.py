"""Public bounds, movement provenance and memory-budget controls."""

from __future__ import annotations

from pathlib import Path
from dataclasses import replace

import pytest

from agents.memory.evidence_context import (
    assess_travel,
    evidence_context_lines,
    ingest_public_meeting_roster,
)
from agents.memory.episodic import EpisodicEvent
from agents.memory.store import absorb_reported_testimony, render_for_prompt
from eval.reasoning_evidence import fixture_map, fixture_memory, fixture_testimony
from meetings.manager import derive_reported_testimony


@pytest.mark.parametrize(
    "from_room,to_room,gap,expected",
    (
        ("A", "B", 1, True),
        ("A", "B", 0, False),
        ("A", "C", 2, True),
        ("A", "C", 1, False),
        ("A", "D", 20, False),
        ("A", "?", 20, None),
    ),
)
def test_travel_uses_public_topology_and_exact_clock(
    from_room: str, to_room: str, gap: int, expected: bool | None
) -> None:
    result = assess_travel(
        fixture_map(),
        from_room=from_room,
        to_room=to_room,
        from_tick=17,
        to_tick=17 + gap,
    )
    assert result.feasible is expected


def test_source_time_event_allows_one_move_after_same_tick_snapshot() -> None:
    assert (
        assess_travel(
            fixture_map(),
            from_room="A",
            to_room="B",
            from_tick=2,
            to_tick=2,
            to_phase="event",
        ).feasible
        is True
    )
    assert (
        assess_travel(
            fixture_map(),
            from_room="A",
            to_room="B",
            from_tick=2,
            to_tick=2,
        ).feasible
        is False
    )
    assert (
        assess_travel(
            fixture_map(),
            from_room="A",
            to_room="B",
            from_tick=2,
            to_tick=2,
            from_phase="unknown",
            to_phase="unknown",
        ).feasible
        is None
    )
    with pytest.raises(ValueError, match="backwards"):
        assess_travel(
            fixture_map(),
            from_room="A",
            to_room="B",
            from_tick=2,
            to_tick=2,
            from_phase="event",
        )


@pytest.mark.parametrize("announced", (False, True))
def test_discovery_retains_only_public_death_bounds(announced: bool) -> None:
    memory = fixture_memory(version=1)
    if announced:
        ingest_public_meeting_roster(
            memory, tick=8, living_ids=("p-1", "p-3", "p-4"), dead_ids=("p-2",)
        )
    memory.episodic.append(
        EpisodicEvent(
            tick=34,
            type="saw_body",
            provenance="observed",
            payload={"victim_id": "p-2", "body_id": "body-p-2", "room": "A"},
        )
    )
    lines = evidence_context_lines(memory, own_agent_id="p-1", teammate_ids=frozenset())
    assert len(lines) == 1
    assert f"known dead by tick {8 if announced else 34}" in lines[0]
    assert "body at tick 34" in lines[0] and "last saw them alive at tick 0" in lines[0]
    assert "Discovery does not date the death" in lines[0]


def test_public_roster_is_exact_once_and_conflicts_raise() -> None:
    memory = fixture_memory(version=1)
    kwargs = {"tick": 8, "living_ids": ("p-1", "p-3", "p-4"), "dead_ids": ("p-2",)}
    ingest_public_meeting_roster(memory, **kwargs)  # type: ignore[arg-type]
    size = len(memory.episodic)
    ingest_public_meeting_roster(memory, **kwargs)  # type: ignore[arg-type]
    assert len(memory.episodic) == size
    with pytest.raises(ValueError, match="conflicting"):
        ingest_public_meeting_roster(
            memory, tick=8, living_ids=("p-1", "p-2", "p-4"), dead_ids=("p-3",)
        )
    with pytest.raises(ValueError, match="disjoint"):
        ingest_public_meeting_roster(
            memory, tick=9, living_ids=("p-1",), dead_ids=("p-1",)
        )


def test_public_death_filters_current_beliefs_without_erasing_evidence() -> None:
    memory = fixture_memory(version=1)
    memory.beliefs.seed_player("p-2", suspicion=0.9, trust=0.5)
    before = render_for_prompt(memory)
    ingest_public_meeting_roster(
        memory, tick=8, living_ids=("p-1", "p-3", "p-4"), dead_ids=("p-2",)
    )
    after = render_for_prompt(memory)
    assert "p-2" in before.split("## Your current beliefs", 1)[-1]
    assert "Death evidence for p-2" in after
    assert memory.beliefs.view("p-2").suspicion == 0.9
    assert "p-2" not in after.split("## Your current beliefs", 1)[-1].split("##", 1)[0]


def test_reported_transition_preserves_origin_and_public_source_without_citable_upgrade() -> (
    None
):
    memory = fixture_memory(version=1)
    rows = derive_reported_testimony(
        fixture_testimony(), testimony_shapes=True, evidence_reasoning_version=1
    )
    absorb_reported_testimony(memory, statements=rows)
    event = memory.episodic.recent(since_tick=1)[-1]
    assert event.provenance == "reported" and event.observation_id is None
    assert event.payload["from_room"] == "A"
    text = render_for_prompt(memory)
    assert "move from A to B" in text
    assert "reported source turn:m:turn-0:obs:0" in text
    assert "not your own observation" in text


def test_witnessed_movement_supplies_breadcrumb_without_invented_tick() -> None:
    memory = fixture_memory(version=1)
    memory.episodic.append(
        EpisodicEvent(
            tick=4,
            type="saw_player_move",
            provenance="observed",
            payload={"player_id": "p-2", "from_room": "B", "to_room": "C"},
            observation_id="p-1:4:0",
        )
    )
    memory.episodic.append(
        EpisodicEvent(
            tick=5,
            type="saw_player",
            provenance="observed",
            payload={"player_id": "p-2", "room": "C", "action": None},
            observation_id="p-1:5:0",
        )
    )
    old = fixture_memory()
    for row in memory.episodic.recent(since_tick=4):
        old.episodic.append(row)
    assert "last seen there at tick 4" in render_for_prompt(memory)
    assert "last seen there at tick 4" not in render_for_prompt(old)


@pytest.mark.parametrize("budget", (300, 600, 1500))
def test_context_respects_existing_memory_budget(budget: int) -> None:
    memory = fixture_memory(version=1)
    ingest_public_meeting_roster(
        memory, tick=8, living_ids=("p-1",), dead_ids=("p-2", "p-3", "p-4")
    )
    assert len(render_for_prompt(memory, token_budget=budget)) <= budget * 4


@pytest.mark.parametrize("temporal", (False, True))
def test_actual_killer_packet_never_renders_own_victim_as_discovery(
    tmp_path: "Path",
    temporal: bool,
) -> None:
    from agents.memory.store import AgentMemory
    from agents.perception import ingest_event_observations, ingest_packet
    from engine.tick import advance_tick
    from engine.world import load_canonical_map
    from observation.service import ObservationService
    from tests.observation.test_service import _action, _base_world_state

    game_map = load_canonical_map()
    state, events = advance_tick(
        _base_world_state(),
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )
    memory = AgentMemory(evidence_reasoning_version=1)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit.jsonl",
        temporal_observations=temporal,
    )
    try:
        if temporal:
            batch = service.build_event_observations(
                world_state=state,
                agent_id="p-4",
                engine_events=events,
            )
            assert batch is not None and batch.own_kill is not None
            ingest_event_observations(batch=batch, memory=memory.episodic)
        packet = service.build_packet(
            world_state=state,
            agent_id="p-4",
            engine_events=events,
        )
        assert packet.visible_bodies
        ingest_packet(packet=packet, memory=memory.episodic)
        rendered = render_for_prompt(memory)
        assert "You (IMPOSTOR) killed p-1" in rendered
        assert "discovered" not in rendered
    finally:
        service.close()


@pytest.mark.parametrize("action", ("vent", "kill"))
def test_legacy_action_packet_clock_does_not_forge_impossible_travel(
    action: str,
) -> None:
    from agents.perception import ingest_packet
    from observation.packet import PlayerView
    from tests.agents.test_perception import _packet

    memory = fixture_memory(version=1)
    for tick, room, observed_action in ((3, "A", action), (4, "C", None)):
        packet = _packet(
            tick=tick,
            agent_id="p-1",
            room="A",
            visible_players=(PlayerView(id="p-2", room=room, action=observed_action),),
        )
        ingest_packet(packet=packet, memory=memory.episodic)
    lines = evidence_context_lines(memory, own_agent_id="p-1", teammate_ids=frozenset())
    assert not any("Travel check for p-2" in line for line in lines)
    # Replacing the ambiguous legacy action with an ordinary snapshot supplies
    # the missing clock precision and makes the two-edge/one-tick conflict real.
    from agents.memory.episodic import MemoryStore

    original = memory.episodic.recent(since_tick=0)
    memory.episodic = MemoryStore()
    for event in original:
        memory.episodic.append(
            replace(event, payload={**event.payload, "action": None})
            if event.type == "saw_player" and event.tick == 3
            else event
        )
    lines = evidence_context_lines(memory, own_agent_id="p-1", teammate_ids=frozenset())
    assert any("cannot be reconciled by walking" in line for line in lines)


@pytest.mark.parametrize("leaves", (False, True))
def test_suppression_is_not_movement_and_real_departure_remains(leaves: bool) -> None:
    from agents.memory.store import AgentMemory
    from agents.perception import ingest_packet
    from observation.packet import BodyView, PlayerView
    from tests.agents.test_perception import _packet

    memories = []
    for version in (None, 1):
        memory = AgentMemory(evidence_reasoning_version=version)
        for tick in range(8):
            packet = _packet(
                tick=tick,
                agent_id="p-1",
                room="A",
                role="IMPOSTOR",
                fellow_impostor_ids=("p-2",),
                visible_players=()
                if leaves and tick == 7
                else (PlayerView(id="p-2", room="A", action=None),),
                visible_bodies=(BodyView(id="body-p-3", victim_id="p-3", room="A"),)
                if tick == 4
                else (),
            )
            ingest_packet(packet=packet, memory=memory.episodic)
        memories.append(render_for_prompt(memory))
    legacy, candidate = memories
    assert "[tick 1] p-2 left A." in legacy
    assert "[tick 5] p-2 entered A." in legacy
    assert "[tick 1] p-2 left A." not in candidate
    assert "[tick 5] p-2 entered A." not in candidate
    assert ("[tick 7] p-2 left A." in candidate) is leaves


@pytest.mark.parametrize("source_timed", (False, True))
def test_death_lower_bound_uses_precise_sighting_not_legacy_delivery(
    source_timed: bool,
) -> None:
    from agents.perception import ingest_event_observations, ingest_packet
    from observation.packet import EventObservationBatch, PlayerView
    from tests.agents.test_perception import _packet

    memory = fixture_memory(version=1)
    player = PlayerView(id="p-2", room="A", action="vent")
    if source_timed:
        batch = EventObservationBatch(
            tick=7,
            agent_id="p-1",
            witnessed_actions=(player,),
        )
        ingest_event_observations(batch=batch, memory=memory.episodic)
    else:
        ingest_packet(
            packet=_packet(tick=8, agent_id="p-1", room="A", visible_players=(player,)),
            memory=memory.episodic,
        )
    ingest_public_meeting_roster(
        memory,
        tick=8,
        living_ids=("p-1", "p-3", "p-4"),
        dead_ids=("p-2",),
    )
    lines = evidence_context_lines(memory, own_agent_id="p-1", teammate_ids=frozenset())
    line = next(line for line in lines if line.startswith("Death evidence for p-2"))
    assert f"last saw them alive at tick {7 if source_timed else 0}" in line
    assert "known dead by tick 8" in line
    assert "alive at tick 8" not in line
