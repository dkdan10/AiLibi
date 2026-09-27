"""Bounded tactical comparisons over the agent's own observations.

The default FSMs remain the anchors. These explicitly constructed subclasses
replace selected choices and preserve body, task, repair and escape interrupts.
Public meeting knowledge belongs to each policy instance; speculative plans
never enter a model's evidence memory.

Two vent values change how an experimental impostor hides and nothing else:
``vent_exit_policy = "look_and_wait"`` looks before it leaves a vent, and
``vent_entry_policy = "own_fresh_kill"`` dives into a vent only beside its own
fresh kill. Both read only the impostor's memory rows and the public map. Their
window and cap are the named constants below, frozen once a round records them.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, StrictBool, field_validator, model_validator

from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.perception import (
    EVENT_OWN_KILL,
    EVENT_SAW_BODY,
    EVENT_SAW_PLAYER,
    EVENT_SAW_PLAYER_MOVE,
    EVENT_SELF_STATE,
    PROVENANCE_OBSERVED,
)
from agents.tactical.crewmate_policy import CrewmatePolicy, EmergencyButtonView
from agents.tactical.impostor_policy import ImpostorPolicy
from agents.tactical.pathing import find_path
from observation.action_intent import ActionIntent, PlayerId, ReportBodyIntent
from observation.public_map import PublicMapView, RoomId, VentId

#: The frozen meaning of ``vent_entry_policy = "own_fresh_kill"``: the impostor
#: enters a vent only when a body in its room is its own victim, killed at most
#: this many engine ticks before the entry with no meeting between. The census
#: counts the same window (``eval.gameplay_census.FRESH_KILL_WINDOW_TICKS``); a
#: test pins the two equal. A revision adds a new value, never a new window.
FRESH_KILL_WINDOW_TICKS: Final[int] = 3

#: The frozen meaning of ``vent_exit_policy = "look_and_wait"``: the most play
#: ticks an impostor stays inside a vent, counted from its entry or from the
#: last meeting boundary, whichever is later. At this count it surfaces whatever
#: it sees. The census's ``IN_VENT_CAP_TICKS`` is pinned equal to it.
IN_VENT_CAP_TICKS: Final[int] = 4

# The post-meeting episodic marker (``agents.memory.store._EVENT_MEETING_BOUNDARY``),
# mirrored so no private name crosses a module boundary; a test pins the two.
_MEETING_BOUNDARY_EVENT: Final[str] = "meeting_boundary"

# An ``own_kill`` snapshot row lands on the observation after the kill: the
# engine resolves the kill during tick K and advances the state to K + 1 before
# the next packet is built (``engine.tick.advance_tick``), so the row's tick is
# the kill's engine tick plus this lag.
_OWN_KILL_ROW_LAG_TICKS: Final[int] = 1

# An event-time row carries this payload key (``agents.perception`` stamps it on
# every temporal-observation row). Such a row is dated at its source tick, not
# one observation later, so the entry gate refuses it rather than misdate a kill.
_EVENT_TIME_ROW_KEY: Final[str] = "source_event_id"


class TacticalExperimentOptions(BaseModel):
    """Engine-free policy switches, decomposed by the orchestrator."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    crew_idle_policy: Literal["hub_wait", "patrol", "accompany"] = "hub_wait"
    vent_exit_policy: Literal["target_distance", "observed_risk", "look_and_wait"] = (
        "target_distance"
    )
    vent_entry_policy: Literal["any_body", "own_fresh_kill"] = "any_body"
    post_meeting_retarget: StrictBool = False
    self_report: StrictBool = False
    sabotage_threshold: Literal["six_sevenths", "two_thirds"] = "six_sevenths"
    meeting_positions_preserved: StrictBool = True
    investigation_version: Literal[1] | None = None
    contextual_self_report_version: Literal[1] | None = None

    @field_validator(
        "investigation_version", "contextual_self_report_version", mode="before"
    )
    @classmethod
    def _strict_version(cls, value: object) -> object:
        if value is not None and type(value) is not int:
            raise ValueError("tactical versions must be integers")
        return value

    @model_validator(mode="after")
    def _independent_choices(self) -> TacticalExperimentOptions:
        if (
            self.investigation_version is not None
            and self.crew_idle_policy != "hub_wait"
        ):
            raise ValueError("investigation conflicts with the old crew idle policy")
        if self.contextual_self_report_version is not None and self.self_report:
            raise ValueError(
                "contextual reporting conflicts with unconditional reporting"
            )
        return self


#: Option values declared ahead of their behaviour. A policy built with one
#: raises instead of running the default decision under the arm's name; the
#: card that builds a value's behaviour deletes it here. Empty since the
#: look-and-wait card built ``look_and_wait`` and ``own_fresh_kill``; the arm
#: spine's pending-equals-unbuilt test still reads it, and the card that deletes
#: ``WAVE_ARMS_PENDING`` deletes this guard with that test.
UNBUILT_OPTION_VALUES: Final[Mapping[str, frozenset[str]]] = MappingProxyType({})


class UnbuiltTacticalOptionError(ValueError):
    """A declared tactical option value whose behaviour does not exist yet."""


def _refuse_unbuilt_options(options: TacticalExperimentOptions) -> None:
    for field, unbuilt in UNBUILT_OPTION_VALUES.items():
        value = getattr(options, field)
        if value in unbuilt:
            raise UnbuiltTacticalOptionError(
                f"{field}={value!r} is declared but its policy behaviour is not "
                "built; building a policy with it would run the default instead"
            )


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


def inferred_visible_rooms(
    public_map: PublicMapView, room: RoomId, *, sabotage_active: bool
) -> frozenset[RoomId]:
    """The rooms an impostor inside the vent in ``room`` infers it can see.

    The agent receives no visible-room list, so this is inferred from the public
    map: the room itself and its map neighbours, or the room alone while any
    sabotage is active. A test pins it to the engine's sight for an impostor
    observer at base visibility and under lights. Under a reactor sabotage the
    engine still shows the neighbours, so there this set is narrower than what
    the engine shows: a neighbour counts as unseen.
    """

    neighbours = public_map.room_neighbors.get(room)
    if neighbours is None:
        raise ValueError(f"the public map lists no neighbours for room {room!r}")
    if sabotage_active:
        return frozenset({room})
    return frozenset({room, *neighbours})


def _watchers_by_room(
    latest: tuple[EpisodicEvent, ...],
    *,
    visible: frozenset[RoomId],
    not_watchers: frozenset[PlayerId],
) -> dict[RoomId, int]:
    """Non-teammates sighted first-hand this tick, counted per visible room.

    Only a ``saw_player`` row of observed provenance counts; the caller passes
    the impostor itself and its fellow impostors as ``not_watchers``. A sighting
    outside ``visible`` is not read, so under a sabotage a neighbour the engine
    still shows is treated as unseen.
    """

    seen: dict[RoomId, set[PlayerId]] = {}
    for event in latest:
        if event.type != EVENT_SAW_PLAYER or event.provenance != PROVENANCE_OBSERVED:
            continue
        subject = ImpostorPolicy._sighting_subject(event)
        room = ImpostorPolicy._sighting_room(event)
        if subject in not_watchers or room not in visible:
            continue
        seen.setdefault(room, set()).add(subject)
    return {room: len(subjects) for room, subjects in seen.items()}


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
    """Compare vent risk, route persistence, reporting and task pressure.

    Under ``look_and_wait`` an impostor inside a vent surfaces only when no
    non-teammate is sighted in a room it infers it can see, and at the in-vent
    cap it surfaces whatever it sees (:meth:`_look_and_wait_exit`). Under
    ``own_fresh_kill`` it enters a vent only beside its own fresh kill and
    otherwise walks away as the default cover does (:meth:`_own_fresh_kill_here`).
    """

    def __init__(self, *, agent_id: str, options: TacticalExperimentOptions) -> None:
        _refuse_unbuilt_options(options)
        super().__init__(agent_id=agent_id)
        self.options = options
        self._announced_dead: frozenset[str] = frozenset()
        self._meeting_announced = False

    def note_meeting_concluded(self, *, dead_ids: tuple[str, ...]) -> None:
        """Accept the public meeting roster, never private death attribution."""

        self._announced_dead = frozenset(dead_ids)
        self._meeting_announced = True

    def decide(self, memory: MemoryStore, public_map: PublicMapView) -> ActionIntent:
        events = memory.recent(since_tick=0)
        if self.options.vent_exit_policy == "look_and_wait":
            # Decided before the anchor, so nothing inside the vent reads the
            # kill ranking. A memory with no self_state falls through to the
            # anchor, which refuses it. Inside a vent, the anchor's row checks
            # run first (:meth:`_refuse_rows_the_anchor_refuses`), so every row
            # the anchor refuses before its in-vent exit is refused here too.
            inside = self._latest_self_state(events)
            if inside is not None and self._in_vent_from_self_state(inside):
                self._refuse_rows_the_anchor_refuses(events, state=inside)
                return self._look_and_wait_exit(
                    events, public_map=public_map, state=inside
                )
        anchor = super().decide(memory, public_map)
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
            if self.options.self_report or (
                self.options.contextual_self_report_version == 1
                and self._contextual_report(
                    anchor,
                    latest=latest,
                    tick=tick,
                    own_room=own_room,
                    teammates=teammates,
                    public_map=public_map,
                )
            ):
                body_id = CrewmatePolicy._first_visible_body(latest, own_room=own_room)
                assert body_id is not None
                return ReportBodyIntent.model_validate(
                    {
                        "type": "report",
                        "actor": self.agent_id,
                        "payload": {"body_id": body_id},
                    }
                )
            if (
                self.options.vent_entry_policy == "own_fresh_kill"
                and not self._own_fresh_kill_here(
                    events, latest=latest, own_room=own_room, tick=tick
                )
            ):
                # Any body but the impostor's own fresh kill: the default cover's
                # walk-away move. The anchor here is that vent or that move
                # already (``ImpostorPolicy._cover_or_vent``), so only a vent
                # entry changes.
                return self._cover(public_map=public_map, own_room=own_room)
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

    def _contextual_report(
        self,
        anchor: ActionIntent,
        *,
        latest: tuple[EpisodicEvent, ...],
        tick: int,
        own_room: str,
        teammates: frozenset[str],
        public_map: PublicMapView,
    ) -> bool:
        """Compare reporting with escape using current own-room observations."""

        escape = (
            anchor.type == "move"
            and anchor.payload.to_room in public_map.room_neighbors[own_room]
        ) or (
            anchor.type == "vent"
            and public_map.vent_rooms.get(anchor.payload.vent_id) == own_room
        )
        if not escape:
            return True
        cooldown = self._latest_cooldown(latest)
        if cooldown is None:
            raise ValueError("contextual reporting requires current own cooldown")
        nearby = any(
            event.type == EVENT_SAW_PLAYER
            and event.provenance == PROVENANCE_OBSERVED
            and event.payload.get("source_tick") == tick
            and event.payload.get("observation_phase") == "snapshot"
            and event.payload.get("room") == own_room
            and event.payload.get("player_id") not in teammates | {self.agent_id}
            for event in latest
        )
        return nearby and cooldown > 0

    @staticmethod
    def _refuse_rows_the_anchor_refuses(
        events: tuple[EpisodicEvent, ...], *, state: EpisodicEvent
    ) -> None:
        """Raise, with the anchor's message, on a row the anchor refuses in a vent.

        ``ImpostorPolicy.decide`` validates these rows before its in-vent exit:
        the pending task on the latest ``self_state`` as it reads that row, and,
        while it builds the kill ranking, the room of every ``self_state`` row,
        the victim of every ``saw_body`` row and the subject and room of every
        ``saw_player`` row of any provenance. This runs the anchor's own readers
        over them and builds no ranking. :meth:`_look_and_wait_exit` reads the
        anchor's other in-vent inputs itself: the latest ``self_state``'s room
        and fellow ids, the cooldown, this tick's body rooms and the vent in the
        impostor's room.
        """

        ImpostorPolicy._pending_task_from_self_state(state)
        ImpostorPolicy._confirmed_dead_from_bodies(events)
        for event in events:
            if event.type == EVENT_SELF_STATE:
                ImpostorPolicy._room_from_self_state(event)
            elif event.type == EVENT_SAW_PLAYER:
                ImpostorPolicy._sighting_subject(event)
                ImpostorPolicy._sighting_room(event)

    def _look_and_wait_exit(
        self,
        events: tuple[EpisodicEvent, ...],
        *,
        public_map: PublicMapView,
        state: EpisodicEvent,
    ) -> ActionIntent:
        """Look before leaving the vent: surface clear, wait, or surface at the cap.

        Before the cap it surfaces only when no non-teammate is sighted first-hand
        this tick in any room of :func:`inferred_visible_rooms`: in place, or at a
        visible connected vent whose room ranks better on (a body there, the room
        fled from, vent id). The room fled from is the vent's own room, since an
        impostor inside never changes vents without surfacing, so a clear
        connected room beats in place unless only it holds a body. Otherwise it
        waits. At :data:`IN_VENT_CAP_TICKS` ticks inside it surfaces at the
        candidate ranked first by the cap key (:meth:`_cap_exit`). It never reads
        a target sighting from an earlier tick.
        """

        tick = events[-1].tick
        latest = tuple(event for event in events if event.tick == tick)
        if self._latest_cooldown(latest) is None:
            raise ValueError(
                "impostor policy requires a cooldown_status event at the latest tick"
            )
        own_room = self._room_from_self_state(state)
        current = self._vent_in_room(public_map, own_room)
        if current is None:
            raise ValueError(
                f"impostor is in_vent but no vent maps to its room: {own_room!r}"
            )
        connected = tuple(sorted(public_map.vent_graph.get(current, ())))
        unmapped = [vent for vent in connected if vent not in public_map.vent_rooms]
        if unmapped:
            raise ValueError(f"connected vents with no room on the map: {unmapped!r}")
        visible = inferred_visible_rooms(
            public_map, own_room, sabotage_active=self._active_sabotage(events)
        )
        watchers = _watchers_by_room(
            latest,
            visible=visible,
            not_watchers=self._fellow_impostor_ids_from_self_state(state)
            | {self.agent_id},
        )
        bodies = self._body_visible_rooms(latest) & visible
        if self._ticks_inside(events) >= IN_VENT_CAP_TICKS:
            return self._vent(
                vent_id=self._cap_exit(
                    current=current,
                    connected=connected,
                    public_map=public_map,
                    visible=visible,
                    watchers=watchers,
                    bodies=bodies,
                    fled_room=own_room,
                )
            )
        if watchers:
            return self._wait()
        clear = (
            current,
            *(vent for vent in connected if public_map.vent_rooms[vent] in visible),
        )
        return self._vent(
            vent_id=min(
                clear,
                key=lambda vent: (
                    public_map.vent_rooms[vent] in bodies,
                    public_map.vent_rooms[vent] == own_room,
                    vent,
                ),
            )
        )

    @staticmethod
    def _cap_exit(
        *,
        current: VentId,
        connected: tuple[VentId, ...],
        public_map: PublicMapView,
        visible: frozenset[RoomId],
        watchers: Mapping[RoomId, int],
        bodies: frozenset[RoomId],
        fled_room: RoomId,
    ) -> VentId:
        """The forced exit at the cap, by the key ruled on 2026-09-24.

        Each candidate (in place, or a connected vent) is classed by the
        impostor's inferred sight this tick: clear (visible, no non-teammate
        sighted there) before unseen (outside the inferred-visible set) before
        watched (visible, a non-teammate sighted there). Within a class: fewer
        sighted non-teammates, then a room with no body, then a room other than
        the one fled from, then a connected vent before in place, then vent id.
        """

        def key(vent: VentId) -> tuple[int, int, bool, bool, bool, VentId]:
            room = public_map.vent_rooms[vent]
            sighted = watchers.get(room, 0)
            if sighted:
                sight_class = 2
            elif room in visible:
                sight_class = 0
            else:
                sight_class = 1
            return (
                sight_class,
                sighted,
                room in bodies,
                room == fled_room,
                vent == current,
                vent,
            )

        return min((current, *connected), key=key)

    @staticmethod
    def _ticks_inside(events: tuple[EpisodicEvent, ...]) -> int:
        """Play ticks inside the current vent, read from memory rows alone.

        The trailing run of ``self_state`` rows that place the impostor in a
        vent, counted back to the last ``meeting_boundary`` row, which the
        post-meeting fold appends before the resume tick's perception. The
        first observation inside counts 1, so the count equals the census's
        ticks inside at the tick an exit would resolve.
        """

        inside = 0
        for event in reversed(events):
            if event.type == _MEETING_BOUNDARY_EVENT:
                break
            if event.type != EVENT_SELF_STATE:
                continue
            if not ImpostorPolicy._in_vent_from_self_state(event):
                break
            inside += 1
        return inside

    @staticmethod
    def _own_fresh_kill_here(
        events: tuple[EpisodicEvent, ...],
        *,
        latest: tuple[EpisodicEvent, ...],
        own_room: RoomId,
        tick: int,
    ) -> bool:
        """Whether a body in ``own_room`` is this impostor's own fresh kill.

        Fresh means killed at most :data:`FRESH_KILL_WINDOW_TICKS` engine ticks
        before an entry at ``tick``, with no meeting between. The kill's engine
        tick is its ``own_kill`` row's tick less :data:`_OWN_KILL_ROW_LAG_TICKS`.
        A meeting at or after the kill puts its boundary row on or after the
        kill's row tick, since a kill on a meeting's trigger tick is perceived
        on the resume tick. The victim's body must be sighted in ``own_room``
        this tick. An event-time ``own_kill`` row (temporal observations) raises.
        """

        boundary = max(
            (event.tick for event in events if event.type == _MEETING_BOUNDARY_EVENT),
            default=None,
        )
        # The anchor has already refused a saw_body row without a string room or
        # victim, so these reads cannot meet a malformed row.
        victims_here = {
            event.payload["victim_id"]
            for event in latest
            if event.type == EVENT_SAW_BODY and event.payload["room"] == own_room
        }
        for event in events:
            if event.type != EVENT_OWN_KILL:
                continue
            if _EVENT_TIME_ROW_KEY in event.payload:
                raise ValueError(
                    "the own-fresh-kill entry gate dates a kill from snapshot "
                    "own_kill rows; an event-time row is not supported"
                )
            victim = event.payload.get("victim_id")
            room = event.payload.get("room")
            if not isinstance(victim, str) or not isinstance(room, str):
                raise ValueError(
                    f"own_kill event missing string victim_id or room: {event.payload!r}"
                )
            kill_tick = event.tick - _OWN_KILL_ROW_LAG_TICKS
            if tick - kill_tick > FRESH_KILL_WINDOW_TICKS:
                continue
            if boundary is not None and boundary >= event.tick:
                continue
            if room == own_room and victim in victims_here:
                return True
        return False

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
