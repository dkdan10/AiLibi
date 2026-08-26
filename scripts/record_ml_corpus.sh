#!/usr/bin/env bash
#
# FROZEN (Phase 19 tier map, training/README.md): recorder of the frozen corpus
# bytes; the Bash-recorder port is explicitly out of scope. Bug fixes and
# evidence readers only; no new search.
#
# record_ml_corpus.sh — record the frozen ML-calibration corpus at baseline-6
# config (Task 15.12 corpus, re-grounded onto baseline 6 by Task 18.13;
# audits/audit-phase-18-baseline-6.md; audits/audit-phase-16-model-lock.md;
# audits/post-phase-14-ML-training-signal.md §5.6, §7.2; tasks/post-phase-14-plan.md §4).
#
# The surrogate (15.13) and the impostor bake-off (15.15+) consume a FROZEN
# training/calibration corpus recorded at EXACT baseline-6 config — the locked
# substrate: Qwen/Qwen3.6-27B on Featherless, the qwen3_6_27b prompt set (all four
# templates at v3), the baseline-6 lever slate (the thirteen retired always-on
# levers — including the four meeting-layer graduations of Task 18.12:
# roll_call_round / whereabouts_interior_flags / vent_placement_contradictions /
# absence_prior — with every live toggle default-OFF unless --expect-levers
# declares otherwise), $0 flat-rate.
# Nothing trains against a meeting layer scheduled to change, so this corpus is a
# SEPARATE release artifact from the canonical samples: it lands under
# replays/ml_corpus/ (NOT replays/samples/), at fresh seed ranges so a corpus game
# can never be confused with a canonical 0–49 game.
#
# Two sets, ~3x the canonical 9p2i meeting/ejection volume (~22-23h wall with 2
# Featherless seed workers — the Task-18.13 MEASURED figure: 4p1i 0h45m + 9p2i
# 19h26m + a 2h43m phantom-repair pass. Baseline-5 ran ~14-15h; the baseline-6
# roll-call round adds ~36% meeting LLM calls and drives the 9p2i meeting rate to
# 1.00, so treat the ~14-15h figure as stale; the 16.14/17.9/18.12 operator notes apply:
# staggered worker starts, jittered backoff, per-seed atomic staging,
# AILIBI_SEED_MAX_ATTEMPTS=8, and checkpoint-push of each completed seed range so
# an interruption never loses a leg):
#   9p2i  — 150 seeds (1000..1149), roster 9p/2i, 2 tasks/crewmate   [primary]
#   4p1i  —  50 seeds (1000..1049), roster 4p/1i, 1 task/crewmate    [secondary]
#
# This is a THIN wrapper that COMPOSES the same underlying tooling
# scripts/refresh_samples.sh drives — it never edits it, and never edits
# scripts/run_tournament.py. Per set it: stamps the 15.9 FSM-default tactical
# policy onto every game (--tactical-policy-stamp fsm-default), records each seed
# through scripts/run_tournament.py (2 parallel workers pulling from a shared
# queue, per-seed transport crash-retry), maintains MANIFEST.md via
# scripts/_manifest_writer.py, rebuilds tournament-eval-report.json via
# scripts/build_sample_report.py, writes a committed by-game splits.json
# (train/val/test — DATA ONLY; the loader is 15.11's), and FREEZES the set by
# appending an explicit FROZEN line naming the git SHA.
#
# Acceptance (run per set, by the operator, before the PR merges — NOT here):
#   uv run python scripts/validity_gate.py replays/ml_corpus/<set> \
#       --expected-model Qwen/Qwen3.6-27B --require-zero-cost
#   scripts/verify_samples.sh replays/ml_corpus/<set>        # byte-verify
#
# Hosted models do NOT byte-reproduce FRESH generation; RECORDINGS replay
# byte-identically (the loosened contract the canonical baselines already carry),
# so the validity gate + byte-verify — not generation-replay equality — is the
# acceptance.
#
# Usage:
#   scripts/record_ml_corpus.sh [--set 9p2i|4p1i|both] [--dry-run | --splits-only]
#                               [--expect-levers KEY,KEY]
#
#   --set 9p2i|4p1i|both  which set(s) to record (default: both)
#   --dry-run             print the resolved plan; touch nothing, no network
#   --splits-only         (re)write splits.json for the selected set(s) from the
#                         replays already on disk, then exit — no network, no record
#   --expect-levers       the toggleable substrate levers this record expects ON
#                         (comma-separated registry keys; default: none). The live
#                         slate must match it exactly, and every recorded game_over
#                         stamp is judged against the same slate.
#   -h, --help            show this help
#
# Operator gate: requires FEATHERLESS_API_KEY and AILIBI_PROMPT_SET=qwen3_6_27b; the
# corpus is baseline-6, so the FULL substrate is LOCKED: the provider (a run under
# any other provider — including the fake CI provider — is refused, so a corpus
# game can never be silently recorded off-substrate, AGENTS.md "no silent
# fallbacks"), the meeting/trigger models (a non-baseline AILIBI_LLM_MEETING_MODEL
# / AILIBI_LLM_TRIGGER_MODEL override is refused), the endpoint (a non-default
# AILIBI_FEATHERLESS_BASE_URL override is refused), the LEVER SLATE (the live
# substrate snapshot must equal the ruled baseline-6 state — a stale AILIBI_*
# lever export, most dangerously AILIBI_IMPOSTOR_ROLL_CALL, is refused before any
# seed stages), and the per-template prompt versions (the registry must still
# resolve qwen3_6_27b to the locked v3 map, and rows recorded off that map are
# refused at freeze).
# ~22-23h wall MEASURED at Task 18.13 (the baseline-6 roll-call round adds ~36%
# meeting calls over the ~14-15h baseline-5 record, and a phantom-repair pass
# re-records any seed carrying a (deadline_default) wall-clock-miss row — 10/150
# on the 18.13 9p2i leg. Dropping those and resuming is safe at any time: the
# finalize's check_seed_count asserts the exact locked set is present before it
# freezes, so a mistimed drop fails loud with the missing seeds named rather than
# freezing a short set). Commit is one atomic PR after the gate + byte-verify pass
# per set, with checkpoint commits of completed seed ranges along the way. May
# share the baseline-6 operator session.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Corpus root — a PARENT of the per-set subdirs. The two-level nesting
# (replays/ml_corpus/<set>/, NOT replays/<set>/) is LOAD-BEARING: a set placed
# directly under replays/ would make the API's directory resolution treat
# ./replays as the active parent and SHADOW the canonical samples (Task 12.12
# discovery; pinned by tests/api/test_set_discovery_ml_corpus.py). Overridable for
# tests via AILIBI_ML_CORPUS_ROOT; the default is the committed layout.
CORPUS_ROOT="${AILIBI_ML_CORPUS_ROOT:-$REPO_ROOT/replays/ml_corpus}"

# =============================================================================
# PIN BLOCK — the baseline-7 substrate; the committed corpus IS current.
# =============================================================================
# The pins below name the BASELINE-7 substrate — the substrate this recorder
# records (and freezes) at, and the substrate the COMMITTED corpus under
# replays/ml_corpus/ now carries: Qwen/Qwen3.6-27B (the Task 16.2 locked model,
# audits/audit-phase-16-model-lock.md, locked 2026-07-12) + the qwen3_6_27b
# prompt set at v4 (the Task-20.31 evidence-honesty bump; lineage v1 bespoke port
# -> v2 elicitation batch -> v3 persona voice -> v4) + the baseline-7 lever slate:
# the twenty-one retired always-on levers, which since the baseline-7 record
# include the eight Phase-20 evidence-honesty levers
# (audits/audit-phase-20-baseline-7.md §6.1), with the one surviving live toggle
# (impostor_roll_call) recorded OFF unless --expect-levers declares it ON.
# The preflight COUPLES model + prompt set + prompt versions + lever slate
# as ONE substrate, so they re-pin together.
#
# Both canonical artifacts sit at baseline 7 — the samples and this corpus were
# re-recorded together at the baseline-7 record — so the freeze-path provenance
# guards (check_replay_provenance — the model, the $0 cost, and the lever slate on
# every recorded stamp — and check_recorded_prompt_versions — the MANIFEST version
# cells) PASS over the committed bytes by construction. They still REFUSE anything
# off-substrate (a prior baseline-6 recording, whose stamp carries the eight
# Phase-20 levers OFF; a phantom seed) from being resumed-over and frozen: that
# refusal is correct and expected. Nothing here weakens to accommodate
# off-substrate bytes.
# =============================================================================

# The locked Featherless baseline model (Task 16.2 model lock); mirrors
# llm.featherless_client.DEFAULT_FEATHERLESS_MODEL and refresh_samples.sh. Stamped
# onto no-meeting rows and asserted by the operator's --expected-model gate.
DEFAULT_FEATHERLESS_MODEL="Qwen/Qwen3.6-27B"
# The hosted Featherless endpoint; mirrors
# llm.featherless_client.DEFAULT_FEATHERLESS_BASE_URL. build_default_client honors
# AILIBI_FEATHERLESS_BASE_URL, so the preflight pins it — a leftover mock/staging
# export must never record the "hosted-$0" corpus against an alternate endpoint.
DEFAULT_FEATHERLESS_BASE_URL="https://api.featherless.ai/v1"
# The locked prompt set the corpus records under (baseline 7; Task 16.13/16.17,
# bumped to v4 at Task 20.31). A featherless run with any other set would
# SILENTLY record the wrong substrate.
REQUIRED_PROMPT_SET="qwen3_6_27b"
# The per-template prompt versions the set must resolve to (all four at v4 since
# Task 20.31's evidence-honesty bump; the lineage is v1 bespoke port -> v2
# elicitation batch -> v3 persona voice -> v4). The set NAME alone is not a
# version pin — the registry entry can be bumped by a later task — so the
# preflight asserts orchestrator.game.PROMPT_VERSION_SETS still resolves
# $REQUIRED_PROMPT_SET to exactly this map, and the finalize refuses to freeze a
# set whose MANIFEST rows carry any other version string. Sorted, comma+space-
# joined (the MANIFEST cell rendering). A corpus recorded before this constant
# moved carries the older stamps in its own MANIFEST; re-locking it is an owner
# decision (re-record + re-freeze), which is what a stamp mismatch here forces.
REQUIRED_PROMPT_VERSIONS="accusation_round.qwen3_6_27b.v4, crewmate_report.qwen3_6_27b.v4, impostor_report.qwen3_6_27b.v4, vote_ballot.qwen3_6_27b.v4"
# The 15.9 tactical-policy stamp for the canonical scripted FSMs. Every corpus
# game is FSM-default (no learned mover exists yet); the stamp makes that explicit
# provenance rather than the absent = FSM-default default, so the MANIFEST policy
# column reads fsm-default and the bake-off can attribute every game.
POLICY_STAMP="fsm-default"

# Deterministic, auditable by-game split rule (documented in every splits.json and
# in the FROZEN MANIFEST line): a game's seed mod 5 buckets it —
#   {0,1,2} -> train, {3} -> val, {4} -> test   (60/20/20 by construction).
# Split is by GAME (one game per seed), so no game can appear in two splits — the
# rule is a total function of the seed, auditable from the file alone.
SPLIT_RULE_DESC="seed mod 5: {0,1,2}=train, {3}=val, {4}=test"

usage() {
  cat <<EOF
Usage: $(basename "$0") [--set 9p2i|4p1i|both] [--dry-run | --splits-only]
                        [--expect-levers KEY,KEY]

  --set 9p2i|4p1i|both  which corpus set(s) to record (default: both)
  --dry-run             print the resolved plan; touch nothing, make no API call
  --splits-only         (re)write splits.json for the selected set(s) from the
                        replays already on disk, then exit (no network, no record)
  --expect-levers       the toggleable substrate levers this record expects ON,
                        comma-separated (default: none — the bare slate). The
                        live slate must match it EXACTLY before any seed stages,
                        and every recorded game_over stamp is judged against it.
  -h, --help            show this help

Records the frozen ML-calibration corpus at baseline-6 config into
$CORPUS_ROOT/<set>/. Requires FEATHERLESS_API_KEY and
AILIBI_PROMPT_SET=$REQUIRED_PROMPT_SET (the provider is LOCKED to featherless).
EOF
}

# Per-set config (Task 15.12). Fresh seed ranges, disjoint from the canonical
# 0–49 sets, so a corpus game is never confused with a canonical one.
set_config() {
  # Echoes: start_seed count num_players num_impostors tasks_per_crewmate
  case "$1" in
    9p2i) echo "1000 150 9 2 2" ;;
    4p1i) echo "1000 50 4 1 1" ;;
    *)
      echo "Error: unknown set '$1' (want 9p2i or 4p1i)." >&2
      return 1
      ;;
  esac
}

# --- argument parsing --------------------------------------------------------

set_arg="both"
dry_run=0
splits_only=0
# The toggleable levers this record expects ON (comma-separated registry keys).
# Empty is the bare slate: every live toggle OFF.
expect_levers=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --set)
      shift
      set_arg="${1:-}"
      if [[ -z "$set_arg" ]]; then
        echo "Error: --set requires a value (9p2i|4p1i|both)." >&2
        usage
        exit 1
      fi
      ;;
    --dry-run) dry_run=1 ;;
    --splits-only) splits_only=1 ;;
    --expect-levers)
      # An explicitly EMPTY value is the bare slate (every live toggle OFF), so
      # automation can pass "$LEVERS" unconditionally; only a MISSING argument is
      # an error, which is why this counts what is left rather than testing the
      # string.
      shift
      if [[ $# -eq 0 ]]; then
        echo "Error: --expect-levers requires a comma-separated lever list (pass an empty string for the bare slate)." >&2
        usage
        exit 1
      fi
      expect_levers="$1"
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ "$dry_run" -eq 1 && "$splits_only" -eq 1 ]]; then
  echo "Error: --dry-run and --splits-only are mutually exclusive." >&2
  usage
  exit 1
fi

# One human-readable rendering of the expected slate, so the preview echo, the
# refusal and the freeze guard all name the SAME slate.
if [[ -n "$expect_levers" ]]; then
  expect_levers_desc="$expect_levers"
else
  expect_levers_desc="(none — the bare slate: every live toggle OFF)"
fi

# Substrate-lever preflight: the slate is checked POSITIVELY against the slate the
# operator declared (--expect-levers) before any seed stages. A half-set export
# would otherwise record the whole ~22-23h corpus off-substrate while the echo
# claims the ruled slate — and an acceptance gate run in the SAME polluted shell
# would pass coherently, because it reads the same environment. A blacklist of
# variable names cannot catch a lever MISSING from the export, which is why this
# is a whole-slate equality. The DRY RUN runs it too: reading the environment
# writes nothing, and a preview that cannot refuse would let an operator confirm a
# plan the real run rejects. The comparison lives in
# orchestrator.replay.substrate_slate_mismatches, shared with
# scripts/refresh_samples.sh so both recorders judge a slate the same way.
substrate_lever_preflight() {
  local diag
  if diag="$(uv run python -c '
import sys

from orchestrator.replay import substrate_slate_mismatches

problems = substrate_slate_mismatches(
    [key for key in sys.argv[1].split(",") if key]
)
if problems:
    sys.stderr.write("; ".join(problems))
    sys.exit(1)
' "$expect_levers" 2>&1)"; then
    echo "Substrate slate OK: expected levers ON = $expect_levers_desc; every other live toggle OFF; the graduated levers unconditional ON."
    return 0
  fi
  echo "Error: the live substrate-lever slate does not match --expect-levers." >&2
  echo "       Expected ON: $expect_levers_desc" >&2
  echo "       Mismatch: ${diag}" >&2
  echo "       Export exactly the levers you named and unset every other AILIBI_*" >&2
  echo "       lever export, then re-run. Nothing was recorded." >&2
  return 1
}

case "$set_arg" in
  9p2i) sets=("9p2i") ;;
  4p1i) sets=("4p1i") ;;
  both) sets=("9p2i" "4p1i") ;;
  *)
    echo "Error: --set must be one of 9p2i, 4p1i, both (got '$set_arg')." >&2
    usage
    exit 1
    ;;
esac

# --- worker/queue/crash-retry knobs (mirrors refresh_samples.sh, Task 14.12) --

# TWO seed workers saturate the hosted Featherless plan (4 concurrent units; a 27B
# request uses 2) without exceeding it. Overridable via AILIBI_REFRESH_WORKERS —
# the same env refresh_samples.sh reads, so a shared operator session tunes both
# alike. Never silently derived (AGENTS.md "no silent fallbacks").
REFRESH_WORKERS="${AILIBI_REFRESH_WORKERS:-2}"
if [[ ! "$REFRESH_WORKERS" =~ ^[0-9]+$ ]] || [[ "$((10#$REFRESH_WORKERS))" -lt 1 ]]; then
  echo "Error: AILIBI_REFRESH_WORKERS must be a positive integer, got '$REFRESH_WORKERS'." >&2
  exit 1
fi
REFRESH_WORKERS="$((10#$REFRESH_WORKERS))"

# Per-seed crash-retry budget: over a multi-hour HOSTED run a game aborts on a
# TRANSPORT-level error (httpx.ConnectError / read timeout) the client's HTTP
# 429/5xx retry does not cover — a transient blip a re-run clears. A recorded
# parse/schema failure is NOT a crash (it lands as a FailedCallReplayEntry and the
# game continues), so this budget only spends on genuine transport errors.
SEED_MAX_ATTEMPTS="${AILIBI_SEED_MAX_ATTEMPTS:-4}"
if [[ ! "$SEED_MAX_ATTEMPTS" =~ ^[0-9]+$ ]] || [[ "$((10#$SEED_MAX_ATTEMPTS))" -lt 1 ]]; then
  echo "Error: AILIBI_SEED_MAX_ATTEMPTS must be a positive integer, got '$SEED_MAX_ATTEMPTS'." >&2
  exit 1
fi
SEED_MAX_ATTEMPTS="$((10#$SEED_MAX_ATTEMPTS))"

# --- splits.json (by-game train/val/test; data only — the loader is 15.11's) --

# Write <set_dir>/splits.json from the replay-seed-*.jsonl present in <set_dir>,
# applying the deterministic SPLIT_RULE_DESC. By GAME (one game per seed), so the
# three buckets are disjoint by construction. Fails loud on an empty set dir.
# Pure Python (no network), so --splits-only is hermetic and unit-testable.
write_splits() {
  local set_name="$1" set_dir="$2"
  uv run python - "$set_name" "$set_dir" "$SPLIT_RULE_DESC" <<'PY'
import json
import sys
from pathlib import Path

set_name, set_dir, rule = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
seeds: list[int] = []
for path in set_dir.glob("replay-seed-*.jsonl"):
    core = path.stem[len("replay-seed-") :]
    if core.isdigit():
        seeds.append(int(core))
seeds = sorted(set(seeds))
if not seeds:
    sys.stderr.write(f"write_splits: no replay-seed-*.jsonl under {set_dir}\n")
    raise SystemExit(1)

buckets: dict[str, list[int]] = {"train": [], "val": [], "test": []}
name_by_mod = {0: "train", 1: "train", 2: "train", 3: "val", 4: "test"}
for seed in seeds:
    buckets[name_by_mod[seed % 5]].append(seed)

# Belt-and-suspenders: a game must never appear in two splits (the DoD invariant a
# test also asserts by reading the file). The rule is a total function of the
# seed, so this can only trip on a logic bug — fail loud if it ever does.
seen: set[int] = set()
for split_seeds in buckets.values():
    for seed in split_seeds:
        if seed in seen:
            raise SystemExit(f"write_splits: seed {seed} landed in two splits")
        seen.add(seed)

doc = {
    "set": set_name,
    "split_rule": rule,
    "counts": {name: len(vals) for name, vals in buckets.items()},
    "total_games": len(seeds),
    "train": buckets["train"],
    "val": buckets["val"],
    "test": buckets["test"],
}
(set_dir / "splits.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
print(
    f"  splits.json: {len(buckets['train'])} train / {len(buckets['val'])} val / "
    f"{len(buckets['test'])} test ({len(seeds)} games)"
)
PY
}

# List every seed whose replay is present on disk but has NO row in the MANIFEST,
# ascending, comma-separated (empty output = none missing). Used by the finalize
# to close the crash window where a seed's replay was moved into place but its
# per-seed MANIFEST update never ran. Deliberately NOT "all present seeds": a
# resumed run must not restamp previously recorded seeds with the resume run's
# git_sha — existing rows keep the provenance of the session that recorded their
# bytes (per-seed history is exactly what a later audit reads). Reuses
# _manifest_writer's own discovery + parser so the definition of "a seed" and
# "a row" can never drift from the writer's.
_seeds_missing_rows_csv() {
  local set_dir="$1" manifest="$2"
  uv run python - "$REPO_ROOT" "$set_dir" "$manifest" <<'PYINNER'
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
from _manifest_writer import discover_seeds, parse_manifest  # noqa: E402

set_dir, manifest = Path(sys.argv[2]), Path(sys.argv[3])
stamped = (
    set(parse_manifest(manifest.read_text(encoding="utf-8"))) if manifest.exists() else set()
)
missing = sorted(seed for seed in discover_seeds(set_dir) if seed not in stamped)
print(",".join(str(seed) for seed in missing))
PYINNER
}

# Fail loud when a set dir holds any replay-seed-*.jsonl OUTSIDE the set's locked
# contiguous seed range — or a non-canonical alias (leading zeros, a non-integer
# stem) that would shadow/duplicate an in-range seed. The finalize discovers
# replays by filename, so without this check a stray file dropped into a resumed
# set dir would be swept into the MANIFEST/report/splits and silently FROZEN into
# the corpus (growing it past the required game count and contaminating
# train/val/test). Checked BEFORE recording (fail before spend) and again before
# the finalize/freeze. Pure Python, no network.
check_seed_range() {
  local set_dir="$1" start="$2" last="$3"
  uv run python - "$set_dir" "$start" "$last" <<'PYINNER'
import sys
from pathlib import Path

set_dir, start, last = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
bad: list[str] = []
for path in sorted(set_dir.glob("replay-seed-*.jsonl")):
    core = path.stem[len("replay-seed-") :]
    if not core.isdigit() or str(int(core)) != core or not (start <= int(core) <= last):
        bad.append(path.name)
if bad:
    sys.stderr.write(
        f"check_seed_range: {len(bad)} replay file(s) in {set_dir} fall outside the "
        f"locked seed range {start}..{last}: {', '.join(bad)}\n"
        "Remove the stray file(s); refusing to record into / freeze a dirty set.\n"
    )
    raise SystemExit(1)
PYINNER
}

# Refuse to FREEZE unless EXACTLY the locked seed set is present — every seed in
# [start, last], no gap, no duplicate alias. check_seed_range above only bounds the
# UPPER edge (no stray out-of-range file); it says nothing about a MISSING in-range
# seed, so a set that lost a seed after seed_list was built (a defaulted replay
# dropped from a still-running or resumed leg, a file deleted mid-run, an
# interruption between the drop and the re-record) would still glob into the
# finalize and freeze SHORT — build_sample_report / write_splits / freeze_manifest
# all derive from "whatever replay-seed-*.jsonl are present" and none counts them
# against the contract (PR #301 review). This closes that path: the finalize
# asserts the full contiguous count is on disk before it publishes anything. Pure
# Python, no network.
check_seed_count() {
  local set_dir="$1" start="$2" last="$3"
  uv run python - "$set_dir" "$start" "$last" <<'PYINNER'
import sys
from pathlib import Path

set_dir, start, last = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
present: set[int] = set()
for path in sorted(set_dir.glob("replay-seed-*.jsonl")):
    core = path.stem[len("replay-seed-") :]
    if core.isdigit() and str(int(core)) == core:
        present.add(int(core))
required = set(range(start, last + 1))
missing = sorted(required - present)
extra = sorted(present - required)  # check_seed_range should have caught these
if missing or extra:
    parts = []
    if missing:
        parts.append(f"{len(missing)} MISSING seed(s): {missing}")
    if extra:
        parts.append(f"{len(extra)} out-of-range seed(s): {extra}")
    sys.stderr.write(
        f"check_seed_count: {set_dir} is not the exact locked set "
        f"{start}..{last} ({len(required)} games) — {'; '.join(parts)}. "
        "Refusing to freeze a short/dirty corpus; record the missing seed(s) "
        "and re-run.\n"
    )
    raise SystemExit(1)
PYINNER
}

# Assert the live registry still resolves $REQUIRED_PROMPT_SET to EXACTLY the
# locked baseline-6 per-template versions. Run at preflight (fail before spend):
# a later task bumping the set's registry entry must stop this recorder cold —
# re-locking the corpus to a new prompt baseline is an owner decision, never a
# silent drift. Pure Python, no network.
check_prompt_version_registry() {
  uv run python - "$REPO_ROOT" "$REQUIRED_PROMPT_SET" "$REQUIRED_PROMPT_VERSIONS" <<'PYINNER'
import sys

sys.path.insert(0, sys.argv[1])
from orchestrator.game import PROMPT_VERSION_SETS  # noqa: E402

set_name, locked = sys.argv[2], sys.argv[3]
resolved = ", ".join(sorted(PROMPT_VERSION_SETS[set_name].values()))
if resolved != locked:
    sys.stderr.write(
        f"Error: the prompt-set registry has moved off the locked baseline-6 versions.\n"
        f"  PROMPT_VERSION_SETS[{set_name!r}] resolves to: {resolved}\n"
        f"  the Task-15.12 corpus is frozen at:            {locked}\n"
        "Recording the baseline-6 corpus against a bumped prompt set would freeze a\n"
        "non-baseline corpus as Task 15.12. Re-locking to a new prompt baseline is an\n"
        "owner decision (re-record + re-freeze); nothing was recorded.\n"
    )
    raise SystemExit(1)
PYINNER
}

# Refuse to freeze a set whose meeting-bearing MANIFEST rows are not EXACTLY the
# locked baseline-6 prompt-version map. The preflight pins the registry FORWARD
# from this run; this catches the RESUME case looking BACKWARD — seeds recorded
# by an earlier session under a different (older/newer) prompt baseline, OR rows
# with stripped/partial provenance (a row carrying only allowed tokens is still a
# violation: the manager stamps the FULL set map on every meeting, so anything
# short of the exact four is missing provenance, not a lighter meeting — every
# meeting-bearing row empirically carries all four). No-meeting rows carry
# the "(none — no meetings)" sentinel and are exempt (they invoked no template).
check_recorded_prompt_versions() {
  local set_dir="$1" manifest="$2"
  uv run python - "$REPO_ROOT" "$set_dir" "$manifest" "$REQUIRED_PROMPT_VERSIONS" <<'PYINNER'
import sys
from pathlib import Path

sys.path.insert(0, str(Path(sys.argv[1]) / "scripts"))
from _manifest_writer import parse_manifest  # noqa: E402

set_dir, manifest, locked_csv = sys.argv[2], Path(sys.argv[3]), sys.argv[4]
locked = ", ".join(sorted(token.strip() for token in locked_csv.split(",")))
if not manifest.exists():
    sys.stderr.write(f"check_recorded_prompt_versions: no MANIFEST at {manifest}\n")
    raise SystemExit(1)
bad: dict[int, str] = {}
for seed, row in sorted(parse_manifest(manifest.read_text(encoding="utf-8")).items()):
    cell = row.prompt_versions
    if cell.startswith("(none"):  # the no-meetings sentinel: no template invoked
        continue
    normalized = ", ".join(sorted(token.strip() for token in cell.split(",")))
    if normalized != locked:
        bad[seed] = cell
if bad:
    listing = "; ".join(f"seed {seed}: {cell!r}" for seed, cell in bad.items())
    sys.stderr.write(
        f"check_recorded_prompt_versions: {len(bad)} meeting-bearing MANIFEST row(s) "
        f"in {set_dir} do not carry EXACTLY the locked baseline-6 prompt versions "
        f"[{locked}] — {listing}\n"
        "A resumed set must not mix prompt baselines or carry stripped prompt\n"
        "provenance; re-record the offending seeds.\n"
    )
    raise SystemExit(1)
PYINNER
}

# Refuse to treat a present replay as a corpus game unless its BYTES prove the
# baseline-6 provenance the corpus contract requires. File presence is not
# provenance: the resume skip-scan trusts any non-empty in-range replay, but the
# model/endpoint preflights only govern seeds recorded by THIS run, and the
# MANIFEST cannot carry these checks (its policy column renders an absent stamp
# identically to an explicit one, and its model column derives from the same
# bytes) — so without this guard a foreign replay dropped into the dir would be
# resumed-over and silently FROZEN, leaving the external validity gate to fail
# only AFTER the set was marked frozen. Per replay, four byte-level checks:
#   * the 15.9 tactical-policy stamp is present and equals the FULL five-field
#     canonical fsm_default_tactical_policy_stamp() — matching policy_id alone
#     would accept a hand-crafted stamp with non-canonical method/encoder/
#     weights/anchor fields that the MANIFEST renders indistinguishably;
#   * every model recorded anywhere in it (meeting llm_calls AND failed-call
#     rows) is the locked baseline model — this also refuses a wall-clock-miss
#     "(deadline_default)" phantom, which the validity gate rejects too;
#   * NO failed-call row carries error_type == "deadline_default", whatever its
#     model field says. The model check above is NOT sufficient, and this is the
#     PR #301 review finding: _record_deadline_defaults (orchestrator/game.py)
#     writes deadline defaults in TWO shapes. A participant that submitted
#     nothing yields the zero-spend marker stamped with the
#     "(deadline_default)" sentinel model — caught by the model check. But a
#     participant whose generation FAILED TO PARSE and whose in-turn retry also
#     failed yields one row per burned generation stamped with the REAL baseline
#     model, and the model check waves those straight through. Both shapes mean
#     the same thing: that turn was DEFAULTED, so the transcript carries a
#     fallback husk rather than model output. A frozen training/eval corpus must
#     not contain degraded turns under either shape, so key on error_type, which
#     is the property that actually matters, rather than on the model sentinel,
#     which is an artifact of which branch emitted the row;
#   * its summed cost is exactly $0 (the flat-rate provider contract);
#   * its game_over substrate_flags stamp POSITIVELY carries the DECLARED lever
#     slate — every retired always-on lever present and True, every toggle named
#     by --expect-levers True, every other toggle False — the same tolerant
#     per-lever match the validity gate (check_cost_and_provenance) and the loader
#     (_assert_substrate_matches) enforce. The env preflight only refuses a
#     polluted live slate; this asserts the SLATE in the recorded BYTES, so a
#     stale baseline-5 replay (whose stamp records the four meeting-layer levers
#     OFF) is refused here, at the recorder, not only at the external validity
#     gate.
# Checked pre-spend (before the skip-scan treats a replay as complete) and again
# before the freeze. $0, no network.
check_replay_provenance() {
  local set_dir="$1"
  uv run python - "$REPO_ROOT" "$set_dir" "$DEFAULT_FEATHERLESS_MODEL" \
    "$expect_levers" <<'PYINNER'
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from orchestrator.replay import (  # noqa: E402
    SUBSTRATE_FLAG_KEYS,
    TOGGLEABLE_SUBSTRATE_FLAG_KEYS,
    FailedCallReplayEntry,
    MeetingReplayEntry,
    compute_cost_usd,
    fsm_default_tactical_policy_stamp,
    read_all_entries,
    read_substrate_flags,
    read_tactical_policy_stamp,
)

set_dir, baseline_model = Path(sys.argv[2]), sys.argv[3]
canonical = fsm_default_tactical_policy_stamp()
# The slate this record declared (--expect-levers): every graduated lever ON, the
# named toggles ON, every other toggle OFF. Derived from the DECLARATION rather
# than from the live environment, so a recorded stamp is judged against the slate
# that was ruled -- a shell that drifted after the preflight cannot re-define what
# the bytes are allowed to say.
_expected_on = {key for key in sys.argv[4].split(",") if key}
_toggleable = set(TOGGLEABLE_SUBSTRATE_FLAG_KEYS)
slate = {
    key: (key in _expected_on) if key in _toggleable else True
    for key in SUBSTRATE_FLAG_KEYS
}
canonical_keys = set(SUBSTRATE_FLAG_KEYS)
bad: list[str] = []
for path in sorted(set_dir.glob("replay-seed-*.jsonl")):
    stamp = read_tactical_policy_stamp(path)
    if stamp is None:
        bad.append(f"{path.name}: no tactical_policy stamp")
    elif stamp != canonical:
        bad.append(
            f"{path.name}: tactical_policy stamp differs from the canonical "
            f"fsm-default (got {stamp.model_dump()!r})"
        )
    models: set[str] = set()
    defaulted = 0
    for entry in read_all_entries(path):
        if isinstance(entry, MeetingReplayEntry):
            models.update(call.model for call in entry.llm_calls)
        elif isinstance(entry, FailedCallReplayEntry):
            models.add(entry.model)
            # Phase-18 ledger, labeled in place (Phase 19 tier map,
            # training/README.md §6; audit-phase-18-close.md §7 items 6+7):
            # this freeze-guard branch has no unit test (item 6 —
            # tests/scripts/test_record_ml_corpus.py carries zero
            # deadline_default occurrences), and the validity gate has no
            # deadline_default check at all — the recorder is deliberately
            # stricter than the gate (item 7, unassigned at the close; the
            # gate-side anchor is an absence of code). Frozen as-is.
            # Key on error_type, NOT on the model sentinel: the burned-generation
            # branch stamps the REAL baseline model, so a model-only check misses
            # it entirely (PR #301 review).
            if entry.error_type == "deadline_default":
                defaulted += 1
    foreign = sorted(models - {baseline_model})
    if foreign:
        bad.append(f"{path.name}: non-baseline model(s) recorded: {', '.join(foreign)}")
    if defaulted:
        bad.append(
            f"{path.name}: {defaulted} deadline_default failed-call row(s) — the "
            "turn(s) were DEFAULTED, so the transcript carries a fallback husk "
            "rather than model output; re-record the seed"
        )
    cost = compute_cost_usd(path)
    if cost != 0.0:
        bad.append(f"{path.name}: non-zero recorded cost ${cost:.4f}")
    # POSITIVE substrate-slate assertion: the game_over stamp must CARRY the
    # declared lever slate, not merely survive the env refusal. Same tolerant
    # per-lever match as _assert_substrate_matches: an always-on lever must be
    # present and True, a toggle must match the declared slate on both sides
    # (a missing key reads False), and an unknown key is a stripped/foreign stamp.
    flags = read_substrate_flags(path)
    if flags is None:
        bad.append(f"{path.name}: no substrate_flags stamp on game_over")
    else:
        unknown = sorted(set(flags) - canonical_keys)
        if unknown:
            bad.append(
                f"{path.name}: unknown substrate keys {unknown} "
                f"(not the declared slate {sorted(canonical_keys)})"
            )
        differing = sorted(
            key for key in canonical_keys if bool(flags.get(key)) != bool(slate.get(key))
        )
        if differing:
            bad.append(
                f"{path.name}: substrate stamp disagrees with the declared "
                f"lever slate on {differing} "
                f"(got {dict(sorted(flags.items()))})"
            )
if bad:
    listing = "; ".join(bad)
    sys.stderr.write(
        f"check_replay_provenance: {len(bad)} violation(s) in {set_dir} — {listing}\n"
        "A present replay's bytes must prove the full provenance (the canonical\n"
        "15.9 fsm-default stamp, the locked model on every recorded call, $0 cost,\n"
        "and the DECLARED lever slate on its game_over stamp); presence alone must\n"
        "never make it a corpus game. Remove the file(s) and re-record the seed(s)\n"
        "with this recorder.\n"
    )
    raise SystemExit(1)
PYINNER
}

# --- FREEZE: append the explicit FROZEN line naming the git SHA --------------

# The MANIFEST already stamps git_sha per row (via _manifest_writer update). The
# freeze is an ADDITIONAL explicit marker: a trailing prose line naming the SHA
# of the run that FROZE the set, so a frozen set is unmistakable from the MANIFEST
# alone.
#
# WHAT THAT SHA IS, precisely (PR #301 review): it is HEAD at the moment the
# recording RAN — the CODE STATE that produced these bytes (engine, prompts,
# lever slate). It is NOT, and cannot be, the commit that CONTAINS the frozen
# bytes: that commit does not exist yet when the freeze line is written, so no
# recorder could name it. Checking the sha out therefore gives you the code that
# generated the corpus, not the corpus. The line says so in as many words, because
# reading it as an artifact pointer sends an auditor to the wrong tree. The
# pointer TO the bytes is the commit/tag that lands them (see the corpus README's
# note on the annotated tag). Any pre-existing FROZEN line is stripped first: a per-seed update
# re-renders the table and drops it (so an incomplete re-run is never left looking
# frozen), but a no-op re-finalize — all seeds present, no rows backfilled —
# skips that rewrite, and without the strip each re-run would append a duplicate.
freeze_manifest() {
  local manifest="$1" set_name="$2" git_sha="$3" refreshed_at="$4"
  if ! uv run python - "$manifest" <<'PYINNER'
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
lines = manifest.read_text(encoding="utf-8").splitlines()
kept = [line for line in lines if not line.startswith("**FROZEN**")]
while kept and not kept[-1].strip():  # drop trailing blanks left by old freezes
    kept.pop()
manifest.write_text("\n".join(kept) + "\n", encoding="utf-8")
PYINNER
  then
    return 1
  fi
  {
    printf '\n'
    printf '**FROZEN** — recording-time code state git_sha `%s` (the commit the recorder RAN at, NOT the commit containing these bytes, which cannot exist yet at freeze time; recorded %s; Task 15.12, baseline-7 re-record per Task 20.36): the %s ML-calibration corpus is frozen at Qwen/Qwen3.6-27B Featherless, prompt set %s, lever slate — expected ON = %s, every other live toggle OFF, the graduated levers unconditional ON — tactical policy %s. By-game split rule: %s. Do not re-record without re-freezing.\n' \
      "$git_sha" "$refreshed_at" "$set_name" "$REQUIRED_PROMPT_SET" "$expect_levers_desc" "$POLICY_STAMP" "$SPLIT_RULE_DESC"
  } >>"$manifest"
  echo "  FROZEN: $manifest at git_sha $git_sha"
}

# --- --splits-only: regenerate splits from disk, then exit (no network) -------

if [[ "$splits_only" -eq 1 ]]; then
  for set_name in "${sets[@]}"; do
    read -r _start _count _np _ni _tpc <<<"$(set_config "$set_name")"
    set_dir="$CORPUS_ROOT/$set_name"
    if [[ ! -d "$set_dir" ]]; then
      echo "Error: --splits-only: $set_dir does not exist (record the set first)." >&2
      exit 1
    fi
    echo "=== splits-only: $set_name ($set_dir) ==="
    # A stray out-of-range replay would otherwise be partitioned into the splits,
    # and a MISSING in-range seed would silently write a SHORT splits.json (a
    # partial train/val/test is never a valid committed artifact). Both are
    # refused before a byte is written.
    check_seed_range "$set_dir" "$_start" "$((_start + _count - 1))"
    check_seed_count "$set_dir" "$_start" "$((_start + _count - 1))"
    write_splits "$set_name" "$set_dir"
  done
  exit 0
fi

# --- dry-run: print the plan; touch nothing ---------------------------------

if [[ "$dry_run" -eq 1 ]]; then
  echo "[dry-run] sets: ${sets[*]}"
  echo "[dry-run] corpus root: $CORPUS_ROOT"
  echo "[dry-run] provider: featherless (LOCKED — the corpus is baseline-6)"
  echo "[dry-run] preflight: would require FEATHERLESS_API_KEY (hosted run; \$0 provider-keyed cost)"
  echo "[dry-run] prompt set: $REQUIRED_PROMPT_SET (must be exported as AILIBI_PROMPT_SET)"
  echo "[dry-run] model: $DEFAULT_FEATHERLESS_MODEL (meeting + trigger pinned; a non-baseline AILIBI_LLM_MEETING_MODEL/AILIBI_LLM_TRIGGER_MODEL override is refused)"
  echo "[dry-run] endpoint: $DEFAULT_FEATHERLESS_BASE_URL (pinned; a non-default AILIBI_FEATHERLESS_BASE_URL override is refused)"
  echo "[dry-run] prompt versions: locked to [$REQUIRED_PROMPT_VERSIONS] (the registry is asserted at preflight; rows off this map are refused at freeze)"
  echo "[dry-run] substrate flags: expected levers ON = $expect_levers_desc; every other live toggle OFF; the graduated levers unconditional ON"
  echo "[dry-run] substrate-lever preflight: would require the live lever slate to equal that expectation exactly and refuse before any seed stages — an expected-ON lever left unexported and an unexpected AILIBI_* export are both named"
  echo "[dry-run] tactical policy stamp: $POLICY_STAMP (15.9 FSM-default on every game)"
  if [[ "$REFRESH_WORKERS" -gt 1 ]]; then
    echo "[dry-run] seed workers: $REFRESH_WORKERS parallel (each records one seed, then pulls the next available seed from the queue; Featherless: 2 units per 27B request → 4-unit cap)"
  else
    echo "[dry-run] seed workers: 1 (sequential)"
  fi
  echo "[dry-run] seed crash-retry: up to $SEED_MAX_ATTEMPTS attempt(s) per seed on a transport/crash error (recorded parse failures are non-fatal)"
  echo "[dry-run] resume: seeds whose replay already exists in the set dir are skipped (a re-run records only the missing ones; a present replay must carry the explicit $POLICY_STAMP tactical-policy stamp or the run is refused)"
  echo "[dry-run] split rule: $SPLIT_RULE_DESC (by game; no game in two splits)"
  for set_name in "${sets[@]}"; do
    read -r start count np ni tpc <<<"$(set_config "$set_name")"
    last=$((start + count - 1))
    set_dir="$CORPUS_ROOT/$set_name"
    echo "[dry-run] --- set $set_name ---"
    echo "[dry-run]   seed range: $start..$last ($count games)"
    echo "[dry-run]   roster: num_players=$np num_impostors=$ni tasks_per_crewmate=$tpc"
    echo "[dry-run]   output dir: $set_dir"
    echo "[dry-run]   roster descriptor: would ensure $set_dir/roster.json = {num_players: $np, num_impostors: $ni, tasks_per_crewmate: $tpc}"
    echo "[dry-run]   per seed, would run via a temp stage (then move the replay in and update that seed's manifest row):"
    echo "[dry-run]     AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=$REQUIRED_PROMPT_SET uv run python scripts/run_tournament.py --start-seed <seed> --num-games 1 --output-dir <stage> --num-players $np --num-impostors $ni --tasks-per-crewmate $tpc --tactical-policy-stamp $POLICY_STAMP --force"
    echo "[dry-run]   manifest: $set_dir/MANIFEST.md (rows carry the $POLICY_STAMP policy column)"
    echo "[dry-run]   eval report: would rebuild $set_dir/tournament-eval-report.json (scripts/build_sample_report.py; \$0, no provider)"
    echo "[dry-run]   splits: would write $set_dir/splits.json ($SPLIT_RULE_DESC)"
    echo "[dry-run]   freeze: would append a FROZEN line naming the git_sha to $set_dir/MANIFEST.md"
  done
  echo "[dry-run] acceptance (per set, before merge): scripts/validity_gate.py <set> --expected-model $DEFAULT_FEATHERLESS_MODEL --require-zero-cost; scripts/verify_samples.sh <set>"
  echo "[dry-run] no API calls made; no files written."
  if ! substrate_lever_preflight; then
    exit 1
  fi
  exit 0
fi

# --- real path: preflight (provider LOCKED to featherless) -------------------

# The corpus is baseline 6 == Featherless. Refuse any other provider so a corpus
# game can never be silently recorded off-substrate (the fake CI provider, an
# anthropic/ollama misconfiguration). Read the ambient AILIBI_LLM_PROVIDER only to
# REJECT a wrong one; the recorder always exports featherless below.
PROVIDER="$(printf '%s' "${AILIBI_LLM_PROVIDER:-featherless}" | tr '[:upper:]' '[:lower:]')"
if [[ "$PROVIDER" != "featherless" ]]; then
  echo "Error: the ML-calibration corpus is baseline-6, so it records ONLY on featherless." >&2
  echo "       Unset AILIBI_LLM_PROVIDER or set it to 'featherless' (got '$PROVIDER')." >&2
  exit 1
fi

if [[ -z "${FEATHERLESS_API_KEY:-}" ]]; then
  echo "Error: FEATHERLESS_API_KEY must be set to record the ML-calibration corpus." >&2
  exit 1
fi
echo "Using Featherless API key prefix: ${FEATHERLESS_API_KEY:0:8}"

if [[ "${AILIBI_PROMPT_SET:-}" != "$REQUIRED_PROMPT_SET" ]]; then
  echo "Error: the corpus must record the locked baseline-6 substrate (Task 18.13)." >&2
  echo "       Export the locked prompt set before re-running; nothing was recorded:" >&2
  echo "  - AILIBI_PROMPT_SET must be '$REQUIRED_PROMPT_SET' (got '${AILIBI_PROMPT_SET:-<unset>}')" >&2
  exit 1
fi

# ... and the LEVER SLATE, before any seed stages (the function above states why).
if ! substrate_lever_preflight; then
  exit 1
fi
echo "Locked substrate OK: AILIBI_PROMPT_SET=$REQUIRED_PROMPT_SET."

# Baseline-5 also locks the MODEL: build_default_client honors
# AILIBI_LLM_MEETING_MODEL / AILIBI_LLM_TRIGGER_MODEL for featherless, so a
# leftover export from a model sweep would silently record the whole multi-hour
# corpus on a non-baseline model while the MANIFEST/no-meeting rows keep stamping
# $DEFAULT_FEATHERLESS_MODEL. Refuse any non-baseline override (AGENTS.md "no
# silent fallbacks" — never silently discard an operator's explicit setting),
# then export both knobs pinned to the baseline so the recorded model can never
# drift from the stamped one.
for model_env in AILIBI_LLM_MEETING_MODEL AILIBI_LLM_TRIGGER_MODEL; do
  model_val="${!model_env:-}"
  if [[ -n "$model_val" && "$model_val" != "$DEFAULT_FEATHERLESS_MODEL" ]]; then
    echo "Error: the corpus must record the locked baseline-6 model ($DEFAULT_FEATHERLESS_MODEL)." >&2
    echo "       $model_env='$model_val' would record off-baseline while the MANIFEST stamps the baseline model." >&2
    echo "       Unset $model_env (or set it to '$DEFAULT_FEATHERLESS_MODEL') and re-run; nothing was recorded." >&2
    exit 1
  fi
done
export AILIBI_LLM_MEETING_MODEL="$DEFAULT_FEATHERLESS_MODEL"
export AILIBI_LLM_TRIGGER_MODEL="$DEFAULT_FEATHERLESS_MODEL"
echo "Locked model OK: meeting/trigger models pinned to $DEFAULT_FEATHERLESS_MODEL."

# ... and the ENDPOINT: build_default_client also honors AILIBI_FEATHERLESS_BASE_URL
# (llm/provider.py ENV_FEATHERLESS_BASE_URL), so a leftover export for a mock or
# staging endpoint would record the whole "baseline-6 Featherless" corpus against
# an alternate server while the MANIFEST stamps the baseline model and $0 — and
# the validity gate cannot catch it if that endpoint echoes the same model id.
# Refuse any non-default override (never silently discard an operator's explicit
# setting), then export the knob pinned to the hosted endpoint.
if [[ -n "${AILIBI_FEATHERLESS_BASE_URL:-}" \
  && "${AILIBI_FEATHERLESS_BASE_URL}" != "$DEFAULT_FEATHERLESS_BASE_URL" ]]; then
  echo "Error: the corpus must record against the hosted Featherless endpoint ($DEFAULT_FEATHERLESS_BASE_URL)." >&2
  echo "       AILIBI_FEATHERLESS_BASE_URL='${AILIBI_FEATHERLESS_BASE_URL}' would record against an alternate endpoint while the MANIFEST stamps the baseline substrate." >&2
  echo "       Unset AILIBI_FEATHERLESS_BASE_URL (or set it to '$DEFAULT_FEATHERLESS_BASE_URL') and re-run; nothing was recorded." >&2
  exit 1
fi
export AILIBI_FEATHERLESS_BASE_URL="$DEFAULT_FEATHERLESS_BASE_URL"
echo "Locked endpoint OK: base URL pinned to $DEFAULT_FEATHERLESS_BASE_URL."

# ... and the PROMPT VERSIONS, not just the set name: the corpus contract freezes
# the baseline-6 versions (all four templates at v3), but AILIBI_PROMPT_SET
# names a REGISTRY entry whose per-template versions can be bumped by a later
# task. If that happens, re-running/resuming this recorder would silently record
# (or mix) a non-baseline-prompt corpus and freeze it as Task 15.12. Assert the
# live registry still resolves the set to EXACTLY the locked map; a mismatch is a
# fail-loud stop — re-locking the corpus to a new prompt baseline is an owner
# decision (a re-record + re-freeze), never a silent drift.
if ! check_prompt_version_registry; then
  exit 1
fi
echo "Locked prompt versions OK: $REQUIRED_PROMPT_SET resolves to the baseline-6 map ($REQUIRED_PROMPT_VERSIONS)."

# Export the resolved provider so run_tournament.py records on Featherless — never
# fall through to build_default_client()'s fake default (which would silently
# record fake output at $0 with the wrong model).
export AILIBI_LLM_PROVIDER="featherless"

# Provenance shared by every seed in this run.
git_sha="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
refreshed_at="$(date -u +%F)"
echo "Recording at git_sha $git_sha, model $DEFAULT_FEATHERLESS_MODEL, policy $POLICY_STAMP."

corpus_start="$(date +%s)"

# --- record ONE set: stage + move + manifest + report + splits + freeze ------

record_set() {
  local set_name="$1"
  local start count np ni tpc set_dir manifest
  read -r start count np ni tpc <<<"$(set_config "$set_name")"
  set_dir="$CORPUS_ROOT/$set_name"
  manifest="$set_dir/MANIFEST.md"
  local last=$((start + count - 1))
  echo "===================================================================="
  echo "Recording corpus set $set_name: seeds $start..$last ($count games), "
  echo "  roster ${np}p/${ni}i @ ${tpc} task(s)/crewmate -> $set_dir"
  echo "===================================================================="

  # record_set is invoked in an `if ! record_set ...` conditional, which disables
  # errexit for the whole function body (Bash semantics) — so every step that
  # must not be skipped over on failure carries an EXPLICIT `if ! ...; then
  # return 1` guard. Without them a failed roster pin / manifest refresh / report
  # rebuild / splits write would fall through and still FREEZE the set with a
  # zero exit status.
  if ! mkdir -p "$set_dir"; then
    echo "ERROR: could not create $set_dir; nothing recorded." >&2
    return 1
  fi
  # Refuse a dirty set dir BEFORE spending: a stray replay outside the locked
  # range would survive the resume skip-scan and be swept into the finalize.
  if ! check_seed_range "$set_dir" "$start" "$last"; then
    return 1
  fi
  # File presence is not provenance: before the resume skip-scan treats a present
  # replay as "already recorded", prove its bytes carry the full baseline-6
  # provenance — the canonical five-field 15.9 stamp, the locked model on every
  # recorded call, and $0 cost (see check_replay_provenance — a foreign replay
  # would otherwise freeze undetected).
  if ! check_replay_provenance "$set_dir"; then
    return 1
  fi
  # Pin the set's roster.json BEFORE spending, so the recorded replays reconstruct
  # from their own descriptor (fails loud if an existing one disagrees).
  if ! uv run python "$REPO_ROOT/scripts/_manifest_writer.py" roster \
    --sample-dir "$set_dir" \
    --num-players "$np" \
    --num-impostors "$ni" \
    --tasks-per-crewmate "$tpc"; then
    echo "ERROR: roster pin failed for $set_name; nothing recorded." >&2
    return 1
  fi

  # Build the contiguous seed list for this set, SKIPPING any seed whose replay is
  # already present in the set dir (RESUME): a re-run after an interruption records
  # only the missing seeds. The per-seed move is atomic, so an existing replay in
  # the set dir is always complete. A fully-recorded set records nothing here and
  # jumps straight to the finalize (report + splits + freeze), which is idempotent.
  local -a seed_list=()
  local s already=0
  for ((s = start; s <= last; s++)); do
    if [[ -s "$set_dir/replay-seed-$s.jsonl" ]]; then
      already=$((already + 1))
      continue
    fi
    seed_list+=("$s")
  done
  local total_seeds="${#seed_list[@]}"
  if [[ "$already" -gt 0 ]]; then
    echo "Resume: $already/$count seed(s) already recorded; $total_seeds remaining."
  fi

  # Stage per-seed runs on the same filesystem as the set dir so the replay can be
  # moved into place atomically, and only after the run succeeds. Each seed gets
  # its OWN sub-stage, so parallel workers never collide on run_tournament's
  # per-run tournament-eval-report.json / <stem>.audit.jsonl sidecars — and ONLY
  # the replay JSONL is moved in (the audit sidecar + per-run report stay in the
  # discarded stage, so the set dir holds no non-replay JSONL the validity gate /
  # loader would trip on).
  local stage_dir
  if ! stage_dir="$(mktemp -d "$set_dir/.ailibi-corpus-stage-XXXXXX")"; then
    echo "ERROR: could not create the staging dir under $set_dir; nothing recorded." >&2
    return 1
  fi
  # shellcheck disable=SC2064
  trap "rm -rf '$stage_dir'" RETURN

  # Shared cross-worker state (mirrors refresh_samples.sh). Files on the stage fs,
  # mutated only under a portable mkdir-based lock so two workers never corrupt
  # MANIFEST.md (a read-modify-write) or garble the progress stream.
  mkdir -p "$stage_dir/.state"
  printf '0' >"$stage_dir/.next_idx"
  printf '0' >"$stage_dir/.state/completed"
  printf '0' >"$stage_dir/.state/meetings"
  local lockdir="$stage_dir/.lock"

  # Phase-18 ledger, labeled in place (Phase 19 tier map, training/README.md §6;
  # audit-phase-18-close.md §7 item 5 — the recorder lock-race): the Bash-3.2
  # dead-owner degradation recorded below is the known limitation; frozen as-is.
  # Portable mkdir mutex with DEAD-OWNER detection: the holder records its PID; a
  # waiter that finds the lock owned by a dead process marks the run failed (the
  # half-written MANIFEST is unsafe to freeze) and gives up. Returns non-zero when
  # the lock was NOT acquired — callers must not enter the critical section then.
  # The owner PID uses $BASHPID (the WORKER subshell's own PID) when available, and
  # falls back to $$ on macOS's stock Bash 3.2, which predates $BASHPID (the ${:-}
  # form is exempt from `set -u`, so an undefined $BASHPID never fatally aborts the
  # worker there). On 3.2 every worker shares $$ (the main shell), so dead-owner
  # detection degrades to a no-op — the mkdir mutex + release still serialize
  # correctly; only the rare "a worker was SIGKILLed mid-critical-section" safety
  # net is lost. Install a newer bash (`brew install bash`) to restore it.
  acquire_lock() {
    local owner
    [[ -e "$stage_dir/.failed" ]] && return 1
    while ! mkdir "$lockdir" 2>/dev/null; do
      if [[ -e "$stage_dir/.failed" ]]; then
        return 1
      fi
      owner="$(cat "$lockdir/owner" 2>/dev/null || true)"
      if [[ -n "$owner" ]] && ! kill -0 "$owner" 2>/dev/null; then
        echo "ERROR: corpus lock owner (pid $owner) died holding the lock" \
          "(killed/crashed mid critical section); the set is incomplete." >&2
        touch "$stage_dir/.failed"
        return 1
      fi
      sleep 0.1
    done
    printf '%s' "${BASHPID:-$$}" >"$lockdir/owner"
    return 0
  }
  release_lock() { rm -rf "$lockdir" 2>/dev/null || true; }

  # Atomically claim the next unclaimed seed (the queue). Echoes the seed, or
  # nothing when drained. Lock-guarded so no seed is double-recorded or skipped.
  claim_next_seed() {
    local idx
    acquire_lock || return 1
    idx="$(cat "$stage_dir/.next_idx")"
    if [[ "$idx" -ge "$total_seeds" ]]; then
      release_lock
      return 0
    fi
    printf '%s' "$((idx + 1))" >"$stage_dir/.next_idx"
    release_lock
    printf '%s' "${seed_list[$idx]}"
  }

  # Record ONE seed end to end: stage the run (with the FSM-default policy stamp),
  # atomically move the replay into the set dir, then (serialized) sync its
  # MANIFEST row + tally + a progress line. Any failure touches .failed and returns
  # non-zero so the pool stops claiming — the set must be COMPLETE or not frozen.
  # Always invoked in a `||` context, so set -e is disabled inside it.
  record_one_seed() {
    local seed="$1" worker="$2"
    local seed_stage seed_start now seed_secs elapsed eta rate completed meetings seed_meeting
    local attempt max_attempts
    max_attempts="$SEED_MAX_ATTEMPTS"
    seed_start="$(date +%s)"
    echo "--- [worker $worker] recording $set_name seed $seed ---"
    if ! seed_stage="$(mktemp -d "$stage_dir/seed-${seed}-XXXXXX")"; then
      echo "ERROR: seed $seed stage mktemp failed (worker $worker); nothing spent." >&2
      touch "$stage_dir/.failed"
      return 1
    fi
    attempt=0
    while :; do
      attempt=$((attempt + 1))
      if uv run python "$REPO_ROOT/scripts/run_tournament.py" \
        --start-seed "$seed" \
        --num-games 1 \
        --output-dir "$seed_stage" \
        --num-players "$np" \
        --num-impostors "$ni" \
        --tasks-per-crewmate "$tpc" \
        --tactical-policy-stamp "$POLICY_STAMP" \
        --force; then
        break
      fi
      if [[ "$attempt" -ge "$max_attempts" ]]; then
        echo "ERROR: seed $seed run_tournament failed after $attempt attempts (worker $worker)." >&2
        touch "$stage_dir/.failed"
        rm -rf "$seed_stage"
        return 1
      fi
      echo "WARN: seed $seed attempt $attempt/$max_attempts failed (worker $worker); retrying after $((attempt * 15))s (transient provider/network error)." >&2
      sleep "$((attempt * 15))"
    done
    # Atomic replace on success; move ONLY the replay JSONL (leave the audit
    # sidecar + per-run report in the discarded stage).
    if ! mv -f "$seed_stage/replay-seed-$seed.jsonl" \
      "$set_dir/replay-seed-$seed.jsonl"; then
      echo "ERROR: seed $seed replay move failed (worker $worker)." >&2
      touch "$stage_dir/.failed"
      rm -rf "$seed_stage"
      return 1
    fi
    rm -rf "$seed_stage"
    if grep -q 'meeting_id' "$set_dir/replay-seed-$seed.jsonl"; then
      seed_meeting="yes"
    else
      seed_meeting="no "
    fi
    # Serialize the MANIFEST update + tally bump + progress print.
    if ! acquire_lock; then
      echo "ERROR: seed $seed could not acquire the manifest lock (worker $worker)." >&2
      return 1
    fi
    if ! uv run python "$REPO_ROOT/scripts/_manifest_writer.py" update \
      --seeds "$seed" \
      --git-sha "$git_sha" \
      --refreshed-at "$refreshed_at" \
      --model "$DEFAULT_FEATHERLESS_MODEL" \
      --sample-dir "$set_dir" \
      --manifest "$manifest"; then
      release_lock
      echo "ERROR: seed $seed manifest update failed (worker $worker)." >&2
      touch "$stage_dir/.failed"
      return 1
    fi
    completed="$(($(cat "$stage_dir/.state/completed") + 1))"
    printf '%s' "$completed" >"$stage_dir/.state/completed"
    meetings="$(cat "$stage_dir/.state/meetings")"
    if [[ "$seed_meeting" == "yes" ]]; then
      meetings=$((meetings + 1))
      printf '%s' "$meetings" >"$stage_dir/.state/meetings"
    fi
    now="$(date +%s)"
    seed_secs=$((now - seed_start))
    elapsed=$((now - corpus_start))
    rate=$((meetings * 100 / completed))
    eta=$((elapsed * (total_seeds - completed) / completed))
    printf '    %s seed %s done in %3ds | meeting: %s | meetings %d/%d (%d%%) | done %d/%d | elapsed %dm%02ds | ETA ~%dm\n' \
      "$set_name" "$seed" "$seed_secs" "$seed_meeting" "$meetings" "$completed" "$rate" \
      "$completed" "$total_seeds" "$((elapsed / 60))" "$((elapsed % 60))" "$((eta / 60))"
    release_lock
    return 0
  }

  # One worker: pull the next seed and record it until the queue drains or any
  # worker flags a failure. Returns 0 even on a recorded failure — the .failed
  # sentinel (checked after the pool joins) is the fail-loud signal.
  run_worker() {
    local worker="$1" seed
    while :; do
      [[ -e "$stage_dir/.failed" ]] && return 0
      seed="$(claim_next_seed)"
      [[ -z "$seed" ]] && return 0
      record_one_seed "$seed" "$worker" || return 0
    done
  }

  if [[ "$REFRESH_WORKERS" -gt 1 ]]; then
    echo "Recording $total_seeds seeds with $REFRESH_WORKERS parallel workers" \
      "(each records one seed, then pulls the next available seed from the queue)."
    local -a worker_pids=()
    local w
    for ((w = 1; w <= REFRESH_WORKERS; w++)); do
      run_worker "$w" &
      worker_pids+=("$!")
    done
    local pid
    for pid in "${worker_pids[@]}"; do
      if ! wait "$pid"; then
        touch "$stage_dir/.failed"
        echo "ERROR: corpus worker (pid $pid) exited non-zero (killed/crashed" \
          "outside a seed's handled failure path); the set is incomplete." >&2
      fi
    done
  else
    run_worker 1
  fi

  if [[ -e "$stage_dir/.failed" ]]; then
    echo "Error: a seed failed while recording $set_name; the set is INCOMPLETE and must NOT be frozen/committed." >&2
    echo "       Already-recorded seeds + their MANIFEST rows are preserved on disk; fix the failure and re-run." >&2
    return 1
  fi

  local meetings_seen
  meetings_seen="$(cat "$stage_dir/.state/meetings")"
  echo "Set $set_name recorded: $meetings_seen/$total_seeds seeds reached a meeting"
  echo "  (authoritative meeting_rate is in the eval report)."

  # Re-validate the set dir right before the finalize sweeps it by filename: a
  # stray out-of-range replay that appeared mid-run must never be frozen in.
  if ! check_seed_range "$set_dir" "$start" "$last"; then
    echo "ERROR: $set_name holds replays outside seeds $start..$last; NOT freezing." >&2
    return 1
  fi
  # ... and the EXACT count: refuse to freeze a set that is missing any in-range
  # seed. The finalize below derives the MANIFEST/report/splits from whatever is
  # present, so without this a short set (a defaulted seed dropped from a resumed
  # leg, a lost replay) would freeze as if complete (PR #301 review). This is the
  # hard invariant behind the README's "drop phantoms only after the leg drains"
  # note — enforced now, not left to operator discipline.
  if ! check_seed_count "$set_dir" "$start" "$last"; then
    echo "ERROR: $set_name is not the exact locked seed set; NOT freezing." >&2
    return 1
  fi

  # Backfill MANIFEST rows for seeds that have a replay on disk but NO row (the
  # crash window: a replay was moved into place but its per-seed MANIFEST update
  # never ran); $0, no provider call. ONLY row-less seeds are stamped — seeds
  # recorded by an earlier session keep their existing rows' git_sha untouched,
  # so a resume never rewrites the provenance of bytes it did not record (the
  # per-seed history is exactly what a later audit reads; the FROZEN line names
  # the sha of the run that FROZE the set).
  local missing_csv
  if ! missing_csv="$(_seeds_missing_rows_csv "$set_dir" "$manifest")"; then
    echo "ERROR: could not reconcile recorded seeds with $manifest; NOT freezing." >&2
    return 1
  fi
  if [[ -n "$missing_csv" ]]; then
    echo "Backfilling MANIFEST rows for row-less seeds: $missing_csv ..."
    if ! uv run python "$REPO_ROOT/scripts/_manifest_writer.py" update \
      --seeds "$missing_csv" \
      --git-sha "$git_sha" \
      --refreshed-at "$refreshed_at" \
      --model "$DEFAULT_FEATHERLESS_MODEL" \
      --sample-dir "$set_dir" \
      --manifest "$manifest"; then
      echo "ERROR: the MANIFEST backfill failed for $set_name; NOT freezing." >&2
      return 1
    fi
  fi

  # Refuse to freeze rows recorded under a different prompt baseline (the resume
  # counterpart of the preflight registry pin — see check_recorded_prompt_versions).
  if ! check_recorded_prompt_versions "$set_dir" "$manifest"; then
    echo "ERROR: $set_name carries non-baseline prompt versions; NOT freezing." >&2
    return 1
  fi

  # Refuse to freeze a replay whose bytes fail the full baseline-6 provenance
  # check (re-run of the pre-spend guard over the now-complete set, incl.
  # anything that appeared mid-run; MANIFEST rows cannot carry this check — see
  # check_replay_provenance).
  if ! check_replay_provenance "$set_dir"; then
    echo "ERROR: $set_name holds replays that fail baseline-6 provenance; NOT freezing." >&2
    return 1
  fi

  # Rebuild the derived eval report (roles ground truth) from the recorded replays.
  echo "Rebuilding eval report for $set_name ..."
  if ! uv run python "$REPO_ROOT/scripts/build_sample_report.py" --sample-dir "$set_dir"; then
    echo "ERROR: the eval-report rebuild failed for $set_name; NOT freezing." >&2
    return 1
  fi

  # Write the committed by-game splits.json.
  echo "Writing splits.json for $set_name ..."
  if ! write_splits "$set_name" "$set_dir"; then
    echo "ERROR: writing splits.json failed for $set_name; NOT freezing." >&2
    return 1
  fi

  # FREEZE: append the explicit FROZEN line naming the git SHA (last, after every
  # per-seed MANIFEST update, so the freeze line survives the final render).
  if ! freeze_manifest "$manifest" "$set_name" "$git_sha" "$refreshed_at"; then
    echo "ERROR: appending the FROZEN line failed for $set_name." >&2
    return 1
  fi
  echo "Set $set_name complete and FROZEN."
}

overall_status=0
for set_name in "${sets[@]}"; do
  if ! record_set "$set_name"; then
    overall_status=1
    echo "Stopping: $set_name did not complete cleanly." >&2
    break
  fi
done

corpus_wall=$(($(date +%s) - corpus_start))
if [[ "$overall_status" -eq 0 ]]; then
  echo "===================================================================="
  echo "Corpus recording complete in $((corpus_wall / 60))m$((corpus_wall % 60))s."
  echo "Acceptance (run per set before committing the PR):"
  for set_name in "${sets[@]}"; do
    echo "  uv run python scripts/validity_gate.py $CORPUS_ROOT/$set_name --expected-model $DEFAULT_FEATHERLESS_MODEL --require-zero-cost"
    echo "  scripts/verify_samples.sh $CORPUS_ROOT/$set_name"
  done
else
  echo "Corpus recording INCOMPLETE after $((corpus_wall / 60))m$((corpus_wall % 60))s; do not commit." >&2
fi
exit "$overall_status"
