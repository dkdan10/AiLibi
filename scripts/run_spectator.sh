#!/usr/bin/env bash
# scripts/run_spectator.sh — one-command spectator UI launcher (Task 4.12).
#
# Starts the FastAPI replay backend (port 8000) and the Vite dev frontend
# (port 5173), waits for both to become healthy, opens the browser, and stays
# in the foreground until Ctrl-C — at which point both child processes are
# cleaned up via a trap.
#
# Supported platforms: macOS, Linux. Windows is intentionally unsupported
# (different shell, different process management, different package manager
# idioms; bash on cmd/PowerShell is a separate task).
#
# Dependencies must be installed first via `bash scripts/setup_env.sh`. This
# script does NOT auto-invoke setup_env.sh — installing dependencies without
# explicit consent is a footgun.

set -euo pipefail

# Platform check ---------------------------------------------------------------
case "$(uname -s)" in
  Darwin|Linux) ;;
  *)
    echo "Unsupported platform: $(uname -s). macOS + Linux only." >&2
    exit 1
    ;;
esac

# Dependency check -------------------------------------------------------------
if ! command -v uv >/dev/null 2>&1 || [ ! -d frontend/node_modules ]; then
  echo "Run bash scripts/setup_env.sh first." >&2
  exit 1
fi

# lsof is required for the port check below. Without this guard, a missing lsof
# causes the `if lsof ...; then` test to be silently false, the port check is
# skipped, and an unrelated server already bound to 8000 or 5173 can fool the
# downstream health probe into reporting AiLibi healthy. macOS ships lsof;
# minimal Linux images (Alpine, slim Debian containers) often do not.
if ! command -v lsof >/dev/null 2>&1; then
  echo "lsof is required to verify ports 8000 and 5173 are free." >&2
  echo "Install it: Debian/Ubuntu \`apt install lsof\`, Fedora/RHEL \`dnf install lsof\`, Alpine \`apk add lsof\`." >&2
  exit 1
fi

# Port check -------------------------------------------------------------------
for port in 8000 5173; do
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    pid=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t | head -1)
    echo "Port $port already in use by PID $pid. Run: kill $pid" >&2
    exit 1
  fi
done

# Process lifecycle ------------------------------------------------------------
api_pid=""
ui_pid=""

# SIGTERM the given PID and every descendant, leaves-first. Needed because
# `npm` spawns `vite` and `uv run` spawns `python` as children, and a bare
# `kill $pid` against the parent can orphan the child (which then keeps the
# port bound after the script exits).
kill_tree() {
  local pid="$1"
  [ -z "$pid" ] && return
  local children
  children=$(pgrep -P "$pid" 2>/dev/null || true)
  for child in $children; do
    kill_tree "$child"
  done
  kill "$pid" 2>/dev/null || true
}

cleanup() {
  kill_tree "$api_pid"
  kill_tree "$ui_pid"
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Serve the committed curated sample set by default. Without this the loader's
# fallthrough prefers a local ./replays scratch dir if one exists, so the
# spectator could show an ad-hoc run instead of the canonical committed games.
# Override AILIBI_REPLAY_DIR to point at an ad-hoc run dir on purpose.
export AILIBI_REPLAY_DIR="${AILIBI_REPLAY_DIR:-replays/samples}"

# Start API + frontend with prefixed logs. Use process substitution
# (`> >(sed …) 2>&1`) rather than a pipe (`| sed …`) so `$!` captures the
# PID of the actual server command — pipe semantics give `$!` the trailing
# `sed`, and SIGTERM-ing only `sed` lets a quiet uvicorn/Vite keep listening.
uv run uvicorn api.main:app --port 8000 > >(sed 's/^/[api] /') 2>&1 &
api_pid=$!
(cd frontend && npm run dev) > >(sed 's/^/[ui] /') 2>&1 &
ui_pid=$!

# Health-check loop ------------------------------------------------------------
wait_for() {
  local url="$1" name="$2" elapsed=0
  while [ "$elapsed" -lt 30 ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
    elapsed=$((elapsed + 1))
    echo "  waiting for $name ($elapsed s)..." >&2
  done
  echo "$name failed to respond at $url within 30s" >&2
  return 1
}

wait_for "http://localhost:8000/" "api" || exit 1
wait_for "http://localhost:5173/" "ui" || exit 1

echo "Open http://localhost:5173 in your browser."
echo "Press Ctrl-C to stop."

case "$(uname -s)" in
  Darwin) open "http://localhost:5173" 2>/dev/null || true ;;
  Linux)  xdg-open "http://localhost:5173" 2>/dev/null || true ;;
esac

# Stay in the foreground until Ctrl-C; cleanup trap handles the rest.
wait "$api_pid" "$ui_pid"
