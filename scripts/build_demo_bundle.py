#!/usr/bin/env python3
"""Build the self-contained STATIC demo bundle (Task 19.13).

The spectator UI is the project's strongest surface and, until this script, it
had no shippable form: ``vite build`` output was never served by anything, there
is no ``StaticFiles`` mount, and the live API is an unauthenticated GM view that
``docs/deployment.md`` binds to loopback forever. So the demo cannot be "run the
API somewhere" — it has to be an artifact with no API in it at all.

That artifact is one directory:

.. code-block:: text

    <out>/
      index.html            the built frontend (relative asset URLs)
      assets/…              its chunks
      data/<set>/…          the API's URL space, MIRRORED as files

``frontend/src/api/client.ts`` carries the matching half — a data-source seam
that, in a build made with ``VITE_AILIBI_STATIC_DATA=1``, resolves every call to
``./data/<set>/<path>.json`` instead of ``/api/<path>?set=<set>``. Nothing else in
the frontend knows which mode it is in, so the bundle exercises the REAL viewer,
not a cut-down copy of it.

**What is baked, and what is not.** Only the hand-curated FEATURED games —
read straight out of ``frontend/src/components/ReplayPicker.tsx`` so the demo can
never drift from the editorial list — plus the picker metadata and the rubric rows
those games need. Deliberately absent: ``tournament-eval-report.json`` (the 9p2i
one is 29 MB — that is the corpus, not a demo), the per-tick endpoint and the cost
summary (no caller), and every set the featured list does not name. The dashboard
tab in a bundle therefore renders its existing first-class "No tournament report"
panel. That is the honest state, not a bug.

**Offline and $0.** Everything is derived from committed bytes through the SAME
:class:`api.replay_loader.ReplayLoader` the live API uses — no model, no network,
no recording. The one subprocess is ``npm run build``.

Usage::

    uv run python scripts/build_demo_bundle.py [--out DIR]
    uv run python scripts/build_demo_bundle.py --out DIR --skip-frontend-build

Then serve it with anything::

    python -m http.server -d <out> 8080

The default ``--out`` lands inside ``frontend/dist/``, which ``frontend/.gitignore``
already excludes, so a built bundle never shows up in the index. Note that a plain
``npm run build`` empties ``frontend/dist/`` — rebuild the bundle after one.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from api.replay_loader import DEFAULT_SET, ReplayLoader  # noqa: E402
from api.schemas import RubricView  # noqa: E402

_FRONTEND_DIR = _REPO_ROOT / "frontend"
_PICKER_TSX = _FRONTEND_DIR / "src" / "components" / "ReplayPicker.tsx"
_SAMPLES_DIR = _REPO_ROOT / "replays" / "samples"
_DEFAULT_OUT = _FRONTEND_DIR / "dist" / "demo-bundle"

# The committed featured list lives in the picker as editorial DATA (Task 19.9),
# so it is READ from the source rather than restated here — a bundle that baked a
# second copy of the curation would be a second place to forget to update. Same
# two regexes ``tests/api/test_sets.py`` uses to pin the list against the sets on
# disk, so the parse cannot drift between the two readers either.
_FEATURED_BLOCK = re.compile(
    r"FEATURED_GAMES: readonly FeaturedGame\[\] = \[(.*?)\n\];", re.DOTALL
)
_FEATURED_ENTRY = re.compile(r'set: "([^"]+)",\s*\n\s*seed: (\d+),')

# Mirror of ``pathSegment()`` in frontend/src/api/client.ts (static mode): in a
# bundle a path segment is not a route parameter, it is a FILE. Meeting ids are
# ``headless-seed-2:meeting-0``, and a percent-encoded ``:`` comes back out of any
# static server as a literal ``:`` in a filename — portable nowhere. Both sides
# reduce ids to the same safe token instead, and :func:`_bake_set` fails loud if
# two ids ever collapse onto one name.
_UNSAFE_IN_FILENAME = re.compile(r"[^A-Za-z0-9._-]")

# The env vars the frontend build reads (Vite forwards ``VITE_``-prefixed process
# env into ``import.meta.env``). ``STATIC_DATA`` flips the client's seam;
# ``DEFAULT_SET`` is the answer a bundle gives when a request omits ``set``, which
# the live API would resolve server-side from what is on disk.
_ENV_STATIC_DATA = "VITE_AILIBI_STATIC_DATA"
_ENV_DEFAULT_SET = "VITE_AILIBI_STATIC_DEFAULT_SET"

# The proof that the build actually compiled in static mode: the seam's data
# root, which only the static branch of ``apiUrl()`` references.
# ``STATIC_DATA_MODE`` is a build-time constant, so in a NORMAL build that branch
# — and this string with it — is dropped by dead-code elimination. Finding it in
# the emitted JS is therefore a positive signal, not a coincidence. Matched
# WITHOUT a trailing slash: the minifier hoists the constant and builds the path
# by interpolation, so the joined form never appears as one literal.
_STATIC_MODE_MARKER = "./data"


@dataclass(frozen=True)
class FeaturedGame:
    """One curated ``(set, seed)`` pair from the picker's ``FEATURED_GAMES``."""

    set_name: str
    seed: int


@dataclass(frozen=True)
class BakeSummary:
    """What :func:`bake_data` wrote."""

    sets: tuple[str, ...]
    default_set: str
    games: tuple[str, ...]
    files: int
    bytes_written: int


def parse_featured_games(picker_tsx: Path = _PICKER_TSX) -> tuple[FeaturedGame, ...]:
    """The committed featured ``(set, seed)`` pairs, in their curated order.

    Raises :class:`ValueError` when the block is missing, parses empty, or parses
    PARTIALLY.

    The partial case is the dangerous one and the reason for the brace count
    below. ``findall`` is silent about entries it could not match, so a future
    entry written on one line — or with ``seed`` before ``set`` — would be
    dropped while every other entry still matched, and a "did anything match?"
    check would sail straight past it. The bundle would then ship the compiled
    frontend still carrying that editorial entry, with no baked replay behind it,
    and the picker's metadata join would quietly drop the card: the exact
    single-source-of-truth guarantee this parse exists to provide, broken
    silently. One ``{`` per entry object is a format-independent count of what
    the block declares, so a mismatch fails the build instead
    (AGENTS.md: no silent fallbacks).
    """

    block = _FEATURED_BLOCK.search(picker_tsx.read_text(encoding="utf-8"))
    if block is None:
        raise ValueError(f"FEATURED_GAMES not found in {picker_tsx}")
    body = block.group(1)
    games = tuple(
        FeaturedGame(set_name=set_name, seed=int(seed))
        for set_name, seed in _FEATURED_ENTRY.findall(body)
    )
    if not games:
        raise ValueError(f"FEATURED_GAMES in {picker_tsx} parsed to zero entries")
    declared = body.count("{")
    if len(games) != declared:
        raise ValueError(
            f"FEATURED_GAMES in {picker_tsx} parsed {len(games)} of {declared} "
            "entries — an entry does not match the expected "
            '`set: "<name>",\\n seed: <int>,` shape (reformatted? keys reordered?). '
            "Fix the entry or this parser; a partially parsed curation would ship "
            "a bundle missing a featured game."
        )
    return games


def _file_segment(value: str) -> str:
    """Reduce one id to the file name the client's static seam will ask for."""

    return _UNSAFE_IN_FILENAME.sub("_", value)


def resolve_default_set(set_names: tuple[str, ...]) -> str:
    """The set a bundle serves for a request that omits ``set``.

    Mirrors :meth:`api.replay_loader.SetLoaderRegistry.default_set` over the sets
    the bundle actually carries: the curated :data:`api.replay_loader.DEFAULT_SET`
    when it is one of them, else the first — so the advertised default always
    resolves to a directory that exists.
    """

    if not set_names:
        raise ValueError("cannot resolve a default set: the bundle bakes no sets")
    if DEFAULT_SET in set_names:
        return DEFAULT_SET
    return sorted(set_names)[0]


class _Writer:
    """Writes the baked files and tallies them."""

    def __init__(self, data_root: Path) -> None:
        self._data_root = data_root
        self.files = 0
        self.bytes_written = 0
        self._written: dict[Path, str] = {}

    def write(self, relative: str, payload: str, *, source: str) -> None:
        """Write one baked endpoint, failing loud on a name collision.

        Two distinct ids reducing to one file name would silently serve one
        game's bytes for another (AGENTS.md: no silent fallbacks), so the
        originating id is recorded per path and a second, different writer for
        the same path raises.
        """

        path = self._data_root / relative
        previous = self._written.get(path)
        if previous is not None and previous != source:
            raise ValueError(
                f"baked-file name collision at {relative}: {previous!r} and "
                f"{source!r} reduce to the same file name"
            )
        self._written[path] = source
        path.parent.mkdir(parents=True, exist_ok=True)
        data = payload.encode("utf-8")
        path.write_bytes(data)
        self.files += 1
        self.bytes_written += len(data)


def _trimmed_rubric(rubric: RubricView, seeds: frozenset[int]) -> str:
    """The set's rubric with ``per_game`` cut down to the baked seeds.

    The Highlights reel builds its cards FROM ``per_game`` (ReplayPicker's
    ``buildCards``), so shipping the full 50-row rubric in a 4-game bundle would
    render 46 cards that 404 on click. Every other field — the seedset, the
    provenance shas, the staleness verdict — is passed through untouched: the
    bundle subsets the corpus, it does not restate its provenance.
    """

    trimmed = rubric.model_copy(
        update={"per_game": tuple(g for g in rubric.per_game if g.seed in seeds)}
    )
    return trimmed.model_dump_json(by_alias=True)


def _bake_set(
    writer: _Writer,
    *,
    set_name: str,
    seeds: tuple[int, ...],
    samples_dir: Path,
) -> tuple[str, ...]:
    """Bake one recorded set's featured games. Returns their game ids."""

    set_dir = samples_dir / set_name
    if not set_dir.is_dir():
        raise FileNotFoundError(f"no such recorded set: {set_dir}")
    loader = ReplayLoader(replay_dir=set_dir)

    by_seed = {meta.seed: meta for meta in loader.list_replays()}
    missing = [seed for seed in seeds if seed not in by_seed]
    if missing:
        raise FileNotFoundError(
            f"featured seeds absent from {set_dir}: {sorted(missing)}"
        )
    # Seed-sorted, like the live ``GET /replays`` listing, so the browser's card
    # order is the one a reader would see against the real API.
    metas = [by_seed[seed] for seed in sorted(seeds)]
    prefix = _file_segment(set_name)
    writer.write(
        f"{prefix}/replays.json",
        json.dumps([m.model_dump(mode="json", by_alias=True) for m in metas]),
        source=f"{set_name}/replays",
    )

    game_ids: list[str] = []
    for meta in metas:
        game_id = meta.game_id
        game_ids.append(game_id)
        gid = _file_segment(game_id)
        replay = loader.load_replay(game_id)
        writer.write(
            f"{prefix}/replays/{gid}.json",
            replay.model_dump_json(by_alias=True),
            source=game_id,
        )
        frames = loader.belief_frames(game_id)
        writer.write(
            f"{prefix}/replays/{gid}/beliefs.json",
            json.dumps([f.model_dump(mode="json", by_alias=True) for f in frames]),
            source=f"{game_id}/beliefs",
        )
        agent_ids = sorted(
            {state.agent_id for tick in replay.ticks for state in tick.agent_states}
        )
        for meeting in replay.meetings:
            mid = _file_segment(meeting.meeting_id)
            writer.write(
                f"{prefix}/replays/{gid}/meetings/{mid}.json",
                meeting.model_dump_json(by_alias=True),
                source=meeting.meeting_id,
            )
            for agent_id in agent_ids:
                try:
                    memory = loader.get_meeting_memory(
                        game_id, meeting.meeting_id, agent_id
                    )
                except KeyError:
                    # No snapshot for this agent at this meeting (they were
                    # already dead). The live API answers 404; so does a static
                    # server with no file there — same shape, no special case.
                    continue
                writer.write(
                    f"{prefix}/replays/{gid}/meetings/{mid}/memory/"
                    f"{_file_segment(agent_id)}.json",
                    memory.model_dump_json(by_alias=True),
                    source=f"{meeting.meeting_id}/{agent_id}",
                )

    try:
        rubric = loader.rubric()
    except FileNotFoundError:
        # An unscored set (4p1i, the fast fixture). The live API 404s; the bundle
        # simply has no file, and the reel renders its "no rubric" empty state.
        pass
    else:
        writer.write(
            f"{prefix}/eval/rubric.json",
            _trimmed_rubric(rubric, frozenset(seeds)),
            source=f"{set_name}/rubric",
        )
    return tuple(game_ids)


def bake_data(
    out_dir: Path,
    *,
    games: tuple[FeaturedGame, ...],
    samples_dir: Path = _SAMPLES_DIR,
) -> BakeSummary:
    """Write ``<out_dir>/data/`` — the API's URL space mirrored as files.

    Any prior ``data/`` tree is REMOVED first, not overwritten in place. Baking
    is not idempotent by overwrite: drop a seed from the curated list (or a whole
    set) and its JSON would survive under a reused output directory, still
    directly fetchable, while this note and ``docs/deployment.md`` both promise
    the bundle ships the current featured games and nothing else. The normal path
    gets this from ``vite build --emptyOutDir``; the ``--skip-frontend-build``
    reuse path would not, and that is the path where a curation edit is most
    likely to be re-baked over an old tree. Only ``data/`` is cleared — the
    frontend assets beside it are what the reuse path exists to keep.
    """

    seeds_by_set: dict[str, list[int]] = {}
    for game in games:
        seeds_by_set.setdefault(game.set_name, []).append(game.seed)
    set_names = tuple(sorted(seeds_by_set))
    default_set = resolve_default_set(set_names)

    data_root = out_dir / "data"
    if data_root.exists():
        shutil.rmtree(data_root)
    writer = _Writer(data_root)
    baked_games: list[str] = []
    for set_name in set_names:
        baked_games.extend(
            _bake_set(
                writer,
                set_name=set_name,
                seeds=tuple(sorted(set(seeds_by_set[set_name]))),
                samples_dir=samples_dir,
            )
        )

    # ``GET /sets`` is the one endpoint that is not per-set. Rather than buy a
    # special case in the client seam, the identical answer is written into EVERY
    # set directory — a few dozen bytes against one uniform resolution rule.
    sets_payload = json.dumps({"sets": list(set_names), "default": default_set})
    for set_name in set_names:
        writer.write(
            f"{_file_segment(set_name)}/sets.json", sets_payload, source="sets"
        )

    return BakeSummary(
        sets=set_names,
        default_set=default_set,
        games=tuple(baked_games),
        files=writer.files,
        bytes_written=writer.bytes_written,
    )


def build_frontend(out_dir: Path, *, default_set: str) -> None:
    """Run ``npm run build`` in static-bundle mode into ``out_dir``.

    ``--emptyOutDir`` is explicit because the target is usually outside Vite's
    root, where Vite refuses to clear a directory it was not told to clear. The
    build runs FIRST and the data is baked into the emptied tree afterwards.
    """

    if not (_FRONTEND_DIR / "node_modules").is_dir():
        raise FileNotFoundError(
            f"{_FRONTEND_DIR / 'node_modules'} is missing — run "
            "`bash scripts/setup_env.sh` (or `npm ci` in frontend/) first"
        )
    env = dict(os.environ)
    env[_ENV_STATIC_DATA] = "1"
    env[_ENV_DEFAULT_SET] = default_set
    subprocess.run(
        [
            "npm",
            "run",
            "build",
            "--",
            "--outDir",
            str(out_dir),
            "--emptyOutDir",
        ],
        cwd=_FRONTEND_DIR,
        env=env,
        check=True,
    )
    _assert_static_mode_compiled_in(out_dir)


def _assert_static_mode_compiled_in(out_dir: Path) -> None:
    """Fail loud unless the emitted JS really was built with the seam flipped.

    Without this the failure mode is silent and nasty: a build that did not pick
    up ``VITE_AILIBI_STATIC_DATA`` produces a bundle that looks complete, ships
    all the baked JSON, and then requests ``/api/...`` from a server that is not
    there. The marker only survives dead-code elimination in a static build.
    """

    index = out_dir / "index.html"
    if not index.is_file():
        # Worded for BOTH callers: a fresh build that emitted nothing, and
        # `--skip-frontend-build` pointed at a directory holding no build.
        raise FileNotFoundError(f"no frontend build in {out_dir}: {index} is missing")
    scripts = sorted(out_dir.glob("assets/*.js"))
    if not scripts:
        raise FileNotFoundError(f"no frontend build in {out_dir}: no assets/*.js")
    if not any(
        _STATIC_MODE_MARKER in script.read_text(encoding="utf-8", errors="replace")
        for script in scripts
    ):
        raise RuntimeError(
            f"the built bundle in {out_dir} carries no {_STATIC_MODE_MARKER!r} data "
            f"root — it was NOT built with {_ENV_STATIC_DATA}=1 and would call the "
            "live API"
        )


def write_bundle_readme(out_dir: Path, summary: BakeSummary) -> None:
    """A short note beside the artifact saying what it is and what it is not.

    This note is what the person PUBLISHING the bundle reads, so it has to be
    exact about the one thing that matters for that decision: what removing the
    API did and did not remove. It removed the live query surface. It did NOT
    remove the game-master DATA — the spectator is a post-game GM view by design
    (docs/architecture.md), so the baked JSON for the featured games carries
    roles, kill attribution, vent usage, per-agent memories and the rendered LLM
    prompts, exactly as the local spectator shows them. Those bytes are already
    committed in ``replays/samples/``; the note says so rather than letting
    "no GM surface" read as "the hidden information is stripped".
    """

    lines = [
        "# AiLibi — static spectator demo",
        "",
        "A self-contained build of the AiLibi spectator UI. There is no API",
        "process and no live game-master endpoint here: every call reads the",
        "pre-baked JSON under `data/`, so any static file server can host it.",
        "",
        "**What that does not mean.** The spectator is a *post-game GM view* by",
        "design, and this bundle keeps that view for the games it ships: `data/`",
        "contains their roles, kill attribution, vent usage, per-agent memories",
        "and rendered LLM prompts. What is gone is the live, unauthenticated,",
        "unbounded query surface over whatever the host has on disk — not the",
        "hidden information for these particular games, which is already public",
        "in `replays/samples/`. Publish accordingly.",
        "",
        "```bash",
        "python -m http.server -d . 8080",
        "```",
        "",
        f"Recorded sets: {', '.join(summary.sets)} (default: {summary.default_set}).",
        f"Games: {len(summary.games)} — the hand-curated featured list only.",
        "",
        "NOT included, on purpose: every recorded game the featured list does not",
        "name, and the aggregate tournament eval report (tens of MB — that is the",
        "corpus, not a demo), so the Dashboard tab shows its 'No tournament",
        "report' state.",
        "",
        "The full corpus, the eval dashboard and the reproducibility commands live",
        "in the repository: https://github.com/dkdan10/AiLibi",
        "",
        "Built by `scripts/build_demo_bundle.py`.",
        "",
    ]
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _human_bytes(count: int) -> str:
    size = float(count)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024
    raise AssertionError("unreachable")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build the self-contained static demo bundle: the built frontend "
            "plus pre-baked JSON for the featured replays only."
        )
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_DEFAULT_OUT,
        help=(
            "Bundle output directory (default: frontend/dist/demo-bundle, which "
            "frontend/.gitignore already excludes)."
        ),
    )
    parser.add_argument(
        "--samples-dir",
        type=Path,
        default=_SAMPLES_DIR,
        help="Parent of the per-set recorded sample dirs (default: replays/samples).",
    )
    parser.add_argument(
        "--skip-frontend-build",
        action="store_true",
        help=(
            "Re-bake data/ over an EXISTING static-mode build in --out (the fast "
            "path when iterating on what gets baked). The reused build is held to "
            "the same static-mode check as a fresh one, so an empty directory or "
            "an ordinary `npm run build` fails here rather than producing a "
            "bundle that calls a live API."
        ),
    )
    args = parser.parse_args()
    out_dir: Path = args.out.resolve()

    games = parse_featured_games()
    set_names = tuple(sorted({game.set_name for game in games}))
    default_set = resolve_default_set(set_names)

    if args.skip_frontend_build:
        # The REUSED build is validated exactly like a fresh one. Skipping the
        # check here would make the documented fast path the one way to produce a
        # bundle that looks complete — data/, README and a zero exit — over an
        # empty directory or an ordinary `npm run build`, i.e. one that calls an
        # API nobody is running (AGENTS.md: no silent fallbacks).
        _assert_static_mode_compiled_in(out_dir)
        print(f"Reusing the static-mode build in {out_dir}; re-baking data/")
    else:
        build_frontend(out_dir, default_set=default_set)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = bake_data(out_dir, games=games, samples_dir=args.samples_dir)
    write_bundle_readme(out_dir, summary)

    total = sum(p.stat().st_size for p in out_dir.rglob("*") if p.is_file())
    print(
        f"Wrote {out_dir}: {len(summary.games)} featured games across "
        f"{len(summary.sets)} set(s) (default {summary.default_set}), "
        f"{summary.files} baked JSON files "
        f"({_human_bytes(summary.bytes_written)}), "
        f"{_human_bytes(total)} total."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
