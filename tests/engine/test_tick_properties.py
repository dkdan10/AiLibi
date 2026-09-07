"""Engine totality, life/role consistency and terminal-state properties."""

from __future__ import annotations

from dataclasses import replace

import pytest
from hypothesis import given, settings, strategies as st
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import PlayerState
from engine.events import EngineEvent, GameOverEvent
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.win_conditions import evaluate_win_conditions
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


def _assert_state_invariants(
    before: WorldState, after: WorldState, events: list[EngineEvent]
) -> None:
    assert set(after.players) == set(before.players)
    for pid, player in after.players.items():
        assert player.role == before.players[pid].role, "role changed during a tick"
        assert before.players[pid].alive or not player.alive, "dead player revived"
    assert all(
        not after.players[body.player_id].alive for body in after.bodies.values()
    ), "body belongs to a living player"
    terminal = [event for event in events if isinstance(event, GameOverEvent)]
    outcome = evaluate_win_conditions(after)
    if after.phase == "GAME_OVER":
        assert len(terminal) == 1 and outcome is not None, (
            "terminal state lacks a winner"
        )
        assert (terminal[0].winner, terminal[0].reason) == (
            outcome.winner,
            outcome.reason,
        )
    else:
        assert not terminal, "nonterminal state carries a terminal event"
        assert outcome is None, "a decided game continued into play or a meeting"


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
        _assert_state_invariants(state, next_state, events)

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


# R-12: role-aware action vocabulary. Constants below pin the actor / target
# / vent pools to the canonical ``_initial_state`` shape: ``p-3`` is the
# only impostor, ``p-1`` and ``p-2`` are crewmates, and the six vent ids
# come from ``engine/maps/canonical_1.yaml``. Body ids are deliberately a
# mix of plausible and missing strings so the engine's rejection path gets
# exercised alongside the rare "real body" hit.
_IMPOSTOR_ID = "p-3"
_CREWMATE_IDS = ("p-1", "p-2")
_VENT_IDS = (
    "REACTOR_VENT",
    "STORAGE_VENT",
    "ENGINEERING_VENT",
    "ADMIN_VENT",
    "MEDBAY_VENT",
    "LABS_VENT",
)
_BODY_ID_DRAWS = ("body-p-1-0", "body-p-2-0", "missing-body")


@st.composite
def _role_aware_actions(draw: st.DrawFn) -> Action:
    """Draw a role-valid action from the broader kill / vent / report / wait
    vocabulary. ``kill`` and ``vent`` are gated on the impostor role;
    ``report`` and ``wait`` accept any actor in ``_ACTORS``. Aliveness is
    *not* checked here on purpose — the engine catches dead-actor and
    dead-target attempts via ``ActionRejectedError`` and converts them to
    ``ActionRejectedEvent``s, which is exactly the rejection path this
    property is meant to exercise.
    """

    kind = draw(st.sampled_from(("kill", "vent", "report", "wait")))
    if kind == "kill":
        target = draw(st.sampled_from(_CREWMATE_IDS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "kill", "actor": _IMPOSTOR_ID, "payload": {"target": target}}
        )
    if kind == "vent":
        vent_id = draw(st.sampled_from(_VENT_IDS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "vent", "actor": _IMPOSTOR_ID, "payload": {"vent_id": vent_id}}
        )
    if kind == "report":
        actor = draw(st.sampled_from(_ACTORS))
        body_id = draw(st.sampled_from(_BODY_ID_DRAWS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "report", "actor": actor, "payload": {"body_id": body_id}}
        )
    actor = draw(st.sampled_from(_ACTORS))
    return _ACTION_ADAPTER.validate_python(
        {"type": "wait", "actor": actor, "payload": {}}
    )


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    action_batches=st.lists(st.lists(_role_aware_actions(), max_size=3), max_size=10),
)
@settings(max_examples=50, deadline=None)
def test_advance_tick_does_not_raise_under_role_aware_actions(
    seed: int,
    action_batches: list[list[Action]],
) -> None:
    """R-12: ``advance_tick`` must not raise on any role-aware batch.

    Pairs with ``test_advance_tick_is_total_under_arbitrary_safe_actions``
    above: that property covers ``move`` / ``wait`` sequences; this one
    covers the previously unexplored ``kill`` / ``vent`` / ``report`` /
    ``wait`` interleavings. Engine rejections must surface as
    ``ActionRejectedEvent``s (see ``engine/tick.py``), not exceptions.
    """

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
        _assert_state_invariants(state, next_state, events)
        state = next_state


def test_properties_reject_a_meeting_that_suppresses_parity() -> None:
    before = _initial_state(seed=0)
    poisoned = replace(
        before,
        phase="MEETING",
        players={
            **before.players,
            "p-1": replace(before.players["p-1"], alive=False),
        },
    )
    with pytest.raises(AssertionError, match="a decided game continued"):
        _assert_state_invariants(before, poisoned, [])


def test_properties_reject_reviving_a_dead_player() -> None:
    alive = _initial_state(seed=0)
    before = replace(
        alive,
        players={
            **alive.players,
            "p-1": replace(alive.players["p-1"], alive=False),
        },
    )
    with pytest.raises(AssertionError, match="dead player revived"):
        _assert_state_invariants(before, alive, [])
