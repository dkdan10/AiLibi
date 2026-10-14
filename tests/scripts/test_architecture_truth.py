"""The architecture note links the game's rules, and that page names its enforcers.

The rules that shape every game open the observation contract
(``docs/observation-contract.md``), which the architecture note's engine
paragraph links; each rule must keep naming the symbol that enforces it. Every
check runs against the committed pages and against a planted page that has to
make it fire.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHITECTURE = _REPO_ROOT / "docs" / "architecture.md"
_RULES_PAGE = _REPO_ROOT / "docs" / "observation-contract.md"
_RULES_LINK = "](observation-contract.md)"
# The architecture paragraph that sends a reader to the rules.
_ENGINE_PARAGRAPH = "**`engine/`**"

# One enforcing symbol per rule the page states.
_FACT_SYMBOLS: dict[str, str] = {
    "venting is visible": "resolve_vent",
    "impostors never report": "ImpostorPolicy",
    "player-id order and the trigger-tick throwaway": "order_actions_for_tick",
    "every move takes one tick": "traversal_ticks",
    "corpses persist and kill cooldowns pause": "apply_meeting_result",
    "crewmates see one room": "_resolve_observer_visibility_mode",
}

# A task or audit identifier: the page is reader-facing prose (craft rule 4).
_RECORD_ID = re.compile(r"\b[Tt]ask \d|\baudit|\bPR #\d")


def _engine_paragraph(architecture: str) -> str:
    """The architecture note's paragraph on the engine package, or ``""``."""

    return next(
        (
            block
            for block in architecture.split("\n\n")
            if block.startswith(_ENGINE_PARAGRAPH)
        ),
        "",
    )


def _note_problems(note: str, architecture: str) -> list[str]:
    problems = [
        f"the rules page no longer names {symbol} ({fact})"
        for fact, symbol in _FACT_SYMBOLS.items()
        if symbol not in note
    ]
    if _RULES_LINK not in _engine_paragraph(architecture):
        problems.append(
            "docs/architecture.md's engine paragraph no longer links "
            "docs/observation-contract.md"
        )
    problems.extend(
        f"the rules page carries a record identifier: {match.group(0)!r}"
        for match in _RECORD_ID.finditer(note)
    )
    return problems


def test_the_rules_page_names_every_enforcing_symbol() -> None:
    assert (
        _note_problems(
            _RULES_PAGE.read_text(encoding="utf-8"),
            _ARCHITECTURE.read_text(encoding="utf-8"),
        )
        == []
    )


@pytest.mark.parametrize("fact", sorted(_FACT_SYMBOLS))
def test_a_page_missing_one_fact_symbol_is_rejected(fact: str) -> None:
    # Planted: the committed page with one rule's enforcing symbol removed.
    symbol = _FACT_SYMBOLS[fact]
    note = _RULES_PAGE.read_text(encoding="utf-8")
    assert symbol in note
    planted = note.replace(symbol, "")
    problems = _note_problems(planted, _ARCHITECTURE.read_text(encoding="utf-8"))
    assert f"the rules page no longer names {symbol} ({fact})" in problems


def test_an_engine_paragraph_linking_the_retired_page_is_rejected() -> None:
    # Planted: the engine paragraph pointing back at the page the rules left.
    # The note's other link to the contract stays, so only this paragraph counts.
    architecture = _ARCHITECTURE.read_text(encoding="utf-8")
    paragraph = _engine_paragraph(architecture)
    assert _RULES_LINK in paragraph
    planted = architecture.replace(
        paragraph, paragraph.replace(_RULES_LINK, "](game-shape.md)")
    )
    assert _RULES_LINK in planted
    assert _note_problems(_RULES_PAGE.read_text(encoding="utf-8"), planted) == [
        "docs/architecture.md's engine paragraph no longer links "
        "docs/observation-contract.md"
    ]


def test_a_page_carrying_a_task_id_is_rejected() -> None:
    note = _RULES_PAGE.read_text(encoding="utf-8") + "\nSee Task 10.8.\n"
    assert _note_problems(note, _ARCHITECTURE.read_text(encoding="utf-8")) == [
        "the rules page carries a record identifier: 'Task 1'"
    ]
