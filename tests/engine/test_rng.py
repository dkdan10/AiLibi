"""Snapshot/restore tests for ``engine.rng.EngineRng``.

Replay determinism depends on ``snapshot()`` + ``from_state()`` round-tripping
exactly. These tests lock today's behavior so any future change to the RNG
encoding (e.g., switching off ``repr`` + ``ast.literal_eval``) gets a hard
signal if anything diverges.
"""

from __future__ import annotations

from engine.rng import EngineRng


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


def test_snapshot_returns_bytes() -> None:
    snapshot = EngineRng.from_seed(0).snapshot()

    assert isinstance(snapshot, bytes)
    assert snapshot  # non-empty
