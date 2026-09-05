"""Prepare one replay and its observation audit before either writer starts."""

from __future__ import annotations

import os
import stat
import tempfile
from collections.abc import Callable, Iterator, Sequence
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
    backups: Sequence[tuple[Path, Path]], error: BaseException | None
) -> None:
    """Attempt every restoration, retaining recoverable files if one fails."""
    failures: list[BaseException] = []
    for target, backup in reversed(backups):
        try:
            backup.replace(target)
            backup.parent.rmdir()
        except OSError as exc:
            failures.append(exc)
    if failures:
        locations = ", ".join(str(backup) for _, backup in backups if backup.exists())
        raise BaseExceptionGroup(
            f"Recording setup and rollback failed; recover retained backups at: {locations}",
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
) -> Iterator[Callable[[], None]]:
    """Replace both outputs, restoring previous files if writer setup fails.

    Construct and close the writers inside this context. Call the yielded
    ``begin_recording`` after construction succeeds, before writing any rows.
    Before that boundary, setup failures restore previous files. Afterwards,
    failures retain the new partial evidence. Backups are retired only after
    the run and its handles finish; a cleanup error cannot destroy current data.
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
    recording_started = False
    failure: BaseException | None = None

    def begin_recording() -> None:
        nonlocal recording_started
        recording_started = True

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
        yield begin_recording
    except BaseException as exc:
        failure = exc
        raise
    finally:
        if not recording_started:
            _restore_backups(backups, failure)
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
