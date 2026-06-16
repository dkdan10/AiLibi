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

* ``VENT_EXIT`` -- the impostor is already inside a vent (its own
  ``SelfView.in_vent`` is set, Task 11.1, DESIGN.md §3.4). This is the
  highest-priority branch so a vented impostor always has an exit: emit a
  :class:`VentIntent` to a connected vent whose room holds no visible body,
  preferring the room toward the current best isolated target
  (``_scored_targets``) and otherwise the alphabetically-first connected
  vent. If no connected vent is body-free the impostor still exits (to the
  alphabetically-first connected vent) and if the current vent has no
  connection at all it exits in place -- it is never left stuck in a vent.
  Once repositioned (``in_vent`` clears next tick) normal stalking resumes.
* ``COVER`` -- a body is visible in the impostor's current room. This is
  the FSM ``KILL -> COVER`` edge: after the kill the body is in the room and
  the impostor must not file a report. When a vent sits in that room, the
  impostor is not already vented, and NO non-teammate witness is co-present
  this tick, the impostor VENTS (emits :class:`VentIntent`) to hide the
  post-kill sighting trail (Task 11.1, experiments/lab/report-vent-escape-
  lab.md) instead of walking away. A co-present non-teammate witness (a
  fellow impostor never counts) makes a vent and a walk equal exposure, so
  the branch falls back to the move-away: one step to the alphabetically-
  first neighbor to vacate the scene. ``heard_vent_use`` stays observable, so
  a vent next to a witness would be a new catchable tell -- the witness guard
  is the only suppression, deliberately leaving the careless-vent tell in
  place (rubric R2, "deception sometimes fails").
* ``SABOTAGE`` -- the crew is near a task win and no sabotage is active (Task
  11.7, DESIGN.md §3.4 impostor actions, §4.4 impostor FSM; mirrors the 11.1
  vent-wiring precedent, experiments/lab/report-vent-escape-lab.md). Below the
  in-vent exit and COVER-or-vent branches but above the kill/stalk block, the
  impostor emits :class:`SabotageIntent` for the task-gating ``reactor`` kind
  (Task 11.5) to convert a near-certain crew task-win into a forced repair
  scramble + a hard loss timer. The trigger is a conservative, pure function of
  the freshest public ``global_status`` -- ``_active_sabotage`` is False AND
  ``_crew_near_task_win`` (the crew has completed ``_IMMINENT_CREW_WIN_COMPLETION``
  -- ~6/7 -- of the task instances) -- so it never fires when one is already active and
  never spams a sabotage every cooldown tick (which would starve kills, a
  degenerate low-interest loop). An AVAILABLE kill this tick still
  out-prioritizes the lever (``_kill_available_now``): the impostor keeps
  hunting and the lever only pre-empts a stalk/idle. No RNG and no module state,
  so replays stay byte-identical.
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
* Co-location: a kill is only ever emitted against a target whose
  *freshest* observation (a ``saw_player`` at the latest tick) still
  places it in the impostor's own room. This is re-validated at the
  emission seam by ``_target_colocated_now`` against the current-tick
  events the policy already holds — not trusted from the scoring
  snapshot — so a stale lead never queues a kill (audit gp-3; tightened
  per the 2026-06-07 audit gp-5 / MECH-B-1, re-confirmed by the
  2026-06-13-1816 audit MECH-B-1 / D-D-7: the producer emits a kill ONLY
  against a target co-located this tick, so producer cross-room kill
  emissions are 0 by construction and a kill during cooldown is suppressed
  by the ``cooldown == 0`` gate below). Stale sightings stay valid
  for stalking and navigation below; only the kill emission tightens.
  Intra-tick simultaneity is canonically id-ordered (DESIGN.md §3.4): a
  co-located lower-id target's same-tick move legitimately escapes a
  queued kill, so the engine same-room guard stays the backstop for that
  canonical residual (the ``kill requires same room`` rejections that
  remain are this dodge, NOT a producer defect) — this is producer-side
  waste removal, not the enforcement.
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
  knows its room, route there or perform it; otherwise wait. This is
  the BLENDING branch (Task 10.14, audit-2026-06-13-1816 D-D-1): the
  pretend-task id is surfaced on the impostor's self channel by
  ``observation.service.impostor_pretend_task_id`` (impostors own no real
  instance), so the branch -- dormant while that id was always ``None`` --
  now fires and the impostor moves to / "performs" a task like a crewmate
  instead of waiting, collapsing the ~51% "never-tasks" wait-share toward
  crew levels. The fake ``do_task`` renders as a do_task action and consumes
  the tick but the engine rejects it (no owned instance), so it advances no
  real task and never moves the crew win denominator.

Conventions consumed from perception (DESIGN.md §4.2 / §6.2):

* ``self_state`` events carry the impostor's current room, (optional)
  pending pretend-task id (a real map task id the impostor does not own,
  Task 10.14), ``fellow_impostor_ids`` (the impostor's teammates;
  ``()`` for a sole impostor or when the field is absent), and ``in_vent``
  (whether the impostor is currently inside a vent, Task 11.1; ``False``
  when the field is absent).
* ``cooldown_status`` events carry the impostor's kill cooldown for the
  observation tick.
* ``saw_player`` events at any tick are candidate-target sightings.
* ``saw_body`` events at the latest tick whose ``room`` matches the
  impostor's current room trigger the ``COVER`` interrupt.
* ``global_status`` events (the public, role-blind aggregate perception ingests
  every tick, Task 11.5) carry ``tasks_completed`` / ``tasks_total`` and
  ``sabotage_active``; the ``SABOTAGE`` branch reads the freshest one to fire the
  ``reactor`` lever at an imminent crew task-win.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_COOLDOWN_STATUS,
    EVENT_GLOBAL_STATUS,
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
    SabotageIntent,
    VentIntent,
    WaitIntent,
)
from observation.public_map import PublicMapView, RoomId, VentId

# Stale sightings (a `saw_player` event older than this threshold) are
# dropped from `_scored_targets`. The audit's seed-0 reproduction had
# the impostor chasing a stale sighting near tick 4 for the rest of
# the game; any threshold well below that range fixes the chase loop.
# Thirty ticks is the documented default — wide enough to keep
# legitimate stalk targets, tight enough to kill the perpetual loop.
_STALENESS_THRESHOLD: Final[int] = 30

# The task-gating sabotage the impostor emits (Task 11.5/11.7, DESIGN.md §3.4).
# ``reactor`` is the only ``gates_tasks: true`` kind in the canonical map; it
# stalls the task race and surfaces public repair rooms, so it is the lever that
# turns an imminent crew task-win into a contestable clock. The string is the
# map's ``sabotages`` key, round-tripped verbatim as the SabotageIntent payload.
_REACTOR_SABOTAGE_KIND: Final[str] = "reactor"

# The crew is "near a task win" when it has completed at least this FRACTION of
# all per-player task INSTANCES (``tasks_completed / tasks_total``, both read
# from the public ``global_status``; the denominator is the engine win total,
# DESIGN.md §3.2). Stored as an exact ``(numerator, denominator)`` ratio so the
# comparison is integer arithmetic -- no float drift, byte-identical replays.
#
# Anchored to "imminent crew win" (Task 11.7, DESIGN.md §3.4/§4.4) as a
# ROSTER-ROBUST fraction rather than an absolute remaining-count: at the
# canonical 9p/2i eval roster (14 instances) >=6/7 engages at 12/14 and 13/14 --
# the crew's final one or two task-completions, exactly when denying the win is
# strongest. Firing at 12/14 (not only the very last 13/14) is a deliberate
# one-completion buffer so the impostor pulls the lever BEFORE the last task can
# land on the sabotage tick. The conservative ~86% floor keeps the predicate
# False for the whole game until the crew is on the brink, so the impostor never
# sabotages every cooldown tick (a kill-starving, low-interest degenerate loop).
# A fraction (not a fixed count) also keeps small rosters sane: the flat 4p/1i
# determinism reference (3 or 6 instances) can never reach >=6/7 without already
# being complete, so the lever is a counterplay for the canonical eval roster,
# not the reference set. It is a sabotage TRIGGER parameter, NOT the frozen task
# clock; re-tuned (with the reactor timer) at the 11.8 re-record if R5 win-shape
# diversity does not rise.
_IMMINENT_CREW_WIN_COMPLETION: Final[tuple[int, int]] = (6, 7)


@dataclass(frozen=True)
class _ScoredTarget:
    """Per-player scoring snapshot used by the FSM.

    Holds only what the STALK/navigation and witness-gate branches read:
    the candidate's id, its most-recent-sighting ``room`` (which may be
    stale — that is fine for navigation), the co-present witness count, and
    the score. Current-tick co-location for the *kill* gate is re-validated
    separately against the freshest observation (``_target_colocated_now``),
    so the snapshot intentionally does not carry the sighting tick.
    """

    player_id: PlayerId
    room: RoomId
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
        in_vent = self._in_vent_from_self_state(self_state)

        cooldown = self._latest_cooldown(latest_events)
        if cooldown is None:
            raise ValueError(
                "impostor policy requires a cooldown_status event at the latest tick"
            )

        body_rooms = self._body_visible_rooms(latest_events)
        confirmed_dead = self._confirmed_dead_from_bodies(events)
        targets = self._scored_targets(
            events,
            cooldown=cooldown,
            current_tick=latest_tick,
            confirmed_dead=confirmed_dead,
            fellow_impostor_ids=fellow_impostor_ids,
        )

        # VENT_EXIT (Task 11.1): an already-vented impostor takes the highest-
        # priority branch so it is never left stuck inside a vent. It exits
        # toward an isolated / non-body room before any body or kill logic.
        if in_vent:
            return self._vent_exit(
                public_map=public_map,
                own_room=own_room,
                body_rooms=body_rooms,
                targets=targets,
            )

        # COVER-or-vent (Task 11.1): a body in the impostor's own room. Vent to
        # hide the post-kill sighting trail when a vent is here and no
        # non-teammate witness is co-present; otherwise walk away.
        if own_room in body_rooms:
            return self._cover_or_vent(
                public_map=public_map,
                own_room=own_room,
                latest_events=latest_events,
                fellow_impostor_ids=fellow_impostor_ids,
            )

        # SABOTAGE (Task 11.7): deny an imminent crew task win. Below the in-vent
        # exit and COVER-or-vent branches but above the kill/stalk block -- yet an
        # AVAILABLE kill this tick still out-prioritizes the lever (the impostor
        # keeps hunting; the lever only pre-empts a stalk/idle). Conservative,
        # pure trigger: no sabotage active AND the crew has completed
        # ``_IMMINENT_CREW_WIN_COMPLETION`` (~6/7) of its task instances, both
        # read from the freshest public ``global_status``, so it converts a
        # near-certain task-win into a forced repair scramble + a hard loss timer
        # (the Task 11.5 ``reactor`` kind) without ever spamming a sabotage per
        # cooldown tick. No RNG / module state -> replays stay byte-identical.
        if (
            self._crew_near_task_win(events)
            and not self._active_sabotage(events)
            and not self._kill_available_now(
                latest_events=latest_events,
                cooldown=cooldown,
                targets=targets,
                own_room=own_room,
            )
        ):
            return self._sabotage(kind=_REACTOR_SABOTAGE_KIND)

        if cooldown == 0 and targets:
            best = targets[0]
            # Kill-emission seam — re-validate the chosen target against THIS
            # tick's visibility before queuing (audit-2026-06-07-0717 gp-5,
            # findings MECH-B-1 / A-A-3). ``_scored_targets`` ranks
            # ``saw_player`` sightings from any tick in the staleness window,
            # which is correct for the STALK/navigation branch below, but a
            # kill must only fire when the freshest observation still places
            # the target in our room this tick — otherwise the engine rejects
            # it ("kill requires same room") and the impostor wastes the tick.
            #
            # This is producer-side waste removal, NOT the enforcement: per
            # DESIGN.md §3.4 intra-tick simultaneity is canonically id-ordered,
            # so a co-located lower-id target's same-tick move legitimately
            # escapes a queued kill. That residual dodge is documented canon
            # and the engine same-room guard stays the backstop; the producer
            # only guarantees it never *emits* against a stale/out-of-room
            # target.
            in_own_room_now = self._target_colocated_now(
                latest_events, target_id=best.player_id, own_room=own_room
            )
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
            body_rooms=body_rooms,
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
    def _in_vent_from_self_state(event: EpisodicEvent) -> bool:
        """Read the impostor's own ``in_vent`` flag from the self_state payload.

        ``in_vent`` rides the privileged self channel (Task 11.1,
        ``observation/service.py`` populates it from ``PlayerState.in_vent``) and
        is serialized by ``agents.perception._self_state_payload``. It is absent
        on pre-11.1 / engine-only self_state events, which maps to ``False`` (not
        in a vent) -- the correct meaning, not a silent fallback, mirroring the
        absent-``fellow_impostor_ids`` handling above. A present-but-non-bool
        value is a boundary-contract violation and raises.
        """

        raw = event.payload.get("in_vent")
        if raw is None:
            return False
        if not isinstance(raw, bool):
            raise ValueError(
                f"self_state event has non-bool in_vent: {event.payload!r}"
            )
        return raw

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
    def _latest_global_status(
        events: tuple[EpisodicEvent, ...],
    ) -> EpisodicEvent | None:
        """Return the most recent ``global_status`` event, or ``None`` if absent.

        Perception appends exactly one ``global_status`` (the public, role-blind
        aggregate, Task 11.5) per observation tick, so the last one in the log is
        the freshest task / sabotage reading. Mirrors :meth:`_latest_self_state`.
        Absent only on hand-built fixtures that omit the aggregate; the SABOTAGE
        predicates below map that to "no observed signal" rather than guessing.
        """

        for event in reversed(events):
            if event.type == EVENT_GLOBAL_STATUS:
                return event
        return None

    @staticmethod
    def _active_sabotage(events: tuple[EpisodicEvent, ...]) -> bool:
        """Return ``True`` iff a sabotage is currently active (Task 11.7).

        The SABOTAGE-branch guard (DESIGN.md §3.4): the impostor never emits a
        second :class:`SabotageIntent` while one is already active. Reads
        ``sabotage_active`` from the freshest ``global_status`` -- the public,
        role-blind aggregate (Task 11.5). An absent global_status event (or an
        absent ``sabotage_active`` key on a hand-built event) maps to ``False``
        (no observed sabotage -- the correct meaning, not a silent fallback,
        mirroring the absent-``in_vent`` handling); a present-but-non-bool
        ``sabotage_active`` is a boundary-contract violation and raises.
        """

        status = ImpostorPolicy._latest_global_status(events)
        if status is None:
            return False
        active = status.payload.get("sabotage_active")
        if active is None:
            return False
        if not isinstance(active, bool):
            raise ValueError(
                f"global_status event has non-bool sabotage_active: {status.payload!r}"
            )
        return active

    @staticmethod
    def _crew_near_task_win(events: tuple[EpisodicEvent, ...]) -> bool:
        """Return ``True`` iff the crew has crossed the imminent-win threshold.

        The SABOTAGE trigger predicate (Task 11.7, DESIGN.md §3.4/§4.4): a pure
        function of the freshest public ``global_status`` -- ``tasks_completed``
        / ``tasks_total`` (per-player task INSTANCES, the engine win
        denominator, DESIGN.md §3.2). ``True`` when at least one instance still
        remains (``tasks_completed < tasks_total`` -- there is a win left to
        deny) AND completion has reached ``_IMMINENT_CREW_WIN_COMPLETION`` of the
        total (the imminent-win fraction; see that constant for the anchor). The
        fraction is compared with integer cross-multiplication so the decision is
        exact and byte-identical across replays -- no float, no RNG, no module
        state. An absent global_status event (or absent task counts) maps to
        ``False`` -- no observed near-win, so do not sabotage -- while
        present-but-non-int counts are a boundary-contract violation and raise.
        """

        status = ImpostorPolicy._latest_global_status(events)
        if status is None:
            return False
        completed = status.payload.get("tasks_completed")
        total = status.payload.get("tasks_total")
        if completed is None or total is None:
            return False
        if not isinstance(completed, int) or not isinstance(total, int):
            raise ValueError(
                f"global_status event has non-int task counts: {status.payload!r}"
            )
        if total <= 0 or completed >= total:
            return False
        numerator, denominator = _IMMINENT_CREW_WIN_COMPLETION
        return completed * denominator >= total * numerator

    @staticmethod
    def _body_visible_rooms(
        latest_events: tuple[EpisodicEvent, ...],
    ) -> frozenset[RoomId]:
        """Rooms holding a body the impostor sees THIS tick (``saw_body``).

        Drives two seams: the ``COVER`` interrupt (a body in the impostor's OWN
        room) and the Task 10.14 cover-discipline gate in ``_idle`` (never route
        the blend back into a room that holds a body — see ``_idle``). A missing
        or non-string ``room`` is a boundary-contract violation and raises (no
        silent guess), mirroring the other ``saw_body`` scanners.
        """

        rooms: set[RoomId] = set()
        for event in latest_events:
            if event.type != EVENT_SAW_BODY:
                continue
            room = event.payload.get("room")
            if not isinstance(room, str):
                raise ValueError(
                    f"saw_body event missing string 'room' field: {event.payload!r}"
                )
            rooms.add(room)
        return frozenset(rooms)

    @staticmethod
    def _target_colocated_now(
        latest_events: tuple[EpisodicEvent, ...],
        *,
        target_id: PlayerId,
        own_room: RoomId,
    ) -> bool:
        """Return ``True`` iff ``target_id`` is seen in ``own_room`` THIS tick.

        Kill-emission re-validation (audit-2026-06-07-0717 gp-5, finding
        MECH-B-1; DESIGN.md §3.4). ``latest_events`` are the freshest
        observation the policy holds — all stamped with the current tick — so
        a ``saw_player`` match for ``target_id`` in ``own_room`` is current-tick
        co-location. Deriving the kill gate here (rather than from the
        ``_scored_targets`` snapshot, which ranks sightings from any tick in
        the staleness window) keeps the kill-safety invariant local to the
        emission seam and independent of the scoring model: a stale or
        adjacent-room sighting can still drive stalking but never a kill.

        A missing or non-string ``player_id`` / ``room`` on a ``saw_player``
        event is a boundary-contract violation and raises (no silent guess),
        mirroring the other ``saw_player`` scanners in this policy.
        """

        for event in latest_events:
            if event.type != EVENT_SAW_PLAYER:
                continue
            player_id = event.payload.get("player_id")
            if not isinstance(player_id, str):
                raise ValueError(
                    f"saw_player event missing string 'player_id': {event.payload!r}"
                )
            if player_id != target_id:
                continue
            room = event.payload.get("room")
            if not isinstance(room, str):
                raise ValueError(
                    f"saw_player event missing string 'room': {event.payload!r}"
                )
            if room == own_room:
                return True
        return False

    @staticmethod
    def _kill_available_now(
        *,
        latest_events: tuple[EpisodicEvent, ...],
        cooldown: int,
        targets: tuple[_ScoredTarget, ...],
        own_room: RoomId,
    ) -> bool:
        """Return ``True`` iff the kill/stalk block would EMIT a kill this tick.

        The SABOTAGE priority guard (Task 11.7): an available kill out-prioritizes
        sabotage so the impostor keeps hunting (definition of done). This is
        exactly the kill block's emission condition -- ``cooldown == 0`` AND the
        best-scoring target is co-located in our room THIS tick
        (:meth:`_target_colocated_now`, the same freshest-observation
        re-validation the kill seam uses) with no co-present non-teammate witness
        (``co_present == 0``). It deliberately mirrors the "kill or
        coordinate-defer" entry condition: when ``True`` a kill resolves in this
        room this tick (by us, or by a co-located lower-id fellow we defer to),
        so the impostor commits to the hunt and the lever stands aside. A
        witness-blocked opportunity (``co_present > 0``) or a different-room stalk
        target is NOT an available kill, so the lever may still pre-empt that
        stalk/wait. A pure function of memory -- no RNG, no module state.
        """

        if cooldown != 0 or not targets:
            return False
        best = targets[0]
        if best.co_present != 0:
            return False
        return ImpostorPolicy._target_colocated_now(
            latest_events, target_id=best.player_id, own_room=own_room
        )

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
    def _non_teammate_witness_present(
        latest_events: tuple[EpisodicEvent, ...],
        *,
        own_room: RoomId,
        fellow_impostor_ids: frozenset[PlayerId],
    ) -> bool:
        """Return ``True`` iff a non-teammate is co-present in ``own_room`` now.

        The vent-enter witness guard (Task 11.1). It reuses the same current-tick
        ``saw_player`` scan the kill gate runs on ``latest_events`` so "no
        witness" means the same thing for a kill and for a vent: a fellow
        impostor (in ``fellow_impostor_ids``) is never a witness, exactly as it
        is never a co-present witness in the kill score. A ``saw_player`` event
        missing its ``player_id`` / ``room`` is a boundary-contract violation and
        raises (no silent guess), mirroring the other ``saw_player`` scanners.
        """

        for event in latest_events:
            if event.type != EVENT_SAW_PLAYER:
                continue
            player_id = event.payload.get("player_id")
            if not isinstance(player_id, str):
                raise ValueError(
                    f"saw_player event missing string 'player_id': {event.payload!r}"
                )
            if player_id in fellow_impostor_ids:
                continue
            room = event.payload.get("room")
            if not isinstance(room, str):
                raise ValueError(
                    f"saw_player event missing string 'room': {event.payload!r}"
                )
            if room == own_room:
                return True
        return False

    @staticmethod
    def _vent_in_room(public_map: PublicMapView, room: RoomId) -> VentId | None:
        """Return the (deterministic) vent id sitting in ``room``, or ``None``.

        ``PublicMapView.vent_rooms`` maps each vent id to its room; this inverts
        it. The canonical map has at most one vent per room, but the lookup is
        defensive: if several vents ever shared a room the alphabetically-first
        vent id is chosen so the decision stays replay-stable with no RNG.
        """

        vent_ids = sorted(
            vent_id
            for vent_id, vent_room in public_map.vent_rooms.items()
            if vent_room == room
        )
        return vent_ids[0] if vent_ids else None

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
                    co_present=co_present,
                    score=score,
                )
            )
        scored.sort(key=lambda target: (-target.score, target.player_id))
        return tuple(scored)

    def _cover_or_vent(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        latest_events: tuple[EpisodicEvent, ...],
        fellow_impostor_ids: frozenset[PlayerId],
    ) -> ActionIntent:
        """COVER the body: vent if it is safe, otherwise walk away (Task 11.1).

        A vent hides the post-kill sighting trail that the offline lab proved is
        ~91% of the structured evidence against impostors
        (experiments/lab/report-vent-escape-lab.md). The impostor vents only when
        a vent sits in this room AND no non-teammate witness is co-present this
        tick -- the same witness notion the kill gate uses. The caller already
        guarantees the impostor is not already in a vent (the VENT_EXIT branch
        runs first). When a witness is present a vent and a walk are equal
        exposure (the witness saw the impostor regardless), so the simpler
        move-away fallback is kept; ``heard_vent_use`` would otherwise add a NEW
        catchable tell with no upside.
        """

        vent_id = self._vent_in_room(public_map, own_room)
        if vent_id is not None and not self._non_teammate_witness_present(
            latest_events,
            own_room=own_room,
            fellow_impostor_ids=fellow_impostor_ids,
        ):
            return self._vent(vent_id=vent_id)
        return self._cover(public_map=public_map, own_room=own_room)

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

    def _vent_exit(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
        body_rooms: frozenset[RoomId],
        targets: tuple[_ScoredTarget, ...],
    ) -> ActionIntent:
        """Exit the vent toward an isolated / non-body room (Task 11.1).

        Highest-priority branch for an ``in_vent`` impostor, so it can never be
        left stuck in a vent. The impostor's current room is its current vent's
        room. Candidate destinations are the connected vents
        (``vent_graph``); among those whose room holds no visible body, the one
        nearest the best isolated target's room is chosen (A* hop count over the
        public topology, vent-id tie-break -- deterministic, no RNG), else the
        alphabetically-first such vent. If every connected vent's room holds a
        body the impostor still exits (alphabetically-first connected vent), and
        if the current vent has no connection at all it exits in place. All
        tie-breaks are id/room-sorted so replays stay byte-identical.
        """

        current_vent = self._vent_in_room(public_map, own_room)
        if current_vent is None:
            raise ValueError(
                f"impostor is in_vent but no vent maps to its room: {own_room!r}"
            )
        connected = tuple(
            vent_id
            for vent_id in sorted(public_map.vent_graph.get(current_vent, ()))
            if vent_id in public_map.vent_rooms
        )
        if not connected:
            # No connected vent: exit in place via the current vent so the
            # impostor is never pathologically stuck inside the vent.
            return self._vent(vent_id=current_vent)
        body_free = tuple(
            vent_id
            for vent_id in connected
            if public_map.vent_rooms[vent_id] not in body_rooms
        )
        pool = body_free if body_free else connected
        chosen = self._choose_exit_vent(
            public_map=public_map, pool=pool, targets=targets
        )
        return self._vent(vent_id=chosen)

    def _choose_exit_vent(
        self,
        *,
        public_map: PublicMapView,
        pool: tuple[VentId, ...],
        targets: tuple[_ScoredTarget, ...],
    ) -> VentId:
        """Pick the exit vent toward the best target, else alphabetically first.

        ``pool`` is a non-empty, already-filtered tuple of candidate vent ids.
        When there is a scored target, the vent whose room is fewest A* hops from
        the best target's room wins, with the vent id as a deterministic
        tie-break; otherwise the alphabetically-first vent id is chosen. Both
        paths are pure functions of the public map and the memory, so the choice
        is replay-stable.
        """

        if targets:
            target_room = targets[0].room
            return min(
                pool,
                key=lambda vent_id: (
                    self._vent_distance(
                        public_map=public_map,
                        room=public_map.vent_rooms[vent_id],
                        target_room=target_room,
                    ),
                    vent_id,
                ),
            )
        return min(pool)

    @staticmethod
    def _vent_distance(
        *,
        public_map: PublicMapView,
        room: RoomId,
        target_room: RoomId,
    ) -> int:
        """A* hop count from ``room`` to ``target_room`` (unreachable = sentinel).

        Unreachable or unknown rooms sort last via a sentinel one larger than any
        possible path length, keeping the ``_choose_exit_vent`` ordering total and
        deterministic without raising on a disconnected topology.
        """

        try:
            return (
                len(find_path(public_map=public_map, start=room, goal=target_room)) - 1
            )
        except ValueError:
            return len(public_map.room_ids) + 1

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

    def _vent(self, *, vent_id: VentId) -> ActionIntent:
        return VentIntent.model_validate(
            {
                "type": "vent",
                "actor": self._agent_id,
                "payload": {"vent_id": vent_id},
            }
        )

    def _sabotage(self, *, kind: str) -> ActionIntent:
        """Build a :class:`SabotageIntent` for ``kind`` (Task 11.7).

        Mirrors :meth:`_kill` / :meth:`_vent`: stamps the impostor's own actor id
        and round-trips the sabotage ``kind`` (a map ``sabotages`` key, e.g.
        ``reactor``) verbatim. The orchestrator maps the intent to the
        engine-owned sabotage action; the policy stays engine-free.
        """

        return SabotageIntent.model_validate(
            {
                "type": "sabotage",
                "actor": self._agent_id,
                "payload": {"kind": kind},
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
        body_rooms: frozenset[RoomId],
    ) -> ActionIntent:
        if pending_task_id is None:
            return self._wait()
        task_room = public_map.task_locations.get(pending_task_id)
        if task_room is None:
            return self._wait()
        # Cover-discipline (Task 10.14, audit-2026-06-13-1816; Codex review):
        # never route the blend back into a room that holds a visible body. After
        # a kill, ``_cover`` vacates the scene; if the pretend task sits in that
        # room, routing toward it would drag the impostor straight back onto the
        # corpse — oscillating against the COVER interrupt and destroying the
        # sheltered alibi the cover exists to build. ``own_room`` never holds a
        # body here (that is the COVER branch, taken before ``_idle``), so this
        # only gates the routing/performing target; the impostor waits sheltered
        # instead until the body is reported and removed.
        if task_room in body_rooms:
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
