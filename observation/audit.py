from __future__ import annotations

import json
from pathlib import Path
from typing import TextIO

from observation.packet import EventObservationBatch, ObservationPacket


class ObservationAuditLog:
    """Append-only on-disk audit log for serialized observation packets."""

    def __init__(self, path: Path) -> None:
        # Assigned first so __del__ is safe even if construction raises below.
        self._handle: TextIO | None = None
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    def record_packet(self, packet: ObservationPacket | EventObservationBatch) -> None:
        handle = self._handle
        if handle is None:
            # Lazy open + reuse: one open per audit log instead of one per
            # packet (build_packet runs once per alive agent per tick — the
            # Task 5.9 profile surfaced the per-packet open as a hot path).
            # Append mode is preserved (two instances writing the same path
            # still concatenate in order).
            handle = self._path.open("a", encoding="utf-8")
            self._handle = handle
        handle.write(json.dumps(packet.model_dump(mode="json"), sort_keys=True))
        handle.write("\n")
        # Flush each row so a reader opening the path while the log is alive
        # sees every packet — byte-identical to the original open/close-per-
        # write, minus the per-write open/close syscalls.
        handle.flush()

    def close(self) -> None:
        """Flush and release the append handle (idempotent)."""

        handle = self._handle
        if handle is not None:
            self._handle = None
            handle.close()

    def __del__(self) -> None:
        # Best-effort descriptor release for callers that drop the log without
        # closing it (e.g. ``del service`` in the observation tests). Per-write
        # flush already persisted every line; __del__ must never raise.
        try:
            self.close()
        except Exception:
            pass
