from __future__ import annotations

from collections.abc import Sequence
import json

from engine.actions import Action


def order_actions_for_tick(actions: Sequence[Action]) -> tuple[Action, ...]:
    """Return the deterministic action order future async dispatch must use."""

    return tuple(sorted(actions, key=_action_order_key))


def _action_order_key(action: Action) -> tuple[str, str, str]:
    action_payload = json.dumps(
        action.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
    )
    return action.actor, action.type, action_payload
