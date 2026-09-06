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
(not the 4p1i fixture), the rubric's provenance key agrees between producer and
loader on the committed mixed-provenance manifest, and every hand-curated featured
seed exists in the set it names.
"""

from __future__ import annotations

import importlib
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
    _rubric_is_stale,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PARENT = _REPO_ROOT / "replays" / "samples"
_COMMITTED_4P1I = _PARENT / "4p1i"
# A small, fast committed 4p1i seed used to stamp fake set subdirs in tmp dirs.
_FAST_SEED = 0

# The rubric regen producer is a top-level lab module (experiments/lab is not on
# mypy_path); import it dynamically so mypy does not try to resolve it by name —
# the same pattern tests/api/test_view_model.py uses.
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


def test_eval_rubric_is_per_set(monkeypatch: pytest.MonkeyPatch) -> None:
    with _client(_PARENT, monkeypatch) as client:
        # 9p2i ships a rubric; the flat 4p1i fixture ships none (404 → empty state).
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


# ── the committed rubric's provenance key + the curated featured list ────────
#
# Task 19.9. The 9p2i manifest carries THREE distinct recording shas, so the old
# scalar key resolved to None on BOTH sides and the picker's staleness banner was
# unconditionally, falsely "stale" — no re-score could clear it. The key is now a
# SET FINGERPRINT over the sorted per-seed shas, produced by
# ``experiments.lab.rubric_score._set_manifest_sha`` and recomputed by
# ``api.replay_loader._manifest_git_sha`` from the same bytes.
#
# The committed rubric was regenerated at HEAD with ($0, offline, no provider):
#   PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py \
#     >/dev/null \
#     && uv run python experiments/lab/rubric_score.py \
#       "${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json" \
#       --set-dir replays/samples/9p2i
# (the same pair scripts/refresh_samples.sh runs after a re-record).


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


def test_the_served_rubric_reads_stale_against_the_rerecorded_manifest() -> None:
    # THE PROBE PIN, and at this HEAD it pins the STALE side deliberately.
    #
    # The baseline-8 record re-recorded 9p2i, but its rubric could NOT be
    # regenerated: one of the gameplay-facts extractor's self-checks fails on
    # these bytes (the extractor's genuine-class re-derivation disagrees with
    # eval.vote_correctness by one supplied row), and the lab scorer floors EVERY
    # game's score to zero on any self-check FAIL. A geomean of 0.0 that
    # eval.watchability reads at 48.57 is a scorer artifact, not a measurement,
    # so it was NOT shipped: the rubric artifacts stay at their previous content
    # and the served rubric is therefore STALE against the new manifest.
    #
    # That is the honest state and the banner exists to show it. This test pins
    # it so the staleness cannot pass unnoticed, and so the day the extractor is
    # reconciled and the rubric regenerated, THIS test fails and has to be moved
    # back to the fresh side on purpose.
    set_dir = _PARENT / "9p2i"
    manifest_sha = _manifest_git_sha(set_dir)

    # The producer's own recomputation still tracks the manifest exactly — the
    # mechanism is intact; it is the artifact that is behind.
    assert _rubric_score._set_manifest_sha(set_dir) == manifest_sha

    view = SetLoaderRegistry(_PARENT).get("9p2i").rubric()
    assert view.manifest_sha == manifest_sha
    assert view.git_head != manifest_sha
    assert view.stale is True


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


def test_set_fingerprints_compare_by_exact_equality() -> None:
    # Review fix (PR #324, P2): a fingerprint is a fixed-width digest, not a
    # truncatable sha, so it must NOT ride the bidirectional prefix comparison —
    # a shortened or hand-edited stamp would otherwise prefix-match the real key
    # and silently suppress the honesty banner on an artifact with no valid
    # provenance. Malformed on either side → stale (the fail-safe direction).
    real = _manifest_git_sha(_PARENT / "9p2i")
    assert real is not None
    assert _rubric_is_stale(real, real) is False

    # The malformed variants are built from a SYNTHETIC well-formed fingerprint,
    # not from whatever the committed set happens to carry. Deriving them from
    # `real` silently lost its teeth the moment the baseline-8 record gave every
    # set a single recording sha: `real` became a bare 8-character sha, so
    # truncating it to 11 characters returned the string itself and the
    # "truncated digest" case compared a value against itself.
    fingerprint = "multi:0123456789ab"
    assert _rubric_is_stale(fingerprint, fingerprint) is False
    for malformed in (
        "multi:",  # prefix only
        fingerprint[: len("multi:") + 5],  # truncated digest
        fingerprint.upper(),  # non-lowercase hex
        fingerprint + "ab",  # over-long
        "multi:zzzzzzzzzzzz",  # non-hex
    ):
        assert _rubric_is_stale(malformed, fingerprint) is True, malformed
        assert _rubric_is_stale(fingerprint, malformed) is True, malformed
        # ...and malformed against the real committed key, in both directions.
        assert _rubric_is_stale(malformed, real) is True, malformed
        assert _rubric_is_stale(real, malformed) is True, malformed
    # A different well-formed fingerprint is stale too (the point of the key).
    assert _rubric_is_stale("multi:000000000000", fingerprint) is True
    assert _rubric_is_stale("multi:000000000000", real) is True
    # A bare git sha keeps the prefix comparison: the manifest stores a SHORT sha
    # and a rubric may carry the full HEAD.
    assert _rubric_is_stale("1e48c40deadbeef", "1e48c40") is False
    # ...and a sha never matches a fingerprint in either direction.
    assert _rubric_is_stale("1e48c40", real) is True


def test_featured_seeds_exist_in_their_committed_sets() -> None:
    # The curated featured list is committed DATA (frontend/src/components/
    # ReplayPicker.tsx: FEATURED_GAMES) — the audits' named good tail, each with a
    # hand-written why-watch line. Its one drift risk is a seed the served set does
    # not carry, which would render as a dead entry; pin that here. The ORDER is
    # editorial and deliberately unpinned — the rubric does not validate it.
    featured = _parse_featured_games()
    assert {game[0] for game in featured} == {"4p1i", "9p2i"}
    # Re-curated against the baseline-7 bytes: every earlier blurb described a
    # game the record changed (audits/audit-phase-20-baseline-7.md §4), so the
    # list was re-read rather than re-scored. Baseline 6 featured 9p2i {2, 8, 17,
    # 23} and 4p1i {2, 29, 41}.
    assert featured[0] == ("9p2i", 2)  # the tour's landing game (the curated head)
    assert {seed for set_name, seed in featured if set_name == "9p2i"} == {
        2,
        13,
        23,
        46,
    }
    assert {seed for set_name, seed in featured if set_name == "4p1i"} == {2, 11, 29}
    registry = SetLoaderRegistry(_PARENT)
    for set_name, seed in featured:
        loader = registry.get(set_name)
        assert any(meta.seed == seed for meta in loader.list_replays())


def test_featured_seed_13_card_states_the_served_turn_shape() -> None:
    # The seed-13 card used to claim five meetings; the served game has THREE, of
    # 7, 6 and 5 spoken turns (audits/audit-phase-21-rerecord.md §5.1.1c). A blurb
    # that names a countable fact needs a check that counts it, or the next record
    # falsifies it again in silence — so the card's own numbers are read back out
    # of the picker and compared against the served set through the loader.
    #
    # The turn counts are read from the SET LOADER rather than from the raw
    # JSONL: the card describes what a viewer sees, which is the served payload.
    registry = SetLoaderRegistry(_PARENT)
    replay = registry.get("9p2i").load_replay("headless-seed-13")
    served = tuple(len(meeting.turns) for meeting in replay.meetings)
    assert served == (7, 6, 5), served

    label = next(
        label
        for (set_name, seed), label in zip(
            _parse_featured_games(), _FEATURED_LABEL.findall(_featured_block())
        )
        if (set_name, seed) == ("9p2i", 13)
    )
    # The card names the shrinking run in words; the words and the bytes agree.
    assert "seven turns, then six, then five" in label
    # ...and it no longer claims a meeting count the served game does not have.
    assert "five meetings" not in label.lower()


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


def _assert_featured_counts(label: str, replay: ReplayView) -> None:
    """Check the bounded count vocabulary used by these editorial labels."""
    words = {"one": 1, "three": 3, "four": 4, "twenty-six": 26}
    text = label.lower()
    meeting = re.search(r"\b(one|four) (?:short )?meetings?\b", text)
    turns = re.search(r"\b(three|twenty-six) (?:spoken )?turns\b", text)
    assert meeting is not None or turns is not None
    if meeting is not None:
        assert len(replay.meetings) == words[meeting.group(1)]
    if turns is not None:
        assert sum(len(item.turns) for item in replay.meetings) == words[turns.group(1)]
    if "no flagged contradictions" in text:
        assert not any(item.contradictions for item in replay.meetings)


@pytest.mark.parametrize(
    "set_name,seed",
    [("9p2i", 2), ("9p2i", 23), ("9p2i", 46), ("4p1i", 29), ("4p1i", 2), ("4p1i", 11)],
)
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
    for claim in (
        "no evidence at all",
        "everything the crew will ever know",
        "engine flagged",
        "most-argued",
    ):
        assert claim not in label
