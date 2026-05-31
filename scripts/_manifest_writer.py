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
* ``roster --sample-dir DIR --num-players N --num-impostors M
  --tasks-per-crewmate K`` — ensure the set's ``roster.json`` matches the
  requested roster (write it for a non-default set, fail loud if an existing one
  disagrees), so a per-set refresh produces a reconstructable set.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
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

# Per-set roster sidecar (Task 7.4). Mirrors api.replay_loader: the flat MVP
# baseline (4p/1i + 1 task) carries NO sidecar — the loader reconstructs it from
# its defaults (num_impostors=1, tasks_per_crewmate=1, num_players inferred from
# the action stream). EVERY other committed set carries an explicit roster.json
# (also the deferred frontend browse track's metadata source), so a per-set
# refresh must write + validate it BEFORE spending. Kept as literals (not an
# orchestrator.game import) so this lightweight refresh helper stays cheap to load.
_ROSTER_FILENAME = "roster.json"
_ROSTER_FIELDS = ("num_players", "num_impostors", "tasks_per_crewmate")
# (num_players, num_impostors, tasks_per_crewmate) of the descriptor-less baseline.
_MVP_BASELINE_ROSTER = (4, 1, 1)

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


def _atomic_write_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically (Audit H-H-3).

    The manifest is rewritten in full on every ``update`` / ``prune`` /
    ``rebuild``. A plain ``Path.write_text`` truncates the live file before
    writing, so a crash mid-write leaves a half-written or empty MANIFEST. Here
    the new content is written to a sibling temp file on the *same* filesystem
    and ``os.replace``-d into place: ``os.replace`` is atomic, so a reader (or a
    crash) sees either the complete old file or the complete new one, never a
    truncated one. The temp file is removed if anything fails before the rename.
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


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
    _atomic_write_text(manifest_path, render_manifest(rows.values()))


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
        _atomic_write_text(manifest_path, render_manifest(kept.values()))
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
    _atomic_write_text(manifest_path, render_manifest(rows))
    return len(rows)


def sum_cost(sample_dir: Path, seeds: Sequence[int]) -> float:
    return sum(compute_cost_usd(_sample_path(sample_dir, seed)) for seed in seeds)


def _roster_needs_sidecar(
    num_players: int, num_impostors: int, tasks_per_crewmate: int
) -> bool:
    """True for every set except the descriptor-less flat MVP baseline (4p/1i).

    The loader reconstructs the baseline from its defaults with no sidecar; any
    other roster — multi-impostor, multi-task, OR a different player count — is
    given an explicit descriptor so "no descriptor" unambiguously means the
    baseline and the browse track can read each non-baseline set's roster.
    """

    return (num_players, num_impostors, tasks_per_crewmate) != _MVP_BASELINE_ROSTER


def _validated_roster(raw: object, *, source: str) -> dict[str, int]:
    """Validate a roster mapping with ``api.replay_loader``'s strict rules.

    Mirrors ``api.replay_loader._load_roster_config``: ``raw`` must be a mapping
    with EXACTLY :data:`_ROSTER_FIELDS`, each a positive ``int`` (``bool``
    rejected — ``true`` is not ``1``). Raises :class:`ValueError` otherwise.

    Used as the pre-spend gate for BOTH the requested roster (reject a mistyped /
    non-positive env value before writing a malformed sidecar) and any existing
    on-disk descriptor (reject a type-malformed sidecar — e.g. ``7.0`` or
    ``true`` — that would ``==`` the requested ints under Python equality but be
    rejected by the loader only AFTER the money is spent). ``source`` names the
    subject for the error message.
    """

    if not isinstance(raw, dict):
        raise ValueError(f"{source}: expected a JSON object, got {type(raw).__name__}")
    keys = set(raw)
    expected_keys = set(_ROSTER_FIELDS)
    if keys != expected_keys:
        raise ValueError(
            f"{source}: keys must be exactly {sorted(expected_keys)}, "
            f"got {sorted(keys)}"
        )
    validated: dict[str, int] = {}
    for key in _ROSTER_FIELDS:
        value = raw[key]
        # ``bool`` is an ``int`` subclass; reject it so ``true`` is not read as 1.
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"{source}: {key} must be an integer, got {value!r}")
        if value < 1:
            raise ValueError(f"{source}: {key} must be a positive integer, got {value}")
        validated[key] = value
    return validated


def _validate_roster_is_seedable(roster: dict[str, int]) -> None:
    """Reject a roster the seeder itself would reject, BEFORE writing a sidecar.

    ``_validated_roster`` guarantees positive ints, but the seeder also enforces
    cross-field invariants (``2 <= num_players``, ``1 <= num_impostors <
    num_players``) and the map's task-pool capacity (``num_crewmates *
    tasks_per_crewmate <= len(map.tasks)``). Run those EXACT checks by probing
    :func:`orchestrator.seeder.seed_initial_state` against the canonical map
    ``run_tournament.py`` uses, so an invalid-but-positive roster (e.g. ``1p/1i``,
    or a task count that exhausts the map) fails loud here instead of being
    written into a sidecar that ``run_tournament.py`` then rejects — which would
    poison the directory with a descriptor a later corrected refresh refuses to
    overwrite. Imported lazily so the per-seed ``update`` path stays cheap.
    """

    from engine.world import load_canonical_map
    from orchestrator.seeder import seed_initial_state

    try:
        seed_initial_state(
            seed=0,
            game_map=load_canonical_map(),
            num_players=roster["num_players"],
            num_impostors=roster["num_impostors"],
            tasks_per_crewmate=roster["tasks_per_crewmate"],
        )
    except ValueError as exc:
        raise ValueError(f"requested roster is invalid for the seeder: {exc}") from exc


def ensure_roster_descriptor(
    sample_dir: Path,
    *,
    num_players: int,
    num_impostors: int,
    tasks_per_crewmate: int,
) -> str:
    """Make ``<sample_dir>/roster.json`` consistent with the requested roster.

    Run by ``refresh_samples.sh`` BEFORE any real-provider spend so a per-set
    refresh produces a set the loader can actually reconstruct, instead of
    failing the per-tick state-hash check AFTER the money is spent (the sidecar
    carries ``num_impostors``/``tasks_per_crewmate``, which are not recoverable
    from the replay). Behaviour:

    * the REQUESTED roster is validated first — a mistyped / non-positive value,
      or one the seeder rejects (bad parity, exhausted task pool), raises here
      rather than being written into a malformed/poison sidecar;
    * if a sidecar exists it is validated with the SAME strict rules and must
      MATCH the requested roster, else raise — never silently overwrite a
      committed set's descriptor, and never let a type-malformed sidecar (e.g.
      ``7.0`` or ``true``) slip past this gate only for the loader to reject it
      after spending; this also catches a refresh that forgot/mistyped the env;
    * else if the requested roster needs a sidecar and none exists, write it;
    * else (flat 4p/1i baseline) leave the directory descriptor-less so the
      loader's default path applies.

    Returns a one-line operator status. Idempotent: a matching sidecar is a no-op.
    The written JSON matches ``api.replay_loader.RosterConfig`` exactly (the three
    integer keys, no extras), so the loader parses it without falling back.
    """

    expected = _validated_roster(
        {
            "num_players": num_players,
            "num_impostors": num_impostors,
            "tasks_per_crewmate": tasks_per_crewmate,
        },
        source="requested roster",
    )
    # Reject a positive-but-seeder-invalid roster (bad parity, exhausted task
    # pool) before writing anything, so a failed refresh leaves no poison sidecar.
    _validate_roster_is_seedable(expected)
    path = sample_dir / _ROSTER_FILENAME
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"unreadable roster descriptor {path}: {exc}") from exc
        existing = _validated_roster(raw, source=f"roster descriptor {path}")
        if existing != expected:
            raise ValueError(
                f"roster descriptor {path} disagrees with the requested roster "
                f"(on disk {existing!r}, requested {expected!r}); refusing to "
                "overwrite. Re-check AILIBI_NUM_PLAYERS / AILIBI_NUM_IMPOSTORS / "
                "AILIBI_TASKS_PER_CREWMATE for this set."
            )
        return f"roster descriptor already matches: {path}"
    if not _roster_needs_sidecar(num_players, num_impostors, tasks_per_crewmate):
        return (
            f"flat {num_players}p/{num_impostors}i default roster — no sidecar "
            f"needed in {sample_dir}"
        )
    _atomic_write_text(path, json.dumps(expected, sort_keys=True) + "\n")
    return f"wrote roster descriptor: {path}"


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

    roster = sub.add_parser(
        "roster",
        help=(
            "ensure <sample-dir>/roster.json matches the requested roster (write "
            "it for a non-default set, fail loud if an existing one disagrees)"
        ),
    )
    roster.add_argument("--sample-dir", type=Path, default=_DEFAULT_SAMPLE_DIR)
    roster.add_argument("--num-players", type=int, required=True)
    roster.add_argument("--num-impostors", type=int, required=True)
    roster.add_argument("--tasks-per-crewmate", type=int, required=True)

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
    if args.command == "roster":
        status = ensure_roster_descriptor(
            args.sample_dir,
            num_players=args.num_players,
            num_impostors=args.num_impostors,
            tasks_per_crewmate=args.tasks_per_crewmate,
        )
        print(status, file=sys.stderr)
        return 0
    return 1  # unreachable: subparser is required


if __name__ == "__main__":
    sys.exit(main())
