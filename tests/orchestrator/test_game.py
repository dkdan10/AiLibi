from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from engine.entities import BodyState, PlayerId, PlayerState, Role
from engine.world import Map, WorldState, load_canonical_map
from llm.client import CallKind, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from llm.provider import LLMCallFailure, _attach_parse_failure  # noqa: PLC2701
from meetings.manager import (
    VOTE_PARSE_DEFAULT_MARKER,
    DefaultedCall,
    LLMProviderError,
    MeetingTrigger,
    SuspicionEntry,
)
from meetings.schemas import (
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ModelAuthoredVoteBallot,
    ObservationId,
    SightingRecord,
    VentWitnessRecord,
    VoteBallot,
)
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import (
    DEFAULT_NUM_PLAYERS,
    DEFAULT_TASKS_PER_CREWMATE,
    HEADLESS_MEETING_DEADLINES,
    ROSTER_PRESETS,
    HeadlessGame,
    HeadlessGameResult,
    MeetingArtifacts,
    RosterPreset,
    TacticalAgent,
    apply_meeting_result,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import (
    FailedCallReplayEntry,
    MeetingReplayEntry,
    read_all_entries,
    read_replay_entries,
)
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
        *,
        seed: int,
        game_map: Map,
        num_players: int,
        num_impostors: int = 1,
        tasks_per_crewmate: int = 1,
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


class _ForgingAgent:
    """Test-only agent that acts as SOMEONE ELSE — the seam under test.

    ``ActionIntent.actor`` is a field the agent fills in, so nothing in the
    ``AgentInterface`` Protocol stops a decide() from naming a different seat.
    A learned mover that decodes its intent from a policy head (rather than
    copying the packet's ``agent_id``) can produce exactly this on a mask or
    decode bug, which is why the orchestrator validates it.
    """

    def __init__(self, *, agent_id: PlayerId, acting_as: PlayerId) -> None:
        self._agent_id = agent_id
        self._acting_as = acting_as

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        return _intent({"type": "wait", "actor": self._acting_as, "payload": {}})


def test_headless_game_refuses_an_intent_forging_another_actor(
    tmp_path: Path,
) -> None:
    # p-2's agent returns an intent acting as p-3. Untranslated, that action
    # would reach the engine as p-3's — moving, killing, or calling a meeting on
    # another player's behalf, recorded in the replay as that player's row. The
    # boundary refuses it loudly rather than dispatching it.
    def factory(agent_id: PlayerId, role: Role) -> _ForgingAgent | _ScriptedAgent:
        if agent_id == "p-2":
            return _ForgingAgent(agent_id=agent_id, acting_as="p-3")
        return _ScriptedAgent(agent_id=agent_id)

    game = HeadlessGame(
        seed=42,
        game_map=load_canonical_map(),
        agent_factory=factory,
        replay_path=tmp_path / "replay.jsonl",
        scheduler=TickScheduler(max_ticks=2),
    )

    with pytest.raises(ValueError) as excinfo:
        game.run()

    message = str(excinfo.value)
    # Names both seats: which agent was asked, and who it tried to act as.
    assert "'p-2'" in message
    assert "'p-3'" in message


def test_headless_game_accepts_an_intent_for_its_own_actor(tmp_path: Path) -> None:
    # The other side of the check: an agent naming ITS OWN seat is untouched by
    # the validation (the whole suite depends on this, so it is pinned here).
    def factory(agent_id: PlayerId, role: Role) -> _ForgingAgent:
        return _ForgingAgent(agent_id=agent_id, acting_as=agent_id)

    game = HeadlessGame(
        seed=42,
        game_map=load_canonical_map(),
        agent_factory=factory,
        replay_path=tmp_path / "replay.jsonl",
        scheduler=TickScheduler(max_ticks=2),
    )

    result = game.run()

    assert result.outcome == "TICK_BUDGET_REACHED"


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


def test_live_loop_refuses_incomplete_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    game = HeadlessGame(
        seed=42,
        game_map=load_canonical_map(),
        agent_factory=_wait_factory({}),
        replay_path=tmp_path / "incomplete.jsonl",
        scheduler=TickScheduler(max_ticks=1),
    )
    monkeypatch.setattr(game, "_collect_intents", lambda **kwargs: [])
    with pytest.raises(ValueError, match="every living player.*missing="):
        game.run()
    # Refusal occurs before an engine tick or a replay tick can claim execution.
    assert not (tmp_path / "incomplete.jsonl").exists()


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
        # The do_task payload carries the agent-facing MAP id (DESIGN.md §3.2),
        # which the engine resolves to this actor's own per-player instance — not
        # the composite ``"{owner}:{map_task_id}"`` dict key.
        owned = [
            task.map_task_id
            for task in completable_tasks.values()
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


def test_every_recorded_tick_row_carries_its_action_dispositions(
    tmp_path: Path,
) -> None:
    """The production recorder always hands the engine's events to the log.

    Pins the row shape a full fake-provider game writes: one disposition per
    submitted action on EVERY tick row, so the path can never silently regress
    to the omitted shape. It also pins that the class this task exists for
    actually occurs — a meeting convened mid-batch discards the actions ordered
    behind it, and those are recorded as discarded rather than as events that
    happened.
    """

    replay_path = tmp_path / "dispositions.jsonl"
    game = HeadlessGame(
        seed=0,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=replay_path,
        num_players=9,
        num_impostors=2,
        tasks_per_crewmate=DEFAULT_TASKS_PER_CREWMATE,
        scheduler=TickScheduler(max_ticks=60),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
    )
    game.run()

    entries = read_replay_entries(replay_path)
    assert entries
    for entry in entries:
        assert entry.action_dispositions is not None
        assert len(entry.action_dispositions) == len(entry.actions)

    discarded = sum(
        1
        for entry in entries
        if entry.action_dispositions is not None
        for disposition in entry.action_dispositions
        if disposition == "discarded_by_meeting"
    )
    assert discarded > 0


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


def test_headless_game_seed_0_impostor_does_not_oscillate_after_kill(
    tmp_path: Path,
) -> None:
    """R-3 integration regression (DESIGN.md §4.4).

    The audit's seed-0 reproduction had the impostor alternating
    ``ENGINEERING <-> REACTOR`` for ~30 consecutive ticks after killing
    p-4 at tick 4. Post-fix, the impostor must not exhibit that 30-
    tick alternation pattern after a confirmed kill.

    Concretely: across any 30-tick window of impostor actions that
    begins after the first ``KillAction``, do not have 30 consecutive
    ``MoveIntent`` actions whose destinations only span at most two
    distinct rooms. Either the impostor mixes in non-move actions
    (waits, kills) or the move destinations diversify beyond a 2-room
    cycle.
    """

    replay_path = tmp_path / "seed-0-regression.jsonl"
    game = HeadlessGame(
        seed=0,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=200),
    )
    result = game.run()
    entries = read_replay_entries(replay_path)

    # The default-agent impostor is the player whose final state has
    # role IMPOSTOR.
    impostor_ids = {
        player_id
        for player_id, player in result.final_state.players.items()
        if player.role == "IMPOSTOR"
    }
    assert impostor_ids, "the seed-0 game must have an impostor"
    impostor_id = next(iter(impostor_ids))

    actions_by_tick: dict[int, dict[str, str | None]] = {}
    first_kill_tick: int | None = None
    for entry in entries:
        for action in entry.actions:
            if action.get("actor") != impostor_id:
                continue
            action_type = action.get("type")
            assert isinstance(action_type, str)
            to_room: str | None = None
            if action_type == "move":
                payload = action.get("payload", {})
                assert isinstance(payload, dict)
                room_value = payload.get("to_room")
                assert isinstance(room_value, str)
                to_room = room_value
            actions_by_tick[entry.tick] = {
                "type": action_type,
                "to_room": to_room,
            }
            if action_type == "kill" and first_kill_tick is None:
                first_kill_tick = entry.tick

    assert first_kill_tick is not None, (
        "the seed-0 reproduction expects the default-agent impostor to "
        "complete at least one kill within max_ticks"
    )

    ticks_after_kill = sorted(
        tick for tick in actions_by_tick if tick > first_kill_tick
    )
    for window_start_index in range(len(ticks_after_kill)):
        window_ticks = ticks_after_kill[window_start_index : window_start_index + 30]
        if len(window_ticks) < 30:
            break
        window_actions = [actions_by_tick[tick] for tick in window_ticks]
        all_moves = all(action["type"] == "move" for action in window_actions)
        destinations: set[str] = set()
        for action in window_actions:
            destination = action["to_room"]
            if action["type"] == "move" and isinstance(destination, str):
                destinations.add(destination)
        assert not (all_moves and len(destinations) <= 2), (
            "impostor stuck in a 2-room move loop over a 30-tick window "
            f"starting at tick {window_ticks[0]}: destinations={sorted(destinations)}"
        )


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
        assert any(
            body.id == f"body-{fresh_body.player_id}" for body in packet.visible_bodies
        ), f"observer {observer_id} should see the undiscovered body"

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
        assert packet.visible_bodies == (), (
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


def _capture_seed_kwargs(
    monkeypatch: pytest.MonkeyPatch, captured: dict[str, int]
) -> None:
    """Patch ``orchestrator.game.seed_initial_state`` with a recording spy.

    The spy records ``tasks_per_crewmate`` (the value HeadlessGame threads
    through) and delegates to the real seeder so the game still runs.
    """

    def spy(
        *,
        seed: int,
        game_map: Map,
        num_players: int,
        num_impostors: int = 1,
        tasks_per_crewmate: int = 1,
    ) -> WorldState:
        captured["tasks_per_crewmate"] = tasks_per_crewmate
        return seed_initial_state(
            seed=seed,
            game_map=game_map,
            num_players=num_players,
            num_impostors=num_impostors,
            tasks_per_crewmate=tasks_per_crewmate,
        )

    monkeypatch.setattr("orchestrator.game.seed_initial_state", spy)


def test_headless_game_threads_default_tasks_per_crewmate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """HeadlessGame defaults tasks_per_crewmate to the locked harness default.

    The seeder's own parameter default is 1, but every harness caller passes the
    value explicitly; HeadlessGame's default is ``DEFAULT_TASKS_PER_CREWMATE``
    (2), so a game constructed without the kwarg seeds 2 tasks per crewmate.
    """

    captured: dict[str, int] = {}
    _capture_seed_kwargs(monkeypatch, captured)

    HeadlessGame(
        seed=2026,
        game_map=load_canonical_map(),
        agent_factory=_wait_factory({}),
        replay_path=tmp_path / "default-tpc.jsonl",
        scheduler=TickScheduler(max_ticks=1),
    ).run()

    assert captured["tasks_per_crewmate"] == DEFAULT_TASKS_PER_CREWMATE == 2


def test_headless_game_threads_explicit_tasks_per_crewmate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An explicit tasks_per_crewmate overrides the default and reaches the seeder."""

    captured: dict[str, int] = {}
    _capture_seed_kwargs(monkeypatch, captured)

    HeadlessGame(
        seed=2026,
        game_map=load_canonical_map(),
        agent_factory=_wait_factory({}),
        replay_path=tmp_path / "explicit-tpc.jsonl",
        tasks_per_crewmate=1,
        scheduler=TickScheduler(max_ticks=1),
    ).run()

    assert captured["tasks_per_crewmate"] == 1


def test_default_tasks_per_crewmate_constant_is_two() -> None:
    """The locked Phase 7 W0.1 default (diagnosis audit §3) is 2."""

    assert DEFAULT_TASKS_PER_CREWMATE == 2


def test_roster_presets_pin_baseline_and_eval_roster_configs() -> None:
    """``4p1i`` reproduces the committed baseline; ``9p2i`` is the eval roster.

    ``4p1i`` is pinned at ``tasks_per_crewmate=1`` (NOT the new default of 2) so
    it reproduces the byte-identical committed 4p/1i baseline; ``9p2i`` is the
    canonical eval roster (DESIGN.md §3.5) and carries the new default of 2.
    ``RosterPreset`` is frozen and data-only.
    """

    assert set(ROSTER_PRESETS) == {"4p1i", "9p2i"}
    assert ROSTER_PRESETS["4p1i"] == RosterPreset(
        num_players=4, num_impostors=1, tasks_per_crewmate=1
    )
    assert ROSTER_PRESETS["9p2i"] == RosterPreset(
        num_players=9, num_impostors=2, tasks_per_crewmate=2
    )

    with pytest.raises(FrozenInstanceError):
        ROSTER_PRESETS["9p2i"].num_players = 7  # type: ignore[misc]


# --- Deadline-free recording + visible deadline defaults (audit gp-2) -------


def _seed_meeting_with_body(
    monkeypatch: pytest.MonkeyPatch, *, game_map: Map, seed: int = 2026
) -> str:
    """Pre-seed a state with a corpse so a p-1 report opens a meeting at tick 0."""

    initial = seed_initial_state(seed=seed, game_map=game_map, num_players=4)
    body_id = "body-p-2-1"
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
    return body_id


def _report_then_wait_factory(
    body_id: str,
) -> Callable[[PlayerId, Role], _ScriptedAgent]:
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

    return factory


def test_build_default_meeting_runner_is_deadline_free() -> None:
    """The headless recording surface wires None deadlines (audit gp-2).

    ``MeetingDeadlines`` keeps a 30 s interactive/API default; the production
    headless runner overrides it to deadline-free at the construction site so
    recording never loses a turn to a wall-clock race.
    """

    runner = build_default_meeting_runner(llm_client=FakeProvider())

    config = runner._manager._config  # noqa: SLF001
    assert config.deadlines == HEADLESS_MEETING_DEADLINES
    assert config.deadlines.turn_seconds is None
    assert config.deadlines.vote_seconds is None


def test_explicit_config_overrides_the_headless_deadline_default() -> None:
    """An explicit config is honoured (interactive/live opts back into 30 s)."""

    from meetings.manager import MeetingConfig, MeetingDeadlines

    interactive = MeetingConfig(deadlines=MeetingDeadlines())  # 30 s defaults
    runner = build_default_meeting_runner(llm_client=FakeProvider(), config=interactive)

    config = runner._manager._config  # noqa: SLF001
    assert config.deadlines.turn_seconds == 30.0
    assert config.deadlines.vote_seconds == 30.0


class _DefaultingMeetingRunner:
    """Runner returning a SKIPPED result that carries pre-set ``defaulted_calls``.

    Isolates the orchestrator-side recording: it does not build participants
    from agents, so any agent factory works and no LLM is touched.
    """

    def __init__(self, *, defaulted_calls: tuple[DefaultedCall, ...]) -> None:
        self._defaulted_calls = defaulted_calls

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[PlayerId, object],
    ) -> MeetingArtifacts:
        result = MeetingResult(
            meeting_id=meeting_id,
            triggered_by=trigger.triggered_by,
            trigger_tick=trigger.trigger_tick,
            outcome="SKIPPED",
            ejected_player_id=None,
            ballots=(),
            contradictions=(),
            transcript=MeetingTranscript(),
        )
        return MeetingArtifacts(
            result=result,
            llm_calls=(),
            prompt_versions={"crewmate_report": "test.v0"},
            defaulted_calls=self._defaulted_calls,
        )


def test_fired_defaults_recorded_as_deadline_default_entries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each surfaced default becomes a visible failed-call marker (audit gp-2).

    Routes through the EXISTING failed-call channel as
    ``error_type="deadline_default"`` (no new record kind) and carries zero
    spend (a visibility marker, never double-counting the meeting's llm_calls).
    """

    game_map = load_canonical_map()
    body_id = _seed_meeting_with_body(monkeypatch, game_map=game_map)
    runner = _DefaultingMeetingRunner(
        defaulted_calls=(
            DefaultedCall(
                phase="opening", agent_id="p-1", trigger="validation", turn_index=0
            ),
            DefaultedCall(phase="vote", agent_id="p-3", trigger="deadline"),
        )
    )
    replay_path = tmp_path / "defaults.jsonl"
    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=_report_then_wait_factory(body_id),
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=5),
        meeting_runner=runner,
    )
    game.run()

    entries = read_all_entries(replay_path)
    meeting = next(e for e in entries if isinstance(e, MeetingReplayEntry))
    failed = [e for e in entries if isinstance(e, FailedCallReplayEntry)]

    assert len(failed) == 2
    assert all(f.error_type == "deadline_default" for f in failed)
    # Zero spend: never mistaken for a model call, never double-counted.
    assert all(f.cost_usd == 0.0 for f in failed)
    assert all(f.input_tokens == 0 and f.output_tokens == 0 for f in failed)
    # Carries the meeting id + tick (DoD); the tick matches the meeting's tick.
    assert all(f.meeting_id == meeting.meeting_id for f in failed)
    assert all(f.tick == meeting.tick for f in failed)
    # The defaulted phase + the trigger kind are named in error_message.
    messages = sorted(f.error_message for f in failed)
    assert any("opening" in m and "validation" in m and "p-1" in m for m in messages)
    assert any("vote" in m and "deadline" in m and "p-3" in m for m in messages)


class _MeetingAwareReporter:
    """Minimal MeetingAware agent: p-1 reports once at tick 0, everyone waits."""

    def __init__(
        self, *, agent_id: PlayerId, role: Role, report_body_id: str | None
    ) -> None:
        self._agent_id = agent_id
        self._role = role
        self._report_body_id = report_body_id
        self._fired = False

    def decide(
        self, packet: ObservationPacket, public_map: PublicMapView
    ) -> ActionIntent:
        if self._report_body_id is not None and not self._fired:
            self._fired = True
            return _intent(
                {
                    "type": "report",
                    "actor": self._agent_id,
                    "payload": {"body_id": self._report_body_id},
                }
            )
        return _intent({"type": "wait", "actor": self._agent_id, "payload": {}})

    def render_memory_for_meeting(
        self,
        *,
        token_budget: int = 1500,
        suspicion_override: Mapping[PlayerId, float] | None = None,
    ) -> str:
        return f"## Your role: {self._role}\nstub memory for {self._agent_id}"

    def suspicion_graph_for_meeting(self) -> tuple[SuspicionEntry, ...]:
        return ()

    def vent_witness_records_for_meeting(self) -> tuple[VentWitnessRecord, ...]:
        # Task 15.4: this double DOES cross ``_build_participants`` (it runs
        # under ``build_default_meeting_runner``), so the runtime-checkable
        # protocol requires the accessor; a canned stub grounds nothing.
        return ()

    def sighting_records_for_meeting(self) -> tuple[SightingRecord, ...]:
        # Task 16.7: the vent accessor's sighting sibling -- same protocol
        # requirement, same canned grounds-nothing stub.
        return ()

    def observation_ids_for_meeting(self) -> tuple[ObservationId, ...]:
        # Task 16.5: the stable observation-id set -- same protocol
        # requirement, same canned cites-nothing stub.
        return ()

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def role(self) -> Role:
        return self._role


class _InvalidTurnClient:
    """Real-pipeline LLM stand-in: every MeetingTurn is invalid; every vote SKIP.

    With deadline-free recording, an opening that never parses (retried once,
    still invalid) is the parse-failure path the retry guards -- exactly the
    husk the audit found. The default opening names no accusation, so the
    discussion chain terminates on it; the now-unconditional roll_call then
    gives each not-yet-spoken living player one terminal opt_in turn, which
    defaults the same way, so the opening and every opt_in turn default.
    """

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if schema is MeetingTurn:
            text = "{}"  # missing required fields -> MeetingTurn validation fails
        elif schema is ModelAuthoredVoteBallot:
            text = VoteBallot(
                voter="x",
                target="SKIP",
                confidence=0.0,
                primary_reason_id=None,
                considered_alternatives=(),
                rationale_text="skip",
            ).model_dump_json()
        else:  # pragma: no cover - defensive
            raise AssertionError(f"unexpected schema: {schema!r}")
        return LLMResponse(
            text=text,
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "invalid-turn",
        )


def test_validation_default_recorded_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Full pipeline (build_default_meeting_runner -> manager -> orchestrator).

    A deadline-free meeting whose opening never parses defaults after the one
    retry, and the orchestrator records a visible ``deadline_default`` entry --
    the audit gp-2 husk that previously left no record at all. Proves the glue:
    the manager surfaces the default, the runner forwards it, the orchestrator
    writes it.
    """

    game_map = load_canonical_map()
    body_id = _seed_meeting_with_body(monkeypatch, game_map=game_map)

    def factory(agent_id: PlayerId, role: Role) -> _MeetingAwareReporter:
        return _MeetingAwareReporter(
            agent_id=agent_id,
            role=role,
            report_body_id=body_id if agent_id == "p-1" else None,
        )

    runner = build_default_meeting_runner(llm_client=_InvalidTurnClient())
    replay_path = tmp_path / "e2e-default.jsonl"
    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=6),
        meeting_runner=runner,
    )
    game.run()

    entries = read_all_entries(replay_path)
    meeting = next(e for e in entries if isinstance(e, MeetingReplayEntry))
    failed = [e for e in entries if isinstance(e, FailedCallReplayEntry)]

    # The husk opening defaulted; roll_call is now unconditional, so each
    # not-yet-spoken living player also takes a terminal opt_in turn that
    # defaults the same way -> opening + opt_in visible deadline_default entries.
    assert meeting.outcome == "SKIPPED"
    assert len(failed) == 3
    entry = failed[0]
    assert entry.error_type == "deadline_default"
    assert "opening" in entry.error_message
    assert "validation" in entry.error_message
    # Zero spend on the marker; the turns' real spend stays in the meeting's
    # llm_calls -- the opening is retried once (two "{}" attempts) and each of
    # the two terminal opt_in turns is attempted once ("{}"), so it is not
    # double-counted.
    assert entry.cost_usd == 0.0
    assert entry.input_tokens == 0 and entry.output_tokens == 0
    invalid_opening_calls = [c for c in meeting.llm_calls if c.response_text == "{}"]
    assert len(invalid_opening_calls) == 4  # opening x2 (one retry) + 2 opt_in x1


# --- Validation-default spend preservation + abort-path visibility (gp-2) ----
# Both close review feedback on PR #123: a REAL provider validates internally
# and RAISES (carrying LLMCallFailure metadata) before _RecordingLLMClient can
# log the call, so (1) the burned spend must be recovered onto the default's
# replay row rather than zeroed, and (2) a default that fired before a LATER
# call aborts the meeting must still be recorded.


class _ProviderRaisesTurnClient:
    """Real-provider stand-in: ``complete()`` RAISES a ``ValidationError``
    carrying ``LLMCallFailure`` metadata on every ``MeetingTurn`` (the
    Anthropic/Ollama ``_attach_parse_failure`` pattern); votes return SKIP. The
    burned turn calls never reach ``_RecordingLLMClient``'s append.
    """

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if schema is MeetingTurn:
            try:
                MeetingTurn.model_validate_json("{}")
            except ValidationError as exc:
                _attach_parse_failure(
                    exc,
                    LLMCallFailure(
                        model="qwen2.5:7b-instruct",
                        prompt_length=len(prompt),
                        raw_response="garbage not json",
                        input_tokens=200,
                        output_tokens=9,
                        cost_usd=0.0,
                        error_type="ValidationError",
                        error_message="bad turn",
                    ),
                )
                raise
            raise AssertionError("unreachable")  # pragma: no cover
        if schema is ModelAuthoredVoteBallot:
            return LLMResponse(
                text=VoteBallot(
                    voter="x",
                    target="SKIP",
                    confidence=0.0,
                    primary_reason_id=None,
                    considered_alternatives=(),
                    rationale_text="skip",
                ).model_dump_json(),
                usage=TokenUsage(input_tokens=1, output_tokens=1),
                cost_usd=0.0,
                model=model or "provider-raises",
            )
        raise AssertionError(f"unexpected schema: {schema!r}")  # pragma: no cover


def test_provider_validation_default_preserves_spend_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real-provider validation default records its REAL spend, not zeros."""

    game_map = load_canonical_map()
    body_id = _seed_meeting_with_body(monkeypatch, game_map=game_map)

    def factory(agent_id: PlayerId, role: Role) -> _MeetingAwareReporter:
        return _MeetingAwareReporter(
            agent_id=agent_id,
            role=role,
            report_body_id=body_id if agent_id == "p-1" else None,
        )

    runner = build_default_meeting_runner(llm_client=_ProviderRaisesTurnClient())
    replay_path = tmp_path / "provider-default.jsonl"
    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=6),
        meeting_runner=runner,
    )
    game.run()

    entries = read_all_entries(replay_path)
    meeting = next(e for e in entries if isinstance(e, MeetingReplayEntry))
    failed = [e for e in entries if isinstance(e, FailedCallReplayEntry)]

    assert meeting.outcome == "SKIPPED"
    # The burned turn attempts (opening + the two unconditional opt_in turns)
    # raised before the recording client logged them, so llm_calls holds only
    # the 3 SKIP votes (no double-count)...
    assert len(meeting.llm_calls) == 3
    # ...and each consumed attempt has its own identity and real usage: two
    # opening attempts plus one per opt_in turn. A separate zero-spend marker
    # keeps each default visible without charging the same response again.
    attempts = [f for f in failed if f.call_id is not None]
    defaults = [f for f in failed if f.error_type == "deadline_default"]
    assert len(failed) == 7
    assert len(attempts) == len({f.call_id for f in attempts}) == 4
    assert all(f.error_type == "ValidationError" for f in attempts)
    assert all(f.model == "qwen2.5:7b-instruct" for f in attempts)
    assert all(f.input_tokens == 200 and f.output_tokens == 9 for f in attempts)
    assert all(f.raw_response == "garbage not json" for f in attempts)
    assert len(defaults) == 3
    assert all(f.input_tokens == f.output_tokens == 0 for f in defaults)
    assert all(f.cost_usd == 0 for f in defaults)
    assert all(
        ("opening" in f.error_message or "opt_in" in f.error_message) for f in defaults
    )
    assert (
        sum(f.input_tokens for f in failed)
        + sum(call.input_tokens for call in meeting.llm_calls)
        == 803
    )
    assert (
        sum(f.output_tokens for f in failed)
        + sum(call.output_tokens for call in meeting.llm_calls)
        == 39
    )


class _OpeningDefaultsThenBallotsDefaultClient:
    """Opening AND ballots return invalid text — every call fails validation.

    Pre-10.9.1 this client ABORTED the game on the first ballot (votes had
    no fail-soft; the seed-8 / PR #147 F1 shape). Under the vote-ballot
    fail-soft the same payloads degrade: the opening to its placeholder
    default (after the retry) and every ballot to a marked SKIP, so the
    meeting resolves and the run continues.
    """

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        # "{}" is invalid for both MeetingTurn and VoteBallot. The turn path
        # fail-softs into a default (Task 7.10); since Task 10.9.1 the vote
        # path fail-softs too (a marked SKIP) instead of re-raising.
        return LLMResponse(
            text="{}",
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "all-invalid",
        )


def test_malformed_ballots_no_longer_abort_and_every_default_is_recorded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The PR #147 F1 abort path is unreachable from a malformed ballot.

    The orchestrator-level read-verify for Task 10.9.1: the exact client
    shape that used to kill the game (every completion schema-invalid) now
    yields a RESOLVED meeting — the opening placeholder-defaults, every
    ballot degrades to a ``VOTE_PARSE_DEFAULT_MARKER`` SKIP, the meeting
    row records, and one zero-spend ``deadline_default`` visibility row
    per fired default reaches the replay through the UNCHANGED
    ``_record_deadline_defaults`` writer (no new trigger literal; the
    pre-existing ``validation`` trigger + ``vote`` phase name the rows).
    """

    game_map = load_canonical_map()
    body_id = _seed_meeting_with_body(monkeypatch, game_map=game_map)

    def factory(agent_id: PlayerId, role: Role) -> _MeetingAwareReporter:
        return _MeetingAwareReporter(
            agent_id=agent_id,
            role=role,
            report_body_id=body_id if agent_id == "p-1" else None,
        )

    runner = build_default_meeting_runner(
        llm_client=_OpeningDefaultsThenBallotsDefaultClient()
    )
    replay_path = tmp_path / "ballots-default-no-abort.jsonl"
    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=6),
        meeting_runner=runner,
    )
    game.run()  # completes; the old behavior raised ValidationError here

    entries = read_all_entries(replay_path)
    # The meeting resolved and recorded; every ballot is the marked
    # degraded SKIP, so the tally is a clean SKIPPED, not a crash.
    meeting = next(e for e in entries if isinstance(e, MeetingReplayEntry))
    assert meeting.outcome == "SKIPPED"
    marker_prefix = VOTE_PARSE_DEFAULT_MARKER.split("{head!r}")[0]
    assert meeting.ballots
    assert all(b.target == "SKIP" for b in meeting.ballots)
    assert all(b.rationale_text.startswith(marker_prefix) for b in meeting.ballots)
    # One visibility row per fired default: the opening (validation, after
    # its retry), one per now-unconditional opt_in roll_call turn, plus one per
    # degraded ballot — none lost, none double-spent (manager-side validation
    # rows are zero-spend; llm_calls holds the real spend).
    deadline_defaults = [
        e
        for e in entries
        if isinstance(e, FailedCallReplayEntry) and e.error_type == "deadline_default"
    ]
    opening_rows = [e for e in deadline_defaults if "opening" in e.error_message]
    opt_in_rows = [e for e in deadline_defaults if "opt_in" in e.error_message]
    vote_rows = [
        e for e in deadline_defaults if "vote defaulted (validation)" in e.error_message
    ]
    assert len(opening_rows) == 1
    assert len(vote_rows) == len(meeting.ballots)
    assert len(deadline_defaults) == len(opening_rows) + len(opt_in_rows) + len(
        vote_rows
    )


class _OpeningDefaultsThenBallotTransportAbortsClient:
    """Opening returns invalid text (manager-side default after retry); the
    first ballot raises a transport ``TimeoutError``, which the manager
    re-tags ``LLMProviderError`` and propagates — the abort vector that
    REMAINS fail-loud after Task 10.9.1 (only deadline + parse failures
    fail soft). The opening default must survive that abort.
    """

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if schema is ModelAuthoredVoteBallot:
            raise TimeoutError("provider transport timeout")
        return LLMResponse(
            text="{}",
            usage=TokenUsage(input_tokens=1, output_tokens=1),
            cost_usd=0.0,
            model=model or "transport-aborts",
        )


def test_default_recorded_when_a_later_ballot_aborts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A default that fired before a meeting-aborting ballot is still recorded.

    The gp-2 abort-survival pin, re-anchored on the abort vector that still
    exists after Task 10.9.1: a provider/transport failure on the ballot
    (``LLMProviderError``) — a malformed ballot no longer aborts (see
    ``test_malformed_ballots_no_longer_abort_and_every_default_is_recorded``).
    """

    game_map = load_canonical_map()
    body_id = _seed_meeting_with_body(monkeypatch, game_map=game_map)

    def factory(agent_id: PlayerId, role: Role) -> _MeetingAwareReporter:
        return _MeetingAwareReporter(
            agent_id=agent_id,
            role=role,
            report_body_id=body_id if agent_id == "p-1" else None,
        )

    runner = build_default_meeting_runner(
        llm_client=_OpeningDefaultsThenBallotTransportAbortsClient()
    )
    replay_path = tmp_path / "abort-after-default.jsonl"
    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=6),
        meeting_runner=runner,
    )
    with pytest.raises(LLMProviderError):
        game.run()

    entries = read_all_entries(replay_path)
    # The meeting aborted on the ballot, so no meeting row was recorded...
    assert not any(isinstance(e, MeetingReplayEntry) for e in entries)
    # ...but the defaults that fired BEFORE the abort are still visible: the
    # opening plus each now-unconditional opt_in roll_call turn (all before the
    # first ballot, which is where the transport abort lands).
    deadline_defaults = [
        e
        for e in entries
        if isinstance(e, FailedCallReplayEntry) and e.error_type == "deadline_default"
    ]
    assert len(deadline_defaults) == 3
    assert "opening" in deadline_defaults[0].error_message


class _RaiseFirstTurnThenSucceedClient:
    """First ``MeetingTurn`` raises a provider-side ``ValidationError`` (with
    ``LLMCallFailure``); later turns parse (accusation-free); votes SKIP. Models
    a retry that recovers after one provider parse-failure -- the failed attempt
    must still be accounted even though the turn ultimately succeeded.
    """

    def __init__(self) -> None:
        self._turn_calls = 0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        if schema is MeetingTurn:
            self._turn_calls += 1
            if self._turn_calls == 1:
                try:
                    MeetingTurn.model_validate_json("{}")
                except ValidationError as exc:
                    _attach_parse_failure(
                        exc,
                        LLMCallFailure(
                            model="qwen2.5:7b-instruct",
                            prompt_length=len(prompt),
                            raw_response="garbage not json",
                            input_tokens=150,
                            output_tokens=8,
                            cost_usd=0.0,
                            error_type="ValidationError",
                            error_message="bad turn",
                        ),
                    )
                    raise
                raise AssertionError("unreachable")  # pragma: no cover
            return LLMResponse(
                text=MeetingTurn(
                    turn_id="x",
                    turn_index=0,
                    speaker="x",
                    turn_kind="opening",
                    reply_to=None,
                    observations=(),
                    claims=(),
                    # "unsure" satisfies the Task 10.3 opening validation, so
                    # the retry genuinely recovers (no default fires).
                    free_text="recovered opening (unsure)",
                ).model_dump_json(),
                usage=TokenUsage(input_tokens=1, output_tokens=1),
                cost_usd=0.0,
                model=model or "recovered",
            )
        if schema is ModelAuthoredVoteBallot:
            return LLMResponse(
                text=VoteBallot(
                    voter="x",
                    target="SKIP",
                    confidence=0.0,
                    primary_reason_id=None,
                    considered_alternatives=(),
                    rationale_text="skip",
                ).model_dump_json(),
                usage=TokenUsage(input_tokens=1, output_tokens=1),
                cost_usd=0.0,
                model=model or "recovered",
            )
        raise AssertionError(f"unexpected schema: {schema!r}")  # pragma: no cover


def test_recovered_failure_recorded_when_retry_succeeds_end_to_end(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A provider parse-failure recovered on retry is still accounted (gp-2).

    The failed first attempt never reached the recording client (it raised), and
    the succeeding turn carries no default — so without surfacing it the burned
    spend would vanish. It is recorded once as a failed-call with real spend,
    and is NOT in llm_calls (no double-count) and NOT a deadline_default (no
    default fired).
    """

    game_map = load_canonical_map()
    body_id = _seed_meeting_with_body(monkeypatch, game_map=game_map)

    def factory(agent_id: PlayerId, role: Role) -> _MeetingAwareReporter:
        return _MeetingAwareReporter(
            agent_id=agent_id,
            role=role,
            report_body_id=body_id if agent_id == "p-1" else None,
        )

    runner = build_default_meeting_runner(llm_client=_RaiseFirstTurnThenSucceedClient())
    replay_path = tmp_path / "recovered.jsonl"
    game = HeadlessGame(
        seed=2026,
        game_map=game_map,
        agent_factory=factory,
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=6),
        meeting_runner=runner,
    )
    game.run()

    entries = read_all_entries(replay_path)
    meeting = next(e for e in entries if isinstance(e, MeetingReplayEntry))
    failed = [e for e in entries if isinstance(e, FailedCallReplayEntry)]

    # The opening recovered on retry -> meeting completed (not aborted/default).
    assert meeting.outcome == "SKIPPED"
    # opening (recovered) + two now-unconditional opt_in roll_call turns.
    assert len(meeting.transcript.turns) == 3
    # llm_calls: the recovered opening (1) + 2 opt_in turns + 3 SKIP votes = 6;
    # the raised first attempt is NOT among them (no double-count).
    assert len(meeting.llm_calls) == 6
    # The burned first attempt is recorded once with its real spend...
    assert len(failed) == 1
    assert failed[0].input_tokens == 150 and failed[0].output_tokens == 8
    assert failed[0].model == "qwen2.5:7b-instruct"
    # ...and it is NOT a deadline_default (the turn succeeded; no default fired).
    assert failed[0].error_type == "ValidationError"


# ---------------------------------------------------------------------------
# Dead-crewmate task rule — redistribute (DESIGN.md §3.5; Task 13.10).
# ---------------------------------------------------------------------------


def _redistribute_map() -> Map:
    """Canonical map with the dead-crewmate task rule flipped to
    ``redistribute`` (DESIGN.md §3.5; Task 13.10)."""

    return load_canonical_map().model_copy(update={"dead_task_rule": "redistribute"})


def test_ejection_redistributes_incomplete_tasks_under_redistribute_rule() -> None:
    """Under ``redistribute`` an EJECTED crewmate's incomplete instances re-key to
    living crewmates instead of dropping — mirroring the kill path (DESIGN.md
    §3.5). The default ``drop`` is unchanged (covered in test_meeting_integration).
    """

    game_map = _redistribute_map()
    # 5-player lobby so ejecting one crewmate does not reach impostor parity.
    base = seed_initial_state(seed=2026, game_map=game_map, num_players=5)
    state = replace(base, phase="MEETING", tick=42)

    # The lowest-id living crewmate that is NOT the ejected target is the
    # expected recipient for any of the target's incomplete map tasks it does
    # not already own.
    living_crew = sorted(
        pid for pid, p in state.players.items() if p.alive and p.role == "CREWMATE"
    )
    target = living_crew[0]
    target_incomplete = {
        task.map_task_id
        for task in state.tasks.values()
        if task.owner == target and not task.completed
    }
    assert target_incomplete, "fixture must give the target incomplete tasks"

    ballot = VoteBallot(
        voter="p-1",
        target=target,
        confidence=0.9,
        primary_reason_id=None,
        considered_alternatives=(),
        rationale_text=f"eject {target}",
    )
    result = MeetingResult(
        meeting_id="g-1:meeting-0",
        triggered_by="p-1",
        trigger_tick=42,
        outcome="EJECTED",
        ejected_player_id=target,
        ballots=(ballot,),
        contradictions=(),
        transcript=MeetingTranscript(),
    )

    next_state, _ = apply_meeting_result(state, result, game_map=game_map)

    assert next_state.players[target].alive is False
    # The target owns no incomplete instances afterwards (re-keyed away).
    assert not any(
        task.owner == target and not task.completed
        for task in next_state.tasks.values()
    )
    # Each redistributed map task landed on a living crewmate not previously
    # owning it, carrying over as a new instance keyed by the recipient.
    other_crew = [pid for pid in living_crew if pid != target]
    for map_task_id in target_incomplete:
        owners_before = {
            task.owner
            for task in state.tasks.values()
            if task.map_task_id == map_task_id
        }
        recipient = next((pid for pid in other_crew if pid not in owners_before), None)
        if recipient is None:
            # No eligible recipient -> the no-recipient drop fallback applies.
            continue
        new_id = f"{recipient}:{map_task_id}"
        assert new_id in next_state.tasks
        moved = next_state.tasks[new_id]
        assert moved.owner == recipient
        assert moved.map_task_id == map_task_id


def test_redistribute_game_resims_to_identical_state(tmp_path: Path) -> None:
    """Determinism: a full game under ``redistribute`` (with kills firing) re-sims
    byte-identically across two runs (DESIGN.md §3.5; Task 13.10). Seed 0 reaches
    an impostor win with multiple deaths, so the redistribute re-key path is
    exercised by the run."""

    game_map = _redistribute_map()
    first_path = tmp_path / "first.jsonl"
    second_path = tmp_path / "second.jsonl"

    results = []
    for replay_path in (first_path, second_path):
        game = HeadlessGame(
            seed=0,
            game_map=game_map,
            agent_factory=build_default_agent_factory(),
            replay_path=replay_path,
            scheduler=TickScheduler(max_ticks=400),
        )
        results.append(game.run())

    # The run terminates with deaths (so redistribute fired) and is reproducible.
    assert results[0].outcome == results[1].outcome
    assert sum(1 for p in results[0].final_state.players.values() if not p.alive) >= 1
    assert first_path.read_bytes() == second_path.read_bytes()
