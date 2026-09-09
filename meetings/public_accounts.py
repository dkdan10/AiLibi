"""Compare attributed public statements without consulting private witness records."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import Final, Literal, TypeAlias

from meetings.schemas import (
    AlibiClaim,
    CompletedTaskObservation,
    ContradictionRef,
    FoundBodyObservation,
    MeetingTranscript,
    MeetingTurn,
    SawKillObservation,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
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


# How a placement was read out of one spoken account. ``stated`` is a direct
# public placement of its subject; ``witness`` is the SPEAKER's own position
# implied by a sighting they claim to have made; ``co_present`` is a bystander
# the speaker names alongside that sighting.
_Derivation: TypeAlias = Literal["stated", "witness", "co_present"]

# Sighting shapes: the speaker asserts they watched another player act, which
# also says where the SPEAKER was. A crewmate sees only its own room and an
# impostor at most one hop (DESIGN.md §3.4 vision), so a witness placement
# carries one hop of slack -- see ``_Placement.vision_slack``.
_SIGHTINGS: Final = (
    SawPlayerObservation,
    SawVentObservation,
    SawKillObservation,
    SawMoveObservation,
)


@dataclass(frozen=True)
class _Placement:
    event_id: str
    speaker: str
    subject: str
    room: str
    start: int
    end: int
    derivation: _Derivation = "stated"
    # Hops of room uncertainty this placement carries. A directly stated
    # placement names the room outright (0). A ``witness`` placement is
    # inferred from what the speaker claims to have seen, and vision reaches
    # one adjacent room for an impostor, so the comparison grants that hop
    # rather than calling a legal account impossible.
    vision_slack: int = 0


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
            event_id = (
                f"turn:{turn.turn_id}:"
                f"{'whereabouts' if isinstance(observation, WhereaboutsClaim) else 'obs'}"
                f":{index}"
            )
            rows.append(_Placement(event_id, turn.speaker, subject, room, start, end))
            if not isinstance(observation, _SIGHTINGS):
                continue
            # Watching an event happen says where the watcher was: a sighting
            # claim places its own speaker, so a speaker cannot claim to have
            # seen something in a room they simultaneously say they were far
            # from. A witnessed transition is stated from its origin room --
            # a witness standing at the destination is one hop away, which
            # ``vision_slack`` already covers.
            rows.append(
                _Placement(
                    f"{event_id}:witness",
                    turn.speaker,
                    turn.speaker,
                    observation.from_room
                    if isinstance(observation, SawMoveObservation)
                    else observation.room,
                    start,
                    end,
                    derivation="witness",
                    vision_slack=1,
                )
            )
            if not isinstance(observation, SawPlayerObservation):
                continue
            # A named bystander is placed in the sighting's room too, so
            # denying that co-presence is a comparable public disagreement.
            for bystander_index, bystander in enumerate(observation.co_present):
                rows.append(
                    _Placement(
                        f"{event_id}:co_present:{bystander_index}",
                        turn.speaker,
                        bystander,
                        room,
                        start,
                        end,
                        derivation="co_present",
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


def _clause(placement: _Placement) -> str:
    """Name the placement's source, so a listener can weigh how it was made."""

    ticks = f"ticks {placement.start}–{placement.end}"
    if placement.derivation == "witness":
        return (
            f"{placement.speaker}'s own sighting places {placement.speaker} "
            f"in {placement.room} at {ticks}"
        )
    if placement.derivation == "co_present":
        return (
            f"{placement.speaker} places {placement.subject} alongside that "
            f"sighting in {placement.room} at {ticks}"
        )
    return (
        f"{placement.speaker} places {placement.subject} in {placement.room} at {ticks}"
    )


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

    A conflict is evidence that two accounts disagree. When both placements
    come from ONE speaker about a third party the flag impeaches that speaker
    instead of the player they named -- two sentences from one mouth are one
    account, and naming the third party would let a single unverified speaker
    mark an innocent. That mirrors the private detector's own rule for the
    same shape (:func:`meetings.transcript._apply_proxy_intra_turn_guard`),
    reimplemented here rather than shared because this module compares only
    public speech and reads no private record.
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
            # speaker's private event phase to declare an honest route impossible,
            # plus each placement's own vision slack.
            slack = first.vision_slack + second.vision_slack
            possible_steps = max(0, later.start - earlier.end) + 1 + slack
            distance = _distance(earlier.room, later.room, room_neighbors)
            if distance is None or distance <= possible_steps:
                continue
            allowance = (
                "even allowing an extra step for unspecified within-tick timing"
                if not slack
                else (
                    "even allowing an extra step for unspecified within-tick "
                    "timing and one more for each placement inferred from a "
                    "claimed sighting"
                )
            )
            explanation = (
                f"If the player walked between these stated placements, "
                f"{allowance}, the public route is longer than the available "
                "interval. An unseen vent is not excluded."
            )
            # One speaker contradicting themselves about somebody else is a
            # single unreliable account, so the flag names that speaker.
            single_author = (
                first.speaker == second.speaker and first.speaker != first.subject
            )
            attribution = (
                f" Both placements come from {first.speaker} alone, so this "
                f"impeaches that speaker's own account rather than "
                f"{first.subject}."
                if single_author
                else ""
            )
            source = f"{first.event_id}|{second.event_id}"
            flags.append(
                ContradictionRef(
                    contradiction_id="public-account-"
                    + sha256(source.encode()).hexdigest()[:16],
                    kind="alibi_conflict",
                    event_a_id=first.event_id,
                    event_b_id=second.event_id,
                    subjects=(first.speaker,) if single_author else (first.subject,),
                    description=(
                        f"{_clause(first)}; {_clause(second)}. {explanation}"
                        f"{attribution} These are attributed accounts, not "
                        "independently verified facts."
                    ),
                    evidence_band="weak",
                )
            )
    return tuple(flags)
