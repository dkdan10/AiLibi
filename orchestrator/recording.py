"""Prepare one replay and its observation audit before either writer starts."""

from __future__ import annotations

import os
import stat
import tempfile
from collections.abc import Iterator, Sequence
from contextlib import ExitStack, contextmanager
from pathlib import Path

from orchestrator.replay import ReplayLog


def _recording_paths(replay_path: Path, audit_path: Path) -> tuple[Path, ...]:
    """Reject destinations that alias or cannot hold independent regular files."""
    replay_resolved = replay_path.resolve()
    audit_resolved = audit_path.resolve()
    if (
        replay_resolved == audit_resolved
        or replay_resolved in audit_resolved.parents
        or audit_resolved in replay_resolved.parents
    ):
        raise ValueError("Replay and audit paths must be separate, non-nested files")

    # A caller may deliberately discard observations. Never rotate the device;
    # no-replay training uses it too, without entering this recording lifecycle.
    paths = (
        (replay_path,) if audit_path == Path(os.devnull) else (replay_path, audit_path)
    )
    for path in paths:
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(
                f"Recording output must be a regular file, not a link or device: {path}"
            )
    if len(paths) == 2 and all(path.exists() for path in paths):
        if replay_path.samefile(audit_path):
            raise ValueError("Replay and audit paths refer to the same file")
    return paths


def _restore_backups(
    backups: Sequence[tuple[Path, Path]],
    error: BaseException | None,
    *,
    remove_empty: Sequence[Path] = (),
) -> None:
    """Restore prior bytes and absence, attempting every path after a failure."""
    failures: list[BaseException] = []
    for target, backup in reversed(backups):
        try:
            backup.replace(target)
            backup.parent.rmdir()
        except OSError as exc:
            failures.append(exc)
    for path in remove_empty:
        try:
            if path.exists():
                if path.stat().st_size:
                    raise OSError(
                        f"Refusing to remove nonempty recording output: {path}"
                    )
                path.unlink()
        except OSError as exc:
            failures.append(exc)
    if failures:
        locations = ", ".join(
            str(path)
            for path in (*(backup for _, backup in backups), *remove_empty)
            if path.exists()
        )
        raise BaseExceptionGroup(
            f"Recording setup and rollback failed; recover retained paths at: {locations}",
            ([error] if error is not None else []) + failures,
        )


def _discard_backups(backups: Sequence[tuple[Path, Path]]) -> None:
    """Retire the old generation after the new run's handles have closed."""
    failures: list[Exception] = []
    for _, backup in backups:
        try:
            backup.unlink()
            backup.parent.rmdir()
        except OSError as exc:
            failures.append(exc)
    if failures:
        locations = ", ".join(
            str(backup.parent) for _, backup in backups if backup.parent.exists()
        )
        raise ExceptionGroup(
            f"Recording outputs retained; old-backup cleanup failed at: {locations}",
            failures,
        )


@contextmanager
def prepare_recording_paths(
    replay_path: Path, audit_path: Path, *, force: bool
) -> Iterator[None]:
    """Replace both outputs, restoring previous files until new bytes exist.

    Construct and close the writers inside this context. Writer construction
    and entering the run loop do not commit replacement: either output must
    actually contain bytes after the handles close. Before that boundary,
    failures restore previous files. Afterwards, failures retain new partial
    evidence, including an audit-only prefix or an incomplete write. Backups
    retire after the handles finish; cleanup cannot destroy current data.
    Sibling backups also support audits on another filesystem.

    This handles ordinary exceptions; it is not a crash-atomic publication
    protocol or coordination between concurrent writers.
    """
    paths = _recording_paths(replay_path, audit_path)
    for path in paths:
        if path.exists() and not force:
            raise ReplayLog.AlreadyExistsError(
                f"Recording output already exists: {path}. Pass force=True to replace "
                "the replay and its audit, or choose different paths."
            )
    # Finish potentially failing directory preparation before moving old files.
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)

    # Recheck after mkdir: on a case-insensitive filesystem a newly created
    # parent can alias the other output. Probe missing destinations with real
    # exclusive opens, detecting unwritable paths and fresh case/Unicode aliases
    # before moving existing evidence. Only our own empty probes are removed.
    paths = _recording_paths(replay_path, audit_path)
    with ExitStack() as probes:
        for path in paths:
            if not path.exists():
                with path.open("x", encoding="utf-8"):
                    probes.callback(path.unlink)
        _recording_paths(replay_path, audit_path)

    backups: list[tuple[Path, Path]] = []
    initially_absent = tuple(path for path in paths if not path.exists())
    preparation_finished = False
    failure: BaseException | None = None

    try:
        if force:
            for path in paths:
                if not path.exists():
                    continue
                directory = Path(
                    tempfile.mkdtemp(prefix=".ailibi-recording-", dir=path.parent)
                )
                backup = directory / path.name
                try:
                    path.replace(backup)
                except BaseException:
                    directory.rmdir()
                    raise
                backups.append((path, backup))
        preparation_finished = True
        yield
    except BaseException as exc:
        failure = exc
        raise
    finally:
        if not preparation_finished or not any(
            path.exists() and path.stat().st_size for path in paths
        ):
            _restore_backups(backups, failure, remove_empty=initially_absent)
        else:
            try:
                _discard_backups(backups)
            except Exception as cleanup_error:
                if failure is not None:
                    raise BaseExceptionGroup(
                        "Recording and old-backup cleanup both failed",
                        [failure, cleanup_error],
                    ) from None
                raise
