"""A cooperative wall deadline shared by every game in a tournament."""

from __future__ import annotations

import math
import time
import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

_T = TypeVar("_T")


class RunDeadlineExceeded(RuntimeError):
    """The tournament's elapsed wall allowance has been consumed."""


class RunDeadline:
    """Check between ticks and bound asynchronous meeting work with one clock.

    Synchronous Python is not preempted. The next orchestration boundary raises
    after a long tick; asynchronous meeting work is cancelled at the deadline.
    """

    def __init__(
        self, seconds: float, *, clock: Callable[[], float] = time.monotonic
    ) -> None:
        if not math.isfinite(seconds) or seconds < 0:
            raise ValueError("remaining wall seconds must be finite and non-negative")
        self._clock = clock
        self._end = clock() + seconds

    def remaining(self) -> float:
        remaining = self._end - self._clock()
        if remaining <= 0:
            raise RunDeadlineExceeded("Tournament wall-time limit reached")
        return remaining

    def check(self) -> None:
        self.remaining()

    async def run(self, work: Coroutine[Any, Any, _T]) -> _T:
        """Cancel awaited work at the same deadline used between game ticks."""
        try:
            seconds = self.remaining()
        except RunDeadlineExceeded:
            work.close()
            raise
        timeout = asyncio.timeout(seconds)
        try:
            async with timeout:
                return await work
        except TimeoutError as exc:
            if timeout.expired():
                raise RunDeadlineExceeded("Tournament wall-time limit reached") from exc
            raise
