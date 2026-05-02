from __future__ import annotations

import json
from pathlib import Path

from observation.packet import ObservationPacket


class ObservationAuditLog:
    """Append-only on-disk audit log for serialized observation packets."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def record_packet(self, packet: ObservationPacket) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(packet.model_dump(mode="json"), sort_keys=True))
            handle.write("\n")
