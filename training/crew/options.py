"""The observable-only crew option set + per-option features (Task 15.16).

The crew twin of the 15.15 utility-scorer menu
(:mod:`training.bakeoff.utility_es`): keep the scripted crew FSM's option
GENERATION verbatim where the FSM has one (report / emergency / repair /
task-continuation / hold — the decide() ladder,
``agents/tactical/crewmate_policy.py:343-423``) and add the two observable-only
options the planning audit names and the FSM lacks
(audits/post-phase-14-ML-planning.md §4.1 "no witness/buddy/safety awareness",
§5.2 the crew option vocabulary): **buddy** toward the nearest visible /
belief-trusted group and **patrol** toward the last-seen suspect. A learned
linear utility (:class:`training.crew.scorer.CrewOptionScorer`) arbitrates the
menu where the ladder used a fixed priority.

Observable-only is the load-bearing doctrine (§5.2): every per-option feature
derives from the observation packet + the crew agent's OWN memory — its
episodic sighting log and its OWN belief suspicion floats, INTEGER-QUANTIZED
through the encoder's grid (:func:`agents.tactical.features.quantize_unit_interval`,
the §6.3 residue-flips-argmax mitigation) — the same information class that
already reaches crew tactics through the emergency gate
(``EmergencyPacingTracker._over_gate`` reads the identical self-held suspicion
against the identical :data:`meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD`).
Roles are hidden: "belief-trusted group" keys on visible co-presence + low
own-suspicion, NEVER role. Task-ordering is structurally out — the packet
carries a single engine-fed ``pending_task_id`` and no owned-task set, so the
menu can only continue the engine-fed task (the surface ask the crew report
states for the pause).

Emergency semantics are preserved, not re-derived: the emergency option exists
only when the crew FSM's OWN tracker-gated decision took the button course this
tick — detected from ``fsm_intent`` plus the FSM's own pure helpers (the
zero-reimplementation-drift idiom of the 15.15 menu), never by re-implementing
:class:`~agents.tactical.crewmate_policy.EmergencyPacingTracker` bookkeeping.
The emitted press carries the FSM's ``reason`` payload verbatim; the 15.16
``build_action_mask`` emergency canonicalization is what makes that payload
submission-legal.

Zero reimplementation drift: the FSM-derived options call
:class:`~agents.tactical.crewmate_policy.CrewmatePolicy`'s own helpers
(``_first_visible_body`` / ``_kill_witnessed`` / ``_active_gating_sabotage`` /
``_walk_to_button`` / ``_walk_to_repair`` / ``_return_to_hub`` /
``_move_toward`` / ``_do_task`` / ``_report``) and the module-level
``_seen_victim_ids``; the last-seen scan is the encoder's own
(``agents.tactical.features._episodic_last_seen``). What the FSM computes with
a short-circuiting priority ladder, the scorer computes with a learned linear
head over these option features and a single argmax.

Task 15.22 widens the option basis (audits/audit-phase-15-pause.md decision 5,
the four-item review's item 4 — the encoder note): :class:`OwnedTaskOptionBasis`
is a WRAPPER around :func:`enumerate_crew_options` (the legacy function stays
byte-identical — every 15.16 pin holds) that re-bases each option onto the
widened :data:`OWNED_TASK_OPTION_FEATURE_NAMES` alphabet (a ``nearest_task``
one-hot + four owned-task scalars over the new
:attr:`observation.packet.SelfView.owned_task_ids` self channel) and appends the
``nearest_task`` option — nearest-of-N owned-task selection + same-room batching,
the crew report §7 ask. The basis's version string bumps to
``crew-option-features-v2`` (:data:`training.crew.scorer.OWNED_TASK_ENCODER_VERSION`);
the PRODUCTION encoder (``agents/tactical/features.py``) is NOT touched. The
FO-8-style interrupt-preserving constraint the pause scoped is STRUCTURAL: when a
body is visible the widened menu carries ONLY ``report`` — the learned head is
removed from the ``report`` selectable set rather than penalized for suppressing
it (structural unreachability, not a reward term — the Goodhart lesson), so the
15.16 win-by-meeting-starvation failure mode is unreachable.

No ``eval.*`` import may appear here (the 15.15 firewall-test pattern —
``tests/training/test_crew_scorer.py`` AST-scans this module): the crew eval
twin in :mod:`training.crew.scorer` computes every reported metric.
"""

from __future__ import annotations

from dataclasses import dataclass
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
)
from agents.tactical.pathing import find_path
from meetings.constants import DEFAULT_SKIP_CONFIDENCE_THRESHOLD
from observation.action_intent import (
    ActionIntent,
    DoTaskIntent,
    EmergencyMeetingIntent,
    MoveIntent,
    WaitIntent,
)
from observation.packet import ObservationPacket
from observation.public_map import PublicMapView

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
    # basis :class:`OwnedTaskOptionBasis` re-bases onto.
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
    """One crew option the learned utility ranks (Task 15.16 public type).

    ``kind`` is the menu slot (a :data:`CREW_OPTION_KINDS` member), ``intent``
    the concrete submission-legal
    :class:`~observation.action_intent.ActionIntent` realizing it this tick,
    ``target_id`` the option's target — the patrol suspect's player id, the
    buddy option's goal room id — or ``None``, and ``features`` the fixed-order
    :data:`CREW_OPTION_FEATURE_NAMES` vector the scorer dots its weights
    against. Signature is stable per the task contract.
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

    Mirrors the crew decide() ladder's structure
    (``agents/tactical/crewmate_policy.py:343-423``) but keeps EVERY option the
    state admits instead of short-circuiting on the ladder's fixed priority, so
    the learned utility (:class:`training.crew.scorer.CrewOptionScorer`) does
    the arbitration the ladder hard-coded. Self facts come from the PACKET (the
    observable self surface): ``room`` / ``in_vent`` / ``pending_task_id``.
    Body / witnessed-kill / gating-sabotage facts come from the FSM's own pure
    helpers over the agent's live episodic events, so the FSM-derived options
    are byte-faithful to the scripted ladder with zero reimplementation drift.

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
      tracked (the eval wrapper) a PRESS is skipped at zero remaining uses —
      the mask's emergency legality mirror — while ``None`` (an untracked
      caller, e.g. the 15.10 determinism harness's fixed ``FramePolicy``
      surface) keys the press on the FSM's own proposal alone.
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


@dataclass(frozen=True)
class OwnedTaskOptionBasis:
    """The Task 15.22 widened option basis over ``SelfView.owned_task_ids``.

    A stateless, stable-signature PUBLIC TYPE (downstream tasks import it) that
    WRAPS :func:`enumerate_crew_options` (the pinned 15.16 menu stays
    byte-identical — this never forks its logic) and re-bases its options onto
    the widened :data:`OWNED_TASK_OPTION_FEATURE_NAMES` alphabet: the eight kind
    one-hots, the fourteen legacy scalars carried VERBATIM, and the four
    owned-task scalars derived from the recipient's own unfinished map task ids
    (:attr:`observation.packet.SelfView.owned_task_ids`, the decision-5 self
    channel). It then appends the ``nearest_task`` option — nearest-of-N owned
    selection + same-room batching, the crew report §7 ask the closed
    ``pending_task_id``-only surface hides.

    The interrupt-preserving constraint is STRUCTURAL (audit decision 5, the
    FO-8-style guard): a visible body routes to ``report`` and ONLY ``report``
    — the widened menu drops every other option, so the learned head is REMOVED
    from the ``report`` selectable set rather than penalized for suppressing it
    (structural unreachability, not a reward term — the 15.16 Goodhart lesson).
    The 15.16 win-by-meeting-starvation failure mode is consequently
    unreachable.
    """

    @property
    def kinds(self) -> tuple[CrewOptionKind, ...]:
        """The widened option alphabet (the 15.16 prefix + ``nearest_task``)."""

        return OWNED_TASK_OPTION_KINDS

    @property
    def feature_names(self) -> tuple[str, ...]:
        """The widened per-option feature-name vector (26 names)."""

        return OWNED_TASK_OPTION_FEATURE_NAMES

    def genome_length(self) -> int:
        """The widened flat genome length (feature count + bias = 27)."""

        return owned_task_genome_length()

    def enumerate(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
        memory: AgentMemory,
        *,
        fsm_intent: ActionIntent,
        emergency_uses_remaining: int | None = None,
    ) -> tuple[CrewOption, ...]:
        """Re-base the legacy menu onto the widened basis + append nearest_task.

        Inherits every raise semantic of :func:`enumerate_crew_options` (empty
        memory / non-crew / vented) by delegating to it FIRST. When a body is
        visible the legacy menu carries a ``report`` option; the constraint
        returns a 1-tuple of ONLY the re-based report (intent/target verbatim)
        — the structural interrupt. Otherwise every legacy option is widened
        (its one-hot re-based to the widened alphabet — the 15.16 kinds are a
        prefix, so a kept option's index is unchanged — its fourteen legacy
        scalars carried verbatim, and the four owned-task scalars appended) and
        a ``nearest_task`` option is appended when the nearest routable owned
        task is not the engine-fed ``pending_task_id``.
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
                1.0 if kind == candidate else 0.0
                for candidate in OWNED_TASK_OPTION_KINDS
            )

        def widen(option: CrewOption, *, goal_room: str | None) -> CrewOption:
            legacy_scalars = option.features[len(CREW_OPTION_KINDS) :]
            return CrewOption(
                kind=option.kind,
                intent=option.intent,
                target_id=option.target_id,
                features=one_hots(option.kind)
                + legacy_scalars
                + owned_block(goal_room),
            )

        # continue_task's goal room recomputed EXACTLY as the legacy function:
        # the pending task's room, or the meeting room when there is none.
        task_room = (
            public_map.task_locations.get(pending_task_id)
            if pending_task_id is not None
            else None
        )
        continue_goal_room = (
            task_room if task_room is not None else public_map.meeting_room
        )

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
                goal_room=(
                    continue_goal_room if option.kind == "continue_task" else None
                ),
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


__all__ = [
    "CREW_OPTION_FEATURE_NAMES",
    "CREW_OPTION_KINDS",
    "OWNED_TASK_OPTION_FEATURE_NAMES",
    "OWNED_TASK_OPTION_KINDS",
    "CrewOption",
    "CrewOptionKind",
    "OwnedTaskOptionBasis",
    "crew_genome_length",
    "enumerate_crew_options",
    "owned_task_genome_length",
]
