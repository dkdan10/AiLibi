from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from engine.actions import Action
from engine.events import EngineEvent, KilledEvent
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval.leak_scan import (
    PacketContext,
    assert_no_factory_packet_leaks,
    _reconstruct_factory_records,
)
from eval.witness_entitlement import assert_event_witnesses_match_source_state
from observation.service import ObservationService
from orchestrator.seeder import seed_initial_state


def _action(kind: str, actor: str, **payload: str) -> Action:
    return TypeAdapter(Action).validate_python(
        {"type": kind, "actor": actor, "payload": payload}
    )


@pytest.mark.parametrize("moves_first", [False, True])
def test_witnesses_follow_event_order_not_the_final_snapshot(moves_first: bool) -> None:
    game_map = load_canonical_map()
    before = seed_initial_state(
        seed=0, game_map=game_map, num_players=9, num_impostors=2
    )
    impostor = next(pid for pid, p in before.players.items() if p.role == "IMPOSTOR")
    victim, observer = [
        pid for pid, p in before.players.items() if p.role == "CREWMATE"
    ][:2]
    before = replace(before, cooldowns={pid: 0 for pid in before.cooldowns})
    kill = _action("kill", impostor, target=victim)
    move = _action("move", observer, to_room="EAST_HALL")
    after, events = advance_tick(
        before, [move, kill] if moves_first else [kill, move], game_map=game_map
    )
    killed = next(event for event in events if isinstance(event, KilledEvent))
    assert (observer in killed.witnesses) is not moves_first
    assert_event_witnesses_match_source_state(
        pre_state=before, state=after, events=events, game_map=game_map
    )
    corrupted = replace(
        killed,
        witnesses=tuple(pid for pid in killed.witnesses if pid != observer)
        if not moves_first
        else tuple(sorted((*killed.witnesses, observer))),
    )
    poisoned: Sequence[EngineEvent] = [
        corrupted if event is killed else event for event in events
    ]
    with pytest.raises(AssertionError, match="kill witness entitlement"):
        assert_event_witnesses_match_source_state(
            pre_state=before, state=after, events=poisoned, game_map=game_map
        )


def test_a_witness_killed_later_keeps_the_earlier_entitlement() -> None:
    game_map = load_canonical_map()
    before = seed_initial_state(
        seed=0, game_map=game_map, num_players=9, num_impostors=2
    )
    impostors = [pid for pid, p in before.players.items() if p.role == "IMPOSTOR"]
    first, second = [pid for pid, p in before.players.items() if p.role == "CREWMATE"][
        :2
    ]
    before = replace(before, cooldowns={pid: 0 for pid in before.cooldowns})
    after, events = advance_tick(
        before,
        [
            _action("kill", impostors[0], target=first),
            _action("kill", impostors[1], target=second),
        ],
        game_map=game_map,
    )
    first_kill = next(event for event in events if isinstance(event, KilledEvent))
    assert second in first_kill.witnesses and not after.players[second].alive
    assert_event_witnesses_match_source_state(
        pre_state=before, state=after, events=events, game_map=game_map
    )


def test_factory_scan_rejects_another_crewmates_valid_task_id(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    state = seed_initial_state(
        seed=0, game_map=game_map, num_players=9, num_impostors=2
    )
    observer = next(pid for pid, p in state.players.items() if p.role == "CREWMATE")
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )
    try:
        packet = service.build_packet(
            world_state=state, agent_id=observer, engine_events=()
        )
    finally:
        service.close()
    context = PacketContext((), state, game_map)
    assert_no_factory_packet_leaks([(packet, context)])
    foreign = next(
        task.map_task_id
        for task in state.tasks.values()
        if task.owner != observer
        and task.map_task_id not in packet.self_state.owned_task_ids
    )
    poisoned = packet.model_copy(
        update={
            "self_state": packet.self_state.model_copy(
                update={"owned_task_ids": (foreign,), "pending_task_id": None}
            )
        }
    )
    with pytest.raises(AssertionError, match="engine-truth own unfinished set"):
        assert_no_factory_packet_leaks([(poisoned, context)])


def test_factory_reconstruction_checks_the_actual_engine_witness_producer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A missing witness list changes no engine hash, so strict hash equality
    # alone cannot detect this producer mutation.
    monkeypatch.setattr("engine.rules._witnesses_in_room", lambda *args, **kwargs: ())
    source = Path("replays/samples/9p2i/replay-seed-23.jsonl")
    with pytest.raises(AssertionError, match="witness entitlement"):
        _reconstruct_factory_records(
            source,
            game_map=load_canonical_map(),
            seed=23,
            num_players=9,
            num_impostors=2,
            tasks_per_crewmate=2,
            audit_dir=tmp_path,
        )
