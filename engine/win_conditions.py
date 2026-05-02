from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from engine.world import WorldState

WinResultType = Literal["CREWMATE_TASKS", "IMPOSTOR_PARITY", "IMPOSTOR_SABOTAGE"]


@dataclass(frozen=True)
class WinResult:
    winner: Literal["CREWMATES", "IMPOSTORS"]
    reason: WinResultType


def evaluate_win_conditions(state: WorldState) -> WinResult | None:
    """Evaluate win conditions in the strict DESIGN.md §3.5 order."""
    total_tasks = len(state.tasks)
    completed_tasks = sum(1 for task in state.tasks.values() if task.completed)
    if completed_tasks == total_tasks and total_tasks > 0:
        return WinResult(winner="CREWMATES", reason="CREWMATE_TASKS")

    alive_players = [player for player in state.players.values() if player.alive]
    alive_impostors = sum(1 for player in alive_players if player.role == "IMPOSTOR")
    alive_crewmates = sum(1 for player in alive_players if player.role == "CREWMATE")
    if alive_impostors >= alive_crewmates:
        return WinResult(winner="IMPOSTORS", reason="IMPOSTOR_PARITY")

    if (
        state.sabotage is not None
        and state.sabotage.active
        and state.sabotage.remaining_ticks == 0
    ):
        return WinResult(winner="IMPOSTORS", reason="IMPOSTOR_SABOTAGE")

    return None
