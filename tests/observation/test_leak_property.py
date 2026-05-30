"""Property-based observation-purity sweep (DESIGN.md §11.2, audit I-I-2).

DESIGN.md §11.2 calls the leak test "the most important test" and mandates a
many-seeds / property-based purity sweep. The fixture-driven check in
``eval/leak_test.py`` walks exactly three hand-authored scripted games, so a
leak that only manifests under an unseen packet shape would slip through
(audit I-I-2). This module closes that gap: it drives ``ObservationService``
over every living agent on every tick across many Hypothesis-generated games
and feeds each packet through the EXISTING scanners from ``eval/leak_test.py``.

The scanners are imported, not reimplemented — the value here is breadth of
inputs, not new assertions. The action vocabulary is the role-aware strategy
from ``tests/engine/test_tick_properties.py`` (``_role_aware_actions``), reused
so the sweep exercises kills, vents, and reports — the events that populate
``visible_players`` / ``visible_bodies`` / ``audible_events`` where a leak
would surface.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from engine.actions import Action
from engine.tick import advance_tick
from engine.world import load_canonical_map
from eval.leak_test import (
    JsonValue,
    _assert_no_recursive_hidden_fields,
    _assert_no_role_bearing_values,
)
from observation.service import ObservationService
from tests.engine.test_tick_properties import (
    _initial_state,
    _role_aware_actions,
    _unique_actions_per_actor,
)


@given(
    seed=st.integers(min_value=0, max_value=2**31 - 1),
    action_batches=st.lists(st.lists(_role_aware_actions(), max_size=3), max_size=10),
)
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_observation_packets_never_leak_hidden_information(
    seed: int,
    action_batches: list[list[Action]],
    tmp_path: Path,
) -> None:
    """No packet for any living agent on any tick leaks hidden information.

    Runs ``ObservationService`` exactly as the orchestrator does — one packet
    per living agent per tick — and applies the imported leak scanners to each
    packet dump. ``advance_tick`` is only ever called on a ``PLAY`` state (it
    raises otherwise), and the loop stops once the game leaves ``PLAY``,
    mirroring ``eval/leak_test._run_scripted_game``.
    """

    game_map = load_canonical_map()
    state = _initial_state(seed)
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
        if state.phase != "PLAY":
            break

    service.close()
