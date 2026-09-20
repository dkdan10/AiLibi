"""The featured-criterion instrument, over the committed bytes it reads.

``scripts/measure_featured_criterion.py`` prints the counts the spectator's
featured order rests on. Two of its claims are load-bearing enough to pin here:

* ``alternatives_shape`` — the spectator's ballot card ANNOTATES a recorded
  alternative that duplicates the card's own header (the voter itself, or the
  target the vote applied to). That render is a statement about the recordings,
  so the committed games that carry each shape are named here rather than left
  to a reviewer's trust;
* ``_parse_games`` — a malformed selector raises instead of quietly measuring
  fewer games than the caller asked for, which would print a number nobody
  could reproduce.

The ejection bands themselves are pinned on the other side of the fence, in
``tests/api/test_sets.py``, which re-implements the predicate deliberately.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

import pytest

from api.replay_loader import SetLoaderRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT = _REPO_ROOT / "replays" / "samples"

# `scripts/` is not a package; import the module the way the other script tests
# in this directory do.
_SCRIPTS = _REPO_ROOT / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
_criterion: Any = importlib.import_module("measure_featured_criterion")


@pytest.mark.parametrize(
    "seed,shape,why",
    [
        # (ballots, recorded entries, ballots naming the voter, naming the target)
        (2, (7, 13, 2, 0), "two voters list THEMSELVES in the first meeting"),
        (13, (18, 35, 1, 2), "one lists itself; two list the target they voted"),
        (23, (26, 36, 0, 0), "the tour's landing game carries neither shape"),
    ],
)
def test_alternatives_shape_reads_the_committed_duplicates(
    seed: int, shape: tuple[int, int, int, int], why: str
) -> None:
    # The annotation in `frontend/src/components/BallotCard.tsx` exists because
    # these bytes exist. Seed 2 is the case in the flesh: p-1 and p-5 each record
    # THEMSELVES among the players they weighed, which without a note renders as
    # a second identical pill beside the one in the ballot's header.
    replay = SetLoaderRegistry(_PARENT).get("9p2i").load_replay(f"headless-seed-{seed}")
    assert _criterion.alternatives_shape(replay) == shape


def test_parse_games_rejects_a_malformed_selector() -> None:
    assert _criterion._parse_games(["9p2i:23", "9p2i:13", "4p1i:2"]) == {
        "9p2i": frozenset({23, 13}),
        "4p1i": frozenset({2}),
    }
    for bad in ("9p2i", "9p2i:", ":23", "9p2i:head", ""):
        with pytest.raises(ValueError):
            _criterion._parse_games([bad])
