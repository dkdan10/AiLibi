#!/usr/bin/env python3
"""Report relative markdown links that point at nothing.

Reads each tracked ``.md`` page with markdown-it, so a link inside code is not a
link, drops the ``#fragment`` from every link and image target, including the
``href`` and ``src`` of raw HTML, resolves the path from the page's own folder
and reports each target that does not exist. Web addresses and in-page anchors
are skipped.

By default only the live pages are read (:data:`DEFAULT_SCOPE`). Old records
keep links that were true when they were written, so ``--all`` reads every
tracked page and prints the broken links counted by top-level folder, to compare
against an earlier run. Either way the exit code is 1 when a page read has a
broken link.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
from collections import Counter
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Final
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.token import Token

_REPO_ROOT: Final = Path(__file__).resolve().parents[1]
# The live pages and the generated report pages, plus the record pages the
# README and the reading guide send a reader to. Task cards are left out:
# several link a card that is not written yet.
DEFAULT_SCOPE: Final[tuple[str, ...]] = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "docs/**",
    "eval/reports/**",
    "llm/README.md",
    "training/README.md",
    "experiments/**/README.md",
    "replays/**/README.md",
    "process/README.md",
    "process/tasks/README.md",
    "process/audits/README.md",
    "process/audits/audit-phase-21-close.md",
    "process/audits/review-2026-08-19/README.md",
    "process/audits/review-2026-09-06/README.md",
    "process/audits/review-2026-09-06/correction-record.md",
)
_ABSOLUTE_TARGET: Final = re.compile(r"\A(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)
_HTML_TARGET: Final = re.compile(
    r"""\b(?:href|src)\s*=\s*["']([^"']*)["']""", re.IGNORECASE
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report broken relative links.")
    parser.add_argument("--all", action="store_true", help="read every tracked page")
    parser.add_argument("--root", type=Path, default=_REPO_ROOT, help="a git checkout")
    args = parser.parse_args(argv)
    root: Path = args.root
    pages = [page for page in tracked_pages(root) if args.all or in_scope(page)]
    misses = broken_links(root, pages)
    if args.all:
        folders = Counter(
            page.partition("/")[0] if "/" in page else "." for page, _ in misses
        )
        for folder, count in sorted(folders.items()):
            print(f"{folder}: {count}")
    else:
        for page, target in misses:
            print(f"{page}: the link {target!r} points at nothing")
    print(f"{len(misses)} broken relative links in {len(pages)} pages")
    return 1 if misses else 0


def tracked_pages(root: Path) -> list[str]:
    """Every tracked ``.md`` path under ``root``; raises when git cannot list them."""

    listed = subprocess.run(
        ["git", "ls-files", "-z", "--", "*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted(path for path in listed.stdout.split("\0") if path)


def in_scope(page: str, scope: Sequence[str] = DEFAULT_SCOPE) -> bool:
    """Whether ``page`` matches a pattern of ``scope``.

    ``**/`` spans zero or more folders, a final ``**`` everything below its
    folder, and ``*`` stays inside one folder name.
    """

    for pattern in scope:
        regex = re.escape(pattern).replace(r"\*\*/", "(?:.*/)?").replace(r"\*\*", ".*")
        if re.fullmatch(regex.replace(r"\*", "[^/]*"), page):
            return True
    return False


def broken_links(root: Path, pages: Sequence[str]) -> list[tuple[str, str]]:
    """``(page, target)`` for every relative target in ``pages`` that does not exist."""

    return [
        (page, target)
        for page in pages
        for target, resolved in relative_targets(
            root, page, (root / page).read_text(encoding="utf-8")
        )
        if not resolved.exists()
    ]


def relative_targets(
    repo_root: Path, document: str, text: str
) -> Iterator[tuple[str, Path]]:
    """Each relative link or image target in ``text``, with the path it names."""

    base = posixpath.dirname(document)
    for target in markdown_targets(MarkdownIt("commonmark").parse(text)):
        if target.startswith("#") or _ABSOLUTE_TARGET.match(target):
            continue
        path = unquote(target.split("#", 1)[0])
        if path:
            yield target, repo_root / posixpath.normpath(posixpath.join(base, path))


def markdown_targets(tokens: Sequence[Token]) -> Iterator[str]:
    """Rendered link and image targets, never code or image alt text.

    Raw HTML counts too: the ``href`` and ``src`` of an inline tag or an HTML
    block, since GitHub renders both.
    """

    for token in tokens:
        attribute = {"link_open": "href", "image": "src"}.get(token.type)
        if attribute is not None:
            target = token.attrGet(attribute)
            if target is not None:
                if not isinstance(target, str):
                    raise TypeError(f"Markdown {attribute} must be text: {target!r}")
                yield target
        elif token.type in ("html_inline", "html_block"):
            yield from _HTML_TARGET.findall(token.content)
        elif token.children is not None:
            yield from markdown_targets(token.children)


if __name__ == "__main__":
    raise SystemExit(main())
