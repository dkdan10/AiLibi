"""Crewmate tactical policy (DESIGN.md §4.4).

Implements the deterministic crewmate finite-state machine:

    IDLE -> MOVE_TO_TASK -> DO_TASK -> IDLE

with four override interrupts (highest priority first):

* ``BODY_VISIBLE -> REPORT`` -- a body is visible at the agent's most recent
  perception tick, so the agent files a :class:`ReportBodyIntent` for the
  alphabetically-first body id.
* ``KILL_WITNESSED -> FLEE_AND_REPORT`` -- a kill is in progress in the agent's
  current room, so the agent moves one A* step toward
  ``public_map.emergency_button_room``; if it is already there, it raises an
  :class:`EmergencyMeetingIntent`.
* ``REPAIR_SABOTAGE -> DIVERT_AND_REPAIR`` (Task 11.6, DESIGN.md §1.3, §4.4) --
  an active task-gating sabotage (the ``reactor`` kind) is surfaced on the
  freshest ``global_status``, so the agent diverts to fix it: one A* step per
  tick toward the nearest surfaced repair room (``sabotage_repair_rooms``, with a
  sorted-room-id tie-break so equidistant rooms never ping-pong the route), and a
  :class:`RepairSabotageIntent` for the sabotage kind once it stands in a repair
  room. An unrepaired gating sabotage is a hard loss timer (the dormant
  ``IMPOSTOR_SABOTAGE`` win), so this OUTRANKS the discretionary suspicion walk
  and task routing below it; a body or kill still ends the round and keeps
  priority above it. The diversion is scoped to ``sabotage_is_gating`` so a
  non-gating ``lights`` sabotage leaves crew behavior byte-identical to the
  pre-11.6 FSM. Repair rooms are read ONLY from the public :class:`GlobalView`
  channel -- the policy is engine-free, never importing from ``engine/`` and
  never hardcoding room names.
* ``SUSPICION_ACCUMULATED -> CALL_MEETING`` (Task 10.8, DESIGN.md §3.2, §5.2;
  audit gp-3 B-B-4) -- the agent's private max suspicion over presumed-living
  players has reached the §4.6 eject gate since the last meeting, so the agent
  takes the same button walk and presses the button. The walk is the
  counterplay cost and deliberately stays. Eligibility is bookkept by
  :class:`EmergencyPacingTracker` (one call per player per game, plus the
  global :data:`EMERGENCY_COOLDOWN_TICKS` cooldown since the last meeting
  ended) and handed to :meth:`CrewmatePolicy.decide` as an immutable
  :class:`EmergencyButtonView` snapshot, so the decision itself stays a pure
  function of its inputs.

When the agent re-enters IDLE with no pending task (the canonical FSM step
``DO_TASK -> IDLE``) the policy routes back to ``public_map.meeting_room``
and waits there. Without this routing the agent would issue
:class:`WaitIntent` from wherever the last task happened to finish, which
strands surviving crewmates inside task rooms and prevents headless games
from terminating — the impostor's stale ``saw_player`` sightings drive it
toward the kill site, and waiting crewmates never re-enter the impostor's
visibility window so no second kill or quorum body discovery is possible.

The policy is stateless: every decision is a pure function of the agent's
:class:`MemoryStore`, the :class:`PublicMapView`, and the optional
:class:`EmergencyButtonView` snapshot. The temporal bookkeeping the snapshot
is derived from (threshold crossings, the global meeting cooldown, the spent
call) lives in :class:`EmergencyPacingTracker`, owned by the agent runtime
and updated only from deterministic inputs, so replays are byte-identical.
Tie-breakers use sorted ids and no module under ``agents/`` imports from
``engine/``.

Conventions consumed from perception (DESIGN.md §4.2 / §6.2):

* ``saw_body`` events at the latest tick mean a body is visible to the agent.
* ``saw_player`` events at the latest tick whose payload ``action`` field
  equals ``"kill"`` and whose ``room`` matches the agent's own room indicate
  a kill in progress that the agent has witnessed.
* ``global_status`` events carry the public, role-blind sabotage aggregate
  (``sabotage_active`` / ``sabotage_kind`` / ``sabotage_repair_rooms`` /
  ``sabotage_is_gating``, Task 11.5, DESIGN.md §8.3); the freshest one drives the
  ``REPAIR_SABOTAGE`` interrupt above.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from agents.memory.beliefs import BeliefState
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_GLOBAL_STATUS,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
)
from agents.tactical.pathing import find_path
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    EmergencyMeetingIntent,
    MoveIntent,
    PlayerId,
    RepairSabotageIntent,
    ReportBodyIntent,
    WaitIntent,
)
from observation.public_map import PublicMapView, RoomId

KILL_ACTION: Final[str] = "kill"
KILL_WITNESS_REASON: Final[str] = "kill_witnessed"

SUSPICION_ACCUMULATION_REASON: Final[str] = "suspicion_accumulation"
"""``EmergencyMeetingIntent.payload.reason`` stamped by the Task 10.8 trigger.

Distinct from :data:`KILL_WITNESS_REASON` so replay / eval tooling can tell
the two producers of the same intent apart without re-deriving belief state.
"""

EMERGENCY_COOLDOWN_TICKS: Final[int] = 6
"""Global cooldown between a meeting's end and the next emergency call
(Task 10.8, DESIGN.md §3.2, §5.2; audit gp-3 B-B-2/B-B-4).

Anchored to the W0 set's mean kill interval (6.18 ticks -> 6). The anchor
reasoning, recorded for future re-tunes: emergency supply should roughly
match and never exceed organic body-report supply, so meetings cannot spawn
faster than evidence accrues -- suspicion only moves on kill-driven
observations (§6.3 Rules 1/4), so a cooldown of one mean kill interval lets
at most one emergency ride each kill's evidence. The anchor shifts whenever
kill cadence changes: Wave 2's kill-intent gating (Task 10.11) changes that
cadence and re-derives this constant there.

The cooldown counts from the tick gameplay resumed after the last meeting
(any trigger kind). Before the first meeting there is nothing to cool down
from, so the gate is open -- the suspicion threshold itself is the limiter,
since beliefs cannot cross 0.60 before evidence accrues.
"""


@dataclass(frozen=True)
class EmergencyButtonView:
    """Immutable per-tick eligibility snapshot for the suspicion trigger.

    Produced by :meth:`EmergencyPacingTracker.observe_tick` and consumed by
    :meth:`CrewmatePolicy.decide` -- the split keeps the policy a pure
    function (the snapshot is data) while the tracker owns the temporal
    bookkeeping. All four conditions must hold for the trigger to fire:

    * ``over_gate`` -- the agent's private max suspicion over presumed-living
      players is at or above the §4.6 eject gate
      (:data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`) at this
      tick.
    * ``crossed_since_meeting`` -- that belief crossed the gate from below
      AFTER the last meeting ended (a high prior carried through a meeting
      does not re-fire; the meeting was its discussion opportunity).
    * ``call_available`` -- the agent's one emergency call per game
      (DESIGN.md §3.4) is unspent.
    * ``cooldown_remaining == 0`` -- at least
      :data:`EMERGENCY_COOLDOWN_TICKS` ticks have elapsed since the last
      meeting ended (0 before the first meeting).
    """

    over_gate: bool
    crossed_since_meeting: bool
    call_available: bool
    cooldown_remaining: int

    @property
    def is_eligible(self) -> bool:
        """Whether the suspicion-accumulation trigger may fire this tick."""

        return (
            self.over_gate
            and self.crossed_since_meeting
            and self.call_available
            and self.cooldown_remaining == 0
        )


class EmergencyPacingTracker:
    """Deterministic emergency-trigger bookkeeping for one crewmate (Task 10.8).

    Tracks the three temporal facts :meth:`CrewmatePolicy.decide` cannot
    derive from a single tick's memory/belief snapshot:

    * whether max suspicion over presumed-living players crossed the §4.6
      gate since the last meeting (sampled once per gameplay tick);
    * when the last meeting ended, for the global
      :data:`EMERGENCY_COOLDOWN_TICKS` cooldown;
    * whether this agent's one emergency call per game is spent -- counted
      when a meeting actually OPENS with this agent as its emergency caller
      (engine truth), never when the intent is merely emitted, so an intent
      pre-empted by another player's same-tick report does not burn the call.

    "Presumed living" is derived only from knowledge the agent legitimately
    holds: the dead roster announced at each meeting (deaths and ejections
    are public at meetings -- the same channel the Task 10.3 DEAD prompt
    line uses) plus victims of bodies the agent saw first-hand. No engine
    state crosses the firewall.

    Every update is a deterministic function of the agent's own episodic
    store, its belief state, and the meeting-end notifications the
    orchestrator fans out -- all replay-stable inputs -- so cooldown
    bookkeeping replays byte-identically. Updates are idempotent within a
    tick (re-sampling the same state changes nothing), keeping repeated
    ``decide`` calls equal.
    """

    def __init__(self) -> None:
        self._was_over_gate = False
        self._crossed_since_meeting = False
        self._last_meeting_end_tick: int | None = None
        self._announced_dead: frozenset[PlayerId] = frozenset()
        self._own_calls_used = 0

    def observe_tick(
        self,
        *,
        tick: int,
        memory: MemoryStore,
        beliefs: BeliefState,
        own_id: PlayerId,
    ) -> EmergencyButtonView:
        """Sample this tick's belief state and return the eligibility snapshot.

        Called once per gameplay tick by the agent runtime, after perception
        has ingested the tick's packet (so ``beliefs`` reflects the §6.3
        rule updates for this tick).
        """

        over_gate = self._over_gate(memory=memory, beliefs=beliefs, own_id=own_id)
        if over_gate and not self._was_over_gate:
            self._crossed_since_meeting = True
        self._was_over_gate = over_gate
        return EmergencyButtonView(
            over_gate=over_gate,
            crossed_since_meeting=self._crossed_since_meeting,
            call_available=self._own_calls_used == 0,
            cooldown_remaining=self._cooldown_remaining(tick),
        )

    def observe_meeting_end(
        self,
        *,
        end_tick: int,
        announced_dead: Iterable[PlayerId],
        was_own_emergency_call: bool,
        memory: MemoryStore,
        beliefs: BeliefState,
        own_id: PlayerId,
    ) -> None:
        """Fold one concluded meeting into the bookkeeping.

        ``end_tick`` is the tick gameplay resumes at; ``announced_dead`` is
        the public post-meeting dead roster (including an ejectee);
        ``was_own_emergency_call`` is whether the meeting opened from THIS
        agent's emergency action. The crossed flag resets -- the meeting was
        the discussion opportunity for whatever belief crossed before it --
        and the over-gate baseline re-samples the post-meeting-fold beliefs,
        so only a fresh below-to-above crossing re-arms the trigger.
        """

        self._last_meeting_end_tick = end_tick
        self._announced_dead = self._announced_dead | frozenset(announced_dead)
        if was_own_emergency_call:
            self._own_calls_used += 1
        self._crossed_since_meeting = False
        self._was_over_gate = self._over_gate(
            memory=memory, beliefs=beliefs, own_id=own_id
        )

    def _cooldown_remaining(self, tick: int) -> int:
        if self._last_meeting_end_tick is None:
            return 0
        elapsed = tick - self._last_meeting_end_tick
        return max(0, EMERGENCY_COOLDOWN_TICKS - elapsed)

    def _over_gate(
        self,
        *,
        memory: MemoryStore,
        beliefs: BeliefState,
        own_id: PlayerId,
    ) -> bool:
        """Max suspicion over presumed-living players is at/above the §4.6 gate.

        The gate constant is read from its one home
        (:data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`) and the
        comparison is inclusive at the cutoff, matching the vote tally's
        "exactly the threshold ejects" semantics. Players the agent presumes
        dead -- meeting-announced dead plus first-hand-seen body victims --
        are excluded: a dead player's stale suspicion row is not actionable
        at a meeting. The agent's own id is excluded defensively (the belief
        store never materialises a self row).
        """

        presumed_dead = self._announced_dead | _seen_victim_ids(memory)
        return any(
            beliefs.view(player_id).suspicion >= DEFAULT_SKIP_CONFIDENCE_THRESHOLD
            for player_id in beliefs.known_players()
            if player_id != own_id and player_id not in presumed_dead
        )


def _seen_victim_ids(memory: MemoryStore) -> frozenset[PlayerId]:
    """Victims of every body the agent saw first-hand (``saw_body`` events).

    Payload fields are read defensively (the
    ``agents.memory.store._latest_self_guard_fields`` convention): a
    hand-built fixture event without ``victim_id`` contributes nothing
    rather than failing.
    """

    victims: set[PlayerId] = set()
    for event in memory.recent(since_tick=0):
        if event.type != EVENT_SAW_BODY:
            continue
        victim_id = event.payload.get("victim_id")
        if isinstance(victim_id, str):
            victims.add(victim_id)
    return frozenset(victims)


@dataclass(frozen=True)
class _GatingSabotage:
    """The active task-gating sabotage surfaced on the freshest ``global_status``.

    Built by :meth:`CrewmatePolicy._active_gating_sabotage` from the public,
    role-blind :class:`observation.packet.GlobalView` channel (Task 11.5): ``kind``
    stamps the emitted :class:`RepairSabotageIntent` and ``repair_rooms`` are the
    surfaced repair targets the crew routes toward. Internal to this module --
    a typed carrier so the REPAIR_SABOTAGE interrupt stays a pure function of the
    public channel with no ``engine/`` coupling and no hardcoded room names.
    """

    kind: str
    repair_rooms: tuple[RoomId, ...]


class CrewmatePolicy:
    """Deterministic crewmate FSM (DESIGN.md §4.4).

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
        *,
        emergency: EmergencyButtonView | None = None,
    ) -> ActionIntent:
        """Choose this tick's :class:`ActionIntent` from memory (DESIGN.md §4.4).

        ``emergency`` is the optional Task 10.8 eligibility snapshot from
        :meth:`EmergencyPacingTracker.observe_tick`. When supplied and
        eligible, the suspicion-accumulation trigger takes the same button
        walk as the witnessed-kill interrupt (a second producer of the same
        intent, not a new pipeline); ``None`` -- callers without belief
        wiring -- preserves the pre-10.8 FSM byte-for-byte. The decision
        remains a pure function of its arguments.
        """

        events = memory.recent(since_tick=0)
        if not events:
            raise ValueError(
                "crewmate policy requires at least one episodic event in memory"
            )

        latest_tick = events[-1].tick
        latest_events = tuple(event for event in events if event.tick == latest_tick)

        self_state = self._latest_self_state(events)
        if self_state is None:
            raise ValueError(
                "crewmate policy requires a self_state event before deciding"
            )
        own_room = self._room_from_self_state(self_state)
        pending_task_id = self._pending_task_from_self_state(self_state)

        body_id = self._first_visible_body(latest_events, own_room=own_room)
        if body_id is not None:
            return self._report(body_id=body_id)

        if self._kill_witnessed(latest_events, own_room=own_room):
            return self._walk_to_button(
                public_map=public_map,
                own_room=own_room,
                reason=KILL_WITNESS_REASON,
            )

        # REPAIR_SABOTAGE (Task 11.6, DESIGN.md §1.3, §4.4): an active task-gating
        # sabotage is a hard loss timer (the dormant IMPOSTOR_SABOTAGE win), so the
        # crew diverts to fix it ABOVE the discretionary suspicion walk and task
        # routing -- but BELOW the body/kill interrupts, which end the round anyway.
        # The signal is re-read fresh each tick from the public GlobalView channel
        # (no cross-tick tracker); a non-gating ``lights`` sabotage returns None
        # here so lights-era crew behavior stays byte-identical.
        gating_sabotage = self._active_gating_sabotage(events)
        if gating_sabotage is not None:
            return self._walk_to_repair(
                public_map=public_map,
                own_room=own_room,
                sabotage=gating_sabotage,
            )

        if emergency is not None and emergency.is_eligible:
            return self._walk_to_button(
                public_map=public_map,
                own_room=own_room,
                reason=SUSPICION_ACCUMULATION_REASON,
            )

        if pending_task_id is None:
            return self._return_to_hub(public_map=public_map, own_room=own_room)

        task_room = public_map.task_locations.get(pending_task_id)
        if task_room is None:
            return self._return_to_hub(public_map=public_map, own_room=own_room)

        if own_room == task_room:
            return self._do_task(task_id=pending_task_id)

        return self._move_toward(
            public_map=public_map, own_room=own_room, goal=task_room
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
    def _first_visible_body(
        events: tuple[EpisodicEvent, ...],
        *,
        own_room: RoomId,
    ) -> str | None:
        """Return the alphabetically-first body in ``own_room`` at the latest tick.

        Bodies in adjacent rooms are visible to the agent (perception
        records them as ``saw_body`` events) but ``ReportBodyAction``
        requires the actor to share the body's room. The interrupt only
        fires when a report would actually succeed, so the policy does
        not stall against the engine rejecting every adjacent-body report.
        """

        body_ids: list[str] = []
        for event in events:
            if event.type != EVENT_SAW_BODY:
                continue
            body_id = event.payload.get("body_id")
            if not isinstance(body_id, str):
                raise ValueError(
                    f"saw_body event missing string 'body_id': {event.payload!r}"
                )
            body_room = event.payload.get("room")
            if not isinstance(body_room, str):
                raise ValueError(
                    f"saw_body event missing string 'room': {event.payload!r}"
                )
            if body_room != own_room:
                continue
            body_ids.append(body_id)
        if not body_ids:
            return None
        return sorted(body_ids)[0]

    @staticmethod
    def _kill_witnessed(
        events: tuple[EpisodicEvent, ...],
        *,
        own_room: RoomId,
    ) -> bool:
        for event in events:
            if event.type != EVENT_SAW_PLAYER:
                continue
            if event.payload.get("action") != KILL_ACTION:
                continue
            if event.payload.get("room") != own_room:
                continue
            return True
        return False

    @staticmethod
    def _active_gating_sabotage(
        events: tuple[EpisodicEvent, ...],
    ) -> _GatingSabotage | None:
        """Return the active task-gating sabotage on the freshest ``global_status``.

        Reads the most recent ``global_status`` event -- the public, role-blind
        aggregate perception appends once per tick (Task 11.5, DESIGN.md §8.3) --
        mirroring the ``_latest_self_state`` reversed scan, and returns the gating
        sabotage's kind plus surfaced repair rooms ONLY when both
        ``sabotage_active`` and ``sabotage_is_gating`` hold; otherwise ``None``
        (no diversion). Scoping to ``sabotage_is_gating`` is what keeps a
        non-gating ``lights`` sabotage byte-identical to the pre-11.6 FSM. There is
        no cross-tick tracker -- the signal is re-read fresh each tick.

        A missing ``global_status`` (or a falsy ``sabotage_active`` /
        ``sabotage_is_gating``) means "no active gating sabotage" -- the correct
        meaning, not a silent fallback, mirroring the absent-field handling in the
        self_state accessors. Once committed to acting (active AND gating) a
        missing / malformed ``sabotage_kind`` or ``sabotage_repair_rooms`` is a
        boundary-contract violation and raises (no silent guess), as does an active
        gating sabotage that surfaces no repair room to route toward.
        """

        for event in reversed(events):
            if event.type != EVENT_GLOBAL_STATUS:
                continue
            payload = event.payload
            if not payload.get("sabotage_active"):
                return None
            if not payload.get("sabotage_is_gating"):
                return None
            kind = payload.get("sabotage_kind")
            if not isinstance(kind, str):
                raise ValueError(
                    "global_status event missing string 'sabotage_kind' for an "
                    f"active gating sabotage: {payload!r}"
                )
            raw_rooms = payload.get("sabotage_repair_rooms")
            if isinstance(raw_rooms, str) or not isinstance(raw_rooms, Iterable):
                raise ValueError(
                    "global_status event has non-iterable 'sabotage_repair_rooms': "
                    f"{payload!r}"
                )
            repair_rooms: list[RoomId] = []
            for room in raw_rooms:
                if not isinstance(room, str):
                    raise ValueError(
                        f"global_status event has non-string repair room: {payload!r}"
                    )
                repair_rooms.append(room)
            if not repair_rooms:
                raise ValueError(
                    "active gating sabotage surfaced no repair rooms to route "
                    f"toward: {payload!r}"
                )
            return _GatingSabotage(kind=kind, repair_rooms=tuple(repair_rooms))
        return None

    def _walk_to_button(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        reason: str,
    ) -> ActionIntent:
        """Shared button-walk for both emergency producers (DESIGN.md §4.4).

        One A* step toward ``public_map.emergency_button_room`` per tick;
        once there, press the button. ``reason`` distinguishes the producer
        on the emitted intent (:data:`KILL_WITNESS_REASON` for the
        witnessed-kill interrupt, :data:`SUSPICION_ACCUMULATION_REASON` for
        the Task 10.8 suspicion trigger). The walk is deliberately not
        shortcut for either producer -- it is the counterplay cost.
        """

        target = public_map.emergency_button_room
        if own_room == target:
            return EmergencyMeetingIntent.model_validate(
                {
                    "type": "emergency",
                    "actor": self._agent_id,
                    "payload": {"reason": reason},
                }
            )
        return self._move_toward(public_map=public_map, own_room=own_room, goal=target)

    def _walk_to_repair(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        sabotage: _GatingSabotage,
    ) -> ActionIntent:
        """Divert to fix an active task-gating sabotage (Task 11.6, DESIGN.md §4.4).

        Once the agent stands in a surfaced repair room it emits
        :class:`RepairSabotageIntent` for the sabotage kind; otherwise it takes one
        A* step per tick toward the nearest repair room. The repair rooms come
        ONLY from the public ``GlobalView`` channel (carried on ``sabotage``), so
        the policy never imports from ``engine/`` and never hardcodes a room name.
        A disconnected repair set degrades to a wait via :meth:`_move_toward`.
        """

        if own_room in sabotage.repair_rooms:
            return self._repair(kind=sabotage.kind)
        target = self._nearest_repair_room(
            public_map=public_map,
            own_room=own_room,
            repair_rooms=sabotage.repair_rooms,
        )
        return self._move_toward(public_map=public_map, own_room=own_room, goal=target)

    def _nearest_repair_room(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        repair_rooms: tuple[RoomId, ...],
    ) -> RoomId:
        """Pick the repair room fewest A* hops away, sorted-room-id tie-break.

        ``repair_rooms`` is the non-empty surfaced repair set. The room with the
        smallest ``(hop_count, room_id)`` key wins -- a deterministic min that is
        independent of the surfaced order (so equidistant rooms break by id, not by
        payload ordering) and stable as the agent closes the distance: the chosen
        room's hop count strictly decreases each tick while every other room's
        changes by at most one, so the choice cannot oscillate across ticks (the
        ping-pong integration risk). Mirrors
        :meth:`agents.tactical.impostor_policy.ImpostorPolicy._choose_exit_vent`.
        """

        return min(
            repair_rooms,
            key=lambda room: (
                self._repair_distance(public_map=public_map, start=own_room, goal=room),
                room,
            ),
        )

    @staticmethod
    def _repair_distance(
        *,
        public_map: PublicMapView,
        start: RoomId,
        goal: RoomId,
    ) -> int:
        """A* hop count from ``start`` to ``goal`` (unreachable = sentinel).

        Mirrors :meth:`ImpostorPolicy._vent_distance`: an unreachable or unknown
        goal sorts last via a sentinel one larger than any possible path length,
        keeping :meth:`_nearest_repair_room`'s ordering total and deterministic
        without raising on a disconnected topology (the route then degrades to a
        wait when :meth:`_move_toward` fails to path).
        """

        try:
            return len(find_path(public_map=public_map, start=start, goal=goal)) - 1
        except ValueError:
            return len(public_map.room_ids) + 1

    def _return_to_hub(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
    ) -> ActionIntent:
        """Idle behaviour: route back to the meeting room and wait.

        Once the crewmate is at the meeting room there is nothing useful
        for the rule-based policy to do, so it issues :class:`WaitIntent`.
        Until then it walks one A* step toward the meeting room each tick.
        Moving lets the surviving crewmate re-enter the impostor's
        visibility window after the FSM exits ``DO_TASK``, which is the
        only path to game termination without the strategic-layer meeting
        manager (Phase 3.8) — sitting in the task room would otherwise
        leave the impostor's stale sightings pointing at the kill site
        and produce ``TICK_BUDGET_REACHED`` for every default seed.
        """

        hub = public_map.meeting_room
        if own_room == hub:
            return self._wait()
        return self._move_toward(public_map=public_map, own_room=own_room, goal=hub)

    def _move_toward(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        goal: RoomId,
    ) -> ActionIntent:
        try:
            path = find_path(public_map=public_map, start=own_room, goal=goal)
        except ValueError:
            return self._wait()
        next_room = path[1]
        return MoveIntent.model_validate(
            {
                "type": "move",
                "actor": self._agent_id,
                "payload": {"to_room": next_room},
            }
        )

    def _do_task(self, *, task_id: str) -> ActionIntent:
        return DoTaskIntent.model_validate(
            {
                "type": "do_task",
                "actor": self._agent_id,
                "payload": {"task_id": task_id},
            }
        )

    def _repair(self, *, kind: str) -> ActionIntent:
        """Build the :class:`RepairSabotageIntent`, mirroring :meth:`_do_task`.

        Emitted once the agent stands in a surfaced repair room (Task 11.6); the
        engine resolves the agent's repair contribution against the active
        sabotage's repair rooms, so the policy submits only the public sabotage
        ``kind`` it read from the ``GlobalView`` channel.
        """

        return RepairSabotageIntent.model_validate(
            {
                "type": "repair_sabotage",
                "actor": self._agent_id,
                "payload": {"kind": kind},
            }
        )

    def _report(self, *, body_id: str) -> ActionIntent:
        return ReportBodyIntent.model_validate(
            {
                "type": "report",
                "actor": self._agent_id,
                "payload": {"body_id": body_id},
            }
        )

    def _wait(self) -> ActionIntent:
        return WaitIntent.model_validate(
            {"type": "wait", "actor": self._agent_id, "payload": {}}
        )


__all__ = [
    "EMERGENCY_COOLDOWN_TICKS",
    "KILL_ACTION",
    "KILL_WITNESS_REASON",
    "SUSPICION_ACCUMULATION_REASON",
    "CrewmatePolicy",
    "EmergencyButtonView",
    "EmergencyPacingTracker",
]
