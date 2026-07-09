"""Tests for the observable-only crew option set (Task 15.16).

Pins the definition-of-done contract for :mod:`training.crew.options` and the
``build_action_mask`` emergency-intent canonicalization region this task owns
in ``training/env.py``:

* the button-room fixture the contract names: a crew emergency carrying the
  FSM's ``reason`` payload (``suspicion_accumulation`` / ``kill_witnessed``)
  validates as ``submission_legal`` under the mask — the 15.8 exact-equality
  gap (``eval/leak_test.py`` ``_IdleExploreAgent`` docstring) that today's
  ``tests/training/test_env.py`` emergency fixture cannot fail on, because it
  only round-trips the mask's own default-payload object;
* the menu mirrors the crew FSM ladder rung-for-rung (report / emergency /
  repair / task-continuation / hold) and adds the two audit options (buddy /
  patrol) keyed on co-presence + the agent's OWN quantized suspicion, never
  role;
* every enumerated option is submission-legal under the mask built from the
  same packet;
* the observable-only proof: a sweep over committed-corpus replays rebuilds
  the packets every crew agent actually saw, feeds them (plus the agent's own
  reconstructed memory — the enumeration's ENTIRE input surface) through the
  menu, and asserts totality + mask legality + the pinned feature shape.
"""

from __future__ import annotations

import tempfile
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Literal

import pytest
from pydantic import TypeAdapter

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import AgentMemory
from agents.perception import (
    EVENT_GLOBAL_STATUS,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_INFERRED,
    PROVENANCE_OBSERVED,
    ingest_packet,
)
from agents.tactical.crewmate_policy import (
    KILL_WITNESS_REASON,
    SUSPICION_ACCUMULATION_REASON,
    CrewmatePolicy,
)
from engine.actions import Action
from engine.entities import PlayerId
from engine.events import MeetingTriggeredEvent
from engine.tick import advance_tick
from engine.world import Map, WorldState, load_canonical_map
from meetings.schemas import MeetingResult
from observation.action_intent import (
    DoTaskIntent,
    EmergencyMeetingIntent,
    MoveIntent,
    RepairSabotageIntent,
    ReportBodyIntent,
    WaitIntent,
)
from observation.packet import (
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerView,
    SelfView,
)
from observation.public_map import PublicMapView, RoomId
from observation.service import ObservationService
from orchestrator.boundary import public_map_from_engine_map
from orchestrator.game import apply_meeting_result
from orchestrator.replay import MeetingReplayEntry, ReplayEntry, read_all_entries
from orchestrator.seeder import seed_initial_state
from training.crew.options import (
    CREW_OPTION_FEATURE_NAMES,
    CREW_OPTION_KINDS,
    CrewOption,
    crew_genome_length,
    enumerate_crew_options,
)
from training.env import build_action_mask

_ACTION_ADAPTER: TypeAdapter[Action] = TypeAdapter(Action)

# The committed 9p2i corpus preset (replays/ml_corpus/9p2i/MANIFEST.md).
_CORPUS_DIR = Path("replays/ml_corpus/9p2i")
_NUM_PLAYERS = 9
_NUM_IMPOSTORS = 2
_TASKS = 2

# --------------------------------------------------------------------------- #
# Fixture topology — the 4-room star map mirrored from test_bakeoff_methods,   #
# plus a line map whose button walk and task walk diverge (the star's hub      #
# makes every route's first hop CAFETERIA, so the suspicion-walk detection      #
# needs a topology where the two courses differ).                              #
# --------------------------------------------------------------------------- #


def _star_map() -> PublicMapView:
    return PublicMapView(
        map_id="test_map",
        room_ids=("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
        room_neighbors={
            "ADMIN": ("CAFETERIA",),
            "CAFETERIA": ("ADMIN", "ELECTRICAL", "MEDBAY"),
            "ELECTRICAL": ("CAFETERIA",),
            "MEDBAY": ("CAFETERIA",),
        },
        vent_graph={},
        vent_rooms={},
        task_locations={"swipe_card": "ADMIN", "wires_electrical": "ELECTRICAL"},
        spawn_room="CAFETERIA",
        meeting_room="CAFETERIA",
        emergency_button_room="CAFETERIA",
    )


def _line_map() -> PublicMapView:
    """A — B — C — D line: button at A, task at D, so the button walk (toward
    A) and the task walk (toward D) take opposite first hops from B/C."""

    return PublicMapView(
        map_id="line_map",
        room_ids=("A", "B", "C", "D"),
        room_neighbors={
            "A": ("B",),
            "B": ("A", "C"),
            "C": ("B", "D"),
            "D": ("C",),
        },
        vent_graph={},
        vent_rooms={},
        task_locations={"calibrate": "D"},
        spawn_room="A",
        meeting_room="A",
        emergency_button_room="A",
    )


def _self_state_event(
    *, tick: int, room: RoomId, pending_task_id: str | None
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SELF_STATE,
        payload={"room": room, "pending_task_id": pending_task_id},
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_player_event(
    *, tick: int, player_id: str, room: RoomId, action: str | None = None
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_PLAYER,
        payload={"player_id": player_id, "room": room, "action": action},
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_body_event(
    *, tick: int, body_id: str, room: RoomId, victim_id: str
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_BODY,
        payload={"body_id": body_id, "room": room, "victim_id": victim_id},
        provenance=PROVENANCE_OBSERVED,
    )


def _global_status_event(
    *,
    tick: int,
    sabotage_active: bool = False,
    sabotage_kind: str | None = None,
    sabotage_repair_rooms: tuple[RoomId, ...] = (),
    sabotage_is_gating: bool = False,
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_GLOBAL_STATUS,
        payload={
            "tasks_completed": 0,
            "tasks_total": 14,
            "task_completion_percent": 0.0,
            "sabotage_active": sabotage_active,
            "sabotage_kind": sabotage_kind,
            "sabotage_repair_rooms": list(sabotage_repair_rooms),
            "sabotage_is_gating": sabotage_is_gating,
        },
        provenance=PROVENANCE_INFERRED,
    )


def _memory(*events: EpisodicEvent) -> AgentMemory:
    store = MemoryStore()
    for event in events:
        store.append(event)
    return AgentMemory(episodic=store)


def _packet(
    *,
    tick: int,
    room: RoomId,
    agent_id: str = "p-1",
    role: Literal["CREWMATE", "IMPOSTOR"] = "CREWMATE",
    pending_task_id: str | None = None,
    in_vent: bool = False,
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
    sabotage_active: bool = False,
    sabotage_kind: str | None = None,
    sabotage_repair_rooms: tuple[RoomId, ...] = (),
    sabotage_is_gating: bool = False,
) -> ObservationPacket:
    """A synthetic packet whose observable surface matches the memory fixtures.

    The menu reads self facts (room / in_vent / pending_task_id) off the
    packet and body / witnessed-kill / sabotage facts off memory, so every
    fixture builds BOTH consistently — which is what makes every enumerated
    option submission-legal under the mask (the ``test_bakeoff_methods``
    fixture convention).
    """

    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,
            pending_task_id=pending_task_id,
            in_vent=in_vent,
        ),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=0,
            tasks_total=14,
            task_completion_percent=0.0,
            sabotage_active=sabotage_active,
            sabotage_kind=sabotage_kind,
            sabotage_repair_rooms=sabotage_repair_rooms,
            sabotage_is_gating=sabotage_is_gating,
        ),
        cooldown=None,
    )


def _wait_intent(actor: str = "p-1") -> WaitIntent:
    return WaitIntent(actor=actor, type="wait")


def _by_kind(options: tuple[CrewOption, ...]) -> dict[str, list[CrewOption]]:
    grouped: dict[str, list[CrewOption]] = {}
    for option in options:
        grouped.setdefault(option.kind, []).append(option)
    return grouped


# --------------------------------------------------------------------------- #
# 1. The genome/feature layout pins.                                           #
# --------------------------------------------------------------------------- #


def test_genome_length_is_feature_count_plus_bias() -> None:
    assert crew_genome_length() == len(CREW_OPTION_FEATURE_NAMES) + 1
    # The one-hot block leads the layout, in CREW_OPTION_KINDS order.
    assert CREW_OPTION_FEATURE_NAMES[: len(CREW_OPTION_KINDS)] == tuple(
        f"kind_{kind}" for kind in CREW_OPTION_KINDS
    )


# --------------------------------------------------------------------------- #
# 2. The button-room fixture — the 15.8 exact-equality gap this task closes.   #
#    (The existing test_env fixture only round-trips the mask's own            #
#    default-payload object, so it cannot fail on the reason-stamped press.)   #
# --------------------------------------------------------------------------- #


def _canonical_mask(
    packet: ObservationPacket, *, uses_remaining: int
) -> tuple[Map, object]:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    return game_map, build_action_mask(
        packet,
        public_map,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_remaining=uses_remaining,
    )


def test_fsm_reason_emergency_is_submission_legal_in_button_room() -> None:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    button_room = public_map.emergency_button_room
    packet = _packet(tick=5, room=button_room)
    mask = build_action_mask(
        packet,
        public_map,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_remaining=game_map.emergency.uses_per_player,
    )
    for reason in (SUSPICION_ACCUMULATION_REASON, KILL_WITNESS_REASON):
        press = EmergencyMeetingIntent.model_validate(
            {"type": "emergency", "actor": "p-1", "payload": {"reason": reason}}
        )
        assert mask.is_submission_legal(press), reason
        assert mask.is_engine_legal(press), reason
    # The default-payload object stays legal (the pre-fix fixture's shape).
    assert mask.is_submission_legal(
        EmergencyMeetingIntent(actor="p-1", type="emergency")
    )


def test_reason_emergency_stays_illegal_outside_button_room_and_when_spent() -> None:
    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    press = EmergencyMeetingIntent.model_validate(
        {
            "type": "emergency",
            "actor": "p-1",
            "payload": {"reason": SUSPICION_ACCUMULATION_REASON},
        }
    )
    other_room = sorted(
        room for room in public_map.room_ids if room != public_map.emergency_button_room
    )[0]
    wrong_room_mask = build_action_mask(
        _packet(tick=5, room=other_room),
        public_map,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_remaining=game_map.emergency.uses_per_player,
    )
    assert not wrong_room_mask.is_submission_legal(press)
    spent_mask = build_action_mask(
        _packet(tick=5, room=public_map.emergency_button_room),
        public_map,
        sabotage_kinds=tuple(sorted(game_map.sabotages)),
        emergency_uses_remaining=0,
    )
    assert not spent_mask.is_submission_legal(press)


# --------------------------------------------------------------------------- #
# 3. The menu mirrors the FSM ladder rung-for-rung.                            #
# --------------------------------------------------------------------------- #


def test_report_option_mirrors_fsm_interrupt() -> None:
    public_map = _star_map()
    memory = _memory(
        _self_state_event(tick=4, room="ADMIN", pending_task_id="swipe_card"),
        _saw_body_event(tick=4, body_id="b-2", room="ADMIN", victim_id="p-5"),
        _saw_body_event(tick=4, body_id="b-1", room="ADMIN", victim_id="p-6"),
    )
    packet = _packet(
        tick=4,
        room="ADMIN",
        pending_task_id="swipe_card",
        visible_bodies=(
            BodyView(id="b-2", room="ADMIN", victim_id="p-5"),
            BodyView(id="b-1", room="ADMIN", victim_id="p-6"),
        ),
    )
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    )
    (report,) = options["report"]
    assert isinstance(report.intent, ReportBodyIntent)
    # Alphabetically-first body, exactly the FSM's own tie-break.
    assert report.intent.payload.body_id == "b-1"
    assert report.intent == fsm_intent


def test_kill_witness_emergency_walks_then_presses_with_fsm_reason() -> None:
    public_map = _star_map()
    kill_event = _saw_player_event(
        tick=6, player_id="p-3", room="MEDBAY", action="kill"
    )
    memory = _memory(
        _self_state_event(tick=6, room="MEDBAY", pending_task_id=None), kill_event
    )
    packet = _packet(
        tick=6,
        room="MEDBAY",
        visible_players=(PlayerView(id="p-3", room="MEDBAY", action="kill"),),
    )
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    )
    (emergency,) = options["emergency"]
    # Away from the button: the option IS the FSM's one-hop button walk.
    assert emergency.intent == fsm_intent
    assert isinstance(emergency.intent, MoveIntent)
    assert emergency.intent.payload.to_room == "CAFETERIA"

    # In the button room the option is the press carrying the FSM's reason.
    kill_at_button = _saw_player_event(
        tick=7, player_id="p-3", room="CAFETERIA", action="kill"
    )
    memory_at_button = _memory(
        _self_state_event(tick=7, room="CAFETERIA", pending_task_id=None),
        kill_at_button,
    )
    packet_at_button = _packet(
        tick=7,
        room="CAFETERIA",
        visible_players=(PlayerView(id="p-3", room="CAFETERIA", action="kill"),),
    )
    fsm_press = CrewmatePolicy(agent_id="p-1").decide(
        memory_at_button.episodic, public_map
    )
    options_at_button = _by_kind(
        enumerate_crew_options(
            packet_at_button,
            public_map,
            memory_at_button,
            fsm_intent=fsm_press,
            emergency_uses_remaining=1,
        )
    )
    (press,) = options_at_button["emergency"]
    assert isinstance(press.intent, EmergencyMeetingIntent)
    assert press.intent.payload.reason == KILL_WITNESS_REASON
    assert press.intent == fsm_press

    # With the agent's one emergency use spent, the press is off the menu
    # (the mask's emergency-uses mirror) — the walk case above is unaffected.
    exhausted = _by_kind(
        enumerate_crew_options(
            packet_at_button,
            public_map,
            memory_at_button,
            fsm_intent=fsm_press,
            emergency_uses_remaining=0,
        )
    )
    assert "emergency" not in exhausted
    assert "hold" in exhausted


def test_suspicion_press_is_kept_verbatim() -> None:
    public_map = _star_map()
    memory = _memory(_self_state_event(tick=9, room="CAFETERIA", pending_task_id=None))
    packet = _packet(tick=9, room="CAFETERIA")
    fsm_press = EmergencyMeetingIntent.model_validate(
        {
            "type": "emergency",
            "actor": "p-1",
            "payload": {"reason": SUSPICION_ACCUMULATION_REASON},
        }
    )
    options = _by_kind(
        enumerate_crew_options(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_press,
            emergency_uses_remaining=1,
        )
    )
    (emergency,) = options["emergency"]
    assert emergency.intent == fsm_press
    assert isinstance(emergency.intent, EmergencyMeetingIntent)
    assert emergency.intent.payload.reason == SUSPICION_ACCUMULATION_REASON


def test_suspicion_button_walk_detected_by_ladder_reconstruction() -> None:
    public_map = _line_map()
    memory = _memory(_self_state_event(tick=3, room="C", pending_task_id="calibrate"))
    packet = _packet(tick=3, room="C", pending_task_id="calibrate")
    # The tracker-gated FSM walks toward the button (A): first hop is B, while
    # the task continuation's first hop is D — the courses diverge, so the
    # reconstruction attributes the move to the emergency course.
    button_walk = MoveIntent.model_validate(
        {"type": "move", "actor": "p-1", "payload": {"to_room": "B"}}
    )
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=button_walk)
    )
    (emergency,) = options["emergency"]
    assert emergency.intent == button_walk
    (continue_task,) = options["continue_task"]
    assert isinstance(continue_task.intent, MoveIntent)
    assert continue_task.intent.payload.to_room == "D"

    # Gate closed: the FSM continues to the task, and no emergency option is
    # materialized from a plain task walk.
    task_walk = MoveIntent.model_validate(
        {"type": "move", "actor": "p-1", "payload": {"to_room": "D"}}
    )
    gate_closed = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=task_walk)
    )
    assert "emergency" not in gate_closed

    # Ambiguous case: from B both courses' first hop is A (task at A too), so
    # no separate emergency option is materialized — the move is already on
    # the menu as the task continuation.
    ambiguous_map = PublicMapView(
        map_id="ambiguous",
        room_ids=("A", "B", "C", "D"),
        room_neighbors={
            "A": ("B",),
            "B": ("A", "C"),
            "C": ("B", "D"),
            "D": ("C",),
        },
        vent_graph={},
        vent_rooms={},
        task_locations={"calibrate": "A"},
        spawn_room="A",
        meeting_room="A",
        emergency_button_room="A",
    )
    memory_b = _memory(_self_state_event(tick=3, room="B", pending_task_id="calibrate"))
    packet_b = _packet(tick=3, room="B", pending_task_id="calibrate")
    toward_a = MoveIntent.model_validate(
        {"type": "move", "actor": "p-1", "payload": {"to_room": "A"}}
    )
    ambiguous = _by_kind(
        enumerate_crew_options(packet_b, ambiguous_map, memory_b, fsm_intent=toward_a)
    )
    assert "emergency" not in ambiguous
    assert ambiguous["continue_task"][0].intent == toward_a


def test_repair_option_and_gated_do_task() -> None:
    public_map = _star_map()
    sabotage = _global_status_event(
        tick=5,
        sabotage_active=True,
        sabotage_kind="reactor",
        sabotage_repair_rooms=("ELECTRICAL",),
        sabotage_is_gating=True,
    )
    # In the surfaced repair room: the option is the repair itself, and the
    # in-place do_task is dropped (engine-illegal while the sabotage gates).
    memory = _memory(
        _self_state_event(
            tick=5, room="ELECTRICAL", pending_task_id="wires_electrical"
        ),
        sabotage,
    )
    packet = _packet(
        tick=5,
        room="ELECTRICAL",
        pending_task_id="wires_electrical",
        sabotage_active=True,
        sabotage_kind="reactor",
        sabotage_repair_rooms=("ELECTRICAL",),
        sabotage_is_gating=True,
    )
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    )
    (repair,) = options["repair"]
    assert isinstance(repair.intent, RepairSabotageIntent)
    assert repair.intent.payload.kind == "reactor"
    assert repair.intent == fsm_intent
    assert "continue_task" not in options

    # Away from the repair room: the option is the FSM's diversion walk, and
    # the task WALK stays on the menu (repair-vs-task is the arbitration the
    # scorer owns; only the engine-illegal in-place do_task is dropped).
    memory_away = _memory(
        _self_state_event(tick=6, room="ADMIN", pending_task_id="swipe_card"),
        _global_status_event(
            tick=6,
            sabotage_active=True,
            sabotage_kind="reactor",
            sabotage_repair_rooms=("ELECTRICAL",),
            sabotage_is_gating=True,
        ),
    )
    packet_away = _packet(
        tick=6,
        room="ADMIN",
        pending_task_id="swipe_card",
        sabotage_active=True,
        sabotage_kind="reactor",
        sabotage_repair_rooms=("ELECTRICAL",),
        sabotage_is_gating=True,
    )
    fsm_away = CrewmatePolicy(agent_id="p-1").decide(memory_away.episodic, public_map)
    options_away = _by_kind(
        enumerate_crew_options(
            packet_away, public_map, memory_away, fsm_intent=fsm_away
        )
    )
    (repair_away,) = options_away["repair"]
    assert repair_away.intent == fsm_away
    assert isinstance(repair_away.intent, MoveIntent)
    # ADMIN is the task room, so the continuation was do_task — dropped; the
    # menu carries no continue_task here (repair / buddy / patrol / hold do).
    assert "continue_task" not in options_away


def test_continue_task_walk_do_task_and_hub_routing() -> None:
    public_map = _star_map()
    # In the task room: do_task.
    memory = _memory(
        _self_state_event(tick=3, room="ADMIN", pending_task_id="swipe_card")
    )
    packet = _packet(tick=3, room="ADMIN", pending_task_id="swipe_card")
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    )
    (continue_task,) = options["continue_task"]
    assert isinstance(continue_task.intent, DoTaskIntent)
    assert continue_task.intent == fsm_intent

    # No pending task, away from the hub: the FSM's hub-routing walk.
    memory_idle = _memory(_self_state_event(tick=4, room="ADMIN", pending_task_id=None))
    packet_idle = _packet(tick=4, room="ADMIN")
    fsm_idle = CrewmatePolicy(agent_id="p-1").decide(memory_idle.episodic, public_map)
    options_idle = _by_kind(
        enumerate_crew_options(
            packet_idle, public_map, memory_idle, fsm_intent=fsm_idle
        )
    )
    (hub_walk,) = options_idle["continue_task"]
    assert hub_walk.intent == fsm_idle
    assert isinstance(hub_walk.intent, MoveIntent)
    assert hub_walk.intent.payload.to_room == "CAFETERIA"

    # No pending task, AT the hub: the FSM waits — hold carries it, no
    # duplicate continue_task.
    memory_hub = _memory(
        _self_state_event(tick=5, room="CAFETERIA", pending_task_id=None)
    )
    packet_hub = _packet(tick=5, room="CAFETERIA")
    fsm_hub = CrewmatePolicy(agent_id="p-1").decide(memory_hub.episodic, public_map)
    options_hub = _by_kind(
        enumerate_crew_options(packet_hub, public_map, memory_hub, fsm_intent=fsm_hub)
    )
    assert "continue_task" not in options_hub
    (hold,) = options_hub["hold"]
    assert hold.intent == fsm_hub == _wait_intent()


# --------------------------------------------------------------------------- #
# 4. The two audit additions: buddy + patrol.                                   #
# --------------------------------------------------------------------------- #


def test_buddy_targets_largest_trusted_group_and_excludes_over_gate() -> None:
    public_map = _star_map()
    memory = _memory(
        _saw_player_event(tick=7, player_id="p-2", room="MEDBAY"),
        _saw_player_event(tick=7, player_id="p-3", room="MEDBAY"),
        _saw_player_event(tick=8, player_id="p-4", room="ELECTRICAL"),
        _saw_player_event(tick=8, player_id="p-9", room="MEDBAY"),
        _self_state_event(tick=8, room="ADMIN", pending_task_id=None),
    )
    # p-9 is OVER the eject gate — excluded from the trusted group, so MEDBAY
    # counts two trusted members (p-2, p-3), not three.
    memory.beliefs.seed_player("p-9", suspicion=0.9, trust=0.1)
    memory.beliefs.seed_player("p-2", suspicion=0.2, trust=0.8)
    packet = _packet(tick=8, room="ADMIN")
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    )
    (buddy,) = options["buddy"]
    assert buddy.target_id == "MEDBAY"
    assert isinstance(buddy.intent, MoveIntent)
    assert buddy.intent.payload.to_room == "CAFETERIA"  # first hop toward MEDBAY
    # Already with the group: buddy holds position (a wait).
    memory_with = _memory(
        _self_state_event(tick=9, room="MEDBAY", pending_task_id=None),
        _saw_player_event(tick=9, player_id="p-2", room="MEDBAY"),
    )
    packet_with = _packet(
        tick=9,
        room="MEDBAY",
        visible_players=(PlayerView(id="p-2", room="MEDBAY", action=None),),
    )
    fsm_with = CrewmatePolicy(agent_id="p-1").decide(memory_with.episodic, public_map)
    options_with = _by_kind(
        enumerate_crew_options(
            packet_with, public_map, memory_with, fsm_intent=fsm_with
        )
    )
    (buddy_with,) = options_with["buddy"]
    assert buddy_with.intent == _wait_intent()
    assert buddy_with.target_id == "MEDBAY"


def test_patrol_targets_most_suspected_and_needs_a_cue() -> None:
    public_map = _star_map()
    memory = _memory(
        _saw_player_event(tick=6, player_id="p-7", room="ELECTRICAL"),
        _saw_player_event(tick=7, player_id="p-8", room="MEDBAY"),
        _self_state_event(tick=8, room="ADMIN", pending_task_id=None),
    )
    memory.beliefs.seed_player("p-7", suspicion=0.8, trust=0.2)
    memory.beliefs.seed_player("p-8", suspicion=0.7, trust=0.3)
    packet = _packet(tick=8, room="ADMIN")
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    )
    (patrol,) = options["patrol"]
    assert patrol.target_id == "p-7"  # highest suspicion wins
    assert isinstance(patrol.intent, MoveIntent)

    # Nobody above the neutral 0.5 prior: there is no suspect to patrol.
    memory_neutral = _memory(
        _saw_player_event(tick=7, player_id="p-8", room="MEDBAY"),
        _self_state_event(tick=8, room="ADMIN", pending_task_id=None),
    )
    packet_neutral = _packet(tick=8, room="ADMIN")
    fsm_neutral = CrewmatePolicy(agent_id="p-1").decide(
        memory_neutral.episodic, public_map
    )
    options_neutral = _by_kind(
        enumerate_crew_options(
            packet_neutral, public_map, memory_neutral, fsm_intent=fsm_neutral
        )
    )
    assert "patrol" not in options_neutral


def test_presumed_dead_players_leave_buddy_and_patrol() -> None:
    public_map = _star_map()
    memory = _memory(
        _saw_player_event(tick=6, player_id="p-7", room="ELECTRICAL"),
        _saw_body_event(tick=7, body_id="b-1", room="MEDBAY", victim_id="p-7"),
        _self_state_event(tick=8, room="ADMIN", pending_task_id=None),
    )
    memory.beliefs.seed_player("p-7", suspicion=0.9, trust=0.1)
    # The body is NOT in the agent's own room, so no report interrupt fires —
    # but the victim is presumed dead and leaves the patrol candidate pool.
    packet = _packet(tick=8, room="ADMIN")
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = _by_kind(
        enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    )
    assert "patrol" not in options
    assert "buddy" not in options


def test_hold_is_always_on_the_menu() -> None:
    public_map = _star_map()
    memory = _memory(_self_state_event(tick=2, room="ADMIN", pending_task_id=None))
    packet = _packet(tick=2, room="ADMIN")
    fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
    options = enumerate_crew_options(packet, public_map, memory, fsm_intent=fsm_intent)
    holds = [option for option in options if option.kind == "hold"]
    assert len(holds) == 1
    assert holds[0].intent == _wait_intent()


# --------------------------------------------------------------------------- #
# 5. Fail-loud guards.                                                          #
# --------------------------------------------------------------------------- #


def test_menu_raises_on_empty_memory_impostor_and_vented_states() -> None:
    public_map = _star_map()
    packet = _packet(tick=2, room="ADMIN")
    with pytest.raises(ValueError, match="at least one episodic event"):
        enumerate_crew_options(
            packet, public_map, AgentMemory(), fsm_intent=_wait_intent()
        )
    memory = _memory(_self_state_event(tick=2, room="ADMIN", pending_task_id=None))
    impostor_packet = _packet(tick=2, room="ADMIN", role="IMPOSTOR")
    with pytest.raises(ValueError, match="crew-only"):
        enumerate_crew_options(
            impostor_packet, public_map, memory, fsm_intent=_wait_intent()
        )
    vented_packet = _packet(tick=2, room="ADMIN", in_vent=True)
    with pytest.raises(ValueError, match="in-vent"):
        enumerate_crew_options(
            vented_packet, public_map, memory, fsm_intent=_wait_intent()
        )


# --------------------------------------------------------------------------- #
# 6. Every enumerated option is submission-legal + feature vectors well-formed.#
# --------------------------------------------------------------------------- #


def _fixture_scenarios() -> list[tuple[ObservationPacket, AgentMemory]]:
    """Representative fixture states spanning every option kind."""

    scenarios: list[tuple[ObservationPacket, AgentMemory]] = []
    # Body + witnessed kill in the button room (report + emergency press).
    memory = _memory(
        _self_state_event(tick=7, room="CAFETERIA", pending_task_id="swipe_card"),
        _saw_body_event(tick=7, body_id="b-1", room="CAFETERIA", victim_id="p-6"),
        _saw_player_event(tick=7, player_id="p-3", room="CAFETERIA", action="kill"),
    )
    scenarios.append(
        (
            _packet(
                tick=7,
                room="CAFETERIA",
                pending_task_id="swipe_card",
                visible_players=(
                    PlayerView(id="p-3", room="CAFETERIA", action="kill"),
                ),
                visible_bodies=(BodyView(id="b-1", room="CAFETERIA", victim_id="p-6"),),
            ),
            memory,
        )
    )
    # Gating sabotage away from the repair room, task pending, suspect + group.
    memory_sabotage = _memory(
        _saw_player_event(tick=8, player_id="p-2", room="MEDBAY"),
        _saw_player_event(tick=8, player_id="p-7", room="MEDBAY"),
        _self_state_event(tick=9, room="ADMIN", pending_task_id="wires_electrical"),
        _global_status_event(
            tick=9,
            sabotage_active=True,
            sabotage_kind="reactor",
            sabotage_repair_rooms=("ELECTRICAL",),
            sabotage_is_gating=True,
        ),
    )
    memory_sabotage.beliefs.seed_player("p-7", suspicion=0.8, trust=0.2)
    scenarios.append(
        (
            _packet(
                tick=9,
                room="ADMIN",
                pending_task_id="wires_electrical",
                sabotage_active=True,
                sabotage_kind="reactor",
                sabotage_repair_rooms=("ELECTRICAL",),
                sabotage_is_gating=True,
            ),
            memory_sabotage,
        )
    )
    # Plain task routing with a trusted group elsewhere.
    memory_plain = _memory(
        _saw_player_event(tick=3, player_id="p-2", room="ELECTRICAL"),
        _self_state_event(tick=4, room="MEDBAY", pending_task_id="swipe_card"),
    )
    scenarios.append(
        (_packet(tick=4, room="MEDBAY", pending_task_id="swipe_card"), memory_plain)
    )
    return scenarios


def test_every_menu_option_is_submission_legal_on_fixtures() -> None:
    public_map = _star_map()
    for packet, memory in _fixture_scenarios():
        fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
        options = enumerate_crew_options(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=1,
        )
        mask = build_action_mask(
            packet,
            public_map,
            sabotage_kinds=("lights", "reactor"),
            emergency_uses_remaining=1,
        )
        for option in options:
            assert mask.is_submission_legal(option.intent), (
                option.kind,
                option.intent,
            )


def test_every_option_feature_vector_is_well_formed() -> None:
    public_map = _star_map()
    for packet, memory in _fixture_scenarios():
        fsm_intent = CrewmatePolicy(agent_id="p-1").decide(memory.episodic, public_map)
        for option in enumerate_crew_options(
            packet, public_map, memory, fsm_intent=fsm_intent
        ):
            assert len(option.features) == len(CREW_OPTION_FEATURE_NAMES)
            one_hots = option.features[: len(CREW_OPTION_KINDS)]
            assert sum(one_hots) == 1.0
            assert one_hots[CREW_OPTION_KINDS.index(option.kind)] == 1.0
            for name, value in zip(
                CREW_OPTION_FEATURE_NAMES, option.features, strict=True
            ):
                assert 0.0 <= value <= 1.0, (option.kind, name, value)


# --------------------------------------------------------------------------- #
# 7. The observable-only proof: sweep committed-corpus packets.                 #
# --------------------------------------------------------------------------- #


def _corpus_replays(count: int) -> list[Path]:
    replays = sorted(_CORPUS_DIR.glob("replay-seed-*.jsonl"))
    assert replays, f"no committed corpus replays under {_CORPUS_DIR}"
    return replays[:count]


def _walk_replay_packets(
    replay_path: Path, *, game_map: Map, seed: int
) -> Iterator[tuple[WorldState, Mapping[PlayerId, ObservationPacket]]]:
    """Re-walk a committed replay, yielding each PLAY state + per-agent packets.

    Mirrors ``tests/training/test_env.py``'s reconstruction walk (advance the
    recorded actions, apply the recorded meetings) while rebuilding the
    observation packets every living agent actually consumed.
    """

    entries = read_all_entries(replay_path)
    tick_entries = [entry for entry in entries if isinstance(entry, ReplayEntry)]
    meeting_by_tick: dict[int, MeetingReplayEntry] = {
        entry.tick: entry for entry in entries if isinstance(entry, MeetingReplayEntry)
    }
    state = seed_initial_state(
        seed=seed,
        game_map=game_map,
        num_players=_NUM_PLAYERS,
        num_impostors=_NUM_IMPOSTORS,
        tasks_per_crewmate=_TASKS,
    )
    with tempfile.TemporaryDirectory(prefix="ailibi-crew-sweep-") as tmp:
        service = ObservationService(
            game_map=game_map, audit_log_path=Path(tmp) / "audit.jsonl"
        )
        last_events: tuple[object, ...] = ()
        for entry in tick_entries:
            if state.phase == "PLAY":
                packets = {
                    pid: service.build_packet(
                        world_state=state,
                        agent_id=pid,
                        engine_events=last_events,  # type: ignore[arg-type]
                    )
                    for pid, player in state.players.items()
                    if player.alive
                }
                yield state, packets
            actions = [
                _ACTION_ADAPTER.validate_python(dict(raw)) for raw in entry.actions
            ]
            state, events = advance_tick(state, actions, game_map=game_map)
            if state.phase == "GAME_OVER":
                break
            if state.phase != "MEETING":
                last_events = tuple(events)
                continue
            meeting_entry = meeting_by_tick[entry.tick]
            body_id = next(
                (
                    event.body_id
                    for event in events
                    if isinstance(event, MeetingTriggeredEvent)
                ),
                None,
            )
            result = MeetingResult(
                meeting_id=meeting_entry.meeting_id,
                triggered_by=meeting_entry.triggered_by,
                trigger_tick=meeting_entry.tick,
                outcome=meeting_entry.outcome,
                ejected_player_id=meeting_entry.ejected_player_id,
                ballots=meeting_entry.ballots,
                contradictions=meeting_entry.contradictions,
                transcript=meeting_entry.transcript,
            )
            pre = tuple(events)
            state, post = apply_meeting_result(
                state, result, game_map=game_map, triggering_body_id=body_id
            )
            last_events = pre + tuple(post)
            if state.phase == "GAME_OVER":
                break
        service.close()


def test_corpus_sweep_menu_is_total_legal_and_observable_only() -> None:
    """Sweep committed-corpus packets through the menu (the observable-only DoD).

    The enumeration's ENTIRE input surface is ``(packet, public_map, memory,
    fsm_intent)`` where ``memory`` is the agent's OWN store rebuilt by
    ingesting exactly the packets that agent saw — so a passing sweep proves
    every per-option feature derives from the packet + the crew agent's own
    memory (nothing else exists to read), is TOTAL over every committed
    packet shape, and emits only submission-legal intents. The leak-side proof
    (the factory mode through the crew wrapper) lives in
    ``tests/training/test_crew_scorer.py``.
    """

    game_map = load_canonical_map()
    public_map = public_map_from_engine_map(game_map)
    sabotage_kinds = tuple(sorted(game_map.sabotages))
    uses = game_map.emergency.uses_per_player
    decisions = 0
    for replay_path in _corpus_replays(2):
        seed = int(replay_path.stem.removeprefix("replay-seed-"))
        memories: dict[PlayerId, AgentMemory] = {}
        crew_ids: set[PlayerId] | None = None
        for state, packets in _walk_replay_packets(
            replay_path, game_map=game_map, seed=seed
        ):
            if crew_ids is None:
                crew_ids = {
                    pid
                    for pid, player in state.players.items()
                    if player.role == "CREWMATE"
                }
            for pid, packet in sorted(packets.items()):
                memory = memories.setdefault(pid, AgentMemory())
                ingest_packet(
                    packet=packet, memory=memory.episodic, beliefs=memory.beliefs
                )
                if pid not in crew_ids:
                    continue
                fsm_intent = CrewmatePolicy(agent_id=pid).decide(
                    memory.episodic, public_map
                )
                options = enumerate_crew_options(
                    packet,
                    public_map,
                    memory,
                    fsm_intent=fsm_intent,
                    emergency_uses_remaining=uses,
                )
                mask = build_action_mask(
                    packet,
                    public_map,
                    sabotage_kinds=sabotage_kinds,
                    emergency_uses_remaining=uses,
                )
                kinds = [option.kind for option in options]
                assert "hold" in kinds
                for option in options:
                    assert len(option.features) == len(CREW_OPTION_FEATURE_NAMES)
                    assert all(0.0 <= value <= 1.0 for value in option.features)
                    assert mask.is_submission_legal(option.intent), (
                        seed,
                        packet.tick,
                        pid,
                        option.kind,
                        option.intent,
                    )
                decisions += 1
    assert decisions > 100, f"corpus sweep covered only {decisions} crew decisions"
