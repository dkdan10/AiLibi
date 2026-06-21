"""Sanitized spectator DTOs for the replay viewer API (DESIGN.md §7, §11.4).

These models are the *only* shapes the Phase 4 frontend consumes. They
deliberately shadow engine / meetings / orchestrator internal types rather
than re-export them: the spectator API is a separate surface from the
observation firewall (DESIGN.md §1.3), but it must never embed a raw
``WorldState``, ``ReplayEntry``, or meeting-internal type, because doing so
would couple the frontend to engine shape and re-introduce leakage paths via
copy-paste.

**Privilege model.** The replay viewer is a *post-game* privileged spectator
(the "GM view" analog). Role, kill attribution, vent usage, and impostor-only
state are intentionally exposed — that is what makes a replay watchable. The
leak test in ``tests/api/test_leak.py`` does not redact those fields; it
asserts every field here is *intentional* by pinning the DTO inventory and
forbidding internal types in field annotations.

Every model is frozen and forbids extra fields. ``tuple[X, ...]`` is used for
collections (immutability matching the engine/meetings pattern); Pydantic v2
serializes tuples as JSON arrays, so the frontend sees plain arrays.
Discriminated unions mirror ``meetings.schemas`` and use
``Field(discriminator="type")``.

The three discriminated-union aliases (``TickEventView``,
``ObservationClaimView``, ``StatementClaimView``) are public, importable
module symbols but are intentionally excluded from ``__all__`` / the DTO
inventory: they are compositions of already-inventoried DTOs, not standalone
DTOs. The leak test's ``EXPECTED_DTOS`` fixture therefore lists only the
concrete models.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Annotated, Final, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

# Versioned view-model contract (Phase 12, Task 12.2; DESIGN.md §7). The served
# payload carries this so the frontend can fail loud on an incompatible
# contract rather than silently mis-rendering a drifted shape. Bumped only on a
# breaking shape change; additive projections do NOT bump it. Kept a plain
# string (not semver) so a future minor revision ("1.1") is representable
# without retyping the field. ``frontend/src/types/api.ts`` is generated from
# these models (no hand-mirror), so DTO ↔ TS cannot drift.
VIEW_MODEL_VERSION: Final[str] = "1"


class _FrozenView(BaseModel):
    """Base for every spectator DTO: frozen, extra fields rejected."""

    model_config = ConfigDict(frozen=True, extra="forbid")


# ---------------------------------------------------------------------------
# Map + roster DTOs (loaded once, shared across all replays)
# ---------------------------------------------------------------------------


class PositionView(_FrozenView):
    """Shadows ``engine.world.Position`` (widened from int to float for the
    renderer)."""

    x: float
    y: float


class SizeView(_FrozenView):
    """Shadows ``engine.world.Size`` (widened from int to float for the
    renderer)."""

    width: float
    height: float


class RoomView(_FrozenView):
    """Shadows ``engine.world.Room``.

    Excludes: ``kind``, ``notes``, visibility defaults, and any internal task
    slot indices — the spectator only needs geometry and a label.
    """

    id: str
    name: str
    position: PositionView
    size: SizeView


class VentView(_FrozenView):
    """Shadows ``engine.world.Vent`` (the vent network for impostor routes).

    Excludes: nothing material — the vent shape is already minimal. The
    source's ``traversal_ticks`` is dropped (not needed for rendering).
    """

    id: str
    room_id: str
    connected_room_ids: tuple[str, ...]


class EdgeView(_FrozenView):
    """Shadows ``engine.world.Edge`` (room adjacency, for door rendering).

    Excludes: ``kind`` and ``traversal_ticks``; ``is_door`` flattens the
    door/hallway distinction the renderer needs.
    """

    from_room_id: str
    to_room_id: str
    is_door: bool


class MapLayoutView(_FrozenView):
    """The static map geometry shared across every replay.

    Excludes: task definitions — task completion is surfaced per-tick in
    ``TickView`` and per-agent in ``AgentMemoryView`` instead.
    """

    rooms: tuple[RoomView, ...]
    vents: tuple[VentView, ...]
    edges: tuple[EdgeView, ...]


class PlayerView(_FrozenView):
    """Shadows the static identity slice of ``engine.entities.PlayerState``.

    ``role`` is intentionally exposed: the spectator is privileged. ``color``
    is a render hint assigned deterministically from ``agent_id``.

    Excludes: all dynamic state (position, alive, cooldowns, current action) —
    those live in ``AgentTickStateView`` so they vary per tick.
    """

    agent_id: str
    display_name: str
    role: Literal["CREWMATE", "IMPOSTOR"]
    color: str


# ---------------------------------------------------------------------------
# Per-tick state DTOs
# ---------------------------------------------------------------------------


class VisiblePlayerView(_FrozenView):
    """One other player inside an agent's firewall-filtered field of view at a
    tick (Task 12.3; DESIGN.md §3.2 fog, §1.3 firewall).

    Shadows the AGENT-facing ``observation.packet.PlayerView`` — ``id`` / ``room``
    / ``action`` only — NOT the privileged spectator :class:`PlayerView` (which
    carries ``role`` / ``color``). That is the whole point of the As-agent
    perspective: it *simulates* the firewall, so a sighting never leaks role,
    kill attribution, or identity colour. ``action`` is a witnessed kill / vent
    (the engine's witness gate is what permits it — ``eval/leak_test.py``) and is
    ``None`` for an ordinary co-located sighting.
    """

    id: str
    room: str
    action: str | None


class VisibleBodyView(_FrozenView):
    """One body inside an agent's field of view at a tick (Task 12.3; DESIGN.md
    §3.2 fog, §1.3 firewall).

    Shadows the AGENT-facing ``observation.packet.BodyView`` — ``id`` / ``room``
    / ``victim_id`` only. The privileged kill attribution (``killed_by``, carried
    by the spectator :class:`BodyView`) is deliberately ABSENT: the As-agent view
    must never expose who killed whom — only that a body is visible and whose it
    is (the UI leak test in ``tests/api/test_leak.py`` pins this).
    """

    id: str
    room: str
    victim_id: str


class AudibleEventView(_FrozenView):
    """One audio cue inside an agent's field of view at a tick (Task 12.3;
    DESIGN.md §3.2, §4.2).

    Shadows ``observation.packet.AudibleEvent`` — the SEPARATE audio firewall
    channel (``observation.service.ObservationService._audible_events``), distinct
    from the visual field: ``vent_use_heard`` (an impostor vent heard from the
    source / destination room) or ``sabotage_alarm`` (the global alarm, ``room``
    is ``None``).
    """

    kind: Literal["vent_use_heard", "sabotage_alarm"]
    room: str | None


class AgentVisibilityView(_FrozenView):
    """One living agent's per-tick field of view — the As-agent fog projection
    (Task 12.3; DESIGN.md §3.2 fog, §7 visibility row, §1.3 firewall).

    Captured from the agent's already-firewall-filtered ``ObservationPacket``
    (``observation.service.ObservationService.build_packet``) re-built during the
    loader's engine re-walk — the SAME pipeline ``eval/leak_test.py`` validates —
    so the As-agent perspective *simulates* the firewall rather than the renderer
    hiding data client-side. It carries only what the agent could perceive at this
    tick: the visual field (``visible_players`` / ``visible_bodies``, graph- and
    lights-dependent, from ``engine.visibility.compute_visibility_for_player``)
    and the audio field (``audible_events``). It is the ONE genuinely-expensive
    per-tick projection (a visibility solve per living agent per tick, stage-0
    §0.5), so it is derived once inside the LRU-cached re-walk, never per request.

    Attached to ``AgentTickStateView.visibility``; ``None`` there for a dead agent
    (a dead agent has no field of view — there is no As-agent fog to simulate).
    The privileged self channel (``role`` / ``fellow_impostor_ids`` / ``cooldown``
    / ``own_kill`` / ``pending_task_id``) is intentionally NOT projected here:
    those are exactly the fields the As-agent view must hide.
    """

    visible_players: tuple[VisiblePlayerView, ...]
    visible_bodies: tuple[VisibleBodyView, ...]
    audible_events: tuple[AudibleEventView, ...]


class AgentTickStateView(_FrozenView):
    """The dynamic slice of one agent's ``engine.entities.PlayerState`` at one
    tick.

    ``is_venting`` is impostor-only state, exposed because the spectator is
    privileged. ``task_progress`` is ``None`` for impostors.

    ``visibility`` is the agent's per-tick field of view — the As-agent fog
    projection (Task 12.3; DESIGN.md §3.2, §7). It is ``None`` for a dead agent
    (no field of view) and populated for every living agent. This is the one
    genuinely-expensive per-tick projection, derived from the firewall-filtered
    observation packet inside the cached re-walk (see :class:`AgentVisibilityView`).
    It defaults to ``None`` so hand-constructed instances and the (visibility-free)
    meeting-memory re-walk stay valid; the served replay path always sets it.

    Excludes: ``target_room``, ``planned_path``, ``kill_cooldown_ticks``,
    ``vent_cooldown_ticks`` — engine-internal tactical state.
    """

    agent_id: str
    room_id: str | None
    is_alive: bool
    is_venting: bool
    task_progress: float | None
    current_action: Literal[
        "IDLE", "MOVING", "TASK", "KILL", "VENT", "REPORT", "SABOTAGE"
    ]
    visibility: AgentVisibilityView | None = None


class KillEventView(_FrozenView):
    """Projects ``engine.events.KilledEvent`` (privileged kill attribution)."""

    type: Literal["kill"]
    tick: int
    killer_id: str
    victim_id: str
    room_id: str


class ReportBodyEventView(_FrozenView):
    """Projects the engine body-report event that opens a meeting
    (``engine.events``)."""

    type: Literal["report_body"]
    tick: int
    reporter_id: str
    body_of: str
    room_id: str


class SabotageEventView(_FrozenView):
    """Projects ``engine.events.SabotageStartedEvent`` (DESIGN.md §8.3): the
    visibility-degrading ``lights`` and the task-gating ``reactor`` (Task 11.5),
    so the contestable-clock win shape is observable on the public timeline."""

    type: Literal["sabotage"]
    tick: int
    kind: Literal["lights", "reactor"]
    room_id: str | None
    actor_id: str


class TaskCompletedEventView(_FrozenView):
    """Projects ``engine.events.TaskCompletedEvent``."""

    type: Literal["task_completed"]
    tick: int
    agent_id: str
    task_id: str
    room_id: str


class MeetingTriggeredEventView(_FrozenView):
    """Projects ``engine.events.MeetingTriggeredEvent``."""

    type: Literal["meeting_triggered"]
    tick: int
    meeting_id: str
    triggered_by: str
    trigger_kind: Literal["body", "emergency"]


class VentEventView(_FrozenView):
    """Projects ``engine.events.VentEnteredEvent`` / ``VentExitedEvent`` — the
    Phase-11 impostor deception lever made observable (DESIGN.md §3.2, §7).

    The engine already emits both endpoints with the source/destination rooms
    and ``traversal_ticks``, but only an ``is_venting`` bool survived into the
    per-tick DTO, so the map renderer could only blink the token in/out. This
    projection carries the full dive→travel→emerge so the map stage (Task 12.5)
    can animate the route along ``MapLayoutView.vents``. ``phase`` is ``enter``
    (dive) for ``VentEntered`` and ``exit`` (emerge) for ``VentExited``;
    ``from_room_id`` / ``to_room_id`` are the engine's ``source_room`` /
    ``destination_room``. The per-vent witness sets are intentionally NOT
    projected here — vent witnessing is the agent-facing firewall channel and
    is reconstructed by the Task 12.3 per-tick visibility projection, not the
    spectator timeline.
    """

    type: Literal["vent"]
    tick: int
    actor_id: str
    phase: Literal["enter", "exit"]
    from_room_id: str
    to_room_id: str
    traversal_ticks: int


TickEventView: TypeAlias = Annotated[
    KillEventView
    | ReportBodyEventView
    | SabotageEventView
    | TaskCompletedEventView
    | MeetingTriggeredEventView
    | VentEventView,
    Field(discriminator="type"),
]


class BodyView(_FrozenView):
    """Persistent body marker projected from ``engine.world.WorldState.bodies``
    (DESIGN.md §3.2, §7).

    ``KillEventView`` carries the kill attribution at the instant of the kill;
    this projection re-states a body on the floor at EVERY tick it persists, so
    the map can keep the marker (and its attribution) until the body is reported.
    ``killed_by`` is the privileged SPECTATOR attribution (the killer's id),
    which the agent-facing ``BodyView`` in ``observation/`` deliberately omits —
    the spectator surface is privileged, so it is re-exposed here.
    """

    body_id: str
    victim_id: str
    room_id: str
    killed_by: str


class SabotageDetailView(_FrozenView):
    """The active sabotage's per-room repair race + countdown, projected from the
    re-walked ``engine.entities.SabotageState`` (DESIGN.md §3.2, §8.3, §7).

    ``remaining_ticks`` is the gating-reactor countdown (SPECTATOR-privileged;
    firewalled from agents). ``repair_progress`` maps each repair room to ticks
    of repair already applied, so the map can render the genuine multi-room
    repair race the ``lights``/``reactor`` sabotages drive — none of which was
    in any DTO before (only the kind survived, via ``TickView.sabotage_active``).
    """

    kind: Literal["lights", "reactor"]
    remaining_ticks: int
    affected_rooms: tuple[str, ...]
    repair_progress: Mapping[str, int]


class AdvantageView(_FrozenView):
    """Per-tick crew-vs-impostor advantage, derived from re-walked state
    (DESIGN.md §4, §7) — the data behind the advantage graph / second scrubber.

    The component counts are authoritative; ``advantage`` is a single rendering
    heuristic in ``[-1, 1]`` (positive favours the crew). It blends the crew
    task clock (``tasks_completed / tasks_required``) against impostor parity
    pressure (``impostors_alive / max(crew_alive, 1)``) and is clamped — see
    ``api.replay_loader._advantage_view`` for the exact formula. Consumers that
    want a different curve re-derive it from the counts.

    Two task denominators, on purpose (DESIGN.md §4; Phase-12 close-audit):
    ``tasks_required`` is the LIVE win-condition denominator — ``len(state.tasks)``
    this tick, which shrinks as crewmates die and their task instances leave the
    pool (a crewmate dying mid-game made the roster meter read "7/10" after
    "0/14", a misleading shrink). ``tasks_required_total`` is the FIXED
    game-start instance count (``len(initial_state.tasks)``), the SAME for every
    tick of a game. The advantage curve keeps using the live ``tasks_required``;
    the roster DISPLAY meter divides by the fixed ``tasks_required_total`` so its
    denominator and bar are stable + monotonic.
    """

    crew_alive: int
    impostors_alive: int
    tasks_completed: int
    tasks_required: int
    tasks_required_total: int
    advantage: float


class TickView(_FrozenView):
    """One reconstructed tick of a replay.

    ``tasks_completed_total`` / ``tasks_required_total`` count completed vs.
    total per-player task *instances* across all players (DESIGN.md §3.2): the
    denominator is the live instance count, NOT bounded by the map's task pool
    (e.g. 14 instances at the canonical 9p/2i, ``tasks_per_crewmate=2``, over the
    12 map tasks). Both stay ``int``.

    Excludes: state hashes, raw engine actions, and raw per-tick replay
    records — those are reconstruction inputs, not spectator data.
    """

    tick: int
    agent_states: tuple[AgentTickStateView, ...]
    events: tuple[TickEventView, ...]
    sabotage_active: tuple[str, ...]
    tasks_completed_total: int
    tasks_required_total: int
    # Additive Phase-12 projections, all from already-re-walked state (DESIGN.md
    # §7). ``bodies`` re-states every body on the floor this tick (persistent
    # attribution); ``sabotage`` is the active sabotage's repair race + countdown
    # (``None`` when no sabotage is active); ``advantage`` is the crew/impostor
    # advantage frame for the §4 advantage graph.
    bodies: tuple[BodyView, ...]
    sabotage: SabotageDetailView | None
    advantage: AdvantageView


# ---------------------------------------------------------------------------
# Meeting DTOs (mirror ``meetings.schemas`` with deliberate field re-exposure)
# ---------------------------------------------------------------------------


class SawPlayerView(_FrozenView):
    """Shadows ``meetings.schemas.SawPlayerObservation``."""

    type: Literal["saw_player"]
    tick: int
    subject: str
    room: str
    co_present: tuple[str, ...]


class CompletedTaskObsView(_FrozenView):
    """Shadows ``meetings.schemas.CompletedTaskObservation``."""

    type: Literal["completed_task"]
    tick: int
    task_id: str
    room: str


class FoundBodyObsView(_FrozenView):
    """Shadows ``meetings.schemas.FoundBodyObservation``."""

    type: Literal["found_body"]
    tick: int
    body_of: str
    room: str


ObservationClaimView: TypeAlias = Annotated[
    SawPlayerView | CompletedTaskObsView | FoundBodyObsView,
    Field(discriminator="type"),
]


class AlibiClaimView(_FrozenView):
    """Shadows the ``alibi`` variant of ``meetings.schemas.Claim``."""

    type: Literal["alibi"]
    subject: str
    from_tick: int
    to_tick: int
    room: str
    evidence: tuple[str, ...]


class AccusationClaimView(_FrozenView):
    """Shadows the ``accusation`` variant of ``meetings.schemas.Claim``."""

    type: Literal["accusation"]
    against: str
    confidence: float
    reason: str


class CorroborationClaimView(_FrozenView):
    """Shadows the ``corroboration`` variant of ``meetings.schemas.Claim``."""

    type: Literal["corroboration"]
    supports: str
    on_tick: int
    reason: str


StatementClaimView: TypeAlias = Annotated[
    AlibiClaimView | AccusationClaimView | CorroborationClaimView,
    Field(discriminator="type"),
]


class TurnView(_FrozenView):
    """Shadows ``meetings.schemas.MeetingTurn`` (one turn in the §5.2 chain).

    A turn carries the speaker's structured ``observations`` (with tick
    references) and ``claims`` (alibi / accusation / corroboration) plus the
    free-text argument. ``turn_kind`` is ``opening`` (turn 0 — the
    body-reporter / emergency caller states findings and accuses or declares
    unsure), ``reply`` (the accused responds, ``reply_to`` set to the accusing
    turn's ``turn_id``), or ``opt_in`` (a terminal info-share turn from a
    relevant non-speaker). ``turn_id`` is ``"{meeting_id}:turn-{turn_index}"``
    and is what ``BallotView.primary_reason_id`` references.

    The old parallel ``ReportView`` / ``StatementView`` split folds into this
    single turn shape (Task 8.7/8.10): the opening turn carries the former
    report's ``found_body`` / ``saw_player`` observations, and every turn
    carries its claims — there is no separate report list and no "round".
    """

    turn_id: str
    turn_index: int
    speaker: str
    turn_kind: Literal["opening", "reply", "opt_in"]
    reply_to: str | None
    observations: tuple[ObservationClaimView, ...]
    claims: tuple[StatementClaimView, ...]
    free_text: str
    # True when this (emergency) opening had a fabricated found_body
    # deterministically stripped (meetings.manager ``EMERGENCY_BODY_STRIP_MARKER``,
    # parsed off ``free_text`` at load). The transcript renders a role-neutral
    # "FABRICATED" chip instead of the raw dev-jargon marker (DESIGN.md §3.4, §5.5).
    fabricated_opening: bool


class ContradictionView(_FrozenView):
    """Shadows ``meetings.schemas.ContradictionRef`` (a flagged contradiction).

    ``weak`` / ``severity`` lift the detector's weak-vs-strong classification out
    of the free-text ``description`` marker into a structured field (DESIGN.md
    §3.4, §7). Weakness is a substring marker in ``description``
    (``meetings.transcript.WEAK_CONTRADICTION_MARKER_PREFIX``); the loader
    re-derives the class at load via ``meetings.transcript.is_weak_contradiction``
    (imported, never re-implemented) so the meeting view can draw weak=dashed /
    strong=solid links without re-parsing the string client-side. Belief Rule 2
    keys its graduated down-weight on the same predicate, so the two cannot
    drift.
    """

    contradiction_id: str
    kind: Literal["alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical"]
    event_a_id: str
    event_b_id: str
    subjects: tuple[str, ...]
    description: str
    weak: bool
    severity: Literal["weak", "strong"]


class BallotView(_FrozenView):
    """Shadows ``meetings.schemas.VoteBallot``.

    ``target`` flattens ``str | Literal["SKIP"]`` to a plain ``str`` ("SKIP"
    or a player id) for JSON simplicity.

    ``rewrite_reasons`` / ``rationale_text_clean`` parse the firewall/parse
    audit markers the meeting layer prepends to ``rationale_text`` (DESIGN.md
    §3.4, §7) into structured chips + the model-authored remainder. The loader
    matches the markers by IMPORTING the constants from ``meetings.voting`` and
    ``meetings.manager`` (never hard-coding the literals, which are
    ``.format()``-interpolated), so a marker rename cannot silently break the
    parse. ``VOTE_PARSE_DEFAULT`` is special-cased: it is the WHOLE
    ``rationale_text`` (the model authored nothing), so ``rationale_text_clean``
    is empty for it. See ``api.replay_loader._parse_rewrite_reasons``.
    """

    voter: str
    target: str
    confidence: float
    primary_reason_id: str | None
    considered_alternatives: tuple[str, ...]
    rationale_text: str
    rewrite_reasons: tuple[str, ...]
    rationale_text_clean: str


class LLMCallView(_FrozenView):
    """Shadows ``orchestrator.replay.LLMCallRecord``.

    ``prompt_template_id`` is derived from the ``prompt_versions`` lookup.
    ``agent_id`` is the originating game-agent (the speaker for meeting
    calls); ``None`` for system-level calls or replays recorded before the
    field existed.
    """

    call_kind: Literal["meeting", "trigger"]
    model: str
    prompt_template_id: str
    prompt_text: str
    response_text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    agent_id: str | None


class GateView(_FrozenView):
    """The per-meeting §4.6 verdict, recomputed from the persisted ballots
    (DESIGN.md §3.4, §4.6, §7).

    The real rule (``meetings.voting.tally_ballots``) is **plurality + at least
    one leader ballot with ``confidence >= threshold`` (0.6), tie or
    SKIP-plurality → SKIPPED** — NOT a vote-count majority, and NOT the
    template-time ``rendered_max`` (which is transient and only persisted on
    failed calls, so it is intentionally dropped). ``leader`` is the sole
    non-SKIP plurality leader (the ejection candidate) or ``None`` when SKIP
    won, the leaders tied, or there were no ballots; ``leader_max_confidence`` is
    that leader's strongest ballot (``0.0`` when there is no leader); ``passed``
    is ``True`` iff the gate ejects (``leader is not None`` and
    ``leader_max_confidence >= threshold``). ``passed`` therefore mirrors the
    meeting's recorded outcome and ``leader`` its ``ejected_player_id`` — pinned
    by the consistency test in ``tests/api/test_view_model.py``.
    """

    leader: str | None
    leader_max_confidence: float
    threshold: float
    passed: bool


class MeetingView(_FrozenView):
    """Shadows ``orchestrator.replay.MeetingReplayEntry``.

    ``trigger_kind`` is derived from the source meeting trigger. ``outcome``
    and ``ejected_player_id`` are coupled (EJECTED <=> non-null id).
    ``total_cost_usd`` is the sum of ``llm_calls[*].cost_usd``. ``gate`` is the
    per-meeting §4.6 verdict recomputed from ``ballots`` (see :class:`GateView`).

    ``turns`` is the single ordered transcript of the reactive accusation
    chain (DESIGN.md §5.2): opening turn, then the reactive ``reply`` chain,
    then any terminal ``opt_in`` turns — in chain (``turn_index``) order, with
    no "round" grouping. It replaces the old ``reports`` / ``statements`` pair.

    Excludes: ``state_hash_before`` / ``state_hash_after`` (engine-internal).
    """

    meeting_id: str
    tick: int
    triggered_by: str
    trigger_kind: Literal["body", "emergency"]
    outcome: Literal["EJECTED", "SKIPPED"]
    ejected_player_id: str | None
    turns: tuple[TurnView, ...]
    ballots: tuple[BallotView, ...]
    contradictions: tuple[ContradictionView, ...]
    llm_calls: tuple[LLMCallView, ...]
    prompt_versions: Mapping[str, str]
    total_cost_usd: float
    gate: GateView


# ---------------------------------------------------------------------------
# Memory + suspicion DTOs (meeting-boundary only for MVP)
# ---------------------------------------------------------------------------


class BeliefEntryView(_FrozenView):
    """Meeting boundary tick at which this belief snapshot was taken. Beliefs
    themselves are timeless; this field timestamps when the spectator API
    observed the belief, not when the belief mutated. All BeliefEntryView
    entries within one AgentMemoryView share the same snapshot_tick."""

    subject: str
    suspicion: float
    confidence: float
    snapshot_tick: int


class AgentMemoryView(_FrozenView):
    """Shadows the ``agents.memory.store`` surface at a meeting boundary.

    MVP exposes agent memory ONLY at meeting boundaries (where the captured
    meeting prompt holds rendered memory); between-meeting memory is not
    exposed. ``observations`` is salience-ordered; ``rendered_memory_text`` is
    the raw prompt render, for the ThoughtStream panel.

    ``tasks_completed`` / ``tasks_assigned`` count this agent's OWN task
    *instances* — its per-player deal, owner-scoped under the per-player keyspace
    (DESIGN.md §3.2), never another player's. Both stay ``int``.

    Excludes: raw memory-store internals and decay timestamps.
    """

    agent_id: str
    tick: int
    role: Literal["CREWMATE", "IMPOSTOR"]
    tasks_completed: int
    tasks_assigned: int
    observations: tuple[ObservationClaimView, ...]
    beliefs: tuple[BeliefEntryView, ...]
    open_contradictions: tuple[ContradictionView, ...]
    rendered_memory_text: str


class BeliefErrorView(_FrozenView):
    """One directed observer→subject belief cell at a meeting boundary, with its
    error vs ground truth (DESIGN.md §3.3, §7) — the Belief × Truth hero datum.

    ``suspicion`` / ``confidence`` are the observer's belief about the subject
    (from the reconstructed ``agents.memory`` belief state). ``subject_is_impostor``
    is the privileged SPECTATOR ground truth (the subject's ``PlayerView.role``),
    and ``error`` is the signed Belief − Truth projection: ``suspicion - (1.0 if
    subject_is_impostor else 0.0)``. A crewmate strongly suspecting the real
    impostor → ``error`` near +1 against an impostor subject ("got it"); a cool
    column on a real impostor → ``error`` near −1 ("getting away with it"); a hot
    column on a crewmate → ``error`` near +1 against a crew subject ("confidently
    wrong"). The Error view buckets/renders these LOUD client-side with its own
    tokens — the projection here is pure arithmetic vs role, baking in no
    thresholds (so the suspicion buckets stay single-sourced in ``tokens.ts``).
    The firewall (identity ≠ guilt; ground-truth suppressed in fog) is enforced
    by the renderer, not this privileged contract.

    ``has_belief`` is ``False`` for a cell the observer holds NO belief about yet
    (the subject is absent from its sparse belief store): the frame is the FULL
    observer×subject grid, so the 9×9 matrix can render an explicit "NO BELIEF
    YET" cell that is distinct from a genuine neutral/low suspicion ("no belief
    yet" ≠ 0, a binding honesty rule). For a no-belief cell ``suspicion`` is the
    neutral 0.5 prior (``confidence`` 0.0), present only to keep the
    ``error == suspicion - truth`` invariant total; the renderer keys on
    ``has_belief``, not the placeholder magnitude.
    """

    observer: str
    subject: str
    suspicion: float
    confidence: float
    subject_is_impostor: bool
    error: float
    has_belief: bool


class BeliefFrameView(_FrozenView):
    """A per-MEETING snapshot of the full belief × truth matrix (DESIGN.md §3.3,
    §7).

    Beliefs are "timeless" (per-meeting, not per-tick) by the Phase-4 decision
    (see :class:`BeliefEntryView` and stage-0 §0.5): between meetings only belief
    Rules 1/4 fire and the vote-time Rule-2 lift is never persisted, so a
    per-tick belief frame would be noise *and* disagree with the ballot. This
    frame is therefore meeting-granular: ``tick`` is the meeting boundary, and
    ``entries`` is the directed observer→subject matrix with the error vs ground
    truth. The frontend steps before→after across the game's (median 2, max 4)
    meetings — small-multiples, not animation.
    """

    meeting_id: str
    tick: int
    entries: tuple[BeliefErrorView, ...]


class SuspicionEntryView(_FrozenView):
    """One directed observer -> subject suspicion edge, derived from per-agent
    ``agents.memory`` belief state."""

    observer: str
    subject: str
    suspicion: float


class SuspicionGraphView(_FrozenView):
    """The suspicion graph at one tick, derived from every agent's
    ``agents.memory`` belief state.

    **Intentionally dead — kept, not revived (DESIGN.md §7; stage-0 §0.5).** This
    per-TICK shape has no route and no producer, and Phase 12 deliberately does
    NOT add one: beliefs are "timeless" (per-meeting). Between meetings only
    belief Rules 1 & 4 fire (flat except isolated body/vent bumps), the
    contradiction lift the agent votes on is computed on a throwaway copy at vote
    time and never persisted, and games hold a median of 2 meetings — so a
    reconstructed per-tick suspicion frame would be noise that DISAGREES with the
    recorded ballot. The Belief × Truth surface is the per-meeting
    :class:`BeliefFrameView` instead. This type is retained (importable,
    inventoried) only so the documented decision and its rationale stay visible
    in the contract rather than being silently deleted and re-proposed later.
    """

    tick: int
    entries: tuple[SuspicionEntryView, ...]


# ---------------------------------------------------------------------------
# Replay-level DTOs
# ---------------------------------------------------------------------------


class ReplayMetadataView(_FrozenView):
    """Shadows ``orchestrator.replay.GameEndReplayEntry`` plus the
    ``compute_cost_usd`` reduction.

    ``seed`` is parsed from ``game_id`` (``headless-seed-{N}``); documented as
    derived, not authoritative. ``winner`` is ``None`` for a partial /
    unfinished game. ``created_at`` is an ISO-8601 timestamp from file mtime,
    ``None`` if not derivable.
    """

    game_id: str
    seed: int
    total_ticks: int
    winner: Literal["CREWMATES", "IMPOSTORS"] | None
    winner_reason: str | None
    meeting_count: int
    total_cost_usd: float
    prompt_versions: Mapping[str, str]
    created_at: str | None


class FailedCallView(_FrozenView):
    """Shadows ``orchestrator.replay.FailedCallReplayEntry``.

    ``error_message`` is truncated to the first 200 chars at the DTO layer.

    Excludes: ``raw_response`` (1KB blob) and ``prompt_length``.
    """

    meeting_id: str
    tick: int
    model: str
    cost_usd: float
    error_type: str
    error_message: str


class FailedCallEvalView(_FrozenView):
    """Sanitized failed-call DTO for the eval-report surface (DESIGN.md §11.2, §11.3).

    The Phase 5 eval route ``GET /eval/tournament-report`` serves the deep
    :class:`eval.meeting_quality.TournamentEvalReport`, which transitively
    embeds :class:`orchestrator.replay.FailedCallReplayEntry` with its raw
    ``raw_response`` blob, ``prompt_length``, and full ``error_message``. The
    Phase 4 replay surface already redacts those via :class:`FailedCallView`, so
    serving them raw over HTTP on the eval route re-exposed exactly what the
    parallel surface suppresses (audit B-B-1 = D-D-1). This view mirrors
    :class:`FailedCallView`'s exclusions so both privileged GM surfaces agree on
    the failed-call contract; the eval route maps each entry through it at the
    route boundary (it does not mutate the underlying replay record).

    It is a *distinct* type from :class:`FailedCallView` rather than a reuse so
    the two surfaces can diverge later without coupling — today their field sets
    are identical by intent. Like :class:`FailedCallView`, ``error_message`` is
    truncated to the first 200 chars at the mapping boundary, not enforced here.

    Excludes: ``raw_response`` (the multi-KB blob), ``prompt_length``, and the
    per-call ``input_tokens`` / ``output_tokens`` — the per-game cost roll-up on
    ``GameCostSummary`` and the cost dashboard already carry token totals, so the
    per-failed-call counts add no spectator value over the raw exposure risk.
    """

    meeting_id: str
    tick: int
    model: str
    cost_usd: float
    error_type: str
    error_message: str


class ReplayView(_FrozenView):
    """The full reconstructed replay: metadata, map, roster, tick timeline,
    meetings, and any failed LLM calls.

    Excludes: per-tick agent memory (only available via the separate
    meeting-boundary endpoint), state hashes, and raw replay entries.

    ``view_model_version`` stamps the versioned contract (:data:`VIEW_MODEL_VERSION`)
    on the primary served payload so the frontend can fail loud on an
    incompatible shape. It serializes as ``viewModelVersion`` (the contract name
    in DESIGN.md §7 / the task) via a ``serialization_alias`` — the lone
    camelCase key, kept exactly as the contract spells it so downstream
    compatibility guards match; the Python attribute stays snake_case.
    """

    view_model_version: str = Field(
        default=VIEW_MODEL_VERSION, serialization_alias="viewModelVersion"
    )
    metadata: ReplayMetadataView
    map: MapLayoutView
    players: tuple[PlayerView, ...]
    ticks: tuple[TickView, ...]
    meetings: tuple[MeetingView, ...]
    failed_calls: tuple[FailedCallView, ...]


# ---------------------------------------------------------------------------
# Eval DTO (single endpoint for now; expand in Phase 5)
# ---------------------------------------------------------------------------


class EvalCostSummaryView(_FrozenView):
    """Aggregates ``orchestrator.replay.compute_cost_usd`` and game outcomes
    across every replay in the directory."""

    total_replays: int
    total_cost_usd: float
    mean_cost_per_replay: float
    max_cost_per_replay: float
    decisive_split: dict[str, float]


class RubricGameView(_FrozenView):
    """One per-game interestingness row from ``results-rubric-score.json``
    (DESIGN.md §3.1, §7; ``experiments/lab/rubric_score.py``).

    Mirrors the ``interestingness.per_game[]`` entry the rubric scorer emits:
    the 0–100 ``score`` (decoupled from who won), the ``win_shape`` tag, the
    drama counts, and the four sub-scores (R1/R2/R3/R7). Joined to a playable
    replay via ``seed`` → ``game_id = headless-seed-{seed}``.
    """

    seed: int
    score: float
    reason: str
    n_meetings: int
    win_shape: str
    ejected_impostors: int
    accused_impostors: int
    survived_accused: int
    r1_decisive: float
    r2_deception: float
    r3_arcs: float
    r7_legible: float


class RubricView(_FrozenView):
    """The per-set rubric surface served at ``/eval/rubric`` (DESIGN.md §3.1, §7).

    The rubric is **per-set** (the 9p2i target set carries one; the default 4p1i
    set has none → 404 / empty state) and **staleness-guarded**: ``git_head`` is
    the commit the rubric was scored at, ``manifest_sha`` is the commit the
    served set's replays were recorded at (read from its ``MANIFEST.md``), and
    ``stale`` is ``True`` when they disagree (the rubric was scored against a
    different code/replay version than the set on disk). ``per_game`` is sorted
    best-first by the scorer, so the Highlights reel renders it directly.
    """

    view_model_version: str = Field(
        default=VIEW_MODEL_VERSION, serialization_alias="viewModelVersion"
    )
    seedset: str
    git_head: str | None
    manifest_sha: str | None
    stale: bool
    per_game: tuple[RubricGameView, ...]


__all__ = [
    "AccusationClaimView",
    "AdvantageView",
    "AgentMemoryView",
    "AgentTickStateView",
    "AgentVisibilityView",
    "AlibiClaimView",
    "AudibleEventView",
    "BallotView",
    "BeliefEntryView",
    "BeliefErrorView",
    "BeliefFrameView",
    "BodyView",
    "CompletedTaskObsView",
    "ContradictionView",
    "CorroborationClaimView",
    "EdgeView",
    "EvalCostSummaryView",
    "FailedCallEvalView",
    "FailedCallView",
    "FoundBodyObsView",
    "GateView",
    "KillEventView",
    "LLMCallView",
    "MapLayoutView",
    "MeetingTriggeredEventView",
    "MeetingView",
    "PlayerView",
    "PositionView",
    "ReplayMetadataView",
    "ReplayView",
    "ReportBodyEventView",
    "RoomView",
    "RubricGameView",
    "RubricView",
    "SabotageDetailView",
    "SabotageEventView",
    "SawPlayerView",
    "SizeView",
    "SuspicionEntryView",
    "SuspicionGraphView",
    "TaskCompletedEventView",
    "TickView",
    "TurnView",
    "VentEventView",
    "VentView",
    "VisibleBodyView",
    "VisiblePlayerView",
]
