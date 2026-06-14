from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from engine.entities import PlayerId
from engine.events import EngineEvent, KilledEvent, VentEnteredEvent, VentExitedEvent
from engine.visibility import VisibilityResult, compute_visibility_for_player
from engine.world import Map, TaskId, WorldState
from observation.audit import ObservationAuditLog
from observation.packet import (
    AudibleEvent,
    BodyView,
    GlobalView,
    ObservationPacket,
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
# The rotation is reconciled with the memory renderer (Codex review, PR #155).
# ``agents/memory/store.py`` infers a "You completed {task}" observation on ANY
# change of ``pending_task_id`` away from a non-None value — correct for a
# crewmate (its owned set only shrinks, so a change IS a completion) but a lie for
# the impostor, whose pretend tasks never complete. Rather than freeze the blend
# (which costs the roam AND balance), the renderer's completion inference is
# role-GATED to crewmates, so a rotating impostor pretend id mints NO fictitious
# completed-task memory and cannot become a fabricated ``completed_task`` alibi —
# the impostor's memory stays accurate; the alibi fabrication is the LLM's job at
# the meeting (DESIGN.md §4.7). Seats are taken over ALL role==IMPOSTOR players
# (alive or dead — ejection marks ``alive=False`` but never removes the player),
# so a seat never shifts mid-game when a teammate is ejected.
IMPOSTOR_PRETEND_TASK_SET_SIZE: Final[int] = 3
# How many ticks the impostor dwells on one pretend task before the deterministic
# rotation advances to the next in its per-seat set. Anchored above the map
# diameter and the kill cooldown so the impostor reaches and "performs" a task
# within a window (no per-tick re-route oscillation), then roams to the next.
# Re-derived at 10.17 against the toolkit-shifted kill cadence.
IMPOSTOR_PRETEND_TASK_DWELL_TICKS: Final[int] = 6


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
    map tasks and rotates through it purely by ``tick // dwell``. No RNG, no
    module state — the same ``(game_map, agent_id, impostor_ids, tick)`` always
    yields the same id, keeping replay reconstruction byte-identical. The
    rotation is safe for the renderer because its completion inference is
    role-gated to crewmates (see the module note). Returns ``None`` only for a
    task-less map.

    Fail-loud (AGENTS.md no silent fallbacks): ``agent_id`` MUST be a member of
    ``impostor_ids``. A non-member is a caller wiring error (a filtered or stale
    roster) — it raises rather than silently reusing seat 0's window and masking
    the bug (Codex review, PR #155).
    """

    map_task_ids = sorted(game_map.tasks)
    n = len(map_task_ids)
    if n == 0:
        return None
    sorted_impostors = sorted(impostor_ids)
    if agent_id not in sorted_impostors:
        raise ValueError(
            f"impostor_pretend_task_id called for {agent_id!r}, which is not in "
            f"impostor_ids {tuple(sorted_impostors)!r} (caller wiring error)"
        )
    seat = sorted_impostors.index(agent_id)
    offset = (seat * IMPOSTOR_PRETEND_TASK_SET_SIZE) % n
    pretend_set: list[TaskId] = []
    for i in range(min(IMPOSTOR_PRETEND_TASK_SET_SIZE, n)):
        candidate = map_task_ids[(offset + i) % n]
        if candidate not in pretend_set:
            pretend_set.append(candidate)
    index = (tick // IMPOSTOR_PRETEND_TASK_DWELL_TICKS) % len(pretend_set)
    return pretend_set[index]


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
        observed_actions = self._observed_actions_for_agent(
            agent_id=agent_id,
            engine_events=engine_events,
        )
        visible_players = self._visible_players(
            world_state=world_state,
            visibility=visibility,
            observed_actions=observed_actions,
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
                fellow_impostor_ids=fellow_impostor_ids,
            ),
            visible_players=visible_players,
            visible_bodies=visible_bodies,
            audible_events=self._audible_events(
                world_state=world_state,
                observed_actions=observed_actions,
            ),
            global_state=self._global_view(world_state=world_state),
            cooldown=cooldown,
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
        engine_events: Sequence[EngineEvent],
    ) -> dict[PlayerId, _ObservedAction]:
        observed_actions: dict[PlayerId, _ObservedAction] = {}
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
        return observed_actions

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

        return GlobalView(
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            task_completion_percent=task_completion_percent,
            sabotage_active=(
                world_state.sabotage is not None and world_state.sabotage.active
            ),
            sabotage_kind=world_state.sabotage.kind
            if world_state.sabotage is not None
            else None,
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
