#!/usr/bin/env bash
#
# verify_samples.sh — CPU-only verification of the replay samples
# (Task 4.17; DESIGN.md §11.4).
#
# Walks every replays/samples/replay-seed-*.jsonl, loads each through
# api.replay_loader.ReplayLoader, and asserts the recorded state-hash chain
# reconstructs byte-identically under the current engine. No API spend — this
# is the free safety net that catches silent drift from an engine change
# before any Phase 5 metric reads a sample and produces a wrong number.
#
# Exits non-zero (and prints the sample id + divergent tick + expected/actual
# hashes) if any sample fails to reconstruct.
#
# Usage: scripts/verify_samples.sh [SAMPLE_DIR]   (default: replays/samples)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

exec uv run python "$SCRIPT_DIR/_verify_samples.py" \
  "${1:-$REPO_ROOT/replays/samples}"
