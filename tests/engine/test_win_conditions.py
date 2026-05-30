"""Characterization tests for ``engine.win_conditions.evaluate_win_conditions``.

These pin the CURRENT win-check ordering (DESIGN.md §3.5) so a future refactor
of the parity / sabotage / task comparisons cannot silently change an outcome
(audit I-I-3). The centrepiece is
``test_zero_alive_impostors_with_incomplete_tasks_returns_none``: it pins the
known-deferred impostor-elimination gap and is intended to go RED — and be
flipped — when Task 6.3 closes that gap.
"""

from __future__ import annotations

from engine.entities import PlayerState, SabotageState, TaskState
from engine.rng import EngineRng
from engine.win_conditions import WinResult, evaluate_win_conditions
from engine.world import WorldState, load_canonical_map


def _player(player_id: str, role: str, *, alive: bool = True) -> PlayerState:
    return PlayerState(
        id=player_id,
        role="IMPOSTOR" if role == "IMPOSTOR" else "CREWMATE",
        alive=alive,
        room="CAFETERIA",
        position=(0.0, 0.0),
        last_action=None,
        in_vent=False,
    )


def _task(task_id: str, owner: str, *, completed: bool) -> TaskState:
    return TaskState(
        id=task_id,
        owner=owner,
        room="ADMIN",
        progress=1 if completed else 0,
        required_ticks=1,
        completed=completed,
    )


def _world_state(
    *,
    players: dict[str, PlayerState],
    tasks: dict[str, TaskState] | None = None,
    sabotage: SabotageState | None = None,
) -> WorldState:
    game_map = load_canonical_map()
    return WorldState(
        tick=10,
        phase="PLAY",
        map=game_map.id,
        players=players,
        bodies={},
        tasks=tasks or {},
        sabotage=sabotage,
        cooldowns={},
        emergency_uses={},
        rng_state=EngineRng.from_seed(7).snapshot(),
        seed=7,
    )


def test_zero_alive_impostors_with_incomplete_tasks_returns_none() -> None:
    # DEFERRED IMPOSTOR-ELIMINATION GAP (memory
    # `project_win_condition_impostor_elimination_gap`, audit I-I-3, repro
    # seed 49): with every impostor dead but tasks still incomplete,
    # `evaluate_win_conditions` currently returns None — the game keeps running
    # even though the crew has effectively won. This test pins that CURRENT
    # behavior. Task 6.3 closes the gap and FLIPS this assertion from `is None`
    # to asserting the crew elimination win; do not "fix" it here (Task 6.2 is
    # tests-only, no production change).
    state = _world_state(
        players={
            "p-1": _player("p-1", "CREWMATE", alive=True),
            "p-2": _player("p-2", "CREWMATE", alive=True),
            "p-3": _player("p-3", "IMPOSTOR", alive=False),
        },
        tasks={"swipe_card": _task("swipe_card", "p-1", completed=False)},
    )

    assert evaluate_win_conditions(state) is None


def test_impostor_parity_returns_impostor_win() -> None:
    # Parity is checked first (DESIGN.md §3.5): one impostor + one crewmate
    # alive resolves as an impostor win.
    state = _world_state(
        players={
            "p-1": _player("p-1", "CREWMATE", alive=True),
            "p-2": _player("p-2", "IMPOSTOR", alive=True),
        },
        tasks={"swipe_card": _task("swipe_card", "p-1", completed=False)},
    )

    assert evaluate_win_conditions(state) == WinResult(
        winner="IMPOSTORS", reason="IMPOSTOR_PARITY"
    )


def test_active_sabotage_timeout_returns_impostor_win() -> None:
    # Sabotage timeout is checked after parity and before tasks: with crew
    # outnumbering impostors but a sabotage at zero remaining ticks, impostors
    # win.
    state = _world_state(
        players={
            "p-1": _player("p-1", "CREWMATE", alive=True),
            "p-2": _player("p-2", "CREWMATE", alive=True),
            "p-3": _player("p-3", "IMPOSTOR", alive=True),
        },
        tasks={"swipe_card": _task("swipe_card", "p-1", completed=False)},
        sabotage=SabotageState(
            kind="lights",
            remaining_ticks=0,
            affected_rooms=("ADMIN",),
            active=True,
        ),
    )

    assert evaluate_win_conditions(state) == WinResult(
        winner="IMPOSTORS", reason="IMPOSTOR_SABOTAGE"
    )


def test_all_alive_owned_tasks_complete_returns_crew_win() -> None:
    # With crew outnumbering a living impostor, no sabotage timeout, and every
    # remaining task complete, the crew wins on tasks.
    state = _world_state(
        players={
            "p-1": _player("p-1", "CREWMATE", alive=True),
            "p-2": _player("p-2", "CREWMATE", alive=True),
            "p-3": _player("p-3", "IMPOSTOR", alive=True),
        },
        tasks={"swipe_card": _task("swipe_card", "p-1", completed=True)},
    )

    assert evaluate_win_conditions(state) == WinResult(
        winner="CREWMATES", reason="CREWMATE_TASKS"
    )
