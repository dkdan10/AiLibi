"""Validate the work cards and the task index's card inventory.

The card check is structural; acceptance evidence still needs review. The
index's card counts are checked here too, against the same cards: its totals
were hand-maintained and no gate read them, so a card flipped to ``active``
broke the index silently.
"""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"

_CARD_STATUSES = ("ready", "active", "done")
_STATUS_LINE = re.compile(r"^\*\*Status:\*\* (.*)$", re.MULTILINE)

# The index's ONE card-inventory sentence. Its numbers are re-derived from the
# cards below, and the as-of stamp keeps a count that ages without an edit from
# reading as a standing measurement.
_TASK_INDEX = "README.md"
_INVENTORY_SENTENCE = re.compile(
    r"As of (\d{4}-\d{2}-\d{2}), `tasks/work/` holds (\d+) cards: ([^.]+)\."
)
# One breakdown item, matched END TO END: a search would let a repeated status
# and any prose between two items pass through unread, so a number the index
# displays would never reach the tally.
_INVENTORY_ITEM = re.compile(r"(\d+) ([a-z]+)")


def parse_inventory_breakdown(breakdown: str) -> tuple[dict[str, int], str | None]:
    """The breakdown sentence as ``{status: count}``, or the reason it is not.

    Every number the index displays has to be one this gate compares. Scanning
    for ``<count> <status>`` pairs did not do that: ``999 ready, 2 ready`` kept
    only the last pair, and ``2 ready and 900 more, 1 done`` dropped the text
    between items, so a README could show a fabricated count with the gate
    green. Each comma-separated item is matched whole instead, and a repeated
    status is refused rather than merged.
    """

    claimed: dict[str, int] = {}
    for item in breakdown.split(","):
        stripped = item.strip()
        match = _INVENTORY_ITEM.fullmatch(stripped)
        if match is None:
            return claimed, f"{stripped!r} is not a '<count> <status>' item"
        count, status = match.groups()
        if status in claimed:
            return claimed, f"{status!r} is counted more than once"
        claimed[status] = int(count)
    return claimed, None


def main() -> int:
    errors: list[str] = []
    work_count = validate_work_cards(TASKS_DIR / "work", errors)
    validate_card_inventory(TASKS_DIR, errors)

    if errors:
        print_errors(errors)
        return 1

    print(f"Task docs validation passed: {work_count} work cards.")
    return 0


def validate_work_cards(directory: Path, errors: list[str]) -> int:
    """Check card structure and completion declarations, not evidence quality."""

    paths = sorted(directory.glob("*.md"))
    if not paths:
        # A missing or emptied folder means the gate is pointed at the wrong
        # place; checking nothing must not read as a pass.
        raise FileNotFoundError(f"{directory}: no work cards to validate.")
    for path in paths:
        body = _without_fenced_content(path.read_text())
        if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.stem) is None:
            errors.append(f"{path}: use a lowercase, hyphen-separated card name.")
        if len(re.findall(r"^# \S.*$", body, re.MULTILINE)) != 1:
            errors.append(f"{path}: expected one # title.")
        statuses = re.findall(r"^\*\*Status:\*\* (.*)$", body, re.MULTILINE)
        if len(statuses) != 1 or statuses[0] not in {"ready", "active", "done"}:
            errors.append(f"{path}: expected one Status: ready, active, or done.")

        sections: dict[str, str] = {}
        for block in re.split(r"^## ", body, flags=re.MULTILINE)[1:]:
            heading, _, content = block.partition("\n")
            if heading in sections:
                errors.append(f"{path}: duplicate section {heading!r}.")
            sections[heading] = content.strip()
        for heading in (
            "Outcome",
            "Evidence",
            "Acceptance",
            "Constraints",
            "Expected scope",
            "Record impact",
            "Validation",
        ):
            if not sections.get(heading):
                errors.append(f"{path}: missing or empty ## {heading}.")

        checks = re.findall(
            r"^[ \t]*(?:[-*+]|\d+[.)]) \[([^\]]*)\] \S.*$",
            sections.get("Acceptance", ""),
            re.MULTILINE,
        )
        if not checks:
            errors.append(f"{path}: Acceptance needs at least one checkbox.")
        if any(check not in {" ", "x", "X"} for check in checks):
            errors.append(f"{path}: Acceptance checkbox must be [ ] or [x].")
        if statuses == ["done"]:
            if " " in checks:
                errors.append(f"{path}: done card has unchecked acceptance items.")
            if not sections.get("Results"):
                errors.append(f"{path}: done card needs ## Results with evidence.")
    return len(paths)


def card_statuses(directory: Path) -> Counter[str]:
    """Tally the ``**Status:**`` of every card in ``directory``."""

    tally: Counter[str] = Counter()
    for path in sorted(directory.glob("*.md")):
        statuses = _STATUS_LINE.findall(_without_fenced_content(path.read_text()))
        if len(statuses) == 1 and statuses[0] in _CARD_STATUSES:
            tally[statuses[0]] += 1
    return tally


def _index_label(path: Path) -> str:
    """The index path as the repo sees it, or as given from another tree."""

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def validate_card_inventory(tasks_dir: Path, errors: list[str]) -> None:
    """The task index's card counts, re-derived from the cards themselves.

    ``tasks/README.md`` is the file AGENTS.md sends every reader to, and its
    inventory was typed: the total and the per-status counts could be set to
    anything with every gate green, and flipping one card's Status broke them
    with nothing to notice. Both are recomputed here from the same
    ``tasks/work/*.md`` files the card check just parsed, so the index cannot
    drift from the queue it describes.

    Cards whose own Status line is missing or unrecognised are reported by
    :func:`validate_work_cards`; they are absent from this tally, so the
    numbers here always describe well-formed cards. The breakdown is read whole
    by :func:`parse_inventory_breakdown`, so no displayed number escapes the
    comparison.
    """

    index_path = tasks_dir / _TASK_INDEX
    try:
        index = index_path.read_text()
    except OSError as error:
        errors.append(f"{_index_label(index_path)}: unreadable ({error}).")
        return
    tally = card_statuses(tasks_dir / "work")
    expected = ", ".join(
        f"{tally[status]} {status}" for status in _CARD_STATUSES if tally[status]
    )
    sentence = (
        f"As of <date>, `tasks/work/` holds {sum(tally.values())} cards: {expected}."
    )
    # Matched over collapsed whitespace so the sentence may wrap in the file.
    matches = _INVENTORY_SENTENCE.findall(" ".join(index.split()))
    if len(matches) != 1:
        errors.append(
            f"{_index_label(index_path)}: expected exactly one card-inventory "
            f"sentence of the form {sentence!r}, found {len(matches)}. The "
            "index's counts are derived from tasks/work/*.md, so the sentence "
            "has to be there to derive them into."
        )
        return
    stamp, total, breakdown = matches[0]
    try:
        date.fromisoformat(stamp)
    except ValueError:
        errors.append(
            f"{_index_label(index_path)}: the card inventory is stamped "
            f"'as of {stamp}', which is not a calendar date."
        )
    if int(total) != sum(tally.values()):
        errors.append(
            f"{_index_label(index_path)}: the card inventory says {total} cards, "
            f"but tasks/work/ holds {sum(tally.values())}."
        )
    claimed, malformed = parse_inventory_breakdown(breakdown)
    if malformed is not None:
        errors.append(
            f"{_index_label(index_path)}: the card inventory breakdown "
            f"{breakdown!r} is not a comma-separated list of '<count> <status>' "
            f"items — {malformed}. Every number the index shows has to be one "
            f"this check derives; expected {expected!r}."
        )
        return
    if claimed != {status: count for status, count in tally.items() if count}:
        errors.append(
            f"{_index_label(index_path)}: the card inventory breaks down as "
            f"{breakdown!r}, but tasks/work/ holds {expected}."
        )


def _without_fenced_content(body: str) -> str:
    """Ignore example syntax while retaining fences as nonempty section content."""

    lines: list[str] = []
    fence: str | None = None
    for line in body.splitlines():
        if fence is not None:
            if re.fullmatch(
                rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line
            ):
                fence = None
                lines.append(line)
            continue
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match is not None:
            fence = match.group(1)
        lines.append(line)
    return "\n".join(lines)


def print_errors(errors: list[str]) -> None:
    print("Task docs validation failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
