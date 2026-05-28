#!/usr/bin/env bash
#
# refresh_samples.sh — regenerate the replay samples under replays/samples/
# (Task 4.17; DESIGN.md §9, §11.4).
#
# Wraps scripts/run_tournament.py (real-provider spend) to re-record samples,
# then updates replays/samples/MANIFEST.md and prints total spend. Opt-in only:
# nothing here runs automatically. Three mutually-exclusive modes:
#
#   --full          Re-run all 50 sample seeds          (~$1,    ~3 min)
#   --meetings      Re-run only the meeting-bearing seeds (~$0.10, ~30s)
#   --seeds N,N,N   Re-run a specific comma-separated subset (custom)
#
# Add --dry-run to print the resolved seeds and planned actions without
# touching the API, the samples, or the manifest.
#
# run_tournament.py drives contiguous seed ranges (--start-seed/--num-games),
# not arbitrary sets, so we invoke it once per seed (--num-games 1 --force).
# That keeps run_tournament.py frozen (Task 4.16) while supporting the
# non-contiguous --meetings / --seeds subsets, and each per-seed --force re-run
# truncates only that seed's replay.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Overridable for tests; default to the bundled sample set + its manifest.
SAMPLE_DIR="${AILIBI_SAMPLE_DIR:-$REPO_ROOT/replays/samples}"
MANIFEST="${AILIBI_MANIFEST:-$SAMPLE_DIR/MANIFEST.md}"

usage() {
  cat <<EOF
Usage: $(basename "$0") (--full | --meetings | --seeds N,N,N) [--dry-run]

  --full          Re-run all 50 sample seeds              (~\$1,    ~3 min)
  --meetings      Re-run only the meeting-bearing seeds   (~\$0.10, ~30s)
  --seeds N,N,N   Re-run a specific comma-separated subset (custom spend)
  --dry-run       Print the resolved seeds + planned actions; touch nothing
  -h, --help      Show this help

Modes are mutually exclusive. The meeting-bearing seeds are derived from
$MANIFEST (rows whose prompt_versions column is populated).
EOF
}

mode=""
dry_run=0
seeds_arg=""

set_mode() {
  if [[ -n "$mode" ]]; then
    echo "Error: --full / --meetings / --seeds are mutually exclusive." >&2
    usage
    exit 1
  fi
  mode="$1"
}

# Derive meeting-bearing seeds from the manifest: a row is meeting-bearing iff
# its prompt_versions cell (column 4) is populated and not the no-meetings
# sentinel. Columns are pipe-delimited: | seed | model | prompt_versions | ...
extract_meeting_seeds() {
  if [[ ! -f "$MANIFEST" ]]; then
    echo "Manifest not found: $MANIFEST (needed to resolve --meetings)." >&2
    return 1
  fi
  awk -F'|' '
    {
      seed = $2; gsub(/^[[:space:]]+|[[:space:]]+$/, "", seed)
      pv   = $4; gsub(/^[[:space:]]+|[[:space:]]+$/, "", pv)
      if (seed ~ /^[0-9]+$/ && pv != "" && pv !~ /^\(none/) print seed
    }
  ' "$MANIFEST" | paste -sd, -
}

# Validate a comma-separated seed list and echo the normalized, de-duplicated
# form. Surrounding whitespace around a seed is tolerated; whitespace *inside* a
# token (e.g. "1 2") is rejected rather than silently collapsed to seed 12.
validate_seeds() {
  local csv="$1" token seen=""
  local -a normalized=()
  IFS=',' read -ra tokens <<<"$csv"
  for token in "${tokens[@]}"; do
    [[ -z "${token//[[:space:]]/}" ]] && continue  # blank (e.g. a trailing comma)
    if [[ ! "$token" =~ ^[[:space:]]*([0-9]+)[[:space:]]*$ ]]; then
      echo "Invalid seed (want a non-negative integer): '$token'" >&2
      return 1
    fi
    token="${BASH_REMATCH[1]}"
    token="$((10#$token))" # canonicalize (01 -> 1) so numeric aliases de-dup
    # De-duplicate (keep first occurrence) so a typo like "22,22" or "1,01"
    # cannot double-spend on the provider or double-count in the cost sum.
    case ",$seen," in
      *",$token,"*) continue ;;
    esac
    seen="${seen:+$seen,}$token"
    normalized+=("$token")
  done
  if [[ ${#normalized[@]} -eq 0 ]]; then
    echo "No seeds provided to --seeds." >&2
    return 1
  fi
  (
    IFS=','
    echo "${normalized[*]}"
  )
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --full) set_mode full ;;
    --meetings) set_mode meetings ;;
    --seeds)
      set_mode seeds
      shift
      seeds_arg="${1:-}"
      if [[ -z "$seeds_arg" ]]; then
        echo "Error: --seeds requires a comma-separated seed list." >&2
        usage
        exit 1
      fi
      ;;
    --dry-run) dry_run=1 ;;
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

if [[ -z "$mode" ]]; then
  echo "Error: pick one mode (--full, --meetings, or --seeds N,N,N)." >&2
  usage
  exit 1
fi

case "$mode" in
  full) seeds_csv="$(seq -s, 0 49)" ;;
  meetings)
    if ! seeds_csv="$(extract_meeting_seeds)"; then
      exit 1
    fi
    if [[ -z "$seeds_csv" ]]; then
      echo "No meeting-bearing seeds found in $MANIFEST." >&2
      exit 1
    fi
    ;;
  seeds)
    if ! seeds_csv="$(validate_seeds "$seeds_arg")"; then
      usage
      exit 1
    fi
    ;;
esac

if [[ "$dry_run" -eq 1 ]]; then
  echo "[dry-run] mode: $mode"
  echo "[dry-run] seeds: $seeds_csv"
  echo "[dry-run] sample dir: $SAMPLE_DIR"
  echo "[dry-run] provider: AILIBI_LLM_PROVIDER=anthropic (forced)"
  echo "[dry-run] meeting model: ${AILIBI_LLM_MEETING_MODEL:-(provider default)}"
  echo "[dry-run] per seed, would run via a temp stage (then move the replay in and update that seed's manifest row):"
  echo "[dry-run]   AILIBI_LLM_PROVIDER=anthropic uv run python scripts/run_tournament.py --start-seed <seed> --num-games 1 --output-dir <stage> --force"
  if [[ "$mode" == "full" ]]; then
    echo "[dry-run] full mode would then remove non-canonical samples (seeds outside 0-49) and prune their manifest rows"
  fi
  echo "[dry-run] manifest: $MANIFEST"
  echo "[dry-run] no API calls made; no files written."
  exit 0
fi

# Real-provider preflight: a refresh spends money, so fail before any call if
# the key is missing. Only the prefix is printed (never the full key).
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "Error: ANTHROPIC_API_KEY must be set for a sample refresh (real-provider spend)." >&2
  exit 1
fi
echo "Using API key prefix: ${ANTHROPIC_API_KEY:0:8}"

# Force the real provider. llm.provider.build_default_client() defaults to the
# FAKE provider whenever AILIBI_LLM_PROVIDER is unset (its documented default so
# CI never hits the network), even when ANTHROPIC_API_KEY is present. Without
# this a refresh run with only the key set would silently re-record
# fake-provider output (zero spend, fake model) over the real samples and
# corrupt MANIFEST provenance + every Phase 5 metric derived from it.
export AILIBI_LLM_PROVIDER=anthropic
echo "Using LLM provider: $AILIBI_LLM_PROVIDER (forced for real-provider refresh)"
echo "Refreshing seeds: $seeds_csv"

# Compute provenance once so every seed in this refresh shares one sha + date.
git_sha="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
refreshed_at="$(date -u +%F)"

# Resolve the meeting model this refresh runs with, so seeds that record no LLM
# call (no meeting) are attributed in MANIFEST to the active model rather than a
# stale directory-derived one. Defaults to the provider's meeting model when
# AILIBI_LLM_MEETING_MODEL is unset.
active_model="${AILIBI_LLM_MEETING_MODEL:-}"
if [[ -z "$active_model" ]]; then
  active_model="$(uv run python -c \
    'from llm.provider import DEFAULT_MEETING_MODEL; print(DEFAULT_MEETING_MODEL)')"
fi
echo "Attributing no-meeting seeds to model: $active_model"

# Stage each per-seed run in a temp dir on the same filesystem as the sample dir
# so the replay can be moved into place atomically, and only after the run
# succeeds. A mid-write provider/schema failure then leaves the live
# replay-seed-N.jsonl and its MANIFEST row untouched (the partial write hit the
# stage, which set -e + the trap discard) -- exactly the stale/partial-sample
# state this workflow exists to prevent. It also keeps replays/samples/ to just
# replay JSONLs: run_balance_eval writes a sibling <stem>.audit.jsonl that stays
# behind in the stage.
stage_dir="$(mktemp -d "$(dirname "$SAMPLE_DIR")/.ailibi-refresh-stage-XXXXXX")"
trap 'rm -rf "$stage_dir"' EXIT

IFS=',' read -ra seed_list <<<"$seeds_csv"
for seed in "${seed_list[@]}"; do
  echo "--- Refreshing seed $seed ---"
  uv run python "$REPO_ROOT/scripts/run_tournament.py" \
    --start-seed "$seed" \
    --num-games 1 \
    --output-dir "$stage_dir" \
    --force
  # Atomic replace on success, THEN sync this seed's manifest row, so the live
  # sample and its provenance never drift. Per-seed (rather than one update
  # after the loop) keeps earlier seeds consistent if a later one fails.
  mv -f "$stage_dir/replay-seed-$seed.jsonl" "$SAMPLE_DIR/replay-seed-$seed.jsonl"
  uv run python "$REPO_ROOT/scripts/_manifest_writer.py" update \
    --seeds "$seed" \
    --git-sha "$git_sha" \
    --refreshed-at "$refreshed_at" \
    --model "$active_model" \
    --sample-dir "$SAMPLE_DIR" \
    --manifest "$MANIFEST"
done

# Full mode = the canonical 0-49 set. All 50 are now regenerated in place, so
# drop any stray non-canonical samples (numeric seed > 49) a prior --seeds run
# left behind, plus their manifest rows. Done only after a successful full regen
# so a mid-run failure never deletes data, and only for seeds outside 0-49 so a
# canonical sample is never removed.
if [[ "$mode" == "full" ]]; then
  for path in "$SAMPLE_DIR"/replay-seed-*.jsonl; do
    [[ -e "$path" ]] || continue
    n="$(basename "$path")"
    n="${n#replay-seed-}"
    n="${n%.jsonl}"
    [[ "$n" =~ ^[0-9]+$ ]] || continue # not a numeric seed file; leave it
    if ((10#$n <= 49)); then
      continue # canonical seed; keep
    fi
    echo "Removing stale non-canonical sample: $(basename "$path") (seed $n outside 0-49)"
    rm -f "$path"
  done
  uv run python "$REPO_ROOT/scripts/_manifest_writer.py" prune \
    --sample-dir "$SAMPLE_DIR" \
    --manifest "$MANIFEST"
fi

total="$(uv run python "$REPO_ROOT/scripts/_manifest_writer.py" sum-cost \
  --seeds "$seeds_csv" --sample-dir "$SAMPLE_DIR")"
echo "Refresh complete. Total spend: \$$total (recorded in $MANIFEST)."
