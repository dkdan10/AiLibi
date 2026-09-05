"""Planted invalid cards prove the prospective workflow check rejects them."""

from __future__ import annotations

from pathlib import Path

import pytest

import validate_task_docs


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
