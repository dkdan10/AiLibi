from __future__ import annotations

from typing import Protocol, runtime_checkable

from observation.action_intent import ActionIntent
from observation.packet import EventObservationBatch, ObservationPacket
from observation.public_map import PublicMapView


@runtime_checkable
class AgentInterface(Protocol):
    """Minimal contract every agent satisfies (DESIGN.md §4.1).

    Agents stay behind the observation firewall: they only see the engine-free
    `ObservationPacket` plus the public `PublicMapView` and they only emit
    `ActionIntent`. They never import from `engine/`.
    """

    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent: ...


@runtime_checkable
class EventObservingAgent(Protocol):
    """Optional source-time event ingestion, without another tactical decision."""

    def observe_events(self, batch: EventObservationBatch) -> None: ...
