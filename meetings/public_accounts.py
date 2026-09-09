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
from meetings.transcript import (
    WEAK_CONTRADICTION_MARKER_PREFIX,
    WEAK_REASON_PROXY_INTRA_TURN,
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
    # The transcript artifact this row was read out of, in the ONE event-id
    # vocabulary every reader knows -- ``turn:<turn_id>:claim:<i>``,
    # ``:obs:<i>``, ``:whereabouts:<i>`` (``frontend/src/lib/contradictions.ts``
    # declares it; ``MeetingView`` builds its parser from that declaration). A
    # derived row keeps the id of the artifact it derives from, so a flag's
    # endpoints always resolve to a turn artifact a reader can show.
    event_id: str
    speaker: str
    subject: str
    room: str
    start: int
    end: int
    derivation: _Derivation = "stated"
    # Which ``co_present`` name a ``co_present`` row reads; 0 for every other
    # derivation. Part of :attr:`identity`, never of the event id.
    slot: int = 0
    # Hops of room uncertainty this placement carries. A directly stated
    # placement names the room outright (0). A ``witness`` placement is
    # inferred from what the speaker claims to have seen, and vision reaches
    # one adjacent room for an impostor, so the comparison grants that hop
    # rather than calling a legal account impossible.
    vision_slack: int = 0

    @property
    def identity(self) -> str:
        """This row's own key: the artifact plus how the row was derived.

        One artifact yields up to three rows (the stated placement, the
        speaker's implied witness position, one per named bystander), so the
        ``contradiction_id`` hashes THIS rather than the event id -- otherwise
        two different derived pairs off one pair of artifacts would collide on
        a single id. It is never an endpoint: :attr:`event_id` is.
        """

        if self.derivation == "stated":
            return self.event_id
        if self.derivation == "co_present":
            return f"{self.event_id}:co_present:{self.slot}"
        return f"{self.event_id}:witness"


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
                    event_id,
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
                if bystander == turn.speaker:
                    # A speaker naming ITSELF among the bystanders is saying
                    # again what the witness row above already says: it was
                    # there to see this. That row carries the vision hop; a
                    # duplicate without it would make the speaker's own
                    # sighting impeach the speaker's own stated position, so
                    # this reads the self-mention as the repetition it is
                    # rather than as a second, stricter account. Nothing is
                    # lost: the speaker stays placed by the witness row.
                    continue
                rows.append(
                    _Placement(
                        event_id,
                        turn.speaker,
                        bystander,
                        room,
                        start,
                        end,
                        derivation="co_present",
                        slot=bystander_index,
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
    mark an innocent -- and it carries
    :data:`~meetings.transcript.WEAK_REASON_PROXY_INTRA_TURN`, so
    :func:`meetings.transcript.contradiction_lift_key` folds every re-target
    against one speaker into a single belief delta. Both halves mirror the
    private detector's rule for the same shape
    (:func:`meetings.transcript._apply_proxy_intra_turn_guard`, Task 10.10);
    the comparison is reimplemented here rather than shared because this module
    compares only public speech and reads no private record.
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
            # single unreliable account, so the flag names that speaker -- and
            # carries the private detector's own proxy-intra-turn reason, which
            # is what makes ``contradiction_lift_key`` fold every one of this
            # speaker's re-targets into a SINGLE belief delta. Without the
            # marker, N incompatible sentences from one mouth would be N weak
            # lifts against that mouth, which is the stack Task 10.10 exists to
            # prevent (audit C-C-2: one bad claim cannot mint two stacking
            # deltas).
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
            # The audit marker closes the description, exactly as the private
            # detector's re-target closes its own.
            marker = (
                f" {WEAK_CONTRADICTION_MARKER_PREFIX}{WEAK_REASON_PROXY_INTRA_TURN}]"
                if single_author
                else ""
            )
            source = f"{first.identity}|{second.identity}"
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
                        f"independently verified facts.{marker}"
                    ),
                    evidence_band="weak",
                )
            )
    return tuple(flags)
