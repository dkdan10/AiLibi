"""Unit tests for ``api.main._resolve_replay_dir`` (Task 4.12).

Covers all four fallthrough paths defined by the task contract:

1. ``AILIBI_REPLAY_DIR`` set and non-empty: honored verbatim.
2. Env var unset, ``./replays/`` populated: returns ``./replays``.
3. Env var unset, ``./replays/`` empty (or absent), ``./replays/samples/``
   populated: returns ``./replays/samples``.
4. Env var unset, neither directory populated: raises ``RuntimeError`` whose
   message names all three slots and points to the rescue commands.

Filesystem state is isolated per test with pytest ``tmp_path`` +
``monkeypatch.chdir``; the env var is scrubbed with ``monkeypatch.delenv``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from api.main import ENV_REPLAY_DIR, _resolve_replay_dir


def test_env_var_takes_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    explicit = tmp_path / "custom-replays"
    explicit.mkdir()
    monkeypatch.setenv(ENV_REPLAY_DIR, str(explicit))
    monkeypatch.chdir(tmp_path)

    # Populate both fallback slots to prove the env var wins regardless.
    (tmp_path / "replays").mkdir()
    (tmp_path / "replays" / "replay-seed-0.jsonl").write_text("{}\n")
    (tmp_path / "replays" / "samples").mkdir()
    (tmp_path / "replays" / "samples" / "replay-seed-1.jsonl").write_text("{}\n")

    assert _resolve_replay_dir() == explicit


def test_falls_through_to_replays_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    replays = tmp_path / "replays"
    replays.mkdir()
    (replays / "replay-seed-7.jsonl").write_text("{}\n")
    # Samples populated too — the priority is ./replays/ before ./replays/samples/.
    samples = replays / "samples"
    samples.mkdir()
    (samples / "replay-seed-9.jsonl").write_text("{}\n")

    assert _resolve_replay_dir() == Path("./replays")


def test_falls_through_to_samples(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    # ./replays/ exists but holds no replay-seed-*.jsonl files; resolver must
    # skip it and try ./replays/samples/ next.
    replays = tmp_path / "replays"
    replays.mkdir()
    (replays / "README.md").write_text("not a replay\n")
    samples = replays / "samples"
    samples.mkdir()
    (samples / "replay-seed-22.jsonl").write_text("{}\n")

    assert _resolve_replay_dir() == Path("./replays/samples")


def test_raises_when_all_slots_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    with pytest.raises(RuntimeError) as excinfo:
        _resolve_replay_dir()

    msg = str(excinfo.value)
    # Names all three slots so the operator knows what was checked.
    assert ENV_REPLAY_DIR in msg
    assert "replays" in msg
    assert "samples" in msg
    # Points the user at the rescue commands.
    assert "scripts/run_spectator.sh" in msg
    assert "scripts/run_game.py" in msg
