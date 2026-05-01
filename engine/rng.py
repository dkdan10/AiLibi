from __future__ import annotations

from dataclasses import dataclass
import ast
import random


@dataclass(frozen=True)
class EngineRng:
    """Deterministic RNG wrapper with explicit serialized state threading."""

    _random: random.Random

    @classmethod
    def from_seed(cls, seed: int) -> EngineRng:
        return cls(_random=random.Random(seed))

    @classmethod
    def from_state(cls, state: bytes) -> EngineRng:
        value = random.Random()
        value.setstate(ast.literal_eval(state.decode("utf-8")))
        return cls(_random=value)

    def snapshot(self) -> bytes:
        return repr(self._random.getstate()).encode("utf-8")

    def randint(self, a: int, b: int) -> tuple[int, bytes]:
        value = self._random.randint(a, b)
        return value, self.snapshot()
