from __future__ import annotations

import dataclasses
from collections.abc import Sequence
import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyState, PlayerState, TaskState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from observation.packet import PlayerView
from observation.service import ObservationService, impostor_pretend_task_id

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _action(data: object) -> Action:
    return _ACTION_ADAPTER.validate_python(data)


def _task_instance(
    *,
    owner: str,
    map_task_id: str,
    room: str,
    progress: int = 0,
    required_ticks: int = 1,
    completed: bool = False,
) -> TaskState:
    # Per-player task instance (DESIGN.md §3.2): the instance ``id`` is the
    # composite ``"{owner}:{map_task_id}"`` and equals its ``WorldState.tasks``
    # key, while the agent-facing id is the bare ``map_task_id``.
    return TaskState(
        id=f"{owner}:{map_task_id}",
        owner=owner,
        map_task_id=map_task_id,
        room=room,
        progress=progress,
        required_ticks=required_ticks,
        completed=completed,
    )


def _tasks(*instances: TaskState) -> dict[str, TaskState]:
    return {task.id: task for task in instances}


def _player(
    player_id: str,
    role: str,
    room: str,
    position: tuple[float, float],
) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="IMPOSTOR" if role == "IMPOSTOR" else "CREWMATE",
        alive=True,
        room=room,
        position=position,
        last_action=None,
        in_vent=False,
    )


def _base_world_state(*, seed: int = 42) -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "p-1": _player("p-1", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "p-2": _player("p-2", "CREWMATE", "REACTOR", (0.0, 0.0)),
            "p-3": _player("p-3", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "p-4": _player("p-4", "IMPOSTOR", "STORAGE", (1.0, 0.0)),
        },
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={"p-4": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def _multi_impostor_world_state(*, seed: int = 7) -> WorldState:
    # Five players, two impostors (p-2, p-4), three crewmates (p-1, p-3, p-5).
    # The three committed scripted fixtures are all 4p/1i, so this is the only
    # service-level roster that exercises the impostor-sees-teammate path and a
    # roster where a crew misroute into ``fellow_impostor_ids`` could surface.
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "p-1": _player("p-1", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "p-2": _player("p-2", "IMPOSTOR", "REACTOR", (0.0, 0.0)),
            "p-3": _player("p-3", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "p-4": _player("p-4", "IMPOSTOR", "STORAGE", (1.0, 0.0)),
            "p-5": _player("p-5", "CREWMATE", "ADMIN", (0.0, 0.0)),
        },
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={"p-2": 0, "p-4": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def _observation_service(tmp_path: Path) -> ObservationService:
    return ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "observation_audit.jsonl",
    )


def _visible_player(packet_id: str, packet_players: Sequence[PlayerView]) -> PlayerView:
    return next(player for player in packet_players if player.id == packet_id)


def test_kill_witness_sees_killer_action(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["p-2"] = _player("p-2", "CREWMATE", "STORAGE", (2.0, 0.0))
    state = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns=state.cooldowns,
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    state, events = advance_tick(
        state,
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=events,
    )

    visible_impostor = _visible_player("p-4", packet.visible_players)
    assert visible_impostor.action == "kill"


def test_visible_player_action_does_not_reveal_unseen_kill(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _base_world_state(),
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )
    state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "ENGINEERING"},
                }
            )
        ],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=events,
    )

    visible_impostor = _visible_player("p-4", packet.visible_players)
    assert visible_impostor.action is None


def test_vent_witness_sees_vent_action_and_audible_event(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["p-4"] = _player("p-4", "IMPOSTOR", "ADMIN", (1.0, 0.0))
    players["p-2"] = _player("p-2", "CREWMATE", "ADMIN", (0.0, 0.0))
    state = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns=state.cooldowns,
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-4",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=events,
    )

    visible_impostor = _visible_player("p-4", packet.visible_players)
    assert visible_impostor.action == "vent"
    assert [event.model_dump(mode="json") for event in packet.audible_events] == [
        {"kind": "vent_use_heard", "room": "ADMIN"},
    ]


def test_vented_player_is_hidden_without_same_tick_event(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = _base_world_state()
    players = dict(state.players)
    players["p-4"] = _player("p-4", "IMPOSTOR", "ADMIN", (1.0, 0.0))
    players["p-2"] = _player("p-2", "CREWMATE", "ADMIN", (0.0, 0.0))
    state = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns=state.cooldowns,
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )
    state, _ = advance_tick(
        state,
        [
            _action(
                {
                    "type": "vent",
                    "actor": "p-4",
                    "payload": {"vent_id": "ADMIN_VENT"},
                }
            )
        ],
        game_map=game_map,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state,
        agent_id="p-2",
        engine_events=[],
    )

    assert "p-4" not in {player.id for player in packet.visible_players}


def test_crewmate_cooldown_is_never_exposed(tmp_path: Path) -> None:
    state = _base_world_state()
    state_with_bad_cooldown = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=state.players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns={**dict(state.cooldowns), "p-2": 7},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state_with_bad_cooldown,
        agent_id="p-2",
        engine_events=[],
    )

    assert packet.cooldown is None


def test_impostor_receives_own_cooldown(tmp_path: Path) -> None:
    state = _base_world_state()
    state_with_cooldown = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=state.players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns={"p-4": 6},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state_with_cooldown,
        agent_id="p-4",
        engine_events=[],
    )

    assert packet.cooldown == 6


def test_impostors_see_each_other_and_crew_see_empty_team(tmp_path: Path) -> None:
    # Task 7.2 (DESIGN.md §1.3, locked decision 3): each impostor receives the
    # identity of its fellow impostor(s) on the privileged self channel, with
    # its own id excluded; every crewmate receives an empty tuple.
    state = _multi_impostor_world_state()
    service = _observation_service(tmp_path)

    packets = {
        player_id: service.build_packet(
            world_state=state, agent_id=player_id, engine_events=[]
        )
        for player_id in state.players
    }

    # Each impostor sees exactly the OTHER impostor; its own id is excluded.
    assert packets["p-2"].self_state.fellow_impostor_ids == ("p-4",)
    assert packets["p-4"].self_state.fellow_impostor_ids == ("p-2",)
    assert "p-2" not in packets["p-2"].self_state.fellow_impostor_ids
    assert "p-4" not in packets["p-4"].self_state.fellow_impostor_ids

    # Crew-empty leak invariant over every crewmate-recipient packet built from
    # the 2-impostor world state -- a misroute into a crew tuple would surface
    # here, where it cannot in the single-impostor scripted fixtures.
    for crew_id in ("p-1", "p-3", "p-5"):
        assert packets[crew_id].self_state.role == "CREWMATE"
        assert packets[crew_id].self_state.fellow_impostor_ids == ()


def test_sole_impostor_has_no_fellow_impostors(tmp_path: Path) -> None:
    # An impostor with no teammates (the 4p/1i base roster) gets an empty
    # tuple -- the same value a crewmate gets, by construction.
    state = _base_world_state()
    packet = _observation_service(tmp_path).build_packet(
        world_state=state, agent_id="p-4", engine_events=[]
    )

    assert packet.self_state.role == "IMPOSTOR"
    assert packet.self_state.fellow_impostor_ids == ()


def test_audit_log_records_sanitized_packet(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state, _ = advance_tick(
        _base_world_state(),
        [_action({"type": "kill", "actor": "p-4", "payload": {"target": "p-1"}})],
        game_map=game_map,
    )
    state, events = advance_tick(
        state,
        [
            _action(
                {
                    "type": "move",
                    "actor": "p-2",
                    "payload": {"to_room": "ENGINEERING"},
                }
            )
        ],
        game_map=game_map,
    )
    state_with_bad_cooldown = WorldState(
        tick=state.tick,
        phase=state.phase,
        map=state.map,
        players=state.players,
        bodies=state.bodies,
        tasks=state.tasks,
        sabotage=state.sabotage,
        cooldowns={**dict(state.cooldowns), "p-2": 7},
        emergency_uses=state.emergency_uses,
        rng_state=state.rng_state,
        seed=state.seed,
    )
    audit_path = tmp_path / "observation_audit.jsonl"
    service = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=audit_path,
    )

    packet = service.build_packet(
        world_state=state_with_bad_cooldown,
        agent_id="p-2",
        engine_events=events,
    )

    [audit_entry] = [
        json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()
    ]
    visible_impostor = next(
        player for player in audit_entry["visible_players"] if player["id"] == "p-4"
    )
    assert audit_entry == packet.model_dump(mode="json")
    assert visible_impostor["action"] is None
    assert audit_entry["cooldown"] is None


def test_discovered_body_is_hidden_from_subsequent_packets(tmp_path: Path) -> None:
    # Pins today's engine/visibility.py rule (DESIGN.md §3.6 / §4.2): once a
    # body has discovered_by set, it is filtered out of every observer's
    # visible_bodies — including the discoverer's own packet on the same tick.
    state = _base_world_state()
    body = BodyState(
        id="body-p-1-0",
        player_id="p-1",
        room="REACTOR",
        position=(0.0, 0.0),
        killed_by="p-4",
        discovered_by=None,
    )
    state_with_body = dataclasses.replace(state, bodies={body.id: body})
    service = _observation_service(tmp_path)

    packet_before = service.build_packet(
        world_state=state_with_body,
        agent_id="p-2",
        engine_events=[],
    )
    assert "body-p-1-0" in {b.id for b in packet_before.visible_bodies}

    discovered_body = dataclasses.replace(body, discovered_by="p-2")
    state_after_discovery = dataclasses.replace(
        state_with_body, bodies={discovered_body.id: discovered_body}
    )

    packet_after = service.build_packet(
        world_state=state_after_discovery,
        agent_id="p-2",
        engine_events=[],
    )

    assert packet_after.visible_bodies == ()


def test_visible_body_carries_victim_id_from_body_state(tmp_path: Path) -> None:
    # R-4: ObservationService is the single privileged consumer of engine
    # state (DESIGN.md §1.3). It reads ``BodyState.player_id`` and
    # surfaces it as ``BodyView.victim_id``. The body-id format already
    # encodes the victim id; this assertion pins that the typed field
    # carries the same value across every visible body in every packet.
    # REACTOR is adjacent to ENGINEERING in canonical_1, so an observer
    # in REACTOR sees bodies in either room.
    state = _base_world_state()
    bodies = {
        "body-p-1-3": BodyState(
            id="body-p-1-3",
            player_id="p-1",
            room="REACTOR",
            position=(0.0, 0.0),
            killed_by="p-4",
            discovered_by=None,
        ),
        "body-p-3-4": BodyState(
            id="body-p-3-4",
            player_id="p-3",
            room="ENGINEERING",
            position=(0.0, 0.0),
            killed_by="p-4",
            discovered_by=None,
        ),
    }
    state_with_bodies = dataclasses.replace(state, bodies=bodies)
    service = _observation_service(tmp_path)

    packet = service.build_packet(
        world_state=state_with_bodies,
        agent_id="p-2",
        engine_events=[],
    )

    bodies_by_id = {body.id: body for body in packet.visible_bodies}
    assert set(bodies_by_id) == {"body-p-1-3", "body-p-3-4"}
    assert bodies_by_id["body-p-1-3"].victim_id == bodies["body-p-1-3"].player_id
    assert bodies_by_id["body-p-3-4"].victim_id == bodies["body-p-3-4"].player_id
    # Every visible body has the field populated; victim_id is required by
    # the Pydantic schema, so an unset value would have failed validation
    # before the packet was returned.
    for body in packet.visible_bodies:
        assert body.victim_id, "victim_id must be a non-empty string"


def test_observation_packet_collections_are_immutable(tmp_path: Path) -> None:
    packet = _observation_service(tmp_path).build_packet(
        world_state=_base_world_state(),
        agent_id="p-2",
        engine_events=[],
    )

    assert isinstance(packet.visible_players, tuple)
    assert isinstance(packet.visible_bodies, tuple)
    assert isinstance(packet.audible_events, tuple)
    with pytest.raises(AttributeError):
        packet.visible_players.append(PlayerView(id="x", room="ADMIN", action=None))  # type: ignore[attr-defined]


def test_audit_log_appends_across_two_instances(tmp_path: Path) -> None:
    """R-13 regression: two ``ObservationService`` instances pointed at the
    same audit-log path must each *append*, not overwrite. Pins
    ``observation/audit.py:20-23`` open mode ``"a"`` — flipping to ``"w"``
    silently slips past single-instance tests today.
    """

    state = _base_world_state()
    service_one = _observation_service(tmp_path)
    service_one.build_packet(world_state=state, agent_id="p-1", engine_events=[])
    del service_one

    service_two = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "observation_audit.jsonl",
    )
    service_two.build_packet(world_state=state, agent_id="p-2", engine_events=[])

    audit_path = tmp_path / "observation_audit.jsonl"
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first_entry = json.loads(lines[0])
    second_entry = json.loads(lines[1])
    assert first_entry["agent_id"] == "p-1"
    assert second_entry["agent_id"] == "p-2"


class TestPendingTaskIdIsOwnMapId:
    """``SelfView.pending_task_id`` is the agent's OWN map task id (DESIGN.md §3.2,
    §1.3). Under the per-player keyspace ``WorldState.tasks`` is keyed by the
    composite instance id; the observation boundary must surface the bare map id,
    owner-scoped, never the composite and never another player's task.
    """

    def test_pending_task_id_is_the_map_id_not_the_instance_id(
        self, tmp_path: Path
    ) -> None:
        state = dataclasses.replace(
            _base_world_state(),
            tasks=_tasks(
                _task_instance(owner="p-1", map_task_id="swipe_card", room="ADMIN"),
            ),
        )

        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )

        # The agent-facing MAP id, never the composite instance id "p-1:swipe_card".
        assert packet.self_state.pending_task_id == "swipe_card"
        assert ":" not in (packet.self_state.pending_task_id or "")

    def test_two_owners_of_one_map_task_each_see_only_the_shared_map_id(
        self, tmp_path: Path
    ) -> None:
        # p-1 and p-2 each hold an INSTANCE of the same map task. Each packet
        # carries only the shared map id -- no instance id, no ownership -- so the
        # engine can resolve (actor, map_id) to each owner's own instance.
        state = dataclasses.replace(
            _base_world_state(),
            tasks=_tasks(
                _task_instance(owner="p-1", map_task_id="swipe_card", room="ADMIN"),
                _task_instance(owner="p-2", map_task_id="swipe_card", room="ADMIN"),
            ),
        )
        service = _observation_service(tmp_path)

        packet_one = service.build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )
        packet_two = service.build_packet(
            world_state=state, agent_id="p-2", engine_events=[]
        )

        assert packet_one.self_state.pending_task_id == "swipe_card"
        assert packet_two.self_state.pending_task_id == "swipe_card"
        assert ":" not in (packet_one.self_state.pending_task_id or "")
        assert ":" not in (packet_two.self_state.pending_task_id or "")

    def test_pending_task_id_selects_first_unfinished_map_id_deterministically(
        self, tmp_path: Path
    ) -> None:
        # p-1 owns two unfinished instances and one completed one. The completed
        # instance is skipped (its map id would sort first if it were not), and
        # the lexicographically-first remaining map id is surfaced.
        state = dataclasses.replace(
            _base_world_state(),
            tasks=_tasks(
                _task_instance(owner="p-1", map_task_id="swipe_card", room="ADMIN"),
                _task_instance(owner="p-1", map_task_id="submit_scan", room="MEDBAY"),
                _task_instance(
                    owner="p-1",
                    map_task_id="align_engine_output",
                    room="ENGINEERING",
                    completed=True,
                ),
            ),
        )

        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )

        # sorted unfinished map ids: ["submit_scan", "swipe_card"] -> first.
        # "align_engine_output" is completed and excluded despite sorting first.
        assert packet.self_state.pending_task_id == "submit_scan"

    def test_pending_task_id_is_none_when_all_owned_instances_complete(
        self, tmp_path: Path
    ) -> None:
        state = dataclasses.replace(
            _base_world_state(),
            tasks=_tasks(
                _task_instance(
                    owner="p-1",
                    map_task_id="swipe_card",
                    room="ADMIN",
                    completed=True,
                ),
                # Another player's unfinished instance must NOT surface for p-1.
                _task_instance(owner="p-2", map_task_id="submit_scan", room="MEDBAY"),
            ),
        )

        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )

        assert packet.self_state.pending_task_id is None


class TestGlobalViewCountsInstances:
    """``GlobalView.tasks_total`` / ``task_completion_percent`` count per-player
    task INSTANCES, equal to the engine's win denominator (DESIGN.md §3.2/§3.5).
    """

    def test_tasks_total_counts_instances_not_map_tasks(self, tmp_path: Path) -> None:
        # Two owners of the SAME map task = two INSTANCES. The denominator counts
        # instances (2), not the single distinct map task -- so it can exceed the
        # 12 map-task pool the moment overlap exists (the cap removal's premise).
        tasks = _tasks(
            _task_instance(
                owner="p-1",
                map_task_id="swipe_card",
                room="ADMIN",
                completed=True,
            ),
            _task_instance(owner="p-2", map_task_id="swipe_card", room="ADMIN"),
            _task_instance(owner="p-3", map_task_id="submit_scan", room="MEDBAY"),
        )
        state = dataclasses.replace(_base_world_state(), tasks=tasks)

        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )

        # ``len(world_state.tasks)`` is the exact expression
        # ``engine/win_conditions.py`` counts over, so the agent-visible total
        # equals the engine's instance total.
        assert packet.global_state.tasks_total == len(state.tasks) == 3
        assert packet.global_state.tasks_completed == 1
        assert packet.global_state.task_completion_percent == pytest.approx(1 / 3)

    def test_empty_task_pool_reports_zero_completion(self, tmp_path: Path) -> None:
        state = _base_world_state()  # tasks={}
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )

        assert packet.global_state.tasks_total == 0
        assert packet.global_state.tasks_completed == 0
        assert packet.global_state.task_completion_percent == 0.0


def test_multi_impostor_packets_carry_no_foreign_task_ownership(
    tmp_path: Path,
) -> None:
    # Per-player tasks under the 2-impostor roster (DESIGN.md §1.3, §3.2): every
    # crewmate-recipient packet must carry ONLY that crewmate's own map task and an
    # empty fellow-impostor team. A misroute of another player's task (its map id,
    # instance id, or ownership) into a crew packet would surface here, where the
    # flat single-impostor scripted fixtures cannot reach. Each crewmate owns a
    # DISTINCT map task so an owner-scope leak is unambiguous.
    #
    # The two IMPOSTORS (p-2, p-4) own NO task instance -- production seeds tasks
    # to crewmates only -- so they carry a deterministic PRETEND map id (Task
    # 10.14 blending). The pretend id is map-derived and surfaced only on the
    # impostor's own self channel: it is never a WorldState.tasks instance (the
    # win-denominator integrity invariant) and never leaks into a crew packet.
    crew_map_id = {
        "p-1": "swipe_card",
        "p-3": "submit_scan",
        "p-5": "fuel_reserves",
    }
    task_room = {
        "swipe_card": "ADMIN",
        "submit_scan": "MEDBAY",
        "fuel_reserves": "STORAGE",
    }
    state = dataclasses.replace(
        _multi_impostor_world_state(),
        tasks=_tasks(
            *(
                _task_instance(owner=owner, map_task_id=map_id, room=task_room[map_id])
                for owner, map_id in crew_map_id.items()
            )
        ),
    )
    game_map = load_canonical_map()
    impostor_ids = ["p-2", "p-4"]
    service = _observation_service(tmp_path)

    packets = {
        player_id: service.build_packet(
            world_state=state, agent_id=player_id, engine_events=[]
        )
        for player_id in state.players
    }

    # Each impostor's deterministic pretend map id (own-seat blend target). The
    # canonical map is non-empty, so the selector never returns None here.
    impostor_pretend: dict[str, str] = {}
    for imp_id in impostor_ids:
        pretend_id = impostor_pretend_task_id(
            game_map=game_map,
            agent_id=imp_id,
            impostor_ids=impostor_ids,
            tick=state.tick,
        )
        assert pretend_id is not None
        impostor_pretend[imp_id] = pretend_id

    for crew_id in ("p-1", "p-3", "p-5"):
        packet = packets[crew_id]
        assert packet.self_state.role == "CREWMATE"
        # Own task only -- the exact map id, never the composite instance id.
        assert packet.self_state.pending_task_id == crew_map_id[crew_id]
        assert ":" not in (packet.self_state.pending_task_id or "")
        # The crew-empty fellow-impostor invariant still holds with tasks present.
        assert packet.self_state.fellow_impostor_ids == ()
        # No OTHER player's task -- crew map id OR an impostor's pretend id --
        # appears anywhere in the crew packet (the firewall both ways).
        dumped = json.dumps(packet.model_dump(mode="json"))
        foreign_ids = {
            other_map_id
            for other_id, other_map_id in crew_map_id.items()
            if other_id != crew_id
        } | set(impostor_pretend.values())
        for foreign in foreign_ids:
            assert foreign not in dumped, (
                f"{crew_id} packet leaked foreign task {foreign!r}"
            )

    # Each impostor carries its OWN pretend map id (a bare map id, never the
    # composite), continues to see exactly its fellow impostor, and -- the
    # integrity invariant -- that pretend id was NEVER minted as a
    # WorldState.tasks instance, so it cannot move the crew win denominator.
    for imp_id in impostor_ids:
        packet = packets[imp_id]
        assert packet.self_state.role == "IMPOSTOR"
        assert packet.self_state.pending_task_id == impostor_pretend[imp_id]
        assert ":" not in (packet.self_state.pending_task_id or "")
        assert f"{imp_id}:{impostor_pretend[imp_id]}" not in state.tasks
    assert packets["p-2"].self_state.fellow_impostor_ids == ("p-4",)
    assert packets["p-4"].self_state.fellow_impostor_ids == ("p-2",)


class TestImpostorPretendTaskIntegrity:
    """The blending pretend-task never advances the real task counter (Task
    10.14, DESIGN.md §3.4/§3.5; audit-2026-06-13-1816 D-D-1). The fake
    ``do_task`` renders as a do_task action and consumes the tick, but the engine
    rejects it (the impostor owns no instance), so it advances no instance and
    cannot move the CREWMATE_TASKS win denominator -- a fake task can never help
    the crew win. The inviolable invariant of the toolkit, pinned end-to-end.
    """

    def test_fake_do_task_rejected_advances_no_instance_no_denominator(
        self, tmp_path: Path
    ) -> None:
        game_map = load_canonical_map()
        base = _multi_impostor_world_state()
        impostor_ids = ["p-2", "p-4"]
        # The impostor's deterministic pretend task at this tick.
        pretend = impostor_pretend_task_id(
            game_map=game_map,
            agent_id="p-4",
            impostor_ids=impostor_ids,
            tick=base.tick,
        )
        assert pretend is not None
        pretend_room = game_map.tasks[pretend].room
        # The sharpest integrity case: a CREWMATE (p-1) owns an instance of the
        # SAME map task the impostor will pretend, co-located in the same room.
        # The impostor's fake do_task must not advance p-1's instance -- the
        # engine resolves (actor, map_task_id) to the ACTOR's own instance, and
        # the impostor owns none.
        crew_instance = _task_instance(
            owner="p-1",
            map_task_id=pretend,
            room=pretend_room,
            progress=0,
            required_ticks=3,
        )
        players = dict(base.players)
        players["p-4"] = dataclasses.replace(base.players["p-4"], room=pretend_room)
        players["p-1"] = dataclasses.replace(base.players["p-1"], room=pretend_room)
        state = dataclasses.replace(
            base,
            players=players,
            tasks=_tasks(crew_instance),
            # Cooldown up so the impostor cannot kill the co-located crewmate and
            # the tick exercises only the do_task path.
            cooldowns={"p-2": 4, "p-4": 4},
        )
        tasks_total_before = len(state.tasks)

        actions = [
            _action(
                {"type": "do_task", "actor": "p-4", "payload": {"task_id": pretend}}
            ),
            # The crew owner waits so its own instance does not progress via the
            # continuing-task path -- isolating the impostor's fake do_task.
            _action({"type": "wait", "actor": "p-1", "payload": {}}),
        ]
        next_state, events = advance_tick(state, actions, game_map=game_map)

        # The fake do_task RENDERS as a do_task action but is REJECTED for owning
        # no instance -- it consumed the tick and made no progress.
        rejections = [
            event
            for event in events
            if event.type == "ActionRejected" and event.actor == "p-4"
        ]
        assert len(rejections) == 1
        assert rejections[0].action == "do_task"
        assert "owns no task instance" in rejections[0].reason
        # No TaskProgressed/TaskCompleted event names the impostor.
        assert not [
            event
            for event in events
            if event.type in {"TaskProgressed", "TaskCompleted"}
            and getattr(event, "actor", None) == "p-4"
        ]
        # The crew owner's real instance is UNTOUCHED (the impostor is not owner).
        assert next_state.tasks[crew_instance.id].progress == 0
        assert next_state.tasks[crew_instance.id].completed is False
        # The win denominator did not move: no pretend instance was minted.
        assert len(next_state.tasks) == tasks_total_before
        assert f"p-4:{pretend}" not in next_state.tasks
        # The agent-visible global denominator is likewise unchanged.
        packet = _observation_service(tmp_path).build_packet(
            world_state=next_state, agent_id="p-1", engine_events=[]
        )
        assert packet.global_state.tasks_total == tasks_total_before
        assert packet.global_state.tasks_completed == 0
