"""The charges a meeting brought, and the stated pairs the map or the regroup reconciles.

A charge is an EJECT ballot or a contradiction flag resting on typed placements
of its target that the meeting's turns stated. A charge rests on a reconcilable
pair when one of its placements is an end of a pair of the target's stated
places in two different rooms that the station's doors link within the ticks
between, or that the public regroup falls between. That is a process count over
what was said at the table: it reads no role, and a reconcilable pair proves no
innocence.

These four definitions are the charge half of the offline route-check replay
(``experiments/lab/route_check_replay.py``), moved here so the gameplay census
can count them; the replay imports them back and keeps no copy. The placement
reader, its sort key and the pair rule are imported from their one home,
:mod:`meetings.route_lines`, and never defined here. This module imports only
:mod:`meetings`, the standard library and nothing under ``experiments/``.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from typing import Literal

from meetings.route_lines import (
    Placement,
    _placement_key,
    placements_of,
    reconcilable,
)
from meetings.schemas import ContradictionRef, PlayerId, VoteBallot


def ordered_pairs(spots: Sequence[Placement]) -> Iterator[tuple[Placement, Placement]]:
    ordered = sorted(spots, key=_placement_key)
    for index, earlier in enumerate(ordered):
        for later in ordered[index + 1 :]:
            yield earlier, later


@dataclass(frozen=True)
class Charge:
    """An EJECT ballot or a flag resting on typed placements of its target."""

    source: Literal["ballot", "flag"]
    placements: frozenset[Placement]


def charges_against(
    target: PlayerId,
    *,
    ballots: Sequence[VoteBallot],
    contradictions: Sequence[ContradictionRef],
    universe: Sequence[Placement],
) -> tuple[Charge, ...]:
    """The charges against ``target`` at one meeting.

    A charge is an EJECT ballot for ``target`` whose primary reason cites a turn
    carrying a typed placement of ``target``, or a contradiction flag naming
    ``target`` whose every event is such a placement.
    """

    own = placements_of(universe, target)
    found: list[Charge] = []
    for ballot in ballots:
        if ballot.target != target or ballot.primary_reason_id is None:
            continue
        cited = frozenset(
            spot for spot in own if spot.turn_id == ballot.primary_reason_id
        )
        if cited:
            found.append(Charge("ballot", cited))
    for flag in contradictions:
        if target not in flag.subjects:
            continue
        events = (flag.event_a_id, flag.event_b_id)
        resolved = [
            frozenset(spot for spot in own if spot.event_id == event)
            for event in events
        ]
        if all(resolved):
            found.append(Charge("flag", frozenset().union(*resolved)))
    return tuple(found)


def misjudging_pairs(
    universe_of_target: Sequence[Placement],
    charged: frozenset[Placement],
    *,
    regroup_ticks: frozenset[int],
) -> tuple[tuple[Placement, Placement], ...]:
    """The reconcilable pairs of which a charged placement is one end."""

    return tuple(
        (earlier, later)
        for earlier, later in ordered_pairs(universe_of_target)
        if (earlier in charged or later in charged)
        and reconcilable(earlier, later, regroup_ticks=regroup_ticks) is not None
    )


__all__ = ["Charge", "charges_against", "misjudging_pairs", "ordered_pairs"]
