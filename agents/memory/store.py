"""Composite memory surface and prompt rendering (DESIGN.md §6.1, §6.6).

Aggregates the three stores introduced in Task 2.3 (`agents/memory/episodic.py`,
`agents/memory/working.py`, `agents/memory/beliefs.py`) into a single
:class:`AgentMemory` surface. ``render_for_prompt`` reads from all three
components to produce the token-budgeted Markdown view per DESIGN.md §6.6.

This composite is the integration point Phase 3 strategic agents import
through (audit R-6, `audits/audit-2026-05-15-0225-reconciled.md`).
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Final, TypeAlias

from agents.memory.beliefs import (
    BODY_PROXIMITY_WINDOW_TICKS,
    AlibiClaim,
    BeliefState,
    ContradictionRef,
    PlayerBelief,
    apply_meeting_evidence_rules,
)
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.working import LastSeen, WorkingMemory

PlayerId: TypeAlias = str
RoomId: TypeAlias = str
TaskId: TypeAlias = str

DEFAULT_TOKEN_BUDGET: Final[int] = 1500

# 4 chars/token is the widely-cited heuristic for English BPE
# tokenizers. The renderer does not depend on a provider tokenizer:
# the budget arithmetic must be deterministic across providers so
# golden tests pin behavior, not the provider's tokenizer choice.
_CHARS_PER_TOKEN: Final[int] = 4

# Salience weights per renderable event type. Higher = more salient
# (more likely to survive a tight token budget). Matches the priority
# in DESIGN.md §6.2: body discoveries, kills, vent observations,
# sightings, task completions, routine status.
_SALIENCE_FOUND_BODY: Final[int] = 100
# The recipient's OWN kill (Task 11.3, DESIGN.md §6.2): legibility-only -- it
# states the act the impostor committed, which is otherwise invisible to its own
# memory (the engine excludes a killer from its own kill's witnesses). Ranked
# above the witnessed-kill line per the task contract.
_SALIENCE_OWN_KILL: Final[int] = 96
_SALIENCE_KILL_WITNESSED: Final[int] = 95
_SALIENCE_VENT_WITNESSED: Final[int] = 85
_SALIENCE_VENT_HEARD: Final[int] = 75
_SALIENCE_SABOTAGE_HEARD: Final[int] = 65
_SALIENCE_SAW_PLAYER_ACTIVE: Final[int] = 55
_SALIENCE_SAW_PLAYER: Final[int] = 50
# A within-vision entry/exit (Task 13.9), derived from consecutive own-room
# ``saw_player`` deltas. Ranked just below a direct sighting: it is valuable
# trajectory testimony but secondary to the sighting it is reconstructed from,
# so a tight budget keeps the primary sightings and sheds transitions first.
_SALIENCE_TRANSITION: Final[int] = 48
_SALIENCE_COMPLETED_TASK: Final[int] = 30
_SALIENCE_COOLDOWN_STATUS: Final[int] = 10

_EVENT_SAW_BODY: Final[str] = "saw_body"
_EVENT_SAW_PLAYER: Final[str] = "saw_player"
_EVENT_HEARD_VENT_USE: Final[str] = "heard_vent_use"
_EVENT_HEARD_SABOTAGE_ALARM: Final[str] = "heard_sabotage_alarm"
_EVENT_SELF_STATE: Final[str] = "self_state"
_EVENT_OWN_KILL: Final[str] = "own_kill"
_EVENT_GLOBAL_STATUS: Final[str] = "global_status"
_EVENT_COOLDOWN_STATUS: Final[str] = "cooldown_status"

_ACTIVE_PLAYER_ACTIONS: Final[frozenset[str]] = frozenset({"report", "task"})


@dataclass
class AgentMemory:
    """Composite memory surface for a single agent (DESIGN.md §6.1).

    Aggregates references to the three Task-2.3 stores. The composite
    does not copy state: callers mutate the underlying stores directly
    and the composite reflects every change. ``render_for_prompt``
    reads from all three components (R-6 acceptance gate).
    """

    episodic: MemoryStore = field(default_factory=MemoryStore)
    working: WorkingMemory = field(default_factory=WorkingMemory)
    beliefs: BeliefState = field(default_factory=BeliefState)


@dataclass(frozen=True)
class _Observation:
    """One renderable observation line with the data needed to sort and budget it."""

    salience: int
    tick: int
    line: str


@dataclass(frozen=True)
class _Breadcrumb:
    """A subject's most-recent room change, for the directional sighting render.

    Task 13.6 (report-phase-b-plan "Prompts"): the directional breadcrumb. For a
    subject the agent saw move between rooms, the most-recent ``saw_player`` line
    gains a "moved from A, last seen there at tick t" suffix, surfacing the
    subject's PATH so the model states it as the concrete who/where/when testimony
    the inferential detector mines (the 13.4 GATE FINDING: the committed transcripts
    are too thin to reconstruct physical alibis from).
    """

    subject_tick: int  # tick of the subject's most-recent rendered sighting
    prior_room: str
    prior_tick: int
    current_room: str


def render_for_prompt(
    memory: AgentMemory,
    *,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> str:
    """Produce a token-budgeted Markdown view of agent memory (DESIGN.md §6.6).

    Reads from every component in ``memory``:

    * episodic → role line, tasks-completed line, observation lines.
    * beliefs  → ``Your current beliefs`` and ``Open contradictions``.
    * working  → last-seen suffixes on belief lines.

    Salience ordering is deterministic: events are sorted by salience
    descending, tick descending, then line text ascending for stable
    tie-breaks. Events past ``token_budget`` are dropped by lowest
    salience first; the role line, tasks-completed line, beliefs, and
    contradictions are always retained because they are agent-essential
    context that the LLM cannot work around.

    Raises :class:`ValueError` if ``token_budget`` is non-positive or
    if no ``self_state`` event has been recorded. A render call before
    perception has run is a wiring bug, not a normal state, so we
    fail loud (AGENTS.md "no silent fallbacks").
    """

    if token_budget <= 0:
        raise ValueError(f"token_budget must be positive, got {token_budget}")

    role = _latest_role(memory.episodic)
    if role is None:
        raise ValueError(
            "cannot render memory: no self_state event has been recorded; "
            "perception must run at least once before rendering."
        )

    tasks_summary = _latest_tasks_summary(memory.episodic)
    # Team-internal firewall self-channel (Task 9.3, DESIGN.md §4.7). The
    # recipient's own id drives self-subject suppression for EVERY role; the
    # fellow-impostor set drives teammate kill-window suppression and is
    # role-gated to IMPOSTOR so a non-impostor render never fires the teammate
    # guard (the reasoner leak-guard role-gating precedent). Both are read
    # defensively, so an older self_state payload without them renders
    # byte-identically.
    own_agent_id, fellow_impostor_ids = _latest_self_guard_fields(memory.episodic)
    teammate_ids = fellow_impostor_ids if role == "IMPOSTOR" else frozenset()
    observations = sorted(
        _build_observations(
            memory.episodic,
            own_agent_id=own_agent_id,
            teammate_ids=teammate_ids,
        ),
        key=lambda obs: (-obs.salience, -obs.tick, obs.line),
    )
    # §6.6 roster filter (Task 10.2, audit gp-6 C-C-8): belief rows AND
    # open-contradiction lines render only for engine-witnessed player
    # ids, so a garbage subject that somehow reached the store (the
    # seed-12 m2 turn-id-as-player rows) cannot render into any prompt
    # through either section. Gated on the same 9.3 self channel as the
    # guards above: with no recorded ``agent_id`` (pre-9.3 fixtures) the
    # roster is underivable and the render is byte-identical to today --
    # production perception has recorded the id on every tick since
    # Task 9.3.
    roster = _known_roster_ids(memory.episodic) if own_agent_id is not None else None
    beliefs_lines = _build_belief_lines(memory.beliefs, memory.working, roster=roster)
    contradiction_lines = _build_contradiction_lines(memory.beliefs, roster=roster)

    return _assemble_view(
        role=role,
        tasks_summary=tasks_summary,
        observations=observations,
        beliefs_lines=beliefs_lines,
        contradiction_lines=contradiction_lines,
        token_budget=token_budget,
    )


def absorb_meeting_evidence(
    memory: AgentMemory,
    *,
    accused: Sequence[PlayerId],
    corroborated: Sequence[PlayerId] = (),
    contradicted: Sequence[PlayerId] = (),
) -> None:
    """Fold one meeting's public evidence into ``memory.beliefs`` (Task 9.8).

    The composite-store half of the persistent post-meeting belief path:
    the orchestrator extracts the meeting's deduplicated subject sets
    (``meetings.manager.extract_belief_evidence``) and calls this once per
    living agent after the meeting result is applied. The belief update
    itself is the pure :func:`agents.memory.beliefs.apply_meeting_evidence_rules`;
    this wrapper adopts the result in place (the ``load_from`` pattern
    perception uses), so the accusation bump, Rule 3 corroboration, and
    Rule 5 decay land on the SAME :class:`BeliefState` the next meeting's
    suspicion graph and rendered memory are built from -- which is what
    makes suspicion carry forward across meetings instead of being
    rebuilt and thrown away at vote time.

    The recipient's own id and teammate set come from the latest
    ``self_state`` episodic event -- the identical privileged self channel
    the Task 9.3 render guard reads (:func:`_latest_self_guard_fields`),
    role-gated to IMPOSTOR so a crewmate never carries a teammate guard.
    An impostor therefore accrues NO accusation bump against a fellow
    impostor (DESIGN.md §4.7, the 7.12/9.3 firewall), with zero new
    orchestrator-supplied channel.

    Roster filter (Task 10.2; audit gp-6 C-C-8, H-H-6). The fold is
    filtered to the agent's engine-witnessed player-id set
    (:func:`_known_roster_ids`, derived from the same episodic store), so
    a hallucinated structural id in the evidence -- a game id, a turn id,
    a free-text phrase -- never materialises a persistent belief row and
    therefore never renders into the §6.6 view or the next meeting's
    suspicion graph (the seed-12 m2 garbage-row shape). The fold also
    PURGES any pre-existing non-roster row from the store
    (:meth:`~agents.memory.beliefs.BeliefState.drop_player`), so even a
    store polluted by a hypothetical write path the filters do not cover
    self-heals at its first post-meeting fold -- every downstream
    snapshot, including the vote prompt's suspicion graph
    (``orchestrator.game.TacticalAgent.suspicion_graph_for_meeting``),
    carries roster ids only. Players co-spawn, so the set covers the
    full roster from the first perception tick and both filters are
    no-ops on real-player data. This is the defense-in-depth backstop
    behind the Task 10.2 meeting-layer chokepoint, which already drops
    garbage-subject claims before they are recorded.

    Raises :class:`ValueError` when no ``self_state`` event carrying the
    agent's own id has been recorded: the self-subject guard cannot run
    without it, and a meeting before perception is a wiring bug, not a
    normal state (AGENTS.md "no silent fallbacks"; production perception
    has recorded ``agent_id`` on every tick since Task 9.3).
    """

    role = _latest_role(memory.episodic)
    own_agent_id, fellow_impostor_ids = _latest_self_guard_fields(memory.episodic)
    if role is None or own_agent_id is None:
        raise ValueError(
            "cannot absorb meeting evidence: no self_state event carrying "
            "'agent_id' has been recorded; perception must run at least once "
            "before a meeting's beliefs are folded."
        )
    teammate_ids = fellow_impostor_ids if role == "IMPOSTOR" else frozenset()
    memory.beliefs.load_from(
        apply_meeting_evidence_rules(
            memory.beliefs,
            own_id=own_agent_id,
            accused=accused,
            corroborated=corroborated,
            contradicted=contradicted,
            fellow_impostor_ids=tuple(sorted(teammate_ids)),
            roster=_known_roster_ids(memory.episodic),
        )
    )


def _estimate_tokens(text: str) -> int:
    """Approximate BPE token count from character length.

    Uses ceiling division so the estimate never undercounts the true
    token cost of a string. The contract for ``render_for_prompt`` is
    "actual rendered token count <= token_budget"; floor division
    would let a 5-char string score as 1 token even though most BPE
    tokenizers split it into 2, and the rendered view could quietly
    overrun the budget. Ceiling is conservative — we may pack one
    fewer observation than strictly necessary, but we never overshoot.
    The 4 chars/token ratio is the standard heuristic for English text
    in BPE-style tokenizers.
    """

    if not text:
        return 0
    return (len(text) + _CHARS_PER_TOKEN - 1) // _CHARS_PER_TOKEN


def _latest_role(episodic: MemoryStore) -> str | None:
    role: str | None = None
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SELF_STATE:
            continue
        value = event.payload.get("role")
        if isinstance(value, str):
            role = value
    return role


def _latest_self_guard_fields(
    episodic: MemoryStore,
) -> tuple[str | None, frozenset[str]]:
    """Self-channel inputs for the Task 9.3 firewall (DESIGN.md §4.7).

    Returns the recipient's own ``agent_id`` (or ``None`` when no
    ``self_state`` event carries it -- hand-built fixtures predating Task
    9.3) and the set of ``fellow_impostor_ids``. Role / team are stable for
    the life of a game, so the latest ``self_state`` is authoritative; both
    keys are read with ``.get`` so a payload missing them yields
    ``(None, frozenset())`` and the render is byte-identical (crew / older
    fixtures never drop a row).
    """

    agent_id: str | None = None
    teammates: frozenset[str] = frozenset()
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SELF_STATE:
            continue
        own = event.payload.get("agent_id")
        if isinstance(own, str):
            agent_id = own
        fellows = event.payload.get("fellow_impostor_ids")
        if isinstance(fellows, (tuple, list)):
            teammates = frozenset(str(player_id) for player_id in fellows)
    return agent_id, teammates


def _known_roster_ids(episodic: MemoryStore) -> frozenset[str]:
    """Player ids the agent witnessed through the observation firewall.

    The agent-side notion of "known roster ids" (Task 10.2; audit gp-6
    C-C-8): every id below entered the episodic store from an
    engine-derived :class:`~observation.packet.ObservationPacket` field
    (``agents.perception.ingest_packet``), so the set can contain real
    players only -- an LLM-hallucinated structural id (a game id, a turn
    id, a free-text phrase) has no path into it. Sources:

    * ``self_state`` -- the recipient's own ``agent_id`` plus the
      privileged ``fellow_impostor_ids`` self channel;
    * ``saw_player`` -- every first-hand sighting's ``player_id``;
    * ``saw_body`` -- every discovered body's ``victim_id``.

    Players co-spawn in one room (``orchestrator.seeder``), so in
    production the set covers the full game roster -- living AND dead --
    from the first perception tick; dead players stay in it, matching
    "roster id" (liveness is the meeting chokepoint's rule, not this
    set's). Used by :func:`absorb_meeting_evidence` to filter the
    post-meeting fold and by :func:`render_for_prompt` to filter the
    §6.6 belief rows, so garbage subjects neither materialise belief
    rows nor render into any prompt surface. Payload fields are read
    defensively (the :func:`_latest_self_guard_fields` convention), so a
    hand-built fixture event missing a field contributes nothing rather
    than failing.
    """

    ids: set[str] = set()
    for event in episodic.recent(since_tick=0):
        if event.type == _EVENT_SELF_STATE:
            own = event.payload.get("agent_id")
            if isinstance(own, str):
                ids.add(own)
            fellows = event.payload.get("fellow_impostor_ids")
            if isinstance(fellows, (tuple, list)):
                ids.update(str(player_id) for player_id in fellows)
        elif event.type == _EVENT_SAW_PLAYER:
            player_id = event.payload.get("player_id")
            if isinstance(player_id, str):
                ids.add(player_id)
        elif event.type == _EVENT_SAW_BODY:
            victim_id = event.payload.get("victim_id")
            if isinstance(victim_id, str):
                ids.add(victim_id)
    return frozenset(ids)


def _collect_body_sightings(episodic: MemoryStore) -> tuple[tuple[str, int], ...]:
    """Every ``(room, tick)`` the agent recorded a body, for the §4.7 guard.

    The teammate kill-window check (:func:`_is_kill_window_sighting`) mirrors
    DESIGN.md §6.3 Rule 1's body-proximity window: a teammate ``saw_player``
    row counts as "at a kill room/tick" when the agent also saw a body in the
    same room within ``BODY_PROXIMITY_WINDOW_TICKS`` ticks at or after the
    sighting. The set is needed up front because the body discovery can be
    appended after the sighting it incriminates.
    """

    sightings: list[tuple[str, int]] = []
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SAW_BODY:
            continue
        room = event.payload.get("room")
        if isinstance(room, str):
            sightings.append((room, event.tick))
    return tuple(sightings)


def _collect_own_kill_victims(episodic: MemoryStore) -> frozenset[str]:
    """Victim ids the recipient itself killed (Task 11.3, DESIGN.md §6.2).

    Collected up front -- like ``_collect_body_sightings`` -- because the
    self-victim ``saw_body`` row (the body the killer made, surfaced through the
    ordinary sighting channel) can be appended after the ``own_kill`` event for
    the same tick, and the renderer must suppress that "discovered body" line for
    the killer's own victim regardless of append order so the kill is narrated
    once, as a kill, not as a discovery.
    """

    victims: set[str] = set()
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_OWN_KILL:
            continue
        victim_id = event.payload.get("victim_id")
        if isinstance(victim_id, str):
            victims.add(victim_id)
    return frozenset(victims)


def _collect_movement_breadcrumbs(
    episodic: MemoryStore,
    *,
    own_agent_id: str | None,
    teammate_ids: frozenset[str],
    body_sightings: tuple[tuple[str, int], ...],
) -> dict[str, _Breadcrumb]:
    """Each subject's most-recent room change, from the agent's own sightings (Task 13.6).

    A pure read of the existing ``saw_player`` episodic deltas -- NO packet field,
    firewall untouched (the leak test scans packets, not this derived line). For a
    subject the agent saw in two DIFFERENT rooms, the most-recent ordinary sighting
    gets a directional "moved from A" suffix (:func:`_movement_suffix_for`), so the
    rendered memory surfaces the subject's PATH and the model can state it as the
    who/where/when testimony the inferential detector reconstructs from.

    Only ordinary sightings feed the path (``vent`` / ``kill`` are witnessed events
    rendered as their own high-salience lines, never suffixed), and the SAME §4.7
    suppressions the renderer applies are mirrored here (self-subject, teammate
    kill-window), so a suppressed sighting never contributes a breadcrumb. A subject
    seen in only one room (or once) yields no breadcrumb, so a render whose subjects
    never move is byte-identical to the pre-13.6 output.
    """

    paths: dict[str, list[tuple[int, str]]] = {}
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SAW_PLAYER:
            continue
        player_id = event.payload.get("player_id")
        room = event.payload.get("room")
        if not isinstance(player_id, str) or not isinstance(room, str):
            continue
        action = event.payload.get("action")
        action_str = action if isinstance(action, str) else None
        if action_str in ("vent", "kill"):
            continue
        if _sighting_is_suppressed(
            player_id=player_id,
            room=room,
            tick=event.tick,
            action=action_str,
            own_agent_id=own_agent_id,
            teammate_ids=teammate_ids,
            body_sightings=body_sightings,
        ):
            continue
        paths.setdefault(player_id, []).append((event.tick, room))

    breadcrumbs: dict[str, _Breadcrumb] = {}
    for subject, sightings in paths.items():
        # Stable sort by tick keeps recorded order for same-tick ties, so the
        # most-recent sighting and its prior different-room sighting are
        # replay-deterministic.
        ordered = sorted(sightings, key=lambda tr: tr[0])
        last_tick, last_room = ordered[-1]
        prior: tuple[int, str] | None = None
        for tick, room in reversed(ordered[:-1]):
            if room != last_room:
                prior = (tick, room)
                break
        if prior is not None:
            breadcrumbs[subject] = _Breadcrumb(
                subject_tick=last_tick,
                prior_room=prior[1],
                prior_tick=prior[0],
                current_room=last_room,
            )
    return breadcrumbs


def _movement_suffix_for(
    breadcrumbs: dict[str, _Breadcrumb] | None,
    *,
    player_id: str,
    tick: int,
    room: str,
) -> str:
    """The directional breadcrumb suffix for one ``saw_player`` line (Task 13.6).

    Empty unless this line IS the subject's most-recent ordinary sighting
    (``subject_tick`` + ``current_room`` match), so exactly one line per moving
    subject is suffixed and a non-moving subject's render is byte-unchanged.
    """

    if breadcrumbs is None:
        return ""
    breadcrumb = breadcrumbs.get(player_id)
    if (
        breadcrumb is None
        or breadcrumb.subject_tick != tick
        or breadcrumb.current_room != room
    ):
        return ""
    return (
        f" (moved from {breadcrumb.prior_room}, "
        f"last seen there at tick {breadcrumb.prior_tick})"
    )


def _is_kill_window_sighting(
    *,
    room: str,
    tick: int,
    action: str | None,
    body_sightings: tuple[tuple[str, int], ...],
) -> bool:
    """Whether a ``saw_player`` row places its subject at a kill room/tick.

    Two ways a sighting is kill-window incriminating (DESIGN.md §4.7):

    * ``action == "kill"`` -- the agent directly witnessed the subject
      killing (ObservationService stamps the killer's ``PlayerView.action``
      ``"kill"`` for witnesses).
    * the agent saw a body in the same ``room`` within
      ``BODY_PROXIMITY_WINDOW_TICKS`` ticks at or after the sighting -- the
      subject was at the scene shortly before the body surfaced there
      (mirrors the §6.3 Rule 1 proximity window the perception guard uses).
    """

    if action == "kill":
        return True
    return any(
        body_room == room and 0 <= body_tick - tick <= BODY_PROXIMITY_WINDOW_TICKS
        for body_room, body_tick in body_sightings
    )


def _sighting_is_suppressed(
    *,
    player_id: str,
    room: str,
    tick: int,
    action: str | None,
    own_agent_id: str | None,
    teammate_ids: frozenset[str],
    body_sightings: tuple[tuple[str, int], ...],
) -> bool:
    """Whether a ``saw_player`` row is dropped by the §4.7 team-internal firewall.

    The single source of truth for the two suppressions the renderer applies to
    every sighting-derived line (Task 9.3, DESIGN.md §4.7):

    * a self-subject sighting (the recipient's own id) -- it would render as
      third-person "You saw {self}" garble; dropped for EVERY role.
    * an impostor's sighting of a fellow impostor at a kill room/tick -- dropping
      it from the impostor's own meeting input stops the own-goal where it
      publicly places a teammate at the scene (audit gp-7 seed 47).
      ``teammate_ids`` is empty for crew / a sole impostor (and role-gated to
      IMPOSTOR by the caller), so the crew path never drops a row.

    Shared by ``_render_saw_player`` (the sighting line), ``_collect_co_presence``
    (the "with …" companions), and ``_collect_transitions`` (the entered/left
    deltas) so a suppressed subject never re-surfaces through co-presence or a
    transition -- the firewall holds across all three Task 13.9 surfaces.
    """

    if own_agent_id is not None and player_id == own_agent_id:
        return True
    return player_id in teammate_ids and _is_kill_window_sighting(
        room=room,
        tick=tick,
        action=action,
        body_sightings=body_sightings,
    )


def _collect_co_presence(
    episodic: MemoryStore,
    *,
    own_agent_id: str | None,
    teammate_ids: frozenset[str],
    body_sightings: tuple[tuple[str, int], ...],
) -> dict[tuple[int, str], frozenset[str]]:
    """Who the observer saw TOGETHER, keyed by ``(tick, room)`` (Task 13.9).

    A pure read of the existing ``saw_player`` episodic log: every non-suppressed
    subject the observer saw in one room on one tick is co-present with the
    others there. ``_render_saw_player`` turns this into the "(with …)" suffix so
    the model states reliable co-presence, which feeds ``reconstruct_stated_paths``
    -- the two-source material the inferential ``alibi_vs_physical`` detector
    needs (the Wave-C smoke finding: room-only crew starved it of co-located
    witnesses). NO packet field -- the firewall is untouched (the leak test scans
    packets, not this derived render).

    The §4.7 suppressions (:func:`_sighting_is_suppressed`) are mirrored here so a
    self-subject or a teammate-at-a-kill-window never appears as a companion --
    co-presence cannot re-introduce the own-goal the sighting line itself drops.
    """

    groups: dict[tuple[int, str], set[str]] = {}
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SAW_PLAYER:
            continue
        player_id = event.payload.get("player_id")
        room = event.payload.get("room")
        if not isinstance(player_id, str) or not isinstance(room, str):
            continue
        action = event.payload.get("action")
        action_str = action if isinstance(action, str) else None
        if _sighting_is_suppressed(
            player_id=player_id,
            room=room,
            tick=event.tick,
            action=action_str,
            own_agent_id=own_agent_id,
            teammate_ids=teammate_ids,
            body_sightings=body_sightings,
        ):
            continue
        groups.setdefault((event.tick, room), set()).add(player_id)
    return {key: frozenset(members) for key, members in groups.items()}


def _co_presence_suffix(
    co_presence: dict[tuple[int, str], frozenset[str]] | None,
    *,
    player_id: str,
    tick: int,
    room: str,
) -> str:
    """The "(with …)" companion suffix for one ``saw_player`` line (Task 13.9).

    Empty unless the observer saw at least one OTHER (non-suppressed) subject in
    the same room on the same tick, so a solitary sighting renders byte-identically
    to the pre-13.9 output. Companions are sorted for replay determinism.
    """

    if co_presence is None:
        return ""
    companions = co_presence.get((tick, room), frozenset()) - {player_id}
    if not companions:
        return ""
    return " (with " + ", ".join(sorted(companions)) + ")"


def _collect_transitions(
    episodic: MemoryStore,
    *,
    own_agent_id: str | None,
    teammate_ids: frozenset[str],
    body_sightings: tuple[tuple[str, int], ...],
) -> list[_Observation]:
    """Within-vision entry/exit lines at the observer's OWN rooms (Task 13.9).

    A pure read of consecutive own-room ``saw_player`` deltas: a subject ABSENT at
    tick N but PRESENT at N+1 ⇒ "entered"; PRESENT at N but ABSENT at N+1 ⇒ "left"
    (DESIGN.md §1.3; the Wave-C smoke finding). Emitted ONLY across a tick pair the
    observer spent STATIONARY in one room (same own room at N and N+1, ticks
    adjacent): if the observer moved -- or a meeting opened a tick gap -- the field
    of view changed, so a delta cannot be attributed to the SUBJECT moving and is
    skipped. The observer never sees the adjacent origin/destination (room-only),
    so the full X→Y trajectory emerges COLLECTIVELY when meeting testimony is
    combined -- complementing the 13.6 own-sightings breadcrumb.

    Own-room scoping uses the observer's ``self_state`` room per tick; only
    sightings in that room count, so an impostor's adjacent-room sightings (which
    the observer cannot vouch a transition for) are excluded. The §4.7
    suppressions are mirrored so a suppressed subject never produces a transition.
    """

    own_room_by_tick: dict[int, str] = {}
    seen_in_own_room: dict[int, set[str]] = {}
    for event in episodic.recent(since_tick=0):
        if event.type == _EVENT_SELF_STATE:
            room = event.payload.get("room")
            if isinstance(room, str):
                own_room_by_tick[event.tick] = room

    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SAW_PLAYER:
            continue
        player_id = event.payload.get("player_id")
        room = event.payload.get("room")
        if not isinstance(player_id, str) or not isinstance(room, str):
            continue
        if own_room_by_tick.get(event.tick) != room:
            continue
        action = event.payload.get("action")
        action_str = action if isinstance(action, str) else None
        if _sighting_is_suppressed(
            player_id=player_id,
            room=room,
            tick=event.tick,
            action=action_str,
            own_agent_id=own_agent_id,
            teammate_ids=teammate_ids,
            body_sightings=body_sightings,
        ):
            continue
        seen_in_own_room.setdefault(event.tick, set()).add(player_id)

    transitions: list[_Observation] = []
    observed_ticks = sorted(own_room_by_tick)
    for prev_tick, tick in zip(observed_ticks, observed_ticks[1:]):
        if tick - prev_tick != 1:
            continue
        room = own_room_by_tick[tick]
        if own_room_by_tick.get(prev_tick) != room:
            continue
        prev_seen = seen_in_own_room.get(prev_tick, set())
        now_seen = seen_in_own_room.get(tick, set())
        for subject in sorted(now_seen - prev_seen):
            transitions.append(
                _Observation(
                    salience=_SALIENCE_TRANSITION,
                    tick=tick,
                    line=f"[tick {tick}] {subject} entered {room}.",
                )
            )
        for subject in sorted(prev_seen - now_seen):
            transitions.append(
                _Observation(
                    salience=_SALIENCE_TRANSITION,
                    tick=tick,
                    line=f"[tick {tick}] {subject} left {room}.",
                )
            )
    return transitions


def _latest_tasks_summary(episodic: MemoryStore) -> str | None:
    summary: str | None = None
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_GLOBAL_STATUS:
            continue
        completed = event.payload.get("tasks_completed")
        total = event.payload.get("tasks_total")
        if isinstance(completed, int) and isinstance(total, int):
            summary = f"{completed} / {total}"
    return summary


def _build_observations(
    episodic: MemoryStore,
    *,
    own_agent_id: str | None = None,
    teammate_ids: frozenset[str] = frozenset(),
) -> list[_Observation]:
    observations: list[_Observation] = []
    seen_body_ids: set[str] = set()
    last_pending_task: str | None = None
    last_pending_task_room: str | None = None
    first_self_state = True
    body_sightings = _collect_body_sightings(episodic)
    own_kill_victims = _collect_own_kill_victims(episodic)
    breadcrumbs = _collect_movement_breadcrumbs(
        episodic,
        own_agent_id=own_agent_id,
        teammate_ids=teammate_ids,
        body_sightings=body_sightings,
    )
    # Task 13.9 same-room enrichment, both pure reads of the existing episodic
    # ``saw_player`` log (no packet field, firewall untouched): co-presence
    # ("with …") suffixes the sighting line, and within-vision transitions
    # ("entered/left") render as their own lines below.
    co_presence = _collect_co_presence(
        episodic,
        own_agent_id=own_agent_id,
        teammate_ids=teammate_ids,
        body_sightings=body_sightings,
    )
    observations.extend(
        _collect_transitions(
            episodic,
            own_agent_id=own_agent_id,
            teammate_ids=teammate_ids,
            body_sightings=body_sightings,
        )
    )

    for event in episodic.recent(since_tick=0):
        if event.type == _EVENT_SELF_STATE:
            pending_raw = event.payload.get("pending_task_id")
            pending = pending_raw if isinstance(pending_raw, str) else None
            room = event.payload.get("room")
            role = event.payload.get("role")
            # For a CREWMATE, ``pending_task_id`` is the lexicographically-first
            # owned, UNFINISHED map task (observation/service.py). Its owned set
            # only ever shrinks -- a task completes; none is added mid-game -- so
            # the pending id changes if and only if the previous pending task
            # completed, whether it clears to ``None`` (the final task) OR rolls to
            # the next map id (an intermediate task in a multi-task 9p/2i loadout).
            # Infer completion on ANY change away from a non-None pending task so an
            # intermediate completion is not dropped from rendered memory (PR #109).
            #
            # An IMPOSTOR's pending_task_id is a fabricated BLEND target (Task
            # 10.14) that the engine always rejects and that never completes; it
            # rotates through a per-seat set tick-to-tick. A change in it is NOT a
            # completion, so the inference is GATED to crewmates -- otherwise the
            # blend would mint fictitious "You completed ..." memory that could
            # become a fabricated ``completed_task`` alibi and corrupt the
            # meeting/eval evidence (Codex review, PR #155). The impostor's memory
            # stays accurate; alibi fabrication is the LLM's job (DESIGN.md §4.7).
            if (
                role == "CREWMATE"
                and not first_self_state
                and isinstance(last_pending_task, str)
                and pending != last_pending_task
            ):
                completed_room = (
                    last_pending_task_room
                    if isinstance(last_pending_task_room, str)
                    else "an unknown room"
                )
                observations.append(
                    _Observation(
                        salience=_SALIENCE_COMPLETED_TASK,
                        tick=event.tick,
                        line=(
                            f"[tick {event.tick}] You completed "
                            f"{last_pending_task} (you were in "
                            f"{completed_room})."
                        ),
                    )
                )
            last_pending_task = pending
            last_pending_task_room = room if isinstance(room, str) else None
            first_self_state = False
            continue

        if event.type == _EVENT_OWN_KILL:
            victim_id = event.payload.get("victim_id")
            room = event.payload.get("room")
            if not isinstance(victim_id, str) or not isinstance(room, str):
                continue
            observations.append(
                _Observation(
                    salience=_SALIENCE_OWN_KILL,
                    tick=event.tick,
                    line=(
                        f"[tick {event.tick}] You (IMPOSTOR) killed "
                        f"{victim_id} in {room}."
                    ),
                )
            )
            continue

        if event.type == _EVENT_SAW_BODY:
            body_id = event.payload.get("body_id")
            if not isinstance(body_id, str):
                continue
            if body_id in seen_body_ids:
                continue
            victim_id = event.payload.get("victim_id")
            room = event.payload.get("room")
            if not isinstance(victim_id, str) or not isinstance(room, str):
                # Don't mark the body as seen yet -- a later well-formed
                # event for the same body_id should still surface its
                # discovery.
                continue
            if victim_id in own_kill_victims:
                # The killer's own victim (Task 11.3, DESIGN.md §6.2): the body
                # it made surfaces through the ordinary ``saw_body`` channel, but
                # the kill is already narrated by the ``own_kill`` line above, so
                # suppress the "You discovered ... body" render for it. Other
                # bodies render normally. Mark it seen so a later duplicate
                # sighting of the same body stays suppressed too.
                seen_body_ids.add(body_id)
                continue
            seen_body_ids.add(body_id)
            observations.append(
                _Observation(
                    salience=_SALIENCE_FOUND_BODY,
                    tick=event.tick,
                    line=(
                        f"[tick {event.tick}] You discovered {victim_id}'s "
                        f"body in {room}."
                    ),
                )
            )
            continue

        if event.type == _EVENT_SAW_PLAYER:
            obs = _render_saw_player(
                event,
                own_agent_id=own_agent_id,
                teammate_ids=teammate_ids,
                body_sightings=body_sightings,
                breadcrumbs=breadcrumbs,
                co_presence=co_presence,
            )
            if obs is not None:
                observations.append(obs)
            continue

        if event.type == _EVENT_HEARD_VENT_USE:
            obs = _render_heard(
                event,
                salience=_SALIENCE_VENT_HEARD,
                noun="vent use",
            )
            if obs is not None:
                observations.append(obs)
            continue

        if event.type == _EVENT_HEARD_SABOTAGE_ALARM:
            obs = _render_heard(
                event,
                salience=_SALIENCE_SABOTAGE_HEARD,
                noun="sabotage alarm",
            )
            if obs is not None:
                observations.append(obs)
            continue

        if event.type == _EVENT_COOLDOWN_STATUS:
            cooldown = event.payload.get("cooldown")
            if isinstance(cooldown, int) and cooldown > 0:
                observations.append(
                    _Observation(
                        salience=_SALIENCE_COOLDOWN_STATUS,
                        tick=event.tick,
                        line=(
                            f"[tick {event.tick}] Your kill cooldown is "
                            f"{cooldown} ticks."
                        ),
                    )
                )

    return observations


def _render_saw_player(
    event: EpisodicEvent,
    *,
    own_agent_id: str | None = None,
    teammate_ids: frozenset[str] = frozenset(),
    body_sightings: tuple[tuple[str, int], ...] = (),
    breadcrumbs: dict[str, _Breadcrumb] | None = None,
    co_presence: dict[tuple[int, str], frozenset[str]] | None = None,
) -> _Observation | None:
    player_id = event.payload.get("player_id")
    room = event.payload.get("room")
    if not isinstance(player_id, str) or not isinstance(room, str):
        return None
    action = event.payload.get("action")
    action_str: str | None = action if isinstance(action, str) else None
    # Team-internal firewall (Task 9.3, DESIGN.md §4.7): suppress the self-subject
    # garble and the impostor's teammate-at-a-kill-window own-goal before the row
    # is built, so neither variant ever reaches the prompt (shared with
    # co-presence + transitions via :func:`_sighting_is_suppressed`).
    if _sighting_is_suppressed(
        player_id=player_id,
        room=room,
        tick=event.tick,
        action=action_str,
        own_agent_id=own_agent_id,
        teammate_ids=teammate_ids,
        body_sightings=body_sightings,
    ):
        return None
    if action_str == "vent":
        return _Observation(
            salience=_SALIENCE_VENT_WITNESSED,
            tick=event.tick,
            line=(f"[tick {event.tick}] You witnessed {player_id} vent in {room}."),
        )
    if action_str == "kill":
        return _Observation(
            salience=_SALIENCE_KILL_WITNESSED,
            tick=event.tick,
            line=(f"[tick {event.tick}] You witnessed {player_id} kill in {room}."),
        )
    # Task 13.9 co-presence + Task 13.6 breadcrumb suffixes, ordinary sightings
    # only (the vent/kill witnessed lines above stay clean). Co-presence ("with …")
    # lists the other subjects seen in the same room on the same tick; the
    # breadcrumb states the subject's most-recent prior room. Both are empty for a
    # solitary, non-moving subject, so that render is byte-identical to pre-13.6/9.
    co_present = _co_presence_suffix(
        co_presence, player_id=player_id, tick=event.tick, room=room
    )
    suffix = _movement_suffix_for(
        breadcrumbs, player_id=player_id, tick=event.tick, room=room
    )
    if action_str in _ACTIVE_PLAYER_ACTIONS:
        return _Observation(
            salience=_SALIENCE_SAW_PLAYER_ACTIVE,
            tick=event.tick,
            line=(
                f"[tick {event.tick}] You saw {player_id} "
                f"{action_str} in {room}{co_present}{suffix}."
            ),
        )
    return _Observation(
        salience=_SALIENCE_SAW_PLAYER,
        tick=event.tick,
        line=f"[tick {event.tick}] You saw {player_id} in {room}{co_present}{suffix}.",
    )


def _render_heard(
    event: EpisodicEvent,
    *,
    salience: int,
    noun: str,
) -> _Observation | None:
    room = event.payload.get("room")
    if isinstance(room, str):
        line = f"[tick {event.tick}] You heard a {noun} in {room}."
    elif room is None:
        line = f"[tick {event.tick}] You heard a {noun}."
    else:
        return None
    return _Observation(salience=salience, tick=event.tick, line=line)


def _build_belief_lines(
    beliefs: BeliefState,
    working: WorkingMemory,
    *,
    roster: frozenset[str] | None = None,
) -> list[str]:
    """Render the §6.6 belief rows, filtered to ``roster`` when supplied.

    ``roster`` is the engine-witnessed player-id set
    (:func:`_known_roster_ids`): a belief row outside it is a phantom
    subject (audit gp-6 C-C-8 -- e.g. a turn id materialised as a player
    row) and is skipped rather than rendered into the prompt. ``None``
    renders every known row (legacy fixtures without the 9.3 self
    channel, where the roster is underivable).
    """

    lines: list[str] = []
    for player_id in sorted(beliefs.known_players()):
        if roster is not None and player_id not in roster:
            continue
        belief = beliefs.view(player_id)
        belief_text = _format_belief_score(belief)
        if belief_text is None:
            continue
        suffix = _format_last_seen_suffix(working.last_seen(player_id))
        if suffix:
            lines.append(f"{player_id}: {belief_text} ({suffix})")
        else:
            lines.append(f"{player_id}: {belief_text}")
    return lines


def _format_belief_score(belief: PlayerBelief) -> str | None:
    suspicion_dev = abs(belief.suspicion - 0.5)
    trust_dev = abs(belief.trust - 0.5)
    # Anything within half of the displayed precision (0.01) rounds to
    # "0.50" in the rendered line and carries no signal, so treat it as
    # neutral. Float accumulation from repeated ``decay_suspicion``
    # toward 0.5 can otherwise leave a non-zero residue that escapes an
    # exact equality check and bloats the prompt with empty belief
    # rows.
    if suspicion_dev < 0.005 and trust_dev < 0.005:
        return None
    if suspicion_dev >= trust_dev:
        return f"suspicion {belief.suspicion:.2f}"
    return f"trust {belief.trust:.2f}"


def _format_last_seen_suffix(last_seen: LastSeen | None) -> str:
    if last_seen is None:
        return ""
    return f"last seen in {last_seen.room} at tick {last_seen.tick}"


def _build_contradiction_lines(
    beliefs: BeliefState,
    *,
    roster: frozenset[str] | None = None,
) -> list[str]:
    """Render the §6.6 open-contradiction lines, roster-filtered like beliefs.

    ``roster`` is the engine-witnessed player-id set
    (:func:`_known_roster_ids`): an inconsistency recorded on a
    non-roster (phantom-subject) row is skipped, mirroring
    :func:`_build_belief_lines`, so neither §6.6 section can surface a
    garbage subject (audit gp-6 C-C-8). The cross-player dedup is
    unchanged -- a flag recorded on both a roster and a non-roster row
    still renders once, via the roster row. ``None`` renders every known
    row (legacy fixtures without the 9.3 self channel).
    """

    seen: set[tuple[str, str, str]] = set()
    contradictions: list[ContradictionRef] = []
    for player_id in sorted(beliefs.known_players()):
        if roster is not None and player_id not in roster:
            continue
        belief = beliefs.view(player_id)
        for contradiction in belief.inconsistencies:
            key = (
                contradiction.summary,
                contradiction.left_ref,
                contradiction.right_ref,
            )
            if key in seen:
                continue
            seen.add(key)
            contradictions.append(contradiction)
    contradictions.sort(key=lambda c: (c.summary, c.left_ref, c.right_ref))
    return [c.summary for c in contradictions]


def _assemble_view(
    *,
    role: str,
    tasks_summary: str | None,
    observations: list[_Observation],
    beliefs_lines: list[str],
    contradiction_lines: list[str],
    token_budget: int,
) -> str:
    """Assemble the final Markdown view, enforcing token budget on observations.

    The role line, tasks-completed line, beliefs, and contradictions are
    treated as fixed (always rendered) because they are essential context.
    Observations are the elastic section: they fill the remaining budget,
    dropped from lowest salience first if the budget is tight.

    The budget arithmetic charges every character that lands in the
    final output, including the Markdown separators (``"\\n\\n"`` between
    blocks and the trailing ``"\\n"``), so the rendered view's actual
    token estimate cannot exceed ``token_budget``.
    """

    fixed_lines: list[str] = [f"## Your role: {role}"]
    if tasks_summary is not None:
        fixed_lines.append(f"## Tasks completed (global): {tasks_summary}")

    beliefs_block: list[str] = []
    if beliefs_lines:
        beliefs_block.append("## Your current beliefs:")
        beliefs_block.extend(f"- {line}" for line in beliefs_lines)

    contradictions_block: list[str] = []
    if contradiction_lines:
        contradictions_block.append("## Open contradictions:")
        contradictions_block.extend(f"- {line}" for line in contradiction_lines)

    non_elastic_blocks: list[list[str]] = [fixed_lines]
    if beliefs_block:
        non_elastic_blocks.append(beliefs_block)
    if contradictions_block:
        non_elastic_blocks.append(contradictions_block)
    non_elastic_text = (
        "\n\n".join("\n".join(block) for block in non_elastic_blocks) + "\n"
    )
    non_elastic_cost = _estimate_tokens(non_elastic_text)

    observations_header = "## Recent observations (most salient first):"
    # The observations block is inserted as a new top-level block, so
    # adding it costs one ``"\n\n"`` separator plus the header line.
    header_with_separator = "\n\n" + observations_header
    header_cost = _estimate_tokens(header_with_separator)

    remaining = token_budget - non_elastic_cost
    if remaining < header_cost:
        return non_elastic_text

    kept = _select_within_budget(
        observations=observations,
        budget=remaining - header_cost,
    )

    if not kept:
        return non_elastic_text

    blocks: list[list[str]] = [fixed_lines]
    observation_block = [observations_header]
    observation_block.extend(f"- {obs.line}" for obs in kept)
    blocks.append(observation_block)
    if beliefs_block:
        blocks.append(beliefs_block)
    if contradictions_block:
        blocks.append(contradictions_block)

    return "\n\n".join("\n".join(block) for block in blocks) + "\n"


def _select_within_budget(
    *,
    observations: Iterable[_Observation],
    budget: int,
) -> list[_Observation]:
    """Include observations in salience order until one cannot fit.

    ``observations`` must already be sorted by salience descending. As
    soon as an observation does not fit, we stop: every observation
    past the cutoff is at lower-or-equal salience, so allowing any of
    them through would violate "drop by lowest salience first"
    (DESIGN.md §6.6, DoD bullet 1). The kept set is therefore always a
    salience-ordered prefix of the input.

    Each observation line is preceded by a ``"\\n- "`` separator inside
    the observations block (the line is joined to the previous bullet
    line with ``"\\n"`` and prefixed with ``"- "``), so the budget cost
    of inserting it is computed against ``"\\n- " + obs.line``.
    """

    kept: list[_Observation] = []
    remaining = budget
    for obs in observations:
        line_with_separator = "\n- " + obs.line
        cost = _estimate_tokens(line_with_separator)
        if cost > remaining:
            break
        kept.append(obs)
        remaining -= cost
    return kept


__all__ = [
    "AgentMemory",
    "AlibiClaim",
    "BeliefState",
    "ContradictionRef",
    "DEFAULT_TOKEN_BUDGET",
    "EpisodicEvent",
    "MemoryStore",
    "PlayerBelief",
    "PlayerId",
    "RoomId",
    "TaskId",
    "WorkingMemory",
    "absorb_meeting_evidence",
    "render_for_prompt",
]
