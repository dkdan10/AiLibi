#!/bin/bash
# Task 18.26 leg runner — one arm, seeds 0..49, sharded one-seed-per-invocation
# (the 17.14 §6 form; run_tournament.py has no built-in resume, so resume =
# skip seeds whose replay exists and reaches game_over).
# Usage: leg-runner.sh <arm-name> [run_tournament extra args...]
# Launch under `caffeinate -i` so the Mac never idle-sleeps mid-leg.
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

echo "{\"event\":\"leg-start\",\"arm\":\"$ARM\",\"args\":\"$*\",\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"

for pass in 1 2 3; do
  incomplete=0
  for seed in $(seq 0 49); do
    replay="$OUT/replay-seed-$seed.jsonl"
    if [ -f "$replay" ] && grep -q '"game_over"' "$replay" && grep -q '"winner"' "$replay"; then
      continue
    fi
    t0=$(date +%s)
    uv run python scripts/run_tournament.py "$@" \
      --start-seed "$seed" --num-games 1 \
      --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 \
      --output-dir "$OUT" --force \
      > "$ROOT/stdout-$ARM-seed-$seed.log" 2>&1
    rc=$?
    t1=$(date +%s)
    echo "{\"event\":\"seed-recorded\",\"arm\":\"$ARM\",\"seed\":$seed,\"pass\":$pass,\"rc\":$rc,\"wall_seconds\":$((t1-t0)),\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
    if [ $rc -ne 0 ]; then
      incomplete=1
      sleep 30   # brief back-off before the next seed on a provider hiccup
    fi
  done
  # count seeds still missing a completed replay
  missing=0
  for seed in $(seq 0 49); do
    replay="$OUT/replay-seed-$seed.jsonl"
    if ! { [ -f "$replay" ] && grep -q '"game_over"' "$replay" && grep -q '"winner"' "$replay"; }; then
      missing=$((missing+1))
    fi
  done
  echo "{\"event\":\"pass-done\",\"arm\":\"$ARM\",\"pass\":$pass,\"missing\":$missing,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
  if [ "$missing" -eq 0 ]; then
    echo "{\"event\":\"leg-done\",\"arm\":\"$ARM\",\"complete\":50,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
    exit 0
  fi
  [ $incomplete -eq 0 ] && sleep 60
done

echo "{\"event\":\"leg-abort\",\"arm\":\"$ARM\",\"missing\":$missing,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
exit 1
