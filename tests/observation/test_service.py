from __future__ import annotations

import dataclasses
from collections.abc import Sequence
import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import BodyState, PlayerState, SabotageState, TaskState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from observation.packet import MovedPlayerView, PlayerView
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
    # Under asymmetric visibility (Task 13.8) a crewmate sees only its OWN room
    # at base, so the observer cannot witness the STORAGE kill from one room
    # away. It sits in ENGINEERING while p-4 kills p-1 in adjacent STORAGE, then
    # walks INTO STORAGE the next tick: it now sees the killer co-located, but
    # the kill was a PRIOR tick, so the visible-player action must stay None.
    state = _base_world_state()
    players = dict(state.players)
    players["p-2"] = _player("p-2", "CREWMATE", "ENGINEERING", (0.0, 0.0))
    state = dataclasses.replace(state, players=players)
    state, _ = advance_tick(
        state,
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
                    "payload": {"to_room": "STORAGE"},
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


def test_self_view_carries_in_vent_only_for_the_recipient(tmp_path: Path) -> None:
    # Task 11.1 (DESIGN.md §1.3, §3.4): ``SelfView.in_vent`` mirrors the
    # recipient's OWN ``PlayerState.in_vent``. A vented impostor sees ``in_vent``
    # True on its own packet; every other agent's packet carries its own value
    # (False here). The field rides only the privileged self channel -- a vented
    # player is hidden from others' ``visible_players`` -- so it never leaks onto
    # the crew-visible channel (asserted by the leak-property sweep).
    state = _base_world_state()
    players = dict(state.players)
    players["p-4"] = dataclasses.replace(players["p-4"], in_vent=True)
    state = dataclasses.replace(state, players=players)
    service = _observation_service(tmp_path)

    impostor_packet = service.build_packet(
        world_state=state, agent_id="p-4", engine_events=[]
    )
    crew_packet = service.build_packet(
        world_state=state, agent_id="p-1", engine_events=[]
    )

    assert impostor_packet.self_state.in_vent is True
    assert crew_packet.self_state.in_vent is False


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
    # See test_visible_player_action_does_not_reveal_unseen_kill: under Task 13.8
    # asymmetric visibility the crewmate observer is room-only at base, so it
    # cannot witness the adjacent-room kill — it walks INTO STORAGE to stand with
    # the killer the next tick, where the (prior-tick) kill stays sanitized.
    state = _base_world_state()
    players = dict(state.players)
    players["p-2"] = _player("p-2", "CREWMATE", "ENGINEERING", (0.0, 0.0))
    state = dataclasses.replace(state, players=players)
    state, _ = advance_tick(
        state,
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
                    "payload": {"to_room": "STORAGE"},
                }
            )
        ],
        game_map=game_map,
    )
    state_with_bad_cooldown = dataclasses.replace(
        state, cooldowns={**dict(state.cooldowns), "p-2": 7}
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
    # Both bodies sit in the observer's OWN room (REACTOR): a crewmate is
    # room-only at base under asymmetric visibility (Task 13.8), so co-locating
    # them keeps two bodies in view to exercise the multi-body path.
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
            room="REACTOR",
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


class TestImpostorPretendTaskSelector:
    """The pretend-task selector contract (Task 10.14; Codex review, PR #155)."""

    def test_pretend_set_is_disjoint_across_seats_and_deterministic(self) -> None:
        # Disjoint per-seat windows so two impostors never pretend the SAME task in
        # lockstep, and a pure function of (map, seat, tick) -- deterministic /
        # replay-safe.
        game_map = load_canonical_map()
        impostor_ids = ["p-2", "p-4"]
        a = impostor_pretend_task_id(
            game_map=game_map, agent_id="p-2", impostor_ids=impostor_ids, tick=0
        )
        b = impostor_pretend_task_id(
            game_map=game_map, agent_id="p-4", impostor_ids=impostor_ids, tick=0
        )
        assert a is not None and b is not None
        assert a != b
        # Same inputs -> same id (no RNG, no module state).
        assert (
            impostor_pretend_task_id(
                game_map=game_map, agent_id="p-2", impostor_ids=impostor_ids, tick=0
            )
            == a
        )

    def test_pretend_task_rotates_through_a_per_seat_set(self) -> None:
        # The blend roams: across dwell boundaries the pretend id advances through
        # the seat's set (so the impostor moves room-to-room, not camps one).
        game_map = load_canonical_map()
        seen = {
            impostor_pretend_task_id(
                game_map=game_map,
                agent_id="p-2",
                impostor_ids=["p-2", "p-4"],
                tick=t,
            )
            for t in range(0, 6 * 3, 6)  # one tick per dwell window
        }
        assert len(seen) > 1  # more than one distinct task over the rotation

    def test_pretend_task_raises_for_non_member_agent(self) -> None:
        # Fail-loud (no silent fallback): a non-member agent id is a caller wiring
        # error, not a seat-0 default.
        game_map = load_canonical_map()
        with pytest.raises(ValueError, match="not in impostor_ids"):
            impostor_pretend_task_id(
                game_map=game_map,
                agent_id="p-9",
                impostor_ids=["p-2", "p-4"],
                tick=0,
            )


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


class TestGlobalViewSabotageRepairChannel:
    """The public, role-blind repair channel (Task 11.5, DESIGN.md §8.3): the two
    new ``GlobalView`` fields populate only while a sabotage is active, read from
    the map definition, and are identical across every role (leak-clean)."""

    def _sabotage(self, kind: str, *, active: bool = True) -> SabotageState:
        return SabotageState(
            kind=kind,
            remaining_ticks=5,
            affected_rooms=(),
            active=active,
        )

    def test_fields_default_empty_when_no_sabotage(self, tmp_path: Path) -> None:
        packet = _observation_service(tmp_path).build_packet(
            world_state=_base_world_state(), agent_id="p-1", engine_events=[]
        )
        assert packet.global_state.sabotage_active is False
        assert packet.global_state.sabotage_repair_rooms == ()
        assert packet.global_state.sabotage_is_gating is False

    def test_gating_reactor_populates_repair_rooms_and_flag(
        self, tmp_path: Path
    ) -> None:
        state = dataclasses.replace(
            _base_world_state(), sabotage=self._sabotage("reactor")
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )
        assert packet.global_state.sabotage_active is True
        assert packet.global_state.sabotage_repair_rooms == ("REACTOR", "ENGINEERING")
        assert packet.global_state.sabotage_is_gating is True

    def test_non_gating_lights_surfaces_repair_rooms_without_gating(
        self, tmp_path: Path
    ) -> None:
        state = dataclasses.replace(
            _base_world_state(), sabotage=self._sabotage("lights")
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )
        assert packet.global_state.sabotage_repair_rooms == ("ADMIN",)
        assert packet.global_state.sabotage_is_gating is False

    def test_inactive_sabotage_leaves_fields_default(self, tmp_path: Path) -> None:
        state = dataclasses.replace(
            _base_world_state(),
            sabotage=self._sabotage("reactor", active=False),
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=[]
        )
        assert packet.global_state.sabotage_active is False
        assert packet.global_state.sabotage_repair_rooms == ()
        assert packet.global_state.sabotage_is_gating is False

    def test_repair_channel_is_role_invariant(self, tmp_path: Path) -> None:
        # Identical across crew and impostor recipients -- the channel is public.
        state = dataclasses.replace(
            _multi_impostor_world_state(), sabotage=self._sabotage("reactor")
        )
        service = _observation_service(tmp_path)
        views = [
            service.build_packet(
                world_state=state, agent_id=player_id, engine_events=[]
            ).global_state
            for player_id in state.players
        ]
        assert all(
            view.sabotage_repair_rooms == ("REACTOR", "ENGINEERING") for view in views
        )
        assert all(view.sabotage_is_gating is True for view in views)


def _observed_activity_world(*, seed: int = 99) -> WorldState:
    """A STORAGE scene for the Task 13.9 observed-activity (fake-task) lever.

    ``p-1`` (crew) and ``p-3`` (impostor) stand in STORAGE; ``p-2`` (crew) owns
    the STORAGE map task ``fuel_reserves`` and performs it for real while ``p-3``
    submits a pretend ``do_task`` the engine REJECTS (impostors own no instance).
    ``p-4`` (crew) sits in REACTOR -- room-only and non-adjacent to STORAGE -- as
    the can't-see control, and ``p-5`` (impostor) sits in ENGINEERING, the one
    room adjacent to STORAGE, so an adjacent-vision observer is exercised too.
    """

    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "p-1": _player("p-1", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "p-2": _player("p-2", "CREWMATE", "STORAGE", (1.0, 0.0)),
            "p-3": _player("p-3", "IMPOSTOR", "STORAGE", (2.0, 0.0)),
            "p-4": _player("p-4", "CREWMATE", "REACTOR", (0.0, 0.0)),
            "p-5": _player("p-5", "IMPOSTOR", "ENGINEERING", (0.0, 0.0)),
        },
        bodies={},
        tasks=_tasks(
            _task_instance(
                owner="p-2",
                map_task_id="fuel_reserves",
                room="STORAGE",
                required_ticks=6,
            ),
        ),
        sabotage=None,
        cooldowns={"p-3": 0, "p-5": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


def _do_task(actor: str, map_task_id: str = "fuel_reserves") -> Action:
    return _action(
        {"type": "do_task", "actor": actor, "payload": {"task_id": map_task_id}}
    )


class TestObservedActivityTaskLever:
    """The Task 13.9 observed-activity enrichment (the fake-task lever, DESIGN.md
    §1.3; the Wave-C smoke finding). A ``do_task`` a visible player submits this
    tick stamps ``PlayerView.action="task"``: vision-gated, role-blind, and
    BYTE-IDENTICAL whether the engine RESOLVED it (a crewmate's real task) or
    REJECTED it (an impostor's instance-less pretend task) -- the cover mechanic
    and the deduction surface in one. ``kill``/``vent`` stay resolved-witness-gated
    so a rejected kill can never surface.
    """

    def test_visible_real_and_pretend_task_render_byte_identical(
        self, tmp_path: Path
    ) -> None:
        game_map = load_canonical_map()
        state, events = advance_tick(
            _observed_activity_world(),
            [_do_task("p-2"), _do_task("p-3")],
            game_map=game_map,
        )

        # The two do_tasks resolved DIFFERENTLY in the engine: the crewmate
        # progressed, the impostor's pretend task was rejected for owning no
        # instance. The render below must erase that difference entirely.
        assert any(
            event.type == "TaskProgressed" and event.actor == "p-2" for event in events
        )
        assert any(
            event.type == "ActionRejected"
            and event.actor == "p-3"
            and event.action == "do_task"
            for event in events
        )

        service = _observation_service(tmp_path)
        # Every observer who can see STORAGE: the crew room-only observer (p-1,
        # co-located) and the impostor adjacent-vision observer (p-5, next door).
        for observer in ("p-1", "p-5"):
            packet = service.build_packet(
                world_state=state, agent_id=observer, engine_events=events
            )
            crew_view = _visible_player("p-2", packet.visible_players)
            impostor_view = _visible_player("p-3", packet.visible_players)
            assert crew_view.action == "task"
            assert impostor_view.action == "task"
            # Byte-identical except the id: no role leaks through room or action.
            assert crew_view.model_dump(exclude={"id"}) == impostor_view.model_dump(
                exclude={"id"}
            )
            assert crew_view.model_dump(exclude={"id"}) == {
                "room": "STORAGE",
                "action": "task",
            }

    def test_completed_do_task_also_stamps_task(self, tmp_path: Path) -> None:
        # A do_task that COMPLETES (TaskCompleted, not TaskProgressed) still reads
        # as "task" to the observer -- resolution shape is invisible at the boundary.
        game_map = load_canonical_map()
        base = _observed_activity_world()
        tasks = _tasks(
            _task_instance(
                owner="p-2",
                map_task_id="fuel_reserves",
                room="STORAGE",
                required_ticks=1,
            )
        )
        state, events = advance_tick(
            dataclasses.replace(base, tasks=tasks),
            [_do_task("p-2")],
            game_map=game_map,
        )
        assert any(
            event.type == "TaskCompleted" and event.actor == "p-2" for event in events
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert _visible_player("p-2", packet.visible_players).action == "task"

    def test_continuing_task_stamps_task_without_resubmission(
        self, tmp_path: Path
    ) -> None:
        # The annotation tracks task ACTIVITY, not just the submission tick: a
        # multi-tick task continued by the engine (no fresh do_task) still emits a
        # TaskProgressed each tick, so a stationary observer keeps seeing "task".
        game_map = load_canonical_map()
        state, _ = advance_tick(
            _observed_activity_world(), [_do_task("p-2")], game_map=game_map
        )
        state, events = advance_tick(state, [], game_map=game_map)
        assert any(
            event.type == "TaskProgressed" and event.actor == "p-2" for event in events
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert _visible_player("p-2", packet.visible_players).action == "task"

    def test_task_is_vision_gated_not_surfaced_to_a_blind_observer(
        self, tmp_path: Path
    ) -> None:
        # p-4 is a room-only crewmate in REACTOR, which is NOT adjacent to STORAGE,
        # so it cannot see the STORAGE task-doers at all -- the annotation surfaces
        # no one the observer could not already see (it never ADDS a visible
        # player, unlike the witness-gated kill/vent channel).
        game_map = load_canonical_map()
        state, events = advance_tick(
            _observed_activity_world(),
            [_do_task("p-2"), _do_task("p-3")],
            game_map=game_map,
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-4", engine_events=events
        )
        visible_ids = {player.id for player in packet.visible_players}
        assert "p-2" not in visible_ids
        assert "p-3" not in visible_ids

    def test_rejected_kill_never_surfaces_as_a_visible_action(
        self, tmp_path: Path
    ) -> None:
        # The firewall edge: a do_task rejection surfaces as "task", but a KILL
        # rejection must NEVER surface (it would leak the actor's impostor-only
        # intent). p-3 is on cooldown, so its kill is rejected the same way the
        # pretend task is -- yet the observer sees action=None, not "kill"/"task".
        game_map = load_canonical_map()
        base = _observed_activity_world()
        state = dataclasses.replace(base, cooldowns={**dict(base.cooldowns), "p-3": 5})
        state, events = advance_tick(
            state,
            [_action({"type": "kill", "actor": "p-3", "payload": {"target": "p-2"}})],
            game_map=game_map,
        )
        assert any(
            event.type == "ActionRejected"
            and event.actor == "p-3"
            and event.action == "kill"
            for event in events
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert _visible_player("p-3", packet.visible_players).action is None


def _move(actor: str, to_room: str) -> Action:
    return _action({"type": "move", "actor": actor, "payload": {"to_room": to_room}})


def _movement_world(*, seed: int = 11) -> WorldState:
    # A roster wired for the movement-perception witness gate (Task 13.5.4). A
    # transition is witnessed by an observer who could see the DEPARTURE room
    # (Codex P2): the observer p-1 sits in STORAGE alongside the movers p-2 / p-4,
    # so it sees them LEAVE STORAGE (the departure); p-3 sits in ADMIN and cannot
    # see STORAGE, so it never witnesses those transits. ENGINEERING is the shared
    # destination (adjacent to STORAGE), and an observer who only saw the ARRIVAL
    # there must NOT receive the move (test_move_not_surfaced_for_arrival_only).
    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "p-1": _player("p-1", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "p-2": _player("p-2", "CREWMATE", "STORAGE", (0.0, 0.0)),
            "p-3": _player("p-3", "CREWMATE", "ADMIN", (0.0, 0.0)),
            "p-4": _player("p-4", "IMPOSTOR", "STORAGE", (1.0, 0.0)),
            # Arrival-only observer: sits in the shared DESTINATION, so it sees
            # the movers arrive but never saw them leave STORAGE.
            "p-5": _player("p-5", "CREWMATE", "ENGINEERING", (2.0, 0.0)),
        },
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={"p-4": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


class TestMovementPerception:
    """Witness gate + flag boundary for perceived room transitions (Task 13.5.4)."""

    def test_flag_default_off_and_env_parsing(self) -> None:
        from observation.service import movement_perception_enabled

        assert movement_perception_enabled({}) is False
        assert movement_perception_enabled({"AILIBI_MOVEMENT_PERCEPTION": ""}) is False
        assert (
            movement_perception_enabled({"AILIBI_MOVEMENT_PERCEPTION": "nope"}) is False
        )
        for truthy in ("1", "true", "TRUE", "yes", "on"):
            assert movement_perception_enabled(
                {"AILIBI_MOVEMENT_PERCEPTION": truthy}
            ), truthy

    def test_witnessed_move_surfaces_for_co_located_observer(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        game_map = load_canonical_map()
        state, events = advance_tick(
            _movement_world(),
            [_move("p-2", "ENGINEERING")],
            game_map=game_map,
        )
        assert any(
            event.type == "Moved"
            and event.actor == "p-2"
            and event.from_room == "STORAGE"
            and event.to_room == "ENGINEERING"
            for event in events
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert packet.moved_players == (
            MovedPlayerView(id="p-2", from_room="STORAGE", to_room="ENGINEERING"),
        )

    def test_move_not_surfaced_for_observer_who_cannot_see_actor(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The witness gate (identical to ``saw_player``): p-3 in ADMIN cannot see
        # ENGINEERING, so p-2's transit must NEVER reach p-3's packet -- the §4.7
        # firewall / leak invariant the task pins as the hard gate.
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        game_map = load_canonical_map()
        state, events = advance_tick(
            _movement_world(),
            [_move("p-2", "ENGINEERING")],
            game_map=game_map,
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-3", engine_events=events
        )
        assert packet.moved_players == ()

    def test_no_op_same_room_move_is_not_a_transition(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        game_map = load_canonical_map()
        # p-2 "moves" to the room it is already in: a MovedEvent with from==to,
        # which is not a transition and must not surface.
        state, events = advance_tick(
            _movement_world(),
            [_move("p-2", "STORAGE")],
            game_map=game_map,
        )
        # p-1 cannot see STORAGE-resident p-2 anyway; assert from the perspective
        # of an observer co-located with p-2 to isolate the from==to skip.
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert packet.moved_players == ()

    def test_multiple_witnessed_moves_are_sorted_by_actor_id(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        game_map = load_canonical_map()
        # p-2 and p-4 both LEAVE STORAGE (where observer p-1 waits and witnesses
        # both departures) for ENGINEERING; the packet lists them deterministically
        # by actor id.
        state, events = advance_tick(
            _movement_world(),
            [_move("p-2", "ENGINEERING"), _move("p-4", "ENGINEERING")],
            game_map=game_map,
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert packet.moved_players == (
            MovedPlayerView(id="p-2", from_room="STORAGE", to_room="ENGINEERING"),
            MovedPlayerView(id="p-4", from_room="STORAGE", to_room="ENGINEERING"),
        )

    def test_move_not_surfaced_for_arrival_only_observer(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Witness the DEPARTURE, not the post-move position (Codex P2): p-5 sits in
        # the DESTINATION (ENGINEERING) and sees p-2 ARRIVE, but never saw it leave
        # STORAGE, so the transition (and its STORAGE origin) must NOT reach p-5 --
        # it still gets the plain ``saw_player`` for p-2 in ENGINEERING, just no
        # movement with an origin it did not witness.
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        game_map = load_canonical_map()
        state, events = advance_tick(
            _movement_world(),
            [_move("p-2", "ENGINEERING")],
            game_map=game_map,
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-5", engine_events=events
        )
        assert packet.moved_players == ()
        # The arrival itself is still seen via the ordinary sighting channel.
        assert any(view.id == "p-2" for view in packet.visible_players)

    def test_flag_off_packet_dump_omits_moved_players(self, tmp_path: Path) -> None:
        # Codex P2 byte-identity: the audit log writes ``packet.model_dump(mode=
        # "json")`` verbatim (observation/audit.py), so a flag-OFF packet must NOT
        # carry ``"moved_players": []`` -- that would diverge from pre-task HEAD
        # with no re-record. The empty default is omitted from serialization.
        game_map = load_canonical_map()
        state, events = advance_tick(
            _movement_world(), [_move("p-2", "ENGINEERING")], game_map=game_map
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert "moved_players" not in packet.model_dump(mode="json")

    def test_flag_on_packet_dump_includes_witnessed_moves(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # When the lever is ON and a transition was witnessed, the non-empty tuple
        # serializes normally (the observer p-1 sees p-2 leave STORAGE).
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        game_map = load_canonical_map()
        state, events = advance_tick(
            _movement_world(), [_move("p-2", "ENGINEERING")], game_map=game_map
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert packet.model_dump(mode="json")["moved_players"] == [
            {"id": "p-2", "from_room": "STORAGE", "to_room": "ENGINEERING"}
        ]

    def test_flag_off_yields_no_moved_players(self, tmp_path: Path) -> None:
        # No env set (default OFF): a witnessed transition produces an EMPTY
        # ``moved_players`` -- the byte-identity boundary with pre-task HEAD.
        game_map = load_canonical_map()
        state, events = advance_tick(
            _movement_world(),
            [_move("p-2", "ENGINEERING")],
            game_map=game_map,
        )
        packet = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert packet.moved_players == ()

    def test_movement_signal_is_replay_deterministic(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Re-deriving from the SAME recorded ``MovedEvent`` yields an identical
        # packet -- the replay-determinism contract (committed replays
        # reconstruct byte-identically).
        monkeypatch.setenv("AILIBI_MOVEMENT_PERCEPTION", "1")
        game_map = load_canonical_map()
        state, events = advance_tick(
            _movement_world(),
            [_move("p-2", "ENGINEERING")],
            game_map=game_map,
        )
        first = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        second = _observation_service(tmp_path).build_packet(
            world_state=state, agent_id="p-1", engine_events=events
        )
        assert first.moved_players == second.moved_players
        assert first.model_dump(mode="json") == second.model_dump(mode="json")
