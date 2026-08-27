from __future__ import annotations

import json
import random
import struct
from array import array
from dataclasses import dataclass
from enum import Enum


class RngStateHashPolicy(Enum):
    """Per-tick RNG-state serialization policy (Task 15.8.1).

    :class:`EngineRng.snapshot` re-serializes the full 625-int Mersenne state on
    every draw. That serialization is hashed into every committed ``state_hash``
    (``orchestrator/replay.py``), so it is LOAD-BEARING for replay byte-identity
    and MUST NEVER change in place (audit post-phase-14-pause.md §4; the "do not
    touch in place" verifier note). This enum is the explicit, opt-in switch that
    lets a NON-RECORDED training rollout skip the expensive ``json.dumps`` of the
    Mersenne state — measured at ~43% of bare-engine cost
    (audit post-phase-14-ML-planning.md §3.5, §11.2) — while every recorded /
    committed path keeps the byte-identical default.

    * :attr:`FULL` — the DEFAULT. Serialize the Mersenne state as the
      version-portable ``{"v","s","g"}`` JSON payload, byte-identical to the
      pre-15.8.1 writer. Every recording, every committed replay, and every
      reconstruction uses this policy, so ``state_hash`` chains stay stable.
    * :attr:`TRAINING_FAST` — the OPT-IN training fast path. The draw still
      happens (the Mersenne cursor advances exactly as under :attr:`FULL`, so
      trajectories are identical), but the resulting state is serialized with a
      cheap, self-describing binary codec instead of ``json.dumps``. The bytes it
      produces are NOT the committed JSON encoding, so a ``TRAINING_FAST`` rollout
      must never be recorded — the orchestrator refuses the policy at any
      replay-writing construction (:class:`orchestrator.game.HeadlessGame`), so
      the fast bytes never reach a committed ``state_hash``.

    The policy is threaded EXPLICITLY through ``engine.tick.advance_tick`` and
    ``orchestrator.game.apply_meeting_result`` (no env-var magic; AGENTS.md "no
    silent fallbacks"). :meth:`EngineRng.from_state` is self-describing — it
    detects the codec from the bytes — so a game whose seeded ``rng_state`` is the
    JSON default can advance under :attr:`TRAINING_FAST` without a format mismatch.
    """

    FULL = "full"
    TRAINING_FAST = "training_fast"


# Self-describing marker for a :attr:`RngStateHashPolicy.TRAINING_FAST` snapshot.
# The :attr:`RngStateHashPolicy.FULL` (JSON) encoding always begins with ``{``
# (0x7B); this marker begins with ``R`` (0x52), so :meth:`EngineRng.from_state`
# routes on the leading bytes with no ambiguity and no silent fallback. The
# trailing ``\x00`` keeps the marker outside the printable-JSON space.
_FAST_STATE_MARKER: bytes = b"RNGFAST1\x00"

# Fixed fast-codec header: getstate() version (int32), a gauss-present flag
# (bool), and the gauss double (0.0 when absent). ``random.Random`` only sets
# ``gauss_next`` via ``gauss()`` / ``normalvariate()``, which the engine never
# calls, so in practice the flag is always ``False`` — but the header carries it
# so the codec round-trips any valid ``getstate()`` faithfully.
_FAST_HEADER = struct.Struct("<i?d")


@dataclass(frozen=True)
class EngineRng:
    """Deterministic RNG wrapper with explicit serialized state threading.

    State is serialized as UTF-8 JSON of ``random.Random.getstate()``: a
    ``{"v": version, "s": [...internal...], "g": gauss_next}`` payload. The
    inner state list is re-tupled before ``setstate`` so the encoding is
    Python-version-portable rather than coupled to a pickle protocol.

    The default :meth:`snapshot` / :meth:`randint` serialization is the
    LOAD-BEARING committed encoding (:attr:`RngStateHashPolicy.FULL`); the opt-in
    training fast path (:attr:`RngStateHashPolicy.TRAINING_FAST`) is described on
    :class:`RngStateHashPolicy`.
    """

    _random: random.Random

    @classmethod
    def from_seed(cls, seed: int) -> EngineRng:
        return cls(_random=random.Random(seed))

    @classmethod
    def from_state(cls, state: bytes) -> EngineRng:
        """Restore an :class:`EngineRng` from a serialized state (self-describing).

        Detects the codec from the leading bytes so a game can advance under the
        :attr:`RngStateHashPolicy.TRAINING_FAST` fast path even though its seeded
        ``rng_state`` was written with the :attr:`RngStateHashPolicy.FULL` JSON
        codec (``orchestrator.seeder``): a fast-codec blob carries the
        :data:`_FAST_STATE_MARKER`, and every other blob is the committed JSON
        encoding. This is format DETECTION, not a silent fallback — a corrupt blob
        that is neither valid fast-codec bytes nor valid JSON still raises.
        """

        if state.startswith(_FAST_STATE_MARKER):
            return cls._from_fast_state(state)
        payload = json.loads(state.decode("utf-8"))
        # ``random.Random()`` would seed a 624-word Mersenne state that the next
        # line discards — safe to skip ONLY because ``setstate`` follows
        # immediately: a bare ``__new__`` object has no ``gauss_next`` until then.
        inner = random.Random.__new__(random.Random)
        inner.setstate((payload["v"], tuple(payload["s"]), payload["g"]))
        return cls(_random=inner)

    @classmethod
    def _from_fast_state(cls, state: bytes) -> EngineRng:
        header_start = len(_FAST_STATE_MARKER)
        header_end = header_start + _FAST_HEADER.size
        version, has_gauss, gauss_value = _FAST_HEADER.unpack(
            state[header_start:header_end]
        )
        words = array("Q")
        words.frombytes(state[header_end:])
        gauss = gauss_value if has_gauss else None
        inner = random.Random.__new__(random.Random)
        inner.setstate((version, tuple(words), gauss))
        return cls(_random=inner)

    def snapshot(
        self, *, hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL
    ) -> bytes:
        """Serialize the current Mersenne state per ``hash_policy``.

        :attr:`RngStateHashPolicy.FULL` (the default) is byte-identical to the
        pre-15.8.1 encoding — the committed, load-bearing ``state_hash`` input.
        :attr:`RngStateHashPolicy.TRAINING_FAST` skips the ~43%-of-engine-cost
        ``json.dumps`` (audit post-phase-14-ML-planning.md §3.5) in favor of the
        cheap self-describing binary codec.
        """

        version, internal, gauss = self._random.getstate()
        if hash_policy is RngStateHashPolicy.FULL:
            payload = {"v": version, "s": list(internal), "g": gauss}
            return json.dumps(payload, separators=(",", ":")).encode("utf-8")
        if hash_policy is RngStateHashPolicy.TRAINING_FAST:
            header = _FAST_HEADER.pack(
                version, gauss is not None, gauss if gauss is not None else 0.0
            )
            return _FAST_STATE_MARKER + header + array("Q", internal).tobytes()
        # No silent fallback (AGENTS.md): an unrecognised policy -- e.g. a raw
        # config string or ``None`` reaching an untyped caller -- must fail loud
        # here rather than fall through to the fast codec and silently emit
        # non-committed rng_state bytes under a caller that asked for something
        # else.
        raise ValueError(
            f"unknown RngStateHashPolicy: {hash_policy!r}; expected "
            f"{RngStateHashPolicy.FULL!r} or {RngStateHashPolicy.TRAINING_FAST!r}"
        )

    def randint(
        self,
        a: int,
        b: int,
        *,
        hash_policy: RngStateHashPolicy = RngStateHashPolicy.FULL,
    ) -> tuple[int, bytes]:
        """Draw ``randint(a, b)`` and snapshot the advanced state per ``hash_policy``.

        The DRAW is identical under either policy — only the returned snapshot's
        encoding differs — so a :attr:`RngStateHashPolicy.TRAINING_FAST` rollout
        advances the Mersenne cursor exactly as the recorded path would, and the
        two produce identical action / event streams (Task 15.8.1).
        """

        value = self._random.randint(a, b)
        return value, self.snapshot(hash_policy=hash_policy)
