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


def ingest_public_regroup(
    memory: AgentMemory,
    *,
    tick: int,
    room: str,
    player_ids: tuple[str, ...],
) -> None:
    """Record an announced relocation, not an inferred walk or hidden route."""
    if memory.evidence_reasoning_version != 2:
        return
    if tick < 0 or not room or len(set(player_ids)) != len(player_ids):
        raise ValueError(
            "public regroup requires a valid tick, room and distinct players"
        )
    if memory.public_map is not None and room not in memory.public_map.room_ids:
        raise ValueError("public regroup names an unknown room")
    payload = {"room": room, "player_ids": tuple(sorted(player_ids))}
    existing = [
        row
        for row in memory.episodic.recent(since_tick=tick)
        if row.tick == tick and row.type == "public_regroup"
    ]
    if existing:
        if existing[-1].payload != payload:
            raise ValueError("conflicting public regroups at one tick")
        return
    memory.episodic.append(
        EpisodicEvent(
            tick=tick, type="public_regroup", payload=payload, provenance="public"
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
    if memory.evidence_reasoning_version == 2:
        return _v2_evidence_context_lines(
            memory, own_agent_id=own_agent_id, teammate_ids=teammate_ids
        )
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


def _v2_evidence_context_lines(
    memory: AgentMemory,
    *,
    own_agent_id: str | None,
    teammate_ids: frozenset[str],
) -> tuple[str, ...]:
    """Keep earlier intervals and explicitly condition checks on public claims.

    A claim has no within-tick phase. The conservative unknown-phase assessment
    cannot turn that missing precision into an impossible-travel verdict.
    """
    rows = memory.episodic.recent(since_tick=0)
    own_victims = {
        row.payload.get("victim_id")
        for row in rows
        if row.type == "own_kill" and row.provenance == "observed"
    }
    dead_by: dict[str, int] = {}
    discovered: dict[str, int] = {}
    alive: dict[str, tuple[int, str]] = {}
    placements: dict[str, list[tuple[int, str, ObservationPhase, str]]] = {}
    claims: list[tuple[str, int, str, str]] = []
    regroups: list[tuple[int, str, frozenset[str]]] = []
    for row in rows:
        if row.type == "public_regroup" and row.provenance == "public":
            regroup_room = str(row.payload["room"])
            regrouped = frozenset(str(pid) for pid in row.payload["player_ids"])
            regroups.append((row.tick, regroup_room, regrouped))
            for regroup_subject in sorted(regrouped):
                if (
                    regroup_subject != own_agent_id
                    and regroup_subject not in teammate_ids
                ):
                    placements.setdefault(regroup_subject, []).append(
                        (row.tick, regroup_room, "snapshot", "the public regroup")
                    )
        if row.type == "public_meeting_roster":
            for victim in row.payload["dead_ids"]:
                dead_by.setdefault(str(victim), row.tick)
        if row.type == "reported_testimony" and row.provenance == "reported":
            subject, room = row.payload.get("subject"), row.payload.get("room")
            tick, kind = row.payload.get("from_tick"), row.payload.get("kind")
            if (
                kind in ("whereabouts", "alibi", "saw_player")
                and isinstance(subject, str)
                and isinstance(room, str)
                and isinstance(tick, int)
            ):
                claims.append(
                    (subject, tick, room, f"claim by {row.payload.get('speaker')}")
                )
        if row.provenance != "observed":
            continue
        if row.type == "saw_body":
            victim = row.payload.get("victim_id")
            if isinstance(victim, str) and victim not in own_victims:
                dead_by.setdefault(victim, row.tick)
                discovered.setdefault(victim, row.tick)
        if row.type not in ("saw_player", "saw_player_move"):
            continue
        subject = row.payload.get("player_id")
        room = (
            row.payload.get("to_room")
            if row.type == "saw_player_move"
            else row.payload.get("room")
        )
        if not isinstance(subject, str) or not isinstance(room, str):
            continue
        phase: ObservationPhase = "unknown"
        if row.payload.get("observation_phase") == "snapshot":
            phase = "snapshot"
        elif row.payload.get("observation_phase") == "event":
            phase = "event"
        timing = (
            f"start of tick {row.tick}"
            if phase == "snapshot"
            else f"during tick {row.tick}"
            if phase == "event"
            else f"tick {row.tick}, timing unspecified"
        )
        alive[subject] = row.tick, timing
        if subject != own_agent_id and subject not in teammate_ids:
            source = (
                f"your observation {row.observation_id}"
                if row.observation_id
                else "your recorded sighting"
            )
            placements.setdefault(subject, []).append((row.tick, room, phase, source))
    lines: list[str] = []
    for victim, upper in sorted(dead_by.items()):
        facts = [f"known dead by tick {upper}"]
        if victim in alive:
            facts.insert(0, f"you last saw them alive at {alive[victim][1]}")
        if victim in discovered:
            facts.append(
                f"you discovered their body at the start of tick {discovered[victim]}"
            )
        lines.append(
            f"Death evidence for {victim}: {'; '.join(facts)}. Discovery does not date the death."
        )
    if memory.public_map is None:
        return tuple(lines)
    checks: list[
        tuple[
            str,
            tuple[int, str, ObservationPhase, str],
            tuple[int, str, ObservationPhase, str],
            bool,
        ]
    ] = []
    for subject, observed in sorted(placements.items()):
        # Each change interval survives a later harmless sighting. We do not
        # replace the historical interval with the latest pair of rooms.
        for earlier, later in zip(observed, observed[1:], strict=False):
            if earlier[1] != later[1]:
                checks.append((subject, earlier, later, False))
    for subject, tick, room, source in claims:
        if subject == own_agent_id or subject in teammate_ids:
            continue
        claimed: tuple[int, str, ObservationPhase, str] = (
            tick,
            room,
            "unknown",
            source,
        )
        observed = placements.get(subject, [])
        before = [row for row in observed if row[0] <= tick]
        after = [row for row in observed if row[0] >= tick]
        if before:
            checks.append((subject, before[-1], claimed, True))
        if after and (not before or after[0] != before[-1]):
            checks.append((subject, claimed, after[0], True))
        lines.append(
            f"Account uncertainty for {subject}: route feasibility alone cannot establish the {source}'s claimed presence in {room} at tick {tick}."
        )
        if not before and not after:
            lines.append(
                f"Travel check for {subject}: insufficient observed placements to check the {source} at tick {tick}."
            )
    seen: set[str] = set()
    for subject, earlier, later, includes_claim in checks:
        crossed = [
            regroup
            for regroup in regroups
            if subject in regroup[2] and earlier[0] < regroup[0] <= later[0]
        ]
        if crossed:
            when, destination, _ = crossed[-1]
            line = f"Travel check for {subject}: the interval from tick {earlier[0]} to tick {later[0]} crosses the public regroup at tick {when} in {destination}. A walking-only check cannot decide this interval."
            if line not in seen:
                lines.append(line)
                seen.add(line)
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
        timing_a = (
            "start"
            if earlier[2] == "snapshot"
            else "during"
            if earlier[2] == "event"
            else "unspecified phase"
        )
        timing_b = (
            "start"
            if later[2] == "snapshot"
            else "during"
            if later[2] == "event"
            else "unspecified phase"
        )
        subject_clause = (
            "Assuming the claimed placement is accurate, " if includes_claim else ""
        )
        prefix = f"Travel check for {subject}: {earlier[1]} at tick {earlier[0]} ({timing_a}; {earlier[3]}) to {later[1]} at tick {later[0]} ({timing_b}; {later[3]}). {subject_clause}"
        if assessment.feasible is True:
            result = "a walk fits the public map; this contests an impossible-travel allegation and does not establish innocence."
        elif assessment.feasible is False:
            result = "walking cannot reconcile these placements. Check their sources; this alone does not prove a role."
        else:
            result = "the available timing or placements are insufficient for a walking verdict."
        line = prefix + result
        if line not in seen:
            lines.append(line)
            seen.add(line)
    return tuple(lines)
