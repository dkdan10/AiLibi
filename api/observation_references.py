"""Bounded citation projections from one observer's actual episodic snapshot."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from agents.memory.episodic import EpisodicEvent
from api.schemas import ObservationReferenceView


def _string(payload: Mapping[str, Any], field: str) -> str | None:
    value = payload.get(field)
    return value if isinstance(value, str) else None


def observation_references(
    *,
    observer_id: str,
    cited_ids: Sequence[str],
    events: Sequence[EpisodicEvent],
    scene_ticks: Mapping[str, int],
) -> tuple[ObservationReferenceView, ...]:
    """Resolve requested IDs by equality, with no nearby-ID or prose fallback.

    ``events`` belongs to this observer at this meeting boundary. ``scene_ticks``
    maps deliveries to actual replay frames; an absent mapping leaves scene time
    unknown. It is never inferred from opaque IDs or from observation time.
    """
    by_id = {
        event.observation_id: event
        for event in events
        if event.observation_id is not None
    }
    references: list[ObservationReferenceView] = []
    for observation_id in sorted(set(cited_ids)):
        event = by_id.get(observation_id)
        subject = room = from_room = to_room = text = kind = None
        if event is not None:
            payload = event.payload
            subject = _string(payload, "player_id")
            room = _string(payload, "room")
            from_room = _string(payload, "from_room")
            to_room = _string(payload, "to_room")
            kind = event.type
            if kind == "saw_player" and subject is not None and room is not None:
                action = _string(payload, "action")
                if action in {"vent", "kill"}:
                    kind = f"saw_{action}"
                    text = f"{observer_id} witnessed {subject} {action} in {room}."
                else:
                    companions = sorted(
                        {
                            player
                            for other in events
                            if other.type == "saw_player"
                            and other.tick == event.tick
                            and other.payload.get("room") == room
                            and (player := _string(other.payload, "player_id"))
                            is not None
                            and player != subject
                        }
                    )
                    with_others = f" with {', '.join(companions)}" if companions else ""
                    text = f"{observer_id} saw {subject} in {room}{with_others}."
            elif (
                kind == "saw_player_move"
                and subject is not None
                and from_room is not None
                and to_room is not None
            ):
                text = (
                    f"{observer_id} saw {subject} move from {from_room} to {to_room}."
                )
            elif kind == "saw_body" and room is not None:
                subject = _string(payload, "victim_id")
                if subject is not None:
                    text = f"{observer_id} discovered {subject}'s body in {room}."
            elif kind == "self_state" and room is not None:
                subject = observer_id
                text = f"{observer_id} was in {room}."
            elif kind == "heard_vent_use":
                text = f"{observer_id} heard a vent sound" + (
                    f" in {room}." if room else "."
                )
            elif kind == "heard_sabotage_alarm":
                text = f"{observer_id} heard a sabotage alarm."
        references.append(
            ObservationReferenceView(
                observation_id=observation_id,
                observer_id=observer_id,
                resolved=event is not None,
                observation_tick=event.tick if event is not None else None,
                scene_tick=scene_ticks.get(observation_id)
                if event is not None
                else None,
                provenance=event.provenance if event is not None else None,
                kind=kind,
                text=text,
                subject_id=subject,
                room=room,
                from_room=from_room,
                to_room=to_room,
            )
        )
    return tuple(references)
