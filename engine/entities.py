from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

PlayerId: TypeAlias = str
BodyId: TypeAlias = str
RoomId: TypeAlias = str
TaskId: TypeAlias = str
Role: TypeAlias = Literal["CREWMATE", "IMPOSTOR"]


@dataclass(frozen=True)
class PlayerState:
    id: PlayerId
    role: Role
    alive: bool
    room: RoomId
    position: tuple[float, float]
    last_action: object | None
    in_vent: bool


@dataclass(frozen=True)
class BodyState:
    id: BodyId
    player_id: PlayerId
    room: RoomId
    position: tuple[float, float]
    killed_by: PlayerId
    discovered_by: PlayerId | None


@dataclass(frozen=True)
class TaskState:
    id: TaskId
    owner: PlayerId
    room: RoomId
    progress: int
    required_ticks: int
    completed: bool


@dataclass(frozen=True)
class SabotageState:
    kind: str
    remaining_ticks: int
    affected_rooms: tuple[RoomId, ...]
    active: bool
