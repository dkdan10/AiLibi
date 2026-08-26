from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_GLOBAL_STATUS,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_INFERRED,
    PROVENANCE_OBSERVED,
)
from agents.memory.store import _EVENT_MEETING_BOUNDARY
from agents.tactical.impostor_policy import (
    _MEETING_BOUNDARY_EVENT,
    ImpostorPolicy,
)
from eval.evidence_honesty import (
    LIVE_POLICY_FOLD,
    RATIFIED_BASELINE,
    RATIFIED_I11_CELLS,
    ImpostorTargetingCells,
    compute_evidence_honesty,
    reconstruct_impostor_decisions,
)
from observation.action_intent import (
    DoTaskIntent,
    KillIntent,
    MoveIntent,
    SabotageIntent,
    VentIntent,
    WaitIntent,
)
from observation.public_map import PublicMapView, RoomId


# Vents (Task 11.1). Three vents -- in ADMIN, ELECTRICAL, MEDBAY -- all mutually
# connected; CAFETERIA deliberately has NO vent so the move-away cover fallback
# and the every-other-branch tests (which use CAFETERIA) are unaffected by the
# vent wiring. The graph is symmetric, mirroring the canonical map's vent layout.
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


def _public_map(
    *,
    rooms: tuple[RoomId, ...] = ("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
    neighbors: Mapping[RoomId, tuple[RoomId, ...]] | None = None,
    task_locations: Mapping[str, RoomId] | None = None,
    vent_graph: Mapping[str, tuple[str, ...]] | None = None,
    vent_rooms: Mapping[str, RoomId] | None = None,
    emergency_button_room: RoomId = "CAFETERIA",
    meeting_room: RoomId = "CAFETERIA",
    spawn_room: RoomId = "CAFETERIA",
) -> PublicMapView:
    if neighbors is None:
        neighbors = {
            "ADMIN": ("CAFETERIA",),
            "CAFETERIA": ("ADMIN", "ELECTRICAL", "MEDBAY"),
            "ELECTRICAL": ("CAFETERIA",),
            "MEDBAY": ("CAFETERIA",),
        }
    if task_locations is None:
        task_locations = {"swipe_card": "ADMIN", "wires_electrical": "ELECTRICAL"}
    return PublicMapView(
        map_id="test_map",
        room_ids=rooms,
        room_neighbors=neighbors,
        vent_graph=_DEFAULT_VENT_GRAPH if vent_graph is None else vent_graph,
        vent_rooms=_DEFAULT_VENT_ROOMS if vent_rooms is None else vent_rooms,
        task_locations=task_locations,
        spawn_room=spawn_room,
        meeting_room=meeting_room,
        emergency_button_room=emergency_button_room,
    )


def _self_state_event(
    *,
    tick: int,
    room: RoomId,
    pending_task_id: str | None = None,
    role: str = "IMPOSTOR",
    fellow_impostor_ids: tuple[str, ...] = (),
    in_vent: bool = False,
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "room": room,
        "role": role,
        "pending_task_id": pending_task_id,
        "fellow_impostor_ids": fellow_impostor_ids,
        "in_vent": in_vent,
    }
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SELF_STATE,
        payload=payload,
        provenance=PROVENANCE_OBSERVED,
    )


def _cooldown_event(*, tick: int, cooldown: int) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_COOLDOWN_STATUS,
        payload={"cooldown": cooldown},
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_player_event(
    *,
    tick: int,
    player_id: str,
    room: RoomId,
    action: str | None = None,
) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_PLAYER,
        payload={"player_id": player_id, "room": room, "action": action},
        provenance=PROVENANCE_OBSERVED,
    )


def _saw_body_event(
    *,
    tick: int,
    body_id: str,
    room: RoomId,
    victim_id: str,
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
    sabotage_repair_rooms: tuple[RoomId, ...] = (),
    sabotage_is_gating: bool = False,
) -> EpisodicEvent:
    # Mirrors agents.perception._global_state_payload so the SABOTAGE branch
    # reads the same public, role-blind aggregate shape it sees in production
    # (Task 11.5/11.7). Provenance is INFERRED, matching the perception ingest.
    denominator = tasks_total if tasks_total else 1
    payload: dict[str, Any] = {
        "tasks_completed": tasks_completed,
        "tasks_total": tasks_total,
        "task_completion_percent": tasks_completed / denominator,
        "sabotage_active": sabotage_active,
        "sabotage_kind": sabotage_kind,
        "sabotage_repair_rooms": sabotage_repair_rooms,
        "sabotage_is_gating": sabotage_is_gating,
    }
    return EpisodicEvent(
        tick=tick,
        type=EVENT_GLOBAL_STATUS,
        payload=payload,
        provenance=PROVENANCE_INFERRED,
    )


def _meeting_boundary_event(*, tick: int) -> EpisodicEvent:
    # Mirrors agents.memory.store.absorb_meeting_evidence, which appends this
    # marker per living agent at the resume tick on the live and the replay path.
    return EpisodicEvent(
        tick=tick,
        type=_EVENT_MEETING_BOUNDARY,
        payload={},
        provenance=PROVENANCE_INFERRED,
    )


_REPLAYS = Path(__file__).resolve().parents[2] / "replays"
_SAMPLES_9P2I = _REPLAYS / "samples/9p2i"


def _frozen_static_ranking(memory: MemoryStore) -> tuple[Any, ...]:
    """``_scored_targets`` as the ES option enumerators call it, unrepaired.

    The repair composes new helpers over this static instead of changing it, so a
    pin that reads it is reading the defect the review measured.
    """

    events = memory.recent(since_tick=0)
    self_state = [event for event in events if event.type == EVENT_SELF_STATE][-1]
    latest = events[-1].tick
    cooldown = [
        event
        for event in events
        if event.type == EVENT_COOLDOWN_STATUS and event.tick == latest
    ][-1]
    return ImpostorPolicy._scored_targets(
        events,
        cooldown=int(cooldown.payload["cooldown"]),
        current_tick=latest,
        confirmed_dead=ImpostorPolicy._confirmed_dead_from_bodies(events),
        fellow_impostor_ids=ImpostorPolicy._fellow_impostor_ids_from_self_state(
            self_state
        ),
    )


def _own_room(memory: MemoryStore) -> str:
    events = memory.recent(since_tick=0)
    self_state = [event for event in events if event.type == EVENT_SELF_STATE][-1]
    room = self_state.payload["room"]
    assert isinstance(room, str)
    return room


def _store_with(*events: EpisodicEvent) -> MemoryStore:
    store = MemoryStore()
    for event in events:
        store.append(event)
    return store


class TestImpostorIdle:
    def test_cooldown_positive_with_no_targets_and_no_task_returns_wait(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=5),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)
        assert intent.actor == "imp"

    def test_idle_with_pending_task_in_other_room_moves_toward_task(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=3),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"
        assert intent.actor == "imp"

    def test_idle_with_pending_task_in_own_room_pretends_to_do_task(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=3),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, DoTaskIntent)
        assert intent.payload.task_id == "swipe_card"

    def test_idle_with_unknown_task_falls_back_to_wait(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="ghost_task"),
            _cooldown_event(tick=10, cooldown=3),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)


class TestImpostorKill:
    def test_solo_target_in_own_room_with_zero_cooldown_emits_kill(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == "victim"
        assert intent.actor == "imp"

    def test_kill_overrides_pretend_task_in_same_room(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="ADMIN"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == "victim"

    def test_kill_blocked_by_positive_cooldown(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=2),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)

    def test_stale_sighting_in_own_room_does_not_trigger_kill(self) -> None:
        # Saw victim in CAFETERIA at tick 5 but the latest tick has no
        # current sightings: the impostor cannot assume the victim is still
        # there, so it falls through to IDLE rather than KILL.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="CAFETERIA"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)


class TestImpostorKillRoomRevalidation:
    """Task 9.2 (audit-2026-06-07-0717 gp-5, findings MECH-B-1 / A-A-3).

    The kill emission re-validates the chosen target against the *freshest*
    observation (a current-tick ``saw_player`` in the actor's own room) instead
    of trusting the ``_scored_targets`` snapshot, which ranks sightings from any
    tick in the staleness window. Stale sightings still drive STALK/navigation;
    only the kill emission tightens. The engine same-room guard stays the
    backstop for the canonical id-order dodge (DESIGN.md §3.4).
    """

    def test_stale_sighting_in_other_room_does_not_emit_kill(self) -> None:
        # Target last seen in MEDBAY at tick 5 (another room, earlier); by tick
        # 10 the impostor is in CAFETERIA with no current sighting. The freshest
        # knowledge places the target elsewhere, so the policy stalks toward
        # MEDBAY and never queues a kill.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="MEDBAY"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, KillIntent)
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "MEDBAY"

    def test_target_seen_leaving_room_does_not_emit_kill(self) -> None:
        # The target was co-located in CAFETERIA at tick 8, but the freshest
        # sighting (tick 9) places it in MEDBAY: the stale tick-8 co-location
        # must not drive a kill. The current tick (10) carries no sighting, so
        # the re-validation fails and the policy stalks the freshest lead. This
        # is the case that distinguishes re-validating against the freshest
        # observation from trusting the scoring snapshot.
        store = _store_with(
            _self_state_event(tick=8, room="CAFETERIA"),
            _cooldown_event(tick=8, cooldown=0),
            _saw_player_event(tick=8, player_id="victim", room="CAFETERIA"),
            _self_state_event(tick=9, room="CAFETERIA"),
            _cooldown_event(tick=9, cooldown=0),
            _saw_player_event(tick=9, player_id="victim", room="MEDBAY"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, KillIntent)
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "MEDBAY"

    def test_current_tick_co_location_still_emits_kill(self) -> None:
        # The co-located case still kills: the target's freshest observation
        # (tick 10) places it in the impostor's own room, so the re-validation
        # passes and the kill is queued despite an earlier sighting elsewhere.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="MEDBAY"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == "victim"

    def test_target_colocated_now_raises_on_missing_player_id(self) -> None:
        # Boundary contract (no silent guess): a current-tick saw_player event
        # missing its player_id is rejected, mirroring the other saw_player
        # scanners. ``_saw_player_event`` always supplies the field, so the
        # malformed event is constructed directly.
        malformed = EpisodicEvent(
            tick=10,
            type=EVENT_SAW_PLAYER,
            payload={"room": "CAFETERIA", "action": None},
            provenance=PROVENANCE_OBSERVED,
        )

        with pytest.raises(ValueError, match="player_id"):
            ImpostorPolicy._target_colocated_now(
                (malformed,), target_id="victim", own_room="CAFETERIA"
            )

    def test_target_colocated_now_raises_on_missing_room(self) -> None:
        # A matching player_id with a missing room is also a contract violation.
        malformed = EpisodicEvent(
            tick=10,
            type=EVENT_SAW_PLAYER,
            payload={"player_id": "victim", "action": None},
            provenance=PROVENANCE_OBSERVED,
        )

        with pytest.raises(ValueError, match="room"):
            ImpostorPolicy._target_colocated_now(
                (malformed,), target_id="victim", own_room="CAFETERIA"
            )


class TestImpostorKillOpportunity:
    def test_two_players_in_own_room_waits_due_to_witness(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p2", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="p3", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)

    def test_three_players_in_own_room_still_waits(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p2", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="p3", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="p4", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)


class TestImpostorTeammateAwareness:
    """Task 7.9 (audit gp-1/gp-3): teammate filter + co-location + coordination."""

    def test_fellow_impostor_never_selected_as_kill_target(self) -> None:
        # p-1 is alone in CAFETERIA with only its fellow impostor p-2 in view.
        # Pre-7.9 the policy would have scored p-2 as a perfectly isolated
        # target and killed it (the friendly-fire trend). With the teammate
        # filter p-2 is not a candidate, so there is no target and the policy
        # idles instead of self-sabotaging the team.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", fellow_impostor_ids=("p-2",)),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p-2", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)

    def test_out_of_room_target_never_emits_kill(self) -> None:
        # gp-3 co-location: the only candidate was last seen in another room, so
        # the policy stalks toward it and never queues a kill against an
        # out-of-room target (which the engine would reject "kill requires same
        # room").
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, KillIntent)
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "MEDBAY"

    def test_crewmate_killed_despite_co_located_fellow_impostor(self) -> None:
        # A fellow impostor is no witness risk, so it is excluded from the
        # co-present count: a lone crewmate sharing the room with the impostor
        # and its teammate still scores co_present == 0 and is killable. p-1 is
        # the lower id among the co-located impostors, so it is the one that
        # acts.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", fellow_impostor_ids=("p-2",)),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p-2", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == "victim"

    def test_higher_id_impostor_defers_kill_to_co_located_lower_id_fellow(
        self,
    ) -> None:
        # Mirror of the case above from the higher-id impostor's seat: p-2 sees
        # the same killable crewmate but a co-located lower-id fellow (p-1), so
        # it defers (waits). Only the lower id emits, so the two co-located
        # impostors never both kill on the same tick.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", fellow_impostor_ids=("p-1",)),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p-1", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="p-2")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)

    def test_lower_id_fellow_in_other_room_does_not_force_defer(self) -> None:
        # The coordination tie-break is gated on co-location: a lower-id fellow
        # in a different room is not competing for this kill, so p-2 still kills
        # the co-located crewmate.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", fellow_impostor_ids=("p-1",)),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p-1", room="MEDBAY"),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="p-2")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == "victim"


class TestImpostorStalk:
    def test_stalks_toward_last_seen_isolated_target(self) -> None:
        # Saw victim in MEDBAY at tick 5. By tick 10 we are in CAFETERIA
        # with no current sightings: STALK toward MEDBAY (one hop).
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="MEDBAY"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "MEDBAY"

    def test_stalk_takes_one_a_star_step_along_multi_room_path(self) -> None:
        # ADMIN <-> CAFETERIA <-> ELECTRICAL. Victim last seen in
        # ELECTRICAL; impostor in ADMIN should step to CAFETERIA.
        store = _store_with(
            _self_state_event(tick=5, room="ADMIN"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="ELECTRICAL"),
            _self_state_event(tick=10, room="ADMIN"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    def test_stalk_picks_alphabetically_first_id_when_scores_tie(self) -> None:
        # Both players last seen alone (score == 1.0) one hop from CAFETERIA, so
        # score AND proximity tie and the player id is the only tier left: "alpha"
        # over "beta".
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="beta", room="ELECTRICAL"),
            _self_state_event(tick=8, room="CAFETERIA"),
            _cooldown_event(tick=8, cooldown=0),
            _saw_player_event(tick=8, player_id="alpha", room="MEDBAY"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        ranking = policy.ranked_targets(store, _public_map())
        intent = policy.decide(store, _public_map())

        assert [target.player_id for target in ranking] == ["alpha", "beta"]
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "MEDBAY"

    def test_stalk_prefers_the_nearer_target_when_score_and_id_would_split(
        self,
    ) -> None:
        # The proximity tier, proved by perturbing only distance: "beta" is one
        # hop away and "alpha" is two, both alone. The id tier alone would take
        # "alpha"; the tier below the score takes the nearer "beta".
        # ELECTRICAL neighbours CAFETERIA only, so beta is one hop out and alpha
        # (in ADMIN) is two; both are alone, so the scores tie at 1.0.
        store = _store_with(
            _self_state_event(tick=5, room="ELECTRICAL"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="alpha", room="ADMIN"),
            _saw_player_event(tick=5, player_id="beta", room="CAFETERIA"),
            _self_state_event(tick=10, room="ELECTRICAL"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        ranking = policy.ranked_targets(store, _public_map())

        assert [target.score for target in ranking] == [1.0, 1.0]
        assert [target.player_id for target in ranking] == ["beta", "alpha"]
        intent = policy.decide(store, _public_map())
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    def test_stalk_prefers_more_isolated_target_over_witnessed_one(self) -> None:
        # alpha was alone in ELECTRICAL at tick 5; beta and gamma are together in
        # the impostor's OWN room right now, so proximity favours them as far as it
        # can. It cannot reach above the score: alpha's 1.0 beats their 0.25 and the
        # FSM walks out of an occupied room to hunt the isolated target.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="alpha", room="ELECTRICAL"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="beta", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="gamma", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        ranking = policy.ranked_targets(store, _public_map())
        intent = policy.decide(store, _public_map())

        assert ranking[0].player_id == "alpha" and ranking[0].score == 1.0
        assert isinstance(intent, MoveIntent)
        # CAFETERIA neighbors ELECTRICAL directly, so the first step is
        # ELECTRICAL itself.
        assert intent.payload.to_room == "ELECTRICAL"

    def test_stalk_falls_through_to_idle_when_cooldown_positive(self) -> None:
        # Cooldown gates the score multiplier to 0, so the impostor cannot
        # justify approaching a target and reverts to pretend-task.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA", pending_task_id="swipe_card"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="alpha", room="ELECTRICAL"),
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=4),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        # Pretend-task move toward ADMIN, not toward ELECTRICAL.
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"


class TestImpostorCover:
    def test_body_in_own_room_routes_away_from_scene(self) -> None:
        # Body in CAFETERIA. The CAFETERIA neighbors are ADMIN, ELECTRICAL,
        # MEDBAY. Alphabetically first is "ADMIN".
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=8),
            _saw_body_event(
                tick=10,
                body_id="body-victim-10",
                room="CAFETERIA",
                victim_id="victim",
            ),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"

    def test_cover_takes_priority_over_kill(self) -> None:
        # Even with a fresh kill opportunity in the same room, COVER fires
        # first so the impostor does not stack a second body.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
            _saw_body_event(
                tick=10,
                body_id="body-other-9",
                room="CAFETERIA",
                victim_id="other",
            ),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"

    def test_body_in_other_room_does_not_trigger_cover(self) -> None:
        # Body in MEDBAY while impostor is in CAFETERIA: not COVER. With
        # nothing else to do (no targets, cooldown high) the impostor idles.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=8),
            _saw_body_event(
                tick=10,
                body_id="body-far-9",
                room="MEDBAY",
                victim_id="far",
            ),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, WaitIntent)


class TestImpostorDeterminism:
    def test_repeated_decide_calls_return_equal_intents(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")
        public_map = _public_map()

        intents = [policy.decide(store, public_map) for _ in range(5)]

        first = intents[0]
        assert isinstance(first, KillIntent)
        for intent in intents:
            assert isinstance(intent, KillIntent)
            assert intent.payload.target == first.payload.target
            assert intent.actor == first.actor

    def test_stalk_choice_independent_of_neighbor_listing_order(self) -> None:
        # Diamond ADMIN -> {B, C} -> ELECTRICAL. Victim last seen in
        # ELECTRICAL: A* tie-break on sorted ids chooses "B" regardless of
        # how the neighbor tuples are presented.
        neighbors_forward = {
            "ADMIN": ("B", "C"),
            "B": ("ADMIN", "ELECTRICAL"),
            "C": ("ADMIN", "ELECTRICAL"),
            "ELECTRICAL": ("B", "C"),
        }
        neighbors_reverse = {
            "ADMIN": ("C", "B"),
            "B": ("ELECTRICAL", "ADMIN"),
            "C": ("ELECTRICAL", "ADMIN"),
            "ELECTRICAL": ("C", "B"),
        }
        rooms = ("ADMIN", "B", "C", "ELECTRICAL")
        store = _store_with(
            _self_state_event(tick=5, room="ADMIN"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="ELECTRICAL"),
            _self_state_event(tick=10, room="ADMIN"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent_forward = policy.decide(
            store,
            _public_map(
                rooms=rooms,
                neighbors=neighbors_forward,
                task_locations={},
                emergency_button_room="ADMIN",
                meeting_room="ADMIN",
                spawn_room="ADMIN",
            ),
        )
        intent_reverse = policy.decide(
            store,
            _public_map(
                rooms=rooms,
                neighbors=neighbors_reverse,
                task_locations={},
                emergency_button_room="ADMIN",
                meeting_room="ADMIN",
                spawn_room="ADMIN",
            ),
        )

        assert isinstance(intent_forward, MoveIntent)
        assert isinstance(intent_reverse, MoveIntent)
        assert intent_forward.payload.to_room == "B"
        assert intent_reverse.payload.to_room == "B"


class TestImpostorInputValidation:
    def test_decide_raises_when_memory_is_empty(self) -> None:
        policy = ImpostorPolicy(agent_id="imp")

        with pytest.raises(ValueError, match="at least one episodic event"):
            policy.decide(MemoryStore(), _public_map())

    def test_decide_raises_when_no_self_state_event_present(self) -> None:
        store = _store_with(
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        with pytest.raises(ValueError, match="self_state event"):
            policy.decide(store, _public_map())

    def test_decide_raises_when_cooldown_event_missing_at_latest_tick(self) -> None:
        # cooldown_status appears at an earlier tick but not at the latest
        # one; the policy refuses to guess.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _self_state_event(tick=10, room="CAFETERIA"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        with pytest.raises(ValueError, match="cooldown_status event"):
            policy.decide(store, _public_map())


class TestImpostorAgentIdProperty:
    def test_agent_id_is_exposed_as_property(self) -> None:
        policy = ImpostorPolicy(agent_id="imp42")

        assert policy.agent_id == "imp42"


class TestImpostorStaleAndDeadTargetPruning:
    """R-3 / R-4: stale and confirmed-dead targets must be pruned from scoring.

    The audit's seed-0 reproduction shows the impostor oscillating between
    the room where it last saw a victim and the adjacent room forever.
    ``_scored_targets`` must drop sightings older than the documented
    staleness threshold and players observed as dead. Confirmed-dead
    derivation reads ``victim_id`` directly from the ``saw_body`` event
    payload populated by ``observation/service.py`` (see R-4 retirement
    in ``audits/audit-2026-05-16-0036-reconciled.md``).
    """

    def test_stale_sighting_with_matching_body_does_not_drive_stalk(self) -> None:
        # Impostor saw "victim" in MEDBAY at tick 5 and saw victim's body
        # back at tick 5 too. By tick 40 the sighting is 35 ticks old
        # (over the 30-tick staleness threshold) AND the body confirms
        # victim is dead. The policy must not stalk MEDBAY (the stale-
        # sighting room) and must not pick the stale/dead target — with
        # no valid targets it falls through to IDLE → wait.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="MEDBAY"),
            _saw_body_event(
                tick=5,
                body_id="body-victim-5",
                room="MEDBAY",
                victim_id="victim",
            ),
            _self_state_event(tick=40, room="CAFETERIA"),
            _cooldown_event(tick=40, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, KillIntent)
        assert not isinstance(intent, MoveIntent) or intent.payload.to_room != "MEDBAY"
        assert isinstance(intent, WaitIntent)

    def test_dead_target_filtered_even_when_sighting_is_recent(self) -> None:
        # Even within the staleness window, a sighting of a confirmed-dead
        # player must be ignored. Impostor saw "victim" alone in MEDBAY
        # at tick 10 (recent) but also saw victim's body in MEDBAY at
        # tick 10 — confirming death. The policy must not move toward
        # MEDBAY and must not pick victim as the scored target.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
            _saw_body_event(
                tick=10,
                body_id="body-victim-10",
                room="MEDBAY",
                victim_id="victim",
            ),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, MoveIntent) or intent.payload.to_room != "MEDBAY"

    def test_alive_target_still_stalked_when_other_target_confirmed_dead(self) -> None:
        # Two candidates: "victim" (confirmed dead at tick 5) and "alive"
        # (seen alone in ELECTRICAL at tick 8). The policy must skip
        # victim and stalk toward alive's room.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="victim", room="MEDBAY"),
            _saw_body_event(
                tick=5,
                body_id="body-victim-5",
                room="MEDBAY",
                victim_id="victim",
            ),
            _self_state_event(tick=8, room="CAFETERIA"),
            _cooldown_event(tick=8, cooldown=0),
            _saw_player_event(tick=8, player_id="alive", room="ELECTRICAL"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        # CAFETERIA neighbors ELECTRICAL directly.
        assert intent.payload.to_room == "ELECTRICAL"

    def test_body_with_unfamiliar_victim_does_not_block_other_targets(self) -> None:
        # R-4: with ``victim_id`` populated at the boundary, the policy
        # always knows which player a body belongs to. A body whose
        # victim is not among the impostor's sighted candidates simply
        # contributes a confirmed-dead entry for that unknown id and
        # does not affect scoring of other live targets.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="alive", room="ELECTRICAL"),
            _saw_body_event(
                tick=5,
                body_id="body-stranger-3",
                room="MEDBAY",
                victim_id="stranger",
            ),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        # alive is still a valid target; impostor stalks toward ELECTRICAL.
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ELECTRICAL"

    def test_confirmed_dead_from_bodies_raises_on_missing_victim_id(self) -> None:
        # R-4: the ValueError guard at ``impostor_policy.py::_confirmed_dead_from_bodies``
        # is the boundary-contract check after the body-id regex was
        # retired. Pin the branch so a future change to the ``saw_body``
        # payload shape cannot silently disable confirmed-dead pruning.
        # The ``_saw_body_event`` helper types ``victim_id: str`` and so
        # cannot reach this branch — construct the event directly.
        malformed = EpisodicEvent(
            tick=0,
            type=EVENT_SAW_BODY,
            payload={"body_id": "body-victim-0", "room": "MEDBAY"},
            provenance=PROVENANCE_OBSERVED,
        )

        with pytest.raises(ValueError, match="victim_id"):
            ImpostorPolicy._confirmed_dead_from_bodies((malformed,))

    def test_confirmed_dead_from_bodies_raises_on_non_string_victim_id(self) -> None:
        # The guard also rejects a non-string ``victim_id`` -- the only
        # contract the policy accepts is "string player id".
        malformed = EpisodicEvent(
            tick=0,
            type=EVENT_SAW_BODY,
            payload={"body_id": "body-victim-0", "room": "MEDBAY", "victim_id": None},
            provenance=PROVENANCE_OBSERVED,
        )

        with pytest.raises(ValueError, match="victim_id"):
            ImpostorPolicy._confirmed_dead_from_bodies((malformed,))


class TestImpostorVentCover:
    """Task 11.1 (DESIGN.md §1.3, §3.4; report-vent-escape-lab.md).

    POST-KILL VENT-ENTER: the COVER branch vents to hide the post-kill sighting
    trail when a vent sits in the body's room and no non-teammate witness is
    co-present this tick; otherwise it keeps the move-away fallback. ``MEDBAY``,
    ``ADMIN`` and ``ELECTRICAL`` carry vents in ``_public_map``; ``CAFETERIA``
    deliberately does not.
    """

    def test_vent_enter_fires_when_alone_with_body_in_vent_room(self) -> None:
        # Body in MEDBAY (a vent room), impostor alone: VENT to hide the trail
        # instead of walking away.
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY"),
            _cooldown_event(tick=10, cooldown=8),
            _saw_body_event(tick=10, body_id="body-v-10", room="MEDBAY", victim_id="v"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, VentIntent)
        assert intent.payload.vent_id == "MEDBAY_VENT"
        assert intent.actor == "imp"

    def test_vent_enter_suppressed_when_witness_co_present(self) -> None:
        # A non-teammate witness shares the body room: a vent and a walk are equal
        # exposure (and a vent would add a heard_vent_use tell), so the impostor
        # falls back to the move-away. MEDBAY's only neighbor is CAFETERIA.
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY"),
            _cooldown_event(tick=10, cooldown=8),
            _saw_player_event(tick=10, player_id="witness", room="MEDBAY"),
            _saw_body_event(tick=10, body_id="body-v-10", room="MEDBAY", victim_id="v"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    def test_vent_enter_skipped_when_no_vent_in_room(self) -> None:
        # The body sits in CAFETERIA, which has no vent: the impostor keeps the
        # plain move-away (alphabetically-first neighbor ADMIN).
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=8),
            _saw_body_event(
                tick=10, body_id="body-v-10", room="CAFETERIA", victim_id="v"
            ),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"

    def test_fellow_impostor_does_not_count_as_vent_witness(self) -> None:
        # A co-located fellow impostor is no witness, exactly as in the kill
        # gate: the impostor still vents away from the body.
        store = _store_with(
            _self_state_event(tick=10, room="MEDBAY", fellow_impostor_ids=("p-2",)),
            _cooldown_event(tick=10, cooldown=8),
            _saw_player_event(tick=10, player_id="p-2", room="MEDBAY"),
            _saw_body_event(tick=10, body_id="body-v-10", room="MEDBAY", victim_id="v"),
        )
        policy = ImpostorPolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, VentIntent)
        assert intent.payload.vent_id == "MEDBAY_VENT"

    def test_non_teammate_witness_present_raises_on_missing_player_id(self) -> None:
        # Boundary contract (no silent guess), mirroring the other saw_player
        # scanners: a current-tick saw_player missing its player_id is rejected.
        malformed = EpisodicEvent(
            tick=10,
            type=EVENT_SAW_PLAYER,
            payload={"room": "MEDBAY", "action": None},
            provenance=PROVENANCE_OBSERVED,
        )

        with pytest.raises(ValueError, match="player_id"):
            ImpostorPolicy._non_teammate_witness_present(
                (malformed,), own_room="MEDBAY", fellow_impostor_ids=frozenset()
            )


class TestImpostorVentExit:
    """Task 11.1 (DESIGN.md §1.3, §3.4): the in-vent vent-exit branch.

    An ``in_vent`` impostor takes the highest-priority branch and exits toward an
    isolated / non-body room. All tie-breaks are id/room-sorted and replay-stable,
    and an in-vent impostor always has an exit (never pathologically stuck).
    """

    def test_in_vent_exits_toward_best_isolated_target(self) -> None:
        # In ADMIN's vent with the best isolated target last seen in MEDBAY: of
        # the connected vents (ELECTRICAL_VENT, MEDBAY_VENT), MEDBAY_VENT is the
        # one whose room is the target's, so it is the closest.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", in_vent=True),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, VentIntent)
        assert intent.payload.vent_id == "MEDBAY_VENT"

    def test_in_vent_exit_avoids_a_body_room(self) -> None:
        # The target is in MEDBAY but a body is there too: MEDBAY_VENT is dropped
        # as a body room and the impostor exits via the next body-free connected
        # vent (ELECTRICAL_VENT) instead of surfacing onto the corpse.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", in_vent=True),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
            _saw_body_event(tick=10, body_id="body-x-10", room="MEDBAY", victim_id="x"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, VentIntent)
        assert intent.payload.vent_id == "ELECTRICAL_VENT"

    def test_in_vent_exit_is_alphabetical_when_no_target(self) -> None:
        # No sightings: deterministic fall-back to the alphabetically-first
        # connected vent (ELECTRICAL_VENT < MEDBAY_VENT).
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", in_vent=True),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, VentIntent)
        assert intent.payload.vent_id == "ELECTRICAL_VENT"

    def test_in_vent_with_no_connected_vents_exits_in_place(self) -> None:
        # Stuck-guard: a current vent with no connections still yields an exit
        # (in place via the current vent), so the impostor is never trapped.
        public_map = _public_map(
            vent_rooms={"ADMIN_VENT": "ADMIN"},
            vent_graph={"ADMIN_VENT": ()},
        )
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", in_vent=True),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, public_map)

        assert isinstance(intent, VentIntent)
        assert intent.payload.vent_id == "ADMIN_VENT"

    def test_in_vent_exit_takes_priority_over_kill(self) -> None:
        # A co-located, killable target does NOT pre-empt the exit: the in_vent
        # branch runs before the kill logic so the impostor first repositions.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", in_vent=True),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="ADMIN"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, VentIntent)

    def test_in_vent_exit_is_deterministic(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", in_vent=True),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
        )
        policy = ImpostorPolicy(agent_id="imp")
        public_map = _public_map()

        intents = [policy.decide(store, public_map) for _ in range(5)]

        for intent in intents:
            assert isinstance(intent, VentIntent)
            assert intent.payload.vent_id == "MEDBAY_VENT"


class TestImpostorToolkit1014:
    """The 10.14 toolkit, pinned cohesively (DESIGN.md §3.4, §4.5;
    audit-2026-06-13-1816 D-D-1/D-D-7, MECH-B-1).

    BLENDING: the dormant ``_idle`` do_task branch fires once the observation
    service surfaces a pretend ``pending_task_id`` (impostors own no real
    instance). The impostor now ROUTES TO / PERFORMS a task during idle ticks --
    including the post-kill cooldown window -- instead of waiting, collapsing the
    ~51% "never-tasks" wait-share toward crew levels.

    KILL DISCIPLINE: the producer gate emits a kill ONLY against a target
    co-located THIS tick, so a cross-room candidate degrades to move-toward
    (never a cross-room ActionRejected no-op), and a kill during cooldown is
    suppressed. Producer cross-room / cooldown kill emissions are 0 by
    construction; the residual engine ``same room`` rejections are the §3.4
    canonical intra-tick dodge, not a producer defect.
    """

    def test_blending_fills_post_kill_cooldown_idle_with_movement(self) -> None:
        # The wait-share reducer: on cooldown (the post-kill window) with no
        # target, a pretend task in another room makes the impostor STALK toward
        # it (blend) rather than wait -- this is the bulk of the reclaimed idle.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=3),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"

    def test_blending_performs_fake_do_task_when_in_task_room(self) -> None:
        # In the pretend task's room, the idle impostor EMITS a do_task -- a fake
        # task that renders as do_task and consumes the tick. (The engine rejects
        # it for owning no instance, so it makes no progress; that integrity
        # invariant is pinned engine-side in tests/observation/test_service.py.)
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=3),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, DoTaskIntent)
        assert intent.payload.task_id == "swipe_card"

    def test_kill_discipline_cross_room_candidate_degrades_to_move(self) -> None:
        # MECH-B-1: a kill candidate whose freshest sighting is a DIFFERENT room
        # never produces a cross-room kill emission -- the producer degrades to a
        # move-toward (stalk). Cooldown is 0, so this isolates the room gate.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="ELECTRICAL"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, KillIntent)
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ELECTRICAL"

    def test_kill_discipline_suppresses_kill_during_cooldown_and_blends(
        self,
    ) -> None:
        # D-D-7: a co-located target during cooldown yields NO kill emission. With
        # a pretend task the impostor blends in place (do_task) instead of leaking
        # a doomed kill intent that the engine would reject for cooldown.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=2),
            _saw_player_event(tick=10, player_id="victim", room="ADMIN"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, KillIntent)
        assert isinstance(intent, DoTaskIntent)
        assert intent.payload.task_id == "swipe_card"

    def test_cover_discipline_does_not_route_blend_into_a_body_room(self) -> None:
        # Cover discipline (Codex review): after a kill the impostor must not let
        # its pretend task drag it back onto the corpse. Here the impostor is on
        # cooldown in CAFETERIA with a pretend task in ADMIN, but a body is
        # visible in ADMIN -- routing there would oscillate against the COVER
        # interrupt and blow the sheltered alibi, so the impostor waits instead.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=3),
            _saw_body_event(tick=10, body_id="body-v-7", room="ADMIN", victim_id="v"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        # swipe_card lives in ADMIN (a body room): no move-toward, no do_task.
        assert isinstance(intent, WaitIntent)

    def test_blend_still_performs_when_body_is_in_a_different_room(self) -> None:
        # The gate is narrow: a body in some OTHER room (not the pretend task's)
        # does not block the blend. The impostor is in its sheltered task room
        # ADMIN (no body) and performs the fake task; the body in MEDBAY is
        # irrelevant to the routing/performing target.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", pending_task_id="swipe_card"),
            _cooldown_event(tick=10, cooldown=3),
            _saw_body_event(tick=10, body_id="body-v-7", room="MEDBAY", victim_id="v"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, DoTaskIntent)
        assert intent.payload.task_id == "swipe_card"


class TestImpostorSabotage:
    """Task 11.7 (DESIGN.md §3.4 impostor actions, §4.4 impostor FSM;
    report-vent-escape-lab.md is the 11.1 vent-wiring precedent).

    The impostor USES the task-gating lever: a new SABOTAGE branch below the
    in-vent exit and COVER-or-vent branches but above the kill/stalk block. It
    emits ``SabotageIntent("reactor")`` strategically -- only when the crew is at
    an imminent task win (``_crew_near_task_win``), only while no sabotage is
    active (``_active_sabotage``), and only when this completion level has not
    been sabotaged yet (``_sabotage_window_open``) -- so it never spams a sabotage
    per cooldown tick, never re-fires on a static repaired-but-near-win state (the
    sabotage/repair loop), yet does not forfeit the window if a higher-priority
    branch ran on the completion tick. An available kill (one this actor will
    actually emit), the in-vent exit, and COVER all still out-prioritize it; the
    decision is a pure, deterministic function of memory + ``PublicMapView``.

    ``_IMMINENT_CREW_WIN_COMPLETION`` is ~6/7, so at 14 total instances (the
    canonical 9p/2i roster) the lever arms at 12/14 and 13/14. The fraction
    (not a fixed remaining-count) keeps tiny rosters sane -- 3 or 6 instances
    never reach >=6/7 without already being complete, so the lever never fires
    there.
    """

    def test_emits_reactor_sabotage_when_crew_near_win_and_no_sabotage_active(
        self,
    ) -> None:
        # Sole impostor, no co-located target, cooldown free, crew one instance
        # from victory and no sabotage has run at this level: pull the lever.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"
        assert intent.actor == "imp"

    def test_does_not_emit_when_sabotage_already_active(self) -> None:
        # A sabotage is already active this tick: the active-guard suppresses a
        # second emission and the impostor falls through to idle.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(
                tick=10,
                tasks_completed=13,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="reactor",
                sabotage_is_gating=True,
            ),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, SabotageIntent)
        assert isinstance(intent, WaitIntent)

    def test_does_not_emit_when_crew_not_near_win(self) -> None:
        # Early game (2/14): far from a win, so the conservative predicate is
        # False -- no per-tick sabotage spam, the impostor just idles.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=2, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, SabotageIntent)
        assert isinstance(intent, WaitIntent)

    def test_does_not_emit_when_no_task_instance_remains(self) -> None:
        # Defensive: with every instance complete there is no win left to deny,
        # so the predicate is False even though "remaining (0) <= threshold".
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=14, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, SabotageIntent)
        assert isinstance(intent, WaitIntent)

    def test_threshold_arms_at_six_sevenths_completion(self) -> None:
        # Pins the documented anchor (_IMMINENT_CREW_WIN_COMPLETION ~ 6/7): at 14
        # instances 12/14 (>=6/7) arms the lever, 11/14 (<6/7) does not.
        policy = ImpostorPolicy(agent_id="imp")

        near = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=12, tasks_total=14),
        )
        far = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=11, tasks_total=14),
        )

        assert isinstance(policy.decide(near, _public_map()), SabotageIntent)
        assert not isinstance(policy.decide(far, _public_map()), SabotageIntent)

    def test_small_reference_rosters_never_arm_the_lever(self) -> None:
        # Roster-robustness: the flat 4p/1i determinism reference (3 instances at
        # tasks_per_crewmate=1, 6 at =2) can never reach >=6/7 without already
        # being complete, so the impostor never sabotages there even at the last
        # pre-win count. This is what keeps the short 4p/1i meeting/budget
        # integration games byte-identical (the lever is a 9p/2i-eval counterplay).
        policy = ImpostorPolicy(agent_id="imp")

        for completed, total in ((2, 3), (5, 6)):
            store = _store_with(
                _self_state_event(tick=10, room="CAFETERIA"),
                _cooldown_event(tick=10, cooldown=0),
                _global_status_event(
                    tick=10, tasks_completed=completed, tasks_total=total
                ),
            )

            assert not isinstance(policy.decide(store, _public_map()), SabotageIntent)

    def test_available_kill_pre_empts_sabotage(self) -> None:
        # A clean, co-located kill this actor will emit out-prioritizes the lever
        # even at the near-win edge: the impostor keeps hunting.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == "victim"

    def test_stalk_does_not_pre_empt_sabotage(self) -> None:
        # The only target is in another room (a STALK, not an available kill), so
        # the lever pre-empts the stalk to deny the imminent win first. The
        # impostor resumes hunting next tick (sabotage then active -> guarded).
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="MEDBAY"),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_witness_blocked_kill_opportunity_still_sabotages(self) -> None:
        # A co-located target with a co-present witness is NOT an available kill
        # (the kill block would wait), so the lever may still fire near a win --
        # strictly better than waiting while the crew finishes its tasks.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="witness", room="CAFETERIA"),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_in_vent_exit_pre_empts_sabotage(self) -> None:
        # The highest-priority in-vent exit runs first: a vented impostor
        # repositions before it would ever consider the lever, even at the
        # near-win edge.
        store = _store_with(
            _self_state_event(tick=10, room="ADMIN", in_vent=True),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, VentIntent)
        assert not isinstance(intent, SabotageIntent)

    def test_cover_pre_empts_sabotage(self) -> None:
        # A body in the impostor's own room takes the COVER branch (move-away
        # from CAFETERIA, which has no vent) before the SABOTAGE branch, even at
        # the near-win edge.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=8),
            _saw_body_event(
                tick=10, body_id="body-v-10", room="CAFETERIA", victim_id="v"
            ),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "ADMIN"
        assert not isinstance(intent, SabotageIntent)

    def test_multi_impostor_sabotages_without_fellow_coordination(self) -> None:
        # Multi-impostor: a co-located fellow is no witness and the sabotage
        # trigger needs no coordination tie-break (unlike kill). p-1 still emits
        # the lever; an engine-side dedup handles a same-tick second emission.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", fellow_impostor_ids=("p-2",)),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p-2", room="CAFETERIA"),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="p-1")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_decision_tracks_only_global_status(self) -> None:
        # Same self/cooldown, differing only in the global_status counts: the
        # near-win one sabotages, the far one idles -- the trigger is a pure
        # function of the observed global_status.
        policy = ImpostorPolicy(agent_id="imp")
        movement = (
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        near = _store_with(
            *movement,
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        far = _store_with(
            *movement,
            _global_status_event(tick=10, tasks_completed=3, tasks_total=14),
        )

        assert isinstance(policy.decide(near, _public_map()), SabotageIntent)
        assert isinstance(policy.decide(far, _public_map()), WaitIntent)

    def test_repeated_decide_calls_are_deterministic(self) -> None:
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")
        public_map = _public_map()

        intents = [policy.decide(store, public_map) for _ in range(5)]

        for intent in intents:
            assert isinstance(intent, SabotageIntent)
            assert intent.payload.kind == "reactor"
            assert intent.actor == "imp"

    def test_does_not_refire_after_repair_without_new_progress(self) -> None:
        # Codex P1 (sabotage/repair loop): the crew reached 12/14 and the impostor
        # sabotaged; the gating reactor FROZE the count, so once the crew repairs
        # the latest global_status reads the SAME 12/14 with sabotage now inactive.
        # The near-win + not-active guards alone would re-fire instantly (the
        # loop); the progress edge suppresses it because no NEW completion landed.
        store = _store_with(
            _global_status_event(tick=8, tasks_completed=12, tasks_total=14),
            _global_status_event(
                tick=9,
                tasks_completed=12,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="reactor",
                sabotage_is_gating=True,
            ),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=12, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert not isinstance(intent, SabotageIntent)
        assert isinstance(intent, WaitIntent)

    def test_refires_only_on_a_genuinely_fresh_completion(self) -> None:
        # The flip side of the loop fix: after a repair, once the crew makes a
        # GENUINELY new completion (12 -> 13) the lever re-arms. Sabotage is thus
        # tied to crew progress and bounded by the remaining completions (<=2 for
        # the 9p/2i roster), not an unbounded per-tick loop.
        store = _store_with(
            _global_status_event(
                tick=9,
                tasks_completed=12,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="reactor",
                sabotage_is_gating=True,
            ),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_window_stays_open_after_a_busy_completion_tick(self) -> None:
        # Codex P2 (missed window): the crew reached 13/14 on a tick the impostor
        # spent on a higher-priority action (no sabotage started). The window must
        # NOT be forfeited just because no completion lands THIS tick: with the
        # count still 13/14, no sabotage ever run, and no kill, a later free tick
        # still fires the lever.
        store = _store_with(
            _global_status_event(tick=8, tasks_completed=12, tasks_total=14),
            _global_status_event(tick=9, tasks_completed=13, tasks_total=14),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_deferred_kill_does_not_suppress_sabotage(self) -> None:
        # Codex P2 (deferred kill): p-2 (higher id) has cooldown 0 and a co-located
        # crewmate, but a co-located lower-id fellow p-1 means p-2 would DEFER the
        # kill -- and cooldowns are per-actor, so p-1 may not kill either. p-2 must
        # not waste the tick on Wait: with no kill it will actually emit, it pulls
        # the reactor lever at the near-win edge instead.
        store = _store_with(
            _self_state_event(tick=10, room="CAFETERIA", fellow_impostor_ids=("p-1",)),
            _cooldown_event(tick=10, cooldown=0),
            _saw_player_event(tick=10, player_id="p-1", room="CAFETERIA"),
            _saw_player_event(tick=10, player_id="victim", room="CAFETERIA"),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="p-2")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_re_arms_when_a_crew_death_drops_the_task_total(self) -> None:
        # Codex P2 (denominator drop): the impostor reactor-gated at 12/14, then a
        # crewmate died with an incomplete task -- removing that instance drops the
        # total to 13 (DESIGN.md §3.5), so the repaired state is 12/13: the crew is
        # now ONE task from a win with no completion. Keying the re-arm on
        # REMAINING (not completed) re-opens the window so the lever fires again.
        store = _store_with(
            _global_status_event(
                tick=9,
                tasks_completed=12,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="reactor",
                sabotage_is_gating=True,
            ),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=12, tasks_total=13),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_non_gating_lights_does_not_close_the_reactor_window(self) -> None:
        # Codex P2 (non-gating in the re-arm gate): a lights sabotage (non-gating
        # -- it does not freeze the task race or deny the win) ran at 12/14 and was
        # repaired. It must NOT consume the reactor's window: with the crew still
        # at 12/14 and no GATING sabotage ever run, the impostor still fires.
        store = _store_with(
            _global_status_event(
                tick=9,
                tasks_completed=12,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="lights",
                sabotage_is_gating=False,
            ),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
            _global_status_event(tick=10, tasks_completed=12, tasks_total=14),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, SabotageIntent)
        assert intent.payload.kind == "reactor"

    def test_sabotage_window_open_when_never_sabotaged(self) -> None:
        events = (_global_status_event(tick=10, tasks_completed=13, tasks_total=14),)

        assert ImpostorPolicy._sabotage_window_open(events) is True

    def test_sabotage_window_open_ignores_a_non_gating_sabotage(self) -> None:
        # Only GATING sabotages close the window: an active lights observation does
        # not register, so the window stays open at the same count.
        events = (
            _global_status_event(
                tick=9,
                tasks_completed=12,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="lights",
                sabotage_is_gating=False,
            ),
            _global_status_event(tick=10, tasks_completed=12, tasks_total=14),
        )

        assert ImpostorPolicy._sabotage_window_open(events) is True

    def test_sabotage_window_closed_at_an_already_sabotaged_level(self) -> None:
        # Sabotaged at 12 then repaired; the frozen count never exceeds 12, so the
        # window stays closed (the loop fix).
        events = (
            _global_status_event(
                tick=9,
                tasks_completed=12,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="reactor",
                sabotage_is_gating=True,
            ),
            _global_status_event(tick=10, tasks_completed=12, tasks_total=14),
        )

        assert ImpostorPolicy._sabotage_window_open(events) is False

    def test_sabotage_window_reopens_above_the_sabotaged_level(self) -> None:
        # Once the crew completes a genuinely higher level (12 -> 13) the window
        # re-opens -- sabotage is bounded by the remaining completions.
        events = (
            _global_status_event(
                tick=9,
                tasks_completed=12,
                tasks_total=14,
                sabotage_active=True,
                sabotage_kind="reactor",
                sabotage_is_gating=True,
            ),
            _global_status_event(tick=10, tasks_completed=13, tasks_total=14),
        )

        assert ImpostorPolicy._sabotage_window_open(events) is True

    def test_active_sabotage_absent_global_status_is_false(self) -> None:
        # No global_status row (the pre-11.5 hand-built shape used across the
        # other suites): "no observed sabotage", not a raise.
        events = (_cooldown_event(tick=10, cooldown=0),)

        assert ImpostorPolicy._active_sabotage(events) is False

    def test_active_sabotage_raises_on_non_bool(self) -> None:
        # Boundary contract: a present-but-non-bool sabotage_active is rejected.
        malformed = EpisodicEvent(
            tick=10,
            type=EVENT_GLOBAL_STATUS,
            payload={"sabotage_active": "yes"},
            provenance=PROVENANCE_INFERRED,
        )

        with pytest.raises(ValueError, match="sabotage_active"):
            ImpostorPolicy._active_sabotage((malformed,))

    def test_crew_near_task_win_raises_on_non_int_counts(self) -> None:
        # Boundary contract: present-but-non-int task counts are rejected.
        malformed = EpisodicEvent(
            tick=10,
            type=EVENT_GLOBAL_STATUS,
            payload={"tasks_completed": "lots", "tasks_total": 14},
            provenance=PROVENANCE_INFERRED,
        )

        with pytest.raises(ValueError, match="task counts"):
            ImpostorPolicy._crew_near_task_win((malformed,))


class TestRankedTargetsAccessor:
    """The read-only ranking accessor an offline instrument reads.

    ``ranked_targets`` exposes the ordering ``decide`` acts on without a second
    implementation of the scoring; these tests pin that the two agree, so the
    accessor cannot drift into measuring a different policy.
    """

    def test_ranking_matches_the_target_decide_acts_on(self) -> None:
        policy = ImpostorPolicy(agent_id="p-4")
        memory = MemoryStore()
        for event in (
            _saw_player_event(tick=9, player_id="p-1", room="ELECTRICAL"),
            _saw_player_event(tick=9, player_id="p-6", room="ADMIN"),
            _self_state_event(tick=9, room="ADMIN"),
            _cooldown_event(tick=9, cooldown=0),
        ):
            memory.append(event)

        ranking = policy.ranked_targets(memory, _public_map())

        # Proximity is a tier below the score, so the co-located p-6 now heads a
        # 1.0/1.0 tie the id alone used to give to the remote p-1 -- and the intent
        # decide emits is the kill, read off the same accessor an instrument reads.
        assert [target.player_id for target in ranking] == ["p-6", "p-1"]
        assert ranking[0].score == 1.0 and ranking[0].co_present == 0
        intent = policy.decide(memory, _public_map())
        assert isinstance(intent, KillIntent)
        assert intent.payload.target == "p-6"

    def test_ranking_drops_a_fellow_and_a_confirmed_corpse(self) -> None:
        policy = ImpostorPolicy(agent_id="p-4")
        memory = MemoryStore()
        for event in (
            _saw_player_event(tick=9, player_id="p-1", room="ADMIN"),
            _saw_player_event(tick=9, player_id="p-6", room="ADMIN"),
            _saw_body_event(
                tick=9, body_id="body-p-1-8", room="ADMIN", victim_id="p-1"
            ),
            _self_state_event(tick=9, room="ADMIN", fellow_impostor_ids=("p-6",)),
            _cooldown_event(tick=9, cooldown=0),
        ):
            memory.append(event)

        assert policy.ranked_targets(memory, _public_map()) == ()

    def test_ranking_is_empty_without_the_rows_decide_requires(self) -> None:
        policy = ImpostorPolicy(agent_id="p-4")
        assert policy.ranked_targets(MemoryStore(), _public_map()) == ()

        no_cooldown = MemoryStore()
        no_cooldown.append(_self_state_event(tick=3, room="ADMIN"))
        assert policy.ranked_targets(no_cooldown, _public_map()) == ()


class TestImpostorFreeKillScan:
    """The kill seam scans the ranking instead of testing only its head (C-3)."""

    @staticmethod
    def _store(*, remote: str, victim: str) -> MemoryStore:
        # ``remote`` is alone in ELECTRICAL and ``victim`` is alone in the
        # impostor's own room: both score 1.0, so before the repair whichever id
        # sorted first took the ranking and a remote head walked the kill away.
        return _store_with(
            _self_state_event(tick=9, room="ADMIN"),
            _cooldown_event(tick=9, cooldown=0),
            _saw_player_event(tick=9, player_id=remote, room="ELECTRICAL"),
            _saw_player_event(tick=9, player_id=victim, room="ADMIN"),
        )

    @pytest.mark.parametrize(("remote", "victim"), [("p-1", "p-6"), ("p-6", "p-1")])
    def test_a_free_co_located_victim_is_killed_from_either_id_order(
        self, remote: str, victim: str
    ) -> None:
        policy = ImpostorPolicy(agent_id="p-4")

        intent = policy.decide(self._store(remote=remote, victim=victim), _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == victim

    def test_a_witnessed_co_located_target_is_still_not_killed(self) -> None:
        # The scan is a FREE-kill scan, not an any-co-located scan: two crewmates
        # in our room witness each other, so the seam finds nothing and holds.
        store = _store_with(
            _self_state_event(tick=9, room="ADMIN"),
            _cooldown_event(tick=9, cooldown=0),
            _saw_player_event(tick=9, player_id="p-1", room="ADMIN"),
            _saw_player_event(tick=9, player_id="p-6", room="ADMIN"),
        )
        policy = ImpostorPolicy(agent_id="p-4")

        assert isinstance(policy.decide(store, _public_map()), WaitIntent)

    @pytest.mark.parametrize(("remote", "victim"), [("p-1", "p-6"), ("p-6", "p-1")])
    def test_sabotage_never_fires_on_a_tick_carrying_a_free_kill(
        self, remote: str, victim: str
    ) -> None:
        # The crew is one instance from a task win, so the reactor lever is armed;
        # the shared free-kill scan backs the guard, so the kill still wins the
        # tick whichever way the two 1.0-scoring ids sort.
        store = _store_with(
            _self_state_event(tick=9, room="ADMIN"),
            _cooldown_event(tick=9, cooldown=0),
            _global_status_event(tick=9, tasks_completed=13, tasks_total=14),
            _saw_player_event(tick=9, player_id=remote, room="ELECTRICAL"),
            _saw_player_event(tick=9, player_id=victim, room="ADMIN"),
        )
        policy = ImpostorPolicy(agent_id="p-4")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, KillIntent)
        assert intent.payload.target == victim

    def test_sabotage_still_fires_when_the_ranking_carries_no_free_kill(self) -> None:
        # The perturbation that proves the guard is a guard and not a blanket
        # suppression: move the victim out of our room and the lever fires.
        store = _store_with(
            _self_state_event(tick=9, room="ADMIN"),
            _cooldown_event(tick=9, cooldown=0),
            _global_status_event(tick=9, tasks_completed=13, tasks_total=14),
            _saw_player_event(tick=9, player_id="p-1", room="ELECTRICAL"),
            _saw_player_event(tick=9, player_id="p-6", room="MEDBAY"),
        )
        policy = ImpostorPolicy(agent_id="p-4")

        assert isinstance(policy.decide(store, _public_map()), SabotageIntent)


class TestImpostorEjectionBarrier:
    """No player ejected at a concluded meeting can occupy the ranking (G-12)."""

    def test_the_marker_string_matches_its_producer(self) -> None:
        # The policy mirrors the store's constant rather than importing it; this
        # is the pin that keeps the mirror honest.
        assert _MEETING_BOUNDARY_EVENT == _EVENT_MEETING_BOUNDARY

    def test_a_sighting_before_the_marker_cannot_rank(self) -> None:
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="ejected", room="MEDBAY"),
            _meeting_boundary_event(tick=6),
            _self_state_event(tick=6, room="CAFETERIA"),
            _cooldown_event(tick=6, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        assert policy.ranked_targets(store, _public_map()) == ()
        assert isinstance(policy.decide(store, _public_map()), WaitIntent)

    def test_the_same_sighting_ranks_without_the_marker(self) -> None:
        # The planted counter-case: drop the marker and the identical lead is a
        # live stalk target, so the barrier is what removed it.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="ejected", room="MEDBAY"),
            _self_state_event(tick=6, room="CAFETERIA"),
            _cooldown_event(tick=6, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "MEDBAY"

    def test_a_sighting_at_or_after_the_marker_still_ranks(self) -> None:
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="survivor", room="MEDBAY"),
            _meeting_boundary_event(tick=6),
            _self_state_event(tick=6, room="CAFETERIA"),
            _cooldown_event(tick=6, cooldown=0),
            _saw_player_event(tick=6, player_id="survivor", room="MEDBAY"),
        )
        policy = ImpostorPolicy(agent_id="imp")

        ranking = policy.ranked_targets(store, _public_map())

        assert [target.player_id for target in ranking] == ["survivor"]

    @pytest.mark.slow
    def test_seed_36_tick_50_kills_instead_of_ranking_the_ejected_player(self) -> None:
        # The demonstrable case (A/verdicts.md claim 12): p-6 was ejected at the
        # tick-35 meeting boundary and its tick-24 sighting still heads the FROZEN
        # scoring static -- the one the ES option enumerators call, which this
        # repair does not touch. The decision ranking drops it and the co-located,
        # isolated, cooldown-0 p-7 is killed instead.
        decision = next(
            row
            for row in reconstruct_impostor_decisions(_SAMPLES_9P2I, seed=36)
            if row.tick == 50 and row.actor == "p-2"
        )
        frozen = _frozen_static_ranking(decision.memory)

        assert frozen[0].player_id == "p-6"
        assert [target.player_id for target in decision.ranked] == ["p-7", "p-9"]
        assert isinstance(decision.intent, KillIntent)
        assert decision.intent.payload.target == "p-7"
        # The recording walked away instead; that is the kill the defect cost.
        assert decision.recorded["type"] == "move"

    @pytest.mark.slow
    def test_seed_31_never_ranks_the_ejected_p1_after_its_meeting(self) -> None:
        # The window the review attributed to a dead subject (C-4 / G-12): p-1
        # heads p-5's ranking up to the meeting and never appears in one again.
        rows = [
            row
            for row in reconstruct_impostor_decisions(_SAMPLES_9P2I, seed=31)
            if row.actor == "p-5"
        ]
        headed = [
            row.tick for row in rows if row.ranked and row.ranked[0].player_id == "p-1"
        ]
        after = [
            row.tick
            for row in rows
            if row.tick >= 14 and any(t.player_id == "p-1" for t in row.ranked)
        ]

        assert headed and max(headed) < 14
        assert after == []


class TestImpostorRefutedSighting:
    """A sighting the impostor has since stood in and disproved is dropped (C-4)."""

    def test_standing_in_the_room_without_the_subject_drops_the_lead(self) -> None:
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="ghost", room="MEDBAY"),
            _self_state_event(tick=8, room="MEDBAY", pending_task_id="swipe_card"),
            _cooldown_event(tick=8, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        assert policy.ranked_targets(store, _public_map()) == ()
        # The fall-through lands in the pretend-task blend, not another walk back.
        intent = policy.decide(store, _public_map())
        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "CAFETERIA"

    def test_the_same_lead_survives_a_visit_to_a_different_room(self) -> None:
        # The planted counter-case: only the sighting's OWN room refutes it.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="ghost", room="MEDBAY"),
            _self_state_event(tick=8, room="ELECTRICAL"),
            _cooldown_event(tick=8, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        ranking = policy.ranked_targets(store, _public_map())

        assert [target.player_id for target in ranking] == ["ghost"]

    def test_the_drop_survives_leaving_the_room(self) -> None:
        # Permanence is the whole point: a refutation that lapsed on leaving would
        # re-create the A-B pendulum it exists to remove.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="ghost", room="MEDBAY"),
            _self_state_event(tick=8, room="MEDBAY"),
            _cooldown_event(tick=8, cooldown=0),
            _self_state_event(tick=9, room="CAFETERIA"),
            _cooldown_event(tick=9, cooldown=0),
            _self_state_event(tick=12, room="CAFETERIA"),
            _cooldown_event(tick=12, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        assert policy.ranked_targets(store, _public_map()) == ()

    def test_seeing_the_subject_again_clears_the_refutation(self) -> None:
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="ghost", room="MEDBAY"),
            _self_state_event(tick=8, room="MEDBAY"),
            _cooldown_event(tick=8, cooldown=0),
            _self_state_event(tick=9, room="CAFETERIA"),
            _cooldown_event(tick=9, cooldown=0),
            _saw_player_event(tick=9, player_id="ghost", room="ELECTRICAL"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        ranking = policy.ranked_targets(store, _public_map())

        assert [target.player_id for target in ranking] == ["ghost"]

    @pytest.mark.slow
    def test_seed_7_refutes_a_living_lead_and_keeps_it_dropped(self) -> None:
        # The demonstrable case for the LIVING half of C-4, the half the ejection
        # barrier does not cover: p-2 stands in WEST_HALL at tick 13 without seeing
        # p-1 there, so p-1 leaves the ranking -- and stays out at tick 14, after
        # p-2 has moved on to ADMIN.
        rows = {
            row.tick: row
            for row in reconstruct_impostor_decisions(_SAMPLES_9P2I, seed=7)
            if row.actor == "p-2" and row.tick in (13, 14)
        }
        for tick in (13, 14):
            frozen = _frozen_static_ranking(rows[tick].memory)
            assert frozen[0].player_id == "p-1" and frozen[0].room == "WEST_HALL"
            assert all(target.player_id != "p-1" for target in rows[tick].ranked)
        assert _own_room(rows[13].memory) == "LABS"
        assert _own_room(rows[14].memory) == "LABS"


class TestCommittedCorpusTargetingPins:
    """The I-11 co-intervention cells over the committed bytes, before and after.

    The "before" is frozen (``eval.evidence_honesty.RATIFIED_I11_CELLS``): it is the
    measurement of the policy the recorded bytes were produced with, and that policy
    left the tree with this repair, so nothing can recompute it. The "after" is the
    live fold over the SAME frozen bytes -- a per-decision counterfactual, no
    re-simulation -- which is why its ``reconstruction_mismatches`` is non-zero and
    is itself the size of the behaviour change. No ratified bar rides I-11; it is a
    secondary, observed-not-gated cell (memo section 11, 2026-08-20).
    """

    @staticmethod
    def _targeting(name: str) -> ImpostorTargetingCells:
        return compute_evidence_honesty(_REPLAYS / name).impostor_targeting

    @pytest.mark.slow
    def test_free_zero_witness_kills_declined_pins(self) -> None:
        before = RATIFIED_I11_CELLS["samples/9p2i"]
        after = self._targeting("samples/9p2i")

        # Before: 190/415 = 45.8% of the policy's own legal, zero-witness kill
        # opportunities declined, 168 of them purely on the id tie-break.
        assert (before.free_kills_declined, before.free_kill_opportunities) == (
            190,
            415,
        )
        assert before.decline_reason_ranking == 168
        assert before.decline_reason_fellow_defer == 15
        assert before.decline_reason_cover == 7
        # After: 35/415 = 8.4%, under the < 10% bar, and every survivor lands in a
        # named legitimate branch -- 28 fellow-impostor defers and 7 COVER bodies.
        # The contract predicted 22 (15 + 7). The 13-decision difference is the
        # fellow-defer population the OLD seam never reached: those declines were
        # attributed to the ranking because the ranking's head was not the victim,
        # and with the head no longer deciding they resolve to the deliberate defer
        # they always were. Predicted residual and measured residual differ; the
        # measured one is the pin.
        assert (
            after.free_kills_declined.numerator,
            after.free_kills_declined.denominator,
        ) == (8, 228)
        assert after.free_kills_declined.rate is not None
        assert after.free_kills_declined.rate < 0.10
        assert after.decline_reason_ranking == 0
        assert after.decline_reason_other == 0
        assert after.decline_reason_fellow_defer == 6
        assert after.decline_reason_cover == 2
        # The reconstruction still walks every decision the recording holds.
        assert after.decisions_reconstructed == before.decisions_reconstructed == 2461
        assert after.in_vent_decisions == before.in_vent_decisions == 130

    @pytest.mark.slow
    def test_no_recorded_kill_is_lost(self) -> None:
        # The loss guard: a repair that gains free kills must not silently drop one
        # the recording made. Every recorded kill state re-emits the same intent.
        for name, recorded_kills in (
            ("samples/9p2i", 225),
            ("ml_corpus/9p2i", 640),
            ("samples/4p1i", 64),
            ("ml_corpus/4p1i", 57),
        ):
            cells = self._targeting(name)
            assert cells.recorded_kill_decisions == recorded_kills
            assert cells.recorded_kills_reproduced == recorded_kills

    @pytest.mark.slow
    def test_ghost_top_decisions_pin_on_every_set(self) -> None:
        names = ("samples/9p2i", "ml_corpus/9p2i", "samples/4p1i", "ml_corpus/4p1i")
        before = {name: RATIFIED_I11_CELLS[name] for name in names}
        after = {name: self._targeting(name) for name in names}

        # Before: 303/2461, 555/6663, 0/632, 0/579 over 10,335 decisions.
        assert [
            (before[name].ghost_top, before[name].decisions_reconstructed)
            for name in names
        ] == [(303, 2461), (555, 6663), (0, 632), (0, 579)]
        assert sum(before[name].decisions_reconstructed for name in names) == 10_335
        assert before["samples/9p2i"].ghost_top_ejected == 222
        assert before["samples/9p2i"].ghost_top_unseen_death == 81
        # After: the whole ejected sub-population is gone on both 9p2i sets, and
        # the partner's-unseen-victim residual the ruling excludes a kill-knowledge
        # channel for falls with it because a cross-meeting lead cannot rank either.
        assert [
            (after[name].ghost_top.numerator, after[name].ghost_top.denominator)
            for name in names
        ] == [(5, 1750), (4, 5528), (0, 551), (0, 529)]
        assert after["samples/9p2i"].ghost_top_ejected == 0
        assert after["samples/9p2i"].ghost_top_unseen_death == 5
        assert after["ml_corpus/9p2i"].ghost_top_ejected == 0
        # 4p1i was clean on both sets before and stays clean: the defect was a
        # 9p2i-roster phenomenon, which is to say it biased the eval baseline.
        assert after["samples/4p1i"].ghost_top_ejected == 0

    @pytest.mark.slow
    def test_ghost_top_no_longer_blocks_a_kill(self) -> None:
        before = RATIFIED_I11_CELLS["samples/9p2i"]
        after = self._targeting("samples/9p2i")

        # Before: 30 legal zero-witness kills declined while an already-ejected
        # player headed the ranking (A/verdicts.md claim 12).
        assert before.kills_blocked_by_ghost_top == 30
        assert after.kills_blocked_by_ghost_top == 0
        assert after.games_with_a_blocked_kill == 0

    @pytest.mark.slow
    def test_the_counterfactual_labels_itself_and_counts_its_own_size(self) -> None:
        # The fold is no longer a reproduction of the recorded policy and says so:
        # the block carries the mode that produced it and the mismatch count IS the
        # behaviour change, not a broken recording.
        after = self._targeting("samples/9p2i")

        assert after.policy_mode == LIVE_POLICY_FOLD
        assert RATIFIED_I11_CELLS["samples/9p2i"].policy_mode == RATIFIED_BASELINE
        assert after.reconstruction_mismatches == 0  # was 419
