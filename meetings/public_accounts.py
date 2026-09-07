"""Compare attributed public statements without consulting private witness records."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256

from meetings.schemas import (
    AlibiClaim,
    CompletedTaskObservation,
    ContradictionRef,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    SawMoveObservation,
    TaskActivityAccount,
    WhereaboutsClaim,
)


class PublicAccountValidationError(ValueError):
    """An account cannot refer to the stated public game context."""


def validate_public_accounts(
    turn: MeetingTurn,
    *,
    roster: frozenset[str],
    current_tick: int,
    room_ids: frozenset[str],
    task_ids: frozenset[str],
) -> None:
    """Validate references and time bounds, not whether a speaker is truthful.

    Neither source observation identifiers nor private records are inputs.
    Impossible combinations of otherwise valid statements remain public claims.
    """

    for row in (*turn.observations, *turn.claims):
        data = row.model_dump()
        for key in ("subject", "body_of", "against", "supports"):
            if key in data and data[key] not in roster:
                raise PublicAccountValidationError(f"unknown public player in {key}")
        for player in data.get("co_present", ()):
            if player not in roster:
                raise PublicAccountValidationError("unknown co-present player")
        for key in ("room", "from_room", "to_room"):
            if key in data and data[key] not in room_ids:
                raise PublicAccountValidationError(f"unknown public room in {key}")
        if "task_id" in data and data["task_id"] not in task_ids:
            raise PublicAccountValidationError("unknown public task")
        for key in ("tick", "from_tick", "to_tick", "on_tick"):
            if key in data and not 0 <= data[key] <= current_tick:
                raise PublicAccountValidationError(
                    "account tick is outside game history"
                )


@dataclass(frozen=True)
class _Placement:
    event_id: str
    speaker: str
    subject: str
    room: str
    start: int
    end: int


def _placements(transcript: MeetingTranscript) -> tuple[_Placement, ...]:
    rows: list[_Placement] = []
    for turn in transcript.turns:
        for index, observation in enumerate(turn.observations):
            subject = turn.speaker
            if isinstance(observation, TaskActivityAccount):
                start, end = observation.from_tick, observation.to_tick
                room = observation.room
            else:
                start = end = observation.tick
                if isinstance(observation, SawMoveObservation):
                    room = observation.to_room
                else:
                    room = observation.room
                if not isinstance(
                    observation,
                    (CompletedTaskObservation, WhereaboutsClaim, FoundBodyObservation),
                ):
                    subject = observation.subject
            rows.append(
                _Placement(
                    f"turn:{turn.turn_id}:{'whereabouts' if isinstance(observation, WhereaboutsClaim) else 'obs'}:{index}",
                    turn.speaker,
                    subject,
                    room,
                    start,
                    end,
                )
            )
        for index, claim in enumerate(turn.claims):
            if isinstance(claim, AlibiClaim):
                rows.append(
                    _Placement(
                        f"turn:{turn.turn_id}:claim:{index}",
                        turn.speaker,
                        claim.subject,
                        claim.room,
                        claim.from_tick,
                        claim.to_tick,
                    )
                )
    return tuple(rows)


def _distance(
    origin: str, destination: str, neighbors: Mapping[str, tuple[str, ...]]
) -> int | None:
    pending = deque([(origin, 0)])
    seen = {origin}
    while pending:
        room, distance = pending.popleft()
        if room == destination:
            return distance
        for adjacent in neighbors.get(room, ()):
            if adjacent not in seen:
                seen.add(adjacent)
                pending.append((adjacent, distance + 1))
    return None


def detect_public_account_conflicts(
    transcript: MeetingTranscript,
    *,
    roster: frozenset[str],
    room_neighbors: Mapping[str, tuple[str, ...]],
) -> tuple[ContradictionRef, ...]:
    """Describe inconsistent accounts, without declaring a speaker or role proven.

    Movement places the named player at the stated destination only. A walking
    comparison is conditional: public speech cannot exclude an unseen vent.
    Discovery dates a speaker's account, never a victim's death.
    """

    placements = _placements(transcript)
    flags: list[ContradictionRef] = []
    for index, first in enumerate(placements):
        for second in placements[index + 1 :]:
            if (
                first.subject != second.subject
                or first.subject not in roster
                or first.room == second.room
            ):
                continue
            earlier, later = (
                (first, second) if first.start <= second.start else (second, first)
            )
            # Tick-only speech does not specify before/after action order.
            # Allow one additional within-tick step instead of borrowing the
            # speaker's private event phase to declare an honest route impossible.
            possible_steps = max(0, later.start - earlier.end) + 1
            distance = _distance(earlier.room, later.room, room_neighbors)
            if distance is None or distance <= possible_steps:
                continue
            explanation = (
                "If the player walked between these stated placements, even "
                "allowing an extra step for unspecified within-tick timing, "
                "the public route is longer than the available interval. An "
                "unseen vent is not excluded."
            )
            source = f"{first.event_id}|{second.event_id}"
            flags.append(
                ContradictionRef(
                    contradiction_id="public-account-"
                    + sha256(source.encode()).hexdigest()[:16],
                    kind="alibi_conflict",
                    event_a_id=first.event_id,
                    event_b_id=second.event_id,
                    subjects=(first.subject,),
                    description=(
                        f"{first.speaker} places {first.subject} in {first.room} "
                        f"at ticks {first.start}–{first.end}; {second.speaker} "
                        f"places them in {second.room} at ticks "
                        f"{second.start}–{second.end}. {explanation} These are "
                        "attributed accounts, not independently verified facts."
                    ),
                    evidence_band="weak",
                )
            )
    return tuple(flags)
