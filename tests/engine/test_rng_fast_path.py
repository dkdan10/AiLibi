"""Tests for the training-only RNG hash fast path (Task 15.8.1).

``engine/rng.py`` re-serializes the full 625-int Mersenne state via ``json.dumps``
on every draw, and that serialization is hashed into every committed
``state_hash`` (``orchestrator/replay.py``), so it must NEVER change in place
(audit post-phase-14-pause.md §4). :class:`~engine.rng.RngStateHashPolicy` is the
explicit, opt-in switch that skips that ~43%-of-engine-cost snapshot (audit
post-phase-14-ML-planning.md §3.5, §11.2) for non-recorded training rollouts.

These tests pin the contract:

* :attr:`RngStateHashPolicy.FULL` is byte-identical to the legacy encoding (so
  every committed replay keeps its hash chain);
* the DRAW is policy-invariant — only the snapshot ENCODING differs — so a
  ``TRAINING_FAST`` walk advances the Mersenne cursor exactly as ``FULL`` does
  and produces an identical event stream;
* :meth:`EngineRng.from_state` is self-describing, so a game whose seeded
  ``rng_state`` is the JSON default advances under the fast codec without a
  format mismatch.
"""

from __future__ import annotations

import json
import random

import pytest

from engine.actions import Action, WaitAction
from engine.entities import PlayerId
from engine.rng import EngineRng, RngStateHashPolicy
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from orchestrator.seeder import seed_initial_state

_SEED = 7
_NUM_PLAYERS = 9
_NUM_IMPOSTORS = 2
_TASKS = 2


def _seeded_state() -> WorldState:
    return seed_initial_state(
        seed=_SEED,
        game_map=load_canonical_map(),
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS,
    )


def _wait_actions(state: WorldState) -> list[Action]:
    return [
        WaitAction(type="wait", actor=PlayerId(pid))
        for pid, player in sorted(state.players.items())
        if player.alive
    ]


def test_policy_enum_has_full_and_fast_members() -> None:
    assert {member.name for member in RngStateHashPolicy} == {"FULL", "TRAINING_FAST"}


def test_full_snapshot_is_byte_identical_to_the_legacy_encoding() -> None:
    rng = EngineRng.from_seed(123)

    # The default and the explicit FULL policy must both produce the committed
    # UTF-8 JSON encoding, byte-for-byte -- this is the load-bearing state_hash
    # input every committed replay depends on.
    default = rng.snapshot()
    explicit_full = rng.snapshot(hash_policy=RngStateHashPolicy.FULL)

    assert default == explicit_full
    payload = json.loads(default.decode("utf-8"))
    assert set(payload) == {"v", "s", "g"}


def test_fast_snapshot_is_marked_and_is_not_the_json_encoding() -> None:
    rng = EngineRng.from_seed(123)

    fast = rng.snapshot(hash_policy=RngStateHashPolicy.TRAINING_FAST)
    full = rng.snapshot(hash_policy=RngStateHashPolicy.FULL)

    assert fast != full
    # Self-describing: the fast blob carries the marker; the JSON encoding begins
    # with ``{``, so ``from_state`` can route on the leading bytes with no
    # ambiguity.
    assert fast.startswith(b"RNGFAST1\x00")
    assert not full.startswith(b"RNGFAST1\x00")
    assert full.startswith(b"{")


def test_from_state_is_self_describing_and_round_trips_both_codecs() -> None:
    rng = EngineRng.from_seed(456)
    full = rng.snapshot(hash_policy=RngStateHashPolicy.FULL)
    fast = rng.snapshot(hash_policy=RngStateHashPolicy.TRAINING_FAST)

    restored_from_full = EngineRng.from_state(full)
    restored_from_fast = EngineRng.from_state(fast)

    # Both decode to the SAME underlying Mersenne state as the original.
    assert (
        restored_from_full._random.getstate()
        == restored_from_fast._random.getstate()
        == rng._random.getstate()
    )


def test_randint_draw_is_policy_invariant() -> None:
    seed_state = EngineRng.from_seed(2024).snapshot()

    value_full, next_full = EngineRng.from_state(seed_state).randint(
        0, 2**31 - 1, hash_policy=RngStateHashPolicy.FULL
    )
    value_fast, next_fast = EngineRng.from_state(seed_state).randint(
        0, 2**31 - 1, hash_policy=RngStateHashPolicy.TRAINING_FAST
    )

    # The drawn value is identical (the draw itself is untouched); only the
    # snapshot ENCODING of the advanced state differs.
    assert value_full == value_fast
    assert next_full != next_fast
    # ...and the encodings decode to the SAME advanced Mersenne state, so the
    # cursor advanced identically under either policy.
    assert (
        EngineRng.from_state(next_full)._random.getstate()
        == EngineRng.from_state(next_fast)._random.getstate()
    )


def test_snapshot_rejects_an_unknown_policy() -> None:
    # No silent fallback: a raw config value / None reaching an untyped caller
    # must fail loud rather than default to the fast codec.
    rng = EngineRng.from_seed(1)
    with pytest.raises(ValueError, match="unknown RngStateHashPolicy"):
        rng.snapshot(hash_policy="training_fast")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unknown RngStateHashPolicy"):
        rng.snapshot(hash_policy=None)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="unknown RngStateHashPolicy"):
        rng.randint(0, 10, hash_policy="full")  # type: ignore[arg-type]


def test_fast_codec_matches_a_hand_rolled_getstate_round_trip() -> None:
    # An independent reference: the fast codec must preserve exactly what
    # ``random.Random.getstate`` / ``setstate`` round-trip, so a fast-encoded
    # state re-draws the SAME value a fresh Random with the same getstate would.
    reference = random.Random(99)
    for _ in range(50):
        reference.randint(0, 2**31 - 1)
    rng = EngineRng(_random=reference)

    fast = rng.snapshot(hash_policy=RngStateHashPolicy.TRAINING_FAST)
    decoded = EngineRng.from_state(fast)

    assert decoded._random.getstate() == reference.getstate()
    assert decoded._random.randint(0, 2**31 - 1) == reference.randint(0, 2**31 - 1)


def test_advance_tick_default_is_byte_identical_to_full_policy() -> None:
    state = _seeded_state()
    actions = _wait_actions(state)

    default_state, default_events = advance_tick(
        state, actions, game_map=load_canonical_map()
    )
    full_state, full_events = advance_tick(
        state,
        actions,
        game_map=load_canonical_map(),
        rng_hash_policy=RngStateHashPolicy.FULL,
    )

    # The default advance_tick and the explicit FULL policy are the same code
    # path; the rng_state bytes are byte-identical, so state_hash chains are too.
    assert default_state == full_state
    assert default_state.rng_state == full_state.rng_state
    assert default_events == full_events


def test_advance_tick_fast_preserves_the_draw_sequence_and_events() -> None:
    game_map = load_canonical_map()

    full_state = _seeded_state()
    fast_state = _seeded_state()
    assert full_state.rng_state == fast_state.rng_state

    for _ in range(25):
        full_actions = _wait_actions(full_state)
        fast_actions = _wait_actions(fast_state)
        assert full_actions == fast_actions

        full_state, full_events = advance_tick(
            full_state,
            full_actions,
            game_map=game_map,
            rng_hash_policy=RngStateHashPolicy.FULL,
        )
        fast_state, fast_events = advance_tick(
            fast_state,
            fast_actions,
            game_map=game_map,
            rng_hash_policy=RngStateHashPolicy.TRAINING_FAST,
        )

        # Events are identical every tick (the trajectory is untouched)...
        assert full_events == fast_events
        # ...the rng_state bytes DIFFER (fast codec vs committed JSON)...
        assert full_state.rng_state != fast_state.rng_state
        # ...yet the two encodings decode to the SAME advanced Mersenne state, so
        # the draw sequence is preserved -- the fast path stays a drop-in even if
        # a future engine change makes the drawn value load-bearing.
        assert (
            EngineRng.from_state(full_state.rng_state)._random.getstate()
            == EngineRng.from_state(fast_state.rng_state)._random.getstate()
        )
        # And every non-rng field of the world state is identical.
        assert full_state.tick == fast_state.tick
        assert full_state.players == fast_state.players
        assert full_state.tasks == fast_state.tasks
