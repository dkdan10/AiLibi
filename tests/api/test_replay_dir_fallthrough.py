"""Unit tests for ``api.main._resolve_replay_dir`` (Task 4.12; Task 12.12).

Since Task 12.12, ``_resolve_replay_dir`` resolves the PARENT of per-set subdirs
(``replays/samples/`` -> ``4p1i/``, ``9p2i/``), so a valid fallback slot is a
directory holding at least one per-set subdir (a subdir with
``replay-seed-*.jsonl``). Covers the fallthrough paths:

1. ``AILIBI_REPLAY_DIR`` set and non-empty: honored verbatim (populated or not).
2. Env var unset, ``./replays/`` is a parent of a set subdir: returns ``./replays``.
3. Env var unset, ``./replays/`` is not a parent, ``./replays/samples/`` is:
   returns ``./replays/samples``.
4. Env var unset, no slot holds a set subdir: raises ``RuntimeError`` whose
   message names the slots and points to the rescue commands.

Filesystem state is isolated per test with pytest ``tmp_path`` +
``monkeypatch.chdir``; the env var is scrubbed with ``monkeypatch.delenv``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from api.main import ENV_REPLAY_DIR, _resolve_replay_dir


def _make_set(parent: Path, name: str, seed: int = 0) -> None:
    """Create ``parent/<name>/replay-seed-<seed>.jsonl`` (a minimal set subdir)."""

    set_dir = parent / name
    set_dir.mkdir(parents=True)
    (set_dir / f"replay-seed-{seed}.jsonl").write_text("{}\n")


def test_env_var_takes_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    explicit = tmp_path / "custom-replays"
    explicit.mkdir()
    monkeypatch.setenv(ENV_REPLAY_DIR, str(explicit))
    monkeypatch.chdir(tmp_path)

    # Populate both fallback slots as valid parents to prove the env var wins.
    _make_set(tmp_path / "replays", "4p1i")
    _make_set(tmp_path / "replays" / "samples", "9p2i")

    assert _resolve_replay_dir() == explicit


def test_falls_through_to_replays_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    # ./replays is itself a PARENT of a set subdir -> it wins (before samples).
    _make_set(tmp_path / "replays", "4p1i")
    _make_set(tmp_path / "replays" / "samples", "9p2i")

    assert _resolve_replay_dir() == Path("./replays")


def test_falls_through_to_samples(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    # ./replays exists but holds no set subdir (only a loose file), so the resolver
    # skips it and uses ./replays/samples, which does hold a set subdir.
    replays = tmp_path / "replays"
    replays.mkdir()
    (replays / "README.md").write_text("not a set\n")
    _make_set(replays / "samples", "4p1i")

    assert _resolve_replay_dir() == Path("./replays/samples")


def test_invalid_name_scratch_dir_does_not_shadow_valid_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression (Codex P2): ./replays holds ONLY an invalid-name scratch "set" (a
    # dot-prefixed dir the registry's set-name filter skips), while ./replays/samples
    # holds a real set. The resolver uses the registry's set definition, so ./replays
    # has no SERVEABLE set and it falls through to ./replays/samples — rather than
    # stopping at ./replays (whose /sets would then be empty and default /replays
    # 404).
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    _make_set(tmp_path / "replays", ".tmp")  # invalid set name -> registry skips it
    _make_set(tmp_path / "replays" / "samples", "4p1i")

    assert _resolve_replay_dir() == Path("./replays/samples")


def test_legacy_flat_samples_does_not_shadow_nested_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression (Codex round-4 P2): stale flat replays left directly under
    # ./replays/samples (pre-4p1i-move cruft) sit next to the real 4p1i/ subdir.
    # ./replays must NOT win — its "samples" child is a CONTAINER (has a set-subdir),
    # not a leaf set — so the resolver falls through to ./replays/samples.
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    samples = tmp_path / "replays" / "samples"
    _make_set(samples, "4p1i")  # ./replays/samples/4p1i/replay-seed-0.jsonl
    (samples / "replay-seed-0.jsonl").write_text("{}\n")  # stale flat cruft

    assert _resolve_replay_dir() == Path("./replays/samples")


def test_raises_when_no_set_subdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    # Both slots exist but neither holds a per-set subdir (only loose files), so a
    # flat replay file at the root no longer counts — the resolver wants a parent.
    replays = tmp_path / "replays"
    (replays / "samples").mkdir(parents=True)
    (replays / "replay-seed-0.jsonl").write_text("{}\n")

    with pytest.raises(RuntimeError) as excinfo:
        _resolve_replay_dir()

    msg = str(excinfo.value)
    # Names the slots so the operator knows what was checked.
    assert ENV_REPLAY_DIR in msg
    assert "replays" in msg
    assert "samples" in msg
    # Points the user at the rescue commands.
    assert "scripts/run_spectator.sh" in msg
    assert "scripts/run_game.py" in msg
