#!/usr/bin/env bash
#
# verify_samples.sh — CPU-only verification of the replay samples
# (Task 4.17; DESIGN.md §11.4).
#
# Walks every replay-seed-*.jsonl in ONE per-set sample dir (Task 12.12:
# replays/samples is now a parent of per-set subdirs like 4p1i/ and 9p2i/), loads
# each through api.replay_loader.ReplayLoader, and asserts the recorded state-hash
# chain reconstructs byte-identically under the current engine. No API spend —
# this is the free safety net that catches silent drift from an engine change
# before any Phase 5 metric reads a sample and produces a wrong number.
#
# Exits non-zero (and prints the sample id + divergent tick + expected/actual
# hashes) if any sample fails to reconstruct.
#
# Usage: scripts/verify_samples.sh [SAMPLE_DIR]
#   - with an explicit SAMPLE_DIR, verifies just that set (e.g. replays/samples/9p2i);
#   - with NO argument, verifies EVERY committed set under the samples root. Task
#     14.12 baseline 2 ships BOTH 4p1i and 9p2i, so the documented bare gate
#     `bash scripts/verify_samples.sh` must walk every set -- verifying only the
#     old 4p1i default would silently skip a stale/corrupted 9p2i replay (PR #218
#     Codex review). The samples root defaults to replays/samples and is
#     overridable via AILIBI_SAMPLES_ROOT (used by the wrapper test).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Explicit single-set path: verify exactly it (back-compat).
if [[ "$#" -ge 1 ]]; then
  exec uv run python "$SCRIPT_DIR/_verify_samples.py" "$1"
fi

# No argument: walk every committed set (a subdir holding replay-seed-*.jsonl)
# under the samples root, aggregating the exit status so a drift in ANY set fails
# the gate.
samples_root="${AILIBI_SAMPLES_ROOT:-$REPO_ROOT/replays/samples}"
status=0
found=0
for set_dir in "$samples_root"/*/; do
  compgen -G "${set_dir}replay-seed-*.jsonl" >/dev/null 2>&1 || continue
  found=1
  echo "=== verifying ${set_dir} ==="
  if ! uv run python "$SCRIPT_DIR/_verify_samples.py" "$set_dir"; then
    status=1
  fi
done
if [[ "$found" -eq 0 ]]; then
  echo "No committed sample sets (subdirs with replay-seed-*.jsonl) under ${samples_root}" >&2
  exit 2
fi
exit "$status"
