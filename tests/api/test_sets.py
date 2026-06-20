"""Tests for multi-set serving + the ``GET /sets`` route (Task 12.12;
design/phase-12/stage-1-design.md §2.1, §7).

Covers the three guarantees the set selector + per-set serving rest on:

* ``SetLoaderRegistry`` lists the parent's per-set subdirs, AUTO-GROWS when a new
  set is recorded, skips stray non-set entries, caches a per-set loader, and
  rejects unknown / path-traversal set names;
* ``GET /sets`` surfaces that list + the default-served set;
* ``/replays`` and ``/eval/*`` are set-parametrized over the per-set loader, with
  determinism holding PER SET across the two committed sets, and an unknown set is
  a 404.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import ENV_REPLAY_DIR, create_app
from api.replay_loader import DEFAULT_SET, ReplayLoader, SetLoaderRegistry

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT = _REPO_ROOT / "replays" / "samples"
_COMMITTED_4P1I = _PARENT / "4p1i"
# A small, fast committed 4p1i seed used to stamp fake set subdirs in tmp dirs.
_FAST_SEED = 0


def _stamp_set(
    parent: Path, name: str, *, seeds: tuple[int, ...] = (_FAST_SEED,)
) -> Path:
    """Create ``parent/<name>/`` and copy committed 4p1i replays into it."""

    set_dir = parent / name
    set_dir.mkdir(parents=True)
    for seed in seeds:
        src = _COMMITTED_4P1I / f"replay-seed-{seed}.jsonl"
        (set_dir / src.name).write_bytes(src.read_bytes())
    return set_dir


def _client(parent: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # The env var is honored as-is as the PARENT of per-set subdirs (Task 12.12).
    monkeypatch.setenv(ENV_REPLAY_DIR, str(parent))
    return TestClient(create_app())


# ── SetLoaderRegistry ────────────────────────────────────────────────────────


def test_available_sets_lists_committed_subdirs() -> None:
    registry = SetLoaderRegistry(_PARENT)
    assert registry.available_sets() == ["4p1i", "9p2i"]


def test_available_sets_skips_stray_non_set_entries(tmp_path: Path) -> None:
    _stamp_set(tmp_path, "4p1i")
    _stamp_set(tmp_path, "9p2i")
    # A loose top-level file (a README) and a replay-less subdir are NOT sets.
    (tmp_path / "README.md").write_text("not a set\n")
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "notes.txt").write_text("no replays here\n")
    registry = SetLoaderRegistry(tmp_path)
    assert registry.available_sets() == ["4p1i", "9p2i"]


def test_available_sets_auto_grows(tmp_path: Path) -> None:
    _stamp_set(tmp_path, "4p1i")
    registry = SetLoaderRegistry(tmp_path)
    assert registry.available_sets() == ["4p1i"]
    # A newly-recorded set subdir appears with no code change (the listing is
    # recomputed from disk each call).
    _stamp_set(tmp_path, "7p2i")
    assert registry.available_sets() == ["4p1i", "7p2i"]


def test_available_sets_empty_for_missing_parent(tmp_path: Path) -> None:
    assert SetLoaderRegistry(tmp_path / "nope").available_sets() == []


def test_get_returns_per_set_loader_and_caches(tmp_path: Path) -> None:
    _stamp_set(tmp_path, "a")
    _stamp_set(tmp_path, "b")
    registry = SetLoaderRegistry(tmp_path)
    loader_a = registry.get("a")
    assert isinstance(loader_a, ReplayLoader)
    # Cached per set: the same set returns the same loader instance (its per-game
    # caches persist), and distinct sets get distinct loaders.
    assert registry.get("a") is loader_a
    assert registry.get("b") is not loader_a


def test_get_unknown_set_raises_file_not_found(tmp_path: Path) -> None:
    _stamp_set(tmp_path, "a")
    with pytest.raises(FileNotFoundError):
        SetLoaderRegistry(tmp_path).get("missing")


@pytest.mark.parametrize("bad", ["../9p2i", "a/b", "/abs", "..", ".", ""])
def test_get_rejects_path_traversal_set_name(tmp_path: Path, bad: str) -> None:
    with pytest.raises(ValueError):
        SetLoaderRegistry(tmp_path).get(bad)


# ── GET /sets ────────────────────────────────────────────────────────────────


def test_sets_route_lists_committed_sets_and_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with _client(_PARENT, monkeypatch) as client:
        response = client.get("/sets")
    assert response.status_code == 200
    body = response.json()
    assert body["sets"] == ["4p1i", "9p2i"]
    assert body["default"] == DEFAULT_SET  # the no-`set` request resolves here


def test_sets_route_auto_grows(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stamp_set(tmp_path, "4p1i")
    with _client(tmp_path, monkeypatch) as client:
        assert client.get("/sets").json()["sets"] == ["4p1i"]
    _stamp_set(tmp_path, "9p2i")
    # A fresh app re-reads the parent, so the new set appears with no code change.
    with _client(tmp_path, monkeypatch) as client:
        assert client.get("/sets").json()["sets"] == ["4p1i", "9p2i"]


def test_sets_route_default_falls_back_to_first_when_default_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # When the configured DEFAULT_SET is not present, the advertised default is the
    # first available set so it always resolves.
    _stamp_set(tmp_path, "7p2i")
    with _client(tmp_path, monkeypatch) as client:
        body = client.get("/sets").json()
    assert body["sets"] == ["7p2i"]
    assert body["default"] == "7p2i"


# ── set-parametrized serving + per-set determinism ───────────────────────────


def test_replays_is_set_parametrized(monkeypatch: pytest.MonkeyPatch) -> None:
    with _client(_PARENT, monkeypatch) as client:
        # Default (no `set`) resolves to DEFAULT_SET (4p1i); both committed sets
        # carry seeds 0..49, so both list 50 replays over their own loader.
        default = client.get("/replays")
        nine = client.get("/replays", params={"set": "9p2i"})
    assert default.status_code == 200
    assert nine.status_code == 200
    assert len(default.json()) == 50
    assert len(nine.json()) == 50


def test_eval_rubric_is_per_set(monkeypatch: pytest.MonkeyPatch) -> None:
    with _client(_PARENT, monkeypatch) as client:
        # 9p2i ships a rubric; the flat 4p1i default ships none (404 → empty state).
        nine = client.get("/eval/rubric", params={"set": "9p2i"})
        four = client.get("/eval/rubric", params={"set": "4p1i"})
    assert nine.status_code == 200
    assert nine.json()["seedset"] == "9p2i"
    assert four.status_code == 404


def test_tournament_report_is_per_set(monkeypatch: pytest.MonkeyPatch) -> None:
    with _client(_PARENT, monkeypatch) as client:
        four = client.get("/eval/tournament-report", params={"set": "4p1i"})
        nine = client.get("/eval/tournament-report", params={"set": "9p2i"})
    assert four.status_code == 200
    assert nine.status_code == 200


def test_unknown_set_is_404_on_replays(monkeypatch: pytest.MonkeyPatch) -> None:
    with _client(_PARENT, monkeypatch) as client:
        assert client.get("/replays", params={"set": "nope"}).status_code == 404
        # A path-traversal set name is likewise rejected (never escapes the parent).
        assert client.get("/replays", params={"set": "../9p2i"}).status_code == 404


def test_determinism_holds_per_set() -> None:
    # The determinism gate runs PER SET (Task 12.12 DoD): each committed set
    # reconstructs byte-identically through its own per-set loader. A divergence
    # raises ReplayStateMismatchError inside load_replay.
    registry = SetLoaderRegistry(_PARENT)
    for set_name in registry.available_sets():
        loader = registry.get(set_name)
        replay = loader.load_replay(f"headless-seed-{_FAST_SEED}")
        assert replay.metadata.game_id == f"headless-seed-{_FAST_SEED}"
