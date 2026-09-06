"""Public time bounds and map feasibility derived from an agent's own records."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

from agents.memory.episodic import EpisodicEvent
from observation.public_map import PublicMapView

if TYPE_CHECKING:
    from agents.memory.store import AgentMemory

ObservationPhase = Literal["snapshot", "event", "unknown"]


class TravelAssessment(BaseModel):
    """Walking feasibility conditional on the stated placements being accurate."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    hops: int | None
    available_moves: int | None
    feasible: bool | None


def assess_travel(
    public_map: PublicMapView,
    *,
    from_room: str,
    to_room: str,
    from_tick: int,
    to_tick: int,
    from_phase: ObservationPhase = "snapshot",
    to_phase: ObservationPhase = "snapshot",
) -> TravelAssessment:
    """Use the actual public graph and one move per actor per engine tick.

    Ordinary snapshots precede actions at their tick; event observations follow
    their source action. Unknown timing never turns an ambiguous interval into
    an impossible-travel accusation. A feasible walk does not establish innocence.
    """

    if from_tick < 0 or to_tick < from_tick:
        raise ValueError("travel observations must have ordered nonnegative ticks")
    if from_room not in public_map.room_ids or to_room not in public_map.room_ids:
        return TravelAssessment(hops=None, available_moves=None, feasible=None)
    pending = deque([(from_room, 0)])
    seen = {from_room}
    hops = None
    while pending:
        room, distance = pending.popleft()
        if room == to_room:
            hops = distance
            break
        for neighbor in public_map.room_neighbors.get(room, ()):
            if neighbor not in seen:
                pending.append((neighbor, distance + 1))
                seen.add(neighbor)
    if hops is None:
        return TravelAssessment(hops=None, available_moves=None, feasible=False)
    elapsed = to_tick - from_tick
    if "unknown" in (from_phase, to_phase):
        feasible = (
            True
            if hops <= max(0, elapsed - 1)
            else (False if hops > elapsed + 1 else None)
        )
        return TravelAssessment(hops=hops, available_moves=None, feasible=feasible)
    available = elapsed + int(to_phase == "event") - int(from_phase == "event")
    if available < 0:
        raise ValueError("travel observation phases run backwards within one tick")
    return TravelAssessment(
        hops=hops, available_moves=available, feasible=hops <= available
    )


def ingest_public_meeting_roster(
    memory: AgentMemory,
    *,
    tick: int,
    living_ids: tuple[str, ...],
    dead_ids: tuple[str, ...],
) -> None:
    """Remember when a public roster became known, never when a victim was killed."""

    if memory.evidence_reasoning_version is None:
        return
    if tick < 0 or set(living_ids) & set(dead_ids):
        raise ValueError("public roster requires a valid tick and disjoint groups")
    if len(set(living_ids)) != len(living_ids) or len(set(dead_ids)) != len(dead_ids):
        raise ValueError("public roster contains duplicate players")
    payload = {
        "living_ids": tuple(sorted(living_ids)),
        "dead_ids": tuple(sorted(dead_ids)),
    }
    existing = [
        event
        for event in memory.episodic.recent(since_tick=tick)
        if event.type == "public_meeting_roster" and event.tick == tick
    ]
    if existing:
        if existing[-1].payload != payload:
            raise ValueError("conflicting public rosters at one meeting tick")
        return
    memory.episodic.append(
        EpisodicEvent(
            tick=tick,
            type="public_meeting_roster",
            payload=payload,
            provenance="public",
        )
    )


def publicly_dead_ids(memory: AgentMemory) -> frozenset[str]:
    """Read announced deaths; the permanent known-player roster stays untouched."""

    return frozenset(
        str(player)
        for event in memory.episodic.recent(since_tick=0)
        if event.type == "public_meeting_roster"
        for player in event.payload["dead_ids"]
    )


def evidence_context_lines(
    memory: AgentMemory, *, own_agent_id: str | None, teammate_ids: frozenset[str]
) -> tuple[str, ...]:
    """Render bounded death/discovery facts and conditional walking counterevidence."""

    if memory.evidence_reasoning_version is None:
        return ()
    last_alive: dict[str, int] = {}
    dead_by: dict[str, int] = {}
    discovered: dict[str, int] = {}
    paths: dict[str, list[tuple[int, str, ObservationPhase]]] = {}
    own_victims = {
        event.payload.get("victim_id")
        for event in memory.episodic.recent(since_tick=0)
        if event.type == "own_kill" and event.provenance == "observed"
    }
    for event in memory.episodic.recent(since_tick=0):
        if event.type == "public_meeting_roster":
            for player in event.payload["dead_ids"]:
                dead_by.setdefault(str(player), event.tick)
        if event.provenance != "observed":
            continue
        if event.type == "saw_body":
            victim = event.payload.get("victim_id")
            if isinstance(victim, str) and victim not in own_victims:
                discovered.setdefault(victim, event.tick)
                dead_by.setdefault(victim, event.tick)
        if event.type == "saw_player":
            subject, room = event.payload.get("player_id"), event.payload.get("room")
            if not isinstance(subject, str) or not isinstance(room, str):
                continue
            phase: ObservationPhase
            if event.payload.get("source_event_id"):
                phase = "event"
            elif event.payload.get("action") in ("vent", "kill"):
                # Legacy packets date these source-room events when delivered.
                # They do not establish an ordinary snapshot at that tick.
                phase = "unknown"
            else:
                phase = "snapshot"
            if phase != "unknown":
                last_alive[subject] = event.tick
            if subject == own_agent_id or subject in teammate_ids:
                continue
            paths.setdefault(subject, []).append((event.tick, room, phase))
    lines = []
    for victim, upper in sorted(dead_by.items()):
        facts = [f"known dead by tick {upper}"]
        if victim in last_alive:
            facts.insert(0, f"you last saw them alive at tick {last_alive[victim]}")
        if victim in discovered:
            facts.append(f"you discovered their body at tick {discovered[victim]}")
        lines.append(
            f"Death evidence for {victim}: {'; '.join(facts)}. Discovery does not date the death."
        )
    if memory.public_map is not None:
        for subject, rows in sorted(paths.items()):
            if subject in dead_by or len(rows) < 2:
                continue
            later = rows[-1]
            earlier = next(
                (row for row in reversed(rows[:-1]) if row[1] != later[1]), None
            )
            if earlier is None:
                continue
            assessment = assess_travel(
                memory.public_map,
                from_room=earlier[1],
                to_room=later[1],
                from_tick=earlier[0],
                to_tick=later[0],
                from_phase=earlier[2],
                to_phase=later[2],
            )
            if assessment.feasible is True:
                lines.append(
                    f"Travel check for {subject}: {earlier[1]} at tick {earlier[0]} to {later[1]} at tick {later[0]} fits the public walking map. This contests an impossible-travel claim; it does not establish innocence."
                )
            elif assessment.feasible is False:
                lines.append(
                    f"Travel check for {subject}: {earlier[1]} at tick {earlier[0]} to {later[1]} at tick {later[0]} cannot be reconciled by walking in that interval. Check the placement sources; this alone does not prove a role."
                )
    return tuple(lines)
