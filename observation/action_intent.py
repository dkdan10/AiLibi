from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

BodyId: TypeAlias = str
PlayerId: TypeAlias = str
RoomId: TypeAlias = str
TaskId: TypeAlias = str
VentId: TypeAlias = str


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class _BaseIntent(_FrozenModel):
    actor: PlayerId


class _MovePayload(_FrozenModel):
    to_room: RoomId


class MoveIntent(_BaseIntent):
    type: Literal["move"]
    payload: _MovePayload


class _DoTaskPayload(_FrozenModel):
    task_id: TaskId


class DoTaskIntent(_BaseIntent):
    type: Literal["do_task"]
    payload: _DoTaskPayload


class _KillPayload(_FrozenModel):
    target: PlayerId


class KillIntent(_BaseIntent):
    type: Literal["kill"]
    payload: _KillPayload

    @model_validator(mode="after")
    def validate_not_self_target(self) -> KillIntent:
        if self.actor == self.payload.target:
            raise ValueError("kill target must be a different player")
        return self


class _VentPayload(_FrozenModel):
    vent_id: VentId


class VentIntent(_BaseIntent):
    type: Literal["vent"]
    payload: _VentPayload


class _ReportPayload(_FrozenModel):
    body_id: BodyId


class ReportBodyIntent(_BaseIntent):
    type: Literal["report"]
    payload: _ReportPayload


class _EmergencyPayload(_FrozenModel):
    reason: str | None = None


class EmergencyMeetingIntent(_BaseIntent):
    type: Literal["emergency"]
    payload: _EmergencyPayload = Field(default_factory=_EmergencyPayload)


class _SabotagePayload(_FrozenModel):
    kind: str


class SabotageIntent(_BaseIntent):
    type: Literal["sabotage"]
    payload: _SabotagePayload


class _RepairSabotagePayload(_FrozenModel):
    kind: str


class RepairSabotageIntent(_BaseIntent):
    type: Literal["repair_sabotage"]
    payload: _RepairSabotagePayload


class _WaitPayload(_FrozenModel):
    pass


class WaitIntent(_BaseIntent):
    type: Literal["wait"]
    payload: _WaitPayload = Field(default_factory=_WaitPayload)


ActionIntent: TypeAlias = Annotated[
    MoveIntent
    | DoTaskIntent
    | KillIntent
    | VentIntent
    | ReportBodyIntent
    | EmergencyMeetingIntent
    | SabotageIntent
    | RepairSabotageIntent
    | WaitIntent,
    Field(discriminator="type"),
]
