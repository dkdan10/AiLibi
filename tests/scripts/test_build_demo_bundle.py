"""Tests for ``scripts/build_demo_bundle.py`` — the static demo bundle's builder.

Three things have to hold for the artifact to be worth shipping, and each is a
different kind of failure:

* the bundle bakes the CURATED games and nothing else — the featured list is read
  out of ``ReplayPicker.tsx``, so a curation edit changes the bundle and a bundle
  that quietly baked a stale list is caught here;
* every baked file sits at the URL the client will ask for — including the
  filename reduction that turns ``headless-seed-2:meeting-0`` into a portable
  name, which is duplicated across a TypeScript file and a Python file and so is
  pinned from both ends;
* the baked bytes are the SAME bytes the live API serves. A bundle that silently
  served a differently-shaped DTO would render wrong rather than fail, which is
  exactly the class of bug a browser test finds late and expensively.

The browser half — that the BUILT bundle actually plays with zero ``/api``
requests — is ``frontend/e2e/bundle.spec.ts``. This file never runs ``npm``.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import build_demo_bundle as bdb
from api.main import ENV_REPLAY_DIR, create_app
from api.replay_loader import DEFAULT_SET

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLES = _REPO_ROOT / "replays" / "samples"
_CLIENT_TS = _REPO_ROOT / "frontend" / "src" / "api" / "client.ts"

# One curated 9p2i game: a scored set (so the rubric path is exercised) with
# meetings in it (so the meeting + memory mirrors are non-empty).
_ONE_9P2I = (bdb.FeaturedGame(set_name="9p2i", seed=2),)


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    """A live spectator API over the committed samples — the parity reference.

    The env var is scoped to this module's context rather than set globally: a
    leaked ``AILIBI_REPLAY_DIR`` would silently re-point every later test's loader.
    """

    with pytest.MonkeyPatch.context() as patch:
        patch.setenv(ENV_REPLAY_DIR, str(_SAMPLES))
        yield TestClient(create_app())


def _read(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


# ── the curated list is READ, not restated ───────────────────────────────────


def test_featured_games_are_read_from_the_picker() -> None:
    """Every curated ``(set, seed)`` names a recorded replay that exists."""

    games = bdb.parse_featured_games()
    assert games, "the featured list parsed empty"
    for game in games:
        replay = _SAMPLES / game.set_name / f"replay-seed-{game.seed}.jsonl"
        assert replay.is_file(), f"featured game has no recording: {replay}"


def test_a_missing_featured_block_fails_loud(tmp_path: Path) -> None:
    """A picker with no ``FEATURED_GAMES`` raises rather than baking nothing."""

    fake = tmp_path / "ReplayPicker.tsx"
    fake.write_text("export const NOTHING = [];\n", encoding="utf-8")
    with pytest.raises(ValueError, match="FEATURED_GAMES not found"):
        bdb.parse_featured_games(fake)


def test_a_featured_seed_the_set_does_not_carry_fails_loud(tmp_path: Path) -> None:
    """A curated seed with no recording is an error, not a missing card."""

    with pytest.raises(FileNotFoundError, match="featured seeds absent"):
        bdb.bake_data(
            tmp_path,
            games=(bdb.FeaturedGame(set_name="9p2i", seed=9999),),
            samples_dir=_SAMPLES,
        )


# ── the default set ──────────────────────────────────────────────────────────


def test_default_set_prefers_the_curated_default() -> None:
    """Mirrors ``SetLoaderRegistry.default_set`` over the sets the bundle has."""

    assert bdb.resolve_default_set(("4p1i", DEFAULT_SET)) == DEFAULT_SET
    # No curated default in the bundle → the first, so the advertised default
    # always resolves to a directory that is actually there.
    assert bdb.resolve_default_set(("zzz", "4p1i")) == "4p1i"
    with pytest.raises(ValueError, match="bakes no sets"):
        bdb.resolve_default_set(())


# ── the URL mirror ───────────────────────────────────────────────────────────


def test_bake_writes_the_url_mirror_the_client_asks_for(tmp_path: Path) -> None:
    summary = bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)

    assert summary.sets == ("9p2i",)
    assert summary.default_set == "9p2i"
    assert summary.games == ("headless-seed-2",)

    data = tmp_path / "data" / "9p2i"
    assert _read(data / "sets.json") == {"sets": ["9p2i"], "default": "9p2i"}

    listing = _read(data / "replays.json")
    assert isinstance(listing, list)
    assert [row["seed"] for row in listing] == [2]

    replay = _read(data / "replays" / "headless-seed-2.json")
    assert isinstance(replay, dict)
    assert (data / "replays" / "headless-seed-2" / "beliefs.json").is_file()

    # Every meeting the replay view names has its own file, and every meeting
    # file has at least one agent memory beside it.
    meetings_dir = data / "replays" / "headless-seed-2" / "meetings"
    for meeting in replay["meetings"]:
        name = bdb._file_segment(meeting["meeting_id"])
        assert (meetings_dir / f"{name}.json").is_file()
        memories = sorted((meetings_dir / name / "memory").glob("*.json"))
        assert memories, f"no baked memory for meeting {meeting['meeting_id']}"


def test_the_filename_reduction_matches_the_client(tmp_path: Path) -> None:
    """The rule is duplicated across two languages — pin BOTH ends of it.

    ``pathSegment()`` in ``frontend/src/api/client.ts`` and ``_file_segment()``
    here have to agree exactly, or the browser asks for files the builder never
    wrote. The regex is lifted out of the TypeScript source and re-run in Python
    over a real meeting id, so an edit to either side fails here.
    """

    source = _CLIENT_TS.read_text(encoding="utf-8")
    match = re.search(r"value\.replace\(/(\[\^[^/]+?\])/g, \"_\"\)", source)
    assert match is not None, "pathSegment()'s static-mode regex not found in client.ts"
    client_rule = re.compile(match.group(1))

    meeting_id = "headless-seed-2:meeting-0"
    assert client_rule.sub("_", meeting_id) == bdb._file_segment(meeting_id)
    assert bdb._file_segment(meeting_id) == "headless-seed-2_meeting-0"

    bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    baked = tmp_path / "data/9p2i/replays/headless-seed-2/meetings"
    assert (baked / "headless-seed-2_meeting-0.json").is_file()


def test_a_filename_collision_fails_loud(tmp_path: Path) -> None:
    """Two ids reducing to one name must raise, never silently overwrite."""

    writer = bdb._Writer(tmp_path)
    writer.write("a/b.json", "{}", source="id:one")
    with pytest.raises(ValueError, match="name collision"):
        writer.write("a/b.json", "{}", source="id_one")


# ── parity with the live API ─────────────────────────────────────────────────


def test_baked_bytes_are_the_bytes_the_live_api_serves(
    tmp_path: Path, api: TestClient
) -> None:
    """The bundle is a recording of the API's answers, not a second encoding.

    Serialization aliases (``viewModelVersion``) and by-alias dumping are easy to
    get subtly wrong in a hand-rolled baker; comparing against the real app is the
    only check that stays true when a DTO changes.
    """

    bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    data = tmp_path / "data" / "9p2i"

    replay = api.get("/replays/headless-seed-2", params={"set": "9p2i"})
    assert replay.status_code == 200
    baked_replay = _read(data / "replays" / "headless-seed-2.json")
    assert baked_replay == replay.json()

    listing = api.get("/replays", params={"set": "9p2i"}).json()
    live_row = next(row for row in listing if row["seed"] == 2)
    baked_listing = _read(data / "replays.json")
    assert isinstance(baked_listing, list)
    assert baked_listing == [live_row]

    beliefs = api.get("/replays/headless-seed-2/beliefs", params={"set": "9p2i"})
    assert (
        _read(data / "replays" / "headless-seed-2" / "beliefs.json") == beliefs.json()
    )

    assert isinstance(baked_replay, dict)
    meeting_id = str(baked_replay["meetings"][0]["meeting_id"])
    name = bdb._file_segment(meeting_id)
    meetings_dir = data / "replays" / "headless-seed-2" / "meetings"
    live_meeting = api.get(
        f"/replays/headless-seed-2/meetings/{meeting_id}", params={"set": "9p2i"}
    )
    assert _read(meetings_dir / f"{name}.json") == live_meeting.json()

    agent = sorted((meetings_dir / name / "memory").glob("*.json"))[0]
    live_memory = api.get(
        f"/replays/headless-seed-2/meetings/{meeting_id}/memory/{agent.stem}",
        params={"set": "9p2i"},
    )
    assert live_memory.status_code == 200
    assert _read(agent) == live_memory.json()


def test_rubric_is_trimmed_to_the_baked_seeds(tmp_path: Path, api: TestClient) -> None:
    """Everything but ``per_game`` passes through; ``per_game`` is subsetted.

    The Highlights reel builds its cards FROM ``per_game``, so a full 50-row
    rubric in a one-game bundle would render 49 cards that 404 on click.
    """

    bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    baked = _read(tmp_path / "data" / "9p2i" / "eval" / "rubric.json")
    live = api.get("/eval/rubric", params={"set": "9p2i"}).json()

    assert isinstance(baked, dict)
    assert [row["seed"] for row in baked["per_game"]] == [2]
    assert baked["per_game"] == [row for row in live["per_game"] if row["seed"] == 2]
    for field in ("seedset", "git_head", "manifest_sha", "stale", "viewModelVersion"):
        assert baked[field] == live[field], field


def test_an_unscored_set_bakes_no_rubric(tmp_path: Path) -> None:
    """4p1i ships none, so the bundle has no file and the reel 404s — as live."""

    bdb.bake_data(
        tmp_path,
        games=(bdb.FeaturedGame(set_name="4p1i", seed=29),),
        samples_dir=_SAMPLES,
    )
    assert not (tmp_path / "data" / "4p1i" / "eval" / "rubric.json").exists()


# ── the frontend-build guard ─────────────────────────────────────────────────


def test_a_non_static_build_is_rejected(tmp_path: Path) -> None:
    """The guard that stops a bundle shipping with the seam switched OFF.

    Its failure mode is the worst one available: a complete-looking bundle that
    calls an API nobody is running. The marker only survives dead-code
    elimination when the static branch compiled in.
    """

    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    (tmp_path / "assets" / "index.js").write_text(
        'fetch("/api/sets")', encoding="utf-8"
    )
    with pytest.raises(RuntimeError, match="carries no './data' data root"):
        bdb._assert_static_mode_compiled_in(tmp_path)

    (tmp_path / "assets" / "index.js").write_text(
        'const o="./data";fetch(`${o}/9p2i/sets.json`)', encoding="utf-8"
    )
    bdb._assert_static_mode_compiled_in(tmp_path)


def test_an_empty_build_dir_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="no .*index.html"):
        bdb._assert_static_mode_compiled_in(tmp_path)


# ── the shipped note ─────────────────────────────────────────────────────────


def test_bundle_readme_names_what_is_missing(tmp_path: Path) -> None:
    """The omission is documented IN the artifact, not only in the repo."""

    summary = bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    bdb.write_bundle_readme(tmp_path, summary)
    note = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "No tournament report" in note or "tournament eval report" in note
    assert "9p2i" in note
