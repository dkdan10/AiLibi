from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import replace
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from engine.entities import BodyState, PlayerId, PlayerState, Role
from engine.world import Map, WorldState, load_canonical_map
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import (
    DEFAULT_NUM_PLAYERS,
    HeadlessGame,
    HeadlessGameResult,
    TacticalAgent,
    build_default_agent_factory,
)
from orchestrator.replay import read_replay_entries
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

_INTENT_ADAPTER: TypeAdapter[ActionIntent] = TypeAdapter(ActionIntent)


def _intent(data: object) -> ActionIntent:
    return _INTENT_ADAPTER.validate_python(data)


class _ScriptedAgent:
    """Test-only agent that replays a fixed intent sequence.

    Captures every packet and public-map view it receives so tests can
    assert the orchestrator dispatched only engine-free types.
    """

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        intents: Iterable[ActionIntent] = (),
    ) -> None:
        self._agent_id = agent_id
        self._intents = list(intents)
        self._default = _intent({"type": "wait", "actor": agent_id, "payload": {}})
        self._cursor = 0
        self.received_packets: list[ObservationPacket] = []
        self.received_public_maps: list[PublicMapView] = []

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        self.received_packets.append(packet)
        self.received_public_maps.append(public_map)
        if self._cursor < len(self._intents):
            intent = self._intents[self._cursor]
            self._cursor += 1
            return intent
        return self._default


def _wait_factory(
    seen: dict[PlayerId, _ScriptedAgent],
) -> Callable[[PlayerId, Role], _ScriptedAgent]:
    def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        agent = _ScriptedAgent(agent_id=agent_id)
        seen[agent_id] = agent
        return agent

    return factory


def _override_seeder(monkeypatch: pytest.MonkeyPatch, *, state: WorldState) -> None:
    """Install a stub `seed_initial_state` that returns ``state`` verbatim.

    `HeadlessGame` constructs its initial state by calling
    `seed_initial_state`; this lets a test pre-seed a specific scenario
    without adding API surface to the orchestrator.
    """

    def _stub(
        *, seed: int, game_map: Map, num_players: int, num_impostors: int = 1
    ) -> WorldState:
        return state

    monkeypatch.setattr("orchestrator.game.seed_initial_state", _stub)


def test_headless_game_records_one_replay_entry_per_tick(tmp_path: Path) -> None:
    replay_path = tmp_path / "replay.jsonl"
    game = HeadlessGame(
        seed=42,
        game_map=load_canonical_map(),
        agent_factory=_wait_factory({}),
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=5),
    )

    result = game.run()
    entries = read_replay_entries(replay_path)

    assert result.outcome == "TICK_BUDGET_REACHED"
    assert result.final_state.tick == 5
    assert [entry.tick for entry in entries] == [0, 1, 2, 3, 4]
    assert all(entry.game_id == "headless-seed-42" for entry in entries)


def test_headless_game_dispatches_only_public_types_to_agents(
    tmp_path: Path,
) -> None:
    replay_path = tmp_path / "replay.jsonl"
    seen: dict[PlayerId, _ScriptedAgent] = {}
    game = HeadlessGame(
        seed=42,
        game_map=load_canonical_map(),
        agent_factory=_wait_factory(seen),
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=2),
    )

    game.run()

    assert set(seen) == {"p-1", "p-2", "p-4", "p-3"}
    for agent in seen.values():
        assert len(agent.received_packets) == 2
        for packet in agent.received_packets:
            assert isinstance(packet, ObservationPacket)
        for public_map in agent.received_public_maps:
            assert isinstance(public_map, PublicMapView)


def test_headless_game_replay_is_byte_identical_for_same_seed(
    tmp_path: Path,
) -> None:
    first_path = tmp_path / "first.jsonl"
    second_path = tmp_path / "second.jsonl"

    for replay_path in (first_path, second_path):
        game = HeadlessGame(
            seed=42,
            game_map=load_canonical_map(),
            agent_factory=build_default_agent_factory(),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=20),
        )
        game.run()

    assert first_path.read_bytes() == second_path.read_bytes()


def test_headless_game_writes_audit_log_alongside_replay(tmp_path: Path) -> None:
    replay_path = tmp_path / "replay.jsonl"
    game = HeadlessGame(
        seed=42,
        game_map=load_canonical_map(),
        agent_factory=_wait_factory({}),
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=3),
    )

    game.run()

    audit_path = tmp_path / "replay.audit.jsonl"
    assert audit_path.exists()
    audit_lines = audit_path.read_text(encoding="utf-8").splitlines()
    # 4 alive players × 3 ticks = 12 packets.
    assert len(audit_lines) == 4 * 3


def test_headless_game_stops_when_meeting_phase_reached(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `ReportBody` intent that the engine accepts must pause the loop."""

    game_map = load_canonical_map()
    initial = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
    body_id = "body-1"
    body = BodyState(
        id=body_id,
        player_id="p-2",
        room=game_map.spawn.room,
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    state_with_body = replace(
        initial,
        bodies={body_id: body},
        players={
            **initial.players,
            "p-2": replace(initial.players["p-2"], alive=False),
        },
    )
    _override_seeder(monkeypatch, state=state_with_body)

    def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        if agent_id == "p-1":
            return _ScriptedAgent(
                agent_id=agent_id,
                intents=[
                    _intent(
                        {
                            "type": "report",
                            "actor": "p-1",
                            "payload": {"body_id": body_id},
                        }
                    )
                ],
            )
        return _ScriptedAgent(agent_id=agent_id)

    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=tmp_path / "meeting.jsonl",
        scheduler=TickScheduler(max_ticks=5),
    )
    result = game.run()

    assert result.outcome == "MEETING_PHASE_REACHED"
    assert result.final_state.phase == "MEETING"
    assert result.final_state.bodies[body_id].discovered_by == "p-1"


def test_headless_game_emits_crewmates_outcome_when_all_tasks_complete(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When all assigned tasks complete, the engine emits a CREWMATES GameOver."""

    game_map = load_canonical_map()
    initial = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
    completable_tasks = {
        task_id: replace(task, progress=task.required_ticks - 1)
        for task_id, task in initial.tasks.items()
    }
    seeded_players: dict[PlayerId, PlayerState] = dict(initial.players)
    for task in completable_tasks.values():
        owner = task.owner
        seeded_players[owner] = replace(seeded_players[owner], room=task.room)
    pre_state = replace(initial, players=seeded_players, tasks=completable_tasks)
    _override_seeder(monkeypatch, state=pre_state)

    def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        owned = [
            task_id
            for task_id, task in completable_tasks.items()
            if task.owner == agent_id
        ]
        intents: list[ActionIntent] = []
        if owned:
            intents.append(
                _intent(
                    {
                        "type": "do_task",
                        "actor": agent_id,
                        "payload": {"task_id": owned[0]},
                    }
                )
            )
        return _ScriptedAgent(agent_id=agent_id, intents=intents)

    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=tmp_path / "crew-win.jsonl",
        scheduler=TickScheduler(max_ticks=5),
    )

    result = game.run()

    assert result.outcome == "CREWMATES"
    assert result.final_state.phase == "GAME_OVER"
    assert all(task.completed for task in result.final_state.tasks.values())


def test_headless_game_emits_impostors_outcome_at_parity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two scripted kills push the engine into IMPOSTOR_PARITY → IMPOSTORS win."""

    game_map = load_canonical_map()
    initial = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
    # Cooldown 0 so consecutive kills work without waiting for cooldown decrement.
    no_cooldown_state = replace(initial, cooldowns={"p-3": 0})
    _override_seeder(monkeypatch, state=no_cooldown_state)

    def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        if agent_id == "p-3":
            # Tick 0: kill player-1 → cooldown jumps to kill_cooldown_ticks.
            # Subsequent ticks: wait for cooldown.
            return _ScriptedAgent(
                agent_id=agent_id,
                intents=[
                    _intent(
                        {
                            "type": "kill",
                            "actor": "p-3",
                            "payload": {"target": "p-1"},
                        }
                    ),
                ],
            )
        return _ScriptedAgent(agent_id=agent_id)

    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=tmp_path / "impostor-1-kill.jsonl",
        scheduler=TickScheduler(max_ticks=20),
    )
    result_after_first = game.run()

    # After a single kill: 1 impostor vs 2 crewmates, parity NOT reached.
    assert result_after_first.outcome != "IMPOSTORS"

    # Now run a second scenario with a state already at near-parity: only
    # one crewmate alive. One more kill triggers parity.
    near_parity = replace(
        initial,
        players={
            **initial.players,
            "p-2": replace(initial.players["p-2"], alive=False),
            "p-4": replace(initial.players["p-4"], alive=False),
        },
        bodies={
            "body-p-2": BodyState(
                id="body-p-2",
                player_id="p-2",
                room=game_map.spawn.room,
                position=(0.0, 0.0),
                killed_by="p-3",
                discovered_by=None,
            ),
            "body-p-4": BodyState(
                id="body-p-4",
                player_id="p-4",
                room=game_map.spawn.room,
                position=(0.0, 0.0),
                killed_by="p-3",
                discovered_by=None,
            ),
        },
        cooldowns={"p-3": 0},
    )
    monkeypatch.setattr(
        "orchestrator.game.seed_initial_state",
        lambda **_: near_parity,
    )

    def parity_factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        if agent_id == "p-3":
            return _ScriptedAgent(
                agent_id=agent_id,
                intents=[
                    _intent(
                        {
                            "type": "kill",
                            "actor": "p-3",
                            "payload": {"target": "p-1"},
                        }
                    ),
                ],
            )
        return _ScriptedAgent(agent_id=agent_id)

    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=parity_factory,
        replay_path=tmp_path / "impostor-parity.jsonl",
        scheduler=TickScheduler(max_ticks=5),
    )
    result = game.run()

    assert result.outcome == "IMPOSTORS"
    assert result.final_state.phase == "GAME_OVER"


def test_headless_game_orders_intents_through_action_boundary(
    tmp_path: Path,
) -> None:
    """The orchestrator must sort intents by the boundary's deterministic key."""

    game_map = load_canonical_map()

    def factory(agent_id: PlayerId, role: Role) -> _ScriptedAgent:
        if agent_id == "p-1":
            return _ScriptedAgent(
                agent_id=agent_id,
                intents=[
                    _intent(
                        {
                            "type": "move",
                            "actor": "p-1",
                            "payload": {"to_room": "UPPER_HALL"},
                        }
                    )
                ],
            )
        return _ScriptedAgent(agent_id=agent_id)

    replay_path = tmp_path / "ordered.jsonl"
    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=1),
    )
    game.run()

    entries = read_replay_entries(replay_path)
    assert len(entries) == 1
    actors = [action["actor"] for action in entries[0].actions]
    assert actors == sorted(actors)


def test_headless_game_default_agents_run_without_crashing(
    tmp_path: Path,
) -> None:
    replay_path = tmp_path / "default-agents.jsonl"
    game = HeadlessGame(
        seed=42,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=20),
    )

    result = game.run()
    entries = read_replay_entries(replay_path)

    assert isinstance(result, HeadlessGameResult)
    assert result.outcome in {
        "CREWMATES",
        "IMPOSTORS",
        "MEETING_PHASE_REACHED",
        "TICK_BUDGET_REACHED",
    }
    assert len(entries) >= 1
    assert result.replay_path == replay_path


def test_discovered_body_is_hidden_from_every_observer(tmp_path: Path) -> None:
    """Regression: bodies with `discovered_by` set are hidden from all packets.

    Pins today's `engine/visibility.py` behaviour: ``visible_body_ids``
    filters out any body whose ``discovered_by`` field is non-``None``,
    including for the reporter on the discovery tick. The test drives
    `ObservationService` directly so a future change in how the
    orchestrator routes observations cannot bypass the engine filter.
    """

    game_map = load_canonical_map()
    initial = seed_initial_state(seed=2026, game_map=game_map, num_players=4)

    body_id = "body-p-2-2026"
    fresh_body = BodyState(
        id=body_id,
        player_id="p-2",
        room=game_map.spawn.room,
        position=(0.0, 0.0),
        killed_by="p-3",
        discovered_by=None,
    )
    state_with_fresh_body = replace(
        initial,
        bodies={body_id: fresh_body},
        players={
            **initial.players,
            "p-2": replace(initial.players["p-2"], alive=False),
        },
    )

    audit_path = tmp_path / "discovery.audit.jsonl"
    observation_service = ObservationService(
        game_map=game_map, audit_log_path=audit_path
    )

    observer_ids = ("p-1", "p-4", "p-3")
    for observer_id in observer_ids:
        packet = observation_service.build_packet(
            world_state=state_with_fresh_body,
            agent_id=observer_id,
            engine_events=[],
        )
        assert any(body.id == body_id for body in packet.visible_bodies), (
            f"observer {observer_id} should see the undiscovered body"
        )

    discovered_body = replace(fresh_body, discovered_by="p-1")
    state_after_discovery = replace(
        state_with_fresh_body, bodies={body_id: discovered_body}
    )
    for observer_id in observer_ids:
        packet = observation_service.build_packet(
            world_state=state_after_discovery,
            agent_id=observer_id,
            engine_events=[],
        )
        assert all(body.id != body_id for body in packet.visible_bodies), (
            f"discovered body must be hidden from {observer_id}"
        )


def test_tactical_agent_rejects_packet_for_other_actor(tmp_path: Path) -> None:
    from agents.tactical.crewmate_policy import CrewmatePolicy

    agent = TacticalAgent(
        agent_id="p-1",
        policy=CrewmatePolicy(agent_id="p-1"),
    )
    game_map = load_canonical_map()
    initial = seed_initial_state(seed=2026, game_map=game_map, num_players=4)
    audit_path = tmp_path / "agent.audit.jsonl"
    observation_service = ObservationService(
        game_map=game_map, audit_log_path=audit_path
    )
    foreign_packet = observation_service.build_packet(
        world_state=initial, agent_id="p-2", engine_events=[]
    )

    with pytest.raises(ValueError, match="p-1"):
        agent.decide(foreign_packet, public_map_from_engine_map(game_map))


def test_tick_scheduler_rejects_non_positive_max_ticks() -> None:
    with pytest.raises(ValueError, match="max_ticks"):
        TickScheduler(max_ticks=0)


def test_headless_game_handles_num_players_override(tmp_path: Path) -> None:
    replay_path = tmp_path / "three-player.jsonl"
    seen: dict[PlayerId, _ScriptedAgent] = {}
    game = HeadlessGame(
        seed=2026,
        game_map=load_canonical_map(),
        agent_factory=_wait_factory(seen),
        replay_path=replay_path,
        num_players=3,
        num_impostors=1,
        scheduler=TickScheduler(max_ticks=2),
    )

    game.run()

    assert set(seen) == {"p-1", "p-2", "p-3"}


def test_headless_game_uses_default_player_count_constants() -> None:
    """The implementation hint pins 4 players / 1 impostor as the default."""

    assert DEFAULT_NUM_PLAYERS == 4
