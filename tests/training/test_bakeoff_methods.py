"""Tests for the four bake-off entrants' train/eval loops (Task 15.15).

Each entrant trains at a tiny CI budget (a handful of generations / iterations
on 1-2 seeds) through the SAME :func:`training.bakeoff.harness.rollout_candidate`
runner, so these tests pin the seams that the full operator-executed runs ride:
the BC held-out agreement diagnostics + genome-shape match, the utility scorer's
FSM-faithful option menu (the bounded path's ``a test enumerates the options on
fixture states and pins the menu`` obligation), the policy-net ES warm-start
seam, the MAP-Elites archive coverage + binning, and the frozen-candidate
byte-determinism the 15.10 harness depends on.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import AgentMemory
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_GLOBAL_STATUS,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    PROVENANCE_INFERRED,
    PROVENANCE_OBSERVED,
)
from agents.tactical.features import TacticalFeatureEncoder
from engine.world import load_canonical_map
from observation.action_intent import (
    DoTaskIntent,
    EmergencyMeetingIntent,
    KillIntent,
    MoveIntent,
    RepairSabotageIntent,
    ReportBodyIntent,
    SabotageIntent,
    VentIntent,
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
from orchestrator.boundary import public_map_from_engine_map
from training.bakeoff import es
from training.bakeoff.bc import BcDaggerEntrant, bc_budget
from training.bakeoff.harness import (
    BAKEOFF_BASELINE_ID,
    BakeoffPolicy,
    TrainedCandidate,
    load_candidate_weights,
    rollout_candidate,
)
from training.bakeoff.map_elites import (
    BEHAVIOR_DESCRIPTOR_CONFIGURATION,
    DESCRIPTOR_AXES,
    REFEREE_TENSION_DESCRIPTOR_CONFIGURATION,
    TOTAL_CELLS,
    ArchiveCell,
    DescriptorConfiguration,
    MapElitesEntrant,
    bakeoff_substrate_sha,
    bin_descriptors,
    load_archive_cell_genomes,
    map_elites_budget,
    write_archive_cell_artifacts,
)
from training.bakeoff.policy_es import (
    KIND_SLOTS,
    PolicyEsConfig,
    PolicyEsEntrant,
    build_masked_mlp_policy,
    head_slot_for_intent,
    policy_es_budget,
    policy_genome_length,
)
from training.bakeoff.utility_es import (
    OPTION_FEATURE_NAMES,
    OPTION_KINDS,
    UtilityEsEntrant,
    enumerate_options,
    utility_es_budget,
    utility_genome_length,
)
from training.env import build_action_mask

import pytest

# --------------------------------------------------------------------------- #
# Shared map + genome-shape constants.                                         #
# --------------------------------------------------------------------------- #

_CANONICAL_PUBLIC_MAP: PublicMapView = public_map_from_engine_map(load_canonical_map())
_HIDDEN: int = 8
_POLICY_GENOME_LENGTH: int = policy_genome_length(
    _CANONICAL_PUBLIC_MAP, hidden=_HIDDEN, encoder=TacticalFeatureEncoder()
)


# --------------------------------------------------------------------------- #
# Fixture-state builders mirrored from tests/agents/test_impostor_policy.py.    #
# --------------------------------------------------------------------------- #

# The vent topology of the mirrored ``_public_map``: three mutually-connected
# vents (ADMIN / ELECTRICAL / MEDBAY) and a vent-free CAFETERIA.
_DEFAULT_VENT_ROOMS: Mapping[str, RoomId] = {
    "ADMIN_VENT": "ADMIN",
    "ELECTRICAL_VENT": "ELECTRICAL",
    "MEDBAY_VENT": "MEDBAY",
}
_DEFAULT_VENT_GRAPH: Mapping[str, tuple[str, ...]] = {
    "ADMIN_VENT": ("ELECTRICAL_VENT", "MEDBAY_VENT"),
    "ELECTRICAL_VENT": ("ADMIN_VENT", "MEDBAY_VENT"),
    "MEDBAY_VENT": ("ADMIN_VENT", "ELECTRICAL_VENT"),
}


def _public_map() -> PublicMapView:
    """The four-room fixture topology from ``test_impostor_policy`` (mirrored)."""

    return PublicMapView(
        map_id="test_map",
        room_ids=("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
        room_neighbors={
            "ADMIN": ("CAFETERIA",),
            "CAFETERIA": ("ADMIN", "ELECTRICAL", "MEDBAY"),
            "ELECTRICAL": ("CAFETERIA",),
            "MEDBAY": ("CAFETERIA",),
        },
        vent_graph=_DEFAULT_VENT_GRAPH,
        vent_rooms=_DEFAULT_VENT_ROOMS,
        task_locations={"swipe_card": "ADMIN", "wires_electrical": "ELECTRICAL"},
        spawn_room="CAFETERIA",
        meeting_room="CAFETERIA",
        emergency_button_room="CAFETERIA",
    )


def _cooldown_event(*, tick: int, cooldown: int) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_COOLDOWN_STATUS,
        payload={"cooldown": cooldown},
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_player_event(*, tick: int, player_id: str, room: RoomId) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_PLAYER,
        payload={"player_id": player_id, "room": room, "action": None},
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
    tasks_completed: int,
    tasks_total: int,
    sabotage_active: bool = False,
    sabotage_kind: str | None = None,
) -> EpisodicEvent:
    denominator = tasks_total if tasks_total else 1
    payload: dict[str, Any] = {
        "tasks_completed": tasks_completed,
        "tasks_total": tasks_total,
        "task_completion_percent": tasks_completed / denominator,
        "sabotage_active": sabotage_active,
        "sabotage_kind": sabotage_kind,
        "sabotage_repair_rooms": (),
        "sabotage_is_gating": False,
    }
    return EpisodicEvent(
        tick=tick,
        type=EVENT_GLOBAL_STATUS,
        payload=payload,
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
    agent_id: str = "imp",
    role: Literal["CREWMATE", "IMPOSTOR"] = "IMPOSTOR",
    pending_task_id: str | None = None,
    fellow_impostor_ids: tuple[str, ...] = (),
    in_vent: bool = False,
    cooldown: int | None = 0,
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
    tasks_completed: int = 0,
    tasks_total: int = 1,
    sabotage_active: bool = False,
    sabotage_kind: str | None = None,
) -> ObservationPacket:
    """A synthetic ObservationPacket whose observable surface matches the memory.

    The option menu reads self facts (room / in_vent / pending_task_id / cooldown
    / fellow_impostor_ids) off the packet and target/body/witness/sabotage facts
    off memory, so every fixture builds BOTH consistently: the visible players /
    bodies / cooldown here mirror the episodic events the FSM helpers scan, which
    is what makes every enumerated option submission-legal under the mask.
    """

    completion = tasks_completed / tasks_total if tasks_total else 0.0
    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,
            pending_task_id=pending_task_id,
            fellow_impostor_ids=fellow_impostor_ids,
            in_vent=in_vent,
        ),
        visible_players=visible_players,
        visible_bodies=visible_bodies,
        audible_events=(),
        global_state=GlobalView(
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            task_completion_percent=completion,
            sabotage_active=sabotage_active,
            sabotage_kind=sabotage_kind,
        ),
        cooldown=cooldown,
    )


# --------------------------------------------------------------------------- #
# Module-scope tiny-budget candidates (expensive artifacts shared per entrant). #
# --------------------------------------------------------------------------- #


@pytest.fixture(scope="module")
def bc_candidate() -> TrainedCandidate:
    """One CI-budget BC/DAgger champion, shared by the BC + warm-start tests."""

    return BcDaggerEntrant(config=bc_budget("ci")).train()


@pytest.fixture(scope="module")
def map_elites_run() -> tuple[MapElitesEntrant, TrainedCandidate]:
    """One CI-budget MAP-Elites entrant TRAINED once (Task 18.6).

    The trained entrant carries the frozen ``last_archive`` — the persisted
    behaviorally-diverse pool the 18.6 persistence tests round-trip — and the
    returned candidate carries the default-map config the byte-stability pin
    reads. Shared module-scope so the ci train (≈ 2 s) runs once for the suite.
    """

    entrant = MapElitesEntrant(config=map_elites_budget("ci"))
    candidate = entrant.train()
    return entrant, candidate


# --------------------------------------------------------------------------- #
# 1. BC/DAgger tiny-budget end-to-end.                                          #
# --------------------------------------------------------------------------- #


def test_bc_dagger_tiny_budget(bc_candidate: TrainedCandidate) -> None:
    assert bc_candidate.entrant == "bc-dagger"
    # The clone rides the shared MaskedMlpPolicy family, so its genome shape is an
    # exact warm-start match for the ES/QD entrants.
    assert len(bc_candidate.weights) == _POLICY_GENOME_LENGTH
    assert isinstance(bc_candidate.policy, BakeoffPolicy)

    metadata = bc_candidate.train_metadata
    agreement = metadata["heldout_intent_agreement"]
    assert isinstance(agreement, float)
    assert 0.0 <= agreement <= 1.0
    assert metadata["intent_agreement_bar"] == 0.90
    assert metadata["bar_met"] == (agreement >= 0.90)

    dataset_size = metadata["dataset_size"]
    assert isinstance(dataset_size, int)
    assert dataset_size > 0

    per_kind = metadata["per_kind_agreement"]
    assert isinstance(per_kind, dict)
    assert per_kind  # non-empty: the held-out game produced impostor decisions
    for stats in per_kind.values():
        assert isinstance(stats, dict)
        assert stats["hits"] <= stats["total"]


# --------------------------------------------------------------------------- #
# 2. head_slot_for_intent — the shared BC / policy-net label map.               #
# --------------------------------------------------------------------------- #


def test_head_slot_for_intent() -> None:
    rooms = sorted(_CANONICAL_PUBLIC_MAP.room_ids)
    room_index = {room: index for index, room in enumerate(rooms)}
    base = len(room_index)

    move = MoveIntent.model_validate(
        {"type": "move", "actor": "imp", "payload": {"to_room": rooms[3]}}
    )
    assert head_slot_for_intent(move, room_index=room_index) == 3

    kill = KillIntent.model_validate(
        {"type": "kill", "actor": "imp", "payload": {"target": "p-3"}}
    )
    vent = VentIntent.model_validate(
        {"type": "vent", "actor": "imp", "payload": {"vent_id": "v-1"}}
    )
    sabotage = SabotageIntent.model_validate(
        {"type": "sabotage", "actor": "imp", "payload": {"kind": "reactor"}}
    )
    do_task = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": "imp", "payload": {"task_id": "t-5"}}
    )
    report = ReportBodyIntent.model_validate(
        {"type": "report", "actor": "imp", "payload": {"body_id": "b-1"}}
    )
    repair = RepairSabotageIntent.model_validate(
        {"type": "repair_sabotage", "actor": "imp", "payload": {"kind": "reactor"}}
    )
    wait = WaitIntent(actor="imp", type="wait")

    assert head_slot_for_intent(kill, room_index=room_index) == base + KIND_SLOTS.index(
        "kill"
    )
    assert head_slot_for_intent(vent, room_index=room_index) == base + KIND_SLOTS.index(
        "vent"
    )
    assert head_slot_for_intent(
        sabotage, room_index=room_index
    ) == base + KIND_SLOTS.index("sabotage")
    assert head_slot_for_intent(
        do_task, room_index=room_index
    ) == base + KIND_SLOTS.index("do_task")
    assert head_slot_for_intent(
        report, room_index=room_index
    ) == base + KIND_SLOTS.index("report")
    assert head_slot_for_intent(
        repair, room_index=room_index
    ) == base + KIND_SLOTS.index("repair_sabotage")
    assert head_slot_for_intent(wait, room_index=room_index) == base + KIND_SLOTS.index(
        "wait"
    )

    # The emergency intent is structurally excluded from the head vocabulary.
    emergency = EmergencyMeetingIntent(actor="imp", type="emergency")
    assert head_slot_for_intent(emergency, room_index=room_index) is None


# --------------------------------------------------------------------------- #
# 3. THE OPTION-MENU PIN — enumerate the FSM option menu on fixture states.     #
# --------------------------------------------------------------------------- #


def _kinds(packet: ObservationPacket, memory: AgentMemory) -> list[str]:
    return [option.kind for option in enumerate_options(packet, _public_map(), memory)]


def test_menu_in_vent_is_exactly_the_connected_vent_exits() -> None:
    # (a) An in-vent impostor in ADMIN: the menu is EXACTLY the vent-exit options
    # over ADMIN_VENT's connected + vent-roomed pool, nothing else.
    packet = _packet(tick=10, room="ADMIN", in_vent=True, cooldown=0)
    memory = _memory(_cooldown_event(tick=10, cooldown=0))
    options = enumerate_options(packet, _public_map(), memory)
    assert {option.kind for option in options} == {"vent_exit"}
    vent_ids = {
        option.intent.payload.vent_id  # type: ignore[union-attr]
        for option in options
    }
    assert vent_ids == {"ELECTRICAL_VENT", "MEDBAY_VENT"}


def test_menu_body_in_own_room_no_witness_covers() -> None:
    # (b) A body in the impostor's own room with a vent and no witness: cover_vent
    # AND cover_move AND wait; no kill/stalk (no targets seeded).
    packet = _packet(
        tick=10,
        room="ADMIN",
        cooldown=0,
        visible_bodies=(BodyView(id="b-1", room="ADMIN", victim_id="victim"),),
    )
    memory = _memory(
        _cooldown_event(tick=10, cooldown=0),
        _saw_body_event(tick=10, body_id="b-1", room="ADMIN", victim_id="victim"),
    )
    kinds = _kinds(packet, memory)
    assert "cover_vent" in kinds
    assert "cover_move" in kinds
    assert "wait" in kinds
    assert "kill_now" not in kinds
    assert "stalk_toward" not in kinds


def test_menu_body_in_own_room_with_witness_suppresses_cover_vent() -> None:
    # (c) The same body but with a co-present non-teammate witness: cover_vent is
    # gone (venting in front of a witness is a tell), cover_move stays.
    packet = _packet(
        tick=10,
        room="ADMIN",
        cooldown=3,
        visible_players=(PlayerView(id="witness", room="ADMIN", action=None),),
        visible_bodies=(BodyView(id="b-1", room="ADMIN", victim_id="victim"),),
    )
    memory = _memory(
        _cooldown_event(tick=10, cooldown=3),
        _saw_body_event(tick=10, body_id="b-1", room="ADMIN", victim_id="victim"),
        _saw_player_event(tick=10, player_id="witness", room="ADMIN"),
    )
    kinds = _kinds(packet, memory)
    assert "cover_vent" not in kinds
    assert "cover_move" in kinds


def test_menu_kill_now_targets_colocated_player() -> None:
    # (d.1) Cooldown 0 with one fresh isolated co-located target: kill_now against
    # that player, no stalk.
    packet = _packet(
        tick=10,
        room="CAFETERIA",
        cooldown=0,
        visible_players=(PlayerView(id="victim", room="CAFETERIA", action=None),),
    )
    memory = _memory(
        _cooldown_event(tick=10, cooldown=0),
        _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
    )
    options = enumerate_options(packet, _public_map(), memory)
    kill_options = [option for option in options if option.kind == "kill_now"]
    assert len(kill_options) == 1
    assert kill_options[0].target_id == "victim"
    assert kill_options[0].intent.payload.target == "victim"  # type: ignore[union-attr]
    assert "stalk_toward" not in {option.kind for option in options}


def test_menu_stalk_toward_target_in_other_room() -> None:
    # (d.2) The same target seen in ANOTHER room: stalk_toward (one A*-hop move),
    # kill_now absent.
    packet = _packet(tick=10, room="CAFETERIA", cooldown=0)
    memory = _memory(
        _cooldown_event(tick=10, cooldown=0),
        _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
    )
    options = enumerate_options(packet, _public_map(), memory)
    stalk_options = [option for option in options if option.kind == "stalk_toward"]
    assert len(stalk_options) == 1
    stalk = stalk_options[0]
    assert stalk.target_id == "victim"
    assert isinstance(stalk.intent, MoveIntent)
    assert stalk.intent.payload.to_room == "MEDBAY"  # one hop toward the sighting
    assert "kill_now" not in {option.kind for option in options}


def test_menu_kill_now_suppressed_by_lower_id_fellow_deferral() -> None:
    # (d.3) The FSM's coordination INVARIANT is mirrored (Codex review on PR
    # #242): a LOWER-id fellow impostor co-located this tick takes the kill, so
    # no kill_now is generated for this impostor — while a HIGHER-id fellow in
    # the same state leaves the kill on the menu (the invariant is id-ordered,
    # not a witness preference).
    def menu_with_fellow(fellow_id: str) -> set[str]:
        packet = _packet(
            tick=10,
            room="CAFETERIA",
            cooldown=0,
            fellow_impostor_ids=(fellow_id,),
            visible_players=(
                PlayerView(id="victim", room="CAFETERIA", action=None),
                PlayerView(id=fellow_id, room="CAFETERIA", action=None),
            ),
        )
        memory = _memory(
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id=fellow_id, room="CAFETERIA"),
        )
        return {
            option.kind for option in enumerate_options(packet, _public_map(), memory)
        }

    # "a-fellow" < "imp" (the default actor id): the lower id acts, we defer.
    assert "kill_now" not in menu_with_fellow("a-fellow")
    # "z-fellow" > "imp": this impostor is the lower id, so the kill stays.
    assert "kill_now" in menu_with_fellow("z-fellow")


def test_menu_reposition_during_cooldown_toward_pending_task() -> None:
    # (e) Cooldown > 0 with a pending task in another room: reposition present,
    # no kill/stalk, wait present.
    packet = _packet(
        tick=10, room="CAFETERIA", cooldown=3, pending_task_id="swipe_card"
    )
    memory = _memory(_cooldown_event(tick=10, cooldown=3))
    options = enumerate_options(packet, _public_map(), memory)
    kinds = {option.kind for option in options}
    reposition = [option for option in options if option.kind == "reposition"]
    assert len(reposition) == 1
    assert isinstance(reposition[0].intent, MoveIntent)
    assert reposition[0].intent.payload.to_room == "ADMIN"
    assert "kill_now" not in kinds
    assert "stalk_toward" not in kinds
    assert "wait" in kinds


def test_menu_fake_task_in_own_room() -> None:
    # (f) The pending task is in the impostor's own room: fake_task (a do_task).
    packet = _packet(tick=10, room="ADMIN", cooldown=3, pending_task_id="swipe_card")
    memory = _memory(_cooldown_event(tick=10, cooldown=3))
    options = enumerate_options(packet, _public_map(), memory)
    fake = [option for option in options if option.kind == "fake_task"]
    assert len(fake) == 1
    assert isinstance(fake[0].intent, DoTaskIntent)
    assert fake[0].intent.payload.task_id == "swipe_card"


def test_menu_sabotage_gated_on_fsm_predicates() -> None:
    # (g) Near-task-win (12/14 == 6/7) with no active sabotage: sabotage present;
    # with a sabotage already active it is gone (the FSM's own trigger predicates).
    present_packet = _packet(
        tick=10,
        room="CAFETERIA",
        cooldown=3,
        tasks_completed=12,
        tasks_total=14,
        sabotage_active=False,
    )
    present_memory = _memory(
        _cooldown_event(tick=10, cooldown=3),
        _global_status_event(
            tick=10, tasks_completed=12, tasks_total=14, sabotage_active=False
        ),
    )
    assert "sabotage" in _kinds(present_packet, present_memory)

    absent_packet = _packet(
        tick=10,
        room="CAFETERIA",
        cooldown=3,
        tasks_completed=12,
        tasks_total=14,
        sabotage_active=True,
        sabotage_kind="reactor",
    )
    absent_memory = _memory(
        _cooldown_event(tick=10, cooldown=3),
        _global_status_event(
            tick=10,
            tasks_completed=12,
            tasks_total=14,
            sabotage_active=True,
            sabotage_kind="reactor",
        ),
    )
    assert "sabotage" not in _kinds(absent_packet, absent_memory)


def _all_menu_cases() -> list[tuple[str, ObservationPacket, AgentMemory]]:
    """Every option-menu fixture (label, packet, memory) for the sweep tests."""

    return [
        (
            "in_vent",
            _packet(tick=10, room="ADMIN", in_vent=True, cooldown=0),
            _memory(_cooldown_event(tick=10, cooldown=0)),
        ),
        (
            "body_no_witness",
            _packet(
                tick=10,
                room="ADMIN",
                cooldown=0,
                visible_bodies=(BodyView(id="b-1", room="ADMIN", victim_id="victim"),),
            ),
            _memory(
                _cooldown_event(tick=10, cooldown=0),
                _saw_body_event(
                    tick=10, body_id="b-1", room="ADMIN", victim_id="victim"
                ),
            ),
        ),
        (
            "body_with_witness",
            _packet(
                tick=10,
                room="ADMIN",
                cooldown=3,
                visible_players=(PlayerView(id="witness", room="ADMIN", action=None),),
                visible_bodies=(BodyView(id="b-1", room="ADMIN", victim_id="victim"),),
            ),
            _memory(
                _cooldown_event(tick=10, cooldown=3),
                _saw_body_event(
                    tick=10, body_id="b-1", room="ADMIN", victim_id="victim"
                ),
                _saw_player_event(tick=10, player_id="witness", room="ADMIN"),
            ),
        ),
        (
            "kill_now",
            _packet(
                tick=10,
                room="CAFETERIA",
                cooldown=0,
                visible_players=(
                    PlayerView(id="victim", room="CAFETERIA", action=None),
                ),
            ),
            _memory(
                _cooldown_event(tick=10, cooldown=0),
                _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
            ),
        ),
        (
            "stalk",
            _packet(tick=10, room="CAFETERIA", cooldown=0),
            _memory(
                _cooldown_event(tick=10, cooldown=0),
                _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
            ),
        ),
        (
            "reposition",
            _packet(
                tick=10, room="CAFETERIA", cooldown=3, pending_task_id="swipe_card"
            ),
            _memory(_cooldown_event(tick=10, cooldown=3)),
        ),
        (
            "fake_task",
            _packet(tick=10, room="ADMIN", cooldown=3, pending_task_id="swipe_card"),
            _memory(_cooldown_event(tick=10, cooldown=3)),
        ),
        (
            "sabotage",
            _packet(
                tick=10,
                room="CAFETERIA",
                cooldown=3,
                tasks_completed=12,
                tasks_total=14,
            ),
            _memory(
                _cooldown_event(tick=10, cooldown=3),
                _global_status_event(tick=10, tasks_completed=12, tasks_total=14),
            ),
        ),
    ]


def test_every_menu_option_is_submission_legal() -> None:
    # (h) The structurally-bounded claim: every option the menu ever materializes
    # is submission-legal under the mask on its own fixture state.
    public_map = _public_map()
    for label, packet, memory in _all_menu_cases():
        mask = build_action_mask(
            packet,
            public_map,
            sabotage_kinds=("reactor",),
            emergency_uses_remaining=0,
        )
        for option in enumerate_options(packet, public_map, memory):
            assert mask.is_submission_legal(option.intent), (
                f"{label}: option {option.kind} intent {option.intent!r} is not "
                "submission-legal"
            )


def test_every_menu_option_feature_vector_is_well_formed() -> None:
    # (i) Every option's feature tuple has the fixed OPTION_FEATURE_NAMES width and
    # a kind one-hot matching its own kind.
    public_map = _public_map()
    for _label, packet, memory in _all_menu_cases():
        for option in enumerate_options(packet, public_map, memory):
            assert len(option.features) == len(OPTION_FEATURE_NAMES)
            one_hot = option.features[: len(OPTION_KINDS)]
            assert sum(one_hot) == 1.0
            assert one_hot[OPTION_KINDS.index(option.kind)] == 1.0


# --------------------------------------------------------------------------- #
# 4. Utility-scorer + ES tiny-budget train.                                     #
# --------------------------------------------------------------------------- #


def test_utility_es_tiny_budget() -> None:
    candidate = UtilityEsEntrant(config=utility_es_budget("ci")).train()
    assert candidate.entrant == "utility-es"
    assert len(candidate.weights) == utility_genome_length()
    assert isinstance(candidate.policy, BakeoffPolicy)

    metadata = candidate.train_metadata
    assert isinstance(metadata["es_digest"], str)
    fitness_trace = metadata["fitness_trace"]
    assert isinstance(fitness_trace, list)
    assert fitness_trace  # one entry per generation plus the seeded genome


# --------------------------------------------------------------------------- #
# 5. Policy-net + ES tiny-budget — the BC-then-ES warm-start seam.              #
# --------------------------------------------------------------------------- #


def test_policy_es_without_warm_start() -> None:
    entrant = PolicyEsEntrant(config=policy_es_budget("ci"), warm_start=lambda: None)
    candidate = entrant.train()
    assert candidate.entrant == "policy-es"
    assert len(candidate.weights) == _POLICY_GENOME_LENGTH
    assert candidate.train_metadata["warm_start_used"] is False


def test_policy_es_with_bc_warm_start(bc_candidate: TrainedCandidate) -> None:
    warm_genome = bc_candidate.weights

    def warm_start() -> tuple[float, ...] | None:
        return warm_genome

    config: PolicyEsConfig = policy_es_budget("ci")
    candidate = PolicyEsEntrant(config=config, warm_start=warm_start).train()
    # The BC champion's genome shape aligns with the policy-net family, so the
    # warm start is accepted (the spike's BC-then-ES seam).
    assert candidate.train_metadata["warm_start_used"] is True


# --------------------------------------------------------------------------- #
# 6. MAP-Elites tiny-budget — archive coverage + the binning unit checks.       #
# --------------------------------------------------------------------------- #


def test_bin_descriptors_unit() -> None:
    assert bin_descriptors(0.0, 0.0, 0.0) == (0, 0, 0)
    assert bin_descriptors(1.0, 0.3, 3.0) == (1, 2, 2)
    assert bin_descriptors(7.0, 0.9, 10.0) == (5, 3, 3)


def test_map_elites_tiny_budget() -> None:
    candidate = MapElitesEntrant(config=map_elites_budget("ci")).train()
    assert candidate.entrant == "map-elites"

    metadata = candidate.train_metadata
    coverage = metadata["archive_coverage"]
    assert isinstance(coverage, float)
    assert 0.0 < coverage <= 1.0

    filled_cells = metadata["filled_cells"]
    assert isinstance(filled_cells, int)
    assert filled_cells >= 1
    assert metadata["total_cells"] == TOTAL_CELLS == 96

    champion_cell = metadata["champion_cell"]
    assert isinstance(champion_cell, list)
    assert len(champion_cell) == 3

    best_per_cell = metadata["best_per_cell"]
    assert isinstance(best_per_cell, list)
    assert best_per_cell
    for row in best_per_cell:
        assert isinstance(row, dict)
        assert isinstance(row["cell"], list)
        assert len(row["cell"]) == 3
        assert "fitness" in row
        assert "kill_count" in row
        assert "witness_exposure_rate" in row
        assert "vent_usage" in row


# --------------------------------------------------------------------------- #
# 6b. MAP-Elites cell persistence + referee-tension descriptors (Task 18.6).    #
# --------------------------------------------------------------------------- #


def test_descriptor_configuration_rejects_duplicate_axis() -> None:
    """A repeated axis fails loud at construction (Task 18.6).

    Three axes that are not DISTINCT would degenerate the grid (two coordinates
    bin the same value) and collapse the per-cell descriptor dict, so the
    ``__post_init__`` validation refuses it even though the len==3 and edge-key
    checks would both pass.
    """

    with pytest.raises(ValueError, match="must be distinct"):
        DescriptorConfiguration(
            name="dup",
            axes=("kill_count", "kill_count", "vent_usage"),
            edges={
                "kill_count": (0.5, 1.5),
                "vent_usage": (0.5, 2.5),
            },
        )


def test_map_elites_persisted_cells_round_trip(
    tmp_path: Path,
    map_elites_run: tuple[MapElitesEntrant, TrainedCandidate],
) -> None:
    """The freeze-persisted cell pool reloads bit-exactly (Task 18.6).

    The 18.6 freeze retains the whole illuminated archive (the pool the 18.20
    hall-of-fame seeds from), and :func:`write_archive_cell_artifacts` /
    :func:`load_archive_cell_genomes` round-trip it EXACTLY — bit-exact genomes
    via float-hex, exact fitness/descriptors via JSON repr round-trip.
    """

    entrant, _candidate = map_elites_run
    archive = entrant.last_archive
    assert archive is not None
    assert archive  # the freeze retained a non-empty behaviorally-diverse pool

    cells_dir = write_archive_cell_artifacts(
        archive, tmp_path, config=map_elites_budget("ci")
    )
    reloaded = load_archive_cell_genomes(tmp_path)
    assert reloaded == dict(archive)

    index = json.loads((cells_dir / "index.json").read_text())
    assert index["substrate"]["substrate_sha256"] == bakeoff_substrate_sha()

    # Every sidecar is exactly ``<sha256(weights bytes)>  weights.json`` — the
    # committed harness sidecar byte format.
    for i, j, k in archive:
        cell_dir = cells_dir / f"{i}-{j}-{k}"
        weights_bytes = (cell_dir / "weights.json").read_bytes()
        digest = hashlib.sha256(weights_bytes).hexdigest()
        sidecar = (cell_dir / "weights.json.sha256").read_text()
        assert sidecar == f"{digest}  weights.json\n"


def test_map_elites_cell_artifacts_are_byte_deterministic(
    tmp_path: Path,
    map_elites_run: tuple[MapElitesEntrant, TrainedCandidate],
) -> None:
    """Two freezes of the same archive produce byte-identical trees (Task 18.6).

    Sorted cell iteration + ``sort_keys`` JSON + float-hex weights make the
    persisted tree a pure function of the archive: every relative path and every
    file's bytes match across two independent writes.
    """

    entrant, _candidate = map_elites_run
    archive = entrant.last_archive
    assert archive is not None
    config = map_elites_budget("ci")

    first = write_archive_cell_artifacts(archive, tmp_path / "a", config=config)
    second = write_archive_cell_artifacts(archive, tmp_path / "b", config=config)
    first_files = sorted(p.relative_to(first) for p in first.rglob("*") if p.is_file())
    second_files = sorted(
        p.relative_to(second) for p in second.rglob("*") if p.is_file()
    )
    assert first_files == second_files
    assert first_files  # the tree is non-empty
    for rel in first_files:
        assert (first / rel).read_bytes() == (second / rel).read_bytes()


def test_map_elites_cell_loader_fails_loud(
    tmp_path: Path,
    map_elites_run: tuple[MapElitesEntrant, TrainedCandidate],
) -> None:
    """Every persisted-pool integrity violation fails loud (Task 18.6).

    A wrong adopted substrate sha (the 18.24 stale-seed fence), a corrupted
    cell's weights, and index/disk drift (a missing OR a stray cell dir) each
    raise :class:`ValueError` — drift is never papered over.
    """

    entrant, _candidate = map_elites_run
    archive = entrant.last_archive
    assert archive is not None
    victim = sorted(archive)[0]
    victim_name = f"{victim[0]}-{victim[1]}-{victim[2]}"

    # (a) A wrong expected substrate sha refuses the reload; the recorded one
    # passes, proving the fence trips only on a genuine mismatch.
    good_dir = tmp_path / "good"
    write_archive_cell_artifacts(archive, good_dir, config=map_elites_budget("ci"))
    load_archive_cell_genomes(good_dir, expected_substrate_sha=bakeoff_substrate_sha())
    with pytest.raises(ValueError, match="adopted substrate"):
        load_archive_cell_genomes(good_dir, expected_substrate_sha="deadbeef")

    # (b) Tamper the victim's weights with DIFFERENT but VALID float-hex JSON, so
    # the loader must reach the sha cross-check (not merely fail to parse the
    # bytes): a loader with the sha check deleted would happily reload this.
    corrupt_dir = tmp_path / "corrupt"
    cells = write_archive_cell_artifacts(
        archive, corrupt_dir, config=map_elites_budget("ci")
    )
    weights_file = cells / victim_name / "weights.json"
    tampered = json.loads(weights_file.read_text())
    tampered[0] = float(float.fromhex(tampered[0]) + 1.0).hex()
    weights_file.write_text(json.dumps(tampered) + "\n")
    with pytest.raises(ValueError, match="hashes to"):
        load_archive_cell_genomes(corrupt_dir)

    # (c) Deleting a cell dir the index still references fails loud.
    missing_dir = tmp_path / "missing"
    cells = write_archive_cell_artifacts(
        archive, missing_dir, config=map_elites_budget("ci")
    )
    shutil.rmtree(cells / victim_name)
    with pytest.raises(ValueError, match="do not match the index"):
        load_archive_cell_genomes(missing_dir)

    # (d) A stray cell dir the index does NOT list fails loud too.
    stray_dir = tmp_path / "stray"
    cells = write_archive_cell_artifacts(
        archive, stray_dir, config=map_elites_budget("ci")
    )
    (cells / "9-9-9").mkdir()
    with pytest.raises(ValueError, match="do not match the index"):
        load_archive_cell_genomes(stray_dir)


def test_map_elites_edge_relabel_is_rejected(tmp_path: Path) -> None:
    """A same-axes-DIFFERENT-edges relabel is rejected on write AND load (18.6).

    The subtle mislabel Codex flagged: a configuration whose axes match but whose
    EDGES differ re-bins some cells to a DIFFERENT coordinate, yet the axis-key and
    per-component-range checks pass. The writer now re-bins every cell under the
    recorded edges and refuses when a coordinate does not reproduce; the loader
    rebuilds the recorded configuration and self-validates each index entry the
    same way, so a tampered edge block is caught on reload too. Uses a synthetic
    cell whose ``kill_count`` (0.55) provably straddles the behavior edge 0.5 and
    the shifted edge 0.6 — the all-zeros ci archive cannot re-bin under a
    positive-edge shift, so it cannot exercise this guard.
    """

    descriptors = {"kill_count": 0.55, "witness_exposure_rate": 0.0, "vent_usage": 0.0}
    cell_key = BEHAVIOR_DESCRIPTOR_CONFIGURATION.bin_values(descriptors)
    assert cell_key == (1, 0, 0)  # binned under the behavior edges
    archive = {
        cell_key: ArchiveCell(genome=(0.25, -0.5), fitness=1.0, descriptors=descriptors)
    }
    shifted = DescriptorConfiguration(
        name="behavior-shifted",
        axes=DESCRIPTOR_AXES,
        edges={
            "kill_count": (0.6, 1.6, 2.6, 3.6, 4.6),
            "witness_exposure_rate": (0.1, 0.3, 0.6),
            "vent_usage": (0.7, 2.7, 5.7),
        },
    )
    # Under the shifted edges kill_count 0.55 falls in bin 0, not 1.
    assert shifted.bin_values(descriptors) == (0, 0, 0)

    # (a) The writer refuses the shifted config (re-bin mismatch), before any I/O.
    with pytest.raises(ValueError, match="re-bins cell"):
        write_archive_cell_artifacts(
            archive,
            tmp_path / "shifted",
            config=map_elites_budget("ci"),
            descriptor_configuration=shifted,
        )

    # (b) An honestly-written tree, then a tampered index edge block, is caught on
    # reload: the recorded (1, 0, 0) entry re-bins to (0, 0, 0) under the shifted
    # kill_count edges.
    cells_dir = write_archive_cell_artifacts(
        archive,
        tmp_path / "tamper",
        config=map_elites_budget("ci"),
        descriptor_configuration=BEHAVIOR_DESCRIPTOR_CONFIGURATION,
    )
    index = json.loads((cells_dir / "index.json").read_text())
    index["descriptor_config"]["edges"]["kill_count"] = [0.6, 1.6, 2.6, 3.6, 4.6]
    (cells_dir / "index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n"
    )
    with pytest.raises(ValueError, match="re-bins to"):
        load_archive_cell_genomes(tmp_path / "tamper")


def test_map_elites_referee_tension_configuration_is_additive(tmp_path: Path) -> None:
    """The referee-tension map is a selectable, deterministic alternative (18.6).

    Selecting :data:`REFEREE_TENSION_DESCRIPTOR_CONFIGURATION` tessellates the
    archive over the three watchability-tension axes (never as fitness), records
    the config name + 64-cell shape, carries the tension descriptors in every
    best-per-cell row with ``impostor_win`` in [0, 1], and reproduces the champion
    + rows bit-for-bit on a second identical run. Its archive also persists +
    reloads bit-exactly under the tension configuration, and the writer REFUSES
    that archive when the configuration is omitted (the FIX-2 mislabel guard).
    """

    config = map_elites_budget("ci")
    entrant = MapElitesEntrant(
        config=config,
        descriptor_configuration=REFEREE_TENSION_DESCRIPTOR_CONFIGURATION,
    )
    candidate = entrant.train()

    assert candidate.config["descriptor_config"] == "referee-tension-v1"
    assert candidate.config["axes"] == [
        "witness_exposure_rate",
        "meeting_trigger_rate",
        "impostor_win",
    ]
    assert candidate.config["total_cells"] == 64

    best_per_cell = candidate.train_metadata["best_per_cell"]
    assert isinstance(best_per_cell, list)
    assert best_per_cell
    for row in best_per_cell:
        assert set(row) == {
            "cell",
            "fitness",
            "witness_exposure_rate",
            "meeting_trigger_rate",
            "impostor_win",
        }
        assert 0.0 <= row["impostor_win"] <= 1.0

    # A second identical run reproduces the champion genome + best_per_cell.
    again = MapElitesEntrant(
        config=map_elites_budget("ci"),
        descriptor_configuration=REFEREE_TENSION_DESCRIPTOR_CONFIGURATION,
    ).train()
    assert again.weights == candidate.weights
    assert again.train_metadata["best_per_cell"] == best_per_cell

    # The non-default persistence path round-trips bit-exactly under its own
    # configuration, and the index block records the tension name + 64-cell shape.
    tension_archive = entrant.last_archive
    assert tension_archive is not None
    cells_dir = write_archive_cell_artifacts(
        tension_archive,
        tmp_path / "tension",
        config=config,
        descriptor_configuration=REFEREE_TENSION_DESCRIPTOR_CONFIGURATION,
    )
    reloaded = load_archive_cell_genomes(tmp_path / "tension")
    assert reloaded == dict(tension_archive)
    index = json.loads((cells_dir / "index.json").read_text())
    assert index["descriptor_config"]["name"] == "referee-tension-v1"
    assert index["descriptor_config"]["total_cells"] == 64

    # FIX-2 regression pin: omitting descriptor_configuration would record a
    # behavior-v1 index block around tension-binned cells — the writer refuses it
    # BEFORE any file I/O rather than write an undetectable mislabel.
    with pytest.raises(ValueError, match="was binned on axes"):
        write_archive_cell_artifacts(
            tension_archive, tmp_path / "mislabel", config=config
        )


def test_map_elites_default_run_config_is_byte_stable(
    map_elites_run: tuple[MapElitesEntrant, TrainedCandidate],
) -> None:
    """The additive configuration did not move the committed default (18.6).

    The default ci candidate's config carries NO ``descriptor_config`` key and
    the exact committed axes / edge lists / 96-cell literal, and
    :meth:`DescriptorConfiguration.bin_values` under the behavior map agrees with
    the untouched public :func:`bin_descriptors` on the pinned probe triples.
    """

    _entrant, candidate = map_elites_run
    config = candidate.config
    assert "descriptor_config" not in config
    assert config["axes"] == ["kill_count", "witness_exposure_rate", "vent_usage"]
    assert config["edges"] == {
        "kill_count": [0.5, 1.5, 2.5, 3.5, 4.5],
        "witness_exposure_rate": [1e-9, 0.25, 0.5],
        "vent_usage": [0.5, 2.5, 5.5],
    }
    assert config["total_cells"] == TOTAL_CELLS == 96

    for kill_count, witness_exposure_rate, vent_usage in (
        (0.0, 0.0, 0.0),
        (1.0, 0.3, 3.0),
        (7.0, 0.9, 10.0),
    ):
        values = {
            "kill_count": kill_count,
            "witness_exposure_rate": witness_exposure_rate,
            "vent_usage": vent_usage,
        }
        assert BEHAVIOR_DESCRIPTOR_CONFIGURATION.bin_values(values) == bin_descriptors(
            kill_count, witness_exposure_rate, vent_usage
        )


def test_the_committed_map_elites_pool_is_current_and_structurally_untouched() -> None:
    """The pool's STAMP is current and its GENOMES are unchanged, asserted together.

    The MAP-Elites archive is SUBSTRATE-INDEPENDENT: the illumination runs fresh
    deterministic fake-provider rollouts off ``seed`` + the canonical map and never
    reads the corpus, so the cell genomes, the cell count and the champion do not
    move when the corpus is re-recorded. The provenance stamp in
    ``cells/index.json`` DOES move -- ``substrate.substrate_sha256`` is the sha of
    the corpus ``MANIFEST.md``, deliberately chosen (``bakeoff_substrate_sha``) as
    the thing that trips when a re-record lands.

    Between the baseline-7 record and the Task-21.17 re-ground this test was the
    INVERTED tripwire: it asserted the stamp was stale, precisely so a lone
    two-field edit could not quietly forge it green while the fits underneath
    stayed un-re-ground. The re-ground moved the stamp WITH the fits, so the
    assertion inverts — and the two halves stay asserted together, so a current
    stamp can never be read without the untouched structure beside it.
    """

    root = Path("training/artifacts/impostor/map-elites")
    archive = load_archive_cell_genomes(root)
    assert len(archive) == 30

    index = json.loads((root / "cells" / "index.json").read_text())
    assert index["filled_cells"] == 30
    # The pool declares the adopted baseline ...
    assert index["baseline_id"] == BAKEOFF_BASELINE_ID == "baseline-8"
    # ... and its stamp is the corpus now on disk.
    assert index["substrate"]["substrate_sha256"] == bakeoff_substrate_sha()
    assert index["substrate"]["corpus_manifest"] == "replays/ml_corpus/9p2i/MANIFEST.md"

    # The substrate-independent structure, unchanged across the re-record.
    champion_key, champion_cell = min(
        archive.items(), key=lambda item: (-item[1].fitness, item[1].genome)
    )
    assert champion_key == (5, 0, 3)
    assert round(champion_cell.fitness, 4) == 18.8641
    assert champion_cell.genome == load_candidate_weights(root)


# --------------------------------------------------------------------------- #
# 7. Frozen-candidate byte-determinism through the shared rollout runner.       #
# --------------------------------------------------------------------------- #


def test_frozen_candidate_is_byte_deterministic(tmp_path: Path) -> None:
    genome = es.random_genome(_POLICY_GENOME_LENGTH, seed=1, scale=0.3)
    policy = build_masked_mlp_policy(genome, hidden=_HIDDEN)
    first = rollout_candidate(policy, 1004, output_dir=tmp_path / "a")
    second = rollout_candidate(policy, 1004, output_dir=tmp_path / "b")
    assert first.state_hashes == second.state_hashes
    assert first.state_hashes  # a non-empty state-hash chain was actually rolled


# --------------------------------------------------------------------------- #
# 8. The vent-EXIT choice is learnable through the room head (PR #242 review).  #
# --------------------------------------------------------------------------- #


def test_policy_vent_exit_choice_is_learned_via_room_head() -> None:
    # A vent candidate scores its kind slot PLUS the room slot of its vent's
    # room, so an in-vent impostor's exit choice follows the learned room
    # preference instead of the lexical vent-id tie (Codex review on PR #242).
    from training.bakeoff.policy_es import MaskedMlpPolicy
    from agents.tactical.features import mlp_genome_length

    public_map = _public_map()
    encoder = TacticalFeatureEncoder()
    input_dim = encoder.feature_dimension(public_map)
    rooms = sorted(public_map.room_ids)
    output = len(rooms) + len(KIND_SLOTS)
    length = mlp_genome_length(input_dim=input_dim, hidden=_HIDDEN, output=output)
    b2_start = input_dim * _HIDDEN + _HIDDEN + _HIDDEN * output

    def vent_choice(preferred_room: str) -> str:
        genome = [0.0] * length
        genome[b2_start + len(rooms) + KIND_SLOTS.index("vent")] = 10.0
        genome[b2_start + rooms.index(preferred_room)] = 5.0
        policy = MaskedMlpPolicy(
            genome=genome,
            public_map=public_map,
            sabotage_kinds=("reactor",),
            hidden=_HIDDEN,
        )
        packet = _packet(tick=5, room="ADMIN", in_vent=True, cooldown=3)
        frame = policy.evaluate(
            packet,
            public_map,
            AgentMemory(),
            fsm_intent=WaitIntent(actor="imp", type="wait"),
        )
        assert isinstance(frame.intent, VentIntent)
        return frame.intent.payload.vent_id

    # From ADMIN_VENT every vent is submission-legal (current + two connected);
    # the learned room preference — not the lexical vent id — picks the exit.
    assert vent_choice("ELECTRICAL") == "ELECTRICAL_VENT"
    assert vent_choice("MEDBAY") == "MEDBAY_VENT"
