from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from engine.actions import Action
from engine.entities import PlayerId, SabotageState, TaskState
from engine.rng import EngineRng
from engine.rules import ActionRejectedError, resolve_win_conditions
from engine.world import WorldState


EngineEvent = dict[str, Any]


def _decrement_cooldowns(state: WorldState) -> dict[PlayerId, int]:
    return {player_id: max(0, ticks - 1) for player_id, ticks in state.cooldowns.items()}


def _advance_sabotage(sabotage: SabotageState | None) -> SabotageState | None:
    if sabotage is None or not sabotage.active:
        return sabotage
    return replace(sabotage, remaining_ticks=max(0, sabotage.remaining_ticks - 1))


def _advance_tasks(tasks: dict[str, TaskState]) -> dict[str, TaskState]:
    return tasks


def advance_tick(state: WorldState, actions: Sequence[Action]) -> tuple[WorldState, list[EngineEvent]]:
    """Advance one engine tick using the DESIGN.md §3.1 seven-step loop."""

    events: list[EngineEvent] = []

    # 1) Apply queued actions from previous tick.
    for action in actions:
        try:
            _ = action
        except ActionRejectedError as exc:
            events.append({"type": "ActionRejected", "tick": state.tick, "reason": str(exc)})

    # 2) Resolve passive effects.
    cooldowns = _decrement_cooldowns(state)
    sabotage = _advance_sabotage(state.sabotage)
    tasks = _advance_tasks(dict(state.tasks))

    working_state = replace(state, cooldowns=cooldowns, sabotage=sabotage, tasks=tasks)

    # 3) Check victory.
    win_result = resolve_win_conditions(working_state)
    if win_result is not None:
        game_over_state = replace(working_state, phase="GAME_OVER")
        events.append(
            {
                "type": "GameOver",
                "tick": state.tick,
                "winner": win_result.winner,
                "reason": win_result.reason,
            }
        )
        return game_over_state, events

    # 4) Compute observations (owned by observation service; placeholder event).
    events.append({"type": "ObservationsComputed", "tick": state.tick})

    # 5) Solicit actions (owned by orchestrator/agents; placeholder event).
    events.append({"type": "ActionsSolicited", "tick": state.tick})

    # RNG state is explicitly threaded through the tick transition.
    rng = EngineRng.from_state(state.rng_state)
    _, next_rng_state = rng.randint(0, 2**31 - 1)

    next_state = replace(working_state, tick=state.tick + 1, rng_state=next_rng_state)

    # 6) Emit tick event.
    events.append({"type": "TickAdvanced", "tick": next_state.tick})

    # 7) Tick increment happens in next_state above.
    return next_state, events
