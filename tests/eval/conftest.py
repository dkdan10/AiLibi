"""Session-scoped instrument reports shared by more than one eval test module.

A committed-set walk that two modules both need is the case a package fixture
answers: it gives the walk one name, one scope and one obvious place to look.
The walk and its per-worker cache live in ``tests/_helpers/committed.py``; this
file is the fixture-shaped door onto it for ``tests/eval/``.

Only the genuinely shared walks belong here. The single-module instruments keep
their fixtures beside their pins, because their fixture names are taken by a
different type in a sibling module (``corpus_nine`` is a
``DeceptionInstrumentsReport`` in test_deception_instruments.py and an
``OffMenuActionReport`` in test_off_menu.py; ``samples_9p2i`` is a
``SolvabilityReport`` in test_solvability.py and a ``TournamentEvalReport`` in
test_deduction_metrics.py) — hoisting those names would make the wrong object
reachable by the right name. They lose nothing by staying: the shared cache, not
the fixture scope, is what makes each walk happen once per worker.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests._helpers.committed import SAMPLES_4P1I, kill_craft_report

if TYPE_CHECKING:
    from eval.kill_craft import KillCraftReport


@pytest.fixture(scope="session")
def committed_kill_craft_4p1i() -> "KillCraftReport":
    """The 4p1i sample set's kill-craft report.

    Two pins read it: the kill-craft fold's own cells, and the deduction
    metrics' evidence-supply adoption, which asserts that the block it publishes
    was copied from this walk rather than recomputed.
    """

    return kill_craft_report(SAMPLES_4P1I)
