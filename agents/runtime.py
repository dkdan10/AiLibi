from __future__ import annotations

from agents.memory.episodic import MemoryStore
from agents.perception import ingest_packet
from observation.action_intent import ActionIntent, WaitIntent
from observation.packet import ObservationPacket, PlayerId
from observation.public_map import PublicMapView


class AgentRuntime:
    """Glue object that wires perception → memory → tactical (DESIGN.md §4.1).

    Task 2.2 introduces only the runtime skeleton. The perception, memory, and
    tactical hooks below are deliberate stubs that later phase-2 tasks fill in:

    - ``_perceive`` is owned by Task 2.4 (`agents/perception.py`).
    - ``_update_memory`` is owned by Task 2.3 (`agents/memory/`).
    - ``_choose_action`` is owned by Tasks 2.6 / 2.7 (`agents/tactical/`).

    The runtime never imports from ``engine/``: it consumes only the engine-free
    observation schemas and emits ``ActionIntent``.
    """

    def __init__(
        self,
        *,
        agent_id: PlayerId,
        memory: MemoryStore | None = None,
    ) -> None:
        self._agent_id = agent_id
        self._memory = memory

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    @property
    def memory(self) -> MemoryStore | None:
        return self._memory

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
        Without a store, this remains a pure stub so callers that have not
        yet wired memory keep working.
        """

        if self._memory is None:
            return ()
        ingest_packet(packet=packet, memory=self._memory)
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
