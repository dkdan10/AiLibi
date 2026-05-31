"""Property-based observation-purity sweep (DESIGN.md §11.2, audit I-I-2).

DESIGN.md §11.2 calls the leak test "the most important test" and mandates a
many-seeds / property-based purity sweep. The fixture-driven check in
``eval/leak_test.py`` walks exactly three hand-authored scripted games, so a
leak that only manifests under an unseen packet shape would slip through
(audit I-I-2). This module closes that gap: it drives ``ObservationService``
over every living agent on every tick across many Hypothesis-generated games
and feeds each packet through the EXISTING scanners from ``eval/leak_test.py``.

The scanners are imported, not reimplemented -- the value here is breadth of
inputs. Task 7.2 additionally parametrizes the sweep over ``num_impostors``
(1, 2, and 3 on a crew-majority 7-player roster) and asserts the new crew-empty
firewall invariant -- ``self_state.fellow_impostor_ids == ()`` for every
crewmate-recipient packet -- inside the per-packet loop. This is the project's
strongest leak test guarding the FIRST self-channel field beyond ``role``: the
generic scanners cannot catch a crewmate erroneously receiving a teammate id
(role-neutral ids like ``p-2`` do not trip the value scanner, and the field
name is not in the recursive scanner's set), and the single-impostor scripted
fixtures cannot surface a crew-tuple misroute (every impostor's tuple is also
empty there), so a multi-impostor roster is required to exercise it.

The action vocabulary mirrors the role-aware strategy from
``tests/engine/test_tick_properties.py`` but is generalized off that module's
single-impostor roster so the sweep exercises kills, vents, and reports across
the whole multi-impostor roster -- the events that populate ``visible_players``
/ ``visible_bodies`` / ``audible_events`` where a leak would surface.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pydantic import TypeAdapter

from engine.actions import Action
from engine.entities import PlayerState
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from eval.leak_test import (
    JsonValue,
    _assert_no_recursive_hidden_fields,
    _assert_no_role_bearing_values,
)
from observation.service import ObservationService
from tests.engine.test_tick_properties import _unique_actions_per_actor

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# Seven-player roster (p-1 .. p-7). The valid impostor counts keep crewmates in
# the majority -- impostor parity is an immediate win (engine/win_conditions.py)
# -- so 1/2/3 impostors all start in a non-terminal PLAY state. The first
# ``num_impostors`` ids are the impostors.
_ROSTER_PLAYER_IDS = tuple(f"p-{index}" for index in range(1, 8))
_VALID_IMPOSTOR_COUNTS = (1, 2, 3)

# Canonical_1 vent ids and a mix of plausible / missing body ids, mirroring
# ``tests/engine/test_tick_properties.py``. The engine rejects role-invalid,
# dead-actor, unknown-vent, and missing-body attempts via ``ActionRejectedEvent``
# (never an exception), so any drawn action is safe to feed to ``advance_tick``.
_ROSTER_VENT_IDS = (
    "REACTOR_VENT",
    "STORAGE_VENT",
    "ENGINEERING_VENT",
    "ADMIN_VENT",
    "MEDBAY_VENT",
    "LABS_VENT",
)
_ROSTER_BODY_ID_DRAWS = ("body-p-1-0", "body-p-2-0", "missing-body")


def _roster_initial_state(*, seed: int, num_impostors: int) -> WorldState:
    """Build a 7-player ``PLAY`` state with ``num_impostors`` impostors.

    The first ``num_impostors`` ids are impostors; the rest are crewmates.
    Everyone spawns in CAFETERIA with empty tasks -- the win check only ends on
    impostor parity (guarded by the crew majority) or completed tasks (none
    here), so the game runs until the drawn action batches drive it out of
    ``PLAY``. Generalizes ``test_tick_properties._initial_state`` off its
    single-impostor roster so the sweep can exercise multi-impostor games.
    """

    impostor_ids = set(_ROSTER_PLAYER_IDS[:num_impostors])
    players = {
        player_id: PlayerState(
            id=player_id,
            role="IMPOSTOR" if player_id in impostor_ids else "CREWMATE",
            alive=True,
            room="CAFETERIA",
            position=(0.0, 0.0),
            last_action=None,
            in_vent=False,
        )
        for player_id in _ROSTER_PLAYER_IDS
    }
    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players=players,
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns={impostor_id: 0 for impostor_id in impostor_ids},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )


@st.composite
def _roster_action(draw: st.DrawFn) -> Action:
    """Draw a role-aware kill / vent / report / wait action over the full
    7-player roster. Actor and kill target are drawn from the whole roster; the
    engine rejects role-invalid or dead attempts, so kills land only when the
    drawn actor is a living impostor -- exactly the multi-impostor coverage this
    sweep adds over the single-impostor engine strategy.
    """

    kind = draw(st.sampled_from(("kill", "vent", "report", "wait")))
    actor = draw(st.sampled_from(_ROSTER_PLAYER_IDS))
    if kind == "kill":
        # ``KillAction`` rejects a self-target at construction, so draw the
        # target from the roster minus the actor (6 ids, always non-empty).
        target = draw(
            st.sampled_from(tuple(pid for pid in _ROSTER_PLAYER_IDS if pid != actor))
        )
        return _ACTION_ADAPTER.validate_python(
            {"type": "kill", "actor": actor, "payload": {"target": target}}
        )
    if kind == "vent":
        vent_id = draw(st.sampled_from(_ROSTER_VENT_IDS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "vent", "actor": actor, "payload": {"vent_id": vent_id}}
        )
    if kind == "report":
        body_id = draw(st.sampled_from(_ROSTER_BODY_ID_DRAWS))
        return _ACTION_ADAPTER.validate_python(
            {"type": "report", "actor": actor, "payload": {"body_id": body_id}}
        )
    return _ACTION_ADAPTER.validate_python(
        {"type": "wait", "actor": actor, "payload": {}}
    )


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    num_impostors=st.sampled_from(_VALID_IMPOSTOR_COUNTS),
    action_batches=st.lists(st.lists(_roster_action(), max_size=3), max_size=10),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_observation_packets_never_leak_hidden_information(
    seed: int,
    num_impostors: int,
    action_batches: list[list[Action]],
    tmp_path: Path,
) -> None:
    """No packet for any living agent on any tick leaks hidden information, and
    no crewmate-recipient packet ever carries a non-empty ``fellow_impostor_ids``
    -- across many seeds and 1/2/3-impostor rosters.

    Runs ``ObservationService`` exactly as the orchestrator does -- one packet
    per living agent per tick -- and applies the imported leak scanners plus the
    Task 7.2 crew-empty invariant to each packet. ``advance_tick`` is only ever
    called on a ``PLAY`` state (it raises otherwise), and the loop stops once the
    game leaves ``PLAY``, mirroring ``eval/leak_test._run_scripted_game``.
    """

    game_map = load_canonical_map()
    state = _roster_initial_state(seed=seed, num_impostors=num_impostors)
    service = ObservationService(
        game_map=game_map, audit_log_path=tmp_path / "audit.jsonl"
    )

    for batch in action_batches:
        if state.phase != "PLAY":
            break
        state, events = advance_tick(
            state, _unique_actions_per_actor(batch), game_map=game_map
        )
        for player_id, player in state.players.items():
            if not player.alive:
                continue
            packet = service.build_packet(
                world_state=state,
                agent_id=player_id,
                engine_events=events,
            )
            packet_dump = cast(JsonValue, packet.model_dump(mode="json"))
            _assert_no_recursive_hidden_fields(packet_dump)
            _assert_no_role_bearing_values(packet_dump)
            if packet.self_state.role == "CREWMATE":
                assert packet.self_state.fellow_impostor_ids == ()
        if state.phase != "PLAY":
            break

    service.close()
