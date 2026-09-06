"""Identify the recording bytes an optional enrichment was derived from."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


def recording_fingerprint(directory: Path) -> str:
    """Hash replay filenames/content and the roster and manifest, including absence.

    Observation audit sidecars and derived reports are deliberately excluded.
    The versioned digest binds an enrichment to actual source bytes even when a
    replay is replaced without updating its manifest's recording commit label.
    """

    replays = sorted(
        path
        for path in directory.glob("replay-seed-*.jsonl")
        if re.fullmatch(r"replay-seed-\d+\.jsonl", path.name)
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
