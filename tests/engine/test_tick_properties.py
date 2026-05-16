"""Property-based totality tests for ``engine.tick.advance_tick``.

DESIGN.md §11.1 mandates that for any sequence of valid actions,
``advance_tick`` is total and never produces invalid state.

The original ``_safe_actions`` strategy below intentionally scopes its
vocabulary to ``move`` and ``wait`` — the verbs Phase 2 tactical agents
emit en masse. The point of that property is to prove the engine never
crashes on weird movement sequences, not to model every kill scenario.

R-12 (audits/audit-2026-05-15-0225-reconciled.md §R-12) adds a second,
role-aware strategy alongside it that draws batches mixing ``kill``,
``vent``, ``report``, and ``wait`` actions. Engine-level rejections
(`ActionRejectedError`) are caught in ``advance_tick`` and turned into
``ActionRejectedEvent``s, so the new property remains narrow:
``advance_tick`` must never raise on a drawn batch. Deeper invariants
(role-correct event emission, witness sets, etc.) stay in dedicated unit
tests.
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
        state, _ = advance_tick(
            state,
            _unique_actions_per_actor(batch),
            game_map=game_map,
        )
