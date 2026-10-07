"""The charge library: the route-check replay's charge half, in its one home.

``eval/route_charges.py`` holds ``ordered_pairs``, ``Charge``,
``charges_against`` and ``misjudging_pairs``, lifted from the offline
route-check replay; ``eval/gameplay_census.py`` holds ``is_witness_meeting``.
The placement reader and the pair rule stay in ``meetings/route_lines.py``.
These tests plant each library rule's own breach and hold the one-home rule,
for the charge half and for the route field's reader, with this library in the
tree.
"""

from __future__ import annotations

import ast
from collections.abc import Mapping
from pathlib import Path
from typing import Final

import pytest

import eval.gameplay_census as census
import eval.route_charges as route_charges
import experiments.lab.route_check_replay as rcr
import meetings.route_lines as route_lines
from eval.route_charges import charges_against, misjudging_pairs, ordered_pairs
from meetings.route_lines import placements_of, spoken_placements
from meetings.schemas import (
    ContradictionRef,
    MeetingTranscript,
    MeetingTurn,
    ObservationClaim,
    SawPlayerObservation,
    VoteBallot,
    WhereaboutsClaim,
)
from tests.meetings.test_route_lines import _definers, _tracked_sources

_REPO: Final = Path(__file__).resolve().parents[2]
_SUBJECT: Final = "p-5"

#: Each lifted definition and its one home.
_HOMES: Final[Mapping[str, str]] = {
    "ordered_pairs": "eval/route_charges.py",
    "Charge": "eval/route_charges.py",
    "charges_against": "eval/route_charges.py",
    "misjudging_pairs": "eval/route_charges.py",
    "is_witness_meeting": "eval/gameplay_census.py",
}


def charge_definers(sources: Mapping[str, str]) -> dict[str, list[str]]:
    """Which modules define each lifted function or class, by name."""

    found: dict[str, list[str]] = {name: [] for name in sorted(_HOMES)}
    for path, source in sorted(sources.items()):
        for node in ast.walk(ast.parse(source)):
            if (
                isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
                and node.name in _HOMES
            ):
                found[node.name].append(path)
    return found


def test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy() -> None:
    sources = _tracked_sources()
    assert charge_definers(sources) == {name: [home] for name, home in _HOMES.items()}
    # The lab reads them back and keeps their public names.
    assert rcr.Charge is route_charges.Charge
    assert rcr.charges_against is route_charges.charges_against
    assert rcr.misjudging_pairs is route_charges.misjudging_pairs
    assert rcr.ordered_pairs is route_charges.ordered_pairs
    assert rcr.is_witness_meeting is census.is_witness_meeting
    # Planted: a copy of a charge function left in the lab is found.
    planted = dict(sources)
    planted["experiments/lab/route_check_replay.py"] += (
        "\n\ndef charges_against(target, *, ballots, contradictions, universe):\n"
        "    return ()\n"
    )
    assert charge_definers(planted)["charges_against"] == [
        "eval/route_charges.py",
        "experiments/lab/route_check_replay.py",
    ]


def test_the_field_one_home_test_holds_with_this_library_and_finds_a_copy_in_it() -> (
    None
):
    """The route field's ``ast`` test stays green with the charge library in the
    tree; a copy of ``reconcilable`` defined in it turns that test's reading red."""

    sources = _tracked_sources()
    assert "eval/route_charges.py" in sources
    assert _definers(sources) == {
        "reconcilable": ["meetings/route_lines.py"],
        "spoken_placements": ["meetings/route_lines.py"],
    }
    planted = dict(sources)
    planted["eval/route_charges.py"] += (
        "\n\ndef reconcilable(earlier, later, *, regroup_ticks):\n    return None\n"
    )
    assert _definers(planted)["reconcilable"] == [
        "eval/route_charges.py",
        "meetings/route_lines.py",
    ]


def foreign_imports(source: str) -> list[str]:
    """Each module ``source`` imports outside ``meetings`` and the standard library."""

    allowed = {"__future__", "collections", "dataclasses", "typing", "meetings"}
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        found.extend(name for name in names if name.split(".")[0] not in allowed)
    return found


def test_the_library_imports_only_meetings_and_the_standard_library() -> None:
    source = (_REPO / "eval" / "route_charges.py").read_text(encoding="utf-8")
    assert foreign_imports(source) == []
    planted = source + "\nfrom experiments.lab import route_check_replay\n"
    assert foreign_imports(planted) == ["experiments.lab"]
    # The reader and the rule come from the field's module, never defined here.
    assert vars(route_charges)["reconcilable"] is route_lines.reconcilable
    assert vars(route_charges)["placements_of"] is route_lines.placements_of


# ---------------------------------------------------------------------------
# The library's own planted cases
# ---------------------------------------------------------------------------


def _turn(index: int, speaker: str, *observations: ObservationClaim) -> MeetingTurn:
    return MeetingTurn(
        turn_id=f"m:turn-{index}",
        turn_index=index,
        speaker=speaker,
        turn_kind="opening" if index == 0 else "reply",
        reply_to=None if index == 0 else f"m:turn-{index - 1}",
        observations=observations,
        claims=(),
        free_text=f"turn {index}",
    )


def _saw(subject: str, room: str, tick: int) -> SawPlayerObservation:
    return SawPlayerObservation(
        type="saw_player", tick=tick, subject=subject, room=room
    )


def _ballot(voter: str, target: str, reason: str | None) -> VoteBallot:
    return VoteBallot(
        voter=voter,
        target=target,
        confidence=0.8,
        primary_reason_id=reason,
        rationale_text="a recorded rationale",
    )


def _flag(event_a: str, event_b: str, *subjects: str) -> ContradictionRef:
    return ContradictionRef(
        contradiction_id="c-1",
        kind="alibi_vs_sighting",
        event_a_id=event_a,
        event_b_id=event_b,
        subjects=subjects,
        description="planted",
    )


def _universe(*turns: MeetingTurn) -> tuple[route_lines.Placement, ...]:
    return spoken_placements(MeetingTranscript(turns=turns))


#: The subject seen in WEST_HALL at 14 and ADMIN at 15 (one door, one tick: a
#: walk), and REACTOR at 16 (four doors from WEST_HALL in two ticks: neither).
_TURNS: Final = (
    _turn(0, "p-1", _saw(_SUBJECT, "WEST_HALL", 14)),
    _turn(1, "p-3", _saw(_SUBJECT, "ADMIN", 15)),
    _turn(2, "p-7", _saw(_SUBJECT, "REACTOR", 16)),
    _turn(3, "p-2", WhereaboutsClaim(type="whereabouts", tick=16, room="STORAGE")),
)


def test_a_charge_is_an_eject_citing_a_placement_or_a_flag_of_placements() -> None:
    universe = _universe(*_TURNS)
    ballots = (
        _ballot("p-3", _SUBJECT, "m:turn-0"),
        # Citing a turn that places someone else, citing nothing, and a SKIP.
        _ballot("p-1", _SUBJECT, "m:turn-3"),
        _ballot("p-2", _SUBJECT, None),
        _ballot("p-7", "SKIP", "m:turn-1"),
    )
    flags = (
        _flag("turn:m:turn-1:obs:0", "turn:m:turn-2:obs:0", _SUBJECT),
        # A flag one of whose events places no one, and one not naming the subject.
        _flag("turn:m:turn-1:obs:0", "turn:m:turn-9:obs:0", _SUBJECT),
        _flag("turn:m:turn-0:obs:0", "turn:m:turn-1:obs:0", "p-1"),
    )
    charges = charges_against(
        _SUBJECT, ballots=ballots, contradictions=flags, universe=universe
    )
    assert [(c.source, sorted(p.tick for p in c.placements)) for c in charges] == [
        ("ballot", [14]),
        ("flag", [15, 16]),
    ]


def test_a_charged_pair_is_misjudged_only_when_the_map_or_the_regroup_reconciles() -> (
    None
):
    own = placements_of(_universe(*_TURNS), _SUBJECT)
    by_tick = {spot.tick: spot for spot in own}
    walk = frozenset({by_tick[15]})
    # WEST_HALL at 14 to ADMIN at 15 walks; ADMIN at 15 to REACTOR at 16 does not.
    assert [
        (earlier.tick, later.tick)
        for earlier, later in misjudging_pairs(own, walk, regroup_ticks=frozenset())
    ] == [(14, 15)]
    far = frozenset({by_tick[16]})
    assert misjudging_pairs(own, far, regroup_ticks=frozenset()) == ()
    # A public regroup at 16 reconciles both pairs ending there.
    assert [
        (earlier.tick, later.tick)
        for earlier, later in misjudging_pairs(own, far, regroup_ticks=frozenset({16}))
    ] == [(14, 16), (15, 16)]
    # No charged end, no misjudged pair.
    assert misjudging_pairs(own, frozenset(), regroup_ticks=frozenset({16})) == ()


def test_ordered_pairs_are_every_pair_in_the_placement_order() -> None:
    own = placements_of(_universe(*reversed(_TURNS)), _SUBJECT)
    assert [(a.tick, b.tick) for a, b in ordered_pairs(own)] == [
        (14, 15),
        (14, 16),
        (15, 16),
    ]
    with pytest.raises(ValueError, match="ordered by tick"):
        route_lines.reconcilable(own[-1], own[0], regroup_ticks=frozenset())
