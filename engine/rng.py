from __future__ import annotations

import pickle
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class EngineRng:
    """Deterministic RNG wrapper with explicit serialized state threading.

    State is serialized via :mod:`pickle` rather than ``repr`` of the internal
    Mersenne Twister tuple. ``pickle`` is the standard library tool designed
    for round-tripping arbitrary tuple/int structures and avoids the implicit
    coupling to CPython's ``repr`` format. Replays are local-only artifacts;
    the standard ``pickle`` trust caveat does not apply here.
    """

    _random: random.Random

    @classmethod
    def from_seed(cls, seed: int) -> EngineRng:
        return cls(_random=random.Random(seed))

    @classmethod
    def from_state(cls, state: bytes) -> EngineRng:
        value = random.Random()
        value.setstate(pickle.loads(state))
        return cls(_random=value)

    def snapshot(self) -> bytes:
        return pickle.dumps(self._random.getstate(), protocol=pickle.DEFAULT_PROTOCOL)

    def randint(self, a: int, b: int) -> tuple[int, bytes]:
        value = self._random.randint(a, b)
        return value, self.snapshot()
