"""Exercise destination identity, writability and retired-backup failures."""

from __future__ import annotations

import stat
from collections.abc import Sequence
from pathlib import Path
from traceback import format_exception

import pytest

from engine.actions import Action
from engine.events import EngineEvent
from engine.world import WorldState, load_canonical_map
from llm.fake_provider import FakeProvider
from orchestrator.game import (
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.scheduler import TickScheduler
from orchestrator.replay import GameStopReplayEntry, ReplayLog, read_all_entries


def _game(
    replay: Path,
    *,
    audit: Path | None = None,
    seed: int = 1,
    ticks: int = 3,
    force: bool = False,
) -> HeadlessGame:
    return HeadlessGame(
        seed=seed,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=build_default_agent_factory(),
        replay_path=replay,
        audit_log_path=audit,
        scheduler=TickScheduler(max_ticks=ticks),
        meeting_runner=build_default_meeting_runner(llm_client=FakeProvider()),
        force=force,
    )


def _audit_path(replay: Path) -> Path:
    return replay.with_name(f"{replay.stem}.audit.jsonl")


def test_fresh_case_variants_follow_actual_filesystem_identity(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "case-probe"
    marker.write_text("probe", encoding="utf-8")
    insensitive = (tmp_path / "CASE-PROBE").exists()
    marker.unlink()
    replay = tmp_path / "recording.jsonl"
    audit = tmp_path / "RECORDING.jsonl"

    if insensitive:
        with pytest.raises(ValueError):
            _game(replay, audit=audit).run()
        assert not replay.exists()
        assert not audit.exists()
        assert list(tmp_path.iterdir()) == []
    else:
        _game(replay, audit=audit).run()
        assert not replay.samefile(audit)
        entries = read_all_entries(replay)
        assert len(entries) == 4
        assert isinstance(entries[-1], GameStopReplayEntry)
        assert entries[-1].reason == "TICK_BUDGET_REACHED"
        assert len(audit.read_text(encoding="utf-8").splitlines()) == 21


def test_unwritable_missing_audit_preserves_existing_replay(tmp_path: Path) -> None:
    replay = tmp_path / "recording.jsonl"
    _game(replay).run()
    original = replay.read_bytes()
    original_audit = _audit_path(replay).read_bytes()
    directory = tmp_path / "read-only"
    directory.mkdir()
    original_mode = stat.S_IMODE(directory.stat().st_mode)
    directory.chmod(0o500)
    audit = directory / "audit.jsonl"
    try:
        # Root and some filesystems bypass mode bits. Detect that explicitly so
        # a skipped control never claims to exercise a permission failure.
        probe = directory / "permission-probe"
        try:
            probe.write_bytes(b"probe")
        except PermissionError:
            pass
        else:
            probe.unlink()
            pytest.skip("this environment can write through directory mode 0500")

        with pytest.raises(PermissionError):
            _game(replay, audit=audit, seed=2, force=True).run()

        assert replay.read_bytes() == original
        assert _audit_path(replay).read_bytes() == original_audit
        assert not audit.exists()
        assert not list(tmp_path.rglob(".ailibi-recording-*"))
    finally:
        directory.chmod(original_mode)


def _contains_error(error: BaseException, expected: BaseException) -> bool:
    if error is expected:
        return True
    if isinstance(error, BaseExceptionGroup):
        return any(_contains_error(item, expected) for item in error.exceptions)
    return error.__cause__ is not None and _contains_error(error.__cause__, expected)


@pytest.mark.parametrize("runtime_failure", [False, True])
def test_backup_retirement_failure_preserves_new_recording_and_recovery_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, runtime_failure: bool
) -> None:
    replay = tmp_path / "recording.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    original_audit = audit.read_bytes()
    control = tmp_path / "control" / "recording.jsonl"
    cleanup_error = PermissionError("injected second-backup retirement failure")
    runtime_error = RuntimeError("injected interruption after the first tick")
    unlink = Path.unlink
    record_tick = ReplayLog.record_tick

    def record_then_fail(
        log: ReplayLog,
        tick: int,
        actions: list[Action],
        state: WorldState,
        *,
        events: Sequence[EngineEvent] | None = None,
    ) -> None:
        record_tick(log, tick, actions, state, events=events)
        raise runtime_error

    def fail_audit_backup(path: Path, missing_ok: bool = False) -> None:
        if (
            path.parent.name.startswith(".ailibi-recording-")
            and path.name == audit.name
        ):
            raise cleanup_error
        unlink(path, missing_ok=missing_ok)

    # Compare against the same runtime interruption without retirement failure.
    # A normal one-tick run additionally records its deliberate stop reason.
    with monkeypatch.context() as patch:
        if runtime_failure:
            patch.setattr(ReplayLog, "record_tick", record_then_fail)
            with pytest.raises(RuntimeError, match="injected interruption"):
                _game(control, seed=2, ticks=2).run()
        else:
            _game(control, seed=2, ticks=2).run()

    with monkeypatch.context() as patch:
        patch.setattr(Path, "unlink", fail_audit_backup)
        if runtime_failure:
            patch.setattr(ReplayLog, "record_tick", record_then_fail)
        with pytest.raises((OSError, BaseExceptionGroup)) as excinfo:
            _game(replay, seed=2, ticks=2, force=True).run()

    assert _contains_error(excinfo.value, cleanup_error)
    if runtime_failure:
        assert _contains_error(excinfo.value, runtime_error)
    assert replay.read_bytes() == control.read_bytes()
    assert audit.read_bytes() == _audit_path(control).read_bytes()
    retained = list(tmp_path.glob(f".ailibi-recording-*/{audit.name}"))
    assert len(retained) == 1
    assert retained[0].read_bytes() == original_audit
    assert str(retained[0].parent) in "".join(format_exception(excinfo.value))
