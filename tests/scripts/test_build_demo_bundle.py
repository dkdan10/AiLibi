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
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import build_demo_bundle as bdb
from api.main import ENV_REPLAY_DIR, create_app
from api.replay_loader import DEFAULT_SET, ReplayLoader
from api.schemas import PublicResultsView

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLES = _REPO_ROOT / "replays" / "samples"
_CLIENT_TS = _REPO_ROOT / "frontend" / "src" / "api" / "client.ts"

# One 9p2i game with meetings in it (so the meeting + memory mirrors are
# non-empty); the shown set ships the game-shape profile, trimmed to it.
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


def _picker_source(entries: str) -> str:
    """A minimal `ReplayPicker.tsx` carrying just the curated block."""

    return f"export const FEATURED_GAMES: readonly FeaturedGame[] = [\n{entries}\n];\n"


def test_a_partially_parsed_curation_fails_loud(tmp_path: Path) -> None:
    """An entry the regex cannot read is an ERROR, not a silently dropped game.

    The dangerous case is not a broken block — it is a block where every entry
    but one matches. ``findall`` says nothing about the one it skipped, so the
    build would ship a frontend still advertising that featured game with no
    baked replay behind it. The per-entry brace count catches it whatever the
    reformatting was.
    """

    fake = tmp_path / "ReplayPicker.tsx"
    # Second entry: keys reordered. The compiled frontend keeps it; the old
    # "did anything match?" check would have passed with one game.
    fake.write_text(
        _picker_source(
            '  {\n    set: "9p2i",\n    seed: 2,\n    label: "a",\n  },\n'
            '  {\n    seed: 17,\n    set: "9p2i",\n    label: "b",\n  },'
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="parsed 1 of 2 entries"):
        bdb.parse_featured_games(fake)

    # …and the same block, correctly formatted, parses both.
    fake.write_text(
        _picker_source(
            '  {\n    set: "9p2i",\n    seed: 2,\n    label: "a",\n  },\n'
            '  {\n    set: "9p2i",\n    seed: 17,\n    label: "b",\n  },'
        ),
        encoding="utf-8",
    )
    assert [g.seed for g in bdb.parse_featured_games(fake)] == [2, 17]


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
    match = re.search(r"value\.replace\(/(\[\^[^/]+?\])/(g[a-z]*), \"_\"\)", source)
    assert match is not None, "pathSegment()'s static-mode regex not found in client.ts"
    client_rule = re.compile(match.group(1))

    # The `u` flag is part of the contract, not style. Without it a JS character
    # class matches UTF-16 code units, so one non-BMP character is TWO matches
    # ("😀" -> "__") where Python's code-point matching gives one ("_"). The
    # builder's collision guard cannot see a disagreement that happens in the
    # other runtime — the browser would simply request a file nobody wrote.
    assert "u" in match.group(2), (
        "pathSegment()'s static-mode regex must carry the `u` flag so JS matches "
        "code points like Python does"
    )

    meeting_id = "headless-seed-2:meeting-0"
    assert client_rule.sub("_", meeting_id) == bdb._file_segment(meeting_id)
    assert bdb._file_segment(meeting_id) == "headless-seed-2_meeting-0"
    # The case the flag exists for, pinned on the Python side.
    assert bdb._file_segment("a\U0001f600b") == "a_b"

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

    replay = api.get(
        "/replays/headless-seed-2",
        params={"set": "9p2i", "include_llm_bodies": "false"},
    )
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


#: The baked profile's keys, half by half: provenance and catalogue, and the
#: member lists cut to the baked seeds. No class table, size or count ships.
_BAKED_PROFILE_KEYS: dict[str, set[str]] = {
    "": {
        "viewModelVersion",
        "rubric_version",
        "era",
        "manifest_key",
        "source_fingerprint",
        "seedset",
        "stale",
        "constants",
        "catalogue",
        "pre_reveal",
        "reveal",
    },
    "pre_reveal": {"shelves", "chips", "games", "tripwires"},
    "pre_reveal.tripwires": {"readings"},
    "reveal": {"shelves", "decided_without_proof", "games"},
}

#: Each catalogue entry names a shelf, chip, facet or tripwire and nothing else.
_CATALOGUE_KEYS = {"name", "half", "kind", "classification"}


def baked_profile_problems(baked: dict[str, object], seeds: set[int]) -> list[str]:
    """Why a baked profile is not the trimmed shape: a stray key, or a member
    of a game the bundle does not bake."""

    problems: list[str] = []
    for path, expected in _BAKED_PROFILE_KEYS.items():
        node: object = baked
        for key in path.split(".") if path else ():
            assert isinstance(node, dict)
            node = node[key]
        assert isinstance(node, dict)
        if set(node) != expected:
            problems.append(f"{path or 'top'} keys {sorted(set(node) ^ expected)}")
    catalogue = baked["catalogue"]
    assert isinstance(catalogue, list)
    problems.extend(
        f"catalogue entry {entry.get('name')} keys {sorted(set(entry) ^ _CATALOGUE_KEYS)}"
        for entry in catalogue
        if set(entry) != _CATALOGUE_KEYS
    )
    pre = baked["pre_reveal"]
    reveal = baked["reveal"]
    assert isinstance(pre, dict) and isinstance(reveal, dict)
    pair = reveal["decided_without_proof"]
    lists = {
        **{f"shelf {s['name']}": s["members"] for s in pre["shelves"]},
        **{f"chip {c['name']}": c["members"] for c in pre["chips"]},
        "all games": pre["games"],
        **{f"tripwire {r['name']}": r["entries"] for r in pre["tripwires"]["readings"]},
        **{f"reveal shelf {s['name']}": s["members"] for s in reveal["shelves"]},
        "the right half": pair["right"]["members"],
        "the wrong half": pair["wrong"]["members"],
        "reveal facets": reveal["games"],
    }
    problems.extend(
        f"{where} holds seed {item['seed']}"
        for where, items in lists.items()
        for item in items
        if item["seed"] not in seeds
    )
    return problems


def test_the_profile_is_trimmed_to_the_baked_seeds(
    tmp_path: Path, api: TestClient
) -> None:
    """Every member list keeps the baked seed; provenance passes through."""

    bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    baked = _read(tmp_path / "data" / "9p2i" / "eval" / "game-profile.json")
    live = api.get("/eval/game-profile", params={"set": "9p2i"})
    assert live.status_code == 200
    served = live.json()
    assert isinstance(baked, dict)
    assert baked_profile_problems(baked, {2}) == []
    for field in (
        "viewModelVersion",
        "rubric_version",
        "era",
        "manifest_key",
        "source_fingerprint",
        "seedset",
        "stale",
        "constants",
        "catalogue",
    ):
        assert baked[field] == served[field], field
    assert baked["stale"] is False
    assert baked["pre_reveal"]["games"] == [
        game for game in served["pre_reveal"]["games"] if game["seed"] == 2
    ]
    assert baked["reveal"]["games"] == [
        game for game in served["reveal"]["games"] if game["seed"] == 2
    ]
    for baked_shelf, served_shelf in zip(
        baked["pre_reveal"]["shelves"], served["pre_reveal"]["shelves"], strict=True
    ):
        assert baked_shelf["members"] == [
            member for member in served_shelf["members"] if member["seed"] == 2
        ]
    assert served["reveal"]["class_tables"]
    assert served["pre_reveal"]["tripwires"]["alibi_flags"] == 15


def test_the_featured_bake_ships_seeds_19_and_14_only(tmp_path: Path) -> None:
    games = tuple(
        game for game in bdb.parse_featured_games() if game.set_name == "9p2i"
    )
    assert sorted(game.seed for game in games) == [14, 19]
    bdb.bake_data(tmp_path, games=games, samples_dir=_SAMPLES)
    path = tmp_path / "data" / "9p2i" / "eval" / "game-profile.json"
    baked = _read(path)
    assert isinstance(baked, dict)
    # Written compact, as the bundle writes its pydantic views.
    assert path.read_text(encoding="utf-8") == json.dumps(baked, separators=(",", ":"))
    assert baked_profile_problems(baked, {14, 19}) == []
    readings = baked["pre_reveal"]["tripwires"]["readings"]
    assert all(reading["entries"] == [] for reading in readings)
    pair = baked["reveal"]["decided_without_proof"]
    assert [m["seed"] for m in pair["right"]["members"]] == [14, 19]
    assert pair["wrong"]["members"] == []


def test_a_bake_that_skips_the_trim_fails_the_shape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the whole served profile baked untrimmed."""

    monkeypatch.setattr(
        bdb,
        "_trimmed_profile",
        lambda profile, seeds: profile.model_dump_json(by_alias=True),
    )
    bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    baked = _read(tmp_path / "data" / "9p2i" / "eval" / "game-profile.json")
    assert isinstance(baked, dict)
    problems = baked_profile_problems(baked, {2})
    assert "reveal keys ['class_tables']" in problems
    assert (
        "pre_reveal.tripwires keys ['alibi_flags', 'alibi_flags_evaluable']" in problems
    )
    assert any(problem.startswith("all games holds seed") for problem in problems)


def test_a_bake_passing_the_class_tables_through_fails_the_key_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the trim keeps the class tables, so every shelf size ships."""

    monkeypatch.setattr(
        bdb,
        "_UNBAKED_PROFILE_KEYS",
        (
            ("pre_reveal", "tripwires", "alibi_flags"),
            ("pre_reveal", "tripwires", "alibi_flags_evaluable"),
        ),
    )
    bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    baked = _read(tmp_path / "data" / "9p2i" / "eval" / "game-profile.json")
    assert isinstance(baked, dict)
    assert baked_profile_problems(baked, {2}) == ["reveal keys ['class_tables']"]


def test_the_four_player_set_bakes_no_profile(tmp_path: Path, api: TestClient) -> None:
    """4p1i ships none, so the bundle has no file and the reel 404s — as live."""

    bdb.bake_data(
        tmp_path,
        games=(bdb.FeaturedGame(set_name="4p1i", seed=29),),
        samples_dir=_SAMPLES,
    )
    assert not (tmp_path / "data" / "4p1i" / "eval" / "game-profile.json").exists()
    assert api.get("/eval/game-profile", params={"set": "4p1i"}).status_code == 404
    assert not (tmp_path / "data" / "4p1i" / "eval" / "rubric.json").exists()


def test_a_stale_profile_bakes_no_member(tmp_path: Path) -> None:
    import shutil

    samples = tmp_path / "samples"
    shutil.copytree(_SAMPLES / "9p2i", samples / "9p2i")
    served = samples / "9p2i" / "results-game-profile.json"
    payload = json.loads(served.read_text(encoding="utf-8"))
    served.write_text(
        json.dumps({**payload, "manifest_key": "deadbee"}), encoding="utf-8"
    )
    out = tmp_path / "out"
    bdb.bake_data(out, games=_ONE_9P2I, samples_dir=samples)
    baked = _read(out / "data" / "9p2i" / "eval" / "game-profile.json")
    assert isinstance(baked, dict)
    assert baked["stale"] is True
    assert baked_profile_problems(baked, set()) == []
    assert baked["pre_reveal"]["games"] == []


def test_rebaking_removes_the_previous_data_tree(tmp_path: Path) -> None:
    """A de-curated game must LEAVE the bundle, not linger as fetchable JSON.

    Overwrite-only baking would keep serving a dropped seed (or a dropped set)
    out of a reused output directory, contradicting the bundle's own note that it
    ships the current featured games and nothing else.
    """

    bdb.bake_data(
        tmp_path,
        games=(
            bdb.FeaturedGame(set_name="9p2i", seed=2),
            bdb.FeaturedGame(set_name="4p1i", seed=29),
        ),
        samples_dir=_SAMPLES,
    )
    assert (tmp_path / "data" / "4p1i" / "replays" / "headless-seed-29.json").is_file()

    # Re-bake with 4p1i de-curated entirely, into the same directory.
    summary = bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    assert summary.sets == ("9p2i",)
    assert not (tmp_path / "data" / "4p1i").exists()
    assert _read(tmp_path / "data" / "9p2i" / "sets.json") == {
        "sets": ["9p2i"],
        "default": "9p2i",
    }


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


def test_a_build_without_the_bundle_empty_state_is_rejected(tmp_path: Path) -> None:
    """The bundle's empty state must be present AND be the arm that compiled.

    That card is the whole Tournament tab for a visitor — the bundle bakes no
    report on purpose — and it renders from a branch only the static build
    selects, so both failures are invisible to a local run, a unit test and
    `tsc`. Each gets its own planted build: copy deleted, and the local-checkout
    arm surviving into the bundle (which would tell a visitor to run a
    tournament in a checkout they do not have).
    """

    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<html></html>", encoding="utf-8")
    emitted = tmp_path / "assets" / "index.js"

    # The demo's own sentence is gone.
    emitted.write_text(
        'const c={noReportTitle:"No tournament report."}', encoding="utf-8"
    )
    with pytest.raises(RuntimeError, match="compact results surface"):
        bdb._assert_results_compiled_in(tmp_path)

    # Both arms emitted — the gate stopped selecting, so the local guidance
    # survived dead-code elimination alongside the demo's copy.
    emitted.write_text(
        'const c={noReportBundle:"What the recordings show"};'
        'const j="scripts/run_tournament.py"',
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="LOCAL-checkout arm"):
        bdb._assert_results_compiled_in(tmp_path)

    # The static arm alone: present sentence, absent local guidance.
    emitted.write_text(
        'const c={noReportBundle:"What the recordings show"}',
        encoding="utf-8",
    )
    bdb._assert_results_compiled_in(tmp_path)


def test_the_local_guidance_marker_is_unique_to_the_arm_it_probes() -> None:
    """The absent-side marker only works if one arm is its only source.

    It is asserted ABSENT from the bundle, so a second occurrence anywhere that
    ships in both builds would fail every build for the wrong reason. Pinning it
    to the single JSX literal it probes is what keeps that a deliberate change
    rather than a mystery.
    """

    src = _REPO_ROOT / "frontend" / "src"
    hits = [
        path
        for path in src.rglob("*.ts*")
        if not path.name.endswith(".test.ts")
        and bdb._LOCAL_GUIDANCE_MARKER in path.read_text(encoding="utf-8")
    ]
    assert hits == [src / "components" / "TournamentDashboard.tsx"], hits


def test_results_marker_tracks_the_actual_public_view() -> None:
    source = (_REPO_ROOT / "frontend/src/components/PublicResults.tsx").read_text()
    assert bdb._RESULTS_MARKER in source


def test_an_empty_build_dir_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="no .*index.html"):
        bdb._assert_static_mode_compiled_in(tmp_path)
    with pytest.raises(FileNotFoundError, match="no .*index.html"):
        bdb._assert_results_compiled_in(tmp_path)


# ── the --out guard ──────────────────────────────────────────────────────────


def test_an_out_dir_containing_the_project_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The catastrophic typo, refused before Vite is ever invoked.

    `build_frontend` passes `--emptyOutDir`, and vite 8.0.16's `prepareOutDir`
    calls `emptyDir(outDir, [..., ".git"])` — it empties the target and preserves
    exactly one entry. Nothing in Vite checks that the target is not the project,
    so `--out .` from the repo root would take the checkout with it: tracked
    files recoverable from `.git`, everything untracked gone.
    """

    for destructive in (_REPO_ROOT, _REPO_ROOT / "frontend", _REPO_ROOT.parent):
        with pytest.raises(ValueError, match="refusing --out"):
            bdb.assert_safe_out_dir(destructive)

    # …and via a RELATIVE path, which `is_relative_to` would otherwise compare
    # False against the absolute repo root and wave straight through.
    monkeypatch.chdir(_REPO_ROOT)
    for spelling in (Path("."), Path("frontend"), Path("frontend/../frontend")):
        with pytest.raises(ValueError, match="refusing --out"):
            bdb.assert_safe_out_dir(spelling)


def test_an_unowned_out_dir_is_refused(tmp_path: Path) -> None:
    """Ownership is a marker this script WROTE, never a resemblance.

    "It has an index.html" is true of every static site on disk, so a
    shape-based check would wave `--out ~/my-site` through to an `emptyDir`.
    Deleting someone's files takes proof, not a family resemblance.
    """

    occupied = tmp_path / "someones-files"
    occupied.mkdir()
    (occupied / "thesis.txt").write_text("do not delete", encoding="utf-8")
    with pytest.raises(ValueError, match="carries no .ailibi-demo-bundle marker"):
        bdb.assert_safe_out_dir(occupied)
    assert (occupied / "thesis.txt").is_file()

    # An unrelated WEB project — the case a structural check would have missed.
    site = tmp_path / "my-site"
    (site / "assets").mkdir(parents=True)
    (site / "index.html").write_text("<html>my blog</html>", encoding="utf-8")
    with pytest.raises(ValueError, match="carries no .ailibi-demo-bundle marker"):
        bdb.assert_safe_out_dir(site)
    assert (site / "index.html").is_file()

    with pytest.raises(ValueError, match="not a directory"):
        bdb.assert_safe_out_dir(occupied / "thesis.txt")


def test_new_empty_and_previous_bundle_out_dirs_are_allowed(tmp_path: Path) -> None:
    """The three shapes the documented workflow actually produces."""

    bdb.assert_safe_out_dir(tmp_path / "does-not-exist-yet")

    empty = tmp_path / "empty"
    empty.mkdir()
    bdb.assert_safe_out_dir(empty)

    # A previous bundle: allowed because THIS script stamped it, and the stamp
    # is what a rebuild is allowed to destroy.
    previous = tmp_path / "previous-bundle"
    (previous / "assets").mkdir(parents=True)
    (previous / "index.html").write_text("<html></html>", encoding="utf-8")
    bdb.write_bundle_marker(previous)
    bdb.assert_safe_out_dir(previous)


def test_a_failed_build_leaves_the_out_dir_rerunnable(tmp_path: Path) -> None:
    """The ownership marker must not make a FAILED build sticky.

    Vite empties and populates the directory before the bake can fail, so
    without cleanup one wrong `--samples-dir` would leave it non-empty and
    unmarked — refused by the guard on the next, corrected attempt, after having
    already destroyed whatever bundle was there. The recovery must be "retype
    the command", not "go and rm -rf it".
    """

    # (a) the directory pre-existed: rewind to empty, which the guard accepts.
    existing = tmp_path / "existing"
    (existing / "assets").mkdir(parents=True)
    (existing / "index.html").write_text("half a build", encoding="utf-8")
    bdb.discard_partial_output(existing, remove_dir=False)
    assert existing.is_dir()
    assert not any(existing.iterdir())
    bdb.assert_safe_out_dir(existing)

    # (b) this run created it: rewind to not existing, likewise accepted.
    created = tmp_path / "created"
    (created / "assets").mkdir(parents=True)
    (created / "index.html").write_text("half a build", encoding="utf-8")
    bdb.discard_partial_output(created, remove_dir=True)
    assert not created.exists()
    bdb.assert_safe_out_dir(created)

    # Cleaning up something that is already gone is not an error.
    bdb.discard_partial_output(tmp_path / "never-there", remove_dir=True)


def test_the_marker_is_written_before_the_fallible_bake() -> None:
    """Belt to the cleanup's braces: ownership precedes the steps that can fail.

    If cleanup itself fails (permissions, a full disk), the directory is still
    one the guard accepts, so the operator is never locked out of their own
    output directory by a build that broke halfway.
    """

    source = Path(bdb.__file__).read_text(encoding="utf-8")
    marker_at = source.index("write_bundle_marker(out_dir)\n        summary =")
    bake_at = source.index("summary = bake_data(out_dir, games=games")
    assert marker_at < bake_at


def test_there_is_no_bake_only_fast_path() -> None:
    """Removed deliberately, so pin its absence.

    A reuse flag decouples two halves built from the SAME source read: the
    curated list and the resolved default set are compiled into the frontend AND
    are what the data is baked from. Re-baking over an older frontend lets them
    disagree — a de-curated game disappears through the picker's metadata join, a
    newly curated one is baked but never featured, and a curation that drops the
    old default leaves the compiled default pointing at a directory the bundle no
    longer carries. Keeping the flag correct would need the compiled curation
    stamped into the artifact and validated on every re-bake; building both
    halves every time makes the mismatch impossible instead.
    """

    source = Path(bdb.__file__).read_text(encoding="utf-8")
    assert "--skip-frontend-build" not in source
    assert "skip_frontend_build" not in source


# ── the shipped note ─────────────────────────────────────────────────────────


def test_bundle_readme_names_what_is_missing(tmp_path: Path) -> None:
    """The omission is documented IN the artifact, not only in the repo."""

    summary = bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    bdb.write_bundle_readme(tmp_path, summary)
    note = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "No tournament report" in note or "tournament eval report" in note
    assert "9p2i" in note
    # The GM data the bundle DOES carry is named, so "no GM endpoint" cannot be
    # read as "the hidden information is stripped".
    assert "roles, kill attribution, vent usage" in note


def test_the_note_names_its_source_and_claims_nothing_more(tmp_path: Path) -> None:
    """The note states WHERE the bytes came from, and makes no claim beyond it.

    A conditional "…and it was already public anyway" lived here across four
    review rounds and was wrong in a new way each time — asserted unchecked,
    then checked by path, then by `git status` (blind to ignored files), then
    against a synthesized filename rather than the one the loader consumed. The
    lesson was that the sentence promised a fact about bytes this script cannot
    establish, so it is gone: the source is named, and the reader — who can
    actually answer it for their own directory — is handed the question.

    HOW it is named is the second half. The note ships inside the artifact this
    project publishes, so it names a repository-relative path when it can and no
    filesystem path at all when it cannot — never the builder's own absolute
    path, which is a home directory to a stranger and a dead end to everyone.
    """

    alt = tmp_path / "private-recordings"
    (alt / "4p1i").mkdir(parents=True)
    src = _SAMPLES / "4p1i" / "replay-seed-29.jsonl"
    (alt / "4p1i" / src.name).write_bytes(src.read_bytes())

    out = tmp_path / "bundle"
    summary = bdb.bake_data(
        out, games=(bdb.FeaturedGame(set_name="4p1i", seed=29),), samples_dir=alt
    )
    bdb.write_bundle_readme(out, summary)
    note = (out / "README.md").read_text(encoding="utf-8")

    # Recordings from outside the checkout: the note says so and names no path.
    # The absolute one the builder resolved is what must NOT be there.
    assert "outside the repository" in note
    assert str(alt.resolve()) not in note
    assert "does not judge whether they are public" in note
    assert "already public" not in note

    # …and the SAME wording ships when the canonical samples are used: there is
    # no branch left that could reintroduce a conditional claim. Only the path's
    # rendering differs — repository-relative, because it can be.
    canonical_out = tmp_path / "canonical"
    canonical = bdb.bake_data(canonical_out, games=_ONE_9P2I, samples_dir=_SAMPLES)
    bdb.write_bundle_readme(canonical_out, canonical)
    canonical_note = (canonical_out / "README.md").read_text(encoding="utf-8")
    assert "does not judge whether they are public" in canonical_note
    assert "`replays/samples` in the repository" in canonical_note
    assert str(_SAMPLES.resolve()) not in canonical_note


def test_authored_text_with_no_host_path_passes(tmp_path: Path) -> None:
    """The real note and the real marker clear the check they ship behind."""

    summary = bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    bdb.write_bundle_readme(tmp_path, summary)
    bdb.write_bundle_marker(tmp_path)
    bdb.assert_no_host_paths(tmp_path)


def test_a_host_path_in_authored_text_fails_the_build(tmp_path: Path) -> None:
    """The check bites — on either authored file, and not on the bundle's URL.

    `_source_phrase` fixes the ONE line that carried an absolute path; this check
    is what makes the class unrepeatable, so it has to be shown failing rather
    than merely present. The perturbation is the exact defect the review found:
    a home directory interpolated into the bundle's note.
    """

    summary = bdb.bake_data(tmp_path, games=_ONE_9P2I, samples_dir=_SAMPLES)
    bdb.write_bundle_readme(tmp_path, summary)
    bdb.write_bundle_marker(tmp_path)
    note = tmp_path / "README.md"
    clean = note.read_text(encoding="utf-8")

    note.write_text(
        clean.replace(
            "`replays/samples` in the repository.",
            "`/Users/someone/projects/AiLibi/replays/samples`.",
        ),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="/Users/someone/projects/AiLibi"):
        bdb.assert_no_host_paths(tmp_path)

    # A ONE-component absolute path is caught too. `/root` is the whole point:
    # it is a complete home directory, and the one `Path.home()` resolves to for
    # a build running as root — a depth floor would wave it straight through.
    note.write_text(
        clean.replace("`replays/samples` in the repository.", "`/root`."),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="/root"):
        bdb.assert_no_host_paths(tmp_path)

    # The ownership marker is authored prose too, and is checked the same way.
    note.write_text(clean, encoding="utf-8")
    marker = tmp_path / bdb._BUNDLE_MARKER
    marker.write_text(
        marker.read_text(encoding="utf-8") + "Built in /home/ci/work/bundle.\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="/home/ci/work/bundle"):
        bdb.assert_no_host_paths(tmp_path)


def test_the_repository_url_is_not_read_as_a_host_path() -> None:
    """A check that flagged the note's own GitHub link would be unusable.

    The clean-note leg above passes with that link already in place, so this pins
    the discrimination directly: an https URL is not a filesystem path, a
    relative path is not one either, and a slash between two words is not one at
    all. What IS one is refused at any depth.
    """

    assert bdb._HOST_PATH_IN_TEXT.search("https://github.com/dkdan10/AiLibi") is None
    assert bdb._HOST_PATH_IN_TEXT.search("`replays/samples/` is public") is None
    assert bdb._HOST_PATH_IN_TEXT.search("and/or, on 2026/08/19") is None

    # Every absolute shape, at any depth and in any script — the gate claims
    # "no absolute path", so an ASCII-only or two-deep reading of it is a hole.
    for named in (
        "run `/Users/dan/x/y`",
        "built in /root",
        "built in /équipe/private",
        "built in /+srv/private",
        "built in C:\\Users\\dan",
        "built in C:/Users/dan",
        r"built in \\corp-server\private\replays",
    ):
        assert bdb._HOST_PATH_IN_TEXT.search(named) is not None, named


def test_summary_covers_full_validated_set_but_links_only_baked_cases(
    tmp_path: Path, api: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The featured head, seed 19, carries both curated cases, so its baked
    # summary is the live one over all fifty games, both cases included.
    head = (bdb.FeaturedGame(set_name="9p2i", seed=19),)
    bdb.bake_data(tmp_path, games=head, samples_dir=_SAMPLES)
    path = tmp_path / "data/9p2i/eval/summary.json"
    summary = json.loads(path.read_text())
    response = api.get("/eval/summary", params={"set": "9p2i"})
    assert response.status_code == 200
    assert summary == response.json()
    assert summary["games"] == 50
    assert [case["case_id"] for case in summary["cases"]] == [
        "witnessed-vent",
        "weak-evidence",
    ]
    assert path.stat().st_size < 50 * 1024

    # Planted: the same summary carrying a case on the baked game and one on a
    # game the bundle does not bake keeps only the first, and its meeting and
    # the observer's memory are baked beside it.
    import api.public_results as public

    real = public.build_public_results
    curated = public._curated_cases()  # noqa: SLF001
    planted_cases = (
        curated[0],
        curated[1].model_copy(update={"game_id": "headless-seed-4"}),
    )

    def planted(loader: ReplayLoader) -> PublicResultsView:
        return real(loader).model_copy(update={"cases": planted_cases})

    monkeypatch.setattr(bdb, "build_public_results", planted)
    out = tmp_path / "planted"
    bdb.bake_data(out, games=head, samples_dir=_SAMPLES)
    baked = json.loads((out / "data/9p2i/eval/summary.json").read_text())
    assert [case["game_id"] for case in baked["cases"]] == ["headless-seed-19"]
    for case in baked["cases"]:
        base = out / "data/9p2i/replays" / case["game_id"] / "meetings"
        mid = bdb._file_segment(case["meeting_id"])
        assert (base / f"{mid}.json").is_file()
        assert (base / mid / "memory" / f"{case['observer_id']}.json").is_file()


def _assert_strip_carries_every_case(
    out: Path, build: Callable[[ReplayLoader], PublicResultsView]
) -> None:
    """Every case ``build`` publishes for a baked set is in its baked summary."""

    import api.public_results as public

    for set_dir in sorted((out / "data").iterdir()):
        live = build(ReplayLoader(_SAMPLES / set_dir.name))
        baked = json.loads((set_dir / "eval/summary.json").read_text())
        assert [case["case_id"] for case in baked["cases"]] == [
            case.case_id for case in live.cases
        ], (set_dir.name, "a published case is missing from the baked summary")
    # The check is about the real curation, so the real one is non-empty.
    assert public._curated_cases()  # noqa: SLF001


def test_the_strip_carries_every_published_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The bundle bakes a case only beside its game, and bakes only featured
    # games, so a case the curation moves off the strip would vanish from the
    # demo with every other test green. Baking the strip's OWN list keeps every
    # case the live results publish.
    import api.public_results as public

    strip = bdb.parse_featured_games()
    bdb.bake_data(tmp_path / "strip", games=strip, samples_dir=_SAMPLES)
    _assert_strip_carries_every_case(tmp_path / "strip", public.build_public_results)
    nine = json.loads((tmp_path / "strip/data/9p2i/eval/summary.json").read_text())
    assert len(nine["cases"]) == 2

    # Planted: a case pointed at a game the strip does not feature is published
    # live and missing from the bundle.
    real = public.build_public_results
    curated = public._curated_cases()  # noqa: SLF001
    moved = curated[1].model_copy(
        update={"game_id": "headless-seed-2", "meeting_id": "headless-seed-2:meeting-0"}
    )

    def planted(loader: ReplayLoader) -> PublicResultsView:
        result = real(loader)
        if loader._replay_dir.name != "9p2i":  # noqa: SLF001
            return result
        return result.model_copy(update={"cases": (curated[0], moved)})

    monkeypatch.setattr(bdb, "build_public_results", planted)
    bdb.bake_data(tmp_path / "planted", games=strip, samples_dir=_SAMPLES)
    with pytest.raises(AssertionError, match="missing from the baked summary"):
        _assert_strip_carries_every_case(tmp_path / "planted", planted)
