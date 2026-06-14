"""Task-id propagation round-trip: observation -> perception -> policy -> engine.

DESIGN.md §3.2 (agent-facing map id), §1.3 (observation firewall);
audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.2, §4 coupling 5.

The render-field-reader triad (``SelfView.pending_task_id`` ->
``agents/perception.py`` -> ``agents/memory``) and the ``do_task`` round-trip in
both tactical policies must all agree that the agent-facing id is the MAP id and
that the engine resolves it to the ACTING agent's OWN instance. These tests drive
the full path -- an :class:`ObservationService` packet, perception ingestion, a
tactical policy decision, intent->action translation, and one engine tick -- and
prove a ``do_task`` advances only the actor's own instance, never a co-owner of
the same map task. A drift in any leg (a composite instance id leaking into the
packet, a stale lookup against the map-keyed ``task_locations``, or the engine
resolving the wrong owner) breaks one of these tests; that is the determinism +
correctness guard the type checker cannot provide (the task's integration risk).

Tests legitimately import from ``engine/`` (the import-linter firewall constrains
``agents/`` source, not test code); the production agent path stays engine-free.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from agents.memory.episodic import MemoryStore
from agents.perception import ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerState, TaskState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from observation.action_intent import DoTaskIntent
from observation.service import ObservationService, impostor_pretend_task_id
from orchestrator.boundary import (
    public_map_from_engine_map,
    translate_action_intent,
)

# A real canonical-map task: ``swipe_card`` lives in ADMIN, so a policy can resolve
# it against ``task_locations`` and the engine accepts a ``do_task`` there.
_MAP_TASK_ID = "swipe_card"
_TASK_ROOM = "ADMIN"


def _player(player_id: str, role: str, room: str) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="IMPOSTOR" if role == "IMPOSTOR" else "CREWMATE",
        alive=True,
        room=room,
        position=(0.0, 0.0),
        last_action=None,
        in_vent=False,
    )


def _own_instance(owner: str) -> TaskState:
    # Each owner holds its OWN instance of the same map task (``swipe_card``) in
    # ADMIN with required_ticks=3, so a single do_task tick moves progress 0 -> 1
    # (not completion) and the "only the actor's instance advanced" assertion is
    # crisp: the co-owner's instance stays at exactly 0.
    return TaskState(
        id=f"{owner}:{_MAP_TASK_ID}",
        owner=owner,
        map_task_id=_MAP_TASK_ID,
        room=_TASK_ROOM,
        progress=0,
        required_ticks=3,
        completed=False,
    )


def _round_trip_world(*, seed: int = 99) -> WorldState:
    """Two crewmates and one impostor, all in ADMIN. The two crewmates each own an
    INSTANCE of the same map task ``swipe_card``; the impostor co-owns one too --
    a deliberately artificial instance (production seeds tasks to crewmates only)
    kept ONLY to prove the crewmate isolation case (a crew do_task never touches a
    co-owner's instance, impostor included). The impostor is on cooldown so its
    policy idles into the BLENDING pretend-task path (Task 10.14) rather than
    attempting a kill -- and that pretend id is a DIFFERENT map task than
    ``swipe_card`` (impostors own no real instance), so its do_task is rejected.
    """

    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "p-1": _player("p-1", "CREWMATE", _TASK_ROOM),
            "p-2": _player("p-2", "CREWMATE", _TASK_ROOM),
            "p-3": _player("p-3", "IMPOSTOR", _TASK_ROOM),
        },
        bodies={},
        tasks={
            instance.id: instance
            for instance in (
                _own_instance("p-1"),
                _own_instance("p-2"),
                _own_instance("p-3"),
            )
        },
        sabotage=None,
        cooldowns={"p-3": 5},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def test_crewmate_do_task_round_trip_advances_only_own_instance(
    tmp_path: Path,
) -> None:
    game_map = load_canonical_map()
    state = _round_trip_world()
    public_map = public_map_from_engine_map(game_map)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    # Observation leg: the packet carries the MAP id, owner-scoped to p-1.
    packet = service.build_packet(world_state=state, agent_id="p-1", engine_events=[])
    assert packet.self_state.pending_task_id == _MAP_TASK_ID

    # Perception leg: the map id rides into memory verbatim.
    memory = MemoryStore()
    ingest_packet(packet=packet, memory=memory)

    # Policy/reader leg: the crewmate resolves the map id against the map-keyed
    # ``task_locations`` and submits the SAME map id back as the do_task payload.
    intent = CrewmatePolicy(agent_id="p-1").decide(memory, public_map)
    assert isinstance(intent, DoTaskIntent)
    assert intent.payload.task_id == _MAP_TASK_ID

    # Engine leg: (actor=p-1, swipe_card) resolves to p-1's OWN instance only.
    action = translate_action_intent(intent)
    next_state, _ = advance_tick(state, [action], game_map=game_map)
    assert next_state.tasks["p-1:swipe_card"].progress == 1
    assert next_state.tasks["p-2:swipe_card"].progress == 0
    assert next_state.tasks["p-3:swipe_card"].progress == 0


def test_impostor_pretend_do_task_round_trip_advances_no_instance(
    tmp_path: Path,
) -> None:
    # Task 10.14 BLENDING round-trip: the impostor's pending_task_id is a PRETEND
    # map id (impostors own no instance), DIFFERENT from the swipe_card it co-owns
    # in this artificial fixture. The full observation -> perception -> policy ->
    # engine round-trip emits a do_task on the pretend id, which the engine
    # REJECTS (no owned instance): no instance advances -- not even the swipe_card
    # the impostor happens to co-own, because the engine resolves the PRETEND id,
    # which the impostor owns none of -- and no pretend instance is minted, so the
    # crew win denominator never moves. The integrity invariant, end-to-end.
    game_map = load_canonical_map()
    base = _round_trip_world()
    pretend = impostor_pretend_task_id(
        game_map=game_map,
        agent_id="p-3",
        impostor_ids=["p-3"],
        tick=base.tick,
    )
    assert pretend is not None
    assert pretend != _MAP_TASK_ID  # a DIFFERENT map task than the co-owned one
    pretend_room = game_map.tasks[pretend].room
    # Place the impostor in the pretend task's room so its idle policy PERFORMS it
    # (rather than routing toward it), exercising the do_task leg end-to-end.
    players = dict(base.players)
    players["p-3"] = _player("p-3", "IMPOSTOR", pretend_room)
    state = dataclasses.replace(base, players=players)
    public_map = public_map_from_engine_map(game_map)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    packet = service.build_packet(world_state=state, agent_id="p-3", engine_events=[])
    assert packet.self_state.pending_task_id == pretend
    assert packet.cooldown == 5

    memory = MemoryStore()
    ingest_packet(packet=packet, memory=memory)

    intent = ImpostorPolicy(agent_id="p-3").decide(memory, public_map)
    assert isinstance(intent, DoTaskIntent)
    assert intent.payload.task_id == pretend

    tasks_before = len(state.tasks)
    action = translate_action_intent(intent)
    next_state, events = advance_tick(state, [action], game_map=game_map)

    # The fake do_task is REJECTED for owning no instance -- no progress anywhere.
    assert any(
        event.type == "ActionRejected"
        and event.actor == "p-3"
        and "owns no task instance" in event.reason
        for event in events
    )
    # Not even the swipe_card the impostor co-owns advances (it acted on the
    # pretend id, which it does not own), and the crew co-owners are untouched.
    assert next_state.tasks["p-3:swipe_card"].progress == 0
    assert next_state.tasks["p-1:swipe_card"].progress == 0
    assert next_state.tasks["p-2:swipe_card"].progress == 0
    # No pretend instance was minted: the win denominator did not move.
    assert len(next_state.tasks) == tasks_before
    assert f"p-3:{pretend}" not in next_state.tasks


def test_co_owners_advance_independently_over_the_round_trip(
    tmp_path: Path,
) -> None:
    # Both crewmate co-owners act on the SAME tick: each do_task advances only its
    # own instance, proving the per-player progress isolation holds end-to-end
    # through the observation/policy round-trip (not just at the engine boundary).
    game_map = load_canonical_map()
    state = _round_trip_world()
    public_map = public_map_from_engine_map(game_map)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    actions = []
    for crew_id in ("p-1", "p-2"):
        packet = service.build_packet(
            world_state=state, agent_id=crew_id, engine_events=[]
        )
        memory = MemoryStore()
        ingest_packet(packet=packet, memory=memory)
        intent = CrewmatePolicy(agent_id=crew_id).decide(memory, public_map)
        assert isinstance(intent, DoTaskIntent)
        actions.append(translate_action_intent(intent))

    next_state, _ = advance_tick(state, actions, game_map=game_map)

    assert next_state.tasks["p-1:swipe_card"].progress == 1
    assert next_state.tasks["p-2:swipe_card"].progress == 1
    # The impostor never acted: its instance of the same map task stays at 0.
    assert next_state.tasks["p-3:swipe_card"].progress == 0
