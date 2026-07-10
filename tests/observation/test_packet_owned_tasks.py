from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from engine.entities import PlayerState, TaskState
from engine.rng import EngineRng
from engine.world import WorldState, load_canonical_map
from observation.packet import ObservationPacket, SelfView
from observation.service import (
    ObservationService,
    impostor_pretend_task_id,
    impostor_pretend_task_set,
)

# Local-builder idiom (mirrors tests/observation/test_service.py; deliberately
# NOT imported from it): the small world-state builders this module needs, kept
# self-contained so the packet-owned-task contract is pinned independently.


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
    # Four players, one impostor (p-4) -- the base 4p/1i roster.
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
    # Five players, two impostors (p-2, p-4), three crewmates (p-1, p-3, p-5) --
    # the only roster that exercises the per-seat pretend window across seats.
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


def test_crewmate_owned_task_ids_are_sorted_unfinished_map_ids(
    tmp_path: Path,
) -> None:
    # p-1 owns two unfinished instances and one completed one. ``owned_task_ids``
    # is exactly the sorted unfinished map ids (the completed one is excluded even
    # though its map id sorts first), and ``pending_task_id`` is its head.
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

    # "align_engine_output" is completed and excluded despite sorting first.
    assert packet.self_state.owned_task_ids == ("submit_scan", "swipe_card")
    for task_id in packet.self_state.owned_task_ids:
        assert ":" not in task_id
    assert packet.self_state.pending_task_id == packet.self_state.owned_task_ids[0]
    assert ":" not in (packet.self_state.pending_task_id or "")


def test_two_owners_of_one_shared_map_task_each_carry_the_shared_map_id(
    tmp_path: Path,
) -> None:
    # p-1 and p-2 each hold an INSTANCE of the same map task. Each packet carries
    # only the shared MAP id in its owned set -- no instance id, no ownership --
    # mirroring the pending-task shared-map-id contract.
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

    assert packet_one.self_state.owned_task_ids == ("swipe_card",)
    assert packet_two.self_state.owned_task_ids == ("swipe_card",)
    assert ":" not in packet_one.self_state.owned_task_ids[0]
    assert ":" not in packet_two.self_state.owned_task_ids[0]
    assert packet_one.self_state.pending_task_id == "swipe_card"
    assert packet_two.self_state.pending_task_id == "swipe_card"


def test_owned_task_ids_empty_and_pending_none_when_all_owned_complete(
    tmp_path: Path,
) -> None:
    state = dataclasses.replace(
        _base_world_state(),
        tasks=_tasks(
            _task_instance(
                owner="p-1", map_task_id="swipe_card", room="ADMIN", completed=True
            ),
            # Another player's unfinished instance must NOT surface for p-1.
            _task_instance(owner="p-2", map_task_id="submit_scan", room="MEDBAY"),
        ),
    )

    packet = _observation_service(tmp_path).build_packet(
        world_state=state, agent_id="p-1", engine_events=[]
    )

    assert packet.self_state.owned_task_ids == ()
    assert packet.self_state.pending_task_id is None


def test_owned_task_ids_never_carry_another_players_tasks(tmp_path: Path) -> None:
    # Multi-crew world with DISJOINT map ids: each crewmate carries exactly its
    # own owned set and no other player's task (its map id) appears anywhere in
    # the packet -- the owner-scope firewall (DESIGN.md §1.3, §3.2).
    crew_map_id = {
        "p-1": "swipe_card",
        "p-2": "submit_scan",
        "p-3": "fuel_reserves",
    }
    task_room = {
        "swipe_card": "ADMIN",
        "submit_scan": "MEDBAY",
        "fuel_reserves": "STORAGE",
    }
    state = dataclasses.replace(
        _base_world_state(),
        tasks=_tasks(
            *(
                _task_instance(owner=owner, map_task_id=map_id, room=task_room[map_id])
                for owner, map_id in crew_map_id.items()
            )
        ),
    )
    game_map = load_canonical_map()
    service = _observation_service(tmp_path)

    # The sole impostor's pretend window -- a foreign set no crew packet may carry.
    impostor_window = set(
        impostor_pretend_task_set(
            game_map=game_map, agent_id="p-4", impostor_ids=["p-4"]
        )
    )

    for crew_id, own_map_id in crew_map_id.items():
        packet = service.build_packet(
            world_state=state, agent_id=crew_id, engine_events=[]
        )
        assert packet.self_state.owned_task_ids == (own_map_id,)
        dumped = json.dumps(packet.model_dump(mode="json"))
        foreign = (
            {
                other_map_id
                for other_id, other_map_id in crew_map_id.items()
                if other_id != crew_id
            }
            | impostor_window
        ) - set(packet.self_state.owned_task_ids)
        for foreign_id in foreign:
            assert foreign_id not in dumped, (
                f"{crew_id} packet leaked foreign task {foreign_id!r}"
            )


def test_impostor_owned_task_ids_are_the_camouflage_window(tmp_path: Path) -> None:
    # An impostor's ``owned_task_ids`` is its per-seat camouflage window (Task
    # 10.14 blending), role-indistinguishable from a crewmate's owned set: it
    # never mints a ``WorldState.tasks`` instance, and ``pending_task_id`` rotates
    # WITHIN the window every tick.
    game_map = load_canonical_map()
    base = _base_world_state()  # sole impostor p-4
    window = impostor_pretend_task_set(
        game_map=game_map, agent_id="p-4", impostor_ids=["p-4"]
    )
    assert len(window) == min(3, len(game_map.tasks)) == 3
    service = _observation_service(tmp_path)

    # Rebuild across a full rotation (dwell=6): ticks 0/6/12 walk the window and
    # 18 wraps back, so ``pending_task_id`` must stay a member at every tick while
    # the window itself is tick-independent.
    for tick in (0, 6, 12, 18):
        state = dataclasses.replace(base, tick=tick)
        packet = service.build_packet(
            world_state=state, agent_id="p-4", engine_events=[]
        )
        assert packet.self_state.role == "IMPOSTOR"
        assert packet.self_state.owned_task_ids == window
        assert packet.self_state.pending_task_id in packet.self_state.owned_task_ids
        # The impostor owns zero real instances, and no pretend id is ever a
        # ``WorldState.tasks`` instance.
        assert not any(task.owner == "p-4" for task in state.tasks.values())
        for tid in window:
            assert f"p-4:{tid}" not in state.tasks


def test_multi_impostor_windows_are_per_seat_and_foreign_absent(
    tmp_path: Path,
) -> None:
    # 5p/2i: each impostor carries its OWN seat window; the other impostor's
    # window ids (minus any shared with its own) are absent from its packet dump.
    game_map = load_canonical_map()
    state = _multi_impostor_world_state()
    impostor_ids = ["p-2", "p-4"]
    service = _observation_service(tmp_path)

    windows = {
        imp: impostor_pretend_task_set(
            game_map=game_map, agent_id=imp, impostor_ids=impostor_ids
        )
        for imp in impostor_ids
    }
    # The two seats draw disjoint windows.
    assert set(windows["p-2"]).isdisjoint(windows["p-4"])

    for imp in impostor_ids:
        packet = service.build_packet(world_state=state, agent_id=imp, engine_events=[])
        assert packet.self_state.owned_task_ids == windows[imp]
        dumped = json.dumps(packet.model_dump(mode="json"))
        other = next(o for o in impostor_ids if o != imp)
        foreign = set(windows[other]) - set(windows[imp])
        for foreign_id in foreign:
            assert foreign_id not in dumped, (
                f"{imp} packet leaked seat window id {foreign_id!r}"
            )


def test_impostor_pretend_task_set_is_sorted_and_rotation_member_for_every_seat() -> (
    None
):
    # For 1..4 impostors, every seat's camouflage set is sorted ascending with no
    # duplicates, and every id the rotating selector returns over a full 25-tick
    # sweep is a member of the set -- the set/rotator cannot drift.
    game_map = load_canonical_map()
    for num_impostors in range(1, 5):
        impostor_ids = [f"p-{index}" for index in range(1, num_impostors + 1)]
        for agent_id in impostor_ids:
            camouflage = impostor_pretend_task_set(
                game_map=game_map, agent_id=agent_id, impostor_ids=impostor_ids
            )
            assert camouflage == tuple(sorted(camouflage))
            assert len(set(camouflage)) == len(camouflage)
            assert len(camouflage) == min(3, len(game_map.tasks))
            for tick in range(25):
                rotating = impostor_pretend_task_id(
                    game_map=game_map,
                    agent_id=agent_id,
                    impostor_ids=impostor_ids,
                    tick=tick,
                )
                assert rotating is not None
                assert rotating in camouflage


def test_pre_widening_bytes_reconstruct_with_default_empty(tmp_path: Path) -> None:
    # Byte discipline (additive field): pre-widening bytes -- a SelfView / packet
    # dict with NO ``owned_task_ids`` key -- reconstruct with the ``()`` default.
    self_view = SelfView.model_validate(
        {"room": "ADMIN", "role": "CREWMATE", "pending_task_id": None}
    )
    assert self_view.owned_task_ids == ()

    pre_widening_packet = {
        "tick": 0,
        "agent_id": "p-1",
        "self_state": {"room": "ADMIN", "role": "CREWMATE", "pending_task_id": None},
        "visible_players": [],
        "visible_bodies": [],
        "audible_events": [],
        "global_state": {
            "tasks_completed": 0,
            "tasks_total": 1,
            "task_completion_percent": 0.0,
            "sabotage_active": False,
            "sabotage_kind": None,
        },
        "cooldown": None,
    }
    reconstructed = ObservationPacket.model_validate(pre_widening_packet)
    assert reconstructed.self_state.owned_task_ids == ()

    # Round-trip a service-built packet: dump -> reload is byte-stable.
    state = dataclasses.replace(
        _base_world_state(),
        tasks=_tasks(
            _task_instance(owner="p-1", map_task_id="swipe_card", room="ADMIN"),
        ),
    )
    packet = _observation_service(tmp_path).build_packet(
        world_state=state, agent_id="p-1", engine_events=[]
    )
    assert ObservationPacket.model_validate_json(packet.model_dump_json()) == packet


def test_owned_task_ids_always_serialize(tmp_path: Path) -> None:
    # Unlike ``moved_players`` (omit-when-empty), ``owned_task_ids`` ALWAYS
    # serializes -- present as a list of strings on every SelfView dump, and as an
    # empty list even when the recipient owns nothing.
    game_map = load_canonical_map()
    service = _observation_service(tmp_path)

    crew_state = dataclasses.replace(
        _base_world_state(),
        tasks=_tasks(
            _task_instance(owner="p-1", map_task_id="swipe_card", room="ADMIN"),
        ),
    )
    crew_dump = service.build_packet(
        world_state=crew_state, agent_id="p-1", engine_events=[]
    ).model_dump(mode="json")
    assert "owned_task_ids" in crew_dump["self_state"]
    assert crew_dump["self_state"]["owned_task_ids"] == ["swipe_card"]
    assert all(
        isinstance(tid, str) for tid in crew_dump["self_state"]["owned_task_ids"]
    )

    impostor_dump = service.build_packet(
        world_state=crew_state, agent_id="p-4", engine_events=[]
    ).model_dump(mode="json")
    assert "owned_task_ids" in impostor_dump["self_state"]
    assert impostor_dump["self_state"]["owned_task_ids"] == list(
        impostor_pretend_task_set(
            game_map=game_map, agent_id="p-4", impostor_ids=["p-4"]
        )
    )

    # Empty case: all owned tasks complete -> still serializes an empty list.
    all_complete_state = dataclasses.replace(
        _base_world_state(),
        tasks=_tasks(
            _task_instance(
                owner="p-1", map_task_id="swipe_card", room="ADMIN", completed=True
            ),
        ),
    )
    empty_dump = service.build_packet(
        world_state=all_complete_state, agent_id="p-1", engine_events=[]
    ).model_dump(mode="json")
    assert empty_dump["self_state"]["owned_task_ids"] == []
