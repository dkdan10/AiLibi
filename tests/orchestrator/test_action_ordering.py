from __future__ import annotations

from pydantic import TypeAdapter
import pytest

from engine.actions import Action
from orchestrator.action_ordering import (
    ActionBatchValidationError,
    order_actions_for_tick,
)

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _action(data: object) -> Action:
    return _ACTION_ADAPTER.validate_python(data)


def test_order_actions_for_tick_sorts_by_actor_without_mutating_input() -> None:
    actions = [
        _action({"type": "wait", "actor": "player-2", "payload": {}}),
        _action(
            {
                "type": "move",
                "actor": "player-1",
                "payload": {"to_room": "ADMIN"},
            }
        ),
        _action({"type": "wait", "actor": "impostor-1", "payload": {}}),
    ]

    ordered = order_actions_for_tick(actions)

    assert [action.actor for action in ordered] == [
        "impostor-1",
        "player-1",
        "player-2",
    ]
    assert [action.actor for action in actions] == [
        "player-2",
        "player-1",
        "impostor-1",
    ]


def test_order_actions_for_tick_rejects_duplicate_actor_actions() -> None:
    actions = [
        _action({"type": "wait", "actor": "player-1", "payload": {}}),
        _action(
            {
                "type": "move",
                "actor": "player-1",
                "payload": {"to_room": "ADMIN"},
            }
        ),
    ]

    with pytest.raises(ActionBatchValidationError, match="player-1"):
        order_actions_for_tick(actions)
