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
cleanup() {
  if [ -n "$api_pid" ]; then
    kill "$api_pid" 2>/dev/null || true
  fi
  if [ -n "$ui_pid" ]; then
    kill "$ui_pid" 2>/dev/null || true
  fi
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Start API + frontend with prefixed logs --------------------------------------
uv run uvicorn api.main:app --port 8000 2>&1 | sed 's/^/[api] /' &
api_pid=$!
(cd frontend && npm run dev) 2>&1 | sed 's/^/[ui] /' &
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
