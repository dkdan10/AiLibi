"""Tests for scripts/refresh_samples.sh argument handling (Task 4.17).

Exercises mode parsing, mutual exclusion, seed validation, and --dry-run via
subprocess. Every case is hermetic: --dry-run makes no API call, runs no
tournament, and writes nothing, so no real-provider spend or sample mutation
happens here.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import socket
import subprocess
import threading
from collections.abc import Iterator, Sequence
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REFRESH_SH = _REPO_ROOT / "scripts" / "refresh_samples.sh"
# The flat 4p1i baseline (incl. its MANIFEST.md) now lives under
# replays/samples/4p1i/ (Task 12.12); the default refresh target follows it.
_MANIFEST = _REPO_ROOT / "replays" / "samples" / "4p1i" / "MANIFEST.md"

# The canonical local model the ollama preflight checks for (mirrors
# llm.ollama_client.DEFAULT_OLLAMA_MODEL / refresh_samples.sh's
# DEFAULT_OLLAMA_MODEL).
_OLLAMA_MODEL = "qwen3.5:9b"

pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash required to run refresh_samples.sh"
)


def _run(
    *args: str, env: dict[str, str] | None = None, timeout: float | None = None
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
        timeout=timeout,
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
    # Meeting-bearing seeds derived from the committed flat MANIFEST.md after the
    # Task 13.12 redistribute + Wave-E re-record: the far more meeting-dense
    # recording carries a meeting on 39/50 flat 4p/1i seeds.
    assert (
        "[dry-run] seeds: 0,1,2,3,4,5,6,7,8,9,10,11,13,16,17,18,19,20,21,22,23,"
        "24,26,27,28,29,32,33,35,36,39,41,42,44,45,46,47,48,49" in proc.stdout
    )


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


def test_dry_run_default_provider_is_anthropic() -> None:
    # With AILIBI_LLM_PROVIDER unset the refresh defaults to anthropic (never the
    # fake provider, which would silently re-record fake output over the real
    # samples) and the dry-run echoes the resolved provider + its preflight.
    proc = _run("--seeds", "22", "--dry-run", env=_clean_env())
    assert proc.returncode == 0
    assert "[dry-run] provider: anthropic" in proc.stdout
    assert "[dry-run] preflight: would require ANTHROPIC_API_KEY" in proc.stdout
    # The threaded tournament command still pins the provider explicitly so the
    # subprocess cannot fall through to build_default_client()'s fake default.
    assert "AILIBI_LLM_PROVIDER=anthropic uv run python" in proc.stdout


def test_dry_run_featherless_provider_echoes_substrate() -> None:
    # Task 14.7: AILIBI_LLM_PROVIDER=featherless is an accepted provider; the
    # dry-run echoes it, its FEATHERLESS_API_KEY preflight, the prompt set, and
    # the substrate provenance so the locked tuple is never silent (AGENTS.md
    # "no silent fallbacks"). All five levers are unconditionally ON (the four
    # 13.5 levers since Task 14.9, the Task-14.10 evidence_quality_lift lever
    # since the 14.12 close), so no substrate env vars are exported and the echo
    # states the unconditional substrate.
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] provider: featherless" in proc.stdout
    assert "[dry-run] preflight: would require FEATHERLESS_API_KEY" in proc.stdout
    assert "[dry-run] prompt set: qwen3_6_27b" in proc.stdout
    assert (
        "[dry-run] substrate flags: all five levers ON (unconditional; 13.5 "
        "since Task 14.9, evidence_quality_lift since the 14.12 close)" in proc.stdout
    )


def test_dry_run_featherless_defaults_to_two_seed_workers() -> None:
    # Task 14.12: a Featherless refresh records seeds with TWO parallel workers by
    # default (the hosted plan permits 4 concurrent units and a 32B request uses
    # 2, so 2 workers saturate it), each pulling the next available seed from the
    # queue. The dry-run surfaces the worker count so the parallelism is never
    # silent (AGENTS.md "no silent fallbacks").
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
    )
    proc = _run("--full", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] seed workers: 2 parallel" in proc.stdout
    assert "pulls the next available seed from the queue" in proc.stdout


def test_dry_run_worker_count_is_overridable() -> None:
    # An operator who knows their backend can absorb more (or wants a Featherless
    # run pinned to 1 for clean per-seed latency) overrides AILIBI_REFRESH_WORKERS.
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_REFRESH_WORKERS="3",
    )
    proc = _run("--seeds", "0,1,2", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] seed workers: 3 parallel" in proc.stdout

    env["AILIBI_REFRESH_WORKERS"] = "1"
    proc = _run("--seeds", "0,1,2", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] seed workers: 1 (sequential)" in proc.stdout


def test_dry_run_non_featherless_is_sequential_by_default() -> None:
    # Local Ollama (single GPU) and metered Anthropic stay sequential (1 worker):
    # seed parallelism there thrashes the GPU or multiplies the metered burst. The
    # 2-worker default is scoped to the hosted Featherless plan.
    for provider in ("ollama", "anthropic"):
        env = dict(_clean_env(), AILIBI_LLM_PROVIDER=provider)
        proc = _run("--seeds", "0,1", "--dry-run", env=env)
        assert proc.returncode == 0, provider
        assert "[dry-run] seed workers: 1 (sequential)" in proc.stdout, provider


def test_dry_run_seed_crash_retry_scoped_to_featherless() -> None:
    # Task 14.12: a multi-hour hosted Featherless run retries a seed that CRASHES
    # on a transport error (httpx.ConnectError / timeout the client's 429/5xx
    # retry does not cover) up to 4 attempts; local Ollama / Anthropic default to
    # 1 (a crash there is a real, fail-fast error, not a network blip). Overridable
    # via AILIBI_SEED_MAX_ATTEMPTS. The dry-run surfaces the budget (never silent).
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] seed crash-retry: up to 4 attempt(s)" in proc.stdout

    env["AILIBI_SEED_MAX_ATTEMPTS"] = "6"
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] seed crash-retry: up to 6 attempt(s)" in proc.stdout

    env2 = dict(_clean_env(), AILIBI_LLM_PROVIDER="ollama")
    proc = _run("--seeds", "0", "--dry-run", env=env2)
    assert proc.returncode == 0
    assert "[dry-run] seed crash-retry: up to 1 attempt(s)" in proc.stdout


def test_invalid_seed_max_attempts_fails_loud() -> None:
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_SEED_MAX_ATTEMPTS="lots",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode != 0
    assert "AILIBI_SEED_MAX_ATTEMPTS must be a positive integer" in (
        proc.stdout + proc.stderr
    )


def test_invalid_worker_count_fails_loud() -> None:
    # A garbage AILIBI_REFRESH_WORKERS must fail loud, not silently fall back to a
    # default -- a mis-set worker count could over-subscribe the plan.
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_REFRESH_WORKERS="two",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode != 0
    assert "AILIBI_REFRESH_WORKERS must be a positive integer" in (
        proc.stdout + proc.stderr
    )


def test_featherless_preflight_requires_api_key_before_spend() -> None:
    # A real (non-dry-run) featherless mode with no key must fail at preflight,
    # before any tournament invocation -- so this test never spends, even with a
    # key configured in the ambient environment (it is stripped here).
    env = {k: v for k, v in _clean_env().items() if k != "FEATHERLESS_API_KEY"}
    env["AILIBI_LLM_PROVIDER"] = "featherless"
    proc = _run("--seeds", "0", env=env)
    assert proc.returncode != 0
    assert "FEATHERLESS_API_KEY must be set" in proc.stdout + proc.stderr


def test_featherless_refresh_requires_locked_substrate_before_spend() -> None:
    # Task 14.7 / 14.12 (PR #209 review): a real featherless refresh WITH a key
    # but WITHOUT the locked prompt set (qwen3_6_27b) must fail loud at preflight,
    # before any seed is staged -- so an operator cannot spend a multi-hour run
    # recording the wrong (default 9B) set and only learn afterward from the
    # MANIFEST. The substrate LEVERS need no env: all five are unconditionally ON
    # (the four 13.5 levers since Task 14.9, the Task-14.10 evidence_quality_lift
    # lever since the 14.12 close), so the guard only pins the prompt set.
    # _clean_env strips every AILIBI_* var, so the locked prompt set is absent
    # here; the dummy key clears the key check so the substrate guard (which
    # follows it) is what fires.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "featherless"
    env["FEATHERLESS_API_KEY"] = "test-key-unused"  # guard exits before any call
    proc = _run("--seeds", "0", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "locked substrate" in out
    assert "AILIBI_PROMPT_SET must be 'qwen3_6_27b'" in out
    # No substrate-lever env is required any more (they are all unconditional).
    assert "AILIBI_EVIDENCE_QUALITY_LIFT" not in out
    assert "AILIBI_TESTIMONY_AS_CONTENT" not in out


def test_featherless_refresh_accepts_locked_substrate() -> None:
    # Task 14.12: with the locked prompt set, the substrate guard passes -- no
    # lever env needed (all five levers are unconditional). Use --dry-run so the
    # test never spends.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "featherless"
    env["AILIBI_PROMPT_SET"] = "qwen3_6_27b"
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] prompt set: qwen3_6_27b" in proc.stdout
    assert (
        "[dry-run] substrate flags: all five levers ON (unconditional; 13.5 "
        "since Task 14.9, evidence_quality_lift since the 14.12 close)" in proc.stdout
    )


def test_unknown_provider_lists_featherless_in_error() -> None:
    # A typo must not silently select a provider; the error names the three valid
    # providers, now including featherless (Task 14.7).
    env = dict(_clean_env(), AILIBI_LLM_PROVIDER="featherles")
    proc = _run("--seeds", "0", env=env)
    assert proc.returncode != 0
    assert "featherless" in proc.stdout + proc.stderr


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
    # 2), so a default refresh re-records replays/samples/4p1i/ byte-identically.
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


def test_dry_run_default_roster_previews_descriptor() -> None:
    # Post-12.12 there is no privileged flat-root dir: the default 4p1i subdir gets
    # an explicit roster.json like any other set, so the dry-run previews the write
    # (4p/1i) rather than the old "no sidecar" path.
    proc = _run("--seeds", "22", "--dry-run", env=_clean_env())
    assert proc.returncode == 0
    assert "would ensure" in proc.stdout
    assert "replays/samples/4p1i/roster.json" in proc.stdout
    assert "{num_players: 4, num_impostors: 1, tasks_per_crewmate: 1}" in proc.stdout


def test_dry_run_default_dir_has_no_flat_baseline_guard() -> None:
    # The flat-baseline refuse-guard is REMOVED (Task 12.12): every set is a named
    # subdir, so a non-4p/1i roster on the default dir is no longer a special-cased
    # error — the dry-run just previews the descriptor it would write. (A real
    # disagreement with an EXISTING committed descriptor still fails loud, at the
    # _manifest_writer roster gate — not in the dry-run.)
    env = _clean_env()  # no AILIBI_SAMPLE_DIR -> the default 4p1i subdir
    env["AILIBI_NUM_IMPOSTORS"] = "2"
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "refusing to refresh the flat" not in proc.stdout + proc.stderr
    assert "{num_players: 4, num_impostors: 2, tasks_per_crewmate: 1}" in proc.stdout


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
    # A 9p/2i refresh must preview that it would ensure the set's roster.json,
    # so the descriptor write is observable before any spend.
    set_dir = tmp_path / "9p2i"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
        AILIBI_NUM_PLAYERS="9",
        AILIBI_NUM_IMPOSTORS="2",
        AILIBI_TASKS_PER_CREWMATE="2",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert f"would ensure {set_dir}/roster.json" in proc.stdout
    assert "{num_players: 9, num_impostors: 2, tasks_per_crewmate: 2}" in proc.stdout


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


def test_leading_zero_roster_env_canonicalizes_on_default_dir() -> None:
    # A leading-zero value (08 == 8) must canonicalize to base 10, not be parsed as
    # octal (which would error "value too great for base"). Post-12.12 there is no
    # flat-baseline guard, so on the default 4p1i subdir AILIBI_NUM_IMPOSTORS=08 just
    # canonicalizes to 8 and the dry-run previews that roster cleanly.
    env = _clean_env()  # no AILIBI_SAMPLE_DIR -> the default 4p1i subdir
    env["AILIBI_NUM_IMPOSTORS"] = "08"
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "value too great for base" not in proc.stderr
    assert "{num_players: 4, num_impostors: 8, tasks_per_crewmate: 1}" in proc.stdout


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


def test_dry_run_routes_per_set_for_9p2i(tmp_path: Path) -> None:
    # The canonical 9p/2i eval set (DESIGN.md §3.5) is generated by setting the
    # roster + per-set dir/manifest env hooks. The dry-run must show the resolved
    # roster, the per-set SAMPLE_DIR / MANIFEST, and the threaded
    # run_tournament.py invocation — all observable without spend, and proving the
    # refresh cannot overwrite the 4p/1i baseline.
    set_dir = tmp_path / "9p2i"
    manifest = set_dir / "MANIFEST.md"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(manifest),
        AILIBI_NUM_PLAYERS="9",
        AILIBI_NUM_IMPOSTORS="2",
        AILIBI_TASKS_PER_CREWMATE="2",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert f"[dry-run] sample dir: {set_dir}" in proc.stdout
    assert f"[dry-run] manifest: {manifest}" in proc.stdout
    assert (
        "[dry-run] roster: num_players=9 num_impostors=2 tasks_per_crewmate=2"
        in proc.stdout
    )
    assert "--num-players 9 --num-impostors 2 --tasks-per-crewmate 2" in proc.stdout


def test_missing_key_creates_no_per_set_directory(tmp_path: Path) -> None:
    # The per-set mkdir is gated behind the API-key preflight: a real (non-dry-run)
    # refresh into a not-yet-existing set dir with no key must fail at preflight
    # WITHOUT creating the directory or spending (no side effect before the check).
    set_dir = tmp_path / "9p2i"
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


# -- provider-aware preflight (Task 7.7) --------------------------------------


@contextlib.contextmanager
def _stub_ollama_server(model_names: Sequence[str]) -> Iterator[str]:
    """Serve a stub Ollama ``/api/tags`` endpoint; yield its ``host:port``.

    Lets the provider-aware preflight tests exercise the real reachability +
    model-pulled check against a reachable server WITHOUT a real Ollama (and
    without spend): the handler returns a ``models`` list built from
    ``model_names``, so a test can include or omit the configured model.
    """

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 (stdlib handler API)
            if self.path.rstrip("/") == "/api/tags":
                body = json.dumps(
                    {"models": [{"name": name} for name in model_names]}
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self.send_error(404)

        def log_message(self, *args: object) -> None:  # silence test-server noise
            pass

    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _closed_port() -> int:
    """Reserve then release an ephemeral port so nothing is listening on it.

    A connection to the returned port is refused, which is what the
    server-down preflight test needs.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_dry_run_ollama_provider_shows_ollama_preflight() -> None:
    # AILIBI_LLM_PROVIDER=ollama must be honored: the dry-run echoes provider
    # ollama and describes the reachability + model-pulled preflight (default
    # host + canonical model), without making any network call.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "ollama"
    proc = _run("--seeds", "22", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] provider: ollama" in proc.stdout
    assert (
        f"would ping http://localhost:11434/api/tags for reachability and confirm "
        f"model {_OLLAMA_MODEL} is pulled" in proc.stdout
    )
    assert "no API calls made" in proc.stdout


def test_dry_run_ollama_provider_honors_custom_host() -> None:
    # The preflight description must reflect AILIBI_OLLAMA_HOST, so a non-default
    # host is checked (and recorded against) rather than localhost.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "ollama"
    env["AILIBI_OLLAMA_HOST"] = "remote-box:9999"
    proc = _run("--seeds", "22", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "http://remote-box:9999/api/tags" in proc.stdout


def test_dry_run_provider_is_case_insensitive() -> None:
    # Mirror build_default_client()'s lower-casing so "Ollama" / "ANTHROPIC"
    # resolve like their canonical lower-case forms.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "Ollama"
    proc = _run("--seeds", "22", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] provider: ollama" in proc.stdout


def test_dry_run_fake_provider_maps_to_anthropic() -> None:
    # A refresh records REAL samples, so the fake provider is meaningless here.
    # `fake` is the test/CI ambient convention (tests/conftest.py pins it), so it
    # maps to the historical forced default (anthropic) rather than recording
    # fake output -- preserving the original "works regardless of ambient shell".
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "fake"
    proc = _run("--seeds", "22", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] provider: anthropic" in proc.stdout


def test_dry_run_inherited_fake_provider_still_resolves_anthropic() -> None:
    # The common real case: the ambient env (here, the inherited test env, which
    # tests/conftest.py pins to fake) must not break the refresh -- it resolves to
    # anthropic exactly as the historical forced-anthropic behavior did.
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "[dry-run] provider: anthropic" in proc.stdout


def test_dry_run_rejects_unknown_provider() -> None:
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "banana"
    proc = _run("--seeds", "22", "--dry-run", env=env)
    assert proc.returncode != 0
    assert "unknown AILIBI_LLM_PROVIDER='banana'" in proc.stdout + proc.stderr


def test_ollama_preflight_fails_loud_when_server_down() -> None:
    # A real (non-dry-run) ollama refresh must fail BEFORE any spend if the local
    # server is unreachable. Pointing at a closed port makes the reachability
    # ping fail with a clear "ollama serve" remediation; no tournament runs.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "ollama"
    env["AILIBI_OLLAMA_HOST"] = f"127.0.0.1:{_closed_port()}"
    proc = _run("--seeds", "0", env=env, timeout=60)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "Ollama server unreachable" in combined
    assert "ollama serve" in combined


def test_ollama_preflight_fails_loud_when_model_missing(tmp_path: Path) -> None:
    # Server reachable but the configured model not pulled -> fail loud with an
    # "ollama pull" remediation, before any spend.
    set_dir = tmp_path / "9p2i"
    with _stub_ollama_server(model_names=["llama3.1:8b"]) as host:
        env = _clean_env()
        env.update(
            AILIBI_LLM_PROVIDER="ollama",
            AILIBI_OLLAMA_HOST=host,
            AILIBI_SAMPLE_DIR=str(set_dir),
            AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
        )
        proc = _run("--seeds", "0", env=env, timeout=60)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert f"Ollama model {_OLLAMA_MODEL!r} is not pulled" in combined
    assert f"ollama pull {_OLLAMA_MODEL}" in combined


def test_ollama_preflight_proceeds_when_reachable_and_model_present(
    tmp_path: Path,
) -> None:
    # Server reachable AND the configured model pulled -> the preflight passes and
    # the run proceeds past it (the "Ollama preflight OK" gate line is printed).
    # The stub does not serve /api/generate, so any later tournament step just
    # fails fast against it -- this test asserts only that the GATE proceeded, and
    # that it did NOT report a preflight failure. No real provider, no spend.
    set_dir = tmp_path / "9p2i"
    with _stub_ollama_server(model_names=[_OLLAMA_MODEL, "llama3.1:8b"]) as host:
        env = _clean_env()
        env.update(
            AILIBI_LLM_PROVIDER="ollama",
            AILIBI_OLLAMA_HOST=host,
            AILIBI_SAMPLE_DIR=str(set_dir),
            AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
        )
        proc = _run("--seeds", "0", env=env, timeout=120)
    combined = proc.stdout + proc.stderr
    assert "Ollama preflight OK" in combined
    assert f"model {_OLLAMA_MODEL} present" in combined
    # The gate proceeded: no reachability / model-missing failure was reported.
    assert "Ollama server unreachable" not in combined
    assert "is not pulled" not in combined
