"""Bounded tactical comparisons over the agent's own observations.

The default FSMs remain the anchors. These explicitly constructed subclasses
replace selected choices and preserve body, task, repair and escape interrupts.
Public meeting knowledge belongs to each policy instance; speculative plans
never enter a model's evidence memory.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictBool

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_SAW_PLAYER,
    EVENT_SAW_PLAYER_MOVE,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
)
from agents.tactical.crewmate_policy import CrewmatePolicy, EmergencyButtonView
from agents.tactical.impostor_policy import ImpostorPolicy
from agents.tactical.pathing import find_path
from observation.action_intent import ActionIntent, ReportBodyIntent
from observation.public_map import PublicMapView


class TacticalExperimentOptions(BaseModel):
    """Engine-free policy switches, decomposed by the orchestrator."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    crew_idle_policy: Literal["hub_wait", "patrol", "accompany"] = "hub_wait"
    vent_exit_policy: Literal["target_distance", "observed_risk"] = "target_distance"
    post_meeting_retarget: StrictBool = False
    self_report: StrictBool = False
    sabotage_threshold: Literal["six_sevenths", "two_thirds"] = "six_sevenths"
    meeting_positions_preserved: StrictBool = True


def _visits(events: tuple[EpisodicEvent, ...]) -> dict[str, int]:
    return {
        CrewmatePolicy._room_from_self_state(event): event.tick
        for event in events
        if event.type == EVENT_SELF_STATE
    }


def _recent_players(
    events: tuple[EpisodicEvent, ...], *, tick: int
) -> dict[str, tuple[int, str, str | None]]:
    """Latest first-hand location per person, with a two-tick expiry."""

    seen: dict[str, tuple[int, str, str | None]] = {}
    for event in events:
        if event.provenance != PROVENANCE_OBSERVED or tick - event.tick > 2:
            continue
        if event.type not in (EVENT_SAW_PLAYER, EVENT_SAW_PLAYER_MOVE):
            continue
        subject = event.payload.get("player_id")
        room = event.payload.get(
            "room" if event.type == EVENT_SAW_PLAYER else "to_room"
        )
        action = event.payload.get("action")
        if not isinstance(subject, str) or not isinstance(room, str):
            raise ValueError("a first-hand player location requires subject and room")
        if action is not None and not isinstance(action, str):
            raise ValueError("an observed player action must be text or absent")
        seen[subject] = (event.tick, room, action)
    return seen


def _patrol_goal(
    events: tuple[EpisodicEvent, ...], *, own_room: str, public_map: PublicMapView
) -> str | None:
    visits = _visits(events)
    reachable: list[tuple[int, int, str]] = []
    for room in public_map.room_ids:
        if room == own_room:
            continue
        try:
            path = find_path(public_map=public_map, start=own_room, goal=room)
        except ValueError:
            continue
        reachable.append((visits.get(room, -1), len(path), room))
    return min(reachable)[2] if reachable else None


class ExperimentalCrewmatePolicy(CrewmatePolicy):
    """Replace finished-crew hub waiting with a bounded exploration choice."""

    def __init__(self, *, agent_id: str, options: TacticalExperimentOptions) -> None:
        super().__init__(agent_id=agent_id)
        self.options = options

    def decide(
        self,
        memory: MemoryStore,
        public_map: PublicMapView,
        *,
        emergency: EmergencyButtonView | None = None,
    ) -> ActionIntent:
        anchor = super().decide(memory, public_map, emergency=emergency)
        if self.options.crew_idle_policy == "hub_wait":
            return anchor
        events = memory.recent(since_tick=0)
        state = self._latest_self_state(events)
        assert state is not None  # The anchor validates this boundary.
        own_room = self._room_from_self_state(state)
        latest = tuple(event for event in events if event.tick == events[-1].tick)
        if (
            self._pending_task_from_self_state(state) is not None
            or self._first_visible_body(latest, own_room=own_room) is not None
            or self._kill_witnessed(latest, own_room=own_room)
            or self._active_gating_sabotage(events) is not None
            or (emergency is not None and emergency.is_eligible)
        ):
            return anchor
        goal = _patrol_goal(events, own_room=own_room, public_map=public_map)
        if self.options.crew_idle_policy == "accompany":
            # Join a recently observed person in a room not visited in four
            # ticks. A visit consumes that opportunity; two finished agents
            # cannot settle into an indefinite mutual-following wait.
            visits = _visits(events)
            companions = [
                (-seen_tick, subject, room)
                for subject, (seen_tick, room, _) in _recent_players(
                    events, tick=events[-1].tick
                ).items()
                if subject != self.agent_id
                and room != own_room
                and visits.get(room, -5) < events[-1].tick - 4
                and room in public_map.room_ids
            ]
            if companions:
                goal = min(companions)[2]
        if goal is None:
            return self._wait()
        return self._move_toward(public_map=public_map, own_room=own_room, goal=goal)


class ExperimentalImpostorPolicy(ImpostorPolicy):
    """Compare vent risk, route persistence, reporting and task pressure."""

    def __init__(self, *, agent_id: str, options: TacticalExperimentOptions) -> None:
        super().__init__(agent_id=agent_id)
        self.options = options
        self._announced_dead: frozenset[str] = frozenset()
        self._meeting_announced = False

    def note_meeting_concluded(self, *, dead_ids: tuple[str, ...]) -> None:
        """Accept the public meeting roster, never private death attribution."""

        self._announced_dead = frozenset(dead_ids)
        self._meeting_announced = True

    def decide(self, memory: MemoryStore, public_map: PublicMapView) -> ActionIntent:
        anchor = super().decide(memory, public_map)
        events = memory.recent(since_tick=0)
        state = self._latest_self_state(events)
        assert state is not None
        tick = events[-1].tick
        latest = tuple(event for event in events if event.tick == tick)
        own_room = self._room_from_self_state(state)
        teammates = self._fellow_impostor_ids_from_self_state(state)
        bodies = self._body_visible_rooms(latest)
        if self._in_vent_from_self_state(state):
            if self.options.vent_exit_policy == "observed_risk":
                return self._observed_risk_exit(
                    anchor,
                    events=events,
                    public_map=public_map,
                    own_room=own_room,
                    body_rooms=bodies,
                    teammates=teammates,
                )
            return anchor
        if own_room in bodies:
            if self.options.self_report:
                body_id = CrewmatePolicy._first_visible_body(latest, own_room=own_room)
                assert body_id is not None
                return ReportBodyIntent.model_validate(
                    {
                        "type": "report",
                        "actor": self.agent_id,
                        "payload": {"body_id": body_id},
                    }
                )
            return anchor
        if anchor.type in ("kill", "sabotage"):
            return anchor

        cooldown = self._latest_cooldown(latest)
        assert cooldown is not None
        targets = self._scored_targets(
            events,
            cooldown=cooldown,
            current_tick=tick,
            confirmed_dead=self._confirmed_dead_from_bodies(events)
            | self._announced_dead,
            fellow_impostor_ids=teammates,
        )
        if (
            self.options.sabotage_threshold == "two_thirds"
            and self._two_thirds_complete(events)
            and self._sabotage_window_open(events)
            and not self._active_sabotage(events)
            and not self._kill_available_now(
                latest_events=latest,
                cooldown=cooldown,
                targets=targets,
                own_room=own_room,
                fellow_impostor_ids=teammates,
            )
        ):
            return self._sabotage(kind="reactor")
        if (
            self.options.post_meeting_retarget
            and self.options.meeting_positions_preserved
            and self._meeting_announced
            and cooldown == 0
        ):
            # A meeting does not move surviving players under the preserve
            # rule. Retain recent, unrefuted leads on announced survivors.
            refuted = self._refuted_subjects(events)
            eligible = sorted(
                (target for target in targets if target.player_id not in refuted),
                key=lambda target: (
                    -target.score,
                    self._proximity_rank(
                        public_map=public_map, own_room=own_room, room=target.room
                    ),
                    target.player_id,
                ),
            )
            if eligible and eligible[0].room != own_room:
                target = eligible[0]
                anchor = self._move_toward(
                    public_map=public_map, own_room=own_room, goal=target.room
                )
        return anchor

    @staticmethod
    def _two_thirds_complete(events: tuple[EpisodicEvent, ...]) -> bool:
        status = ImpostorPolicy._latest_global_status(events)
        counts = None if status is None else ImpostorPolicy._task_counts_of(status)
        if counts is None:
            return False
        completed, total = counts
        return total > 0 and completed < total and completed * 3 >= total * 2

    def _observed_risk_exit(
        self,
        anchor: ActionIntent,
        *,
        events: tuple[EpisodicEvent, ...],
        public_map: PublicMapView,
        own_room: str,
        body_rooms: frozenset[str],
        teammates: frozenset[str],
    ) -> ActionIntent:
        current = self._vent_in_room(public_map, own_room)
        assert current is not None
        connected = tuple(sorted(public_map.vent_graph.get(current, ())))
        if not connected:
            return anchor
        pool = (
            tuple(v for v in connected if public_map.vent_rooms[v] not in body_rooms)
            or connected
        )
        tick = events[-1].tick
        risks: dict[str, int] = {}
        for subject, (seen_tick, room, _) in _recent_players(events, tick=tick).items():
            if subject != self.agent_id and subject not in teammates:
                risks[room] = risks.get(room, 0) + 3 - (tick - seen_tick)
        # Zero means no recent positive sighting, not a certified empty room.
        # Preserve the anchor on equal risk so uncertainty does not invent a
        # preferred destination or prevent leaving the vent.
        assert anchor.type == "vent"
        chosen = min(
            pool,
            key=lambda vent: (
                risks.get(public_map.vent_rooms[vent], 0),
                vent != anchor.payload.vent_id,
                vent,
            ),
        )
        return self._vent(vent_id=chosen)
