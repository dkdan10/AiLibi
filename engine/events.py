from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias

from engine.entities import BodyId, PlayerId, RoomId, TaskId
from engine.win_conditions import WinResultType

EventType: TypeAlias = Literal[
    "ActionRejected",
    "Moved",
    "TaskProgressed",
    "TaskCompleted",
    "Killed",
    "VentEntered",
    "VentExited",
    "SabotageStarted",
    "SabotageRepairProgressed",
    "SabotageRepaired",
    "MeetingTriggered",
    "Waited",
    "GameOver",
    "TickAdvanced",
]


@dataclass(frozen=True)
class ActionRejectedEvent:
    type: Literal["ActionRejected"]
    tick: int
    actor: PlayerId
    action: str
    reason: str


@dataclass(frozen=True)
class MovedEvent:
    type: Literal["Moved"]
    tick: int
    actor: PlayerId
    from_room: RoomId
    to_room: RoomId


@dataclass(frozen=True)
class TaskProgressedEvent:
    type: Literal["TaskProgressed"]
    tick: int
    actor: PlayerId
    task_id: TaskId
    progress: int
    required_ticks: int


@dataclass(frozen=True)
class TaskCompletedEvent:
    type: Literal["TaskCompleted"]
    tick: int
    actor: PlayerId
    task_id: TaskId
    progress: int
    required_ticks: int


@dataclass(frozen=True)
class KilledEvent:
    type: Literal["Killed"]
    tick: int
    actor: PlayerId
    target: PlayerId
    room: RoomId
    witnesses: tuple[PlayerId, ...]


@dataclass(frozen=True)
class VentEnteredEvent:
    type: Literal["VentEntered"]
    tick: int
    actor: PlayerId
    vent_id: str
    room: RoomId
    source_vent_id: str
    destination_vent_id: str
    source_room: RoomId
    destination_room: RoomId
    traversal_ticks: int
    witnesses: tuple[PlayerId, ...]
    source_witnesses: tuple[PlayerId, ...]
    destination_witnesses: tuple[PlayerId, ...]


@dataclass(frozen=True)
class VentExitedEvent:
    type: Literal["VentExited"]
    tick: int
    actor: PlayerId
    vent_id: str
    room: RoomId
    source_vent_id: str
    destination_vent_id: str
    source_room: RoomId
    destination_room: RoomId
    traversal_ticks: int
    witnesses: tuple[PlayerId, ...]
    source_witnesses: tuple[PlayerId, ...]
    destination_witnesses: tuple[PlayerId, ...]


@dataclass(frozen=True)
class SabotageStartedEvent:
    type: Literal["SabotageStarted"]
    tick: int
    actor: PlayerId
    kind: str
    duration_ticks: int
    affected_rooms: tuple[RoomId, ...]


@dataclass(frozen=True)
class SabotageRepairProgressedEvent:
    type: Literal["SabotageRepairProgressed"]
    tick: int
    actor: PlayerId
    kind: str
    room: RoomId
    progress: int
    required_ticks: int


@dataclass(frozen=True)
class SabotageRepairedEvent:
    type: Literal["SabotageRepaired"]
    tick: int
    actor: PlayerId
    kind: str
    room: RoomId
    progress: int
    required_ticks: int


@dataclass(frozen=True)
class MeetingTriggeredEvent:
    type: Literal["MeetingTriggered"]
    tick: int
    actor: PlayerId
    trigger: Literal["report", "emergency"]
    body_id: BodyId | None = None


@dataclass(frozen=True)
class WaitedEvent:
    type: Literal["Waited"]
    tick: int
    actor: PlayerId


@dataclass(frozen=True)
class GameOverEvent:
    type: Literal["GameOver"]
    tick: int
    winner: Literal["CREWMATES", "IMPOSTORS"]
    reason: WinResultType


@dataclass(frozen=True)
class TickAdvancedEvent:
    type: Literal["TickAdvanced"]
    tick: int


EngineEvent: TypeAlias = (
    ActionRejectedEvent
    | MovedEvent
    | TaskProgressedEvent
    | TaskCompletedEvent
    | KilledEvent
    | VentEnteredEvent
    | VentExitedEvent
    | SabotageStartedEvent
    | SabotageRepairProgressedEvent
    | SabotageRepairedEvent
    | MeetingTriggeredEvent
    | WaitedEvent
    | GameOverEvent
    | TickAdvancedEvent
)


def event_to_dict(event: object) -> dict[str, Any]:
    if isinstance(event, ActionRejectedEvent):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "action": event.action,
            "reason": event.reason,
        }
    if isinstance(event, MovedEvent):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": {"from_room": event.from_room, "to_room": event.to_room},
        }
    if isinstance(event, (TaskProgressedEvent, TaskCompletedEvent)):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": {
                "task_id": event.task_id,
                "progress": event.progress,
                "required_ticks": event.required_ticks,
            },
        }
    if isinstance(event, KilledEvent):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": {
                "target": event.target,
                "room": event.room,
                "witnesses": event.witnesses,
            },
        }
    if isinstance(event, (VentEnteredEvent, VentExitedEvent)):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": {
                "vent_id": event.vent_id,
                "room": event.room,
                "source_vent_id": event.source_vent_id,
                "destination_vent_id": event.destination_vent_id,
                "source_room": event.source_room,
                "destination_room": event.destination_room,
                "traversal_ticks": event.traversal_ticks,
                "witnesses": event.witnesses,
                "source_witnesses": event.source_witnesses,
                "destination_witnesses": event.destination_witnesses,
            },
        }
    if isinstance(event, SabotageStartedEvent):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": {
                "kind": event.kind,
                "duration_ticks": event.duration_ticks,
                "affected_rooms": event.affected_rooms,
            },
        }
    if isinstance(event, (SabotageRepairProgressedEvent, SabotageRepairedEvent)):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": {
                "kind": event.kind,
                "room": event.room,
                "progress": event.progress,
                "required_ticks": event.required_ticks,
            },
        }
    if isinstance(event, MeetingTriggeredEvent):
        details: dict[str, str] = {"trigger": event.trigger}
        if event.body_id is not None:
            details["body_id"] = event.body_id
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": details,
        }
    if isinstance(event, WaitedEvent):
        return {
            "type": event.type,
            "tick": event.tick,
            "actor": event.actor,
            "details": {},
        }
    if isinstance(event, GameOverEvent):
        return {
            "type": event.type,
            "tick": event.tick,
            "winner": event.winner,
            "reason": event.reason,
        }
    if isinstance(event, TickAdvancedEvent):
        return {"type": event.type, "tick": event.tick}
    raise TypeError(f"unsupported engine event type: {type(event).__name__}")
