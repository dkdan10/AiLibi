"""Impostor tactical policy (DESIGN.md §4.4).

Implements the deterministic impostor finite-state machine:

    IDLE -> STALK -> KILL_OPPORTUNITY -> KILL -> COVER

Target selection follows the implementation hint:

    score = isolation * (1 - witness_risk) * (cooldown == 0)

For every player ever observed, the score is computed at that player's
*most recent* ``saw_player`` sighting:

* ``co_present``  - count of OTHER players seen in the same room at the
  same sighting tick (``saw_player`` events never include the impostor
  itself, so the candidate is the only entry to subtract).
* ``isolation``   - ``1 / (1 + co_present)`` (higher is more alone).
* ``witness_risk`` - ``co_present / (1 + co_present)`` (higher is riskier).
* ``cooldown == 0`` contributes a binary ``1.0 / 0.0`` multiplier.

The policy is stateless: every decision is a pure function of the
agent's :class:`MemoryStore` and the :class:`PublicMapView`. Tie-
breakers use sorted ids so replays are byte-identical, and no module
under ``agents/`` imports from ``engine/``.

State derivation each tick (highest priority first):

* ``COVER`` -- a body is visible in the impostor's current room. Move
  one step to the alphabetically-first neighbor to vacate the scene.
  This is the FSM ``KILL -> COVER`` edge: after the kill the body is
  in the room and the impostor must not file a report.
* ``KILL`` -- ``cooldown == 0`` AND the best-scoring target was seen
  in our current room at the latest tick with no co-present
  witnesses. Emit :class:`KillIntent` against the target. A fellow
  impostor is never a candidate (see teammate-awareness below), so a
  kill always targets a crewmate.
* ``KILL_OPPORTUNITY`` -- ``cooldown == 0`` AND the best-scoring
  target was seen in our current room at the latest tick but
  co-present witnesses keep the score at zero. Hold position.

Teammate-awareness (Phase 7 Task 7.9, audit gp-1/gp-3, DESIGN.md §3.4):

* The recipient's ``fellow_impostor_ids`` (delivered on the privileged
  self channel by Task 7.2) are excluded from ``_scored_targets``
  entirely — both as kill/stalk candidates and from the co-present
  witness count, since a teammate is no witness risk. An impostor
  therefore never selects a fellow impostor as a target, which closes
  the friendly-fire trend the gameplay-data audit found.
* Co-location: a kill is only ever emitted against a target seen in the
  impostor's own room at the latest tick, so the policy never queues a
  kill against an out-of-room target (audit gp-3).
* Coordination: when a fellow impostor is co-located in the same room on
  the same tick and would also reach a kill, only the lower-id impostor
  emits the kill and the higher-id defers (a pure ``min(actor_id,
  fellow_id)`` tie-break over ids — no RNG, replay-safe). This prevents
  two co-located impostors from both killing on one tick (e.g. the
  tick-1 mutual-spawn case).
* ``STALK`` -- ``cooldown == 0`` AND the best-scoring target's most
  recent sighting puts them in a different reachable room. Take one
  A* step toward that room.
* ``IDLE`` -- nothing else applies (cooldown > 0, no usable
  sightings, etc.). If the impostor has a pending pretend-task and
  knows its room, route there or perform it; otherwise wait.

Conventions consumed from perception (DESIGN.md §4.2 / §6.2):

* ``self_state`` events carry the impostor's current room, (optional)
  pending pretend-task id, and ``fellow_impostor_ids`` (the impostor's
  teammates; ``()`` for a sole impostor or when the field is absent).
* ``cooldown_status`` events carry the impostor's kill cooldown for the
  observation tick.
* ``saw_player`` events at any tick are candidate-target sightings.
* ``saw_body`` events at the latest tick whose ``room`` matches the
  impostor's current room trigger the ``COVER`` interrupt.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
)
from agents.tactical.pathing import find_path
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    KillIntent,
    MoveIntent,
    PlayerId,
    WaitIntent,
)
from observation.public_map import PublicMapView, RoomId

# Stale sightings (a `saw_player` event older than this threshold) are
# dropped from `_scored_targets`. The audit's seed-0 reproduction had
# the impostor chasing a stale sighting near tick 4 for the rest of
# the game; any threshold well below that range fixes the chase loop.
# Thirty ticks is the documented default — wide enough to keep
# legitimate stalk targets, tight enough to kill the perpetual loop.
_STALENESS_THRESHOLD: Final[int] = 30


@dataclass(frozen=True)
class _ScoredTarget:
    """Per-player scoring snapshot used by the FSM."""

    player_id: PlayerId
    room: RoomId
    last_tick: int
    co_present: int
    score: float


class ImpostorPolicy:
    """Deterministic impostor FSM (DESIGN.md §4.4).

    Policy state lives entirely in the agent's :class:`MemoryStore`; the
    object itself only holds the agent id used to stamp emitted intents.
    """

    def __init__(self, *, agent_id: PlayerId) -> None:
        self._agent_id = agent_id

    @property
    def agent_id(self) -> PlayerId:
        return self._agent_id

    def decide(
        self,
        memory: MemoryStore,
        public_map: PublicMapView,
    ) -> ActionIntent:
        events = memory.recent(since_tick=0)
        if not events:
            raise ValueError(
                "impostor policy requires at least one episodic event in memory"
            )

        latest_tick = events[-1].tick
        latest_events = tuple(event for event in events if event.tick == latest_tick)

        self_state = self._latest_self_state(events)
        if self_state is None:
            raise ValueError(
                "impostor policy requires a self_state event before deciding"
            )
        own_room = self._room_from_self_state(self_state)
        pending_task_id = self._pending_task_from_self_state(self_state)
        fellow_impostor_ids = self._fellow_impostor_ids_from_self_state(self_state)

        cooldown = self._latest_cooldown(latest_events)
        if cooldown is None:
            raise ValueError(
                "impostor policy requires a cooldown_status event at the latest tick"
            )

        if self._body_visible_in(latest_events, own_room=own_room):
            return self._cover(public_map=public_map, own_room=own_room)

        confirmed_dead = self._confirmed_dead_from_bodies(events)
        targets = self._scored_targets(
            events,
            cooldown=cooldown,
            current_tick=latest_tick,
            confirmed_dead=confirmed_dead,
            fellow_impostor_ids=fellow_impostor_ids,
        )

        if cooldown == 0 and targets:
            best = targets[0]
            in_own_room_now = best.room == own_room and best.last_tick == latest_tick
            if in_own_room_now and best.co_present == 0:
                if self._defers_to_colocated_fellow(
                    latest_events,
                    own_room=own_room,
                    fellow_impostor_ids=fellow_impostor_ids,
                ):
                    # A lower-id fellow impostor is co-located this tick and
                    # would also reach this kill; the lower id acts and we
                    # defer so two impostors never both kill on one tick.
                    return self._wait()
                return self._kill(target_id=best.player_id)
            if in_own_room_now:
                return self._wait()
            if best.room != own_room and best.room in public_map.room_ids:
                try:
                    return self._move_toward(
                        public_map=public_map, own_room=own_room, goal=best.room
                    )
                except ValueError:
                    pass

        return self._idle(
            public_map=public_map,
            own_room=own_room,
            pending_task_id=pending_task_id,
        )

    @staticmethod
    def _latest_self_state(
        events: tuple[EpisodicEvent, ...],
    ) -> EpisodicEvent | None:
        for event in reversed(events):
            if event.type == EVENT_SELF_STATE:
                return event
        return None

    @staticmethod
    def _room_from_self_state(event: EpisodicEvent) -> RoomId:
        room = event.payload.get("room")
        if not isinstance(room, str):
            raise ValueError(
                f"self_state event missing string 'room' field: {event.payload!r}"
            )
        return room

    @staticmethod
    def _pending_task_from_self_state(event: EpisodicEvent) -> str | None:
        pending = event.payload.get("pending_task_id")
        if pending is None:
            return None
        if not isinstance(pending, str):
            raise ValueError(
                f"self_state event has non-string pending_task_id: {event.payload!r}"
            )
        return pending

    @staticmethod
    def _fellow_impostor_ids_from_self_state(
        event: EpisodicEvent,
    ) -> frozenset[PlayerId]:
        """Extract the impostor's teammates from the self_state payload.

        ``fellow_impostor_ids`` rides the privileged self channel (Task 7.2,
        ``observation/service.py``) and is serialized by
        ``agents.perception._self_state_payload``. It is absent on pre-7.2 /
        engine-only self_state events and empty for a sole impostor; both map
        to the empty set (no teammates), which is not a silent fallback — it
        is the correct meaning. A present-but-malformed value (a bare string
        or non-string entry) is a boundary-contract violation and raises.
        """

        raw = event.payload.get("fellow_impostor_ids")
        if raw is None:
            return frozenset()
        if isinstance(raw, str) or not isinstance(raw, Iterable):
            raise ValueError(
                f"self_state event has non-iterable fellow_impostor_ids: "
                f"{event.payload!r}"
            )
        fellows: set[PlayerId] = set()
        for fellow_id in raw:
            if not isinstance(fellow_id, str):
                raise ValueError(
                    f"self_state event has non-string fellow_impostor id: "
                    f"{event.payload!r}"
                )
            fellows.add(fellow_id)
        return frozenset(fellows)

    @staticmethod
    def _latest_cooldown(latest_events: tuple[EpisodicEvent, ...]) -> int | None:
        for event in latest_events:
            if event.type != EVENT_COOLDOWN_STATUS:
                continue
            cooldown = event.payload.get("cooldown")
            if not isinstance(cooldown, int):
                raise ValueError(
                    "cooldown_status event missing int 'cooldown' field: "
                    f"{event.payload!r}"
                )
            return cooldown
        return None

    @staticmethod
    def _body_visible_in(
        latest_events: tuple[EpisodicEvent, ...],
        *,
        own_room: RoomId,
    ) -> bool:
        for event in latest_events:
            if event.type != EVENT_SAW_BODY:
                continue
            room = event.payload.get("room")
            if not isinstance(room, str):
                raise ValueError(
                    f"saw_body event missing string 'room' field: {event.payload!r}"
                )
            if room == own_room:
                return True
        return False

    @staticmethod
    def _confirmed_dead_from_bodies(
        events: tuple[EpisodicEvent, ...],
    ) -> frozenset[PlayerId]:
        """Derive the set of confirmed-dead player ids from ``saw_body`` events.

        ``victim_id`` is populated at the observation boundary by
        :class:`observation.service.ObservationService` from
        ``BodyState.player_id``; perception surfaces it on every
        ``saw_body`` event payload. This used to parse a regex over the
        body id format -- see R-4 in
        ``audits/audit-2026-05-16-0036-reconciled.md`` for the
        retired coupling. A missing or non-string ``victim_id`` is a
        boundary contract violation: the impostor policy refuses to
        guess and raises immediately.
        """

        dead: set[PlayerId] = set()
        for event in events:
            if event.type != EVENT_SAW_BODY:
                continue
            victim_id = event.payload.get("victim_id")
            if not isinstance(victim_id, str):
                raise ValueError(
                    f"saw_body event missing string 'victim_id': {event.payload!r}"
                )
            dead.add(victim_id)
        return frozenset(dead)

    def _defers_to_colocated_fellow(
        self,
        latest_events: tuple[EpisodicEvent, ...],
        *,
        own_room: RoomId,
        fellow_impostor_ids: frozenset[PlayerId],
    ) -> bool:
        """Return ``True`` when a lower-id fellow impostor is co-located now.

        The coordination tie-break (Task 7.9, audit gp-1): among the impostors
        co-located in ``own_room`` at the latest tick, only the lowest id acts,
        so two co-located impostors never both emit a kill on the same tick —
        the tick-1 mutual-spawn self-destruct cannot occur. It is a pure
        function of ids: ``min(actor_id, fellow_id)`` acts, with no RNG, so
        replay reconstruction stays byte-identical (DESIGN.md §4 / locked
        decision 6). Ids compare lexically, matching the id ordering used
        throughout the policy and the observation service's sorted
        ``fellow_impostor_ids``.
        """

        if not fellow_impostor_ids:
            return False
        for event in latest_events:
            if event.type != EVENT_SAW_PLAYER:
                continue
            player_id = event.payload.get("player_id")
            if not isinstance(player_id, str):
                raise ValueError(
                    f"saw_player event missing string 'player_id': {event.payload!r}"
                )
            if player_id not in fellow_impostor_ids:
                continue
            room = event.payload.get("room")
            if not isinstance(room, str):
                raise ValueError(
                    f"saw_player event missing string 'room': {event.payload!r}"
                )
            if room == own_room and player_id < self._agent_id:
                return True
        return False

    @staticmethod
    def _scored_targets(
        events: tuple[EpisodicEvent, ...],
        *,
        cooldown: int,
        current_tick: int,
        confirmed_dead: frozenset[PlayerId],
        fellow_impostor_ids: frozenset[PlayerId],
    ) -> tuple[_ScoredTarget, ...]:
        """Rank ``saw_player`` sightings by isolation × witness × cooldown.

        Three filters are applied before scoring (DESIGN.md §4.4, §3.4):

        * ``fellow_impostor_ids`` sightings are dropped entirely (Task 7.9,
          audit gp-1) — a teammate is never a kill/stalk candidate, and it is
          also excluded from the co-present witness count because a fellow
          impostor is no witness risk. This is what stops the impostor from
          self-sabotaging its own team.
        * ``confirmed_dead`` sightings are dropped so the impostor never
          re-scores a corpse.
        * Sightings older than ``_STALENESS_THRESHOLD`` ticks are dropped
          so a stale lead cannot drive an endless chase.

        The cooldown factor preserves the original Task 2.7 scoring:
        scores are zero while ``cooldown > 0`` so the policy does not
        approach a target it cannot kill.
        """

        latest_sighting: dict[PlayerId, EpisodicEvent] = {}
        bucket: dict[tuple[int, RoomId], int] = {}
        for event in events:
            if event.type != EVENT_SAW_PLAYER:
                continue
            player_id = event.payload.get("player_id")
            if not isinstance(player_id, str):
                raise ValueError(
                    f"saw_player event missing string 'player_id': {event.payload!r}"
                )
            room = event.payload.get("room")
            if not isinstance(room, str):
                raise ValueError(
                    f"saw_player event missing string 'room': {event.payload!r}"
                )
            if player_id in fellow_impostor_ids:
                continue
            if player_id in confirmed_dead:
                continue
            if current_tick - event.tick > _STALENESS_THRESHOLD:
                continue
            latest_sighting[player_id] = event
            key = (event.tick, room)
            bucket[key] = bucket.get(key, 0) + 1

        cooldown_factor = 1.0 if cooldown == 0 else 0.0
        scored: list[_ScoredTarget] = []
        for player_id, sighting in latest_sighting.items():
            sighting_room = sighting.payload["room"]
            assert isinstance(sighting_room, str)
            sighting_tick = sighting.tick
            total_in_room = bucket.get((sighting_tick, sighting_room), 0)
            co_present = max(0, total_in_room - 1)
            isolation = 1.0 / (1.0 + co_present)
            witness_risk = co_present / (1.0 + co_present)
            score = isolation * (1.0 - witness_risk) * cooldown_factor
            scored.append(
                _ScoredTarget(
                    player_id=player_id,
                    room=sighting_room,
                    last_tick=sighting_tick,
                    co_present=co_present,
                    score=score,
                )
            )
        scored.sort(key=lambda target: (-target.score, target.player_id))
        return tuple(scored)

    def _cover(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
    ) -> ActionIntent:
        neighbors = sorted(public_map.room_neighbors.get(own_room, ()))
        if not neighbors:
            return self._wait()
        return MoveIntent.model_validate(
            {
                "type": "move",
                "actor": self._agent_id,
                "payload": {"to_room": neighbors[0]},
            }
        )

    def _move_toward(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        goal: RoomId,
    ) -> ActionIntent:
        path = find_path(public_map=public_map, start=own_room, goal=goal)
        next_room = path[1]
        return MoveIntent.model_validate(
            {
                "type": "move",
                "actor": self._agent_id,
                "payload": {"to_room": next_room},
            }
        )

    def _kill(self, *, target_id: PlayerId) -> ActionIntent:
        return KillIntent.model_validate(
            {
                "type": "kill",
                "actor": self._agent_id,
                "payload": {"target": target_id},
            }
        )

    def _wait(self) -> ActionIntent:
        return WaitIntent.model_validate(
            {"type": "wait", "actor": self._agent_id, "payload": {}}
        )

    def _idle(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        pending_task_id: str | None,
    ) -> ActionIntent:
        if pending_task_id is None:
            return self._wait()
        task_room = public_map.task_locations.get(pending_task_id)
        if task_room is None:
            return self._wait()
        if own_room == task_room:
            return DoTaskIntent.model_validate(
                {
                    "type": "do_task",
                    "actor": self._agent_id,
                    "payload": {"task_id": pending_task_id},
                }
            )
        try:
            return self._move_toward(
                public_map=public_map, own_room=own_room, goal=task_room
            )
        except ValueError:
            return self._wait()


__all__ = ["ImpostorPolicy"]
