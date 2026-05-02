from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from engine.entities import BodyId, PlayerId, Role
from engine.world import RoomId, TaskId


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class SelfView(_FrozenModel):
    room: RoomId
    role: Role
    pending_task_id: TaskId | None


class PlayerView(_FrozenModel):
    id: PlayerId
    room: RoomId
    action: str | None


class BodyView(_FrozenModel):
    id: BodyId
    room: RoomId


class AudibleEvent(_FrozenModel):
    kind: Literal["vent_use_heard", "sabotage_alarm"]
    room: RoomId | None = None


class GlobalView(_FrozenModel):
    tasks_completed: int
    tasks_total: int
    task_completion_percent: float
    sabotage_active: bool
    sabotage_kind: str | None


class ObservationPacket(_FrozenModel):
    tick: int
    agent_id: PlayerId
    self_state: SelfView
    visible_players: list[PlayerView]
    visible_bodies: list[BodyView]
    audible_events: list[AudibleEvent]
    global_state: GlobalView
    cooldown: int | None
