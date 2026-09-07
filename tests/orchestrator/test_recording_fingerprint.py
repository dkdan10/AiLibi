"""One filename pattern decides what counts as a recording, for every reader.

The fingerprint is a claim about the published source bytes, so it has to see
exactly the files a reader will serve or catalogue. These tests pin the two
committed sets' published fingerprints (the positive control: a shared pattern
that changed them would be a different claim), show that a recording the loader
would serve moves the fingerprint, and hold the parsers to one answer.

The parsers under comparison live in packages of their own (``api``,
``scripts``), so this module imports nothing from ``tests.api`` and defers the
heavier imports into the one test that needs them.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

from orchestrator.recording_fingerprint import (
    recording_fingerprint,
    replay_seed_from_filename,
)
from tests.orchestrator.test_replay_integrity import (
    completed_recording as completed_recording,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SAMPLES = _REPO_ROOT / "replays" / "samples"

# The published fingerprints ``api.public_results._source_url`` maps to a source
# URL. A pattern change that moved either one would silently republish a
# different claim about which bytes the results came from.
_PUBLISHED_9P2I = (
    "sha256:85fb119eeb09cc9b70fc8e9c7e202d41a3c3a93ff62b8ef824907c4cdec25d10"
)
_PUBLISHED_4P1I = (
    "sha256:8bbf89bf86072311d45338dd84a98f4fe51c42fe6709bb606926072c4e617d14"
)

# Names and the seed each one declares (``None`` = declares no seed).
_DECLARED_SEED_CASES: tuple[tuple[str, int | None], ...] = (
    ("replay-seed-1.jsonl", 1),
    ("replay-seed--1.jsonl", -1),
    ("replay-seed-01.jsonl", 1),
    ("replay-seed-debug.jsonl", None),
    ("replay-seed-1.audit.jsonl", None),
)


@pytest.fixture
def recording_dir(completed_recording: Path, tmp_path: Path) -> Path:
    destination = tmp_path / completed_recording.name
    shutil.copyfile(completed_recording, destination)
    roster = completed_recording.parent / "roster.json"
    if roster.exists():
        shutil.copyfile(roster, tmp_path / roster.name)
    return tmp_path


def test_committed_sets_keep_their_source_fingerprint() -> None:
    assert recording_fingerprint(_SAMPLES / "9p2i") == _PUBLISHED_9P2I
    assert recording_fingerprint(_SAMPLES / "4p1i") == _PUBLISHED_4P1I


def test_negative_seed_recording_changes_the_fingerprint(recording_dir: Path) -> None:
    before = recording_fingerprint(recording_dir)
    negative = recording_dir / "replay-seed--1.jsonl"
    negative.write_bytes((recording_dir / "replay-seed-1.jsonl").read_bytes())
    assert recording_fingerprint(recording_dir) != before
    negative.unlink()
    assert recording_fingerprint(recording_dir) == before


def test_a_declared_seed_is_parsed_the_same_way_everywhere() -> None:
    # ``scripts/`` modules resolve as top-level names (mypy_path = "scripts"),
    # the way tests/scripts/conftest.py arranges it for its own package.
    scripts_dir = str(_REPO_ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import _manifest_writer
    import _verify_samples

    from api.replay_loader import _parse_seed_from_filename

    for name, seed in _DECLARED_SEED_CASES:
        assert replay_seed_from_filename(name) == seed, name
        assert _parse_seed_from_filename(name) == seed, name
        assert _verify_samples._seed_from_filename(name) == seed, name
        assert _manifest_writer._seed_from_filename(name) == seed, name
