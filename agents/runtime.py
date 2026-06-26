"""TEST-ONLY runtime harness (DESIGN.md §4.1) — NOT the production agent.

`AgentRuntime` is a Phase-2 glue scaffold, imported only by tests (the
2026-06-25 memory-pipeline diagnosis, workflow `wg54kfoxy`, confirmed zero
non-test importers of ``agents.runtime``). It is NOT wired into a live game:
its ``_choose_action`` is a hardcoded ``WaitIntent`` and its ``_update_memory``
is a no-op, so it never drives a real tactical decision.

The REAL production agent is ``orchestrator/game.py::TacticalAgent`` — that is
the class the orchestrator's default :data:`~orchestrator.game.AgentFactory`
instantiates per player, and the class that actually bridges perception,
memory, and policy in a live game. Do not mistake this harness for the
production path, and do not delete it as dead code: it is the Phase-2 skeleton
later phases keep around as a documented reference (it is exercised by tests).
"""

from __future__ import annotations

from agents.memory.beliefs import BeliefState
from agents.memory.episodic import MemoryStore
from agents.perception import ingest_packet
from observation.action_intent import ActionIntent, WaitIntent
from observation.packet import ObservationPacket, PlayerId
from observation.public_map import PublicMapView


class AgentRuntime:
    """TEST-ONLY glue harness (DESIGN.md §4.1) — NOT the production agent.

    A Phase-2 skeleton, imported only by tests; the live game's agent is
    ``orchestrator/game.py::TacticalAgent`` (see this module's docstring). Task
    2.2 introduces only the runtime skeleton, and in the absence of the later
    phase-2 wiring the hooks below remain stubs at runtime:

    - ``_perceive`` is owned by Task 2.4 (`agents/perception.py`).
    - ``_update_memory`` is a NO-OP (Task 2.3's full wiring was never bolted
      back onto this harness — ``TacticalAgent`` carries the production path).
    - ``_choose_action`` always returns a hardcoded ``WaitIntent`` (the
      role-specific FSMs of Tasks 2.6 / 2.7 live in ``agents/tactical/`` and
      are driven by ``TacticalAgent``, not this harness).

    The runtime never imports from ``engine/``: it consumes only the engine-free
    observation schemas and emits ``ActionIntent``.
    """

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        memory: MemoryStore | None = None,
        beliefs: BeliefState | None = None,
    ) -> None:
        self._agent_id = agent_id
        self._memory = memory
        # The runtime owns a BeliefState whenever it owns a MemoryStore, so
        # perception can run the DESIGN.md §6.3 belief rules (1 and 4) in a
        # headless game rather than leaving them dormant (audit A-A-4). A
        # caller may inject one (e.g. a shared belief store); otherwise a
        # fresh state is created alongside the memory store. Without a memory
        # store there is nothing to ingest, so no belief state is created.
        if beliefs is not None:
            self._beliefs: BeliefState | None = beliefs
        elif memory is not None:
            self._beliefs = BeliefState()
        else:
            self._beliefs = None

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def memory(self) -> MemoryStore | None:
        return self._memory

    @property
    def beliefs(self) -> BeliefState | None:
        return self._beliefs

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        if packet.agent_id != self._agent_id:
            raise ValueError(
                "observation packet for agent "
                f"{packet.agent_id!r} given to runtime bound to "
                f"{self._agent_id!r}"
            )
        events = self._perceive(packet, public_map)
        self._update_memory(events)
        return self._choose_action(packet, public_map)

    def _perceive(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> tuple[object, ...]:
        """Convert the packet into typed episodic events.

        When the runtime owns a :class:`MemoryStore`, perception writes
        directly into it via :func:`agents.perception.ingest_packet` and
        returns ``()`` (no events for ``_update_memory`` to re-process).
        The runtime's :class:`BeliefState` is threaded into ``ingest_packet``
        so the DESIGN.md §6.3 rule-based belief updates (Rules 1 and 4) run
        per tick in a headless game (audit A-A-4); ``ingest_packet`` adopts
        the rule result into the passed state in place. Without a store, this
        remains a pure stub so callers that have not yet wired memory keep
        working.
        """

        if self._memory is None:
            return ()
        ingest_packet(packet=packet, memory=self._memory, beliefs=self._beliefs)
        return ()

    def _update_memory(self, events: tuple[object, ...]) -> None:
        """Memory stub. Task 2.3 wires the episodic / belief / working stores."""

        return None

    def _choose_action(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent:
        """Tactical stub. Tasks 2.6 / 2.7 install role-specific FSMs.

        Until then the runtime emits a `WaitIntent` so downstream wiring (the
        orchestrator boundary, replay, eval) can exercise the full decide path
        without depending on a tactical policy that does not yet exist.
        """

        return WaitIntent.model_validate(
            {"type": "wait", "actor": self._agent_id, "payload": {}}
        )
