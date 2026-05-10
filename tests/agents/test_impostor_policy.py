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
) -> EpisodicEvent:
    payload: dict[str, Any] = {
        "room": room,
        "role": role,
        "pending_task_id": pending_task_id,
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


def _saw_body_event(*, tick: int, body_id: str, room: RoomId) -> EpisodicEvent:
    return EpisodicEvent(
        tick=tick,
        type=EVENT_SAW_BODY,
        payload={"body_id": body_id, "room": room},
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
            _saw_body_event(tick=10, body_id="victim-body", room="CAFETERIA"),
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
            _saw_body_event(tick=10, body_id="other-body", room="CAFETERIA"),
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
            _saw_body_event(tick=10, body_id="far-body", room="MEDBAY"),
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
