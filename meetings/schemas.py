"""Shared meeting / output schemas (DESIGN.md §5.1, §5.3, §5.4, §5.5, Appendix A).

This module owns the canonical Pydantic shapes for every artifact a
meeting produces:

* :class:`ReportDocument` -- the structured-plus-free-text report each
  living agent submits in Phase 1 of the meeting protocol (§5.3).
* :class:`Statement` -- one accusation-round turn (§5.2).
* :class:`VoteBallot` -- the structured vote each agent casts (§5.5).
* :class:`ContradictionRef` -- a detected contradiction between two
  events (§5.4, §6.4); information, not a verdict.
* :class:`MeetingResult` -- the engine-free DTO :class:`MeetingManager`
  returns to the orchestrator after voting resolves (§5.1).

Every model is frozen, forbids extra fields, and is suitable for
structured LLM output (Pydantic v2 JSON-schema generation). Agent-side
re-exports live in ``agents/strategic/output_schemas.py``; downstream
code must import from one of these two locations and never duplicate a
schema definition.
"""

from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

from pydantic import BaseModel, ConfigDict, Field, model_validator

PlayerId: TypeAlias = str
RoomId: TypeAlias = str
TaskId: TypeAlias = str
BodyId: TypeAlias = str
StatementId: TypeAlias = str
ContradictionId: TypeAlias = str


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# ---------------------------------------------------------------------------
# Observation claims used inside ReportDocument (DESIGN.md §5.3)
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
    """Body-discovery report tied to the report's trigger event."""

    type: Literal["found_body"]
    tick: int
    body_of: PlayerId
    room: RoomId


ObservationClaim: TypeAlias = Annotated[
    SawPlayerObservation | CompletedTaskObservation | FoundBodyObservation,
    Field(discriminator="type"),
]


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
    """Accusation against another player with explicit confidence."""

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
# Meeting artifacts (DESIGN.md §5.2, §5.3, §5.5)
# ---------------------------------------------------------------------------


class ReportDocument(_FrozenModel):
    """Phase-1 report each living agent submits (DESIGN.md §5.3)."""

    agent_id: PlayerId
    tick: int
    observations: tuple[ObservationClaim, ...] = ()
    claims: tuple[Claim, ...] = ()
    free_text: str


class Statement(_FrozenModel):
    """One accusation-round turn (DESIGN.md §5.2).

    A statement either targets another agent (accusation) or is purely
    defensive. Structured ``claims`` are mechanically parseable; the
    free-text version is shown to spectators and to other agents in
    subsequent rounds.
    """

    statement_id: StatementId
    speaker: PlayerId
    tick: int
    round_index: int
    target: PlayerId | None
    claims: tuple[Claim, ...] = ()
    free_text: str


class VoteBallot(_FrozenModel):
    """Voting output (DESIGN.md §5.5).

    The structured fields drive the tally; the rationale is logged
    post-hoc for transparency. ``primary_reason_id`` references a
    :class:`Statement` id from the accusation rounds when applicable.
    """

    voter: PlayerId
    target: PlayerId | Literal["SKIP"]
    confidence: float = Field(ge=0.0, le=1.0)
    primary_reason_id: StatementId | None
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
    (statement / report / observation ids); ``kind`` captures the
    detector category so consumers can branch on it without parsing
    free text.
    """

    contradiction_id: ContradictionId
    kind: Literal["alibi_conflict", "alibi_vs_sighting"]
    event_a_id: str
    event_b_id: str
    subjects: tuple[PlayerId, ...]
    description: str


# ---------------------------------------------------------------------------
# Meeting result (DESIGN.md §5.1, §5.2)
# ---------------------------------------------------------------------------


MeetingOutcome: TypeAlias = Literal["EJECTED", "SKIPPED"]


class MeetingTranscript(_FrozenModel):
    """Structured transcript of a meeting.

    Combines the Phase-1 reports and the Phase-2 statements; used both
    for replay and for rendering the meeting view to the spectator UI.
    """

    reports: tuple[ReportDocument, ...] = ()
    statements: tuple[Statement, ...] = ()


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
    "If tie or below threshold, skip" (§5.2 PHASE 4). The
    ``MeetingOutcome`` alias therefore exposes only ``EJECTED`` and
    ``SKIPPED`` -- any third outcome would leak protocol-incompatible
    state that downstream consumers (Task 3.10 voting, Task 3.12
    orchestrator integration) would have to special-case.

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
    "ObservationClaim",
    "PlayerId",
    "ReportDocument",
    "RoomId",
    "SawPlayerObservation",
    "Statement",
    "StatementId",
    "TaskId",
    "VoteBallot",
]
