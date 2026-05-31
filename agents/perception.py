"""Perception ingestion (DESIGN.md §4.2, §6.2).

Convert an :class:`ObservationPacket` into typed :class:`EpisodicEvent` rows
and append them to the agent's :class:`MemoryStore`. Tactical policies read
from memory only and never parse raw packets — keeping all raw-packet
parsing in this module is what makes that possible.

Provenance values:

* ``"observed"`` — first-hand sensory data: own room/role/task, sightings of
  other players, body discoveries, audible cues, and the impostor kill
  cooldown reading.
* ``"inferred"`` — the global aggregate the agent receives but does not
  directly perceive (system-wide task progress, sabotage status). The
  number is derived from world state the agent could not see itself.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from agents.memory.beliefs import (
    BODY_PROXIMITY_WINDOW_TICKS,
    BeliefState,
    apply_observation_rules,
)
from agents.memory.episodic import EpisodicEvent, MemoryStore
from observation.packet import (
    AudibleEvent,
    BodyId,
    BodyView,
    GlobalView,
    ObservationPacket,
    PlayerId,
    PlayerView,
    RoomId,
    SelfView,
)

PROVENANCE_OBSERVED: Final[str] = "observed"
PROVENANCE_INFERRED: Final[str] = "inferred"

EVENT_SELF_STATE: Final[str] = "self_state"
EVENT_COOLDOWN_STATUS: Final[str] = "cooldown_status"
EVENT_SAW_PLAYER: Final[str] = "saw_player"
EVENT_SAW_BODY: Final[str] = "saw_body"
EVENT_HEARD_VENT_USE: Final[str] = "heard_vent_use"
EVENT_HEARD_SABOTAGE_ALARM: Final[str] = "heard_sabotage_alarm"
EVENT_GLOBAL_STATUS: Final[str] = "global_status"

_AUDIBLE_EVENT_TYPES: Final[Mapping[str, str]] = {
    "vent_use_heard": EVENT_HEARD_VENT_USE,
    "sabotage_alarm": EVENT_HEARD_SABOTAGE_ALARM,
}


def ingest_packet(
    *,
    packet: ObservationPacket,
    memory: MemoryStore,
    beliefs: BeliefState | None = None,
) -> None:
    """Append typed :class:`EpisodicEvent` rows for one observation tick.

    Order of appended events at ``packet.tick``:

    1. ``self_state`` (own room, role, pending task)
    2. ``cooldown_status`` (impostor only — skipped when ``cooldown`` is None)
    3. ``saw_player`` for each entry in ``visible_players`` (packet order)
    4. ``saw_body`` for each entry in ``visible_bodies`` (packet order)
    5. one ``heard_*`` per ``audible_events`` entry (packet order)
    6. ``global_status`` (inferred system-wide aggregate)

    When ``beliefs`` is supplied, the agent's DESIGN.md §6.3 rule-based belief
    updates (Rules 1 and 4) run after the episodic append: the proximity and
    co-presence inputs are derived from the just-updated episodic store and
    fed to :func:`agents.memory.beliefs.apply_observation_rules`, whose result
    is adopted in place so the caller's ``BeliefState`` reflects the update.
    Callers that only need episodic ingestion (e.g. the runtime stub) omit it.
    """

    tick = packet.tick

    memory.append(
        EpisodicEvent(
            tick=tick,
            type=EVENT_SELF_STATE,
            payload=_self_state_payload(packet.self_state),
            provenance=PROVENANCE_OBSERVED,
        )
    )

    if packet.cooldown is not None:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_COOLDOWN_STATUS,
                payload={"cooldown": packet.cooldown},
                provenance=PROVENANCE_OBSERVED,
            )
        )

    for player in packet.visible_players:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_SAW_PLAYER,
                payload=_visible_player_payload(player),
                provenance=PROVENANCE_OBSERVED,
            )
        )

    for body in packet.visible_bodies:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_SAW_BODY,
                payload=_visible_body_payload(body),
                provenance=PROVENANCE_OBSERVED,
            )
        )

    for audible in packet.audible_events:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=_audible_event_type(audible),
                payload=_audible_event_payload(audible),
                provenance=PROVENANCE_OBSERVED,
            )
        )

    memory.append(
        EpisodicEvent(
            tick=tick,
            type=EVENT_GLOBAL_STATUS,
            payload=_global_state_payload(packet.global_state),
            provenance=PROVENANCE_INFERRED,
        )
    )

    if beliefs is not None:
        beliefs.load_from(
            apply_observation_rules(
                beliefs,
                observation=packet,
                previous_visible_bodies=_previously_seen_body_ids(
                    memory, before_tick=tick
                ),
                recent_co_presence=_recent_co_presence(memory, current_tick=tick),
            )
        )


def _previously_seen_body_ids(memory: MemoryStore, *, before_tick: int) -> set[BodyId]:
    """Body ids the agent recorded seeing strictly before ``before_tick``.

    Rule 1 fires only on a body's first sighting; a body already present in
    this set was seen on an earlier tick and must not re-elevate suspicion.
    The current tick's ``saw_body`` rows are excluded by the strict ``<``
    comparison, so call order relative to the episodic append does not matter.
    """

    return {
        event.payload["body_id"]
        for event in memory.recent(since_tick=0)
        if event.type == EVENT_SAW_BODY and event.tick < before_tick
    }


def _recent_co_presence(
    memory: MemoryStore, *, current_tick: int
) -> dict[RoomId, list[tuple[int, PlayerId]]]:
    """Map each room to the ``(tick, player_id)`` sightings in the proximity
    window ``[current_tick - BODY_PROXIMITY_WINDOW_TICKS, current_tick - 1]``.

    Built only from the agent's own first-hand ``saw_player`` rows, so it
    carries no information the agent did not directly observe -- the firewall
    is preserved. The current tick is excluded (the window is "shortly before"
    a discovery), so this is safe to call after the tick's rows are appended.
    """

    earliest_tick = current_tick - BODY_PROXIMITY_WINDOW_TICKS
    co_presence: dict[RoomId, list[tuple[int, PlayerId]]] = {}
    for event in memory.recent(since_tick=earliest_tick):
        if event.type != EVENT_SAW_PLAYER or event.tick >= current_tick:
            continue
        room = event.payload["room"]
        player_id = event.payload["player_id"]
        co_presence.setdefault(room, []).append((event.tick, player_id))
    return co_presence


def _self_state_payload(self_state: SelfView) -> Mapping[str, Any]:
    # ``fellow_impostor_ids`` rides the same privileged self-state payload that
    # already carries ``role`` (Task 7.2): the impostor policy/prompt layer
    # reads its teammates from here in Wave 2 (J-5). It is ``()`` for crewmates
    # and serializes to a list in the prompt JSON, like other tuple fields.
    return {
        "room": self_state.room,
        "role": self_state.role,
        "pending_task_id": self_state.pending_task_id,
        "fellow_impostor_ids": self_state.fellow_impostor_ids,
    }


def _visible_player_payload(player: PlayerView) -> Mapping[str, Any]:
    return {
        "player_id": player.id,
        "room": player.room,
        "action": player.action,
    }


def _visible_body_payload(body: BodyView) -> Mapping[str, Any]:
    # ``body_id`` is the canonical body identifier for deduplication and
    # replay references; ``victim_id`` is the authoritative source for
    # downstream agent code that needs the body's victim player id
    # (DESIGN.md §1.3, Task 3.2 R-4 retirement).
    return {
        "body_id": body.id,
        "room": body.room,
        "victim_id": body.victim_id,
    }


def _audible_event_type(event: AudibleEvent) -> str:
    event_type = _AUDIBLE_EVENT_TYPES.get(event.kind)
    if event_type is None:
        raise ValueError(f"unknown audible event kind: {event.kind!r}")
    return event_type


def _audible_event_payload(event: AudibleEvent) -> Mapping[str, Any]:
    return {
        "kind": event.kind,
        "room": event.room,
    }


def _global_state_payload(global_state: GlobalView) -> Mapping[str, Any]:
    return {
        "tasks_completed": global_state.tasks_completed,
        "tasks_total": global_state.tasks_total,
        "task_completion_percent": global_state.task_completion_percent,
        "sabotage_active": global_state.sabotage_active,
        "sabotage_kind": global_state.sabotage_kind,
    }


__all__ = [
    "EVENT_COOLDOWN_STATUS",
    "EVENT_GLOBAL_STATUS",
    "EVENT_HEARD_SABOTAGE_ALARM",
    "EVENT_HEARD_VENT_USE",
    "EVENT_SAW_BODY",
    "EVENT_SAW_PLAYER",
    "EVENT_SELF_STATE",
    "PROVENANCE_INFERRED",
    "PROVENANCE_OBSERVED",
    "ingest_packet",
]
