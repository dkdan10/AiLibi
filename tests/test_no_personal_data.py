"""No tracked file carries a person's home directory or mail address.

The repository is published, so a home path or an address in any tracked line
reaches every reader. The gate runs ``git grep`` over the tracked tree for a
cheap superset of home-path and address shapes, then reports every match whose
account or domain is not one of the generic ones below: the cloud container's
``/home/user``, the CI and test-fixture accounts, and the no-reply and reserved
example domains. A home directory written as ``~`` passes, which is how the
recorded run output and the review archive spell the operator's. Commit
metadata lives outside the tree and outside this gate.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Final

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]

#: The cheap ``git grep`` superset: any home-path or mail-address shape.
_CANDIDATES: Final = r"/(Users|home)/|-(Users|home)-|@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}"
#: ``/Users/<name>`` or ``/home/<name>``, and the dashed form a tool derives from
#: a working path when it names a per-project directory after it.
_HOME: Final = re.compile(
    r"/(?:Users|home)/([A-Za-z0-9._-]+)|-(?:Users|home)-([A-Za-z0-9._]+)-"
)
#: An address: a local part directly before the ``@``, so a decorator never matches.
_MAIL: Final = re.compile(r"[A-Za-z0-9._%+-]+@((?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,})")
#: Account names that belong to no person: the cloud container, CI, the test
#: fixtures (``dan`` is the demo-bundle host-path fixture) and an elided name.
_GENERIC_ACCOUNTS: Final = frozenset({"user", "ci", "nobody", "someone", "dan", "..."})
#: Domains that address no person.
_GENERIC_DOMAINS: Final = frozenset(
    {"anthropic.com", "example.invalid", "example.com", "users.noreply.github.com"}
)

#: One ``git grep`` match: repo-relative path, line number, line text.
GrepRow = tuple[str, str, str]


def personal_data_hits(rows: Iterable[GrepRow]) -> list[str]:
    """Every personal match in ``rows``, as ``path:line: match``."""

    hits: list[str] = []
    for path, line, text in rows:
        for match in _HOME.finditer(text):
            account = match.group(1) or match.group(2)
            if account not in _GENERIC_ACCOUNTS:
                hits.append(f"{path}:{line}: {match.group(0)}")
        for match in _MAIL.finditer(text):
            if match.group(1).lower() not in _GENERIC_DOMAINS:
                hits.append(f"{path}:{line}: {match.group(0)}")
    return hits


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    # An inherited GIT_DIR or GIT_INDEX_FILE would point git at another repository.
    env = {
        name: value for name, value in os.environ.items() if not name.startswith("GIT_")
    }
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        encoding="utf-8",
        env=env,
        check=False,
    )


def tracked_candidate_rows(root: Path) -> list[GrepRow]:
    """Every line of a tracked text file under ``root`` with a candidate shape."""

    completed = _git(root, "grep", "-z", "-n", "-I", "--no-color", "-E", _CANDIDATES)
    # git grep exits 1 when nothing matches; any other status is a failed scan.
    if completed.returncode not in (0, 1):
        raise RuntimeError(
            f"git grep exited {completed.returncode}: {completed.stderr}"
        )
    rows: list[GrepRow] = []
    for record in completed.stdout.split("\n"):
        if record:
            path, line, text = record.split("\0", 2)
            rows.append((path, line, text))
    return rows


def test_no_tracked_file_names_a_personal_account_or_address() -> None:
    assert personal_data_hits(tracked_candidate_rows(_REPO_ROOT)) == []


def test_a_planted_home_path_and_address_in_a_tracked_file_are_reported(
    tmp_path: Path,
) -> None:
    # Split so this file's own bytes never hold a match.
    home, dashed, mail = (
        "/Users/" + "alice",
        "-Users-" + "alice-",
        "alice" + "@icloud.com",
    )
    planted = tmp_path / "docs" / "x.md"
    planted.parent.mkdir()
    planted.write_text(
        "# Notes\n"
        "\n"
        f"ran from {home}/projects/AiLibi\n"
        f"scratch at /private/tmp/claude-501/{dashed}projects-AiLibi/s\n"
        f"authored as {mail}\n"
        "/home/user/AiLibi, /Users/someone/x and noreply@anthropic.com\n"
        "~/projects/AiLibi, ~/.claude/projects/.../memory and /private/tmp/.../scratchpad\n"
        "    @pytest.mark.parametrize\n",
        encoding="utf-8",
    )
    (tmp_path / "untracked.md").write_text(f"{home}/scratch\n", encoding="utf-8")
    for args in (("init", "-q"), ("add", "docs/x.md")):
        assert _git(tmp_path, *args).returncode == 0

    assert personal_data_hits(tracked_candidate_rows(tmp_path)) == [
        f"docs/x.md:3: {home}",
        f"docs/x.md:4: {dashed}",
        f"docs/x.md:5: {mail}",
    ]
