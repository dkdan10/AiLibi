"""Challenge opt-in choices with interrupts, stale evidence and idle loops."""

from __future__ import annotations

from typing import Any

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.tactical.crewmate_policy import CrewmatePolicy
from agents.tactical.experimental import (
    ExperimentalCrewmatePolicy,
    ExperimentalImpostorPolicy,
    TacticalExperimentOptions,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from observation.action_intent import ActionIntent
from observation.public_map import PublicMapView


def _map() -> PublicMapView:
    return PublicMapView(
        map_id="tactical_control",
        room_ids=("H", "A", "B", "C"),
        room_neighbors={
            "H": ("A", "B"),
            "A": ("H", "C"),
            "B": ("H", "C"),
            "C": ("A", "B"),
        },
        vent_rooms={"V0": "H", "V1": "A", "V2": "B"},
        vent_graph={"V0": ("V1", "V2"), "V1": ("V0", "V2"), "V2": ("V0", "V1")},
        task_locations={"task_a": "A", "task_c": "C"},
        spawn_room="H",
        meeting_room="H",
        emergency_button_room="H",
    )


def _vent_id(intent: ActionIntent) -> str:
    assert intent.type == "vent"
    return intent.payload.vent_id


def _event(
    memory: MemoryStore,
    tick: int,
    kind: str,
    *,
    provenance: str = "observed",
    **payload: Any,
) -> None:
    memory.append(
        EpisodicEvent(tick=tick, type=kind, provenance=provenance, payload=payload)
    )


def _snapshot(
    memory: MemoryStore,
    *,
    tick: int,
    room: str = "H",
    pending: str | None = None,
    vented: bool = False,
    cooldown: int = 2,
    teammates: tuple[str, ...] = (),
) -> None:
    _event(
        memory,
        tick,
        "self_state",
        room=room,
        role="IMPOSTOR",
        pending_task_id=pending,
        in_vent=vented,
        fellow_impostor_ids=teammates,
    )
    _event(memory, tick, "cooldown_status", cooldown=cooldown)


@pytest.mark.parametrize("idle", ["patrol", "accompany"])
def test_finished_crew_keep_exploring_and_resume_new_work(idle: str) -> None:
    options = TacticalExperimentOptions.model_validate({"crew_idle_policy": idle})
    policy = ExperimentalCrewmatePolicy(agent_id="crew", options=options)
    memory = MemoryStore()
    room = "H"
    visits: set[str] = set()
    for tick in range(16):
        _snapshot(memory, tick=tick, room=room)
        _event(
            memory,
            tick,
            "saw_player",
            player_id="companion",
            room="A",
            action="do_task",
        )
        intent = policy.decide(memory, _map())
        assert intent == policy.decide(memory, _map())
        assert intent.type == "move"
        assert intent.payload.to_room in _map().room_neighbors[room]
        room = intent.payload.to_room
        visits.add(room)
    assert visits == set(_map().room_ids)
    _snapshot(memory, tick=16, room="A", pending="task_a")
    assert policy.decide(memory, _map()).type == "do_task"


@pytest.mark.parametrize("interrupt", ["body", "repair"])
def test_exploring_crew_preserve_body_and_repair_interrupts(interrupt: str) -> None:
    memory = MemoryStore()
    _snapshot(memory, tick=3)
    if interrupt == "body":
        _event(
            memory, 3, "saw_body", body_id="public-victim", victim_id="victim", room="H"
        )
    else:
        _event(
            memory,
            3,
            "global_status",
            provenance="inferred",
            sabotage_active=True,
            sabotage_kind="reactor",
            sabotage_is_gating=True,
            sabotage_repair_rooms=("A",),
        )
    for idle in ("patrol", "accompany"):
        policy = ExperimentalCrewmatePolicy(
            agent_id="crew",
            options=TacticalExperimentOptions.model_validate(
                {"crew_idle_policy": idle}
            ),
        )
        assert policy.decide(memory, _map()) == CrewmatePolicy(agent_id="crew").decide(
            memory, _map()
        )


def test_risk_aware_exit_uses_only_recent_non_teammate_observations() -> None:
    policy = ExperimentalImpostorPolicy(
        agent_id="imp",
        options=TacticalExperimentOptions(vent_exit_policy="observed_risk"),
    )
    memory = MemoryStore()
    _snapshot(memory, tick=5, vented=True)
    _event(memory, 5, "saw_player", player_id="witness", room="A", action=None)
    assert _vent_id(ImpostorPolicy(agent_id="imp").decide(memory, _map())) == "V1"
    assert _vent_id(policy.decide(memory, _map())) == "V2"

    for mode in ("reported", "teammate", "stale"):
        alternate = MemoryStore()
        if mode == "stale":
            _event(
                alternate, 1, "saw_player", player_id="witness", room="A", action=None
            )
        _snapshot(
            alternate,
            tick=5,
            vented=True,
            teammates=("witness",) if mode == "teammate" else (),
        )
        if mode != "stale":
            _event(
                alternate,
                5,
                "saw_player",
                provenance="reported" if mode == "reported" else "observed",
                player_id="witness",
                room="A",
                action=None,
            )
        assert _vent_id(policy.decide(alternate, _map())) == "V1"


def test_risk_aware_exit_still_leaves_when_every_exit_is_exposed() -> None:
    memory = MemoryStore()
    _snapshot(memory, tick=5, vented=True)
    for room in ("A", "B"):
        _event(memory, 5, "saw_player", player_id=room, room=room, action=None)
    policy = ExperimentalImpostorPolicy(
        agent_id="imp",
        options=TacticalExperimentOptions(vent_exit_policy="observed_risk"),
    )
    intent = policy.decide(memory, _map())
    assert intent.type == "vent" and intent.payload.vent_id in ("V1", "V2")


def test_self_reporting_is_an_explicit_policy_choice_and_respects_vent_priority() -> (
    None
):
    memory = MemoryStore()
    _snapshot(memory, tick=5)
    _event(memory, 5, "saw_body", body_id="public-victim", victim_id="victim", room="H")
    candidate = ExperimentalImpostorPolicy(
        agent_id="imp", options=TacticalExperimentOptions(self_report=True)
    )
    assert ImpostorPolicy(agent_id="imp").decide(memory, _map()).type == "vent"
    assert candidate.decide(memory, _map()).type == "report"
    _snapshot(memory, tick=6, vented=True)
    _event(memory, 6, "saw_body", body_id="public-victim", victim_id="victim", room="H")
    assert candidate.decide(memory, _map()).type == "vent"


def test_earlier_sabotage_threshold_reaches_the_three_task_case_and_preserves_kills() -> (
    None
):
    memory = MemoryStore()
    _snapshot(memory, tick=5, pending="task_a")
    _event(
        memory,
        5,
        "global_status",
        provenance="inferred",
        tasks_completed=2,
        tasks_total=3,
        sabotage_active=False,
    )
    candidate = ExperimentalImpostorPolicy(
        agent_id="imp",
        options=TacticalExperimentOptions(sabotage_threshold="two_thirds"),
    )
    assert ImpostorPolicy(agent_id="imp").decide(memory, _map()).type == "move"
    assert candidate.decide(memory, _map()).type == "sabotage"
    _snapshot(memory, tick=6, cooldown=0)
    _event(memory, 6, "saw_player", player_id="victim", room="H", action=None)
    _event(
        memory,
        6,
        "global_status",
        provenance="inferred",
        tasks_completed=2,
        tasks_total=3,
        sabotage_active=False,
    )
    assert candidate.decide(memory, _map()).type == "kill"


def test_post_meeting_leads_require_survival_and_preserved_positions() -> None:
    memory = MemoryStore()
    _snapshot(memory, tick=5, cooldown=0)
    _event(memory, 5, "saw_player", player_id="survivor", room="A", action=None)
    _event(memory, 6, "meeting_boundary")
    _snapshot(memory, tick=6, cooldown=0)
    assert ImpostorPolicy(agent_id="imp").decide(memory, _map()).type == "wait"
    candidate = ExperimentalImpostorPolicy(
        agent_id="imp", options=TacticalExperimentOptions(post_meeting_retarget=True)
    )
    candidate.note_meeting_concluded(dead_ids=())
    assert candidate.decide(memory, _map()).type == "move"
    candidate.note_meeting_concluded(dead_ids=("survivor",))
    assert candidate.decide(memory, _map()).type == "wait"
    reset = ExperimentalImpostorPolicy(
        agent_id="imp",
        options=TacticalExperimentOptions(
            post_meeting_retarget=True, meeting_positions_preserved=False
        ),
    )
    reset.note_meeting_concluded(dead_ids=())
    assert reset.decide(memory, _map()).type == "wait"


def test_changed_repair_goal_preserves_a_legitimate_immediate_reverse() -> None:
    memory = MemoryStore()
    policy = ExperimentalCrewmatePolicy(
        agent_id="crew", options=TacticalExperimentOptions(crew_idle_policy="patrol")
    )
    _snapshot(memory, tick=0, room="H", pending="task_a")
    outbound = policy.decide(memory, _map())
    assert outbound.type == "move" and outbound.payload.to_room == "A"
    _snapshot(memory, tick=1, room="A", pending="task_a")
    _event(
        memory,
        1,
        "global_status",
        provenance="inferred",
        sabotage_active=True,
        sabotage_kind="reactor",
        sabotage_is_gating=True,
        sabotage_repair_rooms=("H",),
    )
    returning = policy.decide(memory, _map())
    assert returning.type == "move" and returning.payload.to_room == "H"


def test_body_escape_may_reverse_a_previously_useful_hunt() -> None:
    public_map = _map().model_copy(update={"vent_rooms": {}, "vent_graph": {}})
    memory = MemoryStore()
    policy = ExperimentalImpostorPolicy(
        agent_id="imp",
        options=TacticalExperimentOptions(vent_exit_policy="observed_risk"),
    )
    # C's alphabetically first neighbor is A, so walking A -> C to hunt
    # becomes C -> A to leave a newly discovered body. A reverse ban is wrong.
    _snapshot(memory, tick=0, room="A", cooldown=0)
    _event(memory, 0, "saw_player", player_id="target", room="C", action=None)
    outbound = policy.decide(memory, public_map)
    assert outbound.type == "move" and outbound.payload.to_room == "C"
    _snapshot(memory, tick=1, room="C", cooldown=0)
    _event(memory, 1, "saw_body", body_id="body-target", victim_id="target", room="C")
    returning = policy.decide(memory, public_map)
    assert returning.type == "move" and returning.payload.to_room == "A"


def test_unchanged_task_goal_strictly_reduces_public_route_distance() -> None:
    from agents.tactical.pathing import find_path

    public_map = _map()
    for start in public_map.room_ids:
        memory = MemoryStore()
        policy = ExperimentalCrewmatePolicy(
            agent_id="crew",
            options=TacticalExperimentOptions(crew_idle_policy="patrol"),
        )
        room = start
        remaining = len(find_path(public_map=public_map, start=room, goal="C"))
        for tick in range(len(public_map.room_ids)):
            _snapshot(memory, tick=tick, room=room, pending="task_c")
            intent = policy.decide(memory, public_map)
            if room == "C":
                assert intent.type == "do_task"
                break
            assert intent.type == "move"
            room = intent.payload.to_room
            new_remaining = len(find_path(public_map=public_map, start=room, goal="C"))
            assert new_remaining == remaining - 1
            remaining = new_remaining
        else:
            pytest.fail("a fixed reachable task goal failed to make progress")
