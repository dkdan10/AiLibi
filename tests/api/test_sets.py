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

Task 19.9 adds the curated-default pins: ``DEFAULT_SET`` is the 9p2i spectator set
(not the 4p1i fixture), the game-shape profile's stamp agrees with the loader's
own provenance key on the committed manifest, and every hand-curated featured
seed exists in the set it names. Version 1 of the rubric writes no served file.
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from api.main import ENV_REPLAY_DIR, create_app
from api.schemas import ReplayView
from api.replay_loader import (
    DEFAULT_SET,
    ReplayLoader,
    SetLoaderRegistry,
    _manifest_git_sha,
    _manifest_seed_shas,
    _provenance_is_stale,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROFILE_FILENAME = "results-game-profile.json"
_PARENT = _REPO_ROOT / "replays" / "samples"
_COMMITTED_4P1I = _PARENT / "4p1i"
# A small, fast committed 4p1i seed used to stamp fake set subdirs in tmp dirs.
_FAST_SEED = 0

# The retired version-1 scorer is a top-level lab module (experiments/lab is not
# on mypy_path); import it dynamically so mypy does not try to resolve it by name.
_LAB_DIR = _REPO_ROOT / "experiments" / "lab"
if str(_LAB_DIR) not in sys.path:
    sys.path.insert(0, str(_LAB_DIR))
_rubric_score: Any = importlib.import_module("rubric_score")

# The committed featured list lives in the picker as DATA (Task 19.9); the seeds
# are read back out of the source so a curated seed that no set carries fails here
# instead of rendering as a dead entry in the UI.
_PICKER_TSX = _REPO_ROOT / "frontend" / "src" / "components" / "ReplayPicker.tsx"
_FEATURED_BLOCK = re.compile(
    r"FEATURED_GAMES: readonly FeaturedGame\[\] = \[(.*?)\n\];", re.DOTALL
)
_FEATURED_ENTRY = re.compile(r'set: "([^"]+)",\s*\n\s*seed: (\d+),')
_FEATURED_LABEL = re.compile(r'label:\s*\n?\s*"([^"]*)"')


def _featured_block() -> str:
    block = _FEATURED_BLOCK.search(_PICKER_TSX.read_text(encoding="utf-8"))
    assert block is not None, "FEATURED_GAMES not found in ReplayPicker.tsx"
    return block.group(1)


def _parse_featured_games() -> list[tuple[str, int]]:
    """The committed ``(set, seed)`` featured pairs, in their curated order."""

    return [
        (set_name, int(seed))
        for set_name, seed in _FEATURED_ENTRY.findall(_featured_block())
    ]


def _featured_heads() -> list[tuple[str, int]]:
    """The FIRST featured pair of every set, in the strip's curated order.

    The picker renders one row per set and the guided tour opens the curated head
    OF THE SET IT TARGETS (``frontend/src/components/GuidedTour.tsx``), so "the
    opener" is a per-set thing: pinning only ``featured[0]`` would leave the 4p1i
    row's opener unchecked behind a grounded 9p2i one. Derived from the committed
    data rather than typed, so a set added to the strip is covered the day it
    lands instead of the day somebody remembers to extend this list.
    """

    heads: dict[str, int] = {}
    for set_name, seed in _parse_featured_games():
        heads.setdefault(set_name, seed)
    return list(heads.items())


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


def test_get_rejects_replay_less_subdir(tmp_path: Path) -> None:
    # Regression (Codex P2): a stray / in-progress subdir with no replays is NOT a
    # set — `/sets` already omits it, and an explicit get() must 404 too (not serve
    # an empty-but-200 list), so resolution and listing stay consistent.
    _stamp_set(tmp_path, "real")
    (tmp_path / "scratch").mkdir()  # exists, but ships no replay-seed-*.jsonl
    registry = SetLoaderRegistry(tmp_path)
    assert registry.available_sets() == ["real"]
    with pytest.raises(FileNotFoundError):
        registry.get("scratch")


@pytest.mark.parametrize("bad", ["../9p2i", "a/b", "/abs", "..", ".", ""])
def test_get_rejects_path_traversal_set_name(tmp_path: Path, bad: str) -> None:
    with pytest.raises(ValueError):
        SetLoaderRegistry(tmp_path).get(bad)


def test_available_sets_skips_non_parseable_seed_dir(tmp_path: Path) -> None:
    # Regression (Codex round-4 P2): a subdir whose only replay file has a
    # NON-parseable seed (replay-seed-debug.jsonl) is not a set — the loader's own
    # _replay_paths would find zero replays there — so available_sets omits it and
    # get() 404s, matching the loader's definition of a replay.
    _stamp_set(tmp_path, "4p1i")
    (tmp_path / "scratch").mkdir()
    (tmp_path / "scratch" / "replay-seed-debug.jsonl").write_text("{}\n")
    registry = SetLoaderRegistry(tmp_path)
    assert registry.available_sets() == ["4p1i"]
    with pytest.raises(FileNotFoundError):
        registry.get("scratch")


def test_available_sets_skips_parent_of_sets_container(tmp_path: Path) -> None:
    # Regression (Codex round-4 P2): a dir holding BOTH stray flat replays AND
    # per-set subdirs is a container, not a set — it must not be served as one set
    # (which would shadow the real nested sets). Here tmp_path/samples has a flat
    # replay next to a 4p1i/ subdir, so it is excluded from the parent's listing.
    container = tmp_path / "samples"
    _stamp_set(container, "4p1i")
    (container / "replay-seed-0.jsonl").write_bytes(
        (_COMMITTED_4P1I / "replay-seed-0.jsonl").read_bytes()
    )
    registry = SetLoaderRegistry(tmp_path)
    assert registry.available_sets() == []  # "samples" is a container, not a set
    with pytest.raises(FileNotFoundError):
        registry.get("samples")


def test_replay_less_subdir_is_404_on_route(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The same rule end-to-end: /replays?set=<replay-less subdir> is a 404, not an
    # empty 200, so a typo'd set name fails loud instead of masquerading as a set.
    _stamp_set(tmp_path, "real")
    (tmp_path / "scratch").mkdir()
    with _client(tmp_path, monkeypatch) as client:
        assert "scratch" not in client.get("/sets").json()["sets"]
        assert client.get("/replays", params={"set": "scratch"}).status_code == 404


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


def test_default_set_is_the_curated_9p2i_set() -> None:
    # THE DEFAULT-SET PIN (Task 19.9; audits/audit-phase-19-triage.md §7 item 10):
    # the product default is the CURATED set, not the fast 4p1i fixture. 4p1i is
    # median 12 ticks with at most one meeting per game (39/50 exactly one, 11/50
    # none) and ships no rubric; 9p2i is the set with meetings, suspicion arcs and
    # a scored highlight reel. A regression here silently re-points every
    # no-`set` deep-link at the weakest set.
    assert DEFAULT_SET == "9p2i"


def test_default_set_prefers_9p2i_else_first(tmp_path: Path) -> None:
    # With 9p2i present it is the default (the curated spectator set)...
    _stamp_set(tmp_path, "9p2i")
    _stamp_set(tmp_path, "4p1i")
    assert SetLoaderRegistry(tmp_path).default_set() == "9p2i"
    # ...without it, the first available set...
    only = tmp_path / "only"
    _stamp_set(only, "7p2i")
    assert SetLoaderRegistry(only).default_set() == "7p2i"
    # ...and the constant for an empty parent (every set request 404s there anyway).
    assert SetLoaderRegistry(tmp_path / "nope").default_set() == DEFAULT_SET


def test_omitted_set_resolves_advertised_default_on_parent_without_the_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Regression (Codex P2): on a parent that lacks DEFAULT_SET, a no-`set` request
    # must resolve the SAME default `/sets` advertises (the first set), not the
    # absent hard-coded name — so it serves rather than 404s. The advertised
    # default and the route fallback share one resolver
    # (SetLoaderRegistry.default_set).
    _stamp_set(tmp_path, "7p2i")
    with _client(tmp_path, monkeypatch) as client:
        assert client.get("/sets").json()["default"] == "7p2i"
        no_set = client.get("/replays")
        explicit = client.get("/replays", params={"set": "7p2i"})
    assert no_set.status_code == 200
    assert explicit.status_code == 200
    # The no-`set` response is the advertised default's set, not an empty 404 body.
    assert no_set.json() == explicit.json()


# ── set-parametrized serving + per-set determinism ───────────────────────────


def test_replays_is_set_parametrized(monkeypatch: pytest.MonkeyPatch) -> None:
    with _client(_PARENT, monkeypatch) as client:
        # Default (no `set`) resolves to DEFAULT_SET (9p2i); both committed sets
        # carry seeds 0..49, so both list 50 replays over their own loader.
        default = client.get("/replays")
        four = client.get("/replays", params={"set": "4p1i"})
        nine = client.get("/replays", params={"set": "9p2i"})
    assert default.status_code == 200
    assert four.status_code == 200
    assert nine.status_code == 200
    assert len(default.json()) == 50
    assert len(four.json()) == 50
    # The omitted-`set` response IS the curated default's set (Task 19.9), not the
    # 4p1i fixture's — the client's omitted-set contract comment states this.
    assert default.json() == nine.json()


def _stamped_profile(set_dir: Path) -> None:
    """The committed profile, re-stamped for ``set_dir``'s own bytes."""

    from orchestrator.recording_fingerprint import recording_fingerprint

    served = json.loads(
        (_PARENT / "9p2i" / _PROFILE_FILENAME).read_text(encoding="utf-8")
    )
    (set_dir / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}),
        encoding="utf-8",
    )
    (set_dir / "MANIFEST.md").write_text(
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "|---|---|---|---|---|---|---|\n"
        f"| {_FAST_SEED} | m | v | 2026-10-01 | 1e48c40 | 0.0 | CREWMATES |\n",
        encoding="utf-8",
    )
    (set_dir / _PROFILE_FILENAME).write_text(
        json.dumps(
            {
                **served,
                "manifest_key": "1e48c40",
                "source_fingerprint": recording_fingerprint(set_dir),
            }
        ),
        encoding="utf-8",
    )


def test_eval_game_profile_is_per_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The shown 9p2i set ships the game-shape profile; 4p1i ships none and serves
    # the empty state (404).
    with _client(_PARENT, monkeypatch) as client:
        nine = client.get("/eval/game-profile", params={"set": "9p2i"})
        four = client.get("/eval/game-profile", params={"set": "4p1i"})
    assert nine.status_code == 200
    assert nine.json()["seedset"] == "9p2i"
    assert nine.json()["stale"] is False
    assert four.status_code == 404
    # Per set: a scratch parent where only one set carries a profile serves it
    # there and the empty state beside it.
    profiled = _stamp_set(tmp_path, "profiled")
    _stamp_set(tmp_path, "bare")
    _stamped_profile(profiled)
    with _client(tmp_path, monkeypatch) as client:
        served = client.get("/eval/game-profile", params={"set": "profiled"})
        empty = client.get("/eval/game-profile", params={"set": "bare"})
    assert served.status_code == 200
    assert served.json()["stale"] is False
    assert served.json()["manifest_key"] == "1e48c40"
    assert empty.status_code == 404


def _synthetic_facts(set_dir: Path) -> dict[str, object]:
    """Gameplay facts for one synthetic game, keyed to ``set_dir``'s recordings."""

    from orchestrator.recording_fingerprint import recording_fingerprint

    return {
        "source_fingerprint": recording_fingerprint(set_dir),
        "seedset": set_dir.name,
        "git_head": "ignored-rest-stamped",
        "games": [
            {
                "seed": _FAST_SEED,
                "reason": "CREWMATE_EJECT",
                "roles": {"p-1": "IMPOSTOR", "p-2": "CREWMATE"},
                "deaths": [],
                "meetings": [
                    {
                        "ejected_player_id": "p-1",
                        "ejected_role": "IMPOSTOR",
                        "n_contradictions": 1,
                        "accusations": [{"speaker": "p-2", "accused": "p-1"}],
                        "contradictions_by_subject": {},
                    }
                ],
            }
        ],
    }


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


# ── the committed profile's provenance key + the curated featured list ───────
#
# Task 19.9. The 9p2i manifest once carried THREE distinct recording shas, so a
# scalar key resolved to None and every derived file read falsely stale. The key
# is a SET FINGERPRINT over the sorted per-seed shas when a set is mixed,
# recomputed by ``api.replay_loader._manifest_git_sha`` from the manifest's bytes.
#
# The committed profile is regenerated with ($0, offline, no provider):
#   uv run python scripts/publish_game_profile.py
# (the step scripts/refresh_samples.sh runs after a re-record of the set).


def test_committed_manifests_key_on_their_single_recording_sha() -> None:
    # The premise this test shipped under is dead: 9p2i had been refreshed
    # piecemeal, so it carried several recording shas and keyed on a `multi:`
    # fingerprint. The baseline-8 record recorded each set in ONE pass, so every
    # set now has exactly one sha and keys on it directly — the uniform branch.
    # The `multi:` branch is therefore unexercised by committed bytes and is
    # covered by the synthetic case below, which is where a mixed set must be
    # pinned once no recording produces one.
    for name in ("9p2i", "4p1i"):
        rows = _manifest_seed_shas(_PARENT / name)
        assert len({sha for _, sha in rows}) == 1, name
        sha = _manifest_git_sha(_PARENT / name)
        assert sha is not None and not sha.startswith("multi:"), name


def test_a_mixed_provenance_manifest_still_keys_on_a_multi_fingerprint(
    tmp_path: Path,
) -> None:
    # The `multi:` branch, kept alive by construction now that no committed set
    # exercises it. Two seeds recorded at different shas must not collapse to
    # either one — the fingerprint has to say "mixed" or a piecemeal refresh
    # would serve a rubric keyed to a sha half its bytes never saw.
    shutil.copytree(_PARENT / "4p1i", tmp_path / "mixed")
    manifest = tmp_path / "mixed" / "MANIFEST.md"
    text = manifest.read_text(encoding="utf-8")
    rows = _manifest_seed_shas(tmp_path / "mixed")
    original = rows[0][1]
    doctored = ("0" if original[0] != "0" else "f") + original[1:]
    # Move exactly one row's sha, leaving the rest at the recorded one.
    first_row_marker = f"| {rows[0][0]} |"
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith(first_row_marker):
            lines[index] = line.replace(original, doctored, 1)
            break
    manifest.write_text("".join(lines), encoding="utf-8")

    assert len({sha for _, sha in _manifest_seed_shas(tmp_path / "mixed")}) > 1
    mixed = _manifest_git_sha(tmp_path / "mixed")
    assert mixed is not None and mixed.startswith("multi:")


def test_the_promoted_set_ships_its_profile_on_its_own_key() -> None:
    # The served 9p2i set holds candidate round 3's bytes since 2026-10-09 and
    # ships the game-shape profile, stamped with the key the loader derives from
    # the set's own MANIFEST and the fingerprint of its recordings, so the loader
    # serves it fresh. No version-1 served file is shipped beside it. Was the
    # producer-loader agreement on the version-1 key (``_set_manifest_sha``).
    from orchestrator.recording_fingerprint import recording_fingerprint

    set_dir = _PARENT / "9p2i"
    assert not (set_dir / "results-rubric-score.json").exists()
    served = json.loads((set_dir / _PROFILE_FILENAME).read_text(encoding="utf-8"))
    manifest_sha = _manifest_git_sha(set_dir)
    assert manifest_sha == "641b4254"  # was 43b5ee45, round 2's recording sha
    assert served["manifest_key"] == manifest_sha
    assert served["source_fingerprint"] == recording_fingerprint(set_dir)
    assert served["era"] == "stage-b-r3"  # was stage-b-r2
    assert SetLoaderRegistry(_PARENT).get("9p2i").game_profile().stale is False


def _scorer_writes_no_served_file(
    scorer: Any, set_dir: Path, workdir: Path, monkeypatch: pytest.MonkeyPatch
) -> bool:
    """Run ``scorer.main`` with ``--set-dir`` and report that it refused cleanly.

    The scoring tables are stubbed: the question is only whether any code path
    still writes a version-1 served file beside the recordings.
    """

    (workdir / "experiments" / "lab").mkdir(parents=True, exist_ok=True)
    facts_path = workdir / "facts.json"
    facts_path.write_text(json.dumps(_synthetic_facts(set_dir)), encoding="utf-8")
    monkeypatch.chdir(workdir)
    monkeypatch.setattr(scorer, "score", lambda facts: [("R1", "planted", "planted")])
    monkeypatch.setattr(
        scorer,
        "geomean_validation",
        lambda facts: {
            "mean_score": 0,
            "median_score": 0,
            "validation": {
                "ranking_contested_above_stopwatch": {
                    "all_eject_decided_above_all_stopwatch": True
                }
            },
        },
    )
    monkeypatch.setattr(
        sys, "argv", ["rubric_score.py", str(facts_path), "--set-dir", str(set_dir)]
    )
    try:
        code = scorer.main()
    except SystemExit as refused:
        code = refused.code
    return (
        code not in (0, None) and not (set_dir / "results-rubric-score.json").exists()
    )


def test_version_one_writes_no_served_file_for_the_era(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    copy = tmp_path / "set" / "9p2i"
    shutil.copytree(_PARENT / "9p2i", copy)
    assert _scorer_writes_no_served_file(
        _rubric_score, copy, tmp_path / "work", monkeypatch
    )
    assert not any((tmp_path / "work" / "experiments" / "lab").iterdir())


#: The served-file write the retirement deleted from the scorer, verbatim from
#: ``experiments/lab/rubric_score.py`` at ``76270d6c`` (the producer's long
#: docstring cut to its first line), each as (a line of today's module, that
#: line with the deleted code restored beside it). The planted case rebuilds the
#: pre-retirement scorer from today's module and these lines, so it reads no git
#: history and runs on a shallow checkout.
_RETIRED_SERVED_FILE_WRITE: tuple[tuple[str, str], ...] = (
    (
        "    sys.path.insert(0, str(_REPO_ROOT))\n",
        "    sys.path.insert(0, str(_REPO_ROOT))\n"
        "\n"
        "from orchestrator.recording_fingerprint import recording_fingerprint"
        "  # noqa: E402\n"
        "\n"
        'RUBRIC_RESULTS_FILENAME = "results-rubric-score.json"\n',
    ),
    (
        "\n\ndef main() -> int:\n",
        '''

def regen_for_set(
    facts: dict[str, Any], set_dir: Path, *, git_head: str | None = None
) -> Path:
    """Re-run the scorer and co-locate ``results-rubric-score.json`` into a set."""

    source_fingerprint = facts.get("source_fingerprint")
    if source_fingerprint != recording_fingerprint(set_dir):
        raise ValueError(
            "facts do not identify the current recording bytes; re-extract them "
            "before publishing highlight scores"
        )
    head = (
        git_head
        if git_head is not None
        else (_set_manifest_sha(set_dir) or facts.get("git_head"))
    )
    out = {
        "seedset": facts.get("seedset"),
        "git_head": head,
        "source_fingerprint": source_fingerprint,
        "interestingness": interestingness(facts),
    }
    dest = Path(set_dir) / RUBRIC_RESULTS_FILENAME
    dest.write_text(json.dumps(out, indent=2))
    return dest


def main() -> int:
''',
    ),
    (
        '    parser.add_argument("facts_json", help="gameplay-facts extractor output")\n',
        '    parser.add_argument("facts_json", help="gameplay-facts extractor output")\n'
        "    parser.add_argument(\n"
        '        "--set-dir",\n'
        "        default=None,\n"
        "        help=(\n"
        '            "also co-locate results-rubric-score.json into this served replay "\n'
        '            "set dir, stamped with git HEAD (the per-set regen producer for "\n'
        '            "/eval/rubric)"\n'
        "        ),\n"
        "    )\n",
    ),
    (
        "    set_dir = Path(sample_dir) if sample_dir else None\n",
        "    set_dir = (\n"
        "        Path(args.set_dir)\n"
        "        if args.set_dir is not None\n"
        "        else (Path(sample_dir) if sample_dir else None)\n"
        "    )\n",
    ),
    (
        "        f\"{rank['all_eject_decided_above_all_stopwatch']})\"\n"
        "    )\n"
        "    return 0\n",
        "        f\"{rank['all_eject_decided_above_all_stopwatch']})\"\n"
        "    )\n"
        "\n"
        "    if args.set_dir is not None:\n"
        "        dest = regen_for_set(facts, Path(args.set_dir))\n"
        '        print(f"co-located per-set rubric (git_head stamped): {dest}")\n'
        "    return 0\n",
    ),
)


def _pre_retirement_scorer_source() -> str:
    """Today's scorer with the deleted served-file write restored, as text."""

    source = Path(_rubric_score.__file__).read_text(encoding="utf-8")
    for today, restored in _RETIRED_SERVED_FILE_WRITE:
        assert source.count(today) == 1, today
        source = source.replace(today, restored)
    return source


def test_the_scorer_before_the_retirement_wrote_one_and_fails_the_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: the scorer as it stood at ``76270d6c``, rebuilt without git history.

    Today's module with the retired ``regen_for_set`` and ``--set-dir`` restored
    writes the served file, so the check that today's scorer passes fails on it.
    """

    source = _pre_retirement_scorer_source()
    assert "def regen_for_set(" in source and '"--set-dir"' in source
    path = tmp_path / "rubric_score_pre_retirement.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None and spec.loader is not None
    old = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, path.stem, old)
    spec.loader.exec_module(old)
    copy = tmp_path / "set" / "9p2i"
    shutil.copytree(_PARENT / "9p2i", copy)
    assert not _scorer_writes_no_served_file(old, copy, tmp_path / "work", monkeypatch)
    assert (copy / "results-rubric-score.json").exists()


def test_featured_labels_are_spoiler_free() -> None:
    # Review fix (PR #324, P1): the featured strip renders BEFORE any game is
    # opened, and a static blurb is prose — 19.10's unspoiled-mode reveal gate
    # covers outcome-derived DATA, and 19.10's contract forbids copy changes in
    # ReplayPicker.tsx, so nothing downstream can retract a spoiler written here.
    # The labels name the setup and the question, never the answer. This guards
    # the rule stated above FEATURED_GAMES against a future well-meaning edit.
    banned = (
        "wins",
        "won",
        "victory",
        "ejects",
        "ejected",
        "is the impostor",
        "their own killer",
        "7–1",
        "5–0",
        "crew win",
        "impostor win",
    )
    labels = _FEATURED_LABEL.findall(_featured_block())
    assert len(labels) == len(_parse_featured_games())
    for label in labels:
        lowered = label.lower()
        for token in banned:
            assert token not in lowered, f"outcome spoiler {token!r} in: {label}"


_PLAYER_ID = re.compile(r"\bp-\d+\b")
_VOTE_OR_ENDING = re.compile(
    r"\b(?:votes?|voted|tally|unanimous|skip(?:s|ped)?|eject\w*)\b", re.IGNORECASE
)


def _assert_label_shape(label: str) -> None:
    """A 9p2i card's shape: one question, and no player, vote or ending named."""

    assert label.count("?") == 1, ("one question", label)
    assert _PLAYER_ID.search(label) is None, ("names a player", label)
    assert _VOTE_OR_ENDING.search(label) is None, ("names a vote or ending", label)


def test_each_9p2i_label_poses_one_question_and_names_no_player_or_vote() -> None:
    # The strip renders before a game opens, so a card may count what a viewer
    # will see and ask one question about it, and may not say who, which vote
    # or how it ends. The 4p1i cards predate the question rule and are kept.
    pairs = zip(_parse_featured_games(), _FEATURED_LABEL.findall(_featured_block()))
    nine = [label for (set_name, _), label in pairs if set_name == "9p2i"]
    assert len(nine) == 2
    for label in nine:
        _assert_label_shape(label)
    for planted, why in (
        ("Three meetings. Who saw what? Who said so?", "one question"),
        ("Three meetings, and p-6 is accused. Who saw what?", "names a player"),
        ("Three meetings. Which way does the vote go?", "names a vote"),
        ("Three meetings, and nobody is ejected. Why not?", "names a vote"),
    ):
        with pytest.raises(AssertionError, match=why):
            _assert_label_shape(planted)


def test_set_fingerprints_compare_by_exact_equality() -> None:
    # Review fix (PR #324, P2): a fingerprint is a fixed-width digest, not a
    # truncatable sha, so it must NOT ride the bidirectional prefix comparison —
    # a shortened or hand-edited stamp would otherwise prefix-match the real key
    # and silently suppress the honesty banner on an artifact with no valid
    # provenance. Malformed on either side → stale (the fail-safe direction).
    real = _manifest_git_sha(_PARENT / "9p2i")
    assert real is not None
    assert _provenance_is_stale(real, real) is False

    # The malformed variants are built from a SYNTHETIC well-formed fingerprint,
    # not from whatever the committed set happens to carry. Deriving them from
    # `real` silently lost its teeth the moment the baseline-8 record gave every
    # set a single recording sha: `real` became a bare 8-character sha, so
    # truncating it to 11 characters returned the string itself and the
    # "truncated digest" case compared a value against itself.
    fingerprint = "multi:0123456789ab"
    assert _provenance_is_stale(fingerprint, fingerprint) is False
    for malformed in (
        "multi:",  # prefix only
        fingerprint[: len("multi:") + 5],  # truncated digest
        fingerprint.upper(),  # non-lowercase hex
        fingerprint + "ab",  # over-long
        "multi:zzzzzzzzzzzz",  # non-hex
    ):
        assert _provenance_is_stale(malformed, fingerprint) is True, malformed
        assert _provenance_is_stale(fingerprint, malformed) is True, malformed
        # ...and malformed against the real committed key, in both directions.
        assert _provenance_is_stale(malformed, real) is True, malformed
        assert _provenance_is_stale(real, malformed) is True, malformed
    # A different well-formed fingerprint is stale too (the point of the key).
    assert _provenance_is_stale("multi:000000000000", fingerprint) is True
    assert _provenance_is_stale("multi:000000000000", real) is True
    # A bare git sha keeps the prefix comparison: the manifest stores a SHORT sha
    # and a rubric may carry the full HEAD.
    assert _provenance_is_stale("1e48c40deadbeef", "1e48c40") is False
    # ...and a sha never matches a fingerprint in either direction.
    assert _provenance_is_stale("1e48c40", real) is True


def _assert_opens_on_role_proof(
    registry: SetLoaderRegistry, set_name: str, seed: int
) -> None:
    """The featured-head criterion, asserted against the SERVED replay.

    A tour opener has to show a table that established something, so the head's
    FIRST meeting — the one the viewer's auto-follow opens — must eject a player
    who carries a ``role_proof`` flag naming them in that same meeting.
    ``role_proof`` is the derived category for a grounded vent sighting; the
    other categories are two accounts that cannot both be true, which the alibi
    envelope manufactures against honest movers, so "any flag" is the wrong band
    to open a demo on.

    Deliberately re-implemented rather than imported from
    ``scripts/measure_featured_criterion.py``: the script MEASURES the bands over
    every committed game and this PINS the one game the strip leads with, and two
    independent readings of the same bytes is the point — the same discipline the
    evidence taxonomy's API-side and eval-side twins follow.
    """

    replay = registry.get(set_name).load_replay(f"headless-seed-{seed}")
    first = replay.meetings[0]
    assert first.outcome == "EJECTED", (set_name, seed, first.outcome)
    ejected = first.ejected_player_id
    assert ejected is not None, (set_name, seed)
    assert any(
        flag.category == "role_proof" and ejected in flag.subjects
        for flag in first.contradictions
    ), (
        set_name,
        seed,
        [(f.kind, f.category, f.subjects) for f in first.contradictions],
    )
    roles = {player.agent_id: player.role for player in replay.players}
    assert roles[ejected] == "IMPOSTOR", (set_name, seed, ejected, roles[ejected])


def _assert_non_vent_opener(
    registry: SetLoaderRegistry, set_name: str, seed: int
) -> None:
    """The second 9p2i card's criterion, asserted against the SERVED replay.

    The game's FIRST meeting ejects an impostor, no meeting in the game raises a
    flag of any kind, and no vent event happens at or before that meeting's
    tick: the table decided without a vent sighting or a flagged contradiction
    in front of it. The role read describes the strip and gates nothing else.

    Re-implemented rather than imported from
    ``scripts/measure_featured_criterion.py`` (its
    ``opens_on_non_vent_impostor_ejection``), for the reason
    :func:`_assert_opens_on_role_proof` gives. The clauses run in this order and
    each names itself in its message, so a planted case can say which one it
    isolates.
    """

    replay = registry.get(set_name).load_replay(f"headless-seed-{seed}")
    first = replay.meetings[0]
    assert first.outcome == "EJECTED", (set_name, seed, first.outcome)
    ejected = first.ejected_player_id
    assert ejected is not None, (set_name, seed)
    roles = {player.agent_id: player.role for player in replay.players}
    assert roles[ejected] == "IMPOSTOR", (set_name, seed, ejected, roles[ejected])
    flagged = [
        (meeting.meeting_id, len(meeting.contradictions))
        for meeting in replay.meetings
        if meeting.contradictions
    ]
    assert not flagged, (set_name, seed, "flags", flagged)
    vents = [
        (event.tick, event.phase)
        for frame in replay.ticks
        for event in frame.events
        if event.type == "vent" and event.tick <= first.tick
    ]
    assert not vents, (set_name, seed, "vent at or before the first meeting", vents)


def test_featured_seeds_exist_in_their_committed_sets() -> None:
    # The curated featured list is committed DATA (frontend/src/components/
    # ReplayPicker.tsx: FEATURED_GAMES) — the audits' named good tail, each with a
    # hand-written why-watch line. Its one drift risk is a seed the served set does
    # not carry, which would render as a dead entry; pin that here.
    #
    # WHICH games are featured stays editorial. The ORDER's head no longer is: it
    # is a measured property of the recordings, so this pins the CRITERION and not
    # merely a seed — when the next re-record replaces the bytes, a head that
    # stopped satisfying it fails here instead of shipping a tour that opens on a
    # table which established nothing. Reproduce the bands the criterion selects
    # from with `uv run python scripts/measure_featured_criterion.py`.
    featured = _parse_featured_games()
    assert {game[0] for game in featured} == {"4p1i", "9p2i"}
    # On the recordings the set holds since 2026-10-09, eleven of fifty 9p2i
    # games open on a role-proof ejection and five open on an impostor ejection
    # with no vent evidence about (`scripts/measure_featured_criterion.py
    # --list`; on round 2's bytes eleven and two). The head is seed 19 of the
    # first list and the second card seed 14 of the second, as on round 2's
    # bytes, re-picked by the criterion and the reasons below. The holding strip
    # featured 9p2i {3}; the baseline-9 bytes {23, 0, 29, 2}; baseline 8 {2,
    # 13, 23, 46}.
    assert featured[0] == ("9p2i", 19)  # the tour's landing game (the curated head)
    nine = [seed for set_name, seed in featured if set_name == "9p2i"]
    assert nine == [19, 14]
    assert {seed for set_name, seed in featured if set_name == "4p1i"} == {2, 11, 29}
    registry = SetLoaderRegistry(_PARENT)
    for set_name, seed in featured:
        loader = registry.get(set_name)
        assert any(meta.seed == seed for meta in loader.list_replays())
    # EVERY set's head carries the criterion, not just the strip's first entry.
    # The picker shows a row per set and the tour opens the head of the set it
    # targets, so a 4p1i opener that established nothing would ship unnoticed
    # behind a grounded 9p2i one — which is exactly what a round-1 verifier
    # demonstrated by swapping the 4p1i entries while this pin stayed green.
    heads = _featured_heads()
    assert {set_name for set_name, _ in heads} == {set_name for set_name, _ in featured}
    assert heads[0] == featured[0]
    for set_name, seed in heads:
        _assert_opens_on_role_proof(registry, set_name, seed)
    # The 9p2i second card carries its own measured kind: an impostor ejected
    # in the first meeting with no flag anywhere and no vent at or before it.
    _assert_non_vent_opener(registry, "9p2i", nine[1])


def _wrong_shelf_problems(
    featured: list[tuple[str, int]], served: dict[str, Any]
) -> list[str]:
    """Each featured 9p2i seed the served profile puts on the wrong shelf.

    "Decided without proof: wrong on what it held" is a reveal-only shelf: a
    wrong-but-believable ejection. The strip renders before any game opens, so
    no featured game may be one of its members.
    """

    wrong = served["reveal"]["decided_without_proof"]["wrong"]
    assert wrong["name"] == "decided_without_proof_wrong"
    members = {member["seed"] for member in wrong["members"]}
    return [
        f"9p2i seed {seed} is on the wrong shelf"
        for set_name, seed in featured
        if set_name == "9p2i" and seed in members
    ]


def test_no_featured_game_is_a_wrong_but_believable_ejection() -> None:
    """The strip holds no member of the served profile's wrong shelf.

    Planted: a strip naming one of the shelf's members fails, naming it.
    """

    served = json.loads(
        (_PARENT / "9p2i" / _PROFILE_FILENAME).read_text(encoding="utf-8")
    )
    featured = _parse_featured_games()
    assert [seed for set_name, seed in featured if set_name == "9p2i"]
    assert _wrong_shelf_problems(featured, served) == []
    member = served["reveal"]["decided_without_proof"]["wrong"]["members"][0]["seed"]
    planted = [*featured, ("9p2i", member)]
    assert _wrong_shelf_problems(planted, served) == [
        f"9p2i seed {member} is on the wrong shelf"
    ]


def _vent_trips_before_the_first_meeting(
    replay: ReplayView,
) -> list[tuple[str, int, int | None]]:
    """Each impostor's vent trip up to the first meeting: (actor, entered, exited).

    ``exited`` is ``None`` for a trip still open when the meeting is called, which
    that meeting's return to the meeting room closes.
    """

    first = replay.meetings[0].tick
    trips: list[tuple[str, int, int | None]] = []
    open_trips: dict[str, int] = {}
    for frame in replay.ticks:
        for event in frame.events:
            if event.type != "vent" or event.tick > first:
                continue
            if event.phase == "enter":
                open_trips[event.actor_id] = event.tick
            elif event.actor_id in open_trips:
                trips.append(
                    (event.actor_id, open_trips.pop(event.actor_id), event.tick)
                )
    trips.extend((actor, entered, None) for actor, entered in open_trips.items())
    return trips


def _shows_both_vent_behaviours(replay: ReplayView) -> bool:
    """A stay of three ticks or more inside a vent, and a dive the meeting closes."""

    trips = _vent_trips_before_the_first_meeting(replay)
    stays = any(
        exited is not None and exited - entered >= 3 for _, entered, exited in trips
    )
    return stays and any(exited is None for _, _, exited in trips)


def _second_voice_sighting(replay: ReplayView) -> bool:
    """The first meeting's vent sighting comes from a player other than its caller.

    That player's turn describes the ejected player using a vent, its own
    ballot rests on that observation, and another voter's ballot cites its turn.
    """

    first = replay.meetings[0]
    ejected = first.ejected_player_id
    for turn in first.turns:
        if turn.speaker == first.triggered_by or not any(
            item.type == "saw_vent" and item.subject == ejected
            for item in turn.observations
        ):
            continue
        own = any(
            ballot.voter == turn.speaker
            and ballot.target == ejected
            and ballot.primary_reason_observation_id is not None
            for ballot in first.ballots
        )
        cited = any(
            ballot.voter != turn.speaker
            and ballot.target == ejected
            and ballot.primary_reason_id == turn.turn_id
            for ballot in first.ballots
        )
        if own and cited:
            return True
    return False


def test_the_head_is_the_one_eligible_game_its_stated_reasons_pick() -> None:
    """The strip comment's reasons, measured on the served bytes.

    Of the eleven games whose first meeting ejects on a role-proof flag, three
    show both vent behaviours the map draws before that meeting (6, 19 and 20),
    and of those only seed 19's sighting is a second voice: a player other than
    the body's reporter describes the vent use, its ballot rests on it and other
    ballots cite its turn, which is the supported case's shape on the landing
    game. Planted: the head moved to seed 20 reads the same first filter and
    fails the second.
    """

    loader = SetLoaderRegistry(_PARENT).get("9p2i")
    eligible = []
    for seed in range(50):
        try:
            _assert_opens_on_role_proof(SetLoaderRegistry(_PARENT), "9p2i", seed)
        except AssertionError:
            continue
        eligible.append(seed)
    assert eligible == [3, 5, 6, 7, 10, 11, 19, 20, 27, 42, 49]
    replays = {seed: loader.load_replay(f"headless-seed-{seed}") for seed in eligible}
    both = [seed for seed in eligible if _shows_both_vent_behaviours(replays[seed])]
    assert both == [6, 19, 20]
    picked = [seed for seed in both if _second_voice_sighting(replays[seed])]
    assert picked == [_featured_heads()[0][1]] == [19]
    assert _shows_both_vent_behaviours(replays[20])
    assert not _second_voice_sighting(replays[20])


@pytest.mark.parametrize(
    "set_name,seed,why,message",
    [
        ("9p2i", 4, "no ejection anywhere in the game", "SKIPPED"),
        ("9p2i", 36, "no ejection anywhere in the game", "SKIPPED"),
        ("9p2i", 32, "the first meeting skips", "SKIPPED"),
        (
            "9p2i",
            0,
            "the first meeting skips, though a later one ejects on role proof",
            "SKIPPED",
        ),
        (
            "9p2i",
            8,
            "the first meeting ejects an IMPOSTOR on no flag at all",
            r"'9p2i', 8, \[\]",
        ),
        (
            "9p2i",
            25,
            "the first meeting ejects a CREWMATE on no flag at all",
            r"'9p2i', 25, \[\]",
        ),
        (
            "9p2i",
            23,
            "the baseline-9 head: its first meeting ejects a CREWMATE on no flag",
            r"'9p2i', 23, \[\]",
        ),
        (
            "9p2i",
            14,
            "the strip's second card: an IMPOSTOR ejected on no flag at all",
            r"'9p2i', 14, \[\]",
        ),
        (
            "9p2i",
            1,
            "the first meeting ejects a CREWMATE while weak flags name others",
            r"'9p2i', 1, \[\('alibi_vs_sighting', 'weak_signal', \('p-1',\)\)",
        ),
        (
            "9p2i",
            12,
            "the first meeting ejects a CREWMATE that a weak flag names",
            r"'9p2i', 12, \[\('alibi_vs_sighting', 'weak_signal', \('p-2',\)\)\]",
        ),
        ("4p1i", 29, "the one meeting skips: no ejection anywhere", "SKIPPED"),
        (
            "4p1i",
            11,
            "the first meeting ejects an impostor on no flag at all",
            r"'4p1i', 11, \[\]",
        ),
    ],
)
def test_featured_head_criterion_rejects_a_head_that_establishes_nothing(
    set_name: str, seed: int, why: str, message: str
) -> None:
    # THE PLANTED CASES for the pin above. A criterion nobody can fail is a
    # sentence, not a gate, so each of these is a real committed game that the
    # criterion must reject, named with the reason it fails and with the
    # assertion message it must fail through — ``match=`` so a case that started
    # failing for a DIFFERENT reason (a skipping meeting, say) stops counting as
    # proof of the clause it was chosen for.
    #
    # BOTH SETS are represented, because the pin above now applies the criterion
    # to each set's head: 4p1i seed 29 (the strip's own third 4p1i entry) skips
    # its one meeting and seed 11 ejects an impostor on no flag, so promoting
    # either to the 4p1i head turns this red. Measured, every flag recorded
    # anywhere in `replays/samples/4p1i` is a role-proof vent sighting, so no
    # 4p1i game can isolate the category clause.
    #
    # No 9p2i game isolates it either on the recordings the set holds since
    # 2026-10-09 (no first meeting ejects an impostor that only a
    # non-role-proof flag names), so the clause rests on the planted case below,
    # `test_the_role_proof_clause_rejects_a_recategorised_head`: the head's own
    # served first meeting with its role-proof flag recategorised.
    #
    # The rest bracket it. 8 and 14 (the strip's own second card) eject an
    # IMPOSTOR in their first meeting on no flag at all, so a pin checking only
    # "the head ejects" or "the head ejects correctly" would wave them through;
    # 25 and 23 (the baseline-9 head) eject a CREWMATE on no flag; 1 ejects a
    # CREWMATE while weak flags name others, and 12 a CREWMATE that a weak flag
    # names; 0 establishes something only in a LATER meeting, which the tour's
    # auto-follow does not open first; 32 skips its first meeting and 4 and 36
    # eject nobody at all.
    # (Re-derived on the promoted bytes, 2026-10-09; round 2's cases were 1, 12,
    # 17 and 2 where these read 32, 25, 1 and 12, and no first meeting on round
    # 3's bytes ejects anyone a cross-statement flag names. The baseline-9 cases
    # were 2, 10, 46, 36, 44, 12, 13 and 7.)
    registry = SetLoaderRegistry(_PARENT)
    with pytest.raises(AssertionError, match=message):
        _assert_opens_on_role_proof(registry, set_name, seed)


class _PlantedLoader:
    """One served replay, standing in for a set's loader."""

    def __init__(self, replay: ReplayView) -> None:
        self._replay = replay

    def load_replay(self, _game_id: str) -> ReplayView:
        return self._replay


class _PlantedRegistry:
    """A registry whose every set serves the one planted replay."""

    def __init__(self, replay: ReplayView) -> None:
        self._replay = replay

    def get(self, _set_name: str) -> _PlantedLoader:
        return _PlantedLoader(self._replay)


def test_the_role_proof_clause_rejects_a_recategorised_head() -> None:
    # The planted case the category clause rests on. Take the head's served
    # replay and recategorise its first meeting's role-proof flags as
    # cross-statement, changing nothing else: the meeting still ejects the same
    # impostor and the flags still name them, so the category comparison is the
    # only clause left that can reject it. The head itself passes, so the
    # rejection is the recategorisation's; and the weakened predicate (any flag
    # naming the ejected player) accepts the perturbed replay, which is what
    # shows the perturbation isolates the category clause and nothing else.
    registry = SetLoaderRegistry(_PARENT)
    head = _featured_heads()[0]
    assert head == ("9p2i", 19)
    _assert_opens_on_role_proof(registry, *head)

    replay = registry.get(head[0]).load_replay(f"headless-seed-{head[1]}")
    first = replay.meetings[0]
    ejected = first.ejected_player_id
    assert ejected is not None
    assert any(
        flag.category == "role_proof" and ejected in flag.subjects
        for flag in first.contradictions
    )
    recategorised = first.model_copy(
        update={
            "contradictions": tuple(
                flag.model_copy(update={"category": "cross_statement"})
                if flag.category == "role_proof"
                else flag
                for flag in first.contradictions
            )
        }
    )
    planted = replay.model_copy(
        update={"meetings": (recategorised, *replay.meetings[1:])}
    )

    def weakened(candidate: ReplayView) -> None:
        """The criterion with its category clause dropped: any flag naming them."""

        opening = candidate.meetings[0]
        assert opening.outcome == "EJECTED"
        named = opening.ejected_player_id
        assert named is not None
        assert any(named in flag.subjects for flag in opening.contradictions)
        roles = {player.agent_id: player.role for player in candidate.players}
        assert roles[named] == "IMPOSTOR"

    weakened(planted)
    with pytest.raises(AssertionError, match="cross_statement"):
        _assert_opens_on_role_proof(_PlantedRegistry(planted), *head)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "seed,why,message",
    [
        (16, "an impostor ejected, no flag anywhere, a vent trip before", "vent at"),
        (21, "an impostor ejected, a flag raised in a later meeting", "'flags'"),
        (9, "an impostor ejected, no vent before, a later flag", "'flags'"),
        (19, "the head: its first meeting carries role proof", "'flags'"),
        (23, "the first meeting ejects a CREWMATE", "CREWMATE"),
        (0, "the first meeting skips", "SKIPPED"),
    ],
)
def test_the_non_vent_criterion_rejects_a_card_with_vent_evidence(
    seed: int, why: str, message: str
) -> None:
    # THE PLANTED CASES for the second card's criterion, each a committed game
    # it must reject through the clause named. 16 isolates the vent clause
    # (nothing else fails); 9 isolates the flag clause (no vent before its
    # first meeting); 21 is the card's named case for a later flag; 19 shows the
    # head itself could not be this card; 23 and 0 fail earlier clauses. No
    # committed game ejects a crewmate with no flag anywhere and no vent before,
    # so the role clause rests on the perturbation in the next test.
    # (Re-derived on the promoted bytes, 2026-10-09; round 2's cases were 24, 8
    # and 34, whose first meetings now skip or meet a vent first.)
    registry = SetLoaderRegistry(_PARENT)
    with pytest.raises(AssertionError, match=message):
        _assert_non_vent_opener(registry, "9p2i", seed)


def test_the_non_vent_criterion_reads_the_role_and_the_vent_tick() -> None:
    # Seed 14 with its ejected impostor read as a crewmate fails the role
    # clause; seed 44 with its one vent trip moved onto the meeting's own tick
    # fails the vent clause, and moved to the tick after still passes.
    registry = SetLoaderRegistry(_PARENT)
    card = registry.get("9p2i").load_replay("headless-seed-14")
    ejected = card.meetings[0].ejected_player_id
    flipped = card.model_copy(
        update={
            "players": tuple(
                p.model_copy(update={"role": "CREWMATE"})
                if p.agent_id == ejected
                else p
                for p in card.players
            )
        }
    )
    _assert_non_vent_opener(_PlantedRegistry(card), "9p2i", 14)  # type: ignore[arg-type]
    with pytest.raises(AssertionError, match="CREWMATE"):
        _assert_non_vent_opener(_PlantedRegistry(flipped), "9p2i", 14)  # type: ignore[arg-type]

    other = registry.get("9p2i").load_replay("headless-seed-44")
    opened = other.meetings[0].tick

    def vent_moved_to(tick: int) -> ReplayView:
        event = next(
            e for frame in other.ticks for e in frame.events if e.type == "vent"
        )
        assert event.tick > opened
        moved = event.model_copy(update={"tick": tick})
        return other.model_copy(
            update={
                "ticks": tuple(
                    frame.model_copy(
                        update={
                            "events": tuple(e for e in frame.events if e is not event)
                            + ((moved,) if frame.tick == tick else ())
                        }
                    )
                    for frame in other.ticks
                )
            }
        )

    _assert_non_vent_opener(_PlantedRegistry(vent_moved_to(opened + 1)), "9p2i", 44)  # type: ignore[arg-type]
    with pytest.raises(AssertionError, match="vent at"):
        _assert_non_vent_opener(_PlantedRegistry(vent_moved_to(opened)), "9p2i", 44)  # type: ignore[arg-type]


def test_determinism_holds_per_set(monkeypatch: pytest.MonkeyPatch) -> None:
    # The determinism gate runs PER SET (Task 12.12 DoD): each committed set
    # reconstructs byte-identically through its own per-set loader. A divergence
    # raises ReplayStateMismatchError inside load_replay.
    #
    # The committed sets were re-recorded (Task 14.12 baseline 2) with all four
    # Phase-13.5 levers ON (unconditional since Task 14.9) plus the Task-14.10
    # evidence_quality_lift lever ON. That lever is still default-OFF, so
    # flag-aware reconstruction of the committed sets requires it exported.
    monkeypatch.setenv("AILIBI_EVIDENCE_QUALITY_LIFT", "1")
    registry = SetLoaderRegistry(_PARENT)
    for set_name in registry.available_sets():
        loader = registry.get(set_name)
        replay = loader.load_replay(f"headless-seed-{_FAST_SEED}")
        assert replay.metadata.game_id == f"headless-seed-{_FAST_SEED}"


# The flag claims a label may make, each bound to the flags it promises: a
# reported vent sighting, a meeting whose flags are ALL weak signals, and a
# meeting whose flags are ALL contradictions (the viewer's own group headings).
_FLAG_CLAIMS: dict[str, str] = {
    r"\bvent\b": "vent",
    r"only flags are weak signals": "weak_signal",
    r"flags are contradictions": "cross_statement",
}


def _flag_claim_holds(claim: str, replay: ReplayView) -> bool:
    if claim == "vent":
        return any(
            flag.kind == "vent_sighting"
            for meeting in replay.meetings
            for flag in meeting.contradictions
        )
    return any(
        meeting.contradictions
        and all(flag.category == claim for flag in meeting.contradictions)
        for meeting in replay.meetings
    )


def _assert_featured_counts(label: str, replay: ReplayView) -> None:
    """Check the bounded count vocabulary used by these editorial labels.

    The vocabulary grows word by word with the strip: a count word no label
    uses is not here, so a label reaching for a new number fails until its
    word is added and checked.
    """
    words = {
        "one": 1,
        "three": 3,
        "four": 4,
        "eight": 8,
        "nineteen": 19,
        "twenty-three": 23,
    }
    number = "|".join(sorted(words, key=len, reverse=True))
    text = label.lower()
    meeting = re.search(rf"\b({number}) (?:short )?meetings?\b", text)
    turns = re.search(rf"\b({number}) (?:spoken )?turns\b", text)
    assert meeting is not None or turns is not None
    if meeting is not None:
        assert len(replay.meetings) == words[meeting.group(1)], ("meetings", label)
    if turns is not None:
        spoken = sum(len(item.turns) for item in replay.meetings)
        assert spoken == words[turns.group(1)], ("turns", label)
    if "no flagged contradictions" in text:
        flagged = [item.meeting_id for item in replay.meetings if item.contradictions]
        assert not flagged, ("no flagged contradictions", flagged)
    for pattern, claim in _FLAG_CLAIMS.items():
        if re.search(pattern, text):
            assert _flag_claim_holds(claim, replay), (claim, label)


def _without_flags(replay: ReplayView, claim: str) -> ReplayView:
    """The served replay with every flag the named claim rests on removed."""

    def keep(kind: str, category: str) -> bool:
        return kind != "vent_sighting" if claim == "vent" else category != claim

    return replay.model_copy(
        update={
            "meetings": tuple(
                meeting.model_copy(
                    update={
                        "contradictions": tuple(
                            flag
                            for flag in meeting.contradictions
                            if keep(flag.kind, flag.category)
                        )
                    }
                )
                for meeting in replay.meetings
            )
        }
    )


_LABELLED_PAIRS: tuple[tuple[str, int], ...] = (
    ("9p2i", 19),
    ("9p2i", 14),
    ("4p1i", 2),
    ("4p1i", 11),
    ("4p1i", 29),
)


def test_every_featured_label_is_checked() -> None:
    # The parametrize below is the strip, in order: a card added or re-pointed
    # without its label check fails here rather than shipping unchecked.
    assert tuple(_parse_featured_games()) == _LABELLED_PAIRS


@pytest.mark.parametrize("set_name,seed", _LABELLED_PAIRS)
def test_current_featured_claims_match_source_and_gate_bites(
    set_name: str, seed: int
) -> None:
    label = next(
        label
        for pair, label in zip(
            _parse_featured_games(), _FEATURED_LABEL.findall(_featured_block())
        )
        if pair == (set_name, seed)
    )
    replay = (
        SetLoaderRegistry(_PARENT).get(set_name).load_replay(f"headless-seed-{seed}")
    )
    _assert_featured_counts(label, replay)
    with pytest.raises(AssertionError):
        _assert_featured_counts(label, replay.model_copy(update={"meetings": ()}))
    # A turn count bites on its own: one turn fewer, every meeting kept.
    if re.search(r"\bturns\b", label.lower()):
        last = replay.meetings[-1]
        fewer = replay.model_copy(
            update={
                "meetings": (
                    *replay.meetings[:-1],
                    last.model_copy(update={"turns": last.turns[:-1]}),
                )
            }
        )
        with pytest.raises(AssertionError, match="turns"):
            _assert_featured_counts(label, fewer)
    # Each flag claim the label makes bites on its own: strip only the flags that
    # claim rests on, leave every meeting, turn and other flag in place, and the
    # same label must fail.
    for pattern, claim in _FLAG_CLAIMS.items():
        if re.search(pattern, label.lower()):
            with pytest.raises(AssertionError, match=claim):
                _assert_featured_counts(label, _without_flags(replay, claim))
    # The no-flags promise bites the other way: one flag planted in the first
    # meeting, copied from the featured head's first meeting, which carries one
    # by its criterion (was 9p2i seed 2's, which raises none on round 3's bytes).
    if "no flagged contradictions" in label.lower():
        head_set, head_seed = _featured_heads()[0]
        flag = (
            SetLoaderRegistry(_PARENT)
            .get(head_set)
            .load_replay(f"headless-seed-{head_seed}")
            .meetings[0]
            .contradictions[0]
        )
        first = replay.meetings[0]
        planted = replay.model_copy(
            update={
                "meetings": (
                    first.model_copy(update={"contradictions": (flag,)}),
                    *replay.meetings[1:],
                )
            }
        )
        with pytest.raises(AssertionError, match="no flagged contradictions"):
            _assert_featured_counts(label, planted)
    for claim in (
        "no evidence at all",
        "everything the crew will ever know",
        "engine flagged",
        "most-argued",
    ):
        assert claim not in label
