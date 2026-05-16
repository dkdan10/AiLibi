"""Agent-side re-exports of the shared meeting schemas (DESIGN.md §5.3, §5.5).

The canonical Pydantic shapes live in :mod:`meetings.schemas`. This
module exists so strategic agent code can import the symbols from a
location under ``agents/strategic/`` without duplicating any
definition. Adding a new strategic output type means defining it in
``meetings/schemas.py`` and re-exporting it here.
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
    ObservationClaim,
    ReportDocument,
    SawPlayerObservation,
    Statement,
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
    "ObservationClaim",
    "ReportDocument",
    "SawPlayerObservation",
    "Statement",
    "VoteBallot",
]
