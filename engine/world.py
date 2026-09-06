from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, TypeVar, cast

import yaml

from engine.entities import (
    BodyId,
    BodyState,
    PlayerId,
    PlayerState,
    SabotageState,
    TaskInstanceId,
    TaskState,
)

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MapId: TypeAlias = str
RoomId: TypeAlias = str
VentId: TypeAlias = str
TaskId: TypeAlias = str

RoomKind: TypeAlias = Literal["hallway", "room", "task_room", "meeting_room", "utility"]
EdgeKind: TypeAlias = Literal["doorway", "hallway"]
TaskType: TypeAlias = Literal["short", "long", "common"]
VisibilityMode: TypeAlias = Literal["same_room_and_adjacent", "same_room_only"]
# The dead-crewmate task rule (DESIGN.md §3.5). ``drop`` (the default) DELETES a
# dead crewmate's incomplete task instances; ``redistribute`` RE-KEYS each to a
# living crewmate so the task burden does not shrink on death. Default ``drop``
# keeps the committed replays + their state-hash verify byte-identical; the
# canonical flip to ``redistribute`` is the 13.12 re-record.
DeadTaskRule: TypeAlias = Literal["drop", "redistribute"]

_ROOM_OR_VENT_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
_TASK_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_CANONICAL_MAP_PATH = Path(__file__).resolve().parent / "maps" / "canonical_1.yaml"
_MappingKey = TypeVar("_MappingKey")
_MappingValue = TypeVar("_MappingValue")


class MapValidationError(ValueError):
    """Raised when map data violates the static engine map contract."""


@dataclass(frozen=True)
class WorldState:
    tick: int
    phase: Literal["PLAY", "MEETING", "GAME_OVER"]
    map: MapId
    players: Mapping[PlayerId, PlayerState]
    bodies: Mapping[BodyId, BodyState]
    # Per-player task instances (DESIGN.md §3.2): keyed by the composite instance
    # id ``"{owner}:{map_task_id}"`` (a ``TaskInstanceId``), NOT by the map task
    # id, so several crewmates can each hold an instance of the same map task with
    # independent progress. The agent-facing id stays the map id; the engine
    # resolves ``(actor, map_task_id)`` to the actor's own instance.
    tasks: Mapping[TaskInstanceId, TaskState]
    sabotage: SabotageState | None
    cooldowns: Mapping[PlayerId, int]
    emergency_uses: Mapping[PlayerId, int]
    rng_state: bytes
    seed: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "players", _readonly_mapping(self.players))
        object.__setattr__(self, "bodies", _readonly_mapping(self.bodies))
        object.__setattr__(self, "tasks", _readonly_mapping(self.tasks))
        object.__setattr__(self, "cooldowns", _readonly_mapping(self.cooldowns))
        object.__setattr__(
            self, "emergency_uses", _readonly_mapping(self.emergency_uses)
        )


def _readonly_mapping(
    source: Mapping[_MappingKey, _MappingValue],
) -> Mapping[_MappingKey, _MappingValue]:
    return MappingProxyType(dict(source))


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Position(_FrozenModel):
    x: int
    y: int

    @model_validator(mode="after")
    def validate_non_negative(self) -> Position:
        if self.x < 0 or self.y < 0:
            raise MapValidationError("room positions must be non-negative")
        return self


class Size(_FrozenModel):
    width: int
    height: int

    @model_validator(mode="after")
    def validate_positive(self) -> Size:
        if self.width <= 0 or self.height <= 0:
            raise MapValidationError("room sizes must be positive")
        return self


class VisibilityDefaults(_FrozenModel):
    base: VisibilityMode
    lights_sabotage: VisibilityMode


class Room(_FrozenModel):
    id: RoomId
    name: str
    kind: RoomKind
    position: Position
    size: Size
    notes: str = ""

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: RoomId) -> RoomId:
        if _ROOM_OR_VENT_ID_PATTERN.fullmatch(value) is None:
            raise MapValidationError(f"invalid room id: {value}")
        return value


class Edge(_FrozenModel):
    from_room: RoomId = Field(alias="from")
    to_room: RoomId = Field(alias="to")
    kind: EdgeKind
    traversal_ticks: int
    door_id: str | None

    @model_validator(mode="after")
    def validate_edge(self) -> Edge:
        if self.traversal_ticks < 1:
            raise MapValidationError("edge traversal_ticks must be at least 1")
        if self.traversal_ticks != 1:
            raise MapValidationError(
                "edge traversal_ticks must be 1; multi-tick traversal is unsupported"
            )
        if self.from_room == self.to_room:
            raise MapValidationError(
                f"edge cannot connect a room to itself: {self.from_room}"
            )
        return self


class Vent(_FrozenModel):
    id: VentId
    room: RoomId
    connects_to: tuple[VentId, ...]
    traversal_ticks: int

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: VentId) -> VentId:
        if _ROOM_OR_VENT_ID_PATTERN.fullmatch(value) is None:
            raise MapValidationError(f"invalid vent id: {value}")
        if not value.endswith("_VENT"):
            raise MapValidationError(f"vent id must end with _VENT: {value}")
        return value

    @model_validator(mode="after")
    def validate_vent(self) -> Vent:
        if self.traversal_ticks < 1:
            raise MapValidationError("vent traversal_ticks must be at least 1")
        if self.traversal_ticks != 1:
            raise MapValidationError(
                "vent traversal_ticks must be 1; multi-tick traversal is unsupported"
            )
        if self.id in self.connects_to:
            raise MapValidationError(f"vent cannot connect to itself: {self.id}")
        return self


class TaskDefinition(_FrozenModel):
    id: TaskId
    name: str
    room: RoomId
    duration_ticks: int
    task_type: TaskType
    weight: int

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: TaskId) -> TaskId:
        if _TASK_ID_PATTERN.fullmatch(value) is None:
            raise MapValidationError(f"invalid task id: {value}")
        return value

    @model_validator(mode="after")
    def validate_task(self) -> TaskDefinition:
        if self.duration_ticks < 1:
            raise MapValidationError("task duration_ticks must be at least 1")
        if self.weight < 1:
            raise MapValidationError("task weight must be at least 1")
        return self


class SabotageDefinition(_FrozenModel):
    affected_visibility: VisibilityMode
    repair_rooms: tuple[RoomId, ...]
    duration_ticks: int
    repair_ticks: int = 3
    # Whether an active instance of this sabotage HALTS the crew task race
    # (DESIGN.md §3.1 tick loop, §8.3 sabotage). Declared in data so the engine
    # gates on a flag, not by string-matching ``kind`` (the codebase deliberately
    # avoids kind string-matching). Defaulted ``False`` so ``lights`` and every
    # existing map-loader pin stay byte-stable; only a gating kind (``reactor``)
    # sets it true.
    gates_tasks: bool = False

    @model_validator(mode="after")
    def validate_sabotage(self) -> SabotageDefinition:
        if self.duration_ticks < 1:
            raise MapValidationError("sabotage duration_ticks must be at least 1")
        if self.repair_ticks < 1:
            raise MapValidationError("sabotage repair_ticks must be at least 1")
        return self


class EmergencyConfig(_FrozenModel):
    button_room: RoomId
    uses_per_player: int

    @model_validator(mode="after")
    def validate_emergency(self) -> EmergencyConfig:
        if self.uses_per_player < 1:
            raise MapValidationError("emergency uses_per_player must be at least 1")
        return self


class SpawnConfig(_FrozenModel):
    room: RoomId


class MeetingConfig(_FrozenModel):
    room: RoomId


class Map(_FrozenModel):
    id: MapId = Field(alias="map_id")
    name: str
    version: str
    tick_rate_hz: int
    kill_cooldown_ticks: int
    dead_task_rule: DeadTaskRule = "drop"
    visibility_defaults: VisibilityDefaults
    rooms: Mapping[RoomId, Room]
    edges: tuple[Edge, ...]
    vents: Mapping[VentId, Vent]
    tasks: Mapping[TaskId, TaskDefinition]
    sabotages: Mapping[str, SabotageDefinition]
    emergency: EmergencyConfig
    spawn: SpawnConfig
    meeting: MeetingConfig

    @model_validator(mode="before")
    @classmethod
    def attach_ids(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        prepared = dict(data)
        for field_name in ("rooms", "vents", "tasks"):
            if field_name in prepared:
                prepared[field_name] = _attach_mapping_ids(
                    field_name=field_name,
                    raw_items=prepared[field_name],
                )
        return prepared

    @model_validator(mode="after")
    def validate_map(self) -> Map:
        if self.tick_rate_hz <= 0:
            raise MapValidationError("tick_rate_hz must be positive")
        if self.kill_cooldown_ticks < 1:
            raise MapValidationError("kill_cooldown_ticks must be at least 1")
        self._validate_disjoint_namespaces()
        self._validate_room_graph()
        self._validate_vent_network()
        self._validate_tasks()
        self._validate_sabotages()
        self._validate_special_rooms()
        object.__setattr__(self, "rooms", _readonly_mapping(self.rooms))
        object.__setattr__(self, "vents", _readonly_mapping(self.vents))
        object.__setattr__(self, "tasks", _readonly_mapping(self.tasks))
        object.__setattr__(self, "sabotages", _readonly_mapping(self.sabotages))
        return self

    def room_neighbors(self, room_id: RoomId) -> tuple[RoomId, ...]:
        if room_id not in self.rooms:
            raise MapValidationError(f"unknown room id: {room_id}")
        neighbors: set[RoomId] = set()
        for edge in self.edges:
            if edge.from_room == room_id:
                neighbors.add(edge.to_room)
            if edge.to_room == room_id:
                neighbors.add(edge.from_room)
        return tuple(sorted(neighbors))

    def vent_neighbors(self, vent_id: VentId) -> tuple[VentId, ...]:
        if vent_id not in self.vents:
            raise MapValidationError(f"unknown vent id: {vent_id}")
        return tuple(sorted(self.vents[vent_id].connects_to))

    def vent_for_room(self, room_id: RoomId) -> Vent | None:
        if room_id not in self.rooms:
            raise MapValidationError(f"unknown room id: {room_id}")
        matching_vents = [vent for vent in self.vents.values() if vent.room == room_id]
        if len(matching_vents) > 1:
            raise MapValidationError(f"room has multiple vents: {room_id}")
        return matching_vents[0] if matching_vents else None

    def _validate_disjoint_namespaces(self) -> None:
        # These are the MAP's room / vent / task ids (the agent-facing keyspace),
        # NOT ``WorldState.tasks`` (which is re-keyed per-player to the composite
        # ``"{owner}:{map_task_id}"`` instance id — DESIGN.md §3.2). The composite
        # instance keyspace embeds a ``:`` separator, which no map id can contain
        # (map task ids match ``^[a-z][a-z0-9_]*$``), so it stays disjoint from
        # these namespaces by construction.
        room_ids = set(self.rooms)
        vent_ids = set(self.vents)
        task_ids = set(self.tasks)
        reused_ids = (
            (room_ids & vent_ids) | (room_ids & task_ids) | (vent_ids & task_ids)
        )
        if reused_ids:
            joined = ", ".join(sorted(reused_ids))
            raise MapValidationError(f"map ids must be namespace-disjoint: {joined}")

    def _validate_room_graph(self) -> None:
        for edge in self.edges:
            for room_id in (edge.from_room, edge.to_room):
                if room_id not in self.rooms:
                    raise MapValidationError(f"edge references unknown room: {room_id}")

        if "CAFETERIA" not in self.rooms:
            raise MapValidationError("canonical room graph requires CAFETERIA")

        visited = {"CAFETERIA"}
        frontier = ["CAFETERIA"]
        while frontier:
            current = frontier.pop()
            for neighbor in self.room_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    frontier.append(neighbor)

        missing = set(self.rooms) - visited
        if missing:
            joined = ", ".join(sorted(missing))
            raise MapValidationError(f"room graph is not fully connected: {joined}")

    def _validate_vent_network(self) -> None:
        for vent in self.vents.values():
            if vent.room not in self.rooms:
                raise MapValidationError(f"vent references unknown room: {vent.room}")
            for connected_id in vent.connects_to:
                if connected_id not in self.vents:
                    raise MapValidationError(
                        f"vent {vent.id} references unknown vent: {connected_id}"
                    )
                reverse_connections = self.vents[connected_id].connects_to
                if vent.id not in reverse_connections:
                    raise MapValidationError(
                        f"vent link must be symmetric: {vent.id} -> {connected_id}"
                    )

    def _validate_tasks(self) -> None:
        for task in self.tasks.values():
            room = self.rooms.get(task.room)
            if room is None:
                raise MapValidationError(f"task references unknown room: {task.room}")
            if room.kind == "hallway":
                raise MapValidationError(f"task assigned to hallway: {task.id}")

    def _validate_sabotages(self) -> None:
        for sabotage_id, sabotage in self.sabotages.items():
            for room_id in sabotage.repair_rooms:
                if room_id not in self.rooms:
                    raise MapValidationError(
                        f"sabotage {sabotage_id} references unknown room: {room_id}"
                    )

    def _validate_special_rooms(self) -> None:
        special_rooms = {
            "emergency.button_room": self.emergency.button_room,
            "spawn.room": self.spawn.room,
            "meeting.room": self.meeting.room,
        }
        for label, room_id in special_rooms.items():
            if room_id not in self.rooms:
                raise MapValidationError(f"{label} references unknown room: {room_id}")


def _attach_mapping_ids(
    *, field_name: str, raw_items: object
) -> dict[str, dict[str, object]]:
    if not isinstance(raw_items, Mapping):
        raise MapValidationError(f"{field_name} must be a mapping")

    prepared_items: dict[str, dict[str, object]] = {}
    for item_id, raw_item in raw_items.items():
        if not isinstance(item_id, str):
            raise MapValidationError(f"{field_name} ids must be strings")
        if not isinstance(raw_item, Mapping):
            raise MapValidationError(f"{field_name}.{item_id} must be a mapping")

        item_data = dict(raw_item)
        embedded_id = item_data.get("id")
        if embedded_id is not None and embedded_id != item_id:
            raise MapValidationError(
                f"{field_name}.{item_id} embedded id must match mapping key"
            )
        item_data["id"] = item_id
        prepared_items[item_id] = item_data
    return prepared_items


def load_canonical_map() -> Map:
    return load_map(_CANONICAL_MAP_PATH)


def load_map(path: Path) -> Map:
    data = _load_map_yaml(path)
    return Map.model_validate(data)


def _load_map_yaml(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, dict):
        raise MapValidationError("map file must contain a top-level mapping")
    return cast(dict[str, object], parsed)
