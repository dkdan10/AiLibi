"""Shared world-state builders for the canonical scripted-game fixtures.

Both `eval/leak_test.py` and `eval/determinism_test.py` need an identical
initial `WorldState` to reproduce the scripted-game fixtures byte-for-byte.
Centralizing the helper here keeps them in lockstep — drift between the two
copies would silently break determinism guarantees.
"""

from __future__ import annotations

from engine.entities import PlayerState, TaskState
from engine.rng import EngineRng
from engine.world import WorldState, load_canonical_map


def scripted_initial_world_state(*, seed: int) -> WorldState:
    """Build the initial WorldState used by the scripted-game fixtures."""

    game_map = load_canonical_map()
    return WorldState(
        tick=0,
        phase="PLAY",
        map=game_map.id,
        players={
            "player-1": PlayerState(
                id="player-1",
                role="CREWMATE",
                alive=True,
                room=game_map.spawn.room,
                position=(0.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
            "player-2": PlayerState(
                id="player-2",
                role="CREWMATE",
                alive=True,
                room=game_map.spawn.room,
                position=(1.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
            "impostor-1": PlayerState(
                id="impostor-1",
                role="IMPOSTOR",
                alive=True,
                room=game_map.spawn.room,
                position=(2.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
            "player-3": PlayerState(
                id="player-3",
                role="CREWMATE",
                alive=True,
                room=game_map.spawn.room,
                position=(3.0, 0.0),
                last_action=None,
                in_vent=False,
            ),
        },
        bodies={},
        tasks={
            "swipe_card": TaskState(
                id="swipe_card",
                owner="player-1",
                room="ADMIN",
                progress=0,
                required_ticks=1,
                completed=False,
            ),
            "submit_scan": TaskState(
                id="submit_scan",
                owner="player-2",
                room="MEDBAY",
                progress=0,
                required_ticks=1,
                completed=False,
            ),
            "empty_trash": TaskState(
                id="empty_trash",
                owner="player-3",
                room="CAFETERIA",
                progress=0,
                required_ticks=1,
                completed=False,
            ),
        },
        sabotage=None,
        cooldowns={"impostor-1": 0},
        emergency_uses={},
        rng_state=EngineRng.from_seed(seed).snapshot(),
        seed=seed,
    )
