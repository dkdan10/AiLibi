"""CPU-only engine-playback verification for replay samples (Task 4.17).

Walks every ``replay-seed-*.jsonl`` in a sample directory, loads each through
:class:`api.replay_loader.ReplayLoader`, and asserts the recorded state-hash
chain reconstructs byte-identically under the current engine (DESIGN.md §0,
§11.4). No API spend: this is pure engine playback. The free safety net that
catches silent drift from an engine change before any Phase 5 metric reads a
sample and produces a wrong number.

On divergence it reports the sample id, the divergent tick, and the
expected/actual hashes; a corrupted or unreadable file is reported too.
``verify_samples`` is importable for unit tests; ``main`` is the CLI behind
``scripts/verify_samples.sh``.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

# Allow `uv run python scripts/_verify_samples.py ...` to find top-level
# packages (mirrors scripts/run_tournament.py).
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pydantic import ValidationError  # noqa: E402

from api.replay_loader import ReplayLoader, ReplayStateMismatchError  # noqa: E402
from orchestrator.replay import (  # noqa: E402
    MeetingReplayEntry,
    ReplayEntry,
    ReplayLog,
    read_all_entries,
)

_DEFAULT_SAMPLE_DIR = _REPO_ROOT / "replays" / "samples"
_FILENAME_PREFIX = "replay-seed-"
_FILENAME_SUFFIX = ".jsonl"


@dataclass(frozen=True)
class VerifyFailure:
    """One sample that failed to reconstruct cleanly."""

    game_id: str
    tick: int | None
    expected: str | None
    actual: str | None
    reason: str

    def render(self) -> str:
        if self.tick is not None:
            return (
                f"FAIL: {self.game_id} diverged at tick {self.tick}: "
                f"recorded {self.expected!r}, reconstructed {self.actual!r}"
            )
        return f"FAIL: {self.game_id}: {self.reason}"


def _seed_from_filename(name: str) -> int | None:
    if not (name.startswith(_FILENAME_PREFIX) and name.endswith(_FILENAME_SUFFIX)):
        return None
    core = name[len(_FILENAME_PREFIX) : -len(_FILENAME_SUFFIX)]
    return int(core) if core.isdigit() else None


def sample_paths(sample_dir: Path) -> list[Path]:
    """Every ``replay-seed-<seed>.jsonl`` in ``sample_dir``, sorted by seed."""

    paths: list[tuple[int, Path]] = []
    for path in sample_dir.glob(f"{_FILENAME_PREFIX}*{_FILENAME_SUFFIX}"):
        seed = _seed_from_filename(path.name)
        if seed is not None:
            paths.append((seed, path))
    return [path for _, path in sorted(paths)]


def _paths_by_seed(sample_dir: Path) -> dict[int, list[Path]]:
    by_seed: dict[int, list[Path]] = {}
    for path in sample_paths(sample_dir):
        seed = _seed_from_filename(path.name)
        assert seed is not None  # sample_paths only returns matching names
        by_seed.setdefault(seed, []).append(path)
    return by_seed


def _check_meeting_pre_hashes(game_id: str, path: Path) -> VerifyFailure | None:
    """Cross-check each meeting's recorded ``state_hash_before``.

    ``ReplayLoader.load_replay`` verifies every tick hash and each meeting's
    ``state_hash_after`` against engine playback, but not ``state_hash_before``.
    That field equals the trigger-tick state, i.e. the tick hash at the meeting
    tick — which load_replay *does* verify against reconstruction — so checking
    ``state_hash_before == tick_hash[tick]`` pins it to a verified value and
    catches a corrupted pre-hash the loader would otherwise accept.
    """

    entries = read_all_entries(path)
    tick_hash = {e.tick: e.state_hash for e in entries if isinstance(e, ReplayEntry)}
    for entry in entries:
        if isinstance(entry, MeetingReplayEntry):
            expected = tick_hash.get(entry.tick)
            if expected is not None and entry.state_hash_before != expected:
                return VerifyFailure(
                    game_id=game_id,
                    tick=entry.tick,
                    expected=expected,
                    actual=entry.state_hash_before,
                    reason="meeting state_hash_before diverged from the tick hash",
                )
    return None


def verify_samples(sample_dir: Path) -> list[VerifyFailure]:
    """Engine-replay every sample; return the failures (empty == all clean)."""

    loader = ReplayLoader(sample_dir)
    failures: list[VerifyFailure] = []
    for seed, paths in sorted(_paths_by_seed(sample_dir).items()):
        game_id = f"headless-seed-{seed}"
        # ReplayLoader resolves a game_id to a single canonical path per seed, so
        # two files mapping to the same seed (e.g. replay-seed-0 and
        # replay-seed-00) would let a corrupted duplicate slip through unchecked.
        # The contract is "walk every replay-seed-*.jsonl"; reject the ambiguity.
        if len(paths) > 1:
            names = ", ".join(sorted(p.name for p in paths))
            failures.append(
                VerifyFailure(
                    game_id=game_id,
                    tick=None,
                    expected=None,
                    actual=None,
                    reason=(
                        f"{len(paths)} files map to seed {seed} ({names}); "
                        "ambiguous — only one would be verified"
                    ),
                )
            )
            continue
        try:
            loader.load_replay(game_id)
        except ReplayStateMismatchError as exc:
            failures.append(
                VerifyFailure(
                    game_id=game_id,
                    tick=exc.tick,
                    expected=exc.expected,
                    actual=exc.actual,
                    reason="state-hash mismatch",
                )
            )
            continue
        except ReplayLog.CorruptedFileError as exc:
            failures.append(
                VerifyFailure(
                    game_id=game_id,
                    tick=None,
                    expected=None,
                    actual=None,
                    reason=f"corrupted replay file: {exc}",
                )
            )
            continue
        except (FileNotFoundError, ValueError, ValidationError) as exc:
            failures.append(
                VerifyFailure(
                    game_id=game_id,
                    tick=None,
                    expected=None,
                    actual=None,
                    reason=f"{type(exc).__name__}: {exc}",
                )
            )
            continue
        pre_hash_failure = _check_meeting_pre_hashes(game_id, paths[0])
        if pre_hash_failure is not None:
            failures.append(pre_hash_failure)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify replay samples reconstruct byte-identically under the "
            "current engine (Task 4.17; DESIGN.md §11.4). CPU only, no API."
        ),
    )
    parser.add_argument(
        "sample_dir",
        nargs="?",
        type=Path,
        default=_DEFAULT_SAMPLE_DIR,
        help="directory of replay-seed-*.jsonl files (default: replays/samples)",
    )
    args = parser.parse_args(argv)
    sample_dir: Path = args.sample_dir

    if not sample_dir.is_dir():
        print(f"Sample directory not found: {sample_dir}", file=sys.stderr)
        return 2
    paths = sample_paths(sample_dir)
    if not paths:
        print(f"No replay-seed-*.jsonl files in {sample_dir}", file=sys.stderr)
        return 2

    failures = verify_samples(sample_dir)
    if failures:
        for failure in failures:
            print(failure.render())
        print(
            f"Sample verification FAILED: {len(failures)}/{len(paths)} samples "
            "drifted from engine determinism (DESIGN.md §0, §11.4). The engine "
            "no longer reproduces these replays byte-identically."
        )
        return 1
    print(f"All {len(paths)} samples verified clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
