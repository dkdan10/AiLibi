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
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import uuid
from collections.abc import Iterator, Sequence
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import MappingProxyType

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

import _declared_experiment as de
from eval.eras import BASELINE_9, COMMITTED_SETS, CommittedSet
from api.replay_loader import ReplayLoader
from meetings.evidence_profile import EXPERIMENT_ENV_NAMES
from orchestrator.experiment_config import RecordedExperimentConfig
from orchestrator.replay import GameEndReplayEntry, ReplayEntry, read_all_entries

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
    # Meeting-bearing seeds derived from the committed flat MANIFEST.md: the
    # baseline-8 record carries a meeting on 39/50 flat 4p/1i seeds
    # (baseline 7 carried 40 — seed 3 goes meeting-free on the new bytes).
    assert (  # was 1,2,3,4,5,6,7,9,10,11,13,14,16,…  (40 seeds, seed 3 included)
        "[dry-run] seeds: 1,2,4,5,6,7,9,10,11,13,14,16,17,18,19,"
        "20,21,22,23,24,26,27,28,29,32,33,35,36,38,39,40,41,42,44,45,46,47,48,49"
        in proc.stdout
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
    # AILIBI_LLM_PROVIDER=featherless is an accepted provider; the dry-run echoes
    # it, its FEATHERLESS_API_KEY preflight, the prompt set, and the expected
    # lever slate, so the substrate an operator is about to record is never
    # silent (AGENTS.md "no silent fallbacks").
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
    assert _BARE_SLATE_ECHO in proc.stdout
    assert _PREFLIGHT_ECHO in proc.stdout


# The two dry-run lines that describe the substrate. The slate is a property of
# the GAME, not of the LLM backend, so both print for every provider.
_BARE_SLATE_ECHO = (
    "[dry-run] substrate flags: expected levers ON = (none — the bare slate: "
    "every live toggle OFF); every other live toggle OFF; the graduated levers "
    "unconditional ON"
)
_PREFLIGHT_ECHO = (
    "[dry-run] substrate-lever preflight: would require the live lever slate to "
    "equal that expectation exactly and refuse before any seed stages"
)


@pytest.mark.parametrize("provider", ["anthropic", "ollama", "featherless"])
def test_dry_run_echoes_the_expected_slate_for_every_provider(provider: str) -> None:
    # The echo used to sit inside the featherless branch while the check it
    # describes runs outside every provider block, so an operator previewing an
    # anthropic or ollama refresh was told nothing about the gate that would
    # refuse them. Both lines now print for all three.
    env = dict(_clean_env(), AILIBI_LLM_PROVIDER=provider)
    proc = _run("--seeds", "0", "--dry-run", env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert _BARE_SLATE_ECHO in proc.stdout
    assert _PREFLIGHT_ECHO in proc.stdout


@pytest.mark.parametrize("provider", ["anthropic", "ollama", "featherless"])
def test_dry_run_echo_names_the_levers_the_operator_declared(provider: str) -> None:
    # And the echo quotes the RESOLVED slate rather than a hard-coded sentence,
    # so the preview and the gate can never describe different substrates.
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER=provider,
        AILIBI_IMPOSTOR_ROLL_CALL="1",
        AILIBI_SELF_LOCATION_TRAIL="1",
    )
    proc = _run(
        "--seeds",
        "0",
        "--dry-run",
        "--expect-levers",
        "grounded_prosecution,self_location_trail",
        env=env,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert (
        "[dry-run] substrate flags: expected levers ON = "
        "grounded_prosecution,self_location_trail" in proc.stdout
    )


def test_expect_levers_requires_an_argument() -> None:
    # A --expect-levers with NOTHING after it is an operator typo: the value was
    # meant to be there and got lost, so refusing beats silently recording the
    # bare substrate under a flag that claims otherwise.
    proc = _run("--seeds", "0", "--dry-run", "--expect-levers")
    assert proc.returncode != 0
    assert "--expect-levers requires a comma-separated lever list" in (
        proc.stdout + proc.stderr
    )


def test_an_explicitly_empty_expect_levers_is_the_bare_slate() -> None:
    # An empty STRING is a declaration, not a typo: automation can pass
    # --expect-levers "$LEVERS" unconditionally and get the bare slate when the
    # variable is unset. The two cases are distinguished by whether an argument
    # follows the flag at all.
    proc = _run("--seeds", "0", "--dry-run", "--expect-levers", "", env=_clean_env())
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "Substrate slate OK: expected levers ON = (none" in out


def test_preflight_refuses_a_declared_lever_that_is_not_exported() -> None:
    # Direction 1 -- the failure a blacklist of variable names cannot catch. The
    # operator declared a lever the shell never exported, so every seed would be
    # recorded on the OLD substrate while the echo claims the new one.
    env = _clean_env()
    proc = _run(
        "--seeds", "0", "--dry-run", "--expect-levers", "impostor_roll_call", env=env
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "does not match --expect-levers" in out
    assert "impostor_roll_call must be ON" in out
    assert "AILIBI_IMPOSTOR_ROLL_CALL" in out


def test_preflight_refuses_an_export_nobody_declared() -> None:
    # Direction 2 -- a stale export from an earlier probe session would ship an
    # unruled arm into the record, and an acceptance gate run in the same shell
    # would pass coherently because it reads the same environment.
    env = dict(_clean_env(), AILIBI_IMPOSTOR_ROLL_CALL="1")
    proc = _run("--seeds", "0", "--dry-run", env=env)
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "impostor_roll_call must be OFF" in out


def test_preflight_refuses_a_typo_in_the_declared_slate() -> None:
    # An expectation nobody can check is worse than no expectation: a misspelled
    # key must fail loud rather than be silently ignored.
    proc = _run("--seeds", "0", "--dry-run", "--expect-levers", "grounded_prosecutions")
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "is not a lever in the registry" in out


def test_preflight_accepts_the_declared_slate_when_the_environment_matches() -> None:
    # The gate must be passable, or it is not a gate: with exactly the declared
    # levers exported the preflight reports the resolved slate and continues.
    env = dict(_clean_env(), AILIBI_IMPOSTOR_ROLL_CALL="1")
    proc = _run(
        "--seeds", "0", "--dry-run", "--expect-levers", "impostor_roll_call", env=env
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "Substrate slate OK: expected levers ON = impostor_roll_call" in out


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
    assert _BARE_SLATE_ECHO in proc.stdout


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
    assert (
        f"would refuse a sample dir or manifest inside {_REPO_ROOT}/replays"
        in proc.stdout
    )


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
    assert "Substrate slate OK: expected levers ON = (none" in out
    # The real run's provenance echo renders the SAME resolved slate the preview
    # and the gate name, so an operator can never read three different substrates.
    assert (
        "Substrate flags: expected levers ON = (none — the bare slate: every "
        "live toggle OFF); every other live toggle OFF; the graduated levers "
        "unconditional ON" in out
    )
    assert "Attributing no-meeting seeds to model: fake-meeting" in out
    assert (set_dir / "replay-seed-0.jsonl").is_file()


# The only names a `--seeds 0` refresh writes into its target dir: the replay,
# the roster descriptor, the manifest, the rebuilt eval report and (9p2i only)
# the rubric. Restoring exactly these keeps the guard below honest without
# reading every committed replay on every case.
_REFRESH_OUTPUT_NAMES = (
    "replay-seed-0.jsonl",
    "roster.json",
    "MANIFEST.md",
    "tournament-eval-report.json",
    "results-rubric-score.json",
)
# A refused run must never create this; the `..` cases point through it.
_STRAY_TARGET_ROOT = _REPO_ROOT / "not-a-real-dir"


@contextlib.contextmanager
def _replays_tree_restored() -> Iterator[None]:
    """Put the committed tree back if a refused run turns out not to be refused.

    The refusal cases below aim a REAL recording run at the committed tree,
    which is the only way to prove the guard refuses it. Their assertions report
    a regression; this undoes the damage, so a regressed guard cannot also leave
    the repository dirty. It takes a recursive inventory of ``replays/`` and
    removes anything new (files and directories alike, deepest first), and keeps
    the bytes of the files a refresh would overwrite in any of the directories
    these cases name.
    """

    replays = _REPO_ROOT / "replays"
    targets = [replays, replays / "samples" / "4p1i", replays / "samples" / "9p2i"]
    inventory = set(replays.rglob("*"))
    contents: dict[Path, bytes] = {}
    for directory in targets:
        for name in _REFRESH_OUTPUT_NAMES:
            path = directory / name
            if path.is_file():
                contents[path] = path.read_bytes()
    try:
        yield
    finally:
        strays = sorted(
            (path for path in replays.rglob("*") if path not in inventory),
            key=lambda path: len(path.parts),
            reverse=True,  # children before their parents
        )
        for path in strays:
            if path.is_dir() and not path.is_symlink():
                path.rmdir()
            else:
                path.unlink()
        for path, data in contents.items():
            if not path.is_file() or path.read_bytes() != data:
                path.write_bytes(data)
        if _STRAY_TARGET_ROOT.exists():
            shutil.rmtree(_STRAY_TARGET_ROOT)


@pytest.mark.parametrize(
    "relative_target",
    [
        "replays",
        "replays/samples/4p1i",
        "replays/samples/9p2i",
        # A `..` that leaves the tree textually and re-enters it physically: the
        # case a string-prefix form of the guard would wave through.
        "scripts/../replays/samples/4p1i",
        # The same trick behind a component that does not exist yet, which the
        # kernel cannot resolve but `mkdir -p` would create on the way in.
        "not-a-real-dir/../replays/samples/new-set",
    ],
)
def test_fake_refresh_refuses_a_replays_target(relative_target: str) -> None:
    # The guard that makes an explicit `fake` safe: committed sets are REAL
    # recordings, so fake bytes may never land in the repo's replays/ tree. The
    # refusal fires before mkdir/staging and names the path and the rule.
    target = f"{_REPO_ROOT}/{relative_target}"
    env = _clean_env()
    env.update(
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_SAMPLE_DIR=target,
        AILIBI_MANIFEST=f"{target}/MANIFEST.md",
    )
    # The promoted 9p2i set records only its era's declared config, so the run
    # declares it: the era rule passes and the provider gate is what refuses.
    era = (
        ("--experiment-config", str(_ERA_CONFIG))
        if relative_target == "replays/samples/9p2i"
        else ()
    )
    with _replays_tree_restored():
        proc = _run("--seeds", "0", *era, env=env, timeout=300)
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0
        assert "may not write into the repository's replays/ tree" in out
        assert f"{_REPO_ROOT}/replays" in out  # the rule's root, physically resolved
        assert "nothing was staged" in out
        # It aborted at the provider gate: the later pre-spend gates never ran,
        # so no directory, descriptor or stage was created.
        assert "Substrate slate OK" not in out
        samples_root = _REPO_ROOT / "replays" / "samples"
        assert list(samples_root.glob(".ailibi-refresh-stage-*")) == []
        # The `..` cases must not create their leading component on the way in
        # (asserted inside the block, before the cleanup would remove it).
        assert not _STRAY_TARGET_ROOT.exists()


def test_fake_refresh_refuses_a_manifest_inside_replays(tmp_path: Path) -> None:
    # AILIBI_MANIFEST is configurable independently of AILIBI_SAMPLE_DIR, so a
    # scratch sample dir alone does not make a fake run safe: the manifest writer
    # would rewrite a committed MANIFEST's rows from the scratch replays. Both
    # outputs are guarded, and the error names which one offended.
    set_dir = tmp_path / "scratch-set"
    env = _clean_env()
    env.update(
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_SAMPLE_DIR=str(set_dir),
        AILIBI_MANIFEST=str(_COMMITTED_4P1I / "MANIFEST.md"),
    )
    with _replays_tree_restored():
        proc = _run("--seeds", "0", env=env, timeout=300)
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0
        assert "may not write into the repository's replays/ tree" in out
        assert "(from AILIBI_MANIFEST)" in out
        assert "nothing was staged" in out
        assert not set_dir.exists()  # refused before the target dir was created


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
        assert "may not write into the repository's replays/ tree" in out
        assert list(decoy.iterdir()) == []
    finally:
        shutil.rmtree(decoy)


def test_fake_refresh_refuses_a_symlink_revealed_by_normalization(
    tmp_path: Path,
) -> None:
    # The two evasions COMPOSED, which each one alone does not catch: a `..`
    # behind a component that does not exist yet, collapsing onto a symlink that
    # points into replays/. Resolving once and normalizing once leaves the
    # symlink unresolved, so the guard has to run both steps to a fixed point.
    # Again aimed at a throwaway subdir, so a regression costs nothing.
    decoy = _REPO_ROOT / "replays" / "samples" / ".test-composed-decoy"
    link = tmp_path / "samples-link"
    target = f"{tmp_path}/not-there/../samples-link/new-set"
    env = _clean_env()
    env.update(
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_SAMPLE_DIR=target,
        AILIBI_MANIFEST=f"{target}/MANIFEST.md",
    )
    decoy.mkdir()
    link.symlink_to(decoy)
    try:
        proc = _run("--seeds", "0", env=env, timeout=300)
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0
        assert "may not write into the repository's replays/ tree" in out
        assert str(decoy) in out  # resolved all the way through the symlink
        assert list(decoy.iterdir()) == []
        assert not (tmp_path / "not-there").exists()
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
    # WHICH worker drains which seed is up to the scheduler, so asserting a
    # particular split would be a timing assumption. What is pinned instead is
    # what holds under every split: every seed was claimed by a worker of the
    # spawned pool, exactly once, and the manifest kept a row for each.
    claims = re.findall(r"--- \[worker (\d+)\] recording seed", proc.stdout)
    assert len(claims) == 4
    assert set(claims) <= {"1", "2"}


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


# Two real processes calling the real ``update_manifest`` with their critical
# sections deliberately overlapped: each reads the manifest, then waits until
# BOTH have read and merged, and only then writes. Two handshakes, no sleeps —
# `late` additionally waits for `early`'s write to have COMPLETED, so the write
# order is established by observation rather than by timing and a descheduled
# process cannot reorder them. This is what the refresh script's mutex prevents,
# expressed without it.
_RACE_DRIVER = """
import sys
import time
from pathlib import Path

scripts_dir, role, manifest, sample_dir, seed, barrier_dir = sys.argv[1:]
sys.path.insert(0, scripts_dir)
import _manifest_writer as mw

barrier = Path(barrier_dir)
render_merged = mw.render_manifest


def await_signal(predicate, what):
    deadline = time.monotonic() + 60
    while not predicate():
        if time.monotonic() > deadline:
            raise SystemExit("timed out waiting for " + what + " in role " + role)
        time.sleep(0.01)


def signal(name):
    (barrier / name).write_text("1", encoding="utf-8")


def gated_render(rows):
    # Reached after update_manifest has read the manifest and merged this seed,
    # and evaluated before _atomic_write_text runs -- exactly the seam the lock
    # covers in the recorder.
    text = render_merged(rows)
    signal(role + ".read")
    await_signal(lambda: len(list(barrier.glob("*.read"))) == 2, "both reads")
    if role == "late":
        await_signal(lambda: (barrier / "early.wrote").exists(), "early's write")
    return text


mw.render_manifest = gated_render
mw.update_manifest(
    Path(manifest),
    Path(sample_dir),
    [int(seed)],
    git_sha="deadbeef",
    refreshed_at="2026-08-19",
    model_override="fake-meeting",
)
signal(role + ".wrote")
"""


def test_unserialized_manifest_updates_lose_a_row(tmp_path: Path) -> None:
    # The perturbation proving the concurrency gate above bites. `update_manifest`
    # parses the whole manifest, merges one seed and atomically replaces the file,
    # so two processes whose read-merge-write windows overlap keep only the later
    # writer's row. Run for real, in two processes, with the overlap forced by a
    # barrier at the read/write seam and the write order established by waiting
    # for the first write to land -- so the outcome is fixed by observation, not
    # by timing, while the race itself is genuine.
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
    serialized_start = manifest.read_text(encoding="utf-8")

    # Serialized (what the lock guarantees): both new rows land.
    _update_manifest_row(sample_dir, manifest, 12)
    _update_manifest_row(sample_dir, manifest, 22)
    assert [int(cells[0]) for cells in _manifest_data_rows(manifest)] == [0, 12, 22]

    # Unserialized: the same two updates, run concurrently with overlapping
    # critical sections.
    manifest.write_text(serialized_start, encoding="utf-8")
    driver = tmp_path / "race_driver.py"
    driver.write_text(_RACE_DRIVER, encoding="utf-8")
    barrier = tmp_path / "barrier"
    barrier.mkdir()
    processes = [
        subprocess.Popen(
            [
                "uv",
                "run",
                "python",
                str(driver),
                str(_REPO_ROOT / "scripts"),
                role,
                str(manifest),
                str(sample_dir),
                str(seed),
                str(barrier),
            ],
            cwd=_REPO_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for role, seed in (("early", 12), ("late", 22))
    ]
    for process in processes:
        _, stderr = process.communicate(timeout=300)
        assert process.returncode == 0, stderr

    # Both readers saw {0}; the later writer's file is what survives, so the row
    # the earlier writer added is gone while the row both of them read remains.
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


# -- the lock's dead-owner verdict ---------------------------------------------
#
# _acquire_lock's liveness probe (cat owner, then kill -0) inherently races the
# holder's release: a holder that releases the lock and exits between the two
# steps (a worker draining the queue, or a seed-claim command-substitution
# subshell whose pid dies with the claim) probes as dead even though it finished
# cleanly. The lock therefore requires the SAME dead pid to stay the recorded
# owner across consecutive polls before declaring death -- a truly dead holder
# leaves the owner file frozen, while a released lock is gone on the next poll.
# These cases drive the script's own lock functions, extracted verbatim, so they
# bite on the committed implementation rather than a copy.

_LOCK_DRIVER = """\
set -euo pipefail
stage_dir="$1"
_lockdir="$stage_dir/.lock"
{functions}
if _acquire_lock; then
  echo ACQUIRED
  _release_lock
else
  echo REFUSED
  exit 1
fi
"""


def _lock_driver(tmp_path: Path) -> Path:
    """A driver script around the committed _acquire_lock/_release_lock."""

    script = _REFRESH_SH.read_text(encoding="utf-8")
    functions = []
    for pattern in (
        r"(?ms)^_acquire_lock\(\) \{\n.*?\n\}$",
        r"(?m)^_release_lock\(\) \{ .*\}$",
    ):
        match = re.search(pattern, script)
        assert match is not None, f"lock function not found: {pattern}"
        functions.append(match.group(0))
    driver = tmp_path / "lock_driver.sh"
    driver.write_text(
        _LOCK_DRIVER.format(functions="\n".join(functions)), encoding="utf-8"
    )
    return driver


def _reaped_pid() -> str:
    """The pid of a process that has already exited and been reaped."""

    proc = subprocess.run(
        ["bash", "-c", "echo $$"], capture_output=True, text=True, timeout=60
    )
    assert proc.returncode == 0
    return proc.stdout.strip()


def test_lock_fails_loud_when_a_dead_owner_stays_the_owner(tmp_path: Path) -> None:
    # The safety net the stability window must NOT lose: a holder SIGKILLed/OOMed
    # mid-critical-section leaves the mkdir lock held forever, and every waiter
    # would spin while the parent hangs in `wait`. A lock whose recorded owner is
    # dead and never released must be refused, flagged in .failed, and named --
    # and only after the streak of polls, never on a single probe.
    stage = tmp_path / "stage"
    lockdir = stage / ".lock"
    lockdir.mkdir(parents=True)
    (lockdir / "owner").write_text(_reaped_pid(), encoding="utf-8")
    start = time.monotonic()
    proc = subprocess.run(
        ["bash", str(_lock_driver(tmp_path)), str(stage)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "REFUSED" in proc.stdout
    assert "died holding the lock" in proc.stderr
    assert (stage / ".failed").exists()
    # The verdict took at least the confirmation window (10 polls x 0.1s sleep);
    # an instant verdict would mean the single-probe race is back.
    assert time.monotonic() - start >= 0.5


def test_lock_tolerates_a_release_racing_the_dead_owner_probe(tmp_path: Path) -> None:
    # A dead owner pid may belong to a holder that RELEASED the lock and
    # finished between the waiter's cat and its kill -0 -- a clean handoff, not
    # a corpse, and it must not fail the refresh. The waiter here provably
    # probes the dead owner first (gated on the xtrace showing kill -0), then
    # the lock is released out from under it; the waiter must acquire and flag
    # nothing. (Pins the task 20.21 CI flake seen on PRs #369/#372/#378.)
    stage = tmp_path / "stage"
    lockdir = stage / ".lock"
    lockdir.mkdir(parents=True)
    dead = _reaped_pid()
    (lockdir / "owner").write_text(dead, encoding="utf-8")
    trace = tmp_path / "trace.txt"
    probe = re.compile(rf"kill -0 {dead}\b")
    with (
        trace.open("w", encoding="utf-8") as trace_fh,
        subprocess.Popen(
            ["bash", "-x", str(_lock_driver(tmp_path)), str(stage)],
            stdout=subprocess.PIPE,
            stderr=trace_fh,
            text=True,
        ) as proc,
    ):
        # On any failure below the waiter may still be spinning on the held
        # lock, and Popen.__exit__ waits for it unboundedly -- kill it so the
        # gate reports the failure instead of hanging.
        try:
            deadline = time.monotonic() + 60
            while not probe.search(trace.read_text(encoding="utf-8")):
                assert time.monotonic() < deadline, "waiter never probed the dead owner"
                assert proc.poll() is None, (
                    "waiter exited on a single dead probe: "
                    + trace.read_text(encoding="utf-8")
                )
                time.sleep(0.01)
            shutil.rmtree(lockdir)  # the release the probe raced
            stdout, _ = proc.communicate(timeout=60)
        except BaseException:
            proc.kill()
            raise
    assert proc.returncode == 0, stdout + trace.read_text(encoding="utf-8")
    assert "ACQUIRED" in stdout
    assert not (stage / ".failed").exists()


def test_default_fake_model_mirrors_the_fake_client() -> None:
    # A fake row must be attributable as a fake row: the shell constant used for
    # MANIFEST attribution is pinned against the id the fake client actually
    # reports, so a hermetic recording can never render as a real-model row.
    from llm.fake_provider import _FAKE_MEETING_MODEL

    script = _REFRESH_SH.read_text(encoding="utf-8")
    match = re.search(r'^DEFAULT_FAKE_MODEL="([^"]+)"$', script, re.MULTILINE)
    assert match is not None, "DEFAULT_FAKE_MODEL constant missing from script"
    assert match.group(1) == _FAKE_MEETING_MODEL


# -- the declared experiment config (--experiment-config) ---------------------
#
# scripts/_declared_experiment.py holds the three rules the recorder applies
# before any preflight or staging: the file, the meeting-experiment
# environment, and the target a switched-on config may record into.

#: The declared test config: three arms that exist today, since the pending
#: guard refuses the wave's new values.
_TEST_CONFIG_JSON = (
    '{"format_version": 1, "meeting_reset": "hub_with_grace", '
    '"vent_exit_policy": "observed_risk", "bounded_rebuttal_version": 1}\n'
)
_TEST_CONFIG = RecordedExperimentConfig.model_validate_json(_TEST_CONFIG_JSON)
_TEST_SETTINGS_ECHO = (
    "Experiment config settings: meeting_reset='hub_with_grace', "
    "vent_exit_policy='observed_risk', bounded_rebuttal_version=1"
)
#: Today's per-seed line, byte for byte: the recorder's seven flags.
_SEVEN_FLAG_LINE = (
    "[dry-run]   AILIBI_LLM_PROVIDER=anthropic uv run python "
    "scripts/run_tournament.py --start-seed <seed> --num-games 1 --output-dir "
    "<stage> --num-players 4 --num-impostors 1 --tasks-per-crewmate 1 --force"
)
_NOTHING_STAGED = "Nothing was staged."

#: The promoted 9p2i set's era config, the one file a run into that set may carry.
_ERA_CONFIG = _REPO_ROOT / "replays" / "samples" / "9p2i" / "experiment-config.json"
#: Candidate round 1's config, a real switched-on config of another round.
_ROUND_1_CONFIG = (
    _REPO_ROOT / "replays" / "candidates" / "stage-b-r1" / "experiment-config.json"
)
#: The era rule's refusal, as it names the promoted set.
_ERA_REFUSAL = "inside the committed set replays/samples/9p2i, whose recordings"
#: The era registry with no declared config anywhere: the planted repositories
#: below exercise the canonical-tree rule alone, and the era rule has its own
#: cases (``test_a_committed_set_records_only_its_eras_declared_config``).
_CANONICAL_RULE_ONLY = tuple(
    CommittedSet(entry.path, BASELINE_9) for entry in COMMITTED_SETS
)


def _era_outcome(
    config_path: Path | None, target: Path, manifest: Path | None = None
) -> str | None:
    """The real repository's verdict on a run carrying ``config_path`` into ``target``."""

    config = (
        None
        if config_path is None
        else RecordedExperimentConfig.model_validate_json(config_path.read_bytes())
    )
    sha = (
        None
        if config_path is None
        else hashlib.sha256(config_path.read_bytes()).hexdigest()
    )
    try:
        de.refuse_unsafe_target(
            config,
            sample_dir=target,
            manifest=manifest if manifest is not None else target / "MANIFEST.md",
            sample_dir_explicit=True,
            config_sha256=sha,
        )
    except de.DeclaredExperimentError as exc:
        return str(exc)
    return None


def test_a_committed_set_records_only_its_eras_declared_config(
    tmp_path: Path,
) -> None:
    """Planted: every config but the era's own is refused at the promoted set.

    The era's declared file passes there and nowhere else committed; a bare run,
    round 1's config and the era config with one byte changed are refused by
    the era rule, and the era config aimed at the 4p1i sample or the corpus is
    refused by the canonical-tree rule.
    """

    samples_9 = _REPO_ROOT / "replays" / "samples" / "9p2i"
    assert _era_outcome(_ERA_CONFIG, samples_9) is None
    for refused in (None, _ROUND_1_CONFIG):
        outcome = _era_outcome(refused, samples_9) or ""
        assert _ERA_REFUSAL in outcome, refused
        assert outcome.endswith(_NOTHING_STAGED)
    changed = tmp_path / "experiment-config.json"
    era_bytes = _ERA_CONFIG.read_bytes()
    changed.write_bytes(
        era_bytes.replace(b'"format_version": 1', b'"format_version":1')
    )
    assert changed.read_bytes() != era_bytes
    assert RecordedExperimentConfig.model_validate_json(
        changed.read_bytes()
    ) == RecordedExperimentConfig.model_validate_json(era_bytes)
    assert _ERA_REFUSAL in (_era_outcome(changed, samples_9) or "")
    assert "inside replays/samples/" in (
        _era_outcome(_ERA_CONFIG, _REPO_ROOT / "replays" / "samples" / "4p1i") or ""
    )
    assert "inside replays/ml_corpus/" in (
        _era_outcome(_ERA_CONFIG, _REPO_ROOT / "replays" / "ml_corpus" / "9p2i") or ""
    )
    # Its own directory only, with its manifest directly inside it.
    assert "below the committed set replays/samples/9p2i" in (
        _era_outcome(_ERA_CONFIG, samples_9 / "nested") or ""
    )
    assert "below the committed set replays/samples/9p2i" in (
        _era_outcome(_ERA_CONFIG, samples_9, samples_9 / "nested" / "MANIFEST.md") or ""
    )
    # A scratch directory outside replays/ keeps the candidate rules.
    scratch = tmp_path / "scratch-set"
    assert _era_outcome(_ERA_CONFIG, scratch) is None


def test_a_set_whose_declared_config_is_missing_refuses_by_name(
    tmp_path: Path,
) -> None:
    """Planted: a checkout whose promoted set lost its declared file."""

    target = tmp_path / "repo" / "replays" / "samples" / "9p2i"
    target.mkdir(parents=True)
    with pytest.raises(de.DeclaredExperimentError) as refused:
        de.refuse_unsafe_target(
            _TEST_CONFIG,
            sample_dir=target,
            manifest=target / "MANIFEST.md",
            sample_dir_explicit=True,
            repo_root=tmp_path / "repo",
            config_sha256="0" * 64,
        )
    assert "declared config replays/samples/9p2i/experiment-config.json is missing" in (
        str(refused.value)
    )


def test_the_era_verdict_follows_the_declared_file_on_disk(tmp_path: Path) -> None:
    """Planted: a checkout whose promoted set declares different valid bytes.

    The rule reads the declared file's sha256 from disk, never a remembered
    value: with the scratch file's own sha256 the run passes, and with round 2's
    sha256 (the committed file's) the same run is refused.
    """

    repo = tmp_path / "repo"
    target = repo / "replays" / "samples" / "9p2i"
    target.mkdir(parents=True)
    era_bytes = _ERA_CONFIG.read_bytes()
    moved = era_bytes.replace(b'"look_and_wait"', b'"observed_risk"')
    assert moved != era_bytes
    (target / "experiment-config.json").write_bytes(moved)
    config = RecordedExperimentConfig.model_validate_json(moved)
    assert config.vent_exit_policy == "observed_risk"

    def verdict(sha: str) -> str | None:
        try:
            de.refuse_unsafe_target(
                config,
                sample_dir=target,
                manifest=target / "MANIFEST.md",
                sample_dir_explicit=True,
                repo_root=repo,
                config_sha256=sha,
            )
        except de.DeclaredExperimentError as exc:
            return str(exc)
        return None

    assert verdict(hashlib.sha256(moved).hexdigest()) is None
    round_2 = hashlib.sha256(era_bytes).hexdigest()
    assert round_2 == "0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b"
    assert _ERA_REFUSAL in (verdict(round_2) or "")


def _era_dry_run(*extra: str) -> subprocess.CompletedProcess[str]:
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR="replays/samples/9p2i",
        AILIBI_MANIFEST="replays/samples/9p2i/MANIFEST.md",
        AILIBI_NUM_PLAYERS="9",
        AILIBI_NUM_IMPOSTORS="2",
        AILIBI_TASKS_PER_CREWMATE="2",
    )
    return _run("--dry-run", "--seeds", "0", "--expect-levers", "", *extra, env=env)


def test_the_era_config_passes_the_dry_run_into_the_promoted_set() -> None:
    before = _git_status()
    proc = _era_dry_run("--experiment-config", str(_ERA_CONFIG))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    sha = hashlib.sha256(_ERA_CONFIG.read_bytes()).hexdigest()
    lines = proc.stdout.splitlines()
    assert f"[dry-run] Experiment config: {_ERA_CONFIG} (sha256 {sha})" in lines
    # The rubric step skips an era the extractor does not read, by name.
    assert any(
        line.startswith("[dry-run] interestingness rubric: would skip it")
        and "ships no rubric" in line
        for line in lines
    )
    assert not any("would regenerate" in line and "rubric" in line for line in lines)
    assert _git_status() == before


def test_a_bare_dry_run_into_the_promoted_set_is_refused() -> None:
    before = _git_status()
    proc = _era_dry_run()
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert _ERA_REFUSAL in proc.stderr
    assert _NOTHING_STAGED in proc.stderr
    assert "[dry-run]" not in proc.stdout
    assert _git_status() == before


def _test_config(tmp_path: Path, text: str = _TEST_CONFIG_JSON) -> Path:
    path = tmp_path / "experiment-config.json"
    path.write_text(text, encoding="utf-8")
    return path


def _git_status() -> str:
    return subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _stage_dirs() -> list[Path]:
    return sorted((_REPO_ROOT / "replays").rglob(".ailibi-refresh-stage-*"))


def test_the_dry_run_echoes_the_config_and_stages_nothing(tmp_path: Path) -> None:
    config = _test_config(tmp_path)
    set_dir = tmp_path / "scratch-set"
    env = _clean_env()
    env.update(
        AILIBI_SAMPLE_DIR=str(set_dir), AILIBI_MANIFEST=str(set_dir / "MANIFEST.md")
    )
    before = _git_status()
    proc = _run(
        "--seeds",
        "0,1",
        "--dry-run",
        "--expect-levers",
        "",
        "--experiment-config",
        str(config),
        env=env,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    sha = hashlib.sha256(config.read_bytes()).hexdigest()
    lines = proc.stdout.splitlines()
    assert f"[dry-run] Experiment config: {config} (sha256 {sha})" in lines
    assert f"[dry-run] {_TEST_SETTINGS_ECHO}" in lines
    assert "[dry-run] Experiment switch exports: none" in lines
    assert (
        _SEVEN_FLAG_LINE + " --experiment-config <stage-dir>/experiment-config.json"
    ) in lines
    assert any(
        line.startswith("[dry-run] experiment config: would copy") and sha in line
        for line in lines
    )
    assert not set_dir.exists()
    assert sorted(tmp_path.iterdir()) == [config]
    assert _git_status() == before


def test_without_the_flag_the_per_seed_line_is_todays_seven_flag_line() -> None:
    proc = _run("--seeds", "0,1", "--dry-run", "--expect-levers", "", env=_clean_env())
    assert proc.returncode == 0, proc.stdout + proc.stderr
    lines = proc.stdout.splitlines()
    assert [line for line in lines if "run_tournament.py" in line] == [_SEVEN_FLAG_LINE]
    assert (
        "[dry-run] Experiment config: none declared; the recording keeps the "
        "historical defaults"
    ) in lines
    assert not any("experiment-config" in line for line in lines)


def test_the_flag_needs_a_file_argument() -> None:
    proc = _run("--seeds", "0", "--dry-run", "--experiment-config", env=_clean_env())
    assert proc.returncode == 1
    assert "--experiment-config requires a config file path" in proc.stderr


@pytest.mark.parametrize("name", sorted(EXPERIMENT_ENV_NAMES))
@pytest.mark.parametrize("value", ["1", "0"])
def test_every_meeting_experiment_export_is_refused_before_the_slate_check(
    name: str, value: str
) -> None:
    """The planted case that turned red: the export once passed the slate check.

    ``AILIBI_BOUNDED_REBUTTAL=1`` with ``--expect-levers ""`` printed "Substrate
    slate OK" before this check existed. Each of the four names is refused, with
    or without a config, whatever its value.
    """

    env = _clean_env()
    env[name] = value
    proc = _run("--seeds", "0", "--expect-levers", "", "--dry-run", env=env)
    assert proc.returncode == 1
    assert f"the environment exports {name}." in proc.stderr
    assert _NOTHING_STAGED in proc.stderr
    assert "Substrate slate OK" not in proc.stdout
    assert "[dry-run] mode:" not in proc.stdout


def test_a_run_without_any_export_passes_the_environment_check() -> None:
    proc = _run("--seeds", "0", "--expect-levers", "", "--dry-run", env=_clean_env())
    assert proc.returncode == 0
    assert "[dry-run] Experiment switch exports: none" in proc.stdout
    assert "Substrate slate OK" in proc.stdout


_DECOY = _REPO_ROOT / "replays" / "samples" / ".test-config-decoy"


def _require_absent_round(name: str) -> str:
    """``name``, once no path the round cases aim at exists under it; else raises.

    Committed rounds land under ``replays/candidates/``, so the cases below never
    aim at a fixed round name: each takes a name of its own and proves it absent
    before the run, which keeps their "the run created nothing" checks true
    whichever rounds the tree holds.
    """

    replays = _REPO_ROOT / "replays"
    for path in (
        replays / name,
        replays / "candidates" / name,
        replays / "candidates" / f".{name}",
    ):
        if path.exists():
            raise ValueError(f"round name {name!r} is taken: {path} exists")
    return name


def _absent_round_name() -> str:
    """A candidate round name of this case's own, absent from ``replays/``."""

    return _require_absent_round(f"probe-{uuid.uuid4().hex[:12]}")


def _new_replays_paths(before: set[Path]) -> list[Path]:
    """Every path under ``replays/`` that ``before`` does not hold, in path order."""

    return sorted(
        path for path in (_REPO_ROOT / "replays").rglob("*") if path not in before
    )


#: macOS reaches every directory of its data volume through this prefix too (a
#: firmlink): the same directory on disk under a second spelling.
_DATA_VOLUME = Path("/System/Volumes/Data")


def _case_insensitive(directory: Path) -> bool:
    """Whether ``directory``'s name, case-flipped, opens the same directory."""

    flipped = directory.parent / directory.name.swapcase()
    return (
        flipped.name != directory.name
        and flipped.exists()
        and os.path.samefile(flipped, directory)
    )


def _firmlinked(directory: Path) -> Path | None:
    """``directory`` reached through the data-volume firmlink, where one exists."""

    alias = Path(f"{_DATA_VOLUME}{os.path.realpath(directory)}")
    if alias.exists() and os.path.samefile(alias, directory):
        return alias
    return None


def _alias_skip_reason(case: str) -> str | None:
    """Why this filesystem cannot plant ``case``'s second spelling, if it cannot."""

    if case == "a case-variant spelling of samples" and not _case_insensitive(
        _REPO_ROOT / "replays"
    ):
        return "this filesystem tells case-variant names apart"
    if case == "a case-variant ancestor into ml_corpus" and not _case_insensitive(
        _REPO_ROOT
    ):
        return "this filesystem tells case-variant names apart"
    if case == "a firmlink into samples" and _firmlinked(_REPO_ROOT) is None:
        return "no firmlink reaches this checkout"
    return None


def _refused_target_env(
    case: str, tmp_path: Path, round_name: str
) -> tuple[dict[str, str], str]:
    """The environment aiming a switched-on config at ``case``, and the refusal.

    The three round-name cases aim at ``round_name``, a round of the case's own.
    """

    env = _clean_env()
    replays = _REPO_ROOT / "replays"
    if case == "default target":
        return env, "needs an explicit AILIBI_SAMPLE_DIR"
    targets = {
        "samples 9p2i": (replays / "samples" / "9p2i", _ERA_REFUSAL),
        "ml_corpus 9p2i": (replays / "ml_corpus" / "9p2i", "inside replays/ml_corpus/"),
        "a .. alias into samples": (
            Path(f"{_REPO_ROOT}/scripts/../replays/samples/4p1i"),
            "inside replays/samples/",
        ),
        "a symlink into samples": (
            tmp_path / "looks-like-scratch",
            "inside replays/samples/",
        ),
        "replays/<name>": (replays / round_name, "records only into a candidate set"),
        "one-level candidates/<round>": (
            replays / "candidates" / round_name,
            "records only into a candidate set",
        ),
        "a hidden round name": (
            replays / "candidates" / f".{round_name}" / "9p2i",
            f"name '.{round_name}' must start with a letter or digit",
        ),
        "a case-variant spelling of samples": (
            _REPO_ROOT / "REPLAYS" / "Samples" / "9p2i",
            _ERA_REFUSAL,
        ),
        "a case-variant ancestor into ml_corpus": (
            _REPO_ROOT.parent
            / _REPO_ROOT.name.swapcase()
            / "replays"
            / "ml_corpus"
            / "9p2i",
            "inside replays/ml_corpus/",
        ),
        "a firmlink into samples": (
            Path(f"{_DATA_VOLUME}{_REPO_ROOT}") / "replays" / "samples" / "9p2i",
            _ERA_REFUSAL,
        ),
    }
    if case == "a scratch dir with a committed manifest":
        env.update(
            AILIBI_SAMPLE_DIR=str(tmp_path / "scratch-set"),
            AILIBI_MANIFEST=str(_COMMITTED_4P1I / "MANIFEST.md"),
        )
        return env, "AILIBI_MANIFEST resolves to"
    target, refusal = targets[case]
    env.update(AILIBI_SAMPLE_DIR=str(target), AILIBI_MANIFEST=f"{target}/MANIFEST.md")
    return env, refusal


@pytest.mark.parametrize(
    "case",
    [
        "default target",
        "samples 9p2i",
        "ml_corpus 9p2i",
        "a .. alias into samples",
        "a symlink into samples",
        "a scratch dir with a committed manifest",
        "replays/<name>",
        "one-level candidates/<round>",
        "a hidden round name",
        "a case-variant spelling of samples",
        "a case-variant ancestor into ml_corpus",
        "a firmlink into samples",
    ],
)
def test_a_switched_on_config_is_refused_at_every_unsafe_target(
    case: str, tmp_path: Path
) -> None:
    """A real run (no key, so any gate after the check would fail differently).

    The last three cases spell a committed tree the way only some filesystems
    allow (a case-flipped segment or ancestor, the macOS data-volume firmlink),
    so each runs where its filesystem gives that second spelling and is skipped
    elsewhere.
    """

    skip_reason = _alias_skip_reason(case)
    if skip_reason is not None:
        pytest.skip(skip_reason)
    round_name = _absent_round_name()
    env, refusal = _refused_target_env(case, tmp_path, round_name)
    config = _test_config(tmp_path)
    if case == "a symlink into samples":
        _DECOY.mkdir()
        (tmp_path / "looks-like-scratch").symlink_to(_DECOY)
    before = set((_REPO_ROOT / "replays").rglob("*"))
    try:
        with _replays_tree_restored():
            proc = _run("--seeds", "0", "--experiment-config", str(config), env=env)
            assert proc.returncode == 1
            assert refusal in proc.stderr
            assert _NOTHING_STAGED in proc.stderr
            # The refusal names the offending path as it resolves physically.
            offending = {
                "default target": None,
                "a scratch dir with a committed manifest": env.get("AILIBI_MANIFEST"),
            }.get(case, env.get("AILIBI_SAMPLE_DIR"))
            if offending is not None:
                assert f"resolves to {os.path.realpath(offending)}" in proc.stderr
            # The check ran before every preflight: the key gate never spoke.
            assert "ANTHROPIC_API_KEY" not in proc.stderr
            assert "Substrate slate OK" not in proc.stdout
            assert _stage_dirs() == []
            assert not (_REPO_ROOT / "replays" / round_name).exists()
            assert not (_REPO_ROOT / "replays" / "candidates" / round_name).exists()
            assert not (
                _REPO_ROOT / "replays" / "candidates" / f".{round_name}"
            ).exists()
            assert _new_replays_paths(before) == []
            assert not (tmp_path / "scratch-set").exists()
    finally:
        if _DECOY.exists():
            shutil.rmtree(_DECOY)


def test_a_switched_on_config_is_accepted_at_a_candidate_set_directory(
    tmp_path: Path,
) -> None:
    target = _REPO_ROOT / "replays" / "candidates" / _absent_round_name() / "9p2i"
    env = _clean_env()
    env.update(AILIBI_SAMPLE_DIR=str(target), AILIBI_MANIFEST=f"{target}/MANIFEST.md")
    config = _test_config(tmp_path)
    before = set((_REPO_ROOT / "replays").rglob("*"))
    with _replays_tree_restored():
        proc = _run(
            "--seeds",
            "0",
            "--dry-run",
            "--expect-levers",
            "",
            "--experiment-config",
            str(config),
            env=env,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert f"[dry-run] {_TEST_SETTINGS_ECHO}" in proc.stdout.splitlines()
        assert not target.parent.exists()
        assert _new_replays_paths(before) == []


def test_a_round_already_on_disk_is_still_refused_and_left_as_it_was(
    tmp_path: Path,
) -> None:
    """Planted: a round directory of the case's own sits on disk, as a committed one does.

    Aimed at that directory itself, one level deep, a switched-on config is
    refused; the planted bytes stay as they were and nothing new appears under
    ``replays/``. The no-trace check bites: a path made after the snapshot is
    named, and a name whose round exists is refused as a probe name.
    """

    round_name = _absent_round_name()
    planted = _REPO_ROOT / "replays" / "candidates" / round_name
    env = _clean_env()
    env.update(AILIBI_SAMPLE_DIR=str(planted), AILIBI_MANIFEST=f"{planted}/MANIFEST.md")
    config = _test_config(tmp_path)
    with _replays_tree_restored():
        planted.mkdir()
        (planted / "README.md").write_text("planted\n", encoding="utf-8")
        before = set((_REPO_ROOT / "replays").rglob("*"))
        proc = _run("--seeds", "0", "--experiment-config", str(config), env=env)
        assert proc.returncode == 1
        assert "records only into a candidate set" in proc.stderr
        assert f"resolves to {os.path.realpath(planted)}" in proc.stderr
        assert _NOTHING_STAGED in proc.stderr
        assert "Substrate slate OK" not in proc.stdout
        assert _new_replays_paths(before) == []
        assert sorted(planted.iterdir()) == [planted / "README.md"]
        assert (planted / "README.md").read_text(encoding="utf-8") == "planted\n"
        with pytest.raises(ValueError, match="is taken"):
            _require_absent_round(round_name)
        stray = planted / "9p2i"
        stray.mkdir()
        assert _new_replays_paths(before) == [stray]
    assert not planted.exists()


def test_a_config_of_historical_defaults_goes_anywhere_and_records_no_key(
    tmp_path: Path,
) -> None:
    defaults = _test_config(
        tmp_path, '{"format_version": 1, "meeting_reset": "preserve"}\n'
    )
    proc = _run(
        "--seeds",
        "0",
        "--dry-run",
        "--expect-levers",
        "",
        "--experiment-config",
        str(defaults),
        env=_clean_env(),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert (
        "[dry-run] Experiment config settings: none: historical defaults"
        in proc.stdout.splitlines()
    )
    set_dir, env = _fake_set(tmp_path)
    proc = _run(
        "--seeds", "0", "--experiment-config", str(defaults), env=env, timeout=600
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert '"experiment_config"' not in (set_dir / "replay-seed-0.jsonl").read_text()


def _arms_on_refresh(
    tmp_path: Path,
) -> tuple[Path, Path, subprocess.CompletedProcess[str]]:
    """A fake refresh of seeds 0 and 1 on the test config, traced, in a bare shell."""

    config = _test_config(tmp_path)
    set_dir, env = _fake_set(tmp_path)
    proc = subprocess.run(
        [
            "bash",
            "-x",
            str(_REFRESH_SH),
            "--seeds",
            "0,1",
            "--expect-levers",
            "",
            "--experiment-config",
            str(config),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    return config, set_dir, proc


def test_a_fake_arms_on_refresh_records_exactly_the_file_and_loads_verified(
    tmp_path: Path,
) -> None:
    config, set_dir, proc = _arms_on_refresh(tmp_path)
    assert "Refresh complete" in proc.stdout, proc.stdout[-4000:] + proc.stderr[-4000:]
    for seed in (0, 1):
        entries = read_all_entries(set_dir / f"replay-seed-{seed}.jsonl")
        stamped = [
            entry.experiment_config
            for entry in entries
            if isinstance(entry, (ReplayEntry, GameEndReplayEntry))
        ]
        assert len(stamped) > 1 and all(item == _TEST_CONFIG for item in stamped)
        replay = ReplayLoader(set_dir).load_replay(f"headless-seed-{seed}")
        assert replay.metadata.outcome_verified
    # The config was copied into the stage once, and every seed recorded from
    # that copy, never from the file the operator could still edit.
    snapshots = re.findall(
        r"Experiment config snapshot: (\S+) \(sha256 ([0-9a-f]{64})\)", proc.stdout
    )
    assert len(snapshots) == 1
    snapshot, sha = snapshots[0]
    assert sha == hashlib.sha256(config.read_bytes()).hexdigest()
    assert ".ailibi-refresh-stage-" in snapshot
    invocations = [
        line
        for line in proc.stderr.splitlines()
        if "scripts/run_tournament.py" in line
        and line.lstrip("+").startswith(" uv run")
    ]
    assert len(invocations) == 2
    assert all(
        line.endswith(f"--force --experiment-config {snapshot}") for line in invocations
    )
    assert list(tmp_path.glob(".ailibi-refresh-stage-*")) == []


def test_the_post_step_builds_and_checks_the_report_of_an_arms_on_set(
    tmp_path: Path,
) -> None:
    _config, set_dir, proc = _arms_on_refresh(tmp_path)
    assert proc.returncode == 0, proc.stdout[-4000:] + proc.stderr[-4000:]
    check = subprocess.run(
        [
            "uv",
            "run",
            "python",
            str(_REPO_ROOT / "scripts" / "build_sample_report.py"),
            "--sample-dir",
            str(set_dir),
            "--check",
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=_clean_env(),
        timeout=600,
    )
    assert check.returncode == 0, check.stdout + check.stderr
    assert "is consistent with its replays" in check.stdout


# -- the helper's own rules, below the script ---------------------------------


def test_the_snapshot_refuses_a_file_edited_after_the_check(tmp_path: Path) -> None:
    config = _test_config(tmp_path)
    checked = de.load_declared_config(config)
    config.write_text(_TEST_CONFIG_JSON.replace("observed_risk", "target_distance"))
    dest = tmp_path / "stage" / "experiment-config.json"
    dest.parent.mkdir()
    edited = hashlib.sha256(config.read_bytes()).hexdigest()
    with pytest.raises(
        de.DeclaredExperimentError, match="changed after it was checked"
    ) as refused:
        de.write_snapshot(config, dest, expected_sha256=checked.sha256)
    assert f"it now reads sha256 {edited}" in str(refused.value)
    assert f"the checked copy read {checked.sha256}" in str(refused.value)
    assert not dest.exists()
    config.write_text(_TEST_CONFIG_JSON)
    line = de.write_snapshot(config, dest, expected_sha256=checked.sha256)
    assert dest.read_bytes() == config.read_bytes()
    assert line.endswith("every seed records from this copy")


def test_the_snapshot_validates_the_bytes_it_copies(tmp_path: Path) -> None:
    config = _test_config(tmp_path, '{"hidden_travel": "on"}\n')
    dest = tmp_path / "copy.json"
    with pytest.raises(de.DeclaredExperimentError, match="hidden_travel"):
        de.write_snapshot(
            config,
            dest,
            expected_sha256=hashlib.sha256(config.read_bytes()).hexdigest(),
        )
    assert not dest.exists()


@pytest.mark.parametrize(
    ("text", "detail"),
    [
        ('{"hidden_travel": "on"}', "hidden_travel"),
        ('{"meeting_reset": "sometimes"}', "meeting_reset"),
        ('{"bounded_rebuttal_version": true}', "bounded_rebuttal_version"),
        (
            '{"meeting_reset": "hub_with_grace", "meeting_reset": "preserve"}',
            "more than once",
        ),
        ('["meeting_reset"]', "one object"),
        ("{", "not a valid experiment config"),
    ],
)
def test_the_file_must_be_one_valid_config(
    tmp_path: Path, text: str, detail: str
) -> None:
    with pytest.raises(de.DeclaredExperimentError, match=detail):
        de.load_declared_config(_test_config(tmp_path, text + "\n"))


def test_the_sha256_covers_exactly_the_bytes_read(tmp_path: Path) -> None:
    config = _test_config(tmp_path)
    declared = de.load_declared_config(config)
    assert declared.sha256 == hashlib.sha256(config.read_bytes()).hexdigest()
    assert declared.config == _TEST_CONFIG
    assert declared.settings() == (
        ("meeting_reset", "hub_with_grace"),
        ("vent_exit_policy", "observed_risk"),
        ("bounded_rebuttal_version", 1),
    )


def test_the_target_rule_reads_physical_paths(tmp_path: Path) -> None:
    """The rule over a planted repository: its own replays/ tree, not this one."""

    repo = tmp_path / "repo"
    (repo / "replays" / "samples" / "4p1i").mkdir(parents=True)
    (repo / "replays" / "candidates").mkdir(parents=True)
    link = tmp_path / "link"
    link.symlink_to(repo / "replays" / "samples")
    candidate = repo / "replays" / "candidates" / "r1" / "9p2i"

    def refusal(sample_dir: Path, manifest: Path | None = None) -> str | None:
        try:
            de.refuse_unsafe_target(
                _TEST_CONFIG,
                sample_dir=sample_dir,
                manifest=manifest
                if manifest is not None
                else sample_dir / "MANIFEST.md",
                sample_dir_explicit=True,
                repo_root=repo,
            )
        except de.DeclaredExperimentError as exc:
            return str(exc)
        return None

    assert refusal(candidate) is None
    assert refusal(tmp_path / "scratch") is None
    assert "inside replays/samples/" in (refusal(link / "new-set") or "")
    assert "inside replays/samples/" in (
        refusal(tmp_path / "gone" / ".." / "link" / "4p1i") or ""
    )
    assert "records only into a candidate set" in (
        refusal(candidate, repo / "replays" / "candidates" / "r1" / "MANIFEST.md") or ""
    )
    assert "records only into a candidate set" in (
        refusal(repo / "replays" / "candidates" / "r1" / "9p2i" / "deeper") or ""
    )
    assert refusal(candidate, candidate / "MANIFEST.md") is None
    # A canonical tree this repository lacks is still refused where the recorder
    # would create it: below the nearest existing directory, spelled exactly.
    assert "inside replays/ml_corpus/" in (
        refusal(repo / "replays" / "ml_corpus" / "9p2i") or ""
    )
    # The replays/ directory itself is no candidate set directory.
    assert "records only into a candidate set" in (refusal(repo / "replays") or "")
    # A path through a regular file is placed by the nearest directory holding
    # it: outside replays/ it is accepted (the recorder fails to create it), and
    # a file inside a canonical tree is inside that tree.
    (tmp_path / "a-file").write_text("not a directory\n", encoding="utf-8")
    assert refusal(tmp_path / "a-file" / "set") is None
    committed = repo / "replays" / "samples" / "4p1i" / "MANIFEST.md"
    committed.write_text("| seed |\n", encoding="utf-8")
    assert "inside replays/samples/" in (refusal(committed) or "")
    assert "inside replays/samples/" in (refusal(committed / "set") or "")
    # The historical defaults record nothing new, so they go anywhere.
    de.refuse_unsafe_target(
        RecordedExperimentConfig(),
        sample_dir=repo / "replays" / "samples" / "4p1i",
        manifest=repo / "replays" / "samples" / "4p1i" / "MANIFEST.md",
        sample_dir_explicit=False,
        repo_root=repo,
    )


# -- the helper's rules as properties over generated families -----------------

#: Path segments the target property composes, including the ones a string
#: prefix test would mishandle: ``..``, ``.``, a link into a canonical tree,
#: names that look like trees one level off, and case-flipped spellings (the
#: same directory on a case-insensitive filesystem, a new name elsewhere).
_SEGMENTS = st.sampled_from(
    [
        "..",
        ".",
        "samples",
        "ml_corpus",
        "candidates",
        "records",
        "into-samples",
        "into-corpus",
        "r1",
        "9p2i",
        "a.b",
        ".hidden",
        "SAMPLES",
        "Ml_Corpus",
        "Candidates",
        "Replays",
        "INTO-SAMPLES",
        "R1",
    ]
)


@pytest.fixture(scope="module")
def planted_repo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A repository whose replays/ tree carries both canonical trees and links.

    The links are relative, so a copy of the tree links within the copy.
    """

    root = tmp_path_factory.mktemp("planted-repo")
    replays = root / "repo" / "replays"
    for tree in ("samples/4p1i", "ml_corpus/9p2i", "candidates/r1/9p2i", "records"):
        (replays / tree).mkdir(parents=True)
    (replays / "candidates" / "into-samples").symlink_to(Path("..") / "samples")
    (root / "outside").mkdir()
    (root / "outside" / "into-corpus").symlink_to(
        Path("..") / "repo" / "replays" / "ml_corpus"
    )
    return root


@pytest.fixture(scope="module")
def planted_copies(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Where the target property copies the planted repository, once per example."""

    return Path(os.path.realpath(tmp_path_factory.mktemp("planted-copies")))


def _target_outcome(repo: Path, target: Path, manifest: Path) -> str | None:
    try:
        de.refuse_unsafe_target(
            _TEST_CONFIG,
            sample_dir=target,
            manifest=manifest,
            sample_dir_explicit=True,
            repo_root=repo,
            registry=_CANONICAL_RULE_ONLY,
        )
    except de.DeclaredExperimentError as exc:
        return str(exc)
    return None


def _landed_place(replays: Path, target: Path) -> tuple[str, ...] | None:
    """Where ``mkdir -p`` puts ``target``, as segments below ``replays``.

    The directory is made, then found by device and inode among the directories
    ``replays`` holds afterwards, under the names they were made with. ``None``
    when it landed anywhere else.
    """

    target.mkdir(parents=True, exist_ok=True)
    landed = target.stat()
    for directory, _subdirectories, _files in os.walk(replays):
        status = os.stat(directory)
        if (status.st_dev, status.st_ino) == (landed.st_dev, landed.st_ino):
            return Path(directory).relative_to(replays).parts
    return None


@settings(deadline=None, max_examples=300)
@given(
    base=st.sampled_from(
        [
            "repo/replays",
            "repo",
            "outside",
            "repo/replays/candidates",
            "REPO/REPLAYS",
            "Outside",
        ]
    ),
    flip_root=st.booleans(),
    segments=st.lists(_SEGMENTS, max_size=5),
)
def test_no_accepted_target_resolves_inside_a_canonical_tree(
    planted_repo: Path,
    planted_copies: Path,
    base: str,
    flip_root: bool,
    segments: list[str],
) -> None:
    """Whatever the path's spelling, the directory it lands in decides.

    A target accepted for a switched-on config never lands inside
    ``replays/samples/`` or ``replays/ml_corpus/``, and inside ``replays/`` it is
    exactly a candidate set directory with names the verifier's glob can see.
    The oracle compares no spellings: after the rule has spoken, it makes the
    target in a fresh copy of the planted repository the way the recorder
    would, and finds the made directory by device and inode among the copy's
    ``replays/`` directories. On a case-insensitive filesystem a flipped
    segment or a flipped planted root opens the same directory; elsewhere it is
    a new name.
    """

    copy = Path(tempfile.mkdtemp(dir=planted_copies))
    try:
        shutil.copytree(planted_repo, copy / "planted", symlinks=True)
        repo = copy / "planted" / "repo"
        root = copy / ("PLANTED" if flip_root else "planted")
        target = Path(root, base, *segments)
        outcome = _target_outcome(repo, target, target / "MANIFEST.md")
        if copy not in Path(os.path.realpath(target)).parents:
            # It climbed out of the copy, so it is nowhere near replays/.
            assert outcome is None, (target, outcome)
            return
        parts = _landed_place(repo / "replays", target)
    finally:
        shutil.rmtree(copy)
    if parts is None:
        assert outcome is None, (target, outcome)
    elif parts[:1] in (("samples",), ("ml_corpus",)):
        assert outcome is not None and f"inside replays/{parts[0]}/" in outcome
    elif (
        len(parts) == 3
        and parts[0] == "candidates"
        and all(not name.startswith(".") for name in parts[1:])
    ):
        assert outcome is None, (target, outcome)
    else:
        assert outcome is not None, (target, parts)


@settings(deadline=None, max_examples=100)
@given(
    round_name=st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._-]{0,8}", fullmatch=True),
    set_name=st.from_regex(r"[A-Za-z0-9][A-Za-z0-9._-]{0,8}", fullmatch=True),
)
def test_every_well_named_candidate_set_directory_is_accepted(
    planted_repo: Path, round_name: str, set_name: str
) -> None:
    repo = planted_repo / "repo"
    if "into-samples" in (round_name, set_name) or ".." in (round_name, set_name):
        return
    target = repo / "replays" / "candidates" / round_name / set_name
    assert _target_outcome(repo, target, target / "MANIFEST.md") is None
    # The same set's manifest aimed one level up is refused.
    assert _target_outcome(repo, target, target.parent / "MANIFEST.md") is not None


@settings(deadline=None, max_examples=200)
@given(
    exported=st.sets(st.sampled_from(sorted(EXPERIMENT_ENV_NAMES))),
    others=st.dictionaries(
        st.from_regex(r"AILIBI_[A-Z_]{1,12}", fullmatch=True), st.text(max_size=5)
    ),
    value=st.text(max_size=8),
)
def test_any_meeting_experiment_export_is_refused_whatever_its_value(
    exported: set[str], others: dict[str, str], value: str
) -> None:
    environ = {
        key: item for key, item in others.items() if key not in EXPERIMENT_ENV_NAMES
    }
    environ.update({name: value for name in exported})
    names = de.ambient_experiment_exports(environ)
    assert names == tuple(sorted(exported))
    for recorder in ("refresh", "tournament"):
        if exported:
            with pytest.raises(de.DeclaredExperimentError) as refused:
                de.refuse_ambient_exports(environ, recorder=recorder)
            assert ", ".join(sorted(exported)) in str(refused.value)
        else:
            de.refuse_ambient_exports(environ, recorder=recorder)


def test_the_refused_names_follow_the_experiment_registry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Planted: a fifth switch registered is refused too, with no edit here."""

    monkeypatch.setattr(
        de,
        "EXPERIMENT_ENV_NAMES",
        MappingProxyType({**EXPERIMENT_ENV_NAMES, "AILIBI_PLANTED_SWITCH": "planted"}),
    )
    with pytest.raises(de.DeclaredExperimentError, match="AILIBI_PLANTED_SWITCH"):
        de.refuse_ambient_exports({"AILIBI_PLANTED_SWITCH": "1"}, recorder="refresh")


def test_the_settings_follow_the_config_model() -> None:
    """Planted: a field added to the config model is listed once it is set."""

    class _Wider(RecordedExperimentConfig):
        planted_rule: str = "old"

    wider = _Wider(meeting_reset="hub_with_grace", planted_rule="new")
    assert de.non_default_settings(wider) == (
        ("meeting_reset", "hub_with_grace"),
        ("planted_rule", "new"),
    )
    assert de.describe_settings(wider) == (
        "meeting_reset='hub_with_grace', planted_rule='new'"
    )
    assert de.describe_settings(None) == "none: historical defaults"
    assert de.describe_settings(RecordedExperimentConfig(format_version=2)) == (
        "none: historical defaults"
    )


def test_an_unreadable_config_is_refused_by_name(tmp_path: Path) -> None:
    missing = tmp_path / "absent.json"
    with pytest.raises(de.DeclaredExperimentError, match="it cannot be read"):
        de.load_declared_config(missing)
    with pytest.raises(de.DeclaredExperimentError, match="it cannot be read"):
        de.write_snapshot(missing, tmp_path / "copy.json", expected_sha256="0" * 64)
    assert not (tmp_path / "copy.json").exists()


def test_the_target_rule_resolves_the_repository_itself(tmp_path: Path) -> None:
    """Planted: the repository reached through a link, the target by its real path.

    Both sides are compared physically, so a checkout opened through a link
    still refuses its own canonical trees and still accepts its candidates.
    """

    repo = tmp_path / "repo"
    (repo / "replays" / "samples" / "9p2i").mkdir(parents=True)
    (repo / "replays" / "records").mkdir(parents=True)
    linked = tmp_path / "linked-checkout"
    linked.symlink_to(repo)
    for root, target in (
        (linked, repo / "replays" / "samples" / "9p2i"),
        (repo, linked / "replays" / "samples" / "9p2i"),
    ):
        with pytest.raises(de.DeclaredExperimentError, match="inside replays/samples/"):
            de.refuse_unsafe_target(
                _TEST_CONFIG,
                sample_dir=target,
                manifest=target / "MANIFEST.md",
                sample_dir_explicit=True,
                repo_root=root,
                registry=_CANONICAL_RULE_ONLY,
            )
    candidate = repo / "replays" / "candidates" / "r1" / "9p2i"
    de.refuse_unsafe_target(
        _TEST_CONFIG,
        sample_dir=candidate,
        manifest=candidate / "MANIFEST.md",
        sample_dir_explicit=True,
        repo_root=linked,
        registry=_CANONICAL_RULE_ONLY,
    )
    # The candidate depth is not enough on its own: the family must be candidates.
    records = repo / "replays" / "records" / "r1" / "9p2i"
    with pytest.raises(de.DeclaredExperimentError, match="records only into"):
        de.refuse_unsafe_target(
            _TEST_CONFIG,
            sample_dir=records,
            manifest=records / "MANIFEST.md",
            sample_dir_explicit=True,
            repo_root=repo,
            registry=_CANONICAL_RULE_ONLY,
        )


def test_the_target_rule_decides_each_tree_by_identity_not_spelling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Planted: a second name for each directory, as a second mount would give.

    Each alias is a real directory elsewhere whose spelling shares nothing with
    the tree it stands for; the patched identity reports it as that tree's
    device and inode. Before the patch every alias is an ordinary scratch
    directory and is accepted, so the patch alone is what refuses them.
    """

    replays = tmp_path / "repo" / "replays"
    for tree in ("samples/9p2i", "ml_corpus/9p2i", "candidates"):
        (replays / tree).mkdir(parents=True)
    mounts = Path(os.path.realpath(tmp_path)) / "mounts"
    second_samples = mounts / "second-samples"
    second_corpus = mounts / "second-corpus"
    second_replays = mounts / "second-replays"
    second_candidates = mounts / "second-candidates"
    aliases = {
        second_samples: replays / "samples",
        second_corpus: replays / "ml_corpus",
        second_replays: replays,
        second_candidates: replays / "candidates",
    }
    for alias in aliases:
        alias.mkdir(parents=True)
    repo = tmp_path / "repo"
    scratch = tmp_path / "scratch"
    probes = (
        second_samples,
        second_samples / "new-set",
        second_corpus / "9p2i",
        second_replays / "newset",
        second_candidates / "r1",
        second_candidates / "r1" / "9p2i",
        second_candidates / ".r1" / "9p2i",
    )
    for probe in probes:
        assert _target_outcome(repo, probe, probe / "MANIFEST.md") is None, probe

    unpatched = de._identity

    def aliased(path: Path) -> tuple[int, int]:
        return unpatched(aliases[path] if path in aliases else path)

    monkeypatch.setattr(de, "_identity", aliased)

    def outcome(sample_dir: Path, manifest: Path | None = None) -> str:
        return (
            _target_outcome(
                repo,
                sample_dir,
                manifest if manifest is not None else sample_dir / "MANIFEST.md",
            )
            or ""
        )

    assert "inside replays/samples/" in outcome(second_samples)
    assert "inside replays/samples/" in outcome(second_samples / "new-set")
    assert "inside replays/ml_corpus/" in outcome(second_corpus / "9p2i")
    assert "records only into a candidate set" in outcome(second_replays / "newset")
    assert "records only into a candidate set" in outcome(second_candidates / "r1")
    assert "name '.r1' must start" in outcome(second_candidates / ".r1" / "9p2i")
    assert outcome(second_candidates / "r1" / "9p2i") == ""
    manifest_refusal = outcome(scratch, second_samples / "9p2i" / "MANIFEST.md")
    assert manifest_refusal.startswith("Refused: AILIBI_MANIFEST resolves to ")
    assert "inside replays/samples/" in manifest_refusal
    assert outcome(scratch) == ""


def test_case_variant_spellings_name_the_same_directories(tmp_path: Path) -> None:
    """Planted: case-flipped segments and a case-flipped ancestor.

    On a case-insensitive filesystem each flipped spelling opens the directory
    it flips, so it gets that directory's verdict; the recorder would write
    there. Skipped where the filesystem tells the names apart.
    """

    repo = tmp_path / "repo"
    for tree in ("samples/9p2i", "ml_corpus/9p2i", "candidates/r1"):
        (repo / "replays" / tree).mkdir(parents=True)
    if not _case_insensitive(repo):
        pytest.skip("this filesystem tells case-variant names apart")
    flipped_ancestor = tmp_path.parent / tmp_path.name.swapcase()
    assert os.path.samefile(flipped_ancestor, tmp_path)
    cases = {
        repo / "REPLAYS" / "Samples" / "9p2i": "inside replays/samples/",
        repo / "Replays" / "samples" / "new-set": "inside replays/samples/",
        repo / "REPLAYS" / "ML_CORPUS" / "9p2i": "inside replays/ml_corpus/",
        flipped_ancestor / "repo" / "replays" / "samples" / "9p2i": (
            "inside replays/samples/"
        ),
        flipped_ancestor / "REPO" / "replays" / "ml_corpus": (
            "inside replays/ml_corpus/"
        ),
        repo / "REPLAYS" / "newset": "records only into a candidate set",
        repo / "replays" / "CANDIDATES" / "r1": "records only into a candidate set",
    }
    for target, refusal in cases.items():
        assert refusal in (
            _target_outcome(repo, target, target / "MANIFEST.md") or ""
        ), target
    # The candidate family under a flipped spelling is still the family.
    for target in (
        repo / "REPLAYS" / "candidates" / "r1" / "9p2i",
        repo / "replays" / "CANDIDATES" / "R1" / "9p2i",
        flipped_ancestor / "REPO" / "Replays" / "Candidates" / "new" / "9p2i",
    ):
        assert _target_outcome(repo, target, target / "MANIFEST.md") is None, target


def test_a_firmlink_spelling_names_the_same_directories(tmp_path: Path) -> None:
    """Planted: the planted repository reached through the data-volume firmlink.

    Skipped where no firmlink reaches the temporary directory.
    """

    repo = tmp_path / "repo"
    for tree in ("samples/9p2i", "ml_corpus/9p2i", "candidates/r1"):
        (repo / "replays" / tree).mkdir(parents=True)
    firmlinked = _firmlinked(repo)
    if firmlinked is None:
        pytest.skip("no firmlink reaches this temporary directory")
    assert str(firmlinked) != os.path.realpath(repo)
    for tree, refusal in (
        ("samples/9p2i", "inside replays/samples/"),
        ("ml_corpus/9p2i", "inside replays/ml_corpus/"),
        ("newset", "records only into a candidate set"),
    ):
        target = firmlinked / "replays" / tree
        assert refusal in (
            _target_outcome(repo, target, target / "MANIFEST.md") or ""
        ), target
    candidate = firmlinked / "replays" / "candidates" / "r1" / "9p2i"
    assert _target_outcome(repo, candidate, candidate / "MANIFEST.md") is None


def test_an_unreadable_directory_under_replays_raises_rather_than_being_skipped(
    tmp_path: Path,
) -> None:
    """Planted: a canonical tree the walk cannot list.

    Its place cannot be read from disk, so the rule raises instead of treating
    the tree as outside ``replays/``. Skipped where permissions do not bind (a
    superuser reads every directory).
    """

    repo = tmp_path / "repo"
    samples = repo / "replays" / "samples"
    (samples / "9p2i").mkdir(parents=True)
    # The manifest goes to scratch, so only the walk can see the tree.
    scratch_manifest = tmp_path / "scratch" / "MANIFEST.md"
    samples.chmod(0)
    try:
        if os.access(samples, os.R_OK):
            pytest.skip("permissions do not bind for this user")
        with pytest.raises(PermissionError):
            _target_outcome(repo, samples, scratch_manifest)
    finally:
        samples.chmod(0o755)
    assert "inside replays/samples/" in (
        _target_outcome(repo, samples, scratch_manifest) or ""
    )
