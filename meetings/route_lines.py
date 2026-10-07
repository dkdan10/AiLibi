"""Route lines: the changes of room a table's stated places allow.

A ballot of the served ``qwen3_6_27b`` set may carry one ``<routes>`` block,
built here while a recording's declared config sets ``route_lines_version``.
For each living candidate whose places stated at this table change room in a
way the station's doors or the public regroup allow, one line lists each such
change in tick order and gives one of two readings: the map links the two rooms
within the ticks between, over any number of doors (``walking_fits``), or the
public regroup falls between the two ticks, so walking cannot decide the change
(``regroup_between``). A change of room that neither allows is left out, and a
candidate with no allowed change has no line, so a line never says that a move
was impossible.

A line is a pure function of what the voter already holds: the meeting's
transcript (the same ballot renders it), the map's doors (the ``<map>`` card
renders the same :data:`meetings.transcript.CANONICAL_ROOM_NEIGHBORS` table) and
the public regroup ticks (the voter's memory announces each one). It reads no
role, no private record and no engine state, so a lie stated at the table yields
a line as plain as an honest account, and every voter who may vote for a player
reads that player's line byte for byte the same. It never says a statement is
accurate, never says where anyone stood, and names, ranks or recommends no one:
:class:`RouteStep` and :class:`RouteLine` hold no free text, and their
validators refuse a step whose door count or reading the map does not give.

This module is also the one home of the spoken-placement reader and the pair
rule the offline route-check replay reads (``experiments/lab/
route_check_replay.py`` imports them from here). It imports only
:mod:`meetings.schemas`, :mod:`meetings.transcript`, the standard library and
pydantic, so the prompt loader can import its types and ``agents`` never
reaches the manager or the engine.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from typing import Final, Literal, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from meetings.schemas import (
    AlibiClaim,
    MeetingTranscript,
    MeetingTurn,
    PlayerId,
    SawMoveObservation,
    SawPlayerObservation,
    SawVentObservation,
    WhereaboutsClaim,
)
from meetings.transcript import (
    CANONICAL_ROOMS,
    _turn_claim_id,
    _turn_whereabouts_id,
    canonical_rooms,
    maximal_stays,
    room_hops,
    turn_observation_id,
)

PlacementKind: TypeAlias = Literal[
    "saw_player", "company", "saw_move", "whereabouts", "alibi_stay", "saw_vent"
]


class _Spot(Protocol):
    @property
    def tick(self) -> int: ...

    @property
    def rooms(self) -> frozenset[str]: ...


@dataclass(frozen=True)
class Placement:
    """One typed placement of ``player`` spoken at the meeting, ungated."""

    player: PlayerId
    tick: int
    rooms: frozenset[str]
    kind: PlacementKind
    event_id: str
    turn_id: str


def _placement_key(spot: Placement) -> tuple[int, tuple[str, ...], str, str]:
    return (spot.tick, tuple(sorted(spot.rooms)), spot.event_id, spot.kind)


def _alibi_stay_placements(turn: MeetingTurn) -> Iterator[Placement]:
    """Each maximal stay of each alibi route, at its first and last tick."""

    for index, claim in enumerate(turn.claims):
        if not isinstance(claim, AlibiClaim):
            continue
        event_id = _turn_claim_id(turn=turn, index=index)
        for stay in maximal_stays(claim.route):
            rooms = canonical_rooms(stay.room)
            if not rooms:
                continue
            for tick in sorted({stay.from_tick, stay.to_tick}):
                yield Placement(
                    claim.subject, tick, rooms, "alibi_stay", event_id, turn.turn_id
                )


def spoken_placements(transcript: MeetingTranscript) -> tuple[Placement, ...]:
    """Every typed placement spoken at the meeting, for every player it places.

    Sightings place their subject and their company, a movement sighting its
    destination, a whereabouts its speaker, an alibi route its subject (one
    placement at each end of each stay), a vent sighting its subject. Nothing is
    gated; a label with no canonical room places nobody.
    """

    found: set[Placement] = set()
    for turn in transcript.turns:
        for index, observation in enumerate(turn.observations):
            event_id = turn_observation_id(turn=turn, index=index)
            if isinstance(observation, SawPlayerObservation):
                rooms = canonical_rooms(observation.room)
                if not rooms:
                    continue
                found.add(
                    Placement(
                        observation.subject,
                        observation.tick,
                        rooms,
                        "saw_player",
                        event_id,
                        turn.turn_id,
                    )
                )
                for companion in observation.co_present:
                    if companion != observation.subject:
                        found.add(
                            Placement(
                                companion,
                                observation.tick,
                                rooms,
                                "company",
                                event_id,
                                turn.turn_id,
                            )
                        )
            elif isinstance(observation, SawMoveObservation):
                rooms = canonical_rooms(observation.to_room)
                if rooms:
                    found.add(
                        Placement(
                            observation.subject,
                            observation.tick,
                            rooms,
                            "saw_move",
                            event_id,
                            turn.turn_id,
                        )
                    )
            elif isinstance(observation, WhereaboutsClaim):
                rooms = canonical_rooms(observation.room)
                if rooms:
                    found.add(
                        Placement(
                            turn.speaker,
                            observation.tick,
                            rooms,
                            "whereabouts",
                            _turn_whereabouts_id(turn=turn, index=index),
                            turn.turn_id,
                        )
                    )
            elif isinstance(observation, SawVentObservation):
                rooms = canonical_rooms(observation.room)
                if rooms:
                    found.add(
                        Placement(
                            observation.subject,
                            observation.tick,
                            rooms,
                            "saw_vent",
                            event_id,
                            turn.turn_id,
                        )
                    )
        found.update(_alibi_stay_placements(turn))
    return tuple(sorted(found, key=_placement_key))


def placements_of(
    placements: Iterable[Placement], player: PlayerId
) -> tuple[Placement, ...]:
    return tuple(spot for spot in placements if spot.player == player)


def reconcilable(
    earlier: _Spot, later: _Spot, *, regroup_ticks: frozenset[int]
) -> Literal["walk", "regroup"] | None:
    """How a pair in two different rooms is reconciled, or ``None``.

    ``earlier`` must not be later than ``later``. The rooms must be disjoint
    canonical sets. A walk reconciles when ``1 <= hops <= elapsed`` over the
    whole canonical map (the hop search bounded by the room count); otherwise the
    public regroup reconciles a pair whose interval holds one of its ticks.
    """

    if earlier.tick > later.tick:
        raise ValueError("a pair is ordered by tick")
    hops = room_hops(earlier.rooms, later.rooms, max_hops=len(CANONICAL_ROOMS))
    if hops is None or hops == 0:
        return None
    if hops <= later.tick - earlier.tick:
        return "walk"
    if any(earlier.tick < tick <= later.tick for tick in regroup_ticks):
        return "regroup"
    return None


# ---------------------------------------------------------------------------
# The route lines
# ---------------------------------------------------------------------------

#: The spoken placement kinds a route line reads: sightings, their company,
#: movement destinations, whereabouts and the stays of alibi routes. A vent
#: sighting is not among them; the ballot's Proof paragraph reads that class.
ROUTE_PLACEMENT_KINDS: Final[frozenset[PlacementKind]] = frozenset(
    {"saw_player", "company", "saw_move", "whereabouts", "alibi_stay"}
)

#: A step's two readings: the doors link the rooms within the ticks between, or
#: the public regroup falls between the ticks.
RouteReading: TypeAlias = Literal["walking_fits", "regroup_between"]

#: The block's delimiters, each on a line of its own in the served ballot.
ROUTE_BLOCK_OPEN: Final[str] = "<routes>"
ROUTE_BLOCK_CLOSE: Final[str] = "</routes>"

#: The ballot's own closing lines the block's place is read from: the
#: transcript's, above which the reader reads nothing, and the map card's, two
#: lines below which the block opens.
_TRANSCRIPT_CLOSE: Final[str] = "</transcript>"
_MAP_CLOSE: Final[str] = "</map>"

#: The served form of one line and of one of its steps. The steps of a line are
#: joined by ``"; "`` and the line ends with a full stop.
ROUTE_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"- `(?P<subject>[^`\s]+)`, places stated at this table: (?P<steps>.+)\."
)
ROUTE_STEP_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?P<from_rooms>[A-Z_]+(?:/[A-Z_]+)*) at tick (?P<from_tick>0|[1-9]\d*) to "
    r"(?P<to_rooms>[A-Z_]+(?:/[A-Z_]+)*) at tick (?P<to_tick>0|[1-9]\d*), "
    r"(?P<doors>[1-9]\d*) (?P<noun>doors?) apart, (?:(?P<walk>walking fits)|the "
    r"public regroup at tick (?P<regroup_tick>0|[1-9]\d*) falls between, walking "
    r"cannot decide it)"
)


def _max_doors() -> int:
    """The hop bound of every door count here: the whole map, read when asked.

    The same bound :func:`reconcilable` reads, so a room table that changed would
    move both together.
    """

    return len(CANONICAL_ROOMS)


class RouteStep(BaseModel):
    """One change of room a candidate's stated places make, and how it reads.

    ``doors`` is the fewest doors between the two room sets on the station map,
    and ``reading`` follows from it: ``walking_fits`` when the doors are at most
    the ticks between, otherwise ``regroup_between`` with ``regroup_tick`` a
    public regroup tick inside ``(from_tick, to_tick]``. A step whose rooms
    overlap, whose door count the map does not give, or whose reading does not
    follow from its doors and ticks is refused.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    from_rooms: tuple[str, ...]
    from_tick: int
    to_rooms: tuple[str, ...]
    to_tick: int
    doors: int
    reading: RouteReading
    regroup_tick: int | None = None

    @field_validator("from_tick", "to_tick", "doors", "regroup_tick", mode="before")
    @classmethod
    def _whole_numbers(cls, value: object) -> object:
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("a route step's ticks and doors are whole numbers")
        return value

    @model_validator(mode="after")
    def _the_map_gives_it(self) -> RouteStep:
        for rooms in (self.from_rooms, self.to_rooms):
            if not rooms or tuple(sorted(set(rooms))) != rooms:
                raise ValueError(
                    "a route step names its rooms once each, in sorted order"
                )
            if not set(rooms) <= CANONICAL_ROOMS:
                raise ValueError("a route step names only the station's rooms")
        if set(self.from_rooms) & set(self.to_rooms):
            raise ValueError("a route step is a change of room: its rooms are disjoint")
        doors = room_hops(
            frozenset(self.from_rooms), frozenset(self.to_rooms), max_hops=_max_doors()
        )
        if doors != self.doors:
            raise ValueError(
                f"a route step's door count is the map's: {doors}, not {self.doors}"
            )
        if self.doors <= self.to_tick - self.from_tick:
            if self.reading != "walking_fits" or self.regroup_tick is not None:
                raise ValueError(
                    "the doors fit the ticks between, so the step reads walking_fits"
                )
        elif (
            self.reading != "regroup_between"
            or self.regroup_tick is None
            or not self.from_tick < self.regroup_tick <= self.to_tick
        ):
            raise ValueError(
                "the doors exceed the ticks between, so the step reads "
                "regroup_between with a regroup tick inside its ticks"
            )
        return self


class RouteLine(BaseModel):
    """One candidate's route line: its steps, in tick order, at least one."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    subject: PlayerId
    steps: tuple[RouteStep, ...]

    @model_validator(mode="after")
    def _steps_in_tick_order(self) -> RouteLine:
        if not self.subject or any(c.isspace() or c == "`" for c in self.subject):
            raise ValueError("a route line's subject is a player id")
        if not self.steps:
            raise ValueError("a route line holds at least one step")
        for earlier, later in zip(self.steps, self.steps[1:], strict=False):
            if later.from_tick < earlier.to_tick:
                raise ValueError("a route line lists its steps in tick order")
        return self


@dataclass(frozen=True)
class _RouteSpot:
    """One stated place of a candidate, deduplicated by tick and rooms."""

    tick: int
    rooms: frozenset[str]


def _route_spots(placements: Iterable[Placement]) -> tuple[_RouteSpot, ...]:
    """A candidate's stated places of the route kinds, once each, by tick and rooms."""

    spots = {
        _RouteSpot(spot.tick, spot.rooms)
        for spot in placements
        if spot.kind in ROUTE_PLACEMENT_KINDS
    }
    return tuple(sorted(spots, key=lambda s: (s.tick, tuple(sorted(s.rooms)))))


def _route_step(
    earlier: _RouteSpot, later: _RouteSpot, *, regroup_ticks: frozenset[int]
) -> RouteStep | None:
    """The step a consecutive pair of places makes, or ``None`` when neither reading allows it."""

    how = reconcilable(earlier, later, regroup_ticks=regroup_ticks)
    doors = room_hops(earlier.rooms, later.rooms, max_hops=_max_doors())
    if how is None or doors is None:
        return None
    return RouteStep(
        from_rooms=tuple(sorted(earlier.rooms)),
        from_tick=earlier.tick,
        to_rooms=tuple(sorted(later.rooms)),
        to_tick=later.tick,
        doors=doors,
        reading="walking_fits" if how == "walk" else "regroup_between",
        regroup_tick=None
        if how == "walk"
        else min(t for t in regroup_ticks if earlier.tick < t <= later.tick),
    )


def _require_lines_on_the_table(
    lines: Sequence[RouteLine], *, candidate_targets: Sequence[PlayerId]
) -> tuple[RouteLine, ...]:
    """Refuse a line about a player who is not a candidate, or a second line for one."""

    subjects = [line.subject for line in lines]
    if not set(subjects) <= set(candidate_targets):
        raise ValueError("a route line names only a candidate of this ballot")
    if len(set(subjects)) != len(subjects):
        raise ValueError("a candidate has at most one route line")
    return tuple(lines)


def build_route_lines(
    *,
    transcript: MeetingTranscript,
    candidate_targets: tuple[PlayerId, ...],
    regroup_ticks: frozenset[int],
) -> tuple[RouteLine, ...]:
    """The route lines of one ballot, in ``candidate_targets`` order.

    Each candidate's spoken placements of :data:`ROUTE_PLACEMENT_KINDS` are
    deduplicated by tick and rooms and ordered by tick and rooms, and each
    consecutive pair that :func:`reconcilable` reconciles becomes a step: a walk
    when the doors are at most the ticks between (a walk wins over a crossing),
    otherwise the first regroup tick inside ``(earlier, later]``. A pair that
    neither walks nor crosses is no step, and a candidate with no step has no
    line. ``candidate_targets`` must name each player once, and every regroup
    tick must be a whole tick.
    """

    if len(set(candidate_targets)) != len(candidate_targets):
        raise ValueError("candidate_targets names each candidate once")
    if any(type(tick) is not int or tick < 0 for tick in regroup_ticks):
        raise ValueError(
            f"regroup ticks must be non-negative integers: {sorted(regroup_ticks)}"
        )
    placements = spoken_placements(transcript)
    lines: list[RouteLine] = []
    for subject in candidate_targets:
        spots = _route_spots(placements_of(placements, subject))
        steps = tuple(
            step
            for earlier, later in zip(spots, spots[1:], strict=False)
            if (step := _route_step(earlier, later, regroup_ticks=regroup_ticks))
            is not None
        )
        if steps:
            lines.append(RouteLine(subject=subject, steps=steps))
    return _require_lines_on_the_table(lines, candidate_targets=candidate_targets)


def route_block_span(prompt: str) -> tuple[int, int] | None:
    """The line indices of the block's open and close delimiters, or ``None``.

    The block is read only where the ballot template writes it. Nothing above
    the transcript's last closing line is read, so no text spoken or remembered
    there (a turn's free text, a claim's reason or evidence, a spoken room
    label, a memory line) opens, closes or stands in for a block, and a prompt
    with no transcript closing line carries none. Below that line, a prompt with
    no delimiter line carries no block; otherwise it carries exactly one open
    and one close delimiter line, the open after a blank line two lines below
    the map card's only closing line and the close after the open, and any
    other shape raises.

    The fence stops at the transcript, and holds for a ballot that renders the
    map card, as every ballot of the served set does (rendered without it, a
    served block has no place and raises). Below the transcript the template
    quotes spoken room labels in contradiction sentences and evidence rows: a
    label holding a delimiter line there raises, as does one holding a map
    closing line on a ballot that carries the block, and one holding a
    transcript closing line below the block moves the fence past it, so the
    block reads as absent.
    """

    lines = prompt.split("\n")
    fences = [index for index, line in enumerate(lines) if line == _TRANSCRIPT_CLOSE]
    if not fences:
        return None
    below = range(fences[-1] + 1, len(lines))
    opens = [index for index in below if lines[index] == ROUTE_BLOCK_OPEN]
    closes = [index for index in below if lines[index] == ROUTE_BLOCK_CLOSE]
    if not opens and not closes:
        return None
    if len(opens) > 1 or len(closes) > 1:
        raise ValueError("a ballot carries the route block at most once")
    if not opens:
        raise ValueError("a route block closes but never opens")
    start = opens[0]
    if lines[start - 1] != "":
        raise ValueError("the route block opens after a blank line")
    if [index for index in below if lines[index] == _MAP_CLOSE] != [start - 2]:
        raise ValueError("the route block opens right below the map card")
    if not closes or closes[0] < start:
        raise ValueError("the route block is never closed")
    return start, closes[0]


def without_route_block(prompt: str) -> str:
    """``prompt`` with its route block and the blank line before it removed."""

    span = route_block_span(prompt)
    if span is None:
        return prompt
    start, end = span
    lines = prompt.split("\n")
    return "\n".join(lines[: start - 1] + lines[end + 1 :])


def _parse_step(text: str) -> RouteStep:
    match = ROUTE_STEP_PATTERN.fullmatch(text)
    if match is None:
        raise ValueError("a route step is not in the served form")
    doors = int(match["doors"])
    if (match["noun"] == "door") != (doors == 1):
        raise ValueError("a route step's door noun agrees with its count")
    return RouteStep(
        from_rooms=tuple(match["from_rooms"].split("/")),
        from_tick=int(match["from_tick"]),
        to_rooms=tuple(match["to_rooms"].split("/")),
        to_tick=int(match["to_tick"]),
        doors=doors,
        reading="walking_fits" if match["walk"] else "regroup_between",
        regroup_tick=None if match["walk"] else int(match["regroup_tick"]),
    )


def parse_route_lines(prompt: str) -> tuple[RouteLine, ...]:
    """The route lines a served ballot carries, read back off its block.

    The block is found by :func:`route_block_span`, only where the template
    writes it, so text spoken in the transcript is never read as a block; no
    block reads ``()``. Inside the block, the fixed header comes first and
    every line after it is one candidate's line in the served form; a line in
    any other form, a header line after the first line, a block with no line or
    a second line for one candidate raises, as does every check of
    :class:`RouteStep` and :class:`RouteLine`.
    """

    span = route_block_span(prompt)
    if span is None:
        return ()
    start, end = span
    rows = prompt.split("\n")[start + 1 : end]
    lines: list[RouteLine] = []
    for row in rows:
        if not row.startswith("- "):
            if lines:
                raise ValueError("the route block's header precedes its lines")
            continue
        match = ROUTE_LINE_PATTERN.fullmatch(row)
        if match is None:
            raise ValueError("a route line is not in the served form")
        lines.append(
            RouteLine(
                subject=match["subject"],
                steps=tuple(_parse_step(step) for step in match["steps"].split("; ")),
            )
        )
    if not lines:
        raise ValueError("a route block carries at least one line")
    subjects = [line.subject for line in lines]
    if len(set(subjects)) != len(subjects):
        raise ValueError("a candidate has at most one route line")
    return tuple(lines)
