from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from dataclasses import dataclass
from typing import Any, Literal, TypeAlias, TypeVar, cast

from engine.entities import (
    BodyId,
    BodyState,
    PlayerId,
    PlayerState,
    SabotageState,
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

_ROOM_OR_VENT_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
_TASK_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
_CANONICAL_MAP_PATH = Path(__file__).resolve().parent / "maps" / "canonical_1.yaml"
_MappingKey = TypeVar("_MappingKey")
_MappingValue = TypeVar("_MappingValue")


class MapValidationError(ValueError):
    """Raised when map data violates the static engine map contract."""


class Phase(str):
    PLAY = "PLAY"
    MEETING = "MEETING"
    GAME_OVER = "GAME_OVER"


@dataclass(frozen=True)
class WorldState:
    tick: int
    phase: Literal["PLAY", "MEETING", "GAME_OVER"]
    map: MapId
    players: Mapping[PlayerId, PlayerState]
    bodies: Mapping[BodyId, BodyState]
    tasks: Mapping[TaskId, TaskState]
    sabotage: SabotageState | None
    cooldowns: Mapping[PlayerId, int]
    rng_state: bytes
    seed: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "players", _readonly_mapping(self.players))
        object.__setattr__(self, "bodies", _readonly_mapping(self.bodies))
        object.__setattr__(self, "tasks", _readonly_mapping(self.tasks))
        object.__setattr__(self, "cooldowns", _readonly_mapping(self.cooldowns))


def _readonly_mapping(
    source: Mapping[_MappingKey, _MappingValue],
) -> Mapping[_MappingKey, _MappingValue]:
    return MappingProxyType(dict(source))


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True)


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

    @model_validator(mode="after")
    def validate_sabotage(self) -> SabotageDefinition:
        if self.duration_ticks < 1:
            raise MapValidationError("sabotage duration_ticks must be at least 1")
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
    visibility_defaults: VisibilityDefaults
    rooms: dict[RoomId, Room]
    edges: tuple[Edge, ...]
    vents: dict[VentId, Vent]
    tasks: dict[TaskId, TaskDefinition]
    sabotages: dict[str, SabotageDefinition]
    emergency: EmergencyConfig
    spawn: SpawnConfig
    meeting: MeetingConfig

    @model_validator(mode="before")
    @classmethod
    def attach_ids(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        raw_rooms = data.get("rooms")
        if isinstance(raw_rooms, dict):
            data["rooms"] = {
                room_id: {**room_data, "id": room_id}
                for room_id, room_data in raw_rooms.items()
                if isinstance(room_data, dict)
            }
        raw_vents = data.get("vents")
        if isinstance(raw_vents, dict):
            data["vents"] = {
                vent_id: {**vent_data, "id": vent_id}
                for vent_id, vent_data in raw_vents.items()
                if isinstance(vent_data, dict)
            }
        raw_tasks = data.get("tasks")
        if isinstance(raw_tasks, dict):
            data["tasks"] = {
                task_id: {**task_data, "id": task_id}
                for task_id, task_data in raw_tasks.items()
                if isinstance(task_data, dict)
            }
        return data

    @model_validator(mode="after")
    def validate_map(self) -> Map:
        if self.tick_rate_hz <= 0:
            raise MapValidationError("tick_rate_hz must be positive")
        self._validate_disjoint_namespaces()
        self._validate_room_graph()
        self._validate_vent_network()
        self._validate_tasks()
        self._validate_sabotages()
        self._validate_special_rooms()
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


def load_canonical_map() -> Map:
    return load_map(_CANONICAL_MAP_PATH)


def load_map(path: Path) -> Map:
    data = _load_yaml_subset(path)
    return Map.model_validate(data)


def _load_yaml_subset(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    parser = _YamlSubsetParser(lines)
    parsed = parser.parse()
    if not isinstance(parsed, dict):
        raise MapValidationError("map file must contain a top-level mapping")
    return cast(dict[str, object], parsed)


class _YamlSubsetParser:
    def __init__(self, lines: list[str]) -> None:
        self._lines = lines
        self._index = 0

    def parse(self) -> object:
        self._skip_ignored()
        if self._index >= len(self._lines):
            raise MapValidationError("map file is empty")
        return self._parse_mapping(self._current_indent())

    def _parse_mapping(self, indent: int) -> dict[str, object]:
        result: dict[str, object] = {}
        while self._index < len(self._lines):
            self._skip_ignored()
            if self._index >= len(self._lines) or self._current_indent() < indent:
                break
            if self._current_indent() > indent:
                raise MapValidationError(
                    f"unexpected indentation at line {self._index + 1}"
                )

            content = self._current_content()
            if content.startswith("- "):
                raise MapValidationError(
                    f"unexpected list item at line {self._index + 1}"
                )

            key, raw_value = self._split_key_value(content)
            self._index += 1
            if raw_value == "":
                result[key] = self._parse_nested_value(indent)
            elif raw_value in {">", "|"}:
                result[key] = self._parse_block_scalar(indent)
            else:
                result[key] = self._parse_scalar(raw_value)
        return result

    def _parse_sequence(self, indent: int) -> list[object]:
        result: list[object] = []
        while self._index < len(self._lines):
            self._skip_ignored()
            if self._index >= len(self._lines) or self._current_indent() < indent:
                break
            if self._current_indent() > indent:
                raise MapValidationError(
                    f"unexpected indentation at line {self._index + 1}"
                )

            content = self._current_content()
            if not content.startswith("- "):
                break
            raw_value = content[2:].strip()
            self._index += 1
            if raw_value == "":
                result.append(self._parse_nested_value(indent))
            else:
                result.append(self._parse_scalar(raw_value))
        return result

    def _parse_nested_value(self, parent_indent: int) -> object:
        self._skip_ignored()
        if self._index >= len(self._lines) or self._current_indent() <= parent_indent:
            raise MapValidationError(
                f"missing nested value near line {self._index + 1}"
            )
        nested_indent = self._current_indent()
        if self._current_content().startswith("- "):
            return self._parse_sequence(nested_indent)
        return self._parse_mapping(nested_indent)

    def _parse_block_scalar(self, parent_indent: int) -> str:
        block_lines: list[str] = []
        while self._index < len(self._lines):
            raw_line = self._lines[self._index]
            if not raw_line.strip():
                block_lines.append("")
                self._index += 1
                continue
            current_indent = len(raw_line) - len(raw_line.lstrip(" "))
            if current_indent <= parent_indent:
                break
            block_lines.append(raw_line.strip())
            self._index += 1
        return " ".join(line for line in block_lines if line).strip()

    def _split_key_value(self, content: str) -> tuple[str, str]:
        if ":" not in content:
            raise MapValidationError(
                f"expected key/value pair at line {self._index + 1}"
            )
        key, raw_value = content.split(":", 1)
        key = key.strip()
        if not key:
            raise MapValidationError(f"empty key at line {self._index + 1}")
        return key, raw_value.strip()

    def _parse_scalar(self, raw_value: str) -> object:
        if raw_value == "null":
            return None
        if raw_value.startswith("{") and raw_value.endswith("}"):
            return self._parse_inline_mapping(raw_value)
        if raw_value.startswith("[") and raw_value.endswith("]"):
            return self._parse_inline_sequence(raw_value)
        if raw_value.isdecimal():
            return int(raw_value)
        return raw_value.strip("\"'")

    def _parse_inline_mapping(self, raw_value: str) -> dict[str, object]:
        inner = raw_value[1:-1].strip()
        if not inner:
            return {}
        result: dict[str, object] = {}
        for item in inner.split(","):
            key, value = self._split_inline_key_value(item.strip())
            result[key] = self._parse_scalar(value)
        return result

    def _parse_inline_sequence(self, raw_value: str) -> list[object]:
        inner = raw_value[1:-1].strip()
        if not inner:
            return []
        return [self._parse_scalar(item.strip()) for item in inner.split(",")]

    def _split_inline_key_value(self, item: str) -> tuple[str, str]:
        if ":" not in item:
            raise MapValidationError(f"invalid inline mapping item: {item}")
        key, value = item.split(":", 1)
        return key.strip(), value.strip()

    def _skip_ignored(self) -> None:
        while self._index < len(self._lines):
            stripped = self._lines[self._index].strip()
            if stripped and not stripped.startswith("#"):
                return
            self._index += 1

    def _current_indent(self) -> int:
        line = self._lines[self._index]
        return len(line) - len(line.lstrip(" "))

    def _current_content(self) -> str:
        return self._lines[self._index].strip()
