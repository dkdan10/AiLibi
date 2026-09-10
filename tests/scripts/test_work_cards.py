"""Planted invalid cards prove the prospective workflow check rejects them."""

from __future__ import annotations

from pathlib import Path

import pytest

import validate_task_docs
from _task_parser import TASKS_DIR


_CARD = """# Account for spent tokens

**Status:** active

## Outcome
Reported usage counts after an invalid response.
## Evidence
An injected transport returns invalid JSON with usage.
## Acceptance
- [ ] Invalid output consumes its reported usage.
## Constraints
No real provider calls.
## Expected scope
llm/budgeted_client.py and its tests.
## Record impact
Future failed calls can reach the cap earlier.
## Validation
Run the injected-transport regression and the full check.
"""


def _validate(tmp_path: Path, body: str) -> list[str]:
    (tmp_path / "accounting.md").write_text(body)
    errors: list[str] = []
    assert validate_task_docs.validate_work_cards(tmp_path, errors) == 1
    return errors


def test_active_card_needs_no_generated_prompt(tmp_path: Path) -> None:
    assert _validate(tmp_path, _CARD) == []


@pytest.mark.parametrize(
    ("old", "new", "diagnostic"),
    [
        ("# Account for spent tokens", "", "one # title"),
        ("**Status:** active", "**Status:** guessed", "one Status"),
        ("## Evidence", "## Background", "empty ## Evidence"),
        (
            "## Record impact\nFuture failed calls can reach the cap earlier.",
            "## Record impact",
            "empty ## Record impact",
        ),
        ("- [ ] Invalid", "Invalid", "at least one checkbox"),
        ("**Status:** active", "**Status:** done", "unchecked acceptance"),
        ("**Status:** active", "**Status:** done", "needs ## Results"),
    ],
)
def test_perturbed_card_is_rejected(
    tmp_path: Path, old: str, new: str, diagnostic: str
) -> None:
    errors = _validate(tmp_path, _CARD.replace(old, new))
    assert any(diagnostic in error for error in errors)


def test_duplicate_section_is_rejected(tmp_path: Path) -> None:
    errors = _validate(tmp_path, _CARD + "\n## Evidence\nA different account.\n")
    assert any("duplicate section 'Evidence'" in error for error in errors)


@pytest.mark.parametrize("bullet", ["*", "+", "  -", "1.", "2)"])
def test_done_card_rejects_unchecked_alternative_bullets(
    tmp_path: Path, bullet: str
) -> None:
    body = _CARD.replace("active", "done").replace(
        "- [ ] Invalid output consumes its reported usage.",
        f"- [x] Usage is recorded.\n{bullet} [ ] Recovery still needs verification.",
    )
    errors = _validate(tmp_path, body + "\n## Results\nPartial verification.")
    assert any("unchecked acceptance" in error for error in errors)


def test_unknown_checkbox_state_is_rejected(tmp_path: Path) -> None:
    errors = _validate(tmp_path, _CARD.replace("[ ]", "[?]"))
    assert any("checkbox must be" in error for error in errors)


@pytest.mark.parametrize("fence", ["```", "~~~", "````"])
def test_fenced_example_is_not_document_structure(tmp_path: Path, fence: str) -> None:
    body = _CARD.replace(
        "An injected transport returns invalid JSON with usage.",
        f"{fence}sh\n# Reproduce the failure\n## Outcome\n"
        f"**Status:** example\nuv run pytest tests/llm\n{fence}",
    )
    assert _validate(tmp_path, body) == []


def test_fenced_checked_example_does_not_satisfy_acceptance(tmp_path: Path) -> None:
    body = _CARD.replace(
        "- [ ] Invalid output consumes its reported usage.",
        "```md\n- [x] Example only.\n```",
    )
    assert any("at least one checkbox" in error for error in _validate(tmp_path, body))


def test_done_card_declares_evidence_and_completed_checks(tmp_path: Path) -> None:
    body = _CARD.replace("active", "done").replace("- [ ]", "- [x]")
    assert (
        _validate(tmp_path, body + "\n## Results\nRegression and full check passed.")
        == []
    )


def test_missing_card_inventory_is_rejected(tmp_path: Path) -> None:
    errors: list[str] = []
    assert validate_task_docs.validate_work_cards(tmp_path / "missing", errors) == 0
    assert any("expected at least one work card" in error for error in errors)


def test_main_validates_cards_alongside_historical_contracts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Keep the real historical contracts and prompt validation; redirect only
    # the new card inventory to a planted incomplete card.
    cards = tmp_path / "work"
    cards.mkdir()
    (cards / "incomplete.md").write_text("# Missing contract\n")
    monkeypatch.setattr(validate_task_docs, "TASKS_DIR", tmp_path)
    assert validate_task_docs.main() == 1


_INDEX = """# Task index

As of 2026-09-09, `tasks/work/` holds {total} cards: {breakdown}.
"""


def _index_tree(tmp_path: Path, *statuses: str, index: str | None = None) -> Path:
    """A tasks/ tree with one card per status and a derived index sentence."""

    cards = tmp_path / "work"
    cards.mkdir()
    for number, status in enumerate(statuses):
        (cards / f"card-{number}.md").write_text(
            _CARD.replace("**Status:** active", f"**Status:** {status}")
        )
    if index is None:
        order = [
            f"{statuses.count(status)} {status}"
            for status in ("ready", "active", "done")
            if statuses.count(status)
        ]
        index = _INDEX.format(total=len(statuses), breakdown=", ".join(order))
    (tmp_path / "README.md").write_text(index)
    return tmp_path


def test_card_inventory_is_derived_from_the_cards(tmp_path: Path) -> None:
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(
        _index_tree(tmp_path, "ready", "done", "done"), errors
    )
    assert errors == []


def test_flipped_card_status_breaks_the_index(tmp_path: Path) -> None:
    # The planted proof: a card moves to active and nobody touches the index.
    tasks = _index_tree(tmp_path, "ready", "done", "done")
    card = tasks / "work" / "card-0.md"
    card.write_text(card.read_text().replace("**Status:** ready", "**Status:** active"))
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(tasks, errors)
    assert len(errors) == 1
    assert "breaks down as '1 ready, 2 done'" in errors[0]
    assert "holds 1 active, 2 done" in errors[0]


def test_repeated_status_in_the_breakdown_is_rejected(tmp_path: Path) -> None:
    # The planted proof for the whole-breakdown parse: scanning for pairs kept
    # only the LAST '<count> ready', so a README could display 999 ready cards
    # while the tally it was compared against read 2.
    tasks = _index_tree(
        tmp_path,
        "ready",
        "ready",
        "done",
        index=_INDEX.format(total=3, breakdown="999 ready, 2 ready, 1 done"),
    )
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(tasks, errors)
    assert len(errors) == 1
    assert "'ready' is counted more than once" in errors[0]


def test_unmatched_text_in_the_breakdown_is_rejected(tmp_path: Path) -> None:
    # Prose between two valid items was discarded, so anything could sit in the
    # sentence unread. Each comma-separated item must now match end to end.
    tasks = _index_tree(
        tmp_path,
        "ready",
        "ready",
        "done",
        index=_INDEX.format(total=3, breakdown="2 ready and lots else, 1 done"),
    )
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(tasks, errors)
    assert len(errors) == 1
    assert "'2 ready and lots else' is not a '<count> <status>' item" in errors[0]


def test_wrong_card_total_is_rejected(tmp_path: Path) -> None:
    tasks = _index_tree(
        tmp_path,
        "done",
        "done",
        index=_INDEX.format(total=99, breakdown="2 done"),
    )
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(tasks, errors)
    assert len(errors) == 1
    assert "says 99 cards, but tasks/work/ holds 2" in errors[0]


def test_missing_inventory_sentence_is_rejected(tmp_path: Path) -> None:
    tasks = _index_tree(tmp_path, "done", index="# Task index\n\nNo counts here.\n")
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(tasks, errors)
    assert len(errors) == 1
    assert "expected exactly one card-inventory sentence" in errors[0]


def test_unstamped_inventory_sentence_is_rejected(tmp_path: Path) -> None:
    # The stamp's shape is checked: a count that ages without an edit must say
    # when it was true.
    tasks = _index_tree(
        tmp_path,
        "done",
        index="# Task index\n\n`tasks/work/` holds 1 cards: 1 done.\n",
    )
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(tasks, errors)
    assert len(errors) == 1
    assert "expected exactly one card-inventory sentence" in errors[0]


def test_inventory_sentence_may_wrap_in_the_file(tmp_path: Path) -> None:
    tasks = _index_tree(
        tmp_path,
        "done",
        "done",
        index="# Task index\n\nAs of 2026-09-09, `tasks/work/` holds 2\ncards: 2\ndone.\n",
    )
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(tasks, errors)
    assert errors == []


def test_committed_task_index_matches_its_cards() -> None:
    errors: list[str] = []
    validate_task_docs.validate_card_inventory(TASKS_DIR, errors)
    assert errors == []
