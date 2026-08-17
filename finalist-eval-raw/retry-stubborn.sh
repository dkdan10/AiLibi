#!/bin/bash
# Task 18.26 — stubborn-seed retry loop (owner decision 2026-07-29: opportunistic,
# idle-slot only). Cycles the two LLM-sampling-variant stuck seeds, keeping every
# impure attempt for forensics. Deterministic stalemates are NOT in scope here.
set -uo pipefail
ROOT="$HOME/ailibi-campaign-1826"
REPO="/Users/danielkeinan/projects/AiLibi"
FORENSICS="$ROOT/forensics"
mkdir -p "$FORENSICS"
cd "$REPO"
set -a; source "$REPO/.env"; set +a
export AILIBI_LLM_PROVIDER=featherless AILIBI_PROMPT_SET=qwen3_6_27b AILIBI_SEED_MAX_ATTEMPTS=8
unset AILIBI_IMPOSTOR_ROLL_CALL
LOG="$ROOT/leg-log-stubborn.jsonl"

attempt_seed() {  # arm seed extra-args...
  local arm="$1" seed="$2"; shift 2
  local out="$ROOT/$arm" replay="$ROOT/$arm/replay-seed-$seed.jsonl"
  if [ -f "$replay" ] && grep -q '"game_over"' "$replay" && grep -q '"winner"' "$replay" && ! grep -q '(deadline_default)' "$replay"; then
    return 0  # already clean
  fi
  local t0=$(date +%s)
  uv run python scripts/run_tournament.py "$@" \
    --start-seed "$seed" --num-games 1 \
    --num-players 9 --num-impostors 2 --tasks-per-crewmate 2 \
    --output-dir "$out" --force > "$ROOT/stdout-$arm-seed-$seed.log" 2>&1
  local rc=$? t1=$(date +%s)
  if [ $rc -eq 0 ] && grep -q '(deadline_default)' "$replay"; then
    mv "$replay" "$FORENSICS/$arm-seed-$seed-$(date -u +%H%M%S).jsonl"
    rc=99
  fi
  echo "{\"event\":\"stubborn-attempt\",\"arm\":\"$arm\",\"seed\":$seed,\"rc\":$rc,\"wall_seconds\":$((t1-t0)),\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
  return $rc
}

for round in 1 2 3 4 5 6; do
  done_count=0
  attempt_seed p18-fsm-comparator 5 --tactical-policy-stamp fsm-default && done_count=$((done_count+1))
  attempt_seed p18-imp-7f73929d 35 --candidate-artifact training/artifacts/coevo/runnerups/run-03-utility-bcanchor/gen-8/7f73929d5b91f4afe67adc1b2ac7ca42bdd3ab1f49ed0393342ab21c7db0985e && done_count=$((done_count+1))
  echo "{\"event\":\"round-done\",\"round\":$round,\"clean\":$done_count,\"at\":\"$(date -u +%FT%TZ)\"}" >> "$LOG"
  [ "$done_count" -eq 2 ] && exit 0
done
exit 1
