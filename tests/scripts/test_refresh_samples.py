"""Tests for scripts/refresh_samples.sh argument handling (Task 4.17).

Exercises mode parsing, mutual exclusion, seed validation, and --dry-run via
subprocess. Every case is hermetic: --dry-run makes no API call, runs no
tournament, and writes nothing, so no real-provider spend or sample mutation
happens here.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REFRESH_SH = _REPO_ROOT / "scripts" / "refresh_samples.sh"
_MANIFEST = _REPO_ROOT / "replays" / "samples" / "MANIFEST.md"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash required to run refresh_samples.sh"
)


def _run(
    *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    # Default to the real defaults by stripping any ambient sample/manifest
    # overrides; callers that need a fixture manifest pass their own env.
    if env is None:
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("AILIBI_MANIFEST", "AILIBI_SAMPLE_DIR")
        }
    return subprocess.run(
        ["bash", str(_REFRESH_SH), *args],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def test_no_args_prints_usage_and_fails() -> None:
    proc = _run()
    assert proc.returncode != 0
    assert "Usage:" in proc.stdout + proc.stderr


def test_help_exits_zero() -> None:
    proc = _run("--help")
    assert proc.returncode == 0
    assert "Usage:" in proc.stdout


def test_refresh_sh_is_executable() -> None:
    assert _REFRESH_SH.exists()
    assert os.access(_REFRESH_SH, os.X_OK)


def test_full_dry_run_lists_all_seeds() -> None:
    proc = _run("--full", "--dry-run")
    assert proc.returncode == 0
    assert "[dry-run] seeds: 0,1,2," in proc.stdout
    assert ",49" in proc.stdout
    assert "no API calls" in proc.stdout


def test_meetings_dry_run_uses_real_manifest() -> None:
    proc = _run("--meetings", "--dry-run")
    assert proc.returncode == 0
    assert "[dry-run] seeds: 22,24,26,49" in proc.stdout


def test_meetings_dry_run_derives_from_manifest(tmp_path: Path) -> None:
    # A fixture manifest with a different meeting-seed set proves the seed list
    # is read from the manifest, not hard-coded.
    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text(
        "# Sample Replay Manifest\n\n"
        "| seed | model | prompt_versions | refreshed_at | git_sha | cost_usd | winner |\n"
        "|------|-------|-----------------|--------------|---------|----------|--------|\n"
        "| 1 | m | (none — no meetings) | d | s | 0.0000 | CREWMATES |\n"
        "| 5 | m | accusation_round.v2, vote_ballot/v1 | d | s | 0.1000 | IMPOSTORS |\n"
        "| 9 | m | crewmate_report.v1 | d | s | 0.0500 | CREWMATES |\n"
    )
    env = dict(os.environ, AILIBI_MANIFEST=str(manifest))
    proc = _run("--meetings", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] seeds: 5,9" in proc.stdout


def test_seeds_dry_run() -> None:
    proc = _run("--seeds", "7,13,40", "--dry-run")
    assert proc.returncode == 0
    assert "[dry-run] seeds: 7,13,40" in proc.stdout


def test_seeds_requires_value() -> None:
    assert _run("--seeds").returncode != 0


def test_invalid_seed_rejected() -> None:
    proc = _run("--seeds", "3,x", "--dry-run")
    assert proc.returncode != 0
    assert "Invalid seed" in proc.stdout + proc.stderr


@pytest.mark.parametrize(
    "combo",
    [
        ("--full", "--meetings"),
        ("--full", "--seeds", "1"),
        ("--meetings", "--seeds", "1"),
    ],
)
def test_modes_mutually_exclusive(combo: tuple[str, ...]) -> None:
    proc = _run(*combo)
    assert proc.returncode != 0
    assert "mutually exclusive" in proc.stdout + proc.stderr


def test_unknown_argument_rejected() -> None:
    assert _run("--frobnicate").returncode != 0


def test_dry_run_writes_nothing() -> None:
    before = _MANIFEST.read_bytes()
    proc = _run("--full", "--dry-run")
    assert proc.returncode == 0
    assert _MANIFEST.read_bytes() == before


def test_preflight_requires_api_key_before_spend() -> None:
    # A real (non-dry-run) mode with no key must fail at preflight, before any
    # tournament invocation -- so this test never spends, even with a key
    # configured in the ambient environment (it is stripped here).
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    proc = _run("--seeds", "0", env=env)
    assert proc.returncode != 0
    assert "ANTHROPIC_API_KEY must be set" in proc.stdout + proc.stderr


def test_dry_run_forces_anthropic_provider() -> None:
    # The refresh must force the real provider: build_default_client() defaults
    # to the fake provider when AILIBI_LLM_PROVIDER is unset, which would
    # silently re-record fake output over the real samples.
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "AILIBI_LLM_PROVIDER=anthropic" in proc.stdout


def test_duplicate_seeds_deduped() -> None:
    # A typo like 22,22 must not double-call the provider / double-count cost.
    proc = _run("--seeds", "22,22,24", "--dry-run")
    assert proc.returncode == 0
    assert "[dry-run] seeds: 22,24" in proc.stdout


def test_seed_aliases_canonicalized() -> None:
    # "1,01" both parse to seed 1; they must collapse to one, not double-spend.
    proc = _run("--seeds", "1,01", "--dry-run")
    assert proc.returncode == 0
    seeds_line = next(
        line for line in proc.stdout.splitlines() if line.startswith("[dry-run] seeds:")
    )
    assert seeds_line == "[dry-run] seeds: 1"


def test_dry_run_mentions_staging() -> None:
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "temp stage" in proc.stdout


def test_embedded_whitespace_in_seed_rejected() -> None:
    # "1 2" must fail loud rather than silently collapse to seed 12.
    proc = _run("--seeds", "1 2", "--dry-run")
    assert proc.returncode != 0
    assert "Invalid seed" in proc.stdout + proc.stderr


def test_dry_run_mentions_per_seed_manifest_update() -> None:
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "update that seed's manifest row" in proc.stdout


def test_dry_run_shows_meeting_model() -> None:
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "meeting model:" in proc.stdout


def test_full_dry_run_announces_canonical_cleanup() -> None:
    proc = _run("--full", "--dry-run")
    assert proc.returncode == 0
    assert "non-canonical samples" in proc.stdout


def test_non_full_dry_run_has_no_cleanup() -> None:
    # Cleanup is a --full-only behavior; targeted refreshes must not announce it.
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "non-canonical" not in proc.stdout
