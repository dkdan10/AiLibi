"""The review ledger's post-merge commit register, re-derived from git.

`P-10` observed that the ledger's per-commit SHA register stopped at the review:
eight post-review commits had no row, and nothing noticed. A register that is
typed rots the same way, so every field of every row here is recomputed from
`git log` and compared: the shas, their order, the card each commit names in its
`Card:` trailer, and the commit's subject line.

A commit cannot contain its own sha, so the register declares the coverage tip
it reaches and the tip is checked to be the register's own last row and an
ancestor of (or equal to) `HEAD`. The commit after the one it records is what
advances the register.

The git-derived half needs the merge commit in the object store. CI checks out
at `fetch-depth: 1`, where the range cannot be resolved; the structural half
below runs everywhere and the derived half reports why it could not run rather
than passing quietly.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LEDGER = _REPO_ROOT / "tasks" / "review-ledger.md"

#: The merge that landed the cleanup into `main`. Everything after it is a
#: post-review commit; the ledger's earlier sections stop here.
_MERGE_CHECKPOINT = "8161689a"

_SECTION_HEADING = re.compile(
    r"^## Post-merge commit register \(as of (\d{4}-\d{2}-\d{2})\)$", re.MULTILINE
)
_COVERAGE = re.compile(
    rf"Rows cover every non-merge commit from `{_MERGE_CHECKPOINT}` to `([0-9a-f]{{8}})`"
)
_ROW = re.compile(r"^\| `([0-9a-f]{8})` \| (\S+) \| (.+?) \|$", re.MULTILINE)
_LOG_FORMAT = "%h%x00%s%x00%(trailers:key=Card,valueonly,separator=%x2C)"


def _section() -> str:
    text = _LEDGER.read_text(encoding="utf-8")
    heading = _SECTION_HEADING.search(text)
    assert heading is not None, "the ledger has no post-merge commit register"
    following = re.search(r"^## ", text[heading.end() :], re.MULTILINE)
    end = len(text) if following is None else heading.end() + following.start()
    return text[heading.start() : end]


def _rows() -> list[tuple[str, str, str]]:
    return [
        (sha, card, subject.strip()) for sha, card, subject in _ROW.findall(_section())
    ]


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def _commits(tip: str) -> list[tuple[str, str, str]] | None:
    """Every non-merge commit in the covered range, or ``None`` without history.

    ``None`` means git could not resolve the range at all — no repository, or a
    shallow clone without the merge checkpoint. The caller reports that as a
    skip with its reason, never as a pass.
    """

    if _git("cat-file", "-e", f"{_MERGE_CHECKPOINT}^{{commit}}").returncode != 0:
        return None
    result = _git(
        "log",
        "--no-merges",
        "--reverse",
        f"--format={_LOG_FORMAT}",
        "--abbrev=8",
        f"{_MERGE_CHECKPOINT}..{tip}",
    )
    if result.returncode != 0:
        return None
    commits: list[tuple[str, str, str]] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        sha, subject, card = line.split("\0")
        trailer = card.strip()
        slug = Path(trailer.split(",")[0].strip()).stem if trailer else "—"
        commits.append((sha, slug, subject))
    return commits


def _coverage_tip() -> str:
    match = _COVERAGE.search(_section())
    assert match is not None, "the register does not declare the tip it covers"
    return match.group(1)


def test_the_register_declares_a_tip_that_is_its_own_last_row() -> None:
    rows = _rows()
    assert rows, "the register has no rows"
    assert _coverage_tip() == rows[-1][0]
    shas = [sha for sha, _, _ in rows]
    assert len(set(shas)) == len(shas), "a commit is registered twice"


def test_every_registered_commit_matches_the_commit_it_names() -> None:
    tip = _coverage_tip()
    commits = _commits(tip)
    if commits is None:
        pytest.skip(
            f"{_MERGE_CHECKPOINT} is not in this checkout's object store "
            "(shallow clone); the register cannot be re-derived here"
        )
    registered = _rows()
    missing = [
        commit for commit in commits if commit[0] not in {r[0] for r in registered}
    ]
    assert not missing, f"post-review commits with no ledger row: {missing}"
    invented = [row for row in registered if row[0] not in {c[0] for c in commits}]
    assert not invented, f"ledger rows naming no commit in range: {invented}"
    assert registered == commits


def test_the_coverage_tip_is_reachable_from_this_branch() -> None:
    tip = _coverage_tip()
    if _git("cat-file", "-e", f"{tip}^{{commit}}").returncode != 0:
        pytest.skip(f"{tip} is not in this checkout's object store (shallow clone)")
    assert _git("merge-base", "--is-ancestor", tip, "HEAD").returncode == 0, (
        f"the register claims coverage to {tip}, which is not an ancestor of HEAD"
    )
