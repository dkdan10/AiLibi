"""The full meeting reset, coherent for agents and instruments.

``meeting_reset = "hub_with_grace"`` is the full reset: at a meeting's close the
engine gathers the survivors in the meeting room, clears every corpse, empties
the vents, stops ongoing actions and restarts each living impostor's kill
cooldown at the map's value (``engine.meeting_reset``). This module pins that
reset at the orchestrator entry, the order it runs in, the grace window it
opens, what the first packets after it are built from
(``orchestrator.replay.compose_resume_events``), the four readings of one
fake-provider game that must agree at every meeting open (the live agents, the
replay loader, the prompt golden and the evidence-honesty walk), the gameplay
census cells the reset forces to zero, the viewer's first frame after it, and
the documents that state it. Every recording is made from a declared config,
with no environment export, by the fake provider and a scripted client.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Final

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import BaseModel

import api.replay_loader as loader_module
import eval.evidence_honesty as honesty_module
import eval.funnel as funnel_module
import eval.replay_walk as walk_module
import orchestrator.game as game_module
import orchestrator.replay as replay_module
import tests.meetings.test_prompt_byte_golden as golden
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import AgentMemory, render_for_prompt
from api.replay_loader import ReplayLoader
from engine.actions import (
    Action,
    DoTaskAction,
    EmergencyMeetingAction,
    KillAction,
    MoveAction,
    VentAction,
    WaitAction,
)
from engine.entities import BodyState, SabotageState, TaskState
from engine.events import (
    ActionRejectedEvent,
    EngineEvent,
    GameOverEvent,
    KilledEvent,
    MeetingTriggeredEvent,
    MovedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
    TickAdvancedEvent,
    VentEnteredEvent,
    VentExitedEvent,
    WaitedEvent,
)
from engine.rng import EngineRng
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from eval.gameplay_census import (
    BUTTON_COOLDOWN_TICKS,
    _REGROUP_DROPPED_KINDS,
    CensusInputs,
    GameplayCensusConformanceError,
    load_census_inputs,
)
from eval.recorded_settings import read_recorded_settings
from eval.replay_walk import (
    MeetingApplied,
    MeetingOpened,
    TickOpened,
    WalkComplete,
    walk_replay,
)
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from agents.memory.store import DEFAULT_TOKEN_BUDGET
from meetings.manager import MeetingManager, MeetingTrigger, extract_belief_evidence
from meetings.schemas import (
    CorroborationClaim,
    FoundBodyObservation,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    SawPlayerObservation,
)
from observation.service import ObservationService
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.game import (
    DefaultMeetingRunner,
    _assert_no_emergency_opening_body,
    apply_meeting_result,
)
from orchestrator.replay import (
    REGROUP_KEPT_EVENTS,
    REGROUP_REPORTED_DROP_KINDS,
    MeetingReplayEntry,
    ResumeEvents,
    compose_resume_events,
    derive_regroup_ticks,
    fold_public_regroup,
    meeting_regrouped,
    read_all_entries,
    regroup_room_for,
)
from orchestrator.seeder import seed_initial_state
from tests._helpers.scripted_meeting import record_game

_SCRIPTS: Final[Path] = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import publish_gameplay_census  # noqa: E402

RESET: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    meeting_reset="hub_with_grace"
)
_ROSTER: Final[dict[str, int]] = {
    "num_players": 9,
    "num_impostors": 2,
    "tasks_per_crewmate": 2,
}


# =========================================================================== #
# 1. The reset at the orchestrator entry                                      #
# =========================================================================== #


@dataclass(frozen=True)
class _Cast:
    """Who is who in a hand-built 9-player meeting state."""

    impostors: tuple[str, str]
    crew: tuple[str, ...]

    @property
    def venter(self) -> str:
        return self.impostors[0]

    @property
    def trigger_victim(self) -> str:
        return self.crew[0]

    @property
    def unreported(self) -> tuple[str, str]:
        return (self.crew[1], self.crew[2])

    @property
    def reporter(self) -> str:
        return self.crew[3]


def _cast(state: WorldState) -> _Cast:
    impostors = tuple(
        sorted(pid for pid, p in state.players.items() if p.role == "IMPOSTOR")
    )
    crew = tuple(
        sorted(pid for pid, p in state.players.items() if p.role == "CREWMATE")
    )
    assert len(impostors) == 2
    return _Cast(impostors=(impostors[0], impostors[1]), crew=crew)


_ROOMS: Final[tuple[str, ...]] = (
    "ADMIN",
    "LABS",
    "MEDBAY",
    "ENGINEERING",
    "STORAGE",
    "REACTOR",
    "WEST_HALL",
    "EAST_HALL",
    "UPPER_HALL",
)


def _meeting_state(game_map: Map) -> tuple[WorldState, _Cast, str]:
    """A MEETING state: a trigger corpse, two unreported corpses, a venting impostor.

    The impostor in a vent has cooldown 0, the reactor is sabotaged with repair
    progress, one player has used the button, and every player stands outside
    the meeting room.
    """

    state = seed_initial_state(seed=3, game_map=game_map, **_ROSTER)
    cast = _cast(state)
    dead = {cast.trigger_victim, *cast.unreported}
    players = {
        pid: replace(
            player,
            room=_ROOMS[index],
            alive=pid not in dead,
            in_vent=pid == cast.venter,
        )
        for index, (pid, player) in enumerate(sorted(state.players.items()))
    }
    players[cast.venter] = replace(players[cast.venter], room="ADMIN", in_vent=True)
    bodies = {
        f"body-{victim}-7": BodyState(
            id=f"body-{victim}-7",
            player_id=victim,
            room=players[victim].room,
            position=(0.0, 0.0),
            killed_by=cast.impostors[1],
            discovered_by=cast.reporter if victim == cast.trigger_victim else None,
        )
        for victim in sorted(dead)
    }
    tasks = {
        task_id: task for task_id, task in state.tasks.items() if task.owner not in dead
    }
    state = replace(
        state,
        tick=9,
        phase="MEETING",
        players=players,
        bodies=bodies,
        tasks=tasks,
        cooldowns={cast.venter: 0, cast.impostors[1]: 2},
        sabotage=SabotageState(
            kind="reactor",
            remaining_ticks=5,
            affected_rooms=(),
            active=True,
            repair_progress={"REACTOR": 1},
        ),
        emergency_uses={cast.crew[4]: 1},
    )
    return state, cast, f"body-{cast.trigger_victim}-7"


def _skipped(state: WorldState, opener: str) -> MeetingResult:
    return MeetingResult(
        meeting_id="m-0",
        triggered_by=opener,
        trigger_tick=state.tick,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
        transcript=MeetingTranscript(turns=()),
    )


def _one_draw(rng_state: bytes) -> bytes:
    _, advanced = EngineRng.from_state(rng_state).randint(0, 2**31 - 1)
    return advanced


def test_the_reset_at_the_orchestrator_entry_clears_what_it_must() -> None:
    game_map = load_canonical_map()
    state, cast, trigger_body = _meeting_state(game_map)
    after, events = apply_meeting_result(
        state,
        _skipped(state, cast.reporter),
        game_map=game_map,
        triggering_body_id=trigger_body,
        meeting_reset="hub_with_grace",
    )
    assert events == []
    assert after.phase == "PLAY"
    assert dict(after.bodies) == {}
    assert not any(player.in_vent for player in after.players.values())
    assert dict(after.cooldowns) == {
        impostor: game_map.kill_cooldown_ticks for impostor in cast.impostors
    }
    assert {
        pid: player.room for pid, player in after.players.items() if player.alive
    } == {
        pid: game_map.meeting.room
        for pid, player in state.players.items()
        if player.alive
    }
    assert after.tasks == state.tasks
    assert after.sabotage == state.sabotage
    assert after.emergency_uses == state.emergency_uses
    assert {pid: p.alive for pid, p in after.players.items()} == {
        pid: p.alive for pid, p in state.players.items()
    }
    assert after.tick == state.tick + 1
    assert after.rng_state == _one_draw(state.rng_state)


def test_the_preserve_twin_keeps_the_unreported_corpses_the_vent_and_the_cooldown() -> (
    None
):
    game_map = load_canonical_map()
    state, cast, trigger_body = _meeting_state(game_map)
    after, _ = apply_meeting_result(
        state,
        _skipped(state, cast.reporter),
        game_map=game_map,
        triggering_body_id=trigger_body,
    )
    assert set(after.bodies) == set(state.bodies) - {trigger_body}
    assert after.players[cast.venter].in_vent
    assert after.cooldowns == state.cooldowns
    assert {pid: p.room for pid, p in after.players.items()} == {
        pid: p.room for pid, p in state.players.items()
    }
    assert after.tick == state.tick + 1


def test_the_reset_reads_its_room_and_its_cooldown_from_the_map() -> None:
    game_map = load_canonical_map()
    planted = game_map.model_copy(
        update={
            "kill_cooldown_ticks": game_map.kill_cooldown_ticks + 3,
            "meeting": game_map.meeting.model_copy(update={"room": "ADMIN"}),
        }
    )
    state, cast, trigger_body = _meeting_state(game_map)
    after, _ = apply_meeting_result(
        state,
        _skipped(state, cast.reporter),
        game_map=planted,
        triggering_body_id=trigger_body,
        meeting_reset="hub_with_grace",
    )
    assert set(after.cooldowns.values()) == {game_map.kill_cooldown_ticks + 3}
    assert {p.room for p in after.players.values() if p.alive} == {"ADMIN"}


# =========================================================================== #
# 2. Order and openings                                                       #
# =========================================================================== #


def test_an_impostor_parity_win_at_the_meeting_ends_before_any_reset() -> None:
    game_map = load_canonical_map()
    state, cast, trigger_body = _meeting_state(game_map)
    # Two impostors and three crewmates alive; ejecting a crewmate reaches parity.
    extra_dead = {cast.crew[4]}
    players = {
        pid: replace(player, alive=False) if pid in extra_dead else player
        for pid, player in state.players.items()
    }
    state = replace(state, players=players)
    alive_crew = sorted(
        pid for pid, p in state.players.items() if p.alive and p.role == "CREWMATE"
    )
    assert len(alive_crew) == 3
    ejected = alive_crew[-1]
    result = _skipped(state, cast.reporter).model_copy(
        update={"outcome": "EJECTED", "ejected_player_id": ejected}
    )
    after, events = apply_meeting_result(
        state,
        result,
        game_map=game_map,
        triggering_body_id=trigger_body,
        meeting_reset="hub_with_grace",
    )
    assert after.phase == "GAME_OVER"
    assert [type(event) for event in events] == [GameOverEvent]
    assert isinstance(events[0], GameOverEvent) and events[0].winner == "IMPOSTORS"
    # No reset ran: the survivors stand where they stood, the unreported
    # corpses lie where they fell, and neither tick nor rng moved.
    assert {pid: p.room for pid, p in after.players.items()} == {
        pid: p.room for pid, p in state.players.items()
    }
    assert set(after.bodies) == set(state.bodies) - {trigger_body}
    assert after.players[cast.venter].in_vent
    assert after.tick == state.tick
    assert after.rng_state == state.rng_state


def _found_body_opening(result_id: str, opener: str) -> MeetingResult:
    return MeetingResult(
        meeting_id=result_id,
        triggered_by=opener,
        trigger_tick=20,
        outcome="SKIPPED",
        ejected_player_id=None,
        ballots=(),
        transcript=MeetingTranscript(
            turns=(
                MeetingTurn(
                    turn_id=f"{result_id}:turn-0",
                    turn_index=0,
                    speaker=opener,
                    turn_kind="opening",
                    reply_to=None,
                    observations=(
                        FoundBodyObservation(
                            type="found_body", tick=19, body_of="p-9", room="LABS"
                        ),
                    ),
                    free_text="I found a body -- unsure who did it",
                ),
            )
        ),
    )


def test_a_found_body_emergency_opening_still_raises() -> None:
    with pytest.raises(RuntimeError, match="fabricated found_body"):
        _assert_no_emergency_opening_body(
            trigger_kind="emergency", result=_found_body_opening("m-1", "p-2")
        )
    _assert_no_emergency_opening_body(
        trigger_kind="report", result=_found_body_opening("m-1", "p-2")
    )


# =========================================================================== #
# 3. The grace window, end to end                                             #
# =========================================================================== #


def _kill_sequence(meeting_reset: str) -> list[tuple[int, str]]:
    """Advance play after a meeting at tick 9, the ready impostor trying to kill.

    Returns ``(tick, outcome)`` per play tick, where outcome is ``Killed`` or the
    rejection reason.
    """

    game_map = load_canonical_map()
    state, cast, trigger_body = _meeting_state(game_map)
    killer = cast.venter
    target = next(
        pid for pid in cast.crew if state.players[pid].alive and pid != cast.reporter
    )
    players = dict(state.players)
    # Out of the vent and beside the target, so only the cooldown decides.
    players[killer] = replace(players[killer], in_vent=False, room="ADMIN")
    players[target] = replace(players[target], room="ADMIN")
    state = replace(state, players=players)
    state, _ = apply_meeting_result(
        state,
        _skipped(state, cast.reporter),
        game_map=game_map,
        triggering_body_id=trigger_body,
        meeting_reset=meeting_reset,  # type: ignore[arg-type]
    )
    outcomes: list[tuple[int, str]] = []
    for _ in range(game_map.kill_cooldown_ticks + 1):
        actions = [
            KillAction.model_validate(
                {"type": "kill", "actor": killer, "payload": {"target": target}}
            )
        ] + [
            WaitAction.model_validate({"type": "wait", "actor": pid, "payload": {}})
            for pid, player in sorted(state.players.items())
            if player.alive and pid != killer
        ]
        tick = state.tick
        state, events = advance_tick(state, actions, game_map=game_map)
        killed = [event for event in events if isinstance(event, KilledEvent)]
        rejected = [
            event
            for event in events
            if isinstance(event, ActionRejectedEvent) and event.actor == killer
        ]
        outcomes.append((tick, "Killed" if killed else rejected[0].reason))
        if killed:
            break
    return outcomes


def test_a_kill_after_a_regroup_is_refused_until_the_map_cooldown_runs_out() -> None:
    cooldown = load_canonical_map().kill_cooldown_ticks
    outcomes = _kill_sequence("hub_with_grace")
    meeting_tick = 9
    assert [tick for tick, outcome in outcomes if outcome != "Killed"] == list(
        range(meeting_tick + 1, meeting_tick + cooldown + 1)
    )
    assert all(outcome == "kill is on cooldown" for _, outcome in outcomes[:-1])
    assert outcomes[-1] == (meeting_tick + cooldown + 1, "Killed")


def test_under_preserve_the_ready_impostor_kills_on_the_resume_tick() -> None:
    assert _kill_sequence("preserve") == [(10, "Killed")]


# =========================================================================== #
# 4. Resume perception, one helper                                           #
# =========================================================================== #


@dataclass(frozen=True)
class _TriggerTick:
    """One trigger tick's world: the meeting state, its events and who is where."""

    state: WorldState
    events: tuple[EngineEvent, ...]
    leaver: str
    tasker: str
    medbay_observer: str
    venter: str
    vent_witness: str
    killer: str
    kill_witness: str


def _trigger_tick() -> _TriggerTick:
    """The trigger tick before a button call, resolved by the real engine.

    In action order: a crewmate walks out of the meeting room, another steps a
    MEDBAY task beside a MEDBAY observer, an impostor enters the ADMIN vent in
    view of a crewmate, the other impostor kills in ENGINEERING in view of a
    crewmate, and a player presses the button.
    """

    game_map = load_canonical_map()
    state = seed_initial_state(seed=3, game_map=game_map, **_ROSTER)
    cast = _cast(state)
    crew = cast.crew
    venter, killer = cast.impostors
    leaver, tasker, medbay_observer, vent_witness, victim, kill_witness, caller = crew
    rooms = {
        leaver: "CAFETERIA",
        tasker: "MEDBAY",
        medbay_observer: "MEDBAY",
        venter: "ADMIN",
        vent_witness: "ADMIN",
        killer: "ENGINEERING",
        victim: "ENGINEERING",
        kill_witness: "ENGINEERING",
        caller: "CAFETERIA",
    }
    players = {pid: replace(p, room=rooms[pid]) for pid, p in state.players.items()}
    tasks = dict(state.tasks)
    tasks[f"{tasker}:submit_scan"] = TaskState(
        id=f"{tasker}:submit_scan",
        owner=tasker,
        map_task_id="submit_scan",
        room="MEDBAY",
        progress=0,
        required_ticks=10,
        completed=False,
    )
    state = replace(
        state, tick=12, players=players, tasks=tasks, cooldowns={killer: 0, venter: 0}
    )
    actions: list[Action] = [
        MoveAction.model_validate(
            {"type": "move", "actor": leaver, "payload": {"to_room": "UPPER_HALL"}}
        ),
        DoTaskAction.model_validate(
            {"type": "do_task", "actor": tasker, "payload": {"task_id": "submit_scan"}}
        ),
        VentAction.model_validate(
            {"type": "vent", "actor": venter, "payload": {"vent_id": "ADMIN_VENT"}}
        ),
        KillAction.model_validate(
            {"type": "kill", "actor": killer, "payload": {"target": victim}}
        ),
        EmergencyMeetingAction.model_validate(
            {"type": "emergency", "actor": caller, "payload": {"reason": "check in"}}
        ),
    ]
    meeting, events = advance_tick(state, actions, game_map=game_map)
    assert meeting.phase == "MEETING"
    kinds = [type(event) for event in events]
    assert kinds == [
        MovedEvent,
        TaskProgressedEvent,
        VentEnteredEvent,
        KilledEvent,
        MeetingTriggeredEvent,
    ]
    return _TriggerTick(
        state=meeting,
        events=tuple(events),
        leaver=leaver,
        tasker=tasker,
        medbay_observer=medbay_observer,
        venter=venter,
        vent_witness=vent_witness,
        killer=killer,
        kill_witness=kill_witness,
    )


def _resume_packets(
    trigger: _TriggerTick, *, meeting_reset: str, regrouped: bool
) -> dict[str, Any]:
    game_map = load_canonical_map()
    resumed, post_events = apply_meeting_result(
        trigger.state,
        _skipped(trigger.state, "p-1"),
        game_map=game_map,
        meeting_reset=meeting_reset,  # type: ignore[arg-type]
    )
    events = compose_resume_events(trigger.events, post_events, regrouped=regrouped)
    with tempfile.TemporaryDirectory() as directory:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(directory) / "audit.jsonl"
        )
        try:
            return {
                pid: service.build_packet(
                    world_state=resumed, agent_id=pid, engine_events=events.events
                )
                for pid, player in sorted(resumed.players.items())
                if player.alive
            }
        finally:
            service.close()


def _moved_ids(packets: Mapping[str, Any]) -> set[tuple[str, str]]:
    return {
        (observer, moved.id)
        for observer, packet in packets.items()
        for moved in packet.moved_players
    }


def _actions(packets: Mapping[str, Any]) -> set[tuple[str, str, str, str | None]]:
    return {
        (observer, seen.id, seen.room, seen.action)
        for observer, packet in packets.items()
        for seen in packet.visible_players
        if seen.action is not None
    }


def test_after_a_regroup_no_observer_views_the_trigger_ticks_walk_or_task() -> None:
    trigger = _trigger_tick()
    packets = _resume_packets(trigger, meeting_reset="hub_with_grace", regrouped=True)
    assert not any(mover == trigger.leaver for _, mover in _moved_ids(packets))
    assert not any(
        subject == trigger.tasker and action == "task"
        for _, subject, _, action in _actions(packets)
    )


def test_after_a_regroup_the_witnessed_vent_and_kill_still_arrive() -> None:
    trigger = _trigger_tick()
    packets = _resume_packets(trigger, meeting_reset="hub_with_grace", regrouped=True)
    actions = _actions(packets)
    assert (trigger.vent_witness, trigger.venter, "ADMIN", "vent") in actions
    assert (trigger.kill_witness, trigger.killer, "ENGINEERING", "kill") in actions
    assert packets[trigger.killer].self_state.own_kill is not None


def test_without_the_filter_the_regroup_hands_every_observer_false_views() -> None:
    trigger = _trigger_tick()
    packets = _resume_packets(trigger, meeting_reset="hub_with_grace", regrouped=False)
    game_map = load_canonical_map()
    # Everyone now stands in the meeting room, so the departure and the task step
    # read as seen from there by observers who were nowhere near them.
    assert (trigger.medbay_observer, trigger.leaver) in _moved_ids(packets)
    assert (
        trigger.kill_witness,
        trigger.tasker,
        game_map.meeting.room,
        "task",
    ) in _actions(packets)


def test_a_keep_set_without_the_kill_loses_the_kill_witness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trigger = _trigger_tick()
    monkeypatch.setattr(
        replay_module, "REGROUP_KEPT_EVENTS", (VentEnteredEvent, VentExitedEvent)
    )
    packets = _resume_packets(trigger, meeting_reset="hub_with_grace", regrouped=True)
    assert (trigger.kill_witness, trigger.killer, "ENGINEERING", "kill") not in (
        _actions(packets)
    )
    assert packets[trigger.killer].self_state.own_kill is None


def test_the_preserve_twin_still_delivers_the_medbay_task_sighting() -> None:
    trigger = _trigger_tick()
    packets = _resume_packets(trigger, meeting_reset="preserve", regrouped=False)
    assert (trigger.medbay_observer, trigger.tasker, "MEDBAY", "task") in _actions(
        packets
    )


def _event_pool(tick: int) -> list[EngineEvent]:
    return [
        MovedEvent(type="Moved", tick=tick, actor="p-1", from_room="A", to_room="B"),
        TaskProgressedEvent(
            type="TaskProgressed",
            tick=tick,
            actor="p-2",
            task_id="submit_scan",
            progress=1,
            required_ticks=10,
        ),
        TaskCompletedEvent(
            type="TaskCompleted",
            tick=tick,
            actor="p-3",
            task_id="swipe_card",
            progress=3,
            required_ticks=3,
        ),
        KilledEvent(
            type="Killed", tick=tick, actor="p-4", target="p-5", room="A", witnesses=()
        ),
        VentEnteredEvent(
            type="VentEntered",
            tick=tick,
            actor="p-4",
            vent_id="ADMIN_VENT",
            room="ADMIN",
            source_vent_id="ADMIN_VENT",
            destination_vent_id="ADMIN_VENT",
            source_room="ADMIN",
            destination_room="ADMIN",
            traversal_ticks=1,
            witnesses=(),
            source_witnesses=(),
            destination_witnesses=(),
        ),
        VentExitedEvent(
            type="VentExited",
            tick=tick,
            actor="p-4",
            vent_id="MEDBAY_VENT",
            room="MEDBAY",
            source_vent_id="ADMIN_VENT",
            destination_vent_id="MEDBAY_VENT",
            source_room="ADMIN",
            destination_room="MEDBAY",
            traversal_ticks=1,
            witnesses=(),
            source_witnesses=(),
            destination_witnesses=(),
        ),
        ActionRejectedEvent(
            type="ActionRejected", tick=tick, actor="p-6", action="do_task", reason="x"
        ),
        MeetingTriggeredEvent(
            type="MeetingTriggered",
            tick=tick,
            actor="p-7",
            trigger="emergency",
            body_id=None,
        ),
        WaitedEvent(type="Waited", tick=tick, actor="p-8"),
        TickAdvancedEvent(type="TickAdvanced", tick=tick + 1),
    ]


@settings(deadline=None, max_examples=200)
@given(
    picks=st.lists(st.integers(min_value=0, max_value=9), max_size=25),
    tail=st.lists(st.integers(min_value=0, max_value=9), max_size=3),
)
def test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest(
    picks: list[int], tail: list[int]
) -> None:
    pool = _event_pool(12)
    trigger_events = [pool[index] for index in picks]
    meeting_events = [pool[index] for index in tail]
    plain = compose_resume_events(trigger_events, meeting_events)
    assert plain == ResumeEvents(
        events=tuple(trigger_events) + tuple(meeting_events), dropped=()
    )
    if meeting_events:
        with pytest.raises(
            ValueError,
            match=rf"applying it emits no events; got {len(meeting_events)}$",
        ):
            compose_resume_events(trigger_events, meeting_events, regrouped=True)
        return
    regrouped = compose_resume_events(trigger_events, (), regrouped=True)
    assert regrouped.events == tuple(
        event
        for event in trigger_events
        if isinstance(event, (KilledEvent, VentEnteredEvent, VentExitedEvent))
    )
    counts = {
        kind: sum(1 for event in trigger_events if event.type == kind)
        for kind in ("Moved", "TaskProgressed", "TaskCompleted")
    }
    assert regrouped.dropped == tuple(
        (kind, count) for kind, count in counts.items() if count
    )


def test_the_helper_names_the_kinds_the_census_table_counts() -> None:
    assert REGROUP_REPORTED_DROP_KINDS == _REGROUP_DROPPED_KINDS
    assert {cls.__name__ for cls in REGROUP_KEPT_EVENTS} == {
        "KilledEvent",
        "VentEnteredEvent",
        "VentExitedEvent",
    }


# =========================================================================== #
# 5. The regroup ticks                                                        #
# =========================================================================== #


@settings(deadline=None)
@given(meeting_ticks=st.frozensets(st.integers(min_value=0, max_value=200), max_size=8))
def test_the_regroup_ticks_are_each_prior_meetings_resume_tick(
    meeting_ticks: frozenset[int],
) -> None:
    assert derive_regroup_ticks(RESET, meeting_ticks) == frozenset(
        tick + 1 for tick in meeting_ticks
    )
    assert derive_regroup_ticks(None, meeting_ticks) == frozenset()
    assert (
        derive_regroup_ticks(RecordedExperimentConfig(), meeting_ticks) == frozenset()
    )


@pytest.mark.parametrize("room", ["CAFETERIA", "ADMIN"])
def test_the_regroup_room_is_the_maps_meeting_room_under_the_reset(room: str) -> None:
    assert regroup_room_for(RESET, meeting_room=room) == room
    assert regroup_room_for(None, meeting_room=room) is None
    assert regroup_room_for(RecordedExperimentConfig(), meeting_room=room) is None


@pytest.mark.parametrize(
    ("config", "phase", "expected"),
    [
        (RESET, "PLAY", True),
        (RESET, "GAME_OVER", False),
        (RecordedExperimentConfig(), "PLAY", False),
        (None, "PLAY", False),
    ],
)
def test_a_meeting_regroups_only_under_the_reset_and_only_when_play_resumes(
    config: RecordedExperimentConfig | None, phase: str, expected: bool
) -> None:
    assert meeting_regrouped(config, phase_after=phase) is expected


def test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else() -> None:
    game_map = load_canonical_map()
    state = seed_initial_state(seed=SEED, game_map=game_map, **_ROSTER)
    dead = "p-3"
    state = replace(
        state,
        tick=14,
        players={
            pid: replace(player, alive=pid != dead)
            for pid, player in state.players.items()
        },
    )
    memories = {pid: AgentMemory() for pid in state.players if pid != "p-9"}
    fold_public_regroup(memories, state=state, room="ADMIN")
    living = tuple(sorted(pid for pid in state.players if pid != dead))
    for pid, memory in memories.items():
        rows = [
            (row.tick, row.payload["room"], tuple(row.payload["player_ids"]))
            for row in memory.episodic.recent(since_tick=0)
        ]
        assert rows == ([] if pid == dead else [(14, "ADMIN", living)]), pid
    ended = AgentMemory()
    fold_public_regroup(
        {"p-1": ended}, state=replace(state, phase="GAME_OVER"), room="ADMIN"
    )
    assert ended.episodic.recent(since_tick=0) == ()


# --------------------------------------------------------------------------- #
# A runner of the game's own, and an agent without a memory                    #
# --------------------------------------------------------------------------- #


class _ButtonAgent:
    """Not a tactical agent: presses the button once, at ``press_tick``, then waits."""

    def __init__(self, player_id: str, *, press_tick: int) -> None:
        self.player_id = player_id
        self.press_tick = press_tick

    def decide(self, packet: Any, public_map: Any) -> Any:
        from pydantic import TypeAdapter

        from observation.action_intent import ActionIntent

        kind = "emergency" if packet.tick == self.press_tick else "wait"
        return TypeAdapter(ActionIntent).validate_python(
            {"actor": self.player_id, "type": kind, "payload": {}}
        )


class _SkippingRunner:
    """A runner of the game's own: every living player skips. Records its ticks."""

    def __init__(self) -> None:
        self.regroup_ticks: list[frozenset[int]] = []

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[str, Any],
        regroup_ticks: frozenset[int] = frozenset(),
    ) -> Any:
        from meetings.schemas import VoteBallot
        from orchestrator.game import MeetingArtifacts

        self.regroup_ticks.append(regroup_ticks)
        living = sorted(pid for pid, p in state.players.items() if p.alive)
        return MeetingArtifacts(
            result=MeetingResult(
                meeting_id=meeting_id,
                triggered_by=trigger.triggered_by,
                trigger_tick=trigger.trigger_tick,
                outcome="SKIPPED",
                ejected_player_id=None,
                ballots=tuple(
                    VoteBallot(
                        voter=pid,
                        target="SKIP",
                        confidence=0.5,
                        primary_reason_id=None,
                        considered_alternatives=(),
                        rationale_text="skip",
                    )
                    for pid in living
                ),
                transcript=MeetingTranscript(),
            ),
            llm_calls=(),
            prompt_versions={},
        )


class _OldRunner(_SkippingRunner):
    """A runner written before the regroup ticks existed."""

    async def run_meeting(  # type: ignore[override]
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[str, Any],
    ) -> Any:
        return await super().run_meeting(
            meeting_id=meeting_id, trigger=trigger, state=state, agents=agents
        )


def _button_game(
    runner: Any,
    *,
    config: RecordedExperimentConfig | None,
    game_map: Map | None = None,
    replay_path: Path | None = None,
) -> tuple[Any, dict[str, Any]]:
    from orchestrator.game import HeadlessGame, build_default_agent_factory
    from orchestrator.scheduler import TickScheduler

    tactical = build_default_agent_factory(experiment_config=config)
    presses = {"p-1": 0, "p-2": 2}
    built: dict[str, Any] = {}

    def _factory(player_id: str, role: str) -> Any:
        if player_id in presses:
            agent: Any = _ButtonAgent(player_id, press_tick=presses[player_id])
        else:
            agent = tactical(player_id, role)  # type: ignore[arg-type]
        built[player_id] = agent
        return agent

    game = HeadlessGame(
        seed=4,
        game_map=game_map if game_map is not None else load_canonical_map(),
        agent_factory=_factory,
        meeting_runner=runner,
        experiment_config=config,
        replay_path=replay_path,
        scheduler=TickScheduler(max_ticks=5),
        num_players=5,
        num_impostors=1,
        tasks_per_crewmate=1,
    )
    return game, built


def test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped() -> (
    None
):
    runner = _SkippingRunner()
    game, agents = _button_game(runner, config=RESET)
    game.run_unrecorded()
    assert runner.regroup_ticks == [frozenset(), frozenset({1})]
    for pid, agent in agents.items():
        if isinstance(agent, _ButtonAgent):
            continue
        rows = [
            row.tick
            for row in agent.memory.episodic.recent(since_tick=0)
            if row.type == "public_regroup"
        ]
        assert rows == [1, 3], pid


@pytest.mark.parametrize(
    "config",
    [None, RecordedExperimentConfig(redistribution_policy="least_remaining_work")],
    ids=["no-settings", "other-settings"],
)
def test_outside_the_reset_a_runner_written_before_the_ticks_runs_unchanged(
    config: RecordedExperimentConfig | None,
) -> None:
    # Recorded settings without the reset hand the runner no regroup ticks.
    game, _ = _button_game(_OldRunner(), config=config)
    game.run_unrecorded()


def test_a_runner_written_before_the_ticks_is_refused_in_a_regroup_game() -> None:
    game, _ = _button_game(_OldRunner(), config=RESET)
    with pytest.raises(TypeError, match="regroup_ticks"):
        game.run_unrecorded()


class _EjectingRunner(_SkippingRunner):
    """Ejects the only impostor at the first meeting, so that meeting ends the game.

    Every living player votes the impostor with full confidence, so the ballots
    tally to the ejection the result states and the meeting can be recorded.
    """

    async def run_meeting(
        self,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[str, Any],
        regroup_ticks: frozenset[int] = frozenset(),
    ) -> Any:
        artifacts = await super().run_meeting(
            meeting_id=meeting_id,
            trigger=trigger,
            state=state,
            agents=agents,
            regroup_ticks=regroup_ticks,
        )
        impostor = next(
            pid
            for pid, player in sorted(state.players.items())
            if player.alive and player.role == "IMPOSTOR"
        )
        ballots = tuple(
            ballot.model_copy(update={"target": impostor, "confidence": 1.0})
            for ballot in artifacts.result.ballots
        )
        return replace(
            artifacts,
            result=artifacts.result.model_copy(
                update={
                    "outcome": "EJECTED",
                    "ejected_player_id": impostor,
                    "ballots": ballots,
                }
            ),
        )


def test_a_meeting_that_ends_the_game_under_the_reset_resumes_nothing() -> None:
    # The meeting's own game-over event must reach the loop's end: the resume
    # composition regroups only when play resumes.
    runner = _EjectingRunner()
    game, _ = _button_game(runner, config=RESET)
    result = game.run_unrecorded()
    assert result.final_state.phase == "GAME_OVER"
    assert result.outcome == "CREWMATES"
    assert runner.regroup_ticks == [frozenset()]


@pytest.mark.parametrize(
    "profile",
    [honesty_module._WALK_CONFIG, funnel_module._WALK_CONFIG],
    ids=["evidence-honesty", "funnel-instrument"],
)
def test_a_recorded_meeting_that_ends_the_game_walks_to_its_terminal_meeting(
    tmp_path: Path, profile: Any
) -> None:
    # The walk composes the resume before it stops at game over, so it must read
    # the phase the meeting left: a meeting that ends the game regroups nobody.
    path = tmp_path / "headless-seed-4.jsonl"
    game, _ = _button_game(_EjectingRunner(), config=RESET, replay_path=path)
    recorded = game.run()
    assert recorded.outcome == "CREWMATES"
    events = list(
        walk_replay(
            path,
            seed=4,
            game_map=load_canonical_map(),
            config=profile,
            num_players=5,
            num_impostors=1,
            tasks_per_crewmate=1,
        )
    )
    applied = [event for event in events if isinstance(event, MeetingApplied)]
    assert len(applied) == 1
    assert applied[0].state.phase == "GAME_OVER"
    assert [type(event) for event in applied[0].post_events][-1] is GameOverEvent
    complete = events[-1]
    assert isinstance(complete, WalkComplete)
    assert complete.terminal_tick == applied[0].entry.tick
    assert events[-2] is applied[0]


def _admin_meeting_map() -> Map:
    """The canonical map with its meeting room moved, so a hard-coded room shows."""

    canonical = load_canonical_map()
    moved = canonical.model_copy(
        update={"meeting": canonical.meeting.model_copy(update={"room": "ADMIN"})}
    )
    assert moved.meeting.room != canonical.meeting.room
    return moved


def test_the_live_notice_names_the_maps_meeting_room() -> None:
    game, agents = _button_game(
        _SkippingRunner(), config=RESET, game_map=_admin_meeting_map()
    )
    game.run_unrecorded()
    rooms = {
        row.payload["room"]
        for agent in agents.values()
        if not isinstance(agent, _ButtonAgent)
        for row in agent.memory.episodic.recent(since_tick=0)
        if row.type == "public_regroup"
    }
    assert rooms == {"ADMIN"}


def test_the_readers_name_the_maps_meeting_room(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tests._helpers.scripted_meeting as scripted

    game_map = _admin_meeting_map()
    monkeypatch.setattr(scripted, "load_canonical_map", lambda: game_map)
    directory = tmp_path / "9p2i"
    path = record_game(directory, seed=SEED, config=RESET)
    applied = [
        event
        for event in walk_replay(
            path,
            seed=SEED,
            game_map=game_map,
            config=honesty_module._WALK_CONFIG,
            **_ROSTER,
        )
        if isinstance(event, MeetingApplied) and event.state.phase == "PLAY"
    ]
    assert applied
    assert {event.regroup_room for event in applied} == {"ADMIN"}
    meetings = [
        row for row in read_all_entries(path) if isinstance(row, MeetingReplayEntry)
    ]
    assert len(meetings) >= 2
    from agents.memory import store

    notice = store._REGROUP_NOTICE.format(tick=meetings[0].tick + 1, room="ADMIN")
    loader = ReplayLoader(directory, game_map=game_map)
    for ballot in meetings[1].ballots:
        view = loader.get_meeting_memory(
            f"headless-seed-{SEED}", meetings[1].meeting_id, ballot.voter
        )
        assert notice in view.rendered_memory_text, ballot.voter


# =========================================================================== #
# 6. One recorded game, four readings                                         #
# =========================================================================== #

#: A fake 9p2i game whose three meetings all resume play.
SEED: Final[int] = 1000

#: The live-loop and reader sites, each withheld in turn below.
LIVE_SITES: Final[tuple[str, ...]] = (
    "live-run-ticks",
    "live-absorb-ticks",
    "live-resume",
    "live-notice",
)
READER_SITES: Final[tuple[str, ...]] = (
    "loader-ticks",
    "loader-resume",
    "loader-notice",
    "walk-ticks",
    "walk-resume",
    "walk-notice",
    "golden-ticks",
    "golden-resume",
    "golden-notice",
)


@dataclass(frozen=True)
class _Opening:
    """What the live agents held when one meeting opened."""

    meeting_id: str
    tick: int
    trigger: MeetingTrigger
    regroup_ticks: frozenset[int]
    dead_ids: tuple[str, ...]
    memories: Mapping[str, str]
    beliefs: Mapping[str, Mapping[str, float]]
    episodic: Mapping[str, tuple[tuple[object, ...], ...]]


@dataclass
class _Live:
    """One live game: its recording, every meeting opening and every absorb."""

    path: Path
    openings: list[_Opening] = field(default_factory=list)
    evidence: list[tuple[tuple[str, ...], ...]] = field(default_factory=list)
    dropped: list[tuple[tuple[str, int], ...]] = field(default_factory=list)
    public_rows: dict[str, int] = field(default_factory=dict)


def _episodic_rows(store: MemoryStore) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            event.tick,
            event.type,
            json.dumps(event.payload, sort_keys=True, default=list),
            event.provenance,
            event.observation_id,
        )
        for event in store.recent(since_tick=0)
    )


def _beliefs(memory: AgentMemory) -> dict[str, float]:
    return {
        subject: memory.beliefs.view(subject).suspicion
        for subject in sorted(memory.beliefs.known_players())
    }


def _evidence_key(evidence: Any) -> tuple[tuple[str, ...], ...]:
    return (
        tuple(evidence.accused),
        tuple(evidence.corroborated),
        tuple(evidence.contradicted),
    )


class _VouchingClient:
    """The fake provider, except the second turn of every meeting after the first.

    That turn vouches for the meeting's opener at the previous meeting's resume
    tick and says it saw the opener in the meeting room then: the shape the
    regroup window must empty. The resume tick is read off the trigger ticks the
    runner saw, never off the production derivation.
    """

    def __init__(self, live: _Live, *, meeting_room: str) -> None:
        self.fake = FakeProvider()
        self.live = live
        self.meeting_room = meeting_room
        self.turns: dict[str, int] = {}
        self.vouches = 0

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        response = await self.fake.complete(
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
            call_kind=call_kind,
            model=model,
            agent_id=agent_id,
        )
        if schema is not MeetingTurn or len(self.live.openings) < 2:
            return response
        opening, previous = self.live.openings[-1], self.live.openings[-2]
        index = self.turns.get(opening.meeting_id, 0)
        self.turns[opening.meeting_id] = index + 1
        if index != 1 or agent_id is None:
            return response
        opener = opening.trigger.triggered_by
        resume = previous.tick + 1
        self.vouches += 1
        text = MeetingTurn(
            turn_id="scripted",
            turn_index=index,
            speaker=agent_id,
            turn_kind="opt_in",
            reply_to=None,
            observations=(
                SawPlayerObservation(
                    type="saw_player",
                    tick=resume,
                    subject=opener,
                    room=self.meeting_room,
                ),
            ),
            claims=(
                CorroborationClaim(
                    type="corroboration",
                    supports=opener,
                    on_tick=resume,
                    reason="they stood beside me",
                ),
            ),
            free_text=f"I can vouch for {opener}.",
        ).model_dump_json()
        return response.model_copy(update={"text": text})


def _ignore_regroup(
    real: Callable[..., ResumeEvents],
) -> Callable[..., ResumeEvents]:
    def _compose(
        trigger_tick_events: Any, meeting_events: Any, *, regrouped: bool = False
    ) -> ResumeEvents:
        return real(trigger_tick_events, meeting_events)

    return _compose


def _record_live(directory: Path, *, withhold: str | None = None) -> _Live:
    """Record the vouching game from the declared config, snapshotting each opening."""

    live = _Live(path=directory / f"replay-seed-{SEED}.jsonl")
    real_run = DefaultMeetingRunner.run_meeting
    real_extract = extract_belief_evidence
    real_compose = compose_resume_events
    real_absorb = game_module._absorb_meeting_beliefs

    async def _run_meeting(
        self: DefaultMeetingRunner,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[str, Any],
        regroup_ticks: frozenset[int] = frozenset(),
    ) -> Any:
        living = sorted(pid for pid, player in state.players.items() if player.alive)
        live.openings.append(
            _Opening(
                meeting_id=meeting_id,
                tick=trigger.trigger_tick,
                trigger=trigger,
                regroup_ticks=regroup_ticks,
                dead_ids=tuple(
                    sorted(pid for pid, p in state.players.items() if not p.alive)
                ),
                memories={
                    pid: render_for_prompt(
                        agents[pid].memory, token_budget=DEFAULT_TOKEN_BUDGET
                    )
                    for pid in living
                },
                beliefs={pid: _beliefs(agents[pid].memory) for pid in living},
                episodic={
                    pid: _episodic_rows(agents[pid].memory.episodic) for pid in living
                },
            )
        )
        return await real_run(
            self,
            meeting_id=meeting_id,
            trigger=trigger,
            state=state,
            agents=agents,
            regroup_ticks=frozenset()
            if withhold == "live-run-ticks"
            else regroup_ticks,
        )

    def _extract(result: MeetingResult, **kwargs: Any) -> Any:
        evidence = real_extract(result, **kwargs)
        live.evidence.append(_evidence_key(evidence))
        return evidence

    def _compose(
        trigger_tick_events: Any, meeting_events: Any, *, regrouped: bool = False
    ) -> ResumeEvents:
        composed = real_compose(
            trigger_tick_events,
            meeting_events,
            regrouped=regrouped and withhold != "live-resume",
        )
        live.dropped.append(composed.dropped)
        return composed

    def _absorb(**kwargs: Any) -> None:
        kwargs["regroup_ticks"] = frozenset()
        real_absorb(**kwargs)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(DefaultMeetingRunner, "run_meeting", _run_meeting)
        patch.setattr(game_module, "extract_belief_evidence", _extract)
        patch.setattr(game_module, "compose_resume_events", _compose)
        if withhold == "live-absorb-ticks":
            patch.setattr(game_module, "_absorb_meeting_beliefs", _absorb)
        if withhold == "live-notice":
            patch.setattr(game_module, "fold_public_regroup", lambda *a, **k: None)
        client = _VouchingClient(live, meeting_room=load_canonical_map().meeting.room)
        record_game(directory, seed=SEED, config=RESET, client=client)
    assert client.vouches >= 2
    return live


def _withheld_reader(site: str, patch: pytest.MonkeyPatch) -> None:
    owner, _, part = site.partition("-")
    module = {"loader": loader_module, "walk": walk_module, "golden": golden}[owner]
    if part == "ticks":
        patch.setattr(module, "derive_regroup_ticks", lambda *a, **k: frozenset())
    elif part == "resume":
        patch.setattr(
            module, "compose_resume_events", _ignore_regroup(compose_resume_events)
        )
    else:
        patch.setattr(module, "regroup_room_for", lambda *a, **k: None)


def _honesty_reading(
    path: Path,
) -> tuple[dict[str, dict[str, tuple[tuple[object, ...], ...]]], list[Any]]:
    """The evidence-honesty walk's memories at each opening, and what it absorbed."""

    game_map = load_canonical_map()
    initial = seed_initial_state(seed=SEED, game_map=game_map, **_ROSTER)
    memories = {pid: MemoryStore() for pid in initial.players}
    composites = {pid: AgentMemory(episodic=store) for pid, store in memories.items()}
    openings: dict[str, dict[str, tuple[tuple[object, ...], ...]]] = {}
    absorbed: list[Any] = []
    real_extract = extract_belief_evidence

    def _extract(result: MeetingResult, **kwargs: Any) -> Any:
        evidence = real_extract(result, **kwargs)
        absorbed.append(_evidence_key(evidence))
        return evidence

    with (
        tempfile.TemporaryDirectory() as directory,
        pytest.MonkeyPatch.context() as patch,
    ):
        patch.setattr(honesty_module, "extract_belief_evidence", _extract)
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(directory) / "audit.jsonl"
        )
        try:
            for walk_event in read_recorded_settings(
                walk_replay(
                    path,
                    seed=SEED,
                    game_map=game_map,
                    config=honesty_module._WALK_CONFIG,
                    **_ROSTER,
                ),
                reader="the evidence-honesty walk",
                reads=honesty_module.HONESTY_READS,
            ):
                if isinstance(walk_event, TickOpened):
                    honesty_module._perceive_tick(
                        walk_event, service=service, memories=memories
                    )
                elif isinstance(walk_event, MeetingOpened):
                    openings[walk_event.entry.meeting_id] = {
                        pid: _episodic_rows(memories[pid])
                        for pid, player in sorted(walk_event.state.players.items())
                        if player.alive
                    }
                elif isinstance(walk_event, MeetingApplied):
                    honesty_module._fold_meeting_into_memories(
                        walk_event, composites=composites
                    )
        finally:
            service.close()
    return openings, absorbed


def _disagreements(live: _Live) -> list[str]:
    """Every place the four readings of ``live``'s recording disagree with it."""

    problems: list[str] = []
    game_id = f"headless-seed-{SEED}"
    loader = ReplayLoader(live.path.parent)
    for opening in live.openings:
        for pid, text in opening.memories.items():
            view = loader.get_meeting_memory(game_id, opening.meeting_id, pid)
            if view.rendered_memory_text != text:
                problems.append(f"loader memory {opening.meeting_id} {pid}")
            if {b.subject: b.suspicion for b in view.beliefs} != opening.beliefs[pid]:
                problems.append(f"loader beliefs {opening.meeting_id} {pid}")
    walk = golden.walk_directory(live.path.parent)
    if walk.meetings != len(live.openings):
        problems.append(f"golden meetings {walk.meetings}")
    problems.extend(
        f"golden prompt {prompt.meeting_id} {prompt.agent_id}"
        for prompt in walk.prompts
        if not prompt.reproduced
    )
    problems.extend(f"golden consumption {name}" for name in walk.miscounted_meetings)
    honesty_openings, honesty_absorbed = _honesty_reading(live.path)
    for opening in live.openings:
        if honesty_openings.get(opening.meeting_id) != dict(opening.episodic):
            problems.append(f"honesty memory {opening.meeting_id}")
    if honesty_absorbed != live.evidence:
        problems.append("honesty absorbed evidence")
    return problems


@pytest.fixture(scope="module")
def live_game(tmp_path_factory: pytest.TempPathFactory) -> _Live:
    return _record_live(tmp_path_factory.mktemp("live") / "9p2i")


def test_the_game_resumes_from_at_least_two_regroups(live_game: _Live) -> None:
    entries = read_all_entries(live_game.path)
    meetings = [row for row in entries if isinstance(row, MeetingReplayEntry)]
    assert len(meetings) == len(live_game.openings) >= 3
    # Every meeting before the last resumed play and so regrouped.
    assert all(row.outcome == "SKIPPED" for row in meetings), (
        "the fake provider ejects nobody"
    )
    assert len(live_game.openings[:-1]) >= 2
    assert sum(count for dropped in live_game.dropped for _, count in dropped) > 0


def test_each_meeting_receives_the_resume_tick_of_every_meeting_before_it(
    live_game: _Live,
) -> None:
    for index, opening in enumerate(live_game.openings):
        assert opening.regroup_ticks == frozenset(
            earlier.tick + 1 for earlier in live_game.openings[:index]
        )


def test_the_four_readings_agree_at_every_meeting_open(live_game: _Live) -> None:
    assert _disagreements(live_game) == []


@pytest.mark.parametrize("site", LIVE_SITES)
def test_withholding_the_window_or_the_resume_at_a_live_site_breaks_agreement(
    site: str, tmp_path: Path
) -> None:
    assert _disagreements(_record_live(tmp_path / "9p2i", withhold=site))


@pytest.mark.parametrize("site", READER_SITES)
def test_withholding_the_window_or_the_resume_at_a_reader_breaks_agreement(
    site: str, live_game: _Live, monkeypatch: pytest.MonkeyPatch
) -> None:
    _withheld_reader(site, monkeypatch)
    assert _disagreements(live_game)


def test_every_living_agent_holds_one_public_row_per_regroup(live_game: _Live) -> None:
    for index, opening in enumerate(live_game.openings):
        for pid, rows in opening.episodic.items():
            regroup_rows = [row for row in rows if row[1] == "public_regroup"]
            assert [row[0] for row in regroup_rows] == [
                earlier.tick + 1 for earlier in live_game.openings[:index]
            ], (opening.meeting_id, pid)


# =========================================================================== #
# 7. Openings: a button meeting beside an unreported corpse                   #
# =========================================================================== #


@pytest.fixture(scope="module")
def fake_game(tmp_path_factory: pytest.TempPathFactory) -> _Live:
    """The same seed with the fake provider alone: it keeps a button meeting."""

    directory = tmp_path_factory.mktemp("fake") / "9p2i"
    live = _Live(path=directory / f"replay-seed-{SEED}.jsonl")
    real_run = DefaultMeetingRunner.run_meeting
    real_compose = compose_resume_events

    async def _run_meeting(
        self: DefaultMeetingRunner,
        *,
        meeting_id: str,
        trigger: MeetingTrigger,
        state: WorldState,
        agents: Mapping[str, Any],
        regroup_ticks: frozenset[int] = frozenset(),
    ) -> Any:
        live.openings.append(
            _Opening(
                meeting_id=meeting_id,
                tick=trigger.trigger_tick,
                trigger=trigger,
                regroup_ticks=regroup_ticks,
                dead_ids=tuple(
                    sorted(pid for pid, p in state.players.items() if not p.alive)
                ),
                memories={},
                beliefs={},
                episodic={},
            )
        )
        return await real_run(
            self,
            meeting_id=meeting_id,
            trigger=trigger,
            state=state,
            agents=agents,
            regroup_ticks=regroup_ticks,
        )

    def _compose(
        trigger_tick_events: Any, meeting_events: Any, *, regrouped: bool = False
    ) -> ResumeEvents:
        composed = real_compose(
            trigger_tick_events, meeting_events, regrouped=regrouped
        )
        live.dropped.append(composed.dropped)
        return composed

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(DefaultMeetingRunner, "run_meeting", _run_meeting)
        patch.setattr(game_module, "compose_resume_events", _compose)
        record_game(directory, seed=SEED, config=RESET)
    return live


def _census(directory: Path) -> CensusInputs:
    return load_census_inputs(directory)


def test_a_button_meeting_under_the_reset_names_no_body_and_clears_the_corpse(
    fake_game: _Live,
) -> None:
    (game,) = _census(fake_game.path.parent).games
    button = [
        (index, meeting)
        for index, meeting in enumerate(game.meetings)
        if meeting.trigger_kind == "emergency"
        and any(discovered is None for _, discovered in meeting.bodies_at_open)
    ]
    assert button, "the fixture game holds a button meeting beside a corpse"
    index, meeting = button[0]
    opening = fake_game.openings[index]
    assert opening.trigger.kind == "emergency"
    assert opening.trigger.body_victim_id is None
    assert "body" not in opening.trigger.description
    assert meeting.bodies_after == frozenset()
    entries = read_all_entries(fake_game.path)
    recorded = [row for row in entries if isinstance(row, MeetingReplayEntry)][index]
    _assert_no_emergency_opening_body(
        trigger_kind="emergency",
        result=MeetingResult(
            meeting_id=recorded.meeting_id,
            triggered_by=recorded.triggered_by,
            trigger_tick=recorded.tick,
            outcome=recorded.outcome,
            ejected_player_id=recorded.ejected_player_id,
            ballots=tuple(recorded.ballots),
            transcript=recorded.transcript,
        ),
    )
    # The victims whose corpses the reset cleared are announced at the next
    # meeting, from the same dead roster the runner hands the manager.
    victims = {
        body.player_id
        for body in _bodies_at(fake_game.path, meeting.tick).values()
        if body.discovered_by is None
    }
    assert victims
    assert index + 1 < len(fake_game.openings)
    assert victims <= set(fake_game.openings[index + 1].dead_ids)


def _bodies_at(path: Path, tick: int) -> Mapping[str, BodyState]:
    """The engine's corpses when the meeting at ``tick`` opened."""

    game_map = load_canonical_map()
    for event in walk_replay(
        path,
        seed=SEED,
        game_map=game_map,
        config=honesty_module._WALK_CONFIG,
        **_ROSTER,
    ):
        if isinstance(event, MeetingOpened) and event.entry.tick == tick:
            return event.state.bodies
    raise AssertionError(f"no meeting at tick {tick}")


def test_the_manager_receives_the_dead_roster_the_runner_derives(
    fake_game: _Live, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # The runner hands the manager the dead roster it reads off the state: the
    # snapshots above read the same state, and the manager is handed that set.
    seen: list[tuple[str, ...]] = []
    real = MeetingManager.run

    async def _run(self: MeetingManager, **kwargs: Any) -> Any:
        seen.append(tuple(kwargs["dead_ids"]))
        return await real(self, **kwargs)

    monkeypatch.setattr(MeetingManager, "run", _run)
    record_game(tmp_path / "9p2i", seed=SEED, config=RESET)
    assert seen == [opening.dead_ids for opening in fake_game.openings]


# =========================================================================== #
# 8. The census, end to end                                                   #
# =========================================================================== #

_ZERO_BY_CONSTRUCTION: Final[tuple[str, ...]] = (
    "stale_report_meetings",
    "play_resumes_with_impostor_in_vent",
    "play_resumes_with_corpse",
    "kills_in_grace_window_after_regroup",
)


def _census_section(
    directory: Path, load: Callable[[Path], CensusInputs] | None = None
) -> Any:
    raw = (
        publish_gameplay_census.set_dir_json(directory)
        if load is None
        else publish_gameplay_census.set_dir_json(directory, load=load)
    )
    return json.loads(raw)


def test_the_census_reads_zero_where_the_reset_forces_it(fake_game: _Live) -> None:
    cells = _census_section(fake_game.path.parent)["cells"]
    for key in _ZERO_BY_CONSTRUCTION:
        assert cells[key]["numerator"] == 0, key
        assert cells[key]["denominator"] > 0, key
    for key in ("trips_closed_by_regroup", "sabotage_active_at_regroup"):
        assert cells[key]["denominator"] > 0, key


def test_the_census_discards_what_the_resume_helper_dropped(fake_game: _Live) -> None:
    table = _census_section(fake_game.path.parent)["tables"][
        "trigger_tick_events_dropped_by_regroup"
    ]
    helper: dict[str, int] = {}
    for dropped in fake_game.dropped:
        for kind, count in dropped:
            helper[kind] = helper.get(kind, 0) + count
    assert sum(helper.values()) > 0
    assert table["counts"] == helper


def _regroup_game(inputs: CensusInputs) -> tuple[Any, int]:
    (game,) = inputs.games
    first = next(index for index, m in enumerate(game.meetings) if m.regrouped)
    return game, first


def _with_kill_at(inputs: CensusInputs, tick: int) -> CensusInputs:
    """The carrier with one kill after the first regroup moved to ``tick``."""

    game, first = _regroup_game(inputs)
    meeting = game.meetings[first]
    next_tick = game.meetings[first + 1].tick
    index = next(
        position
        for position, kill in enumerate(game.kills)
        if meeting.tick < kill.tick <= next_tick
    )
    kills = list(game.kills)
    kills[index] = replace(kills[index], tick=tick)
    return replace(inputs, games=(replace(game, kills=tuple(kills)),))


def _carrier(inputs: CensusInputs) -> Callable[[Path], CensusInputs]:
    """A census loader that hands the fold ``inputs`` whatever directory it names."""

    def _load(_directory: Path) -> CensusInputs:
        return inputs

    return _load


def test_the_census_grace_window_is_the_engines(fake_game: _Live) -> None:
    directory = fake_game.path.parent
    inputs = _census(directory)
    game, first = _regroup_game(inputs)
    meeting_tick = game.meetings[first].tick
    cooldown = load_canonical_map().kill_cooldown_ticks
    assert inputs.kill_cooldown_ticks == cooldown
    for offset in range(1, cooldown + 3):
        perturbed = _with_kill_at(inputs, meeting_tick + offset)
        if offset <= cooldown:
            with pytest.raises(GameplayCensusConformanceError, match="grace window"):
                _census_section(directory, load=_carrier(perturbed))
        else:
            _census_section(directory, load=_carrier(perturbed))


def test_a_corpse_restored_at_a_resume_raises_the_breach(fake_game: _Live) -> None:
    directory = fake_game.path.parent
    inputs = _census(directory)
    game, first = _regroup_game(inputs)
    meetings = list(game.meetings)
    meetings[first] = replace(meetings[first], bodies_after=frozenset({"body-p-9-3"}))
    perturbed = replace(inputs, games=(replace(game, meetings=tuple(meetings)),))
    with pytest.raises(GameplayCensusConformanceError, match="corpse"):
        _census_section(directory, load=_carrier(perturbed))


def test_a_kill_witness_button_call_soon_after_a_regroup_is_counted(
    fake_game: _Live,
) -> None:
    # No development game (seeds 1000-1007) holds one, so the call is inserted:
    # the button meeting moves to the last tick of the button cooldown after the
    # regroup, the kills between the two meetings move to the tick before it --
    # past the grace window, which the reset keeps empty -- and the first of
    # them gains the button's opener as a witness.
    directory = fake_game.path.parent
    inputs = _census(directory)
    game, first = _regroup_game(inputs)
    meeting = game.meetings[first]
    button = game.meetings[first + 1]
    assert button.trigger_kind == "emergency"
    call_tick = meeting.tick + BUTTON_COOLDOWN_TICKS
    assert call_tick - 1 > meeting.tick + inputs.kill_cooldown_ticks
    between = [
        position
        for position, kill in enumerate(game.kills)
        if meeting.tick < kill.tick <= button.tick
    ]
    assert between
    kills = list(game.kills)
    for position in between:
        kills[position] = replace(kills[position], tick=call_tick - 1)
    kills[between[0]] = replace(
        kills[between[0]], witnesses=kills[between[0]].witnesses | {button.opener}
    )
    meetings = list(game.meetings)
    meetings[first + 1] = replace(button, tick=call_tick)
    perturbed = replace(
        inputs,
        games=(replace(game, kills=tuple(kills), meetings=tuple(meetings)),),
    )
    cell = _census_section(directory, load=_carrier(perturbed))["cells"][
        "kill_witness_button_calls_soon_after_regroup"
    ]
    assert (cell["numerator"], cell["denominator"]) == (1, 1)
    unperturbed = _census_section(directory)["cells"][
        "kill_witness_button_calls_soon_after_regroup"
    ]
    assert unperturbed["numerator"] == 0


# =========================================================================== #
# 8b. The version-3 policy rebuild                                            #
# =========================================================================== #

#: A version-3 recording's settings with the regroup reset; version 3 requires
#: evidence version 2, which ingests the regroup row too.
_V3_RESET: Final[RecordedExperimentConfig] = RecordedExperimentConfig(
    format_version=3, evidence_reasoning_version=2, meeting_reset="hub_with_grace"
)


def test_the_policy_rebuild_folds_the_meeting_with_its_regroup_ticks(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from orchestrator import policy_reconstruction

    game_map = load_canonical_map()
    initial = seed_initial_state(seed=SEED, game_map=game_map, **_ROSTER)
    service = ObservationService(
        game_map=game_map,
        audit_log_path=tmp_path / "audit.jsonl",
        temporal_observation_version=2,
    )
    rebuild = policy_reconstruction.PolicyReconstruction(
        initial_state=initial,
        game_map=game_map,
        experiment=_V3_RESET,
        service=service,
        testimony_shapes=False,
    )
    seen: list[frozenset[int]] = []

    def _spy(**kwargs: Any) -> None:
        seen.append(kwargs["regroup_ticks"])

    monkeypatch.setattr(policy_reconstruction, "_absorb_meeting_beliefs", _spy)
    resumed = replace(initial, tick=9)
    rebuild.complete_meeting(
        state=resumed,
        result=_skipped(resumed, "p-1"),
        emergency=True,
        regroup_ticks=frozenset({4}),
    )
    service.close()
    assert seen == [frozenset({4})]
    for memory in rebuild.memories.values():
        rows = [
            row
            for row in memory.episodic.recent(since_tick=0)
            if row.type == "public_regroup"
        ]
        assert [(row.tick, row.payload["room"]) for row in rows] == [
            (9, game_map.meeting.room)
        ]


class _RecordingRebuild:
    """Stands in for the version-3 policy rebuild, recording each meeting fold."""

    folds: list[frozenset[int]] = []

    def __init__(self, *, initial_state: WorldState, **_kwargs: Any) -> None:
        self.memories: dict[str, AgentMemory] = {}
        for pid in initial_state.players:
            memory = AgentMemory()
            memory.episodic.append(
                EpisodicEvent(
                    tick=0,
                    type="self_state",
                    payload={"room": "CAFETERIA", "role": "CREWMATE", "agent_id": pid},
                    provenance="observed",
                )
            )
            self.memories[pid] = memory

    def before_tick(self, **_kwargs: Any) -> dict[str, tuple[object, ...]]:
        return {}

    def after_tick(self, **_kwargs: Any) -> dict[str, tuple[object, ...]]:
        return {}

    def open_meeting(self, _state: WorldState) -> None:
        return None

    def complete_meeting(
        self, *, regroup_ticks: frozenset[int], **_kwargs: Any
    ) -> None:
        type(self).folds.append(regroup_ticks)


@pytest.mark.parametrize("reader", ["walk", "loader"])
def test_each_reader_hands_the_policy_rebuild_every_meetings_regroup_ticks(
    fake_game: _Live, monkeypatch: pytest.MonkeyPatch, reader: str
) -> None:
    # The rebuild runs only for a version-3 recording, which a fake game on the
    # default evidence path cannot be; the reader is handed version-3 settings
    # instead, and the stand-in records what each meeting fold receives.
    _RecordingRebuild.folds = []
    module = walk_module if reader == "walk" else loader_module
    monkeypatch.setattr(
        module, "recorded_experiment_config", lambda _entries: _V3_RESET
    )
    monkeypatch.setattr(module, "PolicyReconstruction", _RecordingRebuild)
    if reader == "walk":
        list(
            walk_replay(
                fake_game.path,
                seed=SEED,
                game_map=load_canonical_map(),
                config=replace(
                    honesty_module._WALK_CONFIG,
                    reconstruct_v3_policies=True,
                    threaded_layers=frozenset({"orchestrator", "tactical", "meeting"}),
                ),
                **_ROSTER,
            )
        )
    else:
        ReplayLoader(fake_game.path.parent).load_replay(f"headless-seed-{SEED}")
    assert _RecordingRebuild.folds == [
        opening.regroup_ticks for opening in fake_game.openings
    ]
    assert len(_RecordingRebuild.folds) >= 2 and _RecordingRebuild.folds[1]


# =========================================================================== #
# 9. The viewer's data layer                                                  #
# =========================================================================== #

#: A fake 9p2i game whose first meeting (a report) opens beside a second,
#: unreported corpse and resumes play.
CORPSE_SEED: Final[int] = 1001


def _first_resume_frame_bodies(directory: Path, seed: int) -> tuple[str, ...]:
    path = directory / f"replay-seed-{seed}.jsonl"
    meetings = [
        row for row in read_all_entries(path) if isinstance(row, MeetingReplayEntry)
    ]
    replay = ReplayLoader(directory).load_replay(f"headless-seed-{seed}")
    frame = next(tick for tick in replay.ticks if tick.tick == meetings[0].tick + 1)
    return tuple(body.body_id for body in frame.bodies)


def test_the_first_frame_after_a_regroup_shows_no_corpse(tmp_path: Path) -> None:
    reset = tmp_path / "reset" / "9p2i"
    preserve = tmp_path / "preserve" / "9p2i"
    record_game(reset, seed=CORPSE_SEED, config=RESET)
    record_game(preserve, seed=CORPSE_SEED, config=None)
    (game,) = load_census_inputs(reset).games
    first = game.meetings[0]
    unreported = [
        body
        for body, discovered in first.bodies_at_open
        if body != first.trigger_body and discovered is None
    ]
    assert unreported and first.phase_after == "PLAY"
    assert _first_resume_frame_bodies(reset, CORPSE_SEED) == ()
    assert set(unreported) <= set(_first_resume_frame_bodies(preserve, CORPSE_SEED))


# =========================================================================== #
# 10. The documents and the copy                                              #
# =========================================================================== #

_REPO: Final[Path] = Path(__file__).resolve().parents[2]
_CONTRACT: Final[Path] = _REPO / "docs" / "observation-contract.md"
_GLOSSARY: Final[Path] = _REPO / "docs" / "glossary.md"

#: How each engine event kind the resume helper keeps is named in prose.
_KIND_WORDS: Final[Mapping[str, str]] = {
    "KilledEvent": "kill",
    "VentEnteredEvent": "vent entr",
    "VentExitedEvent": "vent exit",
}


def _doc_section(text: str, heading: str) -> str:
    """The body under the heading that starts with ``heading``, to the next heading."""

    match = re.search(
        rf"^#+ {re.escape(heading)}[^\n]*\n(?P<body>.*?)(?=^#+ |\Z)",
        text,
        re.M | re.S | re.I,
    )
    assert match is not None, f"no heading {heading!r}"
    return match.group("body")


def _glossary_regroup_entry() -> str:
    return _doc_section(_GLOSSARY.read_text(encoding="utf-8"), "regroup (")


def _contract_resume_rule() -> str:
    body = _doc_section(_CONTRACT.read_text(encoding="utf-8"), "The regroup reset")
    (rule,) = [
        part for part in body.split("\n\n") if part.startswith("**The resume rule.**")
    ]
    return rule


def _documented(kept: tuple[type[object], ...]) -> list[str]:
    missing: list[str] = []
    contract = " ".join(_contract_resume_rule().lower().split())
    glossary = " ".join(_glossary_regroup_entry().lower().split())
    for cls in kept:
        word = _KIND_WORDS.get(cls.__name__)
        if word is None or word not in contract or word not in glossary:
            missing.append(cls.__name__)
    return missing


def test_the_contract_and_the_glossary_name_every_kept_event_kind() -> None:
    assert _documented(REGROUP_KEPT_EVENTS) == []
    assert "resume" in _contract_resume_rule().lower()


def test_a_kind_added_to_the_keep_set_without_the_documents_fails() -> None:
    assert _documented((*REGROUP_KEPT_EVENTS, MovedEvent)) == ["MovedEvent"]


#: The contract's body-handle paragraph as it read before the body-handle
#: setting existed: removal "only in temporal mode", with no setting named.
_PRE_HANDLE_PARAGRAPH: Final[str] = (
    "Public packet body handles are an unconditional boundary repair. Full "
    "model-facing removal is implemented only in temporal mode: **OFF opening "
    "descriptions still contain the internal body ID and can expose its encoded "
    "death tick.**"
)


def _body_handle_paragraph() -> str:
    text = _CONTRACT.read_text(encoding="utf-8")
    (paragraph,) = [
        part
        for part in text.split("\n\n")
        if part.startswith("Public packet body handles")
    ]
    return " ".join(paragraph.split())


def _body_handle_problems(paragraph: str) -> list[str]:
    """What the paragraph fails to say about the recorded body-handle setting."""

    from observation.body_ids import public_body_id

    setting = "report_body_handle_version"
    assert setting in RecordedExperimentConfig.model_fields
    problems: list[str] = []
    if f"`{setting} = 1`" not in paragraph:
        problems.append("names no body-handle setting")
    if f"`{public_body_id('{victim_id}')}`" not in paragraph:
        problems.append("names no public handle")
    if "only in temporal mode" in paragraph:
        problems.append("still says only temporal mode removes the id")
    if "With neither" not in paragraph:
        problems.append("drops the default path's exposure")
    return problems


def test_the_contract_names_the_recorded_body_handle_setting() -> None:
    assert _body_handle_problems(_body_handle_paragraph()) == []


def test_the_paragraph_before_the_setting_fails_the_body_handle_check() -> None:
    assert _body_handle_problems(_PRE_HANDLE_PARAGRAPH) == [
        "names no body-handle setting",
        "names no public handle",
        "still says only temporal mode removes the id",
        "drops the default path's exposure",
    ]


def test_the_glossary_says_what_moves_what_clears_and_what_survives() -> None:
    entry = _glossary_regroup_entry().lower()
    for fact in (
        "meeting room",
        "corpse",
        "vent",
        "cooldown",
        "task",
        "button",
        "sabotage",
    ):
        assert fact in entry, fact


#: Task, audit and card identifiers, and threshold arithmetic.
_IDENTIFIER: Final[re.Pattern[str]] = re.compile(
    r"\b(?:Task \d|audit[- ]\d|phase[- ]\d|B[0-9]\b|R\d{1,2}\b|A-\d)"
    r"|[0-9]+\s*[<>]=?|[<>]=?\s*[0-9]+|\d+\s*[+*/]\s*\d+",
    re.IGNORECASE,
)


def _copy_strings() -> tuple[str, ...]:
    from agents.memory import store

    return (
        store._REGROUP_NOTICE,
        store._REGROUP_GROUP_PREFIX,
        store._TRAIL_REGROUP_STEP,
        _glossary_regroup_entry(),
    )


def _copy_problems(strings: tuple[str, ...]) -> list[str]:
    return [text for text in strings if _IDENTIFIER.search(text)]


def test_the_new_copy_carries_no_identifier_and_no_arithmetic() -> None:
    assert _copy_problems(_copy_strings()) == []


@pytest.mark.parametrize("planted", ["see Task 13.5", "the B2 card", "tick < 4"])
def test_a_planted_identifier_fails_the_copy_scan(planted: str) -> None:
    strings = _copy_strings()
    assert _copy_problems((strings[0] + " " + planted, *strings[1:]))
