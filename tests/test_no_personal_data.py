"""No tracked file carries a person's home directory or mail address.

The repository is published, so a home path or an address in any tracked line
reaches every reader. The gate runs ``git grep`` over the tracked tree for a
cheap, case-insensitive superset of home-path and address shapes, then reports
every match that is not on the allow-lists below.

A home path is ``/Users/<name>`` or ``/home/<name>`` (which also covers the
``C:/Users/<name>`` spelling), the backslash form ``C:\\Users\\<name>`` with or
without its drive letter and with single or doubled backslashes, or the dashed
form a tool derives from a working path by turning each ``/`` into ``-``.
``Users`` matches in any case, as the macOS and Windows file systems resolve it;
``home`` matches in any case only in the backslash form, since on Linux
``/Home/`` is not the home root (``Arrow/Home/End`` names keys). In the slash
and backslash forms the account passes only when it is one of
:data:`_GENERIC_ACCOUNTS`, compared without case: the cloud container's
``user``, the CI and infrastructure accounts ``runner``, ``ci``, ``node`` and
``linuxbrew``, macOS's ``Shared``, the fixtures' ``nobody`` and ``someone``, and
an elided ``...``. A home directory written as ``~`` never matches, which is how
the recorded run output and the review archive spell the operator's.

The dashed form cannot say where the account ends, since an account may hold a
``-`` itself (``user-john``), so it is judged whole: its tail runs from after
the ``Users-`` or ``home-`` to the first character that is not a word
character, ``.`` or ``-`` (a ``/``, a space, a quote, the end of the line), and
it passes only when that entire tail is one of :data:`_GENERIC_DASHED_TAILS`.
The per-account list never applies to it.

An address passes only when it is one of :data:`_GENERIC_ADDRESSES` exactly
(the commit trailer's ``noreply@anthropic.com`` and GitHub's
``noreply@github.com``) or sits on one of :data:`_GENERIC_DOMAINS`: the reserved
example domains, and GitHub's per-user no-reply domain. Anyone else at
``anthropic.com`` or ``github.com`` is reported.

The gate guards the current tracked tree only. Earlier commits' contents and
every commit's author and committer identity still carry the data: history is
not rewritten, and nothing here reads it.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Iterable
from pathlib import Path
from typing import Final

import pytest

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]

#: The cheap ``git grep -i`` superset: any home-path or mail-address shape.
_CANDIDATES: Final = (
    r"/(users|home)/|\\+(users|home)\\+|-(users|home)-|@([a-z0-9-]+\.)+[a-z]{2,}"
)
#: The three home-path spellings. The first two groups hold an account; the
#: third holds a dashed form's whole tail.
_HOME: Final = re.compile(
    r"/(?:(?i:users)|home)/([\w.-]+)"
    r"|(?i:(?:[a-z]:)?\\+(?:users|home)\\+)([\w.-]+)"
    r"|-(?:(?i:users)|home)-([\w.-]+)"
)
#: An address: a local part directly before the ``@``, so a decorator never matches.
_MAIL: Final = re.compile(r"[\w.%+-]+@((?:[a-z0-9-]+\.)+[a-z]{2,})", re.IGNORECASE)
#: Account names that belong to no person, lower-cased.
_GENERIC_ACCOUNTS: Final = frozenset(
    {"user", "runner", "ci", "node", "linuxbrew", "shared", "nobody", "someone", "..."}
)
#: Dashed tails that belong to no person, lower-cased: the cloud sandbox's
#: scratch directory, ``/tmp/claude-0/-home-user-AiLibi/``.
_GENERIC_DASHED_TAILS: Final = frozenset({"user-ailibi"})
#: Addresses that reach no person, matched whole and without case.
_GENERIC_ADDRESSES: Final = frozenset({"noreply@anthropic.com", "noreply@github.com"})
#: Domains on which no address reaches a person, matched whole and without case.
_GENERIC_DOMAINS: Final = frozenset(
    {
        "example.com",
        "example.org",
        "example.net",
        "example.invalid",
        "users.noreply.github.com",
    }
)

#: One ``git grep -z -n`` record: the path, the line number, the line's text.
_RECORD: Final = re.compile(rb"([^\0]*)\0([0-9]+)\0([^\n]*)\n")

#: One ``git grep`` match: repo-relative path, line number, line text.
GrepRow = tuple[str, str, str]


def personal_data_hits(rows: Iterable[GrepRow]) -> list[str]:
    """Every personal match in ``rows``, as ``path:line: match``."""

    hits: list[str] = []
    for path, line, text in rows:
        for match in _HOME.finditer(text):
            slashed, backslashed, dashed = match.groups()
            if dashed is not None:
                generic = dashed.lower() in _GENERIC_DASHED_TAILS
            else:
                account = slashed if slashed is not None else backslashed
                generic = account.lower() in _GENERIC_ACCOUNTS
            if not generic:
                hits.append(f"{path}:{line}: {match.group(0)}")
        for match in _MAIL.finditer(text):
            if (
                match.group(0).lower() not in _GENERIC_ADDRESSES
                and match.group(1).lower() not in _GENERIC_DOMAINS
            ):
                hits.append(f"{path}:{line}: {match.group(0)}")
    return hits


def grep_rows(output: bytes) -> list[GrepRow]:
    """Split ``git grep -z -n`` output into rows, raising on anything else.

    Read as bytes and cut on git's own separators only: a line runs to the next
    ``\\n`` byte, so a carriage return inside one stays part of its text. Bytes
    that are not UTF-8 decode to U+FFFD, which leaves the ASCII shapes around
    them matchable.
    """

    rows: list[GrepRow] = []
    position = 0
    while position < len(output):
        record = _RECORD.match(output, position)
        if record is None:
            raise ValueError(
                f"unparseable git grep output at byte {position}: "
                f"{output[position : position + 80]!r}"
            )
        path, line, text = (
            field.decode("utf-8", errors="replace") for field in record.groups()
        )
        rows.append((path, line, text))
        position = record.end()
    return rows


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    # An inherited GIT_DIR or GIT_INDEX_FILE would point git at another repository.
    env = {
        name: value for name, value in os.environ.items() if not name.startswith("GIT_")
    }
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, env=env, check=False
    )


def tracked_candidate_rows(root: Path) -> list[GrepRow]:
    """Every line of a tracked text file under ``root`` with a candidate shape."""

    completed = _git(
        root, "grep", "-z", "-n", "-I", "-i", "--no-color", "-E", _CANDIDATES
    )
    # git grep exits 1 when nothing matches; any other status is a failed scan.
    if completed.returncode not in (0, 1):
        stderr = completed.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"git grep exited {completed.returncode}: {stderr}")
    return grep_rows(completed.stdout)


def test_no_tracked_file_names_a_personal_account_or_address() -> None:
    assert personal_data_hits(tracked_candidate_rows(_REPO_ROOT)) == []


def test_a_planted_home_path_and_address_in_a_tracked_file_are_reported(
    tmp_path: Path,
) -> None:
    # Split so this file's own bytes never hold a match.
    home, dashed, mail = (
        "/Users/" + "alice",
        "-Users-" + "alice-projects-AiLibi",
        "alice" + "@icloud.com",
    )
    # A hyphenated account, a CI account's dashed path, and a non-ASCII one: each
    # dashed tail is judged whole, so a generic first component does not pass it.
    hyphenated, runner, accented_dashed = (
        "-Users-" + "user-john-projects-x",
        "-home-" + "runner-work-x",
        "-home-" + "émile-x",
    )
    staff = "alice" + "@anthropic.com"
    windows, doubled = "C:\\" + "Users\\alice", "C:\\\\" + "Users\\\\alice"
    shouted, lowered = "/USERS/" + "alice", "c:\\" + "users\\alice"
    accented = "/home/" + "émile"
    planted = tmp_path / "docs" / "x.md"
    planted.parent.mkdir()
    planted.write_bytes(
        (
            "# Notes\n"
            "\n"
            f"ran from {home}/projects/AiLibi\n"
            f"scratch at /private/tmp/claude-501/{dashed}/s\n"
            f"authored as {mail}\n"
            "/home/user/AiLibi, /Users/someone/x and noreply@anthropic.com\n"
            "~/projects/AiLibi, ~/.claude/projects/.../memory and /private/tmp/.../scratchpad\n"
            "    @pytest.mark.parametrize\n"
            f"reviewed by {staff}\n"
            "noreply@github.com, 1+someone@users.noreply.github.com, a@example.org\n"
            "/home/runner/work, /Users/Shared/x, /home/linuxbrew/.linuxbrew, /home/node\n"
            f"ran from {windows}\\AiLibi and {doubled}\\\\AiLibi\n"
            f"ran from {shouted}, {lowered} and {accented}; Arrow/Home/End seek\n"
            f"progress 10%\rprogress 100% in {home}/scratch\n"
            f"after the carriage return, {mail}\n"
            f"scratch at /tmp/{hyphenated}/s, '{runner}' and {accented_dashed}\n"
            "scratch at /tmp/claude-0/-home-user-AiLibi/abc\n"
        ).encode("utf-8")
    )
    (tmp_path / "untracked.md").write_text(f"{home}/scratch\n", encoding="utf-8")
    for args in (("init", "-q"), ("add", "docs/x.md")):
        assert _git(tmp_path, *args).returncode == 0

    assert personal_data_hits(tracked_candidate_rows(tmp_path)) == [
        f"docs/x.md:3: {home}",
        f"docs/x.md:4: {dashed}",
        f"docs/x.md:5: {mail}",
        f"docs/x.md:9: {staff}",
        f"docs/x.md:12: {windows}",
        f"docs/x.md:12: {doubled}",
        f"docs/x.md:13: {shouted}",
        f"docs/x.md:13: {lowered}",
        f"docs/x.md:13: {accented}",
        f"docs/x.md:14: {home}",
        f"docs/x.md:15: {mail}",
        f"docs/x.md:16: {hyphenated}",
        f"docs/x.md:16: {runner}",
        f"docs/x.md:16: {accented_dashed}",
    ]


def test_grep_output_without_git_separators_raises() -> None:
    """A record the parser cannot split is an error, never a skipped line."""

    assert grep_rows(b"a.md\x002\x00one\rtwo\n") == [("a.md", "2", "one\rtwo")]
    with pytest.raises(ValueError, match="unparseable git grep output at byte 0"):
        grep_rows(b"a.md:2:" + b"/Users/" + b"alice\n")
    with pytest.raises(ValueError, match="at byte 11"):
        grep_rows(b"a.md\x002\x00one\nno separators\n")
