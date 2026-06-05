from __future__ import annotations

from collections.abc import Mapping
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict

MapId: TypeAlias = str
RoomId: TypeAlias = str
TaskId: TypeAlias = str
VentId: TypeAlias = str


class PublicMapView(BaseModel):
    """Engine-free public topology available to agents."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    map_id: MapId
    room_ids: tuple[RoomId, ...]
    room_neighbors: Mapping[RoomId, tuple[RoomId, ...]]
    vent_graph: Mapping[VentId, tuple[VentId, ...]]
    vent_rooms: Mapping[VentId, RoomId]
    # Keyed by MAP task id (a ``game_map.tasks`` key), one entry per map task --
    # NOT per per-player instance (DESIGN.md §3.2). The per-player re-key (Task 8.1)
    # keeps the agent-facing id the map id, so a policy resolves its own
    # ``pending_task_id`` (a map id) to a room here regardless of which owner holds
    # the instance; this mapping is shared across all agents and stays map-keyed.
    task_locations: Mapping[TaskId, RoomId]
    spawn_room: RoomId
    meeting_room: RoomId
    emergency_button_room: RoomId
