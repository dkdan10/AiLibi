"""Shared meeting / output schemas (DESIGN.md §5.2, §5.3, §5.4, §5.5, Appendix A).

This module owns the canonical Pydantic shapes for every artifact a
meeting produces under the reactive accusation-chain protocol (DESIGN.md
§5.2):

* :class:`MeetingTurn` -- one entry in the ordered ``transcript.turns``
  list (§5.2, §5.3, Appendix A). A turn is ``opening`` (the reporter's
  findings + accuse-or-unsure), ``reply`` (the accused responds), or
  ``opt_in`` (a relevant non-speaker volunteers). It carries both the
  structured ``observations`` / ``claims`` and the free-text argument.
* :class:`VoteBallot` -- the structured vote each agent casts (§5.5).
* :class:`ContradictionRef` -- a detected contradiction between two
  events (§5.4, §6.4); information, not a verdict.
* :class:`MeetingResult` -- the engine-free DTO :class:`MeetingManager`
  returns to the orchestrator after voting resolves (§5.1).

Every model is frozen, forbids extra fields, and is suitable for
structured LLM output (Pydantic v2 JSON-schema generation). This module
is the single home for these shapes: downstream code imports them from
here and never duplicates a schema definition.

Record-shape note (Task 8.7). The parallel-reports + fixed-round
``Statement`` record was replaced by the single ordered ``turns`` list:
``ReportDocument`` folds into the ``opening`` turn (its ``found_body`` /
``saw_player`` observations now live on turn 0) and ``Statement`` becomes
:class:`MeetingTurn`. Reshaping :class:`MeetingTranscript` from
``(reports, statements)`` to ``turns`` changes ``MeetingReplayEntry``
(``extra='forbid'``), so committed meeting rows recorded under the old
shape stop validating and are re-recorded in Task 8.12.
"""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

PlayerId: TypeAlias = str
RoomId: TypeAlias = str
TaskId: TypeAlias = str
BodyId: TypeAlias = str
TurnId: TypeAlias = str
ContradictionId: TypeAlias = str


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ---------------------------------------------------------------------------
# Observation claims carried by a MeetingTurn (DESIGN.md §5.3)
# ---------------------------------------------------------------------------


class SawPlayerObservation(_FrozenModel):
    """First-hand sighting of another player at a tick."""

    type: Literal["saw_player"]
    tick: int
    subject: PlayerId
    room: RoomId
    co_present: tuple[PlayerId, ...] = ()


class CompletedTaskObservation(_FrozenModel):
    """Own task completion claim (used as alibi evidence)."""

    type: Literal["completed_task"]
    tick: int
    task_id: TaskId
    room: RoomId


class FoundBodyObservation(_FrozenModel):
    """Body-discovery report tied to the meeting's trigger event."""

    type: Literal["found_body"]
    tick: int
    body_of: PlayerId
    room: RoomId


class SawVentObservation(_FrozenModel):
    """First-hand witnessed impostor vent (Task 15.4).

    Role-proving testimony: vents are impostor-only (DESIGN.md §3.4), so a
    witnessed vent names its ``subject`` as an impostor. Deliberately NO
    enter/exit phase field: the perception layer collapses both vent engine
    events into a single witnessed "vent" action
    (``observation/service.py::_vent_observation_for_agent``) and episodic
    memory persists only player/room/action, so a phase field would be
    unobservable fabrication.

    Speech alone never mints hard evidence from this shape: the STRONG
    ``vent_sighting`` flag fires only when the meeting layer grounds the
    spoken observation against the speaker's OWN typed
    :class:`VentWitnessRecord` channel
    (:func:`meetings.transcript.detect_contradictions`); an ungrounded
    claim records as ordinary testimony and raises no flag. Deliberately
    NOT reduced to a :class:`ReportedStatement` either — the Task 13.5.2
    reported-testimony scope is owner-locked to its four kinds.
    """

    type: Literal["saw_vent"]
    tick: int
    subject: PlayerId
    room: RoomId


ObservationClaim: TypeAlias = Annotated[
    SawPlayerObservation
    | CompletedTaskObservation
    | FoundBodyObservation
    | SawVentObservation,
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# Typed vent-witness grounding channel (Task 15.4)
# ---------------------------------------------------------------------------


class VentWitnessRecord(_FrozenModel):
    """One of an agent's OWN witnessed-vent episodic records (Task 15.4).

    The typed grounding input behind the ``vent_sighting`` hard flag: the
    meeting boundary otherwise hands the manager only rendered-memory prose
    plus a suspicion graph — nothing a validator could check a spoken vent
    claim against without parsing prompt text. The
    ``MeetingAwareAgent.vent_witness_records_for_meeting()`` accessor
    (``orchestrator/game.py``) surfaces these straight off episodic memory
    (``saw_player`` rows with ``action == "vent"``,
    ``provenance == "observed"``), and
    :func:`meetings.transcript.detect_contradictions` confirms a speaker's
    spoken :class:`SawVentObservation` ONLY against the speaker's own
    records (subject + room, tick within
    :data:`meetings.transcript.VENT_GROUNDING_TICK_TOLERANCE`) — the
    chokepoint never parses rendered prose. Firewall-clean by construction:
    an agent reporting its own witnessed events leaks nothing, and the
    packet stamp the records derive from is witness-gated by the engine
    (``eval/leak_test.py``).
    """

    subject: PlayerId
    room: RoomId
    tick: int


# ---------------------------------------------------------------------------
# Higher-level claims (alibi / accusation / corroboration) (DESIGN.md §5.3)
# ---------------------------------------------------------------------------


class AlibiClaim(_FrozenModel):
    """Self- or other-player alibi for a tick range.

    Tick ranges are inclusive and must be chronological
    (``from_tick <= to_tick``). DESIGN.md §5.4 contradiction detection
    indexes alibis by ``(agent, tick_range, location)``; a reversed
    range would be silently interpreted as an empty/no-overlap window
    and produce wrong contradiction flags rather than fail loud
    (AGENTS.md "no silent fallbacks").
    """

    type: Literal["alibi"]
    subject: PlayerId
    from_tick: int
    to_tick: int
    room: RoomId
    evidence: tuple[str, ...] = ()

    @model_validator(mode="after")
    def _validate_chronological_range(self) -> AlibiClaim:
        if self.from_tick > self.to_tick:
            raise ValueError(
                "AlibiClaim tick range must be chronological: "
                f"from_tick={self.from_tick} > to_tick={self.to_tick}"
            )
        return self


class AccusationClaim(_FrozenModel):
    """Accusation against another player with explicit confidence.

    The reactive chain (DESIGN.md §5.2) passes the turn to the accused:
    the next speaker is a pure function of a turn's accusation target,
    which is read off the turn's first :class:`AccusationClaim`
    (:func:`meetings.transcript.accusation_target`).
    """

    type: Literal["accusation"]
    against: PlayerId
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str


class CorroborationClaim(_FrozenModel):
    """Public corroboration of another agent's claim or alibi."""

    type: Literal["corroboration"]
    supports: PlayerId
    on_tick: int
    reason: str


Claim: TypeAlias = Annotated[
    AlibiClaim | AccusationClaim | CorroborationClaim,
    Field(discriminator="type"),
]


# ---------------------------------------------------------------------------
# Meeting turn record (DESIGN.md §5.2, §5.3, Appendix A)
# ---------------------------------------------------------------------------


TurnKind: TypeAlias = Literal["opening", "reply", "opt_in"]
"""Discriminator for the three turn roles in the accusation chain.

* ``opening`` -- turn 0: the body-reporter / emergency caller states
  findings and accuses one player or declares "unsure".
* ``reply`` -- a reactive-chain turn: the accused responds and may
  counter-accuse. ``reply_to`` references the accusing turn.
* ``opt_in`` -- a terminal info-share turn from a relevant non-speaker;
  it may accuse but never extends the chain.
"""


class MeetingTurn(_FrozenModel):
    """One entry in the ordered ``transcript.turns`` list (DESIGN.md §5.2).

    A turn carries the speaker's structured ``observations`` (with tick
    references) and ``claims`` (alibi / accusation / corroboration) plus
    the free-text argument shown to spectators and to later speakers.

    ``turn_id`` is ``"{meeting_id}:turn-{turn_index}"`` -- unique even
    when a player speaks twice -- and is what
    :attr:`VoteBallot.primary_reason_id` references. ``reply_to`` is the
    ``turn_id`` this turn answers (set on a ``reply``; ``None`` on
    ``opening`` and on a volunteering ``opt_in``).

    The reporter's ``found_body`` / ``saw_player`` observations live on
    the ``opening`` turn (turn 0); :mod:`eval.vote_correctness` reads
    them from there.
    """

    turn_id: TurnId
    turn_index: int
    speaker: PlayerId
    turn_kind: TurnKind
    reply_to: TurnId | None
    observations: tuple[ObservationClaim, ...] = ()
    claims: tuple[Claim, ...] = ()
    free_text: str


# ---------------------------------------------------------------------------
# Reported testimony (Task 13.5.2 -- testimony as reported episodic content)
# ---------------------------------------------------------------------------


ReportedStatementKind: TypeAlias = Literal[
    "saw_player", "alibi", "accusation", "corroboration"
]
"""Discriminator for the four STRUCTURED testimony shapes carried as content.

Task 13.5.2 (2026-06-25 memory diagnosis, workflow ``wg54kfoxy``: "social info
is a scalar, not content"). Exactly the four structured claim/observation kinds
the owner scoped IN -- a :class:`SawPlayerObservation` sighting, an
:class:`AlibiClaim`, an :class:`AccusationClaim`, a :class:`CorroborationClaim`.
Free-text is excluded by construction (it never produces a
:class:`ReportedStatement`).
"""


class ReportedStatement(_FrozenModel):
    """One public testimony statement reduced from a meeting transcript (Task 13.5.2).

    The engine-free DTO :func:`meetings.manager.derive_reported_testimony`
    emits and :func:`agents.memory.store.absorb_reported_testimony` ingests as
    ``provenance="reported"`` episodic content -- the "social info is a scalar,
    not content" fix from the 2026-06-25 memory diagnosis (workflow
    ``wg54kfoxy``). It mirrors the scalar twin
    (:class:`meetings.manager.MeetingBeliefEvidence`) but carries the WHAT of a
    statement, not a suspicion delta: who spoke (``speaker``), the structured
    ``kind``, who it is about (``subject``), and the optional tick window / room.

    The optional fields are populated per ``kind``:

    * ``saw_player`` -- ``from_tick == to_tick`` (the sighting tick), ``room``, and
      any ``co_present`` companions the sighting publicly named (the "who was with
      whom" evidence the structured schema carries; Task 13.5.2, Codex P2).
    * ``alibi`` -- the inclusive ``from_tick``/``to_tick`` window and ``room``.
    * ``accusation`` -- ``subject`` only (no tick, no room).
    * ``corroboration`` -- ``from_tick == to_tick`` (the corroborated tick); no room.

    Frozen and ``extra='forbid'`` like every meeting DTO, so the reduction is a
    pure, replay-deterministic function of the recorded ``MeetingResult``.
    """

    speaker: PlayerId
    kind: ReportedStatementKind
    subject: PlayerId
    from_tick: int | None = None
    to_tick: int | None = None
    room: RoomId | None = None
    co_present: tuple[PlayerId, ...] = ()


# ---------------------------------------------------------------------------
# Voting (DESIGN.md §5.5)
# ---------------------------------------------------------------------------


class VoteBallot(_FrozenModel):
    """Voting output (DESIGN.md §5.5).

    The structured fields drive the tally; the rationale is logged
    post-hoc for transparency. ``primary_reason_id`` references a
    :class:`MeetingTurn` ``turn_id`` from the chain when applicable.
    """

    voter: PlayerId
    target: PlayerId | Literal["SKIP"]
    confidence: float = Field(ge=0.0, le=1.0)
    primary_reason_id: TurnId | None
    considered_alternatives: tuple[PlayerId, ...] = ()
    rationale_text: str


# ---------------------------------------------------------------------------
# Contradiction detection (DESIGN.md §5.4, §6.4)
# ---------------------------------------------------------------------------


class ContradictionRef(_FrozenModel):
    """A flagged contradiction between two events (DESIGN.md §5.4).

    Flags are information, not verdicts: detected contradictions feed
    back into the rendered memory view that subsequent agents see.
    ``event_a_id`` and ``event_b_id`` reference structured artifacts
    (turn claim / observation ids); ``kind`` captures the detector
    category so consumers can branch on it without parsing free text.

    Task 13.4 (report-phase-b-plan B3/B4): ``alibi_vs_physical`` is the
    inferential kind reconstructed from public testimony -- a subject's OWN
    stated alibi physically contradicted by independent co-presence placements
    of them elsewhere over the alibi window (see
    :func:`meetings.transcript.detect_contradictions`). The manager persists
    ``detect_contradictions`` at meeting close, so a recorded ``MeetingResult``
    can carry it; the served ``api.schemas.ContradictionView`` and the frontend
    ``ContradictionKind`` union both accept it (rendered like the other alibi
    kinds).

    Task 15.4: ``vent_sighting`` is the role-proving kind -- a spoken
    :class:`SawVentObservation` GROUNDED against the speaker's own typed
    :class:`VentWitnessRecord` channel (vents are impostor-only, DESIGN.md
    §3.4). Always STRONG (no weak marker): the grounding chokepoint is the
    precision gate, so an ungrounded spoken vent claim raises no flag at
    all rather than a weak one. Both event ids reference the SAME spoken
    observation (the single public artifact; the private grounding record
    has no transcript id by design). Committed v4 replays predate the kind
    and never carry it; the spectator-view mirror is Task 15.4.1.
    """

    contradiction_id: ContradictionId
    kind: Literal[
        "alibi_conflict", "alibi_vs_sighting", "alibi_vs_physical", "vent_sighting"
    ]
    event_a_id: str
    event_b_id: str
    subjects: tuple[PlayerId, ...]
    description: str


# ---------------------------------------------------------------------------
# Meeting result (DESIGN.md §5.1, §5.2)
# ---------------------------------------------------------------------------


MeetingOutcome: TypeAlias = Literal["EJECTED", "SKIPPED"]


class MeetingTranscript(_FrozenModel):
    """Ordered transcript of a meeting (DESIGN.md §5.2).

    A single ``turns`` tuple in chain order: the ``opening`` turn, then
    the reactive ``reply`` chain, then any terminal ``opt_in`` turns.
    Used both for replay and for rendering the meeting view to the
    spectator UI. Replacing the old ``(reports, statements)`` pair with
    ``turns`` is the meeting-side record-format change (Task 8.7): an old
    committed transcript carrying ``reports`` / ``statements`` keys fails
    this model's ``extra='forbid'`` and is re-recorded in Task 8.12.
    """

    turns: tuple[MeetingTurn, ...] = ()


class MeetingResult(_FrozenModel):
    """Engine-free DTO returned by :class:`MeetingManager` (DESIGN.md §5.1).

    Carries enough information for the orchestrator to apply the
    outcome to engine-owned state and to persist the meeting in the
    replay log. The orchestrator -- not the meeting manager -- mutates
    engine state.

    ``outcome`` and ``ejected_player_id`` are coupled invariants:

    * ``EJECTED`` requires a non-``None`` ``ejected_player_id``.
    * ``SKIPPED`` requires ``ejected_player_id is None``.

    DESIGN.md §5.1 and §5.2 define meeting resolution as
    ejection-or-skip; tied votes also collapse into ``SKIPPED`` per
    "tie or below threshold -> skip" (§5.2 PHASE 5). The
    ``MeetingOutcome`` alias therefore exposes only ``EJECTED`` and
    ``SKIPPED`` -- any third outcome would leak protocol-incompatible
    state that downstream consumers would have to special-case.

    Enforcing this at parse time prevents structured LLM output (or a
    buggy ``MeetingManager``) from producing a logically inconsistent
    payload that the orchestrator would have to guess at.
    """

    meeting_id: str
    triggered_by: PlayerId
    trigger_tick: int
    outcome: MeetingOutcome
    ejected_player_id: PlayerId | None
    ballots: tuple[VoteBallot, ...]
    contradictions: tuple[ContradictionRef, ...] = ()
    transcript: MeetingTranscript

    @model_validator(mode="after")
    def _validate_outcome_matches_ejection(self) -> MeetingResult:
        if self.outcome == "EJECTED" and self.ejected_player_id is None:
            raise ValueError(
                "MeetingResult outcome='EJECTED' requires a non-None ejected_player_id"
            )
        if self.outcome == "SKIPPED" and self.ejected_player_id is not None:
            raise ValueError(
                "MeetingResult outcome='SKIPPED' requires ejected_player_id is None"
            )
        return self


__all__ = [
    "AccusationClaim",
    "AlibiClaim",
    "BodyId",
    "Claim",
    "CompletedTaskObservation",
    "ContradictionId",
    "ContradictionRef",
    "CorroborationClaim",
    "FoundBodyObservation",
    "MeetingOutcome",
    "MeetingResult",
    "MeetingTranscript",
    "MeetingTurn",
    "ObservationClaim",
    "PlayerId",
    "ReportedStatement",
    "ReportedStatementKind",
    "RoomId",
    "SawPlayerObservation",
    "SawVentObservation",
    "TaskId",
    "TurnId",
    "TurnKind",
    "VentWitnessRecord",
    "VoteBallot",
]
