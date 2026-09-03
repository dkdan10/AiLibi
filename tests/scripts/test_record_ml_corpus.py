"""Tests for scripts/record_ml_corpus.sh (Task 15.12).

Exercises argument handling, the --dry-run plan, the provider/substrate/model
preflight (which the corpus LOCKS to featherless + qwen3_6_27b + the baseline
model), the locked-seed-range guard, and the hermetic --splits-only emission.
Every case is hermetic and makes NO network call and NO real-provider record:

* --dry-run touches nothing and describes the plan;
* the preflight cases fail loud BEFORE any tournament invocation (wrong
  provider / missing key / wrong prompt set), so no record ever starts — the
  ambient FEATHERLESS_API_KEY / ANTHROPIC_API_KEY are stripped by _clean_env so
  a test can never accidentally kick off the ~18–20h operator recording;
* --splits-only derives splits.json from stub replay files in a tmp corpus root
  (AILIBI_ML_CORPUS_ROOT) with no provider call at all.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from collections.abc import Mapping
from pathlib import Path

import pytest

from orchestrator.replay import substrate_flag_snapshot

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RECORD_SH = _REPO_ROOT / "scripts" / "record_ml_corpus.sh"

# The committed corpus under replays/ml_corpus/ IS the baseline-6 re-record (Task
# 18.13), so it satisfies every axis the recorder's freeze-path provenance guard
# (check_replay_provenance) gates: the canonical fsm-default stamp, the locked
# MODEL id on every recorded call, $0 cost, and the baseline-6 lever slate on the
# game_over substrate_flags stamp. The record-path fixtures below borrow one
# committed replay as their substrate-CURRENT input; the model rebase is retained
# as a no-op safety net so the fixture stays valid if a future re-record lands
# before this pin moves. read_tactical_policy_stamp reads the untouched stamp
# block and compute_cost_usd sums the recorded (all-$0) cost fields, so the rebase
# leaves the canonical fsm-default stamp and the $0 provenance intact.
_STALE_CORPUS_MODEL = "Qwen/Qwen3-32B"
_BASELINE_MODEL = "Qwen/Qwen3.6-27B"
_COMMITTED_CORPUS_REPLAY = (
    _REPO_ROOT / "replays" / "ml_corpus" / "4p1i" / "replay-seed-1000.jsonl"
)

# The bare baseline-6 lever slate a substrate-current recording stamps (Task
# 18.13): the THIRTEEN retired always-on levers True — including the four
# meeting-layer graduations of Task 18.12 (roll_call_round,
# whereabouts_interior_flags, vent_placement_contradictions, absence_prior) — with
# impostor_roll_call OFF (the unshipped impostor-answer arm; the CREW-ONLY ruling
# of audits/audit-phase-18-meeting-gate.md §9). Derived from the build snapshot
# with an explicit bare env so the fixture always tracks the recorder's documented
# substrate — the same slate check_replay_provenance asserts positively in the
# recorded bytes.
_BASELINE6_SUBSTRATE_SLATE = substrate_flag_snapshot(env={})

# The stale baseline-5 slate (the committed corpus's PRE-re-record substrate): the
# nine baseline-5 levers True, MISSING the four Task-18.12 meeting-layer
# graduations. Synthesized here because the committed bytes are now themselves the
# baseline-6 re-record (Task 18.13), so the negative slate test can no longer
# borrow a genuinely-stale replay off disk.
_STALE_BASELINE5_SLATE = {
    "testimony_as_content": True,
    "witnessed_kill_evidence": True,
    "movement_perception": True,
    "unfreeze_memory": True,
    "evidence_quality_lift": True,
    "reporter_exculpation": True,
    "hard_evidence_gate": True,
    "observation_id_rendering": True,
    "citation_gate": True,
}


def _rewrite_game_over_substrate(text: str, flags: Mapping[str, bool]) -> str:
    """Return ``text`` with the game_over row's substrate_flags stamp set to ``flags``.

    Line-wise: parse the one game_over row, replace its substrate_flags, re-dump
    that line. The recorder reads the stamp via Pydantic (read_substrate_flags),
    so the re-serialized key order is immaterial; every other row is left
    byte-untouched.
    """

    lines = text.splitlines()
    for i, line in enumerate(lines):
        record = json.loads(line)
        if record.get("kind") == "game_over":
            record["substrate_flags"] = dict(flags)
            lines[i] = json.dumps(record, separators=(",", ":"))
    return "\n".join(lines) + "\n"


def _baseline6_corpus_replay_text() -> str:
    """The one committed corpus replay, rebased onto the baseline-6 substrate.

    Yields a replay that carries the canonical fsm-default stamp, the baseline
    model on every recorded call, $0 cost, AND the baseline-6 lever slate on its
    game_over stamp — the substrate the re-pinned recorder accepts on every
    check_replay_provenance axis.
    """

    text = _COMMITTED_CORPUS_REPLAY.read_text(encoding="utf-8").replace(
        f'"model":"{_STALE_CORPUS_MODEL}"', f'"model":"{_BASELINE_MODEL}"'
    )
    return _rewrite_game_over_substrate(text, _BASELINE6_SUBSTRATE_SLATE)


pytestmark = pytest.mark.skipif(
    shutil.which("bash") is None, reason="bash required to run record_ml_corpus.sh"
)


def _clean_env() -> dict[str, str]:
    """Ambient env with every ``AILIBI_*`` override AND every provider key stripped.

    Stripping the keys is a SAFETY invariant: a test must never be able to fall
    into the real record path (which would start the ~18–20h operator recording).
    """

    return {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("AILIBI_")
        and k not in ("FEATHERLESS_API_KEY", "ANTHROPIC_API_KEY")
    }


def _run(
    *args: str, env: dict[str, str] | None = None, timeout: float | None = 60
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(_RECORD_SH), *args],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=env if env is not None else _clean_env(),
        timeout=timeout,
    )


# -- basics -------------------------------------------------------------------


def test_record_sh_is_executable() -> None:
    assert _RECORD_SH.exists()
    assert os.access(_RECORD_SH, os.X_OK)


def test_help_exits_zero() -> None:
    proc = _run("--help")
    assert proc.returncode == 0
    assert "Usage:" in proc.stdout


def test_unknown_argument_rejected() -> None:
    proc = _run("--frobnicate")
    assert proc.returncode != 0
    assert "Unknown argument" in proc.stdout + proc.stderr


def test_bad_set_rejected() -> None:
    proc = _run("--set", "7p3i", "--dry-run")
    assert proc.returncode != 0
    assert "must be one of 9p2i, 4p1i, both" in proc.stdout + proc.stderr


def test_dry_run_and_splits_only_mutually_exclusive() -> None:
    proc = _run("--dry-run", "--splits-only")
    assert proc.returncode != 0
    assert "mutually exclusive" in proc.stdout + proc.stderr


# -- dry-run plan -------------------------------------------------------------


def test_dry_run_default_is_both_sets() -> None:
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert "[dry-run] sets: 9p2i 4p1i" in proc.stdout
    assert "no API calls made; no files written." in proc.stdout


def test_dry_run_9p2i_seed_range_and_roster() -> None:
    # The primary set: 150 seeds at 1000..1149 (fresh range, disjoint from the
    # canonical 0–49 sets), roster 9p/2i @ 2 tasks/crewmate (baseline-6 9p2i).
    proc = _run("--set", "9p2i", "--dry-run")
    assert proc.returncode == 0
    assert "seed range: 1000..1149 (150 games)" in proc.stdout
    assert "roster: num_players=9 num_impostors=2 tasks_per_crewmate=2" in proc.stdout


def test_dry_run_4p1i_seed_range_and_roster() -> None:
    # The secondary set: 50 seeds at 1000..1049, roster 4p/1i @ 1 task/crewmate.
    proc = _run("--set", "4p1i", "--dry-run")
    assert proc.returncode == 0
    assert "seed range: 1000..1049 (50 games)" in proc.stdout
    assert "roster: num_players=4 num_impostors=1 tasks_per_crewmate=1" in proc.stdout


def test_dry_run_locks_provider_to_featherless() -> None:
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert "provider: featherless (LOCKED" in proc.stdout
    assert "would require FEATHERLESS_API_KEY" in proc.stdout
    assert "prompt set: qwen3_6_27b" in proc.stdout


def test_dry_run_announces_endpoint_and_prompt_version_locks() -> None:
    # The full substrate lock is visible in the plan: the hosted endpoint pin
    # (a non-default AILIBI_FEATHERLESS_BASE_URL is refused) and the exact
    # per-template prompt-version map the corpus is frozen at.
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert (
        "endpoint: https://api.featherless.ai/v1 (pinned; a non-default "
        "AILIBI_FEATHERLESS_BASE_URL override is refused)" in proc.stdout
    )
    assert (
        "prompt versions: the declared slate resolves to "
        "[accusation_round.qwen3_6_27b.v5, "
        "crewmate_report.qwen3_6_27b.v5, impostor_report.qwen3_6_27b.v5, "
        "vote_ballot.qwen3_6_27b.v5]" in proc.stdout
    )


# The two dry-run lines that describe the substrate, mirroring
# scripts/refresh_samples.sh so both recorders preview the slate identically.
_BARE_SLATE_ECHO = (
    "[dry-run] substrate flags: expected levers ON = (none — the bare slate: "
    "every live toggle OFF); every other live toggle OFF; the graduated levers "
    "unconditional ON"
)
_PREFLIGHT_ECHO = (
    "[dry-run] substrate-lever preflight: would require the live lever slate to "
    "equal that expectation exactly and refuse before any seed stages"
)


def test_dry_run_announces_the_expected_slate_and_the_lever_preflight() -> None:
    # The plan names the lever slate this record expects AND the preflight that
    # enforces it, so an operator previewing a ~22-23h run can confirm the
    # substrate before spending.
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert _BARE_SLATE_ECHO in proc.stdout
    assert _PREFLIGHT_ECHO in proc.stdout


def test_dry_run_echo_names_the_levers_the_operator_declared() -> None:
    # The echo quotes the RESOLVED slate, so the preview and the gate can never
    # describe different substrates.
    env = dict(_clean_env(), AILIBI_IMPOSTOR_ROLL_CALL="1")
    proc = _run("--dry-run", "--expect-levers", "impostor_roll_call", env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert (
        "[dry-run] substrate flags: expected levers ON = impostor_roll_call"
        in proc.stdout
    )


def test_expect_levers_requires_an_argument() -> None:
    # A --expect-levers with NOTHING after it is an operator typo.
    proc = _run("--dry-run", "--expect-levers")
    assert proc.returncode != 0
    assert "--expect-levers requires a comma-separated lever list" in (
        proc.stdout + proc.stderr
    )


def test_an_explicitly_empty_expect_levers_is_the_bare_slate() -> None:
    # An empty STRING is a declaration, not a typo: automation can pass
    # --expect-levers "$LEVERS" unconditionally and get the bare slate.
    proc = _run("--dry-run", "--expect-levers", "")
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert _BARE_SLATE_ECHO in proc.stdout


def test_preflight_refuses_a_declared_lever_that_is_not_exported(
    tmp_path: Path,
) -> None:
    # Direction 1: the operator declared a lever the shell never exported, so the
    # whole corpus would be recorded on the OLD substrate. A blacklist of variable
    # names cannot catch this; a positive whole-slate equality can.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", "--expect-levers", "impostor_roll_call", env=env)
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "does not match --expect-levers" in out
    assert "impostor_roll_call must be ON" in out
    assert not corpus_root.exists()  # refused before any record


def test_preflight_accepts_the_declared_slate_when_the_environment_matches(
    tmp_path: Path,
) -> None:
    # The gate must be passable: with exactly the declared lever exported the
    # lever rung passes and the run proceeds to the next preflight rung.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_IMPOSTOR_ROLL_CALL="1",
        AILIBI_LLM_MEETING_MODEL="some-other/Model-7B",  # stops the run one rung on
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", "--expect-levers", "impostor_roll_call", env=env)
    out = proc.stdout + proc.stderr
    assert "Substrate slate OK: expected levers ON = impostor_roll_call" in out
    assert "does not match --expect-levers" not in out
    assert proc.returncode != 0  # stopped at the MODEL guard, not the lever guard
    assert "locked model" in out


def test_dry_run_stamps_fsm_default_policy() -> None:
    # Every corpus game carries the 15.9 FSM-default tactical-policy stamp, both in
    # the run_tournament invocation preview and as the MANIFEST policy column.
    proc = _run("--set", "9p2i", "--dry-run")
    assert proc.returncode == 0
    assert "tactical policy stamp: fsm-default" in proc.stdout
    assert "--tactical-policy-stamp fsm-default --force" in proc.stdout
    assert "rows carry the fsm-default policy column" in proc.stdout


def test_dry_run_previews_tournament_invocation_with_roster_flags() -> None:
    proc = _run("--set", "9p2i", "--dry-run")
    assert proc.returncode == 0
    assert "--num-players 9 --num-impostors 2 --tasks-per-crewmate 2" in proc.stdout
    assert "scripts/run_tournament.py" in proc.stdout


def test_dry_run_announces_report_splits_and_freeze() -> None:
    proc = _run("--set", "4p1i", "--dry-run")
    assert proc.returncode == 0
    assert (
        "would rebuild" in proc.stdout and "tournament-eval-report.json" in proc.stdout
    )
    assert "would write" in proc.stdout and "splits.json" in proc.stdout
    assert "would append a FROZEN line naming the git_sha" in proc.stdout


def test_dry_run_announces_split_rule() -> None:
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert "seed mod 5: {0,1,2}=train, {3}=val, {4}=test" in proc.stdout


def test_dry_run_announces_acceptance_commands() -> None:
    # The operator's per-set acceptance (validity gate + byte-verify) is surfaced
    # so the recording is never mistaken for the whole task.
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert "scripts/validity_gate.py" in proc.stdout
    assert "--expected-model Qwen/Qwen3.6-27B --require-zero-cost" in proc.stdout
    assert "scripts/verify_samples.sh" in proc.stdout


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    corpus_root = tmp_path / "ml_corpus"
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--dry-run", env=env)
    assert proc.returncode == 0
    assert not corpus_root.exists()


# -- worker / crash-retry knobs (shared with refresh_samples.sh) --------------


def test_dry_run_defaults_to_two_seed_workers() -> None:
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert "seed workers: 2 parallel" in proc.stdout
    assert "pulls the next available seed from the queue" in proc.stdout


def test_dry_run_worker_count_is_overridable() -> None:
    env = dict(_clean_env(), AILIBI_REFRESH_WORKERS="1")
    proc = _run("--dry-run", env=env)
    assert proc.returncode == 0
    assert "seed workers: 1 (sequential)" in proc.stdout


def test_dry_run_crash_retry_budget_and_override() -> None:
    proc = _run("--set", "9p2i", "--dry-run")
    assert proc.returncode == 0
    assert "seed crash-retry: up to 4 attempt(s)" in proc.stdout

    env = dict(_clean_env(), AILIBI_SEED_MAX_ATTEMPTS="6")
    proc = _run("--set", "9p2i", "--dry-run", env=env)
    assert proc.returncode == 0
    assert "seed crash-retry: up to 6 attempt(s)" in proc.stdout


def test_invalid_worker_count_fails_loud() -> None:
    env = dict(_clean_env(), AILIBI_REFRESH_WORKERS="two")
    proc = _run("--dry-run", env=env)
    assert proc.returncode != 0
    assert "AILIBI_REFRESH_WORKERS must be a positive integer" in (
        proc.stdout + proc.stderr
    )


def test_invalid_seed_max_attempts_fails_loud() -> None:
    env = dict(_clean_env(), AILIBI_SEED_MAX_ATTEMPTS="lots")
    proc = _run("--dry-run", env=env)
    assert proc.returncode != 0
    assert "AILIBI_SEED_MAX_ATTEMPTS must be a positive integer" in (
        proc.stdout + proc.stderr
    )


# -- preflight (LOCKED to featherless; every case fails BEFORE any record) -----


def test_preflight_refuses_non_featherless_provider(tmp_path: Path) -> None:
    # The corpus is baseline-6 == Featherless: any other provider (incl. the fake
    # CI provider) is refused so a corpus game can never be recorded off-substrate.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="anthropic",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env)
    assert proc.returncode != 0
    assert "records ONLY on featherless" in proc.stdout + proc.stderr
    assert not corpus_root.exists()  # refused before any record


def test_preflight_refuses_fake_provider_at_the_committed_corpus_tree() -> None:
    # RETARGETED from the blanket provider refusal (Task 15.12): `fake` is now
    # reachable by name, because the recording engine cannot be tested at all
    # without it. What protects the committed corpus is therefore WHERE a fake
    # run may write, not whether it may run. The default corpus root IS the
    # committed tree, so a bare `fake` run is refused, names both committed set
    # dirs, and stages nothing. (`fake` pointed at a scratch corpus root is
    # allowed — see the hermetic recording family below.)
    env = dict(
        _clean_env(), AILIBI_LLM_PROVIDER="fake", AILIBI_PROMPT_SET="qwen3_6_27b"
    )
    proc = _run(env=env, timeout=180)
    out = proc.stdout + proc.stderr

    assert proc.returncode != 0
    assert "may not write into the repository's replays/ tree" in out
    assert "replays/ml_corpus/9p2i" in out
    assert "replays/ml_corpus/4p1i" in out
    assert "nothing was staged" in out
    assert not list(
        (_REPO_ROOT / "replays" / "ml_corpus").glob("**/.ailibi-corpus-stage-*")
    )


def test_preflight_requires_api_key_before_record(tmp_path: Path) -> None:
    # featherless but no key: fail at preflight, before any tournament invocation.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env)
    assert proc.returncode != 0
    assert "FEATHERLESS_API_KEY must be set" in proc.stdout + proc.stderr
    assert not corpus_root.exists()


def test_preflight_requires_locked_prompt_set_before_record(tmp_path: Path) -> None:
    # A key present but the WRONG (or missing) prompt set must fail loud at the
    # substrate guard, before any seed is staged — so an operator cannot spend a
    # multi-hour run recording the wrong (default 9B) set. A dummy key clears the
    # key check so the substrate guard is what fires; the guard exits before any
    # provider call, so the dummy key is never used.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="wrong_set",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "locked substrate" in out
    assert "AILIBI_PROMPT_SET must be 'qwen3_6_27b'" in out
    assert not corpus_root.exists()


@pytest.mark.parametrize(
    "model_env", ["AILIBI_LLM_MEETING_MODEL", "AILIBI_LLM_TRIGGER_MODEL"]
)
def test_preflight_refuses_non_baseline_model_override(
    tmp_path: Path, model_env: str
) -> None:
    # build_default_client honors the model env knobs for featherless, so a
    # leftover export from a model sweep would record the whole corpus on a
    # non-baseline model while the MANIFEST stamps Qwen/Qwen3.6-27B. The preflight
    # must refuse it BEFORE any record.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    env[model_env] = "some-other/Model-7B"
    proc = _run("--set", "4p1i", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "locked model" in out
    assert model_env in out
    assert not corpus_root.exists()  # refused before any record


@pytest.mark.parametrize("lever_value", ["1", "true"])
def test_preflight_refuses_impostor_roll_call_export(
    tmp_path: Path, lever_value: str
) -> None:
    # impostor_roll_call is the ONE live env-gated toggle left after the Task-18.12
    # meeting-layer graduation (which retired absence_prior — the lever this test
    # previously guarded — alongside roll_call_round /
    # whereabouts_interior_flags / vent_placement_contradictions), and the
    # baseline-6 substrate this recorder freezes is its recorded stay-OFF: the
    # CREW-ONLY ruling did NOT ship the impostor-answer arm
    # (audits/audit-phase-18-meeting-gate.md §9; audits/audit-phase-18-baseline-6.md
    # §0.1). A leftover AILIBI_IMPOSTOR_ROLL_CALL export (e.g. from a
    # counterfactual probe session) would record the whole ~18–20h corpus lever-ON
    # while the preflight echo claims the ruled substrate — and an acceptance gate
    # run in the SAME polluted shell would then PASS coherently
    # (substrate_flag_snapshot() reads the same env). The preflight refuses it
    # BEFORE any record.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    env["AILIBI_IMPOSTOR_ROLL_CALL"] = lever_value
    proc = _run("--set", "4p1i", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "does not match --expect-levers" in out
    assert "impostor_roll_call must be OFF" in out
    assert "unset every other AILIBI_*" in out
    assert not corpus_root.exists()  # refused before any record


def test_preflight_accepts_explicitly_off_impostor_roll_call(tmp_path: Path) -> None:
    # The preflight is a POSITIVE slate check, not a variable-name blacklist: an
    # export that resolves to the ruled state (impostor_roll_call OFF) records the
    # substrate this recorder documents, so it passes the lever gate and the run
    # proceeds to the next preflight rung. Pinned so the check can never regress
    # into refusing a value that agrees with the ruled slate.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_IMPOSTOR_ROLL_CALL="0",
        AILIBI_LLM_MEETING_MODEL="some-other/Model-7B",  # stops the run one rung on
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env)
    out = proc.stdout + proc.stderr
    assert "Locked substrate OK" in out
    assert "does not match --expect-levers" not in out
    assert proc.returncode != 0  # stopped at the MODEL guard, not the lever guard
    assert "locked model" in out


def test_preflight_refuses_non_default_base_url(tmp_path: Path) -> None:
    # build_default_client also honors AILIBI_FEATHERLESS_BASE_URL for
    # featherless, so a leftover mock/staging export would record the whole
    # "hosted-$0" corpus against an alternate endpoint while the MANIFEST stamps
    # the baseline substrate — undetectable by the validity gate if that endpoint
    # echoes the same model id. The preflight must refuse it BEFORE any record.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_FEATHERLESS_BASE_URL="http://localhost:9999/v1",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "hosted Featherless endpoint" in out
    assert "AILIBI_FEATHERLESS_BASE_URL" in out
    assert not corpus_root.exists()  # refused before any record


def test_prompt_version_registry_matches_locked_script_constant() -> None:
    # The corpus contract freezes the prompt VERSIONS (all four templates at
    # v5), not just the set name — the recorder's preflight asserts the live
    # registry still resolves qwen3_6_27b to its locked BASE constant. Pin the
    # two together here: if a later task bumps the registry entry, this test
    # fails and forces the corpus re-lock conversation instead of letting the
    # recorder's guard and the registry drift apart silently. The slate-resolved
    # map the recorder freezes against is derived from that base at runtime; the
    # base is what an owner decision moves.
    from orchestrator.game import PROMPT_VERSION_SETS

    script = _RECORD_SH.read_text(encoding="utf-8")
    match = re.search(
        r'^REQUIRED_PROMPT_VERSIONS_BASE="([^"]+)"$', script, re.MULTILINE
    )
    assert match is not None, (
        "REQUIRED_PROMPT_VERSIONS_BASE constant missing from script"
    )
    locked = match.group(1)
    resolved = ", ".join(sorted(PROMPT_VERSION_SETS["qwen3_6_27b"].values()))
    assert resolved == locked, (
        "PROMPT_VERSION_SETS['qwen3_6_27b'] has moved off the locked "
        "corpus versions; recording/resuming the 15.12 corpus would now drift. "
        "Re-locking is an owner decision (re-record + re-freeze)."
    )


def test_declared_slate_resolves_the_prompt_versions_the_dry_run_prints() -> None:
    # The recorder must freeze against what its meetings STAMP, not against the
    # bare literals: a lever with a prompt-version overlay serves its own arm's
    # strings, so a lever-ON record carries composites. Drive both slates through
    # the committed dry-run and compare each against the registry's own
    # resolution, so the script's derivation cannot drift from the map the
    # manager writes.
    from orchestrator.game import prompt_versions_for_set
    from orchestrator.replay import env_var_for_lever

    wave2 = ("reporter_reasoning", "corroboration_discipline", "testimony_shapes")
    for declared in ((), wave2):
        env = _clean_env()
        env["AILIBI_PROMPT_SET"] = "qwen3_6_27b"
        for key in declared:
            env[env_var_for_lever(key)] = "1"
        proc = _run(
            "--set",
            "9p2i",
            "--dry-run",
            "--expect-levers",
            ",".join(declared),
            env=env,
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        expected = ", ".join(
            sorted(
                prompt_versions_for_set(
                    "qwen3_6_27b",
                    env={env_var_for_lever(key): "1" for key in declared},
                ).values()
            )
        )
        assert f"[{expected}]" in proc.stdout, proc.stdout
    # The loop's expectation is computed from the same registry the script reads,
    # so it would also pass if BOTH went on printing the bare literals. The last
    # iteration is the Wave-2 slate: assert its output actually carries a
    # composite, or the comparison above proves nothing about the lever arm.
    assert "accusation_round.qwen3_6_27b.v5.reporter_reasoning" in proc.stdout


def test_acceptance_pairs_carry_the_maps_own_keys_not_the_version_prefix() -> None:
    # The acceptance line the script prints feeds
    # `validity_gate.py --expected-prompt-versions`, which matches on TEMPLATE
    # KEYS. An arm that swaps a variant FILE serves a value whose first
    # dot-segment is the VARIANT's name while its map key is unchanged, so a key
    # inferred from the version string would print a map the gate rejects AFTER
    # the record froze. impostor_roll_call is exactly that arm, which is why it
    # is the planted case here even though this phase records it OFF.
    from orchestrator.game import prompt_versions_for_set
    from orchestrator.replay import env_var_for_lever

    resolved = prompt_versions_for_set(
        "qwen3_6_27b", env={env_var_for_lever("impostor_roll_call"): "1"}
    )
    # The premise the planted case rests on: at least one key differs from its
    # value's first dot-segment. Without this the test could not fail.
    assert any(key != value.split(".", 1)[0] for key, value in resolved.items()), (
        "impostor_roll_call no longer swaps a variant file; re-plant this case"
    )

    env = _clean_env()
    env["AILIBI_PROMPT_SET"] = "qwen3_6_27b"
    env[env_var_for_lever("impostor_roll_call")] = "1"
    proc = _run(
        "--set",
        "9p2i",
        "--dry-run",
        "--expect-levers",
        "impostor_roll_call",
        env=env,
    )

    assert proc.returncode == 0, proc.stdout + proc.stderr
    expected = ",".join(f"{key}={resolved[key]}" for key in sorted(resolved))
    assert f"--expected-prompt-versions {expected};" in proc.stdout, proc.stdout


# The slates whose STAMP outpaces their BODIES, derived from the registry rather
# than typed here: an arm SWAPS a variant file for template T when its overlay
# value's first dot-segment is not T, and a sibling RE-BODIES T when its overlay
# value for T differs from the default. Deriving the expectation the same way the
# guard does would make the test vacuous, so the pairs are enumerated below and a
# separate case asserts the registry still produces exactly them.
_OUTPACING_PAIRS = (
    ("impostor_roll_call", "reporter_reasoning"),
    ("impostor_roll_call", "testimony_shapes"),
)
_NON_OUTPACING_SLATES = (
    ("reporter_reasoning", "corroboration_discipline", "testimony_shapes"),
    ("impostor_roll_call", "corroboration_discipline"),
    ("impostor_roll_call",),
    ("reporter_reasoning",),
    ("testimony_shapes",),
)


def _env_for(declared: "tuple[str, ...]") -> dict[str, str]:
    from orchestrator.replay import env_var_for_lever

    env = _clean_env()
    env["AILIBI_PROMPT_SET"] = "qwen3_6_27b"
    for key in declared:
        env[env_var_for_lever(key)] = "1"
    return env


def test_the_registry_still_produces_exactly_the_enumerated_outpacing_pairs() -> None:
    # The premise the planted cases rest on. If a future arm changes which
    # templates are swapped or re-bodied, this fails FIRST and says so, instead of
    # letting the refusal tests pass over a set of pairs nobody re-checked.
    from orchestrator.game import PROMPT_VERSION_SETS, prompt_versions_for_set
    from orchestrator.replay import (
        TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
        env_var_for_lever,
    )

    default = PROMPT_VERSION_SETS["qwen3_6_27b"]
    entries = {
        key: prompt_versions_for_set("qwen3_6_27b", env={env_var_for_lever(key): "1"})
        for key in TOGGLEABLE_SUBSTRATE_FLAG_KEYS
    }
    derived = {
        (swapper, sibling)
        for swapper, swapper_entry in entries.items()
        for sibling, sibling_entry in entries.items()
        if sibling != swapper
        for template, value in swapper_entry.items()
        if value.split(".", 1)[0] != template
        and sibling_entry[template] != default[template]
    }

    assert derived == set(_OUTPACING_PAIRS), (
        "the registry's file-swapping arms changed; re-check _OUTPACING_PAIRS "
        f"(derived {sorted(derived)})"
    )


@pytest.mark.parametrize(("swapper", "sibling"), _OUTPACING_PAIRS)
def test_the_startup_derivation_refuses_a_slate_whose_stamps_outpace_its_bodies(
    swapper: str, sibling: str
) -> None:
    # PATH A: the startup derivation, which is where --expect-levers first
    # becomes a map. impostor_roll_call swaps accusation_round.j2 for a variant
    # carrying neither the reporter block nor the testimony_shapes blocks, so
    # with either sibling ON the two compose in the STAMP and not in the BYTES
    # (pinned by tests/meetings/test_prompt_byte_golden.py::
    # test_a_file_swapping_arm_serves_a_body_its_siblings_do_not_reach).
    proc = _run(
        "--set",
        "9p2i",
        "--dry-run",
        "--expect-levers",
        f"{swapper},{sibling}",
        env=_env_for((swapper, sibling)),
    )

    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "outpace its bodies" in out
    assert f"{swapper!r} swaps a variant file for 'accusation_round'" in out
    assert sibling in out
    assert "nothing was recorded" in out


@pytest.mark.parametrize(("swapper", "sibling"), _OUTPACING_PAIRS)
def test_the_preflight_path_refuses_the_same_slate(
    tmp_path: Path, swapper: str, sibling: str
) -> None:
    # PATH B: the preflight's registry check is the SECOND place a derived map is
    # accepted, and the dry-run exits before it. A guard wired into only the
    # startup derivation would leave this path able to freeze a record against
    # provenance its prompts do not carry, so the shared guard is driven here
    # directly out of the committed script.
    driver = _slate_guard_driver(tmp_path)
    proc = subprocess.run(
        ["bash", str(driver), f"{swapper},{sibling}"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=_clean_env(),
        timeout=300,
    )

    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "outpace its bodies" in out
    assert sibling in out


@pytest.mark.parametrize("declared", _NON_OUTPACING_SLATES)
def test_the_outpacing_refusal_reaches_no_slate_without_a_collision(
    tmp_path: Path, declared: "tuple[str, ...]"
) -> None:
    # The refusal must bite on the colliding pairs and nothing else — the Wave-2
    # slate the record runs, each arm alone, and roll_call beside a lever that
    # re-bodies only the ballot. A guard that also refused these would block the
    # record it exists to protect. Both paths are checked.
    proc = _run(
        "--set",
        "9p2i",
        "--dry-run",
        "--expect-levers",
        ",".join(declared),
        env=_env_for(declared),
    )
    assert proc.returncode == 0, (declared, proc.stdout + proc.stderr)
    assert "outpace its bodies" not in (proc.stdout + proc.stderr)

    guard = subprocess.run(
        ["bash", str(_slate_guard_driver(tmp_path)), ",".join(declared)],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=_clean_env(),
        timeout=300,
    )
    assert guard.returncode == 0, (declared, guard.stdout + guard.stderr)


def test_derivation_refuses_an_expect_levers_key_that_is_not_a_live_toggle() -> None:
    # A typo in --expect-levers would otherwise resolve to the BARE map and
    # freeze a lever-ON record against provenance it does not carry, hours after
    # the spend. Refuse before anything stages.
    env = _clean_env()
    env["AILIBI_PROMPT_SET"] = "qwen3_6_27b"
    proc = _run(
        "--set", "9p2i", "--dry-run", "--expect-levers", "reporter_resoning", env=env
    )
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "not a live substrate toggle" in out
    assert "reporter_resoning" in out


_SLATE_GUARD_DRIVER = """\
set -euo pipefail
REPO_ROOT="{repo_root}"
REQUIRED_PROMPT_SET="qwen3_6_27b"
expect_levers="$1"
{functions}
check_slate_bodies_carry_their_stamps
"""


def _slate_guard_driver(tmp_path: Path) -> Path:
    """A driver around the committed body/stamp guard, as the preflight calls it."""

    script = _RECORD_SH.read_text(encoding="utf-8")
    # Anchored on the heredoc terminator, not on the first bare "}": the guard's
    # own Python body closes a dict comprehension at column 0, which a
    # first-brace match would truncate at — silently producing a driver that
    # cannot fail.
    match = re.search(
        r"(?ms)^check_slate_bodies_carry_their_stamps\(\) \{\n.*?\nPYINNER\n\}$",
        script,
    )
    assert match is not None, "check_slate_bodies_carry_their_stamps not found"
    driver = tmp_path / "slate_guard.sh"
    driver.write_text(
        _SLATE_GUARD_DRIVER.format(repo_root=_REPO_ROOT, functions=match.group(0)),
        encoding="utf-8",
    )
    return driver


_PROMPT_VERSION_FREEZE_DRIVER = """\
set -euo pipefail
REPO_ROOT="{repo_root}"
REQUIRED_PROMPT_SET="qwen3_6_27b"
expect_levers="{expect_levers}"
{derivation}
if ! _derived="$(derive_required_prompt_versions)"; then
  exit 1
fi
REQUIRED_PROMPT_VERSIONS="$(printf '%s\\n' "$_derived" | sed -n '1p')"
{check}
check_recorded_prompt_versions "$1" "$2"
"""


def _prompt_version_freeze_driver(tmp_path: Path, expect_levers: str) -> Path:
    """A driver around the committed derivation + freeze-path version check."""

    script = _RECORD_SH.read_text(encoding="utf-8")
    derivation = re.search(
        r"(?ms)^derive_required_prompt_versions\(\) \{\n.*?\n\}$", script
    )
    check = re.search(r"(?ms)^check_recorded_prompt_versions\(\) \{\n.*?\n\}$", script)
    assert derivation is not None, "derive_required_prompt_versions not found"
    assert check is not None, "check_recorded_prompt_versions not found"
    driver = tmp_path / f"prompt_versions_{expect_levers or 'bare'}.sh"
    driver.write_text(
        _PROMPT_VERSION_FREEZE_DRIVER.format(
            repo_root=_REPO_ROOT,
            expect_levers=expect_levers,
            derivation=derivation.group(0),
            check=check.group(0),
        ),
        encoding="utf-8",
    )
    return driver


def _manifest_with_prompt_versions(path: Path, cell: str) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    manifest = path / "MANIFEST.md"
    manifest.write_text(
        "# Sample Replay Manifest\n\n"
        "| seed | model | prompt_versions | flags | policy | refreshed_at | "
        "git_sha | cost_usd | winner |\n"
        "|------|-------|-----------------|-------|--------|--------------|"
        "---------|----------|--------|\n"
        f"| 1000 | Qwen/Qwen3.6-27B | {cell} | reporter_reasoning | fsm-default | "
        "2026-09-02 | abc1234 | 0.0000 | CREWMATES |\n",
        encoding="utf-8",
    )
    return manifest


def _run_prompt_version_check(
    tmp_path: Path, expect_levers: str, cell: str
) -> subprocess.CompletedProcess[str]:
    manifest = _manifest_with_prompt_versions(tmp_path, cell)
    return subprocess.run(
        [
            "bash",
            str(_prompt_version_freeze_driver(tmp_path, expect_levers)),
            str(tmp_path),
            str(manifest),
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=_clean_env(),
        timeout=300,
    )


_BARE_VERSION_CELL = (
    "accusation_round.qwen3_6_27b.v5, crewmate_report.qwen3_6_27b.v5, "
    "impostor_report.qwen3_6_27b.v5, vote_ballot.qwen3_6_27b.v5"
)
_WAVE2_VERSION_CELL = (
    "accusation_round.qwen3_6_27b.v5.reporter_reasoning"
    "+accusation_round.qwen3_6_27b.v5.testimony_shapes, "
    "crewmate_report.qwen3_6_27b.v5.reporter_reasoning"
    "+crewmate_report.qwen3_6_27b.v5.testimony_shapes, "
    "impostor_report.qwen3_6_27b.v5, "
    "vote_ballot.qwen3_6_27b.v5.corroboration_discipline"
    "+vote_ballot.qwen3_6_27b.v5.testimony_shapes"
)
_WAVE2_SLATE = "reporter_reasoning,corroboration_discipline,testimony_shapes"


def test_freeze_accepts_the_rows_the_declared_slate_stamps(tmp_path: Path) -> None:
    # Both directions of the derivation, on the freeze path that actually breaks
    # a record: a bare-slate run accepts the base literals, and a Wave-2 run
    # accepts the composites its own meetings stamp.
    bare = _run_prompt_version_check(tmp_path / "bare", "", _BARE_VERSION_CELL)
    assert bare.returncode == 0, bare.stdout + bare.stderr
    wave2 = _run_prompt_version_check(
        tmp_path / "wave2", _WAVE2_SLATE, _WAVE2_VERSION_CELL
    )
    assert wave2.returncode == 0, wave2.stdout + wave2.stderr


@pytest.mark.parametrize(
    ("expect_levers", "planted_cell"),
    [
        # The defect this fix removes: a lever-ON record whose rows carry the
        # bare literals. Before the derivation the guard compared against those
        # literals and PASSED, so the failure landed only at the end of a
        # multi-hour spend; now the row is refused for the provenance it lacks.
        (_WAVE2_SLATE, _BARE_VERSION_CELL),
        # The mirror: a bare-slate freeze must refuse rows stamped by an ON run.
        ("", _WAVE2_VERSION_CELL),
    ],
)
def test_freeze_refuses_rows_recorded_under_another_slate(
    tmp_path: Path, expect_levers: str, planted_cell: str
) -> None:
    proc = _run_prompt_version_check(tmp_path, expect_levers, planted_cell)

    assert proc.returncode != 0, proc.stdout + proc.stderr
    out = proc.stdout + proc.stderr
    assert "do not carry EXACTLY the slate-resolved prompt versions" in out
    assert "seed 1000" in out


def test_record_path_accepts_baseline_model_override_and_rejects_stray_replay(
    tmp_path: Path,
) -> None:
    # Several guards in one hermetic run of the REAL record path (no network: the
    # run stops before any tournament invocation):
    # * an override explicitly set TO the baseline model is not a drift risk, so
    #   the model preflight passes it ("Locked model OK");
    # * a base-URL override explicitly set TO the hosted endpoint likewise passes
    #   ("Locked endpoint OK"), and the registry check confirms the locked prompt
    #   versions ("Locked prompt versions OK");
    # * a stray replay outside the set's locked seed range then fails the
    #   pre-spend check_seed_range, BEFORE any seed is staged — proving both that
    #   the range guard fires in the record path and that it fails before spend.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = _stub_set(corpus_root, "4p1i", [1000, 1001, 2000])  # 2000 is stray
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_LLM_MEETING_MODEL="Qwen/Qwen3.6-27B",
        AILIBI_LLM_TRIGGER_MODEL="Qwen/Qwen3.6-27B",
        AILIBI_FEATHERLESS_BASE_URL="https://api.featherless.ai/v1",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "Locked model OK" in out  # baseline-valued override passed the guard
    assert "Locked endpoint OK" in out  # default-valued base URL passed the guard
    assert "Locked prompt versions OK" in out  # registry matches the locked map
    assert "locked seed range 1000..1049" in out
    assert "replay-seed-2000.jsonl" in out
    # Failed BEFORE any record/finalize: no roster.json, manifest, or splits.
    assert set(p.name for p in set_dir.iterdir()) == {
        "replay-seed-1000.jsonl",
        "replay-seed-1001.jsonl",
        "replay-seed-2000.jsonl",
    }


def test_record_path_refuses_unstamped_present_replay(tmp_path: Path) -> None:
    # File presence is not provenance (Task 15.9 / 15.12): the resume skip-scan
    # treats a present in-range replay as "already recorded", but an UNSTAMPED
    # replay renders in the MANIFEST policy column identically to a stamped one
    # and the validity gate never checks the stamp — so the recorder must refuse
    # it BEFORE any spend. Fixture: a committed CANONICAL sample (predates the
    # 15.9 stamp, so read_tactical_policy_stamp() returns None) copied into the
    # corpus set dir under an in-range seed name. Hermetic: fails before any
    # tournament invocation.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    unstamped = _REPO_ROOT / "replays" / "samples" / "4p1i" / "replay-seed-0.jsonl"
    shutil.copyfile(unstamped, set_dir / "replay-seed-1000.jsonl")
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_replay_provenance" in out
    assert "replay-seed-1000.jsonl: no tactical_policy stamp" in out
    # Refused BEFORE the roster pin / any record: the dir still holds only the
    # offending replay.
    assert {p.name for p in set_dir.iterdir()} == {"replay-seed-1000.jsonl"}


def test_record_path_accepts_stamped_present_replay(tmp_path: Path) -> None:
    # The positive half: a present replay whose bytes DO carry the explicit
    # fsm-default stamp (the committed corpus game, rebased onto the baseline
    # model) passes the policy guard, and the run proceeds to the next pre-spend
    # step — pinned here by a roster.json that disagrees with the set's config,
    # which fails loud AFTER the stamp check and still before any tournament
    # invocation.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    # The committed corpus IS the baseline-6 record; the rebase is a no-op safety
    # net so a substrate-current stamped replay is present for the guard.
    (set_dir / "replay-seed-1000.jsonl").write_text(
        _baseline6_corpus_replay_text(), encoding="utf-8"
    )
    (set_dir / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2})
    )
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    # The stamp guard passed (no policy complaint) ...
    assert "check_replay_provenance" not in out
    # ... and the failure is the roster conflict, the step AFTER the guard.
    assert "disagrees with the requested roster" in out


def test_an_audit_sidecar_is_refused_by_range_not_misread_as_a_stampless_replay(
    tmp_path: Path,
) -> None:
    # The planted case for the <n>.audit guard, and it pins WHICH guard speaks.
    #
    # A wrapper writes each seed's observation log as replay-seed-<n>.audit.jsonl,
    # and BOTH scans over that glob match it. check_seed_range refuses it as a
    # stray file — pre-spend, naming the real cause. check_replay_provenance must
    # NOT also report it as a stampless replay: that message is wrong (the file is
    # not a replay) and it is the one that arrives at the END of a multi-hour leg.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    (set_dir / "replay-seed-1000.jsonl").write_text(
        _baseline6_corpus_replay_text(), encoding="utf-8"
    )
    # The sidecar: a real one holds observation packets, and carries no stamp.
    (set_dir / "replay-seed-1000.audit.jsonl").write_text(
        '{"kind": "observation_packet"}\n', encoding="utf-8"
    )
    (set_dir / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2})
    )
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )

    proc = _run("--set", "4p1i", env=env, timeout=120)

    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    # The range guard speaks, names the file, and refuses BEFORE any spend.
    assert "check_seed_range" in out
    assert "replay-seed-1000.audit.jsonl" in out
    # The provenance scan does NOT: it skipped the sidecar rather than judging it.
    assert "check_replay_provenance" not in out
    assert "no tactical_policy stamp" not in out


def test_record_path_refuses_non_canonical_stamp_fields(tmp_path: Path) -> None:
    # Matching policy_id alone is not enough: a hand-crafted stamp with
    # policy_id="fsm-default" but non-canonical method/encoder/weights/anchor
    # fields renders identically in the MANIFEST policy column, so the guard must
    # compare the FULL five-field stamp to fsm_default_tactical_policy_stamp().
    # Fixture: a committed corpus replay with its game_over stamp's method field
    # doctored. Hermetic: refused before any tournament invocation.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    # Baseline-6-rebased committed replay, then doctor the game_over stamp's
    # method field.
    lines = _baseline6_corpus_replay_text().splitlines()
    for i, line in enumerate(lines):
        record = json.loads(line)
        if record.get("kind") == "game_over" and record.get("tactical_policy"):
            record["tactical_policy"]["method"] = "hand-edited"
            lines[i] = json.dumps(record, separators=(",", ":"))
    (set_dir / "replay-seed-1000.jsonl").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_replay_provenance" in out
    assert "differs from the canonical" in out
    assert "hand-edited" in out


def test_record_path_refuses_non_baseline_model_in_replay_bytes(
    tmp_path: Path,
) -> None:
    # The model/endpoint preflights only govern seeds recorded by THIS run; a
    # resumed replay recorded under another model (but carrying a valid stamp)
    # must be refused by its BYTES before the skip-scan treats it as complete —
    # not left for the external validity gate to fail after the freeze. Fixture:
    # the baseline-6-rebased committed replay with every recorded model id then
    # rewritten to a foreign model. Hermetic: refused before any tournament
    # invocation.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    doctored = _baseline6_corpus_replay_text().replace(
        '"model":"Qwen/Qwen3.6-27B"', '"model":"Other/Model-32B"'
    )
    assert '"model":"Other/Model-32B"' in doctored  # the fixture has LLM calls
    (set_dir / "replay-seed-1000.jsonl").write_text(doctored, encoding="utf-8")
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_replay_provenance" in out
    assert "non-baseline model(s) recorded: Other/Model-32B" in out


def test_record_path_refuses_stale_baseline5_substrate_slate(tmp_path: Path) -> None:
    # The 17.9 POSITIVE slate gate, negative direction, re-grounded at 18.13: a
    # present replay carrying the STALE baseline-5 substrate slate (the nine-lever
    # set, missing the four Task-18.12 meeting-layer graduations) is refused by its
    # BYTES, not just by the env preflight — so the PRIOR corpus recording can
    # never be resumed-over and silently frozen into the baseline-6 corpus.
    # Fixture: the substrate-current replay with its game_over substrate stamp
    # rewritten to the nine-lever baseline-5 slate, so the model check passes and
    # the slate check fires. (Synthesized rather than read off disk: the committed
    # corpus is itself the baseline-6 re-record now, so it no longer carries a
    # stale slate to borrow.)
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    stale_substrate = _rewrite_game_over_substrate(
        _baseline6_corpus_replay_text(), _STALE_BASELINE5_SLATE
    )
    (set_dir / "replay-seed-1000.jsonl").write_text(stale_substrate, encoding="utf-8")
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_replay_provenance" in out
    assert "disagrees with the declared lever slate" in out
    # The four missing meeting-layer graduations are named — the substrate axis
    # this re-record discharges.
    assert "roll_call_round" in out
    assert "whereabouts_interior_flags" in out
    assert "vent_placement_contradictions" in out
    assert "absence_prior" in out


def test_record_path_refuses_impostor_roll_call_on_in_recorded_slate(
    tmp_path: Path,
) -> None:
    # The slate gate also refuses a replay whose game_over stamp records
    # impostor_roll_call ON: after the Task-18.12 baseline-6 graduation the four
    # meeting-layer levers are unconditional and impostor_roll_call is the SOLE
    # remaining default-OFF toggle (the CREW-ONLY ruling did not ship it), so a
    # lever-ON recording (e.g. bytes from an impostor-arm probe session) must be
    # refused by its BYTES even though the model + stamp + cost are all
    # baseline-current. (``_BASELINE6_SUBSTRATE_SLATE`` reads the live snapshot, so
    # it carries the baseline-6 slate; before graduation this deviation was flipped
    # on absence_prior, which has since graduated into the always-on set.)
    # Fixture: the substrate-current replay with impostor_roll_call flipped True.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    lever_on = dict(_BASELINE6_SUBSTRATE_SLATE)
    lever_on["impostor_roll_call"] = True
    (set_dir / "replay-seed-1000.jsonl").write_text(
        _rewrite_game_over_substrate(_baseline6_corpus_replay_text(), lever_on),
        encoding="utf-8",
    )
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_replay_provenance" in out
    assert "disagrees with the declared lever slate" in out
    assert "impostor_roll_call" in out


def _on_slate_corpus_replay_text() -> str:
    """The committed corpus replay re-stamped with the DECLARED on-slate substrate.

    ``_on_slate_env`` exports the one live toggle, so a replay carrying the bare
    stamp is off-slate by construction; this is the matching fixture.
    """

    on_slate = dict(_BASELINE6_SUBSTRATE_SLATE)
    on_slate["impostor_roll_call"] = True
    text = _COMMITTED_CORPUS_REPLAY.read_text(encoding="utf-8").replace(
        f'"model":"{_STALE_CORPUS_MODEL}"', f'"model":"{_BASELINE_MODEL}"'
    )
    return _rewrite_game_over_substrate(text, on_slate)


def _on_slate_env(corpus_root: Path) -> dict[str, str]:
    """A locked-substrate env with ONE Phase-20 lever exported."""

    return dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_IMPOSTOR_ROLL_CALL="1",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )


def test_record_path_accepts_a_replay_stamped_with_the_declared_slate(
    tmp_path: Path,
) -> None:
    # The freeze guard judges recorded stamps against the slate the operator
    # DECLARED, not against a frozen bare snapshot -- otherwise a lever-ON record
    # would be refused seed by seed by its own recorder. A replay whose stamp
    # carries the declared lever passes; the run then stops at the roster
    # conflict, the step AFTER the guard.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    (set_dir / "replay-seed-1000.jsonl").write_text(
        _on_slate_corpus_replay_text(), encoding="utf-8"
    )
    (set_dir / "roster.json").write_text(
        json.dumps({"num_players": 9, "num_impostors": 2, "tasks_per_crewmate": 2})
    )
    proc = _run(
        "--set",
        "4p1i",
        "--expect-levers",
        "impostor_roll_call",
        env=_on_slate_env(corpus_root),
        timeout=120,
    )
    out = proc.stdout + proc.stderr
    assert "Substrate slate OK: expected levers ON = impostor_roll_call" in out
    assert "check_replay_provenance" not in out
    assert "disagrees with the requested roster" in out


def test_record_path_refuses_a_bare_slate_replay_inside_an_on_slate_record(
    tmp_path: Path,
) -> None:
    # The other direction, and the reason the guard cannot simply be relaxed: a
    # replay recorded BEFORE the lever was exported is a different substrate, so
    # dropping it into an ON-slate set must be refused BY NAME rather than swept
    # into the freeze because it happens to be present.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    (set_dir / "replay-seed-1000.jsonl").write_text(
        _baseline6_corpus_replay_text(), encoding="utf-8"
    )
    proc = _run(
        "--set",
        "4p1i",
        "--expect-levers",
        "impostor_roll_call",
        env=_on_slate_env(corpus_root),
        timeout=120,
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0
    assert "check_replay_provenance" in out
    assert "disagrees with the declared lever slate" in out
    assert "impostor_roll_call" in out


def test_record_path_refuses_missing_substrate_stamp(tmp_path: Path) -> None:
    # A replay carrying the canonical fsm-default stamp, the baseline model, and $0
    # cost but NO game_over substrate_flags stamp (a pre-14.7 recording) is refused:
    # presence + a policy stamp is not enough, the baseline-6 lever slate must be
    # positively present in the bytes. Fixture: the substrate-current replay with
    # its game_over substrate_flags stripped out entirely.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    set_dir.mkdir(parents=True)
    lines = _baseline6_corpus_replay_text().splitlines()
    for i, line in enumerate(lines):
        record = json.loads(line)
        if record.get("kind") == "game_over":
            record.pop("substrate_flags", None)
            lines[i] = json.dumps(record, separators=(",", ":"))
    (set_dir / "replay-seed-1000.jsonl").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="featherless",
        FEATHERLESS_API_KEY="test-key-unused",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env, timeout=120)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_replay_provenance" in out
    assert "no substrate_flags stamp on game_over" in out


# -- splits-only (hermetic; no network, no record) ----------------------------


def _stub_set(corpus_root: Path, set_name: str, seeds: list[int]) -> Path:
    set_dir = corpus_root / set_name
    set_dir.mkdir(parents=True)
    for seed in seeds:
        (set_dir / f"replay-seed-{seed}.jsonl").write_text("{}\n")
    return set_dir


def test_splits_only_emits_deterministic_partition(tmp_path: Path) -> None:
    # The EXACT locked 9p2i set (150 games) — --splits-only refuses a short set
    # (see test_splits_only_refuses_a_short_set), so the partition is exercised on
    # the real committed shape (90/30/30), not a toy subset.
    corpus_root = tmp_path / "ml_corpus"
    seeds = list(range(1000, 1150))
    set_dir = _stub_set(corpus_root, "9p2i", seeds)
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "9p2i", "--splits-only", env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    doc = json.loads((set_dir / "splits.json").read_text())
    train, val, test = set(doc["train"]), set(doc["val"]), set(doc["test"])
    # By-game split: the three buckets are disjoint and cover exactly the games.
    assert train & val == set()
    assert train & test == set()
    assert val & test == set()
    assert train | val | test == set(seeds)
    # Deterministic rule: seed mod 5 -> {0,1,2}=train, {3}=val, {4}=test.
    for seed in seeds:
        bucket = (
            "train" if seed % 5 in (0, 1, 2) else "val" if seed % 5 == 3 else "test"
        )
        assert seed in doc[bucket], (seed, bucket)
    assert doc["set"] == "9p2i"
    assert doc["total_games"] == len(seeds)
    assert doc["counts"] == {"train": 90, "val": 30, "test": 30}


def test_splits_only_writes_no_replays_and_makes_no_network_call(
    tmp_path: Path,
) -> None:
    # splits-only is pure: it reads the on-disk replay filenames and writes
    # splits.json, never invoking a provider. Prove it never records by stripping
    # every provider key AND leaving the set with only stub replays.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = _stub_set(corpus_root, "4p1i", list(range(1000, 1050)))
    before = {p.name for p in set_dir.iterdir()}
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "4p1i", "--splits-only", env=env, timeout=60)
    assert proc.returncode == 0
    after = {p.name for p in set_dir.iterdir()}
    # Only splits.json was added; no replay-seed-*.jsonl was recorded/removed.
    assert after - before == {"splits.json"}


def test_splits_only_missing_set_dir_fails_loud(tmp_path: Path) -> None:
    corpus_root = tmp_path / "ml_corpus"
    corpus_root.mkdir()
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "9p2i", "--splits-only", env=env)
    assert proc.returncode != 0
    assert "does not exist" in proc.stdout + proc.stderr


def test_splits_only_empty_set_dir_fails_loud(tmp_path: Path) -> None:
    # An empty set dir is a degenerate short set: every locked seed is missing, so
    # the exact-count guard refuses it before write_splits is ever reached.
    corpus_root = tmp_path / "ml_corpus"
    (corpus_root / "9p2i").mkdir(parents=True)  # exists but holds no replays
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "9p2i", "--splits-only", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_seed_count" in out
    assert "150 MISSING seed(s)" in out
    assert not (corpus_root / "9p2i" / "splits.json").exists()


def test_splits_only_refuses_a_short_set(tmp_path: Path) -> None:
    # The exact-count guard (PR #301 review): a set missing even ONE in-range seed
    # is refused before any splits.json is written, so a partial train/val/test can
    # never be committed. Plant 149 of the 150 locked 9p2i seeds.
    corpus_root = tmp_path / "ml_corpus"
    seeds = [s for s in range(1000, 1150) if s != 1073]  # drop one
    set_dir = _stub_set(corpus_root, "9p2i", seeds)
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "9p2i", "--splits-only", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "check_seed_count" in out
    assert "1 MISSING seed(s): [1073]" in out
    assert "Refusing to freeze a short/dirty corpus" in out
    assert not (set_dir / "splits.json").exists()


def test_splits_only_rejects_out_of_range_replay(tmp_path: Path) -> None:
    # A stray replay outside the set's locked seed range (here: a 9p2i seed range
    # file of 1000..1149) must fail loud rather than be partitioned into the
    # committed splits.json (and, in the record path, frozen into the corpus).
    corpus_root = tmp_path / "ml_corpus"
    set_dir = _stub_set(corpus_root, "9p2i", [1000, 1001, 1150])  # 1150 > 1149
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "9p2i", "--splits-only", env=env)
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "locked seed range 1000..1149" in out
    assert "replay-seed-1150.jsonl" in out
    assert not (set_dir / "splits.json").exists()


def test_splits_only_rejects_non_canonical_seed_alias(tmp_path: Path) -> None:
    # A zero-padded alias parses to an in-range seed but is a DUPLICATE of the
    # canonical filename — reject it instead of double-counting the game.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = _stub_set(corpus_root, "4p1i", [1000, 1001])
    (set_dir / "replay-seed-01001.jsonl").write_text("{}\n")
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "4p1i", "--splits-only", env=env)
    assert proc.returncode != 0
    assert "replay-seed-01001.jsonl" in proc.stdout + proc.stderr
    assert not (set_dir / "splits.json").exists()


def test_splits_only_both_sets(tmp_path: Path) -> None:
    corpus_root = tmp_path / "ml_corpus"
    _stub_set(corpus_root, "9p2i", list(range(1000, 1150)))
    _stub_set(corpus_root, "4p1i", list(range(1000, 1050)))
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--splits-only", env=env)
    assert proc.returncode == 0
    for set_name, total in (("9p2i", 150), ("4p1i", 50)):
        doc = json.loads((corpus_root / set_name / "splits.json").read_text())
        assert doc["set"] == set_name
        assert doc["total_games"] == total


# -- the seed subset (--seeds) ------------------------------------------------
#
# The operator mode the sibling recorder has carried since its first version:
# repairing one bad seed of a 150-seed locked range takes minutes instead of a
# whole multi-hour leg. It never widens what may be FROZEN — the finalize still
# demands the exact locked set.


def test_usage_documents_the_seed_subset() -> None:
    proc = _run("--help")
    assert proc.returncode == 0
    assert "--seeds N,N,N" in proc.stdout
    assert "operator" in proc.stdout.lower()


def test_seeds_requires_a_value() -> None:
    proc = _run("--seeds")
    assert proc.returncode != 0
    assert "--seeds requires a comma-separated seed list" in proc.stdout + proc.stderr


def test_seeds_refuses_an_empty_list() -> None:
    proc = _run("--seeds", ",", "--dry-run")
    assert proc.returncode != 0
    assert "--seeds names no seed" in proc.stdout + proc.stderr


def test_seeds_refuses_a_non_numeric_entry() -> None:
    proc = _run("--seeds", "1000,ten", "--dry-run")
    assert proc.returncode != 0
    assert "invalid --seeds entry" in proc.stdout + proc.stderr


def test_seeds_and_splits_only_are_mutually_exclusive() -> None:
    proc = _run("--seeds", "1000", "--splits-only")
    assert proc.returncode != 0
    assert "--seeds and --splits-only are mutually exclusive" in (
        proc.stdout + proc.stderr
    )


def test_seeds_composes_with_dry_run_and_set() -> None:
    proc = _run("--set", "4p1i", "--dry-run", "--seeds", "1000, 1001,1000")
    assert proc.returncode == 0
    # De-duplicated and normalized, so a typo cannot double-record a seed.
    assert "[dry-run] seed subset: --seeds 1000,1001" in proc.stdout
    assert "a subset run finalizes NOTHING" in proc.stdout


def test_seeds_refuses_a_digit_string_that_would_overflow_bash_arithmetic() -> None:
    # $(( )) is fixed-width: 18446744073709552616 wraps to exactly 1000, which is
    # inside BOTH locked ranges, so converting before validating would silently
    # record or replace a real game from a nonsense input. Rejected on width,
    # before any arithmetic touches it.
    assert 18446744073709552616 % 2**64 == 1000  # the alias this refuses

    proc = _run("--set", "4p1i", "--dry-run", "--seeds", "18446744073709552616")

    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "has more digits than any seed can" in out
    assert "18446744073709552616" in out


def test_seeds_still_accepts_a_leading_zero_alias() -> None:
    # The width guard must not cost the canonicalization it replaced: 01000 is
    # still seed 1000, and naming it twice still de-duplicates to one.
    proc = _run("--set", "4p1i", "--dry-run", "--seeds", "01000,1000")

    assert proc.returncode == 0
    assert "[dry-run] seed subset: --seeds 1000" in proc.stdout


def test_seeds_refuses_a_seed_outside_the_locked_range(tmp_path: Path) -> None:
    # Before the set dir is created: a typo costs nothing.
    corpus_root = tmp_path / "ml_corpus"
    proc = _run(
        "--set",
        "4p1i",
        "--seeds",
        "1049,1050",
        env=_fake_env(corpus_root),
        timeout=180,
    )
    assert proc.returncode != 0
    out = proc.stdout + proc.stderr
    assert "--seeds names seed 1050, outside 4p1i's locked range 1000..1049" in out
    assert not (corpus_root / "4p1i").exists()


def test_the_dry_run_refuses_an_out_of_range_seed_too() -> None:
    # An operator previewing a repair command must learn there that the seed does
    # not exist — a preview that says the plan is fine and a real run that
    # refuses it describe different commands.
    proc = _run("--set", "4p1i", "--dry-run", "--seeds", "1050")
    assert proc.returncode != 0
    assert "--seeds names seed 1050, outside 4p1i's locked range 1000..1049" in (
        proc.stdout + proc.stderr
    )


def test_a_seed_valid_for_one_set_is_still_refused_before_the_first_set_records(
    tmp_path: Path,
) -> None:
    # 9p2i locks 1000..1149 and 4p1i 1000..1049, so `--set both --seeds 1100` is
    # half-valid — and `both` is the DEFAULT. Validating per set inside the
    # record loop would be too late: the 9p2i leg would record (on the hosted
    # provider, for hours) and could even freeze before the run failed on a seed
    # the SECOND set never had. The refusal must land before either set is
    # touched, which is what "nothing recorded" has to mean here.
    corpus_root = tmp_path / "ml_corpus"
    proc = _run("--seeds", "1100", env=_fake_env(corpus_root), timeout=300)
    out = proc.stdout + proc.stderr

    assert proc.returncode != 0
    assert "--seeds names seed 1100, outside 4p1i's locked range 1000..1049" in out
    assert not corpus_root.exists()  # NEITHER set was created
    assert "Recording corpus set 9p2i" not in out

    # The dry-run refuses identically, so the preview and the real run can never
    # describe different commands.
    preview = _run("--dry-run", "--seeds", "1100")
    assert preview.returncode != 0
    assert "outside 4p1i's locked range" in preview.stdout + preview.stderr


# -- the hermetic recording path ----------------------------------------------
#
# `fake` is the only provider that can drive the worker pool without spending, so
# these cases are what cover record_set's ~355-line recording engine: run_worker /
# claim_next_seed / record_one_seed / acquire_lock and the lock-guarded MANIFEST
# merge. Every one records into a scratch corpus root under tmp_path; the script
# refuses a target under replays/ outright, which is what protects the committed
# corpus now that `fake` is reachable at all.
#
# COVERAGE BOUNDARY, stated rather than implied: a fake recording can never reach
# the FREEZE. check_seed_count refuses a short set and check_replay_provenance
# refuses non-baseline bytes, both before freeze_manifest — correctly. So the
# family ends at the loud "NOT freezing" refusal with its replays and MANIFEST
# rows on disk, and freeze_manifest gets its own verbatim-extraction driver below.

_FAKE_MODEL = "fake-meeting"


def _fake_env(corpus_root: Path) -> dict[str, str]:
    """A hermetic recording env: the fake provider into a scratch corpus root."""

    return dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )


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


def test_default_fake_model_mirrors_the_fake_client() -> None:
    # A fake row must be attributable as a fake row: the shell constant used for
    # MANIFEST attribution is pinned against the id the fake client actually
    # reports, so a hermetic recording can never render as a Featherless row.
    from llm.fake_provider import _FAKE_MEETING_MODEL

    script = _RECORD_SH.read_text(encoding="utf-8")
    match = re.search(r'^DEFAULT_FAKE_MODEL="([^"]+)"$', script, re.MULTILINE)
    assert match is not None, "DEFAULT_FAKE_MODEL constant missing from script"
    assert match.group(1) == _FAKE_MEETING_MODEL == _FAKE_MODEL


def test_fake_run_records_seeds_end_to_end_and_stops_at_the_freeze_refusal(
    tmp_path: Path,
) -> None:
    # The whole recording engine, hermetically: two seeds are claimed, recorded,
    # moved into the set dir and manifested; the per-run stage dir is discarded;
    # and the run ends at the exact-set refusal rather than freezing a subset.
    corpus_root = tmp_path / "ml_corpus"
    proc = _run(
        "--set", "4p1i", "--seeds", "1000,1001", env=_fake_env(corpus_root), timeout=900
    )
    combined = proc.stdout + proc.stderr
    # The abort this path dies on under macOS's stock Bash 3.2 if the lock owner
    # pid is not written as ${BASHPID:-$$}.
    assert "unbound variable" not in combined

    set_dir = corpus_root / "4p1i"
    assert (set_dir / "replay-seed-1000.jsonl").is_file()
    assert (set_dir / "replay-seed-1001.jsonl").is_file()

    rows = _manifest_data_rows(set_dir / "MANIFEST.md")
    assert [int(cells[0]) for cells in rows] == [1000, 1001]
    for cells in rows:
        # No fake row renders as a real one: the fake client's own model id, and
        # the $0 the hermetic provider actually cost.
        assert cells[1] == _FAKE_MODEL
        assert cells[7] == "0.0000"
    assert (set_dir / "MANIFEST.md").read_text(encoding="utf-8").count(
        "# Sample Replay Manifest"
    ) == 1

    # The per-run stage dir is gone (the RETURN trap discarded it).
    assert not list(set_dir.glob(".ailibi-corpus-stage-*"))

    # ... and the run stopped at the freeze refusal, with the bytes preserved.
    assert proc.returncode != 0
    assert "is not the exact locked seed set; NOT freezing" in combined
    assert "**FROZEN**" not in (set_dir / "MANIFEST.md").read_text(encoding="utf-8")
    assert not (set_dir / "splits.json").exists()


def test_a_subset_run_finalizes_nothing_even_on_a_complete_set(
    tmp_path: Path,
) -> None:
    # The repair case the seed-count check alone cannot express: every locked
    # seed IS on disk after the repair, so the count passes — and the finalize
    # would then rebuild the eval report, rewrite splits.json and re-stamp the
    # FROZEN line under the REPAIR run's sha. A one-seed operation must not
    # restamp set-level provenance as a side effect, so a subset run finalizes
    # nothing and says which command does.
    # The committed 4p1i corpus is the real, FROZEN, provenance-clean set an
    # operator would be repairing — copied to scratch, with one seed dropped as
    # if it had been found bad. Real bytes are required: the pre-spend
    # provenance guard reads every replay already present, so stubs would be
    # refused long before the finalize this case is about.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    shutil.copytree(_REPO_ROOT / "replays" / "ml_corpus" / "4p1i", set_dir)
    (set_dir / "replay-seed-1000.jsonl").unlink()
    manifest = set_dir / "MANIFEST.md"
    frozen_before = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.startswith("**FROZEN**")
    ]
    assert len(frozen_before) == 1, "the committed corpus should arrive frozen"
    # The set-level artifacts a finalize would rewrite, as they stand.
    set_level_before = {
        name: (set_dir / name).read_bytes()
        for name in ("splits.json", "tournament-eval-report.json")
        if (set_dir / name).is_file()
    }
    assert set_level_before, "the committed corpus should ship its set-level artifacts"

    proc = _run(
        "--set", "4p1i", "--seeds", "1000", env=_fake_env(corpus_root), timeout=900
    )
    out = proc.stdout + proc.stderr

    # The repair itself worked...
    assert (set_dir / "replay-seed-1000.jsonl").is_file(), out
    # ... and every locked seed is now present, so the count check PASSED — only
    # the subset guard can be what stopped the finalize.
    assert "is not the exact locked seed set" not in out
    assert "--seeds recorded a subset, so the finalize is skipped; NOT freezing" in out
    assert "Re-run without --seeds" in out
    # Nothing set-level was rebuilt.
    assert {
        name: (set_dir / name).read_bytes() for name in set_level_before
    } == set_level_before
    # And the set does not claim to be frozen: the per-seed MANIFEST update
    # re-renders the table and drops the stale FROZEN line (by design — an
    # incomplete or repaired set must never be left LOOKING frozen), while the
    # skipped finalize adds no new one. So a repair leaves the set honestly
    # unfrozen rather than re-stamped under the repair run's sha, which is the
    # whole point of refusing to finalize here.
    frozen_after = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.startswith("**FROZEN**")
    ]
    assert frozen_after == []
    assert frozen_before[0] not in manifest.read_text(encoding="utf-8")
    # ... and the closing block does not print acceptance commands for a set it
    # never froze.
    assert "no set was finalized or frozen" in proc.stdout
    assert "validity_gate.py" not in proc.stdout


def test_fake_run_bash_trace_names_the_worker_pool(tmp_path: Path) -> None:
    # Coverage proof that survives a reworded progress string: the xtrace of a
    # real (non-dry-run) recording must show the four pool functions invoked.
    corpus_root = tmp_path / "ml_corpus"
    proc = subprocess.run(
        ["bash", "-x", str(_RECORD_SH), "--set", "4p1i", "--seeds", "1000"],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=_fake_env(corpus_root),
        timeout=900,
    )
    assert (corpus_root / "4p1i" / "replay-seed-1000.jsonl").is_file(), proc.stderr[
        -4000:
    ]
    for function in (
        "run_worker",
        "claim_next_seed",
        "record_one_seed",
        "acquire_lock",
    ):
        assert re.search(rf"^\++ {function}\b", proc.stderr, re.MULTILINE), function


def test_two_workers_lose_no_manifest_row(tmp_path: Path) -> None:
    # MANIFEST.md is a whole-file read-modify-write
    # (_manifest_writer.update_manifest), so two workers updating different seeds
    # concurrently would leave one row silently missing — and a missing row is
    # fatal at the next verify gate. The lock-guarded merge is what prevents it;
    # this pins that it holds. (Replays are staged per-seed and land via an atomic
    # `mv -f`, so the race could never TRUNCATE a replay: the exposure is the
    # lost row.)
    corpus_root = tmp_path / "ml_corpus"
    env = dict(_fake_env(corpus_root), AILIBI_REFRESH_WORKERS="2")
    proc = _run("--set", "4p1i", "--seeds", "1000,1001,1002,1003", env=env, timeout=900)
    out = proc.stdout + proc.stderr
    assert "Recording 4 seeds with 2 parallel workers" in proc.stdout, out

    set_dir = corpus_root / "4p1i"
    rows = _manifest_data_rows(set_dir / "MANIFEST.md")
    # None lost, none doubled.
    assert [int(cells[0]) for cells in rows] == [1000, 1001, 1002, 1003]
    for seed in range(1000, 1004):
        assert (set_dir / f"replay-seed-{seed}.jsonl").is_file()
        # The claim counter is lock-guarded, so no seed is recorded twice.
        assert proc.stdout.count(f"recording 4p1i seed {seed} ---") == 1
    # WHICH worker drains which seed is up to the scheduler, so asserting a
    # particular split would be a timing assumption. What holds under every
    # split: every seed was claimed by a worker of the spawned pool, once.
    claims = re.findall(r"--- \[worker (\d+)\] recording 4p1i seed", proc.stdout)
    assert len(claims) == 4
    assert set(claims) <= {"1", "2"}


def _failing_uv_shim(tmp_path: Path, *, fail_seed: int) -> str:
    """A PATH entry whose ``uv`` fails ONE seed's tournament and passes the rest.

    Deterministic by construction: the failure is keyed on the seed argument, not
    on timing, so ``record_one_seed``'s fail-loud branch is exercised without a
    race. Every other ``uv run`` (the preflights, the manifest writer) execs the
    real binary.
    """

    real_uv = shutil.which("uv")
    assert real_uv is not None, "uv is required to drive the recorder"
    bin_dir = tmp_path / "shim-bin"
    bin_dir.mkdir()
    shim = bin_dir / "uv"
    shim.write_text(
        "#!/usr/bin/env bash\n"
        'prev=""\n'
        'for arg in "$@"; do\n'
        f'  if [[ "$prev" == "--start-seed" && "$arg" == "{fail_seed}" ]]; then\n'
        "    echo 'injected tournament failure' >&2\n"
        "    exit 7\n"
        "  fi\n"
        '  prev="$arg"\n'
        "done\n"
        f'exec "{real_uv}" "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    return str(bin_dir)


def test_a_failed_seed_fails_the_run_loud_and_preserves_what_recorded(
    tmp_path: Path,
) -> None:
    # The contract behind every resumable leg: a seed that cannot be recorded
    # stops the set rather than letting it finalize short, says so in the words
    # an operator acts on, and leaves the already-recorded seeds + their MANIFEST
    # rows on disk to resume from.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _fake_env(corpus_root),
        AILIBI_REFRESH_WORKERS="1",
        AILIBI_SEED_MAX_ATTEMPTS="1",
        PATH=_failing_uv_shim(tmp_path, fail_seed=1001)
        + os.pathsep
        + os.environ["PATH"],
    )
    proc = _run("--set", "4p1i", "--seeds", "1000,1001", env=env, timeout=900)
    out = proc.stdout + proc.stderr

    assert proc.returncode == 1
    assert "run_tournament failed after 1 attempts" in out
    assert "INCOMPLETE and must NOT be frozen/committed" in out
    assert "Already-recorded seeds + their MANIFEST rows are preserved" in out

    set_dir = corpus_root / "4p1i"
    assert (set_dir / "replay-seed-1000.jsonl").is_file()
    assert not (set_dir / "replay-seed-1001.jsonl").exists()
    assert [
        int(cells[0]) for cells in _manifest_data_rows(set_dir / "MANIFEST.md")
    ] == [1000]
    assert not list(set_dir.glob(".ailibi-corpus-stage-*"))


# -- the provider seam: `fake` on the sibling's terms, and no looser -----------


def test_the_dry_run_plan_describes_the_provider_the_real_run_would_use(
    tmp_path: Path,
) -> None:
    # --dry-run is documented as "the resolved plan", so under an explicit
    # `fake` it must not print a Featherless plan, claim an API key is needed, or
    # show AILIBI_LLM_PROVIDER=featherless in the invocation it previews — the
    # identical real command runs fake, and a preview that describes a different
    # command is worse than no preview.
    corpus_root = tmp_path / "ml_corpus"
    proc = _run("--set", "4p1i", "--dry-run", env=_fake_env(corpus_root), timeout=180)
    out = proc.stdout

    assert proc.returncode == 0, out + proc.stderr
    assert "[dry-run] provider: fake (hermetic $0" in out
    assert "would require no API key" in out
    assert f"[dry-run] model: {_FAKE_MODEL}" in out
    assert "AILIBI_LLM_PROVIDER=fake AILIBI_PROMPT_SET=qwen3_6_27b" in out
    assert "would require FEATHERLESS_API_KEY" not in out
    assert "AILIBI_LLM_PROVIDER=featherless" not in out
    # A preview writes nothing, including under fake.
    assert not corpus_root.exists()


def test_the_fake_dry_run_previews_the_refusal_it_will_actually_hit(
    tmp_path: Path,
) -> None:
    # A full fake run (no --seeds) records every locked seed and is then refused
    # by check_replay_provenance, because fake rows carry the fake model and the
    # guard demands the locked one. The preview must say so rather than promise
    # a report, a splits.json, a FROZEN line and an acceptance command pinned to
    # a model these bytes will never carry — a plan that advertises exactly what
    # the run is guaranteed to refuse is worse than no plan.
    corpus_root = tmp_path / "ml_corpus"
    proc = _run("--set", "4p1i", "--dry-run", env=_fake_env(corpus_root), timeout=180)
    out = proc.stdout

    assert proc.returncode == 0, out + proc.stderr
    assert "would STOP at check_replay_provenance" in out
    assert f"fake rows are stamped {_FAKE_MODEL}" in out
    assert "eval report / splits / freeze: NONE" in out
    assert "acceptance: N/A" in out
    # None of the featherless finalize promises survive on this path.
    assert "would append a FROZEN line" not in out
    assert "would write $" not in out.replace(str(corpus_root), "$")
    assert "validity_gate.py" not in out


def test_fake_model_bytes_are_refused_by_the_provenance_guard(
    tmp_path: Path,
) -> None:
    # The other half of the pin above: the preview's claim is only honest if the
    # guard really refuses fake-model bytes. Driven over a whole set of them —
    # the committed 4p1i replays copied to scratch and re-stamped with the fake
    # model, which is what a full fake run leaves on disk — so the refusal is
    # reached without recording 50 games. check_replay_provenance is invoked
    # twice per set (pre-spend over what is already present, and again before
    # the freeze); this fixture trips the first, which is the same function and
    # the same verdict: the run stops there and nothing is ever frozen.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = corpus_root / "4p1i"
    shutil.copytree(_REPO_ROOT / "replays" / "ml_corpus" / "4p1i", set_dir)
    rewritten = 0
    for replay in set_dir.glob("replay-seed-*.jsonl"):
        text = replay.read_text(encoding="utf-8")
        if f'"model":"{_BASELINE_MODEL}"' in text:
            rewritten += 1
        replay.write_text(
            text.replace(f'"model":"{_BASELINE_MODEL}"', f'"model":"{_FAKE_MODEL}"'),
            encoding="utf-8",
        )
    assert rewritten, "the fixture must actually carry fake-model rows"

    proc = _run("--set", "4p1i", env=_fake_env(corpus_root), timeout=900)
    out = proc.stdout + proc.stderr

    assert proc.returncode != 0
    assert "check_replay_provenance" in out
    assert _FAKE_MODEL in out
    assert "complete and FROZEN" not in out
    assert "do not commit" in out


def test_the_dry_run_refuses_a_fake_target_inside_the_committed_tree() -> None:
    # A preview that cannot refuse would let an operator confirm a plan the real
    # run rejects — the reason the lever preflight already runs in the dry-run.
    env = dict(
        _clean_env(), AILIBI_LLM_PROVIDER="fake", AILIBI_PROMPT_SET="qwen3_6_27b"
    )
    proc = _run("--dry-run", env=env, timeout=180)

    assert proc.returncode != 0
    assert "may not write into the repository's replays/ tree" in (
        proc.stdout + proc.stderr
    )


def test_the_dry_run_still_describes_featherless_by_default() -> None:
    # The default path is untouched: no provider export still previews the
    # locked hosted plan, key and all.
    proc = _run("--set", "4p1i", "--dry-run")

    assert proc.returncode == 0
    assert "[dry-run] provider: featherless (LOCKED" in proc.stdout
    assert "would require FEATHERLESS_API_KEY" in proc.stdout
    assert f"[dry-run] model: {_BASELINE_MODEL}" in proc.stdout
    assert "AILIBI_LLM_PROVIDER=featherless" in proc.stdout


def test_the_dry_run_refuses_an_unsupported_provider() -> None:
    env = dict(_clean_env(), AILIBI_LLM_PROVIDER="anthropic")
    proc = _run("--dry-run", env=env)

    assert proc.returncode != 0
    assert "records ONLY on featherless" in proc.stdout + proc.stderr


def test_fake_target_guard_resolves_symlinks_and_dot_dot(tmp_path: Path) -> None:
    # Physical paths are compared, so neither a symlink nor a `..` can smuggle
    # the target back under replays/. The decoy lives in the committed tree and
    # must stay empty.
    decoy = _REPO_ROOT / "replays" / "ml_corpus" / ".test-corpus-decoy"
    link = tmp_path / "corpus-link"
    target = f"{tmp_path}/not-there/../corpus-link/scratch"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_PROMPT_SET="qwen3_6_27b",
        AILIBI_ML_CORPUS_ROOT=target,
    )
    decoy.mkdir()
    link.symlink_to(decoy)
    try:
        proc = _run("--set", "4p1i", env=env, timeout=180)
        out = proc.stdout + proc.stderr
        assert proc.returncode != 0
        assert "may not write into the repository's replays/ tree" in out
        assert str(decoy) in out  # resolved all the way through the symlink
        assert list(decoy.iterdir()) == []
        assert not (tmp_path / "not-there").exists()
    finally:
        shutil.rmtree(decoy)


def test_fake_provider_skips_the_api_key_preflight(tmp_path: Path) -> None:
    # There is no key to preflight on a hermetic $0 run, and demanding one would
    # make the seam unusable. The featherless path is untouched (see
    # test_preflight_requires_api_key_before_record).
    corpus_root = tmp_path / "ml_corpus"
    proc = _run(
        "--set", "4p1i", "--seeds", "1000", env=_fake_env(corpus_root), timeout=900
    )
    out = proc.stdout + proc.stderr

    assert "FEATHERLESS_API_KEY must be set" not in out
    assert "Fake-provider target OK" in out
    assert (corpus_root / "4p1i" / "replay-seed-1000.jsonl").is_file()


def test_fake_provider_still_fires_the_substrate_lever_preflight(
    tmp_path: Path,
) -> None:
    # The seam relaxes the KEY, nothing else: a stale lever export is still
    # refused before any seed stages, under fake exactly as under featherless.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(_fake_env(corpus_root), AILIBI_IMPOSTOR_ROLL_CALL="1")
    proc = _run("--set", "4p1i", "--seeds", "1000", env=env, timeout=300)
    out = proc.stdout + proc.stderr

    assert proc.returncode != 0
    assert "does not match --expect-levers" in out
    assert "impostor_roll_call" in out
    assert not (corpus_root / "4p1i" / "replay-seed-1000.jsonl").exists()


def test_fake_provider_still_fires_the_prompt_set_pins(tmp_path: Path) -> None:
    # Both prompt pins survive the seam: the SET the run must be under, and the
    # registry's per-template versions the corpus is frozen at.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(_fake_env(corpus_root), AILIBI_PROMPT_SET="wrong_set")
    proc = _run("--set", "4p1i", "--seeds", "1000", env=env, timeout=300)
    out = proc.stdout + proc.stderr

    assert proc.returncode != 0
    assert "AILIBI_PROMPT_SET must be 'qwen3_6_27b'" in out
    assert not corpus_root.exists()


def test_an_unset_provider_still_resolves_to_featherless(tmp_path: Path) -> None:
    # The silent-fake path stays closed: `fake` is reachable ONLY by naming it.
    corpus_root = tmp_path / "ml_corpus"
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "4p1i", env=env, timeout=180)

    assert proc.returncode != 0
    assert "FEATHERLESS_API_KEY must be set" in proc.stdout + proc.stderr


def test_an_empty_provider_still_resolves_to_featherless(tmp_path: Path) -> None:
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(), AILIBI_LLM_PROVIDER="", AILIBI_ML_CORPUS_ROOT=str(corpus_root)
    )
    proc = _run("--set", "4p1i", env=env, timeout=180)

    assert proc.returncode != 0
    assert "FEATHERLESS_API_KEY must be set" in proc.stdout + proc.stderr


def test_every_other_provider_is_still_refused(tmp_path: Path) -> None:
    corpus_root = tmp_path / "ml_corpus"
    for provider in ("anthropic", "ollama", "openai"):
        env = dict(
            _clean_env(),
            AILIBI_LLM_PROVIDER=provider,
            AILIBI_ML_CORPUS_ROOT=str(corpus_root),
        )
        proc = _run("--set", "4p1i", env=env, timeout=180)
        assert proc.returncode != 0, provider
        assert "records ONLY on featherless" in proc.stdout + proc.stderr
        assert not corpus_root.exists()


# -- the lock's dead-owner verdict --------------------------------------------
#
# acquire_lock's liveness probe (cat owner, then kill -0) inherently races the
# holder's release: a holder that releases the lock and exits between the two
# steps — a worker draining the queue, or the seed-claim command-substitution
# subshell whose pid dies with the claim — probes as dead though it finished
# cleanly. The lock therefore requires the SAME dead pid to stay the recorded
# owner across consecutive polls before declaring death. Driven off the committed
# implementation, extracted verbatim, so these bite on the real script.

_LOCK_DRIVER = """\
set -euo pipefail
stage_dir="$1"
lockdir="$stage_dir/.lock"
{functions}
if acquire_lock; then
  echo ACQUIRED
  release_lock
else
  echo REFUSED
  exit 1
fi
"""


def _dedent_two(block: str) -> str:
    """Strip the two-space nesting the pool functions carry inside record_set."""

    return "\n".join(
        line[2:] if line.startswith("  ") else line for line in block.splitlines()
    )


def _lock_driver(tmp_path: Path) -> Path:
    """A driver script around the committed acquire_lock/release_lock."""

    script = _RECORD_SH.read_text(encoding="utf-8")
    functions = []
    for pattern in (
        r"(?ms)^  acquire_lock\(\) \{\n.*?\n  \}$",
        r"(?m)^  release_lock\(\) \{ .*\}$",
    ):
        match = re.search(pattern, script)
        assert match is not None, f"lock function not found: {pattern}"
        functions.append(_dedent_two(match.group(0)))
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
    # dead and never released must be refused, flagged in .failed, and named —
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
    # A dead owner pid may belong to a holder that RELEASED the lock and finished
    # between the waiter's cat and its kill -0 — a clean handoff, not a corpse,
    # and it must not fail the set. This is the corpus recorder's own version of
    # the race that fired three times in CI on the sibling (PRs #369/#372/#378),
    # and it is structural here: claim_next_seed's only call site is a command
    # substitution, so ${BASHPID:-$$} records a pid that dies with the claim.
    # The waiter provably probes the dead owner first (gated on the xtrace showing
    # kill -0), then the lock is released out from under it; it must acquire and
    # flag nothing.
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
        # On any failure below the waiter may still be spinning on the held lock,
        # and Popen.__exit__ waits for it unboundedly — kill it so the gate
        # reports the failure instead of hanging.
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


# -- the freeze, driven verbatim ----------------------------------------------
#
# freeze_manifest is unreachable from a hermetic recording by design (the
# provenance guards above it correctly refuse fake bytes), so it is driven
# directly out of the committed script rather than left uncovered.

_FREEZE_DRIVER = """\
set -euo pipefail
REQUIRED_PROMPT_SET="qwen3_6_27b"
expect_levers_desc="(none — the bare slate: every live toggle OFF)"
POLICY_STAMP="fsm-default"
SPLIT_RULE_DESC="seed mod 5: {{0,1,2}}=train, {{3}}=val, {{4}}=test"
{functions}
freeze_manifest "$1" "$2" "$3" "$4"
"""


def _freeze_driver(tmp_path: Path) -> Path:
    """A driver script around the committed freeze_manifest."""

    script = _RECORD_SH.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^freeze_manifest\(\) \{\n.*?\n\}$", script)
    assert match is not None, "freeze_manifest not found in the script"
    driver = tmp_path / "freeze_driver.sh"
    driver.write_text(_FREEZE_DRIVER.format(functions=match.group(0)), encoding="utf-8")
    return driver


def _run_freeze(
    tmp_path: Path, manifest: Path, sha: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "bash",
            str(_freeze_driver(tmp_path)),
            str(manifest),
            "4p1i",
            sha,
            "2026-08-27",
        ],
        cwd=_REPO_ROOT,
        capture_output=True,
        text=True,
        env=_clean_env(),
        timeout=300,
    )


def test_freeze_appends_one_frozen_line_naming_the_code_state_sha(
    tmp_path: Path,
) -> None:
    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text("# Sample Replay Manifest\n\n| seed |\n|---|\n| 1000 |\n")

    proc = _run_freeze(tmp_path, manifest, "abc1234")

    assert proc.returncode == 0, proc.stdout + proc.stderr
    text = manifest.read_text(encoding="utf-8")
    assert text.count("**FROZEN**") == 1
    assert "abc1234" in text
    assert "4p1i" in text
    assert "qwen3_6_27b" in text
    assert "fsm-default" in text
    # The line says what the sha IS, because reading it as a pointer to the bytes
    # sends an auditor to the wrong tree.
    assert "NOT the commit containing these bytes" in text
    # The table it was appended to is untouched.
    assert "| 1000 |" in text


def test_re_freezing_replaces_rather_than_stacks_the_frozen_line(
    tmp_path: Path,
) -> None:
    # A no-op re-finalize skips the per-seed table rewrite, so without the strip
    # each re-run would append another FROZEN line and the set would carry two
    # contradicting freeze shas.
    manifest = tmp_path / "MANIFEST.md"
    manifest.write_text("# Sample Replay Manifest\n\n| seed |\n|---|\n| 1000 |\n")

    assert _run_freeze(tmp_path, manifest, "abc1234").returncode == 0
    assert _run_freeze(tmp_path, manifest, "def5678").returncode == 0

    text = manifest.read_text(encoding="utf-8")
    assert text.count("**FROZEN**") == 1
    assert "def5678" in text
    assert "abc1234" not in text
