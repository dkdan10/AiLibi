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


def test_full_dry_run_announces_alias_cleanup() -> None:
    # Full mode must also drop zero-padded aliases (e.g. replay-seed-01.jsonl),
    # not just seeds outside 0-49, since ReplayLoader would otherwise serve the
    # stale alias ahead of the fresh canonical sample.
    proc = _run("--full", "--dry-run")
    assert proc.returncode == 0
    assert "zero-padded aliases" in proc.stdout
    assert "replay-seed-01.jsonl" in proc.stdout


def test_non_full_dry_run_has_no_cleanup() -> None:
    # Cleanup is a --full-only behavior; targeted refreshes must not announce it.
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "non-canonical" not in proc.stdout


# -- per-set roster routing (Task 7.4) ----------------------------------------


def _clean_env() -> dict[str, str]:
    """Ambient env with every ``AILIBI_*`` routing/roster override stripped."""

    return {k: v for k, v in os.environ.items() if not k.startswith("AILIBI_")}


def test_dry_run_shows_default_roster() -> None:
    # With no roster overrides, the refresh threads the committed FLAT 4p/1i
    # baseline at ONE task/crewmate (NOT run_tournament.py's harness default of
    # 2), so a default refresh re-records replays/samples/ byte-identically.
    proc = _run("--seeds", "22", "--dry-run", env=_clean_env())
    assert proc.returncode == 0
    assert (
        "[dry-run] roster: num_players=4 num_impostors=1 tasks_per_crewmate=1"
        in proc.stdout
    )


def test_dry_run_threads_roster_flags_into_tournament_invocation() -> None:
    proc = _run("--seeds", "22", "--dry-run", env=_clean_env())
    assert proc.returncode == 0
    assert "--num-players 4 --num-impostors 1 --tasks-per-crewmate 1" in proc.stdout


def test_dry_run_default_roster_writes_no_descriptor() -> None:
    # The flat 4p/1i baseline dir needs no sidecar; the dry-run must say so.
    proc = _run("--seeds", "22", "--dry-run", env=_clean_env())
    assert proc.returncode == 0
    assert (
        "[dry-run] roster descriptor: flat 4p/1i baseline — no sidecar written"
        in proc.stdout
    )


def test_dry_run_flat_baseline_rejects_non_4p1i_roster() -> None:
    # A non-4p/1i roster pointed at the flat baseline (e.g. forgot AILIBI_SAMPLE_DIR)
    # must fail loud before any spend — it would otherwise corrupt the committed
    # 4p/1i baseline by writing replays/samples/roster.json.
    env = _clean_env()  # no AILIBI_SAMPLE_DIR -> the flat replays/samples baseline
    env["AILIBI_NUM_IMPOSTORS"] = "2"
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode != 0
    assert "refusing to refresh the flat 4p/1i baseline" in proc.stdout + proc.stderr


def test_dry_run_subdir_baseline_roster_previews_descriptor(tmp_path: Path) -> None:
    # A subdir target with the baseline 4p/1i roster (e.g. forgot the roster env
    # vars) still previews a descriptor write — "no descriptor" is reserved for the
    # flat baseline, so a non-flat dir is never left descriptor-less.
    set_dir = tmp_path / "some-set"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert f"would ensure {set_dir}/roster.json" in proc.stdout


def test_dry_run_non_default_roster_previews_descriptor(tmp_path: Path) -> None:
    # A 7p/2i refresh must preview that it would ensure the set's roster.json,
    # so the descriptor write is observable before any spend.
    set_dir = tmp_path / "7p2i"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
        AILIBI_NUM_PLAYERS="7",
        AILIBI_NUM_IMPOSTORS="2",
        AILIBI_TASKS_PER_CREWMATE="2",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert f"would ensure {set_dir}/roster.json" in proc.stdout
    assert "{num_players: 7, num_impostors: 2, tasks_per_crewmate: 2}" in proc.stdout


def test_dry_run_num_players_only_change_previews_descriptor(tmp_path: Path) -> None:
    # A num-players-only change (7p/1i/1task) is still non-baseline, so the dry-run
    # must preview a descriptor write — consistent with _roster_needs_sidecar.
    set_dir = tmp_path / "7p1i"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
        AILIBI_NUM_PLAYERS="7",
        AILIBI_NUM_IMPOSTORS="1",
        AILIBI_TASKS_PER_CREWMATE="1",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert f"would ensure {set_dir}/roster.json" in proc.stdout


@pytest.mark.parametrize("bad", ["7p", "0", "-1", "abc"])
def test_invalid_roster_env_fails_loud(bad: str) -> None:
    # A non-integer / non-positive roster env value must fail loud — even in
    # --dry-run — rather than error out the arithmetic test and still exit 0 with
    # a misleading no-sidecar plan.
    env = _clean_env()
    env["AILIBI_NUM_PLAYERS"] = bad
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode != 0
    assert "must be a positive integer" in proc.stdout + proc.stderr


def test_leading_zero_roster_env_does_not_bypass_flat_guard() -> None:
    # A leading-zero value (08 == 8) must canonicalize to base 10, not be parsed as
    # octal — otherwise the arithmetic errors out and silently skips the
    # flat-baseline guard. So AILIBI_NUM_IMPOSTORS=08 (a non-4p/1i roster) on the
    # flat baseline must fail loud, with no "value too great for base" octal error.
    env = _clean_env()  # no AILIBI_SAMPLE_DIR -> the flat replays/samples baseline
    env["AILIBI_NUM_IMPOSTORS"] = "08"
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode != 0
    assert "refusing to refresh the flat 4p/1i baseline" in proc.stdout + proc.stderr
    assert "value too great for base" not in proc.stderr


def test_leading_zero_roster_env_normalized_for_subdir(tmp_path: Path) -> None:
    # On a subdir, leading-zero roster values canonicalize to base 10 (08/02/02 ->
    # 8/2/2) for the threaded flags + descriptor, with no octal arithmetic errors.
    set_dir = tmp_path / "set"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
        AILIBI_NUM_PLAYERS="08",
        AILIBI_NUM_IMPOSTORS="02",
        AILIBI_TASKS_PER_CREWMATE="02",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "value too great for base" not in proc.stderr
    assert "{num_players: 8, num_impostors: 2, tasks_per_crewmate: 2}" in proc.stdout


def test_dry_run_routes_per_set_for_7p2i(tmp_path: Path) -> None:
    # Task 7.5 generates the 7p/2i set by setting the roster + per-set dir/manifest
    # env hooks. The dry-run must show the resolved roster, the per-set SAMPLE_DIR
    # / MANIFEST, and the threaded run_tournament.py invocation — all observable
    # without spend, and proving the refresh cannot overwrite the 4p/1i baseline.
    set_dir = tmp_path / "7p2i"
    manifest = set_dir / "MANIFEST.md"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(manifest),
        AILIBI_NUM_PLAYERS="7",
        AILIBI_NUM_IMPOSTORS="2",
        AILIBI_TASKS_PER_CREWMATE="2",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert f"[dry-run] sample dir: {set_dir}" in proc.stdout
    assert f"[dry-run] manifest: {manifest}" in proc.stdout
    assert (
        "[dry-run] roster: num_players=7 num_impostors=2 tasks_per_crewmate=2"
        in proc.stdout
    )
    assert "--num-players 7 --num-impostors 2 --tasks-per-crewmate 2" in proc.stdout


def test_missing_key_creates_no_per_set_directory(tmp_path: Path) -> None:
    # The per-set mkdir is gated behind the API-key preflight: a real (non-dry-run)
    # refresh into a not-yet-existing set dir with no key must fail at preflight
    # WITHOUT creating the directory or spending (no side effect before the check).
    set_dir = tmp_path / "7p2i"
    env = _clean_env()
    env.pop("ANTHROPIC_API_KEY", None)
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
    )
    proc = _run("--seeds", "0", env=env)
    assert proc.returncode != 0
    assert "ANTHROPIC_API_KEY must be set" in proc.stdout + proc.stderr
    assert not set_dir.exists()  # mkdir runs only after the preflight passes
