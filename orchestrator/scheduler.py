"""Tick scheduler (DESIGN.md §1.4, §3.1).

Phase 2 ships a tick-budget scheduler only. Live-mode per-agent deadlines
(DESIGN.md §1.4) plug into the same object in later phases — keeping
:class:`TickScheduler` in its own module reserves the boundary now.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TickScheduler:
    """Tick-budget gate for the headless game loop.

    ``should_continue(state.tick)`` returns ``True`` until ``state.tick``
    reaches ``max_ticks``. The orchestrator polls this gate before each
    tick to ensure a runaway game terminates with a defined outcome
    instead of looping forever.
    """

    max_ticks: int

    def __post_init__(self) -> None:
        if self.max_ticks < 1:
            raise ValueError(f"max_ticks must be at least 1, got {self.max_ticks}")

    def should_continue(self, current_tick: int) -> bool:
        if current_tick < 0:
            raise ValueError(f"current_tick must be non-negative, got {current_tick}")
        return current_tick < self.max_ticks


__all__ = ["TickScheduler"]
