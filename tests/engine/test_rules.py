"""Engine kill-rule tests (DESIGN.md §3.4).

Focused coverage for the Phase 7 Task 7.9 friendly-fire guard in
``engine.rules.resolve_kill`` plus the end-to-end invariant that no resolved
kill in a seeded multi-impostor game ever lands on a fellow impostor. The guard
is defense-in-depth: the impostor tactical policy already filters teammates from
target selection, but the engine must independently reject an IMPOSTOR-target
kill so a buggy or future LLM-driven policy can never self-sabotage the team.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engine.actions import KillAction
from engine.entities import PlayerState
from engine.rng import EngineRng
from engine.rules import ActionRejectedError, resolve_kill
from engine.world import WorldState, load_canonical_map
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import read_replay_entries
from orchestrator.scheduler import TickScheduler


def _player(player_id: str, role: str, room: str = "CAFETERIA") -> PlayerState:
    return PlayerState(
        id=player_id,
        role="IMPOSTOR" if role == "IMPOSTOR" else "CREWMATE",
        alive=True,
        room=room,
        position=(0.0, 0.0),
        last_action=None,
        in_vent=False,
    )


def _kill_state(
    *,
    players: dict[str, PlayerState],
    cooldowns: dict[str, int] | None = None,
) -> WorldState:
    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players=players,
        bodies={},
        tasks={},
        sabotage=None,
        cooldowns=cooldowns or {pid: 0 for pid in players},
        emergency_uses={},
        rng_state=EngineRng.from_seed(1).snapshot(),
        seed=1,
    )


def _kill(actor: str, target: str) -> KillAction:
    return KillAction.model_validate(
        {"type": "kill", "actor": actor, "payload": {"target": target}}
    )


def test_resolve_kill_rejects_impostor_target() -> None:
    # The friendly-fire guard: two impostors in the same room, off cooldown —
    # every other precondition for a legal kill is satisfied, yet the kill is
    # rejected purely because the target is a fellow impostor.
    state = _kill_state(
        players={
            "p-1": _player("p-1", "IMPOSTOR"),
            "p-2": _player("p-2", "IMPOSTOR"),
            "p-3": _player("p-3", "CREWMATE"),
        }
    )
    with pytest.raises(ActionRejectedError, match="crewmate"):
        resolve_kill(state, _kill("p-1", "p-2"))


def test_resolve_kill_resolves_crewmate_target() -> None:
    # The legitimate impostor-kills-crewmate path is unchanged: it spawns a body
    # attributed to the actor and emits a Killed event.
    state = _kill_state(
        players={
            "p-1": _player("p-1", "IMPOSTOR"),
            "p-2": _player("p-2", "IMPOSTOR"),
            "p-3": _player("p-3", "CREWMATE"),
        }
    )
    body, event = resolve_kill(state, _kill("p-1", "p-3"))

    assert body.player_id == "p-3"
    assert body.killed_by == "p-1"
    assert event.type == "Killed"
    assert event.target == "p-3"


def test_resolve_kill_actor_must_be_impostor_unchanged() -> None:
    # The actor-is-impostor check still fires (and precedes the target check):
    # a crewmate actor is rejected even when its target is an impostor.
    state = _kill_state(
        players={
            "p-1": _player("p-1", "IMPOSTOR"),
            "p-3": _player("p-3", "CREWMATE"),
        }
    )
    with pytest.raises(ActionRejectedError, match="only impostors can kill"):
        resolve_kill(state, _kill("p-3", "p-1"))


def test_resolve_kill_cooldown_check_unchanged() -> None:
    # The cooldown check still fires on the legitimate crewmate-target path.
    state = _kill_state(
        players={
            "p-1": _player("p-1", "IMPOSTOR"),
            "p-3": _player("p-3", "CREWMATE"),
        },
        cooldowns={"p-1": 2, "p-3": 0},
    )
    with pytest.raises(ActionRejectedError, match="cooldown"):
        resolve_kill(state, _kill("p-1", "p-3"))


def test_resolve_kill_same_room_check_unchanged() -> None:
    # The same-room check still fires on the legitimate crewmate-target path.
    state = _kill_state(
        players={
            "p-1": _player("p-1", "IMPOSTOR", room="CAFETERIA"),
            "p-3": _player("p-3", "CREWMATE", room="ADMIN"),
        }
    )
    with pytest.raises(ActionRejectedError, match="same room"):
        resolve_kill(state, _kill("p-1", "p-3"))


# -- end-to-end invariant: no resolved kill ever lands on an impostor ----------
#
# Repro anchors from audits/audit-2026-06-01-1425-gameplay-data.md (the seeds /
# ticks where the pre-7.9 set self-destructed): seed 4 tick 1 (mutual spawn-room
# kill, CAFETERIA), seed 0 tick 7 (mid-game, MEDBAY), seed 32 tick 1. The other
# seeds add breadth over the friendly-fire-heavy region of the committed set.
_INVARIANT_SEEDS = (0, 4, 32, 13, 17, 34, 1, 9)


def test_no_resolved_kill_targets_an_impostor_across_seeds(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    for seed in _INVARIANT_SEEDS:
        replay_path = tmp_path / f"invariant-seed-{seed}.jsonl"
        game = HeadlessGame(
            seed=seed,
            game_map=game_map,
            agent_factory=build_default_agent_factory(),
            replay_path=replay_path,
            num_players=9,
            num_impostors=2,
            tasks_per_crewmate=2,
            meeting_runner=build_default_meeting_runner(),
            scheduler=TickScheduler(max_ticks=150),
        )
        result = game.run()
        players = result.final_state.players
        impostor_ids = {
            pid for pid, player in players.items() if player.role == "IMPOSTOR"
        }
        assert len(impostor_ids) == 2, f"seed {seed} must seed exactly 2 impostors"

        # (1) Engine guard: every resolved kill (a body) has a CREWMATE victim.
        for body in result.final_state.bodies.values():
            assert players[body.player_id].role == "CREWMATE", (
                f"seed {seed}: resolved kill landed on impostor {body.player_id}"
            )

        # (2) Policy teammate filter: no recorded kill *intent* targeted a fellow
        # impostor either, so the fix holds upstream of the guard, not only
        # because the engine rejected it.
        for entry in read_replay_entries(replay_path):
            for action in entry.actions:
                if action.get("type") != "kill":
                    continue
                actor = action.get("actor")
                payload = action.get("payload", {})
                target = payload.get("target") if isinstance(payload, dict) else None
                assert not (actor in impostor_ids and target in impostor_ids), (
                    f"seed {seed} tick {entry.tick}: impostor {actor} emitted a "
                    f"kill intent against fellow impostor {target}"
                )
