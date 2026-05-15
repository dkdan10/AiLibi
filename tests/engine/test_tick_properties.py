"""Property-based totality tests for ``engine.tick.advance_tick``.

DESIGN.md §11.1 mandates that for any sequence of valid actions,
``advance_tick`` is total and never produces invalid state.

This test deliberately scopes the action vocabulary to ``move`` and ``wait`` —
the action types most likely to be generated en masse by Phase 2 tactical
agents. The point is to prove the engine never crashes on weird sequences,
not to model every kill scenario; richer action coverage belongs in dedicated
unit tests.
"""

from __future__ import annotations

from dataclasses import replace

from hypothesis import given, settings, strategies as st
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import PlayerState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)
_ACTORS = ("p-1", "p-2", "p-3")
_ROOM_NEIGHBORS_FROM_CAFETERIA = ("CAFETERIA", "EAST_HALL", "UPPER_HALL", "WEST_HALL")


def _player(player_id: str, role: str) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="IMPOSTOR" if role == "IMPOSTOR" else "CREWMATE",
        alive=True,
        room="CAFETERIA",
        position=(0.0, 0.0),
        last_action=None,
        in_vent=False,
    )


def _initial_state(seed: int) -> WorldState:
    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players={
            "p-1": _player("p-1", "CREWMATE"),
            "p-2": _player("p-2", "CREWMATE"),
            "p-3": _player("p-3", "IMPOSTOR"),
        },
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={"p-3": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


_VALID_PHASES = frozenset({"PLAY", "MEETING", "GAME_OVER"})

_safe_actions = st.one_of(
    st.builds(
        lambda actor, room: _ACTION_ADAPTER.validate_python(
            {"type": "move", "actor": actor, "payload": {"to_room": room}}
        ),
        actor=st.sampled_from(_ACTORS),
        room=st.sampled_from(_ROOM_NEIGHBORS_FROM_CAFETERIA),
    ),
    st.builds(
        lambda actor: _ACTION_ADAPTER.validate_python(
            {"type": "wait", "actor": actor, "payload": {}}
        ),
        actor=st.sampled_from(_ACTORS),
    ),
)


def _unique_actions_per_actor(actions: list[Action]) -> list[Action]:
    """Phase-1 advance_tick assumes one action per actor per tick."""

    seen: set[str] = set()
    deduped: list[Action] = []
    for action in actions:
        if action.actor in seen:
            continue
        seen.add(action.actor)
        deduped.append(action)
    return deduped


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    action_batches=st.lists(st.lists(_safe_actions, max_size=3), max_size=10),
)
@settings(max_examples=50, deadline=None)
def test_advance_tick_is_total_under_arbitrary_safe_actions(
    seed: int,
    action_batches: list[list[Action]],
) -> None:
    game_map = load_canonical_map()
    state = _initial_state(seed)

    for batch in action_batches:
        if state.phase != "PLAY":
            break

        next_state, events = advance_tick(
            state,
            _unique_actions_per_actor(batch),
            game_map=game_map,
        )

        assert next_state.phase in _VALID_PHASES
        assert next_state.tick >= state.tick
        assert isinstance(events, list)

        # Engine state remains structurally well-formed.
        assert set(next_state.players) == set(state.players)
        for player in next_state.players.values():
            assert player.room in game_map.rooms

        state = next_state


@given(seed=st.integers(min_value=0, max_value=2**31 - 1))
@settings(max_examples=20, deadline=None)
def test_empty_action_batch_advances_tick_without_crashing(seed: int) -> None:
    game_map = load_canonical_map()
    state = _initial_state(seed)

    next_state, events = advance_tick(state, [], game_map=game_map)

    assert next_state.phase == "PLAY"
    assert next_state.tick == state.tick + 1
    assert isinstance(events, list)


def test_property_test_setup_uses_canonical_map() -> None:
    """Sanity: the property tests reference rooms that actually exist."""

    game_map = load_canonical_map()
    for room in _ROOM_NEIGHBORS_FROM_CAFETERIA:
        assert room in game_map.rooms

    initial = _initial_state(seed=0)
    assert all(player.room in game_map.rooms for player in initial.players.values())
    assert replace(initial, tick=initial.tick) == initial
