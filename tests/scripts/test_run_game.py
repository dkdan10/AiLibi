"""Exercise single-game replacement through the offline CLI entry point."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

import run_game


@pytest.mark.parametrize("explicit_audit", [False, True])
def test_force_replaces_replay_and_audit_without_accumulating_packets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, explicit_audit: bool
) -> None:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    replay = tmp_path / "game.jsonl"
    audit = (
        tmp_path / "observations" / "custom.jsonl"
        if explicit_audit
        else tmp_path / "game.audit.jsonl"
    )
    args = ["--replay-path", str(replay), "--seed", "0", "--max-ticks", "2"]
    if explicit_audit:
        args.extend(["--audit-log-path", str(audit)])
    assert run_game.main(args) == 0
    original = replay.read_bytes(), audit.read_bytes()
    assert len(original[1].splitlines()) == 8

    with pytest.raises(FileExistsError):
        run_game.main(args)
    assert (replay.read_bytes(), audit.read_bytes()) == original

    assert run_game.main([*args, "--force"]) == 0
    assert (replay.read_bytes(), audit.read_bytes()) == original


def test_force_preserves_explicit_null_audit_sink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    null_path = Path(os.devnull)
    before = null_path.stat()
    replay = tmp_path / "game.jsonl"
    args = [
        "--replay-path",
        str(replay),
        "--audit-log-path",
        str(null_path),
        "--max-ticks",
        "2",
        "--force",
    ]
    assert run_game.main(args) == 0
    original = replay.read_bytes()
    assert run_game.main(args) == 0
    assert replay.read_bytes() == original
    after = null_path.stat()
    assert stat.S_ISCHR(after.st_mode)
    assert (after.st_dev, after.st_ino) == (before.st_dev, before.st_ino)
    assert not (tmp_path / "game.audit.jsonl").exists()
