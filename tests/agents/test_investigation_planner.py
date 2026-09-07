"""Bounded routes, genuine arrival, interruptions and one-use evidence."""

from __future__ import annotations

from typing import Literal

import pytest

from agents.memory.investigation import (
    InvestigationEvidence,
    InvestigationObservation,
    InvestigationState,
)
from agents.tactical.investigation import transition_investigation
from observation.action_intent import ActionIntent, DoTaskIntent, MoveIntent, WaitIntent
from observation.packet import BodyView, ObservationPacket, PlayerView
from observation.public_map import PublicMapView
from tests.agents.test_tactical_experiments import _map


def _packet(
    tick: int = 6,
    room: str = "H",
    *,
    visible: tuple[PlayerView, ...] = (),
    role: Literal["CREWMATE", "IMPOSTOR"] = "CREWMATE",
) -> ObservationPacket:
    return ObservationPacket.model_validate(
        {
            "tick": tick,
            "agent_id": "crew",
            "self_state": {"room": room, "role": role, "pending_task_id": "task_c"},
            "visible_players": visible,
            "visible_bodies": (),
            "audible_events": (),
            "global_state": {
                "tasks_completed": 0,
                "tasks_total": 6,
                "task_completion_percent": 0,
                "sabotage_active": False,
                "sabotage_kind": None,
            },
            "cooldown": None if role == "CREWMATE" else 2,
            "temporal_observation_version": 2,
        }
    )


def _evidence(
    *, tick: int = 2, room: str = "A", source: str = "opaque:9999", dead: bool = False
) -> InvestigationEvidence:
    return InvestigationEvidence(
        known_player_ids=("crew", "missing"),
        known_dead_ids=("missing",) if dead else (),
        sightings=(
            InvestigationObservation(
                target_id="missing",
                source_observation_id=source,
                source_tick=tick,
                last_known_room=room,
                observation_phase="snapshot",
            ),
        ),
    )


def _anchor() -> MoveIntent:
    return MoveIntent.model_validate(
        {"type": "move", "actor": "crew", "payload": {"to_room": "B"}}
    )


def _step(
    state: InvestigationState | None = None,
    *,
    packet: ObservationPacket | None = None,
    evidence: InvestigationEvidence | None = None,
    public_map: PublicMapView | None = None,
    anchor: ActionIntent | None = None,
    enabled: bool = True,
    urgent: bool = False,
) -> InvestigationState:
    return transition_investigation(
        state,
        packet=packet or _packet(),
        evidence=evidence or _evidence(),
        public_map=public_map or _map(),
        anchor_intent=anchor or _anchor(),
        investigation_version=1 if enabled else None,
        urgent=urgent,
    )


def _destination(state: InvestigationState) -> str:
    assert state.last_intent is not None and state.last_intent.type == "move"
    return state.last_intent.payload.to_room


def test_first_search_changes_task_travel_and_records_real_source() -> None:
    state = _step()
    assert _destination(state) == "A" != _anchor().payload.to_room
    plan = state.active_plan
    assert plan is not None
    assert (plan.source_observation_id, plan.source_tick) == ("opaque:9999", 2)
    assert (plan.started_tick, plan.expires_tick, plan.visited_rooms) == (6, 12, ())
    assert state.consumed_sources[0].target_id == "missing"


def test_arrival_is_observed_not_assumed_and_three_rooms_end_search() -> None:
    state = _step()
    # Rejected/discarded movement must not fabricate arrival.
    state = _step(state, packet=_packet(7))
    assert state.active_plan is not None and state.active_plan.visited_rooms == ()
    state = _step(state, packet=_packet(8, "A"))
    assert state.active_plan is not None and state.active_plan.visited_rooms == ("A",)
    assert _destination(state) == "C"  # C/H are equally close: room tie-break.
    state = _step(state, packet=_packet(9, "C"))
    assert state.active_plan is not None and state.active_plan.visited_rooms == (
        "A",
        "C",
    )
    state = _step(state, packet=_packet(10, "A"))
    assert _destination(state) == "H"
    state = _step(state, packet=_packet(11, "H"))
    assert state.active_plan is None
    assert state.last_intent == _anchor()
    for tick in range(12, 16):
        state = _step(state, packet=_packet(tick))
        assert state.active_plan is None
        assert len(state.consumed_sources) == 1


@pytest.mark.parametrize("age", [0, 3, 13, 40])
def test_fresh_or_stale_sources_do_not_start_a_search(age: int) -> None:
    state = _step(packet=_packet(50), evidence=_evidence(tick=50 - age))
    assert state.active_plan is None
    assert not state.consumed_sources
    assert state.last_intent == _anchor()


@pytest.mark.parametrize("age", [4, 12])
def test_source_age_edges_are_inclusive(age: int) -> None:
    assert _step(packet=_packet(50), evidence=_evidence(tick=50 - age)).active_plan


def test_future_source_is_refused_without_clock_parsing_from_citation_id() -> None:
    with pytest.raises(ValueError, match="future"):
        _step(evidence=_evidence(tick=7))
    assert _step(evidence=_evidence(source="looks-like-future:999999")).active_plan


@pytest.mark.parametrize("change", ["visible", "dead", "new_sighting"])
def test_reacquisition_or_known_death_ends_plan(change: str) -> None:
    packet = _packet(7)
    evidence = _evidence()
    if change == "visible":
        packet = _packet(7, visible=(PlayerView(id="missing", room="H", action=None),))
    elif change == "dead":
        evidence = _evidence(dead=True)
    else:
        evidence = _evidence(tick=6, room="C", source="new-source")
    state = _step(_step(), packet=packet, evidence=evidence)
    assert state.active_plan is None and len(state.consumed_sources) == 1
    assert state.last_intent == _anchor()


def test_new_eligible_sighting_rearms_but_another_id_at_consumed_tick_does_not() -> (
    None
):
    expired = _step(_step(), packet=_packet(12))
    assert expired.active_plan is None
    aliased = _step(
        expired, packet=_packet(13), evidence=_evidence(source="same-tick-id")
    )
    assert aliased.active_plan is None
    new = _step(
        aliased, packet=_packet(14), evidence=_evidence(tick=10, source="fresh")
    )
    assert (
        new.active_plan is not None and new.active_plan.source_observation_id == "fresh"
    )
    assert len(new.consumed_sources) == 1


@pytest.mark.parametrize("interrupt", ["urgent", "task", "body", "repair", "kill"])
def test_interrupts_preserve_anchor_without_renewing_plan_expiry(
    interrupt: str,
) -> None:
    state = _step()
    assert state.active_plan is not None
    for tick in (7, 11, 12, 13):
        packet = _packet(tick)
        anchor: ActionIntent = _anchor()
        if interrupt == "task":
            anchor = DoTaskIntent.model_validate(
                {"type": "do_task", "actor": "crew", "payload": {"task_id": "task_c"}}
            )
        elif interrupt == "body":
            packet = packet.model_copy(
                update={
                    "visible_bodies": (BodyView(id="body:v", victim_id="v", room="H"),)
                }
            )
        elif interrupt == "repair":
            packet = packet.model_copy(
                update={
                    "global_state": packet.global_state.model_copy(
                        update={"sabotage_active": True, "sabotage_is_gating": True}
                    )
                }
            )
        elif interrupt == "kill":
            packet = _packet(
                tick, visible=(PlayerView(id="other", room="H", action="kill"),)
            )
        state = _step(state, packet=packet, anchor=anchor, urgent=interrupt == "urgent")
        if interrupt == "body":
            assert state.last_intent is not None and state.last_intent.type == "report"
        else:
            assert state.last_intent == anchor
        assert (state.active_plan is None) == (tick >= 12)
        if state.active_plan is not None:
            assert state.active_plan.expires_tick == 12
    assert len(state.consumed_sources) == 1


def test_task_execution_and_urgent_walk_do_not_even_start_a_plan() -> None:
    task = DoTaskIntent.model_validate(
        {"type": "do_task", "actor": "crew", "payload": {"task_id": "task_c"}}
    )
    for state in (_step(anchor=task), _step(urgent=True)):
        assert state.active_plan is None and not state.consumed_sources


def test_disconnection_consumes_source_then_resumes_ordinary_work() -> None:
    disconnected = _map().model_copy(
        update={"room_neighbors": {"H": ("B",), "B": ("H",), "A": ("C",), "C": ("A",)}}
    )
    state = _step(public_map=disconnected)
    assert state.active_plan is None and len(state.consumed_sources) == 1
    assert state.last_intent == _anchor()
    assert _step(state, packet=_packet(7), public_map=disconnected).active_plan is None


def test_same_tick_is_idempotent_and_conflicting_or_backwards_packets_raise() -> None:
    state = _step()
    assert _step(state) is state
    with pytest.raises(ValueError, match="conflicting"):
        _step(state, packet=_packet(room="A"))
    with pytest.raises(ValueError, match="backwards"):
        _step(state, packet=_packet(5))


def test_off_and_impostor_decisions_are_cached_without_search() -> None:
    for state in (_step(enabled=False), _step(packet=_packet(role="IMPOSTOR"))):
        assert state.active_plan is None and not state.consumed_sources
        assert state.last_intent == _anchor()
        assert state.last_processed_tick == 6 and state.last_packet_sha256


def test_old_clock_and_foreign_actor_are_refused() -> None:
    with pytest.raises(ValueError, match="clock-corrected"):
        _step(
            packet=_packet().model_copy(update={"temporal_observation_version": None})
        )
    with pytest.raises(ValueError, match="different actor"):
        _step(anchor=WaitIntent(type="wait", actor="somebody-else"))


def test_oldest_eligible_target_then_id_is_deterministic() -> None:
    older = _evidence(tick=1).sightings[0].model_copy(update={"target_id": "older"})
    newer = _evidence(tick=2).sightings[0]
    evidence = InvestigationEvidence(
        known_player_ids=("crew", "older", "missing"), sightings=(newer, older)
    )
    left = _step(evidence=evidence)
    right = _step(evidence=evidence.model_copy(update={"sightings": (older, newer)}))
    assert left == right
    assert left.active_plan is not None and left.active_plan.target_id == "older"


def test_adjacent_visible_body_routes_then_reports_without_private_death_search() -> (
    None
):
    body = BodyView(id="body:missing", victim_id="missing", room="A")
    packet = _packet().model_copy(update={"visible_bodies": (body,)})
    state = _step(packet=packet, evidence=_evidence(dead=True))
    assert _destination(state) == "A"
    assert state.active_plan is None and not state.consumed_sources
    arrived = _packet(7, "A").model_copy(update={"visible_bodies": (body,)})
    state = _step(state, packet=arrived, evidence=_evidence(dead=True))
    assert state.last_intent is not None and state.last_intent.type == "report"
    assert state.last_intent.payload.body_id == body.id
    # A vanished/no-longer-visible body does not leave a latched report route.
    state = _step(state, packet=_packet(8), evidence=_evidence(dead=True))
    assert state.last_intent == _anchor()
    assert _step(packet=packet, enabled=False).last_intent == _anchor()


def test_visible_body_distance_then_id_is_deterministic_and_unreachable_is_not_pursued() -> (
    None
):
    bodies = (
        BodyView(id="z-near", victim_id="z", room="A"),
        BodyView(id="a-far", victim_id="a", room="C"),
        BodyView(id="b-near", victim_id="b", room="B"),
    )
    packet = _packet().model_copy(update={"visible_bodies": bodies})
    assert _destination(_step(packet=packet)) == "B"
    assert _step(packet=packet) == _step(
        packet=packet.model_copy(update={"visible_bodies": tuple(reversed(bodies))})
    ).model_copy(update={"last_packet_sha256": _step(packet=packet).last_packet_sha256})
    disconnected = _map().model_copy(
        update={"room_neighbors": {"H": (), "B": (), "A": ("C",), "C": ("A",)}}
    )
    assert _step(packet=packet, public_map=disconnected).last_intent == _anchor()
