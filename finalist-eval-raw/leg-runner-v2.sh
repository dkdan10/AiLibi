#!/bin/bash
# Task 18.26 leg runner v2 — v1 + record-time model-purity check:
# a completed game whose provenance contains "(deadline_default)" is deleted
# and marked failed so a later pass re-records it (validity's
# cost_and_provenance_exact demands a pure model set).
# Usage: leg-runner-v2.sh <arm-name> [run_tournament extra args...]
set -uo pipefail

ARM="$1"; shift
ROOT="$HOME/ailibi-campaign-1826"
REPO="/Users/danielkeinan/projects/AiLibi"
OUT="$ROOT/$ARM"
LOG="$ROOT/leg-log-$ARM.jsonl"
mkdir -p "$OUT"
cd "$REPO"

set -a; source "$REPO/.env"; set +a
export AILIBI_LLM_PROVIDER=featherless
export AILIBI_PROMPT_SET=qwen3_6_27b
export AILIBI_SEED_MAX_ATTEMPTS=8
unset AILIBI_IMPOSTOR_ROLL_CALL   # baseline-6 crew-only ruling: must stay unset

complete_and_pure() {
  local f="$1"
  [ -f "$f" ] && grep -q '"game_over"' "$f" && grep -q '"winner"' "$f" && ! grep -q '(deadline_default)' "$f"
}

echo "{\"event\":\"leg-start\",\"arm\":\"$ARM\",\"runner\":\"v2\",\"args\":\"$*\",\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"

for pass in 1 2 3 4; do
  for seed in $(seq 0 49); do
    replay="$OUT/replay-seed-$seed.jsonl"
    if complete_and_pure "$replay"; then continue; fi
    t0=$(date +%s)
    uv run python scripts/run_tournament.py "$@" \
      --start-seed "$seed" --num-games 1 \
      --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 \
      --output-dir "$OUT" --force \
      > "$ROOT/stdout-$ARM-seed-$seed.log" 2>&1
    rc=$?
    t1=$(date +%s)
    if [ $rc -eq 0 ] && grep -q '(deadline_default)' "$replay"; then
      rm -f "$replay"
      rc=99
      echo "{\"event\":\"purity-retry\",\"arm\":\"$ARM\",\"seed\":$seed,\"pass\":$pass,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
    fi
    echo "{\"event\":\"seed-recorded\",\"arm\":\"$ARM\",\"seed\":$seed,\"pass\":$pass,\"rc\":$rc,\"wall_seconds\":$((t1-t0)),\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
    [ $rc -ne 0 ] && sleep 30
  done
  missing=0
  for seed in $(seq 0 49); do
    complete_and_pure "$OUT/replay-seed-$seed.jsonl" || missing=$((missing+1))
  done
  echo "{\"event\":\"pass-done\",\"arm\":\"$ARM\",\"pass\":$pass,\"missing\":$missing,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
  if [ "$missing" -eq 0 ]; then
    echo "{\"event\":\"leg-done\",\"arm\":\"$ARM\",\"complete\":50,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
    exit 0
  fi
  sleep 60
done

echo "{\"event\":\"leg-abort\",\"arm\":\"$ARM\",\"missing\":$missing,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
exit 1
