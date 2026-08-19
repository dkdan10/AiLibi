"""Tests for scripts/refresh_samples.sh via subprocess.

Two families, both hermetic — no real provider is ever reached and no committed
byte is ever written:

* argument handling, provider resolution and the pre-spend preflights, driven
  with ``--dry-run`` or with a real mode that must abort at a gate;
* the RECORDING path, driven with ``AILIBI_LLM_PROVIDER=fake`` into a scratch
  dir under ``tmp_path``. That is the only provider the worker pool can be run
  end to end on, so it is what covers ``run_worker`` / ``claim_next_seed`` /
  ``_acquire_lock`` / ``record_one_seed`` and the lock-guarded MANIFEST merge.
"""

from __future__ import annotations

import contextlib
import json
import os
import re
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
    # A real (non-dry-run) anthropic mode with no key must fail at preflight,
    # before any tournament invocation -- so this test never spends, even with a
    # key configured in the ambient environment (it is stripped here). The
    # provider is named explicitly because the ambient test env pins
    # AILIBI_LLM_PROVIDER=fake (tests/conftest.py) and `fake` now resolves to the
    # hermetic provider, which has no key to preflight.
    env = _clean_env()
    env.pop("ANTHROPIC_API_KEY", None)
    env["AILIBI_LLM_PROVIDER"] = "anthropic"
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
    # the substrate provenance so the ruled slate is never silent (AGENTS.md
    # "no silent fallbacks"). Since the Task-18.12 baseline-6 record the four
    # meeting-layer levers graduated unconditional ON beside the earlier
    # graduations and impostor_roll_call stays default-OFF (the CREW-ONLY ruling),
    # so no substrate env vars are exported and the echo states the baseline-6
    # slate.
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
        "[dry-run] substrate flags: baseline-6 slate — the meeting-layer levers "
        "unconditional ON (roll_call_round, whereabouts_interior_flags, "
        "vent_placement_contradictions, absence_prior graduated at Task 18.12), "
        "impostor_roll_call default-OFF (CREW-ONLY ruling)" in proc.stdout
    )
    # Task 18.12: the dry-run also describes the new substrate-lever preflight, so
    # the ruled shipped/unshipped state the real record enforces is never silent.
    assert (
        "[dry-run] substrate-lever preflight: would require the live lever slate "
        "to equal the ruled baseline-6 state (four meeting-layer levers ON, "
        "impostor_roll_call OFF) and refuse a stale AILIBI_* export" in proc.stdout
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


def test_featherless_refresh_requires_coupled_model_before_spend() -> None:
    # Task 16.13 (PR #260 review): the qwen3_6_27b set is coupled to its locked
    # owner model (Qwen/Qwen3.6-27B). Post-16.12 the script DEFAULT matches the
    # owner model, so the guard is a pure backstop: it must still fail loud
    # AFTER the set gate and BEFORE any staging/spend when a stale env pins the
    # OLD incumbent explicitly — recording the new set against another model
    # would corrupt the substrate provenance. (The original pre-16.12 form of
    # this test relied on the un-flipped default; the 16.12 flip made that
    # premise stale — the mismatch is now exercised explicitly.)
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "featherless"
    env["AILIBI_PROMPT_SET"] = "qwen3_6_27b"
    env["FEATHERLESS_API_KEY"] = "test-key-unused"  # guard exits before any call
    env["AILIBI_LLM_MEETING_MODEL"] = "Qwen/Qwen3-32B"  # the stale incumbent
    proc = _run("--seeds", "0", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    # The SET gate passed (its error is absent); the COUPLING gate fired.
    assert "AILIBI_PROMPT_SET must be" not in out
    assert "coupled to its locked owner model" in out
    assert "Qwen/Qwen3.6-27B" in out
    assert "nothing was staged" in out


def test_featherless_coupled_model_env_passes_the_gate(tmp_path: Path) -> None:
    # The acceptance direction, hermetic (no spend): with the locked set AND
    # AILIBI_LLM_MEETING_MODEL pinned to the owner model, the coupling gate
    # passes and the run proceeds to the NEXT pre-spend gate. Which gate that
    # is depends on whether Task 16.12's production registry entry has landed:
    # before it, the refresh must fail loud at the REGISTRY gate (the client
    # would otherwise abort mid-run, after no-meeting seeds re-recorded);
    # after it, the run reaches the roster-descriptor check, here forced to
    # fail loud by a deliberately disagreeing committed roster.json. Both
    # branches prove gate order without any provider call, and the test stays
    # green across 16.12's merge (the two tasks land in parallel).
    from llm.featherless_client import _THINKING_KWARG_BY_MODEL

    set_dir = tmp_path / "set"
    set_dir.mkdir()
    (set_dir / "roster.json").write_text(
        '{"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2}'
    )
    env = _clean_env()
    env.update(
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_LLM_MEETING_MODEL="Qwen/Qwen3.6-27B",
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
    )
    proc = _run("--seeds", "0", env=env, timeout=120)
    assert proc.returncode != 0  # fails at a later pre-spend gate, not coupling
    out = proc.stdout + proc.stderr
    assert "Model-set coupling OK: qwen3_6_27b on Qwen/Qwen3.6-27B" in out
    assert "coupled to its locked owner model" not in out
    registered = any(
        model_id == "Qwen/Qwen3.6-27B" for model_id, _ in _THINKING_KWARG_BY_MODEL
    )
    if registered:
        # Post-16.12 tree: the registry gate passes; the roster gate fires.
        assert "Model registry OK" in out
        assert not set_dir.joinpath("MANIFEST.md").exists()  # no row staged
    else:
        # Pre-16.12 tree: the registry gate fires BEFORE mkdir/staging.
        assert "is not registered in" in out
        assert "nothing was staged" in out


def test_dry_run_featherless_echoes_model_set_coupling() -> None:
    # The dry-run surfaces the coupling requirement (mirroring the key-preflight
    # echo pattern) so the operator sees it before any real invocation.
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_PROMPT_SET="qwen3_6_27b",
    )
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] model-set coupling:" in proc.stdout
    assert "Qwen/Qwen3.6-27B" in proc.stdout
    assert "[dry-run] model registry:" in proc.stdout
    assert "_THINKING_KWARG_BY_MODEL" in proc.stdout


def test_featherless_refresh_accepts_locked_substrate() -> None:
    # Task 14.12 / 18.12: with the locked prompt set the substrate guard passes --
    # no lever env needed (the meeting-layer levers are unconditional since baseline
    # 6 and impostor_roll_call stays default-OFF). Use --dry-run so the test never
    # spends.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "featherless"
    env["AILIBI_PROMPT_SET"] = "qwen3_6_27b"
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] prompt set: qwen3_6_27b" in proc.stdout
    assert (
        "[dry-run] substrate flags: baseline-6 slate — the meeting-layer levers "
        "unconditional ON (roll_call_round, whereabouts_interior_flags, "
        "vent_placement_contradictions, absence_prior graduated at Task 18.12), "
        "impostor_roll_call default-OFF (CREW-ONLY ruling)" in proc.stdout
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


def test_dry_run_explicit_fake_provider_resolves_fake() -> None:
    # An EXPLICIT `fake` selects the hermetic provider (Task 20.21): it is the
    # only provider the recording path can be tested on end to end. It no longer
    # maps to anthropic; what confines it is the recording path's refusal to
    # write into the repo's replays/ tree, which the dry-run also describes.
    env = _clean_env()
    env["AILIBI_LLM_PROVIDER"] = "fake"
    proc = _run("--seeds", "22", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] provider: fake" in proc.stdout
    assert "would require no API key" in proc.stdout
    assert f"would refuse a sample dir inside {_REPO_ROOT}/replays" in proc.stdout


def test_dry_run_inherited_fake_provider_resolves_fake() -> None:
    # The inherited test env pins AILIBI_LLM_PROVIDER=fake (tests/conftest.py),
    # so it resolves to fake here too. An ambient `fake` is stopped from
    # recording over a committed set by the replays/ refusal on the RECORDING
    # path (test_fake_refresh_refuses_a_replays_target), not by a remap.
    proc = _run("--seeds", "22", "--dry-run")
    assert proc.returncode == 0
    assert "[dry-run] provider: fake" in proc.stdout


def test_dry_run_unset_or_empty_provider_resolves_anthropic() -> None:
    # The anti-silent-fake guard, unchanged: a refresh that never set the var --
    # or set it empty -- records REAL samples. Only an explicit `fake` selects
    # the hermetic provider, so no forgotten export can write fake bytes over a
    # committed set.
    env = _clean_env()
    proc = _run("--seeds", "22", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "[dry-run] provider: anthropic" in proc.stdout

    env["AILIBI_LLM_PROVIDER"] = ""
    proc = _run("--seeds", "22", "--dry-run", env=env)
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


# -- locked model literal (Task 16.12) ----------------------------------------


def test_default_featherless_model_pins_the_locked_served_id() -> None:
    # The refresh script's DEFAULT_FEATHERLESS_MODEL is the exact served id locked
    # for production (Task 16.2, audits/audit-phase-16-model-lock.md, locked
    # 2026-07-12): the un-suffixed HuggingFace repo form Qwen/Qwen3.6-27B — the
    # -Instruct variant 404s, so the un-suffixed id is the only servable form.
    # Pin the source literal against the locked id, AND against the client default
    # the script comment promises to mirror, so the shell constant can never drift
    # from either the lock or llm.featherless_client.DEFAULT_FEATHERLESS_MODEL.
    from llm.featherless_client import DEFAULT_FEATHERLESS_MODEL

    script = _REFRESH_SH.read_text(encoding="utf-8")
    match = re.search(r'^DEFAULT_FEATHERLESS_MODEL="([^"]+)"$', script, re.MULTILINE)
    assert match is not None, "DEFAULT_FEATHERLESS_MODEL constant missing from script"
    assert match.group(1) == "Qwen/Qwen3.6-27B"
    assert match.group(1) == DEFAULT_FEATHERLESS_MODEL


# -- the hermetic recording path (Task 20.21) ---------------------------------
#
# `fake` is the only provider that can drive the worker pool without spending,
# so these cases are what cover run_worker / claim_next_seed / _acquire_lock /
# record_one_seed and the lock-guarded MANIFEST merge. Every one records into a
# scratch dir under tmp_path; the script refuses a replays/ target outright.

_VERIFY_SH = _REPO_ROOT / "scripts" / "verify_samples.sh"
_WRITER_PY = _REPO_ROOT / "scripts" / "_manifest_writer.py"
_COMMITTED_4P1I = _REPO_ROOT / "replays" / "samples" / "4p1i"


def _fake_set(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    """A scratch set dir + env for a real (non-dry-run) fake-provider refresh.

    The dir is a subdir of ``tmp_path`` so the per-run staging dir (created in
    its PARENT) also lands in the temp tree. It is left uncreated: the script
    writes its own ``roster.json`` at the default 4p/1i/1-task roster, and the
    loader reconstructs from that descriptor, so a roster override passed here
    that disagreed with the run would surface as a tick-0 hash divergence.
    """

    set_dir = tmp_path / "scratch-set"
    env = _clean_env()
    env.update(
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(set_dir / "MANIFEST.md"),
    )
    return set_dir, env


def _manifest_data_rows(manifest: Path) -> list[list[str]]:
    """Every data row of a rendered MANIFEST, as its stripped cells.

    A list (not a seed-keyed dict) so a duplicated seed row stays visible
    instead of collapsing.
    """

    rows: list[list[str]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and cells[0].isdigit():
            rows.append(cells)
    return rows


def test_fake_refresh_records_seeds_end_to_end(tmp_path: Path) -> None:
    # The whole recording path, hermetically: two seeds are claimed, recorded,
    # moved into the set dir and manifested, the staging dir is discarded by the
    # EXIT trap, and the result reconstructs byte-identically under the engine.
    set_dir, env = _fake_set(tmp_path)
    proc = _run("--seeds", "0,1", env=env, timeout=600)
    combined = proc.stdout + proc.stderr
    assert proc.returncode == 0, combined
    # The abort this path used to die on under macOS's stock Bash 3.2, before the
    # lock owner PID was written as ${BASHPID:-$$}.
    assert "unbound variable" not in combined

    assert (set_dir / "replay-seed-0.jsonl").is_file()
    assert (set_dir / "replay-seed-1.jsonl").is_file()

    manifest = set_dir / "MANIFEST.md"
    rows = _manifest_data_rows(manifest)
    assert [int(cells[0]) for cells in rows] == [0, 1]
    for cells in rows:
        assert cells[1] == "fake-meeting"  # never a Sonnet/Featherless id
        assert cells[-2] == "0.0000"  # cost_usd
    assert manifest.read_text(encoding="utf-8").count("# Sample Replay Manifest") == 1

    # The EXIT trap discarded the per-run stage (created in the set dir's parent).
    assert list(tmp_path.glob(".ailibi-refresh-stage-*")) == []

    verify = subprocess.run(
        ["bash", str(_VERIFY_SH), str(set_dir)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert verify.returncode == 0, verify.stdout + verify.stderr


def test_fake_refresh_skips_the_key_preflight_but_keeps_the_substrate_one(
    tmp_path: Path,
) -> None:
    # No spend is possible on the fake provider, so there is no key to preflight
    # -- but the substrate-lever slate is a property of the GAME, not of the LLM
    # backend, so its preflight still runs unchanged. Both keys are stripped to
    # prove the run does not need them.
    set_dir, env = _fake_set(tmp_path)
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("FEATHERLESS_API_KEY", None)
    proc = _run("--seeds", "0", env=env, timeout=600)
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "ANTHROPIC_API_KEY must be set" not in out
    assert "Using API key prefix" not in out
    assert (
        "Substrate slate OK: four meeting-layer levers ON, impostor_roll_call OFF"
        in out
    )
    assert "Attributing no-meeting seeds to model: fake-meeting" in out
    assert (set_dir / "replay-seed-0.jsonl").is_file()


@contextlib.contextmanager
def _restored_afterwards(directory: Path) -> Iterator[None]:
    """Snapshot ``directory``'s files and put them back on the way out.

    The refusal cases below aim a REAL recording run at a committed set, which
    is the only way to prove the guard refuses it. Their assertions report a
    regression; this restores the bytes so a regressed guard cannot also leave
    the working tree dirty.
    """

    before = {path: path.read_bytes() for path in directory.iterdir() if path.is_file()}
    try:
        yield
    finally:
        for path in directory.iterdir():
            if path.is_file() and path not in before:
                path.unlink()
        for path, data in before.items():
            if not path.is_file() or path.read_bytes() != data:
                path.write_bytes(data)


@pytest.mark.parametrize(
    "relative_target",
    [
        "replays",
        "replays/samples/4p1i",
        "replays/samples/9p2i",
        # A `..` that leaves the tree textually and re-enters it physically: the
        # case a string-prefix form of the guard would wave through.
        "scripts/../replays/samples/4p1i",
    ],
)
def test_fake_refresh_refuses_a_replays_target(relative_target: str) -> None:
    # The guard that makes an explicit `fake` safe: committed sets are REAL
    # recordings, so fake bytes may never land in the repo's replays/ tree. The
    # refusal fires before mkdir/staging and names the dir and the rule.
    target = f"{_REPO_ROOT}/{relative_target}"
    env = _clean_env()
    env.update(
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_SAMPLE_DIR=target,
        AILIBI_MANIFEST=f"{target}/MANIFEST.md",
    )
    with _restored_afterwards(_COMMITTED_4P1I):
        proc = _run("--seeds", "0", env=env, timeout=300)
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0
        assert "may not record into the repository's replays/ tree" in out
        assert f"{_REPO_ROOT}/replays" in out  # the rule's root, physically resolved
        assert "nothing was staged" in out
        # It aborted at the provider gate: the later pre-spend gates never ran,
        # so no directory, descriptor or stage was created.
        assert "Substrate slate OK" not in out
        samples_root = _REPO_ROOT / "replays" / "samples"
        assert list(samples_root.glob(".ailibi-refresh-stage-*")) == []


def test_fake_refresh_refuses_a_symlink_into_replays(tmp_path: Path) -> None:
    # The other way a string-prefix form of this guard is defeated: a sample dir
    # that only LOOKS outside replays/. The guard compares physical paths, so the
    # symlink resolves back into the tree and the run is refused. The link points
    # at a scratch subdir of replays/samples (not a committed set), so a regressed
    # guard would record into a throwaway dir rather than over real bytes.
    decoy = _REPO_ROOT / "replays" / "samples" / ".test-symlink-decoy"
    link = tmp_path / "looks-like-scratch"
    env = _clean_env()
    env.update(
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_SAMPLE_DIR=str(link),
        AILIBI_MANIFEST=str(link / "MANIFEST.md"),
    )
    decoy.mkdir()
    link.symlink_to(decoy)
    try:
        proc = _run("--seeds", "0", env=env, timeout=300)
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0
        assert "may not record into the repository's replays/ tree" in out
        assert list(decoy.iterdir()) == []
    finally:
        shutil.rmtree(decoy)


def test_fake_refresh_bash_trace_names_the_worker_pool(tmp_path: Path) -> None:
    # Coverage proof that survives a reworded progress string: the xtrace of a
    # real run must show the four pool functions actually invoked.
    set_dir, env = _fake_set(tmp_path)
    proc = subprocess.run(
        ["bash", "-x", str(_REFRESH_SH), "--seeds", "0"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    assert proc.returncode == 0, proc.stderr[-4000:]
    assert (set_dir / "replay-seed-0.jsonl").is_file()
    for function in (
        "run_worker",
        "claim_next_seed",
        "record_one_seed",
        "_acquire_lock",
    ):
        assert re.search(rf"^\++ {function}\b", proc.stderr, re.MULTILINE), function


def test_two_workers_lose_no_manifest_row(tmp_path: Path) -> None:
    # MANIFEST.md is a whole-file read-modify-write
    # (_manifest_writer.update_manifest), so two workers updating different seeds
    # concurrently would leave one row silently missing -- and a missing row is
    # fatal at the next verify gate. The mutex around the update is what prevents
    # it; this pins that it holds. (Replays are staged per-seed and land via an
    # atomic `mv -f`, so the race could never TRUNCATE a replay: the exposure is
    # the lost row.)
    set_dir, env = _fake_set(tmp_path)
    env["AILIBI_REFRESH_WORKERS"] = "2"
    proc = _run("--seeds", "0,1,2,3", env=env, timeout=900)
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "Recording 4 seeds with 2 parallel workers" in proc.stdout

    manifest = set_dir / "MANIFEST.md"
    rows = _manifest_data_rows(manifest)
    assert [int(cells[0]) for cells in rows] == [0, 1, 2, 3]  # none lost, none doubled
    assert manifest.read_text(encoding="utf-8").count("# Sample Replay Manifest") == 1
    for seed in range(4):
        assert (set_dir / f"replay-seed-{seed}.jsonl").is_file()
        # The claim counter is lock-guarded, so no seed is recorded twice.
        assert proc.stdout.count(f"recording seed {seed} ---") == 1
    # Both workers drained from the shared queue (4 seeds at ~1s each).
    assert set(re.findall(r"--- \[worker (\d+)\] recording seed", proc.stdout)) == {
        "1",
        "2",
    }


def _update_manifest_row(sample_dir: Path, manifest: Path, seed: int) -> None:
    """One worker's lock-held MANIFEST update, exactly as the script issues it."""

    proc = subprocess.run(
        [
            "uv",
            "run",
            "python",
            str(_WRITER_PY),
            "update",
            "--seeds",
            str(seed),
            "--git-sha",
            "deadbeef",
            "--refreshed-at",
            "2026-08-19",
            "--model",
            "fake-meeting",
            "--sample-dir",
            str(sample_dir),
            "--manifest",
            str(manifest),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_unserialized_manifest_updates_lose_a_row(tmp_path: Path) -> None:
    # The perturbation proving the concurrency gate above bites: drop the
    # serialization and the same two updates lose a row. `update` parses the whole
    # manifest, merges one seed and rewrites the file, so a worker whose READ
    # happened before another worker's WRITE erases that other worker's row while
    # keeping the rows both of them read. Deterministic by construction -- the
    # stale read is replayed by restoring the bytes the second worker would have
    # read, never by racing the two calls.
    sample_dir = tmp_path / "rows"
    sample_dir.mkdir()
    for seed in (0, 12, 22):
        shutil.copy2(
            _COMMITTED_4P1I / f"replay-seed-{seed}.jsonl",
            sample_dir / f"replay-seed-{seed}.jsonl",
        )
    manifest = sample_dir / "MANIFEST.md"

    # A row already in the manifest when both workers read it.
    _update_manifest_row(sample_dir, manifest, 0)
    shared = manifest.read_text(encoding="utf-8")

    # Serialized (what the lock guarantees): both new rows land.
    _update_manifest_row(sample_dir, manifest, 12)
    _update_manifest_row(sample_dir, manifest, 22)
    assert [int(cells[0]) for cells in _manifest_data_rows(manifest)] == [0, 12, 22]

    # Unserialized: worker B read before worker A wrote.
    manifest.write_text(shared, encoding="utf-8")
    _update_manifest_row(sample_dir, manifest, 12)  # A: reads {0}, writes {0,12}
    manifest.write_text(shared, encoding="utf-8")  # B's read predates A's write
    _update_manifest_row(sample_dir, manifest, 22)  # B: merges into {0}, writes {0,22}
    # The row both workers read survives; the row only A wrote is gone.
    assert [int(cells[0]) for cells in _manifest_data_rows(manifest)] == [0, 22]


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="mode 0555 does not block a write as root",
)
def test_fake_refresh_fails_loud_when_a_replay_cannot_land(tmp_path: Path) -> None:
    # record_one_seed's fail-loud branch, driven by a deterministic injected
    # failure: the set dir is read-only, so the game records into the writable
    # stage and the atomic `mv -f` into the set dir fails. The refresh must exit
    # non-zero with the "must NOT be committed" verdict rather than reporting a
    # partial baseline as complete. The descriptor is pre-written and AGREES, so
    # the roster gate no-ops and the failure lands where it is aimed.
    set_dir, env = _fake_set(tmp_path)
    set_dir.mkdir()
    (set_dir / "roster.json").write_text(
        '{"num_players": 4, "num_impostors": 1, "tasks_per_crewmate": 1}',
        encoding="utf-8",
    )
    set_dir.chmod(0o555)
    try:
        proc = _run("--seeds", "0", env=env, timeout=600)
    finally:
        set_dir.chmod(0o755)
    out = proc.stdout + proc.stderr
    assert proc.returncode == 1, out
    assert "seed 0 replay move failed" in out
    assert "the baseline is INCOMPLETE and must NOT be committed" in out
    assert not (set_dir / "replay-seed-0.jsonl").exists()
    # No row is written for a seed that never landed.
    assert not (set_dir / "MANIFEST.md").exists()
    assert list(tmp_path.glob(".ailibi-refresh-stage-*")) == []


def test_lock_owner_pid_tolerates_an_undefined_bashpid() -> None:
    # macOS ships Bash 3.2, which predates $BASHPID, and the script runs under
    # `set -u`: a bare "$BASHPID" aborts the FIRST seed claim with
    # "BASHPID: unbound variable", before any provider call -- so every refresh on
    # the stock host interpreter died there. ${BASHPID:-$$} is exempt from set -u;
    # on 3.2 every worker then shares $$, so dead-owner detection degrades to a
    # no-op while the mkdir mutex still serializes correctly (the same accepted
    # limitation the corpus recorder records; audits/audit-phase-18-close.md §7
    # row 5, training/README.md §6 row 5). The end-to-end cases above run this
    # path under the host bash, which is what bites on 3.2; this source pin bites
    # on every interpreter, including the Bash 5 CI runs where a bare $BASHPID
    # would be perfectly defined.
    script = _REFRESH_SH.read_text(encoding="utf-8")
    assert 'printf \'%s\' "${BASHPID:-$$}" >"$_lockdir/owner"' in script
    code = "\n".join(
        line
        for line in script.splitlines()
        if not line.lstrip().startswith("#")  # the comment above names $BASHPID
    )
    assert "$BASHPID" not in code.replace("${BASHPID:-$$}", "")


def test_default_fake_model_mirrors_the_fake_client() -> None:
    # A fake row must be attributable as a fake row: the shell constant used for
    # MANIFEST attribution is pinned against the id the fake client actually
    # reports, so a hermetic recording can never render as a real-model row.
    from llm.fake_provider import _FAKE_MEETING_MODEL

    script = _REFRESH_SH.read_text(encoding="utf-8")
    match = re.search(r'^DEFAULT_FAKE_MODEL="([^"]+)"$', script, re.MULTILINE)
    assert match is not None, "DEFAULT_FAKE_MODEL constant missing from script"
    assert match.group(1) == _FAKE_MEETING_MODEL
