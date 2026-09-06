"""Versioned identities for recorded inputs and the code deriving model features.

Historical identities describe their original, narrower byte sets. Only version
two binds the roster, map, runtime and local derivation dependency closure.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Literal, TypeAlias

EvidenceScope: TypeAlias = Literal["current", "historical", "synthetic-test"]
SOURCE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = SOURCE_ROOT / "replays/ml_corpus/9p2i"
_DERIVATION_ROOTS = (
    "training/surrogate/dataset.py",
    "training/surrogate/ballots.py",
    "training/conviction/dataset.py",
    "training/conviction/model.py",
    "agents/tactical/features.py",
)


def current_campaign_environment() -> dict[str, str]:
    """The fixed fake-provider, baseline meeting profile for current campaigns.

    This profile is part of the derivation identity. Enabled ambient experiments
    must be refused by campaign preflight, not silently described as this arm.
    """

    return {"AILIBI_LLM_PROVIDER": "fake", "AILIBI_PROMPT_SET": "qwen3_6_27b"}


def require_baseline_campaign_environment() -> None:
    """Refuse experimental runtime inputs before a current campaign writes."""

    from meetings.evidence_profile import MeetingEvidenceProfile
    from orchestrator.replay import substrate_flag_snapshot

    if substrate_flag_snapshot() != substrate_flag_snapshot({}):
        raise ValueError("current campaigns require the baseline substrate profile")
    if MeetingEvidenceProfile.from_environment() != MeetingEvidenceProfile():
        raise ValueError("current campaigns require the baseline evidence profile")


def _digest(rows: list[tuple[str, str]]) -> str:
    return hashlib.sha256(
        json.dumps(rows, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def historical_fit_corpus_fingerprint(corpus_dir: Path) -> str:
    """Reproduce the version-one recorded fingerprint, without certifying a fit."""

    digest = hashlib.sha256()
    paths = sorted(corpus_dir.glob("replay-seed-*.jsonl")) + [
        corpus_dir / name for name in ("splits.json", "MANIFEST.md")
    ]
    for path in paths:
        digest.update(path.name.encode() + b"\x00")
        digest.update(hashlib.sha256(path.read_bytes()).hexdigest().encode() + b"\n")
    return digest.hexdigest()


def derivation_files(source_root: Path = SOURCE_ROOT) -> tuple[Path, ...]:
    """Local Python import closure of the actual feature/label/fit builders.

    Include imported package initializers and relative imports. This is a
    conservative code dependency identity, not a claim that every branch runs
    for every row. Reports and unrelated artifact files are not dependencies.
    """

    pending = [source_root / name for name in _DERIVATION_ROOTS]
    seen: set[Path] = set()
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        tree = ast.parse(path.read_text(), filename=str(path))
        package = list(path.relative_to(source_root).parts[:-1])
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = package[: len(package) - node.level + 1] if node.level else []
                base = ".".join([*prefix, *([node.module] if node.module else [])])
                modules = [base, *(f"{base}.{alias.name}" for alias in node.names)]
            for module in modules:
                parts = module.split(".")
                for index in range(1, len(parts) + 1):
                    base_path = source_root.joinpath(*parts[:index])
                    for candidate in (
                        base_path.with_suffix(".py"),
                        base_path / "__init__.py",
                    ):
                        if candidate.is_file() and candidate not in seen:
                            pending.append(candidate)
    return tuple(sorted(seen))


def derivation_fingerprint(source_root: Path = SOURCE_ROOT) -> str:
    """Bind current reconstruction/fit code, canonical map and installed runtime."""

    paths = [
        *derivation_files(source_root),
        *(
            source_root / name
            for name in (
                "engine/maps/canonical_1.yaml",
                "pyproject.toml",
                "uv.lock",
            )
        ),
    ]
    rows = [
        (
            str(path.relative_to(source_root)),
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in sorted(set(paths))
    ]
    rows.extend(
        [
            ("python", f"{sys.version_info.major}.{sys.version_info.minor}"),
            ("numpy", version("numpy")),
            ("pydantic", version("pydantic")),
        ]
    )
    return _digest(rows)


def fit_corpus_fingerprint(corpus_dir: Path, *, source_root: Path = SOURCE_ROOT) -> str:
    """Version-two fit identity: actual records, roster, split and derivation."""

    paths = sorted(corpus_dir.glob("replay-seed-*.jsonl"))
    if not paths:
        raise ValueError(f"fit corpus contains no replay files: {corpus_dir}")
    paths.extend(
        corpus_dir / name for name in ("roster.json", "splits.json", "MANIFEST.md")
    )
    rows = [
        (path.name, hashlib.sha256(path.read_bytes()).hexdigest()) for path in paths
    ]
    return _digest(
        [
            ("format", "fit-inputs-v2"),
            *rows,
            ("derivation", derivation_fingerprint(source_root)),
        ]
    )


def validate_evidence_scope(scope: EvidenceScope, artifact_dir: Path) -> None:
    """Synthetic fixtures are explicitly isolated from recorded model evidence."""

    if scope not in ("current", "historical", "synthetic-test"):
        raise ValueError(f"unknown model evidence scope: {scope!r}")
    if scope == "synthetic-test":
        if artifact_dir.resolve().is_relative_to(SOURCE_ROOT):
            raise ValueError(
                "synthetic-test evidence must live outside the source tree"
            )
        if (artifact_dir / "fit-corpus.json").exists():
            raise ValueError(
                "synthetic-test weights must not carry fabricated fit-corpus provenance"
            )


def verify_fit_identity(
    *,
    artifact_dir: Path,
    corpus_dir: Path,
    fingerprint_version: int,
    corpus_sha256: str,
    scope: EvidenceScope,
) -> None:
    """Current consumers require v2; historical diagnostics check original bytes."""

    if type(fingerprint_version) is not int or fingerprint_version not in (1, 2):
        raise ValueError("unknown fit fingerprint version")
    validate_evidence_scope(scope, artifact_dir)
    if scope == "synthetic-test":
        raise ValueError("synthetic-test evidence cannot certify a fit identity")
    if scope == "current" and fingerprint_version != 2:
        raise ValueError(
            "historical version-one fit cannot score current inputs; use explicit historical diagnostics or re-ground after a corpus adoption"
        )
    measured = (
        historical_fit_corpus_fingerprint(corpus_dir)
        if fingerprint_version == 1
        else fit_corpus_fingerprint(corpus_dir)
    )
    if measured != corpus_sha256:
        raise ValueError(
            f"fit corpus or derivation drifted; substrate drifted for {artifact_dir}; recorded {corpus_sha256}, measured {measured}"
        )
