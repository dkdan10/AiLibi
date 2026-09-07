"""A replay and its observation audit always belong to the same run."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal, TextIO

import pytest
from pydantic import BaseModel

from agents.base import AgentInterface
from engine.entities import PlayerId, Role
from engine.world import load_canonical_map
from llm.client import CallKind, LLMResponse
from llm.fake_provider import FakeProvider
from observation.audit import ObservationAuditLog
from observation.packet import ObservationPacket
from orchestrator.game import (
    AgentFactory,
    HeadlessGame,
    build_default_agent_factory,
    build_default_meeting_runner,
)
from orchestrator.replay import ReplayLog, read_all_entries, read_replay_entries
from orchestrator.recording import prepare_recording_paths
from orchestrator.run_limits import RunDeadline, RunDeadlineExceeded
from orchestrator.scheduler import TickScheduler


class _FailingProvider:
    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        raise RuntimeError("injected provider failure")


def _game(
    replay: Path,
    *,
    audit: Path | None = None,
    seed: int = 1,
    max_ticks: int = 3,
    force: bool = False,
    fail_meeting: bool = False,
    agent_factory: AgentFactory | None = None,
    deadline: RunDeadline | None = None,
) -> HeadlessGame:
    provider = _FailingProvider() if fail_meeting else FakeProvider()
    return HeadlessGame(
        seed=seed,
        num_players=7,
        tasks_per_crewmate=1,
        game_map=load_canonical_map(),
        agent_factory=agent_factory or build_default_agent_factory(),
        replay_path=replay,
        audit_log_path=audit,
        scheduler=TickScheduler(max_ticks=max_ticks),
        meeting_runner=build_default_meeting_runner(llm_client=provider),
        force=force,
        deadline=deadline,
    )


def _audit_path(replay: Path) -> Path:
    return replay.with_name(f"{replay.stem}.audit.jsonl")


def test_deadline_before_first_output_restores_previous_pair(tmp_path: Path) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    before = _snapshot((replay, audit))
    with pytest.raises(RunDeadlineExceeded):
        _game(replay, force=True, deadline=RunDeadline(0.0)).run()
    assert _snapshot((replay, audit)) == before
    assert set(tmp_path.iterdir()) == {replay, audit}


@pytest.mark.parametrize("bytes_written", [b"", b"partial audit"])
@pytest.mark.parametrize("buffered", [False, True])
def test_first_audit_write_failure_uses_actual_bytes_as_replacement_boundary(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    bytes_written: bytes,
    buffered: bool,
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    before = _snapshot((replay, audit))

    def fail_write(log: ObservationAuditLog, packet: ObservationPacket) -> None:
        # A partial low-level write is still evidence, even without a full row.
        if buffered:
            log._handle = audit.open("w", encoding="utf-8")
            log._handle.write(bytes_written.decode())
            assert audit.stat().st_size == 0
        else:
            audit.write_bytes(bytes_written)
        raise OSError("injected first audit write failure")

    monkeypatch.setattr(ObservationAuditLog, "record_packet", fail_write)
    with pytest.raises(OSError, match="first audit write failure"):
        _game(replay, force=True).run()
    if bytes_written:
        assert not replay.exists()
        assert audit.read_bytes() == bytes_written
        assert set(tmp_path.iterdir()) == {audit}
    else:
        assert _snapshot((replay, audit)) == before
        assert set(tmp_path.iterdir()) == {replay, audit}


@pytest.mark.parametrize("existing", ["replay", "audit", "neither", "both"])
@pytest.mark.parametrize("existing_bytes", [b"", b"prior evidence"])
def test_zero_byte_rollback_restores_original_absence_and_existing_empty_files(
    tmp_path: Path, existing: str, existing_bytes: bytes
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    for name, path in (("replay", replay), ("audit", audit)):
        if existing in {name, "both"}:
            path.write_bytes(existing_bytes)
    before = _snapshot((replay, audit))
    with pytest.raises(RuntimeError, match="zero-byte failure"):
        with prepare_recording_paths(replay, audit, force=True):
            replay.touch()
            audit.touch()
            raise RuntimeError("injected zero-byte failure")
    assert _snapshot((replay, audit)) == before
    assert set(tmp_path.iterdir()) == {
        path for path, content in before.items() if content is not None
    }


def test_empty_output_cleanup_failure_preserves_old_bytes_and_original_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    replay.write_bytes(b"prior replay")
    original_error = RuntimeError("recording failed before writing")
    cleanup_error = PermissionError("empty audit could not be removed")
    original_unlink = Path.unlink

    def refuse_audit(path: Path, *args: Any, **kwargs: Any) -> None:
        if path == audit:
            raise cleanup_error
        original_unlink(path, *args, **kwargs)

    with pytest.raises(BaseExceptionGroup) as caught:
        with prepare_recording_paths(replay, audit, force=True):
            audit.touch()
            monkeypatch.setattr(Path, "unlink", refuse_audit)
            raise original_error
    assert caught.value.exceptions == (original_error, cleanup_error)
    assert str(audit) in str(caught.value)
    assert replay.read_bytes() == b"prior replay"
    assert audit.read_bytes() == b""


def _packets(path: Path) -> tuple[ObservationPacket, ...]:
    return tuple(
        ObservationPacket.model_validate_json(line)
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def _snapshot(paths: tuple[Path, ...]) -> dict[Path, bytes | Path | None]:
    return {
        path: (
            path.readlink()
            if path.is_symlink()
            else path.read_bytes()
            if path.exists()
            else None
        )
        for path in paths
    }


@pytest.mark.parametrize("explicit_audit", [False, True])
def test_forced_replacement_matches_a_clean_run_pair(
    tmp_path: Path, explicit_audit: bool
) -> None:
    replay = tmp_path / "replay.jsonl"
    explicit_path = (
        tmp_path / "separate" / "observations.jsonl" if explicit_audit else None
    )
    audit = explicit_path or _audit_path(replay)
    _game(replay, audit=explicit_path).run()
    assert len(_packets(audit)) == 21

    control = tmp_path / "control" / "replay.jsonl"
    _game(control, seed=2, max_ticks=2).run()
    _game(replay, audit=explicit_path, seed=2, max_ticks=2, force=True).run()

    assert replay.read_bytes() == control.read_bytes()
    assert audit.read_bytes() == _audit_path(control).read_bytes()
    packets = _packets(audit)
    assert len(packets) == 14
    assert len({(packet.tick, packet.agent_id) for packet in packets}) == len(packets)
    assert len(read_replay_entries(replay)) == 2
    assert all(entry.game_id == "headless-seed-2" for entry in read_all_entries(replay))


@pytest.mark.parametrize("existing", ["replay", "audit", "both"])
def test_refusing_an_existing_artifact_preserves_both_paths(
    tmp_path: Path, existing: Literal["replay", "audit", "both"]
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    if existing == "audit":
        replay.unlink()
    elif existing == "replay":
        audit.unlink()
    before = {
        path: path.read_bytes() if path.exists() else None for path in (replay, audit)
    }

    with pytest.raises(FileExistsError):
        _game(replay, seed=2).run()

    assert {
        path: path.read_bytes() if path.exists() else None for path in (replay, audit)
    } == before


def test_invalid_audit_destination_preserves_previous_pair(tmp_path: Path) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    before = replay.read_bytes(), audit.read_bytes()
    invalid = tmp_path / "audit-is-a-directory"
    invalid.mkdir()

    with pytest.raises((OSError, ValueError)):
        _game(replay, audit=invalid, seed=2, force=True).run()

    assert replay.read_bytes() == before[0]
    assert audit.read_bytes() == before[1]
    assert invalid.is_dir()
    assert not list(invalid.iterdir())


def test_runtime_failure_keeps_only_the_current_partial_pair(tmp_path: Path) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay, seed=2).run()

    control = tmp_path / "control" / "replay.jsonl"
    with pytest.raises(RuntimeError, match="injected provider failure"):
        _game(control, max_ticks=200, fail_meeting=True).run()
    with pytest.raises(RuntimeError, match="injected provider failure"):
        _game(replay, max_ticks=200, fail_meeting=True, force=True).run()

    assert replay.read_bytes() == control.read_bytes()
    assert audit.read_bytes() == _audit_path(control).read_bytes()
    entries = read_all_entries(replay)
    assert any(entry.kind == "meeting_aborted" for entry in entries)
    assert not any(entry.kind == "game_over" for entry in entries)
    packets = _packets(audit)
    assert len({(packet.tick, packet.agent_id) for packet in packets}) == len(packets)


def test_second_backup_move_failure_restores_the_previous_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    before = _snapshot((replay, audit))
    original_replace = Path.replace
    error = OSError("injected second backup move failure")
    moves = 0

    def replace(source: Path, target: str | Path) -> Path:
        nonlocal moves
        if source in (replay, audit):
            moves += 1
            if moves == 2:
                raise error
        return original_replace(source, target)

    monkeypatch.setattr(Path, "replace", replace)
    with pytest.raises(OSError) as raised:
        _game(replay, seed=2, force=True).run()

    assert raised.value is error
    assert moves == 2
    assert _snapshot((replay, audit)) == before
    assert set(tmp_path.iterdir()) == {replay, audit}


def test_writer_construction_failure_restores_the_previous_pair(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    before = _snapshot((replay, audit))
    error = RuntimeError("injected observation writer construction failure")
    closed_replays: list[ReplayLog] = []
    original_close = ReplayLog.close

    def close_replay(log: ReplayLog) -> None:
        closed_replays.append(log)
        original_close(log)

    def fail_constructor(*args: object, **kwargs: object) -> None:
        raise error

    monkeypatch.setattr("orchestrator.game.ObservationService", fail_constructor)
    monkeypatch.setattr(ReplayLog, "close", close_replay)
    with pytest.raises(RuntimeError) as raised:
        _game(replay, seed=2, force=True).run()

    assert raised.value is error
    assert _snapshot((replay, audit)) == before
    assert set(tmp_path.iterdir()) == {replay, audit}
    assert len(closed_replays) == 1
    assert closed_replays[0].path == replay


@pytest.mark.parametrize("fail_meeting", [False, True])
def test_recording_handles_close_on_success_and_runtime_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fail_meeting: bool
) -> None:
    replay = tmp_path / "replay.jsonl"
    _game(replay).run()
    replays: list[ReplayLog] = []
    audits: list[ObservationAuditLog] = []
    handles: list[TextIO] = []
    original_append = ReplayLog._append
    original_record = ObservationAuditLog.record_packet

    def append(log: ReplayLog, entry: dict[str, Any]) -> None:
        original_append(log, entry)
        if not replays:
            replays.append(log)
            assert log._handle is not None
            handles.append(log._handle)

    def record(log: ObservationAuditLog, packet: ObservationPacket) -> None:
        original_record(log, packet)
        if not audits:
            audits.append(log)
            assert log._handle is not None
            handles.append(log._handle)

    # Keep the writers alive after run() returns: destructor cleanup cannot
    # disguise a missing close in the game's resource lifecycle.
    monkeypatch.setattr(ReplayLog, "_append", append)
    monkeypatch.setattr(ObservationAuditLog, "record_packet", record)
    game = _game(
        replay,
        max_ticks=200 if fail_meeting else 3,
        fail_meeting=fail_meeting,
        force=True,
    )
    if fail_meeting:
        with pytest.raises(RuntimeError, match="injected provider failure"):
            game.run()
    else:
        game.run()

    assert len(handles) == 2
    assert all(handle.closed for handle in handles)
    assert replays[0]._handle is None
    assert audits[0]._handle is None


def test_failed_rollback_retains_recoverable_bytes_and_both_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    replay_before = replay.read_bytes()
    audit_before = audit.read_bytes()
    setup_error = RuntimeError("injected observation construction failure")
    rollback_error = OSError("injected replay restoration failure")
    original_replace = Path.replace
    retained: list[Path] = []

    def fail_constructor(*args: object, **kwargs: object) -> None:
        raise setup_error

    def replace(source: Path, target: str | Path) -> Path:
        if Path(target) == replay:
            retained.append(source)
            raise rollback_error
        return original_replace(source, target)

    monkeypatch.setattr("orchestrator.game.ObservationService", fail_constructor)
    monkeypatch.setattr(Path, "replace", replace)
    with pytest.raises(BaseExceptionGroup) as raised:
        _game(replay, seed=2, force=True).run()

    assert raised.value.exceptions == (setup_error, rollback_error)
    assert len(retained) == 1
    assert str(retained[0]) in str(raised.value)
    assert retained[0].read_bytes() == replay_before
    assert audit.read_bytes() == audit_before
    assert not replay.exists()


@pytest.mark.parametrize("boundary", ["seed", "factory"])
def test_state_preparation_failure_preserves_the_previous_pair(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    boundary: Literal["seed", "factory"],
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    _game(replay).run()
    before = _snapshot((replay, audit))
    error = RuntimeError(f"injected {boundary} preparation failure")

    def fail_seed(*args: object, **kwargs: object) -> None:
        raise error

    def fail_factory(player_id: PlayerId, role: Role) -> AgentInterface:
        raise error

    if boundary == "seed":
        monkeypatch.setattr("orchestrator.game.seed_initial_state", fail_seed)
    with pytest.raises(RuntimeError) as raised:
        _game(
            replay,
            seed=2,
            force=True,
            agent_factory=fail_factory if boundary == "factory" else None,
        ).run()

    assert raised.value is error
    assert _snapshot((replay, audit)) == before
    assert set(tmp_path.iterdir()) == {replay, audit}


@pytest.mark.parametrize(
    "collision",
    [
        "same",
        "normalized",
        "audit_symlink",
        "replay_symlink",
        "dangling_audit",
        "hardlink",
        "parent_alias",
        "ancestor",
    ],
)
def test_invalid_output_aliases_preserve_existing_files_and_links(
    tmp_path: Path, collision: str
) -> None:
    replay = tmp_path / "replay.jsonl"
    audit = _audit_path(replay)
    missing = tmp_path / "missing.jsonl"
    _game(replay).run()
    configured_audit = audit
    if collision == "same":
        configured_audit = replay
    elif collision == "normalized":
        directory = tmp_path / "nested"
        directory.mkdir()
        configured_audit = directory / ".." / replay.name
    elif collision == "audit_symlink":
        audit.unlink()
        audit.symlink_to(replay)
    elif collision == "replay_symlink":
        replay.unlink()
        replay.symlink_to(audit)
    elif collision == "dangling_audit":
        audit.unlink()
        audit.symlink_to(missing)
    elif collision == "hardlink":
        audit.unlink()
        os.link(replay, audit)
    elif collision == "parent_alias":
        alias = tmp_path / "alias"
        alias.symlink_to(tmp_path, target_is_directory=True)
        configured_audit = alias / replay.name
    elif collision == "ancestor":
        configured_audit = replay / "audit.jsonl"
    else:
        raise AssertionError(f"unhandled collision: {collision}")
    before = _snapshot((replay, audit, missing))

    with pytest.raises(ValueError):
        _game(replay, audit=configured_audit, seed=2, force=True).run()

    assert _snapshot((replay, audit, missing)) == before
    if collision == "hardlink":
        assert replay.samefile(audit)


def test_distinct_audit_output_through_a_parent_symlink_is_supported(
    tmp_path: Path,
) -> None:
    replay = tmp_path / "replay.jsonl"
    actual = tmp_path / "actual"
    actual.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(actual, target_is_directory=True)
    audit = alias / "observations.jsonl"
    _game(replay, audit=audit).run()
    control = tmp_path / "control" / "replay.jsonl"
    _game(control, seed=2, max_ticks=2).run()

    _game(replay, audit=audit, seed=2, max_ticks=2, force=True).run()

    assert replay.read_bytes() == control.read_bytes()
    assert audit.read_bytes() == _audit_path(control).read_bytes()
    assert alias.is_symlink()


def test_explicit_null_audit_sink_can_be_reused_with_forced_replay(
    tmp_path: Path,
) -> None:
    replay = tmp_path / "replay.jsonl"
    _game(replay, audit=Path(os.devnull)).run()
    control = tmp_path / "control" / "replay.jsonl"
    _game(control, seed=2, max_ticks=2).run()

    _game(replay, audit=Path(os.devnull), seed=2, max_ticks=2, force=True).run()

    assert replay.read_bytes() == control.read_bytes()
    assert not _audit_path(replay).exists()
    assert Path(os.devnull).is_char_device()
