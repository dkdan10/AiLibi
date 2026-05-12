"""Headless game orchestrator (DESIGN.md §1.4, §3.1, §11.4).

:class:`HeadlessGame` wires the engine, observation service, agents,
action-intent translation, and replay log into a single deterministic
tick loop. It is the convergence point of Phase 2: existing engine,
observation, agent, and boundary modules all flow through this class.

The orchestrator is the only non-``engine/`` module that imports from
``engine/``. Agents stay behind the observation firewall, receiving
:class:`ObservationPacket` and :class:`PublicMapView` and returning
:class:`ActionIntent`.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Literal, TypeAlias

from agents.base import AgentInterface
from agents.memory.episodic import MemoryStore
from agents.perception import ingest_packet
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.impostor_policy import ImpostorPolicy
from engine.entities import PlayerId, PlayerState, Role
from engine.events import EngineEvent, GameOverEvent
from engine.tick import advance_tick
from engine.world import Map, WorldState
from observation.action_intent import ActionIntent
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView
from observation.service import ObservationService
from orchestrator.boundary import (
    public_map_from_engine_map,
    translate_action_intents_for_tick,
)
from orchestrator.replay import ReplayLog
from orchestrator.scheduler import TickScheduler
from orchestrator.seeder import seed_initial_state

AgentFactory: TypeAlias = Callable[[PlayerId, Role], AgentInterface]

Outcome: TypeAlias = Literal[
    "CREWMATES",
    "IMPOSTORS",
    "MEETING_PHASE_REACHED",
    "TICK_BUDGET_REACHED",
]

DEFAULT_MAX_TICKS: Final[int] = 1000
DEFAULT_NUM_PLAYERS: Final[int] = 4
DEFAULT_NUM_IMPOSTORS: Final[int] = 1


@dataclass(frozen=True)
class HeadlessGameResult:
    """Outcome bundle returned by :meth:`HeadlessGame.run`.

    ``outcome`` is one of:

    - ``CREWMATES`` / ``IMPOSTORS``: an engine ``GameOverEvent`` fired and
      named the winner. ``final_state.phase`` is ``GAME_OVER``.
    - ``MEETING_PHASE_REACHED``: a ``ReportBody`` or ``EmergencyMeeting``
      intent transitioned the engine to ``MEETING``. The orchestrator
      pauses here in Phase 2 (Phase 3.8 owns the meeting manager) and
      does not mutate state to resume. ``final_state.phase`` is
      ``MEETING``.
    - ``TICK_BUDGET_REACHED``: :class:`TickScheduler` capped the game
      before it ended naturally. ``final_state.phase`` is ``PLAY``. The
      partial replay is still written to ``replay_path``.
    """

    final_state: WorldState
    outcome: Outcome
    replay_path: Path


class HeadlessGame:
    """Run one deterministic headless game from a seed."""

    def __init__(
        self,
        *,
        seed: int,
        game_map: Map,
        agent_factory: AgentFactory,
        replay_path: Path,
        audit_log_path: Path | None = None,
        num_players: int = DEFAULT_NUM_PLAYERS,
        num_impostors: int = DEFAULT_NUM_IMPOSTORS,
        scheduler: TickScheduler | None = None,
    ) -> None:
        self._seed = seed
        self._game_map = game_map
        self._agent_factory = agent_factory
        self._replay_path = replay_path
        self._audit_log_path = (
            audit_log_path
            if audit_log_path is not None
            else replay_path.parent / f"{replay_path.stem}.audit.jsonl"
        )
        self._num_players = num_players
        self._num_impostors = num_impostors
        self._scheduler = (
            scheduler
            if scheduler is not None
            else TickScheduler(max_ticks=DEFAULT_MAX_TICKS)
        )
        self._public_map = public_map_from_engine_map(game_map)

    @property
    def public_map(self) -> PublicMapView:
        return self._public_map

    @property
    def replay_path(self) -> Path:
        return self._replay_path

    def run(self) -> HeadlessGameResult:
        """Run the headless tick loop until terminate, meeting, or tick budget.

        Each iteration: build observations for every alive agent, dispatch
        them, collect :class:`ActionIntent`s, translate to engine actions,
        advance the engine one tick, and append to the replay log.
        """

        state = seed_initial_state(
            seed=self._seed,
            game_map=self._game_map,
            num_players=self._num_players,
            num_impostors=self._num_impostors,
        )
        observation_service = ObservationService(
            game_map=self._game_map,
            audit_log_path=self._audit_log_path,
        )
        replay = ReplayLog(self._replay_path, game_id=self._game_id())
        agents = self._build_agents(state.players)

        last_events: tuple[EngineEvent, ...] = ()
        while state.phase == "PLAY":
            if not self._scheduler.should_continue(state.tick):
                return HeadlessGameResult(
                    final_state=state,
                    outcome="TICK_BUDGET_REACHED",
                    replay_path=self._replay_path,
                )

            packets = self._build_packets(
                state=state,
                observation_service=observation_service,
                last_events=last_events,
            )
            intents = self._collect_intents(packets=packets, agents=agents)
            actions = list(translate_action_intents_for_tick(intents))
            input_tick = state.tick
            state, events = advance_tick(state, actions, game_map=self._game_map)
            last_events = tuple(events)
            replay.record_tick(input_tick, actions, state)

            if state.phase == "MEETING":
                return HeadlessGameResult(
                    final_state=state,
                    outcome="MEETING_PHASE_REACHED",
                    replay_path=self._replay_path,
                )

        return HeadlessGameResult(
            final_state=state,
            outcome=self._game_over_outcome(last_events),
            replay_path=self._replay_path,
        )

    def _build_agents(
        self,
        players: Mapping[PlayerId, PlayerState],
    ) -> dict[PlayerId, AgentInterface]:
        agents: dict[PlayerId, AgentInterface] = {}
        for player_id in sorted(players):
            agents[player_id] = self._agent_factory(player_id, players[player_id].role)
        return agents

    def _build_packets(
        self,
        *,
        state: WorldState,
        observation_service: ObservationService,
        last_events: tuple[EngineEvent, ...],
    ) -> dict[PlayerId, ObservationPacket]:
        packets: dict[PlayerId, ObservationPacket] = {}
        for player_id in sorted(state.players):
            if not state.players[player_id].alive:
                continue
            packets[player_id] = observation_service.build_packet(
                world_state=state,
                agent_id=player_id,
                engine_events=last_events,
            )
        return packets

    def _collect_intents(
        self,
        *,
        packets: Mapping[PlayerId, ObservationPacket],
        agents: Mapping[PlayerId, AgentInterface],
    ) -> list[ActionIntent]:
        return [
            agents[player_id].decide(packets[player_id], self._public_map)
            for player_id in sorted(packets)
        ]

    def _game_over_outcome(
        self, last_events: tuple[EngineEvent, ...]
    ) -> Literal["CREWMATES", "IMPOSTORS"]:
        for event in last_events:
            if isinstance(event, GameOverEvent):
                return event.winner
        raise RuntimeError("game loop exited PLAY without emitting a GameOverEvent")

    def _game_id(self) -> str:
        return f"headless-seed-{self._seed}"


class TacticalAgent:
    """Default tactical agent that bridges perception and a tactical policy.

    The orchestrator's default :data:`AgentFactory`
    (:func:`build_default_agent_factory`) returns one of these per player.
    Each agent owns a private :class:`MemoryStore`; perception writes the
    incoming packet into memory, then the policy reads memory and returns
    an :class:`ActionIntent`. The class lives in the orchestrator because
    it composes pieces from ``agents/`` (perception + memory + tactical)
    without leaking that wiring back into ``agents/runtime.py`` — that
    file's stubs are owned by future tasks (3.x reasoning hooks).
    """

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        policy: CrewmatePolicy | ImpostorPolicy,
        memory: MemoryStore | None = None,
    ) -> None:
        self._agent_id = agent_id
        self._policy = policy
        self._memory = memory if memory is not None else MemoryStore()

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def memory(self) -> MemoryStore:
        return self._memory

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        if packet.agent_id != self._agent_id:
            raise ValueError(
                f"observation packet for agent {packet.agent_id!r} given to "
                f"tactical agent bound to {self._agent_id!r}"
            )
        ingest_packet(packet=packet, memory=self._memory)
        return self._policy.decide(self._memory, public_map)


def build_default_agent_factory() -> AgentFactory:
    """Return the orchestrator's default :data:`AgentFactory`.

    Each constructed agent is a :class:`TacticalAgent` with the role-
    appropriate policy. Useful for ``scripts/run_game.py`` and for tests
    that just want a real, deterministic agent without scripting one.
    """

    def factory(agent_id: PlayerId, role: Role) -> AgentInterface:
        policy: CrewmatePolicy | ImpostorPolicy
        if role == "IMPOSTOR":
            policy = ImpostorPolicy(agent_id=agent_id)
        else:
            policy = CrewmatePolicy(agent_id=agent_id)
        return TacticalAgent(agent_id=agent_id, policy=policy)

    return factory


__all__ = [
    "AgentFactory",
    "DEFAULT_MAX_TICKS",
    "DEFAULT_NUM_IMPOSTORS",
    "DEFAULT_NUM_PLAYERS",
    "HeadlessGame",
    "HeadlessGameResult",
    "Outcome",
    "TacticalAgent",
    "build_default_agent_factory",
]
