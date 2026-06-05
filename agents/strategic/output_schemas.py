"""Agent-side re-exports of the shared meeting schemas (DESIGN.md §5.2, §5.3, §5.5).

The canonical Pydantic shapes live in :mod:`meetings.schemas`. This
module exists so strategic agent code can import the symbols from a
location under ``agents/strategic/`` without duplicating any
definition. Adding a new strategic output type means defining it in
``meetings/schemas.py`` and re-exporting it here.

Record-shape note (Task 8.7 / 8.8). The reactive accusation chain
(DESIGN.md §5.2) replaced the parallel-reports + fixed-round
``ReportDocument`` / ``Statement`` pair with the single ordered
``turns`` list, so the agent-facing meeting artifact is now
:class:`~meetings.schemas.MeetingTurn` (``turn_kind`` selects the
opening / reply / opt-in role). The strategic reasoner's
``produce_report`` / ``produce_statement`` both emit a ``MeetingTurn``
and ``produce_vote`` emits a :class:`~meetings.schemas.VoteBallot`.
"""

from __future__ import annotations

from meetings.schemas import (
    AccusationClaim,
    AlibiClaim,
    Claim,
    CompletedTaskObservation,
    ContradictionRef,
    CorroborationClaim,
    FoundBodyObservation,
    MeetingOutcome,
    MeetingResult,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    TurnId,
    TurnKind,
    VoteBallot,
)

__all__ = [
    "AccusationClaim",
    "AlibiClaim",
    "Claim",
    "CompletedTaskObservation",
    "ContradictionRef",
    "CorroborationClaim",
    "FoundBodyObservation",
    "MeetingOutcome",
    "MeetingResult",
    "MeetingTranscript",
    "MeetingTurn",
    "ObservationClaim",
    "SawPlayerObservation",
    "TurnId",
    "TurnKind",
    "VoteBallot",
]
