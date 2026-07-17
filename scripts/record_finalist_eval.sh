#!/usr/bin/env bash
#
# Task 17.14 — the operator recording leg for the real-LLM finalist eval.
#
# One command: records BOTH finalists (utility-es, policy-es) at the baseline-5
# real Featherless substrate, 50 seeds each (9p2i), into an in-repo staging dir
# so the raw replays can be pushed to the PR branch for scoring. This is a
# TEMPORARY transport tool — the session that scores the run removes this script
# and the raw recordings before the PR merges (raw recordings never land on main;
# audits/audit-phase-15-pause.md convention). Only the assembled measurement
# (training/reports/results-finalist-eval.jsonl) is committed to main.
#
# Usage (from the repo root, with the branch checked out):
#     export FEATHERLESS_API_KEY=...
#     bash scripts/record_finalist_eval.sh
#
# It is RESUMABLE: a seed whose replay already has a game_over record is skipped,
# so a re-run continues where a crash left off. Wall-clock ~15 h (the two
# finalists record as 2 parallel Featherless workers — the plan's 2-unit cap).
# The Featherless client retries 429/5xx internally; this script adds per-seed
# crash-retry (AILIBI_SEED_MAX_ATTEMPTS, default 8) on top.
#
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

STAGE_ROOT="${AILIBI_FINALIST_STAGE:-$REPO_ROOT/training/reports/_finalist_eval_raw}"
FINALISTS=(utility-es policy-es)
NUM_SEEDS="${AILIBI_FINALIST_NUM_SEEDS:-50}"   # seeds 0..NUM_SEEDS-1
MAX_ATTEMPTS="${AILIBI_SEED_MAX_ATTEMPTS:-8}"

# --- substrate pins (baseline 5) --------------------------------------------
if [[ -z "${FEATHERLESS_API_KEY:-}" ]]; then
  echo "Error: FEATHERLESS_API_KEY must be set for the real-LLM finalist eval." >&2
  exit 1
fi
export AILIBI_LLM_PROVIDER=featherless
export AILIBI_PROMPT_SET=qwen3_6_27b
export AILIBI_SEED_MAX_ATTEMPTS="$MAX_ATTEMPTS"
if [[ -n "${AILIBI_ABSENCE_PRIOR:-}" ]]; then
  echo "Error: unset AILIBI_ABSENCE_PRIOR — baseline 5 records it at its stay-OFF." >&2
  exit 1
fi
for m in AILIBI_LLM_MEETING_MODEL AILIBI_LLM_TRIGGER_MODEL; do
  v="$(eval "printf '%s' \"\${$m:-}\"")"
  if [[ -n "$v" && "$v" != "Qwen/Qwen3.6-27B" ]]; then
    echo "Error: $m='$v' would record off the baseline-5 model." >&2
    exit 1
  fi
done

# A replay is "complete" if it carries a game_over record — the resume marker.
is_complete() {
  uv run python - "$1" <<'PY' 2>/dev/null
import sys
from pathlib import Path
from orchestrator.replay import read_game_outcome
try:
    sys.exit(0 if read_game_outcome(Path(sys.argv[1])) is not None else 1)
except Exception:
    sys.exit(1)
PY
}

# Seconds -> compact "Hh MMm" / "MMm SSs" for per-seed timing + ETA.
fmt_dur() {
  local s="$1"
  if ((s >= 3600)); then
    printf '%dh%02dm' $((s / 3600)) $(((s % 3600) / 60))
  else
    printf '%dm%02ds' $((s / 60)) $((s % 60))
  fi
}

record_finalist() {
  local entrant="$1"
  local dir="$STAGE_ROOT/$entrant"
  mkdir -p "$dir"
  # The roster sidecar the scorers need (the recorder does not write it).
  printf '{"num_impostors": 2, "num_players": 9, "tasks_per_crewmate": 2}\n' \
    >"$dir/roster.json"
  local last=$((NUM_SEEDS - 1))
  # Running stats for the ETA: average wall-time over seeds recorded THIS run
  # (skipped/resumed seeds cost ~0 and are excluded from the average).
  local completed=0 recorded_count=0 recorded_secs=0
  for seed in $(seq 0 "$last"); do
    local replay="$dir/replay-seed-$seed.jsonl"
    if [[ -f "$replay" ]] && is_complete "$replay"; then
      completed=$((completed + 1))
      echo "[$entrant] seed $seed already complete (resume) | $completed/$NUM_SEEDS"
      continue
    fi
    local ok=0 t0 dt
    t0=$(date +%s)
    for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
      echo "[$entrant] seed $seed recording (attempt $attempt/$MAX_ATTEMPTS) $(date -u +%H:%M:%S)Z"
      if uv run python scripts/run_tournament.py \
          --candidate-artifact "training/artifacts/impostor/$entrant" \
          --start-seed "$seed" --num-games 1 \
          --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 \
          --output-dir "$dir" --force >/dev/null 2>&1 \
         && is_complete "$replay"; then
        ok=1
        break
      fi
      sleep $((attempt * 15))
    done
    dt=$(($(date +%s) - t0))
    # Drop the audit sidecar (huge, gitignored, unused by scoring) as we go.
    rm -f "$dir/replay-seed-$seed.audit.jsonl"
    if [[ "$ok" -eq 1 ]]; then
      completed=$((completed + 1))
      recorded_count=$((recorded_count + 1))
      recorded_secs=$((recorded_secs + dt))
      local avg=$((recorded_secs / recorded_count))
      local eta=$((avg * (NUM_SEEDS - completed)))
      echo "[$entrant] seed $seed done in $(fmt_dur "$dt") | $completed/$NUM_SEEDS | avg $(fmt_dur "$avg")/seed | ETA ~$(fmt_dur "$eta")"
    else
      echo "[$entrant] seed $seed FAILED after $MAX_ATTEMPTS attempts — re-run to retry." >&2
    fi
  done
  echo "[$entrant] done ($(ls "$dir"/replay-seed-*.jsonl 2>/dev/null | wc -l) replays)"
}

# --- single-instance lock ----------------------------------------------------
# Only ONE recording run may be active: two instances would --force the same
# replay-seed files and quadruple the Featherless concurrency, corrupting bytes
# and 429-storming every game. Portable mkdir lock (atomic on macOS + Linux),
# kept OUTSIDE the staged tree so it never gets committed.
LOCK="${TMPDIR:-/tmp}/ailibi_finalist_eval.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  if [[ -f "$LOCK/pid" ]] && kill -0 "$(cat "$LOCK/pid" 2>/dev/null)" 2>/dev/null; then
    echo "Error: another finalist recording run is active (PID $(cat "$LOCK/pid"))." >&2
    echo "       Stop it first: pkill -f record_finalist_eval.sh; pkill -f run_tournament" >&2
    exit 1
  fi
  rm -rf "$LOCK"; mkdir "$LOCK"   # reclaim a stale lock (previous run died)
fi
echo "$$" >"$LOCK/pid"
_cleanup() {
  echo "" >&2
  echo "Stopping workers and releasing lock…" >&2
  # Kill this run's whole process tree so no uv/python game is orphaned.
  pkill -P $$ 2>/dev/null
  rm -rf "$LOCK"
}
trap '_cleanup' EXIT
trap 'exit 130' INT TERM

echo "Recording finalists ${FINALISTS[*]} -> $STAGE_ROOT"
echo "Substrate: Qwen/Qwen3.6-27B, qwen3_6_27b v3, \$0; 2 parallel workers; resumable."

# Two parallel workers (one per finalist) — the documented 2-unit Featherless cap.
# Stagger the second start so their ballot phases are less likely to collide.
record_finalist "${FINALISTS[0]}" &
pid0=$!
sleep 20
record_finalist "${FINALISTS[1]}" &
pid1=$!
wait "$pid0"; wait "$pid1"

echo ""
echo "=== recording complete ==="
for entrant in "${FINALISTS[@]}"; do
  n="$(ls "$STAGE_ROOT/$entrant"/replay-seed-*.jsonl 2>/dev/null | wc -l)"
  echo "  $entrant: $n / $NUM_SEEDS replays in $STAGE_ROOT/$entrant"
done
echo ""
echo "Next: push the raw replays to the PR branch so the session can score them"
echo "(audit sidecars are gitignored; only replay-seed-*.jsonl + roster.json stage):"
echo ""
echo "    git add training/reports/_finalist_eval_raw"
echo "    git commit -m 'wip: raw finalist-eval recordings for scoring (removed before merge)'"
echo "    git push origin claude/phase-17-finalist-eval-e7ekej"
