from __future__ import annotations

import json
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class EngineRng:
    """Deterministic RNG wrapper with explicit serialized state threading.

    State is serialized as UTF-8 JSON of ``random.Random.getstate()``: a
    ``{"v": version, "s": [...internal...], "g": gauss_next}`` payload. The
    inner state list is re-tupled before ``setstate`` so the encoding is
    Python-version-portable rather than coupled to a pickle protocol.
    """

    _random: random.Random

    @classmethod
    def from_seed(cls, seed: int) -> EngineRng:
        return cls(_random=random.Random(seed))

    @classmethod
    def from_state(cls, state: bytes) -> EngineRng:
        payload = json.loads(state.decode("utf-8"))
        inner = random.Random()
        inner.setstate((payload["v"], tuple(payload["s"]), payload["g"]))
        return cls(_random=inner)

    def snapshot(self) -> bytes:
        version, internal, gauss = self._random.getstate()
        payload = {"v": version, "s": list(internal), "g": gauss}
        return json.dumps(payload, separators=(",", ":")).encode("utf-8")

    def randint(self, a: int, b: int) -> tuple[int, bytes]:
        value = self._random.randint(a, b)
        return value, self.snapshot()
