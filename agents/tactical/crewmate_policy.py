"""Crewmate tactical policy (DESIGN.md §4.4).

Implements the deterministic crewmate finite-state machine:

    IDLE -> MOVE_TO_TASK -> DO_TASK -> IDLE

with two override interrupts:

* ``BODY_VISIBLE -> REPORT`` -- a body is visible at the agent's most recent
  perception tick, so the agent files a :class:`ReportBodyIntent` for the
  alphabetically-first body id.
* ``KILL_WITNESSED -> FLEE_AND_REPORT`` -- a kill is in progress in the agent's
  current room, so the agent moves one A* step toward
  ``public_map.emergency_button_room``; if it is already there, it raises an
  :class:`EmergencyMeetingIntent`.

When the agent re-enters IDLE with no pending task (the canonical FSM step
``DO_TASK -> IDLE``) the policy routes back to ``public_map.meeting_room``
and waits there. Without this routing the agent would issue
:class:`WaitIntent` from wherever the last task happened to finish, which
strands surviving crewmates inside task rooms and prevents headless games
from terminating — the impostor's stale ``saw_player`` sightings drive it
toward the kill site, and waiting crewmates never re-enter the impostor's
visibility window so no second kill or quorum body discovery is possible.

The policy is stateless: every decision is a pure function of the agent's
:class:`MemoryStore` and the :class:`PublicMapView`. Tie-breakers use sorted
ids so replays are byte-identical, and no module under ``agents/`` imports
from ``engine/``.

Conventions consumed from perception (DESIGN.md §4.2 / §6.2):

* ``saw_body`` events at the latest tick mean a body is visible to the agent.
* ``saw_player`` events at the latest tick whose payload ``action`` field
  equals ``"kill"`` and whose ``room`` matches the agent's own room indicate
  a kill in progress that the agent has witnessed.
"""

from __future__ import annotations

from typing import Final

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SELF_STATE,
)
from agents.tactical.pathing import find_path
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    EmergencyMeetingIntent,
    MoveIntent,
    PlayerId,
    ReportBodyIntent,
    WaitIntent,
)
from observation.public_map import PublicMapView, RoomId

KILL_ACTION: Final[str] = "kill"
KILL_WITNESS_REASON: Final[str] = "kill_witnessed"


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
    ) -> ActionIntent:
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
            return self._flee_and_report(public_map=public_map, own_room=own_room)

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

    def _flee_and_report(
        self,
        *,
        public_map: PublicMapView,
        own_room: RoomId,
    ) -> ActionIntent:
        target = public_map.emergency_button_room
        if own_room == target:
            return EmergencyMeetingIntent.model_validate(
                {
                    "type": "emergency",
                    "actor": self._agent_id,
                    "payload": {"reason": KILL_WITNESS_REASON},
                }
            )
        return self._move_toward(public_map=public_map, own_room=own_room, goal=target)

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


__all__ = ["KILL_ACTION", "KILL_WITNESS_REASON", "CrewmatePolicy"]
