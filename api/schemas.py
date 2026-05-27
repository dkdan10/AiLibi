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
from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field


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


class AgentTickStateView(_FrozenView):
    """The dynamic slice of one agent's ``engine.entities.PlayerState`` at one
    tick.

    ``is_venting`` is impostor-only state, exposed because the spectator is
    privileged. ``task_progress`` is ``None`` for impostors.

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
    """Projects ``engine.events.SabotageStartedEvent`` (DESIGN.md §8.3 MVP
    scope: lights only)."""

    type: Literal["sabotage"]
    tick: int
    kind: Literal["lights"]
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


TickEventView: TypeAlias = Annotated[
    KillEventView
    | ReportBodyEventView
    | SabotageEventView
    | TaskCompletedEventView
    | MeetingTriggeredEventView,
    Field(discriminator="type"),
]


class TickView(_FrozenView):
    """One reconstructed tick of a replay.

    Excludes: state hashes, raw engine actions, and raw per-tick replay
    records — those are reconstruction inputs, not spectator data.
    """

    tick: int
    agent_states: tuple[AgentTickStateView, ...]
    events: tuple[TickEventView, ...]
    sabotage_active: tuple[str, ...]
    tasks_completed_total: int
    tasks_required_total: int


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


class ReportView(_FrozenView):
    """Shadows ``meetings.schemas.ReportDocument`` (the Phase-1 report)."""

    agent_id: str
    tick: int
    observations: tuple[ObservationClaimView, ...]
    claims: tuple[StatementClaimView, ...]
    free_text: str


class StatementView(_FrozenView):
    """Shadows ``meetings.schemas.Statement`` (one accusation-round turn)."""

    statement_id: str
    speaker: str
    tick: int
    round_index: int
    target: str | None
    claims: tuple[StatementClaimView, ...]
    free_text: str


class ContradictionView(_FrozenView):
    """Shadows ``meetings.schemas.ContradictionRef`` (a flagged contradiction)."""

    contradiction_id: str
    kind: Literal["alibi_conflict", "alibi_vs_sighting"]
    event_a_id: str
    event_b_id: str
    subjects: tuple[str, ...]
    description: str


class BallotView(_FrozenView):
    """Shadows ``meetings.schemas.VoteBallot``.

    ``target`` flattens ``str | Literal["SKIP"]`` to a plain ``str`` ("SKIP"
    or a player id) for JSON simplicity.
    """

    voter: str
    target: str
    confidence: float
    primary_reason_id: str | None
    considered_alternatives: tuple[str, ...]
    rationale_text: str


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


class MeetingView(_FrozenView):
    """Shadows ``orchestrator.replay.MeetingReplayEntry``.

    ``trigger_kind`` is derived from the source meeting trigger. ``outcome``
    and ``ejected_player_id`` are coupled (EJECTED <=> non-null id).
    ``total_cost_usd`` is the sum of ``llm_calls[*].cost_usd``.

    Excludes: ``state_hash_before`` / ``state_hash_after`` (engine-internal).
    """

    meeting_id: str
    tick: int
    triggered_by: str
    trigger_kind: Literal["body", "emergency"]
    outcome: Literal["EJECTED", "SKIPPED"]
    ejected_player_id: str | None
    reports: tuple[ReportView, ...]
    statements: tuple[StatementView, ...]
    ballots: tuple[BallotView, ...]
    contradictions: tuple[ContradictionView, ...]
    llm_calls: tuple[LLMCallView, ...]
    prompt_versions: Mapping[str, str]
    total_cost_usd: float


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


class SuspicionEntryView(_FrozenView):
    """One directed observer -> subject suspicion edge, derived from per-agent
    ``agents.memory`` belief state."""

    observer: str
    subject: str
    suspicion: float


class SuspicionGraphView(_FrozenView):
    """The suspicion graph at one tick, derived from every agent's
    ``agents.memory`` belief state."""

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


class ReplayView(_FrozenView):
    """The full reconstructed replay: metadata, map, roster, tick timeline,
    meetings, and any failed LLM calls.

    Excludes: per-tick agent memory (only available via the separate
    meeting-boundary endpoint), state hashes, and raw replay entries.
    """

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


__all__ = [
    "AccusationClaimView",
    "AgentMemoryView",
    "AgentTickStateView",
    "AlibiClaimView",
    "BallotView",
    "BeliefEntryView",
    "CompletedTaskObsView",
    "ContradictionView",
    "CorroborationClaimView",
    "EdgeView",
    "EvalCostSummaryView",
    "FailedCallView",
    "FoundBodyObsView",
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
    "ReportView",
    "RoomView",
    "SabotageEventView",
    "SawPlayerView",
    "SizeView",
    "StatementView",
    "SuspicionEntryView",
    "SuspicionGraphView",
    "TaskCompletedEventView",
    "TickView",
    "VentView",
]
