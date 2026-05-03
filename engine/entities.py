from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Literal, TypeAlias

if TYPE_CHECKING:
    from engine.actions import Action

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
    last_action: Action | None
    in_vent: bool

    def __post_init__(self) -> None:
        if self.last_action is None:
            return

        from engine.actions import is_action_instance

        if not is_action_instance(self.last_action):
            raise TypeError("last_action must be an engine Action or None")


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
    repair_progress: Mapping[RoomId, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "repair_progress", MappingProxyType(dict(self.repair_progress))
        )
