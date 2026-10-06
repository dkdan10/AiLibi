"""The reopening's re-pricing note stays written where a reopening reads it.

Two texts carry it: one dated paragraph in ``training/README.md`` section 7 (the
reopening checklist) and a clause in the comment directly above
``correct_reports = sum(`` in ``training/rewards.py``. Both say that a reopening
re-prices the two role-correct crew terms role-blind before any search, under a
new ``FITNESS_OBJECTIVE_ID``, and re-registers the conviction GO verdict. The
gate reads file bytes and imports nothing from ``training/``. Each check runs on
the committed files and on fixed planted texts that must make it fire.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_README = _REPO_ROOT / "training" / "README.md"
_REWARDS = _REPO_ROOT / "training" / "rewards.py"

_OPENING = "**Dated 2026-10-06"
_SECTION = "## 7."
_PARAGRAPH_TERMS: tuple[str, ...] = (
    "correct_reports",
    "patrol_coverage",
    "FITNESS_OBJECTIVE_ID",
    "role-blind",
    "before any search",
    "2026-07-09",
    "training/artifacts/conviction/verdict.json",
)
_ANCHOR = "correct_reports = sum("
_COMMENT_TERMS: tuple[str, ...] = (
    "role-blind",
    "FITNESS_OBJECTIVE_ID",
    "before any search",
    "conviction",
    "2026-07-09",
)


def _paragraphs(text: str) -> list[str]:
    return [" ".join(block.split()) for block in re.split(r"\n\s*\n", text)]


def _section(text: str, heading: str) -> str:
    """The body of the one ``## `` section whose heading starts with ``heading``."""

    starts = [
        match.start()
        for match in re.finditer(r"^## ", text, flags=re.MULTILINE)
        if text.startswith(heading, match.start())
    ]
    if len(starts) != 1:
        return ""
    following = re.search(r"^## ", text[starts[0] + 1 :], flags=re.MULTILINE)
    end = len(text) if following is None else starts[0] + 1 + following.start()
    return text[starts[0] : end]


def _readme_problems(text: str) -> list[str]:
    everywhere = [p for p in _paragraphs(text) if p.startswith(_OPENING)]
    in_section = [
        p for p in _paragraphs(_section(text, _SECTION)) if p.startswith(_OPENING)
    ]
    if len(in_section) != 1:
        return [f"section 7 holds {len(in_section)} paragraphs opening {_OPENING!r}"]
    if len(everywhere) != 1:
        return [f"the README holds {len(everywhere)} paragraphs opening {_OPENING!r}"]
    return [
        f"the dated paragraph does not name {term!r}"
        for term in _PARAGRAPH_TERMS
        if term not in in_section[0]
    ]


def _comment_above_anchor(source: str) -> str:
    lines = source.splitlines()
    anchors = [i for i, line in enumerate(lines) if line.strip().startswith(_ANCHOR)]
    if len(anchors) != 1:
        return ""
    block: list[str] = []
    for line in reversed(lines[: anchors[0]]):
        if not line.strip().startswith("#"):
            break
        block.append(line.strip().removeprefix("#"))
    return " ".join(" ".join(reversed(block)).split())


def _comment_problems(source: str) -> list[str]:
    comment = _comment_above_anchor(source)
    if not comment:
        return [f"no comment block directly above {_ANCHOR!r}"]
    return [
        f"the comment above {_ANCHOR!r} does not name {term!r}"
        for term in _COMMENT_TERMS
        if term not in comment
    ]


# A fixed README shaped as the committed one: section 7's last check, the dated
# paragraph, the decide-at-proposal paragraph, then section 8.
_PARAGRAPH = """**Dated 2026-10-06: the objective is re-priced before any search.** Any
reopening re-prices the crew terms `correct_reports` and `patrol_coverage`
(`training/rewards.py`, `_crew_terms`) role-blind before any search, under a
new `FITNESS_OBJECTIVE_ID`. This supersedes in writing the 2026-07-09
ratification. The conviction model's GO verdict
(`training/artifacts/conviction/verdict.json`) is re-registered at that
reopening.
"""
_BEFORE = """## 7. THE REOPENING CHECKLIST

4. **Adequate screening sample sizes and replication.** Screens must be sized.

"""
_AFTER = """
**Decide-at-proposal.** A re-open proposal must name its route.

## 8. APPENDIX

The recorded campaign invocations.
"""
_README_GOOD = _BEFORE + _PARAGRAPH + _AFTER

# A fixed comment shaped as the committed one, with and without the clause.
_COMMENT_GOOD = """    initial_crew = max(1, rollout.num_players - rollout.num_impostors)
    # Role-correct rewards: ``correct_reports`` and ``patrol_coverage`` both pay
    # crew-conduct term. Their values and weights are unchanged while ML work is
    # held (owner ruling of 2026-09-24). Any reopening re-prices both role-blind
    # before any search, under a new ``FITNESS_OBJECTIVE_ID``, and re-registers
    # the conviction GO verdict with them (``training/README.md`` section 7,
    # which supersedes the 2026-07-09 ratification of this engine-truth proxy).
    #
    # correctly-routed reports: count only meetings a crewmate ROUTED via a body
    correct_reports = sum(
"""
_COMMENT_WITHOUT_CLAUSE = """    initial_crew = max(1, rollout.num_players - rollout.num_impostors)
    # Role-correct rewards: ``correct_reports`` and ``patrol_coverage`` both pay
    # crew-conduct term. Their values and weights are unchanged while ML work is
    # held (owner ruling of 2026-09-24).
    #
    # correctly-routed reports: count only meetings a crewmate ROUTED via a body
    correct_reports = sum(
"""


def test_the_committed_readme_carries_the_dated_paragraph_in_section_7() -> None:
    assert _readme_problems(_README.read_text(encoding="utf-8")) == []


def test_the_committed_comment_carries_the_clause() -> None:
    assert _comment_problems(_REWARDS.read_text(encoding="utf-8")) == []


def test_the_fixed_texts_pass_so_the_planted_cases_are_not_vacuous() -> None:
    assert _readme_problems(_README_GOOD) == []
    assert _comment_problems(_COMMENT_GOOD) == []


def test_a_removed_paragraph_is_rejected() -> None:
    assert _readme_problems(_BEFORE + _AFTER) == [
        "section 7 holds 0 paragraphs opening '**Dated 2026-10-06'"
    ]


def test_a_paragraph_moved_into_section_8_is_rejected() -> None:
    moved = _BEFORE + _AFTER + "\n" + _PARAGRAPH
    assert _readme_problems(moved) == [
        "section 7 holds 0 paragraphs opening '**Dated 2026-10-06'"
    ]


def test_a_paragraph_without_patrol_coverage_is_rejected() -> None:
    missing = _README_GOOD.replace(
        "`correct_reports` and `patrol_coverage`", "`correct_reports`"
    )
    assert _readme_problems(missing) == [
        "the dated paragraph does not name 'patrol_coverage'"
    ]


def test_a_doubled_paragraph_is_rejected() -> None:
    doubled = _BEFORE + _PARAGRAPH + "\n" + _PARAGRAPH + _AFTER
    assert _readme_problems(doubled) == [
        "section 7 holds 2 paragraphs opening '**Dated 2026-10-06'"
    ]
    copied = _README_GOOD + "\n" + _PARAGRAPH
    assert _readme_problems(copied) == [
        "the README holds 2 paragraphs opening '**Dated 2026-10-06'"
    ]


def test_the_comment_without_the_clause_is_rejected() -> None:
    assert _comment_problems(_COMMENT_WITHOUT_CLAUSE) == [
        "the comment above 'correct_reports = sum(' does not name 'role-blind'",
        "the comment above 'correct_reports = sum(' does not name "
        "'FITNESS_OBJECTIVE_ID'",
        "the comment above 'correct_reports = sum(' does not name 'before any search'",
        "the comment above 'correct_reports = sum(' does not name 'conviction'",
        "the comment above 'correct_reports = sum(' does not name '2026-07-09'",
    ]


def test_a_clause_moved_off_the_anchor_is_rejected() -> None:
    detached = _COMMENT_GOOD.replace(
        "    correct_reports = sum(\n", "    total = 0\n    correct_reports = sum(\n"
    )
    assert _comment_problems(detached) == [
        "no comment block directly above 'correct_reports = sum('"
    ]
