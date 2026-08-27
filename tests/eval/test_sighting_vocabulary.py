"""The first-hand-sighting vocabulary stays countable, and cannot grow.

A spoken ``saw_move`` places its subject at its destination — the placement the
detector mints flags from (``meetings.transcript.sighting_placement``). A
predicate that ``isinstance``-checks ``SawPlayerObservation`` and omits
``SawMoveObservation`` is therefore blind to a channel the game supplies; on the
committed 9p2i corpus that channel carries 1,136 observations against 2,722
static sightings.

Task 21.9 widened the two predicates that GATE something — the referee's
subject-aware backing bit and its mirror in the conviction label — and
deliberately left five alone. This walk makes that deferral structural: the
remainder is enumerated, each entry carries the reason it is still narrow, and a
sixth cannot appear without failing here.
"""

from __future__ import annotations

import ast
from collections.abc import Iterator
from pathlib import Path
from typing import Final

import pytest

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_WALKED_TREES: Final[tuple[Path, ...]] = (
    _REPO_ROOT / "eval",
    _REPO_ROOT / "training",
)

# The type whose presence makes a check a first-hand PLACEMENT check, and the
# type whose absence makes it narrow.
_PLACEMENT_TYPE: Final[str] = "SawPlayerObservation"
_MOVEMENT_TYPE: Final[str] = "SawMoveObservation"

# The referee's FROZEN pre-15.19 parity bit. It exists to reproduce the 15.2-era
# lab scorer byte-for-byte, so its vocabulary is the vocabulary at that freeze
# and widening it is the regression Task 16.14's re-pin exists to catch
# (tests/eval/test_watchability.py::
# test_historical_15_2_geomean_parity_frozen_pin_on_9p2i).
_FROZEN_PARITY_BIT: Final[str] = "eval/watchability.py::_testimony_vehicle"

# The shared helper every widened site delegates to. Exempt by name so moving it
# into a walked tree does not make the walk fail against its own definition.
_SHARED_HELPER: Final[str] = "sighting_placement"

# The five sites deliberately left narrow, each with the reason. They gate
# NOTHING (eval/funnel.py:1045 says so in its own comment) while the referee's
# floor and the conviction label do, and `vote_correctness_rate` is a
# doc-fact-gated published number whose movement belongs to a task that owns its
# docstring, its seed-by-seed census and its perturbation test.
_ALLOW_LIST: Final[dict[str, str]] = {
    "eval/vote_correctness.py::_has_kill_witness_chain": (
        "Task 21.9: widening moves the doc-fact-gated vote_correctness_rate, "
        "which belongs to a task that owns its census and perturbation test"
    ),
    "eval/funnel.py::_has_killer_placement_observation": (
        "Task 21.9: a reporting cell that gates nothing (eval/funnel.py:1045)"
    ),
    "eval/funnel.py::_vouch_census": (
        "Task 21.9: a reporting cell that gates nothing (eval/funnel.py:1045)"
    ),
    "eval/deception_instruments.py::_impostor_vouch_census": (
        "Task 21.9: a reporting cell that gates nothing (eval/funnel.py:1045)"
    ),
    "eval/deception_instruments.py::_grounded_split": (
        "Task 21.9: a reporting cell that gates nothing (eval/funnel.py:1045)"
    ),
}


def _isinstance_type_names(node: ast.Call) -> frozenset[str]:
    """The type names one ``isinstance(x, T)`` / ``isinstance(x, (A, B))`` names."""

    if not isinstance(node.func, ast.Name) or node.func.id != "isinstance":
        return frozenset()
    if len(node.args) != 2:
        return frozenset()
    checked = node.args[1]
    entries = checked.elts if isinstance(checked, ast.Tuple) else [checked]
    return frozenset(entry.id for entry in entries if isinstance(entry, ast.Name))


def _narrow_sighting_sites(tree: ast.Module, label: str) -> Iterator[str]:
    """Yield ``path::function`` for every narrow first-hand-sighting check.

    NARROW is the predicate B-9 is about: an ``isinstance`` tuple that admits
    ``SawPlayerObservation`` and OMITS ``SawMoveObservation``. A check over
    ``SawVentObservation`` alone is a different question (is this a vent
    sighting?) and is outside the walk rather than allow-listed; so is a check
    that already names ``SawMoveObservation``.
    """

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name == _SHARED_HELPER:
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            names = _isinstance_type_names(inner)
            if _PLACEMENT_TYPE in names and _MOVEMENT_TYPE not in names:
                yield f"{label}::{node.name}"
                break


def _walk_repo() -> set[str]:
    found: set[str] = set()
    for tree_root in _WALKED_TREES:
        for path in sorted(tree_root.rglob("*.py")):
            label = path.relative_to(_REPO_ROOT).as_posix()
            module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            found.update(_narrow_sighting_sites(module, label))
    return found


def test_the_narrow_sighting_remainder_is_exactly_the_allow_list() -> None:
    """Every narrow first-hand-sighting check is named, with its reason."""

    found = _walk_repo()
    permitted = set(_ALLOW_LIST) | {_FROZEN_PARITY_BIT}

    unexpected = found - permitted
    assert not unexpected, (
        "a first-hand-sighting predicate omits SawMoveObservation and is not "
        "declared: " + ", ".join(sorted(unexpected))
    )
    stale = permitted - found
    assert not stale, (
        "a declared narrow site no longer matches the predicate — delete its "
        "entry rather than leaving it: " + ", ".join(sorted(stale))
    )


def test_the_allow_list_has_exactly_five_entries_each_with_a_reason() -> None:
    """Shrinking or growing the deferral is a deliberate edit, never a drift."""

    assert len(_ALLOW_LIST) == 5
    for site, reason in _ALLOW_LIST.items():
        assert "Task 21.9" in reason, site
        assert (_REPO_ROOT / site.split("::")[0]).exists(), site


def test_the_walk_bites_on_a_planted_new_site(tmp_path: Path) -> None:
    """PLANTED: a sixth narrow site is found, and the two shapes outside are not.

    Proves the predicate is the one B-9 states — a vent-only check and a check
    that already names the movement type are NOT narrow, so they are outside the
    walk rather than quietly allow-listed.
    """

    source = """
def _planted_narrow(turn):
    return any(isinstance(obs, SawPlayerObservation) for obs in turn.observations)


def _planted_narrow_tuple(turn):
    return any(
        isinstance(obs, (SawPlayerObservation, FoundBodyObservation))
        for obs in turn.observations
    )


def _planted_vent_only(turn):
    return any(isinstance(obs, SawVentObservation) for obs in turn.observations)


def _planted_already_wide(turn):
    return any(
        isinstance(obs, (SawPlayerObservation, SawMoveObservation))
        for obs in turn.observations
    )


def sighting_placement(artifact):
    return artifact if isinstance(artifact, SawPlayerObservation) else None
"""
    planted = tmp_path / "planted.py"
    planted.write_text(source, encoding="utf-8")
    found = set(_narrow_sighting_sites(ast.parse(source), "planted.py"))

    assert found == {
        "planted.py::_planted_narrow",
        "planted.py::_planted_narrow_tuple",
    }


@pytest.mark.parametrize("site", sorted(_ALLOW_LIST))
def test_each_allow_listed_site_still_exists_and_is_still_narrow(site: str) -> None:
    """A renamed or deleted entry fails here rather than rotting in the list."""

    relative, _, function = site.partition("::")
    path = _REPO_ROOT / relative
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assert site in set(_narrow_sighting_sites(module, relative))
    assert function
