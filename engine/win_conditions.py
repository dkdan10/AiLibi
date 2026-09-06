from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from engine.world import WorldState

WinResultType = Literal[
    "CREWMATE_TASKS",
    "CREWMATE_EJECT",
    "IMPOSTOR_PARITY",
    "IMPOSTOR_SABOTAGE",
]


@dataclass(frozen=True)
class WinResult:
    winner: Literal["CREWMATES", "IMPOSTORS"]
    reason: WinResultType


def evaluate_win_conditions(state: WorldState) -> WinResult | None:
    """Evaluate win conditions in the strict DESIGN.md §3.5 order."""
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

    # Impostor-elimination win (Task 6.3; audit J-J-8, I-I-3; DESIGN.md §3, §8.1).
    # With every impostor dead/ejected the crew wins immediately, before the
    # task-completion check, so a game whose last impostor is ejected before
    # tasks finish attributes to the ejection win rather than running on as a
    # zombie game (recording TICK_BUDGET_REACHED or a delayed CREWMATE_TASKS).
    # Ordered after parity and sabotage — both impostor wins — so an offensive
    # impostor action that resolves on the same tick still attributes to the
    # offense per §3.5; ordered before tasks per the design-thread intent.
    if alive_impostors == 0:
        return WinResult(winner="CREWMATES", reason="CREWMATE_EJECT")

    # Kill and ejection handlers resolve incomplete tasks under the map rule:
    # canonical redistribution reassigns them to eligible living crew, while
    # drop removes them. Completed instances remain in either case. Parity is
    # checked first, including when a death also removes the last unfinished task.
    #
    # Per-player re-key (DESIGN.md §3.2/§3.5): the count is over live task
    # *instances*, so the denominator scales with the roster (e.g. 9p/2i is 14
    # instances over the 12 map tasks). The rule is unchanged — only the
    # magnitude — and an empty instance set is not a crew win (``> 0`` guard).
    total_tasks = len(state.tasks)
    completed_tasks = sum(1 for task in state.tasks.values() if task.completed)
    if completed_tasks == total_tasks and total_tasks > 0:
        return WinResult(winner="CREWMATES", reason="CREWMATE_TASKS")

    return None
