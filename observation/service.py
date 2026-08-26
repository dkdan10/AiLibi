from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from engine.entities import PlayerId
from engine.events import (
    ActionRejectedEvent,
    EngineEvent,
    KilledEvent,
    MovedEvent,
    TaskCompletedEvent,
    TaskProgressedEvent,
    VentEnteredEvent,
    VentExitedEvent,
)
from engine.visibility import VisibilityResult, compute_visibility_for_player
from engine.world import Map, RoomId, TaskId, WorldState
from observation.audit import ObservationAuditLog
from observation.packet import (
    AudibleEvent,
    BodyView,
    GlobalView,
    MovedPlayerView,
    ObservationPacket,
    OwnKillView,
    PlayerView,
    SelfView,
)

# -- Impostor blending: the pretend-task channel (Task 10.14, DESIGN.md §3.4,
# §4.5; audit-2026-06-13-1816 D-D-1) ----------------------------------------
#
# Impostors own no task instances (the seeder assigns tasks to crewmates only),
# so ``_pending_task_id_for_agent``'s owner filter left every impostor packet
# with ``pending_task_id=None`` and the dormant ``ImpostorPolicy._idle`` do_task
# branch never fired: impostors waited ~51% of ticks vs the crew's ~12% — the
# "never-tasks" fingerprint. The blending lever surfaces a PRETEND map task id
# on the impostor's privileged self channel so that branch fires and the
# impostor moves to / "performs" a real task like a crewmate would.
#
# The fake-task SENTINEL is structural, not a string marker: the pretend id is a
# bare MAP task id drawn from ``game_map.tasks`` and surfaced ONLY on
# ``SelfView`` — it is NEVER minted as a ``WorldState.tasks`` instance. So the
# crew-side integrity invariant holds by construction: ``GlobalView`` counts
# ``len(world_state.tasks)`` (the win denominator), which never sees a pretend
# id, and when the impostor emits ``do_task`` against it the engine's
# ``_resolve_owned_task_instance`` finds no owned instance and rejects the action
# (no progress, no instance) — a fake task can never advance the real counter or
# help the crew win (verified offline in tests/observation). The pretend id is
# the contract's ``PRETEND_TASK_MARKER`` (named ``impostor_pretend_task_id`` per
# "or equivalent"); downstream eval (10.17) imports it to identify pretend tasks.
#
# The blend roams a small per-impostor SET (the contract's "small per-impostor
# pretend-task set"): each seat draws a disjoint window of the sorted map tasks
# and rotates through it by ``tick // dwell``, so the impostor moves room-to-room
# like a crewmate working its task list rather than camping one room. Camping a
# single fixed room is BOTH a weaker blend and, empirically, a degenerate balance
# shift (a systematic ambush in the same rooms every game), so the roam is kept.
#
# The rotation is reconciled with the memory renderer: ``agents/memory/store.py``
# must never render a "You completed {task}" observation for a pretend id, so the
# impostor's memory stays accurate and alibi fabrication is the LLM's job at the
# meeting (DESIGN.md §4.7). It reads a completion off an id LEAVING
# ``owned_task_ids``, which the constant camouflage window below never does — so
# the property holds for both roles by construction. Seats are taken over ALL role==IMPOSTOR players (alive or dead —
# ejection marks ``alive=False`` but never removes the player), so a seat never
# shifts mid-game when a teammate is ejected.
IMPOSTOR_PRETEND_TASK_SET_SIZE: Final[int] = 3
# How many ticks the impostor dwells on one pretend task before the deterministic
# rotation advances to the next in its per-seat set. Anchored above the map
# diameter and the kill cooldown so the impostor reaches and "performs" a task
# within a window (no per-tick re-route oscillation), then roams to the next.
# Re-derived at 10.17 against the toolkit-shifted kill cadence.
IMPOSTOR_PRETEND_TASK_DWELL_TICKS: Final[int] = 6


def _impostor_pretend_window(
    *,
    game_map: Map,
    agent_id: PlayerId,
    impostor_ids: Sequence[PlayerId],
) -> list[TaskId]:
    """Build one impostor seat's CONSTRUCTION-ORDER pretend-task window (Task 10.14).

    The tick-independent per-seat blend window both the rotating
    :func:`impostor_pretend_task_id` and the sorted :func:`impostor_pretend_task_set`
    derive from, factored out so the single-id rotator and the set surface CANNOT
    drift (Task 15.22). Each seat (the agent's index in the sorted impostor
    roster) draws a disjoint window of ``IMPOSTOR_PRETEND_TASK_SET_SIZE``
    consecutive sorted map ids starting at ``offset = (seat * size) % n`` and
    wrapping, deduped in append order. Returns the window in CONSTRUCTION order
    (NOT sorted — the rotator indexes it positionally) and ``[]`` for a task-less
    map.

    Fail-loud (AGENTS.md no silent fallbacks): ``agent_id`` MUST be a member of
    ``impostor_ids``. A non-member is a caller wiring error (a filtered or stale
    roster) — it raises rather than silently reusing seat 0's window and masking
    the bug (Codex review, PR #155). A task-less map short-circuits to ``[]``
    before the seat lookup, preserving the pre-refactor ``None`` behavior for the
    degenerate map.
    """

    map_task_ids = sorted(game_map.tasks)
    n = len(map_task_ids)
    if n == 0:
        return []
    sorted_impostors = sorted(impostor_ids)
    if agent_id not in sorted_impostors:
        raise ValueError(
            f"impostor_pretend_task_id called for {agent_id!r}, which is not in "
            f"impostor_ids {tuple(sorted_impostors)!r} (caller wiring error)"
        )
    seat = sorted_impostors.index(agent_id)
    offset = (seat * IMPOSTOR_PRETEND_TASK_SET_SIZE) % n
    window: list[TaskId] = []
    for i in range(min(IMPOSTOR_PRETEND_TASK_SET_SIZE, n)):
        candidate = map_task_ids[(offset + i) % n]
        if candidate not in window:
            window.append(candidate)
    return window


def impostor_pretend_task_id(
    *,
    game_map: Map,
    agent_id: PlayerId,
    impostor_ids: Sequence[PlayerId],
    tick: int,
) -> TaskId | None:
    """Deterministically select an impostor's current PRETEND map task id.

    The blending sentinel (Task 10.14). Returns a bare ``game_map.tasks`` map
    task id — never a ``WorldState.tasks`` instance id and never an owned
    instance (impostors own none) — so the engine rejects the resulting
    ``do_task`` and the win denominator never counts it (see the module note).

    Determinism / replay safety: each seat (the agent's index in the sorted
    impostor roster) draws a stable, disjoint per-impostor window of the sorted
    map tasks (:func:`_impostor_pretend_window`) and rotates through it purely by
    ``tick // dwell``. No RNG, no module state — the same
    ``(game_map, agent_id, impostor_ids, tick)`` always yields the same id,
    keeping replay reconstruction byte-identical. The rotation is safe for the
    renderer because its completion inference is role-gated to crewmates (see the
    module note). Returns ``None`` only for a task-less map. The window is indexed
    in CONSTRUCTION order (not sorted), so this rotation is byte-identical to the
    pre-refactor inline construction.

    Fail-loud (AGENTS.md no silent fallbacks): ``agent_id`` MUST be a member of
    ``impostor_ids`` (raised by :func:`_impostor_pretend_window`).
    """

    window = _impostor_pretend_window(
        game_map=game_map, agent_id=agent_id, impostor_ids=impostor_ids
    )
    if not window:
        return None
    index = (tick // IMPOSTOR_PRETEND_TASK_DWELL_TICKS) % len(window)
    return window[index]


def impostor_pretend_task_set(
    *,
    game_map: Map,
    agent_id: PlayerId,
    impostor_ids: Sequence[PlayerId],
) -> tuple[TaskId, ...]:
    """The impostor's camouflage set for ``SelfView.owned_task_ids`` (Task 15.22).

    The full per-seat pretend WINDOW the rotating ``pending_task_id`` is drawn
    from (:func:`_impostor_pretend_window`), SORTED ascending — because a
    crewmate's owned set is always ascending and the raw construction-order
    window can wrap past the sorted-map-id boundary, so an unsorted wrapped
    window would be an ordering tell that made the field role-distinguishable.
    Contains every id :func:`impostor_pretend_task_id` can return for this seat,
    tick-independent. Never minted as a ``WorldState.tasks`` instance (the
    module-note integrity invariant); ``()`` for a task-less map.
    """

    return tuple(
        sorted(
            _impostor_pretend_window(
                game_map=game_map, agent_id=agent_id, impostor_ids=impostor_ids
            )
        )
    )


@dataclass(frozen=True)
class _ObservedAction:
    action: str
    room: str
    audible_room: str | None = None


class ObservationService:
    """Single boundary object that exposes engine truth as ObservationPackets."""

    def __init__(self, *, game_map: Map, audit_log_path: Path) -> None:
        self._game_map = game_map
        self._audit_log = ObservationAuditLog(audit_log_path)

    def close(self) -> None:
        """Release the audit log's append handle (idempotent).

        The service owns the :class:`ObservationAuditLog`; closing it flushes
        and releases the file descriptor at end of game. Builds after a close
        re-open the handle lazily, so close is safe to call between batches.
        """

        self._audit_log.close()

    def build_packet(
        self,
        *,
        world_state: WorldState,
        agent_id: PlayerId,
        engine_events: Sequence[EngineEvent],
    ) -> ObservationPacket:
        visibility = compute_visibility_for_player(
            observer_id=agent_id,
            world_state=world_state,
            game_map=self._game_map,
        )
        packet = self._build_packet_from_visibility(
            world_state=world_state,
            agent_id=agent_id,
            visibility=visibility,
            engine_events=engine_events,
        )
        self._audit_log.record_packet(packet)
        return packet

    def _build_packet_from_visibility(
        self,
        *,
        world_state: WorldState,
        agent_id: PlayerId,
        visibility: VisibilityResult,
        engine_events: Sequence[EngineEvent],
    ) -> ObservationPacket:
        player = world_state.players.get(agent_id)
        if player is None:
            raise ValueError(f"unknown agent id: {agent_id}")

        pending_task_id = self._pending_task_id_for_agent(
            world_state=world_state, agent_id=agent_id
        )
        owned_task_ids = self._owned_task_ids_for_agent(
            world_state=world_state, agent_id=agent_id
        )
        observed_actions = self._observed_actions_for_agent(
            agent_id=agent_id,
            world_state=world_state,
            visibility=visibility,
            engine_events=engine_events,
        )
        own_kill = self._own_kill_for_agent(
            agent_id=agent_id,
            engine_events=engine_events,
        )
        visible_players = self._visible_players(
            world_state=world_state,
            visibility=visibility,
            observed_actions=observed_actions,
        )
        moved_players = self._moved_players_for_agent(
            visibility=visibility,
            engine_events=engine_events,
        )
        cooldown = (
            world_state.cooldowns.get(agent_id) if player.role == "IMPOSTOR" else None
        )
        # Mutual-awareness substrate (Task 7.2, DESIGN.md §1.3, locked
        # decision 3): an impostor learns its fellow impostor(s) at game start
        # so it never accuses or votes a teammate in meetings. This is a pure,
        # role-derived value -- sorted for replay stability, independent of
        # visibility/alive state (the identity is known even after a teammate
        # dies) -- and lives only on the privileged self channel, never on
        # ``visible_players``. Crewmates and a sole impostor get ``()``.
        fellow_impostor_ids = (
            tuple(
                sorted(
                    other_id
                    for other_id, other in world_state.players.items()
                    if other.role == "IMPOSTOR" and other_id != agent_id
                )
            )
            if player.role == "IMPOSTOR"
            else ()
        )
        visible_bodies = tuple(
            BodyView(
                id=body_id,
                room=world_state.bodies[body_id].room,
                victim_id=world_state.bodies[body_id].player_id,
            )
            for body_id in visibility.visible_body_ids
        )
        packet = ObservationPacket(
            tick=world_state.tick,
            agent_id=agent_id,
            self_state=SelfView(
                room=player.room,
                role=player.role,
                pending_task_id=pending_task_id,
                owned_task_ids=owned_task_ids,
                fellow_impostor_ids=fellow_impostor_ids,
                in_vent=player.in_vent,
                own_kill=own_kill,
            ),
            visible_players=visible_players,
            visible_bodies=visible_bodies,
            audible_events=self._audible_events(
                world_state=world_state,
                observed_actions=observed_actions,
            ),
            global_state=self._global_view(world_state=world_state),
            cooldown=cooldown,
            moved_players=moved_players,
        )
        return packet

    def _visible_players(
        self,
        *,
        world_state: WorldState,
        visibility: VisibilityResult,
        observed_actions: Mapping[PlayerId, _ObservedAction],
    ) -> tuple[PlayerView, ...]:
        visible_players_by_id: dict[PlayerId, PlayerView] = {}
        for player_id in visibility.visible_player_ids:
            observed_action = observed_actions.get(player_id)
            visible_players_by_id[player_id] = PlayerView(
                id=player_id,
                room=observed_action.room
                if observed_action is not None
                else world_state.players[player_id].room,
                action=observed_action.action if observed_action is not None else None,
            )

        for player_id, observed_action in observed_actions.items():
            if player_id not in world_state.players:
                raise ValueError(f"event references unknown actor: {player_id}")
            if player_id not in visible_players_by_id:
                visible_players_by_id[player_id] = PlayerView(
                    id=player_id,
                    room=observed_action.room,
                    action=observed_action.action,
                )

        return tuple(
            visible_players_by_id[player_id]
            for player_id in sorted(visible_players_by_id)
        )

    def _audible_events(
        self,
        *,
        world_state: WorldState,
        observed_actions: Mapping[PlayerId, _ObservedAction],
    ) -> tuple[AudibleEvent, ...]:
        events: list[AudibleEvent] = []
        vent_rooms = tuple(
            sorted(
                {
                    observed_action.audible_room
                    for observed_action in observed_actions.values()
                    if observed_action.action == "vent"
                    and observed_action.audible_room is not None
                }
            )
        )
        events.extend(
            AudibleEvent(kind="vent_use_heard", room=room) for room in vent_rooms
        )
        if world_state.sabotage is not None and world_state.sabotage.active:
            events.append(AudibleEvent(kind="sabotage_alarm", room=None))
        return tuple(events)

    def _observed_actions_for_agent(
        self,
        *,
        agent_id: PlayerId,
        world_state: WorldState,
        visibility: VisibilityResult,
        engine_events: Sequence[EngineEvent],
    ) -> dict[PlayerId, _ObservedAction]:
        """Per-actor activity the observer perceives this tick (DESIGN.md §1.3).

        Two distinct gates, by the action's role-sensitivity:

        * ``kill`` / ``vent`` are WITNESS-gated -- surfaced only when the engine
          recorded ``agent_id`` among the event's witnesses, and ONLY from a
          RESOLVED event (a ``KilledEvent`` / ``Vent*Event``). A rejected kill or
          vent never produces such an event, so it can never surface here -- the
          impostor-exclusive intent stays hidden.
        * ``do_task`` is VISION-gated and role-BLIND (Task 13.9, the fake-task
          lever). Every role tasks, so a SUBMITTED ``do_task`` this tick surfaces
          to any observer who can currently see the actor, regardless of
          resolution: a RESOLVED task (``TaskProgressed`` / ``TaskCompleted``) and
          a REJECTED one (``ActionRejected`` with ``action == "do_task"`` -- an
          impostor's instance-less pretend task, or a crew task the engine
          declined) both stamp ``action="task"``, BYTE-IDENTICAL. Reading the
          tick's task events (not the resolved ``last_action``) is what lets a
          rejected attempt still count; only ``do_task`` rejections are read, so a
          rejected ``kill`` / ``vent`` / ``sabotage`` ``ActionRejectedEvent`` never
          surfaces (it would leak the actor's impostor-exclusive intent).
        """

        observed_actions: dict[PlayerId, _ObservedAction] = {}
        task_actor_ids: set[PlayerId] = set()
        for event in engine_events:
            if isinstance(event, KilledEvent):
                if agent_id in event.witnesses:
                    observed_actions[event.actor] = _ObservedAction(
                        action="kill",
                        room=event.room,
                    )
            elif isinstance(event, (VentEnteredEvent, VentExitedEvent)):
                vent_observation = self._vent_observation_for_agent(
                    event=event,
                    agent_id=agent_id,
                )
                if vent_observation is not None:
                    observed_actions[event.actor] = vent_observation
            elif isinstance(event, (TaskProgressedEvent, TaskCompletedEvent)):
                task_actor_ids.add(event.actor)
            elif isinstance(event, ActionRejectedEvent) and event.action == "do_task":
                task_actor_ids.add(event.actor)

        # Stamp ``action="task"`` on every do_task actor the observer can SEE.
        # ``visibility.visible_player_ids`` already excludes the observer itself,
        # the dead, the vented, and out-of-room players, so this is the vision
        # gate. A witness-gated kill/vent already claimed the slot wins (a player
        # submits one action per tick, so this is only ever defensive). The room
        # is the actor's CURRENT room -- a task does not move its actor, and the
        # actor is co-located/visible by construction.
        visible_player_ids = set(visibility.visible_player_ids)
        for actor_id in sorted(task_actor_ids):
            if actor_id not in visible_player_ids or actor_id in observed_actions:
                continue
            actor = world_state.players.get(actor_id)
            if actor is None:
                continue
            observed_actions[actor_id] = _ObservedAction(
                action="task",
                room=actor.room,
            )
        return observed_actions

    def _moved_players_for_agent(
        self,
        *,
        visibility: VisibilityResult,
        engine_events: Sequence[EngineEvent],
    ) -> tuple[MovedPlayerView, ...]:
        """Room→room transitions the observer DIRECTLY witnessed this tick.

        Movement perception (Task 13.5.4, 2026-06-25 memory diagnosis). The
        engine emits a ``MovedEvent`` (from_room→to_room) per move; this surfaces
        it to an observer who WITNESSED THE TRANSITION -- gated on the observer
        being able to see the DEPARTURE room (``event.from_room`` in
        ``visibility.visible_rooms``), not merely the actor's post-move position.
        ``MovedEvent`` carries no witness set (unlike a kill/vent), and gating on
        the post-advance ``visible_player_ids`` (the actor's ``to_room``) was
        wrong (Codex P2): it attributed the origin to an observer who only saw
        the ARRIVAL -- leaking ``from_room`` to a late-arriver -- and dropped the
        departure for an observer left behind in ``from_room`` who actually saw
        the actor leave. Seeing the source room IS the departure-witness
        condition (in the room-graph an observer in / adjacent-to ``from_room``
        saw the actor there and saw it leave), so the §1.3 / §4.7 firewall and
        the leak suite hold: a transition the observer could not witness never
        appears, and an observer who only saw the arrival still gets the plain
        ``saw_player`` for ``to_room`` (just not the origin). A no-op move
        (``from_room == to_room``) is not a transition and is skipped.

        Unconditional since Task 14.9 (the adopted 13.5.4 lever is the default
        substrate; the ``AILIBI_MOVEMENT_PERCEPTION`` gate is retired). The
        result is sorted by actor id for replay-deterministic packet ordering.
        Reading the engine ``MovedEvent`` here (the orchestrator-owned boundary)
        keeps ``agents/`` engine-free.
        """

        visible_rooms = set(visibility.visible_rooms)
        moved: dict[PlayerId, MovedPlayerView] = {}
        for event in engine_events:
            if not isinstance(event, MovedEvent):
                continue
            if event.from_room == event.to_room:
                continue
            if event.from_room not in visible_rooms:
                continue
            moved[event.actor] = MovedPlayerView(
                id=event.actor,
                from_room=event.from_room,
                to_room=event.to_room,
            )
        return tuple(moved[actor_id] for actor_id in sorted(moved))

    def _own_kill_for_agent(
        self,
        *,
        agent_id: PlayerId,
        engine_events: Sequence[EngineEvent],
    ) -> OwnKillView | None:
        """The kill ``agent_id`` itself committed this tick, or ``None``.

        Privileged self channel (Task 11.3, DESIGN.md §1.3, §6.2). Unlike the
        witness-gated ``_observed_actions_for_agent`` scan, this fires precisely
        when ``event.actor == agent_id`` and WITHOUT a witness check: the engine
        excludes a killer from its own kill's witnesses (``engine/rules.py``), so
        the killer would otherwise never learn the act through any channel. By
        construction it is never another agent's kill, so it can never land in a
        crewmate or fellow-impostor packet -- it lives only on the actor's own
        ``SelfView``, never on the crew-visible ``PlayerView``.
        """

        for event in engine_events:
            if isinstance(event, KilledEvent) and event.actor == agent_id:
                return OwnKillView(victim_id=event.target, room=event.room)
        return None

    def _vent_observation_for_agent(
        self,
        *,
        event: VentEnteredEvent | VentExitedEvent,
        agent_id: PlayerId,
    ) -> _ObservedAction | None:
        witnessed_rooms: list[str] = []
        if agent_id in event.source_witnesses:
            witnessed_rooms.append(event.source_room)
        if agent_id in event.destination_witnesses:
            witnessed_rooms.append(event.destination_room)
        if not witnessed_rooms:
            return None
        return _ObservedAction(
            action="vent",
            room=witnessed_rooms[0],
            audible_room=witnessed_rooms[0],
        )

    def _global_view(self, *, world_state: WorldState) -> GlobalView:
        # Per-player re-key (DESIGN.md §3.2/§3.5): ``WorldState.tasks`` is keyed by
        # per-player INSTANCE, so the denominator counts task instances, not map
        # tasks (e.g. 9p/2i is 14 instances over the 12 map tasks). This is the
        # same set ``engine/win_conditions.py`` counts -- ``_apply_kill`` drops a
        # dead player's incomplete instances, so both read the live-instance total
        # -- which keeps the agent-visible progress equal to the engine's win
        # denominator. The rule is unchanged; only the magnitude scales.
        tasks_total = len(world_state.tasks)
        tasks_completed = sum(
            1 for task in world_state.tasks.values() if task.completed
        )
        task_completion_percent = (
            (tasks_completed / tasks_total) if tasks_total > 0 else 0.0
        )

        # Public, role-blind repair channel (DESIGN.md §8.3, Task 11.5). Surface
        # the active sabotage's repair rooms + gating flag from the MAP definition
        # so the crew (11.6) can route without ``agents/``->``engine/`` coupling.
        # Populated ONLY while a sabotage is active; identical across every role
        # (leak-clean) and empty/false otherwise.
        sabotage_active = (
            world_state.sabotage is not None and world_state.sabotage.active
        )
        sabotage_repair_rooms: tuple[RoomId, ...] = ()
        sabotage_is_gating = False
        if sabotage_active and world_state.sabotage is not None:
            definition = self._game_map.sabotages[world_state.sabotage.kind]
            sabotage_repair_rooms = definition.repair_rooms
            sabotage_is_gating = definition.gates_tasks

        return GlobalView(
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            task_completion_percent=task_completion_percent,
            sabotage_active=sabotage_active,
            sabotage_kind=world_state.sabotage.kind
            if world_state.sabotage is not None
            else None,
            sabotage_repair_rooms=sabotage_repair_rooms,
            sabotage_is_gating=sabotage_is_gating,
        )

    def _pending_task_id_for_agent(
        self, *, world_state: WorldState, agent_id: PlayerId
    ) -> TaskId | None:
        """Return the agent's own next pending MAP task id (DESIGN.md §3.2, §1.3).

        Under the per-player keyspace (Task 8.1) ``WorldState.tasks`` is keyed by
        the composite instance id ``"{owner}:{map_task_id}"`` and ``TaskState.id``
        is that composite. The agent-facing id, however, stays the MAP id: the
        engine resolves ``(actor, map_task_id)`` to the actor's own instance
        (``engine/tick.py``) and ``PublicMapView.task_locations`` is map-keyed, so
        the policy/prompt layers round-trip on the map id. We therefore surface
        ``task.map_task_id`` -- never the composite instance id, which would both
        miss the map-keyed ``task_locations`` lookup and leak the owner prefix.

        For a CREWMATE the result is owner-scoped by construction: the
        ``task.owner == agent_id`` filter means a recipient only ever sees its OWN
        pending task, never another player's task or any ownership (the §1.3
        observation firewall). Selection is deterministic -- the
        lexicographically-first owned, unfinished map task id. The owner prefix is
        constant within one agent, so ordering by map id is identical to the prior
        instance-id ordering.

        For an IMPOSTOR the result is a PRETEND map task id (Task 10.14, audit
        D-D-1): impostors own no instances, so the owner filter would surface
        ``None`` forever and the dormant ``ImpostorPolicy._idle`` do_task branch
        could never fire (the "never-tasks" fingerprint). ``impostor_pretend_task_id``
        supplies a map task id on the privileged self channel so the impostor
        blends; it never mints a ``WorldState.tasks`` instance, so the win
        denominator and the engine's owned-instance resolution never see it (see
        the module-level note for the integrity invariant).
        """

        player = world_state.players.get(agent_id)
        if player is not None and player.role == "IMPOSTOR":
            impostor_ids = [
                other_id
                for other_id, other in world_state.players.items()
                if other.role == "IMPOSTOR"
            ]
            return impostor_pretend_task_id(
                game_map=self._game_map,
                agent_id=agent_id,
                impostor_ids=impostor_ids,
                tick=world_state.tick,
            )

        owned_unfinished_map_ids = [
            task.map_task_id
            for task in world_state.tasks.values()
            if task.owner == agent_id and not task.completed
        ]
        if not owned_unfinished_map_ids:
            return None
        return sorted(owned_unfinished_map_ids)[0]

    def _owned_task_ids_for_agent(
        self, *, world_state: WorldState, agent_id: PlayerId
    ) -> tuple[TaskId, ...]:
        """Return the recipient's OWN unfinished map task ids (DESIGN.md §1.3, §3.2).

        The widened ``SelfView.owned_task_ids`` surface (Task 15.22 decision 5;
        the four-item review item (1) ObservationService scoping). Mirrors
        ``_pending_task_id_for_agent``'s role split and is derived STRICTLY from
        the recipient's OWN engine-side task state, never another player's:

        * For a CREWMATE the ``task.owner == agent_id`` filter yields exactly its
          owned, unfinished map ids (never the composite ``"{owner}:{map_task_id}"``
          instance id, which would leak the owner prefix), sorted ascending for
          replay stability.
        * For an IMPOSTOR — which owns no ``WorldState.tasks`` instance —
          ``impostor_pretend_task_set`` supplies the per-seat camouflage window
          over the SAME impostor roster ``_pending_task_id_for_agent`` uses, so
          the field carries no role bit (Task 10.14 blending, sorted like a
          crewmate's owned set).

        By construction ``pending_task_id`` is this tuple's head for a crewmate
        and a member of the camouflage window for an impostor, so the two
        self-channel fields stay mutually consistent and role-indistinguishable.
        """

        player = world_state.players.get(agent_id)
        if player is not None and player.role == "IMPOSTOR":
            impostor_ids = [
                other_id
                for other_id, other in world_state.players.items()
                if other.role == "IMPOSTOR"
            ]
            return impostor_pretend_task_set(
                game_map=self._game_map,
                agent_id=agent_id,
                impostor_ids=impostor_ids,
            )

        return tuple(
            sorted(
                task.map_task_id
                for task in world_state.tasks.values()
                if task.owner == agent_id and not task.completed
            )
        )
