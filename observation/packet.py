from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

BodyId: TypeAlias = str
PlayerId: TypeAlias = str
Role: TypeAlias = Literal["CREWMATE", "IMPOSTOR"]
RoomId: TypeAlias = str
TaskId: TypeAlias = str


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
    """A body visible to the observer.

    ``victim_id`` formalizes the body's victim player id at the
    observation boundary (DESIGN.md §1.3 / Appendix A). It carries the
    same information that was previously inferrable from the
    ``body-{victim_id}-{tick}`` id format emitted by ``engine/rules.py``,
    so exposing it does not weaken the firewall -- it removes the
    agent→engine string coupling flagged as R-4 in
    ``audits/audit-2026-05-16-0036-reconciled.md``.
    """

    id: BodyId
    room: RoomId
    victim_id: PlayerId = Field(min_length=1)


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
    visible_players: tuple[PlayerView, ...]
    visible_bodies: tuple[BodyView, ...]
    audible_events: tuple[AudibleEvent, ...]
    global_state: GlobalView
    cooldown: int | None
