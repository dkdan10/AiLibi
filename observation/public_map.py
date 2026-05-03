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
    task_locations: Mapping[TaskId, RoomId]
    spawn_room: RoomId
    meeting_room: RoomId
    emergency_button_room: RoomId
