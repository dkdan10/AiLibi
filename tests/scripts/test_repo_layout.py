"""The repository layout after the process record moved under ``process/``.

The task cards, audits, design record and historical notes live under
``process/``; the generated report pages live under ``eval/reports/``. Two
things are held here against the git index: nothing is tracked at a location
the move emptied, so a stray copy cannot reappear beside its moved twin, and
every moved path the code, the links and the artifact registry read is tracked
where they expect it. A planted repository proves the first check fails.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterable
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[2]

#: The locations the move emptied, as ``fnmatch`` patterns over tracked paths
#: (``*`` crosses folders). A folder pattern covers everything beneath it.
OLD_LOCATIONS: Final[tuple[str, ...]] = (
    "tasks/*",
    "audits/*",
    "design/*",
    "agent_prompts/*",
    "DESIGN.md",
    "AGENT_IMPLEMENTATION.md",
    "docs/history.md",
    "docs/cleanup-dispositions.md",
    "docs/gameplay-census.*",
    "docs/game-profile.md",
    "docs/process-scorecard*",
)

#: Paths the move created, each read by code, a link check or the registry.
MOVED_PATHS: Final[tuple[str, ...]] = (
    "process/README.md",
    "process/DESIGN.md",
    "process/AGENT_IMPLEMENTATION.md",
    "process/docs/cleanup-dispositions.md",
    "process/tasks/README.md",
    "process/tasks/review-ledger.md",
    "process/audits/README.md",
    "process/audits/deduction-candidate/held-out/manifest.json",
    "process/design/phase-12/gen_map_reference.py",
    "experiments/extract_gameplay_facts.py",
    "eval/reports/README.md",
    "eval/reports/game-profile.md",
    "eval/reports/gameplay-census.md",
    "eval/reports/gameplay-census.json",
    "eval/reports/process-scorecard.md",
    "eval/reports/process-scorecard-before.json",
)


def tracked_paths(root: Path) -> frozenset[str]:
    """Every path the git index of ``root`` tracks; raises when git cannot list."""

    listed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return frozenset(path for path in listed.stdout.split("\0") if path)


def stale_paths(tracked: Iterable[str]) -> list[str]:
    """The tracked paths that sit at a location the move emptied, sorted."""

    return sorted(
        path
        for path in tracked
        if any(fnmatchcase(path, pattern) for pattern in OLD_LOCATIONS)
    )


def missing_paths(tracked: Iterable[str]) -> list[str]:
    """The moved paths the index does not track, in :data:`MOVED_PATHS` order."""

    present = set(tracked)
    return [path for path in MOVED_PATHS if path not in present]


def test_nothing_is_tracked_at_a_location_the_move_emptied() -> None:
    assert stale_paths(tracked_paths(_REPO_ROOT)) == []


def test_every_moved_path_is_tracked_where_it_is_read() -> None:
    assert missing_paths(tracked_paths(_REPO_ROOT)) == []


def test_a_tracked_file_at_an_old_location_fails_the_check(tmp_path: Path) -> None:
    """Planted: a repository holding one file at each kind of old location.

    A folder, a page and a generated report at their old paths are each named;
    their moved twins, a lookalike folder name and an untracked stray are not.
    """

    planted = {
        "audits/audit-x.md": True,
        "tasks/work/card.md": True,
        "DESIGN.md": True,
        "docs/process-scorecard.json": True,
        "docs/gameplay-census.md": True,
        "process/audits/audit-x.md": False,
        "process/DESIGN.md": False,
        "eval/reports/process-scorecard.md": False,
        "tasksx/notes.md": False,
        "docs/glossary.md": False,
    }
    for relative in planted:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# planted\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    (tmp_path / "design").mkdir()
    (tmp_path / "design" / "untracked.md").write_text("# stray\n", encoding="utf-8")

    tracked = tracked_paths(tmp_path)
    assert stale_paths(tracked) == sorted(
        relative for relative, stale in planted.items() if stale
    )
    missing = missing_paths(tracked)
    assert "process/audits/README.md" in missing
    assert "eval/reports/process-scorecard.md" not in missing
