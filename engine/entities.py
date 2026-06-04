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
# A per-player task *instance* id: the stable string ``"{owner}:{map_task_id}"``
# that keys ``WorldState.tasks`` (DESIGN.md §3.2). Distinct from ``TaskId``, which
# is the MAP task id (``game_map.tasks`` key) the instance is anchored to.
TaskInstanceId: TypeAlias = str
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
    """A per-player task *instance* (DESIGN.md §3.2, §3.3).

    ``id`` is the instance id — the stable composite string
    ``"{owner}:{map_task_id}"`` that keys ``WorldState.tasks`` — so several
    crewmates can each hold an instance of the same map task with independent
    progress. ``map_task_id`` is the MAP task id this instance is anchored to
    (its room is ``game_map.tasks[map_task_id].room``); it is the *agent-facing*
    id the engine resolves against ``owner`` (the agent never sees the composite
    instance id or another player's ownership).
    """

    id: TaskInstanceId
    owner: PlayerId
    map_task_id: TaskId
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
