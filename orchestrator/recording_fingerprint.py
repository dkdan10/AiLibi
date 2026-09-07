"""Identify the recording bytes an optional enrichment was derived from."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Final

# One filename pattern decides what a recording is, shared by the fingerprint
# below and by every reader that serves, verifies or catalogues the same
# directory (api.replay_loader, api.public_results, scripts/_verify_samples,
# scripts/_manifest_writer). The seed core is deliberately permissive: the
# loader already parses, validates and SERVES ``replay-seed--1.jsonl`` as
# ``headless-seed--1``, so a fingerprint of the published inputs that ignored a
# file the loader publishes would not be a fingerprint of what is published.
# Digit-only names match the permissive spelling identically, so every committed
# set keeps its exact published fingerprint.
REPLAY_FILENAME_GLOB: Final[str] = "replay-seed-*.jsonl"
REPLAY_FILENAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"replay-seed-(-?\d+)\.jsonl"
)


def replay_seed_from_filename(name: str) -> int | None:
    """The seed ``name`` declares, or ``None`` when it declares none.

    ``None`` means "not a recording": a hand-named ``replay-seed-debug.jsonl``
    or a sidecar such as ``replay-seed-1.audit.jsonl`` declares no seed, so no
    reader treats it as source bytes.
    """

    match = REPLAY_FILENAME_PATTERN.fullmatch(name)
    return int(match.group(1)) if match is not None else None


def recording_fingerprint(directory: Path) -> str:
    """Hash replay filenames/content and the roster and manifest, including absence.

    Observation audit sidecars and derived reports are deliberately excluded.
    The versioned digest binds an enrichment to actual source bytes even when a
    replay is replaced without updating its manifest's recording commit label.
    """

    replays = sorted(
        path
        for path in directory.glob(REPLAY_FILENAME_GLOB)
        if replay_seed_from_filename(path.name) is not None
    )
    if not replays:
        raise ValueError(f"no recorded replays to fingerprint in {directory}")
    digest = hashlib.sha256(b"ailibi-recording-inputs-v1\n")
    for path in [*replays, directory / "roster.json", directory / "MANIFEST.md"]:
        digest.update(path.name.encode("utf-8") + b"\0")
        digest.update(
            hashlib.sha256(path.read_bytes()).digest() if path.exists() else b"absent"
        )
        digest.update(b"\n")
    return "sha256:" + digest.hexdigest()
