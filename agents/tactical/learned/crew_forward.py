"""The opt-in crew surface's pure-Python forward pass (Task 18.7).

The shipped inference path for the OPT-IN crew deployment surface
(audits/audit-phase-18-planning.md §4 #7) — the learned crew option scorer over
the scripted crew FSM's own option menu, widened to the owned-task basis — ported
line-for-line from the training-side references
(``training/crew/options.py`` + ``training/crew/scorer.py`` + ``training/env.py``)
under the firewall contract. Adoption stays GATED: this module ships a SURFACE
beside the untouched scripted default (``agents/tactical/crewmate_policy.py``), not
a champion. The committed artifact is the measurement-tier
``crew-owned-tasks-es`` genome; nothing here promotes it over the FSM.

Firewall shape (the 15.20 ``utility_es.py`` → ``forward.py`` precedent, crew
edition):

- **No engine import.** The crew menu module already imports only firewall-legal
  packages; the mask mirror (:func:`_build_action_mask`) is derived from the
  observation packet + the two policy-side trackers (sabotage kinds and
  emergency uses-remaining are not on the observation surface — the
  ``EmergencyPacingTracker`` precedent), never from ``engine/``.
- **No training import.** Everything the menu, the mask, and the argmax tie-break
  need is already ``agents/``-side; :class:`~agents.tactical.learned.forward.LearnedDecisionFrame`
  and :func:`~agents.tactical.learned.forward.intent_key` are REUSED from the
  impostor forward pass rather than redefined.
- **No numpy / torch.** The forward pass is a 27-weight LINEAR scorer — a
  ``math.fsum`` dot product plus bias per option, no activation, no
  transcendental — so the Q4 bit-exact gate (audits/audit-phase-15-pause.md
  decision 6) can pin token-identical equality of this pass against the
  training-side reference (``training/crew/scorer.py::CrewOptionScorer``) over
  the committed float-hex weights.

The accumulation is ported VERBATIM: ``math.fsum`` is correctly rounded and
order-independent, so the bit-exact hazard is not summation order — it is
substituting a naive ``sum()`` loop (or numpy) for ``fsum``, which diverges in
the last ULP. Do not "simplify" the ``fsum`` expression.

Zero reimplementation drift on the menu and the mask: exactly like the
references, option generation calls the crew FSM's own pure helpers
(``CrewmatePolicy._first_visible_body`` / ``_kill_witnessed`` /
``_active_gating_sabotage`` / ``_walk_to_button`` / ``_walk_to_repair`` /
``_return_to_hub`` / ``_move_toward`` / ``_do_task`` / ``_report``) and the
module-level ``_seen_victim_ids`` / ``_episodic_last_seen`` — so the menu stays
byte-faithful to the scripted ladder and only the ARBITRATION (which option to
take) is learned. The scripted crew FSM itself stays in-tree untouched as the
default, the anchor, and the fallback.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Final, Literal, TypeAlias

from agents.memory.store import AgentMemory
from agents.tactical.crewmate_policy import (
    KILL_WITNESS_REASON,
    SUSPICION_ACCUMULATION_REASON,
    CrewmatePolicy,
    _seen_victim_ids,
)
from agents.tactical.features import (
    BELIEF_QUANT_LEVELS,
    _episodic_last_seen,
    beliefs_suspicion,
    quantize_unit_interval,
    weights_from_hex_json,
)
from agents.tactical.learned.forward import LearnedDecisionFrame, intent_key
from agents.tactical.pathing import find_path
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    EmergencyMeetingIntent,
    KillIntent,
    MoveIntent,
    RepairSabotageIntent,
    ReportBodyIntent,
    SabotageIntent,
    VentIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView

# --------------------------------------------------------------------------- #
# The crew option menu — ported VERBATIM from training/crew/options.py         #
# (Task 15.16 the pinned menu; Task 15.22 the widened owned-task basis). Only  #
# the arbitration is learned; the generation mirrors the scripted ladder.      #
# --------------------------------------------------------------------------- #

# The crew option alphabet, in fixed order (the kind one-hot block order keys
# off this tuple). The FIXED set the task contract names: five kinds mirror the
# FSM's own ladder rungs; ``buddy`` / ``patrol`` are the two observable-only
# additions from the planning audit's §5.2 option vocabulary.
CrewOptionKind: TypeAlias = Literal[
    "continue_task",
    "buddy",
    "patrol",
    "report",
    "emergency",
    "repair",
    "hold",
    # The Task 15.22 widened-basis addition. It is NOT a member of the PINNED
    # :data:`CREW_OPTION_KINDS` alphabet (the 15.16 seven-kind menu is
    # byte-identical); it appears only in :data:`OWNED_TASK_OPTION_KINDS`, the
    # basis :func:`enumerate_owned_task_options` re-bases onto.
    "nearest_task",
]
CREW_OPTION_KINDS: Final[tuple[CrewOptionKind, ...]] = (
    "continue_task",
    "buddy",
    "patrol",
    "report",
    "emergency",
    "repair",
    "hold",
)

# The per-option feature vector, in fixed order: the seven kind one-hots (in
# CREW_OPTION_KINDS order) then fourteen scalars. The option-specific scalars
# carry exactly the signal the option keys on — ``path_hops_norm`` is the A*
# distance to the option's goal, ``group_size_norm`` / ``group_min_suspicion``
# the buddy group's co-presence + trust shape, ``suspect_suspicion`` /
# ``lastseen_age_norm`` the patrol target's cue strength + staleness,
# ``emergency_press`` whether the emergency option is the press (vs the button
# walk) — and the decision-level scalars carry the ladder's own trigger context
# (body / witnessed kill / gating sabotage / task completion / crowd density /
# the agent's own quantized suspicion aggregates), so a linear head can express
# (and re-weight) the scripted ladder's priorities.
CREW_OPTION_FEATURE_NAMES: Final[tuple[str, ...]] = tuple(
    f"kind_{kind}" for kind in CREW_OPTION_KINDS
) + (
    "path_hops_norm",
    "goal_is_current_room",
    "group_size_norm",
    "group_min_suspicion",
    "suspect_suspicion",
    "lastseen_age_norm",
    "emergency_press",
    "body_in_own_room",
    "kill_witnessed",
    "sabotage_gating",
    "task_completion_percent",
    "visible_players_norm",
    "own_max_suspicion",
    "own_over_gate",
)

# Normalizers keeping the linear head's inputs in a bounded, roster-robust
# range (the 15.15 menu's caps, plus the encoder's last-seen age cap).
_PATH_HOPS_CAP: Final[float] = 10.0
_VISIBLE_PLAYERS_CAP: Final[float] = 8.0
_GROUP_SIZE_CAP: Final[float] = 8.0
_LASTSEEN_AGE_CAP: Final[float] = 50.0

# The eject gate + the neutral prior on the encoder's integer grid. Every
# suspicion comparison below is an INTEGER comparison on this grid — never a
# raw-float ``>=`` (the §6.3 determinism hazard the encoder doctrine kills).
_SUSPICION_GATE_QUANTUM: Final[int] = quantize_unit_interval(
    DEFAULT_SKIP_CONFIDENCE_THRESHOLD
)
_NEUTRAL_SUSPICION_QUANTUM: Final[int] = quantize_unit_interval(0.5)


def crew_genome_length() -> int:
    """Flat genome length: one weight per option feature + a trailing bias."""

    return len(CREW_OPTION_FEATURE_NAMES) + 1


# --------------------------------------------------------------------------- #
# The Task 15.22 widened option basis (audits/audit-phase-15-pause.md decision  #
# 5). The legacy CREW_OPTION_* surfaces above are PINNED (byte-identical);      #
# these are the additive widened surfaces the wrapper basis re-bases onto.      #
# --------------------------------------------------------------------------- #

# The widened alphabet: the seven pinned kinds (a PREFIX of this tuple, so a
# legacy kind's one-hot index is unchanged) then the ``nearest_task`` addition.
OWNED_TASK_OPTION_KINDS: Final[tuple[CrewOptionKind, ...]] = (
    *CREW_OPTION_KINDS,
    "nearest_task",
)

# The owned-task decision-level normalizer (mirrors the 15.16 roster caps): a
# roster carries a handful of owned instances, so eight caps the batch signal.
_OWNED_TASKS_CAP: Final[float] = 8.0

# The widened per-option feature vector: the eight kind one-hots (in
# OWNED_TASK_OPTION_KINDS order) then the FOURTEEN legacy scalars VERBATIM (the
# 15.16 block, carried through re-basing unchanged) then the four owned-task
# scalars — ``owned_tasks_norm`` the batch size, ``nearest_owned_hops_norm`` the
# distance to the nearest owned task, ``same_room_owned_norm`` the in-room batch,
# ``goal_room_owned_norm`` the owned count in a task-directed option's goal room
# (the same-room batching cue). 8 + 14 + 4 = 26.
OWNED_TASK_OPTION_FEATURE_NAMES: Final[tuple[str, ...]] = (
    tuple(f"kind_{kind}" for kind in OWNED_TASK_OPTION_KINDS)
    + CREW_OPTION_FEATURE_NAMES[len(CREW_OPTION_KINDS) :]
    + (
        "owned_tasks_norm",
        "nearest_owned_hops_norm",
        "same_room_owned_norm",
        "goal_room_owned_norm",
    )
)


def owned_task_genome_length() -> int:
    """Widened flat genome length: one weight per widened feature + a bias (27)."""

    return len(OWNED_TASK_OPTION_FEATURE_NAMES) + 1


@dataclass(frozen=True)
class CrewOption:
    """One crew option the learned utility ranks (ported, Task 15.16 shape).

    ``kind`` is the menu slot (a :data:`CREW_OPTION_KINDS` member — or
    ``nearest_task`` for a widened-basis option), ``intent`` the concrete
    submission-legal :class:`~observation.action_intent.ActionIntent` realizing
    it this tick, ``target_id`` the option's target — the patrol suspect's
    player id, the buddy option's goal room id, the nearest_task's task id — or
    ``None``, and ``features`` the fixed-order feature vector the scorer dots its
    weights against.
    """

    kind: CrewOptionKind
    intent: ActionIntent
    target_id: str | None
    features: tuple[float, ...]


def _path_hops(public_map: PublicMapView, start: str, goal: str) -> int:
    """A* hop count from ``start`` to ``goal`` (unreachable = sentinel).

    Mirrors the FSM's ``_repair_distance``: an unreachable or unknown room
    sorts to a sentinel one larger than any possible path length, which the
    feature normalizer then caps at 1.0 — a disconnected topology never raises
    out of the featurizer.
    """

    try:
        return len(find_path(public_map=public_map, start=start, goal=goal)) - 1
    except ValueError:
        return len(public_map.room_ids) + 1


def _movement_step(
    public_map: PublicMapView, start: str, goal: str
) -> tuple[str, int] | None:
    """The next-hop room and full A* distance toward ``goal`` (``None`` if none).

    ``goal`` must differ from ``start`` (the caller guards this); returns the
    first step (the FSM's ``_move_toward`` ``path[1]``) plus ``len(path) - 1``
    so the emitted ``MoveIntent`` is one hop while ``path_hops_norm`` carries
    the full distance. A ``find_path`` ValueError (unreachable / unknown goal)
    maps to ``None`` so the caller SKIPS the option — the FSM's own
    degrade-to-wait fall-through, with the wait already on the menu as
    ``hold``.
    """

    try:
        path = find_path(public_map=public_map, start=start, goal=goal)
    except ValueError:
        return None
    if len(path) < 2:
        return None
    return path[1], len(path) - 1


def enumerate_crew_options(
    packet: ObservationPacket,
    public_map: PublicMapView,
    memory: AgentMemory,
    *,
    fsm_intent: ActionIntent,
    emergency_uses_remaining: int | None = None,
) -> tuple[CrewOption, ...]:
    """The crew option menu — FSM option generation + the two audit additions.

    Ported verbatim from the training-side reference
    (``training/crew/options.py::enumerate_crew_options``). Mirrors the crew
    decide() ladder's structure (``agents/tactical/crewmate_policy.py:343-423``)
    but keeps EVERY option the state admits instead of short-circuiting on the
    ladder's fixed priority, so the learned utility does the arbitration the
    ladder hard-coded. Self facts come from the PACKET (the observable self
    surface): ``room`` / ``in_vent`` / ``pending_task_id``. Body / witnessed-kill
    / gating-sabotage facts come from the FSM's own pure helpers over the agent's
    live episodic events, so the FSM-derived options are byte-faithful to the
    scripted ladder with zero reimplementation drift.

    The menu, rung for rung:

    * ``report`` — the FSM's rung-1 interrupt: the alphabetically-first body in
      the agent's own room (``_first_visible_body``), realized via ``_report``.
    * ``emergency`` — the button course, ONLY when the FSM itself took it this
      tick, so the ``EmergencyPacingTracker`` gate is honored by construction
      (never re-derived, never bypassed): (a) the rung-2 kill-witness interrupt
      is memory-derived (``_kill_witnessed``) and realizes ``_walk_to_button``
      with the FSM's :data:`KILL_WITNESS_REASON`; (b) an
      :class:`EmergencyMeetingIntent` ``fsm_intent`` is the tracker-gated
      rung-4 press, kept VERBATIM (its ``reason`` payload rides through — the
      15.16 mask canonicalization makes it submission-legal); (c) the rung-4
      button WALK is detected by ladder reconstruction — no body, no witnessed
      kill, no gating sabotage, and ``fsm_intent`` equals the button-walk step
      while differing from the task-continuation step (when the two steps
      coincide the move is already on the menu as ``continue_task``, so no
      separate option is materialized). With ``emergency_uses_remaining``
      tracked (the wrapper) a PRESS is skipped at zero remaining uses — the
      mask's emergency legality mirror — while ``None`` (an untracked caller)
      keys the press on the FSM's own proposal alone.
    * ``repair`` — the rung-3 gating-sabotage diversion
      (``_active_gating_sabotage`` + ``_walk_to_repair``).
    * ``continue_task`` — the rung 5-8 task continuation: ``do_task`` in the
      pending task's room (skipped while a gating sabotage makes it
      engine-illegal — the repair option carries that state), one A* step
      toward it otherwise, and the FSM's hub-routing walk when there is no
      routable pending task (``_return_to_hub``; already AT the hub the FSM
      waits, which ``hold`` carries).
    * ``buddy`` — NEW (audit §4.1 "no witness/buddy/safety awareness"): one A*
      step toward the room holding the largest belief-trusted group — presumed-
      living players with a last-seen room whose quantized own-suspicion sits
      BELOW the eject gate — tie-broken (size DESC, hops ASC, room-id ASC); a
      ``WaitIntent`` holds position when already with the group. Co-presence +
      low own-suspicion keyed, never role.
    * ``patrol`` — NEW: one A* step toward the last-seen room of the most-
      suspected presumed-living player (quantized suspicion strictly above the
      neutral 0.5 prior; suspicion DESC, player-id ASC tie-break); a
      ``WaitIntent`` shadows in place when already there.
    * ``hold`` — always: the FSM's wait terminal.

    Raises :class:`ValueError` on empty memory (exactly like the FSM), on a
    non-crew packet (the menu is crew-only; the scorer role-gates before
    calling), and on a vented crew self-state (structurally impossible — crew
    cannot vent — so it is a boundary-contract violation, not a fallback).
    """

    events = memory.episodic.recent(since_tick=0)
    if not events:
        raise ValueError(
            "crew option menu requires at least one episodic event in memory"
        )
    if packet.self_state.role != "CREWMATE":
        raise ValueError(
            f"crew option menu is crew-only; got role {packet.self_state.role!r} "
            f"for {packet.agent_id!r}"
        )
    if packet.self_state.in_vent:
        raise ValueError(
            f"crew option menu got an in-vent crew self-state for "
            f"{packet.agent_id!r} at tick {packet.tick} (crew cannot vent)"
        )

    latest_events = tuple(event for event in events if event.tick == events[-1].tick)
    actor = packet.agent_id
    own_room = packet.self_state.room
    pending_task_id = packet.self_state.pending_task_id
    global_state = packet.global_state
    fsm = CrewmatePolicy(agent_id=actor)

    # The FSM's own trigger facts (its pure helpers — zero drift).
    body_id = CrewmatePolicy._first_visible_body(latest_events, own_room=own_room)
    kill_witnessed = CrewmatePolicy._kill_witnessed(latest_events, own_room=own_room)
    gating_sabotage = CrewmatePolicy._active_gating_sabotage(events)
    sabotage_gating = bool(
        global_state.sabotage_active and global_state.sabotage_is_gating
    )

    # The agent's OWN belief/last-seen surface (encoder-grid quantized, sorted).
    beliefs = memory.beliefs
    last_seen = _episodic_last_seen(memory.episodic)
    presumed_dead = _seen_victim_ids(memory.episodic)
    roster = sorted((set(beliefs.known_players()) | set(last_seen)) - {actor})
    living_seen = [
        player_id
        for player_id in roster
        if player_id not in presumed_dead and player_id in last_seen
    ]
    suspicion_quantum = {
        player_id: quantize_unit_interval(beliefs_suspicion(memory, player_id))
        for player_id in roster
    }
    living_quanta = [
        suspicion_quantum[player_id]
        for player_id in roster
        if player_id not in presumed_dead
    ]
    max_susp_quantum = max(living_quanta, default=0)

    # Decision-level feature constants (identical across every option this tick).
    body_in_own_room = 1.0 if body_id is not None else 0.0
    kill_witnessed_flag = 1.0 if kill_witnessed else 0.0
    sabotage_gating_flag = 1.0 if sabotage_gating else 0.0
    task_completion = global_state.task_completion_percent
    visible_players_norm = len(packet.visible_players) / _VISIBLE_PLAYERS_CAP
    own_max_suspicion = max_susp_quantum / BELIEF_QUANT_LEVELS
    own_over_gate = 1.0 if max_susp_quantum >= _SUSPICION_GATE_QUANTUM else 0.0

    def features_for(
        kind: CrewOptionKind,
        *,
        path_hops: int | None = None,
        goal_is_current: bool = False,
        group_size: int | None = None,
        group_min_suspicion: int | None = None,
        suspect_suspicion: int | None = None,
        lastseen_age: int | None = None,
        emergency_press: bool = False,
    ) -> tuple[float, ...]:
        one_hots = tuple(
            1.0 if kind == candidate else 0.0 for candidate in CREW_OPTION_KINDS
        )
        hops_norm = (
            min(path_hops / _PATH_HOPS_CAP, 1.0) if path_hops is not None else 0.0
        )
        return one_hots + (
            hops_norm,
            1.0 if goal_is_current else 0.0,
            min(group_size / _GROUP_SIZE_CAP, 1.0) if group_size is not None else 0.0,
            (
                group_min_suspicion / BELIEF_QUANT_LEVELS
                if group_min_suspicion is not None
                else 0.0
            ),
            (
                suspect_suspicion / BELIEF_QUANT_LEVELS
                if suspect_suspicion is not None
                else 0.0
            ),
            (
                min(lastseen_age / _LASTSEEN_AGE_CAP, 1.0)
                if lastseen_age is not None
                else 0.0
            ),
            1.0 if emergency_press else 0.0,
            body_in_own_room,
            kill_witnessed_flag,
            sabotage_gating_flag,
            task_completion,
            visible_players_norm,
            own_max_suspicion,
            own_over_gate,
        )

    options: list[CrewOption] = []

    # REPORT — the rung-1 interrupt (mask-legal: the helper filters to bodies in
    # the agent's own room, exactly the mask's report predicate).
    if body_id is not None:
        options.append(
            CrewOption(
                kind="report",
                intent=fsm._report(body_id=body_id),
                target_id=None,
                features=features_for("report", goal_is_current=True),
            )
        )

    # The rung 5-8 task continuation, computed once: it is BOTH the
    # continue_task option's intent and the fallback the suspicion-walk
    # detection diffs the FSM intent against.
    continuation: ActionIntent
    task_room = (
        public_map.task_locations.get(pending_task_id)
        if pending_task_id is not None
        else None
    )
    if pending_task_id is None or task_room is None:
        continuation = fsm._return_to_hub(public_map=public_map, own_room=own_room)
    elif own_room == task_room:
        continuation = fsm._do_task(task_id=pending_task_id)
    else:
        continuation = fsm._move_toward(
            public_map=public_map, own_room=own_room, goal=task_room
        )

    # EMERGENCY — the button course, only when the FSM's own (tracker-gated)
    # decision took it this tick. See the docstring for the three producers.
    emergency_intent: ActionIntent | None = None
    if kill_witnessed:
        emergency_intent = fsm._walk_to_button(
            public_map=public_map, own_room=own_room, reason=KILL_WITNESS_REASON
        )
    elif isinstance(fsm_intent, EmergencyMeetingIntent):
        emergency_intent = fsm_intent
    elif body_id is None and gating_sabotage is None:
        button_course = fsm._walk_to_button(
            public_map=public_map,
            own_room=own_room,
            reason=SUSPICION_ACCUMULATION_REASON,
        )
        if (
            isinstance(button_course, MoveIntent)
            and fsm_intent == button_course
            and fsm_intent != continuation
        ):
            emergency_intent = button_course
    if (
        isinstance(emergency_intent, EmergencyMeetingIntent)
        and emergency_uses_remaining is not None
        and emergency_uses_remaining <= 0
    ):
        # The mask's emergency-uses mirror: a press with no uses remaining is
        # engine-rejected, so it never reaches the menu when the wrapper
        # tracks the count.
        emergency_intent = None
    if emergency_intent is not None:
        press = isinstance(emergency_intent, EmergencyMeetingIntent)
        options.append(
            CrewOption(
                kind="emergency",
                intent=emergency_intent,
                target_id=None,
                features=features_for(
                    "emergency",
                    path_hops=_path_hops(
                        public_map, own_room, public_map.emergency_button_room
                    ),
                    goal_is_current=press,
                    emergency_press=press,
                ),
            )
        )

    # REPAIR — the rung-3 gating-sabotage diversion (repair rooms come ONLY
    # from the public GlobalView channel the helper read).
    if gating_sabotage is not None:
        repair_hops = min(
            _path_hops(public_map, own_room, room)
            for room in gating_sabotage.repair_rooms
        )
        options.append(
            CrewOption(
                kind="repair",
                intent=fsm._walk_to_repair(
                    public_map=public_map, own_room=own_room, sabotage=gating_sabotage
                ),
                target_id=None,
                features=features_for(
                    "repair",
                    path_hops=repair_hops,
                    goal_is_current=own_room in gating_sabotage.repair_rooms,
                ),
            )
        )

    # CONTINUE_TASK — the rung 5-8 continuation. An in-place do_task is skipped
    # while a gating sabotage makes it engine-illegal (the mask's do_task
    # predicate — the repair option carries that state), and the at-hub wait is
    # skipped because ``hold`` carries it.
    include_continuation = not isinstance(continuation, WaitIntent)
    if isinstance(continuation, DoTaskIntent) and sabotage_gating:
        include_continuation = False
    if include_continuation:
        task_goal = task_room if task_room is not None else public_map.meeting_room
        options.append(
            CrewOption(
                kind="continue_task",
                intent=continuation,
                target_id=None,
                features=features_for(
                    "continue_task",
                    path_hops=_path_hops(public_map, own_room, task_goal),
                    goal_is_current=own_room == task_goal,
                ),
            )
        )

    # BUDDY — toward the nearest visible/belief-trusted group (co-presence +
    # low own-suspicion keyed, never role). Trusted = quantized suspicion BELOW
    # the eject gate; grouped by last-seen room; (size DESC, hops ASC, room ASC).
    trusted = [
        player_id
        for player_id in living_seen
        if suspicion_quantum[player_id] < _SUSPICION_GATE_QUANTUM
    ]
    group_rooms: dict[str, list[str]] = {}
    for player_id in trusted:
        group_rooms.setdefault(last_seen[player_id][1], []).append(player_id)
    if group_rooms:
        goal_room = min(
            sorted(group_rooms),
            key=lambda room: (
                -len(group_rooms[room]),
                _path_hops(public_map, own_room, room),
                room,
            ),
        )
        members = group_rooms[goal_room]
        group_min = min(suspicion_quantum[player_id] for player_id in members)
        group_age = min(
            max(0, packet.tick - last_seen[player_id][0]) for player_id in members
        )
        buddy_intent: ActionIntent | None
        buddy_hops = 0
        if goal_room == own_room:
            buddy_intent = WaitIntent(actor=actor, type="wait")
        else:
            step = _movement_step(public_map, own_room, goal_room)
            if step is None:
                buddy_intent = None
            else:
                next_room, buddy_hops = step
                buddy_intent = MoveIntent.model_validate(
                    {
                        "type": "move",
                        "actor": actor,
                        "payload": {"to_room": next_room},
                    }
                )
        if buddy_intent is not None:
            options.append(
                CrewOption(
                    kind="buddy",
                    intent=buddy_intent,
                    target_id=goal_room,
                    features=features_for(
                        "buddy",
                        path_hops=buddy_hops,
                        goal_is_current=goal_room == own_room,
                        group_size=len(members),
                        group_min_suspicion=group_min,
                        lastseen_age=group_age,
                    ),
                )
            )

    # PATROL — toward the last-seen room of the most-suspected presumed-living
    # player (strictly above the neutral prior; suspicion DESC, id ASC).
    suspects = [
        player_id
        for player_id in living_seen
        if suspicion_quantum[player_id] > _NEUTRAL_SUSPICION_QUANTUM
    ]
    if suspects:
        suspect = min(
            suspects, key=lambda player_id: (-suspicion_quantum[player_id], player_id)
        )
        suspect_tick, suspect_room = last_seen[suspect]
        patrol_intent: ActionIntent | None
        patrol_hops = 0
        if suspect_room == own_room:
            patrol_intent = WaitIntent(actor=actor, type="wait")
        else:
            step = _movement_step(public_map, own_room, suspect_room)
            if step is None:
                patrol_intent = None
            else:
                next_room, patrol_hops = step
                patrol_intent = MoveIntent.model_validate(
                    {
                        "type": "move",
                        "actor": actor,
                        "payload": {"to_room": next_room},
                    }
                )
        if patrol_intent is not None:
            options.append(
                CrewOption(
                    kind="patrol",
                    intent=patrol_intent,
                    target_id=suspect,
                    features=features_for(
                        "patrol",
                        path_hops=patrol_hops,
                        goal_is_current=suspect_room == own_room,
                        suspect_suspicion=suspicion_quantum[suspect],
                        lastseen_age=max(0, packet.tick - suspect_tick),
                    ),
                )
            )

    # HOLD — always available (the FSM's wait terminal).
    options.append(
        CrewOption(
            kind="hold",
            intent=WaitIntent(actor=actor, type="wait"),
            target_id=None,
            features=features_for("hold", goal_is_current=True),
        )
    )
    return tuple(options)


def enumerate_owned_task_options(
    packet: ObservationPacket,
    public_map: PublicMapView,
    memory: AgentMemory,
    *,
    fsm_intent: ActionIntent,
    emergency_uses_remaining: int | None = None,
) -> tuple[CrewOption, ...]:
    """Re-base the legacy menu onto the widened basis + append nearest_task.

    Ported verbatim from the training-side reference
    (``training/crew/options.py::OwnedTaskOptionBasis.enumerate``, Task 15.22) as
    a MODULE FUNCTION: the shipped crew surface is FIXED to the committed
    owned-task basis, so there is no basis plumbing and no legacy-genome scorer
    mode. Inherits every raise semantic of :func:`enumerate_crew_options` (empty
    memory / non-crew / vented) by delegating to it FIRST. When a body is visible
    the legacy menu carries a ``report`` option; the interrupt-preserving
    constraint returns a 1-tuple of ONLY the re-based report (intent/target
    verbatim) — the structural interrupt (audit decision 5, the FO-8-style
    guard: the learned head is REMOVED from the ``report`` selectable set rather
    than penalized for suppressing it). Otherwise every legacy option is widened
    (its one-hot re-based to the widened alphabet — the 15.16 kinds are a prefix,
    so a kept option's index is unchanged — its fourteen legacy scalars carried
    verbatim, and the four owned-task scalars appended) and a ``nearest_task``
    option is appended when the nearest routable owned task is not the engine-fed
    ``pending_task_id``.
    """

    legacy = enumerate_crew_options(
        packet,
        public_map,
        memory,
        fsm_intent=fsm_intent,
        emergency_uses_remaining=emergency_uses_remaining,
    )

    actor = packet.agent_id
    own_room = packet.self_state.room
    pending_task_id = packet.self_state.pending_task_id
    owned = packet.self_state.owned_task_ids
    global_state = packet.global_state
    sabotage_gating = bool(
        global_state.sabotage_active and global_state.sabotage_is_gating
    )
    fsm = CrewmatePolicy(agent_id=actor)

    # Owned-task context: the routable owned tasks, their rooms + A* hops.
    # An unroutable / unknown owned task (no ``task_locations`` entry, or a
    # disconnected room) is skipped from the nearest search exactly as the
    # movement featurizer degrades — never a raise.
    owned_rooms: dict[str, str] = {}
    owned_hops: dict[str, int] = {}
    for task_id in owned:
        room = public_map.task_locations.get(task_id)
        if room is None:
            continue
        owned_rooms[task_id] = room
        owned_hops[task_id] = _path_hops(public_map, own_room, room)
    nearest_tid: str | None = None
    if owned_hops:
        nearest_tid = min(owned_hops, key=lambda tid: (owned_hops[tid], tid))
    nearest_room = owned_rooms[nearest_tid] if nearest_tid is not None else None
    nearest_hops = owned_hops[nearest_tid] if nearest_tid is not None else None

    # The decision-level owned scalars (identical across every option).
    owned_tasks_norm = min(len(owned) / _OWNED_TASKS_CAP, 1.0)
    nearest_owned_hops_norm = (
        min(nearest_hops / _PATH_HOPS_CAP, 1.0) if nearest_hops is not None else 0.0
    )

    def owned_in_room(room: str | None) -> float:
        if room is None:
            return 0.0
        count = sum(
            1 for task_id in owned if public_map.task_locations.get(task_id) == room
        )
        return min(count / _OWNED_TASKS_CAP, 1.0)

    same_room_owned_norm = owned_in_room(own_room)

    def owned_block(goal_room: str | None) -> tuple[float, ...]:
        # ``goal_room_owned_norm`` is a task-directed cue: the continue_task
        # / nearest_task goal room's owned count, 0.0 for every other kind.
        return (
            owned_tasks_norm,
            nearest_owned_hops_norm,
            same_room_owned_norm,
            owned_in_room(goal_room),
        )

    def one_hots(kind: CrewOptionKind) -> tuple[float, ...]:
        return tuple(
            1.0 if kind == candidate else 0.0 for candidate in OWNED_TASK_OPTION_KINDS
        )

    def widen(option: CrewOption, *, goal_room: str | None) -> CrewOption:
        legacy_scalars = option.features[len(CREW_OPTION_KINDS) :]
        return CrewOption(
            kind=option.kind,
            intent=option.intent,
            target_id=option.target_id,
            features=one_hots(option.kind) + legacy_scalars + owned_block(goal_room),
        )

    # continue_task's goal room recomputed EXACTLY as the legacy function:
    # the pending task's room, or the meeting room when there is none.
    task_room = (
        public_map.task_locations.get(pending_task_id)
        if pending_task_id is not None
        else None
    )
    continue_goal_room = task_room if task_room is not None else public_map.meeting_room

    # INTERRUPT-PRESERVING CONSTRAINT: a visible body → ONLY report. The
    # widened menu never offers the head anything to select away from — the
    # FSM rung-1 interrupt made structural (the 15.16 starvation channel is
    # unreachable by removal from the selectable set, not by a penalty).
    for option in legacy:
        if option.kind == "report":
            return (widen(option, goal_room=None),)

    widened: list[CrewOption] = [
        widen(
            option,
            goal_room=(continue_goal_room if option.kind == "continue_task" else None),
        )
        for option in legacy
    ]

    # NEAREST_TASK — nearest-of-N owned selection (the widened-basis add).
    # Skipped when the nearest owned task IS already the engine-fed pending
    # task (``continue_task`` carries it) or when there is no routable owned
    # task. The decision block (the last seven legacy scalars — the
    # per-tick constants) is carried from the always-present hold option's
    # tail, so the added option shares the menu's decision context.
    if nearest_tid is not None and nearest_tid != pending_task_id:
        assert nearest_room is not None and nearest_hops is not None
        nearest_intent: ActionIntent | None
        if own_room == nearest_room:
            # In the task room: submit ``do_task`` — but SKIP the whole
            # option while a gating sabotage makes it engine-illegal (the
            # mask/engine do_task predicate; there is no move to fall to).
            nearest_intent = (
                None if sabotage_gating else fsm._do_task(task_id=nearest_tid)
            )
        else:
            step = _movement_step(public_map, own_room, nearest_room)
            nearest_intent = (
                None
                if step is None
                else MoveIntent.model_validate(
                    {
                        "type": "move",
                        "actor": actor,
                        "payload": {"to_room": step[0]},
                    }
                )
            )
        if nearest_intent is not None:
            hold_option = next(option for option in legacy if option.kind == "hold")
            decision_block = hold_option.features[len(CREW_OPTION_KINDS) + 7 :]
            option_scalars = (
                min(nearest_hops / _PATH_HOPS_CAP, 1.0),
                1.0 if own_room == nearest_room else 0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            )
            widened.append(
                CrewOption(
                    kind="nearest_task",
                    intent=nearest_intent,
                    target_id=nearest_tid,
                    features=(
                        one_hots("nearest_task")
                        + option_scalars
                        + decision_block
                        + owned_block(nearest_room)
                    ),
                )
            )
    return tuple(widened)


# --------------------------------------------------------------------------- #
# The submission mask — ported VERBATIM from training/env.py:119-367           #
# (Task 15.8 the mask; Task 15.16 the emergency canonicalization). The mirror  #
# is WHOLE (every branch, including the impostor ones) so the fixture pins can  #
# assert full equality against ``training.env.build_action_mask``. Renamed to  #
# private ``_``-prefixed names: this ships the mirror, not a second public API. #
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _ActionMask:
    """A legal-action mask over the option/intent space at one tick (ported, 15.8).

    Ported verbatim from ``training/env.py::ActionMask``. The mask SPLITS two
    vocabularies (audit §5.1 caveat 2):

    * ``engine_legal`` — concrete :class:`~observation.action_intent.ActionIntent`
      candidates that RESOLVE without an ``ActionRejected`` from the engine.
    * ``submission_only`` — observation-meaningful submissions the engine REJECTS
      but that still carry signal: the impostor's pretend ``do_task`` (it owns no
      instance, so it is engine-rejected, yet it renders as ``action="task"``
      camouflage to witnesses). A strict engine-legal-only vocabulary would
      delete this lever and regress the impostor's task-traffic mimicry.
    * ``illegal`` — enumerated candidates that are neither engine-legal nor
      observation-meaningful (a far move, a wrong-room ``do_task`` for a crew, an
      out-of-range kill, …). Kept so the property test can assert every unmasked
      candidate is engine-rejected.

    ``submission_legal`` is the full set a policy may emit: ``engine_legal`` plus
    ``submission_only``.

    Membership is exact frozen-model equality with ONE canonicalization (Task
    15.16): emergency intents compare with their free-form ``reason`` payload
    dropped — see :func:`_canonical_mask_intent`.
    """

    engine_legal: tuple[ActionIntent, ...]
    submission_only: tuple[ActionIntent, ...]
    illegal: tuple[ActionIntent, ...]

    @property
    def submission_legal(self) -> tuple[ActionIntent, ...]:
        """Every intent a policy may submit (engine-legal + observation-meaningful)."""

        return self.engine_legal + self.submission_only

    def is_engine_legal(self, intent: ActionIntent) -> bool:
        return _canonical_mask_intent(intent) in self.engine_legal

    def is_submission_legal(self, intent: ActionIntent) -> bool:
        canonical = _canonical_mask_intent(intent)
        return canonical in self.engine_legal or canonical in self.submission_only


def _canonical_mask_intent(intent: ActionIntent) -> ActionIntent:
    """Canonicalize one intent for mask membership (ported, Task 15.16).

    Ported verbatim from ``training/env.py::_canonical_mask_intent``. The
    emergency-intent canonicalization that closes the documented 15.8
    exact-equality gap: the mask's emergency entry carries the DEFAULT payload
    (``reason=None``, :func:`_build_action_mask`'s EMERGENCY region), while the
    crew FSM stamps a producer tag on the same action
    (``reason='suspicion_accumulation'`` / ``'kill_witnessed'`` —
    ``agents/tactical/crewmate_policy.py``). The engine's emergency legality is
    reason-blind (the tag is agent-side provenance for replay/eval tooling, never
    an engine input), but frozen-pydantic equality is field-exact, so without
    canonicalization a selector delegating the FSM's own emergency would fail
    :meth:`_ActionMask.is_submission_legal` and raise out of the wrapper.
    Emergency intents therefore compare with the payload dropped; every other
    intent type compares exact — their payloads (rooms, targets, kinds) ARE
    engine inputs.
    """

    if isinstance(intent, EmergencyMeetingIntent):
        return EmergencyMeetingIntent(actor=intent.actor, type="emergency")
    return intent


def _mask_vent_in_room(public_map: PublicMapView, room: str) -> str | None:
    """The (deterministic, alphabetically-first) vent id sitting in ``room``.

    Ported verbatim from ``training/env.py::_vent_in_room``; renamed to avoid
    confusion with ``ImpostorPolicy._vent_in_room`` (a distinct helper).
    """

    vents = sorted(
        vent_id
        for vent_id, vent_room in public_map.vent_rooms.items()
        if vent_room == room
    )
    return vents[0] if vents else None


def _build_action_mask(
    packet: ObservationPacket,
    public_map: PublicMapView,
    *,
    sabotage_kinds: Sequence[str],
    emergency_uses_remaining: int,
) -> _ActionMask:
    """Mirror the engine legality predicates agent-side into an :class:`_ActionMask`.

    Ported verbatim from ``training/env.py::build_action_mask`` (Task 15.8/15.16).
    Every predicate is a pure boolean of ``(state, map, actor)`` with zero RNG
    (audit §5.1), so the mask mirrors them from the observation packet +
    ``PublicMapView`` + the two policy-side trackers (``sabotage_kinds`` — the
    map's sabotage vocabulary, absent from the packet — and
    ``emergency_uses_remaining`` — the actor's spent-use count, absent from the
    packet). It never imports ``engine/``: the mask is a faithful agent-side
    mirror the fixture pins assert against the real engine mask.
    """

    self_state = packet.self_state
    actor = packet.agent_id
    role = self_state.role
    own_room = self_state.room
    in_vent = self_state.in_vent
    fellows = set(self_state.fellow_impostor_ids)
    cooldown = packet.cooldown
    pending = self_state.pending_task_id
    global_state = packet.global_state
    sabotage_active = global_state.sabotage_active
    sabotage_kind = global_state.sabotage_kind
    repair_rooms = set(global_state.sabotage_repair_rooms)
    neighbors = set(public_map.room_neighbors.get(own_room, ()))

    engine_legal: list[ActionIntent] = []
    submission_only: list[ActionIntent] = []
    illegal: list[ActionIntent] = []

    def add(intent: ActionIntent, *, legal: bool) -> None:
        (engine_legal if legal else illegal).append(intent)

    # WAIT — always legal for a live actor (tick.py:530-536).
    engine_legal.append(WaitIntent(actor=actor, type="wait"))

    # MOVE — not in vent; destination is current room or an adjacent room.
    for room in public_map.room_ids:
        add(
            MoveIntent.model_validate(
                {"type": "move", "actor": actor, "payload": {"to_room": room}}
            ),
            legal=(not in_vent) and (room == own_room or room in neighbors),
        )

    # DO_TASK — the crew's real pending task vs the impostor's pretend camouflage.
    if pending is not None:
        do_task = DoTaskIntent.model_validate(
            {"type": "do_task", "actor": actor, "payload": {"task_id": pending}}
        )
        task_room = public_map.task_locations.get(pending)
        if role == "IMPOSTOR":
            # Pretend do_task: engine-rejected (owns no instance). It is the
            # ``action="task"`` camouflage submission ONLY when the impostor
            # actually stands in the pretend task's room and is not vented —
            # matching the FSM blend (``impostor_policy._idle``) and the
            # believable-camouflage semantics (crew task only in task rooms, so a
            # ``do_task`` elsewhere is a tell, not camouflage; a vented actor is
            # unseen, so nothing renders). Elsewhere it is a plain illegal
            # submission, so a selector cannot spam a stationary fake task to
            # farm the camouflage/cadence channel.
            if (not in_vent) and task_room == own_room:
                submission_only.append(do_task)
            else:
                illegal.append(do_task)
        else:
            add(
                do_task,
                legal=(
                    (not in_vent)
                    and not (sabotage_active and global_state.sabotage_is_gating)
                    and task_room == own_room
                ),
            )

    # KILL — impostor only; co-located non-teammate crew; cooldown 0.
    if role == "IMPOSTOR":
        for view in packet.visible_players:
            add(
                KillIntent.model_validate(
                    {"type": "kill", "actor": actor, "payload": {"target": view.id}}
                ),
                legal=(
                    cooldown == 0 and view.room == own_room and view.id not in fellows
                ),
            )

    # VENT — impostor only; enter = vent in current room; exit = connected vent.
    if role == "IMPOSTOR":
        current_vent = _mask_vent_in_room(public_map, own_room) if in_vent else None
        connected = (
            set(public_map.vent_graph.get(current_vent, ()))
            if current_vent is not None
            else set()
        )
        for vent_id in sorted(public_map.vent_rooms):
            if in_vent:
                legal = current_vent is not None and (
                    vent_id == current_vent or vent_id in connected
                )
            else:
                legal = public_map.vent_rooms[vent_id] == own_room
            add(
                VentIntent.model_validate(
                    {"type": "vent", "actor": actor, "payload": {"vent_id": vent_id}}
                ),
                legal=legal,
            )

    # REPORT — a visible body in the actor's own room.
    for body in packet.visible_bodies:
        add(
            ReportBodyIntent.model_validate(
                {"type": "report", "actor": actor, "payload": {"body_id": body.id}}
            ),
            legal=body.room == own_room,
        )

    # EMERGENCY — not in vent; uses remaining; in the emergency-button room.
    add(
        EmergencyMeetingIntent(actor=actor, type="emergency"),
        legal=(
            (not in_vent)
            and emergency_uses_remaining > 0
            and own_room == public_map.emergency_button_room
        ),
    )

    # SABOTAGE — impostor only; no sabotage already active; kind exists (no
    # location or in-vent requirement).
    if role == "IMPOSTOR":
        for kind in sabotage_kinds:
            add(
                SabotageIntent.model_validate(
                    {"type": "sabotage", "actor": actor, "payload": {"kind": kind}}
                ),
                legal=not sabotage_active,
            )

    # REPAIR_SABOTAGE — role-blind; not in vent; an active sabotage of the SAME
    # kind; in that kind's repair room.
    for kind in sabotage_kinds:
        add(
            RepairSabotageIntent.model_validate(
                {
                    "type": "repair_sabotage",
                    "actor": actor,
                    "payload": {"kind": kind},
                }
            ),
            legal=(
                (not in_vent)
                and sabotage_active
                and sabotage_kind == kind
                and own_room in repair_rooms
            ),
        )

    return _ActionMask(
        engine_legal=tuple(engine_legal),
        submission_only=tuple(submission_only),
        illegal=tuple(illegal),
    )


def owned_task_do_task_is_submission_legal(
    intent: ActionIntent, *, packet: ObservationPacket, public_map: PublicMapView
) -> bool:
    """The wrapper legality mirror for an owned-task ``do_task`` (ported, 15.22).

    Ported verbatim from ``training/crew/scorer.py::_owned_task_do_task_is_submission_legal``
    (public here — the factory's re-validation imports it). The action mask
    (:func:`_build_action_mask`) enumerates ``do_task`` ONLY for the engine-fed
    ``pending_task_id`` — the mask has no owned-task vocabulary — while the engine
    (``engine/tick.py::_apply_do_task``) accepts a ``do_task`` for ANY of the
    actor's owned unfinished tasks when it stands in the task room, is not vented,
    and no gating sabotage is active. The widened basis's ``nearest_task``
    override submits exactly such a task, so the wrapper carries this mirror over
    the widened self channel (the emergency-uses tracker precedent for a
    wrapper-carried legality input the mask cannot see). Mirrors the engine
    predicate over the OBSERVABLE surface: a crewmate actor, the task in its own
    :attr:`observation.packet.SelfView.owned_task_ids`, not vented, no gating
    sabotage, and the task's room equal to the actor's room. Returns ``False``
    for any non-``do_task`` intent, so a genuinely off-vocabulary override still
    fails the mask and raises.
    """

    if not isinstance(intent, DoTaskIntent):
        return False
    self_state = packet.self_state
    global_state = packet.global_state
    task_id = intent.payload.task_id
    return (
        intent.actor == packet.agent_id
        and self_state.role == "CREWMATE"
        and task_id in self_state.owned_task_ids
        and not self_state.in_vent
        and not (global_state.sabotage_active and global_state.sabotage_is_gating)
        and public_map.task_locations.get(task_id) == self_state.room
    )


def override_is_submission_legal(
    intent: ActionIntent,
    *,
    packet: ObservationPacket,
    public_map: PublicMapView,
    sabotage_kinds: tuple[str, ...],
    emergency_uses_remaining: int,
) -> bool:
    """The wrapper's combined re-validation predicate (Task 18.7).

    Mirrors ``_CrewCandidateAgent``'s override validation
    (``training/crew/scorer.py:705-730``): the fail-loud backstop for a drifted
    menu. An OVERRIDING crew intent is submission-legal iff it is in the
    :func:`_build_action_mask` submission set OR it is an owned-task ``do_task``
    the mask cannot see (:func:`owned_task_do_task_is_submission_legal` — the
    mask-invisible ``nearest_task`` do_task the widened basis emits). A genuinely
    off-vocabulary override fails both and the caller raises.
    """

    return _build_action_mask(
        packet,
        public_map,
        sabotage_kinds=sabotage_kinds,
        emergency_uses_remaining=emergency_uses_remaining,
    ).is_submission_legal(intent) or owned_task_do_task_is_submission_legal(
        intent, packet=packet, public_map=public_map
    )


# --------------------------------------------------------------------------- #
# The shipped crew scorer + committed-artifact loader (Task 18.7).             #
# --------------------------------------------------------------------------- #

# The shipped crew surface's encoder tag — the widened owned-task per-option
# featurizer, NOT the shared encoder-v2 memory vector — recorded verbatim in the
# provenance stamp. Matches the committed artifact's ``config.json``.
CREW_ENCODER_VERSION: Final[str] = "crew-option-features-v2"

# Flat genome length: one weight per widened option feature + a trailing bias.
CREW_GENOME_LENGTH: Final[int] = len(OWNED_TASK_OPTION_FEATURE_NAMES) + 1  # 27


class LearnedCrewScorer:
    """The shipped crew forward pass (Task 18.7 public type).

    A pure function of ``(packet, public_map, memory, fsm_intent)`` plus the
    optional wrapper-tracked ``emergency_uses_remaining``: impostor decisions
    delegate to the scripted FSM (the impostor side stays the frozen scripted
    FSM this surface); crew decisions enumerate the widened owned-task menu
    (:func:`enumerate_owned_task_options`), score each option with the linear
    head (``fsum(weights[:-1] · features) + weights[-1]``), and realize the
    argmax (score DESC, canonical intent-key ASC — the repo's lexical tie-break
    idiom). Every tie is lexical and the arithmetic is stdlib ``math`` only, so
    the Q4 bit-exact gate can pin token-identical equality against the
    training-side reference (``training/crew/scorer.py::CrewOptionScorer`` over
    the committed owned-task basis).
    """

    def __init__(self, *, weights: Sequence[float]) -> None:
        if len(weights) != CREW_GENOME_LENGTH:
            raise ValueError(
                f"weights length {len(weights)} != expected {CREW_GENOME_LENGTH}"
            )
        self._weights = tuple(float(weight) for weight in weights)

    @property
    def encoder_version(self) -> str:
        return CREW_ENCODER_VERSION

    @property
    def weights(self) -> tuple[float, ...]:
        return self._weights

    def score(self, option: CrewOption) -> float:
        # VERBATIM port of the reference ``_score``: ``math.fsum`` is correctly
        # rounded, so this is the one expression a naive ``sum()`` or a float32
        # intermediate would silently diverge from in the last ULP.
        head = self._weights[:-1]
        bias = self._weights[-1]
        return (
            math.fsum(
                weight * feature
                for weight, feature in zip(head, option.features, strict=True)
            )
            + bias
        )

    def evaluate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> LearnedDecisionFrame:
        if packet.self_state.role != "CREWMATE":
            return LearnedDecisionFrame(
                agent_id=packet.agent_id,
                tick=packet.tick,
                features=(),
                scores=(),
                intent=fsm_intent,
            )
        options = enumerate_owned_task_options(
            packet,
            public_map,
            memory,
            fsm_intent=fsm_intent,
            emergency_uses_remaining=emergency_uses_remaining,
        )
        scores = [self.score(option) for option in options]
        best_option, _ = min(
            zip(options, scores, strict=True),
            key=lambda pair: (-pair[1], intent_key(pair[0].intent)),
        )
        features = tuple(chain.from_iterable(option.features for option in options))
        return LearnedDecisionFrame(
            agent_id=packet.agent_id,
            tick=packet.tick,
            features=features,
            scores=tuple(scores),
            intent=best_option.intent,
        )


_PACKAGE_DIR: Final[Path] = Path(__file__).resolve().parent

# The committed agents-side crew artifact — the COPY of the frozen training-side
# ``training/artifacts/crew/crew-owned-tasks-es/`` (sha256 ``bd6fdd0a…``),
# float64-hex JSON, pinned by test and never read across the package boundary:
# ``agents/`` reading ``training/`` at inference time would breach the firewall.
CREW_CHAMPION_WEIGHTS_PATH: Final[Path] = _PACKAGE_DIR / "crew_weights.json"
CREW_CHAMPION_WEIGHTS_SIDECAR_PATH: Final[Path] = (
    _PACKAGE_DIR / "crew_weights.json.sha256"
)


def _verified_payload(weights_path: Path, sidecar_path: Path) -> tuple[str, str]:
    """Read the weights payload and its sidecar digest, verifying they agree."""

    raw = weights_path.read_text()
    recorded = sidecar_path.read_text().split()[0]
    actual = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if actual != recorded:
        raise ValueError(
            f"{weights_path} hashes to {actual} but the sidecar records {recorded}"
        )
    return raw, recorded


def committed_crew_weights_sha256() -> str:
    """The committed crew sidecar digest, verified against the weights payload.

    The ``weights_sha256`` stamp field
    (:class:`agents.tactical.learned.factory.LearnedCrewPolicyStamp`) reads THIS
    — never a hard-coded constant — so a crew recording surface cannot mis-stamp:
    the stamped digest is always the digest of the artifact actually loaded.
    """

    _, recorded = _verified_payload(
        CREW_CHAMPION_WEIGHTS_PATH, CREW_CHAMPION_WEIGHTS_SIDECAR_PATH
    )
    return recorded


def load_crew_champion_weights() -> tuple[float, ...]:
    """Reload the committed crew genome, verifying the sha256 sidecar."""

    raw, _ = _verified_payload(
        CREW_CHAMPION_WEIGHTS_PATH, CREW_CHAMPION_WEIGHTS_SIDECAR_PATH
    )
    weights = weights_from_hex_json(raw)
    if len(weights) != CREW_GENOME_LENGTH:
        raise ValueError(
            f"{CREW_CHAMPION_WEIGHTS_PATH} carries {len(weights)} weights; the "
            f"crew-owned-tasks-es genome is {CREW_GENOME_LENGTH}"
        )
    return weights


__all__ = [
    "CREW_CHAMPION_WEIGHTS_PATH",
    "CREW_CHAMPION_WEIGHTS_SIDECAR_PATH",
    "CREW_ENCODER_VERSION",
    "CREW_GENOME_LENGTH",
    "CREW_OPTION_FEATURE_NAMES",
    "CREW_OPTION_KINDS",
    "OWNED_TASK_OPTION_FEATURE_NAMES",
    "OWNED_TASK_OPTION_KINDS",
    "CrewOption",
    "CrewOptionKind",
    "LearnedCrewScorer",
    "committed_crew_weights_sha256",
    "crew_genome_length",
    "enumerate_crew_options",
    "enumerate_owned_task_options",
    "load_crew_champion_weights",
    "override_is_submission_legal",
    "owned_task_do_task_is_submission_legal",
    "owned_task_genome_length",
]
