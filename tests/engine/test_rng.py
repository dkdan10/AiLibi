"""Snapshot/restore tests for ``engine.rng.EngineRng``.

Replay determinism depends on ``snapshot()`` + ``from_state()`` round-tripping
exactly. These tests lock today's behavior so any future change to the RNG
encoding gets a hard signal if anything diverges.

Snapshot bytes are UTF-8 JSON of ``random.Random.getstate()`` shaped as
``{"v": version, "s": [...internal...], "g": gauss_next}``. ``from_state``
re-tuples the inner state list before ``setstate``.
"""

from __future__ import annotations

import json
import random

import pytest

from engine.rng import EngineRng, RngStateHashPolicy


def test_snapshot_then_restore_produces_same_sequence() -> None:
    snapshot = EngineRng.from_seed(123).snapshot()

    sequence_a: list[int] = []
    state_a = snapshot
    for _ in range(8):
        rng = EngineRng.from_state(state_a)
        value, state_a = rng.randint(0, 2**31 - 1)
        sequence_a.append(value)

    sequence_b: list[int] = []
    state_b = snapshot
    for _ in range(8):
        rng = EngineRng.from_state(state_b)
        value, state_b = rng.randint(0, 2**31 - 1)
        sequence_b.append(value)

    assert sequence_a == sequence_b
    assert state_a == state_b


def test_snapshot_round_trip_preserves_next_value() -> None:
    rng_a = EngineRng.from_seed(42)
    snapshot_a = rng_a.snapshot()

    expected_value, expected_next_state = EngineRng.from_state(snapshot_a).randint(
        0, 1_000_000
    )
    actual_value, actual_next_state = EngineRng.from_state(snapshot_a).randint(
        0, 1_000_000
    )

    assert actual_value == expected_value
    assert actual_next_state == expected_next_state


def test_same_seed_produces_same_first_value() -> None:
    a, _ = EngineRng.from_seed(7).randint(0, 2**31 - 1)
    b, _ = EngineRng.from_seed(7).randint(0, 2**31 - 1)

    assert a == b


def test_independent_seeds_diverge() -> None:
    a, _ = EngineRng.from_seed(1).randint(0, 2**31 - 1)
    b, _ = EngineRng.from_seed(2).randint(0, 2**31 - 1)

    assert a != b


def test_snapshot_returns_utf8_json_bytes() -> None:
    snapshot = EngineRng.from_seed(0).snapshot()

    assert isinstance(snapshot, bytes)
    assert snapshot  # non-empty

    payload = json.loads(snapshot.decode("utf-8"))
    assert set(payload.keys()) == {"v", "s", "g"}
    assert isinstance(payload["v"], int)
    assert isinstance(payload["s"], list)
    assert all(isinstance(value, int) for value in payload["s"])
    assert payload["g"] is None or isinstance(payload["g"], float)


# --------------------------------------------------------------------------- #
# The restore path skips the seeding it would discard                          #
# --------------------------------------------------------------------------- #
#
# ``from_state`` builds its generator with ``random.Random.__new__`` instead of
# ``random.Random()``: the constructor seeds a 624-word Mersenne state that the
# very next ``setstate`` overwrites. These three pin why the substitution is
# behaviour-identical AND why it is safe only where ``setstate`` follows
# immediately.


def _restored_state() -> tuple[int, tuple[int, ...], float | None]:
    version, internal, gauss = random.Random(20260827).getstate()
    return version, internal, gauss


def test_new_restored_generator_draws_identically_to_a_seeded_one() -> None:
    """1000 identical draws from a FULL-restored and a ``__new__``-restored gen."""

    state = _restored_state()
    seeded = random.Random()
    seeded.setstate(state)
    bare = random.Random.__new__(random.Random)
    bare.setstate(state)

    assert [seeded.random() for _ in range(1000)] == [
        bare.random() for _ in range(1000)
    ]


def test_new_restored_generator_holds_the_same_state_after_those_draws() -> None:
    """...and the two generators' ``getstate()`` agree afterwards, not just their
    outputs: the Mersenne cursor advanced identically, so a chain of snapshots
    restored either way stays byte-identical."""

    state = _restored_state()
    seeded = random.Random()
    seeded.setstate(state)
    bare = random.Random.__new__(random.Random)
    bare.setstate(state)
    for _ in range(1000):
        seeded.random()
        bare.random()

    assert seeded.getstate() == bare.getstate()


def test_getstate_on_a_bare_new_object_raises_before_setstate() -> None:
    """The gotcha the substitution rests on: ``__new__`` leaves ``gauss_next``
    unset, so ``getstate()`` raises until ``setstate`` supplies it. That is why
    :meth:`EngineRng.from_state` may skip the constructor ONLY where the
    ``setstate`` is on the next line — and why nothing else in the engine may
    copy the pattern."""

    bare = random.Random.__new__(random.Random)
    with pytest.raises(AttributeError):
        bare.getstate()
    # ...and it is fully usable the moment setstate lands.
    bare.setstate(_restored_state())
    assert isinstance(bare.getstate(), tuple)


def test_engine_rng_restore_round_trips_through_both_codecs() -> None:
    """Both ``from_state`` branches — committed JSON and the fast codec — restore
    to the same draws, which is what the substitution had to preserve."""

    seeded = EngineRng.from_seed(99)
    json_state = seeded.snapshot()
    fast_state = seeded.snapshot(hash_policy=RngStateHashPolicy.TRAINING_FAST)

    from_json = EngineRng.from_state(json_state)
    from_fast = EngineRng.from_state(fast_state)
    assert [from_json.randint(0, 10**9)[0] for _ in range(64)] == [
        from_fast.randint(0, 10**9)[0] for _ in range(64)
    ]
