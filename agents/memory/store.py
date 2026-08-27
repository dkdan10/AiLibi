"""Composite memory surface and prompt rendering (DESIGN.md §6.1, §6.6).

Aggregates the three stores introduced in Task 2.3 (`agents/memory/episodic.py`,
`agents/memory/working.py`, `agents/memory/beliefs.py`) into a single
:class:`AgentMemory` surface. ``render_for_prompt`` reads from all three
components to produce the token-budgeted Markdown view per DESIGN.md §6.6.

This composite is the integration point Phase 3 strategic agents import
through (audit R-6, `audits/audit-2026-05-15-0225-reconciled.md`).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field, replace
import os
from typing import Any, Final, TypeAlias

from agents.memory.beliefs import (
    BODY_PROXIMITY_WINDOW_TICKS,
    AlibiClaim,
    BeliefState,
    ContradictionRef,
    PlayerBelief,
    apply_meeting_evidence_rules,
    hard_evidence_gated_suspicion,
)
from agents.memory.episodic import EpisodicEvent, MemoryStore
from agents.memory.working import (
    LastSeen,
    MeetingHistory,
    RevealedRole,
    WorkingMemory,
)
from agents.perception import (
    EVENT_REPORTED_TESTIMONY,
    EVENT_SAW_PLAYER_MOVE,
    PROVENANCE_REPORTED,
)
from meetings.schemas import ReportedStatement

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
# A DIRECTLY-witnessed room→room transition (Task 13.5.4). First-hand sighting
# class -- the witness actually saw the actor move -- so it ranks just above a
# bare ``saw_player`` snapshot (it carries strictly more information: where the
# actor came FROM) and well above the RECONSTRUCTED within-vision breadcrumb
# (``_SALIENCE_TRANSITION``=48), which is inferred from consecutive deltas rather
# than seen. A tight budget therefore keeps the witnessed transit over the
# reconstructed one.
_SALIENCE_SAW_PLAYER_MOVE: Final[int] = 52
_SALIENCE_SAW_PLAYER: Final[int] = 50
# A within-vision entry/exit (Task 13.9), derived from consecutive own-room
# ``saw_player`` deltas. Ranked just below a direct sighting: it is valuable
# trajectory testimony but secondary to the sighting it is reconstructed from,
# so a tight budget keeps the primary sightings and sheds transitions first.
_SALIENCE_TRANSITION: Final[int] = 48
_SALIENCE_COMPLETED_TASK: Final[int] = 30
# Reported testimony: a meeting speaker's public CLAIM, rendered self-framed as
# unverified -- something the model WEIGHS, never ground truth it acts on as if
# witnessed. Banded above bare co-presence and below every first-hand HARD-evidence
# row (body, own kill, witnessed kill, witnessed vent, heard vent, heard sabotage),
# so the budget sheds routine sightings before it sheds the game's only
# cross-meeting social memory.
_SALIENCE_REPORTED_TESTIMONY: Final[int] = 60
_SALIENCE_COOLDOWN_STATUS: Final[int] = 10

# Per-subject cap on rendered reported alibis (Task 13.5.2, Codex P2). The §6.6
# belief block is the non-elastic carve-out (``_assemble_view`` never budgets it),
# so an unbounded accumulated alibi list could push ``render_for_prompt`` over
# ``DEFAULT_TOKEN_BUDGET``. Render only the most-recent few per subject; a newer
# alibi supersedes a stale one and N x subjects x this cap stays bounded.
_MAX_RENDERED_ALIBIS: Final[int] = 3

_EVENT_SAW_BODY: Final[str] = "saw_body"
_EVENT_SAW_PLAYER: Final[str] = "saw_player"
_EVENT_HEARD_VENT_USE: Final[str] = "heard_vent_use"
_EVENT_HEARD_SABOTAGE_ALARM: Final[str] = "heard_sabotage_alarm"
_EVENT_SELF_STATE: Final[str] = "self_state"
_EVENT_OWN_KILL: Final[str] = "own_kill"
_EVENT_GLOBAL_STATUS: Final[str] = "global_status"
_EVENT_COOLDOWN_STATUS: Final[str] = "cooldown_status"
# A meeting-boundary marker (Task 13.9, Codex review). Recorded at the resume
# tick by :func:`absorb_meeting_evidence` (the per-living-agent post-meeting fold,
# called by both the live orchestrator and the replay loader) so the within-vision
# transition render can tell that the world changed DISCONTINUOUSLY here -- a
# player ejected/removed at the meeting is gone without gameplay movement, and the
# resume tick is adjacent to the pre-meeting tick, so the tick-gap guard cannot see
# it. Carries no sighting data; it is inert to every other consumer.
_EVENT_MEETING_BOUNDARY: Final[str] = "meeting_boundary"

_ACTIVE_PLAYER_ACTIONS: Final[frozenset[str]] = frozenset({"report", "task"})

# The last-seen repair gate. ON, the "last seen in ROOM at tick T" suffix is the
# argmax over EVERY first-hand sighting the agent holds (ordinary looks included,
# not transitions alone) and the movement breadcrumb keeps the placement a
# witnessed vent/kill carries; OFF is the movement-only derivation the committed
# prompt bytes were recorded under. Accepts ``1/true/yes/on`` case-insensitively;
# anything else, unset included, is OFF.
#
# DEFAULT-OFF only to hold the byte-identity seam: every committed replay
# reconstructs against the OFF path, which is the code this build ships. The gate
# flips unconditional and is deleted at Task 21.15's combined re-record.
ENV_LAST_SEEN_FROM_SIGHTINGS: Final[str] = "AILIBI_LAST_SEEN_FROM_SIGHTINGS"
_LAST_SEEN_FROM_SIGHTINGS_FLAG_TRUE: Final[frozenset[str]] = frozenset(
    {"1", "true", "yes", "on"}
)


def last_seen_from_sightings_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Whether the render derives last-seen from every sighting (see the gate above).

    ``orchestrator.replay`` mirrors this resolver for the substrate stamp; the two
    are pinned equivalent over the env grid in ``tests/orchestrator/test_replay.py``.
    """

    environment = env if env is not None else os.environ
    return (
        environment.get(ENV_LAST_SEEN_FROM_SIGHTINGS, "").strip().lower()
        in _LAST_SEEN_FROM_SIGHTINGS_FLAG_TRUE
    )


@dataclass
class AgentMemory:
    """Composite memory surface for a single agent (DESIGN.md §6.1).

    Aggregates references to the episodic, working and belief stores plus the
    ``meeting_history`` channel. The composite does not copy state: callers
    mutate the underlying stores directly and the composite reflects every
    change. ``render_for_prompt`` reads all four (the R-6 acceptance gate);
    ``meeting_history`` is fed by :func:`record_meeting_outcome` from the public
    ``note_meeting_concluded`` hook, read by the v3 tactical feature encoder, and
    rendered as the ``## Meetings so far:`` block. Every field defaults, so a
    three-store construction still builds.
    """

    episodic: MemoryStore = field(default_factory=MemoryStore)
    working: WorkingMemory = field(default_factory=WorkingMemory)
    beliefs: BeliefState = field(default_factory=BeliefState)
    meeting_history: MeetingHistory = field(default_factory=MeetingHistory)


@dataclass(frozen=True)
class _Observation:
    """One renderable observation line with the data needed to sort and budget it.

    ``observation_id`` is the stable id of the SINGLE episodic event this line
    derives from, or ``None`` when the line is not a single citable observation
    (a RECONSTRUCTED breadcrumb / transition, a meeting boundary);
    :func:`render_for_prompt` folds it into the line as an ``[obs {id}]`` prefix.

    ``sighting`` carries the span key of a bare co-presence row and is ``None`` for
    every other class; it is what :func:`_coalesce_sightings` folds runs on.
    ``sighting_suffix`` is that row's directional breadcrumb, carried beside the key
    rather than inside it -- it lands on a subject's most-recent sighting only, so
    it must not split the run it terminates.
    """

    salience: int
    tick: int
    line: str
    observation_id: str | None = None
    sighting: _SightingKey | None = None
    sighting_suffix: str = ""


@dataclass(frozen=True)
class _SightingKey:
    """What two bare sightings must share to belong to one coalesced span.

    A run folds only when its rows say the same thing about the same subject --
    same room, same action, the same companions -- so the span line states exactly
    what the rows it replaces stated.
    """

    subject: str
    room: str
    action: str | None
    companions: frozenset[str]


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


@dataclass(frozen=True)
class _SelfPlacement:
    """Where the agent's own ``self_state`` record puts it at one recorded tick."""

    room: str
    in_vent: bool


@dataclass(frozen=True)
class _SelfLocationSpan:
    """One coalesced run of adjacent recorded ticks the agent spent in one place."""

    start_tick: int
    end_tick: int
    room: str
    in_vent: bool


# Most spans the trail block renders; past it the OLDEST are dropped and the block
# says so. Sized from the committed sets: the furthest back a crew ``whereabouts``
# answer ever reaches is 10 spans on both 9p2i sets and 4 on both 4p1i sets, so 12
# holds every recorded claim's tick while keeping a long game's route bounded.
SELF_LOCATION_TRAIL_MAX_SPANS: Final[int] = 12

_TRAIL_HEADER: Final[str] = "## Where you were:"
_TRAIL_TRUNCATED_LINE: Final[str] = "Earlier parts of your route are not listed."
# The route renders as ONE chained line rather than one line per span. A step
# carries the same room and the same tick range a per-span line did, at roughly
# half the budget, so more of the observations block survives beside a full route
# (the displacement both shapes cost is pinned in tests/eval/test_evidence_honesty).
_TRAIL_ROUTE_PREFIX: Final[str] = "Your route (t = tick): "
_TRAIL_STEP_JOIN: Final[str] = " -> "
# A tick the agent holds no row for is stated, never bridged: the arrow between
# two steps means "and then", so an unrecorded stretch needs its own step.
_TRAIL_GAP_STEP: Final[str] = "(no record)"

_MEETINGS_HEADER: Final[str] = "## Meetings so far:"

# The one-line summary that replaces a full-roster tick-0 sighting group. It names
# every subject it stands for, so the fold costs a line instead of a roster.
_SPAWN_GROUP_PREFIX: Final[str] = "You saw every other player in "


def _impostors_remaining_clause(remaining: int | None) -> str:
    """The trailing parity sentence, or "" when the count is underivable."""

    if remaining is None:
        return ""
    noun = "impostor remains" if remaining == 1 else "impostors remain"
    return f" {remaining} {noun}."


def _meeting_history_lines(history: MeetingHistory) -> list[str]:
    """One plain line per concluded meeting, oldest first.

    The grammar the agent reads back is the sentence the table heard::

        Meeting 1 (tick 14): p-4 EJECTED 7-1 — p-4 was an IMPOSTOR. 1 impostor remains.
        Meeting 2 (tick 27): no ejection (6 skip). 1 impostor remains.

    Every clause is dropped rather than guessed when the fold did not carry it:
    an outcome with no tally states the ejection alone, one with no announced
    role omits the role clause, and an underivable parity count says nothing.
    """

    lines: list[str] = []
    for index, outcome in enumerate(history.outcomes):
        head = f"Meeting {index + 1} (tick {outcome.end_tick}):"
        if outcome.ejected_id is None:
            body = (
                "no ejection."
                if outcome.skip_votes is None
                else f"no ejection ({outcome.skip_votes} skip)."
            )
        else:
            tally = (
                ""
                if outcome.votes_for_ejected is None or outcome.skip_votes is None
                else f" {outcome.votes_for_ejected}-{outcome.skip_votes}"
            )
            body = f"{outcome.ejected_id} EJECTED{tally}."
            if outcome.revealed_role is not None:
                article = "an" if outcome.revealed_role == "IMPOSTOR" else "a"
                body = (
                    f"{outcome.ejected_id} EJECTED{tally} — "
                    f"{outcome.ejected_id} was {article} {outcome.revealed_role}."
                )
        clause = _impostors_remaining_clause(history.impostors_remaining_after(index))
        lines.append(f"{head} {body}{clause}")
    return lines


def render_for_prompt(
    memory: AgentMemory,
    *,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
    suspicion_override: Mapping[PlayerId, float] | None = None,
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

    ``suspicion_override`` (Task 13.5.5) replaces the SUSPICION value of a
    belief line for the listed players, leaving trust, alibis, last-seen,
    and the open-contradictions section read from ``memory.beliefs``. The
    meeting passes the per-voter pre-vote-folded suspicion (the same numbers
    the vote-ballot ``suspicion_graph`` kwarg carries) so the ballot's belief
    lines and that graph agree by construction. ``None`` (the default, and
    every non-ballot render) is byte-identical to pre-task HEAD.

    Every first-hand observation line carries its stable
    ``[obs {agent}:{tick}:{seq}]`` id, folded in BEFORE the salience sort so
    ordering, tie-breaks and the token-budget arithmetic all see the final bytes.
    RECONSTRUCTED lines (breadcrumb transitions, the meeting boundary) derive
    from several events, carry no id and render unadorned. The completed-task
    line is minted from the ids that LEAVE the agent's ``owned_task_ids`` and
    takes its room from the same ``self_state`` row that dates it, so it carries
    one clock.

    The ``## Meetings so far:`` block renders one plain line per concluded
    meeting, oldest first: ``Meeting {n} (tick {resume}): {id} EJECTED
    {for}-{skip} — {id} was an IMPOSTOR. {k} impostors remain.``, or ``… no
    ejection ({skip} skip). …`` when the vote skipped or tied. It joins the
    NON-elastic set above the observations, so a budget-tight render sheds
    sightings around it and never sheds the record of what a meeting decided.
    The role clause is the one place a rendered memory names another player's
    role, and it is entitled rather than exempt: confirm-ejects makes the EJECTED
    player's role public at the table on the same footing as ``dead_ids`` and the
    announced tally (DESIGN.md §4.7), so it is disclosed only for a player the
    table ejected and only from that meeting onward -- never for a living player,
    and never for a kill victim, whose role nobody saw. The orchestrator is the
    only module that reads a role off engine state; ``agents/`` and ``meetings/``
    receive the announcement already made. ``eval.leak_scan`` states the same
    rule independently of this code
    (:func:`~eval.leak_scan.assert_memory_render_role_disclosure_is_entitled`).

    The ``## Where you were:`` block sits between the fixed lines and the
    observations, so the agent answers the meeting's roll-call from its own
    record instead of extrapolating: the ticks its ``self_state`` channel
    recorded, coalesced oldest-first into spans and chained onto ONE line,
    ``ROOM t{a}-{b} -> ROOM t{c} -> ...`` (a lone tick states one tick, and a
    tick spent in a vent says so). Chaining costs about half the per-span shape,
    so the whole route reaches the prompt beside the observations rather than
    displacing them. A tick with no recorded row BREAKS a span and renders its
    own ``(no record)`` step -- the trail never interpolates across a gap --
    while a meeting boundary does not, because a meeting freezes movement
    (DESIGN.md §5.1). At most :data:`SELF_LOCATION_TRAIL_MAX_SPANS` spans render;
    past that the oldest are dropped and the block says so in one plain line. The
    route line carries no ``[obs ...]`` prefix -- a span is coalesced from several
    rows rather than being one citable observation -- so it cannot teach a model
    to cite an id the ballot validator would null.

    The observations budget is spent on what discriminates. A run of consecutive
    sightings of one subject in one room, same action and an unchanged companion
    set, renders as ONE line stating its tick range (``You saw p-9 in CAFETERIA
    ticks 0-4 (with p-8).``); any change of room, action or companions -- and any
    tick the agent holds no row for -- breaks the run, so a span never claims a
    tick its rows did not. A tick-0 group that names the whole known roster minus
    the observer collapses to one summary line naming those subjects, over the
    stretch they all shared, because "everyone started together" is one fact and
    a partial view is not (a player absent at spawn is real information, so that
    view keeps its rows). The span carries its FIRST row's ``observation_id``, so
    every id a ballot can cite off the render is still one of the agent's own
    stored ids. Reported testimony ranks above bare co-presence in the salience
    ladder, so the budget sheds routine sightings before it sheds the game's only
    cross-meeting social memory.

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
    observations = _build_observations(
        memory.episodic,
        own_agent_id=own_agent_id,
        teammate_ids=teammate_ids,
    )
    # §6.6 roster filter (Task 10.2, audit gp-6 C-C-8): belief rows AND
    # open-contradiction lines render only for engine-witnessed player
    # ids, so a garbage subject that somehow reached the store (the
    # seed-12 m2 turn-id-as-player rows) cannot render into any prompt
    # through either section. Gated on the same 9.3 self channel as the
    # guards above: with no recorded ``agent_id`` (pre-9.3 fixtures) the
    # roster is underivable and the render is byte-identical to today --
    # production perception has recorded the id on every tick since
    # Task 9.3. The span fold reads the same set, so "everyone" in its
    # tick-0 summary means the same roster the belief rows are filtered by.
    roster = _known_roster_ids(memory.episodic) if own_agent_id is not None else None
    # Fold the runs BEFORE the id prefix and the sort: the fold works on the
    # built observations, so every firewall suppression, co-presence suffix
    # and breadcrumb is already settled and a span cites a real stored id.
    observations = _coalesce_sightings(
        observations, roster=roster, own_agent_id=own_agent_id
    )
    # Fold each first-hand observation's stable id into its line BEFORE the
    # salience sort, so ordering, tie-breaks and the token-budget arithmetic all
    # see the final bytes. RECONSTRUCTED lines (breadcrumb transitions, the
    # meeting boundary) carry ``observation_id is None`` -- they derive from
    # MULTIPLE events and are not a single citable observation -- so they render
    # unchanged. The ``[obs ...]`` wrapper is render dressing only; a ballot
    # cites the raw ``{agent}:{tick}:{seq}`` id, not the wrapper.
    observations = [
        replace(obs, line=f"[obs {obs.observation_id}] {obs.line}")
        if obs.observation_id is not None
        else obs
        for obs in observations
    ]
    observations = sorted(
        observations,
        key=lambda obs: (-obs.salience, -obs.tick, obs.line),
    )
    # Fill ``working.last_seen`` ← the latest first-hand sighting of each subject,
    # read by the belief-line suffix below (the R-6 composite-memory gate: render
    # reads all three stores). Idempotent across repeated renders and
    # firewall-suppressed -- see :func:`_record_last_seen_sightings`.
    _record_last_seen_sightings(
        memory.episodic,
        memory.working,
        own_agent_id=own_agent_id,
        teammate_ids=teammate_ids,
        body_sightings=_collect_body_sightings(memory.episodic),
    )
    beliefs_lines = _build_belief_lines(
        memory.beliefs,
        memory.working,
        roster=roster,
        suspicion_override=suspicion_override,
    )
    contradiction_lines = _build_contradiction_lines(memory.beliefs, roster=roster)
    spans = _collect_self_location_spans(memory.episodic)
    trail_truncated = len(spans) > SELF_LOCATION_TRAIL_MAX_SPANS
    trail_spans = spans[-SELF_LOCATION_TRAIL_MAX_SPANS:]

    meeting_lines = _meeting_history_lines(memory.meeting_history)

    return _assemble_view(
        role=role,
        tasks_summary=tasks_summary,
        observations=observations,
        beliefs_lines=beliefs_lines,
        contradiction_lines=contradiction_lines,
        meeting_lines=meeting_lines,
        trail_spans=trail_spans,
        trail_truncated=trail_truncated,
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

    # Mark the meeting boundary so the §6.9 within-vision transition render does
    # NOT infer a movement across it (Task 13.9, Codex review). Gameplay resumes at
    # the pre-meeting tick + 1 (``apply_meeting_result``: ``working.tick + 1``) and
    # the meeting-trigger ``advance_tick`` does not increment the tick, so the
    # pre-meeting and resume packets land on ADJACENT ticks -- the transition's
    # tick-gap guard cannot see the boundary. Without this marker a player
    # ejected/removed at the meeting (gone, no body, no gameplay movement) renders a
    # bogus "left ROOM" on the resume tick. This is the universal per-living-agent
    # post-meeting hook (live orchestrator AND replay loader both call it), so the
    # marker lands on every path that reconstructs memory; it carries no sighting
    # data and is inert to every consumer except :func:`_collect_transitions`.
    last_perceived_tick = _latest_self_state_tick(memory.episodic)
    if last_perceived_tick is not None:
        memory.episodic.append(
            EpisodicEvent(
                tick=last_perceived_tick + 1,
                type=_EVENT_MEETING_BOUNDARY,
                payload={},
                provenance="inferred",
            )
        )


def absorb_reported_testimony(
    memory: AgentMemory,
    *,
    statements: Sequence[ReportedStatement],
) -> None:
    """Fold one meeting's public testimony into ``memory`` as CONTENT (Task 13.5.2).

    The content twin of :func:`absorb_meeting_evidence`. Where that wrapper folds
    a meeting into a scalar suspicion Δ, this one preserves the WHAT of public
    speech (the 2026-06-25 memory diagnosis, workflow ``wg54kfoxy``: "social info
    is a scalar, not content"): it appends one ``provenance="reported"`` episodic
    row per :class:`~meetings.schemas.ReportedStatement` and, for each
    ``alibi`` statement, populates the previously-dead ``alibi_map`` via
    :meth:`BeliefState.record_alibi`. The orchestrator and the replay loader call
    it per LIVING agent in the SAME loop as :func:`absorb_meeting_evidence`,
    unconditionally since Task 14.9 (the adopted 13.5.2 lever is the default
    substrate; the ``AILIBI_TESTIMONY_AS_CONTENT`` gate is retired).

    Reported rows land at the meeting-boundary tick (``_latest_self_state_tick``
    + 1, the tick :func:`absorb_meeting_evidence` already uses for its boundary
    marker), so the episodic store's non-decreasing-tick invariant holds and the
    rows render under a ``[meeting]`` tag at a salience strictly below first-hand.

    Three guards, mirroring the scalar twin's self channel / roster filter:

    * OWN statements are SKIPPED -- a statement whose ``speaker`` is the
      recipient's own id (read from the privileged ``self_state`` channel,
      :func:`_latest_self_guard_fields`) is testimony the agent itself gave; it
      already lives in the agent's first-hand memory and must not echo back as a
      third-party claim.
    * ROSTER-only -- both the speaker and the subject must be in the agent's
      engine-witnessed id set (:func:`_known_roster_ids`), so a hallucinated
      structural id never materialises a reported row (the same backstop
      :func:`absorb_meeting_evidence` applies to the scalar fold).
    * NOT teammate-firewalled -- reported content is PUBLIC speech (owner
      decision, locked 2026-06-25), so a teammate-incriminating public statement
      DOES appear in an impostor's reported memory. Only the SCALAR suspicion
      firewall stays (unchanged, in :func:`absorb_meeting_evidence`).
    A ``saw_vent`` statement is kept as CONTENT: the game's one role-proving
    public observation survives the trip into memory with its room and tick
    intact, instead of arriving as a bare accusation.

    Each row also carries the 1-based ``meeting_index`` it was spoken at, counted
    from the ``meeting_boundary`` markers :func:`absorb_meeting_evidence` has
    already appended for this meeting — the agent's OWN record of how many
    meetings it has taken evidence from, so the tag and the ``## Meetings so far:``
    block number the same meetings. The live orchestrator and the replay loader
    both run that fold first, so the index is the same on either path. An agent
    that folds no meeting evidence holds no such record: the index is then
    UNDERIVABLE and the row carries none, so the render states the untagged
    ``[meeting]`` frame rather than a fabricated ordinal.

    Raises :class:`ValueError` when no ``self_state`` event carrying the agent's
    own id has been recorded -- the own-statement guard cannot run without it,
    and a meeting before perception is a wiring bug, not a normal state (AGENTS.md
    "no silent fallbacks"; matches :func:`absorb_meeting_evidence`).
    """

    own_agent_id, _fellow_impostor_ids = _latest_self_guard_fields(memory.episodic)
    if own_agent_id is None:
        raise ValueError(
            "cannot absorb reported testimony: no self_state event carrying "
            "'agent_id' has been recorded; perception must run at least once "
            "before a meeting's testimony is folded."
        )
    last_perceived_tick = _latest_self_state_tick(memory.episodic)
    if last_perceived_tick is None:
        # Unreachable when own_agent_id is set (both come from self_state rows),
        # but keeps the tick derivation total for mypy and future callers.
        return
    boundary_tick = last_perceived_tick + 1
    roster = _known_roster_ids(memory.episodic)
    boundaries = sum(
        1
        for event in memory.episodic.recent(since_tick=0)
        if event.type == _EVENT_MEETING_BOUNDARY
    )
    # No boundary record means this agent folds no meeting evidence, so which
    # meeting this is cannot be known -- state nothing rather than guess.
    meeting_index = boundaries if boundaries > 0 else None
    for statement in statements:
        if statement.speaker == own_agent_id:
            continue
        if statement.speaker not in roster or statement.subject not in roster:
            continue
        memory.episodic.append(
            EpisodicEvent(
                tick=boundary_tick,
                type=EVENT_REPORTED_TESTIMONY,
                payload={
                    "speaker": statement.speaker,
                    "kind": statement.kind,
                    "subject": statement.subject,
                    "meeting_index": meeting_index,
                    "from_tick": statement.from_tick,
                    "to_tick": statement.to_tick,
                    "room": statement.room,
                    # Co-present companions, roster-gated like the subject -- the
                    # public "who was with whom" sighting evidence (Codex P2).
                    "co_present": sorted(
                        companion
                        for companion in statement.co_present
                        if companion in roster
                    ),
                },
                provenance=PROVENANCE_REPORTED,
            )
        )
        # A reported alibi ABOUT the recipient never materialises a SELF belief
        # row: belief rows are about OTHER players and the scalar fold excludes
        # own_id, so a self alibi would pollute the §6.6 view and the vote-prompt
        # suspicion graph (Codex P2). The episodic CONTENT row above is still kept
        # -- the agent may want to know it was publicly placed somewhere.
        if (
            statement.kind == "alibi"
            and statement.from_tick is not None
            and statement.subject != own_agent_id
        ):
            memory.beliefs.record_alibi(
                AlibiClaim(
                    player_id=statement.subject,
                    tick=statement.from_tick,
                    room=statement.room if statement.room is not None else "",
                    source=statement.speaker,
                )
            )


def record_meeting_outcome(
    memory: AgentMemory,
    *,
    end_tick: int,
    ejected_id: PlayerId | None,
    revealed_role: RevealedRole | None = None,
    votes_for_ejected: int | None = None,
    skip_votes: int | None = None,
    roster_impostor_count: int | None = None,
) -> None:
    """Fold one concluded meeting's public outcome into memory.

    The meeting-history twin of :func:`absorb_meeting_evidence`: where that
    wrapper folds a meeting into a scalar suspicion Δ on the belief state, this
    one records the meeting's PUBLIC result into ``memory.meeting_history`` by
    delegating to :meth:`~agents.memory.working.MeetingHistory.record` -- the
    resume ``end_tick``, the announced ``ejected_id`` (``None`` when the vote
    skipped or tied), the confirm-ejects ``revealed_role`` of that player, the
    announced ``votes_for_ejected`` / ``skip_votes`` tally, and the
    ``roster_impostor_count`` stated at game start.

    The channel is fed EXCLUSIVELY from the ``note_meeting_concluded`` hook's
    PUBLIC payload, so it is firewall-clean by construction: every field is a
    fact every player at the table already heard, and no engine-private state
    crosses into agent memory (DESIGN.md §4.7, the same public footing as the
    meeting's ``dead_ids``). The role in particular is the confirm-ejects
    announcement and nothing else -- a KILLED player's role is never folded,
    because nobody at the table saw it. The four announcement fields default to
    ``None``, so a caller that knows only the tick and the ejection still
    records and the v3 tactical feature encoder's three-scalar channel reads
    exactly what it read before they existed.

    Rendered by :func:`render_for_prompt` as the ``## Meetings so far:`` block.

    The non-negative / non-decreasing ``end_tick`` guards and the
    skip-reveals-no-role guard live in ``MeetingHistory.record``, so an
    inconsistent fold fails loud (AGENTS.md "no silent fallbacks") rather than
    silently recording a contradiction.
    """

    memory.meeting_history.record(
        end_tick=end_tick,
        ejected_id=ejected_id,
        revealed_role=revealed_role,
        votes_for_ejected=votes_for_ejected,
        skip_votes=skip_votes,
        roster_impostor_count=roster_impostor_count,
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


def _latest_self_state_tick(episodic: MemoryStore) -> int | None:
    """The tick of the most recent ``self_state`` -- the last tick the agent
    perceived. ``self_state`` rows are appended in non-decreasing tick order, so
    the last one seen is the latest. ``None`` before any perception has run.
    """

    tick: int | None = None
    for event in episodic.recent(since_tick=0):
        if event.type == _EVENT_SELF_STATE:
            tick = event.tick
    return tick


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
    * ``saw_player_move`` -- every witnessed transition's mover (Task 13.5.4);
      a player the agent saw move is a witnessed roster member (in practice it
      always co-occurs with a ``saw_player`` row under the same visibility
      gate);
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
        elif event.type in (_EVENT_SAW_PLAYER, EVENT_SAW_PLAYER_MOVE):
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

    The ANCHOR -- the one line that gets suffixed -- is always the subject's most
    recent ORDINARY sighting, so exactly one line per moving subject carries a
    suffix and the vent / kill lines stay clean (they are witnessed events with
    their own high-salience rendering, and :func:`_render_saw_player` returns them
    before any suffix is computed). The PRIOR room is the subject's most recent
    different-room row at or before that anchor -- ordinary rows always, and
    behind the last-seen repair gate (:func:`last_seen_from_sightings_enabled`)
    vent / kill rows too. A witnessed vent is the strongest placement evidence a
    game produces; dropping it from the path under-reports the subject as last
    seen in that room at an EARLIER tick than the render itself states one line
    above.

    The SAME §4.7 suppressions the renderer applies are mirrored here
    (self-subject, teammate kill-window), so a suppressed sighting never
    contributes a breadcrumb. A subject seen in only one room (or once) yields no
    breadcrumb.
    """

    fold_vent_and_kill_rows = last_seen_from_sightings_enabled()
    # ``(tick, room, is_ordinary)``: the flag separates anchor candidates (ordinary
    # only) from prior-room candidates (all recorded rows).
    paths: dict[str, list[tuple[int, str, bool]]] = {}
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SAW_PLAYER:
            continue
        player_id = event.payload.get("player_id")
        room = event.payload.get("room")
        if not isinstance(player_id, str) or not isinstance(room, str):
            continue
        action = event.payload.get("action")
        action_str = action if isinstance(action, str) else None
        is_ordinary = action_str not in ("vent", "kill")
        if not is_ordinary and not fold_vent_and_kill_rows:
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
        paths.setdefault(player_id, []).append((event.tick, room, is_ordinary))

    breadcrumbs: dict[str, _Breadcrumb] = {}
    for subject, sightings in paths.items():
        # Stable sort by tick keeps recorded order for same-tick ties, so the
        # most-recent sighting and its prior different-room sighting are
        # replay-deterministic.
        ordered = sorted(sightings, key=lambda entry: entry[0])
        anchors = [entry for entry in ordered if entry[2]]
        if not anchors:
            continue
        last_tick, last_room, _ = anchors[-1]
        prior: tuple[int, str] | None = None
        for tick, room, _is_ordinary in reversed(ordered):
            # At or before the anchor only: a row the agent saw AFTER the
            # suffixed line is not that line's prior room.
            if tick > last_tick or room == last_room:
                continue
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


def _co_presence_members(
    co_presence: dict[tuple[int, str], frozenset[str]] | None,
    *,
    player_id: str,
    tick: int,
    room: str,
) -> frozenset[str]:
    """The OTHER (non-suppressed) subjects seen in this room on this tick.

    The companion set the sighting line's suffix is written from and the span fold
    groups on, so both read one answer to "who else was there".
    """

    if co_presence is None:
        return frozenset()
    return co_presence.get((tick, room), frozenset()) - {player_id}


def _co_presence_suffix(companions: frozenset[str]) -> str:
    """The "(with …)" companion suffix for one ``saw_player`` line (Task 13.9).

    Empty for a solitary subject, so that render is byte-identical to the pre-13.9
    output. Companions are sorted for replay determinism.
    """

    if not companions:
        return ""
    return " (with " + ", ".join(sorted(companions)) + ")"


def _self_placement_by_tick(episodic: MemoryStore) -> dict[int, _SelfPlacement]:
    """The one answer to "where was I at tick N", read off the own self channel.

    Ticks with no readable room are ABSENT rather than guessed, so every consumer
    can distinguish "recorded elsewhere" from "no record at all". A tick holds ONE
    placement: two rows that disagree about it raise, because the route has no
    sub-tick step to render them as, and a completion line placed by its own row
    would then contradict the route the same prompt shows.
    An ABSENT ``in_vent`` key means "not in a vent" (pre-11.1 and engine-only rows
    carry none); a key that IS present must hold a bool, and anything else --
    including an explicit null -- is a boundary-contract violation and raises
    rather than quietly rendering an ordinary room stay.
    """

    placements: dict[int, _SelfPlacement] = {}
    for event in episodic.recent(since_tick=0):
        if event.type != _EVENT_SELF_STATE:
            continue
        room = event.payload.get("room")
        if not isinstance(room, str):
            continue
        in_vent = False
        if "in_vent" in event.payload:
            raw_in_vent = event.payload["in_vent"]
            if not isinstance(raw_in_vent, bool):
                raise ValueError(
                    f"self_state event has non-bool in_vent: {event.payload!r}"
                )
            in_vent = raw_in_vent
        placement = _SelfPlacement(room=room, in_vent=in_vent)
        recorded = placements.get(event.tick)
        if recorded is not None and recorded != placement:
            raise ValueError(
                f"self_state events disagree about tick {event.tick}: "
                f"{recorded} then {placement}"
            )
        placements[event.tick] = placement
    return placements


def _collect_self_location_spans(episodic: MemoryStore) -> list[_SelfLocationSpan]:
    """Coalesce the agent's own recorded ticks into an oldest-first route.

    A run extends only while the next recorded tick is ADJACENT and the placement
    is unchanged, so a tick the agent holds no row for BREAKS the span instead of
    being interpolated across -- the trail may only claim ticks it has a record
    for. A meeting boundary does NOT break a span: the meeting freezes movement
    (DESIGN.md §5.1), so one room really does cover both sides of it. That is the
    single place this walk differs from :func:`_collect_transitions`, which must
    break there because OTHERS change discontinuously across a meeting.
    """

    spans: list[_SelfLocationSpan] = []
    placements = _self_placement_by_tick(episodic)
    for tick in sorted(placements):
        placement = placements[tick]
        if spans:
            open_span = spans[-1]
            if (
                open_span.end_tick + 1 == tick
                and open_span.room == placement.room
                and open_span.in_vent == placement.in_vent
            ):
                spans[-1] = replace(open_span, end_tick=tick)
                continue
        spans.append(
            _SelfLocationSpan(
                start_tick=tick,
                end_tick=tick,
                room=placement.room,
                in_vent=placement.in_vent,
            )
        )
    return spans


def _trail_step(span: _SelfLocationSpan) -> str:
    """One step of the route: where the agent was, then the ticks it was there."""

    where = f"a vent in {span.room}" if span.in_vent else span.room
    ticks = (
        f"t{span.start_tick}"
        if span.start_tick == span.end_tick
        else f"t{span.start_tick}-{span.end_tick}"
    )
    return f"{where} {ticks}"


def _trail_route_line(spans: Sequence[_SelfLocationSpan]) -> str:
    """Chain the spans into one oldest-first route line, stating every gap.

    Steps are joined by an arrow meaning "and then"; a stretch of ticks the agent
    holds no row for gets its own ``(no record)`` step, so the line never reads as
    a claim about a tick the record does not cover.

    The line carries no ``[obs ...]`` prefix: a step is coalesced from several
    self-state rows rather than being one citable observation, and the roll-call
    asks for a room and a tick, not a citation. Chaining is also what keeps the
    whole route affordable — one header and one bullet for the entire route.
    """

    steps: list[str] = []
    previous_end: int | None = None
    for span in spans:
        if previous_end is not None and span.start_tick != previous_end + 1:
            steps.append(_TRAIL_GAP_STEP)
        steps.append(_trail_step(span))
        previous_end = span.end_tick
    return _TRAIL_ROUTE_PREFIX + _TRAIL_STEP_JOIN.join(steps)


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
    adjacent): if the observer moved the field of view changed, so a delta cannot
    be attributed to the SUBJECT moving and is skipped. A tick pair that SPANS a
    meeting boundary (``_EVENT_MEETING_BOUNDARY`` at the resume tick) is likewise
    skipped: gameplay resumes one tick after the pre-meeting tick, so the pair is
    adjacent, but the world changed discontinuously (ejections, body consumption)
    and no delta across it is movement (Codex review). The observer never sees the
    adjacent origin/destination (room-only), so the full X→Y trajectory emerges
    COLLECTIVELY when meeting testimony is combined -- complementing the 13.6
    own-sightings breadcrumb.

    Own-room scoping uses the observer's ``self_state`` room per tick; only
    sightings in that room count, so an impostor's adjacent-room sightings (which
    the observer cannot vouch a transition for) are excluded. The §4.7
    suppressions are mirrored so a suppressed subject never produces a transition.
    A subject that vanished because it was KILLED in the room (its body now
    visible there) produces NO "left": a death in place is not a departure, and
    the ``saw_body`` line carries the truthful testimony.
    """

    own_room_by_tick: dict[int, str] = {
        tick: placement.room
        for tick, placement in _self_placement_by_tick(episodic).items()
    }
    seen_in_own_room: dict[int, set[str]] = {}
    # Resume ticks of concluded meetings (recorded by ``absorb_meeting_evidence``).
    # The world changes DISCONTINUOUSLY across a meeting -- a player can be ejected
    # or otherwise removed with no gameplay movement -- and the resume tick is
    # adjacent to the pre-meeting tick, so a delta across this boundary must NOT
    # become a transition (Codex review).
    meeting_boundary_ticks: set[int] = set()
    # Bodies the observer saw, keyed by tick -> {(victim_id, room)}. A subject seen
    # at N but gone at N+1 because it was KILLED in the room (its body now visible)
    # did NOT leave -- the body discovery is the truthful testimony. Suppressing the
    # bogus "left" keeps path reconstruction from recording a departure that never
    # happened (Codex review): a death in place is not a movement.
    body_victims_by_tick: dict[int, set[tuple[str, str]]] = {}
    for event in episodic.recent(since_tick=0):
        if event.type == _EVENT_SAW_BODY:
            victim_id = event.payload.get("victim_id")
            body_room = event.payload.get("room")
            if isinstance(victim_id, str) and isinstance(body_room, str):
                body_victims_by_tick.setdefault(event.tick, set()).add(
                    (victim_id, body_room)
                )
        elif event.type == _EVENT_MEETING_BOUNDARY:
            meeting_boundary_ticks.add(event.tick)

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
        if tick in meeting_boundary_ticks:
            # A meeting concluded between prev_tick and tick: the world changed
            # discontinuously (ejections, body consumption), so no delta across
            # this boundary is gameplay movement (Codex review).
            continue
        room = own_room_by_tick[tick]
        if own_room_by_tick.get(prev_tick) != room:
            continue
        prev_seen = seen_in_own_room.get(prev_tick, set())
        now_seen = seen_in_own_room.get(tick, set())
        killed_in_room = {
            victim
            for victim, body_room in body_victims_by_tick.get(tick, set())
            if body_room == room
        }
        for subject in sorted(now_seen - prev_seen):
            transitions.append(
                _Observation(
                    salience=_SALIENCE_TRANSITION,
                    tick=tick,
                    line=f"[tick {tick}] {subject} entered {room}.",
                )
            )
        for subject in sorted(prev_seen - now_seen):
            if subject in killed_in_room:
                # Killed in place (body visible in this room/tick): a death, not a
                # departure. The saw_body line carries the truthful testimony.
                continue
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


def _owned_task_ids(payload: Mapping[str, Any]) -> frozenset[TaskId] | None:
    """The self-state row's own unfinished map task ids, or ``None`` if unreadable.

    ``None`` means the row carries no usable ``owned_task_ids`` -- a pre-widening
    recording or a hand-built fixture -- and the caller must then mint nothing.
    """

    raw = payload.get("owned_task_ids")
    if not isinstance(raw, (tuple, list, frozenset, set)):
        return None
    if not all(isinstance(task_id, str) for task_id in raw):
        return None
    return frozenset(str(task_id) for task_id in raw)


def _completed_task_observation(
    *,
    tick: int,
    task_id: TaskId,
    room: str | None,
    observation_id: str | None,
) -> _Observation:
    """One rendered completion line, placed where the agent was when it finished."""

    completed_room = room if room is not None else "an unknown room"
    return _Observation(
        salience=_SALIENCE_COMPLETED_TASK,
        tick=tick,
        line=f"[tick {tick}] You completed {task_id} (you were in {completed_room}).",
        # The self_state row the completion was read off: one id-stamped row, so
        # the rendered line is citable.
        observation_id=observation_id,
    )


def _build_observations(
    episodic: MemoryStore,
    *,
    own_agent_id: str | None = None,
    teammate_ids: frozenset[str] = frozenset(),
) -> list[_Observation]:
    observations: list[_Observation] = []
    seen_body_ids: set[str] = set()
    last_owned_task_ids: frozenset[TaskId] | None = None
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
            room = event.payload.get("room")
            self_room = room if isinstance(room, str) else None
            owned = _owned_task_ids(event.payload)
            # One row dates the completion, places it and stamps its citation:
            # the row this iteration is reading. The line therefore carries one
            # clock, and its ``[obs ...]`` handle names the row it is placed by.
            completion_room = self_room
            # An id LEAVING a living agent's owned set is a completion it
            # performed: only completion removes an id, while redistribution
            # merely ADDS a dead player's unfinished instances to a survivor
            # and the victim receives no further packet. One line per departed
            # id, sorted, so a genuine completion is not dropped when an
            # inherited earlier-sorting task already holds the pending id, and
            # ties render in a fixed order. Role-blind: an impostor's
            # ``owned_task_ids`` is a CONSTANT per-seat camouflage window
            # (observation/service.py), so its rotating pretend id never leaves
            # the set. Both rows must carry the set -- a payload without it is
            # no evidence, so nothing is minted.
            # G-3 / C-2, audits/review-2026-08-19/D/FINAL-synthesis.md §1 RC3.
            if last_owned_task_ids is not None and owned is not None:
                observations.extend(
                    _completed_task_observation(
                        tick=event.tick,
                        task_id=task_id,
                        room=completion_room,
                        observation_id=event.observation_id,
                    )
                    for task_id in sorted(last_owned_task_ids - owned)
                )
            last_owned_task_ids = owned
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
                    observation_id=event.observation_id,
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
                    observation_id=event.observation_id,
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

        if event.type == EVENT_SAW_PLAYER_MOVE:
            obs = _render_saw_player_move(
                event,
                own_agent_id=own_agent_id,
                teammate_ids=teammate_ids,
                body_sightings=body_sightings,
            )
            if obs is not None:
                observations.append(obs)
            continue

        if event.type == EVENT_REPORTED_TESTIMONY:
            obs = _render_reported_testimony(event)
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
                        observation_id=event.observation_id,
                    )
                )

    return observations


def _coalesce_sightings(
    observations: Sequence[_Observation],
    *,
    roster: frozenset[str] | None,
    own_agent_id: str | None,
) -> list[_Observation]:
    """Fold runs of sightings that differ only by their tick into span lines.

    Bare co-presence rows are the bulk of a rendered memory and most of them
    restate the previous tick verbatim. Rows sharing a :class:`_SightingKey` on
    CONSECUTIVE ticks become one line carrying the tick range; a gap in the ticks
    or any change of room, action or companions starts a new span, so a span never
    claims a tick its rows did not. The stretch from tick 0 over which the whole
    known roster stood together becomes one summary line, and whatever each subject
    did after it keeps its own span. Every other observation class -- vents, kills,
    bodies, transitions, testimony, own rows -- passes through untouched.
    """

    grouped: dict[_SightingKey, list[_Observation]] = {}
    passthrough: list[_Observation] = []
    for obs in observations:
        if obs.sighting is None:
            passthrough.append(obs)
        else:
            grouped.setdefault(obs.sighting, []).append(obs)

    runs: list[tuple[_SightingKey, list[_Observation]]] = []
    for key, rows in grouped.items():
        run: list[_Observation] = []
        for row in sorted(rows, key=lambda obs: obs.tick):
            if run and row.tick != run[-1].tick + 1:
                runs.append((key, run))
                run = []
            run.append(row)
        runs.append((key, run))

    spawn_indices = _spawn_group_indices(runs, roster=roster, own_agent_id=own_agent_id)
    folded: list[_Observation] = []
    spawn_end = -1
    if spawn_indices:
        # The summary covers only the ticks EVERY member shares, so it never
        # outlives the group it stands for; each member's remaining ticks stay
        # its own span.
        spawn_end = min(runs[index][1][-1].tick for index in spawn_indices)
        folded.append(_spawn_group_observation(runs, spawn_indices, end_tick=spawn_end))
    consumed = frozenset(spawn_indices)
    for index, (key, rows) in enumerate(runs):
        if index in consumed:
            rows = [row for row in rows if row.tick > spawn_end]
            if not rows:
                continue
        folded.append(_span_observation(key, rows))
    return passthrough + folded


def _span_observation(key: _SightingKey, rows: list[_Observation]) -> _Observation:
    """One span line for a run, or the run's single row unchanged.

    The span sorts by its LAST tick -- a run is as current as its most recent row
    -- and cites its FIRST row's ``observation_id``, so the id a ballot can copy off
    the render is one the agent's own store holds. It carries the LAST row's
    directional breadcrumb: only a subject's most-recent sighting has one, and it
    describes the whole stay in that room.
    """

    if len(rows) == 1:
        return rows[0]
    first, last = rows[0], rows[-1]
    action = f"{key.action} " if key.action is not None else ""
    return _Observation(
        salience=first.salience,
        tick=last.tick,
        line=(
            f"You saw {key.subject} {action}in {key.room} "
            f"ticks {first.tick}-{last.tick}"
            f"{_co_presence_suffix(key.companions)}{last.sighting_suffix}."
        ),
        observation_id=first.observation_id,
        sighting=key,
        sighting_suffix=last.sighting_suffix,
    )


def _spawn_group_indices(
    runs: Sequence[tuple[_SightingKey, list[_Observation]]],
    *,
    roster: frozenset[str] | None,
    own_agent_id: str | None,
) -> list[int]:
    """The tick-0 runs that together say "everyone started in one room".

    Empty unless the runs beginning at tick 0 name the full known roster minus the
    observer, in ONE room, each listing the rest of that roster as its companions --
    the one fact the summary line states. A partial view, a split room or a subject
    the observer did not see at spawn is real information and keeps its own rows.
    How far past tick 0 the summary reaches is the caller's shared-tick arithmetic,
    not a condition on collapsing at all.
    """

    if roster is None or own_agent_id is None:
        return []
    expected = roster - {own_agent_id}
    if not expected:
        return []
    indices = [
        index
        for index, (key, rows) in enumerate(runs)
        if rows[0].tick == 0 and key.action is None and not rows[0].sighting_suffix
    ]
    keys = [runs[index][0] for index in indices]
    if len(indices) != len(expected) or {key.subject for key in keys} != expected:
        return []
    if len({key.room for key in keys}) != 1:
        return []
    if any(key.companions != expected - {key.subject} for key in keys):
        return []
    return indices


def _spawn_group_observation(
    runs: Sequence[tuple[_SightingKey, list[_Observation]]],
    indices: Sequence[int],
    *,
    end_tick: int,
) -> _Observation:
    """The single line a full-roster spawn group renders as.

    It names every subject it stands for, so the fold costs a line instead of a
    roster and loses nothing; it cites the first-listed subject's tick-0 row.
    """

    rows_by_subject = {runs[index][0].subject: runs[index][1] for index in indices}
    subjects = sorted(rows_by_subject)
    room = runs[indices[0]][0].room
    prefix = "[tick 0] " if end_tick == 0 else ""
    span = "" if end_tick == 0 else f" ticks 0-{end_tick}"
    return _Observation(
        salience=_SALIENCE_SAW_PLAYER,
        tick=end_tick,
        line=(f"{prefix}{_SPAWN_GROUP_PREFIX}{room}{span}: {', '.join(subjects)}."),
        observation_id=rows_by_subject[subjects[0]][0].observation_id,
    )


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
            observation_id=event.observation_id,
        )
    if action_str == "kill":
        return _Observation(
            salience=_SALIENCE_KILL_WITNESSED,
            tick=event.tick,
            line=(f"[tick {event.tick}] You witnessed {player_id} kill in {room}."),
            observation_id=event.observation_id,
        )
    # Task 13.9 co-presence + Task 13.6 breadcrumb suffixes, ordinary sightings
    # only (the vent/kill witnessed lines above stay clean). Co-presence ("with …")
    # lists the other subjects seen in the same room on the same tick; the
    # breadcrumb states the subject's most-recent prior room. Both are empty for a
    # solitary, non-moving subject, so that render is byte-identical to pre-13.6/9.
    companions = _co_presence_members(
        co_presence, player_id=player_id, tick=event.tick, room=room
    )
    co_present = _co_presence_suffix(companions)
    suffix = _movement_suffix_for(
        breadcrumbs, player_id=player_id, tick=event.tick, room=room
    )
    # The span key travels with the row so the coalesced render can fold runs
    # without re-reading the line it already built; it is ignored on the OFF path.
    key = _SightingKey(
        subject=player_id,
        room=room,
        action=action_str if action_str in _ACTIVE_PLAYER_ACTIONS else None,
        companions=companions,
    )
    if action_str in _ACTIVE_PLAYER_ACTIONS:
        return _Observation(
            salience=_SALIENCE_SAW_PLAYER_ACTIVE,
            tick=event.tick,
            line=(
                f"[tick {event.tick}] You saw {player_id} "
                f"{action_str} in {room}{co_present}{suffix}."
            ),
            observation_id=event.observation_id,
            sighting=key,
            sighting_suffix=suffix,
        )
    return _Observation(
        salience=_SALIENCE_SAW_PLAYER,
        tick=event.tick,
        line=f"[tick {event.tick}] You saw {player_id} in {room}{co_present}{suffix}.",
        observation_id=event.observation_id,
        sighting=key,
        sighting_suffix=suffix,
    )


def _render_saw_player_move(
    event: EpisodicEvent,
    *,
    own_agent_id: str | None = None,
    teammate_ids: frozenset[str] = frozenset(),
    body_sightings: tuple[tuple[str, int], ...] = (),
) -> _Observation | None:
    """Render one DIRECTLY-witnessed room→room transition (Task 13.5.4).

    A first-hand sighting-class line ("You saw p-3 move from CAFETERIA to ADMIN
    at tick 5"), distinct from the RECONSTRUCTED within-vision breadcrumb
    (``_collect_movement_breadcrumbs`` / ``_collect_transitions``): this is the
    single-tick transit the witness actually saw, gated upstream exactly like a
    ``saw_player`` sighting. The §4.7 firewall suppressions
    (:func:`_sighting_is_suppressed`) are mirrored from ``_render_saw_player`` so
    a self-subject move never garbles and an impostor's witnessed teammate transit
    at a kill room/tick is dropped, just as the ordinary sighting line is.

    A malformed payload (missing player / room) renders nothing, matching the
    defensive ``.get`` convention of the sibling renderers.
    """

    player_id = event.payload.get("player_id")
    from_room = event.payload.get("from_room")
    to_room = event.payload.get("to_room")
    if (
        not isinstance(player_id, str)
        or not isinstance(from_room, str)
        or not isinstance(to_room, str)
    ):
        return None
    # Suppression keys on the actor's CURRENT room (``to_room``, where the witness
    # saw it), with no active action -- the same shape ``_render_saw_player`` uses
    # for an ordinary sighting.
    if _sighting_is_suppressed(
        player_id=player_id,
        room=to_room,
        tick=event.tick,
        action=None,
        own_agent_id=own_agent_id,
        teammate_ids=teammate_ids,
        body_sightings=body_sightings,
    ):
        return None
    return _Observation(
        salience=_SALIENCE_SAW_PLAYER_MOVE,
        tick=event.tick,
        line=(
            f"[tick {event.tick}] You saw {player_id} move from "
            f"{from_room} to {to_room}."
        ),
        observation_id=event.observation_id,
    )


def _render_reported_testimony(event: EpisodicEvent) -> _Observation | None:
    """Render one ``reported_testimony`` row as a self-framed unverified claim.

    The framing is LOAD-BEARING (the §6.6 contract): every line reads
    ``[meeting {n}] CLAIM by X (unverified): …`` so a weaker model WEIGHS the
    testimony as a third party's assertion rather than treating a reported
    sighting as something it witnessed, and the tag names WHICH meeting it was
    spoken at (untagged when the agent holds no meeting record to number it by).
    The line states the claim's own tick(s) / room, while the
    :class:`_Observation` sorts by ``event.tick`` (the meeting-boundary tick) at
    :data:`_SALIENCE_REPORTED_TESTIMONY` -- above bare co-presence and
    still below every hard-evidence row.

    A malformed payload (missing speaker / subject / kind) renders nothing,
    matching the defensive ``.get`` convention of the other renderers.
    """

    speaker = event.payload.get("speaker")
    subject = event.payload.get("subject")
    kind = event.payload.get("kind")
    if (
        not isinstance(speaker, str)
        or not isinstance(subject, str)
        or not isinstance(kind, str)
    ):
        return None
    room = event.payload.get("room")
    from_tick = event.payload.get("from_tick")
    to_tick = event.payload.get("to_tick")
    meeting_index = event.payload.get("meeting_index")
    meeting_tag = "[meeting]"
    if isinstance(meeting_index, int):
        meeting_tag = f"[meeting {meeting_index}]"
    prefix = f"[tick {event.tick}] {meeting_tag} CLAIM by {speaker} (unverified):"
    if kind == "saw_vent" and isinstance(room, str) and isinstance(from_tick, int):
        body = f"saw {subject} VENT in {room} @ tick {from_tick}"
    elif kind == "saw_player" and isinstance(room, str) and isinstance(from_tick, int):
        companions = event.payload.get("co_present")
        with_suffix = ""
        if isinstance(companions, (list, tuple)) and companions:
            with_suffix = f" (with {', '.join(str(c) for c in companions)})"
        body = f"saw {subject} in {room} @ tick {from_tick}{with_suffix}"
    elif (
        kind == "alibi"
        and isinstance(room, str)
        and isinstance(from_tick, int)
        and isinstance(to_tick, int)
    ):
        body = f"{subject} was in {room} during ticks {from_tick}-{to_tick}"
    elif kind == "accusation":
        body = f"accused {subject}"
    elif kind == "corroboration" and isinstance(from_tick, int):
        body = f"backed {subject}'s account @ tick {from_tick}"
    else:
        return None
    return _Observation(
        salience=_SALIENCE_REPORTED_TESTIMONY,
        tick=event.tick,
        line=f"{prefix} {body}.",
        # A reported-testimony event carries no observation id (it is not first-hand
        # perception), so this threads ``None`` naturally (Task 16.5).
        observation_id=event.observation_id,
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
    return _Observation(
        salience=salience,
        tick=event.tick,
        line=line,
        observation_id=event.observation_id,
    )


def _record_last_seen_sightings(
    episodic: MemoryStore,
    working: WorkingMemory,
    *,
    own_agent_id: str | None,
    teammate_ids: frozenset[str],
    body_sightings: tuple[tuple[str, int], ...],
) -> None:
    """Record each subject's LATEST non-suppressed first-hand sighting as last-seen.

    The §6.6 render reads ``working.last_seen`` for the belief row's "last seen in
    ROOM at tick T" (the R-6 composite-memory gate), so this writer fills it with
    the freshest thing the agent actually saw: a witnessed room→room transition
    contributes its ``to_room``, an ordinary look contributes its ``room``, and
    the later tick wins. That makes the rendered suffix the argmax over the
    agent's own log, so it cannot contradict an observation printed above it in
    the same prompt.

    Folding ordinary looks in is gated by :func:`last_seen_from_sightings_enabled`;
    OFF the writer reads witnessed transitions alone, which is the derivation the
    committed prompt bytes were recorded under.

    The §4.7 firewall applies to every row with that row's OWN action
    (:func:`_sighting_is_suppressed`, as the sighting render applies it): a
    self-subject row, and -- for an impostor -- a teammate carrying a ``kill``
    action or standing in a kill-window body room, are skipped, so the suffix can
    never reintroduce the teammate-at-scene own-goal the sighting line itself
    suppresses.

    IDEMPOTENT across the repeated renders a meeting drives (a refreshed turn, a
    vote prompt, the per-turn re-render): ``working.last_seen`` persists between
    renders, so a row whose tick is NOT after the player's already-recorded
    last-seen is skipped -- re-processing the same rows never trips
    :meth:`WorkingMemory.record_sighting`'s non-decreasing-tick guard.

    Events arrive in append order with non-decreasing ticks, and within one tick
    perception appends visible players before moved players, so a plain
    last-write-wins pass yields the argmax without sorting and settles the
    same-tick tie on the transition -- the row that also states where the subject
    came from.
    """

    fold_ordinary_sightings = last_seen_from_sightings_enabled()
    for event in episodic.recent(since_tick=0):
        action: str | None
        if event.type == EVENT_SAW_PLAYER_MOVE:
            player_id = event.payload.get("player_id")
            room = event.payload.get("to_room")
            action = None
        elif fold_ordinary_sightings and event.type == _EVENT_SAW_PLAYER:
            player_id = event.payload.get("player_id")
            room = event.payload.get("room")
            raw_action = event.payload.get("action")
            action = raw_action if isinstance(raw_action, str) else None
        else:
            continue
        if not isinstance(player_id, str) or not isinstance(room, str):
            continue
        if _sighting_is_suppressed(
            player_id=player_id,
            room=room,
            tick=event.tick,
            action=action,
            own_agent_id=own_agent_id,
            teammate_ids=teammate_ids,
            body_sightings=body_sightings,
        ):
            continue
        previous = working.last_seen(player_id)
        if previous is not None and event.tick < previous.tick:
            # A re-render replays older rows into a ``last_seen`` that already
            # holds a later tick; recording the older one would trip the
            # backwards-tick guard. Skipping it leaves the latest-per-subject
            # value, so repeated renders are stable.
            continue
        working.record_sighting(player_id=player_id, room=room, tick=event.tick)


def _build_belief_lines(
    beliefs: BeliefState,
    working: WorkingMemory,
    *,
    roster: frozenset[str] | None = None,
    suspicion_override: Mapping[PlayerId, float] | None = None,
) -> list[str]:
    """Render the §6.6 belief rows, filtered to ``roster`` when supplied.

    ``roster`` is the engine-witnessed player-id set
    (:func:`_known_roster_ids`): a belief row outside it is a phantom
    subject (audit gp-6 C-C-8 -- e.g. a turn id materialised as a player
    row) and is skipped rather than rendered into the prompt. ``None``
    renders every known row (legacy fixtures without the 9.3 self
    channel, where the roster is underivable).

    ``suspicion_override`` (Task 13.5.5) supplies a per-player effective
    suspicion that replaces ``belief.suspicion`` in the rendered score; a
    player absent from the mapping falls back to its stored suspicion. Only
    the suspicion number is overridden -- trust, alibis, last-seen, and
    contradictions still read from ``beliefs`` -- because the meeting's
    ``suspicion_graph`` it mirrors is suspicion-only. ``None`` is
    byte-identical to pre-task HEAD.

    A row whose stored scalar is used (no override for that player) and whose
    typed provenance is entirely soft renders clamped to
    :data:`~agents.memory.beliefs.HARD_EVIDENCE_GATE_RENDER_CEIL`, just below the
    §4.6 gate; a hard-backed row renders untouched.

    Reads ``working.last_seen`` for the last-seen suffix (the R-6
    composite-memory gate: render reads all three stores). The field is filled by
    :func:`_record_last_seen_sightings` from the agent's own sighting rows
    (firewall-suppressed).
    """

    lines: list[str] = []
    for player_id in sorted(beliefs.known_players()):
        if roster is not None and player_id not in roster:
            continue
        belief = beliefs.view(player_id)
        effective_suspicion = (
            suspicion_override.get(player_id, belief.suspicion)
            if suspicion_override is not None
            else None
        )
        # The J1 render clamp. TWO halves: (1) the STORED-scalar clamp --
        # when this row renders its own ``belief.suspicion`` (no override, or the
        # player is absent from the override mapping) an entirely-soft
        # conviction-grade scalar is clamped sub-gate. (2) an override VALUE passes
        # through UNTOUCHED: it is the post-fold scalar from the already-clamped
        # pipeline (the builder clamped the seed before the manager pre-vote fold),
        # so clamping it again against the STORED provenance would misclassify a row
        # that took fresh HARD lift this meeting. Prose and graph therefore read one
        # clamped source by construction.
        if suspicion_override is None or player_id not in suspicion_override:
            effective_suspicion = hard_evidence_gated_suspicion(
                belief.suspicion, belief.provenance
            )
        belief_text = _format_belief_score(belief, suspicion=effective_suspicion)
        # The "last seen in ROOM at tick T" suffix: the subject's latest
        # non-suppressed first-hand sighting, filled into ``working.last_seen`` by
        # :func:`_record_last_seen_sightings`. Absent for a subject the agent
        # never saw.
        last_seen_suffix = _format_last_seen_suffix(working.last_seen(player_id))
        # alibi_map render (Task 13.5.2): the now-populated ``PlayerBelief.alibis``
        # list, written by :func:`absorb_reported_testimony` from each public
        # ``AlibiClaim``. Empty (so this is the empty string) for a subject
        # never alibied.
        alibi_suffix = _format_alibi_suffix(belief.alibis)
        parentheticals = [s for s in (last_seen_suffix, alibi_suffix) if s]
        if belief_text is None and not parentheticals:
            continue
        if belief_text is None:
            # Neutral suspicion but a recorded alibi (a subject named only in
            # reported testimony): lead the row with the alibi content so the
            # alibi map still surfaces.
            lines.append(f"{player_id}: {'; '.join(parentheticals)}")
        elif parentheticals:
            lines.append(f"{player_id}: {belief_text} ({'; '.join(parentheticals)})")
        else:
            lines.append(f"{player_id}: {belief_text}")
    return lines


def _format_alibi_suffix(alibis: tuple[AlibiClaim, ...]) -> str:
    """Render a subject's recorded alibi claims for the §6.6 belief view (Task 13.5.2).

    Empty for a subject with no recorded alibi, so that subject's belief line
    carries no suffix. Claims are sorted by ``(tick, room, source)`` for replay
    determinism; each renders as ``in ROOM at tick T per SPEAKER`` so the alibi
    stays attributed to the player who asserted it.
    """

    if not alibis:
        return ""
    # Cap the rendered alibis per subject so the non-elastic §6.6 belief block
    # cannot grow unbounded across many meetings and push the budgeted render over
    # ``DEFAULT_TOKEN_BUDGET`` (Codex P2): keep the most-recent
    # ``_MAX_RENDERED_ALIBIS`` by tick (a newer alibi supersedes a stale one),
    # then render oldest-first for a stable, replay-deterministic line.
    ordered = sorted(alibis, key=lambda a: (a.tick, a.room, a.source))
    if len(ordered) > _MAX_RENDERED_ALIBIS:
        recent = sorted(ordered, key=lambda a: (a.tick, a.room, a.source))[
            -_MAX_RENDERED_ALIBIS:
        ]
        ordered = recent
    parts = [
        f"in {alibi.room} at tick {alibi.tick} per {alibi.source}" for alibi in ordered
    ]
    return "alibi: " + "; ".join(parts)


def _format_belief_score(
    belief: PlayerBelief, *, suspicion: float | None = None
) -> str | None:
    # Task 13.5.5: ``suspicion`` overrides the stored value when supplied (the
    # pre-vote-folded number the ballot's ``suspicion_graph`` carries), so the
    # neutral test, the suspicion-vs-trust comparison, AND the rendered figure
    # all read the folded suspicion. ``None`` -> stored value, byte-identical.
    effective_suspicion = belief.suspicion if suspicion is None else suspicion
    suspicion_dev = abs(effective_suspicion - 0.5)
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
        return f"suspicion {effective_suspicion:.2f}"
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
    meeting_lines: Sequence[str],
    trail_spans: Sequence[_SelfLocationSpan],
    trail_truncated: bool,
    token_budget: int,
) -> str:
    """Assemble the final Markdown view, enforcing token budget on observations.

    The role line, tasks-completed line, the meeting record, beliefs, and
    contradictions are treated as fixed (always rendered) because they are
    essential context. Observations are the elastic section: they fill the
    remaining budget, dropped from lowest salience first if the budget is tight.

    ``meeting_lines`` is one line per concluded meeting and joins the NON-elastic
    set deliberately: the record of what a meeting decided is what stops a long
    game re-prosecuting a closed case, so a tight budget must shed observations
    around it rather than shed it.

    ``trail_spans`` (the self-location route, oldest first) is capped upstream and
    charged before the observations as ONE chained line, then shed OLDEST-first if
    even the capped route does not fit, so the trail can never overflow the budget
    onto the observations. Whenever any span was dropped -- by the cap or by that
    shedding -- the block says so.

    The budget arithmetic charges every character that lands in the
    final output, including the Markdown separators (``"\\n\\n"`` between
    blocks and the trailing ``"\\n"``), so the rendered view's actual
    token estimate cannot exceed ``token_budget``.
    """

    fixed_lines: list[str] = [f"## Your role: {role}"]
    if tasks_summary is not None:
        fixed_lines.append(f"## Tasks completed (global): {tasks_summary}")

    meetings_block: list[str] = []
    if meeting_lines:
        meetings_block.append(_MEETINGS_HEADER)
        meetings_block.extend(f"- {line}" for line in meeting_lines)

    beliefs_block: list[str] = []
    if beliefs_lines:
        beliefs_block.append("## Your current beliefs:")
        beliefs_block.extend(f"- {line}" for line in beliefs_lines)

    contradictions_block: list[str] = []
    if contradiction_lines:
        contradictions_block.append("## Open contradictions:")
        contradictions_block.extend(f"- {line}" for line in contradiction_lines)

    non_elastic_blocks: list[list[str]] = [fixed_lines]
    if meetings_block:
        non_elastic_blocks.append(meetings_block)
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
    # The route is charged first, capped and shed oldest-first: it is the one
    # block the meeting's roll-call is answered from, and the observations below
    # it are the elastic section by construction.
    trail_block, trail_cost = _select_trail_within_budget(
        spans=trail_spans,
        truncated=trail_truncated,
        budget=remaining,
    )
    remaining -= trail_cost

    kept: list[_Observation] = []
    if remaining >= header_cost:
        kept = _select_within_budget(
            observations=observations,
            budget=remaining - header_cost,
        )

    if not trail_block and not kept:
        return non_elastic_text

    blocks: list[list[str]] = [fixed_lines]
    if meetings_block:
        blocks.append(meetings_block)
    if trail_block:
        blocks.append(trail_block)
    if kept:
        observation_block = [observations_header]
        observation_block.extend(f"- {obs.line}" for obs in kept)
        blocks.append(observation_block)
    if beliefs_block:
        blocks.append(beliefs_block)
    if contradictions_block:
        blocks.append(contradictions_block)

    return "\n\n".join("\n".join(block) for block in blocks) + "\n"


def _select_trail_within_budget(
    *,
    spans: Sequence[_SelfLocationSpan],
    truncated: bool,
    budget: int,
) -> tuple[list[str], int]:
    """The trail block that fits ``budget``, shedding OLDEST spans first.

    The recent route is the part a roll-call answer is copied from, so a tight
    budget keeps it and drops the far end; an empty block costing nothing is
    returned when not even one span fits. Costs are charged piece by piece exactly
    as the observations block charges its own header and bullets, so the two
    blocks cannot disagree about what a line costs.
    """

    if not spans:
        return [], 0
    header_cost = _estimate_tokens("\n\n" + _TRAIL_HEADER)
    notice_cost = _estimate_tokens("\n- " + _TRAIL_TRUNCATED_LINE)
    for first in range(len(spans)):
        # Any span dropped -- by the cap upstream or by this shedding -- is stated.
        shed = truncated or first > 0
        route = _trail_route_line(spans[first:])
        cost = (
            header_cost
            + (notice_cost if shed else 0)
            + _estimate_tokens("\n- " + route)
        )
        if cost > budget:
            continue
        block = [_TRAIL_HEADER]
        if shed:
            block.append(f"- {_TRAIL_TRUNCATED_LINE}")
        block.append(f"- {route}")
        return block, cost
    return [], 0


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
    "MeetingHistory",
    "MemoryStore",
    "PlayerBelief",
    "PlayerId",
    "ReportedStatement",
    "RoomId",
    "SELF_LOCATION_TRAIL_MAX_SPANS",
    "TaskId",
    "WorkingMemory",
    "absorb_meeting_evidence",
    "absorb_reported_testimony",
    "record_meeting_outcome",
    "render_for_prompt",
]
