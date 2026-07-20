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
        "prompt versions: locked to [accusation_round.qwen3_6_27b.v3, "
        "crewmate_report.qwen3_6_27b.v3, impostor_report.qwen3_6_27b.v3, "
        "vote_ballot.qwen3_6_27b.v3]" in proc.stdout
    )


def test_dry_run_announces_baseline6_substrate_and_lever_preflight() -> None:
    # Task 18.13: the plan names the ruled baseline-6 lever slate AND the
    # substrate-lever preflight that enforces it, so an operator previewing a
    # ~18–20h run can confirm the substrate before spending. Mirrors the Task-18.12
    # echo in scripts/refresh_samples.sh (tests/scripts/test_refresh_samples.py).
    proc = _run("--dry-run")
    assert proc.returncode == 0
    assert (
        "[dry-run] substrate flags: baseline-6 slate — the meeting-layer levers "
        "unconditional ON (roll_call_round, whereabouts_interior_flags, "
        "vent_placement_contradictions, absence_prior graduated at Task 18.12, "
        "beside the earlier graduations), impostor_roll_call default-OFF "
        "(CREW-ONLY ruling)" in proc.stdout
    )
    assert (
        "[dry-run] substrate-lever preflight: would require the live lever slate "
        "to equal the ruled baseline-6 state (thirteen retired levers ON, "
        "impostor_roll_call OFF) and refuse a stale AILIBI_* export before any "
        "seed stages" in proc.stdout
    )


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


def test_preflight_refuses_fake_provider(tmp_path: Path) -> None:
    corpus_root = tmp_path / "ml_corpus"
    env = dict(
        _clean_env(),
        AILIBI_LLM_PROVIDER="fake",
        AILIBI_ML_CORPUS_ROOT=str(corpus_root),
    )
    proc = _run("--set", "4p1i", env=env)
    assert proc.returncode != 0
    assert "records ONLY on featherless" in proc.stdout + proc.stderr
    assert not corpus_root.exists()


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
    assert "locked baseline-6 substrate" in out
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
    assert "locked baseline-6 model" in out
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
    assert "does not equal the ruled baseline-6 state" in out
    assert "impostor_roll_call must be OFF" in out
    assert "Unset any stale AILIBI_* lever export" in out
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
    assert "does not equal the ruled baseline-6 state" not in out
    assert proc.returncode != 0  # stopped at the MODEL guard, not the lever guard
    assert "locked baseline-6 model" in out


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
    # The corpus contract freezes the baseline-6 prompt VERSIONS (all four
    # templates at v3), not just the set name — the recorder's preflight asserts
    # the live registry still resolves qwen3_6_27b to its locked constant. Pin the
    # two together here: if a later task bumps the registry entry, this test
    # fails and forces the corpus re-lock conversation instead of letting the
    # recorder's guard and the registry drift apart silently.
    from orchestrator.game import PROMPT_VERSION_SETS

    script = _RECORD_SH.read_text(encoding="utf-8")
    match = re.search(r'^REQUIRED_PROMPT_VERSIONS="([^"]+)"$', script, re.MULTILINE)
    assert match is not None, "REQUIRED_PROMPT_VERSIONS constant missing from script"
    locked = match.group(1)
    resolved = ", ".join(sorted(PROMPT_VERSION_SETS["qwen3_6_27b"].values()))
    assert resolved == locked, (
        "PROMPT_VERSION_SETS['qwen3_6_27b'] has moved off the locked baseline-6 "
        "corpus versions; recording/resuming the 15.12 corpus would now drift. "
        "Re-locking is an owner decision (re-record + re-freeze)."
    )


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
    assert "disagrees with the baseline-6 lever slate" in out
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
    assert "disagrees with the baseline-6 lever slate" in out
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
    corpus_root = tmp_path / "ml_corpus"
    seeds = list(range(1000, 1010))
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
    assert doc["counts"] == {"train": 6, "val": 2, "test": 2}


def test_splits_only_writes_no_replays_and_makes_no_network_call(
    tmp_path: Path,
) -> None:
    # splits-only is pure: it reads the on-disk replay filenames and writes
    # splits.json, never invoking a provider. Prove it never records by stripping
    # every provider key AND leaving the set with only stub replays.
    corpus_root = tmp_path / "ml_corpus"
    set_dir = _stub_set(corpus_root, "4p1i", list(range(1000, 1005)))
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
    corpus_root = tmp_path / "ml_corpus"
    (corpus_root / "9p2i").mkdir(parents=True)  # exists but holds no replays
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--set", "9p2i", "--splits-only", env=env)
    assert proc.returncode != 0
    assert "no replay-seed-*.jsonl" in proc.stdout + proc.stderr


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
    _stub_set(corpus_root, "9p2i", list(range(1000, 1006)))
    _stub_set(corpus_root, "4p1i", list(range(1000, 1006)))
    env = dict(_clean_env(), AILIBI_ML_CORPUS_ROOT=str(corpus_root))
    proc = _run("--splits-only", env=env)
    assert proc.returncode == 0
    for set_name in ("9p2i", "4p1i"):
        doc = json.loads((corpus_root / set_name / "splits.json").read_text())
        assert doc["set"] == set_name
        assert doc["total_games"] == 6
