#!/usr/bin/env bash
#
# record_ml_corpus.sh — record the frozen ML-calibration corpus at baseline-3
# config (Task 15.12; audits/post-phase-14-ML-training-signal.md §5.6, §7.2;
# tasks/post-phase-14-plan.md §4).
#
# The surrogate (15.13) and the impostor bake-off (15.15+) consume a FROZEN
# training/calibration corpus recorded at EXACT baseline-3 config — the 15.7
# substrate: Qwen/Qwen3-32B on Featherless, the qwen3_32b prompt set (turn/opening
# at v5, vote_ballot at v6), all substrate levers unconditionally ON, $0 flat-rate.
# Nothing trains against a meeting layer scheduled to change, so this corpus is a
# SEPARATE release artifact from the canonical samples: it lands under
# replays/ml_corpus/ (NOT replays/samples/), at fresh seed ranges so a corpus game
# can never be confused with a canonical 0–49 game.
#
# Two sets, ~3x the canonical 9p2i meeting/ejection volume (~7h wall with 2
# Featherless seed workers):
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
#       --expected-model Qwen/Qwen3-32B --require-zero-cost
#   scripts/verify_samples.sh replays/ml_corpus/<set>        # byte-verify
#
# Hosted models do NOT byte-reproduce FRESH generation; RECORDINGS replay
# byte-identically (the loosened contract the canonical baselines already carry),
# so the validity gate + byte-verify — not generation-replay equality — is the
# acceptance.
#
# Usage:
#   scripts/record_ml_corpus.sh [--set 9p2i|4p1i|both] [--dry-run | --splits-only]
#
#   --set 9p2i|4p1i|both  which set(s) to record (default: both)
#   --dry-run             print the resolved plan; touch nothing, no network
#   --splits-only         (re)write splits.json for the selected set(s) from the
#                         replays already on disk, then exit — no network, no record
#   -h, --help            show this help
#
# Operator gate: requires FEATHERLESS_API_KEY and AILIBI_PROMPT_SET=qwen3_32b; the
# corpus is baseline-3, so the provider is LOCKED to featherless (a run under any
# other provider — including the fake CI provider — is refused, so a corpus game
# can never be silently recorded off-substrate, AGENTS.md "no silent fallbacks").
# ~7h wall; commit is one atomic PR after the gate + byte-verify pass per set. May
# share the 15.7 operator session.

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

# The locked Featherless baseline model (Task 14.6); mirrors
# llm.featherless_client.DEFAULT_FEATHERLESS_MODEL and refresh_samples.sh. Stamped
# onto no-meeting rows and asserted by the operator's --expected-model gate.
DEFAULT_FEATHERLESS_MODEL="Qwen/Qwen3-32B"
# The locked prompt set the corpus records under (baseline 3; Task 15.7). A
# featherless run with any other set would SILENTLY record the wrong substrate.
REQUIRED_PROMPT_SET="qwen3_32b"
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

  --set 9p2i|4p1i|both  which corpus set(s) to record (default: both)
  --dry-run             print the resolved plan; touch nothing, make no API call
  --splits-only         (re)write splits.json for the selected set(s) from the
                        replays already on disk, then exit (no network, no record)
  -h, --help            show this help

Records the frozen ML-calibration corpus at baseline-3 config into
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

# TWO seed workers saturate the hosted Featherless plan (4 concurrent units; a 32B
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

# --- FREEZE: append the explicit FROZEN line naming the git SHA --------------

# The MANIFEST already stamps git_sha per row (via _manifest_writer update). The
# freeze is an ADDITIONAL explicit marker: a trailing prose line naming the SHA
# the corpus was recorded at, so a frozen set is unmistakable from the MANIFEST
# alone. Appended AFTER the last per-seed update (a re-record re-renders the table
# and drops this line, so an incomplete re-run is never left looking frozen).
freeze_manifest() {
  local manifest="$1" set_name="$2" git_sha="$3" refreshed_at="$4"
  {
    printf '\n'
    printf '**FROZEN** at git_sha `%s` (recorded %s; Task 15.12): the %s ML-calibration corpus is frozen at baseline-3 config (Qwen/Qwen3-32B Featherless, prompt set %s, all substrate levers ON, tactical policy %s). By-game split rule: %s. Do not re-record without re-freezing.\n' \
      "$git_sha" "$refreshed_at" "$set_name" "$REQUIRED_PROMPT_SET" "$POLICY_STAMP" "$SPLIT_RULE_DESC"
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
    write_splits "$set_name" "$set_dir"
  done
  exit 0
fi

# --- dry-run: print the plan; touch nothing ---------------------------------

if [[ "$dry_run" -eq 1 ]]; then
  echo "[dry-run] sets: ${sets[*]}"
  echo "[dry-run] corpus root: $CORPUS_ROOT"
  echo "[dry-run] provider: featherless (LOCKED — the corpus is baseline-3)"
  echo "[dry-run] preflight: would require FEATHERLESS_API_KEY (hosted run; \$0 provider-keyed cost)"
  echo "[dry-run] prompt set: $REQUIRED_PROMPT_SET (must be exported as AILIBI_PROMPT_SET)"
  echo "[dry-run] substrate flags: all five levers ON (unconditional; 13.5 since Task 14.9, evidence_quality_lift since the 14.12 close)"
  echo "[dry-run] tactical policy stamp: $POLICY_STAMP (15.9 FSM-default on every game)"
  if [[ "$REFRESH_WORKERS" -gt 1 ]]; then
    echo "[dry-run] seed workers: $REFRESH_WORKERS parallel (each records one seed, then pulls the next available seed from the queue; Featherless: 2 units per 32B request → 4-unit cap)"
  else
    echo "[dry-run] seed workers: 1 (sequential)"
  fi
  echo "[dry-run] seed crash-retry: up to $SEED_MAX_ATTEMPTS attempt(s) per seed on a transport/crash error (recorded parse failures are non-fatal)"
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
  exit 0
fi

# --- real path: preflight (provider LOCKED to featherless) -------------------

# The corpus is baseline 3 == Featherless. Refuse any other provider so a corpus
# game can never be silently recorded off-substrate (the fake CI provider, an
# anthropic/ollama misconfiguration). Read the ambient AILIBI_LLM_PROVIDER only to
# REJECT a wrong one; the recorder always exports featherless below.
PROVIDER="$(printf '%s' "${AILIBI_LLM_PROVIDER:-featherless}" | tr '[:upper:]' '[:lower:]')"
if [[ "$PROVIDER" != "featherless" ]]; then
  echo "Error: the ML-calibration corpus is baseline-3, so it records ONLY on featherless." >&2
  echo "       Unset AILIBI_LLM_PROVIDER or set it to 'featherless' (got '$PROVIDER')." >&2
  exit 1
fi

if [[ -z "${FEATHERLESS_API_KEY:-}" ]]; then
  echo "Error: FEATHERLESS_API_KEY must be set to record the ML-calibration corpus." >&2
  exit 1
fi
echo "Using Featherless API key prefix: ${FEATHERLESS_API_KEY:0:8}"

if [[ "${AILIBI_PROMPT_SET:-}" != "$REQUIRED_PROMPT_SET" ]]; then
  echo "Error: the corpus must record the locked baseline-3 substrate (Task 15.7)." >&2
  echo "       Export the locked prompt set before re-running; nothing was recorded:" >&2
  echo "  - AILIBI_PROMPT_SET must be '$REQUIRED_PROMPT_SET' (got '${AILIBI_PROMPT_SET:-<unset>}')" >&2
  exit 1
fi
echo "Locked substrate OK: AILIBI_PROMPT_SET=$REQUIRED_PROMPT_SET (all five levers unconditionally ON)."

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

  mkdir -p "$set_dir"
  # Pin the set's roster.json BEFORE spending, so the recorded replays reconstruct
  # from their own descriptor (fails loud if an existing one disagrees).
  uv run python "$REPO_ROOT/scripts/_manifest_writer.py" roster \
    --sample-dir "$set_dir" \
    --num-players "$np" \
    --num-impostors "$ni" \
    --tasks-per-crewmate "$tpc"

  # Build the contiguous seed list for this set.
  local -a seed_list=()
  local s
  for ((s = start; s <= last; s++)); do
    seed_list+=("$s")
  done
  local total_seeds="${#seed_list[@]}"

  # Stage per-seed runs on the same filesystem as the set dir so the replay can be
  # moved into place atomically, and only after the run succeeds. Each seed gets
  # its OWN sub-stage, so parallel workers never collide on run_tournament's
  # per-run tournament-eval-report.json / <stem>.audit.jsonl sidecars — and ONLY
  # the replay JSONL is moved in (the audit sidecar + per-run report stay in the
  # discarded stage, so the set dir holds no non-replay JSONL the validity gate /
  # loader would trip on).
  local stage_dir
  stage_dir="$(mktemp -d "$set_dir/.ailibi-corpus-stage-XXXXXX")"
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

  # Portable mkdir mutex with DEAD-OWNER detection: the holder records its PID; a
  # waiter that finds the lock owned by a dead process marks the run failed (the
  # half-written MANIFEST is unsafe to freeze) and gives up. Returns non-zero when
  # the lock was NOT acquired — callers must not enter the critical section then.
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
    printf '%s' "$BASHPID" >"$lockdir/owner"
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

  # Rebuild the derived eval report (roles ground truth) from the recorded replays.
  echo "Rebuilding eval report for $set_name ..."
  uv run python "$REPO_ROOT/scripts/build_sample_report.py" --sample-dir "$set_dir"

  # Write the committed by-game splits.json.
  echo "Writing splits.json for $set_name ..."
  write_splits "$set_name" "$set_dir"

  # FREEZE: append the explicit FROZEN line naming the git SHA (last, after every
  # per-seed MANIFEST update, so the freeze line survives the final render).
  freeze_manifest "$manifest" "$set_name" "$git_sha" "$refreshed_at"
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
