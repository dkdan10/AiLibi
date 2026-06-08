#!/usr/bin/env bash
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required to set up AiLibi dependencies." >&2
  echo "Install uv first, then run: bash scripts/setup_env.sh" >&2
  exit 1
fi

uv sync --locked

uv run python --version
uv run ruff --version
uv run mypy --version
uv run pytest --version
uv run lint-imports --version

# Frontend dependencies (Phase 4.3+). Skipped on branches without frontend/.
# When the frontend IS present, npm is a hard prerequisite: failing loudly here
# beats a partially-configured environment that breaks later in obscure ways.
# Uses `npm ci` for a reproducible install from the committed lockfile (fails on
# package.json/lock drift rather than silently rewriting the lock).
if [ -f frontend/package.json ]; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "npm is required to set up the AiLibi frontend (frontend/package.json present)." >&2
    echo "Install Node.js/npm, then re-run: bash scripts/setup_env.sh" >&2
    exit 1
  fi
  echo "Installing frontend dependencies (npm ci in frontend/)..."
  # npm ci pulls from the public registry, which intermittently resets the
  # connection (ECONNRESET) on CI runners and fails the whole job before any
  # check runs. Retry a few times with backoff so a transient network blip does
  # not red the build; a genuine lockfile / package error still fails loudly
  # once the attempts are exhausted.
  npm_ci_max_attempts=3
  npm_ci_attempt=1
  until (cd frontend && npm ci --fetch-retries=5 --fetch-retry-maxtimeout=120000); do
    if [ "$npm_ci_attempt" -ge "$npm_ci_max_attempts" ]; then
      echo "npm ci failed after $npm_ci_max_attempts attempts." >&2
      exit 1
    fi
    echo "npm ci failed (attempt $npm_ci_attempt/$npm_ci_max_attempts) -- retrying in 10s..." >&2
    npm_ci_attempt=$((npm_ci_attempt + 1))
    sleep 10
  done
else
  echo "No frontend/package.json; skipping frontend dependency install."
fi
