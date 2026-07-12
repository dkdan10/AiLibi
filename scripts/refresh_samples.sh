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

# Overridable for tests; default to the flat 4p1i sample set + its manifest. Since
# Task 12.12, replays/samples/ is a PARENT of per-set subdirs, so the default
# targets the 4p1i subdir (the old flat-root default's new home) — never the
# parent, which holds no replays directly.
SAMPLE_DIR="${AILIBI_SAMPLE_DIR:-$REPO_ROOT/replays/samples/4p1i}"
MANIFEST="${AILIBI_MANIFEST:-$SAMPLE_DIR/MANIFEST.md}"

# Per-set roster (Task 7.4). Threaded into scripts/run_tournament.py so a refresh
# records each set at its own roster. The defaults reproduce the committed FLAT
# 4p/1i baseline at ONE task per crewmate — NOT run_tournament.py's harness
# default of 2 — so a default refresh re-records replays/samples/4p1i/
# byte-identically (the committed loader re-seeds the flat set at 1 task/crewmate).
# To record the canonical 9p/2i eval set (DESIGN.md §3.5), set these alongside
# AILIBI_SAMPLE_DIR/AILIBI_MANIFEST:
#   AILIBI_NUM_PLAYERS=9 AILIBI_NUM_IMPOSTORS=2 AILIBI_TASKS_PER_CREWMATE=2 \
#   AILIBI_SAMPLE_DIR=replays/samples/9p2i AILIBI_MANIFEST=replays/samples/9p2i/MANIFEST.md
NUM_PLAYERS="${AILIBI_NUM_PLAYERS:-4}"
NUM_IMPOSTORS="${AILIBI_NUM_IMPOSTORS:-1}"
TASKS_PER_CREWMATE="${AILIBI_TASKS_PER_CREWMATE:-1}"

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

# Provider-aware preflight for AILIBI_LLM_PROVIDER=ollama (Task 7.7). A local
# Ollama refresh spends no money, but it must still fail loud BEFORE any
# generate call if the local server is down or the configured model was never
# pulled (AGENTS.md "no silent fallbacks") -- otherwise run_tournament.py would
# crash mid-record. Pings the server's /api/tags endpoint for reachability and
# confirms $2 is in the pulled-model list, printing an actionable remediation
# ("ollama serve" / "ollama pull <model>") on failure. Uses python3 -- already a
# hard dependency (the manifest/roster helpers run under it) -- rather than curl,
# so the check is portable across macOS/Linux without assuming curl is installed.
ollama_preflight() {
  local host="$1" model="$2"
  python3 - "$host" "$model" <<'PY'
import json
import sys
import urllib.error
import urllib.request

host, model = sys.argv[1], sys.argv[2]
base = host if host.startswith(("http://", "https://")) else "http://" + host
tags_url = base.rstrip("/") + "/api/tags"
try:
    with urllib.request.urlopen(tags_url, timeout=5) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
except (urllib.error.URLError, OSError) as exc:
    sys.stderr.write(
        f"Error: Ollama server unreachable at {tags_url} ({exc}). "
        f"Start it with `ollama serve` "
        f"(set AILIBI_OLLAMA_HOST if it is not localhost:11434).\n"
    )
    raise SystemExit(1)
except ValueError as exc:  # malformed JSON body
    sys.stderr.write(f"Error: Ollama {tags_url} returned non-JSON ({exc}).\n")
    raise SystemExit(1)
names = {str(entry.get("name", "")) for entry in payload.get("models", [])}
if model not in names:
    sys.stderr.write(
        f"Error: Ollama model {model!r} is not pulled on {base} "
        f"(pulled models: {sorted(names)}). Pull it with `ollama pull {model}`.\n"
    )
    raise SystemExit(1)
PY
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

# Validate the roster env as positive integers up front (Task 7.4), for BOTH the
# dry-run and real paths, and canonicalize to base 10. Without this a typo like
# AILIBI_NUM_PLAYERS=7p makes the later `[[ -ne ]]` arithmetic error out but still
# exit 0 with a misleading plan, and a leading-zero value like 08 is parsed as
# octal (`value too great for base`) — which would likewise skip the positivity
# check AND the flat-baseline guard below. Normalize with 10# (as seed parsing
# does) so every later `-lt`/`-ne` and every threaded flag uses a clean base-10
# integer. Fail loud here so the per-set routing the dry-run reports is trustworthy.
for _roster_var in NUM_PLAYERS NUM_IMPOSTORS TASKS_PER_CREWMATE; do
  _roster_val="${!_roster_var}"
  if [[ ! "$_roster_val" =~ ^[0-9]+$ ]]; then
    echo "Error: AILIBI_$_roster_var must be a positive integer, got '$_roster_val'." >&2
    exit 1
  fi
  _roster_val="$((10#$_roster_val))" # 08 -> 8, 007 -> 7 (base 10, not octal)
  if [[ "$_roster_val" -lt 1 ]]; then
    echo "Error: AILIBI_$_roster_var must be a positive integer, got '${!_roster_var}'." >&2
    exit 1
  fi
  printf -v "$_roster_var" '%s' "$_roster_val" # write the normalized value back
done

# Task 12.12 removed the flat-root special-casing: every set is now a named subdir
# under replays/samples/, so there is no privileged root directory a misconfigured
# refresh could clobber. The roster is governed by the target dir's roster.json
# (written + validated below by _manifest_writer.py roster), not by the dir's name,
# so a wrong-roster refresh fails loud at that gate (or, for an existing committed
# set, on the descriptor-disagreement check) rather than needing a path guard here.

# Resolve the LLM provider for this refresh (Task 7.7). Historically this script
# FORCED anthropic, overriding the ambient AILIBI_LLM_PROVIDER entirely so a
# refresh recorded REAL samples regardless of the shell (the test suite pins
# AILIBI_LLM_PROVIDER=fake; eval/dev sandboxes pin anthropic). It now
# ADDITIONALLY honors an explicit `ollama` so a free local run is possible (Task
# 7.8). Mirror llm.provider.build_default_client()'s lower-casing. Resolution:
#   ollama                         -> ollama (explicit local provider)
#   anthropic | fake | unset/empty -> anthropic (the real default; `fake` is the
#                                     test/CI convention and a refresh records
#                                     REAL samples, so it maps to the historical
#                                     forced default rather than recording fake)
#   anything else                  -> fail loud (a typo must not silently select a
#                                     provider the user did not intend, AGENTS.md)
# The resolved provider is echoed (dry-run + real path) and EXPORTED below, so it
# is never silent and never falls through to build_default_client()'s fake default.
#   featherless                    -> featherless (hosted flat-rate provider, Task
#                                     14.7 / 14.12 baseline re-record; $0
#                                     provider-keyed cost, key required, the locked
#                                     Qwen/Qwen3.6-27B model + qwen3_32b prompt set
#                                     exported by the operator — see the hint in
#                                     tasks/phase-14.md Task 14.12. All five
#                                     substrate levers are unconditionally ON —
#                                     the four Phase-13.5 levers since Task 14.9,
#                                     the Task-14.10 evidence_quality_lift lever
#                                     since the 14.12 close — so no flag export is
#                                     needed.)
DEFAULT_OLLAMA_HOST="localhost:11434"
DEFAULT_OLLAMA_MODEL="qwen3.5:9b"
# The locked production model (Task 16.2, audits/audit-phase-16-model-lock.md,
# locked 2026-07-12); mirrors llm.featherless_client.DEFAULT_FEATHERLESS_MODEL.
# Used for the no-meeting-seed MANIFEST attribution so a Featherless refresh
# attributes those rows to the model it actually ran with, not the
# anthropic/ollama default.
DEFAULT_FEATHERLESS_MODEL="Qwen/Qwen3.6-27B"
PROVIDER="$(printf '%s' "${AILIBI_LLM_PROVIDER:-anthropic}" | tr '[:upper:]' '[:lower:]')"
case "$PROVIDER" in
  ollama) ;;
  featherless) ;;
  anthropic | fake) PROVIDER="anthropic" ;;
  *)
    echo "Error: unknown AILIBI_LLM_PROVIDER='$PROVIDER'; expected 'anthropic', 'ollama', or 'featherless'." >&2
    exit 1
    ;;
esac
# Ollama target host + model the preflight checks (and the run uses): mirror
# build_default_client()'s defaults so the preflight cannot validate a different
# model than the tournament records with.
OLLAMA_HOST="${AILIBI_OLLAMA_HOST:-$DEFAULT_OLLAMA_HOST}"
OLLAMA_MODEL="${AILIBI_LLM_MEETING_MODEL:-$DEFAULT_OLLAMA_MODEL}"

# Seed-level parallelism (Task 14.12). The hosted Featherless plan permits 4
# concurrent inference units and a 32B request consumes 2 of them, so TWO seed
# workers saturate the plan without exceeding it. Each worker records exactly one
# seed at a time and pulls the NEXT available seed from a shared queue (a
# lock-guarded claim counter), so a fast seed's worker immediately starts the next
# unclaimed seed rather than idling — the "next available seed in queue" model.
# This is the DEFAULT for Featherless refreshes; local Ollama (a single-GPU model
# server) and metered Anthropic stay sequential (1 worker), where seed
# parallelism thrashes the GPU or multiplies the metered burst. Overridable for
# any provider via AILIBI_REFRESH_WORKERS (a positive integer) — an operator who
# knows their backend can absorb more (or wants a Featherless run pinned to 1 for
# clean per-seed latency) sets it explicitly; the value is never silently
# derived (AGENTS.md "no silent fallbacks").
if [[ "$PROVIDER" == "featherless" ]]; then
  REFRESH_WORKERS="${AILIBI_REFRESH_WORKERS:-2}"
else
  REFRESH_WORKERS="${AILIBI_REFRESH_WORKERS:-1}"
fi
if [[ ! "$REFRESH_WORKERS" =~ ^[0-9]+$ ]] || [[ "$((10#$REFRESH_WORKERS))" -lt 1 ]]; then
  echo "Error: AILIBI_REFRESH_WORKERS must be a positive integer, got '$REFRESH_WORKERS'." >&2
  exit 1
fi
REFRESH_WORKERS="$((10#$REFRESH_WORKERS))"

# Per-seed crash-retry budget (Task 14.12). A game aborts on a TRANSPORT-level
# error (httpx.ConnectError / read timeout) that the client's HTTP-status retry
# (429/5xx) does not cover -- a transient blip that a re-run clears. Over a
# multi-hour HOSTED Featherless run these are near-inevitable, so retry a crashed
# seed a few times before failing loud. Local Ollama / metered Anthropic default
# to 1 attempt (a crash there is a real, fail-fast error, not a network blip).
# Overridable via AILIBI_SEED_MAX_ATTEMPTS. A recorded parse/schema failure is
# NOT a crash (it lands as a FailedCallReplayEntry and the game continues), so
# this budget only ever spends on genuine transport/unhandled errors.
if [[ "$PROVIDER" == "featherless" ]]; then
  SEED_MAX_ATTEMPTS="${AILIBI_SEED_MAX_ATTEMPTS:-4}"
else
  SEED_MAX_ATTEMPTS="${AILIBI_SEED_MAX_ATTEMPTS:-1}"
fi
if [[ ! "$SEED_MAX_ATTEMPTS" =~ ^[0-9]+$ ]] || [[ "$((10#$SEED_MAX_ATTEMPTS))" -lt 1 ]]; then
  echo "Error: AILIBI_SEED_MAX_ATTEMPTS must be a positive integer, got '$SEED_MAX_ATTEMPTS'." >&2
  exit 1
fi
SEED_MAX_ATTEMPTS="$((10#$SEED_MAX_ATTEMPTS))"

if [[ "$dry_run" -eq 1 ]]; then
  echo "[dry-run] mode: $mode"
  echo "[dry-run] seeds: $seeds_csv"
  echo "[dry-run] roster: num_players=$NUM_PLAYERS num_impostors=$NUM_IMPOSTORS tasks_per_crewmate=$TASKS_PER_CREWMATE"
  # Every set is a named subdir (Task 12.12), so the refresh always writes an
  # explicit roster.json for its target (mirrors _manifest_writer.ensure_roster_descriptor;
  # fails loud if an existing one disagrees). The committed flat 4p1i baseline
  # ships descriptor-less and is not re-recorded.
  echo "[dry-run] roster descriptor: would ensure $SAMPLE_DIR/roster.json = {num_players: $NUM_PLAYERS, num_impostors: $NUM_IMPOSTORS, tasks_per_crewmate: $TASKS_PER_CREWMATE} (fails loud if an existing one disagrees)"
  echo "[dry-run] sample dir: $SAMPLE_DIR"
  # Provider + the preflight that WOULD run on the real path (Task 7.7). Honors
  # AILIBI_LLM_PROVIDER (anthropic|ollama, default anthropic); the dry-run only
  # DESCRIBES the preflight -- it makes no network call (see the "no API calls"
  # line below).
  echo "[dry-run] provider: $PROVIDER"
  if [[ "$PROVIDER" == "ollama" ]]; then
    echo "[dry-run] preflight: would ping http://$OLLAMA_HOST/api/tags for reachability and confirm model $OLLAMA_MODEL is pulled"
  elif [[ "$PROVIDER" == "featherless" ]]; then
    echo "[dry-run] preflight: would require FEATHERLESS_API_KEY (hosted run; \$0 provider-keyed cost)"
  else
    echo "[dry-run] preflight: would require ANTHROPIC_API_KEY (real-provider spend)"
  fi
  echo "[dry-run] meeting model: ${AILIBI_LLM_MEETING_MODEL:-(provider default)}"
  # Provenance the recorded replay self-describes (Task 14.7): the prompt set is
  # read from the ambient env by the game (AILIBI_PROMPT_SET) and the substrate
  # levers are stamped into each replay's game_over record + the MANIFEST flags
  # column (all five levers are unconditionally ON — the four Phase-13.5 levers
  # since Task 14.9, the Task-14.10 evidence_quality_lift lever since the 14.12
  # close — so there are NO substrate env vars to export). Echo the config so the
  # substrate is never silent (AGENTS.md "no silent fallbacks").
  echo "[dry-run] prompt set: ${AILIBI_PROMPT_SET:-(default qwen3_5_9b)}"
  echo "[dry-run] substrate flags: all five levers ON (unconditional; 13.5 since Task 14.9, evidence_quality_lift since the 14.12 close)"
  if [[ "$REFRESH_WORKERS" -gt 1 ]]; then
    echo "[dry-run] seed workers: $REFRESH_WORKERS parallel (each records one seed, then pulls the next available seed from the queue; Featherless: 2 units per 32B request → 4-unit cap)"
  else
    echo "[dry-run] seed workers: 1 (sequential)"
  fi
  echo "[dry-run] seed crash-retry: up to $SEED_MAX_ATTEMPTS attempt(s) per seed on a transport/crash error (recorded parse failures are non-fatal)"
  echo "[dry-run] per seed, would run via a temp stage (then move the replay in and update that seed's manifest row):"
  echo "[dry-run]   AILIBI_LLM_PROVIDER=$PROVIDER uv run python scripts/run_tournament.py --start-seed <seed> --num-games 1 --output-dir <stage> --num-players $NUM_PLAYERS --num-impostors $NUM_IMPOSTORS --tasks-per-crewmate $TASKS_PER_CREWMATE --force"
  if [[ "$mode" == "full" ]]; then
    echo "[dry-run] full mode would then remove non-canonical samples (seeds outside 0-49 and zero-padded aliases like replay-seed-01.jsonl) and prune their manifest rows"
  fi
  echo "[dry-run] manifest: $MANIFEST"
  echo "[dry-run] eval report: would rebuild $SAMPLE_DIR/tournament-eval-report.json from the refreshed replays (scripts/build_sample_report.py; \$0, no provider)"
  echo "[dry-run] no API calls made; no files written."
  exit 0
fi

# Provider-aware preflight (Task 7.7): fail BEFORE any provider call (no spend,
# no partial record) when the selected provider cannot serve the refresh.
#   anthropic -> the API key must be set (a refresh spends money); only the
#                prefix is printed, never the full key.
#   ollama    -> the local server must be reachable AND the configured model
#                must be pulled (ollama_preflight, above) -- $0 spend, but a
#                missing server/model would otherwise crash mid-record.
if [[ "$PROVIDER" == "ollama" ]]; then
  if ! ollama_preflight "$OLLAMA_HOST" "$OLLAMA_MODEL"; then
    exit 1
  fi
  echo "Ollama preflight OK: $OLLAMA_HOST reachable, model $OLLAMA_MODEL present."
elif [[ "$PROVIDER" == "featherless" ]]; then
  # Featherless is a hosted flat-rate provider ($0 provider-keyed cost, Task
  # 14.7), but the key must still be set BEFORE any call so the run fails loud
  # here instead of crashing mid-record (mirrors build_default_client's fail-loud
  # on a missing FEATHERLESS_API_KEY). Only the prefix is printed, never the key.
  if [[ -z "${FEATHERLESS_API_KEY:-}" ]]; then
    echo "Error: FEATHERLESS_API_KEY must be set for a featherless sample refresh." >&2
    exit 1
  fi
  echo "Using Featherless API key prefix: ${FEATHERLESS_API_KEY:0:8}"
  # Task 14.7 / 14.12: refresh_samples.sh records the CANONICAL baseline into
  # replays/samples/, and the only sanctioned Featherless baseline is the
  # 14.6-locked prompt set qwen3_32b. The substrate levers are ALL unconditionally
  # ON (the four Phase-13.5 levers since Task 14.9, the Task-14.10
  # evidence_quality_lift lever since the 14.12 close), so they need no export and
  # cannot be mis-set — the guard only pins the prompt set. The game reads the
  # prompt set from the ambient env; if it is unset the run would SILENTLY record
  # the wrong substrate (the default 9B set) and only reveal it in the MANIFEST
  # afterward, wasting the whole (multi-hour) spend. Fail loud HERE, before any
  # seed is staged (AGENTS.md "no silent fallbacks"). A future re-lock of the
  # baseline updates REQUIRED_PROMPT_SET to match tasks/phase-14.md §14.6.
  REQUIRED_PROMPT_SET="qwen3_32b"
  if [[ "${AILIBI_PROMPT_SET:-}" != "$REQUIRED_PROMPT_SET" ]]; then
    echo "Error: a featherless refresh must run the locked substrate (Task 14.6)." >&2
    echo "       Export the locked prompt set before re-running; nothing was staged:" >&2
    echo "  - AILIBI_PROMPT_SET must be '$REQUIRED_PROMPT_SET' (got '${AILIBI_PROMPT_SET:-<unset>}')" >&2
    exit 1
  fi
  echo "Locked substrate OK: AILIBI_PROMPT_SET=$REQUIRED_PROMPT_SET (all five levers unconditionally ON)."
else
  if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "Error: ANTHROPIC_API_KEY must be set for an anthropic sample refresh (real-provider spend)." >&2
    exit 1
  fi
  echo "Using API key prefix: ${ANTHROPIC_API_KEY:0:8}"
fi

# Create the target set directory before any spend (Task 7.4). A per-set refresh
# (e.g. AILIBI_SAMPLE_DIR=replays/samples/9p2i) may point at a brand-new subdir;
# without this the per-seed `mv` into $SAMPLE_DIR below would fail AFTER a
# real-provider run had already spent. Done after the API-key preflight so a
# dry-run still touches nothing and a missing-key run still fails first; it also
# guarantees the staging dir's parent (dirname "$SAMPLE_DIR") exists. Idempotent.
mkdir -p "$SAMPLE_DIR"

# Ensure the per-set roster descriptor is consistent with the requested roster
# BEFORE spending (Task 7.4). The loader reconstructs a non-default (multi-impostor
# / multi-task) set only from roster.json, so without it the freshly generated
# replays would fail the determinism check AFTER the money is spent. This writes
# the sidecar for a non-default set, no-ops for the flat 4p/1i default (no
# sidecar), and fails loud (set -e aborts before any provider call) if an existing
# descriptor disagrees with the requested roster.
uv run python "$REPO_ROOT/scripts/_manifest_writer.py" roster \
  --sample-dir "$SAMPLE_DIR" \
  --num-players "$NUM_PLAYERS" \
  --num-impostors "$NUM_IMPOSTORS" \
  --tasks-per-crewmate "$TASKS_PER_CREWMATE"

# Export the RESOLVED provider so run_tournament.py records on it. This is the
# critical guard against silent fake recording: llm.provider.build_default_client()
# defaults to the FAKE provider whenever AILIBI_LLM_PROVIDER is unset (its
# documented default so CI never hits the network), even when ANTHROPIC_API_KEY
# is present. Without an explicit export a refresh that left the var unset would
# silently re-record fake-provider output (zero spend, fake model) over the real
# samples and corrupt MANIFEST provenance + every Phase 5 metric derived from it.
# $PROVIDER is anthropic by default (and only ever anthropic|ollama -- the case
# guard above rejected fake/unknown), so this still never selects fake.
export AILIBI_LLM_PROVIDER="$PROVIDER"
echo "Using LLM provider: $AILIBI_LLM_PROVIDER (real-provider refresh)"
echo "Refreshing seeds: $seeds_csv"

# Compute provenance once so every seed in this refresh shares one sha + date.
git_sha="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
refreshed_at="$(date -u +%F)"

# Resolve the meeting model this refresh runs with, so seeds that record no LLM
# call (no meeting) are attributed in MANIFEST to the active model rather than a
# stale directory-derived one. Defaults to the provider's meeting model when
# AILIBI_LLM_MEETING_MODEL is unset -- which is PROVIDER-SPECIFIC: anthropic's is
# DEFAULT_MEETING_MODEL (Sonnet), ollama's is the local DEFAULT_OLLAMA_MODEL.
# Attributing an ollama no-meeting seed to Sonnet would misrecord provenance.
active_model="${AILIBI_LLM_MEETING_MODEL:-}"
if [[ -z "$active_model" ]]; then
  if [[ "$PROVIDER" == "ollama" ]]; then
    active_model="$DEFAULT_OLLAMA_MODEL"
  elif [[ "$PROVIDER" == "featherless" ]]; then
    active_model="$DEFAULT_FEATHERLESS_MODEL"
  else
    active_model="$(uv run python -c \
      'from llm.provider import DEFAULT_MEETING_MODEL; print(DEFAULT_MEETING_MODEL)')"
  fi
fi
echo "Attributing no-meeting seeds to model: $active_model"
# Echo the substrate provenance the recorded replays self-stamp (Task 14.7), so
# the operator can confirm the locked tuple is in effect and the substrate is
# never silent (AGENTS.md "no silent fallbacks"). The game reads the prompt set
# from the ambient env; the substrate levers (the four Phase-13.5 levers,
# unconditionally ON since Task 14.9) are stamped into each replay's game_over
# record + the MANIFEST flags column; this script does not set them.
echo "Prompt set: ${AILIBI_PROMPT_SET:-(default qwen3_5_9b)}"
echo "Substrate flags: all five levers ON (unconditional; 13.5 since Task 14.9, evidence_quality_lift since the 14.12 close)"

# Stage each per-seed run in a temp dir on the same filesystem as the sample dir
# so the replay can be moved into place atomically, and only after the run
# succeeds. A mid-write provider/schema failure then leaves the live
# replay-seed-N.jsonl and its MANIFEST row untouched (the partial write hit the
# stage, which the trap discards) -- exactly the stale/partial-sample state this
# workflow exists to prevent. Each seed gets its OWN sub-stage (mktemp -d inside
# $stage_dir), so parallel workers never collide on run_tournament's per-run
# tournament-eval-report.json / <stem>.audit.jsonl sidecars.
stage_dir="$(mktemp -d "$(dirname "$SAMPLE_DIR")/.ailibi-refresh-stage-XXXXXX")"
trap 'rm -rf "$stage_dir"' EXIT

IFS=',' read -ra seed_list <<<"$seeds_csv"
total_seeds="${#seed_list[@]}"
refresh_start="$(date +%s)"

# Shared cross-worker state (Task 14.12 parallel seed workers). Files on the
# stage filesystem, mutated only under a portable mkdir-based lock so two workers
# never corrupt MANIFEST.md (a read-modify-write) or garble the progress stream.
# .next_idx is the claim counter (the queue cursor); .failed is the fail-loud
# sentinel; .state/{completed,meetings} back the live tally + ETA.
mkdir -p "$stage_dir/.state"
printf '0' >"$stage_dir/.next_idx"
printf '0' >"$stage_dir/.state/completed"
printf '0' >"$stage_dir/.state/meetings"
_lockdir="$stage_dir/.lock"
# Portable mkdir mutex with DEAD-OWNER detection (PR #218 Codex review). A mkdir
# lock is not auto-released when its holder dies, so a worker SIGKILLed/OOMed
# mid-critical-section (e.g. during the lock-held MANIFEST update) would leave the
# lock held forever: every other worker would spin here, and the parent -- blocked
# in `wait` on those stuck workers -- would HANG instead of failing loud. Guard
# it: the holder records its PID in the lock; a waiter that finds the lock owned
# by a process that no longer exists marks the refresh failed (the half-written
# MANIFEST is unsafe to canonicalize) and gives up, so the pool tears down and the
# `.failed` check fails loud. A waiter also bails the instant any worker flags a
# failure. Returns non-zero when the lock was NOT acquired -- callers must not
# enter the critical section on a non-zero return.
_acquire_lock() {
  local owner
  # Give up the moment any worker has flagged a failure -- even if the lock is
  # free right now -- so a doomed baseline stops touching MANIFEST.md.
  [[ -e "$stage_dir/.failed" ]] && return 1
  while ! mkdir "$_lockdir" 2>/dev/null; do
    if [[ -e "$stage_dir/.failed" ]]; then
      return 1
    fi
    owner="$(cat "$_lockdir/owner" 2>/dev/null || true)"
    if [[ -n "$owner" ]] && ! kill -0 "$owner" 2>/dev/null; then
      echo "ERROR: refresh lock owner (pid $owner) died holding the lock" \
        "(killed/crashed mid critical section); the baseline is incomplete." >&2
      touch "$stage_dir/.failed"
      return 1
    fi
    sleep 0.1
  done
  printf '%s' "$BASHPID" >"$_lockdir/owner"
  return 0
}
# rm -rf (not rmdir): the lock dir now holds the owner-pid file.
_release_lock() { rm -rf "$_lockdir" 2>/dev/null || true; }

# Atomically claim the next unclaimed seed (the queue). Echoes the seed, or
# nothing when the queue is drained. Lock-guarded so no seed is double-recorded
# (double spend) and none is skipped.
claim_next_seed() {
  local idx
  # A non-zero acquire (a dead lock owner / an already-flagged failure) echoes no
  # seed, so the worker drains as if the queue were empty and the .failed check
  # fails loud.
  _acquire_lock || return 1
  idx="$(cat "$stage_dir/.next_idx")"
  if [[ "$idx" -ge "$total_seeds" ]]; then
    _release_lock
    return 0
  fi
  printf '%s' "$((idx + 1))" >"$stage_dir/.next_idx"
  _release_lock
  printf '%s' "${seed_list[$idx]}"
}

# Record ONE seed end to end: stage the run, atomically move the replay into the
# sample dir, then (serialized) sync its MANIFEST row + the shared tally + a
# progress line. Any failure touches .failed and returns non-zero so the pool
# stops claiming and the script exits non-zero -- the baseline must be COMPLETE or
# not committed (AGENTS.md "no silent fallbacks"; the 4.17 partial-sample guard).
# Always invoked in a `||`/`if` context, so set -e is disabled inside it and the
# explicit checks below are what gate each step.
record_one_seed() {
  local seed="$1" worker="$2"
  local seed_stage seed_start now seed_secs elapsed eta rate completed meetings seed_meeting
  local attempt max_attempts
  max_attempts="$SEED_MAX_ATTEMPTS"
  seed_start="$(date +%s)"
  echo "--- [worker $worker] recording seed $seed ---"
  # Guard the stage mktemp explicitly (PR #218 Codex review): record_one_seed runs
  # with set -e disabled (it is called in a `||` context), so a failed assignment
  # would otherwise leave seed_stage EMPTY and run_tournament would spend provider
  # calls with a bogus --output-dir instead of failing before spend. Mark the seed
  # failed and bail BEFORE the tournament runs.
  if ! seed_stage="$(mktemp -d "$stage_dir/seed-${seed}-XXXXXX")"; then
    echo "ERROR: seed $seed stage mktemp failed (worker $worker; staging fs out" \
      "of space/inodes?); nothing was spent." >&2
    touch "$stage_dir/.failed"
    return 1
  fi
  # Bounded retry on a run_tournament CRASH (non-zero exit): the recorded LLM
  # baseline is a multi-hour hosted run, and a game aborts on a TRANSPORT-level
  # error (httpx.ConnectError / read timeout) that the client's HTTP-status retry
  # (429/5xx) does not cover -- a transient network blip that a re-run clears.
  # A recorded parse/schema failure is NOT a crash (it lands as a
  # FailedCallReplayEntry and the game continues), so only genuine transport /
  # unhandled errors reach here. A PERSISTENT failure (bad key, endpoint down,
  # reproducible crash) exhausts the attempts and fails loud -- resilience to
  # blips, never a silent paper-over (AGENTS.md). --force overwrites the partial
  # stage replay each attempt. Tunable via AILIBI_SEED_MAX_ATTEMPTS.
  attempt=0
  while :; do
    attempt=$((attempt + 1))
    if uv run python "$REPO_ROOT/scripts/run_tournament.py" \
      --start-seed "$seed" \
      --num-games 1 \
      --output-dir "$seed_stage" \
      --num-players "$NUM_PLAYERS" \
      --num-impostors "$NUM_IMPOSTORS" \
      --tasks-per-crewmate "$TASKS_PER_CREWMATE" \
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
  # Atomic replace on success so the live sample never drifts to a partial write.
  if ! mv -f "$seed_stage/replay-seed-$seed.jsonl" \
    "$SAMPLE_DIR/replay-seed-$seed.jsonl"; then
    echo "ERROR: seed $seed replay move failed (worker $worker)." >&2
    touch "$stage_dir/.failed"
    rm -rf "$seed_stage"
    return 1
  fi
  rm -rf "$seed_stage"
  # `meeting_id` appears only in a meeting record, so this guarded grep flags
  # whether the seed reached a meeting without parsing it.
  if grep -q 'meeting_id' "$SAMPLE_DIR/replay-seed-$seed.jsonl"; then
    seed_meeting="yes"
  else
    seed_meeting="no "
  fi
  # Serialize the MANIFEST update + tally bump + progress print: MANIFEST.md is a
  # read-modify-write, and interleaved printf from two workers would garble lines.
  # A non-zero acquire (dead lock owner / already-flagged failure) has set .failed
  # already; the seed's replay is on disk but its MANIFEST row is not synced, and
  # the baseline is rejected as INCOMPLETE below.
  if ! _acquire_lock; then
    echo "ERROR: seed $seed could not acquire the manifest lock (worker $worker)." >&2
    return 1
  fi
  if ! uv run python "$REPO_ROOT/scripts/_manifest_writer.py" update \
    --seeds "$seed" \
    --git-sha "$git_sha" \
    --refreshed-at "$refreshed_at" \
    --model "$active_model" \
    --sample-dir "$SAMPLE_DIR" \
    --manifest "$MANIFEST"; then
    _release_lock
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
  elapsed=$((now - refresh_start))
  rate=$((meetings * 100 / completed))
  # Throughput-based ETA: elapsed/completed already folds in the worker count, so
  # this stays honest whether 1 or N workers are draining the queue.
  eta=$((elapsed * (total_seeds - completed) / completed))
  printf '    seed %s done in %3ds | meeting: %s | meetings %d/%d (%d%%) | done %d/%d | elapsed %dm%02ds | ETA ~%dm\n' \
    "$seed" "$seed_secs" "$seed_meeting" "$meetings" "$completed" "$rate" \
    "$completed" "$total_seeds" "$((elapsed / 60))" "$((elapsed % 60))" "$((eta / 60))"
  _release_lock
  return 0
}

# One worker: pull the next seed from the queue and record it until the queue is
# drained or any worker has flagged a failure. Returns 0 even on a recorded
# failure -- the .failed sentinel (checked after the pool joins) is the fail-loud
# signal, so the pool tears down cleanly rather than orphaning in-flight workers.
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
  worker_pids=()
  for ((w = 1; w <= REFRESH_WORKERS; w++)); do
    run_worker "$w" &
    worker_pids+=("$!")
  done
  # Join every worker and record ANY non-zero exit as a refresh failure (PR #218
  # Codex review): a worker killed or crashing OUTSIDE record_one_seed's handled
  # path (SIGKILL / OOM after claiming a seed) never writes .failed, so without
  # this a multi-hour baseline could silently canonicalize a mixed old/new set
  # (the skipped seed keeps its stale replay + MANIFEST row). We still wait on the
  # rest of the pool (never `set -e`-abort mid-join), then the .failed check below
  # fails loud. A normally-finishing worker returns 0 (record_one_seed handles its
  # own failures via .failed), so this only fires on an abnormal exit.
  for pid in "${worker_pids[@]}"; do
    if ! wait "$pid"; then
      touch "$stage_dir/.failed"
      echo "ERROR: refresh worker (pid $pid) exited non-zero (killed/crashed" \
        "outside a seed's handled failure path); the baseline is incomplete." >&2
    fi
  done
else
  run_worker 1
fi

if [[ -e "$stage_dir/.failed" ]]; then
  echo "Error: a seed failed during the refresh; the baseline is INCOMPLETE and must NOT be committed." >&2
  echo "       Already-recorded seeds + their MANIFEST rows are preserved on disk; fix the failure and re-run." >&2
  exit 1
fi

# Hydrate the summary from the shared tally the workers accumulated.
meetings_seen="$(cat "$stage_dir/.state/meetings")"

# Full mode = the canonical 0-49 set, now all regenerated in place. Reconcile the
# directory to exactly those canonical files and prune any orphaned manifest
# rows. This drops both stray samples for seeds outside 0-49 (left by a prior
# --seeds run) AND zero-padded aliases like replay-seed-01.jsonl -- which
# ReplayLoader._replay_paths dedups *ahead* of the fresh replay-seed-1.jsonl
# (lexicographically-first filename), so a surviving alias would shadow the
# canonical sample for every API/eval consumer. Run only after a successful full
# regen, so a mid-run failure never deletes data and the canonical sample for
# every kept seed is already on disk.
if [[ "$mode" == "full" ]]; then
  uv run python "$REPO_ROOT/scripts/_manifest_writer.py" canonicalize \
    --seeds "$seeds_csv" \
    --sample-dir "$SAMPLE_DIR" \
    --manifest "$MANIFEST"
fi

total="$(uv run python "$REPO_ROOT/scripts/_manifest_writer.py" sum-cost \
  --seeds "$seeds_csv" --sample-dir "$SAMPLE_DIR")"
refresh_wall=$(($(date +%s) - refresh_start))
echo "Refresh complete in $((refresh_wall / 60))m$((refresh_wall % 60))s: $meetings_seen/$total_seeds seeds reached a meeting (~$((meetings_seen * 100 / total_seeds))%; authoritative meeting_rate is in the eval report)."
echo "Total spend: \$$total (recorded in $MANIFEST)."

# Rebuild the derived eval report from the freshly-recorded replays. The refresh
# above regenerates the replay JSONL + MANIFEST, but tournament-eval-report.json is
# a separate offline build (roles re-seeded from roster.json); without this step a
# refresh leaves a STALE report that still passes check.sh, since the determinism
# gate only verifies replay state_hash reconstruction, never the report. Runs for
# every real mode (full/meetings/seeds) and reads ALL on-disk seeds, so a partial
# refresh still yields a report consistent with the whole committed set. $0, no
# provider call; set -e makes a build failure fail the refresh loudly.
echo "Rebuilding eval report from the refreshed replays ..."
uv run python "$REPO_ROOT/scripts/build_sample_report.py" --sample-dir "$SAMPLE_DIR"

# Regenerate the per-set interestingness rubric (Task 12.2; DESIGN.md §3.1, §7)
# so /eval/rubric stays FRESH after a re-record instead of only banner-guarded
# when stale. The gameplay-facts extractor is pinned to the canonical 9p2i set
# (it reads replays/samples/9p2i + writes facts to a predictable temp path), so
# this runs only when the refresh target IS that set; for any other set the
# producer is a no-op here (the flat 4p1i baseline ships no rubric by design).
# $0, no provider call. The paid replay JSONL + MANIFEST + eval report are
# already written above (preserved on disk), but a regen FAILURE exits non-zero:
# the refresh is not "complete" — and must not be committed — while the rubric
# is stale, so the operator re-runs it rather than shipping a drifted surface.
if [[ "$SAMPLE_DIR" -ef "$REPO_ROOT/replays/samples/9p2i" ]]; then
  echo "Regenerating the per-set interestingness rubric (9p2i) ..."
  # Run from the repo root in a subshell: the extractor reads its hardcoded 9p2i
  # set + writes facts to this predictable temp path (no sys.path bootstrap, so
  # PYTHONPATH=repo root), and rubric_score's lab-artifact write is repo-relative
  # — a stray caller cwd would otherwise drop it or trip the warning. The rubric
  # stamps the set's MANIFEST sha (not git HEAD), so its freshness is independent
  # of cwd/git. The producer then scores those facts and co-locates the rubric.
  _facts_path="${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json"
  if (
    cd "$REPO_ROOT" \
      && PYTHONPATH="$REPO_ROOT" uv run python \
        audits/workflows/extract_gameplay_facts.py >/dev/null \
      && uv run python experiments/lab/rubric_score.py "$_facts_path" \
        --set-dir "$SAMPLE_DIR"
  ); then
    echo "  rubric refreshed: $SAMPLE_DIR/results-rubric-score.json"
  else
    echo "ERROR: rubric regen failed. The re-recorded replays + MANIFEST +" >&2
    echo "  eval report are preserved on disk, but /eval/rubric is now STALE." >&2
    echo "  Re-run the rubric step before committing the refreshed set:" >&2
    echo "    PYTHONPATH=$REPO_ROOT uv run python \\" >&2
    echo "      audits/workflows/extract_gameplay_facts.py >/dev/null \\" >&2
    echo "      && uv run python experiments/lab/rubric_score.py \\" >&2
    echo "        $_facts_path --set-dir $SAMPLE_DIR" >&2
    exit 1
  fi
fi
