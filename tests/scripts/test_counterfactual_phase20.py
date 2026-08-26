"""The offline counterfactual, after the levers it priced graduated.

The script computed an OFF-vs-ON table by toggling each Phase-20 lever through
its resolver's ``env`` parameter. The baseline-7 record graduated all eight to
unconditional (audits/audit-phase-20-baseline-7.md §6.1), so a graduated
resolver ignores that parameter and the OFF column would silently BE the ON
column — a table that looks like a counterfactual and is not one.

Three things are pinned here:

1. the script still names the eight levers it priced, so the memo's slate stays
   legible after the registry stopped listing them;
2. it REFUSES to run rather than emitting an OFF column it cannot produce, and
   the refusal names every graduated lever and where the ruling is;
3. the memo it produced is still committed and still carries the table, frozen
   as the pre-record prediction it was.

Each gate ships with a planted case proving it bites.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

import pytest

from orchestrator.replay import (
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    env_var_for_lever,
    substrate_flag_snapshot,
)

import counterfactual_phase20 as cf

_REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
_MEMO: Final[Path] = _REPO_ROOT / "audits" / "audit-phase-20-counterfactual.md"
_FAST_SET: Final[str] = "samples/4p1i"


def test_the_slate_is_the_eight_levers_the_memo_priced() -> None:
    assert cf.PHASE_20_LEVERS == (
        "task_completion_from_events",
        "self_location_trail",
        "movement_claim_shape",
        "grounded_prosecution",
        "map_aware_arbitration",
        "structured_turn_markers",
        "meeting_outcome_memory",
        "coalesced_memory_render",
    )
    # None of them is a live toggle any more -- which is exactly why the OFF
    # column is gone. The impostor-answer arm is the one that survives.
    assert set(cf.PHASE_20_LEVERS) & set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS) == set()
    assert cf.NON_PHASE_20_LEVER in TOGGLEABLE_SUBSTRATE_FLAG_KEYS


def test_every_priced_lever_now_reads_on_under_an_empty_env() -> None:
    # The premise of the refusal, asserted rather than assumed: passing an empty
    # env -- the OFF leg's own argument -- returns True for all eight.
    snapshot = substrate_flag_snapshot({})
    assert [snapshot[key] for key in cf.PHASE_20_LEVERS] == [True] * 8


def test_the_run_refuses_and_names_the_graduation() -> None:
    with pytest.raises(SystemExit) as excinfo:
        cf.run([_FAST_SET])
    message = str(excinfo.value)
    assert "the OFF column cannot be produced" in message
    assert "graduated to unconditionally ON at the baseline-7 record" in message
    assert "audits/audit-phase-20-baseline-7.md" in message
    for key in cf.PHASE_20_LEVERS:
        assert key in message
        assert env_var_for_lever(key) in message


def test_the_refusal_lifts_when_nothing_is_graduated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The planted case craft rule 2 asks for: the guard is a real predicate over
    # the live registry, not an unconditional raise. Point it at a lever nobody
    # graduated and it passes.
    monkeypatch.setattr(cf, "PHASE_20_LEVERS", (cf.NON_PHASE_20_LEVER,))
    cf._assert_ambient_slate_is_off("in the planted case")


def test_the_memo_is_committed_and_still_carries_its_table() -> None:
    # The prediction outlives the instrument: the record is read against what
    # this memo committed to in advance, so it must stay findable.
    text = _MEMO.read_text(encoding="utf-8")
    assert "scripts/counterfactual_phase20.py" in text
    assert "| OFF |" in text or "OFF" in text
