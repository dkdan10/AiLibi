"""The committed champion weights artifact + verifying loader (Task 15.20).

``weights.json`` / ``weights.json.sha256`` beside this module are the
agents-side COPY of the frozen training-side champion artifact
``training/artifacts/impostor/utility-es/`` (audits/audit-phase-15-pause.md
decision 1, sha256 ``6d327dcb…``) — float64-hex JSON, the decision-6 retained
lossless representation (:func:`agents.tactical.features.weights_from_hex_json`
round-trips it bit-for-bit). The copy is pinned by test, never read across the
package boundary: ``agents/`` importing ``training/`` (or reading its files at
inference time) would breach the dependency posture the firewall enforces, so
the tests in ``tests/agents/test_learned_policy.py`` assert byte equality of
the payload and sha equality of the sidecars instead.

The loader mirrors ``training.bakeoff.harness.load_candidate_weights``: the
sidecar digest is verified against the payload on every load and drift raises
(fail loud, never a silent fallback).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final

from agents.tactical.features import weights_from_hex_json
from agents.tactical.learned.forward import GENOME_LENGTH

_PACKAGE_DIR: Final[Path] = Path(__file__).resolve().parent

# The committed agents-side champion artifact (the training-side copy).
CHAMPION_WEIGHTS_PATH: Final[Path] = _PACKAGE_DIR / "weights.json"
CHAMPION_WEIGHTS_SIDECAR_PATH: Final[Path] = _PACKAGE_DIR / "weights.json.sha256"


def _verified_payload(weights_path: Path, sidecar_path: Path) -> tuple[str, str]:
    """Read the weights payload and its sidecar digest, verifying they agree."""

    raw = weights_path.read_text()
    recorded = sidecar_path.read_text().split()[0]
    actual = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if actual != recorded:
        raise ValueError(
            f"{weights_path} hashes to {actual} but the sidecar records {recorded}"
        )
    return raw, recorded


def committed_weights_sha256() -> str:
    """The committed sidecar digest, verified against the weights payload.

    The ``weights_sha256`` stamp field
    (:class:`agents.tactical.learned.factory.LearnedPolicyStamp`) reads THIS —
    never a hard-coded constant — so a recording surface cannot mis-stamp: the
    stamped digest is always the digest of the artifact actually loaded.
    """

    _, recorded = _verified_payload(
        CHAMPION_WEIGHTS_PATH, CHAMPION_WEIGHTS_SIDECAR_PATH
    )
    return recorded


def load_champion_weights() -> tuple[float, ...]:
    """Reload the committed champion genome, verifying the sha256 sidecar."""

    raw, _ = _verified_payload(CHAMPION_WEIGHTS_PATH, CHAMPION_WEIGHTS_SIDECAR_PATH)
    weights = weights_from_hex_json(raw)
    if len(weights) != GENOME_LENGTH:
        raise ValueError(
            f"{CHAMPION_WEIGHTS_PATH} carries {len(weights)} weights; the "
            f"utility-es champion genome is {GENOME_LENGTH}"
        )
    return weights


__all__ = [
    "CHAMPION_WEIGHTS_PATH",
    "CHAMPION_WEIGHTS_SIDECAR_PATH",
    "committed_weights_sha256",
    "load_champion_weights",
]
