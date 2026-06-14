from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
)
from agents.tactical.impostor_policy import ImpostorPolicy
from observation.action_intent import (
    DoTaskIntent,
    KillIntent,
    MoveIntent,
    WaitIntent,
)
from observation.public_map import PublicMapView, RoomId


def _public_map(
    *,
    rooms: tuple[RoomId, ...] = ("ADMIN", "CAFETERIA", "ELECTRICAL", "MEDBAY"),
    neighbors: Mapping[RoomId, tuple[RoomId, ...]] | None = None,
    task_locations: Mapping[str, RoomId] | None = None,
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
        vent_graph={},
        vent_rooms={},
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
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "room": room,
        "role": role,
        "pending_task_id": pending_task_id,
        "fellow_impostor_ids": fellow_impostor_ids,
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
        # Both players last seen alone in different rooms (score == 1.0
        # each). Tie-break on sorted player_id chooses "alpha" over "beta".
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

        intent = policy.decide(store, _public_map())

        assert isinstance(intent, MoveIntent)
        assert intent.payload.to_room == "MEDBAY"

    def test_stalk_prefers_more_isolated_target_over_witnessed_one(self) -> None:
        # alpha was alone in ELECTRICAL at tick 5; beta was seen in MEDBAY
        # at tick 8 alongside gamma, so beta has lower isolation. Even
        # though beta's sighting is more recent, alpha's higher score wins.
        store = _store_with(
            _self_state_event(tick=5, room="CAFETERIA"),
            _cooldown_event(tick=5, cooldown=0),
            _saw_player_event(tick=5, player_id="alpha", room="ELECTRICAL"),
            _self_state_event(tick=8, room="CAFETERIA"),
            _cooldown_event(tick=8, cooldown=0),
            _saw_player_event(tick=8, player_id="beta", room="MEDBAY"),
            _saw_player_event(tick=8, player_id="gamma", room="MEDBAY"),
            _self_state_event(tick=10, room="CAFETERIA"),
            _cooldown_event(tick=10, cooldown=0),
        )
        policy = ImpostorPolicy(agent_id="imp")

        intent = policy.decide(store, _public_map())

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
