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
concrete models. The Task-19.11 evidence taxonomy (``EvidenceCategory``,
``classify_evidence``, ``UnclassifiableEvidenceError`` and the two kind sets)
is public and importable for the same reason and excluded for the same one:
it is a derived classification OVER a DTO field, not a DTO.
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
#
# ``"2"`` widens :data:`CurrentAction` from seven values to eleven. A widened
# value set is not an additive projection: a consumer that indexes the old seven
# exhaustively (the map's glyph registry does) has no entry for the four new ones,
# so a build on the old contract must fail loudly rather than render a hole.
VIEW_MODEL_VERSION: Final[str] = "2"


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

    Shadows ``observation.packet.AudibleEvent`` — the audio channel
    (``observation.service.ObservationService._audible_events``), read alongside
    the visual field rather than independently of it: ``sabotage_alarm`` is the
    global alarm (``room`` is ``None``), and ``vent_use_heard`` names a vent the
    observer WITNESSED, never one heard through a wall. The repair gate stops
    minting the vent kind — the sight is the whole perception — so it appears only
    in recordings made before that gate, which this view still has to render.
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


CurrentAction: TypeAlias = Literal[
    "IDLE",
    "MOVING",
    "TASK",
    "KILL",
    "VENT",
    "REPORT",
    "SABOTAGE",
    "PRETEND_TASK",
    "EMERGENCY",
    "REPAIR",
    "BLOCKED",
]
"""What an agent DID on one tick: its recorded intent and how the engine resolved it.

The label describes THIS tick's submitted action and its outcome — never the last
action the engine happened to accept, so it can never be inherited from an earlier
tick. An agent that submitted nothing (dead, or the synthesized Start frame) is
``IDLE``; every other value names an intent that was actually recorded for this
tick.

Four of the eleven values are about intents the engine did NOT carry out, which is
where the spectator's picture used to diverge from the game:

* ``PRETEND_TASK`` — an impostor submitted ``do_task``. An impostor owns no task
  instance, so the engine always rejects it, yet a co-located crewmate witnesses
  an agent working (``observation/service.py`` renders that same rejection as
  ``action="task"``). This is the fake-task bluff: the two projections describe
  ONE event and must move together.
* ``BLOCKED`` — the intent did not happen: the engine rejected it, or a meeting
  opened earlier in the same tick and it was never attempted at all.
* ``EMERGENCY`` — an accepted emergency-button press, kept apart from ``REPORT``
  (a body report), because they are different acts with different tells.
* ``REPAIR`` — an accepted ``repair_sabotage``, kept apart from ``TASK``.

Spectator-side only: this is a projection of already-recorded bytes, so no engine
state, action row or ``state_hash`` is involved.
"""


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
    current_action: CurrentAction
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


class MeetingResolutionView(_FrozenView):
    """Explicit pre/post-resolution labeling for a RESOLVED meeting's tick frame
    (Task 19.10; audits/audit-phase-19-triage.md §7 item 11).

    A meeting :class:`TickView` carries two vintages of the same tick at once.
    Its ``agent_states`` / ``events`` / ``tasks_*_total`` are the **PRE**-resolution
    state — the roster the meeting deliberates over, in which an about-to-be-ejected
    player is still alive — while ``TickView.advantage`` is recomputed from the
    **POST**-resolution state so the win-progress trajectory carries the meeting's
    outcome (the decisive inflection; see ``api.replay_loader._walk``). Before this
    view the two vintages were conflated in one unlabeled frame and every consumer
    had to re-derive which half it was reading. ``pre_advantage`` is the same
    tick's advantage BEFORE the meeting's result applied, so both vintages are now
    present and named rather than mixed.

    ``None`` on every non-meeting frame AND on an unresolved (partial-replay)
    meeting frame, whose ``advantage`` never got the post-resolution rewrite and is
    therefore purely pre-resolution. ``ejected_player_id`` mirrors
    :attr:`MeetingView.ejected_player_id` (``None`` for a SKIPPED meeting) so the
    frame is self-describing without a client-side join against ``meetings``.
    """

    meeting_id: str
    ejected_player_id: str | None
    pre_advantage: AdvantageView


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
    # Task 19.10: the pre/post-resolution label for a RESOLVED meeting frame (see
    # :class:`MeetingResolutionView`). Additive and defaulted so every payload
    # serialized before 19.10 still parses; ``None`` on every other frame.
    meeting_resolution: MeetingResolutionView | None = None


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


class SawVentObservationView(_FrozenView):
    """Shadows ``meetings.schemas.SawVentObservation`` (Task 15.4.1).

    The spectator mirror of the role-proving vent sighting (Task 15.4): a
    witnessed impostor vent named by ``subject`` / ``room`` / ``tick``. Like
    the source shape it carries no enter/exit phase field (the perception
    layer collapses both vent engine events into a single witnessed action).
    Whether the sighting minted a hard flag is conveyed separately by the
    ``vent_sighting`` :class:`ContradictionView`, not by this observation.
    """

    type: Literal["saw_vent"]
    tick: int
    subject: str
    room: str


class WhereaboutsClaimView(_FrozenView):
    """Shadows ``meetings.schemas.WhereaboutsClaim`` (Task 16.7.1).

    The spectator mirror of the roll-call self-placement (Task 16.7): "I was
    in ``room`` at ``tick``". Deliberately SELF-placement — it carries NO
    subject field because the subject IS the turn speaker
    (:attr:`TurnView.speaker`); the placement belongs to whoever took the
    turn. Vouching for OTHERS needs no new kind — a :class:`SawPlayerView`
    already expresses that. Display-only: the source shape is a degenerate
    single-tick self-alibi the manager already indexes for contradiction
    detection, so lying in it surfaces through the EXISTING alibi flag path;
    this view re-derives nothing.
    """

    type: Literal["whereabouts"]
    tick: int
    room: str


class SawMoveObservationView(_FrozenView):
    """Shadows ``meetings.schemas.SawMoveObservation``.

    The spectator mirror of a witnessed transition: ``subject`` moved
    ``from_room`` → ``to_room``, arriving at ``tick``. Display-only, and
    deliberately shows BOTH rooms — the transition is what the witness said,
    while which placement the detector draws from it is a meeting-layer
    decision the transcript never re-derives.
    """

    type: Literal["saw_move"]
    tick: int
    subject: str
    from_room: str
    to_room: str


ObservationClaimView: TypeAlias = Annotated[
    SawPlayerView
    | CompletedTaskObsView
    | FoundBodyObsView
    | SawVentObservationView
    | WhereaboutsClaimView
    | SawMoveObservationView,
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


TurnAnnotationLabel: TypeAlias = Literal[
    "invalid_accusation_target",
    "invalid_alibi_subject",
    "invalid_corroboration_supports",
    "fabricated_opening",
    "opening_degraded_unsure",
]
"""What a meeting guard changed about a turn, as the spectator names it.

Shadows ``meetings.schemas.TurnAnnotationKind`` (this module never imports the
meeting layer); the two are pinned equal in ``tests/api/test_replay_loader.py``,
so a new kind cannot reach the wire without a chip to render it.
"""


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
    # What the meeting layer's guards changed about this turn, as the
    # ``meetings.schemas.TurnAnnotationKind`` vocabulary. Both recorded shapes
    # land here: the structured ``MeetingTurn.annotations`` rows and the audit
    # markers older recordings spliced into ``free_text`` (parsed off at load,
    # so ``free_text`` is the speaker's words alone). Rendered as role-neutral
    # chips beside the turn, never as raw dev jargon (DESIGN.md §3.4, §5.5).
    annotations: tuple[TurnAnnotationLabel, ...] = ()
    # True when this (emergency) opening had a fabricated found_body
    # deterministically stripped — the ``fabricated_opening`` annotation, kept
    # as its own flag because the transcript gives it a dedicated chip.
    fabricated_opening: bool


# ---------------------------------------------------------------------------
# Evidence taxonomy (Task 19.11; audits/audit-phase-19-triage.md §7 item 12)
# ---------------------------------------------------------------------------


EvidenceCategory: TypeAlias = Literal["role_proof", "cross_statement", "weak_signal"]
"""What KIND of evidence a flagged :class:`ContradictionView` actually is.

The meeting layer carries every flag through ONE shape
(``meetings.schemas.ContradictionRef``) and the spectator surface used to
render them all the same way — so a grounded vent sighting, which is role
PROOF, arrived under a "Contradictions" heading as ``p-X ↔ p-X`` (its two
event ids reference the SAME spoken observation by design,
``meetings/schemas.py`` / ``meetings/transcript.py``), and a one-tick
interval artifact stamped ``[weak signal: …]`` drew with the same visual
weight as hard evidence. This alias is the derived classification that keeps
those three things apart:

* ``role_proof`` — a grounded ``vent_sighting`` (Task 15.4): a spoken
  observation matched against the speaker's OWN typed vent-witness record.
  Vents are impostor-only, so the flag names a role, not a conflict. It is
  self-linked (one event, cited twice) and never carries a weak marker.
* ``cross_statement`` — a conflict between two DIFFERENT statements
  (``alibi_conflict`` / ``alibi_vs_sighting`` / ``alibi_vs_physical``). The
  flag says they cannot both be true, never which one is the lie. Usually both
  sides are unverified model-authored testimony — but NOT always, and the
  category deliberately does not claim otherwise: 37 of the 42 committed
  ``alibi_vs_physical`` flags are Task 18.9's GROUNDED vent-placement arm,
  where one side is a typed ``VentWitnessRecord`` (engine truth) rather than
  testimony. Those are arguably role proof; the contract's rule table scopes
  ROLE-PROOF to ``vent_sighting`` / self-linked, so they classify here. See
  the PR's Findings section — widening the rule would move 37 flags and must
  be decided together with Task 19.14's cross-pinned eval-side twin. That twin
  has since landed (``eval.deduction_metrics.classify_flag``) and did NOT
  widen the rule: it re-implements this exact table and the two derivations are
  pinned to identical per-category counts on the committed bytes
  (``tests/eval/test_deduction_metrics.py``). The 37 grounded
  ``alibi_vs_physical`` flags therefore stay ``cross_statement`` on BOTH
  surfaces, and widening remains one decision taken once, in both places.
* ``weak_signal`` — a cross-statement flag the detector itself stamped
  ``[weak signal: …]`` (self-stated alibi pair, narrow window, endpoint-tick
  overlap). Belief Rule 2 already down-weights these; the spectator surface
  subordinates them to match.

Derived at the DTO layer only: recorded bytes and the ``meetings/`` schemas
are frozen, so this is classification, not schema migration. Task 19.14
implements the eval-side twin and the two are cross-pinned (same counts on
the same bytes), which is why :func:`classify_evidence` is a pure function of
primitives rather than of any DTO.
"""


# The role-proving kinds: a flag of this kind is proof regardless of how its
# event ids sit. Today exactly ``vent_sighting`` (Task 15.4's grounding
# chokepoint is the precision gate — an ungrounded spoken vent claim raises no
# flag at all, so a flag of this kind can only name a genuine venter).
ROLE_PROOF_KINDS: Final[frozenset[str]] = frozenset({"vent_sighting"})

# The cross-statement kinds: two DIFFERENT public statements that cannot both
# be true. Whether such a flag is ``cross_statement`` or ``weak_signal``
# depends on the detector's own weak stamp, not on the kind.
CROSS_STATEMENT_KINDS: Final[frozenset[str]] = frozenset(
    {"alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical"}
)


class UnclassifiableEvidenceError(ValueError):
    """A recorded flag matches no :data:`EvidenceCategory` rule.

    Raised — never defaulted — by :func:`classify_evidence`. The taxonomy must
    be TOTAL over every committed byte: a new ``ContradictionRef.kind`` added
    in ``meetings/`` without a corresponding rule here is a finding to record,
    not a bucket to widen ("no silent fallbacks", AGENTS.md).
    """


def classify_evidence(
    *,
    kind: str,
    event_a_id: str,
    event_b_id: str,
    weak: bool,
) -> EvidenceCategory:
    """Classify one recorded flag into its :data:`EvidenceCategory`.

    The rules — a table, deliberately trivial to port (Task 19.14 re-implemented
    it eval-side as ``eval.deduction_metrics.classify_flag``; the two are
    cross-pinned on the same bytes, which is evidence only because neither
    imports the other):

    ==========================================  ==================
    condition                                   category
    ==========================================  ==================
    ``kind`` is not a KNOWN kind                *raise*
    ``kind`` in :data:`ROLE_PROOF_KINDS`        ``role_proof``
    ``event_a_id == event_b_id`` (self-linked)  ``role_proof``
    ``weak`` (the ``[weak signal: …]`` stamp)   ``weak_signal``
    otherwise                                   ``cross_statement``
    ==========================================  ==================

    The kind check comes FIRST and gates everything. Order matters here: with
    the weak rule ahead of it, an unrecognised kind that happened to carry a
    weak stamp would quietly bucket as ``weak_signal`` instead of raising —
    a silent default in the one place the contract says there must not be one.
    Once the kind is known, the remaining rows cannot fall through, so
    ``cross_statement`` is the exhaustive tail rather than a fourth guard.

    Self-linkage is a rule of its own rather than a property of the kind: a
    flag whose two event ids reference the SAME artifact is not a conflict
    between two statements by construction, whatever it is called. On the
    committed corpus the two role-proof rules agree exactly (every self-linked
    flag is a ``vent_sighting`` and vice versa — pinned corpus-wide in
    ``tests/api/test_evidence_taxonomy.py``); keeping both means a known kind
    that starts emitting self-linked flags cannot silently render as a
    contradiction, while a genuinely NEW kind still fails loud above.

    ``weak`` is the caller's, and must come from
    ``meetings.transcript.is_weak_contradiction`` (imported, never
    re-implemented — the same discipline ``ContradictionView.weak`` follows),
    so the marker predicate stays single-sourced beside the marker writer.

    :raises UnclassifiableEvidenceError: on any kind the table does not cover.
    """

    if kind not in ROLE_PROOF_KINDS and kind not in CROSS_STATEMENT_KINDS:
        raise UnclassifiableEvidenceError(
            f"unclassifiable evidence: kind={kind!r} "
            f"(event_a_id={event_a_id!r}, event_b_id={event_b_id!r}, "
            f"weak={weak!r}); the evidence taxonomy has no rule for it — "
            "record it as a finding rather than widening a bucket"
        )
    if kind in ROLE_PROOF_KINDS or event_a_id == event_b_id:
        return "role_proof"
    if weak:
        return "weak_signal"
    return "cross_statement"


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

    Task 15.4.1: the ``vent_sighting`` role-proving kind (Task 15.4) is
    mirrored here — it is always STRONG (grounding is the precision gate, so
    it carries no weak marker). It used to RENDER like the other kinds too;
    ``category`` below is what stopped that.

    Task 19.11: ``category`` derives the :data:`EvidenceCategory` taxonomy at
    load (:func:`classify_evidence`), so the spectator surface can render
    proof as proof instead of as a self-linked ``p-X ↔ p-X`` "contradiction",
    and subordinate weak-stamped flags instead of drawing them at hard-evidence
    weight (audits/audit-phase-19-triage.md §7 item 12; §8 rows 10, 14). It is
    ADDITIVE and derived: ``kind`` / ``event_a_id`` / ``event_b_id`` /
    ``description`` keep their recorded meanings, and every committed
    recording — including those made before ``vent_sighting`` existed —
    classifies without a schema migration.
    """

    contradiction_id: str
    kind: Literal[
        "alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical", "vent_sighting"
    ]
    event_a_id: str
    event_b_id: str
    subjects: tuple[str, ...]
    description: str
    weak: bool
    severity: Literal["weak", "strong"]
    category: EvidenceCategory


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

    Task 16.7.1: ``primary_reason_observation_id`` mirrors the private
    hard-evidence citation channel (``meetings.schemas.VoteBallot`` gained it
    at Task 16.5): a stable episodic observation id
    (``{agent_id}:{tick}:{seq}``) drawn from the VOTER'S OWN memory, distinct
    from ``primary_reason_id`` (which references a public meeting ``turn_id``).
    It is display-only here — the manager already validated it against the
    voter's memory (``meetings.manager._normalize_ballot_observation_id``); the
    spectator surface never re-validates. The ``None`` default mirrors the
    source model's additive rationale (recordings predating the field, and
    ballots that cited nothing, surface ``None``).
    """

    voter: str
    target: str
    confidence: float
    primary_reason_id: str | None
    primary_reason_observation_id: str | None = None
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
# Finale DTOs (Task 19.10) — the recorded outcome as one composed view
# ---------------------------------------------------------------------------


class FinaleEventView(_FrozenView):
    """One decisive beat on the road to the recorded outcome (Task 19.10).

    Shadows the recorded engine kill events and meeting records; composed
    server-side so the finale is ONE view rather than a client-side join over
    ``ticks[*].events`` and ``meetings``. ``actor_id`` is the killer (kill) or the
    player who triggered the meeting (ejection / skipped meeting); ``subject_id``
    is the victim (kill) or the ejected player (ejection). Both are ``None`` on
    the terminal ``game_end`` beat, which exists so the card can name the tick the
    game actually ended on even when nothing else happened there.
    """

    tick: int
    kind: Literal["kill", "ejection", "meeting_skipped", "game_end"]
    actor_id: str | None
    subject_id: str | None


class FinaleAgentRecapView(_FrozenView):
    """One agent's compact "what they knew vs the truth" recap row (Task 19.10).

    Pairs ground truth (``role``, ``alive_at_end``) with the recorded
    decision-level evidence of what the agent believed: their ballot in the LAST
    meeting of the game. ``final_vote_target`` is ``"SKIP"`` or a player id, and
    ``None`` when the game held no meetings or the agent cast no ballot in the
    last one (they were already dead, or the meeting predates their death).
    ``final_vote_named_impostor`` is ``None`` when there is no vote or the vote was
    ``"SKIP"``; otherwise it is whether the target's TRUE role is ``IMPOSTOR``.

    Ballot-derived on purpose. Per-agent beliefs are only reconstructed on the
    separate, expensive memory walk (``ReplayLoader.belief_frames``), whereas
    ballots are recorded bytes already available on the bulk load path — so the
    finale costs nothing extra per ``GET /replays/{game_id}``. The trade-off is
    that this is *decision*-level truth, not *belief*-level; the Belief × Truth
    surface (:class:`BeliefFrameView`) remains the belief-level view.

    ``final_vote_rewritten`` marks the one case where the recorded target is NOT
    evidence of the voter's belief: the meeting layer rewrote the ballot's
    target (an under-gate redirect, a teammate/uncited coercion, an
    invalid-target normalization, or a whole-ballot parse default — the audit
    markers the loader already parses into ``BallotView.rewrite_reasons``).
    ``final_vote_target`` then documents the TALLIED vote, not the authored
    choice — the recorded rationale can explicitly oppose it — so
    ``final_vote_named_impostor`` is ``None`` for a rewritten ballot: judging
    "did they name an impostor" against a target the engine chose would invert
    the agent's actual reasoning (e.g. the committed 9p2i seed 22, where p-5's
    intended target was redirected). Citation-only rewrites (a nulled reason /
    observation id) leave the authored target intact and do NOT set this flag.
    """

    agent_id: str
    role: Literal["CREWMATE", "IMPOSTOR"]
    alive_at_end: bool
    final_vote_target: str | None
    final_vote_named_impostor: bool | None
    # Task 19.10 (review): additive and defaulted so pre-existing serialized
    # payloads still parse; ``False`` for an authored (or absent) ballot.
    final_vote_rewritten: bool = False


class GameFinale(_FrozenView):
    """The game's resolution as one additive view (Task 19.10).

    Winner, win reason, the recorded final tick, the decisive events, and the
    per-agent recap — everything the finale card renders, composed once
    server-side. Built from the recorded ``game_over`` row and the recorded
    meeting records (shadowing ``orchestrator.replay.GameEndReplayEntry``) and
    NEVER re-validated against re-walked state: recorded bytes are authoritative
    (a direct-``ReplayLog`` writer may legitimately stamp a winner onto a
    non-terminal state, as the codegen fidelity fixture does).

    ``winner_reason`` stays a plain ``str`` rather than the four-value
    ``engine.win_conditions.WinResultType`` literal: fixtures and pre-Phase-14
    recordings carry other strings (e.g. ``"all_tasks_complete"``), and this DTO
    shadows what was recorded, not what the current engine would emit.

    ``None`` on :class:`ReplayView` for a partial replay with no ``game_over`` row
    (a crashed / tick-budget-exhausted run) — the game has no recorded outcome, so
    there is no finale to show.
    """

    winner: Literal["CREWMATES", "IMPOSTORS"]
    winner_reason: str
    final_tick: int
    decisive_events: tuple[FinaleEventView, ...]
    agent_recaps: tuple[FinaleAgentRecapView, ...]


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
    # Task 19.10: the composed outcome view (see :class:`GameFinale`). Additive
    # and defaulted so every payload serialized before 19.10 still parses;
    # ``None`` for a partial replay with no recorded ``game_over`` row.
    finale: GameFinale | None = None


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

    The rubric is **per-set** (the default 9p2i target set carries one; the 4p1i
    fast technical fixture, served only via an explicit ``?set=4p1i``, ships none
    → 404 / empty state) and **staleness-guarded**: ``git_head`` is the commit
    the rubric was scored at, ``manifest_sha`` is the commit the served set's
    replays were recorded at (read from its ``MANIFEST.md``), and
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
    "FinaleAgentRecapView",
    "FinaleEventView",
    "FoundBodyObsView",
    "GameFinale",
    "GateView",
    "KillEventView",
    "LLMCallView",
    "MapLayoutView",
    "MeetingResolutionView",
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
    "SawMoveObservationView",
    "SawPlayerView",
    "SawVentObservationView",
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
    "WhereaboutsClaimView",
]
