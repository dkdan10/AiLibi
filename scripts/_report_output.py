"""Protect recording destinations and publish report text without truncation."""

from __future__ import annotations

import os
import stat
import tempfile
from collections.abc import Sequence
from pathlib import Path


def _check_destination(path: Path, recording_paths: Sequence[Path]) -> None:
    resolved = path.resolve()
    for recording in recording_paths:
        other = recording.resolve()
        overlaps = (
            resolved == other or resolved in other.parents or other in resolved.parents
        )
        if path.exists():
            overlaps |= any(
                candidate.exists() and path.samefile(candidate)
                for candidate in (recording, *recording.parents)
            )
        if recording.exists():
            overlaps |= any(
                parent.exists() and recording.samefile(parent)
                for parent in path.parents
            )
        if overlaps:
            raise ValueError(
                f"Report destination overlaps a recording output: {path} and {recording}"
            )
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return
    if not stat.S_ISREG(mode):
        raise ValueError(f"Report destination must be a regular file: {path}")


def _temporary_sibling(path: Path) -> Path:
    descriptor, name = tempfile.mkstemp(prefix=".ailibi-report-", dir=path.parent)
    os.close(descriptor)
    return Path(name)


def preflight_report_output(path: Path, recording_paths: Sequence[Path]) -> None:
    """Refuse invalid aliases and unavailable destinations before provider work.

    Exclusive probes also expose case/Unicode aliases on the actual filesystem.
    Only probes created here are removed; existing report and recording bytes
    stay untouched. Newly created parent directories may remain after refusal.
    Concurrent writers and later filesystem changes are outside this preflight's
    guarantee.
    """
    _check_destination(path, recording_paths)
    path.parent.mkdir(parents=True, exist_ok=True)
    _check_destination(path, recording_paths)
    created = False
    try:
        if not path.exists():
            with path.open("x", encoding="utf-8"):
                created = True
            _check_destination(path, recording_paths)
        temporary = _temporary_sibling(path)
        temporary.unlink()
    finally:
        if created:
            path.unlink()


def atomic_write_report(path: Path, text: str) -> None:
    """Replace a report only after its complete text has been written and closed."""
    temporary = _temporary_sibling(path)
    failure: BaseException | None = None
    try:
        temporary.write_text(text, encoding="utf-8")
        temporary.replace(path)
    except BaseException as error:
        failure = error
        raise
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError as cleanup_error:
            if failure is not None:
                raise BaseExceptionGroup(
                    f"Report publication and cleanup failed; temporary file at {temporary}",
                    [failure, cleanup_error],
                ) from None
            raise
