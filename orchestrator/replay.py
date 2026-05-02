from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

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
    return [action.model_dump(mode="json") for action in actions]


def _state_hash(state: WorldState) -> str:
    serialized_state = _stable_json(_serialize_world_state(state)).encode("utf-8")
    return hashlib.sha256(serialized_state).hexdigest()


def _serialize_world_state(state: WorldState) -> dict[str, Any]:
    return {
        "tick": state.tick,
        "phase": state.phase,
        "map": state.map,
        "players": {player_id: _serialize_model(player) for player_id, player in state.players.items()},
        "bodies": {body_id: _serialize_model(body) for body_id, body in state.bodies.items()},
        "tasks": {task_id: _serialize_model(task) for task_id, task in state.tasks.items()},
        "sabotage": _serialize_model(state.sabotage),
        "cooldowns": dict(state.cooldowns),
        "rng_state": state.rng_state.hex(),
        "seed": state.seed,
    }


def _serialize_model(model: Any) -> Any:
    if model is None:
        return None
    return model.model_dump(mode="json")


def _stable_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
