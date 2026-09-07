"""Exercise single-game replacement through the offline CLI entry point."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from orchestrator.game import HeadlessGame, HeadlessGameResult

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


def test_a_replaced_replay_is_refused_instead_of_reporting_another_games_cost(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A replay path another writer replaced is refused, not reported on.

    The CLI reads outcome and cost back off disk, so a second
    ``run_game.py --force`` against the same ``--replay-path`` can leave this
    process printing the winner's numbers under its own seed. The read-back is
    bound to the identity this game recorded, so foreign rows exit non-zero.
    """

    monkeypatch.setenv("AILIBI_LLM_PROVIDER", "fake")
    foreign_replay = tmp_path / "foreign.jsonl"
    assert (
        run_game.main(
            ["--replay-path", str(foreign_replay), "--seed", "1", "--max-ticks", "2"]
        )
        == 0
    )
    foreign_bytes = foreign_replay.read_bytes()

    class ReplacedByAConcurrentWriter(HeadlessGame):
        """Stand in for a second forced writer finishing against the same path.

        Subclasses the same class ``run_game`` holds; imported directly so the
        type checker can see it, then substituted for the CLI's own reference.
        """

        def run(self) -> HeadlessGameResult:
            result = super().run()
            result.replay_path.write_bytes(foreign_bytes)
            return result

    monkeypatch.setattr(run_game, "HeadlessGame", ReplacedByAConcurrentWriter)
    replay = tmp_path / "game.jsonl"
    capsys.readouterr()
    assert (
        run_game.main(["--replay-path", str(replay), "--seed", "0", "--max-ticks", "2"])
        == 1
    )
    captured = capsys.readouterr()
    assert "headless-seed-1" in captured.err
    assert "headless-seed-0" in captured.err
    assert "cost_usd" not in captured.out
