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

Observation ids (Task 16.5, C8; audits/post-phase-14-Voice-and-Judgment-
planning.md §3.4 C3/C8). Every ``"observed"`` row this module writes is stamped
with a stable ``{agent_id}:{tick}:{seq}`` :data:`~agents.memory.episodic.ObservationId`
via :func:`~agents.memory.episodic.derive_observation_id` — the citation handle the
§6.6 render surfaces (lever-ON) and the vote ballot cites (16.6 enforces). The
``"inferred"`` ``global_status`` aggregate carries no id (a derived aggregate is
not first-hand citable evidence), and reported testimony
(:func:`agents.memory.store.absorb_reported_testimony`) carries none by design.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Final

from agents.memory.beliefs import (
    BODY_PROXIMITY_WINDOW_TICKS,
    BeliefState,
    apply_observation_rules,
    apply_witnessed_action_rules,
)
from agents.memory.episodic import EpisodicEvent, MemoryStore, derive_observation_id
from observation.packet import (
    AudibleEvent,
    BodyId,
    BodyView,
    EventObservationBatch,
    GlobalView,
    MovedPlayerView,
    ObservationPacket,
    OwnKillView,
    PlayerId,
    PlayerView,
    RoomId,
    SelfView,
)

PROVENANCE_OBSERVED: Final[str] = "observed"
PROVENANCE_INFERRED: Final[str] = "inferred"
# Public testimony heard at a meeting (Task 13.5.2; 2026-06-25 memory diagnosis,
# workflow `wg54kfoxy`: "social info is a scalar, not content"). A meeting
# speaker's STRUCTURED claim/observation about another player, ingested as
# episodic content by :func:`agents.memory.store.absorb_reported_testimony` and
# rendered self-framed as an UNVERIFIED claim (strictly below first-hand
# salience). Not first-hand: the recipient did not perceive it, it was stated.
PROVENANCE_REPORTED: Final[str] = "reported"

EVENT_SELF_STATE: Final[str] = "self_state"
EVENT_OWN_KILL: Final[str] = "own_kill"
EVENT_COOLDOWN_STATUS: Final[str] = "cooldown_status"
EVENT_SAW_PLAYER: Final[str] = "saw_player"
# A room→room transition the agent DIRECTLY witnessed this tick (Task 13.5.4;
# 2026-06-25 memory diagnosis, workflow `wg54kfoxy`: "movement is never
# perceived"). First-hand observation, distinct from the within-vision
# transition/breadcrumb the renderer RECONSTRUCTS from consecutive ``saw_player``
# deltas: this is the single-tick transit the witness actually saw, derived from
# the engine ``MovedEvent`` and witness-gated identically to ``saw_player`` in
# ``observation/service.py``. Ingested from ``packet.moved_players``; rendered as
# a first-hand sighting-class line and wires ``WorkingMemory.last_seen``.
EVENT_SAW_PLAYER_MOVE: Final[str] = "saw_player_move"
EVENT_SAW_BODY: Final[str] = "saw_body"
EVENT_HEARD_SABOTAGE_ALARM: Final[str] = "heard_sabotage_alarm"
EVENT_GLOBAL_STATUS: Final[str] = "global_status"
# Episodic type for a reported-testimony row (Task 13.5.2). Written only by
# :func:`agents.memory.store.absorb_reported_testimony`, never by
# :func:`ingest_packet` (testimony is meeting content, not packet perception).
EVENT_REPORTED_TESTIMONY: Final[str] = "reported_testimony"

_AUDIBLE_EVENT_TYPES: Final[Mapping[str, str]] = {
    "sabotage_alarm": EVENT_HEARD_SABOTAGE_ALARM,
}


def ingest_event_observations(
    *,
    batch: EventObservationBatch,
    memory: MemoryStore,
    beliefs: BeliefState | None = None,
) -> tuple[EpisodicEvent, ...]:
    """Append only new source-time evidence, preserving exact-once belief lifts."""

    candidates: list[tuple[str, str, Mapping[str, Any]]] = []
    if batch.own_kill is not None:
        candidates.append(
            (
                EVENT_OWN_KILL,
                batch.own_kill.victim_id,
                _own_kill_payload(batch.own_kill),
            )
        )
    for player in batch.witnessed_actions:
        if player.action not in ("kill", "vent"):
            raise ValueError("event batches only contain witnessed kill/vent actions")
        candidates.append(
            (EVENT_SAW_PLAYER, player.id, _visible_player_payload(player))
        )
    for moved in batch.moved_players:
        candidates.append(
            (EVENT_SAW_PLAYER_MOVE, moved.id, _moved_player_payload(moved))
        )
    existing = memory.recent(since_tick=batch.tick)
    source_rows = {
        event.payload["source_event_id"]: event
        for event in existing
        if "source_event_id" in event.payload
    }
    seq = sum(
        event.tick == batch.tick and event.observation_id is not None
        for event in existing
    )
    appended: list[EpisodicEvent] = []
    new_action_ids: set[str] = set()
    for kind, subject, payload in candidates:
        # Every component is already entitled; no hidden global event ordinal
        # or engine identifier crosses this boundary.
        source_id = f"{batch.agent_id}:{batch.tick}:{kind}:{subject}"
        data = {**payload, "source_event_id": source_id}
        prior = source_rows.get(source_id)
        if prior is not None:
            if prior.type != kind or dict(prior.payload) != data:
                raise ValueError("conflicting content for a delivered source event")
            continue
        event = EpisodicEvent(
            tick=batch.tick,
            type=kind,
            payload=data,
            provenance=PROVENANCE_OBSERVED,
            observation_id=derive_observation_id(
                agent_id=batch.agent_id, tick=batch.tick, seq=seq
            ),
        )
        memory.append(event)
        source_rows[source_id] = event
        appended.append(event)
        seq += 1
        if kind == EVENT_SAW_PLAYER:
            new_action_ids.add(subject)
    if beliefs is not None and new_action_ids:
        beliefs.load_from(
            apply_witnessed_action_rules(
                beliefs,
                witnessed_actions=tuple(
                    action
                    for action in batch.witnessed_actions
                    if action.id in new_action_ids
                ),
                fellow_impostor_ids=batch.fellow_impostor_ids,
            )
        )
    return tuple(appended)


def ingest_packet(
    *,
    packet: ObservationPacket,
    memory: MemoryStore,
    beliefs: BeliefState | None = None,
) -> None:
    """Append typed :class:`EpisodicEvent` rows for one observation tick.

    Order of appended events at ``packet.tick``:

    1. ``self_state`` (own room, role, pending task)
    2. ``own_kill`` (the recipient's OWN kill this tick — skipped when None)
    3. ``cooldown_status`` (impostor only — skipped when ``cooldown`` is None)
    4. ``saw_player`` for each entry in ``visible_players`` (packet order)
    5. ``saw_player_move`` for each entry in ``moved_players`` (packet order)
    6. ``saw_body`` for each entry in ``visible_bodies`` (packet order)
    7. one ``heard_*`` per ``audible_events`` entry (packet order)
    8. ``global_status`` (inferred system-wide aggregate)

    ``moved_players`` is empty when the observer witnessed no transition
    (derived unconditionally in ``observation/service.py`` since Task 14.9) --
    no extra branch is needed here; ingestion simply reacts to the presence of
    the witness-gated signal.

    Each OBSERVED row (steps 1-7) is stamped with a stable
    ``{agent_id}:{tick}:{seq}`` observation id (Task 16.5, C8) via
    :func:`~agents.memory.episodic.derive_observation_id`; ``seq`` is a per-tick
    counter that runs in exactly the documented append order. Step 8's inferred
    ``global_status`` aggregate is left un-stamped -- it is not first-hand citable
    evidence.

    When ``beliefs`` is supplied, the agent's DESIGN.md §6.3 rule-based belief
    updates (Rules 1 and 4) run after the episodic append: the proximity and
    co-presence inputs are derived from the just-updated episodic store and
    fed to :func:`agents.memory.beliefs.apply_observation_rules`, whose result
    is adopted in place so the caller's ``BeliefState`` reflects the update.
    Callers that only need episodic ingestion (e.g. the runtime stub) omit it.
    """

    tick = packet.tick

    # Task 16.5 (C8): stamp a stable ``{agent_id}:{tick}:{seq}`` observation id on
    # each first-hand OBSERVED row below. ``seq`` CONTINUES from the store's
    # existing id-stamped count at this tick rather than resetting to 0: production
    # delivers exactly one packet per (agent, tick), but the store TOLERATES
    # repeated same-tick ingestion (``test_repeated_ingest_across_ticks_is_monotonic``
    # ingests tick 2 twice) and the append-time duplicate-id guard
    # (:meth:`MemoryStore.append`) must never fire on a legitimate call sequence.
    # Continuation keeps ids unique AND stays a pure function of the append history,
    # so a replay reconstruction -- the same call sequence -- regenerates identical
    # ids byte-for-byte.
    seq = sum(
        1
        for event in memory.recent(since_tick=tick)
        if event.tick == tick and event.observation_id is not None
    )

    memory.append(
        EpisodicEvent(
            tick=tick,
            type=EVENT_SELF_STATE,
            payload=_self_state_payload(packet.self_state, agent_id=packet.agent_id),
            provenance=PROVENANCE_OBSERVED,
            observation_id=derive_observation_id(
                agent_id=packet.agent_id, tick=tick, seq=seq
            ),
        )
    )
    seq += 1

    own_kill = packet.self_state.own_kill
    if own_kill is not None:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_OWN_KILL,
                payload=_own_kill_payload(own_kill),
                provenance=PROVENANCE_OBSERVED,
                observation_id=derive_observation_id(
                    agent_id=packet.agent_id, tick=tick, seq=seq
                ),
            )
        )
        seq += 1

    if packet.cooldown is not None:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_COOLDOWN_STATUS,
                payload={"cooldown": packet.cooldown},
                provenance=PROVENANCE_OBSERVED,
                observation_id=derive_observation_id(
                    agent_id=packet.agent_id, tick=tick, seq=seq
                ),
            )
        )
        seq += 1

    for player in packet.visible_players:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_SAW_PLAYER,
                payload=_visible_player_payload(player),
                provenance=PROVENANCE_OBSERVED,
                observation_id=derive_observation_id(
                    agent_id=packet.agent_id, tick=tick, seq=seq
                ),
            )
        )
        seq += 1

    for moved in packet.moved_players:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_SAW_PLAYER_MOVE,
                payload=_moved_player_payload(moved),
                provenance=PROVENANCE_OBSERVED,
                observation_id=derive_observation_id(
                    agent_id=packet.agent_id, tick=tick, seq=seq
                ),
            )
        )
        seq += 1

    for body in packet.visible_bodies:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=EVENT_SAW_BODY,
                payload=_visible_body_payload(body),
                provenance=PROVENANCE_OBSERVED,
                observation_id=derive_observation_id(
                    agent_id=packet.agent_id, tick=tick, seq=seq
                ),
            )
        )
        seq += 1

    for audible in packet.audible_events:
        memory.append(
            EpisodicEvent(
                tick=tick,
                type=_audible_event_type(audible),
                payload=_audible_event_payload(audible),
                provenance=PROVENANCE_OBSERVED,
                observation_id=derive_observation_id(
                    agent_id=packet.agent_id, tick=tick, seq=seq
                ),
            )
        )
        seq += 1

    # The inferred system-wide aggregate is NOT first-hand citable evidence, so it
    # carries no observation id (Task 16.5).
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
                recent_co_presence=_recent_co_presence(
                    memory,
                    current_tick=tick,
                    fellow_impostor_ids=packet.self_state.fellow_impostor_ids,
                ),
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
    memory: MemoryStore,
    *,
    current_tick: int,
    fellow_impostor_ids: tuple[PlayerId, ...] = (),
) -> dict[RoomId, list[tuple[int, PlayerId]]]:
    """Map each room to the ``(tick, player_id)`` sightings in the proximity
    window ``[current_tick - BODY_PROXIMITY_WINDOW_TICKS, current_tick - 1]``.

    Built only from the agent's own first-hand ``saw_player`` rows, so it
    carries no information the agent did not directly observe -- the firewall
    is preserved. The current tick is excluded (the window is "shortly before"
    a discovery), so this is safe to call after the tick's rows are appended.

    Team-internal firewall (Task 9.3 input side, DESIGN.md §4.7). A fellow
    impostor's id in ``fellow_impostor_ids`` (the privileged self channel) is
    excluded from co-presence so DESIGN.md §6.3 Rule 1 never lifts suspicion of
    a teammate the impostor saw near a body it discovered: a witnessed teammate
    kill must not manufacture evidence against the team in the witness's own
    belief graph. The list is ``()`` for every crewmate and a sole impostor, so
    the crew belief path is byte-identical (no row is filtered).
    """

    teammates = frozenset(fellow_impostor_ids)
    earliest_tick = current_tick - BODY_PROXIMITY_WINDOW_TICKS
    co_presence: dict[RoomId, list[tuple[int, PlayerId]]] = {}
    for event in memory.recent(since_tick=earliest_tick):
        if event.type != EVENT_SAW_PLAYER or event.tick >= current_tick:
            continue
        player_id = event.payload["player_id"]
        if player_id in teammates:
            continue
        room = event.payload["room"]
        co_presence.setdefault(room, []).append((event.tick, player_id))
    return co_presence


def _self_state_payload(
    self_state: SelfView, *, agent_id: PlayerId
) -> Mapping[str, Any]:
    # ``agent_id`` is the recipient's OWN player id, recorded so the §6.6
    # renderer can identify and suppress self-subject ``saw_player`` rows
    # (Task 9.3, DESIGN.md §4.7: a self-subject sighting never renders into a
    # player's own prompt as third-person garble). It is the same id the
    # observation packet is addressed to; ObservationService never lists the
    # recipient in its own ``visible_players``, so a self-subject row does not
    # arise from first-hand perception today -- the renderer guard is a
    # defensive backstop that fails safe if such a row ever appears.
    #
    # ``pending_task_id`` is the agent's own next MAP task id (DESIGN.md §3.2) --
    # never the per-player instance id and never another player's task. It rides
    # through verbatim as an opaque string: the tactical policies resolve it
    # against the map-keyed ``task_locations`` and submit it back as the
    # ``do_task`` payload. The render/field/reader legs all treat it as the same
    # map id, so the engine advances the actor's own instance.
    #
    # ``owned_task_ids`` is the agent's own unfinished MAP task ids, recorded
    # verbatim -- same order, nothing filtered -- so the §6.6 renderer can read a
    # completion off the set LOSING an id rather than infer one from a
    # ``pending_task_id`` change (a redistributed instance also changes that id).
    # It rides the same self channel as ``pending_task_id`` and carries no role
    # bit: an impostor's tuple is the camouflage window.
    #
    # ``fellow_impostor_ids`` rides the same privileged self-state payload
    # that already carries ``role`` (Task 7.2): the impostor policy/prompt layer
    # reads its teammates from here in Wave 2 (J-5). It is ``()`` for crewmates
    # and serializes to a list in the prompt JSON, like other tuple fields.
    #
    # ``in_vent`` rides the same privileged self-state payload (Task 11.1): the
    # impostor tactical policy reads it to drive the in-vent vent-exit branch. It
    # is a plain self-position bool (a vented player is hidden from every other
    # agent), so it carries no role information and never leaves the self channel.
    return {
        "agent_id": agent_id,
        "room": self_state.room,
        "role": self_state.role,
        "pending_task_id": self_state.pending_task_id,
        "owned_task_ids": self_state.owned_task_ids,
        "fellow_impostor_ids": self_state.fellow_impostor_ids,
        "in_vent": self_state.in_vent,
    }


def _own_kill_payload(own_kill: OwnKillView) -> Mapping[str, Any]:
    # The recipient's OWN kill this tick (Task 11.3, DESIGN.md §1.3, §6.2). It
    # rides the privileged self channel like ``role``; the §6.2 renderer reads
    # ``victim_id`` to state the act ("You (IMPOSTOR) killed ...") and to
    # suppress the self-victim "discovered body" line.
    return {
        "victim_id": own_kill.victim_id,
        "room": own_kill.room,
    }


def _visible_player_payload(player: PlayerView) -> Mapping[str, Any]:
    return {
        "player_id": player.id,
        "room": player.room,
        "action": player.action,
    }


def _moved_player_payload(moved: MovedPlayerView) -> Mapping[str, Any]:
    # A witnessed room→room transition (Task 13.5.4). ``player_id`` mirrors the
    # ``saw_player`` payload key (the episodic store is internal, NOT the
    # leak-scanned packet, so ``player_id`` is the established episodic
    # convention); ``from_room`` / ``to_room`` give the §6.6 renderer the
    # directional sighting line and ``to_room`` (the actor's current room) wires
    # ``WorkingMemory.last_seen``.
    return {
        "player_id": moved.id,
        "from_room": moved.from_room,
        "to_room": moved.to_room,
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
    # ``sabotage_repair_rooms`` / ``sabotage_is_gating`` ride the public,
    # role-blind global aggregate (Task 11.5, DESIGN.md §8.3): the crew policy
    # (11.6) reads the repair routing target from here, never from ``engine/``.
    # Both are empty/false unless a sabotage is active.
    return {
        "tasks_completed": global_state.tasks_completed,
        "tasks_total": global_state.tasks_total,
        "task_completion_percent": global_state.task_completion_percent,
        "sabotage_active": global_state.sabotage_active,
        "sabotage_kind": global_state.sabotage_kind,
        "sabotage_repair_rooms": global_state.sabotage_repair_rooms,
        "sabotage_is_gating": global_state.sabotage_is_gating,
    }


__all__ = [
    "EVENT_COOLDOWN_STATUS",
    "EVENT_GLOBAL_STATUS",
    "EVENT_HEARD_SABOTAGE_ALARM",
    "EVENT_OWN_KILL",
    "EVENT_REPORTED_TESTIMONY",
    "EVENT_SAW_BODY",
    "EVENT_SAW_PLAYER",
    "EVENT_SAW_PLAYER_MOVE",
    "EVENT_SELF_STATE",
    "PROVENANCE_INFERRED",
    "PROVENANCE_OBSERVED",
    "PROVENANCE_REPORTED",
    "ingest_packet",
]
