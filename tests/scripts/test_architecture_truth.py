"""The architecture note links the game's shape, and that page names its enforcers.

The game-shape facts live on their own page (``docs/game-shape.md``, linked
from one architecture sentence); each fact must keep naming the symbol that
enforces it. Every check runs against the committed page and against a planted
page that has to make it fire.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ARCHITECTURE = _REPO_ROOT / "docs" / "architecture.md"
_GAME_SHAPE = _REPO_ROOT / "docs" / "game-shape.md"
_GAME_SHAPE_LINK = "](game-shape.md)"

# One enforcing symbol per fact the note states.
_FACT_SYMBOLS: dict[str, str] = {
    "venting is visible": "resolve_vent",
    "impostors never report": "ImpostorPolicy",
    "player-id order and the trigger-tick throwaway": "order_actions_for_tick",
    "corpses persist and kill cooldowns pause": "apply_meeting_result",
    "crewmates see one room": "_resolve_observer_visibility_mode",
}

# A task or audit identifier: the note is reader-facing prose (craft rule 4).
_RECORD_ID = re.compile(r"\b[Tt]ask \d|\baudit|\bPR #\d")


def _note_problems(note: str, architecture: str) -> list[str]:
    problems = [
        f"the game-shape note no longer names {symbol} ({fact})"
        for fact, symbol in _FACT_SYMBOLS.items()
        if symbol not in note
    ]
    if _GAME_SHAPE_LINK not in architecture:
        problems.append("docs/architecture.md no longer links docs/game-shape.md")
    problems.extend(
        f"the game-shape note carries a record identifier: {match.group(0)!r}"
        for match in _RECORD_ID.finditer(note)
    )
    return problems


def test_the_game_shape_note_names_every_enforcing_symbol() -> None:
    assert (
        _note_problems(
            _GAME_SHAPE.read_text(encoding="utf-8"),
            _ARCHITECTURE.read_text(encoding="utf-8"),
        )
        == []
    )


@pytest.mark.parametrize("fact", sorted(_FACT_SYMBOLS))
def test_a_note_missing_one_fact_symbol_is_rejected(fact: str) -> None:
    # Planted: the committed note with one fact's enforcing symbol removed.
    symbol = _FACT_SYMBOLS[fact]
    note = _GAME_SHAPE.read_text(encoding="utf-8")
    assert symbol in note
    planted = note.replace(symbol, "")
    problems = _note_problems(planted, _ARCHITECTURE.read_text(encoding="utf-8"))
    assert f"the game-shape note no longer names {symbol} ({fact})" in problems


def test_an_architecture_page_without_the_link_is_rejected() -> None:
    architecture = _ARCHITECTURE.read_text(encoding="utf-8")
    assert _GAME_SHAPE_LINK in architecture
    planted = architecture.replace(_GAME_SHAPE_LINK, "](observation-contract.md)")
    assert _note_problems(_GAME_SHAPE.read_text(encoding="utf-8"), planted) == [
        "docs/architecture.md no longer links docs/game-shape.md"
    ]


def test_a_note_carrying_a_task_id_is_rejected() -> None:
    note = _GAME_SHAPE.read_text(encoding="utf-8") + "\nSee Task 10.8.\n"
    assert _note_problems(note, _ARCHITECTURE.read_text(encoding="utf-8")) == [
        "the game-shape note carries a record identifier: 'Task 1'"
    ]
