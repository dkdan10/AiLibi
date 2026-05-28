"""Maintain ``replays/samples/MANIFEST.md`` (Task 4.17; DESIGN.md §9, §11.4).

The manifest is a Markdown table recording the provenance of every sample
replay under ``replays/samples/``: the model snapshot and prompt-template
versions a sample was generated with, when it was refreshed, the git commit at
refresh time, the LLM spend, and the decisive outcome. Phase 5 metric outputs
can then be attributed to a specific prompt version + model snapshot.

This module is the Python half of the refresh workflow; ``refresh_samples.sh``
is the bash front end that runs the tournament and then calls the ``update`` /
``sum-cost`` commands here. It reads provenance straight from the replay JSONLs
via the existing :mod:`orchestrator.replay` helpers (``read_meeting_entries``,
``read_game_outcome``, ``compute_cost_usd``) — it never re-runs a game.

Commands:

* ``rebuild`` — regenerate every row from the samples currently on disk,
  deriving each row's git SHA + date from the commit that last touched that
  sample file. Used to bootstrap the manifest from a pre-existing sample set.
* ``update --seeds N,N`` — recompute rows for the listed seeds and merge them
  into the existing table, leaving other rows untouched. ``refresh_samples.sh``
  passes ``--git-sha`` / ``--refreshed-at`` for the just-refreshed files.
* ``sum-cost --seeds N,N`` — print (stdout, one float) the summed ``cost_usd``
  across the listed seeds' replays. Used for the post-refresh spend line.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Allow `uv run python scripts/_manifest_writer.py ...` to find top-level
# packages (mirrors scripts/run_tournament.py).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from llm.provider import DEFAULT_MEETING_MODEL  # noqa: E402
from orchestrator.replay import (  # noqa: E402
    compute_cost_usd,
    read_game_outcome,
    read_meeting_entries,
)

_DEFAULT_SAMPLE_DIR = _REPO_ROOT / "replays" / "samples"
_FILENAME_PREFIX = "replay-seed-"
_FILENAME_SUFFIX = ".jsonl"

# Sentinel for the prompt_versions column of a sample that had no meetings (no
# LLM calls, hence no prompt templates in play). refresh_samples.sh keys its
# ``--meetings`` seed discovery off this: a row is meeting-bearing iff its
# prompt_versions cell is neither empty nor this sentinel.
_NO_MEETINGS = "(none — no meetings)"
_NULL_WINNER = "null"

_HEADER = (
    "# Sample Replay Manifest\n"
    "\n"
    "Provenance for the replay samples under `replays/samples/`. Each row "
    "records the\nmodel snapshot and prompt-template versions a sample was "
    "generated with, so\nPhase 5 metric outputs can be attributed to a "
    "specific prompt version + model\nsnapshot (DESIGN.md §9, §11.4). "
    "Maintained by `scripts/refresh_samples.sh` (Task\n4.17); run "
    "`scripts/verify_samples.sh` to confirm every sample still reconstructs\n"
    "byte-identically under the current engine.\n"
)
_COLUMNS = (
    "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |"
)
_SEPARATOR = (
    "|------|-------|-----------------|--------------|---------|----------|--------|"
)
_NUM_COLUMNS = 7


@dataclass(frozen=True)
class ManifestRow:
    """One rendered manifest table row. Fields are display strings."""

    seed: int
    model: str
    prompt_versions: str
    refreshed_at: str
    git_sha: str
    cost_usd: str
    winner: str

    def render(self) -> str:
        return (
            f"| {self.seed} | {self.model} | {self.prompt_versions} | "
            f"{self.refreshed_at} | {self.git_sha} | {self.cost_usd} | "
            f"{self.winner} |"
        )


def _seed_from_filename(name: str) -> int | None:
    if not (name.startswith(_FILENAME_PREFIX) and name.endswith(_FILENAME_SUFFIX)):
        return None
    core = name[len(_FILENAME_PREFIX) : -len(_FILENAME_SUFFIX)]
    return int(core) if core.isdigit() else None


def _sample_path(sample_dir: Path, seed: int) -> Path:
    return sample_dir / f"{_FILENAME_PREFIX}{seed}{_FILENAME_SUFFIX}"


def discover_seeds(sample_dir: Path) -> list[int]:
    """Return every seed with a ``replay-seed-<seed>.jsonl`` file, ascending."""

    seeds: list[int] = []
    for path in sample_dir.glob(f"{_FILENAME_PREFIX}*{_FILENAME_SUFFIX}"):
        seed = _seed_from_filename(path.name)
        if seed is not None:
            seeds.append(seed)
    return sorted(seeds)


def _meeting_models(sample_dir: Path) -> set[str]:
    """Distinct LLM model ids across every meeting in the sample directory."""

    models: set[str] = set()
    for seed in discover_seeds(sample_dir):
        for meeting in read_meeting_entries(_sample_path(sample_dir, seed)):
            models.update(call.model for call in meeting.llm_calls)
    return models


def fallback_model(sample_dir: Path) -> str:
    """Model id to attribute to a sample that recorded no LLM calls.

    A meeting-free sample never invoked the provider, so its replay carries no
    model id. We attribute the model the rest of the directory's meetings used
    (the tournament's strategic model), falling back to the configured default
    when no sample in the directory had a meeting.
    """

    models = _meeting_models(sample_dir)
    if models:
        return ", ".join(sorted(models))
    return DEFAULT_MEETING_MODEL


def sample_provenance(
    sample_dir: Path, seed: int, fallback: str
) -> tuple[str, str, str, str]:
    """Return ``(model, prompt_versions, cost_usd, winner)`` for one sample.

    Derived entirely from the replay JSONL: the union of every meeting's
    ``prompt_versions`` values, the distinct models its LLM calls used, the
    summed cost, and the decisive outcome.
    """

    path = _sample_path(sample_dir, seed)
    versions: set[str] = set()
    models: set[str] = set()
    for meeting in read_meeting_entries(path):
        versions.update(meeting.prompt_versions.values())
        models.update(call.model for call in meeting.llm_calls)
    model = ", ".join(sorted(models)) if models else fallback
    prompt_versions = ", ".join(sorted(versions)) if versions else _NO_MEETINGS
    cost_usd = f"{compute_cost_usd(path):.4f}"
    winner = read_game_outcome(path) or _NULL_WINNER
    return model, prompt_versions, cost_usd, winner


def _git_short_sha() -> str | None:
    return _run_git(["rev-parse", "--short", "HEAD"])


def _git_file_provenance(path: Path) -> tuple[str | None, str | None]:
    """``(short_sha, YYYY-MM-DD)`` of the commit that last touched ``path``.

    Returns ``(None, None)`` when git is unavailable or the file is untracked
    (e.g. a freshly written, uncommitted refresh — the caller then stamps the
    current HEAD + date instead).
    """

    line = _run_git(["log", "-1", "--format=%h:%ad", "--date=short", "--", str(path)])
    if not line or ":" not in line:
        return None, None
    sha, _, date = line.partition(":")
    return (sha or None), (date or None)


def _run_git(args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip() or None


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _resolve_sha_date(
    path: Path, override_sha: str | None, override_date: str | None
) -> tuple[str, str]:
    """Pick the git SHA + date for a row.

    Explicit overrides win (the live-refresh path stamps just-written files
    with the current HEAD + date). Otherwise derive from the file's own git
    history (the bootstrap/rebuild path reconstructs honest provenance from the
    commit that created each sample), falling back to HEAD + today.
    """

    if override_sha is not None and override_date is not None:
        return override_sha, override_date
    file_sha, file_date = _git_file_provenance(path)
    sha = override_sha or file_sha or _git_short_sha() or "unknown"
    date = override_date or file_date or _today()
    return sha, date


def build_row(
    sample_dir: Path,
    seed: int,
    fallback: str,
    override_sha: str | None,
    override_date: str | None,
) -> ManifestRow:
    model, prompt_versions, cost_usd, winner = sample_provenance(
        sample_dir, seed, fallback
    )
    sha, date = _resolve_sha_date(
        _sample_path(sample_dir, seed), override_sha, override_date
    )
    return ManifestRow(
        seed=seed,
        model=model,
        prompt_versions=prompt_versions,
        refreshed_at=date,
        git_sha=sha,
        cost_usd=cost_usd,
        winner=winner,
    )


def render_manifest(rows: Iterable[ManifestRow]) -> str:
    body = "\n".join(row.render() for row in sorted(rows, key=lambda row: row.seed))
    return f"{_HEADER}\n{_COLUMNS}\n{_SEPARATOR}\n{body}\n"


def parse_manifest(text: str) -> dict[int, ManifestRow]:
    """Parse a rendered manifest back into ``{seed: ManifestRow}``.

    Tolerant by design: any line that is not a pipe-delimited row with exactly
    seven cells whose first cell is an integer is skipped (title, prose,
    header, and separator rows all fall away). Prompt-version cells contain
    commas but never pipes, so the split is unambiguous.
    """

    rows: dict[int, ManifestRow] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != _NUM_COLUMNS or not cells[0].isdigit():
            continue
        seed = int(cells[0])
        rows[seed] = ManifestRow(
            seed=seed,
            model=cells[1],
            prompt_versions=cells[2],
            refreshed_at=cells[3],
            git_sha=cells[4],
            cost_usd=cells[5],
            winner=cells[6],
        )
    return rows


def update_manifest(
    manifest_path: Path,
    sample_dir: Path,
    seeds: Sequence[int],
    *,
    git_sha: str | None,
    refreshed_at: str | None,
    model_override: str | None = None,
) -> None:
    """Recompute rows for ``seeds`` and merge into the existing manifest.

    ``model_override`` is the model the refresh actually ran with; it is used
    for seeds whose replay recorded no LLM call (no meeting), so a refresh with
    a non-default ``AILIBI_LLM_MEETING_MODEL`` attributes those rows to the
    active model rather than a stale directory-derived one. Seeds that *did*
    record calls always use their own recorded model. When ``None``, the
    no-call fallback is derived from the directory's meetings.
    """

    fallback = model_override if model_override else fallback_model(sample_dir)
    rows = (
        parse_manifest(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else {}
    )
    for seed in seeds:
        rows[seed] = build_row(sample_dir, seed, fallback, git_sha, refreshed_at)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(render_manifest(rows.values()), encoding="utf-8")


def prune_manifest(manifest_path: Path, sample_dir: Path) -> int:
    """Drop manifest rows whose ``replay-seed-<seed>.jsonl`` is gone.

    Reconciles the manifest with the files on disk so a stale row cannot
    outlive its replay. Returns the number of rows dropped. Used by
    ``refresh_samples.sh --full`` after it removes non-canonical samples, so a
    full refresh leaves the manifest describing exactly the samples present.
    """

    if not manifest_path.exists():
        return 0
    rows = parse_manifest(manifest_path.read_text(encoding="utf-8"))
    present = set(discover_seeds(sample_dir))
    kept = {seed: row for seed, row in rows.items() if seed in present}
    dropped = len(rows) - len(kept)
    if dropped:
        manifest_path.write_text(render_manifest(kept.values()), encoding="utf-8")
    return dropped


def remove_noncanonical_replays(
    sample_dir: Path, canonical_seeds: Iterable[int]
) -> list[Path]:
    """Delete replay files that are not a canonical sample for ``canonical_seeds``.

    After ``refresh_samples.sh --full`` regenerates ``replay-seed-<seed>.jsonl``
    for every seed in ``canonical_seeds``, the directory may still hold:

    * a stray sample for a seed outside the set (left by a prior ``--seeds``
      run), and
    * a zero-padded alias such as ``replay-seed-01.jsonl``. Its canonical
      ``replay-seed-1.jsonl`` was just (re)written, but
      ``ReplayLoader._replay_paths`` dedups duplicate seeds to the
      lexicographically-first filename — and ``replay-seed-01`` sorts *ahead* of
      ``replay-seed-1`` — so the stale alias would shadow the fresh sample for
      every API/eval consumer.

    Both are non-canonical and removed here, so a full refresh leaves exactly one
    canonical file per seed. A file whose seed core is non-numeric (e.g. a
    hand-named ``replay-seed-debug.jsonl``) declares no seed and is ignored by
    ReplayLoader, so it is left untouched. Returns the deleted paths (sorted).
    """

    canonical = set(canonical_seeds)
    removed: list[Path] = []
    for path in sorted(sample_dir.glob(f"{_FILENAME_PREFIX}*{_FILENAME_SUFFIX}")):
        core = path.name[len(_FILENAME_PREFIX) : -len(_FILENAME_SUFFIX)]
        if not core.isdigit():
            continue  # non-numeric core declares no seed; not ours to remove
        seed = int(core)
        canonical_name = f"{_FILENAME_PREFIX}{seed}{_FILENAME_SUFFIX}"
        if seed in canonical and path.name == canonical_name:
            continue  # the canonical sample for an in-set seed; keep it
        path.unlink()
        removed.append(path)
    return removed


def rebuild_manifest(manifest_path: Path, sample_dir: Path) -> int:
    """Regenerate the whole manifest from the samples on disk.

    Each row's git SHA + date come from the commit that last touched the
    sample file. Returns the number of rows written.
    """

    fallback = fallback_model(sample_dir)
    seeds = discover_seeds(sample_dir)
    rows = [build_row(sample_dir, seed, fallback, None, None) for seed in seeds]
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(render_manifest(rows), encoding="utf-8")
    return len(rows)


def sum_cost(sample_dir: Path, seeds: Sequence[int]) -> float:
    return sum(compute_cost_usd(_sample_path(sample_dir, seed)) for seed in seeds)


def _parse_seed_csv(value: str) -> list[int]:
    seeds: list[int] = []
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if not token.isdigit():
            raise argparse.ArgumentTypeError(
                f"invalid seed (want a non-negative integer): {token!r}"
            )
        seed = int(token)
        if seed not in seeds:  # de-dup so sum-cost cannot double-count a seed
            seeds.append(seed)
    if not seeds:
        raise argparse.ArgumentTypeError("no seeds provided")
    return seeds


def _manifest_for(args: argparse.Namespace) -> Path:
    manifest: Path | None = args.manifest
    return manifest if manifest is not None else args.sample_dir / "MANIFEST.md"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Maintain replays/samples/MANIFEST.md (Task 4.17).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    rebuild = sub.add_parser(
        "rebuild", help="regenerate every row from samples on disk"
    )
    rebuild.add_argument("--sample-dir", type=Path, default=_DEFAULT_SAMPLE_DIR)
    rebuild.add_argument("--manifest", type=Path, default=None)

    update = sub.add_parser(
        "update", help="recompute rows for --seeds and merge into the manifest"
    )
    update.add_argument("--seeds", type=_parse_seed_csv, required=True)
    update.add_argument("--git-sha", default=None)
    update.add_argument("--refreshed-at", default=None)
    update.add_argument(
        "--model",
        default=None,
        help="model the refresh ran with; used for seeds that recorded no calls",
    )
    update.add_argument("--sample-dir", type=Path, default=_DEFAULT_SAMPLE_DIR)
    update.add_argument("--manifest", type=Path, default=None)

    prune = sub.add_parser(
        "prune", help="drop manifest rows whose replay file no longer exists"
    )
    prune.add_argument("--sample-dir", type=Path, default=_DEFAULT_SAMPLE_DIR)
    prune.add_argument("--manifest", type=Path, default=None)

    canonicalize = sub.add_parser(
        "canonicalize",
        help=(
            "(full refresh) delete non-canonical replay files for --seeds "
            "(strays + zero-padded aliases), then prune their manifest rows"
        ),
    )
    canonicalize.add_argument(
        "--seeds",
        type=_parse_seed_csv,
        required=True,
        help="the canonical seed set the full refresh regenerated (e.g. 0..49)",
    )
    canonicalize.add_argument("--sample-dir", type=Path, default=_DEFAULT_SAMPLE_DIR)
    canonicalize.add_argument("--manifest", type=Path, default=None)

    sum_cost_parser = sub.add_parser(
        "sum-cost", help="print summed cost_usd across --seeds (stdout, one float)"
    )
    sum_cost_parser.add_argument("--seeds", type=_parse_seed_csv, required=True)
    sum_cost_parser.add_argument("--sample-dir", type=Path, default=_DEFAULT_SAMPLE_DIR)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "rebuild":
        manifest = _manifest_for(args)
        written = rebuild_manifest(manifest, args.sample_dir)
        print(f"Wrote {manifest} ({written} samples).", file=sys.stderr)
        return 0
    if args.command == "update":
        manifest = _manifest_for(args)
        update_manifest(
            manifest,
            args.sample_dir,
            args.seeds,
            git_sha=args.git_sha,
            refreshed_at=args.refreshed_at,
            model_override=args.model,
        )
        seeds_csv = ",".join(str(seed) for seed in args.seeds)
        print(f"Updated {manifest} for seeds {seeds_csv}.", file=sys.stderr)
        return 0
    if args.command == "prune":
        manifest = _manifest_for(args)
        dropped = prune_manifest(manifest, args.sample_dir)
        print(f"Pruned {dropped} stale row(s) from {manifest}.", file=sys.stderr)
        return 0
    if args.command == "canonicalize":
        manifest = _manifest_for(args)
        removed = remove_noncanonical_replays(args.sample_dir, args.seeds)
        for path in removed:
            print(f"Removed non-canonical sample: {path.name}", file=sys.stderr)
        dropped = prune_manifest(manifest, args.sample_dir)
        print(
            f"Canonicalized {args.sample_dir}: removed {len(removed)} "
            f"non-canonical sample(s), pruned {dropped} stale row(s).",
            file=sys.stderr,
        )
        return 0
    if args.command == "sum-cost":
        print(f"{sum_cost(args.sample_dir, args.seeds):.4f}")
        return 0
    return 1  # unreachable: subparser is required


if __name__ == "__main__":
    sys.exit(main())
