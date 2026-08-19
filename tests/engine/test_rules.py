"""Engine action-rule tests (DESIGN.md §3.4).

Two rules with the same shape, both enforced in ``engine/rules.py`` because the
engine — not agent code — is the single source of truth for legality:

* the friendly-fire guard in ``resolve_kill`` (a fellow impostor is never a valid
  target), plus the end-to-end invariant that no resolved kill in a seeded
  multi-impostor game ever lands on a teammate;
* the in-vent ruling: from inside a vent the ONLY legal actions are ``vent`` and
  ``wait``, so kill, report and sabotage are rejected alongside the move,
  do_task, emergency and repair_sabotage guards that already existed.

Both are defense-in-depth — the tactical policies already filter teammates and
branch on ``in_vent`` — so the tests exist to stop a buggy, mask-sampling or
LLM-driven policy from reaching a state the rules forbid.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import get_args

import pytest
from pydantic import TypeAdapter

from engine.actions import Action, KillAction, ReportBodyAction, SabotageAction
from engine.entities import BodyState, PlayerState
from engine.events import event_to_dict
from engine.rng import EngineRng
from engine.rules import (
    ActionRejectedError,
    resolve_kill,
    resolve_report,
    resolve_sabotage,
)
from engine.tick import advance_tick
from engine.world import WorldState, load_canonical_map
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import read_replay_entries
from orchestrator.scheduler import TickScheduler

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)


def _action(data: object) -> Action:
    return _ACTION_ADAPTER.validate_python(data)


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


# -- the in-vent ruling: only `vent` and `wait` are legal from inside a vent ---


def _report(actor: str, body_id: str) -> ReportBodyAction:
    return ReportBodyAction.model_validate(
        {"type": "report", "actor": actor, "payload": {"body_id": body_id}}
    )


def _sabotage(actor: str, kind: str) -> SabotageAction:
    return SabotageAction.model_validate(
        {"type": "sabotage", "actor": actor, "payload": {"kind": kind}}
    )


def _in_vent_state() -> WorldState:
    """An impostor inside the ADMIN vent with every OTHER precondition satisfied.

    ``p-1`` is an IMPOSTOR in the ADMIN vent and off cooldown; ``p-2`` is a living
    crewmate in ADMIN (a legal kill target), ``body-p-4-0`` is an undiscovered
    body in ADMIN (a legal report), and no sabotage is active (a legal sabotage).
    Standing in the room, all three would resolve — so every rejection this
    fixture produces is attributable to the vent alone.
    """

    players = {
        "p-1": replace(_player("p-1", "IMPOSTOR", room="ADMIN"), in_vent=True),
        "p-2": _player("p-2", "CREWMATE", room="ADMIN"),
        "p-3": _player("p-3", "CREWMATE", room="ADMIN"),
        "p-4": replace(_player("p-4", "CREWMATE", room="ADMIN"), alive=False),
    }
    return WorldState(
        tick=0,
        phase="PLAY",
        map="canonical_1",
        players=players,
        bodies={
            "body-p-4-0": BodyState(
                id="body-p-4-0",
                player_id="p-4",
                room="ADMIN",
                position=(0.0, 0.0),
                killed_by="p-1",
                discovered_by=None,
            )
        },
        tasks={},
        sabotage=None,
        cooldowns={pid: 0 for pid in players},
        emergency_uses={},
        rng_state=EngineRng.from_seed(1).snapshot(),
        seed=1,
    )


def _out_of_vent(state: WorldState) -> WorldState:
    """``state`` with ``p-1`` standing in the room instead of inside the vent."""

    players = dict(state.players)
    players["p-1"] = replace(players["p-1"], in_vent=False)
    return replace(state, players=players)


def test_resolve_kill_rejects_in_vent_actor() -> None:
    state = _in_vent_state()
    with pytest.raises(ActionRejectedError, match="cannot kill while in vent"):
        resolve_kill(state, _kill("p-1", "p-2"))

    # The guard bites on the vent and nothing else: out of the vent the same
    # actor, target, room and cooldown resolve the kill.
    body, event = resolve_kill(_out_of_vent(state), _kill("p-1", "p-2"))
    assert body.player_id == "p-2"
    assert event.type == "Killed"


def test_resolve_report_rejects_in_vent_actor() -> None:
    state = _in_vent_state()
    with pytest.raises(ActionRejectedError, match="cannot report a body while in vent"):
        resolve_report(state, _report("p-1", "body-p-4-0"))

    event = resolve_report(_out_of_vent(state), _report("p-1", "body-p-4-0"))
    assert event.type == "MeetingTriggered"
    assert event.trigger == "report"


def test_resolve_sabotage_rejects_in_vent_actor() -> None:
    game_map = load_canonical_map()
    state = _in_vent_state()
    with pytest.raises(ActionRejectedError, match="cannot sabotage while in vent"):
        resolve_sabotage(state, game_map, _sabotage("p-1", "lights"))

    event = resolve_sabotage(_out_of_vent(state), game_map, _sabotage("p-1", "lights"))
    assert event.type == "SabotageStarted"
    assert event.kind == "lights"


# One representative action per member of the ``engine.actions.Action`` union,
# all submitted by the vented ``p-1`` of ``_in_vent_state`` and all naming a real
# canonical-map room / task / vent / sabotage kind. Every in-vent guard precedes
# its own function's remaining preconditions, so an "in vent" rejection reason is
# proof the vent is what rejected the action.
_IN_VENT_ACTION_TABLE: dict[str, dict[str, object]] = {
    "move": {"type": "move", "actor": "p-1", "payload": {"to_room": "CAFETERIA"}},
    "do_task": {
        "type": "do_task",
        "actor": "p-1",
        "payload": {"task_id": "swipe_card"},
    },
    "kill": {"type": "kill", "actor": "p-1", "payload": {"target": "p-2"}},
    "vent": {"type": "vent", "actor": "p-1", "payload": {"vent_id": "ADMIN_VENT"}},
    "report": {
        "type": "report",
        "actor": "p-1",
        "payload": {"body_id": "body-p-4-0"},
    },
    "emergency": {"type": "emergency", "actor": "p-1", "payload": {}},
    "sabotage": {"type": "sabotage", "actor": "p-1", "payload": {"kind": "lights"}},
    "repair_sabotage": {
        "type": "repair_sabotage",
        "actor": "p-1",
        "payload": {"kind": "lights"},
    },
    "wait": {"type": "wait", "actor": "p-1", "payload": {}},
}

# The two survivors, and the event each must emit when it resolves.
_IN_VENT_LEGAL_ACTIONS: dict[str, str] = {"vent": "VentExited", "wait": "Waited"}


def _action_type_names() -> frozenset[str]:
    """Every ``type`` discriminator in the :data:`engine.actions.Action` union.

    Read from the union itself, so a tenth action type fails the table test below
    until the in-vent ruling covers it.
    """

    union, *_ = get_args(Action)
    names: set[str] = set()
    for member in get_args(union):
        (literal,) = get_args(member.model_fields["type"].annotation)
        names.add(str(literal))
    return frozenset(names)


def test_in_vent_actor_may_only_vent_or_wait() -> None:
    # The ruling is TOTAL, not three ad-hoc guards: from inside a vent the engine
    # accepts exactly `vent` and `wait` and rejects every other action type,
    # naming the vent as the reason each time.
    assert set(_IN_VENT_ACTION_TABLE) == _action_type_names(), (
        "the in-vent table must cover every engine action type"
    )

    game_map = load_canonical_map()
    state = _in_vent_state()
    accepted: set[str] = set()
    for action_type, payload in sorted(_IN_VENT_ACTION_TABLE.items()):
        _, events = advance_tick(state, [_action(payload)], game_map=game_map)
        rejections = [event for event in events if event.type == "ActionRejected"]
        if not rejections:
            accepted.add(action_type)
            assert events[0].type == _IN_VENT_LEGAL_ACTIONS.get(action_type), (
                f"{action_type} resolved from inside a vent, emitting {events[0].type}"
            )
            continue
        reason = event_to_dict(rejections[0])["reason"]
        assert "in vent" in reason, (
            f"{action_type} was rejected for a reason other than the vent: {reason}"
        )
    assert accepted == set(_IN_VENT_LEGAL_ACTIONS)


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
