from __future__ import annotations

from typing import Annotated, Literal, TypeAlias, TypeGuard

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.entities import BodyId, PlayerId, TaskId
from engine.world import RoomId, VentId


class _BaseAction(BaseModel):
    """Common immutable fields for all engine actions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    actor: PlayerId


class _MovePayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    to_room: RoomId


class MoveAction(_BaseAction):
    type: Literal["move"]
    payload: _MovePayload


class _DoTaskPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: TaskId


class DoTaskAction(_BaseAction):
    type: Literal["do_task"]
    payload: _DoTaskPayload


class _KillPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    target: PlayerId


class KillAction(_BaseAction):
    type: Literal["kill"]
    payload: _KillPayload

    @model_validator(mode="after")
    def validate_not_self_target(self) -> KillAction:
        if self.actor == self.payload.target:
            raise ValueError("kill target must be a different player")
        return self


class _VentPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    vent_id: VentId


class VentAction(_BaseAction):
    type: Literal["vent"]
    payload: _VentPayload


class _ReportPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    body_id: BodyId


class ReportBodyAction(_BaseAction):
    type: Literal["report"]
    payload: _ReportPayload


class _EmergencyPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    reason: str | None = None


class EmergencyMeetingAction(_BaseAction):
    type: Literal["emergency"]
    payload: _EmergencyPayload = Field(default_factory=_EmergencyPayload)


class _SabotagePayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: str


class SabotageAction(_BaseAction):
    type: Literal["sabotage"]
    payload: _SabotagePayload


class _WaitPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class WaitAction(_BaseAction):
    type: Literal["wait"]
    payload: _WaitPayload = Field(default_factory=_WaitPayload)


Action: TypeAlias = Annotated[
    MoveAction
    | DoTaskAction
    | KillAction
    | VentAction
    | ReportBodyAction
    | EmergencyMeetingAction
    | SabotageAction
    | WaitAction,
    Field(discriminator="type"),
]


def is_action_instance(value: object) -> TypeGuard[Action]:
    return isinstance(
        value,
        (
            MoveAction,
            DoTaskAction,
            KillAction,
            VentAction,
            ReportBodyAction,
            EmergencyMeetingAction,
            SabotageAction,
            WaitAction,
        ),
    )
