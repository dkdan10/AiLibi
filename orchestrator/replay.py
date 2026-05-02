from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from engine.actions import Action
from engine.world import WorldState


class ReplayLog:
    """Append-only JSONL replay log for deterministic game replays."""

    def __init__(self, path: Path, game_id: str) -> None:
        self._path = path
        self._game_id = game_id
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def game_id(self) -> str:
        return self._game_id

    def record_tick(self, tick: int, actions: list[Action], state: WorldState) -> None:
        entry = {
            "game_id": self._game_id,
            "tick": tick,
            "actions": _serialize_actions(actions),
            "state_hash": _state_hash(state),
        }
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(_stable_json(entry))
            handle.write("\n")


def _serialize_actions(actions: list[Action]) -> list[dict[str, Any]]:
    serialized_actions: list[dict[str, Any]] = []
    for action in actions:
        serialized = _to_jsonable(action)
        if not isinstance(serialized, dict):
            raise TypeError(f"action did not serialize to object: {type(action).__name__}")
        serialized_actions.append(serialized)
    return serialized_actions


def _state_hash(state: WorldState) -> str:
    serialized_state = _stable_json(_serialize_world_state(state)).encode("utf-8")
    return hashlib.sha256(serialized_state).hexdigest()


def _serialize_world_state(state: WorldState) -> dict[str, Any]:
    serialized = _to_jsonable(state)
    if not isinstance(serialized, dict):
        raise TypeError("world state did not serialize to object")
    return serialized


def _to_jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, BaseModel):
        return _to_jsonable(value.model_dump(mode="json"))
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _to_jsonable(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        serialized_mapping: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"unsupported mapping key type: {type(key).__name__}")
            serialized_mapping[key] = _to_jsonable(item)
        return serialized_mapping
    if isinstance(value, tuple):
        return [_to_jsonable(item) for item in value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_to_jsonable(item) for item in value]
    raise TypeError(f"unsupported replay serialization type: {type(value).__name__}")


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
