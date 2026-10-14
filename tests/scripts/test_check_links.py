"""Unit tests for scripts/check_links.py.

The link parser reads rendered links only, the default scope is the live pages,
and a broken link on a page in scope fails the run. The live pages hold no
broken link at the committed head.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import check_links

_REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "example",
    [
        "`[example](missing.md)`",
        "``[example](missing.md) with ` inside``",
        "`a multiline\n[example](missing.md) code span`",
        "```md\n[example](missing.md)\n```",
        "~~~md\n[example](missing.md)\n~~~~",
        "````md\n```\n[example](missing.md)\n````",
        "```md\n[example](missing.md)\n",
        "> ```md\n> [example](missing.md)\n",
        "    [example](missing.md)",
        r"\\`[example](missing.md)`",
    ],
)
def test_relative_links_ignore_code_examples(tmp_path: Path, example: str) -> None:
    text = f"[real](actual.md)\n\n{example}"
    assert list(check_links.relative_targets(tmp_path, "docs/page.md", text)) == [
        ("actual.md", tmp_path / "docs" / "actual.md")
    ]


def test_relative_links_retain_broken_links_after_code(tmp_path: Path) -> None:
    text = "`[example](ignored.md)` then [broken](missing.md)"
    assert list(check_links.relative_targets(tmp_path, "page.md", text)) == [
        ("missing.md", tmp_path / "missing.md")
    ]


@pytest.mark.parametrize(
    "text",
    [
        "`unmatched\n\n[broken](missing.md)\n\n`later`",
        "`unmatched\n# Heading\n[broken](missing.md)\n`later`",
        "`unmatched\n- [broken](missing.md)\n\n`later`",
        r"\`[broken](missing.md)`",
        "[broken][ref]\n\n[ref]: missing.md",
    ],
)
def test_relative_links_preserve_rendered_links(tmp_path: Path, text: str) -> None:
    assert list(check_links.relative_targets(tmp_path, "page.md", text)) == [
        ("missing.md", tmp_path / "missing.md")
    ]


def test_raw_html_targets_count_and_html_in_code_does_not(tmp_path: Path) -> None:
    # Planted: a raw <img> and an <a> that GitHub renders, beside the same tags
    # inside a code block, which it shows as text.
    text = (
        '<p align="center"><img src="docs/media/missing.png" alt="x"></p>\n'
        '\nread <a href="gone.md#top">this</a> first\n'
        '\n```html\n<img src="docs/media/also-missing.png">\n```\n'
    )
    assert [
        target
        for target, _ in check_links.relative_targets(tmp_path, "README.md", text)
    ] == [
        "docs/media/missing.png",
        "gone.md#top",
    ]


def test_relative_links_decode_paths_and_include_images(tmp_path: Path) -> None:
    text = '[space](<two words.md>) ![image](pic.png "caption")'
    assert list(check_links.relative_targets(tmp_path, "page.md", text)) == [
        ("two%20words.md", tmp_path / "two words.md"),
        ("pic.png", tmp_path / "pic.png"),
    ]


@pytest.mark.parametrize(
    ("page", "expected"),
    [
        ("README.md", True),
        ("docs/glossary.md", True),
        ("docs/media/README.md", True),
        ("experiments/README.md", True),
        ("experiments/lab/torch_probe/README.md", True),
        ("replays/candidates/stage-b-r2/README.md", True),
        ("eval/reports/process-scorecard.md", True),
        ("process/README.md", True),
        ("process/tasks/README.md", True),
        ("process/audits/README.md", True),
        ("process/audits/review-2026-09-06/correction-record.md", True),
        ("process/audits/audit-2026-10-09-stage-b-r3.md", False),
        ("process/tasks/phase-21.md", False),
        ("process/DESIGN.md", False),
        ("experiments/lab/notes.md", False),
        ("docs.md", False),
    ],
)
def test_the_default_scope_is_the_live_pages(page: str, expected: bool) -> None:
    assert check_links.in_scope(page) is expected


def test_the_live_pages_hold_no_broken_link() -> None:
    assert check_links.main([]) == 0


def test_a_planted_broken_link_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Planted: a page in scope linking a file that is not there, beside one that
    # is, and a record out of scope with its own broken link.
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "kept.md").write_text("# kept\n", encoding="utf-8")
    (tmp_path / "docs" / "page.md").write_text(
        "[kept](kept.md#top) and [gone](gone.md)\n", encoding="utf-8"
    )
    (tmp_path / "process" / "audits").mkdir(parents=True)
    (tmp_path / "process" / "audits" / "old.md").write_text(
        "[gone](gone.md)\n", encoding="utf-8"
    )
    assert check_links.broken_links(tmp_path, ["docs/page.md"]) == [
        ("docs/page.md", "gone.md")
    ]
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    assert check_links.main(["--root", str(tmp_path)]) == 1
    assert (
        "docs/page.md: the link 'gone.md' points at nothing" in capsys.readouterr().out
    )
    assert check_links.main(["--root", str(tmp_path), "--all"]) == 1
    assert capsys.readouterr().out.splitlines() == [
        "docs: 1",
        "process: 1",
        "2 broken relative links in 3 pages",
    ]
