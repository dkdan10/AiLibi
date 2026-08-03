"""Tests for the Task 15.22 widened crew option basis + scorer plumbing.

Pins the definition-of-done contract for :class:`training.crew.options
.OwnedTaskOptionBasis` and the widened-basis seam in
:mod:`training.crew.scorer` (audits/audit-phase-15-pause.md decision 5, the
four-item review's item 4):

* the pinned 15.16 surfaces are byte-identical (the seven-kind menu, the
  21-name feature vector, the 22-weight genome, the v1 encoder tag);
* the widened surfaces are the additive re-basing: an eight-kind alphabet, the
  legacy scalar block carried verbatim, four owned-task scalars, and the
  ``nearest_task`` option over ``SelfView.owned_task_ids``;
* the FO-8-style interrupt is STRUCTURAL — a visible body routes to ``report``
  and ONLY ``report`` (the learned head is removed from the selectable set, not
  penalized), so the 15.16 win-by-meeting-starvation failure mode is
  unreachable;
* the ``nearest_task`` addition selects / routes to the nearest owned task, is
  skipped when that is the engine-fed pending task or while a gating sabotage
  makes the in-room ``do_task`` engine-illegal, and its override passes the
  wrapper's Task 15.22 legality mirror while a genuinely off-vocabulary override
  still raises;
* the widened entrant trains deterministically through the shared 15.14 ES core
  and the eval twin emits the full 15.15-shaped row (encoder v2, genome 27)
  through the candidate's OWN factory — including the leak-test factory mode.

Builders mirror ``tests/training/test_crew_scorer.py`` (local copies, no
cross-test imports); the ``_packet`` builder is extended with the ``owned_task_ids``
self channel Part 1 landed and the sabotage/in-vent surface the gating + mirror
proofs need.
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.store import AgentMemory
from agents.perception import (
    EVENT_GLOBAL_STATUS,
    EVENT_SAW_BODY,
    EVENT_SELF_STATE,
    PROVENANCE_INFERRED,
    PROVENANCE_OBSERVED,
)
from agents.tactical.crewmate_policy import CrewmatePolicy
from engine.world import load_canonical_map
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    MoveIntent,
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
from orchestrator.game import TacticalAgent
from training.bakeoff.harness import intent_key
from training.crew.options import (
    CREW_OPTION_FEATURE_NAMES,
    CREW_OPTION_KINDS,
    OWNED_TASK_OPTION_FEATURE_NAMES,
    OWNED_TASK_OPTION_KINDS,
    CrewOption,
    OwnedTaskOptionBasis,
    crew_genome_length,
    enumerate_crew_options,
    owned_task_genome_length,
)
from training.crew.scorer import (
    CREW_OWNED_TASKS_ENTRANT_NAME,
    ENCODER_VERSION,
    OWNED_TASK_ENCODER_VERSION,
    CrewEsEntrant,
    CrewOptionScorer,
    CrewProtocolConfig,
    _CrewCandidateAgent,
    _owned_task_do_task_is_submission_legal,
    crew_es_budget,
    evaluate_crew_candidate,
    write_crew_results_jsonl,
)
from training.determinism import PolicyFrame

# The 4-room star mirrored from test_crew_scorer._STAR_MAP, with the extra task
# locations the routing-leg / gating geometry needs: ``scan_medbay`` (MEDBAY) and
# ``wires_cafeteria`` (CAFETERIA). Distances: every leaf is one hop from the
# CAFETERIA hub and two hops from every other leaf.
_STAR_MAP = PublicMapView(
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
    task_locations={
        "swipe_card": "ADMIN",
        "wires_electrical": "ELECTRICAL",
        "scan_medbay": "MEDBAY",
        "wires_cafeteria": "CAFETERIA",
    },
    spawn_room="CAFETERIA",
    meeting_room="CAFETERIA",
    emergency_button_room="CAFETERIA",
)


def _weights_favoring_owned(kind: str, *, weight: float = 100.0) -> tuple[float, ...]:
    """A widened genome whose linear head loads ONLY the given kind's one-hot."""

    weights = [0.0] * owned_task_genome_length()
    weights[OWNED_TASK_OPTION_KINDS.index(kind)] = weight
    return tuple(weights)


def _packet(
    *,
    tick: int,
    room: RoomId,
    agent_id: str = "p-1",
    role: str = "CREWMATE",
    pending_task_id: str | None = None,
    owned_task_ids: tuple[str, ...] = (),
    in_vent: bool = False,
    visible_players: tuple[PlayerView, ...] = (),
    visible_bodies: tuple[BodyView, ...] = (),
    sabotage_active: bool = False,
    sabotage_kind: str | None = None,
    sabotage_repair_rooms: tuple[RoomId, ...] = (),
    sabotage_is_gating: bool = False,
) -> ObservationPacket:
    return ObservationPacket(
        tick=tick,
        agent_id=agent_id,
        self_state=SelfView(
            room=room,
            role=role,  # type: ignore[arg-type]
            pending_task_id=pending_task_id,
            owned_task_ids=owned_task_ids,
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


def _memory(*events: EpisodicEvent) -> AgentMemory:
    store = MemoryStore()
    for event in events:
        store.append(event)
    return AgentMemory(episodic=store)


def _self_state_event(
    *, tick: int, room: RoomId, pending_task_id: str | None = None
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SELF_STATE,
        payload={"room": room, "pending_task_id": pending_task_id},
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


def _fsm_intent(memory: AgentMemory) -> ActionIntent:
    return CrewmatePolicy(agent_id="p-1").decide(memory.episodic, _STAR_MAP)


def _features_by_name(option: CrewOption) -> dict[str, float]:
    assert len(option.features) == len(OWNED_TASK_OPTION_FEATURE_NAMES)
    return dict(zip(OWNED_TASK_OPTION_FEATURE_NAMES, option.features, strict=True))


def _nearest_task_option(options: tuple[CrewOption, ...]) -> list[CrewOption]:
    return [option for option in options if option.kind == "nearest_task"]


# --------------------------------------------------------------------------- #
# 1. The pinned 15.16 surfaces are byte-identical.                              #
# --------------------------------------------------------------------------- #


def test_legacy_surfaces_are_unchanged() -> None:
    assert len(CREW_OPTION_KINDS) == 7
    assert len(CREW_OPTION_FEATURE_NAMES) == 21
    assert crew_genome_length() == 22
    # A scorer with no basis is the 15.16 behavior byte-identical: v1 tag, the
    # 22-weight genome.
    scorer = CrewOptionScorer(weights=(0.0,) * crew_genome_length())
    assert scorer.encoder_version == ENCODER_VERSION == "crew-option-features-v1"


# --------------------------------------------------------------------------- #
# 2. The widened shape: the additive re-basing.                                 #
# --------------------------------------------------------------------------- #


def test_widened_feature_layout_and_basis_properties() -> None:
    assert OWNED_TASK_OPTION_KINDS == (*CREW_OPTION_KINDS, "nearest_task")
    assert len(OWNED_TASK_OPTION_KINDS) == 8
    # Eight kind one-hots lead the layout, in OWNED_TASK_OPTION_KINDS order.
    assert OWNED_TASK_OPTION_FEATURE_NAMES[:8] == tuple(
        f"kind_{kind}" for kind in OWNED_TASK_OPTION_KINDS
    )
    # The fourteen legacy scalar names carried VERBATIM.
    assert (
        OWNED_TASK_OPTION_FEATURE_NAMES[8:22]
        == CREW_OPTION_FEATURE_NAMES[len(CREW_OPTION_KINDS) :]
    )
    # The four owned-task scalars trail.
    assert OWNED_TASK_OPTION_FEATURE_NAMES[22:] == (
        "owned_tasks_norm",
        "nearest_owned_hops_norm",
        "same_room_owned_norm",
        "goal_room_owned_norm",
    )
    assert len(OWNED_TASK_OPTION_FEATURE_NAMES) == 26
    assert owned_task_genome_length() == 27

    basis = OwnedTaskOptionBasis()
    assert basis.genome_length() == 27 == owned_task_genome_length()
    assert basis.kinds == OWNED_TASK_OPTION_KINDS
    assert basis.feature_names == OWNED_TASK_OPTION_FEATURE_NAMES


# --------------------------------------------------------------------------- #
# 3. The interrupt-preserving constraint (DoD): a visible body → ONLY report.   #
# --------------------------------------------------------------------------- #


def _body_interrupt_fixture() -> tuple[ObservationPacket, AgentMemory]:
    memory = _memory(
        _self_state_event(tick=4, room="ADMIN", pending_task_id="swipe_card"),
        _saw_body_event(tick=4, body_id="b-1", room="ADMIN", victim_id="p-6"),
    )
    packet = _packet(
        tick=4,
        room="ADMIN",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
        visible_bodies=(BodyView(id="b-1", room="ADMIN", victim_id="p-6"),),
    )
    return packet, memory


def test_body_interrupt_leaves_only_report_and_head_cannot_select_away() -> None:
    packet, memory = _body_interrupt_fixture()
    fsm_intent = _fsm_intent(memory)
    basis = OwnedTaskOptionBasis()

    # basis.enumerate returns EXACTLY one option — the re-based report.
    options = basis.enumerate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
    assert len(options) == 1
    (report,) = options
    assert report.kind == "report"
    assert isinstance(report.intent, ReportBodyIntent)
    assert report.intent.payload.body_id == "b-1"
    assert len(report.features) == len(OWNED_TASK_OPTION_FEATURE_NAMES)

    # A scorer loaded +100 on EVERY non-report kind still emits the report: the
    # option is not on the selectable set (structural unreachability).
    for kind in OWNED_TASK_OPTION_KINDS:
        if kind == "report":
            continue
        scorer = CrewOptionScorer(weights=_weights_favoring_owned(kind), basis=basis)
        frame = scorer.evaluate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
        assert isinstance(frame.intent, ReportBodyIntent), kind

    # Contrast: the legacy menu offers report AMONG other options (the 15.16
    # menu the scorer COULD have selected away from).
    legacy = enumerate_crew_options(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
    legacy_kinds = {option.kind for option in legacy}
    assert "report" in legacy_kinds
    assert len(legacy) > 1


# --------------------------------------------------------------------------- #
# 4. nearest_task selection: the in-room do_task addition.                      #
# --------------------------------------------------------------------------- #


def test_nearest_task_in_room_do_task_selection_and_features() -> None:
    memory = _memory(
        _self_state_event(tick=3, room="ELECTRICAL", pending_task_id="swipe_card")
    )
    packet = _packet(
        tick=3,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    fsm_intent = _fsm_intent(memory)
    basis = OwnedTaskOptionBasis()
    options = basis.enumerate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)

    # Every widened option is well-formed (26 features, exactly one one-hot).
    for option in options:
        vector = option.features
        assert len(vector) == len(OWNED_TASK_OPTION_FEATURE_NAMES)
        one_hots = vector[: len(OWNED_TASK_OPTION_KINDS)]
        assert sum(one_hots) == 1.0
        assert one_hots[OWNED_TASK_OPTION_KINDS.index(option.kind)] == 1.0
        assert all(0.0 <= value <= 1.0 for value in vector)

    # swipe_card (ADMIN) is 2 hops; wires_electrical is in the agent's own room
    # (0 hops) → nearest, and it is not the pending task → the option exists.
    (nearest,) = _nearest_task_option(options)
    assert isinstance(nearest.intent, DoTaskIntent)
    assert nearest.intent.payload.task_id == "wires_electrical"
    assert nearest.target_id == "wires_electrical"
    feats = _features_by_name(nearest)
    assert feats["goal_is_current_room"] == 1.0
    assert feats["owned_tasks_norm"] == pytest.approx(0.25)
    assert feats["same_room_owned_norm"] == pytest.approx(0.125)
    assert feats["nearest_owned_hops_norm"] == pytest.approx(0.0)
    assert feats["goal_room_owned_norm"] == pytest.approx(0.125)

    # A nearest_task-loaded scorer selects it.
    scorer = CrewOptionScorer(
        weights=_weights_favoring_owned("nearest_task"), basis=basis
    )
    frame = scorer.evaluate(packet, _STAR_MAP, memory, fsm_intent=fsm_intent)
    assert isinstance(frame.intent, DoTaskIntent)
    assert frame.intent.payload.task_id == "wires_electrical"


# --------------------------------------------------------------------------- #
# 5. nearest == pending → no nearest_task option (continue_task carries it).     #
# --------------------------------------------------------------------------- #


def test_nearest_equals_pending_offers_no_nearest_task() -> None:
    memory = _memory(
        _self_state_event(tick=3, room="ADMIN", pending_task_id="swipe_card")
    )
    packet = _packet(
        tick=3,
        room="ADMIN",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    fsm_intent = _fsm_intent(memory)
    options = OwnedTaskOptionBasis().enumerate(
        packet, _STAR_MAP, memory, fsm_intent=fsm_intent
    )
    # swipe_card is in the agent's own room (0 hops) and IS the pending task, so
    # the nearest owned task is the pending one → skipped.
    assert _nearest_task_option(options) == []


# --------------------------------------------------------------------------- #
# 6. The routing leg: a MoveIntent toward the nearest non-pending owned task.    #
# --------------------------------------------------------------------------- #


def test_nearest_task_routing_leg_moves_one_hop() -> None:
    memory = _memory(
        _self_state_event(tick=3, room="MEDBAY", pending_task_id="swipe_card")
    )
    packet = _packet(
        tick=3,
        room="MEDBAY",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_cafeteria"),
    )
    fsm_intent = _fsm_intent(memory)
    options = OwnedTaskOptionBasis().enumerate(
        packet, _STAR_MAP, memory, fsm_intent=fsm_intent
    )
    # From MEDBAY: swipe_card (ADMIN) is 2 hops, wires_cafeteria (CAFETERIA) is
    # 1 hop → nearest, not the pending task, not in-room → one A* step toward it.
    (nearest,) = _nearest_task_option(options)
    assert isinstance(nearest.intent, MoveIntent)
    assert nearest.intent.payload.to_room == "CAFETERIA"
    assert nearest.target_id == "wires_cafeteria"
    feats = _features_by_name(nearest)
    assert feats["path_hops_norm"] == pytest.approx(0.1)
    assert feats["goal_is_current_room"] == 0.0
    assert feats["owned_tasks_norm"] == pytest.approx(0.25)
    assert feats["nearest_owned_hops_norm"] == pytest.approx(0.1)
    assert feats["same_room_owned_norm"] == pytest.approx(0.0)
    assert feats["goal_room_owned_norm"] == pytest.approx(0.125)


# --------------------------------------------------------------------------- #
# 7. Gating sabotage: the in-room do_task is engine-illegal → nearest_task gone. #
# --------------------------------------------------------------------------- #


def test_nearest_task_skipped_while_gating_sabotage() -> None:
    memory = _memory(
        _self_state_event(tick=5, room="ELECTRICAL", pending_task_id="swipe_card"),
        _global_status_event(
            tick=5,
            sabotage_active=True,
            sabotage_kind="reactor",
            sabotage_repair_rooms=("MEDBAY",),
            sabotage_is_gating=True,
        ),
    )
    packet = _packet(
        tick=5,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
        sabotage_active=True,
        sabotage_kind="reactor",
        sabotage_repair_rooms=("MEDBAY",),
        sabotage_is_gating=True,
    )
    fsm_intent = _fsm_intent(memory)
    options = OwnedTaskOptionBasis().enumerate(
        packet, _STAR_MAP, memory, fsm_intent=fsm_intent
    )
    # wires_electrical is in-room and nearest, but a gating sabotage makes the
    # in-place do_task engine-illegal and there is no move to fall to → absent.
    assert _nearest_task_option(options) == []


# --------------------------------------------------------------------------- #
# 8. The wrapper legality mirror: override accepted; off-vocabulary raises.      #
# --------------------------------------------------------------------------- #


def test_legality_mirror_predicate() -> None:
    do_wires = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": "p-1", "payload": {"task_id": "wires_electrical"}}
    )
    in_room = _packet(
        tick=3,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    # Positive: crewmate, in the task room, owned, not gating.
    assert _owned_task_do_task_is_submission_legal(
        do_wires, packet=in_room, public_map=_STAR_MAP
    )
    # Not owned.
    do_foreign = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": "p-1", "payload": {"task_id": "scan_medbay"}}
    )
    assert not _owned_task_do_task_is_submission_legal(
        do_foreign, packet=in_room, public_map=_STAR_MAP
    )
    # Wrong room (owned, but the agent stands elsewhere).
    wrong_room = _packet(
        tick=3,
        room="ADMIN",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    assert not _owned_task_do_task_is_submission_legal(
        do_wires, packet=wrong_room, public_map=_STAR_MAP
    )
    # Gating sabotage.
    gated = _packet(
        tick=3,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
        sabotage_active=True,
        sabotage_kind="reactor",
        sabotage_repair_rooms=("MEDBAY",),
        sabotage_is_gating=True,
    )
    assert not _owned_task_do_task_is_submission_legal(
        do_wires, packet=gated, public_map=_STAR_MAP
    )
    # A non-do_task intent and a foreign actor are both rejected.
    assert not _owned_task_do_task_is_submission_legal(
        WaitIntent(actor="p-1", type="wait"), packet=in_room, public_map=_STAR_MAP
    )
    do_other_actor = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": "p-2", "payload": {"task_id": "wires_electrical"}}
    )
    assert not _owned_task_do_task_is_submission_legal(
        do_other_actor, packet=in_room, public_map=_STAR_MAP
    )


def test_wrapper_accepts_owned_task_override_without_raising() -> None:
    inner = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    scorer = CrewOptionScorer(
        weights=_weights_favoring_owned("nearest_task"), basis=OwnedTaskOptionBasis()
    )
    agent = _CrewCandidateAgent(
        inner,
        policy=scorer,
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        trace=None,
        diagnostic=None,
        roles={},
    )
    # The FSM proposes the swipe_card walk (pending in ADMIN); the scorer
    # overrides with the in-room do_task(wires_electrical) — a task the mask
    # never enumerates (it only knows pending) but the engine accepts, so the
    # wrapper accepts it through the legality mirror WITHOUT raising.
    packet = _packet(
        tick=3,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    chosen = agent.decide(packet, _STAR_MAP)
    assert isinstance(chosen, DoTaskIntent)
    assert chosen.payload.task_id == "wires_electrical"


class _StubDoTaskPolicy:
    """A minimal CrewTrackPolicy that always overrides with one do_task intent."""

    def __init__(self, task_id: str) -> None:
        self._task_id = task_id

    @property
    def encoder_version(self) -> str:
        return "stub"

    def _intent(self, packet: ObservationPacket) -> DoTaskIntent:
        return DoTaskIntent.model_validate(
            {
                "type": "do_task",
                "actor": packet.agent_id,
                "payload": {"task_id": self._task_id},
            }
        )

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> PolicyFrame:
        return PolicyFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=(),
            logits=(),
            intent=self._intent(packet),
        )

    def choice_distribution(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> Mapping[str, float]:
        return {intent_key(self._intent(packet)): 1.0}


def test_wrapper_raises_on_unowned_task_override() -> None:
    inner = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    agent = _CrewCandidateAgent(
        inner,
        policy=_StubDoTaskPolicy("wires_electrical"),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        trace=None,
        diagnostic=None,
        roles={},
    )
    # wires_electrical is NOT in the recipient's owned set → the mirror rejects
    # it (as does the mask) → the wrapper fails loud.
    packet = _packet(
        tick=3,
        room="ELECTRICAL",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card",),
    )
    with pytest.raises(ValueError, match="non-submission-legal"):
        agent.decide(packet, _STAR_MAP)


def test_wrapper_raises_on_wrong_room_owned_task_override() -> None:
    inner = TacticalAgent(
        agent_id="p-1", policy=CrewmatePolicy(agent_id="p-1"), role="CREWMATE"
    )
    agent = _CrewCandidateAgent(
        inner,
        policy=_StubDoTaskPolicy("wires_electrical"),
        sabotage_kinds=("lights", "reactor"),
        emergency_uses_per_player=1,
        trace=None,
        diagnostic=None,
        roles={},
    )
    # wires_electrical is owned but the agent stands in MEDBAY (its room is
    # ELECTRICAL) → the engine would reject the do_task, so the mirror does too.
    packet = _packet(
        tick=3,
        room="MEDBAY",
        pending_task_id="swipe_card",
        owned_task_ids=("swipe_card", "wires_electrical"),
    )
    with pytest.raises(ValueError, match="non-submission-legal"):
        agent.decide(packet, _STAR_MAP)


# --------------------------------------------------------------------------- #
# 9. The widened CI-budget entrant trains deterministically.                    #
# --------------------------------------------------------------------------- #


def test_owned_entrant_ci_budget_is_deterministic() -> None:
    basis = OwnedTaskOptionBasis()
    first = CrewEsEntrant(config=crew_es_budget("ci"), basis=basis).train()
    second = CrewEsEntrant(config=crew_es_budget("ci"), basis=basis).train()
    assert first.entrant == CREW_OWNED_TASKS_ENTRANT_NAME
    assert len(first.weights) == owned_task_genome_length() == 27
    assert first.weights == second.weights
    assert first.train_metadata["es_digest"] == second.train_metadata["es_digest"]
    assert first.config["genome_length"] == 27
    assert first.config["encoder_version"] == OWNED_TASK_ENCODER_VERSION
    assert first.config["feature_names"] == list(OWNED_TASK_OPTION_FEATURE_NAMES)
    assert isinstance(first.policy, CrewOptionScorer)


# --------------------------------------------------------------------------- #
# 10. The eval twin's full 15.15-shaped row at a tiny protocol.                 #
# --------------------------------------------------------------------------- #


def test_owned_evaluate_crew_candidate_full_row(tmp_path: Path) -> None:
    game_map = load_canonical_map()
    protocol = CrewProtocolConfig(
        eval_seeds=(1000,),
        determinism_seeds=(1004,),
        leak_seeds=(0, 1),
        repeat_n=2,
    )
    basis = OwnedTaskOptionBasis()
    # ES seed 0 -> 2, for the reason spelled out at the sibling fixture
    # (tests/training/test_crew_scorer.py::test_evaluate_crew_candidate_full_row):
    # a generations=1 / population=2 budget makes the candidate one random draw,
    # most draws are the marathon shape whose games never reach a body, and Task
    # 19.3's portable ES sampler re-rolled which seed lands a terminating one.
    # Seed 2 does here (champion_fitness 13.34, 21 bodies across the leak seeds).
    ci_budget = crew_es_budget("ci")
    budget = replace(ci_budget, es=ci_budget.es.model_copy(update={"seed": 2}))
    entrant = CrewEsEntrant(config=budget, game_map=game_map, basis=basis)
    candidate = entrant.train()
    result = evaluate_crew_candidate(
        candidate, protocol, artifact_root=tmp_path, game_map=game_map
    )

    assert result.entrant == CREW_OWNED_TASKS_ENTRANT_NAME
    assert result.encoder_version == OWNED_TASK_ENCODER_VERSION
    assert result.genome_length == owned_task_genome_length()
    assert result.tier == "candidate"
    assert result.determinism.deterministic
    assert result.repeat_spread is None

    # The leak-test factory mode ran through the candidate's OWN crew factory,
    # scanning the widened packets (the owned_task_ids discipline included).
    assert result.leak_test_passed
    assert result.leak_packets_scanned is not None
    assert result.leak_packets_scanned > 0
    assert result.leak_failure is None

    # The crew metric block + the Q6 diagnostic populate.
    assert 0.0 <= result.crew_win_rate <= 1.0
    assert result.coverage_cue.crew_decisions > 0
    assert result.fsm_intent_agreement is not None

    # The row serializes and round-trips through the jsonl writer.
    line = result.to_json_line()
    assert json.loads(line)["entrant"] == CREW_OWNED_TASKS_ENTRANT_NAME
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "rows.jsonl"
        write_crew_results_jsonl([result], out)
        assert out.read_text().count("\n") == 1


# --------------------------------------------------------------------------- #
# 11. Genome rejection: a basis scorer refuses the 22- and 26-weight genomes.    #
# --------------------------------------------------------------------------- #


def test_basis_scorer_rejects_legacy_and_short_genomes() -> None:
    basis = OwnedTaskOptionBasis()
    with pytest.raises(ValueError, match="weights length"):
        CrewOptionScorer(weights=(0.0,) * crew_genome_length(), basis=basis)  # 22
    with pytest.raises(ValueError, match="weights length"):
        CrewOptionScorer(
            weights=(0.0,) * (owned_task_genome_length() - 1), basis=basis
        )  # 26
