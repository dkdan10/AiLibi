"""Unit tests for ``api.main._resolve_replay_dir`` (Task 4.12; 12.12; 19.24).

Since Task 12.12, ``_resolve_replay_dir`` resolves the PARENT of per-set subdirs
(``replays/samples/`` -> ``4p1i/``, ``9p2i/``), so a valid fallback slot is a
directory holding at least one per-set subdir (a subdir with
``replay-seed-*.jsonl``). Since Task 19.24 the fallbacks are anchored to the REPO
ROOT rather than the process working directory. Covers the resolution ladder:

0. An injected ``replay_dir``: honored as named, over everything else.
1. ``AILIBI_REPLAY_DIR`` set and non-empty: honored as named (populated or not).
   A RELATIVE configured path — injected or env — is resolved against the anchor,
   never the working directory; an absolute one is never rewritten.
2. Env var unset, ``<anchor>/replays/`` is a parent of a set subdir: returns it.
3. Env var unset, ``<anchor>/replays/`` is not a parent, ``<anchor>/replays/
   samples/`` is: returns that.
4. Env var unset, no slot holds a set subdir: raises ``RuntimeError`` whose
   message names the slots and points to the rescue commands.
5. The working directory is IRRELEVANT: chdir-ing somewhere else does not change
   the answer, and the default anchor is the repo root.

Filesystem state is isolated per test with pytest ``tmp_path`` passed as the
``anchor``; the env var is scrubbed with ``monkeypatch.delenv``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from api.main import _REPO_ROOT, ENV_REPLAY_DIR, _resolve_replay_dir


def _make_set(parent: Path, name: str, seed: int = 0) -> None:
    """Create ``parent/<name>/replay-seed-<seed>.jsonl`` (a minimal set subdir)."""

    set_dir = parent / name
    set_dir.mkdir(parents=True)
    (set_dir / f"replay-seed-{seed}.jsonl").write_text("{}\n")


def test_injected_replay_dir_takes_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    injected = tmp_path / "injected-replays"
    injected.mkdir()
    # Both the env var and both fallback slots are valid, to prove injection wins.
    monkeypatch.setenv(ENV_REPLAY_DIR, str(tmp_path / "from-env"))
    _make_set(tmp_path / "replays", "4p1i")
    _make_set(tmp_path / "replays" / "samples", "9p2i")

    assert _resolve_replay_dir(replay_dir=injected, anchor=tmp_path) == injected


def test_env_var_takes_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    explicit = tmp_path / "custom-replays"
    explicit.mkdir()
    monkeypatch.setenv(ENV_REPLAY_DIR, str(explicit))

    # Populate both fallback slots as valid parents to prove the env var wins.
    _make_set(tmp_path / "replays", "4p1i")
    _make_set(tmp_path / "replays" / "samples", "9p2i")

    assert _resolve_replay_dir(anchor=tmp_path) == explicit


def test_a_relative_env_path_is_anchored_not_read_from_the_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The shipped setters pass RELATIVE paths, so this is the real-world case.

    ``scripts/run_spectator.sh`` exports ``AILIBI_REPLAY_DIR=replays/samples`` and
    ``frontend/playwright.config.ts`` passes the same. Read against the process
    CWD, those would resolve to whatever ``replays/samples`` happens to exist next
    to the caller — the exact ambiguity Task 19.24 removes from the fallbacks.
    Anchored, they name one directory from everywhere.
    """

    monkeypatch.setenv(ENV_REPLAY_DIR, "replays/samples")
    decoy = tmp_path / "decoy"
    (decoy / "replays" / "samples").mkdir(parents=True)
    monkeypatch.chdir(decoy)

    assert _resolve_replay_dir(anchor=tmp_path) == tmp_path / "replays" / "samples"


def test_an_absolute_configured_path_is_never_rewritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The escape hatch: an operator naming a corpus OUTSIDE the repo gets exactly
    # that path, injected or configured.
    outside = tmp_path / "elsewhere" / "corpus"
    outside.mkdir(parents=True)

    monkeypatch.setenv(ENV_REPLAY_DIR, str(outside))
    assert _resolve_replay_dir(anchor=tmp_path / "anchor") == outside
    assert (
        _resolve_replay_dir(replay_dir=outside, anchor=tmp_path / "anchor") == outside
    )


def test_a_relative_injected_path_is_anchored_too(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # One rule for both configured slots: whoever injects a relative root means it
    # relative to the project, not to wherever the process was launched.
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)

    resolved = _resolve_replay_dir(replay_dir=Path("replays/samples"), anchor=tmp_path)

    assert resolved == tmp_path / "replays" / "samples"


def test_falls_through_to_replays_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)

    # <anchor>/replays is itself a PARENT of a set subdir -> it wins (before samples).
    _make_set(tmp_path / "replays", "4p1i")
    _make_set(tmp_path / "replays" / "samples", "9p2i")

    assert _resolve_replay_dir(anchor=tmp_path) == tmp_path / "replays"


def test_falls_through_to_samples(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)

    # <anchor>/replays exists but holds no set subdir (only a loose file), so the
    # resolver skips it and uses <anchor>/replays/samples, which does hold one.
    replays = tmp_path / "replays"
    replays.mkdir()
    (replays / "README.md").write_text("not a set\n")
    _make_set(replays / "samples", "4p1i")

    assert _resolve_replay_dir(anchor=tmp_path) == tmp_path / "replays" / "samples"


def test_invalid_name_scratch_dir_does_not_shadow_valid_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression (Codex P2): <anchor>/replays holds ONLY an invalid-name scratch
    # "set" (a dot-prefixed dir the registry's set-name filter skips), while
    # <anchor>/replays/samples holds a real set. The resolver uses the registry's
    # set definition, so <anchor>/replays has no SERVEABLE set and it falls
    # through to <anchor>/replays/samples — rather than stopping at
    # <anchor>/replays (whose /sets would then be empty and default /replays 404).
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)

    _make_set(tmp_path / "replays", ".tmp")  # invalid set name -> registry skips it
    _make_set(tmp_path / "replays" / "samples", "4p1i")

    assert _resolve_replay_dir(anchor=tmp_path) == tmp_path / "replays" / "samples"


def test_legacy_flat_samples_does_not_shadow_nested_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression (Codex round-4 P2): stale flat replays left directly under
    # <anchor>/replays/samples (pre-4p1i-move cruft) sit next to the real 4p1i/
    # subdir. <anchor>/replays must NOT win — its "samples" child is a CONTAINER
    # (has a set-subdir), not a leaf set — so the resolver falls through to
    # <anchor>/replays/samples.
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)

    samples = tmp_path / "replays" / "samples"
    _make_set(samples, "4p1i")  # <anchor>/replays/samples/4p1i/replay-seed-0.jsonl
    (samples / "replay-seed-0.jsonl").write_text("{}\n")  # stale flat cruft

    assert _resolve_replay_dir(anchor=tmp_path) == samples


def test_raises_when_no_set_subdir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)

    # Both slots exist but neither holds a per-set subdir (only loose files), so a
    # flat replay file at the root no longer counts — the resolver wants a parent.
    replays = tmp_path / "replays"
    (replays / "samples").mkdir(parents=True)
    (replays / "replay-seed-0.jsonl").write_text("{}\n")

    with pytest.raises(RuntimeError) as excinfo:
        _resolve_replay_dir(anchor=tmp_path)

    msg = str(excinfo.value)
    # Names the slots so the operator knows what was checked.
    assert ENV_REPLAY_DIR in msg
    assert "replays" in msg
    assert "samples" in msg
    # Points the user at the rescue commands.
    assert "scripts/run_spectator.sh" in msg
    assert "scripts/run_game.py" in msg


def test_resolution_ignores_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CWD-independence contract (Task 19.24), stated as a test.

    A CWD holding a perfectly good ``./replays/<set>/`` used to win; now it is
    invisible, and the anchored default answers the same wherever the process
    runs. Both halves matter: an unrelated corpus in the working directory must
    not be picked up, and the real one must still resolve from a foreign CWD.
    """

    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    _make_set(tmp_path / "replays", "9p2i")  # a decoy under the working directory
    monkeypatch.chdir(tmp_path)

    resolved = _resolve_replay_dir()

    assert resolved != Path("replays")
    assert resolved.is_absolute()
    assert resolved.is_relative_to(_REPO_ROOT)
    # And the anchored default is stable across working directories.
    monkeypatch.chdir(_REPO_ROOT)
    assert _resolve_replay_dir() == resolved
