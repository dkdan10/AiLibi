"""Spectator/API discovery non-collision for the ML-calibration corpus (Task 15.12).

The corpus lands under ``replays/ml_corpus/<set>/`` — a TWO-level nesting under
``replays/`` that is LOAD-BEARING. The API resolves the PARENT of per-set subdirs
(Task 12.12): it walks ``<anchor>/replays`` then ``<anchor>/replays/samples`` and
stops at the first slot that holds a LEAF set (a subdir with
``replay-seed-*.jsonl`` and no replay-bearing child of its own —
:func:`api.replay_loader._is_set_dir`). The anchor is the repo root since Task
19.24 — never the working directory — so these tests pass ``anchor=tmp_path``
to point the same walk at a synthetic layout.

Because ``replays/ml_corpus/`` is a parent-OF-parents (its children ``9p2i`` /
``4p1i`` hold the replays), it is NOT a leaf set, so it does not make
``<anchor>/replays`` an active parent. Default spectator resolution therefore
keeps returning ``<anchor>/replays/samples`` and serving the canonical sets — the
corpus is invisible. An operator can still opt-in serve a corpus set explicitly
via ``AILIBI_REPLAY_DIR=replays/ml_corpus``.

The contrast test pins WHY the nesting matters: a set placed DIRECTLY under
``replays/`` (a flat ``replays/<set>/replay-seed-*.jsonl``) WOULD make
``<anchor>/replays`` the active parent and SHADOW the canonical samples.

These pin the discovery SEMANTICS against a faithful synthetic layout, so the
guarantee holds without depending on the multi-hour operator recording (the real
``replays/ml_corpus/`` sets are recorded by ``scripts/record_ml_corpus.sh``).
Filesystem state is isolated per test with ``tmp_path``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from api.main import ENV_REPLAY_DIR, _resolve_replay_dir
from api.replay_loader import SetLoaderRegistry, _is_set_dir


def _make_set(parent: Path, name: str, seed: int = 0) -> None:
    """Create ``parent/<name>/replay-seed-<seed>.jsonl`` (a minimal leaf set)."""

    set_dir = parent / name
    set_dir.mkdir(parents=True, exist_ok=True)
    (set_dir / f"replay-seed-{seed}.jsonl").write_text("{}\n")


def _make_corpus_layout(root: Path) -> None:
    """Build ``root/replays/{samples,ml_corpus}/{9p2i,4p1i}/`` (the shipped layout).

    Canonical samples at seed 0; the corpus at a fresh seed (1000), two-level
    nested under ``ml_corpus``.
    """

    replays = root / "replays"
    _make_set(replays / "samples", "9p2i", seed=0)
    _make_set(replays / "samples", "4p1i", seed=0)
    _make_set(replays / "ml_corpus", "9p2i", seed=1000)
    _make_set(replays / "ml_corpus", "4p1i", seed=1000)


# -- default resolution ignores the corpus ------------------------------------


def test_default_resolution_ignores_ml_corpus(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # With the corpus present alongside the canonical samples, default resolution
    # must STILL land on <anchor>/replays/samples — ml_corpus does not make
    # <anchor>/replays an active parent.
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    _make_corpus_layout(tmp_path)

    assert _resolve_replay_dir(anchor=tmp_path) == tmp_path / "replays" / "samples"


def test_replays_parent_has_no_leaf_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Neither ``samples`` nor ``ml_corpus`` is a leaf set (both are parents-of-sets),
    # so ``./replays`` advertises no serveable set at all.
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)
    _make_corpus_layout(tmp_path)

    assert SetLoaderRegistry(Path("./replays")).available_sets() == []


def test_default_served_sets_are_the_canonical_samples_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The registry over the resolved parent serves exactly the canonical sets; the
    # corpus names never appear in the default listing.
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    _make_corpus_layout(tmp_path)

    parent = _resolve_replay_dir(anchor=tmp_path)
    registry = SetLoaderRegistry(parent)
    assert registry.available_sets() == ["4p1i", "9p2i"]


def test_ml_corpus_root_is_not_itself_a_set(tmp_path: Path) -> None:
    # ``replays/ml_corpus`` is a parent-of-sets, not a leaf set: it holds no
    # ``replay-seed-*.jsonl`` directly, and its children do.
    _make_corpus_layout(tmp_path)
    ml_corpus = tmp_path / "replays" / "ml_corpus"
    assert _is_set_dir(ml_corpus) is False
    assert _is_set_dir(ml_corpus / "9p2i") is True
    assert _is_set_dir(ml_corpus / "4p1i") is True


# -- explicit opt-in serving still works --------------------------------------


def test_explicit_env_serves_corpus_sets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # An operator points AILIBI_REPLAY_DIR at the corpus root explicitly: the env
    # slot is honored verbatim, and the registry over it serves the corpus sets.
    _make_corpus_layout(tmp_path)
    corpus_root = tmp_path / "replays" / "ml_corpus"
    monkeypatch.setenv(ENV_REPLAY_DIR, str(corpus_root))

    assert _resolve_replay_dir() == corpus_root
    registry = SetLoaderRegistry(corpus_root)
    assert registry.available_sets() == ["4p1i", "9p2i"]


def test_explicit_corpus_set_loads(tmp_path: Path) -> None:
    # A corpus set opted-in explicitly resolves to a per-set loader (the same
    # serving path the canonical sets use); an unknown corpus set 404s.
    _make_corpus_layout(tmp_path)
    corpus_root = tmp_path / "replays" / "ml_corpus"
    registry = SetLoaderRegistry(corpus_root)

    assert registry.get("9p2i") is not None
    assert registry.get("4p1i") is not None
    with pytest.raises(FileNotFoundError):
        registry.get("does-not-exist")


# -- the contrast: WHY the two-level nesting is load-bearing -------------------


def test_flat_set_under_replays_would_shadow_samples(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # If the corpus had been placed as a FLAT set directly under replays/ (the
    # mistake the nesting avoids), <anchor>/replays would hold a leaf set and
    # become the active parent — SHADOWING <anchor>/replays/samples. This pins the
    # failure mode the ml_corpus/<set>/ nesting exists to prevent.
    monkeypatch.delenv(ENV_REPLAY_DIR, raising=False)
    monkeypatch.chdir(tmp_path)
    replays = tmp_path / "replays"
    _make_set(replays, "ml_corpus_9p2i", seed=1000)  # FLAT — directly under replays/
    _make_set(replays / "samples", "9p2i", seed=0)
    _make_set(replays / "samples", "4p1i", seed=0)

    # <anchor>/replays now has a leaf set, so it wins — and the canonical samples
    # are shadowed (only the flat corpus set is served).
    assert _resolve_replay_dir(anchor=tmp_path) == replays
    assert SetLoaderRegistry(Path("./replays")).available_sets() == ["ml_corpus_9p2i"]
