"""Select one bounded response to a newly consequential structured accusation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from meetings.schemas import AccusationClaim, MeetingTranscript


class RebuttalOpportunity(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    speaker: str
    reply_to: str


def select_bounded_rebuttal(
    transcript: MeetingTranscript, *, living_ids: frozenset[str]
) -> RebuttalOpportunity | None:
    """Choose the earliest unanswered new charge after its target already spoke.

    Consequence is structural: a new accusation target or new named observation
    supporting that charge. A separately attributed observation is a new
    allegation, without certifying its truth. Repeated prose alone is not new
    evidence. A later
    turn by the target counts as an existing response opportunity, regardless of
    its quality. The caller may add one turn only and never recursively reselect.
    """

    spoken: set[str] = set()
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    pending: list[RebuttalOpportunity] = []
    for turn in transcript.turns:
        pending = [row for row in pending if row.speaker != turn.speaker]
        for claim in turn.claims:
            if not isinstance(claim, AccusationClaim):
                continue
            target = claim.against
            observations = tuple(
                sorted(
                    observation.model_dump_json()
                    for observation in turn.observations
                    if getattr(observation, "subject", None) == target
                )
            )
            key = (target, turn.speaker if observations else "", observations)
            if key in seen:
                continue
            seen.add(key)
            if target in spoken and target in living_ids and target != turn.speaker:
                pending.append(
                    RebuttalOpportunity(speaker=target, reply_to=turn.turn_id)
                )
        spoken.add(turn.speaker)
    return pending[0] if pending else None
